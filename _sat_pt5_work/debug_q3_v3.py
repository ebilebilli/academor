import importlib.util

spec = importlib.util.spec_from_file_location("r", "scripts/rebuild_sat_math.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

import pymupdf as fitz

pdf = m.find_pdf(5)
doc = fitz.open(pdf)
pages = m.find_module_pages(doc)
loc = m.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], 3)
pidx, marker = loc
page = doc[pidx]
markers = m.question_markers(page)
yb = m.question_band_bottom(page, marker, markers)
col = fitz.Rect(marker["col_rect"])
band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, yb)
choices = m.choice_spans(page, band)
for L, letter_rect, content_rect in choices:
    print(L, "letter", [round(x, 2) for x in letter_rect], "content", [round(x, 2) for x in content_rect])
