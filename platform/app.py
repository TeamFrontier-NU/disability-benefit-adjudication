"""Examiner review panel.

    streamlit run app.py

Flow: import or pick a case -> AI sorting (fast track or human queue) -> examiner
reviews the evidence -> examiner records the final decision. The AI never denies.
"""
from __future__ import annotations

import html
import json
import re
import time
from pathlib import Path

import streamlit as st

from fasttrack.intake import FileImport, LocalFolderConnector
from fasttrack.metrics import DecisionLog, decision_metrics, routing_metrics, stress_metrics
from fasttrack.models import Document, RECEIVED_VIA, SOURCE_TYPES, RULE_SOURCES
from fasttrack.pipeline import run_case
from fasttrack.reader import ClaudeReader, KeywordReader

ROOT = Path(__file__).parent
SIM, IMP = ROOT / "data" / "simulated", ROOT / "data" / "imported"
LOG = DecisionLog(ROOT / "data" / "decisions.jsonl")
COLORS = {"ams_record": "#cdeccd", "ce_report": "#cdeccd", "claimant_form": "#ffe9b3",
          "third_party": "#ffd6cc", "application": "#dbe7ff"}
ROUTE_LABEL = {"fast_track": "Fast track", "human_queue": "Human queue"}

st.set_page_config(page_title="Fast-Track Screening Panel", layout="wide")
IMP.mkdir(parents=True, exist_ok=True)
if not (SIM / "index.json").exists():  # first run: build the simulated cases (same seed = same cases)
    from fasttrack.simulate import generate
    generate(SIM, seed=425)

# ----------------------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Settings")
    source = st.radio("Case source", ["Simulated cases", "Imported files"], horizontal=True)
    con = LocalFolderConnector(SIM if source == "Simulated cases" else IMP)
    sets = sorted({c["case_set"] for c in con.list_cases()}) or ["(none)"]
    order = ["demo", "calibration", "test", "stress", "imported"]
    case_set = st.selectbox("Case set", sorted(sets, key=lambda s: order.index(s) if s in order else 9))
    reader_name = st.radio("Reader", ["Offline keyword baseline", "Claude API (Sonnet 5.5)"],
                           help="The Claude reader needs ANTHROPIC_API_KEY or `ant auth login` on this computer.")
    k = st.select_slider("AMS documents required per criterion", options=[1, 2], value=1,
                         help="The one setting tuned on the calibration cases, then locked.")
    safeguards = st.toggle("Safeguards on", value=True,
                           help="Demo only. Off = source rule, provenance and instruction checks switched off.")
    st.divider()
    examiner = st.text_input("Examiner name", value="Examiner 1")
    mode = st.radio("Review mode", ["Human + AI", "Human only (AI hidden)"],
                    help="Human-only mode hides the AI output so we can compare the two arms.")
    mode_key = "human_plus_ai" if mode.startswith("Human +") else "human_only"


@st.cache_resource
def get_reader(name):
    return ClaudeReader() if name.startswith("Claude") else KeywordReader()


def reader():
    try:
        return get_reader(reader_name)
    except Exception as e:
        st.error(f"Claude reader unavailable ({e}); using the offline baseline.")
        return get_reader("Offline")


runs = st.session_state.setdefault("runs", {})
extra_docs = st.session_state.setdefault("extra_docs", {})


def run_key(cid):
    return (str(con.root), cid, reader_name, k, safeguards, len(extra_docs.get(cid, [])))


def load(cid):
    case = con.load_case(cid)
    case.documents += extra_docs.get(cid, [])
    return case


def get_run(cid, force=False):
    rk = run_key(cid)
    if force or rk not in runs:
        runs[rk] = run_case(load(cid), reader(), k, safeguards)
    return runs[rk]


def highlight(text, quotes):
    out = html.escape(text)
    for q, color in quotes:
        eq = html.escape(q.strip())
        if len(eq) < 3:
            continue
        out = re.sub(re.escape(eq), lambda m: f'<mark style="background:{color};padding:0 2px">{m.group(0)}</mark>',
                     out, flags=re.I)
    return out.replace("\n", "<br>")


