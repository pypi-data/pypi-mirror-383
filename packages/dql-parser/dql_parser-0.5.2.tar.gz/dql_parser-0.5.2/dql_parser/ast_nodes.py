"""
AST node dataclasses for DQL (Data Quality Language).

Defines the Abstract Syntax Tree node structure produced by the DQL parser.
All nodes use Python dataclasses for clean, immutable data structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union


@dataclass
class DQLFile:
    """
    Root AST node representing a complete DQL file.

    A DQL file contains one or more FROM blocks, each defining expectations
    for a specific model.
    """

    from_blocks: List[FromBlock]

    def __str__(self) -> str:
        blocks_str = "\n".join(str(block) for block in self.from_blocks)
        return f"DQLFile(from_blocks={len(self.from_blocks)}):\n{blocks_str}"


@dataclass
class FromBlock:
    """
    Represents a FROM block: a model declaration with its expectations.

    FROM blocks group all expectations that apply to a specific model.
    """

    model_name: str
    expectations: List[ExpectationNode]

    def __str__(self) -> str:
        return f"FROM {self.model_name} ({len(self.expectations)} expectations)"


@dataclass
class ExpectationNode:
    """
    Represents a single EXPECT statement.

    An expectation defines a data quality rule for a column or row,
    with an operator, optional severity, and optional cleaners.
    """

    target: Union[ColumnTarget, RowTarget]
    operator: Operator
    severity: Optional[str] = None  # "critical", "warning", "info", or None (default)
    cleaners: List[CleanerNode] = field(default_factory=list)

    def __str__(self) -> str:
        severity_str = f" severity {self.severity}" if self.severity else ""
        cleaners_str = f" with {len(self.cleaners)} cleaners" if self.cleaners else ""
        return f"EXPECT {self.target} {self.operator}{severity_str}{cleaners_str}"


# Target Types


@dataclass
class ColumnTarget:
    """
    Column-level expectation target.

    Targets a specific field/column in the model.
    """

    field_name: str

    def __str__(self) -> str:
        return f'column("{self.field_name}")'


@dataclass
class RowTarget:
    """
    Row-level expectation target.

    Targets rows matching a WHERE condition.
    """

    condition: Condition

    def __str__(self) -> str:
        return f"row WHERE {self.condition}"


@dataclass
class ExprTarget:
    """
    Expression-level expectation target.

    Targets computed expressions (e.g., price * 1.1, CONCAT(first, last))
    """

    expression: "Expr"

    def __str__(self) -> str:
        return str(self.expression)


# Operator Base and Implementations


@dataclass
class Operator:
    """Base class for all operators."""

    pass


@dataclass
class ToBeNull(Operator):
    """
    to_be_null operator: validates field is NULL.

    No arguments required.
    """

    def __str__(self) -> str:
        return "to_be_null"


@dataclass
class ToNotBeNull(Operator):
    """
    to_not_be_null operator: validates field is NOT NULL.

    No arguments required.
    """

    def __str__(self) -> str:
        return "to_not_be_null"


@dataclass
class ToMatchPattern(Operator):
    """
    to_match_pattern operator: validates field matches regex pattern.

    Args:
        pattern: Regular expression pattern string
    """

    pattern: str

    def __str__(self) -> str:
        return f'to_match_pattern("{self.pattern}")'


@dataclass
class ToBeBetween(Operator):
    """
    to_be_between operator: validates field is within numeric range.

    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
    """

    min_value: Union[int, float]
    max_value: Union[int, float]

    def __str__(self) -> str:
        return f"to_be_between({self.min_value}, {self.max_value})"


@dataclass
class ToBeIn(Operator):
    """
    to_be_in operator: validates field value is in allowed list.

    Args:
        values: List of allowed values
    """

    values: List[Any]

    def __str__(self) -> str:
        values_str = ", ".join(repr(v) for v in self.values)
        return f"to_be_in([{values_str}])"


@dataclass
class ToBeUnique(Operator):
    """
    to_be_unique operator: validates field values are unique.

    No arguments required.
    """

    def __str__(self) -> str:
        return "to_be_unique"


@dataclass
class ToHaveLength(Operator):
    """
    to_have_length operator: validates string/collection length is within range.

    Args:
        min_length: Minimum length (inclusive), optional
        max_length: Maximum length (inclusive), optional
    """

    min_length: Optional[int] = None
    max_length: Optional[int] = None

    def __str__(self) -> str:
        if self.min_length is not None and self.max_length is not None:
            return f"to_have_length({self.min_length}, {self.max_length})"
        elif self.min_length is not None:
            return f"to_have_length(min={self.min_length})"
        elif self.max_length is not None:
            return f"to_have_length(max={self.max_length})"
        else:
            return "to_have_length()"


@dataclass
class ToBeGreaterThan(Operator):
    """
    to_be_greater_than operator: validates numeric field > threshold.

    Args:
        threshold: Numeric threshold value
    """

    threshold: Union[int, float]

    def __str__(self) -> str:
        return f"to_be_greater_than({self.threshold})"


@dataclass
class ToBeLessThan(Operator):
    """
    to_be_less_than operator: validates numeric field < threshold.

    Args:
        threshold: Numeric threshold value
    """

    threshold: Union[int, float]

    def __str__(self) -> str:
        return f"to_be_less_than({self.threshold})"


@dataclass
class ToSatisfy(Operator):
    """
    to_satisfy operator: validates field/row satisfies custom Python expression.

    Args:
        expression: Python lambda expression or function reference as string
        expr_type: Type of expression - "lambda" or "function"
    """

    expression: str
    expr_type: str = "lambda"  # "lambda" or "function"

    def __str__(self) -> str:
        return f"to_satisfy({self.expression})"


@dataclass
class ToReference(Operator):
    """
    to_reference operator: validates foreign key referential integrity.

    Args:
        target_model: Name of the target model (PascalCase)
        target_field: Target field name or list of field names for composite keys
        on_delete: Optional ON_DELETE behavior (CASCADE, SET_NULL, RESTRICT)
    """

    target_model: str
    target_field: Union[str, List[str]]
    on_delete: Optional[str] = None

    def __str__(self) -> str:
        if isinstance(self.target_field, list):
            fields = f"[{', '.join(repr(f) for f in self.target_field)}]"
        else:
            fields = repr(self.target_field)

        if self.on_delete:
            return f"to_reference({self.target_model}, {fields}, ON_DELETE {self.on_delete})"
        return f"to_reference({self.target_model}, {fields})"


# Row-Level Condition Nodes

Condition = Union["Comparison", "LogicalExpr"]
Expr = Union["ColumnRef", "FieldRef", "Value", "FunctionCall", "ArithmeticExpr"]


@dataclass
class Comparison:
    """
    Binary comparison expression.

    Args:
        left: Left-hand side expression
        operator: Comparison operator ("==", "!=", "<", "<=", ">", ">=")
        right: Right-hand side expression
    """

    left: Expr
    operator: str  # "==", "!=", "<", "<=", ">", ">="
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


@dataclass
class LogicalExpr:
    """
    Logical expression (AND, OR, NOT).

    Args:
        operator: Logical operator ("AND", "OR", "NOT")
        operands: List of condition operands (1 for NOT, 2+ for AND/OR)
    """

    operator: str  # "AND", "OR", "NOT"
    operands: List[Condition]

    def __str__(self) -> str:
        if self.operator == "NOT":
            return f"NOT {self.operands[0]}"
        op_str = f" {self.operator} ".join(str(op) for op in self.operands)
        return f"({op_str})"


@dataclass
class ColumnRef:
    """
    Reference to a column/field.

    Args:
        field_name: Name of the field being referenced
    """

    field_name: str

    def __str__(self) -> str:
        return f'column("{self.field_name}")'


@dataclass
class FieldRef:
    """
    Simple field reference (just field name, not column() syntax).

    Args:
        field_name: Name of the field being referenced
    """

    field_name: str

    def __str__(self) -> str:
        return self.field_name


@dataclass
class Value:
    """
    Literal value (string, number, or NULL).

    Args:
        value: The literal value (str, int, float, or None for NULL)
    """

    value: Union[str, int, float, None]

    def __str__(self) -> str:
        if self.value is None:
            return "null"
        return repr(self.value)


@dataclass
class FunctionCall:
    """
    Function call expression.

    Args:
        function_name: Name of the function (e.g., "CONCAT")
        args: List of argument expressions
    """

    function_name: str  # "CONCAT"
    args: List[Expr]

    def __str__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.args)
        return f"{self.function_name}({args_str})"


@dataclass
class ArithmeticExpr:
    """
    Arithmetic expression.

    Args:
        operator: Arithmetic operator ("+", "-", "*", "/", "%")
        left: Left-hand side expression
        right: Right-hand side expression
    """

    operator: str  # "+", "-", "*", "/", "%"
    left: Expr
    right: Expr

    def __str__(self) -> str:
        return f"({self.left} {self.operator} {self.right})"


# Cleaner Nodes


@dataclass
class CleanerNode:
    """
    Represents a cleaner function call in on_failure clean_with clause.

    Args:
        cleaner_name: Name of the cleaner function
        args: List of arguments (empty list for no args)
    """

    cleaner_name: str
    args: List[Any] = field(default_factory=list)

    def __str__(self) -> str:
        if self.args:
            args_str = ", ".join(repr(arg) for arg in self.args)
            return f'clean_with("{self.cleaner_name}", {args_str})'
        return f'clean_with("{self.cleaner_name}")'


@dataclass
class IncludeNode:
    """
    Represents an INCLUDE directive.

    Attributes:
        file_path: Path to file to include (as string from DQL)
    """

    file_path: str

    def __str__(self) -> str:
        return f'INCLUDE "{self.file_path}"'


@dataclass
class MacroDefinitionNode:
    """
    Represents a DEFINE MACRO statement.

    Attributes:
        name: Macro name
        parameters: List of parameter names
        expectations: List of expectation nodes in macro body
    """

    name: str
    parameters: List[str]
    expectations: List[ExpectationNode]

    def __str__(self) -> str:
        params = ", ".join(self.parameters)
        return f"DEFINE MACRO {self.name}({params}) AS {{ {len(self.expectations)} expectations }}"


@dataclass
class MacroInvocationNode:
    """
    Represents a USE MACRO statement.

    Attributes:
        name: Macro name to invoke
        arguments: List of argument values
    """

    name: str
    arguments: List[Any]

    def __str__(self) -> str:
        args = ", ".join(str(arg) for arg in self.arguments)
        return f"USE MACRO {self.name}({args})"
