"""Unit tests for string cleaner functions (Story 2.4)."""

import pytest
from dataclasses import dataclass

from dql_core.cleaners.string_cleaners import (
    trim_whitespace,
    uppercase,
    lowercase,
    normalize_email,
)
from dql_core.results import CleanerResult


# ==================== Test Fixtures ====================


@dataclass
class MockDataclass:
    """Mock dataclass record for testing."""
    name: str = ""
    email: str = ""
    description: str = ""


class MockModel:
    """Mock Django model for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# ==================== trim_whitespace Tests ====================


class TestTrimWhitespace:
    """Test trim_whitespace cleaner function."""

    def test_removes_leading_whitespace(self):
        """Test trim_whitespace removes leading spaces."""
        record = {'description': '  Hello World'}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == '  Hello World'
        assert result.after_value == 'Hello World'
        assert record['description'] == 'Hello World'

    def test_removes_trailing_whitespace(self):
        """Test trim_whitespace removes trailing spaces."""
        record = {'description': 'Hello World  '}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'Hello World'
        assert record['description'] == 'Hello World'

    def test_removes_both_leading_and_trailing(self):
        """Test trim_whitespace removes both leading and trailing spaces."""
        record = {'description': '  Hello World  '}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'Hello World'

    def test_handles_tabs_and_newlines(self):
        """Test trim_whitespace handles tabs and newlines."""
        record = {'description': '\t\nHello World\n\t'}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'Hello World'

    def test_handles_null_value(self):
        """Test trim_whitespace skips NULL values."""
        record = {'description': None}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None
        assert record['description'] is None

    def test_no_modification_when_no_whitespace(self):
        """Test trim_whitespace doesn't modify clean strings."""
        record = {'description': 'Hello World'}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value == 'Hello World'
        assert result.after_value == 'Hello World'

    def test_empty_string(self):
        """Test trim_whitespace with empty string."""
        record = {'description': ''}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False

    def test_whitespace_only_string(self):
        """Test trim_whitespace with whitespace-only string."""
        record = {'description': '   '}
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == ''

    def test_coerces_numeric_to_string(self):
        """Test trim_whitespace coerces numeric values to string."""
        record = {'code': 12345}
        cleaner = trim_whitespace('code')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '12345'

    def test_with_dataclass(self):
        """Test trim_whitespace works with dataclass."""
        record = MockDataclass(description='  Clean Me  ')
        cleaner = trim_whitespace('description')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert record.description == 'Clean Me'

    def test_with_model_instance(self):
        """Test trim_whitespace works with Django model-like object."""
        record = MockModel(name='  John Doe  ')
        cleaner = trim_whitespace('name')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert record.name == 'John Doe'

    def test_missing_field_on_dataclass_returns_error(self):
        """Test trim_whitespace handles missing field on dataclass."""
        record = MockDataclass(name='test')  # Missing 'missing_field'
        cleaner = trim_whitespace('missing_field')
        result = cleaner(record, {})

        assert result.success is False
        assert result.modified is False
        assert result.error is not None
        assert 'missing_field' in result.error


# ==================== uppercase Tests ====================


