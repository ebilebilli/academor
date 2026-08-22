"""Build SAT Practice Test #5 Reading & Writing JSON for Academor."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

import pymupdf as fitz

PDF = Path(r"C:\Users\user\Desktop\sat-practice-test-5-digital.pdf")
OUT_DIR = Path(__file__).resolve().parent
REPO = OUT_DIR.parent
JSON_OUT = REPO / "academor" / "portals" / "resources" / "sat_questions" / "sat_practice_test_5_verbal.json"

# Official College Board answer key (paper digital Practice Test #5)
MODULE1_KEYS = list("ABBDBDBCBBDADBCBABACADBDBBDDBDACD")
MODULE2_KEYS = list("CDAACCBAADADDDDBAABACBACCBCDDADDA")
assert len(MODULE1_KEYS) == 33 and len(MODULE2_KEYS) == 33
assert MODULE1_KEYS[22] == "B" and MODULE1_KEYS[20] == "A"  # Q23, Q21
assert MODULE2_KEYS[9] == "D" and MODULE2_KEYS[10] == "A"  # Q10, Q11

# Underlined spans that text extraction loses (from College Board explanations / item stems)
UNDERLINES: dict[int, str] = {
    8: (
        "Mary Beth Wilhelm and other astrobiologists search for life, or its remains, "
        "in this harsh place because the desert closely mirrors the extreme environment on Mars."
    ),
    9: "there is an irreducibly contextual dimension of transportation mode choice.",
}

TABLE_HTML_Q14 = """
<table border="1" cellpadding="6" cellspacing="0" style="border-collapse:collapse;margin:12px 0;font-size:0.95em;">
  <caption style="text-align:left;font-weight:600;margin-bottom:6px;">Partial List of Candidate Species for De-extinction</caption>
  <thead><tr><th>Common name</th><th>Scientific name</th><th>Became extinct</th></tr></thead>
  <tbody>
    <tr><td>Huia</td><td><em>Heteralocha acutirostris</em></td><td>1907</td></tr>
    <tr><td>Caribbean monk seal</td><td><em>Monachus tropicalis</em></td><td>1952</td></tr>
    <tr><td>Passenger pigeon</td><td><em>Ectopistes migratorius</em></td><td>1914</td></tr>
    <tr><td>Saber-toothed cat</td><td><em>Smilodon</em></td><td>11,000 years before present</td></tr>
    <tr><td>Woolly mammoth</td><td><em>Mammuthus primigenius</em></td><td>6,400 years before present</td></tr>
  </tbody>
