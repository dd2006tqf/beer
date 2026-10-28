# -*- coding: utf-8 -*-
"""C2 配套：50x50 感官相关矩阵的分组结构统计（供图注与正文引用）。"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
raw = pd.read_csv(os.path.join(ROOT, "user_data", "5.csv"), index_col=0)
M = raw.values.astype(float)
sens = pd.read_csv(os.path.join(ROOT, "user_data", "4.csv"), nrows=0).columns[3:].tolist()
assert len(sens) == 50

def grp(s):
    return "A" if s.startswith("A_") else ("F" if s.startswith("F_") else "X")

g = np.array([grp(s) for s in sens])
iu = np.triu_indices(50, k=1)
vals = M[iu]

def block(ga, gb):
    ma = g == ga
    mb = g == gb
    sel = np.array([ma[i] and mb[j] for i, j in zip(*iu)])
    return vals[sel]

out = {"n_dims": 50, "min": round(float(vals.min()), 4), "max": round(float(vals.max()), 4),
       "median_abs": round(float(np.median(np.abs(vals))), 4)}
for name, (a, b) in {"AA": ("A", "A"), "FF": ("F", "F"), "XX": ("X", "X"),
                     "AF": ("A", "F"), "AX": ("A", "X"), "FX": ("F", "X")}.items():
    v = block(a, b)
    out[name] = {"n": int(len(v)), "median_abs": round(float(np.median(np.abs(v))), 4),
                 "mean_abs": round(float(np.mean(np.abs(v))), 4),
                 "max_abs": round(float(np.max(np.abs(v))), 4)}
# 强相关对数
out["n_abs_ge_0.6"] = int((np.abs(vals) >= 0.6).sum())
out["n_abs_ge_0.5"] = int((np.abs(vals) >= 0.5).sum())
p = os.path.join(ROOT, "figures", "derived", "q1_sensory_matrix_stats.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
