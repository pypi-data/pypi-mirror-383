# Brands API Documentation

## Overview

The `BrandsService` provides access to brand-related API endpoints, allowing you to retrieve brand information and their product listings.

## Class: BrandsService

### Initialization

The `BrandsService` is automatically initialized when you create a `DigikalaClient` instance and is accessible via `client.brands`.

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Access brands service
    brands = client.brands
```

---

## Methods

### `get_brand_products()`

Get comprehensive brand information along with their product list with pagination support.

#### Signature

```python
async def get_brand_products(code: str, page: Optional[int] = 1) -> BrandProductsResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `code` | `str` | ✅ Yes | - | Brand code (unique brand identifier, usually in kebab-case like `"samsung"` or `"apple"`) |
| `page` | `int` | ❌ No | `1` | Page number for product pagination |

#### Returns

`BrandProductsResponse` - Comprehensive response including:
- Brand information (name, description, logo, metadata)
- List of brand's products (with pagination)
- Pagination details (current page, total pages, total items)
- Optional sponsored brands and advertisements

#### Raises

- `APIStatusError`: Brand with given code does not exist (status 404)
- `BadRequestError`: Invalid request parameters
- `DigikalaAPIError`: Other API errors

#### Example Usage

**Basic Usage:**

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Get brand products
    brand_data = await client.brands.get_brand_products(
        code="samsung",
        page=1
    )

    # Access brand information
    brand = brand_data.data.brand
    print(f"Brand: {brand.title_fa}")
    print(f"English Name: {brand.title_en}")
    print(f"Code: {brand.code}")
    print(f"Description: {brand.description}")

    # Brand logo
    if brand.logo and brand.logo.url:
        print(f"Logo URL: {brand.logo.url[0]}")

    # Brand metadata
    if brand.url:
        print(f"Brand URL: {brand.url.uri}")

    # Access products
    print(f"\nProducts (Page {brand_data.data.pager.current_page}):")
    for product in brand_data.data.products:
        print(f"- {product.title_fa}")
        print(f"  ID: {product.id}")

        if product.default_variant:
            variant = product.default_variant
            if variant.price:
                price = variant.price
                print(f"  Price: {price.selling_price:,} Rials")
                if price.discount_percent > 0:
                    print(f"  Discount: {price.discount_percent}%")

    # Pagination info
    pager = brand_data.data.pager
    print(f"\nPagination:")
    print(f"  Current Page: {pager.current_page}")
    print(f"  Total Pages: {pager.total_pages}")
    print(f"  Total Items: {pager.total_items}")
```

**Fetching All Brand Products:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    brand_code = "samsung"
    all_products = []
    page = 1

    while True:
        brand_data = await client.brands.get_brand_products(
            code=brand_code,
            page=page
        )
        all_products.extend(brand_data.data.products)

        print(f"Fetched page {page}/{brand_data.data.pager.total_pages}")

        if page >= brand_data.data.pager.total_pages:
            break

        page += 1

    print(f"\nTotal {brand_data.data.brand.title_fa} products: {len(all_products)}")
```

**Brand Product Analysis:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    brand_data = await client.brands.get_brand_products(code="apple", page=1)
    brand = brand_data.data.brand

    print(f"Brand Analysis: {brand.title_fa}")
    print("=" * 50)

    # Product statistics
    total_products = brand_data.data.pager.total_items
    print(f"\nTotal Products: {total_products}")

    # Price range analysis
    prices = []
    for product in brand_data.data.products:
        if product.default_variant and product.default_variant.price:
            prices.append(product.default_variant.price.selling_price)

    if prices:
        print(f"Price Range: {min(prices):,} - {max(prices):,} Rials")
        print(f"Average Price: {sum(prices) // len(prices):,} Rials")

    # Rating analysis
    rated_products = [
        p for p in brand_data.data.products
        if p.rating and p.rating.count > 0
    ]

    if rated_products:
        avg_rating = sum(p.rating.rate for p in rated_products) / len(rated_products)
        print(f"\nAverage Rating: {avg_rating:.2f}/5")
        print(f"Products with Reviews: {len(rated_products)}/{len(brand_data.data.products)}")
