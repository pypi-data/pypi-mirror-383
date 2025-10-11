"""Tests for cleaner registry."""

import pytest
from dql_core.cleaners import CleanerRegistry
from dql_core.results import CleanerResult
from dql_core.exceptions import CleanerError


def sample_cleaner(record, context):
    """Sample cleaner function."""
    return CleanerResult(success=True, modified=True)


class TestCleanerRegistry:
    """Tests for CleanerRegistry."""

    def test_register_and_get_cleaner(self):
        """Test registering and retrieving a cleaner."""
        registry = CleanerRegistry()
        registry.register("trim_whitespace", sample_cleaner)

        cleaner = registry.get("trim_whitespace")
        assert cleaner == sample_cleaner

    def test_register_duplicate_raises_error(self):
        """Test registering duplicate cleaner raises error."""
        registry = CleanerRegistry()
        registry.register("trim_whitespace", sample_cleaner)

        with pytest.raises(CleanerError, match="already registered"):
            registry.register("trim_whitespace", sample_cleaner)

    def test_get_unregistered_raises_error(self):
        """Test getting unregistered cleaner raises error."""
        registry = CleanerRegistry()

        with pytest.raises(CleanerError, match="No cleaner registered"):
            registry.get("nonexistent")

    def test_has_cleaner(self):
        """Test checking if cleaner is registered."""
        registry = CleanerRegistry()
        registry.register("trim_whitespace", sample_cleaner)

        assert registry.has("trim_whitespace") is True
        assert registry.has("nonexistent") is False

    def test_list_cleaners(self):
        """Test listing all registered cleaners."""
        registry = CleanerRegistry()
        registry.register("trim_whitespace", sample_cleaner)
        registry.register("uppercase", sample_cleaner)

        cleaners = registry.list_cleaners()
        assert "trim_whitespace" in cleaners
        assert "uppercase" in cleaners
        assert len(cleaners) == 2
