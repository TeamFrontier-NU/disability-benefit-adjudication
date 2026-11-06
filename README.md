# Frontier: record-based fast-track screening for SSI/SSDI claims

Team 06 · Frontier · SEL_POL 425 · Fall 2026

**What it is.** SSA's current fast tracks (QDD and Compassionate Allowances) read only the application form and fast-track about 8% of initial disability claims. Our tool reads the **medical records**: an AI model fills a fixed checklist where every item quotes the file and gives the page, code checks every quote, and SSA's own rules decide. Claims that clearly qualify go to a **fast track**, where an examiner checks and signs. Every other claim goes to the **human queue**, with the evidence that supports approval. **The tool never denies a claim.**

> **All cases are simulated.** No real applicant data is used anywhere in this repository.

## Open the app

- **Live link:** _added once the team deploys it on Streamlit Community Cloud (see [Deploy](#deploy-on-streamlit-community-cloud))._
- A free Streamlit app goes to sleep when nobody uses it. **Open the link about 10 minutes before presenting** and press "wake up" if it asks.
- The app opens in **Replay mode**: recorded Gemini 3.7 Flash output, no key, no cost. **Live mode** (real Gemini calls) is for the presenter only and needs a passcode.

Pages: **Overview** (the idea and the headline numbers) · **Case explorer** (run Joe, Peter or any stress case step by step) · **New case (live)** (paste or upload a case you have never seen; presenter Live mode only) · **Safeguards** (gaming attempts, safeguards on vs. off, "Try to fool it") · **Results** (every saved run, with 95% confidence intervals and spend) · **About and method**.

## Run it on your own computer (backup if the Wi-Fi fails)

1. Download this repository (green **Code** button → **Download ZIP**) and unzip it, or use the team folder.
2. Open the `platform` folder and double-click:
   - **Mac:** `Start-Frontier.command`. The first time, macOS may block it: right-click it, choose **Open**, then **Open** again.
   - **Windows:** `Start-Frontier.bat`.
   - **Linux:** `bash Start-Frontier.command`.
3. The first run sets everything up (needs internet, about 2 minutes). After that it opens straight away, and Replay mode works with **Wi-Fi off**.

You need Python 3.10 or newer ([python.org](https://www.python.org/downloads/)). Nothing else.

## Current status (Nov 6, 2026)

| Set | What we found | What it means |
| --- | --- | --- |
| Calibration (10 cases), k = 1 | 10/10 routed as the answer key expects, in **each of 3 runs** (same route every time) | Settings locked; not evidence for the claim |
| Stress (8 gaming cases) | 0 of 7 gaming cases fast-tracked; the honest control was fast-tracked | Safeguards work on these cases |
| AI denials | 0 | The code has no way to deny |
| **Test set (40 cases)** | **Not run yet** | Run once, after the plan is posted on OSF |

Pre-registered claim: at least 15% of claims fast-tracked, at least 95% of those eligible, 0 AI denials. Reader: Gemini 3.7 Flash on Google Cloud (Vertex AI), changed from Claude Sonnet 5.5 on Nov 5 (issue I-18). Reader spend so far: about $0.45 at list price.

The test set's answer keys are **not** in this branch. They are kept by the team so the pre-registered test can be scored later. (Earlier commits on `main` did include them.)

## Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io), sign in with the team's GitHub account, and choose **Create app → Deploy a public app from GitHub**.
2. Repository `TeamFrontier-NU/disability-benefit-adjudication`, branch with this code, main file path **`platform/Frontier.py`**.
3. **Advanced settings:** Python 3.12. Under **Secrets**, paste (with your own values):
   ```toml
   LIVE_PASSCODE = "choose-a-passcode"
   GOOGLE_API_KEY = "your-google-cloud-key"
   ```
   Secrets stay in Streamlit; never put them in a file in the repository. Leave both out and the app still works, in Replay mode only.
4. Set a hard budget alert on the Google Cloud project first (Billing → Budgets & alerts), because Live mode spends real money (about 1¢ a case).
5. Before the first deploy, record the reader output once (next section) and commit `platform/results/reader_cache/`.

## Record the reader output for Replay mode (once)

```bash
cd platform
source .venv-app/bin/activate          # or any environment with requirements.txt installed
export GOOGLE_API_KEY=...              # never saved in a file
python scripts/build_reader_cache.py   # demo, calibration, stress + 3 attack examples; about $0.20
```

It refuses the test set. It saves one JSON file per case in `platform/results/reader_cache/`, which the app replays.

## Repository layout

| Path | What |
| --- | --- |
| `platform/Frontier.py`, `platform/views/`, `platform/frontier_ui/` | The presentation app (new) |
| `platform/app.py` | The original examiner panel (still works) |
| `platform/fasttrack/` | Reader, checklist, quote check, rules and routing. **Locked** for the test run |
| `platform/data/simulated/` | 61 simulated cases (test answer keys removed) |
| `platform/results/` | Saved batch runs and the recorded reader output |
| `platform/scripts/` | Batch runs, cost, stability, blind check, cache recording |
| [`CHANGELOG.md`](CHANGELOG.md) | What changed for the app |

## Team

Xinhui Zong, Yanqi Wu, Yihang Ye, Yiling Long, Yixuan Wen, Zhiying Cui. Built with AI assistance (Claude); see the team's weekly AI logs.
