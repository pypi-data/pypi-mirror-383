"""
Breadcrumb configuration system with persistent config file.

Configuration is always loaded from ~/.breadcrumb/config.yaml and created
with defaults if it doesn't exist. CLI and Python API parameters override
file-based configuration.

Configuration precedence: Python API > CLI Args > Config File > Defaults
"""

import os
import sys
import yaml
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Literal
from pathlib import Path


# Config file path
CONFIG_DIR = os.path.expanduser("~/.breadcrumb")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

# Environment variable names
ENV_ENABLED = "BREADCRUMB_ENABLED"
ENV_DB_PATH = "BREADCRUMB_DB_PATH"
ENV_SAMPLE_RATE = "BREADCRUMB_SAMPLE_RATE"

# Default values
DEFAULT_ENABLED = True
DEFAULT_DB_PATH = os.path.expanduser("~/.breadcrumb/traces.duckdb")
DEFAULT_SAMPLE_RATE = 1.0

# Default exclude patterns to avoid instrumentation bugs in common dependencies
DEFAULT_EXCLUDE = ["wrapt.*", "deprecated.*", "opentelemetry.*"]

# Auto-detect best backend based on Python version
def _get_default_backend() -> str:
    """Get default backend based on Python version."""
    if sys.version_info >= (3, 12):
        return "pep669"  # Use PEP 669 on Python 3.12+
    else:
        return "settrace"  # Fallback to sys.settrace on older Python

DEFAULT_BACKEND = _get_default_backend()


BackendType = Literal["pep669", "settrace"]


@dataclass
class BreadcrumbConfig:
    """Configuration for Breadcrumb tracer."""

    enabled: bool = DEFAULT_ENABLED
    include: List[str] = field(default_factory=lambda: ["__main__"])  # Default to tracing only __main__
    exclude: List[str] = field(default_factory=lambda: DEFAULT_EXCLUDE.copy())
    sample_rate: float = DEFAULT_SAMPLE_RATE
    db_path: str = DEFAULT_DB_PATH
    backend: BackendType = DEFAULT_BACKEND
    max_repr_length: int = 2000

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Expand user path in db_path (e.g., ~ to home directory)
        self.db_path = os.path.expanduser(self.db_path)
        self._validate()

    def _validate(self):
        """Validate configuration values."""
        if not 0.0 <= self.sample_rate <= 1.0:
            raise ValueError(
                f"sample_rate must be between 0.0 and 1.0, got {self.sample_rate}"
            )

        if self.backend not in ("pep669", "settrace"):
            raise ValueError(
                f"backend must be 'pep669' or 'settrace', got '{self.backend}'"
            )

        if not isinstance(self.include, list):
            raise TypeError(
                f"include must be a list of strings, got {type(self.include)}"
            )
        if not isinstance(self.exclude, list):
            raise TypeError(
                f"exclude must be a list of strings, got {type(self.exclude)}"
            )
        if not isinstance(self.max_repr_length, int) or self.max_repr_length <= 0:
            raise ValueError(
                f"max_repr_length must be a positive integer, got {self.max_repr_length}"
            )

    def summary(self) -> str:
        """Return a one-line summary of the configuration."""
        status = "enabled" if self.enabled else "disabled"
        backend_info = f"backend={self.backend}"
        backend_info += f" db={self.db_path}"

        sample_info = f"sample_rate={self.sample_rate}"
        include_count = len(self.include)
        filters = f"include={include_count} patterns"
        if self.exclude:
            filters += f", exclude={len(self.exclude)} patterns"
        repr_info = f"max_repr_length={self.max_repr_length}"

        return f"Breadcrumb {status}: {backend_info}, {sample_info}, {filters}, {repr_info}"

    def to_dict(self) -> dict:
        """Convert config to dictionary for YAML serialization."""
        return {
            "enabled": self.enabled,
            "include": self.include,
            "exclude": self.exclude,
            "sample_rate": self.sample_rate,
            "db_path": self.db_path,
            "backend": self.backend,
            "max_repr_length": self.max_repr_length,
        }


# Global configuration instance
_config: Optional[BreadcrumbConfig] = None

# Global backend instance (for PEP 669)
_backend_instance = None

# Global integration instance (connects backend to storage)
_integration_instance = None


def _ensure_config_dir():
    """Ensure config directory exists."""
    os.makedirs(CONFIG_DIR, exist_ok=True)


