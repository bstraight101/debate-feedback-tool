import streamlit as st
import fitz  # PyMuPDF for PDFs
from docx import Document
import tempfile
import requests
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

# Config
GROQ_API_KEY = "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"
GROQ_MODEL = "mixtral-8x7b-32768"

st.set_page_config(page_title="Debate Feedback Tool", layout="centered")
st.title("🗣️ Debate Feedback Tool")
st.markdown("Upload a debate file and receive concise, actionable AI-generated feedback.")

# Extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join(page.get_text() for page in doc).strip()

# Extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

# Analyze argument using Groq + Mixtral
def analyze_argument(text):
    st.spinner("Analyzing arguments...")
    prompt = f"""
You are a skilled debate coach. Provide constructive, critical feedback in bullet points (MAX 250 words) for the following student debate text. Focus on rebuttable claims, weak arguments, unsupported assumptions, and areas for improvement:

{text[:3500]}
"""
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
            "max_tokens": 500
        }
    )

    if response.status_code != 200:
        return f"❌ Error: {response.status_code} - {response.text}"

    result = response.json()
    return result["choices"][0]["message"]["content"].strip()

# Export feedback to PDF
def export_feedback_to_pdf(feedback_text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        c = canvas.Canvas(tmp_file.name, pagesize=LETTER)
        width, height = LETTER
        text_object = c.beginText(40, height - 50)
        text_object.setFont("Helvetica", 11)
        for line in feedback_text.split("\n"):
            text_object.textLine(line)
        c.drawText(text_object)
        c.save()
        return tmp_file.name

# Upload file
uploaded_file = st.file_uploader("Upload a debate file (.pdf or .docx)", type=["pdf", "docx"])

if uploaded_file:
    with st.status("📤 Uploading and extracting text...", expanded=False) as status:
        if uploaded_file.name.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            extracted_text = extract_text_from_docx(uploaded_file)

        if not extracted_text:
            st.error("❌ Could not extract text.")
        else:
            status.update(label="✅ Text extracted!", state="complete")

    if extracted_text:
        with st.status("🧠 Generating feedback...", expanded=False):
            feedback = analyze_argument(extracted_text)
        st.subheader("📋 AI Feedback")
        st.markdown(feedback)

        # Export as PDF
        with st.status("📄 Generating PDF...", expanded=False) as status:
            pdf_path = export_feedback_to_pdf(feedback)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Feedback as PDF",
                    data=pdf_file,
                    file_name="Debate_Feedback.pdf",
                    mime="application/pdf"
                )
            status.update(label="✅ PDF ready!", state="complete")
