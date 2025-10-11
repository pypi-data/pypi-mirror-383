"""Tests for validator registry."""

import pytest
from dql_core.validators import ValidatorRegistry, ToBeNullValidator
from dql_core.exceptions import ValidationError


class TestValidatorRegistry:
    """Tests for ValidatorRegistry."""

    def test_register_and_get_validator(self):
        """Test registering and retrieving a validator."""
        registry = ValidatorRegistry()
        registry.register("to_be_null", ToBeNullValidator)

        validator_class = registry.get("to_be_null")
        assert validator_class == ToBeNullValidator

    def test_register_duplicate_raises_error(self):
        """Test registering duplicate operator raises error."""
        registry = ValidatorRegistry()
        registry.register("to_be_null", ToBeNullValidator)

        with pytest.raises(ValidationError, match="already registered"):
            registry.register("to_be_null", ToBeNullValidator)

    def test_get_unregistered_raises_error(self):
        """Test getting unregistered operator raises error."""
        registry = ValidatorRegistry()

        with pytest.raises(ValidationError, match="No validator registered"):
            registry.get("nonexistent")

    def test_has_validator(self):
        """Test checking if validator is registered."""
        registry = ValidatorRegistry()
        registry.register("to_be_null", ToBeNullValidator)

        assert registry.has("to_be_null") is True
        assert registry.has("nonexistent") is False

    def test_list_operators(self):
        """Test listing all registered operators."""
        registry = ValidatorRegistry()
        registry.register("to_be_null", ToBeNullValidator)
        registry.register("to_not_be_null", ToBeNullValidator)

        operators = registry.list_operators()
        assert "to_be_null" in operators
        assert "to_not_be_null" in operators
        assert len(operators) == 2
