"""Open the study app like a participant would, wake it if it sleeps, and time the load.

    pip install playwright && python -m playwright install chromium     # once
    python study/app/keep_awake.py https://frontier-estimation.streamlit.app/
    python study/app/keep_awake.py <URL> --runs 3                      # load test

Why: a free Streamlit Community Cloud app goes to sleep when nobody opens it for a while
(about 12 hours), and the next visitor waits 1-3 minutes while it boots. Participants read
that as an error and leave. The GitHub Actions workflow `.github/workflows/keep-awake.yml`
runs this script every 3 hours, so the app never sleeps; it also fails (red X in the Actions
tab) when the page takes longer than --max-seconds, so a slow app is noticed before
participants notice it.

A plain HTTP request is not enough: the app counts as used only when a browser opens it, and a
sleeping app shows a "Yes, get this app back up!" button that must be clicked.
Exit code: 0 = the language page appeared in time, 1 = it did not.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

WAKE_BUTTON = "get this app back up"
READY_TEXT = "English"  # the first button on the language page


def open_once(url: str, timeout: float) -> tuple[float | None, bool]:
    """Seconds until the language page is visible (None = not within timeout), and whether
    the app was asleep."""
    from playwright.sync_api import sync_playwright

    woke = False
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or None)
        page = browser.new_page()
        t0 = time.time()
        page.goto(url, wait_until="domcontentloaded", timeout=int(timeout * 1000))
        while time.time() - t0 < timeout:
            for frame in page.frames:  # *.streamlit.app shows the app inside an iframe
                try:
                    wake = frame.get_by_role("button", name=WAKE_BUTTON)
                    if not woke and wake.count():
                        wake.first.click()
                        woke = True
                    if frame.get_by_role("button", name=READY_TEXT).count():
                        secs = time.time() - t0
                        page.wait_for_timeout(3000)  # stay a moment: counts as a visit
                        browser.close()
                        return secs, woke
                except Exception:  # noqa: BLE001  frame navigated away while checking
                    pass
            page.wait_for_timeout(1000)
        browser.close()
    return None, woke


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--timeout", type=float, default=240, help="give up after this many seconds")
    ap.add_argument("--max-seconds", type=float, default=20,
                    help="fail if the page takes longer than this on the LAST run")
    a = ap.parse_args()
    secs, woke = None, False
    for i in range(1, a.runs + 1):
        secs, woke = open_once(a.url, a.timeout)
        state = "was asleep, woken" if woke else "was awake"
        shown = f"{secs:.1f} s" if secs is not None else f"not loaded within {a.timeout:.0f} s"
        print(f"run {i}: {shown} ({state})", flush=True)
    if secs is None:
        print("FAIL: the app did not load. Open it in a browser and check Manage app -> logs.")
        sys.exit(1)
    if woke:  # it had gone to sleep: now awake; the next scheduled run should find it awake
        print("NOTE: the app was asleep (first run after a pause or a redeploy). It is awake now.")
    elif secs > a.max_seconds:
        print(f"FAIL: the awake app took {secs:.0f} s (limit {a.max_seconds:.0f} s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
