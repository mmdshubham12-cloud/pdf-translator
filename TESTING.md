# راهنمای تست

## تست‌ها

### 1. تست API Manager

```bash
python -c "from api_manager import APIManager; manager = APIManager(); print('API Manager works')"
```

### 2. تست PDF Processor

```bash
python -c "from pdf_utils import PDFProcessor; print('PDF Processor works')"
```

### 3. تست Translator

```bash
python -c "from translator import TranslationEngine; print('Translator works')"
```

### 4. تست Output Generator

```bash
python -c "from output_generator import HTMLGenerator; print('Output Generator works')"
```

## تست کامل

```bash
python test_translator.py
```

## تست واحد

### تست PDFProcessor

```python
def test_pdf_processor():
    processor = PDFProcessor("test.pdf")
    assert processor.load_pdf()
    assert len(processor.pages) > 0
    print("✅ PDFProcessor test passed")
```

### تست APIManager

```python
def test_api_manager():
    manager = APIManager()
    assert manager.add_api_key("Test", "key")
    assert manager.set_default_api_key("key")
    assert manager.get_default_api_key() == "key"
    print("✅ APIManager test passed")
```

### تست TranslationEngine

```python
def test_translation_engine():
    manager = APIManager()
    engine = TranslationEngine(manager, None)
    chunk = TranslationChunk(text="Test", page_num=0, block_index=0)
    result = engine.translate_chunk(chunk)
    assert result is not None
    print("✅ TranslationEngine test passed")
```

## تست دستی

### تست ترجمه

```python
from api_manager import APIManager
from translator import TranslationEngine
from pdf_utils import TranslationChunk

# Initialize
manager = APIManager()
engine = TranslationEngine(manager, None)

# Get API key
api_key = manager.get_default_api_key()

# Test text
test_text = "Hello, world!"

# Translate
chunk = TranslationChunk(text=test_text, page_num=0, block_index=0)
translated = engine.translate_chunk(chunk)

if translated:
    print(f"✅ Translated: {test_text} -> {translated}")
else:
    print("❌ Translation failed")
```

### تست PDF Processing

```python
from pdf_utils import PDFProcessor

# Load PDF
processor = PDFProcessor("test.pdf")
if processor.load_pdf():
    # Extract text
    text = processor.extract_text_with_formatting()
    print(f"✅ Extracted {len(text)} characters")

    # Extract structured data
    structured = processor.extract_text_with_structure()
    print(f"✅ Extracted {len(structured)} pages")
else:
    print("❌ Failed to load PDF")
```

### تست API Manager

```python
from api_manager import APIManager

# Initialize
manager = APIManager()

# Add key
if manager.add_api_key("Test Key", "test-key"):
    print("✅ API key added")

# Set default
if manager.set_default_api_key("test-key"):
    print("✅ Default API key set")

# Get stats
stats = manager.get_stats()
print(f"✅ Daily requests: {stats['daily_requests']}")
```

## تست خودکار

### تست با unittest

```python
import unittest
from pdf_utils import PDFProcessor
from api_manager import APIManager

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PDFProcessor("test.pdf")

    def test_load_pdf(self):
        self.assertTrue(self.processor.load_pdf())

    def test_extract_text(self):
        self.processor.load_pdf()
        text = self.processor.extract_text_with_formatting()
        self.assertIsInstance(text, str)

class TestAPIManager(unittest.TestCase):
    def setUp(self):
        self.manager = APIManager()

    def test_add_key(self):
        self.assertTrue(self.manager.add_api_key("Test", "key"))

    def test_set_default(self):
        self.manager.add_api_key("Test", "key")
        self.assertTrue(self.manager.set_default_api_key("key"))

if __name__ == '__main__':
    unittest.main()
```

## تست با pytest

```python
import pytest
from pdf_utils import PDFProcessor
from api_manager import APIManager

def test_pdf_processor():
    processor = PDFProcessor("test.pdf")
    assert processor.load_pdf()

def test_api_manager():
    manager = APIManager()
    assert manager.add_api_key("Test", "key")
    assert manager.set_default_api_key("key")
    assert manager.get_default_api_key() == "key"
```

## تست با nose

```python
from pdf_utils import PDFProcessor
from api_manager import APIManager

def test_pdf_processor():
    processor = PDFProcessor("test.pdf")
    assert processor.load_pdf()

def test_api_manager():
    manager = APIManager()
    assert manager.add_api_key("Test", "key")
```

## تست با coverage

```bash
# نصب coverage
pip install coverage

# اجرای تست
coverage run -m unittest discover

# گزارش
coverage report
coverage html
```

## تست با unittest.mock

```python
from unittest.mock import patch
from translator import TranslationEngine

def test_translation_with_mock():
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Translated"}]
                }
            }]
        }

        manager = APIManager()
        engine = TranslationEngine(manager, None)
        chunk = TranslationChunk(text="Test", page_num=0, block_index=0)
        result = engine.translate_chunk(chunk)

        assert result == "Translated"
```

## تست با pytest-mock

```python
from pytest_mock import MockerFixture

def test_translation_with_mock(mocker: MockerFixture):
    mock_post = mocker.patch('requests.post')
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{"text": "Translated"}]
            }
        }]
    }

    manager = APIManager()
    engine = TranslationEngine(manager, None)
    chunk = TranslationChunk(text="Test", page_num=0, block_index=0)
    result = engine.translate_chunk(chunk)

    assert result == "Translated"
```

## تست با selenium

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def test_ui():
    driver = webdriver.Chrome()
    driver.get("http://localhost:8080")

    # Find element
    element = driver.find_element(By.ID, "button")
    assert element is not None

    driver.quit()
```

## تست با appium

```python
from appium import webdriver

def test_mobile_ui():
    desired_caps = {
        'platformName': 'Android',
        'deviceName': 'Android Device',
        'app': '/path/to/app'
    }

    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

    # Find element
    element = driver.find_element_by_id("button")
    assert element is not None

    driver.quit()
```

## تست با Robot Framework

```robotframework
*** Settings ***
Library    SeleniumLibrary

*** Test Cases ***
Test UI
    [Documentation]    Test UI elements
    [Setup]    Open Browser    http://localhost:8080    chrome
    Element Should Be Visible    id=button
    Click Element    id=button
    [Teardown]    Close Browser
```

## تست با Behave

```python
from behave import given, when, then

@given('a user is on the main screen')
def step_impl(context):
    context.driver.get("http://localhost:8080")

@when('they click the translate button')
def step_impl(context):
    context.driver.find_element_by_id("button").click()

@then('the translation starts')
def step_impl(context):
    assert "Translating" in context.driver.page_source
```

## تست با pytest-bdd

```python
from pytest_bdd import given, when, then

@given('a user is on the main screen')
def step_impl(context):
    context.driver.get("http://localhost:8080")

@when('they click the translate button')
def step_impl(context):
    context.driver.find_element_by_id("button").click()

@then('the translation starts')
def step_impl(context):
    assert "Translating" in context.driver.page_source
```

## تست با unittest

```python
import unittest

class TestPDFTranslator(unittest.TestCase):
    def setUp(self):
        self.app = PDFTranslatorApp()

    def test_load_pdf(self):
        result = self.app.load_pdf("test.pdf")
        self.assertTrue(result)

    def test_translate(self):
        result = self.app.translate_pdf()
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
```

## نکات مهم

1. **تست‌ها را قبل از انتشار اجرا کنید**
2. **تست‌ها را به صورت منظم اجرا کنید**
3. **تست‌ها را در CI/CD اجرا کنید**
4. **تست‌ها را در Docker اجرا کنید**
5. **تست‌ها را در Pydroid 3 اجرا کنید**
