import base64
import json
import re
from pathlib import Path

for n in [5, 7, 9]:
    d = json.loads(
        Path(f"academor/portals/resources/sat_questions/sat_practice_test_{n}_math.json").read_text(
            encoding="utf-8"
        )
    )
    for q in d["questions"]:
        imgs = re.findall(r"data:image/png;base64,([A-Za-z0-9+/=]+)", q["question"])
        if imgs:
            raw = base64.b64decode(imgs[0])
            qid = q["id"]
            Path(f"_sat_pt5_work/dbg_pt{n}_q{qid}_fig.png").write_bytes(raw)
            print(n, qid, "bytes", len(raw))
