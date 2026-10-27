# -*- coding: utf-8 -*-
"""fig_q1_sig —— 主模型相对三类基线的配对 bootstrap 显著性

对已有折外预测做 2000 次配对重采样（同一批样本同时重算主模型与基线），
每行给出 50 维平均 QWK 差值 Δ 的 95% 百分位区间与点估计；跨零者为不显著。
右侧标注 Δ、区间与「主模型更优的重采样比例 π」。

版式参考 ModelViz 09_REL_011（差值条形 + 参考线）。
数据源：submission/q1_oof_predictions.csv（problem1.py 落盘的折外预测）。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import save_fig
from _utils.plot_utils import ROOT

res = json.load(open(os.path.join(ROOT, '_tmp', 'q1_bootstrap_sig.json'), encoding='utf-8'))
ORDER = ['knn', 'rf', 'enet']

plt.rcParams.update({
    'axes.labelsize': 8.0,
    'xtick.labelsize': 7.2,
    'ytick.labelsize': 7.6,
    'legend.fontsize': 6.8,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
    'mathtext.fontset': 'dejavusans',
})

SIG, NS = '#2E5C8A', '#B9C0C9'

fig, ax = plt.subplots(figsize=(5.9, 2.5), layout='constrained')
ys = np.arange(len(ORDER))[::-1]
for y, key in zip(ys, ORDER):
    r = res[key]
    sig = r['lo'] > 0 or r['hi'] < 0
    c = SIG if sig else NS
    ax.plot([r['lo'], r['hi']], [y, y], color=c, lw=2.6, solid_capstyle='round',
            zorder=3, alpha=0.9)
    ax.plot([r['lo'], r['lo']], [y - 0.12, y + 0.12], color=c, lw=1.1, zorder=3)
    ax.plot([r['hi'], r['hi']], [y - 0.12, y + 0.12], color=c, lw=1.1, zorder=3)
    ax.scatter([r['delta']], [y], s=42, color=c, edgecolor='white',
               linewidth=0.7, zorder=5)
    ax.text(max(r['hi'], 0) + 0.008, y,
            'Δ=%+.4f  [%.4f, %.4f]  π=%.2f'
            % (r['delta'], r['lo'], r['hi'], r['pi']),
            va='center', ha='left', fontsize=6.6,
            color='#1F2933' if sig else '#6B7280')
ax.axvline(0, color='#6B7280', lw=0.9, ls=(0, (4, 3)), zorder=2)

ax.set_yticks(ys)
ax.set_yticklabels([res[k]['name'] for k in ORDER], fontsize=7.6)
ax.set_xlabel('50 维平均 QWK 差值 Δ（主模型减基线）')
ax.set_xlim(-0.005, 0.20)
ax.set_ylim(-0.65, len(ORDER) - 0.35)
for s in ('top', 'right', 'left'):
    ax.spines[s].set_visible(False)
ax.tick_params(axis='y', length=0)
ax.grid(axis='x', color='#E5E7EB', lw=0.6, zorder=0)
ax.set_axisbelow(True)

fig.legend(handles=[
    Line2D([], [], color=SIG, lw=2.6, marker='o', ms=4.5, label='95% CI 不跨零（显著）'),
    Line2D([], [], color='#6B7280', lw=0.9, ls=(0, (4, 3)), label='Δ = 0'),
], loc='outside lower center', ncol=2, frameon=False, handletextpad=0.5,
   columnspacing=1.6, borderaxespad=0.1)

save_fig(fig, 'figures/fig_q1_sig.png')
for k in ORDER:
    r = res[k]
    print('%-12s Δ=%+.4f [%.4f, %.4f] π=%.3f' % (r['name'], r['delta'], r['lo'], r['hi'], r['pi']))
