"""
Breadcrumb CLI module.

Provides command-line interface for querying traces, analyzing performance,
and serving the MCP server.
"""

from .main import app, cli

__all__ = ["app", "cli"]
