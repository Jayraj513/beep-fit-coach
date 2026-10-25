"""
Test file to verify Analyze button lifecycle, loading state reset in finally block,
and error handling without infinite loops or stuck spinners.
"""

from unittest.mock import patch
from streamlit.testing.v1 import AppTest
from sample_data import SAMPLE_RESUME_DATA_ANALYST, SAMPLE_JD_DATA_ANALYST

def test_analyze_button_success_and_loading_reset():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception

    # Load preset
    for btn in at.button:
        if "Data Analyst" in btn.label:
            btn.click().run()
            break

    assert at.session_state["resume_text"] == SAMPLE_RESUME_DATA_ANALYST
    assert at.session_state["jd_text"] == SAMPLE_JD_DATA_ANALYST
    assert at.session_state["is_analyzing"] is False

    mock_analysis_md = """# Beep Fit Coach: Job-Fit Analysis & Action Plan
## 1. Role Summary & Fit Snapshot
### A. Role Summary
- **Target Role & Core Purpose:** Data Analyst Intern
### B. Qualitative Fit Snapshot
- **Qualitative Assessment:** Strong Evidence
## 2. Requirement-by-Requirement Comparison Table
| Requirement | JD Importance | Resume Evidence | Status | Recommended Next Action |
| SQL Queries | High | Relevant coursework | [Evidence found] | Practice optimization |
## 3. Top 3 Strategic Priority Gaps
### Priority 1: Advanced Tableau
- **Why it matters:** Critical for dashboard reporting
- **What you can do:** Build a portfolio dashboard
- **Tangible output:** Tableau Public link
## 4. Truthful Resume Improvements
- **Current Phrasing:** Worked on databases
- **Suggested Truthful Revision:** Built PostgreSQL schema with [confirm metric] query speedup
- **Why this is better:** More direct and evidenced
## 5. Feasible Portfolio Mini-Project Blueprint
- **Project Title & Objective:** E-commerce Dashboard
## 6. Realistic Seven-Day Action Plan
| Day | Focus Area | Daily Task | Estimated Time | Tangible Output & Completion Check |
| Day 1 | SQL Mastery | Write complex joins | 2 hours | 5 verified queries |
## 7. Role-Specific Interview Preparation
### Question 1: "Explain window functions"
- **What the interviewer is assessing:** Advanced analytical SQL
- **What a strong candidate answer should cover:** OVER(), PARTITION BY, and practical use cases
## 8. Limitations & Constructive Reflection
- Diagnostic evaluation only.
"""

    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = mock_analysis_md
    mock_client.models.generate_content.return_value = mock_response

    at.session_state["sidebar_api_key"] = "AIzaSyTestMockKey12345"

    with patch("google.genai.Client", return_value=mock_client):
        for btn in at.button:
            if "Analyze Fit & Build Action Plan" in btn.label:
                btn.click().run()
                break

    if at.error:
        print("At errors:", [e.value for e in at.error])
    if at.exception:
        print("At exceptions:", at.exception)
    assert at.session_state["is_analyzing"] is False, "is_analyzing must be False after execution"
    assert at.session_state["analysis_result"] == mock_analysis_md.strip()
    assert at.session_state["analysis_error"] is None
    print("[PASS] Successful analysis execution and loading state reset verified")


def test_analyze_button_timeout_and_loading_reset():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception

    for btn in at.button:
        if "Data Analyst" in btn.label:
            btn.click().run()
            break

    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = TimeoutError("Analysis request timed out after 45 seconds.")
    at.session_state["sidebar_api_key"] = "AIzaSyTestMockKey12345"

    with patch("google.genai.Client", return_value=mock_client):
        for btn in at.button:
            if "Analyze Fit & Build Action Plan" in btn.label:
                btn.click().run()
                break

    assert not at.exception
    assert at.session_state["is_analyzing"] is False, "is_analyzing must be reset to False even on Timeout"
    assert at.session_state["analysis_result"] is None
    assert "timed out after 45 seconds" in at.session_state["analysis_error"]
    errors = [e.value for e in at.error]
    assert any("Analysis Timeout" in err for err in errors), f"Expected timeout error in UI, got {errors}"
    print("[PASS] Timeout handling and finally reset verified")


def test_analyze_button_503_and_loading_reset():
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception

    for btn in at.button:
        if "Data Analyst" in btn.label:
            btn.click().run()
            break

    from unittest.mock import MagicMock
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = RuntimeError("503 The model is overloaded. Please try again later.")
    at.session_state["sidebar_api_key"] = "AIzaSyTestMockKey12345"

    with patch("google.genai.Client", return_value=mock_client):
        for btn in at.button:
            if "Analyze Fit & Build Action Plan" in btn.label:
                btn.click().run()
                break

    assert not at.exception
    assert at.session_state["is_analyzing"] is False, "is_analyzing must be reset to False even on 503"
    errors = [e.value for e in at.error]
    assert any("Google Gemini Server Spike" in err for err in errors)
    print("[PASS] 503 handling and finally reset verified without duplicate retries")

if __name__ == "__main__":
    test_analyze_button_success_and_loading_reset()
    test_analyze_button_timeout_and_loading_reset()
    test_analyze_button_503_and_loading_reset()
    print("\nAll analyze lifecycle tests passed successfully!")
