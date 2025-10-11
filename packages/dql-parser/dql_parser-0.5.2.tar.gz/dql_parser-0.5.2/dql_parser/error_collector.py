"""
Error collector for accumulating syntax errors during error recovery parsing.

Manages collection of multiple syntax errors and enforces error limits
to prevent error spam.
"""

from __future__ import annotations

from typing import List

from .exceptions import DQLSyntaxError


class DQLErrorCollector:
    """
    Collects syntax errors during parsing with error recovery.

    Manages a list of DQLSyntaxError instances and enforces a maximum
    error limit to prevent overwhelming users with too many errors.

    Attributes:
        max_errors: Maximum number of errors to collect (default 10)
        errors: List of collected syntax errors

    Example:
        >>> collector = DQLErrorCollector(max_errors=10)
        >>> collector.add_error(DQLSyntaxError("Bad syntax", 1, 5, "bad line"))
        >>> if collector.has_errors():
        ...     print(f"Collected {len(collector.errors)} errors")
    """

    def __init__(self, max_errors: int = 10):
        """
        Initialize error collector.

        Args:
            max_errors: Maximum number of errors to collect before stopping
        """
        self.max_errors = max_errors
        self.errors: List[DQLSyntaxError] = []

    def add_error(self, error: DQLSyntaxError) -> bool:
        """
        Add a syntax error to the collection.

        Args:
            error: DQLSyntaxError instance to add

        Returns:
            True if error was added, False if max_errors limit reached
        """
        if len(self.errors) < self.max_errors:
            self.errors.append(error)
            return True
        return False

    def has_errors(self) -> bool:
        """
        Check if any errors have been collected.

        Returns:
            True if errors exist, False otherwise
        """
        return len(self.errors) > 0

    def is_at_limit(self) -> bool:
        """
        Check if error limit has been reached.

        Returns:
            True if at max_errors limit, False otherwise
        """
        return len(self.errors) >= self.max_errors

    def get_sorted_errors(self) -> List[DQLSyntaxError]:
        """
        Get errors sorted by line and column number.

        Returns:
            List of errors sorted by (line, column)
        """
        return sorted(self.errors, key=lambda e: (e.line, e.column))

    def format_summary(self) -> str:
        """
        Generate a summary message about collected errors.

        Returns:
            Human-readable summary string

        Example:
            "Found 3 syntax errors"
            "Found 10+ syntax errors (stopped after 10)"
        """
        count = len(self.errors)
        error_word = "error" if count == 1 else "errors"

        if self.is_at_limit():
            return f"Found {self.max_errors}+ syntax {error_word} (stopped after {self.max_errors})"

        return f"Found {count} syntax {error_word}"

    def clear(self) -> None:
        """Clear all collected errors."""
        self.errors.clear()
