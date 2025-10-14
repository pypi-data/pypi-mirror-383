"""Configuration module for wt.

This module provides a hierarchical configuration system with support for:
- TOML configuration files (global and repository-local)
- Environment variable overrides
- CLI argument overrides
- Pydantic-based validation and type safety

Example usage:
    >>> from wt.config import load_config, Settings
    >>> settings = load_config()
    >>> print(settings.global_.base_branch)
    'main'

    >>> # Load with repository-specific config
    >>> from pathlib import Path
    >>> settings = load_config(repo_root=Path('/path/to/repo'))

    >>> # Load with CLI overrides
    >>> cli_overrides = {'global': {'base_branch': 'develop'}}
    >>> settings = load_config(cli_overrides=cli_overrides)
"""

from wt.config.loader import (
    ConfigError,
    ConfigLoader,
    get_config_loader,
    load_config,
)
from wt.config.settings import (
    GitSettings,
    GlobalSettings,
    LoggingSettings,
    PerformanceSettings,
    Settings,
    UISettings,
)

__all__ = [
    # Settings models
    "Settings",
    "GlobalSettings",
    "UISettings",
    "PerformanceSettings",
    "LoggingSettings",
    "GitSettings",
    # Loader
    "ConfigLoader",
    "ConfigError",
    # Convenience functions
    "load_config",
    "get_config_loader",
]
