# Custom Cleaners Guide

Learn how to build your own cleaners for domain-specific data quality rules.

## Overview

While dql-core provides 8 built-in cleaners, real-world applications often need custom cleaners for:

- **Domain-specific validation** - SSN, credit cards, tax IDs
- **Business rules** - Company-specific formatting standards
- **External API integration** - Address validation, data enrichment
- **Complex transformations** - Multi-field cleaning, conditional logic

This guide shows you how to build, test, and deploy custom cleaners.

---

## Quick Start: Your First Custom Cleaner

Let's build a cleaner that normalizes Social Security Numbers to `XXX-XX-XXXX` format.

### Step 1: Import Requirements

```python
from dql_core import cleaner, CleanerResult
import re
```

### Step 2: Write the Cleaner Function

```python
@cleaner(name='normalize_ssn')
def normalize_ssn_cleaner(field_name: str):
    """
    Normalize SSN to XXX-XX-XXXX format.

    Example: "123456789" → "123-45-6789"
    """
    def cleaner_func(record, context):
        # Get field value
        value = getattr(record, field_name) if hasattr(record, field_name) else record.get(field_name)

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

        # Format as XXX-XX-XXXX
        formatted = f"{digits[0:3]}-{digits[3:5]}-{digits[5:9]}"

        # Apply change
        if hasattr(record, field_name):
            setattr(record, field_name, formatted)
        else:
            record[field_name] = formatted

        return CleanerResult(
            success=True,
            modified=(str(value) != formatted),
            before_value=value,
            after_value=formatted
        )

    return cleaner_func
```

### Step 3: Use Your Cleaner

```python
# Create cleaner instance
cleaner = normalize_ssn_cleaner('ssn')

# Apply to record
record = {'ssn': '123456789'}
result = cleaner(record, {})

print(record['ssn'])      # '123-45-6789'
print(result.success)     # True
print(result.modified)    # True
```

**That's it!** Your custom cleaner is ready to use.

---

## Cleaner Anatomy

### The @cleaner Decorator

The `@cleaner` decorator handles registration and validation:

```python
@cleaner(name='my_cleaner', validate=True)
def my_cleaner_function(field_name: str):
    # Returns cleaner function
    pass
```

**Parameters:**
- `name` (str, optional): Registration name (default: function name)
- `validate` (bool, optional): Validate cleaner signature (default: True)

**What it does:**
- Registers cleaner in global CleanerRegistry
- Validates function signature (2 parameters: record, context)
- Enables auto-discovery
- Provides introspection metadata

### Cleaner Factory Pattern

Cleaners use the **factory pattern** - a function that returns a function:

```python
@cleaner
def my_cleaner(field_name: str):           # Factory (configures cleaner)
    def cleaner_func(record, context):      # Cleaner (executes cleaning)
        # Cleaning logic here
        return CleanerResult(...)
    return cleaner_func
```

**Why factory pattern?**
- Parameterize cleaners (field name, options)
- Reuse cleaner logic for different fields
- Separate configuration from execution

### Cleaner Function Signature

The inner cleaner function must have this exact signature:

```python
def cleaner_func(record: Any, context: dict) -> CleanerResult:
    pass
```

**Parameters:**

1. **record** (Any): The record to clean
   - Can be dict, Django model, SQLAlchemy model, or any object
   - **Mutable** - modify in-place

2. **context** (dict): Execution context with metadata
   - Contains: `field_name`, `expectation`, `validation_result`, etc.
   - Use for conditional logic or logging

**Returns:** `CleanerResult` with:
- `success` (bool): Did cleaner succeed?
- `modified` (bool): Was record changed?
- `before_value` (Any): Original value
- `after_value` (Any): New value
- `error` (str): Error message if failed

---

## CleanerResult Structure

```python
from dql_core import CleanerResult

# Success case
result = CleanerResult(
    success=True,
    modified=True,
    before_value='  hello  ',
    after_value='hello'
)

# Failure case
result = CleanerResult(
    success=False,
    modified=False,
    error='Field value is invalid'
)

# No-op case (NULL value)
result = CleanerResult(
    success=True,
    modified=False
)
```

**Field Meanings:**

| Field | Type | Purpose |
|-------|------|---------|
| `success` | bool | Did cleaner complete without errors? |
| `modified` | bool | Did cleaner change the record? |
| `before_value` | Any | Value before cleaning (for audit trail) |
| `after_value` | Any | Value after cleaning (for audit trail) |
| `error` | str | Error message (only if `success=False`) |

**Guidelines:**
- ✅ `success=True, modified=True` - Cleaned successfully
- ✅ `success=True, modified=False` - No change needed (already clean, NULL value)
- ❌ `success=False, modified=False` - Cleaning failed (invalid data, error occurred)
- Always return CleanerResult (never `None` or raise exception)

