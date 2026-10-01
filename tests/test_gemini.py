"""Gemini tests are fully local and do not require network access or credentials."""
import pytest

from ai_core.gemini_generator import GeminiConfigurationError, GeminiDocumentGenerator


def test_missing_api_key_has_actionable_message():
    generator = GeminiDocumentGenerator(api_key="")
    with pytest.raises(GeminiConfigurationError, match="Add GEMINI_API_KEY"):
        generator.generate_document("Contract", "A and B", "As agreed", "2026-10-01")


def test_prompt_preserves_factual_boundaries():
    prompt = GeminiDocumentGenerator.build_prompt(
        "General Agreement", "Alice and Acme", "Pay $500", "2026-10-01", "No jurisdiction supplied"
    )
    assert "Alice and Acme" in prompt
    assert "Pay $500" in prompt
    assert "Do not add a specific governing jurisdiction unless supplied." in prompt
