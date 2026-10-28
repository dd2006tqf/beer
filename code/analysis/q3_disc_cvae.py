# -*- coding: utf-8 -*-
"""D2a：给 CVAE 加风格判别辅助损失，检验隐空间是否恢复风格结构。

对照：λ=0（现有 CVAE）vs λ∈{0.1,0.3,0.5}。
每档训练一个模型，报告：
  - 隐空间质心置换检验 p（三风格，999 次）
  - 隐空间风格线性分类准确率（5 折 OOF）
  - 生成谱 KS（分风格均值 + 三风格均值）
  - 生成谱风格 Top-3 识别率、画像 Spearman、能量距离
  - 重构 MSE（防止判别损失压垮重构）

用法：python code/analysis/q3_disc_cvae.py --lam 0.3
输出：figures/derived/q3_disc_lambda_{lam}.json
"""
import argparse
import copy
import json
import os
import sys

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from scipy.stats import ks_2samp, spearmanr
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
import params as P
import utils as U
import problem3 as Q3

ap = argparse.ArgumentParser()
ap.add_argument("--lam", type=float, default=0.3)
ap.add_argument("--epochs", type=int, default=P.CVAE_EPOCHS)
ap.add_argument("--seed", type=int, default=P.SEED)
args = ap.parse_args()

SEED = args.seed
U.set_all_seeds(SEED)
torch.manual_seed(SEED)

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, "user_data"))
styles = meta[P.STYLE_COL].values
Xv = np.asarray(X.values, dtype=float)
mask = (~np.isnan(Xv)).astype(float)
col_med = np.nanmedian(Xv, axis=0)
Xfill = np.where(np.isnan(Xv), col_med, Xv)
mu_f, sd_f = Xfill.mean(0), Xfill.std(0) + 1e-8
Xstd = (Xfill - mu_f) / sd_f
style_list = sorted(pd.unique(styles).tolist())
s2i = {s: i for i, s in enumerate(style_list)}
S = len(style_list)
onehot = np.eye(S)[[s2i[s] for s in styles]]
y_style = np.array([s2i[s] for s in styles])
dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class CVAEwithCls(Q3.CVAE):
    def __init__(self, n_feat, n_style, latent=P.LATENT_DIM, hidden=128):
        super().__init__(n_feat, n_style, latent, hidden)
        self.cls = nn.Linear(latent, n_style)

    def forward(self, x, s):
        mu, logvar = self.encode(x, s)
        z = self.reparameterize(mu, logvar)
        return self.decode(z, s), mu, logvar, z, self.cls(z)


def train(lam, epochs):
    model = CVAEwithCls(Xstd.shape[1], S).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=P.CVAE_LR)
    Xt = torch.tensor(Xstd, dtype=torch.float32, device=dev)
    Mt = torch.tensor(mask, dtype=torch.float32, device=dev)
    St = torch.tensor(onehot, dtype=torch.float32, device=dev)
    Yt = torch.tensor(y_style, dtype=torch.long, device=dev)
    ce = nn.CrossEntropyLoss()
    N = Xt.shape[0]
    rng = np.random.default_rng(SEED)
    best, best_state, bad, patience = 1e18, None, 0, 60
    for ep in range(1, epochs + 1):
        model.train()
        perm = rng.permutation(N)
        tot = 0.0
        for st in range(0, N, P.CVAE_BATCH):
            b = perm[st:st + P.CVAE_BATCH]
            opt.zero_grad()
            xhat, mu, lv, z, logits = model(Xt[b], St[b])
            beta = P.BETA_KL * min(1.0, ep / max(1, P.KL_ANNEAL_EPOCHS))
            loss, rec, kl = Q3._elbo_loss(xhat, Xt[b], Mt[b], mu, lv, beta)
            loss = loss + lam * ce(logits, Yt[b])
            loss.backward()
            opt.step()
            tot += loss.item() * len(b)
        tot /= N
        if ep <= P.KL_ANNEAL_EPOCHS:
            continue
        if tot < best - 1e-4:
            best, best_state, bad = tot, {k: v.detach().clone() for k, v in model.state_dict().items()}, 0
        else:
            bad += 1
        if bad >= patience:
            print("[lam %.1f] early stop @ %d" % (lam, ep), flush=True)
            break
        if ep % 100 == 0:
            print("[lam %.1f] ep %d loss %.4f" % (lam, ep, tot), flush=True)
    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model


def encode_all(model):
    with torch.no_grad():
        mu, _ = model.encode(torch.tensor(Xstd, dtype=torch.float32, device=dev),
                             torch.tensor(onehot, dtype=torch.float32, device=dev))
    return mu.cpu().numpy()


def perm_test(Z, y, n_perm=999, seed=None):
    rng = np.random.default_rng(SEED if seed is None else seed)
    def stat(zz, yy):
        cs = [zz[yy == c].mean(0) for c in np.unique(yy)]
        d = []
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                d.append(np.linalg.norm(cs[i] - cs[j]))
        return float(np.median(d))
    obs = stat(Z, y)
    null = np.array([stat(Z, rng.permutation(y)) for _ in range(n_perm)])
    return float(obs), float((null >= obs).mean())


