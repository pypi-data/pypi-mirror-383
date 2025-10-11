# Cleaner Examples

Runnable examples demonstrating dql-core cleaner functionality.

## Examples

### 1. email_normalization.py

Demonstrates email normalization with single cleaners and chains.

**Run:**
```bash
python examples/email_normalization.py
```

**Topics:**
- Single cleaner usage
- Chained cleaners
- Bulk processing
- Error handling for NULL values

### 2. custom_cleaner.py

Shows how to create custom cleaners for domain-specific rules.

**Run:**
```bash
python examples/custom_cleaner.py
```

**Topics:**
- SSN normalization
- Special character removal
- String truncation
- Chaining custom cleaners

### 3. transaction_rollback.py

Demonstrates transaction safety with automatic rollback.

**Run:**
```bash
python examples/transaction_rollback.py
```

**Topics:**
- Successful transactions
- Rollback on failure
- Dry-run mode (preview changes)
- Audit logging
- Bulk processing with error handling
- Savepoints

## Running All Examples

```bash
# Run individual examples
python examples/email_normalization.py
python examples/custom_cleaner.py
python examples/transaction_rollback.py

# Or run all at once
for file in examples/*.py; do
    [ "$(basename "$file")" != "__init__.py" ] && python "$file"
done
```

## Expected Output

Each example prints:
- Input data
- Applied cleaners
- Output data
- Success/failure status
- Performance metrics (where applicable)

## Prerequisites

Make sure dql-core is installed:

```bash
pip install -e .
```

Or from the dql-core directory:

```bash
pip install -e ../dql-core
```

## More Resources

- **[Tutorial](../docs/tutorial.md)** - Step-by-step learning
- **[Cleaner Catalog](../docs/cleaner-catalog.md)** - All built-in cleaners
- **[Custom Cleaners Guide](../docs/custom-cleaners-guide.md)** - Build your own
- **[Best Practices](../docs/cleaner-best-practices.md)** - Performance and security
