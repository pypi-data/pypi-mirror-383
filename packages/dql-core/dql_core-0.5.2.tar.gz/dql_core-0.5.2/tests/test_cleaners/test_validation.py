"""Tests for cleaner signature validation (Story 2.6)."""

import pytest
import warnings
from dql_core.cleaners.validation import validate_cleaner_signature, is_cleaner_function
from dql_core.results import CleanerResult


class TestValidateCleanerSignature:
    """Tests for validate_cleaner_signature function."""

    def test_valid_signature_passes(self):
        """Test valid cleaner signature passes validation."""
        def valid_cleaner(record, context):
            """Valid cleaner."""
            return CleanerResult(success=True, modified=False)

        # Should not raise
        validate_cleaner_signature(valid_cleaner)

    def test_invalid_signature_one_param_raises(self):
        """Test signature with one parameter raises TypeError."""
        def invalid_cleaner(record):
            """Invalid cleaner."""
            return CleanerResult(success=True, modified=False)

        with pytest.raises(TypeError, match="exactly 2 parameters"):
            validate_cleaner_signature(invalid_cleaner)

    def test_invalid_signature_three_params_raises(self):
        """Test signature with three parameters raises TypeError."""
        def invalid_cleaner(record, context, extra):
            """Invalid cleaner."""
            return CleanerResult(success=True, modified=False)

        with pytest.raises(TypeError, match="exactly 2 parameters"):
            validate_cleaner_signature(invalid_cleaner)

    def test_invalid_signature_no_params_raises(self):
        """Test signature with no parameters raises TypeError."""
        def invalid_cleaner():
            """Invalid cleaner."""
            return CleanerResult(success=True, modified=False)

        with pytest.raises(TypeError, match="exactly 2 parameters"):
            validate_cleaner_signature(invalid_cleaner)

    def test_valid_signature_any_param_names(self):
        """Test validation allows any parameter names."""
        def valid_cleaner(r, c):
            """Valid cleaner with short param names."""
            return CleanerResult(success=True, modified=False)

        # Should not raise - parameter names don't matter, only count
        validate_cleaner_signature(valid_cleaner)

    def test_missing_docstring_warns(self):
        """Test missing docstring generates warning."""
        def no_docstring(record, context):
            return CleanerResult(success=True, modified=False)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_cleaner_signature(no_docstring)

            # Should have warning about missing docstring
            assert len(w) == 1
            assert "missing docstring" in str(w[0].message).lower()
            assert w[0].category == UserWarning

    def test_with_docstring_no_warning(self):
        """Test function with docstring does not warn."""
        def with_docstring(record, context):
            """This function has a docstring."""
            return CleanerResult(success=True, modified=False)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_cleaner_signature(with_docstring)

            # Filter for non-docstring warnings
            non_docstring_warnings = [warning for warning in w if "docstring" not in str(warning.message).lower()]
            assert len(non_docstring_warnings) == 0

    def test_with_type_hints_valid(self):
        """Test validation works with type hints."""
        def typed_cleaner(record: dict, context: dict) -> CleanerResult:
            """Typed cleaner."""
            return CleanerResult(success=True, modified=False)

        # Should not raise
        validate_cleaner_signature(typed_cleaner)

    def test_wrong_return_type_hint_warns(self):
        """Test wrong return type hint generates warning."""
        def wrong_return_type(record, context) -> str:  # Wrong return type
            """Cleaner with wrong return type."""
            return CleanerResult(success=True, modified=False)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            validate_cleaner_signature(wrong_return_type)

            # Should have warnings (return type + missing docstring check)
            return_type_warnings = [warning for warning in w if "CleanerResult" in str(warning.message)]
            assert len(return_type_warnings) >= 1


class TestIsCleanerFunction:
    """Tests for is_cleaner_function helper."""

    def test_decorated_function_returns_true(self):
        """Test is_cleaner_function returns True for decorated function."""
        def test_func(record, context):
            """Test function."""
            return CleanerResult(success=True, modified=False)

        # Add cleaner metadata (simulating @cleaner decorator)
        test_func._is_cleaner = True

        assert is_cleaner_function(test_func) is True

    def test_regular_function_returns_false(self):
        """Test is_cleaner_function returns False for regular function."""
        def regular_func(record, context):
            """Regular function."""
            return CleanerResult(success=True, modified=False)

        assert is_cleaner_function(regular_func) is False

    def test_function_with_false_flag_returns_false(self):
        """Test is_cleaner_function returns False when flag is False."""
        def test_func(record, context):
            """Test function."""
            return CleanerResult(success=True, modified=False)

        test_func._is_cleaner = False

        assert is_cleaner_function(test_func) is False

    def test_non_function_returns_false(self):
        """Test is_cleaner_function returns False for non-function."""
        assert is_cleaner_function("not a function") is False
        assert is_cleaner_function(123) is False
        assert is_cleaner_function(None) is False
