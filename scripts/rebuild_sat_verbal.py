"""Rebuild only the SAT Verbal JSONs (math is handled by rebuild_sat_math.py)
so the "dollar sign" / "percent sign" / "negative N" symbol-word fix in
normalize_spaces is applied without touching the math builder's improved
image/text logic."""

from __future__ import annotations

import json

import pymupdf as fitz

import build_sat_practice_tests as build

for test_num in sorted(build.KEYS):
    pdf = build.find_pdf(test_num)
    if not pdf:
        print(f"SKIP PT{test_num}: PDF not found")
        continue
    doc = fitz.open(pdf)
    pages = build.find_module_pages(doc)
    missing = [need for need in ("rw1", "rw2", "math1", "math2") if pages.get(need) is None]
    if missing:
        print(f"FAIL PT{test_num}: missing {missing}")
        continue
    keys = build.KEYS[test_num]
    verbal = build.build_verbal(doc, pages, keys, test_num)
    vpath = build.OUT_DIR / f"sat_practice_test_{test_num}_verbal.json"
    vpath.write_text(json.dumps(verbal, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK verbal {vpath.name} n={len(verbal['questions'])}")
