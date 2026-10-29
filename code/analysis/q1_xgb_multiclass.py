# -*- coding: utf-8 -*-
"""对照笔记推荐的 Q1 路线：XGBoost 7 类 softprob 多分类取期望。

与主模型同折、同分箱、同指标；不改变主模型。
"""
import sys, json
sys.path.insert(0, "code")
import numpy as np, pandas as pd
from sklearn.model_selection import StratifiedKFold
import params as P, utils as U

try:
    import xgboost as xgb
except ImportError:
    print("xgboost not installed"); raise SystemExit

df1, X, feat, meta = U.load_chem("user_data")
Y, sens = U.load_sensory("user_data")
Xv = np.asarray(X.values, float); Yv = np.asarray(Y.values, float)
styles = meta[P.STYLE_COL].values
J = len(sens)
vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else "_rare" for s in styles])
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)
folds = list(skf.split(Xv, strat))
k = U.quadratic_weighted_kappa

oof = np.full((len(Xv), J), -1, dtype=int)
tru = np.full((len(Xv), J), -1, dtype=int)
for tr, va in folds:
    for j in range(J):
        b = U.Binner().fit(Yv[tr, j])
        ytr = b.transform(Yv[tr, j]); yva = b.transform(Yv[va, j])
        tru[va, j] = yva
        clf = xgb.XGBClassifier(
            n_estimators=200, max_depth=4, learning_rate=0.08,
            subsample=0.8, colsample_bytree=0.8, reg_lambda=1.0,
            objective="multi:softprob", num_class=7,
            tree_method="hist", random_state=P.SEED, n_jobs=-1,
            verbosity=0)
        clf.fit(Xv[tr], ytr)
        proba = clf.predict_proba(Xv[va])
        oof[va, j] = np.clip(np.round(proba @ np.arange(7)), 0, 6).astype(int)
    print("fold done", flush=True)

q = [k(tru[:, j], oof[:, j]) for j in range(J)]
print("XGBoost 7-class softprob -> QWK %.4f" % np.mean(q))
json.dump({"mean_qwk": round(float(np.mean(q)), 4)},
          open("figures/derived/q1_xgb_multiclass.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
