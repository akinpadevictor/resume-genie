
import os
import tempfile

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
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    .stApp {
        background: linear-gradient(
            135deg,
            #f8fafc 0%,
            #eef2ff 50%,
            #f8fafc 100%
        );
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-weight: 700;
    }


    /* ========================================================
       SIDEBAR
    ======================================================== */

    section[data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #111827 0%,
            #1e293b 100%
        );
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label {
        color: white !important;
    }

    section[data-testid="stSidebar"] button {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.15);
        background-color: rgba(255,255,255,0.06);
        color: white;
        font-weight: 600;
        padding: 0.7rem;
        transition: all 0.2s ease;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: rgba(255,255,255,0.15);
        border-color: rgba(255,255,255,0.4);
        transform: translateY(-1px);
    }


    /* ========================================================
       HERO SECTION
    ======================================================== */

    .hero {
        padding: 2.5rem;
        border-radius: 24px;
        background: linear-gradient(
            135deg,
            #111827 0%,
            #312e81 50%,
            #4f46e5 100%
        );
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 15px 40px rgba(15, 23, 42, 0.18);
    }

    .hero h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        color: white;
    }

    .hero p {
        font-size: 1.15rem;
        color: #e0e7ff;
        max-width: 750px;
        line-height: 1.7;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.2);
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }


    /* ========================================================
       SERVICE HEADER
    ======================================================== */

    .service-card {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.06);
        margin-bottom: 1.5rem;
    }

    .service-card h2 {
        margin-bottom: 0.4rem;
        color: #111827;
    }

    .service-card p {
        color: #64748b;
        font-size: 1rem;
    }


    /* ========================================================
       SECTION HEADERS
    ======================================================== */

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #111827;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
    }


    /* ========================================================
       INPUT CARDS
    ======================================================== */

    .input-card {
        background: white;
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
        margin-bottom: 1rem;
    }


    /* ========================================================
       BUTTONS
    ======================================================== */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 45px;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 20px rgba(79, 70, 229, 0.2);
    }

    .stDownloadButton > button {
        border-radius: 10px;
        font-weight: 600;
    }


    /* ========================================================
       FILE UPLOADER
    ======================================================== */

    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #c7d2fe;
        border-radius: 16px;
        padding: 1rem;
    }


    /* ========================================================
       TEXT AREAS
    ======================================================== */

    textarea {
        border-radius: 12px !important;
    }


    /* ========================================================
       RESULT CARD
    ======================================================== */

    .result-header {
        background: linear-gradient(
            135deg,
            #ecfdf5,
            #eff6ff
        );
        border: 1px solid #dbeafe;
        padding: 1.5rem;
        border-radius: 18px;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    .result-header h2 {
        color: #111827;
        margin-bottom: 0.3rem;
    }


    /* ========================================================
       HOW IT WORKS
    ======================================================== */

    .info-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.3rem;
        min-height: 170px;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
    }

    .info-card h3 {
        font-size: 1.05rem;
        color: #111827;
    }

    .info-card p {
        color: #64748b;
        line-height: 1.6;
    }


    /* ========================================================
       FOOTER
    ======================================================== */

    .footer {
        text-align: center;
        color: #64748b;
        padding: 2rem 0 1rem 0;
        font-size: 0.85rem;
    }


    /* ========================================================
       MOBILE
    ======================================================== */

    @media (max-width: 768px) {

        .hero {
            padding: 1.5rem;
            border-radius: 18px;
        }

        .hero h1 {
            font-size: 2rem;
        }

        .hero p {
            font-size: 1rem;
        }

        .block-container {
            padding-top: 1rem;
        }

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

    st.error(
        "Google API key is not configured. "
        "Please add GOOGLE_API_KEY to your Streamlit secrets."
    )

    st.stop()


# ============================================================
# LOAD GEMINI MODEL
# ============================================================

@st.cache_resource
def load_model():

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
    )


chat = load_model()


# ============================================================
# EXTRACT RESUME
# ============================================================

