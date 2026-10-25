# Product Notes: Beep Fit Coach

## 1. Executive Summary & Strategic Context
**Product Name:** Beep Fit Coach  
**Tagline:** Turn job descriptions into your next career move.  
**Core Value Proposition:** An evidence-based diagnostic tool that transforms complex, intimidating job descriptions into an honest skills-gap analysis and an achievable 7-day preparation roadmap.

---

## 2. Working Hypothesis & Target Persona

### The Working Hypothesis
> *Hypothesis to Validate:* Indian college students, final-year engineering/CS undergraduates, and recent graduates applying for internships and entry-level tech roles struggle to translate lengthy job descriptions into a clear, prioritized action plan.
> 
> Specifically, students often:
> 1. Misinterpret job descriptions as rigid checklists rather than flexible competency guidelines.
> 2. Experience "imposter syndrome" when faced with 10+ bullet points, failing to distinguish between core hard requirements and "nice-to-haves."
> 3. Cannot accurately map what parts of their college projects or coursework provide legitimate evidence for the role.
> 4. Default to generic, unproductive actions (e.g., re-watching broad 40-hour tutorial playlists) rather than producing demonstrable project artifacts or solving targeted problems.

*Critical Product Caveat:* This is a hypothesis formulated for exploration in a product-building prototype. It is not an established fact across all Beep users, and no fabricated surveys or claims about Beep are made.

### Target User Persona
- **Name:** "Anand" (Representative Archetype)
- **Profile:** Final-year B.Tech Information Technology student at a Tier-2/Tier-3 engineering college in India.
- **Current State:** Has completed basic coursework in DBMS and Python; built 1–2 academic projects (e.g., college management system, basic exploratory data analysis on Kaggle).
- **Core Friction:** Sees a "Data Analyst Intern" job description listing SQL, Window Functions, Tableau, PowerBI, A/B Testing, and Git. Anand feels underqualified, cannot tell how his academic projects stack up, and doesn't know whether to rewrite his resume, learn Tableau, or grind LeetCode.
- **Desired Outcome:** An objective, encouraging breakdown showing: *"Here is what your resume already proves (Python, basic SQL); here is what is not evidenced (Tableau, Window functions); and here is a 7-day checklist to bridge that gap."*

---

## 3. Core User Experience & Journey
```
[1. Land on Home Screen]
       │
       ▼
[2. Review Privacy & Evidence Guarantee]
       │
       ▼
[3. Input Resume & Target Job Description]
  (or 1-Click Load Sample Profile for Demo)
       │
       ▼
[4. Server-Side Gemini Evidence Comparison]
       │
       ▼
[5. Structured Diagnostic Report]
  ├── A. Qualitative Fit Snapshot (No fake hiring scores)
  ├── B. Requirement-by-Requirement Table (Green / Amber / Grey)
  ├── C. Top 3 Strategic Priorities (High-ROI gaps)
  ├── D. Truthful Resume Improvements (Phrasing upgrades with placeholders)
  ├── E. Tailored Mini-Project Blueprint (Feasible, unbuilt evidence piece)
  ├── F. Realistic 7-Day Action Plan (Measurable daily deliverables)
  ├── G. 5 Likely Interview Questions (What interviewers assess)
  └── H. Honest Limitations & Reflection
       │
       ▼
[6. Export & Execution]
  └── Download Markdown report, follow daily checklist, prepare with confidence.
```

---

## 4. Trust, Safety, and Ethical AI Choices

1. **"Not Evidenced" vs. "Lacks Ability":**
   - The system prompt explicitly enforces that an unmentioned skill in a resume is classified strictly as *"Not evidenced in the provided resume"*, never as proof of personal incompetence.
2. **Zero Fake Readiness Scores:**
   - Conventional AI career tools generate arbitrary, misleading percentages (e.g., *"You are 68% ready!"*). This misleads students and creates false hope or anxiety. Beep Fit Coach uses qualitative rubrics: **Strong Evidence**, **Partial Evidence**, or **Not Enough Evidence to Assess**, accompanied by clear boundary explanations.
3. **No Fabricated Resume Achievements:**
   - Hallucination prevention is paramount. The AI is strictly instructed to avoid inventing metrics, past employers, or certifications. When phrasing improvements are suggested, bracketed placeholders like `[confirm actual metric, e.g., 20%]` are used.
4. **Data Privacy & Server-Side Execution:**
   - No permanent database storage or full text logging of user resumes or job descriptions.
   - Processing is ephemeral and server-side.
   - Users are prompted to redact phone numbers, physical addresses, and national ID numbers.
5. **Clear Brand Independence:**
   - Prominently labeled as an independent product prototype for an assignment, not affiliated with or endorsed by Beep.

---

## 5. Product Validation: Proposed 7-Day Pilot Experiment

### Objective
Measure whether Beep Fit Coach produces a statistically meaningful improvement in students' ability to identify core job requirements and choose a high-impact next action.

### Primary Outcome Metric
> **Metric:** *Percentage of participants who correctly identify at least 3 critical job requirements and commit to a concrete, demonstrable preparation action.*
> 
> **Target Lift:** +20 percentage points over unassisted baseline (Target to test, not a claimed historical result).

### Pilot Methodology (Within-Subjects or A/B Protocol)
- **Sample Size:** 12 to 20 final-year college students or recent graduates.
- **Task 1 (Baseline - Unassisted):** 
  - Participant is provided a real entry-level tech job description (e.g., Data Analyst Intern).
  - Without any AI tool, participant is asked:
    1. *"What are the top 3 technical requirements for this role?"*
    2. *"What specific project or learning step will you complete in the next 7 days to prepare?"*
  - An independent evaluator records whether requirements are accurate and whether the action is specific (e.g., *"Build an interactive Tableau dashboard on Kaggle churn data"* vs. vague *"Learn data science"*).
- **Task 2 (Assisted - Beep Fit Coach):**
  - Participant is provided a comparable job description and their current resume.
  - Participant runs Beep Fit Coach and answers the same questions.
- **Evaluation Criteria:**
  - Accuracy of requirement identification (0 or 1).
  - Concreteness of selected next action (0 = vague tutorial watching, 1 = specific deliverable with completion criteria).
  - Time to decision (minutes).
  - Self-reported confidence score (1 to 5 scale).
- **Tracking Asset:** Standardized template provided in [`PILOT_METRICS_TEMPLATE.csv`](file:///d:/beep/Beep_Fit_Coach_Starter/PILOT_METRICS_TEMPLATE.csv).

---

## 6. Technology Stack & AI Architecture
- **Frontend / Framework:** Streamlit (Python 3.12) with custom career-tech UI styling, responsive containers, and semantic tab navigation.
- **LLM SDK:** Official Google Gen AI Python SDK (`google-genai`).
- **Core Model:** `gemini-2.5-flash` (with automated fallback to `gemini-2.0-flash` and `gemini-1.5-flash`).
- **Configuration Security:** Key resolution via `.streamlit/secrets.toml` -> `os.getenv("GEMINI_API_KEY")` -> secure session state input.
- **Data Export:** Clean Markdown (.md) and plain text export.

---

## 7. Future Product Roadmap (Post-Validation)
1. **GitHub / Project Repository Analyzer:** Automatically inspect public GitHub repositories to extract verifiable code evidence (e.g., commit history, SQL queries, FastAPI routes) rather than relying solely on resume text.
2. **Interactive Mock Interview Simulator:** Voice- or text-based follow-up simulating the 5 generated interview questions with instant critique.
3. **LinkedIn / PDF Resume Parser:** Direct PDF upload with automated PII scrubbing prior to model inference.
