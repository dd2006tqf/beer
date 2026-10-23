# -*- coding: utf-8 -*-
"""fig_q3_realvsgen — 问题三生成质量验证（2 panel，PCA 降维重叠）
化学谱 PCA 投影：真实样本 vs CVAE 生成样本，按三代表风格着色。
(a) 真实样本  (b) 生成样本；同一投影坐标系，看生成分布是否覆盖真实分布。
数据源：problem_3_results.json::fig_data.pca.{real, gen, explained_var}、summary.ks_distance_by_style。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P3, PALETTE, COLORS, save_fig, set_paper_placement, declutter_axes, panel

pca = P3['fig_data']['pca']
ev = pca['explained_var']
ks = P3['summary']['ks_distance_by_style']
real = pca['real']; gen = pca['gen']
styles = sorted({d['style'] for d in real} | {d['style'] for d in gen})
scol = {s: PALETTE[i % len(PALETTE)] for i, s in enumerate(styles)}

allx = [d['x'] for d in real + gen]; ally = [d['y'] for d in real + gen]
xlim = (min(allx), max(allx)); ylim = (min(ally), max(ally))
xp = (xlim[1] - xlim[0]) * 0.06; yp = (ylim[1] - ylim[0]) * 0.06

fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.6), sharex=True, sharey=True)
set_paper_placement(fig)

for ax, data, tag, title in [(axes[0], real, '(a)', '真实样本'),
                             (axes[1], gen, '(b)', '生成样本')]:
    for s in styles:
        xs = [d['x'] for d in data if d['style'] == s]
        ys = [d['y'] for d in data if d['style'] == s]
        if xs:
            ax.scatter(xs, ys, s=26, color=scol[s], alpha=0.8,
                       edgecolors='white', linewidths=0.4, label=s)
    ax.set_xlabel(f'PC1（{ev[0]*100:.1f}%）')
    ax.set_xlim(xlim[0] - xp, xlim[1] + xp); ax.set_ylim(ylim[0] - yp, ylim[1] + yp)
    declutter_axes(ax)
    panel(ax, f'{tag} {title}')
axes[0].set_ylabel(f'PC2（{ev[1]*100:.1f}%）')
axes[1].legend(loc='upper right', fontsize=7.2, framealpha=0.9,
               title='风格 (KS≈%.2f~%.2f)' % (min(ks.values()), max(ks.values())),
               title_fontsize=7)

fig.tight_layout()
save_fig(fig, 'figures/fig_q3_realvsgen.png')
print('fig_q3_realvsgen done; real=%d gen=%d' % (len(real), len(gen)))
