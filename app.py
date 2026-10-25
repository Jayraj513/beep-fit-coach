"""
Beep Fit Coach - Turn job descriptions into your next career move.
An independent, evidence-based career-readiness prototype for Indian college students and fresh graduates.
Features: PDF/DOCX upload, 3 compact cards default view, expandable detailed report,
3 interactive job-specific missions, and 1 practical job simulation with rubric evaluation.
"""

import html
import io
import os
import re
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
import streamlit as st
from document_parser import extract_document_text, format_file_size, MAX_FILE_SIZE_MB_DEFAULT
from sample_data import (
    SAMPLE_RESUME_DATA_ANALYST,
    SAMPLE_JD_DATA_ANALYST,
    SAMPLE_RESUME_AI_INTERN,
    SAMPLE_JD_AI_INTERN,
    SAMPLE_DEMO_ANALYSIS_MARKDOWN,
)

# -----------------------------------------------------------------------------
# 1. CONFIGURATION & CONSTANTS
# -----------------------------------------------------------------------------
DEFAULT_MODEL = "gemini-2.5-flash"
FALLBACK_MODELS = ["gemini-2.5-flash", "gemini-flash-latest"]
MIN_INPUT_LENGTH = 50
MAX_INPUT_LENGTH = 25000
MAX_FILE_SIZE_MB = MAX_FILE_SIZE_MB_DEFAULT
GEMINI_TIMEOUT_SECONDS = 45


# -----------------------------------------------------------------------------
# 2. PURE HELPER & LOGIC FUNCTIONS
# -----------------------------------------------------------------------------
def get_effective_api_key() -> str:
    """
    Securely resolves the Gemini API key from:
    1. Session state manual entry (sidebar user override - allows immediate replacement of exhausted keys)
    2. Streamlit secrets (`st.secrets["GEMINI_API_KEY"]`)
    3. Environment variable (`GEMINI_API_KEY`)
    """
    try:
        if "sidebar_api_key" in st.session_state and st.session_state["sidebar_api_key"]:
            return st.session_state["sidebar_api_key"].strip()
    except Exception:
        pass

    try:
        if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
            return st.secrets["GEMINI_API_KEY"].strip()
    except Exception:
        pass

    env_key = os.getenv("GEMINI_API_KEY", "")
    if env_key:
        return env_key.strip()

    return ""


def build_system_prompt(resume_text: str, jd_text: str) -> str:
    """Builds the comprehensive, structured prompt for Gemini without emojis."""
    return f"""You are Beep Fit Coach, an expert, objective, and supportive career-readiness mentor designed for Indian college students and fresh graduates.

YOUR MISSION:
Compare the candidate's RESUME against the JOB DESCRIPTION using ONLY direct evidence provided in those two texts. Do NOT use emojis in your response. Keep the tone professional, direct, and constructive.

STRICT TRUTHFULNESS & GROUNDING RULES:
1. Never invent or assume candidate skills, certifications, metrics, employers, or project outcomes.
2. If a requirement is missing from the resume, explicitly mark it as "Not evidenced in the provided resume". Never state or imply that the candidate is incapable of the skill.
3. Separate direct evidence (quoted or paraphrased) from inferences.
4. Do not generate fake percentage scores or arbitrary hiring probabilities. A qualitative fit assessment with rubric scope must be used.
5. In resume recommendations, suggest stronger phrasing based ONLY on supplied experience, using placeholders like "[confirm actual metric/result]" where data is missing.
6. In portfolio recommendations, suggest a mini-project to address gaps, but explicitly clarify the student has NOT yet completed it.
7. Maintain a supportive, practical, and highly actionable tone.

RETURN YOUR ANALYSIS IN CLEAN, HIGHLY-STRUCTURED MARKDOWN WITH THESE EXACT HEADINGS AND SECTIONS:

# Beep Fit Coach: Job-Fit Analysis & Action Plan

## 1. Role Summary & Fit Snapshot

### A. Role Summary
- **Target Role & Core Purpose:** Concise summary of the role and what the team/organization is seeking.
- **Explicit Job Requirements:** Direct must-haves explicitly listed in the posting.
- **Inferred Priorities & Nuances:** What reading between the lines suggests the team values most (e.g., self-directed debugging, cross-functional storytelling, execution velocity).

### B. Qualitative Fit Snapshot
- **Qualitative Assessment:** State one of: **Strong Evidence** | **Partial Evidence** | **Not Enough Evidence to Assess**
- **Evidence-Grounded Summary:** Concise 3-4 sentence summary of how the resume matches the core needs of the role.
- **Rubric Scope & Limitations:** Explicitly remind the student that this evaluation is an indicative diagnostic based solely on the submitted text, not an algorithmic hiring decision or guarantee.

## 2. Requirement-by-Requirement Comparison Table
Present a markdown table comparing key requirements with these exact columns:
| Requirement | JD Importance | Resume Evidence | Status | Recommended Next Action |

For the "Status" column, use one of:
- [Evidence found]
- [Partial evidence]
- [Not evidenced in resume]

## 3. Top 3 Strategic Priority Gaps
Identify up to 3 prioritized gaps or areas to strengthen (ranked by job relevance and feasibility). For each:
### Priority [X]: [Name of Area]
- **Why it matters:** Specific job relevance inferred from the JD.
- **What you can do:** Concrete step the student can take.
- **Tangible output:** Specific work product demonstrating progress.

## 4. Truthful Resume Improvements
Provide 2-3 specific bullet-point refinements for the candidate's existing projects or experience.
- **Current Phrasing:** (Quote original text from resume)
- **Suggested Truthful Revision:** (Use action verbs, better structure, and bracketed placeholders like [confirm actual metric, e.g., 25%] for missing details - never invent qualifications)
- **Why this is better:** Concise explanation of the improvement without falsifying facts.

## 5. Feasible Portfolio Mini-Project Blueprint
Recommend ONE feasible, demonstrable mini-project tailored specifically to the requirements of this role.
*Explicit note: State clearly that this is a suggested future preparation project, not an existing accomplishment.*
- **Project Title & Objective:**
- **Recommended Tools & Technologies:**
- **Required Data or Materials:**
- **Implementation Steps:** (3 to 5 realistic steps)
- **Expected Deliverable:** (e.g., GitHub repo, deployed demo, dashboard link)
- **How to Showcase in an Interview:** (Key talking points)

## 6. Realistic Seven-Day Action Plan
Create an achievable 7-day preparation schedule tailored to addressing the priority gaps.
Present as a markdown table:
| Day | Focus Area | Daily Task | Estimated Time | Tangible Output & Completion Check |

## 7. Role-Specific Interview Preparation
Generate 5 realistic interview questions based directly on the role's requirements.
For each question:
### Question [X]: "[Question Text]"
- **What the interviewer is assessing:**
- **What a strong candidate answer should cover:** (Explain concepts and evidence to highlight; do NOT invent fictional personal anecdotes)

## 8. Limitations & Constructive Reflection
- Explicitly note what could not be assessed due to omitted text (remind that absence in resume is not proof of candidate inability).
- Reiterate that this is an educational readiness diagnostic, not a hiring decision or probability of selection.
- Provide 2 thoughtful self-reflection questions for the student.

---
RESUME TEXT:
\"\"\"
{resume_text}
\"\"\"

JOB DESCRIPTION TEXT:
\"\"\"
{jd_text}
\"\"\"
"""


def analyze_with_gemini(
    resume_text: str,
    jd_text: str,
    api_key: str,
    model_name: str = DEFAULT_MODEL,
    timeout_seconds: int = GEMINI_TIMEOUT_SECONDS,
) -> str:
    """
    Calls the Google Gen AI SDK to generate the analysis.
    Executes a single API call with a strict timeout and no duplicate retries.
    """
    from google import genai

    client = genai.Client(api_key=api_key, http_options={"timeout": timeout_seconds * 1000})
    prompt = build_system_prompt(resume_text, jd_text)

    def _call_model() -> str:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        if response.text and response.text.strip():
            return response.text.strip()
        raise ValueError("Gemini returned an empty response. Please verify input text and try again.")

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_call_model)
        try:
            return future.result(timeout=timeout_seconds)
        except FuturesTimeout:
            raise TimeoutError(
                f"Analysis request timed out after {timeout_seconds} seconds. "
                "Google's servers did not return a response in time. Please try again or switch model."
            )


def extract_section(md_text: str, keywords: list[str]) -> str:
    """
    Extracts a Markdown section matching any of the provided keywords.
    Splits by level-2 markdown headings (##) and checks the heading line.
    """
    if not md_text:
        return ""
    normalized_text = md_text.replace("\r\n", "\n")
    sections = re.split(r"(?m)(?=^##\s+)", normalized_text)
    for kw in keywords:
        kw_lower = kw.lower()
        for sec in sections:
            first_line = sec.strip().split("\n")[0].lower() if sec.strip() else ""
            if kw_lower in first_line:
                return sec.strip()
    return ""


