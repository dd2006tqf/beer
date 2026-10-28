# -*- coding: utf-8 -*-
"""fig_q1_cross -- 跨问联合：可预测性 vs 归因稳定性

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) QWK x Top-1 stability quadrant -> assets/figures/MarkerGeneDotPlot -> param inherit
(b) rank-3 stability vs QWK      -> assets/figures/GroupedViolin (cross-type) -> param inherit

设计问题：第一问说"弱信号维不可预测"，第二问说"弱信号维归因不稳"。
这是两句独立的话，还是同一件事？把 50 个维度同时放到
(QWK, bootstrap 入选频率) 平面上，就能直接看出两条结论是不是同一个现象。
点色=归因来源一致度，点径=±1 准确率，四象限把"可预测且归因稳 / 不可预测也不稳"
等四种组合分开。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import P1, P2, ROOT, save_fig, dim_zh

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

t3 = pd.read_csv(os.path.join(ROOT, "submission", "q2_top3_compounds.csv"))
freq1 = t3[t3["rank"] == 1].set_index("sensory_dim")["bootstrap_select_freq"]
freq3 = t3[t3["rank"] == 3].set_index("sensory_dim")["bootstrap_select_freq"]
verdict = t3[t3["rank"] == 1].set_index("sensory_dim")["source_verdict"]

dims = list(P1["per_dim"].keys())
qwk = np.array([P1["per_dim"][d]["qwk_main"] for d in dims])
acc = np.array([P1["per_dim"][d]["acc_within1_main"] for d in dims])
f1 = np.array([freq1.get(d, np.nan) for d in dims])
f3 = np.array([freq3.get(d, np.nan) for d in dims])
vd = [verdict.get(d, "") for d in dims]

VCOL = {"一致": CATEGORICAL[2], "部分一致": CATEGORICAL[3], "不一致": GREY}
vcol = [VCOL.get(v, "#DDDDDD") for v in vd]

fig = plt.figure(figsize=(7.0, 3.35))
gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.24,
                      left=0.075, right=0.985, top=0.90, bottom=0.190)

# ══════════ (a) quadrant ══════════
ax = fig.add_subplot(gs[0, 0])
qx, qy = 0.30, 0.95
ax.axvspan(-0.05, qx, color="#F7F7F7", lw=0, zorder=0)
ax.axhline(qy, color="#CCCCCC", lw=0.7, ls=(0, (3, 3)), zorder=1)
ax.axvline(qx, color="#CCCCCC", lw=0.7, ls=(0, (3, 3)), zorder=1)
for i, d in enumerate(dims):
    ax.scatter(qwk[i], f1[i], s=10 + 55 * acc[i], color=vcol[i], alpha=0.85,
               edgecolor="white", linewidth=0.5, zorder=4)
ax.set_xlim(-0.05, 0.92)
ax.set_ylim(0.68, 1.03)
ax.set_xlabel("问题一：折外 QWK")
ax.set_ylabel("问题二：Top-1 bootstrap 入选频率")
ax.grid(color="#F3F3F3", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.text(0.02, 0.715, "可预测性低 · 归因稳", fontsize=6.0, color="#888888")
ax.text(0.62, 0.715, "可预测性高 · 归因稳", fontsize=6.0, color="#888888")
ax.text(0.02, 1.005, "可预测性低 · 归因也稳", fontsize=6.0, color="#888888")
ax.set_title("两问结论是否同一现象", loc="left", fontsize=8,
             fontweight="bold", pad=4)
for i in range(len(dims)):
    if qwk[i] < 0.22 and f1[i] < 0.95:
        ax.annotate(dim_zh(dims[i]), (qwk[i], f1[i]), xytext=(4, -7),
                    textcoords="offset points", fontsize=5.6, color="#444444")
leg = [Line2D([], [], marker="o", ls="", color=VCOL[k], ms=5, label=k)
       for k in ("一致", "部分一致", "不一致")]
leg.append(Line2D([], [], marker="o", ls="", color="white", markeredgecolor=GREY,
                  ms=8, label="点径 = ±1 准确率"))
ax.legend(handles=leg, loc="lower right", fontsize=6.0, handletextpad=0.3,
          labelspacing=0.22, borderaxespad=0.25)

# ══════════ (b) rank-3 vs QWK ══════════
ax2 = fig.add_subplot(gs[0, 1])
order = np.argsort(qwk)
bins = [(-1, 0.30), (0.30, 0.55), (0.55, 2)]
names_b = ["弱 <0.30", "中 0.30-0.55", "强 ≥0.55"]
groups = [[f3[i] for i in order if lo <= qwk[i] < hi] for lo, hi in bins]
parts = ax2.violinplot(groups, positions=[0, 1, 2], widths=0.72,
                       showextrema=False, showmedians=False)
for i, body in enumerate(parts["bodies"]):
    body.set_facecolor(CATEGORICAL[i if i < 2 else 0])
    body.set_alpha(0.28)
    body.set_edgecolor("none")
rng = np.random.default_rng(7)
for i, g in enumerate(groups):
    x = i + rng.normal(0, 0.045, len(g))
    ax2.scatter(x, g, s=13, color=CATEGORICAL[i if i < 2 else 0], alpha=0.85,
                edgecolor="white", linewidth=0.4, zorder=4)
    ax2.plot([i - 0.24, i + 0.24], [np.median(g)] * 2, color="#222222", lw=1.1,
             zorder=5)
    ax2.text(i, 0.335, "n=%d" % len(g), ha="center", fontsize=6.0, color=GREY)
ax2.set_xticks([0, 1, 2])
ax2.set_xticklabels(names_b, fontsize=7)
ax2.set_ylim(0.32, 1.06)
ax2.set_ylabel("第 3 位化合物的入选频率")
ax2.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
ax2.set_axisbelow(True)
ax2.set_title("第三名的稳定性随可预测性上升", loc="left", fontsize=8,
              fontweight="bold", pad=4)

for ax_, tag in ((ax, "(a)"), (ax2, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.022, tag, ha='center', va='bottom',
             fontsize=8.5, fontweight='bold', color='#222222')

fig.savefig(os.path.join(ROOT, "figures", "fig_q1_cross.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; corr(qwk,f1)=%.3f corr(qwk,f3)=%.3f"
      % (np.corrcoef(qwk, f1)[0, 1], np.corrcoef(qwk, f3)[0, 1]))
