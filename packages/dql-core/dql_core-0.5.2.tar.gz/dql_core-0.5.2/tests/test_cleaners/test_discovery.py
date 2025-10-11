"""Tests for cleaner auto-discovery (Story 2.6)."""

import pytest
import warnings
from pathlib import Path
from dql_core.cleaners.discovery import discover_cleaners, register_cleaners_from_directory
from dql_core.cleaners import CleanerRegistry, default_cleaner_registry
from dql_core.results import CleanerResult


class TestDiscoverCleaners:
    """Tests for discover_cleaners function."""

    def test_discover_cleaners_finds_decorated_functions(self, tmp_path):
        """Test discover_cleaners finds @cleaner decorated functions."""
        # Create test cleaner file
        cleaner_file = tmp_path / "custom_cleaners.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def custom_cleaner1(record, context):
    '''First custom cleaner.'''
    return CleanerResult(success=True, modified=False)

@cleaner(name='custom_cleaner2')
def some_function(record, context):
    '''Second custom cleaner with explicit name.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=False)

        assert 'custom_cleaner1' in discovered
        assert 'custom_cleaner2' in discovered

    def test_discover_cleaners_skips_test_files(self, tmp_path):
        """Test discover_cleaners skips test_ files."""
        test_file = tmp_path / "test_cleaners.py"
        test_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def should_not_be_discovered(record, context):
    '''This should be skipped.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=False)

        assert 'should_not_be_discovered' not in discovered

    def test_discover_cleaners_skips_init_files(self, tmp_path):
        """Test discover_cleaners skips __init__.py files."""
        init_file = tmp_path / "__init__.py"
        init_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def should_not_be_discovered(record, context):
    '''This should be skipped.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=False)

        assert 'should_not_be_discovered' not in discovered

    def test_discover_cleaners_recursive(self, tmp_path):
        """Test discover_cleaners with recursive=True."""
        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Create cleaner in subdir
        cleaner_file = subdir / "nested_cleaners.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def nested_cleaner(record, context):
    '''Nested cleaner.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=True)

        assert 'nested_cleaner' in discovered

    def test_discover_cleaners_non_recursive(self, tmp_path):
        """Test discover_cleaners with recursive=False."""
        # Create subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        # Create cleaner in subdir
        cleaner_file = subdir / "nested_cleaners.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def nested_cleaner(record, context):
    '''Nested cleaner.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=False)

        # Should not find nested cleaner
        assert 'nested_cleaner' not in discovered

    def test_discover_cleaners_handles_import_errors(self, tmp_path):
        """Test discover_cleaners handles import errors gracefully."""
        # Create file with syntax error
        bad_file = tmp_path / "bad_cleaners.py"
        bad_file.write_text("""
this is not valid python syntax!!!
""")

        # Should warn but not raise
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            discovered = discover_cleaners(str(tmp_path), recursive=False)

            # Should have warning about failed import
            import_warnings = [warning for warning in w if "Failed to import" in str(warning.message)]
            assert len(import_warnings) >= 1

        # Should return empty list (or whatever else was discovered)
        assert isinstance(discovered, list)

    def test_discover_cleaners_ignores_non_cleaner_functions(self, tmp_path):
        """Test discover_cleaners ignores regular functions."""
        cleaner_file = tmp_path / "mixed_functions.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def actual_cleaner(record, context):
    '''This is a cleaner.'''
    return CleanerResult(success=True, modified=False)

def regular_function(record, context):
    '''This is NOT a cleaner.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=False)

        assert 'actual_cleaner' in discovered
        assert 'regular_function' not in discovered

    def test_discover_cleaners_path_not_exist_raises(self):
        """Test discover_cleaners raises FileNotFoundError for non-existent path."""
        with pytest.raises(FileNotFoundError, match="does not exist"):
            discover_cleaners('/nonexistent/path')

    def test_discover_cleaners_multiple_files(self, tmp_path):
        """Test discover_cleaners finds cleaners in multiple files."""
        # Create multiple cleaner files
        file1 = tmp_path / "cleaners1.py"
        file1.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def cleaner_from_file1(record, context):
    '''Cleaner from file 1.'''
    return CleanerResult(success=True, modified=False)
""")

        file2 = tmp_path / "cleaners2.py"
        file2.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def cleaner_from_file2(record, context):
    '''Cleaner from file 2.'''
    return CleanerResult(success=True, modified=False)
""")

        discovered = discover_cleaners(str(tmp_path), recursive=False)

        assert 'cleaner_from_file1' in discovered
        assert 'cleaner_from_file2' in discovered


class TestRegisterCleanersFromDirectory:
    """Tests for register_cleaners_from_directory function."""

    def test_registers_discovered_cleaners(self, tmp_path):
        """Test register_cleaners_from_directory registers cleaners."""
        cleaner_file = tmp_path / "custom_cleaners.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def test_directory_cleaner(record, context):
    '''Test directory cleaner.'''
    return CleanerResult(success=True, modified=False)
""")

        registered = register_cleaners_from_directory(str(tmp_path), recursive=False)

        assert 'test_directory_cleaner' in registered
        # Should also be in default registry
        assert default_cleaner_registry.has('test_directory_cleaner')

    def test_returns_list_of_names(self, tmp_path):
        """Test register_cleaners_from_directory returns list of cleaner names."""
        cleaner_file = tmp_path / "custom_cleaners.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def cleaner_a(record, context):
    '''Cleaner A.'''
    return CleanerResult(success=True, modified=False)

@cleaner
def cleaner_b(record, context):
    '''Cleaner B.'''
    return CleanerResult(success=True, modified=False)
""")

        registered = register_cleaners_from_directory(str(tmp_path), recursive=False)

        assert isinstance(registered, list)
        assert len(registered) == 2
        assert 'cleaner_a' in registered
        assert 'cleaner_b' in registered

    def test_works_with_recursive(self, tmp_path):
        """Test register_cleaners_from_directory with recursive=True."""
        subdir = tmp_path / "nested"
        subdir.mkdir()

        cleaner_file = subdir / "cleaners.py"
        cleaner_file.write_text("""
from dql_core.cleaners.decorators import cleaner
from dql_core.results import CleanerResult

@cleaner
def nested_directory_cleaner(record, context):
    '''Nested cleaner.'''
    return CleanerResult(success=True, modified=False)
""")

        registered = register_cleaners_from_directory(str(tmp_path), recursive=True)

        assert 'nested_directory_cleaner' in registered
