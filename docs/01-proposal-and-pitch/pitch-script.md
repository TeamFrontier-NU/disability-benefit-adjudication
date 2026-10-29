# Pitch script v11 (matches Design-Pitch-v11.pptx)
Total spoken words: 766 (≈ 5.3 min at 145 wpm).


## Slide 1

[Yixuan Wen, ~15 s]

Hi, we're Team Frontier. Meet Joe Swanson and Peter Griffin. Suppose Joe finally leaves the police force because of his spinal cord injury, and Peter decides his back hurts too much to work. Both apply for disability benefits. We'll follow their claims through today's system, and then through ours.



Backup detail for Q&A (not spoken):

- Joe Swanson and Peter Griffin (Family Guy) are used only as illustrative examples for a classroom presentation; all test cases are made-up and no real applicant data is used.

## Slide 2

[Yixuan Wen, ~45 s]

Start with Joe. A spinal cord injury means he can't walk. His form says: back injury, uses a wheelchair. SSA's two fast tracks look only at that form, before any records arrive, so neither flags him. He waits in line, on average 209 days, for an examiner to read his whole file. That's common: 37 percent of claims are approved at this stage, but only 8.3 percent are fast-tracked. And SSA grades its own accuracy, so no one counts eligible people turned away. Our question: can an AI that reads medical records fast-track more clear claims like Joe's, without approving people who don't qualify?

Hand-off: "Xinhui will show how."



Backup detail for Q&A (not spoken):

