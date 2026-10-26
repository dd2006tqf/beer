# -*- coding: utf-8 -*-
"""fig_q2_stability — 问题二归因稳定性（single，点+置信区间）
全部 50 感官维按 Top-1 化合物 bootstrap 入选频率排序；误差棒=500 次重采样的
Wilson 95% 置信区间；点色=跨方法 Jaccard 一致性。入选频率高且 CI 窄=归因稳定。
数据源：problem_2_results.json::fig_data.top1_freq_ranked（[name, freq, jaccard]×50）、summary.n_bootstrap。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import (P2, PALETTE, PALETTE_LIGHT, COLORS, save_fig,
                      set_paper_placement, declutter_axes, dim_zh)

rk = P2['fig_data']['top1_freq_ranked']         # [name, top1_freq, jaccard]
nb = P2['summary']['n_bootstrap']
rk = sorted(rk, key=lambda r: r[1])             # 升序，从下往上递增
names = [r[0] for r in rk]
freq = np.array([r[1] for r in rk])
jac = np.array([r[2] for r in rk])


def wilson(p, n, z=1.96):
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - half, c + half


lo, hi = wilson(freq, nb)
n = len(names)
per = (n + 2) // 3                              # 三列 17/17/16，压矮图高
fig, axes = plt.subplots(1, 3, figsize=(6.9, 4.0), layout='constrained')
set_paper_placement(fig, width_fraction=0.98)
for col, ax in enumerate(axes):
    idx = list(range(col * per, min((col + 1) * per, n)))
    yy = np.arange(len(idx))
    for k, gi in enumerate(idx):
        ax.hlines(yy[k], lo[gi], hi[gi], color=PALETTE_LIGHT[0], lw=1.4, zorder=1)
    h1 = ax.scatter(freq[idx], yy, color=PALETTE[0], s=34, zorder=3,
                    edgecolors='white', linewidths=0.4)
    h2 = ax.scatter(jac[idx], yy, color=PALETTE[1], s=24, marker='s', zorder=2,
                    edgecolors='white', linewidths=0.3, alpha=0.9)
    ax.axvline(1.0, color=COLORS['ref_line'], ls=':', lw=0.9, alpha=0.5)
    ax.set_yticks(yy)
    ax.set_yticklabels([dim_zh(names[i]) if len(dim_zh(names[i])) <= 15
                        else names[i][:14] + '…' for i in idx], fontsize=7.0)
    ax.set_xlim(-0.03, 1.05)
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_ylim(-0.8, len(idx) - 0.2)
    declutter_axes(ax, grid_axis='x')
fig.legend([h1, h2], ['Top-1 入选频率', '跨方法 Jaccard'],
           loc='outside lower center', ncol=2, fontsize=7.5,
           frameon=False, handletextpad=0.4, columnspacing=1.6)
save_fig(fig, 'figures/fig_q2_stability.png')
print('fig_q2_stability done; n=%d nb=%d' % (len(names), nb))
