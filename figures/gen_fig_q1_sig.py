# -*- coding: utf-8 -*-
"""fig_q1_sig -- 主模型相对三类基线的配对 bootstrap 显著性（森林图 + 分布）

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) forest plot  -> assets/figures/BarComparison (cross-type: Forest)  -> param inherit
(b) bootstrapped delta distribution -> assets/figures/RidgePlot      -> param inherit
Design intent: panel (a) answers "how large and how certain is the gain",
panel (b) answers "where does the 2000x resampling mass sit relative to zero".
Data: _tmp/q1_boot_full.json (2000 paired resamples, same rows for main/baseline).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from _figbase import ROOT  # injects project root into sys.path

# ---- Academic Figure Skill typography baseline (CJK-adapted: SimHei first) ----
mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8,
    "axes.titlesize": 8,
    "axes.labelsize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "figure.titlesize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "legend.frameon": False,
    "axes.unicode_minus": False,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# ---- Academic Figure Skill palette (verbatim values) ----
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"
BLACK = "#222222"

res = json.load(open(os.path.join(ROOT, "_tmp", "q1_boot_full.json"), encoding="utf-8"))
ORDER = ["knn", "rf", "enet"]
LABEL = {"knn": "KNN 插补后建模", "rf": "随机森林（中位插补）", "enet": "ElasticNet（中位插补）"}

fig = plt.figure(figsize=(6.4, 2.75))
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.10,
                      left=0.155, right=0.985, top=0.90, bottom=0.17)
axA = fig.add_subplot(gs[0, 0])
axB = fig.add_subplot(gs[0, 1], sharey=axA)

ys = np.arange(len(ORDER))[::-1]
xmax = 0.155

# ---------------- panel (a): forest plot ----------------
axA.axvspan(-0.004, 0, color=GREY, alpha=0.10, lw=0, zorder=0)
axA.axvline(0, color="#555555", lw=0.8, ls=(0, (4, 3)), zorder=2)
for y, key in zip(ys, ORDER):
    r = res["deltas"][key]
    lo, hi, d, pi = r["lo"], r["hi"], r["delta"], r["pi"]
    c = CATEGORICAL[0]
    axA.plot([lo, hi], [y, y], color=c, lw=2.0, solid_capstyle="butt", zorder=3, alpha=0.95)
    for x in (lo, hi):
        axA.plot([x, x], [y - 0.11, y + 0.11], color=c, lw=1.0, zorder=3)
    axA.scatter([d], [y], s=34, marker="D", facecolor="white", edgecolor=c,
                linewidth=1.2, zorder=5)
    axA.annotate("%.4f" % d, (d, y), xytext=(0, 8), textcoords="offset points",
                 ha="center", va="bottom", fontsize=6.6, color=BLACK)
    # right-hand numeric column
    axA.text(xmax * 1.02, y + 0.13, "Δ = %+.4f" % d, fontsize=6.6, color=BLACK,
             va="center", ha="left")
    axA.text(xmax * 1.02, y - 0.17, "[%.4f, %.4f]   π = %.3f" % (lo, hi, pi),
             fontsize=6.2, color=GREY, va="center", ha="left")

axA.set_yticks(ys)
axA.set_yticklabels([LABEL[k] for k in ORDER], fontsize=7.2)
axA.tick_params(axis="y", length=0, pad=4)
axA.set_ylim(-0.62, len(ORDER) - 0.38)
axA.set_xlim(-0.004, xmax * 2.18)
axA.set_xlabel("50 维平均 QWK 差值 Δ（主模型 - 基线）")
axA.xaxis.set_major_locator(MultipleLocator(0.05))
axA.grid(axis="x", color="#E6E6E6", lw=0.4, zorder=0)
axA.set_axisbelow(True)
axA.set_title("(a) 点估计与 95% 置信区间", loc="left", fontsize=8, fontweight="bold", pad=5)

# ---------------- panel (b): bootstrap distributions ----------------
for y, key in zip(ys, ORDER):
    v = np.array(res["deltas"][key]["values"])
    v = v[np.isfinite(v)]
    c = CATEGORICAL[0]
    # horizontal half-violin from kernel density
    from scipy.stats import gaussian_kde
    kde = gaussian_kde(v, bw_method=0.28)
    gx = np.linspace(v.min(), v.max(), 220)
    gy = kde(gx)
    gy = gy / gy.max() * 0.34
    axB.fill_between(gx, y - gy, y, color=c, alpha=0.30, lw=0, zorder=3)
    axB.plot(gx, y - gy, color=c, lw=0.8, zorder=4)
    med = np.median(v)
    axB.plot([med, med], [y - 0.34, y], color=CATEGORICAL[1], lw=0.9, zorder=5)

axB.axvline(0, color="#555555", lw=0.8, ls=(0, (4, 3)), zorder=2)
axB.set_xlim(-0.01, 0.145)
axB.set_xlabel("bootstrap 重采样下的 Δ")
axB.tick_params(axis="y", left=False, labelleft=False)
axB.grid(axis="x", color="#E6E6E6", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.set_title("(b) 2000 次配对重采样分布", loc="left", fontsize=8, fontweight="bold", pad=5)
axB.text(0.004, ys[-1] - 0.30, "Δ = 0", fontsize=6.2, color="#555555", ha="left", va="top")
axB.annotate("三组分布全部落在 0 右侧\n（π = 1.000）", xy=(0.10, ys[0] + 0.03),
             fontsize=6.4, color=CATEGORICAL[1], ha="center", va="bottom")

fig.savefig(os.path.join(ROOT, "figures", "fig_q1_sig.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved fig_q1_sig")
for k in ORDER:
    r = res["deltas"][k]
    print("%-8s d=%+.4f [%.4f, %.4f] pi=%.3f" % (k, r["delta"], r["lo"], r["hi"], r["pi"]))
