# Executor Guide

Implement ValidationExecutor for your framework.

## Overview

ValidationExecutor uses the **Template Method Pattern**: you implement 4 abstract methods, get full validation engine.

## Quick Start

```python
from dql_core import ValidationExecutor

class MyExecutor(ValidationExecutor):
    def get_records(self, model_name: str):
        # Return records for model
        return my_db.query(model_name).all()

    def filter_records(self, records, condition):
        # Filter records by condition
        return [r for r in records if self.evaluate_condition(r, condition)]

    def count_records(self, records):
        # Count records
        return len(list(records))

    def get_field_value(self, record, field_name: str):
        # Get field value
        return getattr(record, field_name)
```

## Abstract Methods

### 1. get_records(model_name)

Fetch all records for a model.

```python
def get_records(self, model_name: str) -> Iterable[Any]:
    """
    Args:
        model_name: Name of model/table

    Returns:
        Iterable of records (QuerySet, list, generator, etc.)
    """
    pass
```

### 2. filter_records(records, condition)

Filter records by row-level condition.

```python
def filter_records(self, records: Iterable, condition: Any) -> Iterable:
    """
    Args:
        records: Records to filter
        condition: AST condition node

    Returns:
        Filtered records
    """
    pass
```

### 3. count_records(records)

Count records in iterable.

```python
def count_records(self, records: Iterable) -> int:
    """
    Args:
        records: Records to count

    Returns:
        Number of records
    """
    pass
```

### 4. get_field_value(record, field_name)

Get field value from record.

```python
def get_field_value(self, record: Any, field_name: str) -> Any:
    """
    Args:
        record: Single record
        field_name: Field name

    Returns:
        Field value
    """
    pass
```

## Framework Examples

### SQLAlchemy

```python
from dql_core import ValidationExecutor
from sqlalchemy.orm import Session

class SQLAlchemyExecutor(ValidationExecutor):
    def __init__(self, session: Session, models: dict):
        self.session = session
        self.models = models  # {"Customer": CustomerModel, ...}

    def get_records(self, model_name: str):
        model_class = self.models[model_name]
        return self.session.query(model_class).all()

    def filter_records(self, records, condition):
        # Convert condition to SQLAlchemy filter
        return [r for r in records if self.evaluate_condition(r, condition)]

    def count_records(self, records):
        if hasattr(records, 'count'):
            return records.count()
        return len(list(records))

    def get_field_value(self, record, field_name: str):
        return getattr(record, field_name)
```

**Usage:**
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql://...")
Session = sessionmaker(bind=engine)
session = Session()

executor = SQLAlchemyExecutor(session, {"Customer": Customer})
result = executor.execute(ast)
```

### Pandas

```python
import pandas as pd
from dql_core import ValidationExecutor

class PandasExecutor(ValidationExecutor):
    def __init__(self, dataframes: dict):
        self.dataframes = dataframes  # {"Customer": df}

    def get_records(self, model_name: str):
        df = self.dataframes[model_name]
        return df.to_dict('records')

    def filter_records(self, records, condition):
        df = pd.DataFrame(records)
        # Apply condition to DataFrame
        mask = self._condition_to_mask(df, condition)
        return df[mask].to_dict('records')

    def count_records(self, records):
        return len(records)

    def get_field_value(self, record, field_name: str):
        return record[field_name]

    def _condition_to_mask(self, df, condition):
        # Convert AST condition to pandas mask
        pass
```

**Usage:**
```python
df_customer = pd.read_csv("customers.csv")
executor = PandasExecutor({"Customer": df_customer})
result = executor.execute(ast)
```

### Django (Full Example)

```python
from dql_core import ValidationExecutor
from django.apps import apps

class DjangoExecutor(ValidationExecutor):
    def get_records(self, model_name: str):
        model_class = apps.get_model(model_name)
        return model_class.objects.all()

    def filter_records(self, records, condition):
        # Convert condition to Django Q objects
        q_obj = self._condition_to_q(condition)
        return records.filter(q_obj)

    def count_records(self, records):
        return records.count()

    def get_field_value(self, record, field_name: str):
        return getattr(record, field_name)

    def _condition_to_q(self, condition):
        from django.db.models import Q
        # Convert AST condition to Q object
        pass
```

### Raw Dicts

```python
from dql_core import ValidationExecutor

class DictExecutor(ValidationExecutor):
    def __init__(self, data: dict):
        self.data = data  # {"Customer": [{...}, {...}]}

    def get_records(self, model_name: str):
        return self.data[model_name]

    def filter_records(self, records, condition):
        return [r for r in records if self._matches(r, condition)]

    def count_records(self, records):
        return len(list(records))

    def get_field_value(self, record, field_name: str):
        return record.get(field_name)

    def _matches(self, record, condition):
        # Evaluate condition against dict record
        pass
```

## Testing Your Executor

```python
import pytest
from dql_parser import DQLParser

def test_executor():
    # Mock data
    class MockRecord:
        def __init__(self, email, age):
            self.email = email
            self.age = age

    records = [
        MockRecord("test@example.com", 25),
        MockRecord(None, 30),  # Should fail to_not_be_null
        MockRecord("user@example.com", 17)  # Should fail age range
    ]

    # Custom executor
    class TestExecutor(ValidationExecutor):
        def get_records(self, model_name):
            return records

        def filter_records(self, records, condition):
            return records

        def count_records(self, records):
            return len(list(records))

        def get_field_value(self, record, field_name):
            return getattr(record, field_name)

    # Parse DQL
    parser = DQLParser()
    ast = parser.parse("""
    FROM Customer
    EXPECT column("email") to_not_be_null SEVERITY critical
    EXPECT column("age") to_be_between(18, 120)
    """)

    # Execute
    executor = TestExecutor()
    result = executor.execute(ast)

    assert not result.overall_passed
    assert result.total_expectations == 2
    assert result.failed_expectations == 2
```

## Performance Tips

### 1. Use Lazy Evaluation

```python
def get_records(self, model_name: str):
    # Return generator for large datasets
    return (record for record in self.db.query(model_name))
```

### 2. Optimize Count

```python
def count_records(self, records):
    # Use DB count if available
    if hasattr(records, 'count'):
        return records.count()
    return len(list(records))
```

### 3. Batch Processing

```python
def get_records(self, model_name: str):
    # Process in batches for large datasets
    return self.db.query(model_name).yield_per(1000)
```

## Next Steps

- **[Extending](extending.md)** - External API patterns
- **[API Reference](api-reference.md)** - Complete API
