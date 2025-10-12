"""
Breadcrumb config command - manage multiple configuration profiles.

Supports creating, editing, and managing named configurations for different
projects and use cases.
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Optional, List
import typer

# Config directory
CONFIG_DIR = os.path.expanduser("~/.breadcrumb")


def _ensure_config_dir():
    """Ensure config directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _get_config_path(name: str) -> str:
    """Get path to named config file."""
    if name == "default":
        return os.path.join(CONFIG_DIR, "config.yaml")
    return os.path.join(CONFIG_DIR, f"{name}.yaml")


def _get_default_config() -> dict:
    """Get default configuration values."""
    import sys

    # Auto-detect best backend based on Python version
    default_backend = "pep669" if sys.version_info >= (3, 12) else "settrace"

    return {
        "enabled": True,
        "include": ["__main__"],
        "sample_rate": 1.0,
        "db_path": os.path.expanduser("~/.breadcrumb/traces.duckdb"),
        "backend": default_backend,
    }


def _format_config_content(config: dict, name: str) -> str:
    """Format config dictionary as YAML with helpful comments."""
    return f"""# Breadcrumb Configuration: {name}
# Custom configuration profile for specialized tracing needs.

# Enable or disable tracing
enabled: {config.get('enabled', True)}

# Module patterns to include (glob style)
# Start with ['__main__'] and iteratively expand:
# - '__main__': Your main script
# - 'myapp.*': Your application modules
# - 'flock.orchestrator.*': Specific library modules
include:
{chr(10).join(f"  - '{pattern}'" for pattern in config.get('include', ['__main__']))}

# Sampling rate (0.0 to 1.0)
sample_rate: {config.get('sample_rate', 1.0)}

# Database path for traces
db_path: '{config.get('db_path', os.path.expanduser('~/.breadcrumb/traces.duckdb'))}'

# Backend: 'pep669' (Python 3.12+) or 'settrace' (older Python)
backend: '{config.get('backend', 'pep669')}'
"""


def config_create(
    name: str,
    include: Optional[List[str]] = None,
    sample_rate: Optional[float] = None,
    db_path: Optional[str] = None,
    force: bool = False,
):
    """
    Create a new named configuration profile.

    Args:
        name: Name of the configuration profile
        include: Module patterns to include
        sample_rate: Sampling rate (0.0 to 1.0)
        db_path: Database path
        force: Overwrite existing config
    """
    _ensure_config_dir()
    config_path = _get_config_path(name)

    # Check if config already exists
    if os.path.exists(config_path) and not force:
        typer.echo(f"Error: Config '{name}' already exists at {config_path}", err=True)
        typer.echo("Use --force to overwrite", err=True)
        raise typer.Exit(1)

    # Start with defaults
    config = _get_default_config()

    # Apply custom values
    if include is not None:
        config["include"] = include
    if sample_rate is not None:
        config["sample_rate"] = sample_rate
    if db_path is not None:
        config["db_path"] = os.path.expanduser(db_path)

    # Write config file
    content = _format_config_content(config, name)
    with open(config_path, 'w') as f:
        f.write(content)

    typer.echo(f"Created config '{name}' at {config_path}")


def config_show(name: str):
    """
    Show the contents of a configuration profile.

    Args:
        name: Name of the configuration profile
    """
    config_path = _get_config_path(name)

    if not os.path.exists(config_path):
        typer.echo(f"Error: Config '{name}' not found at {config_path}", err=True)
        typer.echo(f"Use 'breadcrumb config create {name}' to create it", err=True)
        raise typer.Exit(1)

    # Read and display config
    with open(config_path, 'r') as f:
        content = f.read()

    typer.echo(f"Configuration: {name}")
    typer.echo(f"Path: {config_path}")
    typer.echo("=" * 60)
    typer.echo(content)


