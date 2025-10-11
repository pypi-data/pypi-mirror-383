"""Validators for length checks.

Implements validators for string/collection length constraints.

[Source: Story 2.1 - Advanced Operators Support]
"""

from typing import Any, Iterable

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToHaveLengthValidator(Validator):
    """Validator for to_have_length operator.

    Validates that string/collection length is within specified bounds.
    Supports min_length, max_length, or both.

    Example:
        expect column("name") to_have_length(2, 50) severity critical
        expect column("tags") to_have_length(1, None) severity warning  # min only
    """

    def validate(self, records: Iterable[Any], expectation: Any, executor: Any) -> ValidationResult:
        """Validate that field values have length within specified bounds.

        Args:
            records: Records to validate
            expectation: Expectation with ColumnTarget and ToHaveLength operator
            executor: ValidationExecutor for getting field values

        Returns:
            ValidationResult with pass/fail status

        Raises:
            ValidationError: If operator or target is invalid
        """
        from dql_parser.ast_nodes import ColumnTarget, ToHaveLength

        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_have_length only works with column targets")

        if not isinstance(expectation.operator, ToHaveLength):
            raise ValidationError("Expected ToHaveLength operator")

        field_name = expectation.target.field_name
        min_length = expectation.operator.min_length
        max_length = expectation.operator.max_length

        # Validate arguments
        if min_length is not None and min_length < 0:
            raise ValidationError(f"min_length ({min_length}) must be >= 0")

        if max_length is not None and max_length < 0:
            raise ValidationError(f"max_length ({max_length}) must be >= 0")

        if min_length is not None and max_length is not None and min_length > max_length:
            raise ValidationError(
                f"min_length ({min_length}) must be <= max_length ({max_length})"
            )

        total = 0
        failed = 0
        failures = []

        for record in records:
            value = executor.get_field_value(record, field_name)

            # Skip null values
            if value is None:
                continue

            total += 1

            # Get length (works for strings, lists, tuples, sets, dicts, etc.)
            try:
                actual_length = len(value)
            except TypeError:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "reason": f"Value {repr(value)} of type {type(value).__name__} "
                        f"does not have a length (not a string or collection)",
                    }
                )
                continue

            # Check length constraints
            failed_constraint = False
            reason_parts = []

            if min_length is not None and actual_length < min_length:
                failed_constraint = True
                reason_parts.append(f"length {actual_length} < min {min_length}")

            if max_length is not None and actual_length > max_length:
                failed_constraint = True
                reason_parts.append(f"length {actual_length} > max {max_length}")

            if failed_constraint:
                failed += 1
                reason = f"Length constraint violated: {', '.join(reason_parts)}"
                failures.append(
                    {
                        "record": str(record),
                        "field": field_name,
                        "value": value,
                        "actual_length": actual_length,
                        "min_length": min_length,
                        "max_length": max_length,
                        "reason": reason,
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )
