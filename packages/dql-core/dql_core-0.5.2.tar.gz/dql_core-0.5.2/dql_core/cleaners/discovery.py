"""Auto-discovery of custom cleaner functions (Story 2.6)."""

import os
import sys
import importlib.util
import warnings
from pathlib import Path
from typing import List

from dql_core.cleaners.validation import is_cleaner_function
from dql_core.cleaners.registry import default_cleaner_registry


def discover_cleaners(path: str, recursive: bool = True) -> List[str]:
    """
    Auto-discover cleaners in a directory.

    Scans Python files for @cleaner decorated functions and imports them.
    The @cleaner decorator automatically registers functions in the registry.

    Args:
        path: Directory path to scan
        recursive: Whether to scan subdirectories (default: True)

    Returns:
        List of discovered cleaner names

    Raises:
        FileNotFoundError: If path does not exist

    Example:
        >>> # Discover all cleaners in my_cleaners/ directory
        >>> discovered = discover_cleaners('my_cleaners/')
        >>> print(discovered)
        ['normalize_ssn', 'validate_credit_card', 'format_address']

        >>> # Discover only in top-level directory
        >>> discovered = discover_cleaners('my_cleaners/', recursive=False)
    """
    discovered = []
    path_obj = Path(path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    # Find all Python files
    if recursive:
        py_files = path_obj.rglob('*.py')
    else:
        py_files = path_obj.glob('*.py')

    for py_file in py_files:
        # Skip __init__.py and test files
        if py_file.name.startswith('__') or py_file.name.startswith('test_'):
            continue

        try:
            # Import module
            module_name = py_file.stem
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                warnings.warn(
                    f"Could not load spec for {py_file}",
                    UserWarning
                )
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find cleaner functions
            for attr_name in dir(module):
                # Skip private/dunder attributes
                if attr_name.startswith('_'):
                    continue

                attr = getattr(module, attr_name)
                if callable(attr) and is_cleaner_function(attr):
                    cleaner_name = attr._cleaner_name
                    discovered.append(cleaner_name)

        except Exception as e:
            # Log warning but continue
            warnings.warn(
                f"Failed to import {py_file}: {e}",
                UserWarning
            )

    return discovered


def register_cleaners_from_directory(path: str, recursive: bool = True, registry=None) -> List[str]:
    """
    Discover and register cleaners from a directory.

    Convenience function that combines discovery with registration.
    The @cleaner decorator already registers functions, so this function
    primarily serves to trigger the imports and return the list of names.

    Args:
        path: Directory path to scan
        recursive: Whether to scan subdirectories (default: True)
        registry: CleanerRegistry to use (not currently used, for API compatibility)

    Returns:
        List of registered cleaner names

    Example:
        >>> registered = register_cleaners_from_directory('my_cleaners/')
        >>> print(f"Registered {len(registered)} custom cleaners")
        Registered 3 custom cleaners

        >>> # Use in application startup
        >>> def setup_custom_cleaners():
        ...     register_cleaners_from_directory('app/data_quality/cleaners/')
    """
    # Note: registry parameter not used because @cleaner decorator
    # already registers functions in default_cleaner_registry
    return discover_cleaners(path, recursive)