- Pending: 1.26 M (Jun 2024) to 865,000 (late 2025); average processing time 240 to 209 days (SSA Commissioner's letter, Nov 24, 2025).

- Fast-track share of DDS receipts (QDD + CAL): 4.2% in FY2010, 8.3% in FY2023 (SSA Fast-Track Public Use File).

- Initial approval rate: 357,630 of 963,176 initial medical decisions for 2023 applications = 37.1% (SSDI Annual Statistical Report 2024, Table 61).

- So today's fast track covers roughly 8.3 / 37.1 ≈ 22% of the claims that end up approved at the first decision; about 78% of first-decision approvals go through full review.

- Examiner effect: approval odds vary by which examiner gets the case (Maestas, Mullen & Strand, AER 2013), so past decisions are not a clean answer key.

## Slide 3

[Xinhui Zong, ~45 s]

Our theory of change: an AI that reads the medical records and applies SSA's own rules can fast-track more clear approvals, freeing examiners for hard cases, while a human decides every denial. The mechanism is decision-support automation. Follow Joe along the bottom row. The AI finds his spinal cord injury on page 12 and no earnings. That meets SSA's listing 11.08: fast track. The examiner checks three quotes and signs in minutes, and the saved time goes to Peter's harder file. Why we believe it: about half of SSA approvals meet a medical listing, and QDD shows fast tracks can be accurate.

Hand-off: "Yanqi will open both files."



Backup detail for Q&A (not spoken):

- Basis of final approvals for 2023 applications (all levels, preliminary): meets listing 46.8%, equals listing 3.7%, medical-vocational (age-education-work chart) 40.5% (SSDI Annual Statistical Report 2024, Table 64).

- Why the mechanism is 'decision-support automation', not 'administrative burden reduction': in the literature administrative burden means burden on applicants (Herd & Moynihan).

- IMAGEN: SSA tool that turns medical-record text into data for adjudicators (ACT-IAC use case; FedScoop 2024). No independent evaluation published.

## Slide 4

[Yanqi Wu, ~50 s]

Here are both files. The AI fills the same checklist for every claim: each row copies the exact words from the file and the page they came from, so the examiner can check it in seconds. Joe's rows: complete spinal cord injury, can't stand, no work since 2025. That meets the listing: fast track, signed in minutes. If Joe were still on the force, he'd fail step one, correctly. Peter: a back strain, two ER visits, no specialist. No listing is met, so he goes to a human, and the AI pulls out what argues for him, like an ER note saying he can't lift over ten pounds. The AI never denies. That's the difference from today: QDD and Compassionate Allowances read the form and fast-track 8 percent. We read the records, keep every denial human, and let independent experts count eligible people who get denied.

Hand-off: "Zhiying will tell you what we promise."



Backup detail for Q&A (not spoken):

- QDD: a predictive model gives every initial claim a likelihood score (0.0001 to 0.9999) using only information captured electronically at application; cases above a threshold are expedited. Staff cannot add QDD cases by hand (POMS DI 23022.010; OIG A-15-11-11175).

- CAL: software matches the condition names the claimant lists on the disability report (SSA-3368) against 314 listed conditions (POMS DI 23022.010; SSA, Aug 2026).

- Ours runs after records arrive, so it saves examiner work time, not the wait for records. It can sit alongside QDD: QDD at application, our tool once records are in.

- Joe: complete loss of leg function from a spinal cord injury lasting 3+ months meets Listing 11.08A. Still on the force: earnings above the substantial gainful activity limit → denied at step 1.

- Prompt-injection guard: the LLM only extracts fields with quotes; scoring is done by rules, so text hidden in a document cannot 'tell' the system to approve.

## Slide 5

[Zhiying Cui, ~50 s]

Our user is a state disability examiner. Our claim has three numbers: at least 15 percent fast-tracked, up from 8.3; at least 95 percent of those confirmed eligible by experts; and zero denials without a human. To test it, we write 50 made-up cases like Joe's and Peter's, mixed like real claims. We calibrate on 10, lock everything, then run 40 unseen cases against the experts' answers. A good scorecard: Joe fast-tracked; Peter sent to a human; Joe-still-on-the-force, not fast-tracked. At 15 percent nationally, that frees examiner time for about 84,000 more claims a year.

Hand-off: "Yihang will cover what could go wrong."



Backup detail for Q&A (not spoken):

- Test mix (40 test cases): about 15 eligible (≈ 7 meet a listing, ≈ 6 via the age-education-work chart, ≈ 2 other) and 25 not eligible, so the measured fast-track share is comparable to SSA's 8.3%.

- Time saved per claim ≈ (fast-track share − 8.3%) × full-review minutes. Example: if full review takes 60 minutes and we reach 15%, that is about 4 minutes per claim on average, or about 7% of all review time. These numbers are illustrative; the real ones come from the test.

- We don't run a separate human-only group: the human queue is unchanged, so saved work comes from claims that no longer need full review. This makes our estimate conservative, because the AI summary may also speed up the human queue.

- 15% target: a plausible step up from 8.3% given that about half of approvals meet or equal a listing; to confirm with the instructor.

- In the full study, 'experts' are experienced examiners; in the course build they are stand-ins (answer key + blind teammate check).

- Pilot vs test: the 10 pilot cases are used to tune prompts and set the threshold; then everything is locked and registered on OSF, and only then do we run the 40 test cases once, so the tool can't 'memorize' the test.

- Economic view (illustrative): about 2.36 M initial claims a year (SSA FY2025 plan) × 6.7 extra points fast-tracked ≈ 158,000 claims × about 4 staff-hours saved ≈ 630,000 hours ≈ 300 work-years ≈ $25 M a year at about $40/hour with benefits. Better framing: that capacity could handle about 84,000 more claims a year (276 cases per DDS work-year), cutting the backlog. Hours saved and wage are assumptions.

## Slide 6

[Yihang Ye, ~40 s]

Two biggest risks, each with a case. First, a wrong approval: Peter's ER note is read as a permanent limit, and he slips onto the fast track. If pilot accuracy drops below 95 percent, we raise the threshold. Second, the AI invents evidence: it 'finds' a spinal cord injury that isn't in Joe's file. Every item must quote the record; if a quote doesn't match, the case goes to a human. Smaller risks are on the slide. And our commitment: the AI never denies anyone.

Hand-off: "Yiling will close with the budget."



Backup detail for Q&A (not spoken):

- Why wrong approvals still matter: SSA later recovers overpayments, which can hurt low-income people, so 'better to over-approve' needs a cap: ≥ 95% fast-track accuracy.

- Thin records: applicants with less access to care, or with mental-health conditions, often have scattered records and may rarely reach the fast track. The slow lane is never a reason to deny.

- High-impact AI rules (OMB M-25-21, Apr 2025) call for human review and appeal for people negatively affected; keeping every denial human fits this.

- Transparency: applicants are told AI helped route their claim; appeal rights are unchanged.

## Slide 7

[Yiling Long, ~60 s]

Our course budget is a 200-dollar cap on our team's AI use, priced call by call. The largest line is two months of Claude Pro, 46 dollars, for building and writing; API calls cost from 2 cents on Sonnet up to 14 cents on Fable. And 90 dollars, 45 percent of the cap, is reserved for testing: calibration, demos, stress tests and a stronger-model check.

For real use, the AI is cheap: about 50 cents for a typical 200-page file. Adding secure hosting, audits of fast-tracked claims and a yearly expert check, we estimate about 3 million dollars a year nationally, after about 1 million to build, against examiner time worth about 25 million. We'd scale in steps: a 43,000-dollar study on real files, a one-year state pilot, then national rollout only if our targets hold.

Our ask: approve the 15 and 95 percent targets, and back a one-year state pilot if they hold. Thank you!



Backup detail for Q&A (not spoken):

- $200 plan: Claude Pro $46 (2 months, $20 + tax); API running the tool $6; building $29; testing $42 (Sonnet) + $13 (Opus) + $35 (Fable) = $90; reserve $29. Sonnet 5.5 call (3k in, 1.5k out) = $0.021; Opus 5.5 = $0.042; Fable 5.1 (4k in, 2k out) = $0.14.

- Cost per case (Sonnet): ≈ $0.03 fixed + $0.0024 per page (≈ 600 tokens a page, read twice). 2 pages ≈ 4¢; 50 pages ≈ $0.15; 200 pages ≈ $0.50; 500 pages ≈ $1.25.

- National AI cost: 2.36 M claims × $0.15–$1.25 = $0.35–3 M a year; ≈ $1.2 M at $0.50.

- Audits: 15% × 2.36 M ≈ 354,000 fast-tracked claims; audit 5–10% at ~1 hour × $40 ≈ $0.7–1.4 M.

- Yearly independent expert check: 1,000 cases × 3 experts × 40 min × $75/h ≈ $150,000.

- Hosting, security, maintenance: assumed $0.5–1 M a year.

- Total ≈ $2–6 M a year (≈ $3 M mid). One-time build ≈ $1 M, comparable to the $990,274 Technology Modernization Fund investment in AI for IMAGEN and SSA's case-processing system.

- Benefit: (15% − 8.3%) × 2.36 M ≈ 158,000 claims × ~4 h ≈ 630,000 hours ≈ $25 M a year at ~$40/h (range $14–36 M); at 276 cases per DDS work-year ≈ 84,000 more claims a year. This is capacity, not a cash cut.

- Funding route: one-time build via the Technology Modernization Fund (as IMAGEN was); running costs from SSA's administrative budget.

- State pilot ≈ $1–1.5 M: build ≈ $1 M + AI and audits for ~50,000 claims + an independent evaluation.

- All scaling numbers are rough estimates based on stated assumptions.