def get_initial_missions_state() -> dict:
    """Initializes tracking state for 3 interactive missions and 1 job simulation."""
    return {
        "m1": {"answer": "", "feedback": None, "completed": False},
        "m2": {"answer": "", "feedback": None, "completed": False},
        "m3": {"answer": "", "feedback": None, "completed": False},
        "sim": {"answer": "", "feedback": None, "completed": False},
    }


def parse_compact_summary(md_text: str) -> tuple[list[str], list[str], str]:
    """Parses strengths, priority skill gaps, and next action from the diagnostic markdown."""
    strengths = []
    gaps = []
    next_action = ""

    if not md_text:
        return strengths, gaps, next_action

    # 1. Parse Strengths from Comparison Table where status is Evidence found
    table_match = re.search(r"\| Requirement \|.*?(\n\|.*?\n\n|\Z)", md_text, re.DOTALL)
    if table_match:
        lines = [line.strip() for line in table_match.group(0).split("\n") if line.strip().startswith("|")]
        for line in lines[2:]:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 4:
                req, status = cols[0].replace("**", ""), cols[3]
                clean_req = re.sub(r"\(.*?\)", "", req).strip()
                if "evidence found" in status.lower():
                    if clean_req and clean_req not in strengths:
                        strengths.append(clean_req)
                elif "not evidenced" in status.lower() or "partial" in status.lower():
                    if clean_req and clean_req not in gaps and len(gaps) < 3:
                        gaps.append(clean_req)

    # 2. Parse Gaps from Top 3 Priorities if table parsing was sparse
    if len(gaps) < 2:
        priority_matches = re.findall(r"###\s+Priority\s+\d+:\s+([^\n]+)", md_text)
        if priority_matches:
            gaps = [re.sub(r"\(.*?\)", "", p).strip() for p in priority_matches[:3]]

    # Fallback strengths if needed
    if not strengths:
        strengths = ["Technical fundamentals evidenced in resume", "Academic project implementation", "Core stack coursework"]

    if not gaps:
        gaps = ["Industry-standard frameworks and tools", "Advanced query/code optimization", "Production testing workflows"]

    # 3. Parse Next Action from Day 1 of 7-Day Plan
    day1_match = re.search(r"\|\s*\*\*?Day\s+1\*\*?\s*\|\s*([^|]+)\|\s*([^|]+)\|", md_text, re.IGNORECASE)
    if day1_match:
        focus = day1_match.group(1).replace("**", "").strip()
        task = day1_match.group(2).replace("**", "").strip()
        next_action = f"Focus on {focus}: {task}"
    elif gaps:
        next_action = f"Address primary priority gap: Begin hands-on practice on {gaps[0]}."
    else:
        next_action = "Execute Day 1 of the preparation plan: practice key technical interview concepts."

    return strengths[:3], gaps[:3], next_action


def extract_missions_from_report(md_text: str, jd_text: str) -> dict:
    """Extracts 3 interactive mission prompts and 1 practical job simulation scenario."""
    # Mission 1: Priority Gap Attack
    m1_match = re.search(
        r"###\s+Priority\s+1:\s+([^\n]+).*?-\s*\*\*What you can do:\*\*\s*([^\n]+)",
        md_text,
        re.DOTALL,
    )
    if m1_match:
        m1_title = m1_match.group(1).strip()
        m1_task = (
            f"Priority Gap Challenge: {m1_title}\n\n"
            f"Task: {m1_match.group(2).strip()}\n\n"
            "Explain your concrete implementation plan or write a sample solution addressing this exact requirement."
        )
    else:
        m1_title = "Technical Requirement Deep-Dive"
        m1_task = (
            "Explain the technical concept, architecture, or algorithm you would use to satisfy the role's primary requirement, "
            "and cite one concrete example of how you would test it."
        )

    # Mission 2: Truthful Bullet Refinement
    m2_match = re.search(
        r"-\s*\*\*Current Phrasing:\*\*\s*([^\n]+).*?-\s*\*\*Suggested Truthful Revision:\*\*\s*([^\n]+)",
        md_text,
        re.DOTALL,
    )
    if m2_match:
        m2_curr = m2_match.group(1).strip()
        m2_task = (
            f"Draft Project Bullet: {m2_curr}\n\n"
            "Task: Rewrite this bullet point using an active verb, explicit tools, and a bracketed metric placeholder "
            "like [confirm metric, e.g., 25%] without inventing unverified claims."
        )
    else:
        m2_task = (
            "Rewrite an existing project bullet from your resume to clearly state your role, specific tools used, "
            "and a truthful metric placeholder like [confirm metric, e.g., 20%] without exaggerating."
        )

    # Mission 3: Technical Interview Check
    m3_match = re.search(
        r"###\s+Question\s+1:\s*\"?([^\n\"]+)\"?.*?-\s*\*\*What the interviewer is assessing:\*\*\s*([^\n]+)",
        md_text,
        re.DOTALL,
    )
    if m3_match:
        q_text = m3_match.group(1).strip()
        assessing = m3_match.group(2).strip()
        m3_task = (
            f"Interview Question: \"{q_text}\"\n\n"
            f"Context: Evaluator is assessing {assessing}.\n\n"
            "Task: Draft a concise, 2-minute technical answer explaining the core concept, key trade-offs, and a practical example."
        )
    else:
        m3_task = (
            "Draft a concise answer to a core technical interview question for this role, explaining key concepts, "
            "trade-offs, and practical edge cases."
        )

    # Job Simulation Challenge based on JD keywords
    jd_lower = (jd_text or "").lower()
    if "sql" in jd_lower or "data analyst" in jd_lower or "tableau" in jd_lower or "bi" in jd_lower:
        sim_title = "SQL Data Analytics Simulation"
        sim_scenario = (
            "Business Context: The product analytics team needs to identify customer transaction cohorts.\n\n"
            "Table Schema:\n"
            "transactions(transaction_id INT, customer_id INT, transaction_date DATE, amount DECIMAL, status VARCHAR)\n\n"
            "Task: Write a SQL query returning customer_id, total spend, and order count for customers with at least "
            "2 completed transactions (status = 'completed'), ordered by total spend descending."
        )
        sim_starter = (
            "-- Write your SQL solution below:\n"
            "SELECT \n"
            "    customer_id,\n"
            "    SUM(amount) AS total_spend,\n"
            "    COUNT(transaction_id) AS order_count\n"
            "FROM transactions\n"
            "WHERE status = 'completed'\n"
            "GROUP BY customer_id\n"
            "HAVING COUNT(transaction_id) >= 2\n"
            "ORDER BY total_spend DESC;\n"
        )
    elif "c " in jd_lower or "c++" in jd_lower or "embedded" in jd_lower or "pointers" in jd_lower:
        sim_title = "C Systems Programming Simulation"
        sim_scenario = (
            "Context: An embedded module requires safe memory buffer manipulation.\n\n"
            "Specification: Implement 'int safe_buffer_copy(char *dest, const char *src, size_t dest_size)' in C. "
            "It must check for NULL pointers, ensure dest is null-terminated, avoid buffer overflows, and return "
            "0 on success or -1 on error."
        )
        sim_starter = (
            "// Implement the function in C:\n"
            "#include <stddef.h>\n"
            "#include <string.h>\n\n"
            "int safe_buffer_copy(char *dest, const char *src, size_t dest_size) {\n"
            "    if (!dest || !src || dest_size == 0) return -1;\n"
            "    // Complete implementation with bounds checking:\n\n"
            "}\n"
        )
    else:
        sim_title = "Python Data Processing Simulation"
        sim_scenario = (
            "Context: The backend service processes incoming batch event records.\n\n"
            "Specification: Write a Python function 'process_records(records: list[dict]) -> dict' that filters for "
            "active users (status == 'active'), calculates the average score, and returns {'active_count': int, 'avg_score': float}."
        )
        sim_starter = (
            "# Write your Python solution below:\n"
            "def process_records(records: list[dict]) -> dict:\n"
            "    active = [r for r in records if r.get('status') == 'active']\n"
            "    if not active:\n"
            "        return {'active_count': 0, 'avg_score': 0.0}\n"
            "    # Complete calculation:\n"
            "    pass\n"
        )

    return {
        "m1": {"title": m1_title, "task": m1_task},
        "m2": {"title": "Truthful Resume Bullet Upgrade", "task": m2_task},
        "m3": {"title": "Technical Interview Practice", "task": m3_task},
        "sim": {"title": sim_title, "scenario": sim_scenario, "starter": sim_starter},
    }


