from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header
from frontier_ui.talk import speaker

page_header("Decisions and next steps")
speaker("next")

st.subheader("Two decisions we’re least sure about")
st.caption("We would like your recommendation on both.")
a, b = st.columns(2)
with a:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">A. Mental-health claims always go to a person</h3>
<p>Safer, but it caps our fast-track rate, and these applicants never get the faster path.</p>
<p style="background:#E3ECF7;border-radius:8px;padding:10px 12px"><b>Question:</b> allow a narrow mental-health
fast track (for example, a hospitalization record plus a treating psychiatrist’s findings), or keep the hard line?</p>
</div>""", unsafe_allow_html=True)
with b:
    st.markdown("""<div class="ft-card"><h3 style="margin-top:0">B. Only verified-provider records can support a fast
track</h3>
<p>Records an applicant submits still go to the examiner, but can’t trigger a fast track. That blocks gaming, but
people whose doctors are hard to reach may wait longer. We’d report recommendation and miss rates by case type.</p>
<p style="background:#E3ECF7;border-radius:8px;padding:10px 12px"><b>Question:</b> keep it strict, or let
applicant-submitted records count once the provider confirms them?</p></div>""", unsafe_allow_html=True)

st.subheader("Next steps (rest of the term)")
n1, n2, n3 = st.columns(3)
n1.markdown("""<div class="ft-card"><h3 style="margin-top:0">Test</h3><ul>
<li>Blind-check every answer key</li>
<li>Grow to ~200 cases with a fresh test set, marking cases QDD/CAL would already catch</li>
<li>Freeze, pre-register on OSF, run the test set once</li></ul></div>""", unsafe_allow_html=True)
n2.markdown("""<div class="ft-card"><h3 style="margin-top:0">People</h3><ul>
<li>Examiner pilot: the crossover with classmates</li>
<li>Equity: recommendation and miss rates by case type (physical vs. mental)</li></ul></div>""",
            unsafe_allow_html=True)
n3.markdown("""<div class="ft-card"><h3 style="margin-top:0">Robustness</h3><ul>
<li>Re-run the locked test set on other AI models</li>
<li>Scanned and faxed records: OCR vs. image-reading models</li>
<li>More adversarial cases, plus honest look-alikes</li></ul></div>""", unsafe_allow_html=True)

st.subheader("Where it could go after the course")
st.markdown("""
- **Real files with a state partner:** run the tool on past claims in a secure environment and compare with what
  examiners decided; then a pilot where incoming claims are randomly assigned to the tool or the usual process.
- **Reading SSA’s electronic claim folder directly**, so who sent each record comes from the system, not from typing.
- **Gaming defences at scale:** source tiers, objective findings over conclusions, copy-paste detection, random audits.
""")
