"""Tests for cleaner decorators (Story 2.6)."""

import pytest
import warnings
from dql_core.cleaners import CleanerRegistry, register_cleaner, cleaner
from dql_core.results import CleanerResult


class TestRegisterCleanerDecorator:
    """Tests for @register_cleaner decorator (legacy)."""

    def test_decorator_registers_function(self):
        """Test decorator registers function in registry."""
        registry = CleanerRegistry()

        @register_cleaner("test_cleaner", registry=registry)
        def my_cleaner(record, context):
            return CleanerResult(success=True, modified=False)

        assert registry.has("test_cleaner") is True
        cleaner_func = registry.get("test_cleaner")
        assert cleaner_func == my_cleaner

    def test_decorated_function_still_callable(self):
        """Test decorated function is still callable."""
        registry = CleanerRegistry()

        @register_cleaner("test_cleaner", registry=registry)
        def my_cleaner(record, context):
            return CleanerResult(success=True, modified=False)

        result = my_cleaner(None, {})
        assert result.success is True
        assert result.modified is False


class TestCleanerDecorator:
    """Tests for @cleaner decorator (Story 2.6)."""

    def test_cleaner_decorator_registers_function(self):
        """Test @cleaner registers function in registry."""
        registry = CleanerRegistry()

        @cleaner(registry=registry)
        def test_cleaner(record, context):
            """Test cleaner function."""
            return CleanerResult(success=True, modified=False)

        assert registry.has("test_cleaner") is True
        assert test_cleaner._is_cleaner is True
        assert test_cleaner._cleaner_name == "test_cleaner"

    def test_cleaner_decorator_with_custom_name(self):
        """Test @cleaner(name='...') uses custom name."""
        registry = CleanerRegistry()

        @cleaner(name='custom_cleaner', registry=registry)
        def some_function(record, context):
            """Some function with custom name."""
            return CleanerResult(success=True, modified=False)

        assert registry.has('custom_cleaner') is True
        assert some_function._cleaner_name == 'custom_cleaner'
        assert some_function._is_cleaner is True

    def test_cleaner_decorator_auto_extracts_name(self):
        """Test @cleaner auto-extracts name from function name."""
        registry = CleanerRegistry()

        @cleaner(registry=registry)
        def my_custom_cleaner(record, context):
            """My custom cleaner."""
            return CleanerResult(success=True, modified=False)

        assert registry.has('my_custom_cleaner') is True
        assert my_custom_cleaner._cleaner_name == 'my_custom_cleaner'

    def test_cleaner_decorator_validates_signature(self):
        """Test @cleaner validates function signature."""
        registry = CleanerRegistry()

        with pytest.raises(TypeError, match="exactly 2 parameters"):
            @cleaner(registry=registry)
            def bad_cleaner(record):  # Missing context parameter
                """Bad cleaner with wrong signature."""
                return CleanerResult(success=True, modified=False)

    def test_cleaner_decorator_validates_signature_too_many_params(self):
        """Test @cleaner rejects functions with too many parameters."""
        registry = CleanerRegistry()

        with pytest.raises(TypeError, match="exactly 2 parameters"):
            @cleaner(registry=registry)
            def bad_cleaner(record, context, extra):  # Too many parameters
                """Bad cleaner with too many params."""
                return CleanerResult(success=True, modified=False)

    def test_cleaner_decorator_skip_validation(self):
        """Test @cleaner(validate=False) skips signature validation."""
        registry = CleanerRegistry()

        # Should not raise even with wrong signature
        @cleaner(validate=False, registry=registry)
        def bad_cleaner(record):  # Missing context parameter
            """Bad cleaner but validation skipped."""
            return CleanerResult(success=True, modified=False)

        assert registry.has('bad_cleaner') is True

    def test_cleaner_decorator_warns_missing_docstring(self):
        """Test @cleaner warns when docstring is missing."""
        registry = CleanerRegistry()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            @cleaner(registry=registry)
            def no_docstring_cleaner(record, context):
                return CleanerResult(success=True, modified=False)

            # Should have warning about missing docstring
            assert len(w) == 1
            assert "missing docstring" in str(w[0].message).lower()

    def test_cleaner_decorator_no_warning_with_docstring(self):
        """Test @cleaner does not warn when docstring present."""
        registry = CleanerRegistry()

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            @cleaner(registry=registry)
            def documented_cleaner(record, context):
                """This cleaner has a docstring."""
                return CleanerResult(success=True, modified=False)

            # Should only have docstring warning, no other warnings
            # Filter for non-docstring warnings
            non_docstring_warnings = [warning for warning in w if "docstring" not in str(warning.message).lower()]
            assert len(non_docstring_warnings) == 0

    def test_cleaner_decorator_callable(self):
        """Test decorated function is still callable."""
        registry = CleanerRegistry()

        @cleaner(registry=registry)
        def test_cleaner(record, context):
            """Test cleaner."""
            return CleanerResult(success=True, modified=True, before_value='old', after_value='new')

        result = test_cleaner({'field': 'value'}, {})
        assert result.success is True
        assert result.modified is True
        assert result.before_value == 'old'
        assert result.after_value == 'new'

    def test_cleaner_decorator_without_parentheses(self):
        """Test @cleaner works without parentheses."""
        registry = CleanerRegistry()

        @cleaner
        def simple_cleaner(record, context):
            """Simple cleaner."""
            return CleanerResult(success=True, modified=False)

        # Should be registered in default_cleaner_registry
        from dql_core.cleaners import default_cleaner_registry
        assert default_cleaner_registry.has('simple_cleaner')

    def test_cleaner_decorator_with_name_and_validate(self):
        """Test @cleaner with both name and validate parameters."""
        registry = CleanerRegistry()

        @cleaner(name='custom', validate=True, registry=registry)
        def func(record, context):
            """Custom cleaner."""
            return CleanerResult(success=True, modified=False)

        assert registry.has('custom') is True
        assert func._cleaner_name == 'custom'