def lin_acc(Z, y):
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    acc = []
    for tr, va in skf.split(Z, y):
        clf = LogisticRegression(max_iter=2000).fit(Z[tr], y[tr])
        acc.append(clf.score(Z[va], y[va]))
    return float(np.mean(acc))


def energy_1d(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[np.isfinite(a)], b[np.isfinite(b)]
    if a.size < 5 or b.size < 5:
        return np.nan
    return float(np.sqrt(max(2 * np.abs(a[:, None] - b[None, :]).mean()
                             - np.abs(a[:, None] - a[None, :]).mean()
                             - np.abs(b[:, None] - b[None, :]).mean(), 0.0)))


model = train(args.lam, args.epochs)
Z = encode_all(model)
obs, pval = perm_test(Z, y_style)
acc = lin_acc(Z, y_style)
print("[lam %.1f] centroid dist %.3f  perm p=%.4f  lin acc=%.3f" % (args.lam, obs, pval, acc), flush=True)

# 生成 + 指标
lo, hi = np.nanmin(Xv, axis=0), np.nanmax(Xv, axis=0)
import problem3 as Q3mod
_orig_seed = P.SEED
P.SEED = SEED
gen_records, gen_native = Q3._generate(model, style_list, s2i, S, Xstd, styles,
                                       mu_f, sd_f, dev, lo=lo, hi=hi)
P.SEED = _orig_seed
GEN = ["Tripel", "Kriek", "Lambic"]
per = {}
for st in GEN:
    idx = [i for i, r in enumerate(gen_records) if r["style"] == st]
    G = gen_native[idx]
    R = Xv[styles == st]
    ks, en = [], []
    for kk in range(Xv.shape[1]):
        a = R[:, kk][np.isfinite(R[:, kk])]
        bb = G[:, kk][np.isfinite(G[:, kk])]
        if a.size < 5 or bb.size < 5:
            continue
        ks.append(ks_2samp(a, bb).statistic)
        sdd = np.std(a)
        if sdd > 1e-3:
            e = energy_1d((a - a.mean()) / sdd, (bb - a.mean()) / sdd)
            if np.isfinite(e):
                en.append(e)
    per[st] = {"ks_mean": round(float(np.mean(ks)), 4),
               "energy_median": round(float(np.median(en)), 4)}
    print("[lam %.1f] %-7s KS=%.4f" % (args.lam, st, per[st]["ks_mean"]), flush=True)

clf = LogisticRegression(max_iter=2000).fit(Xstd, y_style)
hits = []
for st in GEN:
    idx = [i for i, r in enumerate(gen_records) if r["style"] == st]
    g = (gen_native[idx] - mu_f) / sd_f
    top3 = clf.classes_[np.argsort(-clf.predict_proba(g), axis=1)[:, :3]]
    hits.append(float(np.mean([s2i[st] in row for row in top3])))

# 画像
import joblib
bundle = joblib.load(U.ckpt_path("q1_models.pkl"))
models_, binners_ = bundle["models"], bundle["binners"]
sens_cols = list(binners_.keys())

def score(Xn):
    o = np.zeros((Xn.shape[0], len(sens_cols)))
    for jj, c in enumerate(sens_cols):
        o[:, jj] = binners_[c].transform_continuous(models_[c].predict(Xn))
    return o

prof = {}
for st in GEN:
    idx = [i for i, r in enumerate(gen_records) if r["style"] == st]
    rp = score(Xv[styles == st]).mean(0)
    gp = score(gen_native[idx]).mean(0)
    prof[st] = {"mae": round(float(np.mean(np.abs(rp - gp))), 4),
                "spearman": round(float(spearmanr(rp, gp).correlation), 4)}

with torch.no_grad():
    xh, mu_, lv_, z_, _ = model(torch.tensor(Xstd, dtype=torch.float32, device=dev),
                                torch.tensor(onehot, dtype=torch.float32, device=dev))
recon_mse = float((((xh - torch.tensor(Xstd, dtype=torch.float32, device=dev)) ** 2)
                   * torch.tensor(mask, dtype=torch.float32, device=dev)).sum()
                  / torch.tensor(mask, dtype=torch.float32, device=dev).sum())

out = {"lam": args.lam, "epochs": args.epochs, "seed": SEED,
       "latent": {"centroid_dist": round(obs, 4), "perm_p": round(pval, 4),
                  "lin_acc": round(acc, 3), "chance": round(1.0 / S, 4)},
       "gen": per,
       "ks_mean_3style": round(float(np.mean([per[s]["ks_mean"] for s in GEN])), 4),
       "top3_acc": dict(zip(GEN, hits)),
       "profile": prof,
       "recon_mse": round(recon_mse, 5)}
p = os.path.join(ROOT, "figures", "derived", "q3_disc_lambda_%s_seed%d.json" % (str(args.lam).replace(".", "p"), SEED))
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
print("saved", p)
