# study/app · participant web app (Group C)

Pages: LYL. Data, assignment, timing: ZXH. Separate from `platform/`.

```bash
pip install -r study/app/requirements.txt
streamlit run study/app/app.py           # http://localhost:8501  (PREVIEW without Secrets)
python study/app/check_content.py        # check A/B content against HANDOFF section 3
```

Flow: language → Welcome (consent, name/email, healthcare/benefits experience) → rule card → T1 → Q1 → [Q2] →
assignment → 6 cases in random order → wrap-up (by group) → thanks. Failing Q1 and Q2 ends at
the thanks page (still in the lottery).

`responses.heard_about_study` stays in the columns (HANDOFF 3.5) but is now always empty: the
Welcome form no longer asks it, nor the major (team decision, Fri 11/13).

## Original document view (both groups)

Under each case (and training case) there is a closed **"View the original document (scanned
PDF)"** panel with an inline viewer and a download button. It is shown to both groups whenever
`content/cases/<id>.<lang>.pdf` exists (so the pages stay identical except the AI panel). Make the
PDFs from the .md files after each content change; `check_content.py` warns when a PDF is older
than its .md:

```bash
pip install playwright markdown && playwright install chromium   # once
python study/app/make_doc_pdfs.py            # study/content/cases + training
```

## Cases as real forms and medical records (PDF documents)

A case can be a set of separate PDFs instead of typed pages: the filled-in SSA forms
(SSA-16, SSA-3368-BK, SSA-827, ...) and the medical records, exactly as a claims examiner
receives them. Put them in a folder named like the case:

```
study/content/cases/C1.en/01_SSA-16.pdf
study/content/cases/C1.en/02_SSA-3368-BK.pdf
study/content/cases/C1.en/03_SSA-827.pdf
study/content/cases/C1.en/04_Lakeshore-Hospital-records.pdf
```

(`study/content/cases/C1/` = one set for every language). When the folder exists, the case page
shows a **Case file** list with one entry per PDF and the chosen PDF full size below it, for
both groups, **in place of** `C1.en.md` (which may then be deleted). The number sets the order
and is hidden; the rest of the file name is the title. Training cases work the same way
(`study/content/training/T1.en/`). The app records how many seconds each document was open
(`docs_json`).

AI findings may name the document: `{"quote": "...", "doc": "04_Lakeshore-Hospital-records.pdf",
"page": 2}` (page within that PDF; the panel shows "Lakeshore Hospital records · page 2").
Without `doc`, `page` counts through all PDFs in order. `check_content.py` checks every quote
against the PDF text (needs `pip install pypdf`).

## What is timed

| Where | Saved in | Columns |
|---|---|---|
| Each case | `responses` | `seconds` (case shown → submit), `seconds_to_answer` (→ first Yes/No click), `seconds_to_confidence` (→ first confidence click), `answer_changes`, `docs_json` (`{"seconds": {document: s}, "order_opened": [...]}`) |
| Welcome, rule card, T1, Q1, Q2, wrap-up | `timings` | `step, seconds, started_at, ended_at, extra_json` (training: the answer, whether it was right, seconds to submit) |

