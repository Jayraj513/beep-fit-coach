# Beep Fit Coach 🎯
> **Turn job descriptions into your next career move.**  
> *An independent, evidence-based career-readiness prototype for Indian college students and fresh graduates.*

---

## 1. Product Overview & Hypothesis
**Beep Fit Coach** helps students turn long, intimidating job descriptions into an honest skills-gap analysis and an achievable 7-day preparation roadmap.

### The Working Hypothesis
Many college students and fresh graduates struggle to translate job postings into targeted preparation. They frequently:
- Misjudge which parts of their coursework and academic projects satisfy the role's requirements.
- Treat missing skills as total disqualification rather than addressable gaps.
- Default to broad, unstructured video tutorials instead of producing verifiable project artifacts.

*Notice:* This is a hypothesis formulated for exploration in a product-building prototype. It is not an established fact across all Beep users, and no claims about Beep or external research are fabricated.

---

## 2. Core Features
- **Document Upload for Resumes & Job Postings:** Upload resumes and job descriptions as **PDF (`.pdf`)** or **Word (`.docx`)** documents with drag-and-drop ease, or paste text directly.
- **In-Memory Text Extraction:** Securely parses documents in memory using `pypdf` and `python-docx` without relying on external third-party file converters.
- **Editable Extraction Preview:** Extracted text is presented in an editable text area so students can review and correct formatting before analysis.
- **Scanned PDF & Encryption Detection:** Clear, user-friendly warnings for image-only/scanned PDFs explaining that OCR is required, password-protected PDFs, oversized files (> 10 MB), and empty documents.
- **Default 3 Compact Cards View:** Replaces the long diagnostic report with 3 immediate action cards: **Your Strengths**, **Your Skill Gaps**, and **Your Next Action** for high-velocity comprehension.
- **Expandable Detailed Report:** Keeps the complete 5-tab diagnostic breakdown (comparison table, rewrites, mini-project blueprint, 7-day plan, interview prep) inside an expandable drawer.
- **3 Interactive Job-Specific Missions:** 3–5 minute micro-tasks tailored to the analyzed role (Technical Requirement Attack, Truthful Bullet Refinement, Technical Interview Response) with live submission, instant rubric feedback, and retry.
- **Practical Role-Specific Job Simulation:** Hands-on technical challenge (e.g. SQL cohort queries for Data Analysts, C safe buffer operations for Systems roles, Python data processing for Software roles) evaluated against professional rubrics.
- **Session Progress Tracking & Practice Export:** Tracks completed missions in session state and exports candidate answers, code solutions, and AI feedback into a downloadable portfolio artifact (`beep_fit_coach_practice_work.md`).
- **Truthful Requirement Mapping:** Compares resume experience against job requirements using only provided evidence. Absences are designated as *"Not evidenced in the provided resume"*, never as proof of inability.
- **No Arbitrary Hiring Percentages:** Uses qualitative rubrics (**Strong Evidence**, **Partial Evidence**, **Not Enough Evidence to Assess**) with clear explanations of rubric scope.
- **Top 3 Strategic Priority Gaps:** Pinpoints the highest-ROI gaps with actionable advice and tangible outputs to produce.
- **Truthful Resume Refinement:** Suggests bullet phrasing improvements strictly grounded in existing experience, utilizing placeholders like `[confirm actual metric]` for unverified details.
- **Feasible Mini-Project Blueprint:** Details a demonstrable, 1-week project tailored to the role's specific stack (clearly labeled as unbuilt future prep).
- **Realistic 7-Day Action Plan:** Day-by-day tasks with estimated times, concrete deliverables, and completion checks.
- **Multi-Format Export:** 1-click download of the complete diagnostic report in both Markdown (`.md`) and Plain Text (`.txt`).
- **Built-in Demo Mode:** 1-click sample presets for **Data Analyst Intern** and **AI/ML Intern** plus an instant offline report and completed mission preview.
- **Privacy First:** Ephemeral server-side processing; zero permanent database storage.

---

