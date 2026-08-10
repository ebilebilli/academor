# -*- coding: utf-8 -*-
"""Write strengthened CEFR reading-test JSON files."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Allow importing sibling modules when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent))

from _reading_a1_data import A1, word_count
from _reading_a2_data import A2
from _reading_b1_data import B1

OUT = Path(__file__).resolve().parents[1] / "academor" / "portals" / "resources" / "quiz_questions"


def validate(item: dict) -> None:
    passage = item["shared_passage"]
    assert item["has_shared_passage"] is True
    assert passage.startswith("<p>")
    assert len(item["questions"]) == 10
    for qrow in item["questions"]:
        opts = qrow["options"]
        assert isinstance(opts, list) and len(opts) == 4, qrow
        assert all(isinstance(o, str) for o in opts), qrow
        assert 0 <= qrow["answer"] < 4


def write_all() -> None:
    targets = {"A1": (100, 160), "A2": (150, 230), "B1": (200, 340)}
    written = 0
    for level_items, prefix in ((A1, "a1"), (A2, "a2"), (B1, "b1")):
        for item in level_items:
            validate(item)
            n = item["quiz"]
            path = OUT / f"{prefix}_reading_test_{n:02d}.json"
            path.write_text(json.dumps(item, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            wc = word_count(item["shared_passage"])
            lo, hi = targets[item["level"]]
            flag = "OK" if lo <= wc <= hi else f"CHECK({lo}-{hi})"
            print(f"{path.name}: {wc} words [{flag}] — {item['title']}")
            written += 1
    print(f"Wrote {written} files to {OUT}")


if __name__ == "__main__":
    write_all()
