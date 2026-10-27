# -*- coding: utf-8 -*-
"""fig_q2_chem_sensory_a/f/x — 化学-感官交叉相关按感官组拆分（香气 / 风味 / 口感缺陷）

原 50×14 整页热图在一页 A4 上过高，这里按感官分组拆成三张独立图：
  fig_q2_chem_sensory_a.png  香气维 A_，15 行
  fig_q2_chem_sensory_f.png  风味维 F_，15 行
  fig_q2_chem_sensory_x.png  口感/缺陷/总体，20 行
三图共用同一色标范围 [-1, 1] 与同一化合物列顺序，可逐列对照阅读。
数据源：supp_eda.json::chem_sensory_corr（1.csv 化学 + 4.csv 感官按 beer_id 对齐派生）。

用法：python figures/gen_fig_q2_chem_sensory_split.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from _figbase import SUPP, save_fig, set_paper_placement, dim_zh
from _utils.plot_utils import draw_vector_heatmap

cs = SUPP["chem_sensory_corr"]
dims = list(cs["sensory_dims"])
comps = list(cs["compounds"])
mat = np.array([[np.nan if v is None else v for v in row] for row in cs["matrix"]])
mat = np.nan_to_num(mat, nan=0.0)

GROUPS = [
    ("a", "A_", "香气维 A_，15 维"),
    ("f", "F_", "风味维 F_，15 维"),
    ("x", None, "口感、缺陷与总体评价，20 维"),
]


def pick(prefix):
    if prefix is None:
        return [i for i, d in enumerate(dims) if not d.startswith(("A_", "F_"))]
    return [i for i, d in enumerate(dims) if d.startswith(prefix)]


# 双栏版式：50 行拆成左右各 25 行，单色标，行高翻倍以保证可读
order = sorted(range(len(dims)), key=lambda i: -np.nanmax(np.abs(mat[i])))
halves = [order[:25], order[25:]]

fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.35), layout='constrained',
                         gridspec_kw={'wspace': 0.30})
short = []
for c in comps:
    c2 = c.replace('_', ' ')
    short.append(c2 if len(c2) <= 12 else c2[:11] + "…")

im = None
for ax, idx in zip(axes, halves):
    sub = mat[idx]
    im = ax.imshow(sub, cmap="RdBu_r", vmin=-1, vmax=1, origin="upper",
                   interpolation="nearest", aspect="auto")
    ax.set_xticks(np.arange(len(comps)))
    ax.set_xticklabels(short, rotation=90, ha="center", fontsize=4.9)
    ax.set_yticks(np.arange(len(idx)))
    ax.set_yticklabels([dim_zh(dims[i]) for i in idx], fontsize=5.4)
    ax.tick_params(length=0, pad=1.2)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)

cb = fig.colorbar(im, ax=axes, fraction=0.016, pad=0.010)
cb.outline.set_visible(False)
cb.ax.tick_params(labelsize=6.2, length=2)
cb.set_label("相关系数", fontsize=7.0)

save_fig(fig, "figures/fig_q2_chem_sensory_all.png")
print("fig_q2_chem_sensory_all rows=%d x2" % len(halves[0]))
