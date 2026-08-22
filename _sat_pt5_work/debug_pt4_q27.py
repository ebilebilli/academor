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

pdf = rb.find_pdf(4)
doc = fitz.open(pdf)
pages = rb.find_module_pages(doc)
located = rb.find_marker_on_pages(doc, pages["math2"], pages["math2_end"], 5)
pidx, marker = located
page = doc[pidx]
markers = rb.question_markers(page)
y_bottom = rb.question_band_bottom(page, marker, markers)
bounds = rb.option_bounds(page, marker, y_bottom)
for L in "ABCD":
    rect = bounds[L]
    spans = rb.collect_region_spans(page, rect)
    merged = rb.merge_fraction_stacks(spans)
    lines = rb.group_lines(merged)
    frac = sum(1 for s in merged if s.get("is_fraction"))
    scattered = rb.looks_like_scattered_graphic(page, rect, lines, frac)
    print(L, rect, "lines=", len(lines), "frac=", frac, "scattered=", scattered)
    dh = 0
    for path in page.get_drawings():
        r = fitz.Rect(path.get("rect"))
        if rect.intersects(r) and r.get_area() > 0:
            dh += 1
    print("   drawing_hits=", dh)
