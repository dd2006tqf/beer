# -*- coding: utf-8 -*-
"""fig_prep_kaggle —— Kaggle 公开啤酒集作为外部旁证（不进入建模）

左：两库 ABV 密度曲线（Kaggle 5558 款 vs 本文 250 款），宏观区间一致；
右：16 个可比风格的 ABV 区间对照，Kaggle P5–P95 淡带、IQR 实带、中位刻度，
     本文实测点为实心圆。跨风格排序 Spearman ρ=0.84，14/16 落在 90% 区间。

版式约定：子图不写标题、不加角标，含义由论文正文说明；
画布按最终 0.94 版心宽（5.9 in）1:1 设定。

参考模板（ModelViz）：04_DIS_002 山脊/密度分布 + 09_REL_011 区间条形。
数据源：_tmp/kaggle/extracted/beer_data_set.csv、user_data/1.csv、figures/supp_kaggle.json。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import gaussian_kde
from _figbase import save_fig, declutter_axes, tag_panels
from _utils.plot_utils import ROOT

k = pd.read_csv(os.path.join(ROOT, '_tmp/kaggle/extracted/beer_data_set.csv'))
ka = k[(k['ABV'] >= 0.1) & (k['ABV'] <= 20)]
c = pd.read_csv(os.path.join(ROOT, 'user_data/1.csv'))
eth = [col for col in c.columns if 'ethanol' in col.lower()][0]
loc_abv = 10 ** c[eth]
res = json.load(open(os.path.join(ROOT, 'figures', 'supp_kaggle.json'), encoding='utf-8'))
mapping = res['mapping']

plt.rcParams.update({
    'axes.labelsize': 8.0,
    'xtick.labelsize': 7.0,
    'ytick.labelsize': 7.0,
    'legend.fontsize': 6.8,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

BLUE, ORANGE = '#2E5C8A', '#E8833A'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.9, 3.5),
                               gridspec_kw={'width_ratios': [1.0, 1.32], 'wspace': 0.52},
                               layout='constrained')

# ── 左：ABV 密度 ───────────────────────────────────────────
xx = np.linspace(0, 12, 300)
for data, col, lab in [(ka['ABV'].values, BLUE, 'Kaggle（5558 款）'),
                       (loc_abv.values, ORANGE, '本文（250 款）')]:
    d = data[np.isfinite(data)]
    kde = gaussian_kde(d, bw_method=0.18)
    ax1.fill_between(xx, kde(xx), color=col, alpha=0.16, zorder=2)
    ax1.plot(xx, kde(xx), color=col, lw=1.5, label=lab, zorder=3)
ax1.set_xlabel('ABV（% vol）')
ax1.set_ylabel('密度')
ax1.set_xlim(0, 12)
ax1.set_ylim(bottom=0)
ax1.legend(loc='lower right', bbox_to_anchor=(1.0, 1.02), frameon=False,
           handlelength=1.4, borderaxespad=0.0, labelspacing=0.3)
declutter_axes(ax1, 'both')

# ── 右：16 风格区间 ────────────────────────────────────────
items = sorted(mapping.items(), key=lambda kv: kv[1]['local_abv'])
for i, (ls, m) in enumerate(items):
    f5 = m['kaggle_abv_five']
    ax2.hlines(i, f5[0], f5[4], color=BLUE, lw=5.5, alpha=0.18, zorder=2)
    ax2.hlines(i, f5[1], f5[3], color=BLUE, lw=3.4, alpha=0.42, zorder=3)
    ax2.plot(f5[2], i, marker='|', color='#16324C', ms=7, mew=1.3, zorder=4)
    col = BLUE if m['abv_hit_iqr'] else ('#7FA8CF' if m['abv_hit_p95'] else ORANGE)
    ax2.scatter(m['local_abv'], i, s=26, color=col, edgecolor='white',
                linewidth=0.5, zorder=5)
ax2.set_yticks(range(len(items)))
ax2.set_yticklabels([m['zh'] for _, m in items], fontsize=6.8)
ax2.set_xlabel('ABV（% vol）')
n95 = sum(m['abv_hit_p95'] for m in mapping.values())
ax2.set_xlim(0, 13.5)
ax2.set_ylim(-0.7, len(items) - 0.3)
declutter_axes(ax2, 'x')

tag_panels([ax1, ax2])
save_fig(fig, 'figures/fig_prep_kaggle.png')
print('done; rho=%.2f p95=%d/16' % (res['abv_spearman'], n95))
