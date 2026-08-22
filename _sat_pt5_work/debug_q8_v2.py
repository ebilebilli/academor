import importlib.util
import io

spec = importlib.util.spec_from_file_location("r", "scripts/rebuild_sat_math.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

import pymupdf as fitz

pdf = m.find_pdf(5)
doc = fitz.open(pdf)
pages = m.find_module_pages(doc)
loc = m.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], 8)
pidx, marker = loc
page = doc[pidx]
markers = m.question_markers(page)
yb = m.question_band_bottom(page, marker, markers)
print("y_bottom", yb)

col = fitz.Rect(marker["col_rect"])
band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, yb)
choices = m.choice_spans(page, band)
by_letter = {L: (lr, cr) for L, lr, cr in choices}
ordered = [(L, *by_letter[L]) for L in "ABCD"]
tops = [ordered[i][1].y0 for i in range(4)]
print("tops", tops)

slots = {}
for i, (L, letter_rect, content_rect) in enumerate(ordered):
    slot_top = letter_rect.y0 - 3 if i == 0 else (tops[i - 1] + tops[i]) / 2
    if i == 3:
        naive_bottom = min(yb - 2, letter_rect.y0 + 400)
        slot_bottom = m.find_gap_cutoff(page, col.x0, col.x1, letter_rect.y1, naive_bottom)
    else:
        slot_bottom = (tops[i] + tops[i + 1]) / 2
    slots[L] = {"top": slot_top, "bottom": slot_bottom, "letter": letter_rect, "content": content_rect}
    print(L, "top", round(slot_top, 1), "bottom", round(slot_bottom, 1))

out = io.open("_sat_pt5_work/dbg_q8_v2.txt", "w", encoding="utf-8")


def owning_slot(mid_y):
    for L, s in slots.items():
        if s["top"] <= mid_y < s["bottom"]:
            return L
    return None


d = page.get_text("dict")
for block in d["blocks"]:
    if block.get("type") != 0:
        continue
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            r = fitz.Rect(span["bbox"])
            mid_y = (r.y0 + r.y1) / 2
            L = owning_slot(mid_y)
            if L == "D":
                letter_rect = slots["D"]["letter"]
                incl = r.x1 > letter_rect.x1 + 1 and r.x0 <= col.x1
                out.write(f"span {span['text']!r} bbox={[round(x,1) for x in r]} mid_y={round(mid_y,1)} included={incl}\n")
for path in page.get_drawings():
    r = fitz.Rect(path.get("rect"))
    mid_y = (r.y0 + r.y1) / 2
    L = owning_slot(mid_y)
    if L == "D":
        letter_rect = slots["D"]["letter"]
        incl = r.x0 >= letter_rect.x1 and r.x0 <= col.x1 and not (r.height > 90 or r.width > 200)
        out.write(f"draw bbox={[round(x,1) for x in r]} mid_y={round(mid_y,1)} h={round(r.height,1)} w={round(r.width,1)} included={incl}\n")

out.close()
print("done")