class TestUppercase:
    """Test uppercase cleaner function."""

    def test_converts_lowercase_to_uppercase(self):
        """Test uppercase converts lowercase strings."""
        record = {'country_code': 'us'}
        cleaner = uppercase('country_code')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == 'us'
        assert result.after_value == 'US'
        assert record['country_code'] == 'US'

    def test_converts_mixed_case_to_uppercase(self):
        """Test uppercase converts mixed case strings."""
        record = {'name': 'John Doe'}
        cleaner = uppercase('name')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'JOHN DOE'

    def test_handles_already_uppercase(self):
        """Test uppercase doesn't modify already uppercase strings."""
        record = {'country_code': 'US'}
        cleaner = uppercase('country_code')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == 'US'

    def test_handles_null_value(self):
        """Test uppercase skips NULL values."""
        record = {'country_code': None}
        cleaner = uppercase('country_code')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None

    def test_handles_empty_string(self):
        """Test uppercase with empty string."""
        record = {'text': ''}
        cleaner = uppercase('text')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False

    def test_coerces_numeric_to_string(self):
        """Test uppercase coerces numeric values to string."""
        record = {'code': 123}
        cleaner = uppercase('code')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False  # Numbers don't change
        assert result.after_value == '123'

    def test_with_special_characters(self):
        """Test uppercase with special characters."""
        record = {'text': 'hello@world!'}
        cleaner = uppercase('text')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'HELLO@WORLD!'

    def test_with_dataclass(self):
        """Test uppercase works with dataclass."""
        record = MockDataclass(name='john')
        cleaner = uppercase('name')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert record.name == 'JOHN'


# ==================== lowercase Tests ====================


class TestLowercase:
    """Test lowercase cleaner function."""

    def test_converts_uppercase_to_lowercase(self):
        """Test lowercase converts uppercase strings."""
        record = {'username': 'JOHNDOE'}
        cleaner = lowercase('username')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == 'JOHNDOE'
        assert result.after_value == 'johndoe'
        assert record['username'] == 'johndoe'

    def test_converts_mixed_case_to_lowercase(self):
        """Test lowercase converts mixed case strings."""
        record = {'name': 'John Doe'}
        cleaner = lowercase('name')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'john doe'

    def test_handles_already_lowercase(self):
        """Test lowercase doesn't modify already lowercase strings."""
        record = {'username': 'johndoe'}
        cleaner = lowercase('username')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == 'johndoe'

    def test_handles_null_value(self):
        """Test lowercase skips NULL values."""
        record = {'username': None}
        cleaner = lowercase('username')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None

    def test_handles_empty_string(self):
        """Test lowercase with empty string."""
        record = {'text': ''}
        cleaner = lowercase('text')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False

    def test_with_special_characters(self):
        """Test lowercase with special characters."""
        record = {'text': 'HELLO@WORLD!'}
        cleaner = lowercase('text')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'hello@world!'

    def test_with_dataclass(self):
        """Test lowercase works with dataclass."""
        record = MockDataclass(name='JOHN')
        cleaner = lowercase('name')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert record.name == 'john'


# ==================== normalize_email Tests ====================


class TestNormalizeEmail:
    """Test normalize_email cleaner function."""

    def test_normalizes_email_with_spaces_and_uppercase(self):
        """Test normalize_email handles spaces and case."""
        record = {'email': ' [email protected] '}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == ' [email protected] '
        assert result.after_value == '[email protected]'
        assert record['email'] == '[email protected]'

    def test_trims_whitespace_from_email(self):
        """Test normalize_email trims leading/trailing whitespace."""
        record = {'email': '  [email protected]  '}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '[email protected]'

    def test_lowercases_email(self):
        """Test normalize_email converts to lowercase."""
        record = {'email': 'TEST@EXAMPLE.COM'}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'test@example.com'

    def test_handles_already_normalized_email(self):
        """Test normalize_email doesn't modify clean emails."""
        record = {'email': '[email protected]'}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '[email protected]'

    def test_handles_null_email(self):
        """Test normalize_email skips NULL values."""
        record = {'email': None}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None
        assert record['email'] is None

    def test_handles_empty_string(self):
        """Test normalize_email with empty string."""
        record = {'email': ''}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False

    def test_with_tabs_and_newlines(self):
        """Test normalize_email handles tabs and newlines."""
        record = {'email': '\t\[email protected]\n'}
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '\\[email protected]'  # Backslash in email is preserved

    def test_with_multiple_formats(self):
        """Test normalize_email with various email formats."""
        test_cases = [
            ('  [email protected]  ', '[email protected]'),
            ('[email protected]', '[email protected]'),
            ('USER+TAG@DOMAIN.COM', 'user+tag@domain.com'),
            (' Test.User@Example.Co.UK ', 'test.user@example.co.uk'),
        ]

        for input_email, expected_email in test_cases:
            record = {'email': input_email}
            cleaner = normalize_email('email')
            result = cleaner(record, {})

            assert result.success is True
            assert result.after_value == expected_email
            assert record['email'] == expected_email

    def test_with_dataclass(self):
        """Test normalize_email works with dataclass."""
        record = MockDataclass(email=' [email protected] ')
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert record.email == '[email protected]'

    def test_with_model_instance(self):
        """Test normalize_email works with Django model-like object."""
        record = MockModel(email=' TEST@EXAMPLE.COM ')
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert record.email == 'test@example.com'


