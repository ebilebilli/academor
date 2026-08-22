"""Rebuild SAT Math JSONs with:
  - tightly cropped figures/tables (images only where a real graphic exists)
  - answer options kept as plain text whenever the content is plain text/numbers
  - math symbols reconstructed as clean text (fractions -> "a/b", exponents -> <sup>)
    whenever that is possible without losing meaning
  - images used ONLY as a last resort, when a choice is a genuine graphic (a
    mini graph/plot) or contains glyphs that cannot be represented as text
    without breaking their meaning
"""

from __future__ import annotations

import base64
import importlib.util
import json
import re
from pathlib import Path

import pymupdf as fitz

REPO = Path(__file__).resolve().parents[1]
DESKTOP = Path(r"C:\Users\user\Desktop")
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"

spec = importlib.util.spec_from_file_location(
    "build_sat",
    REPO / "scripts" / "build_sat_practice_tests.py",
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

KEYS = build.KEYS
find_pdf = build.find_pdf
find_module_pages = build.find_module_pages
extract_pages = build.extract_pages
split_questions = build.split_questions
parse_mcq = build.parse_mcq
normalize_spaces = build.normalize_spaces
spr_answers = build.spr_answers
clean_page_text = build.clean_page_text


# ---------------------------------------------------------------------------
# Low level PDF helpers
# ---------------------------------------------------------------------------

def png_data_uri(page: fitz.Page, clip: fitz.Rect, zoom: float = 2.5) -> str:
    mat = fitz.Matrix(zoom, zoom)
    clip = fitz.Rect(clip) & page.rect
    if clip.is_empty or clip.width < 4 or clip.height < 4:
        raise ValueError(f"empty clip {clip}")
    pix = page.get_pixmap(matrix=mat, alpha=False, clip=clip)
    return "data:image/png;base64," + base64.b64encode(pix.tobytes("png")).decode("ascii")


def img_tag(uri: str, alt: str = "figure") -> str:
    return (
        f'<img alt="{alt}" src="{uri}" '
        f'style="max-width:100%;height:auto;vertical-align:middle;"/>'
    )


def is_directions_page(page: fitz.Page) -> bool:
    head = page.get_text("text")[:900].lower()
    return "directions" in head and ("27 questions" in head or "22 questions" in head)


# ---------------------------------------------------------------------------
# Question / choice marker detection
# ---------------------------------------------------------------------------

def question_markers(page: fitz.Page) -> list[dict]:
    """Return question number markers with column and bbox."""
    if is_directions_page(page):
        return []
    markers = []
    d = page.get_text("dict")
    page_w = page.rect.width
    mid = page_w / 2
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                if not re.fullmatch(r"[1-9]|1\d|2[0-2]", text):
                    continue
                size = float(span.get("size") or 0)
                if size < 9.8 or size > 11.5:
                    continue
                x0, y0, x1, y1 = span["bbox"]
                w = x1 - x0
                h = y1 - y0
                if w < 4.5 or w > 14 or h > 16:
                    continue
                if 35 <= x0 <= 70:
                    col = "left"
                    col_rect = fitz.Rect(36, 90, mid - 6, 740)
                elif mid + 8 <= x0 <= mid + 45:
                    col = "right"
                    col_rect = fitz.Rect(mid + 6, 90, page_w - 36, 740)
                else:
                    continue
                markers.append(
                    {
                        "num": int(text),
                        "bbox": fitz.Rect(span["bbox"]),
                        "col": col,
                        "col_rect": col_rect,
                    }
                )
    best: dict[tuple, dict] = {}
    for m in markers:
        key = (m["num"], m["col"])
        if key not in best or m["bbox"].y0 < best[key]["bbox"].y0:
            best[key] = m
    return sorted(best.values(), key=lambda m: (m["bbox"].y0, m["bbox"].x0))


def choice_spans(page: fitz.Page, band: fitz.Rect) -> list[tuple[str, fitz.Rect, fitz.Rect]]:
    """Return (letter, letter_rect, content_rect) for A-D in band."""
    found = []
    d = page.get_text("dict")
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"].strip()
                m = re.match(r"^([A-D])\)\s*(.*)$", text)
                if not m:
                    continue
                letter = m.group(1)
                rest = m.group(2)
                r = fitz.Rect(span["bbox"])
                if not band.intersects(r):
                    continue
                if rest:
                    letter_w = min(18.0, max(10.0, r.width * 0.28))
                    letter_rect = fitz.Rect(r.x0, r.y0, r.x0 + letter_w, r.y1)
                    content_rect = fitz.Rect(r.x0 + letter_w, r.y0, r.x1, r.y1)
                else:
                    letter_rect = r
                    content_rect = fitz.Rect(r.x1, r.y0, r.x1 + 4, r.y1)
                found.append((letter, letter_rect, content_rect))
    found.sort(key=lambda t: t[1].y0)
    out = []
    seen = set()
    for letter, letter_rect, content_rect in found:
        if letter in seen:
            continue
        seen.add(letter)
        out.append((letter, letter_rect, content_rect))
    return out


def find_gap_cutoff(page: fitz.Page, x0: float, x1: float, y_start: float, y_limit: float, gap: float = 22.0) -> float:
    """Scan for the first large vertical gap between text lines starting at
    y_start; return the y just after the line before the gap. Used to stop
    the last answer choice from swallowing unrelated content below it when
    the true end-of-question boundary couldn't be detected otherwise."""
    d = page.get_text("dict")
    spans = []
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                r = fitz.Rect(span["bbox"])
                if r.height > 40:
                    continue
                if r.y0 < y_start - 1 or r.y0 > y_limit:
                    continue
                if r.x1 < x0 or r.x0 > x1:
                    continue
                spans.append((r.y0, r.y1))
    spans.sort()
    cutoff = y_limit
    prev_end = y_start
    for y0, y1 in spans:
        if y0 - prev_end > gap:
            cutoff = prev_end + 4
            break
        prev_end = max(prev_end, y1)
    return cutoff


PUA_RANGES = ((0xE000, 0xF8FF), (0xF0000, 0xFFFFD), (0x100000, 0x10FFFD))

# Only these specific PUA codepoints are known, purely-decorative "stretched
# bracket" pieces (Adobe/Euclid symbol fonts draw a tall "( )" or fraction
# vinculum as several stacked glyph fragments with no meaning of their own).
# Any OTHER private-use glyph (radicals, unusual operators, etc.) is left
# in place on purpose so it fails the safe-text check below and the choice
# falls back to an image instead of silently dropping real math content.
SAFE_DROP_PUA = {0xF8EB, 0xF8EC, 0xF8ED, 0xF8F6, 0xF8F7, 0xF8F8}


def is_pua_char(ch: str) -> bool:
    cp = ord(ch)
    return any(lo <= cp <= hi for lo, hi in PUA_RANGES)


def strip_pua(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) not in SAFE_DROP_PUA)


