#!/usr/bin/env python3
"""
Custom Cleaner Example

Demonstrates how to create custom cleaners for domain-specific rules.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult
import re


@cleaner(name='normalize_ssn')
def normalize_ssn_cleaner(field_name: str):
    """
    Normalize SSN to XXX-XX-XXXX format.

    Example: "123456789" → "123-45-6789"
    """
    def cleaner_func(record, context):
        # Get field value
        value = record.get(field_name) if isinstance(record, dict) else getattr(record, field_name, None)

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
        if isinstance(record, dict):
            record[field_name] = formatted
        else:
            setattr(record, field_name, formatted)

        return CleanerResult(
            success=True,
            modified=(str(value) != formatted),
            before_value=value,
            after_value=formatted
        )

    return cleaner_func


@cleaner(name='remove_special_chars')
def remove_special_chars_cleaner(field_name: str):
    """Remove special characters, keep only alphanumeric and spaces."""
    def cleaner_func(record, context):
        value = record.get(field_name) if isinstance(record, dict) else getattr(record, field_name, None)

        if value is None:
            return CleanerResult(success=True, modified=False)

        # Remove special characters
        cleaned = re.sub(r'[^a-zA-Z0-9 ]', '', str(value))

        # Apply change
        if isinstance(record, dict):
            record[field_name] = cleaned
        else:
            setattr(record, field_name, cleaned)

        return CleanerResult(
            success=True,
            modified=(str(value) != cleaned),
            before_value=value,
            after_value=cleaned
        )

    return cleaner_func


@cleaner(name='truncate_string')
def truncate_string_cleaner(field_name: str, max_length: int = 100, suffix: str = '...'):
    """Truncate string to maximum length with optional suffix."""
    def cleaner_func(record, context):
        value = record.get(field_name) if isinstance(record, dict) else getattr(record, field_name, None)

        if not value or len(str(value)) <= max_length:
            return CleanerResult(success=True, modified=False)

        # Truncate
        value_str = str(value)
        truncated = value_str[:max_length - len(suffix)] + suffix

        # Apply change
        if isinstance(record, dict):
            record[field_name] = truncated
        else:
            setattr(record, field_name, truncated)

        return CleanerResult(
            success=True,
            modified=True,
            before_value=value,
            after_value=truncated
        )

    return cleaner_func


def example_1_ssn_normalization():
    """Example 1: SSN Normalization"""
    print("=== Example 1: SSN Normalization ===\n")

    test_cases = [
        ('123456789', '123-45-6789', True),
        ('123-45-6789', '123-45-6789', False),  # Already formatted
        ('123.45.6789', '123-45-6789', True),
        ('123', None, False),  # Invalid length
    ]

    cleaner = normalize_ssn_cleaner('ssn')

    for input_val, expected, should_succeed in test_cases:
        record = {'ssn': input_val}
        result = cleaner(record, {})

        if should_succeed:
            status = '✓' if result.success else '✗'
            print(f"{status} '{input_val}' → '{record['ssn']}'")
        else:
            print(f"✗ '{input_val}' → Error: {result.error}")

    print()


def example_2_remove_special_chars():
    """Example 2: Remove Special Characters"""
    print("=== Example 2: Remove Special Characters ===\n")

    records = [
        {'description': 'Product #123 (NEW!)'},
        {'description': 'Email: [email protected]'},
        {'description': 'Price: $19.99'},
    ]

    cleaner = remove_special_chars_cleaner('description')

    for record in records:
        original = record['description']
        result = cleaner(record, {})
        print(f"'{original}' → '{record['description']}'")

    print()


def example_3_truncate_string():
    """Example 3: Truncate Long Strings"""
    print("=== Example 3: Truncate Long Strings ===\n")

    records = [
        {'bio': 'A' * 150},  # Very long
        {'bio': 'Short bio'},  # Within limit
    ]

    cleaner = truncate_string_cleaner('bio', max_length=50, suffix='...')

    for record in records:
        original_length = len(record['bio'])
        result = cleaner(record, {})
        new_length = len(record['bio'])

        if result.modified:
            print(f"Truncated: {original_length} chars → {new_length} chars")
            print(f"  '{record['bio']}'")
        else:
            print(f"Unchanged: {new_length} chars (within limit)")

    print()


def example_4_chaining_custom_cleaners():
    """Example 4: Chaining Custom Cleaners"""
    print("=== Example 4: Chaining Custom Cleaners ===\n")

    from dql_core.cleaners.chain import CleanerChain
    from dql_core.cleaners.string_cleaners import trim_whitespace

    # Chain: trim → remove special chars → truncate
    chain = CleanerChain()
    chain.add('trim_whitespace', 'description')
    chain.add('remove_special_chars', 'description')
    chain.add('truncate_string', 'description')

    record = {'description': '  Product #123 (AMAZING!)  ' + 'A' * 200}
    print(f"Original length: {len(record['description'])}")

    result = chain.execute(record, {})

    print(f"Final length: {len(record['description'])}")
    print(f"Final value: '{record['description'][:80]}...'")
    print(f"Modified: {result.modified}")

    print()


def main():
    """Run all examples"""
    print("Custom Cleaner Examples")
    print("=" * 50 + "\n")

    example_1_ssn_normalization()
    example_2_remove_special_chars()
    example_3_truncate_string()
    example_4_chaining_custom_cleaners()

    print("✅ All examples completed successfully!")


if __name__ == '__main__':
    main()