@st.cache_data(show_spinner=False)
def extract_resume(file_bytes):

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(file_bytes)

            temp_path = temp_file.name


        documents = PyPDFLoader(temp_path).load()


        resume_text = "\n\n".join(
            document.page_content
            for document in documents
        )


        if not resume_text.strip():

            raise ValueError(
                "No readable text was found in the uploaded PDF."
            )


        return resume_text


    finally:

        if temp_path and os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================================
# PROMPTS
# ============================================================

DETAILED_MATCH_PROMPT = """
You are an expert ATS Resume Reviewer, HR Recruiter and Career Coach.

Compare the candidate's resume against the job description.

Resume:
{resume}

Job Description:
{job_description}

Return your answer in Markdown using exactly this structure:

# Overall Resume Match

Resume Match Score: XX/100

ATS Compatibility Score: XX/100

Overall Recommendation:
Excellent Match / Good Match / Moderate Match / Poor Match

---

# Score Breakdown

| Category | Score (/10) | Comments |
|----------|------------:|----------|
| Skills Match | | |
| Experience | | |
| Education | | |
| Projects | | |
| ATS Keywords | | |
| Formatting | | |

---

# Resume Summary

---

# Strengths

---

# Weaknesses

---

# Matching Skills

---

# Missing Skills

---

# Missing ATS Keywords

---

# Experience Review

---

# Education Review

---

# Top 10 Recommendations

Provide ten practical recommendations.

---

# Final Verdict

Would you recommend this candidate for an interview?

Explain why.

Rules:

- Only use information contained in the resume.
- Do not invent information.
- Be objective.
"""


QUICK_MATCH_PROMPT = """
You are an expert ATS Resume Reviewer.

Compare this resume with the job description.

Resume:
{resume}

Job Description:
{job_description}

Return Markdown with these sections:

# Resume Match Score (/100)

# ATS Compatibility Score

# Matching Skills

# Missing Skills and Keywords

# Top 5 Improvements

# Interview Recommendation

Only use information found in the resume.

Do not invent information.
"""


COVER_LETTER_PROMPT = """
You are an expert HR Recruiter and Professional Career Coach.

Write a highly professional ATS-friendly cover letter based on the candidate resume
and job description below.

Candidate Resume:
{resume}

Job Description:
{job_description}

Instructions:

- Address the hiring manager professionally.
- Tailor the letter to the job.
- Match the candidate's genuine skills and experience.
- Highlight measurable achievements only when present in the resume.
- Do not invent information.
- Use a confident and enthusiastic tone.
- Write between 300–450 words.
- Finish with a professional closing.
"""


ATS_EVALUATION_PROMPT = """
You are an expert ATS Resume Reviewer.

Resume:
{resume}

Evaluate this resume and return Markdown with these sections:

# Overall Resume Score (/100)

# ATS Compatibility Score

# Resume Summary

# Strengths

# Weaknesses

# Missing Skills

# Missing ATS Keywords

# Experience Review

# Education Review

# Top 10 Recommendations

# Suggested Career Path

Only use information found in the resume.

Do not invent information.
"""


CAREER_COACH_PROMPT = """
You are an expert Career Coach, HR Recruiter, and Interview Mentor.

Candidate Resume:
{resume}

Candidate Question:
{question}

Answer using information contained in the resume.

You can provide practical, professional guidance about:

- Resume improvements
- Career advice
- Interview preparation
- Salary negotiation
- Career transition
- ATS optimization
- Skill gaps
- Certifications
- LinkedIn optimization
- Portfolio advice
- Job search strategy

Rules:

- Never invent information.
- If the resume lacks relevant information, say so clearly.
- Give practical and actionable advice.
- Keep the answer conversational and professional.
"""


# ============================================================
# SERVICES
# ============================================================

