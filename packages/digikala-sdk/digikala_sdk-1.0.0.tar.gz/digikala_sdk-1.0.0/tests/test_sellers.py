"""Tests for sellers service."""

import pytest
import respx
from httpx import Response

from src.exceptions import NotFoundError


@pytest.mark.asyncio
@respx.mock
async def test_get_seller_products_success(client):
    """Test successful seller products retrieval."""
    seller_response = {
        "status": 200,
        "data": {
            "filters": {},
            "quick_filters": [],
            "products": [],
            "sort": {"default": 4},
            "sort_options": [],
            "did_you_mean": [],
            "related_search_words": [],
            "result_type": "no_change",
            "pager": {
                "current_page": 1,
                "total_pages": 3,
                "total_items": 50
            },
            "search_phase": 0,
            "qpm_api_version": None,
            "search_instead": [],
            "is_text_lenz_eligible": False,
            "text_lenz_eligibility": "nope",
            "search_version": None,
            "advertisement": {"sponsored_brands": []},
            "seller": {
                "id": 123456,
                "title": "Test Seller",
                "code": "TEST",
                "url": {"base": None, "uri": "/seller/TEST/"},
                "stars": 4.5,
                "registration_date": "1 year",
                "grade": {"label": "عالی", "color": "#00a049"},
                "icon": {
                    "storage_ids": {},
                    "url": [],
                    "thumbnail_url": None,
                    "temporary_id": None,
                    "webp_url": []
                },
                "rating": {
                    "total_rate": 85,
                    "total_count": 100,
                    "totally_satisfied": {"title": "کاملا راضی", "rate": 80, "rate_count": 80},
                    "satisfied": {"title": "راضی", "rate": 15, "rate_count": 15},
                    "neutral": {"title": "نظری ندارم", "rate": 3, "rate_count": 3},
                    "dissatisfied": {"title": "ناراضی", "rate": 1, "rate_count": 1},
                    "totally_dissatisfied": {"title": "کاملا ناراضی", "rate": 1, "rate_count": 1}
                },
                "statistics": {
                    "ship_on_time": 95.0,
                    "cancellation": 98.0,
                    "return": 99.0
                },
                "properties": {
                    "is_trusted": True,
                    "is_official": False,
                    "is_new": False
                }
            }
        }
    }

    route = respx.get(
        "https://api.digikala.com/v1/sellers/test-seller/",
        params={"page": 1}
    ).mock(return_value=Response(200, json=seller_response))

    result = await client.sellers.get_seller_products(sku="test-seller", page=1)

    assert route.called
    assert result.status == 200
    assert result.data.seller.id == 123456
    assert result.data.seller.title == "Test Seller"
    assert result.data.pager.total_items == 50


@pytest.mark.asyncio
@respx.mock
async def test_get_seller_info_success(client):
    """Test get_seller_info convenience method."""
    seller_response = {
        "status": 200,
        "data": {
            "filters": {},
            "quick_filters": [],
            "products": [],
            "sort": {"default": 4},
            "sort_options": [],
            "did_you_mean": [],
            "related_search_words": [],
            "result_type": "no_change",
            "pager": {
                "current_page": 1,
                "total_pages": 1,
                "total_items": 10
            },
            "search_phase": 0,
            "qpm_api_version": None,
            "search_instead": [],
            "is_text_lenz_eligible": False,
            "text_lenz_eligibility": "nope",
            "search_version": None,
            "advertisement": {"sponsored_brands": []},
            "seller": {
                "id": 789,
                "title": "Another Seller",
                "code": "ANOTH",
                "url": {"base": None, "uri": "/seller/ANOTH/"},
                "stars": 5.0,
                "registration_date": "2 years",
                "grade": {"label": "عالی", "color": "#00a049"},
                "icon": {
                    "storage_ids": {},
                    "url": [],
                    "thumbnail_url": None,
                    "temporary_id": None,
                    "webp_url": []
                },
                "rating": {
                    "total_rate": 95,
                    "total_count": 200,
                    "totally_satisfied": {"title": "کاملا راضی", "rate": 90, "rate_count": 180},
                    "satisfied": {"title": "راضی", "rate": 5, "rate_count": 10},
                    "neutral": {"title": "نظری ندارم", "rate": 3, "rate_count": 6},
                    "dissatisfied": {"title": "ناراضی", "rate": 1, "rate_count": 2},
                    "totally_dissatisfied": {"title": "کاملا ناراضی", "rate": 1, "rate_count": 2}
                },
                "statistics": {
                    "ship_on_time": 98.0,
                    "cancellation": 99.0,
                    "return": 99.5
                },
                "properties": {
                    "is_trusted": True,
                    "is_official": True,
                    "is_new": False
                }
            }
        }
    }

    route = respx.get(
        "https://api.digikala.com/v1/sellers/another-seller/",
        params={"page": 1}
    ).mock(return_value=Response(200, json=seller_response))

    result = await client.sellers.get_seller_info(sku="another-seller")

    assert route.called
    assert result.status == 200
    assert result.data.seller.id == 789


@pytest.mark.asyncio
@respx.mock
async def test_get_seller_not_found(client):
    """Test seller not found error."""
    respx.get(
        "https://api.digikala.com/v1/sellers/invalid-seller/",
        params={"page": 1}
    ).mock(return_value=Response(404, json={"message": "Seller not found"}))

    with pytest.raises(NotFoundError) as exc_info:
        await client.sellers.get_seller_products(sku="invalid-seller", page=1)

    assert exc_info.value.status_code == 404