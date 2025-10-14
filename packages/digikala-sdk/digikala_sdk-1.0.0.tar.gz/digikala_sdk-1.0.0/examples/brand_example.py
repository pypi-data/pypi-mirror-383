"""Brand API usage examples."""

import asyncio
import logging
from src import DigikalaClient, APIStatusError

# Enable logging to see SDK activity
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def example_get_brand():
    """Example: Get brand information and products."""
    print("\n=== Get Brand Information ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            # Get brand by code
            brand_data = await client.brands.get_brand_products(code="zarin-iran", page=1)

            # Access brand information
            brand = brand_data.data.brand
            print(f"Brand ID: {brand.id}")
            print(f"Title (FA): {brand.title_fa}")
            print(f"Title (EN): {brand.title_en}")
            print(f"Code: {brand.code}")
            print(f"Is Premium: {brand.is_premium}")

            if brand.description:
                print(f"Description: {brand.description}")

            # Pagination info
            pager = brand_data.data.pager
            print(f"\nTotal items: {pager.total_items}")
            print(f"Total pages: {pager.total_pages}")
            print(f"Current page: {pager.current_page}")

            # Display products
            print(f"\nFound {len(brand_data.data.products)} products on this page:")
            for idx, product in enumerate(brand_data.data.products[:5], 1):
                print(f"{idx}. {product.title_fa}")
                if product.default_variant and hasattr(product.default_variant, 'price'):
                    price = product.default_variant.price.selling_price
                    print(f"   Price: {price:,} Rials")

        except APIStatusError as e:
            if e.status_code == 404:
                print(f"Brand not found")
            else:
                print(f"API Error [{e.status_code}]: {e.message}")
        except Exception as e:
            print(f"Error: {e}")
            logging.exception("Example failed")


async def example_pagination():
    """Example: Paginate through brand products."""
    print("\n=== Brand Products Pagination ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            page = 1
            total_products = 0

            while page <= 3:  # Get first 3 pages
                brand_data = await client.brands.get_brand_products(
                    code="zarin-iran",
                    page=page
                )

                print(f"\nPage {page}/{brand_data.data.pager.total_pages}:")
                print(f"Products on this page: {len(brand_data.data.products)}")

                total_products += len(brand_data.data.products)
                page += 1

            print(f"\nTotal products retrieved: {total_products}")

        except APIStatusError as e:
            print(f"API Error [{e.status_code}]: {e.message}")


async def example_multiple_brands():
    """Example: Get information for multiple brands with error handling."""
    print("\n=== Multiple Brands Information ===")

    brand_codes = ["zarin-iran", "samsung", "apple", "invalid-brand"]

    async with DigikalaClient(api_key="your-api-key") as client:
        for code in brand_codes:
            try:
                brand_data = await client.brands.get_brand_info(code=code)
                brand = brand_data.data.brand
                print(f"✓ {code}: {brand.title_fa} ({len(brand_data.data.products)} products)")
            except APIStatusError as e:
                if e.status_code == 404:
                    print(f"✗ {code}: Brand not found")
                else:
                    print(f"✗ {code}: Error [{e.status_code}] - {e.message}")


async def example_brand_filters():
    """Example: Access brand product filters and sorting options."""
    print("\n=== Brand Filters and Sorting ===")

    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            brand_data = await client.brands.get_brand_products(code="samsung", page=1)

            # Access filters
            if brand_data.data.filters:
                print(f"Available filters: {len(brand_data.data.filters)} filter groups")

            # Access sort options
            if brand_data.data.sort_options:
                print(f"\nAvailable sort options:")
                for sort_option in brand_data.data.sort_options:
                    print(f"- {sort_option.title_fa} (ID: {sort_option.id})")

            # Access search suggestions
            if brand_data.data.did_you_mean:
                print(f"\nDid you mean suggestions: {brand_data.data.did_you_mean}")

            if brand_data.data.related_search_words:
                print(f"Related searches: {brand_data.data.related_search_words}")

        except APIStatusError as e:
            print(f"API Error [{e.status_code}]: {e.message}")


async def main():
    """Run all brand examples."""
    try:
        await example_get_brand()
        await example_pagination()
        await example_multiple_brands()
        await example_brand_filters()
    except Exception as e:
        print(f"\nError: {e}")
        logging.exception("Example failed")


if __name__ == "__main__":
    asyncio.run(main())