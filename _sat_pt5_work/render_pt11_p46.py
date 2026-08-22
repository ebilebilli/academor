import importlib.util
from pathlib import Path
import pymupdf as fitz

REPO = Path(r"C:\Users\user\Desktop\Academor")
spec = importlib.util.spec_from_file_location("rb", REPO / "scripts" / "rebuild_sat_math.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

pdf = rb.find_pdf(11)
doc = fitz.open(pdf)
page = doc[46]
pix = page.get_pixmap(matrix=fitz.Matrix(2.2, 2.2))
pix.save(str(REPO / "_sat_pt5_work" / "pt11_p46_full.png"))
print("saved", page.rect)
