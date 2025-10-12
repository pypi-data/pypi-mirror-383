"""
CLI command: exceptions - Show recent exceptions.

Queries the trace database for exceptions within a time range and displays them
in either JSON or table format.
"""

from typing import Optional
import sys

from breadcrumb.storage.query import find_exceptions, QueryError
from breadcrumb.cli.formatters import format_json, format_table, format_error


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


def execute_exceptions(
    since: str = "1h",
    limit: int = 10,
    format: str = "json",
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Execute the exceptions command.

    Args:
        since: Time range ("30m", "2h", "1d", or ISO datetime)
        limit: Maximum number of exceptions to show (default: 10)
        format: Output format ("json" or "table")
        db_path: Optional path to database
        verbose: Enable verbose output

    Returns:
        Exit code (0=success, 1=error, 2=no results)

    Example:
        exit_code = execute_exceptions(since="30m", limit=5, format="table")
    """
    if verbose:
        print(f"Searching for exceptions in the last {since}...", file=sys.stderr)

    try:
        # Query for exceptions
        result = find_exceptions(since=since, limit=limit, db_path=db_path)

        if not result['exceptions']:
            # No exceptions found
            if format == "json":
                output = format_json({
                    "exceptions": [],
                    "total": 0,
                    "time_range": since,
                    "message": f"No exceptions found in the last {since}"
                })
            else:
                output = f"No exceptions found in the last {since}"

            print(output)
            return EXIT_NO_RESULTS

        # Format output
        if format == "json":
            output = format_json({
                "exceptions": result['exceptions'],
                "total": result['total'],
                "time_range": result['time_range'],
                "since_datetime": result['since_datetime'],
                "limit": limit,
                "count": len(result['exceptions'])
            })
        else:
            # For table format, prepare simplified exception data
            table_data = []
            for exc in result['exceptions']:
                table_data.append({
                    'trace_id': exc.get('trace_id', 'N/A'),
                    'exception_type': exc.get('exception_type', 'N/A'),
                    'message': exc.get('message', 'N/A')[:100],  # Truncate long messages
                    'trace_started_at': exc.get('trace_started_at', 'N/A'),
                    'trace_status': exc.get('trace_status', 'N/A')
                })

            output = format_table(
                table_data,
                title=f"Exceptions (last {since}, showing {len(result['exceptions'])} of {result['total']})"
            )

        print(output)
        return EXIT_SUCCESS

    except QueryError as e:
        # Query-specific error (includes invalid time range)
        error_output = format_error(
            error_type="QueryError",
            message=str(e),
            suggestion="Check time range format (e.g., '30m', '2h', '1d') and database accessibility",
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
