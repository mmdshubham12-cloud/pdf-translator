#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Manager for managing multiple API keys and rate limiting
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import threading


class APIManager:
    """Manage multiple API keys and handle rate limiting"""

    def __init__(self, config_path: str = "config.yaml", stats_path: str = "api_stats.json"):
        self.config_path = Path(config_path)
        self.stats_path = Path(stats_path)
        self.config = self._load_config()
        self.stats = self._load_stats()
        self.lock = threading.Lock()
        self.last_request_time = 0
        self.request_queue = []

    def _load_config(self) -> Dict:
        """Load configuration file"""
        defaults = {
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
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            # Empty or invalid file -> fall back to defaults
            if not isinstance(data, dict):
                return defaults
            return data
        except FileNotFoundError:
            # First run: create config with defaults
            self.config = defaults
            self._save_config()
            return defaults
        except Exception as e:
            print(f"❌ Khata dar load config: {e}")
            return defaults

    def _load_stats(self) -> Dict:
        """Load API stats file"""
        try:
            with open(self.stats_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Khata dar load amar: {e}")
            return {
                "daily_requests": 0,
                "daily_limit": 500,
                "rate_limit": 10,
                "tokens_used": 0,
                "tokens_limit": 250000,
                "last_reset": None,
                "api_keys": {}
            }

    def _save_config(self):
        """Save configuration to file"""
        try:
            import yaml
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"❌ Khata dar zakhire config: {e}")

    def _save_stats(self):
        """Save API stats to file"""
        try:
            with open(self.stats_path, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Khata dar zakhire amar: {e}")

    def get_worker_url(self) -> Optional[str]:
        """Get saved Cloudflare Worker URL"""
        return self.config.get("worker_url")

    def save_worker_url(self, url: str):
        """Save Cloudflare Worker URL (empty string disables it)"""
        with self.lock:
            self.config["worker_url"] = url.strip()
            self._save_config()

    def get_api_keys(self) -> List[Dict]:
        """Get all API keys"""
        with self.lock:
            return self.config.get("api_keys", [])

    def add_api_key(self, name: str, api_key: str) -> bool:
        """Add a new API key"""
        with self.lock:
            if not self.config.get("api_keys"):
                self.config["api_keys"] = []

            # Check for duplicate
            for key in self.config["api_keys"]:
                if key.get("api_key") == api_key:
                    print(f"⚠️  Kelid ghablan ezafe shode ast")
                    return False

            new_key = {
                "name": name,
                "api_key": api_key,
                "usage": 0,
                "tokens_used": 0,
                "is_default": False
            }

            self.config["api_keys"].append(new_key)
            self._save_config()

            print(f"✅ Kelid ba movafaghiat ezafe shod: {name}")
            return True

    def set_default_api_key(self, api_key: str) -> bool:
        """Set default API key"""
        with self.lock:
            for key in self.config["api_keys"]:
                if key.get("api_key") == api_key:
                    # Unset all defaults
                    for k in self.config["api_keys"]:
                        k["is_default"] = False

                    key["is_default"] = True
                    self.config["default_api_key"] = api_key
                    self._save_config()
                    print(f"✅ Kelide pishfarz tanzim shod: {key.get('name')}")
                    return True

            print(f"❌ Kelid yaft nashod")
            return False

    def get_default_api_key(self) -> Optional[str]:
        """Get default API key"""
        with self.lock:
            if self.config.get("default_api_key"):
                return self.config["default_api_key"]

            # Find first available key
            for key in self.config.get("api_keys", []):
                if key.get("is_default", False):
                    return key.get("api_key")

            # Return None if no key available
            return None

    def rotate_api_key(self) -> Optional[str]:
        """Rotate to next API key for load balancing"""
        with self.lock:
            api_keys = self.config.get("api_keys", [])
            if not api_keys:
                return None

            # Find next key that's not the current one
            current_key = self.get_default_api_key()
            for key in api_keys:
                if key.get("api_key") != current_key:
                    self.set_default_api_key(key.get("api_key"))
                    return key.get("api_key")

            return current_key

    def record_request(self, api_key: str, tokens: int = 0):
        """Record an API request"""
        with self.lock:
            # Update daily stats
            self.stats["daily_requests"] += 1
            self.stats["tokens_used"] += tokens
            self.stats["total_requests"] += 1

            # Update key stats
            for key in self.config.get("api_keys", []):
                if key.get("api_key") == api_key:
                    key["usage"] += 1
                    key["tokens_used"] += tokens
                    break

            # Check daily limit
            if self.stats["daily_requests"] >= self.stats["daily_limit"]:
                print(f"⚠️  Mahdoodiate roozane raayat shod ({self.stats['daily_requests']}/{self.stats['daily_limit']})")
                return False

            # Check rate limit
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < (60 / self.stats["rate_limit"]):
                wait_time = (60 / self.stats["rate_limit"]) - time_since_last
                print(f"⏳ Dar hale entezar {wait_time:.2f} sanie...")
                time.sleep(wait_time)

            self.last_request_time = time.time()
            self._save_stats()
            return True

    def check_daily_limit(self) -> bool:
        """Check if daily limit is reached"""
        with self.lock:
            return self.stats["daily_requests"] < self.stats["daily_limit"]

    def check_rate_limit(self) -> bool:
        """Check if rate limit is reached"""
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < (60 / self.stats["rate_limit"]):
                return False

            return True

    def reset_daily_stats(self):
        """Reset daily stats"""
        with self.lock:
            today = time.strftime("%Y-%m-%d")
            if self.stats["last_reset"] != today:
                self.stats["daily_requests"] = 0
                self.stats["tokens_used"] = 0
                self.stats["last_reset"] = today
                self._save_stats()

    def get_stats(self) -> Dict:
        """Get current statistics"""
        with self.lock:
            return {
                "daily_requests": self.stats["daily_requests"],
                "daily_limit": self.stats["daily_limit"],
                "rate_limit": self.stats["rate_limit"],
                "tokens_used": self.stats["tokens_used"],
                "tokens_limit": self.stats["tokens_limit"],
                "usage_percent": (self.stats["daily_requests"] / self.stats["daily_limit"]) * 100 if self.stats["daily_limit"] > 0 else 0
            }

    def get_key_stats(self, api_key: str) -> Optional[Dict]:
        """Get stats for a specific API key"""
        with self.lock:
            for key in self.config.get("api_keys", []):
                if key.get("api_key") == api_key:
                    return {
                        "name": key.get("name"),
                        "usage": key.get("usage", 0),
                        "tokens_used": key.get("tokens_used", 0)
                    }
            return None

    def delete_api_key(self, api_key: str) -> bool:
        """Delete an API key"""
        with self.lock:
            api_keys = self.config.get("api_keys", [])
            for i, key in enumerate(api_keys):
                if key.get("api_key") == api_key:
                    deleted_key = api_keys.pop(i)
                    self._save_config()

                    if deleted_key.get("is_default"):
                        self.config["default_api_key"] = None

                    print(f"✅ Kelid hazf shod: {deleted_key.get('name')}")
                    return True

            print(f"❌ Kelid yaft nashod")
            return False
