# Cleaner Catalog

Complete reference for all built-in cleaners in dql-core.

## Overview

dql-core provides 8 built-in cleaners for common data quality issues:

- **4 String Cleaners** - Text normalization and formatting
- **4 Data Type Cleaners** - Type coercion, NULL handling, formatting

## Quick Reference

| Cleaner | Category | Purpose | Example Input | Example Output |
|---------|----------|---------|---------------|----------------|
| `trim_whitespace` | String | Remove leading/trailing whitespace | `"  hello  "` | `"hello"` |
| `uppercase` | String | Convert to uppercase | `"hello"` | `"HELLO"` |
| `lowercase` | String | Convert to lowercase | `"HELLO"` | `"hello"` |
| `normalize_email` | String | Trim and lowercase emails | `"  [email protected]  "` | `"[email protected]"` |
| `strip_non_numeric` | Data Type | Remove non-numeric characters | `"(555) 555-5555"` | `"5555555555"` |
| `normalize_phone` | Data Type | Format phone numbers | `"555-555-5555"` | `"+15555555555"` |
| `coalesce` | Data Type | Replace NULL with default | `None` | `"pending"` |
| `format_date` | Data Type | Convert date formats | `"2025-01-15"` | `"01/15/2025"` |

---

## String Cleaners

### trim_whitespace

**Purpose:** Remove leading and trailing whitespace from string fields.

**Signature:**
```python
trim_whitespace(field_name: str) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import trim_whitespace

# Clean a description field
record = {'description': '  Hello World  '}
cleaner = trim_whitespace('description')
result = cleaner(record, {})

print(record['description'])  # 'Hello World'
print(result.modified)        # True
print(result.before_value)    # '  Hello World  '
print(result.after_value)     # 'Hello World'
```

**When to use:**
- User input with accidental whitespace
- Data imported from CSV with padding
- Text fields requiring exact matching
- Pre-processing before validation

**NULL Handling:** Skips NULL values (no modification)

**Performance:** <0.01ms per record

**Edge Cases:**
- Empty strings remain empty: `""` → `""`
- Whitespace-only strings become empty: `"   "` → `""`
- Internal whitespace preserved: `"hello  world"` → `"hello  world"`

---

### uppercase

**Purpose:** Convert string fields to uppercase.

**Signature:**
```python
uppercase(field_name: str) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import uppercase

# Convert name to uppercase
record = {'name': 'john doe'}
cleaner = uppercase('name')
result = cleaner(record, {})

print(record['name'])       # 'JOHN DOE'
print(result.modified)      # True
```

**When to use:**
- Standardizing codes (state codes, country codes)
- Normalizing identifiers
- Case-insensitive comparisons
- Display formatting requirements

**NULL Handling:** Skips NULL values

**Performance:** <0.01ms per record

**Edge Cases:**
- Already uppercase strings: no change, `modified=False`
- Mixed case: `"Hello World"` → `"HELLO WORLD"`
- Special characters unchanged: `"hello123!@#"` → `"HELLO123!@#"`

---

### lowercase

**Purpose:** Convert string fields to lowercase.

**Signature:**
```python
lowercase(field_name: str) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import lowercase

# Convert email to lowercase
record = {'email': '[email protected]'}
cleaner = lowercase('email')
result = cleaner(record, {})

print(record['email'])      # '[email protected]'
print(result.modified)      # True
```

**When to use:**
- Email normalization
- Username normalization
- Case-insensitive lookups
- Consistent text formatting

**NULL Handling:** Skips NULL values

**Performance:** <0.01ms per record

**Edge Cases:**
- Already lowercase strings: no change, `modified=False`
- Mixed case: `"Hello World"` → `"hello world"`
- Numbers and symbols unchanged: `"HELLO123"` → `"hello123"`

---

### normalize_email

**Purpose:** Normalize email addresses by trimming whitespace and converting to lowercase.

**Signature:**
```python
normalize_email(field_name: str) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import normalize_email

# Normalize email address
record = {'email': '  [email protected]  '}
cleaner = normalize_email('email')
result = cleaner(record, {})

print(record['email'])      # '[email protected]'
print(result.modified)      # True
```

**When to use:**
- User registration forms
- Email validation workflows
- Deduplication of email addresses
- Before email sending

**NULL Handling:** Skips NULL values

**Performance:** <0.01ms per record

**Combination:**
This cleaner combines two operations:
1. `trim_whitespace` - Remove leading/trailing spaces
2. `lowercase` - Convert to lowercase

**Edge Cases:**
- Mixed formatting: `"  [email protected]  "` → `"[email protected]"`
- Already normalized: no change, `modified=False`
- Multiple spaces: `"  user @  example.com  "` → `"user @  example.com"` (internal spaces preserved)

---

## Data Type Cleaners

### strip_non_numeric

**Purpose:** Remove all non-numeric characters from a field, leaving only digits.

