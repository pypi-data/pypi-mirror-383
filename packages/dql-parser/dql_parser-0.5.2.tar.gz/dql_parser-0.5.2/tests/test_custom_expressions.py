"""
Tests for to_satisfy operator with custom Python expressions (Story 1.2)
"""

import pytest

from dql_parser import DQLParser, DQLSyntaxError, ToSatisfy, ColumnTarget


class TestToSatisfyBasicLambdas:
    """Test basic lambda expressions with to_satisfy"""

    def test_simple_lambda_numeric_comparison(self):
        """Test simple lambda with numeric comparison"""
        dql = """
        FROM Product
        EXPECT column("price") to_satisfy("lambda x: x > 0")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert expectation.operator.expression == "lambda x: x > 0"
        assert expectation.operator.expr_type == "lambda"

    def test_lambda_with_string_method(self):
        """Test lambda using string methods"""
        dql = """
        FROM Customer
        EXPECT column("email") to_satisfy("lambda x: x.endswith('@example.com')")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert expectation.operator.expression == "lambda x: x.endswith('@example.com')"
        assert expectation.operator.expr_type == "lambda"

    def test_lambda_with_length_check(self):
        """Test lambda with length validation"""
        dql = """
        FROM Customer
        EXPECT column("username") to_satisfy("lambda x: 3 <= len(x) <= 20")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert "len(x)" in expectation.operator.expression

    def test_lambda_with_and_logic(self):
        """Test lambda with AND logical operator"""
        dql = """
        FROM Product
        EXPECT column("sku") to_satisfy("lambda x: x.startswith('P') and len(x) == 10")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert "and" in expectation.operator.expression


class TestToSatisfyComplexLambdas:
    """Test complex lambda expressions"""

    def test_lambda_with_multiple_conditions(self):
        """Test lambda with multiple AND/OR conditions"""
        dql = """
        FROM Order
        EXPECT column("status") to_satisfy("lambda x: x in ['pending', 'completed'] or x.startswith('cancelled_')")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert "in [" in expectation.operator.expression
        assert "or" in expectation.operator.expression

    def test_lambda_with_nested_calls(self):
        """Test lambda with nested function calls"""
        dql = """
        FROM Customer
        EXPECT column("name") to_satisfy("lambda x: len(x.strip()) > 0")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert "x.strip()" in expectation.operator.expression

    def test_lambda_with_arithmetic(self):
        """Test lambda with arithmetic operations"""
        dql = """
        FROM Product
        EXPECT column("discount") to_satisfy("lambda x: 0 <= x * 100 <= 100")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert "x * 100" in expectation.operator.expression


class TestToSatisfyFunctionReferences:
    """Test function reference syntax (non-lambda)"""

    def test_simple_function_reference(self):
        """Test simple function reference"""
        dql = """
        FROM Customer
        EXPECT column("email") to_satisfy("is_valid_email")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert expectation.operator.expression == "is_valid_email"
        assert expectation.operator.expr_type == "function"

    def test_function_reference_with_underscores(self):
        """Test function reference with underscores"""
        dql = """
        FROM Product
        EXPECT column("sku") to_satisfy("validate_product_sku")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.expression == "validate_product_sku"
        assert expectation.operator.expr_type == "function"

    def test_function_reference_with_numbers(self):
        """Test function reference with numbers"""
        dql = """
        FROM Order
        EXPECT column("status") to_satisfy("validate_status_v2")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.expression == "validate_status_v2"


class TestToSatisfySeverityAndCleaners:
    """Test to_satisfy with severity and cleaners"""

    def test_to_satisfy_with_severity_critical(self):
        """Test to_satisfy with critical severity"""
        dql = """
        FROM Order
        EXPECT column("total") to_satisfy("lambda x: x > 0") severity critical
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)
        assert expectation.severity == "critical"

    def test_to_satisfy_case_insensitive(self):
        """Test to_satisfy keyword is case-insensitive"""
        dql = """
        FROM Product
        EXPECT column("price") TO_SATISFY("lambda x: x > 0")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToSatisfy)


