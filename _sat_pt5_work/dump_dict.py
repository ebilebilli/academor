import sys
import pymupdf as fitz

pdf_path = sys.argv[1]
page_idx = int(sys.argv[2])
out_path = sys.argv[3]

doc = fitz.open(pdf_path)
page = doc[page_idx]
d = page.get_text("dict")
with open(out_path, "w", encoding="utf-8") as f:
    for b in d["blocks"]:
        bbox = b["bbox"]
        if "lines" not in b:
            f.write("--IMAGE BLOCK bbox=%s--\n" % (bbox,))
            continue
        f.write("--BLOCK bbox=%s--\n" % (bbox,))
        for l in b["lines"]:
            line_text = "".join(s["text"] for s in l["spans"])
            f.write(repr(line_text) + "\n")
