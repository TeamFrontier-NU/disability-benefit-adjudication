"""Quick look at a data export: who took part, what they answered, how long each step took.

    python study/analysis/quick_check.py <export folder or .zip>
    python study/analysis/quick_check.py study_export.zip --email someone@school.edu   # one person
    python study/analysis/quick_check.py study_export.zip --key <03_answer_key>/final.csv

The export comes from the app (`<app URL>/?export=1&k=<test word>` -> Download all tables) or
from `python study/app/sheet_admin.py export --out <folder>`. It needs only `responses.csv`;
`timings.csv`, `participants.csv` and `contacts.csv` are used when present.

This is a data check, not the pre-registered analysis (that is analyze.py). It prints:
  1. participants by group and language (TEST- rows shown separately)
  2. one line per participant: cases done, answers, total and median seconds per case
  3. per case and group: share answering yes, mean confidence, seconds (median, mean),
     seconds to the first Yes/No click, answer changes; with --key, share correct
  4. seconds on the other pages (welcome, rule card, training cases, wrap-up)
  5. a regression of log(seconds) on group with case fixed effects, when there is enough data
Writes nothing unless --out is given. Never commit its output when the data are real.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


def read_tables(src: str) -> dict[str, pd.DataFrame]:
    p = Path(src).expanduser()
    out: dict[str, pd.DataFrame] = {}
    if p.suffix == ".zip":
        with zipfile.ZipFile(p) as z:
            for n in z.namelist():
                if n.endswith(".csv"):
                    out[Path(n).stem] = pd.read_csv(io.BytesIO(z.read(n)), dtype=str,
                                                    encoding="utf-8-sig").fillna("")
    elif p.is_dir():
        for f in p.glob("*.csv"):
            out[f.stem] = pd.read_csv(f, dtype=str, encoding="utf-8-sig").fillna("")
    elif p.suffix == ".csv":
        out["responses"] = pd.read_csv(p, dtype=str, encoding="utf-8-sig").fillna("")
    if "responses" not in out:
        sys.exit(f"No responses.csv in {p}")
    return out


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.replace("", np.nan), errors="coerce")


def md(df: pd.DataFrame) -> str:
    if df.empty:
        return "_(none)_"
    try:
        return df.to_markdown(index=False, floatfmt=".1f")
    except ImportError:  # tabulate missing
        return df.to_string(index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("export", help="export folder, .zip, or responses.csv")
    ap.add_argument("--email", help="show only this participant (looked up in contacts.csv)")
    ap.add_argument("--participant", help="show only this participant_id")
    ap.add_argument("--key", help="answer key CSV (case_id,answer) to add share correct")
    ap.add_argument("--no-test", action="store_true", help="drop TEST- rows")
    ap.add_argument("--out", help="also write the report to this .md file")
    a = ap.parse_args()

    t = read_tables(a.export)
    r = t["responses"].copy()
    lines: list[str] = [f"# Quick check of `{Path(a.export).name}`", ""]

    pid = a.participant
    if a.email:
        c = t.get("contacts")
        if c is None:
            sys.exit("--email needs contacts.csv in the export (tick 'include names and emails')")
        hit = c[c["email"].str.strip().str.lower() == a.email.strip().lower()]
        if hit.empty:
            sys.exit(f"{a.email} is not in contacts.csv")
        pid = hit["participant_id"].iloc[-1]
        lines += [f"Participant for {a.email}: `{pid}` "
                  f"({len(hit)} sign-up(s); the latest is used)", ""]
    if a.no_test:
        r = r[~r["participant_id"].str.startswith("TEST-")]
    if pid:
        r = r[r["participant_id"] == pid]
    if r.empty:
        lines.append("No case answers for this selection.")
        print("\n".join(lines))
        return

    for col in ("seconds", "confidence", "seconds_to_answer", "seconds_to_confidence",
                "answer_changes", "case_order"):
        r[col] = num(r[col]) if col in r else np.nan
    # keep the first row per person and case (a retried save can write a duplicate)
    r = r.drop_duplicates(["participant_id", "case_id"], keep="first")
    r["kind"] = np.where(r["participant_id"].str.startswith("TEST-"), "test run", "participant")

    if a.key:
        k = pd.read_csv(a.key, dtype=str)
        k.columns = [x.strip().lower() for x in k.columns]
        k = k.assign(case_id=k["case_id"].str.strip(), key=k["answer"].str.strip().str.lower())
        r = r.merge(k[["case_id", "key"]], on="case_id", how="left")
        r["correct"] = (r["answer"].str.lower() == r["key"]).astype(float)
        r.loc[r["key"].isna(), "correct"] = np.nan

    # 1. sample
    lines += ["## 1. Participants", ""]
    s = (r.groupby(["kind", "arm", "lang"])["participant_id"].nunique()
         .rename("participants").reset_index())
    lines += [md(s), ""]

    # 2. per participant
    lines += ["## 2. One line per participant", ""]
    g = r.sort_values("case_order").groupby("participant_id")
    per = pd.DataFrame({
        "arm": g["arm"].first(), "lang": g["lang"].first(), "cases": g.size(),
        "answers": g.apply(lambda x: " ".join(f"{c}:{v}" for c, v in zip(x.case_id, x.answer)),
                           include_groups=False),
        "total_min": g["seconds"].sum() / 60, "median_s_per_case": g["seconds"].median(),
        "first": g["submitted_at"].min(),
    }).reset_index()
    if "correct" in r:
        per["correct"] = g["correct"].sum().values
    lines += [md(per.sort_values("first")), ""]

    # 3. per case and arm
    lines += ["## 3. Per case and group", ""]
    agg = {"n": ("answer", "size"), "share_yes": ("answer", lambda x: (x == "yes").mean()),
           "confidence": ("confidence", "mean"), "median_s": ("seconds", "median"),
           "mean_s": ("seconds", "mean"), "median_s_to_answer": ("seconds_to_answer", "median"),
           "answer_changes": ("answer_changes", "sum")}
    if "correct" in r:
        agg["share_correct"] = ("correct", "mean")
    pc = r.groupby(["case_id", "arm"]).agg(**agg).reset_index()
    lines += [md(pc), ""]
    if "docs_json" in r and r["docs_json"].str.strip().ne("").any():
        rows = []
        for _, x in r[r["docs_json"].str.strip().ne("")].iterrows():
            d = json.loads(x["docs_json"]).get("seconds", {})
            rows += [{"case_id": x["case_id"], "arm": x["arm"], "document": k, "seconds": v}
                     for k, v in d.items()]
        if rows:
            dd = pd.DataFrame(rows).groupby(["case_id", "arm", "document"])["seconds"] \
                .agg(["count", "median", "mean"]).reset_index()
            lines += ["### Seconds per document (cases shown as PDFs)", "", md(dd), ""]

    # 4. other pages
    tm = t.get("timings")
    if tm is not None and not tm.empty:
        tm = tm[tm["participant_id"].isin(r["participant_id"])] if pid else tm
        tm = tm.assign(seconds=num(tm["seconds"]))
        lines += ["## 4. Seconds on the other pages", "",
                  md(tm.groupby("step")["seconds"].agg(["count", "median", "mean"])
                     .reset_index()), ""]

    # 5. time model
    lines += ["## 5. log(seconds) on group, case fixed effects", ""]
    real = r[(r["seconds"] > 0) & r["arm"].isin(["ai", "noai"])]
    if real["arm"].nunique() == 2 and real["participant_id"].nunique() >= 4:
        import statsmodels.formula.api as smf
        real = real.assign(treat=(real["arm"] == "ai").astype(int),
                           log_s=np.log(real["seconds"]))
        m = smf.ols("log_s ~ treat + C(case_id)", data=real).fit(
            cov_type="cluster", cov_kwds={"groups": real["participant_id"]})
        b, se = m.params["treat"], m.bse["treat"]
        lines += [f"AI group vs no-AI group: {100 * (np.exp(b) - 1):+.0f}% time per case "
                  f"(log b = {b:.3f}, SE {se:.3f} clustered by person, "
                  f"n = {len(real)} answers, {real['participant_id'].nunique()} people). "
                  "A check that the pipeline runs, not a result.", ""]
    else:
        lines += ["Not enough data yet (needs both groups and at least 4 people).", ""]

    text = "\n".join(lines)
    print(text)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
