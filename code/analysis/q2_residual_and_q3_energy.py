
"""Q2-5 残差相关（按名对齐）+ Q3-1 能量距离（稳健口径）/ 画像 MAE。"""
import os, sys, json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'code'))
import params as P, utils as U

out = {}

# ================= Q2-5 残差 Spearman =================
df1, X, feat, meta = U.load_chem('user_data')
Y, sens = U.load_sensory('user_data')
styles = meta[P.STYLE_COL].values
C6, comp_rows, sens6 = U.load_cross_corr('user_data')
Xv = np.asarray(X.values, dtype=float)
Yv = np.asarray(Y.values, dtype=float)
mapped = U.align_sensory_cols(list(C6.columns))   # 6.csv 列 -> 4.csv 短名

Xr = Xv.copy(); Yr = Yv.copy()
for s in np.unique(styles):
    m = styles == s
    if m.sum() < 3: continue
    Xr[m] = Xv[m] - np.nanmean(Xv[m], axis=0)
    Yr[m] = Yv[m] - np.nanmean(Yv[m], axis=0)

# 6.csv 行名 -> 2.csv 行号 -> （按位置）1.csv 列号（与 problem2._corr_evidence 同口径）
R, comp_names = U.load_compound_corr(os.path.join(ROOT, 'user_data'))
name2pos = {n: i for i, n in enumerate(comp_names)}
rows = []
for ri, cname in enumerate(comp_rows):
    if cname not in name2pos: continue
    p = name2pos[cname]
    for k, short in enumerate(mapped):
        if short not in sens: continue
        q = sens.index(short)
        a, b = Xv[:, p], Yv[:, q]
        ok = np.isfinite(a) & np.isfinite(b)
        if ok.sum() <= 10: continue
        r_full = spearmanr(a[ok], b[ok]).correlation
        ar, br = Xr[:, p], Yr[:, q]
        ok2 = np.isfinite(ar) & np.isfinite(br)
        if ok2.sum() <= 10: continue
        r_res = spearmanr(ar[ok2], br[ok2]).correlation
        if np.isfinite(r_full) and np.isfinite(r_res):
            rows.append((cname, short, float(r_full), float(r_res)))

rf = np.array([r[2] for r in rows]); rr = np.array([r[3] for r in rows])
out['q2_residual_corr'] = {
    'n_pairs': len(rows),
    'median_abs_full': round(float(np.median(np.abs(rf))), 4),
    'median_abs_resid': round(float(np.median(np.abs(rr))), 4),
    'corr_full_vs_resid': round(float(np.corrcoef(rf, rr)[0, 1]), 4),
    'sign_agreement': round(float(np.mean(np.sign(rf) == np.sign(rr))), 4),
    'n_abs_full_ge_0.3': int((np.abs(rf) >= 0.3).sum()),
    'n_abs_resid_ge_0.3': int((np.abs(rr) >= 0.3).sum()),
    'top_pairs': [{'compound': c, 'sensory': s, 'r_full': round(a, 4), 'r_resid': round(b, 4)}
                  for c, s, a, b in sorted(rows, key=lambda r: -abs(r[2]))[:10]],
}
print('[Q2-5] n=%d  median|r| full=%.3f resid=%.3f  sign_agree=%.3f  corr=%.3f'
      % (len(rows), out['q2_residual_corr']['median_abs_full'],
         out['q2_residual_corr']['median_abs_resid'],
         out['q2_residual_corr']['sign_agreement'],
         out['q2_residual_corr']['corr_full_vs_resid']), flush=True)

# ================= Q3-1 能量距离 + 画像 MAE =================
real = pd.read_csv(os.path.join(ROOT, 'user_data', '1.csv'))
clip = pd.read_csv(os.path.join(ROOT, 'submission', 'q3_generated_profiles.csv'))
meta_cols = {'beer', 'beer_id', 'tasting_category_fine'}
cols = [c for c in real.columns if c not in meta_cols]
sens_cols = [c for c in clip.columns if c.startswith('SENS_')]