SERVICES = {

    "Resume Match": {
        "icon": "🎯",
        "description": "Compare your resume to a job description and get a focused match report.",
        "prompt": QUICK_MATCH_PROMPT,
        "needs_job_description": True,
        "button": "🚀 Analyze Resume Match",
        "spinner": "Comparing your resume with the role...",
        "download_name": "Resume_Match_Report.md",
        "download_label": "📥 Download Match Report",
        "mime": "text/markdown",
    },

    "Cover Letter": {
        "icon": "✉️",
        "description": "Create a tailored, ATS-friendly cover letter for a specific role.",
        "prompt": COVER_LETTER_PROMPT,
        "needs_job_description": True,
        "button": "🚀 Generate Cover Letter",
        "spinner": "Generating your cover letter...",
        "download_name": "Cover_Letter.txt",
        "download_label": "📥 Download Cover Letter",
        "mime": "text/plain",
    },

    "ATS Evaluation": {
        "icon": "📊",
        "description": "Review your resume's ATS readiness, strengths, gaps, and career direction.",
        "prompt": ATS_EVALUATION_PROMPT,
        "needs_job_description": False,
        "button": "🚀 Evaluate Resume",
        "spinner": "Evaluating your resume...",
        "download_name": "ATS_Evaluation.md",
        "download_label": "📥 Download ATS Evaluation",
        "mime": "text/markdown",
    },

    "Resume Scorer": {
        "icon": "⭐",
        "description": "Generate a detailed resume-to-job scoring report.",
        "prompt": DETAILED_MATCH_PROMPT,
        "needs_job_description": True,
        "button": "🚀 Score Resume",
        "spinner": "Scoring your resume...",
        "download_name": "Resume_Score_Report.md",
        "download_label": "📥 Download Score Report",
        "mime": "text/markdown",
    },

    "Career Coach": {
        "icon": "🧑‍💼",
        "description": "Ask tailored career, interview, ATS, or job-search questions based on your resume.",
        "prompt": CAREER_COACH_PROMPT,
        "needs_job_description": False,
        "needs_question": True,
        "button": "🚀 Ask Career Coach",
        "spinner": "Preparing tailored career advice...",
        "download_name": "Career_Coach_Advice.md",
        "download_label": "📥 Download Advice",
        "mime": "text/markdown",
    },
}


# ============================================================
# SESSION STATE
# ============================================================

if "selected_service" not in st.session_state:

    st.session_state.selected_service = "Resume Match"


if "result" not in st.session_state:

    st.session_state.result = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="text-align:center; padding: 1rem 0;">
            <div style="font-size:3rem;">📄</div>
            <h1 style="margin-bottom:0;">Resume Genie</h1>
            <p style="color:#cbd5e1;">
                Your AI-powered career assistant
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.subheader("🧰 AI Services")

    for service_name, service_data in SERVICES.items():

        button_label = (
            f"{service_data['icon']}  {service_name}"
        )

        if st.button(
            button_label,
            use_container_width=True
        ):

            st.session_state.selected_service = service_name

            st.session_state.result = None

            st.rerun()


    st.divider()

    st.caption(
        "💡 Upload your resume and let Resume Genie help you prepare for your next career opportunity."
    )


# ============================================================
# CURRENT SERVICE
# ============================================================

service_name = st.session_state.selected_service

service = SERVICES[service_name]


# ============================================================
# HERO
# ============================================================

