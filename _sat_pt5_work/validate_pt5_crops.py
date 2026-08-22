import base64
import importlib.util
import json
import re
from pathlib import Path

spec = importlib.util.spec_from_file_location("r", "_sat_pt5_work/rebuild_math_crops.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print(m.process(5))

d = json.loads(
    Path("academor/portals/resources/sat_questions/sat_practice_test_5_math.json").read_text(
        encoding="utf-8"
    )
)
mcq = [q for q in d["questions"] if q.get("options")]
print("mcq", len(mcq))
print("opt img", sum(1 for q in mcq if str(q["options"][0]).startswith("<img")))
print("letter only", sum(1 for q in mcq if q["options"] == ["A", "B", "C", "D"]))
print("with fig", sum(1 for q in d["questions"] if 'alt="figure"' in q["question"]))
for qid in [1, 2, 3, 5, 6]:
    q = next(x for x in d["questions"] if x["id"] == qid)
    imgs = re.findall(r"data:image/png;base64,([A-Za-z0-9+/=]+)", q["question"])
    opt0 = (q.get("options") or [""])[0]
    print("Q", qid, "fig", len(imgs), "opt", ("IMG" if str(opt0).startswith("<img") else str(opt0)[:50]))
    if imgs:
        Path(f"_sat_pt5_work/v2_q{qid}.png").write_bytes(base64.b64decode(imgs[0]))
    if str(opt0).startswith("<img"):
        mm = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", opt0)
        Path(f"_sat_pt5_work/v2_q{qid}_a.png").write_bytes(base64.b64decode(mm.group(1)))
