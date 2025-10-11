"""Tests for custom validators (Story 2.1)."""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToSatisfy
from dql_core.validators import ToSatisfyValidator
from dql_core.exceptions import ValidationError
from tests.conftest import MockRecord, MockExecutor


class TestToSatisfyValidator:
    """Tests for ToSatisfyValidator."""

    def test_simple_lambda_passes(self):
        """Test simple lambda expression that passes."""
        records = [MockRecord(age=25), MockRecord(age=30), MockRecord(age=35)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: x > 18"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is True
        assert result.total_records == 3
        assert result.failed_records == 0

    def test_simple_lambda_fails(self):
        """Test simple lambda expression that fails."""
        records = [MockRecord(age=15), MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: x > 18"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert result.failures[0]["value"] == 15

    def test_complex_lambda_with_string(self):
        """Test complex lambda with string operations."""
        records = [MockRecord(name="Alice"), MockRecord(name="Bob"), MockRecord(name="Alexander")]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="name"),
            operator=ToSatisfy(expression="lambda x: len(x) > 3 and x.startswith('A')"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # Only Bob fails (doesn't start with 'A')

    def test_lambda_with_null_values(self):
        """Test lambda can handle null values (or not)."""
        records = [MockRecord(age=25), MockRecord(age=None)]
        executor = MockExecutor(records)

        # This lambda will fail on None because None > 18 raises TypeError
        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: x > 18"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1
        assert "Error evaluating lambda" in result.failures[0]["reason"]

    def test_lambda_with_null_check(self):
        """Test lambda that explicitly handles nulls."""
        records = [MockRecord(age=25), MockRecord(age=None)]
        executor = MockExecutor(records)

        # Lambda that checks for None first
        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: x is not None and x > 18"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # None fails the lambda

    def test_lambda_with_multiple_conditions(self):
        """Test lambda with multiple AND/OR conditions."""
        records = [
            MockRecord(age=25, status="active"),
            MockRecord(age=15, status="active"),
            MockRecord(age=30, status="inactive"),
        ]
        executor = MockExecutor(records)

        # This lambda needs both fields - will fail since we only check age field
        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: x > 18 and x < 60"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # age=15 fails

    def test_lambda_with_safe_builtins(self):
        """Test lambda can use safe built-in functions."""
        records = [MockRecord(numbers=[1, 2, 3]), MockRecord(numbers=[1, 1])]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="numbers"),
            operator=ToSatisfy(expression="lambda x: sum(x) > 5"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # [1, 1] sum is 2, fails > 5 requirement

    # Security Tests

    def test_import_blocked(self):
        """Test import statements are blocked for security."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: __import__('os').path.exists('/')"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "not allowed" in str(exc_info.value).lower()

    def test_eval_blocked(self):
        """Test eval function is blocked for security."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: eval('1 + 1')"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "not allowed" in str(exc_info.value).lower()

    def test_exec_blocked(self):
        """Test exec function is blocked for security."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: exec('print(1)')"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "not allowed" in str(exc_info.value).lower()

    def test_open_blocked(self):
        """Test open function is blocked for security."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: open('/etc/passwd')"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "not allowed" in str(exc_info.value).lower()

    def test_getattr_blocked(self):
        """Test getattr function is blocked for security."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: getattr(x, '__class__')"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "not allowed" in str(exc_info.value).lower()

    def test_comprehension_blocked(self):
        """Test list comprehensions are blocked for security."""
        records = [MockRecord(numbers=[1, 2, 3])]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="numbers"),
            operator=ToSatisfy(expression="lambda x: [i*2 for i in x]"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "comprehension" in str(exc_info.value).lower()

    def test_invalid_syntax_raises_error(self):
        """Test invalid lambda syntax raises ValidationError."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="lambda x: x > "),  # Incomplete
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "Invalid" in str(exc_info.value) or "syntax" in str(exc_info.value).lower()

    def test_not_a_lambda_raises_error(self):
        """Test non-lambda expression raises ValidationError."""
        records = [MockRecord(age=25)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToSatisfy(expression="x > 18"),  # Not a lambda
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator.validate(records, expectation, executor)

        assert "Invalid" in str(exc_info.value)

    def test_lambda_with_arithmetic(self):
        """Test lambda with arithmetic operations."""
        records = [MockRecord(x=10), MockRecord(x=5)]
        executor = MockExecutor(records)

        expectation = ExpectationNode(
            target=ColumnTarget(field_name="x"),
            operator=ToSatisfy(expression="lambda x: (x * 2) + 5 > 20"),
            severity=None,
            cleaners=[],
        )

        validator = ToSatisfyValidator()
        result = validator.validate(records, expectation, executor)

        assert result.passed is False
        assert result.failed_records == 1  # 5*2+5=15, not >20
