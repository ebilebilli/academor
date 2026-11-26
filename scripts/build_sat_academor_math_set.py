"""Build the original Academor SAT Math practice tests 2–10 (44 questions each).

Same blueprint as practice test 1 (scripts/build_sat_academor_math.py):
  * 2 modules x 22 questions, 35 minutes each (70 minutes in total)
  * per module: 8 Algebra, 8 Advanced Math, 3 Problem-Solving and Data Analysis,
    3 Geometry and Trigonometry; questions get harder through a module, and module 2 is
    harder than module 1
  * student-produced response (SPR) items at positions 6, 7, 13, 14, 20 and 21 of each module
  * in each module the 16 multiple-choice answers are spread 4 A / 4 B / 4 C / 4 D, and numeric
    choices are listed in increasing order, as on the real test

Questions come from the templates in sat_math_templates.py. Each template computes its own answer
(so every key is correct by construction) and builds its wrong choices from typical mistakes. A
fixed seed per test makes the files reproducible.

Output: academor/portals/resources/sat_questions/academor_sat_math_test_{2..10}.json
Load:   python academor/manage.py load_sat_quiz_resources --file academor_sat_math_test_N.json

Requires matplotlib (not a runtime dependency of the site):
    uv run --with matplotlib python scripts/build_sat_academor_math_set.py
"""

from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from sat_math_core import (
    ADV, ALG, GEO, LETTERS, PSDA, numeric_options, spr_answers, text_options,
)
from sat_math_templates import TEMPLATES

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"
SPR_POSITIONS = {6, 7, 13, 14, 20, 21}
DOMAIN_COUNTS = {ALG: 8, ADV: 8, PSDA: 3, GEO: 3}
TESTS = range(2, 11)
SEEN: set[str] = set()  # question HTML already used in an earlier module / test


def level_for(module: int, position: int) -> int:
    if module == 1:
        return 1 if position <= 7 else 2 if position <= 15 else 3
    return 2 if position <= 6 else 3


def domain_order(rng: random.Random) -> list[str]:
    """A shuffled domain sequence; the four domains are spread through the module."""
    while True:
        seq = [d for d, k in DOMAIN_COUNTS.items() for _ in range(k)]
        rng.shuffle(seq)
        thirds = [seq[:7], seq[7:15], seq[15:]]
        # every third of the module should contain Algebra and Advanced Math
        if all(ALG in t and ADV in t for t in thirds):
            return seq


def choose_template(rng, domain, level, mode, used_in_test, usage):
    pool = [t for t in TEMPLATES if t["domain"] == domain and mode in t["modes"] and t["name"] not in used_in_test]
    if not pool:
        # every suitable template is already in this test: reuse one with new numbers
        pool = [t for t in TEMPLATES if t["domain"] == domain and mode in t["modes"]]
    assert pool, (domain, level, mode)
    best = min(abs(t["level"] - level) for t in pool)
    near = [t for t in pool if abs(t["level"] - level) == best]
    least = min(usage[t["name"]] for t in near)
    choices = [t for t in near if usage[t["name"]] == least]
    return choices[rng.randrange(len(choices))]


def make_spec(rng, template, mode):
    for _ in range(40):
        try:
            spec = template["fn"](rng)
        except (AssertionError, ZeroDivisionError, ValueError):
            continue
        if spec["html"] in SEEN:
            continue
        if mode == "spr":
            if spec["kind"] == "num" and spec["spr_ok"]:
                value = spec["spr_value"] if spec["spr_value"] is not None else spec["correct"]
                answers = spr_answers(value)
                if answers and all(len(a) <= 6 for a in answers):
                    return {**spec, "kind": "spr", "answers": answers}
            continue
        if spec["kind"] == "num" and not any(numeric_options(spec, t) for t in range(4)):
            continue
        return spec
    raise RuntimeError(f"template {template['name']} could not produce a usable {mode} item")


def assign_letters(rng, specs):
    """Place the correct answer so each letter is used 4 times in the module's 16 MC items."""
    quota = {L: 4 for L in LETTERS}
    mc = [i for i, s in enumerate(specs) if s["kind"] in ("num", "text")]
    feasible = {}
    for i in mc:
        if specs[i]["kind"] == "num":
            feasible[i] = [t for t in range(4) if numeric_options(specs[i], t)]
        else:
            feasible[i] = [0, 1, 2, 3]
    # prefer placements that use the template's error-based distractors over filler values
    for slack in (0, 1, 3):
        allowed = {}
        for i in mc:
            fill = specs[i].get("_fill") or {}
            if specs[i]["kind"] == "num" and fill:
                best = min(fill[t] for t in feasible[i])
                allowed[i] = [t for t in feasible[i] if fill[t] <= best + slack]
            else:
                allowed[i] = feasible[i]
        q = dict(quota)
        placed = {}
        for i in sorted(mc, key=lambda j: (len(allowed[j]), rng.random())):
            opts = [t for t in allowed[i] if q[LETTERS[t]] > 0]
            if not opts:
                placed = None
                break
            top = max(q[LETTERS[t]] for t in opts)
            best_t = [t for t in opts if q[LETTERS[t]] == top]
            t = best_t[rng.randrange(len(best_t))]
            placed[i] = t
            q[LETTERS[t]] -= 1
        if placed is not None:
            return placed
    return None


