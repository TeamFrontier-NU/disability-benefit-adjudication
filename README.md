# AI-Assisted Fast-Track Screening for Initial SSI/SSDI Disability Claims

Team Frontier · Fall 2026

**Research question.** Can record-based AI screening widen the fast track for initial adult SSI/SSDI claims without lowering accuracy, measured against an independent expert standard?

**The idea.** SSA's current fast tracks (QDD and Compassionate Allowances) read only the application form, and they fast-track 8.3% of claims (FY2023). Our tool reads the medical records, fills a fixed checklist where every item quotes the file and gives the page, and applies SSA's own rules. Claims that clearly qualify go to a fast track for quick human sign-off. Every other claim goes to a human examiner, together with the evidence that supports approval. **The AI never denies anyone.**

**Pre-registered claim.** At least 15% of claims fast-tracked, at least 95% of those confirmed eligible, and no denials made by the AI.

> All data in this repository is simulated. No real applicant data is used.

![Examiner review panel](platform/screenshot_case-review.png)

## Repository layout

| Path | What |
| --- | --- |
| [`platform/`](platform/) | The prototype: examiner review panel, import connectors, AI reader, rules, routing, metrics, simulated cases |
| [`PROGRESS.md`](PROGRESS.md) | What has been built so far |

## Quick start

```bash
cd platform
pip install -r requirements.txt
streamlit run app.py        # opens http://localhost:8501 on this computer only
```

The offline keyword reader runs with no API key; use it on the demo set only. The Claude reader needs `ANTHROPIC_API_KEY`. See [`platform/README.md`](platform/README.md).

## How it works

```
Import files ─► AI sorting ─────────────────────► Examiner review ─► Final decision
(connectors)    Read → Verify → Score → Route      (panel)            (logged, timed)
                fast track  or  human queue
```

- **Source rule:** only quotes from medical records written by an acceptable medical source can count toward a Listing. That way, writing Listing language into your own forms doesn't help.
- **Covered rule paths:** Listing 11.08 (spinal cord), 13.14 (lung cancer), 6.03 (dialysis), and the medical-vocational grid. Mental Listings always go to a human.
- **Safeguards:** quote verification, a provenance check, a consistency check, and an instruction scan against prompt injection. Each one can only move a claim to a human.