```

**Filtering Brand Products:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    brand_data = await client.brands.get_brand_products(code="lg")

    # Filter high-rated products
    high_rated = [
        p for p in brand_data.data.products
        if p.rating and p.rating.rate >= 4.5
    ]

    print(f"High-rated LG products ({len(high_rated)} found):")
    for product in high_rated:
        print(f"  - {product.title_fa}")
        print(f"    Rating: {product.rating.rate}/5 ({product.rating.count} reviews)")

    # Filter discounted products
    discounted = [
        p for p in brand_data.data.products
        if p.default_variant
        and p.default_variant.price
        and p.default_variant.price.discount_percent > 0
    ]

    print(f"\nDiscounted products ({len(discounted)} found):")
    for product in discounted:
        price = product.default_variant.price
        print(f"  - {product.title_fa}")
        print(f"    Discount: {price.discount_percent}%")
        print(f"    Price: {price.selling_price:,} (was {price.rrp_price:,})")
```

---

### `get_brand_info()`

Get brand information as a convenience method. This is an alias for `get_brand_products()` with page 1.

#### Signature

```python
async def get_brand_info(code: str) -> BrandProductsResponse
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | `str` | ✅ Yes | Brand code (unique brand identifier) |

#### Returns

`BrandProductsResponse` - Brand information with the first page of products

#### Raises

- `APIStatusError`: Brand with given code does not exist (status 404)
- `DigikalaAPIError`: Other API errors

#### Example Usage

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Get brand info (first page only)
    brand_data = await client.brands.get_brand_info(code="xiaomi")

    brand = brand_data.data.brand
    print(f"Brand: {brand.title_fa}")
    print(f"English Name: {brand.title_en}")
    print(f"Code: {brand.code}")

    # Brand URL
    if brand.url:
        print(f"URL: {brand.url.uri}")

    # Check brand properties
    if hasattr(brand, 'is_premium') and brand.is_premium:
        print("✓ Premium Brand")

    if hasattr(brand, 'is_miscellaneous') and brand.is_miscellaneous:
        print("⚠ Miscellaneous Brand")

    # Sample products
    print(f"\nSample Products ({len(brand_data.data.products)} items):")
    for product in brand_data.data.products[:5]:  # Show first 5
        print(f"  - {product.title_fa}")
```

**Quick Brand Verification:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    try:
        brand_data = await client.brands.get_brand_info(code="nokia")
        brand = brand_data.data.brand

        print(f"✓ Brand found: {brand.title_fa}")
        print(f"  Code: {brand.code}")
        print(f"  Total Products: {brand_data.data.pager.total_items}")

        # Check if brand has description
        if brand.description:
            print(f"  Description: {brand.description[:100]}...")
        else:
            print("  No description available")

    except APIStatusError as e:
        if e.status_code == 404:
            print("✗ Brand not found")
        else:
            print(f"Error: {e}")
```

---

## Response Models

### BrandProductsResponse

```python
{
    "status": 200,
    "data": {
        "brand": {
            "id": int,
            "title_fa": str,
            "title_en": str,
            "code": str,
            "url": {
                "uri": str
            },
            "logo": {
                "url": [str],
                "thumbnail_url": str
            },
            "description": str,
            "visibility": bool,
            "is_premium": bool,
            "is_miscellaneous": bool,
            "is_name_similar": bool
        },
        "products": [
            {
                "id": int,
                "title_fa": str,
                "title_en": str,
                "status": str,
                "url": {"uri": str},
                "default_variant": {
                    "price": {
                        "selling_price": int,
                        "rrp_price": int,
                        "discount_percent": int
                    }
                },
                "rating": {
                    "rate": float,
                    "count": int
                },
                "images": {
                    "main": {
                        "url": [str]
                    }
                }
            }
        ],
        "pager": {
            "current_page": int,
            "total_pages": int,
            "total_items": int
        },
        "sponsored_brands": [
            {
                "id": int,
                "title": str,
                "code": str
            }
        ]
    }
}
```

---

## Error Handling

```python
from digikala_sdk import DigikalaClient
from digikala_sdk.exceptions import (
    APIStatusError,
    BadRequestError,
    DigikalaAPIError
)

