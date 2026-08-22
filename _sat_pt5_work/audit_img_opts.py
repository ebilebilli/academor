import importlib.util
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(r"C:\Users\user\Desktop\Academor")
spec = importlib.util.spec_from_file_location("rb", REPO / "scripts" / "rebuild_sat_math.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

KEYS = rb.KEYS
find_pdf = rb.find_pdf
find_module_pages = rb.find_module_pages
extract_pages = rb.extract_pages
split_questions = rb.split_questions
parse_mcq = rb.parse_mcq

import pymupdf as fitz

OUT = REPO / "_sat_pt5_work" / "audit"
OUT.mkdir(exist_ok=True)

TARGETS = {
    11: [3, 11, 12, 16, 17, 37, 40, 44],
    7: [29],
}

for test_num, qnums in TARGETS.items():
    pdf = find_pdf(test_num)
    doc = fitz.open(pdf)
    pages = find_module_pages(doc)
    for qid in qnums:
        if qid <= 22:
            local = qid
            pstart, pend = pages["math1"], pages["math1_end"]
        else:
            local = qid - 22
            pstart, pend = pages["math2"], pages["math2_end"]
        located = rb.find_marker_on_pages(doc, pstart, pend, local)
        if not located:
            print(f"PT{test_num} q{qid} NOT LOCATED")
            continue
        pidx, marker = located
        page = doc[pidx]
        markers = rb.question_markers(page)
        y_bottom = rb.question_band_bottom(page, marker, markers)
        print(f"PT{test_num} q{qid} local={local} page={pidx} ybottom={y_bottom}")
        bounds = rb.option_bounds(page, marker, y_bottom)
        if not bounds:
            print("  NO BOUNDS")
            continue
        for L in "ABCD":
            rect = bounds[L]
            raw_spans = rb.collect_region_spans(page, rect)
            plain = "".join(s["text"] for s in raw_spans)
            text = rb.reconstruct_region_text(page, rect)
            print(f"  {L} rect={rect} raw={plain!r} -> text={text!r}")
            try:
                pix = page.get_pixmap(matrix=fitz.Matrix(3, 3), clip=rect)
                pix.save(str(OUT / f"pt{test_num}_q{qid}_{L}.png"))
            except Exception as e:
                print("    crop fail", e)
