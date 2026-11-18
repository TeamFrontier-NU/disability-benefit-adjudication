"""Render a synthetic medical record (.rec.md) as a PDF that looks like a provider printout.

A record file is YAML front matter + a light markup body:

    ---
    style: ehr            # ehr (EHR printout), dictated (transcribed report), lab (lab report), letter
    facility: Lakeshore Rehabilitation Hospital
    dept: Physical Medicine & Rehabilitation
    address: 2200 Shore Rd, Lakeport, IL 60990
    phone: "Tel (555) 013-2200   Fax (555) 013-2201"
    title: INPATIENT REHABILITATION ADMISSION H&P
    patient:              # demographics grid, in order
      Patient: MILLER, JORDAN A
      MRN: LRH-0048213
    banner: "OCT/21/2026 09:14  FROM: LAKESHORE REHAB HIM  TO: DDS  P. {page}/{pages}"  # optional fax line
    exhibit: 2F           # optional exhibit stamp of the electronic folder
    received: "Rec'd 10/21/2026 · Electronic Records Express · DDS request"
    ---
    ## HISTORY OF PRESENT ILLNESS
    Free text paragraph. **bold** works.

    | Test | Result | Flag | Units | Reference |
    |---|---|---|---|---|
    | WBC | 11.2 | H | K/uL | 4.0-10.5 |

    - bullet line
    ===page===            # page break

Every page carries a small "SYNTHETIC RECORD" line so a page can never pass as a real record.

Usage: python render_records.py <in.rec.md> <out.pdf>
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
                                Table, TableStyle)

SYNTH = "SYNTHETIC RECORD - fictional patient, provider and facility; created for research use only."

FONTS = {  # style -> (body, bold, mono)
    "ehr": ("Helvetica", "Helvetica-Bold", 9),
    "dictated": ("Courier", "Courier-Bold", 9.5),
    "lab": ("Courier", "Courier-Bold", 8.5),
    "letter": ("Times-Roman", "Times-Bold", 11),
}


def parse(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError(f"{path}: missing front matter")
    # keys like "Case #:" or "Acc #:" would start a YAML comment: quote them
    head = re.sub(r'^(\s+)([^"\n:]*#[^"\n:]*):', r'\1"\2":', m.group(1), flags=re.M)
    return yaml.safe_load(head) or {}, m.group(2)


def inline(s: str) -> str:
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"__(.+?)__", r"<u>\1</u>", s)
    return s


def make_numbered_canvas(meta: dict, body_font: str):
    banner = meta.get("banner")
    exhibit = meta.get("exhibit")
    received = meta.get("received")

    class NumberedCanvas(rl_canvas.Canvas):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._saved = []

        def showPage(self):
            self._saved.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            n = len(self._saved)
            for st in self._saved:
                self.__dict__.update(st)
                self._decorate(n)
                super().showPage()
            super().save()

        def _decorate(self, n):
            w, h = LETTER
            p = self._pageNumber
            if banner:
                self.setFont("Courier", 7.5)
                self.setFillColor(colors.HexColor("#333333"))
                self.drawString(0.45 * inch, h - 0.32 * inch, banner.format(page=p, pages=n))
            self.setFont("Helvetica", 6.5)
            self.setFillColor(colors.HexColor("#888888"))
            self.drawString(0.6 * inch, 0.35 * inch, SYNTH)
            self.setFillColor(colors.black)
            self.setFont(body_font, 8)
            self.drawRightString(w - 0.6 * inch, 0.55 * inch, f"Page {p} of {n}")
            if exhibit or received:
                # electronic folder stamp, bottom left
                self.setFont("Helvetica-Bold", 8)
                txt = f"Exhibit No. {exhibit}" if exhibit else ""
                self.drawString(0.6 * inch, 0.55 * inch, txt)
                if received:
                    self.setFont("Helvetica", 7)
                    self.drawString(0.6 * inch + (1.05 * inch if exhibit else 0), 0.55 * inch, received)

    return NumberedCanvas


def build(meta: dict, body: str, out: Path) -> None:
    style = meta.get("style", "ehr")
    font, bold, size = FONTS[style]
    lead = size * 1.3
    P = ParagraphStyle("p", fontName=font, fontSize=size, leading=lead, spaceAfter=size * 0.45)
    H = ParagraphStyle("h", fontName=bold, fontSize=size + 0.5, leading=lead + 1, spaceBefore=size * 0.8,
                       spaceAfter=size * 0.25)
    B = ParagraphStyle("b", parent=P, leftIndent=12, bulletIndent=2, spaceAfter=size * 0.15)
    C = ParagraphStyle("c", fontName=font, fontSize=size - 0.5, leading=(size - 0.5) * 1.2)
    CB = ParagraphStyle("cb", parent=C, fontName=bold)
    story = []

    # ---- facility header ----
    if style == "letter":
        story.append(Paragraph(f"<b>{inline(meta['facility'])}</b>", ParagraphStyle(
            "lh", fontName=bold, fontSize=15, leading=18, alignment=TA_CENTER)))
        for k in ("dept", "address", "phone"):
            if meta.get(k):
                story.append(Paragraph(inline(meta[k]), ParagraphStyle(
                    "lh2", fontName=font, fontSize=9, leading=11, alignment=TA_CENTER)))
        story.append(Spacer(1, 18))
    else:
        head = [[Paragraph(f"<b>{inline(meta['facility'])}</b>", ParagraphStyle(
                    "fh", fontName=bold, fontSize=12.5 if style != "dictated" else 11.5, leading=15)),
                 Paragraph("<br/>".join(inline(meta[k]) for k in ("address", "phone") if meta.get(k)),
                           ParagraphStyle("fa", fontName=font, fontSize=7.5, leading=9.5))]]
        if meta.get("dept"):
            head.append([Paragraph(inline(meta["dept"]), ParagraphStyle("fd", fontName=font, fontSize=8.5,
                                                                       leading=10)), ""])
        t = Table(head, colWidths=[4.2 * inch, 3.0 * inch])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("LINEBELOW", (0, -1), (-1, -1), 1.2 if style == "ehr" else 0.6, colors.black)]))
        story.append(t)
        story.append(Spacer(1, 6))
        if meta.get("title"):
            tb = Table([[Paragraph(f"<b>{inline(meta['title'])}</b>", ParagraphStyle(
                "tt", fontName=bold, fontSize=10.5, leading=13,
                alignment=TA_CENTER if style == "dictated" else 0))]], colWidths=[7.2 * inch])
            tb.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1),
                                     colors.HexColor("#e6e6e6") if style in ("ehr", "lab") else colors.white),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 4)]))
            story.append(tb)
            story.append(Spacer(1, 5))
        pat = meta.get("patient") or {}
        if pat:
            items = list(pat.items())
            rows = []
            for i in range(0, len(items), 3):
                row = []
                for k, v in items[i:i + 3]:
                    row += [Paragraph(f"{inline(str(k))}:", CB), Paragraph(inline(str(v)), C)]
                row += [""] * (6 - len(row))
                rows.append(row)
            pt = Table(rows, colWidths=[0.95 * inch, 1.45 * inch] * 3)
            pt.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 1), ("TOPPADDING", (0, 0), (-1, -1), 0.5),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
                                    ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.grey)]))
            story.append(pt)
            story.append(Spacer(1, 6))

    # ---- body ----
    lines = body.strip("\n").split("\n")
    i = 0
    para: list[str] = []

    def flush():
        if para:
            story.append(Paragraph(inline(" ".join(x.strip() for x in para)), P))
            para.clear()

    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if s == "===page===":
            flush(); story.append(PageBreak())
        elif s.startswith("## "):
            flush(); story.append(Paragraph(inline(s[3:]), H))
        elif s.startswith("|"):
            flush()
            rows = []
            header = False
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    header = True
                else:
                    rows.append(cells)
                i += 1
            i -= 1
            ncol = max(len(r) for r in rows)
            data = [[Paragraph(inline(c), CB if (header and r == 0) else C) for c in row + [""] * (ncol - len(row))]
                    for r, row in enumerate(rows)]
            # column widths follow the longest text in each column (like a printout); when the
            # table is too wide, only the long-text columns shrink, never below their longest word
            avail = 7.3 * inch
            cw = lambda n: n * (size - 0.5) * 0.6 + 12
            cols = [[r[c] if c < len(r) else "" for r in rows] for c in range(ncol)]
            nat = [max(cw(max(len(x) for x in col)), 0.45 * inch) for col in cols]
            low = [min(cw(max((len(w) for x in col for w in x.split()), default=0)), n)
                   for col, n in zip(cols, nat)]
            if sum(nat) > avail:
                k = max(0.0, (avail - sum(low)) / max(sum(nat) - sum(low), 1))
                nat = [lo + (n - lo) * k for lo, n in zip(low, nat)]
            t = Table(data, colWidths=nat, repeatRows=1 if header else 0, hAlign="LEFT")
            ts = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 3),
                  ("TOPPADDING", (0, 0), (-1, -1), 1.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2)]
            if header:
                ts += [("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black)]
            if style in ("ehr",):
                ts += [("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#999999"))]
            t.setStyle(TableStyle(ts))
            story.append(t)
            story.append(Spacer(1, 5))
        elif s.startswith("- "):
            flush(); story.append(Paragraph(inline(s[2:]), B, bulletText="-"))
        elif s == "":
            flush()
        else:
            para.append(ln)
        i += 1
    flush()

    doc = SimpleDocTemplate(str(out), pagesize=LETTER, leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                            topMargin=0.55 * inch, bottomMargin=0.85 * inch,
                            title=meta.get("title", ""), author=meta.get("facility", ""))
    doc.build(story, canvasmaker=make_numbered_canvas(meta, font))


def render(src: Path, out: Path) -> None:
    meta, body = parse(src)
    build(meta, body, out)


if __name__ == "__main__":
    render(Path(sys.argv[1]), Path(sys.argv[2]))
