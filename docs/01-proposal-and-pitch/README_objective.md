# Project Objective: Record-Based Fast-Track Screening for Initial SSI/SSDI Claims

Team 06 · Frontier · SEL_POL 425 · Fall 2026
Last updated: Oct 22, 2026 (replaces the Oct 16 research prompt)

This file is the working brief for every later task: building the tool, writing test cases, preparing the halfway and final presentations, and briefing any AI assistant. When this file and an older document disagree, this file wins.

---

## 1. Objective in one sentence

Build and test an AI tool that reads the medical records in each initial adult SSI/SSDI claim, applies SSA's own rules, and sends claims that clearly qualify to a fast track, while every denial stays with a human, and check its results against an independent expert standard, with particular attention to eligible people who get denied.

## 2. Why

- SSA's fast tracks (Quick Disability Determinations, QDD, and Compassionate Allowances, CAL) screen claims from the application form, before medical records arrive. Together they fast-track 8.3% of initial claims (FY2023).
- About 37% of claims are approved at the initial level (2023 applications), so roughly 78% of first-decision approvals still go through a full review from scratch. The average wait for a first decision is about 209 days (late 2025).
- SSA measures its own accuracy (97.1% net accuracy, FY2022). No one independently counts eligible people who are denied.

## 3. Locked design decisions

These are settled. Change them only with a team decision, and record the change here.

1. **Scope:** initial-level adult SSI, SSDI and concurrent claims. Out of scope: reconsideration, hearings, continuing disability reviews, children's claims.
2. **Asymmetric routing:** the AI may send a claim to the fast track for approval. It never denies. Every claim not fast-tracked goes to a human queue, whatever the AI score.
3. **Record-based, rule-based scoring:** an LLM reads the file and fills a fixed checklist; the score comes from transparent SSA rules (Step 1 work and earnings, the Listings, the age-education-work chart), not from the LLM's own judgment.
4. **Quote and page for every checklist item:** each value must quote the file and give the page. Quotes are checked automatically; any item whose quote can't be found is dropped, and the case goes to a human.
5. **Evidence for approval in the human queue:** for every claim sent to a human, the AI also lists the evidence that supports eligibility. It never writes a recommendation to deny.
6. **Independent reference standard:** accuracy is judged against expert decisions made blind to the AI, never against past SSA decisions.
7. **No real applicant data** in the course build. All cases are made up. Joe and Peter are illustrative characters only.
8. **Team AI budget:** $200 for all AI use in the course (subscription plus API).

## 4. Pre-registered claim and thresholds

The claim is the number we promise and will be tested on. It is posted on OSF before any test result is seen.

| Measure | Threshold |
| --- | --- |
| Fast-track rate (share of test cases sent to the fast track) | ≥ 15% (SSA today: 8.3%) |
| Fast-track precision (share of fast-tracked cases the experts judge eligible) | ≥ 95% |
| Denials made by the AI | 0 |

The thresholds are proposed by the team and are to be confirmed with the instructor (open item).

## 5. Course build (Weeks 5–10): what we deliver

- **Tool:** the five-step pipeline: Collect → Read (checklist) → Score (rules) → Route → Decide. It must run live and handle at least two adversarial inputs, such as a file with a hidden instruction or a file with a fabricated injury.
- **Cases:** 50 made-up case files, 1–2 pages each, mixed like real claims (about 37% eligible): 10 calibration cases and 40 test cases. Each has an answer key written to a specific SSA rule, re-checked blind by two teammates who did not write it.
- **Evaluation:** calibrate on the 10 cases, lock prompts and threshold, then run the 40 test cases once and report the measures in Section 4 with 95% confidence intervals.
- **Presentations:** design pitch (Week 5), halfway with live demo (Week 7), final with live demo and honest results (Week 10).

## 6. Milestones

| Week | Milestone | Done when |
| --- | --- | --- |
| 5 | Pitch recorded | Video submitted; case template and rule table drafted |
| 6 | Pipeline v1 + calibration | Tool runs end to end on 10 calibration cases; threshold set; plan posted on OSF |
| 7 | Halfway presentation | Live demo; 40 test cases written and blind-checked |
| 8 | Test run | 40 test cases run once with locked settings; experts' review timed |
| 9 | Analysis + stress tests | Measures and CIs computed; adversarial and equity checks done |
| 10 | Final presentation | Live demo; results reported against the pre-registered thresholds |

## 7. Working rules for anyone on this project (people or AI)

- Use the terms in Section 9 consistently. Say "fast track", not "short check"; say "human queue", not "second look".
- Never put real applicant names or case data into any AI tool.
- Never tune prompts or thresholds on the 40 test cases. If a change is needed after the lock, log it and report it.
- Cite SSA numbers with their source and year. Label estimates and assumptions as such.
- Log AI use weekly in `00 AI Log/weekly-tracker.md`, including spend against the $200.

## 8. Open items

- [ ] Instructor confirms the 15% and 95% thresholds and whether the $200 may include the Claude Pro subscription.
- [ ] Choose the subset of Listings the test cases will cover (for example 11.08 spinal cord disorders, 13.x cancers, 12.04 depressive disorders).
- [ ] Add one course reading that supports the decision-support mechanism.
- [ ] Decide whether to recruit volunteer readers for the human queue (optional; see the proposal, Section 6.4).
- [ ] Decide whether an outside reviewer (e.g. a disability-law clinic contact) can check disputed answer keys.

## 9. Key terms

| Term | Meaning in this project |
| --- | --- |
| Fast track | Claims the tool routes for quick approval; a human signs off and a sample is audited |
| Human queue | Every claim not fast-tracked; decided by an examiner with the AI checklist and evidence for approval |
| Checklist | Fixed set of fields the LLM fills from the file, each with a quote and page number |
| Answer key | The correct decision for a made-up case, fixed when the case is written |
| Calibration cases | The 10 cases used to tune prompts and the threshold before the lock |
| Test cases | The 40 cases run once after the lock to produce the reported numbers |
| Fast-track precision | Share of fast-tracked cases the experts judge eligible |
| Wrongful denial | An eligible person who is denied |

## 10. Related files

- `research-proposal.md`: full design and methods (course build and follow-on study)
- `项目逻辑梳理.md`: Chinese plain-language walkthrough and Q&A prep
- `Design-Pitch-v10.pptx`, `pitch-script-v10.md`: current pitch deck and script
- `study-design.md`: earlier study design (superseded; parts still apply to Phase 2)
