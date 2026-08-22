import sys
import pymupdf as fitz

pdf_path = sys.argv[1]
out_path = sys.argv[2]
start = int(sys.argv[3])
end = int(sys.argv[4])

doc = fitz.open(pdf_path)
with open(out_path, "w", encoding="utf-8") as f:
    for i in range(start, end):
        f.write(f"--- page {i} ---\n")
        f.write(doc[i].get_text())
        f.write("\n")
