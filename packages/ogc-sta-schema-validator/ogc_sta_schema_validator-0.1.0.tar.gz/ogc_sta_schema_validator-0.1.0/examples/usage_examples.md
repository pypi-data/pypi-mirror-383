# Usage Examples

This document provides practical examples of using the OGC SensorThings API Schema Validator.

## Setup

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate
```

## Basic Examples

### 1. Test Connection
```bash
# Test connection to your FROST-Server
uv run python validate.py test-connection

# With custom config
uv run python validate.py --config config/my-config.yaml test-connection
```

### 2. List Available Entities
```bash
# See what entity types are available and their counts
uv run python validate.py list-entities
```

Expected output:
```
Available Entity Types:
----------------------------------------
Things               15 entities
Sensors              8 entities
Observations         1250 entities
Datastreams          12 entities
```

### 3. Validate Schema Files
```bash
# Validate all schema files
uv run python validate.py validate-schema

# Validate specific schema
uv run python validate.py validate-schema --schema-file schemas/thing_schema.json
```

## Entity Validation Examples

### 4. Validate All Things
```bash
# Validate all Thing entities using auto-discovered schema
uv run python validate.py validate --entity-type Things

# Limit to first 10 entities
uv run python validate.py validate --entity-type Things --limit 10

# Use specific schema file
uv run python validate.py validate --entity-type Things --schema schemas/thing_schema.json
```

### 5. Validate Specific Entity
```bash
# Validate a specific Thing by ID
uv run python validate.py validate --entity-type Things --entity-id 123
```

### 6. Filter Entities
```bash
# Validate only recently created Things
uv run python validate.py validate --entity-type Things --filter "createdTime gt 2024-09-01T00:00:00Z"

# Validate only active Things
uv run python validate.py validate --entity-type Things --filter "properties/status eq 'active'"

# Validate Things in specific building
uv run python validate.py validate --entity-type Things --filter "properties/building eq 'Building A'"
```

### 7. Validate Recent Observations
```bash
# Validate observations from the last 24 hours
uv run python validate.py validate --entity-type Observations --filter "phenomenonTime gt 2024-09-21T00:00:00Z" --limit 1000

# Validate observations with specific quality flags
uv run python validate.py validate --entity-type Observations --filter "properties/qualityFlag eq 'suspicious'"
```

## Output Format Examples

### 8. Generate JSON Report
```bash
# Generate JSON report for Things
uv run python validate.py validate --entity-type Things --output-format json --output-file things_report.json

# Include valid entities in the report
uv run python validate.py validate --entity-type Things --output-format json --output-file full_report.json --include-valid
```

### 9. Generate CSV Report
```bash
# Generate CSV report for analysis in Excel/Google Sheets
uv run python validate.py validate --entity-type Sensors --output-format csv --output-file sensors_validation.csv

# CSV with only invalid entities (default)
uv run python validate.py validate --entity-type Observations --output-format csv --output-file observation_errors.csv
```

### 10. Console Output Examples
```bash
# Verbose console output
uv run python validate.py --verbose validate --entity-type Things

# Quiet output (errors only)
uv run python validate.py validate --entity-type Things 2>/dev/null
```

## Batch Validation Examples

### 11. Validate All Entity Types
```bash
# Validate all available entity types
uv run python validate.py validate-all

# Validate specific entity types only
uv run python validate.py validate-all --entity-types Things --entity-types Sensors

# Limit entities per type
uv run python validate.py validate-all --limit-per-type 100

# Generate comprehensive JSON report
uv run python validate.py validate-all --output-format json --output-file comprehensive_report.json
```

### 12. Continuous Validation
```bash
# Run validation every 30 minutes
uv run python validate.py continuous --interval 1800

# Validate specific entity types every hour
uv run python validate.py continuous --interval 3600 --entity-types Things --entity-types Sensors

# Limit entities per run to avoid overload
uv run python validate.py continuous --interval 900 --max-entities 500
```

## Configuration Examples

### 13. Custom Configuration
Create `config/production.yaml`:
```yaml
server:
  url: "https://api.example.com/FROST-Server/v1.1"
  timeout: 60
  username: "validator"
  password: "secret"

validation:
  batch_size: 50
  stop_on_error: true

entity_settings:
  Things:
    batch_size: 25
    schema_file: "custom_thing_schema.json"
  Observations:
    filter: "phenomenonTime gt 2024-01-01T00:00:00Z"
    batch_size: 200
```

Use the custom config:
```bash
uv run python validate.py --config config/production.yaml validate --entity-type Things
```

### 14. Environment-Specific Validation
```bash
# Development environment
uv run python validate.py --config config/dev-config.yaml validate-all

# Staging environment
uv run python validate.py --config config/staging-config.yaml validate-all

# Production environment (with stricter validation)
uv run python validate.py --config config/prod-config.yaml validate-all
```

## Advanced Examples

### 15. Complex Filtering
```bash
# Validate Things in multiple buildings
uv run python validate.py validate --entity-type Things --filter "(properties/building eq 'Building A') or (properties/building eq 'Building B')"

