# -*- coding: utf-8 -*-
"""fig_q3_ksprofile -- 生成谱逐列 KS：偏离集中在少数列

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) per-column KS as sorted lollipop -> assets/figures/BarCategorical -> param inherit
(b) KS vs column detection rate     -> assets/figures/GroupedViolin (cross-type) -> param inherit

KS 均值只有 0.35-0.41，但这是 231 列的平均。真正要回答的是：
偏离是系统性的（所有列都偏），还是集中在少数稀疏列？左图按列排序后可见
大部分列 KS < 0.2，长尾由少数列贡献；右图把 KS 与该列的未检出率联立，
说明高 KS 列正是稀疏、大量卡在检出限的列——这与 5.4 节的删失结构一致。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import ks_2samp
from _figbase import ROOT, save_fig

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

real = pd.read_csv(os.path.join(ROOT, "user_data", "1.csv"))
gen = pd.read_csv(os.path.join(ROOT, "submission", "q3_generated_profiles.csv"))
meta = {"beer", "beer_id", "tasting_category_fine"}
feat = [c for c in real.columns if c not in meta]

GEN = "Tripel"
R = real[real["tasting_category_fine"] == GEN]
G = gen[(gen["style"] == GEN) & (gen["sample_type"] == "generated")]

ks, undet, names = [], [], []
for c in feat:
    a = pd.to_numeric(R[c], errors="coerce").dropna().values
    b = pd.to_numeric(G[c], errors="coerce").dropna().values
    if a.size < 5 or b.size < 5:
        continue
    ks.append(ks_2samp(a, b).statistic)
    undet.append(float((a <= np.nanmin(a)).mean()))
    names.append(c)
ks = np.array(ks); undet = np.array(undet)
order = np.argsort(ks)[::-1]

fig = plt.figure(figsize=(7.0, 3.2))
gs = fig.add_gridspec(1, 2, width_ratios=[1.55, 1.0], wspace=0.20,
                      left=0.065, right=0.985, top=0.90, bottom=0.155)

# ══════════ (a) sorted lollipop ══════════
ax = fig.add_subplot(gs[0, 0])
x = np.arange(len(order))
v = ks[order]
ax.bar(x, v, width=0.9, color="#CFD9E3", edgecolor="none", zorder=2)
hi = v >= 0.5
ax.bar(x[hi], v[hi], width=0.9, color=CATEGORICAL[1], edgecolor="none", zorder=3)
ax.axhline(ks.mean(), color="#333333", lw=0.9, ls=(0, (4, 3)), zorder=4)
ax.set_xlim(-1, len(x))
ax.set_ylim(0, 1.0)
ax.set_xlabel("231 个化学列（按 KS 降序）")
ax.set_ylabel("生成谱 vs 真实 %s 谱的 KS 距离" % GEN)
ax.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.text(len(x) * 0.985, ks.mean() + 0.025, "均值 %.3f" % ks.mean(), ha="right",
        fontsize=6.4, color="#333333")
n_hi = int(hi.sum())
ax.annotate("%d 列 KS ≥ 0.5\n（占 %.1f%%）" % (n_hi, 100 * n_hi / len(x)),
            xy=(n_hi * 0.5, 0.93), xytext=(len(x) * 0.34, 0.80), fontsize=6.5,
            color=CATEGORICAL[1],
            arrowprops=dict(arrowstyle="->", lw=0.6, color="#D9A0A0"))
ax.annotate("其余 %d 列 KS < 0.2" % int((ks < 0.2).sum()),
            xy=(len(x) * 0.86, 0.10), xytext=(len(x) * 0.60, 0.30), fontsize=6.3,
            color="#555555",
            arrowprops=dict(arrowstyle="->", lw=0.6, color="#BBBBBB"))
ax.set_title("(a) 偏离集中在少数列，而非系统性偏移", loc="left", fontsize=8,
             fontweight="bold", pad=4)

# ══════════ (b) KS vs 未检出率 ══════════
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(undet, ks, s=14, color=CATEGORICAL[0], alpha=0.55, edgecolor="white",
            linewidth=0.35, zorder=3)
# 分箱中位数
bins = np.linspace(0, 1, 6)
mid, med = [], []
for i in range(len(bins) - 1):
    m = (undet >= bins[i]) & (undet < bins[i + 1])
    if m.sum() >= 4:
        mid.append((bins[i] + bins[i + 1]) / 2)
        med.append(np.median(ks[m]))
ax2.plot(mid, med, color=CATEGORICAL[1], lw=1.3, marker="o", ms=4, zorder=5)
ax2.set_xlim(-0.02, 1.0)
ax2.set_ylim(0, 1.0)
ax2.set_xlabel("该列在本风格真实谱中的未检出比例")
ax2.set_ylabel("KS 距离")
ax2.grid(color="#F3F3F3", lw=0.4, zorder=0)
ax2.set_axisbelow(True)
ax2.set_title("(b) 高 KS 列对应稀疏检出列", loc="left", fontsize=8,
              fontweight="bold", pad=4)
r = np.corrcoef(undet, ks)[0, 1]
ax2.text(0.03, 0.93, "Pearson r = %.2f" % r, fontsize=6.6, color="#333333",
         transform=ax2.transAxes)
ax2.text(0.03, 0.86, "红点=分箱中位", fontsize=6.2, color=CATEGORICAL[1],
         transform=ax2.transAxes)

fig.savefig(os.path.join(ROOT, "figures", "fig_q3_ksprofile.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; n=%d mean=%.4f hi=%d r=%.2f" % (len(ks), ks.mean(), n_hi, r))
