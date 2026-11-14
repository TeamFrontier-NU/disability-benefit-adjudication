"""Pre-registered analysis for the Frontier participant study (Group B, WYX).

    pip install -r study/analysis/requirements.txt
    python study/analysis/fake_data.py                      # fake data, for testing only
    python study/analysis/analyze.py --responses fake_responses.csv --key fake_key.csv \
        --stress-cases C1                                    # fake run (any case id works)

Real run (files come from the shared drive, never from this repository):

    python study/analysis/analyze.py \
        --responses <06_data>/responses.csv --key <03_answer_key>/final.csv \
        --min-seconds <threshold set after the pilot> --out results.md

Inputs
  responses.csv  the `responses` table export (HANDOFF.md 3.5 columns).
  final.csv      the expert answer key: `case_id,answer` (yes/no). An optional column
                 `ai_wrong` (1 = the AI suggestion on this case is deliberately wrong) marks
                 the stress-test cases. The case IDs are read from that file, or given with
                 --stress-cases; they are never written into this script.

What it reports (DESIGN.md "Analysis", updated for A-group handoff v4)
  1. Sample: participants by arm, exclusions.
  2. Main analysis, cases with a correct AI suggestion only:
       Correct_ij   = a + b*Treat_i + case FE + e_ij       (linear probability model)
       log(Time_ij) = a + b*Treat_i + case FE + e_ij
     Standard errors clustered by participant.
  3. H2 missed fast tracks (key = yes, answered no) and H3 wrong fast tracks (key = no,
     answered yes) by arm. H3 is a non-inferiority test: the AI arm passes if the upper
     end of the one-sided 95% CI (= two-sided 90% CI) of the difference is below +10 pp.
  4. Stress-test cases (deliberately wrong AI suggestion), reported separately: share
     correct by arm, difference, CI, n. Do not compare these with other cases to estimate
     "the effect of a wrong suggestion": the cases themselves differ.
  5. All six cases together (the same two regressions), interpreted as performance on this
     fixed case set with these pre-recorded suggestions.
Nothing is chosen after seeing the data: all of the above is always printed.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

MARGIN = 0.10  # H3 non-inferiority margin (10 percentage points)
N_CASES = 6


def load(responses: str, key: str, stress_arg: str | None, min_seconds: float):
    r = pd.read_csv(responses, dtype={"participant_id": str})
    k = pd.read_csv(key, dtype=str)
    k.columns = [c.strip().lower() for c in k.columns]
    k["case_id"] = k["case_id"].str.strip()
    k["answer"] = k["answer"].str.strip().str.lower()
    if not set(k["answer"]) <= {"yes", "no"}:
        sys.exit("key: answer must be yes or no")

    if stress_arg:
        stress = {c.strip() for c in stress_arg.split(",") if c.strip()}
    elif "ai_wrong" in k.columns:
        stress = set(k.loc[k["ai_wrong"].astype(str).str.strip().isin(["1", "true", "yes"]),
                           "case_id"])
    else:
        stress = set()
    unknown = stress - set(k["case_id"])
    if unknown:
        sys.exit(f"stress cases not in key: {sorted(unknown)}")

    log = []
    n0 = r["participant_id"].nunique()
    r = r[~r["participant_id"].str.upper().str.startswith("TEST")]
    log.append(f"team test runs dropped: {n0 - r['participant_id'].nunique()} participant(s)")

    r = r.drop_duplicates(["participant_id", "case_id"], keep="first")
    done = r.groupby("participant_id")["case_id"].nunique()
    incomplete = done[done < N_CASES].index
    r = r[~r["participant_id"].isin(incomplete)]
    log.append(f"incomplete (fewer than {N_CASES} cases): {len(incomplete)} participant(s)")

    if min_seconds > 0:
        fast = r["seconds"] < min_seconds
        log.append(f"case answers faster than {min_seconds:g}s dropped: {int(fast.sum())} row(s)")
        r = r[~fast]
    else:
        log.append("too-fast threshold: not set yet (set after the pilot, --min-seconds)")
    # failed-training participants never reach the cases, so they have no rows here.

    r = r.merge(k[["case_id", "answer"]].rename(columns={"answer": "key"}), on="case_id",
                how="left", validate="many_to_one")
    if r["key"].isna().any():
        sys.exit(f"cases missing from key: {sorted(r.loc[r['key'].isna(), 'case_id'].unique())}")
    r["answer"] = r["answer"].str.strip().str.lower()
    r["correct"] = (r["answer"] == r["key"]).astype(int)
    r["treat"] = (r["arm"] == "ai").astype(int)
    r["log_time"] = np.log(r["seconds"].clip(lower=0.1))
    r["stress"] = r["case_id"].isin(stress)
    return r, sorted(stress), log


def reg(df: pd.DataFrame, y: str, level: float = 0.95):
    """OLS of y on treat + case FE, SEs clustered by participant."""
    if df["participant_id"].nunique() < 2 or df["treat"].nunique() < 2:
        return None
    fe = " + C(case_id)" if df["case_id"].nunique() > 1 else ""
    m = smf.ols(f"{y} ~ treat{fe}", data=df).fit(
        cov_type="cluster", cov_kwds={"groups": pd.factorize(df["participant_id"])[0]})
    lo, hi = m.conf_int(alpha=1 - level).loc["treat"]
    return {"b": m.params["treat"], "se": m.bse["treat"], "p": m.pvalues["treat"],
            "lo": lo, "hi": hi, "n": int(m.nobs), "people": df["participant_id"].nunique()}


def fmt(res, pct=False, label="95% CI"):
    if res is None:
        return "not estimable (need both arms)"
    s = 100 if pct else 1
    u = " pp" if pct else ""
    return (f"b = {res['b']*s:+.2f}{u} (SE {res['se']*s:.2f}), {label} [{res['lo']*s:+.2f}, "
            f"{res['hi']*s:+.2f}]{u}, p = {res['p']:.3f}; {res['n']} answers, {res['people']} people")


def by_arm(df: pd.DataFrame, col: str) -> str:
    g = df.groupby("arm")[col].agg(["mean", "count"])
    return "; ".join(f"{a}: {row['mean']*100:.1f}% (n = {int(row['count'])})"
                     for a, row in g.iterrows())


def report(r: pd.DataFrame, stress: list[str], log: list[str]) -> str:
    out = ["# Frontier study: pre-registered analysis", ""]
    ppl = r.groupby("arm")["participant_id"].nunique()
    out += ["## 1. Sample", "",
            "Participants analysed: " + ", ".join(f"{a} = {n}" for a, n in ppl.items()),
            "", *[f"- {x}" for x in log],
            f"- stress-test cases (deliberately wrong AI suggestion): {', '.join(stress) or 'none given'}",
            ""]

    main = r[~r["stress"]]
    out += ["## 2. Main analysis (cases with a correct AI suggestion)", "",
            "Linear probability model and log-time model, case fixed effects, SEs clustered by person.", "",
            f"- Correct: {fmt(reg(main, 'correct'), pct=True)}",
            f"- log(Time): {fmt(reg(main, 'log_time'))}"]
    t = reg(main, "log_time")
    if t:
        out.append(f"  - i.e. AI arm time is about {(np.exp(t['b'])-1)*100:+.1f}% vs No-AI (H1: negative)")
    out.append(f"- Mean seconds per case: " + "; ".join(
        f"{a}: {v:.1f}" for a, v in main.groupby("arm")["seconds"].mean().items()))
    out.append(f"- Share correct: {by_arm(main, 'correct')}")
    out.append("")

    yes, no = main[main["key"] == "yes"].copy(), main[main["key"] == "no"].copy()
    yes["missed"] = (yes["answer"] == "no").astype(int)
    no["wrong_ft"] = (no["answer"] == "yes").astype(int)
    out += ["## 3. Error types (main cases)", "",
            "**H2, missed fast tracks** (key = yes, answered no; lower is better)", "",
            f"- {by_arm(yes, 'missed') if len(yes) else 'no yes-cases in main set'}",
            f"- AI − No-AI: {fmt(reg(yes, 'missed'), pct=True) if len(yes) else '—'}", "",
            "**H3, wrong fast tracks** (key = no, answered yes; must not rise by 10 pp or more)", ""]
    if len(no):
        h3 = reg(no, "wrong_ft", level=0.90)
        out += [f"- {by_arm(no, 'wrong_ft')}",
                f"- AI − No-AI: {fmt(h3, pct=True, label='90% CI')}"]
        if h3:
            ok = h3["hi"] < MARGIN
            out.append(f"- Non-inferiority (upper bound {h3['hi']*100:+.1f} pp vs margin "
                       f"+{MARGIN*100:.0f} pp): {'MET' if ok else 'NOT MET'}")
    out.append("")

    out += ["## 4. Stress-test cases (deliberately wrong AI suggestion), reported separately", ""]
    if not stress:
        out.append("- none given (use the `ai_wrong` column in the key or --stress-cases)")
    for c in stress:
        d = r[r["case_id"] == c]
        res = reg(d, "correct")
        key = d["key"].iloc[0] if len(d) else "?"
        out += [f"**{c}** (key = {key})", "",
                f"- Share correct: {by_arm(d, 'correct')}",
                f"- AI − No-AI: {fmt(res, pct=True)}",
                f"- In the AI arm, an answer that matches the wrong suggestion shows agreement "
                f"with it, not why the person chose it.", ""]

    out += ["## 5. All six cases together", "",
            "Performance on this fixed case set with these pre-recorded suggestions.", "",
            f"- Correct: {fmt(reg(r, 'correct'), pct=True)}",
            f"- log(Time): {fmt(reg(r, 'log_time'))}",
            f"- Share correct: {by_arm(r, 'correct')}", ""]

    out += ["## 6. Descriptive (not pre-registered tests)", "",
            "Share correct by case and arm:", "",
            r.pivot_table(index="case_id", columns="arm", values="correct", aggfunc="mean")
             .mul(100).round(1).to_markdown(), "",
            "Participants by language and arm:", "",
            r.drop_duplicates("participant_id").pivot_table(
                index="lang", columns="arm", values="participant_id", aggfunc="count",
                fill_value=0).to_markdown(), "",
            "Feasibility pilot: read directions and intervals, not strong claims."]
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--responses", required=True)
    ap.add_argument("--key", required=True)
    ap.add_argument("--stress-cases", help="comma-separated case ids; overrides the key's ai_wrong column")
    ap.add_argument("--min-seconds", type=float, default=0, help="drop case answers faster than this")
    ap.add_argument("--out", help="also write the report to this markdown file")
    a = ap.parse_args()
    r, stress, log = load(a.responses, a.key, a.stress_cases, a.min_seconds)
    text = report(r, stress, log)
    print(text)
    if a.out:
        Path(a.out).write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
