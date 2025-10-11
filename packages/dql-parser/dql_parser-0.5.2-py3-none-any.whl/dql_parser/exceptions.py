"""
Custom exception classes for DQL parsing errors.

Provides structured error reporting with line/column information and
helpful error messages with intelligent suggestions.
"""

from __future__ import annotations

from typing import List, Optional

from .error_messages import ErrorMessageBuilder


class DQLSyntaxError(Exception):
    """
    Base exception for DQL syntax errors.

    Attributes:
        message: Human-readable error description
        line: Line number where error occurred (1-indexed)
        column: Column number where error occurred (1-indexed)
        context: The problematic line of DQL code
        suggested_fix: Optional suggestion for how to fix the error
        use_enhanced_messages: Whether to use ErrorMessageBuilder (default True)
    """

    def __init__(
        self,
        message: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
        suggested_fix: str = "",
        use_enhanced_messages: bool = True,
    ):
        self.message = message
        self.line = line
        self.column = column
        self.context = context
        self.suggested_fix = suggested_fix
        self.use_enhanced_messages = use_enhanced_messages
        super().__init__(self.get_formatted_message())

    def __str__(self) -> str:
        return self.get_formatted_message()

    def get_formatted_message(self) -> str:
        """
        Format error message with line/column information.

        Uses ErrorMessageBuilder for enhanced suggestions if enabled,
        otherwise falls back to simple formatting.

        Format:
            DQLSyntaxError at line {line}, column {column}:
                {problematic_line}
                {caret_pointer}
            {error_description}
            {suggested_fix}
        """
        # Use simple formatting (for backward compatibility)
        parts = [f"DQLSyntaxError at line {self.line}, column {self.column}:"]

        # Add context line with caret pointer if available
        if self.context:
            parts.append(f"    {self.context}")
            if self.column > 0:
                # Create caret pointer aligned to error column
                caret = " " * (self.column - 1 + 4) + "^"  # +4 for indentation
                parts.append(caret)

        # Add error message
        parts.append(self.message)

        # Add suggested fix if available
        if self.suggested_fix:
            parts.append("")
            parts.append(f"Suggested fix: {self.suggested_fix}")

        return "\n".join(parts)


