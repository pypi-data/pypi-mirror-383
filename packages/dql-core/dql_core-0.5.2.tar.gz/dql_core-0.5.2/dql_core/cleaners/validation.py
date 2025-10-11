"""Signature validation for cleaner functions (Story 2.6)."""

import inspect
import warnings
from typing import Callable, get_type_hints

from dql_core.results import CleanerResult


def validate_cleaner_signature(func: Callable) -> None:
    """
    Validate that a function has the correct signature for a cleaner.

    Required signature: func(record, context) -> CleanerResult

    Args:
        func: Function to validate

    Raises:
        TypeError: If signature is invalid

    Example:
        >>> def my_cleaner(record, context):
        ...     return CleanerResult(success=True, modified=False)
        >>> validate_cleaner_signature(my_cleaner)  # No error

        >>> def bad_cleaner(record):
        ...     return CleanerResult(success=True, modified=False)
        >>> validate_cleaner_signature(bad_cleaner)  # Raises TypeError
    """
    sig = inspect.signature(func)
    params = list(sig.parameters.keys())

    # Check parameter count
    if len(params) != 2:
        raise TypeError(
            f"Cleaner function '{func.__name__}' must have exactly 2 parameters "
            f"(record, context), got {len(params)}: {params}"
        )

    # Check return type hint if present (warning only, not error)
    try:
        type_hints = get_type_hints(func)
        if 'return' in type_hints:
            return_type = type_hints['return']
            # Allow CleanerResult or None (no hint)
            if return_type != CleanerResult and return_type is not type(None):
                warnings.warn(
                    f"Cleaner function '{func.__name__}' should return CleanerResult, "
                    f"got {return_type}",
                    UserWarning,
                    stacklevel=3
                )
    except Exception:
        # Type hints not available or invalid, skip check
        pass

    # Check docstring (warning only)
    if not func.__doc__:
        warnings.warn(
            f"Cleaner function '{func.__name__}' missing docstring",
            UserWarning,
            stacklevel=3
        )


def is_cleaner_function(func: Callable) -> bool:
    """
    Check if a function is decorated with @cleaner.

    Args:
        func: Function to check

    Returns:
        True if function is a cleaner

    Example:
        >>> @cleaner
        ... def my_cleaner(record, context):
        ...     return CleanerResult(success=True, modified=False)
        >>> is_cleaner_function(my_cleaner)
        True

        >>> def regular_function():
        ...     pass
        >>> is_cleaner_function(regular_function)
        False
    """
    return hasattr(func, '_is_cleaner') and func._is_cleaner
