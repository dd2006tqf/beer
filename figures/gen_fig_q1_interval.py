# -*- coding: utf-8 -*-
"""fig_q1_interval —— 预测区间：覆盖率与宽度对照

对应 6.4 节新增的预测区间段。左侧对比两种口径（分位数回归 vs split-conformal）
的实测覆盖率与目标 90%；右侧给出 conformal 口径下香气/风味/口感三组的覆盖率分布。
核心信息：直接分位数回归系统性欠覆盖（75.3%），共形校准把覆盖率拉回 90.2%，
代价是区间宽度从 1.02 增到 1.55。

数据源：figures/derived/q1_prediction_interval.json。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import PALETTE, save_fig

import json
from _figbase import ROOT

d = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_prediction_interval.json"),
                   encoding="utf-8"))
q, c = d["quantile_regression"], d["conformal"]
target = d["target_coverage"]

plt.rcParams.update({
    "axes.labelsize": 7.8,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 7.0,
    "legend.fontsize": 6.8,
    "axes.edgecolor": "#6B7280",
    "axes.unicode_minus": False,
})

fig, axes = plt.subplots(1, 2, figsize=(6.9, 2.85),
                         gridspec_kw={"width_ratios": [1.0, 1.35], "wspace": 0.30},
                         layout="constrained")

# ---- (a) 两口径的覆盖率 / 宽度 ----
ax = axes[0]
names = ["分位数回归", "共形校准"]
covs = [q["overall_coverage"], c["overall_coverage"]]
wids = [q["overall_width"], c["overall_width"]]
x = np.arange(2)
bars = ax.bar(x, covs, width=0.52,
              color=[PALETTE[2], PALETTE[0]], edgecolor="white", linewidth=0.8, zorder=3)
ax.axhline(target, color=PALETTE[1], lw=1.3, ls="--", zorder=4)
ax.text(1.46, target + 0.012, "目标 90%", color=PALETTE[1], fontsize=6.6, ha="right")
for xi, (cv, wd) in enumerate(zip(covs, wids)):
    ax.text(xi, cv + 0.015, "%.1f%%" % (cv * 100), ha="center", fontsize=7.4, fontweight="bold")
    ax.text(xi, 0.045, "宽度 %.2f" % wd, ha="center", fontsize=6.8, color="white",
            fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels(names)
ax.set_ylim(0, 1.0)
ax.set_ylabel("实测覆盖率")
ax.set_title("(a) 区间口径对照", fontsize=8.4, loc="left", pad=4)

# ---- (b) conformal 分组覆盖率 ----
ax = axes[1]
g = c["by_group"]
labels = {"A": "香气\nA_ (15)", "F": "风味\nF_ (15)", "X": "口感/缺陷\nX (20)"}
keys = ["A", "F", "X"]
data = [[g[k]["coverage_mean"]] for k in keys]
pos = np.arange(3)
vals = [g[k]["coverage_mean"] for k in keys]
wds = [g[k]["width_mean"] for k in keys]
ax.bar(pos, vals, width=0.46, color=PALETTE[0], edgecolor="white", linewidth=0.8, zorder=3)
ax.axhline(target, color=PALETTE[1], lw=1.3, ls="--", zorder=4)
ax.axhline(c["overall_coverage"], color="#888888", lw=0.9, ls=":", zorder=4)
for xi, (v, w) in enumerate(zip(vals, wds)):
    ax.text(xi, v + 0.012, "%.1f%%" % (v * 100), ha="center", fontsize=7.2, fontweight="bold")
    ax.text(xi, 0.045, "宽 %.2f" % w, ha="center", fontsize=6.6, color="white")
ax.set_xticks(pos)
ax.set_xticklabels([labels[k] for k in keys])
ax.set_ylim(0, 1.0)
ax.set_ylabel("分组覆盖率")
ax.set_title("(b) 共形口径的分组覆盖", fontsize=8.4, loc="left", pad=4)

for a in axes:
    a.grid(axis="y", color="#DFE3E8", lw=0.5, zorder=0)
    a.set_axisbelow(True)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)

save_fig(fig, "figures/fig_q1_interval.png")