class InvalidOperatorError(DQLSyntaxError):
    """
    Raised when an unknown or invalid operator is used.

    Uses ErrorMessageBuilder to provide intelligent typo suggestions
    and fuzzy matching against valid operators.

    Example:
        expect column("email") to_be_valid
        # "to_be_valid" is not a recognized operator
    """

    def __init__(
        self,
        operator: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        # Use ErrorMessageBuilder for enhanced suggestions
        builder = ErrorMessageBuilder(
            line=line,
            column=column,
            context=context,
            message=f"Unknown operator: '{operator}'",
        )
        builder.add_operator_suggestions(operator)

        # Get the enhanced message
        enhanced_message = builder.build()

        # Call parent with empty message since we'll override get_formatted_message
        self.operator = operator
        self._enhanced_message = enhanced_message
        super().__init__(
            message=f"Unknown operator: '{operator}'",
            line=line,
            column=column,
            context=context,
            suggested_fix="",
        )

    def get_formatted_message(self) -> str:
        """Return the enhanced error message with suggestions."""
        return self._enhanced_message


class InvalidFieldError(DQLSyntaxError):
    """
    Raised when an invalid field reference is encountered.

    Example:
        expect column("") to_be_null
        # Empty field name
    """

    def __init__(
        self,
        field: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        message = f"Invalid field reference: '{field}'"
        suggested_fix = "Field names must be non-empty strings"
        super().__init__(message, line, column, context, suggested_fix)


class MissingFromClauseError(DQLSyntaxError):
    """
    Raised when an expectation is defined without a FROM clause.

    Example:
        expect column("email") to_not_be_null
        # Missing FROM clause before expectation
    """

    def __init__(
        self,
        line: int = 1,
        column: int = 1,
        context: str = "",
    ):
        message = "Missing 'from' clause before expectation statement"
        suggested_fix = (
            "Add 'from ModelName' before expect statement:\n"
            "    from Customer\n"
            '    expect column("email") to_not_be_null severity critical'
        )
        super().__init__(message, line, column, context, suggested_fix)


class InvalidModelNameError(DQLSyntaxError):
    """
    Raised when model name doesn't follow PascalCase convention.

    Model names must start with uppercase letter and follow PascalCase.
    Provides intelligent suggestions for common naming patterns.

    Example:
        from customer_model
        # Should be "Customer" or "CustomerModel" (PascalCase)
    """

    def __init__(
        self,
        model_name: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        # Use ErrorMessageBuilder for enhanced suggestions
        builder = ErrorMessageBuilder(
            line=line,
            column=column,
            context=context,
            message=f"Invalid model name: '{model_name}'\nModel names must be PascalCase (e.g., Customer, OrderItem)",
        )

        # Convert snake_case to PascalCase for suggestion
        suggested_name = "".join(word.capitalize() for word in model_name.split("_"))
        builder.add_suggestion(suggested_name, 0.95)
        builder.add_hint(f"Try: from {suggested_name}")

        # Get the enhanced message
        enhanced_message = builder.build()

        self.model_name = model_name
        self._enhanced_message = enhanced_message
        super().__init__(
            message=f"Invalid model name: '{model_name}'",
            line=line,
            column=column,
            context=context,
            suggested_fix="",
        )

    def get_formatted_message(self) -> str:
        """Return the enhanced error message with suggestions."""
        return self._enhanced_message


class ReservedKeywordError(DQLSyntaxError):
    """
    Raised when a reserved keyword is used as an identifier.

    DQL has reserved keywords that cannot be used as model names
    or field names.
    """

    def __init__(
        self,
        keyword: str,
        line: int = 0,
        column: int = 0,
        context: str = "",
    ):
        message = f"Cannot use reserved keyword '{keyword}' as identifier"
        suggested_fix = (
            "Reserved keywords cannot be used as model names or field names. "
            "Choose a different name."
        )
        super().__init__(message, line, column, context, suggested_fix)


class DQLMultipleErrors(Exception):
    """
    Raised when multiple syntax errors are encountered during parsing.

    Collects all syntax errors found during error recovery and presents
    them in a formatted, easy-to-read report.

    Attributes:
        errors: List of DQLSyntaxError instances
        file_path: Optional file path for error reporting
        max_displayed: Maximum number of errors to display (default 10)
    """

    def __init__(
        self,
        errors: List[DQLSyntaxError],
        file_path: Optional[str] = None,
        max_displayed: int = 10,
    ):
        self.errors = errors
        self.file_path = file_path
        self.max_displayed = max_displayed
        super().__init__(self.get_formatted_message())

    def __str__(self) -> str:
        return self.get_formatted_message()

    def get_formatted_message(self) -> str:
        """
        Format all errors into a comprehensive report.

        Format:
            Found N syntax errors in {file_path}:

            Error 1 of N:
            DQLSyntaxError at line X, column Y:
                {context}
                ^
            {message}

            Error 2 of N:
            ...

            Summary: Found N syntax errors
        """
        parts = []

        # Header
        num_errors = len(self.errors)
        file_info = f" in {self.file_path}" if self.file_path else ""
        error_word = "error" if num_errors == 1 else "errors"

        if num_errors > self.max_displayed:
            parts.append(
                f"Found {num_errors} syntax {error_word}{file_info} (showing first {self.max_displayed}):\n"
            )
        else:
            parts.append(f"Found {num_errors} syntax {error_word}{file_info}:\n")

        # Sort errors by line number
        sorted_errors = sorted(self.errors, key=lambda e: (e.line, e.column))

        # Display errors (up to max_displayed)
        for i, error in enumerate(sorted_errors[: self.max_displayed], 1):
            parts.append(f"Error {i} of {num_errors}:")
            parts.append(error.get_formatted_message())
            parts.append("")  # Blank line between errors

        # Summary
        if num_errors > self.max_displayed:
            parts.append(
                f"... and {num_errors - self.max_displayed} more {error_word}"
            )
            parts.append("")

        parts.append(f"Summary: Found {num_errors} syntax {error_word}")

        return "\n".join(parts)