st.title("Fast-Track Screening Panel")
st.caption("Initial adult SSI/SSDI claims · simulated data only · the AI can send a claim to the fast track, "
           "but every denial is decided by a person.")
tab_q, tab_c, tab_i, tab_r = st.tabs(["Queue", "Case review", "Import files", "Results"])

# ----------------------------------------------------------------------------- queue
with tab_q:
    cases = con.list_cases(case_set) if case_set != "(none)" else []
    c1, c2 = st.columns([1, 4])
    if c1.button("Run AI sorting on this set", type="primary", disabled=not cases):
        bar = st.progress(0.0)
        for i, c in enumerate(cases):
            get_run(c["case_id"])
            bar.progress((i + 1) / len(cases))
    rows = []
    for c in cases:
        r = runs.get(run_key(c["case_id"]))
        rows.append({"Case": c["case_id"], "Title": c["title"], "Claim": c["claim_type"],
                     "AI route": ROUTE_LABEL[r.routing.route] if r else "not run",
                     "Path": r.routing.path if r else "",
                     "Flags": len([f for f in r.routing.flags if f["type"] != "label_only"]) if r else "",
                     "Decided": "yes" if any(d["case_id"] == c["case_id"] for d in LOG.all()) else ""})
    if mode_key == "human_only":
        for row in rows:
            row["AI route"], row["Path"], row["Flags"] = "hidden", "", ""
    st.dataframe(rows, use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------- case review
with tab_c:
    cases = con.list_cases(case_set) if case_set != "(none)" else []
    if not cases:
        st.info("No cases in this set.")
    else:
        cid = st.selectbox("Case", [c["case_id"] for c in cases],
                           format_func=lambda x: f"{x} · {next(c['title'] for c in cases if c['case_id'] == x)}")
        opened = st.session_state.setdefault("opened", {})
        opened.setdefault((cid, mode_key), time.time())
        case = load(cid)
        res = get_run(cid) if mode_key == "human_plus_ai" else None

        left, right = st.columns([3, 2])
        with left:
            st.subheader("Case file")
            st.markdown(" ".join(f'<span style="background:{COLORS[t]};padding:2px 6px;border-radius:4px;'
                                 f'font-size:0.8em">{SOURCE_TYPES[t]}</span>' for t in COLORS if t != "ce_report"),
                        unsafe_allow_html=True)
            quotes_by_page = {}
            if res:
                for it in res.read.items:
                    if it.verified:
                        color = COLORS.get(it.source_type, "#eee") if it.counts_for_rules or it.source_type not in RULE_SOURCES else "#eeeeee"
                        quotes_by_page.setdefault(it.page, []).append((it.quote, color))
            for doc in case.documents:
                tag = f"{SOURCE_TYPES.get(doc.source_type, doc.source_type)} · {RECEIVED_VIA.get(doc.received_via, doc.received_via)}"
                with st.expander(f"{doc.title}  —  pages {', '.join(map(str, sorted(doc.pages)))}", expanded=True):
                    st.caption(tag + (f" · {doc.author} {doc.credential}".rstrip() if doc.author else ""))
                    for p, text in sorted(doc.pages.items()):
                        st.markdown(f"**Page {p}**<br>{highlight(text, quotes_by_page.get(p, []))}",
                                    unsafe_allow_html=True)

        with right:
            if res:
                r = res.routing
                if r.route == "fast_track":
                    st.success(f"**AI route: Fast track** — {r.reasons[0]}. Examiner checks the quotes and signs.")
                else:
                    st.warning("**AI route: Human queue**\n\n" + "\n".join(f"- {x}" for x in r.reasons))
                if not safeguards:
                    st.error("Safeguards are OFF (demo).")
                st.caption(f"Reader: {res.read.reader} · {res.seconds:.1f} s"
                           + (f" · {res.read.input_tokens + res.read.output_tokens:,} tokens" if res.read.input_tokens else ""))
                if st.button("Re-run AI sorting"):
                    get_run(cid, force=True)
                    st.rerun()

                st.subheader("Rule check")
                for rr in r.rule_results:
                    icon = "✅" if rr.met else "▫️"
                    with st.expander(f"{icon} {rr.label}", expanded=rr.met or rr.path == r.path):
                        for cr in rr.criteria:
                            st.markdown(f"{'✔' if cr['met'] else '✘'} {cr['name']}"
                                        + (f" (p. {', '.join(map(str, cr['pages']))})" if cr["pages"] else ""))
                        if rr.note:
                            st.caption(rr.note)

                if r.flags:
                    st.subheader("Flags")
                    for f in r.flags:
                        st.markdown(f"- **{f['type']}**: {f['detail']}" + (f" (p. {f['page']})" if f.get("page") else ""))

                st.subheader("Checklist")
                st.dataframe([{"Field": i.field, "Value": i.value, "Page": i.page,
                               "Source": SOURCE_TYPES.get(i.source_type, i.source_type).split(",")[0],
                               "Quote found": "✔" if i.verified else "✘",
                               "Counts for rules": "✔" if i.counts_for_rules else "",
                               "Why not": i.drop_reason, "Quote": i.quote} for i in res.read.items],
                             use_container_width=True, hide_index=True, height=260)
                if res.read.evidence_for_approval:
                    st.subheader("Evidence for approval")
                    for ev in res.read.evidence_for_approval:
                        st.markdown(f"- p. {ev['page']}: “{ev['quote']}” — {ev['why']}"
                                    + ("" if ev.get("verified", True) else " *(quote not found)*"))
                if res.read.missing_evidence:
                    st.subheader("Missing evidence")
                    for m in res.read.missing_evidence:
                        st.markdown(f"- {m}")
            else:
                st.info("Human-only mode: AI output hidden. Review the file and decide.")

            st.divider()
            st.subheader("Final decision (examiner)")
            with st.form(f"decide-{cid}-{mode_key}"):
                decision = st.radio("Decision", ["allow", "deny", "need_more_evidence"], horizontal=True,
                                    format_func=lambda x: {"allow": "Allow", "deny": "Deny",
                                                           "need_more_evidence": "Need more evidence / CE"}[x])
                basis = st.text_input("Basis (e.g. meets 11.08A, grid 201.09, not severe at Step 2)")
                note = st.text_area("Note", height=70)
                if st.form_submit_button("Record final decision", type="primary"):
                    if decision == "deny" and not basis.strip():
                        st.error("A denial needs a written basis from the examiner.")
                    else:
                        secs = time.time() - opened[(cid, mode_key)]
                        LOG.add(case_id=cid, case_set=case.case_set, examiner=examiner, mode=mode_key,
                                ai_route=res.routing.route if res else None, reader=res.read.reader if res else None,
                                final_decision=decision, basis=basis, note=note, seconds=round(secs, 1))
                        opened.pop((cid, mode_key), None)
                        st.success(f"Recorded: {decision} ({secs / 60:.1f} min).")

        with st.expander("Live test: add a document to this case (for adversarial inputs)"):
            with st.form(f"add-{cid}"):
                text = st.text_area("Document text")
                c1, c2, c3 = st.columns(3)
                stype = c1.selectbox("Who wrote it", list(SOURCE_TYPES), format_func=SOURCE_TYPES.get, index=4)
                via = c2.selectbox("How it arrived", list(RECEIVED_VIA), format_func=RECEIVED_VIA.get, index=2)
                prov = c3.text_input("Provider / facility")
                if st.form_submit_button("Add and re-run") and text.strip():
                    next_page = max(p for d in case.documents for p in d.pages) + 1
                    extra_docs.setdefault(cid, []).append(Document(
                        doc_id=f"LIVE{len(extra_docs.get(cid, [])) + 1}", title="Live test document",
                        source_type=stype, received_via=via, provider=prov, pages={next_page: text}))
                    st.rerun()

# ----------------------------------------------------------------------------- import
with tab_i:
    st.subheader("Import existing files as a new case")
    st.caption("Works now with PDFs and text files (fillable form values are read too). Linking directly to SSA's "
               "electronic claim folder is the planned next step (see `SSAeFolderConnector`).")
    files = st.file_uploader("Files", accept_multiple_files=True, type=["pdf", "md", "txt"])
    with st.form("import"):
        c1, c2 = st.columns(2)
        new_id = c1.text_input("Case id", value=f"imp-{len(LocalFolderConnector(IMP).list_cases()) + 1:03d}")
        ctype = c2.selectbox("Claim type", ["SSDI", "SSI", "concurrent"])
        listed = st.text_area("Providers listed in SSA-3368 section 8 (one per line)")
        meta = []
        for i, f in enumerate(files or []):
            st.markdown(f"**{f.name}**")
            a, b, c = st.columns(3)
            meta.append(dict(name=f.name, data=f.getvalue(),
                             source_type=a.selectbox("Who wrote it", list(SOURCE_TYPES), key=f"s{i}",
                                                     format_func=SOURCE_TYPES.get),
                             received_via=b.selectbox("How it arrived", list(RECEIVED_VIA), key=f"r{i}",
                                                      format_func=RECEIVED_VIA.get),
                             provider=c.text_input("Provider / facility", key=f"p{i}")))
        if st.form_submit_button("Create case", type="primary") and meta:
            FileImport(IMP).create_case(new_id, ctype, [x.strip() for x in listed.splitlines() if x.strip()], meta)
            st.success(f"Created {new_id}. Choose 'Imported files' in the sidebar to review it.")

# ----------------------------------------------------------------------------- results
with tab_r:
    st.subheader("AI routing on this set (internal test)")
    cases = con.list_cases(case_set) if case_set != "(none)" else []
    keyed = [(c, con.answer_key(c["case_id"])) for c in cases]
    keyed = [(c, kk) for c, kk in keyed if kk]
    done = [(c, kk, runs.get(run_key(c["case_id"]))) for c, kk in keyed]
    done = [x for x in done if x[2]]
    if not keyed:
        st.info("This set has no answer keys (imported cases), so accuracy can't be computed.")
    elif not done:
        st.info("Run AI sorting on the Queue tab first.")
    else:
        rows = [dict(case_id=c["case_id"], case_set=case_set, route=r.routing.route, key_eligible=kk["eligible"],
                     key_fast_track=kk["fast_track"], items_total=len(r.read.items),
                     items_verified=sum(i.verified for i in r.read.items), seconds=r.seconds) for c, kk, r in done]
        m = routing_metrics(rows)
        targets = m["targets"]
        names = {"cases": "Cases", "fast_track_rate": "Fast-track rate", "fast_track_precision": "Fast-track precision",
                 "fast_track_recall_of_eligible": "Eligible cases fast-tracked", "route_matches_design": "Route matches answer key",
                 "ai_denials": "Denials made by the AI", "quote_verification_rate": "Quotes found on the cited page",
                 "mean_seconds_per_case": "AI seconds per case"}
        st.table([{"Measure": names[k_], "Result": str(m[k_]), "Target": targets.get(k_, "reported")} for k_ in names])
        if case_set == "stress":
            s_ = stress_metrics(rows)
            st.table([{"Measure": "Gaming cases wrongly fast-tracked", "Result": s_["gaming_cases_wrongly_fast_tracked"], "Target": "0"},
                      {"Measure": "Honest controls sent to a human", "Result": s_["honest_controls_sent_to_human"], "Target": "reported"}])
        if case_set == "test":
            st.caption("Pre-registration: run the test set once, with settings locked after calibration.")
    st.subheader("Examiner decisions: human-only vs. human + AI")
    keys = {c["case_id"]: con.answer_key(c["case_id"]) for c in con.list_cases()}
    keys = {a: b for a, b in keys.items() if b}
    dm = decision_metrics(LOG.all(), keys)
    st.table([{"Arm": {"human_only": "Human only", "human_plus_ai": "Human + AI"}[a], "Decisions": v["decisions"],
               "Accuracy vs answer key": v["accuracy"], "Wrongful denials": v["wrongful_denials"],
               "Median minutes": v["median_minutes"], "Median min, fast-track cases": v["median_minutes_fast_track"],
               "Median min, human-queue cases": v["median_minutes_human_queue"]} for a, v in dm.items()])
    st.caption("AI only = the routing above: it can approve via the fast track but never denies.")
    st.download_button("Download decision log", data="\n".join(json.dumps(d) for d in LOG.all()),
                       file_name="decisions.jsonl")