async with DigikalaClient(api_key="your-api-key") as client:
    try:
        # Try to get brand data
        brand_data = await client.brands.get_brand_products(
            code="invalid-brand-code"
        )

    except APIStatusError as e:
        if e.status_code == 404:
            print("Brand not found")
            print("Please verify the brand code")
        else:
            print(f"API returned error status: {e.status_code}")

    except BadRequestError as e:
        print(f"Invalid request parameters: {e}")

    except DigikalaAPIError as e:
        print(f"API error occurred: {e}")
```

---

## Use Cases

### 1. Brand Comparison

```python
async def compare_brands(code1: str, code2: str):
    async with DigikalaClient(api_key="your-api-key") as client:
        brand1_data = await client.brands.get_brand_info(code=code1)
        brand2_data = await client.brands.get_brand_info(code=code2)

        brand1 = brand1_data.data.brand
        brand2 = brand2_data.data.brand

        print("Brand Comparison")
        print("=" * 60)

        print(f"\n{brand1.title_fa} vs {brand2.title_fa}")
        print(f"Total Products: {brand1_data.data.pager.total_items} vs {brand2_data.data.pager.total_items}")

        # Calculate average prices
        def avg_price(products):
            prices = [
                p.default_variant.price.selling_price
                for p in products
                if p.default_variant and p.default_variant.price
            ]
            return sum(prices) // len(prices) if prices else 0

        avg1 = avg_price(brand1_data.data.products)
        avg2 = avg_price(brand2_data.data.products)

        print(f"Avg Price (sample): {avg1:,} vs {avg2:,} Rials")

        # Check premium status
        if brand1.is_premium:
            print(f"✓ {brand1.title_fa} is a premium brand")
        if brand2.is_premium:
            print(f"✓ {brand2.title_fa} is a premium brand")
```

### 2. Brand Product Catalog Export

```python
async def export_brand_catalog(brand_code: str, min_rating: float = 0.0):
    async with DigikalaClient(api_key="your-api-key") as client:
        page = 1
        all_products = []

        while True:
            response = await client.brands.get_brand_products(
                code=brand_code,
                page=page
            )

            # Filter by rating
            filtered_products = [
                p for p in response.data.products
                if not p.rating or p.rating.rate >= min_rating
            ]

            all_products.extend(filtered_products)

            if page >= response.data.pager.total_pages:
                break
            page += 1

        print(f"Exported {len(all_products)} products from {brand_code}")
        print(f"(filtered by rating >= {min_rating})")

        return all_products
