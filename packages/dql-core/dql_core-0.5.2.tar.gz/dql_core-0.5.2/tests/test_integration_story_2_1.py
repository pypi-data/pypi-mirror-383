"""Integration tests for Story 2.1 Advanced Operators.

Tests end-to-end functionality of all new operators:
- to_have_length
- to_be_greater_than
- to_be_less_than
- to_satisfy

These tests verify that validators work correctly when used together
and handle edge cases properly.
"""

import pytest
from dql_parser.ast_nodes import ExpectationNode, ColumnTarget, ToHaveLength, ToBeGreaterThan, ToBeLessThan, ToSatisfy
from dql_core.validators import default_registry
from dql_core.exceptions import ValidationError
from tests.conftest import MockRecord, MockExecutor


class TestStory2_1Integration:
    """Integration tests for Story 2.1 advanced operators."""

    def test_all_operators_registered(self):
        """Verify all new operators are registered in default registry."""
        assert default_registry.has("to_have_length")
        assert default_registry.has("to_be_greater_than")
        assert default_registry.has("to_be_less_than")
        assert default_registry.has("to_satisfy")

    def test_length_validation_integration(self):
        """Integration test for length validation."""
        records = [
            MockRecord(username="alice", email="alice@example.com"),
            MockRecord(username="bob", email="bob@example.com"),
            MockRecord(username="charlie_long_name", email="charlie@example.com"),
        ]

        # Username length validation
        expectation = ExpectationNode(
            target=ColumnTarget(field_name="username"),
            operator=ToHaveLength(min_length=3, max_length=10),
            severity=None,
            cleaners=[],
        )

        executor = MockExecutor(records=records, validator_registry=default_registry)
        validator = default_registry.get("to_have_length")()
        result = validator.validate(records, expectation, executor)

        # alice (5), bob (3) pass; charlie_long_name (17) fails
        assert result.passed is False
        assert result.failed_records == 1
        assert result.total_records == 3

    def test_comparison_validation_integration(self):
        """Integration test for comparison operators."""
        records = [
            MockRecord(age=25, score=85.5),
            MockRecord(age=17, score=92.0),
            MockRecord(age=30, score=78.0),
        ]

        executor = MockExecutor(records=records, validator_registry=default_registry)

        # Age must be greater than 18
        age_expectation = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeGreaterThan(threshold=18),
            severity=None,
            cleaners=[],
        )

        age_validator = default_registry.get("to_be_greater_than")()
        age_result = age_validator.validate(records, age_expectation, executor)

        # Age: 17 fails
        assert age_result.passed is False
        assert age_result.failed_records == 1

        # Score must be less than 90
        score_expectation = ExpectationNode(
            target=ColumnTarget(field_name="score"),
            operator=ToBeLessThan(threshold=90.0),
            severity=None,
            cleaners=[],
        )

        score_validator = default_registry.get("to_be_less_than")()
        score_result = score_validator.validate(records, score_expectation, executor)

        # Score: 92.0 fails
        assert score_result.passed is False
        assert score_result.failed_records == 1

    def test_custom_lambda_validation_integration(self):
        """Integration test for custom lambda validation."""
        records = [
            MockRecord(email="valid@example.com"),
            MockRecord(email="invalid-email"),
            MockRecord(email="another@test.org"),
        ]

        # Email must contain @ and have reasonable length
        expectation = ExpectationNode(
            target=ColumnTarget(field_name="email"),
            operator=ToSatisfy(expression="lambda x: '@' in x and len(x) > 5"),
            severity=None,
            cleaners=[],
        )

        executor = MockExecutor(records=records, validator_registry=default_registry)
        validator = default_registry.get("to_satisfy")()
        result = validator.validate(records, expectation, executor)

        # "invalid-email" fails (no @)
        assert result.passed is False
        assert result.failed_records == 1
        assert result.total_records == 3

    def test_combined_validations_realistic_scenario(self):
        """Test realistic scenario combining multiple advanced operators."""
        # Simulate user registration data
        records = [
            MockRecord(username="alice", age=25, bio="Software engineer", score=95),
            MockRecord(username="b", age=17, bio="Student", score=85),
            MockRecord(username="charlie_very_long_username", age=30, bio="Designer", score=92),
            MockRecord(username="dave", age=22, bio="PM", score=88),
        ]

        executor = MockExecutor(records=records, validator_registry=default_registry)

        # Username length: 3-15 characters
        username_exp = ExpectationNode(
            target=ColumnTarget(field_name="username"),
            operator=ToHaveLength(min_length=3, max_length=15),
            severity=None,
            cleaners=[],
        )
        username_result = default_registry.get("to_have_length")().validate(records, username_exp, executor)
        # "b" (too short), "charlie_very_long_username" (too long) fail
        assert username_result.failed_records == 2

        # Age must be 18 or older
        age_exp = ExpectationNode(
            target=ColumnTarget(field_name="age"),
            operator=ToBeGreaterThan(threshold=17),  # > 17 means >= 18
            severity=None,
            cleaners=[],
        )
        age_result = default_registry.get("to_be_greater_than")().validate(records, age_exp, executor)
        # 17 fails
        assert age_result.failed_records == 1

        # Bio must have some content
        bio_exp = ExpectationNode(
            target=ColumnTarget(field_name="bio"),
            operator=ToHaveLength(min_length=2, max_length=None),
            severity=None,
            cleaners=[],
        )
        bio_result = default_registry.get("to_have_length")().validate(records, bio_exp, executor)
        # "PM" passes (length 2), all others pass
        assert bio_result.passed is True

        # Score must be reasonable
        score_exp = ExpectationNode(
            target=ColumnTarget(field_name="score"),
            operator=ToSatisfy(expression="lambda x: 0 <= x <= 100"),
            severity=None,
            cleaners=[],
        )
        score_result = default_registry.get("to_satisfy")().validate(records, score_exp, executor)
        # all pass
        assert score_result.passed is True

    def test_lambda_security_integration(self):
        """Integration test verifying lambda security restrictions work end-to-end."""
        records = [MockRecord(value=10)]
        executor = MockExecutor(records=records, validator_registry=default_registry)
        validator = default_registry.get("to_satisfy")()

        dangerous_expressions = [
            "lambda x: __import__('os').system('ls')",
            "lambda x: eval('1+1')",
            "lambda x: open('/etc/passwd')",
        ]

        for expr in dangerous_expressions:
            expectation = ExpectationNode(
                target=ColumnTarget(field_name="value"),
                operator=ToSatisfy(expression=expr),
                severity=None,
                cleaners=[],
            )

            with pytest.raises(ValidationError) as exc_info:
                validator.validate(records, expectation, executor)

            assert "not allowed" in str(exc_info.value).lower()

    def test_null_handling_across_operators(self):
        """Test null value handling is consistent across all new operators."""
        records = [
            MockRecord(field1="value", field2=10, field3="text", field4=5),
            MockRecord(field1=None, field2=None, field3=None, field4=None),
        ]

        executor = MockExecutor(records=records, validator_registry=default_registry)

        # to_have_length should skip nulls
        exp1 = ExpectationNode(
            target=ColumnTarget(field_name="field1"),
            operator=ToHaveLength(min_length=3, max_length=10),
            severity=None,
            cleaners=[],
        )
        result1 = default_registry.get("to_have_length")().validate(records, exp1, executor)
        assert result1.total_records == 1  # null skipped

        # to_be_greater_than should skip nulls
        exp2 = ExpectationNode(
            target=ColumnTarget(field_name="field2"),
            operator=ToBeGreaterThan(threshold=5),
            severity=None,
            cleaners=[],
        )
        result2 = default_registry.get("to_be_greater_than")().validate(records, exp2, executor)
        assert result2.total_records == 1  # null skipped

        # to_be_less_than should skip nulls
        exp3 = ExpectationNode(
            target=ColumnTarget(field_name="field3"),
            operator=ToBeLessThan(threshold=100),
            severity=None,
            cleaners=[],
        )
        result3 = default_registry.get("to_be_less_than")().validate(records, exp3, executor)
        assert result3.total_records == 1  # null skipped

        # to_satisfy doesn't auto-skip nulls - lambda decides
        exp4 = ExpectationNode(
            target=ColumnTarget(field_name="field4"),
            operator=ToSatisfy(expression="lambda x: x is not None and x > 0"),
            severity=None,
            cleaners=[],
        )
        result4 = default_registry.get("to_satisfy")().validate(records, exp4, executor)
        assert result4.total_records == 2  # None evaluated
        assert result4.failed_records == 1  # None fails lambda

    def test_edge_cases_integration(self):
        """Test edge cases across all operators."""
        records = [
            MockRecord(empty_string="", zero=0, negative=-5),
        ]

        executor = MockExecutor(records=records, validator_registry=default_registry)

        # Empty string with min_length=0 should pass
        exp1 = ExpectationNode(
            target=ColumnTarget(field_name="empty_string"),
            operator=ToHaveLength(min_length=0, max_length=10),
            severity=None,
            cleaners=[],
        )
        result1 = default_registry.get("to_have_length")().validate(records, exp1, executor)
        assert result1.passed is True  # empty string passes

        # Zero is not greater than 0
        exp2 = ExpectationNode(
            target=ColumnTarget(field_name="zero"),
            operator=ToBeGreaterThan(threshold=0),
            severity=None,
            cleaners=[],
        )
        result2 = default_registry.get("to_be_greater_than")().validate(records, exp2, executor)
        assert result2.passed is False  # 0 not > 0

        # Negative numbers work with less_than
        exp3 = ExpectationNode(
            target=ColumnTarget(field_name="negative"),
            operator=ToBeLessThan(threshold=0),
            severity=None,
            cleaners=[],
        )
        result3 = default_registry.get("to_be_less_than")().validate(records, exp3, executor)
        assert result3.passed is True  # -5 < 0
