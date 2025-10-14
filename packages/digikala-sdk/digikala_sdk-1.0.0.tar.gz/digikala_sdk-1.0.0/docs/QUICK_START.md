# Digikala SDK - Quick Start Guide

## 🚀 Installation

```bash
pip install httpx pydantic
```

## 💡 Basic Usage

### 1. Get Product Details

```python
import asyncio
from src import DigikalaClient

async def main():
    async with DigikalaClient(api_key="your-api-key") as client:
        product = await client.products.get_product(id=20365865)
        print(f"Product: {product.data.product.title_fa}")
        print(f"Price: {product.data.product.default_variant.price.selling_price:,} Rials")

asyncio.run(main())
```

### 2. Search Products

```python
async def main():
    async with DigikalaClient(api_key="your-api-key") as client:
        results = await client.products.search(q="iphone13", page=1)

        for product in results.data.products:
            print(f"- {product.title_fa}")
            print(f"  Price: {product.default_variant.price.selling_price:,}")

asyncio.run(main())
```

### 3. Get Seller Information

```python
async def main():
    async with DigikalaClient(api_key="your-api-key") as client:
        seller_data = await client.sellers.get_seller_products(id=1792558, page=1)

        print(f"Seller: {seller_data.data.seller.title}")
        print(f"Rating: {seller_data.data.seller.stars}/5")
        print(f"Products: {len(seller_data.data.products)}")

asyncio.run(main())
```

## 🔧 FastAPI Integration

```python
from fastapi import FastAPI
from src import DigikalaClient

app = FastAPI()
client = DigikalaClient(api_key="your-api-key")

@app.on_event("startup")
async def startup():
    await client.open()

@app.on_event("shutdown")
async def shutdown():
    await client.close()

@app.get("/products/{product_id}")
async def get_product(product_id: int):
    result = await client.products.get_product(id=product_id)
    return result.data.product
```

## ⚙️ Configuration

```python
from src import DigikalaClient, DigikalaConfig

config = DigikalaConfig(
    api_key="your-api-key",
    timeout=30.0,
    max_retries=3,
    retry_delay=1.0,
    retry_backoff=2.0
)

async with DigikalaClient(config=config) as client:
    # Use client
    pass
```

## 🚨 Error Handling

```python
from src.exceptions import NotFoundError, RateLimitError

async with DigikalaClient(api_key="your-key") as client:
    try:
        product = await client.products.get_product(id=12345)
    except NotFoundError:
        print("Product not found")
    except RateLimitError as e:
        print(f"Rate limit exceeded, retry after {e.retry_after}s")
```

## 📊 Available Methods

### Products Service
```python
# Get product details
product = await client.products.get_product(id=12345)

# Search products
results = await client.products.search(q="laptop", page=1)
```

### Sellers Service
```python
# Get seller and products
seller_data = await client.sellers.get_seller_products(id=123456, page=1)

# Get seller info only
seller_info = await client.sellers.get_seller_info(id=123456)
```

## 🧪 Running Tests

```bash
pip install pytest pytest-asyncio respx
pytest tests/ -v
```

## 📚 More Examples

Check the `examples/` directory for:
- `basic_usage.py` - Complete usage examples
- `error_handling.py` - Error handling patterns

## 📖 Full Documentation

See `README.md` for complete documentation.

## 🆘 Support

For issues or questions, refer to:
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `README.md` - Full documentation
- Test files in `tests/` - Usage patterns