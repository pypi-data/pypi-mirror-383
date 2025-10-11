"""Tests for enum validators."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToBeIn
from dql_core.validators import ToBeInValidator
from tests.conftest import MockRecord, MockExecutor


class TestToBeInValidator:
    """Tests for ToBeInValidator."""

    def test_all_in_set_passes(self):
        """Test validation passes when all values are in allowed set."""
        records = [MockRecord(status="active"), MockRecord(status="inactive")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="status"),
            operator=ToBeIn(values=["active", "inactive", "pending"]),
            severity=None,
            cleaners=[],
        )

        validator = ToBeInValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2
        assert result.failed_records == 0

    def test_some_not_in_set_fails(self):
        """Test validation fails when some values are not in set."""
        records = [MockRecord(status="active"), MockRecord(status="unknown")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="status"),
            operator=ToBeIn(values=["active", "inactive"]),
            severity=None,
            cleaners=[],
        )

        validator = ToBeInValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1

    def test_null_values_skipped(self):
        """Test null values are skipped in set membership."""
        records = [MockRecord(status="active"), MockRecord(status=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="status"),
            operator=ToBeIn(values=["active", "inactive"]),
            severity=None,
            cleaners=[],
        )

        validator = ToBeInValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