---

## Real-World Examples

### Example 1: Credit Card Validation

Clean and validate credit card numbers using Luhn algorithm:

```python
@cleaner(name='validate_credit_card')
def validate_credit_card_cleaner(field_name: str, mask: bool = False):
    """
    Validate credit card using Luhn algorithm.

    Args:
        field_name: Field to clean
        mask: If True, mask all but last 4 digits
    """
    def cleaner_func(record, context):
        value = getattr(record, field_name) if hasattr(record, field_name) else record.get(field_name)

        if value is None:
            return CleanerResult(success=True, modified=False)

        # Remove spaces and dashes
        digits = re.sub(r'[^0-9]', '', str(value))

        # Validate using Luhn algorithm
        def luhn_check(card_number):
            digits = [int(d) for d in str(card_number)]
            checksum = 0
            for i, d in enumerate(reversed(digits)):
                if i % 2 == 1:
                    d *= 2
                    if d > 9:
                        d -= 9
                checksum += d
            return checksum % 10 == 0

        if not luhn_check(digits):
            return CleanerResult(
                success=False,
                modified=False,
                error='Invalid credit card number (Luhn check failed)'
            )

        # Optionally mask
        if mask:
            masked = '*' * (len(digits) - 4) + digits[-4:]
            if hasattr(record, field_name):
                setattr(record, field_name, masked)
            else:
                record[field_name] = masked
            return CleanerResult(
                success=True,
                modified=True,
                before_value=value,
                after_value=masked
            )

        return CleanerResult(success=True, modified=False)

    return cleaner_func

# Usage
cleaner = validate_credit_card_cleaner('card_number', mask=True)
record = {'card_number': '4532-1488-0343-6467'}
result = cleaner(record, {})

print(record['card_number'])  # '************6467'
print(result.success)         # True
```

### Example 2: Address Validation via External API

Validate and standardize addresses using external API:

```python
import requests

@cleaner(name='validate_address')
def validate_address_cleaner(
    street_field: str,
    city_field: str,
    state_field: str,
    zip_field: str,
    api_key: str
):
    """
    Validate address via USPS API and standardize format.

    Requires USPS API key.
    """
    def cleaner_func(record, context):
        # Extract address components
        street = getattr(record, street_field) if hasattr(record, street_field) else record.get(street_field)
        city = getattr(record, city_field) if hasattr(record, city_field) else record.get(city_field)
        state = getattr(record, state_field) if hasattr(record, state_field) else record.get(state_field)
        zip_code = getattr(record, zip_field) if hasattr(record, zip_field) else record.get(zip_field)

        if not all([street, city, state, zip_code]):
            return CleanerResult(success=True, modified=False)

        try:
            # Call USPS API (mock example)
            response = requests.post(
                'https://secure.shippingapis.com/ShippingAPI.dll',
                params={'API': 'Verify', 'XML': f'<AddressValidateRequest>...</AddressValidateRequest>'},
                timeout=5
            )

            # Parse response (simplified)
            if response.status_code == 200:
                # Extract standardized address from response
                standardized = parse_usps_response(response.text)

                # Update fields
                modified = False
                if hasattr(record, street_field):
                    if getattr(record, street_field) != standardized['street']:
                        setattr(record, street_field, standardized['street'])
                        modified = True
                else:
                    if record[street_field] != standardized['street']:
                        record[street_field] = standardized['street']
                        modified = True

                # Similar for city, state, zip...

                return CleanerResult(
                    success=True,
                    modified=modified,
                    before_value=f"{street}, {city}, {state} {zip_code}",
                    after_value=f"{standardized['street']}, {standardized['city']}, {standardized['state']} {standardized['zip']}"
                )
            else:
                return CleanerResult(
                    success=False,
                    modified=False,
                    error=f'Address validation failed: {response.status_code}'
                )

        except requests.Timeout:
            return CleanerResult(
                success=False,
                modified=False,
                error='Address validation timed out'
            )
        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                error=f'Address validation error: {str(e)}'
            )

    return cleaner_func
```

### Example 3: Multi-Field Cleaner

Clean multiple related fields together:

