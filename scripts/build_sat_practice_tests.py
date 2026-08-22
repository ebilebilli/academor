"""Build Academor SAT Verbal (54/64) + Math (44/70) JSONs from College Board digital practice PDFs."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

import pymupdf as fitz

DESKTOP = Path(r"C:\Users\user\Desktop")
REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"
WORK = REPO / "_sat_pt5_work"

# Official answer keys (paper digital practice tests). RW = 33-letter strings.
# Math = 27 entries (A-D or SPR answer strings with ; alternatives).
KEYS: dict[int, dict] = {
    5: {
        "rw_m1": "ABBDBDBCBBDADBCBABACADBDBBDDBDACD",
        "rw_m2": "CDAACCBAADADDDDBAABACBACCBCDDADDA",
        "math_m1": [
            "C", "B", "D", "B", "B", "4", "29", "C", "B", "B", "C", "D", "6",
            "4.51; 451/100", "C", "D", "B", "D", "A", ".3928; .3929; 11/28", "336",
            "B", "D", "D", "A", "A", "25",
        ],
        "math_m2": [
            "B", "B", "B", "B", "D", "6", "30; -30", "D", "B", "A", "C", "D",
            "14.66; 14.67; 44/3", "4205", "A", "A", "B", "B", "D", "20", "66",
            "D", "D", "D", "A", "C", "4176",
        ],
    },
    4: {
        "rw_m1": "BAACABDBBDCDABCAAAADDDBCBACDAADDC",
        "rw_m2": "DDBBBBACCAABDCCABDCABDDABBAACCAAB",
        "math_m1": [
            "B", "A", "B", "D", "A", "9", "10", "A", "B", "D", "A", "C",
            "1/5; .2", "80", "D", "B", "B", "A", "C", "100", "361/8; 45.12; 45.13",
            "B", "D", "C", "C", "D", "5",
        ],
        "math_m2": [
            "B", "B", "C", "A", "A", "15; -5", "50", "B", "D", "A", "A", "B",
            ".3; 3/10", "2", "A", "C", "B", "D", "A", "15/17; .8824; .8823", "51",
            "A", "C", "C", "D", "B", "600",
        ],
    },
    6: {
        "rw_m1": "DBBDDABBDDAAACBDDBACDDDCBDDCCBABC",
        "rw_m2": "CDCBBCDCCCCCCDDBADCAACBADBDABCDCB",
        "math_m1": [
            "A", "D", "D", "D", "A", "31", "11", "D", "B", "B", "A", "B",
            ".5; 1/2", "7.5; 15/2", "B", "C", "D", "D", "D", "189/5; 37.8", "-24",
            "D", "A", "C", "D", "A", "54",
        ],
        "math_m2": [
            "B", "A", "B", "A", "B", "6", "10", "B", "A", "A", "D", "C", "774", "5",
            "B", "A", "D", "B", "A", ".2916; .2917; 7/24", "1677", "B", "A", "D",
            "A", "A", "-28",
        ],
    },
    7: {
        "rw_m1": "ADBBAAACAADDABABCDADDCCADDADACBCD",
        "rw_m2": "CDCDBABBDBBDCCDDBBDDCCCABDBDADCAC",
        "math_m1": [
            "B", "D", "B", "A", "D", "9", "14; -5; -4", "A", "B", "D", "C", "D",
            "294", "3", "A", "C", "B", "B", "D", "5", "87", "B", "A", "B", "C", "A",
            "-13/2; -6.5",
        ],
        "math_m2": [
            "A", "B", "C", "A", "B", "2850", "11/4; 2.75", "C", "C", "D", "D", "D",
            "4.41; 441/100", "153", "C", "A", "A", "D", "B", "120", "1660", "B", "C",
            "B", "C", "B", "14",
        ],
    },
    8: {
        "rw_m1": "BDACCCDAADBCAADCADCBBADCCDABCACAD",
        "rw_m2": "BABDDACAADBCDBCACDABCACABAAACBDBD",
        "math_m1": [
            "C", "C", "D", "D", "A", "0.2; 1/5", "240", "A", "B", "B", "B", "D",
            "25", "6", "C", "D", "A", "D", "C", "7", "182", "D", "B", "C", "C", "B",
            "284/3; 94.66; 94.67",
        ],
        "math_m2": [
            "C", "C", "D", "C", "D", "9", "68", "B", "D", "D", "C", "B", "986", "24",
            "D", "D", "A", "B", "A", "46", "1.8; 9/5", "A", "B", "C", "B", "D", "168",
        ],
    },
    9: {
        "rw_m1": "ADCCBCAACADCDCADBAAABCCCABABDBBAC",
        "rw_m2": "BCBBCDDDAADADCCDBDCDCCBDCCCABCDCB",
        "math_m1": [
            "B", "C", "B", "A", "A", "9", "224", "A", "C", "B", "A", "B", "40", "14",
            "C", "D", "B", "D", "D", "52", "-3", "B", "D", "A", "D", "B", "1260",
        ],
        "math_m2": [
            "B", "B", "D", "B", "D", "70", "1", "D", "A", "D", "C", "D", "45", "2; -12",
            "B", "C", "B", "B", "C", "410", "-19", "D", "D", "A", "C", "D", "50",
        ],
    },
    10: {
        "rw_m1": "ABBACBDDCCCBAAAACDCBACCCCCABBBBCC",
        "rw_m2": "AADAADBBDDDABADAAADBDCADAABDADDAC",
        "math_m1": [
            "C", "A", "D", "A", "D", "77", "25", "C", "B", "B", "B", "B", "1", "76",
            "A", "D", "D", "A", "A", "35", "113", "A", "C", "C", "D", "A",
            "29/3; 9.666; 9.667",
        ],
        "math_m2": [
            "D", "A", "D", "D", "A", "79", "2", "D", "D", "B", "A", "C", "41", "11875",
            "B", "B", "B", "A", "C", "5", "0.25; 1/4", "D", "C", "C", "D", "B", "104",
        ],
    },
    11: {
        "rw_m1": "ACDDABBDDCBDADBADDDDABBADDDAACADB",
        "rw_m2": "CCCDBBBABCBDCBCCAABBBBBBABDBCBCAA",
        "math_m1": [
            "D", "A", "C", "A", "B", "75", "30", "A", "C", "C", "D", "B", "13", "15000",
            "A", "A", "C", "B", "D", "100", "29", "B", "B", "A", "C", "B", "3331",
        ],
        "math_m2": [
            "C", "B", "D", "D", "A", "8.6; 43/5", "3600", "A", "B", "D", "C", "A", "45",
            "13", "B", "C", "D", "B", "A", ".5061; .5062; 41/81", "1512/5; 302.4", "C",
            "A", "B", "B", "D", "157.8; 789/5",
        ],
    },
}

# Validate key lengths
for n, k in KEYS.items():
    assert len(k["rw_m1"]) == 33 and len(k["rw_m2"]) == 33, n
    assert len(k["math_m1"]) == 27 and len(k["math_m2"]) == 27, n


def find_pdf(test_num: int) -> Path | None:
    patterns = [
        f"sat-practice-test-{test_num}-digital.pdf",
        f"sat-practice-test-{test_num}-digital (1).pdf",
    ]
    for name in patterns:
        p = DESKTOP / name
        if p.is_file():
            return p
    return None


_QUESTIONS_RE = re.compile(r"\b\d{1,2}\s*\n?\s*QUESTIONS\b", re.I)
_MODULE_NUM_RE = re.compile(r"Module\s*\n?\s*([12])\b", re.I)


def _has_rw_header(head: str) -> bool:
    return "Reading and Writing" in head and "Module" in head and bool(_QUESTIONS_RE.search(head))


def _has_math_header(head: str) -> bool:
    return (
        "Reading and Writing" not in head
        and "Module" in head
        and bool(_QUESTIONS_RE.search(head))
        and bool(re.search(r"\bMath\b", head))
    )


def _assign_module_pages(candidate_pages: list[int], heads: list[str]) -> tuple[int | None, int | None]:
    """Assign candidate header pages to module 1 / module 2 slots, honoring an
    explicit module number in the header text when present, else falling back
    to document order."""
    p1 = p2 = None
    unnumbered: list[int] = []
    for p in candidate_pages:
        m = _MODULE_NUM_RE.search(heads[p])
        num = m.group(1) if m else None
        if num == "1" and p1 is None:
            p1 = p
        elif num == "2" and p2 is None:
            p2 = p
        elif num is None:
            unnumbered.append(p)
    for p in unnumbered:
        if p1 is None:
            p1 = p
        elif p2 is None and p != p1:
            p2 = p
    return p1, p2


def _find_q1_mcq_pages(doc: fitz.Document, limit: int) -> list[int]:
    """Fallback: find pages whose (cleaned) text starts a module at question 1
    followed by a full A)/B)/C) option set -- used when PDFs omit the
    "Reading and Writing ... Module ... QUESTIONS" banner text entirely."""
    candidates = []
    for i in range(0, limit):
        text = clean_page_text(doc[i].get_text("text", flags=fitz.TEXT_INHIBIT_SPACES))
        m = re.search(r"(?m)^1\s*\n", text)
        if not m:
            continue
        tail = text[m.end() : m.end() + 2000]
        if (
            re.search(r"(?m)^A\)\s*", tail)
            and re.search(r"(?m)^B\)\s*", tail)
            and re.search(r"(?m)^C\)\s*", tail)
        ):
            candidates.append(i)
    return candidates


def find_module_pages(doc: fitz.Document) -> dict:
    """Return start page indices (0-based) for RW/Math modules.

    Handles several PDF layout variants seen across digital SAT print-format
    practice tests:
    - Standard: "Module / <n> / Reading and Writing / NN QUESTIONS" (or Math)
      banner near the very top of the page.
    - Header pushed down the page by a leftover "Unauthorized copying..." /
      "CONTINUE" running-footer fragment before the real banner text.
    - RW module banners omitted entirely -- module starts are detected by
      Q1 immediately followed by a full A)/B)/C)/D) option set.
    """
    n = len(doc)
    heads = [doc[i].get_text()[:2500] for i in range(n)]

    math_pages = [i for i in range(n) if _has_math_header(heads[i])]
    rw_pages = [i for i in range(n) if _has_rw_header(heads[i])]

    math1, math2 = _assign_module_pages(math_pages, heads)
    rw1, rw2 = _assign_module_pages(rw_pages, heads)

    if rw1 is None or rw2 is None:
        limit = math1 if math1 is not None else n
        fallback = _find_q1_mcq_pages(doc, limit)
        fallback = [p for p in fallback if p not in (rw1, rw2)]
        if rw1 is None and fallback:
            rw1 = fallback.pop(0)
        if rw2 is None:
            fallback = [p for p in fallback if rw1 is None or p > rw1]
            if fallback:
                rw2 = fallback[0]

    found = {"rw1": rw1, "rw2": rw2, "math1": math1, "math2": math2}
    found["rw1_end"] = rw2 if rw2 is not None else (math1 if math1 is not None else n)
    found["rw2_end"] = math1 if math1 is not None else n
    found["math1_end"] = math2 if math2 is not None else n
    found["math2_end"] = n
    return found


# (anchor phrase that opens the question, the question number that should
# precede it) -- see clean_page_text for why this is needed.
_KNOWN_MISSING_NUMBER_ANCHORS: list[tuple[str, int]] = [
    ("As the fourteenth US librarian of Congress,", 23),  # PT7 RW module 2
]


def clean_page_text(text: str) -> str:
    text = text.replace("\u00ad", "")
    text = re.sub(
        r"Start referenced Content:\s*(.*?)\s*End referenced Content\.?",
        r"<u>\1</u>",
        text,
        flags=re.I | re.S,
    )
    # A handful of official PDFs drop a single question-number glyph from
    # the extractable text entirely (the number is only findable, mangled,
    # inside decorative page-footer dashes elsewhere on the page). Restore
    # the missing markers using each question's unique, stable opening
    # phrase as an anchor rather than relying on the corrupted footer digit.
    for anchor, missing_num in _KNOWN_MISSING_NUMBER_ANCHORS:
        text = re.sub(rf"(?m)^({re.escape(anchor)})", rf"{missing_num}\n\1", text, count=1)
    # Some PDFs render a question-number badge with stray decorative glyphs
    # glued onto it (e.g. a leading "." and trailing ","/"________" runs
    # picked up from the badge/divider artwork), such as ".1,\n" or
    # ".2, ________\n____,\n" instead of a clean "1\n"/"2\n". A legitimate
    # line of question text never starts with "." immediately followed by
    # digits, so this is safe to normalize back to a bare number marker.
    text = re.sub(
        r"(?m)^\.(?P<num>\d{1,2}),(?:[ \t]*_+)?[ \t]*\n(?:_+,[ \t]*\n)?",
        lambda m: f"{m.group('num')}\n",
        text,
    )
    # Some PDFs repeat a mini "Module N" banner at the top of every page of
    # a module (not just the module's first page), immediately preceded by
    # that page's footer page-number. The footer digit sits on its own line
    # right before "Module\nN\n" and, being a plausible 1-33 value, would
    # otherwise be mistaken by split_questions for a real question-number
    # marker. Strip the footer-number + repeated mini-banner as a unit --
    # but only when it's trailed by a blank line before the next real
    # content, which is what distinguishes this page-turn artifact (seen in
    # RW modules) from a math module's genuine "<real question number>\n
    # Module\nN\n<question body, no blank line>" page-break layout, where
    # the leading digit is a real marker that must NOT be discarded.
    text = re.sub(r"(?m)^\d{1,2}[ \t]*\nModule[ \t]*\n[12][ \t]*\n\n", "\n", text)
    # Strip the math NOTES / reference-formula-sheet / answer-bubbling
    # instructions block. It's boilerplate present once at the start of
    # every math module and is riddled with bare digit-only lines (fraction
    # numerators/denominators like the "2" in "1/2", triangle/circle
    # dimensions, etc.) that would otherwise be mistaken for question-number
    # markers by split_questions.
    text = re.sub(
        r"(?is)\bNOTES?\b.*?\byour circled answer\.\s*",
        "\n",
        text,
        count=1,
    )
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        if re.fullmatch(r"Module\s*[12]", s, re.I):
            continue
        if re.match(r"^\d+\s+QUESTIONS$", s, re.I):
            continue
        if s.upper().startswith("DIRECTIONS") or s in {"NOTES", "REFERENCE"}:
            continue
        if "Unauthorized copying" in s or s.startswith("CONTINUE"):
            continue
        if re.fullmatch(r"[.\-~—–_\s]+", s):
            continue
        if re.search(r"CO\s*N\s*T|N\s*U\s*E", s) and len(s) < 24:
            continue
        if re.fullmatch(r"-\s*1", s):
            # A lone leading "- 1" decorative dash artifact seen on some
            # PDFs' very first content line.
            lines.append("1")
            continue
        if re.fullmatch(r"-[-\s]*\d{1,2}[-\s]*", s) or re.fullmatch(r"-{2,}", s):
            # Decorative dash separators around page-footer numbers (e.g.
            # "- 23 - - - - -" / "-23----"). These are page/section
            # furniture, not question markers, so drop them entirely rather
            # than risk surfacing the enclosed digit as a false
            # question-number candidate.
            continue
        if re.fullmatch(r"\d{1,2}", s) and int(s) > 33:
            continue
        lines.append(s)
    return "\n".join(lines)


def _fix_scrambled_two_column_question(text: str) -> str:
    """PT9 RW Module 1's page 4 has a PDF content-stream ordering defect: in
    its two-column layout, question 2 (right column, top) got extracted out
    of order relative to question 3 (right column, below it) -- question 2's
    option list landed right after question 1's own options (before question
    3's marker) instead of after its own stem, and question 2's number
    marker got mangled into stray punctuation. Reassemble questions 2 and 3
    into normal numeric reading order using the surrounding wording as an
    anchor (safe no-op for every other PDF/page).
    """
    old = (
        "D)Discussed\n"
        "A)accidental\nB)confident\nC)expensive\nD)consistent\n"
        "3\nDue to their often strange images, highly\n"
        "experimental syntax, and opaque subject matter,\n"
        "many of John Ashbery\u2019s poems can be quite difficult\n"
        "to blankand thus are the object of heated debate\n"
        "among scholars.\n"
        "Which choice completes the text with the most\n"
        "logical and precise word or phrase?\n"
        "A)delegate\nB)compose\nC)interpret\nD)renounce\n"
        "2\n,\n2\n, ________\n____,\n"
        "One challenge of generating electricity from ocean\n"
        "waves is that wave power isn\u2019t blank\n"
        "it varies in\n"
        "unpredictable ways that pose technological and\n"
        "planning problems for electricity generation.\n"
        "Which choice completes the text with the most\n"
        "logical and precise word or phrase?\n"
        "\n4\n"
    )
    new = (
        "D)Discussed\n"
        "2\n"
        "One challenge of generating electricity from ocean\n"
        "waves is that wave power isn\u2019t blank\n"
        "it varies in\n"
        "unpredictable ways that pose technological and\n"
        "planning problems for electricity generation.\n"
        "Which choice completes the text with the most\n"
        "logical and precise word or phrase?\n"
        "A)accidental\nB)confident\nC)expensive\nD)consistent\n"
        "3\nDue to their often strange images, highly\n"
        "experimental syntax, and opaque subject matter,\n"
        "many of John Ashbery\u2019s poems can be quite difficult\n"
        "to blankand thus are the object of heated debate\n"
        "among scholars.\n"
        "Which choice completes the text with the most\n"
        "logical and precise word or phrase?\n"
        "A)delegate\nB)compose\nC)interpret\nD)renounce\n"
        "4\n"
    )
    return text.replace(old, new, 1)


def _fix_leading_stray_question_block(text: str) -> str:
    """PT9 RW Module 2's first page has the same content-stream ordering
    defect as _fix_scrambled_two_column_question, but for question 3 (right
    column, bottom): the entire question came out first in the text stream,
    ahead of the page header and questions 1-2. Move the self-contained
    block back to its correct numeric position, right after question 2 and
    before question 4 (safe no-op for every other PDF/page).
    """
    stray_block = (
        "3\nNigerian American author Teju Cole\u2019s blankhis\n"
        "two passions\u2014photography and the written\n"
        "word\u2014culminates in his 2017 book, Blind Spot,\n"
        "which evocatively combines his original photographs\n"
        "from his travels with his poetic prose.\n"
        "Which choice completes the text with the most\n"
        "logical and precise word or phrase?\n"
        "A)indifference to\nB)enthusiasm for\nC)concern about\nD)surprise at\n"
    )
    if not text.startswith(stray_block):
        return text
    rest = text[len(stray_block):]
    return rest.replace("\n4\n", "\n" + stray_block + "4\n", 1)


def extract_pages(doc, start: int, end: int) -> str:
    parts = []
    for i in range(start, end):
        parts.append(doc[i].get_text("text", flags=fitz.TEXT_INHIBIT_SPACES))
    text = clean_page_text("\n".join(parts))
    text = _fix_scrambled_two_column_question(text)
    return _fix_leading_stray_question_block(text)


def split_questions(module_text: str, max_n: int = 33, require_mcq: bool = False) -> dict[int, str]:
    """Split a module's cleaned text into {question_number: body_text}.

    When require_mcq is True, a candidate numbered line is only accepted as a
    real question start if its body contains a genuine "A)" option marker
    before the next candidate -- this rejects false matches such as graph
    axis-tick numbers (8, 10, 12, ...) that have no options following them.
    """
    pattern = re.compile(rf"(?m)^(?P<num>[1-9]|[12]\d|3[0-3])\s*\n")
    matches = list(pattern.finditer(module_text))

    def is_valid_body(body: str) -> bool:
        if len(body) < 20:
            return False
        if require_mcq:
            has_lettered_options = bool(re.search(r"(?m)^\s*A\)\s*", body))
            has_bullet_options = len(re.findall(r"(?m)^\s*\u2022\s*\S", body)) >= 4
            if not (has_lettered_options or has_bullet_options):
                return False
        return True

    def choose(same_num: list[re.Match], boundary_pos: int) -> re.Match | None:
        # Several raw candidates can share the same number: a running
        # "Module / N" header digit (or a page-footer number) before/after
        # the real question marker, plus the real marker itself. Prefer the
        # LATEST candidate whose body (up to the boundary) is still a valid
        # question -- this skips leading header artifacts (whose body would
        # be the directions/notes text, invalid) while also skipping
        # trailing footer-number artifacts (whose body up to the boundary
        # would be too short/empty, also invalid).
        for cand in reversed(same_num):
            if is_valid_body(module_text[cand.end() : boundary_pos].strip()):
                return cand
        return None

    # Walk matches in document order tracking the expected next question
    # number. Any candidate that is neither the current expected number nor
    # the next one is treated as embedded table/graph data (e.g. axis ticks
    # or a data-row value like "7") and ignored rather than used as a
    # boundary.
    expected = 1
    same_num: list[re.Match] = []
    accepted: list[tuple[int, re.Match]] = []
    for m in matches:
        num = int(m.group("num"))
        if num > max_n:
            continue
        allowed_next = (expected + 1, expected + 2) if require_mcq else (expected + 1,)
        if num == expected:
            same_num.append(m)
        elif num in allowed_next and same_num:
            # Only treat this as "advancing past `expected`" once we've
            # actually seen at least one real candidate for it -- otherwise
            # a stray number from boilerplate/figures that happens to equal
            # expected+1 would prematurely skip the real question. And only
            # actually advance if one of the `expected` candidates produces a
            # valid body; if not (e.g. we're still inside a run of graph
            # axis-tick numbers), keep waiting rather than committing to a
            # bogus/empty body and losing the real question.
            # Allowing a jump of two (not just one) tolerates the rare PDF
            # where a single question's printed number glyph is lost by text
            # extraction entirely -- that question ends up simply missing
            # from the result instead of corrupting everything after it.
            chosen = choose(same_num, m.start())
            if chosen is not None:
                accepted.append((expected, chosen))
                expected = num
                same_num = [m]
    if same_num:
        chosen = choose(same_num, len(module_text))
        if chosen is not None:
            accepted.append((expected, chosen))

    questions: dict[int, str] = {}
    for idx, (num, m) in enumerate(accepted):
        start = m.end()
        end = accepted[idx + 1][1].start() if idx + 1 < len(accepted) else len(module_text)
        body = module_text[start:end].strip()
        if not is_valid_body(body):
            continue
        questions[num] = body
    return questions


def normalize_spaces(s: str) -> str:
    s = s.replace("\n", " ")
    s = re.sub(r"\bblank\b", "_______", s)
    s = re.sub(r"\s+", " ", s)
    trans = str.maketrans({
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\u2212": "-", "\ufb01": "fi", "\ufb02": "fl",
        "\ufffd": "",
    })
    s = s.translate(trans)
    # Some of these PDFs map a literal '$'/'%'/'-' glyph to a spelled-out
    # accessibility label instead of the symbol itself (e.g. "dollar sign
    # 25" for "$25", "20 percent sign" for "20%", "negative 6" for "-6").
    # Collapse those back to the real symbol so the text reads naturally.
    s = re.sub(r"dollar sign\s*", "$", s, flags=re.I)
    s = re.sub(r"\s*percent sign", "%", s, flags=re.I)
    s = re.sub(r"\bnegative\s+(?=\d)", "-", s, flags=re.I)
    s = re.sub(r"\s*</u>\s*", "</u> ", s)
    s = re.sub(r"\s*<u>\s*", " <u>", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"<u><u>(.*?)</u></u>", r"<u>\1</u>", s)
    return s.strip()


OPTION_RE = re.compile(
    r"(?ms)^\s*(?P<letter>[A-D])\)\s*(?P<text>.*?)(?=^\s*[A-D]\)\s*|\Z)"
)


def scrub_option(text: str) -> str:
    text = re.sub(r"\s*STOP\b.*$", "", text, flags=re.I | re.S)
    text = re.sub(r"\s*If you finish before time is called.*$", "", text, flags=re.I | re.S)
    text = re.sub(r"\s*Unauthorized copying.*$", "", text, flags=re.I | re.S)
    return text.strip()


BULLET_OPTION_RE = re.compile(r"(?m)^[ \t]*\u2022[ \t]*(?P<text>\S.*)$")


def parse_mcq(body: str) -> tuple[str, list[str]] | None:
    first = re.search(r"(?m)^\s*A\)\s*", body)
    if first:
        stem = body[: first.start()].strip()
        options = []
        for m in OPTION_RE.finditer(body[first.start() :]):
            options.append(scrub_option(normalize_spaces(m.group("text"))))
        if len(options) != 4:
            return None
        return stem, options

    # Some PDFs render the four answer choices as plain bullets with no
    # "A)"-"D)" letter markers at all.
    bullets = list(BULLET_OPTION_RE.finditer(body))
    if len(bullets) == 4:
        stem = body[: bullets[0].start()].strip()
        options = [scrub_option(normalize_spaces(m.group("text"))) for m in bullets]
        return stem, options
    return None


def format_notes_stem(stem: str) -> str:
    marker = "While researching a topic, a student has taken the following notes:"
    if marker not in stem:
        return stem
    before, after = stem.split(marker, 1)
    q_match = re.search(r"\s*(The student wants\b.*)$", after)
    question_tail = ""
    if q_match:
        question_tail = " " + q_match.group(1).strip()
        after = after[: q_match.start()]
    parts = re.split(r"(?:^|\s)[•·▪◦\uFFFD]\s*", after.strip())
    parts = [p.strip(" ;") for p in parts if p and p.strip(" ;")]
    if len(parts) <= 1 and after.strip():
        parts = [p.strip() for p in re.split(r"(?<=\.)\s+(?=[A-Z\"])", after.strip()) if p.strip()]
    if not parts:
        return f"{before}{marker}{question_tail}"
    items = "".join(f"<li>{p.rstrip('.')}</li>" for p in parts)
    return f"{before}{marker}<ul>{items}</ul>{question_tail}"


def spr_answers(raw: str) -> list[str]:
    parts = [p.strip() for p in raw.split(";") if p.strip()]
    return parts or [raw.strip()]


def render_page_clip(doc, page_index: int, clip: fitz.Rect | None = None) -> str:
    page = doc[page_index]
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat, alpha=False, clip=clip)
    b64 = base64.b64encode(pix.tobytes("png")).decode("ascii")
    return f"data:image/png;base64,{b64}"


def find_question_page(doc, start: int, end: int, qnum: int) -> int | None:
    """Best-effort: page whose text contains a lone question number near start of a block."""
    pat = re.compile(rf"(?m)^{qnum}\s*$")
    for i in range(start, end):
        t = doc[i].get_text("text")
        if pat.search(clean_page_text(t)):
            return i
    return None


def build_verbal(doc, pages, keys, test_num: int) -> dict:
    m1 = split_questions(extract_pages(doc, pages["rw1"], pages["rw1_end"]), require_mcq=True)
    m2 = split_questions(extract_pages(doc, pages["rw2"], pages["rw2_end"]), require_mcq=True)
    items = []
    for local in range(1, 28):
        if local not in m1:
            raise KeyError(f"PT{test_num} RW M1 missing Q{local}")
        parsed = parse_mcq(m1[local])
        if not parsed:
            raise ValueError(f"PT{test_num} RW M1 Q{local} MCQ parse failed")
        stem, options = parsed
        letter = keys["rw_m1"][local - 1]
        correct = options[ord(letter) - ord("A")]
        html = f"<p>{format_notes_stem(normalize_spaces(stem).replace('_______', '<strong>_______</strong>'))}</p>"
        items.append({
            "id": local,
            "question": html,
            "options": options,
            "correct": correct,
            "answer_key": f"<p><strong>Correct Answer: {letter}</strong></p>",
        })
    for local in range(1, 28):
        if local not in m2:
            raise KeyError(f"PT{test_num} RW M2 missing Q{local}")
        parsed = parse_mcq(m2[local])
        if not parsed:
            raise ValueError(f"PT{test_num} RW M2 Q{local} MCQ parse failed")
        stem, options = parsed
        letter = keys["rw_m2"][local - 1]
        correct = options[ord(letter) - ord("A")]
        html = f"<p>{format_notes_stem(normalize_spaces(stem).replace('_______', '<strong>_______</strong>'))}</p>"
        items.append({
            "id": 27 + local,
            "question": html,
            "options": options,
            "correct": correct,
            "answer_key": f"<p><strong>Correct Answer: {letter}</strong></p>",
        })
    assert len(items) == 54
    return {
        "title": f"SAT Practice Test {test_num} Reading and Writing",
        "category_name": "SAT Reading and Writing",
        "service": "sat",
        "is_sat": True,
        "sat_section": "reading",
        "time_limit_minutes": 64,
        "questions": items,
    }


def needs_figure(stem: str) -> bool:
    s = stem.lower()
    return any(w in s for w in ("graph", "figure", "table", "shown", "diagram", "scatterplot"))


def build_math(doc, pages, keys, test_num: int) -> dict:
    """Build math quiz with cropped figures and math option images (CKEditor <img>)."""
    import importlib.util

    crop_path = Path(__file__).with_name("rebuild_sat_math.py")
    spec = importlib.util.spec_from_file_location("rebuild_sat_math", crop_path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.build_math(doc, pages, keys, test_num)


def process_test(test_num: int) -> list[str]:
    pdf = find_pdf(test_num)
    if not pdf:
        return [f"SKIP PT{test_num}: PDF not found"]
    if test_num not in KEYS:
        return [f"SKIP PT{test_num}: no answer keys"]
    doc = fitz.open(pdf)
    pages = find_module_pages(doc)
    msgs = [f"PT{test_num} pages={pages}"]
    for need in ("rw1", "rw2", "math1", "math2"):
        if pages.get(need) is None:
            msgs.append(f"FAIL PT{test_num}: missing {need}")
            return msgs
    keys = KEYS[test_num]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        verbal = build_verbal(doc, pages, keys, test_num)
        vpath = OUT_DIR / f"sat_practice_test_{test_num}_verbal.json"
        vpath.write_text(json.dumps(verbal, ensure_ascii=False, indent=2), encoding="utf-8")
        msgs.append(f"OK verbal {vpath.name} n={len(verbal['questions'])}")
    except Exception as exc:
        msgs.append(f"FAIL verbal PT{test_num}: {exc}")
    try:
        math = build_math(doc, pages, keys, test_num)
        mpath = OUT_DIR / f"sat_practice_test_{test_num}_math.json"
        mpath.write_text(json.dumps(math, ensure_ascii=False, indent=2), encoding="utf-8")
        msgs.append(f"OK math {mpath.name} n={len(math['questions'])}")
    except Exception as exc:
        msgs.append(f"FAIL math PT{test_num}: {exc}")
    return msgs


def main():
    # Also keep existing PT5 verbal if rebuild fails mid-way — process all known
    all_msgs = []
    for n in sorted(KEYS):
        print(f"=== Practice Test {n} ===")
        for line in process_test(n):
            print(line)
            all_msgs.append(line)
    (WORK / "build_all_report.txt").write_text("\n".join(all_msgs), encoding="utf-8")


if __name__ == "__main__":
    main()
