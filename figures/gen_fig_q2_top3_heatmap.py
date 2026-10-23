# -*- coding: utf-8 -*-
"""fig_q2_top3_heatmap — 问题二：感官维 × 关键化合物 Top-3 重要度（single，矩阵热力图）
行=12 感官维，列=所有维 Top-3 命中的关键化合物（并集，按命中维数降序）；
单元格=该化合物对该维的融合入选权重 φ（仅 Top-3 命中处有色，其余留白）。
既显示每维 Top-3 重要度强弱，又显示跨维共享的关键化合物（如 color.EBC.）。
数据源：problem_2_results.json::per_dim[dim].{top3,phi}。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from _figbase import P1, P2, save_fig, set_paper_placement, dim_zh
from _utils.plot_utils import draw_vector_heatmap

per = P2['per_dim']
# 聚焦 Q1 最可预测的 12 个感官维（归因最有意义）
q1_rank = [r[0] for r in P1['fig_data']['qwk_ranked'] if r[0] in per]
dims = q1_rank[:12]

# 列：这些维 Top-3 化合物并集，按"命中维数"降序（共享的排前面）
freq = Counter()
for d in dims:
    for c in per[d]['top3'][:3]:
        freq[c] += 1
comps = [c for c, _ in freq.most_common()]           # 全部并集

# 构造 φ 矩阵（dim × compound），未命中处置 NaN（draw_vector_heatmap 用 mask 留白）
cidx = {c: j for j, c in enumerate(comps)}
mat = np.full((len(dims), len(comps)), np.nan)
for i, d in enumerate(dims):
    for c, p in zip(per[d]['top3'][:3], per[d]['phi'][:3]):
        mat[i, cidx[c]] = p
mask = ~np.isfinite(mat)

w = max(6.2, 0.34 * len(comps) + 1.8)
fig, ax = plt.subplots(figsize=(min(w, 9.0), 4.8))
set_paper_placement(fig, width_fraction=0.98)
draw_vector_heatmap(
    ax, mat, mask=mask,
    xlabels=[c if len(c) <= 13 else c[:12] + '…' for c in comps],
    ylabels=[dim_zh(d) for d in dims],
    annot='auto', fmt='.2f', cmap='YlOrRd', cbar=True, cbar_label='融合入选权重 φ')
ax.set_xticklabels(ax.get_xticklabels(), rotation=60, ha='right', fontsize=5.6)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=7.2)

fig.tight_layout()
save_fig(fig, 'figures/fig_q2_top3_heatmap.png')
print('fig_q2_top3_heatmap done; dims=%d comps=%d' % (len(dims), len(comps)))
