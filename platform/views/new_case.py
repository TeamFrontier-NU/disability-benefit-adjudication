from __future__ import annotations

import copy
import html
import re
import time
from datetime import date

import streamlit as st

from fasttrack.models import RECEIVED_VIA, RULE_SOURCES, SOURCE_TYPES
from fasttrack.pipeline import route, verify
from frontier_ui import autolabel as al
from frontier_ui import new_case as nc
from frontier_ui.talk import speaker
from frontier_ui.common import (K_LOCKED, checklist_table, document_viewer, flags_block, is_live, page_header,
                                pipeline_steps, route_banner, rule_cards, run_live)

page_header("New case (live)",
            "Paste or upload a case you have never seen, then run it through the same locked reader, checklist and "
            "rules. **Live mode only**: each run is one real Gemini 3.7 Flash call (a few cents).")
speaker("attacks")

ss = st.session_state
ss.setdefault("nc_extra", 0)
live = is_live()


def _scrub(s: str) -> str:
    """Never show anything that looks like a key in an error message."""
    return re.sub(r"(AQ\.|AIza|sk-ant)[A-Za-z0-9_\-\.]{6,}", "[key hidden]", str(s))


def text_and_upload(key: str, label: str, help_: str = "") -> tuple[str, tuple | None]:
    text = st.text_area(label, key=f"{key}_text", height=160, help=help_ or None)
    up = st.file_uploader("…or upload a PDF or TXT", type=["pdf", "txt", "md"], key=f"{key}_up")
    return text, ((up.name, up.getvalue()) if up is not None else None)



SRC_LABEL = {"application": "Application form", "claimant_form": "Claimant form (SSA-3368 etc.)",
             "ams_record": "Medical record (doctor)", "ce_report": "Consultative exam report",
             "third_party": "Letter or statement (family, advocate)"}
VIA_LABEL = {"field_office": "Taken by the field office", "dds_request": "Requested by the DDS from the provider",
             "claimant": "Handed in by the claimant or a helper"}
SRC_FROM, VIA_FROM = {v: k for k, v in SRC_LABEL.items()}, {v: k for k, v in VIA_LABEL.items()}


def bulk_upload():
    """Drop all the files at once; suggest labels and case fields when the set of files changes."""
    ups = st.file_uploader("Drop all the case files here (PDF, TXT or MD; several at once)",
                           type=["pdf", "txt", "md"], accept_multiple_files=True, key="nc_bulk")
    files = [(u.name, u.getvalue()) for u in (ups or [])]
    sig = tuple((n, len(d)) for n, d in files)
    if sig != ss.get("nc_bulk_sig"):
        ss["nc_bulk_sig"] = sig
        rows, fields = al.suggest(files) if files else ([], {})
        ss["nc_bulk_rows"] = rows
        if fields.get("title"):
            ss["nc_title"] = fields["title"]
        if fields.get("claim_type"):
            ss["nc_claim"] = fields["claim_type"]
        if fields.get("filing_date"):
            ss["nc_filed"] = fields["filing_date"]
        auto = "\n".join(fields.get("listed", []))
        ss["nc_listed"] = ss["nc_bulk_listed_auto"] = auto
        ss["nc_bulk_ok"] = False
    if files:
        st.caption(f"{len(files)} file{'s' if len(files) != 1 else ''} read. The labels below are suggestions from "
                   "simple text patterns, not from the AI. Check them before you run.")


def bulk_table() -> tuple[list[dict], bool]:
    rows = ss.get("nc_bulk_rows", [])
    if not rows:
        st.info("Drop the files above. Each file becomes one document; a PDF keeps its own pages.")
        return [], False
    table = [{"File": r["file"], "What it is": SRC_LABEL[r["source_type"]], "How it arrived": VIA_LABEL[r["received_via"]],
              "Provider / facility": r["provider"], "Doctor": r["author"], "Credential": r["credential"],
              "Date": r["doc_date"].isoformat() if r["doc_date"] else "", "Why we suggested this": r["why"]}
             for r in rows]
    edited = st.data_editor(
        table, key=f"nc_bulk_editor_{hash(ss.get('nc_bulk_sig'))}", hide_index=True, width="stretch",
        disabled=["File", "Why we suggested this"],
        column_config={
            "What it is": st.column_config.SelectboxColumn(options=list(SRC_LABEL.values()), required=True),
            "How it arrived": st.column_config.SelectboxColumn(options=list(VIA_LABEL.values()), required=True),
            "Date": st.column_config.TextColumn(help="YYYY-MM-DD"),
        })
    st.markdown('<div class="ft-banner ft-note">Who wrote a record and how it arrived decide whether it can count '
                'toward a rule, so a person sets them, never the AI. Medical records count only if they were '
                '<b>requested by the DDS</b> from a provider on the SSA-3368 list (section 3).</div>',
                unsafe_allow_html=True)
    ok = st.checkbox("I have checked what each file is and how it arrived", key="nc_bulk_ok")
    docs = []
    for r, e in zip(rows, edited):
        src, via = SRC_FROM[e["What it is"]], VIA_FROM[e["How it arrived"]]
        d = (e.get("Date") or "").strip()
        if src in ("claimant_form", "application"):
            d = d or filing.isoformat()
        docs.append(dict(title=re.sub(r"\.(pdf|txt|md)$", "", r["file"], flags=re.I), source_type=src,
                         received_via=via, provider=e.get("Provider / facility") or "", author=e.get("Doctor") or "",
                         credential=e.get("Credential") or "", doc_date=d, text="", upload=(r["file"], r["data"])))
    return docs, ok


