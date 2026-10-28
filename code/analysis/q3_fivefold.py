# -*- coding: utf-8 -*-
"""D2b：三种生成器的五折留出对照（CVAE / 风格内高斯 / 风格内重采样）。

每折用训练折拟合生成器、留出折作参照分布，每风格生成 30 条；
折上计算：逐列 KS 均值、能量距离中位、W1 中位、画像 Spearman、画像 MAE、区间内比例。
五折汇总 mean±std，并按 Tripel/Kriek/Lambic 拆分。

输出 figures/derived/q3_fivefold.json。
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import torch
from scipy.stats import ks_2samp, spearmanr, wasserstein_distance
from sklearn.model_selection import StratifiedKFold

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
import params as P
import utils as U
import problem3 as Q3

U.set_all_seeds(P.SEED)
torch.manual_seed(P.SEED)

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, "user_data"))
styles = meta[P.STYLE_COL].values
Xv = np.asarray(X.values, dtype=float)
GEN = ["Tripel", "Kriek", "Lambic"]
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")

import joblib
bundle = joblib.load(U.ckpt_path("q1_models.pkl"))
q1_models, q1_binners = bundle["models"], bundle["binners"]
sens_cols = list(q1_binners.keys())

def score(Xn):
    o = np.zeros((Xn.shape[0], len(sens_cols)))
    for j, c in enumerate(sens_cols):
        o[:, j] = q1_binners[c].transform_continuous(q1_models[c].predict(Xn))
    return o

def energy_1d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if a.size < 5 or b.size < 5:
        return np.nan
    return float(np.sqrt(max(2 * np.abs(a[:, None] - b[None, :]).mean()
                             - np.abs(a[:, None] - a[None, :]).mean()
                             - np.abs(b[:, None] - b[None, :]).mean(), 0.0)))

def metrics(real, gen, lo, hi):
    """real/gen: [n, 231] 原生尺度。"""
    ks, en, w1, inr = [], [], [], []
    for k in range(real.shape[1]):
        a = real[:, k][np.isfinite(real[:, k])]
        b = gen[:, k][np.isfinite(gen[:, k])]
        if a.size < 5 or b.size < 5:
            continue
        ks.append(ks_2samp(a, b).statistic)
        w1.append(wasserstein_distance(a, b))
        sd = np.std(a)
        if sd > 1e-3:
            e = energy_1d((a - a.mean()) / sd, (b - a.mean()) / sd)
            if np.isfinite(e):
                en.append(e)
        inr.append(float(np.mean((gen[:, k] >= lo[k]) & (gen[:, k] <= hi[k]))))
    return {"ks": float(np.mean(ks)), "energy": float(np.median(en)),
            "w1": float(np.median(w1)), "in_range": float(np.mean(inr))}

# 按风格自适应折数：保证每折留出样本 >= 5，否则 KS 无法计算
# Tripel(28)->5 折(5~6/折)；Kriek(10)->2 折(5/折)；Lambic(11)->2 折(5~6/折)
def style_folds():
    out = []
    for st in GEN:
        idx = np.where(styles == st)[0]
        n = len(idx)
        if n < 10:
            continue
        k = 5 if n >= 25 else 2
        k = min(k, max(2, n // 5))
        skf_s = StratifiedKFold(n_splits=k, shuffle=True, random_state=P.SEED)
        dummy = np.zeros(n)
        for fi, (itr, iva) in enumerate(skf_s.split(idx, dummy), 1):
            test = idx[iva]
            train = np.setdiff1d(np.arange(len(Xv)), test)
            out.append((st, fi, k, train, test))
    return out

folds = style_folds()
print("fold plan:", [(s, f, k, len(te)) for s, f, k, _, te in folds], flush=True)

rows = []
for fi, (style_name, sub_fi, k_style, tr, va) in enumerate(folds, 1):
    Xtr, Xva = Xv[tr], Xv[va]
    med = np.nanmedian(Xtr, axis=0)
    Xf = np.where(np.isnan(Xtr), med, Xtr)
    mu_f, sd_f = Xf.mean(0), Xf.std(0) + 1e-8
    Xstd = (Xf - mu_f) / sd_f
    mask = (~np.isnan(Xtr)).astype(float)

    sl = sorted(pd.unique(styles[tr]).tolist())
    s2i = {s: i for i, s in enumerate(sl)}
    onehot = np.eye(len(sl))[[s2i[s] for s in styles[tr]]]
    model = Q3._train_cvae(Xstd, mask, onehot, dev)
    lo, hi = np.nanmin(Xtr, axis=0), np.nanmax(Xtr, axis=0)

    rng = np.random.default_rng(P.SEED + fi)
    for st in [style_name]:
        mtr = styles[tr] == st
        mva = styles[va] == st
        if mtr.sum() < 3 or mva.sum() < 3 or st not in s2i:
            continue
        real_hold = Xva[mva]                     # 留出折作参照
        real_tr = Xtr[mtr]

        # --- CVAE ---
        oh = np.zeros((30, len(sl))); oh[:, s2i[st]] = 1
        z = torch.tensor(rng.standard_normal((30, P.LATENT_DIM)).astype("float32"))
        with torch.no_grad():
            xh = model.decode(z, torch.tensor(oh.astype("float32"))).numpy()
        gen_cvae = np.clip(xh * sd_f + mu_f, lo, hi)

        # --- 高斯 ---
        g_med = np.where(np.isnan(real_tr), med, real_tr)
        mu_g, sd_g = g_med.mean(0), g_med.std(0) + 1e-6
        gen_gauss = np.clip(rng.normal(mu_g, sd_g, (30, Xv.shape[1])), lo, hi)

        # --- 重采样 ---
        idxs = rng.integers(0, real_tr.shape[0], 30)
        gen_boot = real_tr[idxs]

        rp = score(real_hold).mean(0)
        for name, G in (("CVAE", gen_cvae), ("Gaussian", gen_gauss), ("Bootstrap", gen_boot)):
            m = metrics(real_hold, G, lo, hi)
            gp = score(G).mean(0)
            m.update({"fold": sub_fi, "n_folds_style": k_style, "n_holdout": int(mva.sum()),
                      "style": st, "method": name,
                      "profile_mae": float(np.mean(np.abs(rp - gp))),
                      "profile_spearman": float(spearmanr(rp, gp).correlation)})
            rows.append(m)
        print("[%s fold %d/%d] done (holdout=%d)" % (st, sub_fi, k_style, mva.sum()), flush=True)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(ROOT, "figures", "derived", "q3_fivefold.csv"), index=False, encoding="utf-8-sig")

summ = {}
for meth, sub in df.groupby("method"):
    per_style = {}
    for st, s2 in sub.groupby("style"):
        per_style[st] = {k: [round(float(s2[k].mean()), 4), round(float(s2[k].std(ddof=1)), 4)]
                         for k in ("ks", "energy", "w1", "in_range", "profile_mae", "profile_spearman")}
    summ[meth] = {
        "overall": {k: [round(float(sub[k].mean()), 4), round(float(sub[k].std(ddof=1)), 4)]
                    for k in ("ks", "energy", "w1", "in_range", "profile_mae", "profile_spearman")},
        "per_style": per_style,
        "n_rows": int(len(sub)),
    }
out = {"seed": P.SEED, "methods": summ,
       "fold_scheme": {st: int(k) for st, _, k, _, _ in folds},
       "note": "按风格分层留出：每折用训练折拟合生成器、留出折作参照，每风格每折生成 30 条。"
               "折数按风格样本量自适应（Tripel 5 折，Kriek/Lambic 2 折），以保证每折留出 >=5 条、"
               "KS 与 W1 可计算；指标为逐列计算后的汇总（KS 取均值，W1 与能量距离取中位）。"}
json.dump(out, open(os.path.join(ROOT, "figures", "derived", "q3_fivefold.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps({m: v["overall"] for m, v in summ.items()}, ensure_ascii=False, indent=1))
