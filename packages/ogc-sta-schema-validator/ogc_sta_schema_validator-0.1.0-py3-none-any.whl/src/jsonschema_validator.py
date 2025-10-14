"""
JSON Schema-based validation engine for SensorThings API entities.
This module replaces the custom validation engine with standard JSON Schema validation
while preserving all existing functionality including custom error messages and severity levels.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional

import jsonschema
from jsonschema import ValidationError as JsonSchemaValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationError:
    """Represents a validation error with detailed information."""

    property_path: str
    message: str
    validator: str  # JSON Schema validator type (e.g., "required", "type", "pattern")
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    severity: str = "error"  # "error" or "warning"


@dataclass
class ValidationResult:
    """Result of validating an entity."""

    entity_id: Optional[str]
    entity_type: str
    is_valid: bool
    errors: list[ValidationError]
    warnings: list[ValidationError] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class JsonSchemaValidationEngine:
    """JSON Schema-based validation engine that validates entities against JSON Schema specifications."""

    def __init__(self):
        """Initialize the JSON Schema validation engine."""
        self.validator_cache = {}  # Cache compiled validators for performance

    def validate_entity(self, entity: dict[str, Any], schema: dict[str, Any]) -> ValidationResult:
        """
        Validate a single entity against a JSON Schema.

        Args:
            entity: Entity data from SensorThings API
            schema: JSON Schema specification

        Returns:
            ValidationResult with validation status and errors
        """
        entity_id = str(entity.get("@iot.id", "unknown"))
        entity_type = schema.get("x-entityType", schema.get("title", "Unknown"))
        entity_name = entity.get("name", "No name")
        entity_url = entity.get("@iot.selfLink", f"{entity_type}({entity_id})")

        logger.debug(f"Validating entity: {entity_url} (Name: {entity_name})")

        errors = []
        warnings = []

        # Get or create validator
        validator = self._get_validator(schema)

        # Perform JSON Schema validation
        validation_errors = list(validator.iter_errors(entity))

        # Convert JSON Schema errors to our ValidationError format
        for error in validation_errors:
            validation_error = self._convert_jsonschema_error(error, entity_id, entity_type, schema)

            if validation_error.severity == "warning":
                warnings.append(validation_error)
            else:
                errors.append(validation_error)

        is_valid = len(errors) == 0
        result = ValidationResult(
            entity_id=entity_id,
            entity_type=entity_type,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
        )

        logger.debug(
            f"Validation result for {entity_url}: "
            f"{'VALID' if is_valid else 'INVALID'} "
            f"({len(errors)} errors, {len(warnings)} warnings)"
        )

        return result

    def validate_entities(
        self, entities: list[dict[str, Any]], schema: dict[str, Any]
    ) -> list[ValidationResult]:
        """
        Validate multiple entities against a JSON Schema.

        Args:
            entities: List of entity data from SensorThings API
            schema: JSON Schema specification

        Returns:
            List of ValidationResult objects
        """
        results = []
        for entity in entities:
            result = self.validate_entity(entity, schema)
            results.append(result)
        return results

    def _get_validator(self, schema: dict[str, Any]) -> jsonschema.protocols.Validator:
        """
        Get or create a compiled JSON Schema validator.

        Args:
            schema: JSON Schema specification

        Returns:
            Compiled JSON Schema validator
        """
        # Use schema ID or hash as cache key
        schema_id = schema.get("$id", str(hash(str(schema))))

        if schema_id not in self.validator_cache:
            # Create validator with Draft 2020-12 support
            validator_class = jsonschema.validators.validator_for(schema)
            validator_class.check_schema(schema)  # Validate the schema itself

            self.validator_cache[schema_id] = validator_class(schema)
            logger.debug(f"Created new validator for schema: {schema_id}")

        return self.validator_cache[schema_id]

    def _convert_jsonschema_error(
        self,
        error: JsonSchemaValidationError,
        entity_id: str,
        entity_type: str,
        schema: dict[str, Any],
    ) -> ValidationError:
        """
        Convert a JSON Schema validation error to our ValidationError format.

        Args:
            error: JSON Schema validation error
            entity_id: Entity ID
            entity_type: Entity type
            schema: JSON Schema specification

        Returns:
            ValidationError with our custom format
        """
        # Build property path from JSON Schema error path
        property_path = self._build_property_path(error.absolute_path)

        # Get custom error message and severity from schema extensions
        custom_message, severity = self._extract_custom_extensions(error, schema)

        # Use custom message if available, otherwise use JSON Schema message
        message = custom_message or error.message

        return ValidationError(
            property_path=property_path,
            message=message,
            validator=error.validator,  # Use JSON Schema validator name directly
            entity_id=entity_id,
            entity_type=entity_type,
            severity=severity,
        )

    def _build_property_path(self, absolute_path) -> str:
        """
        Build a dot-notation property path from JSON Schema error path.

        Args:
            absolute_path: JSON Schema error absolute path

        Returns:
            Dot-notation property path (e.g., "properties.thingId")
        """
        if not absolute_path:
            return "root"

        # Convert path elements to dot notation
        path_parts = []
        for part in absolute_path:
            if isinstance(part, (str, int)):
                path_parts.append(str(part))

        return ".".join(path_parts) if path_parts else "root"

    def _extract_custom_extensions(
        self, error: JsonSchemaValidationError, schema: dict[str, Any]
    ) -> tuple[Optional[str], str]:
        """
        Extract custom error message and severity from schema extensions.

        Args:
            error: JSON Schema validation error
            schema: JSON Schema specification

        Returns:
            Tuple of (custom_message, severity)
        """
        # Navigate to the specific property in schema to find custom extensions
        try:
            property_schema = self._navigate_to_property(schema, error.absolute_path)

            # Extract custom message
            custom_message = property_schema.get("x-errorMessage")

            # Extract severity (default to "error")
            severity = property_schema.get("x-severity", "error")

            return custom_message, severity

        except (KeyError, TypeError, AttributeError):
            # Fallback if we can't find the property in schema
            return None, "error"

    def _navigate_to_property(self, schema: dict[str, Any], path) -> dict[str, Any]:
        """
        Navigate to a specific property in the schema using the error path.

        Args:
            schema: JSON Schema specification
            path: Path to the property

        Returns:
            Property schema definition
        """
        current = schema

        for part in path:
            if isinstance(part, str) and part in current.get("properties", {}):
                current = current["properties"][part]
            elif isinstance(part, int) and "items" in current:
                current = current["items"]
            else:
                # Path not found in schema structure
                break

        return current

    def clear_cache(self) -> None:
        """Clear the validator cache (useful for testing or memory management)."""
        self.validator_cache.clear()
        logger.debug("Validator cache cleared")

    def get_cache_stats(self) -> dict[str, Any]:
        """
        Get statistics about the validator cache.

        Returns:
            Dictionary with cache statistics
        """
        return {
            "cached_validators": len(self.validator_cache),
            "cache_keys": list(self.validator_cache.keys()),
        }
