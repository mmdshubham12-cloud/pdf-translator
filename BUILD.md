# راهنمای ساخت و کامپایل

## ساخت نسخه

### 1. پاکسازی

```bash
# پاک کردن فایل‌های قدیمی
rm -rf build/ dist/ *.egg-info
rm -rf cache/ temp/ outputs/
rm -f *.pyc __pycache__/
```

### 2. نصب وابستگی‌ها

```bash
python setup.py
```

### 3. اجرای تست‌ها

```bash
python test_translator.py
```

### 4. ساخت فایل اجرایی

#### روش 1: استفاده از PyInstaller

```bash
pip install pyinstaller

# ساخت فایل اجرایی
pyinstaller --onefile --name "PDFTranslator" --icon="assets/icon.png" app.py
```

#### روش 2: استفاده از setuptools

```bash
pip install setuptools wheel

# ساخت فایل اجرایی
python setup.py sdist bdist_wheel
```

## نصب در Pydroid 3

### 1. دانلود پروژه

```bash
git clone <repository-url>
cd my-app
```

### 2. نصب وابستگی‌ها

```bash
python setup.py
```

### 3. اجرای اپلیکیشن

```bash
python app.py
```

## ساخت APK (Android)

### 1. نصب ابزارها

```bash
pip install buildozer
```

### 2. تنظیم buildozer

```bash
buildozer init
```

ویرایش فایل `buildozer.spec`:

```
[app]

title = PDF Translator

source.dir = .

requirements = python3,kivy,kivymd,pymupdf,requests,pillow,pyyaml

android.api = 33
android.minapi = 21
android.ndk = 25b

orientation = portrait

fullscreen = 0
```

### 3. ساخت APK

```bash
buildozer android debug
```

### 4. نصب APK

```bash
buildozer android deploy run
```

## ساخت اپلیکیشن وب

### 1. ساخت فایل HTML

```bash
python -c "from output_generator import HTMLGenerator; gen = HTMLGenerator(); gen.save(gen.generate(data), 'index.html')"
```

### 2. استفاده از Weave

```bash
pip install weave
weave build
```

## ساخت Docker Image

### 1. ساخت Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### 2. ساخت Image

```bash
docker build -t pdf-translator .
```

### 3. اجرا

```bash
docker run -it pdf-translator
```

## ساخت NPM Package

### 1. ساخت package.json

```json
{
  "name": "pdf-translator",
  "version": "1.0.0",
  "main": "app.py",
  "dependencies": {
    "kivy": "^2.3.0",
    "kivymd": "^0.3.14"
  }
}
```

### 2. ساخت package

```bash
npm pack
```

## ساخت PIP Package

### 1. ساخت setup.py

```python
from setuptools import setup, find_packages

setup(
    name="pdf-translator",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "kivy==2.3.0",
        "kivymd==0.3.14",
        "PyMuPDF==1.23.8",
        "requests==2.31.0",
        "Pillow==10.1.0",
        "pyyaml==6.0.1"
    ],
    entry_points={
        "console_scripts": [
            "pdf-translator=app:main"
        ]
    }
)
```

### 2. ساخت package

```bash
python setup.py sdist bdist_wheel
```

### 3. انتشار

```bash
twine upload dist/*
```

## نکات مهم

### ساخت در Pydroid 3

1. از فایل `setup.py` استفاده کنید
2. اپلیکیشن را اجرا کنید
3. خروجی‌ها را در پوشه `outputs/` ذخیره کنید

### ساخت در Linux

1. از PyInstaller استفاده کنید
2. فایل اجرایی را بسازید
3. فایل را به اشتراک بگذارید

### ساخت در Windows

1. از PyInstaller استفاده کنید
2. فایل اجرایی را بسازید
3. فایل را به اشتراک بگذارید

### ساخت در Android

1. از buildozer استفاده کنید
2. APK را بسازید
3. APK را نصب کنید

## خطاهای رایج

### خطای "Module not found"

```bash
pip install -r requirements.txt
```

### خطای "Permission denied"

```bash
chmod +x setup.py
chmod +x app.py
```

### خطای "File not found"

```bash
ls -la
```

## بهینه‌سازی ساخت

### استفاده از کش

```bash
# استفاده از کش برای وابستگی‌ها
pip install --cache-dir=/tmp/pip-cache -r requirements.txt
```

### استفاده از multiprocessing

```bash
# ساخت چندین فایل اجرایی
python setup.py --single-package
```

### استفاده از threading

```bash
# ساخت فایل اجرایی سریع
pyinstaller --onefile --noconsole --name "PDFTranslator" app.py
```

## پشتیبانی

اگر مشکلی در ساخت داشتید:

1. README.md را بخوانید
2. TROUBLESHOOTING.md را بررسی کنید
3. GitHub Issues بپرسید
