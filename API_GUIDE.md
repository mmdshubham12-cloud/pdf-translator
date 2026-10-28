# راهنمای API

## Google Gemini API

### تنظیمات

- **Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`
- **Model**: `gemini-1.5-flash`
- **Rate Limit**: 10 requests per minute
- **Daily Limit**: 500 requests per day
- **Token Limit**: 250,000 input tokens per minute

### درخواست نمونه

```json
{
    "contents": [
        {
            "parts": [
                {
                    "text": "Translate to Persian: Hello, world!"
                }
            ]
        }
    ],
    "generationConfig": {
        "temperature": 0.3,
        "maxOutputTokens": 4096
    }
}
```

### پاسخ نمونه

```json
{
    "candidates": [
        {
            "content": {
                "parts": [
                    {
                        "text": "سلام، دنیا!"
                    }
                ]
            },
            "finishReason": "STOP",
            "finishMessage": null
        }
    ],
    "usageMetadata": {
        "promptTokenCount": 10,
        "candidatesTokenCount": 5,
        "totalTokenCount": 15
    }
}
```

## Cloudflare Worker

### Endpoint

```
POST /translate
Content-Type: application/json
Authorization: Bearer <api_key>
```

### درخواست نمونه

```json
{
    "text": "Translate to Persian: Hello, world!",
    "apiKey": "your-api-key"
}
```

### پاسخ نمونه

```json
{
    "translated_text": "سلام، دنیا!"
}
```

## محدودیت‌ها

### Rate Limit
- **۱۰ درخواست در دقیقه**: برای هر کلید API
- **محدودیت خودکار**: سیستم به صورت خودکار منتظر می‌ماند

### Daily Limit
- **۵۰۰ درخواست در روز**: برای هر کلید API
- **ذخیره وضعیت**: وضعیت در `api_stats.json` ذخیره می‌شود

### Token Limit
- **۲۵۰,۰۰۰ توکن ورودی در دقیقه**: برای هر کلید API
- **محاسبه**: تقریباً ۴ کاراکتر به ازای هر توکن

## مدیریت کلیدها

### افزودن کلید

```python
api_manager.add_api_key(name="My Key", api_key="your-api-key")
```

### تنظیم کلید پیش‌فرض

```python
api_manager.set_default_api_key(api_key="your-api-key")
```

### تغییر کلید

```python
api_manager.rotate_api_key()
```

### نمایش کلیدها

```python
api_keys = api_manager.get_api_keys()
for key in api_keys:
    print(f"{key['name']}: {key['api_key']}")
```

### حذف کلید

```python
api_manager.delete_api_key(api_key="your-api-key")
```

## آمار API

### دریافت آمار

```python
stats = api_manager.get_stats()
print(f"Daily requests: {stats['daily_requests']}/{stats['daily_limit']}")
print(f"Tokens used: {stats['tokens_used']}/{stats['tokens_limit']}")
print(f"Usage percent: {stats['usage_percent']:.1f}%")
```

### دریافت آمار کلید

```python
key_stats = api_manager.get_key_stats(api_key="your-api-key")
print(f"Name: {key_stats['name']}")
print(f"Usage: {key_stats['usage']}")
print(f"Tokens used: {key_stats['tokens_used']}")
```

## مدیریت درخواست‌ها

### ثبت درخواست

```python
api_manager.record_request(api_key="your-api-key", tokens=100)
```

### بررسی محدودیت روزانه

```python
if api_manager.check_daily_limit():
    # Proceed with request
    pass
```

### بررسی محدودیت نرخ

```python
if api_manager.check_rate_limit():
    # Proceed with request
    pass
```

### ریست آمار روزانه

```python
api_manager.reset_daily_stats()
```

## خطاهای رایج

### خطای "Invalid API key"

```json
{
    "error": {
        "message": "API key not valid. Please pass a valid API key.",
        "type": "invalid_request_error",
        "status": 401
    }
}
```

### خطای "API quota exceeded"

```json
{
    "error": {
        "message": "API key has reached its daily limit.",
        "type": "invalid_request_error",
        "status": 429
    }
}
```

### خطای "Rate limit exceeded"

```json
{
    "error": {
        "message": "Rate limit exceeded. Please try again later.",
        "type": "invalid_request_error",
        "status": 429
    }
}
```

### خطای "Invalid model"

```json
{
    "error": {
        "message": "The model 'gemini-1.5-flash' has been deprecated.",
        "type": "invalid_request_error",
        "status": 400
    }
}
```

## بهینه‌سازی

### بخش‌بندی متن‌های طولانی

```python
chunks = text.split('.')  # Split by sentences
```

### استفاده از کش

```python
# Check cache
if cached_translation in translation_cache:
    return cached_translation

# Translate and cache
translated = translate(text)
translation_cache[text] = translated
```

### مدیریت توکن‌ها

```python
# Estimate token count
token_count = len(text) // 4

# Check token limit
if api_manager.tokens_used + token_count > api_manager.tokens_limit:
    # Wait or use different key
    pass
```

## نکات مهم

1. **کلید API**: همیشه از کلید API معتبر استفاده کنید
2. **محدودیت‌ها**: محدودیت‌ها را رعایت کنید
3. **کش**: از کش برای بهینه‌سازی استفاده کنید
4. **بخش‌بندی**: متن‌های طولانی را به بخش‌های کوچک تقسیم کنید
5. **چند کلید**: از چند کلید برای بالانسینگ استفاده کنید

## نمونه کد کامل

```python
from api_manager import APIManager

# Initialize
api_manager = APIManager()

# Add API key
api_manager.add_api_key("My Key", "your-api-key")

# Set default
api_manager.set_default_api_key("your-api-key")

# Check limits
if api_manager.check_daily_limit() and api_manager.check_rate_limit():
    # Translate
    translated = api_manager.translate_text("Hello, world!")
    print(translated)

# Get stats
stats = api_manager.get_stats()
print(f"Usage: {stats['usage_percent']:.1f}%")
```
