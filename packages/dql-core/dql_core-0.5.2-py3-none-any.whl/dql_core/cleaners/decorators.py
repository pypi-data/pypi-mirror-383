"""Decorators for cleaner registration (Story 2.6)."""

from typing import Callable, Optional

from dql_core.cleaners.registry import default_cleaner_registry
from dql_core.cleaners.validation import validate_cleaner_signature


def cleaner(name: Optional[str] = None, registry=None, validate: bool = True):
    """
    Decorator to register a custom cleaner function.

    Supports two usage patterns:
    1. @cleaner - Auto-extracts name from function name
    2. @cleaner(name='custom_name') - Uses explicit name

    Args:
        name: Name to register cleaner under (auto-extracts from function name if not provided)
        registry: CleanerRegistry to use (defaults to default_cleaner_registry)
        validate: Whether to validate function signature (default: True)

    Returns:
        Decorator function or decorated function

    Raises:
        TypeError: If function signature is invalid

    Example:
        >>> @cleaner
        ... def my_cleaner(record, context):
        ...     '''Custom cleaner that does something.'''
        ...     return CleanerResult(success=True, modified=False)

        >>> @cleaner(name='custom_name')
        ... def some_function(record, context):
        ...     '''Custom cleaner with explicit name.'''
        ...     return CleanerResult(success=True, modified=False)

        >>> @cleaner(validate=False)
        ... def no_validation(record, context):
        ...     '''Skip signature validation.'''
        ...     return CleanerResult(success=True, modified=False)
    """
    reg = registry or default_cleaner_registry

    def decorator(func: Callable) -> Callable:
        # Validate signature if requested
        if validate:
            validate_cleaner_signature(func)

        # Extract cleaner name
        cleaner_name = name or func.__name__

        # Register cleaner
        reg.register(cleaner_name, func)

        # Add metadata to function
        func._is_cleaner = True
        func._cleaner_name = cleaner_name

        return func

    # Support both @cleaner and @cleaner(name='...')
    if callable(name):
        # @cleaner (no arguments) - name is actually the function
        func = name
        name = None
        return decorator(func)
    else:
        # @cleaner(name='...') (with arguments)
        return decorator


def register_cleaner(name: str, registry=None):
    """
    Decorator to register a cleaner function (legacy API).

    This is the original decorator from Story 0.2. For new code, use @cleaner instead.

    Args:
        name: Name to register cleaner under
        registry: CleanerRegistry to use (defaults to default_cleaner_registry)

    Returns:
        Decorator function

    Example:
        >>> @register_cleaner('trim_whitespace')
        ... def trim_whitespace(record, context):
        ...     # cleaning logic
        ...     return CleanerResult(success=True, modified=True)
    """
    reg = registry or default_cleaner_registry

    def decorator(func: Callable) -> Callable:
        reg.register(name, func)
        return func

    return decorator
