import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai
from dotenv import load_dotenv
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO

# ---------------------------
# Load Environment
# ---------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="AI Resume Studio", layout="wide")
st.title("AI Resume Studio (Gemini Powered)")
st.markdown("Upgrade your resume. Beat ATS. Stand out from the crowd.")

uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])
job_role = st.text_input("Enter Target Job Role")

# ---------------------------
# PDF Reader
# ---------------------------
def read_pdf(uploaded_file):
    text_content = ""
    reader = PdfReader(uploaded_file)
    for page in reader.pages:
        text_content += page.extract_text()
    return text_content

# ---------------------------
# PDF Creator (Professional Formatting)
# ---------------------------
def create_pdf(text):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()

    heading_style = ParagraphStyle(
        name="HeadingStyle",
        parent=styles["Normal"],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=10
    )

    normal_style = styles["Normal"]

    for line in text.split("\n"):
        if line.strip().isupper():
            elements.append(Paragraph(f"<b>{line}</b>", heading_style))
        else:
            elements.append(Paragraph(line, normal_style))
        elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ---------------------------
# Main Logic
# ---------------------------
if uploaded_file and job_role:

    resume_text = read_pdf(uploaded_file)

    st.subheader(" Original Resume")
    st.text_area("Original Content", resume_text, height=250)

    if st.button(" Optimize Resume"):

        prompt = f"""
        
Do not add this line - Here's a rewritten resume optimized for a Java Software Role, focusing on ATS performance, quantified achievements, and professional presentation.
You are a senior technical recruiter and ATS optimization expert.

JOB ROLE:
{job_role}

RESUME CONTENT:
{resume_text}

INSTRUCTIONS:
- Rewrite the resume to match the job role perfectly.
- Ensure ATS score above 90.
- Add quantified achievements (%, numbers, impact).
- Use strong action verbs.
- Improve project descriptions using STAR method.
- Highlight relevant skills and keywords.
- Make it clean, structured and professional.

FORMAT:

NAME
CONTACT INFORMATION

PROFESSIONAL SUMMARY (Powerful 4-5 lines)

CORE SKILLS (Bullet Points)

TECHNICAL SKILLS

PROJECTS
- Project Name
  • Problem
  • Solution
  • Technologies
  • Impact (with metrics)

EXPERIENCE

EDUCATION

CERTIFICATIONS
"""

        with st.spinner("Optimizing Resume..."):
            response = model.generate_content(prompt)
            optimized_text = response.text

        st.subheader("Optimized Resume")
        st.text_area("Final Resume", optimized_text, height=400)

        # ---------------------------
        # Resume Analysis Section
        # ---------------------------
        analysis_prompt = f"""
Analyze the resume below:

1. Estimate ATS score (out of 100).
2. List top 5 strongest highlights.
3. Mention 3 improvement suggestions.
4. Identify missing keywords for {job_role}.

Resume:
{optimized_text}
"""

        analysis = model.generate_content(analysis_prompt)

        st.subheader(" Resume Analysis & ATS Report")
        st.write(analysis.text)

        # ---------------------------
        # PDF Download
        # ---------------------------
        pdf_file = create_pdf(optimized_text)

        st.download_button(
            label="📥 Download Optimized Resume (PDF)",
            data=pdf_file,
            file_name="Optimized_Resume.pdf",
            mime="application/pdf"
        )

        st.success("Resume Optimization Complete!")
