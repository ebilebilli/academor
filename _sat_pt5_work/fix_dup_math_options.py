"""Fix MCQ questions whose OCR produced duplicate option texts."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path("academor/portals/resources/sat_questions")


def letter_from_answer_key(answer_key: str) -> str | None:
    m = re.search(r"Correct Answer:\s*([A-D])\b", answer_key or "")
    return m.group(1) if m else None


def fix_file(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    fixed = 0
    for q in data["questions"]:
        if q.get("question_type") == "spr" or q.get("spr_correct_answers"):
            continue
        opts = q.get("options") or []
        if len(opts) < 2:
            continue
        if len(opts) == len(set(opts)):
            continue
        letter = letter_from_answer_key(q.get("answer_key") or "")
        if letter not in "ABCD":
            # fall back: try to keep index from first unique attempt
            continue
        q["options"] = ["A", "B", "C", "D"]
        q["correct"] = letter
        fixed += 1
    if fixed:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return fixed


def main() -> None:
    total = 0
    for path in sorted(ROOT.glob("sat_practice_test_*_math.json")):
        n = fix_file(path)
        print(f"{path.name}: fixed {n}")
        total += n
    print("TOTAL_FIXED", total)


if __name__ == "__main__":
    main()
