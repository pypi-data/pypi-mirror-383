# Validator Guide

Learn how to create custom validators for dql-core.

## Quick Example

```python
from dql_core import Validator, default_registry, ValidationResult

class ToBePositiveValidator(Validator):
    """Validates that numeric values are positive."""

    def validate(self, records, expectation, executor):
        field_name = expectation.target.field_name
        failed_records = []

        for record in records:
            value = executor.get_field_value(record, field_name)
            if value is not None and value <= 0:
                failed_records.append({
                    "record": record,
                    "field": field_name,
                    "value": value,
                    "reason": f"Expected positive, got {value}"
                })

        return ValidationResult(
            passed=len(failed_records) == 0,
            total_records=executor.count_records(records),
            failed_records=len(failed_records),
            failures=failed_records
        )

# Register it
default_registry.register("to_be_positive", ToBePositiveValidator)
```

Now use in DQL:
```dql
FROM Product
EXPECT column("price") to_be_positive
```

## Validator Interface

All validators must implement:

```python
from abc import ABC, abstractmethod
from typing import Any, Iterable
from dql_parser.ast_nodes import ExpectationNode
from dql_core.results import ValidationResult

class Validator(ABC):
    @abstractmethod
    def validate(
        self,
        records: Iterable[Any],
        expectation: ExpectationNode,
        executor: 'ValidationExecutor'
    ) -> ValidationResult:
        """
        Validate records against expectation.

        Args:
            records: Records to validate
            expectation: AST node with operator and args
            executor: Executor for data access

        Returns:
            ValidationResult with pass/fail info
        """
        pass
```

## Step-by-Step Guide

### 1. Create Validator Class

```python
from dql_core import Validator

class MyValidator(Validator):
    def validate(self, records, expectation, executor):
        # Implementation
        pass
```

### 2. Extract Operator Arguments

```python
def validate(self, records, expectation, executor):
    # For column-level validation
    field_name = expectation.target.field_name

    # For operators with arguments (like to_match_pattern)
    operator = expectation.operator
    if hasattr(operator, 'pattern'):
        pattern = operator.pattern
    if hasattr(operator, 'min_value'):
        min_val = operator.min_value
        max_val = operator.max_value
```

### 3. Iterate Records and Validate

```python
def validate(self, records, expectation, executor):
    field_name = expectation.target.field_name
    failed_records = []

    for record in records:
        # Get field value using executor
        value = executor.get_field_value(record, field_name)

        # Your validation logic
        if not self.is_valid(value):
            failed_records.append({
                "record": record,
                "field": field_name,
                "value": value,
                "reason": "Validation failed"
            })

    return ValidationResult(
        passed=len(failed_records) == 0,
        total_records=executor.count_records(records),
        failed_records=len(failed_records),
        failures=failed_records
    )
```

### 4. Register Validator

```python
from dql_core import default_registry

default_registry.register("my_operator", MyValidator)
```

## Real-World Examples

### Example 1: Email Domain Validator

```python
class EmailDomainValidator(Validator):
    """Validates email belongs to allowed domains."""

    def validate(self, records, expectation, executor):
        field_name = expectation.target.field_name
        allowed_domains = expectation.operator.domains  # Custom operator attribute
        failed_records = []

        for record in records:
            email = executor.get_field_value(record, field_name)
            if email:
                domain = email.split('@')[-1] if '@' in email else None
                if domain not in allowed_domains:
                    failed_records.append({
                        "record": record,
                        "field": field_name,
                        "value": email,
                        "reason": f"Domain {domain} not in {allowed_domains}"
                    })

        return ValidationResult(
            passed=len(failed_records) == 0,
            total_records=executor.count_records(records),
            failed_records=len(failed_records),
            failures=failed_records
        )

default_registry.register("to_have_domain", EmailDomainValidator)
```

### Example 2: Date Range Validator

```python
from datetime import datetime, timedelta

class DateFreshnessValidator(Validator):
    """Validates date is within N days of today."""

    def validate(self, records, expectation, executor):
        field_name = expectation.target.field_name
        max_days_old = expectation.operator.max_days  # Custom attribute
        cutoff_date = datetime.now() - timedelta(days=max_days_old)
        failed_records = []

        for record in records:
            date_value = executor.get_field_value(record, field_name)
            if date_value and date_value < cutoff_date:
                failed_records.append({
                    "record": record,
                    "field": field_name,
                    "value": date_value,
                    "reason": f"Date older than {max_days_old} days"
                })

        return ValidationResult(
            passed=len(failed_records) == 0,
            total_records=executor.count_records(records),
            failed_records=len(failed_records),
            failures=failed_records
        )
```

### Example 3: External API Validator

```python
class ExternalAPIValidator(Validator):
    """Validates field by calling external API."""

    def __init__(self, api_adapter):
        self.api_adapter = api_adapter

    def validate(self, records, expectation, executor):
        field_name = expectation.target.field_name
        failed_records = []

        for record in records:
            value = executor.get_field_value(record, field_name)
            if value:
                # Call external API
                result = self.api_adapter.call(field=field_name, value=value)
                if not result.get("valid"):
                    failed_records.append({
                        "record": record,
                        "field": field_name,
                        "value": value,
                        "reason": result.get("error", "API validation failed")
                    })

        return ValidationResult(
            passed=len(failed_records) == 0,
            total_records=executor.count_records(records),
            failed_records=len(failed_records),
            failures=failed_records
        )
```

## Best Practices

### 1. Handle NULL Values

```python
def validate(self, records, expectation, executor):
    for record in records:
        value = executor.get_field_value(record, field_name)

        # Skip NULL values (let to_not_be_null handle it)
        if value is None:
            continue

        # Your validation logic
```

### 2. Provide Clear Failure Reasons

```python
failed_records.append({
    "record": record,
    "field": field_name,
    "value": value,
    "reason": f"Expected {expected}, got {value}",  # Clear reason
    "suggestion": "Check data source X"  # Optional
})
```

### 3. Use Type Hints

```python
from typing import Iterable, Any
from dql_parser.ast_nodes import ExpectationNode
from dql_core import Validator, ValidationResult

class MyValidator(Validator):
    def validate(
        self,
        records: Iterable[Any],
        expectation: ExpectationNode,
        executor: 'ValidationExecutor'
    ) -> ValidationResult:
        pass
```

### 4. Test Your Validator

```python
import pytest
from dql_core.executor import ValidationExecutor

class MockExecutor(ValidationExecutor):
    def __init__(self, records):
        self.records = records

    def get_records(self, model_name):
        return self.records

    def count_records(self, records):
        return len(list(records))

    def get_field_value(self, record, field_name):
        return record[field_name]

def test_my_validator():
    records = [
        {"price": 10},
        {"price": -5},  # Should fail
        {"price": 20}
    ]

    executor = MockExecutor(records)
    validator = MyValidator()

    # Create mock expectation
    result = validator.validate(records, expectation, executor)

    assert not result.passed
    assert result.failed_records == 1
```

## Next Steps

- **[Cleaner Guide](cleaner-guide.md)** - Write cleaner functions
- **[Executor Guide](executor-guide.md)** - Implement framework executors
- **[API Reference](api-reference.md)** - Full API documentation
