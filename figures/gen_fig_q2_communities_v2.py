# -*- coding: utf-8 -*-
"""fig_q2_communities — 社区规模分布（ModelViz 模板版式重做）

沿用模板 04_DIS「分布与不确定性」的排序条形版式：降序条形 + 前 8 大社区
数值标注 + 累计覆盖说明；配色改为论文的深蓝/浅灰两级。
数据源：problem_2_results.json::fig_data.community_sizes。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt

from _figbase import P2, save_fig, set_paper_placement, declutter_axes

sizes = sorted(P2["fig_data"]["community_sizes"], reverse=True)
n = len(sizes)
total = sum(sizes)
top8 = sum(sizes[:8])
x = np.arange(1, n + 1)
colors = ["#2E5C8A"] * 8 + ["#C9CED6"] * (n - 8)

fig, ax = plt.subplots(figsize=(7.2, 3.7))
set_paper_placement(fig, width_fraction=0.96)
ax.bar(x, sizes, color=colors, edgecolor="white", linewidth=0.4, zorder=2)
for i in range(8):
    ax.text(x[i], sizes[i] + 0.5, str(sizes[i]), ha="center", fontsize=7.4, color="#222")
ax.axvspan(0.5, 8.5, color="#2E5C8A", alpha=0.05, zorder=0)
ax.text(8.8, max(sizes) * 0.92,
        "前 8 大社区：%d/%d 节点（%.0f%%）" % (top8, total, 100 * top8 / total),
        fontsize=7.8, color="#222", ha="left", va="top")
ax.set_xlabel("社区编号（按规模降序）", fontsize=8.2)
ax.set_ylabel("社区内化合物数", fontsize=8.2)
ax.set_xlim(0.4, n + 0.6)
ax.tick_params(labelsize=7.2)
declutter_axes(ax, grid_axis="y")
fig.tight_layout()
save_fig(fig, "figures/fig_q2_communities.png")
print("fig_q2_communities done; n=%d top8=%d/%d" % (n, top8, total))
