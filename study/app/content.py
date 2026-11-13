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
    return _find(f"cases/{cid}.{lang}.pdf")


def training_pdf(cid: str, lang: str) -> tuple[Path | None, bool]:
    return _find(f"training/{cid}.{lang}.pdf")


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
