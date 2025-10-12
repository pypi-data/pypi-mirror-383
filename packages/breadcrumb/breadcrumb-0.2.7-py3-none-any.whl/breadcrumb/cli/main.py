"""
Breadcrumb CLI - Command-line interface for AI-native Python execution tracer.

Provides commands for querying traces, analyzing performance, finding exceptions,
and serving the MCP server.
"""

import sys
from typing import Optional, List
from pathlib import Path

import typer
from typing_extensions import Annotated

from breadcrumb import __version__


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


# Create main Typer app
app = typer.Typer(
    name="breadcrumb",
    help="AI-native Python execution tracer with MCP integration",
    add_completion=False,
    no_args_is_help=True,
)


# Global options state (using callback to capture before command execution)
class GlobalState:
    """Global state for CLI options."""
    format: str = "json"
    db_path: Optional[str] = None
    verbose: bool = False


state = GlobalState()


def version_callback(value: bool):
    """Callback for --version flag."""
    if value:
        typer.echo(f"breadcrumb {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    ctx: typer.Context,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: json (default, for AI agents) or table (for humans)",
        ),
    ] = "json",
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Path to traces.duckdb database (auto-discovered if not specified)",
        ),
    ] = None,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose output with debug information",
        ),
    ] = False,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
):
    """
    Breadcrumb - AI-native Python execution tracer.

    Query traces, analyze performance, find exceptions, and more.
    Optimized for AI agents (JSON output by default) with human-friendly options.
    """
    # Validate format
    if format not in ["json", "table"]:
        typer.echo(f"Error: Invalid format '{format}'. Must be 'json' or 'table'.", err=True)
        raise typer.Exit(EXIT_ERROR)

    # Store global options in state
    state.format = format
    state.db_path = db_path
    state.verbose = verbose

    if verbose:
        typer.echo(f"Breadcrumb CLI v{__version__}", err=True)
        typer.echo(f"Format: {format}", err=True)
        if db_path:
            typer.echo(f"Database: {db_path}", err=True)
        else:
            typer.echo("Database: auto-discover", err=True)


@app.command()
def query(
    sql: Annotated[
        Optional[str],
        typer.Argument(help="SQL SELECT query to execute (optional if using smart queries)"),
    ] = None,
    gaps: Annotated[
        bool,
        typer.Option(
            "--gaps",
            help="Show untraced function calls (gaps in coverage)",
        ),
    ] = False,
    call: Annotated[
        Optional[str],
        typer.Option(
            "--call",
            help="Show details for function calls (args, returns, duration)",
        ),
    ] = None,
    flow: Annotated[
        bool,
        typer.Option(
            "--flow",
            help="Show chronological execution flow",
        ),
    ] = False,
    module: Annotated[
        Optional[str],
        typer.Option(
            "--module",
            help="Filter flow by module name",
        ),
    ] = None,
    config: Annotated[
        Optional[str],
        typer.Option(
            "--config",
            "-c",
            help="Named configuration profile to use (e.g., 'pizza', 'flock')",
        ),
    ] = None,
):
    """
    Execute queries against trace database (SQL or smart queries).

    Smart queries provide semantic commands for common analysis tasks without SQL.
    Traditional SQL queries are still supported for advanced use cases.

    \b
    Smart Query Examples:
        breadcrumb query --gaps                    # Show untraced calls
        breadcrumb query --call Pizza              # Show Pizza function details
        breadcrumb query --flow                    # Show execution timeline
        breadcrumb query --flow --module flock     # Show flock module execution

    \b
    SQL Query Examples:
        breadcrumb query "SELECT * FROM traces LIMIT 10"
        breadcrumb query -c pizza "SELECT * FROM trace_events WHERE function_name='Pizza'"
        breadcrumb query "SELECT * FROM exceptions WHERE exception_type='ValueError'"
    """
    from breadcrumb.cli.commands.query import execute_query
    from breadcrumb.cli.commands.smart_query import execute_smart_query
    from breadcrumb.cli.commands.config import load_config

    # Load config file if specified to get database path
    effective_db_path = state.db_path
    if config:
        try:
            config_values = load_config(config)
            # Use config's db_path if not overridden by global --db-path
            if state.db_path is None and 'db_path' in config_values:
                effective_db_path = config_values['db_path']
        except FileNotFoundError as e:
            typer.echo(f"Error: {e}", err=True)
            typer.echo(f"Use 'breadcrumb config create {config}' to create it", err=True)
            raise typer.Exit(EXIT_ERROR)

    # Determine query type: smart query or SQL
    is_smart_query = gaps or call is not None or flow

    if is_smart_query:
        # Route to smart query handler
        exit_code = execute_smart_query(
            gaps=gaps,
            call=call,
            flow=flow,
            module=module,
            sql=sql,
            format=state.format,
            db_path=effective_db_path,
            verbose=state.verbose,
            config=config
        )
    elif sql:
        # Route to traditional SQL query handler
        exit_code = execute_query(
            sql=sql,
            format=state.format,
            db_path=effective_db_path,
            verbose=state.verbose
        )
    else:
        # No query specified
        typer.echo("Error: No query specified. Provide SQL query or use smart query options (--gaps, --call, --flow).", err=True)
        typer.echo("\nExamples:", err=True)
        typer.echo("  breadcrumb query --gaps", err=True)
        typer.echo("  breadcrumb query --call Pizza", err=True)
        typer.echo('  breadcrumb query "SELECT * FROM traces LIMIT 10"', err=True)
        raise typer.Exit(EXIT_ERROR)

    raise typer.Exit(exit_code)


