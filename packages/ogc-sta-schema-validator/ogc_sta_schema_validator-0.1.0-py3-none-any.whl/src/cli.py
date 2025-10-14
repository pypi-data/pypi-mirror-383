#!/usr/bin/env python3
"""
OGC SensorThings API Schema Validator - Command Line Interface

This tool validates SensorThings API entities against configurable schemas.
It can validate individual entities, entity types, or run continuous validation.
"""

import logging
import sys
import time
from typing import Optional

import click

from .api_client import SensorThingsAPIClient
from .auth import AuthenticationError, NoAuth, create_auth_strategy
from .config import load_config
from .runner import ValidationRunner
from .schema_loader import SchemaLoader


def setup_logging(level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(level=getattr(logging, level.upper()), format=log_format, handlers=handlers)


@click.group(context_settings={"show_default": True})
@click.option(
    "--config",
    "-c",
    default="config/config.yaml",
    envvar="VALIDATOR_CONFIG_FILE",
    help="Configuration file path",
    show_default=True,
)
@click.option(
    "--server-url",
    envvar="VALIDATOR_SERVER__URL",
    help="SensorThings API server URL (overrides config file)",
)
@click.option(
    "--timeout",
    type=int,
    envvar="VALIDATOR_SERVER__TIMEOUT",
    help="Request timeout in seconds (overrides config file)",
)
@click.option(
    "--batch-size",
    type=int,
    envvar="VALIDATOR_VALIDATION__BATCH_SIZE",
    help="Batch size for validation (overrides config file)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config, server_url, timeout, batch_size, verbose):
    """OGC SensorThings API Schema Validator.

    Configuration can be provided via:
      1. CLI arguments (highest priority)
      2. Environment variables (prefix: VALIDATOR_)
      3. YAML configuration file
      4. Default values (lowest priority)

    Examples:
      # Using config file only
      validate.py --config config/config.yaml test-connection

      # Override server URL via CLI
      validate.py --server-url http://example.com/v1.1 test-connection

      # Override via environment variable
      export VALIDATOR_SERVER__URL=http://example.com/v1.1
      validate.py test-connection
    """
    ctx.ensure_object(dict)

    # Load configuration from all sources (YAML + env vars)
    try:
        config_manager = load_config(config_file=config, validate=True)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)

    # Apply CLI overrides (highest priority)
    if server_url:
        config_manager.set_override("SERVER.URL", server_url)
    if timeout:
        config_manager.set_override("SERVER.TIMEOUT", timeout)
    if batch_size:
        config_manager.set_override("VALIDATION.BATCH_SIZE", batch_size)

    ctx.obj["config"] = config_manager

    log_level = "DEBUG" if verbose else config_manager.get("LOGGING.LEVEL", "INFO")
    log_file = config_manager.get("LOGGING.FILE")
    setup_logging(log_level, log_file)

    server_url_final = config_manager.get("SERVER.URL")
    server_timeout = config_manager.get("SERVER.TIMEOUT", 30)

    try:
        auth_config_dict = config_manager.settings.get("SERVER", {})

        auth_config = None
        if isinstance(auth_config_dict, dict):
            auth_config = auth_config_dict.get("auth") or auth_config_dict.get("AUTH")

        auth_strategy = create_auth_strategy(auth_config) if auth_config else NoAuth()

    except (ValueError, AuthenticationError) as e:
        click.echo(f"Authentication configuration error: {e}", err=True)
        sys.exit(1)

    ctx.obj["api_client"] = SensorThingsAPIClient(
        base_url=server_url_final,
        timeout=server_timeout,
        auth_strategy=auth_strategy,
    )

    schema_path = config_manager.get("SCHEMAS.DEFAULT_PATH", "./schemas")
    ctx.obj["schema_loader"] = SchemaLoader(schema_path)

    batch_size_final = config_manager.get("VALIDATION.BATCH_SIZE", 100)
    stop_on_error = config_manager.get("VALIDATION.STOP_ON_ERROR", False)

    ctx.obj["runner"] = ValidationRunner(
        api_client=ctx.obj["api_client"],
        schema_loader=ctx.obj["schema_loader"],
        batch_size=batch_size_final,
        stop_on_error=stop_on_error,
    )


@cli.command()
@click.pass_context
def test_connection(ctx):
    """Test connection to SensorThings API server."""
    click.echo("Testing connection to SensorThings API...")

    api_client = ctx.obj["api_client"]

    if api_client.test_connection():
        click.echo(click.style("✓ Connection successful!", fg="green"))

        try:
            api_client.get_service_root()
            entity_types = api_client.get_available_entity_types()

            click.echo(f"Server URL: {api_client.base_url}")
            click.echo(f"Available entity types: {', '.join(entity_types)}")

        except Exception as e:
            click.echo(click.style(f"Warning: Could not get service information: {e}", fg="yellow"))
    else:
        click.echo(click.style("✗ Connection failed!", fg="red"))
        sys.exit(1)


@cli.command()
@click.option(
    "--entity-type", "-t", required=True, help="Entity type to validate (Things, Sensors, etc.)"
)
@click.option("--entity-id", "-i", help="Specific entity ID to validate")
@click.option("--schema", "-s", help="Schema file to use (auto-discover if not specified)")
@click.option("--limit", "-l", type=int, help="Maximum number of entities to validate")
@click.option("--filter", "-f", help="OData filter expression")
@click.option(
    "--output-format",
    type=click.Choice(["console", "json", "csv"]),
    envvar="VALIDATOR_OUTPUT__FORMAT",
    help="Output format",
    show_default="from config",
)
@click.option("--output-file", "-o", help="Output file path")
@click.option("--include-valid", is_flag=True, help="Include valid entities in output")
@click.pass_context
def validate(
    ctx, entity_type, entity_id, schema, limit, filter, output_format, output_file, include_valid
):
    """Validate SensorThings API entities."""
    runner = ctx.obj["runner"]
    config = ctx.obj["config"]

    # Apply configuration defaults
    if not output_format:
        output_format = config.get("OUTPUT.FORMAT", "console")

    if include_valid is None:
        include_valid = config.get("OUTPUT.INCLUDE_VALID_ENTITIES", False)

    # Get entity-specific settings
    entity_settings_key = f"ENTITY_SETTINGS.{entity_type}"
    entity_settings = config.settings.get(entity_settings_key, {})

    if not schema and isinstance(entity_settings, dict):
        schema = entity_settings.get("SCHEMA_FILE") or entity_settings.get("schema_file")
    if not filter and isinstance(entity_settings, dict):
        filter = entity_settings.get("FILTER") or entity_settings.get("filter")

    try:
        if entity_id:
            # Validate specific entity
            click.echo(f"Validating {entity_type}({entity_id})...")
            result = runner.validate_specific_entity(entity_type, entity_id, schema)

            if result:
                results = [result]
            else:
                click.echo(f"Entity not found: {entity_type}({entity_id})", err=True)
                sys.exit(1)
        else:
            # Validate entity type
            click.echo(f"Validating {entity_type} entities...")
            if limit:
                click.echo(f"Limit: {limit} entities")
            if filter:
                click.echo(f"Filter: {filter}")

            results = runner.validate_entity_type(entity_type, schema, limit, filter)

        # Generate report
        if results:
            report = runner.generate_report(results, output_format, output_file, include_valid)

            if not output_file:
                click.echo(report)

            total = len(results)
            valid = sum(1 for r in results if r.is_valid)
            invalid = total - valid

            click.echo(click.style("\nValidation Summary:", fg="blue"))
            click.echo(f"  Total: {total}")
            click.echo(
                f"  Valid: {valid} ({valid / total * 100:.1f}%)" if total > 0 else "  Valid: 0"
            )
            click.echo(
                f"  Invalid: {invalid} ({invalid / total * 100:.1f}%)"
                if total > 0
                else "  Invalid: 0"
            )

            if invalid > 0:
                sys.exit(1)
        else:
            click.echo(click.style("No entities found to validate.", fg="yellow"))

    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--entity-types",
    "-t",
    multiple=True,
    help="Specific entity types to validate (validate all if not specified)",
)
@click.option("--limit-per-type", "-l", type=int, help="Maximum entities per type")
@click.option(
    "--output-format",
    type=click.Choice(["console", "json", "csv"]),
    envvar="VALIDATOR_OUTPUT__FORMAT",
    help="Output format",
    show_default="from config",
)
@click.option("--output-file", "-o", help="Output file path")
@click.option("--include-valid", is_flag=True, help="Include valid entities in output")
@click.pass_context
def validate_all(ctx, entity_types, limit_per_type, output_format, output_file, include_valid):
    """Validate all entity types."""
    runner = ctx.obj["runner"]
    config = ctx.obj["config"]

    # Apply configuration defaults
    if not output_format:
        output_format = config.get("OUTPUT.FORMAT", "console")

    if include_valid is None:
        include_valid = config.get("OUTPUT.INCLUDE_VALID_ENTITIES", False)

    # Convert tuple to list, but treat empty list as None for auto-discovery
    entity_types_list = list(entity_types) if entity_types else None

    try:
        click.echo("Validating all entity types...")
        all_results = runner.validate_all_entity_types(entity_types_list, limit_per_type)

        # Combine all results
        combined_results = []
        for _entity_type, results in all_results.items():
            combined_results.extend(results)

        if combined_results:
            # Generate report
            report = runner.generate_report(
                combined_results, output_format, output_file, include_valid
            )

            if not output_file:
                click.echo(report)

            # Show summary per entity type
            click.echo(click.style("\nValidation Summary by Entity Type:", fg="blue"))
            for entity_type, results in all_results.items():
                total = len(results)
                valid = sum(1 for r in results if r.is_valid)

                click.echo(
                    f"  {entity_type}: {valid}/{total} valid ({valid / total * 100:.1f}%)"
                    if total > 0
                    else f"  {entity_type}: 0/0"
                )
        else:
            click.echo(click.style("No entities found to validate.", fg="yellow"))

    except Exception as e:
        click.echo(f"Validation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--interval",
    "-i",
    type=int,
    envvar="VALIDATOR_CONTINUOUS__INTERVAL",
    help="Validation interval in seconds",
    show_default="from config",
)
@click.option(
    "--entity-types",
    "-t",
    multiple=True,
    help="Entity types to validate continuously",
    show_default="from config",
)
@click.option(
    "--max-entities",
    "-m",
    type=int,
    envvar="VALIDATOR_CONTINUOUS__MAX_ENTITIES_PER_RUN",
    help="Maximum entities per validation run",
    show_default="from config",
)
@click.pass_context
def continuous(ctx, interval, entity_types, max_entities):
    """Run continuous validation."""
    config = ctx.obj["config"]
    runner = ctx.obj["runner"]

    if not interval:
        interval = config.get("CONTINUOUS.INTERVAL", 1800)

    if not entity_types:
        entity_types_config = config.get(
            "CONTINUOUS.ENTITY_TYPES", ["Things", "Sensors", "Observations"]
        )
        # Handle both list and string formats
        if isinstance(entity_types_config, str):
            entity_types = [entity_types_config]
        else:
            entity_types = entity_types_config

    if not max_entities:
        max_entities = config.get("CONTINUOUS.MAX_ENTITIES_PER_RUN", 1000)

    click.echo("Starting continuous validation...")
    click.echo(f"  Interval: {interval} seconds ({interval // 60} minutes)")
    click.echo(f"  Entity types: {', '.join(entity_types)}")
    click.echo(f"  Max entities per run: {max_entities}")
    click.echo("Press Ctrl+C to stop")

    try:
        while True:
            start_time = time.time()
            click.echo(f"\n--- Validation run at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")

            try:
                all_results = runner.validate_all_entity_types(
                    list(entity_types), limit_per_type=max_entities
                )

                # Print summary
                for entity_type, results in all_results.items():
                    total = len(results)
                    valid = sum(1 for r in results if r.is_valid)
                    invalid = total - valid

                    click.echo(f"{entity_type}: {valid}/{total} valid")

                    if invalid > 0:
                        click.echo(
                            click.style(f"  {invalid} entities with validation errors", fg="red")
                        )

            except Exception as e:
                click.echo(f"Validation run failed: {e}", err=True)

            elapsed = time.time() - start_time
            sleep_time = max(0, interval - elapsed)

            if sleep_time > 0:
                click.echo(f"Sleeping for {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        click.echo("\nContinuous validation stopped.")


@cli.command()
@click.option("--schema-file", "-s", help="Specific schema file to validate")
@click.pass_context
def validate_schema(ctx, schema_file):
    """Validate schema files."""
    schema_loader = ctx.obj["schema_loader"]

    if schema_file:
        click.echo(f"Validating schema: {schema_file}")
        errors = schema_loader.validate_schema_file(schema_file)

        if errors:
            click.echo(click.style("Schema validation failed:", fg="red"))
            for error in errors:
                click.echo(f"  - {error}")
            sys.exit(1)
        else:
            click.echo(click.style("✓ Schema is valid!", fg="green"))

            info = schema_loader.get_schema_info(schema_file)
            click.echo(f"Entity Type: {info.get('entity_type', 'Unknown')}")
            click.echo(f"Version: {info.get('version', 'Unknown')}")
            click.echo(f"Rules: {info.get('rule_count', 0)}")
    else:
        click.echo("Discovering and validating all schemas...")
        schemas = schema_loader.discover_schemas()

        if not schemas:
            click.echo(click.style("No schemas found.", fg="yellow"))
            return

        for entity_type, schema in schemas.items():
            # The fact that it was loaded means it's valid
            version = schema.get("x-version") or schema.get("version", "unknown")
            click.echo(click.style(f"✓ {entity_type}: {version}", fg="green"))

        click.echo(f"\nFound {len(schemas)} valid schemas")


@cli.command()
@click.pass_context
def list_entities(ctx):
    """List available entity types and their counts."""
    api_client = ctx.obj["api_client"]

    try:
        entity_types = api_client.get_available_entity_types()

        click.echo("Available Entity Types:")
        click.echo("-" * 40)

        for entity_type in entity_types:
            try:
                count = api_client.get_entity_count(entity_type)
                click.echo(f"{entity_type:<20} {count:>10} entities")
            except Exception:
                click.echo(f"{entity_type:<20} {'Error':>10} (Could not get count)")

    except Exception as e:
        click.echo(f"Failed to list entities: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
