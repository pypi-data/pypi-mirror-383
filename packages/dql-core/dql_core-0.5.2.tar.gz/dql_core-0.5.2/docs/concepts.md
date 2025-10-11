# Core Concepts

Understanding the architecture of dql-core.

## Architecture Overview

dql-core uses the **Template Method Pattern** combined with **Abstract Base Classes** to provide a framework-agnostic validation engine.

```
┌─────────────────────────────────────────┐
│         DQL Text (*.dql)                │
└───────────────┬─────────────────────────┘
                │
                │ dql-parser
                ↓
┌─────────────────────────────────────────┐
│         AST (DQLFile)                   │
└───────────────┬─────────────────────────┘
                │
                │ dql-core
                ↓
┌─────────────────────────────────────────┐
│    ValidationExecutor.execute(ast)      │
│  (uses your 4 implemented methods)     │
└───────────────┬─────────────────────────┘
                │
                ↓
┌─────────────────────────────────────────┐
│    ValidationRunResult                  │
└─────────────────────────────────────────┘
```

## ValidationExecutor

The **ValidationExecutor** is the heart of dql-core. It implements the validation orchestration logic but delegates data access to your implementation.

### Template Method Pattern

The `execute(ast)` method is **concrete** - you don't override it. It calls your **abstract** methods:

```python
class ValidationExecutor(ABC):
    def execute(self, ast: DQLFile) -> ValidationRunResult:
        # Concrete implementation - orchestrates validation
        for from_block in ast.from_blocks:
            records = self.get_records(from_block.model_name)  # Abstract - you implement
            for expectation in from_block.expectations:
                # Validation logic here...
                field_value = self.get_field_value(record, field_name)  # Abstract

    @abstractmethod
    def get_records(self, model_name: str) -> Iterable[Any]:
        pass  # You implement

    @abstractmethod
    def filter_records(self, records: Iterable, condition) -> Iterable:
        pass  # You implement

    @abstractmethod
    def count_records(self, records: Iterable) -> int:
        pass  # You implement

    @abstractmethod
    def get_field_value(self, record: Any, field_name: str) -> Any:
        pass  # You implement
```

### Why This Design?

1. **Separation of Concerns**: dql-core handles validation logic, you handle data access
2. **Framework Agnostic**: Works with Django, SQLAlchemy, Pandas, raw dicts, etc.
3. **Testability**: Easy to mock abstract methods for testing
4. **Maintainability**: Core validation logic updates benefit all implementations

## Validators

Validators implement the logic for each DQL operator.

### Validator Interface

```python
class Validator(ABC):
    @abstractmethod
    def validate(
        self,
        records: Iterable[Any],
        expectation: ExpectationNode,
        executor: ValidationExecutor
    ) -> ExpectationResult:
        pass
```

### Built-in Validators

| Operator | Validator Class | What It Checks |
|----------|-----------------|----------------|
| `to_be_null` | `ToBeNullValidator` | Value is NULL |
| `to_not_be_null` | `ToNotBeNullValidator` | Value is NOT NULL |
| `to_match_pattern` | `ToMatchPatternValidator` | Matches regex |
| `to_be_between` | `ToBeBetweenValidator` | In numeric range |
| `to_be_in` | `ToBeInValidator` | In list of values |
| `to_be_unique` | `ToBeUniqueValidator` | No duplicates |

### ValidatorRegistry

Maps operator names to validator classes:

```python
from dql_core import default_registry, Validator

# Built-in registry
validator = default_registry.get("to_not_be_null")  # ToNotBeNullValidator

# Register custom validator
class MyCustomValidator(Validator):
    def validate(self, records, expectation, executor):
        # Custom logic
        pass

default_registry.register("my_operator", MyCustomValidator)
```

## CleanerExecutor

Handles data remediation with transaction safety.

### Transaction Template

```python
class CleanerExecutor(ABC):
    def execute_cleaner(self, cleaner_func, record, context) -> CleanerResult:
        try:
            self.begin_transaction()  # Abstract - you implement
            result = cleaner_func(record, context)
            if result.modified:
                self.save_record(record)  # Abstract - you implement
            self.commit()  # Abstract - you implement
            return result
        except Exception as e:
            self.rollback()  # Abstract - you implement
            return CleanerResult(success=False, error=str(e))

    @abstractmethod
    def begin_transaction(self) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def save_record(self, record: Any) -> None:
        pass
```

### CleanerRegistry

Register cleaner functions:

```python
from dql_core import CleanerRegistry, register_cleaner

registry = CleanerRegistry()

# Using decorator
@register_cleaner("trim", registry=registry)
def trim_whitespace(record, context):
    # Cleaner logic
    return CleanerResult(success=True, modified=True)

# Manual registration
registry.register("lowercase", lowercase_func)
```

## Result Objects

### ValidationRunResult

Top-level result from `executor.execute(ast)`:

```python
@dataclass
class ValidationRunResult:
    overall_passed: bool
    expectation_results: List[ExpectationResult]
    duration: float
    counts: dict  # total, passed, failed expectations
```

### ExpectationResult

Result for each EXPECT statement:

```python
@dataclass
class ExpectationResult:
    expectation: ExpectationNode
    passed: bool
    validation_result: ValidationResult
    severity: str
    model_name: str
```

### ValidationResult

Result of validation on records:

```python
@dataclass
class ValidationResult:
    passed: bool
    total_records: int
    failed_records: int
    failures: List[dict]  # Failed record details
```

### CleanerResult

Result of cleaner execution:

```python
@dataclass
class CleanerResult:
    success: bool
    modified: bool
    before_value: Any
    after_value: Any
    error: Optional[str]
```

## External API Adapters

Framework for calling external APIs during validation.

### APIAdapter

Abstract base class:

```python
class APIAdapter(ABC):
    @abstractmethod
    def call(self, **kwargs) -> dict:
        pass
```

### APIAdapterFactory

Register and create adapters:

```python
from dql_core import APIAdapterFactory, APIAdapter

factory = APIAdapterFactory()

class MyAPIAdapter(APIAdapter):
    def call(self, **kwargs):
        return requests.post("https://api.example.com", json=kwargs).json()

factory.register("my_api", MyAPIAdapter)
adapter = factory.create("my_api")
result = adapter.call(field="email", value="test@example.com")
```

### Rate Limiting

```python
from dql_core import RateLimiter

limiter = RateLimiter(calls_per_second=10)

for record in records:
    limiter.acquire()  # Blocks if rate limit exceeded
    result = api_adapter.call(data=record)
```

### Retry Logic

```python
from dql_core import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=1.0)
def call_external_api(data):
    return requests.post("https://api.example.com", json=data)
```

## Exception Hierarchy

```
DQLCoreError (base)
├── ValidatorNotFoundError
├── CleanerNotFoundError
├── AdapterNotFoundError
└── ValidationExecutionError
```

## Next Steps

- **[Validator Guide](validator-guide.md)** - Create custom validators
- **[Cleaner Guide](cleaner-guide.md)** - Write cleaner functions
- **[Executor Guide](executor-guide.md)** - Implement framework executors
- **[Extending](extending.md)** - External API patterns
