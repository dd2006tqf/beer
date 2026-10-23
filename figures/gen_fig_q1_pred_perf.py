# -*- coding: utf-8 -*-
"""fig_q1_pred_perf — 问题一：50 个感官维交叉验证 QWK 排序（棒棒糖图，双列布局）
按 QWK 降序排列全部 50 维，茎色随 QWK 渐变；虚线为全维均值 QWK。
数据源：problem_1_results.json::fig_data.qwk_ranked（[name, qwk] ×50）、summary.mean_qwk_main。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import colorsys
from _figbase import P1, PALETTE, COLORS, save_fig, set_paper_placement, declutter_axes, dim_zh, panel

ranked = P1['fig_data']['qwk_ranked']           # 已降序
mean_qwk = P1['summary']['mean_qwk_main']
names = [r[0] for r in ranked]
vals = [r[1] for r in ranked]
n = len(names)

vmin, vmax = min(vals), max(vals)
rng = (vmax - vmin) or 1


def grad(c1, c2, t):
    r1, g1, b1 = mc.to_rgb(c1); r2, g2, b2 = mc.to_rgb(c2)
    h1, l1, s1 = colorsys.rgb_to_hls(r1, g1, b1); h2, l2, s2 = colorsys.rgb_to_hls(r2, g2, b2)
    if abs(h2 - h1) > 0.5:
        h1, h2 = (h1 + 1, h2) if h1 < h2 else (h1, h2 + 1)
    return colorsys.hls_to_rgb((h1 + (h2 - h1) * t) % 1, l1 + (l2 - l1) * t, s1 + (s2 - s1) * t)


ctop, cbot = PALETTE[0], PALETTE[1]
half = (n + 1) // 2
fig, axes = plt.subplots(1, 2, figsize=(6.8, 5.6))
set_paper_placement(fig, width_fraction=0.98)

for col, ax in enumerate(axes):
    idx = range(col * half, min((col + 1) * half, n))
    sub = list(idx)
    yy = np.arange(len(sub))[::-1]
    ax.axvline(mean_qwk, color=COLORS['ref_line'], ls=':', lw=1.0, alpha=0.6, zorder=1,
               label=f'全维均值 {mean_qwk:.3f}' if col == 0 else None)
    for k, gi in enumerate(sub):
        t = (vals[gi] - vmin) / rng
        c = grad(ctop, cbot, 1 - t)
        ax.hlines(yy[k], 0, vals[gi], color=c, lw=1.3 + 1.8 * t, zorder=2)
        ax.scatter(vals[gi], yy[k], s=22 + 26 * t, color=c, edgecolors='white',
                   linewidths=0.5, zorder=3)
    ax.set_yticks(yy)
    ax.set_yticklabels([names[i] if len(names[i]) <= 15 else names[i][:14] + '…' for i in sub],
                       fontsize=6.6)
    ax.set_xlabel('交叉验证 QWK')
    ax.set_xlim(0, vmax * 1.16)
    declutter_axes(ax, grid_axis='x')
    if col == 0:
        ax.legend(loc='lower right', fontsize=7, framealpha=0.9)

fig.tight_layout()
save_fig(fig, 'figures/fig_q1_pred_perf.png')
print('fig_q1_pred_perf done; n=%d mean=%.4f' % (n, mean_qwk))