def _create_default_config_file():
    """Create default config file with comments."""
    _ensure_config_dir()

    default_config = {
        "enabled": DEFAULT_ENABLED,
        "include": ["__main__"],
        "exclude": DEFAULT_EXCLUDE.copy(),
        "sample_rate": DEFAULT_SAMPLE_RATE,
        "db_path": DEFAULT_DB_PATH,
        "backend": DEFAULT_BACKEND,
        "max_repr_length": 2000,
    }

    # Write with comments
    config_content = f"""# Breadcrumb AI Tracer Configuration
# This file is automatically created with defaults if it doesn't exist.
# Edit this file to customize your tracing behavior globally.

# Enable or disable tracing
enabled: {default_config['enabled']}

# Module patterns to include (glob style)
# Default: ['__main__'] - only trace your main script
# Expand as needed: ['__main__', 'myapp.*', 'flock.orchestrator.*']
include:
  - '__main__'

# Module patterns to exclude (glob style)
# Automatically skip noisy instrumentation frameworks that can break tracing
exclude:
{chr(10).join(f"  - '{pattern}'" for pattern in default_config['exclude'])}

# Sampling rate (0.0 to 1.0)
sample_rate: {default_config['sample_rate']}

# Database path for traces
db_path: '{default_config['db_path']}'

# Backend: 'pep669' (Python 3.12+) or 'settrace' (older Python)
backend: '{default_config['backend']}'

# Maximum characters captured per value (function args/returns)
# Increase if you need deeper visibility into large payloads
max_repr_length: {default_config['max_repr_length']}
"""

    with open(CONFIG_FILE, 'w') as f:
        f.write(config_content)


def _load_config_file() -> dict:
    """
    Load configuration from YAML file.

    Creates file with defaults if it doesn't exist.

    Returns:
        Config dictionary
    """
    # Create default config file if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        _create_default_config_file()

    # Load config file
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f) or {}
        return config
    except Exception as e:
        print(f"Warning: Failed to load config file {CONFIG_FILE}: {e}", file=sys.stderr)
        print("Using default configuration.", file=sys.stderr)
        return {}


def _parse_bool_env(value: str) -> bool:
    """Parse boolean from environment variable."""
    value_lower = value.lower().strip()
    if value_lower in ("1", "true", "yes", "on"):
        return True
    elif value_lower in ("0", "false", "no", "off"):
        return False
    else:
        raise ValueError(
            f"Invalid boolean value: '{value}'. "
            f"Use 1/true/yes/on or 0/false/no/off"
        )


def _parse_float_env(value: str) -> float:
    """Parse float from environment variable."""
    try:
        return float(value)
    except ValueError:
        raise ValueError(
            f"Invalid float value: '{value}'. "
            f"Must be a number between 0.0 and 1.0"
        )


def _load_from_env() -> dict:
    """Load configuration from environment variables."""
    config = {}

    # BREADCRUMB_ENABLED
    if ENV_ENABLED in os.environ:
        config["enabled"] = _parse_bool_env(os.environ[ENV_ENABLED])

    # BREADCRUMB_DB_PATH
    if ENV_DB_PATH in os.environ:
        config["db_path"] = os.environ[ENV_DB_PATH]

    # BREADCRUMB_SAMPLE_RATE
    if ENV_SAMPLE_RATE in os.environ:
        config["sample_rate"] = _parse_float_env(os.environ[ENV_SAMPLE_RATE])

    return config


