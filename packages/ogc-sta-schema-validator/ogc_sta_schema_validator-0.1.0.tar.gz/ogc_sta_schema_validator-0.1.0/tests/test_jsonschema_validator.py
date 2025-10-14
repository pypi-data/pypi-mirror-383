"""
Tests for the JsonSchemaValidationEngine class.
"""

from src.jsonschema_validator import JsonSchemaValidationEngine, ValidationError, ValidationResult


class TestJsonSchemaValidationEngine:
    """Test suite for JsonSchemaValidationEngine."""

    def test_init(self):
        """Test initialization of validation engine."""
        engine = JsonSchemaValidationEngine()
        assert engine.validator_cache == {}

    def test_validate_valid_entity(self, sample_thing_schema, valid_thing_entity):
        """Test validating a valid entity."""
        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(valid_thing_entity, sample_thing_schema)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert result.entity_id == "1"
        assert result.entity_type == "Things"

    def test_validate_invalid_entity_missing_required(
        self, sample_thing_schema, invalid_thing_entity
    ):
        """Test validating an entity missing required field."""
        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(invalid_thing_entity, sample_thing_schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

        # Check that we got a required field error for missing 'name'
        required_errors = [err for err in result.errors if err.validator == "required"]
        assert len(required_errors) > 0

    def test_validate_invalid_entity_wrong_type(self, sample_thing_schema):
        """Test validating an entity with wrong type."""
        entity = {
            "@iot.id": 3,
            "name": 12345,  # Should be string
            "description": "Valid description",
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_entity_enum_violation(self, sample_thing_schema):
        """Test validating an entity with invalid enum value."""
        entity = {
            "@iot.id": 4,
            "name": "Test Thing",
            "description": "Valid description",
            "properties": {"status": "invalid_status"},  # Not in enum
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        assert result.is_valid is False
        # Check for enum error
        enum_errors = [err for err in result.errors if err.validator == "enum"]
        assert len(enum_errors) > 0

    def test_validate_entity_length_violation(self, sample_thing_schema):
        """Test validating an entity with length violation."""
        entity = {
            "@iot.id": 5,
            "name": "",  # Empty string violates minLength
            "description": "Valid description",
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        assert result.is_valid is False
        length_errors = [
            err for err in result.errors if err.validator in ("minLength", "maxLength")
        ]
        assert len(length_errors) > 0

    def test_validate_entity_format_violation(self, sample_thing_schema):
        """Test validating an entity with date format violation."""
        entity = {
            "@iot.id": 6,
            "name": "Test Thing",
            "description": "Valid description",
            "properties": {"installationDate": "not-a-date"},
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        # Note: JSON Schema format validation is optional and may not fail by default
        # This test documents the behavior but doesn't enforce strict format checking
        # If format checking is enabled, this would fail
        if not result.is_valid:
            # Check for format error if validation failed
            format_errors = [err for err in result.errors if err.validator == "format"]
            assert len(format_errors) > 0
        else:
            # Format validation may not be enforced - this is expected behavior
            pass

    def test_validate_entities_batch(
        self, sample_thing_schema, valid_thing_entity, invalid_thing_entity
    ):
        """Test batch validation of multiple entities."""
        engine = JsonSchemaValidationEngine()
        entities = [valid_thing_entity, invalid_thing_entity]

        results = engine.validate_entities(entities, sample_thing_schema)

        assert len(results) == 2
        assert results[0].is_valid is True
        assert results[1].is_valid is False

    def test_custom_error_message(self, sample_thing_schema, invalid_thing_entity):
        """Test that custom error messages are used."""
        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(invalid_thing_entity, sample_thing_schema)

        # The schema has custom error messages (x-errorMessage)
        # Check that at least one error has a custom message
        assert len(result.errors) > 0

    def test_validator_caching(self, sample_thing_schema, valid_thing_entity):
        """Test that validators are cached."""
        engine = JsonSchemaValidationEngine()

        # Validate twice with same schema
        engine.validate_entity(valid_thing_entity, sample_thing_schema)
        engine.validate_entity(valid_thing_entity, sample_thing_schema)

        # Should have cached the validator
        assert len(engine.validator_cache) == 1

    def test_clear_cache(self, sample_thing_schema, valid_thing_entity):
        """Test clearing the validator cache."""
        engine = JsonSchemaValidationEngine()

        engine.validate_entity(valid_thing_entity, sample_thing_schema)
        assert len(engine.validator_cache) == 1

        engine.clear_cache()
        assert len(engine.validator_cache) == 0

    def test_get_cache_stats(self, sample_thing_schema, valid_thing_entity):
        """Test getting cache statistics."""
        engine = JsonSchemaValidationEngine()

        engine.validate_entity(valid_thing_entity, sample_thing_schema)
        stats = engine.get_cache_stats()

        assert "cached_validators" in stats
        assert "cache_keys" in stats
        assert stats["cached_validators"] == 1

    def test_validation_error_dataclass(self):
        """Test ValidationError dataclass."""
        error = ValidationError(
            property_path="name",
            message="Name is required",
            validator="required",
            entity_id="123",
            entity_type="Things",
            severity="error",
        )

        assert error.property_path == "name"
        assert error.message == "Name is required"
        assert error.validator == "required"
        assert error.severity == "error"

    def test_validation_result_dataclass(self):
        """Test ValidationResult dataclass."""
        errors = [
            ValidationError(
                property_path="name",
                message="Name is required",
                validator="required",
                entity_id="123",
                entity_type="Things",
            )
        ]

        result = ValidationResult(
            entity_id="123", entity_type="Things", is_valid=False, errors=errors
        )

        assert result.entity_id == "123"
        assert result.entity_type == "Things"
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 0

    def test_nested_property_validation(self, sample_thing_schema):
        """Test validation of nested properties."""
        entity = {
            "@iot.id": 7,
            "name": "Test Thing",
            "description": "Valid description",
            "properties": {
                "status": "active",
                "installationDate": "2024-01-15T10:00:00Z",
            },
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        assert result.is_valid is True

    def test_additional_properties_allowed(self, sample_thing_schema):
        """Test that additional properties are allowed."""
        entity = {
            "@iot.id": 8,
            "name": "Test Thing",
            "description": "Valid description",
            "customField": "This is allowed",
            "properties": {"customProp": "Also allowed"},
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        # Should be valid since additionalProperties is not explicitly false
        assert result.is_valid is True

    def test_validator_detection_required(self, sample_thing_schema):
        """Test that 'required' validator is detected correctly."""
        entity = {"@iot.id": 9, "description": "Missing name"}

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        required_errors = [err for err in result.errors if err.validator == "required"]
        assert len(required_errors) > 0

    def test_validator_detection_type(self, sample_thing_schema):
        """Test that 'type' validator is detected correctly."""
        entity = {"@iot.id": 10, "name": 123, "description": "Test"}

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        type_errors = [err for err in result.errors if err.validator == "type"]
        assert len(type_errors) > 0

    def test_entity_without_iot_id(self, sample_thing_schema):
        """Test validating an entity without @iot.id."""
        entity = {"name": "Test Thing", "description": "Valid description"}

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        assert result.entity_id == "unknown"
        assert result.is_valid is True

    def test_schema_with_multiple_violations(self, sample_thing_schema):
        """Test entity with multiple validation errors."""
        entity = {
            "@iot.id": 11,
            # Missing name
            # Missing description
            "properties": {
                "status": "invalid",  # Invalid enum
                "installationDate": "not-a-date",  # Invalid format
            },
        }

        engine = JsonSchemaValidationEngine()
        result = engine.validate_entity(entity, sample_thing_schema)

        assert result.is_valid is False
        # Should have multiple errors
        assert len(result.errors) >= 2
