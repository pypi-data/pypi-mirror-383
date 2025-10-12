"""
FastMCP server for Breadcrumb AI Tracer.

Exposes trace data to AI agents via Model Context Protocol (MCP).
"""

import os
import sys
from pathlib import Path
from typing import Optional
import json

from fastmcp import FastMCP

from breadcrumb.storage.query import (
    query_traces,
    get_trace,
    find_exceptions,
    analyze_performance,
    QueryError,
    InvalidQueryError,
    TraceNotFoundError,
    QueryTimeoutError,
)
from breadcrumb.storage.migrations import CURRENT_SCHEMA_VERSION


def find_breadcrumb_database(start_path: Optional[Path] = None, max_levels: int = 5) -> Optional[Path]:
    """
    Search for .breadcrumb/traces.duckdb in current directory and parent directories.

    Args:
        start_path: Starting directory for search (defaults to current directory)
        max_levels: Maximum number of parent directories to search (default: 5)

    Returns:
        Path to traces.duckdb if found, None otherwise
    """
    current = start_path or Path.cwd()

    for _ in range(max_levels):
        db_path = current / ".breadcrumb" / "traces.duckdb"
        if db_path.exists():
            return db_path

        # Move to parent directory
        parent = current.parent
        if parent == current:
            # Reached root directory
            break
        current = parent

    return None


