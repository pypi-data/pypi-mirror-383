"""Unit tests for data type cleaner functions (Story 2.5)."""

import pytest
from dataclasses import dataclass
from datetime import date, datetime

from dql_core.cleaners.data_type_cleaners import (
    strip_non_numeric,
    normalize_phone,
    coalesce,
    format_date,
)
from dql_core.results import CleanerResult


# Test fixtures
@dataclass
class TestRecord:
    """Test dataclass record."""
    field1: str = ""
    field2: str = ""
    field3: str = ""
    phone: str = ""
    amount: str = ""
    created_at: str = ""
    status: str = ""


class TestStripNonNumeric:
    """Tests for strip_non_numeric cleaner."""

    def test_strips_phone_format(self):
        """Test removing phone number formatting: '(555) 555-5555' → '5555555555'."""
        record = {'phone': '(555) 555-5555'}
        cleaner = strip_non_numeric('phone')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == '(555) 555-5555'
        assert result.after_value == '5555555555'
        assert record['phone'] == '5555555555'

    def test_strips_currency_format(self):
        """Test removing currency formatting: '$1,234.56' → '123456'."""
        record = {'amount': '$1,234.56'}
        cleaner = strip_non_numeric('amount')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == '$1,234.56'
        assert result.after_value == '123456'

    def test_strips_mixed_alphanumeric(self):
        """Test removing letters from mixed string: 'abc123def456' → '123456'."""
        record = {'field1': 'abc123def456'}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '123456'

    def test_already_numeric_unchanged(self):
        """Test already numeric string remains unchanged."""
        record = {'field1': '123456'}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '123456'

    def test_null_value_unchanged(self):
        """Test NULL value is left unchanged (skip NULL pattern)."""
        record = {'field1': None}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None

    def test_empty_string_unchanged(self):
        """Test empty string remains empty."""
        record = {'field1': ''}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == ''

    def test_all_non_numeric_becomes_empty(self):
        """Test string with no digits becomes empty string."""
        record = {'field1': 'abcdef'}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == ''

    def test_numeric_coercion(self):
        """Test numeric value is coerced to string."""
        record = {'field1': 12345}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '12345'

    def test_special_characters_removed(self):
        """Test special characters are removed."""
        record = {'field1': '!@#$123%^&*456()'}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '123456'

    def test_whitespace_removed(self):
        """Test whitespace is removed."""
        record = {'field1': '  123  456  '}
        cleaner = strip_non_numeric('field1')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '123456'


class TestNormalizePhone:
    """Tests for normalize_phone cleaner."""

    def test_normalize_to_e164_with_dashes(self):
        """Test normalizing to E164: '555-555-5555' → '+15555555555'."""
        record = {'phone': '555-555-5555'}
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == '555-555-5555'
        assert result.after_value == '+15555555555'
        assert record['phone'] == '+15555555555'

    def test_normalize_to_e164_with_parens(self):
        """Test normalizing to E164: '(555) 555-5555' → '+15555555555'."""
        record = {'phone': '(555) 555-5555'}
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '+15555555555'

    def test_normalize_to_e164_with_country_code(self):
        """Test normalizing to E164 with existing country code: '+1-555-555-5555' → '+15555555555'."""
        record = {'phone': '+1-555-555-5555'}
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '+15555555555'

    def test_normalize_to_us_format(self):
        """Test normalizing to US format: '5555555555' → '(555) 555-5555'."""
        record = {'phone': '5555555555'}
        cleaner = normalize_phone('phone', format='US')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '(555) 555-5555'

    def test_normalize_to_digits_only(self):
        """Test normalizing to digits only: '(555) 555-5555' → '5555555555'."""
        record = {'phone': '(555) 555-5555'}
        cleaner = normalize_phone('phone', format='digits_only')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '5555555555'

    def test_default_format_is_e164(self):
        """Test default format is E164."""
        record = {'phone': '555-555-5555'}
        cleaner = normalize_phone('phone')  # No format specified
        result = cleaner(record, {})

        assert result.success is True
        assert result.after_value == '+15555555555'

    def test_null_value_unchanged(self):
        """Test NULL value is left unchanged."""
        record = {'phone': None}
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None

    def test_invalid_length_returns_error(self):
        """Test phone with invalid length returns error."""
        record = {'phone': '123'}  # Too short
        cleaner = normalize_phone('phone', format='US')
        result = cleaner(record, {})

        assert result.success is False
        assert result.modified is False
        assert 'US phone must be 10 digits' in result.error

    def test_e164_too_short_returns_error(self):
        """Test E164 phone too short returns error."""
        record = {'phone': '123456789'}  # 9 digits, too short
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is False
        assert 'Invalid phone length: 9 digits' in result.error

    def test_e164_too_long_returns_error(self):
        """Test E164 phone too long returns error."""
        record = {'phone': '1234567890123456'}  # 16 digits, too long
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is False
        assert 'Invalid phone length: 16 digits' in result.error

    def test_unknown_format_returns_error(self):
        """Test unknown format returns error."""
        record = {'phone': '5555555555'}
        cleaner = normalize_phone('phone', format='UNKNOWN')
        result = cleaner(record, {})

        assert result.success is False
        assert "Unknown phone format: 'UNKNOWN'" in result.error

    def test_already_normalized_unchanged(self):
        """Test already normalized phone is not modified."""
        record = {'phone': '+15555555555'}
        cleaner = normalize_phone('phone', format='E164')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '+15555555555'

    def test_us_format_already_formatted_unchanged(self):
        """Test US format already formatted is not modified."""
        record = {'phone': '(555) 555-5555'}
        cleaner = normalize_phone('phone', format='US')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '(555) 555-5555'


