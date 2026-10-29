> **Superseded (Oct 22, 2026).** This study design describes the earlier human-only vs AI-only vs human-plus-AI comparison. The current design is in `research-proposal.md` and `README_objective.md`. Parts of this file (HRS data access, expert panel, IRB) still apply to Phase 2 of the new proposal.

# Study Design: AI-Assisted Adjudication of Initial Adult SSI/SSDI Claims

Oct 16, 2026 · Frontier

Exported from the Claude Doc: https://claude.ai/code/artifact/cfc59e9a-8dbb-4b5a-8da7-e1a9946c83e3 (the doc is the live version).

## Purpose and research questions

The study asks whether AI support, using only evidence in the file on the original decision date, can raise the accuracy of initial adult SSI/SSDI determinations against an independent expert reference standard, cut processing time, and reduce wrongful denials and group disparities. The core design choice is that **agreement with the historical decision is not accuracy**: a model that copies past examiners also copies their errors.

**Two targets, kept separate throughout**

| Target | Label | What a good score means | Used for |
| --- | --- | --- | --- |
| Decision prediction | The historical initial allowance or denial | The model reproduces what examiners did | Training signal, triage, consistency audits |
| Eligibility assessment | Blinded expert panel judgement on the same as-of-date file | The model agrees with what the rules require on that evidence | All accuracy, wrongful-denial and fairness claims |

**Research questions**

1. RQ1 (accuracy): On a stratified sample re-adjudicated by a blinded panel, how do human-only, AI-only and human-plus-AI decisions compare on overall error, wrongful-denial rate and wrongful-allowance rate?
2. RQ2 (efficiency): Can AI triage (for example, flagging likely allowances for fast-track review) reduce examiner review burden and time-to-decision without increasing panel-judged errors?
3. RQ3 (fairness): Do error rates, especially wrongful denials, differ across age, sex, race/ethnicity where available, state, primary impairment category and representation status, and does AI support narrow or widen those gaps?
4. RQ4 (method): How much of any apparent gain survives once the comparison uses the panel standard rather than the historical label, and once leakage and selection bias are controlled?

**Primary hypothesis (pre-registered).** Human-plus-AI lowers the panel-judged wrongful-denial rate relative to human-only, with a non-inferiority margin on wrongful allowances. AI-only is a comparator, not a proposed deployment.

**Scope.** Initial-level determinations only (not reconsideration, ALJ hearings or continuing disability reviews), adults 18 and over, Title II (SSDI) and Title XVI (SSI) disability claims. The unit of analysis is the claim, judged on evidence dated on or before the initial determination date. Track 1 uses HRS data, so its decision-prediction results cover applicants aged about 50 and over; the panel track (Track 2) covers all adults.

## Data sources and access

No verified public or restricted SSA file contains the claimant's medical evidence, so the study runs on two tracks: structured restricted data for decision prediction, and a separately sourced case-file sample for the expert panel. Every source in the first table was opened and checked on 2026-10-16; anything I could not confirm is in the second table and marked inferred.

**Verified sources**