st.markdown(
    """
    <div class="hero">

        <div class="hero-badge">
            ✨ AI-Powered Career Intelligence
        </div>

        <h1>📄 Resume Genie</h1>

        <p>
            Transform your resume into a powerful career tool.
            Analyze your ATS compatibility, match your resume to job opportunities,
            create tailored cover letters, and get personalized career guidance.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SERVICE CARD
# ============================================================

st.markdown(
    f"""
    <div class="service-card">

        <h2>
            {service["icon"]} {service_name}
        </h2>

        <p>
            {service["description"]}
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown(
    '<div class="section-title">📎 Step 1 — Upload Your Resume</div>',
    unsafe_allow_html=True,
)


uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"],
    help="Upload your resume in PDF format.",
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

job_description = ""


if service.get("needs_job_description"):

    st.markdown(
        '<div class="section-title">💼 Step 2 — Add the Job Description</div>',
        unsafe_allow_html=True,
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=280,
        placeholder=(
            "Paste the full job description here...\n\n"
            "Include responsibilities, requirements, skills, "
            "qualifications, and other details."
        ),
    )


# ============================================================
# CAREER COACH QUESTION
# ============================================================

question = ""


if service.get("needs_question"):

    st.markdown(
        '<div class="section-title">💬 Step 2 — Ask Your Career Question</div>',
        unsafe_allow_html=True,
    )

    question = st.text_area(
        "What would you like help with?",
        height=140,
        placeholder=(
            "Example:\n"
            "How can I improve my chances of getting a Data Analyst role?"
        ),
    )


# ============================================================
# ACTION BUTTON
# ============================================================

st.markdown(
    '<div class="section-title">⚡ Step 3 — Generate Your AI Report</div>',
    unsafe_allow_html=True,
)


if st.button(
    service["button"],
    type="primary",
    use_container_width=True,
):

    if uploaded_file is None:

        st.warning(
            "📎 Please upload your resume as a PDF."
        )

        st.stop()


    if (
        service.get("needs_job_description")
        and not job_description.strip()
    ):

        st.warning(
            "💼 Please paste the job description."
        )

        st.stop()


    if (
        service.get("needs_question")
        and not question.strip()
    ):

        st.warning(
            "💬 Please enter a question for the Career Coach."
        )

        st.stop()


    try:

        with st.spinner(
            service["spinner"]
        ):

            resume_text = extract_resume(
                uploaded_file.getvalue()
            )


            prompt = service["prompt"].format(

                resume=resume_text,

                job_description=job_description,

                question=question,
            )


            response = chat.invoke(
                prompt
            )


            st.session_state.result = {

                "service":
                service_name,

                "content":
                response.content,
            }


        st.success(
            f"✅ {service_name} completed successfully!"
        )


    except Exception as error:

        st.error(
            "❌ The service could not complete."
        )

        st.exception(error)


# ============================================================
# DISPLAY RESULT
# ============================================================

result = st.session_state.result


if (
    result
    and result["service"] == service_name
):

    st.markdown(
        f"""
        <div class="result-header">

            <h2>
                📊 {service_name} Result
            </h2>

            <p>
                Your AI-generated analysis is ready.
                Review the results below or download a copy.
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        result["content"]
    )


    st.divider()


    st.download_button(

        label=
        service["download_label"],

        data=
        result["content"],

        file_name=
        service["download_name"],

        mime=
        service["mime"],

        use_container_width=True,
    )


# ============================================================
# HOW IT WORKS
# ============================================================

if not result:

    st.divider()

    st.markdown(
        """
        <h2 style="text-align:center;">
            🚀 How Resume Genie Works
        </h2>
        """,
        unsafe_allow_html=True,
    )

    st.write("")


    col1, col2, col3 = st.columns(3)


    with col1:

        st.markdown(
            """
            <div class="info-card">

                <h3>📎 1. Upload Your Resume</h3>

                <p>
                    Upload your resume as a PDF.
                    Resume Genie extracts and analyzes the content
                    to understand your professional profile.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col2:

        st.markdown(
            """
            <div class="info-card">

                <h3>🤖 2. Let AI Analyze</h3>

                <p>
                    Our AI analyzes your resume against your selected
                    service, job description, or career question.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


    with col3:

        st.markdown(
            """
            <div class="info-card">

                <h3>🎯 3. Get Actionable Insights</h3>

                <p>
                    Receive practical recommendations that can help
                    improve your resume and strengthen your career strategy.
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">

        <p>
            📄 <strong>Resume Genie</strong> —
            AI-powered resume analysis and career guidance.
        </p>

        <p>
            Built with Streamlit + Google Gemini AI
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)
