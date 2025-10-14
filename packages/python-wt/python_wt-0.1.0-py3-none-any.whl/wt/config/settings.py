"""Configuration settings models for wt.

This module defines Pydantic models for all configuration settings,
including defaults, validation, and type safety.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class UISettings(BaseModel):
    """User interface configuration settings."""

    colors: bool = Field(
        default=True,
        description="Enable colored output in CLI",
    )
    show_emoji: bool = Field(
        default=True,
        description="Show emoji in output",
    )
    table_style: str = Field(
        default="rounded",
        description="Rich table style (rounded, simple, heavy, etc.)",
    )
    pager: bool = Field(
        default=True,
        description="Use pager for long output",
    )
    compact: bool = Field(
        default=False,
        description="Use compact display mode",
    )

    @field_validator("table_style")
    @classmethod
    def validate_table_style(cls, v: str) -> str:
        """Validate table style is a known Rich table style."""
        valid_styles = {
            "ascii",
            "ascii2",
            "ascii_double_head",
            "square",
            "square_double_head",
            "minimal",
            "minimal_heavy_head",
            "minimal_double_head",
            "simple",
            "simple_heavy",
            "horizontals",
            "rounded",
            "heavy",
            "heavy_edge",
            "heavy_head",
            "double",
            "double_edge",
            "markdown",
        }
        if v not in valid_styles:
            msg = f"Invalid table style: {v}. Must be one of: {', '.join(sorted(valid_styles))}"
            raise ValueError(msg)
        return v


class GlobalSettings(BaseModel):
    """Global configuration settings for git worktree operations."""

    base_branch: str = Field(
        default="main",
        description="Default base branch for new worktrees",
    )
    setup_command: str | None = Field(
        default=None,
        description="Command to run after creating a worktree (e.g., 'npm install')",
    )
    remote_name: str = Field(
        default="origin",
        description="Default remote name",
    )
    max_concurrent: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Maximum concurrent operations",
    )
    auto_fetch: bool = Field(
        default=True,
        description="Automatically fetch from remote before operations",
    )
    cleanup_on_delete: bool = Field(
        default=True,
        description="Clean up branches when deleting worktrees",
    )
    worktree_dir: str | None = Field(
        default=None,
        description="Default directory for new worktrees (relative to repo root)",
    )

    @field_validator("base_branch", "remote_name")
    @classmethod
    def validate_git_name(cls, v: str) -> str:
        """Validate git branch/remote names."""
        if not v or not v.strip():
            msg = "Git name cannot be empty"
            raise ValueError(msg)
        if v != v.strip():
            msg = "Git name cannot have leading/trailing whitespace"
            raise ValueError(msg)
        # Basic validation - git has complex rules but these cover common issues
        invalid_chars = [" ", "~", "^", ":", "?", "*", "[", "\\", ".."]
        for char in invalid_chars:
            if char in v:
                msg = f"Git name cannot contain '{char}'"
                raise ValueError(msg)
        return v

    @field_validator("setup_command")
    @classmethod
    def validate_setup_command(cls, v: str | None) -> str | None:
        """Validate setup command."""
        if v is not None and not v.strip():
            return None
        return v


class PerformanceSettings(BaseModel):
    """Performance and caching settings."""

    cache_enabled: bool = Field(
        default=True,
        description="Enable caching of git operations",
    )
    cache_ttl: int = Field(
        default=300,
        ge=0,
        description="Cache TTL in seconds (0 = no expiration)",
    )
    parallel_operations: bool = Field(
        default=True,
        description="Enable parallel git operations",
    )


class LoggingSettings(BaseModel):
    """Logging configuration."""

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )
    file: str | None = Field(
        default=None,
        description="Log file path (None = no file logging)",
    )
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )


class GitSettings(BaseModel):
    """Git-specific configuration."""

    default_branch_prefix: str = Field(
        default="",
        description="Default prefix for new branches (e.g., 'feature/')",
    )
    commit_template: str | None = Field(
        default=None,
        description="Path to git commit message template",
    )
    gpg_sign: bool = Field(
        default=False,
        description="Sign commits with GPG",
    )
    pull_strategy: Literal["merge", "rebase", "ff-only"] = Field(
        default="merge",
        description="Default pull strategy",
    )


class Settings(BaseModel):
    """Root configuration settings for wt.

    This is the main settings model that contains all configuration sections.
    It can be loaded from TOML files and merged with environment variables
    and CLI arguments.
    """

    global_: GlobalSettings = Field(
        default_factory=GlobalSettings,
        alias="global",
        description="Global worktree settings",
    )
    ui: UISettings = Field(
        default_factory=UISettings,
        description="User interface settings",
    )
    performance: PerformanceSettings = Field(
        default_factory=PerformanceSettings,
        description="Performance settings",
    )
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description="Logging settings",
    )
    git: GitSettings = Field(
        default_factory=GitSettings,
        description="Git-specific settings",
    )

    model_config = {
        "populate_by_name": True,
        "validate_assignment": True,
        "extra": "forbid",
        "str_strip_whitespace": True,
    }

    def merge_dict(self, other_dict: dict[str, object]) -> Settings:
        """Merge a dictionary of values into this Settings.

        This is more appropriate for merging since we can detect which
        fields were actually provided vs. filled in by defaults.

        Args:
            other_dict: Dictionary with section data to merge

        Returns:
            New Settings object with merged values
        """
        # Start with self's data
        merged_data = self.model_dump(by_alias=True)

        # Deep merge each section that exists in other_dict
        for section_name in ["global", "ui", "performance", "logging", "git"]:
            if section_name in other_dict and isinstance(other_dict[section_name], dict):
                if section_name not in merged_data:
                    merged_data[section_name] = {}
                # Merge the section, with other_dict values taking precedence
                merged_data[section_name].update(other_dict[section_name])

        return Settings(**merged_data)

    def merge(self, other: Settings) -> Settings:
        """Merge another Settings object into this one.

        Values from 'other' take precedence over values in 'self'.
        This creates a new Settings with other's values overlaid on self's values.

        Args:
            other: Settings object to merge from

        Returns:
            New Settings object with merged values
        """
        # Convert both to dicts and merge
        self_data = self.model_dump(by_alias=True)
        other_data = other.model_dump(by_alias=True)

        merged_data = {}
        for section_name in ["global", "ui", "performance", "logging", "git"]:
            merged_data[section_name] = {}
            # Start with self's values
            if section_name in self_data:
                merged_data[section_name].update(self_data[section_name])
            # Override with other's values
            if section_name in other_data:
                merged_data[section_name].update(other_data[section_name])

        return Settings(**merged_data)

    def model_dump_toml(self) -> dict[str, dict[str, object]]:
        """Dump settings in a format suitable for TOML serialization.

        Returns:
            Dictionary with top-level keys for each settings section
        """
        data = self.model_dump(by_alias=True, exclude_defaults=False)
        return data
