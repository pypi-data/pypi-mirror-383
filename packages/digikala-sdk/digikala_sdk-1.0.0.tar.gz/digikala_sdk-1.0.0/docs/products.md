# Products API Documentation

## Overview

The `ProductsService` provides access to product-related API endpoints, allowing you to retrieve detailed product information and perform product searches.

## Class: ProductsService

### Initialization

The `ProductsService` is automatically initialized when you create a `DigikalaClient` instance and is accessible via `client.products`.

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Access products service
    products = client.products
```

---

## Methods

### `get_product()`

Get detailed product information by product ID.

#### Signature

```python
async def get_product(id: int) -> ProductDetailResponse
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `int` | ✅ Yes | Product ID to retrieve |

#### Returns

`ProductDetailResponse` - Complete product details including:
- Product information (title, description, images)
- Brand and category information
- Pricing and availability
- Seller information
- Product specifications
- Reviews and ratings

#### Raises

- `NotFoundError`: Product with given ID does not exist
- `DigikalaAPIError`: Other API errors

#### Example Usage

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Get product details
    product = await client.products.get_product(id=12345)

    # Access product information
    print(f"Title: {product.data.product.title_fa}")
    print(f"English Title: {product.data.product.title_en}")
    print(f"Status: {product.data.product.status}")

    # Access pricing information
    if product.data.product.default_variant:
        price = product.data.product.default_variant.price
        print(f"Selling Price: {price.selling_price:,} Rials")
        print(f"RRP: {price.rrp_price:,} Rials")
        if price.discount_percent > 0:
            print(f"Discount: {price.discount_percent}%")

    # Access brand information
    if product.data.product.brand:
        brand = product.data.product.brand
        print(f"Brand: {brand.title_fa}")
        print(f"Brand Code: {brand.code}")

    # Access category information
    if product.data.product.category:
        category = product.data.product.category
        print(f"Category: {category.title_fa}")

    # Access rating information
    if product.data.product.rating:
        rating = product.data.product.rating
        print(f"Rating: {rating.rate}/5")
        print(f"Total Reviews: {rating.count}")
```

#### Handling Inactive Products

```python
async with DigikalaClient(api_key="your-api-key") as client:
    product = await client.products.get_product(id=12345)

    # Check if product is inactive
    if product.data.product.is_inactive:
        print("Product is inactive or unavailable")
    else:
        print(f"Product: {product.data.product.title_fa}")
        print(f"Price: {product.data.product.default_variant.price.selling_price}")
```

---

### `search()`

Search for products using a query string with pagination support.

#### Signature

```python
async def search(q: str, page: Optional[int] = 1) -> ProductSearchResponse
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | `str` | ✅ Yes | - | Search query string |
| `page` | `int` | ❌ No | `1` | Page number for pagination |

#### Returns

`ProductSearchResponse` - Search results including:
- List of matching products
- Pagination information (total items, total pages, current page)
- Quick filters
- Sort options

#### Raises

- `BadRequestError`: Invalid query parameters
- `DigikalaAPIError`: Other API errors

#### Example Usage

**Basic Search:**

```python
from digikala_sdk import DigikalaClient

async with DigikalaClient(api_key="your-api-key") as client:
    # Search for iPhone products
    results = await client.products.search(q="iphone")

    # Display pagination info
    pager = results.data.pager
    print(f"Total Items: {pager.total_items}")
    print(f"Total Pages: {pager.total_pages}")
    print(f"Current Page: {pager.current_page}")

    # Display products
    for product in results.data.products:
        print(f"\n- {product.title_fa}")
        print(f"  ID: {product.id}")
        print(f"  Status: {product.status}")

        if product.default_variant and product.default_variant.price:
            price = product.default_variant.price
            print(f"  Price: {price.selling_price:,} Rials")
```

