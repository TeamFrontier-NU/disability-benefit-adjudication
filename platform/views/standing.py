from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header
from frontier_ui.talk import (CAP_USD, CASES_SO_FAR, CLAUDE_PRO_USD, PROJECTION_PRICES, api_spend,
                              avg_tokens_per_read, projected_cost, speaker)

page_header("Where the product stands",
            "What works, what doesn’t yet, what changed since the pitch and what we dropped, and what we have spent.")
speaker("standing")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">✅ Works</h3><ul>
<li>The full screening pipeline runs live with Gemini 3.7 Flash</li>
<li>10 simulated calibration cases: routing matched our provisional answer key in 3 separate runs</li>
<li>137 cited quotes checked: every one appears on the page cited</li>
<li>All 7 crafted gaming scenarios went to human review, not the fast track</li>
<li>A case we have never seen can be entered and run live</li></ul>
<p style="color:#4A5568;margin-bottom:0">A quote check shows the words are on the page. It does not show that the quote
supports the conclusion, or that the document is authentic: an examiner still reviews and decides.</p></div>""",
                unsafe_allow_html=True)
with c2:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">⏳ Not yet</h3><ul>
<li>No test-set result yet, so no evidence for the main claim</li>
<li>Answer keys are provisional: not yet blind-reviewed by people</li>
<li>Our files are short and text only: not tested on full DDS electronic folders or scanned documents</li>
<li>Two supporting records per finding (k = 2) can’t be tested on our cases</li></ul></div>""",
                unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">🔁 Changed since the pitch, and why</h3><ul>
<li><b>Source and provenance check</b> (instructor’s concern about gaming): medical findings can support a fast track
only if the record is marked as received through a DDS request from a provider named on the application.
<i>Limitation:</i> this does not independently verify who the provider is</li>
<li><b>Mental-health Listing criteria</b> no longer trigger a fast track: they need an examiner’s judgment</li>
<li><b>Keyword reader</b> no longer used as evidence that the platform works: good on wording close to our
templates, weaker on varied wording. Kept only as a comparison baseline</li></ul></div>""",
                unsafe_allow_html=True)

st.subheader("Spend so far, against the $200 course cap")
st.caption(f"While the budget was pending we kept API use small. Our simulated dataset has {CASES_SO_FAR} distinct "
           "cases: that is the dataset size, not the number of API calls.")
api, tokens = api_spend()
live = sum(x.get("cost_usd", 0) for x in st.session_state.get("live_log", []))
total = CLAUDE_PRO_USD + api + live
rows = [
    {"Line": "Claude Pro subscription (paid by the course, Oct 13 – Nov 10)", "Amount": f"${CLAUDE_PRO_USD:.2f}",
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
           "tokens); the Google Cloud billing page is the real figure.")

# ----------------------------------------------------------------------------- projection
st.subheader("Budget request")
st.markdown("""<div class="ft-card"><b>Requested in one Payment Request Form: $120</b><ul>
<li><b>Claude Pro renewal: $20</b> — building and maintaining the platform, and preparing the evaluation</li>
<li><b>Claude API, prepaid credits: $100</b> — Claude becomes the reader for the full evaluation: about 500–1,000
simulated cases, each read twice (the locked run plus a repeat), estimated at about $50–$100 from measured token
counts (scenario C below). Prepaid credits mean spending cannot go above the approved amount.</li></ul>
<span style="color:#4A5568">If approved, about $60 of the $200 cap would remain.</span></div>""", unsafe_allow_html=True)

st.subheader("Projected budget for the full evaluation")
t_in, t_out = avg_tokens_per_read()
per_read = (t_in * PROJECTION_PRICES["Gemini 3.7 Flash (now)"][0] + t_out * PROJECTION_PRICES["Gemini 3.7 Flash (now)"][1]) / 1e6
st.markdown(f"Plan: **500–1,000 simulated cases**. Today one read of one case uses about **{t_in + t_out:,.0f} "
            f"tokens** (about **{per_read * 100:.1f}¢** on Gemini 3.7 Flash). The new cases will be longer, so we "
            "assume **2× the tokens**. Each case is read twice on the main model (the locked run plus a repeat), "
            "and moving to a Claude model costs more per read.")
GEM, GEM27, SON, OPUS = list(PROJECTION_PRICES)
scen = [
    ("A · Gemini 3.7 Flash only", [(GEM, 2)]),
    ("B · Gemini + one Claude Sonnet robustness read", [(GEM, 2), (SON, 1)]),
    ("C · Switch the main reader to Claude Sonnet", [(SON, 2)]),
    ("D · Gemini + Sonnet, after Gemini’s 2027 price rise", [(GEM27, 2), (SON, 1)]),
]
left = CAP_USD - total
rows = []
for name, reads in scen:
    c5, c10 = projected_cost(500, reads), projected_cost(1000, reads)
    rows.append({"Scenario": name, "500 cases": f"${c5:,.0f}", "1,000 cases": f"${c10:,.0f}",
                 "Fits what’s left of the cap?": "yes" if c10 <= left else ("only at 500" if c5 <= left else "no")})
st.dataframe(rows, width="stretch", hide_index=True)
st.caption(f"‘What’s left’ is ${left:,.0f} after spend so far. Gemini prices are its list prices (introductory "
           "until Dec 31, 2026); Claude prices are from our pitch’s price table. Case generation by another AI "
           "and real files (often 50–500 pages) would add more; a real-file study needs its own budget. These are "
           "projections from short text files: longer records, scanned files or a different model change the cost, "
           "so we will update the budget with measured token counts before the full evaluation.")

with st.expander("Try other numbers"):
    a, b, c = st.columns(3)
    n = a.slider("Cases", 100, 2000, 1000, step=100)
    length = b.select_slider("File length vs. today", [1.0, 2.0, 3.0, 5.0], value=2.0, format_func=lambda x: f"{x:g}×")
    main = c.selectbox("Main reader", list(PROJECTION_PRICES))
    d, e, f = st.columns(3)
    main_reads = d.number_input("Reads per case (main)", 1, 5, 2)
    check = e.selectbox("Robustness model", ["None"] + list(PROJECTION_PRICES), index=3)
    check_reads = f.number_input("Reads per case (robustness)", 0, 3, 1)
    reads = [(main, int(main_reads))] + ([(check, int(check_reads))] if check != "None" and check_reads else [])
    est = projected_cost(n, reads, length)
    st.metric("Estimated API cost", f"${est:,.0f}",
              f"{'within' if est <= left else 'over'} the ${left:,.0f} left under the cap", delta_color="off")
