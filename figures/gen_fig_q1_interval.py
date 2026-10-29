# -*- coding: utf-8 -*-
"""fig_q1_interval —— 90% 预测区间：两种口径的配对对比（PairedBoxScatter 模板）

改用 academic-figure-skill 的 PairedBoxScatter 思路：同一感官维在两种口径下是一对，
用「半箱线 + 配对散点 + 配对连线」直接显示 50 个维度整体上移/下移，
取代原来的柱状图。

(a) 逐维覆盖率：50 个配对点，90% 名义水平用水平虚线；
(b) 逐维区间宽度：同一配对结构，显示共形校准的宽度代价。
Data: figures/derived/q1_prediction_interval.json
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from _figbase import ROOT, save_fig, tag_panels

d = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_prediction_interval.json"),
                   encoding="utf-8"))
q = d["quantile_regression"]["by_dim"]
c = d["conformal"]["by_dim"]
sens = list(c.keys())
target = d["target_coverage"]

C_Q = "#8FA8C0"   # 分位数回归（冷灰蓝）
C_C = "#C0392B"   # 共形校准（暗红）
LINE = "#2E5C8A"

mpl.rcParams.update({
    "font.size": 7.2,
    "axes.labelsize": 7.4,
    "xtick.labelsize": 7.0,
    "ytick.labelsize": 6.8,
    "legend.fontsize": 6.6,
    "axes.edgecolor": "#4D4D4D",
    "axes.linewidth": 0.7,
    "axes.unicode_minus": False,
})

def half_box(ax, x, vals, color, side, width=0.30):
    """半箱线：side=-1 画左半、+1 画右半。"""
    v = np.asarray(vals, float)
    q1, med, q3 = np.percentile(v, [25, 50, 75])
    lo, hi = v.min(), v.max()
    cx = x + side * width / 2
    ax.add_patch(Rectangle((min(cx, cx - side * width), q1), width, q3 - q1,
                           facecolor=color, edgecolor="none", alpha=0.30, zorder=2))
    ax.plot([x, x + side * width], [med, med], color=color, lw=1.5, zorder=4)
    ax.plot([x, x + side * width], [q3, q3], color=color, lw=0.9, zorder=4)
    ax.plot([x, x + side * width], [q1, q1], color=color, lw=0.9, zorder=4)
    ax.plot([x, x], [lo, hi], color=color, lw=0.7, zorder=3)

def paired_panel(ax, key, ylabel, ref=None, ref_label=None):
    vq = np.array([q[s][key] for s in sens])
    vc = np.array([c[s][key] for s in sens])
    xs = [0, 1]
    # 配对连线
    for a, b in zip(vq, vc):
        ax.plot(xs, [a, b], color=LINE, lw=0.5, alpha=0.20, zorder=1)
    # 半箱线
    half_box(ax, 0, vq, C_Q, -1)
    half_box(ax, 1, vc, C_C, +1)
    # 散点（固定偏移，不抖动）
    rng = np.random.default_rng(42)
    ax.scatter(np.full(len(vq), 0.0) - 0.14, vq, s=9, color=C_Q, alpha=0.85,
               edgecolor="white", linewidth=0.3, zorder=5)
    ax.scatter(np.full(len(vc), 1.0) + 0.14, vc, s=9, color=C_C, alpha=0.85,
               edgecolor="white", linewidth=0.3, zorder=5)
    if ref is not None:
        ax.axhline(ref, color="#444444", lw=0.9, ls=(0, (4, 3)), zorder=2)
        ax.text(1.46, ref, ref_label, fontsize=6.2, color="#444444",
                va="bottom", ha="right")
    ax.set_xticks(xs)
    ax.set_xticklabels(["分位数回归", "共形校准"])
    ax.set_xlim(-0.55, 1.55)
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#EEEEEE", lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.0), layout="constrained",
                         gridspec_kw={"wspace": 0.26})

paired_panel(axes[0], "coverage", "实测覆盖率", ref=target, ref_label="90%")
axes[0].set_ylim(0.60, 1.0)

paired_panel(axes[1], "width", "区间宽度（标准化单位）")

tag_panels(axes)

save_fig(fig, "figures/fig_q1_interval.png")

n_up = int(np.sum([c[s]["coverage"] > q[s]["coverage"] for s in sens]))
print("coverage median q=%.4f c=%.4f, %d/%d dims improved"
      % (np.median([q[s]["coverage"] for s in sens]),
         np.median([c[s]["coverage"] for s in sens]), n_up, len(sens)))
