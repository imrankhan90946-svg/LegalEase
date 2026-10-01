"""Paginated PDF export using fpdf2."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fpdf import FPDF
from PIL import Image
from io import BytesIO

from document_utils.text_utils import document_blocks, sanitize_text

NAVY = (24, 59, 86)


def _font_paths():
    candidates = [
        ("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf", "/usr/share/fonts/truetype/liberation2/LiberationSerif-Bold.ttf"),
        ("C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/timesbd.ttf"),
    ]
    for regular, bold in candidates:
        if Path(regular).exists():
            return regular, bold if Path(bold).exists() else regular
    return None, None


class _LegalPDF(FPDF):
    def __init__(self, logo_path=None, *args, **kwargs):
        self.logo_path = logo_path
        super().__init__(*args, **kwargs)
        self._legal_font = "Times"

    def header(self):
        self.set_y(9)
        if self.logo_path:
            self.image(self.logo_path, x=165, y=8, w=28, h=12, keep_aspect_ratio=True)
        else:
            self.set_font(self._legal_font, "B", 9)
            self.set_text_color(*NAVY)
            self.cell(0, 6, "LEGALEASE", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(205, 214, 222)
        self.line(18, 23, 192, 23)
        self.set_y(29)

    def footer(self):
        self.set_y(-15)
        self.set_draw_color(205, 214, 222)
        self.line(18, self.get_y(), 192, self.get_y())
        self.set_y(-12)
        self.set_font(self._legal_font, "", 8)
        self.set_text_color(100, 110, 120)
        self.cell(0, 7, f"LegalEase  |  Page {self.page_no()}/{{nb}}", align="C")


def generate_pdf(text: str, document_type: str, logo=None) -> bytes:
    """Build a readable multi-page PDF and return its bytes."""
    clean_text = sanitize_text(text).strip()
    if not clean_text:
        raise ValueError("Cannot create a PDF from an empty document.")
    logo_path = None
    try:
        if logo is not None:
            data = logo.getvalue() if hasattr(logo, "getvalue") else (logo.read() if hasattr(logo, "read") else bytes(logo))
            if data:
                image = Image.open(BytesIO(data)).convert("RGBA")
                handle = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                logo_path = handle.name
                handle.close()
                image.save(logo_path, format="PNG")
        pdf = _LegalPDF(logo_path=logo_path, format="A4")
        pdf.set_margins(20, 32, 20)
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.alias_nb_pages()
        regular, bold = _font_paths()
        if regular:
            pdf.add_font("Legal", "", regular)
            pdf.add_font("Legal", "B", bold)
            unicode_font = True
            pdf._legal_font = "Legal"
        else:
            unicode_font = False
            pdf._legal_font = "Times"
        pdf.add_page()
        blocks = list(document_blocks(clean_text))
        if not blocks:
            raise ValueError("Cannot create a PDF from an empty document.")
        title = blocks[0][1]
        pdf.set_font(pdf._legal_font, "B", 17)
        pdf.set_text_color(*NAVY)
        pdf.multi_cell(0, 9, title, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        pdf.set_font(pdf._legal_font, "", 10)
        pdf.set_text_color(100, 110, 120)
        pdf.multi_cell(0, 6, document_type, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(9)

        for kind, value in blocks[1:]:
            if not unicode_font:
                value = value.encode("latin-1", "replace").decode("latin-1")
            if kind == "heading":
                pdf.ln(3)
                pdf.set_font(pdf._legal_font, "B", 12)
                pdf.set_text_color(*NAVY)
                pdf.multi_cell(0, 7, value, new_x="LMARGIN", new_y="NEXT")
                pdf.set_text_color(35, 42, 49)
            elif kind == "title":
                continue
            elif kind == "bullet":
                pdf.set_font(pdf._legal_font, "", 11)
                pdf.set_text_color(35, 42, 49)
                pdf.set_x(24)
                pdf.multi_cell(0, 6, "- " + value, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            else:
                pdf.set_font(pdf._legal_font, "", 11)
                pdf.set_text_color(35, 42, 49)
                pdf.multi_cell(0, 6, value, new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)
        return bytes(pdf.output())
    except Exception as exc:
        if isinstance(exc, ValueError):
            raise
        raise ValueError("PDF creation failed. Check the document text and logo file, then try again.") from exc
    finally:
        if logo_path and os.path.exists(logo_path):
            os.unlink(logo_path)
