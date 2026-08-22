import sys
sys.path.insert(0, "scripts")
import build_sat_practice_tests as mod
import pymupdf as fitz

test_num = int(sys.argv[1])
which = sys.argv[2]
qnum = int(sys.argv[3])
out_path = sys.argv[4]

pdf = mod.find_pdf(test_num)
doc = fitz.open(pdf)
pages = mod.find_module_pages(doc)
start = pages[which]
end = pages[which + "_end"]
text = mod.extract_pages(doc, start, end)
qs = mod.split_questions(text, max_n=33, require_mcq=True)
body = qs.get(qnum, "<MISSING>")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"body len={len(body)}\n")
    f.write("=== BODY ===\n")
    f.write(body)
    f.write("\n=== parse_mcq result ===\n")
    f.write(repr(mod.parse_mcq(body)))
