# -*- coding: utf-8 -*-
"""fig_q3_ridge_latent -- 分布形状与隐空间位置合于一张图

(a) 四个代表化合物在三个风格下的真实/生成分布（山脊图）；
(b) 三风格隐空间的 PCA 散点（实心=真实，星号=生成）。

一张图回答两个互补的问题：生成谱在具体化合物上"形状像不像"，
以及生成样本在隐空间里"落在不在对应风格簇里"。
Data: user_data/1.csv、submission/q3_generated_profiles.csv、
      figures/derived/q3_latent_pack.npz
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Patch
from matplotlib.lines import Line2D
from scipy.stats import gaussian_kde
from _figbase import ROOT, save_fig, tag_panels

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.4,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

real = pd.read_csv(os.path.join(ROOT, "user_data", "1.csv"))
gen = pd.read_csv(os.path.join(ROOT, "submission", "q3_generated_profiles.csv"))
META = {"beer", "beer_id", "tasting_category_fine"}
STYLES = ["Tripel", "Kriek", "Lambic"]
COMPS = [("ethanol..v.v.", "乙醇"), ("DMS", "DMS"),
         ("ethyl_octanoate", "辛酸乙酯"), ("alpha.humulene", "α-葎草烯")]

fig = plt.figure(figsize=(7.3, 3.55))
ax = fig.add_axes([0.215, 0.165, 0.330, 0.800])
axB = fig.add_axes([0.655, 0.165, 0.320, 0.800])

# ---------- (a) 山脊图 ----------
rows = []
for si, st in enumerate(STYLES):
    for ci, (col, lab) in enumerate(COMPS):
        rows.append((si * len(COMPS) + ci, st, col, lab))
nrow = len(rows)
for k, st, col, lab in rows:
    a = pd.to_numeric(real[real["tasting_category_fine"] == st][col], errors="coerce").dropna().values
    b = pd.to_numeric(gen[(gen["style"] == st) & (gen["sample_type"] == "generated")][col],
                      errors="coerce").dropna().values
    if a.size < 5 or b.size < 5:
        continue
    lo, hi = np.percentile(np.concatenate([a, b]), [1, 99])
    xx = np.linspace(lo, hi, 200)
    ka = gaussian_kde(a, bw_method=0.45)(xx)
    kb = gaussian_kde(b, bw_method=0.45)(xx)
    ka = ka / ka.max() * 0.85
    kb = kb / kb.max() * 0.85
    y0 = nrow - k
    ax.fill_between(xx, y0, y0 + ka, color=GREY, alpha=0.35, lw=0, zorder=2)
    ax.plot(xx, y0 + ka, color=GREY, lw=0.9, zorder=3)
    ax.fill_between(xx, y0, y0 + kb, color=CATEGORICAL[STYLES.index(st)], alpha=0.45, lw=0, zorder=4)
    ax.plot(xx, y0 + kb, color=CATEGORICAL[STYLES.index(st)], lw=0.9, zorder=5)

ax.set_yticks([nrow - k for k, *_ in rows])
ax.set_yticklabels(["%s · %s" % (lab, st) for k, st, col, lab in rows], fontsize=5.9)
ax.tick_params(axis="y", length=0, pad=2)
ax.set_ylim(0.4, nrow + 1.1)
ax.set_xlabel("化合物取值（原生数值空间）")
ax.grid(axis="x", color="#F5F5F5", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.legend(handles=[Patch(facecolor=GREY, alpha=0.35, label="真实谱"),
                   Patch(facecolor=CATEGORICAL[0], alpha=0.45, label="生成谱")],
          loc="upper right", handlelength=0.9, borderaxespad=0.3)

# ---------- (b) 隐空间 PCA ----------
pack = np.load(os.path.join(ROOT, "figures", "derived", "q3_latent_pack.npz"), allow_pickle=True)
Zr, Zg = pack["Zr"], pack["Zg"]
rs = pack["real_style"].astype(str)
gsty = pack["gen_style"].astype(str)
mu = Zr.mean(0)
_, S_, Vt = np.linalg.svd(Zr - mu, full_matrices=False)
ratio = (S_ ** 2) / np.sum(S_ ** 2)
Pr = (Zr - mu) @ Vt[:2].T
Pg = (Zg - mu) @ Vt[:2].T

for s in STYLES:
    m = rs == s
    c = CATEGORICAL[STYLES.index(s)]
    axB.scatter(Pr[m, 0], Pr[m, 1], s=11, color=c, alpha=0.50, edgecolor="white",
                linewidth=0.3, zorder=3)
    xy = Pr[m]
    vals, vecs = np.linalg.eigh(np.cov(xy.T))
    o = vals.argsort()[::-1]
    vals, vecs = vals[o], vecs[:, o]
    ang = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    w, h = 2 * 2.447 * np.sqrt(np.maximum(vals, 0))
    axB.add_patch(Ellipse(xy.mean(0), w, h, angle=ang, fill=False,
                          edgecolor=c, lw=0.9, ls=(0, (3, 2)), alpha=0.85, zorder=2))
    mg = gsty == s
    axB.scatter(Pg[mg, 0], Pg[mg, 1], s=26, marker="*", color=c,
                edgecolor="white", linewidth=0.35, alpha=0.95, zorder=6)

axB.set_xlabel("隐空间 PC1（%.1f%%）" % (100 * ratio[0]))
axB.set_ylabel("隐空间 PC2（%.1f%%）" % (100 * ratio[1]))
axB.grid(color="#F5F5F5", lw=0.4, zorder=0)
axB.set_axisbelow(True)
handles = [Line2D([], [], marker="o", ls="", color=CATEGORICAL[STYLES.index(s)], ms=4.5, label=s)
           for s in STYLES]
handles.append(Line2D([], [], marker="*", ls="", markerfacecolor=GREY,
                      markeredgecolor="white", ms=7, label="生成样本"))
axB.legend(handles=handles, loc="upper right", ncol=2, handletextpad=0.3,
           columnspacing=0.7, labelspacing=0.22, borderaxespad=0.2)

tag_panels([ax, axB])
save_fig(fig, "figures/fig_q3_ridge_latent.png")
print("saved; ridge rows=%d, PC1=%.1f%% PC2=%.1f%%" % (nrow, 100 * ratio[0], 100 * ratio[1]))
