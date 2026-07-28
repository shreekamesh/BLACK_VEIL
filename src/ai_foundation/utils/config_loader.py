"""
BLACK VEIL V5 - Configuration Loader
YAML/JSON configuration loader with schema validation
"""
import os
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from pydantic import BaseModel, ValidationError


class ConfigLoader:
    """
    Configuration loader supporting YAML, JSON, and environment variables.

    Features:
    - Load from YAML/JSON files
    - Environment variable overrides
    - Schema validation with Pydantic
    - Nested configuration support
    - Default values
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        Args:
            config_path: Optional path to config file
        """
        self._config: Dict[str, Any] = {}
        self._env_prefix = "BV_"

        if config_path:
            self.load_file(config_path)

    def load_file(self, path: str) -> Dict[str, Any]:
        """
        Load configuration from a file.

        Supports .yaml, .yml, and .json files.

        Args:
            path: Path to configuration file

        Returns:
            Dict[str, Any]: Loaded configuration

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        with open(file_path, "r") as f:
            if file_path.suffix in {".yaml", ".yml"}:
                config = yaml.safe_load(f)
            elif file_path.suffix == ".json":
                config = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {file_path.suffix}")

        self._config.update(config)
        return self._config

    def load_string(self, config_str: str, format: str = "yaml") -> Dict[str, Any]:
        """
        Load configuration from a string.

        Args:
            config_str: Configuration string
            format: Format of the string ('yaml' or 'json')

        Returns:
            Dict[str, Any]: Loaded configuration
        """
        if format == "yaml":
            config = yaml.safe_load(config_str)
        elif format == "json":
            config = json.loads(config_str)
        else:
            raise ValueError(f"Unsupported format: {format}")

        self._config.update(config)
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.

        Supports dot notation for nested keys (e.g., 'database.host')

        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found

        Returns:
            Any: Configuration value
        """
        # Check environment variable first
        env_key = f"{self._env_prefix}{key.upper().replace('.', '_')}"
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return self._parse_env_value(env_value)

        # Check nested config
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.

        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def validate(self, schema: type[BaseModel]) -> BaseModel:
        """
        Validate configuration against a Pydantic schema.

        Args:
            schema: Pydantic model class

        Returns:
            BaseModel: Validated configuration

        Raises:
            ValidationError: If validation fails
        """
        return schema(**self._config)

    def to_dict(self) -> Dict[str, Any]:
        """
        Get full configuration as dictionary.

        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        return self._config.copy()

    def merge(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge a configuration dictionary.

        Args:
            config: Configuration to merge

        Returns:
            Dict[str, Any]: Merged configuration
        """
        self._deep_merge(self._config, config)
        return self._config

    @staticmethod
    def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """Deep merge two dictionaries."""
        for key, value in override.items():
            if (
                key in base
                and isinstance(base[key], dict)
                and isinstance(value, dict)
            ):
                ConfigLoader._deep_merge(base[key], value)
            else:
                base[key] = value

    @staticmethod
    def _parse_env_value(value: str) -> Any:
        """Parse environment variable value."""
        # Try boolean
        if value.lower() in {"true", "yes", "1"}:
            return True
        if value.lower() in {"false", "no", "0"}:
            return False

        # Try integer
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Try list
        if value.startswith("[") and value.endswith("]"):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                pass

        # Try dict
        if value.startswith("{") and value.endswith("}"):
            try:
                return json.loads(value)
            except (json.JSONDecodeError, ValueError):
                pass

        return value
