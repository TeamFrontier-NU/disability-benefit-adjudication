"""Shared pieces for the presentation app: paths, colours, case lists, runs and display blocks.

Only UI code lives here. Reading, verifying, scoring and routing all go through the locked
`fasttrack` package unchanged.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

import streamlit as st

from fasttrack.intake import LocalFolderConnector
from fasttrack.models import RECEIVED_VIA, RULE_SOURCES, SOURCE_TYPES, Case
from fasttrack.pipeline import RunResult, run_case

from . import replay

ROOT = Path(__file__).resolve().parents[1]
SIM = ROOT / "data" / "simulated"
SCANNED = ROOT / "data" / "scanned"
RESULTS = ROOT / "results"
K_LOCKED = 1
SHOWN_SETS = ("demo", "stress", "calibration")      # the test set is never listed, run or shown

NAVY, BLUE, ORANGE, BG = "#14213D", "#2F6FB3", "#A8520F", "#FBFBF8"
GREEN_HL, YELLOW_HL, RED_HL, BLUE_HL = "#D6EFD8", "#FFF0B8", "#FFD9D2", "#E3ECF7"

SET_LABEL = {"demo": "Demo", "stress": "Stress (gaming)", "calibration": "Calibration", "scanned": "Scanned records"}


# ----------------------------------------------------------------------------- page chrome

CSS = f"""
<style>
html, body, [class*="css"] {{ font-size: 18px; }}
h1, h2, h3 {{ color: {NAVY}; }}
.ft-banner {{ border-radius: 10px; padding: 14px 20px; margin: 6px 0 14px 0; font-size: 1.25rem; font-weight: 600; }}
.ft-fast {{ background: {BLUE}; color: white; }}
.ft-human {{ background: {ORANGE}; color: white; }}
.ft-note {{ background: #EEF2F8; color: {NAVY}; border-left: 6px solid {NAVY}; font-size: 1rem; font-weight: 500; }}
.ft-card {{ background: white; border: 1px solid #DADCE0; border-radius: 12px; padding: 16px 18px; height: 100%; }}
.ft-card .big {{ font-size: 2.6rem; font-weight: 700; color: {NAVY}; line-height: 1.1; }}
.ft-card .sub {{ color: #4A5568; font-size: 0.95rem; }}
.ft-step {{ border-radius: 10px; padding: 10px 12px; text-align: center; border: 2px solid #CBD2DC; color: #8A94A6;
           background: white; font-weight: 600; }}
.ft-step.on {{ border-color: {NAVY}; color: {NAVY}; background: #EEF2F8; }}
.ft-step .n {{ font-size: 0.9rem; font-weight: 500; display: block; margin-top: 2px; }}
.ft-rule {{ background: white; border: 1px solid #DADCE0; border-radius: 10px; padding: 10px 14px; margin-bottom: 8px; }}
.ft-rule.met {{ border: 2px solid {BLUE}; }}
.ft-rule a {{ color: {BLUE}; }}
.ft-page {{ background: white; border: 1px solid #E2E4E8; border-radius: 8px; padding: 10px 14px; margin: 6px 0 10px 0;
           font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 0.9rem; line-height: 1.5; }}
.ft-inject {{ border: 3px solid #B42318; background: #FDECEA; border-radius: 6px; padding: 2px 6px; }}
.ft-tag {{ display: inline-block; border-radius: 6px; padding: 2px 8px; margin: 2px 4px 2px 0; font-size: 0.85rem; }}
.ft-path {{ display: flex; flex-wrap: wrap; align-items: stretch; gap: 8px; margin: 6px 0; }}
.ft-box {{ flex: 1 1 130px; border-radius: 10px; padding: 10px; font-size: 0.95rem; text-align: center;
          border: 2px solid #CBD2DC; background: white; color: {NAVY}; }}
.ft-box.same {{ background: #F1F3F6; }}
.ft-box.new {{ border-color: {NAVY}; background: #EEF2F8; font-weight: 600; }}
.ft-box.fast {{ border-color: {BLUE}; color: {BLUE}; font-weight: 600; }}
.ft-box.human {{ border-color: {ORANGE}; color: {ORANGE}; font-weight: 600; }}
.ft-arrow {{ align-self: center; font-size: 1.4rem; color: #8A94A6; }}
</style>
"""


def page_header(title: str, subtitle: str = ""):
    st.markdown(CSS, unsafe_allow_html=True)
    st.title(title)
    if subtitle:
        st.markdown(subtitle)
    st.markdown('<div class="ft-banner ft-note">Simulated data only · calibration and stress results only · '
                'the test set has not been run</div>', unsafe_allow_html=True)


# ----------------------------------------------------------------------------- cases

@st.cache_resource
def connector() -> LocalFolderConnector:
    return LocalFolderConnector(SIM)


@st.cache_data
def case_list() -> list[dict]:
    """Every case the app may show: demo, stress and calibration. Never the test set."""
    profiles = {}
    idx = SIM / "index.json"
    if idx.exists():
        for e in json.loads(idx.read_text(encoding="utf-8")):
            if e.get("case_set") != "test":
                profiles[e["case_id"]] = e.get("profile", "")
    out = []
    for c in connector().list_cases():
        if c["case_set"] not in SHOWN_SETS:
            continue
        c = dict(c, profile=profiles.get(c["case_id"], ""))
        name = c["title"] if c["case_set"] in ("demo", "stress") else c["case_id"]
        c["name"] = name
        out.append(c)
    order = {s: i for i, s in enumerate(SHOWN_SETS)}
    return sorted(out, key=lambda c: (order[c["case_set"]], c["case_id"]))


def load_case(case_id: str) -> Case:
    case = connector().load_case(case_id)
    if case.case_set == "test":
        raise ValueError("The test set is not available in this app.")
    return case


def expected_fast_track(case_id: str) -> bool | None:
    """Answer key route for demo / stress / calibration only (used on the Safeguards page)."""
    case = load_case(case_id)
    key = connector().answer_key(case.case_id)
    return None if key is None else bool(key.get("fast_track"))


# ----------------------------------------------------------------------------- runs

def run_replay(case: Case, variant: str = "base", safeguards: bool = True) -> RunResult | None:
    """Run the locked pipeline on recorded reader output. None if nothing was recorded for this case."""
    if not replay.has(case.case_id, variant):
        return None
    return run_case(case, replay.ReplayReader(variant), K_LOCKED, safeguards)


def run_live(case: Case, safeguards: bool = True) -> RunResult:
    res = run_case(case, replay.live_reader(), K_LOCKED, safeguards)
    from fasttrack.reader import PRICES
    p_in, p_out = PRICES.get("gemini-3.7-flash", (0, 0))
    cost = res.read.input_tokens * p_in / 1e6 + res.read.output_tokens * p_out / 1e6
    st.session_state.setdefault("live_log", []).append(
        dict(case_id=case.case_id, input_tokens=res.read.input_tokens, output_tokens=res.read.output_tokens,
             cost_usd=round(cost, 4), route=res.routing.route))
    return res


def is_live() -> bool:
    return bool(st.session_state.get("live_ok"))


# ----------------------------------------------------------------------------- display blocks

def route_banner(res: RunResult):
    r = res.routing
    if r.route == "fast_track":
        label = r.reasons[0].replace("Meets ", "meets ")
        st.markdown(f'<div class="ft-banner ft-fast">➜ FAST TRACK: {html.escape(label)} '
                    f'(examiner checks the quotes and signs)</div>', unsafe_allow_html=True)
    else:
        seen, parts = set(), []
        for x in r.reasons:
            y = _plain_reason(x)
            if y not in seen:
                seen.add(y); parts.append(y)
        why = "; ".join(parts) or "needs an examiner"
        st.markdown(f'<div class="ft-banner ft-human">● HUMAN QUEUE: {html.escape(why)}</div>',
                    unsafe_allow_html=True)


def _plain_reason(x: str) -> str:
    x = x.rstrip(".")
    for k, v in {"instruction: ": "", "step1: ": "Step 1: ", "consistency: ": "facts don't match: ",
                 "repeat_filing: ": "repeat filing: "}.items():
        if x.startswith(k):
            x = v + x[len(k):]
    return x if len(x) < 160 else x[:157] + "…"


def step_counts(res: RunResult) -> list[tuple[str, str]]:
    items = res.read.items
    ver = sum(i.verified for i in items)
    counted = sum(i.counts_for_rules for i in items)
    met = [rr for rr in res.routing.rule_results if rr.met]
    route = "Fast track" if res.routing.route == "fast_track" else "Human queue"
    return [("1 Read", f"{len(items)} items read"),
            ("2 Verify", f"{ver} of {len(items)} quotes found · {counted} count for rules"),
            ("3 Rules", f"{len(met)} of {len(res.routing.rule_results)} paths met"),
            ("4 Route", route)]


def pipeline_steps(res: RunResult, lit: int = 4, holder=None):
    cols = (holder or st).columns(4)
    for i, (name, count) in enumerate(step_counts(res)):
        on = "on" if i < lit else ""
        cols[i].markdown(f'<div class="ft-step {on}">{name}<span class="n">{count if on else "…"}</span></div>',
                         unsafe_allow_html=True)


def rule_cards(res: RunResult):
    for rr in res.routing.rule_results:
        mark = "✓ met" if rr.met else "✗ not met"
        rows = []
        for cr in rr.criteria:
            links = ", ".join(f'<a href="#pg-{p}">p. {p}</a>' for p in cr["pages"])
            rows.append(f'{"✓" if cr["met"] else "✗"} {html.escape(cr["name"])}' + (f" ({links})" if links else ""))
        note = f'<br><small>{html.escape(rr.note)}</small>' if rr.note else ""
        st.markdown(f'<div class="ft-rule {"met" if rr.met else ""}"><b>{html.escape(rr.label)}</b> · {mark}<br>'
                    + "<br>".join(rows) + note + "</div>", unsafe_allow_html=True)


def source_color(doc) -> tuple[str, str]:
    if doc.received_via == "claimant" or doc.source_type == "third_party":
        return RED_HL, "third party or handed in by the claimant"
    if doc.source_type in RULE_SOURCES:
        return GREEN_HL, "medical source"
    if doc.source_type == "claimant_form":
        return YELLOW_HL, "claimant form"
    return BLUE_HL, "application (field office)"


def legend():
    st.markdown(" ".join(f'<span class="ft-tag" style="background:{c}">{t}</span>' for c, t in [
        (GREEN_HL, "Green: medical source"), (YELLOW_HL, "Yellow: claimant form"),
        (RED_HL, "Red: third party or handed in by the claimant"), (BLUE_HL, "Blue: application")])
        + ' <span class="ft-tag ft-inject">Red box: text addressed to the AI</span>', unsafe_allow_html=True)


def _mark(text: str, phrases: list[tuple[str, str]]) -> str:
    out = html.escape(text)
    for q, style in sorted(phrases, key=lambda x: -len(x[0])):
        eq = html.escape(q.strip())
        if len(eq) < 4:
            continue
        out = re.sub(re.escape(eq), lambda m: f'<span style="{style}">{m.group(0)}</span>', out, count=1, flags=re.I)
    return out.replace("\n", "<br>")


def document_viewer(case: Case, res: RunResult | None):
    legend()
    by_page: dict[int, list[tuple[str, str]]] = {}
    if res:
        for it in res.read.items:
            if it.verified:
                doc = case.doc_for_page(it.page)
                color = source_color(doc)[0] if doc else "#EEE"
                by_page.setdefault(it.page, []).append((it.quote, f"background:{color};padding:0 2px;border-radius:3px"))
        for f in res.read.instruction_flags:
            if isinstance(f, dict) and f.get("quote"):
                by_page.setdefault(int(f.get("page", 0)), []).append(
                    (f["quote"], "border:3px solid #B42318;background:#FDECEA;padding:0 3px;border-radius:4px"))
    for doc in case.documents:
        color, label = source_color(doc)
        who = SOURCE_TYPES.get(doc.source_type, doc.source_type)
        via = RECEIVED_VIA.get(doc.received_via, doc.received_via)
        st.markdown(f'<span class="ft-tag" style="background:{color}">{html.escape(label)}</span> '
                    f'<b>{html.escape(doc.title)}</b> · {html.escape(who)} · {html.escape(via)}'
                    + (f" · {html.escape(doc.provider)}" if doc.provider else ""), unsafe_allow_html=True)
        for p, text in sorted(doc.pages.items()):
            st.markdown(f'<div class="ft-page" id="pg-{p}"><b>Page {p}</b><br>{_mark(text, by_page.get(p, []))}</div>',
                        unsafe_allow_html=True)


def flags_block(res: RunResult):
    flags = [f for f in res.routing.flags if f["type"] != "label_only"]
    if not flags:
        st.markdown("No flags.")
        return
    names = {"step1": "Step 1 (work)", "instruction": "Text addressed to the AI", "provenance": "Where a record came from",
             "consistency": "Dates or facts don't match", "repeat_filing": "Repeat filing", "quote_check": "Quote check"}
    for f in flags:
        page = f" (p. {f['page']})" if f.get("page") not in (None, "") else ""
        st.markdown(f"- **{names.get(f['type'], f['type'])}**: {f['detail']}{page}")


def checklist_table(res: RunResult):
    rows = [{"Field": i.field, "Value": str(i.value), "Page": str(i.page),
             "Source": SOURCE_TYPES.get(i.source_type, i.source_type).split(" (")[0],
             "Quote found": "yes" if i.verified else "no", "Counts for rules": "yes" if i.counts_for_rules else "no",
             "Why not": i.drop_reason, "Quote": i.quote} for i in res.read.items]
    st.dataframe(rows, width="stretch", hide_index=True, height=300)


# ----------------------------------------------------------------------------- saved results

@st.cache_data
def saved_runs() -> list[dict]:
    """Batch results files, minus failed calls and minus anything from the test set."""
    out = []
    for f in sorted(RESULTS.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if d.get("set") == "test" or "rows" not in d:
            continue
        rows = d["rows"]
        failed = (d.get("reader", "").startswith("Gemini") and not d.get("tokens")) or \
                 (rows and all(r.get("reader_error") for r in rows))
        d["file"], d["failed"] = f.name, bool(failed)
        out.append(d)
    return out
