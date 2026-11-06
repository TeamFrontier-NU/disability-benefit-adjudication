from __future__ import annotations

import streamlit as st

from frontier_ui.common import page_header

page_header("Questions", "Answers to the questions we expect.")

QA = {
    "Randomization and the evaluation": [
        ("How does randomizing the application forms help you evaluate the product?",
         "**Randomizing the cases makes the test fair.** Each simulated claim comes from a randomly drawn profile "
         "(age, condition, work history, wording, typos). We can’t hand-pick easy cases, and the AI can’t pass by "
         "matching templates: our first keyword baseline scored 61/61 on fixed templates but 27/40 on varied "
         "wording. The calibration/test split is random too, with a recorded seed, so we can’t tune on the cases we "
         "report.\n\n**Randomizing who uses the tool gives the counterfactual.** Volunteers are randomly split into "
         "two groups; each reviews one random block with the AI and the other without. Every volunteer works under "
         "both conditions and every case is seen both ways by different volunteers, so differences come from the "
         "tool rather than from the cases or the people."),
        ("Who will you test it on?",
         "The routing: simulated claim files only, since a course project can’t use real applicant data. The "
         "examiner study: 3–6 classmates after a short training, a pilot of the procedure. With a state partner "
         "later: real files in a secure environment."),
        ("Why a crossover instead of two separate groups?",
         "With so few volunteers, two separate groups would differ by chance in skill and speed. In a crossover each "
         "volunteer works under both conditions, and each case is reviewed under both by different volunteers "
         "(never twice by the same person). Randomizing the order handles learning and fatigue."),
        ("Are 40 test cases enough?",
         "For the fast-track rate they give a usable but wide interval (about 7–29% around 15%). For precision they "
         "are too few: a perfect 13 of 13 only shows about 77%. We plan a larger set enriched with fast-track "
         "cases to estimate precision; the rate is still measured on the representative mix."),
        ("Your repository is public. Can’t people see the test answers?",
         "The 40 test answer keys are in old commits of our public repository. The AI never sees them, but a person "
         "could. Before we freeze the plan we will draw a fresh test set (part of growing to ~200 cases) and keep its "
         "keys out of the repository, so the reported test is on cases nobody has looked at."),
        ("How do you know the answer keys are right?",
         "Each key comes from the case’s fixed profile, not from an AI reading. Two teammates who didn’t write a "
         "case decide it blind; we report agreement and label disagreements as borderline."),
    ],
    "Fraud": [
        ("Won’t applicants game the AI once they know how it works?",
         "Applicants can submit their own evidence, and the examiner sees all of it. But in our design only records "
         "from verified providers can support an automated fast-track recommendation; that is our conservative "
         "rule, not an SSA requirement. Text aimed at the AI is flagged. None of the 7 gaming cases we tested "
         "reached the fast track, though that doesn’t prove robustness against every attack."),
        ("What about gaming at the doctor’s office?",
         "That’s the remaining risk. We count objective findings (imaging, labs, exam results) rather than "
         "conclusions, check consistency across records, and audit fast-tracked cases at random. The age-grid path, "
         "which rests on a doctor’s opinion, gets the most scrutiny."),
        ("What if the AI invents evidence?",
         "Every finding must quote the file word for word with a page number, and code checks the quote is on that "
         "page. That catches invented text, not a real quote used for the wrong conclusion, which is why an "
         "examiner reviews every recommendation."),
    ],
    "Other concerns": [
        ("Wouldn’t QDD/CAL already catch some of these, like lung cancer?",
         "Yes, some overlap is expected. In use, the tool screens only claims QDD/CAL did not pick, so nothing is "
         "counted twice. Our next case set will mark which cases CAL would flag, so we count only the claims the "
         "tool adds."),
        ("Does a fast-track recommendation actually shorten waits?",
         "Not automatically: real waiting time also depends on when records arrive and on examiners’ workloads. "
         "The class pilot measures review time per case; processing time needs real process data."),
        ("Why can’t the tool deny claims too?",
         "A wrong fast-track is caught when the examiner checks it. A wrong denial falls on someone who may be "
         "seriously ill and can take months to reverse. Denials stay with people."),
        ("Won’t examiners just rubber-stamp the AI?",
         "Every finding shows its quote and page so checking is quick, fast-tracked cases are audited at random, and "
         "the examiner pilot measures accuracy with and without the tool."),
        ("Most real records are scans. Does it still work?",
         "In a small trial a clean scan read perfectly; fax-quality OCR lost some dates and words. Most such errors "
         "send a case to a person rather than onto the fast track. Testing this properly is a next step."),
        ("Why Gemini?",
         "Its API was accessible to us and inexpensive. The prompt, checklist and rules don’t depend on the model, "
         "and we plan to compare other models on the same test set."),
        ("What about privacy and real medical data?",
         "We use no real data. A real deployment would run inside SSA’s or the state’s secure systems, under HIPAA "
         "and federal security rules."),
    ],
}
for group, items in QA.items():
    st.subheader(group)
    for q, a in items:
        with st.expander(q):
            st.markdown(a)