```python
@cleaner(name='normalize_name')
def normalize_name_cleaner(first_name_field: str, last_name_field: str):
    """
    Normalize first and last name fields.

    - Trim whitespace
    - Title case
    - Handle suffixes (Jr., Sr., III)
    """
    def cleaner_func(record, context):
        first = getattr(record, first_name_field) if hasattr(record, first_name_field) else record.get(first_name_field)
        last = getattr(record, last_name_field) if hasattr(record, last_name_field) else record.get(last_name_field)

        if not first and not last:
            return CleanerResult(success=True, modified=False)

        modified = False

        # Clean first name
        if first:
            cleaned_first = first.strip().title()
            if first != cleaned_first:
                if hasattr(record, first_name_field):
                    setattr(record, first_name_field, cleaned_first)
                else:
                    record[first_name_field] = cleaned_first
                modified = True

        # Clean last name (handle suffixes)
        if last:
            # Remove common suffixes for normalization
            suffixes = ['Jr.', 'Sr.', 'III', 'II', 'IV']
            cleaned_last = last.strip().title()

            if last != cleaned_last:
                if hasattr(record, last_name_field):
                    setattr(record, last_name_field, cleaned_last)
                else:
                    record[last_name_field] = cleaned_last
                modified = True

        return CleanerResult(
            success=True,
            modified=modified,
            before_value=f"{first} {last}",
            after_value=f"{cleaned_first} {cleaned_last}"
        )

    return cleaner_func

# Usage
cleaner = normalize_name_cleaner('first_name', 'last_name')
record = {'first_name': '  john  ', 'last_name': '  DOE jr.  '}
result = cleaner(record, {})

print(record['first_name'])  # 'John'
print(record['last_name'])   # 'Doe Jr.'
```

---

## Context Usage

The `context` dict provides metadata about the cleaning operation:

```python
@cleaner
def context_aware_cleaner(field_name: str):
    def cleaner_func(record, context):
        # Access metadata
        print(f"Field: {context.get('field_name')}")
        print(f"Expectation: {context.get('expectation')}")
        print(f"Validation: {context.get('validation_result')}")

        # Access chain metadata (if part of CleanerChain)
        chain_info = context.get('cleaner_chain')
        if chain_info:
            print(f"Step {chain_info['current_step']} of {chain_info['total_steps']}")
            print(f"Cleaners: {chain_info['cleaner_names']}")

        # Access previous result (if part of chain)
        prev_result = context.get('previous_result')
        if prev_result:
            print(f"Previous cleaner modified: {prev_result.modified}")

        # Your cleaning logic here
        return CleanerResult(success=True, modified=False)

    return cleaner_func
```

**Available Context Keys:**

| Key | Type | Description |
|-----|------|-------------|
| `field_name` | str | Name of field being cleaned |
| `expectation` | ExpectationNode | DQL expectation that failed |
| `validation_result` | ValidationResult | Validation result |
| `cleaner_chain` | dict | Chain metadata (if in chain) |
| `previous_result` | CleanerResult | Previous cleaner result (if in chain) |
| `transaction_id` | str | Transaction ID (if using SafeCleanerExecutor) |

---

## Auto-Discovery

Automatically discover and register cleaners from a directory:

### Project Structure

```
my_app/
├── custom_cleaners/
│   ├── __init__.py
│   ├── domain_cleaners.py
│   ├── business_rules.py
│   └── api_cleaners.py
└── app.py
```

### Define Cleaners

```python
# my_app/custom_cleaners/domain_cleaners.py

from dql_core import cleaner, CleanerResult

@cleaner
def normalize_ssn(field_name: str):
    """Normalize SSN"""
    # Implementation...
    pass

@cleaner(name='validate_ein')
def check_ein(field_name: str):
    """Validate Employer Identification Number"""
    # Implementation...
    pass
```

### Register at Startup

```python
# my_app/app.py

from dql_core import discover_cleaners

# Discover all @cleaner decorated functions
discovered = discover_cleaners('my_app/custom_cleaners/')
print(f"Registered {len(discovered)} cleaners: {discovered}")

# Now use them
from dql_core import get_cleaner

ssn_cleaner = get_cleaner('normalize_ssn')
```

---

## Testing Custom Cleaners

### Unit Testing Pattern

```python
# tests/test_custom_cleaners.py

import pytest
from dql_core import CleanerResult
from my_app.custom_cleaners import normalize_ssn_cleaner

def test_normalize_ssn_valid():
    """Test SSN normalization with valid input"""
    record = {'ssn': '123456789'}
    cleaner = normalize_ssn_cleaner('ssn')
    result = cleaner(record, {})

    assert result.success is True
    assert result.modified is True
    assert record['ssn'] == '123-45-6789'
    assert result.before_value == '123456789'
    assert result.after_value == '123-45-6789'

def test_normalize_ssn_already_formatted():
    """Test SSN that's already formatted"""
    record = {'ssn': '123-45-6789'}
    cleaner = normalize_ssn_cleaner('ssn')
    result = cleaner(record, {})

    assert result.success is True
    assert result.modified is False  # No change needed
    assert record['ssn'] == '123-45-6789'

def test_normalize_ssn_invalid_length():
    """Test SSN with invalid length"""
    record = {'ssn': '123'}
    cleaner = normalize_ssn_cleaner('ssn')
    result = cleaner(record, {})

    assert result.success is False
    assert result.modified is False
    assert 'must be 9 digits' in result.error

def test_normalize_ssn_null():
    """Test NULL SSN handling"""
    record = {'ssn': None}
    cleaner = normalize_ssn_cleaner('ssn')
    result = cleaner(record, {})

    assert result.success is True
    assert result.modified is False
    assert record['ssn'] is None  # NULL preserved

def test_normalize_ssn_with_formatting():
    """Test SSN with various formatting"""
    test_cases = [
        ('123-45-6789', '123-45-6789'),
        ('123.45.6789', '123-45-6789'),
        ('123 45 6789', '123-45-6789'),
        ('(123)45-6789', '123-45-6789'),
    ]

    for input_val, expected in test_cases:
        record = {'ssn': input_val}
        cleaner = normalize_ssn_cleaner('ssn')
        result = cleaner(record, {})

        assert result.success is True
        assert record['ssn'] == expected
```

