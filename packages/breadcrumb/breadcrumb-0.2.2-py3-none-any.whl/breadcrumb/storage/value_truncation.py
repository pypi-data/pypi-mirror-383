"""
Value truncation utilities for preventing huge trace storage.

Truncates large values to prevent memory and storage issues.
"""

import json
from typing import Any, Dict

# Max size for individual values (1KB)
MAX_VALUE_SIZE = 1024

# Truncation indicator
TRUNCATION_MARKER = "[TRUNCATED"


def truncate_value(value: Any, max_size: int = MAX_VALUE_SIZE) -> Any:
    """
    Truncate large values with indicator.

    Args:
        value: Value to truncate (any type)
        max_size: Maximum size in bytes (default: 1KB)

    Returns:
        Truncated value with indicator if needed

    Example:
        >>> truncate_value("x" * 2000)
        "xxx...[TRUNCATED: original size 2000 bytes]"

        >>> truncate_value({"key": "value"})
        {"key": "value"}  # No truncation needed
    """
    # For non-string types, convert to string first to check size
    if isinstance(value, (dict, list)):
        try:
            json_str = json.dumps(value, default=str)
            if len(json_str.encode('utf-8')) <= max_size:
                return value

            # Truncate JSON string
            truncated = json_str[:max_size]
            original_size = len(json_str.encode('utf-8'))
            return f"{truncated}... {TRUNCATION_MARKER}: original size {original_size} bytes]"
        except (TypeError, ValueError):
            # Fall back to repr
            str_value = repr(value)
            if len(str_value.encode('utf-8')) <= max_size:
                return str_value

            truncated = str_value[:max_size]
            original_size = len(str_value.encode('utf-8'))
            return f"{truncated}... {TRUNCATION_MARKER}: original size {original_size} bytes]"

    # For strings and other types
    str_value = str(value) if not isinstance(value, str) else value
    value_bytes = str_value.encode('utf-8')

    if len(value_bytes) <= max_size:
        return value

    # Truncate to max_size bytes
    # Decode back to string, handling potential encoding issues
    try:
        truncated = value_bytes[:max_size].decode('utf-8', errors='ignore')
    except UnicodeDecodeError:
        truncated = value_bytes[:max_size].decode('utf-8', errors='replace')

    original_size = len(value_bytes)
    return f"{truncated}... {TRUNCATION_MARKER}: original size {original_size} bytes]"


def truncate_dict(data: Dict[str, Any], max_value_size: int = MAX_VALUE_SIZE) -> Dict[str, Any]:
    """
    Recursively truncate all values in a dictionary.

    Args:
        data: Dictionary to truncate
        max_value_size: Maximum size for each value

    Returns:
        Dict with truncated values

    Example:
        >>> truncate_dict({"user": "alice", "data": "x" * 2000})
        {"user": "alice", "data": "xxx...[TRUNCATED: original size 2000 bytes]"}
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, dict):
            result[key] = truncate_dict(value, max_value_size)
        elif isinstance(value, list):
            result[key] = [
                truncate_dict(item, max_value_size) if isinstance(item, dict) else truncate_value(item, max_value_size)
                for item in value
            ]
        else:
            result[key] = truncate_value(value, max_value_size)

    return result
