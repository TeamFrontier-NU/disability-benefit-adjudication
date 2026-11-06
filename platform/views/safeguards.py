from __future__ import annotations

import html

import streamlit as st

from fasttrack.intake import _pdf_pages
from fasttrack.models import RECEIVED_VIA, SOURCE_TYPES, Document
from frontier_ui import replay
from frontier_ui.talk import speaker
from frontier_ui.common import (case_list, document_viewer, expected_fast_track, flags_block, is_live, load_case,
                                page_header, route_banner, run_live, run_replay)

page_header("Safeguards and adversarial tests",
            "What happens when someone tries to game the tool? Each safeguard can only move a claim **to a person**, "
            "never onto the fast track.")
speaker("attacks")

st.subheader("Stress set: safeguards ON vs OFF")
st.caption("Same recorded reader output for each case, run through the locked rules twice: once as built, and once "
           "with the source rule, provenance check and instruction check switched off (demo only).")
stress = [c for c in case_list() if c["case_set"] == "stress"]
WORD = {"fast_track": "Fast track", "human_queue": "Human queue"}
STOP = {"instruction": "instruction check", "provenance": "provenance check (who sent the record)",
        "consistency": "consistency check", "step1": "Step 1 work check", "repeat_filing": "repeat-filing check",
        "quote_check": "quote check"}
rows, missing = [], []
for c in stress:
    case = load_case(c["case_id"])
    on, off = run_replay(case, safeguards=True), run_replay(case, safeguards=False)
    if on is None:
        missing.append(c["name"])
        continue
    exp = expected_fast_track(c["case_id"])
    slipped = off.routing.route == "fast_track" and exp is False
    rows.append({"Case": c["name"], "Should be": WORD["fast_track" if exp else "human_queue"] if exp is not None else "",
                 "Safeguards ON": ("✔ " if (on.routing.route == "fast_track") == exp else "✘ ") + WORD[on.routing.route],
                 "Safeguards OFF": ("⚠ " if slipped else "") + WORD[off.routing.route],
                 "What stops it": "; ".join(dict.fromkeys(STOP.get(f["type"], f["type"]) for f in on.routing.flags
                                                         if f["type"] != "label_only")) or
                                  ("no rule met with medical-source evidence (source rule)" if on.routing.route != "fast_track"
                                   else "")})
if rows:
    st.dataframe(rows, width="stretch", hide_index=True)
    n_slip = sum(r["Safeguards OFF"].startswith("⚠") for r in rows)
    st.markdown(f"**With safeguards on, no gaming case reaches the fast track. With them off, {n_slip} "
                f"gaming case{'s' if n_slip != 1 else ''} would slip through (marked ⚠).**")
if missing:
    st.warning("No recorded output yet for: " + ", ".join(missing) + ". Run `scripts/build_reader_cache.py`.")

st.divider()
st.subheader("Try to fool it")
results = st.session_state.setdefault("fool_runs", {})

if not is_live():
    st.markdown("**Replay mode:** three pre-recorded attacks on Peter's claim (a lumbar strain that should go to a "
                "person). Live attacks with your own text need the presenter's Live mode.")
    choice = st.radio("Attack", list(replay.ADVERSARIAL), format_func=lambda k: replay.ADVERSARIAL[k]["label"],
                      horizontal=True)
    spec = replay.ADVERSARIAL[choice]
    base = load_case(spec["base_case"])
    attacked = load_case(spec["base_case"])
    attacked.documents.append(replay.adversarial_document(attacked, choice))
    if not replay.has(spec["base_case"], choice) or not replay.has(spec["base_case"]):
        st.warning("This example hasn't been recorded yet. Run `scripts/build_reader_cache.py`.")
    elif st.button("Run the attack", type="primary"):
        results["replay"] = (choice, run_replay(base), run_replay(attacked, choice),
                             run_replay(attacked, choice, safeguards=False))
    show = results.get("replay")
    if show and show[0] == choice:
        _, before, after, after_off = show
        case_for_view = attacked
else:
    st.markdown("**Live mode:** add your own document to a case and run the real reader on it (about 1¢).")
    options = {c["case_id"]: f"{c['name']} ({c['case_id']})" for c in case_list()}
    cid = st.selectbox("Case to attack", list(options), format_func=options.get,
                       index=list(options).index("demo-002") if "demo-002" in options else 0)
    with st.form("fool"):
        text = st.text_area("Document text (or upload a file below)", height=150)
        up = st.file_uploader("PDF or TXT", type=["pdf", "txt", "md"])
        a, b, c = st.columns(3)
        stype = a.selectbox("Who it claims to come from", list(SOURCE_TYPES), format_func=SOURCE_TYPES.get, index=2)
        via = b.selectbox("How it arrived", list(RECEIVED_VIA), format_func=RECEIVED_VIA.get, index=2)
        prov = c.text_input("Provider / facility")
        go = st.form_submit_button("Add and run (live)", type="primary")
    if go:
        pages = []
        if up is not None:
            data = up.getvalue()
            pages = _pdf_pages(data) if up.name.lower().endswith(".pdf") else [data.decode("utf-8", "replace")]
        if text.strip():
            pages.append(text)
        pages = [p for p in pages if p.strip()]
        if not pages:
            st.error("Paste some text or upload a file first.")
        else:
            base = load_case(cid)
            attacked = load_case(cid)
            start = max(p for d in attacked.documents for p in d.pages) + 1
            attacked.documents.append(Document(doc_id="LIVE1", title=up.name if up else "Live test document",
                                               source_type=stype, received_via=via, provider=prov,
                                               pages={start + i: t for i, t in enumerate(pages)}))
            with st.spinner("Running the reader on the original and the attacked file…"):
                before = run_replay(base) or run_live(base)
                after = run_live(attacked)
            import copy
            from fasttrack.pipeline import route, verify
            read_off = copy.deepcopy(after.read)   # same reader output, fresh copy for the safeguards-off pass
            for it in read_off.items:
                it.verified, it.counts_for_rules, it.drop_reason = False, False, ""
            items_off = verify(attacked, read_off, safeguards=False)
            off_routing = route(attacked, items_off, read_off, after.k, safeguards=False)
            results["live"] = (cid, before, after, off_routing, attacked)
    show = results.get("live")
    if show and show[0] == cid:
        _, before, after, off_routing, case_for_view = show
        after_off = type("R", (), {"routing": off_routing})()

if (not is_live() and results.get("replay") and results["replay"][0] == choice) or \
        (is_live() and results.get("live") and results["live"][0] == cid):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**Before** (original file)")
        route_banner(before)
    with c2:
        st.markdown("**After the attack: the decision**")
        route_banner(after)
    with c3:
        st.markdown("**What-if only:** the same reading with the safeguards switched off. "
                    "<span style='color:#4A5568'>Not a decision; shown to explain what they stop.</span>",
                    unsafe_allow_html=True)
        r = after_off.routing
        cls = "ft-fast" if r.route == "fast_track" else "ft-human"
        word = "would be FAST TRACK" if r.route == "fast_track" else "would be HUMAN QUEUE"
        st.markdown(f'<div style="opacity:0.55"><div class="ft-banner {cls}" style="border:2px dashed #14213D">'
                    f'{word}: {html.escape((r.reasons or [""])[0])}</div></div>', unsafe_allow_html=True)
    st.subheader("What the safeguards caught")
    flags_block(after)
    with st.expander("Attacked case file, with highlights"):
        document_viewer(case_for_view, after)
