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

## Two modes

| Mode | When | What is saved |
|---|---|---|
| **PREVIEW** | No Secrets (local run, or before ZXH adds the Sheet) | Nothing reaches the Sheet. Random group; add `?arm=ai` or `?arm=noai` to see a group. Badge: "PREVIEW". |
| **Study** | `sheet_id` + `gcp_service_account` in Secrets | Every row goes to the Google Sheet as it happens. Group comes from the allocation table. |

## Deploy (Streamlit Community Cloud)

1. ZXH: create an empty Google Sheet and a Google Cloud service account (Sheets API + Drive API
   enabled); share the Sheet with the service account's email as **Editor**.
2. Put the Secrets in **two places only**: the app's *Settings → Secrets* on Streamlit Cloud, and,
   for running `sheet_admin.py`, `.streamlit/secrets.toml` at the repository root on your own
   computer (gitignored). Never in a chat, a Project or any other file.
   ```toml
   sheet_id = "<the long id in the Sheet URL>"
   test_key = "<a word only the team knows>"
   [gcp_service_account]
   type = "service_account"
   project_id = "..."
   private_key_id = "..."
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "...@....iam.gserviceaccount.com"
   client_id = "..."
   token_uri = "https://oauth2.googleapis.com/token"
   ```
3. ZXH, once: `python study/app/sheet_admin.py setup`. This creates the tabs and draws the
   200-row allocation (blocks of 2). It prints the random seed **once**: save it to
   `Frontier_Study/06_data/seed.txt`. Do not commit it.
4. LYL: *New app* → repo `TeamFrontier-NU/disability-benefit-adjudication`, branch `main`,
   main file `study/app/app.py`. Paste the Secrets. Any push to `main` redeploys; the Sheet keeps
   its data across redeploys.

## Sheet tabs (`data.py`)

| Tab | One row per | Columns |
|---|---|---|
| `responses` | submitted case, written at once | HANDOFF 3.5, exactly (no `correct`) |
| `contacts` | participant | `participant_id, name, email, written_at`: lottery only |
| `allocation` | slot (200) | `slot, block, arm`: pre-drawn, never edited |
| `assignments` | person who passed training | `participant_id, arm, case_order, lang, training_attempts, assigned_at`; row n = slot n |
| `participants` | participant | `participant_id, lang, experience, written_at` (experience stored in English) |
| `training` | person who finished the test | `participant_id, attempts, passed` |
| `survey` | wrap-up | `participant_id, arm, lang, answers_json` (`q1`, `q2` … in the order of the `?` lines) |
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
| `check_content.py` | Content checks for groups A and B |
| `../analysis/fake_data.py` | 30 × 6 fake `responses` rows + a random fake key, for WYX |
