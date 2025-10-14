"""Configuration management for Digikala SDK."""

from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class DigikalaConfig:
    """
    Configuration for Digikala API client.

    Attributes:
        base_url: Base URL for Digikala API (default: https://api.digikala.com)
        api_key: API key for authentication (optional)
        bearer_token: Bearer token for authentication (optional)
        timeout: Request timeout in seconds (default: 30.0)
        max_retries: Maximum number of retry attempts (default: 3)
        retry_delay: Initial retry delay in seconds (default: 1.0)
        retry_backoff: Exponential backoff multiplier (default: 2.0)
        retry_status_codes: HTTP status codes to retry (default: 429, 500, 502, 503, 504)
        max_connections: Maximum total connections in pool (default: 100)
        max_keepalive_connections: Maximum idle connections to keep (default: 20)
        keepalive_expiry: Seconds before idle connection expires (default: 30.0)
        rate_limit_requests: Maximum requests per minute (default: 100, 0 = disabled)
        cache_config: Optional response caching configuration (default: None)
    """

    base_url: str = "https://api.digikala.com"
    api_key: Optional[str] = None
    bearer_token: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    retry_status_codes: tuple = (429, 500, 502, 503, 504)

    # Connection pool configuration
    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 30.0

    # Rate limiting configuration
    rate_limit_requests: int = 100  # requests per minute, 0 = disabled

    # Cache configuration
    # Example configurations:
    # 1. Memory cache (simple):
    #    cache_config = {
    #        "enabled": True,
    #        "backend": "memory",
    #        "ttl": 300
    #    }
    #
    # 2. Redis cache (production):
    #    cache_config = {
    #        "enabled": True,
    #        "backend": "redis",
    #        "redis": {
    #            "endpoint": "localhost",
    #            "port": 6379
    #        },
    #        "ttl": 600
    #    }
    #
    # Fields:
    #   - enabled (bool, required): Enable/disable caching
    #   - backend (str, optional): "memory" (default) or "redis"
    #   - ttl (int, optional): Time-to-live in seconds (default: 300)
    #   - redis (dict, required if backend="redis"):
    #       - endpoint (str): Redis server hostname/IP
    #       - port (int): Redis server port (default: 6379)
    cache_config: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")
        if self.retry_backoff < 1:
            raise ValueError("retry_backoff must be >= 1")

        # Validate connection pool settings
        if self.max_connections <= 0:
            raise ValueError("max_connections must be positive")
        if self.max_keepalive_connections < 0:
            raise ValueError("max_keepalive_connections must be non-negative")
        if self.max_keepalive_connections > self.max_connections:
            raise ValueError("max_keepalive_connections cannot exceed max_connections")
        if self.keepalive_expiry <= 0:
            raise ValueError("keepalive_expiry must be positive")

        # Validate rate limiting settings
        if self.rate_limit_requests < 0:
            raise ValueError("rate_limit_requests must be non-negative")

        # Validate cache configuration if provided
        if self.cache_config:
            if not isinstance(self.cache_config, dict):
                raise ValueError("cache_config must be a dictionary")
            if "enabled" in self.cache_config and not isinstance(self.cache_config["enabled"], bool):
                raise ValueError("cache_config.enabled must be a boolean")

    def get_headers(self) -> dict:
        """
        Generate HTTP headers based on authentication configuration.

        Returns:
            Dictionary of HTTP headers
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["X-API-Key"] = self.api_key

        return headers