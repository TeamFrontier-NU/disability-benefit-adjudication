"""Presentation app for the halfway demo (and anyone who wants to look).

    streamlit run Frontier.py

Six pages: Overview, Case explorer, New case (live), Safeguards, Results, About. Default is Replay mode:
recorded Gemini 3.7 Flash output, no key, no cost. Live mode is presenter-only (passcode).
The original examiner panel is still `app.py`; nothing in `fasttrack/` was changed for this.
"""
from __future__ import annotations

import streamlit as st

from frontier_ui import replay, talk

st.set_page_config(page_title="Frontier Fast-Track Screening", page_icon="⚖️", layout="wide")

with st.sidebar:
    st.markdown("### Frontier · Team 06")
    st.caption("Fast-track screening for initial adult SSI/SSDI claims. Simulated cases only.")
    st.divider()
    if st.session_state.get("live_ok"):
        st.success("**Live mode** (presenter): calls Gemini 3.7 Flash and costs money.")
        log = st.session_state.get("live_log", [])
        if log:
            st.caption(f"Live runs this session: {len(log)} · about ${sum(x['cost_usd'] for x in log):.3f}")
        if st.button("Back to Replay mode"):
            st.session_state["live_ok"] = False
            st.rerun()
    else:
        st.info("**Replay mode**: recorded Gemini 3.7 Flash output. No key, no cost, works offline.")
        if replay.live_configured():
            with st.expander("Presenter: switch on Live mode"):
                code = st.text_input("Passcode", type="password")
                if st.button("Unlock Live mode") and code:
                    if replay.passcode_ok(code):
                        st.session_state["live_ok"] = True
                        st.rerun()
                    else:
                        st.error("Wrong passcode.")
        else:
            st.caption("Live mode is off here (no passcode or key set up).")

pages = {
    "Presentation": [
        st.Page("views/overview.py", title="1 · Where it fits", icon="🏠", default=True),
        st.Page("views/standing.py", title="2 · Where we stand", icon="📍"),
        st.Page("views/case_explorer.py", title="3 · Demo: Joe and Peter", icon="🗂️"),
        st.Page("views/safeguards.py", title="4a · Demo: attacks", icon="🛡️"),
        st.Page("views/new_case.py", title="4b · Demo: a new case (live)", icon="🆕"),
        st.Page("views/evaluation.py", title="5 · Evaluation plan", icon="🧪"),
        st.Page("views/next_steps.py", title="6 · Decisions and next steps", icon="🧭"),
    ],
    "Backup": [
        st.Page("views/qa.py", title="Questions", icon="❓"),
        st.Page("views/results.py", title="Results", icon="📊"),
        st.Page("views/about.py", title="About and method", icon="ℹ️"),
    ],
}
with st.sidebar:
    talk.run_of_show()
st.navigation(pages).run()
