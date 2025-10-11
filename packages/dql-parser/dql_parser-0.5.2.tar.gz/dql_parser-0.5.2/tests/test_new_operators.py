"""
Tests for new operators added in Story 1.1: to_have_length, to_be_greater_than, to_be_less_than
"""

import pytest

from dql_parser import DQLParser
from dql_parser.ast_nodes import (
    ColumnTarget,
    ToBeGreaterThan,
    ToHaveLength,
    ToBeLessThan,
)
from dql_parser.exceptions import DQLSyntaxError


class TestToHaveLengthOperator:
    """Test cases for to_have_length operator"""

    def test_to_have_length_both_min_and_max(self):
        """Test to_have_length with both min and max arguments"""
        dql = """
        FROM Customer
        EXPECT column("username") to_have_length(3, 20)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        block = ast.from_blocks[0]
        assert block.model_name == "Customer"
        assert len(block.expectations) == 1

        expectation = block.expectations[0]
        assert isinstance(expectation.target, ColumnTarget)
        assert expectation.target.field_name == "username"
        assert isinstance(expectation.operator, ToHaveLength)
        assert expectation.operator.min_length == 3
        assert expectation.operator.max_length == 20

    def test_to_have_length_min_only(self):
        """Test to_have_length with only min argument"""
        dql = """
        FROM Product
        EXPECT column("description") to_have_length(10)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToHaveLength)
        assert expectation.operator.min_length == 10
        assert expectation.operator.max_length is None

    def test_to_have_length_case_insensitive(self):
        """Test to_have_length is case-insensitive"""
        dql = """
        FROM Customer
        EXPECT column("name") TO_HAVE_LENGTH(5, 100)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToHaveLength)
        assert expectation.operator.min_length == 5
        assert expectation.operator.max_length == 100

    def test_to_have_length_with_severity(self):
        """Test to_have_length with severity clause"""
        dql = """
        FROM Customer
        EXPECT column("email") to_have_length(5, 255) severity warning
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToHaveLength)
        assert expectation.severity == "warning"


class TestToBeGreaterThanOperator:
    """Test cases for to_be_greater_than operator"""

    def test_to_be_greater_than_integer(self):
        """Test to_be_greater_than with integer threshold"""
        dql = """
        FROM Order
        EXPECT column("total") to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        block = ast.from_blocks[0]
        assert block.model_name == "Order"

        expectation = block.expectations[0]
        assert isinstance(expectation.target, ColumnTarget)
        assert expectation.target.field_name == "total"
        assert isinstance(expectation.operator, ToBeGreaterThan)
        assert expectation.operator.threshold == 0

    def test_to_be_greater_than_float(self):
        """Test to_be_greater_than with float threshold"""
        dql = """
        FROM Product
        EXPECT column("price") to_be_greater_than(0.01)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeGreaterThan)
        assert expectation.operator.threshold == 0.01

    def test_to_be_greater_than_negative_threshold(self):
        """Test to_be_greater_than with negative threshold"""
        dql = """
        FROM Account
        EXPECT column("balance") to_be_greater_than(-1000)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeGreaterThan)
        assert expectation.operator.threshold == -1000

    def test_to_be_greater_than_case_insensitive(self):
        """Test to_be_greater_than is case-insensitive"""
        dql = """
        FROM Order
        EXPECT column("quantity") TO_BE_GREATER_THAN(1)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeGreaterThan)
        assert expectation.operator.threshold == 1

    def test_to_be_greater_than_with_severity_critical(self):
        """Test to_be_greater_than with critical severity"""
        dql = """
        FROM Transaction
        EXPECT column("amount") to_be_greater_than(0) severity critical
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeGreaterThan)
        assert expectation.severity == "critical"


class TestToBeLessThanOperator:
    """Test cases for to_be_less_than operator"""

    def test_to_be_less_than_integer(self):
        """Test to_be_less_than with integer threshold"""
        dql = """
        FROM Customer
        EXPECT column("age") to_be_less_than(150)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        block = ast.from_blocks[0]
        assert block.model_name == "Customer"

        expectation = block.expectations[0]
        assert isinstance(expectation.target, ColumnTarget)
        assert expectation.target.field_name == "age"
        assert isinstance(expectation.operator, ToBeLessThan)
        assert expectation.operator.threshold == 150

    def test_to_be_less_than_float(self):
        """Test to_be_less_than with float threshold"""
        dql = """
        FROM Product
        EXPECT column("discount") to_be_less_than(1.0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeLessThan)
        assert expectation.operator.threshold == 1.0

    def test_to_be_less_than_case_insensitive(self):
        """Test to_be_less_than is case-insensitive"""
        dql = """
        FROM Order
        EXPECT column("priority") To_Be_Less_Than(10)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeLessThan)
        assert expectation.operator.threshold == 10

    def test_to_be_less_than_with_severity_info(self):
        """Test to_be_less_than with info severity"""
        dql = """
        FROM Metric
        EXPECT column("response_time") to_be_less_than(1000) severity info
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToBeLessThan)
        assert expectation.severity == "info"


class TestMultipleNewOperators:
    """Test multiple new operators in single file"""

    def test_all_three_new_operators(self):
        """Test file with all three new operators"""
        dql = """
        FROM Customer
        EXPECT column("username") to_have_length(3, 20)
        EXPECT column("age") to_be_greater_than(0)
        EXPECT column("age") to_be_less_than(150)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks) == 1
        block = ast.from_blocks[0]
        assert len(block.expectations) == 3

        # Check first expectation
        exp1 = block.expectations[0]
        assert isinstance(exp1.operator, ToHaveLength)
        assert exp1.operator.min_length == 3
        assert exp1.operator.max_length == 20

        # Check second expectation
        exp2 = block.expectations[1]
        assert isinstance(exp2.operator, ToBeGreaterThan)
        assert exp2.operator.threshold == 0

        # Check third expectation
        exp3 = block.expectations[2]
        assert isinstance(exp3.operator, ToBeLessThan)
        assert exp3.operator.threshold == 150

    def test_mixed_with_existing_operators(self):
        """Test new operators mixed with existing operators"""
        dql = """
        FROM Order
        EXPECT column("id") to_not_be_null
        EXPECT column("total") to_be_greater_than(0)
        EXPECT column("status") to_be_in(["pending", "completed", "cancelled"])
        EXPECT column("customer_note") to_have_length(0, 500)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 4


class TestNewOperatorErrorHandling:
    """Test error handling for new operators"""

    def test_to_be_greater_than_missing_argument(self):
        """Test to_be_greater_than requires threshold argument"""
        dql = """
        FROM Order
        EXPECT column("total") to_be_greater_than()
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError):
            parser.parse(dql)

    def test_to_be_less_than_missing_argument(self):
        """Test to_be_less_than requires threshold argument"""
        dql = """
        FROM Customer
        EXPECT column("age") to_be_less_than()
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError):
            parser.parse(dql)

    # Note: Argument type validation will be added in Task 4 (Add Argument Validation)
