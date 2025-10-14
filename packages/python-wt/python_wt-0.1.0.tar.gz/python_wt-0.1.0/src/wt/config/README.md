# Configuration System

Modern, hierarchical configuration system for the wt package using Pydantic v2 and TOML.

## Features

- **Type-safe**: Full Pydantic v2 validation with type hints
- **Hierarchical**: Multiple configuration sources with clear precedence
- **Platform-aware**: Uses platformdirs for XDG-compliant paths
- **Flexible**: Supports global, repo, environment, and CLI overrides
- **Validated**: Comprehensive field validation with helpful error messages

## Configuration Sources

Configuration is loaded and merged from multiple sources in this order (later sources override earlier):

1. **Default values** - Sensible defaults defined in the Settings models
2. **Global config** - `~/.config/wt/config.toml` (or platform equivalent)
3. **Repository config** - `.wt/config.toml` in the repo root
4. **Environment variables** - `WT_*` prefixed variables
5. **CLI arguments** - Command-line flags and options

## Configuration Files

### Global Configuration

Location: `~/.config/wt/config.toml` (on Linux/macOS)

This file contains user-wide settings that apply to all repositories.

### Repository Configuration

Location: `.wt/config.toml` in the repository root

This file contains repository-specific settings that override global settings.

### Example Configuration

```toml
[global]
base_branch = "main"
remote_name = "origin"
max_concurrent = 4
auto_fetch = true
cleanup_on_delete = true

[ui]
colors = true
show_emoji = true
table_style = "rounded"
pager = true
compact = false

[performance]
cache_enabled = true
cache_ttl = 300
parallel_operations = true

[logging]
level = "INFO"

[git]
pull_strategy = "merge"
gpg_sign = false
```

## Settings Hierarchy

### GlobalSettings

Git worktree and repository settings:

- `base_branch` (str, default: "main") - Default base branch for new worktrees
- `setup_command` (str|None, default: None) - Command to run after creating worktrees
- `remote_name` (str, default: "origin") - Default remote name
- `max_concurrent` (int, default: 4, range: 1-32) - Maximum concurrent operations
- `auto_fetch` (bool, default: True) - Auto-fetch before operations
- `cleanup_on_delete` (bool, default: True) - Clean up branches when deleting
- `worktree_dir` (str|None, default: None) - Default directory for worktrees

### UISettings

User interface configuration:

- `colors` (bool, default: True) - Enable colored output
- `show_emoji` (bool, default: True) - Show emoji in output
- `table_style` (str, default: "rounded") - Rich table style
- `pager` (bool, default: True) - Use pager for long output
- `compact` (bool, default: False) - Compact display mode

### PerformanceSettings

Performance and caching:

- `cache_enabled` (bool, default: True) - Enable operation caching
- `cache_ttl` (int, default: 300) - Cache TTL in seconds
- `parallel_operations` (bool, default: True) - Enable parallel operations

### LoggingSettings

Logging configuration:

- `level` (str, default: "INFO") - Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- `file` (str|None, default: None) - Log file path
- `format` (str) - Log format string

### GitSettings

Git-specific settings:

- `default_branch_prefix` (str, default: "") - Prefix for new branches
- `commit_template` (str|None, default: None) - Commit message template path
- `gpg_sign` (bool, default: False) - Sign commits with GPG
- `pull_strategy` (str, default: "merge") - Pull strategy (merge/rebase/ff-only)

## Environment Variables

Override any setting using environment variables with the `WT_` prefix:

```bash
export WT_GLOBAL_BASE_BRANCH=develop
export WT_UI_COLORS=false
export WT_GLOBAL_MAX_CONCURRENT=8
export WT_LOGGING_LEVEL=DEBUG
```

Format: `WT_SECTION_KEY=value`

Type conversion is automatic:
- Booleans: true/false, 1/0, yes/no, on/off
- Numbers: Parsed as integers
- Null: none/null/empty string

## Usage

### Basic Usage

```python
from wt.config import load_config

# Load configuration from all sources
config = load_config()

# Access settings
print(config.global_.base_branch)  # "main"
print(config.ui.colors)            # True
```

### With Repository Root

```python
from pathlib import Path
from wt.config import load_config

# Load with repository-specific config
repo_root = Path("/path/to/repo")
config = load_config(repo_root=repo_root)
```

### With CLI Overrides

```python
from wt.config import load_config

# CLI arguments override all other sources
cli_overrides = {
    "global": {"base_branch": "develop"},
    "ui": {"colors": False}
}
config = load_config(cli_overrides=cli_overrides)
```

### Using ConfigLoader Directly

```python
from pathlib import Path
from wt.config import ConfigLoader

# Create loader
loader = ConfigLoader(repo_root=Path("/path/to/repo"))

# Get config paths
print(loader.global_config_path)
print(loader.repo_config_path)

# Load from specific source
global_config = loader.load_global_config()
repo_config = loader.load_repo_config()
env_config = loader.load_env_config()

# Load and merge all sources
config = loader.load()
```

### Saving Configuration

```python
from wt.config import load_config, ConfigLoader
from pathlib import Path

# Load current config
config = load_config()

# Modify settings
config.global_.base_branch = "develop"
config.ui.colors = False

# Save to global config
loader = ConfigLoader()
loader.save_global_config(config)

# Save to repo config
loader = ConfigLoader(repo_root=Path.cwd())
loader.save_repo_config(config)
```

## Validation

All settings are validated using Pydantic:

```python
from wt.config import Settings
from pydantic import ValidationError

try:
    # This will fail - max_concurrent must be 1-32
    config = Settings(global_={"max_concurrent": 100})
except ValidationError as e:
    print(e)

try:
    # This will fail - invalid table style
    config = Settings(ui={"table_style": "invalid"})
except ValidationError as e:
    print(e)
```

## Error Handling

```python
from wt.config import load_config, ConfigError

try:
    config = load_config()
except ConfigError as e:
    print(f"Configuration error: {e}")
```

Common errors:
- Invalid TOML syntax in config files
- Invalid values that fail validation
- Missing required dependencies (e.g., tomli_w for saving)

## Dependencies

- **pydantic** >= 2.9.0 - Settings validation and type safety
- **platformdirs** >= 4.3.0 - XDG-compliant config paths
- **tomli** (Python < 3.11) - TOML parsing
- **tomli_w** (optional) - TOML writing for save operations

## Architecture

```
wt/config/
├── __init__.py      - Public API exports
├── settings.py      - Pydantic models for all settings
└── loader.py        - Configuration loading and merging logic
```

### Key Design Decisions

1. **Pydantic v2**: Provides robust validation, type safety, and JSON Schema support
2. **TOML format**: Human-readable, well-supported, hierarchical
3. **platformdirs**: Cross-platform config directory handling
4. **Merge strategy**: Later sources override earlier, but only for explicitly set values
5. **Type safety**: Full type hints for IDE support and static analysis

## Testing

The configuration system is thoroughly tested:

```bash
# Run basic tests
python test_config_standalone.py

# Test TOML loading
python test_toml_loading.py

# Test merge logic
python test_merge_logic.py
```

## Future Enhancements

Potential improvements:
- JSON Schema export for editor autocomplete
- Configuration migration utilities
- Configuration validation CLI command
- Per-worktree configuration overrides
- Config file encryption for sensitive values
