"""Data type cleaner functions for data quality remediation (Story 2.5).

This module provides data type cleaning functions:
- strip_non_numeric: Remove all non-numeric characters
- normalize_phone: Normalize phone numbers to specified format
- coalesce: Replace NULL values with default
- format_date: Convert date strings between formats

All cleaners are framework-agnostic and work with Django models, dicts, and dataclasses.
"""

import re
from typing import Any, Callable
from datetime import datetime, date

from dql_core.results import CleanerResult


def strip_non_numeric(field_name: str) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that removes all non-numeric characters.

    Keeps only digits 0-9, removes letters, spaces, punctuation.

    Args:
        field_name: Name of the field to clean

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = strip_non_numeric('phone')
        >>> # "(555) 555-5555" → "5555555555"
        >>> # "Price: $123.45" → "12345"
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute strip_non_numeric cleaning."""
        try:
            before_value = _get_field_value(record, field_name)

            if before_value is None:
                return CleanerResult(
                    success=True,
                    modified=False,
                    before_value=None,
                    after_value=None,
                    error=None,
                )

            # Coerce to string
            str_value = str(before_value)

            # Remove all non-digit characters
            after_value = re.sub(r'[^0-9]', '', str_value)

            modified = (str_value != after_value)

            if modified:
                _set_field_value(record, field_name, after_value)

            return CleanerResult(
                success=True,
                modified=modified,
                before_value=before_value,
                after_value=after_value,
                error=None,
            )

        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                before_value=None,
                after_value=None,
                error=f"Error cleaning field '{field_name}': {str(e)}",
            )

    return cleaner_func


def normalize_phone(field_name: str, format: str = 'E164') -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that normalizes phone numbers to specified format.

    Supported formats:
    - 'E164': +1XXXXXXXXXX (international format, e.g., +15555555555)
    - 'US': (XXX) XXX-XXXX (US display format, e.g., (555) 555-5555)
    - 'digits_only': XXXXXXXXXX (no formatting, e.g., 5555555555)

    Args:
        field_name: Name of the phone field to clean
        format: Output format (default: 'E164')

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = normalize_phone('phone', format='US')
        >>> # "555-555-5555" → "(555) 555-5555"
        >>> # "(555) 555-5555" → "(555) 555-5555" (no change)
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute normalize_phone cleaning."""
        try:
            before_value = _get_field_value(record, field_name)

            if before_value is None:
                return CleanerResult(
                    success=True,
                    modified=False,
                    before_value=None,
                    after_value=None,
                    error=None,
                )

            # Strip all non-numeric characters
            str_value = str(before_value)
            digits_only = re.sub(r'[^0-9]', '', str_value)

            # Validate length (US: 10 digits, international: 11-15)
            if format == 'E164':
                if len(digits_only) == 10:
                    # Assume US, prepend country code
                    digits_only = '1' + digits_only
                elif len(digits_only) < 11 or len(digits_only) > 15:
                    return CleanerResult(
                        success=False,
                        modified=False,
                        before_value=before_value,
                        after_value=None,
                        error=f"Invalid phone length: {len(digits_only)} digits (expected 10 or 11-15 for E164)",
                    )

            elif format == 'US' or format == 'digits_only':
                if len(digits_only) != 10:
                    return CleanerResult(
                        success=False,
                        modified=False,
                        before_value=before_value,
                        after_value=None,
                        error=f"US phone must be 10 digits, got {len(digits_only)}",
                    )

            # Apply formatting
            if format == 'E164':
                after_value = '+' + digits_only

            elif format == 'US':
                # (XXX) XXX-XXXX
                after_value = f"({digits_only[0:3]}) {digits_only[3:6]}-{digits_only[6:10]}"

            elif format == 'digits_only':
                after_value = digits_only

            else:
                return CleanerResult(
                    success=False,
                    modified=False,
                    before_value=before_value,
                    after_value=None,
                    error=f"Unknown phone format: '{format}' (valid: E164, US, digits_only)",
                )

            modified = (str(before_value) != after_value)

            if modified:
                _set_field_value(record, field_name, after_value)

            return CleanerResult(
                success=True,
                modified=modified,
                before_value=before_value,
                after_value=after_value,
                error=None,
            )

        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                before_value=None,
                after_value=None,
                error=f"Error cleaning field '{field_name}': {str(e)}",
            )

    return cleaner_func


