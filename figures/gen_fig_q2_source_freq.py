# -*- coding: utf-8 -*-
"""fig_q2_source_freq — 各来源类别 Top3 化合物的 bootstrap 入选频率分布（小提琴+散点）
反映不同来源类别化合物被 500 次重采样选入 Top3 的稳定程度。
数据源：problem_2_results.json::fig_data.freq_by_source。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P2, save_fig, set_paper_placement, declutter_axes

fd = P2['fig_data']['freq_by_source']
zh = {'Yeast': '酵母酯醇', 'Hops': '酒花萜类', 'Malt': '麦芽',
      'Spices': '香料', 'Others': '其他', 'Wild flora': '野生菌群'}
src_color = {'Yeast': '#2E5C8A', 'Hops': '#3E8E5A', 'Malt': '#D4A017',
             'Spices': '#7D5BA6', 'Others': '#6C7A89', 'Wild flora': '#2A9D8F'}
order = ['Yeast', 'Hops', 'Malt', 'Others', 'Spices']
order = [k for k in order if k in fd]
data = [np.array(fd[k]) for k in order]
labels = [f'{zh[k]}\n(n={len(fd[k])})' for k in order]

rng = np.random.default_rng(42)
fig, ax = plt.subplots(figsize=(8.0, 4.2))
set_paper_placement(fig)
parts = ax.violinplot(data, positions=range(1, len(order) + 1),
                      showmeans=False, showmedians=True, showextrema=False, widths=0.85)
for i, body in enumerate(parts['bodies']):
    body.set_facecolor(src_color[order[i]]); body.set_alpha(0.25)
    body.set_edgecolor(src_color[order[i]])
parts['cmedians'].set_color('#444'); parts['cmedians'].set_linewidth(1.4)
for i, (k, vals) in enumerate(zip(order, data)):
    jitter = rng.uniform(-0.12, 0.12, size=len(vals))
    ax.scatter(np.full(len(vals), i + 1) + jitter, vals, s=16,
               color=src_color[k], alpha=0.7, edgecolor='white', linewidth=0.3, zorder=3)
    ax.text(i + 1, 0.05, f'中位 {np.median(vals):.2f}', ha='center',
            fontsize=7.2, color='#333')
ax.set_xticks(range(1, len(order) + 1)); ax.set_xticklabels(labels, fontsize=9)
ax.set_ylabel('Bootstrap 入选频率（500 次重采样）')
ax.set_ylim(0, 1.06)
declutter_axes(ax, grid_axis='y')
fig.tight_layout()
save_fig(fig, 'figures/fig_q2_source_freq.png')
print('fig_q2_source_freq done; groups=%d' % len(order))
