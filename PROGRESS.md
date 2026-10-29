# Progress

Newest first.

## 2026-10-29
- **Realistic simulated cases.** Medical records now state the same finding in different ways, use abbreviations and mixed date formats, and include routine content around the key lines. Added near-miss cases that look eligible but aren't: a spinal cord injury under 3 months old, temporary dialysis, and sedentary limits at age 47.

## 2026-10-24
- **Prototype platform.** It covers import connectors, the AI reader with an offline baseline, quote verification, the source rule, a rule table (Listings 11.08, 13.14 and 6.03, plus the medical-vocational grid), routing, and the examiner review panel with timed decisions. It also measures the AI routing and compares human-only with human + AI.
- **Simulated data set.** 61 cases with answer keys: 3 demo, 10 calibration, 40 test, and 8 gaming attempts.
- **Safeguards against gaming.** The source rule, provenance check, consistency check and instruction scan each send a suspicious case to a human.

## Next
- Run the Claude reader on the calibration cases and lock the settings.
- Run the test set once and report the results with confidence intervals.
- Time examiner decisions with and without AI assistance.
