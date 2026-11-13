"""A local stand-in for the Google Sheet, for offline development and tests only.

    STUDY_LOCAL_SHEET=/tmp/study_sheet streamlit run study/app/app.py

Each tab is a JSON file in that folder (never inside the repository). Implements only the
few gspread calls data.py uses: worksheet, append_row, get_all_values, col_values,
update_cell, update, clear.
"""
from __future__ import annotations

import fcntl
import json
from contextlib import contextmanager
from pathlib import Path


class _Sheet:
    def __init__(self, folder: Path, name: str):
        self.path = folder / f"{name}.json"
        self.title = name

    @contextmanager
    def _locked(self):
        lock = open(str(self.path) + ".lock", "w")
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            rows = json.loads(self.path.read_text()) if self.path.exists() else []
            yield rows
            self.path.write_text(json.dumps(rows, ensure_ascii=False))
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
            lock.close()

    def append_row(self, values, **_):
        with self._locked() as rows:
            rows.append([str(v) for v in values])
            n = len(rows)
        return {"updates": {"updatedRange": f"{self.title}!A{n}:Z{n}"}}

    def get_all_values(self):
        return json.loads(self.path.read_text()) if self.path.exists() else []

    def col_values(self, col: int):
        return [r[col - 1] if len(r) >= col else "" for r in self.get_all_values()]

    def update_cell(self, row: int, col: int, value):
        with self._locked() as rows:
            while len(rows[row - 1]) < col:
                rows[row - 1].append("")
            rows[row - 1][col - 1] = str(value)

    def update(self, values, range_name="A1", **_):
        with self._locked() as rows:
            rows[:] = [[str(v) for v in r] for r in values]

    def clear(self):
        with self._locked() as rows:
            rows[:] = []


class _Book:
    def __init__(self, folder: str):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)

    def worksheet(self, name: str) -> _Sheet:
        if not (self.folder / f"{name}.json").exists():
            raise KeyError(f"no tab {name!r}; run sheet_admin.py setup")
        return _Sheet(self.folder, name)

    def add_worksheet(self, title: str, rows: int = 0, cols: int = 0) -> _Sheet:
        sh = _Sheet(self.folder, title)
        sh.path.write_text("[]")
        return sh

    def worksheets(self):
        return [_Sheet(self.folder, p.stem) for p in self.folder.glob("*.json")]


def open_book(folder: str) -> _Book:
    return _Book(folder)
