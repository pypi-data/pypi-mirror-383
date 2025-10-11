"""
dql-parser: Pure Python parser for Data Quality Language (DQL).

This package provides a standalone DQL parser with zero dependencies on Django
or any web framework. It parses DQL text into Abstract Syntax Trees (AST) composed
of strongly-typed dataclass nodes.

Example:
    >>> from dql_parser import DQLParser
    >>> parser = DQLParser()
    >>> ast = parser.parse('''
    ... from Customer
    ... expect column("email") to_not_be_null severity critical
    ... ''')
    >>> print(ast.from_blocks[0].model_name)
    Customer
"""

__version__ = "0.2.0"

# Parser
from .parser import DQLParser, parse_dql, parse_dql_file

# Cache (Story 1.8)
from .cache import ParserCache, FileCache

# INCLUDE and MACRO support (Story 1.9)
from .file_resolver import FileResolver
from .macro_registry import MacroRegistry

# Parse Result
from .parse_result import ParseResult

# Error Collector
from .error_collector import DQLErrorCollector

# AST Nodes
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
    LogicalExpr,
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

# Exceptions
from .exceptions import (
    DQLMultipleErrors,
    DQLSyntaxError,
    InvalidFieldError,
    InvalidModelNameError,
    InvalidOperatorError,
    MissingFromClauseError,
    ReservedKeywordError,
)

__all__ = [
    # Version
    "__version__",
    # Parser
    "DQLParser",
    "parse_dql",
    "parse_dql_file",
    # Cache
    "ParserCache",
    "FileCache",
    # INCLUDE and MACRO
    "FileResolver",
    "MacroRegistry",
    # Parse Result
    "ParseResult",
    # Error Collector
    "DQLErrorCollector",
    # AST Nodes - Core
    "DQLFile",
    "FromBlock",
    "ExpectationNode",
    # AST Nodes - Targets
    "ColumnTarget",
    "RowTarget",
    "ExprTarget",
    # AST Nodes - Operators
    "ToBeNull",
    "ToNotBeNull",
    "ToMatchPattern",
    "ToBeBetween",
    "ToBeIn",
    "ToBeUnique",
    "ToHaveLength",
    "ToBeGreaterThan",
    "ToBeLessThan",
    "ToSatisfy",
    "ToReference",
    # AST Nodes - Conditions/Expressions
    "Comparison",
    "LogicalExpr",
    "ColumnRef",
    "FieldRef",
    "Value",
    "FunctionCall",
    "ArithmeticExpr",
    # AST Nodes - Cleaners
    "CleanerNode",
    # Exceptions
    "DQLSyntaxError",
    "DQLMultipleErrors",
    "InvalidOperatorError",
    "InvalidFieldError",
    "MissingFromClauseError",
    "InvalidModelNameError",
    "ReservedKeywordError",
]
