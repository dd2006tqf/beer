# -*- coding: utf-8 -*-
"""fig_q1_model_bar — 多模型折外平均 QWK 对比（主模型 LightGBM 高亮）
另以文字标注各模型的折外 Spearman 与 ±1 级准确率（数据见 by_model）。
数据源：problem_1_results.json::summary.by_model。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P1, PALETTE, save_fig, set_paper_placement, declutter_axes

bm = P1['summary']['by_model']
order = [('lightgbm', 'LightGBM\n（本文主模型）'), ('knn_impute', 'KNN 插补'),
         ('rf', '随机森林'), ('elasticnet', '弹性网'), ('mean_baseline', '均值基线')]
names = [o[1] for o in order]
keys = [o[0] for o in order]
qwk = [bm[k]['mean_qwk'] for k in keys]
sp = [bm[k]['mean_spearman'] for k in keys]
a1 = [bm[k]['mean_acc_within1'] for k in keys]
colors = [PALETTE[0] if i == 0 else '#A9C3DD' if i < 4 else '#C9CED6' for i in range(len(keys))]

fig, ax = plt.subplots(figsize=(8.2, 4.4))
set_paper_placement(fig)
x = np.arange(len(names))
bars = ax.bar(x, qwk, color=colors, edgecolor='white', width=0.62, zorder=3)
for i, (q, s, a) in enumerate(zip(qwk, sp, a1)):
    ax.text(i, q + 0.012, f'{q:.3f}', ha='center', va='bottom', fontsize=10,
            fontweight='bold' if i == 0 else 'normal', color='#222')
    if q > 0.08:
        ax.text(i, q - 0.048, f'Spearman {s:.3f}\n±1级 {a:.1%}', ha='center', va='top',
                fontsize=7.2, color='#333')
    else:
        ax.text(i, q + 0.018, f'Spearman {s:.3f}　±1级 {a:.1%}', ha='center', va='bottom',
                fontsize=7.2, color='#333')
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=9)
ax.set_ylabel('折外平均 QWK（分层 5 折，50 维平均）')
ax.set_ylim(0, max(qwk) * 1.22)
declutter_axes(ax, grid_axis='y')
fig.tight_layout()
save_fig(fig, 'figures/fig_q1_model_bar.png')
print('fig_q1_model_bar done; main=%.4f' % qwk[0])
