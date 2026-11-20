"""Gift-card winners (approved by Diego, Nov 18): six $10 cards, the top 3 scorers by accuracy
in each group (AI / No-AI), among participants who completed the full study; ties by lottery.

    python study/analysis/winners.py --responses <06_data>/responses.csv \
        --key <03_answer_key>/final.csv [--contacts <06_data>/contacts.csv] \
        [--min-seconds <threshold>] [--seed <number announced before the draw>] \
        --exclude <ids or a file of ids> --out winners.csv

Score = number of assigned cases answered correctly. Only participants with all
--cases-per-person (default 3) answers count; TEST- runs are dropped. With --min-seconds,
a case answered faster than the threshold counts as invalid (scored wrong). Ties at the
cut-off are broken by a random draw; fix --seed in advance and write it down so the draw
can be repeated. Team members are not eligible: pass their participant IDs with --exclude
(comma-separated, or a file with one ID per line, kept in the shared drive). The script stops if
--exclude is missing, so they cannot be left in by accident; pass --exclude none if no team member
took part. The output holds names and emails: keep it in the shared drive only,
never in the repository.
"""
from __future__ import annotations

import argparse
import random
from pathlib import Path

import pandas as pd

PER_GROUP = 3


def read_ids(arg: str) -> set[str]:
    """--exclude value: 'none', a file with one ID per line, or comma-separated IDs."""
    if arg.strip().lower() == "none":
        return set()
    p = Path(arg)
    text = p.read_text(encoding="utf-8-sig") if p.is_file() else arg
    return {x.strip() for x in text.replace(",", "\n").splitlines() if x.strip()}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--responses", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--contacts", help="contacts.csv (participant_id, name, email)")
    ap.add_argument("--cases-per-person", type=int, default=3)
    ap.add_argument("--min-seconds", type=float, default=0)
    ap.add_argument("--seed", type=int, default=425)
    ap.add_argument("--exclude", required=True,
                    help="team members' participant IDs: comma-separated, a file with one per line, or 'none'")
    ap.add_argument("--out", default="winners.csv")
    a = ap.parse_args()
    exclude = read_ids(a.exclude)

    r = pd.read_csv(a.responses, dtype={"participant_id": str})
    k = pd.read_csv(a.key, dtype=str)
    k["answer"] = k["answer"].str.strip().str.lower()
    r = r[~r["participant_id"].str.upper().str.startswith("TEST")]
    excluded = sorted(set(r["participant_id"]) & exclude)
    r = r[~r["participant_id"].isin(exclude)]
    print(f"excluded as team members: {len(excluded)} participant(s) with answers {excluded}")
    missing = sorted(exclude - set(excluded))
    if missing:
        print(f"note: {len(missing)} excluded ID(s) have no answers in this file: {missing}")
    r = r.drop_duplicates(["participant_id", "case_id"], keep="first")
    r = r.merge(k[["case_id", "answer"]].rename(columns={"answer": "key"}), on="case_id")
    r["correct"] = (r["answer"].str.strip().str.lower() == r["key"]).astype(int)
    if a.min_seconds > 0:
        r.loc[r["seconds"] < a.min_seconds, "correct"] = 0

    g = r.groupby(["participant_id", "arm"]).agg(cases=("case_id", "nunique"),
                                                score=("correct", "sum"),
                                                seconds=("seconds", "sum")).reset_index()
    g = g[g["cases"] >= a.cases_per_person]
    rng = random.Random(a.seed)
    g["draw"] = [rng.random() for _ in range(len(g))]

    picks = []
    for arm, d in g.groupby("arm"):
        d = d.sort_values(["score", "draw"], ascending=[False, True]).head(PER_GROUP).copy()
        cut = d["score"].min() if len(d) else None
        tied = int((g[(g["arm"] == arm)]["score"] == cut).sum()) if cut is not None else 0
        d["rank"] = range(1, len(d) + 1)
        d["note"] = [f"tie at score {cut} among {tied}, decided by draw" if s == cut and tied > (d["score"] == cut).sum() else ""
                     for s in d["score"]]
        picks.append(d)
        print(f"{arm}: {len(g[g['arm'] == arm])} eligible; winners' scores {list(d['score'])}"
              + (f"; {tied} people tied at {cut}, draw used" if tied > (d['score'] == cut).sum() else ""))
    w = pd.concat(picks) if picks else g.head(0)
    if a.contacts:
        c = pd.read_csv(a.contacts, dtype={"participant_id": str})[["participant_id", "name", "email"]]
        w = w.merge(c.drop_duplicates("participant_id"), on="participant_id", how="left")
    cols = [x for x in ["arm", "rank", "participant_id", "name", "email", "score", "cases", "note"] if x in w.columns]
    w[cols].to_csv(a.out, index=False)
    print(f"seed {a.seed}; wrote {len(w)} winners to {a.out} (shared drive only)")


if __name__ == "__main__":
    main()
