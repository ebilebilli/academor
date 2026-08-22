import importlib.util
import sys
import io
import re
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(r"C:\Users\user\Desktop\Academor")
spec = importlib.util.spec_from_file_location("rb", REPO / "scripts" / "rebuild_sat_math.py")
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

import pymupdf as fitz

pdf = rb.find_pdf(8)
doc = fitz.open(pdf)
pages = rb.find_module_pages(doc)
located = rb.find_marker_on_pages(doc, pages["math2"], pages["math2_end"], 8)
pidx, marker = located
page = doc[pidx]
markers = rb.question_markers(page)
y_bottom = rb.question_band_bottom(page, marker, markers)

col = fitz.Rect(marker["col_rect"])
band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, y_bottom)
choices = rb.choice_spans(page, band)
by_letter = {L: (lr, cr) for L, lr, cr in choices}
ordered = [(L, *by_letter[L]) for L in "ABCD"]
last_letter = ordered[3][1]
naive_bottom = min(y_bottom - 2, last_letter.y0 + 400)
hard_end = rb.find_gap_cutoff(page, col.x0, col.x1, last_letter.y1, naive_bottom)
top_limit = ordered[0][1].y0 - 3
order_letters = [L for L, _, _ in ordered]
tops = {L: lr.y0 for L, lr, _ in ordered}
range_bounds = [top_limit] + [tops[L] - 1 for L in order_letters[1:]] + [hard_end]

def default_slot(mid_y):
    if mid_y < top_limit or mid_y >= hard_end:
        return None
    for i in range(len(order_letters)):
        if range_bounds[i] <= mid_y < range_bounds[i+1]:
            return i
    return None

FRACTION_TOKEN_RE = re.compile(r"^[\-\u2212]?[A-Za-z0-9]{1,4}$")
LETTER_RE = re.compile(r"^[A-D]\)")
all_band_spans = []
narrow_candidates = []
d_scan = page.get_text("dict")
for block in d_scan["blocks"]:
    if block.get("type") != 0:
        continue
    for line in block.get("lines", []):
        for span in line.get("spans", []):
            r = fitz.Rect(span["bbox"])
            if r.height > 40 or not band.intersects(r):
                continue
            all_band_spans.append((r, span["text"]))
            if span.get("flags", 0) & 1:
                continue
            if r.width <= 22 and FRACTION_TOKEN_RE.match(span["text"].strip()):
                narrow_candidates.append(r)

def rkey(r):
    return (round(r.x0,1), round(r.y0,1), round(r.x1,1), round(r.y1,1))

def is_isolated_row(r1):
    for r, text in all_band_spans:
        if r is r1 or r.height > 22:
            continue
        stripped = text.strip()
        if not stripped or LETTER_RE.match(stripped) or all(rb.is_pua_char(ch) for ch in stripped):
            continue
        y_overlap = min(r.y1, r1.y1) - max(r.y0, r1.y0)
        if y_overlap <= 2:
            continue
        min_w = min(r.width, r1.width)
        x_overlap = (min(r.x1, r1.x1) - max(r.x0, r1.x0)) if min_w > 0 else -1
        if min_w > 0 and x_overlap / min_w > 0.5:
            continue
        print(f"  row-mate found for {rkey(r1)}: {text!r} {r}")
        return False
    return True

# find D's numerator "1"
target = None
for r in narrow_candidates:
    if 320 < r.y0 < 330 and 370 < r.x0 < 385:
        target = r
        print("candidate", r)

promote = set()
for r1 in narrow_candidates:
    s1 = default_slot((r1.y0+r1.y1)/2)
    if s1 is None:
        continue
    iso = is_isolated_row(r1)
    if not iso:
        continue
    for r2 in narrow_candidates:
        if r1 is r2:
            continue
        s2 = default_slot((r2.y0+r2.y1)/2)
        if s2 != s1+1:
            continue
        min_w = min(r1.width, r2.width)
        if min_w <= 0:
            continue
        x_overlap = min(r1.x1, r2.x1) - max(r1.x0, r2.x0)
        if x_overlap/min_w < 0.35:
            continue
        if -2 <= (r2.y0 - r1.y1) <= 8:
            print(f"PROMOTE {rkey(r1)} slot{s1}->slot{s2}")
            promote.add(rkey(r1))
            break

print("target in promote:", rkey(target) in promote if target else "no target found")
