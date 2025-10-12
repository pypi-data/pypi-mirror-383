"""
CLI command: list - Show recent traces.

Queries the trace database for the most recent traces and displays them
in either JSON or table format.
"""

from typing import Optional
import sys

from breadcrumb.storage.query import query_traces, QueryError
from breadcrumb.cli.formatters import format_json, format_table, format_error


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


def execute_list(
    limit: int = 10,
    format: str = "json",
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Execute the list command.

    Args:
        limit: Number of traces to show (default: 10)
        format: Output format ("json" or "table")
        db_path: Optional path to database
        verbose: Enable verbose output

    Returns:
        Exit code (0=success, 1=error, 2=no results)

    Example:
        exit_code = execute_list(limit=20, format="table")
    """
    if verbose:
        print(f"Querying {limit} most recent traces...", file=sys.stderr)

    try:
        # Query for recent traces ordered by started_at descending
        sql = """
            SELECT
                id,
                status,
                started_at,
                ended_at,
                thread_id,
                metadata
            FROM traces
            ORDER BY started_at DESC
            LIMIT ?
        """

        results = query_traces(sql, params=[limit], db_path=db_path)

        if not results:
            # No traces found
            if format == "json":
                output = format_json({
                    "traces": [],
                    "count": 0,
                    "message": "No traces found in database"
                })
            else:
                output = "No traces found in database"

            print(output)
            return EXIT_NO_RESULTS

        # Format output
        if format == "json":
            output = format_json({
                "traces": results,
                "count": len(results)
            })
        else:
            output = format_table(results, title=f"Recent Traces (limit: {limit})")

        print(output)
        return EXIT_SUCCESS

    except QueryError as e:
        # Query-specific error
        error_output = format_error(
            error_type="QueryError",
            message=str(e),
            suggestion="Check that the database exists and is accessible",
            format=format
        )
        print(error_output, file=sys.stderr)
        return EXIT_ERROR

    except Exception as e:
        # Unexpected error
        error_output = format_error(
            error_type="UnexpectedError",
            message=str(e),
            suggestion="Run with --verbose for more details",
            format=format
        )
        print(error_output, file=sys.stderr)

        if verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)

        return EXIT_ERROR
