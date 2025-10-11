"""
Enhanced error message builder with suggestions and hints.

Provides tools for creating helpful, context-aware error messages
with typo suggestions and actionable hints.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from .fuzzy_matcher import fuzzy_match
from .typo_dictionary import (
    VALID_KEYWORDS,
    VALID_OPERATORS,
    get_correct_case,
    get_typo_correction,
    is_case_error,
)


class ErrorMessageBuilder:
    """
    Builder for enhanced error messages with suggestions and hints.

    Example:
        >>> builder = ErrorMessageBuilder(
        ...     line=5,
        ...     column=23,
        ...     context='expect column("email") to_not_null',
        ...     message="Unknown operator"
        ... )
        >>> builder.add_operator_suggestions("to_not_null")
        >>> print(builder.build())
    """

    def __init__(
        self,
        line: int,
        column: int,
        context: str,
        message: str,
    ):
        """
        Initialize error message builder.

        Args:
            line: Line number where error occurred
            column: Column number where error occurred
            context: The line of code with the error
            message: Base error message
        """
        self.line = line
        self.column = column
        self.context = context
        self.message = message
        self.suggestions: List[Tuple[str, float]] = []
        self.hints: List[str] = []

    def add_suggestion(self, text: str, confidence: float) -> None:
        """
        Add a suggestion with confidence score.

        Args:
            text: Suggested correction
            confidence: Confidence score (0.0-1.0)
        """
        self.suggestions.append((text, confidence))

    def add_hint(self, hint: str) -> None:
        """
        Add a contextual hint.

        Args:
            hint: Helpful hint text
        """
        self.hints.append(hint)

    def add_operator_suggestions(
        self, unknown_operator: str, threshold: float = 0.7
    ) -> None:
        """
        Add suggestions for an unknown operator.

        Checks:
        1. Common typo dictionary
        2. Case sensitivity
        3. Fuzzy matching against valid operators

        Args:
            unknown_operator: The unknown operator string
            threshold: Minimum similarity threshold (default 0.7)
        """
        # Check common typos first
        typo_correction = get_typo_correction(unknown_operator)
        if typo_correction != unknown_operator:
            self.add_suggestion(typo_correction, 0.95)
            self.add_hint(
                f"Common typo: '{unknown_operator}' → '{typo_correction}'"
            )
            return

        # Check case sensitivity
        if is_case_error(unknown_operator, VALID_OPERATORS):
            correct_case = get_correct_case(unknown_operator, VALID_OPERATORS)
            self.add_suggestion(correct_case, 0.90)
            self.add_hint(
                f"Operator names must be lowercase: '{unknown_operator}' → '{correct_case}'"
            )
            return

        # Fuzzy match against valid operators
        matches = fuzzy_match(unknown_operator, VALID_OPERATORS, threshold=threshold)
        for operator, confidence in matches:
            self.add_suggestion(operator, confidence)

        if matches:
            self.add_hint(
                "Valid operators: " + ", ".join(VALID_OPERATORS[:5]) + ", ..."
            )

    def add_keyword_suggestions(self, unknown_keyword: str, threshold: float = 0.7) -> None:
        """
        Add suggestions for an unknown keyword.

        Args:
            unknown_keyword: The unknown keyword string
            threshold: Minimum similarity threshold (default 0.7)
        """
        # Check case sensitivity
        if is_case_error(unknown_keyword, VALID_KEYWORDS):
            correct_case = get_correct_case(unknown_keyword, VALID_KEYWORDS)
            self.add_suggestion(correct_case, 0.90)
            self.add_hint(
                f"Keywords must be lowercase: '{unknown_keyword}' → '{correct_case}'"
            )
            return

        # Fuzzy match against valid keywords
        matches = fuzzy_match(unknown_keyword, VALID_KEYWORDS, threshold=threshold)
        for keyword, confidence in matches:
            self.add_suggestion(keyword, confidence)

        if matches:
            self.add_hint(
                "Valid keywords: " + ", ".join(VALID_KEYWORDS[:8]) + ", ..."
            )

    def build(self) -> str:
        """
        Build the complete formatted error message.

        Returns:
            Formatted error message with suggestions and hints

        Format:
            DQLSyntaxError at line X, column Y:
                {context}
                ^
            {message}

            Did you mean:
              • suggestion1 (95% match)
              • suggestion2 (80% match)

            Hint:
              {hint1}
              {hint2}
        """
        parts = []

        # Error location header
        parts.append(f"DQLSyntaxError at line {self.line}, column {self.column}:")

        # Context line with caret
        if self.context:
            parts.append(f"    {self.context}")
            if self.column > 0:
                caret = " " * (self.column - 1 + 4) + "^"
                parts.append(caret)

        # Main error message
        parts.append(self.message)

        # Suggestions section
        if self.suggestions:
            parts.append("")
            parts.append("Did you mean:")
            # Show top 3 suggestions
            for suggestion, confidence in self.suggestions[:3]:
                confidence_pct = int(confidence * 100)
                parts.append(f"  • {suggestion} ({confidence_pct}% match)")

        # Hints section
        if self.hints:
            parts.append("")
            if len(self.hints) == 1:
                parts.append("Hint:")
            else:
                parts.append("Hints:")
            for hint in self.hints:
                parts.append(f"  {hint}")

        return "\n".join(parts)


def enhance_lark_error_message(
    error_message: str,
    line: int,
    column: int,
    context: str,
    unexpected_token: Optional[str] = None,
) -> str:
    """
    Enhance a Lark parser error message with suggestions.

    Args:
        error_message: Original Lark error message
        line: Line number
        column: Column number
        context: Line of code with error
        unexpected_token: The unexpected token, if known

    Returns:
        Enhanced error message with suggestions

    Example:
        >>> enhance_lark_error_message(
        ...     "Unexpected token",
        ...     5,
        ...     23,
        ...     'expect column("email") to_not_null',
        ...     "to_not_null"
        ... )
    """
    builder = ErrorMessageBuilder(line, column, context, error_message)

    # If we have an unexpected token, try to provide suggestions
    if unexpected_token:
        # Check if it looks like an operator
        if unexpected_token.startswith("to_"):
            builder.add_operator_suggestions(unexpected_token)
        # Check if it looks like a keyword
        elif unexpected_token.lower() in ["from", "expect", "column", "row", "where", "severity"]:
            builder.add_keyword_suggestions(unexpected_token)

    return builder.build()


def create_unknown_operator_error(
    operator: str,
    line: int,
    column: int,
    context: str,
) -> str:
    """
    Create an error message for an unknown operator.

    Args:
        operator: The unknown operator string
        line: Line number
        column: Column number
        context: Line of code with error

    Returns:
        Formatted error message with suggestions
    """
    builder = ErrorMessageBuilder(
        line=line,
        column=column,
        context=context,
        message=f"Unknown operator: '{operator}'",
    )
    builder.add_operator_suggestions(operator)
    return builder.build()


def create_incomplete_syntax_error(
    issue: str,
    line: int,
    column: int,
    context: str,
    hint: Optional[str] = None,
) -> str:
    """
    Create an error message for incomplete syntax.

    Args:
        issue: Description of the incomplete syntax issue
        line: Line number
        column: Column number
        context: Line of code with error
        hint: Optional helpful hint

    Returns:
        Formatted error message

    Example:
        >>> create_incomplete_syntax_error(
        ...     "Unclosed parenthesis",
        ...     5,
        ...     30,
        ...     'expect column("email") to_match_pattern("test',
        ...     "Add closing parenthesis ')' and closing quote"
        ... )
    """
    builder = ErrorMessageBuilder(
        line=line,
        column=column,
        context=context,
        message=issue,
    )
    if hint:
        builder.add_hint(hint)
    return builder.build()
