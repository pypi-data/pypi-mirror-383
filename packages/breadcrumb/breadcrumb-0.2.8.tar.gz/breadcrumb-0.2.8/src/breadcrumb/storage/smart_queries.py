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
    try:
        import json

        # Get database connection
        manager = get_manager(db_path)
        conn = manager.get_connection()

        # Get the most recent trace_id if not specified
        trace_result = conn.execute("""
            SELECT id FROM traces
            ORDER BY started_at DESC
            LIMIT 1
        """).fetchone()

        if not trace_result:
            # No traces in database
            return {
                "function": function_name,
                "calls": []
            }

        trace_id = trace_result[0]

        # Get all call and return events for this function
        # We'll pair them up in Python to avoid complex SQL joins
        events_query = """
            SELECT
                id,
                timestamp,
                event_type,
                data
            FROM trace_events
            WHERE trace_id = ?
              AND function_name = ?
              AND event_type IN ('call', 'return')
            ORDER BY timestamp
        """

        event_rows = conn.execute(events_query, [trace_id, function_name]).fetchall()

        if not event_rows:
            # Function not found in traces
            return {
                "function": function_name,
                "calls": []
            }

        # Pair up call and return events
        # Use a stack to match calls with their returns
        rows = []
        call_stack = []

        for event_id, timestamp, event_type, data_json in event_rows:
            if event_type == 'call':
                # Push call onto stack
                call_stack.append({
                    'id': event_id,
                    'timestamp': timestamp,
                    'data': data_json
                })
            elif event_type == 'return' and call_stack:
                # Pop matching call from stack
                call_event = call_stack.pop()
                # Create matched pair
                rows.append((
                    call_event['id'],
                    call_event['timestamp'],
                    call_event['data'],
                    timestamp,
                    data_json,
                    trace_id
                ))

        if not rows:
            # Function not found in traces
            return {
                "function": function_name,
                "calls": []
            }

        # Build call records
        calls = []
        for row in rows:
            call_id, call_timestamp, call_data_json, return_timestamp, return_data_json, trace_id = row

            # Parse call data
            call_data = json.loads(call_data_json) if call_data_json else {}
            return_data = json.loads(return_data_json) if return_data_json else {}

            # Extract args and kwargs
            args = call_data.get('args', {})
            kwargs = call_data.get('kwargs', {})

            # Combine args and kwargs into single dict
            # Args are positional, but we need to convert them to named parameters
            # For now, we'll just include what's available
            call_args = {}
            if isinstance(args, dict):
                call_args.update(args)
            if isinstance(kwargs, dict):
                call_args.update(kwargs)

            # Extract return value
            return_value = return_data.get('return_value')

            # Calculate duration
            duration_ms = None
            if return_timestamp:
                # DuckDB returns timestamps as datetime objects
                from datetime import datetime

                # Handle both datetime objects and strings
                if isinstance(call_timestamp, str):
                    call_time = datetime.fromisoformat(call_timestamp.replace('Z', '+00:00'))
                else:
                    call_time = call_timestamp

                if isinstance(return_timestamp, str):
                    return_time = datetime.fromisoformat(return_timestamp.replace('Z', '+00:00'))
                else:
                    return_time = return_timestamp

                duration_seconds = (return_time - call_time).total_seconds()
                duration_ms = duration_seconds * 1000

            # Find caller (called_by)
            # Look for the most recent call event before this one that hasn't returned yet
            caller_query = """
                SELECT function_name, module_name
                FROM trace_events
                WHERE trace_id = ?
                  AND event_type = 'call'
                  AND timestamp < ?
                  AND NOT EXISTS (
                      SELECT 1 FROM trace_events r
                      WHERE r.trace_id = trace_events.trace_id
                        AND r.function_name = trace_events.function_name
                        AND r.event_type = 'return'
                        AND r.timestamp > trace_events.timestamp
                        AND r.timestamp < ?
                  )
                ORDER BY timestamp DESC
                LIMIT 1
            """
            caller_row = conn.execute(caller_query, [trace_id, call_timestamp, call_timestamp]).fetchone()

            called_by = None
            if caller_row:
                caller_function, caller_module = caller_row
                if caller_module:
                    called_by = f"{caller_module}.{caller_function}"
                else:
                    called_by = caller_function

            # Find callees (calls_made)
            # Find all distinct functions called between this call and return
            callees = []
            if return_timestamp:
                callees_query = """
                    SELECT DISTINCT function_name, module_name
                    FROM trace_events
                    WHERE trace_id = ?
                      AND event_type = 'call'
                      AND timestamp > ?
                      AND timestamp < ?
                    ORDER BY function_name
                """
                callee_rows = conn.execute(callees_query, [trace_id, call_timestamp, return_timestamp]).fetchall()

                for callee_function, callee_module in callee_rows:
                    if callee_module:
                        callees.append(f"{callee_module}.{callee_function}")
                    else:
                        callees.append(callee_function)

            # Build call record
            # Convert timestamp to ISO string if it's a datetime object
            timestamp_str = call_timestamp.isoformat() if not isinstance(call_timestamp, str) else call_timestamp

            call_record = {
                "timestamp": timestamp_str,
                "args": call_args,
                "return_value": return_value,
            }

            if duration_ms is not None:
                call_record["duration_ms"] = round(duration_ms, 3)

            if called_by:
                call_record["called_by"] = called_by

            call_record["calls_made"] = callees

            calls.append(call_record)

        return {
            "function": function_name,
            "calls": calls
        }

    except QueryError as e:
        # Database query error
        raise e
    except Exception as e:
        # Unexpected error
        raise QueryError(f"Failed to query function calls: {str(e)}")


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
    try:
        import json

        # Get database connection
        manager = get_manager(db_path)
        conn = manager.get_connection()

        # Get the most recent trace_id if not specified
        trace_result = conn.execute("""
            SELECT id FROM traces
            ORDER BY started_at DESC
            LIMIT 1
        """).fetchone()

        if not trace_result:
            # No traces in database
            return {
                "flow": []
            }

        trace_id = trace_result[0]

        # Build query with optional module filter
        query = """
            SELECT
                id,
                timestamp,
                event_type,
                function_name,
                module_name,
                data
            FROM trace_events
            WHERE trace_id = ?
              AND event_type IN ('call', 'return', 'exception')
        """

        params = [trace_id]

        if module_filter:
            query += " AND module_name = ?"
            params.append(module_filter)

        query += " ORDER BY timestamp ASC"

        rows = conn.execute(query, params).fetchall()

        if not rows:
            # No events found
            return {
                "flow": []
            }

        # Process events and calculate depth
        flow_events = []
        depth_stack = []  # Track call depth

        for event_id, timestamp, event_type, function_name, module_name, data_json in rows:
            # Parse data JSON
            data = json.loads(data_json) if data_json else {}

            # Calculate current depth
            current_depth = len(depth_stack)

            # Build event record
            # Convert timestamp to ISO string if it's a datetime object
            timestamp_str = timestamp.isoformat() if not isinstance(timestamp, str) else timestamp

            event_record = {
                "timestamp": timestamp_str,
                "event_type": event_type,
                "function": f"{module_name}.{function_name}" if module_name else function_name,
                "depth": current_depth
            }

            # Add module_name field
            if module_name:
                event_record["module_name"] = module_name

            # Add args for call events
            if event_type == 'call':
                args = data.get('args', {})
                kwargs = data.get('kwargs', {})

                # Combine args and kwargs
                call_args = {}
                if isinstance(args, dict):
                    call_args.update(args)
                if isinstance(kwargs, dict):
                    call_args.update(kwargs)

                if call_args:
                    event_record["args"] = call_args

                # Push onto depth stack
                depth_stack.append(function_name)

            # Add return_value for return events
            elif event_type == 'return':
                return_value = data.get('return_value')
                if return_value is not None:
                    event_record["return_value"] = return_value

                # Pop from depth stack (if not empty)
                if depth_stack:
                    depth_stack.pop()

            # Add exception info for exception events
            elif event_type == 'exception':
                exception_info = data.get('exception')
                if exception_info:
                    event_record["exception"] = exception_info

            flow_events.append(event_record)

        return {
            "flow": flow_events
        }

    except QueryError as e:
        # Database query error
        raise e
    except Exception as e:
        # Unexpected error
        raise QueryError(f"Failed to query execution flow: {str(e)}")


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
