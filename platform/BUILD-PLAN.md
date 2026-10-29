# Build Plan: Step by Step to the Final Presentation

Team 06 · Frontier · written 2026-10-29 by Claude (Opus 5.5) · design confirmed by the team on 2026-10-29
Follows `02 Project Revision/design-final_v1_2026-10-24.md`. The prototype in this folder is the starting point.

How to use this plan: do the steps in order. Each step has a "done when" line. Tick the box when it's true, not when the work has started. Owner **[Team]** means a person has to do it; **[Claude]** means Claude can do it in a project thread; **[Both]** means Claude drafts and the team checks.

Key dates (from the course rubrics): halfway presentation with live demo, **Week 7 Friday (Nov 6)**. Final presentation, **Week 10**.

---

## Overview

| Step | What | Week | Owner | Feeds |
| --- | --- | --- | --- | --- |
| 1 | Get the panel running on the team computer | 6 (now) | Team | Everything |
| 2 | Make the simulated cases realistic | 6 | Claude, then Team checks | Fair test |
| 3 | Blind-check the answer keys | 6–7 | Team | Reference standard |
| 4 | Calibrate the Claude reader on the 10 calibration cases | 6–7 | Both | Locked settings |
| 5 | Lock settings and pre-register on OSF | 7 (before Nov 6) | Team | Evaluation plan (halfway, 5 pts) |
| 6 | Prepare the halfway demo and slides | 7 | Both | Halfway presentation (20 pts) |
| 7 | Run the 40 test cases once | 8 | Team runs, Claude helps | The claim |
| 8 | Examiner study: human-only vs. human + AI | 8 | Team + volunteers | Speed and accuracy numbers |
| 9 | Stress tests, equity check, analysis | 9 | Both | Honest results |
| 10 | Government connector design + final presentation | 9–10 | Both | Final (60 pts) |

---

## Step 1. Get the panel running on the team computer (Week 6, now)

- [ ] Open a terminal in `03 Platform` and run `pip install -r requirements.txt`, then `streamlit run app.py`.
- [ ] Click through the demo set: Joe should go to the fast track. Peter and "Joe, still working" should go to the human queue.
- [ ] Turn "Safeguards on" off on the stress set, then on again. Check that 3 gaming cases move onto the fast track and back.
- [ ] Set up an API key for the Claude reader (`export ANTHROPIC_API_KEY=...` or `ant auth login`). Set a spending limit on the account so the $200 cap can't be passed by mistake.
- [ ] Note any errors or confusing screens in the issue log at the end of this file.

**Done when:** every teammate who will demo has opened the panel once, and one Claude-reader run on Joe has worked.

## Step 2. Make the simulated cases realistic (Week 6)

Issue this fixes: every case uses the same template sentences, so the test is easier than real records. The offline baseline's 61/61 score is circular because of this (issue I-1).

- [x] **[Claude]** Generator v2 adds 3–4 wordings for each finding, so "complete loss of function" also appears as, for example, "complete paraplegia with no motor or sensory function in either leg". *(Done Oct 29)*
- [x] **[Claude]** Make records longer, with unrelated history, vitals, normal findings and medicine notes, so the reader has to find the relevant line. *(Done Oct 29: still one page per record; multi-page records are a possible later step)*
- [x] **[Claude]** Add realistic noise: abbreviations (BLE, SCI, ESRD), small typos, and dates in different formats. *(Done Oct 29)*
- [x] **[Claude]** Add near-miss cases that look eligible but aren't: a spinal cord injury under 3 months old, temporary dialysis, and sedentary limits at age 47. Resected stage I lung cancer was already in the test set. *(Done Oct 29)*
- [ ] **[Team]** Each teammate rewrites 2 cases by hand in their own words. These become the hardest part of the test.
- [ ] Keep v1 for the demo; v2 is used for calibration and test. The test mix stays as in the design (15 eligible / 25 not; 13 on a fast-track path).

**Done when:** the offline keyword baseline no longer gets everything right on v2. That proves the wording varies. The test-mix table in `README.md` still matches.

## Step 3. Blind-check the answer keys (Weeks 6–7)

Matches design decision 6 and risk R3 in the pitch.

- [ ] **[Team]** Two teammates who did not write a case each decide it without seeing the key: allow, deny or need more evidence, plus the basis.
- [ ] Disagreements: discuss. Rewrite the case, or label it "borderline" and report it separately.
- [ ] **[Claude]** Write a small script that lists the agreement rate (kappa) for the report.

**Done when:** all 10 calibration and 40 test keys have two blind checks recorded in `answer_key.json` (`checker_1`, `checker_2`, `agreed`).

## Step 4. Calibrate the Claude reader (Weeks 6–7)

- [ ] Run `python scripts/run_batch.py --set calibration --reader claude --k 1`, then the same with `--k 2`. That's about $1 for both.
- [ ] **[Both]** Read every mismatch on the panel. Is it a prompt problem, a rule problem, or a bad case?
- [ ] Fix prompts or rules. Only use calibration cases for this, **never** the test cases.
- [ ] Record each run's cost in the weekly AI log, against the $200 cap.

**Done when:** calibration results are stable over two runs, and k is chosen with a written reason.

## Step 5. Lock and pre-register (Week 7, before the halfway presentation)

This answers the halfway rubric line "claim, threshold, counterfactual, and assignment mechanism approved by the instructor".

