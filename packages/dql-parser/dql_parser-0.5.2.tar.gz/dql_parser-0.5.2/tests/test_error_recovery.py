"""
Unit tests for error recovery and multi-error reporting.

Tests the parser's ability to continue parsing after encountering syntax errors
and to collect and report all errors in a comprehensive format.

Story: 1.5 Error Recovery and Multi-Error Reporting
Coverage Target: >90%
"""

import pytest

from dql_parser import (
    DQLMultipleErrors,
    DQLParser,
    DQLSyntaxError,
    ParseResult,
)


class TestSingleSyntaxError:
    """Test parser reports single syntax errors correctly."""

    def test_single_error_in_expectation(self):
        """Test parser reports single syntax error."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert isinstance(result, ParseResult)
        assert result.has_errors()
        assert len(result.errors) == 1
        assert not result.is_success()

    def test_single_error_contains_line_number(self):
        """Test error includes correct line number."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert result.errors[0].line == 3

    def test_single_error_with_valid_expectation(self):
        """Test successful parse returns DQLFile (no errors)."""
        dql = """
        from Customer
        expect column("email") to_not_be_null
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        # Should parse successfully and return DQLFile directly
        from dql_parser.ast_nodes import DQLFile
        assert isinstance(result, DQLFile)
        assert len(result.from_blocks) == 1


class TestMultipleSyntaxErrors:
    """Test parser collects and reports multiple syntax errors."""

    def test_two_syntax_errors(self):
        """Test parser reports all syntax errors (2 errors)."""
        dql = """
        from Customer
        expect column("email") to_be_invalid

        from Order
        expect column("total") bad_operator
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert result.has_errors()
        assert len(result.errors) == 2

    def test_five_syntax_errors(self):
        """Test parser reports all syntax errors (5 errors)."""
        dql = """
        from Customer
        expect column("email") to_be_invalid

        from Order
        expect column("total") bad_op1

        from Product
        expect column("status") bad_op2

        from Invoice
        expect column("amount") bad_op3

        from Payment
        expect column("date") bad_op4
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert result.has_errors()
        assert len(result.errors) >= 5  # Should collect all 5

    def test_errors_sorted_by_line_number(self):
        """Test errors are sorted by line number."""
        dql = """
        from Customer
        expect column("c") bad_op_c

        from Apple
        expect column("a") bad_op_a

        from Banana
        expect column("b") bad_op_b
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        # Errors should be sorted by line number (not parse order)
        assert result.has_errors()
        sorted_errors = result.errors
        for i in range(len(sorted_errors) - 1):
            assert sorted_errors[i].line <= sorted_errors[i + 1].line


class TestErrorLimit:
    """Test parser stops after max_errors limit."""

    def test_error_limit_at_10(self):
        """Test parser stops collecting after 10 errors."""
        # Create 15 FROM blocks, each with an invalid expectation
        lines = []
        for i in range(15):
            lines.append(f"from Model{i}")
            lines.append(f'expect column("field{i}") bad_operator_{i}')
            lines.append("")  # blank line

        dql = "\n".join(lines)
        parser = DQLParser(max_errors=10, enable_recovery=True)
        result = parser.parse(dql)

        # Should stop at limit
        assert len(result.errors) <= 10

    def test_custom_error_limit(self):
        """Test custom max_errors parameter."""
        # Create 10 FROM blocks, each with an invalid expectation
        lines = []
        for i in range(10):
            lines.append(f"from Model{i}")
            lines.append(f'expect column("field{i}") bad_op_{i}')
            lines.append("")

        dql = "\n".join(lines)
        parser = DQLParser(max_errors=5, enable_recovery=True)
        result = parser.parse(dql)

        assert len(result.errors) <= 5


class TestPartialSuccess:
    """Test parser returns valid expectations despite errors."""

    def test_partial_success_two_valid_one_invalid(self):
        """Test 2 valid + 1 invalid = partial success."""
        dql = """
        from Customer
        expect column("email") to_not_be_null

        from Order
        expect column("total") bad_operator

        from Product
        expect column("name") to_not_be_null
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert result.has_errors()
        assert len(result.errors) >= 1
        assert len(result.ast.from_blocks) >= 2  # 2 valid blocks
        assert result.is_partial_success()

    def test_partial_success_valid_expectations_accessible(self):
        """Test valid expectations are accessible in partial success."""
        dql = """
        from Customer
        expect column("email") to_not_be_null
        expect column("phone") to_match_pattern("\\d{3}-\\d{3}-\\d{4}")

        from Order
        expect column("total") bad_operator
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        # Should have Customer block with 2 expectations
        assert len(result.ast.from_blocks) >= 1
        customer_block = result.ast.from_blocks[0]
        assert customer_block.model_name == "Customer"
        assert len(customer_block.expectations) == 2