**Signature:**
```python
strip_non_numeric(field_name: str) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import strip_non_numeric

# Clean phone number formatting
record = {'phone': '(555) 555-5555'}
cleaner = strip_non_numeric('phone')
result = cleaner(record, {})

print(record['phone'])      # '5555555555'
print(result.modified)      # True
```

**When to use:**
- Cleaning phone numbers before validation
- Extracting numeric data from formatted strings
- Removing currency symbols
- Pre-processing numeric identifiers

**NULL Handling:** Skips NULL values

**Performance:** <0.01ms per record

**More Examples:**

```python
# Currency values
record = {'amount': '$1,234.56'}
cleaner = strip_non_numeric('amount')
result = cleaner(record, {})
print(record['amount'])     # '123456' (decimal point removed!)

# Social Security Numbers
record = {'ssn': '123-45-6789'}
cleaner = strip_non_numeric('ssn')
result = cleaner(record, {})
print(record['ssn'])        # '123456789'

# Zip codes
record = {'zip': '12345-6789'}
cleaner = strip_non_numeric('zip')
result = cleaner(record, {})
print(record['zip'])        # '123456789'
```

**Important Notes:**
- Removes **all** non-digit characters including decimal points
- Use `normalize_phone` for proper phone formatting
- For currency, consider preserving decimal points with custom cleaner

---

### normalize_phone

**Purpose:** Format phone numbers to standard formats (E164, US, digits only).

**Signature:**
```python
normalize_phone(field_name: str, format: str = 'E164') -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean
- `format` (str): Output format - `'E164'`, `'US'`, or `'digits_only'` (default: `'E164'`)

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import normalize_phone

# E164 format (international standard)
record = {'phone': '(555) 555-5555'}
cleaner = normalize_phone('phone', format='E164')
result = cleaner(record, {})
print(record['phone'])      # '+15555555555'

# US format (pretty formatting)
record = {'phone': '5555555555'}
cleaner = normalize_phone('phone', format='US')
result = cleaner(record, {})
print(record['phone'])      # '(555) 555-5555'

# Digits only (no formatting)
record = {'phone': '+1-555-555-5555'}
cleaner = normalize_phone('phone', format='digits_only')
result = cleaner(record, {})
print(record['phone'])      # '5555555555'
```

**Format Options:**

| Format | Output Example | Use Case |
|--------|---------------|----------|
| `E164` | `+15555555555` | International, API integration, database storage |
| `US` | `(555) 555-5555` | Display formatting for US numbers |
| `digits_only` | `5555555555` | Simple validation, legacy systems |

**When to use:**
- Normalizing phone numbers for storage
- Formatting for display
- Before phone validation
- API integration (use E164)

**NULL Handling:** Skips NULL values

**Performance:** <0.05ms per record

**Input Formats Accepted:**
- `"(555) 555-5555"` - US formatted
- `"555-555-5555"` - Dashed
- `"5555555555"` - Digits only
- `"+1 555 555 5555"` - E164 with spaces
- `"1-555-555-5555"` - Country code with dashes

**Limitations:**
- Currently assumes US country code (+1)
- Does not validate if number is real/valid
- Does not handle international numbers (future enhancement)

---

### coalesce

**Purpose:** Replace NULL/None values with a default value.

**Signature:**
```python
coalesce(field_name: str, default_value: Any) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean
- `default_value` (Any): Value to use if field is NULL

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import coalesce

# Replace NULL status with default
record = {'status': None}
cleaner = coalesce('status', default_value='pending')
result = cleaner(record, {})

print(record['status'])     # 'pending'
print(result.modified)      # True

# Non-NULL values are unchanged
record = {'status': 'active'}
result = cleaner(record, {})
print(record['status'])     # 'active'
print(result.modified)      # False
```

**When to use:**
- Setting default values for optional fields
- Handling missing data
- Ensuring non-NULL constraints
- Data migration with incomplete records

