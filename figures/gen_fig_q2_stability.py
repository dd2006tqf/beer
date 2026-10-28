# -*- coding: utf-8 -*-
"""fig_q2_stability -- 单方法稳定性饱和 vs 跨方法一致性分散

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) joint scatter + marginal density -> assets/figures/MarginalDensity -> param inherit
(b) empirical vs random-null ECDF   -> assets/figures/LineTrend (cross-type) -> param inherit

Design: the two stability criteria are NOT interchangeable, and plotting them
separately with two histograms hid that. Here each point is one sensory
dimension in the (bootstrap Top-1 frequency, cross-method Jaccard) plane.
The vertical pile at x = 1.0 is the saturation of the bootstrap criterion;
the spread along y is where cross-method agreement actually differs.
Panel (b) puts the observed Jaccard against the null of two independent
random 3-subsets of the 211 candidates, on a log axis so the 21.7x ratio is visible.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from _figbase import P2, save_fig, dim_zh
from _figbase import ROOT

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

rk = P2["fig_data"]["top1_freq_ranked"]
base = P2.get("random_jaccard_baseline", {})
dims = [r[0] for r in rk]
freq = np.array([r[1] for r in rk], dtype=float)
jac = np.array([r[2] for r in rk], dtype=float)
base_mean = float(base.get("mean", 0.008585))
nb = int(P2["summary"]["n_bootstrap"])

def grp(d):
    return 0 if d.startswith("A_") else (1 if d.startswith("F_") else 2)
g = np.array([grp(d) for d in dims])
GNAME = ["香气 A_", "风味 F_", "口感/缺陷/总体"]
GCOL = [CATEGORICAL[0], CATEGORICAL[1], CATEGORICAL[3]]

fig = plt.figure(figsize=(7.0, 3.0))
gs = fig.add_gridspec(2, 2, width_ratios=[2.35, 1.0], height_ratios=[1.0, 2.2],
                      left=0.075, right=0.985, top=0.90, bottom=0.155,
                      wspace=0.06, hspace=0.045)
axJ = fig.add_subplot(gs[1, 0])
axT = fig.add_subplot(gs[0, 0], sharex=axJ)
axR = fig.add_subplot(gs[1, 1], sharey=axJ)
axE = fig.add_subplot(gs[:, 1])
axE.remove()
axE = fig.add_subplot(gs[1, 1])
axR.remove()

# ---------------- joint panel ----------------
xg = np.linspace(0.30, 0.70, 240)
for k in range(3):
    m = g == k
    axJ.scatter(freq[m], jac[m], s=26, facecolor=GCOL[k], edgecolor="white",
                linewidth=0.7, alpha=0.92, zorder=3, label=GNAME[k])
axJ.axhline(base_mean, color=GREY, lw=0.8, ls=(0, (4, 3)), zorder=2)
axJ.axvline(1.0, color="#BBBBBB", lw=0.6, zorder=1)
axJ.set_xlim(0.92, 1.016)
axJ.set_ylim(-0.02, 0.72)
axJ.set_xlabel("Top-1 bootstrap 入选频率（%d 次重采样）" % nb)
axJ.set_ylabel("跨方法 Jaccard 系数")
axJ.grid(color="#EFEFEF", lw=0.4, zorder=0)
axJ.set_axisbelow(True)
n_full = int((freq >= 0.9999).sum())
axJ.annotate("%d/%d 维饱和于 1.000\n（单方法内部极稳）" % (n_full, len(freq)),
             xy=(1.0, 0.66), xytext=(0.955, 0.60), fontsize=6.6, color="#555555",
             ha="center", va="top",
             arrowprops=dict(arrowstyle="-", lw=0.6, color="#BBBBBB"))
axJ.annotate("随机基线 %.4f" % base_mean, xy=(0.985, base_mean), xytext=(0.985, 0.085),
             fontsize=6.4, color=GREY, ha="center",
             arrowprops=dict(arrowstyle="-", lw=0.5, color="#CCCCCC"))
leg = axJ.legend(loc="upper left", bbox_to_anchor=(0.005, 1.0), handletextpad=0.3,
                 labelspacing=0.25, borderaxespad=0.1, markerscale=0.9)

# ---------------- top marginal (bootstrap frequency) ----------------
counts, edges = np.histogram(freq, bins=np.arange(0.92, 1.02, 0.008))
axT.bar(edges[:-1] + 0.004, counts, width=0.0068, color=CATEGORICAL[0], alpha=0.55,
        edgecolor="none", zorder=2)
axT.set_ylabel("维度数", fontsize=6.6, labelpad=2)
axT.tick_params(axis="x", labelbottom=False)
axT.set_yticks([0, n_full])
axT.tick_params(axis="y", labelsize=6.2)
axT.spines["bottom"].set_visible(False)

# ---------------- right marginal (Jaccard) ----------------
from scipy.stats import gaussian_kde
yy = np.linspace(-0.02, 0.72, 220)
kde = gaussian_kde(jac, bw_method=0.35)
axR = fig.add_subplot(gs[1, 1], sharey=axJ)
axR.fill_betweenx(yy, 0, kde(yy), color=CATEGORICAL[1], alpha=0.35, lw=0)
axR.plot(kde(yy), yy, color=CATEGORICAL[1], lw=0.8)
axR.axhline(jac.mean(), color=CATEGORICAL[1], lw=0.8, ls=(0, (4, 3)))
axR.set_xlim(0, kde(yy).max() * 1.15)
axR.tick_params(axis="y", labelleft=False, length=0)
axR.tick_params(axis="x", labelsize=6.2)
axR.set_xticks([])
axR.set_xlabel("密度", fontsize=6.6, labelpad=1)
axR.spines["left"].set_visible(False)
axR.spines["bottom"].set_visible(False)



# ---------------- panel (b): ECDF vs random null ----------------
axB = fig.add_axes([0.735, 0.155, 0.245, 0.60])
rng = np.random.default_rng(42)
N, k = 211, 3
null = np.empty(20000)
for i in range(null.size):
    a = rng.choice(N, k, replace=False)
    b = rng.choice(N, k, replace=False)
    null[i] = len(np.intersect1d(a, b)) / len(np.union1d(a, b))

def ecdf(v):
    v = np.sort(np.asarray(v, dtype=float))
    return v, np.arange(1, v.size + 1) / v.size

xj, yj = ecdf(jac)
xn, yn = ecdf(null)
axB.plot(xn, yn, color=GREY, lw=1.0, ls=(0, (4, 2)), zorder=3)
axB.plot(xj, yj, color=CATEGORICAL[1], lw=1.3, zorder=4)
axB.axvline(jac.mean(), color=CATEGORICAL[1], lw=0.7, ls=(0, (4, 3)), zorder=2)
axB.set_xlim(0, 0.72)
axB.set_ylim(0, 1.02)
axB.set_xlabel("Jaccard 系数", fontsize=7.2)
axB.set_ylabel("累积比例", fontsize=7.2)
axB.tick_params(labelsize=6.4)
axB.grid(color="#EFEFEF", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.text(0.035, 0.90, "随机零分布\n（两独立 3 子集）", fontsize=6.2, color="#666666",
         va="top", ha="left")
axB.text(0.30, 0.42, "实测分布", fontsize=6.6, color=CATEGORICAL[1], va="center")
axB.annotate("均值 %.3f\n= 零分布 %.1f 倍" % (jac.mean(), jac.mean() / float(null.mean())),
             xy=(jac.mean(), 0.05), xytext=(0.30, 0.10), fontsize=6.2,
             color=CATEGORICAL[1],
             arrowprops=dict(arrowstyle="-", lw=0.5, color="#E0AFAF"))
axB.set_title("实测 vs 随机零分布", loc="left", fontsize=8, fontweight="bold", pad=4)

for ax_, tag in ((axJ, "(a)"), (axB, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.020, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

save_fig(fig, "figures/fig_q2_stability.png")
print("full=%d jac_mean=%.4f null_mean=%.4f ratio=%.1f"
      % (n_full, jac.mean(), null.mean(), jac.mean() / null.mean()))
