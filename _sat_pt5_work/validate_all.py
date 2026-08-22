import json
import pathlib

d = pathlib.Path("academor/portals/resources/sat_questions")
problems = []
for p in sorted(d.glob("*.json")):
    j = json.load(open(p, encoding="utf-8"))
    qs = j.get("questions", [])
    for i, q in enumerate(qs):
        qtype = (q.get("question_type") or "mcq").strip().lower()
        if qtype == "spr":
            if not q.get("spr_correct_answers"):
                problems.append(f"{p.name} #{i+1} (id={q.get('id')}): SPR missing spr_correct_answers")
        else:
            opts = [str(o).strip() for o in (q.get("options") or []) if str(o).strip()]
            if len(opts) < 2:
                problems.append(f"{p.name} #{i+1} (id={q.get('id')}): only {len(opts)} non-empty options")
                continue
            correct = (q.get("correct") or "").strip()
            if not correct:
                problems.append(f"{p.name} #{i+1} (id={q.get('id')}): missing correct answer")
            elif correct not in opts:
                problems.append(f"{p.name} #{i+1} (id={q.get('id')}): correct answer not in options: {correct!r} vs {opts!r}")
        if not (q.get("question") or "").strip():
            problems.append(f"{p.name} #{i+1} (id={q.get('id')}): missing question text")

if problems:
    print(f"{len(problems)} PROBLEM(S):")
    for pr in problems:
        print(" -", pr)
else:
    print("All good, no problems found.")
