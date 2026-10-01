"""Beginner-friendly command helper. Start backend and frontend in separate terminals."""


def main() -> None:
    print("LegalEase local development\n")
    print("Open two VS Code terminals from the project root.")
    print("Terminal 1 — FastAPI backend:")
    print("  uvicorn backend.main:app --reload")
    print("\nTerminal 2 — Streamlit frontend:")
    print("  streamlit run frontend/app.py")
    print("\nAPI docs: http://127.0.0.1:8000/docs")
    print("App UI:   http://localhost:8501")
    print("\nMake sure .env exists and GEMINI_API_KEY is set before generating drafts.")


if __name__ == "__main__":
    main()
