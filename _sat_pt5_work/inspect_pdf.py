import sys
import pymupdf as fitz

pdf_path = sys.argv[1]
out_path = sys.argv[2]
n_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 10

doc = fitz.open(pdf_path)
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"pages={len(doc)}\n")
    for i in range(min(n_pages, len(doc))):
        f.write(f"--- page {i} ---\n")
        f.write(doc[i].get_text()[:500])
        f.write("\n")
