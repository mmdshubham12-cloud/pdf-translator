#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Utility Functions for PDF Translator
Handles PDF processing, structure preservation, and text extraction
"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple
import re


class PDFProcessor:
    """Process PDF files while preserving structure"""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = None
        self.pages = []

    def load_pdf(self) -> bool:
        """Load PDF file"""
        try:
            self.doc = fitz.open(self.pdf_path)
            self.pages = []
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                self.pages.append({
                    'page_num': page_num,
                    'text': page.get_text(),
                    'blocks': self._extract_blocks(page)
                })
            return True
        except Exception as e:
            print(f"❌ خطا در لود PDF: {e}")
            return False

    def _extract_blocks(self, page) -> List[Dict]:
        """Extract text blocks with formatting"""
        blocks = []
        blocks_text = page.get_text("blocks")

        for block in blocks_text:
            if block[4] == 0:  # text block
                block_data = {
                    'x0': block[0],
                    'y0': block[1],
                    'x1': block[2],
                    'y1': block[3],
                    'text': block[4].strip(),
                    'font': block[5],
                    'size': block[6],
                    'flags': block[7]
                }
                blocks.append(block_data)

        return blocks

    def extract_text_with_formatting(self) -> str:
        """Extract text while preserving formatting"""
        full_text = ""

        for page in self.pages:
            # Add page number
            full_text += f"\n--- صفحه {page['page_num'] + 1} ---\n\n"

            # Extract blocks
            for block in page['blocks']:
                if block['text']:
                    full_text += block['text'] + "\n"

        return full_text

    def extract_text_with_structure(self) -> List[Dict]:
        """Extract text with page and block structure"""
        structured_data = []

        for page in self.pages:
            page_data = {
                'page_num': page['page_num'] + 1,
                'blocks': []
            }

            for block in page['blocks']:
                if block['text']:
                    block_data = {
                        'x0': block['x0'],
                        'y0': block['y0'],
                        'x1': block['x1'],
                        'y1': block['y1'],
                        'text': block['text'],
                        'is_bold': bool(block['flags'] & 0x02)  # Bold flag
                    }
                    page_data['blocks'].append(block_data)

            structured_data.append(page_data)

        return structured_data

    def split_text_by_blocks(self, text: str) -> List[str]:
        """Split text into blocks for translation"""
        # Split by page markers
        page_markers = re.split(r'--- صفحه \d+ ---', text)
        blocks = []

        for marker in page_markers:
            if marker.strip():
                blocks.append(marker.strip())

        return blocks

    def process_images(self, page) -> List[Dict]:
        """Extract images from page"""
        images = []
        image_list = page.get_images(full=True)

        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = self.doc.extract_image(xref)
            image_data = {
                'xref': xref,
                'image': base_image,
                'ext': base_image['ext']
            }
            images.append(image_data)

        return images

    def save_page(self, page_num: int, text: str, output_path: str):
        """Save processed text to output file"""
        try:
            with open(output_path, 'a', encoding='utf-8') as f:
                f.write(f"\n--- صفحه {page_num + 1} ---\n\n")
                f.write(text)
                f.write("\n")
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره صفحه: {e}")
            return False

    def close(self):
        """Close PDF document"""
        if self.doc:
            self.doc.close()


class PDFStructureParser:
    """Parse and preserve PDF structure"""

    @staticmethod
    def identify_structure(text: str) -> List[Dict]:
        """Identify different sections in text"""
        sections = []

        # Check for headings (lines with less characters and uppercase)
        lines = text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if it's a heading
            if len(line) < 100 and line.isupper():
                sections.append({
                    'type': 'heading',
                    'text': line
                })
            # Check if it's a bullet point
            elif line.startswith(('-', '*', '•', '✓')):
                sections.append({
                    'type': 'bullet',
                    'text': line
                })
            # Regular text
            else:
                if not current_section:
                    current_section = {
                        'type': 'paragraph',
                        'text': line
                    }
                    sections.append(current_section)
                else:
                    current_section['text'] += ' ' + line

        return sections

    @staticmethod
    def format_for_translation(text: str) -> List[str]:
        """Format text into translation-ready chunks"""
        # Split into sentences
        chunks = re.split(r'(?<=[.!?])\s+', text)
        return [chunk.strip() for chunk in chunks if chunk.strip()]

    @staticmethod
    def restore_formatting(text: str, original_format: Dict) -> str:
        """Restore formatting to translated text"""
        # Simple implementation - could be enhanced
        return text


class TranslationChunk:
    """Manage translation chunks with metadata"""

    def __init__(self, text: str, page_num: int = 0, block_index: int = 0):
        self.text = text
        self.page_num = page_num
        self.block_index = block_index
        self.translated_text = None
        self.is_processed = False
        self.translation_time = None


class TranslationManager:
    """Manage translation chunks and caching"""

    def __init__(self, cache_dir: str = "cache/translations"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.chunks = []

    def create_chunks(self, structured_data: List[Dict]) -> List[TranslationChunk]:
        """Create translation chunks from structured data"""
        self.chunks = []

        for page_data in structured_data:
            for i, block in enumerate(page_data['blocks']):
                chunk = TranslationChunk(
                    text=block['text'],
                    page_num=page_data['page_num'],
                    block_index=i
                )
                self.chunks.append(chunk)

        return self.chunks

    def save_cache(self):
        """Save translation cache to disk"""
        cache_data = []
        for chunk in self.chunks:
            cache_data.append({
                'text': chunk.text,
                'translated_text': chunk.translated_text,
                'page_num': chunk.page_num,
                'block_index': chunk.block_index,
                'is_processed': chunk.is_processed,
                'translation_time': chunk.translation_time
            })

        cache_file = self.cache_dir / f"cache_{len(self.chunks)}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            import json
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def load_cache(self, cache_file: str):
        """Load translation cache from disk"""
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            self.chunks = []
            for data in cache_data:
                chunk = TranslationChunk(
                    text=data['text'],
                    page_num=data['page_num'],
                    block_index=data['block_index']
                )
                chunk.translated_text = data.get('translated_text')
                chunk.is_processed = data.get('is_processed', False)
                chunk.translation_time = data.get('translation_time')

            return True
        except Exception as e:
            print(f"❌ خطا در لود کش: {e}")
            return False
