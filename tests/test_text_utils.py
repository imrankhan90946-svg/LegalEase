"""Text normalization and preview-safety tests."""
from document_utils.text_utils import format_html_preview, sanitize_text


def test_sanitize_typographic_punctuation_and_controls():
    assert sanitize_text("“Hi”—it’s fine…\x00\nNext") == '"Hi"-it\'s fine...\nNext'
    assert sanitize_text("Café, $10.50!") == "Café, $10.50!"


def test_preview_escapes_html_and_formats_headings():
    preview = format_html_preview("SERVICE AGREEMENT\n\nTERMS AND CONDITIONS\n<script>alert('x')</script>")
    assert "<h1>SERVICE AGREEMENT</h1>" in preview
    assert "<h2>TERMS AND CONDITIONS</h2>" in preview
    assert "&lt;script&gt;" in preview
    assert "<script>" not in preview
