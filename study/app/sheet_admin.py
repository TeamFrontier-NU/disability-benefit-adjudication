"""Set up, check and clear the study Google Sheet (Group C, ZXH). Run on your own computer.

    python study/app/sheet_admin.py setup        # create tabs + headers, fill allocation (once)
    python study/app/sheet_admin.py status       # row counts per tab
    python study/app/sheet_admin.py clear-test   # delete TEST- rows (team test runs)
    python study/app/sheet_admin.py clear-all --yes   # before real data collection: empty every
                                                      # data tab (pilot rows, contacts, slots used)

Credentials come from .streamlit/secrets.toml at the repository root (gitignored; same
content as the Streamlit Secrets) or from STUDY_LOCAL_SHEET for offline tests.
Run clear-test / clear-all only while nobody is taking the study (they rewrite the tabs).

`setup` draws the allocation with a fresh random seed and prints it ONCE. Save it to the
shared drive `06_data/seed.txt`. Never commit it. The allocation table itself lives only
in the Sheet. `setup` refuses to redraw an allocation that already has rows.
"""
from __future__ import annotations

import argparse
import os
import random
import secrets
import sys
import tomllib
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import data as D  # noqa: E402

N_ROWS = 200
DATA_TABS = ["responses", "contacts", "assignments", "participants", "training", "survey",
             "test_assignments"]


def _load_secrets() -> None:
    if os.environ.get("STUDY_LOCAL_SHEET"):
        return
    tries = [HERE.parents[1] / ".streamlit" / "secrets.toml", HERE / ".streamlit" / "secrets.toml"]
    path = next((p for p in tries if p.exists()), None)
    if path is None:
        sys.exit(f"Missing {tries[0]} (copy the Streamlit Secrets there; it is gitignored).")
    sec = tomllib.loads(path.read_text(encoding="utf-8"))
    D._secrets = lambda: sec  # use the same secrets outside Streamlit


def draw_allocation(seed: int, n: int = N_ROWS) -> list[list]:
    """Blocks of 2, one ai + one noai each, order random within the block."""
    rng = random.Random(seed)
    rows = []
    for b in range(n // 2):
        pair = ["ai", "noai"]
        rng.shuffle(pair)
        for arm in pair:
            rows.append([len(rows) + 1, b + 1, arm])
    return rows


def setup() -> None:
    book = D._book()
    have = {w.title for w in book.worksheets()}
    for tab, cols in D.TABS.items():
        if tab not in have:
            book.add_worksheet(title=tab, rows=1000 if tab != "allocation" else N_ROWS + 10,
                               cols=len(cols) + 2)
            print(f"created tab {tab}")
        w = book.worksheet(tab)
        head = (w.get_all_values() or [[]])[0]
        if not head:
            w.update([cols], "A1")
        elif head[:len(cols)] != cols:
            sys.exit(f"tab {tab} has unexpected headers {head}; fix by hand before continuing")
    alloc = book.worksheet("allocation")
    if len(alloc.get_all_values()) > 1:
        print("allocation already filled: left unchanged")
    else:
        seed = secrets.randbits(32)
        alloc.update([D.TABS["allocation"]] + draw_allocation(seed), "A1")
        print(f"allocation filled with {N_ROWS} rows.\n\n  SEED = {seed}\n\n"
              "Save this number to the shared drive 06_data/seed.txt now. Do not commit it.")
    status()


def status() -> None:
    for tab in D.TABS:
        try:
            n = len(D.ws(tab).get_all_values()) - 1
        except Exception as e:  # noqa: BLE001
            print(f"{tab:18} ERROR {e}")
            continue
        print(f"{tab:18} {max(n, 0)} rows")


def _rewrite(tab: str, keep) -> int:
    w = D.ws(tab)
    vals = w.get_all_values()
    if not vals:
        return 0
    head, rows = vals[0], vals[1:]
    kept = [r for r in rows if keep(r)]
    removed = len(rows) - len(kept)
    if removed:
        w.clear()
        w.update([head] + kept, "A1")
    return removed


def clear_test() -> None:
    for tab in DATA_TABS:
        n = _rewrite(tab, lambda r: not (r and r[0].startswith("TEST-")))
        print(f"{tab:18} removed {n} TEST- rows")


def clear_all() -> None:
    for tab in DATA_TABS:
        n = _rewrite(tab, lambda r: False)
        print(f"{tab:18} removed {n} rows")
    print("allocation kept; the next participant gets slot 1 again.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["setup", "status", "clear-test", "clear-all"])
    ap.add_argument("--yes", action="store_true", help="confirm clear-all")
    a = ap.parse_args()
    _load_secrets()
    if a.cmd == "setup":
        setup()
    elif a.cmd == "status":
        status()
    elif a.cmd == "clear-test":
        clear_test()
    elif a.cmd == "clear-all":
        if not a.yes:
            sys.exit("clear-all deletes every data row (allocation kept). Re-run with --yes.")
        clear_all()


if __name__ == "__main__":
    main()
