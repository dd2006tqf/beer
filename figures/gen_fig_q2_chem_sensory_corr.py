# -*- coding: utf-8 -*-
"""fig_q2_chem_sensory_corr — 问题二合理性证据（single，相关矩阵热力图）
12 感官维 × 14 关键化合物的 Pearson 相关矩阵，展示化学-感官交叉关联结构。
数据源：supp_eda.json::chem_sensory_corr（由 1.csv 化学 + 4.csv 感官按 beer_id 对齐派生）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import SUPP, save_fig, set_paper_placement, dim_zh
from _utils.plot_utils import draw_vector_heatmap

cs = SUPP['chem_sensory_corr']
dims = cs['sensory_dims']
comps = cs['compounds']
mat = np.array([[np.nan if v is None else v for v in row] for row in cs['matrix']])

fig, ax = plt.subplots(figsize=(6.6, 4.8))
set_paper_placement(fig)
draw_vector_heatmap(
    ax, mat,
    xlabels=[c if len(c) <= 12 else c[:11] + '…' for c in comps],
    ylabels=[dim_zh(d) for d in dims],
    annot='auto', fmt='.2f', cmap='coolwarm', center=0.0,
    vmin=-1, vmax=1, cbar=True, cbar_label='Pearson 相关系数')
ax.set_xticklabels(ax.get_xticklabels(), rotation=55, ha='right', fontsize=6.4)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=7.0)

fig.tight_layout()
save_fig(fig, 'figures/fig_q2_chem_sensory_corr.png')
print('fig_q2_chem_sensory_corr done; shape=%dx%d' % mat.shape)
