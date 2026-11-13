"""Frontier examiner study: participant web app (Group C, LYL).

Flow: language -> welcome -> training (rule card, T1, Q1, [Q2]) -> random
assignment -> 6 cases -> wrap-up survey -> thanks.

All page text comes from study/content/ (see HANDOFF.md section 3). Data,
assignment and timing come from ZXH's data.py / assign.py; until those exist
backend_stub.py is used and the page says PREVIEW.

Run locally:  streamlit run study/app/app.py
"""
from __future__ import annotations

import re

import streamlit as st

import content as C

try:  # ZXH's real modules win; the stub is only a stand-in.
    import assign as A  # noqa: N812
    import data as D  # noqa: N812
    IS_STUB = False
except ImportError:
    import backend_stub as A  # noqa: N812
    D = A
    IS_STUB = True

st.set_page_config(page_title="Study", page_icon=None, layout="wide",
                   initial_sidebar_state="collapsed")

CSS = """
<style>
#MainMenu, footer, [data-testid="stSidebarNav"], [data-testid="stToolbar"] {visibility: hidden;}
.block-container {max-width: 1250px; padding-top: 1.5rem;}
.doc {background: #fff; color: #1d1d1d; border: 1px solid #d0d0d0; border-radius: 4px;
      padding: 22px 28px; margin: 0 0 16px 0; font-family: Georgia, 'Times New Roman', serif;
      box-shadow: 0 1px 3px rgba(0,0,0,.08); line-height: 1.5;}
.doc h4 {font-family: system-ui, sans-serif; font-size: 0.95rem; margin: 0 0 4px 0;}
.doc .pg {font-family: system-ui, sans-serif; font-size: 0.75rem; color: #777; margin-bottom: 12px;
          border-bottom: 1px solid #e5e5e5; padding-bottom: 6px;}
.gl {border-bottom: 1px dashed #555; cursor: help; position: relative;}
.gl .gl-tip {visibility: hidden; opacity: 0; position: absolute; left: 0; top: 1.5em; z-index: 50;
             width: 260px; background: #222; color: #fff; font: 0.8rem/1.35 system-ui, sans-serif;
             padding: 8px 10px; border-radius: 4px; transition: opacity .1s;}
.gl:hover .gl-tip, .gl:focus .gl-tip {visibility: visible; opacity: 1;}
.gl-missing {border-bottom: 2px dotted #c00;}
.ph {display: inline-block; background: #fff3cd; color: #7a5b00; border: 1px solid #f0d27a;
     font: 0.72rem system-ui, sans-serif; padding: 1px 6px; border-radius: 3px; margin: 2px 0 8px;}
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


def show_document(pages: list[tuple[str, str]], ph: bool, src: str) -> None:
    if ph:
        ph_badge(src)
    n = len(pages)
    for i, (title, body) in enumerate(pages, 1):
        page_lbl = C.ui("page_of", S.lang).format(i=i, n=n)
        inner = C.render_terms(body, S.lang)
        # markdown inside the HTML block: blank lines let Streamlit parse it
        st.markdown(f'<div class="doc"><h4>{title}</h4><div class="pg">{page_lbl}</div>\n\n'
                    f'{inner}\n\n</div>', unsafe_allow_html=True)


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


def go(stage: str) -> None:
    S.stage = stage
    st.rerun()


def preview_banner() -> None:
    if IS_STUB:
        st.markdown('<span class="ph">PREVIEW · placeholder backend (no data is saved to the '
                    'Sheet). Add ?arm=treat or ?arm=control to the URL to preview a group.</span>',
                    unsafe_allow_html=True)


# ---------------- pages ----------------

def page_language() -> None:
    st.write("")
    c1, c2, _ = st.columns([1, 1, 3])
    if c1.button("English", use_container_width=True, type="primary"):
        S.lang = "en"
        go("welcome")
    if c2.button("中文", use_container_width=True, type="primary"):
        S.lang = "zh"
        go("welcome")


def page_welcome() -> None:
    for key in ("welcome", "why_fast_track", "consent"):
        show_text(key)
        st.divider()
    show_text("lottery")
    st.divider()

    with st.form("welcome_form"):
        name = st.text_input(C.ui("name", S.lang))
        email = st.text_input(C.ui("email", S.lang))
        major = st.text_input(C.ui("major", S.lang))
        exp_opts = C.ui_list("experience_options", S.lang)
        exp = st.radio(C.ui("experience", S.lang), exp_opts, index=None)
        heard = st.text_input(C.ui("heard_about_study", S.lang))
        agree = st.checkbox(C.ui("consent_checkbox", S.lang))
        sent = st.form_submit_button(C.ui("start", S.lang), type="primary")
    if sent:
        if not agree:
            st.error(C.ui("need_consent", S.lang))
            return
        if not (name.strip() and re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip())
                and major.strip() and exp is not None):
            st.error(C.ui("need_fields", S.lang))
            return
        S.pid = A.new_participant_id()
        S.heard = heard.strip()
        D.write_contact(S.pid, name.strip(), email.strip())
        D.write_participant(S.pid, S.lang, {"major": major.strip(), "experience": exp})
        go("rule")


def page_rule() -> None:
    show_text("rule_card")
    if st.button(C.ui("continue", S.lang), type="primary"):
        go("T1")


def training_item(cid: str, next_ok: str, next_wrong: str) -> None:
    """Answer first, then show whether it was right and the explanation."""
    rule_card(expanded=False)
    body, ph = C.training_case(cid, S.lang)
    show_document(C.split_pages(body), ph, f"content/training/{cid}.{S.lang}.md")
    done_key = f"done_{cid}"
    if not S.get(done_key):
        ans = yes_no(f"ans_{cid}")
        if st.button(C.ui("submit", S.lang), type="primary", disabled=ans is None):
            S[done_key] = ans
            st.rerun()
        return
    key_ans = C.training_answer(cid)
    correct = S[done_key] == key_ans
    if C.training_key()[1]:
        ph_badge("content/training/training_key.yaml")
    (st.success if correct else st.error)(C.ui("correct" if correct else "incorrect", S.lang))
    st.markdown(C.render_terms(C.training_explanation(cid, S.lang), S.lang),
                unsafe_allow_html=True)
    if st.button(C.ui("continue", S.lang), type="primary"):
        if cid == "T1":
            go(next_ok)
        S.training_attempts = 1 if cid == "Q1" else 2
        go(next_ok if correct else next_wrong)


def page_assign() -> None:
    """Runs once, at the moment the participant passes the test."""
    if "arm" not in S:
        forced = {"treat": "ai", "control": "noai"}.get(st.query_params.get("arm", ""))
        S.arm = forced if IS_STUB and forced else A.assign_arm(S.pid)
        S.order = A.case_order(S.pid)
        S.idx = 0
        S.timers = {}
    go("case")


def ai_panel(cid: str) -> None:
    ai, ph = C.ai_output(cid, S.lang)
    with st.container(border=True):
        _ai_panel_body(cid, ai, ph)


def _ai_panel_body(cid: str, ai: dict | None, ph: bool) -> None:
    if ph:
        ph_badge(f"content/ai/{cid}.{S.lang}.json")
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
                st.markdown(f"> “{f.get('quote', '')}” — {pg}")
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

    st.caption(C.ui("case_progress", S.lang).format(i=S.idx + 1, n=len(S.order)))
    rule_card(expanded=False)
    pages, ph = C.case_pages(cid, S.lang)
    if S.arm == "ai":
        left, right = st.columns([3, 2], gap="large")
        with left:
            show_document(pages, ph, f"content/cases/{cid}.{S.lang}.md")
        with right:
            ai_panel(cid)
    else:  # no-AI page: full width, nothing about AI anywhere
        show_document(pages, ph, f"content/cases/{cid}.{S.lang}.md")

    st.divider()
    ans = yes_no(f"case_ans_{cid}")
    conf_lbl = {1: f"1 · {C.ui('conf_low', S.lang)}", 5: f"5 · {C.ui('conf_high', S.lang)}"}
    conf = st.radio(C.ui("confidence_question", S.lang), [1, 2, 3, 4, 5], index=None,
                    horizontal=True, key=f"case_conf_{cid}",
                    format_func=lambda v: conf_lbl.get(v, str(v)))
    st.caption(C.ui("no_going_back", S.lang))
    if st.button(C.ui("submit", S.lang), type="primary", disabled=ans is None or conf is None):
        secs, started, submitted = A.stop_timer(S.timers[cid])
        D.write_response({
            "participant_id": S.pid, "lang": S.lang, "arm": S.arm, "case_id": cid,
            "case_order": S.idx + 1, "answer": ans, "confidence": conf, "seconds": secs,
            "started_at": started, "submitted_at": submitted,
            "training_attempts": S.training_attempts, "heard_about_study": S.heard,
        })
        S.idx += 1
        st.rerun()


SURVEY_RE = re.compile(r"^\?(scale|text|choice):\s*(.+)$")


def page_wrapup() -> None:
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
    if sent:
        D.write_survey(S.pid, S.arm, answers)
        go("thanks")


def page_thanks() -> None:
    show_text("thanks")


def page_failed() -> None:
    """Failed the qualification test twice: end, but still in the lottery."""
    show_text("thanks")


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

S.setdefault("stage", "lang")
S.setdefault("lang", "en")
preview_banner()
PAGES[S.stage]()
