# Debate Feedback Tool

This Streamlit app allows instructors and students to upload debate files (.pdf or .docx), extract text, and receive AI-generated constructive feedback in bullet-point form.

## Features
- Upload PDF or DOCX files
- Text extraction and argument analysis via GPT-4
- Feedback is limited to 250 words in bullet format
- Feedback viewable in the app and downloadable as PDF
- Progress indicators at each step

## Setup

```bash
pip install -r requirements.txt
```

Add your OpenAI API key to your environment:

```bash
export OPENAI_API_KEY='your-key-here'
```

## Run

```bash
streamlit run debate_feedback_tool.py
```

---