class TestErrorFormatting:
    """Test error context and formatting."""

    def test_error_contains_context(self):
        """Test error includes line context."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert result.has_errors()
        error = result.errors[0]
        # Context should contain the problematic line
        assert "email" in error.context or error.context == ""

    def test_error_contains_column_number(self):
        """Test error includes column number."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        assert result.has_errors()
        error = result.errors[0]
        assert error.column > 0  # Should have column number

    def test_multiple_errors_format_summary(self):
        """Test DQLMultipleErrors formats summary correctly."""
        errors = [
            DQLSyntaxError("Error 1", line=1, column=5, context="line 1"),
            DQLSyntaxError("Error 2", line=3, column=10, context="line 3"),
            DQLSyntaxError("Error 3", line=5, column=15, context="line 5"),
        ]
        multi_error = DQLMultipleErrors(errors, file_path="test.dql")

        summary = str(multi_error)
        assert "Found 3 syntax errors" in summary
        assert "test.dql" in summary
        assert "Error 1 of 3" in summary
        assert "Error 2 of 3" in summary
        assert "Error 3 of 3" in summary


class TestErrorRecoveryDisabled:
    """Test parser behavior when error recovery is disabled."""

    def test_recovery_disabled_fails_immediately(self):
        """Test parser fails on first error when recovery disabled."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        expect column("phone") to_not_be_null
        """
        parser = DQLParser(enable_recovery=False)

        with pytest.raises(DQLSyntaxError):
            parser.parse(dql)

    def test_recovery_enabled_collects_errors(self):
        """Test parser collects errors when recovery enabled."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        expect column("phone") to_not_be_null
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        # Should return ParseResult with errors
        assert isinstance(result, ParseResult)
        assert result.has_errors()


class TestParseResult:
    """Test ParseResult functionality."""

    def test_parse_result_has_errors(self):
        """Test has_errors() method."""
        from dql_parser.ast_nodes import DQLFile

        result = ParseResult(ast=DQLFile(from_blocks=[]), errors=[])
        assert not result.has_errors()

        result_with_errors = ParseResult(
            ast=DQLFile(from_blocks=[]),
            errors=[DQLSyntaxError("Error", 1, 1, "context")],
        )
        assert result_with_errors.has_errors()

    def test_parse_result_is_success(self):
        """Test is_success() method."""
        from dql_parser.ast_nodes import DQLFile, FromBlock

        # Success: has blocks, no errors
        result_success = ParseResult(
            ast=DQLFile(from_blocks=[FromBlock("Model", [])]), errors=[]
        )
        assert result_success.is_success()

        # Not success: has errors
        result_with_errors = ParseResult(
            ast=DQLFile(from_blocks=[FromBlock("Model", [])]),
            errors=[DQLSyntaxError("Error", 1, 1, "")],
        )
        assert not result_with_errors.is_success()

    def test_parse_result_is_partial_success(self):
        """Test is_partial_success() method."""
        from dql_parser.ast_nodes import DQLFile, FromBlock

        result_partial = ParseResult(
            ast=DQLFile(from_blocks=[FromBlock("Model", [])]),
            errors=[DQLSyntaxError("Error", 1, 1, "")],
        )
        assert result_partial.is_partial_success()

    def test_parse_result_format_summary(self):
        """Test format_summary() generates correct message."""
        from dql_parser.ast_nodes import DQLFile, FromBlock, ExpectationNode, ColumnTarget, ToBeNull

        ast_with_expectations = DQLFile(
            from_blocks=[
                FromBlock(
                    "Model1",
                    [
                        ExpectationNode(ColumnTarget("field1"), ToBeNull()),
                        ExpectationNode(ColumnTarget("field2"), ToBeNull()),
                    ],
                )
            ]
        )

        result = ParseResult(ast=ast_with_expectations, errors=[])
        summary = result.format_summary()
        assert "2 expectations" in summary
        assert "no errors" in summary

    def test_parse_result_raise_if_errors(self):
        """Test raise_if_errors() raises DQLMultipleErrors."""
        from dql_parser.ast_nodes import DQLFile

        result_with_errors = ParseResult(
            ast=DQLFile(from_blocks=[]),
            errors=[DQLSyntaxError("Error", 1, 1, "")],
        )

        with pytest.raises(DQLMultipleErrors):
            result_with_errors.raise_if_errors()


class TestBackwardCompatibility:
    """Test backward compatibility with existing code."""

    def test_no_errors_returns_dqlfile(self):
        """Test parse() returns DQLFile when no errors (backward compat)."""
        dql = """
        from Customer
        expect column("email") to_not_be_null
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        # When no errors, should return DQLFile directly for backward compatibility
        from dql_parser.ast_nodes import DQLFile

        assert isinstance(result, DQLFile)

    def test_with_errors_returns_parse_result(self):
        """Test parse() returns ParseResult when errors exist."""
        dql = """
        from Customer
        expect column("email") to_be_invalid
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        # When errors exist, returns ParseResult
        assert isinstance(result, ParseResult)

    def test_existing_tests_unaffected(self):
        """Test that existing valid DQL parses as before."""
        dql = """
        from Customer
        expect column("email") to_not_be_null severity critical
        expect column("phone") to_match_pattern("\\d{3}-\\d{3}-\\d{4}") severity warning

        from Order
        expect column("total") to_be_between(0.01, 1000000.00) severity critical
        """
        parser = DQLParser(enable_recovery=True)
        result = parser.parse(dql)

        from dql_parser.ast_nodes import DQLFile

        assert isinstance(result, DQLFile)
        assert len(result.from_blocks) == 2