class TestToSatisfyErrorHandling:
    """Test error handling for invalid expressions"""

    def test_empty_expression_rejected(self):
        """Test empty expression is rejected"""
        dql = """
        FROM Product
        EXPECT column("price") to_satisfy("")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="cannot be empty"):
            parser.parse(dql)

    def test_invalid_lambda_syntax_rejected(self):
        """Test invalid lambda syntax is rejected"""
        dql = """
        FROM Product
        EXPECT column("price") to_satisfy("lambda x x > 0")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="Invalid lambda syntax"):
            parser.parse(dql)

    def test_dangerous_function_eval_rejected(self):
        """Test dangerous function eval is rejected"""
        dql = """
        FROM Product
        EXPECT column("price") to_satisfy("lambda x: eval('x > 0')")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="[Dd]angerous function"):
            parser.parse(dql)

    def test_dangerous_function_exec_rejected(self):
        """Test dangerous function exec is rejected"""
        dql = """
        FROM Product
        EXPECT column("code") to_satisfy("lambda x: exec('print(x)')")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="[Dd]angerous function"):
            parser.parse(dql)

    def test_dangerous_function_import_rejected(self):
        """Test __import__ is rejected"""
        dql = """
        FROM Product
        EXPECT column("data") to_satisfy("lambda x: __import__('os').path.exists(x)")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="[Dd]angerous function"):
            parser.parse(dql)

    def test_dangerous_function_compile_rejected(self):
        """Test compile is rejected"""
        dql = """
        FROM Product
        EXPECT column("code") to_satisfy("lambda x: compile(x, '<string>', 'exec')")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="[Dd]angerous function"):
            parser.parse(dql)

    def test_dangerous_function_open_rejected(self):
        """Test open is rejected"""
        dql = """
        FROM Product
        EXPECT column("filename") to_satisfy("lambda x: open(x).read()")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="[Dd]angerous function"):
            parser.parse(dql)

    def test_dangerous_function_reference_rejected(self):
        """Test dangerous function as function reference is rejected"""
        dql = """
        FROM Product
        EXPECT column("code") to_satisfy("eval")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="[Dd]angerous function"):
            parser.parse(dql)

    def test_invalid_function_reference_rejected(self):
        """Test invalid function reference (not an identifier)"""
        dql = """
        FROM Product
        EXPECT column("data") to_satisfy("my-invalid-name")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="not a valid identifier"):
            parser.parse(dql)


class TestToSatisfyMultipleOperators:
    """Test to_satisfy mixed with other operators"""

    def test_mixed_with_other_operators(self):
        """Test file with multiple operator types including to_satisfy"""
        dql = """
        FROM Product
        EXPECT column("id") to_not_be_null
        EXPECT column("price") to_satisfy("lambda x: x > 0")
        EXPECT column("price") to_be_greater_than(0)
        EXPECT column("name") to_have_length(1, 255)
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 4
        exp2 = ast.from_blocks[0].expectations[1]
        assert isinstance(exp2.operator, ToSatisfy)

    def test_multiple_to_satisfy_operators(self):
        """Test multiple to_satisfy operators in same file"""
        dql = """
        FROM Product
        EXPECT column("price") to_satisfy("lambda x: x > 0")
        EXPECT column("sku") to_satisfy("validate_sku")
        EXPECT column("name") to_satisfy("lambda x: len(x.strip()) > 0")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 3
        for exp in ast.from_blocks[0].expectations:
            assert isinstance(exp.operator, ToSatisfy)


class TestToSatisfyEdgeCases:
    """Test edge cases for to_satisfy"""

    def test_lambda_with_nested_parentheses(self):
        """Test lambda with nested parentheses"""
        dql = """
        FROM Product
        EXPECT column("data") to_satisfy("lambda x: ((x > 0) and (x < 100))")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert "((x > 0) and (x < 100))" in expectation.operator.expression

    def test_lambda_with_string_literals(self):
        """Test lambda with string literals containing quotes"""
        dql = """
        FROM Customer
        EXPECT column("status") to_satisfy("lambda x: x != 'inactive'")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert "'inactive'" in expectation.operator.expression

    def test_lambda_with_list_comprehension(self):
        """Test lambda with list comprehension"""
        dql = """
        FROM Order
        EXPECT column("items") to_satisfy("lambda x: all([item['qty'] > 0 for item in x])")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert "[item['qty'] > 0 for item in x]" in expectation.operator.expression

    def test_lambda_with_ternary_operator(self):
        """Test lambda with ternary conditional"""
        dql = """
        FROM Product
        EXPECT column("stock") to_satisfy("lambda x: 'available' if x > 0 else 'sold out'")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert "if x > 0 else" in expectation.operator.expression