# ==================== Framework Agnostic Tests ====================


class TestFrameworkAgnostic:
    """Test cleaners work with multiple record types."""

    def test_dict_record_trim_whitespace(self):
        """Test trim_whitespace with dict record."""
        record = {'field': '  value  '}
        cleaner = trim_whitespace('field')
        result = cleaner(record, {})

        assert result.success is True
        assert record['field'] == 'value'

    def test_dataclass_record_uppercase(self):
        """Test uppercase with dataclass record."""
        record = MockDataclass(name='test')
        cleaner = uppercase('name')
        result = cleaner(record, {})

        assert result.success is True
        assert record.name == 'TEST'

    def test_model_record_lowercase(self):
        """Test lowercase with model-like record."""
        record = MockModel(name='TEST')
        cleaner = lowercase('name')
        result = cleaner(record, {})

        assert result.success is True
        assert record.name == 'test'

    def test_model_record_normalize_email(self):
        """Test normalize_email with model-like record."""
        record = MockModel(email=' TEST@EXAMPLE.COM ')
        cleaner = normalize_email('email')
        result = cleaner(record, {})

        assert result.success is True
        assert record.email == 'test@example.com'


# ==================== Error Handling Tests ====================


class TestErrorHandling:
    """Test error handling in cleaners."""

    def test_missing_field_on_dict_returns_none(self):
        """Test cleaner handles missing field on dict (dict.get returns None)."""
        record = {'other_field': 'value'}
        cleaner = trim_whitespace('missing')
        result = cleaner(record, {})

        # Dict.get() returns None for missing keys, so it's handled as NULL
        assert result.success is True
        assert result.modified is False
        assert result.before_value is None

    def test_unsupported_record_type(self):
        """Test cleaner handles unsupported record type."""
        record = "not a valid record type"
        cleaner = trim_whitespace('field')
        result = cleaner(record, {})

        assert result.success is False
        assert result.error is not None


# ==================== CleanerResult Structure Tests ====================


class TestCleanerResult:
    """Test CleanerResult structure and values."""

    def test_result_has_all_fields_on_success(self):
        """Test CleanerResult has all required fields on success."""
        record = {'field': '  value  '}
        cleaner = trim_whitespace('field')
        result = cleaner(record, {})

        assert hasattr(result, 'success')
        assert hasattr(result, 'modified')
        assert hasattr(result, 'before_value')
        assert hasattr(result, 'after_value')
        assert hasattr(result, 'error')
        assert result.error is None

    def test_result_has_all_fields_on_error(self):
        """Test CleanerResult has all required fields on error."""
        record = "invalid_type"  # Will cause AttributeError
        cleaner = trim_whitespace('field')
        result = cleaner(record, {})

        assert result.success is False
        assert result.modified is False
        assert result.error is not None
        assert isinstance(result.error, str)

    def test_before_after_values_captured(self):
        """Test before/after values are captured correctly."""
        record = {'field': '  OLD  '}
        cleaner = trim_whitespace('field')
        result = cleaner(record, {})

        assert result.before_value == '  OLD  '
        assert result.after_value == 'OLD'
        assert result.before_value != result.after_value
