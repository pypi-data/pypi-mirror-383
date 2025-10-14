"""Error handling examples for Digikala SDK."""

import asyncio
import logging
from src import DigikalaClient, APIStatusError

# Enable logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def example_1_handle_404():
    """Example 1: Handle 404 errors gracefully."""
    print("\n" + "=" * 60)
    print("Example 1: Handling 404 - Resource Not Found")
    print("=" * 60)

    async with DigikalaClient(api_key="your-api-key") as client:
        # Try to get a product that doesn't exist
        print("\n1. Trying to get non-existent product (ID: 99999999)...")
        try:
            product = await client.products.get_product(id=99999999)
            print(f"Success: {product.data.product.title_fa}")
        except APIStatusError as e:
            print(f"✓ Handled error gracefully:")
            print(f"  Status Code: {e.status_code}")
            print(f"  Message: {e.message}")
            print(f"  Type: {type(e).__name__}")


async def example_2_batch_with_error_handling():
    """Example 2: Process multiple items with error handling."""
    print("\n" + "=" * 60)
    print("Example 2: Batch Processing with Error Handling")
    print("=" * 60)

    async with DigikalaClient(api_key="your-api-key") as client:
        # List of seller SKUs (some valid, some invalid)
        seller_skus = [
            "FRVMM",      # Valid
            "INVALID1",   # Invalid
            "5AMEZ",      # Valid
            "NOTFOUND",   # Invalid
            "DYU2S",      # Valid
        ]

        results = {
            "success": [],
            "failed": []
        }

        print(f"\nProcessing {len(seller_skus)} sellers...")
        for sku in seller_skus:
            try:
                seller_data = await client.sellers.get_seller_products(
                    sku=sku,
                    page=1
                )
                seller_name = seller_data.data.seller.title
                results["success"].append({
                    "sku": sku,
                    "name": seller_name
                })
                print(f"  ✓ {sku}: {seller_name}")

            except APIStatusError as e:
                results["failed"].append({
                    "sku": sku,
                    "error": f"[{e.status_code}] {e.message}"
                })
                print(f"  ✗ {sku}: Error {e.status_code}")

        # Summary
        print("\n" + "-" * 60)
        print(f"Summary:")
        print(f"  Success: {len(results['success'])}")
        print(f"  Failed: {len(results['failed'])}")


async def example_3_different_error_types():
    """Example 3: Handle different types of errors."""
    print("\n" + "=" * 60)
    print("Example 3: Handling Different Error Types")
    print("=" * 60)

    async with DigikalaClient(api_key="your-api-key") as client:
        test_cases = [
            {
                "name": "Valid Product",
                "action": lambda: client.products.get_product(id=20365865),
                "expected": "Success"
            },
            {
                "name": "Invalid Product (404)",
                "action": lambda: client.products.get_product(id=99999999),
                "expected": "404 Error"
            },
            {
                "name": "Invalid Seller (404)",
                "action": lambda: client.sellers.get_seller_products(
                    sku="NOTEXIST",
                    page=1
                ),
                "expected": "404 Error"
            },
        ]

        for i, test in enumerate(test_cases, 1):
            print(f"\n{i}. {test['name']} (Expected: {test['expected']}):")
            try:
                result = await test["action"]()
                print(f"   ✓ Success!")

            except APIStatusError as e:
                if e.status_code == 404:
                    print(f"   ✓ Caught 404: Resource not found")
                elif e.status_code == 401:
                    print(f"   ✓ Caught 401: Unauthorized")
                elif e.status_code == 403:
                    print(f"   ✓ Caught 403: Forbidden")
                elif e.status_code >= 500:
                    print(f"   ✓ Caught {e.status_code}: Server error")
                else:
                    print(f"   ✓ Caught {e.status_code}: {e.message}")


async def example_4_retry_pattern():
    """Example 4: Retry pattern for transient errors."""
    print("\n" + "=" * 60)
    print("Example 4: Retry Pattern for Transient Errors")
    print("=" * 60)

    async with DigikalaClient(api_key="your-api-key") as client:
        max_retries = 3
        product_id = 99999999  # Non-existent product

        print(f"\nTrying to get product {product_id} with {max_retries} retries...")

        for attempt in range(1, max_retries + 1):
            try:
                print(f"\nAttempt {attempt}/{max_retries}:")
                product = await client.products.get_product(id=product_id)
                print(f"  ✓ Success: {product.data.product.title_fa}")
                break

            except APIStatusError as e:
                print(f"  ✗ Error {e.status_code}: {e.message}")

                # Don't retry for client errors (4xx)
                if 400 <= e.status_code < 500:
                    print(f"  → Client error, not retrying")
                    break

                # Retry for server errors (5xx)
                if attempt < max_retries:
                    print(f"  → Will retry...")
                    await asyncio.sleep(1)  # Wait before retry
                else:
                    print(f"  → Max retries reached")


async def example_5_contextual_error_handling():
    """Example 5: Contextual error handling with business logic."""
    print("\n" + "=" * 60)
    print("Example 5: Contextual Error Handling")
    print("=" * 60)

    async with DigikalaClient(api_key="your-api-key") as client:
        print("\nScenario: Check if seller exists and has products")

        test_sellers = ["FRVMM", "INVALID_SELLER"]

        for sku in test_sellers:
            print(f"\n→ Checking seller: {sku}")

            try:
                seller_data = await client.sellers.get_seller_products(
                    sku=sku,
                    page=1
                )

                # Business logic based on successful response
                seller = seller_data.data.seller
                product_count = len(seller_data.data.products)

                print(f"  ✓ Seller found: {seller.title}")
                print(f"  ✓ Rating: {seller.stars}/5")
                print(f"  ✓ Products on page: {product_count}")

                # Business decision based on data
                if seller.stars >= 4.0 and product_count > 0:
                    print(f"  ✓ Recommendation: Good seller to work with!")
                else:
                    print(f"  ⚠ Recommendation: Review seller carefully")

            except APIStatusError as e:
                # Business logic based on error type
                if e.status_code == 404:
                    print(f"  ✗ Seller not found in system")
                    print(f"  → Action: Skip this seller")
                elif e.status_code == 403:
                    print(f"  ✗ Access denied to seller data")
                    print(f"  → Action: Check API permissions")
                else:
                    print(f"  ✗ Error: {e.message}")
                    print(f"  → Action: Log for investigation")


async def main():
    """Run all error handling examples."""
    print("\n" + "=" * 60)
    print("Digikala SDK - Error Handling Examples")
    print("=" * 60)

    try:
        await example_1_handle_404()
        await example_2_batch_with_error_handling()
        await example_3_different_error_types()
        await example_4_retry_pattern()
        await example_5_contextual_error_handling()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logging.exception("Error in examples")


if __name__ == "__main__":
    asyncio.run(main())