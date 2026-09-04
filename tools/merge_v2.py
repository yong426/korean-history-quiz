# -*- coding: utf-8 -*-
"""tools/exp2/<회차>.json(빨간펜 구조 해설) → data.js의 해당 문항에 why/fx/tip/neg 필드로 병합.
검증 통과한 회차만 반영. 사용: python tools/merge_v2.py"""
import os, json, glob, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "data.js")
s = open(p, encoding="utf-8").read()
data = json.loads(s[s.index("=") + 1:].rstrip().rstrip(";"))
byid = {q["id"]: q for q in data["questions"]}
total = 0
for f in sorted(glob.glob(os.path.join(ROOT, "tools", "exp2", "*.json"))):
    r = os.path.splitext(os.path.basename(f))[0]
    if ".part" in r: continue
    items = {e["n"]: e for e in json.load(open(f, encoding="utf-8"))}
    bad = []
    for n in range(1, 51):
        q = byid.get(f"{r}-{n}"); e = items.get(n)
        if not q or not e or not e.get("why") or not e.get("topic"): bad.append(n); continue
        fx = e.get("fixes", [])
        ok = all(isinstance(x.get("o"), int) and 1 <= x["o"] <= 4 and x.get("wrong") and x.get("right") for x in fx)
        if not ok or (any(x["o"] == q["ans"] for x in fx) and not e.get("neg")) or (not fx and not e.get("flag")): bad.append(n)
    if bad:
        print(f"! {r}: 형식 이상 {bad} → 제외"); continue
    for n in range(1, 51):
        q = byid[f"{r}-{n}"]; e = items[n]
        q["topic"] = e["topic"].strip()
        q["why"] = re.sub(r"\s+", " ", e["why"]).strip()
        q["fx"] = [[x["o"], x["wrong"].strip(), x["right"].strip()] for x in sorted(e.get("fixes", []), key=lambda x: x["o"])]
        for k in ("neg", "tip"):
            q.pop(k, None)
        if e.get("neg"): q["neg"] = 1
        if e.get("tip"): q["tip"] = e["tip"].strip()
    flags = [(n, items[n]["flag"]) for n in range(1, 51) if items[n].get("flag")]
    total += 50
    print(f"{r}: 50문항 OK" + (f"  flag {flags}" if flags else ""))
open(p, "w", encoding="utf-8").write("window.QUIZ_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(f"v2 반영 {total}문항 / 전체 {len(data['questions'])}")
