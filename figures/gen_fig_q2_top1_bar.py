# -*- coding: utf-8 -*-
"""fig_q2_top1_bar — 50 个感官维 Top1 化合物的 bootstrap 入选频率（双列条形）
替代稀疏 Top3 热图：每个感官维只显示其最稳定的 Top1 化合物，条尾标注化合物名与频率。
数据源：submission/q2_top3_compounds.csv（rank=1）、problem_2_results.json::summary。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P2, save_fig, set_paper_placement, declutter_axes, dim_zh
from _utils.plot_utils import ROOT

df = pd.read_csv(os.path.join(ROOT, 'submission', 'q2_top3_compounds.csv'))
t1 = df[df['rank'] == 1].copy().sort_values(
    'bootstrap_select_freq', ascending=False).reset_index(drop=True)
meanfreq = P2['summary']['mean_top1_select_freq']
n = len(t1); half = (n + 1) // 2

fig, axes = plt.subplots(1, 2, figsize=(10.2, 7.6))
set_paper_placement(fig)
for col, ax in enumerate(axes):
    sub = t1.iloc[col * half:min((col + 1) * half, n)]
    yy = np.arange(len(sub))[::-1]
    for k, (_, r) in enumerate(sub.iterrows()):
        f = r['bootstrap_select_freq']
        c = '#2E5C8A' if f >= 0.95 else ('#7FA8CF' if f >= 0.8 else '#E8833A')
        ax.barh(yy[k], max(f - 0.80, 0.001), left=0.80, color=c, zorder=3, height=0.62)
        nm = r['compound'] if len(r['compound']) <= 15 else r['compound'][:14] + '…'
        ax.text(1.008, yy[k], f'{nm}', va='center', ha='left', fontsize=6.6, color='#333')
    ax.set_yticks(yy)
    ax.set_yticklabels([dim_zh(d) for d in sub['sensory_dim']], fontsize=7.2)
    ax.set_xlim(0.80, 1.22)
    ax.set_xticks([0.80, 0.85, 0.90, 0.95, 1.00])
    ax.set_xlabel('Top1 入选频率（B=500）')
    declutter_axes(ax, grid_axis='x')
fig.tight_layout()
save_fig(fig, 'figures/fig_q2_top1_bar.png')
print('fig_q2_top1_bar done; n=%d mean=%.4f' % (n, meanfreq))