- [ ] **[Claude]** Draft the OSF pre-registration with these items:
  - Claim: fast-track rate ≥ 15%, fast-track precision ≥ 95%, 0 AI denials.
  - Counterfactual: today's form-based fast track (8.3%), and examiners working without AI.
  - Assignment: each volunteer reviews half the cases with AI and half without. The cases are swapped between volunteers in random order (a crossover design), so each case is seen both ways.
  - Sample: 40 test cases, with a ±11-point CI said out loud.
  - Analysis: Wilson CIs, with the stress set reported separately.
- [ ] **[Team]** Email the instructor to confirm the thresholds and the $200 scope. This is an open item since Week 5.
- [ ] **[Team]** Freeze: tag the code (zip `03 Platform` as `platform_locked_<date>.zip`), then post on OSF.

**Done when:** the OSF link is in `01 Proposal & Pitch/README_objective.md` and the instructor has replied.

## Step 6. Halfway presentation (Week 7, Nov 6)

The rubric, 20 points: honest account 7, live demo 5, evaluation plan 5, uncertainties 3.

- [ ] **[Claude]** Draft an 8-minute deck. Check every number against the consistency list in the design doc, §8.
- [ ] Honest account: what works (the panel, the rules, the safeguards), what doesn't yet (no examiner timing, wording realism), and what changed since the pitch (D1–D6) and why. Include spend to date with the largest line.
- [ ] Live demo plan: Joe → fast track; Peter → human queue; then the discussant team's adversarial input through "Live test: add a document". Rehearse with a hidden instruction and a fake record.
- [ ] Two real uncertainties: (a) mental claims always go to a human (D5), which caps the fast-track rate; (b) claimant-supplied records are never allowed onto the fast track (C3).
- [ ] Backup: offline reader mode if the network fails. Practice switching to it.

**Done when:** one full rehearsal under 8 minutes, with a live adversarial input.

## Step 7. Run the 40 test cases once (Week 8)

- [ ] Run `python scripts/run_batch.py --set test --reader claude --k <locked>` **once**. Save the results file, and don't re-run after looking.
- [ ] If something breaks mid-run, log it and report it. Don't quietly re-run.

**Done when:** one saved results file, with its cost logged.

## Step 8. Examiner study (Week 8)

- [ ] **[Team]** Recruit 3–6 volunteers (classmates are fine), and give them a 10-minute training on the panel.
- [ ] Each volunteer reviews about 10 cases in the panel: half "Human only", half "Human + AI", with the assignment from Step 5.
- [ ] The panel times each decision and logs it to `data/decisions.jsonl`. Back this file up after every session.

**Done when:** at least 40 logged decisions, split evenly between the two modes.

## Step 9. Stress tests, equity check and analysis (Week 9)

- [ ] Run the stress set (8 cases) and the near-miss cases.
- [ ] **[Claude]** Add two measures promised in the proposal that aren't built yet:
  - **Equity check:** fast-track rate and recall for physical vs. mental cases (issue I-5).
  - **Evidence-for-approval recall:** this needs key evidence pages in each answer key (issue I-6).
- [ ] **[Both]** Results table: each measure, the target, the result with its CI, and met or not met.
- [ ] Write the limitations honestly: simulated data, a small sample, volunteers instead of real examiners.

**Done when:** a results section exists that the team can defend line by line.

## Step 10. Government connector design and final presentation (Weeks 9–10)

- [ ] **[Claude]** Write a 1-page design for `SSAeFolderConnector`. It should cover what data it reads, how `source_type` and `received_via` come from the system's own metadata, security, and what a pilot partner would need to give us. No access is assumed.
- [ ] **[Both]** Final 12-minute deck: problem → design → live demo → evaluation → results → next steps (real-file study, state pilot).
- [ ] Rehearse Q&A: every member answers questions on their own section.

**Done when:** final rehearsal done, and the demo handles two adversarial inputs.

---

## Issue log (keep adding to this)

| # | Issue | Found | Fix in step | Status |
| --- | --- | --- | --- | --- |
| I-1 | The offline keyword baseline scores 61/61 because it was written alongside the templates. It is not evidence for the claim | Oct 24 | 2 | Fixed Oct 29: on v2 it scores 27/40; use offline mode only on the demo set |
| I-2 | The Claude reader has not been run yet; the fallback option with structured output is untested | Oct 24 | 1, 4 | Open |
| I-3 | Only one wording per finding; records are short | Oct 24 | 2 | Mostly fixed Oct 29 (v2); hand-written cases still to do |
| I-4 | Answer keys are written by Claude and not yet checked by people | Oct 24 | 3 | Open |
| I-5 | Equity measure (physical vs. mental) not built | Oct 29 | 9 | Open |
| I-6 | Evidence-for-approval recall not built; answer keys lack key-evidence pages for every case | Oct 29 | 9 | Open |
| I-7 | The 11.08 duration check uses the latest medical record's date, not the date of the record that supports the finding | Oct 29 | 4 | Open |
| I-8 | The decision log is one local file; two examiners at once on different computers would need merging | Oct 29 | 8 | Open (fine for the course) |
| I-9 | The Week 6 tracking file update from Oct 24 didn't reach the team computer (found Oct 29); re-sent | Oct 29 | — | Fixed |
| I-10 | `research-proposal.md` §5.1 still lists "working above SGA" in the test mix, and `README_objective.md` §10 still names the v10 deck | Oct 24 | 5 | Open |
| I-11 | Instructor hasn't confirmed the 15% / 95% thresholds and the $200 scope | Week 5 | 5 | Open |
| I-12 | With v2 wording, the offline backup can't show the "safeguards off" demo; that now needs the Claude reader | Oct 29 | 6 | Open: plan the halfway demo around it |
