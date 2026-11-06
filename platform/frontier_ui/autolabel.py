"""Suggest labels for files dropped onto the "New case (live)" page.

Plain pattern matching, no AI: who wrote a document and how it arrived decide whether it can count
toward a rule, so the AI is never allowed to set them. These are only suggestions that the presenter
checks and corrects in a table before running. When unsure about a medical-looking record, the
suggestion is the safe one ("handed in by the claimant"), which can never support a fast track.
"""
from __future__ import annotations

import re
from datetime import date, datetime

from fasttrack.intake import _pdf_pages

FACILITY_WORDS = (r"Hospital|Clinic|Center|Centre|Institute|Associates|Practice|Medicine|Medical Group|"
                  r"Rehabilitation|Rehab|Imaging|Radiology|Cardiology|Nephrology|Oncology|Neurology|Orthopedics|"
                  r"Psychiatry|Health|Dialysis|Trauma Center|Care")
FACILITY = re.compile(rf"(?<![\w.])((?:(?:St\.|[A-Z][a-zA-Z'’&\-]*)\s+){{0,5}}(?:{FACILITY_WORDS})"
                      rf"(?:\s+(?:of|for)\s+[A-Z][a-zA-Z'’&\-]*)?)\b")
CRED = r"(?:M\.?D\.?|D\.?O\.?|Ph\.?D\.?|Psy\.?D\.?|NP|PA-C|DPM|OD)"
SIGNER = re.compile(rf"(?:(?:signed|Provider|Physician|Doctor)[:\s,]+(?:by\s+)?)?(?:Dr\.?\s+)?"
                    rf"([A-Z][a-zA-Z.\-]+(?:\s+[A-Z][a-zA-Z.\-]+){{0,3}}),?\s+({CRED})\b")
FORM_CUES = re.compile(r"SSA-?\s?(16|8000|3368|3373|3369|827)\b|\A\s*(Form\s+)?(Disability Report|Function Report)|"
                       r"Application for (Disability|Supplemental)|\b(filed|applied) for (SSDI|SSI|both|disability|"
                       r"benefits)\b|\bfiling date\b|\bclaim type\b", re.I)
LIST_CUES = re.compile(r"\b(lists?|listed|Section 8|medical (treatment|sources?)|treat(s|ed|ing)? (her|him|them)|"
                       r"providers?)\b", re.I)
MED_CUES = re.compile(r"\b(diagnos\w*|assessment|impression|exam(ination)?|history of|MRI|CT\b|X-ray|biopsy|"
                      r"dialysis|ejection fraction|eGFR|ASIA [A-E]|carcinoma|strength \d/5|plan:|follow[- ]up)\b", re.I)
LETTER_CUES = re.compile(r"(^|\n)\s*(Dear\b|To whom it may concern)|\bSincerely\b|\bI have known\b|\b(my|his|her) "
                         r"(wife|husband|son|daughter|mother|father|friend|neighbou?r|brother|sister)\b|"
                         r"\bletter from\b|\bcase manager\b|\badvocate\b", re.I)
CE_CUES = re.compile(r"consultative (exam|examination)", re.I)

MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December|" \
         "Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec"
