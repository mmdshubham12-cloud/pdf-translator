#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for PDF Translator App
Installs all dependencies and configures the app for Pydroid 3
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def print_step(step, message):
    """Print a formatted step message"""
    print(f"\n{'='*60}")
    print(f"📌 {step}: {message}")
    print('='*60)


def check_python_version():
    """Check Python version"""
    print_step("1", "بررسی نسخه پایتون")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ نسخه پایتون: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ نسخه پایتون: {version.major}.{version.minor}.{version.micro}")
        print("⚠️  نیاز به پایتون 3.8 یا بالاتر")
        return False


def create_directories():
    """Create necessary directories"""
    print_step("2", "ایجاد پوشه‌ها")

    directories = [
        "cache/translations",
        "cache/profiles",
        "temp",
        "outputs",
        "ui",
        "assets/icons"
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ ساخته شد: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    print_step("3", "نصب وابستگی‌ها")

    requirements = [
        "kivy==2.3.0",
        "kivy-garden==0.1.4",
        "kivymd==0.3.14",
        "PyMuPDF==1.23.8",
        "requests==2.31.0",
        "Pillow==10.1.0",
        "pyyaml==6.0.1"
    ]

    for req in requirements:
        print(f"📦 نصب: {req}")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--quiet", req],
                check=True
            )
            print(f"✅ نصب موفق: {req}")
        except subprocess.CalledProcessError as e:
            print(f"❌ خطا در نصب {req}: {e}")
            print("⚠️  تلاش مجدد...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", req],
                    check=True
                )
                print(f"✅ نصب موفق: {req}")
            except subprocess.CalledProcessError as e2:
                print(f"❌ نصب ناموفق: {req}")
                return False

    return True


def setup_kivy_garden():
    """Setup Kivy Garden"""
    print_step("4", "تنظیم Kivy Garden")

    try:
        from kivy.garden import garden
        garden.install_garden("material")
        print("✅ Kivy Garden نصب شد")
        return True
    except Exception as e:
        print(f"❌ خطا در Kivy Garden: {e}")
        return False


def create_default_config():
    """Create default configuration file"""
    print_step("5", "ایجاد فایل تنظیمات")

    default_config = {
        "api_keys": [],
        "current_profile": None,
        "default_api_key": None,
        "settings": {
            "output_format": "pdf",
            "html_output": True,
            "pdf_output": True,
            "auto_save": True,
            "theme": "dark"
        },
        "stats": {
            "total_requests": 0,
            "today_requests": 0,
            "last_reset": None
        }
    }

    config_path = "config.yaml"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            import yaml
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        print(f"✅ فایل تنظیمات ساخته شد: {config_path}")
        return True
    except Exception as e:
        print(f"❌ خطا در ایجاد فایل تنظیمات: {e}")
        return False


def create_default_api_stats():
    """Create default API stats file"""
    print_step("6", "ایجاد فایل آمار API")

    default_stats = {
        "daily_requests": 0,
        "daily_limit": 500,
        "rate_limit": 10,
        "tokens_used": 0,
        "tokens_limit": 250000,
        "last_reset": None,
        "api_keys": {}
    }

    stats_path = "api_stats.json"
    try:
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(default_stats, f, indent=2, ensure_ascii=False)
        print(f"✅ فایل آمار ساخته شد: {stats_path}")
        return True
    except Exception as e:
        print(f"❌ خطا در ایجاد فایل آمار: {e}")
        return False


def create_cloudflare_worker():
    """Create Cloudflare Worker setup"""
    print_step("7", "ایجاد ورکر کلادفلر")

    try:
        with open("cloudflare-worker.js", "w", encoding="utf-8") as f:
            f.write('''/**
 * Cloudflare Worker for PDF Translation
 * Auto-generated setup
 */

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url)

    // Proxy requests to Google Gemini
    if (url.pathname === '/translate') {
        return handleTranslation(request)
    }

    return new Response('PDF Translator Worker', { status: 200 })
}

async function handleTranslation(request) {
    const body = await request.json()
    const { text, apiKey } = body

    // Make request to Google Gemini
    const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            contents: [{
                parts: [{ text }]
            }]
        })
    })

    const data = await response.json()
    return new Response(JSON.stringify(data), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' }
    })
}
''')
        print("✅ ورکر کلادفلر ساخته شد: cloudflare-worker.js")
        return True
    except Exception as e:
        print(f"❌ خطا در ایجاد ورکر: {e}")
        return False


def create_readme():
    """Create README file"""
    print_step("8", "ایجاد فایل راهنما")

    readme_content = """# PDF Translator with Gemini 3.5 Flash

## نصب و راه‌اندازی

### 1. نصب وابستگی‌ها
این اسکریپت به صورت خودکار همه چیز را نصب می‌کند:
```bash
python setup.py
```

### 2. راه‌اندازی اپلیکیشن
```bash
python main.py
```

### 3. تنظیمات اولیه
- در صفحه تنظیمات، کلید API خود را اضافه کنید
- کلید پیش‌فرض را انتخاب کنید

## ویژگی‌ها

✅ ترجمه PDF با حفظ ساختار
✅ خروجی HTML و PDF
✅ مدیریت چند کلید API
✅ محدودیت‌های API
✅ کار با Cloudflare Worker
✅ رابط کاربری زیبا (Kivy/KivyMD)

## محدودیت‌ها

- 500 درخواست در روز
- 250,000 توکن ورودی در دقیقه
- 10 درخواست در دقیقه

## فایل‌های مهم

- `main.py` - برنامه اصلی
- `config.yaml` - تنظیمات
- `api_stats.json` - آمار API
- `cloudflare-worker.js` - ورکر کلادفلر
"""

    try:
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ فایل راهنما ساخته شد: README.md")
        return True
    except Exception as e:
        print(f"❌ خطا در ایجاد README: {e}")
        return False


def run_checks():
    """Run all setup checks"""
    print("\n" + "="*60)
    print("🚀 شروع نصب PDF Translator")
    print("="*60)

    # Run all steps
    steps = [
        ("نسخه پایتون", check_python_version),
        ("ایجاد پوشه‌ها", create_directories),
        ("نصب وابستگی‌ها", install_dependencies),
        ("تنظیم Kivy Garden", setup_kivy_garden),
        ("ایجاد فایل تنظیمات", create_default_config),
        ("ایجاد فایل آمار", create_default_api_stats),
        ("ایجاد ورکر کلادفلر", create_cloudflare_worker),
        ("ایجاد فایل راهنما", create_readme)
    ]

    results = []
    for name, func in steps:
        try:
            result = func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ خطای ناگهانی در {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "="*60)
    print("📊 خلاصه نصب")
    print("="*60)

    for name, result in results:
        status = "✅ موفق" if result else "❌ ناموفق"
        print(f"{status} - {name}")

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    print(f"\nنتیجه: {success_count}/{total_count} موفق")

    if success_count == total_count:
        print("\n🎉 نصب با موفقیت انجام شد!")
        print("برای راه‌اندازی اپلیکیشن:")
        print("   python main.py")
    else:
        print("\n⚠️  برخی موارد نصب نشدند")
        print("لطفاً خطاها را بررسی کنید")

    print("\n" + "="*60 + "\n")

    return success_count == total_count


if __name__ == "__main__":
    try:
        success = run_checks()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  نصب متوقف شد توسط کاربر")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطای ناگهانی: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
