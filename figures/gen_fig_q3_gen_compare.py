# -*- coding: utf-8 -*-
"""fig_q3_gen_compare — 三种生成方式的四维对照（新增）

小多图：分布保真（KS）、新颖性、相关结构差异、观测区间内比例。
数据源：figures/derived/q3_generation_compare.csv（权威副本）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _figbase import save_fig, set_paper_placement, declutter_axes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, "figures", "derived", "q3_generation_compare.csv"))

sel = ["bootstrap", "gaussian", "CVAE-raw", "CVAE-clipped"]
zh = {"bootstrap": "风格内重采样", "gaussian": "风格内高斯",
      "CVAE-raw": "CVAE（截断前）", "CVAE-clipped": "CVAE（截断后）"}
agg = df[df.method.isin(sel)].groupby("method")[
    ["ks", "novelty_med", "corr_mae", "in_range"]].mean().reindex(sel)

PANELS = [
    ("ks", "分布保真：KS 距离（越小越好）", "#2E5C8A"),
    ("corr_mae", "结构保真：相关结构差异（越小越好）", "#3E8E5A"),
    ("in_range", "合规：落在观测区间内比例", "#8C6D31"),
    ("novelty_med", "新颖性：到最近真实样本距离（对数）", "#7D5BA6"),
]

fig, axes = plt.subplots(1, 4, figsize=(7.4, 2.9))
set_paper_placement(fig, width_fraction=0.99)

labels = [zh[m] for m in sel]
for ax, (col, title, color) in zip(axes, PANELS):
    vals = agg[col].values
    ax.bar(range(len(vals)), vals, color=color, edgecolor="white",
           linewidth=0.5, width=0.66, zorder=2)
    for i, v in enumerate(vals):
        txt = "%.3f" % v if abs(v) < 10 else "%.0f" % v
        ax.text(i, v * 1.02 if v > 0 else 0.02, txt, ha="center",
                va="bottom", fontsize=6.2, rotation=0)
    ax.set_xticks(range(len(vals)))
    ax.set_xticklabels(labels, rotation=38, ha="right", fontsize=6.0)
    ax.set_title(title, fontsize=6.9, pad=4)
    if col == "novelty_med":
        ax.set_yscale("symlog", linthresh=1.0)
    ax.tick_params(axis="y", labelsize=6.2)
    ax.set_ylim(0, max(vals) * 1.28 if max(vals) > 0 else 1)
    declutter_axes(ax, grid_axis="y")

fig.tight_layout()
save_fig(fig, "figures/fig_q3_gen_compare.png")
print("fig_q3_gen_compare done")
print(agg.round(4).to_string())
