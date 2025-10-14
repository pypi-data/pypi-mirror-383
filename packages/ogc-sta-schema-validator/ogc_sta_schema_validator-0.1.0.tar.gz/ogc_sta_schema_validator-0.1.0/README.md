# OGC SensorThings API Schema Validator

[![CI/CD Pipeline](https://github.com/janbeckert/ogc-sta-schema-validator/actions/workflows/ci.yml/badge.svg)](https://github.com/janbeckert/ogc-sta-schema-validator/actions/workflows/ci.yml)

## Abstract

This tool provides automated validation of entities stored in [OGC SensorThings API](https://www.ogc.org/standards/sensorthings) implementations against organization-specific JSON Schema definitions. The OGC SensorThings API is an open geospatial standard for interconnecting Internet of Things (IoT) devices, data, and applications over the Web, providing a unified framework for managing sensor data and observations.

As SensorThings API implementations grow in scale and complexity, ensuring data quality and compliance with organizational requirements becomes critical. This validation tool addresses the need for systematic quality assurance by enabling configurable, schema-driven validation of entity properties beyond the base OGC specification requirements.

## Standards & Specifications

This implementation is designed to work with:

- **[OGC SensorThings API Part 1: Sensing (Version 1.1)](https://docs.ogc.org/is/18-088/18-088.html)** - The core specification defining the data model and REST API for IoT sensor observations (OGC Document 18-088)
- **[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core.html)** - The validation schema language used to define entity constraints

## Compatible Implementations

This tool has been tested with:

- **[FROST-Server](https://github.com/FraunhoferIOSB/FROST-Server)** - The Fraunhofer IOSB reference implementation of the OGC SensorThings API, widely used in production environments
- Any OGC SensorThings API 1.0/1.1 compliant server implementation

## Overview

### SensorThings API Data Model

The OGC SensorThings API defines a standard data model consisting of eight core entity types that capture the "who, what, when, where, and how" of sensor observations:

- **Thing** - The object of interest (e.g., a weather station, vehicle, building)
- **Location** - The geographic location of a Thing
- **HistoricalLocation** - Historical location information
- **Datastream** - A collection of observations grouped by sensor and observed property
- **Sensor** - The instrument or procedure that produced the observations
- **ObservedProperty** - The phenomenon being measured (e.g., temperature, humidity)
- **Observation** - The actual measurement or result
- **FeatureOfInterest** - The feature that is the subject of an observation

This validator enables organizations to enforce custom validation rules on any of these entity types through JSON Schema definitions.

## Features

- **Standards-Based Validation**: Implements JSON Schema Draft 2020-12 for validation rule definition
- **Comprehensive Coverage**: Supports all OGC SensorThings API entity types
- **Flexible Validation Scope**: Validate individual entities, entity types, or entire datasets
- **Multiple Output Formats**: Console, JSON, and CSV reporting for different use cases
- **Continuous Monitoring**: Scheduled validation runs for ongoing data quality assurance
- **Nested Property Support**: Full validation of nested object structures and custom properties
- **Custom Extensions**: Organization-specific error messages and severity levels
- **Configurable Architecture**: YAML-based configuration with entity-specific settings
- **Production Ready**: Docker images, Docker Compose, and CI/CD workflows
- **Authentication Support**: Multiple authentication methods including Basic Auth, Bearer tokens, and Keycloak OIDC

## Quick Start

### 🎯 Quick Demo (5 Minutes)

Want to see the validator in action right away? Try the fully automated demo:

```bash
# Clone the repository
git clone https://github.com/janbeckert/ogc-sta-schema-validator.git
cd ogc-sta-schema-validator

# Run the demo (requires Docker and Docker Compose)
./demo.sh
```

This will:
- Start a complete FROST-Server environment
- Provision sample entities (both valid and invalid)
- Run validation and show results with intentional errors
- Demonstrate the validator catching real data quality issues

**Or use Docker Compose directly:**

```bash
docker compose up --build
```

The demo shows validation catching common errors like missing required fields, invalid data types, out of range values, and malformed dates.

---

### Option 1: Docker (Recommended for Quick Testing)

The easiest way to get started is using Docker:

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/janbeckert/ogc-sta-schema-validator:latest

# Or build locally
docker build -t ogc-sta-schema-validator .

# Run a simple test (show help)
docker run --rm ogc-sta-schema-validator

# Test connection to a FROST-Server
docker run --rm \
  -e VALIDATOR_SERVER__URL=http://your-server:8080/FROST-Server/v1.1 \
  ogc-sta-schema-validator \
  test-connection

# Validate with your own config and schemas
docker run --rm \
  -v $(pwd)/config:/app/config:ro \
  -v $(pwd)/schemas:/app/schemas:ro \
  -v $(pwd)/output:/app/output \
  ogc-sta-schema-validator \
  validate --entity-type Things --output-file /app/output/report.json
```

### Option 2: Local Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup the project
cd ogc-sta-schema-validator

# Install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate     # On Windows
```

### Configuration

1. Copy the example configuration file:
```bash
cp config/config.example.yaml config/config.yaml
```

2. Edit `config/config.yaml` with your server details:
```yaml
server:
  url: "http://your-frost-server:8080/FROST-Server/v1.1"
```

3. Configure authentication if required (see config file for examples)

4. Set up your validation schemas:
```bash
# Option 1: Copy example schemas
cp examples/schemas/*.json schemas/

# Option 2: Create custom schemas in schemas/ directory
```

### Basic Usage

```bash
# Test connection to your FROST-Server
uv run ogc-sta-validate test-connection

# List available entity types
uv run ogc-sta-validate list-entities

# Validate all Things
uv run ogc-sta-validate validate --entity-type Things

# Validate a specific Thing
uv run ogc-sta-validate validate --entity-type Things --entity-id 123

# Validate with custom schema
uv run ogc-sta-validate validate --entity-type Things --schema schemas/thing_schema.json

# Generate JSON report
uv run ogc-sta-validate validate --entity-type Things --output-format json --output-file report.json

# Validate all entity types
uv run ogc-sta-validate validate-all

# Run continuous validation (every 30 minutes)
uv run ogc-sta-validate continuous --interval 1800
```

## Configuration

The tool supports **multiple configuration sources** with the following precedence (highest to lowest):

1. **CLI arguments** (highest priority)
2. **Environment variables**
3. **YAML configuration file**
4. **Default values** (lowest priority)

This flexible approach allows you to:
- Store sensitive credentials in environment variables
- Override configuration temporarily via CLI arguments
- Maintain base configuration in YAML files
- Use different configurations across environments (dev/staging/prod)

### Method 1: YAML Configuration File

The primary configuration method uses YAML files. This is covered in the Quick Start section above.

```yaml
# config/config.yaml
server:
  url: "http://localhost:8080/FROST-Server/v1.1"
  timeout: 30
  auth:
    method: "basic"
    username: "user"
    password: "pass"

validation:
  batch_size: 100
  stop_on_error: false
```

See `config/config.example.yaml` for a complete configuration template with all available options.

### Method 2: Environment Variables

Environment variables can override YAML configuration values. This is especially useful for:
- **Sensitive data**: Store credentials securely outside of config files
- **CI/CD pipelines**: Configure differently across environments
- **Docker deployments**: Use Docker environment variables

#### Naming Convention

Environment variables use the prefix `VALIDATOR_` and double underscores (`__`) for nested values:

```bash
# Format: VALIDATOR_<SECTION>__<KEY>
VALIDATOR_SERVER__URL=http://example.com/v1.1
VALIDATOR_SERVER__TIMEOUT=60
VALIDATOR_VALIDATION__BATCH_SIZE=200
```

#### Quick Setup

```bash
# Copy the example environment file
cp .env.example .env
```

#### Example Environment Variables

```bash
# Server configuration
export VALIDATOR_SERVER__URL="http://example.com/FROST-Server/v1.1"
export VALIDATOR_SERVER__TIMEOUT=60

# Authentication (recommended for sensitive credentials)
export VALIDATOR_SERVER__AUTH__METHOD="basic"
export VALIDATOR_SERVER__AUTH__USERNAME="myuser"
export VALIDATOR_SERVER__AUTH__PASSWORD="mypassword"

# Validation settings
export VALIDATOR_VALIDATION__BATCH_SIZE=200
export VALIDATOR_OUTPUT__FORMAT="json"

# Now run the tool - environment variables will be used
uv run ogc-sta-validate test-connection
```

See `.env.example` for all available environment variables.

### Method 3: CLI Arguments

CLI arguments provide the highest precedence.

#### Common CLI Options

```bash
# Override server URL
uv run ogc-sta-validate --server-url http://example.com/v1.1 test-connection

# Override timeout
uv run ogc-sta-validate --timeout 60 test-connection

# Override batch size
uv run ogc-sta-validate --batch-size 200 validate --entity-type Things

# Combine multiple overrides
uv run ogc-sta-validate \
  --server-url http://example.com/v1.1 \
  --timeout 60 \
  --batch-size 200 \
  validate --entity-type Things
```

#### Command-Specific Options

Each command also has specific options:

```bash
# Validate command options
uv run ogc-sta-validate validate \
  --entity-type Things \
  --limit 100 \
  --output-format json \
  --output-file report.json \
  --filter "properties/status eq 'active'"

# Continuous validation options
uv run ogc-sta-validate continuous \
  --interval 3600 \
  --entity-types Things \
  --entity-types Sensors \
  --max-entities 500
```

### Getting Help

View all available CLI options:

```bash
# Main help
uv run ogc-sta-validate --help

# Command-specific help
uv run ogc-sta-validate validate --help
uv run ogc-sta-validate continuous --help
```

## Validation Methodology

### Approach

This tool implements a **schema-driven validation approach** that operates independently of the OGC SensorThings API server's internal validation. While the SensorThings API specification defines mandatory properties and data types, organizations often have additional requirements such as:

- Custom property schemas for domain-specific metadata
- Enumerated value constraints for controlled vocabularies
- Pattern matching for identifiers following organizational conventions
- Range validation for sensor measurements
- Date/time format requirements beyond ISO 8601

The validation engine retrieves entities via the SensorThings API's standardized REST interface and applies JSON Schema rules without modifying the source data, making it suitable for both development and production environments.

### Validation Process

1. **Entity Retrieval**: Fetches entities from the SensorThings API server using HTTP GET requests with optional [OData filtering](https://www.odata.org/documentation/)
2. **Schema Loading**: Loads JSON Schema definitions from the local filesystem, matched by entity type
3. **Rule Application**: Applies JSON Schema validation rules using the `jsonschema` library
4. **Error Aggregation**: Collects validation errors with property paths and rule type information
5. **Report Generation**: Produces detailed reports in multiple formats (console, JSON, CSV)

### Architecture

The validator implements a modular architecture with separation of concerns:

```
┌─────────────────┐
│  CLI Interface  │  Command-line interface (Click framework)
│   (cli.py)      │
└────────┬────────┘
         │
         ├──┬──────────────────────────────────────────────────┐
         │  │                                                  │
┌────────▼──────────┐  ┌──────────────┐  ┌──────────────────┐  │
│   API Client      │  │Schema Loader │  │ Validator Engine │  │
│(api_client.py)    │  │(loader.py)   │  │ (validator.py)   │  │
│                   │  │              │  │                  │  │
│ - HTTP requests   │  │- JSON Schema │  │ - Rule engine    │  │
│ - Pagination      │  │  discovery   │  │ - Error handling │  │
│ - Auth strategies │  │- Validation  │  │ - Type checking  │  │
│ - OData filters   │  │              │  │                  │  │
└────────┬──────────┘  └──────┬───────┘  └────────┬─────────┘  │
         │                    │                   │            │
         │                    │                   │            │
         └────────────────────┴───────────────────┴────────────┤
                                                               │
                            ┌──────────────────────────────────▼┐
                            │      Validation Runner            │
                            │         (runner.py)               │
                            │                                   │
                            │ - Orchestration & batch processing│
                            │ - Multi-format report generation  │
                            │ - Error/warning categorization    │
                            └───────────────────────────────────┘
```

## JSON Schema Format

Validation schemas use standard JSON Schema Draft 2020-12. This example demonstrates common validation features:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.sensorthings.org/things.json",
  "title": "Things Schema",
  "type": "object",
  "required": ["name", "description"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 100,
      "description": "Thing name is mandatory",
      "x-errorMessage": "Thing must have a non-empty name (1-100 characters)"
    },
    "description": {
      "type": "string",
      "minLength": 1
    },
    "properties": {
      "type": "object",
      "required": ["thingId"],
      "properties": {
        "thingId": {
          "type": "string",
          "minLength": 1
        },
        "status": {
          "enum": ["active", "inactive", "maintenance"],
          "description": "Status must be one of the allowed values"
        },
        "code": {
          "type": "string",
          "pattern": "^[A-Z]{2}[0-9]{4}$",
          "description": "Building code format: two uppercase letters + four digits"
        },
        "temperature": {
          "type": "number",
          "minimum": -50,
          "maximum": 100
        },
        "timestamp": {
          "type": "string",
          "format": "date-time"
        },
        "coordinates": {
          "type": "array",
          "minItems": 2,
          "maxItems": 3,
          "description": "Coordinates [longitude, latitude, altitude?]"
        },
        "tags": {
          "type": "array",
          "minItems": 1,
          "maxItems": 10
        }
      }
    }
  }
}
```

See [JSON Schema specification](https://json-schema.org/draft/2020-12/json-schema-validation.html) for complete documentation.

### Custom Extensions

This validator supports custom JSON Schema extension fields (prefixed with `x-` per JSON Schema conventions) to enhance validation functionality:

#### Schema-Level Extensions

**`x-version`** (string, optional): Schema version identifier for tracking and documentation
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "x-version": "2.0.0",
  "x-entityType": "Things",
  "title": "Things Schema"
}
```

**`x-entityType`** (string, optional): Specifies the SensorThings API entity type this schema validates
```json
{
  "x-entityType": "Things"
}
```
Used for entity type identification when the schema filename doesn't match the entity type.

#### Property-Level Extensions

**`x-errorMessage`** (string, optional): Custom error message shown when validation fails
```json
{
  "type": "string",
  "pattern": "^de\\.sn\\.stlp\\..+",
  "x-errorMessage": "ID must start with Leipzig prefix (de.sn.stlp.)"
}
```

**`x-severity`** (string, optional): Validation severity level - either `"error"` or `"warning"`
```json
{
  "type": "string",
  "pattern": "^[A-Z]{2}[0-9]{4}$",
  "x-errorMessage": "Recommended format: XX9999",
  "x-severity": "warning"
}
```

- **`error`** (default): Validation failure causes entity to be marked as invalid
- **`warning`**: Validation failure is reported but entity remains valid

#### Complete Example

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://schemas.sensorthings.org/things.json",
  "x-version": "2.0.0",
  "x-entityType": "Things",
  "title": "Things Schema",
  "type": "object",
  "required": ["name"],
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "x-errorMessage": "Thing must have a non-empty name"
    },
    "properties": {
      "type": "object",
      "properties": {
        "thingId": {
          "type": "string",
          "pattern": "^de\\.sn\\.stlp\\..+",
          "x-errorMessage": "Thing ID must use Leipzig prefix",
          "x-severity": "error"
        },
        "installationDate": {
          "type": "string",
          "format": "date-time",
          "x-errorMessage": "Installation date should be in ISO 8601 format",
          "x-severity": "warning"
        }
      }
    }
  }
}
```

## CLI Commands

### test-connection
Test connection to the SensorThings API server.

### validate
Validate entities of a specific type.

Options:
- `--entity-type`, `-t`: Entity type to validate (required)
- `--entity-id`, `-i`: Specific entity ID to validate
- `--schema`, `-s`: Schema file to use
- `--limit`, `-l`: Maximum number of entities to validate
- `--filter`, `-f`: OData filter expression
- `--output-format`: Output format (console, json, csv)
- `--output-file`, `-o`: Output file path
- `--include-valid`: Include valid entities in output

### validate-all
Validate all entity types.

Options:
- `--entity-types`, `-t`: Specific entity types to validate
- `--limit-per-type`, `-l`: Maximum entities per type
- `--output-format`: Output format
- `--output-file`, `-o`: Output file path
- `--include-valid`: Include valid entities in output

### continuous
Run continuous validation.

Options:
- `--interval`, `-i`: Validation interval in seconds
- `--entity-types`, `-t`: Entity types to validate
- `--max-entities`, `-m`: Maximum entities per run

### validate-schema
Validate schema files.

Options:
- `--schema-file`, `-s`: Specific schema file to validate

### list-entities
List available entity types and their counts.

## Development

### Setup Development Environment
```bash
# Install with development dependencies
uv sync --dev

# Run tests
uv run pytest

# Format code and fix imports (replaces black + isort)
uv run ruff format .

# Lint code (replaces flake8)
uv run ruff check .

# Lint and auto-fix issues
uv run ruff check --fix .
```

### Adding Dependencies
```bash
# Add a new dependency
uv add requests

# Add a development dependency
uv add --dev pytest

# Update dependencies
uv sync
```

## Example Validation Schemas

The repository includes example validation schemas in `examples/schemas/` demonstrating validation patterns for common SensorThings API entity types:

- `examples/schemas/thing_schema.json` - Validation schema for Thing entities with custom property constraints
- `examples/schemas/sensor_schema.json` - Validation schema for Sensor entities with metadata requirements
- `examples/schemas/observation_schema.json` - Validation schema for Observation entities with result value constraints
- `examples/schemas/datastream_schema.json` - Validation schema for Datastream entities with unit of measurement validation

Copy these to your `schemas/` directory and customize them for your organization:

```bash
cp examples/schemas/*.json schemas/
```

See `examples/schemas/README.md` for customization guidance.

## Output Formats

### Console Output
Human-readable text format with validation summary and error details.

### JSON Output
Structured JSON format suitable for programmatic processing:
```json
{
  "summary": {
    "total_entities": 100,
    "valid_entities": 95,
    "invalid_entities": 5,
    "total_errors": 8,
    "total_warnings": 2
  },
  "results": [
    {
      "entityId": "123",
      "entityType": "Things",
      "isValid": false,
      "errors": [
        {
          "property_path": "properties.building",
          "message": "Required field is missing",
          "validator": "required"
        }
      ]
    }
  ]
}
```

### CSV Output
Tabular format suitable for spreadsheet analysis with columns:
- EntityType, EntityId, IsValid, ErrorCount, WarningCount, PropertyPath, ErrorType, Message, Severity

## Troubleshooting

### Connection Issues
- Verify the SensorThings API server URL conforms to the specification (e.g., ends with `/v1.0` or `/v1.1`)
- Check network connectivity and firewall rules
- Ensure authentication credentials are correct for your server's authentication method

### Schema Issues
- Use `validate-schema` command to check JSON Schema validity against Draft 2020-12
- Verify JSON syntax and required meta-properties (`$schema`, `type`, etc.)
- Ensure custom extensions (`x-errorMessage`, `x-severity`) follow the expected format

### Performance
- Adjust `batch_size` based on entity complexity and network latency (typical range: 50-500)
- Use OData `$filter` expressions to limit validation scope to relevant entities

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.