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
import json

for test_num in [4, 5, 6, 7, 8, 9, 10, 11]:
    p = REPO / "academor" / "portals" / "resources" / "sat_questions" / f"sat_practice_test_{test_num}_math.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    flagged = []
    for q in d["questions"]:
        opts = q.get("options")
        if not opts:
            continue
        if any(isinstance(o, str) and o.startswith("<img") for o in opts):
            flagged.append(q["id"])
    if not flagged:
        continue
    pdf = rb.find_pdf(test_num)
    doc = fitz.open(pdf)
    pages = rb.find_module_pages(doc)
    print(f"=== PT{test_num}: {flagged} ===")
    for qid in flagged:
        if qid <= 22:
            local = qid
            pstart, pend = pages["math1"], pages["math1_end"]
        else:
            local = qid - 22
            pstart, pend = pages["math2"], pages["math2_end"]
        located = rb.find_marker_on_pages(doc, pstart, pend, local)
        if not located:
            print(f" q{qid} NOT LOCATED")
            continue
        pidx, marker = located
        page = doc[pidx]
        markers = rb.question_markers(page)
        y_bottom = rb.question_band_bottom(page, marker, markers)
        bounds = rb.option_bounds(page, marker, y_bottom)
        if not bounds:
            print(f" q{qid} NO BOUNDS")
            continue
        for L in "ABCD":
            rect = bounds[L]
            text = rb.reconstruct_region_text(page, rect)
            if text is None:
                raw_spans = rb.collect_region_spans(page, rect)
                plain = "".join(s["text"] for s in raw_spans)
                print(f" q{qid} {L} IMG raw={plain!r}")
