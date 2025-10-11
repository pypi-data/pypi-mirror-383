"""Validators for foreign key reference operators."""

from typing import Any, Iterable, Set, Union, List

from dql_core.validators.base import Validator
from dql_core.results import ValidationResult
from dql_core.exceptions import ValidationError


class ToReferenceValidator(Validator):
    """Validator for to_reference operator (foreign key validation).

    Validates that foreign key values in source records exist in the target model.
    Supports both single field and composite key validation.

    Examples:
        # Single field FK
        EXPECT column('customer_id') to_reference(Customer, 'id')

        # Composite key
        EXPECT column('customer_id') to_reference(Order, ['customer_id', 'region_id'])
    """

    def validate(
        self, records: Iterable[Any], expectation: Any, executor: Any
    ) -> ValidationResult:
        """Validate foreign key references exist in target model.

        Args:
            records: Source records to validate
            expectation: ExpectationNode with ToReference operator
            executor: ValidationExecutor instance

        Returns:
            ValidationResult with pass/fail status and failure details

        Raises:
            ValidationError: If target model not found or invalid arguments
        """
        from dql_parser.ast_nodes import ColumnTarget, ToReference

        # Extract AST nodes
        if not isinstance(expectation.target, ColumnTarget):
            raise ValidationError("to_reference only works with column targets")

        if not isinstance(expectation.operator, ToReference):
            raise ValidationError("Expected ToReference operator")

        source_field = expectation.target.field_name
        target_model_name = expectation.operator.target_model
        target_field = expectation.operator.target_field

        # Handle single field vs composite key
        if isinstance(target_field, str):
            return self._validate_single_field(
                records, source_field, target_model_name, target_field, executor
            )
        elif isinstance(target_field, list):
            return self._validate_composite_key(
                records, source_field, target_model_name, target_field, executor
            )
        else:
            raise ValidationError(
                f"target_field must be string or list, got {type(target_field).__name__}"
            )

    def _validate_single_field(
        self,
        records: Iterable[Any],
        source_field: str,
        target_model_name: str,
        target_field: str,
        executor: Any,
    ) -> ValidationResult:
        """Validate single field foreign key reference.

        Uses bulk query approach to avoid N+1 queries:
        1. Collect all FK values from source records
        2. Query target model once for all values
        3. Compare and identify missing references
        """
        # Step 1: Collect all FK values from source records (skip nulls per AC5)
        source_fk_values = set()
        records_list = list(records)  # Convert to list for two-pass iteration

        for record in records_list:
            fk_value = executor.get_field_value(record, source_field)
            if fk_value is not None:  # Skip null FK values per AC5
                source_fk_values.add(fk_value)

        # If no non-null FK values, validation passes
        if not source_fk_values:
            return ValidationResult(
                passed=True, total_records=0, failed_records=0, failures=[]
            )

        # Step 2: Get target model
        try:
            target_model = executor.get_model(target_model_name)
        except Exception as e:
            raise ValidationError(
                f"Failed to get target model '{target_model_name}': {e}"
            )

        # Step 3: Query target model once for all FK values
        try:
            existing_fk_values = executor.query_field_values(
                target_model, target_field, source_fk_values
            )
        except Exception as e:
            raise ValidationError(
                f"Failed to query target model '{target_model_name}.{target_field}': {e}"
            )

        # Step 4: Find missing FK values (set difference)
        missing_fk_values = source_fk_values - existing_fk_values

        # Step 5: Iterate records to identify failures
        total = 0
        failed = 0
        failures = []

        for record in records_list:
            fk_value = executor.get_field_value(record, source_field)

            # Skip null values (don't count in total for consistency with other validators)
            if fk_value is None:
                continue

            total += 1

            if fk_value in missing_fk_values:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": source_field,
                        "value": fk_value,
                        "target_model": target_model_name,
                        "target_field": target_field,
                        "reason": f"Foreign key value {repr(fk_value)} does not exist "
                        f"in {target_model_name}.{target_field}",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )

    def _validate_composite_key(
        self,
        records: Iterable[Any],
        source_field: str,
        target_model_name: str,
        target_fields: List[str],
        executor: Any,
    ) -> ValidationResult:
        """Validate composite key foreign key reference.

        For composite keys, the source_field should contain a tuple/list of values
        that correspond to the target_fields.

        Example:
            source_field = "order_key"  # Contains (customer_id, region_id)
            target_fields = ["customer_id", "region_id"]
        """
        # For composite keys, we need to query based on multiple fields
        # This is more complex and requires checking combinations
        records_list = list(records)
        total = 0
        failed = 0
        failures = []

        # Collect all composite key values from source
        source_key_tuples = set()
        type_error_records = []  # Track records with type/length errors

        for record in records_list:
            key_value = executor.get_field_value(record, source_field)

            # Skip null values
            if key_value is None:
                continue

            # key_value should be a tuple/list matching target_fields length
            if not isinstance(key_value, (tuple, list)):
                total += 1
                failed += 1
                type_error_records.append(id(record))
                failures.append(
                    {
                        "record": str(record),
                        "field": source_field,
                        "value": key_value,
                        "reason": f"Composite key value must be tuple/list, got {type(key_value).__name__}",
                    }
                )
                continue

            if len(key_value) != len(target_fields):
                total += 1
                failed += 1
                type_error_records.append(id(record))
                failures.append(
                    {
                        "record": str(record),
                        "field": source_field,
                        "value": key_value,
                        "reason": f"Composite key length mismatch: expected {len(target_fields)} fields, got {len(key_value)}",
                    }
                )
                continue

            source_key_tuples.add(tuple(key_value))
            total += 1

        # If no valid composite keys to check, return with any type errors
        if not source_key_tuples:
            return ValidationResult(
                passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
            )

        # Get target model
        try:
            target_model = executor.get_model(target_model_name)
        except Exception as e:
            raise ValidationError(
                f"Failed to get target model '{target_model_name}': {e}"
            )

        # For composite keys, we need to build tuples from target model records
        # Since the model object is a list of records in MockExecutor,
        # we can iterate directly
        try:
            target_key_tuples = set()

            # target_model is already a list of records (from executor.get_model())
            if isinstance(target_model, list):
                for target_record in target_model:
                    key_tuple = tuple(
                        executor.get_field_value(target_record, field)
                        for field in target_fields
                    )
                    target_key_tuples.add(key_tuple)
            else:
                # If not a list, try getting records via executor
                target_records = executor.get_records(target_model_name)
                for target_record in target_records:
                    key_tuple = tuple(
                        executor.get_field_value(target_record, field)
                        for field in target_fields
                    )
                    target_key_tuples.add(key_tuple)

        except Exception as e:
            raise ValidationError(
                f"Failed to query target model '{target_model_name}': {e}"
            )

        # Find missing composite keys
        missing_keys = source_key_tuples - target_key_tuples

        # Identify failed records (only those not already counted as type errors)
        for record in records_list:
            # Skip records already counted in type/length errors
            if id(record) in type_error_records:
                continue

            key_value = executor.get_field_value(record, source_field)

            if key_value is None:
                continue

            if not isinstance(key_value, (tuple, list)):
                continue  # Already counted in failures above

            if len(key_value) != len(target_fields):
                continue  # Already counted in failures above

            key_tuple = tuple(key_value)
            if key_tuple in missing_keys:
                failed += 1
                failures.append(
                    {
                        "record": str(record),
                        "field": source_field,
                        "value": key_value,
                        "target_model": target_model_name,
                        "target_fields": target_fields,
                        "reason": f"Composite foreign key {key_value} does not exist "
                        f"in {target_model_name}({', '.join(target_fields)})",
                    }
                )

        return ValidationResult(
            passed=(failed == 0), total_records=total, failed_records=failed, failures=failures
        )
