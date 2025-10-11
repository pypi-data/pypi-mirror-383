"""
Lark Transformer for converting parse tree to DQL AST nodes.

This module transforms the Lark parse tree generated from grammar.lark
into strongly-typed AST node dataclasses defined in ast_nodes.py.
"""

from __future__ import annotations

from typing import Any, List, Union

from lark import Token, Transformer

from .ast_nodes import (
    ArithmeticExpr,
    CleanerNode,
    ColumnRef,
    ColumnTarget,
    Comparison,
    DQLFile,
    ExpectationNode,
    ExprTarget,
    FieldRef,
    FromBlock,
    FunctionCall,
    IncludeNode,
    LogicalExpr,
    MacroDefinitionNode,
    MacroInvocationNode,
    RowTarget,
    ToBeGreaterThan,
    ToBeIn,
    ToBeBetween,
    ToBeLessThan,
    ToBeNull,
    ToBeUnique,
    ToHaveLength,
    ToMatchPattern,
    ToNotBeNull,
    ToReference,
    ToSatisfy,
    Value,
)
from .expression_validator import LambdaExpressionValidator


class DQLTransformer(Transformer):
    """
    Transforms Lark parse tree into DQL AST nodes.

    Each method corresponds to a grammar rule and transforms the parsed
    children into appropriate AST node instances.
    """

    # Top-level structure

    def dql_file(self, children: List[Any]) -> DQLFile:
        """Transform dql_file: (include_directive | macro_definition | from_block)+ → DQLFile

        Separates includes, macros, and from_blocks into appropriate lists.
        Includes and macros will be processed by the parser, from_blocks are the main AST.
        """
        includes = []
        macros = []
        from_blocks = []

        for child in children:
            if isinstance(child, IncludeNode):
                includes.append(child)
            elif isinstance(child, MacroDefinitionNode):
                macros.append(child)
            elif isinstance(child, FromBlock):
                from_blocks.append(child)

        # Store includes and macros as metadata in DQLFile
        # The parser will process these before returning final AST
        dql_file = DQLFile(from_blocks=from_blocks)
        dql_file.includes = includes  # type: ignore
        dql_file.macros = macros  # type: ignore
        return dql_file

    def from_block(self, children: List[Any]) -> FromBlock:
        """Transform from_block: FROM model_name (expectation | macro_invocation)+ → FromBlock

        Separates expectations and macro invocations.
        Macro invocations will be expanded by the parser before final AST.
        """
        # Filter out FROM terminal token, keep only transformed nodes
        filtered = [c for c in children if not isinstance(c, Token)]
        model_name = filtered[0]

        # Separate expectations from macro invocations
        expectations = []
        macro_invocations = []

        for item in filtered[1:]:
            if isinstance(item, MacroInvocationNode):
                macro_invocations.append(item)
            else:
                expectations.append(item)

        # Store macro invocations as metadata
        from_block = FromBlock(model_name=model_name, expectations=expectations)
        from_block.macro_invocations = macro_invocations  # type: ignore
        return from_block

    def model_name(self, children: List[Token]) -> str:
        """Transform model_name: IDENTIFIER → str"""
        return str(children[0])

    # Expectation structure

    def expectation(self, children: List[Any]) -> ExpectationNode:
        """Transform expectation: EXPECT target operator_clause severity? cleaners? → ExpectationNode"""
        # Filter out EXPECT terminal token
        filtered = [c for c in children if not isinstance(c, Token)]

        target = filtered[0]
        operator = filtered[1]
        severity = None
        cleaners = []

        # Process optional severity and cleaners
        for child in filtered[2:]:
            if isinstance(child, str):  # severity level
                severity = child
            elif isinstance(child, list):  # cleaners list
                cleaners = child

        return ExpectationNode(
            target=target, operator=operator, severity=severity, cleaners=cleaners
        )

    # Target types

    def target(
        self, children: List[Union[ColumnTarget, RowTarget, ExprTarget]]
    ) -> Union[ColumnTarget, RowTarget, ExprTarget]:
        """Transform target: column_target | row_target | expr_target"""
        return children[0]

    def column_target(self, children: List[Token]) -> ColumnTarget:
        """Transform column_target: "column" "(" STRING ")" → ColumnTarget"""
        field_name = self._unquote_string(children[0])
        return ColumnTarget(field_name=field_name)

    def row_target(self, children: List[Any]) -> RowTarget:
        """Transform row_target: "row" WHERE condition → RowTarget"""
        # Filter out WHERE terminal token
        filtered = [c for c in children if not isinstance(c, Token)]
        condition = filtered[0]
        return RowTarget(condition=condition)

    def expr_target(self, children: List[Any]) -> ExprTarget:
        """Transform expr_target: expr → ExprTarget"""
        return ExprTarget(expression=children[0])

    # Operators

    def operator_clause(
        self, children: List[Any]
    ) -> Union[ToBeNull, ToNotBeNull, ToMatchPattern, ToBeBetween, ToBeIn, ToBeUnique, ToHaveLength, ToBeGreaterThan, ToBeLessThan, ToSatisfy, ToReference]:
        """Transform operator_clause: operator_name operator_args? → Operator"""
        operator = children[0]  # Already transformed by operator_name

        # If operator needs args, get them from children[1]
        if len(children) > 1:
            args = children[1]
            # Update operator with args
            if isinstance(operator, ToMatchPattern):
                return ToMatchPattern(pattern=self._unquote_string(args[0]))
            elif isinstance(operator, ToBeBetween):
                return ToBeBetween(min_value=args[0], max_value=args[1])
            elif isinstance(operator, ToBeIn):
                return ToBeIn(values=args[0])  # args[0] is already a list
            elif isinstance(operator, ToHaveLength):
                # Handle optional min/max arguments - must be integers
                min_length = args[0] if len(args) > 0 else None
                max_length = args[1] if len(args) > 1 else None

                # Validate argument types
                if min_length is not None and not isinstance(min_length, int):
                    raise ValueError(f"to_have_length min_length must be integer, got {type(min_length).__name__}")
                if max_length is not None and not isinstance(max_length, int):
                    raise ValueError(f"to_have_length max_length must be integer, got {type(max_length).__name__}")

                # Validate min <= max
                if min_length is not None and max_length is not None and min_length > max_length:
                    raise ValueError(f"to_have_length min_length ({min_length}) must be <= max_length ({max_length})")

                return ToHaveLength(min_length=min_length, max_length=max_length)
            elif isinstance(operator, ToBeGreaterThan):
                # Validate threshold is numeric
                threshold = args[0]
                if not isinstance(threshold, (int, float)):
                    raise ValueError(f"to_be_greater_than threshold must be numeric, got {type(threshold).__name__}")
                return ToBeGreaterThan(threshold=threshold)
            elif isinstance(operator, ToBeLessThan):
                # Validate threshold is numeric
                threshold = args[0]
                if not isinstance(threshold, (int, float)):
                    raise ValueError(f"to_be_less_than threshold must be numeric, got {type(threshold).__name__}")
                return ToBeLessThan(threshold=threshold)
            elif isinstance(operator, ToSatisfy):
                # Extract and validate expression string
                expression = self._unquote_string(args[0])

                # Validate the expression
                is_valid, expr_type, error_msg = LambdaExpressionValidator.validate(expression)
                if not is_valid:
                    raise ValueError(f"to_satisfy expression invalid: {error_msg}")

                return ToSatisfy(expression=expression, expr_type=expr_type)
            elif isinstance(operator, ToReference):
                # Extract target_model, target_field, and optional on_delete
                # Args: [target_model, target_field, on_delete?]
                target_model = args[0] if isinstance(args[0], str) else str(args[0])

                # target_field can be a string or a list (for composite keys)
                target_field = args[1]
                if isinstance(target_field, str):
                    target_field = self._unquote_string(target_field) if target_field.startswith('"') or target_field.startswith("'") else target_field
                elif isinstance(target_field, list):
                    # Composite key - list of field names
                    target_field = [self._unquote_string(f) if isinstance(f, str) and (f.startswith('"') or f.startswith("'")) else str(f) for f in target_field]

                # Optional on_delete parameter
                on_delete = None
                if len(args) > 2:
                    on_delete_value = args[2]
                    if isinstance(on_delete_value, str):
                        on_delete = self._unquote_string(on_delete_value) if on_delete_value.startswith('"') or on_delete_value.startswith("'") else on_delete_value
                        # Validate on_delete value
                        valid_on_delete = ["CASCADE", "SET_NULL", "RESTRICT"]
                        if on_delete.upper() not in valid_on_delete:
                            raise ValueError(f"to_reference on_delete must be one of {valid_on_delete}, got '{on_delete}'")
                        on_delete = on_delete.upper()

                return ToReference(target_model=target_model, target_field=target_field, on_delete=on_delete)

        return operator

    def operator_name(
        self, children: List[Any]
    ) -> Union[ToBeNull, ToNotBeNull, ToMatchPattern, ToBeBetween, ToBeIn, ToBeUnique, ToHaveLength, ToBeGreaterThan, ToBeLessThan, ToSatisfy, ToReference]:
        """Transform operator_name: operator_rule → Operator"""
        # children[0] is the specific operator instance
        return children[0]

    # Individual operator rules

    def to_be_null(self, children: List[Any]) -> ToBeNull:
        """Transform to_be_null: "to_be_null" → ToBeNull()"""
        return ToBeNull()

    def to_not_be_null(self, children: List[Any]) -> ToNotBeNull:
        """Transform to_not_be_null: "to_not_be_null" → ToNotBeNull()"""
        return ToNotBeNull()

    def to_match_pattern(self, children: List[Any]) -> ToMatchPattern:
        """Transform to_match_pattern: "to_match_pattern" → ToMatchPattern()"""
        # Args will be added by operator_clause
        return ToMatchPattern(pattern="")

    def to_be_between(self, children: List[Any]) -> ToBeBetween:
        """Transform to_be_between: "to_be_between" → ToBeBetween()"""
        # Args will be added by operator_clause
        return ToBeBetween(min_value=0, max_value=0)

    def to_be_in(self, children: List[Any]) -> ToBeIn:
        """Transform to_be_in: "to_be_in" → ToBeIn()"""
        # Args will be added by operator_clause
        return ToBeIn(values=[])

    def to_be_unique(self, children: List[Any]) -> ToBeUnique:
        """Transform to_be_unique: "to_be_unique" → ToBeUnique()"""
        return ToBeUnique()

    def to_have_length(self, children: List[Any]) -> ToHaveLength:
        """Transform to_have_length: "to_have_length" → ToHaveLength()"""
        # Args will be added by operator_clause
        return ToHaveLength()

    def to_be_greater_than(self, children: List[Any]) -> ToBeGreaterThan:
        """Transform to_be_greater_than: "to_be_greater_than" → ToBeGreaterThan()"""
        # Args will be added by operator_clause
        return ToBeGreaterThan(threshold=0)

    def to_be_less_than(self, children: List[Any]) -> ToBeLessThan:
        """Transform to_be_less_than: "to_be_less_than" → ToBeLessThan()"""
        # Args will be added by operator_clause
        return ToBeLessThan(threshold=0)

    def to_satisfy(self, children: List[Any]) -> ToSatisfy:
        """Transform to_satisfy: "to_satisfy" → ToSatisfy()"""
        # Args will be added by operator_clause
        return ToSatisfy(expression="")

    def to_reference(self, children: List[Any]) -> ToReference:
        """Transform to_reference: "to_reference" → ToReference()"""
        # Args will be added by operator_clause
        return ToReference(target_model="", target_field="")

    def operator_args(self, children: List[Any]) -> Any:
        """Transform operator_args: "(" arg_list ")" → pass through arg_list"""
        return children[0] if len(children) == 1 else children

    def arg_list(self, children: List[Any]) -> List[Any]:
        """Transform arg_list: arg ("," arg)* → List[Any]"""
        return children

    def arg(self, children: List[Any]) -> Any:
        """Transform arg: STRING | NUMBER | list | IDENTIFIER → value"""
        value = children[0]
        if isinstance(value, Token):
            if value.type == "STRING":
                return self._unquote_string(value)
            elif value.type == "NUMBER":
                return self._parse_number(value)
            elif value.type == "IDENTIFIER":
                return str(value)  # Return identifier as string
        return value  # Already transformed list

    def list(self, children: List[Any]) -> List[Any]:
        """Transform list: "[" arg_list "]" → List[Any]"""
        return children[0] if children else []

    # Severity

    def severity_clause(self, children: List[Any]) -> str:
        """Transform severity_clause: "severity" severity_level → str"""
        # Filter out "severity" terminal
        filtered = [
            c for c in children if not isinstance(c, Token) or c.type.startswith("SEVERITY_")
        ]
        return filtered[0] if filtered else children[0]

    def severity_level(self, children: List[Token]) -> str:
        """Transform severity_level: SEVERITY_CRITICAL | SEVERITY_WARNING | SEVERITY_INFO → str"""
        severity_token = children[0]
        # Extract the severity level from token type
        if severity_token.type == "SEVERITY_CRITICAL":
            return "critical"
        elif severity_token.type == "SEVERITY_WARNING":
            return "warning"
        elif severity_token.type == "SEVERITY_INFO":
            return "info"
        return str(severity_token)

    # Cleaners

    def cleaner_clause(self, children: List[CleanerNode]) -> List[CleanerNode]:
        """Transform cleaner_clause: cleaner_call+ → List[CleanerNode]"""
        return children

    def cleaner_call(self, children: List[Any]) -> CleanerNode:
        """Transform cleaner_call: ON_FAILURE CLEAN_WITH "(" STRING args? ")" → CleanerNode"""
        # Filter out ON_FAILURE and CLEAN_WITH terminals
        filtered = [c for c in children if not isinstance(c, Token) or c.type == "STRING"]
        cleaner_name = self._unquote_string(filtered[0])
        args = filtered[1] if len(filtered) > 1 else []
        return CleanerNode(cleaner_name=cleaner_name, args=args)

    def cleaner_args(self, children: List[Any]) -> List[Any]:
        """Transform cleaner_args: "," arg_list → List[Any]"""
        return children[0]

    # Row-level conditions

    def condition(self, children: List[Any]) -> Union[Comparison, LogicalExpr]:
        """Transform condition: comparison | logical_expr | "(" condition ")" → Condition"""
        return children[0]

    def comparison(self, children: List[Any]) -> Comparison:
        """Transform comparison: expr COMPARATOR expr → Comparison"""
        left = children[0]
        operator = str(children[1])
        right = children[2]
        return Comparison(left=left, operator=operator, right=right)

    def logical_expr(self, children: List[Any]) -> LogicalExpr:
        """Transform logical_expr: condition (AND|OR) condition | NOT condition → LogicalExpr"""
        if len(children) == 1:  # NOT condition (NOT is filtered out)
            operator = "NOT"
            operands = [children[0]]
        elif len(children) == 2 and isinstance(children[0], Token):  # NOT token, condition
            operator = "NOT"
            operands = [children[1]]
        else:  # condition (AND|OR) condition
            # Filter to get: condition, operator_token, condition
            filtered = [c for c in children if not isinstance(c, Token) or c.type in ("AND", "OR")]
            left = filtered[0] if not isinstance(filtered[0], Token) else filtered[1]
            right = filtered[2] if len(filtered) > 2 else filtered[1]
            # Find the operator token
            op_token = next(
                (c for c in filtered if isinstance(c, Token) and c.type in ("AND", "OR")), None
            )
            operator = op_token.type if op_token else "AND"
            operands = [left, right]
        return LogicalExpr(operator=operator, operands=operands)

    # Expressions - with proper precedence handling

    # Arithmetic operations (from grammar aliases)
    def add(self, children: List[Any]) -> ArithmeticExpr:
        """Transform add: expr "+" term → ArithmeticExpr"""
        return ArithmeticExpr(operator="+", left=children[0], right=children[1])

    def subtract(self, children: List[Any]) -> ArithmeticExpr:
        """Transform subtract: expr "-" term → ArithmeticExpr"""
        return ArithmeticExpr(operator="-", left=children[0], right=children[1])

    def multiply(self, children: List[Any]) -> ArithmeticExpr:
        """Transform multiply: term "*" factor → ArithmeticExpr"""
        return ArithmeticExpr(operator="*", left=children[0], right=children[1])

    def divide(self, children: List[Any]) -> ArithmeticExpr:
        """Transform divide: term "/" factor → ArithmeticExpr"""
        return ArithmeticExpr(operator="/", left=children[0], right=children[1])

    def modulo(self, children: List[Any]) -> ArithmeticExpr:
        """Transform modulo: term "%" factor → ArithmeticExpr"""
        return ArithmeticExpr(operator="%", left=children[0], right=children[1])

    def parentheses(self, children: List[Any]) -> Any:
        """Transform parentheses: "(" expr ")" → expr (pass through)"""
        return children[0]

    # Atoms (literals and references)
    def number_literal(self, children: List[Token]) -> Value:
        """Transform number_literal: NUMBER → Value"""
        return Value(value=self._parse_number(children[0]))

    def string_literal(self, children: List[Token]) -> Value:
        """Transform string_literal: STRING → Value"""
        return Value(value=self._unquote_string(children[0]))

    def null_literal(self, children: List[Token]) -> Value:
        """Transform null_literal: NULL → Value(None)"""
        return Value(value=None)

    def field_reference(self, children: List[FieldRef]) -> FieldRef:
        """Transform field_reference: field_ref → FieldRef"""
        return children[0]

    def field_ref(self, children: List[Token]) -> FieldRef:
        """Transform field_ref: FIELD_NAME → FieldRef"""
        return FieldRef(field_name=str(children[0]))

    def value(self, children: List[Token]) -> Value:
        """Transform value: STRING | NUMBER | NULL → Value"""
        token = children[0]
        if token.type == "STRING":
            return Value(value=self._unquote_string(token))
        elif token.type == "NUMBER":
            return Value(value=self._parse_number(token))
        elif token.type == "NULL":
            return Value(value=None)
        return Value(value=str(token))

    # Functions

    def function_call(self, children: List[FunctionCall]) -> FunctionCall:
        """Transform function_call: string_func | date_func | concat_func → FunctionCall"""
        return children[0]

    def string_func(self, children: List[FunctionCall]) -> FunctionCall:
        """Transform string_func: upper_func | lower_func | trim_func | length_func → FunctionCall"""
        return children[0]

    def date_func(self, children: List[FunctionCall]) -> FunctionCall:
        """Transform date_func: year_func | month_func | day_func | age_func → FunctionCall"""
        return children[0]

    # String functions
    def upper_func(self, children: List[Any]) -> FunctionCall:
        """Transform upper_func: "UPPER" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="UPPER", args=[children[0]])

    def lower_func(self, children: List[Any]) -> FunctionCall:
        """Transform lower_func: "LOWER" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="LOWER", args=[children[0]])

    def trim_func(self, children: List[Any]) -> FunctionCall:
        """Transform trim_func: "TRIM" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="TRIM", args=[children[0]])

    def length_func(self, children: List[Any]) -> FunctionCall:
        """Transform length_func: "LENGTH" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="LENGTH", args=[children[0]])

    # Date functions
    def year_func(self, children: List[Any]) -> FunctionCall:
        """Transform year_func: "YEAR" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="YEAR", args=[children[0]])

    def month_func(self, children: List[Any]) -> FunctionCall:
        """Transform month_func: "MONTH" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="MONTH", args=[children[0]])

    def day_func(self, children: List[Any]) -> FunctionCall:
        """Transform day_func: "DAY" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="DAY", args=[children[0]])

    def age_func(self, children: List[Any]) -> FunctionCall:
        """Transform age_func: "AGE" "(" expr ")" → FunctionCall"""
        return FunctionCall(function_name="AGE", args=[children[0]])

    # CONCAT function (variable arguments)
    def concat_func(self, children: List[Any]) -> FunctionCall:
        """Transform concat_func: "CONCAT" "(" expr ("," expr)+ ")" → FunctionCall"""
        return FunctionCall(function_name="CONCAT", args=children)

    # INCLUDE and MACRO support (Story 1.9)

    def include_directive(self, children: List[Any]) -> IncludeNode:
        """Transform include_directive: INCLUDE STRING → IncludeNode"""
        file_path = self._unquote_string(children[0])
        return IncludeNode(file_path=file_path)

    def macro_definition(self, children: List[Any]) -> MacroDefinitionNode:
        """Transform macro_definition: DEFINE MACRO MACRO_NAME "(" parameter_list? ")" AS "{" expectation+ "}" → MacroDefinitionNode

        Args:
            children: [DEFINE, MACRO, MACRO_NAME, parameter_list?, AS, expectation+]
                - Terminals: DEFINE, MACRO, AS (filtered out)
                - MACRO_NAME token
                - parameter_list (optional)
                - expectation nodes
        """
        from lark import Token

        # Filter out terminal keywords (DEFINE, MACRO, AS)
        filtered = [c for c in children if not isinstance(c, Token) or c.type == "MACRO_NAME"]

        # First item should be MACRO_NAME
        name = str(filtered[0])  # MACRO_NAME token

        # Separate parameters from expectations
        # If parameter_list exists, it will be filtered[1]
        # Expectations come after
        if len(filtered) > 1 and isinstance(filtered[1], list):
            # Has parameters
            parameters = filtered[1]  # parameter_list
            expectations = filtered[2:]  # Rest are expectations
        else:
            # No parameters
            parameters = []
            expectations = filtered[1:]  # All remaining are expectations

        return MacroDefinitionNode(name=name, parameters=parameters, expectations=expectations)

    def parameter_list(self, children: List[Any]) -> List[str]:
        """Transform parameter_list: IDENTIFIER ("," IDENTIFIER)* → List[str]"""
        return [str(param) for param in children]

    def macro_invocation(self, children: List[Any]) -> MacroInvocationNode:
        """Transform macro_invocation: USE MACRO MACRO_NAME "(" macro_args? ")" → MacroInvocationNode

        Args:
            children: [USE, MACRO, MACRO_NAME, macro_args?]
                - children[0-1]: USE, MACRO terminals (filtered out)
                - children[2]: MACRO_NAME token
                - children[3]: macro_args (if present)
        """
        # Filter out terminal tokens (USE, MACRO)
        from lark import Token
        filtered = [c for c in children if not isinstance(c, Token) or c.type == "MACRO_NAME"]

        # First filtered item should be MACRO_NAME, second should be macro_args (if present)
        name = str(filtered[0])  # MACRO_NAME token
        arguments = filtered[1] if len(filtered) > 1 else []
        return MacroInvocationNode(name=name, arguments=arguments)

    def macro_args(self, children: List[Any]) -> List[Any]:
        """Transform macro_args: arg ("," arg)* → List[Any]"""
        return children  # Already transformed arg nodes (STRING, NUMBER, IDENTIFIER, list)

    # Helper methods

    def _unquote_string(self, token: Token) -> str:
        """Remove surrounding quotes from STRING token"""
        s = str(token)
        if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
            return s[1:-1]
        return s

    def _parse_number(self, token: Token) -> Union[int, float]:
        """Parse NUMBER token to int or float"""
        s = str(token)
        if "." in s:
            return float(s)
        return int(s)
