# Blind check: guide for checkers

Team 06 · Frontier · prepared Nov 6, 2026. This fixes issue I-4: the answer keys were written by Claude, and nobody on the team has checked them yet.

## What you are doing

Each of the 50 calibration and test cases goes to two of you. You decide each case the way a DDS examiner would at the initial level, using only the case file. The script then compares your decisions with the answer key and with each other.

| Checker | Cases | About how long (5 min a case) |
| --- | --- | --- |
| Xinhui Zong | 16 | 1 h 20 |
| Yanqi Wu | 16 | 1 h 20 |
| Yihang Ye | 16 | 1 h 20 |
| Yiling Long | 16 | 1 h 20 |
| Yixuan Wen | 20 | 1 h 40 |
| Zhiying Cui | 16 | 1 h 20 |

**Finish by:** before anyone runs the test set (BUILD-PLAN Step 7). If an answer key changes after the AI's test results have been seen, the test is no longer blind.

## Rules for staying blind

- Open only your own folder: `blind-check/<Your_Name>/`.
- Don't open `data/simulated/`, any `answer_key.json`, the panel, `results/`, or anyone else's sheet.
- Don't discuss a case with anyone until the scores are run. Disagreements are what we're measuring.
- If you wrote or edited a case, say so in `notes` and skip it.

## How to decide each case

Read the whole file, then pick one:

- **allow**: the file as it stands shows the claimant is disabled under SSA's rules.
- **deny**: the file as it stands shows the claimant is not disabled.
- **need_more_evidence**: you can't decide either way without records that aren't in the file.

Points to keep in mind (these are SSA's rules, not the tool's):

1. **Step 1, work.** If the claimant works with earnings above the substantial gainful activity (SGA) amount printed in the file, it's a denial at Step 1.
2. **Medical evidence.** An impairment has to be shown by an acceptable medical source (a doctor, psychologist or similar). What the claimant, a friend or a helper says counts as a description of symptoms, not as proof of the impairment.
3. **Duration.** The impairment must have lasted, or be expected to last, at least 12 months, or be expected to result in death.
4. **Listings** used in these cases: 11.08 (spinal cord disorders), 13.14 (lung cancer), 6.03 (chronic kidney disease on dialysis), 12.03 / 12.04 (mental disorders). Look up the exact criteria in SSA's Blue Book (ssa.gov/disability/professionals/bluebook) if you need to.
5. **The medical-vocational grid** (20 CFR Part 404, Subpart P, Appendix 2) for people who don't meet a Listing: age, education, past work and the most they can still do (sedentary, light and so on).

You don't need to know where the tool would route the case. Decide eligibility only.

## Filling in `decisions.csv`

| Column | What to write |
| --- | --- |
| `decision` | `allow`, `deny` or `need_more_evidence` (exactly these words) |
| `basis` | the rule, for example `meets 11.08A`, `grid 201.09`, `not severe at Step 2`, `SGA at Step 1`, `no 12-month duration` |
| `minutes` | how long the case took you |
| `notes` | anything odd: a typo that changes the meaning, a borderline call, "I wrote this case" |

Keep the file as a CSV (in Excel: Save As, then "CSV UTF-8"). Don't add or rename columns.

## When everyone is done

One person runs, from `03 Platform`:

```bash
python scripts/blind_check.py score --out blind-check
```

This writes `blind-check/summary.md` with agreement rates, Cohen's kappa and the list of disagreements. Then meet once to go through every disagreement and either rewrite the case or label it "borderline" (it is then reported separately). Only after that meeting, run the same command with `--write` to record the checks in the answer keys.

Warning sign from the proposal (risk R3): if checkers disagree with the answer key on more than 20% of cases, the keys need rework before the test run.
