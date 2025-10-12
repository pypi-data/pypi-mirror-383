"""
CLI command: serve-mcp - Start MCP server for AI agents.

Launches the Model Context Protocol server on stdio transport.
This allows AI agents (like Claude Desktop) to query trace data.
"""

from typing import Optional
import sys

from breadcrumb.mcp.server import run_server


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1


def execute_serve_mcp(
    db_path: Optional[str] = None,
    port: Optional[int] = None,
    verbose: bool = False
) -> int:
    """
    Execute the serve-mcp command.

    Starts the MCP server and blocks until interrupted (Ctrl+C).
    The server uses stdio transport by default.

    Args:
        db_path: Optional path to traces.duckdb database
        port: Optional port for TCP transport (not yet implemented)
        verbose: Enable verbose output

    Returns:
        Exit code (0=success, 1=error)

    Example:
        exit_code = execute_serve_mcp(db_path="/path/to/traces.duckdb", verbose=True)
    """
    # Warn if port is specified (TCP transport not yet implemented)
    if port is not None:
        print("Warning: TCP transport not yet implemented. Using stdio transport.", file=sys.stderr)

    # Log startup info if verbose
    if verbose:
        print("Starting Breadcrumb MCP Server...", file=sys.stderr)
        if db_path:
            print(f"Database: {db_path}", file=sys.stderr)
        else:
            print("Database: auto-discover", file=sys.stderr)

    # Run the MCP server (this will block until interrupted)
    # The run_server function handles its own error logging via sys.exit()
    try:
        run_server(db_path)
        # If run_server returns normally (shouldn't happen), exit successfully
        return EXIT_SUCCESS
    except KeyboardInterrupt:
        # Graceful shutdown on Ctrl+C
        if verbose:
            print("\nServer shutdown complete", file=sys.stderr)
        return EXIT_SUCCESS
    except SystemExit as e:
        # run_server calls sys.exit() on errors
        # Propagate the exit code
        return e.code if isinstance(e.code, int) else EXIT_ERROR
    except Exception as e:
        # Unexpected error
        print(f"Error: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return EXIT_ERROR