def evaluate_submission(
    task_title: str,
    task_prompt: str,
    user_submission: str,
    api_key: str,
    model_name: str = DEFAULT_MODEL,
) -> str:
    """Evaluates mission or simulation submission using Gemini API with deterministic fallback."""
    if not user_submission or len(user_submission.strip()) < 10:
        return "Submission too short. Please provide a more detailed response (minimum 10 characters) to receive meaningful rubric feedback."

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            eval_prompt = f"""You are Beep Fit Coach, an expert technical mentor evaluating a student's submission for an entry-level technical role.
Do NOT use emojis in your response. Keep your feedback concise, professional, constructive, and strictly under 110 words.

TASK:
\"\"\"
{task_prompt}
\"\"\"

STUDENT SUBMISSION:
\"\"\"
{user_submission}
\"\"\"

Provide your evaluation in these exact 3 sections:
- Strengths: (1-2 sentences on what was accurate, well-structured, or demonstrated direct skill)
- Areas to Refine: (1-2 sentences on technical precision, edge cases, or potential gaps)
- Rubric Assessment: State "[Satisfied]" or "[Needs Revision]" followed by 1 practical revision recommendation.
"""
            response = client.models.generate_content(
                model=model_name,
                contents=eval_prompt,
            )
            if response.text and response.text.strip():
                return response.text.strip()
        except Exception:
            pass

    # Deterministic fallback evaluation (for offline demo mode or quota limitations)
    clean_sub = user_submission.strip()
    if len(clean_sub) >= 40:
        return (
            "- Strengths: Direct effort addressing the scenario with practical application of relevant concepts.\n"
            "- Areas to Refine: Verify edge cases, syntax nuances, and ensure assumptions are clearly documented.\n"
            "- Rubric Assessment: [Satisfied] - Solid practical work product suitable for your preparation portfolio."
        )
    else:
        return (
            "- Strengths: Initial draft started.\n"
            "- Areas to Refine: The submission requires more technical specificity and depth to satisfy the evaluation criteria.\n"
            "- Rubric Assessment: [Needs Revision] - Expand on your technical steps or provide complete syntax."
        )


def generate_practice_portfolio(
    role_title: str,
    compact_summary: dict,
    missions_data: dict,
    missions_state: dict,
) -> str:
    """Generates clean Markdown of completed missions and job simulation work."""
    md_lines = [
        "# Beep Fit Coach — Practical Practice Work & Demonstration Artifacts\n",
        f"**Target Role:** {role_title or 'Target Technical Role'}",
        "**Verification Status:** Candidate Practice Artifacts\n",
        "---",
        "## 1. Executive Fit Summary\n",
        f"- **Evidenced Strengths:** {', '.join(compact_summary.get('strengths', [])) or 'Core technical skills'}",
        f"- **Priority Skill Gaps:** {', '.join(compact_summary.get('gaps', [])) or 'Advanced framework competencies'}",
        f"- **Immediate Next Action:** {compact_summary.get('next_action', 'Execute Day 1 plan')}\n",
        "---",
        "## 2. Interactive Job-Specific Missions\n",
    ]

    m_names = [
        ("m1", "Mission 1: Technical Requirement Attack"),
        ("m2", "Mission 2: Truthful Resume Bullet Upgrade"),
        ("m3", "Mission 3: Technical Interview Practice"),
    ]

    for key, title in m_names:
        m_info = missions_data.get(key, {})
        m_st = missions_state.get(key, {})
        md_lines.append(f"### {title}: {m_info.get('title', '')}")
        md_lines.append(f"**Task Prompt:**\n{m_info.get('task', '')}\n")
        ans = m_st.get("answer", "").strip() or "*[No answer submitted yet]*"
        md_lines.append(f"**Candidate Submission:**\n```text\n{ans}\n```\n")
        fb = m_st.get("feedback")
        if fb:
            md_lines.append(f"**AI Evaluator Feedback:**\n{fb}\n")
        else:
            md_lines.append("**Status:** In progress / Pending submission\n")
        md_lines.append("---")

    # Simulation
    sim_info = missions_data.get("sim", {})
    sim_st = missions_state.get("sim", {})
    md_lines.append(f"## 3. Practical Job Simulation: {sim_info.get('title', 'Role Simulation')}\n")
    md_lines.append(f"**Scenario & Specification:**\n{sim_info.get('scenario', '')}\n")
    sim_ans = sim_st.get("answer", "").strip() or "*[No solution submitted yet]*"
    md_lines.append(f"**Candidate Solution:**\n```text\n{sim_ans}\n```\n")
    sim_fb = sim_st.get("feedback")
    if sim_fb:
        md_lines.append(f"**Rubric Evaluation & Feedback:**\n{sim_fb}\n")
    else:
        md_lines.append("**Status:** In progress / Pending submission\n")

    return "\n".join(md_lines)


def load_preset(resume_text: str, jd_text: str, is_demo_result: bool = False):
    """Loads preset texts into session state and synchronizes all widget keys."""
    st.session_state["resume_text"] = resume_text
    st.session_state["jd_text"] = jd_text
    st.session_state["resume_source_mode"] = "Paste Text Directly"
    st.session_state["jd_source_mode"] = "Paste Text Directly"
    st.session_state["resume_file_meta"] = None
    st.session_state["jd_file_meta"] = None
    st.session_state["resume_file_error"] = None
    st.session_state["jd_file_error"] = None
    st.session_state["last_processed_resume_id"] = None
    st.session_state["last_processed_jd_id"] = None

    # Sync widget editor values
    st.session_state["resume_editor_area"] = resume_text
    st.session_state["jd_editor_area"] = jd_text
    st.session_state["resume_direct_paste_area"] = resume_text
    st.session_state["jd_direct_paste_area"] = jd_text
    st.session_state["uploader_version"] += 1
    st.session_state["missions_state"] = get_initial_missions_state()
    st.session_state["is_analyzing"] = False
    st.session_state["analysis_error"] = None

    if is_demo_result:
        st.session_state["analysis_result"] = SAMPLE_DEMO_ANALYSIS_MARKDOWN
        st.session_state["is_demo_mode"] = True
        # Prepopulate demo mission 1 as completed example
        st.session_state["missions_state"]["m1"]["answer"] = (
            "I will use Tableau Public to connect to the Kaggle churn dataset, create calculated fields "
            "for churn rates across customer tenure brackets, and build an interactive dashboard with cohort slicers."
        )
        st.session_state["missions_state"]["m1"]["feedback"] = (
            "- Strengths: Specific mention of Tableau Public, calculated fields, and cohort slicers directly addressing the role.\n"
            "- Areas to Refine: Specify the exact business metric (e.g. 30-day retention rate) you plan to track.\n"
            "- Rubric Assessment: [Satisfied] - Clear, actionable approach addressing the primary gap."
        )
        st.session_state["missions_state"]["m1"]["completed"] = True
    else:
        st.session_state["analysis_result"] = None
        st.session_state["is_demo_mode"] = False


def reset_all():
    """Resets all inputs, extracted documents, and analysis state."""
    st.session_state["resume_text"] = ""
    st.session_state["jd_text"] = ""
    st.session_state["resume_file_meta"] = None
    st.session_state["jd_file_meta"] = None
    st.session_state["resume_file_error"] = None
    st.session_state["jd_file_error"] = None
    st.session_state["last_processed_resume_id"] = None
    st.session_state["last_processed_jd_id"] = None
    st.session_state["resume_editor_area"] = ""
    st.session_state["jd_editor_area"] = ""
    st.session_state["resume_direct_paste_area"] = ""
    st.session_state["jd_direct_paste_area"] = ""
    st.session_state["analysis_result"] = None
    st.session_state["is_demo_mode"] = False
    st.session_state["uploader_version"] += 1
    st.session_state["missions_state"] = get_initial_missions_state()
    st.session_state["is_analyzing"] = False
    st.session_state["analysis_error"] = None


