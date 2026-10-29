# Follow-up 01: The Initial Claim Process and What Our Tool Reads

Responds to instructor feedback #1: "go through the application form and process in full to determine exactly what needs to be filled in."
Team 06 · Frontier · drafted 2026-10-24 by Claude (Opus 5.5) for team review.
Sources: the blank forms in `SSI_SSDI_Forms/` (SSA-16 09-2025, SSA-8000 09-2024, SSA-3368 06-2024, SSA-3369 07-2026, SSA-3373 10-2026, SSA-827 06-2024) and the filled Farnsworth packet in `SOAR sample/`. Process steps follow 20 CFR 404.1520 / 416.920 (the five-step sequential evaluation). Items marked **[check]** should be confirmed against POMS before the halfway presentation.

---

## 1. Summary

- An initial adult claim passes through two offices. The **field office** takes the application and decides the non-medical questions. The **state DDS** (disability examiner + medical consultant) decides the medical question. Our tool sits only at the DDS, after the medical records arrive.
- Of the six forms, the tool needs content from four: SSA-3368 (most of it), SSA-16 (a few items), SSA-3369 and SSA-3373 (when the DDS requests them). It reads nothing from the SSA-8000's income and resource sections, and SSA-827 is only an authorization.
- **The medical records themselves are not an SSA form.** They are the main input, and our made-up cases need them most. The README in `SSI_SSDI_Forms/` already says this.
- One design point changes: the field office already screens out people working above the substantial gainful activity (SGA) level at Step 1, so "Joe, still working" normally never reaches our tool. The tool's Step 1 check is a re-check, not the main screen.

## 2. The process, step by step

| # | Stage | Who | What happens | Forms | Our tool? |
| --- | --- | --- | --- | --- | --- |
| 1 | Apply | Claimant (often helped by a SOAR worker, family or rep) | Files online, by phone or at the field office | SSA-16 (SSDI) and/or SSA-8000 (SSI), SSA-3368, SSA-827; SSA-1696 if a rep is appointed | No |
| 2 | Non-medical review | Field office | SSDI: insured status (work credits). SSI: income, resources, living arrangements. Both: **Step 1, is the person working above SGA?** If yes, the claim is denied here and never goes to the DDS. **[check: POMS DI 10501 / SI 00501]** | SSA-16 Q13–16, SSA-8000 Parts 1–4, SSA-3368 §4 | No |
| 3 | Intake at DDS | DDS system | QDD model and CAL condition matching run on the electronic application; flagged claims are expedited | SSA-3368 §3 (conditions) feeds CAL | No (this is the existing fast track we compare against) |
| 4 | Evidence gathering | DDS examiner | Requests records from every provider in SSA-3368 §8, using SSA-827. May send SSA-3373 and SSA-3369 to the claimant. May buy a consultative exam (CE) if records are thin | SSA-827, SSA-3373, SSA-3369 | No |
| 5 | **Records arrive** | | | Medical evidence of record (MER), CE report, third-party letters (e.g. a SOAR Medical Summary Report) | **Our tool runs here:** Collect → Read → Score → Route |
| 6 | Medical decision, Steps 2–5 | Examiner + medical consultant | Step 2 severe and lasting 12 months; Step 3 meets or equals a Listing; Steps 4–5 residual functional capacity, past work (last 5 years), other work using age, education and the grid | All of the above | Fast track: examiner confirms the checklist and signs. Human queue: full review with the AI's evidence for approval |
| 7 | Notice | DDS / SSA | Allowance or denial notice | | No |
| 8 | Appeals | Claimant | Reconsideration, then ALJ hearing | SSA-561, SSA-3441, HA-501 (in the SOAR sample) | **Out of scope** |

## 3. Field map: what the tool reads from each form

"Can satisfy a rule?" means whether a value from this source can, by itself, count toward a Listing or a fast-track decision. Under 20 CFR 404.1521 / 416.921, an impairment must be shown by objective medical evidence from an acceptable medical source; the claimant's own statement of symptoms or a diagnosis is not enough. This is also our main defense against gaming (see follow-up 02).

### SSA-3368-BK, Adult Disability Report (15 pages, 12 sections)

