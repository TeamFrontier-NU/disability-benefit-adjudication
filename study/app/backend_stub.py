"""PLACEHOLDER backend, used only until ZXH's data.py and assign.py exist.

app.py calls exactly these functions. ZXH: implement the same names and
signatures in study/app/data.py and study/app/assign.py and the app will use
them automatically (it imports those first and falls back to this file).

Nothing here is the real allocation: arms are drawn with an unseeded RNG and
rows go to a local temp file that is never committed.
"""
from __future__ import annotations

import json
import random
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

IS_STUB = True
CASE_IDS = ["C1", "C2", "C3", "C4", "C5", "C6"]
_OUT = Path(tempfile.gettempdir()) / "frontier_study_stub"
_OUT.mkdir(exist_ok=True)


def _append(table: str, row: dict) -> None:
    with open(_OUT / f"{table}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ---------------- assign.py interface ----------------

def new_participant_id() -> str:
    """Short random id; the only identifier written to `responses`."""
    return "P" + uuid.uuid4().hex[:8]


def assign_arm(participant_id: str) -> str:
    """Return 'ai' or 'noai'. Real version: next unused row of the allocation sheet, locked."""
    return random.choice(["ai", "noai"])


def case_order(participant_id: str) -> list[str]:
    """Random order of C1..C6 for this participant."""
    order = CASE_IDS[:]
    random.shuffle(order)
    return order


def start_timer() -> dict:
    """Called when a case is first shown."""
    return {"t0": time.monotonic(), "started_at": datetime.now(timezone.utc).isoformat()}


def stop_timer(token: dict) -> tuple[float, str, str]:
    """Called on submit. Returns (seconds, started_at, submitted_at)."""
    secs = round(time.monotonic() - token["t0"], 2)
    return secs, token["started_at"], datetime.now(timezone.utc).isoformat()


# ---------------- data.py interface ----------------

RESPONSE_COLUMNS = [
    "participant_id", "lang", "arm", "case_id", "case_order", "answer", "confidence",
    "seconds", "started_at", "submitted_at", "training_attempts", "heard_about_study",
]


def write_response(row: dict) -> None:
    """One row per submitted case, written immediately. Keys = HANDOFF 3.5 columns."""
    _append("responses", {k: row.get(k) for k in RESPONSE_COLUMNS})


def write_contact(participant_id: str, name: str, email: str) -> None:
    """Lottery only. Never joined into `responses`."""
    _append("contacts", {"participant_id": participant_id, "name": name, "email": email})


def write_participant(participant_id: str, lang: str, background: dict) -> None:
    """Welcome-page background answers (major, medical/SSA experience).
    OPEN QUESTION for ZXH: HANDOFF 3.5 has no table for these yet."""
    _append("participants", {"participant_id": participant_id, "lang": lang, **background})


def write_survey(participant_id: str, arm: str, answers: dict) -> None:
    """Wrap-up survey answers. OPEN QUESTION for ZXH: no table in HANDOFF 3.5 yet."""
    _append("survey", {"participant_id": participant_id, "arm": arm, **answers})
