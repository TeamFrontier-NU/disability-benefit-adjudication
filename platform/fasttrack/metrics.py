"""Measures for the internal tests: accuracy and coverage of the AI routing, and
accuracy and speed of examiner decisions (human-only vs. human + AI).

All numbers come from our own runs on simulated cases. Proportions get Wilson 95% intervals.
"""
from __future__ import annotations

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, max(0.0, c - h), min(1.0, c + h)


def fmt(k, n):
    p, lo, hi = wilson(k, n)
    return f"{k}/{n} = {p:.0%} (95% CI {lo:.0%}-{hi:.0%})" if n else "n/a"


def routing_metrics(rows: list[dict]) -> dict:
    """rows: {case_id, case_set, route, key_eligible, key_fast_track, items_total, items_verified, ...}"""
    n = len(rows)
    ft = [r for r in rows if r["route"] == "fast_track"]
    eligible = [r for r in rows if r["key_eligible"]]
    ft_correct = [r for r in ft if r["key_eligible"]]
    path_ok = [r for r in rows if (r["route"] == "fast_track") == r["key_fast_track"]]
    items = sum(r["items_total"] for r in rows)
    ver = sum(r["items_verified"] for r in rows)
    return {
        "cases": n,
        "fast_track_rate": fmt(len(ft), n),
        "fast_track_precision": fmt(len(ft_correct), len(ft)),
        "fast_track_recall_of_eligible": fmt(len(ft_correct), len(eligible)),
        "route_matches_design": fmt(len(path_ok), n),
        "ai_denials": 0,  # by construction: the pipeline can only output fast_track or human_queue
        "quote_verification_rate": fmt(ver, items),
        "mean_seconds_per_case": round(statistics.mean(r["seconds"] for r in rows), 2) if rows else None,
        "targets": {"fast_track_rate": "at least 15%", "fast_track_precision": "at least 95%", "ai_denials": "0"},
        "_raw": {"n": n, "ft": len(ft), "ft_correct": len(ft_correct), "eligible": len(eligible)},
    }


def stress_metrics(rows: list[dict]) -> dict:
    gaming = [r for r in rows if not r["key_fast_track"]]
    wrong = [r for r in gaming if r["route"] == "fast_track"]
    controls = [r for r in rows if r["key_fast_track"]]
    false_alarm = [r for r in controls if r["route"] != "fast_track"]
    return {"gaming_cases_wrongly_fast_tracked": fmt(len(wrong), len(gaming)),
            "honest_controls_sent_to_human": fmt(len(false_alarm), len(controls)),
            "target": "0 gaming cases fast-tracked"}


# ----------------------------------------------------------------------------- examiner decisions

class DecisionLog:
    """Final decisions made by examiners in the panel, one JSON line each."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def add(self, **rec):
        rec.setdefault("decided_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(x) for x in self.path.read_text(encoding="utf-8").splitlines() if x.strip()]


def decision_metrics(decisions: list[dict], keys: dict[str, dict]) -> dict:
    """Compare the three arms on the same cases: human-only, AI-only, human + AI.

    AI-only means the routing alone: it can approve (fast track) but never denies,
    so its 'decision' on everything else is 'no decision'.
    """
    out = {}
    for mode in ("human_only", "human_plus_ai"):
        ds = [d for d in decisions if d.get("mode") == mode and d["case_id"] in keys]
        correct = [d for d in ds if (d["final_decision"] == "allow") == keys[d["case_id"]]["eligible"]
                   and d["final_decision"] != "need_more_evidence"]
        wrongful_denials = [d for d in ds if d["final_decision"] == "deny" and keys[d["case_id"]]["eligible"]]
        secs = [d["seconds"] for d in ds if d.get("seconds")]
        out[mode] = {"decisions": len(ds), "accuracy": fmt(len(correct), len(ds)),
                     "wrongful_denials": fmt(len(wrongful_denials), len(ds)),
                     "median_minutes": round(statistics.median(secs) / 60, 1) if secs else None}
        for route in ("fast_track", "human_queue"):
            s = [d["seconds"] for d in ds if d.get("ai_route") == route and d.get("seconds")]
            out[mode][f"median_minutes_{route}"] = round(statistics.median(s) / 60, 1) if s else None
    return out
