"""
Query command implementation.

Executes SQL queries against the trace database with support for JSON and table output.
"""

from typing import Optional
import sys

from breadcrumb.storage.query import query_traces, QueryError, InvalidQueryError
from breadcrumb.cli.formatters import format_json, format_table, format_error


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


def execute_query(
    sql: str,
    format: str = "json",
    db_path: Optional[str] = None,
    verbose: bool = False,
    disable_truncation: bool = False
) -> int:
    """
    Execute SQL query against trace database.

    Args:
        sql: SQL SELECT query to execute
        format: Output format ("json" or "table")
        db_path: Optional path to traces.duckdb database
        verbose: Enable verbose output

    Returns:
        Exit code (0=success, 1=error, 2=no results)

    Example:
        exit_code = execute_query(
            "SELECT * FROM traces LIMIT 5",
            format="json"
        )
    """
    if verbose:
        print(f"Executing query: {sql}", file=sys.stderr)
        if db_path:
            print(f"Database: {db_path}", file=sys.stderr)

    try:
        # Execute query using storage layer
        results = query_traces(sql, params=None, db_path=db_path)

        if verbose:
            print(f"Query returned {len(results)} rows", file=sys.stderr)

        # Check for empty results
        if not results:
            # Return exit code 2 for no results
            if format == "json":
                # Still output valid JSON for empty results
                output = format_json({"results": [], "total": 0})
                print(output)
            else:
                # Table format: show "No results" message
                print("No results")

            return EXIT_NO_RESULTS

        # Format and output results
        if format == "json":
            output = format_json({"results": results, "total": len(results)})
        else:  # table
            output = format_table(results, disable_truncation=disable_truncation)

        print(output)
        return EXIT_SUCCESS

    except InvalidQueryError as e:
        # Invalid SQL query
        error_msg = format_error(
            error_type="InvalidQueryError",
            message=str(e),
            suggestion="Ensure you're using a SELECT query. Only SELECT queries are allowed for safety.",
            format=format
        )
        print(error_msg, file=sys.stderr)
        return EXIT_ERROR

    except QueryError as e:
        # General query error (e.g., syntax error, database connection issue)
        error_msg = format_error(
            error_type="QueryError",
            message=str(e),
            suggestion="Check SQL syntax and database path. Use --verbose for more details.",
            format=format
        )
        print(error_msg, file=sys.stderr)
        return EXIT_ERROR

    except FileNotFoundError as e:
        # Database not found
        error_msg = format_error(
            error_type="DatabaseNotFound",
            message=str(e),
            suggestion="Check that the database path is correct or use --db-path to specify the location.",
            format=format
        )
        print(error_msg, file=sys.stderr)
        return EXIT_ERROR

    except Exception as e:
        # Unexpected error
        error_msg = format_error(
            error_type="UnexpectedError",
            message=str(e),
            suggestion="Use --verbose for more details.",
            format=format
        )
        print(error_msg, file=sys.stderr)

        if verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)

        return EXIT_ERROR
