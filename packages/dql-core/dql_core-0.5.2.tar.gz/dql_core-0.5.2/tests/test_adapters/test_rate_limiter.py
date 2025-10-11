"""Tests for rate limiter."""

import time
import pytest
from dql_core.adapters import RateLimiter


class TestRateLimiter:
    """Tests for RateLimiter."""

    def test_rate_limiting(self):
        """Test rate limiter enforces delay."""
        limiter = RateLimiter(calls_per_second=10)

        start = time.time()
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        duration = time.time() - start

        # Should take at least 0.1 seconds (1/10 calls per second)
        assert duration >= 0.1

    def test_reset(self):
        """Test reset clears rate limiter state."""
        limiter = RateLimiter(calls_per_second=10)
        limiter.wait_if_needed()
        assert limiter.last_call_time is not None

        limiter.reset()
        assert limiter.last_call_time is None
