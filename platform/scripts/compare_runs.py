"""Compare repeated runs of the same set, case by case (run-to-run stability, issue I-17).

    python scripts/compare_runs.py results/calibration_gemini_k1_*.json

Give two or more results files from the same set and k. Prints each case's route in every run,
marks cases whose route changed, and counts how many cases kept the same route in all runs.
Files from failed calls (every case errored, or no tokens) are skipped with a note.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(paths):
    runs = []
    for p in paths:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
        rows = d.get("rows", [])
        if d.get("reader", "").startswith("Gemini") and not d.get("tokens"):
            print(f"skip {Path(p).name}: no token counts, so the reader did not answer (failed call)")
            continue
        if rows and all(r.get("reader_error") for r in rows):
            print(f"skip {Path(p).name}: the reader failed on every case")
            continue
        runs.append((Path(p).name, d, {r["case_id"]: r for r in rows}))
    if len(runs) < 2:
        sys.exit("Need at least two usable results files.")
    sets = {(d["set"], d["k"]) for _, d, _ in runs}
    if len(sets) > 1:
        sys.exit(f"Files mix different sets or k values: {sorted(sets)}")
    ids = sorted(set().union(*(r.keys() for _, _, r in runs)))
    print("Runs:")
    for i, (name, d, _) in enumerate(runs, 1):
        print(f"  {i}. {name}  ({d['reader']}, {d['metrics']['route_matches_design']} match the key)")
    print(f"\n{'case':11} " + " ".join(f"{'run ' + str(i):12}" for i in range(1, len(runs) + 1)) + " key")
    same = 0
    for cid in ids:
        routes = [r.get(cid, {}).get("route", "-") for _, _, r in runs]
        key = next((r[cid]["key_fast_track"] for _, _, r in runs if cid in r), None)
        stable = len(set(routes)) == 1
        same += stable
        print(f"{cid:11} " + " ".join(f"{x:12}" for x in routes)
              + f" {'fast_track' if key else 'human_queue'}" + ("" if stable else "   <-- changed"))
    print(f"\nSame route in all {len(runs)} runs: {same}/{len(ids)} cases")


if __name__ == "__main__":
    main(sys.argv[1:])
