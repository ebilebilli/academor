import json
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

d7 = json.loads(
    Path("academor/portals/resources/sat_questions/sat_practice_test_7_math.json").read_text(encoding="utf-8")
)
for q in d7["questions"]:
    if 'alt="question"' in q["question"]:
        print("PT7 stem-img id", q["id"])

d11 = json.loads(
    Path("academor/portals/resources/sat_questions/sat_practice_test_11_math.json").read_text(
        encoding="utf-8"
    )
)
mcq = [q for q in d11["questions"] if q.get("options")]
for q in mcq:
    if any(str(o).startswith("<img") for o in q["options"]):
        kinds = ["IMG" if str(o).startswith("<img") else o for o in q["options"]]
        print("PT11 id", q["id"], kinds)
