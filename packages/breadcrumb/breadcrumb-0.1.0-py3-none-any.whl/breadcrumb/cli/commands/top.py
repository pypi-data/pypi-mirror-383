"""
Breadcrumb top command - show most frequently called functions.

This command is essential for iterative debugging and config optimization.
By identifying the most called functions, you can decide which modules
to exclude from tracing to reduce noise and focus on relevant code.

Example workflow:
  1. Run: breadcrumb run --timeout 30 python app.py
  2. Check: breadcrumb top 10
  3. Notice: flock.logging._serialize_value called 500 times
  4. Decide: "This is internal logging, not relevant for debugging"
  5. Optimize: breadcrumb config edit myconfig --add-exclude "flock.logging*"
  6. Re-run: breadcrumb run -c myconfig --timeout 30 python app.py
"""

import os
import sys
import typer
from pathlib import Path
from typing import Optional


def top_command(
    limit: int = typer.Argument(10, help="Number of top functions to show"),
    skip: int = typer.Option(0, "--skip", "-s", help="Skip first N functions"),
    trace_id: Optional[str] = typer.Option(
        None,
        "--trace",
        "-t",
        help="Specific trace ID to query (default: most recent)"
    ),
    db_path: Optional[str] = typer.Option(
        None,
        "--db-path",
        help="Path to traces database (default: ~/.breadcrumb/traces.duckdb)"
    ),
) -> None:
    """
    Show the most frequently called functions from traces.

    This is a critical debugging tool for optimizing your trace configuration.
    Use it to identify noisy functions that should be excluded from tracing.

    Examples:

        # Show top 10 most called functions from last trace
        breadcrumb top 10

        # Show top 20
        breadcrumb top 20

        # Skip first 5, show next 20 (positions 6-26)
        breadcrumb top 20 --skip 5

        # Analyze a specific trace
        breadcrumb top 15 --trace abc123def456

    Debugging workflow:

        After running your script, use this command to see what's getting called:

        $ breadcrumb top 10

        You might see:
          1. flock.logging._serialize_value: 500 calls
          2. flock.logging.get_logger: 200 calls
          3. myapp.process_item: 50 calls

        Then you can decide: "Hmm, flock.logging is getting invoked very often.
        Is this important for debugging? Probably not! Let's exclude it!"

        $ breadcrumb config edit myconfig --add-exclude "flock.logging*"

        Re-run with the optimized config to focus on your actual application code.
    """
    try:
        from breadcrumb.storage.connection import get_manager

        # Discover database path if not provided
        if db_path is None:
            db_path = os.path.expanduser("~/.breadcrumb/traces.duckdb")

        db_file = Path(db_path)
        if not db_file.exists():
            typer.echo(f"Error: No trace database found at {db_path}", err=True)
            typer.echo("Run a script with 'breadcrumb run' first to generate traces.", err=True)
            raise typer.Exit(1)

        manager = get_manager(str(db_path))

        with manager.get_connection_context() as conn:
            # Get trace ID to query
            target_trace_id = trace_id
            if target_trace_id is None:
                # Get most recent trace
                recent = conn.execute("""
                    SELECT id, started_at
                    FROM traces
                    ORDER BY started_at DESC
                    LIMIT 1
                """).fetchone()

                if not recent:
                    typer.echo("No traces found in database.", err=True)
                    typer.echo("Run a script with 'breadcrumb run' first.", err=True)
                    raise typer.Exit(1)

                target_trace_id, started_at = recent
                typer.echo(f"Analyzing most recent trace: {target_trace_id}")
                typer.echo(f"Started at: {started_at}")
            else:
                # Verify trace exists
                trace_exists = conn.execute("""
                    SELECT id FROM traces WHERE id = ?
                """, (target_trace_id,)).fetchone()

                if not trace_exists:
                    typer.echo(f"Error: Trace '{target_trace_id}' not found.", err=True)
                    raise typer.Exit(1)

                typer.echo(f"Analyzing trace: {target_trace_id}")

            # Query top functions with limit and offset
            top_functions = conn.execute("""
                SELECT module_name, function_name, COUNT(*) as call_count
                FROM trace_events
                WHERE trace_id = ? AND event_type = 'call'
                GROUP BY module_name, function_name
                ORDER BY call_count DESC
                LIMIT ? OFFSET ?
            """, (target_trace_id, limit, skip)).fetchall()

            if not top_functions:
                if skip > 0:
                    typer.echo(f"\nNo functions found (skipped {skip}).", err=True)
                else:
                    typer.echo("\nNo function calls found in this trace.", err=True)
                raise typer.Exit(0)

            # Get total count for context
            total_funcs = conn.execute("""
                SELECT COUNT(DISTINCT module_name || '.' || function_name)
                FROM trace_events
                WHERE trace_id = ? AND event_type = 'call'
            """, (target_trace_id,)).fetchone()[0]

            # Print results
            typer.echo("\n" + "=" * 70)
            if skip > 0:
                typer.echo(f"TOP {limit} MOST CALLED FUNCTIONS (skipping first {skip})")
                typer.echo(f"Showing positions {skip + 1}-{skip + len(top_functions)} of {total_funcs} unique functions")
            else:
                typer.echo(f"TOP {limit} MOST CALLED FUNCTIONS")
                typer.echo(f"Showing {len(top_functions)} of {total_funcs} unique functions")
            typer.echo("=" * 70)

            # Find max width for alignment
            max_func_width = max(
                len(f"{module}.{func}") for module, func, _ in top_functions
            )

            for i, (module, func, count) in enumerate(top_functions, start=skip + 1):
                func_name = f"{module}.{func}"
                typer.echo(f"{i:4d}. {func_name:<{max_func_width}} : {count:6d} calls")

            # Show helpful tips
            typer.echo("\n" + "=" * 70)
            typer.echo("DEBUGGING TIPS:")
            typer.echo("  - High call counts often indicate:")
            typer.echo("    * Internal framework/library code (consider excluding)")
            typer.echo("    * Logging/serialization utilities (usually safe to exclude)")
            typer.echo("    * Hot loops in your application (keep these!)")
            typer.echo()
            typer.echo("  - To exclude noisy modules:")
            typer.echo(f"    breadcrumb config edit <name> --add-exclude '<pattern>'")
            typer.echo()
            typer.echo("  - Example patterns to exclude:")

            # Suggest patterns based on actual data
            suggested_excludes = set()
            for module, func, count in top_functions[:5]:  # Look at top 5
                # Suggest excluding if it's clearly infrastructure
                if any(keyword in module.lower() for keyword in ['logging', 'telemetry', 'webhook', 'serialize']):
                    suggested_excludes.add(f"'{module.split('.')[0]}.*'")

            if suggested_excludes:
                for pattern in suggested_excludes:
                    typer.echo(f"    --add-exclude {pattern}")

            typer.echo("=" * 70 + "\n")

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)
