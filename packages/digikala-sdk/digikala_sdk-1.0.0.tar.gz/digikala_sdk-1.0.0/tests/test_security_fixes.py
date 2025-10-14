"""Tests for security fixes applied to BaseService.

This test module verifies:
1. Fixed error_data scope issue in _raise_for_status()
2. Blake2b cache key generation
3. Input length validation (DoS protection)
"""

import pytest
import httpx
from unittest.mock import Mock, AsyncMock

from src.services.base import BaseService
from src.config import DigikalaConfig
from src.exceptions import (
    BadRequestError,
    NotFoundError,
    ServerError,
)


@pytest.fixture
def base_config():
    """Create a basic configuration for testing."""
    return DigikalaConfig(
        base_url="https://api.digikala.com",
        api_key="test-key",
        timeout=10.0,
        max_retries=0,  # Disable retries for testing
    )


@pytest.fixture
def mock_client():
    """Create a mock HTTP client."""
    client = Mock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def base_service(mock_client, base_config):
    """Create a BaseService instance for testing."""
    return BaseService(mock_client, base_config)


class TestErrorDataScopeFix:
    """Test that error_data is properly initialized (fix for locals() antipattern)."""

    def test_error_data_none_when_json_parsing_fails(self, base_service):
        """Verify error_data is None when response.json() raises exception."""
        # Create a mock response that fails JSON parsing
        response = Mock(spec=httpx.Response)
        response.is_success = False
        response.status_code = 400
        response.text = "<html>Bad Request</html>"
        response.json = Mock(side_effect=ValueError("Invalid JSON"))

        # Should raise BadRequestError with error_data=None
        with pytest.raises(BadRequestError) as exc_info:
            base_service._raise_for_status(response)

        error = exc_info.value
        assert error.status_code == 400
        assert error.response is None  # Should be None, not undefined
        assert "Bad Request" in str(error) or "HTTP 400" in str(error)

    def test_error_data_populated_when_json_valid(self, base_service):
        """Verify error_data contains parsed JSON when valid."""
        response = Mock(spec=httpx.Response)
        response.is_success = False
        response.status_code = 404
        response.text = "Not Found"
        response.json = Mock(return_value={"message": "Product not found", "code": "NOT_FOUND"})

        with pytest.raises(NotFoundError) as exc_info:
            base_service._raise_for_status(response)

        error = exc_info.value
        assert error.status_code == 404
        assert error.response == {"message": "Product not found", "code": "NOT_FOUND"}
        assert "Product not found" in str(error)

    def test_all_status_codes_handle_none_error_data(self, base_service):
        """Verify all error status codes handle None error_data correctly."""
        test_cases = [
            (400, BadRequestError),
            (401, BadRequestError),  # Will raise BadRequestError via base class
            (403, BadRequestError),
            (404, NotFoundError),
            (500, ServerError),
            (502, ServerError),
            (503, ServerError),
        ]

        for status_code, expected_exception in test_cases:
            response = Mock(spec=httpx.Response)
            response.is_success = False
            response.status_code = status_code
            response.text = f"Error {status_code}"
            response.json = Mock(side_effect=ValueError("Invalid JSON"))
            response.headers = Mock(spec=httpx.Headers)
            response.headers.get = Mock(return_value=None)

            with pytest.raises(Exception) as exc_info:
                base_service._raise_for_status(response)

            # Should not raise NameError for undefined error_data
            assert exc_info.value.status_code == status_code
            # error_data should be None when JSON parsing fails
            assert exc_info.value.response is None


class TestBlake2bCacheKeys:
    """Test Blake2b hash function for cache key generation."""

    def test_blake2b_produces_32_char_hex(self, base_service):
        """Verify Blake2b with digest_size=16 produces 32-character hex string."""
        cache_key = base_service._generate_cache_key(
            "/v2/product/123/",
            {"lang": "fa"}
        )

        # 16 bytes = 32 hex characters
        assert len(cache_key) == 32
        assert all(c in "0123456789abcdef" for c in cache_key)

    def test_different_endpoints_different_keys(self, base_service):
        """Verify different endpoints produce different cache keys."""
        key1 = base_service._generate_cache_key("/v2/product/1/", None)
        key2 = base_service._generate_cache_key("/v2/product/2/", None)

        assert key1 != key2

    def test_different_params_different_keys(self, base_service):
        """Verify different parameters produce different cache keys."""
        key1 = base_service._generate_cache_key("/v1/search/", {"q": "laptop"})
        key2 = base_service._generate_cache_key("/v1/search/", {"q": "phone"})

        assert key1 != key2

    def test_same_params_same_key(self, base_service):
        """Verify identical requests produce identical cache keys."""
        key1 = base_service._generate_cache_key(
            "/v1/search/",
            {"q": "test", "page": 1}
        )
        key2 = base_service._generate_cache_key(
            "/v1/search/",
            {"q": "test", "page": 1}
        )

        assert key1 == key2

    def test_param_order_irrelevant(self, base_service):
        """Verify parameter order doesn't affect cache key (sorted internally)."""
        key1 = base_service._generate_cache_key(
            "/v1/search/",
            {"page": 1, "q": "test"}
        )
        key2 = base_service._generate_cache_key(
            "/v1/search/",
            {"q": "test", "page": 1}
        )

        # Should be identical due to sorted keys in json.dumps
        assert key1 == key2

    def test_none_params_handled(self, base_service):
        """Verify None parameters don't cause errors."""
        cache_key = base_service._generate_cache_key("/v2/product/123/", None)

        assert len(cache_key) == 32
        assert all(c in "0123456789abcdef" for c in cache_key)


