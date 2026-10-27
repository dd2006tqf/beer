# -*- coding: utf-8 -*-
"""fig_q1_model_pair —— 主模型与三类基线的逐维配对对比（50 维）

每个感官维度一行，左端为基线 QWK、右端为主模型 QWK，连线颜色表示主模型
是否更优。相比"平均 QWK 柱状图"，配对图直接显示胜负维数与增益分布，
避免用单一均值掩盖"半数维度其实打平"的事实。

版式参考 ModelViz 09_REL_001（棒棒糖/哑铃）与 08_PRD_005（多面板评估）。
数据源：figures/problem_1_results.json::per_dim。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import load, PALETTE, save_fig, declutter_axes, dim_zh

P1 = load('problem_1_results.json')
PD = P1['per_dim']
D = chr(36)

plt.rcParams.update({
    'axes.labelsize': 7.6,
    'xtick.labelsize': 6.8,
    'ytick.labelsize': 6.4,
    'legend.fontsize': 6.6,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'xtick.color': '#4B5563',
    'ytick.color': '#4B5563',
    'axes.unicode_minus': False,
    'mathtext.fontset': 'dejavusans',
})

WIN = PALETTE[3]      # 主模型更优
LOSE = PALETTE[2]     # 基线更优
MAIN = PALETTE[0]
BASE = '#9CA3AF'

baselines = [
    ('knn_impute', 'KNN 插补 + LightGBM'),
    ('rf', '随机森林'),
    ('elasticnet', 'ElasticNet'),
]

fig, axes = plt.subplots(1, 3, figsize=(5.9, 4.35),
                         gridspec_kw={'width_ratios': [1, 1, 1.18], 'wspace': 0.10},
                         layout='constrained', sharey=True)

dims = list(PD.keys())
main_q = np.array([PD[k]['qwk_main'] for k in dims])
order = np.argsort(main_q)          # 按主模型 QWK 升序，自下而上
labels = [dim_zh(dims[i]) for i in order]

for ax, (key, title) in zip(axes, baselines):
    base_q = np.array([PD[k]['qwk_' + key] for k in dims])
    y = np.arange(len(dims))
    for pos, i in enumerate(order):
        b, m = base_q[i], main_q[i]
        ax.plot([b, m], [pos, pos], color=WIN if m >= b else LOSE,
                lw=0.9, alpha=0.55, zorder=2, solid_capstyle='round')
    ax.scatter(base_q[order], y, s=9, color=BASE, edgecolor='white',
               linewidth=0.25, zorder=3, label='基线')
    ax.scatter(main_q[order], y, s=11, color=MAIN, edgecolor='white',
               linewidth=0.3, zorder=4, label='主模型')
    ax.axvline(0, color='#D1D5DB', lw=0.7, zorder=1)
    ax.set_xlim(-0.06, 0.90)
    ax.set_ylim(-0.9, len(dims) - 0.1)
    n_win = int((main_q >= base_q).sum())
    ax.text(0.02, 0.985, '胜 %d/%d' % (n_win, len(dims)), transform=ax.transAxes,
            ha='left', va='top', fontsize=7.0,
            color=WIN if n_win > len(dims) / 2 else LOSE)
    ax.text(0.02, 0.935, '\u0394中位 %+.3f' % float(np.median(main_q - base_q)),
            transform=ax.transAxes, ha='left', va='top', fontsize=6.6, color='#4B5563')
    ax.set_title(title, fontsize=7.4, pad=4, color='#1F2933')
    ax.set_xlabel('折外 QWK')
    ax.set_xticks([0, 0.3, 0.6, 0.9])
    declutter_axes(ax, 'x')
    ax.tick_params(axis='y', length=0)

axes[0].set_yticks(np.arange(len(dims)))
axes[0].set_yticklabels(labels, fontsize=6.0)
for t in axes[0].get_yticklabels():
    t.set_color('#374151')

handles = [
    Line2D([], [], marker='o', ls='', color=BASE, markersize=4, label='基线'),
    Line2D([], [], marker='o', ls='', color=MAIN, markersize=4, label='主模型'),
    Line2D([], [], color=WIN, lw=1.6, label='主模型更优'),
    Line2D([], [], color=LOSE, lw=1.6, label='基线更优'),
]
fig.legend(handles=handles, loc='outside lower center', ncol=4, frameon=False,
           handletextpad=0.4, columnspacing=1.4, borderaxespad=0.1)

save_fig(fig, 'figures/fig_q1_model_pair.png')
print('saved; wins knn/rf/net =',
      int((main_q >= np.array([PD[k]['qwk_knn_impute'] for k in dims])).sum()),
      int((main_q >= np.array([PD[k]['qwk_rf'] for k in dims])).sum()),
      int((main_q >= np.array([PD[k]['qwk_elasticnet'] for k in dims])).sum()))
