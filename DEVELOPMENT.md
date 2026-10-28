# راهنمای توسعه

## ساختار پروژه

```
my-app/
├── setup.py              # نصب خودکار
├── app.py                # برنامه اصلی
├── main.py               # نسخه خط فرمان
├── pdf_utils.py          # ابزارهای PDF
├── api_manager.py        # مدیریت API
├── translator.py         # لاجیک ترجمه
├── output_generator.py   # تولید خروجی
├── ui/                   # رابط کاربری
│   ├── main_screen.kv
│   ├── settings_screen.kv
│   └── progress_screen.kv
├── cache/                # کش
├── temp/                 # فایل‌های موقت
├── outputs/              # خروجی‌ها
└── docs/                 # مستندات
```

## راه‌اندازی محیط توسعه

### 1. نصب وابستگی‌ها

```bash
python setup.py
```

### 2. نصب Kivy Garden

```bash
python -m kivy.garden install material
```

### 3. اجرای تست‌ها

```bash
python test_translator.py
```

## ساختار کد

### کلاس‌ها

#### PDFProcessor
```python
processor = PDFProcessor(pdf_path)
processor.load_pdf()
text = processor.extract_text_with_formatting()
structured_data = processor.extract_text_with_structure()
processor.save_page(page_num, text, output_path)
processor.close()
```

#### APIManager
```python
manager = APIManager()
manager.add_api_key(name, api_key)
manager.set_default_api_key(api_key)
stats = manager.get_stats()
manager.record_request(api_key, tokens)
```

#### TranslationEngine
```python
engine = TranslationEngine(api_manager, translation_manager)
chunk = TranslationChunk(text, page_num, block_index)
translated = engine.translate_chunk(chunk)
results = engine.translate_all(chunks, progress_callback)
```

#### OutputGenerator
```python
html_gen = HTMLGenerator()
html = html_gen.generate(structured_data)
html_gen.save(html, output_path)

pdf_gen = PDFGenerator()
pdf_gen.generate(structured_data, html_path, pdf_path)
```

## نوشتن کد جدید

### 1. اضافه کردن فایل جدید

1. فایل را در مسیر مناسب بسازید
2. کلاس‌ها را اضافه کنید
3. در main.py یا app.py فراخوانی کنید

### 2. اضافه کردن کلاس جدید

```python
class NewClass:
    """Description of class"""

    def __init__(self, **kwargs):
        """Initialize class"""
        pass

    def method(self, param):
        """Method description"""
        pass
```

### 3. اضافه کردن قابلیت جدید

1. در فایل مناسب متد جدید اضافه کنید
2. در main.py یا app.py فراخوانی کنید
3. تست کنید

## نوشتن تست

### تست واحد

```python
def test_function():
    """Test function"""
    result = function_to_test(param)
    assert result == expected_value
```

### تست PDF

```python
def test_pdf_processing():
    """Test PDF processing"""
    processor = PDFProcessor("test.pdf")
    assert processor.load_pdf()
    assert len(processor.pages) > 0
```

### تست API

```python
def test_api_manager():
    """Test API manager"""
    manager = APIManager()
    assert manager.add_api_key("test", "key")
    assert manager.set_default_api_key("key")
```

## کدنویسی با Kivy

### فایل KV

```yaml
#:kivy 1.11.1

<ScreenName>:
    orientation: 'vertical'

    MDTopAppBar:
        title: "Screen Title"

    MDScrollView:

        MDBoxLayout:
            orientation: 'vertical'
            padding: 'dp(20)'
            spacing: 'dp(20)'

            MDLabel:
                text: "Label Text"
                halign: 'center'
```

### کلاس Screen

```python
class ScreenName(Screen):
    """Screen description"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize screen

    def on_enter(self):
        """Called when screen is entered"""
        pass
```

### کلاس App

```python
class MyApp(App):
    """Main application"""

    def build(self):
        """Build UI"""
        return sm

    def method(self):
        """Method description"""
        pass
```

## استایل کد

### نام‌گذاری

- کلاس‌ها: PascalCase (`MyClass`)
- متغیرها: snake_case (`my_variable`)
- توابع: snake_case (`my_function`)
- ثابت‌ها: UPPER_CASE (`MY_CONSTANT`)

### کامنت‌ها

```python
def function():
    """Function description"""
    # Description of what this does
    pass
```

### نوع داده‌ها

```python
def function(param: str) -> bool:
    """Function with type hints"""
    pass
```

## دیباگ

### استفاده از print

```python
print(f"Debug: {variable}")
```

### استفاده از logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
logging.debug(f"Debug: {variable}")
```

### استفاده از pdb

```python
import pdb; pdb.set_trace()
```

## بهینه‌سازی

### مصرف حافظه

```python
# استفاده از context manager
with PDFProcessor(pdf_path) as processor:
    text = processor.extract_text()
```

### مصرف باتری

```python
# استفاده از threading
thread = threading.Thread(target=long_task)
thread.start()
```

### مصرف CPU

```python
# استفاده از multiprocessing
from multiprocessing import Pool
with Pool(processes=4) as pool:
    results = pool.map(process, items)
```

## مستندسازی

### Docstrings

```python
def function(param):
    """
    Function description.

    Args:
        param (str): Parameter description.

    Returns:
        bool: Return description.
    """
    pass
```

### README

- توضیح نحوه استفاده
- توضیح ویژگی‌ها
- توضیح ساختار
- توضیح مشکلات

## انتشار

### ساخت نسخه

1. تغییرات را در CHANGELOG.md اضافه کنید
2. تست‌ها را اجرا کنید
3. مستندات را به‌روز کنید
4. نسخه را بسازید

### انتشار در PyPI

1. فایل setup.py را تنظیم کنید
2. فایل setup.cfg را بسازید
3. فایل MANIFEST.in را بسازید
4. بیلد کنید: `python setup.py sdist bdist_wheel`
5. در PyPI منتشر کنید

## سوالات رایج

### چطور اضافه کردن قابلیت جدید؟
1. در فایل مناسب متد جدید اضافه کنید
2. در main.py یا app.py فراخوانی کنید
3. تست کنید

### چطور رابط کاربری تغییر کند؟
1. فایل KV مربوطه را ویرایش کنید
2. تغییرات را ذخیره کنید
3. اپلیکیشن را ریستارت کنید

### چطور خطا را پیدا کند؟
1. تست‌ها را اجرا کنید
2. لاگ‌ها را بررسی کنید
3. از debug استفاده کنید

### چطور بهینه‌سازی کند؟
1. مصرف حافظه را بررسی کنید
2. مصرف باتری را بررسی کنید
3. مصرف CPU را بررسی کنید
4. بهینه‌سازی کنید
