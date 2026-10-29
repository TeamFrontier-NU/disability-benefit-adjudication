# Research Proposal: Record-Based Fast-Track Screening for Initial Adult SSI/SSDI Claims

Team 06 · Frontier · SEL_POL 425 · Oct 22, 2026
Replaces the Oct 16 proposal (blinded comparison of human-only, AI-only and human-plus-AI adjudication). The verified data sources, ethics plan and expert-panel design from that version carry over to Phase 2 below.

## Title and abstract

**Can an AI That Reads Medical Records Widen SSA's Disability Fast Track? A Pre-Registered Evaluation of Record-Based, Approval-Only Screening for Initial SSI/SSDI Claims**

**Abstract.** State disability determination services (DDS) decide about 2.4 million initial disability claims a year. SSA's two fast tracks, Quick Disability Determinations (QDD) and Compassionate Allowances (CAL), screen claims from the application form, before medical records arrive, and together fast-track 8.3% of claims, even though about 37% are approved at the initial level. Most clear approvals therefore wait for a full review. We propose a tool that reads each claim's medical records with a large language model (LLM), fills a fixed checklist in which every item quotes the file and gives the page, and applies SSA's own rules (Step 1 work and earnings, the medical Listings and the age-education-work chart) to send claims that clearly qualify to a fast track. The design is asymmetric: the tool may fast-track approvals, but it never denies; every other claim goes to a human, together with a list of the evidence that supports eligibility. We test it against an independent expert standard, not against past SSA decisions. The pre-registered claim is a fast-track rate of at least 15%, with at least 95% of fast-tracked claims judged eligible by experts and no denial made without a human. Phase 1, a course build, tests the tool on 50 made-up case files within a $200 team AI budget. Phase 2, a nine-month follow-on study, tests it on consented real case files with a three-expert panel. If the 15% target held nationally, the freed examiner time would equal about 84,000 additional claims a year.

## 1. Background and gap