Times are measured on the server from when the page was sent to when the click arrived, so
they include a second or so of network time. The four new `responses` columns come after the
old ones; the header of an existing table is extended automatically on the first write, so
earlier rows (the teacher's test run) keep their meaning with these columns empty.

## Getting the data (any browser, no Python)

Open `<app URL>/?export=1&k=<test_key>` → **Read the data now** → **Download all tables
(.zip)**: one CSV per table. Names and emails are left out unless the box is ticked. Then:

```bash
python study/analysis/quick_check.py study_export_<time>.zip                  # everyone
python study/analysis/quick_check.py study_export_<time>.zip --email <address>  # one person
```

Or with the Secrets on your computer: `python study/app/sheet_admin.py export --out <folder>`.

## Fast, reliable loading

A free Streamlit Community Cloud app **sleeps after about 12 hours without visitors**; the next
visitor then waits 1-3 minutes for it to boot, which looks like an error. Fixes in place:

- `.github/workflows/keep-awake.yml` opens the app in a real browser every 3 hours (and clicks
  "get this app back up" if it slept), using `keep_awake.py`. A red X in the Actions tab = the
  app did not load or was slow. **It needs the app URL in that file to be right.**
- Every push to the deployed branch reboots the app: **do not push to that branch during data
  collection**, and after a push open the app once yourself (or run the workflow by hand).
- No web fonts (a blocked Google Fonts request delayed the first paint), PDFs are read once per
  server process, and the database table check runs only the first time.

Load test from any computer: `python study/app/keep_awake.py <app URL> --runs 3` (prints the
seconds until the first page shows). Before sending the link, open it on 3-4 different
computers and networks (lab, laptop on campus Wi-Fi, a phone on mobile data, a home network)
and check the language page appears within a few seconds.

## Two modes

| Mode | When | What is saved |
|---|---|---|
| **PREVIEW** | No Secrets (local run, or before ZXH adds the Sheet) | Nothing reaches the Sheet. Random group; add `?arm=ai` or `?arm=noai` to see a group. Badge: "PREVIEW". |
| **Study** | `sheet_id` + `gcp_service_account` in Secrets | Every row goes to the Google Sheet as it happens. Group comes from the allocation table. |

## Deploy (Streamlit Community Cloud + Supabase)

Data is stored in **Supabase** (free Postgres, sign in with GitHub), because the team has no Google
account. Google Sheets still works if `sheet_id` + `gcp_service_account` are in Secrets instead.

1. ZXH: create a Supabase project and copy its **Session pooler** connection string
   (step-by-step: `Frontier_Study` project files, `XINHUI-supabase-setup.md`).
2. `python study/app/sheet_admin.py make-secrets --database-url "<URI>" --test-word <word>` writes
   `.streamlit/secrets.toml` at the repository root (gitignored). Its two lines are the Secrets:
   ```toml
   database_url = "postgresql://postgres.<ref>:<password>@<host>.pooler.supabase.com:5432/postgres"
   test_key = "<a word only the team knows>"
   ```
3. ZXH, once: `python study/app/sheet_admin.py setup` creates the table and draws the 200-row
   allocation (blocks of 2). It prints the seed **once**: save it to `Frontier_Study/06_data/seed.txt`.
4. LYL: Streamlit Cloud app from branch `main`, main file `study/app/app.py`; paste the Secrets in
   *Settings → Secrets*. Any push to `main` redeploys; the data stays in Supabase.
5. Export: `python study/app/sheet_admin.py export --out <shared drive>/06_data/export` (CSV per tab).

All data sits in one table `study_rows (tab, id, vals)`; "tab" names below are kept from the
Sheet design. Row-level security is on, so Supabase's public API cannot read it.

## Data tabs (`data.py`)

| Tab | One row per | Columns |
|---|---|---|
| `responses` | submitted case, written at once | HANDOFF 3.5, exactly (no `correct`) |
| `contacts` | participant | `participant_id, name, email, written_at`: lottery only |
| `allocation` | slot (200) | `slot, block, arm`: pre-drawn, never edited |
| `assignments` | person who passed training | `participant_id, arm, case_order, lang, training_attempts, assigned_at`; row n = slot n |
| `participants` | participant | `participant_id, lang, experience, written_at` (experience stored in English) |
| `training` | person who finished the test | `participant_id, attempts, passed` |
| `survey` | wrap-up | `participant_id, arm, lang, answers_json` (`q1`, `q2` … in the order of the `?` lines) |
| `timings` | non-case page | `participant_id, step, seconds, started_at, ended_at, extra_json` |
| `test_assignments` | team test run | as `assignments`; uses no slot |

**Assignment.** The n-th person who passes the test gets allocation row n. The slot is claimed by
appending to `assignments` (Google applies appends one at a time, so two people arriving together
get different rows). Once given, a group never changes.

**Safe writes.** Each write is retried 5 times with backoff. If it still fails, the page says so and
stays where it is; clicking again sends the same row (time is fixed at the first click). In the rare
case of a duplicate row, keep the first row per `participant_id, case_id`.

**Refresh / closed tab.** After Welcome the URL carries `?p=<id>`. Opening that URL again continues
with the same id, group and case order, skipping cases already submitted.

## Team test runs (B's testing, pilot dry runs)

Open `<app URL>/?arm=ai&k=<test_key>` or `?arm=noai&k=<test_key>`. The id starts with `TEST-`,
no allocation slot is used, and the banner says TEST RUN without naming the group. A wrong or
missing `k` is ignored (normal participant). Remove test rows:

```bash
python study/app/sheet_admin.py status        # rows per tab
python study/app/sheet_admin.py clear-test    # delete TEST- rows
python study/app/sheet_admin.py clear-all --yes   # Sun 18:00, before real participants: empty all data tabs
```

Run the clear commands only while nobody is taking the study.

## Languages

English, Spanish and Chinese (`en`, `es`, `zh`). The first page is in English and lists them by
English name with the native name. A language can be chosen once `texts/welcome.<lang>.md`
exists (real or placeholder). Spanish placeholders are in `placeholder/`; `check_content.py`
checks all three languages, including "IA"/"inteligencia artificial" on No-AI pages.

## Where the page text comes from

Only from `study/content/` (formats: `HANDOFF.md` section 3). While a file is missing, the copy in
`study/app/placeholder/` (same layout) is used and the page shows a yellow PLACEHOLDER badge.
Delivering the real file is all it takes; no code change.

Extra files the pages need, beyond the HANDOFF list (proposed, examples in `placeholder/`):

| File | Owner (proposed) | What |
|---|---|---|
| `content/texts/ai_notice.<lang>.md` | B | Top of the AI panel: "the AI's suggestion may be wrong; you decide" |
| `content/texts/ui.yaml` | B | Buttons and form labels in both languages (`check_content.py` reports missing labels) |
| `wrapup_*` question lines | B (WYX) | `?scale: question` (1–5), `?text: question`, `?choice: question \| A \| B` |
| `training/training_key.yaml` | A (CZY) | `T1: {answer: "yes", explanation: {en: ..., zh: ...}}` (quote "yes"/"no") |

## Offline testing

`STUDY_LOCAL_SHEET=/tmp/study_sheet` makes `data.py` use local JSON files instead of Google
(`local_sheet.py`); `STUDY_TEST_KEY=...` sets the test key. Run `sheet_admin.py setup` first.

## Files

| File | What |
|---|---|
| `app.py` | Pages (LYL) |
| `content.py` | Reads `study/content/` with placeholder fallback |
| `data.py` | Google Sheet writes and reads (ZXH) |
| `assign.py` | Group assignment, case order, timer, resume (ZXH) |
| `backend_stub.py` | PREVIEW backend, same interface, saves nothing to the Sheet |
| `sheet_admin.py` | Sheet setup, allocation draw, status, clean-up |
| `make_doc_pdfs.py` | Builds the scanned-style original PDFs from the case/training .md files |
| `local_sheet.py` | Offline stand-in for the Sheet (tests only) |
| `keep_awake.py` | Opens the live app in a browser, wakes it, times the load (used by the keep-awake workflow) |
| `../analysis/quick_check.py` | Quick report on a data export: per person, per case, seconds |
| `check_content.py` | Content checks for groups A and B |
| `../analysis/fake_data.py` | 30 × 6 fake `responses` rows + a random fake key, for WYX |
