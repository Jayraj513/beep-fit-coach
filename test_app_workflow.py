"""
Automated functional verification for Beep Fit Coach Streamlit UI.
Tests presets, compact cards, missions, job simulation, and portfolio download.
"""

from streamlit.testing.v1 import AppTest
from sample_data import SAMPLE_RESUME_DATA_ANALYST, SAMPLE_JD_DATA_ANALYST

def test_stream_app():
    print("Testing Streamlit app with AppTest...")
    at = AppTest.from_file("app.py", default_timeout=30)
    at.run()
    assert not at.exception, f"App threw exception on launch: {at.exception}"
    print("[PASS] Initial app render succeeded")

    # 1. Test "Sample: Data Analyst Intern" button
    sample_btn = None
    for btn in at.button:
        if "Data Analyst" in btn.label:
            sample_btn = btn
            break
    assert sample_btn is not None, "Data Analyst sample button not found"
    sample_btn.click().run()
    assert not at.exception
    assert at.session_state["resume_text"] == SAMPLE_RESUME_DATA_ANALYST
    assert at.session_state["jd_text"] == SAMPLE_JD_DATA_ANALYST
    print("[PASS] Preset 'Data Analyst Intern' loaded into session state")

    # 2. Test "Preview Sample Report" button
    preview_btn = None
    for btn in at.button:
        if "Preview Sample Report" in btn.label:
            preview_btn = btn
            break
    assert preview_btn is not None, "Preview sample report button not found"
    preview_btn.click().run()
    assert not at.exception
    assert at.session_state["analysis_result"] is not None
    assert at.session_state["is_demo_mode"] is True
    print("[PASS] Preview Sample Report mode active")

    # 3. Verify Compact Cards rendered
    md_texts = " ".join([m.value for m in at.markdown])
    assert "Your Strengths" in md_texts
    assert "Your Skill Gaps" in md_texts
    assert "Your Next Action" in md_texts
    print("[PASS] 3 Compact cards (Strengths, Skill Gaps, Next Action) rendered successfully")

    # 4. Verify Interactive Missions state
    assert "missions_state" in at.session_state
    m_state = at.session_state["missions_state"]
    assert "m1" in m_state and "m2" in m_state and "m3" in m_state and "sim" in m_state
    assert m_state["m1"]["completed"] is True, "Expected demo mission 1 to be marked completed"
    print("[PASS] Interactive missions initialized (Demo Mission 1 completed)")

    # 5. Verify Download Completed Work button exists
    download_labels = [d.label for d in at.download_button]
    assert any("Completed Work" in lbl for lbl in download_labels), f"Download button missing: {download_labels}"
    print("[PASS] Download Completed Work button verified")

    # 6. Test "Reset All" button
    reset_btn = None
    for btn in at.button:
        if "Reset All" in btn.label:
            reset_btn = btn
            break
    assert reset_btn is not None, "Reset All button not found"
    reset_btn.click().run()
    assert not at.exception
    assert at.session_state["resume_text"] == ""
    assert at.session_state["jd_text"] == ""
    assert at.session_state["analysis_result"] is None
    assert at.session_state["missions_state"]["m1"]["completed"] is False
    print("[PASS] Reset All cleared inputs, results, and missions state")

    print("\nAll Streamlit AppTest workflow checks passed successfully!")

if __name__ == "__main__":
    test_stream_app()
