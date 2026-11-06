from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header

page_header("About and method")

st.header("The design in plain language")
st.markdown("""
1. **Collect.** The case file arrives as it does today: the application, the claimant's disability report (SSA-3368)
   and the medical records the state agency requested. Each document is tagged with **who wrote it** and **how it
   arrived**. The AI never decides that.
2. **Read.** An AI model (Gemini 3.7 Flash, locked for the test) fills a fixed checklist. Every item must quote the
   file word for word and give the page. It never sees the rules and never judges eligibility.
3. **Verify.** Code checks that every quote really is on the cited page. Quotes that aren't found are dropped.
   Only findings from an **acceptable medical source**, in records the agency requested from a provider the claimant
   listed, can count toward a rule (the source rule and the provenance check).
4. **Rules.** Code applies SSA's own rules: Listings 11.08 (spinal cord), 13.14 (lung cancer), 6.03 (dialysis) and the
   medical-vocational grid. One setting was tuned on calibration: how many medical documents must support each
   finding (k = 1, locked).
5. **Route.** If one path is fully met and nothing is flagged, the claim goes to the **fast track**, where an examiner
   checks the quotes and signs. Everything else goes to the **human queue**, with the evidence that supports
   approval. **There is no path that denies.**
""")

st.header("The claim we will test")
st.markdown("""
- At least **15%** of claims fast-tracked, at least **95%** of fast-tracked claims eligible, and **0** denials made
  by the AI.
- Tested **once** on 40 locked simulated test cases, after the plan is posted on OSF. The ±11-point confidence
  interval at n = 40 is said out loud.
- Compared with today's form-based fast tracks (QDD and CAL, about 8.3% of claims) and with examiners working without
  the tool.
""")

st.header("Out of scope")
st.markdown("""
- **Applying for benefits.** Help with the application itself is SOAR's job, not this tool's.
- **Appeals** (reconsideration, hearings).
- **Denials.** The tool can only send a claim to the fast track or to a person.
- **Real applicant data.** Every case here is simulated.
""")

st.header("Known limits")
st.markdown("""
- **I-15:** k = 2 can't be tested on our data. No fast-track case has two medical-source records stating the key
  finding, so k = 1 was chosen because the data can't tell the two apart.
- **I-16:** calibration covers 8 of the 15 test categories. The other 15 test cases (thin records, grid "not
  disabled", not severe and others) were never seen in calibration.
- **I-17 (fixed Nov 5):** calibration was stable over 3 runs at k = 1 (same route for all 10 cases). Stability on the
  test set is still unknown.
- **I-18:** the reader changed from Claude Sonnet 5.5 (pitch) to Gemini 3.7 Flash, because no Anthropic API account
  was ready in time. Same prompt, checklist and rules. Other models become a robustness check.
- **Answer keys** were written with AI help and are being blind-checked by two teammates per case.
- **Simulated cases are cleaner than real files.** Real files are 50 to 500 pages, often scanned or faxed.
- **Mental-health claims always go to a person** (the B criteria need judgment), which caps the fast-track rate.
""")

st.header("Next steps")
st.markdown("""
- A bigger case set, including records with two medical sources per finding (so k = 2 can be tested).
- Scanned and faxed records, read page by page.
- Gaming defences: source tiers and more adversarial cases from the discussant team.
- Equity check: fast-track rate and recall for physical vs. mental claims.
- A design for reading SSA's electronic claim folder directly (no access is assumed).
""")

st.header("Team")
st.markdown("Team 06 · Frontier · SEL_POL 425: Xinhui Zong, Yanqi Wu, Yihang Ye, Yiling Long, Yixuan Wen, "
            "Zhiying Cui.")
st.caption("Built with AI assistance (Claude); see the team's weekly AI logs.")
