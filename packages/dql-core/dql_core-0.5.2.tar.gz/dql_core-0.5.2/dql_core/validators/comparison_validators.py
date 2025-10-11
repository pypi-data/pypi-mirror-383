"""Validators for numeric comparison checks.

Implements validators for greater than / less than comparisons.

[Source: Story 2.1 - Advanced Operators Support]
"""

from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToBeGreaterThanValidator(Validator):
    """Validator for to_be_greater_than operator.

    Validates that numeric field values are greater than a threshold.

    Example:
        expect column("age") to_be_greater_than(18) severity critical
        expect column("price") to_be_greater_than(0.0) severity warning
    """

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are greater than threshold.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToBeGreaterThan operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status

        Raises:
            ValidationError: If operator or target is invalid
        """
        from dql_parser.ast_nodes import ColumnTarget, ToBeGreaterThan

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_be_greater_than only works with column targets")

        if not isinstance(expectation.operator, ToBeGreaterThan):
            raise ValidationError("Expected ToBeGreaterThan operator")

        field_name = expectation.target.field_name
        threshold = expectation.operator.threshold

        total = 0
        failed = 0
        failures = []

        for record in records:
            value = executor.get_field_value(record, field_name)

            # Skip null values
            if value is None:
                continue

            total += 1

            try:
                if not (value > threshold):
                    failed += 1
                    failures.append(
                        {
                            "record": str(record),
                            "field": field_name,
                            "value": value,
                            "threshold": threshold,
                            "reason": f"Value {value} is not greater than {threshold}",
                        }
                    )
            except TypeError as e:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "threshold": threshold,
                        "reason": f"Cannot compare value {repr(value)} of type {type(value).__name__} "
                        f"with threshold {threshold}: {e}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )


class ToBeLessThanValidator(Validator):
    """Validator for to_be_less_than operator.

    Validates that numeric field values are less than a threshold.

    Example:
        expect column("age") to_be_less_than(100) severity warning
        expect column("discount") to_be_less_than(1.0) severity critical
    """

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values are less than threshold.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToBeLessThan operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status

        Raises:
            ValidationError: If operator or target is invalid
        """
        from dql_parser.ast_nodes import ColumnTarget, ToBeLessThan

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_be_less_than only works with column targets")

        if not isinstance(expectation.operator, ToBeLessThan):
            raise ValidationError("Expected ToBeLessThan operator")

        field_name = expectation.target.field_name
        threshold = expectation.operator.threshold

        total = 0
        failed = 0
        failures = []

        for record in records:
            value = executor.get_field_value(record, field_name)

            # Skip null values
            if value is None:
                continue

            total += 1

            try:
                if not (value < threshold):
                    failed += 1
                    failures.append(
                        {
                            "record": str(record),
                            "field": field_name,
                            "value": value,
                            "threshold": threshold,
                            "reason": f"Value {value} is not less than {threshold}",
                        }
                    )
            except TypeError as e:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "threshold": threshold,
                        "reason": f"Cannot compare value {repr(value)} of type {type(value).__name__} "
                        f"with threshold {threshold}: {e}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )
