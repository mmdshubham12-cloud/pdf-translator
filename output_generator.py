#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Generator for HTML and PDF
Creates translated outputs with preserved structure
"""

from pathlib import Path
from typing import List, Dict
import re


class HTMLGenerator:
    """Generate HTML output with formatting preserved"""

    def __init__(self):
        self.html_template = self._get_template()

    def _get_template(self) -> str:
        """Get HTML template"""
        return """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ترجمه PDF</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Tahoma', 'Segoe UI', sans-serif;
            line-height: 1.8;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }}

        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}

        .page {{
            margin: 30px 0;
            padding: 20px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: #f9f9f9;
        }}

        .page-header {{
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 20px;
            padding: 10px;
            background: #f0f0f0;
            border-radius: 5px;
        }}

        .paragraph {{
            margin: 15px 0;
            text-align: justify;
        }}

        .bold {{
            font-weight: bold;
            color: #333;
        }}

        .bullet {{
            list-style-type: disc;
            margin-right: 20px;
        }}

        .heading {{
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0 10px 0;
            text-align: center;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                padding: 0;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📄 ترجمه PDF با Gemini 3.5 Flash</h1>
        {content}
    </div>
</body>
</html>"""

    def generate(self, structured_data: List[Dict]) -> str:
        """Generate HTML from structured data"""
        content = ""

        for page in structured_data:
            content += self._generate_page(page)

        return self.html_template.format(content=content)

    def _generate_page(self, page_data: Dict) -> str:
        """Generate HTML for a single page"""
        page_num = page_data['page_num']
        blocks = page_data['blocks']

        page_html = f'<div class="page">\n'

        # Page header
        page_html += f'    <div class="page-header">صفحه {page_num}</div>\n'

        # Generate blocks
        for block in blocks:
            if block.get('is_bold'):
                page_html += f'    <div class="paragraph bold">{block["text"]}</div>\n'
            else:
                page_html += f'    <div class="paragraph">{block["text"]}</div>\n'

        page_html += '</div>\n'
        return page_html

    def save(self, html: str, output_path: str):
        """Save HTML to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"❌ خطا در ذخیره HTML: {e}")
            return False


class PDFGenerator:
    """Generate PDF output with preserved structure"""

    def __init__(self):
        try:
            from fpdf import FPDF
            self.FPDF = FPDF
        except ImportError:
            print("⚠️  فایل FPDF نصب نیست. لطفاً نصب کنید: pip install fpdf2")
            self.FPDF = None

    def generate(self, structured_data: List[Dict], html_path: str, pdf_path: str):
        """Generate PDF from structured data"""
        if not self.FPDF:
            print("❌ FPDF نصب نیست")
            return False

        try:
            pdf = self.FPDF()
            pdf.add_page()

            # Add title
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'ترجمه PDF با Gemini 3.5 Flash', 0, 1, 'C')

            for page in structured_data:
                pdf.ln(10)
                pdf.set_font('Arial', 'B', 12)
                pdf.cell(0, 10, f'صفحه {page["page_num"]}', 0, 1, 'C')

                for block in page['blocks']:
                    pdf.set_font('Arial', '', 11)
                    pdf.cell(0, 7, block['text'], 0, 1)

            pdf.output(pdf_path)
            return True

        except Exception as e:
            print(f"❌ خطا در تولید PDF: {e}")
            return False

    def save(self, html_content: str, pdf_path: str):
        """Save HTML content to PDF"""
        if not self.FPDF:
            print("❌ FPDF نصب نیست")
            return False

        try:
            # Read HTML
            with open(pdf_path.replace('.pdf', '.html'), 'w', encoding='utf-8') as f:
                f.write(html_content)

            # Convert to PDF using weasyprint (if available)
            try:
                from weasyprint import HTML
                HTML(string=html_content).write_pdf(pdf_path)
                return True
            except ImportError:
                print("⚠️  weasyprint نصب نیست. فقط HTML ذخیره شد.")
                return True

        except Exception as e:
            print(f"❌ خطا در ذخیره PDF: {e}")
            return False


class OutputManager:
    """Manage output generation"""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.html_generator = HTMLGenerator()
        self.pdf_generator = PDFGenerator()

    def generate_outputs(self, structured_data: List[Dict], input_file: str, output_format: str = "pdf") -> Dict[str, str]:
        """Generate outputs based on format"""
        outputs = {}

        # Generate HTML
        html_content = self.html_generator.generate(structured_data)

        if output_format in ["html", "pdf"]:
            html_path = self.output_dir / f"{Path(input_file).stem}_translated.html"
            if self.html_generator.save(html_content, str(html_path)):
                outputs["html"] = str(html_path)

        # Generate PDF
        if output_format == "pdf":
            pdf_path = self.output_dir / f"{Path(input_file).stem}_translated.pdf"
            if self.pdf_generator.generate(structured_data, str(html_path), str(pdf_path)):
                outputs["pdf"] = str(pdf_path)

        return outputs
