# Lab session prompt

## Before you paste the prompt (once per lab session)

1. Open a terminal and get the latest code:
   ```bash
   git clone https://github.com/TeamFrontier-NU/disability-benefit-adjudication.git   # first time only
   cd disability-benefit-adjudication
   git pull
   ```
2. Open the shared drive folder `Frontier_Study/` in the browser (answers and data live there, not on GitHub).
3. Start Claude in the repository folder (Claude Code, or upload the files below to a Claude chat).
4. Replace `<YOUR INITIALS>` and paste the prompt.

## Prompt

```text
I am <YOUR INITIALS> on Team Frontier (SEL_POL 425). We are building a participant study that compares
people with and without our AI tool on one decision: should a disability claim enter the fast track (yes/no).

Read these files in the repository first, in this order:
1. study/README.md            (what each file is)
2. study/DESIGN.md            (the study design)
3. study/HANDOFF.md           (who owns what, file formats, schedule, handoffs)
4. study/tasks/<my file>.md   (my own tasks)

Then:
- Tell me in 5 lines what I must deliver in THIS lab session, where it goes, and who receives it.
- Help me do it, one deliverable at a time. Follow the file formats in HANDOFF.md section 3 exactly.
- Only touch the folders my task file says I own. Do not change platform/ or another group's files.
- This repository is public: never commit answer keys, expert judgments, participant data,
  the allocation table, random seeds or keys.
- If I am on the expert group (WYQ, WYX, ZXH) and have not submitted my expert judgment yet,
  do not show me answer keys or AI outputs.
- At the end, list what I finished, what is left, and the exact message I should post to the group
  for the handoff.
```

## At the end of the session

```bash
git add study/
git status          # check that no answer, data, seed or key file is listed
git commit -m "<initials>: <what you finished>"
git pull --rebase
git push
```

Then post the handoff message in the group chat.
