# -*- coding: utf-8 -*-
"""fig_q1_sig -- 逐维配对胜负：均值赢了，但赢在哪几维

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) per-dimension delta strip + win/loss tally -> assets/figures/GroupedViolin -> param inherit
(b) delta sorted curve with cumulative win share   -> assets/figures/LineTrend   -> param inherit

为什么不用森林图：表 7 已经给出三类基线的 Δ 与 95% CI，森林图只是把同一组数字
重画一遍，属于重复可视化。这里改问一个表里没有的问题——50 个维度里主模型究竟
赢了几维、输的那几维亏多少、增益是否只由少数维度撑起。
(a) 把 150 个配对差值按基线分组铺开，并标出胜/负维数；
(b) 把差值降序累加，斜率的陡缓直接显示"增益集中在少数维"还是"普遍小胜"。
数据：_tmp/q1_perdim_delta.json（由 submission/q1_oof_predictions.csv 逐维重算）。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import ROOT, save_fig, tag_panels

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

d = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_perdim_delta.json"), encoding="utf-8"))
ORDER = ["knn", "rf", "enet"]

fig = plt.figure(figsize=(7.0, 3.15))
gs = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.22], wspace=0.26,
                      left=0.085, right=0.985, top=0.895, bottom=0.190)

# ══════════ (a) 逐维差值 strip ══════════
ax = fig.add_subplot(gs[0, 0])
rng = np.random.default_rng(5)
for i, k in enumerate(ORDER):
    r = d["models"][k]
    v = np.array(r["delta"], dtype=float)
    x = i + rng.normal(0, 0.055, v.size)
    pos = v > 0
    ax.scatter(x[pos], v[pos], s=11, color=CATEGORICAL[0], alpha=0.62,
               edgecolor="none", zorder=3)
    ax.scatter(x[~pos], v[~pos], s=16, marker="v", color=CATEGORICAL[1],
               alpha=0.85, edgecolor="white", linewidth=0.35, zorder=4)
    ax.plot([i - 0.26, i + 0.26], [np.median(v)] * 2, color="#222222", lw=1.2, zorder=5)
ax.axhline(0, color="#555555", lw=0.8, ls=(0, (4, 3)), zorder=2)
ax.set_xticks(range(3))
ax.set_xticklabels([d["models"][k]["name"] for k in ORDER], fontsize=7)
ax.set_xlim(-0.55, 2.55)
ax.set_ylim(-0.09, 0.42)
ax.set_ylabel("逐维 Δ QWK（主模型 - 基线）")
ax.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.set_title(" ", loc="left", fontsize=8, fontweight="bold", pad=4)

# ══════════ (b) 降序累计 ══════════
ax2 = fig.add_subplot(gs[0, 1])
styles = ["-", "--", ":"]
for i, k in enumerate(ORDER):
    r = d["models"][k]
    v = np.sort(np.array(r["delta"], dtype=float))[::-1]
    ax2.plot(np.arange(1, v.size + 1), v, color=CATEGORICAL[i], lw=1.5,
             ls=styles[i], zorder=3)
    ax2.scatter([r["win"]], [v[r["win"] - 1]], s=22, color=CATEGORICAL[i],
                edgecolor="white", linewidth=0.6, zorder=5)
ax2.axhline(0, color="#555555", lw=0.8, ls=(0, (4, 3)), zorder=2)
ax2.set_xlim(0, 51)
ax2.set_ylim(-0.09, 0.40)
ax2.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
ax2.set_axisbelow(True)
ax2.set_title(" ", loc="left", fontsize=8, fontweight="bold", pad=4)
tag_panels([ax, ax2])

fig.savefig(os.path.join(ROOT, "figures", "fig_q1_sig.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; win:", {k: d["models"][k]["win"] for k in ORDER})
