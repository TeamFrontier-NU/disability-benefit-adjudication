from __future__ import annotations

import time

import streamlit as st

from fasttrack.metrics import DecisionLog, decision_metrics
from frontier_ui import replay
from frontier_ui.talk import speaker
from frontier_ui.common import (ROOT, SET_LABEL, case_list, checklist_table, connector, document_viewer, flags_block,
                                is_live, load_case, page_header, pipeline_steps, route_banner, rule_cards, run_live,
                                run_replay)

page_header("Case explorer", "Pick a case, then press **Run AI sorting**.")
speaker("demo")
LOG = DecisionLog(ROOT / "data" / "decisions.jsonl")
cases = case_list()
by_id = {c["case_id"]: c for c in cases}
if "case_id" not in st.session_state or st.session_state["case_id"] not in by_id:
    st.session_state["case_id"] = "demo-001" if "demo-001" in by_id else cases[0]["case_id"]


def card_grid(group: list[dict], per_row: int = 4):
    for i in range(0, len(group), per_row):
        cols = st.columns(per_row)
        for col, c in zip(cols, group[i:i + per_row]):
            sel = c["case_id"] == st.session_state["case_id"]
            sub = c["profile"] if c["case_set"] == "calibration" else c["case_id"]
            cached = "" if replay.has(c["case_id"]) else " · not recorded"
            if col.button(f"**{c['name']}**  \n{sub}{cached}", key=f"pick-{c['case_id']}",
                          type="primary" if sel else "secondary", width="stretch"):
                st.session_state["case_id"] = c["case_id"]
                st.rerun()


for s, opened in [("demo", True), ("stress", True), ("calibration", False)]:
    group = [c for c in cases if c["case_set"] == s]
    if group:
        with st.expander(f"{SET_LABEL[s]} cases ({len(group)})", expanded=opened):
            card_grid(group)

cid = st.session_state["case_id"]
meta = by_id[cid]
case = load_case(cid)
st.markdown(f"## {meta['name']}  \n{SET_LABEL[meta['case_set']]} set · {cid} · claim type {case.claim_type} · "
            f"filed {case.filing_date} · {len(case.documents)} documents")

runs = st.session_state.setdefault("explorer_runs", {})
mode = "live" if is_live() else "replay"
rk = (cid, mode)

tab_ai, tab_study = st.tabs(["AI sorting", "Examiner study"])

with tab_ai:
    if mode == "replay" and not replay.has(cid):
        st.warning("No recorded Gemini output for this case yet. The team records it once with "
                   "`python scripts/build_reader_cache.py` (needs the key; about 1¢ a case).")
    label = "Run AI sorting (live Gemini call)" if mode == "live" else "Run AI sorting"
    clicked = st.button(label, type="primary", disabled=(mode == "replay" and not replay.has(cid)))
    steps = st.empty()
    if clicked:
        with st.spinner("Reading the case file…" if mode == "live" else "Loading recorded output…"):
            res = run_live(case) if mode == "live" else run_replay(case)
        runs[rk] = res
        for lit in range(1, 5):
            with steps.container():
                pipeline_steps(res, lit)
            time.sleep(0.45)
    res = runs.get(rk)
    if res is not None and not clicked:
        with steps.container():
            pipeline_steps(res, 4)

    if res is not None:
        err = next((m for m in res.read.missing_evidence if str(m).startswith("Reader failed")), "")
        if err:
            st.error(f"The reader failed, so the case goes to a person: {err}")
        if mode == "replay":
            when = replay.recorded_at(cid) if hasattr(replay, "recorded_at") else ""
            st.caption(f"🔁 **Replay:** the reader’s output was recorded earlier{f' ({when})' if when else ''} "
                       "with Gemini 3.7 Flash. The quote check, the source rule, the rules and the routing just ran now. "
                       "Switch on Live mode to have Gemini read the file again.")
        else:
            st.caption("🟢 **Live:** Gemini 3.7 Flash read this file just now; everything after it ran now too.")
        route_banner(res)
        cost = ""
        if res.read.input_tokens:
            cost = f" · {res.read.input_tokens + res.read.output_tokens:,} tokens"
        st.caption(f"{res.read.reader}{cost} · k = {res.k} · same locked prompt, checklist and rules")
        left, right = st.columns([3, 2])
        with right:
            st.subheader("Rule check")
            st.caption("Click a page number to jump to the quote.")
            rule_cards(res)
            st.subheader("Flags")
            flags_block(res)
            if res.read.evidence_for_approval:
                st.subheader("Evidence for approval")
                for ev in res.read.evidence_for_approval:
                    st.markdown(f"- p. {ev.get('page')}: “{ev.get('quote', '')}” ({ev.get('why', '')})"
                                + ("" if ev.get("verified", True) else " *(quote not found)*"))
            if res.read.missing_evidence:
                st.subheader("Missing evidence")
                for m in res.read.missing_evidence:
                    st.markdown(f"- {m}")
        with left:
            st.subheader("Case file")
            document_viewer(case, res)
        with st.expander("Full checklist (every item the reader filled in)"):
            checklist_table(res)
    else:
        st.subheader("Case file")
        document_viewer(case, None)

