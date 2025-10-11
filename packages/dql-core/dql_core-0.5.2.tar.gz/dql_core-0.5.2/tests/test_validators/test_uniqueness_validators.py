"""Tests for uniqueness validators."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToBeUnique
from dql_core.validators import ToBeUniqueValidator
from tests.conftest import MockRecord, MockExecutor


class TestToBeUniqueValidator:
    """Tests for ToBeUniqueValidator."""

    def test_all_unique_passes(self):
        """Test validation passes when all values are unique."""
        records = [MockRecord(email="a@b.com"), MockRecord(email="c@d.com")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToBeUnique(),
            severity=None,
            cleaners=[],
        )

        validator = ToBeUniqueValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2
        assert result.failed_records == 0

    def test_duplicates_fail(self):
        """Test validation fails when duplicates exist."""
        records = [
            MockRecord(email="test@example.com"),
            MockRecord(email="test@example.com"),
        ]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToBeUnique(),
            severity=None,
            cleaners=[],
        )

        validator = ToBeUniqueValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1

    def test_null_values_not_considered_duplicates(self):
        """Test null values are not considered duplicates."""
        records = [
            MockRecord(email=None),
            MockRecord(email=None),
            MockRecord(email="test@example.com"),
        ]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToBeUnique(),
            severity=None,
            cleaners=[],
        )

        validator = ToBeUniqueValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
