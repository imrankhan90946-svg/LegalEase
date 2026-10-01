"""Tests for the local-only draft path; it must not depend on network/API access."""
import pytest

from document_utils.offline_generator import generate_offline_draft


def test_offline_draft_uses_supplied_facts_and_placeholders():
    draft = generate_offline_draft(
        "Freelance Contract",
        "Provider: Jane Doe\nClient: Example Co.",
        "Payment within 30 days; Deliver the agreed project",
        "2026-10-01",
        "Plain language",
    )
    assert draft.startswith("FREELANCE CONTRACT\n")
    assert "OFFLINE TEMPLATE — NO AI OR EXTERNAL API USED" in draft
    assert "Provider: Jane Doe" in draft
    assert "Payment within 30 days" in draft
    assert "Deliver the agreed project" in draft
    assert "Plain language" in draft
    assert "[Specify if agreed; obtain legal review]" in draft
    assert "governing law is" not in draft.lower()


def test_offline_draft_requires_parties_and_terms():
    with pytest.raises(ValueError, match="parties"):
        generate_offline_draft("Contract", "", "Payment on delivery", "2026-10-01")
    with pytest.raises(ValueError, match="agreed term"):
        generate_offline_draft("Contract", "A and B", " ; \n", "2026-10-01")
