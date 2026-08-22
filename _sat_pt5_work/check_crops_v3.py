import base64
import importlib.util
import json
import re
from pathlib import Path

spec = importlib.util.spec_from_file_location("r", "_sat_pt5_work/rebuild_math_crops.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

import pymupdf as fitz

pdf = m.find_pdf(5)
doc = fitz.open(pdf)
pages = m.find_module_pages(doc)

for qn in [1, 3, 5]:
    loc = m.find_marker_on_pages(doc, pages["math1"], pages["math1_end"], qn)
    pidx, marker = loc
    page = doc[pidx]
    markers = m.question_markers(page)
    yb = m.question_band_bottom(page, marker, markers)
    fig = m.figure_clip_for_question(page, marker, yb)
    clips = m.option_clips(page, marker, yb)
    print("Q", qn, "page", pidx, "fig", fig)
    if fig:
        Path(f"_sat_pt5_work/v3_q{qn}_fig.png").write_bytes(
            base64.b64decode(m.png_data_uri(page, fig).split(",", 1)[1])
        )
    if clips:
        for L in "AB":
            Path(f"_sat_pt5_work/v3_q{qn}_{L}.png").write_bytes(
                base64.b64decode(m.png_data_uri(page, clips[L], zoom=2.8).split(",", 1)[1])
            )
            print(" ", L, [round(x) for x in clips[L]], "h", round(clips[L].height))

d = json.loads(
    Path("academor/portals/resources/sat_questions/sat_practice_test_5_math.json").read_text(
        encoding="utf-8"
    )
)
q3 = next(x for x in d["questions"] if x["id"] == 3)
print("Q3 stem has figure", 'alt="figure"' in q3["question"])
print("Q3 stem has question img", 'alt="question"' in q3["question"])
opt = q3["options"][0]
mm = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]+)", opt)
Path("_sat_pt5_work/v3_json_q3_a.png").write_bytes(base64.b64decode(mm.group(1)))
