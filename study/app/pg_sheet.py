"""Postgres (Supabase) storage for the study, behind the same small "sheet" interface that
data.py and sheet_admin.py use (worksheet, append_row, get_all_values, col_values,
update_cell, update, clear). Each "tab" is a set of rows in one table:

    study_rows(tab text, id bigserial, vals text[])     -- first row of a tab = its header

Appends to one tab are serialised with a transaction-level advisory lock, so the row number
returned by append_row (used as the allocation slot) is never given to two people.
Connection string: `database_url` in Streamlit Secrets (Supabase: Session pooler URI).
"""
from __future__ import annotations

import psycopg

DDL = """
create table if not exists study_rows (
    id   bigserial primary key,
    tab  text not null,
    vals text[] not null
);
create index if not exists study_rows_tab_id on study_rows (tab, id);
alter table study_rows enable row level security;  -- no public (anon key) access at all
"""


class _Sheet:
    def __init__(self, book: "_Book", name: str):
        self.book, self.title = book, name

    def _conn(self):
        return self.book.connect()

    def append_row(self, values, **_):
        vals = ["" if v is None else str(v) for v in values]
        with self._conn() as c, c.transaction():
            c.execute("select pg_advisory_xact_lock(hashtext(%s))", (self.title,))
            new_id = c.execute("insert into study_rows (tab, vals) values (%s, %s) returning id",
                               (self.title, vals)).fetchone()[0]
            n = c.execute("select count(*) from study_rows where tab = %s and id <= %s",
                          (self.title, new_id)).fetchone()[0]
        return {"updates": {"updatedRange": f"{self.title}!A{n}:Z{n}"}}

    def get_all_values(self):
        with self._conn() as c:
            rows = c.execute("select vals from study_rows where tab = %s order by id",
                             (self.title,)).fetchall()
        return [list(r[0]) for r in rows]

    def col_values(self, col: int):
        return [r[col - 1] if len(r) >= col else "" for r in self.get_all_values()]

    def update_cell(self, row: int, col: int, value):
        with self._conn() as c, c.transaction():
            rid = c.execute("select id from study_rows where tab = %s order by id offset %s limit 1",
                            (self.title, row - 1)).fetchone()
            if rid:
                c.execute("update study_rows set vals[%s] = %s where id = %s",
                          (col, str(value), rid[0]))

    def update(self, values, range_name="A1", **_):
        """Replace the whole tab (used for headers, the allocation table and clean-up)."""
        with self._conn() as c, c.transaction():
            c.execute("select pg_advisory_xact_lock(hashtext(%s))", (self.title,))
            c.execute("delete from study_rows where tab = %s", (self.title,))
            with c.cursor() as cur:
                cur.executemany("insert into study_rows (tab, vals) values (%s, %s)",
                                [(self.title, [str(v) for v in r]) for r in values])

    def clear(self):
        with self._conn() as c:
            c.execute("delete from study_rows where tab = %s", (self.title,))


class _Book:
    def __init__(self, url: str):
        self.url = url
        with self.connect() as c:
            c.execute(DDL)

    def connect(self):
        # prepare_threshold=None: works through Supabase's pooler
        return psycopg.connect(self.url, autocommit=True, prepare_threshold=None, connect_timeout=10)

    def worksheet(self, name: str) -> _Sheet:
        return _Sheet(self, name)

    def add_worksheet(self, title: str, rows: int = 0, cols: int = 0) -> _Sheet:
        return _Sheet(self, title)

    def worksheets(self):
        with self.connect() as c:
            names = [r[0] for r in c.execute("select distinct tab from study_rows").fetchall()]
        return [_Sheet(self, n) for n in names]


def open_book(url: str) -> _Book:
    return _Book(url)
