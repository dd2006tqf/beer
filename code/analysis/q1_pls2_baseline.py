# -*- coding: utf-8 -*-
"""对照笔记推荐的 Q1 路线：PLS2（多输出偏最小二乘）在同折同分箱下的 QWK。

不改变主模型，仅用于回答"我们的 LightGBM 逐维回归是否与 PLS2 相当"。
"""
import sys, json
sys.path.insert(0, "code")
import numpy as np, pandas as pd
from sklearn.cross_decomposition import PLSRegression
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold
import params as P, utils as U

df1, X, feat, meta = U.load_chem("user_data")
Y, sens = U.load_sensory("user_data")
Xv = np.asarray(X.values, float); Yv = np.asarray(Y.values, float)
styles = meta[P.STYLE_COL].values
J = len(sens)
vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else "_rare" for s in styles])
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)

k = U.quadratic_weighted_kappa
def run_pls(n_comp):
    oof = np.full((len(Xv), J), -1, dtype=int)
    tru = np.full((len(Xv), J), -1, dtype=int)
    for tr, va in skf.split(Xv, strat):
        med = SimpleImputer(strategy="median").fit(Xv[tr])
        Xtr, Xva = med.transform(Xv[tr]), med.transform(Xv[va])
        mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-9
        Xtr = (Xtr - mu) / sd; Xva = (Xva - mu) / sd
        pls = PLSRegression(n_components=n_comp, scale=False).fit(Xtr, Yv[tr])
        pred = pls.predict(Xva)
        for j in range(J):
            b = U.Binner().fit(Yv[tr, j])
            tru[va, j] = b.transform(Yv[va, j])
            oof[va, j] = b.transform_continuous(pred[:, j])
    return np.mean([k(tru[:, j], oof[:, j]) for j in range(J)])

for n in (5, 10, 15):
    print("PLS2 %2d comps -> QWK %.4f" % (n, run_pls(n)), flush=True)
