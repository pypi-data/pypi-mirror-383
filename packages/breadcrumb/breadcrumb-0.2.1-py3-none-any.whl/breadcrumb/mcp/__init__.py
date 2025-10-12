"""
MCP server for Breadcrumb AI Tracer.

Exposes trace data to AI agents via Model Context Protocol.
"""

from breadcrumb.mcp.server import create_mcp_server, run_server

__all__ = [
    'create_mcp_server',
    'run_server',
]
