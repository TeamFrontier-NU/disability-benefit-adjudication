# Analysis (Group B · WYX)

Pre-registered analysis for the participant study. Code only: data and answer keys stay in the shared drive.

```bash
pip install -r study/analysis/requirements.txt

# test on fake data (any case id can stand in for the stress case)
python study/analysis/fake_data.py
python study/analysis/analyze.py --responses fake_responses.csv --key fake_key.csv --stress-cases C1

# real run, files from the shared drive
python study/analysis/analyze.py --responses <06_data>/responses.csv \
    --key <03_answer_key>/final.csv --min-seconds <pilot threshold> --out results.md
```

`final.csv` columns: `case_id,answer` plus optional `ai_wrong` (1 = deliberately wrong AI suggestion).
The stress-test case IDs come from that file (or `--stress-cases`), never from this repository.

Report sections: sample and exclusions · main models on cases with a correct AI suggestion
(`Correct` and `log(Time)` on `Treat` + case FE, SEs clustered by person) · H2 missed fast tracks ·
H3 wrong fast tracks with the 10-point non-inferiority check (90% CI) · stress-test cases separately ·
all six cases together · descriptives. All sections are always printed.

## Gift-card winners

`winners.py` picks the top 3 scorers by accuracy in each group (complete participants only, ties by a
seeded draw) and writes `winners.csv` with names and emails. Keep that file in the shared drive.

```bash
python study/analysis/winners.py --responses <06_data>/responses.csv --key <03_answer_key>/final.csv \
    --contacts <06_data>/contacts.csv --seed <number fixed before the draw> --out winners.csv
```

Since Nov 18 each participant sees 3 of the 6 cases; both scripts take `--cases-per-person` (default 3).

`*.csv` is gitignored. Do not commit outputs or `results.md` from real data.
