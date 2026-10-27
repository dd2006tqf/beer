# -*- coding: utf-8 -*-
"""fig_q2_evidence —— 条件增量与模块增量的二维证据图（A/B/C 分级）

横轴=条件增量（单独置换该化合物后预测的平均绝对变化），
纵轴=模块增量（置换其所在共表达社区的全部列后的变化），
点大小=bootstrap 入选频率，标签为该化合物缩写。
落在 y=0（模块增量为 0）上的点说明它只是模块内的可替代成员——
它的上榜来自模块整体信号，而非独立驱动；对角线附近则说明独立贡献显著。

数据源：_tmp/q2_evidence.json（TreeSHAP 模型上的置换实验）。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import PALETTE, save_fig
from _utils.plot_utils import ROOT

ev = json.load(open(os.path.join(ROOT, '_tmp', 'q2_evidence.json'), encoding='utf-8'))
plt.rcParams.update({
    'axes.labelsize': 7.4,
    'xtick.labelsize': 6.8,
    'ytick.labelsize': 6.8,
    'legend.fontsize': 6.4,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

fig, ax = plt.subplots(figsize=(5.4, 3.0), layout='constrained')
cond_all = [r['cond'] for d in ev.values() for r in d]
mod_all = [r['mod'] for d in ev.values() for r in d if r['mod'] is not None]
lim = max(max(cond_all), max(mod_all)) * 1.18
ax.plot([0, lim], [0, lim], color='#D1D5DB', lw=0.8, ls=(0, (4, 3)), zorder=1)
ax.axhline(0, color='#9CA3AF', lw=0.7, zorder=1)

# 按维度分色（只取四个代表维度避免拥挤）
SHOW = ['alcohol', 'bitternes', 'A_malt_all', 'F_esters_all']
cols = {d: PALETTE[i] for i, d in enumerate(SHOW)}
for d in SHOW:
    for r in ev.get(d, []):
        if r['mod'] is None:          # 该化合物所在社区无其他成员，模块增量不可定义
            ax.scatter(r['cond'], 0, s=18 + 70 * r['freq'], marker='X',
                       color=cols[d], alpha=0.85, edgecolor='white',
                       linewidth=0.5, zorder=4)
            short = r['compound'].replace('_', ' ')
            short = short if len(short) <= 13 else short[:12] + '…'
            ax.annotate(short + '（单点模块）', (r['cond'], 0), xytext=(3, 3),
                        textcoords='offset points', fontsize=6.0, color='#6B7280')
            continue
        ax.scatter(r['cond'], r['mod'], s=18 + 70 * r['freq'],
                   color=cols[d], alpha=0.8, edgecolor='white',
                   linewidth=0.5, zorder=3)
        short = r['compound'].replace('_', ' ')
        short = short if len(short) <= 13 else short[:12] + '…'
        ax.annotate(short, (r['cond'], r['mod']), xytext=(3, 3),
                    textcoords='offset points', fontsize=6.2, color='#4B5563')

ax.set_xlim(0, lim); ax.set_ylim(-lim * 0.03, lim)
ax.set_xlabel('条件增量（单独置换）')
ax.set_ylabel('模块增量（整社区置换）')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)

handles = [plt.Line2D([], [], marker='o', ls='', color=cols[d], markersize=6,
                      label=d.replace('_', ' ')) for d in SHOW]
fig.legend(handles=handles, loc='outside lower center', ncol=2, frameon=False,
           handletextpad=0.35, columnspacing=1.2, borderaxespad=0.05)

save_fig(fig, 'figures/fig_q2_evidence.png')
n0 = sum(1 for d in ev.values() for r in d if r['mod'] is not None and r['mod'] <= 1e-9)
tot = sum(1 for d in ev.values() for r in d if r['mod'] is not None)
print('done; %d/%d 个可定义模块增量的组合为 0' % (n0, tot))
