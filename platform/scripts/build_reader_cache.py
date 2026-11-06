"""Record the Gemini reader's output once, so the presentation app can replay it with no key.

    python scripts/build_reader_cache.py                 # demo, calibration, stress + 3 attack examples
    python scripts/build_reader_cache.py --only demo-001 # just one case

Needs GOOGLE_API_KEY in this terminal. About 24 reader calls, roughly $0.20 at list price.
Saves results/reader_cache/<case_id>.json (and <case_id>__<attack>.json). The test set is never
recorded: it is run once, after the OSF freeze, with scripts/run_batch.py.
Uses the locked reader unchanged (fasttrack.reader.GeminiReader, gemini-3.7-flash).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fasttrack.intake import LocalFolderConnector  # noqa: E402
from fasttrack.reader import PRICES, GeminiReader  # noqa: E402
from frontier_ui import replay  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "simulated"))
    ap.add_argument("--only", nargs="*", help="case ids to (re)record")
    ap.add_argument("--skip-existing", action="store_true", help="keep cases that are already recorded")
    a = ap.parse_args()

    con = LocalFolderConnector(a.data)
    reader = GeminiReader()
    stamp = datetime.now().isoformat(timespec="seconds")
    jobs = []
    for s in ("demo", "calibration", "stress"):
        for c in con.list_cases(s):
            jobs.append((c["case_id"], "base"))
    for key, spec in replay.ADVERSARIAL.items():
        jobs.append((spec["base_case"], key))
    scanned = ROOT / "data" / "scanned"
    if scanned.exists():
        sc = LocalFolderConnector(scanned)
        jobs += [("scanned:" + c["case_id"], "base") for c in sc.list_cases()]
    if a.only:
        jobs = [j for j in jobs if j[0].split(":")[-1] in a.only]

    t_in = t_out = 0
    for cid, variant in jobs:
        src = sc if cid.startswith("scanned:") else con
        cid = cid.split(":")[-1]
        case = src.load_case(cid)
        if case.case_set == "test":
            sys.exit("Refusing to record a test case.")
        if a.skip_existing and replay.has(cid, variant):
            print(f"{cid:11} {variant:18} already recorded, skipped")
            continue
        if variant != "base":
            case.documents.append(replay.adversarial_document(case, variant))
        try:
            read = reader.read(case)
        except Exception as e:
            print(f"{cid:11} {variant:18} FAILED: {str(e)[:200]}")
            continue
        replay.save(case, read, variant, reader.model, stamp)
        t_in, t_out = t_in + read.input_tokens, t_out + read.output_tokens
        print(f"{cid:11} {variant:18} {len(read.items):3} items  {read.input_tokens + read.output_tokens:6} tokens")
    p_in, p_out = PRICES.get(reader.model, (0, 0))
    print(f"\nDone. {t_in} input + {t_out} output tokens, about ${(t_in * p_in + t_out * p_out) / 1e6:.3f} at list price.")
    print("Log this in the weekly AI log. Then commit results/reader_cache/ so the web app can replay it.")


if __name__ == "__main__":
    main()
