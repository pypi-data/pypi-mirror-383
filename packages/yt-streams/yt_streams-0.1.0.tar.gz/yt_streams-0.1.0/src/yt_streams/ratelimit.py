"""Thread-safe token-bucket rate limiting mixin.

Purpose:
    Provide a minimal, dependency-free rate limiter suitable for gating
    broadcast operations in :mod:`yt_streams.controller` (e.g., avoid spamming
    workers with overlapping play cycles). Implemented as a mixin so it can be
    composed into the controller without changing its public API.

Design:
    - **Token bucket** per key (named bucket), each with ``capacity`` and
      ``refill_rate_per_sec`` (tokens per second).
    - Lock-free fast path using per-bucket ``threading.Lock`` guarding state.
    - Monotonic time for precise, drift-resistant refills.

Glossary:
    *capacity*: Max tokens that can be accumulated in the bucket.
    *refill_rate_per_sec*: Tokens regenerated per second (float allowed).

Notes:
    - ``try_acquire()`` is non-blocking; if you need blocking, wrap with a
      simple retry/sleep loop in your caller.
    - Time source is ``time.monotonic()``; not affected by wall clock changes.

Examples:
    Basic usage::

        >>> rl = RateLimitMixin()
        >>> rl.init_bucket("play_cycle", capacity=2, refill_rate_per_sec=0.5)
        >>> bool(rl.try_acquire("play_cycle"))
        True

    Best-effort retry::

        >>> import time
        >>> while not rl.try_acquire("play_cycle"):
        ...     time.sleep(0.1)
        ...
"""
from __future__ import annotations

from dataclasses import dataclass
from threading import Lock
from typing import Final
import time


@dataclass(slots=True)
class _Bucket:
    """Internal token bucket state.

    Args:
        capacity: Max tokens held.
        rate: Tokens per second regenerated.
        tokens: Current token count.
        last: Last monotonic timestamp a refill was computed against.
    """

    capacity: float
    rate: float
    tokens: float
    last: float
    lock: Lock


class RateLimitMixin:
    """Composable rate limiter using per-key token buckets.

    This mixin maintains a dict of token buckets keyed by ``name``. Use
    :meth:`init_bucket` to create one, then call :meth:`try_acquire` before an
    operation you wish to gate.

    The mixin stores no references to your objects and is safe to inherit from
    in cooperating classes like the controller.

    Attributes:
        _buckets: Internal registry of buckets.

    Examples:
        ::
            >>> rl = RateLimitMixin()
            >>> rl.init_bucket("foo", capacity=1, refill_rate_per_sec=1.0)
            >>> rl.try_acquire("foo")
            True
            >>> rl.try_acquire("foo")  # immediate second call fails until refill
            False
    """

    def __init__(self) -> None:
        self._buckets: dict[str, _Bucket] = {}

    # -------------------------- Public API --------------------------
    def init_bucket(self, name: str, *, capacity: int, refill_rate_per_sec: float) -> None:
        """Create or reset a named bucket.

        Args:
            name: Bucket identifier.
            capacity: Maximum tokens that may accumulate (>= 1).
            refill_rate_per_sec: Refill rate in tokens per second (>= 0).

        Raises:
            ValueError: If parameters are invalid.
        """
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        if refill_rate_per_sec < 0:
            raise ValueError("refill_rate_per_sec must be >= 0")
        now = time.monotonic()
        self._buckets[name] = _Bucket(
            capacity=float(capacity),
            rate=float(refill_rate_per_sec),
            tokens=float(capacity),  # start full to allow immediate burst
            last=now,
            lock=Lock(),
        )

    def try_acquire(self, name: str, *, tokens: int = 1) -> bool:
        """Attempt to consume ``tokens`` from ``name``'s bucket without blocking.

        Args:
            name: Bucket identifier created via :meth:`init_bucket`.
            tokens: Number of tokens to consume (>= 1).

        Returns:
            ``True`` if tokens were consumed; ``False`` otherwise.

        Raises:
            KeyError: If the bucket ``name`` does not exist.
        """
        if tokens < 1:
            raise ValueError("tokens must be >= 1")
        b = self._buckets[name]  # KeyError if missing
        now = time.monotonic()
        with b.lock:
            # Refill based on elapsed time
            elapsed = max(0.0, now - b.last)
            if b.rate > 0 and elapsed > 0:
                b.tokens = min(b.capacity, b.tokens + elapsed * b.rate)
            b.last = now
            if b.tokens >= tokens:
                b.tokens -= tokens
                return True
            return False

    # -------------------------- Utilities --------------------------
    def bucket_snapshot(self, name: str) -> dict[str, float]:
        """Return a diagnostic snapshot for ``name``.

        Args:
            name: Bucket identifier.

        Returns:
            Mapping with ``capacity``, ``rate``, ``tokens``, and ``age`` seconds
            since the last refill calculation.
        """
        b = self._buckets[name]
        now = time.monotonic()
        with b.lock:
            return {
                "capacity": b.capacity,
                "rate": b.rate,
                "tokens": b.tokens,
                "age": max(0.0, now - b.last),
            }


__all__: Final[list[str]] = ["RateLimitMixin"]
