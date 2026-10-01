"""LegalEase FastAPI application."""
from fastapi import FastAPI

from backend.routes import router as document_router

app = FastAPI(
    title="LegalEase API",
    description="Private backend for AI-assisted legal document drafting and export.",
    version="1.0.0",
)
app.include_router(document_router, tags=["Documents"])


@app.get("/", tags=["Status"])
def root() -> dict[str, str]:
    return {"message": "LegalEase API is running"}


@app.get("/health", tags=["Status"])
def health() -> dict[str, str]:
    return {"status": "healthy"}
