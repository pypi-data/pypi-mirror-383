"""
Main validation runner that orchestrates the validation process.
Handles entity fetching, validation execution, and report generation.
"""

import csv
import io
import json
import logging
import time
from collections.abc import Iterator
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .api_client import SensorThingsAPIClient
from .jsonschema_validator import JsonSchemaValidationEngine, ValidationResult
from .schema_loader import SchemaLoader

logger = logging.getLogger(__name__)


@dataclass
class ValidationSummary:
    """Summary statistics for a validation run."""

    total_entities: int
    valid_entities: int
    invalid_entities: int
    total_errors: int
    total_warnings: int
    entity_type: str
    validation_time: float
    timestamp: str


class ValidationRunner:
    """Main runner that coordinates validation of SensorThings entities."""

    def __init__(
        self,
        api_client: SensorThingsAPIClient,
        schema_loader: SchemaLoader,
        batch_size: int = 100,
        stop_on_error: bool = False,
    ):
        """
        Initialize the validation runner.

        Args:
            api_client: SensorThings API client
            schema_loader: Schema loader for validation rules
            batch_size: Number of entities to process in each batch
            stop_on_error: Stop validation on first error if True
        """
        self.api_client = api_client
        self.schema_loader = schema_loader
        self.validation_engine = JsonSchemaValidationEngine()
        self.batch_size = batch_size
        self.stop_on_error = stop_on_error

    def validate_entity_type(
        self,
        entity_type: str,
        schema_file: Optional[str] = None,
        limit: Optional[int] = None,
        filter_expr: Optional[str] = None,
    ) -> list[ValidationResult]:
        """
        Validate all entities of a specific type.

        Args:
            entity_type: Type of entity to validate (Things, Sensors, etc.)
            schema_file: Specific schema file to use (if None, auto-discover)
            limit: Maximum number of entities to validate
            filter_expr: OData filter expression to limit entities

        Returns:
            List of validation results
        """
        logger.info(f"Starting validation for entity type: {entity_type}")
        start_time = time.time()

        # Load schema
        if schema_file:
            schema = self.schema_loader.load_schema(schema_file)
        else:
            schema = self.schema_loader.load_schema_for_entity_type(entity_type)

        if not schema:
            logger.error(f"No schema found for entity type: {entity_type}")
            return []

        version = schema.get("x-version") or schema.get("version", "unknown")
        logger.info(f"Using schema version {version} for {entity_type}")

        # Get entity count for progress tracking
        try:
            total_count = self.api_client.get_entity_count(entity_type, filter_expr)
            if limit:
                total_count = min(total_count, limit)
            logger.info(f"Found {total_count} entities to validate")
        except Exception as e:
            logger.warning(f"Could not get entity count: {e}")
            total_count = None

        # Validate entities in batches
        results = []
        processed = 0

        for batch in self._get_entity_batches(entity_type, limit, filter_expr):
            logger.debug(f"Processing batch of {len(batch)} entities")

            batch_results = self.validation_engine.validate_entities(batch, schema)
            results.extend(batch_results)

            processed += len(batch)

            # Progress reporting
            if total_count:
                progress = (processed / total_count) * 100
                logger.info(f"Progress: {processed}/{total_count} ({progress:.1f}%)")
            else:
                logger.info(f"Processed: {processed} entities")

            # Check for errors if stop_on_error is enabled
            if self.stop_on_error:
                errors_in_batch = [r for r in batch_results if not r.is_valid]
                if errors_in_batch:
                    logger.warning("Stopping validation due to errors in batch")
                    break

        elapsed_time = time.time() - start_time
        logger.info(f"Validation completed in {elapsed_time:.2f} seconds")

        return results

    def validate_specific_entity(
        self, entity_type: str, entity_id: str, schema_file: Optional[str] = None
    ) -> Optional[ValidationResult]:
        """
        Validate a specific entity by ID.

        Args:
            entity_type: Type of entity
            entity_id: Entity ID
            schema_file: Specific schema file to use

        Returns:
            ValidationResult or None if entity not found
        """
        logger.info(f"Validating specific entity: {entity_type}({entity_id})")

        # Load schema
        if schema_file:
            schema = self.schema_loader.load_schema(schema_file)
        else:
            schema = self.schema_loader.load_schema_for_entity_type(entity_type)

        if not schema:
            logger.error(f"No schema found for entity type: {entity_type}")
            return None

        # Fetch entity
        entity = self.api_client.get_entity_by_id(entity_type, entity_id)
        if not entity:
            logger.error(f"Entity not found: {entity_type}({entity_id})")
            return None

        # Validate entity using JSON Schema validation
        result = self.validation_engine.validate_entity(entity, schema)
        logger.info(
            f"Validation result for {entity_type}({entity_id}): {'VALID' if result.is_valid else 'INVALID'}"
        )

        return result

    def validate_all_entity_types(
        self, entity_types: Optional[list[str]] = None, limit_per_type: Optional[int] = None
    ) -> dict[str, list[ValidationResult]]:
        """
        Validate all available entity types.

        Args:
            entity_types: Specific entity types to validate (if None or empty, auto-discover)
            limit_per_type: Maximum entities per type

        Returns:
            Dictionary mapping entity type to validation results
        """
        if not entity_types:  # Handle both None and empty list
            entity_types = self.api_client.get_available_entity_types()

        logger.info(f"Validating entity types: {entity_types}")

        all_results = {}

        for entity_type in entity_types:
            try:
                logger.info(f"Starting validation for {entity_type}")
                results = self.validate_entity_type(entity_type, limit=limit_per_type)
                all_results[entity_type] = results

                # Log summary for this entity type
                summary = self._create_summary(results, entity_type)
                logger.info(
                    f"Summary for {entity_type}: "
                    f"{summary.valid_entities}/{summary.total_entities} valid, "
                    f"{summary.total_errors} errors, {summary.total_warnings} warnings"
                )

            except Exception as e:
                logger.error(f"Failed to validate {entity_type}: {e}")
                all_results[entity_type] = []

        return all_results

    def generate_report(
        self,
        results: list[ValidationResult],
        output_format: str = "console",
        output_file: Optional[str] = None,
        include_valid: bool = False,
    ) -> str:
        """
        Generate a validation report.

        Args:
            results: Validation results to include in report
            output_format: Format of output (console, json, csv)
            output_file: File to write output to (if None, return as string)
            include_valid: Include valid entities in report

        Returns:
            Report as string (if output_file is None)
        """
        if output_format == "json":
            return self._generate_json_report(results, output_file, include_valid)
        elif output_format == "csv":
            return self._generate_csv_report(results, output_file, include_valid)
        else:  # console
            return self._generate_console_report(results, output_file, include_valid)

    def _get_entity_batches(
        self, entity_type: str, limit: Optional[int], filter_expr: Optional[str]
    ) -> Iterator[list[dict[str, Any]]]:
        """Get entities in batches for processing."""
        batch = []

        for entity in self.api_client.get_entities(
            entity_type, limit=limit, filter_expr=filter_expr
        ):
            batch.append(entity)

            if len(batch) >= self.batch_size:
                yield batch
                batch = []

        # Yield remaining entities
        if batch:
            yield batch

    def _create_summary(
        self, results: list[ValidationResult], entity_type: str
    ) -> ValidationSummary:
        """Create summary statistics for validation results."""
        total_entities = len(results)
        valid_entities = sum(1 for r in results if r.is_valid)
        invalid_entities = total_entities - valid_entities
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        return ValidationSummary(
            total_entities=total_entities,
            valid_entities=valid_entities,
            invalid_entities=invalid_entities,
            total_errors=total_errors,
            total_warnings=total_warnings,
            entity_type=entity_type,
            validation_time=0,  # Would need to be tracked separately
            timestamp=datetime.now().isoformat(),
        )

    def _generate_console_report(
        self, results: list[ValidationResult], output_file: Optional[str], include_valid: bool
    ) -> str:
        """Generate a human-readable console report."""
        lines = []
        lines.append("SensorThings API Validation Report")
        lines.append("=" * 50)
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("")

        # Overall summary
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)

        lines.append("Summary:")
        lines.append(f"  Total entities: {total}")
        lines.append(
            f"  Valid: {valid} ({valid / total * 100:.1f}%)" if total > 0 else "  Valid: 0"
        )
        lines.append(
            f"  Invalid: {invalid} ({invalid / total * 100:.1f}%)" if total > 0 else "  Invalid: 0"
        )
        lines.append(f"  Total errors: {total_errors}")
        lines.append(f"  Total warnings: {total_warnings}")
        lines.append("")

        # Entity details
        for result in results:
            if not include_valid and result.is_valid:
                continue

            lines.append(f"Entity: {result.entity_type}({result.entity_id})")
            lines.append(f"  Status: {'VALID' if result.is_valid else 'INVALID'}")

            if result.errors:
                lines.append(f"  Errors ({len(result.errors)}):")
                for error in result.errors:
                    lines.append(f"    - {error.property_path}: {error.message}")

            if result.warnings:
                lines.append(f"  Warnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    lines.append(f"    - {warning.property_path}: {warning.message}")

            lines.append("")

        report = "\n".join(lines)

        if output_file:
            Path(output_file).write_text(report, encoding="utf-8")
            logger.info(f"Console report written to: {output_file}")

        return report

    def _generate_json_report(
        self, results: list[ValidationResult], output_file: Optional[str], include_valid: bool
    ) -> str:
        """Generate a JSON report."""
        # Filter results if needed
        filtered_results = results if include_valid else [r for r in results if not r.is_valid]

        # Convert to serializable format
        serializable_results = []
        for result in filtered_results:
            result_dict = {
                "entityId": result.entity_id,
                "entityType": result.entity_type,
                "isValid": result.is_valid,
                "errors": [asdict(error) for error in result.errors],
                "warnings": [asdict(warning) for warning in result.warnings],
            }
            serializable_results.append(result_dict)

        # Create summary
        summary = self._create_summary(results, results[0].entity_type if results else "Unknown")

        report_data = {"summary": asdict(summary), "results": serializable_results}

        report_json = json.dumps(report_data, indent=2, ensure_ascii=False)

        if output_file:
            Path(output_file).write_text(report_json, encoding="utf-8")
            logger.info(f"JSON report written to: {output_file}")

        return report_json

    def _generate_csv_report(
        self, results: list[ValidationResult], output_file: Optional[str], include_valid: bool
    ) -> str:
        """Generate a CSV report."""

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "EntityType",
                "EntityId",
                "IsValid",
                "ErrorCount",
                "WarningCount",
                "PropertyPath",
                "Validator",
                "Message",
                "Severity",
            ]
        )

        for result in results:
            if not include_valid and result.is_valid:
                continue

            base_row = [
                result.entity_type,
                result.entity_id,
                result.is_valid,
                len(result.errors),
                len(result.warnings),
            ]

            # Write errors
            for error in result.errors:
                row = base_row + [error.property_path, error.validator, error.message, "error"]
                writer.writerow(row)

            # Write warnings
            for warning in result.warnings:
                row = base_row + [
                    warning.property_path,
                    warning.validator,
                    warning.message,
                    "warning",
                ]
                writer.writerow(row)

            # If no errors or warnings, write a single row
            if not result.errors and not result.warnings:
                row = base_row + ["", "", "", ""]
                writer.writerow(row)

        csv_content = output.getvalue()
        output.close()

        if output_file:
            Path(output_file).write_text(csv_content, encoding="utf-8")
            logger.info(f"CSV report written to: {output_file}")

        return csv_content
