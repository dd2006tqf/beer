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


for tag, prefix, title in GROUPS:
    idx = pick(prefix)
    # 行内按“该行最大绝对相关”降序，主带集中在顶部，便于读数
    idx = sorted(idx, key=lambda i: -np.nanmax(np.abs(mat[i])))
    sub = mat[idx]
    n_row = len(idx)

    fig, ax = plt.subplots(figsize=(6.6, 0.30 * n_row + 1.5))
    set_paper_placement(fig, width_fraction=0.86)
    im = ax.imshow(sub, cmap="RdBu_r", vmin=-1, vmax=1, origin="upper",
                   interpolation="nearest", aspect="auto")

    ax.set_xticks(np.arange(len(comps)))
    ax.set_xticklabels([c if len(c) <= 13 else c[:12] + "…" for c in comps],
                       rotation=45, ha="right", fontsize=6.8)
    ax.set_yticks(np.arange(n_row))
    ax.set_yticklabels([dim_zh(dims[i]) for i in idx], fontsize=7.0)
    ax.tick_params(length=0)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)

    # 只在 |r|>=0.35 的格内标注数值，避免小字糊成一片
    for i in range(n_row):
        for j in range(len(comps)):
            v = sub[i, j]
            if abs(v) >= 0.35:
                ax.text(j, i, "%.2f" % v, ha="center", va="center",
                        fontsize=5.6, color="white" if abs(v) > 0.72 else "#222")

    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.015)
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=6.5, length=2)
    cb.set_label("Pearson 相关系数", fontsize=7.5)
    ax.set_title(title, fontsize=9, pad=6)

    fig.tight_layout()
    save_fig(fig, "figures/fig_q2_chem_sensory_%s.png" % tag)
    print("fig_q2_chem_sensory_%s rows=%d" % (tag, n_row))
