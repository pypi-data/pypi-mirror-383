# Cleaner Best Practices

Guidelines for writing performant, secure, and maintainable cleaners.

## Table of Contents

- [Performance](#performance)
- [Security](#security)
- [Testing](#testing)
- [Error Handling](#error-handling)
- [NULL Handling](#null-handling)
- [Idempotency](#idempotency)
- [Naming Conventions](#naming-conventions)
- [When NOT to Use Cleaners](#when-not-to-use-cleaners)
- [Monitoring & Alerting](#monitoring--alerting)

---

## Performance

### 1. Minimize Database Queries

**❌ Bad:** Query database in each cleaner (N+1 problem)

```python
@cleaner
def enrich_customer(field_name):
    def cleaner_func(record, context):
        # BAD: N+1 query problem
        related_data = Customer.objects.get(id=record.id).orders.count()
        record.order_count = related_data
        return CleanerResult(success=True, modified=True)
    return cleaner_func
```

**✅ Good:** Prefetch data before cleaning

```python
# Prefetch data once
customers = Customer.objects.prefetch_related('orders').all()

# Clean without additional queries
for customer in customers:
    cleaners = [trim_whitespace('email'), normalize_email('email')]
    executor.execute_cleaners(cleaners, customer, {})
```

### 2. Batch Cleaners by Field

**❌ Bad:** Execute cleaners one record at a time

```python
for record in records:
    cleaner(record, {})
```

**✅ Good:** Batch cleaners in single transaction

```python
with manager.transaction():
    for record in records:
        cleaner(record, {})
```

### 3. Use Dry-Run for Large Datasets

**✅ Good:** Preview changes before applying

```python
# Preview first
result = executor.preview_changes(cleaners, records[0], {})
print(f"Would modify {result.modified} fields")

# User confirms
if confirm("Apply changes to 10,000 records?"):
    for record in records:
        executor.execute_cleaners(cleaners, record, {})
```

### 4. Profile Slow Cleaners

```python
import time

def profile_cleaner(cleaner, record):
    start = time.time()
    result = cleaner(record, {})
    duration = time.time() - start

    if duration > 0.01:  # Slower than 10ms
        print(f"⚠️ Slow cleaner: {cleaner.__name__} took {duration*1000:.2f}ms")

    return result
```

### 5. Avoid External API Calls in Hot Paths

**❌ Bad:** Call external API for every record

```python
@cleaner
def validate_address(field_name):
    def cleaner_func(record, context):
        # BAD: Synchronous API call for every record
        response = requests.post('https://api.usps.com/validate', ...)
        # Process response
        return CleanerResult(...)
    return cleaner_func
```

**✅ Good:** Batch API calls or use async

```python
# Option 1: Batch API calls
addresses = [record['address'] for record in records]
validated = batch_validate_addresses(addresses)  # Single API call

for record, validated_address in zip(records, validated):
    record['address'] = validated_address

# Option 2: Async validation
async def validate_addresses_async(records):
    tasks = [validate_address_api(r) for r in records]
    return await asyncio.gather(*tasks)
```

### Performance Benchmarks

| Operation | Target Time | Excellent | Acceptable | Slow |
|-----------|------------|-----------|------------|------|
| String cleaner | <0.01ms | ✅ | - | - |
| Data type cleaner | <0.05ms | ✅ | 0.05-0.1ms | >0.1ms |
| API call cleaner | <100ms | <50ms | 50-100ms | >100ms ⚠️ |
| Batch (1000 records) | <1s | <0.5s | 0.5-1s | >1s ⚠️ |

---

## Security

### 1. Validate Input

**❌ Bad:** Trust input data without validation

```python
@cleaner
def execute_command(field_name):
    def cleaner_func(record, context):
        # DANGEROUS: Command injection vulnerability!
        command = record[field_name]
        os.system(command)
        return CleanerResult(success=True, modified=False)
    return cleaner_func
```

**✅ Good:** Validate and sanitize input

```python
@cleaner
def normalize_filename(field_name):
    def cleaner_func(record, context):
        value = record.get(field_name)

        if not value:
            return CleanerResult(success=True, modified=False)

        # Sanitize: remove path traversal attempts
        safe_filename = os.path.basename(value)
        safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_filename)

        record[field_name] = safe_filename
        return CleanerResult(
            success=True,
            modified=(value != safe_filename),
            before_value=value,
            after_value=safe_filename
        )
    return cleaner_func
```

### 2. Prevent SQL Injection

**❌ Bad:** Construct SQL queries with user input

```python
@cleaner
def lookup_customer(field_name):
    def cleaner_func(record, context):
        # DANGEROUS: SQL injection vulnerability!
        query = f"SELECT * FROM customers WHERE email = '{record['email']}'"
        cursor.execute(query)
        return CleanerResult(success=True, modified=False)
    return cleaner_func
```

**✅ Good:** Use parameterized queries or ORM

```python
@cleaner
def lookup_customer(field_name):
    def cleaner_func(record, context):
        email = record.get('email')

        # Safe: use ORM
        customer = Customer.objects.filter(email=email).first()

        # Or safe: parameterized query
        cursor.execute("SELECT * FROM customers WHERE email = %s", [email])

        return CleanerResult(success=True, modified=False)
    return cleaner_func
```

### 3. Don't Log Sensitive Data

**❌ Bad:** Log PII in cleaner results

```python
print(f"Cleaned SSN: {result.before_value} → {result.after_value}")
logger.info(f"Credit card: {record['card_number']}")
```

**✅ Good:** Mask sensitive data in logs

```python
def mask_ssn(ssn):
    if len(ssn) >= 4:
        return '***-**-' + ssn[-4:]
    return '***'

print(f"Cleaned SSN: {mask_ssn(result.before_value)} → {mask_ssn(result.after_value)}")
logger.info(f"Credit card: ************{record['card_number'][-4:]}")
```

### 4. Protect Against ReDoS (Regular Expression Denial of Service)

**❌ Bad:** Complex regex that can hang on malicious input

```python
# DANGEROUS: Catastrophic backtracking
pattern = r'^(a+)+$'
re.match(pattern, 'a' * 50 + 'b')  # Can take minutes!
```

**✅ Good:** Use simple regex or timeout

```python
import re
import signal

def regex_with_timeout(pattern, text, timeout=1):
    def handler(signum, frame):
        raise TimeoutError("Regex timeout")

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(timeout)

    try:
        result = re.match(pattern, text)
        signal.alarm(0)
        return result
    except TimeoutError:
        return None
```

---

## Testing

### 1. Test Happy Path

```python
def test_normalize_email_success():
    """Test email normalization with valid input"""
    record = {'email': '  [email protected]  '}
    cleaner = normalize_email('email')
    result = cleaner(record, {})

    assert result.success is True
    assert result.modified is True
    assert record['email'] == '[email protected]'
```

### 2. Test Edge Cases

```python
def test_normalize_email_edge_cases():
    """Test edge cases"""
    test_cases = [
        ('', ''),                    # Empty string
        ('   ', ''),                 # Whitespace only
        ('[email protected]', '[email protected]'),  # Already normalized
        (None, None),                # NULL value
        ('NO@CAPS.COM', 'no@caps.com'),  # Uppercase
    ]

    for input_val, expected in test_cases:
        record = {'email': input_val}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert record['email'] == expected
```

### 3. Test Error Cases

```python
def test_normalize_ssn_invalid():
    """Test SSN normalization with invalid input"""
    record = {'ssn': '123'}  # Too short
    cleaner = normalize_ssn_cleaner('ssn')
    result = cleaner(record, {})

    assert result.success is False
    assert result.modified is False
    assert 'must be 9 digits' in result.error
```

### 4. Test Idempotency

```python
def test_normalize_email_idempotent():
    """Test that running cleaner multiple times produces same result"""
    record = {'email': '  [email protected]  '}
    cleaner = normalize_email('email')

    # First run
    result1 = cleaner(record, {})
    assert result1.modified is True
    value_after_first = record['email']

    # Second run
    result2 = cleaner(record, {})
    assert result2.modified is False  # No change needed
    assert record['email'] == value_after_first
```

### 5. Test Transaction Rollback

```python
def test_cleaner_rollback_on_failure():
    """Test that transaction rolls back on cleaner failure"""
    manager = DictTransactionManager()
    executor = SafeCleanerExecutor(manager)

    record = {'email': '  [email protected]  ', 'ssn': 'invalid'}

    def failing_cleaner(field_name):
        def cleaner_func(record, context):
            return CleanerResult(success=False, error="Validation failed")
        return cleaner_func

    cleaners = [
        normalize_email('email'),
        failing_cleaner('ssn')  # This will fail
    ]

    result = executor.execute_cleaners(cleaners, record, {})

    assert result.success is False
    # Email should be rolled back
    assert record['email'] == '  [email protected]  '  # Original value
```

---

## Error Handling

### 1. Always Return CleanerResult

**❌ Bad:** Raise exceptions

```python
@cleaner
def bad_cleaner(field_name):
    def cleaner_func(record, context):
        if record[field_name] is None:
            raise ValueError("Field cannot be None")  # BAD!
        return CleanerResult(success=True, modified=False)
    return cleaner_func
```

**✅ Good:** Return error result

```python
@cleaner
def good_cleaner(field_name):
    def cleaner_func(record, context):
        if record[field_name] is None:
            return CleanerResult(
                success=False,
                modified=False,
                error="Field cannot be None"
            )
        return CleanerResult(success=True, modified=False)
    return cleaner_func
```

### 2. Catch and Handle Exceptions

```python
@cleaner
def safe_cleaner(field_name):
    def cleaner_func(record, context):
        try:
            # Cleaning logic that might fail
            value = complex_transformation(record[field_name])
            record[field_name] = value
            return CleanerResult(success=True, modified=True)

        except KeyError as e:
            return CleanerResult(
                success=False,
                modified=False,
                error=f"Field not found: {e}"
            )
        except ValueError as e:
            return CleanerResult(
                success=False,
                modified=False,
                error=f"Invalid value: {e}"
            )
        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                error=f"Unexpected error: {str(e)}"
            )
    return cleaner_func
```

### 3. Provide Helpful Error Messages

**❌ Bad:** Vague error messages

```python
return CleanerResult(success=False, error="Invalid")
```

**✅ Good:** Specific, actionable error messages

```python
return CleanerResult(
    success=False,
    error=f"SSN must be 9 digits, got {len(digits)}. Example: 123-45-6789"
)
```

---

## NULL Handling

### 1. Always Handle NULL Values

**✅ Best practice pattern:**

```python
@cleaner
def my_cleaner(field_name):
    def cleaner_func(record, context):
        value = getattr(record, field_name) if hasattr(record, field_name) else record.get(field_name)

        # Handle NULL first
        if value is None:
            return CleanerResult(success=True, modified=False)

        # Continue with cleaning logic
        # ...
        return CleanerResult(success=True, modified=True)

    return cleaner_func
```

### 2. Distinguish NULL from Empty

```python
# NULL vs Empty string
None != ""        # NULL is different from empty
None != 0         # NULL is different from zero
None != False     # NULL is different from false

# Check for NULL explicitly
if value is None:
    # Handle NULL
elif value == "":
    # Handle empty string
else:
    # Handle normal value
```

### 3. Use coalesce for Default Values

```python
from dql_core import coalesce

# Replace NULL with default
cleaner = coalesce('status', default_value='pending')
```

---

## Idempotency

**Idempotent** = Safe to run multiple times with same result

### Why Idempotency Matters

- Cleaners may be re-run if validation fails again
- Retries in error scenarios
- Debugging and testing

### Making Cleaners Idempotent

**✅ Good idempotent cleaner:**

```python
@cleaner
def normalize_email(field_name):
    def cleaner_func(record, context):
        value = record.get(field_name)

        if not value:
            return CleanerResult(success=True, modified=False)

        # Normalize
        normalized = value.strip().lower()

        # Check if change needed (idempotent check)
        if value == normalized:
            return CleanerResult(success=True, modified=False)

        record[field_name] = normalized
        return CleanerResult(
            success=True,
            modified=True,
            before_value=value,
            after_value=normalized
        )
    return cleaner_func
```

Running this cleaner multiple times always produces the same result.

### Test Idempotency

```python
def test_idempotent():
    record = {'email': '  [email protected]  '}
    cleaner = normalize_email('email')

    # Run 5 times
    for i in range(5):
        result = cleaner(record, {})
        if i == 0:
            assert result.modified is True
        else:
            assert result.modified is False  # Subsequent runs: no change

    # Final value same as after first run
    assert record['email'] == '[email protected]'
```

---

## Naming Conventions

### Cleaner Names

**✅ Good naming:**

```python
# Verb-noun pattern
@cleaner(name='normalize_email')
@cleaner(name='validate_credit_card')
@cleaner(name='format_date')
@cleaner(name='strip_non_numeric')

# Clear, descriptive
@cleaner(name='truncate_description')
@cleaner(name='standardize_address')
```

**❌ Bad naming:**

```python
# Too vague
@cleaner(name='clean')
@cleaner(name='process')
@cleaner(name='fix')

# Too generic
@cleaner(name='cleaner1')
@cleaner(name='my_cleaner')
```

### Function Names

```python
# Factory function name should match cleaner name
@cleaner(name='normalize_email')
def normalize_email_cleaner(field_name):  # ✅ Good: matches cleaner name
    pass

@cleaner(name='normalize_email')
def some_random_name(field_name):  # ❌ Bad: confusing
    pass
```

---

## When NOT to Use Cleaners

### ❌ Don't use cleaners for:

1. **Complex business logic**
   - Multi-step workflows with decision trees
   - Logic that requires transaction coordination
   - Use service layer instead

2. **Data transformations that change meaning**
   - Converting currencies
   - Aggregating data
   - Use ETL pipelines instead

3. **Operations with side effects**
   - Sending emails
   - Triggering webhooks
   - Use event handlers instead

4. **Authorization/permissions**
   - Access control decisions
   - Use middleware/decorators instead

5. **Heavy computation**
   - Machine learning inference
   - Image processing
   - Use background jobs instead

### ✅ DO use cleaners for:

1. **Data normalization** - Standardize formats
2. **Whitespace trimming** - Remove extra spaces
3. **Case conversion** - Uppercase/lowercase
4. **NULL handling** - Replace with defaults
5. **Format validation** - Check and fix format issues
6. **Simple transformations** - Date formatting, phone numbers

---

## Monitoring & Alerting

### 1. Track Cleaner Execution

```python
import logging

logger = logging.getLogger(__name__)

@cleaner
def monitored_cleaner(field_name):
    def cleaner_func(record, context):
        start = time.time()

        try:
            # Cleaning logic
            result = CleanerResult(success=True, modified=True)

            # Log success
            duration = time.time() - start
            logger.info(f"Cleaner succeeded: {field_name} in {duration*1000:.2f}ms")

            return result

        except Exception as e:
            # Log failure
            logger.error(f"Cleaner failed: {field_name}", exc_info=True)
            return CleanerResult(success=False, error=str(e))

    return cleaner_func
```

### 2. Use Audit Logging

```python
from dql_core import AuditLogger, SafeCleanerExecutor

# Enable audit logging
audit_logger = AuditLogger(backend='file', file_path='/var/log/cleaners.log')
executor = SafeCleanerExecutor(manager, audit_logger)

# All cleaner executions logged
result = executor.execute_cleaners(cleaners, record, {})
```

### 3. Monitor Cleaner Failures

```python
# Track failure rate
class CleanerMetrics:
    def __init__(self):
        self.total = 0
        self.failures = 0

    def record(self, result):
        self.total += 1
        if not result.success:
            self.failures += 1

    def failure_rate(self):
        return self.failures / self.total if self.total > 0 else 0

metrics = CleanerMetrics()

for record in records:
    result = cleaner(record, {})
    metrics.record(result)

if metrics.failure_rate() > 0.05:  # More than 5% failures
    alert("High cleaner failure rate: {:.2%}".format(metrics.failure_rate()))
```

### 4. Alert on Slow Cleaners

```python
def track_performance(cleaner_name, duration):
    if duration > 0.1:  # Slower than 100ms
        alert(f"Slow cleaner detected: {cleaner_name} took {duration*1000:.0f}ms")
        # Send to monitoring system (Datadog, New Relic, etc.)
        metrics.timing(f'cleaner.{cleaner_name}.duration', duration)
```

---

## Summary Checklist

Before deploying a custom cleaner, verify:

- ✅ Handles NULL values gracefully
- ✅ Returns CleanerResult (never raises exceptions)
- ✅ Sets `modified=True` only when record changes
- ✅ Includes before/after values for audit trail
- ✅ Provides helpful error messages
- ✅ Validated and sanitized input
- ✅ Idempotent (safe to run multiple times)
- ✅ No database queries in hot path
- ✅ No synchronous external API calls for each record
- ✅ Comprehensive unit tests (happy path, edge cases, errors)
- ✅ Performance tested (<10ms for simple cleaners)
- ✅ Documented with docstring
- ✅ Monitoring and logging in place

---

## Next Steps

- **[Cleaner Catalog](cleaner-catalog.md)** - Explore built-in cleaners
- **[Custom Cleaners Guide](custom-cleaners-guide.md)** - Build your own
- **[Troubleshooting](troubleshooting.md)** - Debug issues
- **[Tutorial](tutorial.md)** - Hands-on examples
