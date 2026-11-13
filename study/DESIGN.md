# Examiner Study · Design Spec (short version)

Full design (Chinese, with diagrams): <https://claude.ai/artifact/7vh3fXiGNK9h3Sc95cwitp>. If this file and the full design disagree, the full design wins.

## What we evaluate

Today, QDD/CAL scores only the application form; an examiner then reads the medical records by hand. Our tool lets AI read the records first (quotes + page numbers + rule check), and a person checks it. The study compares **people alone vs. people + AI** on one decision: **should this claim enter the fast track? (yes / no)**. The later full review (approve / deny) is unchanged and not studied.

- A missed fast track (should be yes, answered no) = lost efficiency. The tool should reduce it.
- A wrong fast track (should be no, answered yes) = not allowed to increase. This is the floor.

## Design

- **Between-subjects.** After passing training, each participant is randomly assigned 1:1 (blocked in pairs) to **AI** or **No-AI** and stays there for all 6 cases. Neither group is told the other exists.
- **Same 6 cases for everyone**, shown in random order: a mix of "yes" and "no" cases, plus some cases where the AI panel is deliberately wrong (to measure over-reliance). Each case changes one setting from training: the condition, where the record came from, or how long it has lasted.
- **The case blueprint (which case has which settings, the intended answers and which AI suggestions are wrong) is private**: it lives in the shared drive `03_answer_key/case_blueprint.md`, visible only to group A and LYL until the expert judgment is done. Group A assigns the final case IDs C1–C6 there, so earlier public versions of this file do not reveal the real mapping.
- **Both groups see identical case files** (typed, document-style PDFs, ≤ 2 pages each), the same rule card and the same hover glossary. The AI group additionally sees an AI panel. The No-AI page shows nothing about AI.
- **Language:** participant picks English, Spanish or Chinese at the start (Spanish added Fri 11/13, team decision); not stratified, not controlled (recorded only). All three versions must match exactly.
- **Answer key:** set by an expert group of 3 team members who did not write the cases, judging independently; unanimous = key.
- **Team members are not participants.**

## Flow (≤ 15 minutes)

1. Language → Welcome (consent, name/email, background) — ~1 min
2. Training (~4 min): rule card → worked case T1 → test case Q1; if wrong, explanation + a different test case Q2; fail twice → end (still in lottery)
3. Random assignment (AI / No-AI)
4. 6 cases (~10 min): yes / no + confidence 1–5; time recorded; no going back
5. Wrap-up survey → thanks. Debrief email to everyone after data collection ends.

## Analysis (pre-register on OSF before data collection)

- `Correct_ij = β·Treat_i + λ_App_j + ε_ij` and `log(Time_ij) = β·Treat_i + λ_App_j + ε_ij`; SEs clustered by person.
- Main models exclude the cases with a deliberately wrong AI suggestion (IDs in the private blueprint); report them separately (how many people the wrong AI misled).
- H1 faster with AI; H2 fewer missed fast tracks with AI; H3 wrong fast tracks not higher with AI (margin 10 points).
- Exclusions: failed training twice; incomplete; implausibly fast case (threshold set after pilot).
- Target 30+ participants (~15 per group). Feasibility pilot: report directions and intervals, not strong claims.

## Incentive

4 × $20 gift-card lottery (remaining $80 after Claude Max). Entry does not depend on accuracy. Pending Diego's OK to use course funds.
