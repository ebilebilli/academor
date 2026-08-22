import json
import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

REPO = Path(r"C:\Users\user\Desktop\Academor")
for n in [4,5,6,7,8,9,10,11]:
    p = REPO / "academor" / "portals" / "resources" / "sat_questions" / f"sat_practice_test_{n}_math.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    for q in d["questions"]:
        opts = q.get("options")
        if not opts:
            continue
        for o in opts:
            if isinstance(o, str) and re.search(r"\d/\d", o) and not o.startswith("<img"):
                print(f"PT{n} id={q['id']} opt={o!r}")
