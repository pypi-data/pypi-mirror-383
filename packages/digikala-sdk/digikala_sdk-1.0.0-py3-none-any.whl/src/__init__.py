"""
Digikala SDK - Asynchronous Python SDK for Digikala API
========================================================

A production-grade, fully asynchronous SDK for integrating with Digikala's e-commerce API.

Features:
    - Fully asynchronous using httpx
    - Automatic retry logic with exponential backoff
    - Comprehensive error handling
    - Type-safe with Pydantic models
    - Extensive logging support
    - Easy integration with FastAPI

Quick Start:
    ```python
    import asyncio
    from src import DigikalaClient

    async def main():
        async with DigikalaClient(api_key="your-api-key") as client:
            # Get product details
            product = await client.products.get_product(id=12345)
            print(f"Product: {product.data.product.title_fa}")

            # Search products
            results = await client.products.search(q="laptop", page=1)
            for product in results.data.products:
                print(f"- {product.title_fa}")

            # Get seller products
            seller_data = await client.sellers.get_seller_products(
                id=123456,
                page=1
            )
            print(f"Seller: {seller_data.data.seller.title}")

    asyncio.run(main())
    ```

FastAPI Integration:
    ```python
    from fastapi import FastAPI, Depends
    from src import DigikalaClient, DigikalaConfig

    app = FastAPI()

    config = DigikalaConfig(api_key="your-api-key")
    client = DigikalaClient(config=config)

    @app.on_event("startup")
    async def startup():
        await client.open()

    @app.on_event("shutdown")
    async def shutdown():
        await client.close()

    @app.get("/products/{product_id}")
    async def get_product(product_id: int):
        product = await client.products.get_product(id=product_id)
        return product.data.product
    ```
"""

__version__ = "1.0.0"
__author__ = "Digikala SDK Team"

from .client import DigikalaClient
from .config import DigikalaConfig
from .exceptions import (
    DigikalaAPIError,
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError,
    ValidationError,
    APIStatusError,
)
from .models import (
    # Product models
    Product,
    ProductDetail,
    ProductDetailResponse,
    # Search models
    ProductSearchResponse,
    SearchData,
    # Seller models
    SellerProductListResponse,
    SellerData,
    SellerDetail,
    # Common models
    Price,
    Seller,
    Rating,
    Color,
    Images,
)

__all__ = [
    # Main client
    "DigikalaClient",
    "DigikalaConfig",
    # Exceptions
    "DigikalaAPIError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
    "TimeoutError",
    "ConnectionError",
    "ValidationError",
    "APIStatusError",
    # Models
    "Product",
    "ProductDetail",
    "ProductDetailResponse",
    "ProductSearchResponse",
    "SearchData",
    "SellerProductListResponse",
    "SellerData",
    "SellerDetail",
    "Price",
    "Seller",
    "Rating",
    "Color",
    "Images",
]