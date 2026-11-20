# Examiner Study · Design Spec (short version)

Full design (Chinese, with diagrams): <https://claude.ai/artifact/7vh3fXiGNK9h3Sc95cwitp>. If this file and the full design disagree, the full design wins.

## What we evaluate

Today, QDD/CAL scores only the application form; an examiner then reads the medical records by hand. Our tool lets AI read the records first (quotes + page numbers + rule check), and a person checks it. The study compares **people alone vs. people + AI** on one decision: **should this claim enter the fast track? (yes / no)**. The later full review (approve / deny) is unchanged and not studied.

- A missed fast track (should be yes, answered no) = lost efficiency. The tool should reduce it.
- A wrong fast track (should be no, answered yes) = not allowed to increase. This is the floor.

## Design

- **Between-subjects.** After passing training, each participant is randomly assigned 1:1 (blocked in pairs) to **AI** or **No-AI** and stays there for all of their cases. **Since Nov 19 the recruitment message says that some participants get an AI assistant and others do not**, so participants know there are two groups.
- **Since Nov 18 each participant sees 3 of the 6 cases** (one of the two fast-track cases and two of the four regular-review cases, drawn independently per person, random order). The six cases are a mix of "yes" and "no" cases. **Protocol of Nov 15:** the pre-recorded AI panel agrees with the answer key on all 6 cases; there are no deliberately wrong AI suggestions. Each case changes one setting from training: the condition, where the record came from, or how long it has lasted.
- **The case blueprint (which case has which settings and the intended answers) is private**: it lives in the shared drive `03_answer_key/case_blueprint.md`, visible only to group A and LYL until the expert judgment is done. Group A assigns the final case IDs C1–C6 there, so earlier public versions of this file do not reveal the real mapping.
- **Both groups see identical case files** (typed, document-style PDFs, ≤ 2 pages each), the same rule card and the same hover glossary. The AI group additionally sees an AI panel. The No-AI page shows nothing about AI.
- **Language:** participant picks English, Spanish or Chinese at the start (Spanish added Fri 11/13, team decision); not stratified, not controlled (recorded only). All three versions must match exactly.
- **Answer key:** set by an expert group of 3 team members who did not write the cases, judging independently; unanimous = key.
- **Team members are not participants.**

## Flow (≤ 15 minutes)

1. Language → Welcome (consent, name/email, background) — ~1 min
2. Training (~4 min): rule card → worked case T1 → test case Q1; if wrong, explanation + a different test case Q2; fail twice → end (not eligible for a gift card, which requires completing the full study)
3. Random assignment (AI / No-AI)
4. 3 cases (~10–15 min, full medical records): yes / no + confidence 1–5; time recorded; no going back
5. Wrap-up survey → thanks. Debrief email to everyone after data collection ends.

## Analysis (pre-register on OSF before data collection)

- `Correct_ij = β·Treat_i + λ_App_j + ε_ij` and `log(Time_ij) = β·Treat_i + λ_App_j + ε_ij`; SEs clustered by person.
- All 6 cases enter the main models (Nov 15 protocol: no deliberately wrong AI suggestions). Limitation to state in the write-up: the study shows the effect of a correct AI aid; it does not measure over-reliance on a wrong one (future work).
- H1 faster with AI; H2 fewer missed fast tracks with AI; H3 wrong fast tracks not higher with AI (margin 10 points).
- Exclusions: failed training twice; incomplete; implausibly fast case (threshold set after pilot).
- Target 30+ participants (~15 per group); with 3 cases per person each case is seen by about half of them, so more is better. Feasibility pilot: report directions and intervals, not strong claims.

## Incentive

Approved by Diego on Nov 18: **six $10 gift cards ($60), the top 3 scorers by accuracy in each group**, among participants who complete the full study; ties broken by lottery (`study/analysis/winners.py`). Performance pay may raise effort in both groups; state this in the write-up.
