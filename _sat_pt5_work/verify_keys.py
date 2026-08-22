import json
from pathlib import Path

d = json.loads(
    Path("academor/portals/resources/sat_questions/sat_practice_test_5_verbal.json").read_text(
        encoding="utf-8"
    )
)
# Official College Board answer key (Practice Test 5), first 27 each module
M1 = "ABBDBDBCBBDADBCBABACADBDBBD"
M2 = "CDAACCBAADADDDDBAABACBACCBC"
keys = M1 + M2
print("lens", len(M1), len(M2), len(keys))
assert len(keys) == 54
mism = []
for i, q in enumerate(d["questions"]):
    expected = keys[i]
    letter = "ABCD"[q["options"].index(q["correct"])]
    status = "OK" if letter == expected else "WRONG"
    if letter != expected:
        mism.append((q["id"], expected, letter, q["correct"][:50]))
    print(f"Q{q['id']:02d} expected {expected} got {letter} {status}")
print("mismatches", len(mism))
for row in mism:
    print(" ", row)
