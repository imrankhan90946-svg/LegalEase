# LegalEase — Offline-First Legal Document Generator

LegalEase is a local-first student project that creates an editable legal-document template from user-provided facts without an API key. Its default **Offline template** mode runs locally, adds no AI-generated clauses, and leaves placeholders for unspecified terms. An optional Gemini AI mode can create AI-assisted drafts through a FastAPI backend. Drafts can be reviewed, edited, previewed, and downloaded as TXT, DOCX, or PDF.

> **Legal disclaimer:** LegalEase creates fill-in templates and optional AI-assisted drafts for informational and drafting purposes. It does not provide legal advice. Users should consult a qualified legal professional for legal advice and jurisdiction-specific review.

## Features

- 11 document types, including contracts, NDA, employment, freelance, lease, service, partnership, consulting, and custom documents.
- Offline template generation requiring no API key or runtime internet connection.
- Optional Gemini-backed generation with explicit guardrails against invented facts and unsupported legal claims.
- Editable text area and safe, formatted preview; edits are used in each export.
- TXT, editable Word DOCX, and paginated PDF downloads.
- Optional PNG/JPEG company logo in DOCX/PDF, with upload validation and preview.
- Modular FastAPI / Streamlit architecture, input validation, friendly errors, `.env` secret handling, and pytest coverage.

## Architecture

```text
Offline mode: Streamlit -> local template function -> editable draft -> TXT / DOCX / PDF exports

Optional AI mode: Streamlit -> HTTP POST /generate -> FastAPI -> Gemini API -> editable draft
```

Offline mode calls no external API and does not require FastAPI or `.env`. Gemini mode is optional; it uses FastAPI and reads `GEMINI_API_KEY` from the project-root `.env` file. Google Fonts imports and Streamlit usage telemetry are disabled to avoid those external requests in offline mode.

## Technology

Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Streamlit, Google Gen AI Python SDK (`google-genai`), python-docx, fpdf2, Pillow, requests, python-dotenv, and pytest.

## Folder structure

```text
LegalEase/
├── .streamlit/config.toml       # Disables Streamlit usage-stat collection
├── .vscode/launch.json          # Optional two-service VS Code debug launch
├── ai_core/gemini_generator.py  # Gemini client and drafting prompt
├── assets/                      # Project identity assets
├── backend/                     # FastAPI app, API route, Pydantic models
├── document_utils/              # Offline drafts, sanitization, preview, TXT/DOCX/PDF
├── frontend/                    # Streamlit app and preview component
├── tests/                       # API, text, and export tests
├── .dockerignore                # Keeps local secrets out of Docker builds
├── .env.example                 # Safe environment template (no key)
├── .gitignore                   # Ignores .env and Python environments
├── Dockerfile                   # FastAPI backend container
├── requirements.txt
├── run.py                       # Prints local startup commands
└── README.md
```

## Prerequisites

- Python 3.10 or newer (Python 3.11/3.12 recommended).
- VS Code with the Python extension.
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) only if using optional Gemini AI mode.
- Internet access is needed to install packages initially, but not to generate drafts with Offline template mode after setup.

## Install in Windows VS Code

1. Extract/open the `LegalEase` folder in VS Code: **File → Open Folder…**.
2. Open a VS Code terminal (**Terminal → New Terminal**) and make sure its current directory is the project root (the folder containing `requirements.txt`).
3. Create a virtual environment. Activation is optional; the commands below invoke its Python directly.

### PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

No PowerShell execution-policy change is needed.

### Command Prompt (cmd.exe)

```bat
py -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Optional: configure Gemini AI mode

Offline template mode needs no `.env` file or API key. To enable optional Gemini AI mode, first create the root-level **`.env`** file (`Copy-Item .env.example .env` in PowerShell), then enter your key on the `GEMINI_API_KEY` line:

```dotenv
GEMINI_API_KEY=put_your_google_ai_studio_key_here
GEMINI_MODEL=gemini-3.8-flash
BACKEND_URL=http://127.0.0.1:8000
```

The `.env` file is ignored by Git. Never paste a real key into source code, screenshots, Git commits, or this README. The configured model name can be changed to another model enabled for your Google account. The default shown here is the current stable Flash model at project creation; model access may vary by region/account. The supported model catalog is maintained in [Google's Gemini API model documentation](https://ai.google.dev/gemini-api/docs/models).

## Run locally without an API (default)

From the project root, start Streamlit. Offline mode does not need `.env`, a Gemini key, a backend process, or runtime internet access:

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

In the app, keep **Offline template (no API)** selected. Enter parties and terms, click **Generate document**, then complete placeholders and review the result. This local template uses only supplied information; it does not generate legal clauses or legal advice.

## Optional: run with Gemini AI (two terminals)

Set `GEMINI_API_KEY` in the project-root `.env` first. Keep both processes running in separate terminals.

**Terminal 1 — FastAPI:**

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
```

