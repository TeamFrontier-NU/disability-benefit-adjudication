# Group prompts · Claude Max on the remote machine

Each group uses two Claude tools, for different jobs:

| Tool | Use it for | Where |
|---|---|---|
| **Claude Project** (one shared Project, one thread per group) | Thinking and writing: drafting cases, page text, survey wording, reviewing each other's work | Browser on the remote machine, team Claude Max account |
| **Claude Code** | Anything that touches files or the repository: writing content files in the right format, code, checks, git commits | Terminal on the remote machine, in the repository folder, logged in with the same Max account |

Rule of thumb: **draft in the Project, save to the repo with Claude Code.** Both are covered by the Max subscription and do not spend API credits.

---

## One-time setup (any member, about 10 minutes)

We use **one shared Claude Project** ("Disability Benefit Adjudication") with **one thread per group**, plus Claude Code on the remote machine. Threads move at different speeds, so **GitHub is the single source of truth** and `study/STATUS.md` is the shared progress board.

1. **Repository on the remote machine**
   ```bash
   git clone https://github.com/TeamFrontier-NU/disability-benefit-adjudication.git   # first time only
   cd disability-benefit-adjudication && git pull
   claude          # log in with the team Max account when asked
   ```
2. **Link GitHub to the Project**: in the Project, add the repository `TeamFrontier-NU/disability-benefit-adjudication` as a source (GitHub connector), so every thread can read the latest `study/` files. Re-sync it at the start of each session, because the Project's copy does not update by itself.
3. **Project knowledge**: only public files: `study/README.md`, `study/DESIGN.md`, `study/HANDOFF.md`, `study/STATUS.md`, `study/tasks/*`. **Never add the case blueprint, answers, AI outputs or expert judgments to the Project**: every member can open every thread and file in it, and three members are the expert group.
4. **Threads**: create three threads, named `A · content`, `B · text & checks`, `C · web & data`. Paste the group's "Thread instructions" below as the first message.
5. **Experts (WYQ, WYX, ZXH)**: do not open the `A · content` thread until your expert judgment is submitted.

## How threads stay in sync

Every session, in every thread:

1. **Start**: `git pull`, then read `study/STATUS.md` to see what the other groups have delivered.
2. **Work** only in your own folders (they do not overlap, so pushes rarely conflict).
3. **End**: update your rows in `study/STATUS.md` (status, who, time, one-line note), then `git add study/ && git commit && git pull --rebase && git push`.
4. **Post** the handoff message in the group chat, so the next group knows to `git pull`.

If `git pull --rebase` reports a conflict in `STATUS.md`, keep both groups' rows and push again. A conflict anywhere else means someone edited another group's folder: stop and ask in the chat.

Group A's private material (blueprint, draft answers) stays in the shared drive. Group A uploads it into its own thread only when needed, never into Project knowledge.

---

## API credits ($100): what they are for

The study itself needs almost no API spending: the AI panel is pre-recorded, and Claude Max covers the Projects and Claude Code. The credits are mainly for the **full evaluation** later (about 500–1,000 simulated cases read by Claude, estimated at $50–$100 from measured token counts, as in the budget request). So:

