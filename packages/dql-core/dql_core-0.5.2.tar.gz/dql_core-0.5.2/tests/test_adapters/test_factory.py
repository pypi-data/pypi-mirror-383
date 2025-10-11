"""Tests for adapter factory."""

import pytest
from dql_core.adapters import ExternalAPIAdapter, APIAdapterFactory
from dql_core.exceptions import AdapterError


class MockAdapter(ExternalAPIAdapter):
    """Mock adapter for testing."""

    def call(self, **kwargs):
        return {"result": "success"}


class TestAPIAdapterFactory:
    """Tests for APIAdapterFactory."""

    def test_register_and_create_adapter(self):
        """Test registering and creating an adapter."""
        factory = APIAdapterFactory()
        factory.register("mock", MockAdapter)

        adapter = factory.create("mock")
        assert isinstance(adapter, MockAdapter)

    def test_register_duplicate_raises_error(self):
        """Test registering duplicate adapter type raises error."""
        factory = APIAdapterFactory()
        factory.register("mock", MockAdapter)

        with pytest.raises(AdapterError, match="already registered"):
            factory.register("mock", MockAdapter)

    def test_create_unregistered_raises_error(self):
        """Test creating unregistered adapter raises error."""
        factory = APIAdapterFactory()

        with pytest.raises(AdapterError, match="No adapter registered"):
            factory.create("nonexistent")

    def test_list_types(self):
        """Test listing registered adapter types."""
        factory = APIAdapterFactory()
        factory.register("mock", MockAdapter)
        factory.register("mock2", MockAdapter)

        types = factory.list_types()
        assert "mock" in types
        assert "mock2" in types
        assert len(types) == 2
