"""
Tests for the SchemaLoader class.
"""

import json
from pathlib import Path

import pytest
import yaml

from src.schema_loader import SchemaLoader


class TestSchemaLoader:
    """Test suite for SchemaLoader."""

    def test_init_with_default_directory(self):
        """Test initialization with default schema directory."""
        loader = SchemaLoader()
        assert loader.schema_directory == Path("./schemas")
        assert loader.validate_schemas is True
        assert loader._loaded_schemas == {}

    def test_init_with_custom_directory(self, temp_schema_dir):
        """Test initialization with custom schema directory."""
        loader = SchemaLoader(str(temp_schema_dir))
        assert loader.schema_directory == temp_schema_dir

    def test_load_schema_json(self, temp_schema_dir, sample_thing_schema):
        """Test loading a JSON schema file."""
        # Create schema file
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        # Load schema
        loader = SchemaLoader(str(temp_schema_dir))
        schema = loader.load_schema("thing_schema.json")

        assert schema["x-entityType"] == "Things"
        assert "name" in schema["properties"]
        assert schema["required"] == ["name", "description"]

    def test_load_schema_yaml(self, temp_schema_dir, sample_thing_schema):
        """Test loading a YAML schema file."""
        # Create schema file
        schema_file = temp_schema_dir / "thing_schema.yaml"
        with open(schema_file, "w", encoding="utf-8") as f:
            yaml.dump(sample_thing_schema, f)

        # Load schema
        loader = SchemaLoader(str(temp_schema_dir))
        schema = loader.load_schema("thing_schema.yaml")

        assert schema["x-entityType"] == "Things"

    def test_load_schema_not_found(self, temp_schema_dir):
        """Test loading a non-existent schema file."""
        loader = SchemaLoader(str(temp_schema_dir))

        with pytest.raises(FileNotFoundError, match="Schema file not found"):
            loader.load_schema("nonexistent.json")

    def test_load_schema_invalid_json(self, temp_schema_dir):
        """Test loading a schema file with invalid JSON."""
        # Create invalid JSON file
        schema_file = temp_schema_dir / "invalid.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            f.write("{invalid json")

        loader = SchemaLoader(str(temp_schema_dir))

        with pytest.raises(ValueError, match="Invalid JSON/YAML"):
            loader.load_schema("invalid.json")

    def test_schema_caching(self, temp_schema_dir, sample_thing_schema):
        """Test that schemas are cached after first load."""
        # Create schema file
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))

        # Load schema twice
        schema1 = loader.load_schema("thing_schema.json")
        schema2 = loader.load_schema("thing_schema.json")

        # Should return the same cached object
        assert schema1 is schema2
        assert len(loader._loaded_schemas) == 1

    def test_clear_cache(self, temp_schema_dir, sample_thing_schema):
        """Test clearing the schema cache."""
        # Create schema file
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))

        # Load schema
        loader.load_schema("thing_schema.json")
        assert len(loader._loaded_schemas) == 1

        # Clear cache
        loader.clear_cache()
        assert len(loader._loaded_schemas) == 0

    def test_load_schema_for_entity_type_singular(self, temp_schema_dir, sample_thing_schema):
        """Test loading schema by entity type using singular naming."""
        # Create schema file with singular name
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))
        schema = loader.load_schema_for_entity_type("Things")

        assert schema is not None
        assert schema["x-entityType"] == "Things"

    def test_load_schema_for_entity_type_not_found(self, temp_schema_dir):
        """Test loading schema for entity type that doesn't exist."""
        loader = SchemaLoader(str(temp_schema_dir))
        schema = loader.load_schema_for_entity_type("NonExistent")

        assert schema is None

    def test_discover_schemas(self, temp_schema_dir, sample_thing_schema, sample_sensor_schema):
        """Test discovering all schemas in directory."""
        # Create multiple schema files
        thing_file = temp_schema_dir / "thing_schema.json"
        with open(thing_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        sensor_file = temp_schema_dir / "sensor_schema.json"
        with open(sensor_file, "w", encoding="utf-8") as f:
            json.dump(sample_sensor_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))
        schemas = loader.discover_schemas()

        assert len(schemas) == 2
        assert "Things" in schemas
        assert "Sensors" in schemas

    def test_discover_schemas_empty_directory(self, temp_schema_dir):
        """Test discovering schemas in empty directory."""
        loader = SchemaLoader(str(temp_schema_dir))
        schemas = loader.discover_schemas()

        assert len(schemas) == 0

    def test_discover_schemas_missing_entity_type(self, temp_schema_dir):
        """Test discovering schemas where some files lack x-entityType."""
        # Create schema without x-entityType
        schema_file = temp_schema_dir / "invalid_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump({"$schema": "https://json-schema.org/draft/2020-12/schema"}, f)

        loader = SchemaLoader(str(temp_schema_dir))
        schemas = loader.discover_schemas()

        # Should skip files without x-entityType
        assert len(schemas) == 0

    def test_validate_schema_file_valid(self, temp_schema_dir, sample_thing_schema):
        """Test validating a valid schema file."""
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))
        errors = loader.validate_schema_file("thing_schema.json")

        assert len(errors) == 0

    def test_validate_schema_file_not_found(self, temp_schema_dir):
        """Test validating a non-existent schema file."""
        loader = SchemaLoader(str(temp_schema_dir))
        errors = loader.validate_schema_file("nonexistent.json")

        assert len(errors) == 1
        assert "not found" in errors[0]

    def test_get_schema_info(self, temp_schema_dir, sample_thing_schema):
        """Test getting schema metadata."""
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))
        info = loader.get_schema_info("thing_schema.json")

        assert info["exists"] is True
        assert info["entity_type"] == "Things"
        assert len(info["errors"]) == 0

    def test_get_schema_info_not_found(self, temp_schema_dir):
        """Test getting info for non-existent schema."""
        loader = SchemaLoader(str(temp_schema_dir))
        info = loader.get_schema_info("nonexistent.json")

        assert info["exists"] is False
        assert len(info["errors"]) == 1

    def test_load_schemas_for_entity_types(
        self, temp_schema_dir, sample_thing_schema, sample_sensor_schema
    ):
        """Test loading schemas for multiple entity types."""
        # Create schema files
        thing_file = temp_schema_dir / "thing_schema.json"
        with open(thing_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        sensor_file = temp_schema_dir / "sensor_schema.json"
        with open(sensor_file, "w", encoding="utf-8") as f:
            json.dump(sample_sensor_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))
        schemas = loader.load_schemas_for_entity_types(["Things", "Sensors", "NonExistent"])

        assert len(schemas) == 2
        assert "Things" in schemas
        assert "Sensors" in schemas
        assert "NonExistent" not in schemas

    def test_absolute_path_resolution(self, temp_schema_dir, sample_thing_schema):
        """Test loading schema with absolute path."""
        schema_file = temp_schema_dir / "thing_schema.json"
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(sample_thing_schema, f)

        loader = SchemaLoader(str(temp_schema_dir))
        schema = loader.load_schema(str(schema_file))

        assert schema["x-entityType"] == "Things"