| Source | What it gives the study | Label | Access (as checked) |
| --- | --- | --- | --- |
| [DAF Restricted Access File](https://ssa.gov/disabilityresearch/daf.html), DAF22 application file ([variable list](https://ssa.gov/disabilityresearch/documents/daf/DAF22-V04-List-of-Variables.pdf)) | Claim-level filing date, first initial determination date and result, regulation basis code, primary and secondary diagnosis, body system, state, county, field office | Historical decision | SSA staff, grantees, contractors, federal partners; outside researchers mainly via the RDRC. Stretch extension only, if access reopens. Denials appear to be included (a "denials only" earnings field exists); confirm in the file documentation |
| [DAF Public Use File](https://ssa.gov/disabilityresearch/daf_puf.html) | 10% sample, beneficiaries only, masked dates | None usable (no denials) | Listed as "currently unavailable for download" |
| [HRS Form 831 Disability Records](https://hrs.isr.umich.edu/sites/default/files/restricted_data_docs/1780502517/Form831DD2022.pdf) | SSA initial medical determinations for 4,576 HRS respondents through the 2022 wave, linkable to years of pre-filing survey health, function and work data | Historical decision | HRS restricted-data agreement, Virtual Desktop recommended. **Chosen primary structured source (obtainable)** |
| [SSA 831 Disability File, SIPP extract](https://sap.nsf.gov/dataset/doc_census-315/metadata/identification) | 831 determinations linked to SIPP respondents by Census PIK | Historical decision | Census-held restricted file |
| [SSA State Agency Monthly Workload Data](https://www.ssa.gov/disability/data/ssa-sa-mowl.htm) | Initial receipts, determinations, allowances and allowance rates by state and month, Oct 2000 onward, SSDI/SSI/concurrent split | Aggregate | Public CSV |
| [Combined Disability Processing Time](https://www.ssa.gov/open/data/Combined-Disability-Processing-Time.html) | Mean days from filing to notice for initial claims, monthly, FY2008 onward | Aggregate | Public CSV |
| [DDS Net Accuracy](https://www.ssa.gov/data/disability-determination-services-accuracy.html) ([CSV](https://www.ssa.gov/data/DDS-Net-Accuracy.csv)) | SSA's own quality-review accuracy for initial determinations, by state and nationally, FY2007 onward; national 97.1% (±0.26) in FY2022 | Aggregate | Public CSV (last updated June 2023) |
| [Compassionate Allowances list](https://www.ssa.gov/compassionateallowances) | 314 conditions as of the [Aug 11, 2026 release](https://www.ssa.gov/news/en/press/releases/2026-08-11.html) | Rule | Public |
| [QDD rollout audit, OIG A-01-09-19030](https://oig-files.ssa.gov/audits/full/html/A-01-09-19030.html) | SSA's existing predictive triage: about 3.3% of claims selected, 93% of a 575-case sample allowed, mean 18 days to medical determination | Benchmark | Public |
| [POMS DI 22001.001](https://secure.ssa.gov/poms.nsf/lnx/0422001001) | The five-step sequential evaluation that the rule-based model and the panel protocol encode | Rule | Public |

**Access risk.** SSA [terminated all six RDRC centers on Feb 20, 2025](https://brookdale.org/news/social-security-administration-terminates-research-consortium/), and the centers appealed. I could not confirm the outcome, so the DAF restricted route is kept only as a stretch extension.

**Case-file routes for the expert panel (inferred, not verified)**

| Route | Why it might work | What to check first |
| --- | --- | --- |
| Closed client files from a legal aid office or law-school disability clinic, with client consent | Advocates hold the full medical record and the initial notice; both approvals and denials exist among their clients | IRB approval, consent form, whether files show the initial-date evidence separately from later additions |
| A state DDS research partnership under an SSA data agreement | Gives the actual as-of-date electronic folder | Whether SSA currently approves outside research access; likely slow |
| Constructed vignettes written from the Listings and POMS, then panel-adjudicated | Fully under the student's control; no PII | Only tests eligibility reasoning on designed cases, not real-world accuracy; state that limit plainly |

The recommended default is the HRS route for Track 1, and the team adopted it on Oct 16, 2026 because it is obtainable. Track 2 uses clinic files, with vignettes as the fallback if no partner signs on by the end of month 2.

## Reference standard: blinded expert panel

Eligibility is judged by an independent panel that re-adjudicates each sampled case from the evidence dated on or before the original initial determination date, blind to the historical outcome, the model output and, where the file allows, demographic identifiers.

**Sample.** Draw the panel set from Track 2 case files, stratified by historical outcome (allowed and denied in equal numbers, so both wrongful denials and wrongful allowances are measurable), body system and program (SSDI, SSI, concurrent). Record each case's sampling probability so every estimate can be reweighted to the source population. Set the final n after a 20-case pilot measures review time; plan for roughly 150 to 250 cases as a working range for a master's budget.

**Evidence freeze.** Before review, a non-panel research assistant removes every document dated after the initial determination date and every trace of the decision (notice, rationale, examiner notes, later appeal material). A second assistant audits a random 10% of folders for missed post-date material.

**Panel.** Three reviewers with disability adjudication expertise (for example, a former DDS examiner or medical consultant, a disability attorney or advocate, and a physician). Recruiting these profiles is an assumption to confirm with the advisor. Each reviewer works alone first, following the POMS sequential evaluation.

**What each reviewer records**

| Field | Values |
| --- | --- |
| Determination | Eligible · Not eligible · Insufficient evidence to decide |
| Step that decides it | 1 to 5 of the sequential evaluation |
| Confidence | 1 to 5 |
| Missing evidence | Free text: what a competent examiner should have requested |
| Minutes spent | Number |

**Preserving uncertainty.** "Insufficient evidence" is kept as its own class, because the right action there is to develop the record, and scoring it as either allowance or denial would hide examiner and model failures to ask for evidence. Disagreement is kept, not resolved away: store all three independent ratings, then hold a consensus discussion and store that label separately. Report Fleiss' kappa and Gwet's AC1 for agreement, and run every headline analysis three ways: consensus label, majority vote, and soft labels (the share of reviewers saying eligible).

**Secondary signal.** The later appeal outcome is recorded but never used as the reference standard, because appeals add evidence and a different decision-maker.

## Models and comparison arms

Three model families are trained on historical decisions, tuned on a held-out validation split, then frozen before anyone sees the panel set; six arms are then scored on the same panel cases.

**Models**

| Model | Inputs (all dated on or before the decision) | Why it is here |
| --- | --- | --- |
| Rule-based | Compassionate Allowances match, listing-level rules on diagnosis codes, age and vocational-grid factors, earnings above the substantial gainful activity level | Transparent floor; mirrors SSA's existing CAL and QDD screening |
| Penalized logistic regression | Structured features: age, program, body system and diagnosis at the initial level, earnings history, state; in Track 1 also pre-filing HRS health and function measures | Interpretable, well calibrated, strong baseline |
| Gradient-boosted trees | Same features as the regression | Tests whether nonlinearity adds anything |
| Optional text model (Track 2 only) | Information extracted from the frozen case file by a locally run language model, fed into the regression | Tests whether file content beats structured codes; run locally so no claimant data leaves the secure environment |

Race, ethnicity and sex are excluded as features and used only for the fairness audit.

**Arms scored against the panel**

| Arm | How it is produced |
| --- | --- |
| Human-only (historical) | The actual DDS initial determination |
| Human-only (study readers) | Trained readers decide each frozen case without AI |
| AI-only | Each model's thresholded output, threshold fixed on validation data |
| Human-plus-AI, advisory | The same readers decide with the model's score and top reasons shown |
| Human-plus-AI, triage | Cases above a high-confidence allow threshold are fast-tracked with a light check; the rest get full reader review |
| Rule-based screen plus human | CAL and listing hits fast-tracked, rest to reader |

**Reader study design.** Readers are recruited with adjudication training (an assumption: likely law students or paralegals trained on POMS, since current DDS examiners may not be available). Use a randomized crossover: each reader sees each case once with AI and once without, at least four weeks apart, with order counterbalanced. Analyse with mixed-effects logistic regression, with random effects for reader and case. The historical DDS arm and the study-reader arm are both reported, because readers are not examiners.

## Outcomes and evaluation

The primary outcome is the panel-judged wrongful-denial rate, compared between human-only and human-plus-AI on the same cases; every other metric is secondary and reported for all arms.

| Outcome | Definition (against the panel label unless noted) | Analysis |
| --- | --- | --- |
| Wrongful-denial rate (primary) | Denied among cases the panel judges eligible, i.e. 1 − recall for eligibility | Paired: McNemar test and mixed-effects model; non-inferiority on wrongful allowances |
| Wrongful-allowance rate | Allowed among cases the panel judges not eligible | Same |
| Overall error | Full 3 × 2 confusion matrix, with "insufficient evidence" cases reported as a separate row | Weighted by inverse sampling probability |
| Recall, specificity, PPV | Standard, for the eligible class | Bootstrap 95% CIs |
| Calibration | Brier score, calibration slope and intercept, reliability curve, overall and per subgroup | Model arms only |
| Agreement with history | Accuracy and AUC against the historical decision | Reported to show the gap between the two targets, never as accuracy |
| Review burden | Share of cases sent to full review, flags per case, reader minutes per case | Reader study logs |
| Processing time | Reader minutes per case, plus a simulation of days-to-decision using SSA's public processing-time series as the baseline | Labelled as simulated; the study cannot observe real queue time |
| Subgroup performance | Wrongful-denial rate, calibration and recall by age band (18–49, 50–54, 55+ to match the vocational grid; Track 1 has only the two older bands), sex, race and ethnicity where recorded, program, body system, state and representation | Gap and ratio to the best-off group, with CIs; groups under 30 panel cases flagged as underpowered |

**Fairness criterion.** The main fairness test is equal opportunity: whether eligible claimants in each group face the same wrongful-denial rate, and whether AI support narrows or widens that gap relative to human-only.

**Pre-registration.** Register the primary outcome, margins, thresholds, subgroups and analysis code on OSF before the panel set is unblinded.

## Threats to validity

The largest threat is a model that looks accurate because it learned the historical decision or post-decision information; the controls below target that first.

**Leakage**

- Use only fields fixed at the initial level. In the DAF application file, the "final" diagnosis and body-system fields (FINRPDX, FINBS) and the regulation basis code can be set by or after the decision, so they are excluded unless documentation shows an initial-level, pre-decision value.
- Drop field office, county and examiner identifiers from the main model, since they can encode local leniency; test them only in a sensitivity run.
- In Track 1, use HRS waves completed before the filing date only.
- Split by person (claimants can file more than once) and by time: train on earlier filing years, test on later years.
- Freeze the case file at the decision date and audit the freeze (see the panel section).

**Selection and label bias**

- Historical decisions carry examiner variation: [Maestas, Mullen and Strand (2013)](https://hcp.hms.harvard.edu/publication/does-disability-insurance-receipt-discourage-work-using-examiner-assignment-estimate) used differences in examiner allowance rates as an instrument, which shows the label depends partly on who decided. A decision-prediction model inherits that noise.
- HRS covers adults aged about 50 and over, so Track 1 cannot speak to younger claimants. This is stated as a scope limit up front; evidence on younger claimants comes only from the panel track.
- Clinic files over-represent denied, appealing and represented claimants. Stratified sampling plus reweighting corrects the outcome mix, but not who seeks help.
- Technical denials (non-medical) are excluded throughout, as in SSA's processing-time series.

**Measurement and design**

- The panel is a better standard, not ground truth; disagreement and "insufficient evidence" bound how precise any claim can be.
- Readers in the crossover may show automation bias or learn cases; the washout and counterbalancing reduce but do not remove this.
- Rules change over time (for example, SSA's 2017 revision of the medical-evidence rules, from memory, to verify). The panel applies the rules in force on each decision date.

**Limitations to state up front.** The study cannot measure real queue time, cannot claim deployability, and generalizes only to the claim types and states in the sample. IRB approval, consent for case files and a secure enclave are preconditions, not afterthoughts.

## Feasibility plan

The study fits a nine-month master's timeline if case-file access is settled by the end of month 2; if it is not, Track 2 switches to panel-adjudicated vignettes and the rest of the plan holds.

*Timeline (drawn as a diagram in the Claude Doc): case-file access decides the design by the end of month 2.*

| Phase | Months | Work |
| --- | --- | --- |
| Approvals and access | 1 to 2 | IRB submission; HRS restricted-data agreement; clinic or DDS outreach; OSF pre-registration |
| Build and train | 3 to 4 | Track 1 data build; leakage audit; train three models; panel pilot, 20 cases |
| Panel and readers | 5 to 7 | Evidence freeze; blinded panel review; reader crossover with 4-week washout |
| Analysis, write-up | 8 to 9 | Unblind panel labels; primary and subgroup analyses; thesis draft |

Gates: **end of month 2**, case files secured? (if not, switch Track 2 to vignettes); **end of month 4**, models frozen before any panel label; **end of month 7**, panel complete with agreement reported.

Track 1 (HRS) can start as soon as the restricted-data agreement is signed, so model work does not wait on the panel.

**Fallbacks**

| If this fails | Do this instead | What is lost |
| --- | --- | --- |
| No case-file partner | Constructed vignettes from the Listings and POMS, panel-adjudicated | Real-world accuracy; keeps the method and the human-plus-AI comparison |
| HRS agreement delayed | Build and test the pipeline on public aggregates and synthetic records, swap in HRS later | Time, not design |
| Too few expert reviewers | Two reviewers plus a third only on disagreement | Some precision on agreement statistics |
| Too few readers | Drop the study-reader arms; compare AI-only against historical decisions on the panel set | The human-plus-AI comparison, the core of RQ1 |

**Reproducibility.** Keep all code, the feature dictionary, the panel protocol and the pre-registration in one version-controlled repository; release a synthetic dataset with the same schema so others can run the pipeline without restricted data.

## Sources

All pages below were opened on 2026-10-16. Items marked inferred in the text (case-file routes, panel and reader profiles, the 2017 rule revision) were not verified and need checking before the proposal is submitted.

- SSA, [Disability Analysis File restricted access file](https://ssa.gov/disabilityresearch/daf.html) and [DAF22 list of variables](https://ssa.gov/disabilityresearch/documents/daf/DAF22-V04-List-of-Variables.pdf)
- SSA, [DAF Public Use File](https://ssa.gov/disabilityresearch/daf_puf.html)
- SSA, [Disability research data and surveys](https://ssa.gov/disabilityresearch/data_surveys.htm)
- Health and Retirement Study, [Form 831 Disability Records documentation](https://hrs.isr.umich.edu/sites/default/files/restricted_data_docs/1780502517/Form831DD2022.pdf)
- NSF Standard Application Process, [SSA 831 Disability File SIPP extract](https://sap.nsf.gov/dataset/doc_census-315/metadata/identification)
- SSA, [State Agency Monthly Workload Data](https://www.ssa.gov/disability/data/ssa-sa-mowl.htm)
- SSA, [Combined Disability Processing Time](https://www.ssa.gov/open/data/Combined-Disability-Processing-Time.html)
- SSA, [DDS net accuracy](https://www.ssa.gov/data/disability-determination-services-accuracy.html) and [CSV](https://www.ssa.gov/data/DDS-Net-Accuracy.csv)
- SSA, [Compassionate Allowances](https://www.ssa.gov/compassionateallowances) and [Aug 11, 2026 press release](https://www.ssa.gov/news/en/press/releases/2026-08-11.html)
- SSA OIG, [National Rollout of Quick Disability Determinations, A-01-09-19030](https://oig-files.ssa.gov/audits/full/html/A-01-09-19030.html)
- SSA POMS, [DI 22001.001 Sequential Evaluation of Adult Disability Claims](https://secure.ssa.gov/poms.nsf/lnx/0422001001)
- Brookdale Center, [SSA terminates research consortium](https://brookdale.org/news/social-security-administration-terminates-research-consortium/)
- Maestas, Mullen and Strand, "Does Disability Insurance Receipt Discourage Work?", *American Economic Review* 103(5), 2013 ([summary](https://hcp.hms.harvard.edu/publication/does-disability-insurance-receipt-discourage-work-using-examiner-assignment-estimate))
