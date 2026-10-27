# -*- coding: utf-8 -*-
"""fig_q1_pred_perf —— 50 个感官维的交叉验证 QWK（排序点阵，按强弱分档着色）

横向棒棒糖按 QWK 降序排列 50 维，颜色按可预测性分档（强 / 中 / 弱），
右侧标出该维的 ±1 级准确率，使"预测准不准"与"错得多不多"在同一行可读。
虚线为全维均值。相比等长单色条形，分档配色能一眼看出强信号维只有少数。

版式参考 ModelViz 09_REL_001（棒棒糖）与 08_PRD_005（评估多面板）。
数据源：figures/problem_1_results.json::per_dim、fig_data.qwk_ranked。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import P1, save_fig, declutter_axes, dim_zh

PD = P1['per_dim']
ranked = P1['fig_data']['qwk_ranked']
mean_qwk = P1['summary']['mean_qwk_main']

plt.rcParams.update({
    'axes.labelsize': 8.0,
    'xtick.labelsize': 6.8,
    'ytick.labelsize': 6.6,
    'legend.fontsize': 6.8,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

STRONG, MID, WEAK = '#2E5C8A', '#7FA8CF', '#D8DEE6'
names = [r[0] for r in ranked]
vals = np.array([r[1] for r in ranked])
acc = np.array([PD[n]['acc_within1_main'] for n in names])

def tier(v):
    return STRONG if v >= 0.55 else (MID if v >= 0.30 else WEAK)

n = len(names)
half = (n + 1) // 2
fig, axes = plt.subplots(1, 2, figsize=(5.9, 4.55),
                         gridspec_kw={'wspace': 0.10},
                         layout='constrained', sharex=True)

for col, ax in enumerate(axes):
    lo = col * half
    hi = min((col + 1) * half, n)
    sub = list(range(lo, hi))
    yy = np.arange(len(sub))[::-1]
    for k, gi in enumerate(sub):
        c = tier(vals[gi])
        ax.hlines(yy[k], 0, vals[gi], color=c, lw=1.0, alpha=0.55, zorder=2)
        ax.scatter(vals[gi], yy[k], s=20, color=c, edgecolor='white',
                   linewidth=0.4, zorder=3)
    ax.axvline(mean_qwk, color='#9CA3AF', ls=(0, (4, 2)), lw=0.9, zorder=1)
    ax.set_yticks(yy)
    labels = []
    for gi in sub:
        z = dim_zh(names[gi])
        labels.append(z if len(z) <= 8 else z[:7] + '…')
    ax.set_yticklabels(labels, fontsize=6.4)
    ax.set_xlim(0, 0.92)
    ax.set_ylim(-0.8, len(sub) - 0.2)
    ax.set_xlabel('折外 QWK', fontsize=7.6)

# 右列再标 ±1 准确率
ax = axes[1]
lo = half
sub = list(range(lo, n))
yy = np.arange(len(sub))[::-1]
for k, gi in enumerate(sub):
    ax.text(0.905, yy[k], '%.0f' % (acc[gi] * 100), ha='right', va='center',
            fontsize=6.0, color='#4B5563')
ax.text(0.905, len(sub) + 0.15, '±1%', ha='right', va='bottom',
        fontsize=6.4, color='#1F2933')

fig.legend(handles=[
    Line2D([], [], marker='o', ls='', color=STRONG, markersize=5, label='强（QWK ≥ 0.55）'),
    Line2D([], [], marker='o', ls='', color=MID, markersize=5, label='中（0.30–0.55）'),
    Line2D([], [], marker='o', ls='', color=WEAK, markersize=5, label='弱（< 0.30）'),
], loc='outside lower center', ncol=3, frameon=False,
   handletextpad=0.4, columnspacing=1.6, borderaxespad=0.1)

save_fig(fig, 'figures/fig_q1_pred_perf.png')
strong = int((vals >= 0.55).sum()); weak = int((vals < 0.30).sum())
print('done; n=%d strong=%d weak=%d mean=%.4f' % (n, strong, weak, mean_qwk))
