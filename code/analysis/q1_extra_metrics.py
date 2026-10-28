# -*- coding: utf-8 -*-
"""Q1 表 5 补充指标：等级口径的 MAE / RMSE / 严格一致率 + 两种 Pearson。

数据源 submission/q1_oof_predictions.csv（折外预测，五个模型同一批样本）。
等级口径的 true__* 与 <model>__* 均为 0-6 整数；maincont__* 为主模型的连续输出。

Pearson 给两种口径：
  - pearson_vs_cont：与 4.csv 标准化连续值的相关（表 5 采用这一列）
  - pearson_vs_level：与 0-6 等级的相关（主模型的备选参照）

自检：同时算 QWK，须与 problem_1_results.json 的 0.3830 / 0.3652 /
0.3280 / 0.2762 / 0.0015 对齐，否则说明口径不一致。

输出 figures/derived/q1_extra_metrics.json。
"""
import os
import sys
import json

import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
import utils as U

d = pd.read_csv(os.path.join(ROOT, "submission", "q1_oof_predictions.csv"), encoding="utf-8-sig")
Y, _ = U.load_sensory(os.path.join(ROOT, "user_data"))
sens = [c.split("__", 1)[1] for c in d.columns if c.startswith("true__")]

MODELS = [("主模型", "main", "maincont"), ("KNN 插补", "knn", None),
          ("随机森林", "rf", None), ("ElasticNet", "enet", None), ("逐维均值", "mean", None)]


def qwk(t, p):
    return float(U.quadratic_weighted_kappa(np.asarray(t, int), np.asarray(p, int)))


rows, check = {}, {}
for label, pref, cont in MODELS:
    mae, rmse, exact, r2, pear_c, pear_l = [], [], [], [], [], []
    for j in sens:
        lvl = d["true__" + j].values.astype(float)
        pred = d[pref + "__" + j].values.astype(float)
        ok = np.isfinite(lvl) & np.isfinite(pred)
        lvl, pred = lvl[ok], pred[ok]
        diff = pred - lvl
        mae.append(np.mean(np.abs(diff)))
        rmse.append(np.sqrt(np.mean(diff ** 2)))
        exact.append(np.mean(pred == lvl))
        ss_res = float(np.sum(diff ** 2))
        ss_tot = float(np.sum((lvl - lvl.mean()) ** 2))
        r2.append(1 - ss_res / ss_tot if ss_tot > 0 else np.nan)

        src = d[(cont or pref) + "__" + j].values.astype(float)
        ct = Y[j].values.astype(float)
        ok1 = np.isfinite(src) & np.isfinite(ct)
        if ok1.sum() > 3 and np.std(src[ok1]) > 0:
            pear_c.append(pearsonr(src[ok1], ct[ok1]).statistic)
        ok2 = np.isfinite(src) & np.isfinite(lvl)
        if ok2.sum() > 3 and np.std(src[ok2]) > 0:
            pear_l.append(pearsonr(src[ok2], lvl[ok2]).statistic)

    rows[label] = {
        "mae": round(float(np.mean(mae)), 4),
        "rmse": round(float(np.mean(rmse)), 4),
        "exact": round(float(np.mean(exact)), 4),
        "r2_level": round(float(np.nanmean(r2)), 4),
        "pearson_vs_cont": round(float(np.nanmean(pear_c)), 4),
        "pearson_vs_level": round(float(np.nanmean(pear_l)), 4),
    }
    check[label] = round(float(np.mean([qwk(d["true__" + j], d[pref + "__" + j]) for j in sens])), 4)

out = {
    "n_dims": len(sens),
    "models": rows,
    "qwk_recheck": check,
    "note": ("等级口径 MAE/RMSE/严格一致率按 0-6 整数计算，50 维宏平均；"
             "pearson_vs_cont 为与 4.csv 标准化连续值的相关（表 5 采用），"
             "pearson_vs_level 为与 0-6 等级的相关。"),
}
path = os.path.join(ROOT, "figures", "derived", "q1_extra_metrics.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
