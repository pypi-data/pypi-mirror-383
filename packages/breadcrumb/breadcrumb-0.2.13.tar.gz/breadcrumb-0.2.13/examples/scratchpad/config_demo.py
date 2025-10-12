"""
Demo script showing Breadcrumb configuration options.

This demonstrates the various ways to configure Breadcrumb.
"""

import os
import breadcrumb


def demo_basic_usage():
    """Demo 1: Basic usage with defaults."""
    print("=" * 70)
    print("Demo 1: Basic usage with defaults")
    print("=" * 70)
    breadcrumb.reset_config()
    config = breadcrumb.init()
    print()


def demo_custom_configuration():
    """Demo 2: Custom configuration via Python API."""
    print("=" * 70)
    print("Demo 2: Custom configuration via Python API")
    print("=" * 70)
    breadcrumb.reset_config()
    config = breadcrumb.init(
        include=["src/**/*.py", "lib/**/*.py"],
        exclude=["tests/**", "**/*_test.py"],
        sample_rate=0.5,
        db_path="/var/log/breadcrumb/traces.db",
    )
    print()


def demo_memory_backend():
    """Demo 3: Memory backend for testing."""
    print("=" * 70)
    print("Demo 3: Memory backend (useful for testing)")
    print("=" * 70)
    breadcrumb.reset_config()
    config = breadcrumb.init(backend="memory")
    print()


def demo_environment_variables():
    """Demo 4: Configuration via environment variables."""
    print("=" * 70)
    print("Demo 4: Configuration via environment variables")
    print("=" * 70)
    breadcrumb.reset_config()

    # Set environment variables
    os.environ["BREADCRUMB_ENABLED"] = "true"
    os.environ["BREADCRUMB_SAMPLE_RATE"] = "0.25"
    os.environ["BREADCRUMB_DB_PATH"] = "/tmp/env_traces.db"

    config = breadcrumb.init()

    # Clean up
    del os.environ["BREADCRUMB_ENABLED"]
    del os.environ["BREADCRUMB_SAMPLE_RATE"]
    del os.environ["BREADCRUMB_DB_PATH"]
    print()


def demo_precedence():
    """Demo 5: Configuration precedence (Python API > env vars)."""
    print("=" * 70)
    print("Demo 5: Configuration precedence (Python API > env vars)")
    print("=" * 70)
    breadcrumb.reset_config()

    # Set environment variable
    os.environ["BREADCRUMB_SAMPLE_RATE"] = "0.5"
    print("Environment variable: BREADCRUMB_SAMPLE_RATE=0.5")

    # Python API overrides
    print("Python API: sample_rate=0.1")
    config = breadcrumb.init(sample_rate=0.1)
    print(f"Result: sample_rate={config.sample_rate} (Python API wins!)")

    # Clean up
    del os.environ["BREADCRUMB_SAMPLE_RATE"]
    print()


def demo_disabled():
    """Demo 6: Disabling Breadcrumb."""
    print("=" * 70)
    print("Demo 6: Disabling Breadcrumb")
    print("=" * 70)
    breadcrumb.reset_config()
    config = breadcrumb.init(enabled=False)
    print()


def demo_production_setup():
    """Demo 7: Typical production setup."""
    print("=" * 70)
    print("Demo 7: Typical production setup (10% sampling)")
    print("=" * 70)
    breadcrumb.reset_config()
    config = breadcrumb.init(
        include=["src/**/*.py"],
        exclude=["tests/**", "scripts/**"],
        sample_rate=0.1,  # 10% sampling to reduce overhead
        db_path="/var/log/app/breadcrumb.db",
    )
    print()


if __name__ == "__main__":
    print("\nBreadcrumb Configuration Demo\n")

    demo_basic_usage()
    demo_custom_configuration()
    demo_memory_backend()
    demo_environment_variables()
    demo_precedence()
    demo_disabled()
    demo_production_setup()

    print("=" * 70)
    print("Demo complete!")
    print("=" * 70)
