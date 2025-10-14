"""Configuration loader with hierarchical merging support.

This module provides functionality to load configuration from multiple sources
and merge them according to priority:
  1. Default values (lowest priority)
  2. Global config file (~/.config/wt/config.toml)
  3. Repository config file (.wt/config.toml)
  4. Environment variables (WT_*)
  5. CLI arguments (highest priority)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from platformdirs import user_config_dir
from pydantic import ValidationError

from wt.config.settings import Settings

# Handle tomli/tomllib for different Python versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class ConfigError(Exception):
    """Configuration loading or validation error."""


class ConfigLoader:
    """Configuration loader with support for multiple sources and merging."""

    def __init__(
        self,
        repo_root: Path | None = None,
        global_config_path: Path | None = None,
    ) -> None:
        """Initialize configuration loader.

        Args:
            repo_root: Root directory of the git repository (for .wt/config.toml)
            global_config_path: Override path to global config file
        """
        self.repo_root = repo_root
        self._global_config_path = global_config_path

    @property
    def global_config_path(self) -> Path:
        """Get the path to the global configuration file.

        Returns:
            Path to ~/.config/wt/config.toml (or platform equivalent)
        """
        if self._global_config_path is not None:
            return self._global_config_path

        config_dir = user_config_dir("wt", ensure_exists=True)
        return Path(config_dir) / "config.toml"

    @property
    def repo_config_path(self) -> Path | None:
        """Get the path to the repository configuration file.

        Returns:
            Path to .wt/config.toml if repo_root is set, None otherwise
        """
        if self.repo_root is None:
            return None
        return self.repo_root / ".wt" / "config.toml"

    def load_toml_file(self, path: Path) -> dict[str, Any]:
        """Load and parse a TOML configuration file.

        Args:
            path: Path to the TOML file

        Returns:
            Parsed TOML data as a dictionary

        Raises:
            ConfigError: If file cannot be read or parsed
        """
        try:
            with path.open("rb") as f:
                return tomllib.load(f)
        except FileNotFoundError:
            return {}
        except (OSError, ValueError) as e:
            msg = f"Failed to load config from {path}: {e}"
            raise ConfigError(msg) from e

    def load_from_env(self) -> dict[str, Any]:
        """Load configuration overrides from environment variables.

        Environment variables follow the pattern: WT_SECTION_KEY=value
        Examples:
          - WT_GLOBAL_BASE_BRANCH=develop
          - WT_UI_COLORS=false
          - WT_LOGGING_LEVEL=DEBUG

        Returns:
            Configuration dictionary with overrides from environment
        """
        config: dict[str, Any] = {}
        prefix = "WT_"

        for env_var, value in os.environ.items():
            if not env_var.startswith(prefix):
                continue

            # Remove prefix and split into section and key
            # WT_GLOBAL_BASE_BRANCH -> ["GLOBAL", "BASE", "BRANCH"]
            parts = env_var[len(prefix) :].lower().split("_", 1)
            if len(parts) != 2:
                continue

            section, key = parts

            # Convert section name (handle 'global' specially)
            if section not in ["global", "ui", "performance", "logging", "git"]:
                continue

            # Initialize section if needed
            if section not in config:
                config[section] = {}

            # Parse value based on type
            parsed_value: Any = value

            # Boolean conversion
            if value.lower() in ("true", "1", "yes", "on"):
                parsed_value = True
            elif value.lower() in ("false", "0", "no", "off"):
                parsed_value = False
            # Integer conversion
            elif value.isdigit():
                parsed_value = int(value)
            # None/null conversion
            elif value.lower() in ("none", "null", ""):
                parsed_value = None

            config[section][key] = parsed_value

        return config

    def load_defaults(self) -> Settings:
        """Load default settings.

        Returns:
            Settings object with all default values
        """
        return Settings()

    def load_global_config(self) -> Settings:
        """Load global configuration file.

        Returns:
            Settings object from global config, or defaults if file doesn't exist

        Raises:
            ConfigError: If file exists but cannot be parsed or validated
        """
        global_path = self.global_config_path
        if not global_path.exists():
            return Settings()

        data = self.load_toml_file(global_path)
        try:
            return Settings(**data)
        except ValidationError as e:
            msg = f"Invalid global configuration in {global_path}: {e}"
            raise ConfigError(msg) from e

    def load_repo_config(self) -> Settings:
        """Load repository-local configuration file.

        Returns:
            Settings object from repo config, or defaults if file doesn't exist

        Raises:
            ConfigError: If file exists but cannot be parsed or validated
        """
        repo_path = self.repo_config_path
        if repo_path is None or not repo_path.exists():
            return Settings()

        data = self.load_toml_file(repo_path)
        try:
            return Settings(**data)
        except ValidationError as e:
            msg = f"Invalid repository configuration in {repo_path}: {e}"
            raise ConfigError(msg) from e

    def load_env_config(self) -> Settings:
        """Load configuration from environment variables.

        Returns:
            Settings object with values from environment variables

        Raises:
            ConfigError: If environment variables result in invalid configuration
        """
        env_data = self.load_from_env()
        if not env_data:
            return Settings()

        try:
            return Settings(**env_data)
        except ValidationError as e:
            msg = f"Invalid configuration from environment variables: {e}"
            raise ConfigError(msg) from e

    def load(
        self,
        cli_overrides: dict[str, Any] | None = None,
    ) -> Settings:
        """Load and merge configuration from all sources.

        Configuration is merged in the following order (later sources override earlier):
          1. Default values
          2. Global config file (~/.config/wt/config.toml)
          3. Repository config file (.wt/config.toml)
          4. Environment variables (WT_*)
          5. CLI arguments

        Args:
            cli_overrides: Dictionary of CLI argument overrides

        Returns:
            Merged Settings object

        Raises:
            ConfigError: If any configuration source is invalid
        """
        # Start with defaults
        settings = self.load_defaults()

        # Merge global config (as dict to preserve only set values)
        global_path = self.global_config_path
        if global_path.exists():
            global_data = self.load_toml_file(global_path)
            if global_data:
                settings = settings.merge_dict(global_data)

        # Merge repo config (as dict to preserve only set values)
        repo_path = self.repo_config_path
        if repo_path is not None and repo_path.exists():
            repo_data = self.load_toml_file(repo_path)
            if repo_data:
                settings = settings.merge_dict(repo_data)

        # Merge environment variables (as dict)
        env_data = self.load_from_env()
        if env_data:
            settings = settings.merge_dict(env_data)

        # Merge CLI overrides (as dict)
        if cli_overrides:
            settings = settings.merge_dict(cli_overrides)

        return settings

    def save_global_config(self, settings: Settings) -> None:
        """Save settings to global configuration file.

        Args:
            settings: Settings object to save

        Raises:
            ConfigError: If file cannot be written
        """
        global_path = self.global_config_path
        global_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import tomli_w
        except ImportError as e:
            msg = "tomli_w is required to save configuration (pip install tomli-w)"
            raise ConfigError(msg) from e

        try:
            data = settings.model_dump_toml()
            with global_path.open("wb") as f:
                tomli_w.dump(data, f)
        except (OSError, ValueError) as e:
            msg = f"Failed to save config to {global_path}: {e}"
            raise ConfigError(msg) from e

    def save_repo_config(self, settings: Settings) -> None:
        """Save settings to repository configuration file.

        Args:
            settings: Settings object to save

        Raises:
            ConfigError: If repo_root is not set or file cannot be written
        """
        repo_path = self.repo_config_path
        if repo_path is None:
            msg = "Cannot save repo config: repo_root not set"
            raise ConfigError(msg)

        repo_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            import tomli_w
        except ImportError as e:
            msg = "tomli_w is required to save configuration (pip install tomli-w)"
            raise ConfigError(msg) from e

        try:
            data = settings.model_dump_toml()
            with repo_path.open("wb") as f:
                tomli_w.dump(data, f)
        except (OSError, ValueError) as e:
            msg = f"Failed to save config to {repo_path}: {e}"
            raise ConfigError(msg) from e


def get_config_loader(repo_root: Path | None = None) -> ConfigLoader:
    """Get a ConfigLoader instance.

    Args:
        repo_root: Optional repository root directory

    Returns:
        ConfigLoader instance
    """
    return ConfigLoader(repo_root=repo_root)


def load_config(
    repo_root: Path | None = None,
    cli_overrides: dict[str, Any] | None = None,
) -> Settings:
    """Load configuration from all sources.

    This is a convenience function that creates a ConfigLoader and loads settings.

    Args:
        repo_root: Optional repository root directory
        cli_overrides: Optional CLI argument overrides

    Returns:
        Merged Settings object

    Raises:
        ConfigError: If any configuration source is invalid
    """
    loader = get_config_loader(repo_root=repo_root)
    return loader.load(cli_overrides=cli_overrides)
