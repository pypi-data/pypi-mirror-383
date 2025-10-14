# Digikala SDK Documentation

<div align="center">

**Asynchronous Python SDK for Digikala API**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)]()
[![Framework](https://img.shields.io/badge/Framework-AsyncIO-green)]()
[![License](https://img.shields.io/badge/License-MIT-yellow)]()

</div>

---

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Modules](#api-modules)
  - [Products API](products.md)
  - [Sellers API](sellers.md)
  - [Brands API](brands.md)
- [Advanced Features](#advanced-features)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Introduction

The Digikala SDK is a modern, asynchronous Python library that provides a clean and intuitive interface to the Digikala API. Built on top of `httpx` and `pydantic`, it offers type-safe, fully async/await support for building high-performance applications.

### Why Use This SDK?

- **🚀 Fully Asynchronous**: Built on `asyncio` for maximum performance
- **✅ Type-Safe**: Comprehensive Pydantic models with full type hints
- **🔄 Automatic Retries**: Intelligent retry logic with exponential backoff
- **⚡ Rate Limiting**: Client-side rate limiting to prevent API quota exhaustion
- **💾 Caching**: Optional response caching (memory or Redis)
- **🛡️ Error Handling**: Comprehensive exception hierarchy
- **📝 Well-Documented**: Extensive documentation with examples
- **🧪 Tested**: High test coverage (95%+)

---

## Features

### Core Features

- **Async/Await Support**: Built for modern async Python applications
- **Type Safety**: Full Pydantic v2 validation and serialization
- **Connection Pooling**: Efficient HTTP connection management
- **Automatic Retries**: Configurable retry logic with exponential backoff
- **Error Handling**: Detailed exception types for different error scenarios

### Advanced Features

- **Client-Side Rate Limiting**: Prevent API quota exhaustion (requires `aiolimiter`)
- **Response Caching**: Cache GET requests in memory or Redis (requires `aiocache`)
- **Request Validation**: Security checks to prevent injection attacks
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

### API Coverage

| Module | Description | Status |
|--------|-------------|--------|
| **Products** | Product details and search | ✅ Supported |
| **Sellers** | Seller information and product listings | ✅ Supported |
| **Brands** | Brand information and product listings | ✅ Supported |

---

## Installation

### Basic Installation

```bash
pip install digikala-sdk
```

### With Optional Features

```bash
# With rate limiting support
pip install digikala-sdk[ratelimit]

# With caching support
pip install digikala-sdk[cache]

# With all features
pip install digikala-sdk[full]
```

### For Development

```bash
# Clone repository
git clone https://github.com/digikala/digikala-sdk.git
cd digikala-sdk

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

---

## Quick Start

### Basic Usage

```python
import asyncio
from digikala_sdk import DigikalaClient

async def main():
    # Create client with API key
    async with DigikalaClient(api_key="your-api-key") as client:
        # Get product details
        product = await client.products.get_product(id=12345)
        print(f"Product: {product.data.product.title_fa}")
        print(f"Price: {product.data.product.default_variant.price.selling_price:,} Rials")

        # Search for products
        results = await client.products.search(q="laptop")
        print(f"\nFound {results.data.pager.total_items} products")

        for product in results.data.products[:5]:  # Show first 5
            print(f"- {product.title_fa}")

# Run the async function
asyncio.run(main())
```

### With Bearer Token

```python
async with DigikalaClient(bearer_token="your-bearer-token") as client:
    product = await client.products.get_product(id=12345)
```

### Manual Lifecycle Management

```python
from digikala_sdk import DigikalaClient

client = DigikalaClient(api_key="your-api-key")

# Open connection
await client.open()

try:
    # Use client
    product = await client.products.get_product(id=12345)
    print(product.data.product.title_fa)
finally:
    # Always close
    await client.close()
```

---

## Configuration

### Basic Configuration

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    timeout=60.0,          # Request timeout in seconds
    max_retries=5,         # Maximum retry attempts
    retry_delay=2.0,       # Initial retry delay
    retry_backoff=2.0      # Exponential backoff multiplier
)

async with DigikalaClient(config=config) as client:
    # Use client with custom config
    product = await client.products.get_product(id=12345)
```

### Connection Pool Configuration

```python
config = DigikalaConfig(
    api_key="your-api-key",
    max_connections=200,              # Max total connections
    max_keepalive_connections=50,     # Max idle connections
    keepalive_expiry=30.0             # Idle connection timeout
)
```

### Rate Limiting Configuration

```python
config = DigikalaConfig(
    api_key="your-api-key",
    rate_limit_requests=50  # Max 50 requests per minute
)

async with DigikalaClient(config=config) as client:
    # Requests automatically throttled to 50/minute
    for product_id in range(100):
        product = await client.products.get_product(id=product_id)
```

### Caching Configuration

#### Memory Cache

```python
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

#### Redis Cache

```python
config = DigikalaConfig(
    api_key="your-api-key",
    cache_config={
        "enabled": True,
        "backend": "redis",
        "redis": {
            "endpoint": "localhost",
            "port": 6379
        },
        "ttl": 600  # Cache for 10 minutes
    }
)
```

### Full Configuration Example

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    # Authentication
    api_key="your-api-key",

    # API settings
    base_url="https://api.digikala.com",
    timeout=60.0,

    # Retry configuration
    max_retries=5,
    retry_delay=2.0,
    retry_backoff=2.0,
    retry_status_codes=(429, 500, 502, 503, 504),

    # Connection pool
    max_connections=200,
    max_keepalive_connections=50,
    keepalive_expiry=30.0,

    # Rate limiting
    rate_limit_requests=100,  # 100 requests/minute

    # Caching
    cache_config={
        "enabled": True,
        "backend": "redis",
        "redis": {
            "endpoint": "redis.example.com",
            "port": 6379
        },
        "ttl": 600
    }
)

async with DigikalaClient(config=config) as client:
    # Fully optimized client
    product = await client.products.get_product(id=12345)
```

---

## API Modules

The SDK is organized into service modules, each handling a specific domain of the Digikala API.

### Products API

Access product details and search functionality.

```python
async with DigikalaClient(api_key="your-api-key") as client:
    # Get product details
    product = await client.products.get_product(id=12345)

    # Search products
    results = await client.products.search(q="iphone", page=1)
```

**[📚 Full Products API Documentation →](products.md)**

### Sellers API

Access seller information and their product listings.

```python
async with DigikalaClient(api_key="your-api-key") as client:
    # Get seller products
    seller_data = await client.sellers.get_seller_products(
        sku="seller-sku-code",
        page=1
    )

    # Get seller info only
    seller_info = await client.sellers.get_seller_info(sku="seller-sku-code")
```

**[📚 Full Sellers API Documentation →](sellers.md)**

### Brands API

Access brand information and their product listings.

```python
async with DigikalaClient(api_key="your-api-key") as client:
    # Get brand products
    brand_data = await client.brands.get_brand_products(
        code="samsung",
        page=1
    )

    # Get brand info only
    brand_info = await client.brands.get_brand_info(code="samsung")
```

**[📚 Full Brands API Documentation →](brands.md)**

---

## Advanced Features

### Rate Limiting

Protect your application from exceeding API quotas with client-side rate limiting.

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    rate_limit_requests=50  # 50 requests per minute
)

async with DigikalaClient(config=config) as client:
    # Process many products safely
    for product_id in product_ids:
        product = await client.products.get_product(id=product_id)
        # Automatically waits if rate limit is reached
```

### Response Caching

Improve performance and reduce API calls with automatic caching.

```python
from digikala_sdk import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    cache_config={
        "enabled": True,
        "backend": "memory",
        "ttl": 300  # 5 minutes
    }
)

async with DigikalaClient(config=config) as client:
    # Only GET requests are cached
    product1 = await client.products.get_product(id=12345)  # API call
    product2 = await client.products.get_product(id=12345)  # From cache

    # POST/PUT/DELETE requests are never cached
    results = await client.products.search(q="laptop")  # Always hits API
```

### Logging

Enable detailed logging for debugging and monitoring.

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set SDK logger level
logger = logging.getLogger("digikala_sdk")
logger.setLevel(logging.DEBUG)

# Now you'll see detailed logs
async with DigikalaClient(api_key="your-api-key") as client:
    product = await client.products.get_product(id=12345)
    # Logs: request details, cache hits/misses, rate limiting, retries, etc.
```

---

## Error Handling

The SDK provides a comprehensive exception hierarchy for handling different error scenarios.

### Exception Hierarchy

```
DigikalaAPIError (base exception)
├── BadRequestError (400)
├── UnauthorizedError (401)
├── ForbiddenError (403)
├── NotFoundError (404)
├── RateLimitError (429)
├── ServerError (5xx)
├── TimeoutError
├── ConnectionError
└── ValidationError
```

### Basic Error Handling

```python
from digikala_sdk import DigikalaClient
from digikala_sdk.exceptions import (
    NotFoundError,
    UnauthorizedError,
    RateLimitError,
    DigikalaAPIError
)

async with DigikalaClient(api_key="your-api-key") as client:
    try:
        product = await client.products.get_product(id=12345)
        print(product.data.product.title_fa)

    except NotFoundError:
        print("Product not found")

    except UnauthorizedError:
        print("Invalid API key")

    except RateLimitError as e:
        print(f"Rate limited. Retry after {e.retry_after} seconds")

    except DigikalaAPIError as e:
        print(f"API error: {e}")
        if hasattr(e, 'status_code'):
            print(f"Status code: {e.status_code}")
```

### Advanced Error Handling

```python
import asyncio
from digikala_sdk import DigikalaClient
from digikala_sdk.exceptions import (
    RateLimitError,
    ServerError,
    TimeoutError,
    ConnectionError
)

async def fetch_product_with_retry(client, product_id, max_attempts=3):
    """Fetch product with custom retry logic."""
    for attempt in range(max_attempts):
        try:
            return await client.products.get_product(id=product_id)

        except RateLimitError as e:
            if e.retry_after:
                print(f"Rate limited, waiting {e.retry_after}s...")
                await asyncio.sleep(e.retry_after)
            else:
                await asyncio.sleep(60)  # Default 1 minute
            continue

        except (ServerError, TimeoutError, ConnectionError) as e:
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Error: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            raise

    raise Exception(f"Failed to fetch product after {max_attempts} attempts")
```

---

## Best Practices

### 1. Always Use Context Manager

```python
# ✅ Good
async with DigikalaClient(api_key="your-api-key") as client:
    product = await client.products.get_product(id=12345)

# ❌ Avoid
client = DigikalaClient(api_key="your-api-key")
product = await client.products.get_product(id=12345)
# Connection not properly closed!
```

### 2. Handle Pagination Efficiently

```python
# ✅ Good - Process one page at a time
async with DigikalaClient(api_key="your-api-key") as client:
    page = 1
    while True:
        results = await client.products.search(q="laptop", page=page)

        # Process this page
        for product in results.data.products:
            await process_product(product)

        if page >= results.data.pager.total_pages:
            break
        page += 1

# ❌ Avoid - Loading all pages into memory
async with DigikalaClient(api_key="your-api-key") as client:
    all_products = []
    for page in range(1, 100):  # Don't know total pages
        results = await client.products.search(q="laptop", page=page)
        all_products.extend(results.data.products)  # Memory intensive!
```

### 3. Check for Optional Fields

```python
# ✅ Good
product = await client.products.get_product(id=12345)

if product.data.product.default_variant:
    price = product.data.product.default_variant.price
    print(f"Price: {price.selling_price}")
else:
    print("No pricing information available")

# ❌ Avoid
product = await client.products.get_product(id=12345)
price = product.data.product.default_variant.price  # May be None!
```

### 4. Use Rate Limiting for Bulk Operations

```python
# ✅ Good
config = DigikalaConfig(
    api_key="your-api-key",
    rate_limit_requests=50
)

async with DigikalaClient(config=config) as client:
    for product_id in large_product_list:
        product = await client.products.get_product(id=product_id)
        # Automatically throttled

# ❌ Avoid - No rate limiting
async with DigikalaClient(api_key="your-api-key") as client:
    for product_id in large_product_list:
        product = await client.products.get_product(id=product_id)
        # May hit API rate limits!
```

### 5. Enable Caching for Read-Heavy Workloads

```python
# ✅ Good for read-heavy applications
config = DigikalaConfig(
    api_key="your-api-key",
    cache_config={
        "enabled": True,
        "backend": "redis",
        "ttl": 300
    }
)

async with DigikalaClient(config=config) as client:
    # Repeated calls are cached
    product = await client.products.get_product(id=12345)
```

### 6. Use Proper Logging

```python
# ✅ Good
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async with DigikalaClient(api_key="your-api-key") as client:
    try:
        product = await client.products.get_product(id=12345)
        logger.info(f"Fetched product: {product.data.product.title_fa}")
    except Exception as e:
        logger.error(f"Failed to fetch product: {e}", exc_info=True)
```

---

## Examples

### Example 1: Product Price Monitor

```python
import asyncio
from digikala_sdk import DigikalaClient

async def monitor_product_price(product_id: int):
    """Monitor product price and notify on changes."""
    async with DigikalaClient(api_key="your-api-key") as client:
        product = await client.products.get_product(id=product_id)

        if product.data.product.default_variant:
            price = product.data.product.default_variant.price
            print(f"Product: {product.data.product.title_fa}")
            print(f"Current Price: {price.selling_price:,} Rials")

            if price.discount_percent > 0:
                print(f"🔥 Discount: {price.discount_percent}%")
                print(f"Original Price: {price.rrp_price:,} Rials")
                print(f"You Save: {price.rrp_price - price.selling_price:,} Rials")

asyncio.run(monitor_product_price(12345))
```

### Example 2: Top Rated Products Finder

```python
async def find_top_rated_products(search_query: str, min_rating: float = 4.5):
    """Find top-rated products matching search query."""
    async with DigikalaClient(api_key="your-api-key") as client:
        results = await client.products.search(q=search_query)

        top_products = [
            p for p in results.data.products
            if p.rating and p.rating.rate >= min_rating and p.rating.count >= 10
        ]

        print(f"Top-rated {search_query} products:")
        for product in top_products:
            print(f"- {product.title_fa}")
            print(f"  Rating: {product.rating.rate}/5 ({product.rating.count} reviews)")

            if product.default_variant and product.default_variant.price:
                price = product.default_variant.price
                print(f"  Price: {price.selling_price:,} Rials")

asyncio.run(find_top_rated_products("laptop", min_rating=4.5))
```

### Example 3: Brand Comparison Tool

```python
async def compare_brands(brand_codes: list):
    """Compare multiple brands."""
    async with DigikalaClient(api_key="your-api-key") as client:
        print("Brand Comparison Report")
        print("=" * 60)

        for code in brand_codes:
            brand_data = await client.brands.get_brand_info(code=code)
            brand = brand_data.data.brand
            products = brand_data.data.products

            print(f"\n{brand.title_fa}:")
            print(f"  Total Products: {brand_data.data.pager.total_items}")

            # Calculate average price
            prices = [
                p.default_variant.price.selling_price
                for p in products
                if p.default_variant and p.default_variant.price
            ]

            if prices:
                avg_price = sum(prices) // len(prices)
                print(f"  Avg Price (sample): {avg_price:,} Rials")

            # Check premium status
            if brand.is_premium:
                print("  ✓ Premium Brand")

asyncio.run(compare_brands(["samsung", "apple", "xiaomi"]))
```

### Example 4: Seller Performance Dashboard

```python
async def seller_dashboard(seller_sku: str):
    """Generate seller performance dashboard."""
    async with DigikalaClient(api_key="your-api-key") as client:
        seller_data = await client.sellers.get_seller_info(sku=seller_sku)
        seller = seller_data.data.seller

        print(f"\n{'=' * 60}")
        print(f"Seller Dashboard: {seller.title}")
        print(f"{'=' * 60}")

        print(f"\nOverall Rating: {seller.stars}/5")

        if seller.rating:
            rating = seller.rating
            print(f"Total Reviews: {rating.total_count}")
            print(f"\nPerformance Metrics:")
            print(f"  Performance: {rating.performance * 100:.1f}%")
            print(f"  Commitment: {rating.commitment * 100:.1f}%")
            print(f"  Shipping: {rating.shipping * 100:.1f}%")
            print(f"  No Returns: {rating.no_return * 100:.1f}%")

        print(f"\nTotal Products: {seller_data.data.pager.total_items}")

asyncio.run(seller_dashboard("seller-sku-code"))
```

---

## Troubleshooting

### Rate Limiting Not Working

**Problem**: Requests are not being throttled

**Solution**:
```bash
pip install aiolimiter
```

Verify in logs:
```python
import logging
logging.basicConfig(level=logging.INFO)

# Should see: "Rate limiting enabled: X requests/minute"
```

### Caching Not Working

**Problem**: No cache hits in logs

**Solution**:
```bash
# For memory cache
pip install aiocache

# For Redis cache
pip install aiocache[redis]
```

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Should see "Cache hit" or "Cache miss" messages
```

### Connection Errors

**Problem**: `ConnectionError` or timeout errors

**Solutions**:
1. Check your internet connection
2. Verify API endpoint is accessible
3. Increase timeout:
```python
config = DigikalaConfig(
    api_key="your-api-key",
    timeout=120.0  # Increase to 2 minutes
)
```

### Authentication Errors

**Problem**: `UnauthorizedError` (401)

**Solutions**:
1. Verify API key is correct
2. Check if API key has required permissions
3. Try with bearer token instead:
```python
client = DigikalaClient(bearer_token="your-token")
```

---

## Contributing

We welcome contributions! Here's how you can help:

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/digikala/digikala-sdk.git
cd digikala-sdk

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=src tests/
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_products.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html tests/
```

### Code Style

We follow PEP 8 and use:
- `black` for code formatting
- `isort` for import sorting
- `mypy` for type checking

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type check
mypy src/
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

## Support

- **Documentation**: [Full API Documentation](SDK_Documentation.md)
- **Issues**: [GitHub Issues](https://github.com/digikala/digikala-sdk/issues)
- **Email**: sdk@digikala.com

---

<div align="center">

**Made with ❤️ by the Digikala SDK Team**

[Products API](products.md) • [Sellers API](sellers.md) • [Brands API](brands.md)

</div>