# dql-core Documentation

Welcome to **dql-core**, the framework-agnostic validation engine for Data Quality Language (DQL).

## What is dql-core?

**dql-core** provides abstract base classes and validation logic for implementing DQL validation in any Python framework. Whether you're using Django, Flask, FastAPI, SQLAlchemy, or Pandas, dql-core gives you the foundation to execute DQL validations.

### Key Features

- 🎯 **Framework-Agnostic** - Works with any Python framework or ORM
- 🏗️ **Abstract Base Classes** - Implement 4 methods, get full validation engine
- ✅ **6 Built-in Validators** - Ready-to-use operators
- 🔄 **Cleaner Framework** - Auto-remediation with transaction safety
- 🔌 **External API Adapters** - Rate limiting, retry logic, adapter factory
- 📊 **Rich Results** - Detailed validation results with failure information

## Installation

```bash
pip install dql-core
```

## Quick Start

Here's how to create a custom validator in 30 lines:

```python
from dql_core import ValidationExecutor
from dql_parser import DQLParser

class MyExecutor(ValidationExecutor):
    """Implement for your framework."""

    def get_records(self, model_name: str):
        # Return records from your data source
        return my_database.query(model_name).all()

    def filter_records(self, records, condition):
        return [r for r in records if self.evaluate_condition(r, condition)]

    def count_records(self, records):
        return len(list(records))

    def get_field_value(self, record, field_name: str):
        return getattr(record, field_name)

# Use it
parser = DQLParser()
ast = parser.parse("""
FROM Customer
EXPECT column("email") to_not_be_null SEVERITY critical
EXPECT column("age") to_be_between(18, 120)
""")

executor = MyExecutor()
result = executor.execute(ast)

print(f"Passed: {result.overall_passed}")
print(f"Total: {result.total_expectations}")
print(f"Failed: {result.failed_expectations}")
```

## When to Use dql-core

Use **dql-core** when you:

- Are building a DQL integration for Flask, FastAPI, or another framework
- Want to use DQL with SQLAlchemy, Peewee, or Pandas
- Need the validation engine without Django-specific features
- Are creating a custom data quality tool

### What dql-core Provides

- ✅ Abstract `ValidationExecutor` base class
- ✅ 6 built-in validators with registry pattern
- ✅ Abstract `CleanerExecutor` with transaction management
- ✅ External API adapter framework
- ✅ Result dataclasses for validation output

### What dql-core Does NOT Provide

- ❌ DQL parsing - Use [dql-parser](https://yourusername.github.io/dql-parser/)
- ❌ Django integration - Use [django-dqm](https://yourusername.github.io/django-dqm/)
- ❌ Concrete implementations - You implement for your framework

## Core Concepts

### ValidationExecutor

Abstract base class that orchestrates validation. You implement 4 methods:

1. `get_records(model_name)` - Fetch records to validate
2. `filter_records(records, condition)` - Filter records by condition
3. `count_records(records)` - Count records
4. `get_field_value(record, field_name)` - Get field value from record

The `execute(ast)` method is provided - it uses your implementations.

### Validators

Each DQL operator has a corresponding validator class:

- `ToBeNullValidator` - Checks NULL values
- `ToNotBeNullValidator` - Checks NOT NULL
- `ToMatchPatternValidator` - Regex pattern matching
- `ToBeBetweenValidator` - Range validation
- `ToBeInValidator` - Enum validation
- `ToBeUniqueValidator` - Uniqueness check

All validators extend the `Validator` base class.

### CleanerExecutor

Abstract base class for data remediation with transaction safety:

1. `begin_transaction()` - Start transaction
2. `commit()` - Commit changes
3. `rollback()` - Rollback on error
4. `save_record(record)` - Save modified record

### Result Objects

Validation returns structured results:

- `ValidationRunResult` - Overall validation result
- `ExpectationResult` - Result for each expectation
- `ValidationResult` - Result for column/row validation
- `CleanerResult` - Result of cleaner execution

## Package Ecosystem

```
dql-parser (parse DQL syntax)
    ↓ used by
dql-core (you are here - validation engine)
    ↓ used by
django-dqm (Django integration)
```

- **[dql-parser](https://yourusername.github.io/dql-parser/)** - Parse DQL syntax
- **dql-core** - Framework-agnostic validation engine (you are here)
- **[django-dqm](https://yourusername.github.io/django-dqm/)** - Django integration

## Next Steps

- **[Concepts](concepts.md)** - Core concepts explained
- **[Validator Guide](validator-guide.md)** - Create custom validators
- **[Cleaner Guide](cleaner-guide.md)** - Write cleaner functions
- **[Executor Guide](executor-guide.md)** - Implement framework executors
- **[Extending](extending.md)** - External API adapters
- **[API Reference](api-reference.md)** - Complete API documentation

## Examples

### SQLAlchemy Executor

```python
from dql_core import ValidationExecutor
from sqlalchemy.orm import Session

class SQLAlchemyExecutor(ValidationExecutor):
    def __init__(self, session: Session, models: dict):
        self.session = session
        self.models = models

    def get_records(self, model_name: str):
        model_class = self.models[model_name]
        return self.session.query(model_class).all()

    def filter_records(self, records, condition):
        # SQLAlchemy filtering logic
        return [r for r in records if self.evaluate_condition(r, condition)]

    def count_records(self, records):
        return len(records)

    def get_field_value(self, record, field_name: str):
        return getattr(record, field_name)
```

### Pandas Executor

```python
import pandas as pd
from dql_core import ValidationExecutor

class PandasExecutor(ValidationExecutor):
    def __init__(self, dataframes: dict):
        self.dataframes = dataframes

    def get_records(self, model_name: str):
        return self.dataframes[model_name].to_dict('records')

    def filter_records(self, records, condition):
        # Pandas filtering logic
        df = pd.DataFrame(records)
        # Apply condition to df
        return filtered_df.to_dict('records')

    def count_records(self, records):
        return len(records)

    def get_field_value(self, record, field_name: str):
        return record[field_name]
```

## Contributing

Contributions welcome! See [CONTRIBUTING.md](https://github.com/dql-project/dql-core/blob/main/CONTRIBUTING.md)

## License

MIT License - see [LICENSE](https://github.com/dql-project/dql-core/blob/main/LICENSE)
