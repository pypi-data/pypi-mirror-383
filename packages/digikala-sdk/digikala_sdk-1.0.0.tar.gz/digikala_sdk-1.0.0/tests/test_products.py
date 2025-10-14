"""Tests for products service."""

import pytest
import respx
from httpx import Response

from src import DigikalaClient
from src.exceptions import NotFoundError, RateLimitError


@pytest.mark.asyncio
@respx.mock
async def test_get_product_success(client, sample_product_response):
    """Test successful product retrieval."""
    route = respx.get(
        "https://api.digikala.com/v2/product/12345/"
    ).mock(return_value=Response(200, json=sample_product_response))

    result = await client.products.get_product(id=12345)

    assert route.called
    assert result.status == 200
    assert result.data.product.id == 12345
    assert result.data.product.title_fa == "تست محصول"


@pytest.mark.asyncio
@respx.mock
async def test_get_product_not_found(client):
    """Test product not found error."""
    respx.get(
        "https://api.digikala.com/v2/product/99999/"
    ).mock(return_value=Response(404, json={"message": "Product not found"}))

    with pytest.raises(NotFoundError) as exc_info:
        await client.products.get_product(id=99999)

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@respx.mock
async def test_search_products_success(client):
    """Test successful product search."""
    search_response = {
        "status": 200,
        "data": {
            "filters": {},
            "quick_filters": [],
            "products": [],
            "sort": {"default": 22},
            "sort_options": [],
            "did_you_mean": [],
            "related_search_words": [],
            "result_type": "no_change",
            "pager": {
                "current_page": 1,
                "total_pages": 5,
                "total_items": 100
            },
            "search_phase": 0,
            "qpm_api_version": None,
            "search_instead": [],
            "is_text_lenz_eligible": False,
            "text_lenz_eligibility": "nope",
            "search_version": None,
            "advertisement": {"sponsored_brands": []},
            "search_method": "default"
        }
    }

    route = respx.get(
        "https://api.digikala.com/v1/search/",
        params={"q": "laptop", "page": 1}
    ).mock(return_value=Response(200, json=search_response))

    result = await client.products.search(q="laptop", page=1)

    assert route.called
    assert result.status == 200
    assert result.data.pager.total_items == 100
    assert result.data.pager.total_pages == 5


@pytest.mark.asyncio
@respx.mock
async def test_rate_limit_retry(client):
    """Test retry logic for rate limit errors."""
    # Return 429 three times to exhaust all retries (initial + 2 retries)
    route = respx.get(
        "https://api.digikala.com/v2/product/12345/"
    )
    route.side_effect = [
        Response(429, json={"message": "Rate limit exceeded"}),
        Response(429, json={"message": "Rate limit exceeded"}),
        Response(429, json={"message": "Rate limit exceeded"})
    ]

    # This should raise RateLimitError after retries
    with pytest.raises(RateLimitError):
        await client.products.get_product(id=12345)