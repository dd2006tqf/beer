# -*- coding: utf-8 -*-
"""fig_prep_belowlod —— 未检出（左删失）与真实缺失的区分

左：9 个含真实缺失列（NA）的单元格数，全表共 73 个 NA，集中在少数列；
右：未检出率最高的 15 列，虚线标出 5% 与 95% 两条建指示列的门槛，
     落在两线之间（共 102 列）才建二值指示变量。

版式约定：子图不写标题、不加角标，含义由论文正文说明；
画布按最终 0.94 版心宽（5.9 in）1:1 设定，图内字号即纸面字号。

参考模板（ModelViz）：09_REL_011 横向条形 + 关联矩阵、02_CMP_005 条形+数值标注。
数据源：figures/supp_preprocess.json::missing_vs_belowlod。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import load, PALETTE, save_fig, declutter_axes

mv = load('supp_preprocess.json')['missing_vs_belowlod']
na_total = mv['na_total_cells']
na_by = mv['na_by_col']
below = mv['below_lod_by_col']
n_ind = mv['indicator_cols_5_95']['n']

plt.rcParams.update({
    'axes.labelsize': 8.0,
    'xtick.labelsize': 7.0,
    'ytick.labelsize': 7.0,
    'legend.fontsize': 6.9,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.9, 3.45),
                               gridspec_kw={'width_ratios': [1.0, 1.28], 'wspace': 0.46},
                               layout='constrained')

# ── 左：真实缺失（NA）──────────────────────────────────────
items = sorted(na_by.items(), key=lambda kv: kv[1])
names = [k for k, _ in items]
cnt = np.array([v for _, v in items], float)
yy = np.arange(len(names))
ax1.barh(yy, cnt, height=0.62, color=PALETTE[2], edgecolor='white',
         linewidth=0.6, zorder=3)
for i, v in enumerate(cnt):
    ax1.text(v + max(cnt) * 0.03, i, '%d' % v, va='center', fontsize=6.8,
             color='#374151')
ax1.set_yticks(yy)
ax1.set_yticklabels([n if len(n) <= 15 else n[:14] + '…' for n in names],
                    fontsize=6.7)
ax1.set_xlabel('该列 NA 单元格数（共 %d 个）' % na_total)
ax1.set_xlim(0, max(cnt) * 1.28)
ax1.set_ylim(-0.7, len(names) - 0.3)
declutter_axes(ax1, 'x')

# ── 右：未检出率最高的 15 列 ───────────────────────────────
bl = [(c, v['min_rate'] * 100) for c, v in below.items()]
bl = sorted(bl, key=lambda z: z[1], reverse=True)[:15][::-1]
bn = [c for c, _ in bl]
br = np.array([r for _, r in bl])
yy2 = np.arange(len(bn))
inside = (br >= 5) & (br <= 95)
colors = [PALETTE[1] if ok else '#B9C0C9' for ok in inside]
ax2.barh(yy2, br, height=0.60, color=colors, edgecolor='white',
         linewidth=0.5, zorder=3)
for i, r in enumerate(br):
    ax2.text(r + 1.2, i, '%.0f%%' % r, va='center', fontsize=6.3, color='#4B5563')
ax2.axvline(5, color='#B23A2E', lw=0.9, ls=(0, (4, 2)), zorder=4)
ax2.axvline(95, color='#B23A2E', lw=0.9, ls=(0, (4, 2)), zorder=4)
ax2.set_yticks(yy2)
ax2.set_yticklabels([c if len(c) <= 16 else c[:15] + '…' for c in bn], fontsize=6.6)
ax2.set_xlabel('未检出率（%）')
ax2.set_xlim(0, 104)
ax2.set_ylim(-0.7, len(bn) - 0.3)
declutter_axes(ax2, 'x')
ax2.legend(handles=[
    Line2D([], [], marker='s', ls='', color=PALETTE[1], markersize=6,
           label='建指示列（5%%–95%%，共 %d 列）' % n_ind),
    Line2D([], [], marker='s', ls='', color='#B9C0C9', markersize=6,
           label='不建（过稀或过密）'),
    Line2D([], [], color='#B23A2E', lw=0.9, ls=(0, (4, 2)), label='5% / 95% 门槛'),
], loc='upper center', bbox_to_anchor=(0.5, -0.30), ncol=3, frameon=False,
    handletextpad=0.45, columnspacing=1.2, borderaxespad=0.0, labelspacing=0.3)

save_fig(fig, 'figures/fig_prep_belowlod.png')
print('done; NA=%d indicator_cols=%d' % (na_total, n_ind))