def init(
    enabled: Optional[bool] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    sample_rate: Optional[float] = None,
    db_path: Optional[str] = None,
    backend: Optional[BackendType] = None,
    max_repr_length: Optional[int] = None,
    silent: bool = False,
    config_file: Optional[str] = None,
) -> BreadcrumbConfig:
    """
    Initialize Breadcrumb tracer with configuration.

    Configuration precedence: Python API > Environment Variables > Config File > Defaults

    Args:
        enabled: Enable or disable tracing (default: from config file)
        include: List of glob patterns to include (default: ['__main__'])
        sample_rate: Sampling rate 0.0-1.0 (default: from config file)
        db_path: Path to DuckDB database (default: from config file)
        backend: Instrumentation backend "pep669" or "settrace" (default: from config file)
        max_repr_length: Maximum characters captured per value (default: from config file)
        silent: Suppress initialization message (default: False)
        config_file: Config file path for display (default: shows default config.yaml)

    Returns:
        BreadcrumbConfig: The initialized configuration

    Raises:
        ValueError: If configuration values are invalid
        TypeError: If configuration types are incorrect

    Environment Variables:
        BREADCRUMB_ENABLED: Enable/disable tracing (1/true/yes/on or 0/false/no/off)
        BREADCRUMB_DB_PATH: Path to DuckDB database
        BREADCRUMB_SAMPLE_RATE: Sampling rate 0.0-1.0

    Examples:
        >>> import breadcrumb
        >>> breadcrumb.init(sample_rate=0.5)

        >>> breadcrumb.init(
        ...     include=["__main__", "myapp.*", "flock.orchestrator.*"],
        ...     backend="pep669"
        ... )
    """
    global _config

    # Layer 1: Load from config file (creates with defaults if doesn't exist)
    config_params = _load_config_file()

    # Layer 2: Load from environment variables
    env_config = _load_from_env()
    config_params.update(env_config)

    # Layer 3: Apply Python API parameters (highest priority)
    if enabled is not None:
        config_params["enabled"] = enabled
    if include is not None:
        config_params["include"] = include
    if exclude is not None:
        config_params["exclude"] = exclude
    if sample_rate is not None:
        config_params["sample_rate"] = sample_rate
    if db_path is not None:
        config_params["db_path"] = db_path
    if backend is not None:
        config_params["backend"] = backend
    if max_repr_length is not None:
        config_params["max_repr_length"] = max_repr_length

    # Create configuration instance
    _config = BreadcrumbConfig(**config_params)

    # Initialize backend and integration if enabled and using PEP 669
    global _backend_instance, _integration_instance
    if _config.enabled and _config.backend == "pep669":
        # Check if PEP 669 is available
        if sys.version_info >= (3, 12):
            from breadcrumb.instrumentation.pep669_backend import PEP669Backend
            from breadcrumb.integration import start_integration

            # Create backend (but don't start it yet - integration will start it)
            _backend_instance = PEP669Backend(
                capture_args=True,
                capture_returns=True,
                capture_locals=False,  # Expensive, disabled by default
                capture_exceptions=True,
                include_patterns=_config.include,
                exclude_patterns=_config.exclude,
                max_repr_length=_config.max_repr_length,
            )

            # Start integration layer (this starts both backend and storage)
            max_value_size = max(_config.max_repr_length * 4, 1024)
            _integration_instance = start_integration(
                backend=_backend_instance,
                db_path=_config.db_path,
                max_value_size=max_value_size,
            )
        else:
            raise RuntimeError(
                f"PEP 669 backend requires Python 3.12+. "
                f"Current version: {sys.version_info.major}.{sys.version_info.minor}"
            )

    # Print initialization message
    if not silent:
        # Use provided config_file path if available, otherwise use default
        display_config_path = config_file if config_file else CONFIG_FILE
        config_source = f"(config: {display_config_path})"
        print(f"{_config.summary()} {config_source}")

    return _config


def get_config() -> Optional[BreadcrumbConfig]:
    """
    Get the current configuration.

    Returns:
        BreadcrumbConfig if initialized, None otherwise
    """
    return _config


def get_config_file_path() -> str:
    """
    Get the path to the config file.

    Returns:
        Path to config.yaml
    """
    return CONFIG_FILE


def reset_config():
    """Reset configuration to uninitialized state (mainly for testing)."""
    global _config, _backend_instance, _integration_instance

    # Stop integration if active (this also stops backend and writer)
    if _integration_instance is not None:
        try:
            _integration_instance.stop()
        except:
            pass
        _integration_instance = None

    # Stop backend if active
    if _backend_instance is not None:
        try:
            _backend_instance.stop()
        except:
            pass
        _backend_instance = None

    _config = None


def get_backend():
    """
    Get the active backend instance.

    Returns:
        Backend instance if initialized, None otherwise
    """
    return _backend_instance


def get_events():
    """
    Get trace events from the active backend.

    Returns:
        List of TraceEvent objects if PEP 669 backend is active, None otherwise
    """
    if _backend_instance is not None:
        return _backend_instance.get_events()
    return None


def shutdown(timeout: float = 5.0) -> None:
    """
    Shutdown breadcrumb tracing and flush all pending events.

    This function ensures all trace data is properly persisted to the database
    before the process exits. Should be called at the end of your program or
    automatically via atexit handlers.

    Args:
        timeout: Maximum time to wait for flush (seconds)

    Example:
        >>> import breadcrumb
        >>> breadcrumb.init()
        >>> # ... your code here ...
        >>> breadcrumb.shutdown()  # Ensure all data is flushed
    """
    global _backend_instance, _integration_instance, _config

    # Stop integration first (this marks traces as completed and flushes writer)
    if _integration_instance is not None:
        try:
            _integration_instance.stop(timeout=timeout)
        except Exception:
            pass
        _integration_instance = None

    # Stop backend
    if _backend_instance is not None:
        try:
            _backend_instance.stop()
        except Exception:
            pass
        _backend_instance = None

    _config = None
