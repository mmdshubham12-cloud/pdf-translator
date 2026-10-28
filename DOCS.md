# مستندات PDF Translator

## ساختار مستندات

```
docs/
├── README.md              # راهنمای اصلی
├── PYDROID_SETUP.md       # راهنمای Pydroid 3
├── CLOUDFLARE_SETUP.md    # راهنمای Cloudflare Worker
├── PROJECT_STRUCTURE.md   # ساختار پروژه
├── TROUBLESHOOTING.md     # راهنمای حل مشکلات
├── KV_FILES.md            # فایل‌های KV
├── CHANGELOG.md           # تغییرات
├── DEVELOPMENT.md         # راهنمای توسعه
├── API_GUIDE.md           # راهنمای API
├── BUILD.md               # راهنمای ساخت
├── API_KEYS.md            # راهنمای کلیدهای API
└── DOCS.md                # این فایل
```

## راهنمای استفاده

### نصب و راه‌اندازی

1. **نصب وابستگی‌ها**
   ```bash
   python setup.py
   ```

2. **راه‌اندازی اپلیکیشن**
   ```bash
   python app.py
   ```

3. **تنظیمات اولیه**
   - یک کلید API اضافه کنید
   - کلید پیش‌فرض را انتخاب کنید

### نحوه استفاده

1. **بارگذاری PDF**
   - روی دکمه آپلود کلیک کنید
   - فایل PDF را انتخاب کنید

2. **ترجمه PDF**
   - روی دکمه "شروع ترجمه" کلیک کنید
   - فرآیند ترجمه را مشاهده کنید

3. **تولید خروجی**
   - فرمت خروجی را انتخاب کنید (HTML یا PDF)
   - خروجی را دانلود کنید

## ویژگی‌ها

- ✅ ترجمه PDF با حفظ ساختار
- ✅ خروجی HTML و PDF
- ✅ مدیریت چند کلید API
- ✅ محدودیت‌های API
- ✅ کار با Cloudflare Worker
- ✅ رابط کاربری زیبا
- ✅ نصب خودکار

## محدودیت‌ها

- **۵۰۰ درخواست در روز**: برای هر کلید API
- **۲۵۰,۰۰۰ توکن ورودی در دقیقه**: برای هر کلید API
- **۱۰ درخواست در دقیقه**: برای هر کلید API

## ساختار پروژه

### فایل‌های اصلی
- `setup.py`: نصب خودکار
- `app.py`: برنامه اصلی
- `main.py`: نسخه خط فرمان
- `pdf_utils.py`: ابزارهای PDF
- `api_manager.py`: مدیریت API
- `translator.py`: لاجیک ترجمه
- `output_generator.py`: تولید خروجی

### فایل‌های رابط کاربری
- `ui/main_screen.kv`: صفحه اصلی
- `ui/settings_screen.kv`: صفحه تنظیمات
- `ui/progress_screen.kv`: صفحه پیشرفت

### فایل‌های تنظیمات
- `config.yaml`: تنظیمات اصلی
- `api_stats.json`: آمار API
- `cloudflare-worker.js`: ورکر کلادفلر

### فایل‌های مستندات
- `README.md`: راهنمای اصلی
- `PYDROID_SETUP.md`: راهنمای Pydroid 3
- `CLOUDFLARE_SETUP.md`: راهنمای Cloudflare Worker
- `PROJECT_STRUCTURE.md`: ساختار پروژه
- `TROUBLESHOOTING.md`: راهنمای حل مشکلات
- `KV_FILES.md`: فایل‌های KV
- `CHANGELOG.md`: تغییرات
- `DEVELOPMENT.md`: راهنمای توسعه
- `API_GUIDE.md`: راهنمای API
- `BUILD.md`: راهنمای ساخت
- `API_KEYS.md`: راهنمای کلیدهای API
- `DOCS.md`: این فایل

## نحوه کمک

### گزارش مشکلات

1. خطا را توضیح دهید
2. نسخه پایتون و سیستم عامل را ذکر کنید
3. لاگ‌های خطا را کپی کنید
4. در GitHub Issues بپرسید

### پیشنهادات

1. در GitHub Issues پیشنهاد دهید
2. در بخش Discussion صحبت کنید
3. Pull Request بفرستید

### پشتیبانی

- GitHub Issues
- GitHub Discussions
- Email

## لایسنس

این پروژه تحت لایسنس MIT منتشر شده است.

## نویسنده

ساخته شده با ❤️ برای ترجمه PDF با کیفیت
