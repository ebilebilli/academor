import sys
sys.path.insert(0, "scripts")
import build_sat_practice_tests as mod
import pymupdf as fitz

test_num = int(sys.argv[1])
which = sys.argv[2]  # rw1, rw2, math1, math2
out_path = sys.argv[3]

pdf = mod.find_pdf(test_num)
doc = fitz.open(pdf)
pages = mod.find_module_pages(doc)
start = pages[which]
end = pages[which + "_end"]
text = mod.extract_pages(doc, start, end)
require_mcq = which.startswith("rw")
max_n = 33 if which.startswith("rw") else 27
qs = mod.split_questions(text, max_n=max_n, require_mcq=require_mcq)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"pages {start}..{end}\n")
    f.write(f"found keys: {sorted(qs.keys())}\n")
    missing = [n for n in range(1, (28 if which.startswith('rw') else 23)) if n not in qs]
    f.write(f"missing: {missing}\n\n")
    f.write("=== FULL TEXT ===\n")
    f.write(text)
