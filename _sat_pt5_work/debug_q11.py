import importlib.util

spec = importlib.util.spec_from_file_location("r", "scripts/rebuild_sat_math.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

import pymupdf as fitz

pdf = m.find_pdf(5)
doc = fitz.open(pdf)
pages = m.find_module_pages(doc)
loc = m.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], 11)
pidx, marker = loc
page = doc[pidx]
markers = m.question_markers(page)
yb = m.question_band_bottom(page, marker, markers)
bounds = m.option_bounds(page, marker, yb)

with open("_sat_pt5_work/dbg_q11.txt", "w", encoding="utf-8") as out:
    for L in "ABCD":
        r = bounds[L]
        out.write(f"{L} rect={[round(x,2) for x in r]}\n")
        d = page.get_text("dict", clip=r)
        for block in d.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    out.write(f"  span {span['text']!r} bbox={[round(x,2) for x in span['bbox']]}\n")
        out.write(f"  -> {m.reconstruct_region_text(page, r)!r}\n")
print("done")