def has_vinculum(page: fitz.Page, top: fitz.Rect, bot: fitz.Rect) -> bool:
    """A genuine PDF fraction is drawn as a numerator, a denominator, AND an
    actual short horizontal rule (the vinculum) between them. Two unrelated
    rows that happen to be narrow, x-aligned and a few points apart (e.g. two
    rows of a lookup table) never have this rule, so requiring its presence
    is what tells a real stacked fraction apart from a false-positive
    table-row/answer-row pairing."""
    y_lo, y_hi = top.y1 - 1.5, bot.y0 + 1.5
    x0 = min(top.x0, bot.x0) - 2
    x1 = max(top.x1, bot.x1) + 2
    for path in page.get_drawings():
        r = fitz.Rect(path.get("rect"))
        if r.height > 3 or r.width < 4:
            continue
        mid_y = (r.y0 + r.y1) / 2
        if not (y_lo <= mid_y <= y_hi):
            continue
        if r.x0 < x0 - 3 or r.x1 > x1 + 3:
            continue
        return True
    return False


def merge_fraction_stacks(page: fitz.Page, spans: list[dict]) -> list[dict]:
    """Detect a numerator stacked directly above a denominator (a fraction
    rendered by the PDF as two short numeric runs with a bar between them)
    and linearize it as "num/den" so it can stay as plain text."""
    n = len(spans)
    used = [False] * n

    OPERATOR_RE = re.compile(r"[+\-\u2212=<>\u2264\u2265\u2260]")

    def is_isolated(idx: int, other_idx: int) -> bool:
        # A genuine numerator/denominator has its own row to itself, aside
        # from a short label that is simply part of the same answer (e.g.
        # the "0," before a "(0, 1/10)" coordinate). What disqualifies a
        # candidate is a row-mate that carries an actual comparison/math
        # operator (e.g. the "x >" and "y >" in "x > 0" / "y > 0"), which
        # means the whole row is really one ordinary clause, not a
        # fraction stacked on its own.
        b = spans[idx]["bbox"]
        for k, other in enumerate(spans):
            if k == idx or k == other_idx:
                continue
            ob = other["bbox"]
            if ob.height > 22 or not OPERATOR_RE.search(other["text"]):
                continue
            y_overlap = min(ob.y1, b.y1) - max(ob.y0, b.y0)
            if y_overlap <= 2:
                continue
            min_w = min(ob.width, b.width)
            x_overlap = (min(ob.x1, b.x1) - max(ob.x0, b.x0)) if min_w > 0 else -1
            if min_w > 0 and x_overlap / min_w > 0.5:
                continue
            return False
        return True

    merged: list[dict] = []
    for i in range(n):
        if used[i]:
            continue
        s1 = spans[i]
        b1 = s1["bbox"]
        if b1.width > 22 or not re.fullmatch(r"[\-\u2212]?[A-Za-z0-9]{1,4}", s1["text"].strip()):
            merged.append(s1)
            continue
        partner = None
        for j in range(n):
            if j == i or used[j]:
                continue
            s2 = spans[j]
            b2 = s2["bbox"]
            if b2.width > 22 or not re.fullmatch(r"[\-\u2212]?[A-Za-z0-9]{1,4}", s2["text"].strip()):
                continue
            min_w = min(b1.width, b2.width)
            if min_w <= 0:
                continue
            x_overlap = min(b1.x1, b2.x1) - max(b1.x0, b2.x0)
            if x_overlap / min_w < 0.35:
                continue
            # A real fraction's numerator/denominator sit only a few
            # points apart (just enough room for the vinculum, ~4pt in
            # these PDFs); two unrelated single-line answers stacked in
            # the same column are a full row apart (~6pt or more here).
            gap = (b2.y0 - b1.y1) if b1.y0 < b2.y0 else (b1.y0 - b2.y1)
            if not (-2 <= gap <= 5):
                continue
            if not (is_isolated(i, j) and is_isolated(j, i)):
                continue
            top_r, bot_r = (b1, b2) if b1.y0 < b2.y0 else (b2, b1)
            if not has_vinculum(page, top_r, bot_r):
                continue
            partner = j
            break
        if partner is not None:
            s2 = spans[partner]
            top, bot = (s1, s2) if s1["bbox"].y0 < s2["bbox"].y0 else (s2, s1)
            merged.append(
                {
                    "text": f"{top['text'].strip()}/{bot['text'].strip()}",
                    "bbox": s1["bbox"] | s2["bbox"],
                    "flags": 0,
                    "is_fraction": True,
                }
            )
            used[i] = True
            used[partner] = True
        else:
            merged.append(s1)
    return merged


