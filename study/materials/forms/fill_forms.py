"""Fill the official SSA PDF templates from a case's case.json. No form is redrawn: the script
writes values into the real fields of the blank forms downloaded from ssa.gov, then flattens
them so the result looks like a printed, submitted form.

case.json, "forms" section (keys come from forms/catalog/<form>.csv, column "key"):

    "forms": {
      "ssa-16":      {"Page1.N1FLD": "Jordan A Miller",        # text field
                      "Page1.N6ACB": "Yes",                     # yes/no pair: pick the box whose on-value is "Yes"
                      ...},
      "ssa-3368-bk": {"BodyPage4.P4_N4A_CB2": true, ...},       # single checkbox: true = checked
      "ssa-827":     {...}
    }

A key that does not exist in the template stops the run (so a typo never silently drops data).
Text longer than its box is shrunk to fit (font size down to 6 pt); the script warns when a
value still overflows.

Usage:
    python fill_forms.py <case.json> <out_dir>                # writes 01_SSA-16.pdf, 02_SSA-3368-BK.pdf, 03_SSA-827.pdf
    python fill_forms.py <case.json> <out_dir> --keep-fields  # leave the fields editable (no flattening)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pymupdf

HERE = Path(__file__).parent
TEMPLATES = HERE / "templates"
OUTPUT_NAMES = {"ssa-16": "01_SSA-16.pdf", "ssa-3368-bk": "02_SSA-3368-BK.pdf", "ssa-827": "03_SSA-827.pdf",
                "ssa-3373-bk": "04_SSA-3373-BK.pdf"}

sys.path.insert(0, str(HERE))
from field_catalog import short  # noqa: E402


def _group(key: str) -> str:
    return key.split("#")[0]


def fill_one(form: str, values: dict, out: Path, flatten: bool = True) -> list[str]:
    warnings = []
    doc = pymupdf.open(TEMPLATES / f"{form}.pdf")
    # Drop the XFA layer: viewers that honour XFA would otherwise ignore the AcroForm values.
    try:
        cat = doc.pdf_catalog()
        af = doc.xref_get_key(cat, "AcroForm")
        if af[0] == "xref":
            doc.xref_set_key(int(af[1].split()[0]), "XFA", "null")
    except Exception as e:  # pragma: no cover
        warnings.append(f"{form}: could not remove XFA ({e})")

    pages = [doc[i] for i in range(doc.page_count)]  # keep page objects alive while widgets are used
    widgets, onstate = {}, {}
    for page in pages:
        for w in page.widgets():
            if w.field_type == pymupdf.PDF_WIDGET_TYPE_BUTTON:
                continue
            k = short(w.field_name)
            widgets.setdefault(k, []).append((page.number, w.xref))
            if w.field_type in (pymupdf.PDF_WIDGET_TYPE_CHECKBOX, pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON):
                onstate[k] = str(w.on_state())
    groups: dict[str, list[str]] = {}
    for k in widgets:
        groups.setdefault(_group(k), []).append(k)

    todo: dict[str, object] = {}
    for key, val in values.items():
        if key.startswith("_"):
            continue  # comments
        if key in widgets and not (isinstance(val, str) and len(groups.get(key, [])) > 1):
            todo[key] = val
        elif key in groups and isinstance(val, str):
            # yes/no style group: pick the member whose on-value matches
            hit = None
            for k in groups[key]:
                if k in onstate and onstate[k].lower().replace("#20", " ") == val.lower():
                    hit = k
            if hit is None:
                raise SystemExit(f"{form}: no box in group {key!r} has value {val!r}")
            todo[hit] = True
        else:
            raise SystemExit(f"{form}: unknown field key {key!r} (see forms/catalog/{form}.csv)")

    for key, val in todo.items():
        for pno, xref in widgets[key]:
            w = pages[pno].load_widget(xref)
            if w.field_type in (pymupdf.PDF_WIDGET_TYPE_CHECKBOX, pymupdf.PDF_WIDGET_TYPE_RADIOBUTTON):
                w.field_value = w.on_state() if val else "Off"
            else:
                text = str(val)
                w.text_font = "Cour"
                height = w.rect.height
                multiline = height > 22 or "\n" in text
                if multiline:
                    w.field_flags |= pymupdf.PDF_TX_FIELD_IS_MULTILINE
                size = 9.0
                while size > 6.0 and not _fits(text, w.rect, size, multiline):
                    size -= 0.5
                if not _fits(text, w.rect, size, multiline):
                    warnings.append(f"{form}: text may overflow {key}: {text[:40]!r}...")
                w.text_fontsize = size
                w.field_value = text
            w.update()
    if flatten:
        doc.bake(annots=False, widgets=True)
    doc.save(out, garbage=3, deflate=True)
    return warnings


def _fits(text: str, rect, size: float, multiline: bool) -> bool:
    cw = 0.6 * size  # Courier: every glyph is 0.6 em wide
    width = max(rect.width - 4, 1)
    if not multiline:
        return len(text) * cw <= width
    per_line = max(int(width // cw), 1)
    lines = 0
    for para in text.split("\n"):
        lines += max(1, -(-len(para) // per_line))
    return lines * size * 1.16 <= rect.height - 2


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("case_json")
    ap.add_argument("out_dir")
    ap.add_argument("--keep-fields", action="store_true")
    a = ap.parse_args(argv)
    case = json.loads(Path(a.case_json).read_text(encoding="utf-8"))
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for form, values in case["forms"].items():
        target = out / OUTPUT_NAMES[form]
        for wmsg in fill_one(form, values, target, flatten=not a.keep_fields):
            print("WARNING", wmsg)
        print("wrote", target)


if __name__ == "__main__":
    main()