def create_mcp_server(db_path: Optional[str] = None) -> FastMCP:
    """
    Create and configure the MCP server with tools.

    Args:
        db_path: Optional path to traces.duckdb. If not provided, will search
                for database in current directory and parent directories.

    Returns:
        Configured FastMCP server instance

    Raises:
        FileNotFoundError: If database cannot be found
    """
    # Discover database if not provided
    if db_path is None:
        discovered_db = find_breadcrumb_database()
        if discovered_db is None:
            raise FileNotFoundError(
                "Could not find .breadcrumb/traces.duckdb. "
                "Make sure you have initialized Breadcrumb tracing in your project. "
                "Run: python -c 'import breadcrumb; breadcrumb.init()' to create the database."
            )
        db_path = str(discovered_db)
    else:
        # Verify provided path exists
        db_file = Path(db_path)
        if not db_file.exists():
            # Check if parent directory exists
            if not db_file.parent.exists():
                raise FileNotFoundError(
                    f"Database directory not found: {db_file.parent}. "
                    f"Make sure the path is correct and the directory exists."
                )
            raise FileNotFoundError(
                f"Database not found at: {db_path}. "
                f"Make sure the path is correct and the database has been initialized."
            )

    # Create FastMCP server
    mcp = FastMCP("breadcrumb-tracer")

    # Store database path for tools to access
    mcp.db_path = db_path

    # Register tools
    @mcp.tool()
    def breadcrumb__query_traces(sql: str) -> str:
        """
        Execute a SQL query against the trace database.

        This tool allows you to query traces, events, exceptions, and their relationships.
        Only SELECT queries are allowed for safety.

        Args:
            sql: SQL SELECT query to execute

        Returns:
            JSON string with query results and metadata

        Example queries:
            - Get recent traces: SELECT * FROM traces ORDER BY started_at DESC LIMIT 10
            - Find slow functions: SELECT function_name, COUNT(*) as calls FROM trace_events WHERE event_type='call' GROUP BY function_name
            - Search by status: SELECT * FROM traces WHERE status = 'failed'
        """
        try:
            import time

            start_time = time.time()
            results = query_traces(sql, params=None, db_path=mcp.db_path)
            query_time_ms = int((time.time() - start_time) * 1000)

            response = {
                "traces": results,
                "total": len(results),
                "query_time_ms": query_time_ms,
                "schema_version": CURRENT_SCHEMA_VERSION,
            }

            # Check response size (1MB limit)
            response_json = json.dumps(response, default=str, indent=2)
            MAX_SIZE = 1024 * 1024

            if len(response_json.encode('utf-8')) > MAX_SIZE and len(results) > 1:
                # Truncate results
                truncated_count = len(results)
                results = results[:len(results) // 2]
                response = {
                    "traces": results,
                    "total": truncated_count,
                    "query_time_ms": query_time_ms,
                    "schema_version": CURRENT_SCHEMA_VERSION,
                    "warning": f"Response truncated from {truncated_count} to {len(results)} results (1MB limit). Use LIMIT in your query.",
                }
                response_json = json.dumps(response, default=str, indent=2)

            return response_json

        except QueryTimeoutError as e:
            error_response = {
                "error": "QueryTimeoutError",
                "message": str(e),
                "suggestion": "Query exceeded 30 second timeout. Use LIMIT to reduce result set or simplify your query.",
            }
            return json.dumps(error_response, indent=2)

        except (InvalidQueryError, QueryError) as e:
            # Check if this is an empty database error
            error_msg = str(e)
            if "No trace data found" in error_msg or "table" in error_msg.lower() and "not found" in error_msg.lower():
                error_response = {
                    "error": "EmptyDatabaseError",
                    "message": "No traces found in database",
                    "suggestion": "To start tracing, add 'import breadcrumb; breadcrumb.init()' to your Python code and run your application. See docs/QUICKSTART.md for setup instructions.",
                }
            else:
                error_response = {
                    "error": type(e).__name__,
                    "message": str(e),
                    "suggestion": "Check SQL syntax and ensure only SELECT queries are used. Available tables: traces, trace_events, exceptions",
                }
            return json.dumps(error_response, indent=2)

    @mcp.tool()
    def breadcrumb__get_trace(trace_id: str) -> str:
        """
        Get complete trace details by ID.

        Retrieves a full trace including metadata, all events, and any exceptions.
        Use this when you know the specific trace ID and want all details.

        Args:
            trace_id: UUID of the trace to retrieve

        Returns:
            JSON string with complete trace data

        Example:
            breadcrumb__get_trace("123e4567-e89b-12d3-a456-426614174000")
        """
        try:
            trace_data = get_trace(trace_id, db_path=mcp.db_path)

            response = {
                "trace": trace_data['trace'],
                "events": trace_data['events'],
                "exceptions": trace_data['exceptions'],
                "summary": {
                    "trace_id": trace_id,
                    "status": trace_data['trace']['status'],
                    "event_count": len(trace_data['events']),
                    "exception_count": len(trace_data['exceptions']),
                },
            }

            return json.dumps(response, default=str, indent=2)

        except TraceNotFoundError:
            error_response = {
                "error": "TraceNotFoundError",
                "message": f"No trace found with ID: {trace_id}",
                "suggestion": "Use breadcrumb__query_traces to find available trace IDs",
            }
            return json.dumps(error_response, indent=2)

    @mcp.tool()
    def breadcrumb__find_exceptions(since: str = "1h", limit: int = 10) -> str:
        """
        Find exceptions within a time range.

        Search for exceptions that occurred recently. Useful for debugging failures.

        Args:
            since: Time range to search. Supports relative ("30m", "2h", "1d") or absolute ("2025-01-10") formats. Default: "1h"
            limit: Maximum number of exceptions to return. Default: 10

        Returns:
            JSON string with exception list and metadata

        Examples:
            - Last hour: breadcrumb__find_exceptions(since="1h")
            - Last 30 minutes: breadcrumb__find_exceptions(since="30m", limit=5)
        """
        try:
            result = find_exceptions(since=since, limit=limit, db_path=mcp.db_path)

            response = {
                "exceptions": result['exceptions'],
                "total": result['total'],
                "time_range": result['time_range'],
                "limit": limit,
            }

            if result['total'] == 0:
                response['message'] = f"No exceptions found in the specified time range"

            return json.dumps(response, default=str, indent=2)

        except ValueError as e:
            error_response = {
                "error": "ValueError",
                "message": str(e),
                "suggestion": "Use relative time ('30m', '2h', '1d') or absolute time ('2025-01-10')",
            }
            return json.dumps(error_response, indent=2)

    @mcp.tool()
    def breadcrumb__analyze_performance(function: str, limit: int = 10) -> str:
        """
        Analyze performance statistics for a function.

        Calculates timing statistics (avg, min, max) and returns the slowest traces.
        Use this to identify performance bottlenecks.

        Args:
            function: Name of the function to analyze
            limit: Number of slowest traces to return. Default: 10

        Returns:
            JSON string with performance statistics and slowest traces

        Examples:
            - analyze_performance(function="fetch_data")
            - analyze_performance(function="process_payment", limit=5)
        """
        try:
            result = analyze_performance(function=function, limit=limit, db_path=mcp.db_path)

            if result['stats'] is None:
                error_response = {
                    "error": "FunctionNotFound",
                    "message": f"No traces found for function: {function}",
                    "suggestion": "Check function name spelling. Use breadcrumb__query_traces to find available functions",
                }
                return json.dumps(error_response, indent=2)

            stats = result['stats']
            response = {
                "function": function,
                "statistics": {
                    "call_count": stats['call_count'],
                    "avg_duration_ms": round(stats['avg_duration_ms'], 2) if stats['avg_duration_ms'] else None,
                    "min_duration_ms": round(stats['min_duration_ms'], 2) if stats['min_duration_ms'] else None,
                    "max_duration_ms": round(stats['max_duration_ms'], 2) if stats['max_duration_ms'] else None,
                },
                "slowest_traces": result['slowest_traces'],
            }

            return json.dumps(response, default=str, indent=2)

        except QueryError as e:
            error_response = {
                "error": "QueryError",
                "message": str(e),
                "suggestion": "Check that the database is accessible",
            }
            return json.dumps(error_response, indent=2)

    # Log server initialization
    print(f"Breadcrumb MCP Server initialized", file=sys.stderr)
    print(f"Database: {db_path}", file=sys.stderr)
    print(f"Tools: 4 registered (query_traces, get_trace, find_exceptions, analyze_performance)", file=sys.stderr)

    return mcp


def run_server(db_path: Optional[str] = None):
    """
    Run the MCP server.

    Args:
        db_path: Optional path to traces.duckdb
    """
    try:
        mcp = create_mcp_server(db_path)
        mcp.run(transport="stdio")

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Allow passing database path as command-line argument
    db_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_server(db_path)
