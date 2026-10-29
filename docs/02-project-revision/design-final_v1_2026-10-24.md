# Final Design v1: Record-Based Fast-Track Screening

Team 06 · Frontier · drafted 2026-10-24 by Claude (Opus 5.5) for team review
Status: **proposed final design.** Update 2026-10-24: the prototype in `03 Platform` uses 13.14 (lung; an earlier draft wrongly said 13.13) and 6.03 (dialysis) as the two extra Listings. Once the team agrees, this replaces §3–§5 of `01 Proposal & Pitch/README_objective.md` as the build spec. Nothing here changes the recorded pitch's claim (≥ 15% / ≥ 95% / 0 AI denials).
Builds on `followup-01_application-process-and-field-map.md` and `followup-02_safeguards-against-gaming.md`. Items marked **[check]** need confirming against the SSA Listings or POMS before cases are written.

---

## 1. What changed since the pitch

Each change has to be reported at the halfway presentation (the rubric asks what changed since the pitch and why).

| # | Change | Why | Effect on the claim |
| --- | --- | --- | --- |
| D1 | **Source rule:** only quotes from acceptable-medical-source (AMS) records can count toward a Listing or the grid | Instructor feedback #2 (gaming); 20 CFR 404.1521 | None. It makes precision ≥ 95% easier to defend |
| D2 | **Step 1 is a re-check.** The field office already screens out people working above SGA, so the test mix reflects claims that reach the DDS | Feedback #1 (the real process) | The "working above SGA" cases move from the 40 test cases to the stress set |
| D3 | **Four new checks:** source tag, provenance, consistency, instruction scan (plus repeat filing as an option) | Feedback #2 | Can only move claims to the human queue |
| D4 | **Gaming stress set** (8 cases), reported separately, with a new measure: gaming robustness | Feedback #2; halfway and final adversarial-input criteria | New secondary measure |
| D5 | **Mental Listings always go to the human queue**, with evidence for approval | The B criteria (four functional areas) need judgment | Lowers the possible fast-track rate; equity gap reported (RQ5). A real uncertainty for the halfway presentation |
| D6 | **Case files follow the real forms** (template in follow-up 01, §4) | Feedback #1 | Cases grow from 1–2 to about 2–4 pages; AI cost per case still about 4–6¢ |

## 2. Pipeline (final)

```
Collect ──► Read ──► Verify ──► Score ──► Route ──► Decide
 (docs)    (LLM)    (code)     (rules)   (code)    (human)
```

| Step | Done by | Input | Output | Safeguards |
| --- | --- | --- | --- | --- |
| 1 Collect | Code | Case folder: application, SSA-3368, records, optional SSA-3373 / SSA-3369 / third-party letter | Page-numbered document set, each document tagged with author, credential, source type and how it was received | **C3 provenance**: a record from a provider who is not in SSA-3368 §8, or one handed in by the claimant, is marked "not fast-track eligible" |
| 2 Read | LLM (Sonnet 5.5) | Document set + fixed checklist schema | Checklist JSON: every field has value, verbatim quote, document, page | **C5 instruction scan**: a second short prompt flags text that addresses the AI or gives orders. The LLM never sees the rules or the threshold |
| 3 Verify | Code | Checklist + documents | Each quote is marked verified or dropped (fuzzy string match on the cited page) | Quote check (pitch R2); **C1 source tag** is attached from the document's metadata, not from the LLM |
| 4 Score | Code (rule table, §4) | Verified AMS-sourced fields only | For each covered rule path: met / not met / missing, with the fields used | **C2 findings, not labels**: diagnosis-only or "meets Listing" statements don't satisfy a criterion. **C4 consistency**: onset dates, record dates, conditions vs. records |
| 5 Route | Code | Rule results + flags | **Fast track** or **human queue**, with reasons | Fast track only if all of §5 holds. No code path outputs "deny" |
| 6 Decide | Examiner | Panel view | Fast track: confirm quotes and sign. Human queue: full review with the checklist and evidence for approval | Random audit of fast-tracked claims (scaling plan) |

## 3. Checklist schema (what the LLM fills)

Every field is an object: `{value, quote, doc_id, page}`. A field the LLM can't find is `null`. It is never guessed.

| Group | Fields | Main source |
| --- | --- | --- |
| Claimant | age at filing, claim type, alleged onset date | Application (SSA-16 Q4, Q8 / SSA-8000 Part 1) |
| Work | currently working, months over SGA since onset, stopped date and reason | SSA-16 Q14–16, SSA-3368 §4 |
| Vocational | education level, special education, past jobs in last 5 years with exertional level and skill | SSA-3368 §5–6, SSA-3369 |
| Alleged conditions | conditions as listed by the claimant | SSA-3368 §3 (routing hint only) |
| Diagnoses | each diagnosis with date and diagnosing provider | AMS records |
| Listing findings | the criteria fields for each covered Listing (§4), e.g. "unable to stand from seated", "disorganized motor function in two extremities" | AMS records, CE |
| Duration | earliest documented date of the finding; expected to last 12 months? | AMS records |
| Function | sit / stand / walk / lift limits; AMS-stated RFC if any | AMS records, CE |
| Treatment | providers, visits, medicines, gaps | SSA-3368 §7–8, records |
| Evidence for approval | quotes that support eligibility, from any source, labelled by source | All |
| Missing evidence | records a careful examiner would request | SSA-3368 §8 vs. documents received |

## 4. Rule table (covered paths for the course build)

Proposed: three physical Listings + one grid path + mental Listings to the human queue. Exact criteria to be copied from the current Listings before cases are written **[check]**.

