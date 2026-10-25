# -*- coding: utf-8 -*-
"""fig_q2_communities — 化合物集 C(211) 共表达网络的 Louvain 社区规模分布
55 个社区按规模降序；前 8 大社区（彩色）合计覆盖多数节点，其余为单点小社区。
数据源：problem_2_results.json::fig_data.community_sizes / graph。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P2, PALETTE, save_fig, set_paper_placement, declutter_axes

sizes = sorted(P2['fig_data']['community_sizes'], reverse=True)
g = P2['graph']
n = len(sizes); total = sum(sizes); top8 = sum(sizes[:8])
x = np.arange(1, n + 1)
colors = [PALETTE[i % 6] if i < 8 else '#C9CED6' for i in range(n)]

fig, ax = plt.subplots(figsize=(8.6, 4.0))
set_paper_placement(fig)
ax.bar(x, sizes, color=colors, edgecolor='white', linewidth=0.4)
for i in range(8):
    ax.text(x[i], sizes[i] + 0.5, str(sizes[i]), ha='center', fontsize=8, color='#333')
ax.set_xlabel('社区编号（按规模降序）')
ax.set_ylabel('社区内化合物数')
ax.set_xlim(0.4, n + 0.6)
declutter_axes(ax, grid_axis='y')
fig.tight_layout()
save_fig(fig, 'figures/fig_q2_communities.png')
print('fig_q2_communities done; n=%d top8=%d/%d' % (n, top8, total))
