import importlib.util
import io
import json
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

spec = importlib.util.spec_from_file_location("r", "scripts/rebuild_sat_math.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

print(m.process(5))

d = json.loads(
    Path("academor/portals/resources/sat_questions/sat_practice_test_5_math.json").read_text(
        encoding="utf-8"
    )
)
mcq = [q for q in d["questions"] if q.get("options")]
print("mcq total", len(mcq))
img_opts = [q for q in mcq if any(str(o).startswith("<img") for o in q["options"])]
print("questions with >=1 img option", len(img_opts))
for q in img_opts:
    kinds = ["IMG" if str(o).startswith("<img") else o for o in q["options"]]
    print(" Q", q["id"], kinds)

print()
print("=== text-only sample ===")
for q in mcq:
    if not any(str(o).startswith("<img") for o in q["options"]):
        print(q["id"], q["options"])
