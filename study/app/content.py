"""Load study content in the formats of study/HANDOFF.md section 3.

Real content lives in study/content/ (owned by groups A and B). While a file
is still missing, the matching file under study/app/placeholder/ is used
instead and the page shows a PLACEHOLDER badge. No page text is written in code.
"""
from __future__ import annotations

import html
import json
import re
from functools import lru_cache
from pathlib import Path

import yaml

APP_DIR = Path(__file__).resolve().parent
CONTENT_DIR = APP_DIR.parent / "content"
PLACEHOLDER_DIR = APP_DIR / "placeholder"

CASE_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]
PAGE_BREAK = "---page---"
TERM_RE = re.compile(r"\[\[([^\[\]]+?)\]\]")


def _find(rel: str) -> tuple[Path | None, bool]:
    """Return (path, is_placeholder). Real content always wins."""
    real = CONTENT_DIR / rel
    if real.exists():
        return real, False
    ph = PLACEHOLDER_DIR / rel
    if ph.exists():
        return ph, True
    return None, True


@lru_cache(maxsize=None)
def _read(rel: str) -> tuple[str | None, bool]:
    path, ph = _find(rel)
    if path is None:
        return None, True
    return path.read_text(encoding="utf-8"), ph


def clear_cache() -> None:
    _read.cache_clear()
    glossary.cache_clear()
    ui_strings.cache_clear()
    training_key.cache_clear()


# ---------- 3.1 texts ----------

def text(key: str, lang: str) -> tuple[str, bool]:
    """texts/<key>.<lang>.md -> (markdown, is_placeholder)."""
    body, ph = _read(f"texts/{key}.{lang}.md")
    if body is None:
        return f"**[missing: `content/texts/{key}.{lang}.md`]**", True
    return body, ph


@lru_cache(maxsize=None)
def glossary() -> tuple[dict, bool]:
    body, ph = _read("texts/glossary.yaml")
    return (yaml.safe_load(body) or {}) if body else {}, ph


@lru_cache(maxsize=None)
def ui_strings() -> tuple[dict, bool]:
    """Short interface labels (buttons, field names). Proposed key texts/ui.yaml."""
    body, ph = _read("texts/ui.yaml")
    return (yaml.safe_load(body) or {}) if body else {}, ph


def ui(key: str, lang: str) -> str:
    entry = ui_strings()[0].get(key)
    if isinstance(entry, dict):
        return str(entry.get(lang) or entry.get("en") or key)
    return f"[{key}]"


def ui_list(key: str, lang: str) -> list[str]:
    entry = ui_strings()[0].get(key) or {}
    val = entry.get(lang) or entry.get("en") or []
    return [str(v) for v in val]


# ---------- 3.2 training ----------

def training_case(cid: str, lang: str) -> tuple[str, bool]:
    body, ph = _read(f"training/{cid}.{lang}.md")
    if body is None:
        return f"**[missing: `content/training/{cid}.{lang}.md`]**", True
    return body, ph


@lru_cache(maxsize=None)
def training_key() -> tuple[dict, bool]:
    body, ph = _read("training/training_key.yaml")
    return (yaml.safe_load(body) or {}) if body else {}, ph


def training_answer(cid: str) -> str | None:
    entry = training_key()[0].get(cid) or {}
    ans = entry.get("answer")
    if isinstance(ans, bool):  # YAML reads bare yes/no as booleans
        return "yes" if ans else "no"
    return str(ans).strip().lower() if ans is not None else None


def training_explanation(cid: str, lang: str) -> str:
    entry = training_key()[0].get(cid) or {}
    exp = entry.get("explanation") or {}
    if isinstance(exp, dict):
        return str(exp.get(lang) or exp.get("en") or "")
    return str(exp)


# ---------- 3.3 cases ----------

def case_pages(cid: str, lang: str) -> tuple[list[tuple[str, str]], bool]:
    """Split a case into [(title, body_markdown)]. First line of each page is its title."""
    body, ph = _read(f"cases/{cid}.{lang}.md")
    if body is None:
        return [(cid, f"**[missing: `content/cases/{cid}.{lang}.md`]**")], True
    return split_pages(body), ph


