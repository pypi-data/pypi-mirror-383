"""Base service class with common HTTP functionality.

This module provides the foundational HTTP request handling for all Digikala SDK services,
including rate limiting, retry logic, optional caching, and comprehensive error handling.

Example:
    Basic usage in a service class::

        from .base import BaseService
        from ..models import ProductDetailResponse

        class ProductsService(BaseService):
            async def get_product(self, id: int) -> ProductDetailResponse:
                return await self._request(
                    method="GET",
                    endpoint=f"/v2/product/{id}/",
                    response_model=ProductDetailResponse
                )

    With caching enabled::

        config = DigikalaConfig(
            api_key="your-api-key",
            cache_config={
                "enabled": True,
                "backend": "memory",
                "ttl": 300
            }
        )
        async with DigikalaClient(config=config) as client:
            # GET requests will be cached for 5 minutes
            product = await client.products.get_product(id=123)

    With custom rate limiting::

        config = DigikalaConfig(
            api_key="your-api-key",
            rate_limit_requests=50  # 50 requests per minute
        )
"""

import asyncio
import hashlib
import json
import logging
from typing import Optional, Any, Dict, Type, TypeVar, Callable
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, ValidationError

try:
    from aiolimiter import AsyncLimiter
except ImportError:
    AsyncLimiter = None  # type: ignore

try:
    from aiocache import Cache
    from aiocache.serializers import JsonSerializer
except ImportError:
    Cache = None  # type: ignore
    JsonSerializer = None  # type: ignore

from ..config import DigikalaConfig
from ..exceptions import (
    DigikalaAPIError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError as DigikalaTimeoutError,
    ConnectionError as DigikalaConnectionError,
    ValidationError as DigikalaValidationError,
)
from ..protocols import CacheStrategy, RateLimiter, RequestValidator, AsyncHTTPClient
from ..implementations import (
    DefaultValidator,
    MemoryCacheStrategy,
    NoOpRateLimiter,
    AioLimiterAdapter,
    AioCacheAdapter,
    generate_cache_key,
)

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)

# Allowed HTTP methods for security
ALLOWED_HTTP_METHODS = frozenset({"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"})


