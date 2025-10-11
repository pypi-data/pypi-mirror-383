"""Pytest fixtures for dql-core tests."""

import pytest
from typing import Any, Iterable, Set, Dict

from dql_core.executor import ValidationExecutor
from dql_core.exceptions import ExecutorError


class MockRecord:
    """Mock record object for testing."""

    def __init__(self, **fields):
        for key, value in fields.items():
            setattr(self, key, value)

    def __str__(self):
        fields = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        return f"MockRecord({fields})"


class MockExecutor(ValidationExecutor):
    """Mock executor for testing validators."""

    def __init__(self, records=None, validator_registry=None, models=None):
        super().__init__(validator_registry)
        self._records = records or []
        self._models: Dict[str, Any] = models or {}  # model_name -> model data

    def get_records(self, model_name: str) -> Iterable[Any]:
        """Return mock records."""
        return self._records

    def filter_records(self, records: Iterable[Any], condition: Any) -> Iterable[Any]:
        """Simple mock filtering (just return all records)."""
        return records

    def count_records(self, records: Iterable[Any]) -> int:
        """Count records."""
        return len(list(records))

    def get_field_value(self, record: Any, field_name: str) -> Any:
        """Get field value from mock record."""
        if isinstance(record, dict):
            return record.get(field_name)
        return getattr(record, field_name, None)

    def get_model(self, model_name: str) -> Any:
        """Get mock model by name."""
        if model_name not in self._models:
            raise ExecutorError(f"Model '{model_name}' not found")
        return self._models[model_name]

    def query_field_values(
        self, model: Any, field_name: str, filter_values: Set[Any]
    ) -> Set[Any]:
        """Query field values from mock model."""
        # model is expected to be a list of records
        if not isinstance(model, list):
            raise ExecutorError(f"Invalid model type: {type(model)}")

        result = set()
        for record in model:
            value = self.get_field_value(record, field_name)
            if value in filter_values:
                result.add(value)
        return result


@pytest.fixture
def mock_executor():
    """Fixture providing a mock executor."""
    return MockExecutor()


@pytest.fixture
def sample_records():
    """Fixture providing sample records."""
    return [
        MockRecord(id=1, email="test@example.com", age=25, status="active"),
        MockRecord(id=2, email="user@test.com", age=30, status="active"),
        MockRecord(id=3, email=None, age=35, status="inactive"),
    ]
