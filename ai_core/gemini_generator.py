"""Gemini-backed legal document drafting with lazy SDK initialization."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


class GeminiConfigurationError(RuntimeError):
    """Raised when Gemini credentials or SDK configuration are missing."""


class GeminiGenerationError(RuntimeError):
    """Raised when the upstream model cannot generate a document."""


SYSTEM_INSTRUCTION = """You are a careful legal-document drafting assistant, not a lawyer.
Draft a clear, structured first draft using ONLY facts explicitly supplied by the user.
Never invent names, addresses, amounts, dates, jurisdiction, statutes, or other facts.
If a material detail is missing, insert a conspicuous [USER TO PROVIDE: detail] note.
Use headings relevant to the chosen document type; omit irrelevant clauses. Preserve
user-supplied terms without changing their meaning. Do not claim that the document is
legally valid, enforceable, or jurisdiction-specific. Include signature blocks where
appropriate. Return only the document text, without commentary or markdown code fences."""


class GeminiDocumentGenerator:
    """Create a Gemini client only when generation is requested."""

    def __init__(self, api_key: str | None = None, model: str | None = None, client=None) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "").strip()
        self.model = (model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")).strip()
        self._client = client

    def _get_client(self):
        if not self.api_key:
            raise GeminiConfigurationError(
                "Gemini API key is not configured. Add GEMINI_API_KEY to the project's .env file, then restart the backend."
            )
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except ImportError as exc:
                raise GeminiConfigurationError(
                    "The Google Gemini SDK is not installed. Run: pip install -r requirements.txt"
                ) from exc
            except Exception as exc:
                raise GeminiConfigurationError("Could not initialize Gemini. Check your API key and configuration.") from exc
        return self._client

    @staticmethod
    def build_prompt(document_type: str, parties: str, terms: str, effective_date: str, additional_details: str = "") -> str:
        custom_instruction = (
            "For Custom Legal Document, use the requested document description in additional details to determine the form."
            if document_type == "Custom Legal Document" else ""
        )
        return f"""Draft a {document_type} based on this input.
{custom_instruction}

DOCUMENT TYPE: {document_type}
PARTIES AND ROLES (verbatim source facts):
{parties}

EFFECTIVE DATE: {effective_date}

TERMS AND CONDITIONS (preserve meaning; do not add promises):
{terms}

ADDITIONAL DETAILS (context only; do not infer missing facts):
{additional_details or '[None provided]'}

Formatting guidance: Use a document title, parties, effective date, a concise introduction
if appropriate, document-specific operative sections, and signature blocks where suitable.
Add payment, confidentiality, termination, governing-law, or other clauses only when
appropriate and supported by the supplied information. Mark missing material facts as
[USER TO PROVIDE: ...]. Do not add a specific governing jurisdiction unless supplied."""

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        additional_details: str = "",
    ) -> str:
        client = self._get_client()
        try:
            from google.genai import types
            response = client.models.generate_content(
                model=self.model,
                contents=self.build_prompt(document_type, parties, terms, effective_date, additional_details),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.25,
                    max_output_tokens=8_000,
                ),
            )
            content = (response.text or "").strip()
            if not content:
                raise GeminiGenerationError("Gemini returned an empty draft. Please try again with more details.")
            return content
        except GeminiGenerationError:
            raise
        except Exception as exc:
            # Avoid reflecting upstream exception details that may contain request metadata.
            raise GeminiGenerationError(
                "Gemini could not generate the document. Verify your API key, model name, network connection, and quota, then try again."
            ) from exc
