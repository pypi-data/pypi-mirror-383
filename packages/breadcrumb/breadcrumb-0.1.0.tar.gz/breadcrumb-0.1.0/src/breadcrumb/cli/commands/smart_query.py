"""
Smart query command implementation.

Enhanced query commands that replace raw SQL with intelligent analysis:
- --gaps: Show untraced function calls
- --call <function>: Show function call details with I/O
- --flow: Show execution timeline
- --sql <query>: Fallback to raw SQL

Routes commands to appropriate query functions in storage.smart_queries.
"""

from typing import Optional
import sys

from breadcrumb.storage.smart_queries import gaps_query, call_query, flow_query
from breadcrumb.storage.query import query_traces, QueryError, InvalidQueryError
from breadcrumb.cli.formatters import format_json, format_error


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


def execute_smart_query(
    gaps: bool = False,
    call: Optional[str] = None,
    flow: bool = False,
    module: Optional[str] = None,
    sql: Optional[str] = None,
    format: str = "json",
    db_path: Optional[str] = None,
    verbose: bool = False,
    config: Optional[str] = None
) -> int:
    """
    Execute smart query command.

    Routes to appropriate query function based on parameters:
    - gaps=True: Call gaps_query()
    - call=<name>: Call call_query()
    - flow=True: Call flow_query()
    - sql=<query>: Fall back to raw SQL query

    Args:
        gaps: Show untraced function calls
        call: Function name for call analysis
        flow: Show execution timeline
        module: Module filter (for flow command)
        sql: Raw SQL query (fallback)
        format: Output format ("json" or "table")
        db_path: Optional path to traces.duckdb database
        verbose: Enable verbose output
        config: Named configuration profile to load

    Returns:
        Exit code (0=success, 1=error, 2=no results)

    Example:
        # Show gaps
        exit_code = execute_smart_query(gaps=True, db_path="/path/to/traces.duckdb")

        # Show function calls
        exit_code = execute_smart_query(call="calculate_total", format="json")

        # Show execution flow
        exit_code = execute_smart_query(flow=True, module="__main__")
    """
    if verbose:
        print("Smart query command executing...", file=sys.stderr)
        if db_path:
            print(f"Database: {db_path}", file=sys.stderr)

    # Config parameter is REQUIRED for CLI usage
    if config is None and db_path is None:
        error_msg = format_error(
            error_type="ConfigRequired",
            message="Config parameter is required. Specify which trace to query using -c/--config",
            suggestion="Example: breadcrumb -c myproject query --gaps\nOr use --db-path to specify database directly: breadcrumb --db-path /path/to/traces.duckdb query --gaps",
            format=format
        )
        print(error_msg, file=sys.stderr)
        return EXIT_ERROR

    # Load config and get db_path
    effective_db_path = db_path
    if config:
        try:
            from breadcrumb.cli.commands.config import load_config
            config_values = load_config(config)
            # Use config's db_path if not overridden by --db-path
            if db_path is None and 'db_path' in config_values:
                effective_db_path = config_values['db_path']
                if verbose:
                    print(f"Using db_path from config '{config}': {effective_db_path}", file=sys.stderr)
        except FileNotFoundError as e:
            error_msg = format_error(
                error_type="ConfigNotFound",
                message=str(e),
                suggestion=f"Use 'breadcrumb config create {config}' to create it",
                format=format
            )
            print(error_msg, file=sys.stderr)
            return EXIT_ERROR

    # Validate: only one query type at a time
    query_types_selected = sum([
        gaps,
        call is not None,
        flow,
        sql is not None
    ])

    if query_types_selected == 0:
        error_msg = format_error(
            error_type="NoQueryType",
            message="No query type specified. Use --gaps, --call, --flow, or --sql",
            suggestion="Example: breadcrumb query --gaps",
            format=format
        )
        print(error_msg, file=sys.stderr)
        return EXIT_ERROR

    if query_types_selected > 1:
        error_msg = format_error(
            error_type="MultipleQueryTypes",
            message="Multiple query types specified. Please use only one: --gaps, --call, --flow, or --sql",
            suggestion="Example: breadcrumb query --gaps (not --gaps --flow)",
            format=format
        )
        print(error_msg, file=sys.stderr)
        return EXIT_ERROR

    try:
        # Route to appropriate query function
        if gaps:
            if verbose:
                print("Executing gaps query...", file=sys.stderr)
            result = gaps_query(db_path=effective_db_path)

        elif call is not None:
            if verbose:
                print(f"Executing call query for function: {call}", file=sys.stderr)
            result = call_query(db_path=effective_db_path, function_name=call)

        elif flow:
            if verbose:
                print("Executing flow query...", file=sys.stderr)
            result = flow_query(db_path=effective_db_path, module_filter=module)

        elif sql is not None:
            # Fallback to raw SQL using existing query command
            if verbose:
                print(f"Executing raw SQL query: {sql}", file=sys.stderr)
            from breadcrumb.cli.commands.query import execute_query
            return execute_query(
                sql=sql,
                format=format,
                db_path=effective_db_path,
                verbose=verbose
            )

        else:
            # Should never reach here due to validation above
            error_msg = format_error(
                error_type="InvalidQueryType",
                message="Invalid query type",
                format=format
            )
            print(error_msg, file=sys.stderr)
            return EXIT_ERROR

        # Format and output result
        if verbose:
            print(f"Query completed successfully", file=sys.stderr)

        # Check for empty results
        has_results = False
        if 'untraced_calls' in result and len(result['untraced_calls']) > 0:
            has_results = True
        elif 'calls' in result and len(result['calls']) > 0:
            has_results = True
        elif 'flow' in result and len(result['flow']) > 0:
            has_results = True
        elif 'events' in result and len(result['events']) > 0:
            has_results = True
        elif 'status' in result:
            # Stub response - still output it
            has_results = True

        if not has_results and result.get('status') != 'not_implemented':
            if format == "json":
                # Still output valid JSON for empty results
                output = format_json(result)
                print(output)
            else:
                print("No results")
            return EXIT_NO_RESULTS

        # Output result
        output = format_json(result)
        print(output)
        return EXIT_SUCCESS

    except QueryError as e:
        # Query execution error
        error_msg = format_error(
            error_type="QueryError",
            message=str(e),
            suggestion="Check database path and try again. Use --verbose for more details.",
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
