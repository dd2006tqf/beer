# -*- coding: utf-8 -*-
"""fig_q1_sensory_matrix —— 50 个感官目标的相关矩阵（按香气/风味/口感扩展分组）

数据源：user_data/5.csv（主办方给定的感官相关矩阵，50x50，对称，对角线=1）。
不做重算，口径与附件一致。仅显示上三角，蓝正红负，中心 0。

三组结构：香气 A_(15) / 风味 F_(15) / 口感·缺陷·总体 X(20)。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from _figbase import ROOT, dim_zh, save_fig

plt.rcParams.update({
    "axes.unicode_minus": False,
    "font.size": 7.0,
})

src = os.path.join(ROOT, "user_data", "5.csv")
raw = pd.read_csv(src, index_col=0)
raw.index = [str(i) for i in raw.index]

names6 = [str(c) for c in raw.columns]
assert len(names6) == 50, len(names6)

# 用 4.csv 的列顺序重建短名（5.csv 内部顺序）
sens4 = pd.read_csv(os.path.join(ROOT, "user_data", "4.csv"), nrows=0).columns[3:].tolist()
assert len(sens4) == 50

M = raw.loc[names6, names6].values.astype(float)
assert M.shape == (50, 50)
assert np.allclose(M, M.T, atol=1e-8), "5.csv 非对称"

# 5.csv 与 4.csv 的列顺序按位置一致（已核对 50 列全同名映射），无需重排
order = np.arange(50)
groups = []
for i, s in enumerate(sens4):
    groups.append("A" if s.startswith("A_") else ("F" if s.startswith("F_") else "X"))
groups = np.array(groups)
idx = np.concatenate([[i for i in order if groups[i] == g] for g in ("A", "F", "X")])
Ms = M[np.ix_(idx, idx)]
labels = [dim_zh(sens4[i]) for i in idx]
gs = groups[idx]

cmap = LinearSegmentedColormap.from_list(
    "bluewhite_red", ["#2166AC", "#92C5DE", "#F7F7F7", "#F4A582", "#B2182C"], N=256)

fig, ax = plt.subplots(figsize=(5.5, 4.9), layout="constrained")
Mm = np.ma.masked_where(np.tril(np.ones_like(Ms, dtype=bool), k=-1), Ms)
im = ax.imshow(Mm, cmap=cmap, vmin=-1, vmax=1, interpolation="nearest")

# 分组边界
bounds = [0, 15, 30, 50]
for b in bounds[1:-1]:
    ax.axhline(b - 0.5, color="white", lw=1.6, zorder=5)
    ax.axvline(b - 0.5, color="white", lw=1.6, zorder=5)

ax.set_xticks(range(50))
ax.set_yticks(range(50))
ax.set_xticklabels(labels, rotation=90, fontsize=4.6)
ax.set_yticklabels(labels, fontsize=4.6)
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)

# 组标签
gl = [(0, 15, "香气 Aroma (15)"), (15, 30, "风味 Flavour (15)"), (30, 50, "口感 / 缺陷 / 总体 (20)")]
for lo, hi, name in gl:
    ax.text(-6.0, (lo + hi - 1) / 2, name, rotation=90, va="center", ha="center",
            fontsize=6.2, color="#333333")

cb = fig.colorbar(im, ax=ax, shrink=0.62, pad=0.02, aspect=28)
cb.set_label("Pearson 相关系数", fontsize=7.0)
cb.ax.tick_params(labelsize=6.4)
cb.outline.set_linewidth(0.5)

save_fig(fig, "figures/fig_q1_sensory_matrix.png")
print("group sizes", {g: int((gs == g).sum()) for g in "AFX"})
print("range", float(Ms.min()), float(Ms.max()))
