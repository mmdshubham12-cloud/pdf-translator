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
        self.model_name = "gemini-3.5-flash"
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"

    def translate_chunk(self, chunk: TranslationChunk) -> Optional[str]:
        """Translate a single text chunk"""
        api_key = self.api_manager.get_default_api_key()

        if not api_key:
            print("❌ Hich kelid API tanzim nashode ast")
            return None

        # Check rate limit
        if not self.api_manager.check_rate_limit():
            print("⚠️  Mahdoodiate nerkhe darkhast raayat shod")
            return None

        # Check daily limit
        if not self.api_manager.check_daily_limit():
            print("⚠️  Mahdoodiate roozane raayat shod")
            return None

        # Prepare request
        prompt = (
            "You are a professional translator. Translate the following text to "
            "fluent, natural Persian (Farsi). Keep formatting, bold markers and "
            "meaning exactly. Only output the translation:\n\n"
            f"{chunk.text}"
        )

        try:
            # Record request
            tokens_used = len(chunk.text) // 4  # Approximate token count
            if not self.api_manager.record_request(api_key, tokens_used):
                return None

            # Make request to Gemini API
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
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
                print(f"❌ Khata dar tarjome: {response.status_code}")

                # Rotate API key on error
                self.api_manager.rotate_api_key()
                return None

        except requests.exceptions.Timeout:
            print("⏱️  timeout")
            return None
        except Exception as e:
            print(f"❌ Khataye tarjome: {e}")
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
                    progress_callback(i + 1, len(chunks), "Tekrari")
                continue

            # Translate chunk
            translated_text = self.translate_chunk(chunk)

            if translated_text:
                results["success"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "Movafagh")
            else:
                results["failed"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "Namovafagh")

        return results


class CloudflareWorkerTranslator:
    """Translation using Cloudflare Worker proxy"""

    def __init__(self, worker_url: str, api_manager: APIManager):
        self.worker_url = worker_url.rstrip('/')
        self.api_manager = api_manager

    def translate_chunk(self, chunk: TranslationChunk) -> Optional[str]:
        """Translate a single chunk through the Cloudflare Worker"""
        api_key = self.api_manager.get_default_api_key()

        if not api_key:
            print("❌ Hich kelid API tanzim nashode ast")
            return None

        if not self.api_manager.check_rate_limit():
            print("⚠️  Mahdoodiate nerkhe darkhast raayat shod")
            return None

        if not self.api_manager.check_daily_limit():
            print("⚠️  Mahdoodiate roozane raayat shod")
            return None

        prompt = (
            "You are a professional translator. Translate the following text to "
            "fluent, natural Persian (Farsi). Keep formatting, bold markers and "
            "meaning exactly. Only output the translation:\n\n"
            f"{chunk.text}"
        )

        try:
            tokens_used = len(prompt) // 4
            if not self.api_manager.record_request(api_key, tokens_used):
                return None

            response = requests.post(
                f"{self.worker_url}/translate",
                json={
                    "text": prompt,
                    "apiKey": api_key,
                    "model": "gemini-3.5-flash"
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                translated_text = (
                    result.get("translated_text")
                    or result.get("candidates", [{}])[0]
                    .get("content", {}).get("parts", [{}])[0].get("text", "")
                )

                if translated_text:
                    chunk.translated_text = translated_text
                    chunk.is_processed = True
                    chunk.translation_time = time.time()
                    return translated_text

            print(f"❌ Khata dar tarjome: {response.status_code}")
            return None

        except Exception as e:
            print(f"❌ Khataye tarjome: {e}")
            return None

    def translate_all(self, chunks: List[TranslationChunk], progress_callback=None) -> Dict[str, int]:
        """Translate all chunks"""
        results = {"success": 0, "failed": 0, "skipped": 0}

        for i, chunk in enumerate(chunks):
            if chunk.is_processed:
                results["skipped"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "Tekrari")
                continue

            translated = self.translate_chunk(chunk)
            if translated:
                results["success"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "Movafagh")
            else:
                results["failed"] += 1
                if progress_callback:
                    progress_callback(i + 1, len(chunks), "Namovafagh")

        return results
