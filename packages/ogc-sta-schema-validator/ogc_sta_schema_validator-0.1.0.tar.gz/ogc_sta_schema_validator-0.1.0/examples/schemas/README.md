# Example Schema Files

This directory contains generic example schema files for validating SensorThings API entities. These schemas demonstrate the validation capabilities of the tool using standard JSON Schema Draft 2020-12 format.

## Available Schemas

- **thing_schema.json** - Validation for Thing entities
- **sensor_schema.json** - Validation for Sensor entities
- **observation_schema.json** - Validation for Observation entities
- **datastream_schema.json** - Validation for Datastream entities

## Using These Schemas

### Option 1: Copy to Your Schema Directory

```bash
# Copy example schemas to your schemas directory
cp examples/schemas/*.json schemas/
```

### Option 2: Reference Directly

```bash
# Validate using an example schema
uv run python validate.py validate \
  --entity-type Things \
  --schema examples/schemas/thing_schema.json
```

### Option 3: Create Custom Schemas

Create your own schema files in the `schemas/` directory (which is gitignored):

```bash
# Create your custom schema
cp examples/schemas/thing_schema.json schemas/my_thing_schema.json
# Edit schemas/my_thing_schema.json with your organization-specific rules
```

## Schema Customization

These example schemas are intentionally generic. For production use, you should:

1. **Add organization-specific patterns**: Add regex patterns for IDs, codes, etc.
2. **Define required properties**: Specify which custom properties are mandatory
3. **Add enumerations**: Define allowed values for status, type, etc.
4. **Set validation levels**: Use `x-severity` to mark rules as "error" or "warning"
5. **Customize error messages**: Use `x-errorMessage` for clear validation feedback

## Example Customizations

### Adding ID Pattern Validation

```json
{
  "properties": {
    "properties": {
      "properties": {
        "thingId": {
          "type": "string",
          "pattern": "^org\\.domain\\.prefix\\..+",
          "x-errorMessage": "Thing ID must start with 'org.domain.prefix.' prefix"
        }
      }
    }
  }
}
```

### Making Custom Properties Required

```json
{
  "properties": {
    "properties": {
      "required": ["thingId", "installationDate", "status"],
      "properties": {
        "thingId": {"type": "string"},
        "installationDate": {"type": "string", "format": "date-time"},
        "status": {"enum": ["active", "inactive"]}
      }
    }
  }
}
```

### Using Warning vs Error Severity

```json
{
  "properties": {
    "properties": {
      "properties": {
        "owner": {
          "type": "string",
          "x-severity": "error"
        },
        "notes": {
          "type": "string",
          "x-severity": "warning"
        }
      }
    }
  }
}
```

## JSON Schema Resources

- [JSON Schema Specification](https://json-schema.org/specification)
- [Understanding JSON Schema](https://json-schema.org/understanding-json-schema/)
- [JSON Schema Validator](https://www.jsonschemavalidator.net/)

## Notes

- The `schemas/` directory is gitignored to keep your organization-specific schemas private
- Always test your schemas with sample data before using in production
- Use the `validate-schema` command to check schema validity
