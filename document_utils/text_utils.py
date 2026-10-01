"""Shared text normalization and safe document formatting helpers."""
from __future__ import annotations

import html
import re
import unicodedata

_TRANSLATION = str.maketrans({
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2212": "-", "\u2026": "...",
    "\u00a0": " ", "\u200b": "", "\ufeff": "",
})
_HEADING_WORDS = re.compile(r"^(TITLE|PARTIES|EFFECTIVE DATE|RECITALS?|INTRODUCTION|PURPOSE|TERMS(?: AND CONDITIONS)?|RESPONSIBILITIES|PAYMENT(?: AND COMPENSATION)?|COMPENSATION|CONFIDENTIALITY|TERM(?: AND TERMINATION)?|TERMINATION|GOVERNING LAW|SIGNATURES|EXCLUSIONS|OBLIGATIONS|REMEDIES|MISCELLANEOUS|NOTICES|PROPERTY|RENT|SECURITY DEPOSIT)(\s*:)?$", re.I)


def sanitize_text(text: str | None) -> str:
    """Normalize typographic punctuation and remove unsafe control characters.

    Newlines and tabs are retained; normal punctuation and Unicode letters are not
    stripped. This is text normalization, not HTML escaping.
    """
    if text is None:
        return ""
    normalized = unicodedata.normalize("NFC", str(text)).translate(_TRANSLATION)
    return "".join(ch for ch in normalized if ch in "\n\r\t" or unicodedata.category(ch) != "Cc").replace("\r\n", "\n").replace("\r", "\n")


def _is_heading(line: str) -> bool:
    candidate = line.strip().lstrip("#").strip().rstrip(":").strip()
    if not candidate:
        return False
    if _HEADING_WORDS.fullmatch(candidate):
        return True
    letters = [char for char in candidate if char.isalpha()]
    return len(candidate) <= 80 and len(letters) >= 4 and candidate == candidate.upper()


def document_blocks(text: str):
    """Yield (kind, text) tuples for title, heading, paragraph, and bullet blocks."""
    lines = sanitize_text(text).split("\n")
    meaningful = [line.strip() for line in lines if line.strip()]
    if not meaningful:
        return
    first = True
    in_terms = False
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        if first:
            title = line.lstrip("#").strip().strip("*")
            yield "title", title
            first = False
            continue
        if line.startswith("#") or _is_heading(line):
            heading = line.lstrip("#").strip().strip("*").rstrip(":").strip()
            in_terms = "TERM" in heading.upper() or heading.upper() in {"OBLIGATIONS", "RESPONSIBILITIES"}
            yield "heading", heading
            continue
        bullet_match = re.match(r"^(?:[-*•]|\d+[.)])\s+(.+)$", line)
        if bullet_match:
            yield "bullet", bullet_match.group(1).strip()
            continue
        if in_terms and ";" in line:
            for item in line.split(";"):
                if item.strip():
                    yield "bullet", item.strip()
            continue
        yield "paragraph", line


def format_html_preview(text: str) -> str:
    """Return escaped, presentation-only HTML from plain document text."""
    blocks = list(document_blocks(text))
    out = ['<article class="legal-document">']
    for kind, value in blocks:
        escaped = html.escape(value, quote=True)
        if kind == "title":
            out.append(f"<h1>{escaped}</h1>")
        elif kind == "heading":
            out.append(f"<h2>{escaped}</h2>")
        elif kind == "bullet":
            out.append(f"<p class=\"legal-bullet\">&#8226;&nbsp; {escaped}</p>")
        else:
            out.append(f"<p>{escaped}</p>")
    out.append("</article>")
    return "\n".join(out)
