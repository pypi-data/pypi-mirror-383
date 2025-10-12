"""
Integration tests for Breadcrumb AI Tracer.

These tests validate the complete workflow from trace injection through
storage to querying via MCP and CLI.

All fixtures and helper functions are defined in conftest.py and are
automatically available to all test files in this directory.
"""

# Import helper functions for convenience
from .conftest import run_traced_code, wait_for_traces

__all__ = ['run_traced_code', 'wait_for_traces']
