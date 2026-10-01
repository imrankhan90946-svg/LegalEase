"""Small UI helpers used by the Streamlit frontend."""
from document_utils.text_utils import format_html_preview


def render_document_preview(text: str) -> str:
    """Return escaped preview HTML with a compact document-paper style."""
    body = format_html_preview(text)
    return f"""<style>
    .legal-document {{ background:#fff; color:#273444; max-width:820px; margin:0 auto;
      padding:48px 58px; border:1px solid #e5eaf0; border-radius:8px;
      box-shadow:0 8px 28px rgba(18,42,63,.08); font:15px/1.75 Georgia,'Times New Roman',serif; }}
    .legal-document h1 {{ color:#183b56; font-size:25px; line-height:1.25; text-align:center;
      text-transform:uppercase; letter-spacing:.035em; margin:0 0 30px; }}
    .legal-document h2 {{ color:#183b56; font-size:16px; margin:25px 0 8px; border-bottom:1px solid #e7edf2; padding-bottom:5px; }}
    .legal-document p {{ margin:0 0 12px; white-space:pre-wrap; }}
    .legal-document .legal-bullet {{ padding-left:20px; text-indent:-14px; }}
    @media(max-width:640px) {{ .legal-document {{padding:25px 20px;}} }}
    </style>{body}"""
