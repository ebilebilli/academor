"""Build the original Academor SAT Reading and Writing practice tests 2–10 (54 questions each).

Same blueprint as practice test 1 (scripts/build_sat_academor_verbal.py):
  * 2 modules x 27 questions (64 minutes in total), one short passage (or passage pair) per question
  * each module runs Craft and Structure (7) -> Information and Ideas (7) ->
    Standard English Conventions (7) -> Expression of Ideas (6), with the same skill mix:
      Words in Context 4, Text Structure and Purpose 2, Cross-Text Connections 1,
      Central Ideas and Details 2, Command of Evidence: Textual 1, Command of Evidence: Quantitative 3,
      Inferences 1, Form, Structure, and Sense 4, Boundaries 3, Transitions 3, Rhetorical Synthesis 3
  * the 3 quantitative Command of Evidence questions in each module have a data graphic

The questions live in scripts/sat_verbal/test_NN.py. Each item is written as the correct choice plus
three wrong ones; this builder places the correct choice so the letters are spread evenly in every
module (7 / 7 / 7 / 6), with a fixed seed per test so the files are reproducible.

All passages are original. Researchers named in science passages and the data in the graphics are
fictional unless the passage is about a well-known historical fact.

Output: academor/portals/resources/sat_questions/academor_sat_verbal_test_{2..10}.json
Load:   python academor/manage.py load_sat_quiz_resources --file academor_sat_verbal_test_N.json

Requires matplotlib (not a runtime dependency of the site):
    uv run --with matplotlib python scripts/build_sat_academor_verbal_set.py
"""

from __future__ import annotations

import importlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sat_verbal.common import CS, EOI, II, LETTERS, SEC  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"
TESTS = range(2, 11)

SKILL_PLAN = Counter({
    (CS, "Words in Context"): 4,
    (CS, "Text Structure and Purpose"): 2,
    (CS, "Cross-Text Connections"): 1,
    (II, "Central Ideas and Details"): 2,
    (II, "Command of Evidence: Textual"): 1,
    (II, "Command of Evidence: Quantitative"): 3,
    (II, "Inferences"): 1,
    (SEC, "Form, Structure, and Sense"): 4,
    (SEC, "Boundaries"): 3,
    (EOI, "Transitions"): 3,
    (EOI, "Rhetorical Synthesis"): 3,
})
DOMAIN_ORDER = [CS, II, SEC, EOI]


def check_module(items, name):
    assert len(items) == 27, (name, len(items))
    plan = Counter((it["domain"], it["skill"]) for it in items)
    assert plan == SKILL_PLAN, (name, plan - SKILL_PLAN, SKILL_PLAN - plan)
    order = [DOMAIN_ORDER.index(it["domain"]) for it in items]
    assert order == sorted(order), (name, "domains out of order")
    for it in items:
        opts = [it["correct"]] + it["wrong"]
        assert len(opts) == 4 and len(set(opts)) == 4, (name, it["skill"], opts)
        if it["skill"] == "Command of Evidence: Quantitative":
            assert "<img" in it["question"], (name, "quantitative item without a graphic")


def place(items, rng):
    """Spread the correct letters 7/7/7/6 over the module and build the option lists."""
    counts = [7, 7, 7, 7]
    counts[rng.randrange(4)] = 6
    letters = [L for L, k in zip(LETTERS, counts) for _ in range(k)]
    rng.shuffle(letters)
    out = []
    for it, letter in zip(items, letters):
        t = LETTERS.index(letter)
        wrong = list(it["wrong"])
        options = wrong[:t] + [it["correct"]] + wrong[t:]
        out.append({**it, "options": options, "letter": letter})
    return out


def build_test(number: int) -> dict:
    mod = importlib.import_module(f"sat_verbal.test_{number:02d}")
    m1, m2 = mod.module_1(), mod.module_2()
    check_module(m1, f"test {number} module 1")
    check_module(m2, f"test {number} module 2")
    rng = random.Random(9100 + number)
    m1, m2 = place(m1, rng), place(m2, rng)
    questions = []
    for i, it in enumerate(m1 + m2, start=1):
        questions.append({
            "id": i,
            "module": 1 if i <= 27 else 2,
            "domain": it["domain"],
            "skill": it["skill"],
            "question": it["question"],
            "options": it["options"],
            "correct": it["correct"],
            "answer_key": f"<p><strong>Correct Answer: {it['letter']}</strong></p><p>{it['why']}</p>",
        })
    return {
        "title": f"Academor SAT Practice Test {number} Reading and Writing",
        "category_name": "SAT Reading and Writing",
        "service": "sat-verbal",
        "is_sat": True,
        "sat_section": "reading",
        "time_limit_minutes": 64,
        "questions": questions,
    }


def main(numbers=None):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    seen: dict[str, int] = {}
    for number in numbers or TESTS:
        data = build_test(number)
        for q in data["questions"]:
            body = q["question"]
            assert body not in seen, f"test {number} repeats a passage from test {seen[body]}"
            seen[body] = number
        out = OUT_DIR / f"academor_sat_verbal_test_{number}.json"
        out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        letters = Counter(q["options"].index(q["correct"]) for q in data["questions"])
        letters = {LETTERS[k]: v for k, v in letters.items()}
        n_img = sum(1 for q in data["questions"] if "<img" in q["question"])
        print(f"OK {out.relative_to(REPO)}: {len(data['questions'])} questions, {n_img} with graphics, "
              f"letters {dict(sorted(letters.items()))}, {out.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or None)