class BaseService:
    """
    Base service class providing common HTTP functionality with advanced features.

    This class now follows the Dependency Inversion Principle (SOLID) by depending
    on Protocol abstractions rather than concrete implementations.

    This class provides:
    - Automatic retry logic with exponential backoff
    - Client-side rate limiting (via RateLimiter protocol)
    - Optional response caching for GET requests (via CacheStrategy protocol)
    - Comprehensive error handling
    - Request/response validation (via RequestValidator protocol)
    - Security checks for injection attacks

    All service classes should inherit from this base class to access
    HTTP methods with built-in retry logic and error handling.

    Attributes:
        client: AsyncHTTPClient protocol implementation (default: httpx adapter)
        config: SDK configuration
        rate_limiter: RateLimiter protocol implementation for request throttling
        cache_strategy: CacheStrategy protocol implementation for response caching
        validator: RequestValidator protocol implementation for security checks
    """

    def __init__(
        self,
        client: AsyncHTTPClient,
        config: DigikalaConfig,
        cache_strategy: Optional[CacheStrategy] = None,
        rate_limiter: Optional[RateLimiter] = None,
        validator: Optional[RequestValidator] = None,
    ):
        """
        Initialize base service with dependency injection.

        This constructor now accepts protocol implementations as dependencies,
        following the Dependency Inversion Principle (SOLID).

        Args:
            client: AsyncHTTPClient protocol implementation for HTTP requests
            config: SDK configuration
            cache_strategy: Optional CacheStrategy implementation for response caching.
                If None and caching is configured, a default implementation will be created.
            rate_limiter: Optional RateLimiter implementation for request throttling.
                If None and rate limiting is configured, a default implementation will be created.
            validator: Optional RequestValidator implementation for security checks.
                If None, DefaultValidator will be used.

        Note:
            - If dependencies are not provided, default implementations will be used
            - Default implementations may require additional packages (aiolimiter, aiocache)
            - All dependencies can be swapped for testing or customization
            - The HTTP client is decoupled via AsyncHTTPClient protocol
        """
        self.client = client
        self.config = config

        # Use provided validator or create default
        self.validator: RequestValidator = validator or DefaultValidator()

        # Initialize rate limiter
        if rate_limiter is not None:
            # Use provided rate limiter
            self.rate_limiter: RateLimiter = rate_limiter
            logger.info("Using custom rate limiter")
        elif self.config.rate_limit_requests > 0:
            # Create default rate limiter if configured
            if AsyncLimiter is not None:
                limiter = AsyncLimiter(
                    max_rate=self.config.rate_limit_requests,
                    time_period=60.0
                )
                self.rate_limiter = AioLimiterAdapter(limiter)
                logger.info(
                    f"Rate limiting enabled: {self.config.rate_limit_requests} requests/minute"
                )
            else:
                logger.warning(
                    "Rate limiting requested but 'aiolimiter' is not installed. "
                    "Install with: pip install aiolimiter"
                )
                self.rate_limiter = NoOpRateLimiter()
        else:
            # No rate limiting
            self.rate_limiter = NoOpRateLimiter()

        # Initialize cache strategy
        if cache_strategy is not None:
            # Use provided cache strategy
            self.cache_strategy: Optional[CacheStrategy] = cache_strategy
            logger.info("Using custom cache strategy")
        elif self.config.cache_config and self.config.cache_config.get("enabled", False):
            # Create default cache strategy if configured
            if Cache is not None and JsonSerializer is not None:
                self.cache_strategy = self._create_default_cache_strategy()
            else:
                logger.warning(
                    "Caching requested but 'aiocache' is not installed. "
                    "Install with: pip install aiocache"
                )
                self.cache_strategy = None
        else:
            # No caching
            self.cache_strategy = None

    def _create_default_cache_strategy(self) -> Optional[CacheStrategy]:
        """Create default aiocache-based cache strategy from configuration.

        Returns:
            AioCacheAdapter wrapping aiocache.Cache, or None if creation fails

        Note:
            This is a legacy compatibility layer. For new code, prefer creating
            CacheStrategy implementations directly and passing them to constructor.
        """
        cache_config = self.config.cache_config or {}
        backend = cache_config.get("backend", "memory").lower()
        ttl = cache_config.get("ttl", 300)

        try:
            if backend == "redis":
                redis_config = cache_config.get("redis", {})
                endpoint = redis_config.get("endpoint", "localhost")
                port = redis_config.get("port", 6379)

                cache = Cache(
                    Cache.REDIS,
                    endpoint=endpoint,
                    port=port,
                    serializer=JsonSerializer(),
                    ttl=ttl,
                    namespace="digikala_sdk"
                )
                logger.info(f"Redis cache enabled: {endpoint}:{port}, TTL={ttl}s")
            else:
                # Memory cache (default)
                cache = Cache(
                    Cache.MEMORY,
                    serializer=JsonSerializer(),
                    ttl=ttl,
                    namespace="digikala_sdk"
                )
                logger.info(f"Memory cache enabled: TTL={ttl}s")

            # Wrap aiocache.Cache in an adapter to conform to CacheStrategy protocol
            return AioCacheAdapter(cache)

        except Exception as e:
            logger.error(f"Failed to initialize cache: {str(e)}, falling back to no caching")
            return None

    def _initialize_cache(self) -> None:
        """
        Initialize cache backend based on configuration.

        Supports both memory and Redis backends. Falls back to memory
        if Redis connection fails.
        """
        cache_config = self.config.cache_config or {}
        backend = cache_config.get("backend", "memory").lower()
        ttl = cache_config.get("ttl", 300)

        try:
            if backend == "redis":
                redis_config = cache_config.get("redis", {})
                endpoint = redis_config.get("endpoint", "localhost")
                port = redis_config.get("port", 6379)

                self.cache = Cache(
                    Cache.REDIS,
                    endpoint=endpoint,
                    port=port,
                    serializer=JsonSerializer(),
                    ttl=ttl,
                    namespace="digikala_sdk"
                )
                logger.info(
                    f"Redis cache enabled: {endpoint}:{port}, TTL={ttl}s"
                )
            else:
                # Memory cache (default)
                self.cache = Cache(
                    Cache.MEMORY,
                    serializer=JsonSerializer(),
                    ttl=ttl,
                    namespace="digikala_sdk"
                )
                logger.info(f"Memory cache enabled: TTL={ttl}s")

        except Exception as e:
            logger.error(f"Failed to initialize cache: {str(e)}, falling back to no caching")
            self.cache = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T],
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> T:
        """
        Make an HTTP request with retry logic, rate limiting, and optional caching.

        This is the main entry point for all HTTP requests in the SDK.
        It handles validation, rate limiting, caching, retries, and error handling.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (must start with '/')
            response_model: Pydantic model for response validation
            params: Query parameters (optional)
            json_data: JSON body data (optional)
            **kwargs: Additional httpx request parameters

        Returns:
            Validated response model instance

        Raises:
            ValueError: If method or endpoint validation fails
            DigikalaAPIError: For various API errors (see exception hierarchy)

        Example:
            >>> response = await self._request(
            ...     method="GET",
            ...     endpoint="/v2/product/123/",
            ...     response_model=ProductDetailResponse
            ... )
        """
        # Validate HTTP method
        method_upper = method.upper()
        if method_upper not in ALLOWED_HTTP_METHODS:
            raise ValueError(
                f"Invalid HTTP method: {method}. "
                f"Allowed methods: {', '.join(sorted(ALLOWED_HTTP_METHODS))}"
            )

        # Validate endpoint format
        if not endpoint:
            raise ValueError("Endpoint cannot be empty")

        if not endpoint.startswith("/"):
            raise ValueError(
                f"Endpoint must start with '/'. Got: {endpoint}"
            )

        # Validate parameters to prevent injection attacks (delegate to protocol)
        if params:
            self.validator.validate_params(params)

        # Check cache for GET requests
        if method_upper == "GET" and self.cache_strategy is not None:
            cache_key = generate_cache_key(endpoint, params)
            cached_response = await self.cache_strategy.get(cache_key)
            if cached_response is not None:
                logger.debug(f"Cache hit: {method_upper} {endpoint}")
                try:
                    return response_model(**cached_response)
                except Exception as e:
                    logger.warning(f"Cached response validation failed: {str(e)}")
                    # Continue with fresh request if cache validation fails

        # Apply rate limiting (delegate to protocol)
        await self.rate_limiter.acquire()
        logger.debug(f"Rate limit check passed for {method_upper} {endpoint}")

        result = await self._execute_request(
            method_upper, endpoint, response_model, params, json_data, **kwargs
        )

        # Cache successful GET responses
        if method_upper == "GET" and self.cache_strategy is not None:
            cache_key = generate_cache_key(endpoint, params)
            await self.cache_strategy.set(cache_key, result.model_dump())

        return result

    async def _execute_request(
        self,
        method: str,
        endpoint: str,
        response_model: Type[T],
        params: Optional[Dict[str, Any]],
        json_data: Optional[Dict[str, Any]],
        **kwargs
    ) -> T:
        """
        Execute HTTP request with retry logic.

        This method handles the actual HTTP call and delegates retry logic
        to the _execute_with_retry helper method.

        Args:
            method: HTTP method (already validated and uppercase)
            endpoint: API endpoint path
            response_model: Pydantic model for response validation
            params: Query parameters
            json_data: JSON body data
            **kwargs: Additional httpx request parameters

        Returns:
            Validated response model instance

        Raises:
            DigikalaAPIError: For various API errors
        """
        url = urljoin(self.config.base_url, endpoint)

        async def request_fn() -> T:
            """Inner request function for retry logic."""
            logger.debug(
                f"Executing request: {method} {url}",
                extra={"params": params, "json": json_data}
            )

            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                **kwargs
            )

            # Raise exception for error status codes
            self._raise_for_status(response)

            # Parse and validate response
            try:
                response_data = response.json()
                return response_model(**response_data)
            except (ValueError, ValidationError) as e:
                logger.error(f"Response validation failed: {str(e)}")
                raise DigikalaValidationError(
                    f"Failed to parse response: {str(e)}",
                    status_code=response.status_code,
                    response=response.text
                )

        # Execute with retry logic
        return await self._execute_with_retry(
            request_fn=request_fn,
            max_retries=self.config.max_retries
        )

    async def _execute_with_retry(
        self,
        request_fn: Callable[[], Any],
        max_retries: int
    ) -> T:
        """
        Execute a request function with exponential backoff retry logic.

        This method extracts retry logic from the main request flow,
        making it independently testable and reusable.

        Args:
            request_fn: Async function that performs the HTTP request
            max_retries: Maximum number of retry attempts

        Returns:
            Result from successful request_fn execution

        Raises:
            DigikalaAPIError: After all retry attempts are exhausted

        Example:
            >>> async def my_request():
            ...     return await self.client.get("/endpoint")
            >>>
            >>> result = await self._execute_with_retry(
            ...     request_fn=my_request,
            ...     max_retries=3
            ... )
        """
        attempt = 0
        last_exception = None

        while attempt <= max_retries:
            try:
                # Try to execute the request
                return await request_fn()

            except httpx.TimeoutException as e:
                last_exception = DigikalaTimeoutError(
                    f"Request timeout after {self.config.timeout}s",
                    response=str(e)
                )
                logger.error(f"Request timeout (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")

            except httpx.ConnectError as e:
                last_exception = DigikalaConnectionError(
                    f"Connection failed: {str(e)}",
                    response=str(e)
                )
                logger.error(f"Connection error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")

            except RateLimitError as e:
                # Handle server-side rate limiting with Retry-After header
                last_exception = e
                if e.retry_after and attempt < max_retries:
                    logger.warning(
                        f"Rate limited by server, retrying after {e.retry_after}s "
                        f"(attempt {attempt + 1}/{max_retries + 1})"
                    )
                    await asyncio.sleep(e.retry_after)
                    attempt += 1
                    continue
                logger.error(f"Rate limited by server (attempt {attempt + 1}/{max_retries + 1})")

            except (ServerError, DigikalaAPIError) as e:
                # Retry on 5xx errors and specific status codes
                last_exception = e
                if (
                    hasattr(e, 'status_code') and
                    e.status_code in self.config.retry_status_codes and
                    attempt < max_retries
                ):
                    retry_delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        f"Request failed with status {e.status_code}, "
                        f"retrying after {retry_delay}s (attempt {attempt + 1}/{max_retries + 1})"
                    )
                    await asyncio.sleep(retry_delay)
                    attempt += 1
                    continue
                logger.error(f"API error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")

            except httpx.HTTPError as e:
                last_exception = DigikalaAPIError(
                    f"HTTP error: {str(e)}",
                    response=str(e)
                )
                logger.error(f"HTTP error (attempt {attempt + 1}/{max_retries + 1}): {str(e)}")

            # Retry logic for network errors
            if attempt < max_retries:
                retry_delay = self._calculate_retry_delay(attempt)
                logger.warning(
                    f"Request failed, retrying after {retry_delay}s "
                    f"(attempt {attempt + 1}/{max_retries + 1})"
                )
                await asyncio.sleep(retry_delay)
                attempt += 1
            else:
                break

        # All retries exhausted
        if last_exception:
            raise last_exception
        raise DigikalaAPIError("Request failed after all retry attempts")

    def _calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate retry delay with exponential backoff.

        Args:
            attempt: Current attempt number (0-indexed)

        Returns:
            Delay in seconds before next retry

        Example:
            >>> # With retry_delay=1.0 and retry_backoff=2.0
            >>> self._calculate_retry_delay(0)  # Returns 1.0
            >>> self._calculate_retry_delay(1)  # Returns 2.0
            >>> self._calculate_retry_delay(2)  # Returns 4.0
        """
        return self.config.retry_delay * (self.config.retry_backoff ** attempt)

    def _generate_cache_key(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate a unique cache key for the request.

        The cache key is a hash of the endpoint and parameters,
        ensuring consistent caching across identical requests.

        Uses Blake2b for better collision resistance than MD5.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Blake2b hash string (16-byte digest) to use as cache key

        Example:
            >>> key = self._generate_cache_key("/v2/product/123/", {"lang": "fa"})
            >>> # Returns: "5d41402abc4b2a76b9719d911017c592"  (32 hex chars)
        """
        # Create a deterministic string representation
        params_str = json.dumps(params or {}, sort_keys=True)
        cache_string = f"{endpoint}?{params_str}"

        # Generate Blake2b hash (16-byte digest = 32 hex chars, same as MD5)
        # Blake2b is faster and has better collision resistance than MD5
        return hashlib.blake2b(cache_string.encode(), digest_size=16).hexdigest()

    async def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve response from cache.

        Args:
            cache_key: Unique cache key

        Returns:
            Cached response data or None if not found/expired

        Note:
            Logs cache hits and misses for monitoring purposes.
        """
        if self.cache is None:
            return None

        try:
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data
            else:
                logger.debug(f"Cache miss for key: {cache_key}")
                return None
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {str(e)}")
            return None

    async def _save_to_cache(
        self,
        cache_key: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Save response to cache.

        Args:
            cache_key: Unique cache key
            data: Response data to cache

        Note:
            Failures are logged but don't affect the request flow.
        """
        if self.cache is None:
            return

        try:
            await self.cache.set(cache_key, data)
            logger.debug(f"Cached response for key: {cache_key}")
        except Exception as e:
            logger.warning(f"Cache save failed: {str(e)}")

    def _raise_for_status(self, response: httpx.Response) -> None:
        """
        Raise appropriate exception based on HTTP status code.

        This method provides detailed error handling with proper exception
        types for different HTTP error scenarios.

        Args:
            response: HTTP response object

        Raises:
            BadRequestError: For 400 status codes
            UnauthorizedError: For 401 status codes
            ForbiddenError: For 403 status codes
            NotFoundError: For 404 status codes
            RateLimitError: For 429 status codes
            ServerError: For 5xx status codes
            DigikalaAPIError: For other error status codes
        """
        if response.is_success:
            return

        # Initialize error_data to None to avoid scope issues
        error_data = None
        try:
            error_data = response.json()
            error_message = error_data.get("message", response.text)
        except Exception:
            error_message = response.text or f"HTTP {response.status_code}"

        status_code = response.status_code

        if status_code == 400:
            raise BadRequestError(
                error_message,
                status_code=status_code,
                response=error_data
            )
        elif status_code == 401:
            raise UnauthorizedError(
                error_message,
                status_code=status_code,
                response=error_data
            )
        elif status_code == 403:
            raise ForbiddenError(
                error_message,
                status_code=status_code,
                response=error_data
            )
        elif status_code == 404:
            raise NotFoundError(
                error_message,
                status_code=status_code,
                response=error_data
            )
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                error_message,
                status_code=status_code,
                response=error_data,
                retry_after=int(retry_after) if retry_after else None
            )
        elif 500 <= status_code < 600:
            raise ServerError(
                error_message,
                status_code=status_code,
                response=error_data
            )
        else:
            raise DigikalaAPIError(
                error_message,
                status_code=status_code,
                response=error_data
            )

    def _validate_params(self, params: Dict[str, Any]) -> None:
        """
        Validate request parameters to prevent injection attacks and DoS.

        This method performs security checks on query parameters to detect
        and prevent common injection attack patterns including:
        - Path traversal (../)
        - Protocol injection (://)
        - XSS attempts (<script)
        - JavaScript injection (javascript:)
        - Null byte injection (\\x00)
        - Excessive parameter length (DoS protection)

        Args:
            params: Query parameters dictionary

        Raises:
            ValueError: If parameters contain suspicious content or exceed length limits

        Example:
            >>> self._validate_params({"id": "123"})  # OK
            >>> self._validate_params({"id": "../etc/passwd"})  # Raises ValueError
            >>> self._validate_params({"large": "x" * 300000})  # Raises ValueError
        """
        # Maximum allowed length for parameter keys and string values
        # 10KB should be sufficient for legitimate use cases
        MAX_PARAM_KEY_LENGTH = 512  # Parameter names should be short
        MAX_PARAM_VALUE_LENGTH = 200000  # 200KB for values

        # Suspicious patterns that might indicate injection attempts
        suspicious_patterns = [
            "../",  # Path traversal
            "://",  # Protocol injection
            "<script",  # XSS attempt
            "javascript:",  # JavaScript injection
            "\x00",  # Null byte injection
        ]

        for key, value in params.items():
            # Validate key
            if not isinstance(key, str):
                raise ValueError(f"Parameter key must be string, got {type(key).__name__}")

            if not key:
                raise ValueError("Parameter key cannot be empty")

            # Check key length (DoS protection)
            if len(key) > MAX_PARAM_KEY_LENGTH:
                raise ValueError(
                    f"Parameter key '{key[:50]}...' exceeds maximum length "
                    f"({MAX_PARAM_KEY_LENGTH} characters)"
                )

            # Check key for suspicious patterns
            key_lower = key.lower()
            for pattern in suspicious_patterns:
                if pattern in key_lower:
                    raise ValueError(
                        f"Suspicious pattern detected in parameter key: {key}"
                    )

            # Validate value if it's a string
            if isinstance(value, str):
                # Check value length (DoS protection)
                if len(value) > MAX_PARAM_VALUE_LENGTH:
                    raise ValueError(
                        f"Parameter value for '{key}' exceeds maximum length "
                        f"({MAX_PARAM_VALUE_LENGTH} characters)"
                    )

                value_lower = value.lower()
                for pattern in suspicious_patterns:
                    if pattern in value_lower:
                        raise ValueError(
                            f"Suspicious pattern detected in parameter value for '{key}': {value[:100]}"
                        )

            # Validate nested dictionaries recursively
            elif isinstance(value, dict):
                self._validate_params(value)

            # Validate lists
            elif isinstance(value, (list, tuple)):
                for item in value:
                    if isinstance(item, str):
                        # Check list item length (DoS protection)
                        if len(item) > MAX_PARAM_VALUE_LENGTH:
                            raise ValueError(
                                f"List item in parameter '{key}' exceeds maximum length "
                                f"({MAX_PARAM_VALUE_LENGTH} characters)"
                            )

                        item_lower = item.lower()
                        for pattern in suspicious_patterns:
                            if pattern in item_lower:
                                raise ValueError(
                                    f"Suspicious pattern detected in list item for '{key}': {item[:100]}"
                                )
                    elif isinstance(item, dict):
                        self._validate_params(item)