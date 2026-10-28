#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Engine using Google Gemini API
Handles translation with structure preservation and caching
"""

import requests
import time
from typing import List, Dict, Optional
from pdf_utils import TranslationChunk, TranslationManager
from api_manager import APIManager


class TranslationEngine:
    """Translation engine using Google Gemini API"""

    def __init__(self, api_manager: APIManager, translation_manager: TranslationManager):
        self.api_manager = api_manager
        self.translation_manager = translation_manager
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def translate_chunk(self, chunk: TranslationChunk) -> Optional[str]:
        """Translate a single text chunk"""
        api_key = self.api_manager.get_default_api_key()

        if not api_key:
            print("❌ هیچ کلید API تنظیم نشده است")
            return None

        # Check rate limit
        if not self.api_manager.check_rate_limit():
            print("⚠️  محدودیت نرخ درخواست رعایت شد")
            return None

        # Check daily limit
        if not self.api_manager.check_daily_limit():
            print("⚠️  محدودیت روزانه رعایت شد")
            return None

        # Prepare request
        prompt = f"Translate the following text to Persian:\n\n{chunk.text}"

        try:
            # Record request
            tokens_used = len(chunk.text) // 4  # Approximate token count
            if not self.api_manager.record_request(api_key, tokens_used):
                return None

            # Make request to Gemini API
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": 4096
                }
            }

            response = requests.post(
                self.gemini_url,
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

                # Update chunk
                chunk.translated_text = translated_text
                chunk.is_processed = True
                chunk.translation_time = time.time()

                return translated_text
            else:
                print(f"❌ خطا در ترجمه: {response.status_code}")
                print(f"Response: {response.text}")

                # Rotate API key on error
                self.api_manager.rotate_api_key()
                return None

        except requests.exceptions.Timeout:
            print("⏱️  timeout")
            return None
        except Exception as e:
            print(f"❌ خطای ترجمه: {e}")
            return None

    def translate_all(self, chunks: List[TranslationChunk], progress_callback=None) -> Dict[str, int]:
        """Translate all chunks with progress tracking"""
        results = {
            "success": 0,
            "failed": 0,
            "skipped": 0
        }

        for i, chunk in enumerate(chunks):
            # Skip already translated chunks
            if chunk.is_processed:
                results["skipped"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "تکراری")
                continue

            # Translate chunk
            translated_text = self.translate_chunk(chunk)

            if translated_text:
                results["success"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "موفق")
            else:
                results["failed"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "ناموفق")

        return results

    def translate_page(self, page_data: Dict) -> str:
        """Translate a page with all blocks"""
        page_num = page_data['page_num']
        blocks = page_data['blocks']

        translated_text = f"\n--- صفحه {page_num + 1} ---\n\n"

        for i, block in enumerate(blocks):
            chunk = TranslationChunk(
                text=block['text'],
                page_num=page_num,
                block_index=i
            )

            translated = self.translate_chunk(chunk)

            if translated:
                translated_text += translated + "\n\n"
            else:
                translated_text += block['text'] + "\n\n"

        return translated_text


class CloudflareWorkerTranslator:
    """Translation using Cloudflare Worker proxy"""

    def __init__(self, worker_url: str, api_manager: APIManager):
        self.worker_url = worker_url
        self.api_manager = api_manager
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    def translate_with_worker(self, text: str) -> Optional[str]:
        """Translate using Cloudflare Worker"""
        api_key = self.api_manager.get_default_api_key()

        if not api_key:
            print("❌ هیچ کلید API تنظیم نشده است")
            return None

        if not self.api_manager.check_rate_limit():
            print("⚠️  محدودیت نرخ درخواست رعایت شد")
            return None

        if not self.api_manager.check_daily_limit():
            print("⚠️  محدودیت روزانه رعایت شد")
            return None

        try:
            # Prepare request
            tokens_used = len(text) // 4
            if not self.api_manager.record_request(api_key, tokens_used):
                return None

            # Make request via worker
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            data = {
                "text": text,
                "apiKey": api_key
            }

            response = requests.post(
                f"{self.worker_url}/translate",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("translated_text", "")
            else:
                print(f"❌ خطا در ترجمه: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ خطای ترجمه: {e}")
            return None
