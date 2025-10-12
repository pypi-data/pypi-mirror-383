"""
Smart call frequency tracker for auto-filtering hot loops.

Monitors function call frequency and automatically filters high-frequency
functions to prevent event queue overflow while preserving diagnostic info.
"""

import time
from collections import deque, defaultdict
from typing import Dict, Set, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class TruncationInfo:
    """Information about a truncated function."""
    module_name: str
    function_name: str
    first_truncated_at: float
    total_dropped: int = 0
    reason: str = "auto_filter_hot_loop"


class CallTracker:
    """
    Tracks call frequency and automatically filters hot loops.

    When a function is called more than `threshold` times within `window_seconds`,
    it's automatically filtered to prevent event queue overflow.

    The first `threshold` calls are always kept so AI agents can see the pattern.
    Truncation metadata is logged for transparency.
    """

    def __init__(
        self,
        threshold: int = 100,
        window_seconds: float = 10.0,
        reset_interval: float = 60.0,
    ):
        """
        Initialize call tracker.

        Args:
            threshold: Max calls per function in window before filtering
            window_seconds: Time window for counting calls (seconds)
            reset_interval: How often to reset filters to re-sample (seconds)
        """
        self.threshold = threshold
        self.window_seconds = window_seconds
        self.reset_interval = reset_interval

        # Track timestamps of calls per function
        self.call_timestamps: Dict[Tuple[str, str], deque] = defaultdict(deque)

        # Currently filtered functions
        self.filtered_functions: Set[Tuple[str, str]] = set()

        # Truncation metadata
        self.truncations: Dict[Tuple[str, str], TruncationInfo] = {}

        # Last reset time
        self.last_reset = time.time()

    def should_filter(self, module_name: str, function_name: str) -> bool:
        """
        Check if this function call should be filtered.

        Args:
            module_name: Module name (e.g., "myapp.utils")
            function_name: Function name (e.g., "helper_func")

        Returns:
            True if event should be filtered (dropped), False otherwise
        """
        key = (module_name, function_name)
        current_time = time.time()

        # Check if we should reset filters (re-sample)
        if current_time - self.last_reset > self.reset_interval:
            self._reset_filters()
            self.last_reset = current_time

        # If already filtered, increment counter and drop
        if key in self.filtered_functions:
            if key in self.truncations:
                self.truncations[key].total_dropped += 1
            return True

        # Track this call
        timestamps = self.call_timestamps[key]
        timestamps.append(current_time)

        # Prune old timestamps outside window
        cutoff = current_time - self.window_seconds
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()

        # Check if threshold exceeded
        call_count = len(timestamps)
        if call_count > self.threshold:
            # Start filtering this function
            self.filtered_functions.add(key)
            self.truncations[key] = TruncationInfo(
                module_name=module_name,
                function_name=function_name,
                first_truncated_at=current_time,
                total_dropped=1,  # This call is the first to be dropped
            )
            return True  # Filter this call

        return False  # Allow this call

    def _reset_filters(self):
        """
        Reset filtered functions to allow re-sampling.

        This ensures we detect changes in behavior (e.g., hot loop ends).
        Keeps truncation metadata for reporting.
        """
        # Clear active filters but keep truncation history
        self.filtered_functions.clear()

        # Clear old timestamps to free memory
        self.call_timestamps.clear()

    def get_truncation_summary(self) -> Dict[str, any]:
        """
        Get summary of truncated functions.

        Returns:
            Dictionary with truncation statistics
        """
        if not self.truncations:
            return {"truncated_functions": 0, "total_dropped_events": 0}

        total_dropped = sum(t.total_dropped for t in self.truncations.values())

        return {
            "truncated_functions": len(self.truncations),
            "total_dropped_events": total_dropped,
            "details": [
                {
                    "module": t.module_name,
                    "function": t.function_name,
                    "dropped_count": t.total_dropped,
                    "reason": t.reason,
                }
                for t in self.truncations.values()
            ]
        }

    def get_active_filters(self) -> Set[Tuple[str, str]]:
        """Get currently filtered functions."""
        return self.filtered_functions.copy()
