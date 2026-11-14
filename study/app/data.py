"""Data layer for the participant study (Group C, ZXH).

Storage: Supabase Postgres (`database_url` in Secrets, see pg_sheet.py) — the team's choice,
since a Google account is not available. Google Sheets still works if `sheet_id` +
`gcp_service_account` are given instead. Either way the data is organised as "tabs":

Tabs (created with headers by `sheet_admin.py setup`):

    responses         one row per submitted case (HANDOFF.md section 3.5, exact columns)
    contacts          name + email, only for the lottery; never joined into responses
    allocation        pre-generated blocked randomisation (slot, block, arm); 200 rows
    assignments       one row per participant who passed training; its row number is the slot
    participants      welcome-page background answers
    training          qualification-test outcome (attempts, passed)
    survey            wrap-up answers as JSON
    test_assignments  team test runs (forced group); never uses an allocation slot

Credentials live only in Streamlit Secrets (or .streamlit/secrets.toml, which is gitignored):

    database_url = "postgresql://postgres.<ref>:<password>@<host>.pooler.supabase.com:5432/postgres"
    test_key = "<a word only the team knows>"      # unlocks the forced-group test switch

Every write is retried with backoff. A write that still fails raises SaveError and the
page keeps the participant where they are, so nothing is silently lost.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone

RESPONSE_COLUMNS = [
    "participant_id", "lang", "arm", "case_id", "case_order", "answer", "confidence",
    "seconds", "started_at", "submitted_at", "training_attempts", "heard_about_study",
]

TABS: dict[str, list[str]] = {
    "responses": RESPONSE_COLUMNS,
    "contacts": ["participant_id", "name", "email", "written_at"],
    "allocation": ["slot", "block", "arm"],
    "assignments": ["participant_id", "arm", "case_order", "lang", "training_attempts",
                    "assigned_at"],
    "participants": ["participant_id", "lang", "experience", "written_at"],
    "training": ["participant_id", "attempts", "passed", "written_at"],
    "survey": ["participant_id", "arm", "lang", "answers_json", "written_at"],
    "test_assignments": ["participant_id", "arm", "case_order", "lang", "training_attempts",
                         "assigned_at"],
}


class SaveError(RuntimeError):
    """A write to the Sheet failed after all retries."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------- connection ----------------

def _secrets():
    import streamlit as st
    return st.secrets


def configured() -> bool:
    """True when a Sheet is set up (Secrets) or a local test sheet is in use."""
    if os.environ.get("STUDY_LOCAL_SHEET") or os.environ.get("STUDY_DATABASE_URL"):
        return True
    try:
        s = _secrets()
        return "database_url" in s or ("sheet_id" in s and "gcp_service_account" in s)
    except Exception:  # no secrets file at all
        return False


def test_key() -> str | None:
    try:
        return str(_secrets().get("test_key") or "") or None
    except Exception:
        return os.environ.get("STUDY_TEST_KEY") or None


_BOOK = None
_WS: dict = {}


def _book():
    global _BOOK
    if _BOOK is None:
        local = os.environ.get("STUDY_LOCAL_SHEET")
        db = os.environ.get("STUDY_DATABASE_URL")
        if not (local or db):
            try:
                db = str(_secrets().get("database_url") or "") or None
            except Exception:
                db = None
        if local:  # offline development and automated tests only
            import local_sheet
            _BOOK = local_sheet.open_book(local)
        elif db:  # Supabase / any Postgres
            import pg_sheet
            _BOOK = pg_sheet.open_book(db)
        else:
            import gspread
            s = _secrets()
            gc = gspread.service_account_from_dict(dict(s["gcp_service_account"]))
            _BOOK = gc.open_by_key(str(s["sheet_id"]))
    return _BOOK


def ws(name: str):
    if name not in _WS:
        _WS[name] = _retry(lambda: _book().worksheet(name))
    return _WS[name]


