
"""Q3-2 多 seed 稳定性：同一 CVAE 配置跑 5 个种子，报告 KS / 能量距离 / 识别率 / 画像 MAE 的均值±标准差。"""
import os, sys, json
import numpy as np
import pandas as pd
import torch
from scipy.stats import ks_2samp, spearmanr
from sklearn.linear_model import LogisticRegression

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'code'))
import params as P, utils as U, problem3 as Q3

SEEDS = [42, 7, 2024, 1234, 99]

def energy_1d(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if a.size < 5 or b.size < 5: return np.nan
    d_ab = np.abs(a[:, None] - b[None, :]).mean()
    d_aa = np.abs(a[:, None] - a[None, :]).mean()
    d_bb = np.abs(b[:, None] - b[None, :]).mean()
    return float(np.sqrt(max(2 * d_ab - d_aa - d_bb, 0.0)))

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, 'user_data'))
styles = meta[P.STYLE_COL].values
Xv = np.asarray(X.values, dtype=float)
mask = (~np.isnan(Xv)).astype(float)
col_med = np.nanmedian(Xv, axis=0)
Xfill = np.where(np.isnan(Xv), col_med, Xv)
mu_f, sd_f = Xfill.mean(0), Xfill.std(0) + 1e-8
Xstd = (Xfill - mu_f) / sd_f
style_list = sorted(pd.unique(styles).tolist())
s2i = {s: i for i, s in enumerate(style_list)}
onehot = np.eye(len(style_list))[[s2i[s] for s in styles]]
dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
meta_cols = {'beer', 'beer_id', 'tasting_category_fine'}
cols = [c for c in feat if c not in meta_cols]
STY = P.GEN_STYLES

runs = []
for seed in SEEDS:
    P_seed_backup = P.SEED
    U.set_all_seeds(seed); torch.manual_seed(seed)
    model = Q3._train_cvae(Xstd, mask, onehot, dev)
    model.eval()
    rng = np.random.default_rng(seed)
    rec = {'seed': seed, 'per_style': {}}
    gen_all = {}
    for st in STY:
        oh = np.zeros((100, len(style_list))); oh[:, s2i[st]] = 1.0
        z = torch.tensor(rng.standard_normal((100, P.LATENT_DIM)).astype('float32'))
        with torch.no_grad():
            xh = model.decode(z, torch.tensor(oh.astype('float32'))).numpy()
        xh = xh * sd_f + mu_f
        lo = np.nanmin(Xv, axis=0); hi = np.nanmax(Xv, axis=0)
        xh = np.clip(xh, lo, hi)
        gen_all[st] = xh
        R = Xv[styles == st]
        ks, en = [], []
        for k, c in enumerate(feat):
            a = R[:, k][np.isfinite(R[:, k])]; b = xh[:, k][np.isfinite(xh[:, k])]
            if a.size < 5 or b.size < 5: continue
            ks.append(ks_2samp(a, b).statistic)
            sd = np.std(a)
            if sd > 1e-3:
                e = energy_1d((a - np.mean(a)) / sd, (b - np.mean(a)) / sd)
                if np.isfinite(e): en.append(e)
        rec['per_style'][st] = {'ks_mean': float(np.mean(ks)), 'energy_median': float(np.median(en))}
        print('[seed %d] %-7s KS=%.4f energy=%.4f' % (seed, st, rec['per_style'][st]['ks_mean'],
                                                     rec['per_style'][st]['energy_median']), flush=True)
    # 风格识别率（同一生成谱，用真实谱训分类器）
    Xs = Xstd
    clf = LogisticRegression(max_iter=2000).fit(Xs, styles)
    cls = clf.classes_
    hits = []
    for st in STY:
        g = (gen_all[st] - mu_f) / sd_f
        pr = clf.predict_proba(g)
        top3 = cls[np.argsort(-pr, axis=1)[:, :3]]
        hits.append(float(np.mean([st in row for row in top3])))
    rec['top3_acc'] = dict(zip(STY, hits))
    runs.append(rec)
    print('[seed %d] top3 %s' % (seed, rec['top3_acc']), flush=True)

def agg(vals):
    v = np.asarray(vals, float)
    return {'mean': round(float(v.mean()), 4), 'std': round(float(v.std(ddof=1)), 4),
            'min': round(float(v.min()), 4), 'max': round(float(v.max()), 4)}

out = {'seeds': SEEDS, 'per_style': {}, 'top3_acc': {}}
for st in STY:
    out['per_style'][st] = {
        'ks_mean': agg([r['per_style'][st]['ks_mean'] for r in runs]),
        'energy_median': agg([r['per_style'][st]['energy_median'] for r in runs]),
    }
    out['top3_acc'][st] = agg([r['top3_acc'][st] for r in runs])
out['raw_runs'] = runs
path = os.path.join(ROOT, 'figures', 'derived', 'q3_multiseed.json')
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\n=== 汇总 ===')
print(json.dumps({k: v for k, v in out.items() if k != 'raw_runs'}, ensure_ascii=False, indent=1))
