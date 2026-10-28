# -*- coding: utf-8 -*-
"""C5.2 配套：各模型"R²>0 的维度数"（统一等级口径，可与主模型连续口径并列对照）"""
import os, sys, json
import numpy as np, pandas as pd
from sklearn.metrics import r2_score

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
import utils as U

d = pd.read_csv(os.path.join(ROOT, "submission", "q1_oof_predictions.csv"), encoding="utf-8-sig")
sens = [c.split("__", 1)[1] for c in d.columns if c.startswith("true__")]
MODELS = [("主模型", "main"), ("KNN 插补", "knn"), ("随机森林", "rf"),
          ("ElasticNet", "enet"), ("逐维均值", "mean")]

lvl = {}
for label, pref in MODELS:
    r2s = []
    for j in sens:
        t = d["true__" + j].values.astype(float)
        p = d[pref + "__" + j].values.astype(float)
        ok = np.isfinite(t) & np.isfinite(p)
        r2s.append(float(r2_score(t[ok], p[ok])) if ok.sum() > 5 else np.nan)
    r2s = np.array(r2s)
    lvl[label] = {"n_positive": int(np.nansum(r2s > 0)), "n": len(r2s),
                  "mean_r2_level": round(float(np.nanmean(r2s)), 4)}
    print("%-10s 等级口径 R2>0: %2d/50  meanR2=%.4f" % (label, lvl[label]["n_positive"],
                                                       lvl[label]["mean_r2_level"]))

# 主模型的连续口径（与 problem_1_results.json 一致）
p1 = json.load(open(os.path.join(ROOT, "figures", "problem_1_results.json"), encoding="utf-8"))
r2c = np.array([p1["per_dim"][c]["r2_main"] for c in sens])
print("主模型 连续口径 R2>0: %d/50  meanR2=%.4f" % (int((r2c > 0).sum()), r2c.mean()))

out = {"level_basis": lvl,
       "main_continuous": {"n_positive": int((r2c > 0).sum()), "n": len(r2c),
                           "mean_r2": round(float(r2c.mean()), 4)},
       "note": "level_basis 为 0-6 等级预测对 0-6 等级标签的 R²（五模型同口径、可横向比较）；"
               "main_continuous 为主模型连续预测对 4.csv 标准化连续标签的 R²，"
               "与 problem_1_results.json 的 r2_main 一致，仅用于说明主模型在连续口径下 46/50 维为正。"}
p = os.path.join(ROOT, "figures", "derived", "q1_r2_positive.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved")
