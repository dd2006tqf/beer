# -*- coding: utf-8 -*-
"""fig_q2_top1_bar —— 每维 Top-1/2/3 的 bootstrap 入选频率（名次 x 维度热力矩阵）

行是 50 个感官维度（按第 3 位频率升序），列是第 1、2、3 位化合物；
格内数字为 500 次 bootstrap 下的入选频率，颜色深即稳定。
第 1、2 列几乎全为 1.000（47/50 维恰为 1.000），真正有信息的是第 3 列：
它回答"第三名是不是凑数"。矩阵化后一眼可见右侧一列的颜色衰减。

版式参考 ModelViz 09_REL_003（多层编码相关性热图）。
数据源：submission/q2_top3_compounds.csv（rank=1/2/3）。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from _figbase import save_fig, dim_zh
from _utils.plot_utils import ROOT

df = pd.read_csv(os.path.join(ROOT, 'submission', 'q2_top3_compounds.csv'))
piv = df.pivot(index='sensory_dim', columns='rank',
               values='bootstrap_select_freq')
piv = piv.sort_values(3, ascending=False)   # 第 3 位最稳的在最上

plt.rcParams.update({
    'axes.labelsize': 7.6,
    'xtick.labelsize': 7.2,
    'ytick.labelsize': 6.2,
    'axes.unicode_minus': False,
})

vals = piv[[1, 2, 3]].values
cmap = LinearSegmentedColormap.from_list(
    'freq', ['#F2F5F8', '#B9CFE3', '#6C97BE', '#2E5C8A', '#173B5C'])

fig, ax = plt.subplots(figsize=(7.4, 2.35), layout='constrained')
vals_t = vals.T                      # 3 行（名次） × 50 列（维度）
im = ax.imshow(vals_t, cmap=cmap, vmin=0.35, vmax=1.0, aspect='auto',
               interpolation='nearest')

ax.set_yticks([0, 1, 2])
ax.set_yticklabels(['第 1 位', '第 2 位', '第 3 位'], fontsize=7.2)
ax.set_xticks(np.arange(len(piv)))
ax.set_xticklabels([dim_zh(d) for d in piv.index], fontsize=5.6,
                   rotation=90, ha='center')
ax.tick_params(length=0)
for s_ in ax.spines.values():
    s_.set_visible(False)

# 第 1、2 位几乎饱和，只标第 3 位的具体频率
for j in range(len(piv)):
    v3 = piv.iloc[j][3]
    ax.text(j, 2, '%.2f' % v3, ha='center', va='center', fontsize=5.0,
            color='white' if v3 > 0.78 else '#1F2933')

cb = fig.colorbar(im, ax=ax, fraction=0.020, pad=0.012)
cb.outline.set_visible(False)
cb.set_label('入选频率', fontsize=7.0)
cb.ax.tick_params(labelsize=6.4, length=2)
cb.set_ticks([0.4, 0.6, 0.8, 1.0])

save_fig(fig, 'figures/fig_q2_top1_bar.png')
print('done; n=%d rank3 min=%.3f' % (len(piv), piv[3].min()))
