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
    print("🧪 Test tarjome")
    print("="*60)

    # Initialize components
    api_manager = APIManager()
    translation_engine = TranslationEngine(api_manager, None)

    # Get API key
    api_key = api_manager.get_default_api_key()

    if not api_key:
        print("\n❌ Hich kelid API tanzim nashode ast")
        print("Lotfan aval yek kelid API ezafe konid:")
        name = input("Nam kelid: ")
        api_key = input("Kelid API: ")

        if api_manager.add_api_key(name, api_key):
            api_manager.set_default_api_key(api_key)
        else:
            print("❌ Ezafe kardan kelid namovafagh bood")
            return False

    # Test text
    test_text = """
    Salam, in yek matne testi baraye tarjome ast.
    In matn shamel chand jomele sade ast.
    Hamchenin mitavanad havi-e etelaat mofid bashad.
    """

    print("\n📝 Matne testi:")
    print(test_text)

    # Translate
    print("\n🔄 Shoro tarjome...")
    translated = translation_engine.translate_chunk(
        TranslationChunk(text=test_text.strip(), page_num=0, block_index=0)
    )

    if translated:
        print("\n✅ Tarjome movafagh!")
        print("\n📝 Matne tarjome shode:")
        print(translated)
        return True
    else:
        print("\n❌ Tarjome namovafagh")
        return False


def test_pdf_processing():
    """Test PDF processing"""
    print("\n" + "="*60)
    print("🧪 Test pardazesh PDF")
    print("="*60)

    pdf_path = input("\nMasire file PDF ra vared konid (baraye rad kardan, Enter bezanid): ").strip()

    if not pdf_path:
        print("❌ Masire PDF vared nashod")
        return False

    if not Path(pdf_path).exists():
        print(f"❌ File {pdf_path} yaft nashod")
        return False

    print(f"\n📂 Bargozari PDF: {pdf_path}")

    processor = PDFProcessor(pdf_path)
    if not processor.load_pdf():
        print("❌ Bargozari PDF namovafagh bood")
        return False

    print(f"✅ PDF bargozari shod. {len(processor.pages)} safhe yaft shod.")

    # Extract text
    text = processor.extract_text_with_formatting()
    print(f"✅ {len(text)} karakter estekhraj shod")

    # Extract structured data
    structured_data = processor.extract_text_with_structure()
    print(f"✅ {len(structured_data)} safhe va {len(structured_data[0]['blocks'])} blok estekhraj shod")

    return True


def test_api_manager():
    """Test API manager"""
    print("\n" + "="*60)
    print("🧪 Test API Manager")
    print("="*60)

    api_manager = APIManager()

    # Test add key
    print("\n1. Ezafe kardan kelide jadid...")
    if api_manager.add_api_key("Test Key", "test-api-key-123"):
        print("✅ Kelid ezafe shod")
    else:
        print("❌ Ezafe kardan kelid namovafagh bood")

    # Test set default
    print("\n2. Tanzim kelide pishfarz...")
    api_key = api_manager.get_api_keys()[0]['api_key']
    if api_manager.set_default_api_key(api_key):
        print("✅ Kelide pishfarz tanzim shod")
    else:
        print("❌ Tanzim kelide pishfarz namovafagh bood")

    # Test stats
    print("\n3. Namayesh amar...")
    stats = api_manager.get_stats()
    print(f"   Darkhasthaye emrooz: {stats['daily_requests']}/{stats['daily_limit']}")
    print(f"   Token estefade shode: {stats['tokens_used']}/{stats['tokens_limit']}")
    print(f"   Darsade estefade: {stats['usage_percent']:.1f}%")

    return True


def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🧪 Azmayeshhaye PDF Translator")
    print("="*60)

    while True:
        print("\n" + "="*60)
        print("📋 Menu azmayesh")
        print("="*60)
        print("1. Test API Manager")
        print("2. Test tarjome")
        print("3. Test pardazesh PDF")
        print("4. Hame azmayeshha")
        print("5. Khorooj")
        print("="*60)

        choice = input("\nEntekhab konid (1-5): ").strip()

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
            print("\n👋 Khodahafez!")
            break
        else:
            print("❌ Gozine namotabar")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Azmayesh motavaghef shod")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Khataye nagahani: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
