
import os
import tempfile

import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Resume Genie",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GOOGLE GEMINI API KEY
# ============================================================

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

if not GOOGLE_API_KEY:
    st.error(
        "Google API key is not configured. "
        "Please add GOOGLE_API_KEY to your Azure App Service Environment Variables."
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
# EXTRACT TEXT FROM RESUME PDF
# ============================================================

@st.cache_data(show_spinner=False)
def extract_resume(file_bytes):
    """
    Extract text from an uploaded PDF.

    The temporary PDF file is deleted after processing.
    """

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_file.write(file_bytes)
            temp_path = temp_file.name

        # Load PDF
        documents = PyPDFLoader(temp_path).load()

        # Extract text
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
- Match the candidate's genuine skills and experience to the requirements.
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

        "description":
        "Compare your resume to a job description and get a focused match report.",

        "prompt":
        QUICK_MATCH_PROMPT,

        "needs_job_description":
        True,

        "button":
        "🚀 Analyze Resume Match",

        "spinner":
        "Comparing your resume with the role...",

        "download_name":
        "Resume_Match_Report.md",

        "download_label":
        "📥 Download Match Report",

        "mime":
        "text/markdown",
    },


    "Cover Letter": {

        "description":
        "Create a tailored, ATS-friendly cover letter for a specific role.",

        "prompt":
        COVER_LETTER_PROMPT,

        "needs_job_description":
        True,

        "button":
        "🚀 Generate Cover Letter",

        "spinner":
        "Generating your cover letter...",

        "download_name":
        "Cover_Letter.txt",

        "download_label":
        "📥 Download Cover Letter",

        "mime":
        "text/plain",
    },


    "ATS Evaluation": {

        "description":
        "Review your resume's ATS readiness, strengths, gaps, and career direction.",

        "prompt":
        ATS_EVALUATION_PROMPT,

        "needs_job_description":
        False,

        "button":
        "🚀 Evaluate Resume",

        "spinner":
        "Evaluating your resume...",

        "download_name":
        "ATS_Evaluation.md",

        "download_label":
        "📥 Download ATS Evaluation",

        "mime":
        "text/markdown",
    },


    "Resume Scorer": {

        "description":
        "Generate a detailed resume-to-job scoring report.",

        "prompt":
        DETAILED_MATCH_PROMPT,

        "needs_job_description":
        True,

        "button":
        "🚀 Score Resume",

        "spinner":
        "Scoring your resume...",

        "download_name":
        "Resume_Score_Report.md",

        "download_label":
        "📥 Download Score Report",

        "mime":
        "text/markdown",
    },


    "Career Coach": {

        "description":
        "Ask tailored career, interview, ATS, or job-search questions based on your resume.",

        "prompt":
        CAREER_COACH_PROMPT,

        "needs_job_description":
        False,

        "needs_question":
        True,

        "button":
        "🚀 Ask Career Coach",

        "spinner":
        "Preparing tailored career advice...",

        "download_name":
        "Career_Coach_Advice.md",

        "download_label":
        "📥 Download Advice",

        "mime":
        "text/markdown",
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

    st.title("📄 Resume Genie")

    st.caption(
        "Your AI-powered resume and career assistant"
    )

    st.divider()

    st.subheader("Choose a Service")

    for service_name in SERVICES:

        if st.button(
            service_name,
            use_container_width=True
        ):

            st.session_state.selected_service = service_name

            st.session_state.result = None

            st.rerun()


# ============================================================
# CURRENT SERVICE
# ============================================================

service_name = st.session_state.selected_service

service = SERVICES[service_name]


# ============================================================
# MAIN APPLICATION
# ============================================================

st.title("📄 Resume Genie")

st.subheader(service_name)

st.write(
    service["description"]
)


# ============================================================
# RESUME UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload Resume (PDF)",
    type=["pdf"],
    help="Upload your resume in PDF format."
)


# ============================================================
# JOB DESCRIPTION
# ============================================================

job_description = ""

if service.get("needs_job_description"):

    job_description = st.text_area(

        "Paste Job Description",

        height=280,

        placeholder=
        "Paste the full job description here..."
    )


# ============================================================
# CAREER COACH QUESTION
# ============================================================

question = ""

if service.get("needs_question"):

    question = st.text_area(

        "What would you like help with?",

        height=140,

        placeholder=
        "Example: How can I improve my chances of getting a Data Analyst role?"
    )


# ============================================================
# ACTION BUTTON
# ============================================================

if st.button(
    service["button"],
    type="primary",
    use_container_width=True
):

    # Validate resume
    if uploaded_file is None:

        st.warning(
            "Please upload your resume as a PDF."
        )

        st.stop()


    # Validate job description
    if (
        service.get("needs_job_description")
        and not job_description.strip()
    ):

        st.warning(
            "Please paste the job description."
        )

        st.stop()


    # Validate career coach question
    if (
        service.get("needs_question")
        and not question.strip()
    ):

        st.warning(
            "Please enter a question for the Career Coach."
        )

        st.stop()


    try:

        with st.spinner(
            service["spinner"]
        ):

            # Extract resume
            resume_text = extract_resume(
                uploaded_file.getvalue()
            )


            # Create prompt
            prompt = service["prompt"].format(

                resume=resume_text,

                job_description=job_description,

                question=question,
            )


            # Call Gemini
            response = chat.invoke(
                prompt
            )


            # Store result
            st.session_state.result = {

                "service":
                service_name,

                "content":
                response.content,
            }


        st.success(
            f"{service_name} completed successfully!"
        )


    except Exception as error:

        st.error(
            "The service could not complete."
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

    st.divider()

    st.subheader(
        f"📊 {service_name} Result"
    )

    st.markdown(
        result["content"]
    )


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
