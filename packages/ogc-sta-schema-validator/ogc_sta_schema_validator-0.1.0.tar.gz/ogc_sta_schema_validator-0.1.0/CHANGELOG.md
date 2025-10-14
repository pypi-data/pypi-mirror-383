# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-10-11

### Added
- Initial release of OGC SensorThings API Schema Validator
- Core validation engine with JSON Schema support (Draft 2020-12)
- Support for all SensorThings API entity types (Things, Sensors, Observations, etc.)
- Multiple authentication methods (Basic Auth, Bearer token, Keycloak OIDC)
- Flexible configuration system (YAML, environment variables, CLI arguments)
- Multiple output formats (console, JSON, CSV)
- Continuous validation mode for monitoring
- CLI commands:
  - `validate` - Validate specific entity types
  - `validate-all` - Validate all entity types
  - `continuous` - Run continuous validation
  - `test-connection` - Test server connectivity
  - `validate-schema` - Validate schema files
  - `list-entities` - List available entity types
- Docker support with multi-platform images
- Docker Compose configuration for easy deployment
- GitHub Actions CI/CD pipeline
- Comprehensive documentation and examples
- Example validation schemas for common entity types

### Features
- Nested property validation with dot notation
- OData filtering support
- Batch processing with configurable sizes
- Error aggregation and detailed reporting
- Schema auto-discovery
- Multi-format report generation

[unreleased]: https://github.com/janbeckert/ogc-sta-schema-validator/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/janbeckert/ogc-sta-schema-validator/releases/tag/v0.1.0
