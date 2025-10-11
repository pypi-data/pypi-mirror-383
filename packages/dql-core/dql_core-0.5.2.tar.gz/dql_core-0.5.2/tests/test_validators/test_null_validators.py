"""Tests for null validators."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToBeNull, ToNotBeNull
from dql_core.validators import ToBeNullValidator, ToNotBeNullValidator
from dql_core.exceptions import ValidationError
from tests.conftest import MockRecord, MockExecutor


class TestToBeNullValidator:
    """Tests for ToBeNullValidator."""

    def test_all_null_passes(self):
        """Test validation passes when all values are null."""
        records = [MockRecord(email=None), MockRecord(email=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"), operator=ToBeNull(), severity=None, cleaners=[]
        )

        validator = ToBeNullValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2
        assert result.failed_records == 0

    def test_some_not_null_fails(self):
        """Test validation fails when some values are not null."""
        records = [MockRecord(email=None), MockRecord(email="test@example.com")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"), operator=ToBeNull(), severity=None, cleaners=[]
        )

        validator = ToBeNullValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1
        assert len(result.failures) == 1


class TestToNotBeNullValidator:
    """Tests for ToNotBeNullValidator."""

    def test_all_not_null_passes(self):
        """Test validation passes when all values are not null."""
        records = [MockRecord(email="a@b.com"), MockRecord(email="c@d.com")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToNotBeNull(),
            severity=None,
            cleaners=[],
        )

        validator = ToNotBeNullValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 2
        assert result.failed_records == 0

    def test_some_null_fails(self):
        """Test validation fails when some values are null."""
        records = [MockRecord(email="test@example.com"), MockRecord(email=None)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToNotBeNull(),
            severity=None,
            cleaners=[],
        )

        validator = ToNotBeNullValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.total_records == 2
        assert result.failed_records == 1
        assert len(result.failures) == 1