def option_bounds(page: fitz.Page, marker: dict, y_bottom: float) -> dict[str, fitz.Rect] | None:
    """Compute a tight rectangle per answer choice (A-D), strictly bounded so
    that content belonging to a neighboring choice (or a different question
    entirely) can never bleed into another choice's crop/text region."""
    col = fitz.Rect(marker["col_rect"])
    band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, y_bottom)
    choices = choice_spans(page, band)
    if len(choices) < 4:
        return None
    by_letter = {L: (letter_rect, content_rect) for L, letter_rect, content_rect in choices}
    if any(L not in by_letter for L in "ABCD"):
        return None
    ordered = [(L, *by_letter[L]) for L in "ABCD"]

    # A choice's own "A)"/"B)"/... label sits at the TOP of a normal single-
    # or multi-line (wrapped prose) answer, so any content between this
    # choice's letter and the NEXT choice's letter belongs to this choice
    # no matter how far down it wraps. The one exception is a stacked
    # fraction, where the label is vertically CENTERED against the whole
    # fraction and so the numerator can sit a few points ABOVE the choice's
    # own letter (i.e. still inside the tail end of the *previous* choice's
    # default range). We handle the common case with a strict sequential
    # range per choice, and rescue only genuine fraction-numerator glyphs
    # (short, narrow, numeric tokens right above the next letter) into the
    # choice that follows.
    last_letter = ordered[3][1]
    naive_bottom = min(y_bottom - 2, last_letter.y0 + 400)
    hard_end = find_gap_cutoff(page, col.x0, col.x1, last_letter.y1, naive_bottom)
    top_limit = ordered[0][1].y0 - 3

    slots: dict[str, dict] = {L: {"letter": letter_rect, "content": content_rect} for L, letter_rect, content_rect in ordered}
    order_letters = [L for L, _, _ in ordered]
    tops = {L: letter_rect.y0 for L, letter_rect, _ in ordered}
    letter_centers = [(letter_rect.y0 + letter_rect.y1) / 2 for _, letter_rect, _ in ordered]
    # The very first range starts at top_limit (not letter A's own top) so
    # that content sitting in the few points between top_limit and the
    # first letter (e.g. a raised superscript belonging to choice A
    # itself) is never silently dropped into a no-man's-land gap.
    range_bounds = [top_limit] + [tops[L] - 1 for L in order_letters[1:]] + [hard_end]

    def default_slot(mid_y: float) -> int | None:
        if mid_y < top_limit or mid_y >= hard_end:
            return None
        for i in range(len(order_letters)):
            if range_bounds[i] <= mid_y < range_bounds[i + 1]:
                return i
        return None

    def nearest_slot_by_center(mid_y: float) -> int | None:
        best_i, best_d = None, None
        for i, c in enumerate(letter_centers):
            dd = abs(mid_y - c)
            if best_d is None or dd < best_d:
                best_i, best_d = i, dd
        return best_i

    # A choice's content normally falls strictly between its own letter and
    # the next letter (handled by default_slot above), EXCEPT a stacked
    # fraction's numerator, which can sit a touch above its own choice's
    # letter -- i.e. still technically inside the tail of the *previous*
    # choice's default range. We only reclassify a span into the next
    # choice when it forms a genuine numerator/denominator PAIR with
    # another narrow token that already defaults into that next choice
    # (same test merge_fraction_stacks uses: narrow, numeric-shaped,
    # x-aligned, vertically adjacent). A lone short algebra token (a
    # single "x", "y" or digit that is simply the tail of a one-line
    # answer) never matches this pairing test, so ordinary short answers
    # are left alone.
    FRACTION_TOKEN_RE = re.compile(r"^[\-\u2212]?[A-Za-z0-9]{1,4}$")
    LETTER_RE = re.compile(r"^[A-D]\)")
    all_band_spans: list[tuple[fitz.Rect, str, int]] = []
    narrow_candidates: list[fitz.Rect] = []
    d_scan = page.get_text("dict")
    for block in d_scan["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                r = fitz.Rect(span["bbox"])
                if r.height > 40 or not band.intersects(r):
                    continue
                all_band_spans.append((r, span["text"], span.get("flags", 0)))
                if span.get("flags", 0) & 1:
                    continue
                if r.width <= 22 and FRACTION_TOKEN_RE.match(span["text"].strip()):
                    narrow_candidates.append(r)

    promote: set[tuple] = set()

    def rkey(r: fitz.Rect) -> tuple:
        return (round(r.x0, 1), round(r.y0, 1), round(r.x1, 1), round(r.y1, 1))

    def is_isolated_row(r1: fitz.Rect) -> bool:
        # A genuine fraction numerator/denominator has its own row entirely
        # to itself (nothing beside it at that height except the choice's
        # own letter, a bracket, or the fraction's other half). An
        # ordinary equation token ("y", "x", a digit, ...) shares its row
        # with the rest of that same equation ("=", other operands, ...),
        # so it is NOT isolated.
        for r, text, flags in all_band_spans:
            if r is r1 or r.height > 22 or flags & 1:
                continue
            stripped = text.strip()
            if not stripped or LETTER_RE.match(stripped) or all(is_pua_char(ch) for ch in stripped):
                continue
            y_overlap = min(r.y1, r1.y1) - max(r.y0, r1.y0)
            if y_overlap <= 2:
                continue
            min_w = min(r.width, r1.width)
            x_overlap = (min(r.x1, r1.x1) - max(r.x0, r1.x0)) if min_w > 0 else -1
            if min_w > 0 and x_overlap / min_w > 0.5:
                continue  # stacked with r1 (the fraction's other half), not a row-mate
            return False
        return True

    for r1 in narrow_candidates:
        s1 = default_slot((r1.y0 + r1.y1) / 2)
        if s1 is None or not is_isolated_row(r1):
            continue
        for r2 in narrow_candidates:
            if r1 is r2:
                continue
            s2 = default_slot((r2.y0 + r2.y1) / 2)
            if s2 != s1 + 1:
                continue
            min_w = min(r1.width, r2.width)
            if min_w <= 0:
                continue
            x_overlap = min(r1.x1, r2.x1) - max(r1.x0, r2.x0)
            if x_overlap / min_w < 0.35:
                continue
            # A true stacked fraction has its numerator and denominator
            # only a few points apart (just enough room for the
            # vinculum, ~4pt in these PDFs). Two unrelated single-line
            # answers stacked in the same column are a full row apart
            # (~6pt or more here), so a tighter cutoff tells them apart.
            if -2 <= (r2.y0 - r1.y1) <= 5 and has_vinculum(page, r1, r2):
                promote.add(rkey(r1))
                break

    def owning_slot(
        mid_y: float, r: fitz.Rect | None = None, flags: int = 0, text: str | None = None
    ) -> str | None:
        # A raised exponent/superscript -- or a piece of a tall stretched
        # bracket/vinculum glyph drawn as several stacked fragments -- sits
        # well above its own choice's letter (sometimes even above the
        # strict per-choice range), so these are matched to whichever
        # letter they are vertically closest to instead of by sequential
        # range containment.
        is_bracket_piece = bool(text) and len(text) <= 4 and all(is_pua_char(ch) for ch in text)
        if (flags & 1 or is_bracket_piece) and r is not None and r.width <= 22:
            if mid_y < top_limit - 10 or mid_y >= hard_end:
                return None
            idx = nearest_slot_by_center(mid_y)
            return order_letters[idx] if idx is not None else None
        idx = default_slot(mid_y)
        if idx is None:
            return None
        if r is not None and idx + 1 < len(order_letters) and rkey(r) in promote:
            idx += 1
        return order_letters[idx]

    bounds: dict[str, fitz.Rect] = {}
    for L, s in slots.items():
        letter_rect = s["letter"]
        content_rect = s["content"]
        r = fitz.Rect(
            letter_rect.x1 + 1,
            letter_rect.y0 - 2,
            max(content_rect.x1, letter_rect.x1 + 20),
            letter_rect.y1 + 2,
        )
        bounds[L] = r

    d = page.get_text("dict")
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                r = fitz.Rect(span["bbox"])
                # Decorative full-column dividers (dotted vertical rules
                # between the two answer columns) render as one tall,
                # narrow "span" and must never be treated as answer content.
                if r.height > 40:
                    continue
                mid_y = (r.y0 + r.y1) / 2
                L = owning_slot(mid_y, r, span.get("flags", 0), span.get("text"))
                if L is None:
                    continue
                letter_rect = slots[L]["letter"]
                if r.x1 <= letter_rect.x1 + 1 or r.x0 > col.x1:
                    continue
                b = bounds[L]
                bounds[L] = fitz.Rect(
                    min(b.x0, letter_rect.x1 + 1),
                    min(b.y0, r.y0 - 1),
                    max(b.x1, r.x1 + 3),
                    max(b.y1, min(hard_end, r.y1 + 1)),
                )

    for path in page.get_drawings():
        r = fitz.Rect(path.get("rect"))
        # Only pull in small strokes (fraction bars, radicals) or genuinely
        # embedded figure-sized drawings; anything else is page furniture
        # (e.g. the dotted column divider, which spans the whole page).
        if r.height > 90 or r.width > 200:
            continue
        mid_y = (r.y0 + r.y1) / 2
        L = owning_slot(mid_y)
        if L is None:
            continue
        letter_rect = slots[L]["letter"]
        if r.x0 < letter_rect.x1 or r.x0 > col.x1:
            continue
        b = bounds[L]
        bounds[L] = fitz.Rect(
            b.x0,
            min(b.y0, r.y0 - 1),
            max(b.x1, r.x1 + 2),
            max(b.y1, min(hard_end, r.y1 + 1)),
        )

    for L in bounds:
        b = bounds[L]
        b.x1 = min(b.x1, col.x1 - 6)
        if b.height < 10:
            b.y1 = b.y0 + 12
        if b.width < 14:
            b.x1 = b.x0 + 14
        bounds[L] = b & page.rect
    return bounds


def collect_region_spans(page: fitz.Page, rect: fitz.Rect) -> list[dict]:
    spans = []
    d = page.get_text("dict", clip=rect)
    for block in d.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                r = fitz.Rect(span["bbox"])
                if r.height > 40:
                    continue
                cleaned = strip_pua(span["text"])
                if not cleaned:
                    continue
                spans.append({"text": cleaned, "bbox": r, "flags": span.get("flags", 0)})
    return spans


# ---------------------------------------------------------------------------
# Text reconstruction (prefer real text over images whenever possible)
# ---------------------------------------------------------------------------

# Characters that are safe to render as plain/HTML text without an image.
SAFE_OPTION_RE = re.compile(
    r"^[A-Za-z0-9\s.,+\-\u2212\u2013\u2014*/=<>()\[\]{}:;'\"\u2018\u2019\u201c\u201d\u2026|°%_√π≤≥≠±⁄?!&@$]*$"
)


def _center_y(s: dict) -> float:
    return (s["bbox"].y0 + s["bbox"].y1) / 2


def group_lines(spans: list[dict], tol: float = 5.0) -> list[dict]:
    """Cluster spans into visual lines using vertical CENTER, not top, so a
    stacked fraction (whose bbox top sits well above the surrounding text's
    top, but whose center lines up with it) stays on the same line as the
    text around it instead of becoming its own out-of-order line."""
    spans = sorted(spans, key=_center_y)
    lines: list[dict] = []
    for s in spans:
        placed = False
        for line in lines:
            if abs(line["y"] - _center_y(s)) <= tol:
                line["spans"].append(s)
                line["y"] = sum(_center_y(x) for x in line["spans"]) / len(line["spans"])
                placed = True
                break
        if not placed:
            lines.append({"y": _center_y(s), "spans": [s]})
    lines.sort(key=lambda l: l["y"])
    for line in lines:
        line["spans"].sort(key=lambda s: s["bbox"].x0)
    return lines


def looks_like_scattered_graphic(page: fitz.Page, rect: fitz.Rect, lines: list[dict], fraction_count: int) -> bool:
    """Heuristics to catch mini graphs/plots whose axis-tick numbers and
    labels happen to consist of "safe" characters but are not a coherent
    textual answer (e.g. several isolated numbers scattered vertically)."""
    if fraction_count > 1:
        return True
    if len(lines) > 3:
        # Wrapped prose (a long sentence/paragraph answer) legitimately
        # spans many lines, but each line fills most of the available
        # width. A scattered mini-graph's "lines" are really isolated
        # axis ticks/labels: short, and not all roughly left-aligned like
        # real text flow. Only treat many lines as a graphic when they
        # do NOT look like continuous flowing text.
        widths = [line["spans"][-1]["bbox"].x1 - line["spans"][0]["bbox"].x0 for line in lines]
        avg_width = sum(widths) / len(widths)
        left_edges = [line["spans"][0]["bbox"].x0 for line in lines]
        left_spread = max(left_edges) - min(left_edges)
        prose_like = avg_width > 0.55 * rect.width and left_spread < 0.25 * rect.width
        if not prose_like:
            return True
    # A real plotted curve/axis typically produces many short vector paths.
    drawing_hits = 0
    for path in page.get_drawings():
        r = fitz.Rect(path.get("rect"))
        if rect.intersects(r) and r.get_area() > 0:
            drawing_hits += 1
            if drawing_hits > 4:
                return True
    return False


def reconstruct_region_text(page: fitz.Page, rect: fitz.Rect) -> str | None:
    """Best-effort reconstruction of the text inside rect as clean HTML-safe
    text (fractions -> a/b, true exponents -> <sup>). Returns None if the
    region contains content that cannot be represented as text without
    losing meaning (e.g. a real graphic, or unmapped symbol-font glyphs)."""
    raw_spans = collect_region_spans(page, rect)
    if not raw_spans:
        return None
    merged = merge_fraction_stacks(page, raw_spans)
    plain_concat = "".join(s["text"] for s in merged)
    if not SAFE_OPTION_RE.match(plain_concat):
        return None
    fraction_count = sum(1 for s in merged if s.get("is_fraction"))
    lines = group_lines(merged)
    if looks_like_scattered_graphic(page, rect, lines, fraction_count):
        return None
    line_texts = [render_line(line) for line in lines]
    text = " ".join(t.strip() for t in line_texts if t.strip())
    # Strip page furniture that sometimes sits just below the last choice
    # (module banner, "CONTINUE" footer) if it leaked into the crop band.
    text = strip_page_furniture(text)
    text = fix_symbol_words(text)
    return text or None


def render_line(line: dict) -> str:
    parts = []
    prev_x1 = None
    for s in line["spans"]:
        t = s["text"]
        core = t.strip()
        # Only wrap a genuine short exponent-like token in <sup>. A comma
        # or space inside a "raised" span usually just means the PDF
        # vertically centered ordinary text (e.g. ", 0" beside a tall
        # stacked fraction) against something taller nearby -- not a real
        # superscript -- so leave that as plain text.
        if s["flags"] & 1 and re.fullmatch(r"[A-Za-z0-9\u2212\-+]{1,3}", core):
            t_out = f"<sup>{core}</sup>"
        else:
            t_out = t
        if prev_x1 is not None:
            gap = s["bbox"].x0 - prev_x1
            needs_space = gap > 1.2
            already_spaced = t.startswith(" ") or (parts and parts[-1].endswith((" ", ">")))
            if needs_space and not already_spaced:
                parts.append(" ")
        parts.append(t_out)
        prev_x1 = s["bbox"].x1
    return "".join(parts)


def apply_sibling_parens(texts: dict[str, str]) -> dict[str, str]:
    """If most choices in a question are wrapped in parens (e.g. coordinate
    pairs), make the rest consistent so we don't drop a bracket that was
    only lost because its glyphs were drawn with a stretched symbol font."""
    wrapped = [t for t in texts.values() if t.startswith("(") and t.endswith(")")]
    if len(wrapped) >= 2:
        for L, t in list(texts.items()):
            if not (t.startswith("(") and t.endswith(")")):
                texts[L] = f"({t})"
    return texts


# ---------------------------------------------------------------------------
# Figure / table cropping (unchanged approach: only crop the actual graphic)
# ---------------------------------------------------------------------------

def figure_clip_for_question(page: fitz.Page, marker: dict, y_bottom: float) -> fitz.Rect | None:
    """Crop only the figure/table image in the question column band."""
    col = fitz.Rect(marker["col_rect"])
    choices = choice_spans(page, fitz.Rect(col.x0, marker["bbox"].y1, col.x1, y_bottom))
    fig_bottom = choices[0][1].y0 - 2 if choices else y_bottom - 2
    band = fitz.Rect(col.x0, marker["bbox"].y1 + 1, col.x1, fig_bottom)
    candidates = []
    for info in page.get_image_info():
        r = fitz.Rect(info["bbox"])
        if r.y1 < 95 or r.height < 48 or r.width < 48:
            continue
        if r.width > col.width * 1.05:
            continue
        inter = r & band
        if inter.is_empty:
            continue
        if inter.width < 45 or inter.height < 45:
            continue
        if inter.get_area() < 0.35 * r.get_area():
            continue
        candidates.append(r)
    if not candidates:
        for path in page.get_drawings():
            r = fitz.Rect(path.get("rect"))
            inter = r & band
            if inter.is_empty:
                continue
            if inter.width >= 70 and inter.height >= 70:
                candidates.append(inter)
    if not candidates:
        band2 = fitz.Rect(col.x0, marker["bbox"].y1 + 1, col.x1, y_bottom - 2)
        for info in page.get_image_info():
            r = fitz.Rect(info["bbox"])
            if r.width > col.width * 1.05 or r.height < 40:
                continue
            inter = r & band2
            if inter.is_empty or inter.width < 40 or inter.height < 40:
                continue
            if inter.get_area() >= 0.35 * r.get_area():
                candidates.append(r)
    if not candidates:
        rules = []
        for path in page.get_drawings():
            r = fitz.Rect(path.get("rect"))
            if r.width < 35:
                continue
            if r.height > 1.8 and abs(r.y1 - r.y0) > 1.8:
                continue
            if not band.intersects(r) and not (
                col.x0 <= r.x0 <= col.x1 and marker["bbox"].y1 < r.y0 < y_bottom
            ):
                continue
            rules.append(fitz.Rect(r.x0, r.y0 - 0.5, r.x1, r.y0 + 0.5))
        if len(rules) >= 3:
            union = rules[0]
            for r in rules[1:]:
                union |= r
            union = fitz.Rect(union.x0 - 6, union.y0 - 8, union.x1 + 6, union.y1 + 8)
            candidates.append(union & col & page.rect)
    if not candidates:
        return None
    clip = max(candidates, key=lambda r: r.get_area())
    if clip.width > col.width * 0.98 and clip.height > 350:
        return None
    clip = fitz.Rect(clip.x0 - 3, clip.y0 - 3, clip.x1 + 3, clip.y1 + 3) & page.rect
    return clip


def find_marker_on_pages(doc, start: int, end: int, qnum: int) -> tuple[int, dict] | None:
    """Pick the best matching question badge in the module page range."""
    candidates: list[tuple[int, int, dict]] = []
    for i in range(start, end):
        page = doc[i]
        for m in question_markers(page):
            if m["num"] != qnum:
                continue
            score = 0
            col = m["col_rect"]
            band = fitz.Rect(col.x0, m["bbox"].y1, col.x1, min(740, m["bbox"].y1 + 280))
            choices = choice_spans(page, band)
            if len(choices) >= 4:
                score += 100
            for info in page.get_image_info():
                r = fitz.Rect(info["bbox"])
                if r.width > col.width * 1.05 or r.height < 50:
                    continue
                if (r & band).get_area() > 2000:
                    score += 40
                    break
            score += max(0, 30 - abs(i - start))
            candidates.append((score, i, m))
    if not candidates:
        return None
    candidates.sort(key=lambda t: (-t[0], t[1]))
    _, pidx, marker = candidates[0]
    return pidx, marker


def question_band_bottom(page: fitz.Page, marker: dict, all_markers: list[dict]) -> float:
    """Bottom y of this question: next same-column marker or choice block end or footer."""
    same = [
        m
        for m in all_markers
        if m["col"] == marker["col"] and m["bbox"].y0 > marker["bbox"].y0 + 5
    ]
    if same:
        return same[0]["bbox"].y0 - 4
    col = marker["col_rect"]
    choices = choice_spans(page, fitz.Rect(col.x0, marker["bbox"].y1, col.x1, 740))
    # Safety cap: a single question block rarely spans more than this.
    hard_cap = min(740, marker["bbox"].y0 + 620)
    if choices:
        # The last choice's own label often sits several lines above the
        # rest of its content (e.g. a multi-row lookup table), so a flat
        # "+36" buffer can truncate it. Scan forward for the first real
        # blank gap instead of guessing a fixed height.
        bottom = find_gap_cutoff(page, col.x0, col.x1, choices[-1][1].y1, hard_cap) + 4
    else:
        bottom = hard_cap
    return min(bottom, hard_cap)


def fix_symbol_words(text: str) -> str:
    """Some of these PDFs map a literal '$' or minus-sign glyph to a
    spelled-out accessibility label ("dollar sign", "negative") instead of
    the symbol itself. Collapse those back to the real symbol so plain
    text reads naturally instead of "dollar sign 25" / "negative 6"."""
    text = re.sub(r"dollar sign\s*", "$", text, flags=re.I)
    text = re.sub(r"\s*percent sign", "%", text, flags=re.I)
    text = re.sub(r"\bnegative\s+(?=\d)", "-", text, flags=re.I)
    return text


def strip_page_furniture(text: str) -> str:
    """Drop trailing page furniture ("Module 1/2", "CONTINUE", ...) that
    sometimes leaks into extracted text wherever it starts."""
    text = re.split(r"\bModule\s*[12]\b", text, maxsplit=1, flags=re.I)[0]
    text = re.split(r"\bCONTINUE\b", text, maxsplit=1)[0]
    return re.sub(r"\s+", " ", text).strip()


def clean_stem_text(stem: str) -> str:
    stem = normalize_spaces(stem)
    stem = re.sub(
        r"^.*?(?=\b(?:The |What |Which |If |For |In |On |A |An |How |Given |Scott |Note:|P |N |C ))",
        "",
        stem,
    )
    return fix_symbol_words(strip_page_furniture(stem))


def looks_like_bad_math_text(text: str) -> bool:
    """Conservative check: only flag text that is genuinely unrenderable
    (leftover symbol-font glyphs or a decode failure), not merely text that
    happens to contain digits/operators."""
    if not text:
        return True
    if any(is_pua_char(ch) for ch in text):
        return True
    if "\ufffd" in text:
        return True
    # Symbol-font glyphs (inequality signs, stretched parens, etc.) that
    # got mapped to plain ASCII stand-ins by the PDF's broken font encoding
    # show up as stray "#" / "^" characters with no legitimate meaning of
    # their own in an SAT question stem.
    if "#" in text or "^" in text:
        return True
    return False


def stem_clip_html(
    page: fitz.Page,
    marker: dict,
    y_bottom: float,
    fig: fitz.Rect | None,
) -> str:
    """Crop stem text/equations (excluding figure and answer choices)."""
    col = fitz.Rect(marker["col_rect"])
    choices = choice_spans(page, fitz.Rect(col.x0, marker["bbox"].y1, col.x1, y_bottom))
    y1 = choices[0][1].y0 - 3 if choices else y_bottom - 3
    y0 = marker["bbox"].y1 + 2
    if fig is not None:
        if fig.y1 + 4 < y1:
            y0 = max(y0, fig.y1 + 2)
        else:
            y1 = min(y1, fig.y0 - 2)
    if y1 - y0 < 18:
        return ""
    clip = fitz.Rect(col.x0, y0, col.x1, y1) & page.rect
    try:
        return f"<p>{img_tag(png_data_uri(page, clip, zoom=2.4), 'question')}</p>"
    except ValueError:
        return ""


# ---------------------------------------------------------------------------
# Question builders
# ---------------------------------------------------------------------------

def build_math_question(
    doc,
    qnum: int,
    body: str,
    ans: str,
    page_start: int,
    page_end: int,
    qid: int,
) -> dict:
    is_spr = len(ans) != 1 or ans not in "ABCD"
    parsed = parse_mcq(body)
    raw_stem = parsed[0] if parsed else body
    stem = clean_stem_text(raw_stem)

    located = find_marker_on_pages(doc, page_start, page_end, qnum)
    fig_html = ""
    option_html: dict[str, str] | None = None

    if located:
        pidx, marker = located
        page = doc[pidx]
        markers = question_markers(page)
        y_bottom = question_band_bottom(page, marker, markers)
        fig = figure_clip_for_question(page, marker, y_bottom)
        if fig is not None:
            try:
                fig_html = f"<p>{img_tag(png_data_uri(page, fig), 'figure')}</p>"
            except ValueError:
                fig_html = ""

        if not is_spr:
            bounds = option_bounds(page, marker, y_bottom)
            if bounds:
                option_html = {}
                for L in "ABCD":
                    rect = bounds[L]
                    text = reconstruct_region_text(page, rect)
                    if text:
                        option_html[L] = text
                    else:
                        try:
                            option_html[L] = img_tag(
                                png_data_uri(page, rect, zoom=2.8), f"option {L}"
                            )
                        except ValueError:
                            option_html = None
                            break
                if option_html:
                    option_html = apply_sibling_parens(option_html)

        if looks_like_bad_math_text(stem):
            stem_img = stem_clip_html(page, marker, y_bottom, fig)
            if stem_img:
                fig_html = f"{fig_html}{stem_img}"
                stem = ""

    if is_spr:
        return {
            "id": qid,
            "question": f"{fig_html}<p>{stem}</p>",
            "question_type": "spr",
            "spr_correct_answers": spr_answers(ans),
            "spr_max_length": 6,
            "answer_key": f"<p><strong>Correct Answer: {ans}</strong></p>",
        }

    text_options = (
        [fix_symbol_words(strip_page_furniture(normalize_spaces(o))) for o in parsed[1]]
        if parsed
        else None
    )
    if option_html:
        options = [option_html[L] for L in "ABCD"]
        correct = option_html[ans]
    elif (
        text_options
        and len(text_options) == 4
        and len(set(text_options)) == 4
        and not any(looks_like_bad_math_text(o) for o in text_options)
    ):
        options = text_options
        correct = options[ord(ans) - ord("A")]
    else:
        options = ["A", "B", "C", "D"]
        correct = ans

    stem_html = f"<p>{stem}</p>" if stem else ""
    return {
        "id": qid,
        "question": f"{fig_html}{stem_html}",
        "options": options,
        "correct": correct,
        "answer_key": f"<p><strong>Correct Answer: {ans}</strong></p>",
    }


def build_math(doc, pages, keys, test_num: int) -> dict:
    m1 = split_questions(extract_pages(doc, pages["math1"], pages["math1_end"]), max_n=27)
    m2 = split_questions(extract_pages(doc, pages["math2"], pages["math2_end"]), max_n=27)
    items = []
    for local in range(1, 23):
        if local not in m1:
            raise KeyError(f"PT{test_num} Math M1 missing Q{local}")
        items.append(
            build_math_question(
                doc,
                local,
                m1[local],
                keys["math_m1"][local - 1],
                pages["math1"],
                pages["math1_end"],
                local,
            )
        )
    for local in range(1, 23):
        if local not in m2:
            raise KeyError(f"PT{test_num} Math M2 missing Q{local}")
        items.append(
            build_math_question(
                doc,
                local,
                m2[local],
                keys["math_m2"][local - 1],
                pages["math2"],
                pages["math2_end"],
                22 + local,
            )
        )
    assert len(items) == 44
    return {
        "title": f"SAT Practice Test {test_num} Math",
        "category_name": "SAT Math",
        "service": "sat",
        "is_sat": True,
        "sat_section": "algebra",
        "time_limit_minutes": 70,
        "questions": items,
    }


def process(test_num: int) -> str:
    pdf = find_pdf(test_num)
    if not pdf:
        return f"SKIP PT{test_num}: no pdf"
    if test_num not in KEYS:
        return f"SKIP PT{test_num}: no keys"
    doc = fitz.open(pdf)
    pages = find_module_pages(doc)
    if pages.get("math1") is None or pages.get("math2") is None:
        return f"FAIL PT{test_num}: math pages {pages}"
    data = build_math(doc, pages, KEYS[test_num], test_num)
    out = OUT_DIR / f"sat_practice_test_{test_num}_math.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    with_fig = sum(1 for q in data["questions"] if 'alt="figure"' in q["question"])
    with_stem_img = sum(1 for q in data["questions"] if 'alt="question"' in q["question"])
    mcq = [q for q in data["questions"] if q.get("options")]
    opt_img = sum(
        1 for q in mcq if any(isinstance(o, str) and o.startswith("<img") for o in q["options"])
    )
    opt_img_count = sum(
        sum(1 for o in q["options"] if isinstance(o, str) and o.startswith("<img")) for q in mcq
    )
    return (
        f"OK PT{test_num} math -> {out.name} "
        f"fig={with_fig} stem_img={with_stem_img} mcq={len(mcq)} "
        f"q_with_img_opt={opt_img} img_opts_total={opt_img_count}"
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for n in sorted(KEYS):
        print(process(n), flush=True)


if __name__ == "__main__":
    main()