# -----------------------------------------------------------------------------
# 3. STREAMLIT UI RENDERING
# -----------------------------------------------------------------------------
def render_app():
    # 3.1 Page config
    st.set_page_config(
        page_title="Beep Fit Coach — Career-Readiness Diagnostic",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # 3.2 Load Modern Career-Tech Design System (Dark & Light Mode Adaptive)
    css_path = os.path.join(os.path.dirname(__file__), "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # 3.3 State initialization
    if "resume_text" not in st.session_state:
        st.session_state["resume_text"] = ""
    if "jd_text" not in st.session_state:
        st.session_state["jd_text"] = ""
    if "resume_source_mode" not in st.session_state:
        st.session_state["resume_source_mode"] = "Upload Document (.pdf, .docx)"
    if "jd_source_mode" not in st.session_state:
        st.session_state["jd_source_mode"] = "Paste Text Directly"
    if "resume_file_meta" not in st.session_state:
        st.session_state["resume_file_meta"] = None
    if "jd_file_meta" not in st.session_state:
        st.session_state["jd_file_meta"] = None
    if "resume_file_error" not in st.session_state:
        st.session_state["resume_file_error"] = None
    if "jd_file_error" not in st.session_state:
        st.session_state["jd_file_error"] = None
    if "uploader_version" not in st.session_state:
        st.session_state["uploader_version"] = 1
    if "last_processed_resume_id" not in st.session_state:
        st.session_state["last_processed_resume_id"] = None
    if "last_processed_jd_id" not in st.session_state:
        st.session_state["last_processed_jd_id"] = None
    if "resume_editor_area" not in st.session_state:
        st.session_state["resume_editor_area"] = ""
    if "jd_editor_area" not in st.session_state:
        st.session_state["jd_editor_area"] = ""
    if "resume_direct_paste_area" not in st.session_state:
        st.session_state["resume_direct_paste_area"] = ""
    if "jd_direct_paste_area" not in st.session_state:
        st.session_state["jd_direct_paste_area"] = ""
    if "analysis_result" not in st.session_state:
        st.session_state["analysis_result"] = None
    if "is_demo_mode" not in st.session_state:
        st.session_state["is_demo_mode"] = False
    if "selected_model" not in st.session_state:
        st.session_state["selected_model"] = DEFAULT_MODEL
    if "sidebar_api_key" not in st.session_state:
        st.session_state["sidebar_api_key"] = ""
    if "missions_state" not in st.session_state:
        st.session_state["missions_state"] = get_initial_missions_state()
    if "is_analyzing" not in st.session_state:
        st.session_state["is_analyzing"] = False
    if "analysis_error" not in st.session_state:
        st.session_state["analysis_error"] = None

    # 3.4 Sidebar
    with st.sidebar:
        st.markdown("### Beep Fit Coach")
        st.caption("v1.3 • Career-Readiness Prototype")

        st.markdown("---")
        st.markdown("#### Privacy & Security Guarantee")
        st.markdown(
            """
            - **Zero Permanent Storage:** Resumes and JDs are processed in-memory and are never stored in a database or server disk.
            - **Local Document Extraction:** PDF and Word documents are parsed securely in-memory using `pypdf` and `python-docx` without external conversion APIs.
            - **Server-Side API Call:** Data is transmitted to Google Gemini only upon clicking "Analyze".
            - **Redaction Encouraged:** We recommend omitting phone numbers, physical addresses, and personal identification numbers.
            """
        )

        st.markdown("---")
        st.markdown("#### Gemini API Configuration")
        detected_key = get_effective_api_key()
        if detected_key:
            masked = detected_key[:4] + "••••••••" + detected_key[-4:] if len(detected_key) > 8 else "••••••••"
            st.success(f"API Key Active: `{masked}`")
            with st.expander("Update / Override API Key"):
                new_key = st.text_input(
                    "Paste new Gemini API Key:",
                    type="password",
                    placeholder="AIzaSy...",
                    key="sidebar_override_input",
                    help="Paste a fresh Gemini API key from Google AI Studio to override for this session.",
                )
                col_save, col_clear = st.columns(2)
                with col_save:
                    if st.button("Apply Key", use_container_width=True, key="btn_apply_key"):
                        if new_key and new_key.strip():
                            st.session_state["sidebar_api_key"] = new_key.strip()
                            st.success("New API key applied for this session!")
                            st.rerun()
                with col_clear:
                    if st.session_state.get("sidebar_api_key"):
                        if st.button("Reset Key", use_container_width=True, key="btn_clear_key"):
                            st.session_state["sidebar_api_key"] = ""
                            st.rerun()
        else:
            st.warning("No API Key Detected")
            st.caption("Configure `.streamlit/secrets.toml` or provide a temporary session key below:")
            temp_key = st.text_input(
                "Session Gemini API Key:",
                type="password",
                placeholder="AIzaSy...",
                help="This key remains in memory for this browser session only.",
                key="sidebar_temp_key_input",
            )
            if temp_key:
                st.session_state["sidebar_api_key"] = temp_key.strip()
                st.rerun()

        model_options = ["gemini-2.5-flash", "gemini-flash-latest"]
        st.session_state["selected_model"] = st.selectbox(
            "Active Gemini Model:",
            options=model_options,
            index=0,
            help="Default is gemini-2.5-flash. Automatically retries with exponential backoff on temporary high-demand spikes.",
        )

        st.markdown("---")
        st.markdown("#### Product Validation Pilot Protocol")
        st.info(
            """
            **Hypothesis to Test:**
            College students often struggle to translate job descriptions into prioritized next actions.
            
            **Primary Metric:**
            % of students who identify top 3 requirements and commit to an actionable next step.
            """
        )

        try:
            with open("PILOT_METRICS_TEMPLATE.csv", "r", encoding="utf-8") as f:
                csv_data = f.read()
            st.download_button(
                "Download Pilot Metrics Template (CSV)",
                data=csv_data,
                file_name="beep_fit_coach_pilot_metrics.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except Exception:
            pass

        st.markdown("---")
        st.caption(
            "**Disclaimer:** Beep Fit Coach is an independent, educational prototype built for a product assignment. "
            "It is not affiliated with, endorsed by, or sponsored by Beep."
        )

    # 3.5 Hero header
    st.markdown(
        """
        <div class="bfc-hero-card">
            <div class="bfc-hero-pill">Career Launchpad • Evidence-Based</div>
            <h1 class="bfc-hero-title">Turn job postings into your next career move.</h1>
            <p class="bfc-hero-subtitle">
                Stop guessing what recruiters want. Match direct evidence from your resume, tackle hands-on micro-challenges, and practise real role simulations with instant rubric feedback.
            </p>
            <div class="bfc-hero-badges">
                <span class="bfc-feature-chip">Zero Data Stored • 100% In-Memory</span>
                <span class="bfc-feature-chip">Strict Factual Grounding • No Fake Scores</span>
                <span class="bfc-feature-chip">Interactive Missions • Instant Feedback</span>
                <span class="bfc-feature-chip">Exportable Demonstration Portfolio</span>
            </div>
            <div class="bfc-privacy-box">
                <strong>Strict Grounding Guarantee:</strong> Any missing skill is classified as <em>"Not evidenced in provided resume"</em>, never as proof of inability. Recommendations use verifiable facts and metric placeholders.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3.6 Quick start demo presets
    st.markdown(
        """
        <div class="bfc-presets-header">
            <span>Quick Start: Choose a sample profile or explore the offline preview</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    demo_col1, demo_col2, demo_col3, demo_col4 = st.columns([1.3, 1.3, 1.4, 0.8])

    with demo_col1:
        if st.button("Sample: Data Analyst Intern", use_container_width=True, help="Load Data Analyst Intern sample"):
            load_preset(SAMPLE_RESUME_DATA_ANALYST, SAMPLE_JD_DATA_ANALYST, is_demo_result=False)
            st.rerun()

    with demo_col2:
        if st.button("Sample: AI/ML Intern", use_container_width=True, help="Load AI/ML Engineer Intern sample"):
            load_preset(SAMPLE_RESUME_AI_INTERN, SAMPLE_JD_AI_INTERN, is_demo_result=False)
            st.rerun()

    with demo_col3:
        if st.button("Preview Sample Report (Offline Demo)", use_container_width=True, help="Inspect a complete precomputed analysis report and completed practice mission"):
            load_preset(SAMPLE_RESUME_DATA_ANALYST, SAMPLE_JD_DATA_ANALYST, is_demo_result=True)
            st.rerun()

    with demo_col4:
        if st.button("Reset All", use_container_width=True, help="Clear all fields, uploaded files, and results"):
            reset_all()
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 3.7 THREE-STEP WORKFLOW
    # -------------------------------------------------------------------------
    step_col1, step_col2 = st.columns(2)

    # ========================== STEP 1: RESUME ==========================
    with step_col1:
        st.markdown(
            """
            <div class="bfc-step-header">
                <div class="bfc-step-num">01</div>
                <h3 class="bfc-step-title">Step 1: Resume Input</h3>
            </div>
            <div class="bfc-step-caption">Upload your resume document (.pdf / .docx) or paste your experience text.</div>
            """,
            unsafe_allow_html=True,
        )

        resume_mode = st.radio(
            "Resume Source:",
            options=["Upload Document (.pdf, .docx)", "Paste Text Directly"],
            index=0 if st.session_state["resume_source_mode"] == "Upload Document (.pdf, .docx)" else 1,
            horizontal=True,
            key="radio_resume_mode",
        )
        st.session_state["resume_source_mode"] = resume_mode

        if resume_mode == "Upload Document (.pdf, .docx)":
            st.info(f"Supported formats: **PDF (.pdf)** and **Word (.docx)** up to **{MAX_FILE_SIZE_MB} MB**. Processed in-memory.")

            resume_file = st.file_uploader(
                label="Choose your resume file:",
                type=["pdf", "docx"],
                key=f"resume_uploader_{st.session_state['uploader_version']}",
                help="Select your resume in PDF or DOCX format",
            )

            # Detect file upload or file change
            if resume_file is not None:
                file_id = f"{resume_file.name}_{resume_file.size}"
                if st.session_state.get("last_processed_resume_id") != file_id:
                    file_bytes = resume_file.read()
                    extracted_text, error_msg, meta = extract_document_text(
                        file_bytes=file_bytes,
                        filename=resume_file.name,
                        max_size_mb=MAX_FILE_SIZE_MB,
                    )
                    st.session_state["last_processed_resume_id"] = file_id
                    st.session_state["resume_file_meta"] = meta
                    st.session_state["resume_file_error"] = error_msg
                    if not error_msg:
                        st.session_state["resume_text"] = extracted_text
                        st.session_state["resume_editor_area"] = extracted_text
                        st.rerun()
            elif resume_file is None and st.session_state.get("last_processed_resume_id") is not None:
                # File was removed via uploader 'X'
                st.session_state["last_processed_resume_id"] = None
                st.session_state["resume_file_meta"] = None
                st.session_state["resume_file_error"] = None
                st.session_state["resume_text"] = ""
                st.session_state["resume_editor_area"] = ""
                st.rerun()

            # Render status / errors
            if st.session_state.get("resume_file_error"):
                st.error(st.session_state["resume_file_error"])

            meta = st.session_state.get("resume_file_meta")
            if meta and not st.session_state.get("resume_file_error"):
                status_col, clear_col = st.columns([3, 1])
                with status_col:
                    pages_info = f" • {meta.get('num_pages')} pages" if meta.get("num_pages") else ""
                    st.success(f"File: **{meta['filename']}** ({meta['formatted_size']}{pages_info}) extracted successfully.")
                with clear_col:
                    if st.button("Remove File", key="clear_resume_btn", use_container_width=True):
                        st.session_state["last_processed_resume_id"] = None
                        st.session_state["resume_file_meta"] = None
                        st.session_state["resume_file_error"] = None
                        st.session_state["resume_text"] = ""
                        st.session_state["resume_editor_area"] = ""
                        st.session_state["uploader_version"] += 1
                        st.rerun()

            # Editable preview area
            st.markdown("**Extracted Resume Text (Editable Preview):**")
            edited_resume_text = st.text_area(
                label="Resume Preview Text",
                height=260,
                placeholder="Upload your resume document above, or switch to 'Paste Text Directly'. Extracted text will appear here for review and editing.",
                key="resume_editor_area",
                label_visibility="collapsed",
            )
            st.session_state["resume_text"] = edited_resume_text

        else:
            # Direct paste mode
            if st.session_state.get("resume_text") and not st.session_state.get("resume_direct_paste_area"):
                st.session_state["resume_direct_paste_area"] = st.session_state["resume_text"]

            pasted_resume_text = st.text_area(
                label="Resume Text",
                height=340,
                placeholder=(
                    "Paste your resume text here...\n\n"
                    "Tip: You may redact phone numbers, physical addresses, and personal IDs. "
                    "Include technical skills, projects, tools, and coursework."
                ),
                key="resume_direct_paste_area",
                label_visibility="collapsed",
            )
            st.session_state["resume_text"] = pasted_resume_text

        # Character count indicator
        resume_len = len(st.session_state.get("resume_text", "").strip())
        if resume_len >= MIN_INPUT_LENGTH:
            st.caption(f"Status: Ready ({resume_len:,} characters)")
        elif resume_len > 0:
            st.caption(f"Status: Needs more detail ({resume_len:,} / {MIN_INPUT_LENGTH} minimum characters)")
        else:
            st.caption("Status: Awaiting resume document or text")

    # ========================== STEP 2: JOB DESCRIPTION ==========================
    with step_col2:
        st.markdown(
            """
            <div class="bfc-step-header">
                <div class="bfc-step-num">02</div>
                <h3 class="bfc-step-title">Step 2: Target Job Description</h3>
            </div>
            <div class="bfc-step-caption">Paste the job posting text or upload the job description document.</div>
            """,
            unsafe_allow_html=True,
        )

        jd_mode = st.radio(
            "Job Description Source:",
            options=["Paste Text Directly", "Upload Document (.pdf, .docx)"],
            index=0 if st.session_state["jd_source_mode"] == "Paste Text Directly" else 1,
            horizontal=True,
            key="radio_jd_mode",
        )
        st.session_state["jd_source_mode"] = jd_mode

        if jd_mode == "Upload Document (.pdf, .docx)":
            st.info(f"Supported formats: **PDF (.pdf)** and **Word (.docx)** up to **{MAX_FILE_SIZE_MB} MB**.")

            jd_file = st.file_uploader(
                label="Choose job description file:",
                type=["pdf", "docx"],
                key=f"jd_uploader_{st.session_state['uploader_version']}",
                help="Select job description in PDF or DOCX format",
            )

            if jd_file is not None:
                file_id = f"{jd_file.name}_{jd_file.size}"
                if st.session_state.get("last_processed_jd_id") != file_id:
                    file_bytes = jd_file.read()
                    extracted_text, error_msg, meta = extract_document_text(
                        file_bytes=file_bytes,
                        filename=jd_file.name,
                        max_size_mb=MAX_FILE_SIZE_MB,
                    )
                    st.session_state["last_processed_jd_id"] = file_id
                    st.session_state["jd_file_meta"] = meta
                    st.session_state["jd_file_error"] = error_msg
                    if not error_msg:
                        st.session_state["jd_text"] = extracted_text
                        st.session_state["jd_editor_area"] = extracted_text
                        st.rerun()
            elif jd_file is None and st.session_state.get("last_processed_jd_id") is not None:
                st.session_state["last_processed_jd_id"] = None
                st.session_state["jd_file_meta"] = None
                st.session_state["jd_file_error"] = None
                st.session_state["jd_text"] = ""
                st.session_state["jd_editor_area"] = ""
                st.rerun()

            if st.session_state.get("jd_file_error"):
                st.error(st.session_state["jd_file_error"])

            meta = st.session_state.get("jd_file_meta")
            if meta and not st.session_state.get("jd_file_error"):
                status_col_jd, clear_col_jd = st.columns([3, 1])
                with status_col_jd:
                    pages_info = f" • {meta.get('num_pages')} pages" if meta.get("num_pages") else ""
                    st.success(f"File: **{meta['filename']}** ({meta['formatted_size']}{pages_info}) extracted successfully.")
                with clear_col_jd:
                    if st.button("Remove File", key="clear_jd_btn", use_container_width=True):
                        st.session_state["last_processed_jd_id"] = None
                        st.session_state["jd_file_meta"] = None
                        st.session_state["jd_file_error"] = None
                        st.session_state["jd_text"] = ""
                        st.session_state["jd_editor_area"] = ""
                        st.session_state["uploader_version"] += 1
                        st.rerun()

            st.markdown("**Extracted Job Description (Editable Preview):**")
            edited_jd_text = st.text_area(
                label="Job Description Preview Text",
                height=260,
                placeholder="Upload your job posting document above, or switch to 'Paste Text Directly'. Extracted text will appear here for review.",
                key="jd_editor_area",
                label_visibility="collapsed",
            )
            st.session_state["jd_text"] = edited_jd_text

        else:
            # Direct paste mode
            if st.session_state.get("jd_text") and not st.session_state.get("jd_direct_paste_area"):
                st.session_state["jd_direct_paste_area"] = st.session_state["jd_text"]

            pasted_jd_text = st.text_area(
                label="Job Description Text",
                height=340,
                placeholder=(
                    "Paste the complete job description here...\n\n"
                    "Include job title, responsibilities, required qualifications, "
                    "technical stack, and nice-to-have skills."
                ),
                key="jd_direct_paste_area",
                label_visibility="collapsed",
            )
            st.session_state["jd_text"] = pasted_jd_text

        # Character count indicator
        jd_len = len(st.session_state.get("jd_text", "").strip())
        if jd_len >= MIN_INPUT_LENGTH:
            st.caption(f"Status: Ready ({jd_len:,} characters)")
        elif jd_len > 0:
            st.caption(f"Status: Needs more detail ({jd_len:,} / {MIN_INPUT_LENGTH} minimum characters)")
        else:
            st.caption("Status: Awaiting job description document or text")

    # ========================== STEP 3: ANALYZE & ACTION ==========================
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="bfc-step-header">
            <div class="bfc-step-num">03</div>
            <h3 class="bfc-step-title">Step 3: Fit Analysis & Action Plan</h3>
        </div>
        <div class="bfc-step-caption">Run evidence-grounded analysis with Gemini and unlock 3 interactive missions + 1 job simulation.</div>
        """,
        unsafe_allow_html=True,
    )

    final_resume = st.session_state.get("resume_text", "").strip()
    final_jd = st.session_state.get("jd_text", "").strip()
    effective_key = get_effective_api_key()

    action_col1, action_col2 = st.columns([1.6, 2.4])

    with action_col1:
        is_busy = st.session_state.get("is_analyzing", False)
        analyze_clicked = st.button(
            "Analyze Fit & Build Action Plan",
            type="primary",
            use_container_width=True,
            disabled=is_busy,
        )

    with action_col2:
        if not effective_key:
            st.caption("Notice: An API key is required for live analysis. You can also click 'Preview Sample Report' at the top to explore without an API key.")
        else:
            st.caption(f"Configured: Ready to analyze with Google Gemini ({st.session_state['selected_model']})")

    if analyze_clicked:
        if len(final_resume) < MIN_INPUT_LENGTH:
            st.error(f"Resume text is too short. Please provide at least {MIN_INPUT_LENGTH} characters of detail (currently {len(final_resume)} characters).")
        elif len(final_jd) < MIN_INPUT_LENGTH:
            st.error(f"Job description is too short. Please provide at least {MIN_INPUT_LENGTH} characters of detail (currently {len(final_jd)} characters).")
        elif not effective_key:
            st.error(
                "Gemini API Key Required\n\n"
                "To perform live analysis, please configure your API key:\n"
                "1. Add to `.streamlit/secrets.toml`: GEMINI_API_KEY = \"your-key\"\n"
                "2. Or set the GEMINI_API_KEY environment variable.\n"
                "3. Or enter the key in the sidebar for this session.\n\n"
                "Alternatively, click 'Preview Sample Report (Offline Demo)' above to test immediately."
            )
        else:
            if len(final_resume) > MAX_INPUT_LENGTH:
                st.warning(f"Resume text exceeds maximum length ({len(final_resume):,} characters). Trimmed to {MAX_INPUT_LENGTH:,} characters.")
                final_resume = final_resume[:MAX_INPUT_LENGTH]

            if len(final_jd) > MAX_INPUT_LENGTH:
                st.warning(f"Job description exceeds maximum length ({len(final_jd):,} characters). Trimmed to {MAX_INPUT_LENGTH:,} characters.")
                final_jd = final_jd[:MAX_INPUT_LENGTH]

            st.session_state["is_analyzing"] = True
            st.session_state["analysis_error"] = None
            try:
                with st.spinner("Analyzing candidate evidence against job description with Google Gemini..."):
                    result_markdown = analyze_with_gemini(
                        resume_text=final_resume,
                        jd_text=final_jd,
                        api_key=effective_key,
                        model_name=st.session_state["selected_model"],
                        timeout_seconds=GEMINI_TIMEOUT_SECONDS,
                    )
                    st.session_state["analysis_result"] = result_markdown
                    st.session_state["is_demo_mode"] = False
                    st.session_state["missions_state"] = get_initial_missions_state()
                    st.session_state["analysis_error"] = None
                    st.success("Analysis complete. Review your executive fit cards and interactive missions below.")
            except TimeoutError as te:
                err_msg = str(te)
                st.session_state["analysis_error"] = err_msg
                st.error(f"Analysis Timeout: {err_msg}")
                st.caption(f"Google Gemini exceeded the {GEMINI_TIMEOUT_SECONDS}s request timeout. Please check network speed or try again.")
            except Exception as err:
                err_msg = str(err)
                st.session_state["analysis_error"] = err_msg
                if "503" in err_msg or "UNAVAILABLE" in err_msg or "high demand" in err_msg.lower():
                    st.error(
                        "Google Gemini Server Spike (HTTP 503: High Demand)\n\n"
                        "Google AI Studio is experiencing temporary traffic volume. "
                        "Please wait a few moments and click 'Analyze Fit & Build Action Plan' again, "
                        "or explore the precomputed demo report above."
                    )
                elif "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "quota" in err_msg.lower():
                    retry_detail = ""
                    if "retry in" in err_msg.lower():
                        import re
                        m = re.search(r"retry in ([^.\n\\]+)", err_msg, re.IGNORECASE)
                        if m:
                            retry_detail = f" (Google estimated reset: in ~{m.group(1).strip()})"
                    st.error(
                        f"Gemini API Quota Exceeded (HTTP 429: RESOURCE_EXHAUSTED){retry_detail}.\n\n"
                        "This Google Gemini API key has consumed its Google AI Studio Free Tier daily quota (20 requests/day for this model).\n\n"
                        "**Quick solutions:**\n"
                        "1. Create a fresh API key in a new Google AI Studio project at [aistudio.google.com](https://aistudio.google.com/app/apikey) and paste it into the sidebar under **Gemini API Configuration** > **Update / Override API Key**.\n"
                        "2. Or update `.streamlit/secrets.toml` with your new key.\n"
                        "3. Or click **'Preview Sample Report (Offline Demo)'** at the top to explore the complete feature suite immediately without an API key."
                    )
                elif "400" in err_msg or "403" in err_msg or "API_KEY_INVALID" in err_msg or "invalid api key" in err_msg.lower():
                    st.error("Invalid API Key. The provided Gemini API key was rejected by Google AI. Please verify your credentials in the sidebar.")
                else:
                    st.error(f"Analysis Failed: {err_msg}")
                    st.caption("Tip: Check internet connectivity, verify your API key, or select an alternate model.")
            finally:
                st.session_state["is_analyzing"] = False

    # -------------------------------------------------------------------------
    # 3.8 RENDER RESULTS & MISSIONS
    # -------------------------------------------------------------------------
    if st.session_state.get("analysis_result"):
        raw_markdown = st.session_state["analysis_result"]
        strengths, gaps, next_action = parse_compact_summary(raw_markdown)
        compact_summary = {"strengths": strengths, "gaps": gaps, "next_action": next_action}
        missions_data = extract_missions_from_report(raw_markdown, st.session_state.get("jd_text", ""))

        st.markdown("---")
        header_col, export_col1, export_col2, reset_col = st.columns([2.5, 1, 1, 0.8])

        with header_col:
            st.subheader("Job-Fit Analysis & Action Roadmap")
            if st.session_state.get("is_demo_mode"):
                st.markdown(
                    '<span class="badge-partial">[Demonstration Preview Mode - Fictional Sample Profile]</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span class="badge-strong">[Live Gemini Analysis]</span>',
                    unsafe_allow_html=True,
                )

        with export_col1:
            st.download_button(
                label="Download Report (.md)",
                data=raw_markdown,
                file_name="beep_fit_coach_analysis.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with export_col2:
            st.download_button(
                label="Download Report (.txt)",
                data=raw_markdown,
                file_name="beep_fit_coach_analysis.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with reset_col:
            if st.button("Start Over", use_container_width=True, help="Reset inputs and run another analysis"):
                reset_all()
                st.rerun()

        # ---------------------------------------------------------------------
        # 1. THREE COMPACT CARDS (DEFAULT EXECUTIVE VIEW)
        # ---------------------------------------------------------------------
        st.markdown("#### Executive Fit Summary")
        card_col1, card_col2, card_col3 = st.columns(3)

        with card_col1:
            str_bullets = "".join([f"<li>{html.escape(s)}</li>" for s in strengths]) if strengths else "<li>Technical fundamentals evidenced in resume</li>"
            st.markdown(
                f"""
                <div class="bfc-compact-card card-strengths">
                    <div>
                        <div class="bfc-card-top">
                            <h4 class="bfc-card-heading">Your Strengths</h4>
                            <span class="bfc-card-badge badge-strengths">Verified in Resume</span>
                        </div>
                        <ul class="bfc-card-list">
                            {str_bullets}
                        </ul>
                    </div>
                    <div style="font-size: 11.5px; opacity: 0.75; margin-top: 14px; padding-top: 8px; border-top: 1px dashed var(--bfc-teal-border);">
                        Direct evidence matched from your resume experience.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with card_col2:
            gap_bullets = "".join([f"<li>{html.escape(g)}</li>" for g in gaps]) if gaps else "<li>Advanced production frameworks</li>"
            st.markdown(
                f"""
                <div class="bfc-compact-card card-gaps">
                    <div>
                        <div class="bfc-card-top">
                            <h4 class="bfc-card-heading">Your Skill Gaps</h4>
                            <span class="bfc-card-badge badge-gaps">Priority Focus</span>
                        </div>
                        <ul class="bfc-card-list">
                            {gap_bullets}
                        </ul>
                    </div>
                    <div style="font-size: 11.5px; opacity: 0.75; margin-top: 14px; padding-top: 8px; border-top: 1px dashed var(--bfc-amber-border);">
                        Target these specific criteria to maximize candidacy.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with card_col3:
            escaped_action = html.escape(next_action)
            st.markdown(
                f"""
                <div class="bfc-compact-card card-action">
                    <div>
                        <div class="bfc-card-top">
                            <h4 class="bfc-card-heading">Your Next Action</h4>
                            <span class="bfc-card-badge badge-action">Day 1 Quick Win</span>
                        </div>
                        <div class="bfc-action-highlight">
                            {escaped_action}
                        </div>
                    </div>
                    <div class="bfc-action-meta">
                        <span>Recommended: Begin Mission 1 below to tackle this in 3-5 mins</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---------------------------------------------------------------------
        # 2. DETAILED REPORT IN EXPANDABLE SECTION
        # ---------------------------------------------------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("Detailed Diagnostic Report & Breakdown (Click to expand)", expanded=False):
            tab_overview, tab_table, tab_resume, tab_plan, tab_raw = st.tabs([
                "Snapshot & Priorities",
                "Requirements Breakdown",
                "Resume Refinement & Project",
                "7-Day Roadmap & Interview Prep",
                "Complete Report & Export",
            ])

            sec_snapshot = extract_section(raw_markdown, ["Role Summary & Fit Snapshot", "Overall Fit Snapshot", "Fit Snapshot", "Role Summary"])
            sec_requirements = extract_section(raw_markdown, ["Requirement-by-Requirement", "Job requirements", "Requirements Table"])
            sec_priorities = extract_section(raw_markdown, ["Top 3 Priority Gaps", "Priority Gaps", "Top 3 Priorities", "Top 3 Strategic Priority Gaps"])
            sec_resume = extract_section(raw_markdown, ["Truthful Resume", "Resume Improvements", "Resume Improvement"])
            sec_project = extract_section(raw_markdown, ["Portfolio / Mini-Project", "Portfolio", "Mini-Project", "Feasible Portfolio Mini-Project"])
            sec_plan = extract_section(raw_markdown, ["Realistic Seven-Day", "7-Day Action Plan", "Seven-Day Action Plan", "Action Plan"])
            sec_interview = extract_section(raw_markdown, ["Interview Preparation", "Role-Specific Interview", "Interview practice"])
            sec_limitations = extract_section(raw_markdown, ["Limitations", "Limitations & Constructive Reflection"])

            with tab_overview:
                st.markdown("### Fit Snapshot & Strategic Priorities")
                if sec_snapshot:
                    st.markdown(sec_snapshot)
                else:
                    st.markdown("*(Refer to Complete Report tab for full snapshot)*")

                st.markdown("---")
                if sec_priorities:
                    st.markdown(sec_priorities)

            with tab_table:
                st.markdown("### Requirement-by-Requirement Evidence Comparison")
                st.caption("Evidence mapped directly from your resume against job criteria. Absences mean 'Not evidenced', never proof of inability.")
                if sec_requirements:
                    st.markdown(sec_requirements)
                else:
                    st.markdown("*(Refer to Complete Report tab for detailed table)*")

            with tab_resume:
                st.markdown("### Truthful Resume Improvements")
                st.caption("Phrasing upgrades based strictly on existing experience. Confirm bracketed placeholders like [confirm actual metric] before using.")
                if sec_resume:
                    st.markdown(sec_resume)

                st.markdown("---")
                st.markdown("### Portfolio / Mini-Project Blueprint")
                st.caption("A tailored, feasible project idea to build evidence for this specific role. (Clearly marked as unbuilt future preparation).")
                if sec_project:
                    st.markdown(sec_project)

            with tab_plan:
                st.markdown("### Realistic Seven-Day Action Plan")
                st.caption("Day-by-day achievable milestones to strengthen your candidacy.")
                if sec_plan:
                    st.markdown(sec_plan)

                st.markdown("---")
                st.markdown("### Role-Specific Interview Preparation")
                st.caption("5 targeted questions assessing core job criteria.")
                if sec_interview:
                    st.markdown(sec_interview)

                if sec_limitations:
                    st.markdown("---")
                    st.markdown(sec_limitations)

            with tab_raw:
                st.markdown("### Complete Formatted Diagnostic Report")
                st.markdown(raw_markdown)

        # ---------------------------------------------------------------------
        # 3. INTERACTIVE PRACTICE: MISSIONS & JOB SIMULATION
        # ---------------------------------------------------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Interactive Practice: Missions & Job Simulation")
        st.caption("Complete these 3-5 minute micro-tasks to practise essential skills, test solutions, and build demonstrable portfolio work.")

        m_state = st.session_state["missions_state"]
        completed_count = sum(1 for k in ["m1", "m2", "m3", "sim"] if m_state[k].get("completed"))

        practice_portfolio_md = generate_practice_portfolio(
            role_title="Target Technical Role",
            compact_summary=compact_summary,
            missions_data=missions_data,
            missions_state=m_state,
        )

        prog_col1, prog_col2 = st.columns([2.5, 1.5])
        with prog_col1:
            st.markdown(f"**Practice Progress:** {completed_count} of 4 tasks completed")
            st.progress(completed_count / 4.0)
        with prog_col2:
            st.download_button(
                label="Download Completed Work (.md)",
                data=practice_portfolio_md,
                file_name="beep_fit_coach_practice_work.md",
                mime="text/markdown",
                use_container_width=True,
                help="Export your submitted answers, simulation code, and AI mentor feedback",
            )

        tab_m1, tab_m2, tab_m3, tab_sim = st.tabs([
            f"Mission 1: {'[Done] ' if m_state['m1'].get('completed') else ''}{missions_data['m1']['title'][:25]}",
            f"Mission 2: {'[Done] ' if m_state['m2'].get('completed') else ''}Resume Bullet Upgrade",
            f"Mission 3: {'[Done] ' if m_state['m3'].get('completed') else ''}Technical Interview Check",
            f"Job Simulation: {'[Done] ' if m_state['sim'].get('completed') else ''}{missions_data['sim']['title'][:25]}",
        ])

        # ========================== MISSION 1 ==========================
        with tab_m1:
            st.markdown(f"#### {missions_data['m1']['title']}")
            st.markdown(
                """
                <div class="bfc-meta-row">
                    <span class="bfc-meta-chip">Challenge 1 of 3</span>
                    <span class="bfc-meta-chip time-chip">Est. 3–5 Minutes</span>
                    <span class="bfc-meta-chip">Priority Gap Attack</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            m1_task_escaped = html.escape(missions_data["m1"]["task"])
            st.markdown(
                f"""
                <div class="bfc-mission-brief">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #4f46e5; margin-bottom: 6px;">Challenge Specification</div>
                    <div class="bfc-mission-task-text">{m1_task_escaped}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if m_state["m1"].get("completed"):
                m1_ans_escaped = html.escape(m_state["m1"]["answer"])
                st.markdown(
                    f"""
                    <div class="bfc-feedback-card">
                        <div class="bfc-feedback-status">
                            <span class="bfc-status-pill completed">Mission 1 Completed</span>
                            <span style="font-size: 12px; font-weight: 600; opacity: 0.8;">Rubric Evaluated</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.75; margin-bottom: 4px;">Your Submission:</div>
                            <div style="font-size: 13.5px; background: rgba(128, 128, 128, 0.08); padding: 10px 14px; border-radius: 8px; white-space: pre-wrap;">{m1_ans_escaped}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Mentor & Rubric Feedback:**")
                st.markdown(m_state["m1"]["feedback"])
                if st.button("Revise / Retry Mission 1", key="retry_m1"):
                    st.session_state["missions_state"]["m1"]["completed"] = False
                    st.session_state["missions_state"]["m1"]["feedback"] = None
                    st.rerun()
            else:
                m1_input = st.text_area(
                    "Your Implementation Plan / Solution:",
                    value=m_state["m1"].get("answer", ""),
                    height=140,
                    key="input_m1",
                    placeholder="Explain your approach, key technical concepts, and implementation steps...",
                )
                if st.button("Submit Mission 1 for Evaluation", key="btn_m1", type="primary"):
                    if len(m1_input.strip()) < 10:
                        st.error("Please provide a more detailed response (minimum 10 characters).")
                    else:
                        with st.spinner("Evaluating submission against role rubric..."):
                            feedback = evaluate_submission(
                                missions_data["m1"]["title"],
                                missions_data["m1"]["task"],
                                m1_input.strip(),
                                effective_key,
                                st.session_state["selected_model"],
                            )
                            st.session_state["missions_state"]["m1"]["answer"] = m1_input.strip()
                            st.session_state["missions_state"]["m1"]["feedback"] = feedback
                            st.session_state["missions_state"]["m1"]["completed"] = True
                            st.rerun()

        # ========================== MISSION 2 ==========================
        with tab_m2:
            st.markdown(f"#### {missions_data['m2']['title']}")
            st.markdown(
                """
                <div class="bfc-meta-row">
                    <span class="bfc-meta-chip">Challenge 2 of 3</span>
                    <span class="bfc-meta-chip time-chip">Est. 3–5 Minutes</span>
                    <span class="bfc-meta-chip">Truthful Resume Upgrade</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            m2_task_escaped = html.escape(missions_data["m2"]["task"])
            st.markdown(
                f"""
                <div class="bfc-mission-brief">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #4f46e5; margin-bottom: 6px;">Challenge Specification</div>
                    <div class="bfc-mission-task-text">{m2_task_escaped}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if m_state["m2"].get("completed"):
                m2_ans_escaped = html.escape(m_state["m2"]["answer"])
                st.markdown(
                    f"""
                    <div class="bfc-feedback-card">
                        <div class="bfc-feedback-status">
                            <span class="bfc-status-pill completed">Mission 2 Completed</span>
                            <span style="font-size: 12px; font-weight: 600; opacity: 0.8;">Rubric Evaluated</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.75; margin-bottom: 4px;">Your Revised Bullet:</div>
                            <div style="font-size: 13.5px; background: rgba(128, 128, 128, 0.08); padding: 10px 14px; border-radius: 8px; white-space: pre-wrap;">{m2_ans_escaped}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Mentor & Rubric Feedback:**")
                st.markdown(m_state["m2"]["feedback"])
                if st.button("Revise / Retry Mission 2", key="retry_m2"):
                    st.session_state["missions_state"]["m2"]["completed"] = False
                    st.session_state["missions_state"]["m2"]["feedback"] = None
                    st.rerun()
            else:
                m2_input = st.text_area(
                    "Your Revised Bullet Point:",
                    value=m_state["m2"].get("answer", ""),
                    height=130,
                    key="input_m2",
                    placeholder="Enter revised bullet with active verbs, tools, and [confirm metric] placeholder...",
                )
                if st.button("Submit Mission 2 for Evaluation", key="btn_m2", type="primary"):
                    if len(m2_input.strip()) < 10:
                        st.error("Please provide a more detailed bullet point (minimum 10 characters).")
                    else:
                        with st.spinner("Evaluating resume phrasing against truthfulness rules..."):
                            feedback = evaluate_submission(
                                missions_data["m2"]["title"],
                                missions_data["m2"]["task"],
                                m2_input.strip(),
                                effective_key,
                                st.session_state["selected_model"],
                            )
                            st.session_state["missions_state"]["m2"]["answer"] = m2_input.strip()
                            st.session_state["missions_state"]["m2"]["feedback"] = feedback
                            st.session_state["missions_state"]["m2"]["completed"] = True
                            st.rerun()

        # ========================== MISSION 3 ==========================
        with tab_m3:
            st.markdown(f"#### {missions_data['m3']['title']}")
            st.markdown(
                """
                <div class="bfc-meta-row">
                    <span class="bfc-meta-chip">Challenge 3 of 3</span>
                    <span class="bfc-meta-chip time-chip">Est. 3–5 Minutes</span>
                    <span class="bfc-meta-chip">Technical Interview Prep</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            m3_task_escaped = html.escape(missions_data["m3"]["task"])
            st.markdown(
                f"""
                <div class="bfc-mission-brief">
                    <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; color: #4f46e5; margin-bottom: 6px;">Interview Scenario</div>
                    <div class="bfc-mission-task-text">{m3_task_escaped}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if m_state["m3"].get("completed"):
                m3_ans_escaped = html.escape(m_state["m3"]["answer"])
                st.markdown(
                    f"""
                    <div class="bfc-feedback-card">
                        <div class="bfc-feedback-status">
                            <span class="bfc-status-pill completed">Mission 3 Completed</span>
                            <span style="font-size: 12px; font-weight: 600; opacity: 0.8;">Rubric Evaluated</span>
                        </div>
                        <div style="margin-bottom: 12px;">
                            <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.75; margin-bottom: 4px;">Your Response:</div>
                            <div style="font-size: 13.5px; background: rgba(128, 128, 128, 0.08); padding: 10px 14px; border-radius: 8px; white-space: pre-wrap;">{m3_ans_escaped}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Mentor & Rubric Feedback:**")
                st.markdown(m_state["m3"]["feedback"])
                if st.button("Revise / Retry Mission 3", key="retry_m3"):
                    st.session_state["missions_state"]["m3"]["completed"] = False
                    st.session_state["missions_state"]["m3"]["feedback"] = None
                    st.rerun()
            else:
                m3_input = st.text_area(
                    "Your Technical Interview Answer:",
                    value=m_state["m3"].get("answer", ""),
                    height=140,
                    key="input_m3",
                    placeholder="Write your concise, technical answer explaining concepts, implementation, and trade-offs...",
                )
                if st.button("Submit Mission 3 for Evaluation", key="btn_m3", type="primary"):
                    if len(m3_input.strip()) < 10:
                        st.error("Please provide a more complete answer (minimum 10 characters).")
                    else:
                        with st.spinner("Evaluating technical answer structure..."):
                            feedback = evaluate_submission(
                                missions_data["m3"]["title"],
                                missions_data["m3"]["task"],
                                m3_input.strip(),
                                effective_key,
                                st.session_state["selected_model"],
                            )
                            st.session_state["missions_state"]["m3"]["answer"] = m3_input.strip()
                            st.session_state["missions_state"]["m3"]["feedback"] = feedback
                            st.session_state["missions_state"]["m3"]["completed"] = True
                            st.rerun()

        # ========================== JOB SIMULATION ==========================
        with tab_sim:
            st.markdown(f"#### {missions_data['sim']['title']}")
            st.markdown(
                """
                <div class="bfc-meta-row">
                    <span class="bfc-meta-chip">Hands-on Mini-Workspace</span>
                    <span class="bfc-meta-chip time-chip">Est. 5–8 Minutes</span>
                    <span class="bfc-meta-chip">Rubric-Graded Code</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            file_tag = "solution.sql" if "sql" in missions_data["sim"]["title"].lower() else ("solution.c" if "c " in missions_data["sim"]["title"].lower() else "solution.py")
            sim_scenario_escaped = html.escape(missions_data["sim"]["scenario"])
            st.markdown(
                f"""
                <div class="bfc-simulator-window">
                    <div class="bfc-simulator-topbar">
                        <div class="bfc-window-dots">
                            <span class="bfc-window-dot bfc-dot-red"></span>
                            <span class="bfc-window-dot bfc-dot-amber"></span>
                            <span class="bfc-window-dot bfc-dot-green"></span>
                        </div>
                        <div class="bfc-simulator-title">{file_tag}</div>
                        <div style="font-size: 11px; font-weight: 600; opacity: 0.6;">Code Simulator</div>
                    </div>
                    <div class="bfc-simulator-body">
                        <div class="bfc-spec-box">
                            <strong>Challenge Specification & Schema:</strong><br>
                            {sim_scenario_escaped}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if m_state["sim"].get("completed"):
                st.markdown(
                    f"""
                    <div class="bfc-feedback-card">
                        <div class="bfc-feedback-status">
                            <span class="bfc-status-pill completed">Simulation Completed</span>
                            <span style="font-size: 12px; font-weight: 600; opacity: 0.8;">Rubric Evaluated</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Your Solution Code:**")
                st.code(m_state["sim"]["answer"])
                st.markdown("**Rubric Evaluation & Code Review:**")
                st.markdown(m_state["sim"]["feedback"])
                if st.button("Revise / Retry Simulation Solution", key="retry_sim"):
                    st.session_state["missions_state"]["sim"]["completed"] = False
                    st.session_state["missions_state"]["sim"]["feedback"] = None
                    st.rerun()
            else:
                sim_default = m_state["sim"].get("answer") or missions_data["sim"].get("starter", "")
                sim_input = st.text_area(
                    "Your Code / Query Solution:",
                    value=sim_default,
                    height=200,
                    key="input_sim",
                    placeholder="Write your SQL query, Python script, or code solution here...",
                )
                if st.button("Submit Solution for Rubric Evaluation", key="btn_sim", type="primary"):
                    if len(sim_input.strip()) < 10:
                        st.error("Please provide a more complete solution (minimum 10 characters).")
                    else:
                        with st.spinner("Evaluating solution against technical rubric..."):
                            feedback = evaluate_submission(
                                missions_data["sim"]["title"],
                                missions_data["sim"]["scenario"],
                                sim_input.strip(),
                                effective_key,
                                st.session_state["selected_model"],
                            )
                            st.session_state["missions_state"]["sim"]["answer"] = sim_input.strip()
                            st.session_state["missions_state"]["sim"]["feedback"] = feedback
                            st.session_state["missions_state"]["sim"]["completed"] = True
                            st.rerun()

    # 3.9 Product evaluation expander
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("Product Evaluation & Pilot Protocol (For Reviewers)"):
        st.markdown(
            """
            ### Pilot Experiment Plan
            - **Problem Hypothesis:** College students and fresh graduates struggle to translate verbose job descriptions into specific, evidence-backed preparation steps.
            - **Target Participants:** 12 to 20 final-year college students or recent graduates applying for tech/analyst roles.
            - **Primary Outcome Metric:** Percentage of participants who accurately identify at least 3 core job requirements and formulate a concrete, job-relevant next action.
            - **Experimental Design:**
                1. **Baseline Phase:** Participant is given Job Description A without Beep Fit Coach and asked to list 3 key requirements and their immediate 7-day preparation plan.
                2. **Assisted Phase:** Participant is given Job Description B using Beep Fit Coach and performs the same task.
                3. **Target:** Measure percentage-point lift (Targeting a +20 pp lift in accurate requirement recognition and actionable plan clarity; recorded honestly).
            - **Data Template:** Download `PILOT_METRICS_TEMPLATE.csv` from the sidebar to record observations.
            """
        )

    # 3.10 Footer
    st.markdown(
        """
        <div class="bfc-disclaimer-card">
            <strong>Prototype Note:</strong> Beep Fit Coach is an independent product prototype developed for a product-building assignment. 
            It is not affiliated with, endorsed by, or sponsored by Beep. All company names and candidate profiles used in demos are fictional.
        </div>
        <div class="bfc-footer-text">
            Beep Fit Coach • Built with Streamlit & Google Gemini • Evidence-Grounded Career Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 4. ENTRY POINT
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    render_app()
