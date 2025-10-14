"""Sellers service for seller-related API endpoints."""

from typing import Optional

from .base import BaseService
from ..models import SellerProductListResponse


class SellersService(BaseService):
    """
    Service for seller-related API operations.

    Example:
        ```python
        async with DigikalaClient(api_key="...") as client:
            # Get seller products
            seller_data = await client.sellers.get_seller_products(
                sku="seller-sku-code",
                page=1
            )
            print(seller_data.data.seller.title)
            for product in seller_data.data.products:
                print(product.title_fa)
        ```
    """

    async def get_seller_products(
        self,
        sku: str,
        page: Optional[int] = 1
    ) -> SellerProductListResponse:
        """
        Get seller information and their product list.

        Args:
            sku: Seller SKU (unique seller identifier)
            page: Page number for pagination (default: 1)

        Returns:
            SellerProductListResponse containing seller info and products

        Raises:
            NotFoundError: If seller with given SKU does not exist
            DigikalaAPIError: For other API errors

        Example:
            ```python
            seller_data = await client.sellers.get_seller_products(
                sku="seller-sku-code",
                page=1
            )

            # Access seller information
            seller = seller_data.data.seller
            print(f"Seller: {seller.title}")
            print(f"Rating: {seller.stars}/5")
            print(f"Total ratings: {seller.rating.total_count}")

            # Access products
            print(f"\\nProducts (Page {seller_data.data.pager.current_page}):")
            for product in seller_data.data.products:
                print(f"- {product.title_fa}")
                print(f"  Price: {product.default_variant.price.selling_price}")

            # Pagination info
            print(f"\\nTotal pages: {seller_data.data.pager.total_pages}")
            print(f"Total items: {seller_data.data.pager.total_items}")
            ```
        """
        params = {
            "page": page
        }
        endpoint = f"/v1/sellers/{sku}/"
        return await self._request(
            method="GET",
            endpoint=endpoint,
            response_model=SellerProductListResponse,
            params=params
        )

    async def get_seller_info(self, sku: str) -> SellerProductListResponse:
        """
        Get seller information (alias for get_seller_products with page 1).

        This is a convenience method for when you only need seller information.

        Args:
            sku: Seller SKU (unique seller identifier)

        Returns:
            SellerProductListResponse containing seller info and first page of products

        Raises:
            NotFoundError: If seller with given SKU does not exist
            DigikalaAPIError: For other API errors

        Example:
            ```python
            seller_data = await client.sellers.get_seller_info(sku="seller-sku-code")
            seller = seller_data.data.seller
            print(f"Seller: {seller.title}")
            print(f"Registration: {seller.registration_date}")
            ```
        """
        return await self.get_seller_products(sku=sku, page=1)