class TestInputLengthValidation:
    """Test input length limits for DoS protection."""

    def test_normal_params_accepted(self, base_service):
        """Verify normal-sized parameters are accepted."""
        params = {
            "id": "12345",
            "q": "laptop",
            "page": 1,
            "sort": "price"
        }

        # Should not raise
        base_service._validate_params(params)

    def test_oversized_key_rejected(self, base_service):
        """Verify parameter keys exceeding 512 chars are rejected."""
        params = {"x" * 600: "value"}  # 600 > 512

        with pytest.raises(ValueError) as exc_info:
            base_service._validate_params(params)

        assert "exceeds maximum length" in str(exc_info.value)
        assert "512" in str(exc_info.value)

    def test_oversized_value_rejected(self, base_service):
        """Verify parameter values exceeding 200KB are rejected."""
        params = {"key": "x" * 250000}  # 250KB > 200KB

        with pytest.raises(ValueError) as exc_info:
            base_service._validate_params(params)

        assert "exceeds maximum length" in str(exc_info.value)
        assert "200000" in str(exc_info.value)

    def test_legitimate_large_value_accepted(self, base_service):
        """Verify values under 200KB are accepted."""
        params = {"description": "x" * 100000}  # 100KB, should pass

        # Should not raise
        base_service._validate_params(params)

    def test_max_key_length_boundary(self, base_service):
        """Test boundary condition at exactly 512 characters."""
        # Exactly 512 chars - should be accepted
        params = {"x" * 512: "value"}
        base_service._validate_params(params)

        # 513 chars - should be rejected
        params = {"x" * 513: "value"}
        with pytest.raises(ValueError, match="exceeds maximum length"):
            base_service._validate_params(params)

    def test_max_value_length_boundary(self, base_service):
        """Test boundary condition at exactly 200KB."""
        # Exactly 200KB - should be accepted
        params = {"key": "x" * 200000}
        base_service._validate_params(params)

        # 200001 chars - should be rejected
        params = {"key": "x" * 200001}
        with pytest.raises(ValueError, match="exceeds maximum length"):
            base_service._validate_params(params)

    def test_oversized_list_item_rejected(self, base_service):
        """Verify oversized items in lists are rejected."""
        params = {
            "items": ["normal", "x" * 250000, "also_normal"]  # One oversized item
        }

        with pytest.raises(ValueError) as exc_info:
            base_service._validate_params(params)

        assert "exceeds maximum length" in str(exc_info.value)

    def test_nested_dict_with_oversized_value(self, base_service):
        """Verify nested dictionaries are recursively validated."""
        params = {
            "filter": {
                "category": "electronics",
                "description": "x" * 250000  # Oversized nested value
            }
        }

        with pytest.raises(ValueError, match="exceeds maximum length"):
            base_service._validate_params(params)


class TestCombinedSecurityValidation:
    """Test combined security checks (injection + length)."""

    def test_injection_still_caught_before_length(self, base_service):
        """Verify injection patterns are still caught."""
        # Short malicious string
        params = {"path": "../../../etc/passwd"}

        with pytest.raises(ValueError, match="Suspicious pattern detected"):
            base_service._validate_params(params)

    def test_xss_in_long_string_caught(self, base_service):
        """Verify injection patterns in long (but acceptable) strings are caught."""
        # Long string with XSS attempt (under 200KB limit)
        malicious = "x" * 1000 + "<script>alert('xss')</script>" + "x" * 1000

        params = {"content": malicious}

        with pytest.raises(ValueError, match="Suspicious pattern detected"):
            base_service._validate_params(params)

    def test_protocol_injection_in_url_param(self, base_service):
        """Verify protocol injection is caught."""
        params = {"redirect": "http://evil.com/payload"}

        with pytest.raises(ValueError, match="Suspicious pattern detected"):
            base_service._validate_params(params)

    def test_null_byte_injection_caught(self, base_service):
        """Verify null byte injection is caught."""
        params = {"filename": "file.txt\x00.jpg"}

        with pytest.raises(ValueError, match="Suspicious pattern detected"):
            base_service._validate_params(params)


class TestBackwardCompatibility:
    """Ensure fixes don't break existing functionality."""

    def test_success_response_unchanged(self, base_service):
        """Verify successful responses are not affected by fixes."""
        response = Mock(spec=httpx.Response)
        response.is_success = True

        # Should return immediately without raising
        result = base_service._raise_for_status(response)
        assert result is None

    def test_cache_key_format_unchanged(self, base_service):
        """Verify cache key format is still 32-char hex (same as MD5)."""
        cache_key = base_service._generate_cache_key("/test", {"a": "b"})

        # Still 32 characters, still hex - compatible with existing caches
        assert len(cache_key) == 32
        assert all(c in "0123456789abcdef" for c in cache_key)

    def test_normal_validation_still_works(self, base_service):
        """Verify existing validation patterns still work."""
        # These should all still be caught
        test_cases = [
            {"key": "../path"},
            {"key": "javascript:alert(1)"},
            {"key": "<script>"},
        ]

        for params in test_cases:
            with pytest.raises(ValueError, match="Suspicious pattern detected"):
                base_service._validate_params(params)