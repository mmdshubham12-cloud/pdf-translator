#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator with Gemini - Android GUI (KivyMD)
"""

import os
import sys
import threading
from pathlib import Path

BASE_DIR = str(Path(__file__).parent)
sys.path.insert(0, BASE_DIR)

import platform
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.filemanager import MDFileManager

from api_manager import APIManager
from pdf_utils import PDFProcessor, TranslationManager
from translator import TranslationEngine, CloudflareWorkerTranslator
from output_generator import OutputManager

# Persian font for proper Arabic-script rendering
FONT_REG = os.path.join(BASE_DIR, "assets", "Vazirmatn-Regular.ttf")
FONT_BOLD = os.path.join(BASE_DIR, "assets", "Vazirmatn-Bold.ttf")

try:
    import arabic_reshaper
    from bidi.algorithm import get_display

    def fa(text):
        """Reshape + bidi Persian text so it renders correctly in Kivy."""
        return get_display(arabic_reshaper.reshape(str(text)))
    HAS_FA = True
except ImportError:
    def fa(text):
        return str(text)
    HAS_FA = False


KV = """
MDScreenManager:
    MainScreen:
        id: main_screen
    KeysScreen:
        id: keys_screen
    ProgressScreen:
        id: progress_screen

<MainScreen>:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "مترجم PDF"
            right_action_items: [["cog", lambda x: app.go_keys()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)

            MDCard:
                orientation: "vertical"
                padding: dp(20)
                spacing: dp(12)
                radius: [dp(16)]
                md_bg_color: app.theme_cls.primaryContainerColor

                MDLabel:
                    id: file_label
                    text: "فایلی انتخاب نشده است"
                    halign: "center"
                    font_name: app.fa_font
                    font_style: "H6"
                    adaptive_height: True

                MDRaisedButton:
                    text: "انتخاب فایل PDF"
                    font_name: app.fa_font
                    pos_hint: {"center_x": .5}
                    on_release: app.open_file_picker()

            MDCard:
                orientation: "vertical"
                padding: dp(20)
                spacing: dp(12)
                radius: [dp(16)]

                MDLabel:
                    text: "درخواست‌های امروز"
                    halign: "center"
                    font_name: app.fa_font
                    font_style: "Body2"

                MDProgressBar:
                    id: quota_bar
                    value: 0
                    max: 500

                MDLabel:
                    id: quota_label
                    text: "0 / 500"
                    halign: "center"
                    font_name: app.fa_font
                    font_style: "Caption"

            MDBoxLayout:
                adaptive_height: True
                spacing: dp(12)

                MDRaisedButton:
                    id: start_btn
                    text: "شروع ترجمه"
                    font_name: app.fa_font
                    size_hint_x: .6
                    on_release: app.start_translation()

                MDRaisedButton:
                    text: "خروجی‌ها"
                    font_name: app.fa_font
                    size_hint_x: .4
                    on_release: app.show_outputs_dialog()

<KeysScreen>:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "کلیدهای API"
            left_action_items: [["arrow-right", lambda x: app.go_main()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(20)
            spacing: dp(16)

            MDTextField:
                id: key_name
                hint_text: "نام کلید"
                mode: "rectangle"
                font_name: app.fa_font

            MDTextField:
                id: key_value
                hint_text: "کلید Gemini API"
                mode: "rectangle"

            MDRaisedButton:
                text: "افزودن کلید"
                font_name: app.fa_font
                pos_hint: {"center_x": .5}
                on_release: app.add_key()

            MDLabel:
                text: "کلیدهای ذخیره‌شده:"
                font_name: app.fa_font
                font_style: "Body2"
                adaptive_height: True

            ScrollView:
                MDList:
                    id: keys_list

            MDTextField:
                id: worker_url
                hint_text: "آدرس Cloudflare Worker (اختیاری)"
                mode: "rectangle"
                on_text_validate: app.save_worker_url()

<ProgressScreen>:
    md_bg_color: app.theme_cls.backgroundColor

    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "در حال ترجمه"

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(24)
            spacing: dp(20)
            pos_hint: {"center_y": .5}

            MDLabel:
                id: prog_title
                text: "در حال آماده‌سازی..."
                halign: "center"
                font_name: app.fa_font
                font_style: "H6"

            MDProgressBar:
                id: prog_bar
                value: 0

            MDLabel:
                id: prog_detail
                text: ""
                halign: "center"
                font_name: app.fa_font
                font_style: "Body2"

            MDLabel:
                id: prog_stats
                text: ""
                halign: "center"
                font_name: app.fa_font
                font_style: "Caption"
"""


class MainScreen(MDScreen):
    pass


class KeysScreen(MDScreen):
    pass


class ProgressScreen(MDScreen):
    pass


class PDFTranslatorApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.api_manager = APIManager()
        self.translation_manager = TranslationManager()
        self.output_manager = OutputManager()

        self.pdf_processor = None
        self.structured = None
        self.chunks = None

        self.is_translating = False
        self.stop_flag = False
        self.progress_dialog = None

        self.worker_url = self.api_manager.get_worker_url()

    def build(self):
        self.title = "PDF Translator"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        # Register Persian fonts
        if os.path.exists(FONT_REG):
            LabelBase.register(name="Vazirmatn", fn_regular=FONT_REG, fn_bold=FONT_BOLD)
            self.fa_font = "Vazirmatn"
        else:
            self.fa_font = "Roboto"

        return Builder.load_string(KV)

    def on_start(self):
        self.refresh_quota()
        self.refresh_keys()
        wu = self.root.ids.keys_screen.ids.worker_url
        if self.worker_url:
            wu.text = self.worker_url

        # Android runtime storage permissions (for reading/saving files)
        if platform == "android":
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE,
                ])
            except Exception:
                pass

    # ---------- Persian text helper ----------
    def P(self, text):
        return fa(text)

    # ---------- Navigation ----------
    def go_main(self):
        self.root.current = "main"

    def go_keys(self):
        self.refresh_keys()
        self.root.current = "keys"

    def go_progress(self):
        self.root.current = "progress"

    # ---------- Quota display ----------
    def refresh_quota(self, *args):
        stats = self.api_manager.get_stats()
        scr = self.root.ids.main_screen
        scr.ids.quota_bar.max = stats["daily_limit"]
        scr.ids.quota_bar.value = stats["daily_requests"]
        scr.ids.quota_label.text = self.P(
            f"{stats['daily_requests']} / {stats['daily_limit']} درخواست"
        )

    # ---------- File picker ----------
    def open_file_picker(self):
        if not hasattr(self, "file_manager"):
            start_dir = "/sdcard" if platform == "android" else BASE_DIR
            self.file_manager = MDFileManager(
                exit_manager=self.close_file_picker,
                select_path=self.pick_file,
                ext=[".pdf", ".PDF"],
                preview=False,
            )
            self.file_manager.show(start_dir)
        else:
            self.file_manager.show("/sdcard" if platform == "android" else BASE_DIR)
        self.file_manager_open = True

    def pick_file(self, path):
        self.close_file_picker(path)
        self.load_pdf(path)

    def close_file_picker(self, *args):
        self.file_manager_open = False
        self.file_manager.close()

    def load_pdf(self, path):
        proc = PDFProcessor(path)
        if not proc.load_pdf():
            self.snack("بارگذاری PDF ناموفق بود")
            return
        self.pdf_processor = proc
        self.structured = proc.extract_text_with_structure()
        self.chunks = self.translation_manager.create_chunks(self.structured)
        self.root.ids.main_screen.ids.file_label.text = self.P(
            f"{Path(path).name}  •  {len(self.structured)} صفحه  •  {len(self.chunks)} بخش"
        )
        self.snack(f"بارگذاری شد: {len(self.structured)} صفحه")

    # ---------- Translation ----------
    def start_translation(self):
        if self.is_translating:
            return
        if not self.structured:
            self.snack("اول یک PDF انتخاب کنید")
            return
        if not self.api_manager.get_default_api_key():
            self.snack("اول یک کلید API اضافه کنید")
            return
        if not self.api_manager.check_daily_limit():
            self.snack("محدودیت روزانه رعایت شد؛ فردا دوباره امتحان کنید")
            return

        self.is_translating = True
        self.stop_flag = False
        self.go_progress()

        worker_url = self.root.ids.keys_screen.ids.worker_url.text.strip()
        use_worker = bool(worker_url)
        threading.Thread(
            target=self._translation_worker,
            args=(use_worker,),
            daemon=True
        ).start()

    def _translation_worker(self, use_worker):
        engine = (
            CloudflareWorkerTranslator(worker_url, self.api_manager)
            if use_worker
            else TranslationEngine(self.api_manager, self.translation_manager)
        )

        results = {"success": 0, "failed": 0, "skipped": 0}
        total = len(self.chunks)

        for i, chunk in enumerate(self.chunks):
            if self.stop_flag:
                break
            if chunk.is_processed:
                results["skipped"] += 1
            else:
                got = engine.translate_chunk(chunk)
                if got:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    # rotate key on failure so next chunk uses another key
                    if len(self.api_manager.get_api_keys()) > 1:
                        self.api_manager.rotate_api_key()

            Clock.schedule_once(
                lambda dt, i=i, t=total, r=dict(results): self._update_progress(i + 1, t, r),
                0
            )

        # Write translations back into page structure
        for chunk in self.chunks:
            if chunk.is_processed and chunk.translated_text:
                pi = chunk.page_num - 1
                if 0 <= pi < len(self.structured):
                    blocks = self.structured[pi]["blocks"]
                    if 0 <= chunk.block_index < len(blocks):
                        blocks[chunk.block_index]["translated"] = chunk.translated_text

        self.translation_manager.save_cache()
        Clock.schedule_once(lambda dt: self._translation_done(results), 0)

    def _update_progress(self, current, total, results):
        if not self.root or self.root.current != "progress":
            return
        scr = self.root.ids.progress_screen
        pct = (current / total) * 100 if total else 0
        scr.ids.prog_bar.value = pct
        scr.ids.prog_title.text = self.P(f"{current} از {total} بخش")
        scr.ids.prog_stats.text = self.P(
            f"موفق: {results['success']}   ناموفق: {results['failed']}   تکراری: {results['skipped']}"
        )
        scr.ids.prog_detail.text = self.P(
            "از طریق Cloudflare Worker" if self.root.ids.keys_screen.ids.worker_url.text.strip()
            else "اتصال مستقیم به Gemini"
        )

    def _translation_done(self, results):
        self.is_translating = False
        self.refresh_quota()
        # Generate outputs
        outputs = self.output_manager.generate_outputs(
            self.structured,
            self.pdf_processor.pdf_path,
            "pdf"
        )
        self.outputs = outputs
        msg = self.P(
            f"تمام شد! موفق: {results['success']} | ناموفق: {results['failed']}"
        )
        self.show_outputs_dialog(done_msg=msg)
        self.go_main()

    def show_outputs_dialog(self, done_msg=None):
        files = getattr(self, "outputs", None)
        if not files:
            files = {}
        lines = done_msg or ""
        for k, v in files.items():
            lines += f"\n{k.upper()}: {v}"
        self.dialog = MDDialog(
            title=self.P("خروجی‌ها"),
            text=self.P(lines),
            buttons=[
                MDRaisedButton(
                    text=self.P("بستن"),
                    font_name=self.fa_font,
                    on_release=lambda x: self.dialog.dismiss()
                )
            ]
        )
        self.dialog.open()

    # ---------- API keys ----------
    def refresh_keys(self):
        try:
            lst = self.root.ids.keys_screen.ids.keys_list
        except Exception:
            return
        lst.clear_widgets()
        default = self.api_manager.get_default_api_key()
        for key in self.api_manager.get_api_keys():
            label = key["name"]
            if key.get("api_key") == default:
                label += " (پیش‌فرض)"
            item = OneLineListItem(
                text=self.P(label),
                on_release=lambda x, k=key["api_key"]: self._select_key(k)
            )
            lst.add_widget(item)

    def _select_key(self, api_key):
        self.api_manager.set_default_api_key(api_key)
        self.refresh_keys()
        self.snack("کلید پیش‌فرض تغییر کرد")

    def add_key(self):
        scr = self.root.ids.keys_screen
        name = scr.ids.key_name.text.strip()
        value = scr.ids.key_value.text.strip()
        if not name or not value:
            self.snack("نام و کلید را وارد کنید")
            return
        if self.api_manager.add_api_key(name, value):
            if not self.api_manager.get_default_api_key():
                self.api_manager.set_default_api_key(value)
            scr.ids.key_name.text = ""
            scr.ids.key_value.text = ""
            self.refresh_keys()
            self.snack("کلید اضافه شد")
            self.refresh_quota()

    def save_worker_url(self):
        url = self.root.ids.keys_screen.ids.worker_url.text.strip()
        self.api_manager.save_worker_url(url)
        self.worker_url = url
        self.snack("آدرس Worker ذخیره شد" if url else "Worker غیرفعال شد")

    # ---------- UI helpers ----------
    def snack(self, text):
        MDSnackbar(text=self.P(text)).open()


if __name__ == "__main__":
    PDFTranslatorApp().run()
