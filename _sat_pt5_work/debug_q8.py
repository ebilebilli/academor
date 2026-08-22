import importlib.util
import io

spec = importlib.util.spec_from_file_location("r", "scripts/rebuild_sat_math.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

import pymupdf as fitz

pdf = m.find_pdf(5)
doc = fitz.open(pdf)
pages = m.find_module_pages(doc)
loc = m.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], 8)
pidx, marker = loc
page = doc[pidx]
markers = m.question_markers(page)
yb = m.question_band_bottom(page, marker, markers)
col = fitz.Rect(marker["col_rect"])
band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, yb)
choices = m.choice_spans(page, band)
print("choices:", [(c[0], round(c[1].y0, 1), round(c[1].y1, 1)) for c in choices])

bounds = m.option_bounds(page, marker, yb)

out = io.open("_sat_pt5_work/dbg_q8_bounds.txt", "w", encoding="utf-8")
for L, r in bounds.items():
    out.write(f"{L} rect={[round(x,1) for x in r]}\n")
    text = m.reconstruct_region_text(page, r)
    out.write(f"  text={text!r}\n")
    spans = m.collect_region_spans(page, r)
    for s in spans:
        out.write(f"    span {s['text']!r} bbox={[round(x,1) for x in s['bbox']]} flags={s['flags']}\n")
    drawings = [p for p in page.get_drawings() if r.intersects(fitz.Rect(p.get("rect")))]
    out.write(f"  drawing_hits={len(drawings)}\n")
    for p in drawings[:10]:
        out.write(f"    draw rect={[round(x,1) for x in fitz.Rect(p.get('rect'))]}\n")
out.close()
print("done")
