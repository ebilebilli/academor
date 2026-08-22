import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(r"C:\Users\user\Desktop\Academor")
for n in [7, 11]:
    p = REPO / "academor" / "portals" / "resources" / "sat_questions" / f"sat_practice_test_{n}_math.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for q in d["questions"]:
        if 'alt="question"' in q["question"]:
            print(f"PT{n} id={q['id']} STEM_IMG")
