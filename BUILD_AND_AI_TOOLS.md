# Beep Fit Coach — Build & AI Tools Explanation (One-Pager)

**Product:** Beep Fit Coach — *Turn job descriptions into your next career move.*  
**Author / Candidate:** Product Building Assignment  
**Target Audience:** Indian college students, engineering/CS undergraduates, and entry-level job seekers.

---

## 1. Problem Context & Core Hypothesis
College students often struggle to translate complex, verbose job descriptions into focused preparation. When reading job postings, students frequently:
1. **Misinterpret requirements as rigid all-or-nothing checklists**, inducing imposter syndrome.
2. **Struggle to map coursework and academic projects** to industry criteria.
3. **Default to broad, passive video tutorial playlists** rather than building verifiable artifacts.

**Beep Fit Coach** bridges this gap by transforming any job description and resume into:
- An evidence-based skills comparison (labeling missing items strictly as *"Not evidenced"*, never as inability).
- Zero fake hiring percentages (qualitative rubrics with transparent scope).
- A concrete, feasible **7-day preparation roadmap** and tailored **portfolio mini-project blueprint**.

---

## 2. Technical Architecture & Build

```
[User Document: PDF / DOCX / Paste] ──> [In-Memory Extractor: pypdf / python-docx]
                                                          │
                                            (Editable Preview & Validation)
                                                          │
[User Target Job Description] ──────────────> [Prompt Assembler]
                                                          │
                                       (Strict Grounding & Anti-Hallucination)
                                                          │
                                           [Google Gemini API: 2.5-flash]
                                                          │
              ┌───────────────────────────────────────────┴───────────────────────────────────────────┐
              ▼                                                                                       ▼
[Default View: 3 Compact Cards]                                                       [Interactive Practice Workspace]
  - Your Strengths (Evidenced skills)                                                   - Mission 1: Technical Gap Attack
  - Your Skill Gaps (High-ROI areas)                                                    - Mission 2: Truthful Bullet Upgrade
  - Your Next Action (Day 1 execution)                                                  - Mission 3: Interview Technical Check
              │                                                                         - Job Simulation: Hands-on Code/SQL
              ▼                                                                                       │
[Expandable Section: 5 Detailed Tabs]                                                                 ▼
  - Breakdown table, rewrites, blueprint, plan                                        [Downloadable Practice Work (.md)]
```

- **Frontend & Workflow:** Streamlit with adaptive CSS design tokens (full dark/light mode compatibility), a 3-step structured workflow, 3 compact cards as default view, an expandable detailed diagnostic section, 3 interactive missions, 1 job simulation, and 1-click sample presets.
- **Interactive Practice & Job Simulation:** Hands-on micro-tasks (3–5 min each) and role-specific coding/data challenge with instant Gemini rubric evaluation, retry support, session-state progress tracking, and downloadable portfolio practice work.
- **Document Processing:** Custom memory-safe extractor (`document_parser.py`) supporting `.pdf` (via `pypdf`) and `.docx` (via `python-docx`). Includes automatic detection of password-protected PDFs, corrupted files, and scanned image-only PDFs with guidance that OCR is required.
- **Data Privacy & Security:** Resumes and job descriptions are processed ephemerally in-memory; no files are saved to server disk or permanent databases. API keys are resolved securely via `.streamlit/secrets.toml` or environment variables and never logged or exposed.

---

## 3. How AI Tools Were Leveraged

### A. AI Used During Development
- **Architectural Scaffolding:** Used LLM pair-programming to design clean Streamlit component abstractions, session-state management, and edge-case handling for multi-format document parsing.
- **Prompt Engineering & Grounding Rules:** Formulated strict multi-stage prompt specifications forbidding fabricated resume metrics, enforcing placeholders like `[confirm actual metric]`, and mandating qualitative rubrics.
- **Synthetic Test Personas:** Generated realistic, representative student profiles (e.g. final-year B.Tech student with basic SQL/Python projects applying for a FinTech Data Analyst Intern role) for automated and offline testing.

### B. AI Used In-App (Runtime)
- **Model:** Google Gemini (`gemini-2.5-flash` with automatic fallback to `gemini-2.0-flash` and `gemini-1.5-flash`) via the official `google-genai` Python SDK.
- **Inference Task:** Comparing extracted resume evidence against job posting requirements, extracting explicit vs inferred company priorities, and drafting an actionable 7-day preparation schedule.

---

## 4. Product Metric & Validation Protocol
- **Primary Metric:** Percentage of student participants who correctly identify at least 3 critical job requirements and commit to a concrete, demonstrable preparation action.
- **Pilot Protocol:** 12–20 students in a Pre/Post (Baseline vs. Assisted) within-subjects test using [`PILOT_METRICS_TEMPLATE.csv`](file:///d:/beep/Beep_Fit_Coach_Starter/PILOT_METRICS_TEMPLATE.csv).
- **Target:** +20 percentage-point improvement in identifying top requirements and choosing an actionable next step.
