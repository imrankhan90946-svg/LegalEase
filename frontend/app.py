"""LegalEase Streamlit frontend. Run with: streamlit run frontend/app.py"""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

from document_utils.docx_generator import generate_docx
from document_utils.pdf_generator import generate_pdf
from document_utils.txt_generator import generate_txt
from frontend.ui_components import render_document_preview

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
DOCUMENT_TYPES = [
    "General Agreement", "Contract", "Non-Disclosure Agreement (NDA)",
    "Employment Contract", "Employment Offer Letter", "Freelance Contract",
    "Lease Agreement", "Service Agreement", "Business Partnership Agreement",
    "Consulting Agreement", "Custom Legal Document",
]
DISCLAIMER = (
    "LegalEase generates AI-assisted legal documents for informational and drafting purposes. "
    "It does not provide legal advice. Users should consult a qualified legal professional "
    "for legal advice and jurisdiction-specific review."
)

st.set_page_config(page_title="LegalEase | AI Legal Document Generator", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
  .stApp { background: linear-gradient(180deg,#f5f8fb 0%,#ffffff 48%); color:#243447; }
  .block-container { max-width:1180px; padding-top:2.1rem; padding-bottom:3rem; }
  h1,h2,h3 { color:#183b56; }
  .hero { background:linear-gradient(120deg,#183b56,#245a75); color:white; padding:28px 34px;
    border-radius:18px; margin-bottom:22px; box-shadow:0 12px 30px rgba(24,59,86,.16); }
  .hero h1 { color:white; font-family:'Playfair Display',Georgia,serif; font-size:2.4rem; margin:0; }
  .hero p { color:#dce8ef; margin:.35rem 0 0; font-size:1rem; }
  .eyebrow { color:#d7b875; text-transform:uppercase; letter-spacing:.16em; font-weight:700; font-size:.74rem; margin-bottom:8px; }
  div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:14px; border-color:#e3eaf0; }
  div.stButton > button[kind="primary"] { background:#183b56; border:0; border-radius:9px; min-height:3rem; font-weight:700; }
  div.stButton > button[kind="primary"]:hover { background:#245a75; border:0; }
  .disclaimer { background:#fff8e9; border:1px solid #f1dfb7; border-left:4px solid #c39845;
    border-radius:9px; padding:13px 16px; color:#5c4d31; font-size:.9rem; }
  .muted { color:#657789; }
</style>
""", unsafe_allow_html=True)

st.image(str(ROOT / "assets" / "logo.png"), width=300)
st.markdown("""
<div class="hero">
  <div class="eyebrow">Draft with clarity</div>
  <h1>Start with a clearer draft.</h1>
  <p>AI-Powered Legal Document Generator · Turn your terms into a clear first draft.</p>
</div>
""", unsafe_allow_html=True)
st.markdown(f'<div class="disclaimer">⚠️ {DISCLAIMER}</div>', unsafe_allow_html=True)
st.write("")

left, right = st.columns([0.92, 1.08], gap="large")
with left:
    st.subheader("Document details")
    doc_type = st.selectbox("Document type", DOCUMENT_TYPES, help="Choose the closest document type. Custom documents need a short description.")
    custom_description = ""
    if doc_type == "Custom Legal Document":
        custom_description = st.text_input("Describe the document", placeholder="e.g., equipment loan agreement")
    parties = st.text_area("Parties", height=115, placeholder="Identify each party and role, for example:\nService Provider: Jane Doe\nClient: TechNova Inc.")
    effective_date = st.date_input("Effective date", value=date.today(), format="YYYY-MM-DD")
    terms = st.text_area("Terms & conditions", height=175, placeholder="Enter only the agreed terms. Separate items with semicolons or new lines.\nPayment within 30 days;\nConfidentiality must be maintained;")
    additional = st.text_area("Additional details (optional)", height=105, placeholder="Context, jurisdiction if known, specific requirements, or details to clarify.")
    uploaded_logo = st.file_uploader("Company logo (optional)", type=["png", "jpg", "jpeg"], help="PNG/JPEG, maximum 2 MB. Used in DOCX and PDF exports.")
    logo_bytes = None
    logo_error = None
    if uploaded_logo is not None:
        raw_logo = uploaded_logo.getvalue()
        if len(raw_logo) > 2 * 1024 * 1024:
            logo_error = "Logo must be 2 MB or smaller."
        else:
            try:
                logo_image = Image.open(uploaded_logo)
                logo_image.verify()
                uploaded_logo.seek(0)
                st.image(uploaded_logo, caption="Logo preview", width=150)
                logo_bytes = raw_logo
            except (UnidentifiedImageError, OSError, ValueError):
                logo_error = "This image could not be read. Please upload a valid PNG or JPEG."
        if logo_error:
            st.error(logo_error)

    generate_clicked = st.button("Generate document", type="primary", use_container_width=True, disabled=bool(logo_error))
    if generate_clicked:
        missing = []
        if not parties.strip():
            missing.append("parties")
        if not terms.strip():
            missing.append("terms and conditions")
        if doc_type == "Custom Legal Document" and not custom_description.strip():
            missing.append("custom document description")
        if missing:
            st.error("Please complete: " + ", ".join(missing) + ".")
        else:
            details = additional.strip()
            if custom_description.strip():
                details = f"Requested custom document: {custom_description.strip()}\n" + details
            payload = {
                "document_type": doc_type,
                "parties": parties.strip(),
                "terms": terms.strip(),
                "effective_date": effective_date.isoformat(),
                "additional_details": details,
            }
            with st.spinner("Drafting your document securely through the LegalEase backend…"):
                try:
                    response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=180)
                    try:
                        result = response.json()
                    except ValueError:
                        result = {}
                    if response.ok and result.get("success") and result.get("content"):
                        st.session_state["edited_document"] = result["content"]
                        st.session_state["document_type"] = doc_type
                        st.session_state["logo_bytes"] = logo_bytes
                        st.success("Your draft is ready. Review and edit it before downloading.")
                    else:
                        message = result.get("detail") or f"Backend returned HTTP {response.status_code}."
                        st.error(message)
                except requests.exceptions.ConnectionError:
                    st.error(f"Could not connect to the backend at {BACKEND_URL}. Start FastAPI in another terminal and try again.")
                except requests.exceptions.Timeout:
                    st.error("The request timed out. The model may still be processing; please retry or check the backend.")
                except requests.RequestException:
                    st.error("A network error interrupted document generation. Please check your connection and retry.")

with right:
    st.subheader("Your draft")
    if "edited_document" not in st.session_state:
        st.markdown("<div class='muted'>Your generated document will appear here. Review it carefully before use.</div>", unsafe_allow_html=True)
    else:
        edited = st.text_area("Edit document", key="edited_document", height=390, help="Changes here are used in every download format.")
        with st.expander("Formatted preview", expanded=True):
            st.markdown(render_document_preview(edited), unsafe_allow_html=True)
        document_type_for_export = st.session_state.get("document_type", doc_type)
        logo_for_export = st.session_state.get("logo_bytes")
        safe_name = "_".join(document_type_for_export.lower().replace("(", "").replace(")", "").replace("&", "and").split())
        col_txt, col_docx, col_pdf = st.columns(3)
        col_txt.download_button("Download TXT", data=generate_txt(edited), file_name=f"{safe_name}.txt", mime="text/plain; charset=utf-8", use_container_width=True)
        try:
            docx_bytes = generate_docx(edited, document_type_for_export, logo=logo_for_export)
            col_docx.download_button("Download DOCX", data=docx_bytes, file_name=f"{safe_name}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        except Exception as exc:
            col_docx.error(f"DOCX export failed: {exc}")
        try:
            pdf_bytes = generate_pdf(edited, document_type_for_export, logo=logo_for_export)
            col_pdf.download_button("Download PDF", data=pdf_bytes, file_name=f"{safe_name}.pdf", mime="application/pdf", use_container_width=True)
        except Exception as exc:
            col_pdf.error(f"PDF export failed: {exc}")

st.divider()
st.caption("Your API key stays on the backend. Avoid entering unnecessary sensitive personal information. Generated drafts are not a substitute for advice from a qualified lawyer.")
