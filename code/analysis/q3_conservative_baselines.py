# -*- coding: utf-8 -*-
"""三条保守生成基线与 CVAE 的同协议对照（仅实验，不改论文）。"""
import os, sys, json
sys.path.insert(0, "code")
import numpy as np, pandas as pd
from scipy.stats import ks_2samp, spearmanr, wasserstein_distance
from scipy.stats import norm
from sklearn.model_selection import StratifiedKFold
from sklearn.covariance import LedoitWolf
import joblib
import params as P, utils as U

ROOT = os.getcwd()
U.set_all_seeds(P.SEED)

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, "user_data"))
styles = np.asarray(meta[P.STYLE_COL].values)
Xv = np.asarray(X.values, float)
GEN = ["Tripel", "Kriek", "Lambic"]

bundle = joblib.load(U.ckpt_path("q1_models.pkl"))
q1m, q1b = bundle["models"], bundle["binners"]
sens_cols = list(q1b.keys())

def score(Xn):
    o = np.zeros((Xn.shape[0], len(sens_cols)))
    for j, c in enumerate(sens_cols):
        o[:, j] = q1b[c].transform_continuous(q1m[c].predict(Xn))
    return o

def energy_1d(a, b):
    a = np.asarray(a, float); b = np.asarray(b, float)
    a = a[np.isfinite(a)]; b = b[np.isfinite(b)]
    if a.size < 5 or b.size < 5:
        return np.nan
    return float(np.sqrt(max(2*np.abs(a[:,None]-b[None,:]).mean()
                             - np.abs(a[:,None]-a[None,:]).mean()
                             - np.abs(b[:,None]-b[None,:]).mean(), 0.0)))

def metrics(real, gen, lo, hi):
    ks, en, w1, inr = [], [], [], []
    for k in range(real.shape[1]):
        a = real[:, k][np.isfinite(real[:, k])]
        b = gen[:, k][np.isfinite(gen[:, k])]
        if a.size < 3 or b.size < 3:
            continue
        ks.append(ks_2samp(a, b).statistic)
        w1.append(wasserstein_distance(a, b))
        sd = np.std(a)
        if sd > 1e-3:
            e = energy_1d((a-a.mean())/sd, (b-a.mean())/sd)
            if np.isfinite(e): en.append(e)
        inr.append(float(np.mean((gen[:, k] >= lo[k]) & (gen[:, k] <= hi[k]))))
    return {"ks": float(np.mean(ks)) if ks else np.nan,
            "energy": float(np.median(en)) if en else np.nan,
            "w1": float(np.median(w1)) if w1 else np.nan,
            "in_range": float(np.mean(inr)) if inr else np.nan}

# ---------------- 三条生成器 ----------------
def gen_gaussian_shrink(reals, n, rng, k_pca=12):
    """风格内高斯，但先在 PCA 潜空间（k 维）估计，再用 Ledoit-Wolf 收缩。

    直接在 231 维上估协方差时样本数仅 10-28，协方差必然奇异；
    这条基线正是为检验"高斯族差是因为没正则化还是因为高斯假设本身"。
    """
    N, Pn = reals.shape
    mu = reals.mean(0)
    Zc = reals - mu
    Uu, Ss, Vt = np.linalg.svd(Zc, full_matrices=False)
    k = int(min(k_pca, Pn, N - 1))
    Y = Zc @ Vt[:k].T
    lw = LedoitWolf().fit(Y)
    Ynew = rng.multivariate_normal(np.zeros(k), lw.covariance_, size=n)
    return Ynew @ Vt[:k] + mu

def gen_copula(reals, n, rng, k_pca=8):
    """高斯 Copula：经验边缘 + 潜变量 PCA 截断 + LW 收缩。"""
    N, Pn = reals.shape
    U = np.zeros_like(reals)
    for k in range(Pn):
        r = pd.Series(reals[:, k]).rank(method="average").values
        U[:, k] = (r - 0.5) / N
    Z = norm.ppf(np.clip(U, 1e-4, 1-1e-4))
    mu = Z.mean(0)
    Zc = Z - mu
    # PCA 截断
    Uu, Ss, Vt = np.linalg.svd(Zc, full_matrices=False)
    k = int(min(k_pca, Zc.shape[1], Zc.shape[0]-1))
    Y = Zc @ Vt[:k].T                       # N x k
    lw = LedoitWolf().fit(Y)
    Ynew = rng.multivariate_normal(np.zeros(k), lw.covariance_, size=n)
    Znew = Ynew @ Vt[:k] + mu
    # 回到均匀再按经验分位逆变换
    Unew = norm.cdf(Znew)
    out = np.zeros((n, Pn))
    for kk in range(Pn):
        out[:, kk] = np.quantile(reals[:, kk], np.clip(Unew[:, kk], 0, 1))
    return out