@app.command()
def list(
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            help="Number of traces to show",
        ),
    ] = 10,
):
    """
    List recent traces.

    Shows the most recent traces with basic metadata (ID, status, timestamp).

    \b
    Examples:
        breadcrumb list
        breadcrumb list --limit 20
        breadcrumb list --format table
    """
    from breadcrumb.cli.commands.list import execute_list

    exit_code = execute_list(
        limit=limit,
        format=state.format,
        db_path=state.db_path,
        verbose=state.verbose
    )
    raise typer.Exit(exit_code)


@app.command()
def get(
    trace_id: Annotated[
        str,
        typer.Argument(help="Trace UUID to retrieve"),
    ],
):
    """
    Get detailed trace by ID.

    Retrieves complete trace with all events, variables, and exceptions.

    \b
    Examples:
        breadcrumb get 123e4567-e89b-12d3-a456-426614174000
        breadcrumb get 123e4567-e89b-12d3-a456-426614174000 --format table
    """
    from breadcrumb.cli.commands.get import execute_get

    exit_code = execute_get(
        trace_id=trace_id,
        format=state.format,
        db_path=state.db_path,
        verbose=state.verbose
    )
    raise typer.Exit(exit_code)


@app.command()
def exceptions(
    since: Annotated[
        str,
        typer.Option(
            "--since",
            "-s",
            help="Time range: relative (30m, 2h, 1d) or absolute (2025-01-10)",
        ),
    ] = "1h",
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            help="Maximum number of exceptions to show",
        ),
    ] = 10,
):
    """
    Find recent exceptions.

    Search for exceptions within a time range. Useful for debugging failures.

    \b
    Examples:
        breadcrumb exceptions
        breadcrumb exceptions --since 30m --limit 5
        breadcrumb exceptions --since 2025-01-10
    """
    from breadcrumb.cli.commands.exceptions import execute_exceptions

    exit_code = execute_exceptions(
        since=since,
        limit=limit,
        format=state.format,
        db_path=state.db_path,
        verbose=state.verbose
    )
    raise typer.Exit(exit_code)


@app.command()
def performance(
    function: Annotated[
        str,
        typer.Argument(help="Function name to analyze"),
    ],
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-n",
            help="Number of slowest traces to show",
        ),
    ] = 10,
):
    """
    Analyze performance statistics for a function.

    Shows avg/min/max execution time and slowest traces.

    \b
    Examples:
        breadcrumb performance fetch_data
        breadcrumb performance process_payment --limit 5
        breadcrumb performance my_function --format table
    """
    from breadcrumb.cli.commands.performance import execute_performance

    exit_code = execute_performance(
        function=function,
        limit=limit,
        format=state.format,
        db_path=state.db_path,
        verbose=state.verbose
    )
    raise typer.Exit(exit_code)


