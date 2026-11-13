# study/ · Examiner study (AI-assisted vs. unassisted)

Everything for the participant study lives here. The existing Frontier platform in `platform/` is **not** changed by this work.

## Start here

| File | What it is | Who needs it |
|---|---|---|
| `GROUP_PROMPTS.md` | Per-group setup for Claude Projects + Claude Code on the remote machine, and how to use the $100 API credits | Everyone |
| `LAB_PROMPT.md` | The prompt to paste into Claude on a lab computer, with setup steps | Everyone, at the start of each lab session |
| `HANDOFF.md` | Master handoff checklist: who owns what, folder layout, file formats, lab schedule, 16 handoff points, final checklist | Everyone |
| `DESIGN.md` | Short English spec of the study design (cases, randomization, flow, analysis) | Everyone; the full Chinese design is linked inside |
| `tasks/A_CZY.md` | CZY: rule card, glossary, training cases, Chinese versions of cases and AI outputs | CZY |
| `tasks/A_YYH.md` | YYH: 6 English cases, draft answer key, English AI outputs | YYH |
| `tasks/B_WYQ.md` | WYQ: welcome, consent and lottery text; instructor emails; expert judgment; pilot | WYQ |
| `tasks/B_WYX.md` | WYX: wrap-up survey, debrief, pre-registration, analysis script, QA; expert judgment | WYX |
| `tasks/C_LYL.md` | LYL: web pages and deployment; final email to the instructor | LYL |
| `tasks/C_ZXH.md` | ZXH: Google Sheet data layer, random assignment, timing, fake data; expert judgment | ZXH |

## Folders

| Folder | Contents | Owner |
|---|---|---|
| `content/texts/` | Page text as `<key>.en.md` / `<key>.zh.md`, plus `glossary.yaml` | B (rule card and glossary: A) |
| `content/training/` | Training case T1, test cases Q1 and Q2, `training_key.yaml` | A |
| `content/cases/` | The 6 study cases `C1`–`C6`, English and Chinese. No answers inside. | A |
| `content/ai/` | Pre-recorded AI panel output per case and language (JSON) | A |
| `app/` | The study web app (Streamlit) | C |
| `analysis/` | Analysis script and fake-data generator. No real data. | B, ZXH |

## Never commit (this repository is public)

Answer keys, expert judgments, participant data, the allocation table, random seeds, API keys or service-account keys. These go in the shared drive `Frontier_Study/` or in Streamlit Secrets. `study/.gitignore` blocks the common file names, but check before you push.
