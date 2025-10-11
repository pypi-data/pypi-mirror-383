"""Tests for length validators (Story 2.1)."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToHaveLength
from dql_core.validators import ToHaveLengthValidator
from dql_core.exceptions import ValidationError
from tests.conftest import MockRecord, MockExecutor


class TestToHaveLengthValidator:
    """Tests for ToHaveLengthValidator."""

    def test_string_within_length_passes(self):
        """Test validation passes when strings are within length bounds."""
        records = [MockRecord(name="Alice"), MockRecord(name="Bob"), MockRecord(name="Charlie")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=2, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0

    def test_string_too_short_fails(self):
        """Test validation fails when string is too short."""
        records = [MockRecord(name="A"), MockRecord(name="Alice")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=3, max_length=None),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1
        assert len(result.failures) == 1
        assert result.failures[0]["field"] == "name"
        assert result.failures[0]["actual_length"] == 1

    def test_string_too_long_fails(self):
        """Test validation fails when string is too long."""
        records = [MockRecord(name="Alice"), MockRecord(name="VeryLongName")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=None, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1
        assert len(result.failures) == 1
        assert result.failures[0]["actual_length"] == 12

    def test_list_length_validation(self):
        """Test validation works with lists."""
        records = [
            MockRecord(tags=["a", "b"]),
            MockRecord(tags=["x", "y", "z"]),
            MockRecord(tags=["p", "q", "r", "s"]),
        ]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="tags"),
            operator=ToHaveLength(min_length=2, max_length=3),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 3
        assert result.failed_records == 1  # 4-element list fails

    def test_min_length_only(self):
        """Test validation with only minimum length."""
        records = [MockRecord(name="Alice"), MockRecord(name="A")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=3, max_length=None),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1

    def test_max_length_only(self):
        """Test validation with only maximum length."""
        records = [MockRecord(name="Alice"), MockRecord(name="VeryLongName")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=None, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1

    def test_null_values_skipped(self):
        """Test null values are skipped in length checking."""
        records = [MockRecord(name="Alice"), MockRecord(name=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=2, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 1  # Only non-null values counted

    def test_non_iterable_type_fails(self):
        """Test validation fails with type error for non-iterable values."""
        records = [MockRecord(age=42)]  # integer has no length
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToHaveLength(min_length=1, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert "does not have a length" in result.failures[0]["reason"]

    def test_invalid_min_length_raises_error(self):
        """Test negative min_length raises ValidationError."""
        records = [MockRecord(name="Alice")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=-1, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "min_length" in str(exc_info.value)
        assert ">= 0" in str(exc_info.value)

    def test_min_greater_than_max_raises_error(self):
        """Test min_length > max_length raises ValidationError."""
        records = [MockRecord(name="Alice")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=10, max_length=5),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "min_length" in str(exc_info.value)
        assert "max_length" in str(exc_info.value)

    def test_empty_string_with_min_zero_passes(self):
        """Test empty string passes when min_length is 0."""
        records = [MockRecord(name="")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=0, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True

    def test_exact_length_boundary(self):
        """Test exact length at boundaries passes."""
        records = [MockRecord(name="ABC"), MockRecord(name="ABCDEFGHIJ")]  # 3 and 10 chars
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToHaveLength(min_length=3, max_length=10),
            severity=None,
            cleaners=[],
        )

        validator = ToHaveLengthValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
