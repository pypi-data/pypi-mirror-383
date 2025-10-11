"""
Lambda expression validator for to_satisfy operator.

Validates Python lambda expressions and function references at parse time,
ensuring syntax is correct and dangerous functions are not used.
"""

import ast
import re
from typing import Tuple


# Dangerous functions that should not be allowed in expressions
DANGEROUS_FUNCTIONS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "open",
    "input",
    "globals",
    "locals",
    "vars",
    "dir",
    "getattr",
    "setattr",
    "delattr",
    "hasattr",
}


class LambdaExpressionValidator:
    """
    Validates Python lambda expressions and function references.

    Performs syntax validation and security checks without executing code.
    """

    @staticmethod
    def validate(expression: str) -> Tuple[bool, str, str]:
        """
        Validate a Python expression for use in to_satisfy operator.

        Args:
            expression: The expression string to validate

        Returns:
            Tuple of (is_valid, expr_type, error_message)
            - is_valid: True if expression is valid
            - expr_type: "lambda" or "function"
            - error_message: Empty string if valid, error description if invalid
        """
        expression = expression.strip()

        if not expression:
            return False, "", "Expression cannot be empty"

        # Check for dangerous functions
        for dangerous in DANGEROUS_FUNCTIONS:
            # Use word boundaries to avoid false positives (e.g., "compile_" should be ok)
            pattern = r'\b' + re.escape(dangerous) + r'\b'
            if re.search(pattern, expression):
                return False, "", f"Dangerous function '{dangerous}' is not allowed in expressions"

        # Determine expression type
        if expression.startswith("lambda "):
            expr_type = "lambda"
            return LambdaExpressionValidator._validate_lambda(expression)
        else:
            expr_type = "function"
            return LambdaExpressionValidator._validate_function_reference(expression)

    @staticmethod
    def _validate_lambda(expression: str) -> Tuple[bool, str, str]:
        """
        Validate a lambda expression using Python's AST parser.

        Args:
            expression: Lambda expression string

        Returns:
            Tuple of (is_valid, "lambda", error_message)
        """
        try:
            # Parse the lambda expression
            parsed = ast.parse(expression, mode='eval')

            # Verify it's actually a lambda
            if not isinstance(parsed.body, ast.Lambda):
                return False, "lambda", "Expression must be a valid lambda expression"

            # Recursively check for dangerous calls in the lambda body
            for node in ast.walk(parsed):
                if isinstance(node, ast.Call):
                    # Check if calling a dangerous function
                    if isinstance(node.func, ast.Name):
                        if node.func.id in DANGEROUS_FUNCTIONS:
                            return False, "lambda", f"Dangerous function '{node.func.id}' is not allowed"

            return True, "lambda", ""

        except SyntaxError as e:
            return False, "lambda", f"Invalid lambda syntax: {e.msg}"
        except Exception as e:
            return False, "lambda", f"Failed to parse lambda: {str(e)}"

    @staticmethod
    def _validate_function_reference(expression: str) -> Tuple[bool, str, str]:
        """
        Validate a function reference (simple identifier).

        Args:
            expression: Function reference string

        Returns:
            Tuple of (is_valid, "function", error_message)
        """
        # Function reference should be a valid Python identifier
        if not expression.isidentifier():
            return False, "function", f"Invalid function reference: '{expression}' is not a valid identifier"

        # Check if it's a dangerous function
        if expression in DANGEROUS_FUNCTIONS:
            return False, "function", f"Dangerous function '{expression}' is not allowed"

        return True, "function", ""
