# Cleaner Guide

Cleaners automatically remediate data quality issues when expectations fail.

## Quick Example

```python
from dql_core import register_cleaner, CleanerResult

@register_cleaner("trim")
def trim_whitespace(record, context):
    """Remove leading/trailing whitespace."""
    field_name = context["field_name"]
    old_value = getattr(record, field_name)

    if old_value and isinstance(old_value, str):
        new_value = old_value.strip()
        setattr(record, field_name, new_value)

        return CleanerResult(
            success=True,
            modified=old_value != new_value,
            before_value=old_value,
            after_value=new_value
        )

    return CleanerResult(success=True, modified=False)
```

Use in DQL:
```dql
FROM Customer
EXPECT column("email") to_not_be_null
  ON_FAILURE clean_with trim
```

## Cleaner Function Signature

```python
from dql_core import CleanerResult

def my_cleaner(record: Any, context: dict) -> CleanerResult:
    """
    Args:
        record: Record to clean (mutable)
        context: {
            "field_name": str,
            "expectation": ExpectationNode,
            "validation_result": ValidationResult
        }

    Returns:
        CleanerResult with success status
    """
    pass
```

## CleanerResult

```python
@dataclass
class CleanerResult:
    success: bool              # Did cleaner execute successfully?
    modified: bool = False     # Was record modified?
    before_value: Any = None   # Value before cleaning
    after_value: Any = None    # Value after cleaning
    error: str = None          # Error message if failed
```

## Registration

### Using @cleaner Decorator (Story 2.6 - Recommended)

```python
from dql_core import cleaner, CleanerResult

@cleaner
def normalize_ssn(record, context):
    """Normalize SSN to XXX-XX-XXXX format."""
    # Cleaner implementation...
    return CleanerResult(success=True, modified=True)

# Auto-registers as 'normalize_ssn' (from function name)
```

With custom name:

```python
@cleaner(name='custom_name')
def some_function(record, context):
    """Custom cleaner with explicit name."""
    return CleanerResult(success=True, modified=False)

# Registers as 'custom_name'
```

Skip signature validation:

```python
@cleaner(validate=False)
def legacy_cleaner(record, context):
    """Skip validation for legacy code."""
    return CleanerResult(success=True, modified=False)
```

### Using @register_cleaner (Legacy)

```python
from dql_core import register_cleaner

@register_cleaner("lowercase")
def lowercase(record, context):
    field_name = context["field_name"]
    old_value = getattr(record, field_name)

    if old_value and isinstance(old_value, str):
        new_value = old_value.lower()
        setattr(record, field_name, new_value)
        return CleanerResult(
            success=True,
            modified=old_value != new_value,
            before_value=old_value,
            after_value=new_value
        )

    return CleanerResult(success=True, modified=False)
```

### Auto-Discovery (Story 2.6)

Automatically discover and register cleaners from a directory:

```python
from dql_core import discover_cleaners

# Discover all @cleaner decorated functions
discovered = discover_cleaners('my_app/custom_cleaners/')
print(f"Discovered {len(discovered)} cleaners: {discovered}")
```

Project structure:

```
my_app/
  custom_cleaners/
    domain_cleaners.py      # @cleaner decorated functions
    business_rules.py       # @cleaner decorated functions
  models.py
```

Example custom cleaner:

```python
# my_app/custom_cleaners/domain_cleaners.py
from dql_core import cleaner, CleanerResult

@cleaner
def normalize_ssn(record, context):
    """Normalize SSN to XXX-XX-XXXX format."""
    # Implementation...
    return CleanerResult(success=True, modified=True)

@cleaner(name='validate_credit_card')
def check_credit_card(record, context):
    """Validate credit card using Luhn algorithm."""
    # Implementation...
    return CleanerResult(success=True, modified=False)
```

Then in your app initialization:

```python
from dql_core import register_cleaners_from_directory

# Auto-discover and register all custom cleaners
register_cleaners_from_directory('my_app/custom_cleaners/')
```

### Manual Registration

```python
from dql_core import CleanerRegistry

registry = CleanerRegistry()
registry.register("my_cleaner", my_cleaner_func)
```

## CleanerExecutor

For transaction safety, implement `CleanerExecutor`:

```python
from dql_core import CleanerExecutor

class MyCleanerExecutor(CleanerExecutor):
    def begin_transaction(self):
        self.db.begin()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def save_record(self, record):
        self.db.save(record)
```

## Built-in Cleaners