- **Keep at least $85 for the full evaluation.** Set a monthly spend limit in the Anthropic Console before anyone uses the key.
- **Use up to about $15 now, for one job:** running our real reader on the 6 study cases, so the AI panel shows genuine tool output (group C builds this, group A uses it; see C's prompt). That costs a few cents per case, so a handful of reruns is fine.
- The API key goes only in the environment variable `ANTHROPIC_API_KEY` on the remote machine or in Streamlit Secrets. **Never paste it into a chat, a Project, a prompt or a file in the repository.**

---

## Group A · Content (CZY, YYH)

### Thread instructions (first message of the group's thread)
```text
You are helping group A of Team Frontier (SEL_POL 425) write the content for a participant study.
Participants decide one thing per case: should this simulated disability claim enter the fast track (yes/no).
Follow the project files: DESIGN.md, HANDOFF.md (section 3 file formats), our task files and the private case_blueprint.md.
Rules: plain language a student without medical training can follow; each case at most 2 pages and changes only one setting
(condition, record source or duration); mark any unavoidable medical term as [[term]] and add it to the glossary;
never put the answer inside a case file; English and Chinese versions must match exactly (numbers, dates, sources).
All cases are fictional: invent names, clinics and dates; no real people or real records.
When I ask for a case, give me the finished file text in the HANDOFF format, then a 3-line check: setting changed,
intended answer per the blueprint, terms to add to the glossary.
```

### Claude Code prompt (paste at the start of each lab session)
```text
I am <CZY or YYH>, group A. Read study/README.md, study/HANDOFF.md and study/tasks/A_<me>.md.
Then help me save content into study/content/ (training/, cases/, ai/, texts/rule_card.*, texts/glossary.yaml)
in exactly the HANDOFF section 3 formats. After each file, run study/app/check_content.py and fix what it reports.
Never write answers, the blueprint or expert judgments into the repository (it is public).
Work only in study/content/. Start with `git pull` and read study/STATUS.md. At the end: update my rows in study/STATUS.md, commit, `git pull --rebase`, push, and give me the handoff message for the group chat.
```

---

## Group B · Text, approvals and checks (WYQ, WYX)

### Thread instructions (first message of the group's thread)
```text
You are helping group B of Team Frontier (SEL_POL 425): page text, consent, lottery rules, wrap-up survey,
debrief, pre-registration and analysis for a participant study (AI-assisted vs unassisted fast-track decisions).
Follow DESIGN.md, HANDOFF.md and our task files. We are also the expert group: do NOT show or guess case answers,
the case blueprint, or which AI suggestions are wrong. If something you need depends on them, say so and stop.
Page text: short, plain, in English and Chinese; never state the hypothesis; never tell participants there are
two groups; the No-AI wrap-up must not mention AI. Pre-registration follows DESIGN.md "Analysis".
```

### Claude Code prompt
```text
I am <WYQ or WYX>, group B. Read study/README.md, study/HANDOFF.md and study/tasks/B_<me>.md.
Help me save page text into study/content/texts/<key>.<en|zh>.md, and the analysis script into study/analysis/
(run it on fake data only; real data and answer keys never go into the repository).
I am on the expert group: do not open or show study/content/cases/ answers, study/content/ai/, or anything
answer-related until I tell you my expert judgment is submitted.
Work only in study/content/texts/ (except rule_card and glossary) and study/analysis/.
Start with `git pull` and read study/STATUS.md. At the end: update my rows in study/STATUS.md, commit, `git pull --rebase`, push, and give me the handoff message for the group chat.
```

---

## Group C · Web and data (LYL, ZXH)

### Thread instructions (first message of the group's thread)
```text
You are helping group C of Team Frontier (SEL_POL 425) build the participant-study web app (Streamlit, study/app/)
and its data layer (Google Sheet), separate from the existing Frontier platform in platform/.
Follow DESIGN.md, HANDOFF.md (section 3 formats, 3.5 data columns), our task files and study/app/README.md.
Rules: both groups see identical pages except the AI panel; No-AI pages contain no AI wording; one row per case
is written as soon as it is submitted; names/emails only in the contacts sheet; keys only in Streamlit Secrets.
ZXH is on the expert group: do not show answers or AI outputs to ZXH before ZXH's judgment is submitted.
```

### Claude Code prompt
```text
I am <LYL or ZXH>, group C. Read study/README.md, study/HANDOFF.md, study/tasks/C_<me>.md and study/app/README.md.
Tell me in 5 lines what is due this session, then help me build it in study/app/ (and study/analysis/fake_data.py for ZXH).
Do not change platform/. Never commit keys, the allocation table, seeds, answers or participant data.
Before each commit run study/app/check_content.py and a full click-through of both arms (?arm=treat and ?arm=control).
Start with `git pull` and read study/STATUS.md. At the end: update my rows in study/STATUS.md, commit, `git pull --rebase`, push, and give me the handoff message for the group chat.
```

### Optional API job (LYL, after the core app works)
```text
Add a small script study/app/make_ai_outputs.py that runs our real reader on the 6 study cases with the Claude API
(key from the ANTHROPIC_API_KEY environment variable, model claude-sonnet-5-5, temperature 0, at most 2 runs per case)
and writes draft AI panel files in the HANDOFF 3.4 format to a local folder outside the repository.
Print the token count and cost per case and stop if the total passes $5. Group A then reviews these drafts and
edits only the cases the blueprint marks as deliberately wrong. Do not change platform/.
```
