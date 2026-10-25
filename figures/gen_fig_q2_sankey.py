# -*- coding: utf-8 -*-
"""fig_q2_sankey — 感官维度类别 → Top3 化合物来源类别 桑基（alluvial）
左：感官维度按其类别归属（Malt/Yeast/Hops/Wild flora/Others/Unknown）；
右：Top3 化合物在 8.xlsx 中标注的来源（origin_paper）；流宽 = 维度×化合物计数（共 150）。
直观呈现「一致/部分/不一致」的来源错配（如麦芽类维归因到酵母酯醇）。
数据源：problem_2_results.json::fig_data.sankey_cat_source。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from _figbase import P2, save_fig, set_paper_placement

rows = P2['fig_data']['sankey_cat_source']
zh = {'Yeast': '酵母酯醇', 'Hops': '酒花萜类', 'Malt': '麦芽', 'Spices': '香料',
      'Others': '其他', 'Wild flora': '野生菌群', 'Unknown': '未标注'}
color = {'Yeast': '#2E5C8A', 'Hops': '#3E8E5A', 'Malt': '#D4A017', 'Spices': '#7D5BA6',
         'Others': '#6C7A89', 'Wild flora': '#2A9D8F', 'Unknown': '#B5BAC1'}

left_cats = ['Yeast', 'Malt', 'Hops', 'Wild flora', 'Others', 'Unknown']
right_cats = ['Yeast', 'Hops', 'Malt', 'Spices', 'Others']
left_cats = [c for c in left_cats if any(r['sensory_category'] == c for r in rows)]
right_cats = [c for c in right_cats if any(r['compound_source'] == c for r in rows)]
total = sum(r['count'] for r in rows)
GAP, H0, BOT = 0.025, 0.90, 0.05

def layout(cats, key):
    tot = {c: sum(r['count'] for r in rows if r[key] == c) for c in cats}
    useg = H0 - GAP * (len(cats) - 1)
    pos, cur = {}, 1 - 0.04
    for c in cats:
        h = tot[c] / total * useg
        pos[c] = (cur - h, cur)
        cur -= h + GAP
    return pos, tot

lp, lt = layout(left_cats, 'sensory_category')
rp, rt = layout(right_cats, 'compound_source')
lcursor = {c: lp[c][1] for c in left_cats}
rcursor = {c: rp[c][1] for c in right_cats}

fig, ax = plt.subplots(figsize=(8.6, 5.4))
set_paper_placement(fig)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')
x0, x1 = 0.24, 0.76; mx = (x0 + x1) / 2

def band(yla, ylb, yra, yrb, fc):
    verts = [(x0, yla), (x0, ylb), (mx, ylb), (mx, yrb), (x1, yrb),
             (x1, yra), (mx, yra), (mx, yla), (x0, yla)]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
             Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=fc, edgecolor='none', alpha=0.28))

# 按右来源聚合排序，减少交叉
for r in sorted(rows, key=lambda z: (right_cats.index(z['compound_source']), -z['count'])):
    h = r['count'] / total * (H0 - GAP * 2)
    lc, rc = r['sensory_category'], r['compound_source']
    ylb = lcursor[lc]; yla = ylb - h; lcursor[lc] = yla
    yrb = rcursor[rc]; yra = yrb - h; rcursor[rc] = yra
    band(yla, ylb, yra, yrb, color[rc])

# 节点条 + 标签
for c in left_cats:
    a, b = lp[c]
    ax.add_patch(plt.Rectangle((x0 - 0.02, a), 0.02, b - a, color=color.get(c, '#999')))
    ax.text(x0 - 0.03, (a + b) / 2, f'{zh.get(c, c)} {lt[c]}', ha='right', va='center', fontsize=9)
for c in right_cats:
    a, b = rp[c]
    ax.add_patch(plt.Rectangle((x1, a), 0.02, b - a, color=color.get(c, '#999')))
    ax.text(x1 + 0.03, (a + b) / 2, f'{zh.get(c, c)} {rt[c]}', ha='left', va='center', fontsize=9)
ax.text(x0 - 0.02, 0.985, '感官维度类别', ha='center', va='top', fontsize=10, fontweight='bold')
ax.text(x1 + 0.02, 0.985, 'Top3 化合物来源', ha='center', va='top', fontsize=10, fontweight='bold')

fig.tight_layout()
save_fig(fig, 'figures/fig_q2_sankey.png')
print('fig_q2_sankey done; total=%d' % total)
