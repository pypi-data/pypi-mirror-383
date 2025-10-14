"""Products service for product-related API endpoints."""

from typing import Optional

from .base import BaseService
from ..models import ProductDetailResponse, ProductSearchResponse


class ProductsService(BaseService):
    """
    Service for product-related API operations.

    Example:
        ```python
        async with DigikalaClient(api_key="...") as client:
            # Get product details
            product = await client.products.get_product(id=12345)
            print(product.data.product.title_fa)

            # Search products
            search_results = await client.products.search(q="iphone", page=1)
            for product in search_results.data.products:
                print(product.title_fa)
        ```
    """

    async def get_product(self, id: int) -> ProductDetailResponse:
        """
        Get detailed product information by ID.

        Args:
            id: Product ID

        Returns:
            ProductDetailResponse containing full product details

        Raises:
            NotFoundError: If product with given ID does not exist
            DigikalaAPIError: For other API errors

        Example:
            ```python
            product = await client.products.get_product(id=12345)
            print(f"Title: {product.data.product.title_fa}")
            print(f"Price: {product.data.product.default_variant.price.selling_price}")
            print(f"Brand: {product.data.product.brand.title_fa}")
            ```
        """
        endpoint = f"/v2/product/{id}/"
        return await self._request(
            method="GET",
            endpoint=endpoint,
            response_model=ProductDetailResponse
        )

    async def search(
        self,
        q: str,
        page: Optional[int] = 1
    ) -> ProductSearchResponse:
        """
        Search for products by query string.

        Args:
            q: Search query string
            page: Page number for pagination (default: 1)

        Returns:
            ProductSearchResponse containing search results and pagination info

        Raises:
            BadRequestError: If query parameters are invalid
            DigikalaAPIError: For other API errors

        Example:
            ```python
            # Search for iPhone products
            results = await client.products.search(q="iphone", page=1)

            print(f"Total items: {results.data.pager.total_items}")
            print(f"Total pages: {results.data.pager.total_pages}")

            for product in results.data.products:
                print(f"- {product.title_fa}")
                print(f"  Price: {product.default_variant.price.selling_price}")
            ```
        """
        params = {
            "q": q,
            "page": page
        }
        return await self._request(
            method="GET",
            endpoint="/v1/search/",
            response_model=ProductSearchResponse,
            params=params
        )