**Paginated Search:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    # Search with pagination
    page = 1
    all_products = []

    while True:
        results = await client.products.search(q="laptop", page=page)
        all_products.extend(results.data.products)

        print(f"Fetched page {page}/{results.data.pager.total_pages}")

        # Check if we've reached the last page
        if page >= results.data.pager.total_pages:
            break

        page += 1

    print(f"\nTotal products fetched: {len(all_products)}")
```

**Working with Search Results:**

```python
async with DigikalaClient(api_key="your-api-key") as client:
    results = await client.products.search(q="samsung phone")

    for product in results.data.products:
        # Product information
        print(f"\nProduct: {product.title_fa}")

        # Check if product has DigiPlus
        if product.digiplus.is_digiplus:
            print("  ✓ DigiPlus eligible")

        # Check shipping
        if product.properties.is_fast_shipping:
            print("  ✓ Fast shipping available")

        # Check rating
        if product.rating and product.rating.count > 0:
            print(f"  Rating: {product.rating.rate}/5 ({product.rating.count} reviews)")

        # Display colors if available
        if product.colors:
            color_names = [color.title for color in product.colors]
            print(f"  Available Colors: {', '.join(color_names)}")
```

---

## Response Models

### ProductDetailResponse

```python
{
    "status": 200,
    "data": {
        "product": {
            "id": int,
            "title_fa": str,
            "title_en": str,
            "status": str,
            "is_inactive": bool,
            "url": {"uri": str},
            "brand": {
                "id": int,
                "code": str,
                "title_fa": str,
                "title_en": str
            },
            "category": {
                "id": int,
                "code": str,
                "title_fa": str,
                "title_en": str
            },
            "default_variant": {
                "id": int,
                "price": {
                    "selling_price": int,
                    "rrp_price": int,
                    "discount_percent": int
                },
                "seller": {
                    "id": int,
                    "title": str
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
    }
}
```

### ProductSearchResponse

```python
{
    "status": 200,
    "data": {
        "products": [
            {
                "id": int,
                "title_fa": str,
                "title_en": str,
                "status": str,
                "url": {"uri": str},
                "default_variant": {...},
                "rating": {...}
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
        # Try to get a product
        product = await client.products.get_product(id=12345)
        print(product.data.product.title_fa)

    except NotFoundError as e:
        print(f"Product not found: {e}")

    except BadRequestError as e:
        print(f"Invalid request: {e}")

    except DigikalaAPIError as e:
        print(f"API error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
```

---

## Best Practices

### 1. Use Context Manager

Always use the async context manager to ensure proper cleanup:

```python
async with DigikalaClient(api_key="your-api-key") as client:
    product = await client.products.get_product(id=12345)
```

### 2. Handle Pagination Efficiently

For large result sets, process pages one at a time:

```python
page = 1
while True:
    results = await client.products.search(q="query", page=page)

    # Process this page's products
    for product in results.data.products:
        process_product(product)

    if page >= results.data.pager.total_pages:
        break
    page += 1
```

### 3. Check for Null Values

Always check for optional fields before accessing:

```python
product = await client.products.get_product(id=12345)

if product.data.product.default_variant:
    price = product.data.product.default_variant.price
    print(f"Price: {price.selling_price}")
else:
    print("No variant information available")
```

### 4. Use Rate Limiting

Enable rate limiting to avoid hitting API limits:

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    rate_limit_requests=50  # 50 requests per minute
)

async with DigikalaClient(config=config) as client:
    # Requests automatically throttled
    for product_id in product_ids:
        product = await client.products.get_product(id=product_id)
```

### 5. Enable Caching for Read Operations

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    cache_config={
        "enabled": True,
        "backend": "memory",
        "ttl": 300  # Cache for 5 minutes
    }
)

async with DigikalaClient(config=config) as client:
    # First call hits API
    product1 = await client.products.get_product(id=12345)

    # Second call returns from cache (within 5 minutes)
    product2 = await client.products.get_product(id=12345)
```

---

## See Also

- [Sellers API Documentation](sellers.md)
- [Brands API Documentation](brands.md)
- [Main SDK Documentation](SDK_Documentation.md)