# -*- coding: utf-8 -*-
"""fig_prep_kaggle — Kaggle 公开集外部旁证（不进入建模）
(a) 两库整体 ABV 分布（Kaggle 5558 款网友库 vs 本文 250 款实验室谱），宏观区间一致；
(b) 16 个可比风格的 ABV：Kaggle P5–P95（淡带）、IQR（实带）、中位刻度，本文实测点（10**log10 还原）。
跨风格 ABV 排序 Spearman ρ=0.84，14/16 落在 Kaggle 90% 区间；本文为比利时小众风格，整体略强于全球中位。
数据源：_tmp/kaggle/extracted/beer_data_set.csv、user_data/1.csv、figures/supp_kaggle.json。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from _figbase import save_fig, set_paper_placement, declutter_axes
from _utils.plot_utils import ROOT

k = pd.read_csv(os.path.join(ROOT, '_tmp/kaggle/extracted/beer_data_set.csv'))
ka = k[(k['ABV'] >= 0.1) & (k['ABV'] <= 20)]
c = pd.read_csv(os.path.join(ROOT, 'user_data/1.csv'))
eth = [col for col in c.columns if 'ethanol' in col.lower()][0]
loc_abv = 10 ** c[eth]
res = json.load(open(os.path.join(ROOT, 'figures', 'supp_kaggle.json'), encoding='utf-8'))
mapping = res['mapping']

fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(12.4, 6.4),
                                 gridspec_kw={'width_ratios': [1.0, 1.35]})
set_paper_placement(fig)

# (a) 整体 ABV 分布
xx = np.linspace(0, 12, 300)
for data, col, lab in [(ka['ABV'].values, '#2E5C8A', 'Kaggle 网友库（5558 款 / 112 风格）'),
                       (loc_abv.values, '#E8833A', '本文（250 款 / 22 风格，比利时系）')]:
    d = data[np.isfinite(data)]
    kde = gaussian_kde(d, bw_method=0.18)
    ax_a.fill_between(xx, kde(xx), color=col, alpha=0.18)
    ax_a.plot(xx, kde(xx), color=col, lw=2.0, label=lab)
ax_a.set_xlabel('ABV（% vol）'); ax_a.set_ylabel('密度')
ax_a.set_title('(a) 两库整体酒精度分布区间一致', fontsize=11, fontweight='bold', loc='left')
ax_a.legend(loc='upper right', fontsize=8, framealpha=0.9)
declutter_axes(ax_a)

# (b) 16 风格 ABV 区间
items = sorted(mapping.items(), key=lambda kv: kv[1]['local_abv'])
for i, (ls, m) in enumerate(items):
    f5 = m['kaggle_abv_five']
    ax_b.hlines(i, f5[0], f5[4], color='#2E5C8A', lw=7, alpha=0.20, zorder=1)
    ax_b.hlines(i, f5[1], f5[3], color='#2E5C8A', lw=4, alpha=0.45, zorder=2)
    ax_b.plot(f5[2], i, marker='|', color='#1d3f5f', ms=9, mew=1.4, zorder=3)
    col = '#2E5C8A' if m['abv_hit_iqr'] else ('#7FA8CF' if m['abv_hit_p95'] else '#E8833A')
    ax_b.scatter(m['local_abv'], i, s=62, color=col, edgecolor='white',
                 linewidth=0.8, zorder=4)
ax_b.set_yticks(range(len(items)))
ax_b.set_yticklabels([m['zh'] for _, m in items], fontsize=8.6)
ax_b.set_xlabel('ABV（% vol）')
n95 = sum(m['abv_hit_p95'] for m in mapping.values())
ax_b.set_title(f"(b) 可比风格 ABV 对照：排序 ρ={res['abv_spearman']}，"
               f"{n95}/16 落在 Kaggle 90% 区间",
               fontsize=11, fontweight='bold', loc='left')
from matplotlib.lines import Line2D
handles = [
    Line2D([0], [0], color='#2E5C8A', lw=7, alpha=0.2, label='Kaggle P5–P95'),
    Line2D([0], [0], color='#2E5C8A', lw=4, alpha=0.45, label='Kaggle 四分位区间'),
    Line2D([0], [0], marker='|', color='#1d3f5f', ls='none', ms=11, label='Kaggle 中位'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#2E5C8A', markersize=9, label='本文实测（在 IQR）'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#7FA8CF', markersize=9, label='本文实测（在 90% 区间）'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor='#E8833A', markersize=9, label='本文实测（略超区间）'),
]
ax_b.legend(handles=handles, loc='lower right', fontsize=7.2, framealpha=0.95, ncol=2)
declutter_axes(ax_b, grid_axis='x')

fig.tight_layout()
save_fig(fig, 'figures/fig_prep_kaggle.png')
print('fig_prep_kaggle done; rho=%.2f p95=%d/16' % (res['abv_spearman'],
      round(res['abv_hit_p95'] * 16)))