**NULL Handling:** This cleaner **handles** NULL values (that's its purpose!)

**Performance:** <0.01ms per record

**More Examples:**

```python
# Default numeric values
record = {'count': None}
cleaner = coalesce('count', default_value=0)
result = cleaner(record, {})
print(record['count'])      # 0

# Default boolean values
record = {'is_active': None}
cleaner = coalesce('is_active', default_value=True)
result = cleaner(record, {})
print(record['is_active'])  # True

# Default empty list
record = {'tags': None}
cleaner = coalesce('tags', default_value=[])
result = cleaner(record, {})
print(record['tags'])       # []
```

**Edge Cases:**
- Empty string is NOT NULL: `""` → `""` (no change)
- Zero is NOT NULL: `0` → `0` (no change)
- False is NOT NULL: `False` → `False` (no change)
- Only `None` is considered NULL

---

### format_date

**Purpose:** Convert date strings or date objects between different format patterns.

**Signature:**
```python
format_date(
    field_name: str,
    input_format: str = '%Y-%m-%d',
    output_format: str = '%m/%d/%Y'
) -> Callable
```

**Parameters:**
- `field_name` (str): Name of the field to clean
- `input_format` (str): strptime format of input date (default: ISO format `'%Y-%m-%d'`)
- `output_format` (str): strftime format for output (default: US format `'%m/%d/%Y'`)

**Returns:** Cleaner function that returns CleanerResult

**Example:**

```python
from dql_core import format_date

# Convert ISO to US format
record = {'created_at': '2025-01-15'}
cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
result = cleaner(record, {})

print(record['created_at'])  # '01/15/2025'
print(result.modified)       # True
```

**Common Format Patterns:**

| Format Code | Description | Example |
|------------|-------------|---------|
| `%Y` | 4-digit year | 2025 |
| `%y` | 2-digit year | 25 |
| `%m` | Month (01-12) | 01 |
| `%d` | Day (01-31) | 15 |
| `%B` | Full month name | January |
| `%b` | Abbreviated month | Jan |
| `%A` | Full weekday | Wednesday |
| `%H` | Hour (00-23) | 14 |
| `%M` | Minute (00-59) | 30 |
| `%S` | Second (00-59) | 45 |

**More Examples:**

```python
# Convert US to ISO format
record = {'date': '01/15/2025'}
cleaner = format_date('date', input_format='%m/%d/%Y', output_format='%Y-%m-%d')
result = cleaner(record, {})
print(record['date'])       # '2025-01-15'

# Format with month names
record = {'date': '2025-01-15'}
cleaner = format_date('date', input_format='%Y-%m-%d', output_format='%B %d, %Y')
result = cleaner(record, {})
print(record['date'])       # 'January 15, 2025'

# Include time
record = {'timestamp': '2025-01-15 14:30:00'}
cleaner = format_date(
    'timestamp',
    input_format='%Y-%m-%d %H:%M:%S',
    output_format='%m/%d/%Y %I:%M %p'
)
result = cleaner(record, {})
print(record['timestamp'])  # '01/15/2025 02:30 PM'

# Works with date/datetime objects
from datetime import date
record = {'created': date(2025, 1, 15)}
cleaner = format_date('created', output_format='%Y-%m-%d')
result = cleaner(record, {})
print(record['created'])    # '2025-01-15'
```

**When to use:**
- Standardizing date formats from external sources
- Converting between ISO and regional formats
- Display formatting
- Before date validation

**NULL Handling:** Skips NULL values

**Performance:** <0.1ms per record

**Error Handling:**
- Returns `CleanerResult(success=False, error=...)` if:
  - Input string doesn't match `input_format`
  - Invalid date values (e.g., '13/45/2025')
  - Field contains non-date value

---

## Comparison Table

### By Use Case

| Use Case | Recommended Cleaner(s) | Example |
|----------|----------------------|---------|
| Email normalization | `normalize_email` | `"  [email protected]  "` → `"[email protected]"` |
| Phone storage | `normalize_phone(format='E164')` | `"(555) 555-5555"` → `"+15555555555"` |
| Phone display | `normalize_phone(format='US')` | `"5555555555"` → `"(555) 555-5555"` |
| Name formatting | `trim_whitespace` + `uppercase`/`lowercase` | Chain both |
| NULL handling | `coalesce` | `None` → `"default"` |
| Date standardization | `format_date` | `"01/15/2025"` → `"2025-01-15"` |
| Extract digits | `strip_non_numeric` | `"(555) 555-5555"` → `"5555555555"` |

### By Performance

| Cleaner | Avg Time | Suitable for Bulk Operations |
|---------|----------|----------------------------|
| `trim_whitespace` | <0.01ms | ✅ Excellent |
| `uppercase` | <0.01ms | ✅ Excellent |
| `lowercase` | <0.01ms | ✅ Excellent |
| `normalize_email` | <0.01ms | ✅ Excellent |
| `strip_non_numeric` | <0.01ms | ✅ Excellent |
| `coalesce` | <0.01ms | ✅ Excellent |
| `normalize_phone` | <0.05ms | ✅ Good |
| `format_date` | <0.1ms | ⚠️ Moderate |

---

## Chaining Built-in Cleaners

Most data quality workflows require multiple cleaners in sequence. Use `CleanerChain`:

```python
from dql_core import CleanerChain

# Email normalization workflow
email_chain = (CleanerChain()
    .add('trim_whitespace', 'email')
    .add('lowercase', 'email')
    .add('normalize_email', 'email'))

record = {'email': '  [email protected]  '}
result = email_chain.execute(record, {})
print(record['email'])  # '[email protected]'
```

**See:** [Cleaner Guide - Chaining Section](cleaner-guide.md#chaining-cleaners-story-26) for more details.

---

## Next Steps

- **[Custom Cleaners Guide](custom-cleaners-guide.md)** - Build your own cleaners
- **[Cleaner Chaining](cleaner-guide.md#chaining-cleaners-story-26)** - Combine multiple cleaners
- **[Transaction Safety](cleaner-guide.md#transaction-safety-story-27)** - Rollback on failure
- **[Best Practices](cleaner-best-practices.md)** - Performance and security tips
- **[Troubleshooting](troubleshooting.md)** - Common issues and solutions
