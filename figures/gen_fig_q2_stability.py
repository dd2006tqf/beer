# -*- coding: utf-8 -*-
"""fig_q2_stability —— 两个稳定性口径各自的分布

左：50 维 Top-1 化合物在 500 次 bootstrap 下的入选频率分布；
右：同一 50 维的跨方法 Jaccard 系数分布，竖线为 10 万次随机抽取的基线。

原版把两个量画在同一横轴的点阵里，但入选频率高度饱和（47/50 恰为 1.000），
退化成一条竖线上的散点，信息量很低。改成分布直方图后可以直接读出：
bootstrap 口径几乎满分，而跨方法一致性虽为随机基线的 21.7 倍，绝对水平仍偏低
（均值 0.186、中位 0.167）。两个口径"一高一低"正是本节要说明的结论。

版式参考 ModelViz 04_DIS_001（组合箱线）与 04_DIS_002（山脊分布）。
数据源：figures/problem_2_results.json::fig_data.top1_freq_ranked、random_jaccard_baseline。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import P2, save_fig, declutter_axes

rk = P2['fig_data']['top1_freq_ranked']
base = P2.get('random_jaccard_baseline', {})
nb = P2['summary']['n_bootstrap']
freq = np.array([r[1] for r in rk])
jac = np.array([r[2] for r in rk])
base_mean = base.get('mean', 0.008585)

plt.rcParams.update({
    'axes.labelsize': 8.0,
    'xtick.labelsize': 7.0,
    'ytick.labelsize': 7.0,
    'legend.fontsize': 6.8,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

BLUE, ORANGE, RED = '#2E5C8A', '#E8833A', '#C0392B'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.9, 2.85),
                               gridspec_kw={'width_ratios': [1.0, 1.18], 'wspace': 0.38},
                               layout='constrained')

# ── 左：bootstrap 入选频率分布 ─────────────────────────────
bins1 = np.arange(0.70, 1.021, 0.02)
ax1.hist(freq, bins=bins1, color=BLUE, alpha=0.85, edgecolor='white',
         linewidth=0.5, zorder=3)
n_full = int((freq >= 0.9999).sum())
ax1.annotate('%d/%d 维恰为 1.000' % (n_full, len(freq)),
             xy=(0.99, n_full), xytext=(0.80, n_full * 0.86),
             fontsize=6.6, color='#374151',
             arrowprops=dict(arrowstyle='-', lw=0.6, color='#9CA3AF'))
ax1.set_xlim(0.69, 1.03)
ax1.set_ylim(0, n_full * 1.18)
ax1.set_xticks([0.7, 0.8, 0.9, 1.0])
ax1.set_xlabel('Top-1 bootstrap 入选频率')
ax1.set_ylabel('维度数')
declutter_axes(ax1, 'both')

# ── 右：跨方法 Jaccard 分布 ────────────────────────────────
bins2 = np.arange(0, 0.72, 0.03)
ax2.hist(jac, bins=bins2, color=ORANGE, alpha=0.85, edgecolor='white',
         linewidth=0.5, zorder=3)
ax2.axvline(base_mean, color='#6B7280', lw=0.9, ls=(0, (4, 3)), zorder=4)
ax2.axvline(jac.mean(), color=RED, lw=1.0, zorder=4)
ax2.set_xlim(0, 0.72)
ax2.set_xlabel('跨方法 Jaccard 系数')
ax2.set_ylabel('维度数')
ax2.set_xticks([0, 0.2, 0.4, 0.6])
declutter_axes(ax2, 'both')
ax2.annotate('随机基线\n%.3f' % base_mean, xy=(base_mean, ax2.get_ylim()[1] * 0.62),
             xytext=(0.055, ax2.get_ylim()[1] * 0.74), fontsize=6.4,
             color='#4B5563',
             arrowprops=dict(arrowstyle='-', lw=0.6, color='#9CA3AF'))
ax2.annotate('均值 %.3f\n（随机基线 %.1f 倍）' % (jac.mean(), jac.mean() / base_mean),
             xy=(jac.mean(), ax2.get_ylim()[1] * 0.30),
             xytext=(0.30, ax2.get_ylim()[1] * 0.55), fontsize=6.4, color=RED,
             arrowprops=dict(arrowstyle='-', lw=0.6, color='#D9A0A0'))

fig.legend(handles=[
    Line2D([], [], marker='s', ls='', color=BLUE, markersize=6, label='bootstrap 入选频率'),
    Line2D([], [], marker='s', ls='', color=ORANGE, markersize=6, label='跨方法 Jaccard'),
], loc='outside lower center', ncol=2, frameon=False, handletextpad=0.45,
    columnspacing=1.6, borderaxespad=0.1)

save_fig(fig, 'figures/fig_q2_stability.png')
print('done; full=%d jac_mean=%.3f jac_med=%.3f' % (n_full, jac.mean(), np.median(jac)))
