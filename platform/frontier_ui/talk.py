"""The halfway presentation: who presents which page, for how long, and the shared numbers.

Change the names here and every page follows. UI only: nothing here touches the locked pipeline.
"""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

# Proposed split for the 8-minute presentation. Swap names freely; keep the times adding up to 8:00.
AGENDA = [
    dict(key="fits", page="1 · Where it fits", speaker="Zhiying Cui", minutes="1:00",
         cue="The applicant’s path today vs. with our tool. QDD/CAL stays; we add a second screen on the "
             "medical records. Never denies."),
    dict(key="standing", page="2 · Where we stand", speaker="Yiling Long", minutes="1:30",
         cue="Works / not yet / changed since the pitch and what we dropped. Spend so far (61 cases, kept small "
             "while the budget isn’t approved; largest line Claude Pro), then the projected cost of 500–1,000 "
             "cases and what switching to Claude would add."),
    dict(key="demo", page="3 · Demo: Joe and Peter", speaker="Yanqi Wu", minutes="1:15",
         cue="Replay mode. Joe → fast track (11.08), show the quotes; Peter → human queue: “not picked means "
             "normal review, not a denial.”"),
    dict(key="attacks", page="4 · Demo: attacks and a new case", speaker="Yihang Ye", minutes="2:00",
         cue="Safeguards page: one recorded attack (instant). Then New case (live) with the discussant’s or "
             "instructor’s input. A live run takes about 90 seconds: press Run, then explain the steps while it "
             "works."),
    dict(key="evaluation", page="5 · Evaluation plan", speaker="Xinhui Zong", minutes="1:30",
         cue="Claim, threshold, counterfactual, assignment. How and on whom. Read the power table out loud."),
    dict(key="next", page="6 · Decisions and next steps", speaker="Yixuan Wen", minutes="0:45",
         cue="Two decisions, asked as questions to the room. Then next steps in one breath."),
]
BY_KEY = {a["key"]: a for a in AGENDA}

# Course budget lines (USD). Claude Pro is the plan figure from the design pitch (2 months, $20 + tax);
# confirm it against the billing page before presenting.
CLAUDE_PRO_USD = 46.0
CAP_USD = 200.0


def speaker(key: str):
    """A small line under the page title: who presents this part and roughly how long."""
    a = BY_KEY.get(key)
    if a:
        st.markdown(f'<div style="color:#4A5568;font-size:0.95rem;margin:-6px 0 8px 0">'
                    f'<b>{a["page"]}</b> · presented by <b>{a["speaker"]}</b> · about {a["minutes"]}</div>',
                    unsafe_allow_html=True)


def run_of_show():
    """Sidebar table for the team (collapsed by default)."""
    with st.expander("Run of show (8 min)"):
        for a in AGENDA:
            st.markdown(f"**{a['minutes']} · {a['page']}**  \n{a['speaker']}  \n"
                        f"<span style='font-size:0.85rem;color:#4A5568'>{a['cue']}</span>",
                        unsafe_allow_html=True)


def api_spend() -> tuple[float, int]:
    """Estimated Gemini spend from every saved run plus the Replay recording, at list price.

    Returns (dollars, tokens). Live runs in this browser session are added on top by the caller.
    """
    from fasttrack.reader import PRICES
    p_in, p_out = PRICES.get("gemini-3.7-flash", (0.0, 0.0))
    t_in = t_out = 0
    for f in sorted(RESULTS.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("set") == "test":
            continue
        tok = d.get("tokens") or {}
        if d.get("reader", "").startswith("Gemini"):
            t_in += tok.get("input", 0)
            t_out += tok.get("output", 0)
    for f in sorted((RESULTS / "reader_cache").glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))["read"]
        except Exception:
            continue
        t_in += r.get("input_tokens", 0) or 0
        t_out += r.get("output_tokens", 0) or 0
    return (t_in * p_in + t_out * p_out) / 1e6, t_in + t_out


# ----------------------------------------------------------------------------- projected budget
# USD per million tokens (input, output). Gemini: list price we use in reader.py (introductory until Dec 31, 2026,
# then doubling). Claude: the price table in our design pitch (Sonnet 5.5 $0.021 and Opus 5.5 $0.042 per
# 3k-in / 1.5k-out call). Confirm all of them before the final budget request.
PROJECTION_PRICES = {
    "Gemini 3.7 Flash (now)": (0.75, 3.75),
    "Gemini 3.7 Flash (from 2027)": (1.50, 7.50),
    "Claude Sonnet 5.5": (2.0, 10.0),
    "Claude Opus 5.5": (4.0, 20.0),
}
CASES_SO_FAR = 61          # simulated cases built so far (demo 3, calibration 10, test 40, stress 8)


def avg_tokens_per_read() -> tuple[float, float]:
    """Average input and output tokens per reader call, measured on the Replay recording (Gemini 3.7 Flash)."""
    t_in = t_out = n = 0
    for f in sorted((RESULTS / "reader_cache").glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))["read"]
        except Exception:
            continue
        if r.get("input_tokens"):
            t_in += r["input_tokens"]
            t_out += r.get("output_tokens", 0) or 0
            n += 1
    return (t_in / n, t_out / n) if n else (2300.0, 2200.0)


def projected_cost(cases: int, reads: list[tuple[str, int]], length: float = 2.0) -> float:
    """Dollars for `cases` cases, each read `reads` times per model, with files `length` times our current ones."""
    t_in, t_out = avg_tokens_per_read()
    total = 0.0
    for model, n in reads:
        p_in, p_out = PROJECTION_PRICES[model]
        total += cases * n * length * (t_in * p_in + t_out * p_out) / 1e6
    return total
