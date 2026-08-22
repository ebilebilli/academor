import sys
sys.path.insert(0, "scripts")
import build_sat_practice_tests as mod
import pymupdf as fitz

pdf = mod.find_pdf(5)
doc = fitz.open(pdf)
pages = mod.find_module_pages(doc)
text = mod.extract_pages(doc, pages["math1"], pages["math1_end"])
qs = mod.split_questions(text, max_n=27, require_mcq=False)
body = qs.get(16, "<MISSING>")
with open("_sat_pt5_work/pt5_q16_dbg.txt", "w", encoding="utf-8") as f:
    f.write("BODY:\n")
    f.write(body)
    f.write("\n\nPARSE_MCQ:\n")
    f.write(repr(mod.parse_mcq(body)))
