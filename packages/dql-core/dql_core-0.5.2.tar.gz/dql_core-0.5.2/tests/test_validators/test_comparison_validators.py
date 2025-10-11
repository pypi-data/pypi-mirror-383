"""Tests for comparison validators (Story 2.1)."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToBeGreaterThan, ToBeLessThan
from dql_core.validators import ToBeGreaterThanValidator, ToBeLessThanValidator
from tests.conftest import MockRecord, MockExecutor


class TestToBeGreaterThanValidator:
    """Tests for ToBeGreaterThanValidator."""

    def test_all_greater_than_passes(self):
        """Test validation passes when all values are greater than threshold."""
        records = [MockRecord(age=25), MockRecord(age=30), MockRecord(age=35)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeGreaterThan(threshold=18),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0

    def test_some_not_greater_fails(self):
        """Test validation fails when some values are not greater than threshold."""
        records = [MockRecord(age=25), MockRecord(age=15)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeGreaterThan(threshold=18),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1
        assert result.failures[0]["value"] == 15

    def test_equal_to_threshold_fails(self):
        """Test validation fails when value equals threshold (not greater)."""
        records = [MockRecord(age=18)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeGreaterThan(threshold=18),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1

    def test_float_comparison(self):
        """Test validation works with float values."""
        records = [MockRecord(price=10.5), MockRecord(price=9.99)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="price"),
            operator=ToBeGreaterThan(threshold=10.0),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # 9.99 fails

    def test_negative_numbers(self):
        """Test validation works with negative numbers."""
        records = [MockRecord(temp=-5), MockRecord(temp=2)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="temp"),
            operator=ToBeGreaterThan(threshold=-10),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True

    def test_null_values_skipped(self):
        """Test null values are skipped in comparison."""
        records = [MockRecord(age=25), MockRecord(age=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeGreaterThan(threshold=18),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 1  # Only non-null values counted

    def test_non_numeric_type_fails(self):
        """Test validation fails with type error for non-numeric values."""
        records = [MockRecord(name="Alice")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToBeGreaterThan(threshold=10),
            severity=None,
            cleaners=[],
        )

        validator = ToBeGreaterThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert "Cannot compare" in result.failures[0]["reason"]


class TestToBeLessThanValidator:
    """Tests for ToBeLessThanValidator."""

    def test_all_less_than_passes(self):
        """Test validation passes when all values are less than threshold."""
        records = [MockRecord(age=15), MockRecord(age=20), MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeLessThan(threshold=30),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0

    def test_some_not_less_fails(self):
        """Test validation fails when some values are not less than threshold."""
        records = [MockRecord(age=25), MockRecord(age=35)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeLessThan(threshold=30),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1
        assert result.failures[0]["value"] == 35

    def test_equal_to_threshold_fails(self):
        """Test validation fails when value equals threshold (not less)."""
        records = [MockRecord(age=30)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeLessThan(threshold=30),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1

    def test_float_comparison(self):
        """Test validation works with float values."""
        records = [MockRecord(price=9.99), MockRecord(price=10.01)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="price"),
            operator=ToBeLessThan(threshold=10.0),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # 10.01 fails

    def test_negative_numbers(self):
        """Test validation works with negative numbers."""
        records = [MockRecord(temp=-15), MockRecord(temp=-5)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="temp"),
            operator=ToBeLessThan(threshold=-10),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # -5 is not < -10

    def test_null_values_skipped(self):
        """Test null values are skipped in comparison."""
        records = [MockRecord(age=25), MockRecord(age=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeLessThan(threshold=30),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 1  # Only non-null values counted

    def test_non_numeric_type_fails(self):
        """Test validation fails with type error for non-numeric values."""
        records = [MockRecord(name="Alice")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToBeLessThan(threshold=10),
            severity=None,
            cleaners=[],
        )

        validator = ToBeLessThanValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert "Cannot compare" in result.failures[0]["reason"]