```

### 3. Brand Performance Dashboard

```python
async def brand_dashboard(brand_code: str):
    async with DigikalaClient(api_key="your-api-key") as client:
        brand_data = await client.brands.get_brand_info(code=brand_code)
        brand = brand_data.data.brand
        products = brand_data.data.products

        print(f"\n{'=' * 60}")
        print(f"Brand Dashboard: {brand.title_fa}")
        print(f"{'=' * 60}")

        # Basic info
        print(f"\nBrand Information:")
        print(f"  Name (EN): {brand.title_en}")
        print(f"  Code: {brand.code}")
        print(f"  Total Products: {brand_data.data.pager.total_items}")

        # Status indicators
        status = []
        if brand.is_premium:
            status.append("Premium")
        if brand.visibility:
            status.append("Visible")

        if status:
            print(f"  Status: {', '.join(status)}")

        # Product statistics
        print(f"\nProduct Statistics (Sample Page):")

        total = len(products)
        with_rating = len([p for p in products if p.rating and p.rating.count > 0])
        with_discount = len([
            p for p in products
            if p.default_variant
            and p.default_variant.price
            and p.default_variant.price.discount_percent > 0
        ])

        print(f"  Total Products (page): {total}")
        print(f"  With Reviews: {with_rating} ({with_rating/total*100:.1f}%)")
        print(f"  With Discount: {with_discount} ({with_discount/total*100:.1f}%)")

        # Price analysis
        prices = [
            p.default_variant.price.selling_price
            for p in products
            if p.default_variant and p.default_variant.price
        ]

        if prices:
            print(f"\nPrice Analysis:")
            print(f"  Min Price: {min(prices):,} Rials")
            print(f"  Max Price: {max(prices):,} Rials")
            print(f"  Avg Price: {sum(prices)//len(prices):,} Rials")

        # Top rated products
        rated = [p for p in products if p.rating and p.rating.count > 0]
        if rated:
            rated.sort(key=lambda x: x.rating.rate, reverse=True)
            print(f"\nTop Rated Products:")
            for i, product in enumerate(rated[:3], 1):
                print(f"  {i}. {product.title_fa}")
                print(f"     Rating: {product.rating.rate}/5 ({product.rating.count} reviews)")
```

### 4. Brand Portfolio Analysis

```python
async def analyze_brand_portfolio(brand_codes: list):
    async with DigikalaClient(api_key="your-api-key") as client:
        print("Multi-Brand Portfolio Analysis")
        print("=" * 60)

        for code in brand_codes:
            try:
                brand_data = await client.brands.get_brand_info(code=code)
                brand = brand_data.data.brand

                print(f"\n{brand.title_fa}:")
                print(f"  Products: {brand_data.data.pager.total_items}")
                print(f"  Premium: {'Yes' if brand.is_premium else 'No'}")

                # Sample price range
                prices = [
                    p.default_variant.price.selling_price
                    for p in brand_data.data.products
                    if p.default_variant and p.default_variant.price
                ]

                if prices:
                    print(f"  Price Range: {min(prices):,} - {max(prices):,}")

            except APIStatusError:
                print(f"\n{code}: Not found")
```

---

## Best Practices

### 1. Cache Brand Information

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    cache_config={
        "enabled": True,
        "backend": "memory",
        "ttl": 3600  # Cache for 1 hour
    }
)

async with DigikalaClient(config=config) as client:
    # Brand info cached for 1 hour
    brand_data = await client.brands.get_brand_info(code="samsung")
```

### 2. Handle Pagination Efficiently

```python
async with DigikalaClient(api_key="your-api-key") as client:
    code = "apple"
    page = 1

    while True:
        response = await client.brands.get_brand_products(code=code, page=page)

        # Process products on this page
        for product in response.data.products:
            await process_product(product)

        if page >= response.data.pager.total_pages:
            break
        page += 1
```

### 3. Validate Brand Data

```python
async with DigikalaClient(api_key="your-api-key") as client:
    brand_data = await client.brands.get_brand_info(code="sony")
    brand = brand_data.data.brand

    # Always check for optional fields
    if brand.logo and brand.logo.url:
        logo_url = brand.logo.url[0]
        print(f"Logo: {logo_url}")
    else:
        print("No logo available")

    if brand.description:
        print(f"Description: {brand.description}")
    else:
        print("No description available")
```

### 4. Use Try-Except for Brand Validation

```python
async def is_valid_brand(code: str) -> bool:
    async with DigikalaClient(api_key="your-api-key") as client:
        try:
            await client.brands.get_brand_info(code=code)
            return True
        except APIStatusError as e:
            if e.status_code == 404:
                return False
            raise  # Re-raise other errors
```

---

## See Also

- [Products API Documentation](products.md)
- [Sellers API Documentation](sellers.md)
- [Main SDK Documentation](SDK_Documentation.md)