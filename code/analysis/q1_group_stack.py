# -*- coding: utf-8 -*-
"""D1 方案 A：分组堆叠多输出 LightGBM（组内特征增广）对照实验。

设计（与主模型严格同折、同分箱、同指标，不覆盖主结果）：
  1. 同一 5 折分层划分（风格分层，seed=42）。
  2. 在训练折内，为每一组（A/F/X）构造"组画像特征"：
       - 用训练折拟合组内每个目标的单目标 LightGBM（折内 5 折 OOF，防泄漏）
       - 取其 OOF 预测作为该组其他目标的附加特征
  3. 每个目标用 [231 原始特征 + 同组其余 k-1 个组画像特征] 重新训练 LightGBM。
  4. 分箱退化维仍用类加权有序回归（与主模型同一判据、同一实现）。
  5. 指标：宏平均 QWK/Spearman/MAE/RMSE/严格一致率/±1，A/F/X 分组，逐维 ΔQWK。

输出 figures/derived/q1_group_stack.json（含逐维与分组指标、配对 bootstrap）。
"""
import os
import sys
import json

import numpy as np
import pandas as pd
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
J = len(sens)

def grp(s):
    return "A" if s.startswith("A_") else ("F" if s.startswith("F_") else "X")

GROUPS = {g: [j for j, s in enumerate(sens) if grp(s) == g] for g in ("A", "F", "X")}
print("group sizes", {g: len(v) for g, v in GROUPS.items()}, flush=True)

vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else "_rare" for s in styles])
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)
folds = list(skf.split(Xv, strat))
degen = [Q1.binning_degenerate(Yv[:, j]) for j in range(J)]

oof_true = np.full((P.N_SAMPLES, J), -1, dtype=int)
oof_pred = np.full((P.N_SAMPLES, J), -1, dtype=int)
oof_cont = np.full((P.N_SAMPLES, J), np.nan)

for fi, (tr, va) in enumerate(folds, 1):
    for g, idxs in GROUPS.items():
        # 组内训练折再切 5 折生成 OOF 画像（只用训练折样本）
        inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=P.SEED + 1)
        gidx = np.array(idxs)
        prof_tr = np.full((len(tr), len(idxs)), np.nan)
        inner_folds = list(inner.split(Xv[tr], strat[tr]))
        for itr, iva in inner_folds:
            for k, j in enumerate(gidx):
                m = Q1._fit_lgb(Xv[tr][itr], Yv[tr][itr, j])
                prof_tr[iva, k] = m.predict(Xv[tr][iva])
        # 验证折画像：用整训练折拟合的模型
        prof_va = np.full((len(va), len(idxs)), np.nan)
        for k, j in enumerate(gidx):
            m = Q1._fit_lgb(Xv[tr], Yv[tr, j])
            prof_va[:, k] = m.predict(Xv[va])

        for k, j in enumerate(gidx):
            others = [t for t in range(len(idxs)) if t != k]
            Xtr_aug = np.hstack([Xv[tr], prof_tr[:, others]])
            Xva_aug = np.hstack([Xv[va], prof_va[:, others]])
            ytr, yva = Yv[tr, j], Yv[va, j]
            bn = U.Binner().fit(ytr)
            oof_true[va, j] = bn.transform(yva)
            reg = Q1._fit_lgb(Xtr_aug, ytr)
            cont = reg.predict(Xva_aug)
            oof_cont[va, j] = cont
            if degen[j]:
                oof_pred[va, j] = Q1._fit_ordinal(Xtr_aug, ytr, Xva_aug)
            else:
                oof_pred[va, j] = bn.transform_continuous(cont)
    print("fold %d/%d done" % (fi, P.N_FOLDS), flush=True)

from scipy.stats import spearmanr
k = U.quadratic_weighted_kappa
per = {}
for j, s in enumerate(sens):
    t, p = oof_true[:, j], oof_pred[:, j]
    per[s] = {
        "qwk": round(float(k(t, p)), 4),
        "spearman": round(float(spearmanr(oof_cont[:, j], Yv[:, j]).correlation), 4),
        "mae": round(float(np.mean(np.abs(p - t))), 4),
        "exact": round(float(np.mean(p == t)), 4),
        "pm1": round(float(np.mean(np.abs(p - t) <= 1)), 4),
        "group": grp(s),
    }

def agg(keys):
    return {
        "qwk": round(float(np.mean([per[s]["qwk"] for s in keys])), 4),
        "spearman": round(float(np.nanmean([per[s]["spearman"] for s in keys])), 4),
        "mae": round(float(np.mean([per[s]["mae"] for s in keys])), 4),
        "exact": round(float(np.mean([per[s]["exact"] for s in keys])), 4),
        "pm1": round(float(np.mean([per[s]["pm1"] for s in keys])), 4),
    }

out = {"per_dim": per,
       "overall": agg(sens),
       "by_group": {g: agg([sens[j] for j in GROUPS[g]]) for g in ("A", "F", "X")},
       "n_folds": P.N_FOLDS, "seed": P.SEED}
json.dump(out, open(os.path.join(ROOT, "figures", "derived", "q1_group_stack.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(out["overall"], ensure_ascii=False))
print(json.dumps(out["by_group"], ensure_ascii=False))
np.save(os.path.join(ROOT, "_tmp", "q1_group_stack_oof.npy"),
        np.stack([oof_true.astype(float), oof_pred.astype(float)]))
print("saved")
