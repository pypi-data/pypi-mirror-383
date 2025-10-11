# Cleaners Tutorial

Hands-on guide to using cleaners for data quality remediation.

## Table of Contents

1. [5-Minute Quick Start](#5-minute-quick-start)
2. [Tutorial 1: Basic Cleaners](#tutorial-1-basic-cleaners)
3. [Tutorial 2: Custom Cleaners](#tutorial-2-custom-cleaners)
4. [Tutorial 3: Cleaner Chains](#tutorial-3-cleaner-chains)
5. [Tutorial 4: Transaction Safety](#tutorial-4-transaction-safety)
6. [Real-World Example: Customer Data Cleanup](#real-world-example-customer-data-cleanup)

---

## 5-Minute Quick Start

Learn the basics of cleaners in 5 minutes.

### Step 1: Import Cleaners

```python
from dql_core.cleaners.string_cleaners import trim_whitespace, normalize_email
from dql_core.cleaners.data_type_cleaners import coalesce
```

### Step 2: Create a Record

```python
record = {
    'email': '  [email protected]  ',
    'name': 'John Doe',
    'status': None
}
```

### Step 3: Apply a Single Cleaner

```python
# Clean email field
cleaner = normalize_email('email')
result = cleaner(record, {})

print(record['email'])      # '[email protected]'
print(result.success)       # True
print(result.modified)      # True
```

### Step 4: Chain Multiple Cleaners

```python
from dql_core.cleaners.chain import CleanerChain

# Create chain
chain = (CleanerChain()
    .add('trim_whitespace', 'email')
    .add('lowercase', 'email')
    .add('normalize_email', 'email'))

# Execute chain
result = chain.execute(record, {})

print(record['email'])      # '[email protected]'
```

### Step 5: Use Transaction Safety

```python
from dql_core.cleaners.transaction import SafeCleanerExecutor, DictTransactionManager

# Create transaction manager and executor
manager = DictTransactionManager()
executor = SafeCleanerExecutor(manager)

# Execute cleaners with transaction safety
cleaners = [
    trim_whitespace('email'),
    normalize_email('email'),
    coalesce('status', default_value='pending')
]

result = executor.execute_cleaners(cleaners, record, {})

# Success → commits
# Failure → rolls back automatically

print(record['email'])      # '[email protected]'
print(record['status'])     # 'pending'
```

**🎉 Congratulations!** You've learned the basics of cleaners.

**Next Steps:**
- [Tutorial 1: Basic Cleaners](#tutorial-1-basic-cleaners) - Explore all built-in cleaners
- [Cleaner Catalog](cleaner-catalog.md) - Reference for all cleaners
- [Custom Cleaners Guide](custom-cleaners-guide.md) - Build your own

---

## Tutorial 1: Basic Cleaners

Explore all 8 built-in cleaners with hands-on examples.

### Setup

```python
from dql_core import (
    trim_whitespace,
    uppercase,
    lowercase,
    normalize_email,
    strip_non_numeric,
    normalize_phone,
    coalesce,
    format_date
)
```

### Exercise 1.1: String Cleaners

**Goal:** Clean messy customer data

```python
# Messy customer record
customer = {
    'first_name': '  john  ',
    'last_name': '  DOE  ',
    'email': '  [email protected]  '
}

# Clean first name: trim whitespace
cleaner = trim_whitespace('first_name')
result = cleaner(customer, {})
print(customer['first_name'])  # 'john'

# Clean last name: trim and uppercase
cleaner1 = trim_whitespace('last_name')
cleaner2 = uppercase('last_name')
cleaner1(customer, {})
cleaner2(customer, {})
print(customer['last_name'])   # 'DOE'

# Clean email: normalize
cleaner = normalize_email('email')
result = cleaner(customer, {})
print(customer['email'])       # '[email protected]'

# Final result
assert customer == {
    'first_name': 'john',
    'last_name': 'DOE',
    'email': '[email protected]'
}
```

### Exercise 1.2: Phone Number Cleaning

**Goal:** Normalize phone numbers to different formats

```python
records = [
    {'phone': '(555) 555-5555'},
    {'phone': '555-555-5555'},
    {'phone': '5555555555'},
]

# Clean to E164 format (international)
cleaner = normalize_phone('phone', format='E164')

for record in records:
    cleaner(record, {})
    print(record['phone'])

# All produce: '+15555555555'

# Clean to US format (pretty)
records2 = [{'phone': '5555555555'}]
cleaner = normalize_phone('phone', format='US')
cleaner(records2[0], {})
print(records2[0]['phone'])  # '(555) 555-5555'
```

### Exercise 1.3: NULL Handling

**Goal:** Replace NULL values with defaults

```python
products = [
    {'name': 'Product A', 'status': None, 'quantity': None},
    {'name': 'Product B', 'status': 'active', 'quantity': 10},
]

# Replace NULL status with 'pending'
status_cleaner = coalesce('status', default_value='pending')

# Replace NULL quantity with 0
quantity_cleaner = coalesce('quantity', default_value=0)

for product in products:
    status_cleaner(product, {})
    quantity_cleaner(product, {})

print(products[0])
# {'name': 'Product A', 'status': 'pending', 'quantity': 0}

print(products[1])
# {'name': 'Product B', 'status': 'active', 'quantity': 10}
```

### Exercise 1.4: Date Formatting

**Goal:** Convert dates between formats

```python
events = [
    {'name': 'Event 1', 'date': '2025-01-15'},
    {'name': 'Event 2', 'date': '2025-02-20'},
]

# Convert ISO to US format
cleaner = format_date(
    'date',
    input_format='%Y-%m-%d',
    output_format='%m/%d/%Y'
)

for event in events:
    cleaner(event, {})
    print(f"{event['name']}: {event['date']}")

# Output:
# Event 1: 01/15/2025
# Event 2: 02/20/2025
```

**✅ Checkpoint:** You now know how to use all 8 built-in cleaners!

---

## Tutorial 2: Custom Cleaners

Build your own cleaners for domain-specific rules.

### Exercise 2.1: Simple Custom Cleaner

**Goal:** Create a cleaner that removes special characters

```python
from dql_core import cleaner, CleanerResult
import re

@cleaner(name='remove_special_chars')
def remove_special_chars_cleaner(field_name: str):
    """Remove special characters, keep only alphanumeric and spaces."""
    def cleaner_func(record, context):
        # Get value
        value = record.get(field_name)

        if value is None:
            return CleanerResult(success=True, modified=False)

        # Remove special characters
        cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', value)

        # Set new value
        record[field_name] = cleaned

        return CleanerResult(
            success=True,
            modified=(value != cleaned),
            before_value=value,
            after_value=cleaned
        )

    return cleaner_func

# Test it
record = {'description': 'Product #123 (special!)'}
cleaner = remove_special_chars_cleaner('description')
result = cleaner(record, {})

print(record['description'])  # 'Product 123 special'
print(result.modified)        # True
```

### Exercise 2.2: Parameterized Custom Cleaner

**Goal:** Create a cleaner that truncates strings to max length

```python
@cleaner(name='truncate_string')
def truncate_string_cleaner(field_name: str, max_length: int = 100, suffix: str = '...'):
    """Truncate string to maximum length with optional suffix."""
    def cleaner_func(record, context):
        value = record.get(field_name)

        if not value or len(value) <= max_length:
            return CleanerResult(success=True, modified=False)

        # Truncate
        truncated = value[:max_length - len(suffix)] + suffix

        record[field_name] = truncated

        return CleanerResult(
            success=True,
            modified=True,
            before_value=value,
            after_value=truncated
        )

    return cleaner_func

# Test with different parameters
record1 = {'bio': 'A' * 200}
cleaner1 = truncate_string_cleaner('bio', max_length=50)
cleaner1(record1, {})
print(len(record1['bio']))  # 50

record2 = {'description': 'B' * 200}
cleaner2 = truncate_string_cleaner('description', max_length=100, suffix='...')
cleaner2(record2, {})
print(len(record2['description']))  # 100
```

### Exercise 2.3: Validation Custom Cleaner

**Goal:** Create a cleaner that validates and normalizes SSNs

```python
@cleaner(name='normalize_ssn')
def normalize_ssn_cleaner(field_name: str):
    """Normalize SSN to XXX-XX-XXXX format."""
    def cleaner_func(record, context):
        value = record.get(field_name)

        if value is None:
            return CleanerResult(success=True, modified=False)

        # Remove all non-digits
        digits = re.sub(r'[^0-9]', '', str(value))

        # Validate length
        if len(digits) != 9:
            return CleanerResult(
                success=False,
                modified=False,
                error=f"SSN must be 9 digits, got {len(digits)}"
            )

        # Format
        formatted = f"{digits[0:3]}-{digits[3:5]}-{digits[5:9]}"
        record[field_name] = formatted

        return CleanerResult(
            success=True,
            modified=(str(value) != formatted),
            before_value=value,
            after_value=formatted
        )

    return cleaner_func

# Test with valid SSN
record = {'ssn': '123456789'}
cleaner = normalize_ssn_cleaner('ssn')
result = cleaner(record, {})

print(record['ssn'])    # '123-45-6789'
print(result.success)   # True

# Test with invalid SSN
record2 = {'ssn': '123'}
result2 = cleaner(record2, {})
print(result2.success)  # False
print(result2.error)    # 'SSN must be 9 digits, got 3'
```

**✅ Checkpoint:** You can now build custom cleaners!

---

## Tutorial 3: Cleaner Chains

Combine multiple cleaners into a workflow.

### Exercise 3.1: Simple Chain

**Goal:** Create an email normalization workflow

```python
from dql_core.cleaners.chain import CleanerChain

# Create chain with method chaining
chain = (CleanerChain()
    .add('trim_whitespace', 'email')
    .add('lowercase', 'email')
    .add('normalize_email', 'email'))

# Test
record = {'email': '  [email protected]  '}
result = chain.execute(record, {})

print(record['email'])      # '[email protected]'
print(result.success)       # True
print(result.modified)      # True
```

### Exercise 3.2: Multi-Field Chain

**Goal:** Clean multiple fields in one workflow

```python
# Create separate chains for different fields
email_chain = (CleanerChain()
    .add('trim_whitespace', 'email')
    .add('lowercase', 'email'))

name_chain = (CleanerChain()
    .add('trim_whitespace', 'name')
    .add('uppercase', 'name'))

# Apply chains
customer = {
    'email': '  [email protected]  ',
    'name': '  john doe  '
}

email_chain.execute(customer, {})
name_chain.execute(customer, {})

print(customer)
# {'email': '[email protected]', 'name': 'JOHN DOE'}
```

### Exercise 3.3: Chain with Custom Cleaners

**Goal:** Mix built-in and custom cleaners

```python
# Custom cleaner from previous exercise
@cleaner
def remove_special_chars(field_name):
    def cleaner_func(record, context):
        value = record.get(field_name)
        if not value:
            return CleanerResult(success=True, modified=False)
        cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', value)
        record[field_name] = cleaned
        return CleanerResult(success=True, modified=True)
    return cleaner_func

# Create chain with built-in and custom
chain = (CleanerChain()
    .add('trim_whitespace', 'description')
    .add('remove_special_chars', 'description')  # Custom!
    .add('lowercase', 'description'))

record = {'description': '  Product #123 (NEW!)  '}
chain.execute(record, {})

print(record['description'])  # 'product 123 new'
```

### Exercise 3.4: Error Handling in Chains

**Goal:** Understand short-circuit behavior

```python
# Chain with failing cleaner
def failing_cleaner(field_name):
    def cleaner_func(record, context):
        return CleanerResult(success=False, error="Validation failed!")
    return cleaner_func

chain = CleanerChain()
chain.add('trim_whitespace', 'email')
chain.add('failing_cleaner', 'email')  # This will fail
chain.add('lowercase', 'email')        # This won't execute

record = {'email': '  [email protected]  '}
result = chain.execute(record, {})

print(result.success)  # False
print(result.error)    # 'Validation failed!'
print(record['email']) # '  TEST  ' (trim executed, lowercase did not)
```

**✅ Checkpoint:** You can now build complex cleaner workflows!

---

## Tutorial 4: Transaction Safety

Use transactions to ensure all-or-nothing cleaner execution.

### Exercise 4.1: Basic Transaction

**Goal:** Execute cleaners with automatic rollback

```python
from dql_core.cleaners.transaction import SafeCleanerExecutor, DictTransactionManager

# Create transaction manager and executor
manager = DictTransactionManager()
executor = SafeCleanerExecutor(manager)

# Define cleaners
cleaners = [
    trim_whitespace('email'),
    lowercase('email'),
    normalize_email('email')
]

# Execute with transaction safety
record = {'email': '  [email protected]  '}
result = executor.execute_cleaners(cleaners, record, {})

print(result.success)   # True
print(record['email'])  # '[email protected]'
```

### Exercise 4.2: Rollback on Failure

**Goal:** See automatic rollback when cleaner fails

```python
# Cleaner that always fails
def failing_cleaner(field_name):
    def cleaner_func(record, context):
        return CleanerResult(success=False, error="Simulated failure")
    return cleaner_func

# Create cleaners with one that fails
cleaners = [
    trim_whitespace('email'),    # This succeeds
    failing_cleaner('email'),    # This fails
    lowercase('email')           # This won't execute
]

record = {'email': '  [email protected]  '}
original_email = record['email']

result = executor.execute_cleaners(cleaners, record, {})

print(result.success)     # False
print(result.error)       # 'Simulated failure'
print(record['email'])    # '  [email protected]  ' (rolled back!)
print(record['email'] == original_email)  # True
```

### Exercise 4.3: Dry-Run Mode

**Goal:** Preview changes without committing

```python
# Preview what cleaners would do
cleaners = [
    trim_whitespace('email'),
    lowercase('email')
]

record = {'email': '  [email protected]  '}
original_email = record['email']

# Dry-run: preview changes
result = executor.preview_changes(cleaners, record, {})

print(f"Would modify: {result.modified}")   # True
print(f"Would change to: {result.after_value}")  # '[email protected]'
print(f"Original unchanged: {record['email']}")  # '  [email protected]  '

# User confirms, now run for real
if input("Apply changes? (y/n): ") == 'y':
    result = executor.execute_cleaners(cleaners, record, {})
    print(f"Applied: {record['email']}")  # '[email protected]'
```

### Exercise 4.4: Audit Logging

**Goal:** Track all cleaner modifications

```python
from dql_core.cleaners.audit import AuditLogger

# Create audit logger
audit_logger = AuditLogger(backend='memory')
executor = SafeCleanerExecutor(manager, audit_logger)

# Execute cleaners
cleaners = [trim_whitespace('email'), lowercase('email')]
record = {'email': '  [email protected]  '}

result = executor.execute_cleaners(cleaners, record, {})

# Review audit logs
logs = audit_logger.get_logs()
for log in logs:
    print(f"Transaction: {log.transaction_id}")
    print(f"Cleaners: {log.cleaner_names}")
    print(f"Changed: {log.before_value} → {log.after_value}")
```

**✅ Checkpoint:** You can now use transaction safety!

---

## Real-World Example: Customer Data Cleanup

A complete example cleaning customer records from a legacy system.

### Scenario

You've imported 10,000 customer records from a legacy system. The data is messy:
- Emails have extra whitespace and mixed case
- Phone numbers have various formats
- Status field is NULL for many records
- Some records have invalid SSNs

**Goal:** Clean all records with transaction safety and audit logging.

### Step 1: Analyze the Data

```python
# Sample of messy data
customers = [
    {
        'id': 1,
        'email': '  [email protected]  ',
        'phone': '(555) 555-1234',
        'status': None,
        'ssn': '123456789'
    },
    {
        'id': 2,
        'email': '[email protected]',
        'phone': '555-555-5678',
        'status': 'ACTIVE',
        'ssn': '987-65-4321'
    },
    {
        'id': 3,
        'email': '  BAD DATA  ',
        'phone': '5555551111',
        'status': None,
        'ssn': '123'  # Invalid!
    }
]

print(f"Total customers: {len(customers)}")
```

### Step 2: Build Cleaning Pipeline

```python
from dql_core.cleaners.chain import CleanerChain
from dql_core.cleaners.transaction import SafeCleanerExecutor, DictTransactionManager
from dql_core.cleaners.audit import AuditLogger

# Create chains for each field
email_chain = CleanerChain().add('trim_whitespace', 'email').add('lowercase', 'email')
phone_cleaner = normalize_phone('phone', format='E164')
status_cleaner = coalesce('status', default_value='pending')
ssn_cleaner = normalize_ssn_cleaner('ssn')  # Custom cleaner from Tutorial 2

# Setup transaction safety with audit logging
manager = DictTransactionManager()
audit_logger = AuditLogger(backend='memory')
executor = SafeCleanerExecutor(manager, audit_logger)
```

### Step 3: Clean Records with Error Handling

```python
cleaned_count = 0
failed_count = 0
failed_records = []

for customer in customers:
    # Preview changes first (optional)
    cleaners = [email_chain, phone_cleaner, status_cleaner, ssn_cleaner]

    # Execute with transaction safety
    result = executor.execute_cleaners(cleaners, customer, {})

    if result.success:
        cleaned_count += 1
        print(f"✓ Cleaned customer {customer['id']}")
    else:
        failed_count += 1
        failed_records.append((customer['id'], result.error))
        print(f"✗ Failed customer {customer['id']}: {result.error}")

print(f"\n=== Summary ===")
print(f"Cleaned: {cleaned_count}")
print(f"Failed: {failed_count}")
```

### Step 4: Review Results

```python
# Show cleaned records
print("\n=== Cleaned Records ===")
for customer in customers[:2]:  # Show first 2
    print(f"Customer {customer['id']}:")
    print(f"  Email: {customer['email']}")
    print(f"  Phone: {customer['phone']}")
    print(f"  Status: {customer['status']}")
    print(f"  SSN: {customer['ssn']}")

# Show failures
print("\n=== Failed Records ===")
for customer_id, error in failed_records:
    print(f"Customer {customer_id}: {error}")

# Review audit log
print("\n=== Audit Log ===")
logs = audit_logger.get_logs()
print(f"Total modifications: {len(logs)}")
for log in logs[:3]:  # Show first 3
    print(f"Transaction: {log.transaction_id}")
    print(f"Cleaners: {log.cleaner_names}")
    print(f"Changed: {log.before_value} → {log.after_value}")
```

### Expected Output

```
✓ Cleaned customer 1
✓ Cleaned customer 2
✗ Failed customer 3: SSN must be 9 digits, got 3

=== Summary ===
Cleaned: 2
Failed: 1

=== Cleaned Records ===
Customer 1:
  Email: [email protected]
  Phone: +15555551234
  Status: pending
  SSN: 123-45-6789

Customer 2:
  Email: [email protected]
  Phone: +15555555678
  Status: active
  SSN: 987-65-4321

=== Failed Records ===
Customer 3: SSN must be 9 digits, got 3

=== Audit Log ===
Total modifications: 8
Transaction: abc-123
Cleaners: ['trim_whitespace', 'lowercase']
Changed:   [email protected]   → [email protected]
```

### Step 5: Handle Failed Records

```python
# Retry failed records with more lenient SSN cleaner
def lenient_ssn_cleaner(field_name):
    """Accept any SSN, just format if valid"""
    def cleaner_func(record, context):
        value = record.get(field_name)
        if not value:
            return CleanerResult(success=True, modified=False)

        digits = re.sub(r'[^0-9]', '', str(value))

        # If valid, format; otherwise leave as-is
        if len(digits) == 9:
            formatted = f"{digits[0:3]}-{digits[3:5]}-{digits[5:9]}"
            record[field_name] = formatted
            return CleanerResult(success=True, modified=True)
        else:
            # Just accept it
            return CleanerResult(success=True, modified=False)

    return cleaner_func

# Retry failed records
for customer_id, error in failed_records:
    customer = next(c for c in customers if c['id'] == customer_id)

    # Use lenient cleaner
    cleaners = [email_chain, phone_cleaner, status_cleaner, lenient_ssn_cleaner('ssn')]

    result = executor.execute_cleaners(cleaners, customer, {})
    if result.success:
        print(f"✓ Retry succeeded for customer {customer_id}")
    else:
        print(f"✗ Retry failed for customer {customer_id}: {result.error}")
```

**🎉 Congratulations!** You've completed a real-world cleaning pipeline!

---

## What You've Learned

✅ Using all 8 built-in cleaners
✅ Creating custom cleaners
✅ Building cleaner chains
✅ Transaction safety with rollback
✅ Dry-run mode and audit logging
✅ Error handling strategies
✅ Real-world data cleaning pipeline

## Next Steps

- **[Cleaner Catalog](cleaner-catalog.md)** - Complete reference
- **[Custom Cleaners Guide](custom-cleaners-guide.md)** - Advanced patterns
- **[Best Practices](cleaner-best-practices.md)** - Performance and security
- **[Troubleshooting](troubleshooting.md)** - Debug common issues
- **[Examples Directory](../examples/)** - Runnable code samples
