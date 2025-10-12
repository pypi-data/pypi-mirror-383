"""
Smart query functions for breadcrumb CLI.

Provides high-level query functions that abstract away SQL complexity:
- gaps_query: Detect untraced function calls
- call_query: Show function call details with I/O
- flow_query: Show execution timeline
- get_call_stack: Build call stack hierarchy

These functions return structured dictionaries ready for JSON output.
"""

from typing import Optional, Dict, Any, List
from breadcrumb.storage.connection import get_manager
from breadcrumb.storage.query import QueryError


def gaps_query(
    db_path: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find untraced function calls (gaps in tracing coverage).

    Analyzes trace data to identify functions that were called but not traced,
    usually because they don't match include/exclude patterns. This helps users
    iteratively expand their tracing configuration.

    Args:
        db_path: Optional path to traces.duckdb database (if not provided, uses config)
        trace_id: Optional trace ID to analyze (default: most recent)

    Returns:
        Dictionary with:
            - untraced_calls: List of untraced function calls
            - each call includes: function name, call count, caller context, suggested_include pattern
            - tip: Suggestion for expanding tracing configuration

    Example:
        result = gaps_query()
        for call in result['untraced_calls']:
            print(f"{call['function']} called {call['call_count']} times by {call['called_by']}")
            print(f"  Suggestion: Add '{call['suggested_include']}' to include patterns")
    """
    try:
        # Get database connection
        # db_path can be None - ConnectionManager will use default path
        manager = get_manager(db_path)
        conn = manager.get_connection()

        # If no trace_id specified, get most recent trace
        if trace_id is None:
            result = conn.execute("""
                SELECT id FROM traces
                ORDER BY started_at DESC
                LIMIT 1
            """).fetchone()

            if not result:
                # No traces in database
                return {
                    "untraced_calls": [],
                    "tip": "No traces found. Run your code with breadcrumb tracing first."
                }

            trace_id = result[0]

        # Query for call_site events (untraced calls)
        query = """
            SELECT
                function_name,
                module_name,
                data
            FROM trace_events
            WHERE trace_id = ?
              AND event_type = 'call_site'
            ORDER BY timestamp
        """

        rows = conn.execute(query, [trace_id]).fetchall()

        if not rows:
            # No gaps found - everything was traced!
            return {
                "untraced_calls": [],
                "tip": "No gaps detected! All function calls are being traced."
            }

        # Aggregate gaps by function
        gaps_dict = {}  # key: (function_name, module_name), value: {callers, count}

        for row in rows:
            function_name, module_name, data_json = row

            # Parse data JSON to get caller information
            import json
            data = json.loads(data_json) if data_json else {}

            caller_function = data.get('called_from_function', 'unknown')
            caller_module = data.get('called_from_module', 'unknown')

            # Create fully qualified function name
            if module_name:
                full_function = f"{module_name}.{function_name}"
            else:
                full_function = function_name

            # Create fully qualified caller name
            if caller_module and caller_function:
                full_caller = f"{caller_module}.{caller_function}"
            else:
                full_caller = caller_function or 'unknown'

            # Aggregate
            key = (full_function, module_name or 'unknown')
            if key not in gaps_dict:
                gaps_dict[key] = {
                    'callers': set(),
                    'count': 0,
                    'module': module_name or 'unknown'
                }

            gaps_dict[key]['callers'].add(full_caller)
            gaps_dict[key]['count'] += 1

        # Build untraced_calls list
        untraced_calls = []

        for (full_function, module), info in sorted(gaps_dict.items(), key=lambda x: x[1]['count'], reverse=True):
            # Generate suggested include pattern
            module_name = info['module']
            if module_name and module_name != 'unknown':
                # Suggest module.* pattern
                suggested_include = f"{module_name}.*"
            else:
                # Can't suggest without module
                suggested_include = full_function

            # Get first caller (most common)
            caller = next(iter(info['callers'])) if info['callers'] else 'unknown'

            untraced_calls.append({
                "function": full_function,
                "module": module_name,
                "called_by": caller,
                "call_count": info['count'],
                "suggested_include": suggested_include
            })

        # Generate tip with config commands
        if untraced_calls:
            # Get unique modules
            unique_modules = set(call['module'] for call in untraced_calls if call['module'] != 'unknown')

            tip_lines = ["Add these to your config to trace them:"]
            for module in sorted(unique_modules)[:3]:  # Top 3 modules
                tip_lines.append(f"  breadcrumb config edit <name> --add-include '{module}.*'")

            tip = "\n".join(tip_lines)
        else:
            tip = "No gaps detected!"

        return {
            "untraced_calls": untraced_calls,
            "tip": tip
        }

    except QueryError as e:
        # Database query error
        raise e
    except Exception as e:
        # Unexpected error
        raise QueryError(f"Failed to analyze gaps: {str(e)}")


def call_query(
    db_path: Optional[str] = None,
    function_name: str = ""
) -> Dict[str, Any]:
    """
    Show detailed information about function calls.

    Retrieves all invocations of a specific function with complete I/O details:
    arguments, return values, duration, caller/callee relationships.

    Args:
        db_path: Optional path to traces.duckdb database
        function_name: Name of function to query

    Returns:
        Dictionary with:
            - function: Function name
            - calls: List of call records
            - each call includes: timestamp, args, return_value, duration_ms, called_by, calls_made

    Example:
        result = call_query(function_name="calculate_total")
        for call in result['calls']:
            print(f"Called at {call['timestamp']} with args: {call['args']}")
            print(f"Returned: {call['return_value']} in {call['duration_ms']}ms")
    """
    # TODO: Implementation in Phase 4
    # This will:
    # 1. Query trace_events WHERE function_name = ?
    # 2. Extract data JSON column (args, kwargs, return_value)
    # 3. Calculate duration from timestamp pairs (PY_START/PY_RETURN)
    # 4. Build caller/callee relationships from call stack
    # 5. Format as structured dictionary
    return {"status": "not_implemented"}


def flow_query(
    db_path: Optional[str] = None,
    module_filter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Show execution timeline (chronological flow of function calls).

    Displays events in the order they occurred, showing the complete execution
    path through the code. Optionally filters by module.

    Args:
        db_path: Optional path to traces.duckdb database
        module_filter: Optional module name to filter events (e.g., '__main__')

    Returns:
        Dictionary with:
            - flow: List of events in chronological order
            - each event includes: timestamp, event_type, function_name, depth, module_name
            - untraced_calls: Optional list of detected gaps

    Example:
        result = flow_query(module_filter='__main__')
        for event in result['flow']:
            indent = "  " * event['depth']
            print(f"{indent}{event['event_type']} {event['function_name']}")
    """
    # TODO: Implementation in Phase 5
    # This will:
    # 1. Query trace_events ORDER BY timestamp
    # 2. Optionally filter WHERE module_name = ?
    # 3. Calculate nesting depth from call stack
    # 4. Identify gaps (calls to untraced functions)
    # 5. Return chronologically ordered events
    return {"status": "not_implemented"}


def get_call_stack(
    db_path: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build complete call stack hierarchy for a trace.

    Reconstructs the nested function call structure by analyzing event
    pairs (PY_START/PY_RETURN) and their relationships.

    Args:
        db_path: Optional path to traces.duckdb database
        trace_id: Optional trace ID (default: most recent)

    Returns:
        Dictionary with:
            - trace_id: Trace UUID
            - call_stack: Hierarchical structure of function calls
            - each node includes: function_name, children, depth, duration_ms

    Example:
        result = get_call_stack()
        def print_stack(node, indent=0):
            print("  " * indent + node['function_name'])
            for child in node.get('children', []):
                print_stack(child, indent + 1)
        print_stack(result['call_stack'])
    """
    # TODO: Implementation helper for other queries
    # This will:
    # 1. Query trace_events for given trace_id
    # 2. Match PY_START with corresponding PY_RETURN events
    # 3. Build parent-child relationships using event sequence
    # 4. Calculate depth and duration for each call
    # 5. Return hierarchical structure
    return {"status": "not_implemented"}
