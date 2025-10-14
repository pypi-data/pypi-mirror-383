"""Tests for the main client."""

import pytest

from src import DigikalaClient, DigikalaConfig
from src.exceptions import DigikalaAPIError


@pytest.mark.asyncio
async def test_client_context_manager():
    """Test client as async context manager."""
    config = DigikalaConfig(api_key="test-key")
    async with DigikalaClient(config=config) as client:
        assert client._http_client is not None
        assert client.config.api_key == "test-key"
    # After exit, client should be closed
    assert client._http_client is None


@pytest.mark.asyncio
async def test_client_manual_lifecycle():
    """Test manual client lifecycle management."""
    config = DigikalaConfig(api_key="test-key")
    client = DigikalaClient(config=config)

    # Client should not be opened yet
    assert client._http_client is None

    # Open client
    await client.open()
    assert client._http_client is not None

    # Close client
    await client.close()
    assert client._http_client is None


@pytest.mark.asyncio
async def test_client_service_access_without_open():
    """Test accessing services without opening client raises error."""
    config = DigikalaConfig(api_key="test-key")
    client = DigikalaClient(config=config)

    with pytest.raises(RuntimeError, match="Client is not opened"):
        _ = client.products

    with pytest.raises(RuntimeError, match="Client is not opened"):
        _ = client.sellers

    with pytest.raises(RuntimeError, match="Client is not opened"):
        _ = client.brands


@pytest.mark.asyncio
async def test_client_config_validation():
    """Test client configuration validation."""
    # Invalid timeout
    with pytest.raises(ValueError, match="timeout must be positive"):
        DigikalaConfig(timeout=-1)

    # Invalid max_retries
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        DigikalaConfig(max_retries=-1)

    # Invalid retry_delay
    with pytest.raises(ValueError, match="retry_delay must be positive"):
        DigikalaConfig(retry_delay=0)

    # Invalid retry_backoff
    with pytest.raises(ValueError, match="retry_backoff must be >= 1"):
        DigikalaConfig(retry_backoff=0.5)

    # Invalid max_connections
    with pytest.raises(ValueError, match="max_connections must be positive"):
        DigikalaConfig(max_connections=0)

    # Invalid max_keepalive_connections
    with pytest.raises(ValueError, match="max_keepalive_connections must be non-negative"):
        DigikalaConfig(max_keepalive_connections=-1)

    # max_keepalive_connections exceeds max_connections
    with pytest.raises(ValueError, match="max_keepalive_connections cannot exceed max_connections"):
        DigikalaConfig(max_connections=10, max_keepalive_connections=20)

    # Invalid keepalive_expiry
    with pytest.raises(ValueError, match="keepalive_expiry must be positive"):
        DigikalaConfig(keepalive_expiry=0)

    # Invalid rate_limit_requests
    with pytest.raises(ValueError, match="rate_limit_requests must be non-negative"):
        DigikalaConfig(rate_limit_requests=-5)

    # Invalid cache_config type
    with pytest.raises(ValueError, match="cache_config must be a dictionary"):
        DigikalaConfig(cache_config="invalid")

    # Invalid cache_config.enabled type
    with pytest.raises(ValueError, match="cache_config.enabled must be a boolean"):
        DigikalaConfig(cache_config={"enabled": "yes"})


def test_client_repr():
    """Test client string representation."""
    config = DigikalaConfig(api_key="test-key")
    client = DigikalaClient(config=config)

    repr_str = repr(client)
    assert "DigikalaClient" in repr_str
    assert "api.digikala.com" in repr_str
    assert "authenticated=True" in repr_str


def test_config_headers():
    """Test configuration header generation."""
    # With API key
    config1 = DigikalaConfig(api_key="test-api-key")
    headers1 = config1.get_headers()
    assert headers1["X-API-Key"] == "test-api-key"
    assert "Authorization" not in headers1

    # With bearer token
    config2 = DigikalaConfig(bearer_token="test-bearer-token")
    headers2 = config2.get_headers()
    assert headers2["Authorization"] == "Bearer test-bearer-token"
    assert "X-API-Key" not in headers2

    # With both (bearer token takes precedence)
    config3 = DigikalaConfig(api_key="api-key", bearer_token="bearer-token")
    headers3 = config3.get_headers()
    assert headers3["Authorization"] == "Bearer bearer-token"
    assert "X-API-Key" not in headers3


@pytest.mark.asyncio
async def test_client_brands_service():
    """Test accessing brands service."""
    config = DigikalaConfig(api_key="test-key")
    async with DigikalaClient(config=config) as client:
        # Access brands service
        brands_service = client.brands
        assert brands_service is not None

        # Second access should return same instance
        brands_service2 = client.brands
        assert brands_service is brands_service2


