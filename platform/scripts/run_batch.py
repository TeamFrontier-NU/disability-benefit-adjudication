"""Run the pipeline on a whole set of simulated cases and report the measures.

    python scripts/run_batch.py --set calibration --reader keyword --k 1
    python scripts/run_batch.py --set test --reader gemini --k 1      # needs a Google Cloud project or Gemini API key
    python scripts/run_batch.py --set test --reader claude --k 1      # needs ANTHROPIC_API_KEY

Results are saved to results/<set>_<reader>_k<k>_<time>.json for the AI log.
Never change prompts or k after looking at test-set results (pre-registration).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fasttrack.intake import LocalFolderConnector  # noqa: E402
from fasttrack.metrics import routing_metrics, stress_metrics  # noqa: E402
from fasttrack.pipeline import run_case  # noqa: E402
from fasttrack.reader import ClaudeReader, GeminiReader, KeywordReader  # noqa: E402


# USD per million tokens (input, output). Gemini 3.8 Flash: Google's listed rate through Dec 31, 2026,
# doubling from Jan 1, 2027. Check the Cloud billing page for the real charge.
PRICES = {"gemini": (0.75, 3.75), "claude": (2, 10)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "simulated"))
    ap.add_argument("--set", default="calibration", choices=["demo", "calibration", "test", "stress"])
    ap.add_argument("--reader", default="keyword", choices=["keyword", "gemini", "claude"])
    ap.add_argument("--k", type=int, default=1, help="AMS documents required per criterion (the one tuned setting)")
    a = ap.parse_args()

    con = LocalFolderConnector(a.data)
    reader = {"gemini": GeminiReader, "claude": ClaudeReader, "keyword": KeywordReader}[a.reader]()
    rows = []
    for c in con.list_cases(a.set):
        case, key = con.load_case(c["case_id"]), con.answer_key(c["case_id"])
        res = run_case(case, reader, a.k)
        rows.append(dict(case_id=case.case_id, case_set=case.case_set, profile=key.get("profile"),
                         route=res.routing.route, path=res.routing.path, reasons=res.routing.reasons,
                         key_eligible=key["eligible"], key_fast_track=key["fast_track"],
                         items_total=len(res.read.items), items_verified=sum(i.verified for i in res.read.items),
                         seconds=res.seconds, input_tokens=res.read.input_tokens,
                         output_tokens=res.read.output_tokens))
        mark = "ok" if (res.routing.route == "fast_track") == key["fast_track"] else "MISMATCH"
        print(f"{case.case_id:11} {key.get('profile', '')[:26]:26} {res.routing.route:11} {mark}")

    report = {"set": a.set, "reader": reader.name, "k": a.k, "run_at": datetime.now().isoformat(timespec="seconds"),
              "metrics": routing_metrics(rows)}
    if a.set == "stress":
        report["stress"] = stress_metrics(rows)
    tokens_in = sum(r["input_tokens"] for r in rows)
    tokens_out = sum(r["output_tokens"] for r in rows)
    if tokens_in:
        p_in, p_out = PRICES.get(a.reader, (0, 0))
        report["estimated_cost_usd"] = round(tokens_in * p_in / 1e6 + tokens_out * p_out / 1e6, 3)
    report["rows"] = rows
    out = ROOT / "results" / f"{a.set}_{a.reader}_k{a.k}_{datetime.now():%Y%m%d-%H%M%S}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