@app.command()
def serve_mcp(
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Path to traces.duckdb database (overrides global --db-path)",
        ),
    ] = None,
    port: Annotated[
        Optional[int],
        typer.Option(
            "--port",
            help="Port for TCP transport (future feature, currently stdio only)",
        ),
    ] = None,
):
    """
    Start MCP server for AI agents.

    Launches the Model Context Protocol server on stdio transport.
    Use this with Claude Desktop or other MCP clients.

    \b
    Examples:
        breadcrumb serve-mcp
        breadcrumb serve-mcp --db-path /path/to/traces.duckdb
    """
    from breadcrumb.cli.commands.serve_mcp import execute_serve_mcp

    # Use command-specific db_path if provided, otherwise fall back to global
    effective_db_path = db_path or state.db_path

    exit_code = execute_serve_mcp(
        db_path=effective_db_path,
        port=port,
        verbose=state.verbose
    )
    raise typer.Exit(exit_code)


# Create config subcommand group
config_app = typer.Typer(
    name="config",
    help="Manage configuration profiles",
    no_args_is_help=True,
)
app.add_typer(config_app, name="config")


@config_app.command("create")
def config_create_cmd(
    name: Annotated[
        str,
        typer.Argument(help="Name of the configuration profile (e.g., 'flock', 'production')"),
    ],
    include: Annotated[
        Optional[List[str]],
        typer.Option(
            "--include",
            "-i",
            help="Module patterns to include (e.g., 'flock.*'). Can be specified multiple times.",
        ),
    ] = None,
    sample_rate: Annotated[
        Optional[float],
        typer.Option("--sample-rate", help="Sampling rate 0.0-1.0"),
    ] = None,
    db_path: Annotated[
        Optional[str],
        typer.Option("--db-path", help="Database path"),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing config"),
    ] = False,
):
    """
    Create a new configuration profile (AI-FIRST: include-only workflow).

    \b
    Examples:
        breadcrumb config create flock --include "flock.*"
        breadcrumb config create production --sample-rate 0.1
        breadcrumb config create debug
    """
    from breadcrumb.cli.commands.config import config_create

    config_create(
        name=name,
        include=include,
        sample_rate=sample_rate,
        db_path=db_path,
        force=force,
    )


@config_app.command("show")
def config_show_cmd(
    name: Annotated[
        str,
        typer.Argument(help="Name of the configuration profile to show"),
    ],
):
    """
    Show a configuration profile.

    \b
    Examples:
        breadcrumb config show flock
        breadcrumb config show default
    """
    from breadcrumb.cli.commands.config import config_show

    config_show(name)


@config_app.command("list")
def config_list_cmd():
    """
    List all configuration profiles.

    \b
    Example:
        breadcrumb config list
    """
    from breadcrumb.cli.commands.config import config_list

    config_list()


@config_app.command("edit")
def config_edit_cmd(
    name: Annotated[
        str,
        typer.Argument(help="Name of the configuration profile to edit"),
    ],
    include: Annotated[
        Optional[List[str]],
        typer.Option("--include", help="Replace include patterns (replaces entire list)"),
    ] = None,
    add_include: Annotated[
        Optional[List[str]],
        typer.Option("--add-include", help="Add pattern to include list"),
    ] = None,
    remove_include: Annotated[
        Optional[List[str]],
        typer.Option("--remove-include", help="Remove pattern from include list"),
    ] = None,
    sample_rate: Annotated[
        Optional[float],
        typer.Option("--sample-rate", help="Set sampling rate"),
    ] = None,
    db_path: Annotated[
        Optional[str],
        typer.Option("--db-path", help="Set database path"),
    ] = None,
    enabled: Annotated[
        Optional[bool],
        typer.Option("--enabled/--disabled", help="Enable/disable tracing"),
    ] = None,
):
    """
    Edit a configuration profile (AI-FIRST: include-only workflow).

    \b
    Examples:
        breadcrumb config edit flock --add-include "flock.agents.*"
        breadcrumb config edit production --sample-rate 0.5
        breadcrumb config edit debug --enabled
    """
    from breadcrumb.cli.commands.config import config_edit

    config_edit(
        name=name,
        include=include,
        add_include=add_include,
        remove_include=remove_include,
        sample_rate=sample_rate,
        db_path=db_path,
        enabled=enabled,
    )


