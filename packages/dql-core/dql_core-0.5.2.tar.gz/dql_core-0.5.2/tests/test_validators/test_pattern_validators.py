"""Tests for pattern validators."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToMatchPattern
from dql_core.validators import ToMatchPatternValidator
from dql_core.exceptions import ValidationError
from tests.conftest import MockRecord, MockExecutor


class TestToMatchPatternValidator:
    """Tests for ToMatchPatternValidator."""

    def test_all_match_passes(self):
        """Test validation passes when all values match pattern."""
        records = [MockRecord(email="test@example.com"), MockRecord(email="user@test.com")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToMatchPattern(pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$"),
            severity=None,
            cleaners=[],
        )

        validator = ToMatchPatternValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2
        assert result.failed_records == 0

    def test_some_dont_match_fails(self):
        """Test validation fails when some values don't match."""
        records = [MockRecord(email="test@example.com"), MockRecord(email="invalid-email")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToMatchPattern(pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$"),
            severity=None,
            cleaners=[],
        )

        validator = ToMatchPatternValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1

    def test_null_values_skipped(self):
        """Test null values are skipped in pattern matching."""
        records = [MockRecord(email="test@example.com"), MockRecord(email=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToMatchPattern(pattern=r"^[\w\.\+-]+@[\w\.-]+\.\w+$"),
            severity=None,
            cleaners=[],
        )

        validator = ToMatchPatternValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2
        assert result.failed_records == 0
