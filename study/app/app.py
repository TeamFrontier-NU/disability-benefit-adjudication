"""Frontier examiner study: participant web app (Group C, LYL).

Flow: language -> welcome -> training (rule card, T1, Q1, [Q2]) -> random
assignment -> 6 cases -> wrap-up survey -> thanks.

All page text comes from study/content/ (see HANDOFF.md section 3). Data,
assignment and timing come from ZXH's data.py / assign.py once a Google Sheet is
set in Streamlit Secrets; without Secrets backend_stub.py is used and the page
says PREVIEW (nothing saved to the Sheet).

Run locally:  streamlit run study/app/app.py
"""
from __future__ import annotations

import html
import re

import streamlit as st

import content as C

import data as _data

if _data.configured():  # Google Sheet in Streamlit Secrets: the real study
    import assign as A  # noqa: N812
    D = _data  # noqa: N816
    IS_STUB = False
else:  # no Secrets: PREVIEW, nothing reaches the Sheet
    import backend_stub as A  # noqa: N812
    D = A
    IS_STUB = True

st.set_page_config(page_title="Study", page_icon=None, layout="wide",
                   initial_sidebar_state="collapsed")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@400;600&display=swap');
:root {--ink:#1b2430; --muted:#5d6b7a; --line:#dfe4ea; --bg:#f4f6f9; --card:#ffffff;
       --brand:#1f3a5f; --brand-2:#2c5282; --tint:#eef3f9; --paper:#fffefb;}
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {background: var(--bg) !important;}
[data-testid="stAppViewContainer"] *:not([data-testid="stIconMaterial"]) {font-family: 'Inter',
       system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;}
#MainMenu, footer, [data-testid="stSidebarNav"], [data-testid="stToolbar"],
[data-testid="stHeader"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {display: none !important;}
.block-container {max-width: 1180px; padding: 0 1.25rem 4rem !important;}
h1, h2, h3, h4 {color: var(--ink); letter-spacing: -0.01em;}
p, li {color: var(--ink); line-height: 1.6;}

/* top bar */
.topbar {display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
         background: var(--brand); color:#fff; margin: 18px 0 24px; padding: 14px 24px; border-radius: 12px;
         box-shadow: 0 4px 14px rgba(31,58,95,.18);}
.topbar .t {font-weight:600; font-size:1.02rem; letter-spacing:.01em; color:#fff;}
.steps {display:flex; gap:6px; flex-wrap:wrap;}
.steps span {font-size:.78rem; padding:4px 11px; border-radius:999px; color:#c9d6e6;
             border:1px solid rgba(255,255,255,.22);}
.steps span.on {background:#fff; color:var(--brand); border-color:#fff; font-weight:600;}
.steps span.done {color:#fff; border-color:rgba(255,255,255,.5);}

/* cards (st.container(border=True)) */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {
    background: var(--card); border:1px solid var(--line) !important; border-radius:12px !important;
    box-shadow: 0 1px 2px rgba(16,24,40,.04), 0 2px 8px rgba(16,24,40,.04);}
.eyebrow {font-size:.72rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
          color: var(--brand-2); margin: 0 0 4px;}
.pagetitle {font-size:1.45rem; font-weight:700; color:var(--ink); margin:0 0 6px;}

/* buttons */
.stButton > button, .stFormSubmitButton > button, .stDownloadButton > button {
    border-radius:8px; font-weight:600; padding: .5rem 1.4rem;}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"],
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--brand) !important; border-color: var(--brand) !important; color:#fff !important;}
.stButton > button[kind="primary"] p, .stFormSubmitButton > button[kind="primary"] p,
.stButton > button[data-testid="stBaseButton-primary"] p,
.stFormSubmitButton > button[data-testid="stBaseButton-primaryFormSubmit"] p {color:#fff !important;}
[data-testid="stColumn"]:has(.st-key-aipanel) {align-self: flex-start; position: sticky; top: 16px;}
[data-testid="stExpander"] details {background: var(--card); border-radius: 10px; border-color: var(--line);}
[data-testid="stExpander"] summary p {font-weight: 600; color: var(--brand);}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button:hover {background: var(--brand-2) !important;}
.stButton > button:disabled {opacity:.45;}
[data-testid="stProgress"] [role="progressbar"] div[style*="width"] {background: var(--brand) !important;}

/* language page */
.hero {text-align:center; padding: 48px 12px 12px;}
.hero .t1 {font-size:1.7rem; font-weight:700; color:var(--ink);}
.hero .t2 {font-size:1.25rem; color:var(--muted); margin-top:4px;}

/* case documents: typed, document-style pages */
.doc {background: var(--paper); color:#1d1d1d; border:1px solid #d9d6cf; border-radius:3px;
      padding: 30px 38px 22px; margin: 0 auto 18px; max-width: 820px;
      box-shadow: 0 1px 2px rgba(0,0,0,.06), 0 6px 18px rgba(0,0,0,.06);}
.doc, .doc * {font-family: 'Source Serif 4', Georgia, 'Songti SC', 'SimSun', serif !important;}
.doc p, .doc li {font-size: 1rem; line-height: 1.65; color:#1d1d1d;}
.doc .lh {display:flex; justify-content:space-between; align-items:flex-end; gap:12px;
          border-bottom: 2px solid #2b2b2b; padding-bottom:8px; margin-bottom:16px;}
.doc .lh .dt {font-weight:600; font-size:1.05rem; color:#111;}
.doc .lh .dn, .doc .pf {font-family: 'Inter', system-ui, sans-serif !important; font-size:.72rem;
          color:#7a7a7a; letter-spacing:.04em; text-transform:uppercase; white-space:nowrap;}
.doc .pf {text-align:right; border-top:1px solid #e6e2da; margin-top:18px; padding-top:6px;}

/* glossary hover */
.gl {border-bottom: 1px dashed #4a5568; cursor: help; position: relative;}
.gl .gl-tip {visibility: hidden; opacity: 0; position: absolute; left: 0; top: 1.6em; z-index: 50;
             width: 270px; background: #1b2430; color: #fff; padding: 9px 11px; border-radius: 6px;
             font: 400 0.82rem/1.4 'Inter', system-ui, sans-serif !important; transition: opacity .12s;
             box-shadow: 0 6px 18px rgba(0,0,0,.18);}
.gl:hover .gl-tip, .gl:focus .gl-tip {visibility: visible; opacity: 1;}
.gl-missing {border-bottom: 2px dotted #c00;}

/* status badges for the team only */
.ph {display: inline-block; background: #fff6db; color: #7a5b00; border: 1px solid #f0d27a;
     font: 500 0.72rem 'Inter', system-ui, sans-serif; padding: 2px 8px; border-radius: 4px; margin: 2px 0 8px;}
.panel-h {font-weight:700; color:var(--brand); font-size:1rem; margin-bottom:6px;}
.quote {border-left:3px solid var(--brand-2); background: var(--tint); padding:8px 12px; border-radius:0 6px 6px 0;
        margin: 6px 0; font-size:.93rem;}
.quote .pg {display:block; font-size:.75rem; color:var(--muted); margin-top:3px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

S = st.session_state


# ---------------- helpers ----------------

def ph_badge(what: str) -> None:
    st.markdown(f'<span class="ph">PLACEHOLDER · {what} not delivered yet</span>',
                unsafe_allow_html=True)


def show_text(key: str) -> None:
    body, ph = C.text(key, S.lang)
    if ph:
        ph_badge(f"content/texts/{key}.{S.lang}.md")
    st.markdown(C.render_terms(body, S.lang), unsafe_allow_html=True)


def show_document(pages: list[tuple[str, str]], ph: bool, src: str,
                  pdf: tuple | None = None) -> None:
    """Typed, document-style pages. If an original PDF exists for this file, both groups get
    the same optional 'original document' viewer under the pages."""
    if ph:
        ph_badge(src)
    n = len(pages)
    for i, (title, body) in enumerate(pages, 1):
        page_lbl = C.ui("page_of", S.lang).format(i=i, n=n)
        inner = C.render_terms(body, S.lang)
        # markdown inside the HTML block: blank lines let Streamlit parse it
        st.markdown(f'<div class="doc"><div class="lh"><div class="dt">{html.escape(title)}</div>'
                    f'<div class="dn">{page_lbl}</div></div>\n\n{inner}\n\n'
                    f'<div class="pf">{page_lbl}</div></div>', unsafe_allow_html=True)
    if pdf and pdf[0]:
        path, pdf_ph = pdf
        with st.expander(C.ui("original_doc", S.lang)):
            if pdf_ph:
                ph_badge(src.replace(".md", ".pdf"))
            st.caption(C.ui("original_doc_note", S.lang))
            try:
                st.pdf(str(path), height=720)
            except Exception:  # viewer component missing: the download still works
                pass
            st.download_button(C.ui("download_pdf", S.lang), data=path.read_bytes(),
                               file_name=path.name, mime="application/pdf",
                               key=f"dl_{path.name}")


def rule_card(expanded: bool) -> None:
    body, ph = C.text("rule_card", S.lang)
    with st.expander(C.ui("rule_card_title", S.lang), expanded=expanded):
        if ph:
            ph_badge(f"content/texts/rule_card.{S.lang}.md")
        st.markdown(C.render_terms(body, S.lang), unsafe_allow_html=True)


def yes_no(key: str) -> str | None:
    labels = {"yes": C.ui("yes", S.lang), "no": C.ui("no", S.lang)}
    return st.radio(C.ui("fast_track_question", S.lang), ["yes", "no"], index=None,
                    format_func=labels.get, horizontal=True, key=key)


STEP_OF = {"lang": 0, "welcome": 0, "rule": 1, "T1": 1, "Q1": 1, "Q2": 1, "assign": 2,
           "case": 2, "wrapup": 3, "thanks": 3, "failed": 3}


def topbar() -> None:
    """Study name + the four steps. Labels come from ui.yaml (no page text in code)."""
    if S.stage == "lang":
        return
    names = C.ui_list("steps", S.lang)
    cur = STEP_OF.get(S.stage, 0)
    pills = "".join(
        f'<span class="{"on" if i == cur else "done" if i < cur else ""}">{html.escape(n)}</span>'
        for i, n in enumerate(names))
    st.markdown(f'<div class="topbar"><div class="t">{html.escape(C.ui("study_title", S.lang))}</div>'
                f'<div class="steps">{pills}</div></div>', unsafe_allow_html=True)


def heading(eyebrow_key: str | None, title: str) -> None:
    eb = f'<div class="eyebrow">{html.escape(C.ui(eyebrow_key, S.lang))}</div>' if eyebrow_key else ""
    st.markdown(f'{eb}<div class="pagetitle">{html.escape(title)}</div>', unsafe_allow_html=True)


def go(stage: str) -> None:
    S.stage = stage
    st.rerun()


def save_once(tag: str, fn, *args, **kw) -> bool:
    """Write one row unless already written this session. On failure, say so and stay put."""
    done = S.setdefault("saved", set())
    if tag in done:
        return True
    try:
        fn(*args, **kw)
    except Exception:  # SaveError after retries, or anything unexpected
        st.error(C.ui("save_failed", S.lang))
        return False
    done.add(tag)
    return True


def forced_arm() -> str | None:
    """Team-only test switch: ?arm=ai|noai (also treat|control). Needs &k=<test_key> once a
    Sheet is configured; in PREVIEW it works without a key. Banners never name the group."""
    arm = {"treat": "ai", "ai": "ai", "control": "noai", "noai": "noai"}.get(
        st.query_params.get("arm", ""))
    if not arm:
        return None
    if IS_STUB:
        return arm
    key = D.test_key()
    return arm if key and st.query_params.get("k") == key else None


def banners() -> None:
    if IS_STUB:
        st.markdown('<span class="ph">PREVIEW · nothing is saved to the study Sheet</span>',
                    unsafe_allow_html=True)
    elif S.get("pid", "").startswith("TEST-") or (S.stage in ("lang", "welcome") and S.test_arm):
        st.markdown('<span class="ph">TEST RUN · team only · rows are marked TEST-</span>',
                    unsafe_allow_html=True)


# ---------------- pages ----------------

def page_language() -> None:
    st.markdown(f'<div class="hero"><div class="t1">{html.escape(C.ui("study_title", "en"))}</div>'
                f'<div class="t2">{html.escape(C.ui("study_title", "zh"))}</div></div>',
                unsafe_allow_html=True)
    _, mid, _ = st.columns([1, 1.3, 1])
    with mid, st.container(border=True):
        st.markdown(f'<p style="text-align:center;margin:4px 0 12px">'
                    f'{html.escape(C.ui("choose_language", "en"))} · '
                    f'{html.escape(C.ui("choose_language", "zh"))}</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("English", use_container_width=True, type="primary"):
            S.lang = "en"
            go("welcome")
        if c2.button("中文", use_container_width=True, type="primary"):
            S.lang = "zh"
            go("welcome")


def page_welcome() -> None:
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        with st.container(border=True):
            show_text("welcome")
            show_text("why_fast_track")
        with st.container(border=True):
            show_text("consent")
        with st.container(border=True):
            show_text("lottery")
        _welcome_form()


def _welcome_form() -> None:
    with st.form("welcome_form", border=True):
        c1, c2 = st.columns(2)
        name = c1.text_input(C.ui("name", S.lang))
        email = c2.text_input(C.ui("email", S.lang))
        exp_opts = C.ui_list("experience_options", S.lang)
        exp_en = C.ui_list("experience_options", "en")
        exp_i = st.radio(C.ui("experience", S.lang), list(range(len(exp_opts))), index=None,
                         format_func=lambda i: exp_opts[i])
        agree = st.checkbox(C.ui("consent_checkbox", S.lang))
        sent = st.form_submit_button(C.ui("start", S.lang), type="primary")
    if sent:
        if not agree:
            st.error(C.ui("need_consent", S.lang))
            return
        if not (name.strip() and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip())
                and exp_i is not None):
            st.error(C.ui("need_fields", S.lang))
            return
        if "pid" not in S:
            S.pid = A.new_participant_id(test=bool(S.test_arm))
        S.heard = ""  # not asked any more; the HANDOFF 3.5 column stays, empty
        exp = exp_en[exp_i] if exp_i < len(exp_en) else exp_opts[exp_i]  # stored in English
        ok = save_once("contact", D.write_contact, S.pid, name.strip(), email.strip())
        ok = ok and save_once("participant", D.write_participant, S.pid, S.lang,
                              {"experience": exp})
        if ok:
            st.query_params["p"] = S.pid  # lets a refreshed page resume
            go("rule")


def page_rule() -> None:
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        with st.container(border=True):
            show_text("rule_card")
        _continue_to_T1()


def _continue_to_T1() -> None:
    if st.button(C.ui("continue", S.lang), type="primary"):
        go("T1")


def training_item(cid: str, next_ok: str, next_wrong: str) -> None:
    """Answer first, then show whether it was right and the explanation."""
    heading("training_eyebrow", C.ui("example_case" if cid == "T1" else "check_case", S.lang))
    rule_card(expanded=False)
    body, ph = C.training_case(cid, S.lang)
    show_document(C.split_pages(body), ph, f"content/training/{cid}.{S.lang}.md",
                  pdf=C.training_pdf(cid, S.lang))
    done_key = f"done_{cid}"
    if not S.get(done_key):
        with st.container(border=True):
            ans = yes_no(f"ans_{cid}")
            if st.button(C.ui("submit", S.lang), type="primary", disabled=ans is None):
                S[done_key] = ans
                st.rerun()
        return
    key_ans = C.training_answer(cid)
    correct = S[done_key] == key_ans
    with st.container(border=True):
        if C.training_key()[1]:
            ph_badge("content/training/training_key.yaml")
        (st.success if correct else st.error)(C.ui("correct" if correct else "incorrect", S.lang))
        st.markdown(C.render_terms(C.training_explanation(cid, S.lang), S.lang),
                    unsafe_allow_html=True)
    if st.button(C.ui("continue", S.lang), type="primary"):
        if cid == "T1":
            go(next_ok)
        S.training_attempts = 1 if cid == "Q1" else 2
        nxt = next_ok if correct else next_wrong
        if nxt in ("assign", "failed") and not save_once(
                "training", D.write_training, S.pid, S.training_attempts, nxt == "assign"):
            return
        go(nxt)


def page_assign() -> None:
    """Runs once, at the moment the participant passes the test."""
    if "arm" not in S:
        if S.get("assign_tried"):  # an earlier try may have reached the Sheet: reuse it
            r = _safe_restore(S.pid)
            if r and r.get("arm"):
                S.arm, S.order = r["arm"], r["order"]
        if "arm" not in S:
            S.assign_tried = True
            try:
                S.arm, S.order = A.assign(S.pid, S.lang, S.training_attempts, S.heard,
                                          forced_arm=S.test_arm)
            except Exception:
                st.error(C.ui("save_failed", S.lang))
                if st.button(C.ui("continue", S.lang), type="primary"):
                    st.rerun()
                return
        S.idx = 0
        S.timers = {}
    go("case")


def ai_panel(cid: str) -> None:
    ai, ph = C.ai_output(cid, S.lang)
    with st.container(border=True, key="aipanel"):
        _ai_panel_body(cid, ai, ph)


def _ai_panel_body(cid: str, ai: dict | None, ph: bool) -> None:
    if ph:
        ph_badge(f"content/ai/{cid}.{S.lang}.json")
    st.markdown(f'<div class="panel-h">{html.escape(C.ui("ai_panel_title", S.lang))}</div>',
                unsafe_allow_html=True)
    show_text("ai_notice")
    if not ai:
        st.markdown(f"**[missing: `content/ai/{cid}.{S.lang}.json`]**")
    else:
        rec = C.ui("yes" if ai.get("recommendation") == "yes" else "no", S.lang)
        st.markdown(f"**{C.ui('ai_recommendation', S.lang)}:** {rec}")
        if ai.get("summary"):
            st.markdown(ai["summary"])
        if ai.get("findings"):
            st.markdown(f"**{C.ui('ai_findings', S.lang)}**")
            for f in ai["findings"]:
                pg = C.ui("page_n", S.lang).format(n=f.get("page"))
                st.markdown(f'<div class="quote">“{html.escape(str(f.get("quote", "")))}”'
                            f'<span class="pg">{html.escape(pg)}</span></div>',
                            unsafe_allow_html=True)
        if ai.get("flags"):
            st.markdown(f"**{C.ui('ai_flags', S.lang)}**")
            for fl in ai["flags"]:
                st.markdown(f"- {fl}")


def page_case() -> None:
    if S.idx >= len(S.order):
        go("wrapup")
    cid = S.order[S.idx]
    if cid not in S.timers:  # start once; reruns do not reset the clock
        S.timers[cid] = A.start_timer()

    progress = C.ui("case_progress", S.lang).format(i=S.idx + 1, n=len(S.order))
    st.markdown(f'<div class="eyebrow">{html.escape(progress)}</div>', unsafe_allow_html=True)
    st.progress((S.idx + 1) / len(S.order))
    rule_card(expanded=False)
    pages, ph = C.case_pages(cid, S.lang)
    src = f"content/cases/{cid}.{S.lang}.md"
    pdf = C.case_pdf(cid, S.lang)
    if S.arm == "ai":
        left, right = st.columns([3, 2], gap="large")
        with left:
            show_document(pages, ph, src, pdf=pdf)
        with right:
            ai_panel(cid)
    else:  # no-AI page: full width, nothing about AI anywhere
        show_document(pages, ph, src, pdf=pdf)

    with st.container(border=True):
        c1, c2 = st.columns([1, 1.4], gap="large")
        with c1:
            ans = yes_no(f"case_ans_{cid}")
        conf_lbl = {1: f"1 · {C.ui('conf_low', S.lang)}", 5: f"5 · {C.ui('conf_high', S.lang)}"}
        with c2:
            conf = st.radio(C.ui("confidence_question", S.lang), [1, 2, 3, 4, 5], index=None,
                            horizontal=True, key=f"case_conf_{cid}",
                            format_func=lambda v: conf_lbl.get(v, str(v)))
        st.caption(C.ui("no_going_back", S.lang))
        clicked = st.button(C.ui("submit", S.lang), type="primary", key=f"submit_{cid}",
                            disabled=ans is None or conf is None)
    if clicked and ans and conf:
        pending = S.setdefault("pending", {})
        if cid not in pending:  # time is fixed at the first click, even if saving is retried
            secs, started, submitted = A.stop_timer(S.timers[cid])
            pending[cid] = {
                "participant_id": S.pid, "lang": S.lang, "arm": S.arm, "case_id": cid,
                "case_order": S.idx + 1, "answer": ans, "confidence": conf, "seconds": secs,
                "started_at": started, "submitted_at": submitted,
                "training_attempts": S.training_attempts, "heard_about_study": S.heard,
            }
        if save_once(f"resp_{cid}", D.write_response, pending[cid]):
            S.idx += 1
            st.rerun()


SURVEY_RE = re.compile(r"^\?(scale|text|choice):\s*(.+)$")


def page_wrapup() -> None:
    _, mid, _ = st.columns([1, 6, 1])
    with mid:
        _wrapup_form()


def _wrapup_form() -> None:
    key = "wrapup_ai" if S.arm == "ai" else "wrapup_noai"
    body, ph = C.text(key, S.lang)
    if ph:
        ph_badge(f"content/texts/{key}.{S.lang}.md")
    answers: dict = {}
    with st.form("wrapup"):
        buf: list[str] = []
        qn = 0
        for line in body.splitlines() + [""]:
            m = SURVEY_RE.match(line.strip())
            if not m:
                buf.append(line)
                continue
            if "".join(buf).strip():
                st.markdown(C.render_terms("\n".join(buf), S.lang), unsafe_allow_html=True)
            buf = []
            qn += 1
            kind, rest = m.groups()
            if kind == "scale":
                answers[f"q{qn}"] = st.radio(rest, [1, 2, 3, 4, 5], index=None,
                                             horizontal=True, key=f"s{qn}")
            elif kind == "text":
                answers[f"q{qn}"] = st.text_area(rest, key=f"s{qn}")
            else:
                parts = [p.strip() for p in rest.split("|")]
                answers[f"q{qn}"] = st.radio(parts[0], parts[1:], index=None, key=f"s{qn}")
        if "".join(buf).strip():
            st.markdown(C.render_terms("\n".join(buf), S.lang), unsafe_allow_html=True)
        sent = st.form_submit_button(C.ui("finish", S.lang), type="primary")
    if sent and save_once("survey", D.write_survey, S.pid, S.arm, answers, lang=S.lang):
        go("thanks")


def page_thanks() -> None:
    _, mid, _ = st.columns([1, 4, 1])
    with mid, st.container(border=True):
        show_text("thanks")


def page_failed() -> None:
    """Failed the qualification test twice: end, but still in the lottery."""
    page_thanks()


PAGES = {
    "lang": page_language,
    "welcome": page_welcome,
    "rule": page_rule,
    "T1": lambda: training_item("T1", "Q1", "Q1"),
    "Q1": lambda: training_item("Q1", "assign", "Q2"),
    "Q2": lambda: training_item("Q2", "assign", "failed"),
    "assign": page_assign,
    "case": page_case,
    "wrapup": page_wrapup,
    "thanks": page_thanks,
    "failed": page_failed,
}

def _safe_restore(pid: str) -> dict | None:
    try:
        return A.restore(pid)
    except Exception:
        return None


def boot() -> None:
    """First run of a browser session. With ?p=<id> in the URL (set after Welcome), a
    refreshed page continues where it was: same id, same group, same case order, and
    cases already submitted are not shown again."""
    if "stage" in S:
        return
    S.stage, S.lang, S.test_arm = "lang", "en", forced_arm()
    pid = st.query_params.get("p")
    r = _safe_restore(pid) if pid else None
    if not r:
        return
    S.pid, S.lang, S.heard = pid, r["lang"], r["heard"]
    S.saved = {"contact", "participant"}
    if r["failed"]:
        S.stage = "failed"
    elif r["arm"]:
        S.arm, S.order, S.training_attempts = r["arm"], r["order"], r["attempts"]
        S.idx, S.timers = r["done"], {}
        S.saved |= {"training"} | {f"resp_{c}" for c in S.order[:S.idx]}
        S.stage = ("thanks" if r["survey_done"] else "wrapup") if S.idx >= len(S.order) else "case"
    elif r["passed"]:
        S.training_attempts, S.stage = r["attempts"], "assign"
        S.saved.add("training")
    else:
        S.stage = "rule"


boot()
topbar()
banners()
PAGES[S.stage]()
