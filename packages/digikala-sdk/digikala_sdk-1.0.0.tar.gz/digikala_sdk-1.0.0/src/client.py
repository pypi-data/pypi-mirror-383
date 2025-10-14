"""Main Digikala API client."""

import logging
from typing import Optional

import httpx

from .config import DigikalaConfig
from .implementations import HttpxAdapter
from .protocols import AsyncHTTPClient
from .services import BrandsService, ProductsService, SellersService

logger = logging.getLogger(__name__)


class DigikalaClient:
    """
    Main asynchronous client for Digikala API.

    This client provides access to all Digikala API services through
    a unified interface with automatic connection management, retry logic,
    and error handling.

    Attributes:
        products: Service for product-related operations
        sellers: Service for seller-related operations
        brands: Service for brand-related operations

    Example:
        ```python
        # Basic usage with context manager (recommended)
        async with DigikalaClient(api_key="your-api-key") as client:
            product = await client.products.get_product(id=12345)
            print(product.data.product.title_fa)

        # Manual lifecycle management
        client = DigikalaClient(api_key="your-api-key")
        await client.open()
        try:
            product = await client.products.get_product(id=12345)
        finally:
            await client.close()

        # Custom configuration
        config = DigikalaConfig(
            base_url="https://api.digikala.com",
            api_key="your-api-key",
            timeout=60.0,
            max_retries=5,
            max_connections=200,
            max_keepalive_connections=50
        )
        async with DigikalaClient(config=config) as client:
            results = await client.products.search(q="laptop")
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        config: Optional[DigikalaConfig] = None,
        **config_kwargs
    ):
        """
        Initialize Digikala API client.

        Args:
            api_key: API key for authentication (optional)
            bearer_token: Bearer token for authentication (optional)
            config: Pre-configured DigikalaConfig instance (optional)
            **config_kwargs: Additional configuration parameters passed to DigikalaConfig

        Raises:
            ValueError: If configuration is invalid

        Note:
            If both `config` and individual parameters are provided,
            the `config` parameter takes precedence.
        """
        if config is None:
            config = DigikalaConfig(
                api_key=api_key,
                bearer_token=bearer_token,
                **config_kwargs
            )
        self.config = config

        self._http_client: Optional[AsyncHTTPClient] = None
        self._products_service: Optional[ProductsService] = None
        self._sellers_service: Optional[SellersService] = None
        self._brands_service: Optional[BrandsService] = None

        logger.info(
            f"Initialized DigikalaClient with base_url={self.config.base_url}"
        )

    async def open(self) -> None:
        """
        Open the HTTP client connection.

        This method is called automatically when using the client as a context manager.
        If managing the client lifecycle manually, call this before making any requests.

        Example:
            ```python
            client = DigikalaClient(api_key="your-key")
            await client.open()
            try:
                # Use client
                 هست = await client.products.get_product(id=123)
            finally:
                await client.close()
            ```
        """
        if self._http_client is None:
            # Configure connection pool limits to prevent resource exhaustion
            limits = httpx.Limits(
                max_connections=self.config.max_connections,
                max_keepalive_connections=self.config.max_keepalive_connections,
                keepalive_expiry=self.config.keepalive_expiry,
            )

            # Create httpx client and wrap with adapter for protocol-based design
            httpx_client = httpx.AsyncClient(
                headers=self.config.get_headers(),
                timeout=httpx.Timeout(self.config.timeout),
                follow_redirects=True,
                limits=limits,
            )
            self._http_client = HttpxAdapter(httpx_client)
            logger.debug(
                "HTTP client opened with connection pool "
                f"(max={limits.max_connections}, keepalive={limits.max_keepalive_connections})"
            )

    async def close(self) -> None:
        """
        Close the HTTP client connection.

        This method is called automatically when exiting the context manager.
        If managing the client lifecycle manually, call this to clean up resources.

        Example:
            ```python
            client = DigikalaClient(api_key="your-key")
            await client.open()
            try:
                # Use client
                pass
            finally:
                await client.close()  # Clean up resources
            ```
        """
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
            logger.debug("HTTP client closed")

    async def __aenter__(self) -> "DigikalaClient":
        """
        Enter async context manager.

        Returns:
            Self for use in context

        Example:
            ```python
            async with DigikalaClient(api_key="your-key") as client:
                # Client is automatically opened
                product = await client.products.get_product(id=123)
            # Client is automatically closed
            ```
        """
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Exit async context manager.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)
        """
        await self.close()

    @property
    def products(self) -> ProductsService:
        """
        Access the products service.

        Returns:
            ProductsService instance

        Raises:
            RuntimeError: If client is not opened

        Example:
            ```python
            async with DigikalaClient(api_key="key") as client:
                product = await client.products.get_product(id=123)
                results = await client.products.search(q="laptop")
            ```
        """
        if self._http_client is None:
            raise RuntimeError(
                "Client is not opened. Use 'async with' or call 'await client.open()' first."
            )
        if self._products_service is None:
            self._products_service = ProductsService(
                self._http_client,
                self.config
            )
        return self._products_service

    @property
    def sellers(self) -> SellersService:
        """
        Access the sellers service.

        Returns:
            SellersService instance

        Raises:
            RuntimeError: If client is not opened

        Example:
            ```python
            async with DigikalaClient(api_key="key") as client:
                seller_data = await client.sellers.get_seller_products(
                    id=123456,
                    page=1
                )
                print(seller_data.data.seller.title)
            ```
        """
        if self._http_client is None:
            raise RuntimeError(
                "Client is not opened. Use 'async with' or call 'await client.open()' first."
            )
        if self._sellers_service is None:
            self._sellers_service = SellersService(
                self._http_client,
                self.config
            )
        return self._sellers_service

    @property
    def brands(self) -> BrandsService:
        """
        Access the brands service.

        Returns:
            BrandsService instance

        Raises:
            RuntimeError: If client is not opened

        Example:
            ```python
            async with DigikalaClient(api_key="key") as client:
                brand_data = await client.brands.get_brand_products(
                    code="zarin-iran",
                    page=1
                )
                print(brand_data.data.brand.title_fa)
            ```
        """
        if self._http_client is None:
            raise RuntimeError(
                "Client is not opened. Use 'async with' or call 'await client.open()' first."
            )
        if self._brands_service is None:
            self._brands_service = BrandsService(
                self._http_client,
                self.config
            )
        return self._brands_service

    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"DigikalaClient(base_url={self.config.base_url}, "
            f"authenticated={bool(self.config.api_key or self.config.bearer_token)})"
        )