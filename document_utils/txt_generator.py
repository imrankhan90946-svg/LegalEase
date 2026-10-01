"""TXT export."""
from document_utils.text_utils import sanitize_text


def generate_txt(text: str) -> bytes:
    """Return a UTF-8 plain-text download payload."""
    return (sanitize_text(text).strip() + "\n").encode("utf-8")