def config_list():
    """
    List all available configuration profiles.
    """
    _ensure_config_dir()

    # Find all .yaml files in config directory
    config_files = []
    for file in os.listdir(CONFIG_DIR):
        if file.endswith('.yaml'):
            config_files.append(file)

    if not config_files:
        typer.echo("No configuration profiles found.")
        typer.echo("Use 'breadcrumb config create <name>' to create one.")
        return

    typer.echo("Available configuration profiles:")
    typer.echo("=" * 60)

    for file in sorted(config_files):
        name = file[:-5]  # Remove .yaml extension
        if name == "config":
            name = "default"

        config_path = os.path.join(CONFIG_DIR, file)

        # Try to load config to show summary
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)

            enabled = "enabled" if config.get('enabled', True) else "disabled"
            include_count = len(config.get('include', []))

            typer.echo(f"  {name:20s} - {enabled}, include={include_count} patterns")
        except Exception:
            typer.echo(f"  {name:20s} - (error reading config)")


def config_edit(
    name: str,
    include: Optional[List[str]] = None,
    add_include: Optional[List[str]] = None,
    remove_include: Optional[List[str]] = None,
    sample_rate: Optional[float] = None,
    db_path: Optional[str] = None,
    enabled: Optional[bool] = None,
):
    """
    Edit an existing configuration profile.

    Args:
        name: Name of the configuration profile
        include: Replace include patterns (replaces entire list)
        add_include: Add patterns to include list
        remove_include: Remove patterns from include list
        sample_rate: Set sampling rate
        db_path: Set database path
        enabled: Enable/disable tracing
    """
    config_path = _get_config_path(name)

    if not os.path.exists(config_path):
        typer.echo(f"Error: Config '{name}' not found at {config_path}", err=True)
        typer.echo(f"Use 'breadcrumb config create {name}' to create it", err=True)
        raise typer.Exit(1)

    # Load existing config
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}

    # Apply edits
    if include is not None:
        config["include"] = include

    # Add patterns
    if add_include:
        current = config.get("include", [])
        for pattern in add_include:
            if pattern not in current:
                current.append(pattern)
        config["include"] = current

    # Remove patterns
    if remove_include:
        current = config.get("include", [])
        for pattern in remove_include:
            if pattern in current:
                current.remove(pattern)
        config["include"] = current

    # Update other settings
    if sample_rate is not None:
        config["sample_rate"] = sample_rate
    if db_path is not None:
        config["db_path"] = os.path.expanduser(db_path)
    if enabled is not None:
        config["enabled"] = enabled

    # Write updated config
    content = _format_config_content(config, name)
    with open(config_path, 'w') as f:
        f.write(content)

    typer.echo(f"Updated config '{name}'")


def config_delete(name: str, force: bool = False):
    """
    Delete a configuration profile.

    Args:
        name: Name of the configuration profile
        force: Skip confirmation prompt
    """
    if name == "default":
        typer.echo("Error: Cannot delete the default configuration", err=True)
        raise typer.Exit(1)

    config_path = _get_config_path(name)

    if not os.path.exists(config_path):
        typer.echo(f"Error: Config '{name}' not found", err=True)
        raise typer.Exit(1)

    # Confirm deletion unless --force
    if not force:
        confirm = typer.confirm(
            f"Delete configuration '{name}'?",
            default=False,
        )
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(0)

    # Delete config file
    os.unlink(config_path)
    typer.echo(f"Deleted config '{name}'")


def load_config(name: str) -> dict:
    """
    Load a named configuration file.

    Args:
        name: Name of the configuration profile

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config doesn't exist
    """
    config_path = _get_config_path(name)

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config '{name}' not found at {config_path}")

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f) or {}

    return config


