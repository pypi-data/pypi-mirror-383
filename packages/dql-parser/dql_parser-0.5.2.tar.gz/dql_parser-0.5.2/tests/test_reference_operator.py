"""
Tests for to_reference operator for foreign key validation (Story 1.3)
"""

import pytest

from dql_parser import DQLParser, DQLSyntaxError, ToReference, ColumnTarget


class TestToReferenceSimpleForeignKey:
    """Test simple foreign key references"""

    def test_simple_foreign_key_string_field(self):
        """Test simple FK with string field"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToReference)
        assert expectation.operator.target_model == "Customer"
        assert expectation.operator.target_field == "id"
        assert expectation.operator.on_delete is None

    def test_simple_foreign_key_with_numbers(self):
        """Test simple FK with model name containing numbers"""
        dql = """
        FROM Order
        EXPECT column("user_id") to_reference(User2, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToReference)
        assert expectation.operator.target_model == "User2"
        assert expectation.operator.target_field == "id"

    def test_foreign_key_different_models(self):
        """Test FK references to different models"""
        dql = """
        FROM OrderItem
        EXPECT column("order_id") to_reference(Order, "id")
        EXPECT column("product_id") to_reference(Product, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 2

        exp1 = ast.from_blocks[0].expectations[0]
        assert exp1.operator.target_model == "Order"
        assert exp1.operator.target_field == "id"

        exp2 = ast.from_blocks[0].expectations[1]
        assert exp2.operator.target_model == "Product"
        assert exp2.operator.target_field == "id"


class TestToReferenceCompositeForeignKey:
    """Test composite foreign key references"""

    def test_composite_foreign_key_two_fields(self):
        """Test composite FK with two fields"""
        dql = """
        FROM OrderItem
        EXPECT column("order_id") to_reference(Order, ["id", "version"])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToReference)
        assert expectation.operator.target_model == "Order"
        assert isinstance(expectation.operator.target_field, list)
        assert expectation.operator.target_field == ["id", "version"]

    def test_composite_foreign_key_three_fields(self):
        """Test composite FK with three fields"""
        dql = """
        FROM Transaction
        EXPECT column("account_ref") to_reference(Account, ["bank_id", "branch_id", "account_number"])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.target_model == "Account"
        assert expectation.operator.target_field == ["bank_id", "branch_id", "account_number"]


class TestToReferenceOnDelete:
    """Test ON_DELETE behavior specifications"""

    def test_on_delete_cascade(self):
        """Test ON_DELETE CASCADE"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id", "CASCADE")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.on_delete == "CASCADE"

    def test_on_delete_set_null(self):
        """Test ON_DELETE SET_NULL"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id", "SET_NULL")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.on_delete == "SET_NULL"

    def test_on_delete_restrict(self):
        """Test ON_DELETE RESTRICT"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id", "RESTRICT")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.on_delete == "RESTRICT"

    def test_on_delete_case_insensitive(self):
        """Test ON_DELETE values are case-insensitive"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id", "cascade")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.on_delete == "CASCADE"


class TestToReferenceSeverityAndCleaners:
    """Test to_reference with severity and cleaners"""

    def test_to_reference_with_severity_critical(self):
        """Test to_reference with critical severity"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id") severity critical
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToReference)
        assert expectation.severity == "critical"

    def test_to_reference_case_insensitive(self):
        """Test to_reference keyword is case-insensitive"""
        dql = """
        FROM Order
        EXPECT column("customer_id") TO_REFERENCE(Customer, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert isinstance(expectation.operator, ToReference)


class TestToReferenceErrorHandling:
    """Test error handling for invalid references"""

    def test_invalid_on_delete_value_rejected(self):
        """Test invalid ON_DELETE value is rejected"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id", "DELETE_ALL")
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError, match="on_delete must be one of"):
            parser.parse(dql)

    def test_to_reference_missing_arguments_rejected(self):
        """Test to_reference requires both model and field"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer)
        """
        parser = DQLParser()
        with pytest.raises(DQLSyntaxError):
            parser.parse(dql)


