"""Local legal-document skeleton generation that makes no network/API calls."""
from __future__ import annotations

import re

from document_utils.text_utils import sanitize_text


def _term_items(text: str) -> list[str]:
    """Split user-supplied terms into readable bullets without creating new terms."""
    items: list[str] = []
    for line in sanitize_text(text).splitlines():
        for item in line.split(";"):
            cleaned = re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", item).strip()
            if cleaned:
                items.append(cleaned)
    return items


def generate_offline_draft(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
    additional_details: str = "",
) -> str:
    """Create a fill-in draft using only user-provided content, without any API call."""
    doc_type = sanitize_text(document_type).strip() or "Legal Document"
    clean_parties = sanitize_text(parties).strip()
    clean_date = sanitize_text(effective_date).strip()
    clean_details = sanitize_text(additional_details).strip()
    terms_list = _term_items(terms)

    if not clean_parties:
        raise ValueError("Enter the parties before generating a draft.")
    if not terms_list:
        raise ValueError("Enter at least one agreed term before generating a draft.")

    lines = [
        doc_type.upper(),
        "OFFLINE TEMPLATE — NO AI OR EXTERNAL API USED",
        "This fill-in draft uses only the information you supplied. It does not generate or add legal clauses. Complete the placeholders and have a qualified legal professional review it before use.",
        "",
        "EFFECTIVE DATE",
        clean_date or "[Enter effective date]",
        "",
        "PARTIES",
        clean_parties,
        "",
        "AGREED TERMS PROVIDED",
    ]
    lines.extend(f"- {item}" for item in terms_list)
    lines.extend([
        "",
        "ADDITIONAL DETAILS",
        clean_details or "[Add any agreed details, or leave blank if not applicable.]",
        "",
        "DETAILS TO COMPLETE IF APPLICABLE",
        "Addresses and notice details: [Complete if needed]",
        "Term, renewal, and termination details: [Complete if agreed]",
        "Governing law or jurisdiction: [Specify if agreed; obtain legal review]",
        "",
        "SIGNATURES",
        "Party/representative name: ______________________________",
        "Signature: _____________________________________________",
        "Date: _________________________________________________",
        "",
        "Party/representative name: ______________________________",
        "Signature: _____________________________________________",
        "Date: _________________________________________________",
        "",
        "REVIEW NOTE",
        "This offline template organizes your inputs; it is not legal advice and is not a complete, jurisdiction-specific agreement. Review and complete it before signing or relying on it.",
    ])
    return "\n".join(lines)
