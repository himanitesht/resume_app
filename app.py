import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import PyPDF2

# ---------------------------
# 1️⃣ Load environment variables
# ---------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ---------------------------
# 2️⃣ Streamlit Page Setup
# ---------------------------
st.set_page_config(page_title="Resume Analyzer", page_icon="🤖", layout="wide")

# ✅ Limit page width to ~80% and center
st.markdown("""
    <style>
        .block-container {
            max-width: 80%;
            margin: 10px auto;
            padding-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    "<h2 style='text-align: center;'>🤖 Resume Analyzer & Interview Assistant</h2>",
    unsafe_allow_html=True
)

# ---------------------------
# 🌟 Toast Notification Helper
# ---------------------------
def show_toast(message, type="success"):
    colors = {"success": "#4CAF50", "error": "#f44336"}
    color = colors.get(type, "#4CAF50")
    toast_html = f"""
    <div style="
        position: fixed;
        top: 60px;
        right: 20px;
        background-color: {color};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.2);
        z-index: 9999;
        font-size: 16px;
        font-weight: 500;
        animation: fadeout 5s forwards;
    ">{message}</div>
    <style>
        @keyframes fadeout {{
            0% {{opacity: 1;}}
            85% {{opacity: 1;}}
            100% {{opacity: 0; display: none;}}
        }}
    </style>
    """
    st.markdown(toast_html, unsafe_allow_html=True)

# ---------------------------
# 3️⃣ Resume Upload
# ---------------------------
st.subheader("📄 Upload Your Resume")
uploaded_file = st.file_uploader("Choose your resume (PDF only):", type=["pdf"])

resume_text = ""
if uploaded_file is not None:
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    for page in pdf_reader.pages:
        resume_text += page.extract_text()
    show_toast("✅ Resume uploaded and text extracted successfully!", "success")

# ---------------------------
# 4️⃣ Initialize Session State
# ---------------------------
if "output_title" not in st.session_state:
    st.session_state["output_title"] = ""
if "output_text" not in st.session_state:
    st.session_state["output_text"] = ""

# ---------------------------
# 5️⃣ Gemini Helper
# ---------------------------
def generate_with_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        show_toast(f"❌ Gemini API Error: {e}", "error")
        return None

# ---------------------------
# 6️⃣ Action Buttons (Multi-Row Layout)
# ---------------------------
st.subheader("🧠 Choose an Action")

# Row 1
row1 = st.columns(6)
with row1[0]: summary_btn = st.button("📑 Generate Summary")
with row1[1]: questions_btn = st.button("💬 Interview Q&A")
with row1[2]: links_btn = st.button("🌐 Study Links")
with row1[3]: cover_btn = st.button("✉️ Cover Letter")
with row1[4]: improve_btn = st.button("🚀 Resume Tips")
with row1[5]: ats_btn = st.button("📊 ATS Score")

# Row 2
row2 = st.columns(5)
with row2[0]: career_btn = st.button("🎯 Career Role Match")
with row2[1]: gap_btn = st.button("🧩 Skill Gap Analysis")
with row2[2]: linkedin_btn = st.button("💼 LinkedIn Summary")
with row2[3]: project_btn = st.button("🧱 Extract Projects")
with row2[4]: email_btn = st.button("📧 Application Email")

st.divider()
st.subheader("🧾 Output")
output_container = st.empty()

# ---------------------------
# 7️⃣ Dynamic Output Renderer
# ---------------------------
def show_output(title, text):
    with output_container.container():
        st.markdown(f"### 📘 {title}")
        st.write(text)
        st.download_button(
            label="⬇️ Download",
            data=text,
            file_name=f"{title.lower().replace(' ', '_')}.txt",
            mime="text/plain"
        )

# ---------------------------
# 8️⃣ Core Button Logic
# ---------------------------
def handle_action(prompt, title, success_msg):
    st.session_state["output_text"] = ""
    output_container.empty()
    if not resume_text:
        show_toast("⚠️ Please upload a resume first.", "error")
        return
    with st.spinner(f"Generating {title.lower()}..."):
        output = generate_with_gemini(prompt)
    if output:
        show_output(title, output)
        show_toast(success_msg, "success")

# --- Summary ---
if summary_btn:
    handle_action(f"""
    You are an expert resume analyzer.
    Review the following resume and create a concise professional summary (7–9 bullet points or short paragraph).
    Resume:
    {resume_text}
    """, "Resume Summary", "✅ Summary generated successfully!")

# --- Interview Q&A ---
elif questions_btn:
    st.session_state["output_text"] = ""
    output_container.empty()
    if not resume_text:
        show_toast("⚠️ Please upload a resume first.", "error")
    else:
        with st.spinner("Generating interview Q&A..."):
            prompt = f"""
            You are a technical interviewer.
            Based on the resume, create 10-15 realistic interview questions with short model answers.
            Format:
            Question: <text>
            Answer: <text>
            Resume:
            {resume_text}
            """
            output = generate_with_gemini(prompt)
        if output:
            formatted = output.replace("Answer:", "\n**Answer:**")
            formatted = formatted.replace("Question:", "Question:")
            qna_blocks = formatted.strip().split("Question:")
            formatted_with_lines = ""
            for block in qna_blocks:
                if block.strip():
                    formatted_with_lines += "Question:" + block.strip() + "\n\n---\n"
            show_output("Interview Questions & Answers", formatted_with_lines)

# --- Study Links ---
elif links_btn:
    handle_action(f"""
    You are a career mentor.
    Based on the resume, list 8–10 online study resources (with working URLs)
    for improving the top technical skills mentioned.
    Resume:
    {resume_text}
    """, "Suggested Study Links", "✅ Study links generated successfully!")

# --- Cover Letter ---
elif cover_btn:
    handle_action(f"""
    You are a professional career consultant.
    Based on the resume, write a formal cover letter for a general job application.
    Keep it concise and tailored.
    Resume:
    {resume_text}
    """, "Cover Letter", "✅ Cover letter generated successfully!")

# --- Resume Improvement Tips ---
elif improve_btn:
    handle_action(f"""
    You are an experienced HR expert.
    Review the resume and provide improvement suggestions (skills, formatting, wording, missing metrics).
    Resume:
    {resume_text}
    """, "Resume Improvement Tips", "✅ Improvement tips generated successfully!")

# --- Career Role Match ---
elif career_btn:
    handle_action(f"""
    You are a career advisor.
    Suggest 5–7 ideal job roles that match this candidate’s resume.
    Give 1-line justification for each.
    Resume:
    {resume_text}
    """, "Career Role Suggestions", "✅ Career roles generated successfully!")

# --- Skill Gap Analysis ---
elif gap_btn:
    handle_action(f"""
    You are a technical recruiter.
    Identify missing or weak skills and recommend new ones to learn
    for improving job readiness.
    Resume:
    {resume_text}
    """, "Skill Gap Analysis", "✅ Skill gap analysis generated!")

# --- LinkedIn Summary ---
elif linkedin_btn:
    handle_action(f"""
    You are a branding coach.
    Write a 5–6 line first-person LinkedIn 'About' section from this resume.
    Resume:
    {resume_text}
    """, "LinkedIn Profile Summary", "✅ LinkedIn summary generated!")

# --- Extract Projects ---
elif project_btn:
    handle_action(f"""
    You are a resume content parser.
    Extract and summarize all projects or achievements in 2–3 bullet points each.
    Resume:
    {resume_text}
    """, "Project Highlights", "✅ Projects extracted successfully!")

# --- ATS Score ---
elif ats_btn:
    handle_action(f"""
    You are an ATS (Applicant Tracking System) evaluator.
    Analyze this resume and score it (0–100) based on:
    - Keyword relevance
    - Formatting simplicity
    - Measurable impact
    - Readability
    Provide actionable optimization tips.
    Resume:
    {resume_text}
    """, "ATS Compatibility Report", "✅ ATS report generated!")

# --- Application Email ---
elif email_btn:
    handle_action(f"""
    You are a professional recruiter.
    Write a short, polite email to send with this resume while applying for a job.
    Resume:
    {resume_text}
    """, "Application Email Template", "✅ Email generated successfully!")

# ---------------------------
# 9️⃣ Footer
# ---------------------------
st.markdown("---")
st.caption("🚀 Built by Hima Nitesh Telaprolu")
st.caption("⚠️ Disclaimer: None of your data is stored or shared. © 2025 Hima Nitesh Telaprolu")
