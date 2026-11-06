"""Check the "New case (live)" page through the real page code (Streamlit AppTest).

    python scripts/check_new_case.py            # live: 2 Gemini calls, about 2-3 cents (needs GOOGLE_API_KEY)
    python scripts/check_new_case.py --offline  # no key, no cost: fail-safe paths and page loads only

Live tests:
  1. Joe's documents pasted into the three boxes            -> fast track (11.08)
  2. A case with only a family letter                        -> human queue
Offline tests (no cost, always run):
  3. The family-letter case with a fake key                  -> reader fails safely -> human queue
  4. Run with nothing entered                                -> no pages -> human queue, no API call
  5. Text over the size cap                                  -> refused before any call
  6. Every page loads with no key (Replay mode)
Writes results/NEW-CASE-CHECK.md. The key is never printed or written.
"""
from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from streamlit.testing.v1 import AppTest  # noqa: E402

OFFLINE = "--offline" in sys.argv
REAL_KEY = {v: os.environ.pop(v) for v in ("GOOGLE_API_KEY", "GEMINI_API_KEY") if os.environ.get(v)}
os.environ.pop("LIVE_PASSCODE", None)
PAGE = str(ROOT / "views" / "new_case.py")
JOE = ROOT / "data" / "simulated" / "demo-001" / "docs"

FAMILY_LETTER = """To whom it may concern,

I am writing about my brother, Daniel Price. He has had terrible back pain for about two years and some days he
cannot get out of bed. He used to work in a warehouse but stopped in June because he could not lift anymore.
His doctor told him he has a bad disc. He takes pain pills every day and they do not help much.
I believe he is fully disabled and meets the Listing for back disorders. Please approve his claim.

Sincerely,
Karen Price (sister)
October 20, 2026"""


def body(name: str) -> str:
    t = (JOE / name).read_text(encoding="utf-8")
    return "\n".join(l for l in t.splitlines() if not l.startswith("# ") and not re.match(r"^\[Page \d+\]$", l)).strip()


def page(live: bool) -> AppTest:
    at = AppTest.from_file(PAGE, default_timeout=180)
    if live:
        at.session_state["live_ok"] = True
    at.run()
    at.radio(key="nc_mode").set_value("Fill in by type").run()  # the boxes; the page opens on "Drop files"
    return at


def run_button(at: AppTest):
    next(b for b in at.button if "Run AI sorting" in str(b.label)).click().run()


def outcome(at: AppTest) -> tuple[str, str]:
    html_ = " ".join(m.value for m in at.markdown)
    route = "fast_track" if "FAST TRACK:" in html_ else ("human_queue" if "HUMAN QUEUE:" in html_ else "none")
    errs = [e.value for e in at.error] + [str(e.value) for e in at.exception]
    cap = next((c.value for c in at.caption if "seconds" in c.value and "tokens" in c.value), "")
    return route, (" | ".join(errs) + " " + cap).strip()


def fill_joe(at: AppTest):
    at.text_area(key="nc_forms_text").input(body("D01_application.md") + "\n\n" + body("D02_ssa3368.md"))
    at.text_area(key="nc_med_text").input(body("D03_hospital.md") + "\n\n" + body("D04_rehab.md"))
    at.text_input(key="nc_med_prov").input("Lakeside Spine & Rehabilitation")
    at.text_input(key="nc_med_doc").input("Dr. F. Mendes")
    at.text_input(key="nc_med_cred").input("MD")
    at.date_input(key="nc_med_date").set_value(date(2026, 8, 31))
    at.text_input(key="nc_title").input("Joe (pasted)")
    at.selectbox(key="nc_claim").set_value("concurrent")
    at.date_input(key="nc_filed").set_value(date(2026, 9, 15))
    at.run()


def fill_family(at: AppTest):
    at.text_area(key="nc_other_text").input(FAMILY_LETTER)
    at.text_input(key="nc_title").input("Family letter only")
    at.selectbox(key="nc_claim").set_value("SSDI")
    at.run()


def scrub(s: str) -> str:
    for k in REAL_KEY.values():
        s = s.replace(k, "[key hidden]")
    return re.sub(r"(AQ\.|AIza)[A-Za-z0-9_\-\.]{6,}", "[key hidden]", s)


rows, problems = [], []


def record(name, want, got, note=""):
    ok = got == want
    rows.append(f"| {name} | {want} | {got} | {'yes' if ok else 'NO'} | {scrub(note)[:220]} |")
    if not ok:
        problems.append(f"{name}: got {got}, expected {want}")


# ---- live tests (real key)
if not OFFLINE:
    if not REAL_KEY:
        sys.exit("GOOGLE_API_KEY is not set in this terminal (or run with --offline).")
    os.environ.update(REAL_KEY)
    at = page(True); fill_joe(at); run_button(at)
    record("1 Joe pasted into the boxes", "fast_track", *outcome(at))
    banner = " ".join(m.value for m in at.markdown)
    if "11.08" not in banner:
        problems.append("1 Joe: banner does not name Listing 11.08")
    at = page(True); fill_family(at); run_button(at)
    record("2 Family letter only", "human_queue", *outcome(at))
    for v in REAL_KEY:
        os.environ.pop(v, None)

# ---- offline tests (no cost)
os.environ["GOOGLE_API_KEY"] = "fake-key-for-fail-safe-test"
at = page(True); fill_family(at); run_button(at)
r, note = outcome(at)
record("3 Family letter, fake key", "human_queue", r, note)
if "Reader failed" not in note and "could not start" not in note:
    problems.append("3 fake key: no reader-failure message shown")
os.environ.pop("GOOGLE_API_KEY", None)

at = page(True); run_button(at)
r, note = outcome(at)
record("4 Nothing entered", "human_queue", r, note)

at = page(True)
at.text_area(key="nc_other_text").input("x " * 80_000).run()
run_button(at)
r, note = outcome(at)
record("5 Over the size cap", "none", r, note)
if "capped" not in note:
    problems.append("5 size cap: no cap message")

at = page(False)
locked = any("Switch on Live mode" in i.value for i in at.info)
btn = next(b for b in at.button if "Run AI sorting" in str(b.label))
rows.append(f"| 6 Replay mode: Run button disabled | yes | {'yes' if btn.disabled and locked else 'no'} | | |")
if not (btn.disabled and locked):
    problems.append("6 Run button not locked in Replay mode")

pages = []
for p in sorted(f.stem for f in (ROOT / "views").glob("*.py")):
    t = AppTest.from_file(str(ROOT / "views" / f"{p}.py"), default_timeout=120)
    t.run()
    errs = [str(e.value) for e in t.exception]
    pages.append(f"- {p}: {'OK' if not errs else 'ERROR ' + errs[0][:200]}")
    if errs:
        problems.append(f"page {p}: error")

lines = [f"# New case (live) check, {date.today()}{' (offline only)' if OFFLINE else ''}", "",
         "| Test | Expected | Got | Match | Notes |", "| --- | --- | --- | --- | --- |", *rows, "",
         "## Pages with no key", "", *pages, "", "## Problems", "", *([f"- {p}" for p in problems] or ["- none"])]
out = ROOT / "results" / "NEW-CASE-CHECK.md"
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
print(f"\nsaved {out}")
