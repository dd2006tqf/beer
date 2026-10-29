# -*- coding: utf-8 -*-
"""fig_q3_ks_ridge -- 生成谱偏离的"幅度"与"形状"合于一张图

(a) 代表化合物在三个风格下的真实/生成分布山脊图（原图 26 左子图）；
(b) Tripel 231 列逐列 KS 排序（原图 27 左子图）。

两件事必须一起看才完整：KS 是标量，只回答"偏多少"；山脊图回答"偏在哪一侧、
形状怎么变"。合成一张后，先看右图确认偏离集中在少数稀疏列，再看左图确认这些
列的形状变化，读者不必在两页之间来回对照。
Data: submission/q3_generated_profiles.csv、user_data/1.csv。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, ks_2samp
from matplotlib.patches import Patch
from _figbase import ROOT, save_fig, tag_panels

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

real = pd.read_csv(os.path.join(ROOT, "user_data", "1.csv"))
gen = pd.read_csv(os.path.join(ROOT, "submission", "q3_generated_profiles.csv"))
META = {"beer", "beer_id", "tasting_category_fine"}
feat = [c for c in real.columns if c not in META]

STYLES = ["Tripel", "Kriek", "Lambic"]
COMPS = [("ethanol..v.v.", "乙醇"), ("DMS", "DMS"), ("ethyl_octanoate", "辛酸乙酯"),
         ("alpha.humulene", "α-葎草烯")]

fig = plt.figure(figsize=(7.3, 3.55))
axL = fig.add_axes([0.205, 0.175, 0.345, 0.755])
axR = fig.add_axes([0.640, 0.175, 0.345, 0.755])

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
    axL.fill_between(xx, y0, y0 + ka, color=GREY, alpha=0.35, lw=0, zorder=2)
    axL.plot(xx, y0 + ka, color=GREY, lw=0.9, zorder=3)
    axL.fill_between(xx, y0, y0 + kb, color=CATEGORICAL[STYLES.index(st)],
                     alpha=0.45, lw=0, zorder=4)
    axL.plot(xx, y0 + kb, color=CATEGORICAL[STYLES.index(st)], lw=0.9, zorder=5)

axL.set_yticks([nrow - k for k, *_ in rows])
axL.set_yticklabels(["%s · %s" % (lab, st) for k, st, col, lab in rows], fontsize=5.9)
axL.tick_params(axis="y", length=0, pad=2)
axL.set_ylim(0.4, nrow + 1.1)
axL.set_xlabel("化合物取值（原生数值空间）")
axL.grid(axis="x", color="#F5F5F5", lw=0.4, zorder=0)
axL.set_axisbelow(True)
axL.legend(handles=[Patch(facecolor=GREY, alpha=0.35, label="真实谱"),
                    Patch(facecolor=CATEGORICAL[0], alpha=0.45, label="生成谱")],
           loc="upper right", handlelength=0.9, borderaxespad=0.3)

# ---------- (b) 逐列 KS 排序（Tripel） ----------
GEN = "Tripel"
R = real[real["tasting_category_fine"] == GEN]
G = gen[(gen["style"] == GEN) & (gen["sample_type"] == "generated")]
ks = []
for c in feat:
    a = pd.to_numeric(R[c], errors="coerce").dropna().values
    b = pd.to_numeric(G[c], errors="coerce").dropna().values
    if a.size < 5 or b.size < 5:
        continue
    ks.append(ks_2samp(a, b).statistic)
ks = np.array(ks)
ks_sorted = np.sort(ks)[::-1]
x = np.arange(len(ks_sorted))
axR.bar(x, ks_sorted, width=0.9, color="#CFD9E3", edgecolor="none", zorder=2)
hi = ks_sorted >= 0.5
axR.bar(x[hi], ks_sorted[hi], width=0.9, color=CATEGORICAL[1], edgecolor="none", zorder=3)
axR.axhline(ks.mean(), color="#333333", lw=0.9, ls=(0, (4, 3)), zorder=4)
axR.set_xlim(-1, len(x))
axR.set_ylim(0, 1.0)
axR.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
axR.set_axisbelow(True)
axR.set_xlabel("231 个化合物（按 KS 降序）")
axR.set_ylabel("逐列 KS 距离")
n_hi = int(hi.sum())
axR.text(len(x) * 0.985, ks.mean() + 0.025, "均值 %.3f" % ks.mean(), ha="right",
         fontsize=6.4, color="#333333")

tag_panels([axL, axR])

save_fig(fig, "figures/fig_q3_ks_ridge.png")
print("saved; mean=%.4f hi=%d (%.1f%%)" % (ks.mean(), n_hi, 100 * n_hi / len(x)))