@config_app.command("delete")
def config_delete_cmd(
    name: Annotated[
        str,
        typer.Argument(help="Name of the configuration profile to delete"),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation prompt"),
    ] = False,
):
    """
    Delete a configuration profile.

    \b
    Examples:
        breadcrumb config delete flock
        breadcrumb config delete old-config --force
    """
    from breadcrumb.cli.commands.config import config_delete

    config_delete(name, force=force)


@config_app.command("validate")
def config_validate_cmd(
    name: Annotated[
        str,
        typer.Argument(help="Name of the configuration profile to validate"),
    ],
):
    """
    Validate a configuration profile and test pattern matching.

    Shows what values would be loaded, tests pattern matching against
    common modules, and provides helpful warnings.

    \b
    Examples:
        breadcrumb config validate pizza
        breadcrumb config validate flock
    """
    from breadcrumb.cli.commands.config import config_validate

    config_validate(name)


@app.command()
def report(
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Path to traces database (default: ~/.breadcrumb/traces.duckdb)",
        ),
    ] = None,
):
    """
    Generate execution report from most recent trace.

    Shows KPIs and call tree (if events < 100) for the most recent trace
    in the database. Useful for analyzing previous runs.

    \b
    Examples:
        breadcrumb report
        breadcrumb report --db-path /path/to/traces.duckdb
    """
    from breadcrumb.cli.commands.run import _generate_run_report

    # Use command-specific db_path if provided, otherwise fall back to global
    effective_db_path = db_path or state.db_path

    _generate_run_report(effective_db_path)
    raise typer.Exit(EXIT_SUCCESS)


@app.command()
def top(
    limit: Annotated[
        int,
        typer.Argument(help="Number of top functions to show"),
    ] = 10,
    skip: Annotated[
        int,
        typer.Option(
            "--skip",
            "-s",
            help="Skip first N functions",
        ),
    ] = 0,
    trace_id: Annotated[
        Optional[str],
        typer.Option(
            "--trace",
            "-t",
            help="Specific trace ID to query (default: most recent)",
        ),
    ] = None,
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Path to traces database (default: ~/.breadcrumb/traces.duckdb)",
        ),
    ] = None,
):
    """
    Show most frequently called functions (critical debugging tool).

    This is an ESSENTIAL feature for iterative debugging and config optimization!
    Use it to identify which functions dominate your traces.

    After running your script, check the top called functions:
      $ breadcrumb top 10

    You might see flock.logging is called 500 times. Ask yourself:
    "Is this important for debugging? Probably not! Focus on application code instead."

    Start with minimal tracing (['__main__']) and expand based on --gaps analysis.

    Re-run with optimized config to focus on relevant code.

    \b
    Examples:
        # Show top 10 from most recent trace
        breadcrumb top 10

        # Show top 20
        breadcrumb top 20

        # Skip first 5, show next 20 (positions 6-26)
        breadcrumb top 20 --skip 5

        # Analyze specific trace
        breadcrumb top 15 --trace abc123
    """
    from breadcrumb.cli.commands.top import top_command

    # Use command-specific db_path if provided, otherwise fall back to global
    effective_db_path = db_path or state.db_path

    top_command(
        limit=limit,
        skip=skip,
        trace_id=trace_id,
        db_path=effective_db_path,
    )


