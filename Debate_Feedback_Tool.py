import streamlit as st
import fitz  # PyMuPDF for PDFs
from docx import Document
import tempfile
from openai import OpenAI
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
import os

# Set up OpenAI client
client = OpenAI()

st.set_page_config(page_title="Debate Feedback Tool", layout="centered")
st.title("🗣️ Debate Feedback Tool")
st.markdown("Upload a debate file and receive concise, actionable AI-generated feedback.")

# Helper: extract text from PDF
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# Helper: extract text from DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip() != ""]).strip()

# Helper: analyze argument text
def analyze_argument(text):
    with st.spinner("Analyzing arguments..."):
        prompt = f"""
You are an expert debate coach. Provide constructive, critical feedback in bullet points (max 250 words total) for the following student debate text. Focus on rebuttable claims, weak arguments, and areas for improvement:

{text[:3000]}
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=350,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()

# Helper: create downloadable PDF
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

# File uploader
uploaded_file = st.file_uploader("Upload a debate file (.pdf or .docx)", type=["pdf", "docx"])

if uploaded_file:
    with st.status("📤 Uploading and extracting text...", expanded=False) as status:
        if uploaded_file.name.endswith(".pdf"):
            extracted_text = extract_text_from_pdf(uploaded_file)
        else:
            extracted_text = extract_text_from_docx(uploaded_file)

        if not extracted_text:
            st.error("❌ Could not extract text. Please check the file.")
        else:
            status.update(label="✅ Text extracted!", state="complete")

    if extracted_text:
        feedback = analyze_argument(extracted_text)
        st.subheader("📋 AI Feedback")
        st.markdown(feedback)

        # Generate PDF
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
