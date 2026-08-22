import sys
import pymupdf as fitz

pdf_path = sys.argv[1]
needle = sys.argv[2]
start = int(sys.argv[3])
end = int(sys.argv[4])

doc = fitz.open(pdf_path)
for i in range(start, end):
    t = doc[i].get_text()
    if needle in t:
        print(i)
