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

pdf = rb.find_pdf(11)
doc = fitz.open(pdf)
pages = rb.find_module_pages(doc)

qids = [7, 9, 12, 17, 20, 26, 27, 33, 36, 37, 38, 39, 40]
m1 = rb.split_questions(rb.extract_pages(doc, pages["math1"], pages["math1_end"]), max_n=27)
m2 = rb.split_questions(rb.extract_pages(doc, pages["math2"], pages["math2_end"]), max_n=27)

for qid in qids:
    if qid <= 22:
        local = qid
        body = m1[local]
    else:
        local = qid - 22
        body = m2[local]
    parsed = rb.parse_mcq(body)
    raw_stem = parsed[0] if parsed else body
    stem = rb.clean_stem_text(raw_stem)
    print(f"id={qid} bad={rb.looks_like_bad_math_text(stem)!r}")
    print(f"  stem={stem!r}")
