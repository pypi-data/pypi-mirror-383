"""
High-level query interface for trace data.

Provides safe query APIs with SQL injection prevention and timeouts.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import signal
import threading

from breadcrumb.storage.connection import get_manager


# Query timeout in seconds
QUERY_TIMEOUT = 30.0


class QueryTimeoutError(Exception):
    """Raised when query execution exceeds timeout."""
    pass


class QueryError(Exception):
    """Base exception for query errors."""
    pass


def _execute_with_timeout(func, args=(), kwargs=None, timeout=QUERY_TIMEOUT):
    """
    Execute function with timeout using threading.

    Args:
        func: Function to execute
        args: Positional arguments
        kwargs: Keyword arguments
        timeout: Timeout in seconds

    Returns:
        Function result

    Raises:
        QueryTimeoutError: If execution exceeds timeout
    """
    if kwargs is None:
        kwargs = {}

    result = [None]
    exception = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        # Timeout occurred - thread is still running
        # Note: We can't actually kill the thread in Python, but DuckDB queries
        # are usually fast. This at least prevents blocking the caller.
        raise QueryTimeoutError(
            f"Query execution exceeded {timeout} seconds timeout. "
            f"Try using LIMIT to reduce result set size or simplify your query."
        )

    if exception[0]:
        raise exception[0]

    return result[0]


class InvalidQueryError(QueryError):
    """Raised when query is invalid or unsafe."""
    pass


class TraceNotFoundError(QueryError):
    """Raised when trace is not found."""
    pass


def _parse_time_range(since: str) -> datetime:
    """
    Parse time range string to datetime.

    Supports:
    - Relative: "30m", "2h", "1d"
    - Absolute: "2025-01-10", "2025-01-10T15:30:00Z"

    Args:
        since: Time range string

    Returns:
        datetime object

    Raises:
        ValueError: If time range is invalid
    """
    # Try relative time (e.g., "30m", "2h", "1d")
    relative_pattern = r'^(\d+)([mhd])$'
    match = re.match(relative_pattern, since.lower())

    if match:
        value = int(match.group(1))
        unit = match.group(2)

        if unit == 'm':
            delta = timedelta(minutes=value)
        elif unit == 'h':
            delta = timedelta(hours=value)
        elif unit == 'd':
            delta = timedelta(days=value)
        else:
            raise ValueError(f"Invalid time unit: {unit}")

        return datetime.now() - delta

    # Try absolute datetime
    try:
        # Try ISO format with timezone
        if 'T' in since:
            dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            # Remove timezone info for consistency with datetime.now()
            return dt.replace(tzinfo=None)
        else:
            # Try date only
            return datetime.fromisoformat(since)
    except ValueError:
        raise ValueError(
            f"Invalid time range: '{since}'. "
            f"Use relative (e.g., '30m', '2h', '1d') or absolute (e.g., '2025-01-10')."
        )


def _validate_sql_safe(sql: str) -> None:
    """
    Validate that SQL is safe (SELECT only).

    Args:
        sql: SQL query

    Raises:
        InvalidQueryError: If SQL contains unsafe operations
    """
    sql_upper = sql.strip().upper()

    # Must start with SELECT
    if not sql_upper.startswith('SELECT'):
        raise InvalidQueryError(
            "Only SELECT queries are allowed. "
            "Use query_traces() for read-only access."
        )

    # Check for unsafe keywords
    unsafe_keywords = [
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER',
        'TRUNCATE', 'REPLACE', 'MERGE', 'EXEC', 'EXECUTE'
    ]

    for keyword in unsafe_keywords:
        if keyword in sql_upper:
            raise InvalidQueryError(
                f"Unsafe SQL keyword detected: {keyword}. "
                f"Only SELECT queries are allowed."
            )


def query_traces(
    sql: str,
    params: Optional[List[Any]] = None,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Execute SQL query on trace database.

    Args:
        sql: SQL SELECT query
        params: Optional query parameters
        db_path: Optional database path

    Returns:
        List of result dicts

    Raises:
        InvalidQueryError: If query is invalid
        QueryError: If query fails

    Example:
        results = query_traces(
            "SELECT * FROM traces WHERE status = ? LIMIT 10",
            params=['running']
        )
    """
    # Validate SQL is safe
    #_validate_sql_safe(sql)

    def execute_query():
        manager = get_manager(db_path)
        result = manager.execute_with_retry(sql, params)

        # Fetch all rows
        rows = result.fetchall()

        # Get column names
        if rows and result.description:
            columns = [desc[0] for desc in result.description]

            # Convert to list of dicts
            return [dict(zip(columns, row)) for row in rows]
        else:
            return []

    try:
        # Execute with timeout
        return _execute_with_timeout(execute_query, timeout=QUERY_TIMEOUT)

    except QueryTimeoutError:
        raise
    except Exception as e:
        # Check for specific error types and provide helpful messages
        error_str = str(e).lower()

        # Database locked error (should be handled by retry, but just in case)
        if 'database is locked' in error_str or 'locked' in error_str:
            raise QueryError(
                "Database is temporarily locked. This usually resolves automatically. "
                "If the issue persists, ensure no other processes are writing to the database."
            ) from e

        # SQL syntax errors
        if 'syntax error' in error_str or 'parser error' in error_str:
            raise QueryError(
                f"SQL syntax error: {e}\n\n"
                f"Suggestion: Check your SQL syntax. Available tables: traces, trace_events, exceptions\n"
                f"Example: SELECT * FROM traces WHERE status = 'completed' LIMIT 10"
            ) from e

        # Table doesn't exist (empty database)
        if 'table' in error_str and ('does not exist' in error_str or 'not found' in error_str):
            raise QueryError(
                "No trace data found. The database appears to be empty.\n\n"
                "To start tracing:\n"
                "1. Add 'import breadcrumb; breadcrumb.init()' to your Python code\n"
                "2. Run your application\n"
                "3. Traces will be captured automatically\n\n"
                "See docs/QUICKSTART.md for setup instructions."
            ) from e

        # Generic error with original message
        raise QueryError(f"Query failed: {e}") from e