def build_module(rng, module: int, usage: Counter, used_in_test: set):
    for _attempt in range(60):
        order = domain_order(rng)
        specs, names = [], []
        local_used = set(used_in_test)
        for pos, domain in enumerate(order, start=1):
            mode = "spr" if pos in SPR_POSITIONS else "mc"
            while True:
                template = choose_template(rng, domain, level_for(module, pos), mode, local_used, usage)
                try:
                    spec = make_spec(rng, template, mode)
                except RuntimeError:
                    local_used.add(template["name"])  # this template has run out of new variants here
                    continue
                break
            specs.append(spec)
            names.append(template["name"])
            local_used.add(template["name"])
        placed = assign_letters(rng, specs)
        if placed is None:
            continue
        rows = []
        for i, spec in enumerate(specs):
            if spec["kind"] == "spr":
                rows.append({**spec, "letter": None})
                continue
            t = placed[i]
            if spec["kind"] == "num":
                options = numeric_options(spec, t)
                correct_text = spec["fmt"](spec["correct"])
            else:
                spec = {**spec, "distractors": rng.sample(spec["distractors"], 3)}
                options = text_options(spec, t)
                correct_text = spec["correct"]
            assert options[t] == correct_text and len(set(options)) == 4, (names[i], options)
            rows.append({**spec, "options": options, "correct_text": correct_text, "letter": LETTERS[t]})
        for name in names:
            usage[name] += 1
        SEEN.update(r["html"] for r in rows)
        used_in_test.update(names)
        return rows
    raise RuntimeError(f"could not balance module {module}")


def to_json_row(number, module, row):
    out = {"id": number, "module": module, "domain": row["domain"], "skill": row["skill"], "question": row["html"]}
    if row["kind"] == "spr":
        out.update({
            "question_type": "spr",
            "spr_correct_answers": row["answers"],
            "spr_max_length": 6,
            "answer_key": f"<p><strong>Correct Answer: {row['answers'][0]}</strong></p><p>{row['why']}</p>",
        })
    else:
        out.update({
            "options": row["options"],
            "correct": row["correct_text"],
            "answer_key": f"<p><strong>Correct Answer: {row['letter']}</strong></p><p>{row['why']}</p>",
        })
    return out


def check(rows, name):
    assert len(rows) == 22, (name, len(rows))
    spr_pos = {i + 1 for i, r in enumerate(rows) if r["kind"] == "spr"}
    assert spr_pos == SPR_POSITIONS, (name, spr_pos)
    letters = Counter(r["letter"] for r in rows if r["letter"])
    assert letters == {"A": 4, "B": 4, "C": 4, "D": 4}, (name, letters)
    assert Counter(r["domain"] for r in rows) == DOMAIN_COUNTS, name


def build_test(number: int, usage: Counter) -> dict:
    rng = random.Random(7000 + number)
    used: set = set()
    m1 = build_module(rng, 1, usage, used)
    m2 = build_module(rng, 2, usage, used)
    check(m1, f"test {number} module 1")
    check(m2, f"test {number} module 2")
    questions = [to_json_row(i, 1 if i <= 22 else 2, row) for i, row in enumerate(m1 + m2, start=1)]
    return {
        "title": f"Academor SAT Practice Test {number} Math",
        "category_name": "SAT Math",
        "service": "sat-math",
        "is_sat": True,
        "sat_section": "algebra",
        "time_limit_minutes": 70,
        "questions": questions,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    usage: Counter = Counter()
    seen = set()
    for number in TESTS:
        data = build_test(number, usage)
        for q in data["questions"]:
            key = q["question"]
            assert key not in seen, f"duplicate question in test {number}: {q['skill']}"
            seen.add(key)
        out = OUT_DIR / f"academor_sat_math_test_{number}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        n_img = sum(1 for q in data["questions"] if "<img" in q["question"])
        n_spr = sum(1 for q in data["questions"] if q.get("question_type") == "spr")
        print(f"OK {out.relative_to(REPO)}: {len(data['questions'])} questions ({n_spr} SPR), {n_img} with figures, "
              f"{out.stat().st_size // 1024} KB")
    unused = [t["name"] for t in TEMPLATES if usage[t["name"]] == 0]
    print(f"templates used: {len(TEMPLATES) - len(unused)}/{len(TEMPLATES)}; unused: {unused}")


if __name__ == "__main__":
    main()
