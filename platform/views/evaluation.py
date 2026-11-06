from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header
from frontier_ui.talk import speaker

page_header("Evaluation plan", "The claim, the threshold, the counterfactual, how cases are assigned, and whether "
            "our sample can support it.")
speaker("evaluation")

cards = [
    ("Claim", "Reading the medical records identifies additional clear-cut claims for expedited human review."),
    ("Threshold", "Of the claims it screens: <b>≥ 15%</b> recommended · precision <b>≥ 95%</b> · "
                  "<b>0</b> automated denials"),
    ("Counterfactual", "QDD/CAL alone: these claims wait for full review. And examiners without the AI."),
    ("Assignment", "Random calibration/test split (recorded seed). Random crossover for examiners."),
]
cols = st.columns(4)
for c, (h, t) in zip(cols, cards):
    c.markdown(f'<div class="ft-card"><h3 style="margin-top:0">{h}</h3>{t}</div>', unsafe_allow_html=True)

st.subheader("How we test it, and on whom")
a, b = st.columns(2)
with a:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">1 · The tool’s routing</h3>
<p class="sub"><b>On:</b> simulated claim files built on the real SSA forms, each from a randomly drawn profile
(age, condition, work history, wording, typos)</p>
<ol><li>Split the cases at random into calibration and test</li>
<li>Tune on calibration only, then freeze and pre-register on OSF</li>
<li>Run the test set once against the answer keys</li></ol></div>""", unsafe_allow_html=True)
with b:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">2 · Examiners with vs. without the tool</h3>
<p class="sub"><b>On:</b> 3–6 classmates acting as examiners (a feasibility pilot)</p>
<ol><li>Two random case blocks, A and B; two random groups of volunteers</li>
<li>Group 1 reviews A with the AI and B without; Group 2 the reverse; order randomized</li>
<li>Each volunteer works under both conditions; each case is seen under both by different volunteers</li></ol>
</div>""", unsafe_allow_html=True)

st.subheader("Sample size and power")
st.dataframe([
    {"Measure": "Fast-track rate", "With 40 test cases": "6 of 40 (15%): 95% CI about 7–29%",
     "Plan": "Report the interval, not just the point"},
    {"Measure": "Precision ≥ 95%",
     "With 40 test cases": "13 should be fast-tracked; even 13 of 13 correct gives a lower bound of ~77%. "
                           "A point estimate of 95% is not evidence of ≥ 95%",
     "Plan": "A larger set enriched with fast-track cases (~80 of ~200); with zero errors, ~73 are needed for a "
             "95% lower bound"},
    {"Measure": "Examiner time and accuracy",
     "With 40 test cases": "3–6 volunteers, repeated decisions by person and case",
     "Plan": "A feasibility pilot: report estimates with uncertainty; real examiners later"},
], width="stretch", hide_index=True)