with tab_study:
    st.caption("For the examiner timing study (BUILD-PLAN Step 8): a volunteer decides the case, and the panel "
               "times it. Human-only mode hides the AI output. On the shared web link, decisions are kept only "
               "until the app restarts, so run the study on the local copy.")
    a, b = st.columns(2)
    examiner = a.text_input("Examiner name", value=st.session_state.get("examiner", "Examiner 1"))
    st.session_state["examiner"] = examiner
    study_mode = b.radio("Review mode", ["Human + AI", "Human only (AI hidden)"], horizontal=True)
    mode_key = "human_plus_ai" if study_mode.startswith("Human +") else "human_only"
    opened_at = st.session_state.setdefault("opened", {})
    opened_at.setdefault((cid, mode_key), time.time())
    study_res = runs.get(rk) if mode_key == "human_plus_ai" else None
    if mode_key == "human_plus_ai":
        if study_res is None:
            st.info("Run AI sorting on the first tab to show the AI's route here.")
        else:
            route_banner(study_res)
    else:
        st.info("Human-only mode: AI output hidden. Review the case file and decide.")
    with st.form(f"decide-{cid}-{mode_key}"):
        decision = st.radio("Decision", ["allow", "deny", "need_more_evidence"], horizontal=True,
                            format_func={"allow": "Allow", "deny": "Deny",
                                         "need_more_evidence": "Need more evidence / CE"}.get)
        basis = st.text_input("Basis (e.g. meets 11.08A, grid 201.09, not severe at Step 2)")
        note = st.text_area("Note", height=70)
        if st.form_submit_button("Record final decision", type="primary"):
            if decision == "deny" and not basis.strip():
                st.error("A denial needs a written basis from the examiner.")
            else:
                secs = time.time() - opened_at[(cid, mode_key)]
                LOG.add(case_id=cid, case_set=case.case_set, examiner=examiner, mode=mode_key,
                        ai_route=study_res.routing.route if study_res else None,
                        reader=study_res.read.reader if study_res else None,
                        final_decision=decision, basis=basis, note=note, seconds=round(secs, 1))
                opened_at.pop((cid, mode_key), None)
                st.success(f"Recorded: {decision} ({secs / 60:.1f} min).")
    if mode_key == "human_only":
        with st.expander("Case file", expanded=True):
            document_viewer(case, None)
    keys = {c["case_id"]: connector().answer_key(c["case_id"]) for c in cases}
    keys = {k_: v for k_, v in keys.items() if v}
    log = [d for d in LOG.all() if d.get("case_id") in keys]
    if log:
        st.subheader("Decisions so far: human only vs. human + AI")
        dm = decision_metrics(log, keys)
        st.dataframe([{"Arm": {"human_only": "Human only", "human_plus_ai": "Human + AI"}[a_], "Decisions": v["decisions"],
                       "Accuracy vs answer key": str(v["accuracy"]), "Wrongful denials": str(v["wrongful_denials"]),
                       "Median minutes": str(v["median_minutes"])} for a_, v in dm.items()],
                     width="stretch", hide_index=True)
        st.download_button("Download decision log", data="\n".join(__import__("json").dumps(d) for d in log),
                           file_name="decisions.jsonl")