**Scale and delay.** SSA reported 1.26 million pending initial disability claims in June 2024, reduced to 865,000 by late 2025, with the average initial processing time down from 240 to 209 days ([SSA Commissioner's letter, Nov 24, 2025](https://www.ssa.gov/blog/en/posts/2025-11-24.html)). DDS productivity fell 21% and processing time rose 81% between FY2019 and FY2023 ([SSA OIG, 2025](https://oig.ssa.gov/news-releases/2025-07-18-disability-determination-service%E2%80%99s-21-percent-productivity-decrease-and-81-percent-increase-in-processing-times-coincided-with-the-loss-of-key-technical-staff/)).

**Narrow fast tracks.** QDD uses a predictive model that gives every initial claim a likelihood score from 0.0001 to 0.9999, based only on information captured electronically at application; claims above a threshold are expedited, and staff cannot add QDD cases by hand ([POMS DI 23022.010](https://secure.ssa.gov/POMS.NSF/lnx/0423022010); [OIG A-15-11-11175](https://oig.ssa.gov/assets/uploads/a-15-11-11175.pdf)). CAL software matches the condition names a claimant lists on the disability report against a list of 314 conditions. Fast-tracked receipts rose from 4.2% of DDS receipts in FY2010 to 8.3% in FY2023 ([SSA Fast-Track Public Use File](https://www.ssa.gov/disabilityresearch/fasttrackpuf.html)). QDD is accurate where it acts: 93% of a 575-case OIG sample was allowed ([OIG A-01-09-19030](https://oig-files.ssa.gov/audits/full/html/A-01-09-19030.html)).

**Room to widen.** For 2023 applications, 357,630 of 963,176 initial medical decisions were allowances (37.1%) ([SSDI Annual Statistical Report 2024, Table 61](https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect04.pdf)). Today's fast track therefore covers about 22% of eventual first-decision approvals. About half of final approvals rest on meeting (46.8%) or equaling (3.7%) a medical listing, and 40.5% on medical-vocational factors (Table 64; all levels, preliminary). Many approvals are thus rule-clear once the medical evidence is read, but no current tool reads it for this purpose.

**AI already in use, unevaluated.** SSA already uses IMAGEN to turn medical-record text into data for adjudicators ([ACT-IAC](https://www.actiac.org/et-use-case/intelligent-medical-language-analysis-generation-imagen)), but no independent evaluation has been published.

**Accuracy is self-measured.** SSA reports a DDS net accuracy of 97.1% for FY2022 from its own quality review ([DDS Net Accuracy](https://www.ssa.gov/data/disability-determination-services-accuracy.html)). Allowance decisions also depend partly on which examiner decides (Maestas, Mullen and Strand, 2013), so past decisions are not a clean answer key.

**The gap.** No study has tested whether reading the medical records can widen the fast track, measured against an independent standard, with wrongful denials counted.

## 2. Research questions and hypotheses

| RQ | Question | Hypothesis / target |
| --- | --- | --- |
| RQ1 Coverage | What share of claims can record-based screening route to the fast track? | Fast-track rate ≥ 15% on a test set mixed like real claims (primary) |
| RQ2 Accuracy | How many fast-tracked claims do experts judge eligible? | Fast-track precision ≥ 95% (primary guardrail) |
| RQ3 Fidelity | How accurately does the LLM extract checklist items, and how often does it cite evidence that isn't in the file? | Field accuracy and quote-verification rate reported; fabricated items caught by the quote check |
| RQ4 Eligible people at risk | For claims sent to humans, does the AI's evidence-for-approval list surface the key pro-eligibility evidence in the answer key? | Recall of key pro-eligibility evidence reported (secondary) |
| RQ5 Equity | Does the fast-track rate or recall differ by impairment type (physical vs. mental) or record length? | Two-sided; gaps reported, no direction assumed |
| RQ6 Efficiency | How much examiner time could the wider fast track free? | Estimated from timed expert reviews (secondary, illustrative at national scale) |

The AI never denies, so it cannot create a wrongful denial by itself; RQ4 tracks whether it helps the human queue avoid them.

## 3. The tool

### 3.1 Pipeline

1. **Collect.** Application data and medical records dated on or before the decision date.
2. **Read.** An LLM fills a fixed checklist. Every item has a value, a verbatim quote and a page number.
3. **Score.** Transparent rules, not the LLM, produce the routing decision:
   - Step 1: current work and earnings above the substantial gainful activity (SGA) limit → not fast-tracked, and flagged for a human;
   - Step 3: findings that meet a covered medical listing;
   - Step 5: the age-education-work chart (medical-vocational guidelines), where it directs a finding of disabled.
4. **Route.** Fast track only if all of these hold: Step 1 is passed; a listing is met or the chart directs disabled; there is no conflicting evidence; every supporting quote is verified; and the rule score is at or above the locked threshold. Everything else goes to the human queue.
5. **Decide.** Fast-tracked claims are approved after a short human sign-off, with a random sample audited. In the human queue an examiner decides, with the checklist and a list of evidence for approval; the tool writes no recommendation to deny.

### 3.2 Checklist fields

| Field | Example (Case A, Joe) |
| --- | --- |
| Age, education, past work and its exertional level | 52; high school; police officer (medium) |
| Current work and earnings | "no work since 2025" (p. 2) |
| Diagnoses, with dates | "complete spinal cord injury" (p. 12) |
| Listing-relevant findings | complete loss of lower-extremity function for 3+ months |
| Functional limits (sit, stand, walk, lift; mental limits) | "cannot stand or walk" (p. 15) |
| Treatment history | surgeries, specialist care, gaps |
| Evidence that supports eligibility | quotes the human queue should see |
| Missing evidence | records a competent examiner would request |

### 3.3 Safeguards built into the design

- **Quote verification:** every quote is string-matched to the cited page. Unmatched items are dropped, and the case goes to a human.
- **Prompt-injection resistance:** the LLM only extracts; rules decide. Text hidden in a document cannot change the routing by instruction.
- **Asymmetry:** no path in the code produces a denial.

### 3.4 How it differs from current practice

| | QDD | CAL | Proposed tool |
| --- | --- | --- | --- |
| When it looks | At application | At application | After records arrive |
| What it reads | Information typed into the application | Condition name on the form | The full medical record |
| How it decides | Statistical likelihood score | Name matches one of 314 conditions | SSA rules on extracted, quoted evidence |
| Share fast-tracked | 8.3% together (FY2023) | (included) | Target ≥ 15% |
| Denials | Normal human review | Normal human review | Always human, with evidence for approval |
| Checked against | SSA's own decisions | SSA's own decisions | Independent experts; wrongful denials counted |

**Theory of change.** SSA's fast tracks see only the form; an AI that reads each claim's medical records and applies SSA's rules can fast-track more clear approvals, freeing examiners for hard cases while a human decides every denial. **Mechanism:** decision-support automation.

## 4. Two phases

| | Phase 1: course build | Phase 2: follow-on study |
| --- | --- | --- |
| Timing | Weeks 5–10 of the course | 9 months |
| Money | $200 team AI budget | About $43,000 (planning estimate) |
| Cases | 50 made-up case files | Consented closed files from a legal aid office or law-school clinic (partner not yet identified); vignettes as fallback |
| Reference standard | Answer key + blind re-check by two teammates | Three-expert blinded panel |
| Scoring | SSA rules | SSA rules; plus logistic regression and boosted trees trained on HRS–SSA records as comparators |
| Data access | None needed | IRB approval; HRS restricted-data agreement |

## 5. Phase 1 methods

### 5.1 Case files

- 50 made-up files of 1–2 pages, each written to one specific rule path. The fictional page numbers mimic a longer file.
- **Mix:** about 37% eligible, matching SSA's initial allowance rate. For the 40 test cases: about 15 eligible (≈ 7 meet a listing, ≈ 6 via the age-education-work chart, ≈ 2 other paths) and about 25 not eligible (including working above SGA, non-severe conditions, and conditions that leave the applicant able to work).
- Both physical and mental impairments are included, so RQ5 can be checked.
- **Answer key:** set by the author per SSA rules and re-decided blind by two teammates who did not write the case. Cases where the reviewers disagree are rewritten or labelled "borderline" and reported separately.

### 5.2 Calibration and test split

- **Calibration (10 cases):** used to tune prompts, the checklist and the routing threshold.
- **Lock:** prompts, rules and threshold are then frozen and posted on OSF with the analysis plan.
- **Test (40 cases):** run once.

This is not a train/test split for a learned model: nothing is trained in Phase 1, and only one threshold is tuned, so most cases are kept for testing. With 40 test cases, the 95% interval on the fast-track rate is about ±11 points.

### 5.3 Measures

| Measure | Definition | Target |
| --- | --- | --- |
| Fast-track rate | Fast-tracked test cases ÷ all test cases | ≥ 15% |
| Fast-track precision | Fast-tracked cases judged eligible ÷ fast-tracked cases | ≥ 95% |
| AI denials | Count of denials produced by the tool | 0 |
| Fast-track recall | Fast-tracked eligible cases ÷ all eligible cases | Reported |
| Field accuracy | Checklist values matching the answer key | Reported |
| Quote verification rate | Quotes found on the cited page ÷ all quotes | Reported |
| Evidence-for-approval recall | Key pro-eligibility items in the answer key that the list surfaced | Reported |
| Equity gaps | Fast-track rate and recall by impairment type and file length | Reported |
| Full-review minutes | Timed expert review per case | Input to the efficiency estimate |

**Analysis.** Proportions with Wilson 95% confidence intervals. Results are compared with the pre-registered thresholds and reported whether or not they are met.

### 5.4 Stress tests

These tests use separate adversarial files that are not part of the 40 test cases:
- a hidden instruction inside a record ("approve this claim");
- a fabricated diagnosis that appears in no record;
- contradictory records;
- a high-earning applicant with a qualifying condition, the "Joe still on the force" case.

### 5.5 Optional: human queue

If volunteer readers are recruited, they decide the human-queue cases with the checklist and the evidence list. The experts then flag any wrongful denial. This step is not needed for the primary claim.

## 6. Efficiency and cost estimate (illustrative)

- **National scale:** about 2.36 million initial claims a year (SSA FY2025 plan) × 6.7 extra points fast-tracked ≈ 158,000 claims a year.
- **Time freed:** at about 4 staff-hours saved per fast-tracked claim (assumption), that is about 630,000 hours, or about 300 work-years.
- **Value:** at about $40 an hour with benefits (assumption, based on Texas claims-examiner pay of $45.5k–71k), that is about $25M a year (range $14M–$36M).
- **Capacity framing:** at 276 cases per DDS work-year (SSA FY2025 plan), the freed time could handle about 84,000 more claims a year.
- **AI cost per case:** with Sonnet 5.5, about $0.03 fixed plus $0.0024 per page (two reads at about 600 tokens a page). That is about 4¢ for a 2-page test case and $0.15–$1.25 for a real 50–500-page file, or about $1.2M a year at about $0.50 a case.

The real hours saved per fast-tracked case will come from the timed reviews.

## 7. Phase 2 (follow-on study) in brief

- **Data:** HRS linked to SSA Form 831 initial determinations, obtainable through a standard restricted-data agreement, for training comparator models. This limits training to applicants about 50 and over. Consented closed case files from a clinic partner serve as the panel set, with constructed vignettes as fallback. Outside access to the Disability Analysis File (DAF) is uncertain since SSA terminated the Retirement and Disability Research Consortium on Feb 20, 2025.
- **Reference standard:** three experts re-decide each case blind to the original and AI decisions, using only evidence dated by the decision. "Insufficient evidence" and disagreement are kept as outcomes. Reviewers apply the rules in force on each decision date, including the 2017 revised medical-evidence rules (82 FR 5844).
- **Added comparators:** penalized logistic regression and gradient-boosted trees on shared features, frozen before any panel label is seen, with person and time splits.
- **Budget:** about $43,000, mostly expert-panel time (planning estimates: panel about $30k, study readers $5k, research assistants $6.6k, data access and computing up to $2.5k).
- **Gates:**
  - month 2: case files secured, or switch to vignettes;
  - month 4: models frozen;
  - month 7: panel complete.

## 8. Risks and responses

| Risk | Example | Warning sign | Design response |
| --- | --- | --- | --- |
| R1 Wrong approvals on the fast track | Peter's ER note is read as a permanent limit | Calibration precision below 95% | Raise the threshold; fast-track fewer claims |
| R2 LLM misreads or invents evidence | The AI "finds" a spinal cord injury not in Joe's file | A quote doesn't match the record | Drop the item; send the case to a human |
| R3 The answer key is only our reading of the rules | Team authors share a mistake | Blind re-check disagrees on > 20% | Rewrite disputed cases; outside reviewer if available |
| R4 Thin records never qualify | Mental-health or rural applicants with scattered records | Fast-track rate differs by impairment type | Report gaps; the human queue is never a denial |
| R5 Made-up cases are cleaner than real files | Results don't transfer | — | State as a limitation; Phase 2 uses real files |

## 9. Ethics

- **No real applicant data** in Phase 1, in prompts, or in any AI tool. In Phase 2, real files are handled only after IRB approval, client consent and a data-use agreement, inside an approved secure environment.
- **The tool never denies.** This is consistent with federal guidance that people negatively affected by high-impact AI receive human review and a chance to appeal (OMB M-25-21, Apr 2025).
- **Wrongful approvals are capped** (≥ 95% precision), because later overpayment recovery harms low-income people.
- **Automation bias:** the human queue sees evidence for approval, never a recommendation to deny.
- **Equity:** results are reported by impairment type and file length.
- **Transparency:** applicants would be told AI helped route their claim; appeal rights are unchanged.

## 10. Phase 1 budget: team AI use against the $200 cap

| Item | Model, $ per M tokens (in / out) | $ per call | Calls | Total |
| --- | --- | --- | --- | --- |
| Claude Pro: building and writing | $20–23 / month | fixed | 2 months | $46 |
| API: running the tool | Sonnet 5.5, $2 / $10 | 0.04 per case | 150 | $6 |
| API: building and fixing the tool | Sonnet 5.5 | 0.021 | 1,400 | $29 |
| API testing: calibration, demos, stress tests | Sonnet 5.5 | 0.021 | 2,000 | $42 |
| API testing: stronger-model check | Opus 5.5, $4 / $20 | 0.042 | 300 | $13 |
| API testing: Fable audit of hard cases | Fable 5.1, $10 / $50 (billed separately) | 0.14 | 250 | $35 |
| Reserve (price changes, longer prompts) | | | | $29 |
| **Total** | | | | **$200** |

Testing accounts for $90 (45% of the cap). Prices are Anthropic list prices as of Oct 22, 2026; token counts will be updated after calibration.

## 11. Timeline (Phase 1)

| Week | Work |
| --- | --- |
| 5 | Pitch; case template; rule table for the covered Listings, the age-education-work chart and SGA |
| 6 | Pipeline v1 (checklist, quote check, rules, routing); 10 calibration cases; threshold set; OSF pre-registration |
| 7 | Halfway presentation with live demo; 40 test cases written and blind-checked |
| 8 | Test run with locked settings; timed expert reviews |
| 9 | Analysis, confidence intervals, equity checks, stress tests |
| 10 | Final presentation with live demo; results against the thresholds |

## 12. Limitations

- Made-up 1–2 page cases are cleaner than real files, so Phase 1 cannot establish real-world accuracy.
- In Phase 1 the answer key and expert review are stand-ins for an expert panel.
- 40 test cases give wide intervals.
- The tool saves examiner work time, not the wait for records to arrive.
- National estimates rest on stated assumptions about hours saved and wages.

## 13. Expected contribution

- A tested design for widening SSA's fast track by reading the medical records, with approval-only routing and quoted evidence.
- The first evaluation of such a tool against an independent standard that counts eligible people who are denied.
- Reusable assets: the checklist schema, rule table, case template, pre-registration and analysis code.

## References

- Maestas, N., Mullen, K. J., and Strand, A. (2013). Does disability insurance receipt discourage work? *American Economic Review*, 103(5).
- Office of Management and Budget (2025). M-25-21, Accelerating Federal Use of AI through Innovation, Governance, and Public Trust (Apr 3, 2025). [Summary](https://www.winston.com/print/v2/content/1100706/white-house-memorandum-elaborates-on-prior-executive-order-with-requirements-for-high-impact-ai-used-by-federal-agencies.pdf)
- Social Security Administration. Commissioner's letter to Congress (Nov 24, 2025). [Link](https://www.ssa.gov/blog/en/posts/2025-11-24.html)
- Social Security Administration. Fast Track Process Public Use Files (FY2010–2023). [Link](https://www.ssa.gov/disabilityresearch/fasttrackpuf.html)
- Social Security Administration. Annual Statistical Report on the SSDI Program, 2024, Section 4. [PDF](https://www.ssa.gov/policy/docs/statcomps/di_asr/2024/sect04.pdf)
- Social Security Administration. POMS DI 23022.010. [Link](https://secure.ssa.gov/POMS.NSF/lnx/0423022010)
- Social Security Administration. FY2025 Annual Performance Plan. [PDF](https://www.ssa.gov/budget/assets/materials/2025/2025APM.pdf)
- Social Security Administration. DDS Net Accuracy. [Link](https://www.ssa.gov/data/disability-determination-services-accuracy.html)
- Social Security Administration (2017). Revisions to rules regarding the evaluation of medical evidence, 82 FR 5844. [Link](https://www.federalregister.gov/documents/2017/01/18/2017-00455/revisions-to-rules-regarding-the-evaluation-of-medical-evidence)
- SSA Office of the Inspector General. A-01-09-19030 (QDD national rollout). [Link](https://oig-files.ssa.gov/audits/full/html/A-01-09-19030.html)
- SSA Office of the Inspector General. A-15-11-11175 (QDD predictive model). [Link](https://oig.ssa.gov/assets/uploads/a-15-11-11175.pdf)
- SSA Office of the Inspector General (2025). DDS productivity and processing times. [Link](https://oig.ssa.gov/news-releases/2025-07-18-disability-determination-service%E2%80%99s-21-percent-productivity-decrease-and-81-percent-increase-in-processing-times-coincided-with-the-loss-of-key-technical-staff/)
- ACT-IAC. Intelligent Medical Language Analysis Generation (IMAGEN). [Link](https://www.actiac.org/et-use-case/intelligent-medical-language-analysis-generation-imagen)
- Health and Retirement Study. Form 831 Disability Records documentation (2022). [PDF](https://hrs.isr.umich.edu/sites/default/files/restricted_data_docs/1780502517/Form831DD2022.pdf)
- Brookdale Center for Healthy Aging (2025). SSA terminates research consortium. [Link](https://brookdale.org/news/social-security-administration-terminates-research-consortium/)
- Texas State Auditor's Office. Claims Examiner job classification and salary ranges (eff. Jul 1, 2026). [PDF](https://hr.sao.texas.gov/Compensation/JobDescriptions/1140.pdf)
