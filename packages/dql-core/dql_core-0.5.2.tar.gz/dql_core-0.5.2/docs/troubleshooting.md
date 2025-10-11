# Troubleshooting Guide

Solutions to common cleaner issues and debugging techniques.

## Table of Contents

- [Common Errors](#common-errors)
- [Debugging Techniques](#debugging-techniques)
- [Performance Issues](#performance-issues)
- [Concurrency Issues](#concurrency-issues)
- [FAQ](#faq)

---

## Common Errors

### Error: "Cleaner not found in registry"

**Symptom:**
```
CleanerError: No cleaner registered with name 'normalize_ssn'
```

**Causes:**
1. Cleaner not imported
2. Cleaner not decorated with `@cleaner`
3. Typo in cleaner name

**Solutions:**

```python
# Solution 1: Import cleaner module
from my_app.custom_cleaners import normalize_ssn_cleaner

# Solution 2: Use auto-discovery
from dql_core import discover_cleaners
discover_cleaners('my_app/custom_cleaners/')

# Solution 3: Manually register
from dql_core import CleanerRegistry
registry = CleanerRegistry()
registry.register('normalize_ssn', normalize_ssn_cleaner)

# Solution 4: Check spelling
cleaner = get_cleaner('normalize_ssn')  # Correct spelling
```

**Debug:**
```python
# List all registered cleaners
from dql_core import CleanerRegistry
registry = CleanerRegistry()
print(registry.list_cleaners())
```

---

### Error: "Transaction rollback"

**Symptom:**
```
TransactionRollback: Transaction rolled back due to cleaner failure
```

**Cause:** One or more cleaners in chain failed

**Solution:**

```python
# Check which cleaner failed
result = executor.execute_cleaners(cleaners, record, {})

if not result.success:
    print(f"Cleaner failed: {result.error}")

# Use dry-run to test
result = executor.preview_changes(cleaners, record, {})
print(f"Would succeed: {result.success}")
```

**Debug with individual cleaners:**

```python
# Test cleaners one by one
for i, cleaner in enumerate(cleaners):
    result = cleaner(record, {})
    if not result.success:
        print(f"Cleaner {i} failed: {result.error}")
        break
```

---

### Error: "Invalid cleaner signature"

**Symptom:**
```
TypeError: Cleaner function must have exactly 2 parameters (record, context)
```

**Cause:** Cleaner function doesn't match required signature

**Wrong:**
```python
@cleaner
def bad_cleaner():  # ❌ No parameters
    pass

@cleaner
def bad_cleaner(record):  # ❌ Only 1 parameter
    pass

@cleaner
def bad_cleaner(record, context, extra):  # ❌ Too many parameters
    pass
```

**Correct:**
```python
@cleaner
def good_cleaner(field_name):  # ✅ Factory function
    def cleaner_func(record, context):  # ✅ Cleaner with correct signature
        # ...
        return CleanerResult(success=True, modified=False)
    return cleaner_func
```

**Solution:**
- Use factory pattern: outer function for parameters, inner function for (record, context)
- Or disable validation: `@cleaner(validate=False)` (not recommended)

---

### Error: "Field not found on record"

**Symptom:**
```
AttributeError: 'Customer' object has no attribute 'emial'
KeyError: 'emial'
```

**Cause:** Typo in field name or field doesn't exist

**Solution:**

```python
@cleaner
def safe_cleaner(field_name):
    def cleaner_func(record, context):
        # Check field exists before accessing
        if hasattr(record, field_name):
            value = getattr(record, field_name)
        elif isinstance(record, dict) and field_name in record:
            value = record[field_name]
        else:
            return CleanerResult(
                success=False,
                modified=False,
                error=f"Field '{field_name}' not found on record"
            )

        # Continue with cleaning...
        return CleanerResult(success=True, modified=False)

    return cleaner_func
```

**Debug:**
```python
# Check available fields
if isinstance(record, dict):
    print(f"Available fields: {list(record.keys())}")
else:
    print(f"Available fields: {dir(record)}")
```

---

### Error: "Record not modified after cleaner"

**Symptom:** Cleaner returns `success=True` but record unchanged

**Causes:**
1. Not setting field value
2. Setting value on wrong object
3. Field is read-only

**Solution:**

```python
@cleaner
def my_cleaner(field_name):
    def cleaner_func(record, context):
        value = getattr(record, field_name) if hasattr(record, field_name) else record.get(field_name)

        new_value = transform(value)

        # IMPORTANT: Actually set the value!
        if hasattr(record, field_name):
            setattr(record, field_name, new_value)  # ✅ Set on object
        else:
            record[field_name] = new_value  # ✅ Set on dict

        return CleanerResult(
            success=True,
            modified=(value != new_value),
            before_value=value,
            after_value=new_value
        )

    return cleaner_func
```

**Debug:**
```python
# Check if field is read-only
try:
    setattr(record, field_name, 'test')
except AttributeError as e:
    print(f"Field is read-only: {e}")
```

---

### Error: "Cleaner modifying wrong field"

**Symptom:** Cleaner modifies different field than expected

**Cause:** Hard-coded field name instead of using parameter

**Wrong:**
```python
@cleaner
def bad_cleaner(field_name):
    def cleaner_func(record, context):
        # ❌ BAD: Hard-coded field name
        record['email'] = record['email'].lower()
        return CleanerResult(success=True, modified=True)
    return cleaner_func
```

**Correct:**
```python
@cleaner
def good_cleaner(field_name):
    def cleaner_func(record, context):
        # ✅ GOOD: Use field_name parameter
        if hasattr(record, field_name):
            value = getattr(record, field_name)
            setattr(record, field_name, value.lower())
        else:
            value = record[field_name]
            record[field_name] = value.lower()
        return CleanerResult(success=True, modified=True)
    return cleaner_func
```

---

### Error: "Maximum recursion depth exceeded"

**Symptom:**
```
RecursionError: maximum recursion depth exceeded
```

**Cause:** Cleaner calling itself or circular dependency

**Wrong:**
```python
@cleaner
def recursive_cleaner(field_name):
    def cleaner_func(record, context):
        # ❌ BAD: Cleaner calls itself
        result = recursive_cleaner(field_name)(record, context)
        return result
    return cleaner_func
```

**Solution:** Remove circular dependency

```python
@cleaner
def fixed_cleaner(field_name):
    def cleaner_func(record, context):
        # ✅ Direct logic, no recursion
        value = record[field_name]
        record[field_name] = value.strip()
        return CleanerResult(success=True, modified=True)
    return cleaner_func
```

---

## Debugging Techniques

### 1. Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('dql_core.cleaners')

# Now all cleaner operations logged
```

### 2. Use Dry-Run Mode

```python
from dql_core import SafeCleanerExecutor, DictTransactionManager

manager = DictTransactionManager()
executor = SafeCleanerExecutor(manager)

# Preview changes without committing
result = executor.preview_changes(cleaners, record, {})

print(f"Would modify: {result.modified}")
print(f"Before: {result.before_value}")
print(f"After: {result.after_value}")
print(f"Success: {result.success}")

if not result.success:
    print(f"Error: {result.error}")
```

### 3. Inspect CleanerResult

```python
result = cleaner(record, {})

print(f"Success: {result.success}")
print(f"Modified: {result.modified}")
print(f"Before: {result.before_value}")
print(f"After: {result.after_value}")
print(f"Error: {result.error}")

# Check if result is valid
assert isinstance(result, CleanerResult), "Cleaner must return CleanerResult"
```

### 4. Test Cleaner in Isolation

```python
# Test cleaner outside of chain
record = {'email': '  [email protected]  '}
cleaner = normalize_email('email')
result = cleaner(record, {})

assert result.success, f"Cleaner failed: {result.error}"
assert record['email'] == '[email protected]', f"Expected '[email protected]', got '{record['email']}'"
```

### 5. Use Audit Logging

```python
from dql_core import AuditLogger

audit_logger = AuditLogger(backend='memory')
executor = SafeCleanerExecutor(manager, audit_logger)

# Execute cleaners
result = executor.execute_cleaners(cleaners, record, {})

# Review audit log
logs = audit_logger.get_logs()
for log in logs:
    print(f"Transaction: {log.transaction_id}")
    print(f"Cleaners: {log.cleaner_names}")
    print(f"Record ID: {log.record_id}")
    print(f"Changed: {log.before_value} → {log.after_value}")
```

### 6. Add Debug Prints

```python
@cleaner
def debug_cleaner(field_name):
    def cleaner_func(record, context):
        print(f"[DEBUG] Field: {field_name}")
        print(f"[DEBUG] Record: {record}")
        print(f"[DEBUG] Context: {context}")

        value = record.get(field_name)
        print(f"[DEBUG] Value: {value}")

        # Cleaning logic...
        new_value = value.strip()
        print(f"[DEBUG] New value: {new_value}")

        record[field_name] = new_value
        return CleanerResult(success=True, modified=True)

    return cleaner_func
```

### 7. Use Python Debugger

```python
@cleaner
def cleaner_with_breakpoint(field_name):
    def cleaner_func(record, context):
        import pdb; pdb.set_trace()  # Breakpoint

        # Cleaning logic...
        return CleanerResult(success=True, modified=False)

    return cleaner_func
```

---

## Performance Issues

### Issue: Slow Cleaner Execution

**Symptom:** Cleaners take >1 second for 1000 records

**Diagnosis:**

```python
import time

def profile_cleaners(cleaners, records):
    for i, cleaner in enumerate(cleaners):
        start = time.time()

        for record in records:
            cleaner(record, {})

        duration = time.time() - start
        print(f"Cleaner {i}: {duration:.2f}s ({duration/len(records)*1000:.2f}ms per record)")
```

**Solutions:**

1. **Remove database queries**
   ```python
   # BAD: Query in cleaner
   def slow_cleaner(field_name):
       def cleaner_func(record, context):
           # N+1 query problem
           related = RelatedModel.objects.get(id=record.related_id)
           return CleanerResult(success=True, modified=False)
       return cleaner_func

   # GOOD: Prefetch before cleaning
   records = Record.objects.prefetch_related('related').all()
   ```

2. **Batch operations**
   ```python
   # Process records in transactions
   with manager.transaction():
       for record in records:
           cleaner(record, {})
   ```

3. **Use simpler regex**
   ```python
   # SLOW: Complex regex
   pattern = r'^(a+)+$'

   # FAST: Simple regex
   pattern = r'^[a]+$'
   ```

### Issue: High Memory Usage

**Symptom:** Process uses >1GB RAM for 10k records

**Solutions:**

1. **Process in batches**
   ```python
   def process_in_batches(records, batch_size=1000):
       for i in range(0, len(records), batch_size):
           batch = records[i:i+batch_size]
           for record in batch:
               cleaner(record, {})
   ```

2. **Use generators**
   ```python
   # BAD: Load all records
   records = list(Record.objects.all())  # Loads everything into memory

   # GOOD: Use iterator
   for record in Record.objects.iterator(chunk_size=1000):
       cleaner(record, {})
   ```

---

## Concurrency Issues

### Issue: Race Conditions

**Symptom:** Records have inconsistent values after parallel cleaning

**Cause:** Multiple cleaners modifying same record concurrently

**Solution: Use locking**

```python
import threading

lock = threading.Lock()

@cleaner
def thread_safe_cleaner(field_name):
    def cleaner_func(record, context):
        with lock:
            # Thread-safe cleaning
            value = record[field_name]
            record[field_name] = value.strip()
            return CleanerResult(success=True, modified=True)
    return cleaner_func
```

**Solution: Use transactions**

```python
from dql_core import SafeCleanerExecutor, DjangoTransactionManager

# Cleaners execute in transaction (serialized)
manager = DjangoTransactionManager()
executor = SafeCleanerExecutor(manager)
```

### Issue: Database Deadlocks

**Symptom:**
```
TransactionRollback: Database deadlock detected
```

**Solution: Increase isolation level**

```python
# Use SERIALIZABLE isolation
manager = DjangoTransactionManager(isolation_level='SERIALIZABLE')
```

**Solution: Serialize cleaners**

```python
# Don't run cleaners in parallel
for record in records:
    result = executor.execute_cleaners(cleaners, record, {})
```

---

## FAQ

### Q: Why is my cleaner not modifying the record?

**A:** Common causes:

1. Not setting field value:
   ```python
   # Wrong
   new_value = value.strip()  # Not setting field!

   # Correct
   record[field_name] = value.strip()
   ```

2. Returning wrong result:
   ```python
   # Wrong
   return CleanerResult(success=True, modified=False)  # Says not modified!

   # Correct
   return CleanerResult(success=True, modified=True)
   ```

3. Record is read-only (check with `hasattr(record, '__setattr__')`)

### Q: How do I test cleaners with Django models?

**A:**

```python
from django.test import TestCase
from myapp.models import Customer
from dql_core import normalize_email

class CleanerTestCase(TestCase):
    def test_normalize_customer_email(self):
        customer = Customer.objects.create(email='  [email protected]  ')

        cleaner = normalize_email('email')
        result = cleaner(customer, {})

        self.assertTrue(result.success)
        self.assertTrue(result.modified)
        self.assertEqual(customer.email, '[email protected]')

        # Save and verify
        customer.save()
        customer.refresh_from_db()
        self.assertEqual(customer.email, '[email protected]')
```

### Q: Can cleaners call other cleaners?

**A:** Yes, but use CleanerChain instead:

```python
# Instead of this (don't do):
@cleaner
def combo_cleaner(field_name):
    def cleaner_func(record, context):
        # Manually calling other cleaners
        trim_whitespace(field_name)(record, context)
        lowercase(field_name)(record, context)
        return CleanerResult(success=True, modified=True)
    return cleaner_func

# Use CleanerChain:
from dql_core import CleanerChain

chain = (CleanerChain()
    .add('trim_whitespace', 'email')
    .add('lowercase', 'email'))

result = chain.execute(record, {})
```

### Q: How do I handle errors in cleaners?

**A:** Return CleanerResult with error:

```python
@cleaner
def safe_cleaner(field_name):
    def cleaner_func(record, context):
        try:
            # Cleaning logic
            return CleanerResult(success=True, modified=True)
        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                error=f"Cleaner failed: {str(e)}"
            )
    return cleaner_func
```

### Q: Can I use cleaners outside of DQL?

**A:** Yes! Cleaners are standalone functions:

```python
from dql_core import normalize_email

# Use directly
record = {'email': '  [email protected]  '}
cleaner = normalize_email('email')
result = cleaner(record, {})

print(record['email'])  # '[email protected]'
```

### Q: How do I debug "modified=False" when record was modified?

**A:** You're probably not setting `modified` correctly:

```python
@cleaner
def my_cleaner(field_name):
    def cleaner_func(record, context):
        value = record[field_name]
        new_value = value.strip()

        # IMPORTANT: Check if value changed
        modified = (value != new_value)

        record[field_name] = new_value

        return CleanerResult(
            success=True,
            modified=modified,  # ✅ Correct
            before_value=value,
            after_value=new_value
        )
    return cleaner_func
```

### Q: Can cleaners modify multiple fields?

**A:** Yes, but you must track all changes:

```python
@cleaner
def multi_field_cleaner(field1, field2):
    def cleaner_func(record, context):
        val1 = record[field1]
        val2 = record[field2]

        new_val1 = val1.strip()
        new_val2 = val2.lower()

        modified = (val1 != new_val1 or val2 != new_val2)

        record[field1] = new_val1
        record[field2] = new_val2

        return CleanerResult(
            success=True,
            modified=modified,
            before_value={'field1': val1, 'field2': val2},
            after_value={'field1': new_val1, 'field2': new_val2}
        )
    return cleaner_func
```

### Q: How do I make cleaners work with both dicts and objects?

**A:** Use this pattern:

```python
@cleaner
def universal_cleaner(field_name):
    def cleaner_func(record, context):
        # Get value (works with dicts and objects)
        if hasattr(record, field_name):
            value = getattr(record, field_name)
        else:
            value = record.get(field_name)

        # Process value
        new_value = value.strip()

        # Set value (works with dicts and objects)
        if hasattr(record, field_name):
            setattr(record, field_name, new_value)
        else:
            record[field_name] = new_value

        return CleanerResult(success=True, modified=True)
    return cleaner_func
```

### Q: What's the difference between @cleaner and @register_cleaner?

**A:**

- `@cleaner` (Story 2.6) - Modern, automatic registration, uses function name
- `@register_cleaner(name)` - Legacy, explicit name required

**Use @cleaner for new code:**
```python
@cleaner  # ✅ Modern
def normalize_email(field_name):
    pass

@register_cleaner('normalize_email')  # ⚠️ Legacy
def normalize_email(record, context):
    pass
```

---

## Getting Help

If you're still stuck:

1. **Check the documentation:**
   - [Cleaner Catalog](cleaner-catalog.md)
   - [Custom Cleaners Guide](custom-cleaners-guide.md)
   - [Best Practices](cleaner-best-practices.md)

2. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Create a minimal reproduction:**
   ```python
   # Simplest possible example that shows the issue
   record = {'email': 'test'}
   cleaner = my_cleaner('email')
   result = cleaner(record, {})
   print(result)
   ```

4. **Check GitHub Issues:** [github.com/your-org/dql/issues](https://github.com)

5. **Ask on Discord/Slack:** [Link to community]
