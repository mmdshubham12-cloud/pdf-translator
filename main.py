#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator with Gemini 3.5 Flash
Main application entry point
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pdf_utils import PDFProcessor, TranslationManager
from api_manager import APIManager
from translator import TranslationEngine, CloudflareWorkerTranslator
from output_generator import OutputManager


class PDFTranslatorApp:
    """Main application class"""

    def __init__(self):
        self.api_manager = APIManager()
        self.translation_manager = TranslationManager()
        self.output_manager = OutputManager()
        self.current_pdf = None
        self.current_structured_data = None
        self.current_chunks = None
        self.translation_engine = None
        self.worker_translator = None
        self.worker_url = "http://127.0.0.1:8787"  # Cloudflare Worker URL

    def initialize(self):
        """Initialize application components"""
        print("🚀 شروع راه‌اندازی PDF Translator...")

        # Initialize translation engine
        self.translation_engine = TranslationEngine(
            self.api_manager,
            self.translation_manager
        )

        # Initialize worker translator
        self.worker_translator = CloudflareWorkerTranslator(
            self.worker_url,
            self.api_manager
        )

        print("✅ راه‌اندازی با موفقیت انجام شد")

    def load_pdf(self, pdf_path: str) -> bool:
        """Load PDF file"""
        print(f"\n📂 بارگذاری PDF: {pdf_path}")

        processor = PDFProcessor(pdf_path)
        if not processor.load_pdf():
            print("❌ بارگذاری PDF ناموفق بود")
            return False

        self.current_pdf = processor
        self.current_structured_data = processor.extract_text_with_structure()
        self.current_chunks = self.translation_manager.create_chunks(self.current_structured_data)

        print(f"✅ PDF بارگذاری شد. {len(self.current_structured_data)} صفحه یافت شد.")
        return True

    def _sync_translations_to_structure(self):
        """Write translated texts back into page structure for output generation"""
        if not self.current_structured_data or not self.current_chunks:
            return

        for chunk in self.current_chunks:
            if chunk.is_processed and chunk.translated_text:
                page_index = chunk.page_num - 1
                if 0 <= page_index < len(self.current_structured_data):
                    blocks = self.current_structured_data[page_index]['blocks']
                    if 0 <= chunk.block_index < len(blocks):
                        blocks[chunk.block_index]['translated'] = chunk.translated_text

    def translate_pdf(self, use_worker: bool = False):
        """Translate PDF content"""
        if not self.current_structured_data:
            print("❌ PDF بارگذاری نشده است")
            return

        print(f"\n🔄 شروع ترجمه ({len(self.current_chunks)} بخش)...")

        # Use appropriate translator
        translator = self.worker_translator if use_worker else self.translation_engine

        # Translate all chunks
        results = translator.translate_all(self.current_chunks, progress_callback=self._update_progress)

        print(f"\n📊 خلاصه ترجمه:")
        print(f"   ✅ موفق: {results['success']}")
        print(f"   ❌ ناموفق: {results['failed']}")
        print(f"   ⏭️  تکراری: {results['skipped']}")

        # Sync translations to page structure and save cache
        self._sync_translations_to_structure()
        self.translation_manager.save_cache()

    def generate_outputs(self, output_format: str = "pdf"):
        """Generate output files"""
        if not self.current_structured_data:
            print("❌ داده‌ای برای تولید وجود ندارد")
            return

        print(f"\n📄 تولید خروجی ({output_format})...")

        outputs = self.output_manager.generate_outputs(
            self.current_structured_data,
            self.current_pdf.pdf_path,
            output_format
        )

        print(f"✅ خروجی‌ها با موفقیت تولید شد:")
        for format_type, path in outputs.items():
            print(f"   {format_type.upper()}: {path}")

    def _update_progress(self, current: int, total: int, status: str):
        """Update progress callback"""
        percent = (current / total) * 100
        print(f"   [{current}/{total}] {percent:.1f}% - {status}")

    def get_stats(self) -> dict:
        """Get application statistics"""
        return {
            "api_stats": self.api_manager.get_stats(),
            "translation_stats": {
                "total_chunks": len(self.current_chunks) if self.current_chunks else 0,
                "processed_chunks": sum(1 for c in self.current_chunks if c.is_processed) if self.current_chunks else 0
            }
        }

    def add_api_key(self, name: str, api_key: str) -> bool:
        """Add API key"""
        return self.api_manager.add_api_key(name, api_key)

    def set_default_api_key(self, api_key: str) -> bool:
        """Set default API key"""
        return self.api_manager.set_default_api_key(api_key)

    def get_api_keys(self):
        """Get API keys"""
        return self.api_manager.get_api_keys()

    def rotate_api_key(self) -> str:
        """Rotate to next API key"""
        return self.api_manager.rotate_api_key()


