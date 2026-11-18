"""Build one case's PDF documents from study/materials/cases/<ID>/:

    case.json            claimant, claim, document list, form field values
    records/*.rec.md     medical records (see render_records.py for the format)

into a folder the study app reads, e.g. study/content/cases/C3/ (all languages):

    01_SSA-16.pdf  02_SSA-3368-BK.pdf  03_SSA-827.pdf  04_<Provider>_records.pdf ...

Each records document is the provider's pages in the order listed in case.json (one PDF per
source, like an exhibit in the electronic claim folder).

Usage:
    python study/materials/build_case.py C3                 # -> study/content/cases/C3/ (shared by en/es/zh)
    python study/materials/build_case.py C3 --out some/dir
    python study/materials/build_case.py --all
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "forms"))
from render_records import render  # noqa: E402
from fill_forms import fill_one  # noqa: E402
from claimant_profile import forms_from_profile  # noqa: E402

CASES = HERE / "cases"
APP_CASES = HERE.parent / "content" / "cases"


def build(cid: str, out: Path | None = None) -> Path:
    src = CASES / cid
    case = json.loads((src / "case.json").read_text(encoding="utf-8"))
    if "forms" not in case:  # short profile -> full field values (forms/claimant_profile.py)
        case["forms"] = forms_from_profile(case["profile"])
    out = out or HERE.parent / "content" / case.get("app_folder", "cases") / cid  # one English set for every language (team decision 2026-11-18); training cases use app_folder "training"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.pdf"):
        old.unlink()
    with tempfile.TemporaryDirectory() as tmp:
        for d in case["documents"]:
            target = out / d["file"]
            if d["kind"] == "form":
                for w in fill_one(d["form"], case["forms"][d["form"]], target):
                    print("  WARNING", w)
            else:
                writer = PdfWriter()
                for rec in d["records"]:
                    pdf = Path(tmp) / (Path(rec).stem + ".pdf")
                    render(src / "records" / rec, pdf)
                    for page in PdfReader(pdf).pages:
                        writer.add_page(page)
                writer.add_metadata({"/Title": target.stem, "/Subject": "Synthetic record for research"})
                with open(target, "wb") as fh:
                    writer.write(fh)
            print("  wrote", target.relative_to(HERE.parent.parent) if target.is_relative_to(HERE.parent.parent) else target)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    ids = sorted(p.name for p in CASES.iterdir() if (p / "case.json").exists()) if a.all else [a.case]
    for cid in ids:
        print(cid)
        build(cid, Path(a.out) / cid if (a.out and a.all) else (Path(a.out) if a.out else None))


if __name__ == "__main__":
    main()
