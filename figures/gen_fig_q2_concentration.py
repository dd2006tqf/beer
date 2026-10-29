# -*- coding: utf-8 -*-
"""fig_q2_concentration —— Top-3 归因的席位集中度与来源构成

左：150 个 Top-3 席位按化合物计数排序的帕累托曲线（前 4 个化合物占 32%）；
右：席位按化合物来源（酵母/酒花/麦芽/其他/香料）的构成与感官维期望来源对比。

相比原来的"四组消融柱状图"（四个数字），这张图回答两个更实质的问题：
归因是否被少数化合物垄断、来源分布是否与酿造机理相符。

版式参考 ModelViz 09_REL_011（横向条形 + 关联矩阵）与 02_CMP_006（百分比堆叠）。
数据源：figures/problem_2_results.json::per_dim。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from _figbase import load, PALETTE, save_fig, declutter_axes, dim_zh, tag_panels

P2 = load('problem_2_results.json')
PD = P2['per_dim']
D = chr(36)

plt.rcParams.update({
    'axes.labelsize': 7.6,
    'xtick.labelsize': 6.8,
    'ytick.labelsize': 6.6,
    'legend.fontsize': 6.6,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'xtick.color': '#4B5563',
    'ytick.color': '#4B5563',
    'axes.unicode_minus': False,
    'mathtext.fontset': 'dejavusans',
})

BLUE, ORANGE, RED, GREEN = PALETTE[0], PALETTE[1], PALETTE[2], PALETTE[3]

cnt = Counter()
for v in PD.values():
    cnt.update(v['top3'])
total = sum(cnt.values())
items = cnt.most_common()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.9, 2.95),
                               gridspec_kw={'width_ratios': [1.35, 1.0], 'wspace': 0.34},
                               layout='constrained')

# ── 左：帕累托曲线（累计席位占比）──────────────────────────
cum = np.cumsum([c for _, c in items]) / total * 100
x = np.arange(1, len(cum) + 1)
ax1.plot(x, cum, color=BLUE, lw=1.4, zorder=3)
ax1.fill_between(x, 0, cum, color=BLUE, alpha=0.10, zorder=2)
ax1.axvline(4, color=ORANGE, lw=0.9, ls=(0, (4, 2)), zorder=4)
ax1.plot([4], [cum[3]], 'o', color=ORANGE, ms=4, zorder=5)
ax1.axhline(80, color='#D1D5DB', lw=0.7, ls=':', zorder=1)
ax1.text(len(x) - 1, 82, '80%', fontsize=6.0, color='#6B7280', ha='right')
ax1.set_xlim(0.5, len(x) + 0.5)
ax1.set_ylim(0, 102)
ax1.set_xlabel('按席位降序排列的化合物数（共 %d 个）' % len(items))
ax1.set_ylabel('累计席位占比（%）')
ax1.set_yticks([0, 25, 50, 75, 100])
declutter_axes(ax1, 'both')

# ── 右：席位来源构成（水平百分比条）────────────────────────
def norm(s):
    s = (s or '').strip().lower()
    if s.startswith('yeast'):
        return 'Yeast'
    if s.startswith('hops'):
        return 'Hops'
    if s.startswith('malt'):
        return 'Malt'
    if s.startswith('spice'):
        return 'Spices'
    if s.startswith('wild'):
        return 'Wild flora'
    return 'Others'

top_src = Counter()
for v in PD.values():
    for s in v['source_category']:
        top_src[norm(s)] += 1
exp_src = Counter()
for v in PD.values():
    exp_src[norm(v.get('expected_source'))] += 1

order = ['Yeast', 'Hops', 'Malt', 'Wild flora', 'Spices', 'Others']
cn = {'Yeast': '酵母代谢', 'Hops': '酒花', 'Malt': '麦芽',
      'Wild flora': '野生菌群', 'Spices': '香料', 'Others': '其他'}
a = np.array([top_src.get(k, 0) for k in order], float) / total * 100
b = np.array([exp_src.get(k, 0) for k in order], float) / sum(exp_src.values()) * 100

yy = np.arange(len(order))[::-1]
h = 0.34
ax2.barh(yy + h / 2, a, height=h, color=BLUE, edgecolor='white',
         linewidth=0.5, label='Top-3 席位', zorder=3)
ax2.barh(yy - h / 2, b, height=h, color=ORANGE, alpha=0.85, edgecolor='white',
         linewidth=0.5, label='感官维期望', zorder=3)
ax2.set_yticks(yy)
ax2.set_yticklabels([cn[k] for k in order], fontsize=7.0)
ax2.set_xlim(0, 70)
ax2.set_xlabel('占比（%）')
for i, k in enumerate(order):
    if a[i] >= 1.5:
        ax2.text(a[i] + 1.0, yy[i] + h / 2, '%.0f' % a[i], va='center',
                 fontsize=6.0, color=BLUE)
    if b[i] >= 1.5:
        ax2.text(b[i] + 1.0, yy[i] - h / 2, '%.0f' % b[i], va='center',
                 fontsize=6.0, color='#B45309')
ax2.legend(loc='lower right', frameon=False, handlelength=1.2,
           borderaxespad=0.2, labelspacing=0.3)
declutter_axes(ax2, 'x')

tag_panels([ax1, ax2])
save_fig(fig, 'figures/fig_q2_concentration.png')
print('top4 share %.1f%% | distinct %d | yeast %.0f%%' % (cum[3], len(items), a[0]))