def energy_1d(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if a.size < 5 or b.size < 5: return np.nan
    d_ab = np.abs(a[:, None] - b[None, :]).mean()
    d_aa = np.abs(a[:, None] - a[None, :]).mean()
    d_bb = np.abs(b[:, None] - b[None, :]).mean()
    return float(np.sqrt(max(2 * d_ab - d_aa - d_bb, 0.0)))

STY = ['Tripel', 'Kriek', 'Lambic']
per = []
for s in STY:
    R = real[real['tasting_category_fine'] == s][cols].apply(pd.to_numeric, errors='coerce')
    G = clip[(clip['style'] == s) & (clip['sample_type'] == 'generated')][cols].apply(pd.to_numeric, errors='coerce')
    mu, sd = R.mean(), R.std().replace(0, np.nan)
    vals = []
    for c in cols:
        if not np.isfinite(sd[c]) or sd[c] < 1e-3:
            continue        # 近乎常数的列不参与（避免 1/sd 放大）
        a = ((R[c] - mu[c]) / sd[c]).values
        b = ((G[c] - mu[c]) / sd[c]).values
        e = energy_1d(a, b)
        if np.isfinite(e): vals.append(e)
    per.append({'style': s, 'n_real': int(len(R)), 'n_gen': int(len(G)),
                'n_cols': len(vals),
                'energy_median': round(float(np.median(vals)), 4),
                'energy_mean': round(float(np.mean(vals)), 4)})
    print('[Q3-1] %-7s energy median=%.4f mean=%.4f (n=%d cols)'
          % (s, per[-1]['energy_median'], per[-1]['energy_mean'], len(vals)), flush=True)

import joblib
bundle = joblib.load(U.ckpt_path('q1_models.pkl'))
models, binners = bundle['models'], bundle['binners']
def score(Xn):
    o = np.zeros((Xn.shape[0], len(binners)))
    for j, col in enumerate(binners.keys()):
        if col in models:
            o[:, j] = binners[col].transform_continuous(models[col].predict(Xn))
        else:
            o[:, j] = 3
    return o

Xfull = np.asarray(X.values, dtype=float)
prof = []
for s in STY:
    rp = score(Xfull[styles == s]).mean(axis=0)
    gm = (clip['style'] == s) & (clip['sample_type'] == 'generated')
    gp = clip.loc[gm, sens_cols].values.mean(axis=0)
    prof.append({'style': s, 'n_dims': len(sens_cols),
                 'profile_mae': round(float(np.mean(np.abs(rp - gp))), 4),
                 'profile_spearman': round(float(spearmanr(rp, gp).correlation), 4)})
    print('[Q3-1] %-7s profile MAE=%.4f rho=%.4f' % (s, prof[-1]['profile_mae'], prof[-1]['profile_spearman']), flush=True)

for r in per:
    for q in prof:
        if q['style'] == r['style']:
            r.update({k: q[k] for k in ('profile_mae', 'profile_spearman', 'n_dims')})

out['q3_energy_profile'] = {
    'per_style': per,
    'mean_energy_median': round(float(np.mean([r['energy_median'] for r in per])), 4),
    'mean_profile_mae': round(float(np.mean([r['profile_mae'] for r in per])), 4),
    'mean_profile_spearman': round(float(np.mean([r['profile_spearman'] for r in per])), 4),
    'note': ('能量距离为逐列一维口径（按真实谱均值方差标准化，剔除方差<1e-3的近常数列），'
             '报中位为主；画像 MAE 为 50 维 0-6 等级的均值绝对差。'),
}
path = os.path.join(ROOT, 'figures', 'derived', 'q2q3_extra_metrics.json')
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nsaved', path)
print(json.dumps(out['q3_energy_profile'], ensure_ascii=False, indent=1)[:600])
