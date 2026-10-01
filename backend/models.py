"""Validated API models for LegalEase."""
from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


DocumentType = Literal[
    "General Agreement",
    "Contract",
    "Non-Disclosure Agreement (NDA)",
    "Employment Contract",
    "Employment Offer Letter",
    "Freelance Contract",
    "Lease Agreement",
    "Service Agreement",
    "Business Partnership Agreement",
    "Consulting Agreement",
    "Custom Legal Document",
]


class DocumentRequest(BaseModel):
    """User-provided facts used to draft a document; no secrets belong here."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    document_type: DocumentType
    parties: str = Field(min_length=1, max_length=8_000, description="Names and roles of all parties")
    terms: str = Field(min_length=1, max_length=20_000, description="User-supplied terms and conditions")
    effective_date: date
    additional_details: str = Field(default="", max_length=8_000)

    @field_validator("parties", "terms")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value.strip()

    @field_validator("additional_details")
    @classmethod
    def normalize_optional_details(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def custom_type_requires_description(self) -> "DocumentRequest":
        if self.document_type == "Custom Legal Document" and not self.additional_details:
            raise ValueError("Describe the custom document in additional_details.")
        return self


class DocumentResponse(BaseModel):
    success: bool = True
    document_type: str
    content: str


class ErrorResponse(BaseModel):
    success: bool = False
    detail: str
