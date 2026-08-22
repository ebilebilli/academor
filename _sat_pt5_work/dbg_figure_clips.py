"""Debug PT5 Math M1 figure clips for Q1/Q3/Q5/Q6."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
import pymupdf as fitz

doc = fitz.open(r"C:\Users\user\Desktop\sat-practice-test-5-digital (1).pdf")


def find_q_markers(page):
    by_n = {}
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        for line in b.get("lines", []):
            spans = line.get("spans", [])
            text = "".join(s["text"] for s in spans).strip()
            if not re.fullmatch(r"\d{1,2}", text):
                continue
            size = spans[0]["size"] if spans else 0
            r = fitz.Rect(line["bbox"])
            if 9.5 <= size <= 11.5 and 100 < r.y0 < 720 and r.x0 < 400:
                n = int(text)
                if n not in by_n or r.y0 < by_n[n].y0:
                    by_n[n] = r
    return sorted(by_n.items(), key=lambda x: (x[1].y0, x[1].x0))


def column_bounds(marker_x, page_w=612.0):
    mid = page_w / 2
    if marker_x < mid:
        return 36.0, mid - 8.0
    return mid + 8.0, page_w - 36.0


def choice_or_stem_y(page, marker, x0, x1):
    """Y of first choice A) or long prose stem below marker in column."""
    best = None
    for b in page.get_text("dict")["blocks"]:
        if b.get("type") != 0:
            continue
        bb = fitz.Rect(b["bbox"])
        if bb.y0 <= marker.y1 + 2:
            continue
        if bb.x1 < x0 or bb.x0 > x1:
            continue
        text = " ".join(
            "".join(s["text"] for s in line["spans"]) for line in b["lines"]
        ).strip()
        if re.match(r"^[A-D]\)", text):
            y = bb.y0
        elif len(text.split()) >= 8 and re.search(r"[A-Za-z]{4,}", text):
            y = bb.y0
        else:
            continue
        if best is None or y < best:
            best = y
    return best


def figure_clip(page, qnum):
    markers = find_q_markers(page)
    marker = next((r for n, r in markers if n == qnum), None)
    if marker is None:
        return None
    x0, x1 = column_bounds(marker.x0, page.rect.width)
    next_y = 730.0
    leftish = marker.x0 < page.rect.width / 2
    for n, r in markers:
        if r.y0 > marker.y0 + 5 and (r.x0 < page.rect.width / 2) == leftish:
            next_y = min(next_y, r.y0 - 4)
    limit = choice_or_stem_y(page, marker, x0, x1)
    y1_limit = min(next_y, limit - 3) if limit else next_y
    y0 = marker.y1 + 1

    rects = []
    for info in page.get_image_info(xrefs=True):
        r = fitz.Rect(info["bbox"])
        if r.height < 50 or r.width < 50 or r.y0 < 90:
            continue
        if r.x0 < x1 and r.x1 > x0 and r.y0 < y1_limit and r.y1 > y0:
            rects.append(r)
    for d in page.get_drawings():
        r = fitz.Rect(d["rect"])
        if r.width < 60 or r.height < 60:
            continue
        if r.x0 < x1 and r.x1 > x0 and r.y0 < y1_limit and r.y1 > y0:
            rects.append(r)

    # Table fallback: union of compact text blocks between marker and stem
    if not rects and limit:
        cells = []
        for b in page.get_text("dict")["blocks"]:
            if b.get("type") != 0:
                continue
            bb = fitz.Rect(b["bbox"])
            if not (y0 < bb.y0 and bb.y1 < limit and bb.x0 >= x0 - 5 and bb.x1 <= x1 + 5):
                continue
            t = " ".join(
                "".join(s["text"] for s in line["spans"]) for line in b["lines"]
            ).strip()
            if not t or len(t) > 60:
                continue
            # skip the stem lead-in line already excluded by limit; keep table cells
            if re.match(r"^[A-D]\)", t):
                continue
            cells.append(bb)
        if len(cells) >= 2:
            u = cells[0]
            for c in cells[1:]:
                u |= c
            rects.append(u)

    if not rects:
        return None
    u = rects[0]
    for r in rects[1:]:
        u |= r
    pad = 6
    return fitz.Rect(
        max(x0, u.x0 - pad),
        max(y0 - 2, u.y0 - pad),
        min(x1, u.x1 + pad),
        min(y1_limit, u.y1 + pad),
    )


# stem debug Q1
page = doc[33]
print("=== Q1 left-col blocks ===")
for b in page.get_text("dict")["blocks"]:
    if b.get("type") != 0:
        continue
    bb = fitz.Rect(b["bbox"])
    if bb.y0 <= 128 or bb.y0 > 360 or bb.x0 > 298:
        continue
    text = " ".join("".join(s["text"] for s in line["spans"]) for line in b["lines"]).strip()
    print(f"y0={bb.y0:.1f} nwords={len(text.split())} :: {text[:90]!r}")

print("\n=== algorithmic clips ===")
for q, pidx in [(1, 33), (3, 33), (5, 34), (6, 34)]:
    clip = figure_clip(doc[pidx], q)
    print(f"Q{q} pdf_page={pidx+1} clip={None if clip is None else tuple(round(x, 1) for x in clip)}")
    if clip:
        pix = doc[pidx].get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False, clip=clip)
        pix.save(rf"C:\Users\user\Desktop\Academor\_sat_pt5_work\fig_pt5_m1_q{q}_alg2.png")

# Q5 table: manual inspection of text between Q5 marker and following prose
page = doc[34]
print("\n=== Q5 region blocks ===")
for b in page.get_text("dict")["blocks"]:
    if b.get("type") != 0:
        continue
    bb = fitz.Rect(b["bbox"])
    if 350 < bb.y0 < 510 and bb.x0 < 300:
        text = " ".join("".join(s["text"] for s in line["spans"]) for line in b["lines"]).strip()
        print(f"{tuple(round(x,1) for x in bb)} :: {text[:100]!r}")
for d in page.get_drawings():
    r = fitz.Rect(d["rect"])
    if 380 < r.y0 < 470 and r.x0 < 250 and (r.width > 20 or r.height > 20):
        print("draw", tuple(round(x, 1) for x in r), f"w={r.width:.0f} h={r.height:.0f}")
