"""Add up the reader's API cost across every saved run in results/.

    python scripts/cost_to_date.py

Uses the token counts saved in each results file and the prices in fasttrack/reader.py (PRICES),
so older files that say estimated_cost_usd: 0.0 are priced correctly. Runs with no token counts
(failed calls, the offline keyword reader) count as $0. This is an estimate at list price: the
Google Cloud billing page is the figure to report.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from fasttrack.reader import PRICES  # noqa: E402


def model_of(reader_name: str) -> str:
    if (reader_name or "").startswith("Keyword"):
        return "keyword (offline)"
    m = re.search(r"\(([^)]+)\)", reader_name or "")
    return m.group(1) if m else reader_name


def main():
    rows, total_in, total_out, total = [], 0, 0, 0.0
    for f in sorted((ROOT / "results").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        tok = d.get("tokens") or {}
        t_in, t_out = tok.get("input", 0), tok.get("output", 0)
        model = model_of(d.get("reader", ""))
        p_in, p_out = PRICES.get(model, (None, None))
        if t_in and p_in is None:
            cost, note = 0.0, "NO PRICE in PRICES: add one"
        else:
            cost = (t_in * (p_in or 0) + t_out * (p_out or 0)) / 1e6
            note = "" if t_in else "no tokens (failed call or offline)"
        rows.append((f.name, model, len(d.get("rows", [])), t_in, t_out, cost, note))
        total_in, total_out, total = total_in + t_in, total_out + t_out, total + cost
    print(f"{'file':48} {'model':18} {'cases':>5} {'in':>8} {'out':>8} {'USD':>8}")
    for name, model, n, t_in, t_out, cost, note in rows:
        print(f"{name:48} {model[:18]:18} {n:5} {t_in:8} {t_out:8} {cost:8.4f}  {note}")
    print(f"{'TOTAL':48} {'':18} {'':5} {total_in:8} {total_out:8} {total:8.4f}")


if __name__ == "__main__":
    main()