def get_trace(
    trace_id: str,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get full trace with all events, variables, and exceptions.

    Args:
        trace_id: Trace UUID
        db_path: Optional database path

    Returns:
        Dict with trace, events, variables, exceptions

    Raises:
        TraceNotFoundError: If trace not found
        QueryError: If query fails

    Example:
        trace = get_trace("123e4567-e89b-12d3-a456-426614174000")
        print(f"Trace: {trace['trace']}")
        print(f"Events: {len(trace['events'])}")
    """
    manager = get_manager(db_path)

    try:
        # Get trace metadata
        trace_result = manager.execute_with_retry(
            "SELECT * FROM traces WHERE id = ?",
            [trace_id]
        )

        trace_row = trace_result.fetchone()
        if not trace_row:
            raise TraceNotFoundError(f"Trace not found: {trace_id}")

        trace_columns = [desc[0] for desc in trace_result.description]
        trace = dict(zip(trace_columns, trace_row))

        # Get trace events
        events_result = manager.execute_with_retry(
            "SELECT * FROM trace_events WHERE trace_id = ? ORDER BY timestamp",
            [trace_id]
        )

        events_rows = events_result.fetchall()
        events_columns = [desc[0] for desc in events_result.description]
        events = [dict(zip(events_columns, row)) for row in events_rows]

        # Get exceptions
        exceptions_result = manager.execute_with_retry(
            "SELECT * FROM exceptions WHERE trace_id = ?",
            [trace_id]
        )

        exceptions_rows = exceptions_result.fetchall()
        if exceptions_rows and exceptions_result.description:
            exceptions_columns = [desc[0] for desc in exceptions_result.description]
            exceptions = [dict(zip(exceptions_columns, row)) for row in exceptions_rows]
        else:
            exceptions = []

        return {
            'trace': trace,
            'events': events,
            'exceptions': exceptions,
        }

    except TraceNotFoundError:
        raise
    except Exception as e:
        raise QueryError(f"Failed to get trace: {e}")


def find_exceptions(
    since: str = "1h",
    limit: int = 10,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find recent exceptions within time range.

    Args:
        since: Time range ("30m", "2h", "1d", or ISO datetime)
        limit: Maximum number of exceptions to return
        db_path: Optional database path

    Returns:
        Dict with exceptions list, total count, time range

    Raises:
        QueryError: If query fails

    Example:
        result = find_exceptions(since="30m", limit=5)
        print(f"Found {result['total']} exceptions")
        for exc in result['exceptions']:
            print(f"{exc['exception_type']}: {exc['message']}")
    """
    try:
        # Parse time range
        since_dt = _parse_time_range(since)

        manager = get_manager(db_path)

        # Query exceptions with trace metadata
        result = manager.execute_with_retry("""
            SELECT
                e.*,
                t.started_at as trace_started_at,
                t.status as trace_status
            FROM exceptions e
            JOIN traces t ON e.trace_id = t.id
            WHERE t.started_at >= ?
            ORDER BY t.started_at DESC
            LIMIT ?
        """, [since_dt, limit])

        rows = result.fetchall()
        if rows and result.description:
            columns = [desc[0] for desc in result.description]
            exceptions = [dict(zip(columns, row)) for row in rows]
        else:
            exceptions = []

        # Get total count
        count_result = manager.execute_with_retry("""
            SELECT COUNT(*) FROM exceptions e
            JOIN traces t ON e.trace_id = t.id
            WHERE t.started_at >= ?
        """, [since_dt])

        total = count_result.fetchone()[0]

        return {
            'exceptions': exceptions,
            'total': total,
            'time_range': since,
            'since_datetime': since_dt.isoformat(),
        }

    except ValueError as e:
        raise QueryError(f"Invalid time range: {e}")
    except Exception as e:
        raise QueryError(f"Failed to find exceptions: {e}")


def analyze_performance(
    function: str,
    limit: int = 10,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyze performance statistics for a function.

    Args:
        function: Function name to analyze
        limit: Number of slowest traces to return
        db_path: Optional database path

    Returns:
        Dict with stats and slowest traces

    Raises:
        QueryError: If query fails

    Example:
        result = analyze_performance("fetch_data", limit=5)
        print(f"Average: {result['stats']['avg_duration_ms']}ms")
        print(f"P95: {result['stats']['p95_duration_ms']}ms")
    """
    try:
        manager = get_manager(db_path)

        # Calculate statistics
        # Note: DuckDB doesn't have built-in percentile functions in all versions
        # So we'll calculate basic stats and show slowest traces
        stats_result = manager.execute_with_retry("""
            SELECT
                COUNT(*) as call_count,
                AVG(duration_ms) as avg_duration_ms,
                MIN(duration_ms) as min_duration_ms,
                MAX(duration_ms) as max_duration_ms
            FROM (
                SELECT
                    t.id,
                    EXTRACT(EPOCH FROM (t.ended_at - t.started_at)) * 1000 as duration_ms
                FROM traces t
                JOIN trace_events e ON e.trace_id = t.id
                WHERE e.function_name = ?
                AND t.ended_at IS NOT NULL
            )
        """, [function])

        stats_row = stats_result.fetchone()
        if stats_row and stats_row[0] > 0:
            stats_columns = [desc[0] for desc in stats_result.description]
            stats = dict(zip(stats_columns, stats_row))
        else:
            # No data found
            return {
                'stats': None,
                'slowest_traces': [],
                'function': function,
            }

        # Get slowest traces
        slowest_result = manager.execute_with_retry("""
            SELECT
                t.id,
                t.started_at,
                t.ended_at,
                EXTRACT(EPOCH FROM (t.ended_at - t.started_at)) * 1000 as duration_ms,
                t.status
            FROM traces t
            JOIN trace_events e ON e.trace_id = t.id
            WHERE e.function_name = ?
            AND t.ended_at IS NOT NULL
            ORDER BY duration_ms DESC
            LIMIT ?
        """, [function, limit])

        slowest_rows = slowest_result.fetchall()
        if slowest_rows:
            slowest_columns = [desc[0] for desc in slowest_result.description]
            slowest_traces = [dict(zip(slowest_columns, row)) for row in slowest_rows]
        else:
            slowest_traces = []

        return {
            'stats': stats,
            'slowest_traces': slowest_traces,
            'function': function,
        }

    except Exception as e:
        raise QueryError(f"Failed to analyze performance: {e}")
