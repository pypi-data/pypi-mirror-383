"""
Tests for computed column expressions (Story 1.4)
"""

import pytest

from dql_parser import (
    ArithmeticExpr,
    DQLParser,
    DQLSyntaxError,
    ExprTarget,
    FieldRef,
    FunctionCall,
    Value,
)


class TestArithmeticOperators:
    """Test arithmetic operators and precedence"""

    def test_simple_multiplication(self):
        """Test simple multiplication: price * 1.1"""
        dql = """
        FROM Order
        EXPECT price * 1.1 to_be_greater_than(10)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.target, ExprTarget)
        expr = expectation.target.expression
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "*"
        assert isinstance(expr.left, FieldRef)
        assert expr.left.field_name == "price"
        assert isinstance(expr.right, Value)
        assert expr.right.value == 1.1

    def test_simple_addition(self):
        """Test simple addition: a + b"""
        dql = """
        FROM Order
        EXPECT subtotal + tax to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "+"

    def test_operator_precedence_multiply_before_add(self):
        """Test precedence: 2 + 3 * 4 should be 2 + (3 * 4)"""
        dql = """
        FROM Product
        EXPECT price + tax * 1.08 to_be_less_than(100)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        # Root should be addition
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "+"
        # Right subtree should be multiplication
        assert isinstance(expr.right, ArithmeticExpr)
        assert expr.right.operator == "*"

    def test_operator_precedence_divide_before_subtract(self):
        """Test precedence: a - b / c should be a - (b / c)"""
        dql = """
        FROM Product
        EXPECT total - discount / 2 to_be_greater_than(50)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.operator == "-"
        assert isinstance(expr.right, ArithmeticExpr)
        assert expr.right.operator == "/"

    def test_modulo_operator(self):
        """Test modulo operator: id % 10"""
        dql = """
        FROM Customer
        EXPECT id % 10 to_be_in([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "%"

    def test_parentheses_override_precedence(self):
        """Test parentheses: (price + tax) * 1.08"""
        dql = """
        FROM Order
        EXPECT (price + tax) * 1.08 to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        # Root should be multiplication
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "*"
        # Left subtree should be addition
        assert isinstance(expr.left, ArithmeticExpr)
        assert expr.left.operator == "+"

    def test_nested_parentheses(self):
        """Test nested parentheses: ((a + b) * c) / d"""
        dql = """
        FROM Order
        EXPECT ((subtotal + tax) * quantity) / discount to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.operator == "/"


class TestStringFunctions:
    """Test string manipulation functions"""

    def test_upper_function(self):
        """Test UPPER function"""
        dql = """
        FROM Customer
        EXPECT UPPER(email) to_match_pattern("[email protected]")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "UPPER"
        assert len(expr.args) == 1
        assert isinstance(expr.args[0], FieldRef)
        assert expr.args[0].field_name == "email"

    def test_lower_function(self):
        """Test LOWER function"""
        dql = """
        FROM Product
        EXPECT LOWER(sku) to_match_pattern("[a-z0-9]+")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "LOWER"

    def test_trim_function(self):
        """Test TRIM function"""
        dql = """
        FROM Customer
        EXPECT TRIM(name) to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "TRIM"

    def test_length_function(self):
        """Test LENGTH function"""
        dql = """
        FROM Customer
        EXPECT LENGTH(password) to_be_between(8, 128)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "LENGTH"

    def test_string_functions_case_variations(self):
        """Test string functions with various case - UPPER is standard"""
        dql = """
        FROM Customer
        EXPECT UPPER(email) to_not_be_null
        EXPECT LOWER(name) to_not_be_null
        EXPECT TRIM(address) to_not_be_null
        EXPECT LENGTH(phone) to_be_greater_than(10)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 4
        # All should parse successfully with uppercase function names
        assert all(
            isinstance(exp.target.expression, FunctionCall)
            for exp in ast.from_blocks[0].expectations
        )


