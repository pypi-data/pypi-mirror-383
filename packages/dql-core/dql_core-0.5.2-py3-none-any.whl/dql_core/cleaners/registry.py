"""Cleaner registry for looking up cleaners by name."""

from typing import Callable, Dict

from dql_core.exceptions import CleanerError


class CleanerRegistry:
    """Registry for mapping cleaner names to cleaner functions."""

    def __init__(self):
        """Initialize empty cleaner registry."""
        self._cleaners: Dict[str, Callable] = {}

    def register(self, name: str, cleaner_func: Callable) -> None:
        """Register a cleaner function.

        Args:
            name: Name of cleaner (e.g., 'trim_whitespace', 'uppercase')
            cleaner_func: Function that performs cleaning

        Raises:
            CleanerError: If cleaner name is already registered
        """
        if name in self._cleaners:
            raise CleanerError(f"Cleaner '{name}' is already registered")
        self._cleaners[name] = cleaner_func

    def get(self, name: str) -> Callable:
        """Get cleaner function by name.

        Args:
            name: Name of cleaner to look up

        Returns:
            Cleaner function

        Raises:
            CleanerError: If no cleaner is registered for name
        """
        if name not in self._cleaners:
            raise CleanerError(f"No cleaner registered with name '{name}'")
        return self._cleaners[name]

    def has(self, name: str) -> bool:
        """Check if a cleaner is registered.

        Args:
            name: Name of cleaner to check

        Returns:
            True if cleaner is registered, False otherwise
        """
        return name in self._cleaners

    def list_cleaners(self) -> list:
        """Get list of all registered cleaner names.

        Returns:
            List of cleaner names
        """
        return list(self._cleaners.keys())


# Global default registry
default_cleaner_registry = CleanerRegistry()


# Register built-in string cleaners (Story 2.4)
from dql_core.cleaners.string_cleaners import (
    trim_whitespace,
    uppercase,
    lowercase,
    normalize_email,
)

default_cleaner_registry.register("trim_whitespace", trim_whitespace)
default_cleaner_registry.register("uppercase", uppercase)
default_cleaner_registry.register("lowercase", lowercase)
default_cleaner_registry.register("normalize_email", normalize_email)

# Register built-in data type cleaners (Story 2.5)
from dql_core.cleaners.data_type_cleaners import (
    strip_non_numeric,
    normalize_phone,
    coalesce,
    format_date,
)

default_cleaner_registry.register("strip_non_numeric", strip_non_numeric)
default_cleaner_registry.register("normalize_phone", normalize_phone)
default_cleaner_registry.register("coalesce", coalesce)
default_cleaner_registry.register("format_date", format_date)
