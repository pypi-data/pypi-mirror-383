"""
CLI command: get - Get detailed trace by ID.

Retrieves complete trace data including metadata, events, variables, and exceptions.
Displays the trace in either JSON or table format.
"""

from typing import Optional
import sys

from breadcrumb.storage.query import get_trace, TraceNotFoundError, QueryError
from breadcrumb.cli.formatters import format_json, format_table, format_error


# Exit codes
EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_NO_RESULTS = 2


def execute_get(
    trace_id: str,
    format: str = "json",
    db_path: Optional[str] = None,
    verbose: bool = False
) -> int:
    """
    Execute the get command.

    Args:
        trace_id: UUID of the trace to retrieve
        format: Output format ("json" or "table")
        db_path: Optional path to database
        verbose: Enable verbose output

    Returns:
        Exit code (0=success, 1=error, 2=trace not found)

    Example:
        exit_code = execute_get("123e4567-e89b-12d3-a456-426614174000", format="table")
    """
    if verbose:
        print(f"Retrieving trace: {trace_id}...", file=sys.stderr)

    try:
        # Get the trace with all events and exceptions
        trace_data = get_trace(trace_id, db_path=db_path)

        if verbose:
            print(f"Found trace with {len(trace_data['events'])} events and {len(trace_data['exceptions'])} exceptions", file=sys.stderr)

        # Format output
        if format == "json":
            # JSON output - machine-readable for AI agents
            output = format_json({
                "trace": trace_data['trace'],
                "events": trace_data['events'],
                "exceptions": trace_data['exceptions'],
                "summary": {
                    "trace_id": trace_id,
                    "status": trace_data['trace']['status'],
                    "event_count": len(trace_data['events']),
                    "exception_count": len(trace_data['exceptions']),
                }
            })
        else:
            # Table output - human-readable
            lines = []

            # Trace metadata section
            lines.append("TRACE DETAILS")
            lines.append("=" * 60)
            lines.append("")

            trace = trace_data['trace']
            trace_info = {
                "ID": trace['id'],
                "Status": trace['status'],
                "Started At": trace['started_at'],
                "Ended At": trace['ended_at'] if trace['ended_at'] else "Running",
                "Parent ID": trace['parent_id'] if trace.get('parent_id') else "None",
            }

            # Add metadata if present
            if trace.get('metadata'):
                trace_info["Metadata"] = trace['metadata']

            lines.append(format_table(trace_info))
            lines.append("")

            # Events section
            lines.append("EVENTS")
            lines.append("=" * 60)
            lines.append("")

            if trace_data['events']:
                # Prepare simplified event list for table display
                events_display = []
                for event in trace_data['events']:
                    event_display = {
                        "Type": event['event_type'],
                        "Function": event.get('function_name', 'N/A'),
                        "Timestamp": event['timestamp'],
                    }

                    # Add file info if available
                    if event.get('file_path'):
                        event_display["Location"] = f"{event['file_path']}:{event.get('line_number', '?')}"

                    events_display.append(event_display)

                lines.append(format_table(events_display))
            else:
                lines.append("No events recorded")

            lines.append("")

            # Exceptions section
            lines.append("EXCEPTIONS")
            lines.append("=" * 60)
            lines.append("")

            if trace_data['exceptions']:
                # Prepare exception list for table display
                exceptions_display = []
                for exc in trace_data['exceptions']:
                    exc_display = {
                        "Type": exc['exception_type'],
                        "Message": exc['message'],
                        "Created At": exc.get('created_at', 'N/A'),
                    }

                    exceptions_display.append(exc_display)

                lines.append(format_table(exceptions_display))

                # Show full stack trace for first exception if available
                if trace_data['exceptions'][0].get('stack_trace'):
                    lines.append("")
                    lines.append("STACK TRACE (first exception)")
                    lines.append("-" * 60)
                    lines.append(trace_data['exceptions'][0]['stack_trace'])
            else:
                lines.append("No exceptions recorded")

            output = "\n".join(lines)

        print(output)
        return EXIT_SUCCESS

    except TraceNotFoundError as e:
        # Trace not found - use EXIT_NO_RESULTS
        error_output = format_error(
            error_type="TraceNotFoundError",
            message=str(e),
            suggestion="Use 'breadcrumb list' to find available trace IDs",
            format=format
        )
        print(error_output, file=sys.stderr)
        return EXIT_NO_RESULTS

    except QueryError as e:
        # Query-specific error
        error_output = format_error(
            error_type="QueryError",
            message=str(e),
            suggestion="Check that the database exists and is accessible",
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
