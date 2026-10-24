# -*- coding: utf-8 -*-
"""fig_q2_chem_sensory_corr — 化学-感官交叉相关矩阵（按类别分组重排）
50 个感官维 × 14 个高频候选化合物的 Pearson 相关矩阵；行按 香气(A_) / 风味(F_) / 口感缺陷 分组排列，
组间以粗黑线分隔，便于读出类别层面的关联结构。
数据源：supp_eda.json::chem_sensory_corr（由 1.csv 化学 + 4.csv 感官按 beer_id 对齐派生）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import SUPP, save_fig, set_paper_placement, dim_zh
from _utils.plot_utils import draw_vector_heatmap

cs = SUPP['chem_sensory_corr']
dims = cs['sensory_dims']; comps = cs['compounds']
mat = np.array([[np.nan if v is None else v for v in row] for row in cs['matrix']])


def grp(d):
    return 0 if d.startswith('A_') else (1 if d.startswith('F_') else 2)


order = sorted(range(len(dims)), key=lambda i: (grp(dims[i]), -np.nanmax(np.abs(mat[i]))))
dims = [dims[i] for i in order]; mat = mat[order]
bounds = [i for i in range(1, len(dims)) if grp(dims[i]) != grp(dims[i - 1])]
group_mid = {}
for g in (0, 1, 2):
    idx = [i for i, d in enumerate(dims) if grp(d) == g]
    group_mid[g] = (idx[0] + idx[-1]) / 2
gname = {0: '香气维', 1: '风味维', 2: '口感/缺陷维'}

fig, ax = plt.subplots(figsize=(7.4, 9.6))
set_paper_placement(fig)
draw_vector_heatmap(
    ax, mat,
    xlabels=[c if len(c) <= 12 else c[:11] + '…' for c in comps],
    ylabels=[dim_zh(d) for d in dims],
    annot='auto', fmt='.2f', cmap='coolwarm', center=0.0,
    vmin=-1, vmax=1, cbar=True, cbar_label='Pearson 相关系数')
ax.set_xticklabels(ax.get_xticklabels(), rotation=55, ha='right', fontsize=6.6)
ax.set_yticklabels(ax.get_yticklabels(), fontsize=6.4)
for b in bounds:
    ax.hlines(b - 0.5, -0.5, len(comps) - 0.5, color='#222', lw=1.6, zorder=6)
for g, mid in group_mid.items():
    ax.text(-1.55, mid, gname[g], ha='center', va='center', rotation=90,
            fontsize=9, fontweight='bold', color='#222')

fig.tight_layout()
save_fig(fig, 'figures/fig_q2_chem_sensory_corr.png')
print('fig_q2_chem_sensory_corr done; shape=%dx%d bounds=%s' % (mat.shape[0], mat.shape[1], bounds))