def _retry(fn, tries: int = 5):
    delay = 1.0
    for i in range(tries):
        try:
            return fn()
        except Exception as e:  # network, quota (429), 5xx
            if i == tries - 1:
                raise SaveError(f"{type(e).__name__}: {e}") from e
            time.sleep(delay)
            delay *= 2


def _append(tab: str, row: dict) -> int:
    """Append one row in the tab's column order. Returns the sheet row number written."""
    cols = TABS[tab]
    values = ["" if row.get(c) is None else row.get(c) for c in cols]
    res = _retry(lambda: ws(tab).append_row(values, value_input_option="RAW",
                                             insert_data_option="INSERT_ROWS",
                                             table_range="A1"))
    rng = (res or {}).get("updates", {}).get("updatedRange", "")  # e.g. "assignments!A7:G7"
    try:
        return int("".join(ch for ch in rng.split("!")[-1].split(":")[0] if ch.isdigit()))
    except ValueError:
        return -1


def _rows(tab: str) -> list[dict]:
    values = _retry(lambda: ws(tab).get_all_values())
    if not values:
        return []
    head = values[0]
    return [dict(zip(head, r)) for r in values[1:]]


# ---------------- writes (interface used by app.py) ----------------

def write_response(row: dict) -> None:
    """One row per submitted case, written immediately. Keys = HANDOFF 3.5 columns only."""
    _append("responses", {k: row.get(k) for k in RESPONSE_COLUMNS})


def write_contact(participant_id: str, name: str, email: str) -> None:
    """Lottery only."""
    _append("contacts", {"participant_id": participant_id, "name": name, "email": email,
                         "written_at": now()})


def write_participant(participant_id: str, lang: str, background: dict) -> None:
    _append("participants", {"participant_id": participant_id, "lang": lang, **background,
                             "written_at": now()})


def write_training(participant_id: str, attempts: int, passed: bool) -> None:
    _append("training", {"participant_id": participant_id, "attempts": attempts,
                         "passed": "yes" if passed else "no", "written_at": now()})


def write_survey(participant_id: str, arm: str, answers: dict, lang: str = "") -> None:
    _append("survey", {"participant_id": participant_id, "arm": arm, "lang": lang,
                       "answers_json": json.dumps(answers, ensure_ascii=False),
                       "written_at": now()})


# ---------------- allocation ----------------

def claim_slot(row: dict, test: bool = False) -> int:
    """Append to `assignments`; the row number is this participant's slot (1-based).

    Appends are applied one at a time by Google, so two people arriving at once get
    different rows: no lock needed. Test runs go to `test_assignments` and use no slot.
    """
    tab = "test_assignments" if test else "assignments"
    r = _append(tab, row)
    return r - 1 if r > 1 else -1


def allocation_arm(slot: int) -> str | None:
    """Arm in row `slot` of the pre-generated allocation table, or None if out of range."""
    for r in _allocation():
        if str(r.get("slot")) == str(slot):
            arm = (r.get("arm") or "").strip()
            return arm if arm in ("ai", "noai") else None
    return None


_ALLOC: list[dict] | None = None


def _allocation() -> list[dict]:
    global _ALLOC
    if not _ALLOC:  # read once per server process; the table never changes
        _ALLOC = _rows("allocation")
    return _ALLOC


def set_assignment_arm(slot: int, arm: str) -> None:
    """Fill the arm into the participant's assignments row (column B), for convenience."""
    try:
        _retry(lambda: ws("assignments").update_cell(slot + 1, 2, arm), tries=3)
    except SaveError:
        pass  # the allocation table is authoritative; this copy is only for reading ease


# ---------------- reads used to resume after a page refresh ----------------

def find_rows(tab: str, participant_id: str) -> list[dict]:
    return [r for r in _rows(tab) if r.get("participant_id") == participant_id]


def count_responses(participant_id: str) -> int:
    col = _retry(lambda: ws("responses").col_values(1))
    return sum(1 for v in col[1:] if v == participant_id)
