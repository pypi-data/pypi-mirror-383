"""
DQL Parser: Parses Data Quality Language into Abstract Syntax Trees.

The DQLParser class provides the main entry point for parsing DQL code.
It uses Lark for parsing with a LALR(1) parser for performance, then
transforms the parse tree into strongly-typed AST nodes.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union

from lark import Lark, UnexpectedInput, UnexpectedToken

from .ast_nodes import DQLFile, FromBlock, MacroInvocationNode
from .cache import ParserCache
from .error_collector import DQLErrorCollector
from .error_messages import enhance_lark_error_message
from .exceptions import (
    DQLSyntaxError,
    InvalidModelNameError,
    MissingFromClauseError,
    ReservedKeywordError,
)
from .file_resolver import FileResolver
from .macro_registry import MacroRegistry
from .parse_result import ParseResult
from .transformer import DQLTransformer


class DQLParser:
    """
    Parser for Data Quality Language (DQL).

    Parses DQL text into a DQLFile AST node containing all FROM blocks
    and expectations. Provides detailed error messages with line/column
    information.

    Example:
        >>> parser = DQLParser()
        >>> dql = '''
        ... from Customer
        ... expect column("email") to_not_be_null severity critical
        ... '''
        >>> ast = parser.parse(dql)
        >>> print(ast.from_blocks[0].model_name)
        Customer
    """

    # Reserved keywords from DQL specification
    RESERVED_KEYWORDS = {
        # Current MVP keywords
        "from",
        "expect",
        "column",
        "row",
        "where",
        "severity",
        "to_be_null",
        "to_not_be_null",
        "to_match_pattern",
        "to_be_between",
        "to_be_in",
        "to_be_unique",
        "on_failure",
        "clean_with",
        "critical",
        "warning",
        "info",
        "null",
        # Future reserved keywords
        "to_be_greater_than",
        "to_be_less_than",
        "to_contain",
        "to_start_with",
        "to_end_with",
        "percentile",
        "mean",
        "median",
        "stddev",
        "count",
        "sum",
        "min",
        "max",
        "avg",
        "group_by",
        "having",
        "order_by",
        "limit",
        "offset",
        "join",
        "inner",
        "left",
        "right",
        "outer",
        "on",
        "as",
        "distinct",
    }

    # PascalCase regex for model names
    PASCALCASE_REGEX = re.compile(r"^[A-Z][a-zA-Z0-9_]*$")

    def __init__(
        self,
        max_errors: int = 10,
        enable_recovery: bool = False,
        cache: ParserCache = None,
        enable_cache: bool = True,
        base_path: Path = None,
    ):
        """
        Initialize DQL parser with Lark grammar.

        Loads grammar from dql_parser/grammar.lark and configures LALR(1)
        parser with position propagation for error reporting.

        Args:
            max_errors: Maximum number of errors to collect during recovery (default 10)
            enable_recovery: Enable error recovery mode (default False for backward compatibility)
            cache: Optional ParserCache instance (creates default if None and enable_cache=True)
            enable_cache: Enable caching (default True, Story 1.8 AC2)
            base_path: Base path for resolving INCLUDE directives (default: current working directory)
        """
        # Find grammar file relative to this module
        grammar_path = Path(__file__).parent / "grammar.lark"

        # Initialize Lark parser with LALR for speed
        self._lark = Lark.open(
            grammar_path,
            start="dql_file",
            parser="lalr",  # LALR(1) for performance
            propagate_positions=True,  # Enable line/column tracking
        )

        # Initialize transformer
        self._transformer = DQLTransformer()

        # Error recovery settings
        self.max_errors = max_errors
        self.enable_recovery = enable_recovery

        # Caching support (Story 1.8)
        self.enable_cache = enable_cache
        self._cache = cache if cache is not None else (ParserCache() if enable_cache else None)

        # INCLUDE and MACRO support (Story 1.9)
        self.file_resolver = FileResolver(base_path or Path.cwd())
        self.macro_registry = MacroRegistry()

    def parse(self, dql_text: str) -> DQLFile:
        """
        Parse DQL text into AST.

        This method will use error recovery if enabled, returning a ParseResult.
        For backward compatibility, if no errors are found, returns DQLFile directly.
        If errors are found and recovery is disabled, raises exception immediately.

        Args:
            dql_text: DQL source code as string

        Returns:
            DQLFile: Root AST node containing all FROM blocks (if no errors)
            ParseResult: Result with AST and errors (if enable_recovery=True)

        Raises:
            DQLSyntaxError: If parsing fails and recovery is disabled
            DQLMultipleErrors: If multiple errors found and recovery is disabled
            MissingFromClauseError: If expectation appears without FROM
            InvalidModelNameError: If model name is not PascalCase
            ReservedKeywordError: If reserved keyword used as identifier

        Example:
            >>> parser = DQLParser()
            >>> ast = parser.parse('from Customer\\nexpect column("email") to_not_be_null')
            >>> len(ast.from_blocks)
            1
        """
        if self.enable_recovery:
            result = self.parse_with_recovery(dql_text)
            # For backward compatibility, return DQLFile if no errors
            if not result.has_errors():
                return result.ast
            # If errors exist, return ParseResult for caller to handle
            return result
        else:
            # Original behavior: fail on first error
            return self._parse_without_recovery(dql_text)

    def _parse_without_recovery(self, dql_text: str) -> DQLFile:
        """
        Parse DQL text without error recovery (original behavior).

        Args:
            dql_text: DQL source code as string

        Returns:
            DQLFile: Root AST node

        Raises:
            DQLSyntaxError: If parsing fails
        """
        # Check cache first (Story 1.8 AC2)
        if self.enable_cache and self._cache is not None:
            cached_ast = self._cache.get(dql_text)
            if cached_ast is not None:
                return cached_ast

        try:
            # Parse with Lark
            tree = self._lark.parse(dql_text)

            # Transform to AST
            ast = self._transformer.transform(tree)

            # Process INCLUDE directives and MACRO definitions/invocations (Story 1.9)
            ast = self._process_includes_and_macros(ast)

            # Validate AST (FROM clause presence, model names, keywords)
            self._validate_ast(ast, dql_text)

            # Store in cache (Story 1.8 AC2)
            if self.enable_cache and self._cache is not None:
                self._cache.set(dql_text, ast)

            return ast

        except UnexpectedInput as e:
            # Lark parsing error - convert to DQLSyntaxError
            self._raise_syntax_error(e, dql_text)

        except (
            DQLSyntaxError,
            MissingFromClauseError,
            InvalidModelNameError,
            ReservedKeywordError,
        ):
            # Our custom exceptions - re-raise as-is
            raise

        except Exception as e:
            # Unexpected error - wrap in DQLSyntaxError
            raise DQLSyntaxError(
                message=f"Unexpected parsing error: {str(e)}",
                line=0,
                column=0,
                context="",
            ) from e

    def parse_with_recovery(self, dql_text: str, file_path: str = None) -> ParseResult:
        """
        Parse DQL text with error recovery enabled.

        Attempts to parse the entire file. If errors occur, continues parsing
        and collects all errors. Returns both valid AST nodes and errors.

        Strategy:
        1. Try parsing the entire file normally
        2. If successful, return ParseResult with no errors
        3. If fails, split into FROM blocks and parse each independently
        4. Collect all errors and valid blocks

        Args:
            dql_text: DQL source code as string
            file_path: Optional file path for error reporting

        Returns:
            ParseResult: Result containing AST and list of errors

        Example:
            >>> parser = DQLParser(enable_recovery=True)
            >>> result = parser.parse_with_recovery(dql_with_errors)
            >>> if result.has_errors():
            ...     for error in result.errors:
            ...         print(error)
            >>> print(f"Parsed {len(result.ast.from_blocks)} valid blocks")
        """
        # Initialize error collector
        collector = DQLErrorCollector(max_errors=self.max_errors)

        # First, try parsing the entire file normally
        try:
            ast = self._parse_without_recovery(dql_text)
            return ParseResult(ast=ast, errors=[], file_path=file_path)
        except Exception:
            # Parsing failed, switch to recovery mode
            pass

        # Split DQL into FROM blocks for independent parsing
        from_blocks = []
        block_errors = []

        # Parse line by line to identify FROM blocks
        lines = dql_text.splitlines()
        current_block_lines = []
        current_block_start = 0

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check if this is a FROM statement (case-insensitive)
            if re.match(r"^from\s+\w+", stripped, re.IGNORECASE):
                # If we have a previous block, try to parse it
                if current_block_lines:
                    block_text = "\n".join(current_block_lines)
                    block_result = self._parse_single_block(
                        block_text, current_block_start, collector
                    )
                    if block_result:
                        from_blocks.append(block_result)

                    if collector.is_at_limit():
                        break

                # Start new block
                current_block_lines = [line]
                current_block_start = i
            elif current_block_lines:
                # Continue current block
                current_block_lines.append(line)
            # Ignore lines before first FROM block

        # Parse the last block if exists
        if current_block_lines and not collector.is_at_limit():
            block_text = "\n".join(current_block_lines)
            block_result = self._parse_single_block(
                block_text, current_block_start, collector
            )
            if block_result:
                from_blocks.append(block_result)

        # Create DQLFile with collected blocks
        ast = DQLFile(from_blocks=from_blocks)

        return ParseResult(
            ast=ast, errors=collector.get_sorted_errors(), file_path=file_path
        )

    def _parse_single_block(
        self, block_text: str, start_line: int, collector: DQLErrorCollector
    ) -> FromBlock:
        """
        Parse a single FROM block with error recovery.

        Args:
            block_text: Text of the FROM block
            start_line: Starting line number in original file
            collector: Error collector to add errors to

        Returns:
            FromBlock if parsing succeeds, None otherwise
        """
        try:
            # Parse the block
            tree = self._lark.parse(block_text)
            ast = self._transformer.transform(tree)

            # Should have exactly one FROM block
            if len(ast.from_blocks) == 1:
                return ast.from_blocks[0]
            return None

        except UnexpectedInput as e:
            # Adjust line numbers to account for block position
            line = getattr(e, "line", 1) + start_line - 1
            column = getattr(e, "column", 0)
            context = self._get_line(block_text, getattr(e, "line", 1))

            # Extract message
            message = str(e)
            if isinstance(e, UnexpectedToken):
                expected = getattr(e, "expected", set())
                if expected:
                    expected_list = ", ".join(sorted(expected)[:5])
                    message = f"Unexpected token. Expected one of: {expected_list}"

            # Create error and add to collector
            error = DQLSyntaxError(
                message=message, line=line, column=column, context=context
            )
            collector.add_error(error)
            return None

        except Exception as e:
            # Unexpected error
            error = DQLSyntaxError(
                message=f"Unexpected error: {str(e)}",
                line=start_line,
                column=0,
                context="",
            )
            collector.add_error(error)
            return None

    def parse_file(self, filepath: Union[str, Path]) -> DQLFile:
        """
        Parse DQL file and return AST.

        Args:
            filepath: Path to .dql file

        Returns:
            DQLFile: Root AST node

        Raises:
            DQLSyntaxError: If syntax is invalid
            FileNotFoundError: If file doesn't exist

        Example:
            >>> parser = DQLParser()
            >>> ast = parser.parse_file('expectations/customer.dql')
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"DQL file not found: {filepath}")

        dql_text = filepath.read_text(encoding="utf-8")
        return self.parse(dql_text)

    def _validate_ast(self, ast: DQLFile, dql_text: str) -> None:
        """
        Validate AST for semantic correctness.

        Checks:
        1. FROM clause exists
        2. Model names are PascalCase
        3. No reserved keywords used as identifiers

        Args:
            ast: Parsed AST to validate
            dql_text: Original DQL text for context in error messages

        Raises:
            MissingFromClauseError: If no FROM blocks found
            InvalidModelNameError: If model name not PascalCase
            ReservedKeywordError: If reserved keyword used as identifier
        """
        # Check FROM clause exists
        if not ast.from_blocks:
            raise MissingFromClauseError(line=1, column=1, context=self._get_line(dql_text, 1))

        # Validate each FROM block
        for block in ast.from_blocks:
            # Validate model name is PascalCase
            if not self.PASCALCASE_REGEX.match(block.model_name):
                # Find line number for this model name
                line_num = self._find_model_line(dql_text, block.model_name)
                context = self._get_line(dql_text, line_num)
                # Column is position after "from " keyword
                col_num = context.lower().index("from") + 6

                raise InvalidModelNameError(
                    model_name=block.model_name,
                    line=line_num,
                    column=col_num,
                    context=context,
                )

            # Check if model name is a reserved keyword
            if block.model_name.lower() in self.RESERVED_KEYWORDS:
                line_num = self._find_model_line(dql_text, block.model_name)
                context = self._get_line(dql_text, line_num)
                col_num = context.lower().index("from") + 6

                raise ReservedKeywordError(
                    keyword=block.model_name,
                    line=line_num,
                    column=col_num,
                    context=context,
                )

    def _raise_syntax_error(self, lark_error: UnexpectedInput, dql_text: str) -> None:
        """
        Convert Lark parsing error to DQLSyntaxError with enhanced error message.

        Uses enhance_lark_error_message to provide intelligent suggestions
        for typos and common mistakes.

        Args:
            lark_error: Lark exception with line/column info
            dql_text: Original DQL text for context

        Raises:
            DQLSyntaxError: Always raises with formatted error message
        """
        line = getattr(lark_error, "line", 0)
        column = getattr(lark_error, "column", 0)
        context = self._get_line(dql_text, line)

        # Extract expected tokens for better error message
        message = str(lark_error)
        unexpected_token = None

        # Check for common error patterns and provide helpful messages
        if isinstance(lark_error, UnexpectedToken):
            unexpected_token = getattr(lark_error, "token", None)
            if unexpected_token:
                unexpected_token = str(unexpected_token.value) if hasattr(unexpected_token, 'value') else str(unexpected_token)

            expected = getattr(lark_error, "expected", set())
            if expected:
                expected_list = ", ".join(sorted(expected)[:5])  # Show first 5
                message = f"Unexpected token. Expected one of: {expected_list}"

        # Use enhanced error message builder
        enhanced_message = enhance_lark_error_message(
            error_message=message,
            line=line,
            column=column,
            context=context,
            unexpected_token=unexpected_token,
        )

        # Create and raise error with enhanced message
        # We override the formatted message by passing it as base message
        # and using use_enhanced_messages=False to prevent double formatting
        error = DQLSyntaxError(
            message=enhanced_message,
            line=line,
            column=column,
            context=context,
            use_enhanced_messages=False,
        )
        # Override __str__ to return enhanced message directly
        error.get_formatted_message = lambda: enhanced_message
        raise error

    def _get_line(self, text: str, line_num: int) -> str:
        """
        Extract a specific line from text.

        Args:
            text: Full text
            line_num: Line number (1-indexed)

        Returns:
            The line at line_num, or empty string if out of range
        """
        lines = text.splitlines()
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1]
        return ""

    def _find_model_line(self, text: str, model_name: str) -> int:
        """
        Find the line number where a model name appears after FROM keyword.

        Args:
            text: Full DQL text
            model_name: Model name to find

        Returns:
            Line number (1-indexed) where model appears, or 1 if not found
        """
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            # Look for "from ModelName" pattern (case-insensitive for "from")
            if re.search(rf"\bfrom\s+{re.escape(model_name)}\b", line, re.IGNORECASE):
                return i
        return 1

    def parse_file(self, file_path: Union[str, Path]) -> DQLFile:
        """
        Parse DQL file with INCLUDE resolution and MACRO expansion (Story 1.9).

        This method recursively loads INCLUDE directives and expands MACRO invocations.

        Args:
            file_path: Path to DQL file

        Returns:
            DQLFile: Root AST node with all includes resolved and macros expanded

        Raises:
            FileNotFoundError: If file doesn't exist
            CircularIncludeError: If circular include detected
            IncludeDepthError: If include depth exceeds limit
            DQLSyntaxError: If parsing fails

        Example:
            >>> parser = DQLParser(base_path=Path("/project/dql"))
            >>> ast = parser.parse_file("/project/dql/models/customer.dql")
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"DQL file not found: {file_path}")

        # Read file content
        dql_text = file_path.read_text(encoding="utf-8")

        # Parse with include resolution
        self.file_resolver.push_file(file_path)
        try:
            ast = self.parse(dql_text)
            return ast
        finally:
            self.file_resolver.pop_file()

    def _process_includes_and_macros(self, ast: DQLFile) -> DQLFile:
        """
        Process INCLUDE directives and MACRO definitions/invocations (Story 1.9).

        1. Collect MACRO definitions
        2. Expand MACRO invocations in each from_block
        3. Remove include/macro nodes from AST (they've been processed)

        Args:
            ast: DQLFile with includes and macros metadata

        Returns:
            DQLFile: Processed AST with macros expanded
        """
        # Phase 1: Register all MACRO definitions
        macros = getattr(ast, "macros", [])
        for macro_def in macros:
            self.macro_registry.define(
                macro_def.name,
                macro_def.parameters,
                macro_def.expectations
            )

        # Phase 2: Expand MACRO invocations in each from_block
        for from_block in ast.from_blocks:
            macro_invocations = getattr(from_block, "macro_invocations", [])
            if macro_invocations:
                # Expand each macro invocation
                expanded_expectations = []
                for invocation in macro_invocations:
                    expanded = self.macro_registry.expand(
                        invocation.name,
                        invocation.arguments
                    )
                    expanded_expectations.extend(expanded)

                # Add expanded expectations to from_block
                from_block.expectations.extend(expanded_expectations)

        # Phase 3: Clean up metadata (includes and macros have been processed)
        # Note: We keep from_blocks as-is, they now have expanded expectations
        return ast

    def get_cache_stats(self) -> dict:
        """
        Get cache statistics (Story 1.8 AC5).

        Returns:
            Dictionary with cache stats or empty dict if caching disabled
        """
        if self.enable_cache and self._cache is not None:
            return self._cache.get_stats()
        return {}

    def clear_cache(self):
        """
        Clear parser cache.

        Useful for testing or when memory is constrained.
        """
        if self._cache is not None:
            self._cache.clear()


# Convenience functions


def parse_dql(dql_text: str) -> DQLFile:
    """
    Convenience function to parse DQL text.

    Args:
        dql_text: DQL source code as string

    Returns:
        DQLFile: Root AST node

    Example:
        >>> from dql_parser import parse_dql
        >>> ast = parse_dql('from Customer\\nexpect column("email") to_not_be_null')
    """
    parser = DQLParser()
    return parser.parse(dql_text)


def parse_dql_file(filepath: Union[str, Path]) -> DQLFile:
    """
    Convenience function to parse DQL file.

    Args:
        filepath: Path to .dql file

    Returns:
        DQLFile: Root AST node

    Example:
        >>> from dql_parser import parse_dql_file
        >>> ast = parse_dql_file('expectations/customer.dql')
    """
    parser = DQLParser()
    return parser.parse_file(filepath)
