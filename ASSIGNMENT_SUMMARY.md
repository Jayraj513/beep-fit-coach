# Assignment Summary: Beep Fit Coach

## 1. Problem Explored
Indian college students, final-year engineering/CS undergraduates, and recent graduates face high friction when applying for internships and entry-level technical roles. Job descriptions are often lengthy, jargon-dense, and intimidating. Students struggle to determine:
- Which requirements their college coursework and academic projects actually substantiate.
- Which requirements are genuine hard prerequisites vs. aspirational "nice-to-haves."
- What concrete, high-ROI actions they should take over the coming week to bridge demonstrable gaps.

*Hypothesis vs. Fact:* This is treated as a working hypothesis to validate through structured experimentation, not an assumed universal truth.

---

## 2. Why Beep Fit Coach Was Chosen
Rather than building another generic resume builder or an algorithmic "ATS keyword optimizer" (which frequently encourages resume fraud or arbitrary "fit scores"), **Beep Fit Coach** acts as an objective, evidence-based career coach. It provides:
1. **Radical Truthfulness:** Unmentioned skills are labeled as *"Not evidenced in the provided resume"*, never as proof of inability.
2. **Zero Fake Percentages:** Replaces deceptive "You are 72% ready!" scores with qualitative rubrics and boundary explanations.
3. **Actionable Velocity:** Bridges the gap between diagnosis and preparation by generating a custom 7-day action plan, truthful phrasing upgrades with placeholders, and a tailored mini-project blueprint.

---

## 3. How the Application Works
```
+-----------------------------------------------------------------------------------+
|                                 USER INPUT                                        |
|  - Resume text (projects, coursework, tools)                                      |
|  - Job Description (responsibilities, required qualifications)                   |
|  - (Or 1-Click Sample Profile for instant demonstration)                          |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                           SERVER-SIDE GOOGLE GEMINI                               |
|  - SDK: google-genai (Model: gemini-2.5-flash / gemini-2.0-flash / 1.5-flash)     |
|  - Secure key management (Streamlit secrets / env var / session override)         |
|  - Strict system prompt enforcing factual grounding & no hallucination           |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|                        STRUCTURED DIAGNOSTIC REPORT                               |
|  1. Fit Snapshot: Qualitative assessment & rubric scope                           |
|  2. Requirements Table: Requirement | Importance | Evidence Quote | Status | Action |
|  3. Top 3 Strategic Priority Gaps: Why it matters + tangible output to produce    |
|  4. Truthful Resume Improvements: Bullet rewrites with [metric placeholders]      |
|  5. Portfolio Mini-Project Blueprint: Feasible project matching the tech stack    |
|  6. Realistic 7-Day Action Plan: Daily time estimates & completion checklist      |
|  7. Role-Specific Interview Preparation: 5 likely questions & evaluation points   |
|  8. Scope Limitations & Self-Reflection                                           |
+-----------------------------------------------------------------------------------+
```

---

## 4. How AI Was Used During Development & In-App
- **During Development:** AI was leveraged to architect clean Streamlit interfaces, design rigorous multi-step prompt specifications, write realistic fictional test personas (Data Analyst & AI/ML Interns), and establish thorough testing protocols.
- **In-App Inference:** The official Google Gen AI Python SDK (`google-genai`) powers live analysis using `gemini-2.5-flash`. The prompt enforces factual grounding, strictly limits inferences to provided text, forbids invented qualifications, and formats results into clean, parseable Markdown.

---

## 5. Primary Metric & Proposed 7-Day Experiment
- **Primary Metric:** Percentage of student participants who correctly identify at least 3 critical job requirements and commit to a concrete, demonstrable preparation action.
- **Proposed Pilot:** 12–20 students tested in a pre/post setup:
  - *Baseline (Unassisted):* Analyze a job description without the tool and propose a 7-day plan.
  - *Tool-Assisted (Beep Fit Coach):* Analyze a comparable job description with the app.
  - *Target:* +20 percentage-point improvement in identifying top requirements and selecting a concrete next action (target to evaluate, not a claimed outcome).
  - *Tracking:* Provided via [`PILOT_METRICS_TEMPLATE.csv`](file:///d:/beep/Beep_Fit_Coach_Starter/PILOT_METRICS_TEMPLATE.csv).

---

## 6. Implementation Status vs. Hypothesis

| Dimension | Implemented & Verified in Prototype | Remains a Working Hypothesis / Future Scope |
|---|---|---|
| **Core Workflow** | 3-step structured workflow, in-memory PDF/DOCX extraction (via `pypdf` & `python-docx`), editable previews, 1-click presets, Gemini API integration, and 5 structured tabs. | Real-time GitHub repository scanning and code-level commit verification. |
| **Safety & Truthfulness** | Strict absence labeling ("Not evidenced"), no fake scores, placeholders for unverified metrics, explicit vs inferred requirement separation. | Real-time dynamic interview voice interaction. |
| **Demo Capabilities** | 1-click fictional presets and an offline demo report for instant evaluation without an API key. | Live multi-student pilot execution with 20 college participants. |
| **Security & Privacy** | Ephemeral in-memory processing (zero disk retention), secrets masked in UI, `.gitignore` protection. | OAuth-based multi-user workspace accounts. |
