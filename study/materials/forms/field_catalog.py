"""Write one CSV per official SSA template listing every fillable field.

Columns: key (the short name used in case.json), page, type, on_value (checkbox), label (the
form's own tooltip, i.e. what the field asks). Use it to look up the key for an item.

Usage: python field_catalog.py            # writes forms/catalog/<form>.csv
"""
import csv
import re
from pathlib import Path

import pymupdf

HERE = Path(__file__).parent
FORMS = ["ssa-16", "ssa-3368-bk", "ssa-827", "ssa-3373-bk"]


def short(name: str) -> str:
    """'topmostSubform[0].Page1[0].N1FLD[0]' -> 'Page1.N1FLD';  checkbox groups keep their index."""
    parts = name.split(".")
    leaf = parts[-1]
    page = re.sub(r"\[\d+\]$", "", parts[-2]) if len(parts) > 1 else ""
    m = re.match(r"(.*)\[(\d+)\]$", leaf)
    base, idx = (m.group(1), int(m.group(2))) if m else (leaf, 0)
    return f"{page}.{base}" + (f"#{idx}" if idx else "")


def main():
    out = HERE / "catalog"
    out.mkdir(exist_ok=True)
    for f in FORMS:
        doc = pymupdf.open(HERE / "templates" / f"{f}.pdf")
        with open(out / f"{f}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["key", "page", "type", "on_value", "label"])
            for p in doc:
                for wd in p.widgets():
                    if wd.field_type == pymupdf.PDF_WIDGET_TYPE_BUTTON:
                        continue
                    lab = re.sub(r"\s+", " ", wd.field_label or "")[:220]
                    on = wd.on_state() if wd.field_type in (2, 5) else ""
                    w.writerow([short(wd.field_name), p.number + 1, wd.field_type_string, on, lab])
        print("wrote", out / f"{f}.csv")


if __name__ == "__main__":
    main()