class TestDateFunctions:
    """Test date extraction functions"""

    def test_year_function(self):
        """Test YEAR function"""
        dql = """
        FROM Order
        EXPECT YEAR(created_at) to_be_between(2020, 2025)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "YEAR"

    def test_month_function(self):
        """Test MONTH function"""
        dql = """
        FROM Order
        EXPECT MONTH(created_at) to_be_in([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "MONTH"

    def test_day_function(self):
        """Test DAY function"""
        dql = """
        FROM Order
        EXPECT DAY(created_at) to_be_between(1, 31)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "DAY"

    def test_age_function(self):
        """Test AGE function"""
        dql = """
        FROM Customer
        EXPECT AGE(birth_date) to_be_between(18, 100)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "AGE"

    def test_date_functions_all_uppercase(self):
        """Test date functions with uppercase (standard)"""
        dql = """
        FROM Order
        EXPECT YEAR(created_at) to_be_greater_than(2020)
        EXPECT MONTH(created_at) to_be_in([1, 2, 3])
        EXPECT DAY(created_at) to_be_less_than(32)
        EXPECT AGE(created_at) to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 4


class TestConcatFunction:
    """Test CONCAT function with variable arguments"""

    def test_concat_two_fields(self):
        """Test CONCAT with two fields"""
        dql = """
        FROM Customer
        EXPECT CONCAT(first_name, last_name) to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "CONCAT"
        assert len(expr.args) == 2

    def test_concat_with_literal(self):
        """Test CONCAT with field and literal"""
        dql = """
        FROM Customer
        EXPECT CONCAT(first_name, ' ', last_name) to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.function_name == "CONCAT"
        assert len(expr.args) == 3
        # Second arg should be string literal
        assert isinstance(expr.args[1], Value)
        assert expr.args[1].value == " "

    def test_concat_five_arguments(self):
        """Test CONCAT with five arguments"""
        dql = """
        FROM Address
        EXPECT CONCAT(street, ' ', city, ' ', zip_code) to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.function_name == "CONCAT"
        assert len(expr.args) == 5

    def test_concat_uppercase(self):
        """Test CONCAT with uppercase (standard)"""
        dql = """
        FROM Customer
        EXPECT CONCAT(first_name, last_name) to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.function_name == "CONCAT"


class TestNestedExpressions:
    """Test nested function calls and complex expressions"""

    def test_nested_string_functions(self):
        """Test UPPER(TRIM(field))"""
        dql = """
        FROM Customer
        EXPECT UPPER(TRIM(email)) to_match_pattern("[email protected]")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, FunctionCall)
        assert expr.function_name == "UPPER"
        # Argument should be another function call
        assert isinstance(expr.args[0], FunctionCall)
        assert expr.args[0].function_name == "TRIM"

    def test_nested_three_levels(self):
        """Test UPPER(TRIM(CONCAT(a, b)))"""
        dql = """
        FROM Customer
        EXPECT UPPER(TRIM(CONCAT(first_name, last_name))) to_match_pattern("[A-Z]+")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.function_name == "UPPER"
        assert expr.args[0].function_name == "TRIM"
        assert expr.args[0].args[0].function_name == "CONCAT"

    def test_arithmetic_in_function(self):
        """Test function with arithmetic expression: LENGTH(name + suffix)"""
        dql = """
        FROM Product
        EXPECT LENGTH(name) * 2 to_be_greater_than(10)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "*"
        assert isinstance(expr.left, FunctionCall)
        assert expr.left.function_name == "LENGTH"

    def test_function_in_arithmetic(self):
        """Test arithmetic with function: YEAR(date) + 1"""
        dql = """
        FROM Order
        EXPECT YEAR(created_at) + 1 to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, ArithmeticExpr)
        assert expr.operator == "+"
        assert isinstance(expr.left, FunctionCall)
        assert expr.left.function_name == "YEAR"


class TestComplexExpressions:
    """Test complex combined expressions"""

    def test_arithmetic_with_parentheses_and_functions(self):
        """Test (LENGTH(name) + 5) * 2"""
        dql = """
        FROM Product
        EXPECT (LENGTH(name) + 5) * 2 to_be_less_than(100)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.operator == "*"
        assert isinstance(expr.left, ArithmeticExpr)
        assert expr.left.operator == "+"

    def test_concat_with_arithmetic(self):
        """Test CONCAT with arithmetic expressions"""
        dql = """
        FROM Order
        EXPECT CONCAT(id, price * quantity) to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.function_name == "CONCAT"
        # Second arg should be arithmetic
        assert isinstance(expr.args[1], ArithmeticExpr)

    def test_multiple_operations_same_precedence(self):
        """Test a + b + c (left associative)"""
        dql = """
        FROM Order
        EXPECT price + tax + shipping to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        # Should be ((price + tax) + shipping)
        assert expr.operator == "+"
        assert isinstance(expr.left, ArithmeticExpr)
        assert expr.left.operator == "+"


class TestBackwardCompatibility:
    """Test backward compatibility with existing features"""

    def test_simple_column_target_still_works(self):
        """Test that simple column() syntax still works"""
        dql = """
        FROM Customer
        EXPECT column("email") to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        # Should be ColumnTarget, not ExprTarget
        from dql_parser import ColumnTarget

        assert isinstance(expectation.target, ColumnTarget)

    def test_row_level_expressions_still_work(self):
        """Test row-level conditions with field names work"""
        dql = """
        FROM Order
        EXPECT row WHERE price > 10 to_not_be_null
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        from dql_parser import RowTarget

        assert isinstance(expectation.target, RowTarget)

    def test_mixed_old_and_new_syntax(self):
        """Test file with both old and new syntax"""
        dql = """
        FROM Order
        EXPECT column("id") to_not_be_null
        EXPECT price * quantity to_be_greater_than(0)
        EXPECT UPPER(status) to_be_in(["PENDING", "COMPLETED"])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 3


class TestExpressionWithOperators:
    """Test expressions work with various operators"""

    def test_expression_with_to_be_between(self):
        """Test expression with to_be_between"""
        dql = """
        FROM Order
        EXPECT price * 1.1 to_be_between(10, 100)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        from dql_parser import ToBeBetween

        assert isinstance(expectation.operator, ToBeBetween)

    def test_expression_with_to_match_pattern(self):
        """Test expression with to_match_pattern"""
        dql = """
        FROM Customer
        EXPECT UPPER(email) to_match_pattern("[A-Z]+@[A-Z]+\\\\.[A-Z]+")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        from dql_parser import ToMatchPattern

        assert isinstance(expectation.operator, ToMatchPattern)

    def test_expression_with_severity(self):
        """Test expression with severity clause"""
        dql = """
        FROM Order
        EXPECT price * quantity to_be_greater_than(0) severity critical
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.severity == "critical"


class TestEdgeCases:
    """Test edge cases and special scenarios"""

    def test_field_name_with_underscores(self):
        """Test field names with underscores"""
        dql = """
        FROM Order
        EXPECT order_id * 2 to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.left.field_name == "order_id"

    def test_negative_numbers(self):
        """Test negative number literals"""
        dql = """
        FROM Account
        EXPECT balance + -100 to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert isinstance(expr, ArithmeticExpr)

    def test_float_literals(self):
        """Test float literals in expressions"""
        dql = """
        FROM Product
        EXPECT price * 0.85 to_be_less_than(100.50)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expr = ast.from_blocks[0].expectations[0].target.expression
        assert expr.right.value == 0.85
