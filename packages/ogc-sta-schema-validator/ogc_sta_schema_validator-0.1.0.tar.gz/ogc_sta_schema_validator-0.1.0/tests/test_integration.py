"""
Integration tests using real schema files and sample entities.
"""

import pytest

from src.jsonschema_validator import JsonSchemaValidationEngine
from src.schema_loader import SchemaLoader


class TestIntegrationWithExampleSchemas:
    """Integration tests using schemas from examples/schemas directory."""

    def test_validate_thing_valid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating a valid Thing entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Things")
        if not schema:
            pytest.skip("Thing schema not found in examples")

        entity = sample_entities.get("thing_valid")
        if not entity:
            pytest.skip("Valid thing entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.entity_type == "Things"

    def test_validate_thing_invalid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating an invalid Thing entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Things")
        if not schema:
            pytest.skip("Thing schema not found in examples")

        entity = sample_entities.get("thing_invalid")
        if not entity:
            pytest.skip("Invalid thing entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_sensor_valid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating a valid Sensor entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Sensors")
        if not schema:
            pytest.skip("Sensor schema not found in examples")

        entity = sample_entities.get("sensor_valid")
        if not entity:
            pytest.skip("Valid sensor entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_sensor_invalid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating an invalid Sensor entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Sensors")
        if not schema:
            pytest.skip("Sensor schema not found in examples")

        entity = sample_entities.get("sensor_invalid")
        if not entity:
            pytest.skip("Invalid sensor entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_observation_valid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating a valid Observation entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Observations")
        if not schema:
            pytest.skip("Observation schema not found in examples")

        entity = sample_entities.get("observation_valid")
        if not entity:
            pytest.skip("Valid observation entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_observation_invalid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating an invalid Observation entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Observations")
        if not schema:
            pytest.skip("Observation schema not found in examples")

        entity = sample_entities.get("observation_invalid")
        if not entity:
            pytest.skip("Invalid observation entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_datastream_valid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating a valid Datastream entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Datastreams")
        if not schema:
            pytest.skip("Datastream schema not found in examples")

        entity = sample_entities.get("datastream_valid")
        if not entity:
            pytest.skip("Valid datastream entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_datastream_invalid_entity(self, examples_schemas_dir, sample_entities):
        """Test validating an invalid Datastream entity with real schema."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Datastreams")
        if not schema:
            pytest.skip("Datastream schema not found in examples")

        entity = sample_entities.get("datastream_invalid")
        if not entity:
            pytest.skip("Invalid datastream entity not found in sample entities")

        result = engine.validate_entity(entity, schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_discover_all_example_schemas(self, examples_schemas_dir):
        """Test discovering all schemas in examples directory."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        schemas = loader.discover_schemas()

        # Should find at least the 4 example schemas
        assert len(schemas) >= 4
        assert "Things" in schemas
        assert "Sensors" in schemas
        assert "Observations" in schemas
        assert "Datastreams" in schemas

    def test_batch_validation_with_example_data(self, examples_schemas_dir, sample_entities):
        """Test batch validation with multiple entities."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Things")
        if not schema:
            pytest.skip("Thing schema not found in examples")

        valid_entity = sample_entities.get("thing_valid")
        invalid_entity = sample_entities.get("thing_invalid")

        if not valid_entity or not invalid_entity:
            pytest.skip("Sample entities not found")

        entities = [valid_entity, invalid_entity]
        results = engine.validate_entities(entities, schema)

        assert len(results) == 2
        # First should be valid, second should be invalid
        assert results[0].is_valid is True
        assert results[1].is_valid is False

    def test_validate_all_entity_types(self, examples_schemas_dir, sample_entities):
        """Test validating all entity types with their valid samples."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        entity_types = ["Things", "Sensors", "Observations", "Datastreams"]
        valid_keys = ["thing_valid", "sensor_valid", "observation_valid", "datastream_valid"]

        results = []

        for entity_type, valid_key in zip(entity_types, valid_keys):
            schema = loader.load_schema_for_entity_type(entity_type)
            if not schema:
                continue

            entity = sample_entities.get(valid_key)
            if not entity:
                continue

            result = engine.validate_entity(entity, schema)
            results.append((entity_type, result))

        # At least some entity types should be validated
        assert len(results) > 0

        # All valid entities should pass validation
        for entity_type, result in results:
            assert result.is_valid is True, f"Valid {entity_type} entity should pass validation"

    def test_schema_validation_with_custom_error_messages(
        self, examples_schemas_dir, sample_entities
    ):
        """Test that custom error messages from schemas are used."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Things")
        if not schema:
            pytest.skip("Thing schema not found in examples")

        # Entity missing required name field
        entity = sample_entities.get("thing_invalid")
        if not entity:
            pytest.skip("Invalid thing entity not found")

        result = engine.validate_entity(entity, schema)

        # Should have errors with messages
        assert len(result.errors) > 0
        for error in result.errors:
            assert error.message is not None
            assert len(error.message) > 0

    def test_schema_info_retrieval(self, examples_schemas_dir):
        """Test retrieving schema information."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))

        info = loader.get_schema_info("thing_schema.json")

        assert info["exists"] is True
        assert info["entity_type"] == "Things"
        assert len(info["errors"]) == 0

    def test_load_multiple_entity_type_schemas(self, examples_schemas_dir):
        """Test loading schemas for multiple entity types."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))

        entity_types = ["Things", "Sensors", "Observations", "Datastreams"]
        schemas = loader.load_schemas_for_entity_types(entity_types)

        # Should load at least some schemas
        assert len(schemas) > 0

        # Each loaded schema should have correct entity type
        for entity_type, schema in schemas.items():
            assert schema.get("x-entityType") == entity_type


class TestIntegrationErrorScenarios:
    """Test error handling in integration scenarios."""

    def test_schema_not_found_for_entity_type(self, examples_schemas_dir):
        """Test handling when schema is not found for entity type."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        schema = loader.load_schema_for_entity_type("NonExistentEntityType")

        assert schema is None

    def test_validation_with_empty_entity(self, examples_schemas_dir):
        """Test validating an empty entity."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Things")
        if not schema:
            pytest.skip("Thing schema not found")

        result = engine.validate_entity({}, schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validation_preserves_entity_context(self, examples_schemas_dir, sample_entities):
        """Test that validation results include entity context."""
        if not examples_schemas_dir.exists():
            pytest.skip("Examples schemas directory not found")

        loader = SchemaLoader(str(examples_schemas_dir))
        engine = JsonSchemaValidationEngine()

        schema = loader.load_schema_for_entity_type("Things")
        if not schema:
            pytest.skip("Thing schema not found")

        entity = sample_entities.get("thing_valid")
        if not entity:
            pytest.skip("Valid thing entity not found")

        result = engine.validate_entity(entity, schema)

        # Result should include entity context
        assert result.entity_id is not None
        assert result.entity_type == "Things"