def case_pdf(cid: str, lang: str) -> tuple[Path | None, bool]:
    """Optional original-layout PDF next to the case file: cases/<cid>.<lang>.pdf."""
    return _pdf("cases", cid, lang)


def training_pdf(cid: str, lang: str) -> tuple[Path | None, bool]:
    return _pdf("training", cid, lang)


def _pdf(folder: str, cid: str, lang: str) -> tuple[Path | None, bool]:
    """The PDF must come from the same place as the .md (a placeholder PDF never stands in
    for a real case)."""
    md, md_ph = _find(f"{folder}/{cid}.{lang}.md")
    root = PLACEHOLDER_DIR if md_ph else CONTENT_DIR
    path = root / f"{folder}/{cid}.{lang}.pdf"
    return (path if md and path.exists() else None), md_ph


# ---------- 3.3b cases as separate PDF documents (real SSA forms + medical records) ----------
#
# Put the documents of a case in a folder named like the case file, without extension:
#
#     content/cases/C1.en/01_SSA-16.pdf
#     content/cases/C1.en/02_SSA-3368-BK.pdf
#     content/cases/C1.en/03_SSA-827.pdf
#     content/cases/C1.en/04_Northgate-Hospital-records.pdf
#
# (or content/cases/C1/ for one set shared by every language). When such a folder exists, the
# case page shows these PDFs as the case file, one at a time with a document list, IN PLACE OF
# the typed pages from C1.<lang>.md. The leading number sets the order and is not shown; the
# rest of the file name is the document's title ("_" and "-" become spaces).

def _doc_dir(folder: str, cid: str, lang: str) -> tuple[Path | None, bool]:
    for root, ph in ((CONTENT_DIR, False), (PLACEHOLDER_DIR, True)):
        for name in (f"{cid}.{lang}", cid):
            d = root / folder / name
            if d.is_dir() and any(d.glob("*.pdf")):
                return d, ph
    return None, True


def doc_title(path: Path) -> str:
    stem = re.sub(r"^\d+[\s_.-]*", "", path.stem)
    return re.sub(r"[_]+", " ", stem).strip() or path.stem


def case_docs(cid: str, lang: str, folder: str = "cases") -> tuple[list[Path], bool]:
    """The case's PDF documents in display order ([] if the case has no document folder)."""
    d, ph = _doc_dir(folder, cid, lang)
    if d is None:
        return [], True
    return sorted(d.glob("*.pdf"), key=lambda p: p.name.lower()), ph


def training_docs(cid: str, lang: str) -> tuple[list[Path], bool]:
    return case_docs(cid, lang, folder="training")


@lru_cache(maxsize=64)
def pdf_bytes(path: str) -> bytes:
    """Read each PDF once per server process (the page re-runs on every click)."""
    return Path(path).read_bytes()


def find_doc(docs: list[Path], name: str | None) -> Path | None:
    """A finding's optional "doc" (file name, with or without .pdf, or its title)."""
    if not name:
        return None
    key = str(name).strip().lower()
    for d in docs:
        if key in (d.name.lower(), d.stem.lower(), doc_title(d).lower()):
            return d
    return None


def pdf_text_pages(path: Path) -> list[str] | None:
    """Text of each page, for the quote check. None if pypdf is not installed."""
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return [(pg.extract_text() or "") for pg in PdfReader(str(path)).pages]


def split_pages(body: str) -> list[tuple[str, str]]:
    pages = []
    for chunk in re.split(rf"^\s*{re.escape(PAGE_BREAK)}\s*$", body, flags=re.M):
        chunk = chunk.strip("\n")
        if not chunk.strip():
            continue
        lines = chunk.strip().splitlines()
        title = lines[0].lstrip("#").strip()
        pages.append((title, "\n".join(lines[1:]).strip()))
    return pages


