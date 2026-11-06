from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header
from frontier_ui.talk import CAP_USD, CLAUDE_PRO_USD, api_spend, speaker

page_header("Where the product stands",
            "What works, what doesn’t yet, what changed since the pitch and what we dropped, and what we have spent.")
speaker("standing")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">✅ Works</h3><ul>
<li>The full pipeline runs live on the Gemini 3.7 Flash API, chosen because it was accessible to us; we plan to compare more models later</li>
<li>Each cited quote is checked against its page (that the words are there, not that they prove the point)</li>
<li>None of the 7 tested gaming cases reached the fast track</li>
<li>Same routing on 3 calibration runs</li>
<li>A case we have never seen can be entered and run live</li></ul></div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">⏳ Not yet</h3><ul>
<li>No test-set result, so no evidence for the main claim</li>
<li>Answer keys not yet checked blind by people</li>
<li>Our cases are simpler than real files: short, and text only</li>
<li>Two supporting records per finding (k = 2) can’t be tested on our cases</li>
<li>A live run takes about 90 seconds</li></ul></div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">🔁 Changed since the pitch, and why</h3><ul>
<li><b>Source rule:</b> only records from verified providers can support a fast-track recommendation (instructor feedback on gaming)</li>
<li><b>Mental-health claims</b> always go to a person: the criteria need judgment</li>
<li><b>Working-above-SGA cases</b> moved out of the test set: the field office screens them first</li>
<li><b>Dropped:</b> our first keyword baseline as evidence; it only matched our own templates</li></ul></div>""",
                unsafe_allow_html=True)

st.subheader("Spend against the $200 course cap")
api, tokens = api_spend()
live = sum(x.get("cost_usd", 0) for x in st.session_state.get("live_log", []))
total = CLAUDE_PRO_USD + api + live
rows = [
    {"Line": "Claude Pro subscription (2 months, building and writing)", "Amount": f"${CLAUDE_PRO_USD:.2f}",
     "Note": "Largest single line"},
    {"Line": "Gemini 3.7 Flash API: all batch runs and the Replay recording",
     "Amount": f"${api:.2f}", "Note": f"{tokens:,} tokens at list price"},
]
if live:
    rows.append({"Line": "Live runs in this session", "Amount": f"${live:.3f}", "Note": "added as they happen"})
rows.append({"Line": "Total so far", "Amount": f"${total:.2f}", "Note": f"of ${CAP_USD:.0f} ({total / CAP_USD:.0%})"})
st.dataframe(rows, width="stretch", hide_index=True)
m1, m2, m3 = st.columns(3)
m1.metric("Spent so far", f"${total:.2f}", help="Subscription plus API estimate.")
m2.metric("Left under the cap", f"${CAP_USD - total:.2f}")
m3.metric("Largest single line", "Claude Pro", f"${CLAUDE_PRO_USD:.0f}", delta_color="off")
st.caption("API figures are estimates from token counts at Gemini 3.7 Flash list price ($0.75 / $3.75 per million "
           "tokens); the Google Cloud billing page is the real figure. Most of the cap is kept for the test run, "
           "a robustness check on other models and the larger case set.")
