"""
Tests for argument validation of new operators (Story 1.1 Task 4)
"""

import pytest

from dql_parser import DQLParser, DQLSyntaxError


class TestToHaveLengthValidation:
    """Test argument validation for to_have_length operator"""

    def test_to_have_length_string_argument_rejected(self):
        """Test to_have_length rejects string arguments"""
        dql = """
        FROM Customer
        EXPECT column("name") to_have_length("invalid")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="must be integer"):
            parser.parse(dql)

    def test_to_have_length_float_argument_rejected(self):
        """Test to_have_length rejects float arguments"""
        dql = """
        FROM Customer
        EXPECT column("name") to_have_length(3.5)
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="must be integer"):
            parser.parse(dql)

    def test_to_have_length_min_greater_than_max_rejected(self):
        """Test to_have_length rejects min > max"""
        dql = """
        FROM Customer
        EXPECT column("name") to_have_length(100, 10)
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="min_length .* must be <= max_length"):
            parser.parse(dql)

    def test_to_have_length_negative_min_accepted(self):
        """Test to_have_length accepts negative min (edge case, semantically invalid but syntactically valid)"""
        dql = """
        FROM Customer
        EXPECT column("name") to_have_length(-1, 10)
        """
        parser = DQLParser()
        # Should parse without error (semantic validation is separate)
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.min_length == -1


class TestToBeGreaterThanValidation:
    """Test argument validation for to_be_greater_than operator"""

    def test_to_be_greater_than_string_argument_rejected(self):
        """Test to_be_greater_than rejects string arguments"""
        dql = """
        FROM Order
        EXPECT column("total") to_be_greater_than("invalid")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="must be numeric"):
            parser.parse(dql)

    def test_to_be_greater_than_accepts_int(self):
        """Test to_be_greater_than accepts integer"""
        dql = """
        FROM Order
        EXPECT column("total") to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.threshold == 0

    def test_to_be_greater_than_accepts_float(self):
        """Test to_be_greater_than accepts float"""
        dql = """
        FROM Product
        EXPECT column("price") to_be_greater_than(0.01)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.threshold == 0.01


class TestToBeLessThanValidation:
    """Test argument validation for to_be_less_than operator"""

    def test_to_be_less_than_string_argument_rejected(self):
        """Test to_be_less_than rejects string arguments"""
        dql = """
        FROM Customer
        EXPECT column("age") to_be_less_than("invalid")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="must be numeric"):
            parser.parse(dql)

    def test_to_be_less_than_accepts_int(self):
        """Test to_be_less_than accepts integer"""
        dql = """
        FROM Customer
        EXPECT column("age") to_be_less_than(150)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.threshold == 150

    def test_to_be_less_than_accepts_float(self):
        """Test to_be_less_than accepts float"""
        dql = """
        FROM Product
        EXPECT column("discount") to_be_less_than(1.0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.threshold == 1.0


class TestEdgeCases:
    """Test edge cases for argument validation"""

    def test_to_have_length_zero_values(self):
        """Test to_have_length accepts zero values"""
        dql = """
        FROM Customer
        EXPECT column("name") to_have_length(0, 0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        operator = ast.from_blocks[0].expectations[0].operator
        assert operator.min_length == 0
        assert operator.max_length == 0

    def test_to_be_greater_than_zero(self):
        """Test to_be_greater_than accepts zero"""
        dql = """
        FROM Order
        EXPECT column("total") to_be_greater_than(0)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.threshold == 0

    def test_to_be_less_than_negative(self):
        """Test to_be_less_than accepts negative values"""
        dql = """
        FROM Account
        EXPECT column("balance") to_be_less_than(-100)
        """
        parser = DQLParser()
        ast = parser.parse(dql)
        assert ast.from_blocks[0].expectations[0].operator.threshold == -100
