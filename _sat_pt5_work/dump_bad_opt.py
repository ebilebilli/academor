import base64
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"

fp = OUT_DIR / "sat_practice_test_4_math.json"
data = json.loads(fp.read_text(encoding="utf-8"))
q = next(x for x in data["questions"] if x["id"] == 1)
opts = q["options"]
for i, o in enumerate(opts):
    mm = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", o)
    raw = base64.b64decode(mm.group(1))
    Path(f"_sat_pt5_work/bad_pt4_q1_{chr(65+i)}.png").write_bytes(raw)
print("stem:", q["question"][:200])