def main():
    """Main entry point"""
    print("="*60)
    print("🚀 PDF Translator with Gemini 3.5 Flash")
    print("="*60)

    # Initialize app
    app = PDFTranslatorApp()
    app.initialize()

    # Check if API keys exist
    api_keys = app.get_api_keys()
    if not api_keys:
        print("\n⚠️  هیچ کلید API تنظیم نشده است!")
        print("لطفاً ابتدا یک کلید API اضافه کنید:")

        name = input("نام کلید: ")
        api_key = input("کلید API: ")

        if app.add_api_key(name, api_key):
            app.set_default_api_key(api_key)
            print("✅ کلید با موفقیت اضافه و تنظیم شد")

    # Main menu
    while True:
        print("\n" + "="*60)
        print("📋 منوی اصلی")
        print("="*60)
        print("1. بارگذاری PDF")
        print("2. ترجمه PDF")
        print("3. تولید خروجی")
        print("4. مشاهده آمار")
        print("5. افزودن کلید API")
        print("6. تنظیم کلید پیش‌فرض")
        print("7. تغییر کلید API")
        print("8. خروج")
        print("="*60)

        choice = input("انتخاب کنید (1-8): ").strip()

        if choice == "1":
            pdf_path = input("مسیر فایل PDF: ").strip()
            if app.load_pdf(pdf_path):
                print("✅ PDF بارگذاری شد")

        elif choice == "2":
            if not app.current_structured_data:
                print("❌ ابتدا PDF را بارگذاری کنید")
                continue

            use_worker = input("از Cloudflare Worker استفاده کنید؟ (y/n): ").strip().lower() == 'y'
            app.translate_pdf(use_worker=use_worker)

        elif choice == "3":
            if not app.current_structured_data:
                print("❌ ابتدا PDF را ترجمه کنید")
                continue

            output_format = input("فرمت خروجی (html/pdf): ").strip().lower()
            app.generate_outputs(output_format)

        elif choice == "4":
            stats = app.get_stats()
            print("\n📊 آمار:")
            print(f"   درخواست‌های امروز: {stats['api_stats']['daily_requests']}/{stats['api_stats']['daily_limit']}")
            print(f"   توکن استفاده شده: {stats['api_stats']['tokens_used']}/{stats['api_stats']['tokens_limit']}")
            print(f"   درصد استفاده: {stats['api_stats']['usage_percent']:.1f}%")
            print(f"   کل بخش‌های ترجمه شده: {stats['translation_stats']['processed_chunks']}/{stats['translation_stats']['total_chunks']}")

        elif choice == "5":
            name = input("نام کلید: ")
            api_key = input("کلید API: ")
            if app.add_api_key(name, api_key):
                print("✅ کلید اضافه شد")

        elif choice == "6":
            api_keys = app.get_api_keys()
            print("\nکلیدهای موجود:")
            for i, key in enumerate(api_keys, 1):
                default = " (پیش‌فرض)" if key.get('is_default') else ""
                print(f"{i}. {key.get('name')}{default}")

            key_num = input("شماره کلید برای تنظیم به عنوان پیش‌فرض: ")
            if key_num.isdigit() and 1 <= int(key_num) <= len(api_keys):
                selected_key = api_keys[int(key_num) - 1]['api_key']
                app.set_default_api_key(selected_key)
                print("✅ کلید پیش‌فرض تنظیم شد")

        elif choice == "7":
            api_keys = app.get_api_keys()
            if api_keys:
                print("\nکلیدهای موجود:")
                for i, key in enumerate(api_keys, 1):
                    default = " (پیش‌فرض)" if key.get('is_default') else ""
                    print(f"{i}. {key.get('name')}{default}")

                key_num = input("شماره کلید برای تغییر: ")
                if key_num.isdigit() and 1 <= int(key_num) <= len(api_keys):
                    selected_key = api_keys[int(key_num) - 1]['api_key']
                    app.set_default_api_key(selected_key)
                    print("✅ کلید پیش‌فرض تغییر کرد")
            else:
                print("❌ هیچ کلیدی وجود ندارد")

        elif choice == "8":
            print("\n👋 خداحافظ!")
            break

        else:
            print("❌ گزینه نامعتبر")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  برنامه متوقف شد")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ خطای ناگهانی: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
