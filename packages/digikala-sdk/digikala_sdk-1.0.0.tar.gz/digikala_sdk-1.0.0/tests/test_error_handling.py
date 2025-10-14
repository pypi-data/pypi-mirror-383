"""Tests for error handling and APIStatusError."""

import pytest
from pydantic import BaseModel

from src.exceptions import APIStatusError
from src.models.common_models import BaseResponse
from src.models import (
    ProductDetailResponse,
    ProductSearchResponse,
    SellerProductListResponse,
)


class TestAPIStatusError:
    """Test APIStatusError exception class."""

    def test_api_status_error_basic(self):
        """Test basic APIStatusError creation."""
        error = APIStatusError(
            message="Test error",
            status_code=404
        )
        assert error.message == "Test error"
        assert error.status_code == 404
        assert str(error) == "[404] Test error"

    def test_api_status_error_from_response(self):
        """Test APIStatusError.from_response factory method."""
        error = APIStatusError.from_response(status=404)
        assert error.status_code == 404
        assert "Not Found" in error.message

        error = APIStatusError.from_response(status=500)
        assert error.status_code == 500
        assert "Internal Server Error" in error.message

    def test_api_status_error_with_response_data(self):
        """Test APIStatusError with response data."""
        response_data = {"status": 404, "message": "Product not found"}
        error = APIStatusError.from_response(
            status=404,
            response=response_data
        )
        assert error.response == response_data


class TestBaseResponseValidation:
    """Test BaseResponse status validation."""

    def test_base_response_success_status(self):
        """Test BaseResponse with status 200 succeeds."""

        class TestData(BaseModel):
            name: str
            value: int

        class TestResponse(BaseResponse[TestData]):
            pass

        # This should work fine
        response = TestResponse(
            status=200,
            data=TestData(name="test", value=42)
        )

        assert response.status == 200
        assert response.data.name == "test"
        assert response.data.value == 42

    def test_base_response_error_status_404(self):
        """Test BaseResponse with status 404 raises APIStatusError."""

        class TestData(BaseModel):
            name: str

        class TestResponse(BaseResponse[TestData]):
            pass

        # This should raise APIStatusError
        with pytest.raises(APIStatusError) as exc_info:
            TestResponse(status=404, data=None)

        assert exc_info.value.status_code == 404
        assert "Not Found" in str(exc_info.value)

    def test_base_response_error_status_500(self):
        """Test BaseResponse with status 500 raises APIStatusError."""

        class TestData(BaseModel):
            name: str

        class TestResponse(BaseResponse[TestData]):
            pass

        # This should raise APIStatusError
        with pytest.raises(APIStatusError) as exc_info:
            TestResponse(status=500, data=None)

        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in str(exc_info.value)

    def test_base_response_error_status_401(self):
        """Test BaseResponse with status 401 raises APIStatusError."""

        class TestData(BaseModel):
            name: str

        class TestResponse(BaseResponse[TestData]):
            pass

        # This should raise APIStatusError
        with pytest.raises(APIStatusError) as exc_info:
            TestResponse(status=401, data=None)

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)


class TestProductResponseValidation:
    """Test product response models validate status correctly."""

    def test_product_detail_response_error_status(self):
        """Test ProductDetailResponse raises error on non-200 status."""

        with pytest.raises(APIStatusError) as exc_info:
            ProductDetailResponse(status=404, data=None)

        assert exc_info.value.status_code == 404

    def test_product_search_response_error_status(self):
        """Test ProductSearchResponse raises error on non-200 status."""

        with pytest.raises(APIStatusError) as exc_info:
            ProductSearchResponse(status=500, data=None)

        assert exc_info.value.status_code == 500

    def test_seller_product_list_response_error_status(self):
        """Test SellerProductListResponse raises error on non-200 status."""

        with pytest.raises(APIStatusError) as exc_info:
            SellerProductListResponse(status=403, data=None)

        assert exc_info.value.status_code == 403


class TestErrorStatusCodes:
    """Test various HTTP status codes."""

    @pytest.mark.parametrize("status_code,expected_message", [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (403, "Forbidden"),
        (404, "Not Found"),
        (429, "Rate Limit"),
        (500, "Internal Server Error"),
        (502, "Bad Gateway"),
        (503, "Service Unavailable"),
    ])
    def test_various_status_codes(self, status_code, expected_message):
        """Test APIStatusError.from_response with various status codes."""
        error = APIStatusError.from_response(status=status_code)

        assert error.status_code == status_code
        assert expected_message in error.message

    def test_unknown_status_code(self):
        """Test APIStatusError with unknown status code."""
        error = APIStatusError.from_response(status=418)

        assert error.status_code == 418
        assert "418" in error.message