"""Print beginner-friendly commands for the offline app and optional Gemini mode."""


def main() -> None:
    print("LegalEase — offline mode (no API key required)\n")
    print("From the project root, run:")
    print("  python -m streamlit run frontend/app.py")
    print("\nOpen the Local URL Streamlit prints (usually http://localhost:8501).")
    print("Keep 'Offline template (no API)' selected to avoid all external API calls.")
    print("\nOptional Gemini AI mode requires GEMINI_API_KEY in .env and a second terminal:")
    print("  uvicorn backend.main:app --reload")
    print("Then select 'Gemini AI (API key required)' in the app.")


if __name__ == "__main__":
    main()
