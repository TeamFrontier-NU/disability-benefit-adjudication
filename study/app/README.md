# study/app · participant web app (Group C)

Pages: LYL. Data, assignment, timing: ZXH. Separate from `platform/`.

```bash
pip install -r study/app/requirements.txt
streamlit run study/app/app.py           # http://localhost:8501
python study/app/check_content.py        # check A/B content against HANDOFF section 3
```

Deploy (Streamlit Community Cloud): repo `TeamFrontier-NU/disability-benefit-adjudication`, branch `main`,
main file `study/app/app.py`. Keys go in the app's **Secrets**, never in the repo.

## Where the page text comes from

Only from `study/content/` (formats: `HANDOFF.md` section 3). While a file is missing, the copy in
`study/app/placeholder/` (same layout) is used and the page shows a yellow PLACEHOLDER badge.
Delivering the real file is all it takes; no code change.

Extra files the pages need, beyond the HANDOFF list (proposed, examples in `placeholder/`):

| File | Owner (proposed) | What |
|---|---|---|
| `content/texts/ai_notice.<lang>.md` | B | Top of the AI panel: "the AI's suggestion may be wrong; you decide" |
| `content/texts/ui.yaml` | B | Buttons and form labels in both languages |
| `wrapup_*` question lines | B (WYX) | `?scale: question` (1–5), `?text: question`, `?choice: question \| A \| B` |
| `training/training_key.yaml` | A (CZY) | `T1: {answer: "yes", explanation: {en: ..., zh: ...}}` (quote "yes"/"no") |

## Interface for ZXH (`data.py`, `assign.py`)

`app.py` imports `assign` and `data` from this folder; until they exist it uses `backend_stub.py`
(PREVIEW banner, nothing saved to the Sheet, `?arm=treat|control` previews a group).
Same names and signatures as the stub:

```python
# assign.py
new_participant_id() -> str
assign_arm(participant_id) -> "ai" | "noai"      # called once, when the test is passed
case_order(participant_id) -> list[str]          # C1..C6 shuffled
start_timer() -> token                           # when a case is first shown
stop_timer(token) -> (seconds, started_at, submitted_at)
# data.py
write_response(row: dict)                        # keys = HANDOFF 3.5 columns, once per case
write_contact(participant_id, name, email)       # lottery only
write_participant(participant_id, lang, background: dict)   # major, experience  (table TBD)
write_survey(participant_id, arm, answers: dict)            # wrap-up answers    (table TBD)
```
