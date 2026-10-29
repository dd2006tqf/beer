# -*- coding: utf-8 -*-
"""fig_q2_stability —— 单方法稳定性 vs 跨方法一致性（分组小提琴模板）

改用 academic-figure-skill 的 Violin/GroupedViolin 思路：
(a) 单方法稳定性：50 维的 Top-1 bootstrap 入选频率，按香气/风味/口感三组做
    小提琴 + 抖动散点，直接显示"饱和"（绝大多数压在 1.000）；
(b) 跨方法一致性：三对方法（SHAP-相关、SHAP-RF、相关-RF）的逐维 Jaccard 分布，
    小提琴 + 散点，并叠加随机基线 0.0086 作参照；
(c) 以 50 维散点显示两口径的正交性（原 (a) 的核心结论保留为小面板）。

Data: figures/problem_2_results.json + figures/derived/q2_method_agreement.json
"""
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from _figbase import P2, ROOT, save_fig, tag_panels

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 7.6, "axes.labelsize": 7.4, "axes.titlesize": 8.0,
    "xtick.labelsize": 7.0, "ytick.labelsize": 7.0, "legend.fontsize": 6.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.7, "legend.frameon": False,
    "axes.unicode_minus": False,
})

BLUE, RED, GREEN, ORANGE = "#2E5C8A", "#B03A2E", "#3E8E5A", "#D4A017"
GREY = "#8C8C8C"

rk = P2["fig_data"]["top1_freq_ranked"]
dims = [r[0] for r in rk]
freq = np.array([r[1] for r in rk], float)
jac = np.array([r[2] for r in rk], float)
base = P2.get("random_jaccard_baseline", {})
base_mean = float(base.get("mean", 0.0086))

agree = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_method_agreement.json"),
                       encoding="utf-8"))
M = agree["methods"]
PAIRS = [("shap", "corr", "SHAP–相关"), ("shap", "rf", "SHAP–RF"), ("corr", "rf", "相关–RF")]
pair_jac = {}
for a, b, name in PAIRS:
    v = []
    for i in range(len(M["shap"])):
        A, B = set(M[a][i]), set(M[b][i])
        v.append(len(A & B) / max(1, len(A | B)))
    pair_jac[name] = np.array(v, float)

def grp(d):
    return "香气 A_" if d.startswith("A_") else ("风味 F_" if d.startswith("F_") else "口感/缺陷")

G = [grp(d) for d in dims]
GNAME = ["香气 A_", "风味 F_", "口感/缺陷"]
GCOL = [BLUE, RED, ORANGE]

def violin_plus_scatter(ax, data, positions, colors, labels, jitter=0.075):
    for pos, vals, col in zip(positions, data, colors):
        vals = np.asarray(vals, float)
        if vals.size > 2 and vals.std() > 1e-9:
            kde = gaussian_kde(vals, bw_method=0.4)
            span = max(vals.max() - vals.min(), 1e-3) * 1.2
            ys = np.linspace(vals.min() - 0.05 * span, vals.max() + 0.05 * span, 160)
            w = kde(ys)
            w = w / w.max() * 0.34
            ax.fill_betweenx(ys, pos - w, pos + w, color=col, alpha=0.22, lw=0, zorder=2)
            ax.plot(pos - w, ys, color=col, lw=0.7, alpha=0.8, zorder=3)
            ax.plot(pos + w, ys, color=col, lw=0.7, alpha=0.8, zorder=3)
        rng = np.random.default_rng(7)
        xs = pos + rng.uniform(-jitter, jitter, vals.size)
        ax.scatter(xs, vals, s=8, color=col, alpha=0.75, edgecolor="white",
                   linewidth=0.25, zorder=5)
        ax.plot([pos - 0.20, pos + 0.20], [np.median(vals)] * 2, color="#222222",
                lw=1.3, zorder=6)
    ax.set_xticks(positions)
    ax.set_xticklabels(labels)
    ax.grid(axis="y", color="#F0F0F0", lw=0.4, zorder=0)
    ax.set_axisbelow(True)

fig = plt.figure(figsize=(6.6, 2.75))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.18], wspace=0.30,
                      left=0.075, right=0.985, top=0.95, bottom=0.245)

# ---------- (a) 单方法稳定性：按感官组 ----------
ax1 = fig.add_subplot(gs[0, 0])
data1 = [freq[np.array(G) == g] for g in GNAME]
violin_plus_scatter(ax1, data1, [0, 1, 2], GCOL, ["香气", "风味", "口感"])
ax1.set_ylim(0.93, 1.02)
ax1.axhline(1.0, color=GREY, lw=0.7, ls=(0, (4, 3)), zorder=1)

# ---------- (b) 跨方法一致性：三对方法 ----------
ax2 = fig.add_subplot(gs[0, 1])
data2 = [pair_jac[n] for _, _, n in PAIRS]
violin_plus_scatter(ax2, data2, [0, 1, 2], [BLUE, GREEN, RED],
                    ["SHAP–\n相关", "SHAP–\nRF", "相关–\nRF"])
ax2.set_ylim(-0.03, 0.80)
ax2.axhline(base_mean, color=GREY, lw=0.7, ls=(0, (4, 3)), zorder=1)

tag_panels([ax1, ax2])

save_fig(fig, "figures/fig_q2_stability.png")

n_full = int((freq >= 0.9999).sum())
print("saturated %d/%d; jaccard mean %.4f; pairs:" % (n_full, len(freq), jac.mean()))
for n, v in pair_jac.items():
    print("  %-10s median %.3f mean %.3f" % (n, np.median(v), v.mean()))
