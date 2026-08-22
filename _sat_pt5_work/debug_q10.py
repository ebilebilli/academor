import importlib.util
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(r"C:\Users\user\Desktop\Academor")
spec = importlib.util.spec_from_file_location("rb", REPO / "scripts" / "rebuild_sat_math.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

import pymupdf as fitz

pdf = rb.find_pdf(8)
doc = fitz.open(pdf)
pages = rb.find_module_pages(doc)
located = rb.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], 10)
pidx, marker = located
page = doc[pidx]
markers = rb.question_markers(page)
y_bottom = rb.question_band_bottom(page, marker, markers)
col = fitz.Rect(marker["col_rect"])
band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, y_bottom)
choices = rb.choice_spans(page, band)
for L, lr, cr in choices:
    print("choice", L, "letter_rect", lr)
bounds = rb.option_bounds(page, marker, y_bottom)
for L in "ABCD":
    print(L, bounds[L])

print("---- spans in band ----")
d = page.get_text("dict")
for block in d["blocks"]:
    if block.get("type") != 0:
        continue
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            r = fitz.Rect(span["bbox"])
            if not band.intersects(r):
                continue
            print(f"y0={r.y0:.1f} y1={r.y1:.1f} x0={r.x0:.1f} x1={r.x1:.1f} text={span['text']!r}")