# HTTP Client Abstraction Tests
class TestHTTPClientAbstraction:
    """Tests for HTTP client abstraction layer."""

    @pytest.mark.asyncio
    async def test_httpx_adapter_wraps_client(self):
        """Test HttpxAdapter wraps httpx.AsyncClient correctly."""
        import httpx
        from src.implementations import HttpxAdapter
        from src.protocols import AsyncHTTPClient

        httpx_client = httpx.AsyncClient()
        adapter = HttpxAdapter(httpx_client)

        # Verify adapter implements AsyncHTTPClient protocol
        assert isinstance(adapter, AsyncHTTPClient)

        await adapter.aclose()

    @pytest.mark.asyncio
    async def test_httpx_adapter_request_method(self, respx_mock):
        """Test HttpxAdapter.request() method works correctly."""
        import httpx
        from src.implementations import HttpxAdapter

        # Mock API response
        respx_mock.get("https://test.com/api").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )

        httpx_client = httpx.AsyncClient()
        adapter = HttpxAdapter(httpx_client)

        # Make request through adapter
        response = await adapter.request("GET", "https://test.com/api")

        # Verify response implements HTTPResponse protocol
        assert response.status_code == 200
        assert response.is_success is True
        assert response.json() == {"status": "ok"}

        await adapter.aclose()

    @pytest.mark.asyncio
    async def test_httpx_adapter_with_params_and_json(self, respx_mock):
        """Test HttpxAdapter handles params and json body."""
        import httpx
        from src.implementations import HttpxAdapter

        # Mock API response
        respx_mock.post("https://test.com/api").mock(
            return_value=httpx.Response(201, json={"created": True})
        )

        httpx_client = httpx.AsyncClient()
        adapter = HttpxAdapter(httpx_client)

        # Make request with params and json
        response = await adapter.request(
            "POST",
            "https://test.com/api",
            params={"key": "value"},
            json={"data": "test"}
        )

        assert response.status_code == 201
        assert response.json() == {"created": True}

        await adapter.aclose()

    @pytest.mark.asyncio
    async def test_digikala_client_uses_httpx_adapter(self):
        """Test DigikalaClient uses HttpxAdapter internally."""
        from src.implementations import HttpxAdapter
        from src.protocols import AsyncHTTPClient

        config = DigikalaConfig(api_key="test-key")
        async with DigikalaClient(config=config) as client:
            # Verify _http_client is an AsyncHTTPClient
            assert isinstance(client._http_client, AsyncHTTPClient)
            # Verify it's specifically an HttpxAdapter
            assert isinstance(client._http_client, HttpxAdapter)

    @pytest.mark.asyncio
    async def test_services_accept_async_http_client(self):
        """Test services accept any AsyncHTTPClient implementation."""
        import httpx
        from src.implementations import HttpxAdapter
        from src.services import ProductsService

        config = DigikalaConfig(api_key="test-key")
        httpx_client = httpx.AsyncClient()
        adapter = HttpxAdapter(httpx_client)

        # Create service with adapter
        service = ProductsService(adapter, config)
        assert service is not None

        await adapter.aclose()

    @pytest.mark.asyncio
    async def test_base_service_depends_on_abstraction(self):
        """Test BaseService depends on AsyncHTTPClient, not httpx."""
        import httpx
        from src.implementations import HttpxAdapter
        from src.services.base import BaseService

        config = DigikalaConfig(api_key="test-key")
        httpx_client = httpx.AsyncClient()
        adapter = HttpxAdapter(httpx_client)

        # BaseService should accept AsyncHTTPClient
        service = BaseService(adapter, config)
        assert service is not None

        await adapter.aclose()

    @pytest.mark.asyncio
    async def test_http_response_protocol_compliance(self, respx_mock):
        """Test httpx.Response implements HTTPResponse protocol."""
        import httpx
        from src.protocols import HTTPResponse

        # Mock response
        respx_mock.get("https://test.com/test").mock(
            return_value=httpx.Response(
                200,
                json={"test": "data"},
                headers={"Content-Type": "application/json"}
            )
        )

        async with httpx.AsyncClient() as client:
            response = await client.get("https://test.com/test")

            # Verify httpx.Response implements HTTPResponse protocol
            assert isinstance(response, HTTPResponse)
            assert response.status_code == 200
            assert response.is_success is True
            assert "Content-Type" in response.headers
            assert response.json() == {"test": "data"}

    @pytest.mark.asyncio
    async def test_adapter_aclose_closes_underlying_client(self):
        """Test HttpxAdapter.aclose() closes the underlying httpx client."""
        import httpx
        from src.implementations import HttpxAdapter

        httpx_client = httpx.AsyncClient()
        adapter = HttpxAdapter(httpx_client)

        # Client should be open
        assert not httpx_client.is_closed

        await adapter.aclose()

        # Client should be closed after adapter.aclose()
        assert httpx_client.is_closed