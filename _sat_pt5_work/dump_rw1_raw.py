import sys
sys.path.insert(0, "scripts")
import build_sat_practice_tests as mod
import pymupdf as fitz

pdf = mod.find_pdf(9)
doc = fitz.open(pdf)
pages = mod.find_module_pages(doc)
text = mod.extract_pages(doc, pages["rw1"], pages["rw1_end"])
with open("_sat_pt5_work/pt9_rw1_raw.txt", "w", encoding="utf-8") as f:
    f.write(repr(text[:3000]))