| Path | Fast-track rule (all must be verified AMS findings) | Typical case |
| --- | --- | --- |
| **11.08 Spinal cord disorders** | (A) complete loss of function lasting 3 months after the injury, or (B) disorganized motor function in two extremities causing extreme limitation in standing, balancing, or using the arms, lasting 3 months **[check]** | Joe |
| **13.14 lung cancer** (used in the prototype; team can swap) | Documented histology/type plus the qualifying stage feature (e.g. small-cell, or inoperable/unresectable/recurrent/metastatic non-small-cell) **[check]** | Cancer cases (note: many of these are already CAL, so they show overlap with today's fast track) |
| **6.03 kidney disease on chronic dialysis** (used in the prototype; team can swap) | Chronic hemodialysis or peritoneal dialysis documented by the treating nephrologist **[check]** | Dialysis cases |
| **Grid (medical-vocational) path** | Age ≥ 50 **and** AMS-stated RFC of sedentary or less **and** education "limited" or "high school, no direct entry into skilled work" **and** unskilled past work or no transferable skills → rules 201.09 / 201.10 / 201.12 / 201.14 direct "disabled" **[check]** | Older manual workers with documented limits |
| **12.03 / 12.04 mental Listings** | **Never fast-tracked** (D5). Human queue with A-criteria evidence and functional quotes | Farnsworth-style case |
| Anything else | Human queue | Peter |

**The one tuned setting (calibration):** how many independent AMS documents must support each required criterion (1 or 2). Set on the 10 calibration cases, then locked.

## 5. Routing rule

A claim goes to the **fast track** only if all of these are true:

1. Step 1 re-check passes (no current work above SGA).
2. One covered path in §4 is fully met, using verified AMS quotes only.
3. Duration is met.
4. No consistency flag (C4), no instruction flag (C5), no provenance flag on a supporting record (C3).
5. Every supporting quote is verified.
6. The locked support requirement (1 or 2 AMS documents per criterion) is met.

Otherwise the claim goes to the **human queue**, and the panel shows which condition failed. The tool never produces "deny" or "not disabled".

## 6. Evaluation (unchanged claim, updated sets)

| Set | Cases | Mix | Use |
| --- | --- | --- | --- |
| Calibration | 10 | Mixed, includes one Farnsworth-style and one hidden-instruction case | Tune prompts and the support setting, then lock and post on OSF |
| Test | 40 | About 15 eligible (≈ 7 Listing, ≈ 6 grid, ≈ 2 other incl. mental) and 25 not eligible (non-severe, can still work, thin records). **No above-SGA cases** (D2) | Run once; primary claim |
| Stress | 8 | S1–S8 from follow-up 02 (keyword stuffing, hidden instruction, fake record, narrative only, check-box opinion, Farnsworth-style, honest control, above-SGA) | Gaming robustness; reported separately |

Primary measures: fast-track rate ≥ 15%, fast-track precision ≥ 95%, AI denials = 0. Secondary: recall, field accuracy, quote verification rate, evidence-for-approval recall, equity gap (physical vs. mental), gaming robustness, honest-control false alarms. Wilson 95% CIs.

**Honest note for the halfway presentation:** with D5 (mental always human) and only about 13 of 40 cases on a fast-track-eligible path, the maximum possible fast-track rate is about 13/40 = 33%, and 15% means fast-tracking at least 6 cases. The ±11-point CI means even a true 15% may not clear the bar. That is worth saying out loud.

## 7. Product (format decision pending)

Recommended: **an examiner review panel**, a local web app that runs the pipeline live. The same code also runs the 40-case batch evaluation.

| Screen | Shows |
| --- | --- |
| Queue | Case list with route badges (fast track / human queue) and flag icons |
| Case view | Left: the documents, page by page, with every quoted line highlighted and colored by source type (AMS / claimant / third party). Right: checklist with verified ✓ / dropped ✗ per field |
| Rule panel | Which path was tested, each criterion met / not met / missing, and the fields that met it |
| Route card | Fast track or human queue, the failed conditions, evidence for approval. Fast track has a "confirm and sign" button. **There is no deny button** |
| Flags | Instruction scan hits, consistency conflicts, provenance warnings |
| Live test box | Paste or upload an extra document (for the discussant team's adversarial input) and re-run |
| Results | Batch evaluation: measures with CIs, by set |

Proposed stack: Python, Streamlit for the panel, the Claude API (Sonnet 5.5) for Read and the instruction scan, plain-Python rules, cases as Markdown files with page markers, a saved-run cache so the demo still works if the network fails, and logs of every run for the AI log.

## 8. Consistency watch-list (keep these aligned in every later file)

| Item | Current value | Where it appears |
| --- | --- | --- |
| Claim | ≥ 15% fast-tracked, ≥ 95% precision, 0 AI denials | Slide 5, script, README §4, proposal §2 |
| Case counts | 50 = 10 calibration + 40 test (+ 8 stress, new) | Slide 5, README §5, proposal §5 |
| Test mix | ≈ 15 eligible / 25 not; no above-SGA cases (new, D2) | Proposal §5.1 still lists "working above SGA" in the 25. **Update** |
| Budget | $200; testing $90 | Slide 7, script, proposal §10 |
| Terms | fast track, human queue, checklist, answer key, evidence for approval | README §9 |
| Model | Sonnet 5.5 for running; Opus 5.5 and Fable 5.1 for checks | Slide 7, proposal §10 |
| Deck file | `pitch/Design-Pitch_Frontier.pptx` (v11) | README §10 still says v10. **Update** |

## 9. Decisions for the team

1. Agree D1–D6.
2. Choose the cancer Listing and the third physical Listing in §4.
3. Accept "mental Listings always go to the human queue" (D5), or allow 12.x fast track with a stricter rule. Good halfway "least sure" decision.
4. Product format (decision card in the thread).
