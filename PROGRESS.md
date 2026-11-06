# Progress

Newest first.

## 2026-11-05
- **AI reader: Gemini 3.7 Flash on Google Cloud.** The reader moved from Claude Sonnet 5.5 to Gemini 3.7 Flash through Vertex AI. The prompt, checklist, quote check and rules are unchanged. This model is locked for the test run; other models will be a robustness check.
- **First real reader runs.** All three demo cases routed correctly. On the 10 calibration cases at k = 1, all routes were correct: 6 were fast-tracked, all correctly, all 137 quotes were verified, and the AI denied no one. None of the 7 gaming attempts in the stress set reached the fast track.
- **Limits found in review.** k = 2 can't be tested on this data. Calibration covers 8 of the 15 test categories. Stability over repeated runs is not yet checked.

## 2026-10-29
- **Realistic simulated cases.** Medical records now state the same finding in different ways, use abbreviations and mixed date formats, and include routine content around the key lines. Added near-miss cases that look eligible but aren't: a spinal cord injury under 3 months old, temporary dialysis, and sedentary limits at age 47.

## 2026-10-24
- **Prototype platform.** It covers import connectors, the AI reader with an offline baseline, quote verification, the source rule, a rule table (Listings 11.08, 13.14 and 6.03, plus the medical-vocational grid), routing, and the examiner review panel with timed decisions. It also measures the AI routing and compares human-only with human + AI.
- **Simulated data set.** 61 cases with answer keys: 3 demo, 10 calibration, 40 test, and 8 gaming attempts.
- **Safeguards against gaming.** The source rule, provenance check, consistency check and instruction scan each send a suspicious case to a human.

## Next
- Re-run calibration to check stability, then run the 40 test cases once.
- Report the test results with confidence intervals, by category.
- Time examiner decisions with and without AI assistance.
