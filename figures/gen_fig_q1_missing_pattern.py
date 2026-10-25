# -*- coding: utf-8 -*-
"""fig_q1_missing_pattern — 问题一缺失模式（single，左矩阵+右条形）
左：含缺失列（9 列）的缺失模式矩阵（行=样本，深色=缺失），直观看出缺失集中在少数行
右：各列缺失率条形
数据源：supp_eda.json::missing（1.csv 派生）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from _figbase import SUPP, PALETTE, COLORS, save_fig, set_paper_placement, declutter_axes, panel

mi = SUPP['missing']
na_cols = mi['na_cols']
mat = np.array(mi['na_matrix'])                 # (n_rows, n_na_cols) 0/1
col_rate = dict(mi['col_na_rate'])
n_rows, n_cols_total = mi['n_rows'], mi['n_cols']
n_na_rows = mi['n_na_rows']

# 只保留至少有一个缺失的行，让缺失模式更清晰（标题/正文交代共 n_na_rows 行）
row_has_na = mat.sum(axis=1) > 0
sub = mat[row_has_na]
# 按缺失数排序行
order = np.argsort(-sub.sum(axis=1))
sub = sub[order]

fig, axes = plt.subplots(1, 2, figsize=(6.4, 4.0), gridspec_kw={'width_ratios': [1.3, 1]})
set_paper_placement(fig)

# ── 左：缺失模式矩阵 ─────────────────────────
ax = axes[0]
cmap = ListedColormap([_c for _c in ['#EDEFF2', PALETTE[3]]])
ax.imshow(sub, aspect='auto', cmap=cmap, interpolation='nearest', vmin=0, vmax=1)
ax.set_xticks(range(len(na_cols)))
ax.set_xticklabels([c if len(c) <= 12 else c[:11] + '…' for c in na_cols],
                   rotation=55, ha='right', fontsize=6.2)
ax.set_yticks([0, sub.shape[0] - 1])
ax.set_yticklabels([1, sub.shape[0]], fontsize=7)
ax.set_ylabel(f'含缺失样本（共 {n_na_rows} 行）')
# 图例代理
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=PALETTE[3], label='缺失'), Patch(color='#EDEFF2', label='观测')],
          loc='lower right', fontsize=6.8, framealpha=0.9)

# ── 右：列缺失率条形 ─────────────────────────
ax = axes[1]
cols_sorted = sorted(col_rate.items(), key=lambda kv: kv[1])
cnames = [c for c, _ in cols_sorted]
rates = [v * 100 for _, v in cols_sorted]
yy = np.arange(len(cnames))
ax.barh(yy, rates, color=PALETTE[1], edgecolor='white', linewidth=0.6)
for i, r in enumerate(rates):
    ax.text(r + 0.15, i, f'{r:.1f}%', va='center', fontsize=6.6, color=COLORS['text'])
ax.set_yticks(yy)
ax.set_yticklabels([c if len(c) <= 13 else c[:12] + '…' for c in cnames], fontsize=6.4)
ax.set_xlabel('列缺失率（%）')
ax.set_xlim(0, max(rates) * 1.25)
declutter_axes(ax, grid_axis='x')

fig.tight_layout()
save_fig(fig, 'figures/fig_q1_missing_pattern.png')
print('fig_q1_missing_pattern done; na_rows=%d' % n_na_rows)