# Validate Observations with quality issues
uv run python validate.py validate --entity-type Observations --filter "properties/qualityFlag ne 'good'"

# Validate Sensors due for calibration
uv run python validate.py validate --entity-type Sensors --filter "properties/nextCalibrationDate lt now()"
```

### 16. Integration with Other Tools
```bash
# Export validation results for further analysis
uv run python validate.py validate --entity-type Things --output-format json --output-file results.json

# Process results with jq
uv run python validate.py validate --entity-type Things --output-format json | jq '.results[] | select(.isValid == false)'

# Count validation errors
uv run python validate.py validate --entity-type Things --output-format json | jq '.summary.total_errors'

# Get entities with specific error types (e.g., missing required fields)
uv run python validate.py validate --entity-type Things --output-format json | jq '.results[] | select(.errors[] | .validator == "required")'
```

### 17. Automated Monitoring Script
Create `monitor.sh`:
```bash
#!/bin/bash
set -e

echo "Starting daily validation check..."

# Validate critical entity types
for entity_type in Things Sensors Datastreams; do
    echo "Validating $entity_type..."

    uv run python validate.py validate \
        --entity-type "$entity_type" \
        --output-format json \
        --output-file "reports/daily_${entity_type}_$(date +%Y%m%d).json"

    # Check if validation passed
    if [ $? -eq 0 ]; then
        echo "✅ $entity_type validation passed"
    else
        echo "❌ $entity_type validation failed"
        # Send alert or notification here
    fi
done

echo "Daily validation check completed"
```

### 18. Testing with Sample Data
```bash
# Test the validation engine with included sample data
cd examples
uv run python test_validation.py

# This will run validation tests without requiring a live FROST-Server
```

### 19. Schema Development Workflow
```bash
# 1. Create a new schema
cp schemas/thing_schema.json schemas/my_custom_schema.json

# 2. Edit the schema file
# ... modify the schema ...

# 3. Validate the schema syntax
uv run python validate.py validate-schema --schema-file schemas/my_custom_schema.json

# 4. Test with sample entities
uv run python validate.py validate --entity-type Things --schema schemas/my_custom_schema.json --limit 5

# 5. Deploy to production config
# Update config/production.yaml to use the new schema
```

### 20. Performance Optimization
```bash
# For large datasets, optimize batch size
uv run python validate.py validate --entity-type Observations --limit 10000 --config config/high-performance.yaml

# Use filtering to reduce dataset size
uv run python validate.py validate --entity-type Observations --filter "phenomenonTime gt 2024-09-01T00:00:00Z"

# Monitor performance
time uv run python validate.py validate --entity-type Things
```

## Error Handling Examples

### 21. Handling Connection Issues
```bash
# Test connection first
if uv run python validate.py test-connection; then
    echo "Connection OK, proceeding with validation"
    uv run python validate.py validate --entity-type Things
else
    echo "Connection failed, check server configuration"
    exit 1
fi
```

### 22. Handling Large Datasets
```bash
# Process large datasets in chunks
for i in {0..10}; do
    skip=$((i * 1000))
    echo "Processing chunk $i (skip $skip)..."

    # Note: Skip/offset functionality would need to be added to the tool
    uv run python validate.py validate --entity-type Observations --limit 1000 --output-file "chunk_$i.json"
done

# Combine results
jq -s 'add' chunk_*.json > combined_results.json
```

## Reporting Examples

### 23. Daily Quality Report
```bash
#!/bin/bash
# daily_quality_report.sh

DATE=$(date +%Y-%m-%d)
REPORT_DIR="reports/$DATE"
mkdir -p "$REPORT_DIR"

echo "Generating daily quality report for $DATE"

# Generate reports for each entity type
for entity_type in Things Sensors Observations Datastreams; do
    uv run python validate.py validate \
        --entity-type "$entity_type" \
        --output-format json \
        --output-file "$REPORT_DIR/${entity_type,,}_report.json" \
        --include-valid
done

# Generate summary
uv run python validate.py validate-all \
    --output-format console \
    --output-file "$REPORT_DIR/summary.txt"

echo "Reports generated in $REPORT_DIR"
```

### 24. Error Trend Analysis
```bash
# Generate daily validation reports
for days in {1..7}; do
    date_string=$(date -d "$days days ago" +%Y-%m-%d)

    uv run python validate.py validate \
        --entity-type Observations \
        --filter "phenomenonTime gt ${date_string}T00:00:00Z and phenomenonTime lt ${date_string}T23:59:59Z" \
        --output-format json \
        --output-file "trends/observations_$date_string.json"
done

# Analyze trends (would require additional scripting)
python analyze_trends.py trends/observations_*.json
```

These examples demonstrate the flexibility and power of the OGC SensorThings API Schema Validator for various use cases from simple entity validation to complex monitoring and reporting workflows.