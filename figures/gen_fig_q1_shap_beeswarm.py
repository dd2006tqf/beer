# -*- coding: utf-8 -*-
"""fig_q1_shap_beeswarm -- SHAP 蜂群：方向而不只是强度

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a-d) beeswarm per dimension -> assets/figures/MarkerGeneDotPlot (cross-type: beeswarm) -> param inherit

图 12 给的是 |r| 的热力，图 19 只挑了 4 个化合物画依赖散点；两处都读不出
"这个化合物把预测往哪边推、推多少"。蜂群图把 250 个样本的 SHAP 值按特征铺开，
颜色是特征自身的取值：向左的红点/向右的蓝点立刻区分正向与负向驱动。
四个面板分别覆盖强信号维、麦芽维、酯维与 DMS 维，正好对比"机理直观"与"代理变量"两类。
Data: _tmp/q1_shap_beeswarm.json（TreeSHAP，q1_models.pkl）。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from _figbase import ROOT, save_fig

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 6.6, "legend.fontsize": 6.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]

d = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_shap_beeswarm.json"), encoding="utf-8"))
PANELS = [("alcohol", "酒精", "(a)"), ("A_malt_all", "香气·麦芽", "(b)"),
          ("F_esters_all", "风味·酯", "(c)"), ("dms", "DMS", "(d)")]
cmap = LinearSegmentedColormap.from_list("v", ["#2166AC", "#B7C9DC", "#E8E8E8", "#E7A6A0", "#B2182C"])

fig, axes = plt.subplots(2, 2, figsize=(6.8, 4.9),
                         gridspec_kw={"wspace": 0.30, "hspace": 0.28},
                         layout="constrained")
axes = axes.ravel()

rng = np.random.default_rng(3)
for ax, (dim, lab, tag) in zip(axes, PANELS):
    recs = d[dim][::-1]
    n = len(recs)
    for row, r in enumerate(recs):
        s = np.array(r["shap"], dtype=float)
        v = np.array(r["value"], dtype=float)
        q = np.argsort(np.argsort(v)) / max(len(v) - 1, 1)   # 0-1 分位
        y = row + rng.uniform(-0.30, 0.30, len(s))
        ax.scatter(s, y, c=q, cmap=cmap, s=12, alpha=0.85, linewidths=0, zorder=3)
    ax.axvline(0, color="#666666", lw=0.7, ls=(0, (3, 3)), zorder=2)
    ax.set_yticks(range(n))
    nm = [x["name"].replace("_", " ").replace(".", " ") for x in recs]
    ax.set_yticklabels([t if len(t) <= 18 else t[:17] + "…" for t in nm], fontsize=7.2)
    ax.tick_params(axis="y", length=0, pad=2)
    ax.set_ylim(-0.7, n - 0.3)
    ax.set_xlabel("SHAP 值（对 %s 的贡献）" % lab, fontsize=8.2, labelpad=2)
    ax.grid(axis="x", color="#F3F3F3", lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", labelsize=7.2)
    ax.text(0.02, 1.02, tag, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=10, fontweight="bold", color="#222222")

# 颜色条：特征取值高低（挂到整组子图，matplotlib 自动留空间）
sm = mpl.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(0, 1))
cb = fig.colorbar(sm, ax=axes.tolist(), fraction=0.025, pad=0.02)
cb.set_ticks([0, 1]); cb.set_ticklabels(["低", "高"])
cb.ax.tick_params(labelsize=7.2, length=2)
cb.outline.set_visible(False)
cb.set_label("特征取值", fontsize=7.4, labelpad=2)

fig.savefig(os.path.join(ROOT, "figures", "fig_q1_shap_beeswarm.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; dims:", [p[0] for p in PANELS])
