"""Fake study data for testing the analysis script (Group C, ZXH -> WYX). NOT real data.

    python study/analysis/fake_data.py                    # 30 people x 6 cases
    python study/analysis/fake_data.py --n 40 --seed 7 --out fake_responses.csv

Writes `responses` rows in the exact HANDOFF.md 3.5 columns (what the app writes to the
Sheet), plus `fake_key.csv` with a RANDOM yes/no per case so the script can compute
`correct`. The fake key has nothing to do with the real answer key. CSV files are
gitignored; do not commit outputs.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

COLUMNS = ["participant_id", "lang", "arm", "case_id", "case_order", "answer", "confidence",
           "seconds", "started_at", "submitted_at", "training_attempts", "heard_about_study"]
CASES = ["C1", "C2", "C3", "C4", "C5", "C6"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    ap.add_argument("--seed", type=int, default=425)
    ap.add_argument("--out", default="fake_responses.csv")
    ap.add_argument("--key-out", default="fake_key.csv")
    a = ap.parse_args()
    rng = random.Random(a.seed)

    key = {c: rng.choice(["yes", "no"]) for c in CASES}
    with open(a.key_out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "answer"])
        w.writerows(key.items())

    rows = []
    t = datetime(2026, 11, 20, 14, 0, tzinfo=timezone.utc)
    arms: list[str] = []
    while len(arms) < a.n:  # blocks of 2, as in the real allocation
        pair = ["ai", "noai"]
        rng.shuffle(pair)
        arms += pair
    for i in range(a.n):
        arm = arms[i]
        pid = f"P{rng.getrandbits(32):08x}"
        lang = rng.choice(["en", "en", "zh"])
        attempts = 1 if rng.random() < 0.8 else 2
        heard = rng.choice(["", "class", "friend", "flyer"])
        skill = rng.gauss(0, 0.6)
        order = CASES[:]
        rng.shuffle(order)
        t += timedelta(minutes=rng.randint(5, 60))
        clock = t
        for pos, cid in enumerate(order, 1):
            p_right = 1 / (1 + math.exp(-(0.9 + skill + (0.5 if arm == "ai" else 0))))
            right = rng.random() < p_right
            ans = key[cid] if right else ("no" if key[cid] == "yes" else "yes")
            secs = round(math.exp(rng.gauss(4.4 - (0.25 if arm == "ai" else 0), 0.4)), 1)
            start, end = clock, clock + timedelta(seconds=secs)
            clock = end + timedelta(seconds=rng.randint(2, 8))
            rows.append({
                "participant_id": pid, "lang": lang, "arm": arm, "case_id": cid,
                "case_order": pos, "answer": ans,
                "confidence": min(5, max(1, round(rng.gauss(3.5 if right else 2.8, 1)))),
                "seconds": secs, "started_at": start.isoformat(timespec="seconds"),
                "submitted_at": end.isoformat(timespec="seconds"),
                "training_attempts": attempts, "heard_about_study": heard,
            })
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {Path(a.out).resolve()} and a FAKE key to {a.key_out}")


if __name__ == "__main__":
    main()
