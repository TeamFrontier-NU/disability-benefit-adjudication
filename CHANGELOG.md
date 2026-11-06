# Changelog

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
