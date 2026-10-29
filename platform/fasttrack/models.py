"""Core data objects shared by every part of the platform.

A case is a folder of documents. Pages are numbered across the whole case file
(like a real claim folder), so a quote is always cited as one page number.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional

# Who wrote a document. Only AMS and CE documents can satisfy a rule (the source rule).
SOURCE_TYPES = {
    "application": "Application form (field office)",
    "claimant_form": "Claimant form (SSA-3368, SSA-3373, SSA-3369)",
    "ams_record": "Medical record, acceptable medical source",
    "ce_report": "Consultative exam report",
    "third_party": "Third-party letter (case worker, family, advocate)",
}
RULE_SOURCES = {"ams_record", "ce_report"}

# How a document reached the examiner.
RECEIVED_VIA = {
    "field_office": "Taken by the field office",
    "dds_request": "Requested by the DDS from the provider (SSA-827 / ERE)",
    "claimant": "Handed in by the claimant or a helper",
}


@dataclass
class Document:
    doc_id: str
    title: str
    source_type: str
    received_via: str
    author: str = ""
    credential: str = ""
    provider: str = ""            # facility name, matched against SSA-3368 section 8
    doc_date: str = ""            # YYYY-MM-DD
    file: str = ""
    pages: dict[int, str] = field(default_factory=dict)  # global page number -> text


@dataclass
class Case:
    case_id: str
    claim_type: str               # SSDI, SSI or concurrent
    filing_date: str
    case_set: str                 # demo, calibration, test, stress, imported
    documents: list[Document]
    listed_providers: list[str] = field(default_factory=list)  # SSA-3368 section 8
    prior_denial_months: Optional[int] = None
    title: str = ""

    def page_text(self, page: int) -> str:
        for d in self.documents:
            if page in d.pages:
                return d.pages[page]
        return ""

    def doc_for_page(self, page: int) -> Optional[Document]:
        for d in self.documents:
            if page in d.pages:
                return d
        return None

    def all_pages(self) -> list[tuple[int, Document, str]]:
        out = []
        for d in self.documents:
            for p, t in sorted(d.pages.items()):
                out.append((p, d, t))
        return sorted(out, key=lambda x: x[0])


@dataclass
class Item:
    """One checklist entry filled by the reader."""
    field: str
    value: str
    quote: str
    page: int
    # Filled in by verify.py, never by the reader:
    verified: bool = False
    source_type: str = ""
    doc_id: str = ""
    counts_for_rules: bool = False
    drop_reason: str = ""


@dataclass
class ReadResult:
    items: list[Item]
    instruction_flags: list[dict]       # {"quote", "page"}
    evidence_for_approval: list[dict]   # {"quote", "page", "why"}
    missing_evidence: list[str]
    reader: str = ""
    seconds: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class RuleResult:
    path: str
    label: str
    met: bool
    criteria: list[dict]        # {"name", "met", "items": [page numbers]}
    note: str = ""


@dataclass
class Routing:
    route: str                  # "fast_track" or "human_queue". Never "deny".
    path: str = ""
    reasons: list[str] = field(default_factory=list)
    flags: list[dict] = field(default_factory=list)   # {"type", "detail", "page"}
    rule_results: list[RuleResult] = field(default_factory=list)


def to_dict(obj):
    return asdict(obj)
