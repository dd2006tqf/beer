# -*- coding: utf-8 -*-
"""fig_q2_source_freq — 不同来源化合物的 bootstrap 入选频率分布（ModelViz 模板版式重做）

沿用模板 04_DIS「分布与不确定性」的箱线+散点版式：按来源分组、
显示中位数与四分位、叠加原始点；配色使用论文统一的低饱和分类色。
数据源：problem_2_results.json::fig_data.freq_by_source。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt

from _figbase import P2, save_fig, set_paper_placement, declutter_axes

fd = P2["fig_data"]["freq_by_source"]
ZH = {"Yeast": "酵母酯醇", "Hops": "酒花萜类", "Malt": "麦芽",
      "Spices": "香料", "Others": "其他", "Wild flora": "野生菌群"}
ORDER = ["Yeast", "Hops", "Malt", "Others", "Spices"]
ORDER = [k for k in ORDER if k in fd]

data = [np.asarray(fd[k], dtype=float) for k in ORDER]
labels = ["%s\n(n=%d)" % (ZH[k], len(fd[k])) for k in ORDER]
COLORS = ["#2E5C8A", "#3E8E5A", "#8C6D31", "#6C7A89", "#7D5BA6"]

fig, ax = plt.subplots(figsize=(6.8, 3.8))
set_paper_placement(fig, width_fraction=0.94)

bp = ax.boxplot(data, widths=0.5, patch_artist=True, showfliers=False,
                medianprops=dict(color="#222", lw=1.1),
                whiskerprops=dict(color="#666", lw=0.8),
                capprops=dict(color="#666", lw=0.8),
                boxprops=dict(lw=0.8))
for patch, c in zip(bp["boxes"], COLORS[:len(data)]):
    patch.set_facecolor(c)
    patch.set_alpha(0.28)
    patch.set_edgecolor(c)

rng = np.random.default_rng(42)
for i, d in enumerate(data, 1):
    jitter = rng.uniform(-0.14, 0.14, size=len(d))
    ax.scatter(np.full(len(d), i) + jitter, d, s=9, color=COLORS[i - 1],
               alpha=0.75, linewidths=0, zorder=3)

ax.set_xticks(range(1, len(data) + 1))
ax.set_xticklabels(labels, fontsize=7.6)
ax.set_ylabel("Top-3 bootstrap 入选频率", fontsize=8.2)
ax.set_ylim(0.25, 1.03)
ax.tick_params(axis="y", labelsize=7.2)
declutter_axes(ax, grid_axis="y")
fig.tight_layout()
save_fig(fig, "figures/fig_q2_source_freq.png")
print("fig_q2_source_freq done; groups=%s" % [(k, len(fd[k])) for k in ORDER])
