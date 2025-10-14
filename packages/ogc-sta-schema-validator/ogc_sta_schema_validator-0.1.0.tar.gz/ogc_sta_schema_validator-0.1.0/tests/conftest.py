"""
Pytest configuration and shared fixtures for tests.
"""

import json
from pathlib import Path

import pytest


@pytest.fixture
def temp_schema_dir(tmp_path):
    """Create a temporary directory with test schema files."""
    schema_dir = tmp_path / "schemas"
    schema_dir.mkdir()
    return schema_dir


@pytest.fixture
def sample_thing_schema():
    """Return a sample Thing schema."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://schemas.sensorthings.org/things.json",
        "title": "Things Schema",
        "x-entityType": "Things",
        "type": "object",
        "required": ["name", "description"],
        "properties": {
            "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 255,
                "x-errorMessage": "Thing must have a name",
            },
            "description": {
                "type": "string",
                "minLength": 1,
                "x-errorMessage": "Thing must have a description",
            },
            "properties": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive", "maintenance"],
                        "x-errorMessage": "Status must be one of: active, inactive, maintenance",
                    },
                    "installationDate": {
                        "type": "string",
                        "format": "date-time",
                        "x-errorMessage": "Installation date must be in ISO 8601 format",
                    },
                },
            },
        },
    }


@pytest.fixture
def sample_sensor_schema():
    """Return a sample Sensor schema."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://schemas.sensorthings.org/sensors.json",
        "title": "Sensors Schema",
        "x-entityType": "Sensors",
        "type": "object",
        "required": ["name", "description", "encodingType", "metadata"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "description": {"type": "string", "minLength": 1},
            "encodingType": {"type": "string"},
            "metadata": {"type": "string"},
        },
    }


@pytest.fixture
def valid_thing_entity():
    """Return a valid Thing entity."""
    return {
        "@iot.id": 1,
        "@iot.selfLink": "https://example.com/v1.1/Things(1)",
        "name": "Test Thing",
        "description": "A test thing for validation",
        "properties": {"status": "active", "installationDate": "2024-01-15T10:00:00Z"},
    }


@pytest.fixture
def invalid_thing_entity():
    """Return an invalid Thing entity (missing required field)."""
    return {
        "@iot.id": 2,
        "@iot.selfLink": "https://example.com/v1.1/Things(2)",
        "description": "Missing name field",
        "properties": {"status": "invalid_status"},
    }


@pytest.fixture
def valid_sensor_entity():
    """Return a valid Sensor entity."""
    return {
        "@iot.id": 10,
        "@iot.selfLink": "https://example.com/v1.1/Sensors(10)",
        "name": "DHT22 Sensor",
        "description": "Temperature and humidity sensor",
        "encodingType": "application/pdf",
        "metadata": "https://example.com/datasheet.pdf",
    }


@pytest.fixture
def examples_dir():
    """Return the path to the examples directory."""
    return Path(__file__).parent.parent / "examples"


@pytest.fixture
def examples_schemas_dir():
    """Return the path to the examples/schemas directory."""
    return Path(__file__).parent.parent / "examples" / "schemas"


@pytest.fixture
def sample_entities_file():
    """Return the path to the sample entities JSON file."""
    return Path(__file__).parent.parent / "examples" / "sample_entities.json"


@pytest.fixture
def sample_entities(sample_entities_file):
    """Load and return sample entities from the examples file."""
    if not sample_entities_file.exists():
        pytest.skip(f"Sample entities file not found: {sample_entities_file}")

    with open(sample_entities_file, encoding="utf-8") as f:
        data = json.load(f)
    return data["sample_entities"]
