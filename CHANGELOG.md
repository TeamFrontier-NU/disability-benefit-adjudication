# Changelog

## 2026-11-05 (late): the app becomes the presentation

UI only. The locked reader, prompt, checklist, rules, k and model are unchanged; the test set is still never listed, run or shown.

- Navigation regrouped into **Presentation** (1 · Where it fits → 6 · Decisions and next steps, in the halfway rubric's order) and **Backup** (Questions, Results, About).
- New pages: `views/standing.py` (works / not yet / changed since the pitch, and spend against the $200 cap with the largest line), `views/evaluation.py` (claim, threshold, counterfactual, assignment, how and on whom, sample size and power), `views/next_steps.py` (two open decisions, next steps, where it could go), `views/qa.py` (expected questions).
- `frontier_ui/talk.py`: the 8-minute run of show (six presenters, times, cues; shown under each page title and in a collapsed sidebar box), the Claude Pro budget line, and the API spend estimate from saved runs plus the Replay recording.
- Overview corrected: QDD/CAL stays as the early screen; the tool is a second screen on the medical records of claims not yet picked; the 15% target is among claims the tool screens.

## 2026-11-06: "New case (live)" page

UI only. **Not changed:** the reader prompt and schema, the checklist, the rules and routing, k = 1 and the model. The test set was not run or shown.

Added
- `platform/views/new_case.py` (in the navigation as **New case (live)**): enter a brand-new case in three boxes (application and claimant forms; medical records with how it arrived, provider, doctor, credential and date; other letters or statements), each also taking a PDF/TXT upload, plus up to 6 extra documents with their own source type, arrival, provider and date. Claim type, filing date, title, and the SSA-3368 provider list (prefilled from the medical-record providers, editable). The Run button works only in Live mode. Shows the same steps, route banner, rule cards, flags and document viewer as the Case explorer, plus seconds, tokens and estimated cost, and a safeguards-off comparison from the same reader output (no second call).
- `platform/frontier_ui/new_case.py`: builds the case with the existing `FileImport` in a session-only temp folder (`case_set = "imported"`, never in `data/simulated`). Caps a case at 30 pages and 150,000 characters. If there are no pages or the reader cannot start, the case goes to the human queue through `run_case`'s own fail-safe.
- `platform/scripts/check_new_case.py`: tests the page through Streamlit AppTest (Joe pasted into the boxes, family letter only, fake key, nothing entered, size cap, Replay lock, every page loads with no key). `--offline` skips the two paid calls.
- `platform/REHEARSAL-CASES.txt`: two practice cases in plain paragraphs (one should fast-track, one should not).

## 2026-11-05 (evening): presentation app for the halfway demo

UI, packaging and deployment only. **Not changed:** the reader prompt and schema (`SYSTEM`, `SCHEMA` in `fasttrack/reader.py`), the checklist (`fasttrack/fields.py`), the rules and routing (`fasttrack/pipeline.py`), k = 1 and the model (Gemini 3.7 Flash). The test set was not run, recorded or shown.

Added
- `platform/Frontier.py`: new entry point with five pages (`views/`): Overview, Case explorer, Safeguards, Results, About. Colours navy / blue (fast track) / orange (human queue), always with a word as well.
- `platform/frontier_ui/replay.py`: **Replay mode** (recorded Gemini output, no key or cost), the **Live mode** passcode check (`LIVE_PASSCODE` and `GOOGLE_API_KEY` from Streamlit secrets or the environment), and three pre-recorded attacks on Peter's claim (hidden instruction, fake MRI handed in by the claimant, keyword stuffing).
- `platform/frontier_ui/common.py`: shared display blocks (route banner, Read → Verify → Rules → Route steps, rule cards with links to the quoted page, source-coloured document viewer, instruction text in a red box).
- `platform/scripts/build_reader_cache.py`: records the locked reader's output once for Replay mode. Refuses test cases.
- `platform/Start-Frontier.command` (Mac/Linux) and `platform/Start-Frontier.bat` (Windows): double-click launchers that set up a private environment on first run.
- Root `.streamlit/config.toml` (theme, for Streamlit Cloud); theme added to `platform/.streamlit/config.toml`.
- `platform/results/*.json`: the saved Nov 5 runs (demo, calibration, stress), so the Results page has data.
- `README.md` rewritten for the app; this changelog.

Changed
- `platform/app.py` (original panel): `use_container_width=True` → `width="stretch"`; the Flags column is now text (fixes the Arrow mixed-type error). Nothing else.
- `platform/requirements.txt`: `streamlit>=1.50` (for `width="stretch"` and `st.navigation`); adds `pandas` and `altair` explicitly.
- `.gitignore`: virtual environments, zips, AI logs, backups, secrets, the decision log, imported cases, test answer keys and test results.

Removed from the repository (kept by the team locally)
- `platform/data/simulated/test-*/answer_key.json` (40 files), and the test entries in `platform/data/simulated/index.json`. Note: earlier commits on `main` still contain them.

Known gaps
- Replay mode is empty until the team runs `build_reader_cache.py` once with the key (Nov 5 batch runs saved only summaries, not the reader's full output).
- No scanned-record cases or results exist yet, so the Results page says so instead of showing them.
- On the web link, examiner-study decisions are lost when the app restarts; run the timing study on a local copy.
