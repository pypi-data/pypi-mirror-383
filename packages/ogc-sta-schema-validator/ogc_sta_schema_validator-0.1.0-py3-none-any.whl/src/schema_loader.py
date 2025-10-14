"""
Schema loader for validation schemas.
Loads and validates schema files, supports multiple formats and schema validation.
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional

import yaml
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validators

logger = logging.getLogger(__name__)


class SchemaLoader:
    """Loads and validates schema files for entity validation."""

    def __init__(self, schema_directory: str = "./schemas"):
        """
        Initialize the schema loader.

        Args:
            schema_directory: Directory containing schema files
        """
        self.schema_directory = Path(schema_directory)
        self._loaded_schemas = {}  # Cache for loaded schemas

        self.validate_schemas = True  # Flag to enable/disable schema validation

    def load_schema(self, schema_file: str) -> dict[str, Any]:
        """
        Load a schema from a file.

        Args:
            schema_file: Path to schema file (relative to schema_directory or absolute)

        Returns:
            Loaded and validated schema dictionary

        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValueError: If schema is invalid
        """
        schema_path = self._resolve_schema_path(schema_file)

        # Check cache first
        cache_key = str(schema_path)
        if cache_key in self._loaded_schemas:
            return self._loaded_schemas[cache_key]

        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        try:
            logger.debug(f"Loading schema from: {schema_path}")

            # Load file based on extension
            with open(schema_path, encoding="utf-8") as f:
                if schema_path.suffix.lower() in [".yml", ".yaml"]:
                    schema = yaml.safe_load(f)
                else:  # Assume JSON
                    schema = json.load(f)

            # Validate schema against meta-schema
            self._validate_schema_structure(schema, schema_path)

            # Cache the loaded schema
            self._loaded_schemas[cache_key] = schema

            logger.info(
                f"Successfully loaded schema for {schema.get('x-entityType', 'unknown')} from {schema_path}"
            )
            return schema

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid JSON/YAML in schema file {schema_path}: {e}") from e

    def load_schemas_for_entity_types(self, entity_types: list[str]) -> dict[str, dict[str, Any]]:
        """
        Load schemas for multiple entity types.

        Args:
            entity_types: List of entity type names

        Returns:
            Dictionary mapping entity type to schema
        """
        schemas = {}

        for entity_type in entity_types:
            try:
                schema = self.load_schema_for_entity_type(entity_type)
                if schema:
                    schemas[entity_type] = schema
            except (FileNotFoundError, ValueError) as e:
                logger.warning(f"Could not load schema for {entity_type}: {e}")

        return schemas

    def load_schema_for_entity_type(self, entity_type: str) -> Optional[dict[str, Any]]:
        """
        Load schema for a specific entity type using naming convention.

        Args:
            entity_type: Entity type name (e.g., "Things", "Sensors")

        Returns:
            Schema dictionary or None if not found
        """
        # Try different naming conventions
        # First try singular forms for common entity types
        singular_forms = {
            "Things": "thing",
            "Sensors": "sensor",
            "Observations": "observation",
            "Datastreams": "datastream",
        }

        possible_names = []

        # Add singular form if available
        if entity_type in singular_forms:
            singular = singular_forms[entity_type]
            possible_names.extend(
                [
                    f"{singular}_schema.json",
                    f"{singular}_schema.yaml",
                    f"{singular}.json",
                    f"{singular}.yaml",
                ]
            )

        # Add original plural forms
        possible_names.extend(
            [
                f"{entity_type.lower()}_schema.json",
                f"{entity_type.lower()}_schema.yaml",
                f"{entity_type.lower()}.json",
                f"{entity_type.lower()}.yaml",
                f"{entity_type}.json",
                f"{entity_type}.yaml",
            ]
        )

        for name in possible_names:
            try:
                schema = self.load_schema(name)
                return schema
            except FileNotFoundError:
                continue

        logger.debug(f"No schema found for entity type: {entity_type}")
        return None

    def discover_schemas(self) -> dict[str, dict[str, Any]]:
        """
        Discover and load all schemas in the schema directory.

        Returns:
            Dictionary mapping entity type to schema
        """
        schemas = {}

        if not self.schema_directory.exists():
            logger.warning(f"Schema directory does not exist: {self.schema_directory}")
            return schemas

        # Find all JSON and YAML files in the schema directory
        schema_files = (
            list(self.schema_directory.glob("*.json"))
            + list(self.schema_directory.glob("*.yaml"))
            + list(self.schema_directory.glob("*.yml"))
        )

        for schema_file in schema_files:
            try:
                schema = self.load_schema(schema_file.name)
                entity_type = schema.get("x-entityType")

                if entity_type:
                    schemas[entity_type] = schema
                    logger.debug(f"Discovered schema for {entity_type} in {schema_file.name}")
                else:
                    logger.warning(f"Schema file {schema_file.name} missing x-entityType")

            except (FileNotFoundError, ValueError) as e:
                logger.error(f"Failed to load schema from {schema_file.name}: {e}")

        logger.info(f"Discovered {len(schemas)} schemas")
        return schemas

    def validate_schema_file(self, schema_file: str) -> list[str]:
        """
        Validate a schema file without loading it into cache.

        Args:
            schema_file: Path to schema file

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        schema_path = self._resolve_schema_path(schema_file)

        try:
            with open(schema_path, encoding="utf-8") as f:
                if schema_path.suffix.lower() in [".yml", ".yaml"]:
                    schema = yaml.safe_load(f)
                else:
                    schema = json.load(f)

            self._validate_schema_structure(schema, schema_path)

        except FileNotFoundError:
            errors.append(f"Schema file not found: {schema_path}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            errors.append(f"Invalid JSON/YAML: {e}")
        except JsonSchemaValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
        except Exception as e:
            errors.append(f"Unexpected error: {e}")

        return errors

    def clear_cache(self):
        """Clear the schema cache."""
        self._loaded_schemas.clear()
        logger.debug("Schema cache cleared")

    def _resolve_schema_path(self, schema_file: str) -> Path:
        """
        Resolve schema file path.

        Args:
            schema_file: Schema file name or path

        Returns:
            Resolved Path object
        """
        path = Path(schema_file)

        if path.is_absolute():
            return path
        else:
            return self.schema_directory / path

    def _validate_schema_structure(self, schema: dict[str, Any], schema_path: Path):
        """
        Validate that the schema is a valid JSON Schema.

        Args:
            schema: Schema dictionary to validate
            schema_path: Path to schema file (for error reporting)

        Raises:
            JsonSchemaValidationError: If schema is invalid
        """
        if not self.validate_schemas:
            return

        try:
            # Use jsonschema to validate the schema against the JSON Schema meta-schema
            # This will automatically detect the correct meta-schema from $schema field

            # Get the appropriate validator class for this schema
            validator_class = validators.validator_for(schema)

            # Check that the schema itself is valid
            validator_class.check_schema(schema)

            logger.debug(f"Schema {schema_path} is valid JSON Schema")

        except Exception as e:
            logger.error(f"Schema validation failed for {schema_path}: {e}")
            raise JsonSchemaValidationError(f"Invalid JSON Schema: {e}") from e

    def get_schema_info(self, schema_file: str) -> dict[str, Any]:
        """
        Get basic information about a schema file without fully loading it.

        Args:
            schema_file: Path to schema file

        Returns:
            Dictionary with schema metadata
        """
        schema_path = self._resolve_schema_path(schema_file)
        info = {
            "file_path": str(schema_path),
            "exists": schema_path.exists(),
            "entity_type": None,
            "version": None,
            "rule_count": 0,
            "errors": [],
        }

        if not schema_path.exists():
            info["errors"].append("File does not exist")
            return info

        try:
            with open(schema_path, encoding="utf-8") as f:
                if schema_path.suffix.lower() in [".yml", ".yaml"]:
                    schema = yaml.safe_load(f)
                else:
                    schema = json.load(f)

            info["entity_type"] = schema.get("x-entityType")
            info["version"] = schema.get("x-version")
            info["rule_count"] = len(schema.get("rules", {}))

        except Exception as e:
            info["errors"].append(str(e))

        return info
