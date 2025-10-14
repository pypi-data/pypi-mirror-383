"""Brands service for brand-related API endpoints."""

from typing import Optional

from .base import BaseService
from ..models import BrandProductsResponse


class BrandsService(BaseService):
    """
    Service for brand-related API operations.

    Example:
        ```python
        async with DigikalaClient(api_key="...") as client:
            # Get brand products
            brand_data = await client.brands.get_brand_products(
                code="zarin-iran",
                page=1
            )
            print(brand_data.data.brand.title_fa)
            for product in brand_data.data.products:
                print(product.title_fa)
        ```
    """

    async def get_brand_products(
        self,
        code: str,
        page: Optional[int] = 1
    ) -> BrandProductsResponse:
        """
        Get brand information and their product list.

        Args:
            code: Brand code (unique brand identifier)
            page: Page number for pagination (default: 1)

        Returns:
            BrandProductsResponse containing brand info and products

        Raises:
            APIStatusError: If brand with given code does not exist (status 404)
            DigikalaAPIError: For other API errors

        Example:
            ```python
            brand_data = await client.brands.get_brand_products(
                code="zarin-iran",
                page=1
            )

            # Access brand information
            brand = brand_data.data.brand
            print(f"Brand: {brand.title_fa}")
            print(f"Description: {brand.description}")

            # Access products
            print(f"\\nProducts (Page {brand_data.data.pager.current_page}):")
            for product in brand_data.data.products:
                print(f"- {product.title_fa}")
                if product.default_variant and product.default_variant.price:
                    price = product.default_variant.price.selling_price
                    print(f"  Price: {price:,} Rials")

            # Pagination info
            print(f"\\nTotal pages: {brand_data.data.pager.total_pages}")
            print(f"Total items: {brand_data.data.pager.total_items}")
            ```
        """
        params = {
            "page": page
        }
        endpoint = f"/v1/brands/{code}/"
        return await self._request(
            method="GET",
            endpoint=endpoint,
            response_model=BrandProductsResponse,
            params=params
        )

    async def get_brand_info(self, code: str) -> BrandProductsResponse:
        """
        Get brand information (alias for get_brand_products with page 1).

        This is a convenience method for when you only need brand information.

        Args:
            code: Brand code (unique brand identifier)

        Returns:
            BrandProductsResponse containing brand info and first page of products

        Raises:
            APIStatusError: If brand with given code does not exist (status 404)
            DigikalaAPIError: For other API errors

        Example:
            ```python
            brand_data = await client.brands.get_brand_info(code="zarin-iran")
            brand = brand_data.data.brand
            print(f"Brand: {brand.title_fa}")
            print(f"Code: {brand.code}")
            ```
        """
        return await self.get_brand_products(code=code, page=1)