class TestCoalesce:
    """Tests for coalesce cleaner."""

    def test_replaces_null_with_string_default(self):
        """Test replacing NULL with default string value."""
        record = {'status': None}
        cleaner = coalesce('status', 'pending')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value is None
        assert result.after_value == 'pending'
        assert record['status'] == 'pending'

    def test_replaces_null_with_numeric_default(self):
        """Test replacing NULL with default numeric value."""
        record = {'amount': None}
        cleaner = coalesce('amount', 0)
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value is None
        assert result.after_value == 0
        assert record['amount'] == 0

    def test_replaces_null_with_empty_string(self):
        """Test replacing NULL with empty string."""
        record = {'field1': None}
        cleaner = coalesce('field1', '')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == ''

    def test_non_null_value_unchanged(self):
        """Test non-NULL value is left unchanged."""
        record = {'status': 'active'}
        cleaner = coalesce('status', 'pending')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value == 'active'
        assert result.after_value == 'active'
        assert record['status'] == 'active'

    def test_empty_string_not_replaced(self):
        """Test empty string is NOT treated as NULL."""
        record = {'field1': ''}
        cleaner = coalesce('field1', 'default')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == ''

    def test_zero_not_replaced(self):
        """Test zero is NOT treated as NULL."""
        record = {'amount': 0}
        cleaner = coalesce('amount', 100)
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == 0

    def test_false_not_replaced(self):
        """Test False is NOT treated as NULL."""
        record = {'flag': False}
        cleaner = coalesce('flag', True)
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value is False

    def test_replaces_null_with_dict_default(self):
        """Test replacing NULL with dict default."""
        default_dict = {'key': 'value'}
        record = {'config': None}
        cleaner = coalesce('config', default_dict)
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == default_dict