## 3. Technology Stack & Supported Formats
- **Framework:** Python 3.12, Streamlit
- **Document Extraction:** `pypdf` (>= 5.0.0), `python-docx` (>= 1.1.0)
- **Supported Formats:** PDF (`.pdf`), Word (`.docx`), and direct text input
- **File Limit:** Up to 10 MB per document (in-memory processing)
- **AI SDK:** Official Google Gen AI Python SDK (`google-genai` >= 1.0.0)
- **Model:** Google Gemini (`gemini-2.5-flash` with automatic fallback to `gemini-2.0-flash` and `gemini-1.5-flash`)
- **Styling:** Custom Vanilla CSS for career-tech visual hierarchy, semantic status badges, and mobile responsiveness.

---

## 4. Prerequisites
- **Python:** Python 3.11 or 3.12 installed on your system.
- **Gemini API Key:** A free API key from [Google AI Studio](https://aistudio.google.com/apikey).

---

## 5. Quick Start: Run Locally on Windows

Open PowerShell or Command Prompt in the project folder (`d:\beep\Beep_Fit_Coach_Starter`) and execute:

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure your Gemini API key in .streamlit/secrets.toml
# If .streamlit/secrets.toml does not exist, copy from template:
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
# Open .streamlit/secrets.toml and enter your API key:
# GEMINI_API_KEY = "your-actual-api-key"

# 3. Launch the Streamlit application
streamlit run app.py
```

The application will start at `http://localhost:8501`.

---

## 6. How Document Extraction Works & Edge Cases
The application handles document ingestion via [`document_parser.py`](file:///d:/beep/Beep_Fit_Coach_Starter/document_parser.py):
1. **Memory-Safe:** Uploaded bytes are processed in `io.BytesIO` streams. Files are **never** written to the local disk or uploaded to external file converters.
2. **PDF Parsing:** Uses `pypdf.PdfReader` to extract text page-by-page.
   - *Scanned PDFs:* If a PDF contains pages but yields fewer than 30 characters of selectable text, the app identifies it as a scanned/image-based document and informs the user that OCR is required.
   - *Encrypted PDFs:* If a PDF is password-protected, the app detects encryption and instructs the user to provide an unlocked file.
3. **DOCX Parsing:** Uses `docx.Document` to extract both paragraph text and table cell contents (vital for multi-column resumes).
   - *Legacy `.doc` Files:* Detects older Word 97-2003 binary formats and prompts the user to convert to modern `.docx` or paste text directly.
4. **Size Validation:** Validates file size before parsing; files exceeding 10 MB are rejected with clear user guidance.
5. **Editable Preview:** Extracted text is loaded into an editable text area so the user can verify extraction fidelity before submitting to the AI.

---

## 7. How to Configure Your Gemini API Key
The application securely checks for your API key in three places (in order of priority):
1. **Streamlit Secrets (Recommended):**  
   Create `.streamlit/secrets.toml`:
   ```toml
   GEMINI_API_KEY = "AIzaSy..."
   ```
2. **Environment Variable:**  
   In your terminal before running:
   ```powershell
   $env:GEMINI_API_KEY="AIzaSy..."
   ```
3. **Sidebar Session Fallback:**  
   If no file or environment variable is set, you can paste your key directly into the sidebar in the browser. It remains in-memory for that browser session only.

---

## 8. How to Test the Application
- **1. Test Document Upload:**
  - In **Step 1 (Resume)**, select `📁 Upload PDF / DOCX` and upload your `.pdf` or `.docx` resume.
  - Review the file size and character count in the editable preview area.
- **2. Test Job Description:**
  - In **Step 2 (Target Job)**, paste a job posting or upload a JD document.
- **3. Test Live Gemini Analysis:**
  - Click **"🚀 Analyze Fit & Build Action Plan"**. Review the structured tabs.
- **4. Test Demo Mode (No API Key Required):**  
  - Click **"✨ Preview Sample Report (No API Needed)"** at the top to explore a pre-computed diagnostic report for a Data Analyst Intern role.
- **5. Test Presets & Reset:**  
  - Use **"📊 Sample: Data Analyst Intern"** or **"🤖 Sample: AI/ML Intern"** to test 1-click presets.
  - Click **"🔄 Reset All"** or **"Start Over"** to clear inputs and results.
- **6. Run Automated Test Suites:**
  ```powershell
  # Test document parser edge cases (PDF, DOCX, scanned, corrupted, empty)
  python test_document_parser.py

  # Test Streamlit UI workflow and presets
  python test_app_workflow.py
  ```

---

## 9. 5-Minute Loom Video Recording Guide
When recording your video demo (maximum 5 minutes, showing face and screen):
1. **Problem & Hypothesis (1 min):** Explain the student problem—students feeling overwhelmed by job descriptions and defaulting to passive tutorials instead of verifiable preparation.
2. **Document Upload & Extraction (1 min):** Demonstrate dragging-and-dropping a PDF or DOCX resume, highlight the file size display, and show the editable preview.
3. **Live Analysis & Fit Breakdown (1.5 min):** Click Analyze and walk through:
   - Qualitative Fit Snapshot (no arbitrary scores).
   - Requirement-by-Requirement evidence comparison table.
   - Top 3 strategic priority gaps.
4. **7-Day Roadmap & Truthful Resume Refinement (1 min):** Highlight the actionable daily schedule, the mini-project blueprint, and how bracketed placeholders prevent resume exaggeration.
5. **Metric & Validation Plan (0.5 min):** Explain the primary metric (% of students choosing a concrete next action) and the 12–20 student pilot test plan using `PILOT_METRICS_TEMPLATE.csv`.

---

## 10. Deployment: Streamlit Community Cloud

1. **Push to GitHub:**  
   Confirm that `.streamlit/secrets.toml` is ignored by `.gitignore`.
   ```powershell
   git init
   git add .
   git commit -m "Beep Fit Coach with PDF/DOCX upload and 3-step workflow"
   git branch -M main
   git remote add origin https://github.com/your-username/beep-fit-coach.git
   git push -u origin main
   ```
2. **Deploy on Streamlit Community Cloud:**  
   - Visit [share.streamlit.io](https://share.streamlit.io) and link your GitHub repository.
   - Set **Main file path** to `app.py`.
   - In **Settings -> Secrets**, enter:
     ```toml
     GEMINI_API_KEY = "your-actual-api-key"
     ```
3. **Launch:** Click **Deploy**. Streamlit Cloud will install `requirements.txt` and generate your public HTTPS URL.

---

## 11. Privacy, Security & Data Handling
- **Ephemeral Processing:** All documents and text are processed in-memory during inference. No user resume or job description is stored in a permanent database or saved to server disk.
- **User Redaction:** Users are explicitly advised to remove phone numbers, physical addresses, and personal IDs prior to submission.
- **Key Safety:** Keys are never passed to the browser client or logged in application consoles.

---

## 12. Known Limitations
- **Scanned PDFs:** Image-only/scanned documents without selectable text require OCR. The app detects these files and advises the user to upload a text-based document or paste text.
- **Text-Only Dependency:** The tool relies strictly on text provided in the prompt. Skills omitted from the resume are classified as *"Not evidenced"*, not as proof of inability.
- **No ATS Emulation:** The tool is a career readiness coach, not a proprietary ATS keyword checker.

---

## 13. Project Documentation Links
- [`app.py`](file:///d:/beep/Beep_Fit_Coach_Starter/app.py): Complete Streamlit web application.
- [`document_parser.py`](file:///d:/beep/Beep_Fit_Coach_Starter/document_parser.py): PDF & DOCX text extraction module.
- [`sample_data.py`](file:///d:/beep/Beep_Fit_Coach_Starter/sample_data.py): Sample student profiles, job postings, and offline demo data.
- [`BUILD_AND_AI_TOOLS.md`](file:///d:/beep/Beep_Fit_Coach_Starter/BUILD_AND_AI_TOOLS.md): One-page build and AI tools explanation.
- [`ASSIGNMENT_CHECKLIST.md`](file:///d:/beep/Beep_Fit_Coach_Starter/ASSIGNMENT_CHECKLIST.md): 13-point assignment requirements matrix.
- [`PRODUCT_NOTES.md`](file:///d:/beep/Beep_Fit_Coach_Starter/PRODUCT_NOTES.md): Product strategy, user persona, and pilot experiment design.
- [`TESTING_CHECKLIST.md`](file:///d:/beep/Beep_Fit_Coach_Starter/TESTING_CHECKLIST.md): Verification testing checklist.
- [`PILOT_METRICS_TEMPLATE.csv`](file:///d:/beep/Beep_Fit_Coach_Starter/PILOT_METRICS_TEMPLATE.csv): Standardized pilot participant tracking sheet.

---

## 14. Disclaimer
*Beep Fit Coach is an independent prototype created for an educational product assignment. It is not affiliated with, endorsed by, or sponsored by Beep.*
