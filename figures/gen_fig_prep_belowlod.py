# -*- coding: utf-8 -*-
"""fig_prep_belowlod — 未检出(≤列下限) 与 真正缺失(NA) 区分（1×2）
(a) 真正缺失：9 列的 NA 单元格数（全表共 73 个 NA，集中在少数列）
(b) 未检出：未检出率最高的 15 列（取值=列内最小值/检出限编码）；
    未检出率在 5%–95% 的列才建指示变量（共 102 列），过低/过高不建。
数据源：supp_preprocess.json::missing_vs_belowlod。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import load, PALETTE, save_fig, set_paper_placement, declutter_axes

mv = load('supp_preprocess.json')['missing_vs_belowlod']
na_total = mv['na_total_cells']
na_by = mv['na_by_col']
below = mv['below_lod_by_col']
n_ind = mv['indicator_cols_5_95']['n']

fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.2), gridspec_kw={'width_ratios': [1, 1.25]})
set_paper_placement(fig)

# ── (a) 真正缺失（NA）各列单元格数 ─────────────────────
ax = axes[0]
items = sorted(na_by.items(), key=lambda kv: kv[1])
names = [k for k, _ in items]; cnt = [v for _, v in items]
yy = np.arange(len(names))
ax.barh(yy, cnt, color=PALETTE[2], edgecolor='white', linewidth=0.6)
for i, v in enumerate(cnt):
    ax.text(v + 0.2, i, str(v), va='center', fontsize=7, color='#333')
ax.set_yticks(yy); ax.set_yticklabels(names, fontsize=7)
ax.set_xlabel('该列 NA 单元格数（共 250 行）')
ax.set_xlim(0, max(cnt) * 1.25)
declutter_axes(ax, grid_axis='x')

# ── (b) 未检出率最高的 15 列 ───────────────────────────
ax = axes[1]
bl = [(c, v['min_rate'] * 100) for c, v in below.items()]
bl = sorted(bl, key=lambda z: z[1], reverse=True)[:15][::-1]
bn = [c for c, _ in bl]; br = [r for _, r in bl]
yy = np.arange(len(bn))
colors = [PALETTE[1] if 5 <= r <= 95 else PALETTE[7] for r in br]
ax.barh(yy, br, color=colors, edgecolor='white', linewidth=0.5)
ax.axvline(5, color='#B23A2E', ls='--', lw=1.0)
ax.axvline(95, color='#B23A2E', ls='--', lw=1.0)
for i, r in enumerate(br):
    ax.text(r + 0.6, i, f'{r:.0f}%', va='center', fontsize=6.4, color='#333')
ax.set_yticks(yy); ax.set_yticklabels([c if len(c) <= 16 else c[:15] + '…' for c in bn], fontsize=6.6)
ax.set_xlabel('未检出率（%，取值=列内检出限编码）')
ax.set_xlim(0, max(br) * 1.18)
declutter_axes(ax, grid_axis='x')

fig.tight_layout()
save_fig(fig, 'figures/fig_prep_belowlod.png')
print('fig_prep_belowlod done; NA=%d indicator_cols=%d' % (na_total, n_ind))