### Integration Testing

```python
def test_cleaner_with_django_model():
    """Test custom cleaner with Django model"""
    from myapp.models import Customer

    customer = Customer.objects.create(
        ssn='123456789',
        email='  [email protected]  '
    )

    # Apply cleaner
    cleaner = normalize_ssn_cleaner('ssn')
    result = cleaner(customer, {})

    assert result.success is True
    assert customer.ssn == '123-45-6789'

    # Save and verify
    customer.save()
    customer.refresh_from_db()
    assert customer.ssn == '123-45-6789'
```

---

## Best Practices

### ✅ DO

1. **Always handle NULL values**
   ```python
   if value is None:
       return CleanerResult(success=True, modified=False)
   ```

2. **Return CleanerResult, never raise exceptions**
   ```python
   try:
       # Cleaning logic
       return CleanerResult(success=True, modified=True)
   except Exception as e:
       return CleanerResult(success=False, error=str(e))
   ```

3. **Set modified=True only when record changes**
   ```python
   if value != new_value:
       # Apply change
       return CleanerResult(success=True, modified=True)
   else:
       return CleanerResult(success=True, modified=False)
   ```

4. **Include before/after values for audit trail**
   ```python
   return CleanerResult(
       success=True,
       modified=True,
       before_value=old_value,
       after_value=new_value
   )
   ```

5. **Use descriptive error messages**
   ```python
   return CleanerResult(
       success=False,
       error=f"SSN must be 9 digits, got {len(digits)}"
   )
   ```

### ❌ DON'T

1. **Don't raise exceptions** (return error result instead)
2. **Don't modify record on error** (keep original value)
3. **Don't assume field exists** (check with `hasattr()` or `.get()`)
4. **Don't ignore NULL values** (handle them explicitly)
5. **Don't make database queries in cleaners** (prefetch data first)

---

## Advanced Topics

### Parameterized Cleaners

Create flexible cleaners with configuration options:

```python
@cleaner
def truncate_string(field_name: str, max_length: int = 100, suffix: str = '...'):
    """Truncate string to maximum length"""
    def cleaner_func(record, context):
        value = getattr(record, field_name) if hasattr(record, field_name) else record.get(field_name)

        if not value or len(value) <= max_length:
            return CleanerResult(success=True, modified=False)

        truncated = value[:max_length - len(suffix)] + suffix

        if hasattr(record, field_name):
            setattr(record, field_name, truncated)
        else:
            record[field_name] = truncated

        return CleanerResult(
            success=True,
            modified=True,
            before_value=value,
            after_value=truncated
        )

    return cleaner_func

# Usage with different parameters
cleaner1 = truncate_string('description', max_length=50)
cleaner2 = truncate_string('bio', max_length=200, suffix='...')
```

### Conditional Cleaning

Apply different logic based on conditions:

```python
@cleaner
def conditional_format(field_name: str):
    """Format phone or email based on content"""
    def cleaner_func(record, context):
        value = getattr(record, field_name) if hasattr(record, field_name) else record.get(field_name)

        if not value:
            return CleanerResult(success=True, modified=False)

        # Detect type and clean accordingly
        if '@' in value:
            # Email
            cleaned = value.strip().lower()
        elif any(char.isdigit() for char in value):
            # Phone
            cleaned = re.sub(r'[^0-9]', '', value)
        else:
            # Unknown, just trim
            cleaned = value.strip()

        if hasattr(record, field_name):
            setattr(record, field_name, cleaned)
        else:
            record[field_name] = cleaned

        return CleanerResult(
            success=True,
            modified=(value != cleaned),
            before_value=value,
            after_value=cleaned
        )

    return cleaner_func
```

---

## Next Steps

- **[Cleaner Catalog](cleaner-catalog.md)** - Explore built-in cleaners
- **[Best Practices](cleaner-best-practices.md)** - Performance and security tips
- **[Troubleshooting](troubleshooting.md)** - Debug common issues
- **[Tutorial](tutorial.md)** - Hands-on learning
