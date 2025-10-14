"""Comprehensive error handling examples."""

import asyncio
import logging
from src import DigikalaClient
from src.exceptions import (
    DigikalaAPIError,
    BadRequestError,
    UnauthorizedError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError,
)

logging.basicConfig(level=logging.INFO)


async def handle_not_found():
    """Example: Handle product not found."""
    print("\n=== Handling Not Found Errors ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            # Try to get non-existent product
            product = await client.products.get_product(id=99999999)
        except NotFoundError as e:
            print(f"Product not found: {e.message}")
            print(f"Status code: {e.status_code}")
            # Handle gracefully - maybe show similar products instead
            print("Showing alternative products instead...")


async def handle_rate_limit():
    """Example: Handle rate limiting."""
    print("\n=== Handling Rate Limit ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            # This might trigger rate limit
            for i in range(100):
                await client.products.get_product(id=12345)
        except RateLimitError as e:
            print(f"Rate limit exceeded: {e.message}")
            if e.retry_after:
                print(f"Retry after: {e.retry_after} seconds")
                await asyncio.sleep(e.retry_after)
                print("Retrying now...")


async def handle_timeout():
    """Example: Handle timeout errors."""
    print("\n=== Handling Timeout ===")

    # Configure short timeout for demonstration
    from src import DigikalaConfig
    config = DigikalaConfig(
        api_key="your-api-key",
        timeout=0.001  # Very short timeout
    )

    async with DigikalaClient(config=config) as client:
        try:
            product = await client.products.get_product(id=12345)
        except TimeoutError as e:
            print(f"Request timed out: {e.message}")
            print("Consider increasing timeout or checking network connection")


async def handle_server_error():
    """Example: Handle server errors."""
    print("\n=== Handling Server Errors ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            product = await client.products.get_product(id=12345)
        except ServerError as e:
            print(f"Server error: {e.message}")
            print(f"Status code: {e.status_code}")
            print("This is likely temporary. SDK will retry automatically.")


async def handle_authentication():
    """Example: Handle authentication errors."""
    print("\n=== Handling Authentication ===")

    async with DigikalaClient(api_key="invalid-key") as client:
        try:
            product = await client.products.get_product(id=12345)
        except UnauthorizedError as e:
            print(f"Authentication failed: {e.message}")
            print("Please check your API key or bearer token")


async def comprehensive_error_handling():
    """Example: Comprehensive error handling pattern."""
    print("\n=== Comprehensive Error Handling ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            # Attempt API operation
            product = await client.products.get_product(id=12345)
            print(f"Success: {product.data.product.title_fa}")

        except NotFoundError as e:
            # Resource not found - handle gracefully
            print(f"Resource not found: {e.message}")
            return None

        except UnauthorizedError as e:
            # Authentication issue - critical error
            print(f"Authentication failed: {e.message}")
            raise  # Re-raise for upstream handling

        except RateLimitError as e:
            # Rate limit - wait and retry
            print(f"Rate limit hit, waiting {e.retry_after}s...")
            if e.retry_after:
                await asyncio.sleep(e.retry_after)
                # Implement retry logic here
                return await comprehensive_error_handling()

        except TimeoutError as e:
            # Timeout - log and potentially retry
            print(f"Request timeout: {e.message}")
            # Could implement retry with backoff here

        except ConnectionError as e:
            # Connection issue - likely network problem
            print(f"Connection failed: {e.message}")
            print("Please check network connectivity")

        except ServerError as e:
            # Server error - log and alert
            print(f"Server error [{e.status_code}]: {e.message}")
            # Log to monitoring system
            # SDK will retry automatically

        except DigikalaAPIError as e:
            # Catch-all for any other API errors
            print(f"API error: {e.message}")
            if e.status_code:
                print(f"Status code: {e.status_code}")


async def retry_with_fallback():
    """Example: Implement custom retry with fallback."""
    print("\n=== Custom Retry with Fallback ===")

    async def fetch_product_with_fallback(product_id: int, max_attempts: int = 3):
        """Fetch product with custom retry logic and fallback."""
        async with DigikalaClient(api_key="your-api-key") as client:
            for attempt in range(max_attempts):
                try:
                    product = await client.products.get_product(id=product_id)
                    return product

                except NotFoundError:
                    # Don't retry for 404
                    print(f"Product {product_id} not found")
                    return None

                except (ServerError, TimeoutError, ConnectionError) as e:
                    # Retry for transient errors
                    print(f"Attempt {attempt + 1} failed: {e.message}")
                    if attempt < max_attempts - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        print(f"Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        print("All retries exhausted, using fallback")
                        return None

                except DigikalaAPIError as e:
                    # For other errors, fail immediately
                    print(f"Unrecoverable error: {e.message}")
                    raise

    result = await fetch_product_with_fallback(12345)
    if result:
        print(f"Successfully fetched: {result.data.product.title_fa}")
    else:
        print("Using cached or default data as fallback")


async def graceful_degradation():
    """Example: Graceful degradation pattern."""
    print("\n=== Graceful Degradation ===")

    async def get_product_info(product_id: int) -> dict:
        """Get product info with graceful fallback."""
        try:
            async with DigikalaClient(api_key="your-api-key") as client:
                product = await client.products.get_product(id=product_id)
                return {
                    "id": product.data.product.id,
                    "title": product.data.product.title_fa,
                    "price": product.data.product.default_variant.price.selling_price,
                    "available": True,
                    "source": "api"
                }
        except NotFoundError:
            # Product doesn't exist
            return {
                "id": product_id,
                "title": "Product Not Found",
                "available": False,
                "source": "error"
            }
        except (TimeoutError, ServerError, ConnectionError):
            # Temporary issues - return partial data
            return {
                "id": product_id,
                "title": "Loading...",
                "available": True,  # Assume available
                "source": "fallback"
            }
        except DigikalaAPIError:
            # Unknown error - minimal info
            return {
                "id": product_id,
                "title": "Error Loading Product",
                "available": False,
                "source": "error"
            }

    info = await get_product_info(12345)
    print(f"Product Info: {info}")
    print(f"Data source: {info['source']}")


async def main():
    """Run all error handling examples."""
    examples = [
        handle_not_found,
        handle_rate_limit,
        # handle_timeout,  # Commented out as it will always fail
        handle_server_error,
        handle_authentication,
        comprehensive_error_handling,
        retry_with_fallback,
        graceful_degradation,
    ]

    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"Example {example.__name__} raised: {e}")
        await asyncio.sleep(1)  # Rate limiting between examples


if __name__ == "__main__":
    asyncio.run(main())