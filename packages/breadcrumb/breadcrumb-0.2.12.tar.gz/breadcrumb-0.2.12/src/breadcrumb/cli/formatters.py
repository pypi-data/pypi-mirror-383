"""
Output formatters for CLI.

Provides JSON and table formatters for different output types:
- JSON: Machine-readable, for AI agents
- Table: Human-readable, for terminal display
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as JSON.

    Handles datetime objects and other non-JSON-serializable types.

    Args:
        data: Data to format (dict, list, or simple value)
        indent: JSON indentation level (default: 2 for readability)

    Returns:
        JSON string
    """
    def _default_serializer(obj):
        """Handle non-JSON-serializable objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    return json.dumps(data, indent=indent, default=_default_serializer)


def format_table(
    data: Any,
    title: Optional[str] = None,
    disable_truncation: bool = False
) -> str:
    """
    Format data as human-readable table.

    Supports:
    - List of dicts: Renders as table with columns
    - Single dict: Renders as key-value pairs
    - Simple values: Renders as-is

    Args:
        data: Data to format
        title: Optional table title

    Returns:
        Formatted table string
    """
    lines = []

    # Add title if provided
    if title:
        lines.append(title)
        lines.append("=" * len(title))
        lines.append("")

    # Handle different data types
    if isinstance(data, list):
        if not data:
            lines.append("No results")
            return "\n".join(lines)

        # List of dicts -> table
        if isinstance(data[0], dict):
            lines.extend(_format_dict_list_as_table(data, disable_truncation=disable_truncation))
        else:
            # List of simple values
            for item in data:
                lines.append(str(item))

    elif isinstance(data, dict):
        # Single dict -> key-value pairs
        lines.extend(_format_dict_as_key_value(data))

    else:
        # Simple value
        lines.append(str(data))

    return "\n".join(lines)


def _format_dict_list_as_table(
    data: List[Dict[str, Any]],
    disable_truncation: bool
) -> List[str]:
    """
    Format list of dicts as ASCII table.

    Args:
        data: List of dicts with same keys

    Returns:
        List of formatted lines
    """
    if not data:
        return ["No results"]

    lines = []

    # Get column names from first dict
    columns = list(data[0].keys())

    # Calculate column widths (limited unless truncation disabled)
    MAX_COL_WIDTH = None if disable_truncation else 50
    col_widths = {}
    for col in columns:
        # Max of column name and all values
        max_width = len(str(col))
        for row in data:
            value = row.get(col, "")
            value_str = "" if value is None else str(value)
            value_len = len(value_str)
            if MAX_COL_WIDTH is not None:
                value_len = min(value_len, MAX_COL_WIDTH)
            max_width = max(max_width, value_len)
        col_widths[col] = max_width

    # Header row
    header_parts = []
    for col in columns:
        header_parts.append(str(col).ljust(col_widths[col]))
    lines.append(" | ".join(header_parts))

    # Separator
    sep_parts = []
    for col in columns:
        sep_parts.append("-" * col_widths[col])
    lines.append("-+-".join(sep_parts))

    # Data rows
    for row in data:
        row_parts = []
        for col in columns:
            value = row.get(col, "")
            # Truncate long values unless disabled
            value_str = "" if value is None else str(value)
            if (not disable_truncation) and len(value_str) > col_widths[col]:
                cutoff = max(col_widths[col] - 3, 0)
                value_str = value_str[:cutoff] + "..."
            row_parts.append(value_str.ljust(col_widths[col]))
        lines.append(" | ".join(row_parts))

    # Footer with count
    lines.append("")
    lines.append(f"Total: {len(data)} rows")

    return lines


def _format_dict_as_key_value(data: Dict[str, Any]) -> List[str]:
    """
    Format dict as key-value pairs.

    Args:
        data: Dictionary to format

    Returns:
        List of formatted lines
    """
    if not data:
        return ["No data"]

    lines = []

    # Calculate max key width for alignment
    max_key_width = max(len(str(key)) for key in data.keys())

    for key, value in data.items():
        key_str = str(key).ljust(max_key_width)

        # Handle nested structures
        if isinstance(value, (dict, list)):
            value_str = format_json(value, indent=2)
            # Indent multi-line values
            value_lines = value_str.split("\n")
            lines.append(f"{key_str}: {value_lines[0]}")
            for line in value_lines[1:]:
                lines.append(f"{' ' * (max_key_width + 2)}{line}")
        else:
            value_str = str(value)
            lines.append(f"{key_str}: {value_str}")

    return lines


def format_error(
    error_type: str,
    message: str,
    suggestion: Optional[str] = None,
    format: str = "json"
) -> str:
    """
    Format error message.

    Args:
        error_type: Error type/category
        message: Error message
        suggestion: Optional suggestion for fixing the error
        format: Output format ("json" or "table")

    Returns:
        Formatted error string
    """
    error_data = {
        "error": error_type,
        "message": message,
    }

    if suggestion:
        error_data["suggestion"] = suggestion

    if format == "json":
        return format_json(error_data)
    else:
        lines = [
            f"ERROR: {error_type}",
            f"Message: {message}",
        ]
        if suggestion:
            lines.append(f"Suggestion: {suggestion}")
        return "\n".join(lines)


def format_success_message(message: str, format: str = "json") -> str:
    """
    Format success message.

    Args:
        message: Success message
        format: Output format ("json" or "table")

    Returns:
        Formatted message string
    """
    if format == "json":
        return format_json({"status": "success", "message": message})
    else:
        return f"SUCCESS: {message}"