mode = st.radio("How do you want to add the case?", ["Drop files (labels suggested)", "Fill in by type"],
                horizontal=True, key="nc_mode")
bulk = mode.startswith("Drop")
if bulk:
    st.subheader("0. Drop the files")
    bulk_upload()


# ----------------------------------------------------------------------------- case fields
st.subheader("1. The claim")
a, b, c = st.columns([2, 1, 1])
ss.setdefault("nc_title", "New case")
ss.setdefault("nc_claim", nc.CLAIM_TYPES[0])
ss.setdefault("nc_filed", date.today())
title = a.text_input("Title", key="nc_title")
claim_type = b.selectbox("Claim type", nc.CLAIM_TYPES, key="nc_claim")
filing = c.date_input("Filing date", key="nc_filed")

# ----------------------------------------------------------------------------- quick entry
st.subheader("2. Documents")
bulk_ok = True
if bulk:
    docs, bulk_ok = bulk_table()
else:
    st.caption("Each box becomes one document. Pasted text is one page; an uploaded PDF keeps its own pages. "
               f"Up to {nc.MAX_PAGES} pages in total.")
    docs = []

    with st.container(border=True):
        st.markdown("**Application and claimant forms** (SSA-16, SSA-3368 and similar) · treated as a claimant form, "
                    "taken by the field office")
        t, u = text_and_upload("nc_forms", "Form text")
        docs.append(dict(title="Application and claimant forms", source_type="claimant_form", received_via="field_office",
                         doc_date=filing.isoformat(), text=t, upload=u))

    with st.container(border=True):
        st.markdown("**Medical records** · treated as a record from an acceptable medical source")
        t, u = text_and_upload("nc_med", "Medical record text")
        m1, m2 = st.columns(2)
        med_via = m1.selectbox("How it arrived", list(RECEIVED_VIA), format_func=RECEIVED_VIA.get,
                               index=list(RECEIVED_VIA).index("dds_request"), key="nc_med_via")
        med_prov = m2.text_input("Provider / facility", key="nc_med_prov")
        m3, m4, m5 = st.columns([2, 1, 1])
        med_doc = m3.text_input("Doctor", key="nc_med_doc", placeholder="e.g. Dr. F. Mendes")
        med_cred = m4.text_input("Credential", key="nc_med_cred", placeholder="MD, DO, PhD…")
        med_date = m5.date_input("Record date", value=None, key="nc_med_date")
        docs.append(dict(title=f"Medical records{' - ' + med_prov if med_prov.strip() else ''}", source_type="ams_record",
                         received_via=med_via, provider=med_prov, author=med_doc, credential=med_cred,
                         doc_date=med_date.isoformat() if med_date else "", text=t, upload=u))

    with st.container(border=True):
        st.markdown("**Other letters or statements** (family, case worker, advocate) · treated as a third-party letter")
        t, u = text_and_upload("nc_other", "Letter text")
        o_via = st.selectbox("How it arrived", list(RECEIVED_VIA), format_func=RECEIVED_VIA.get,
                             index=list(RECEIVED_VIA).index("claimant"), key="nc_other_via")
        docs.append(dict(title="Other letters or statements", source_type="third_party", received_via=o_via,
                         text=t, upload=u))

    for i in range(ss["nc_extra"]):
        with st.container(border=True):
            st.markdown(f"**Extra document {i + 1}**")
            x1, x2, x3 = st.columns(3)
            xt = x1.text_input("Title", value=f"Extra document {i + 1}", key=f"nc_x{i}_title")
            xs = x2.selectbox("Who it comes from", list(SOURCE_TYPES), format_func=SOURCE_TYPES.get,
                              index=list(SOURCE_TYPES).index("ams_record"), key=f"nc_x{i}_src")
            xv = x3.selectbox("How it arrived", list(RECEIVED_VIA), format_func=RECEIVED_VIA.get,
                              index=list(RECEIVED_VIA).index("dds_request"), key=f"nc_x{i}_via")
            y1, y2 = st.columns([3, 1])
            xp = y1.text_input("Provider / facility", key=f"nc_x{i}_prov")
            xd = y2.date_input("Date", value=None, key=f"nc_x{i}_date")
            t, u = text_and_upload(f"nc_x{i}", "Document text")
            docs.append(dict(title=xt, source_type=xs, received_via=xv, provider=xp,
                             doc_date=xd.isoformat() if xd else "", text=t, upload=u))

    e1, e2, _ = st.columns([1, 1, 3])
    if e1.button("Add another document", disabled=ss["nc_extra"] >= nc.MAX_EXTRA):
        ss["nc_extra"] += 1
        st.rerun()
    if ss["nc_extra"] and e2.button("Remove the last one"):
        ss["nc_extra"] -= 1
        st.rerun()

