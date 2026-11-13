"""PREVIEW backend: used when no Google Sheet is configured (no Secrets).

Same interface as assign.py + data.py. Arms are drawn at random (not the real
allocation) and rows go to a temp folder on the server, never to the Sheet. In preview
anyone may add ?arm=ai or ?arm=noai to the URL to see a group.
"""
from __future__ import annotations

import json
import random
import secrets
import tempfile
from pathlib import Path

from assign import CASE_IDS, TEST_PREFIX, is_test, start_timer, stop_timer  # noqa: F401
from data import RESPONSE_COLUMNS, SaveError, now  # noqa: F401

IS_STUB = True
_OUT = Path(tempfile.gettempdir()) / "frontier_study_preview"
_OUT.mkdir(exist_ok=True)


def _append(table: str, row: dict) -> None:
    with open(_OUT / f"{table}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def configured() -> bool:
    return False


def test_key() -> str | None:
    return None


def new_participant_id(test: bool = False) -> str:
    return (TEST_PREFIX if test else "P") + secrets.token_hex(4)


def case_order(participant_id: str) -> list[str]:
    order = CASE_IDS[:]
    random.shuffle(order)
    return order


def assign(participant_id, lang, training_attempts, heard, forced_arm=None):
    return forced_arm or random.choice(["ai", "noai"]), case_order(participant_id)


def restore(participant_id: str) -> None:
    return None  # preview keeps no progress across refreshes


def write_response(row: dict) -> None:
    _append("responses", {k: row.get(k) for k in RESPONSE_COLUMNS})


def write_contact(participant_id: str, name: str, email: str) -> None:
    _append("contacts", {"participant_id": participant_id, "name": name, "email": email})


def write_participant(participant_id: str, lang: str, background: dict) -> None:
    _append("participants", {"participant_id": participant_id, "lang": lang, **background})


def write_training(participant_id: str, attempts: int, passed: bool) -> None:
    _append("training", {"participant_id": participant_id, "attempts": attempts, "passed": passed})


def write_survey(participant_id: str, arm: str, answers: dict, lang: str = "") -> None:
    _append("survey", {"participant_id": participant_id, "arm": arm, "lang": lang, **answers})
