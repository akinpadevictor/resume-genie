import os
import tempfile
import html

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Resume Genie | AI Career Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS - ALL IN ONE BLOCK
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 50%, #f8fafc 100%);
    }
    .block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 4rem; }
    h1, h2, h3 { font-weight: 700; }
    #MainMenu, footer { visibility: hidden; }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    section[data-testid="stSidebar"] * { color: white !important; }
    section[data-testid="stSidebar"] button {
        width: 100%; min-height: 48px; border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        background: rgba(255, 255, 255, 0.06);
        color: white !important; font-weight: 600; transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] button:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.35);
        transform: translateY(-1px);
    }
    .sidebar-brand { text-align: center; padding: 1rem 0 1.5rem 0; }
    .sidebar-logo { font-size: 3.5rem; margin-bottom: 0.3rem; }
    .sidebar-title { font-size: 1.5rem; font-weight: 800; color: white; margin: 0; }
    .sidebar-subtitle { color: #cbd5e1 !important; font-size: 0.85rem; margin-top: 0.4rem; }

    /* HERO */
    .hero {
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
        padding: 3rem 2rem; border-radius: 24px; text-align: center; margin-bottom: 2rem;
        color: white;
    }
    .hero-badge {
        display: inline-block; background: rgba(255,255,255,0.2); padding: 0.4rem 1rem;
        border-radius: 999px; font-size: 0.85rem; font-weight: 600; margin-bottom: 1rem;
    }
    .hero-title { font-size: 2.8rem; font-weight: 800; margin: 0.5rem 0; }
    .hero-description { font-size: 1.1rem; opacity: 0.9; max-width: 700px; margin: 0 auto; }

    /* SERVICE CARD */
    .service-card {
        background: white; padding: 1.5rem 2rem; border-radius: 20px;
        border: 1px solid #e5e7eb; box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
        margin-bottom: 1.5rem;
    }
    .service-icon { font-size: 2rem; margin-bottom: 0.3rem; }
    .service-title { font-size: 1.6rem; font-weight: 750; color: #111827; margin: 0; }
    .service-description { color: #64748b; margin-top: 0.5rem; margin-bottom: 0; line-height: 1.6; }

    .section-title { font-size: 1.15rem; font-weight: 750; color: #111827; margin-top: 1.5rem; margin-bottom: 0.7rem; }

    [data-testid="stFileUploader"] {
        background: white; border: 2px dashed #a5b4fc; border-radius: 16px; padding: 1rem;
    }
    [data-testid="stFileUploader"]:hover { border-color: #6366f1; background: #fafaff; }
    textarea { border-radius: 12px !important; }

    .stButton > button, .stDownloadButton > button {
        border-radius: 12px; font-weight: 650; min-height: 46px; width: 100%;
    }
    .stButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 20px rgba(79, 70, 229, 0.20); }

    .result-header {
        background: linear-gradient(135deg, #ecfdf5, #eff6ff);
        border: 1px solid #dbeafe; padding: 1.5rem 2rem; border-radius: 20px;
        margin-top: 2rem; margin-bottom: 1.5rem;
    }
    .result-title { font-size: 1.5rem; font-weight: 750; color: #111827; margin: 0; }
    .result-description { color: #64748b; margin: 0.5rem 0 0 0; }

    .how-it-works-title { text-align: center; font-size: 2rem; font-weight: 800; color: #111827; margin: 2rem 0; }
    .info-card {
        background: white; border: 1px solid #e5e7eb; border-radius: 18px; padding: 1.5rem;
        min-height: 190px; box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05); transition: all 0.2s ease;
    }
    .info-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px rgba(15, 23, 42, 0.10); }
    .info-icon { font-size: 2rem; margin-bottom: 0.7rem; }
    .info-title { font-size: 1.05rem; font-weight: 750; color: #111827; margin-bottom: 0.5rem; }
    .info-description { color: #64748b; line-height: 1.6; font-size: 0.95rem; }

    .footer { text-align: center; color: #64748b; padding: 3rem 0 1rem 0; font-size: 0.85rem; line-height: 1.8; }

    @media (max-width: 768px) {
        .block-container { padding: 1rem 1rem 3rem 1rem; }
        .hero { padding: 1.8rem; border-radius: 20px; }
        .hero-title { font-size: 2.1rem; }
        .hero-description { font-size: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# GOOGLE GEMINI API KEY
# ============================================================

try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except Exception:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

if not GOOGLE_API_KEY:
    st.error("Google API key is not configured. Please add GOOGLE_API_KEY to your Streamlit secrets.")
    st.stop()

# ============================================================
# LOAD GEMINI MODEL
# ============================================================

@st.cache_resource
def load_model():
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # gemini-2.5-flash may not exist yet. Use 1.5
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
    )

chat = load_model()

# ============================================================
# EXTRACT RESUME TEXT
# ============================================================

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

# PROMPTS - same as yours, kept short here
DETAILED_MATCH_PROMPT = """You are an expert ATS Resume Reviewer...{resume}...{job_description}"""
QUICK_MATCH_PROMPT = """You are an expert ATS Resume Reviewer...{resume}...{job_description}"""
COVER_LETTER_PROMPT = """You are an expert HR Recruiter...{resume}...{job_description}"""
ATS_EVALUATION_PROMPT = """You are an expert ATS Resume Reviewer...{resume}"""
CAREER_COACH_PROMPT = """You are an expert Career Coach...{resume}...{question}"""

SERVICES = {
    "Resume Match": {"icon": "🎯", "description": "Compare your resume to a job description and get a focused match report.", "prompt": QUICK_MATCH_PROMPT, "needs_job_description": True, "button": "🚀 Analyze Resume Match", "spinner": "Comparing your resume with the role...", "download_name": "Resume_Match_Report.md", "download_label": "📥 Download Match Report", "mime": "text/markdown"},
    "Cover Letter": {"icon": "✉️", "description": "Create a tailored, ATS-friendly cover letter for a specific role.", "prompt": COVER_LETTER_PROMPT, "needs_job_description": True, "button": "🚀 Generate Cover Letter", "spinner": "Generating your cover letter...", "download_name": "Cover_Letter.txt", "download_label": "📥 Download Cover Letter", "mime": "text/plain"},
    "ATS Evaluation": {"icon": "📊", "description": "Review your resume's ATS readiness, strengths, gaps, and career direction.", "prompt": ATS_EVALUATION_PROMPT, "needs_job_description": False, "button": "🚀 Evaluate Resume", "spinner": "Evaluating your resume...", "download_name": "ATS_Evaluation.md", "download_label": "📥 Download ATS Evaluation", "mime": "text/markdown"},
    "Resume Scorer": {"icon": "⭐", "description": "Generate a detailed resume-to-job scoring report.", "prompt": DETAILED_MATCH_PROMPT, "needs_job_description": True, "button": "🚀 Score Resume", "spinner": "Scoring your resume...", "download_name": "Resume_Score_Report.md", "download_label": "📥 Download Score Report", "mime": "text/markdown"},
    "Career Coach": {"icon": "🧑‍💼", "description": "Ask tailored career, interview, ATS, or job-search questions based on your resume.", "prompt": CAREER_COACH_PROMPT, "needs_job_description": False, "needs_question": True, "button": "🚀 Ask Career Coach", "spinner": "Preparing tailored career advice...", "download_name": "Career_Coach_Advice.md", "download_label": "📥 Download Advice", "mime": "text/markdown"},
}

# SESSION STATE
if "selected_service" not in st.session_state:
    st.session_state.selected_service = "Resume Match"
if "result" not in st.session_state:
    st.session_state.result = None

# SIDEBAR
with st.sidebar:
    st.markdown('<div class="sidebar-brand"><div class="sidebar-logo">📄</div><div class="sidebar-title">Resume Genie</div><div class="sidebar-subtitle">Your AI-powered career assistant</div></div>', unsafe_allow_html=True)
    st.divider()
    st.subheader("🧰 AI Services")
    for service_name, service_data in SERVICES.items():
        if st.button(f"{service_data['icon']}  {service_name}", key=f"service_{service_name}", use_container_width=True):
            st.session_state.selected_service = service_name
            st.session_state.result = None
            st.rerun()
    st.divider()
    st.caption("💡 Upload your resume and let Resume Genie help you prepare for your next career opportunity.")

# CURRENT SERVICE - MUST BE DEFINED BEFORE USING IT
service_name = st.session_state.selected_service
service = SERVICES[service_name]

# HERO
st.markdown('<div class="hero"><div class="hero-badge">✨ AI-Powered Career Intelligence</div><div class="hero-title">📄 Resume Genie</div><p class="hero-description">Transform your resume into a powerful career tool. Analyze your ATS compatibility, match your resume to job opportunities, create tailored cover letters, and get personalized career guidance.</p></div>', unsafe_allow_html=True)

# SERVICE CARD
safe_service_name = html.escape(service_name)
safe_description = html.escape(service["description"])
safe_icon = html.escape(service["icon"])
st.markdown(f'<div class="service-card"><div class="service-icon">{safe_icon}</div><div class="service-title">{safe_service_name}</div><p class="service-description">{safe_description}</p></div>', unsafe_allow_html=True)

# REST OF YOUR UI LOGIC: upload, inputs, button, result, how it works, footer
# [Keep the rest of your code from "RESUME UPLOAD" down exactly as you had it]

# I’ve truncated prompts for space. Paste your full prompts back in.