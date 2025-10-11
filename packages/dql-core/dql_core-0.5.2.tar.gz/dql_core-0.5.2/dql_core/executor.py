"""Abstract validation executor."""

import time
from abc import ABC, abstractmethod
from typing import Any, Iterable, Set

from dql_core.results import ValidationRunResult, ExpectationResult, ValidationResult
from dql_core.exceptions import ExecutorError
from dql_core.validators import default_registry


class ValidationExecutor(ABC):
    """Abstract base class for validation executors.

    Framework-specific implementations must subclass and implement
    abstract methods for data access.
    """

    def __init__(self, validator_registry=None):
        """Initialize executor with validator registry.

        Args:
            validator_registry: ValidatorRegistry to use (defaults to default_registry)
        """
        self.validator_registry = validator_registry or default_registry

    @abstractmethod
    def get_records(self, model_name: str) -> Iterable[Any]:
        """Retrieve records for the specified model.

        Args:
            model_name: Name of the model/table to query

        Returns:
            Iterable of records (QuerySet, list, generator, etc.)

        Raises:
            ExecutorError: If model not found or query fails
        """
        pass

    @abstractmethod
    def filter_records(self, records: Iterable[Any], condition: Any) -> Iterable[Any]:
        """Filter records based on condition.

        Args:
            records: Records to filter
            condition: Filtering condition (framework-specific AST node)

        Returns:
            Filtered records

        Raises:
            ExecutorError: If filtering fails
        """
        pass

    @abstractmethod
    def count_records(self, records: Iterable[Any]) -> int:
        """Count records in iterable.

        Args:
            records: Records to count

        Returns:
            Number of records

        Raises:
            ExecutorError: If counting fails
        """
        pass

    @abstractmethod
    def get_field_value(self, record: Any, field_name: str) -> Any:
        """Get field value from record.

        Args:
            record: Single record object
            field_name: Name of field to retrieve

        Returns:
            Field value

        Raises:
            ExecutorError: If field doesn't exist or access fails
        """
        pass

    @abstractmethod
    def get_model(self, model_name: str) -> Any:
        """Get model class by name.

        This method resolves a model name string (e.g., "Customer", "myapp.Order")
        to the actual model class object. The implementation is framework-specific
        (Django uses django.apps.apps.get_model(), SQLAlchemy uses registry, etc.).

        Args:
            model_name: Name of the model. Format depends on framework:
                - Django: "app_label.ModelName" or just "ModelName" (current app)
                - SQLAlchemy: "ModelName" (from declarative base)

        Returns:
            Model class object (e.g., Django Model class, SQLAlchemy declarative class)

        Raises:
            ExecutorError: If model not found or name is invalid

        Example:
            model = executor.get_model("Customer")
            # Returns: <class 'myapp.models.Customer'>
        """
        pass

    @abstractmethod
    def query_field_values(
        self, model: Any, field_name: str, filter_values: Set[Any]
    ) -> Set[Any]:
        """Query unique field values from model where field is in filter set.

        This method performs a bulk query to retrieve field values from the target
        model, filtering by a set of candidate values. Used for efficient FK validation
        to avoid N+1 queries.

        The implementation should:
        1. Query the model for records where field_name is in filter_values
        2. Extract unique values of field_name from matching records
        3. Return as a set for fast membership checking

        Framework-specific implementations:
        - Django: Model.objects.filter(field_name__in=filter_values).values_list(
                    field_name, flat=True).distinct()
        - SQLAlchemy: session.query(Model.field_name).filter(
                        Model.field_name.in_(filter_values)).distinct().all()

        Args:
            model: Model class to query
            field_name: Field name to retrieve values for
            filter_values: Set of values to filter by (SQL: WHERE field IN (...))

        Returns:
            Set of unique field values found in the model

        Raises:
            ExecutorError: If query fails or field doesn't exist

        Example:
            # Get all customer_ids that exist in Customer table
            existing_ids = executor.query_field_values(
                Customer,
                "customer_id",
                {1, 2, 3, 4, 5}
            )
            # Returns: {1, 2, 5}  (if 3 and 4 don't exist in database)
        """
        pass

    def execute(self, ast: Any) -> ValidationRunResult:
        """Execute validation from DQL AST.

        This is a concrete method that orchestrates validation using
        the abstract methods above.

        Args:
            ast: DQL File AST from parser

        Returns:
            ValidationRunResult with all expectation results

        Raises:
            ExecutorError: If execution fails
        """
        from dql_parser.ast_nodes import DQLFile, RowTarget

        if not isinstance(ast, DQLFile):
            raise ExecutorError("Expected DQLFile AST node")

        start_time = time.time()
        expectation_results = []
        overall_passed = True

        for from_block in ast.from_blocks:
            model_name = from_block.model_name

            try:
                # Get all records for this model
                records = self.get_records(model_name)
            except Exception as e:
                raise ExecutorError(f"Failed to get records for model '{model_name}': {e}")

            for expectation in from_block.expectations:
                try:
                    # Handle row-level filtering if needed
                    if isinstance(expectation.target, RowTarget):
                        if expectation.target.condition:
                            records = self.filter_records(records, expectation.target.condition)

                    # Get operator name from expectation.operator class
                    operator_type = type(expectation.operator).__name__
                    # Convert class name to operator name (ToBeNull -> to_be_null)
                    operator_name = self._class_name_to_operator(operator_type)

                    # Get validator for this operator
                    validator_class = self.validator_registry.get(operator_name)
                    validator = validator_class()

                    # Execute validation
                    validation_result = validator.validate(records, expectation, self)

                    # Create expectation result
                    expectation_result = ExpectationResult(
                        expectation=expectation,
                        passed=validation_result.passed,
                        validation_result=validation_result,
                        severity=expectation.severity,
                        model_name=model_name,
                    )

                    expectation_results.append(expectation_result)

                    if not validation_result.passed:
                        overall_passed = False

                except Exception as e:
                    # Catch validation errors and create failed result
                    validation_result = ValidationResult(
                        passed=False,
                        total_records=0,
                        failed_records=0,
                        failures=[{"error": str(e)}],
                    )
                    expectation_result = ExpectationResult(
                        expectation=expectation,
                        passed=False,
                        validation_result=validation_result,
                        severity=expectation.severity,
                        model_name=model_name,
                    )
                    expectation_results.append(expectation_result)
                    overall_passed = False

        duration = time.time() - start_time

        return ValidationRunResult(
            overall_passed=overall_passed,
            expectation_results=expectation_results,
            duration=duration,
        )

    def _class_name_to_operator(self, class_name: str) -> str:
        """Convert operator class name to operator name.

        Args:
            class_name: Class name (e.g., 'ToBeNull')

        Returns:
            Operator name (e.g., 'to_be_null')
        """
        # Convert PascalCase to snake_case
        import re

        # Insert underscore before capitals
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", class_name)
        # Handle consecutive capitals
        s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
        return s2.lower()