dql-core includes 8 built-in cleaners for common data quality issues:

### String Cleaners (Story 2.4)

| Cleaner | Description | Example |
|---------|-------------|---------|
| `trim_whitespace` | Remove leading/trailing whitespace | `"  hello  "` → `"hello"` |
| `uppercase` | Convert to uppercase | `"hello"` → `"HELLO"` |
| `lowercase` | Convert to lowercase | `"HELLO"` → `"hello"` |
| `normalize_email` | Trim and lowercase emails | `"  [email protected]  "` → `"[email protected]"` |

### Data Type Cleaners (Story 2.5)

| Cleaner | Description | Example |
|---------|-------------|---------|
| `strip_non_numeric` | Remove non-numeric characters | `"(555) 555-5555"` → `"5555555555"` |
| `normalize_phone` | Format phone numbers | `"555-555-5555"` → `"+15555555555"` (E164) |
| `coalesce` | Replace NULL with default | `None` → `"pending"` |
| `format_date` | Convert date formats | `"2025-01-15"` → `"01/15/2025"` |

### Using Built-in Cleaners

```python
from dql_core import trim_whitespace, normalize_phone, coalesce

# String cleaner: factory function takes field name
cleaner = trim_whitespace('email')
result = cleaner(record, context)

# Phone cleaner: supports format options (E164, US, digits_only)
cleaner = normalize_phone('phone', format='E164')
result = cleaner(record, context)

# Coalesce: replaces NULL with default
cleaner = coalesce('status', default_value='pending')
result = cleaner(record, context)
```

## Examples

### Address Normalization

```python
@register_cleaner("normalize_address")
def normalize_address(record, context):
    field_name = context["field_name"]
    address = getattr(record, field_name)

    if address:
        # Normalize: uppercase, remove extra spaces
        normalized = " ".join(address.upper().split())
        setattr(record, field_name, normalized)

        return CleanerResult(
            success=True,
            modified=address != normalized,
            before_value=address,
            after_value=normalized
        )

    return CleanerResult(success=True, modified=False)
```

### Phone Number Normalization (Story 2.5)

Using the built-in `normalize_phone` cleaner:

```python
from dql_core import normalize_phone

# Normalize to E164 format (international)
cleaner = normalize_phone('phone', format='E164')
record = {'phone': '(555) 555-5555'}
result = cleaner(record, {})
# record['phone'] is now '+15555555555'

# Normalize to US format
cleaner = normalize_phone('phone', format='US')
record = {'phone': '5555555555'}
result = cleaner(record, {})
# record['phone'] is now '(555) 555-5555'

# Strip to digits only
cleaner = normalize_phone('phone', format='digits_only')
record = {'phone': '+1-555-555-5555'}
result = cleaner(record, {})
# record['phone'] is now '5555555555'
```

### Strip Non-Numeric Characters (Story 2.5)

```python
from dql_core import strip_non_numeric

# Clean phone number formatting
cleaner = strip_non_numeric('phone')
record = {'phone': '(555) 555-5555'}
result = cleaner(record, {})
# record['phone'] is now '5555555555'

# Clean currency values
cleaner = strip_non_numeric('amount')
record = {'amount': '$1,234.56'}
result = cleaner(record, {})
# record['amount'] is now '123456'
```

### NULL Value Handling with Coalesce (Story 2.5)

```python
from dql_core import coalesce

# Replace NULL status with default
cleaner = coalesce('status', default_value='pending')
record = {'status': None}
result = cleaner(record, {})
# record['status'] is now 'pending'

# Replace NULL amount with 0
cleaner = coalesce('amount', default_value=0)
record = {'amount': None}
result = cleaner(record, {})
# record['amount'] is now 0

# Non-NULL values are unchanged
record = {'status': 'active'}
result = cleaner(record, {})
# record['status'] remains 'active'
```

### Date Format Conversion (Story 2.5)

```python
from dql_core import format_date

# Convert ISO to US format
cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
record = {'created_at': '2025-01-15'}
result = cleaner(record, {})
# record['created_at'] is now '01/15/2025'

# Convert US to ISO format
cleaner = format_date('created_at', input_format='%m/%d/%Y', output_format='%Y-%m-%d')
record = {'created_at': '01/15/2025'}
result = cleaner(record, {})
# record['created_at'] is now '2025-01-15'

# Format with month names
cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%B %d, %Y')
record = {'created_at': '2025-01-15'}
result = cleaner(record, {})
# record['created_at'] is now 'January 15, 2025'

# Works with date/datetime objects too
from datetime import date
record = {'created_at': date(2025, 1, 15)}
result = cleaner(record, {})
# Automatically converts date object to string
```