class TestToReferenceSpecialCases:
    """Test special cases for to_reference"""

    def test_self_referencing_foreign_key(self):
        """Test self-referencing FK (e.g., Employee.manager_id → Employee.id)"""
        dql = """
        FROM Employee
        EXPECT column("manager_id") to_reference(Employee, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.target_model == "Employee"
        assert expectation.operator.target_field == "id"

    def test_multiple_fks_to_same_model(self):
        """Test multiple FK fields referencing same model"""
        dql = """
        FROM Order
        EXPECT column("billing_address_id") to_reference(Address, "id")
        EXPECT column("shipping_address_id") to_reference(Address, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 2
        assert ast.from_blocks[0].expectations[0].operator.target_model == "Address"
        assert ast.from_blocks[0].expectations[1].operator.target_model == "Address"

    def test_composite_fk_with_on_delete(self):
        """Test composite FK with ON_DELETE behavior"""
        dql = """
        FROM OrderItem
        EXPECT column("order_ref") to_reference(Order, ["id", "version"], "CASCADE")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        assert expectation.operator.target_field == ["id", "version"]
        assert expectation.operator.on_delete == "CASCADE"


class TestToReferenceModelNameValidation:
    """Test model name validation (PascalCase)"""

    def test_valid_pascal_case_model_names(self):
        """Test various valid PascalCase model names"""
        test_cases = [
            ("Customer", "id"),
            ("OrderItem", "id"),
            ("UserProfile", "user_id"),
            ("Product2", "id"),
            ("APIKey", "id"),
        ]

        for model, field in test_cases:
            dql = f"""
            FROM Order
            EXPECT column("ref") to_reference({model}, "{field}")
            """
            parser = DQLParser()
            ast = parser.parse(dql)
            assert ast.from_blocks[0].expectations[0].operator.target_model == model


class TestToReferenceMultipleOperators:
    """Test to_reference mixed with other operators"""

    def test_mixed_with_other_operators(self):
        """Test file with multiple operator types including to_reference"""
        dql = """
        FROM Order
        EXPECT column("id") to_not_be_null
        EXPECT column("customer_id") to_reference(Customer, "id")
        EXPECT column("total") to_be_greater_than(0)
        EXPECT column("status") to_be_in(["pending", "completed", "cancelled"])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 4
        exp2 = ast.from_blocks[0].expectations[1]
        assert isinstance(exp2.operator, ToReference)

    def test_multiple_to_reference_operators(self):
        """Test multiple to_reference operators in same file"""
        dql = """
        FROM OrderItem
        EXPECT column("order_id") to_reference(Order, "id")
        EXPECT column("product_id") to_reference(Product, "id")
        EXPECT column("warehouse_id") to_reference(Warehouse, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        assert len(ast.from_blocks[0].expectations) == 3
        for exp in ast.from_blocks[0].expectations:
            assert isinstance(exp.operator, ToReference)


class TestToReferenceASTNodeString:
    """Test AST node string representation"""

    def test_simple_fk_string_representation(self):
        """Test __str__ for simple FK"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        str_repr = str(expectation.operator)
        assert "to_reference" in str_repr
        assert "Customer" in str_repr
        assert "id" in str_repr

    def test_composite_fk_string_representation(self):
        """Test __str__ for composite FK"""
        dql = """
        FROM OrderItem
        EXPECT column("order_ref") to_reference(Order, ["id", "version"])
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        str_repr = str(expectation.operator)
        assert "to_reference" in str_repr
        assert "Order" in str_repr
        assert "id" in str_repr
        assert "version" in str_repr

    def test_on_delete_string_representation(self):
        """Test __str__ includes ON_DELETE"""
        dql = """
        FROM Order
        EXPECT column("customer_id") to_reference(Customer, "id", "CASCADE")
        """
        parser = DQLParser()
        ast = parser.parse(dql)

        expectation = ast.from_blocks[0].expectations[0]
        str_repr = str(expectation.operator)
        assert "CASCADE" in str_repr
