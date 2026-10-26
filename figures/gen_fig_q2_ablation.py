# -*- coding: utf-8 -*-
"""fig_q2_ablation — 证据融合消融（新增）

左：四个证据组合的平均模块覆盖数；
右：Top-3 化合物在 50 维中的出现频次分布（集中度）。
数据源：_tmp/q2_ablation.json（本轮复算）。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt

from _figbase import save_fig, set_paper_placement, declutter_axes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "_tmp", "q2_ablation.json"), encoding="utf-8"))

variants = d["variants"]
order = ["corr only", "SHAP + corr", "SHAP only", "full (3-way)"]
zh = {"corr only": "仅交叉相关", "SHAP + corr": "SHAP + 相关",
      "SHAP only": "仅 SHAP", "full (3-way)": "三路融合（本文）"}
vm = {v["variant"]: v for v in variants}
cov = [vm[k]["mean_module_coverage"] for k in order]
names = [zh[k] for k in order]

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.5),
                         gridspec_kw={"width_ratios": [1.2, 1]})
set_paper_placement(fig, width_fraction=0.98)

# 左：模块覆盖数
ax = axes[0]
yy = np.arange(len(cov))[::-1]
cols = ["#C9CED6", "#A9C3DD", "#7BA7CF", "#2E5C8A"]
bars = ax.barh(yy, cov, height=0.6, color=cols, edgecolor="white", linewidth=0.6, zorder=2)
for b, v in zip(bars, cov):
    ax.text(v + 0.04, b.get_y() + b.get_height() / 2, "%.2f" % v,
            va="center", ha="left", fontsize=7.6, color="#222")
ax.set_yticks(yy)
ax.set_yticklabels(names, fontsize=7.8)
ax.set_xlim(0, 3.35)
ax.set_xlabel("单维 Top-3 命中的不同模块数（满分 3）", fontsize=7.8)
ax.tick_params(axis="x", labelsize=7.2)
declutter_axes(ax, grid_axis="x")

# 右：集中度分布
ax = axes[1]
counts = list(d["compound_counts"].values())
hist = {}
for c in counts:
    hist[c] = hist.get(c, 0) + 1
ks = sorted(hist)
ax.bar(ks, [hist[k] for k in ks], color="#2E5C8A", edgecolor="white",
       linewidth=0.6, width=0.7, zorder=2)
ax.set_xlabel("某化合物进入的维度数", fontsize=7.8)
ax.set_ylabel("化合物个数", fontsize=7.8)
ax.set_xticks(ks)
ax.tick_params(labelsize=7.2)
declutter_axes(ax, grid_axis="y")
ax.text(0.97, 0.9, "共 %d 个不同化合物" % d["n_distinct_compounds"],
        transform=ax.transAxes, ha="right", fontsize=7.2, color="#444")

fig.tight_layout()
save_fig(fig, "figures/fig_q2_ablation.png")
print("fig_q2_ablation done; coverage=%s" % cov)
