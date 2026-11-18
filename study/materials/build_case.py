"""Build one case's PDF documents from study/materials/cases/<ID>/:

    case.json            claimant, claim, document list, form field values
    records/*.rec.md     medical records (see render_records.py for the format)

into a folder the study app reads, e.g. study/content/cases/C3/ (English). A case with
translated records in records.es/ or records.zh/ (same file names) is also built into
study/content/cases/C3.es/ and C3.zh/: the records translated, the official SSA forms in English.

    01_SSA-16.pdf  02_SSA-3368-BK.pdf  03_SSA-827.pdf  04_<Provider>_records.pdf ...

Each records document is the provider's pages in the order listed in case.json (one PDF per
source, like an exhibit in the electronic claim folder).

Usage:
    python study/materials/build_case.py C3                 # -> study/content/cases/C3/ (+ C3.es/, C3.zh/)
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
from render_records import parse, render  # noqa: E402
from fill_forms import fill_one  # noqa: E402
from claimant_profile import forms_from_profile  # noqa: E402

CASES = HERE / "cases"
LANGS = ("es", "zh")  # built when the case has records.<lang>/ (translated records); English is records/

# Document names per language (the app shows the file name without its number as the title).
# "<Source>_records" is translated by rule; the official forms stay the English SSA editions.
NAMES = {
    "Fast-track_screen_and_evidence_list": {"es": "Evaluación_de_vía_rápida_y_lista_de_pruebas",
                                            "zh": "快速通道筛查与证据清单"},
    "Application_SSA-3368-BK_Disability_Report": {"es": "Solicitud_SSA-3368-BK_Informe_de_discapacidad_(inglés)",
                                                  "zh": "申请表_SSA-3368-BK_残障报告（英文）"},
    "Application_SSA-16": {"es": "Solicitud_SSA-16_(inglés)", "zh": "申请表_SSA-16（英文）"},
    "Authorization_SSA-827": {"es": "Autorización_SSA-827_(inglés)", "zh": "授权书_SSA-827（英文）"},
    "ClearView_MRI_report_claimant": {"es": "Informe_de_resonancia_ClearView_(del_solicitante)",
                                      "zh": "ClearView_MRI_报告（申请人提交）"},
    "North_Point_Neurology_letter": {"es": "Carta_de_North_Point_Neurology", "zh": "North_Point_Neurology_信函"},
    "North_Point_Neurology_records_response": {"es": "Respuesta_de_North_Point_Neurology_a_la_solicitud",
                                               "zh": "North_Point_Neurology_病历调取回复"},
    "Patient_portal_printout_claimant": {"es": "Impresión_del_portal_del_paciente_(del_solicitante)",
                                         "zh": "患者门户打印件（申请人提交）"},
    "Specialist_letter_claimant": {"es": "Carta_del_especialista_(del_solicitante)", "zh": "专科医生信函（申请人提交）"},
}


def doc_name(file: str, lang: str) -> str:
    """Translated file name, e.g. 02_Riverview_Hospital_records.pdf -> 02_Riverview_Hospital_病历.pdf."""
    if lang == "en":
        return file
    num, rest = file.split("_", 1)
    stem = rest[:-4]
    if stem in NAMES:
        name = NAMES[stem][lang]
    elif stem.endswith("_records"):
        src = stem[: -len("_records")]
        name = f"{src}_病历" if lang == "zh" else f"Registros_de_{src}"
    else:
        raise SystemExit(f"no {lang} name for {file}: add it to NAMES in build_case.py")
    return f"{num}_{name}.pdf"
APP_CASES = HERE.parent / "content" / "cases"


def build(cid: str, out: Path | None = None, lang: str = "en") -> Path:
    src = CASES / cid
    rec_dir = src / ("records" if lang == "en" else f"records.{lang}")
    case = json.loads((src / "case.json").read_text(encoding="utf-8"))
    if "forms" not in case:  # short profile -> full field values (forms/claimant_profile.py)
        case["forms"] = forms_from_profile(case["profile"])
    out = out or HERE.parent / "content" / case.get("app_folder", "cases") / (cid if lang == "en" else f"{cid}.{lang}")  # one English set for every language (team decision 2026-11-18); training cases use app_folder "training"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.pdf"):
        old.unlink()
    pages: dict[str, int] = {}  # exhibit -> rendered pages, checked against the evidence list
    with tempfile.TemporaryDirectory() as tmp:
        for d in case["documents"]:
            target = out / doc_name(d["file"], lang)
            if d["kind"] == "form":
                for w in fill_one(d["form"], case["forms"][d["form"]], target):
                    print("  WARNING", w)
            else:
                writer = PdfWriter()
                for rec in d["records"]:
                    pdf = Path(tmp) / (Path(rec).stem + ".pdf")
                    render(rec_dir / rec, pdf, lang)
                    n = len(PdfReader(pdf).pages)
                    ex = parse(rec_dir / rec)[0].get("exhibit")
                    if ex:
                        pages[str(ex)] = pages.get(str(ex), 0) + n
                    for page in PdfReader(pdf).pages:
                        writer.add_page(page)
                writer.add_metadata({"/Title": target.stem, "/Subject": "Synthetic record for research"})
                with open(target, "wb") as fh:
                    writer.write(fh)
            print("  wrote", target.relative_to(HERE.parent.parent) if target.is_relative_to(HERE.parent.parent) else target)
    if lang != "en" and fix_translated_pages(cid, lang, pages):
        return build(cid, out, lang)  # the translated evidence list now gives the right page counts
    check_screen(rec_dir, pages)
    return out


def fix_translated_pages(cid: str, lang: str, pages: dict[str, int]) -> bool:
    """A translation runs shorter or longer than the English: its evidence list follows its own
    pages. Updates screen_i18n in case.json and rewrites the sheet; True if anything changed."""
    import make_screen
    p = CASES / cid / "case.json"
    case = json.loads(p.read_text(encoding="utf-8"))
    ex = case.get("screen_i18n", {}).get(lang, {}).get("exhibits", [])
    changed = False
    for e in ex:
        if e[0] in pages and e[3] != str(pages[e[0]]):
            print(f"  {lang} evidence list: exhibit {e[0]} {e[3]} -> {pages[e[0]]} page(s)")
            e[3], changed = str(pages[e[0]]), True
    if changed:
        p.write_text(json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        make_screen.make(cid, lang)
    return changed


def check_screen(rec_dir: Path, pages: dict[str, int]) -> None:
    """Warn when the evidence list (00_screen) gives a page count the records do not have."""
    screen = rec_dir / "00_screen.rec.md"
    if not screen.exists():
        return
    for line in screen.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 6 and cells[0] in pages and cells[3] != str(pages[cells[0]]):
            print(f"  WARNING evidence list says exhibit {cells[0]} has {cells[3]} page(s), "
                  f"records render {pages[cells[0]]}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    ids = sorted(p.name for p in CASES.iterdir() if (p / "case.json").exists()) if a.all else [a.case]
    for cid in ids:
        print(cid)
        for lang in ("en",) + tuple(x for x in LANGS if (CASES / cid / f"records.{x}").is_dir()):
            if lang != "en":
                print(f"{cid} ({lang})")
            o = (Path(a.out) / (cid if lang == "en" else f"{cid}.{lang}")) if a.out else None
            build(cid, o, lang)


if __name__ == "__main__":
    main()
