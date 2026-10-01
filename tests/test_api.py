"""API tests do not call Gemini or require an API key."""
from fastapi.testclient import TestClient

from backend.main import app
from backend.routes import generator

client = TestClient(app)


def test_root_and_health():
    assert client.get("/").json() == {"message": "LegalEase API is running"}
    assert client.get("/health").json() == {"status": "healthy"}
    assert client.get("/docs").status_code == 200


def test_generate_uses_generator(monkeypatch):
    def fake_generate(**kwargs):
        assert kwargs["document_type"] == "Freelance Contract"
        assert kwargs["effective_date"] == "2026-10-01"
        return "FREELANCE CONTRACT\n\nPARTIES\nJane Doe and TechNova Inc."

    monkeypatch.setattr(generator, "generate_document", fake_generate)
    response = client.post("/generate", json={
        "document_type": "Freelance Contract",
        "parties": "Jane Doe (Provider); TechNova Inc. (Client)",
        "terms": "Payment within 30 days; confidentiality must be maintained",
        "effective_date": "2026-10-01",
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["document_type"] == "Freelance Contract"
    assert "Jane Doe" in payload["content"]


def test_required_fields_and_unsupported_type_rejected():
    response = client.post("/generate", json={
        "document_type": "Invalid Agreement", "parties": " ", "terms": "", "effective_date": "not-a-date"
    })
    assert response.status_code == 422


def test_custom_document_requires_description():
    response = client.post("/generate", json={
        "document_type": "Custom Legal Document", "parties": "Party A and Party B",
        "terms": "As agreed", "effective_date": "2026-10-01",
    })
    assert response.status_code == 422
