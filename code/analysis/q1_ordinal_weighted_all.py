# -*- coding: utf-8 -*-
"""Q1 全 50 维类加权有序回归对照：为表 4 的同口径比较提供可复现值。

背景：表 4 的「统一有序回归（不加权）」列用的是阈值二分类器不加权的版本，
而「本文采用」列用的是类加权版本，两列口径不同。本脚本把类加权口径
铺到全部 50 维，报告 QWK / Spearman / ±1 三项指标，用于正文的取舍论证。

输出 figures/derived/q1_ordinal_weighted_all.json。
"""
import os
import sys
import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.model_selection import StratifiedKFold

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))

import params as P
import utils as U
import problem1 as Q1

U.set_all_seeds(P.SEED)
df1, X, feat, meta = U.load_chem(os.path.join(ROOT, "user_data"))
Y, sens = U.load_sensory(os.path.join(ROOT, "user_data"))
Xv = np.asarray(X.values, dtype=float)
Yv = np.asarray(Y.values, dtype=float)
styles = meta[P.STYLE_COL].values

vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else "_rare" for s in styles])
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)
folds = list(skf.split(Xv, strat))

J = len(sens)
oof = np.full((P.N_SAMPLES, J), -1, dtype=int)
tru_lv = np.full((P.N_SAMPLES, J), -1, dtype=int)
reg_cont = np.full((P.N_SAMPLES, J), np.nan)
for tr, va in folds:
    for j in range(J):
        b = U.Binner().fit(Yv[tr, j])
        tru_lv[va, j] = b.transform(Yv[va, j])
        oof[va, j] = Q1._fit_ordinal(Xv[tr], Yv[tr, j], Xv[va])
        reg_cont[va, j] = Q1._fit_lgb(Xv[tr], Yv[tr, j]).predict(Xv[va])
    print("fold done", flush=True)

k = U.quadratic_weighted_kappa
q = np.array([k(tru_lv[:, j], oof[:, j]) for j in range(J)])
sp_ord = np.array([spearmanr(oof[:, j], Yv[:, j]).correlation for j in range(J)])
sp_reg = np.array([spearmanr(reg_cont[:, j], Yv[:, j]).correlation for j in range(J)])
p1_ord = np.array([np.mean(np.abs(oof[:, j] - tru_lv[:, j]) <= 1) for j in range(J)])

degen = [Q1.binning_degenerate(Yv[:, j]) for j in range(J)]
di = [j for j in range(J) if degen[j]]

out = {
    "dims": sens,
    "degen": [sens[j] for j in di],
    "qwk_ordinal_weighted": [round(float(v), 4) for v in q],
    "spearman_ordinal": round(float(np.nanmean(sp_ord)), 4),
    "spearman_regression": round(float(np.nanmean(sp_reg)), 4),
    "pm1_ordinal": round(float(np.mean(p1_ord)), 4),
    "mean_ordinal_weighted": round(float(q.mean()), 4),
    "degen_ordinal_weighted": round(float(np.mean(q[di])), 4),
    "rest_ordinal_weighted": round(float(np.mean([q[j] for j in range(J) if j not in di])), 4),
    "note": "类加权阈值分解铺到全部 50 维（与主流水线同一 _fit_ordinal），只用训练折估计，不接触验证折。",
}
path = os.path.join(ROOT, "figures", "derived", "q1_ordinal_weighted_all.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps({kk: vv for kk, vv in out.items() if kk not in ("dims", "qwk_ordinal_weighted")},
                 ensure_ascii=False, indent=1))
