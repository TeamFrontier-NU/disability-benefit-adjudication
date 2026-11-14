"""Check delivered content against HANDOFF.md section 3 before handing it to C.

    python study/app/check_content.py

Reports, per language: which files are still placeholders, AI quotes that are
not word-for-word on the stated page, [[terms]] missing from glossary.yaml,
and No-AI-visible text that mentions AI. Reads only; changes nothing.
"""
import re
import sys

import content as C

LANGS = ("en", "zh", "es")
AI_WORDS = r"\bAI\b|人工智能|\bIA\b|[Ii]nteligencia artificial"
TEXT_KEYS = ["welcome", "why_fast_track", "consent", "lottery", "rule_card", "ai_notice",
             "wrapup_ai", "wrapup_noai", "thanks"]
problems = 0
for lang in LANGS:
    print(f"\n== {lang} ==")
    still_ph = [f"texts/{k}" for k in TEXT_KEYS if C.text(k, lang)[1]]
    still_ph += [f"training/{t}" for t in ("T1", "Q1", "Q2") if C.training_case(t, lang)[1]]
    still_ph += [f"cases/{c}" for c in C.CASE_IDS if C.case_pages(c, lang)[1]]
    still_ph += [f"ai/{c}" for c in C.CASE_IDS if C.ai_output(c, lang)[1]]
    print("placeholder (not delivered yet):", ", ".join(still_ph) or "none")
    for cid in C.CASE_IDS:
        for p in C.quote_problems(cid, lang):
            problems += 1
            print(f"QUOTE {cid}.{lang}: {p}")
        ai, _ = C.ai_output(cid, lang)
        if ai and ai.get("recommendation") not in ("yes", "no"):
            problems += 1
            print(f"AI {cid}.{lang}: recommendation must be \"yes\" or \"no\"")
    for f, term in C.missing_terms(lang):
        problems += 1
        print(f"GLOSSARY {f}: [[{term}]] not in glossary.yaml")
    noai_visible = ["rule_card", "wrapup_noai", "thanks", "welcome", "why_fast_track", "consent", "lottery"]
    for k in noai_visible:
        if re.search(AI_WORDS, C.text(k, lang)[0]):
            problems += 1
            print(f"NO-AI PAGE texts/{k}.{lang}.md mentions AI")
    for cid in C.CASE_IDS:
        pages, _ = C.case_pages(cid, lang)
        if any(re.search(AI_WORDS, t + b) for t, b in pages):
            problems += 1
            print(f"NO-AI PAGE cases/{cid}.{lang}.md mentions AI")
# original-layout PDFs must be rebuilt after a case changes (make_doc_pdfs.py)
for folder in ("cases", "training"):
    for md in sorted((C.CONTENT_DIR / folder).glob("*.md")):
        pdf = md.with_suffix(".pdf")
        if pdf.exists() and pdf.stat().st_mtime < md.stat().st_mtime:
            problems += 1
            print(f"PDF {folder}/{pdf.name} is older than its .md: run make_doc_pdfs.py")

# ui.yaml from group B must keep every label the pages use
ph_ui = C.yaml.safe_load((C.PLACEHOLDER_DIR / "texts/ui.yaml").read_text(encoding="utf-8"))
real_ui = C.CONTENT_DIR / "texts/ui.yaml"
if real_ui.exists():
    got = C.yaml.safe_load(real_ui.read_text(encoding="utf-8")) or {}
    for k in ph_ui:
        for lang in LANGS:
            if not isinstance(got.get(k), dict) or not got[k].get(lang):
                problems += 1
                print(f"UI texts/ui.yaml: label {k!r} missing for {lang}")
print(f"\n{problems} problem(s)")
sys.exit(1 if problems else 0)
