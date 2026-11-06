from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from fasttrack.metrics import routing_metrics, stress_metrics, wilson
from fasttrack.reader import PRICES
from frontier_ui.common import BLUE, NAVY, ORANGE, SCANNED, page_header, saved_runs

page_header("Results so far", "Every number is from a saved batch run in `results/`, with a Wilson 95% confidence "
                              "interval. **Not evidence for the claim yet**: these are calibration and stress sets.")

runs = saved_runs()
ok = [r for r in runs if not r["failed"]]
NAMES = {"fast_track_rate": "Fast-track rate", "fast_track_precision": "Fast-track precision (eligible)",
         "fast_track_recall_of_eligible": "Eligible cases fast-tracked", "route_matches_design": "Route matches answer key",
         "ai_denials": "Denials made by the AI", "quote_verification_rate": "Quotes found on the cited page",
         "mean_seconds_per_case": "AI seconds per case"}
TARGET = {"fast_track_rate": "at least 15%", "fast_track_precision": "at least 95%", "ai_denials": "0"}


def when(r):
    return r["run_at"].replace("T", " ")[:16]


def metric_table(r):
    m = routing_metrics(r["rows"])
    st.dataframe([{"Measure": NAMES[k], "Result": str(m[k]), "Target": TARGET.get(k, "reported")} for k in NAMES],
                 width="stretch", hide_index=True)


# ----------------------------------------------------------------------------- calibration
st.header("Calibration set (10 cases)")
cal1 = [r for r in ok if r["set"] == "calibration" and r["k"] == 1 and r["reader"].startswith("Gemini")]
cal2 = [r for r in ok if r["set"] == "calibration" and r["k"] == 2 and r["reader"].startswith("Gemini")]
if cal1:
    rows = []
    for i, r in enumerate(cal1, 1):
        raw = routing_metrics(r["rows"])["_raw"]
        match = sum((x["route"] == "fast_track") == x["key_fast_track"] for x in r["rows"])
        for name, k, n in [("Route matches answer key", match, raw["n"]), ("Fast-track rate", raw["ft"], raw["n"])]:
            p, lo, hi = wilson(k, n)
            rows.append(dict(run=f"Run {i} · {when(r)[11:]}", measure=name, value=p * 100, lo=lo * 100, hi=hi * 100,
                             label=f"{k}/{n}"))
    df = pd.DataFrame(rows)
    base = alt.Chart(df).encode(y=alt.Y("run:N", title=None), x=alt.X("value:Q", title="percent", scale=alt.Scale(domain=[0, 100])))
    bars = base.mark_bar(color=BLUE, height=22).encode(tooltip=["run", "measure", "label"])
    err = base.mark_rule(color=NAVY, strokeWidth=2).encode(x="lo:Q", x2="hi:Q")
    text = base.mark_text(align="left", dx=6, color=NAVY, fontSize=14).encode(text="label:N")
    chart = alt.layer(bars, err, text).properties(height=110, width=520).facet(
        row=alt.Row("measure:N", title=None, header=alt.Header(labelFontSize=15, labelAngle=0, labelAlign="left")))
    st.altair_chart(chart)
    st.caption("Lines show the Wilson 95% confidence interval. The fast-track rate target (at least 15%) is for the "
               "test set; calibration has more eligible cases than the test mix.")
    st.markdown(f"**k = 1, {len(cal1)} run{'s' if len(cal1) > 1 else ''}.** Measures from the latest run:")
    metric_table(cal1[-1])
    same = all({x["case_id"]: x["route"] for x in r["rows"]} == {x["case_id"]: x["route"] for x in cal1[0]["rows"]}
               for r in cal1)
    if len(cal1) > 1:
        st.markdown(("✔ Every case got the same route in all runs." if same else
                     "⚠ Some cases changed route between runs (see `scripts/compare_runs.py`)."))
if cal2:
    with st.expander("k = 2 (not used): why every case goes to a person"):
        metric_table(cal2[-1])
        st.markdown("**Issue I-15:** no fast-track case in our data has two medical-source records stating the key "
                    "finding, so k = 2 sends every case to a person by construction. k = 1 was chosen because the data "
                    "can't tell the two apart, not because calibration preferred it.")

# ----------------------------------------------------------------------------- stress
st.header("Stress set (8 gaming cases)")
stress = [r for r in ok if r["set"] == "stress" and r["reader"].startswith("Gemini")]
if stress:
    r = stress[-1]
    s = stress_metrics(r["rows"])
    c1, c2 = st.columns(2)
    c1.metric("Gaming cases put on the fast track", s["gaming_cases_wrongly_fast_tracked"].split(" (")[0], help=s["gaming_cases_wrongly_fast_tracked"])
    c2.metric("Honest controls sent to a person", s["honest_controls_sent_to_human"].split(" (")[0], help=s["honest_controls_sent_to_human"])
    st.dataframe([{"Case": x["profile"], "Route": "Fast track" if x["route"] == "fast_track" else "Human queue",
                   "Should be": "Fast track" if x["key_fast_track"] else "Human queue",
                   "Match": "yes" if (x["route"] == "fast_track") == x["key_fast_track"] else "NO"} for x in r["rows"]],
                 width="stretch", hide_index=True)
    st.caption(f"Run {when(r)}. Target: 0 gaming cases on the fast track. " + s["gaming_cases_wrongly_fast_tracked"])
else:
    st.info("No stress run saved.")

# ----------------------------------------------------------------------------- scanned
st.header("Scanned-record sample")
scan_runs = [r for r in ok if r["set"] == "scanned"]
img = SCANNED / "scan_levels_demo-001_p4.png"
if scan_runs or img.exists():
    if img.exists():
        st.image(str(img), caption="The same page at three scan qualities (clean, fax, poor)")
    for r in scan_runs:
        st.markdown(f"**{when(r)}**")
        metric_table(r)
else:
    st.info("Not in this build yet: no scanned-record cases or results were found in `data/scanned/`.")

# ----------------------------------------------------------------------------- all runs + spend
st.header("Every saved run")
tbl = []
for r in runs:
    m = r.get("metrics", {})
    tok = r.get("tokens") or {}
    model = r["reader"].split("(")[-1].rstrip(")") if "(" in r["reader"] else r["reader"]
    p_in, p_out = PRICES.get(model, (0, 0))
    cost = (tok.get("input", 0) * p_in + tok.get("output", 0) * p_out) / 1e6
    tbl.append({"Run": when(r), "Set": r["set"], "k": r["k"], "Reader": r["reader"],
                "Route matches key": str(m.get("route_matches_design", "")).split(" (")[0],
                "Status": "failed call (wrong model name), kept as a record" if r["failed"] else "ok",
                "Tokens": f"{tok.get('input', 0) + tok.get('output', 0):,}", "Est. cost": f"${cost:.3f}"})
st.dataframe(tbl, width="stretch", hide_index=True)
total = 0.0
for r in runs:
    tok = r.get("tokens") or {}
    model = r["reader"].split("(")[-1].rstrip(")") if "(" in r["reader"] else ""
    p_in, p_out = PRICES.get(model, (0, 0))
    total += (tok.get("input", 0) * p_in + tok.get("output", 0) * p_out) / 1e6
st.metric("Reader spend so far (estimate)", f"${total:.2f}",
          help="Token counts from the saved runs × Gemini 3.7 Flash list price ($0.75 / $3.75 per million, "
               "introductory until Dec 31, 2026). The Google Cloud billing page is the real figure.")
st.caption("Estimate from token counts at list price. The real figure is on the Google Cloud billing page. "
           "The largest line in the course budget is the Claude Pro subscription, not the API.")
