"""Unit tests for reference (foreign key) validators."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToReference
from dql_core.validators.reference_validators import ToReferenceValidator
from dql_core.exceptions import ValidationError
from tests.conftest import MockRecord, MockExecutor


class TestToReferenceValidator:
    """Test suite for ToReferenceValidator (single field FK)."""

    def test_single_field_all_valid_references(self):
        """Test single field FK validation where all references exist."""
        # Source records with customer_id values
        source_records = [
            MockRecord(id=1, customer_id=101),
            MockRecord(id=2, customer_id=102),
            MockRecord(id=3, customer_id=103),
        ]

        # Target Customer records
        target_customers = [
            MockRecord(id=101, name="Alice"),
            MockRecord(id=102, name="Bob"),
            MockRecord(id=103, name="Charlie"),
            MockRecord(id=104, name="Dave"),  # Extra record, not referenced
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Customer": target_customers}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="Customer", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0
        assert len(result.failures) == 0

    def test_single_field_some_invalid_references(self):
        """Test single field FK validation with missing references."""
        # Source records - customer_id 999 doesn't exist in target
        source_records = [
            MockRecord(id=1, customer_id=101),
            MockRecord(id=2, customer_id=999),  # Invalid FK
            MockRecord(id=3, customer_id=103),
        ]

        # Target Customer records
        target_customers = [
            MockRecord(id=101, name="Alice"),
            MockRecord(id=103, name="Charlie"),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Customer": target_customers}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="Customer", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 3
        assert result.failed_records == 1
        assert len(result.failures) == 1
        assert result.failures[0]["value"] == 999
        assert result.failures[0]["target_model"] == "Customer"
        assert result.failures[0]["target_field"] == "id"

    def test_single_field_all_invalid_references(self):
        """Test single field FK validation where all references are missing."""
        source_records = [
            MockRecord(id=1, customer_id=201),
            MockRecord(id=2, customer_id=202),
        ]

        # Empty target model
        target_customers = []

        executor = MockExecutor(
            records=source_records,
            models={"Customer": target_customers}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="Customer", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 2
        assert len(result.failures) == 2

    def test_null_fk_values_skipped(self):
        """Test null FK values are skipped per AC5."""
        source_records = [
            MockRecord(id=1, customer_id=101),
            MockRecord(id=2, customer_id=None),  # Null FK - should skip
            MockRecord(id=3, customer_id=103),
        ]

        target_customers = [
            MockRecord(id=101, name="Alice"),
            MockRecord(id=103, name="Charlie"),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Customer": target_customers}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="Customer", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2  # Only non-null records counted
        assert result.failed_records == 0

    def test_all_null_fk_values(self):
        """Test validation passes when all FK values are null."""
        source_records = [
            MockRecord(id=1, customer_id=None),
            MockRecord(id=2, customer_id=None),
        ]

        target_customers = []  # Empty target is OK if all FKs are null

        executor = MockExecutor(
            records=source_records,
            models={"Customer": target_customers}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="Customer", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 0  # No non-null records
        assert result.failed_records == 0

    def test_invalid_target_model_raises_error(self):
        """Test validation error when target model not found."""
        source_records = [MockRecord(id=1, customer_id=101)]

        executor = MockExecutor(
            records=source_records,
            models={}  # No models registered
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="NonExistentModel", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(source_records, expectation, executor)

        assert "NonExistentModel" in str(exc_info.value)

    def test_self_referencing_fk(self):
        """Test self-referencing foreign key (model references itself)."""
        # Employee table with manager_id referencing same table
        source_records = [
            MockRecord(id=1, name="Alice", manager_id=None),  # Top manager
            MockRecord(id=2, name="Bob", manager_id=1),       # Reports to Alice
            MockRecord(id=3, name="Charlie", manager_id=1),   # Reports to Alice
            MockRecord(id=4, name="Dave", manager_id=2),      # Reports to Bob
        ]

        # For self-referencing, target model is same as source
        target_employees = source_records  # Same model

        executor = MockExecutor(
            records=source_records,
            models={"Employee": target_employees}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="manager_id"),
            operator=ToReference(target_model="Employee", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3  # Null manager_id skipped
        assert result.failed_records == 0

    def test_self_referencing_fk_invalid(self):
        """Test self-referencing FK with invalid reference."""
        source_records = [
            MockRecord(id=1, name="Alice", manager_id=None),
            MockRecord(id=2, name="Bob", manager_id=999),  # Invalid - no employee with id=999
        ]

        target_employees = source_records

        executor = MockExecutor(
            records=source_records,
            models={"Employee": target_employees}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="manager_id"),
            operator=ToReference(target_model="Employee", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert result.failures[0]["value"] == 999

    def test_bulk_validation_performance(self):
        """Test bulk validation with many records (should use single query)."""
        # Create 100 source records
        source_records = [
            MockRecord(id=i, customer_id=i % 10)  # FK values 0-9
            for i in range(100)
        ]

        # Target has only 0-7, missing 8 and 9
        target_customers = [
            MockRecord(id=i, name=f"Customer{i}")
            for i in range(8)
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Customer": target_customers}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="customer_id"),
            operator=ToReference(target_model="Customer", target_field="id"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        # Records with FK 8 and 9 should fail (20 records total: 10 with FK=8, 10 with FK=9)
        assert result.passed is False
        assert result.total_records == 100
        assert result.failed_records == 20

    def test_string_fk_values(self):
        """Test FK validation with string values (e.g., UUID, codes)."""
        source_records = [
            MockRecord(id=1, country_code="US"),
            MockRecord(id=2, country_code="UK"),
            MockRecord(id=3, country_code="XX"),  # Invalid code
        ]

        target_countries = [
            MockRecord(code="US", name="United States"),
            MockRecord(code="UK", name="United Kingdom"),
            MockRecord(code="CA", name="Canada"),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Country": target_countries}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="country_code"),
            operator=ToReference(target_model="Country", target_field="code"),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert result.failures[0]["value"] == "XX"


class TestToReferenceValidatorCompositeKey:
    """Test suite for ToReferenceValidator with composite keys."""

    def test_composite_key_all_valid(self):
        """Test composite key FK validation where all references exist."""
        # Source records with composite FK (customer_id, region_id)
        source_records = [
            MockRecord(id=1, order_key=(101, 1)),
            MockRecord(id=2, order_key=(102, 2)),
            MockRecord(id=3, order_key=(103, 1)),
        ]

        # Target records with composite key
        target_orders = [
            MockRecord(customer_id=101, region_id=1, amount=100),
            MockRecord(customer_id=102, region_id=2, amount=200),
            MockRecord(customer_id=103, region_id=1, amount=300),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Order": target_orders}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="order_key"),
            operator=ToReference(
                target_model="Order",
                target_field=["customer_id", "region_id"]
            ),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0

    def test_composite_key_some_invalid(self):
        """Test composite key FK with missing references."""
        source_records = [
            MockRecord(id=1, order_key=(101, 1)),
            MockRecord(id=2, order_key=(999, 9)),  # Invalid composite key
        ]

        target_orders = [
            MockRecord(customer_id=101, region_id=1, amount=100),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Order": target_orders}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="order_key"),
            operator=ToReference(
                target_model="Order",
                target_field=["customer_id", "region_id"]
            ),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert result.failures[0]["value"] == (999, 9)

    def test_composite_key_null_skipped(self):
        """Test null composite keys are skipped."""
        source_records = [
            MockRecord(id=1, order_key=(101, 1)),
            MockRecord(id=2, order_key=None),  # Null composite key
        ]

        target_orders = [
            MockRecord(customer_id=101, region_id=1, amount=100),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Order": target_orders}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="order_key"),
            operator=ToReference(
                target_model="Order",
                target_field=["customer_id", "region_id"]
            ),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 1  # Null skipped

    def test_composite_key_wrong_type(self):
        """Test composite key with wrong type (not tuple/list)."""
        source_records = [
            MockRecord(id=1, order_key=101),  # Should be tuple, not int
        ]

        target_orders = [
            MockRecord(customer_id=101, region_id=1, amount=100),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Order": target_orders}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="order_key"),
            operator=ToReference(
                target_model="Order",
                target_field=["customer_id", "region_id"]
            ),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert "must be tuple/list" in result.failures[0]["reason"]

    def test_composite_key_length_mismatch(self):
        """Test composite key with wrong number of fields."""
        source_records = [
            MockRecord(id=1, order_key=(101,)),  # Should have 2 fields, has 1
        ]

        target_orders = [
            MockRecord(customer_id=101, region_id=1, amount=100),
        ]

        executor = MockExecutor(
            records=source_records,
            models={"Order": target_orders}
        )

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="order_key"),
            operator=ToReference(
                target_model="Order",
                target_field=["customer_id", "region_id"]
            ),
            severity=None,
            cleaners=[],
        )

        validator = ToReferenceValidator()
        result = validator.validate(source_records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert "length mismatch" in result.failures[0]["reason"]
