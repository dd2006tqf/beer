# -*- coding: utf-8 -*-
"""C2 补充：A_/F_ 同名配对（同一感官属性的香气通道 vs 风味通道）的相关强度。"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
M = pd.read_csv(os.path.join(ROOT, "user_data", "5.csv"), index_col=0).values.astype(float)
sens = pd.read_csv(os.path.join(ROOT, "user_data", "4.csv"), nrows=0).columns[3:].tolist()
pos = {s: i for i, s in enumerate(sens)}

pairs, matched = [], 0
for i, s in enumerate(sens):
    if not s.startswith("A_"):
        continue
    twin = "F_" + s[2:]
    if twin in pos:
        matched += 1
        r = float(M[i, pos[twin]])
        if abs(r) >= 0.3:
            pairs.append({"a": s, "f": twin, "r": round(r, 3)})

rs = [p["r"] for p in pairs]
out = {
    "n_A_dims": sum(s.startswith("A_") for s in sens),
    "n_matched_pairs": matched,
    "median_r": round(float(np.median(rs)), 4),
    "mean_r": round(float(np.mean(rs)), 4),
    "min_r": round(float(min(rs)), 4),
    "max_r": round(float(max(rs)), 4),
    "n_ge_0.6": int(sum(1 for r in rs if r >= 0.6)),
    "pairs_sorted": sorted(pairs, key=lambda d: -d["r"]),
}
p = os.path.join(ROOT, "figures", "derived", "q1_sensory_af_pairs.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("matched", matched, "median_r", out["median_r"], "n>=0.6", out["n_ge_0.6"])
for d in out["pairs_sorted"][:6]:
    print(d)
