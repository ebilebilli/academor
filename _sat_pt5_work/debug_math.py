import sys
sys.path.insert(0, "scripts")
import build_sat_practice_tests as mod
import pymupdf as fitz

test_num = int(sys.argv[1])
which = sys.argv[2]
out_path = sys.argv[3]

pdf = mod.find_pdf(test_num)
doc = fitz.open(pdf)
pages = mod.find_module_pages(doc)
start = pages[which]
end = pages[which + "_end"]
text = mod.extract_pages(doc, start, end)
qs = mod.split_questions(text, max_n=27, require_mcq=False)
found = sorted(qs.keys())
missing = [n for n in range(1, 28) if n not in found]
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"found keys: {found}\n")
    f.write(f"missing: {missing}\n\n")
    f.write("=== FULL TEXT ===\n")
    f.write(text)
