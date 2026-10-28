# راهنمای Cloudflare Worker

## نصب و راه‌اندازی Cloudflare Worker

### 1. ایجاد Worker

1. به داشبورد Cloudflare بروید: https://dash.cloudflare.com/
2. به بخش Workers & Pages بروید
3. روی "Create Application" کلیک کنید
4. روی "Create Worker" کلیک کنید
5. یک نام برای Worker انتخاب کنید (مثلاً: "pdf-translator-worker")
6. روی "Deploy" کلیک کنید

### 2. کد Worker

کد Worker را در بخش "Edit code" جایگزین کنید:

```javascript
/**
 * Cloudflare Worker for PDF Translation
 */

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url)

    if (url.pathname === '/translate') {
        return handleTranslation(request)
    }

    return new Response('PDF Translator Worker', { status: 200 })
}

async function handleTranslation(request) {
    const body = await request.json()
    const { text, apiKey } = body

    try {
        const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                contents: [{
                    parts: [{ text }]
                }],
                generationConfig: {
                    temperature: 0.3,
                    maxOutputTokens: 4096
                }
            })
        })

        const data = await response.json()

        return new Response(JSON.stringify(data), {
            status: response.status,
            headers: { 'Content-Type': 'application/json' }
        })
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
            headers: { 'Content-Type': 'application/json' }
        })
    }
}
```

### 3. اجرای Worker محلی

برای تست:

```bash
# نصب Wrangler CLI
npm install -g wrangler

# لاگین
wrangler login

# اجرا در محلی
wrangler dev

# خروجی URL
# معمولاً: http://localhost:8787
```

### 4. استفاده در اپلیکیشن

در `translator.py`:

```python
self.worker_translator = CloudflareWorkerTranslator(
    worker_url="http://127.0.0.1:8787",  # یا URL از Cloudflare
    api_manager=self.api_manager
)
```

### 5. استفاده از Worker واقعی

URL Worker واقعی را در `app.py` تنظیم کنید:

```python
self.worker_url = "https://pdf-translator-worker.your-subdomain.workers.dev"
```

## مزایای استفاده از Worker

✅ دور زدن محدودیت‌های ایران
✅ مدیریت بهتر درخواست‌ها
✅ امنیت بیشتر
✅ سرعت بهتر

## نکات مهم

- Worker باید در دسترس باشد
- کلید API را در سرور امن نگه دارید
- محدودیت‌های Worker را چک کنید
- از caching استفاده کنید برای بهینه‌سازی
