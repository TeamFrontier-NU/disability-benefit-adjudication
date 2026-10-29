"""Collect step: connectors that bring case files into the platform.

Every connector returns the same Case object, so the rest of the pipeline does
not care where a file came from.

  LocalFolderConnector   cases stored on disk in our format (simulated data)   - works now
  FileImport             turn uploaded PDFs / text files into a new case        - works now
  SSAeFolderConnector    link to SSA's electronic claim folder and records      - planned (next step)
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Iterable

from .models import Case, Document

PAGE_RE = re.compile(r"^\[Page (\d+)\]\s*$", re.M)


def _split_pages(text: str) -> dict[int, str]:
    parts = PAGE_RE.split(text)
    pages = {}
    for i in range(1, len(parts), 2):
        pages[int(parts[i])] = parts[i + 1].strip()
    return pages


class LocalFolderConnector:
    """Reads cases saved as folders: case.json + docs/*.md (+ answer_key.json, never shown to the reader)."""

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def list_cases(self, case_set: str | None = None) -> list[dict]:
        out = []
        for meta in sorted(self.root.glob("*/case.json")):
            m = json.loads(meta.read_text(encoding="utf-8"))
            if case_set and m["case_set"] != case_set:
                continue
            out.append(dict(case_id=m["case_id"], title=m.get("title", ""), case_set=m["case_set"],
                            claim_type=m["claim_type"]))
        return out

    def load_case(self, case_id: str) -> Case:
        cdir = self.root / case_id
        m = json.loads((cdir / "case.json").read_text(encoding="utf-8"))
        docs = []
        for dm in m["documents"]:
            pages = _split_pages((cdir / dm["file"]).read_text(encoding="utf-8"))
            docs.append(Document(doc_id=dm["doc_id"], title=dm["title"], source_type=dm["source_type"],
                                 received_via=dm["received_via"], author=dm.get("author", ""),
                                 credential=dm.get("credential", ""), provider=dm.get("provider", ""),
                                 doc_date=dm.get("doc_date", ""), file=dm["file"], pages=pages))
        return Case(case_id=m["case_id"], claim_type=m["claim_type"], filing_date=m["filing_date"],
                    case_set=m["case_set"], documents=docs, listed_providers=m.get("listed_providers", []),
                    prior_denial_months=m.get("prior_denial_months"), title=m.get("title", ""))

    def answer_key(self, case_id: str) -> dict | None:
        f = self.root / case_id / "answer_key.json"
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def _pdf_pages(data: bytes) -> list[str]:
    """Text of each PDF page, plus the values typed into fillable form fields on that page."""
    import io
    from pypdf import PdfReader

    r = PdfReader(io.BytesIO(data))
    out = []
    for page in r.pages:
        text = page.extract_text() or ""
        filled = []
        for a in page.get("/Annots") or []:
            a = a.get_object()
            v = a.get("/V")
            if v not in (None, "", "/Off") and not str(v).startswith("/"):
                filled.append(str(v))
        if filled:
            text += "\n\nFilled-in values on this page:\n" + "\n".join(f"- {v}" for v in filled)
        out.append(text.strip())
    return out


class FileImport:
    """Builds a new case folder from files the examiner uploads (PDF, .md or .txt).

    The examiner states who wrote each file and how it arrived, because the
    source rule depends on it and the AI is never allowed to decide that.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def create_case(self, case_id: str, claim_type: str, listed_providers: list[str],
                    files: Iterable[dict], filing_date: str | None = None, title: str = "") -> str:
        """files: dicts with name, data (bytes), source_type, received_via, author, credential, provider, doc_date."""
        cdir = self.root / case_id
        (cdir / "docs").mkdir(parents=True, exist_ok=True)
        page = 0
        meta_docs = []
        for i, f in enumerate(files, 1):
            if f["name"].lower().endswith(".pdf"):
                texts = _pdf_pages(f["data"])
            else:
                texts = [f["data"].decode("utf-8", errors="replace")]
            nums = list(range(page + 1, page + 1 + len(texts)))
            page += len(texts)
            doc_id = f"D{i:02d}_{re.sub(r'[^A-Za-z0-9]+', '_', Path(f['name']).stem)[:40]}"
            body = "\n\n".join(f"[Page {n}]\n{t}" for n, t in zip(nums, texts))
            (cdir / "docs" / f"{doc_id}.md").write_text(f"# {f['name']}\n\n{body}\n", encoding="utf-8")
            meta_docs.append(dict(doc_id=doc_id, title=f["name"], source_type=f["source_type"],
                                  received_via=f["received_via"], author=f.get("author", ""),
                                  credential=f.get("credential", ""), provider=f.get("provider", ""),
                                  doc_date=f.get("doc_date", ""), file=f"docs/{doc_id}.md", page_numbers=nums))
        meta = dict(case_id=case_id, title=title or case_id, claim_type=claim_type,
                    filing_date=filing_date or date.today().isoformat(), case_set="imported",
                    listed_providers=listed_providers, prior_denial_months=None, documents=meta_docs)
        (cdir / "case.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
        return case_id


class SSAeFolderConnector:
    """PLANNED, not built. Next step once a partner gives access.

    Idea: read a claim's electronic folder the way a DDS examiner sees it
    (application data from the field office, the SSA-3368, and medical records
    that providers send in through Electronic Records Express), map each item to
    a Document with source_type and received_via set from the system's own
    metadata, and return the same Case object as the other connectors.

    What is needed first: a data-use agreement, a test environment with
    synthetic claims, and a security review. Nothing in the course build calls this.
    """

    def __init__(self, *_, **__):
        raise NotImplementedError("SSA electronic folder access is the next step; see the class docstring.")
