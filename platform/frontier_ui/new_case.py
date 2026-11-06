"""Builds a brand-new case from pasted text and uploads, for the "New case (live)" page.

UI and packaging only. The case is written with the locked `fasttrack.intake.FileImport` into a
session-only temp folder (case_set "imported"), read back with `LocalFolderConnector`, and run
through the unchanged pipeline. Nothing is written to data/simulated, and it is never a test case.
"""
from __future__ import annotations

import re
import shutil
import tempfile
from datetime import date
from pathlib import Path

from fasttrack.intake import FileImport, LocalFolderConnector, _pdf_pages
from fasttrack.models import Case, ReadResult
from fasttrack.pipeline import RunResult, run_case

MAX_PAGES = 30
MAX_CHARS = 150_000          # about 40k input tokens, about 3 cents
MAX_EXTRA = 6
CLAIM_TYPES = ["SSDI", "SSI", "concurrent"]
_PAGE_LINE = re.compile(r"^\s*\[Page (\d+)\]\s*$", re.M)


def _clean_text(t: str) -> str:
    """A pasted "[Page 3]" line would confuse the page splitter, so it becomes plain text."""
    return _PAGE_LINE.sub(lambda m: f"(Page {m.group(1)})", t.replace("\r\n", "\n")).strip()


def file_entries(doc: dict) -> list[dict]:
    """One input block (pasted text and/or an uploaded file) -> FileImport file dicts."""
    meta = {k: (doc.get(k) or "").strip() for k in ("source_type", "received_via", "author", "credential",
                                                     "provider", "doc_date")}
    title = (doc.get("title") or "").strip() or "Document"
    out = []
    up = doc.get("upload")  # (name, bytes) or None
    if up:
        name, data = up
        if not name.lower().endswith(".pdf"):
            data = _clean_text(data.decode("utf-8", "replace")).encode("utf-8")
        out.append(dict(meta, name=f"{title} ({name})" if not name.lower().endswith(".pdf") else
                        f"{title} ({Path(name).stem}).pdf", data=data))
    text = _clean_text(doc.get("text") or "")
    if text:
        out.append(dict(meta, name=f"{title}.txt", data=text.encode("utf-8")))
    return out


def count_pages(entries: list[dict]) -> tuple[int, int]:
    pages = chars = 0
    for f in entries:
        texts = _pdf_pages(f["data"]) if f["name"].lower().endswith(".pdf") else [f["data"].decode("utf-8", "replace")]
        texts = [t for t in texts if t.strip()]
        pages += len(texts)
        chars += sum(len(t) for t in texts)
    return pages, chars


def build_case(docs: list[dict], claim_type: str, filing_date: str, title: str,
               listed_providers: list[str], old_dir: str | None = None) -> tuple[Case, str, int]:
    """Write the case to a fresh temp folder and load it back. Returns (case, folder, page count)."""
    if old_dir and Path(old_dir).exists() and Path(old_dir).name.startswith("frontier-new-case-"):
        shutil.rmtree(old_dir, ignore_errors=True)
    entries = [e for d in docs for e in file_entries(d)]
    n_pages, n_chars = count_pages(entries) if entries else (0, 0)
    if n_pages > MAX_PAGES:
        raise ValueError(f"This case has {n_pages} pages. The live demo is capped at {MAX_PAGES} pages; "
                         "remove a document and try again.")
    if n_chars > MAX_CHARS:
        raise ValueError(f"This case has {n_chars:,} characters of text. The live demo is capped at "
                         f"{MAX_CHARS:,}; shorten a document and try again.")
    tmp = tempfile.mkdtemp(prefix="frontier-new-case-")
    case_id = f"new-{date.today():%Y%m%d}"
    FileImport(tmp).create_case(case_id, claim_type, [p.strip() for p in listed_providers if p.strip()], entries,
                                filing_date=filing_date, title=title.strip() or "New case")
    case = LocalFolderConnector(tmp).load_case(case_id)
    if case.case_set != "imported":  # belt and braces: a new case is never a test or simulated case
        raise ValueError("A new case must be an imported case.")
    for d in case.documents:  # drop empty pages (e.g. a blank PDF page)
        d.pages = {p: t for p, t in d.pages.items() if t.strip()}
        d.title = re.sub(r"\.(txt|md)$", "", d.title)
    case.documents = [d for d in case.documents if d.pages]
    return case, tmp, sum(len(d.pages) for d in case.documents)


class FailedReader:
    """Stands in when the reader can't start (no key, bad key, no pages). run_case catches the
    error and sends the case to the human queue, exactly as for any other reader failure."""

    def __init__(self, why: str):
        self.why, self.name = why, "Gemini 3.7 Flash (not run)"

    def read(self, case: Case) -> ReadResult:
        raise RuntimeError(self.why)


def run_fail_safe(case: Case, why: str, k: int) -> RunResult:
    return run_case(case, FailedReader(why), k, True)
