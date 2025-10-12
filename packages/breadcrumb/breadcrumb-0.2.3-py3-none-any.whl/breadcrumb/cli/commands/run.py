"""
Breadcrumb run command - execute scripts with automatic tracing injection.

This command allows running Python scripts with breadcrumb tracing enabled
without modifying the source code.
"""

import os
import sys
import subprocess
import tempfile
import time
import typer
from typing import List, Optional, Tuple
from pathlib import Path
from datetime import datetime


def _generate_timeout_report(timeout_seconds: int, db_path: Optional[str] = None) -> None:
    """
    Generate diagnostic report when command times out.

    Args:
        timeout_seconds: The timeout that was exceeded
        db_path: Optional database path to query for trace data
    """
    print("\n" + "=" * 60, file=sys.stderr)
    print("BREADCRUMB TIMEOUT REPORT", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print(f"\nCommand exceeded timeout of {timeout_seconds} seconds", file=sys.stderr)

    # Try to get trace information from database
    try:
        from breadcrumb.storage.connection import get_manager
        from collections import Counter

        # Discover database path if not provided
        if db_path is None:
            db_path = os.path.expanduser("~/.breadcrumb/traces.duckdb")

        db_file = Path(db_path)
        if not db_file.exists():
            print("\nNo trace database found - unable to show execution details", file=sys.stderr)
            print("=" * 60 + "\n", file=sys.stderr)
            return

        manager = get_manager(str(db_path))

        with manager.get_connection_context() as conn:
            # Get most recent trace
            recent_trace = conn.execute("""
                SELECT id, started_at, thread_id
                FROM traces
                ORDER BY started_at DESC
                LIMIT 1
            """).fetchone()

            if not recent_trace:
                print("\nNo traces found in database", file=sys.stderr)
                print("=" * 60 + "\n", file=sys.stderr)
                return

            trace_id, started_at, thread_id = recent_trace
            print(f"\nMost Recent Trace: {trace_id}", file=sys.stderr)
            print(f"Started at: {started_at}", file=sys.stderr)
            print(f"Thread ID: {thread_id}", file=sys.stderr)

            # Get function call statistics
            function_stats = conn.execute("""
                SELECT module_name, function_name, COUNT(*) as call_count
                FROM trace_events
                WHERE trace_id = ? AND event_type = 'call'
                GROUP BY module_name, function_name
                ORDER BY call_count DESC
                LIMIT 20
            """, (trace_id,)).fetchall()

            if function_stats:
                print(f"\nTop 20 Functions Called Before Timeout:", file=sys.stderr)
                for module, func, count in function_stats:
                    print(f"  {module}.{func}: {count} calls", file=sys.stderr)

            # Get last few events before timeout
            last_events = conn.execute("""
                SELECT timestamp, event_type, module_name, function_name, file_path, line_number
                FROM trace_events
                WHERE trace_id = ?
                ORDER BY timestamp DESC
                LIMIT 10
            """, (trace_id,)).fetchall()

            if last_events:
                print(f"\nLast 10 Events Before Timeout (most recent first):", file=sys.stderr)
                for ts, event_type, module, func, file_path, line_no in last_events:
                    location = f"{file_path}:{line_no}" if file_path else "unknown"
                    print(f"  [{event_type}] {module}.{func} at {location}", file=sys.stderr)

            # Try to reconstruct call stack from events
            call_stack = conn.execute("""
                SELECT module_name, function_name, file_path, line_number
                FROM trace_events
                WHERE trace_id = ? AND event_type = 'call'
                AND timestamp > (
                    SELECT MAX(timestamp)
                    FROM trace_events
                    WHERE trace_id = ? AND event_type = 'return'
                )
                ORDER BY timestamp ASC
            """, (trace_id, trace_id)).fetchall()

            if call_stack:
                print(f"\nLikely Call Stack at Timeout ({len(call_stack)} frames):", file=sys.stderr)
                for i, (module, func, file_path, line_no) in enumerate(call_stack):
                    location = f"{file_path}:{line_no}" if file_path else "unknown"
                    print(f"  {i}: {module}.{func} at {location}", file=sys.stderr)

    except Exception as e:
        print(f"\nError generating timeout report: {e}", file=sys.stderr)

    print("\nRecommendations:", file=sys.stderr)
    print("  1. Increase timeout if script needs more time", file=sys.stderr)
    print("  2. Check if script is stuck in infinite loop", file=sys.stderr)
    print("  3. Use breadcrumb query to investigate trace events", file=sys.stderr)
    print("=" * 60 + "\n", file=sys.stderr)


def _generate_run_report(db_path: Optional[str] = None) -> None:
    """
    Generate execution report after successful run.

    Shows KPIs and call tree if events < 100.

    Args:
        db_path: Optional database path to query for trace data
    """
    try:
        from breadcrumb.storage.connection import get_manager

        # Discover database path if not provided
        if db_path is None:
            db_path = os.path.expanduser("~/.breadcrumb/traces.duckdb")

        db_file = Path(db_path)
        if not db_file.exists():
            return  # No traces captured, silent exit

        manager = get_manager(str(db_path))

        with manager.get_connection_context() as conn:
            # Get most recent trace
            recent_trace = conn.execute("""
                SELECT id, started_at, ended_at, status, thread_id
                FROM traces
                ORDER BY started_at DESC
                LIMIT 1
            """).fetchone()

            if not recent_trace:
                return  # No traces found

            trace_id, started_at, ended_at, status, thread_id = recent_trace

            # Count events
            event_counts = conn.execute("""
                SELECT event_type, COUNT(*) as count
                FROM trace_events
                WHERE trace_id = ?
                GROUP BY event_type
            """, (trace_id,)).fetchall()

            event_dict = {event_type: count for event_type, count in event_counts}
            total_events = sum(event_dict.values())

            # Count exceptions
            exception_count = conn.execute("""
                SELECT COUNT(*) FROM exceptions WHERE trace_id = ?
            """, (trace_id,)).fetchone()[0]

            # Calculate duration
            duration_ms = None
            if started_at and ended_at:
                # started_at and ended_at are already datetime objects from DuckDB
                duration_ms = (ended_at - started_at).total_seconds() * 1000

            # Print report header
            print("\n" + "=" * 60)
            print("BREADCRUMB RUN REPORT")
            print("=" * 60)

            # KPIs
            print(f"\nKey Metrics:")
            print(f"  Total Events: {total_events}")
            print(f"  - Calls: {event_dict.get('call', 0)}")
            print(f"  - Returns: {event_dict.get('return', 0)}")
            print(f"  - Exceptions: {event_dict.get('exception', 0)}")
            if duration_ms:
                print(f"  Duration: {duration_ms:.2f} ms")
            print(f"  Status: {status}")

            # Exception summary
            if exception_count > 0:
                print(f"\nExceptions Raised: {exception_count}")
                exceptions = conn.execute("""
                    SELECT exception_type, message
                    FROM exceptions
                    WHERE trace_id = ?
                    ORDER BY created_at
                """, (trace_id,)).fetchall()

                for exc_type, message in exceptions:
                    print(f"  - {exc_type}: {message}")

            # Call tree (only if events < 100)
            if total_events <= 100:
                print(f"\nCall Tree:")

                # Get all call and return events in order
                events = conn.execute("""
                    SELECT timestamp, event_type, module_name, function_name
                    FROM trace_events
                    WHERE trace_id = ? AND event_type IN ('call', 'return')
                    ORDER BY timestamp ASC
                """, (trace_id,)).fetchall()

                # Build call tree
                call_stack = []
                call_times = {}  # (module, func) -> start_time

                for timestamp, event_type, module_name, function_name in events:
                    key = (module_name, function_name)

                    if event_type == 'call':
                        # Push to stack
                        indent = "  " * len(call_stack)
                        call_stack.append(key)
                        # timestamp is already a datetime object from DuckDB
                        call_times[key] = timestamp

                        # Print call (using ASCII arrow instead of Unicode)
                        func_name = f"{module_name}.{function_name}"
                        print(f"{indent}-> {func_name}")

                    elif event_type == 'return':
                        # Pop from stack and calculate duration
                        if call_stack and call_stack[-1] == key:
                            call_stack.pop()

                            if key in call_times:
                                start_time = call_times[key]
                                # timestamp is already a datetime object from DuckDB
                                duration_ms = (timestamp - start_time).total_seconds() * 1000

                                indent = "  " * len(call_stack)
                                func_name = f"{module_name}.{function_name}"
                                print(f"{indent}<- {func_name} ({duration_ms:.2f}ms)")

                                del call_times[key]
            else:
                print(f"\nCall Tree:")
                print(f"  (Too many events: {total_events} > 100)")
                print(f"  Use 'breadcrumb query' to explore trace details")

                # Show top 10 most called functions
                top_functions = conn.execute("""
                    SELECT module_name, function_name, COUNT(*) as call_count
                    FROM trace_events
                    WHERE trace_id = ? AND event_type = 'call'
                    GROUP BY module_name, function_name
                    ORDER BY call_count DESC
                    LIMIT 10
                """, (trace_id,)).fetchall()

                if top_functions:
                    print(f"\n  Top 10 Most Called Functions:")
                    for module, func, count in top_functions:
                        print(f"    {module}.{func}: {count} calls")

                    print(f"\n  TIP: Use 'breadcrumb top 20' to see more!")
                    print(f"       Use 'breadcrumb top 20 --skip 10' to see positions 11-30")
                    print(f"       High call counts? Consider excluding with:")
                    print(f"       breadcrumb config edit <name> --add-exclude '<pattern>*'")

            print("\n" + "=" * 60 + "\n")

    except Exception as e:
        # Silently fail - don't interrupt user's workflow
        pass


def run_command(
    command: List[str] = typer.Argument(..., help="Command to run with tracing enabled"),
    timeout: int = typer.Option(
        ...,
        "--timeout",
        "-t",
        help="Maximum execution time in seconds (required for safety)"
    ),
    include: Optional[List[str]] = typer.Option(
        None,
        "--include",
        "-i",
        help="Module patterns to include (e.g., 'myapp.*'). Can be specified multiple times."
    ),
    exclude: Optional[List[str]] = typer.Option(
        None,
        "--exclude",
        "-e",
        help="Module patterns to exclude (e.g., 'flock.*'). Can be specified multiple times."
    ),
    db_path: Optional[str] = typer.Option(
        None,
        "--db-path",
        help="Path to traces database (default: ~/.breadcrumb/traces.duckdb)"
    ),
    sample_rate: Optional[float] = typer.Option(
        None,
        "--sample-rate",
        help="Sampling rate 0.0-1.0 (default: 1.0)"
    ),
    silent: bool = typer.Option(
        False,
        "--silent",
        help="Suppress breadcrumb initialization message"
    ),
    config_file: Optional[str] = None,
) -> None:
    """
    Run command with automatic breadcrumb tracing.

    This injects breadcrumb.init() before your code runs, so you don't need
    to modify your source files.

    Examples:

        # Run a script with tracing (60 second timeout)
        breadcrumb run --timeout 60 python main.py

        # Run with uv (2 minute timeout)
        breadcrumb run -t 120 uv run my_app.py

        # Exclude frameworks (30 second timeout)
        breadcrumb run -t 30 --exclude "flock.*" --exclude "pydantic.*" python main.py

        # Only trace your code (10 second timeout)
        breadcrumb run --timeout 10 --include "__main__" python script.py

        # Custom database path
        breadcrumb run -t 60 --db-path /tmp/traces.duckdb python main.py

        # Run tests with tracing (5 minute timeout)
        breadcrumb run -t 300 pytest tests/

        # Run with specific sample rate
        breadcrumb run -t 60 --sample-rate 0.1 python main.py
    """
    # Build breadcrumb.init() call with user's config
    init_args = []

    if include:
        # Convert to Python list literal
        include_str = "[" + ", ".join(f"'{p}'" for p in include) + "]"
        init_args.append(f"include={include_str}")

    if exclude:
        exclude_str = "[" + ", ".join(f"'{p}'" for p in exclude) + "]"
        init_args.append(f"exclude={exclude_str}")

    if db_path:
        init_args.append(f"db_path={repr(db_path)}")

    if sample_rate is not None:
        init_args.append(f"sample_rate={sample_rate}")

    if silent:
        init_args.append("silent=True")

    if config_file:
        init_args.append(f"config_file={repr(config_file)}")

    init_call = f"breadcrumb.init({', '.join(init_args)})" if init_args else "breadcrumb.init()"

    # Detect if this is a Python script invocation
    if len(command) >= 2 and command[0] in ('python', 'python3', 'python.exe', 'python3.exe'):
        # Find the script path (could be after flags like -u, -W, etc.)
        script_path = None
        script_index = None

        for i, arg in enumerate(command[1:], start=1):
            # Skip flags and their values
            if arg.startswith('-'):
                continue
            # This should be the script
            if arg.endswith('.py') or not arg.startswith('-'):
                script_path = arg
                script_index = i
                break

        if script_path and script_index:
            # Create a wrapper script that initializes breadcrumb then runs the target script
            wrapper_script = f"""# Auto-generated breadcrumb wrapper
import sys
import os

# Initialize breadcrumb FIRST (before modifying sys.path to avoid import collisions)
try:
    import breadcrumb
    {init_call}
except Exception as e:
    print(f"Warning: Failed to initialize breadcrumb: {{e}}", file=sys.stderr)

# Add script directory to path so user's imports work
script_path = {repr(os.path.abspath(script_path))}
script_dir = os.path.dirname(script_path)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Run the target script as __main__
import runpy
try:
    sys.argv = {repr(command[script_index:])}  # Set argv to script and its args
    runpy.run_path(script_path, run_name='__main__')
finally:
    # CRITICAL: Ensure all trace data is flushed to database before exit
    try:
        import breadcrumb
        breadcrumb.shutdown(timeout=5.0)
    except Exception:
        pass
"""

            # Write wrapper to temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                delete=False,
                suffix='.py',
                prefix='breadcrumb_wrapper_'
            ) as f:
                f.write(wrapper_script)
                wrapper_file = f.name

            # DEBUG: Print wrapper script (optional)
            if os.environ.get('BREADCRUMB_DEBUG'):
                typer.echo(f"=== Generated wrapper script at {wrapper_file} ===", err=True)
                typer.echo(wrapper_script, err=True)
                typer.echo("=" * 60, err=True)

            try:
                # Run Python with the wrapper script instead
                # Use sys.executable to ensure we use the same Python that has breadcrumb installed
                wrapper_command = [sys.executable] + command[1:script_index] + [wrapper_file]
                try:
                    result = subprocess.run(wrapper_command, timeout=timeout)
                    # Give writer thread time to flush (race condition workaround)
                    time.sleep(0.5)
                    _generate_run_report(db_path)  # Show run report on success
                    sys.exit(result.returncode)
                except subprocess.TimeoutExpired:
                    typer.echo(f"\nError: Command timed out after {timeout} seconds", err=True)
                    _generate_timeout_report(timeout, db_path)
                    sys.exit(124)  # Standard timeout exit code
            finally:
                # Cleanup wrapper script
                try:
                    os.unlink(wrapper_file)
                except Exception:
                    pass
        else:
            # Couldn't find script, fall through to original command
            typer.echo("Warning: Could not detect Python script to wrap. Running command as-is.", err=True)
            try:
                result = subprocess.run(command, timeout=timeout)
                sys.exit(result.returncode)
            except subprocess.TimeoutExpired:
                typer.echo(f"\nError: Command timed out after {timeout} seconds", err=True)
                _generate_timeout_report(timeout, db_path)
                sys.exit(124)  # Standard timeout exit code
    else:
        # Not a direct Python invocation - use environment variable approach
        # This works for tools like 'uv run', 'poetry run', etc.
        startup_script = f"""# Auto-generated breadcrumb startup
import sys
try:
    import breadcrumb
    {init_call}
except Exception as e:
    print(f"Warning: Failed to initialize breadcrumb: {{e}}", file=sys.stderr)
"""

        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='.py',
            prefix='breadcrumb_startup_'
        ) as f:
            f.write(startup_script)
            startup_file = f.name

        try:
            # Use PYTHONSTARTUP for non-direct Python invocations
            env = os.environ.copy()
            env['PYTHONSTARTUP'] = startup_file

            try:
                result = subprocess.run(command, env=env, timeout=timeout)
                sys.exit(result.returncode)
            except subprocess.TimeoutExpired:
                typer.echo(f"\nError: Command timed out after {timeout} seconds", err=True)
                _generate_timeout_report(timeout, db_path)
                sys.exit(124)  # Standard timeout exit code
        finally:
            try:
                os.unlink(startup_file)
            except Exception:
                pass
