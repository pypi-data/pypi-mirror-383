"""Concrete implementations of protocols for BaseService.

This module provides default implementations of CacheStrategy, RateLimiter,
RequestValidator, and AsyncHTTPClient protocols that can be used with BaseService.
"""

import asyncio
import hashlib
import json
import time
from enum import Enum
from typing import Optional, Dict, Any, Callable, Mapping

from .protocols import (
    CacheStrategy,
    RateLimiter,
    RequestValidator,
    CircuitBreaker,
    AsyncHTTPClient,
    HTTPResponse,
)
from .exceptions import CircuitBreakerOpenError


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"  # Normal operation
    OPEN = "OPEN"  # Circuit is open, fail fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


class DefaultValidator(RequestValidator):
    """Default request validation with security checks."""

    # User-adjusted limits from security analysis
    MAX_PARAM_KEY_LENGTH = 512
    MAX_PARAM_VALUE_LENGTH = 200000  # 200KB

    def validate_params(self, params: Dict[str, Any]) -> None:
        """Validate request parameters for security and DoS protection."""
        suspicious_patterns = [
            "../",  # Path traversal
            "://",  # Protocol injection
            "<script",  # XSS attempt
            "javascript:",  # JavaScript injection
            "\x00",  # Null byte injection
        ]

        def _check_value(key: str, value: Any, path: str = "") -> None:
            """Recursively validate parameter values."""
            current_path = f"{path}.{key}" if path else key

            # Check key length (DoS protection)
            if len(key) > self.MAX_PARAM_KEY_LENGTH:
                raise ValueError(
                    f"Parameter key '{key[:50]}...' exceeds maximum length "
                    f"({self.MAX_PARAM_KEY_LENGTH} characters)"
                )

            if isinstance(value, str):
                # Check value length (DoS protection)
                if len(value) > self.MAX_PARAM_VALUE_LENGTH:
                    raise ValueError(
                        f"Parameter value for '{current_path}' exceeds maximum length "
                        f"({self.MAX_PARAM_VALUE_LENGTH} characters)"
                    )

                # Check for suspicious patterns (injection protection)
                value_lower = value.lower()
                for pattern in suspicious_patterns:
                    if pattern in value_lower:
                        raise ValueError(
                            f"Suspicious pattern detected in parameter '{current_path}': {pattern}"
                        )

            elif isinstance(value, dict):
                # Recursively validate nested dictionaries
                for nested_key, nested_value in value.items():
                    _check_value(nested_key, nested_value, current_path)

            elif isinstance(value, list):
                # Validate list items
                for idx, item in enumerate(value):
                    _check_value(f"[{idx}]", item, current_path)

        # Validate all parameters
        for key, value in params.items():
            _check_value(key, value)

    def validate_endpoint(self, endpoint: str) -> None:
        """Validate endpoint path."""
        if not endpoint.startswith("/"):
            raise ValueError(f"Endpoint must start with '/': {endpoint}")

        # Check for suspicious patterns
        suspicious = ["../", "//", "\x00"]
        for pattern in suspicious:
            if pattern in endpoint:
                raise ValueError(f"Suspicious pattern in endpoint: {pattern}")


class MemoryCacheStrategy(CacheStrategy):
    """Simple in-memory cache implementation using a dict.

    Note: This is a basic implementation. For production use, consider
    using aiocache or similar libraries with TTL support.
    """

    def __init__(self) -> None:
        """Initialize empty cache."""
        self._cache: Dict[str, Dict[str, Any]] = {}

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key."""
        return self._cache.get(key)

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Store value in cache (TTL not implemented in basic version)."""
        self._cache[key] = value

    async def delete(self, key: str) -> None:
        """Remove key from cache."""
        self._cache.pop(key, None)

    async def clear(self) -> None:
        """Clear all cached values."""
        self._cache.clear()


class NoOpRateLimiter(RateLimiter):
    """Rate limiter that does nothing (no rate limiting).

    Useful as default when rate limiting is not configured.
    """

    async def acquire(self) -> None:
        """No-op acquire (always succeeds immediately)."""
        pass

    async def try_acquire(self) -> bool:
        """No-op try_acquire (always returns True)."""
        return True


class AioLimiterAdapter(RateLimiter):
    """Adapter for aiolimiter library.

    Wraps aiolimiter.AsyncLimiter to conform to RateLimiter protocol.
    """

    def __init__(self, limiter: Any) -> None:
        """Initialize with aiolimiter.AsyncLimiter instance.

        Args:
            limiter: aiolimiter.AsyncLimiter instance
        """
        self._limiter = limiter

    async def acquire(self) -> None:
        """Acquire rate limit permission (blocks if necessary)."""
        await self._limiter.acquire()

    async def try_acquire(self) -> bool:
        """Try to acquire without blocking."""
        # aiolimiter doesn't have try_acquire, so we use acquire
        # This is a limitation of the current adapter
        await self._limiter.acquire()
        return True


