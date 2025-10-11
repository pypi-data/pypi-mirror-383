"""String cleaner functions for data quality remediation (Story 2.4).

This module provides basic string cleaning functions:
- trim_whitespace: Remove leading/trailing whitespace
- uppercase: Convert to uppercase
- lowercase: Convert to lowercase
- normalize_email: Trim and lowercase email addresses

All cleaners are framework-agnostic and work with Django models, dicts, and dataclasses.
"""

from typing import Any, Callable
from dql_core.results import CleanerResult


def trim_whitespace(field_name: str) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that removes leading/trailing whitespace.

    Args:
        field_name: Name of the field to clean

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = trim_whitespace('description')
        >>> result = cleaner(record, {})
        >>> result.modified  # True if whitespace was removed
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute trim_whitespace cleaning."""
        try:
            # Extract field value
            before_value = _get_field_value(record, field_name)

            # Handle NULL
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

            # Apply cleaning
            after_value = str_value.strip()

            # Check if modified
            modified = (str_value != after_value)

            # Set field value
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


def uppercase(field_name: str) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that converts field to uppercase.

    Args:
        field_name: Name of the field to clean

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = uppercase('country_code')
        >>> result = cleaner(record, {})
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute uppercase cleaning."""
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

            str_value = str(before_value)
            after_value = str_value.upper()
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


def lowercase(field_name: str) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that converts field to lowercase.

    Args:
        field_name: Name of the field to clean

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = lowercase('username')
        >>> result = cleaner(record, {})
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute lowercase cleaning."""
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

            str_value = str(before_value)
            after_value = str_value.lower()
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


def normalize_email(field_name: str) -> Callable[[Any, dict], CleanerResult]:
    """
    Create a cleaner that normalizes email addresses.

    Normalization:
    - Remove leading/trailing whitespace
    - Convert to lowercase
    - Optional: Basic format validation

    Args:
        field_name: Name of the email field to clean

    Returns:
        Cleaner function that takes (record, context) and returns CleanerResult

    Example:
        >>> cleaner = normalize_email('email')
        >>> result = cleaner(record, {})
        >>> # " [email protected] " → "[email protected]"
    """
    def cleaner_func(record: Any, context: dict) -> CleanerResult:
        """Execute normalize_email cleaning."""
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

            # Apply normalization: strip + lowercase
            str_value = str(before_value)
            after_value = str_value.strip().lower()
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
