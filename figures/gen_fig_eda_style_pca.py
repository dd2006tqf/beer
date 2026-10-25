# -*- coding: utf-8 -*-
"""fig_eda_style_pca — 数据探索（2 panel）
(a) 22 种啤酒风格样本量横向条形（看类别不均衡）
(b) 231 维化学谱标准化后 PCA 前两主成分散点，按风格着色（看化学谱可分性）
数据源：supp_eda.json（由 1.csv 派生：style_counts, pca_chem）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import SUPP, PALETTE, PALETTE_LIGHT, COLORS, save_fig, set_paper_placement, panel, declutter_axes

sc = SUPP['style_counts']                       # [[name, n], ...] 已降序
_abbr = {'Flanders old brown': 'Fl.o.brn', 'West Flanders ale': 'W.Fl.ale',
         'Brett/cofermented': 'Brett', 'Low/No alcohol': 'LowAlc',
         'Stout/Porter': 'Stout', 'Strong ale': 'Strong', 'Christmas': 'Xmas',
         'Fruitbeer': 'Fruit', 'Pils/Lager': 'Pils'}
names = [_abbr.get(x[0], x[0]) for x in sc]
counts = [x[1] for x in sc]
pca = SUPP['pca_chem']
ev = pca['explained_var']

fig, axes = plt.subplots(1, 2, figsize=(6.8, 4.3), gridspec_kw={'width_ratios': [1, 1.1]})
set_paper_placement(fig)

# ── panel (a): 风格样本量横向条形（渐变单色族）────────────────
ax = axes[0]
y = np.arange(len(names))[::-1]
base = PALETTE[0]
from _figbase import _lighten
cols = [_lighten(base, 0.0 + 0.55 * i / max(1, len(names) - 1)) for i in range(len(names))]
ax.barh(y, counts, color=cols, edgecolor='white', linewidth=0.6)
ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=6.6)
ax.set_xlabel('样本量（款）')
ax.set_xlim(0, max(counts) * 1.08)
declutter_axes(ax, grid_axis='x')

# ── panel (b): 化学谱 PCA 散点，按风格着色（高亮本题 Q3 的 3 风格）───
ax = axes[1]
styles = pca['style']
uniq = [s for s, _ in sc]                       # 按样本量排序的风格
highlight = {'Tripel', 'Kriek', 'Lambic'}
cmap_cols = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(uniq)}
x = np.array(pca['x']); yv = np.array(pca['y'])
# 先画非高亮（浅灰小点），再画高亮（彩色大点）
is_h = np.array([s in highlight for s in styles])
ax.scatter(x[~is_h], yv[~is_h], s=16, c=COLORS['grid'], alpha=0.55,
           edgecolors='white', linewidths=0.3, zorder=2, label='其他风格')
for s in ['Tripel', 'Kriek', 'Lambic']:
    m = np.array([st == s for st in styles])
    ax.scatter(x[m], yv[m], s=34, color=cmap_cols[s], alpha=0.9,
               edgecolors='white', linewidths=0.5, label=s, zorder=3)
ax.set_xlabel(f'PC1（{ev[0]*100:.1f}%）')
ax.set_ylabel(f'PC2（{ev[1]*100:.1f}%）')
ax.legend(loc='upper right', fontsize=7, framealpha=0.85, handletextpad=0.3)
declutter_axes(ax)

fig.tight_layout()
save_fig(fig, 'figures/fig_eda_style_pca.png')
print('fig_eda_style_pca done')
