"""Make the optional 'original document' PDFs from the case and training files (Group C).

    pip install playwright markdown && playwright install chromium   # once
    python study/app/make_doc_pdfs.py                # study/content/{cases,training}/*.md
    python study/app/make_doc_pdfs.py --placeholder  # the preview placeholders

Each <id>.<lang>.md becomes <id>.<lang>.pdf next to it: one PDF page per `---page---` page,
laid out like a scanned paper record. The text is the same file the page shows, so the two
can never disagree. Re-run after group A changes a case. [[term]] markers become plain text.

The app shows the PDF to both groups under "View the original document"; if a PDF is
missing, the viewer is simply not shown (for anyone). Group A may also drop in a real
designed/scanned PDF with the same name instead; it must match the .md exactly.
"""
from __future__ import annotations

import argparse
import html
import os
import random
import sys
from pathlib import Path

import markdown

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402

CSS = """
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; background: #fff; }
.sheet { width: 8.5in; height: 11in; position: relative; overflow: hidden; page-break-after: always;
         background:
           radial-gradient(ellipse at 20% 10%, rgba(0,0,0,.025), transparent 60%),
           radial-gradient(ellipse at 85% 90%, rgba(0,0,0,.035), transparent 55%),
           #fbfaf6; }
.sheet:last-child { page-break-after: auto; }
.inner { position: absolute; inset: 0.85in 0.9in 0.9in; transform: rotate(var(--rot));
         font-family: 'Times New Roman', 'Liberation Serif', 'Noto Serif CJK SC', 'Songti SC', 'SimSun',
                      'WenQuanYi Zen Hei', serif;
         color: #222; font-size: 11.5pt; line-height: 1.55; filter: contrast(1.05); }
.lh { display: flex; justify-content: space-between; align-items: flex-end;
      border-bottom: 2px solid #333; padding-bottom: 6pt; margin-bottom: 14pt; }
.lh .t { font-weight: bold; font-size: 13pt; }
.lh .n, .foot { font-family: Arial, 'Liberation Sans', 'WenQuanYi Zen Hei', sans-serif; font-size: 8pt;
                color: #666; letter-spacing: .05em; }
.foot { position: absolute; bottom: 0.45in; right: 0.9in; }
.edge { position: absolute; inset: 0; box-shadow: inset 0 0 40px rgba(0,0,0,.06); pointer-events: none; }
table { border-collapse: collapse; } td, th { border: 1px solid #999; padding: 3pt 6pt; }
"""


def build_html(pages: list[tuple[str, str]], seed: str) -> str:
    rng = random.Random(seed)
    out = []
    n = len(pages)
    for i, (title, body) in enumerate(pages, 1):
        plain = C.TERM_RE.sub(lambda m: m.group(1), body)
        lbl = f"{i} / {n}"
        out.append(
            f'<div class="sheet"><div class="inner" style="--rot:{rng.uniform(-0.35, 0.35):.2f}deg">'
            f'<div class="lh"><div class="t">{html.escape(title)}</div><div class="n">{lbl}</div></div>'
            f'{markdown.markdown(plain, extensions=["tables"])}</div>'
            f'<div class="foot">{lbl}</div><div class="edge"></div></div>')
    return f"<!doctype html><meta charset='utf-8'><style>{CSS}</style>{''.join(out)}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--placeholder", action="store_true")
    a = ap.parse_args()
    root = C.PLACEHOLDER_DIR if a.placeholder else C.CONTENT_DIR
    files = sorted((root / "cases").glob("*.md")) + sorted((root / "training").glob("*.md"))
    if not files:
        sys.exit(f"no .md files under {root}/cases or {root}/training")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        exe = os.environ.get("CHROMIUM_PATH")  # optional: use an existing Chromium binary
        b = p.chromium.launch(executable_path=exe) if exe else p.chromium.launch()
        page = b.new_page()
        for f in files:
            pages = C.split_pages(f.read_text(encoding="utf-8"))
            page.set_content(build_html(pages, f.stem), wait_until="load")
            out = f.with_suffix(".pdf")
            page.pdf(path=str(out), format="Letter", print_background=True)
            print(f"{out.relative_to(HERE.parent)}  ({len(pages)} pages)")
        b.close()


if __name__ == "__main__":
    main()
