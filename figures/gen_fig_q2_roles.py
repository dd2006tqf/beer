# -*- coding: utf-8 -*-
"""fig_q2_roles -- 化合物角色：跨维枢纽 vs 单维专精

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) bubble scatter: breadth vs depth, size = phi -> assets/figures/MarginalDensity -> param inherit
(b) top-8 hub ranking with rank-1 share    -> assets/figures/BarComposition  -> param inherit

图 17 已经说明"少数化合物占掉大量席位"，但没有回答"这些化合物是同一种角色吗"。
把每个化合物放到（覆盖维度数，平均关键度）平面上：
右上=跨维枢纽，右下=只在一维极强（专精），左下=边缘候选。
点径=平均 bootstrap 入选频率，颜色=是否在高频区间。
这张图也让"26/50 化合物只出现 1 次"这件事有了位置感——它们全部堆在左侧。
Data: submission/q2_top3_compounds.csv。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
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
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

t = pd.read_csv(os.path.join(ROOT, "submission", "q2_top3_compounds.csv"))
g = t.groupby("compound").agg(
    n_dim=("sensory_dim", "nunique"),
    rank1=("rank", lambda s: int((s == 1).sum())),
    phi=("phi_score", "mean"),
    freq=("bootstrap_select_freq", "mean"),
).reset_index()

fig = plt.figure(figsize=(7.0, 3.25))
gs = fig.add_gridspec(1, 2, width_ratios=[1.16, 1.0], wspace=0.26,
                      left=0.080, right=0.975, top=0.885, bottom=0.195)
ax = fig.add_subplot(gs[0, 0])
axB = fig.add_subplot(gs[0, 1])

# ══════════ (a) bubble ══════════
hub = g["n_dim"] >= 3
ax.scatter(g.loc[~hub, "n_dim"], g.loc[~hub, "phi"],
           s=18 + 150 * g.loc[~hub, "freq"], color=GREY, alpha=0.55,
           edgecolor="white", linewidth=0.5, zorder=3)
ax.scatter(g.loc[hub, "n_dim"], g.loc[hub, "phi"],
           s=18 + 150 * g.loc[hub, "freq"], color=CATEGORICAL[0], alpha=0.85,
           edgecolor="white", linewidth=0.5, zorder=4)
for _, r in g.nlargest(8, "n_dim").iterrows():
    nm = r["compound"].replace("_", " ")
    ax.annotate(nm, (r["n_dim"], r["phi"]), xytext=(5, 4), textcoords="offset points",
                fontsize=5.8, color="#333333")
ax.axvline(2.5, color="#BBBBBB", lw=0.7, ls=(0, (3, 3)), zorder=1)
ax.set_xlim(0.2, 17.5)
ax.set_ylim(0.28, 1.02)
ax.set_xticks([1, 2, 3, 4, 6, 8, 10, 12, 16])
ax.set_xlabel("覆盖的感官维度数")
ax.set_ylabel("平均关键度 φ")
ax.grid(color="#F5F5F5", lw=0.4, zorder=0)
ax.set_axisbelow(True)

# ══════════ (b) hub ranking ══════════
top = g.nlargest(8, "n_dim").iloc[::-1]
y = np.arange(len(top))
share = top["rank1"] / top["n_dim"]
axB.barh(y, top["n_dim"], height=0.62, color="#DCE6F0", edgecolor="none", zorder=2)
axB.barh(y, top["n_dim"] * share, height=0.62, color=CATEGORICAL[1], alpha=0.75,
         edgecolor="none", zorder=3)
for yi, (_, r) in zip(y, top.iterrows()):
    axB.text(r["n_dim"] + 0.25, yi, "%d 维（%d 次第一）" % (r["n_dim"], r["rank1"]),
             va="center", fontsize=6.2, color="#333333")
axB.set_yticks(y)
axB.set_yticklabels([c.replace("_", " ") for c in top["compound"]], fontsize=6.4)
axB.tick_params(axis="y", length=0, pad=3)
axB.set_xlim(0, 22)
axB.set_xlabel("入选的维度数")
axB.grid(axis="x", color="#F5F5F5", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.spines["left"].set_visible(False)

tag_panels([ax, axB])

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_roles.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; compounds=%d hub=%d single=%d" % (len(g), int(hub.sum()), int((g.n_dim == 1).sum())))
