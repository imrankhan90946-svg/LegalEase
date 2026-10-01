"""Document-generation API routes."""
from fastapi import APIRouter, HTTPException

from ai_core.gemini_generator import GeminiDocumentGenerator, GeminiConfigurationError, GeminiGenerationError
from backend.models import DocumentRequest, DocumentResponse

router = APIRouter()
generator = GeminiDocumentGenerator()


@router.post("/generate", response_model=DocumentResponse, responses={
    422: {"description": "Input validation failed"},
    502: {"description": "Gemini generation failed"},
    503: {"description": "Gemini API key is not configured"},
})
def generate_document(request: DocumentRequest) -> DocumentResponse:
    """Draft a document from user-supplied information using Gemini."""
    try:
        content = generator.generate_document(
            document_type=request.document_type,
            parties=request.parties,
            terms=request.terms,
            effective_date=request.effective_date.isoformat(),
            additional_details=request.additional_details,
        )
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except GeminiGenerationError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # Defensive boundary: never return a traceback to a client.
        raise HTTPException(status_code=502, detail="Document generation failed. Check the server logs and try again.") from exc
    return DocumentResponse(document_type=request.document_type, content=content)
