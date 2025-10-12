"""
Breadcrumb - AI-native Python execution tracer

Zero-config execution tracing with MCP integration for AI agents.
"""

__version__ = "0.1.0"

from .config import (
    init,
    get_config,
    reset_config,
    get_backend,
    get_events,
    shutdown,
    BreadcrumbConfig,
)

__all__ = [
    "init",
    "get_config",
    "reset_config",
    "get_backend",
    "get_events",
    "shutdown",
    "BreadcrumbConfig",
]
