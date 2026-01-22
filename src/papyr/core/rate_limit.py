"""Rate limiting utilities."""

from __future__ import annotations

import time

from papyr.core.models import RateLimitPolicy


class RateLimiter:
    """Simple rate limiter using minimum delay between calls."""

    def __init__(self, policy: RateLimitPolicy) -> None:
        self._policy = policy
        self._last_call: float | None = None

    def wait(self) -> None:
        """Sleep to enforce minimum delay."""
        if self._last_call is None:
            self._last_call = time.time()
            return
        elapsed = time.time() - self._last_call
        if elapsed < self._policy.min_delay_seconds:
            time.sleep(self._policy.min_delay_seconds - elapsed)
        self._last_call = time.time()
