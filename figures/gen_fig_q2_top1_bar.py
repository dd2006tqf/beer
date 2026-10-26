# -*- coding: utf-8 -*-
"""fig_q2_top1_bar — 问题二：每维 Top-1/2/3 化合物的 bootstrap 入选频率（三点图，三列）
横轴为 500 次 bootstrap 的入选频率 f_jp（化合物进入该维 Top-3 的比例），
每维三行分别给出第 1、2、3 位：第 1 位几乎全为 1（47/50 恰为 1.000），
差异体现在第 2、3 位。用点形与配色区分名次（与 fig_q2_stability 同一 PALETTE 色系），
不再用条形长度表达近乎饱和的量。
数据源：submission/q2_top3_compounds.csv（rank=1/2/3）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from _figbase import (P2, PALETTE, PALETTE_LIGHT, save_fig,
                      set_paper_placement, declutter_axes, dim_zh)
from _utils.plot_utils import ROOT

df = pd.read_csv(os.path.join(ROOT, 'submission', 'q2_top3_compounds.csv'))
piv = df.pivot(index='sensory_dim', columns='rank',
               values='bootstrap_select_freq')
piv['mean'] = piv.mean(axis=1)
piv = piv.sort_values('mean', ascending=False)

STYLE = {1: dict(marker='o', s=26, c=PALETTE[0], z=3, label='第 1 位'),
         2: dict(marker='s', s=18, c=PALETTE[1], z=2, label='第 2 位'),
         3: dict(marker='^', s=20, c=PALETTE_LIGHT[0], z=1, label='第 3 位')}

n = len(piv); per = (n + 2) // 3                 # 三列 17/17/16，压矮图高
n_full = int((piv[1] >= 0.9999).sum())
fig, axes = plt.subplots(1, 3, figsize=(6.9, 4.0), layout='constrained')
set_paper_placement(fig, width_fraction=0.98)

for col, ax in enumerate(axes):
    sub = piv.iloc[col * per:min((col + 1) * per, n)]
    yy = np.arange(len(sub))[::-1]
    for r in (3, 2, 1):
        st = STYLE[r]
        ax.scatter(sub[r].values, yy, marker=st['marker'], s=st['s'],
                   color=st['c'], edgecolors=st.get('edgecolors', 'white'),
                   linewidths=0.4, zorder=st['z'], label=st['label'])
    ax.set_yticks(yy)
    ax.set_yticklabels([dim_zh(d) for d in sub.index], fontsize=7.0)
    ax.set_xlim(0.30, 1.04)
    ax.set_ylim(-0.8, len(sub) - 0.2)
    ax.set_xticks([0.4, 0.6, 0.8, 1.0])
    ax.set_xlabel('bootstrap 入选频率')
    declutter_axes(ax, grid_axis='x')

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='outside lower center', ncol=3, fontsize=7.5,
           frameon=False, handletextpad=0.4, columnspacing=1.6)
save_fig(fig, 'figures/fig_q2_top1_bar.png')
print('fig_q2_top1_bar done; n=%d first_rank_eq_1=%d' % (n, n_full))
