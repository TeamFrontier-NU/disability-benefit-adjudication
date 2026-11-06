from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header, saved_runs
from frontier_ui.talk import speaker

page_header("Fast-track screening for initial SSI/SSDI claims",
            "For claims already filed, at the state DDS stage. The tool reads the medical records, fills a fixed "
            "checklist with quotes and page numbers, and applies SSA’s own rules. Clear-cut claims are "
            "**recommended for expedited review** by an examiner. Everything else goes to the **human queue**. "
            "**The tool never denies a claim.**")
speaker("fits")

st.subheader("Same path, a second screen at step 4")
box = lambda cls, t: f'<div class="ft-box {cls}">{t}</div>'
arrow = '<div class="ft-arrow">→</div>'
today = [box("same", "1 Apply<br><small>forms, list of doctors, record release</small>"), arrow,
         box("same", "2 Field office<br><small>non-medical check</small>"), arrow,
         box("same", "3 QDD / CAL<br><small>early screen: predictive model, reported conditions</small>"), arrow,
         box("same", "4 State DDS<br><small>requests and reviews records</small>"), arrow,
         f'<div style="flex:1 1 160px;display:flex;flex-direction:column;gap:6px">'
         f'{box("fast", "FAST TRACK: 8.3%<br><small>picked by QDD/CAL</small>")}'
         f'{box("human", "EVERYONE ELSE<br><small>full review, ~209 days</small>")}</div>']
ours = [box("same", "1 Apply<br><small>unchanged</small>"), arrow,
        box("same", "2 Field office<br><small>unchanged</small>"), arrow,
        box("same", "3 QDD / CAL<br><small>kept as is</small>"), arrow,
        box("new", "4 Our tool reads the <b>medical records</b><br><small>of the claims not yet picked</small>"),
        arrow,
        f'<div style="flex:1 1 160px;display:flex;flex-direction:column;gap:6px">'
        f'{box("fast", "EXPEDITED REVIEW<br><small>target ≥ 15% of claims screened</small>")}'
        f'{box("human", "HUMAN QUEUE<br><small>same review as today</small>")}</div>']
st.markdown("**Today**")
st.markdown(f'<div class="ft-path">{"".join(today)}</div>', unsafe_allow_html=True)
st.markdown("**With our tool**")
st.markdown(f'<div class="ft-path">{"".join(ours)}</div>', unsafe_allow_html=True)
st.caption("8.3% and ~209 days: FY2023 figures from our design pitch. ≥ 15% is our target among the claims the tool "
           "screens, not a projection for all applications. No path ends in a denial: a denial is always decided by "
           "a person.")

st.subheader("Inside step 4")
steps = [("1 Read", "AI fills a checklist, quoting the file with page numbers"),
         ("2 Verify", "Code checks each quote is on its page, and who wrote the record"),
         ("3 Rules", "Spinal cord 11.08 · lung cancer 13.14 · dialysis 6.03 · age grid"),
         ("4 Route", "Rule met with verified evidence and all checks passed: recommend. Otherwise: human queue"),
         ("5 Examiner", "Reviews the evidence and decides")]
cols = st.columns(5)
for c, (h, t) in zip(cols, steps):
    c.markdown(f'<div class="ft-card"><b style="color:#2F6FB3">{h}</b><br><span class="sub">{t}</span></div>',
               unsafe_allow_html=True)

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
        st.markdown(f'<div class="ft-card"><div class="sub">Stress set (tested gaming cases)</div>'
                    f'<div class="big">{len(wrong)}/{len(gaming)}</div>reached the fast track</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="ft-card">No stress run saved yet.</div>', unsafe_allow_html=True)
with c3:
    n = sum(len(r["rows"]) for r in runs if r["reader"].startswith("Gemini"))
    st.markdown(f'<div class="ft-card"><div class="sub">All Gemini runs (demo, calibration, stress)</div>'
                f'<div class="big">0</div>automated denials, in {n} case reads. The code has no way to deny.</div>',
                unsafe_allow_html=True)
