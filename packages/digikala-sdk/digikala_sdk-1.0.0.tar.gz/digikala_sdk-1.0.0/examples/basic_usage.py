"""Basic usage examples for Digikala SDK."""

import asyncio
import logging
from src import DigikalaClient, DigikalaConfig, APIStatusError

# Enable logging to see SDK activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def example_get_product():
    """Example: Get product details."""
    print("\n=== Get Product Details ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        # Get product by ID
        product = await client.products.get_product(id=20365865)

        # Access product information
        print(f"ID: {product.data.product.id}")
        print(f"Title (FA): {product.data.product.title_fa}")
        print(f"Title (EN): {product.data.product.title_en}")
        print(f"Brand: {product.data.product.brand.title_fa}")
        print(f"Category: {product.data.product.category.title_fa}")
        print(f"Status: {product.data.product.status}")

        # Price information
        price = product.data.product.default_variant.price
        print(f"Selling Price: {price.selling_price:,} Rials")
        print(f"Discount: {price.discount_percent}%")

        # Seller information
        seller = product.data.product.default_variant.seller
        print(f"Seller: {seller.title}")
        print(f"Seller Rating: {seller.stars}/5 ({seller.rating.total_count} reviews)")

        # Availability
        shipment = product.data.product.default_variant.shipment_methods
        print(f"Availability: {shipment.description}")


async def example_search_products():
    """Example: Search for products."""
    print("\n=== Search Products ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        # Search for iPhone products
        results = await client.products.search(q="iphone13", page=1)

        # Pagination info
        pager = results.data.pager
        print(f"Total items: {pager.total_items}")
        print(f"Total pages: {pager.total_pages}")
        print(f"Current page: {pager.current_page}")

        # Display products
        print(f"\nFound {len(results.data.products)} products on this page:")
        for idx, product in enumerate(results.data.products[:5], 1):
            print(f"{idx}. {product.title_fa}")
            if product.default_variant and product.default_variant.price:
                price = product.default_variant.price.selling_price
                print(f"   Price: {price:,} Rials")


async def example_get_seller(sku: str):
    """Example: Get seller information and products with error handling."""
    print(f"\n=== Get Seller Information (SKU: {sku}) ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            # Get seller and their products
            seller_data = await client.sellers.get_seller_products(
                sku=sku,
                page=1
            )

            # Seller information
            seller = seller_data.data.seller
            print(f"Seller: {seller.title}")
            print(f"Code: {seller.code}")
            print(f"Rating: {seller.stars}/5")
            print(f"Total Reviews: {seller.rating.total_count}")
            print(f"Registration: {seller.registration_date}")

            # Seller statistics
            stats = seller.statistics
            print(f"\nPerformance:")
            print(f"  On-time Shipping: {stats.ship_on_time}%")
            print(f"  Cancellation Rate: {stats.cancellation}%")
            print(f"  Return Rate: {stats.return_}%")

            # Seller properties
            props = seller.properties
            print(f"\nProperties:")
            print(f"  Trusted: {props.is_trusted}")
            print(f"  Official: {props.is_official}")

            # Products
            print(f"\nProducts (Page {seller_data.data.pager.current_page}):")
            for idx, product in enumerate(seller_data.data.products[:5], 1):
                print(f"{idx}. {product.title_fa}")

        except APIStatusError as e:
            # Handle API-level errors (status != 200 in response body)
            if e.status_code == 404:
                print(f"❌ Seller '{sku}' not found")
            elif e.status_code == 403:
                print(f"❌ Access denied to seller '{sku}'")
            else:
                print(f"❌ API Error [{e.status_code}]: {e.message}")
            logging.warning(f"Seller {sku} failed: {e}")


async def example_with_custom_config():
    """Example: Using custom configuration."""
    print("\n=== Custom Configuration ===")

    # Create custom configuration
    config = DigikalaConfig(
        base_url="https://api.digikala.com",
        api_key="your-api-key",
        timeout=60.0,          # 60 second timeout
        max_retries=5,         # Retry up to 5 times
        retry_delay=2.0,       # 2 second initial delay
        retry_backoff=2.0,     # Double delay each retry
    )

    async with DigikalaClient(config=config) as client:
        print(f"Client configured with:")
        print(f"  Base URL: {config.base_url}")
        print(f"  Timeout: {config.timeout}s")
        print(f"  Max Retries: {config.max_retries}")

        # Use client as normal
        product = await client.products.get_product(id=20365865)
        print(f"  Product: {product.data.product.title_fa}")


async def example_pagination():
    """Example: Paginating through results."""
    print("\n=== Pagination Example ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        page = 1
        total_products = 0

        while page <= 3:  # Get first 3 pages
            results = await client.products.search(q="laptop", page=page)

            print(f"\nPage {page}/{results.data.pager.total_pages}:")
            print(f"Products on this page: {len(results.data.products)}")

            total_products += len(results.data.products)
            page += 1

        print(f"\nTotal products retrieved: {total_products}")


async def example_error_handling():
    """Example: Comprehensive error handling."""
    print("\n=== Error Handling Examples ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        # Example 1: Product not found (404)
        print("\n1. Handling 404 - Product Not Found:")
        try:
            await client.products.get_product(id=99999999)
        except APIStatusError as e:
            if e.status_code == 404:
                print(f"   ✓ Caught 404: Product doesn't exist")
                print(f"   Status: {e.status_code}")
                print(f"   Message: {e.message}")

        # Example 2: Seller not found (404)
        print("\n2. Handling 404 - Seller Not Found:")
        try:
            await client.sellers.get_seller_products(sku="INVALID_SKU", page=1)
        except APIStatusError as e:
            if e.status_code == 404:
                print(f"   ✓ Caught 404: Seller doesn't exist")
                print(f"   Response data available: {e.response is not None}")

        # Example 3: Generic error handling
        print("\n3. Generic Error Handling:")
        test_sellers = ["DHU6J", "INVALID1", "INVALID2"]
        for sku in test_sellers:
            try:
                result = await client.sellers.get_seller_products(sku=sku, page=1)
                print(f"   ✓ {sku}: Found - {result.data.seller.title}")
            except APIStatusError as e:
                print(f"   ✗ {sku}: Error [{e.status_code}] - {e.message}")


async def main():
    """Run all examples."""
    try:
        sku_sellers = ['dmhxe', 'FRVMM', 'hdwnc', '5AMEZ', '5A52N', 'DHU6J', 'DYU2S', 'cpgdj',
                       'CZ4T5', 'GN54D' ,'D3TF9', 'ANU4X', 'D6HK4', 'ahygt', '5A55Y', 'H6JX9',
                       'DARP4', 'C9A22', 'FPS32', 'HDAVV', 'CFD4K', 'HGG93', 'dwkmp', 'F3FNX']
        await example_get_product()
        await example_search_products()
        for sku in sku_sellers:
            await example_get_seller(sku)
        await example_with_custom_config()
        await example_pagination()
    except Exception as e:
        print(f"\nError: {e}")
        logging.exception("Example failed")


if __name__ == "__main__":
    asyncio.run(main())