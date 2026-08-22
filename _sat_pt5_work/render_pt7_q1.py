import importlib.util
from pathlib import Path
import pymupdf as fitz

REPO = Path(r"C:\Users\user\Desktop\Academor")
spec = importlib.util.spec_from_file_location("rb", REPO / "scripts" / "rebuild_sat_math.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

pdf = rb.find_pdf(7)
doc = fitz.open(pdf)
pages = rb.find_module_pages(doc)
located = rb.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], 1)
pidx, marker = located
page = doc[pidx]
pix = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2))
pix.save(str(REPO / "_sat_pt5_work" / "pt7_q1_full.png"))
print("page", pidx, page.rect)
