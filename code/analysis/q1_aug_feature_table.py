# -*- coding: utf-8 -*-
"""C3a：43 个阈值超限列 + 8 个模块 PC1 的完整清单（供附录表 B.1 / B.2）。

阈值列口径与 code/analysis/q1_feature_aug.py 完全一致：
  读 8.xlsx 的 Sensory thresholds，筛 threshold_mean 非空且 field_name_R 在 231 特征内；
  按 figures/derived/q1_col_scale.json 判定 log10 换算（log10 列取 log10(threshold)）；
  超阈比例按全样本统计（与增广实验的训练折口径方向一致，仅作描述性说明）。

模块 PC1：从 q2_full_network.json 的 nodes 按 comm 分组，取成员 >=5 的前 8 个模块；
  逐折在训练折上 fit PCA 后记录第一主成分解释方差率，报五折均值。
"""
import os
import sys
import json

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
import params as P
import utils as U

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, "user_data"))
Xv = np.asarray(X.values, dtype=float)
idx = {c: i for i, c in enumerate(feat)}
scale = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_col_scale.json"), encoding="utf-8"))
th = pd.read_excel(os.path.join(ROOT, "user_data", "8.xlsx"), sheet_name="Sensory thresholds")

# ---------- 阈值列 ----------
rows = []
for _, r in th.iterrows():
    if not pd.notna(r["threshold_mean"]):
        continue
    c = r["field_name_R"]
    if c not in idx:
        continue
    t_raw = float(r["threshold_mean"])
    kind = scale.get(c)
    t_use = float(np.log10(t_raw)) if (kind == "log10" and t_raw > 0) else t_raw
    col = Xv[:, idx[c]]
    ok = np.isfinite(col)
    frac = float(np.mean(col[ok] >= t_use)) if ok.sum() else float("nan")
    rows.append({"field": c, "source": str(r.get("compound_source", "")).strip(),
                 "scale": kind or "raw", "threshold_raw": round(t_raw, 6),
                 "threshold_1csv": round(t_use, 6), "over_frac": round(frac, 4),
                 "n_valid": int(ok.sum())})
rows.sort(key=lambda d: -d["over_frac"])
json.dump({"n_cols": len(rows), "cols": rows},
          open(os.path.join(ROOT, "figures", "derived", "q1_threshold_cols.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("threshold cols:", len(rows))

# ---------- 模块 PC1 ----------
net = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_full_network.json"), encoding="utf-8"))
node_names = [n["name"] for n in net["nodes"]]
comm = {}
for n in net["nodes"]:
    comm.setdefault(n["comm"], []).append(n["name"])
mods = [m for m in comm.items() if m[0] != "" and len(m[1]) >= 5]
mods.sort(key=lambda kv: -len(kv[1]))
mods = mods[:8]

styles = meta[P.STYLE_COL].values
vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else "_rare" for s in styles])
from sklearn.model_selection import StratifiedKFold
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)
folds = list(skf.split(Xv, strat))

deg = {n["name"]: n["deg"] for n in net["nodes"]}
out_mods = []
for cid, members in mods:
    pos = [idx[m] for m in members if m in idx]
    ratios = []
    for tr, _ in folds:
        sub = Xv[np.ix_(tr, pos)]
        med = np.nanmedian(sub, axis=0)
        sub = np.where(np.isnan(sub), med, sub)
        ratios.append(float(PCA(n_components=1).fit(sub).explained_variance_ratio_[0]))
    reps = sorted(members, key=lambda m: -deg.get(m, 0))[:3]
    out_mods.append({"comm": cid, "n_members": len(members),
                     "pc1_var_ratio_mean": round(float(np.mean(ratios)), 4),
                     "pc1_var_ratio_std": round(float(np.std(ratios, ddof=1)), 4),
                     "representatives": reps})
json.dump({"n_modules": len(out_mods), "modules": out_mods},
          open(os.path.join(ROOT, "figures", "derived", "q1_pc1_modules.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("modules:", len(out_mods))
for m in out_mods:
    print(" ", m["comm"], m["n_members"], m["pc1_var_ratio_mean"], m["representatives"])
