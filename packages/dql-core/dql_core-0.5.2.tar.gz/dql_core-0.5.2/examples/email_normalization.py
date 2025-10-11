#!/usr/bin/env python3
"""
Email Normalization Example

Demonstrates how to normalize email addresses using cleaners.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dql_core.cleaners.string_cleaners import trim_whitespace, lowercase, normalize_email
from dql_core.cleaners.chain import CleanerChain


def example_1_single_cleaner():
    """Example 1: Using a single cleaner"""
    print("=== Example 1: Single Cleaner ===\n")

    record = {'email': '  [email protected]  '}
    print(f"Original: '{record['email']}'")

    # Apply single cleaner
    cleaner = normalize_email('email')
    result = cleaner(record, {})

    print(f"Cleaned:  '{record['email']}'")
    print(f"Modified: {result.modified}")
    print(f"Success:  {result.success}\n")


def example_2_chained_cleaners():
    """Example 2: Chaining multiple cleaners"""
    print("=== Example 2: Chained Cleaners ===\n")

    records = [
        {'email': '  [email protected]  '},
        {'email': '[email protected]'},
        {'email': '  MIXED case  '},
    ]

    # Create cleaner chain
    chain = (CleanerChain()
        .add('trim_whitespace', 'email')
        .add('lowercase', 'email')
        .add('normalize_email', 'email'))

    print("Original emails:")
    for i, record in enumerate(records, 1):
        print(f"  {i}. '{record['email']}'")

    # Apply chain to all records
    for record in records:
        chain.execute(record, {})

    print("\nCleaned emails:")
    for i, record in enumerate(records, 1):
        print(f"  {i}. '{record['email']}'")
    print()


def example_3_bulk_processing():
    """Example 3: Bulk processing with error handling"""
    print("=== Example 3: Bulk Processing ===\n")

    # Simulate customer records
    customers = [
        {'id': 1, 'email': '  [email protected]  '},
        {'id': 2, 'email': '[email protected]'},
        {'id': 3, 'email': '  [email protected]  '},
        {'id': 4, 'email': None},  # NULL email
        {'id': 5, 'email': '  '},  # Empty email
    ]

    cleaner = normalize_email('email')

    cleaned_count = 0
    for customer in customers:
        result = cleaner(customer, {})

        if result.modified:
            cleaned_count += 1
            print(f"✓ Cleaned customer {customer['id']}: '{result.before_value}' → '{result.after_value}'")
        elif customer['email'] is None:
            print(f"○ Skipped customer {customer['id']}: NULL email")
        else:
            print(f"○ Skipped customer {customer['id']}: already clean")

    print(f"\nTotal cleaned: {cleaned_count}/{len(customers)}\n")


def main():
    """Run all examples"""
    print("Email Normalization Examples")
    print("=" * 50 + "\n")

    example_1_single_cleaner()
    example_2_chained_cleaners()
    example_3_bulk_processing()

    print("✅ All examples completed successfully!")


if __name__ == '__main__':
    main()
