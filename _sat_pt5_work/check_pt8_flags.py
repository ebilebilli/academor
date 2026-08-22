import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(r"C:\Users\user\Desktop\Academor")
p = REPO / "academor" / "portals" / "resources" / "sat_questions" / "sat_practice_test_8_math.json"
d = json.loads(p.read_text(encoding="utf-8"))
for q in d["questions"]:
    opts = q.get("options")
    if not opts:
        continue
    if any(isinstance(o, str) and o.startswith("<img") for o in opts):
        print(f"id={q['id']}")
