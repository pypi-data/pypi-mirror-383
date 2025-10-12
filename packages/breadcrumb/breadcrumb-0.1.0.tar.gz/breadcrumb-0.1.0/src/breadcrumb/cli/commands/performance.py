"""
CLI command: performance - Analyze performance statistics for a function.

Queries the trace database for performance metrics and displays timing statistics
along with slowest traces in either JSON or table format.
"""

from typing import Optional
import sys

from breadcrumb.storage.query import analyze_performance, QueryError
from breadcrumb.cli.formatters import format_json, format_table, format_error


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


def execute_performance(
    function: str,
    limit: int = 10,
    format: str = "json",
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Execute the performance command.

    Args:
        function: Function name to analyze
        limit: Number of slowest traces to show (default: 10)
        format: Output format ("json" or "table")
        db_path: Optional path to database
        verbose: Enable verbose output

    Returns:
        Exit code (0=success, 1=error, 2=no results)

    Example:
        exit_code = execute_performance(
            function="fetch_data",
            limit=5,
            format="table"
        )
    """
    if verbose:
        print(f"Analyzing performance for function: {function}...", file=sys.stderr)

    try:
        # Query for performance statistics
        result = analyze_performance(function=function, limit=limit, db_path=db_path)

        if result['stats'] is None:
            # No traces found for function
            if format == "json":
                output = format_json({
                    "error": "FunctionNotFound",
                    "message": f"No traces found for function: {function}",
                    "suggestion": "Check function name spelling or ensure the function has been traced"
                })
            else:
                output = f"No traces found for function: {function}\nCheck function name spelling or ensure the function has been traced."

            print(output, file=sys.stderr)
            return EXIT_NO_RESULTS

        # Format output
        if format == "json":
            stats = result['stats']
            output = format_json({
                "function": function,
                "statistics": {
                    "call_count": stats['call_count'],
                    "avg_duration_ms": round(stats['avg_duration_ms'], 2) if stats['avg_duration_ms'] else None,
                    "min_duration_ms": round(stats['min_duration_ms'], 2) if stats['min_duration_ms'] else None,
                    "max_duration_ms": round(stats['max_duration_ms'], 2) if stats['max_duration_ms'] else None,
                },
                "slowest_traces": result['slowest_traces'],
                "limit": limit,
                "count": len(result['slowest_traces'])
            })
        else:
            # For table format, show statistics and slowest traces
            stats = result['stats']

            # Build statistics section
            lines = [
                f"Performance Statistics for: {function}",
                "=" * (len(function) + 27),
                "",
                f"Call Count:     {stats['call_count']}",
                f"Avg Duration:   {stats['avg_duration_ms']:.2f} ms" if stats['avg_duration_ms'] else "Avg Duration:   N/A",
                f"Min Duration:   {stats['min_duration_ms']:.2f} ms" if stats['min_duration_ms'] else "Min Duration:   N/A",
                f"Max Duration:   {stats['max_duration_ms']:.2f} ms" if stats['max_duration_ms'] else "Max Duration:   N/A",
                "",
                f"Slowest {len(result['slowest_traces'])} Traces:",
                ""
            ]

            # Add slowest traces table
            if result['slowest_traces']:
                table_data = []
                for trace in result['slowest_traces']:
                    table_data.append({
                        'trace_id': trace.get('id', 'N/A')[:36],  # Full UUID
                        'duration_ms': f"{trace.get('duration_ms', 0):.2f}",
                        'status': trace.get('status', 'N/A'),
                        'started_at': trace.get('started_at', 'N/A')
                    })

                table_output = format_table(table_data)
                lines.append(table_output)
            else:
                lines.append("No slowest traces available")

            output = "\n".join(lines)

        print(output)
        return EXIT_SUCCESS

    except QueryError as e:
        # Query-specific error
        error_output = format_error(
            error_type="QueryError",
            message=str(e),
            suggestion="Check that the database is accessible",
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
