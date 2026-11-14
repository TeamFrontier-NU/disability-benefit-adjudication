"""Random assignment, case order and timing (Group C, ZXH).

Assignment: the n-th person who passes the qualification test gets row n of the
pre-generated `allocation` tab (blocks of 2: one ai, one noai, order random within the
block). The slot is claimed by appending to `assignments`, so it is given exactly once and
never changes. Team test runs (forced group) go to `test_assignments` and use no slot.
"""
from __future__ import annotations

import random
import secrets
import time
from datetime import datetime, timezone

import data as D

CASE_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]
TEST_PREFIX = "TEST-"


def new_participant_id(test: bool = False) -> str:
    """Random id, the only identifier in `responses`. Team test runs start with TEST-."""
    return (TEST_PREFIX if test else "P") + secrets.token_hex(4)


def is_test(participant_id: str) -> bool:
    return participant_id.startswith(TEST_PREFIX)


def case_order(participant_id: str) -> list[str]:
    """C1..C6 shuffled independently for each participant."""
    order = CASE_IDS[:]
    random.SystemRandom().shuffle(order)
    return order


def assign(participant_id: str, lang: str, training_attempts: int, heard: str,
           forced_arm: str | None = None) -> tuple[str, list[str]]:
    """Called once, when the test is passed. Returns (arm, case order) and records both."""
    order = case_order(participant_id)
    row = {"participant_id": participant_id, "arm": forced_arm or "",
           "case_order": ",".join(order), "lang": lang,
           "training_attempts": training_attempts,
           "assigned_at": D.now()}
    if forced_arm:  # team test run
        D.claim_slot(row, test=True)
        return forced_arm, order
    slot = D.claim_slot(row)
    arm = D.allocation_arm(slot) if slot > 0 else None
    if arm is None:  # allocation table used up or unreadable: fall back, still balanced in expectation
        arm = random.SystemRandom().choice(["ai", "noai"])
    D.set_assignment_arm(slot, arm)
    return arm, order


def restore(participant_id: str) -> dict | None:
    """Rebuild progress after a page refresh. None if the id is unknown."""
    who = D.find_rows("participants", participant_id)
    if not who:
        return None
    p = who[0]
    out = {"lang": p.get("lang") or "en", "heard": "",
           "arm": None, "order": None, "attempts": None, "done": 0,
           "failed": False, "passed": False, "survey_done": False}
    tr = D.find_rows("training", participant_id)
    if any(r.get("passed") == "no" for r in tr):
        out["failed"] = True
        return out
    passed = [r for r in tr if r.get("passed") == "yes"]
    if passed:
        out["passed"] = True
        out["attempts"] = int(passed[0].get("attempts") or 1)
    tab = "test_assignments" if is_test(participant_id) else "assignments"
    rows = D._rows(tab)
    for i, r in enumerate(rows):
        if r.get("participant_id") == participant_id:
            arm = r.get("arm") or (D.allocation_arm(i + 1) if tab == "assignments" else None)
            out.update(arm=arm, order=r["case_order"].split(","),
                       attempts=int(r.get("training_attempts") or 1))
            break
    if out["arm"]:
        out["done"] = D.count_responses(participant_id)
        out["survey_done"] = bool(D.find_rows("survey", participant_id))
    return out


def start_timer() -> dict:
    """When a case is first shown."""
    return {"t0": time.time(), "started_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def stop_timer(token: dict) -> tuple[float, str, str]:
    """On submit: (seconds, started_at, submitted_at)."""
    secs = round(time.time() - token["t0"], 1)
    return secs, token["started_at"], datetime.now(timezone.utc).isoformat(timespec="seconds")
