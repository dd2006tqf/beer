# -*- coding: utf-8 -*-
"""fig_q1_bystyle -- 分风格的可预测性：总体 QWK 中有多少来自风格间差异

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) per-style within-style QWK strip + median -> assets/figures/GroupedViolin -> param inherit
(b) overall vs within-style mean by dim group   -> assets/figures/BarComparison -> param inherit

动机：0.3830 是全样本的均值，其中一部分判别力来自"不同风格整体感官水平不同"。
把样本按风格切开、在每个风格内部重算 QWK，会把这个成分去掉，得到更严格的口径。
这张图不是要否定主结果，而是把主结果的来源讲清楚：跨风格差异贡献了多少、
风格内部还剩多少可预测性。每格 n>=8 才计入。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from _figbase import ROOT, save_fig, dim_zh, tag_panels

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

df = pd.read_csv(os.path.join(ROOT, "figures", "derived", "q1_by_style.csv"))
g = df.groupby("style").agg(med=("qwk", "median"), mean=("qwk", "mean"),
                            n=("qwk", "size")).sort_values("med", ascending=True)

fig = plt.figure(figsize=(7.0, 3.4))
gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.22,
                      left=0.115, right=0.985, top=0.90, bottom=0.185)

# ══════════ (a) 分风格条带 ══════════
ax = fig.add_subplot(gs[0, 0])
rng = np.random.default_rng(11)
for k, (sty, row) in enumerate(g.iterrows()):
    v = df.loc[df["style"] == sty, "qwk"].values
    c = CATEGORICAL[0] if row["med"] >= 0 else GREY
    ax.scatter(k + rng.normal(0, 0.075, v.size), v, s=7, color=c, alpha=0.45,
               edgecolor="none", zorder=3)
    ax.plot([k - 0.26, k + 0.26], [row["med"]] * 2, color="#222222", lw=1.2, zorder=5)
ax.axhline(0, color="#555555", lw=0.7, ls=(0, (3, 3)), zorder=2)
ax.set_xticks(np.arange(len(g)))
ax.set_xticklabels(g.index, rotation=55, ha="right", fontsize=6.2)
ax.set_ylim(-0.95, 0.72)
ax.set_ylabel("风格内 50 维 QWK")
ax.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.set_title(" ", loc="left",
             fontsize=8, fontweight="bold", pad=4)

# ══════════ (b) 总体 vs 风格内 ══════════
ax2 = fig.add_subplot(gs[0, 1])
p1 = __import__("json").load(open(os.path.join(ROOT, "figures", "problem_1_results.json"), encoding="utf-8"))
groups = {"香气 A_": 0, "风味 F_": 1, "口感/缺陷": 2}
def grp(d):
    return 0 if d.startswith("A_") else (1 if d.startswith("F_") else 2)
overall = [p1["per_dim"][k]["qwk_main"] for k in p1["per_dim"]]
overall_g = [[] for _ in range(3)]
for k, v in p1["per_dim"].items():
    overall_g[grp(k)].append(v["qwk_main"])
within_g = [[] for _ in range(3)]
for k, v in df.groupby("dim")["qwk"].mean().items():
    within_g[grp(k)].append(v)

x = np.arange(3)
w = 0.34
mo = [np.median(v) for v in overall_g]
mw = [np.median(v) for v in within_g]
ax2.bar(x - w / 2, mo, w, color=CATEGORICAL[0], alpha=0.85, edgecolor="white",
        linewidth=0.6, label="全样本（跨风格）", zorder=3)
ax2.bar(x + w / 2, mw, w, color=CATEGORICAL[3], alpha=0.85, edgecolor="white",
        linewidth=0.6, label="风格内", zorder=3)
for xi, a, b in zip(x, mo, mw):
    ax2.text(xi - w / 2, a + 0.012, "%.2f" % a, ha="center", fontsize=6.2)
    ax2.text(xi + w / 2, b + 0.012, "%.2f" % b, ha="center", fontsize=6.2)
ax2.set_xticks(x)
ax2.set_xticklabels(["香气 A_", "风味 F_", "口感/缺陷"], fontsize=7)
ax2.set_ylim(0, max(mo) * 1.30)
ax2.set_ylabel("QWK 中位数")
ax2.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
ax2.set_axisbelow(True)
ax2.legend(loc="upper right", handletextpad=0.35, borderaxespad=0.3)
ax2.set_title(" ", loc="left", fontsize=8, fontweight="bold", pad=4)

tag_panels([ax, ax2])

fig.savefig(os.path.join(ROOT, "figures", "fig_q1_bystyle.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; styles=%d overall_med=%.3f within_med=%.3f"
      % (len(g), np.median(overall), np.median(df["qwk"])))
