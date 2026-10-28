# -*- coding: utf-8 -*-
"""fig_q3_latent -- 隐空间：条件把"平均位置"分开了，但单样本仍然重叠

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) latent PCA, 3 representative styles, real (ellipse) + generated (star) -> assets/figures/PCA -> param inherit
(b) centroid separation vs permutation null -> assets/figures/GroupedViolin (cross-type) -> param inherit

这张图是对现有论述的一次检验，结论必须照实写：
三个代表风格在隐空间里的质心确实互不重合（两两距离 0.52-0.78），
但把风格标签随机打乱后，重新分出的两组质心间距中位反而更大（1.04-1.31），
置换检验 p = 0.92 / 0.99 / 1.00。也就是说，16 维隐空间里没有超出噪声的风格结构，
逐样本层面更是如此：生成样本里只有约三成离"本风格质心"比离最近的异风格质心更近。
这与化学谱 PCA（图 23）能清楚分开并不矛盾——判别信息在 231 维里，
而 CVAE 为了重建 231 列，把风格条件压缩成了很小的偏移。迁移正是靠这个小的质心平移
实现的，所以缺陷约束才成为必要的一步。这一发现已写进正文，属于如实报告的局限。
Data: _tmp/q3_latent_pack.npz、_tmp/q3_latent_snr.json。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D
from _figbase import ROOT, save_fig

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

pack = np.load(os.path.join(ROOT, "figures", "derived", "q3_latent_pack.npz"), allow_pickle=True)
Zr, Zg = pack["Zr"], pack["Zg"]
rs = pack["real_style"].astype(str); gsty = pack["gen_style"].astype(str)
snr = json.load(open(os.path.join(ROOT, "figures", "derived", "q3_latent_centroid_permtest.json"), encoding="utf-8"))

STY = ["Tripel", "Kriek", "Lambic"]
cols = {s: CATEGORICAL[i] for i, s in enumerate(STY)}

mu = Zr.mean(0)
_, S_, Vt = np.linalg.svd(Zr - mu, full_matrices=False)
ratio = (S_ ** 2) / np.sum(S_ ** 2)
Pr = (Zr - mu) @ Vt[:2].T
Pg = (Zg - mu) @ Vt[:2].T
cent = {s: Zr[rs == s].mean(0) for s in STY}

fig = plt.figure(figsize=(7.0, 3.35))
grid = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.26,
                        left=0.072, right=0.975, top=0.885, bottom=0.19)
ax = fig.add_subplot(grid[0, 0])
axB = fig.add_subplot(grid[0, 1])

for s in STY:
    m = rs == s
    c = cols[s]
    ax.scatter(Pr[m, 0], Pr[m, 1], s=13, color=c, alpha=0.50, edgecolor="white",
               linewidth=0.3, zorder=3)
    xy = Pr[m]
    vals, vecs = np.linalg.eigh(np.cov(xy.T))
    o = vals.argsort()[::-1]; vals, vecs = vals[o], vecs[:, o]
    ang = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))
    w, h = 2 * 2.447 * np.sqrt(np.maximum(vals, 0))
    ax.add_patch(Ellipse(xy.mean(0), w, h, angle=ang, fill=False,
                         edgecolor=c, lw=0.9, ls=(0, (3, 2)), alpha=0.85, zorder=2))
    mg = gsty == s
    ax.scatter(Pg[mg, 0], Pg[mg, 1], s=30, marker="*", color=c,
               edgecolor="white", linewidth=0.35, alpha=0.95, zorder=6)

ax.set_xlabel("隐空间 PC1（%.1f%%）" % (100 * ratio[0]))
ax.set_ylabel("隐空间 PC2（%.1f%%）" % (100 * ratio[1]))
ax.grid(color="#F5F5F5", lw=0.4, zorder=0)
ax.set_axisbelow(True)
handles = [Line2D([], [], marker="o", ls="", color=cols[s], ms=4.5, label=s) for s in STY]
handles.append(Line2D([], [], marker="*", ls="", markerfacecolor=GREY,
                      markeredgecolor="white", ms=8, label="生成样本"))
ax.legend(handles=handles, loc="upper right", ncol=2, handletextpad=0.3,
          columnspacing=0.8, labelspacing=0.22, borderaxespad=0.2)

# ---------- (b) 质心分离 vs 置换零分布 ----------
axB.axhline(0, color="#CCCCCC", lw=0.7, zorder=1)
xs = np.arange(len(snr))
for i, r in enumerate(snr):
    d, nmed, p = r["d"], r["null_med"], r["p"]
    axB.plot([i, i], [nmed, d], color=GREY, lw=0.8, ls=(0, (2, 2)), zorder=2)
    axB.scatter(i - 0.10, nmed, s=34, marker="s", color=GREY, alpha=0.85,
                edgecolor="white", linewidth=0.5, zorder=4)
    axB.scatter(i + 0.10, d, s=34, color=CATEGORICAL[0], edgecolor="white",
                linewidth=0.5, zorder=4)
    axB.text(i, d + 0.06, "p=%.2f" % p, ha="center", fontsize=6.2, color=CATEGORICAL[1])
axB.set_xticks(xs)
axB.set_xticklabels([r["pair"].replace("-", "\n") for r in snr], fontsize=6.2)
axB.set_ylabel("两风格质心的隐空间距离")
axB.set_ylim(0, 1.75)
axB.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.legend(handles=[
    Line2D([], [], marker="o", ls="", color=CATEGORICAL[0], ms=5, label="实测"),
    Line2D([], [], marker="s", ls="", color=GREY, ms=5, label="标签打乱后中位"),
], loc="upper left", handletextpad=0.3, labelspacing=0.22, borderaxespad=0.3)

for ax_, tag in ((ax, "(a)"), (axB, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.026, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

fig.savefig(os.path.join(ROOT, "figures", "fig_q3_latent.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; PC1=%.1f%% PC2=%.1f%%" % (100 * ratio[0], 100 * ratio[1]))
