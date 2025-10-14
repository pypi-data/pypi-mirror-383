# Error Handling Guide

این راهنما نحوه مدیریت خطاها در Digikala SDK را توضیح می‌دهد.

## خلاصه سریع

وقتی API response با `status != 200` برمی‌گردد، SDK به صورت خودکار `APIStatusError` را raise می‌کند:

```python
from src import DigikalaClient, APIStatusError

async with DigikalaClient(api_key="...") as client:
    try:
        product = await client.products.get_product(id=12345)
        print(product.data.product.title_fa)
    except APIStatusError as e:
        print(f"Error [{e.status_code}]: {e.message}")
```

## انواع خطاها

### 1. APIStatusError (خطای سطح Application)

این خطا زمانی raise می‌شود که HTTP response موفق است (200 OK) اما در body response، field `status` برابر با 200 نیست:

```python
# مثال: API با HTTP 200 OK جواب می‌دهد
# اما در body: {"status": 404, "data": null}

try:
    seller = await client.sellers.get_seller_products(sku="INVALID", page=1)
except APIStatusError as e:
    print(f"Status Code: {e.status_code}")  # 404
    print(f"Message: {e.message}")           # "Not Found - Resource does not exist"
    print(f"Response: {e.response}")         # Full response data
```

### 2. Status Code های معمول

| کد | معنی | نمونه |
|----|------|-------|
| 400 | Bad Request | پارامترهای نامعتبر |
| 401 | Unauthorized | API key نامعتبر یا نداشتن |
| 403 | Forbidden | عدم دسترسی به resource |
| 404 | Not Found | Resource وجود ندارد |
| 429 | Rate Limit | تعداد درخواست‌ها زیاد است |
| 500 | Server Error | خطای سرور |
| 502 | Bad Gateway | مشکل gateway |
| 503 | Service Unavailable | سرویس در دسترس نیست |

## الگوهای مدیریت خطا

### 1. مدیریت ساده

```python
try:
    result = await client.products.get_product(id=12345)
except APIStatusError as e:
    print(f"Error: {e}")
```

### 2. مدیریت بر اساس Status Code

```python
try:
    seller = await client.sellers.get_seller_products(sku="TEST", page=1)
    print(f"Found: {seller.data.seller.title}")
except APIStatusError as e:
    if e.status_code == 404:
        print("Seller not found")
    elif e.status_code == 403:
        print("Access denied")
    elif e.status_code >= 500:
        print("Server error, try again later")
    else:
        print(f"Unknown error: {e.message}")
```

### 3. Batch Processing با Error Handling

```python
sellers = ["SELLER1", "INVALID", "SELLER3"]
results = {"success": [], "failed": []}

for sku in sellers:
    try:
        data = await client.sellers.get_seller_products(sku=sku, page=1)
        results["success"].append(data.data.seller.title)
    except APIStatusError as e:
        results["failed"].append({"sku": sku, "error": str(e)})

print(f"Success: {len(results['success'])}, Failed: {len(results['failed'])}")
```

### 4. Retry Pattern برای خطاهای موقت

```python
max_retries = 3
for attempt in range(max_retries):
    try:
        result = await client.products.get_product(id=12345)
        break  # Success
    except APIStatusError as e:
        # فقط برای خطاهای سرور (5xx) retry کن
        if 500 <= e.status_code < 600 and attempt < max_retries - 1:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            continue
        else:
            raise  # خطاهای 4xx یا آخرین تلاش
```

### 5. Context-Aware Error Handling

```python
async def safe_get_seller(sku: str):
    """Get seller with comprehensive error handling."""
    try:
        data = await client.sellers.get_seller_products(sku=sku, page=1)
        return {
            "success": True,
            "data": data.data,
            "message": f"Found: {data.data.seller.title}"
        }
    except APIStatusError as e:
        return {
            "success": False,
            "data": None,
            "message": f"Error [{e.status_code}]: {e.message}",
            "status_code": e.status_code
        }

# استفاده
result = await safe_get_seller("TEST")
if result["success"]:
    print(f"✓ {result['message']}")
else:
    print(f"✗ {result['message']}")
```

## Best Practices

### ✅ انجام دهید

1. **همیشه خطاها را handle کنید**:
```python
try:
    result = await client.products.get_product(id=12345)
except APIStatusError as e:
    logger.error(f"Failed to get product: {e}")
```

2. **خطاهای مختلف را متفاوت handle کنید**:
```python
if e.status_code == 404:
    # Resource پیدا نشد - این طبیعی است
    pass
elif e.status_code >= 500:
    # خطای سرور - باید retry کرد
    retry()
```

3. **اطلاعات کامل خطا را log کنید**:
```python
except APIStatusError as e:
    logger.error(
        f"API Error: status={e.status_code}, "
        f"message={e.message}, response={e.response}"
    )
```

4. **برای خطاهای سرور retry کنید، نه خطاهای client**:
```python
# ✓ درست
if e.status_code >= 500:
    await retry()

# ✗ غلط - 404 یعنی resource وجود ندارد، retry فایده ندارد
if e.status_code == 404:
    await retry()  # Bad!
```

### ❌ انجام ندهید

1. **خطاها را ignore نکنید**:
```python
# ✗ غلط
try:
    result = await client.products.get_product(id=12345)
except:
    pass  # Bad!
```

2. **همه exception ها را یکسان handle نکنید**:
```python
# ✗ غلط
except Exception as e:
    print("An error occurred")  # خیلی کلی است
```

3. **به `data` در زمان خطا دسترسی نداشته باشید**:
```python
# ✗ غلط - وقتی status != 200، data ممکن است None باشد
try:
    result = await client.products.get_product(id=12345)
except APIStatusError as e:
    print(result.data.product.title)  # Error! result doesn't exist
```

## نمونه‌های کامل

برای مثال‌های کامل‌تر، فایل‌های زیر را ببینید:

- `examples/basic_usage.py` - مثال‌های پایه با error handling
- `examples/error_handling_example.py` - مثال‌های تخصصی error handling

## راه اندازی و تست

```bash
# نصب dependencies
pip install -e .

# اجرای مثال‌های error handling
python examples/error_handling_example.py

# اجرای تست‌ها
pytest tests/test_error_handling.py -v
```

## منابع بیشتر

- [Exception Hierarchy](src/exceptions.py) - لیست کامل exception ها
- [Base Response Model](src/models/common_models.py) - پیاده‌سازی validation
- [Tests](tests/test_error_handling.py) - تست‌های error handling

## پشتیبانی

اگر مشکلی با error handling دارید:

1. لاگ کامل خطا را بررسی کنید
2. مقدار `e.status_code` و `e.response` را چک کنید
3. مستندات API Digikala را بررسی کنید
4. Issue باز کنید در [GitHub Repository](https://github.com/your-repo)