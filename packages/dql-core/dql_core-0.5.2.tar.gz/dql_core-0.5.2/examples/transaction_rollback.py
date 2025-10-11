#!/usr/bin/env python3
"""
Transaction Rollback Example

Demonstrates transaction safety with automatic rollback on failure.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dql_core.cleaners.string_cleaners import trim_whitespace, lowercase
from dql_core.cleaners.transaction import SafeCleanerExecutor, DictTransactionManager
from dql_core.cleaners.audit import AuditLogger
from dql_core.results import CleanerResult


def failing_cleaner(field_name: str):
    """A cleaner that always fails (for demonstration)"""
    def cleaner_func(record, context):
        return CleanerResult(
            success=False,
            modified=False,
            error="Simulated validation failure"
        )
    return cleaner_func


def example_1_successful_transaction():
    """Example 1: Successful transaction commits"""
    print("=== Example 1: Successful Transaction ===\n")

    manager = DictTransactionManager()
    executor = SafeCleanerExecutor(manager)

    record = {'email': '  [email protected]  '}
    print(f"Original: '{record['email']}'")

    cleaners = [
        trim_whitespace('email'),
        lowercase('email')
    ]

    result = executor.execute_cleaners(cleaners, record, {})

    print(f"Cleaned:  '{record['email']}'")
    print(f"Success:  {result.success}")
    print(f"Modified: {result.modified}")
    print(f"Transaction: Committed ✓\n")


def example_2_failed_transaction():
    """Example 2: Failed transaction rolls back"""
    print("=== Example 2: Failed Transaction (Rollback) ===\n")

    manager = DictTransactionManager()
    executor = SafeCleanerExecutor(manager)

    record = {'email': '  [email protected]  '}
    original_email = record['email']
    print(f"Original: '{record['email']}'")

    # Cleaners: first succeeds, second fails
    cleaners = [
        trim_whitespace('email'),    # This succeeds
        failing_cleaner('email'),    # This fails
        lowercase('email')           # This won't execute
    ]

    result = executor.execute_cleaners(cleaners, record, {})

    print(f"After:    '{record['email']}'")
    print(f"Success:  {result.success}")
    print(f"Error:    {result.error}")
    print(f"Rolled back: {record['email'] == original_email} ✓\n")


def example_3_dry_run_mode():
    """Example 3: Dry-run mode (preview changes)"""
    print("=== Example 3: Dry-Run Mode ===\n")

    manager = DictTransactionManager()
    executor = SafeCleanerExecutor(manager)

    record = {'email': '  [email protected]  '}
    original_email = record['email']

    cleaners = [trim_whitespace('email'), lowercase('email')]

    print(f"Original: '{record['email']}'")

    # Preview changes without committing
    result = executor.preview_changes(cleaners, record, {})

    print(f"Would change to: '{result.after_value}'")
    print(f"Would modify: {result.modified}")
    print(f"Original unchanged: '{record['email']}'")
    print(f"Still original: {record['email'] == original_email} ✓\n")


def example_4_audit_logging():
    """Example 4: Audit logging"""
    print("=== Example 4: Audit Logging ===\n")

    manager = DictTransactionManager()
    audit_logger = AuditLogger(backend='memory')
    executor = SafeCleanerExecutor(manager, audit_logger)

    records = [
        {'id': 1, 'email': '  [email protected]  '},
        {'id': 2, 'email': '  [email protected]  '},
        {'id': 3, 'email': '  [email protected]  '},
    ]

    cleaners = [trim_whitespace('email'), lowercase('email')]

    print("Cleaning records with audit logging...\n")
    for record in records:
        result = executor.execute_cleaners(cleaners, record, {})
        print(f"✓ Cleaned record {record['id']}: '{record['email']}'")

    # Review audit logs
    print("\n=== Audit Log ===")
    logs = audit_logger.get_logs()
    print(f"Total entries: {len(logs)}\n")

    for i, log in enumerate(logs[:3], 1):  # Show first 3
        print(f"Entry {i}:")
        print(f"  Transaction ID: {log.transaction_id}")
        print(f"  Cleaners: {log.cleaner_names}")
        print(f"  Record ID: {log.record_id}")
        print(f"  Changed: '{log.before_value}' → '{log.after_value}'")
        print()


def example_5_bulk_with_error_handling():
    """Example 5: Bulk processing with error handling"""
    print("=== Example 5: Bulk Processing ===\n")

    manager = DictTransactionManager()
    executor = SafeCleanerExecutor(manager)

    # Mix of valid and invalid records
    records = [
        {'id': 1, 'email': '  [email protected]  ', 'valid': True},
        {'id': 2, 'email': '  [email protected]  ', 'valid': True},
        {'id': 3, 'email': '  invalid  ', 'valid': False},  # Will fail validation
        {'id': 4, 'email': '  [email protected]  ', 'valid': True},
    ]

    def validate_email(field_name: str):
        """Custom validator that checks email format"""
        def cleaner_func(record, context):
            value = record.get(field_name)
            if not value or '@' not in value:
                return CleanerResult(
                    success=False,
                    modified=False,
                    error="Invalid email format: missing @"
                )
            return CleanerResult(success=True, modified=False)
        return cleaner_func

    cleaners = [
        trim_whitespace('email'),
        lowercase('email'),
        validate_email('email')  # Custom validator
    ]

    success_count = 0
    failure_count = 0

    for record in records:
        original_email = record['email']
        result = executor.execute_cleaners(cleaners, record, {})

        if result.success:
            success_count += 1
            print(f"✓ Record {record['id']}: '{original_email.strip()}' → '{record['email']}'")
        else:
            failure_count += 1
            print(f"✗ Record {record['id']}: Failed - {result.error}")
            # Email rolled back to original
            assert record['email'] == original_email

    print(f"\n=== Summary ===")
    print(f"Success: {success_count}/{len(records)}")
    print(f"Failures: {failure_count}/{len(records)}")
    print()


def example_6_nested_transactions():
    """Example 6: Using savepoints"""
    print("=== Example 6: Savepoints ===\n")

    manager = DictTransactionManager()

    record = {'email': '  [email protected]  '}
    print(f"Original: '{record['email']}'")

    # Manual transaction with savepoints
    manager.begin()

    try:
        # Apply first cleaner
        cleaner1 = trim_whitespace('email')
        cleaner1(record, {})
        print(f"After trim: '{record['email']}'")

        # Create savepoint
        manager.savepoint('sp1')

        # Apply second cleaner
        cleaner2 = lowercase('email')
        cleaner2(record, {})
        print(f"After lowercase: '{record['email']}'")

        # Commit
        manager.commit()
        print(f"Transaction: Committed ✓\n")

    except Exception as e:
        manager.rollback()
        print(f"Transaction: Rolled back ✗")
        print(f"Error: {e}\n")


def main():
    """Run all examples"""
    print("Transaction Rollback Examples")
    print("=" * 50 + "\n")

    example_1_successful_transaction()
    example_2_failed_transaction()
    example_3_dry_run_mode()
    example_4_audit_logging()
    example_5_bulk_with_error_handling()
    example_6_nested_transactions()

    print("✅ All examples completed successfully!")


if __name__ == '__main__':
    main()
