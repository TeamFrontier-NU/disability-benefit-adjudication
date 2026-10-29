"""Blind check of the answer keys by people who did not write the cases.

1. Export review packets (case documents only: no answer key, no AI output):
       python scripts/blind_check.py export --sets calibration test --checkers "Name A" "Name B" "Name C" --out blind-check
   Each case is assigned to two different checkers. Every checker gets a folder of case files and
   one CSV to fill in: decision = allow, deny or need_more_evidence, plus the basis.

2. Score the filled-in CSVs against the answer keys and against each other:
       python scripts/blind_check.py score --out blind-check
   Prints agreement and Cohen's kappa, lists every disagreement, and writes blind-check/summary.md.
   Add --write to record checker_1, checker_2 and agreed in each answer_key.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import defaultdict
from itertools import cycle
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fasttrack.intake import LocalFolderConnector  # noqa: E402

DECISIONS = {"allow", "deny", "need_more_evidence"}


def eligible(decision: str) -> bool:
    return decision.strip().lower() == "allow"


def kappa(pairs: list[tuple[bool, bool]]) -> float:
    n = len(pairs)
    if not n:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    pa = sum(a for a, _ in pairs) / n
    pb = sum(b for _, b in pairs) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def export(a):
    con = LocalFolderConnector(a.data)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cases = [c for s in a.sets for c in con.list_cases(s)]
    if len(a.checkers) < 2:
        sys.exit("Need at least two checkers.")
    pairs = cycle([(x, y) for i, x in enumerate(a.checkers) for y in a.checkers[i + 1:]])
    assign = defaultdict(list)
    for c in cases:
        x, y = next(pairs)
        assign[x].append(c["case_id"])
        assign[y].append(c["case_id"])
    for checker, ids in assign.items():
        cdir = out / checker.replace(" ", "_")
        if cdir.exists():
            shutil.rmtree(cdir)
        (cdir / "cases").mkdir(parents=True)
        for cid in ids:
            case = con.load_case(cid)
            parts = [f"# Case {cid}\n\nClaim type: {case.claim_type} · Filing date: {case.filing_date}\n"
                     f"Providers listed in SSA-3368 section 8: {', '.join(case.listed_providers) or 'none'}\n"]
            for d in case.documents:
                parts.append(f"\n## {d.title}\n_Written by: {d.source_type}; received via: {d.received_via}_\n")
                for p, t in sorted(d.pages.items()):
                    parts.append(f"\n**Page {p}**\n\n{t}\n")
            (cdir / "cases" / f"{cid}.md").write_text("".join(parts), encoding="utf-8")
        with (cdir / "decisions.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["case_id", "checker", "decision", "basis", "minutes", "notes"])
            for cid in ids:
                w.writerow([cid, checker, "", "", "", ""])
        print(f"{checker}: {len(ids)} cases -> {cdir}")
    (out / "README.md").write_text(
        "# Blind check of the answer keys\n\n"
        "Open your folder. For each file in `cases/`, decide as an examiner would, **without** looking at "
        "`answer_key.json`, the panel, or anyone else's sheet.\n\n"
        "Fill in `decisions.csv`: `decision` is `allow`, `deny` or `need_more_evidence`; `basis` is the rule "
        "(for example \"meets 11.08A\", \"grid 201.09\", \"not severe at Step 2\"); `minutes` is how long it took.\n\n"
        "When everyone is done, run `python scripts/blind_check.py score --out blind-check`.\n", encoding="utf-8")


def score(a):
    con = LocalFolderConnector(a.data)
    out = Path(a.out)
    rows = []
    for f in sorted(out.glob("*/decisions.csv")):
        with f.open(encoding="utf-8") as fh:
            rows += [r for r in csv.DictReader(fh) if r.get("decision", "").strip()]
    bad = [r for r in rows if r["decision"].strip().lower() not in DECISIONS]
    if bad:
        sys.exit(f"Unknown decisions: {[(r['case_id'], r['decision']) for r in bad]}")
    by_case = defaultdict(list)
    for r in rows:
        by_case[r["case_id"]].append(r)
    keys = {cid: con.answer_key(cid) for cid in by_case}
    vs_key = [(eligible(r["decision"]), keys[r["case_id"]]["eligible"]) for r in rows]
    between = [(eligible(rs[0]["decision"]), eligible(rs[1]["decision"])) for rs in by_case.values() if len(rs) >= 2]
    disagreements = []
    for cid, rs in sorted(by_case.items()):
        k = keys[cid]
        votes = {eligible(r["decision"]) for r in rs}
        if len(votes) > 1 or votes != {k["eligible"]}:
            disagreements.append((cid, k, rs))
    lines = ["# Blind check results\n",
             f"- Decisions recorded: {len(rows)} on {len(by_case)} cases",
             f"- Checker vs. answer key (allow vs. not): {sum(x == y for x, y in vs_key)}/{len(vs_key)} agree, "
             f"kappa {kappa(vs_key):.2f}",
             f"- Checker vs. checker: {sum(x == y for x, y in between)}/{len(between)} agree, kappa {kappa(between):.2f}",
             f"- Cases to discuss (any disagreement): {len(disagreements)}\n",
             "| Case | Answer key | Checkers |", "| --- | --- | --- |"]
    for cid, k, rs in disagreements:
        lines.append(f"| {cid} | {'eligible' if k['eligible'] else 'not eligible'} ({k['basis']}) | "
                     + "; ".join(f"{r['checker']}: {r['decision']} ({r['basis']})" for r in rs) + " |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    if a.write:
        for cid, rs in by_case.items():
            f = Path(a.data) / cid / "answer_key.json"
            k = json.loads(f.read_text(encoding="utf-8"))
            for i, r in enumerate(rs[:2], 1):
                k[f"checker_{i}"] = {"name": r["checker"], "decision": r["decision"], "basis": r["basis"]}
            k["agreed"] = all(eligible(r["decision"]) == k["eligible"] for r in rs)
            f.write_text(json.dumps(k, indent=2), encoding="utf-8")
        print(f"Recorded checker results in {len(by_case)} answer keys.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "simulated"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--sets", nargs="+", default=["calibration", "test"])
    e.add_argument("--checkers", nargs="+", required=True)
    e.add_argument("--out", default="blind-check")
    s = sub.add_parser("score")
    s.add_argument("--out", default="blind-check")
    s.add_argument("--write", action="store_true")
    a = ap.parse_args()
    export(a) if a.cmd == "export" else score(a)


if __name__ == "__main__":
    main()