class TestFormatDate:
    """Tests for format_date cleaner."""

    def test_format_iso_to_us(self):
        """Test converting ISO to US format: '2025-01-15' → '01/15/2025'."""
        record = {'created_at': '2025-01-15'}
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.before_value == '2025-01-15'
        assert result.after_value == '01/15/2025'
        assert record['created_at'] == '01/15/2025'

    def test_format_us_to_iso(self):
        """Test converting US to ISO format: '01/15/2025' → '2025-01-15'."""
        record = {'created_at': '01/15/2025'}
        cleaner = format_date('created_at', input_format='%m/%d/%Y', output_format='%Y-%m-%d')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '2025-01-15'

    def test_format_with_time(self):
        """Test formatting datetime with time: '2025-01-15 14:30:00' → '01/15/2025 02:30 PM'."""
        record = {'created_at': '2025-01-15 14:30:00'}
        cleaner = format_date('created_at', input_format='%Y-%m-%d %H:%M:%S', output_format='%m/%d/%Y %I:%M %p')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '01/15/2025 02:30 PM'

    def test_format_date_object(self):
        """Test formatting date object (no input_format needed)."""
        date_obj = date(2025, 1, 15)
        record = {'created_at': date_obj}
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '01/15/2025'

    def test_format_datetime_object(self):
        """Test formatting datetime object (no input_format needed)."""
        datetime_obj = datetime(2025, 1, 15, 14, 30, 0)
        record = {'created_at': datetime_obj}
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y %I:%M %p')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == '01/15/2025 02:30 PM'

    def test_null_value_unchanged(self):
        """Test NULL value is left unchanged."""
        record = {'created_at': None}
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.before_value is None
        assert result.after_value is None

    def test_invalid_date_string_returns_error(self):
        """Test unparseable date string returns error."""
        record = {'created_at': 'invalid-date'}
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is False
        assert result.modified is False
        assert "Cannot parse date 'invalid-date'" in result.error

    def test_wrong_format_returns_error(self):
        """Test date string with wrong format returns error."""
        record = {'created_at': '01/15/2025'}  # US format
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')  # Expects ISO
        result = cleaner(record, {})

        assert result.success is False
        assert "Cannot parse date '01/15/2025'" in result.error

    def test_non_date_type_returns_error(self):
        """Test non-date/string type returns error."""
        record = {'created_at': 12345}  # Numeric value
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is False
        assert 'Expected date/datetime or string, got int' in result.error

    def test_already_formatted_unchanged(self):
        """Test already formatted date is not modified."""
        record = {'created_at': '01/15/2025'}
        cleaner = format_date('created_at', input_format='%m/%d/%Y', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is False
        assert result.after_value == '01/15/2025'

    def test_format_month_names(self):
        """Test formatting with month names: '2025-01-15' → 'January 15, 2025'."""
        record = {'created_at': '2025-01-15'}
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%B %d, %Y')
        result = cleaner(record, {})

        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'January 15, 2025'


class TestFrameworkAgnostic:
    """Tests for framework-agnostic record handling."""

    def test_strip_non_numeric_with_dict(self):
        """Test strip_non_numeric works with dict records."""
        record = {'phone': '(555) 555-5555'}
        cleaner = strip_non_numeric('phone')
        result = cleaner(record, {})

        assert result.success is True
        assert record['phone'] == '5555555555'

    def test_normalize_phone_with_dataclass(self):
        """Test normalize_phone works with dataclass records."""
        record = TestRecord(phone='555-555-5555')
        cleaner = normalize_phone('phone', format='US')
        result = cleaner(record, {})

        assert result.success is True
        assert record.phone == '(555) 555-5555'

    def test_coalesce_with_dict(self):
        """Test coalesce works with dict records."""
        record = {'status': None}
        cleaner = coalesce('status', 'pending')
        result = cleaner(record, {})

        assert result.success is True
        assert record['status'] == 'pending'

    def test_format_date_with_dataclass(self):
        """Test format_date works with dataclass records."""
        record = TestRecord(created_at='2025-01-15')
        cleaner = format_date('created_at', input_format='%Y-%m-%d', output_format='%m/%d/%Y')
        result = cleaner(record, {})

        assert result.success is True
        assert record.created_at == '01/15/2025'


class TestErrorHandling:
    """Tests for error handling in data type cleaners."""

    def test_missing_field_on_dataclass_returns_error(self):
        """Test missing field on dataclass returns error."""
        record = TestRecord()
        cleaner = strip_non_numeric('nonexistent_field')
        result = cleaner(record, {})

        assert result.success is False
        assert "Cannot access field 'nonexistent_field'" in result.error

    def test_missing_field_on_dict_returns_none(self):
        """Test missing field on dict returns None (handled as NULL)."""
        record = {'other_field': 'value'}
        cleaner = coalesce('missing_field', 'default')
        result = cleaner(record, {})

        # dict.get() returns None, which coalesce replaces with default
        assert result.success is True
        assert result.modified is True
        assert result.after_value == 'default'


class TestCleanerResult:
    """Tests for CleanerResult structure from data type cleaners."""

    def test_result_structure_on_success(self):
        """Test CleanerResult has correct structure on success."""
        record = {'phone': '(555) 555-5555'}
        cleaner = strip_non_numeric('phone')
        result = cleaner(record, {})

        assert isinstance(result, CleanerResult)
        assert result.success is True
        assert result.modified is True
        assert result.before_value == '(555) 555-5555'
        assert result.after_value == '5555555555'
        assert result.error is None

    def test_result_structure_on_error(self):
        """Test CleanerResult has correct structure on error."""
        record = {'phone': '123'}
        cleaner = normalize_phone('phone', format='US')
        result = cleaner(record, {})

        assert isinstance(result, CleanerResult)
        assert result.success is False
        assert result.modified is False
        assert result.error is not None
        assert 'US phone must be 10 digits' in result.error

    def test_result_structure_on_unchanged(self):
        """Test CleanerResult has correct structure when value unchanged."""
        record = {'status': 'active'}
        cleaner = coalesce('status', 'pending')
        result = cleaner(record, {})

        assert isinstance(result, CleanerResult)
        assert result.success is True
        assert result.modified is False
        assert result.before_value == 'active'
        assert result.after_value == 'active'
        assert result.error is None
