# -*- coding: utf-8 -*-
"""fig_q3_profile_heat —— 三代表风格生成谱的 50 维感官画像热图

3 行（Tripel / Kriek / Lambic）× 50 列（感官维，按香气 15 / 风味 15 / 口感缺陷 20 分组），
格内为生成谱经问题一模型打分后的平均预测等级；列内用 0-6 等级做零中心色标，
故同一行内高低可比，跨行只看形状。

雷达图只能容纳 8-10 维，热图能一次展示 50 维完整画像：Tripel 醇厚与酒精高、
Kriek 酸与甜高、Lambic 酸次之但野味突出，且三者缺陷维均处于低位。

数据源：submission/q3_generated_profiles.csv 的 SENS_ 列。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from _figbase import save_fig, dim_zh
from _utils.plot_utils import ROOT

gen = pd.read_csv(os.path.join(ROOT, 'submission', 'q3_generated_profiles.csv'))
sens = [c[len('SENS_'):] for c in gen.columns if c.startswith('SENS_')]
A = [c for c in sens if c.startswith('A_')]
F = [c for c in sens if c.startswith('F_')]
X = [c for c in sens if not c.startswith(('A_', 'F_'))]
order = A + F + X
styles = ['Tripel', 'Kriek', 'Lambic']

M = np.zeros((len(styles), len(order)))
for i, s in enumerate(styles):
    sub = gen[(gen['style'] == s) & (gen['sample_type'] == 'generated')]
    for j, c in enumerate(order):
        M[i, j] = sub['SENS_' + c].mean()

plt.rcParams.update({
    'axes.labelsize': 7.4,
    'xtick.labelsize': 6.0,
    'ytick.labelsize': 8.4,
    'axes.unicode_minus': False,
})

fig, ax = plt.subplots(figsize=(5.9, 2.35), layout='constrained')
norm = TwoSlopeNorm(vmin=0, vcenter=3, vmax=6)
im = ax.imshow(M, cmap='RdBu_r', norm=norm, aspect='auto', interpolation='nearest')

ax.set_yticks(range(len(styles)))
ax.set_yticklabels(styles, fontsize=8.2)
ax.set_xticks(np.arange(len(order)))
labels = [dim_zh(c).replace('香·', '').replace('味·', '') for c in order]
ax.set_xticklabels(labels, rotation=62, ha='right', fontsize=5.6)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)

# 组间分隔线：A(15) | F(15) | X(20)
for x in (len(A) - 0.5, len(A) + len(F) - 0.5):
    ax.axvline(x, color='white', lw=1.6, zorder=4)
# 组名标在顶部（图内不写标题，用简短组名标定位）
for x0, x1, txt in ((0, len(A), '香气 Aroma'), (len(A), len(A) + len(F), '风味 Flavour'),
                    (len(A) + len(F), len(order), '口感 / 缺陷 / 总体')):
    ax.text((x0 + x1 - 1) / 2, -1.05, txt, ha='center', va='bottom',
            fontsize=6.8, color='#374151')

cb = fig.colorbar(im, ax=ax, fraction=0.020, pad=0.012)
cb.outline.set_visible(False)
cb.set_label('预测等级', fontsize=7.0)
cb.ax.tick_params(labelsize=6.4, length=2)
cb.set_ticks([0, 3, 6])

save_fig(fig, 'figures/fig_q3_profile_heat.png')
print('done; rows=%d cols=%d (A%d/F%d/X%d)' % (len(styles), len(order), len(A), len(F), len(X)))
print('Tripel 高值维:', [(dim_zh(order[j]), round(M[0, j], 1))
                      for j in np.argsort(-M[0])[:5]])
