"""Tests for input validation and security features."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel

from src.services.base import BaseService
from src.config import DigikalaConfig


class SimpleTestResponse(BaseModel):
    """Minimal response model for validation tests."""
    status: int
    data: dict


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    return MagicMock()


@pytest.fixture
def config():
    """Create a test configuration."""
    return DigikalaConfig(api_key="test-key")


@pytest.fixture
def base_service(mock_client, config):
    """Create a BaseService instance with mocked client."""
    return BaseService(mock_client, config)


class TestHTTPMethodValidation:
    """Test HTTP method validation."""

    @pytest.mark.asyncio
    async def test_valid_http_methods(self, base_service, mock_client):
        """Test that valid HTTP methods are accepted."""
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

        for method in valid_methods:
            # Mock successful response with simple test structure
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.is_success = True
            mock_response.json.return_value = {"status": 200, "data": {}}
            mock_client.request = AsyncMock(return_value=mock_response)

            # Should not raise ValueError
            try:
                await base_service._request(
                    method=method,
                    endpoint="/test",
                    response_model=SimpleTestResponse,
                )
            except ValueError as e:
                pytest.fail(f"Valid method {method} raised ValueError: {e}")

    @pytest.mark.asyncio
    async def test_invalid_http_method(self, base_service):
        """Test that invalid HTTP methods are rejected."""
        invalid_methods = ["INVALID", "TRACE", "CONNECT", "BREW", ""]

        for method in invalid_methods:
            with pytest.raises(ValueError, match="Invalid HTTP method"):
                await base_service._request(
                    method=method,
                    endpoint="/test",
                    response_model=SimpleTestResponse,
                )

    @pytest.mark.asyncio
    async def test_case_insensitive_method_validation(self, base_service, mock_client):
        """Test that HTTP method validation is case-insensitive."""
        # Mock successful response with simple test structure
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"status": 200, "data": {}}
        mock_client.request = AsyncMock(return_value=mock_response)

        # Lowercase method should work
        try:
            await base_service._request(
                method="get",
                endpoint="/test",
                response_model=SimpleTestResponse,
            )
        except ValueError:
            pytest.fail("Lowercase 'get' should be valid")


class TestEndpointValidation:
    """Test endpoint format validation."""

    @pytest.mark.asyncio
    async def test_valid_endpoints(self, base_service, mock_client):
        """Test that valid endpoints are accepted."""
        valid_endpoints = ["/test", "/v1/products", "/api/users/123"]

        # Mock successful response with simple test structure
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.is_success = True
        mock_response.json.return_value = {"status": 200, "data": {}}
        mock_client.request = AsyncMock(return_value=mock_response)

        for endpoint in valid_endpoints:
            try:
                await base_service._request(
                    method="GET",
                    endpoint=endpoint,
                    response_model=SimpleTestResponse,
                )
            except ValueError as e:
                pytest.fail(f"Valid endpoint {endpoint} raised ValueError: {e}")

    @pytest.mark.asyncio
    async def test_empty_endpoint(self, base_service):
        """Test that empty endpoint is rejected."""
        with pytest.raises(ValueError, match="Endpoint cannot be empty"):
            await base_service._request(
                method="GET",
                endpoint="",
                response_model=SimpleTestResponse,
            )

    @pytest.mark.asyncio
    async def test_endpoint_without_leading_slash(self, base_service):
        """Test that endpoint without leading slash is rejected."""
        invalid_endpoints = ["test", "v1/products", "api/users"]

        for endpoint in invalid_endpoints:
            with pytest.raises(ValueError, match="Endpoint must start with"):
                await base_service._request(
                    method="GET",
                    endpoint=endpoint,
                    response_model=SimpleTestResponse,
                )


class TestParameterValidation:
    """Test parameter validation for injection attacks."""

    def test_valid_parameters(self, base_service):
        """Test that valid parameters pass validation."""
        valid_params = {
            "page": 1,
            "q": "test query",
            "limit": 10,
            "filter": {"status": "active"},
            "tags": ["tag1", "tag2"],
        }

        # Should not raise ValueError
        try:
            base_service._validate_params(valid_params)
        except ValueError as e:
            pytest.fail(f"Valid parameters raised ValueError: {e}")

    def test_path_traversal_attack(self, base_service):
        """Test that path traversal attempts are blocked."""
        malicious_params = [
            {"file": "../etc/passwd"},
            {"path": "../../secrets"},
            {"dir": "../../../root"},
        ]

        for params in malicious_params:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)

    def test_protocol_injection_attack(self, base_service):
        """Test that protocol injection attempts are blocked."""
        malicious_params = [
            {"url": "http://evil.com"},
            {"redirect": "https://malicious.site"},
            {"link": "ftp://bad.server"},
        ]

        for params in malicious_params:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)

    def test_xss_attack(self, base_service):
        """Test that XSS attempts are blocked."""
        malicious_params = [
            {"comment": "<script>alert('xss')</script>"},
            {"text": "<SCRIPT>malicious()</SCRIPT>"},
            {"html": "<ScRiPt>hack()</ScRiPt>"},
        ]

        for params in malicious_params:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)

    def test_javascript_injection_attack(self, base_service):
        """Test that JavaScript injection attempts are blocked."""
        malicious_params = [
            {"onclick": "javascript:alert('xss')"},
            {"href": "JavaScript:malicious()"},
            {"action": "JAVASCRIPT:hack()"},
        ]

        for params in malicious_params:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)

    def test_null_byte_injection(self, base_service):
        """Test that null byte injection is blocked."""
        malicious_params = [
            {"file": "test\x00.txt"},
            {"path": "safe\x00../etc/passwd"},
        ]

        for params in malicious_params:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)

    def test_empty_parameter_key(self, base_service):
        """Test that empty parameter keys are rejected."""
        with pytest.raises(ValueError, match="Parameter key cannot be empty"):
            base_service._validate_params({"": "value"})

    def test_non_string_parameter_key(self, base_service):
        """Test that non-string parameter keys are rejected."""
        with pytest.raises(ValueError, match="Parameter key must be string"):
            base_service._validate_params({123: "value"})

    def test_nested_dict_validation(self, base_service):
        """Test that nested dictionaries are validated recursively."""
        malicious_params = {
            "filter": {
                "user": {
                    "path": "../etc/passwd"
                }
            }
        }

        with pytest.raises(ValueError, match="Suspicious pattern detected"):
            base_service._validate_params(malicious_params)

    def test_list_validation(self, base_service):
        """Test that list items are validated."""
        malicious_params = {
            "urls": [
                "https://safe.com",
                "../etc/passwd",  # Malicious item
                "https://another-safe.com"
            ]
        }

        with pytest.raises(ValueError, match="Suspicious pattern detected"):
            base_service._validate_params(malicious_params)

    def test_case_insensitive_pattern_detection(self, base_service):
        """Test that suspicious patterns are detected case-insensitively."""
        malicious_params = [
            {"script": "<SCRIPT>alert()</SCRIPT>"},
            {"js": "JavaScript:hack()"},
            {"path": "../ETC/passwd"},
        ]

        for params in malicious_params:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)


class TestConnectionPoolLimits:
    """Test connection pool configuration."""

    @pytest.mark.asyncio
    async def test_connection_pool_limits_configured(self):
        """Test that connection pool limits are properly configured."""
        import httpx
        from unittest.mock import patch
        from src import DigikalaClient

        # Mock httpx.AsyncClient to capture initialization arguments
        with patch('httpx.AsyncClient') as mock_async_client:
            # Create a mock instance to return
            mock_instance = MagicMock()
            mock_instance.aclose = AsyncMock()
            mock_async_client.return_value = mock_instance

            client = DigikalaClient(api_key="test-key")
            await client.open()

            # Verify AsyncClient was called with correct limits
            mock_async_client.assert_called_once()
            call_kwargs = mock_async_client.call_args[1]

            assert 'limits' in call_kwargs
            limits = call_kwargs['limits']
            assert isinstance(limits, httpx.Limits)
            assert limits.max_connections == 100
            assert limits.max_keepalive_connections == 20
            assert limits.keepalive_expiry == 30.0

            await client.close()

    @pytest.mark.asyncio
    async def test_connection_pool_prevents_exhaustion(self):
        """Test that connection pool limits prevent resource exhaustion."""
        import httpx
        from unittest.mock import patch
        from src import DigikalaClient

        # Mock httpx.AsyncClient to capture initialization arguments
        with patch('httpx.AsyncClient') as mock_async_client:
            mock_instance = MagicMock()
            mock_instance.aclose = AsyncMock()
            mock_async_client.return_value = mock_instance

            client = DigikalaClient(api_key="test-key")
            await client.open()

            # Verify limits prevent resource exhaustion
            call_kwargs = mock_async_client.call_args[1]
            limits = call_kwargs['limits']

            # Verify that max_connections is a reasonable limit
            assert limits.max_connections > 0
            assert limits.max_connections <= 1000

            # Verify keepalive settings
            assert limits.max_keepalive_connections > 0
            assert limits.max_keepalive_connections < limits.max_connections

            await client.close()