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

for qid in [17, 27, 32]:
    if qid <= 22:
        local = qid
        pstart, pend = pages["math1"], pages["math1_end"]
    else:
        local = qid - 22
        pstart, pend = pages["math2"], pages["math2_end"]
    located = rb.find_marker_on_pages(doc, pstart, pend, local)
    pidx, marker = located
    page = doc[pidx]
    markers = rb.question_markers(page)
    y_bottom = rb.question_band_bottom(page, marker, markers)
    bounds = rb.option_bounds(page, marker, y_bottom)
    print(f"q{qid} local={local} page={pidx}")
    if not bounds:
        print("  NO BOUNDS")
        continue
    for L in "ABCD":
        rect = bounds[L]
        raw_spans = rb.collect_region_spans(page, rect)
        plain = "".join(s["text"] for s in raw_spans)
        text = rb.reconstruct_region_text(page, rect)
        print(f"  {L} raw={plain!r} -> text={text!r}")
