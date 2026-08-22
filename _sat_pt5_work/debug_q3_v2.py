import importlib.util
import io

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
bounds = m.option_bounds(page, marker, yb)

out = io.open("_sat_pt5_work/dbg_q3_v2.txt", "w", encoding="utf-8")
for L in "AB":
    r = bounds[L]
    out.write(f"{L} rect={[round(x,2) for x in r]}\n")
    spans = m.collect_region_spans(page, r)
    for s in spans:
        out.write(f"  span {s['text']!r} bbox={[round(x,2) for x in s['bbox']]} flags={s['flags']}\n")
    text = m.reconstruct_region_text(page, r)
    out.write(f"  -> text={text!r}\n")
out.close()
print("done")