## Chaining Cleaners (Story 2.6)

Execute multiple cleaners in sequence with `CleanerChain`:

```python
from dql_core import CleanerChain

# Create chain with chainable syntax
chain = (CleanerChain()
    .add('trim_whitespace', 'email')
    .add('lowercase', 'email')
    .add('normalize_email', 'email'))

record = {'email': '  [email protected]  '}
result = chain.execute(record, {})
# record['email'] is now '[email protected]'
```

### Factory Method

```python
# Create chain from list of cleaner names
chain = CleanerChain.from_names(
    ['trim_whitespace', 'lowercase', 'normalize_email'],
    field_name='email'
)

result = chain.execute(record, {})
```

### Chaining Behavior

- Cleaners execute **sequentially** in order added
- Execution **short-circuits** on first error
- **Context metadata** passed between cleaners:
  - `cleaner_chain`: {total_steps, current_step, cleaner_names}
  - `previous_result`: Previous cleaner's CleanerResult
- **Context isolation**: Input context is deep-copied

### Phone Number Workflow Example

```python
# Chain: strip formatting → normalize to E164
chain = (CleanerChain()
    .add('strip_non_numeric', 'phone')
    .add('normalize_phone', 'phone', format='E164'))

record = {'phone': '(555) 555-5555'}
result = chain.execute(record, {})
# record['phone'] is now '+15555555555'

assert result.success is True
assert result.modified is True
```

### DQL Syntax (Future)

```dql
EXPECT column("email") to_match_pattern("[a-z]+@[a-z]+")
  ON_FAILURE clean_with trim_whitespace, lowercase, normalize_email
```

## Error Handling

```python
@register_cleaner("safe_cleaner")
def safe_cleaner(record, context):
    try:
        # Cleaning logic
        return CleanerResult(success=True, modified=True)
    except Exception as e:
        return CleanerResult(
            success=False,
            modified=False,
            error=str(e)
        )
```

## Testing

```python
def test_trim_cleaner():
    class MockRecord:
        def __init__(self):
            self.email = "  test@example.com  "

    record = MockRecord()
    context = {"field_name": "email"}

    result = trim_whitespace(record, context)

    assert result.success
    assert result.modified
    assert record.email == "test@example.com"
    assert result.before_value == "  test@example.com  "
    assert result.after_value == "test@example.com"
```

## Next Steps

- **[Executor Guide](executor-guide.md)** - Implement framework executors
- **[Extending](extending.md)** - External API patterns

## Transaction Safety (Story 2.7)

Execute cleaners with automatic rollback on failure using `SafeCleanerExecutor`:

```python
from dql_core import SafeCleanerExecutor, DictTransactionManager

# Create transaction manager and executor
manager = DictTransactionManager()
executor = SafeCleanerExecutor(manager)

# Execute cleaners with transaction safety
cleaners = [trim_whitespace('email'), lowercase('email')]
record = {'email': '  [email protected]  '}

result = executor.execute_cleaners(cleaners, record, {})
# If any cleaner fails, transaction rolls back
```

### Dry-Run Mode

Preview changes without committing:

```python
# Preview what cleaners would do
result = executor.preview_changes(cleaners, record, {})

print(f"Would modify: {result.modified}")
print(f"Before: {result.before_value}")
print(f"After: {result.after_value}")

# Original record unchanged
assert record['email'] == '  [email protected]  '
```

### Audit Logging

Track all cleaner modifications:

```python
from dql_core import AuditLogger

# Create audit logger
audit_logger = AuditLogger(backend='memory')
executor = SafeCleanerExecutor(manager, audit_logger)

# Execute cleaners
result = executor.execute_cleaners(cleaners, record, {})

# Retrieve audit logs
logs = audit_logger.get_logs()
for log in logs:
    print(f"Transaction: {log.transaction_id}")
    print(f"Cleaners: {log.cleaner_names}")
    print(f"Changed: {log.before_value} → {log.after_value}")
```

### Transaction Managers

**DictTransactionManager** - For dict records (testing):
- Provides transaction semantics
- Best-effort rollback for dict records
- Ideal for testing without database

**Future**: Django and SQLAlchemy transaction managers for database-backed records with full rollback support.

