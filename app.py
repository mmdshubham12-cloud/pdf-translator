#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Translator Application with Kivy/KivyMD
Main application class with UI management
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
import threading
from pathlib import Path

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from pdf_utils import PDFProcessor, TranslationManager
from api_manager import APIManager
from translator import TranslationEngine
from output_generator import OutputManager


class MainScreen(Screen):
    """Main screen for PDF translation"""
    current_file = StringProperty("")
    temp_pdf_path = StringProperty("")
    html_output = BooleanProperty(True)
    pdf_output = BooleanProperty(True)
    daily_requests = NumericProperty(0)
    daily_limit = NumericProperty(500)
    tokens_used = NumericProperty(0)
    tokens_limit = NumericProperty(250000)
    usage_percent = NumericProperty(0)

    def on_enter(self):
        """Called when screen is entered"""
        app = App.get_running_app()
        stats = app.api_manager.get_stats()
        self.daily_requests = stats['daily_requests']
        self.daily_limit = stats['daily_limit']
        self.tokens_used = stats['tokens_used']
        self.tokens_limit = stats['tokens_limit']
        self.usage_percent = stats['usage_percent']


class SettingsScreen(Screen):
    """Settings screen for API keys and profiles"""
    current_profile_name = StringProperty("")
    auto_save_html = BooleanProperty(True)
    auto_save_pdf = BooleanProperty(True)
    theme_mode = StringProperty("dark")

    def on_enter(self):
        """Called when screen is entered"""
        app = App.get_running_app()
        profile = app.api_manager.get_default_api_key()
        if profile:
            key_stats = app.api_manager.get_key_stats(profile)
            self.current_profile_name = key_stats['name'] if key_stats else "نامشخص"


class ProgressScreen(Screen):
    """Progress screen for translation"""
    current_progress = NumericProperty(0)
    total_progress = NumericProperty(0)
    progress_value = NumericProperty(0)
    progress_status = StringProperty("در حال انتظار...")
    success_count = NumericProperty(0)
    failed_count = NumericProperty(0)
    skipped_count = NumericProperty(0)