class AioCacheAdapter(CacheStrategy):
    """Adapter for aiocache library to conform to CacheStrategy protocol.

    Wraps aiocache.Cache to provide a consistent interface.
    """

    def __init__(self, cache: Any) -> None:
        """Initialize with aiocache.Cache instance.

        Args:
            cache: aiocache.Cache instance
        """
        self._cache = cache

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key."""
        try:
            data = await self._cache.get(key)
            return data if data is not None else None
        except Exception:
            return None

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Store value in cache with optional TTL."""
        try:
            if ttl is not None:
                await self._cache.set(key, value, ttl=ttl)
            else:
                await self._cache.set(key, value)
        except Exception:
            pass  # Silently fail cache writes

    async def delete(self, key: str) -> None:
        """Remove key from cache."""
        try:
            await self._cache.delete(key)
        except Exception:
            pass

    async def clear(self) -> None:
        """Clear all cached values."""
        try:
            await self._cache.clear()
        except Exception:
            pass


class DefaultCircuitBreaker(CircuitBreaker):
    """Default circuit breaker implementation.

    Implements the circuit breaker pattern to prevent cascading failures:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, fail fast without calling service
    - HALF_OPEN: Testing if service recovered

    Args:
        failure_threshold: Number of consecutive failures to open circuit (default: 5)
        recovery_timeout: Seconds before attempting recovery (default: 60)
        success_threshold: Successes needed in HALF_OPEN to close circuit (default: 2)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2
    ):
        """Initialize circuit breaker with thresholds."""
        self._state = CircuitState.CLOSED
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._success_threshold = success_threshold

        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function through circuit breaker."""
        async with self._lock:
            # Check if we should attempt recovery
            if self._state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._state = CircuitState.HALF_OPEN
                    self._success_count = 0
                else:
                    # Still open, fail fast
                    time_since_failure = time.time() - (self._last_failure_time or 0)
                    retry_after = self._recovery_timeout - time_since_failure
                    raise CircuitBreakerOpenError(
                        message=f"Circuit breaker is OPEN for {func.__name__}",
                        failure_count=self._failure_count,
                        retry_after=max(0, retry_after)
                    )

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise e

    def record_success(self) -> None:
        """Record successful execution."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._success_threshold:
                # Recovered! Close the circuit
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
        elif self._state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def record_failure(self) -> None:
        """Record failed execution."""
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            # Failed during recovery attempt, reopen circuit
            self._state = CircuitState.OPEN
            self._failure_count = self._failure_threshold
        elif self._state == CircuitState.CLOSED:
            self._failure_count += 1
            if self._failure_count >= self._failure_threshold:
                # Too many failures, open the circuit
                self._state = CircuitState.OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery."""
        if self._last_failure_time is None:
            return True
        time_since_failure = time.time() - self._last_failure_time
        return time_since_failure >= self._recovery_timeout

    @property
    def state(self) -> str:
        """Get current circuit state."""
        return self._state.value

    @property
    def failure_count(self) -> int:
        """Get current consecutive failure count."""
        return self._failure_count


class NoOpCircuitBreaker(CircuitBreaker):
    """No-op circuit breaker that does nothing.

    Useful as default when circuit breaker is not configured.
    """

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function without circuit breaker protection."""
        return await func(*args, **kwargs)

    def record_success(self) -> None:
        """No-op."""
        pass

    def record_failure(self) -> None:
        """No-op."""
        pass

    @property
    def state(self) -> str:
        """Always returns CLOSED."""
        return CircuitState.CLOSED.value

    @property
    def failure_count(self) -> int:
        """Always returns 0."""
        return 0


def generate_cache_key(endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Generate Blake2b hash for cache key.

    Uses Blake2b (faster and more secure than MD5) with 16-byte digest
    to produce 32-character hex string (same format as MD5).

    Args:
        endpoint: API endpoint path
        params: Request parameters

    Returns:
        32-character hex string
    """
    params_str = json.dumps(params or {}, sort_keys=True)
    cache_string = f"{endpoint}?{params_str}"
    return hashlib.blake2b(cache_string.encode(), digest_size=16).hexdigest()


class HttpxAdapter(AsyncHTTPClient):
    """Adapter for httpx.AsyncClient to conform to AsyncHTTPClient protocol.

    This adapter wraps httpx.AsyncClient and provides a protocol-based interface,
    allowing the SDK to be decoupled from httpx and potentially support other
    HTTP clients in the future.

    Args:
        client: httpx.AsyncClient instance to wrap
    """

    def __init__(self, client: Any) -> None:
        """Initialize adapter with httpx.AsyncClient.

        Args:
            client: httpx.AsyncClient instance
        """
        self._client = client

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> HTTPResponse:
        """Send HTTP request using httpx.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            json: JSON body data
            **kwargs: Additional httpx request options

        Returns:
            HTTPResponse (httpx.Response implements this protocol)
        """
        response = await self._client.request(
            method=method,
            url=url,
            params=params,
            json=json,
            **kwargs
        )
        # httpx.Response already implements HTTPResponse protocol
        return response

    async def aclose(self) -> None:
        """Close the httpx client."""
        await self._client.aclose()