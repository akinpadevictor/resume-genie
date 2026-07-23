import os
import tempfile
import html

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(
    page_title="Resume Genie | AI Career Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%); }
.block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 4rem; }
#MainMenu, footer { visibility: hidden; }
section[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%); }
section[data-testid="stSidebar"] * { color: white !important; }
.hero { background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%); padding: 3rem 2rem; border-radius: 24px; text-align: center; margin-bottom: 2rem; color: white; }
.hero-badge { display: inline-block; background: rgba(255,255,255,0.2); padding: 0.4rem 1rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem; }
.hero-title { font-size: 2.8rem; font-weight: 800; margin: 0.5rem 0; }
.hero-description { font-size: 1.1rem; opacity: 0.9; max-width: 700px; margin: 0 auto; }
.service-card { background: white; padding: 1.5rem 2rem; border-radius: 20px; border: 1px solid #e5e7eb; box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06); margin-bottom: 1.5rem; }
.service-icon { font-size: 2rem; } .service-title { font-size: 1.6rem; font-weight: 750; color: #111827; } .service-description { color: #64748b; }
.section-title { font-size: 1.15rem; font-weight: 750; color: #111827; margin-top: 1.5rem; margin-bottom: 0.7rem; }
.result-header { background: linear-gradient(135deg, #ecfdf5, #eff6ff); border: 1px solid #dbeafe; padding: 1.5rem 2rem; border-radius: 20px; margin-top: 2rem; }
.info-card { background: white; border: 1px solid #e5e7eb; border-radius: 18px; padding: 1.5rem; }
.footer { text-align: center; color: #64748b; padding: 3rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)

# API KEY
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if not GOOGLE_API_KEY:
    st.error("Google API key is not configured. Please add GOOGLE_API_KEY to your Streamlit secrets.")
    st.stop()

@st.cache_resource
def load_model():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",  # FIX 1: correct model name
        google_api_key=GOOGLE_API_KEY,    # FIX 2: use the global var directly
        temperature=0.2,
        convert_system_message_to_human=True # helps with long prompts
    )
chat = load_model() # FIX 3: no argument needed now

@st.cache_data(show_spinner=False)
def extract_resume(file_bytes):
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        documents = PyPDFLoader(temp_path).load()
        resume_text = "\n\n".join(document.page_content for document in documents)
        if not resume_text.strip():
            raise ValueError("No readable text was found in the uploaded PDF.")
        return resume_text
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

# PROMPTS
DETAILED_MATCH_PROMPT = """You are an expert ATS Resume Reviewer...\nResume:\n{resume}\nJob Description:\n{job_description}\nReturn Markdown..."""
QUICK_MATCH_PROMPT = """You are an expert ATS Resume Reviewer...\nResume:\n{resume}\nJob Description:\n{job_description}\nReturn Markdown..."""
COVER_LETTER_PROMPT = """You are an expert HR Recruiter...\nCandidate Resume:\n{resume}\nJob Description:\n{job_description}\nWrite cover letter..."""
ATS_EVALUATION_PROMPT = """You are an expert ATS Resume Reviewer...\nResume:\n{resume}\nEvaluate..."""
CAREER_COACH_PROMPT = """You are an expert Career Coach...\nCandidate Resume:\n{resume}\nCandidate Question:\n{question}\nAnswer..."""

SERVICES = {
    "Resume Match": {"icon": "🎯", "description": "Compare your resume to a job description", "prompt": QUICK_MATCH_PROMPT, "needs_job_description": True, "button": "🚀 Analyze Resume Match", "spinner": "Comparing...", "download_name": "Resume_Match_Report.md", "download_label": "📥 Download Match Report", "mime": "text/markdown"},
    "Cover Letter": {"icon": "✉️", "description": "Create a tailored cover letter", "prompt": COVER_LETTER_PROMPT, "needs_job_description": True, "button": "🚀 Generate Cover Letter", "spinner": "Generating...", "download_name": "Cover_Letter.txt", "download_label": "📥 Download Cover Letter", "mime": "text/plain"},
    "ATS Evaluation": {"icon": "📊", "description": "Review your resume's ATS readiness", "prompt": ATS_EVALUATION_PROMPT, "needs_job_description": False, "button": "🚀 Evaluate Resume", "spinner": "Evaluating...", "download_name": "ATS_Evaluation.md", "download_label": "📥 Download ATS Evaluation", "mime": "text/markdown"},
    "Resume Scorer": {"icon": "⭐", "description": "Generate a detailed scoring report", "prompt": DETAILED_MATCH_PROMPT, "needs_job_description": True, "button": "🚀 Score Resume", "spinner": "Scoring...", "download_name": "Resume_Score_Report.md", "download_label": "📥 Download Score Report", "mime": "text/markdown"},
    "Career Coach": {"icon": "🧑‍💼", "description": "Ask career questions based on your resume", "prompt": CAREER_COACH_PROMPT, "needs_job_description": False, "needs_question": True, "button": "🚀 Ask Career Coach", "spinner": "Preparing advice...", "download_name": "Career_Coach_Advice.md", "download_label": "📥 Download Advice", "mime": "text/markdown"},
}

if "selected_service" not in st.session_state:
    st.session_state.selected_service = "Resume Match"
if "result" not in st.session_state:
    st.session_state.result = None

# SIDEBAR
with st.sidebar:
    st.markdown('<div style="text-align:center"><div style="font-size:3rem">📄</div><div style="font-size:1.5rem;font-weight:800">Resume Genie</div></div>', unsafe_allow_html=True)
    st.divider()
    for service_name, service_data in SERVICES.items():
        if st.button(f"{service_data['icon']}  {service_name}", key=f"service_{service_name}", use_container_width=True):
            st.session_state.selected_service = service_name
            st.session_state.result = None
            st.rerun()

service_name = st.session_state.selected_service
service = SERVICES[service_name]

# HERO + SERVICE CARD
st.markdown('<div class="hero"><div class="hero-badge">✨ AI-Powered Career Intelligence</div><div class="hero-title">📄 Resume Genie</div><p class="hero-description">Transform your resume into a powerful career tool.</p></div>', unsafe_allow_html=True)
st.markdown(f'<div class="service-card"><div class="service-icon">{html.escape(service["icon"])}</div><div class="service-title">{html.escape(service_name)}</div><p class="service-description">{html.escape(service["description"])}</p></div>', unsafe_allow_html=True)

# STEP 1 UPLOAD
st.markdown('<div class="section-title">📎 Step 1 — Upload Your Resume</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

# STEP 2
job_description = ""
question = ""
if service.get("needs_job_description"):
    st.markdown('<div class="section-title">💼 Step 2 — Add the Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area("Paste Job Description", height=280)

if service.get("needs_question"):
    st.markdown('<div class="section-title">💬 Step 2 — Ask Your Career Question</div>', unsafe_allow_html=True)
    question = st.text_area("What would you like help with?", height=140)

# STEP 3 BUTTON
st.markdown('<div class="section-title">⚡ Step 3 — Generate Your AI Report</div>', unsafe_allow_html=True)
if st.button(service["button"], type="primary", use_container_width=True):
    if uploaded_file is None:
        st.warning("📎 Please upload your resume as a PDF.")
        st.stop()
    if service.get("needs_job_description") and not job_description.strip():
        st.warning("💼 Please paste the job description.")
        st.stop()
    if service.get("needs_question") and not question.strip():
        st.warning("💬 Please enter a question.")
        st.stop()

    try:
        with st.spinner(service["spinner"]):
            resume_text = extract_resume(uploaded_file.getvalue())
            prompt = service["prompt"].format(resume=resume_text, job_description=job_description, question=question)
            response = chat.invoke(prompt)
            st.session_state.result = {"service": service_name, "content": response.content}
        st.success(f"✅ {service_name} completed successfully!")
    except Exception as error:
        st.error("❌ The service could not complete.")
        st.exception(error)

# RESULT
result = st.session_state.result
if result and result["service"] == service_name:
    st.markdown(f'<div class="result-header"><div style="font-size:1.5rem;font-weight:750">📊 {html.escape(service_name)} Result</div></div>', unsafe_allow_html=True)
    st.markdown(result["content"])
    st.download_button(label=service["download_label"], data=result["content"], file_name=service["download_name"], mime=service["mime"], use_container_width=True)

# HOW IT WORKS
if not result:
    st.divider()
    st.markdown('<div style="text-align:center;font-size:2rem;font-weight:800">🚀 How Resume Genie Works</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown('<div class="info-card"><div style="font-size:2rem">📎</div><b>1. Upload</b><p>Upload your resume as PDF.</p></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="info-card"><div style="font-size:2rem">🤖</div><b>2. Let AI Analyze</b><p>AI analyzes vs job or question.</p></div>', unsafe_allow_html=True)
    with c3: st.markdown('<div class="info-card"><div style="font-size:2rem">🎯</div><b>3. Get Insights</b><p>Receive actionable recommendations.</p></div>', unsafe_allow_html=True)

st.markdown('<div class="footer"><p>📄 <strong>Resume Genie</strong> — Built with Streamlit + Google Gemini AI</p></div>', unsafe_allow_html=True)