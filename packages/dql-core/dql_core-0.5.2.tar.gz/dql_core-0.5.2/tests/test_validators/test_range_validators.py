"""Tests for range validators."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToBeBetween
from dql_core.validators import ToBeBetweenValidator
from tests.conftest import MockRecord, MockExecutor


class TestToBeBetweenValidator:
    """Tests for ToBeBetweenValidator."""

    def test_all_in_range_passes(self):
        """Test validation passes when all values are in range."""
        records = [MockRecord(age=25), MockRecord(age=30), MockRecord(age=35)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeBetween(min_value=20, max_value=40),
            severity=None,
            cleaners=[],
        )

        validator = ToBeBetweenValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0

    def test_some_out_of_range_fails(self):
        """Test validation fails when some values are out of range."""
        records = [MockRecord(age=25), MockRecord(age=45)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeBetween(min_value=20, max_value=40),
            severity=None,
            cleaners=[],
        )

        validator = ToBeBetweenValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1

    def test_null_values_skipped(self):
        """Test null values are skipped in range checking."""
        records = [MockRecord(age=25), MockRecord(age=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeBetween(min_value=20, max_value=40),
            severity=None,
            cleaners=[],
        )

        validator = ToBeBetweenValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
