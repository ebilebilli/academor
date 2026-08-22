"""Rebuild SAT Math JSONs with properly cropped figures and math option images."""

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


def png_data_uri(page: fitz.Document | fitz.Page, clip: fitz.Rect, zoom: float = 2.5) -> str:
    page = page if isinstance(page, fitz.Page) else page
    mat = fitz.Matrix(zoom, zoom)
    # clamp clip to page
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
                # Badge digits ~5-12pt wide
                if w < 4.5 or w > 14 or h > 16:
                    continue
                # Badge sits in left gutter of each column
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
                # Estimate letter-only width when "A) value" is one span
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


def option_clips(page: fitz.Page, marker: dict, y_bottom: float) -> dict[str, fitz.Rect] | None:
    col = fitz.Rect(marker["col_rect"])
    band = fitz.Rect(col.x0, marker["bbox"].y1, col.x1, y_bottom)
    choices = choice_spans(page, band)
    if len(choices) < 4:
        return None
    by_letter = {letter: (letter_rect, content_rect) for letter, letter_rect, content_rect in choices}
    if any(L not in by_letter for L in "ABCD"):
        return None
    ordered = [(L, by_letter[L][0], by_letter[L][1]) for L in "ABCD"]
    letter_ys = {L: (letter_rect.y0 + letter_rect.y1) / 2 for L, letter_rect, _ in ordered}

    def nearest_letter(mid_y: float) -> str:
        return min(letter_ys, key=lambda L: abs(letter_ys[L] - mid_y))

    # Seed each option with its letter/content rect
    bounds: dict[str, fitz.Rect] = {}
    for L, letter_rect, content_rect in ordered:
        r = fitz.Rect(letter_rect.x1 + 1, letter_rect.y0 - 2, max(content_rect.x1, letter_rect.x1 + 20), letter_rect.y1 + 2)
        bounds[L] = r

    d = page.get_text("dict")
    first_choice_y = ordered[0][1].y0 - 6
    for block in d["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                r = fitz.Rect(span["bbox"])
                mid_y = (r.y0 + r.y1) / 2
                if mid_y < first_choice_y or mid_y > y_bottom:
                    continue
                owning = nearest_letter(mid_y)
                letter_rect = by_letter[owning][0]
                if r.x1 <= letter_rect.x1 + 1:
                    continue
                if r.x0 > col.x1:
                    continue
                b = bounds[owning]
                bounds[owning] = fitz.Rect(
                    min(b.x0, letter_rect.x1 + 1),
                    min(b.y0, r.y0 - 1),
                    max(b.x1, r.x1 + 3),
                    max(b.y1, r.y1 + 1),
                )

    for path in page.get_drawings():
        r = fitz.Rect(path.get("rect"))
        if r.height > 24 or r.width < 1.5 or r.width > 140:
            continue
        mid_y = (r.y0 + r.y1) / 2
        if mid_y < first_choice_y or mid_y > y_bottom:
            continue
        owning = nearest_letter(mid_y)
        letter_rect = by_letter[owning][0]
        if r.x0 < letter_rect.x1 or r.x0 > col.x1:
            continue
        b = bounds[owning]
        bounds[owning] = fitz.Rect(
            b.x0,
            min(b.y0, r.y0 - 1),
            max(b.x1, r.x1 + 2),
            max(b.y1, r.y1 + 1),
        )

    # Clamp so options don't invade neighbors by more than a tiny pad
    clips = {}
    for i, (L, letter_rect, _) in enumerate(ordered):
        b = bounds[L]
        if i > 0:
            prev_mid = letter_ys[ordered[i - 1][0]]
            cur_mid = letter_ys[L]
            split = (prev_mid + cur_mid) / 2
            if b.y0 < split:
                b.y0 = split
        if i + 1 < len(ordered):
            next_mid = letter_ys[ordered[i + 1][0]]
            cur_mid = letter_ys[L]
            split = (cur_mid + next_mid) / 2
            if b.y1 > split:
                b.y1 = split
        b.x0 = letter_rect.x1 + 1
        b.x1 = min(b.x1, col.x1 - 6)
        if b.height < 10:
            b.y1 = b.y0 + 12
        if b.width < 14:
            b.x1 = b.x0 + 14
        clips[L] = b & page.rect
    return clips


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
        # skip full-page decorative plates
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
        # Text/line tables: cluster short horizontal strokes
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
            # pad to include cell text around the grid
            union = fitz.Rect(union.x0 - 6, union.y0 - 8, union.x1 + 6, union.y1 + 8)
            candidates.append(union & col & page.rect)
    if not candidates:
        return None
    clip = max(candidates, key=lambda r: r.get_area())
    # Reject near-full-column captures
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
            # Prefer markers that have an image/figure below them
            for info in page.get_image_info():
                r = fitz.Rect(info["bbox"])
                if r.width > col.width * 1.05 or r.height < 50:
                    continue
                if (r & band).get_area() > 2000:
                    score += 40
                    break
            # Prefer earlier content pages over late false ticks
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
    if choices:
        return min(740, choices[-1][1].y1 + 36)
    return 740


def clean_stem_text(stem: str) -> str:
    stem = normalize_spaces(stem)
    stem = re.sub(
        r"^.*?(?=\b(?:The |What |Which |If |For |In |On |A |An |How |Given |Scott |Note:|P |N |C ))",
        "",
        stem,
    )
    # drop trailing module junk
    stem = re.sub(r"\s*\d+\s*Module\s*[12].*$", "", stem, flags=re.I)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem


def looks_like_bad_math_text(text: str) -> bool:
    if not text:
        return True
    if any(ch in text for ch in ("\uf8eb", "\uf8f6", "\uf8ec", "\uf8f7", "\uf8ed", "\uf8f8", "\ufffd")):
        return True
    if "Module" in text or "CONTINUE" in text:
        return True
    if re.search(r"\d,\s*-?\d+\s+\d+", text):
        return True
    if re.search(r"[A-Za-z]\s+[A-Za-z]\s+[A-Za-z]\s*=", text):
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
        # stem usually below the figure
        if fig.y1 + 4 < y1:
            y0 = max(y0, fig.y1 + 2)
        else:
            # figure mid-stem: crop above figure then skip (use figure alone)
            y1 = min(y1, fig.y0 - 2)
    if y1 - y0 < 18:
        return ""
    clip = fitz.Rect(col.x0, y0, col.x1, y1) & page.rect
    try:
        return f"<p>{img_tag(png_data_uri(page, clip, zoom=2.4), 'question')}</p>"
    except ValueError:
        return ""


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
    option_imgs: dict[str, str] | None = None
    fig: fitz.Rect | None = None
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
            clips = option_clips(page, marker, y_bottom)
            if clips and len(clips) == 4:
                option_imgs = {}
                for letter in "ABCD":
                    try:
                        option_imgs[letter] = img_tag(
                            png_data_uri(page, clips[letter], zoom=2.8),
                            f"option {letter}",
                        )
                    except ValueError:
                        option_imgs = None
                        break

        # If stem text is garbled math, crop the prose/equation band as an image
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

    # Always prefer PDF-cropped option images for math symbol fidelity (CKEditor-safe <img>)
    text_options = [normalize_spaces(o) for o in parsed[1]] if parsed else None
    if option_imgs:
        options = [option_imgs[L] for L in "ABCD"]
        correct = option_imgs[ans]
    elif text_options and len(text_options) == 4 and len(set(text_options)) == 4 and not any(
        looks_like_bad_math_text(o) for o in text_options
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
    # stats
    with_fig = sum(1 for q in data["questions"] if "<img alt=\"figure\"" in q["question"])
    with_opt_img = sum(
        1
        for q in data["questions"]
        if q.get("options") and any(isinstance(o, str) and o.startswith("<img") for o in q["options"])
    )
    return f"OK PT{test_num} math -> {out.name} fig={with_fig} opt_img={with_opt_img}"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for n in sorted(KEYS):
        print(process(n), flush=True)


if __name__ == "__main__":
    main()