def coalesce(field_name: str, default_value: Any) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that replaces NULL values with a default.

    This cleaner ONLY modifies NULL values. Non-NULL values are left unchanged.

    Args:
        field_name: Name of the field to clean
        default_value: Value to use when field is NULL

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = coalesce('status', 'pending')
        >>> # record['status'] = None → 'pending'
        >>> # record['status'] = 'active' → 'active' (unchanged)
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute coalesce cleaning."""
        try:
            before_value = _get_field_value(record, field_name)

            # Only modify if NULL
            if before_value is None:
                _set_field_value(record, field_name, default_value)

                return CleanerResult(
                    success=True,
                    modified=True,
                    before_value=None,
                    after_value=default_value,
                    error=None,
                )
            else:
                # Non-NULL, leave unchanged
                return CleanerResult(
                    success=True,
                    modified=False,
                    before_value=before_value,
                    after_value=before_value,
                    error=None,
                )

        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                before_value=None,
                after_value=None,
                error=f"Error cleaning field '{field_name}': {str(e)}",
            )

    return cleaner_func


def format_date(field_name: str, input_format: str, output_format: str) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that converts date strings between formats.

    Handles both date/datetime objects and string values.

    Args:
        field_name: Name of the date field to clean
        input_format: strptime format string (e.g., '%Y-%m-%d')
        output_format: strftime format string (e.g., '%m/%d/%Y')

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = format_date('created_at', '%Y-%m-%d', '%m/%d/%Y')
        >>> # "2025-01-15" → "01/15/2025"

    Common Formats:
        - '%Y-%m-%d': ISO format (2025-01-15)
        - '%m/%d/%Y': US format (01/15/2025)
        - '%d-%b-%Y': Day-Month-Year (15-Jan-2025)
        - '%Y-%m-%d %H:%M:%S': ISO datetime
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute format_date cleaning."""
        try:
            before_value = _get_field_value(record, field_name)

            if before_value is None:
                return CleanerResult(
                    success=True,
                    modified=False,
                    before_value=None,
                    after_value=None,
                    error=None,
                )

            # Handle date/datetime objects
            if isinstance(before_value, (date, datetime)):
                date_obj = before_value
                after_value = date_obj.strftime(output_format)

            # Handle string values
            elif isinstance(before_value, str):
                try:
                    date_obj = datetime.strptime(before_value, input_format)
                    after_value = date_obj.strftime(output_format)
                except ValueError as e:
                    return CleanerResult(
                        success=False,
                        modified=False,
                        before_value=before_value,
                        after_value=None,
                        error=f"Cannot parse date '{before_value}' with format '{input_format}': {e}",
                    )

            else:
                return CleanerResult(
                    success=False,
                    modified=False,
                    before_value=before_value,
                    after_value=None,
                    error=f"Expected date/datetime or string, got {type(before_value).__name__}",
                )

            modified = (str(before_value) != after_value)

            if modified:
                _set_field_value(record, field_name, after_value)

            return CleanerResult(
                success=True,
                modified=modified,
                before_value=before_value,
                after_value=after_value,
                error=None,
            )

        except Exception as e:
            return CleanerResult(
                success=False,
                modified=False,
                before_value=None,
                after_value=None,
                error=f"Error cleaning field '{field_name}': {str(e)}",
            )

    return cleaner_func


# Helper functions for framework-agnostic field access


def _get_field_value(record: Any, field_name: str) -> Any:
    """
    Get field value from record (Django model, dict, dataclass).

    Args:
        record: Record object
        field_name: Field name to extract

    Returns:
        Field value or None

    Raises:
        AttributeError: If field doesn't exist
    """
    # Django model or dataclass (has attributes)
    if hasattr(record, field_name):
        return getattr(record, field_name)

    # Dictionary
    elif isinstance(record, dict):
        return record.get(field_name)

    else:
        raise AttributeError(f"Cannot access field '{field_name}' on {type(record)}")


def _set_field_value(record: Any, field_name: str, value: Any) -> None:
    """
    Set field value on record (Django model, dict, dataclass).

    Args:
        record: Record object
        field_name: Field name to set
        value: New value

    Raises:
        AttributeError: If field doesn't exist or is read-only
    """
    # Django model or dataclass (has attributes)
    if hasattr(record, field_name):
        setattr(record, field_name, value)

    # Dictionary
    elif isinstance(record, dict):
        record[field_name] = value

    else:
        raise AttributeError(f"Cannot set field '{field_name}' on {type(record)}")
