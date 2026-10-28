
"""Q1-5 预测区间（两种口径）：
   (A) LightGBM quantile 0.05/0.95 直接输出
   (B) split-conformal：用训练折内部再切出的校准集残差分位数给区间定宽
报告两者的覆盖率与宽度，说明为什么采用共形校准。
"""
import os, sys, json
import numpy as np
from sklearn.model_selection import StratifiedKFold, train_test_split

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'code'))
import params as P, utils as U
import lightgbm as lgb

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, 'user_data'))
Y, sens = U.load_sensory(os.path.join(ROOT, 'user_data'))
styles = meta[P.STYLE_COL].values
Xv = np.asarray(X.values, dtype=float)
Yv = np.asarray(Y.values, dtype=float)
J = len(sens)
import pandas as pd
vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else '_rare' for s in styles])
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)

PARAMS = dict(n_estimators=150, num_leaves=8, learning_rate=0.05,
              min_child_samples=15, feature_fraction=0.6, bagging_fraction=0.8,
              bagging_freq=1, lambda_l2=1.0, random_state=P.SEED, n_jobs=-1, verbose=-1)

lo_q = np.full((len(Xv), J), np.nan); hi_q = np.full((len(Xv), J), np.nan)
lo_c = np.full((len(Xv), J), np.nan); hi_c = np.full((len(Xv), J), np.nan)
ALPHA = 0.10

for fi, (tr, va) in enumerate(skf.split(Xv, strat), 1):
    tr_fit, tr_cal = train_test_split(tr, test_size=0.30, random_state=P.SEED,
                                      stratify=strat[tr])
    for j in range(J):
        # (A) 直接分位数回归
        for a, store in ((0.05, lo_q), (0.95, hi_q)):
            m = lgb.LGBMRegressor(objective='quantile', alpha=a, **PARAMS)
            m.fit(Xv[tr], Yv[tr, j]); store[va, j] = m.predict(Xv[va])
        # (B) conformal：点模型 + 校准集绝对残差分位
        mp = lgb.LGBMRegressor(**PARAMS).fit(Xv[tr_fit], Yv[tr_fit, j])
        resid = np.abs(Yv[tr_cal, j] - mp.predict(Xv[tr_cal]))
        n = len(resid)
        k = int(np.ceil((n + 1) * (1 - ALPHA))) - 1
        q = float(np.sort(resid)[min(k, n - 1)])
        pred = mp.predict(Xv[va])
        lo_c[va, j] = pred - q; hi_c[va, j] = pred + q
    print('[Q1-5] fold %d/%d' % (fi, P.N_FOLDS), flush=True)

def summarize(lo, hi):
    cov, wid, per = [], [], {}
    for j, col in enumerate(sens):
        y = Yv[:, j]
        c = float(np.mean((y >= lo[:, j]) & (y <= hi[:, j])))
        w = float(np.mean(hi[:, j] - lo[:, j]))
        cov.append(c); wid.append(w)
        per[col] = {'coverage': round(c, 4), 'width': round(w, 4)}
    def grp(d):
        return 'A' if d.startswith('A_') else ('F' if d.startswith('F_') else 'X')
    g = {}
    for k in ('A', 'F', 'X'):
        cs = [per[c]['coverage'] for c in sens if grp(c) == k]
        ws = [per[c]['width'] for c in sens if grp(c) == k]
        g[k] = {'n': len(cs), 'coverage_mean': round(float(np.mean(cs)), 4),
                'width_mean': round(float(np.mean(ws)), 4)}
    return {'overall_coverage': round(float(np.mean(cov)), 4),
            'overall_width': round(float(np.mean(wid)), 4),
            'by_group': g, 'by_dim': per}

out = {
    'target_coverage': 1 - ALPHA,
    'quantile_regression': summarize(lo_q, hi_q),
    'conformal': summarize(lo_c, hi_c),
    'note': ('标签为标准化连续值。分位数回归用 LightGBM objective=quantile(alpha=0.05/0.95)；'
             '共形口径在每个训练折内再切 30% 作校准集，取绝对残差的 ceil((n+1)(1-alpha)) 分位作为半宽。'
             '覆盖率在验证折上统计。'),
}
path = os.path.join(ROOT, 'figures', 'derived', 'q1_prediction_interval.json')
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n分位数回归: 覆盖率 %.4f 宽度 %.4f' % (out['quantile_regression']['overall_coverage'],
                                        out['quantile_regression']['overall_width']))
print('共形校准  : 覆盖率 %.4f 宽度 %.4f' % (out['conformal']['overall_coverage'],
                                        out['conformal']['overall_width']))
print(json.dumps(out['conformal']['by_group'], ensure_ascii=False, indent=1))
