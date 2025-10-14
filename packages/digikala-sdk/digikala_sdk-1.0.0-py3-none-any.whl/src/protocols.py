"""Protocol definitions for dependency injection in BaseService.

This module defines abstract interfaces (Protocols) that allow BaseService
to depend on abstractions rather than concrete implementations, following
the Dependency Inversion Principle (SOLID).
"""

from typing import Protocol, Optional, Dict, Any, runtime_checkable, Mapping


@runtime_checkable
class CacheStrategy(Protocol):
    """Protocol for cache implementations.

    Allows BaseService to work with any cache backend (memory, Redis, etc.)
    without coupling to specific implementations.
    """

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached value by key.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached dict if found, None otherwise
        """
        ...

    async def set(
        self,
        key: str,
        value: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> None:
        """Store value in cache with optional TTL.

        Args:
            key: Cache key
            value: Dict to cache
            ttl: Time-to-live in seconds (None = no expiration)
        """
        ...

    async def delete(self, key: str) -> None:
        """Remove key from cache.

        Args:
            key: Cache key to remove
        """
        ...

    async def clear(self) -> None:
        """Clear all cached values."""
        ...


@runtime_checkable
class RateLimiter(Protocol):
    """Protocol for rate limiting implementations.

    Allows BaseService to work with any rate limiting strategy
    (token bucket, leaky bucket, fixed window, etc.)
    """

    async def acquire(self) -> None:
        """Acquire permission to proceed (may block until available).

        Raises:
            Exception: If rate limit cannot be acquired (implementation-specific)
        """
        ...

    async def try_acquire(self) -> bool:
        """Try to acquire without blocking.

        Returns:
            True if acquired, False if rate limited
        """
        ...


@runtime_checkable
class RequestValidator(Protocol):
    """Protocol for request validation strategies.

    Allows different validation strategies (strict, permissive, custom)
    """

    def validate_params(self, params: Dict[str, Any]) -> None:
        """Validate request parameters.

        Args:
            params: Parameters to validate

        Raises:
            ValueError: If validation fails
        """
        ...

    def validate_endpoint(self, endpoint: str) -> None:
        """Validate endpoint path.

        Args:
            endpoint: Endpoint path to validate

        Raises:
            ValueError: If validation fails
        """
        ...


@runtime_checkable
class CircuitBreaker(Protocol):
    """Protocol for circuit breaker implementations.

    Circuit breaker prevents cascading failures by opening the circuit
    after N consecutive failures and closing it after recovery period.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Circuit is open, requests fail fast
    - HALF_OPEN: Testing if service recovered
    """

    async def call(self, func, *args, **kwargs):
        """Execute function through circuit breaker.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from func execution

        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception from func
        """
        ...

    def record_success(self) -> None:
        """Record successful execution."""
        ...

    def record_failure(self) -> None:
        """Record failed execution."""
        ...

    @property
    def state(self) -> str:
        """Get current circuit state (CLOSED, OPEN, HALF_OPEN)."""
        ...

    @property
    def failure_count(self) -> int:
        """Get current consecutive failure count."""
        ...


@runtime_checkable
class HTTPResponse(Protocol):
    """Protocol for HTTP response objects.

    Allows BaseService to work with any HTTP client library
    without coupling to httpx.Response specifically.
    """

    @property
    def status_code(self) -> int:
        """HTTP status code."""
        ...

    @property
    def headers(self) -> Mapping[str, str]:
        """Response headers."""
        ...

    @property
    def text(self) -> str:
        """Response body as text."""
        ...

    def json(self) -> Any:
        """Parse response body as JSON.

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If response is not valid JSON
        """
        ...

    @property
    def is_success(self) -> bool:
        """Check if response is successful (2xx status code)."""
        ...


@runtime_checkable
class AsyncHTTPClient(Protocol):
    """Protocol for async HTTP client implementations.

    Allows DigikalaClient to work with any HTTP client library
    (httpx, aiohttp, etc.) without tight coupling.

    This follows the Dependency Inversion Principle by depending
    on an abstraction rather than a concrete implementation.
    """

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> HTTPResponse:
        """Send an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            params: Query parameters
            json: JSON body data
            **kwargs: Additional request options

        Returns:
            HTTPResponse protocol implementation

        Raises:
            Exception: Various HTTP/network errors (implementation-specific)
        """
        ...

    async def aclose(self) -> None:
        """Close the HTTP client and release resources."""
        ...