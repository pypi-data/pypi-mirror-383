"""Tests for brands service."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from src import DigikalaClient
from src.exceptions import APIStatusError
from src.models import BrandProductsResponse, BrandData, BrandDetail


@pytest.fixture
def mock_http_client():
    """Create a mock HTTP client."""
    client = MagicMock()
    return client


@pytest.fixture
def sample_brand_response():
    """Sample brand API response data."""
    return {
        "status": 200,
        "data": {
            "filters": {},
            "quick_filters": [],
            "products": [
                {
                    "id": 123,
                    "title_fa": "محصول تستی",
                    "title_en": "Test Product",
                    "url": {"base": "https://digikala.com", "uri": "/product"},
                    "status": "marketable",
                    "has_quick_view": True,
                    "data_layer": {
                        "brand": "TestBrand",
                        "category": "Test",
                        "metric6": 1,
                        "dimension2": 1,
                        "dimension6": 1,
                        "dimension7": "test",
                        "dimension9": 1.0,
                        "dimension11": 1,
                        "dimension20": "test",
                        "item_category2": "test",
                        "item_category3": "test",
                        "item_category4": "test",
                        "item_category5": "test"
                    },
                    "product_type": "product",
                    "test_title_fa": "",
                    "test_title_en": "",
                    "digiplus": {
                        "services": [],
                        "service_list": [],
                        "services_summary": [],
                        "is_jet_eligible": False,
                        "cash_back": 0,
                        "is_general_location_jet_eligible": False
                    },
                    "images": {
                        "main": {
                            "storage_ids": [],
                            "url": ["https://example.com/image.jpg"],
                            "thumbnail_url": None,
                            "temporary_id": None,
                            "webp_url": []
                        }
                    },
                    "rating": {
                        "rate": 4.5,
                        "count": 10
                    },
                    "default_variant": [],
                    "colors": [],
                    "platforms": [],
                    "has_fresh_touchpoint": False,
                    "second_default_variant": [],
                    "properties": {
                        "is_fast_shipping": False,
                        "is_ship_by_seller": False,
                        "free_shipping_badge": False,
                        "is_multi_warehouse": False,
                        "is_fake": False,
                        "has_gift": False,
                        "min_price_in_last_month": 0,
                        "is_non_inventory": False,
                        "is_ad": False,
                        "ad": [],
                        "is_jet_eligible": False,
                        "is_medical_supplement": False
                    }
                }
            ],
            "sort": {},
            "sort_options": [],
            "did_you_mean": [],
            "related_search_words": [],
            "result_type": "brand",
            "pager": {
                "current_page": 1,
                "next_page": 2,
                "total_pages": 10,
                "total_items": 100
            },
            "search_phase": 1,
            "qpm_api_version": None,
            "search_instead": [],
            "is_text_lenz_eligible": False,
            "text_lenz_eligibility": "not_eligible",
            "search_version": None,
            "intrack": None,
            "seo": None,
            "advertisement": None,
            "brand": {
                "id": 1,
                "code": "test-brand",
                "title_fa": "برند تستی",
                "title_en": "Test Brand",
                "url": {"base": "https://digikala.com", "uri": "/brand"},
                "visibility": True,
                "logo": None,
                "is_premium": False,
                "is_miscellaneous": False,
                "is_name_similar": False,
                "description": "این یک برند تستی است"
            },
            "search_method": "default",
            "bigdata_tracker_data": None
        }
    }


class TestBrandsService:
    """Test brands service methods."""

    @pytest.mark.asyncio
    async def test_get_brand_products_success(self, sample_brand_response):
        """Test successful brand products retrieval."""
        # Create response object
        response = BrandProductsResponse(**sample_brand_response)

        assert response.status == 200
        assert response.data is not None
        assert isinstance(response.data, BrandData)
        assert isinstance(response.data.brand, BrandDetail)
        assert response.data.brand.title_fa == "برند تستی"
        assert response.data.brand.code == "test-brand"
        assert response.data.brand.description == "این یک برند تستی است"
        assert len(response.data.products) == 1
        assert response.data.pager.current_page == 1
        assert response.data.pager.total_items == 100

    @pytest.mark.asyncio
    async def test_get_brand_products_404(self):
        """Test brand not found error."""
        error_response = {
            "status": 404,
            "data": None
        }

        with pytest.raises(APIStatusError) as exc_info:
            BrandProductsResponse(**error_response)

        assert exc_info.value.status_code == 404
        assert "Not Found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_brand_model_with_nullable_fields(self):
        """Test brand model handles nullable fields correctly."""
        brand_data = {
            "id": 1,
            "code": "test",
            "title_fa": "تست",
            "title_en": "Test",
            "url": {"base": "https://test.com", "uri": "/test"},
            "visibility": True,
            "logo": None,
            "is_premium": False,
            "is_miscellaneous": False,
            "is_name_similar": False,
            "description": None  # Nullable field
        }

        brand = BrandDetail(**brand_data)
        assert brand.description is None
        assert brand.title_fa == "تست"

    @pytest.mark.asyncio
    async def test_brand_data_with_empty_arrays(self):
        """Test brand data handles empty arrays correctly."""
        brand_response = {
            "status": 200,
            "data": {
                "filters": {},
                "quick_filters": [],  # Empty array
                "products": [],  # Empty array
                "sort": {},
                "sort_options": [],  # Empty array
                "did_you_mean": [],  # Empty array
                "related_search_words": [],  # Empty array
                "result_type": "brand",
                "pager": {
                    "current_page": 1,
                    "next_page": None,
                    "total_pages": 0,
                    "total_items": 0
                },
                "search_phase": 1,
                "search_instead": [],  # Empty array
                "is_text_lenz_eligible": False,
                "text_lenz_eligibility": "not_eligible",
                "brand": {
                    "id": 1,
                    "code": "empty-brand",
                    "title_fa": "برند خالی",
                    "title_en": "Empty Brand",
                    "url": {"base": "https://digikala.com", "uri": "/brand"},
                    "visibility": True,
                    "is_premium": False,
                    "is_miscellaneous": False,
                    "is_name_similar": False
                },
                "search_method": "default"
            }
        }

        response = BrandProductsResponse(**brand_response)
        assert response.status == 200
        assert len(response.data.products) == 0
        assert len(response.data.quick_filters) == 0
        assert len(response.data.did_you_mean) == 0


    @pytest.mark.asyncio
    async def test_get_brand_info_alias(self, respx_mock, sample_brand_response):
        """Test get_brand_info is an alias for get_brand_products with page=1."""
        from src.services.brands import BrandsService
        from src.config import DigikalaConfig
        import httpx

        # Mock API response
        respx_mock.get("https://api.digikala.com/v1/brands/test-brand/").mock(
            return_value=httpx.Response(200, json=sample_brand_response)
        )

        config = DigikalaConfig(api_key="test-key")
        async with httpx.AsyncClient() as client:
            service = BrandsService(client, config)
            result = await service.get_brand_info("test-brand")

            assert result.status == 200
            assert result.data.brand.code == "test-brand"
            # Verify it uses page=1
            assert result.data.pager.current_page == 1


class TestBrandResponseValidation:
    """Test brand response validation."""

    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500, 502, 503])
    def test_brand_response_error_status(self, status_code):
        """Test BrandProductsResponse raises error on non-200 status."""
        with pytest.raises(APIStatusError) as exc_info:
            BrandProductsResponse(status=status_code, data=None)

        assert exc_info.value.status_code == status_code

    def test_brand_response_success_status(self, sample_brand_response):
        """Test BrandProductsResponse accepts status 200."""
        response = BrandProductsResponse(**sample_brand_response)

        assert response.status == 200
        assert response.data is not None


class TestBrandIntegration:
    """Integration tests for brands client usage."""

    def test_brand_detail_extends_brand_basic(self):
        """Test that BrandDetail extends Brand with description."""
        from src.models.product_models import Brand

        brand_data = {
            "id": 1,
            "code": "test",
            "title_fa": "تست",
            "title_en": "Test",
            "url": {"base": "https://test.com", "uri": "/test"},
            "visibility": True,
            "is_premium": False,
            "is_miscellaneous": False,
            "is_name_similar": False,
            "description": "Test description"
        }

        # BrandDetail should accept all Brand fields plus description
        brand = BrandDetail(**brand_data)
        assert brand.description == "Test description"
        assert brand.title_fa == "تست"
        assert brand.code == "test"

    def test_brand_with_advertisement(self, sample_brand_response):
        """Test brand data with advertisement section."""
        sample_brand_response["data"]["advertisement"] = {
            "sponsored_brands": {
                "brand1": {
                    "id": 1,
                    "code": "sponsored",
                    "title_fa": "برند اسپانسر",
                    "title_en": "Sponsored Brand",
                    "url": {"base": "https://test.com", "uri": "/"},
                    "visibility": True,
                    "is_premium": True,
                    "landing_url": "https://test.com"
                }
            }
        }

        response = BrandProductsResponse(**sample_brand_response)
        assert response.data.advertisement is not None
        assert response.data.advertisement.sponsored_brands is not None