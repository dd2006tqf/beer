# -*- coding: utf-8 -*-
"""fig_q2_top1_bar -- Top-1/2/3 入选频率：饱和与衰减

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) strip plot over 3 ranks        -> assets/figures/GroupedViolin -> param inherit
(b) lollipop of weakest rank-3     -> assets/figures/BarCategorical -> param inherit

原版是 3x50 的热力矩阵，前两列几乎全为 1.000，整图呈一片同色，读者读不出信息。
这里改成两个互补视图：
(a) 三个名次上全部 50 维的实际取值，直接看出 rank1/2 饱和、rank3 才分化；
(b) 把 rank3 最低的 14 维单独列出并写明化合物，回答"第三名是不是凑数"。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from _figbase import ROOT, save_fig, dim_zh, tag_panels

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

df = pd.read_csv(os.path.join(ROOT, "submission", "q2_top3_compounds.csv"))
piv = df.pivot(index="sensory_dim", columns="rank", values="bootstrap_select_freq")
comp = df.pivot(index="sensory_dim", columns="rank", values="compound")
piv = piv.loc[piv[3].sort_values().index]

fig = plt.figure(figsize=(7.4, 3.35))
gs = fig.add_gridspec(1, 2, width_ratios=[0.52, 1.0], wspace=0.78,
                      left=0.070, right=0.975, top=0.870, bottom=0.190)

# ---------------- (a) strip plot ----------------
ax = fig.add_subplot(gs[0, 0])
long = piv.reset_index().melt(id_vars="sensory_dim", var_name="rank", value_name="freq")
long["x"] = long["rank"].map({1: 0, 2: 1, 3: 2})
swarm_pal = {0: CATEGORICAL[0], 1: CATEGORICAL[0], 2: CATEGORICAL[1]}
sns.swarmplot(data=long, x="x", y="freq", ax=ax, size=2.6,
              palette=swarm_pal, hue="x", legend=False,
              linewidth=0.2, edgecolor="white", alpha=0.85, zorder=3)
ax.set_xlabel("")
for i, r in enumerate([1, 2, 3]):
    v = piv[r].values
    ax.plot([i - 0.24, i + 0.24], [np.median(v)] * 2, color="#222222", lw=1.0, zorder=5)
    ax.text(i, 1.055, "%.3f" % v.mean(), ha="center", va="bottom", fontsize=6.6,
            color="#222222")
    ax.text(i, 0.335, "n=%d" % v.size, ha="center", va="bottom", fontsize=6.0, color=GREY)
ax.set_xticks([0, 1, 2])
ax.set_xticklabels(["第 1 位", "第 2 位", "第 3 位"])
ax.set_xlim(-0.55, 2.55)
ax.set_ylim(0.32, 1.09)
ax.set_ylabel("bootstrap 入选频率（500 次重采样）")
ax.grid(axis="y", color="#EFEFEF", lw=0.4, zorder=0)
ax.set_axisbelow(True)
# 两处 annotate 标注与引线已移除（改由图题与正文承担说明）


# ---------------- (b) weakest rank-3 lollipop ----------------
axB = fig.add_subplot(gs[0, 1])
K = 14
sub = piv[[3]].head(K).iloc[::-1]
names = []
for d in sub.index:
    nm = comp.loc[d, 3]
    nm = nm.replace("_", " ")
    names.append("%s ← %s" % (dim_zh(d), nm if len(nm) <= 15 else nm[:14] + "…"))
y = np.arange(K)
vals = sub[3].values
# 参考：全维 rank3 均值
mu = piv[3].mean()
axB.axvline(mu, color=GREY, lw=0.8, ls=(0, (4, 3)), zorder=2)
colors = [CATEGORICAL[1] if v < 0.7 else (CATEGORICAL[3] if v < 0.9 else CATEGORICAL[0])
          for v in vals]
for yi, v, c in zip(y, vals, colors):
    axB.plot([0.30, v], [yi, yi], color=c, lw=1.4, alpha=0.55, zorder=3,
             solid_capstyle="round")
    axB.scatter([v], [yi], s=26, color=c, edgecolor="white", linewidth=0.7, zorder=4)
    axB.text(v + 0.012, yi, "%.3f" % v, va="center", ha="left", fontsize=6.1, color="#333333")
axB.set_yticks(y)
axB.set_yticklabels(names, fontsize=6.4)
axB.tick_params(axis="y", length=0, pad=3)
axB.set_xlim(0.30, 1.06)
axB.set_ylim(-0.7, K - 0.3)
axB.set_xlabel("第 3 位化合物的入选频率")
axB.grid(axis="x", color="#EFEFEF", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.text(mu - 0.012, K - 0.55, "全维均值 %.3f" % mu, ha="right", va="center",
         fontsize=6.1, color=GREY)


# 子图编号置于各自下方（面板底部居中）
tag_panels([ax, axB])

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_top1_bar.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; rank3 min=%.3f mean=%.3f" % (piv[3].min(), mu))