def hard_breaks(md: str) -> str:
    """Keep the line breaks the case writers typed (label on one line, text on the next)."""
    out = []
    lines = md.split("\n")
    for i, ln in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        plain = ln.strip() and nxt.strip() and not ln.lstrip().startswith(("|", "#", "-", "*  ", ">"))
        out.append(ln.rstrip() + "  " if plain and not nxt.lstrip().startswith("|") else ln)
    return "\n".join(out)


def render_terms(md: str, lang: str) -> str:
    """Turn [[term]] into a hover span using glossary.yaml."""
    gl = glossary()[0]

    def repl(m: re.Match) -> str:
        term = m.group(1).strip()
        entry = gl.get(term) or {}
        tip = entry.get(lang) or entry.get("en") if isinstance(entry, dict) else None
        if not tip:
            return f'<span class="gl gl-missing" title="not in glossary.yaml">{html.escape(term)}</span>'
        return (f'<span class="gl" tabindex="0">{html.escape(term)}'
                f'<span class="gl-tip">{html.escape(str(tip))}</span></span>')

    return TERM_RE.sub(repl, md)


def missing_terms(lang: str) -> list[tuple[str, str]]:
    """(file, term) pairs whose [[term]] is not in glossary.yaml. Used by the self-check."""
    gl = glossary()[0]
    out = []
    srcs = [("cases", c) for c in CASE_IDS] + [("training", t) for t in ("T1", "Q1", "Q2")]
    for folder, cid in srcs:
        body, _ = _read(f"{folder}/{cid}.{lang}.md")
        for term in TERM_RE.findall(body or ""):
            if term.strip() not in gl:
                out.append((f"{folder}/{cid}.{lang}.md", term.strip()))
    return out


# ---------- 3.4 AI output ----------

def ai_output(cid: str, lang: str) -> tuple[dict | None, bool]:
    body, ph = _read(f"ai/{cid}.{lang}.json")
    if body is None:
        return None, True
    return json.loads(body), ph


def quote_problems(cid: str, lang: str) -> list[str]:
    """Quotes in ai/<cid>.<lang>.json that are not found word-for-word on the stated page."""
    ai, _ = ai_output(cid, lang)
    if not ai:
        return []
    docs, _ = case_docs(cid, lang)
    if docs:  # PDF documents: page n = page n of the whole case file, documents in order
        texts = {}
        for d in docs:
            got = pdf_text_pages(d)
            if got is None:
                return ["pypdf not installed: quotes in PDF cases were not checked"]
            texts[d] = got
        cjk = r"[\u2e80-\u9fff\uff00-\uffef\u3000-\u303f]"
        # PDF text breaks lines; a Chinese line break leaves a space where the text has none
        norm = lambda t: re.sub(rf"(?<={cjk}) | (?={cjk})", "", re.sub(r"\s+", " ", t).strip())  # noqa: E731
        probs = []
        for f in ai.get("findings", []):
            q, p = f.get("quote", ""), f.get("page")
            d = find_doc(docs, f.get("doc"))
            if f.get("doc") and d is None:
                probs.append(f"document {f.get('doc')!r} not found: {q!r}")
                continue
            plain = texts[d] if d else [t for dd in docs for t in texts[dd]]
            where = f"{d.name} " if d else "the case file "
            if not isinstance(p, int) or not 1 <= p <= len(plain):
                probs.append(f"page {p} does not exist ({where}has {len(plain)} pages): {q!r}")
            elif norm(q) not in norm(plain[p - 1]):
                probs.append(f"not on page {p} of {where.strip()}: {q!r}")
        return probs
    pages, _ = case_pages(cid, lang)
    plain = [TERM_RE.sub(lambda m: m.group(1), t + "\n" + b) for t, b in pages]
    probs = []
    for f in ai.get("findings", []):
        q, p = f.get("quote", ""), f.get("page")
        if not isinstance(p, int) or not 1 <= p <= len(plain):
            probs.append(f"page {p} does not exist: {q!r}")
        elif q not in plain[p - 1]:
            probs.append(f"not on page {p}: {q!r}")
    return probs