def config_validate(name: str):
    """
    Validate a configuration profile and show what would be loaded.

    Args:
        name: Name of the configuration profile
    """
    config_path = _get_config_path(name)

    typer.echo(f"Validating config: {name}")
    typer.echo(f"Path: {config_path}")
    typer.echo("=" * 70)

    # Check if file exists
    if not os.path.exists(config_path):
        typer.echo(f"[ERROR] Config file not found", err=True)
        typer.echo(f"", err=True)
        typer.echo(f"Create it with:", err=True)
        typer.echo(f"  breadcrumb config create {name}", err=True)
        raise typer.Exit(1)

    typer.echo(f"[OK] Config file exists\n")

    # Try to load YAML
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if config is None:
            typer.echo("[ERROR] Config file is empty or invalid YAML", err=True)
            raise typer.Exit(1)

        typer.echo(f"[OK] YAML syntax is valid\n")
    except yaml.YAMLError as e:
        typer.echo(f"[ERROR] Invalid YAML syntax", err=True)
        typer.echo(f"  {e}", err=True)
        raise typer.Exit(1)

    # Validate fields
    typer.echo("Configuration values:")
    typer.echo("-" * 70)

    # Check enabled
    enabled = config.get('enabled', True)
    typer.echo(f"  enabled: {enabled}")
    if not isinstance(enabled, bool):
        typer.echo(f"    [WARNING] Should be boolean (true/false)", err=True)

    # Check include patterns
    include = config.get('include', ['__main__'])
    typer.echo(f"  include: {include}")
    if not isinstance(include, list):
        typer.echo(f"    [ERROR] Should be a list", err=True)
    else:
        typer.echo(f"    [OK] {len(include)} pattern(s)")
        for pattern in include:
            typer.echo(f"      - '{pattern}'")

    # Check sample_rate
    sample_rate = config.get('sample_rate', 1.0)
    typer.echo(f"  sample_rate: {sample_rate}")
    if not isinstance(sample_rate, (int, float)):
        typer.echo(f"    [ERROR] Should be a number", err=True)
    elif not 0.0 <= sample_rate <= 1.0:
        typer.echo(f"    [ERROR] Should be between 0.0 and 1.0", err=True)
    else:
        typer.echo(f"    [OK] Valid ({int(sample_rate * 100)}% of traces)")

    # Check db_path
    db_path = config.get('db_path')
    typer.echo(f"  db_path: {db_path}")
    if db_path:
        expanded = os.path.expanduser(db_path)
        typer.echo(f"    Expands to: {expanded}")

    # Check backend
    backend = config.get('backend', 'pep669')
    typer.echo(f"  backend: {backend}")
    if backend not in ('pep669', 'settrace'):
        typer.echo(f"    [ERROR] Should be 'pep669' or 'settrace'", err=True)
    else:
        typer.echo(f"    [OK] Valid")

    # Test pattern matching
    typer.echo("\n" + "=" * 70)
    typer.echo("Pattern Matching Test:")
    typer.echo("-" * 70)

    test_modules = [
        '__main__',
        'flock.logging',
        'flock.logging.trace_and_logged',
        'flock.registry',
        'flock.agent',
        'myapp',
        'myapp.core',
        'requests',
        'pydantic',
    ]

    def match_pattern(text: str, pattern: str) -> bool:
        """Simple glob-style pattern matching."""
        if pattern == '*':
            return True
        if pattern.endswith('.*'):
            prefix = pattern[:-2]
            return text == prefix or text.startswith(prefix + '.')
        return text == pattern

    for module in test_modules:
        # Check if included
        included = any(match_pattern(module, p) for p in include)

        if included:
            status = "[+] INCLUDED"
        else:
            status = "[ ] NOT MATCHED"

        typer.echo(f"  {module:40s} {status}")

    # Summary
    typer.echo("\n" + "=" * 70)
    typer.echo("Summary:")
    typer.echo("-" * 70)

    # Estimate event count
    if isinstance(include, list):
        if '*' in include:
            typer.echo("  [WARNING] Tracing ALL modules (high overhead)")
            typer.echo("     Consider using specific patterns like ['__main__', 'myapp.*']")
        elif '__main__' in include or any('.' in p or '*' in p for p in include):
            typer.echo("  [OK] Configuration looks reasonable - include-only workflow")
        else:
            typer.echo("  [INFO] Specific modules selected - good for focused tracing")

    typer.echo(f"\nConfig '{name}' is valid and ready to use!")
    typer.echo(f"Use it with: breadcrumb run -c {name} --timeout 60 python script.py")
