"""Professional editable DOCX export using python-docx."""
from __future__ import annotations

from io import BytesIO

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from document_utils.text_utils import document_blocks, sanitize_text

NAVY = "183B56"


def _logo_stream(logo):
    if logo is None:
        return None
    if hasattr(logo, "getvalue"):
        data = logo.getvalue()
    elif hasattr(logo, "read"):
        data = logo.read()
    else:
        data = bytes(logo)
    if not data:
        return None
    # Re-encode through Pillow to normalize JPEG/PNG and reject invalid image data.
    from PIL import Image
    image = Image.open(BytesIO(data))
    image.verify()
    image = Image.open(BytesIO(data)).convert("RGBA")
    output = BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output


def _set_cell_shading(cell, fill: str) -> None:
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    cell._tc.get_or_add_tcPr().append(shading)


def _add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("LegalEase  |  Page ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)


def generate_docx(text: str, document_type: str, logo=None) -> bytes:
    """Build a legal-style DOCX and return its bytes. Logo may be bytes or a file-like object."""
    clean_text = sanitize_text(text).strip()
    if not clean_text:
        raise ValueError("Cannot create a DOCX from an empty document.")
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(35, 42, 49)
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.12
    for style_name, size in (("Heading 1", 15), ("Heading 2", 12)):
        style = doc.styles[style_name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(NAVY)
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(5)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    try:
        logo_stream = _logo_stream(logo)
        if logo_stream:
            header.add_run().add_picture(logo_stream, width=Inches(1.0))
        else:
            run = header.add_run("LEGALEASE")
            run.bold = True
            run.font.name = "Times New Roman"
            run.font.color.rgb = RGBColor.from_string(NAVY)
    except Exception as exc:
        raise ValueError("The uploaded logo could not be added to the DOCX. Please upload a valid PNG or JPEG.") from exc

    footer = section.footer.paragraphs[0]
    _add_page_number(footer)
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].font.color.rgb = RGBColor(100, 110, 120)

    blocks = list(document_blocks(clean_text))
    if not blocks:
        raise ValueError("Cannot create a DOCX from an empty document.")
    title_text = blocks[0][1]
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(14)
    title_run = title.add_run(title_text)
    title_run.bold = True
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(18)
    title_run.font.color.rgb = RGBColor.from_string(NAVY)
    type_line = doc.add_paragraph(document_type)
    type_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    type_line.paragraph_format.space_after = Pt(18)
    for run in type_line.runs:
        run.italic = True
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(100, 110, 120)

    for kind, value in blocks[1:]:
        if kind == "heading":
            doc.add_heading(value, level=1)
        elif kind == "bullet":
            para = doc.add_paragraph(style="List Bullet")
            para.paragraph_format.left_indent = Inches(0.25)
            para.add_run(value)
        else:
            para = doc.add_paragraph(value)
            if value.upper().startswith("[USER TO PROVIDE:"):
                for run in para.runs:
                    run.italic = True
                    run.font.color.rgb = RGBColor(150, 80, 20)

    # Keep sensible defaults on the final section for later editing in Word.
    doc.core_properties.title = title_text[:250]
    doc.core_properties.subject = f"{document_type} draft generated with LegalEase"
    doc.core_properties.author = "LegalEase"
    buffer = BytesIO()
    doc.save(buffer)
    return buffer.getvalue()