</table>
""".strip()


def clean_page_text(text: str) -> str:
    text = text.replace("\u00ad", "")  # soft hyphen
    # Accessibility tags around underlined phrases
    text = re.sub(
        r"Start referenced Content:\s*(.*?)\s*End referenced Content\.?",
        r"<u>\1</u>",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(r"[ \t]+\n", "\n", text)
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            lines.append("")
            continue
        if s.startswith("====="):
            continue
        if re.fullmatch(r"Module\s*[12]", s, re.I):
            continue
        if re.match(r"^\d+\s+QUESTIONS$", s, re.I):
            continue
        if s.upper().startswith("DIRECTIONS"):
            continue
        if "Unauthorized copying" in s or s.startswith("CONTINUE"):
            continue
        if re.fullmatch(r"[.\-~—–_\s]+", s):
            continue
        if re.fullmatch(r"N\s*U\s*E\d*", s, re.I):
            continue
        if re.fullmatch(r"E\d+", s):
            continue
        if re.search(r"CO\s*N\s*T|N\s*U\s*E", s) and len(s) < 24:
            continue
        # Module 2 Q1 is emitted as "- 1"
        if re.fullmatch(r"-\s*1", s):
            lines.append("1")
            continue
        # lone page numbers in footers (often 2 digits after CONTINUE)
        if re.fullmatch(r"\d{1,2}", s) and int(s) > 33:
            continue
        lines.append(s)
    return "\n".join(lines)


def normalize_spaces(s: str) -> str:
    s = s.replace("\n", " ")
    # PDF often renders blank as the word "blank"
    s = re.sub(r"\bblank\b", "_______", s)
    s = re.sub(r"\s+", " ", s)
    s = fix_broken_words(s)
    trans = str.maketrans({
        "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
        "\u2013": "-", "\u2014": "-", "\ufb01": "fi", "\ufb02": "fl",
        "\ufffd": "",
    })
    s = s.translate(trans)
    s = re.sub(r"\s*</u>\s*", "</u> ", s)
    s = re.sub(r"\s*<u>\s*", " <u>", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"<u>\s+", "<u>", s)
    s = re.sub(r"\s+</u>", "</u>", s)
    s = re.sub(r"<u><u>(.*?)</u></u>", r"<u>\1</u>", s)
    s = re.sub(r"(<u>.*?</u>)\s*\1", r"\1", s)
    return s.strip()


def split_questions(module_text: str) -> dict[int, str]:
    # Match question starts: line beginning with number 1-33
    pattern = re.compile(r"(?m)^(?P<num>[1-9]|[12]\d|3[0-3])\s*\n")
    matches = list(pattern.finditer(module_text))
    questions: dict[int, str] = {}
    for idx, m in enumerate(matches):
        num = int(m.group("num"))
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(module_text)
        body = module_text[start:end].strip()
        if len(body) < 40:
            continue
        if "A)" not in body and not re.search(r"(?m)^A\)", body):
            if "Which choice" not in body and "According to" not in body:
                continue
        questions[num] = body
    return questions


OPTION_RE = re.compile(
    r"(?ms)^\s*(?P<letter>[A-D])\)\s*(?P<text>.*?)(?=^\s*[A-D]\)\s*|\Z)"
)


def format_notes_stem(stem: str) -> str:
    """Turn 'student has taken notes' items into an HTML list when present."""
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
    # If bullets failed, keep sentences ending with period as notes
    if len(parts) <= 1 and after.strip():
        parts = [p.strip() for p in re.split(r"(?<=\.)\s+(?=[A-Z\"])", after.strip()) if p.strip()]
    if not parts:
        return f"{before}{marker}{question_tail}"
    items = "".join(f"<li>{p.rstrip('.')}</li>" for p in parts)
    return f"{before}{marker}<ul>{items}</ul>{question_tail}"


def scrub_option(text: str) -> str:
    text = re.sub(
        r"\s*STOP\b.*$",
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(
        r"\s*If you finish before time is called.*$",
        "",
        text,
        flags=re.I | re.S,
    )
    return text.strip()


def apply_underline(qid: int, stem: str) -> str:
    target = UNDERLINES.get(qid)
    if not target:
        return stem
    plain = stem.replace("<u>", "").replace("</u>", "")
    tgt = re.sub(r"\s+", " ", target)
    if tgt.rstrip(".")[:50] in plain and "<u>" in stem:
        return stem
    if tgt in stem:
        return stem.replace(tgt, f"<u>{tgt}</u>", 1)
    tgt2 = tgt.rstrip(".")
    if tgt2 in stem:
        return stem.replace(tgt2, f"<u>{tgt2}</u>", 1)
    return stem


def parse_options(body: str) -> tuple[str, list[str]]:
    first = re.search(r"(?m)^\s*A\)\s*", body)
    if not first:
        raise ValueError("No A) option found")
    stem = body[: first.start()].strip()
    opt_block = body[first.start() :]
    options = []
    for m in OPTION_RE.finditer(opt_block):
        text = scrub_option(normalize_spaces(m.group("text")))
        text = re.sub(r"\s*Unauthorized copying.*$", "", text)
        options.append(text)
    if len(options) != 4:
        raise ValueError(f"Expected 4 options, got {len(options)}: {options!r}")
    return stem, options


def stem_to_html(qid: int, stem: str, *, graph_data_uri: str | None = None) -> str:
    stem = apply_underline(qid, normalize_spaces(stem))
    stem = stem.replace("H eteralocha", "Heteralocha")
    stem = stem.replace("M ammuthus", "Mammuthus")
    stem = stem.replace("L . pertusa", "L. pertusa")

    parts = []
    if qid == 14:
        prose_match = re.search(
            r"(The passage of time is among the many obstacles.*)$",
            stem,
            flags=re.I,
        )
        if prose_match:
            stem = prose_match.group(1)
        parts.append(TABLE_HTML_Q14)

    if qid == 16 and graph_data_uri:
        stem = re.sub(
            r"^.*?Ratio of Manganese to Calcium.*?(?=The population of the coral)",
            "",
            stem,
            flags=re.I | re.S,
        )
        if "The population of the coral" in stem:
            stem = stem[stem.index("The population of the coral") :]
        parts.append(
            f'<p><img alt="Ratio of Manganese to Calcium in Samples from Alboran Sea '
            f'and Mauritanian Coast" src="{graph_data_uri}" '
            f'style="max-width:100%;height:auto;"/></p>'
        )

    stem = stem.replace("_______", "<strong>_______</strong>")
    stem = format_notes_stem(stem)
    parts.append(f"<p>{stem}</p>")
    return "".join(parts)


def crop_graph_png(doc: fitz.Document) -> str:
    """Render only the manganese/calcium graph (left column of module 1 page 10)."""
    page = doc[9]
    mat = fitz.Matrix(3, 3)
    clip = fitz.Rect(70, 125, 285, 375)
    pix = page.get_pixmap(matrix=mat, alpha=False, clip=clip)
    path = OUT_DIR / "graph_q16.png"
    pix.save(path)
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{b64}"


def fix_broken_words(s: str) -> str:
    """Repair mid-word spaces introduced by PDF text extraction."""
    fixes = [
        (r"\brem ains\b", "remains"),
        (r"\bcl osely\b", "closely"),
        (r"\benvir onment\b", "environment"),
        (r"\bastrobiolo gists\b", "astrobiologists"),
        (r"\bmicroor ganisms\b", "microorganisms"),
        (r"\bunrepre sentative\b", "unrepresentative"),
        (r"\btelecommunica tions\b", "telecommunications"),
        (r"\bH eteralocha\b", "Heteralocha"),
        (r"\bM ammuthus\b", "Mammuthus"),
        (r"\bL \. pertusa\b", "L. pertusa"),
        (r"\bL\.pertusa\b", "L. pertusa"),
    ]
    for pat, repl in fixes:
        s = re.sub(pat, repl, s, flags=re.I)
    s = re.sub(r"\b([a-z]{2,}) ([a-z]{2,})\b", lambda m: _maybe_join(m.group(1), m.group(2)), s)
    return s


def _maybe_join(a: str, b: str) -> str:
    joined = a + b
    known = {
        "remains", "closely", "environment", "astrobiologists", "microorganisms",
        "unrepresentative", "telecommunications", "photosphere", "electromagnetic",
        "population", "characteristics", "information", "significant", "especially",
        "scientists", "civilization", "mathematicians", "oxygenation", "declined",
    }
    if joined.lower() in known:
        return joined
    return f"{a} {b}"


def extract_module_text(doc: fitz.Document, start: int, end: int) -> str:
    parts = []
    for i in range(start, end):
        parts.append(doc[i].get_text("text", flags=fitz.TEXT_INHIBIT_SPACES))
    return clean_page_text("\n".join(parts))


def main():
    doc = fitz.open(PDF)
    graph_uri = crop_graph_png(doc)

    m1_text = extract_module_text(doc, 3, 17)
    m2_text = extract_module_text(doc, 17, 31)
    (OUT_DIR / "rw_m1_clean.txt").write_text(m1_text, encoding="utf-8")
    (OUT_DIR / "rw_m2_clean.txt").write_text(m2_text, encoding="utf-8")

    m1_q = split_questions(m1_text)
    m2_q = split_questions(m2_text)
    print("M1 found:", sorted(m1_q.keys()), "count", len(m1_q))
    print("M2 found:", sorted(m2_q.keys()), "count", len(m2_q))

    for label, qs in (("M1", m1_q), ("M2", m2_q)):
        missing = [i for i in range(1, 34) if i not in qs]
        if missing:
            print(label, "MISSING", missing)

    # Digital SAT RW = 27 + 27 = 54 (paper booklet has 33/module; keep first 27 each)
    per_module = 27
    items = []
    for local_num in range(1, per_module + 1):
        body = m1_q[local_num]
        try:
            stem, options = parse_options(body)
        except Exception as exc:
            print(f"M1 Q{local_num} parse fail: {exc}")
            print(body[:400])
            raise
        key = MODULE1_KEYS[local_num - 1]
        correct = options[ord(key) - ord("A")]
        html = stem_to_html(local_num, stem, graph_data_uri=graph_uri if local_num == 16 else None)
        items.append(
            {
                "id": local_num,
                "question": html,
                "options": options,
                "correct": correct,
                "answer_key": f"<p><strong>Correct Answer: {key}</strong></p>",
            }
        )

    for local_num in range(1, per_module + 1):
        body = m2_q[local_num]
        try:
            stem, options = parse_options(body)
        except Exception as exc:
            print(f"M2 Q{local_num} parse fail: {exc}")
            print(body[:500])
            raise
        key = MODULE2_KEYS[local_num - 1]
        correct = options[ord(key) - ord("A")]
        html = stem_to_html(local_num + 100, stem)  # +100 avoids module1 special cases
        items.append(
            {
                "id": per_module + local_num,
                "question": html,
                "options": options,
                "correct": correct,
                "answer_key": f"<p><strong>Correct Answer: {key}</strong></p>",
            }
        )
    assert len(items) == 54, len(items)

    payload = {
        "title": "SAT Practice Test 5 Reading and Writing",
        "category_name": "SAT Reading and Writing",
        "service": "sat",
        "is_sat": True,
        "sat_section": "reading",
        "time_limit_minutes": 64,
        "questions": items,
    }

    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Wrote", JSON_OUT, "questions", len(items))
    for q in items:
        assert q["correct"] in q["options"], q["id"]


if __name__ == "__main__":
    main()
