"""Check Replay mode after recording, with no API key (offline).

    python scripts/check_replay.py

1. Runs every recorded case through the locked pipeline (the same code the app uses) and prints the
   route, whether it matches the answer key, any reader error, and how it compares with the latest
   saved batch run (results/*.json). Also the 3 attacks on Peter.
2. Opens every app page headlessly (Streamlit AppTest) and reports any error on the page.
3. Writes the report to results/reader_cache/REPLAY-CHECK.md and prints token totals and cost.
Never touches the test set and never calls an API.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
for v in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "ANTHROPIC_API_KEY", "LIVE_PASSCODE"):
    os.environ.pop(v, None)  # prove Replay needs no key

from fasttrack.intake import LocalFolderConnector  # noqa: E402
from fasttrack.pipeline import run_case  # noqa: E402
from fasttrack.reader import PRICES  # noqa: E402
from frontier_ui import replay  # noqa: E402

WORD = {"fast_track": "fast track", "human_queue": "human queue"}


def latest_batch_routes() -> dict:
    """case_id -> route from the latest successful Gemini k = 1 batch run of each set."""
    best = {}
    for f in sorted((ROOT / "results").glob("*_gemini_k1_*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("set") == "test" or not d.get("tokens"):
            continue
        best[d["set"]] = (f.name, {r["case_id"]: r["route"] for r in d["rows"]})
    out = {}
    for name, routes in best.values():
        for cid, r in routes.items():
            out[cid] = (r, name)
    return out


def main():
    con = LocalFolderConnector(ROOT / "data" / "simulated")
    earlier = latest_batch_routes()
    lines = [f"# Replay check, {datetime.now():%Y-%m-%d %H:%M}", "",
             "| Case | Set | Variant | Route | Answer key | Match | Earlier batch run | Reader error |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    t_in = t_out = 0
    problems, gaming, gaming_ft = [], 0, 0
    jobs = [(c["case_id"], "base") for s in ("demo", "calibration", "stress") for c in con.list_cases(s)]
    jobs += [(spec["base_case"], k) for k, spec in replay.ADVERSARIAL.items()]
    for cid, variant in jobs:
        case = con.load_case(cid)
        if case.case_set == "test":
            sys.exit("Test case found: stopping.")
        rec = replay.load(cid, variant)
        if rec is None:
            lines.append(f"| {cid} | {case.case_set} | {variant} | NOT RECORDED | | | | |")
            problems.append(f"{cid} {variant}: not recorded")
            continue
        t_in += rec["read"].get("input_tokens", 0)
        t_out += rec["read"].get("output_tokens", 0)
        if variant != "base":
            case.documents.append(replay.adversarial_document(case, variant))
        res = run_case(case, replay.ReplayReader(variant), 1, True)
        key = con.answer_key(cid) or {}
        want = "fast_track" if key.get("fast_track") else "human_queue"
        if variant != "base":
            want = "human_queue"  # an attack must never move Peter onto the fast track
        match = res.routing.route == want
        err = next((m for m in res.read.missing_evidence if str(m).startswith("Reader failed")), "")
        prev = earlier.get(cid) if variant == "base" else None
        prev_txt = "" if not prev else ("same" if prev[0] == res.routing.route else f"DIFFERENT (was {WORD[prev[0]]})")
        if case.case_set == "stress" and variant == "base" and not key.get("fast_track"):
            gaming += 1
            gaming_ft += res.routing.route == "fast_track"
        if not match:
            problems.append(f"{cid} {variant}: route {res.routing.route}, expected {want}")
        if prev_txt.startswith("DIFFERENT"):
            problems.append(f"{cid}: route differs from the earlier batch run {prev[1]}")
        if err:
            problems.append(f"{cid} {variant}: reader error")
        lines.append(f"| {cid} | {case.case_set} | {variant} | {WORD[res.routing.route]} | {WORD[want]} | "
                     f"{'yes' if match else 'NO'} | {prev_txt} | {err[:80]} |")
    p_in, p_out = PRICES.get("gemini-3.7-flash", (0, 0))
    cost = (t_in * p_in + t_out * p_out) / 1e6
    lines += ["", f"- Stress set: {gaming_ft} of {gaming} gaming cases fast-tracked",
              f"- Recorded tokens: {t_in:,} input + {t_out:,} output = {t_in + t_out:,}; about ${cost:.3f} "
              "at the $0.75 / $3.75 per million list price"]

    # pages, headless
    try:
        from streamlit.testing.v1 import AppTest
        lines += ["", "## App pages (headless, no key)", ""]
        for page in ("overview", "case_explorer", "safeguards", "results", "about"):
            at = AppTest.from_file(str(ROOT / "views" / f"{page}.py"), default_timeout=60)
            at.run()
            errs = [e.value for e in at.exception]
            lines.append(f"- {page}: {'OK' if not errs else 'ERROR ' + str(errs)[:200]}")
            if errs:
                problems.append(f"page {page}: error")
    except Exception as e:
        lines.append(f"- page check skipped: {e}")

    lines += ["", "## Problems", ""] + ([f"- {p}" for p in problems] or ["- none"])
    out = replay.CACHE / "REPLAY-CHECK.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nsaved {out}")


if __name__ == "__main__":
    main()
