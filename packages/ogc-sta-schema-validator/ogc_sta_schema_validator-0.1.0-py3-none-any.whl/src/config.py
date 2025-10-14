"""
Configuration management using Dynaconf.

Supports multiple configuration sources with the following precedence:
1. CLI arguments (highest priority)
2. Environment variables (prefix: VALIDATOR_)
3. YAML configuration file
4. Default values (lowest priority)

Environment variable naming convention:
- Use double underscore for nested values: VALIDATOR_SERVER__URL
- Example: VALIDATOR_SERVER__URL=http://example.com maps to config['server']['url']
"""

from pathlib import Path
from typing import Any, Optional

from dynaconf import Dynaconf, Validator


def get_default_config_path() -> str:
    """Get the default configuration file path."""
    return str(Path(__file__).parent.parent / "config" / "config.yaml")


def create_settings(
    config_file: Optional[str] = None,
    env_file: Optional[str] = ".env",
    validate_on_load: bool = True,
) -> Dynaconf:
    """
    Create Dynaconf settings instance with validation.

    Args:
        config_file: Path to YAML configuration file. Uses default if None.
        env_file: Path to .env file for environment variables. Uses .env if exists.
        validate_on_load: Whether to validate configuration on load.

    Returns:
        Dynaconf settings instance

    Raises:
        ValueError: If configuration is invalid
    """
    if config_file is None:
        config_file = get_default_config_path()

    if env_file and not Path(env_file).exists():
        env_file = None

    validators = [
        # Server configuration
        Validator("SERVER.URL", must_exist=True, default="http://localhost:8080/FROST-Server/v1.1"),
        Validator("SERVER.TIMEOUT", must_exist=True, default=30, gte=1, lte=300),
        # Validation settings
        Validator("VALIDATION.BATCH_SIZE", must_exist=True, default=100, gte=1, lte=10000),
        Validator("VALIDATION.STOP_ON_ERROR", must_exist=True, default=False, is_type_of=bool),
        Validator("VALIDATION.INCLUDE_WARNINGS", must_exist=True, default=True, is_type_of=bool),
        # Schema settings
        Validator("SCHEMAS.DEFAULT_PATH", must_exist=True, default="./schemas"),
        Validator("SCHEMAS.AUTO_DISCOVER", must_exist=True, default=True, is_type_of=bool),
        # Output settings
        Validator(
            "OUTPUT.FORMAT",
            must_exist=True,
            default="console",
            is_in=["console", "json", "csv"],
        ),
        Validator("OUTPUT.VERBOSE", must_exist=True, default=True, is_type_of=bool),
        Validator("OUTPUT.INCLUDE_VALID_ENTITIES", must_exist=True, default=False, is_type_of=bool),
        # Logging settings
        Validator(
            "LOGGING.LEVEL",
            must_exist=True,
            default="INFO",
            is_in=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        ),
        # Continuous validation settings
        Validator("CONTINUOUS.ENABLED", must_exist=True, default=False, is_type_of=bool),
        Validator("CONTINUOUS.INTERVAL", must_exist=True, default=1800, gte=60),
        Validator(
            "CONTINUOUS.MAX_ENTITIES_PER_RUN", must_exist=True, default=1000, gte=1, lte=100000
        ),
    ]

    settings = Dynaconf(
        # Environment variables prefix
        envvar_prefix="VALIDATOR",
        # Configuration file settings
        settings_files=[config_file] if Path(config_file).exists() else [],
        # Support for .env files
        load_dotenv=True,
        dotenv_path=env_file,
        # Nested access with double underscore
        environments=False,  # We don't use environment-specific configs (dev/prod)
        # Case sensitivity
        lowercase_read=False,  # Keep uppercase keys for consistency
        # Merge strategies
        merge_enabled=True,
        # Validation
        validators=validators if validate_on_load else [],
    )

    if validate_on_load:
        try:
            settings.validators.validate()
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}") from e

    return settings


class ConfigManager:
    """
    Manages configuration with support for CLI overrides.

    This class provides a bridge between Dynaconf settings and CLI arguments,
    allowing CLI arguments to override configuration values.
    """

    def __init__(self, settings: Dynaconf):
        """
        Initialize configuration manager.

        Args:
            settings: Dynaconf settings instance
        """
        self.settings = settings
        self._overrides = {}

    def set_override(self, key: str, value: Any) -> None:
        """
        Set a configuration override (typically from CLI arguments).

        Args:
            key: Configuration key (dot notation supported, e.g., 'server.url')
            value: Override value
        """
        if value is not None:
            self._overrides[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with override support.

        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found

        Returns:
            Configuration value
        """
        # Check for override first
        if key in self._overrides:
            return self._overrides[key]

        # Check for nested key override (e.g., 'server.url' when override is 'server')
        parts = key.split(".")
        if len(parts) > 1:
            override_key = parts[0]
            if override_key in self._overrides:
                nested_value = self._overrides[override_key]
                for part in parts[1:]:
                    if isinstance(nested_value, dict) and part in nested_value:
                        nested_value = nested_value[part]
                    else:
                        break
                else:
                    return nested_value

        # Fall back to settings
        try:
            # Dynaconf uses uppercase keys internally
            key_upper = key.upper().replace(".", "__")
            return self.settings.get(key_upper, default)
        except Exception:
            return default

    def get_nested(self, *keys, default: Any = None) -> Any:
        """
        Get nested configuration value.

        Args:
            *keys: Sequence of keys to traverse
            default: Default value if key not found

        Returns:
            Configuration value

        Example:
            config.get_nested('server', 'url') -> config['server']['url']
        """
        key = ".".join(keys)
        return self.get(key, default)

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration with overrides applied
        """
        # Start with settings dict
        result = self.settings.as_dict()

        # Apply overrides
        for key, value in self._overrides.items():
            parts = key.split(".")
            current = result
            for part in parts[:-1]:
                part_upper = part.upper()
                if part_upper not in current:
                    current[part_upper] = {}
                current = current[part_upper]
            current[parts[-1].upper()] = value

        return result


def load_config(
    config_file: Optional[str] = None,
    env_file: Optional[str] = ".env",
    validate: bool = True,
) -> ConfigManager:
    """
    Load configuration from all sources.

    Args:
        config_file: Path to YAML configuration file
        env_file: Path to .env file
        validate: Whether to validate configuration

    Returns:
        ConfigManager instance

    Example:
        config = load_config('config/config.yaml')
        server_url = config.get('server.url')
        config.set_override('server.timeout', 60)  # CLI override
    """
    settings = create_settings(config_file, env_file, validate)
    return ConfigManager(settings)