DATE_RES = [
    (re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"), ["%Y-%m-%d"]),
    (re.compile(rf"\b((?:{MONTHS})\.?\s+\d{{1,2}},?\s+\d{{4}})\b"), ["%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y"]),
    (re.compile(rf"\b(\d{{1,2}}\s+(?:{MONTHS})\.?\s+\d{{4}})\b"), ["%d %B %Y", "%d %b %Y"]),
    (re.compile(r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b"), ["%m/%d/%Y", "%m/%d/%y"]),
]


def file_text(name: str, data: bytes) -> str:
    if name.lower().endswith(".pdf"):
        try:
            return "\n\n".join(_pdf_pages(data))
        except Exception:
            return ""
    return data.decode("utf-8", "replace")


def _parse_date(s: str) -> date | None:
    s = s.replace("Sept ", "Sep ").replace(".", "")
    for rx, fmts in DATE_RES:
        if rx.fullmatch(s):
            for f in fmts:
                try:
                    return datetime.strptime(s, f).date()
                except ValueError:
                    pass
    return None


def dates_in(text: str) -> list[date]:
    found = []
    for rx, _ in DATE_RES:
        for m in rx.finditer(text):
            d = _parse_date(m.group(1))
            if d and 1990 <= d.year <= 2035:
                found.append((m.start(), d))
    return [d for _, d in sorted(found)]


def facilities_in(text: str) -> list[str]:
    out = []
    for m in FACILITY.finditer(text):
        name = re.sub(r"\s+", " ", m.group(1)).strip(" .,;:()")
        name = re.sub(r"^(The|the|at|from|At|From|by)\s+", "", name)
        if len(name.split()) >= 2 and name not in out:
            out.append(name)
    return out


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def match_listed(provider: str, listed: list[str]) -> str | None:
    p = _norm(provider)
    for name in listed:
        n = _norm(name)
        if p and n and (p == n or p in n or n in p):
            return name
    return None


def guess_source(name: str, text: str) -> str:
    head = text[:600]
    if CE_CUES.search(text):
        return "ce_report"
    if FORM_CUES.search(head) or re.search(r"ssa|application|form|3368|8000", name, re.I):
        return "claimant_form"
    if LETTER_CUES.search(text) and not SIGNER.search(text):
        return "third_party"
    if SIGNER.search(text) and MED_CUES.search(text):
        return "ams_record"
    if LETTER_CUES.search(text):
        return "third_party"
    if MED_CUES.search(text):
        return "ams_record"
    return "third_party"


def case_fields(form_texts: list[str]) -> dict:
    """Claim type, filing date, claimant name and SSA-3368 providers from the forms, when they can be found."""
    t = "\n".join(form_texts)
    out: dict = {}
    if re.search(r"\b(concurrent|both SSI and SSDI|both SSDI and SSI|SSI and SSDI|SSDI and SSI)\b", t, re.I):
        out["claim_type"] = "concurrent"
    elif re.search(r"\bSSDI\b|Disability Insurance", t):
        out["claim_type"] = "SSDI"
    elif re.search(r"\bSSI\b|Supplemental Security Income", t):
        out["claim_type"] = "SSI"
    m = re.search(r"(?:filed|applied|filing date|application date)[^.\n]*?((?:%s)\.?\s+\d{1,2},?\s+\d{4}|"
                  r"\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})" % MONTHS, t, re.I)
    if m:
        d = _parse_date(m.group(1))
        if d:
            out["filing_date"] = d
    m = re.search(r"^\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})(?:,\s*\d+,)?\s+(?:filed|applied)", t, re.M)
    if m:
        out["title"] = m.group(1)
    # SSA-3368 providers: only facilities named in sentences that list where the claimant is treated
    listed: list[str] = []

    def add(chunk: str):
        for f in facilities_in(chunk):
            if f not in listed:
                listed.append(f)

    # prose: sentences that say where the claimant is treated ("Dr." and "St." don't end a sentence)
    prose = re.sub(r"\b(Dr|St|Mr|Mrs|Ms|Jr|Sr|No)\.", r"\1<dot>", t)
    for sent in re.split(r"(?<=[.!?])\s+", prose):
        if LIST_CUES.search(sent):
            add(sent.replace("<dot>", "."))
    # forms: a "Section 8 / Medical treatment" heading and the indented or numbered lines under it
    region = False
    for line in t.splitlines():
        if LIST_CUES.search(line):
            region = True
            add(line)
        elif region and (line.startswith((" ", "\t")) or re.match(r"\s*\d+[.)]|\s*[-•*]", line)):
            add(line)
        else:
            region = False
    out["listed"] = listed
    return out


def suggest(files: list[tuple[str, bytes]]) -> tuple[list[dict], dict]:
    """Suggested label rows (one per file) and case fields. Nothing here is final until the presenter checks it."""
    texts = [(n, d, file_text(n, d)) for n, d in files]
    srcs = [guess_source(n, t) for n, _, t in texts]
    fields = case_fields([t for (n, _, t), s in zip(texts, srcs) if s == "claimant_form"])
    listed = fields.get("listed", [])
    rows = []
    for (name, data, text), src in zip(texts, srcs):
        fac = facilities_in(text[:400]) or facilities_in(text)
        provider = fac[0] if fac else ""
        signer = SIGNER.search(text)
        author, cred = (signer.group(1).strip(), signer.group(2).replace(".", "")) if signer else ("", "")
        ds = dates_in(text)
        if src == "claimant_form":
            via, why = "field_office", "application or claimant form"
            provider, author, cred = "", "", ""
        elif src == "third_party":
            via, why = "claimant", "letter or statement"
            provider = ""
        else:
            hit = match_listed(provider, listed) if provider else None
            if hit:
                via, why, provider = "dds_request", "medical record from a provider on the SSA-3368", hit
            else:
                via = "claimant"
                why = ("medical-looking record from a provider NOT on the SSA-3368: check how it arrived"
                       if provider else "medical-looking record, provider not found: check")
        rows.append(dict(file=name, source_type=src, received_via=via, provider=provider, author=author,
                         credential=cred, doc_date=(max(ds) if src != "claimant_form" and ds else None),
                         why=why, data=data))
    # No fallback: if no SSA-3368 list is found, medical records stay "handed in by the claimant" until the
    # presenter adds the providers and confirms how each record arrived. Safe by default.
    return rows, fields