| Section | Contains | Tool reads? | Used for | Can satisfy a rule? |
| --- | --- | --- | --- | --- |
| §1 About you | Name, SSN, address, contact, other names | No (masked in the course build) | Identity only | — |
| §2 Contacts | Someone who knows about the conditions | No | — | — |
| §3 Medical information | 3.A list of conditions; 3.B–C height, weight | **Yes** | Tells the tool which Listings to check; height and weight for BMI | **No.** A routing hint only |
| §4 Work activity | 4.A working now? 4.C date stopped and why; 4.D–G work changes, months over $1,550 | **Yes** | Step 1 re-check; onset date; consistency with SSA-16 | Only as a stop: "currently working above SGA" sends the case to a human |
| §5 Education, training, literacy | Highest grade, special education, training, reading and writing English | **Yes** | Education category for the grid (Step 5) | Yes, for the grid's education factor |
| §6 Work history | Jobs in the 5 years before becoming unable to work; hours, pay | **Yes** | Past relevant work (Step 4); skill and exertion level for the grid | Yes, for the grid's work factor |
| §7 Medicines | Name, prescriber, reason | **Yes** | Cross-check that treatment exists and who prescribed it | No, supporting only |
| §8 Medical treatment | Each provider: facility, doctor, conditions, first and last visit; tests | **Yes** | **Records index:** which records should exist. Used for completeness and provenance checks | No, but a record that is missing from §8, or a §8 provider with no records, is a flag |
| §9 Other medical information | Other organizations with records (VA, workers' comp, prisons…) | Partly | Flags other record sources | No |
| §10 Support services | Only for people already on SSI | No | — | — |
| §11 Remarks | Free text | Yes, as a claimant statement | Context; scanned for instructions aimed at the AI | **No** |
| §12 Who completed it | Claimant or someone else | **Yes** | Tags whether statements are first-person or third-party | — |

### SSA-16, Application for Disability Insurance Benefits (SSDI)

| Item | Tool reads? | Used for |
| --- | --- | --- |
| Q4 date of birth | **Yes** | Age category for the grid |
| Q8 date the condition became severe enough to stop work | **Yes** | Alleged onset date; must be consistent with SSA-3368 §4 and the records |
| Q14–16 employers and earnings this year and last year | **Yes** | Step 1 re-check |
| Q17 still unable to work? | Yes | Duration check |
| Citizenship, marriage, children, other countries, direct deposit, railroad | No | Field office only |

### SSA-8000, Application for SSI (24 pages)

| Part | Tool reads? | Why |
| --- | --- | --- |
| Part 1 basic eligibility (name, DOB, filing date) | DOB and filing date only | Age; timing |
| Part 2 living arrangements, Part 3 resources, Part 4 income, Part 5 SNAP and other benefits | **No** | SSI financial eligibility is decided by the field office before the DDS sees the claim. The tool takes it as already passed |
| Part 7 remarks | Yes, as a claimant statement | Context only |

### Other documents

| Document | Tool reads? | Notes |
| --- | --- | --- |
| SSA-827 authorization | No content | Only confirms records were requested from providers. Supports the provenance rule in follow-up 02 |
| SSA-3369 Work History Report | **Yes, if present** | Physical and mental demands of each past job (Steps 4–5) |
| SSA-3373 Function Report | **Yes, if present** | Daily activities and limits in the claimant's words. Goes into the "evidence for approval" list for the human queue. Cannot satisfy a Listing alone. The SOAR checklist notes it is only needed when there is no Medical Summary Report |
| **Medical evidence of record** (office notes, imaging, labs, discharge summaries, psychiatric evaluations) | **Yes, primary source** | Every checklist value that counts toward a Listing must quote one of these, with the page |
| Consultative exam report | **Yes** | Written by an acceptable medical source paid by the DDS |
| SOAR Medical Summary Report and other third-party letters | Yes, weighted | Narrative from a case worker. Only the parts written or signed by an acceptable medical source (in the Farnsworth MSR, the psychiatrist's quoted findings) can count. The rest is supporting context |
| SSA-1696, SSA-1699, SSA-3288 | No | Representative and release forms |
| SSA-561, SSA-3441, HA-501 | No | Appeals, out of scope |

## 4. What each made-up case must contain (case-file template)

Based on the map above, each of the 50 cases needs these parts. The pitch says "1–2 pages each"; this template is 2–4 pages. The team should decide whether to keep the 1–2 page target by shortening the records, or update the README.

```
case-XX/
  answer-key.md          ← never shown to the tool
  01_application.md      ← ½ page
  02_SSA-3368.md         ← 1 page
  03_records/            ← 1–3 short record excerpts
    r1_<provider>.md
    r2_<provider>.md
  04_SSA-3373.md         ← optional
  05_SSA-3369.md         ← optional
  06_third-party.md      ← optional (MSR-style letter)
```

**01_application** (from SSA-16 or SSA-8000): claim type (SSDI, SSI or concurrent); date of birth; filing date; alleged onset date (SSA-16 Q8); earnings this year and last year (SSA-16 Q16). State that the field office's non-medical review has been passed.

**02_SSA-3368**: §3 conditions as the claimant wrote them (this is where gaming cases plant keywords); §4 working now / date stopped / why; §5 highest grade and special education; §6 jobs in the last 5 years with hours; §7 medicines and prescriber; §8 every provider with dates; §12 who completed the form.

**03_records**: each excerpt has a header with provider name and credential (MD, DO, PhD psychologist, etc.), facility, visit date and page number. Content: history, exam findings, test results, diagnosis, plan. Every provider in §8 should have a record, unless the case is meant to test a missing record.

**answer-key**: correct outcome (allow / deny / needs more evidence); basis (e.g. "meets 11.08A", "grid rule 201.14", "not severe, Step 2"); should it be fast-tracked (yes/no); the key evidence with page numbers; category (clear / uncertain / ineligible / adversarial); author; blind checker 1 and 2 and whether they agreed.

## 5. Worked example: the Farnsworth sample through the map

| Map item | What the packet says | Tool's reading |
| --- | --- | --- |
| Claim type | SSA-8000 and SSA-16 both filed 01/17/2017 | Concurrent claim |
| Age | DOB 9/1/1962, age 54 | "Closely approaching advanced age" (50–54) for the grid |
| §3 conditions | "Schizophrenia, chronic undifferentiated type" | Check Listing 12.03 |
| Self-reported conditions (MSR) | Leukemia, cerebral palsy, polio, tumors, "Franchrascicon Broyde" cysts; the MSR says no provider has confirmed them | **Must not count.** No acceptable-medical-source record supports them |
| §4 work | Stopped 09/01/2014 because of conditions | Consistent with SSA-16 Q8 (9/1/2014). Step 1 re-check passes |
| §5 education | 10th grade, special education | "Limited" education for the grid |
| §6 work history | Shelf stocker (drug store, discount store), part-time | Unskilled work |
| §7 medicines | Risperdal (for schizophrenia); Chlortrimeton and Theragran "to treat brain tumors" | Risperdal confirms treatment. The other two reflect delusional beliefs, not a confirmed condition |
| §8 providers | Holy Cross Mobile Treatment (03–05/2016, psychotic disorder NOS); Union Hospital, Dr. Sagamore (10–12/2016, schizophrenia) | Records index: two providers, records expected from both |
| Acceptable-medical-source evidence | Dr. Sagamore's mental status exam: "thought processes were quite disorganized, circumstantial, tangential"; no insight; judgment impaired; recommends a representative payee | Counts toward 12.03 A criteria; B criteria need examiner judgment |
| Data problem | MSR dated 01/17/2017 describes appointments in March and April 2017 | Date-consistency flag → human |

**Likely route: human queue**, with an evidence-for-approval list (the psychiatrist's quoted findings, repeated loss of contact with treatment, decompensation about every 90 days). Mental Listings need judgment on the four functional areas, which the README rules reserve for a person. This makes Farnsworth a good **calibration or stress case**: a correct tool will not fast-track on the self-reported cancers, and will still surface the real evidence for approval.

## 6. Decisions for the team

1. Confirm the "tool reads" column above.
2. Decide whether Step 1 is a re-check only (recommended, since the field office already does it), and update slide 4/5's "Joe, still working" line to match.
3. Keep the 1–2 page case target or accept 2–4 pages.
4. Decide whether to use a Farnsworth-style case (rewritten with new names, not the original) in calibration or in the stress set.
