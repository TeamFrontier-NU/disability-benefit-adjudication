"""Write records/00_screen.rec.md (the DDS fast-track screen and evidence list that opens each
case file) from the "screen" block of case.json.

    "screen": {
      "printed": "11/16/2026",
      "allegations": ["...", "..."],                 # SSA-3368 3.A in the claimant's words
      "cal": "MATCH - allegation 1 '...'",           # or "No match"
      "qdd": "Selected (score above threshold)",     # or "Not selected"
      "exhibits": [["1F", "Source", "dates", "pages", "received", "how received"], ...],
      "pending":  [["Source", "requested", "follow-up", "status"], ...]
    }

The sheet only shows what the existing process already produced (allegations, the QDD/CAL
flags, what arrived and how). It never states a medical finding.

Usage: python study/materials/make_screen.py C1 [C2 ...] | --all
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CASES = Path(__file__).resolve().parent / "cases"


def make(cid: str) -> Path:
    case = json.loads((CASES / cid / "case.json").read_text(encoding="utf-8"))
    s, cl, cm = case["screen"], case["claimant"], case["claim"]
    last, first = cl["name"].replace(".", "").rsplit(" ", 1)[1], cl["name"].replace(".", "").rsplit(" ", 1)[0]
    al = "\n".join(f"| {i} | {a} |" for i, a in enumerate(s["allegations"], 1))
    ex = "\n".join("| " + " | ".join(e) + " |" for e in s["exhibits"])
    pend = "\n".join("| " + " | ".join(p) + " |" for p in s.get("pending", [])) or "| None outstanding | | | |"
    text = f"""---
style: ehr
facility: Illinois Disability Determination Services
dept: Case development worksheet - initial claim (Title II)
address: SSA / State DDS electronic folder
phone: "Printed {s.get('printed', '11/16/2026')}"
title: FAST-TRACK SCREEN AND EVIDENCE LIST
patient:
  Claimant: {last.upper()}, {first.upper()}
  SSN: {cl['ssn']}
  Claim: DIB initial
  Filed: {cm['filed']}
  Rec'd at DDS: {cm['dds_received']}
  Alleged onset: {cm['alleged_onset']}
  Field office: {cm['field_office'].replace(' Field Office', ' FO')}
  Level: Initial
  Case status: Pending MER review
---
## 1. AUTOMATED SCREEN (already completed at transfer from the field office)
The application forms (SSA-16, SSA-3368-BK, SSA-827) were taken by the field office and screened by the existing selection software on the alleged conditions in SSA-3368 Section 3.A. The forms are in this file for reference only; they have not been checked against the medical evidence.

| # | Alleged condition (claimant's words, SSA-3368 3.A) |
|---|---|
{al}

| Screen | Result |
|---|---|
| Compassionate Allowance (CAL) selection | {s['cal']} |
| Quick Disability Determination (QDD) model | {s['qdd']} |

A CAL or QDD flag is based on the claimant's allegation only. It is not a finding.

## 2. MEDICAL EVIDENCE OF RECORD IN FILE (Section F)
| Exhibit | Source | Dates of service | Pages | Received | How received |
|---|---|---|---|---|---|
{ex}

## 3. REQUESTS NOT ANSWERED
| Source | Requested | Follow-up | Status |
|---|---|---|---|
{pend}

## 4. EXAMINER ACTION
Review the medical evidence of record and decide whether the claim stays on the fast track under the study rules (condition, source of the key finding, duration).
"""
    out = CASES / cid / "records" / "00_screen.rec.md"
    out.write_text(text, encoding="utf-8")
    return out


if __name__ == "__main__":
    ids = sorted(p.name for p in CASES.iterdir() if (p / "case.json").exists()) if sys.argv[1:] == ["--all"] else sys.argv[1:]
    for c in ids:
        print("wrote", make(c))