def gen_local_convex(reals, n, rng, k=3):
    N = reals.shape[0]
    out = np.zeros((n, reals.shape[1]))
    mu = reals.mean(0); sd = reals.std(0) + 1e-9
    Zs = (reals - mu) / sd
    for i in range(n):
        anchor = Zs[rng.integers(0, N)]
        d = np.linalg.norm(Zs - anchor, axis=1)
        nn = np.argsort(d)[:min(k, N)]
        w = rng.dirichlet(np.ones(len(nn)))
        out[i] = (reals[nn] * w[:, None]).sum(0)
    return out

# ---------------- 留出协议 ----------------
def style_folds():
    out = []
    for st in GEN:
        idx = np.where(styles == st)[0]
        n = len(idx)
        if n < 10: continue
        k = 5 if n >= 25 else 2
        k = min(k, max(2, n // 5))
        skf = StratifiedKFold(n_splits=k, shuffle=True, random_state=P.SEED)
        for fi, (itr, iva) in enumerate(skf.split(idx, np.zeros(n)), 1):
            test = idx[iva]
            train = np.setdiff1d(np.arange(len(Xv)), test)
            out.append((st, fi, k, train, test))
    return out

folds = style_folds()
print("folds:", [(s, f, k, len(te)) for s, f, k, _, te in folds], flush=True)

rows = []
for fi, (st, sub_fi, k_style, tr, va) in enumerate(folds, 1):
    Xtr, Xva = Xv[tr], Xv[va]
    mtr = styles[tr] == st
    mva = styles[va] == st
    if mtr.sum() < 3 or mva.sum() < 3:
        continue
    reals_raw = Xtr[mtr]
    med_tr = np.nanmedian(Xtr, axis=0)
    reals = np.where(np.isnan(reals_raw), med_tr, reals_raw)
    real_hold = Xva[mva]
    lo, hi = np.nanmin(Xtr, axis=0), np.nanmax(Xtr, axis=0)
    rng = np.random.default_rng(P.SEED + fi)
    rp = score(real_hold).mean(0)

    gens = {}
    try:
        gens["gaussian_shrink"] = np.clip(gen_gaussian_shrink(reals, 30, rng), lo, hi)
    except Exception as e:
        print("gauss fail", e)
    try:
        gens["copula"] = np.clip(gen_copula(reals, 30, rng), lo, hi)
    except Exception as e:
        print("copula fail", e)
    try:
        gens["local_convex"] = np.clip(gen_local_convex(reals, 30, rng), lo, hi)
    except Exception as e:
        print("lconv fail", e)

    for name, G in gens.items():
        m = metrics(real_hold, G, lo, hi)
        gp = score(G).mean(0)
        m.update({"fold": sub_fi, "n_folds_style": k_style, "n_holdout": int(mva.sum()),
                  "style": st, "method": name,
                  "profile_mae": float(np.mean(np.abs(rp - gp))),
                  "profile_spearman": float(spearmanr(rp, gp).correlation)})
        rows.append(m)
    print("[%s fold %d/%d] done" % (st, sub_fi, k_style), flush=True)

df = pd.DataFrame(rows)
df.to_csv(os.path.join(ROOT, "figures", "derived", "q3_conservative_baselines.csv"),
          index=False, encoding="utf-8-sig")

print()
summary = {}
for meth, sub in df.groupby("method"):
    summary[meth] = {k: round(float(sub[k].mean()), 4) for k in
                     ("ks", "w1", "energy", "profile_mae", "profile_spearman", "in_range")}
    print("%-18s KS %.3f  W1 %.3f  energy %.3f  profRho %.3f  inRange %.3f" % (
        meth, summary[meth]["ks"], summary[meth]["w1"], summary[meth]["energy"],
        summary[meth]["profile_spearman"], summary[meth]["in_range"]))
json.dump(summary, open(os.path.join(ROOT, "figures", "derived",
          "q3_conservative_baselines.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nsaved")
