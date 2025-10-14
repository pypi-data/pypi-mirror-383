# Sellers API Documentation

## Overview

The `SellersService` provides access to seller-related API endpoints, allowing you to retrieve seller information and their product listings.

## Class: SellersService

### Initialization

The `SellersService` is automatically initialized when you create a `DigikalaClient` instance and is accessible via `client.sellers`.

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Access sellers service
    sellers = client.sellers
```

---

## Methods

### `get_seller_products()`

Get comprehensive seller information along with their product list with pagination support.

#### Signature

```python
async def get_seller_products(sku: str, page: Optional[int] = 1) -> SellerProductListResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sku` | `str` | ✅ Yes | - | Seller SKU (unique seller identifier/code) |
| `page` | `int` | ❌ No | `1` | Page number for product pagination |

#### Returns

`SellerProductListResponse` - Comprehensive response including:
- Seller information (name, rating, registration date, statistics)
- List of seller's products (with pagination)
- Pagination details (current page, total pages, total items)

#### Raises

- `NotFoundError`: Seller with given SKU does not exist
- `DigikalaAPIError`: Other API errors

#### Example Usage

**Basic Usage:**

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Get seller products
    seller_data = await client.sellers.get_seller_products(
        sku="seller-sku-code",
        page=1
    )

    # Access seller information
    seller = seller_data.data.seller
    print(f"Seller: {seller.title}")
    print(f"ID: {seller.id}")
    print(f"Registration: {seller.registration_date}")

    # Access seller rating
    if seller.rating:
        rating = seller.rating
        print(f"Rating: {seller.stars}/5")
        print(f"Total Ratings: {rating.total_count}")
        print(f"Performance: {rating.performance * 100}%")
        print(f"Commitment: {rating.commitment * 100}%")
        print(f"Shipping: {rating.shipping * 100}%")

    # Access products
    print(f"\nProducts (Page {seller_data.data.pager.current_page}):")
    for product in seller_data.data.products:
        print(f"- {product.title_fa}")
        print(f"  ID: {product.id}")

        if product.default_variant and product.default_variant.price:
            price = product.default_variant.price
            print(f"  Price: {price.selling_price:,} Rials")
            if price.discount_percent > 0:
                print(f"  Discount: {price.discount_percent}%")

    # Pagination info
    pager = seller_data.data.pager
    print(f"\nPagination:")
    print(f"  Current Page: {pager.current_page}")
    print(f"  Total Pages: {pager.total_pages}")
    print(f"  Total Items: {pager.total_items}")
```

**Fetching All Seller Products:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    sku = "seller-sku-code"
    all_products = []
    page = 1

    while True:
        seller_data = await client.sellers.get_seller_products(sku=sku, page=page)
        all_products.extend(seller_data.data.products)

        print(f"Fetched page {page}/{seller_data.data.pager.total_pages}")

        if page >= seller_data.data.pager.total_pages:
            break

        page += 1

    print(f"\nTotal products: {len(all_products)}")

    # Access seller info from last response
    seller = seller_data.data.seller
    print(f"Seller: {seller.title}")
```

**Analyzing Seller Performance:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    seller_data = await client.sellers.get_seller_products(sku="seller-sku-code")
    seller = seller_data.data.seller

    print(f"Seller Analysis: {seller.title}")
    print("=" * 50)

    # Rating breakdown
    if seller.rating:
        rating = seller.rating
        print(f"\nRating Breakdown:")
        print(f"  Overall: {seller.stars}/5 ({rating.total_count} reviews)")
        print(f"  Performance: {rating.performance * 100}%")
        print(f"  Commitment: {rating.commitment * 100}%")
        print(f"  Shipping: {rating.shipping * 100}%")
        print(f"  No Returns: {rating.no_return * 100}%")

    # Statistics
    if hasattr(seller, 'statistics'):
        stats = seller.statistics
        print(f"\nStatistics:")
        print(f"  Total Products: {len(seller_data.data.products)}")
        # Add more statistics as available in the model

    # Check seller properties
    if hasattr(seller, 'is_trusted') and seller.is_trusted:
        print("\n✓ Trusted Seller")

    if hasattr(seller, 'is_premium') and seller.is_premium:
        print("✓ Premium Seller")
```

---

### `get_seller_info()`

Get seller information as a convenience method. This is an alias for `get_seller_products()` with page 1.

#### Signature

```python
async def get_seller_info(sku: str) -> SellerProductListResponse
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sku` | `str` | ✅ Yes | Seller SKU (unique seller identifier) |

#### Returns

`SellerProductListResponse` - Seller information with the first page of products

#### Raises

- `NotFoundError`: Seller with given SKU does not exist
- `DigikalaAPIError`: Other API errors

#### Example Usage

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Get seller info (first page only)
    seller_data = await client.sellers.get_seller_info(sku="seller-sku-code")

    seller = seller_data.data.seller
    print(f"Seller Name: {seller.title}")
    print(f"Seller ID: {seller.id}")
    print(f"Registration Date: {seller.registration_date}")

    if seller.rating:
        print(f"Rating: {seller.stars}/5")
        print(f"Total Reviews: {seller.rating.total_count}")

    # First page of products (if needed)
    print(f"\nSample Products ({len(seller_data.data.products)} items):")
    for product in seller_data.data.products[:5]:  # Show first 5
        print(f"  - {product.title_fa}")
