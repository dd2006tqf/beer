# -*- coding: utf-8 -*-
"""fig_q1_r2_by_group —— 分组的 R² / ±1 准确率点阵（替代纯 QWK 条形）

50 个维度按香气 A_ / 风味 F_ / 口感缺陷 X 三组分行，行内按 R² 降序；
点大小=±1 准确率，组内红虚线为该组平均 R²。
一张图同时给出"连续值可解释程度（R²）"与"离散等级容错度（±1）"，
并与图 8 的 QWK 排序形成互补：R² 低不必然 QWK 低（分箱会压缩差异）。

数据源：figures/problem_1_results.json::per_dim。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P1, PALETTE, save_fig, dim_zh

PD = P1['per_dim']
plt.rcParams.update({
    'axes.labelsize': 7.6,
    'xtick.labelsize': 6.8,
    'ytick.labelsize': 6.2,
    'legend.fontsize': 6.6,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

GROUPS = [('A_', '香气 Aroma', PALETTE[0]),
          ('F_', '风味 Flavour', PALETTE[1]),
          (None, '口感 / 缺陷 / 总体', PALETTE[3])]

def pick(pre):
    if pre is None:
        return [k for k in PD if not k.startswith(('A_', 'F_'))]
    return [k for k in PD if k.startswith(pre)]

rows = []
for pre, name, col in GROUPS:
    ks = sorted(pick(pre), key=lambda k: -PD[k]['r2_main'])
    rows.append((name, col, ks))

n_total = sum(len(r[2]) for r in rows)
fig, axes = plt.subplots(1, 3, figsize=(6.6, 4.0),
                         gridspec_kw={'width_ratios': [15, 15, 20], 'wspace': 0.12},
                         layout='constrained', sharex=True)

for ax, (name, col, ks) in zip(axes, rows):
    yy = np.arange(len(ks))[::-1]
    r2 = np.array([PD[k]['r2_main'] for k in ks])
    acc = np.array([PD[k]['acc_within1_main'] for k in ks])
    ax.axvline(0, color='#D1D5DB', lw=0.8, zorder=1)
    ax.hlines(yy, 0, r2, color=col, lw=0.8, alpha=0.35, zorder=2)
    ax.scatter(r2, yy, s=8 + 120 * (acc - 0.4), color=col, alpha=0.85,
               edgecolor='white', linewidth=0.35, zorder=3)
    ax.axvline(r2.mean(), color='#C0392B', lw=0.9, ls=(0, (4, 3)), zorder=4)
    ax.set_yticks(yy)
    ax.set_yticklabels([dim_zh(k) for k in ks], fontsize=6.0)
    ax.set_xlim(-0.12, 0.78)
    ax.set_ylim(-0.8, len(ks) - 0.2)
    ax.set_xlabel(name, fontsize=7.0)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.tick_params(axis='x', length=2)
    ax.grid(axis='x', color='#EDEFF2', lw=0.55, zorder=0)
    ax.set_axisbelow(True)
    ax.text(r2.mean(), len(ks) - 0.45, '均值 %.3f' % r2.mean(),
            color='#C0392B', fontsize=6.0, ha='left', va='bottom')

fig.text(0.5, -0.030, '点大小 = ±1 级准确率（0.40–0.85）；红虚线 = 组内平均 R²',
         ha='center', fontsize=6.4, color='#6B7280')

save_fig(fig, 'figures/fig_q1_r2_by_group.png')
print('done; groups=%s' % [(r[0], len(r[2]), round(float(np.mean([PD[k]['r2_main'] for k in r[2]])), 3)) for r in rows])