# ----------------------------------------------------------------------------- SSA-3368 providers
st.subheader("3. Providers listed on the SSA-3368")
auto = "\n".join(dict.fromkeys(d["provider"].strip() for d in docs
                               if d["source_type"] in RULE_SOURCES and (d.get("provider") or "").strip()))
if bulk:
    auto = ss.get("nc_bulk_listed_auto", "")
if ss.get("nc_listed") is None or ss.get("nc_listed") == ss.get("nc_listed_auto", ""):
    ss["nc_listed"] = auto        # follow the medical-record providers until someone edits the list
ss["nc_listed_auto"] = auto
listed = st.text_area("One provider per line", key="nc_listed", height=90)
st.caption("The provenance check uses this list: a medical record counts only if it was requested by the DDS from a "
           "provider named here (exact name, any letter case).")

# ----------------------------------------------------------------------------- run
st.subheader("4. Run")
if not live:
    st.info("Switch on Live mode to run a new case (presenter passcode, in the sidebar).")
if live and bulk and docs and not bulk_ok:
    st.warning("Tick “I have checked what each file is and how it arrived” first.")
go = st.button("Run AI sorting (live Gemini call)", type="primary", disabled=not live or (bulk and not bulk_ok))

if go and live:
    try:
        case, folder, n_pages = nc.build_case(docs, claim_type, filing.isoformat(), title, listed.splitlines(),
                                              old_dir=ss.get("nc_folder"))
    except ValueError as e:
        st.error(str(e))
        st.stop()
    ss["nc_folder"] = folder
    before = len(ss.get("live_log", []))
    with st.spinner("Reading the case file…"):
        if n_pages == 0:
            res = nc.run_fail_safe(case, "No pages to read: paste text or upload a file", K_LOCKED)
        else:
            try:
                res = run_live(case)
            except Exception as e:  # the reader could not even start: same fail-safe as run_case
                res = nc.run_fail_safe(case, f"the reader could not start ({type(e).__name__}: {_scrub(e)[:200]})",
                                       K_LOCKED)
    log = ss.get("live_log", [])
    cost = log[-1]["cost_usd"] if len(log) > before else 0.0
    off = None
    if res.read.items:   # safeguards-off pass on a fresh copy of the same reader output (no second API call)
        read_off = copy.deepcopy(res.read)
        for it in read_off.items:
            it.verified, it.counts_for_rules, it.drop_reason = False, False, ""
        off = route(case, verify(case, read_off, safeguards=False), read_off, res.k, safeguards=False)
    ss["nc_run"] = dict(case=case, res=res, off=off, cost=cost, pages=n_pages, fresh=True)

run = ss.get("nc_run")
if run:
    case, res = run["case"], run["res"]
    steps = st.empty()
    if run.pop("fresh", False):
        for lit in range(1, 5):
            with steps.container():
                pipeline_steps(res, lit)
            time.sleep(0.45)
    else:
        with steps.container():
            pipeline_steps(res, 4)
    err = next((m for m in res.read.missing_evidence if str(m).startswith("Reader failed")), "")
    if err:
        st.error(f"The reader failed, so the case goes to a person: {_scrub(err)}")
    route_banner(res)
    tok = res.read.input_tokens + res.read.output_tokens
    st.caption(f"{res.read.reader} · {run['pages']} page{'s' if run['pages'] != 1 else ''} · "
               f"{res.seconds:.1f} seconds · {tok:,} tokens · about ${run['cost']:.3f} · k = {res.k} · "
               "same locked prompt, checklist and rules")

    off = run["off"]
    if off is not None and off.route == "fast_track" and res.routing.route != "fast_track":
        # One decision only. Say in one line what the safeguards stopped (same reading, no second AI call).
        blocked = {}
        for it in res.read.items:
            if it.verified and not it.counts_for_rules and it.drop_reason and it.source_type in RULE_SOURCES:
                d = case.doc_for_page(it.page)
                blocked.setdefault(d.title if d else f"page {it.page}", it.drop_reason)
        items = "".join(f"<li><b>{html.escape(t)}</b>: {html.escape(r)}</li>" for t, r in blocked.items())
        why = html.escape((off.reasons or [""])[0])
        st.markdown(f'<div class="ft-banner ft-note">🛡️ <b>Stopped by the safeguards.</b> Without them, this file '
                    f'would have reached the fast track ({why}), relying on evidence that can’t count:'
                    f'<ul style="margin:6px 0 0 0">{items or "<li>see the flags below</li>"}</ul></div>',
                    unsafe_allow_html=True)

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
                st.markdown(f"- {_scrub(m)}")
    with left:
        st.subheader("Case file")
        if case.documents:
            document_viewer(case, res)
        else:
            st.markdown("No pages.")
    with st.expander("Full checklist (every item the reader filled in)"):
        checklist_table(res)
    st.caption("This case lives only in this browser session (a temporary folder). It is not saved to the "
               "simulated data or to any results file.")
