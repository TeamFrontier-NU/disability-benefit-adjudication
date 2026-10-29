# 03 Platform: Fast-Track Screening Prototype

Team 06 · Frontier · started 2026-10-24 (Week 6). Code and simulated data written by Claude (Opus 5.5) for the team to review and extend. Built to the spec in `02 Project Revision/design-final_v1_2026-10-24.md`.

## What it does

```
Import files ─► AI sorting ─────────────────────► Examiner review ─► Final decision
(connectors)    Read → Verify → Score → Route      (panel)            (logged, timed)
                fast track  or  human queue
                (the AI never denies)
```

1. **Import.** Brings a case into the platform. Three connectors share one case format:
   - `LocalFolderConnector`: our simulated cases (works now)
   - `FileImport`: upload existing PDFs or text files, including filled SSA forms, and say who wrote each one (works now)
   - `SSAeFolderConnector`: link to SSA's electronic claim folder (**planned next step**; needs a partner, a data-use agreement and a test environment)
2. **AI sorting.** The reader fills the fixed checklist with a quote and page for every item. Code then checks each quote, applies the source rule, runs the rule table (11.08, 13.14, 6.03, grid; mental Listings always go to a human) and routes the case.
3. **Examiner review.** The panel shows the file with quotes highlighted by source (green = medical source, yellow = claimant form, red = third party), the rule check, flags, the checklist and the evidence for approval.
4. **Final decision.** The examiner records allow, deny or need more evidence. A denial needs a written basis. Each decision is timed and logged, which gives us the speed numbers.

**Human-only mode** hides the AI output. Running the same cases in both modes gives the three-way comparison from the project topic: human only, AI only (the routing), and human + AI.

## How to run it (on the team computer)

```bash
cd "03 Platform"
pip install -r requirements.txt
streamlit run app.py          # opens the panel in a browser
```

- **Offline keyword baseline** works with no key. Use it to try the panel.
- **Claude API (Sonnet 5.5)** is the real reader. It needs an API key (`export ANTHROPIC_API_KEY=...`, or `ant auth login`). Estimated cost is about 4–6¢ per simulated case, so the 10 calibration cases are about $0.50 and the 40 test cases about $2.
- Batch runs for the evaluation: `python scripts/run_batch.py --set calibration --reader claude --k 1`. Results are saved in `results/` for the AI log.
- The simulated cases are in `simulated-cases_seed425_v2.zip`; unzip it into `data/` to read them. If `data/simulated/` is missing, the panel rebuilds the same 61 cases on first start.
- New simulated cases: `python -m fasttrack.simulate --out data/simulated --seed 425`. This overwrites the simulated cases, so change the seed to make a different set.

## Simulated data (`data/simulated/`)

No government data is used. Each case is generated from a profile whose correct answer is known, then written as short documents that follow the real forms (SSA-16/8000 extract, SSA-3368 extract, medical records, optional SSA-3373 and third-party letters). The answer key is in `answer_key.json`, which the reader never sees.

| Set | Cases | Eligible | Correct route = fast track |
| --- | --- | --- | --- |
| demo | 3 (Joe, Peter, Joe still working) | 1 | 1 |
| calibration | 10 | 7 | 6 |
| test | 40 | 15 | 13 |
| stress | 8 (S1–S8 from follow-up 02) | 3 | 1 (the honest control) |

Test mix as in the design: about 37% eligible; above-SGA cases moved to the stress set (design D2). Best possible fast-track rate on the test set: 13/40 = 32.5%.

## Case wording: v1 and v2 (updated 2026-10-29)

- **v1 (demo set only):** one fixed template sentence per finding. Easy to read in a presentation.
- **v2 (calibration, test, stress):** each medical record is rewritten with different wordings for the same finding ("complete paraplegia", "flaccid paralysis of both legs", "BLE"), mixed date formats, and routine content around the key lines (vitals, history, normal findings, a few typos). Three near-miss cases were added to the test set and one to calibration: a spinal cord injury under 3 months old, temporary dialysis, and sedentary limits at age 47. The test mix is unchanged: 15 eligible, 25 not, 13 on a fast-track path.

## Results so far (offline keyword baseline, not the real reader)

| Check | v1 wording (Oct 24) | v2 wording (Oct 29) |
| --- | --- | --- |
| Test cases routed as the answer key expects | 40/40 | 27/40 (it fast-tracks nothing) |
| Gaming cases wrongly fast-tracked (stress set) | 0 of 7 | 0 of 7 |
| Honest control sent to a human by mistake | 0 of 1 | 1 of 1 |
| Denials made by the AI | 0 | 0 |

The v1 score was circular: the baseline was written alongside the templates. On v2 it can't find the findings any more. That's what we want, because it shows the cases now test reading, not pattern-matching. **None of these numbers are evidence for the claim.** The real test is the Claude reader on the calibration set, then the locked test set. Use the offline mode only on the demo set, as a backup if the network fails during a presentation. The "safeguards off" demo (gaming cases slipping onto the fast track) now needs the Claude reader.

## Known limits and next steps

1. **Run the Claude reader on the 10 calibration cases** and set k (1 or 2). Then lock and post on OSF before touching the test set.
2. **Wording:** done for v2 (Oct 29). Still to do: teammates rewrite 2 cases each by hand (BUILD-PLAN step 2).
3. **Teammate blind check of answer keys** (README design decision 6 and R3 in the pitch).
4. **Examiner timing** needs people: volunteers review cases in both modes so we can compare speed and accuracy.
5. **Government connector**: design the `SSAeFolderConnector` interface in more detail for the final presentation; no access is assumed.

## Files

| Path | What |
| --- | --- |
| `app.py` | Examiner panel (Streamlit) |
| `fasttrack/intake.py` | Import connectors |
| `fasttrack/reader.py` | Claude reader and keyword baseline |
| `fasttrack/pipeline.py` | Quote check, source rule, rule table, flags, routing |
| `fasttrack/fields.py` | The fixed checklist |
| `fasttrack/metrics.py` | Measures with Wilson CIs, decision log, human-only vs. human + AI |
| `fasttrack/simulate.py` | Simulated case generator |
| `scripts/run_batch.py` | Batch evaluation |
| `data/simulated/` | 61 generated cases |
| `data/imported/` | Cases created from uploaded files |
