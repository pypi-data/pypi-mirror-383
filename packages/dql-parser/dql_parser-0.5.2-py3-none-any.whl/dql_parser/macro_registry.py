"""
Macro storage, lookup, and expansion for DQL parser.

Handles DEFINE MACRO definitions, parameter validation, and expansion
of macro invocations with parameter substitution.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .ast_nodes import ExpectationNode
from .exceptions import DQLSyntaxError


@dataclass
class MacroDefinition:
    """
    Represents a macro definition.

    Attributes:
        name: Macro name (lowercase identifier)
        parameters: List of parameter names
        template: List of expectation AST nodes forming the macro body
    """

    name: str
    parameters: List[str]
    template: List[ExpectationNode]


class MacroRegistry:
    """
    Registry for macro definitions and expansion.

    Stores macro definitions and provides lookup and expansion
    with parameter substitution.

    Example:
        >>> registry = MacroRegistry()
        >>> registry.define("email_required", [], [expectation_node])
        >>> macro = registry.get("email_required")
        >>> expanded = registry.expand("email_required", [])
    """

    def __init__(self):
        """Initialize empty macro registry."""
        self.macros: Dict[str, MacroDefinition] = {}

    def define(
        self,
        name: str,
        parameters: List[str],
        template: List[ExpectationNode],
    ) -> None:
        """
        Register a macro definition.

        Args:
            name: Macro name (must be unique)
            parameters: List of parameter names
            template: List of expectation nodes forming macro body

        Raises:
            DQLSyntaxError: If macro name already defined
        """
        if name in self.macros:
            raise DQLSyntaxError(
                message=f"Macro '{name}' is already defined",
                line=0,
                column=0,
                context="",
            )

        # Validate parameter count (0-5 as per AC7)
        if len(parameters) > 5:
            raise DQLSyntaxError(
                message=f"Macro '{name}' has {len(parameters)} parameters. "
                f"Maximum is 5.",
                line=0,
                column=0,
                context="",
            )

        # Check for duplicate parameters
        if len(parameters) != len(set(parameters)):
            raise DQLSyntaxError(
                message=f"Macro '{name}' has duplicate parameters",
                line=0,
                column=0,
                context="",
            )

        self.macros[name] = MacroDefinition(name, parameters, template)

    def get(self, name: str) -> Optional[MacroDefinition]:
        """
        Lookup macro by name.

        Args:
            name: Macro name

        Returns:
            MacroDefinition if found, None otherwise
        """
        return self.macros.get(name)

    def exists(self, name: str) -> bool:
        """
        Check if macro is defined.

        Args:
            name: Macro name

        Returns:
            True if macro exists, False otherwise
        """
        return name in self.macros

    def expand(
        self, name: str, arguments: List[Any], line: int = 0, column: int = 0
    ) -> List[ExpectationNode]:
        """
        Expand macro with given arguments.

        Args:
            name: Macro name
            arguments: List of argument values
            line: Line number of macro invocation (for error messages)
            column: Column number of macro invocation (for error messages)

        Returns:
            List of expanded expectation nodes with parameters substituted

        Raises:
            DQLSyntaxError: If macro not defined or argument count mismatch
        """
        macro = self.get(name)
        if not macro:
            raise DQLSyntaxError(
                message=f"Undefined macro: '{name}'",
                line=line,
                column=column,
                context="",
                suggested_fix=f"Define macro with: DEFINE MACRO {name}(...) AS {{ ... }}",
            )

        if len(arguments) != len(macro.parameters):
            raise DQLSyntaxError(
                message=f"Macro '{name}' expects {len(macro.parameters)} "
                f"argument(s), got {len(arguments)}",
                line=line,
                column=column,
                context="",
                suggested_fix=f"Macro definition: {name}({', '.join(macro.parameters)})",
            )

        # Create expander and expand
        expander = MacroExpander(macro, arguments)
        return expander.expand()

    def clear(self) -> None:
        """Clear all macro definitions."""
        self.macros.clear()

    def get_all_names(self) -> List[str]:
        """
        Get list of all defined macro names.

        Returns:
            List of macro names
        """
        return list(self.macros.keys())


class MacroExpander:
    """
    Expands macro template with parameter substitution.

    Clones macro template AST nodes and replaces parameter references
    with actual argument values.

    Example:
        >>> macro = MacroDefinition("required_field", ["field_name"], [template_node])
        >>> expander = MacroExpander(macro, ['"email"'])
        >>> expanded = expander.expand()
    """

    def __init__(self, macro: MacroDefinition, arguments: List[Any]):
        """
        Initialize macro expander.

        Args:
            macro: Macro definition to expand
            arguments: Argument values for substitution
        """
        self.macro = macro
        self.param_map = dict(zip(macro.parameters, arguments))

    def expand(self) -> List[ExpectationNode]:
        """
        Clone template AST and substitute parameters.

        Returns:
            List of expanded expectation nodes
        """
        expanded = []
        for expectation in self.macro.template:
            # Deep copy to avoid mutating original template
            cloned = copy.deepcopy(expectation)
            # Substitute parameters in the cloned node
            substituted = self._substitute_parameters(cloned)
            expanded.append(substituted)
        return expanded

    def _substitute_parameters(
        self, expectation: ExpectationNode
    ) -> ExpectationNode:
        """
        Replace parameter references with actual arguments.

        Recursively walks the expectation AST node and replaces
        any parameter references found.

        Args:
            expectation: Expectation node to process

        Returns:
            Expectation node with parameters substituted
        """
        # Substitute in target (column name, row condition, etc.)
        if hasattr(expectation, "target"):
            expectation.target = self._substitute_in_target(expectation.target)

        # Substitute in operator arguments
        if hasattr(expectation, "operator") and hasattr(expectation.operator, "arguments"):
            expectation.operator.arguments = [
                self._substitute_value(arg) for arg in expectation.operator.arguments
            ]

        return expectation

    def _substitute_in_target(self, target: Any) -> Any:
        """
        Substitute parameters in expectation target.

        Args:
            target: Target node (ColumnTarget, RowTarget, etc.)

        Returns:
            Target with parameters substituted
        """
        # For ColumnTarget, substitute field_name if it's a parameter
        if hasattr(target, "field_name"):
            target.field_name = self._substitute_value(target.field_name)

        # For RowTarget, substitute in condition
        if hasattr(target, "condition"):
            target.condition = self._substitute_in_condition(target.condition)

        return target

    def _substitute_in_condition(self, condition: Any) -> Any:
        """
        Substitute parameters in row-level conditions.

        Args:
            condition: Condition node (Comparison, LogicalExpr, etc.)

        Returns:
            Condition with parameters substituted
        """
        # Recursively substitute in left and right sides
        if hasattr(condition, "left"):
            condition.left = self._substitute_value(condition.left)
        if hasattr(condition, "right"):
            condition.right = self._substitute_value(condition.right)

        # Recursively substitute in nested conditions
        if hasattr(condition, "conditions"):
            condition.conditions = [
                self._substitute_in_condition(c) for c in condition.conditions
            ]

        return condition

    def _substitute_value(self, value: Any) -> Any:
        """
        Substitute parameter reference with argument value.

        Args:
            value: Value that may be a parameter reference

        Returns:
            Substituted value if parameter, otherwise original value
        """
        # If value is a string parameter reference, substitute it
        if isinstance(value, str) and value in self.param_map:
            return self.param_map[value]

        # If value is a parameter name node, substitute it
        if hasattr(value, "__class__") and value.__class__.__name__ == "ParamRef":
            param_name = value.name
            if param_name in self.param_map:
                return self.param_map[param_name]

        return value