**Terminal 2 — Streamlit:**

```powershell
.\.venv\Scripts\python.exe -m streamlit run frontend/app.py
```

Open the URL printed by Streamlit (usually <http://localhost:8501>) and select **Gemini AI (API key required)**. API documentation is at <http://127.0.0.1:8000/docs>; API status is <http://127.0.0.1:8000/health>.

`python run.py` prints the one-terminal offline command and the optional Gemini backend command.

## API endpoints

- `GET /` — `{"message":"LegalEase API is running"}`
- `GET /health` — `{"status":"healthy"}`
- `POST /generate` — accepts a JSON `DocumentRequest` and returns `{ "success": true, "document_type": "...", "content": "..." }`.

Example request:

```json
{
  "document_type": "Freelance Contract",
  "parties": "Jane Doe (Service Provider); TechNova Inc. (Client)",
  "terms": "Payment within 30 days; Provider will deliver the project by the agreed deadline; Confidentiality must be maintained; Either party may terminate with 15 days notice.",
  "effective_date": "2026-10-01",
  "additional_details": "Use plain, professional language."
}
```

Required values must be nonblank, the date must be an ISO date (`YYYY-MM-DD`), unsupported document types are rejected, and custom-document requests require a description in `additional_details`. Generation errors return a readable HTTP error rather than an application traceback.

## Use the app and download a document

1. Select a document type. For **Custom Legal Document**, describe it in the additional custom-description field.
2. Enter party names and roles, the effective date, terms, and optional details. Only provide facts that should appear in the draft.
3. Optionally upload a PNG/JPEG logo (maximum 2 MB).
4. Select **Generate document**. Offline mode formats your supplied inputs locally; Gemini mode waits for the backend response.
5. Review the preview and edit the generated text in **Edit document**. All three downloads use the edited text.
6. Download TXT, DOCX, or PDF. DOCX remains editable in Microsoft Word.

The application does not store drafts in a database. The draft stays in the current Streamlit session; users should handle sensitive legal or personal data cautiously.

## Tests

No Gemini key or live Gemini request is needed for automated tests; API generation is mocked. Offline mode is deterministic local template formatting.

```powershell
pytest -q
```

The tests cover API status endpoints and request validation, safe text/HTML handling, TXT encoding, DOCX structure/term bullets, and PDF output. Run syntax validation with:

```powershell
python -m compileall backend ai_core frontend document_utils tests
```

## Docker (optional backend only)

The provided Dockerfile runs FastAPI. The Streamlit UI can run in VS Code as above. For local Docker testing, set the key in your shell/environment (do not bake it into the image), then:

```powershell
docker build -t legalease-api .
docker run --rm -p 8000:8000 --env-file .env legalease-api
```

## Troubleshooting

- **Backend connection refused:** Start `uvicorn backend.main:app --reload` and verify `BACKEND_URL` in `.env`.
- **Want to generate without an API key:** Select **Offline template (no API)**. It uses only supplied information and does not require Uvicorn.
- **Missing API key in Gemini mode:** Copy `.env.example` to `.env`, set `GEMINI_API_KEY`, and restart Uvicorn. The key belongs in the project-root `.env`, not the Streamlit code.
- **Invalid key/model, quota, or network error:** Recheck the Google AI Studio key, your account's model access, the `GEMINI_MODEL` value, network, and Google AI API quota.
- **Module not found:** Install with `.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt` from the project root, then run the app through that same `.venv` Python.
- **DOCX/PDF export error:** Try without the optional logo, confirm the draft is not empty, and verify all dependencies are installed.
- **Port already in use:** Stop the other process or use a different Uvicorn port and update `BACKEND_URL` to match.

## Security and legal notes

- `.env` is ignored by Git; `.env.example` contains blank credentials only.
- API keys remain backend-side; exception details and user documents are not logged by the app.
- User text is validated, normalized for exports, and HTML-escaped before preview. It is never executed as code.
- LegalEase is a drafting aid, not a lawyer. Generated clauses may be wrong, incomplete, or unsuitable for a jurisdiction. Have a qualified legal professional review before signing or relying on any document.

## Future enhancements

Possible extensions include jurisdiction-aware clause libraries reviewed by counsel, user authentication, encrypted document storage, version history, richer template-specific forms, and an audit trail with explicit retention controls.
