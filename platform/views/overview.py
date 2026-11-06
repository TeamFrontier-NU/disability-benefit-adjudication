from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header, saved_runs

page_header("Fast-track screening for disability claims",
            "The tool reads a claim's medical records, fills a fixed checklist with quotes and page numbers, and "
            "applies SSA's own rules. Claims that clearly qualify go to a **fast track**, where an examiner checks "
            "and signs. Everything else goes to the **human queue**. **The tool never denies a claim.**")

st.subheader("Same path, a wider fast track at step 4")
box = lambda cls, t: f'<div class="ft-box {cls}">{t}</div>'
arrow = '<div class="ft-arrow">→</div>'
today = [box("same", "1 Apply<br><small>SSA-16, SSA-3368</small>"), arrow,
         box("same", "2 Field office<br><small>non-medical rules, work</small>"), arrow,
         box("same", "3 State DDS<br><small>requests medical records</small>"), arrow,
         box("same", "4 Fast track from the <b>form</b> only<br><small>QDD / CAL: about 8% of claims</small>"), arrow,
         box("same", "Everyone else waits for full review")]
ours = [box("same", "1 Apply<br><small>unchanged</small>"), arrow,
        box("same", "2 Field office<br><small>unchanged</small>"), arrow,
        box("same", "3 State DDS<br><small>unchanged</small>"), arrow,
        box("new", "4 AI reads the <b>medical records</b><br><small>quotes every finding, applies SSA rules</small>"), arrow,
        f'<div style="flex:1 1 160px;display:flex;flex-direction:column;gap:6px">'
        f'{box("fast", "FAST TRACK<br><small>examiner checks and signs</small>")}'
        f'{box("human", "HUMAN QUEUE<br><small>with evidence for approval</small>")}</div>']
st.markdown("**Today**")
st.markdown(f'<div class="ft-path">{"".join(today)}</div>', unsafe_allow_html=True)
st.markdown("**With our tool**")
st.markdown(f'<div class="ft-path">{"".join(ours)}</div>', unsafe_allow_html=True)
st.caption("There is no path that ends in a denial. A denial is always decided by a person.")

st.subheader("What we have measured so far")
runs = [r for r in saved_runs() if not r["failed"]]
cal = [r for r in runs if r["set"] == "calibration" and r["k"] == 1]
stress = [r for r in runs if r["set"] == "stress"]


def matches(r):
    return sum((x["route"] == "fast_track") == x["key_fast_track"] for x in r["rows"]), len(r["rows"])


c1, c2, c3 = st.columns(3)
with c1:
    if cal:
        m = [matches(r) for r in cal]
        same = len({mm for mm in m}) == 1
        big = f"{m[0][0]}/{m[0][1]}" if same else " · ".join(f"{a}/{b}" for a, b in m)
        st.markdown(f'<div class="ft-card"><div class="sub">Calibration set, k = 1</div><div class="big">{big}</div>'
                    f'routed as the answer key expects, in {"each of " if len(cal) > 1 else ""}{len(cal)} '
                    f'run{"s" if len(cal) > 1 else ""}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ft-card">No calibration runs saved yet.</div>', unsafe_allow_html=True)
with c2:
    if stress:
        r = stress[-1]
        gaming = [x for x in r["rows"] if not x["key_fast_track"]]
        wrong = [x for x in gaming if x["route"] == "fast_track"]
        st.markdown(f'<div class="ft-card"><div class="sub">Stress set (gaming attempts)</div>'
                    f'<div class="big">{len(wrong)}/{len(gaming)}</div>gaming cases put on the fast track</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="ft-card">No stress run saved yet.</div>', unsafe_allow_html=True)
with c3:
    n = sum(len(r["rows"]) for r in runs if r["reader"].startswith("Gemini"))
    st.markdown(f'<div class="ft-card"><div class="sub">All Gemini runs (demo, calibration, stress)</div>'
                f'<div class="big">0</div>denials made by the AI, in {n} case reads. The code has no way to deny.</div>',
                unsafe_allow_html=True)

l1, l2, l3 = st.columns(3)
l1.page_link("views/results.py", label="Calibration details", icon="📊")
l2.page_link("views/safeguards.py", label="Stress set details", icon="🛡️")
l3.page_link("views/case_explorer.py", label="Try a case", icon="🗂️")

st.info("These are calibration and stress results on simulated cases. They are **not evidence for the claim yet**. "
        "The claim (at least 15% fast-tracked, at least 95% of those eligible, 0 AI denials) is tested once on 40 "
        "locked test cases, after the plan is posted on OSF.")
