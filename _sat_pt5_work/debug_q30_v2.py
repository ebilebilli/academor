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
located = rb.find_marker_on_pages(doc, pages["math2"], pages["math2_end"], 8)
pidx, marker = located
page = doc[pidx]
markers = rb.question_markers(page)
y_bottom = rb.question_band_bottom(page, marker, markers)
bounds = rb.option_bounds(page, marker, y_bottom)
for L in "ABCD":
    print(L, bounds[L])
    spans = rb.collect_region_spans(page, bounds[L])
    for s in spans:
        print("   ", s["text"], s["bbox"], s.get("flags"))
