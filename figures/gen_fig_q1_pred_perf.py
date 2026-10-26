# -*- coding: utf-8 -*-
"""fig_q1_pred_perf — 问题一：50 个感官维交叉验证 QWK 排序（单色水平条，双列布局）
按 QWK 降序排列全部 50 维，统一用灰蓝单色；虚线为全维均值 QWK。
数据源：problem_1_results.json::fig_data.qwk_ranked（[name, qwk] ×50）、summary.mean_qwk_main。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P1, save_fig, set_paper_placement, declutter_axes, dim_zh

ranked = P1['fig_data']['qwk_ranked']           # 已降序
mean_qwk = P1['summary']['mean_qwk_main']
names = [r[0] for r in ranked]
vals = [r[1] for r in ranked]
n = len(names)

# 朴素配色：同一灰蓝、无点标记、无图例框，只靠条长表达差异
BAR = '#6E7B8B'
REF = '#333333'
half = (n + 1) // 2
fig, axes = plt.subplots(1, 2, figsize=(6.8, 5.6))
set_paper_placement(fig, width_fraction=0.98)

for col, ax in enumerate(axes):
    idx = range(col * half, min((col + 1) * half, n))
    sub = list(idx)
    yy = np.arange(len(sub))[::-1]
    ax.axvline(mean_qwk, color=REF, ls='--', lw=0.9, alpha=0.75, zorder=1)
    ax.barh(yy, [vals[gi] for gi in sub], height=0.62, color=BAR,
            edgecolor='none', zorder=2)
    ax.set_yticks(yy)
    ax.set_yticklabels([(dim_zh(names[i]) if len(dim_zh(names[i])) <= 9
                        else dim_zh(names[i])[:8] + '…') for i in sub],
                       fontsize=7.0)
    ax.set_xlabel('交叉验证 QWK')
    ax.set_xlim(0, max(vals) * 1.16)
    declutter_axes(ax, grid_axis='x')

# 均值线只在左图用文字标注，避免图例框
axes[0].text(mean_qwk + 0.012, len(range(half)) - 0.4,
             f'全维均值 {mean_qwk:.3f}', fontsize=7, color=REF,
             va='top', ha='left')

fig.tight_layout()
save_fig(fig, 'figures/fig_q1_pred_perf.png')
print('fig_q1_pred_perf done; n=%d mean=%.4f' % (n, mean_qwk))
