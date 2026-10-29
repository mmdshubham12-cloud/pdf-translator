#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Generator for HTML and PDF
Creates translated outputs with preserved structure
"""

from pathlib import Path
from typing import List, Dict


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
        <h1>📄 ترجمه PDF با Gemini</h1>
        {content}
    </div>
</body>
</html>"""

    def generate(self, structured_data: List[Dict], use_translated: bool = True) -> str:
        """Generate HTML from structured data."""
        content = ""

        for page in structured_data:
            content += self._generate_page(page, use_translated)

        return self.html_template.format(content=content)

    def _generate_page(self, page_data: Dict, use_translated: bool) -> str:
        """Generate HTML for a single page"""
        page_num = page_data['page_num']
        blocks = page_data['blocks']

        page_html = '<div class="page">\n'
        page_html += f'    <div class="page-header">صفحه {page_num}</div>\n'

        for block in blocks:
            if use_translated and block.get('translated'):
                text = block['translated']
            else:
                text = block['text']
            import html as html_module
            text = html_module.escape(text)

            if block.get('is_bold'):
                page_html += f'    <div class="paragraph bold">{text}</div>\n'
            else:
                page_html += f'    <div class="paragraph">{text}</div>\n'

        page_html += '</div>\n'
        return page_html

    def save(self, html: str, output_path: str):
        """Save HTML to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            return True
        except Exception as e:
            print(f"❌ Khata dar zakhire HTML: {e}")
            return False


class PDFGenerator:
    """Generate PDF output using fpdf2 (works on Pydroid 3)"""

    def __init__(self):
        try:
            from fpdf import FPDF
            self.FPDF = FPDF
        except ImportError:
            print("⚠️  fpdf2 nasb nist. Nasb konid: pip install fpdf2")
            self.FPDF = None

    def generate(self, structured_data: List[Dict], pdf_path: str) -> bool:
        """Generate PDF directly from structured data (translated text)"""
        if not self.FPDF:
            print("❌ fpdf2 nasb nist")
            return False

        try:
            pdf = self.FPDF(orientation='P', unit='mm', format='A4')
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()

            # Title
            pdf.set_font('helvetica', 'B', 16)
            pdf.cell(0, 10, 'PDF Translator', 0, 1, 'C')
            pdf.ln(5)

            for page in structured_data:
                pdf.set_font('helvetica', 'B', 12)
                pdf.cell(0, 10, f'Page {page["page_num"]}', 0, 1, 'C')
                pdf.ln(2)

                for block in page['blocks']:
                    text = block.get('translated') or block['text']
                    # fpdf2 core fonts can't render Persian/Arabic or Unicode.
                    # Encode to latin-1 fallback so it does not crash.
                    safe_text = text.encode('latin-1', errors='replace').decode('latin-1')

                    if block.get('is_bold'):
                        pdf.set_font('helvetica', 'B', 11)
                    else:
                        pdf.set_font('helvetica', '', 11)

                    pdf.multi_cell(0, 7, safe_text)
                    pdf.ln(2)

            pdf.output(pdf_path)
            return True

        except Exception as e:
            print(f"❌ Khata dar tolid PDF: {e}")
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
        if output_format in ["html", "pdf"]:
            html_content = self.html_generator.generate(structured_data, use_translated=True)
            html_path = self.output_dir / f"{Path(input_file).stem}_translated.html"
            if self.html_generator.save(html_content, str(html_path)):
                outputs["html"] = str(html_path)

        # Generate PDF directly with fpdf2 (no weasyprint dependency)
        if output_format == "pdf":
            pdf_path = self.output_dir / f"{Path(input_file).stem}_translated.pdf"
            if self.pdf_generator.generate(structured_data, str(pdf_path)):
                outputs["pdf"] = str(pdf_path)

        return outputs
