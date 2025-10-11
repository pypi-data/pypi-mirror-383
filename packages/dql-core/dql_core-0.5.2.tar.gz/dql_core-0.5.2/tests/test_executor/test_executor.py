"""Tests for validation executor."""

import pytest
from dql_parser import parse_dql
from dql_core.executor import ValidationExecutor
from dql_core.results import ValidationRunResult
from tests.conftest import MockRecord, MockExecutor


class TestValidationExecutor:
    """Tests for ValidationExecutor."""

    def test_execute_simple_validation(self):
        """Test executing a simple validation."""
        dql_text = """
        from Customer
        expect column("email") to_not_be_null
        """
        ast = parse_dql(dql_text)

        records = [MockRecord(email="test@example.com"), MockRecord(email="user@test.com")]
        executor = MockExecutor(records)

        result = executor.execute(ast)

        assert isinstance(result, ValidationRunResult)
        assert result.overall_passed is True
        assert result.total_expectations == 1
        assert result.passed_expectations == 1
        assert result.failed_expectations == 0

    def test_execute_failing_validation(self):
        """Test executing a validation that fails."""
        dql_text = """
        from Customer
        expect column("email") to_not_be_null
        """
        ast = parse_dql(dql_text)

        records = [MockRecord(email="test@example.com"), MockRecord(email=None)]
        executor = MockExecutor(records)

        result = executor.execute(ast)

        assert result.overall_passed is False
        assert result.total_expectations == 1
        assert result.passed_expectations == 0
        assert result.failed_expectations == 1

    def test_execute_multiple_expectations(self):
        """Test executing multiple expectations."""
        dql_text = """
        from Customer
        expect column("email") to_not_be_null
        expect column("age") to_be_between(18, 100)
        """
        ast = parse_dql(dql_text)

        records = [
            MockRecord(email="test@example.com", age=25),
            MockRecord(email="user@test.com", age=30),
        ]
        executor = MockExecutor(records)

        result = executor.execute(ast)

        assert result.overall_passed is True
        assert result.total_expectations == 2
        assert result.passed_expectations == 2

    def test_class_name_to_operator_conversion(self):
        """Test operator class name to operator name conversion."""
        executor = MockExecutor()

        assert executor._class_name_to_operator("ToBeNull") == "to_be_null"
        assert executor._class_name_to_operator("ToNotBeNull") == "to_not_be_null"
        assert executor._class_name_to_operator("ToMatchPattern") == "to_match_pattern"
        assert executor._class_name_to_operator("ToBeBetween") == "to_be_between"
        assert executor._class_name_to_operator("ToBeIn") == "to_be_in"
        assert executor._class_name_to_operator("ToBeUnique") == "to_be_unique"
