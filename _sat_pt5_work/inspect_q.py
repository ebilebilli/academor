import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "academor" / "portals" / "resources" / "sat_questions"

pt = int(sys.argv[1]) if len(sys.argv) > 1 else 4
qid = int(sys.argv[2]) if len(sys.argv) > 2 else 1

fp = OUT_DIR / f"sat_practice_test_{pt}_math.json"
d = json.loads(fp.read_text(encoding="utf-8"))
q = next(x for x in d["questions"] if x["id"] == qid)
print("has fig:", 'alt="figure"' in q["question"])
print("has stem img:", 'alt="question"' in q["question"])
txt = re.sub(r"<img[^>]*>", "[IMG]", q["question"])
print("STEM:", txt)
opts = q.get("options")
if opts:
    for i, o in enumerate(opts):
        o2 = re.sub(r"<img[^>]*>", "[IMG]", str(o))
        print(f"OPT {chr(65+i)}:", o2[:120])
print("correct is img?", str(q.get("correct")).startswith("<img"))