@app.command()
def init(
    project_name: Annotated[
        str,
        typer.Argument(help="Project name for this configuration (e.g., 'myproject', 'pizza-app')"),
    ],
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Custom database path (default: ~/.breadcrumb/PROJECT_NAME-traces.duckdb)",
        ),
    ] = None,
):
    """
    Initialize breadcrumb for a project (AI-FIRST workflow).

    Creates a named configuration in ~/.breadcrumb/PROJECT_NAME.yaml with sensible defaults.
    After init, all commands require -c PROJECT_NAME for explicit context.

    This is AI-FIRST design: explicit > implicit!
    - Humans: "Ugh, typing -c every time?"
    - AI Agents: "Perfect! No ambiguity, no context confusion!"

    \b
    Examples:
        breadcrumb init myproject
        breadcrumb init pizza-app --db-path ~/traces/pizza.duckdb

    \b
    After init, use with -c:
        breadcrumb run -c myproject --timeout 60 python script.py
        breadcrumb query -c myproject --gaps
        breadcrumb config edit myproject --add-include 'mymodule.*'
    """
    from breadcrumb.cli.commands.config import config_create, _get_config_path
    import os

    # Auto-generate db_path if not provided: ~/.breadcrumb/PROJECT_NAME-traces.duckdb
    if db_path is None:
        db_path = os.path.expanduser(f"~/.breadcrumb/{project_name}-traces.duckdb")

    # Create config with sensible defaults
    config_create(
        name=project_name,
        include=["__main__"],  # Start with just __main__, expand iteratively with --gaps
        sample_rate=1.0,
        db_path=db_path,
        force=False,
    )

    config_path = _get_config_path(project_name)
    typer.echo(f"\n✅ Project '{project_name}' initialized!")
    typer.echo(f"   Config: {config_path}")
    typer.echo(f"   Database: {db_path}")
    typer.echo(f"\n💡 AI-FIRST Workflow (always use -c {project_name}):")
    typer.echo(f"   1. Run with tracing:  breadcrumb run -c {project_name} --timeout 60 python script.py")
    typer.echo(f"   2. Find gaps:         breadcrumb query -c {project_name} --gaps")
    typer.echo(f"   3. Expand coverage:   breadcrumb config edit {project_name} --add-include 'mymodule.*'")
    typer.echo(f"   4. Re-run refined:    breadcrumb run -c {project_name} --timeout 60 python script.py")


