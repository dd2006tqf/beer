# -*- coding: utf-8 -*-
"""C4：150 条全量 Top-3 A/B/C 分级（附录表 B.4 的数据源）。"""
import os, json
import csv

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
d = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_evidence_full.json"), encoding="utf-8"))
sens = list(d.keys())
assert len(sens) == 50

rows = []
for s in sens:
    for r in sorted(d[s], key=lambda x: x["rank"]):
        rows.append({
            "dim": s, "rank": r["rank"], "compound": r["compound"],
            "freq": r["freq"], "cond_norm": r["cond_norm"], "mod_norm": r["mod_norm"],
            "n_pos": r["n_folds_pos"], "r2": r["r2"], "above_null": r["above_null"],
            "grade": r["grade"],
        })
assert len(rows) == 150, len(rows)

from collections import Counter
c = Counter(r["grade"] for r in rows)
print("grade counts:", dict(c))
print("ranks:", Counter(r["rank"] for r in rows))

with open(os.path.join(ROOT, "figures", "derived", "q2_appendix_grade_rows.csv"), "w",
          encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print("saved 150 rows")