class PDFTranslatorApp(App):
    """Main application class"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize app components
        self.api_manager = APIManager()
        self.translation_manager = TranslationManager()
        self.output_manager = OutputManager()

        # Translation state
        self.current_pdf = None
        self.current_structured_data = None
        self.current_chunks = None
        self.translation_engine = None
        self.worker_translator = None
        self.worker_url = "http://127.0.0.1:8787"
        self.is_translating = False
        self.stop_translation_flag = False

    def build(self):
        """Build the application UI"""
        # Configure theme
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Orange"
        self.theme_cls.theme_style = "Dark"

        # Create screen manager
        self.sm = ScreenManager()

        # Add screens
        self.sm.add_widget(MainScreen(name='main'))
        self.sm.add_widget(SettingsScreen(name='settings'))
        self.sm.add_widget(ProgressScreen(name='progress'))

        return self.sm

    # Main Screen Methods
    def open_pdf_dialog(self):
        """Open file selection dialog"""
        self.temp_pdf_path = ""

    def on_pdf_path_set(self):
        """Called when PDF path is set"""
        if self.temp_pdf_path:
            self.current_file = self.temp_pdf_path
            self.load_pdf()

    def load_pdf(self):
        """Load PDF file"""
        if not self.temp_pdf_path:
            return

        print(f"Loading PDF: {self.temp_pdf_path}")

        processor = PDFProcessor(self.temp_pdf_path)
        if processor.load_pdf():
            self.current_pdf = processor
            self.current_structured_data = processor.extract_text_with_structure()
            self.current_chunks = self.translation_manager.create_chunks(self.current_structured_data)

            # Update stats
            stats = self.api_manager.get_stats()
            self.daily_requests = stats['daily_requests']
            self.daily_limit = stats['daily_limit']
            self.tokens_used = stats['tokens_used']
            self.tokens_limit = stats['tokens_limit']
            self.usage_percent = stats['usage_percent']

            print(f"PDF loaded successfully. {len(self.current_structured_data)} pages found.")
        else:
            print("Failed to load PDF")

    def start_translation(self):
        """Start translation"""
        if not self.current_structured_data:
            print("Please load a PDF first")
            return

        if not self.api_manager.get_default_api_key():
            print("Please add an API key first")
            return

        self.show_progress_screen()
        self.is_translating = True
        self.stop_translation_flag = False

        # Run translation in background thread
        thread = threading.Thread(target=self._run_translation)
        thread.start()

    def _run_translation(self):
        """Run translation in background"""
        self.translation_engine = TranslationEngine(self.api_manager, self.translation_manager)
        self.worker_translator = None  # Not using worker for now

        results = self.translation_engine.translate_all(
            self.current_chunks,
            progress_callback=self._update_progress
        )

        self.success_count = results['success']
        self.failed_count = results['failed']
        self.skipped_count = results['skipped']

        self.translation_manager.save_cache()

        # Generate outputs
        if self.html_output or self.pdf_output:
            self.generate_outputs()

        self.is_translating = False

    def _update_progress(self, current, total, status):
        """Update progress"""
        progress = (current / total) * 100
        self.progress_value = progress
        self.current_progress = current
        self.total_progress = total
        self.progress_status = status

    def generate_outputs(self):
        """Generate output files"""
        output_format = "html" if self.html_output else "pdf"

        outputs = self.output_manager.generate_outputs(
            self.current_structured_data,
            self.current_pdf.pdf_path,
            output_format
        )

        print(f"Output generated: {outputs}")

    def stop_translation(self):
        """Stop translation"""
        self.stop_translation_flag = True

    # Settings Screen Methods
    def add_api_key_dialog(self):
        """Open add API key dialog"""
        dialog_key_name = self.root.ids.settings.ids.dialog_key_name
        dialog_key_api = self.root.ids.settings.ids.dialog_key_api

        name = dialog_key_name.text
        api_key = dialog_key_api.text

        if name and api_key:
            if self.api_manager.add_api_key(name, api_key):
                self.api_manager.set_default_api_key(api_key)
                self.refresh_api_keys_list()
                dialog_key_name.text = ""
                dialog_key_api.text = ""

    def change_profile_dialog(self):
        """Open change profile dialog"""
        self.refresh_api_keys_list()

    def confirm_add_api_key(self):
        """Confirm add API key"""
        dialog_key_name = self.root.ids.settings.ids.dialog_key_name
        dialog_key_api = self.root.ids.settings.ids.dialog_key_api

        name = dialog_key_name.text
        api_key = dialog_key_api.text

        if name and api_key:
            if self.api_manager.add_api_key(name, api_key):
                self.api_manager.set_default_api_key(api_key)
                self.refresh_api_keys_list()
                self.current_profile_name = name
                dialog_key_name.text = ""
                dialog_key_api.text = ""

    def refresh_api_keys_list(self):
        """Refresh API keys list"""
        api_keys = self.api_manager.get_api_keys()
        list_widget = self.root.ids.settings.ids.api_keys_list

        # Clear list
        list_widget.clear_widgets()

        # Add keys
        for key in api_keys:
            OneLineListItem:
                text: f"{key['name']} {'(پیش‌فرض)' if key['is_default'] else ''}"
                on_release: self.select_profile(key['api_key'])

    def select_profile(self, api_key):
        """Select profile"""
        self.api_manager.set_default_api_key(api_key)
        stats = self.api_manager.get_key_stats(api_key)
        self.current_profile_name = stats['name'] if stats else "نامشخص"

    # Screen Navigation
    def show_progress_screen(self):
        """Show progress screen"""
        screen = self.sm.get_screen('progress')
        screen.current_progress = 0
        screen.total_progress = len(self.current_chunks) if self.current_chunks else 0
        screen.progress_value = 0
        screen.progress_status = "در حال انتظار..."
        screen.success_count = 0
        screen.failed_count = 0
        screen.skipped_count = 0
        self.sm.current = 'progress'

    def show_settings_screen(self):
        """Show settings screen"""
        self.sm.current = 'settings'

    def show_main_screen(self):
        """Show main screen"""
        self.sm.current = 'main'

    # Utility Methods
    def toggle_html_output(self, value):
        """Toggle HTML output"""
        self.html_output = value

    def toggle_pdf_output(self, value):
        """Toggle PDF output"""
        self.pdf_output = value

    def toggle_auto_save_html(self, value):
        """Toggle auto save HTML"""
        self.auto_save_html = value

    def toggle_auto_save_pdf(self, value):
        """Toggle auto save PDF"""
        self.auto_save_pdf = value


if __name__ == '__main__':
    PDFTranslatorApp().run()
