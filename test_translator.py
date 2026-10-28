#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for translator
Tests the translation engine without GUI
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pdf_utils import PDFProcessor
from api_manager import APIManager
from translator import TranslationEngine


def test_translation():
    """Test translation with sample text"""
    print("="*60)
    print("🧪 تست ترجمه")
    print("="*60)

    # Initialize components
    api_manager = APIManager()
    translation_engine = TranslationEngine(api_manager, None)

    # Get API key
    api_key = api_manager.get_default_api_key()

    if not api_key:
        print("\n❌ هیچ کلید API تنظیم نشده است")
        print("لطفاً ابتدا یک کلید API اضافه کنید:")
        name = input("نام کلید: ")
        api_key = input("کلید API: ")

        if api_manager.add_api_key(name, api_key):
            api_manager.set_default_api_key(api_key)
        else:
            print("❌ اضافه کردن کلید ناموفق بود")
            return False

    # Test text
    test_text = """
    سلام، این یک متن تستی برای ترجمه است.
    این متن شامل چند جمله ساده است.
    همچنین می‌تواند حاوی اطلاعات مفید باشد.
    """

    print("\n📝 متن تستی:")
    print(test_text)

    # Translate
    print("\n🔄 شروع ترجمه...")
    translated = translation_engine.translate_chunk(
        TranslationChunk(text=test_text.strip(), page_num=0, block_index=0)
    )

    if translated:
        print("\n✅ ترجمه موفق!")
        print("\n📝 متن ترجمه شده:")
        print(translated)
        return True
    else:
        print("\n❌ ترجمه ناموفق")
        return False


def test_pdf_processing():
    """Test PDF processing"""
    print("\n" + "="*60)
    print("🧪 تست پردازش PDF")
    print("="*60)

    pdf_path = input("\nمسیر فایل PDF را وارد کنید (برای رد کردن، Enter بزنید): ").strip()

    if not pdf_path:
        print("❌ مسیر PDF وارد نشد")
        return False

    if not Path(pdf_path).exists():
        print(f"❌ فایل {pdf_path} یافت نشد")
        return False

    print(f"\n📂 بارگذاری PDF: {pdf_path}")

    processor = PDFProcessor(pdf_path)
    if not processor.load_pdf():
        print("❌ بارگذاری PDF ناموفق بود")
        return False

    print(f"✅ PDF بارگذاری شد. {len(processor.pages)} صفحه یافت شد.")

    # Extract text
    text = processor.extract_text_with_formatting()
    print(f"✅ {len(text)} کاراکتر استخراج شد")

    # Extract structured data
    structured_data = processor.extract_text_with_structure()
    print(f"✅ {len(structured_data)} صفحه و {len(structured_data[0]['blocks'])} بلوک استخراج شد")

    return True


def test_api_manager():
    """Test API manager"""
    print("\n" + "="*60)
    print("🧪 تست API Manager")
    print("="*60)

    api_manager = APIManager()

    # Test add key
    print("\n1. اضافه کردن کلید جدید...")
    if api_manager.add_api_key("Test Key", "test-api-key-123"):
        print("✅ کلید اضافه شد")
    else:
        print("❌ اضافه کردن کلید ناموفق بود")

    # Test set default
    print("\n2. تنظیم کلید پیش‌فرض...")
    api_key = api_manager.get_api_keys()[0]['api_key']
    if api_manager.set_default_api_key(api_key):
        print("✅ کلید پیش‌فرض تنظیم شد")
    else:
        print("❌ تنظیم کلید پیش‌فرض ناموفق بود")

    # Test stats
    print("\n3. نمایش آمار...")
    stats = api_manager.get_stats()
    print(f"   درخواست‌های امروز: {stats['daily_requests']}/{stats['daily_limit']}")
    print(f"   توکن استفاده شده: {stats['tokens_used']}/{stats['tokens_limit']}")
    print(f"   درصد استفاده: {stats['usage_percent']:.1f}%")

    return True


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🧪 آزمایش‌های PDF Translator")
    print("="*60)

    while True:
        print("\n" + "="*60)
        print("📋 منوی آزمایش")
        print("="*60)
        print("1. تست API Manager")
        print("2. تست ترجمه")
        print("3. تست پردازش PDF")
        print("4. همه آزمایش‌ها")
        print("5. خروج")
        print("="*60)

        choice = input("\nانتخاب کنید (1-5): ").strip()

        if choice == "1":
            test_api_manager()
        elif choice == "2":
            test_translation()
        elif choice == "3":
            test_pdf_processing()
        elif choice == "4":
            test_api_manager()
            test_translation()
            test_pdf_processing()
        elif choice == "5":
            print("\n👋 خداحافظ!")
            break
        else:
            print("❌ گزینه نامعتبر")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  آزمایش متوقف شد")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطای ناگهانی: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