@app.command()
def clear(
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Path to traces database (default: ~/.breadcrumb/traces.duckdb)",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation prompt",
        ),
    ] = False,
):
    """
    Clear trace database (delete all traces).

    Deletes the entire trace database file. This action cannot be undone.

    \b
    Examples:
        breadcrumb clear
        breadcrumb clear --force
        breadcrumb clear --db-path /path/to/traces.duckdb
    """
    import os
    from pathlib import Path

    # Determine database path
    if db_path is None:
        db_path = os.path.expanduser("~/.breadcrumb/traces.duckdb")
    else:
        db_path = os.path.expanduser(db_path)

    db_file = Path(db_path)

    # Check if database exists
    if not db_file.exists():
        typer.echo(f"Database not found: {db_path}")
        typer.echo("Nothing to clear.")
        raise typer.Exit(EXIT_SUCCESS)

    # Confirm deletion unless --force
    if not force:
        confirm = typer.confirm(
            f"Delete trace database at {db_path}?\nThis will permanently delete all traces.",
            default=False,
        )
        if not confirm:
            typer.echo("Cancelled.")
            raise typer.Exit(EXIT_SUCCESS)

    # Delete database file
    try:
        db_file.unlink()
        typer.echo(f"Deleted: {db_path}")
        typer.echo("All traces cleared.")
        raise typer.Exit(EXIT_SUCCESS)
    except Exception as e:
        typer.echo(f"Error deleting database: {e}", err=True)
        raise typer.Exit(EXIT_ERROR)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def run(
    ctx: typer.Context,
    timeout: Annotated[
        int,
        typer.Option(
            "--timeout",
            "-t",
            help="Maximum execution time in seconds (required for safety)",
        ),
    ],
    config: Annotated[
        str,
        typer.Option(
            "--config",
            "-c",
            help="Named configuration profile to use (REQUIRED for AI-first workflow)",
        ),
    ],
    include: Annotated[
        Optional[List[str]],
        typer.Option(
            "--include",
            "-i",
            help="Module patterns to include (e.g., 'myapp.*'). Can be specified multiple times.",
        ),
    ] = None,
    db_path: Annotated[
        Optional[str],
        typer.Option(
            "--db-path",
            help="Path to traces database (default: ~/.breadcrumb/traces.duckdb)",
        ),
    ] = None,
    sample_rate: Annotated[
        Optional[float],
        typer.Option(
            "--sample-rate",
            help="Sampling rate 0.0-1.0 (default: 1.0)",
        ),
    ] = None,
    silent: Annotated[
        bool,
        typer.Option(
            "--silent",
            help="Suppress breadcrumb initialization message",
        ),
    ] = False,
):
    """
    Run command with automatic breadcrumb tracing (AI-FIRST workflow).

    REQUIRES -c PROJECT: Explicit configuration for zero ambiguity!
    This is AI-FIRST design - typing -c is trivial for AI agents but eliminates
    all context confusion. Perfect for AI workflows!

    This injects breadcrumb.init() before your code runs, so you don't need
    to modify your source files.

    \b
    AI-FIRST Iterative Workflow:
        1. breadcrumb init myproject                           # One-time setup
        2. breadcrumb run -c myproject -t 60 python app.py     # Run with tracing
        3. breadcrumb query -c myproject --gaps                # Find untraced calls
        4. breadcrumb config edit myproject --add-include 'x'  # Expand coverage
        5. breadcrumb run -c myproject -t 60 python app.py     # Re-run refined!

    \b
    Examples:
        breadcrumb run -c myproject --timeout 60 python main.py
        breadcrumb run -c flock -t 120 uv run my_app.py
        breadcrumb run -c pizza -t 300 pytest tests/

    \b
    Override config settings:
        breadcrumb run -c myproject -t 60 --include "myapp.*" python app.py
        breadcrumb run -c myproject -t 60 --include "myapp.*" --include "flock.*" python app.py
    """
    from breadcrumb.cli.commands.run import run_command
    from breadcrumb.cli.commands.config import load_config

    # Get the command from extra args (everything after 'run' and its options)
    command = ctx.args

    if not command:
        typer.echo("Error: No command specified to run", err=True)
        typer.echo("\nUsage: breadcrumb run [OPTIONS] COMMAND...", err=True)
        typer.echo("\nExamples:", err=True)
        typer.echo("  breadcrumb run --timeout 60 python main.py", err=True)
        typer.echo("  breadcrumb run -c flock --timeout 30 python main.py", err=True)
        raise typer.Exit(EXIT_ERROR)

    # Load config file (REQUIRED for AI-first workflow)
    try:
        from breadcrumb.cli.commands.config import _get_config_path
        config_values = load_config(config)
        config_file_path = _get_config_path(config)
        if not silent:
            typer.echo(f"Using config profile: {config}", err=True)
    except FileNotFoundError as e:
        typer.echo(f"Error: Config '{config}' not found", err=True)
        typer.echo(f"Create it first: breadcrumb init {config}", err=True)
        raise typer.Exit(EXIT_ERROR)

    # Merge config file with command-line options (CLI takes precedence)
    # Config file values are used as defaults
    final_include = include if include is not None else config_values.get('include')
    final_db_path = db_path if db_path is not None else config_values.get('db_path')
    final_sample_rate = sample_rate if sample_rate is not None else config_values.get('sample_rate')

    # Call the run command implementation
    run_command(
        command=command,
        timeout=timeout,
        include=final_include,
        db_path=final_db_path,
        sample_rate=final_sample_rate,
        silent=silent,
        config_file=config_file_path,
    )


def cli():
    """Entry point for the CLI."""
    try:
        app()
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        if state.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(EXIT_ERROR)


if __name__ == "__main__":
    cli()