```

**Quick Seller Verification:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    try:
        seller_data = await client.sellers.get_seller_info(sku="seller-sku-code")
        seller = seller_data.data.seller

        # Quick verification
        is_reliable = (
            seller.stars >= 4.0 and
            seller.rating.total_count >= 100 and
            seller.rating.performance >= 0.8
        )

        if is_reliable:
            print(f"✓ {seller.title} is a reliable seller")
            print(f"  Rating: {seller.stars}/5")
            print(f"  Reviews: {seller.rating.total_count}")
        else:
            print(f"⚠ {seller.title} - Review carefully")
            print(f"  Rating: {seller.stars}/5")

    except NotFoundError:
        print("Seller not found")
```

---

## Response Models

### SellerProductListResponse

```python
{
    "status": 200,
    "data": {
        "seller": {
            "id": int,
            "title": str,
            "code": str,
            "registration_date": str,
            "stars": float,  # Overall rating
            "rating": {
                "total_count": int,
                "performance": float,  # 0.0 to 1.0
                "commitment": float,
                "shipping": float,
                "no_return": float
            },
            "grade": {
                "label": str,
                "color": str
            },
            "icon": {
                "url": [str]
            }
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
                }
            }
        ],
        "pager": {
            "current_page": int,
            "total_pages": int,
            "total_items": int
        }
    }
}
```

---

## Error Handling

```python
from digikala_sdk import DigikalaClient
from digikala_sdk.exceptions import (
    NotFoundError,
    BadRequestError,
    DigikalaAPIError
)

async with DigikalaClient(api_key="your-api-key") as client:
    try:
        # Try to get seller data
        seller_data = await client.sellers.get_seller_products(
            sku="invalid-sku"
        )

    except NotFoundError as e:
        print(f"Seller not found: {e}")
        print("Please verify the seller SKU")

    except BadRequestError as e:
        print(f"Invalid request parameters: {e}")

    except DigikalaAPIError as e:
        print(f"API error occurred: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
```

---

## Use Cases

### 1. Seller Comparison

```python
async def compare_sellers(sku1: str, sku2: str):
    async with DigikalaClient(api_key="your-api-key") as client:
        seller1 = (await client.sellers.get_seller_info(sku=sku1)).data.seller
        seller2 = (await client.sellers.get_seller_info(sku=sku2)).data.seller

        print("Seller Comparison")
        print("=" * 50)

        print(f"\n{seller1.title} vs {seller2.title}")
        print(f"Rating: {seller1.stars}/5 vs {seller2.stars}/5")

        if seller1.rating and seller2.rating:
            print(f"Reviews: {seller1.rating.total_count} vs {seller2.rating.total_count}")
            print(f"Performance: {seller1.rating.performance:.1%} vs {seller2.rating.performance:.1%}")
            print(f"Shipping: {seller1.rating.shipping:.1%} vs {seller2.rating.shipping:.1%}")

        # Determine better seller
        if seller1.stars > seller2.stars:
            print(f"\n✓ {seller1.title} has higher rating")
        elif seller2.stars > seller1.stars:
            print(f"\n✓ {seller2.title} has higher rating")
        else:
            print(f"\n= Both sellers have equal rating")
```

### 2. Product Catalog Export

```python
async def export_seller_catalog(sku: str):
    async with DigikalaClient(api_key="your-api-key") as client:
        page = 1
        products = []

        while True:
            response = await client.sellers.get_seller_products(sku=sku, page=page)
            products.extend(response.data.products)

            if page >= response.data.pager.total_pages:
                break
            page += 1

        # Export to CSV or process
        print(f"Exported {len(products)} products from seller")
        return products
```

### 3. Seller Monitoring

```python
async def monitor_seller_performance(sku: str):
    async with DigikalaClient(api_key="your-api-key") as client:
        seller_data = await client.sellers.get_seller_info(sku=sku)
        seller = seller_data.data.seller

        # Define thresholds
        MIN_RATING = 4.0
        MIN_PERFORMANCE = 0.85
        MIN_REVIEWS = 50

        issues = []

        if seller.stars < MIN_RATING:
            issues.append(f"Rating below {MIN_RATING}: {seller.stars}/5")

        if seller.rating:
            if seller.rating.performance < MIN_PERFORMANCE:
                issues.append(
                    f"Performance below {MIN_PERFORMANCE:.0%}: "
                    f"{seller.rating.performance:.0%}"
                )

            if seller.rating.total_count < MIN_REVIEWS:
                issues.append(
                    f"Insufficient reviews: {seller.rating.total_count}"
                )

        if issues:
            print(f"⚠ Issues found for {seller.title}:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"✓ {seller.title} meets all performance criteria")
```

---

## Best Practices

### 1. Cache Seller Information

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    cache_config={
        "enabled": True,
        "backend": "memory",
        "ttl": 600  # Cache for 10 minutes
    }
)

async with DigikalaClient(config=config) as client:
    # Seller info cached for 10 minutes
    seller_data = await client.sellers.get_seller_info(sku="seller-sku")
```

### 2. Handle Pagination Efficiently

```python
async with DigikalaClient(api_key="your-api-key") as client:
    sku = "seller-sku"
    page = 1

    while True:
        response = await client.sellers.get_seller_products(sku=sku, page=page)

        # Process products on this page
        for product in response.data.products:
            await process_product(product)

        if page >= response.data.pager.total_pages:
            break
        page += 1
```

### 3. Validate Seller Data

```python
async with DigikalaClient(api_key="your-api-key") as client:
    seller_data = await client.sellers.get_seller_info(sku="seller-sku")
    seller = seller_data.data.seller

    # Always check for None values
    if seller.rating:
        rating = seller.rating
        performance = rating.performance if rating.performance else 0.0
        print(f"Performance: {performance:.1%}")
    else:
        print("No rating information available")
```

---

## See Also

- [Products API Documentation](products.md)
- [Brands API Documentation](brands.md)
- [Main SDK Documentation](SDK_Documentation.md)