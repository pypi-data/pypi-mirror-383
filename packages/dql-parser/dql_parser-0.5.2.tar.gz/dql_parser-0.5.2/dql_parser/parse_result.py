"""
ParseResult class for representing parsing results with error recovery.

Supports partial success mode where some expectations parse successfully
while others have syntax errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .ast_nodes import DQLFile
from .exceptions import DQLSyntaxError


@dataclass
class ParseResult:
    """
    Result of parsing DQL with error recovery support.

    Allows the parser to return both successfully parsed expectations
    and any syntax errors encountered during parsing.

    Attributes:
        ast: The parsed DQLFile with valid expectations
        errors: List of syntax errors encountered (empty if no errors)
        file_path: Optional file path for error reporting

    Example:
        >>> result = parser.parse(dql_text)
        >>> if result.has_errors():
        ...     print(f"Found {len(result.errors)} errors")
        ...     for error in result.errors:
        ...         print(error)
        >>> if result.ast.from_blocks:
        ...     print(f"Parsed {len(result.ast.from_blocks)} FROM blocks")
    """

    ast: DQLFile
    errors: List[DQLSyntaxError] = field(default_factory=list)
    file_path: Optional[str] = None

    def has_errors(self) -> bool:
        """
        Check if any syntax errors were encountered.

        Returns:
            True if errors exist, False otherwise
        """
        return len(self.errors) > 0

    def is_success(self) -> bool:
        """
        Check if parsing was completely successful (no errors).

        Returns:
            True if no errors and at least one expectation parsed
        """
        return not self.has_errors() and len(self.ast.from_blocks) > 0

    def is_partial_success(self) -> bool:
        """
        Check if parsing was partially successful (some valid, some errors).

        Returns:
            True if has both valid expectations and errors
        """
        return self.has_errors() and len(self.ast.from_blocks) > 0

    def raise_if_errors(self) -> None:
        """
        Raise DQLMultipleErrors if any errors exist.

        Raises:
            DQLMultipleErrors: If errors list is not empty
        """
        if self.has_errors():
            from .exceptions import DQLMultipleErrors

            raise DQLMultipleErrors(self.errors, file_path=self.file_path)

    def format_summary(self) -> str:
        """
        Generate a summary message about parsing results.

        Returns:
            Human-readable summary string

        Example:
            "Successfully parsed 3 expectations with no errors"
            "Parsed 2 valid expectations, found 1 syntax error"
            "Found 5 syntax errors, no valid expectations parsed"
        """
        num_blocks = len(self.ast.from_blocks)
        num_expectations = sum(len(block.expectations) for block in self.ast.from_blocks)
        num_errors = len(self.errors)

        if not self.has_errors():
            return f"Successfully parsed {num_expectations} expectations with no errors"

        if self.is_partial_success():
            error_word = "error" if num_errors == 1 else "errors"
            return f"Parsed {num_expectations} valid expectations, found {num_errors} syntax {error_word}"

        # Only errors, no valid expectations
        error_word = "error" if num_errors == 1 else "errors"
        return f"Found {num_errors} syntax {error_word}, no valid expectations parsed"
