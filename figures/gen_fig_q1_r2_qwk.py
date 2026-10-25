# -*- coding: utf-8 -*-
"""fig_q1_r2_qwk — 50 个感官维的可预测性散点（x=折外 R², y=折外 QWK）
按 香气(A_)/风味(F_)/口感缺陷 分组着色；标注强信号维（酒精/苦味/酒体）与弱信号维（芫荽/丁香）。
数据源：problem_1_results.json::per_dim。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P1, PALETTE, save_fig, set_paper_placement, declutter_axes, dim_zh

pd = P1['per_dim']
groups = {'A_': ('香气维度', PALETTE[0]), 'F_': ('风味维度', PALETTE[1])}
other_color = PALETTE[7]
annot_strong = ['alcohol', 'bitternes', 'body', 'F_hops_all', 'lactic', 'acidity']
annot_weak = ['coriander', 'clove', 'A_esters_fruity']

fig, ax = plt.subplots(figsize=(8.0, 5.2))
set_paper_placement(fig)
pts = {'A_': [], 'F_': [], 'other': []}
for name, v in pd.items():
    r2 = v.get('r2_main'); q = v.get('qwk_main')
    if r2 is None or q is None:
        continue
    g = name[:2] if name[:2] in ('A_', 'F_') else 'other'
    pts[g].append((r2, q, name))
for g, (lab, col) in zip(['A_', 'F_'], [groups['A_'], groups['F_']]):
    xs = [p[0] for p in pts[g]]; ys = [p[1] for p in pts[g]]
    ax.scatter(xs, ys, s=46, color=col, alpha=0.78, edgecolor='white',
               linewidth=0.6, label=f'{lab}（n={len(xs)}）', zorder=3)
xs = [p[0] for p in pts['other']]; ys = [p[1] for p in pts['other']]
ax.scatter(xs, ys, s=46, color=other_color, alpha=0.78, edgecolor='white',
           linewidth=0.6, label=f'口感/缺陷维（n={len(xs)}）', zorder=3)

# 趋势线（全体）
allx = np.array([v.get('r2_main') for v in pd.values() if v.get('r2_main') is not None])
ally = np.array([v.get('qwk_main') for v in pd.values() if v.get('qwk_main') is not None])
b, a = np.polyfit(allx, ally, 1)
xx = np.linspace(allx.min(), allx.max(), 50)
ax.plot(xx, a + b * xx, '--', color='#888', lw=1.2, zorder=2, alpha=0.8)

offsets = {'body': (-10, 10), 'F_hops_all': (8, -12), 'alcohol': (6, 5), 'bitternes': (6, 5),
           'lactic': (6, 4), 'acidity': (6, 4), 'coriander': (-2, -13), 'clove': (-10, 6),
           'A_esters_fruity': (6, -4)}
for name in annot_strong + annot_weak:
    if name in pd:
        v = pd[name]
        dx, dy = offsets.get(name, (5, 5))
        ax.annotate(dim_zh(name), xy=(v['r2_main'], v['qwk_main']),
                    xytext=(dx, dy), textcoords='offset points', fontsize=7.6,
                    color='#B23A2E' if name in annot_strong else '#333',
                    fontweight='bold' if name in annot_strong else 'normal', zorder=6)
ax.set_xlabel('折外 R$^2$（连续预测对标准化分）')
ax.set_ylabel('折外 QWK（7 级）')
ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
declutter_axes(ax)
fig.tight_layout()
save_fig(fig, 'figures/fig_q1_r2_qwk.png')
print('fig_q1_r2_qwk done')
