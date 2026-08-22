import sys
import pymupdf as fitz

pdf_path = sys.argv[1]
out_path = sys.argv[2]
page_idx = int(sys.argv[3])

doc = fitz.open(pdf_path)
with open(out_path, "w", encoding="utf-8") as f:
    f.write("=== plain get_text ===\n")
    f.write(repr(doc[page_idx].get_text()[:400]))
    f.write("\n\n=== TEXT_INHIBIT_SPACES ===\n")
    f.write(repr(doc[page_idx].get_text("text", flags=fitz.TEXT_INHIBIT_SPACES)[:400]))
