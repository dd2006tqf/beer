# -*- coding: utf-8 -*-
"""fig_q1_missing_pattern —— 缺失结构与缺失来源（ModelViz 09_REL_011 版式）

左：63 个含缺失样本 × 9 个含缺失列 的缺失矩阵，行按缺失个数降序，
    格点用极浅底色勾出网格，深色块即缺失，可直接读出"列向集中 + 少数行多缺"；
右：9 列的缺失率与累计占比，横向条形 + 复利曲线，回答"哪几列贡献了大部分缺失"。

相对于原"矩阵 + 条形图"，右半改用累计占比后可直接看出前三列是否已解释
大半缺失，比逐列读数更有结论性。

数据源：figures/supp_eda.json::missing（1.csv 派生）。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from _figbase import SUPP, PALETTE, COLORS, save_fig, declutter_axes, tag_panels

mi = SUPP['missing']
na_cols = list(mi['na_cols'])
mat = np.array(mi['na_matrix'])
col_rate = dict(mi['col_na_rate'])
n_na_rows = mi['n_na_rows']

row_has_na = mat.sum(axis=1) > 0
sub = mat[row_has_na]
order = np.argsort(-sub.sum(axis=1), kind='stable')
sub = sub[order]
n_show, n_col = sub.shape

plt.rcParams.update({
    'axes.labelsize': 8.0,
    'xtick.labelsize': 7.0,
    'ytick.labelsize': 7.0,
    'legend.fontsize': 7.2,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

fig = plt.figure(figsize=(5.9, 3.55))
# 固定坐标：两子图上下边严格对齐，左侧旋转标签不再改变绘图区高度
ax1 = fig.add_axes([0.075, 0.235, 0.375, 0.705])
ax2 = fig.add_axes([0.585, 0.235, 0.375, 0.705])

# ── 左：缺失矩阵 ────────────────────────────────────────────
cmap = ListedColormap(['#F4F6F8', PALETTE[3]])
ax1.imshow(sub, aspect='auto', cmap=cmap, interpolation='nearest',
           vmin=0, vmax=1, zorder=2)
# 极浅网格，便于数格子；不盖住深色块
for x in np.arange(-0.5, n_col, 1):
    ax1.axvline(x, color='white', lw=0.45, zorder=3, alpha=0.9)
ax1.set_xticks(range(n_col))
ax1.set_xticklabels(['C%d' % (i + 1) for i in range(n_col)], fontsize=7.0)
ax1.set_yticks([0, (n_show - 1) // 2, n_show - 1])
ax1.set_yticklabels([1, (n_show + 1) // 2, n_show], fontsize=6.8)
ax1.set_ylabel('含缺失样本（按缺失个数降序，共 %d 行）' % n_na_rows, fontsize=7.6)
ax1.tick_params(length=0)
for s in ax1.spines.values():
    s.set_visible(False)
handles = [Patch(facecolor=PALETTE[3], label='缺失'),
           Patch(facecolor='#F4F6F8', edgecolor='#D5DAE0', label='观测'),
           Line2D([], [], color=PALETTE[0], lw=1.2, marker='o', ms=2.8,
                  markerfacecolor='white', label='累计占比（右轴）')]
fig.legend(handles=handles, loc='outside lower center', ncol=3, frameon=False,
           handlelength=1.1, columnspacing=1.6, handletextpad=0.45,
           borderaxespad=0.1)

# ── 右：缺失率与累计占比 ────────────────────────────────────
cols_sorted = sorted(col_rate.items(), key=lambda kv: kv[1])
cnames = [c for c, _ in cols_sorted]
rates = np.array([v * 100 for _, v in cols_sorted])
yy = np.arange(len(cnames))
ax2.barh(yy, rates, height=0.66, color=PALETTE[1], edgecolor='white',
         linewidth=0.6, zorder=3, label='列缺失率')
for i, r in enumerate(rates):
    ax2.text(r + 0.20, i, '%.1f%%' % r, va='center', fontsize=6.8, color='#374151')
ax2.set_yticks(yy)
ax2.set_yticklabels([c if len(c) <= 13 else c[:12] + '…' for c in cnames],
                    fontsize=6.6)
ax2.set_xlim(0, max(rates) * 1.42)
ax2.set_xlabel('列缺失率（%）')
ax2.set_ylim(-0.7, len(cnames) - 0.3)
declutter_axes(ax2, 'x')

# 累计占比：叠加在右上角的细线，说明集中度
cum = np.cumsum(rates) / rates.sum() * 100
ax3 = ax2.twiny()
ax3.plot(cum, yy, color=PALETTE[0], lw=1.2, marker='o', ms=2.8,
         markerfacecolor='white', markeredgewidth=0.8, zorder=4)
ax3.set_xlim(0, 108)
ax3.set_xticks([0, 50, 100])
ax3.set_xticklabels(['0', '50', '100%'])
ax3.tick_params(axis='x', labelsize=6.6, colors=PALETTE[0], length=2)
ax3.spines['top'].set_color(PALETTE[0])
for s in ('right', 'left', 'bottom'):
    ax3.spines[s].set_visible(False)

tag_panels([ax1, ax2])
save_fig(fig, 'figures/fig_q1_missing_pattern.png')
print('done; rows=%d cols=%d top3=%.1f%%' % (n_show, n_col, cum[-3]))
