# -*- coding: utf-8 -*-
"""fig_q1_pred_perf -- 50 维 QWK 排序 + 逐维 bootstrap 区间

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) ranked dot + 95% CI  -> assets/figures/BarCategorical (cross-type: forest) -> param inherit
(b) QWK vs ±1 accuracy   -> assets/figures/MarginalDensity (cross-type)        -> param inherit

新增信息：每维 QWK 的 2000 次 bootstrap 95% 区间。原图只有点估计，
读者无法判断"0.32 与 0.40 的差距是不是抽样噪声"。区间与点一起画之后，
强信号维(区间整体远离 0)与弱信号维(区间跨 0 或贴近 0)立刻分开。
右图把 QWK 与 ±1 准确率联立：弱信号维即便 QWK 低，±1 仍可 >0.5，
说明偏差集中在相邻一级。

Data: figures/problem_1_results.json::per_dim + _tmp/q1_boot_full.json::per_dim
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import P1, ROOT, save_fig, dim_zh, tag_panels

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 6.4, "legend.fontsize": 6.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

PD = P1["per_dim"]
ranked = P1["fig_data"]["qwk_ranked"]
boot = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_boot_full.json"), encoding="utf-8"))["per_dim"]
mean_qwk = P1["summary"]["mean_qwk_main"]

names = [r[0] for r in ranked]
vals = np.array([PD[n]["qwk_main"] for n in names])
acc = np.array([PD[n]["acc_within1_main"] for n in names])
lo = np.array([boot[n]["lo"] for n in names])
hi = np.array([boot[n]["hi"] for n in names])

def tier(v):
    return CATEGORICAL[0] if v >= 0.55 else (CATEGORICAL[3] if v >= 0.30 else GREY)

fig = plt.figure(figsize=(7.2, 4.6))
gs = fig.add_gridspec(1, 2, width_ratios=[1.15, 1.0], wspace=0.13,
                      left=0.135, right=0.985, top=0.92, bottom=0.115)

# ══════════ (a) 排序 + CI ══════════
ax = fig.add_subplot(gs[0, 0])
y = np.arange(len(names))[::-1]
ax.axvline(0, color="#BBBBBB", lw=0.7, zorder=1)
for k, i in enumerate(range(len(names))):
    c = tier(vals[i])
    ax.plot([lo[i], hi[i]], [y[k], y[k]], color=c, lw=1.5, alpha=0.55,
            solid_capstyle="butt", zorder=2)
    ax.scatter(vals[i], y[k], s=17, color=c, edgecolor="white", linewidth=0.45, zorder=4)
ax.axvline(mean_qwk, color="#444444", lw=0.8, ls=(0, (4, 3)), zorder=3)
ax.set_yticks(y)
ax.set_yticklabels([dim_zh(n) for n in names], fontsize=5.6)
ax.tick_params(axis="y", length=0, pad=2)
ax.set_ylim(-0.9, len(names) - 0.1)
ax.set_xlim(-0.03, 0.95)
ax.set_xlabel("折外 QWK（点=点估计，横线=2000 次 bootstrap 95% 区间）")
ax.grid(axis="x", color="#F0F0F0", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.annotate("全维均值 %.3f" % mean_qwk, xy=(mean_qwk, len(names) - 7),
            xytext=(mean_qwk + 0.16, len(names) - 11), fontsize=6.2, color="#333333",
            arrowprops=dict(arrowstyle="-", lw=0.5, color="#999999"))
ax.legend(handles=[
    Line2D([], [], marker="o", ls="", color=CATEGORICAL[0], ms=4.5, label="强（≥0.55）"),
    Line2D([], [], marker="o", ls="", color=CATEGORICAL[3], ms=4.5, label="中（0.30–0.55）"),
    Line2D([], [], marker="o", ls="", color=GREY, ms=4.5, label="弱（<0.30）"),
], loc="lower right", handletextpad=0.3, labelspacing=0.25, borderaxespad=0.2)

# ══════════ (b) QWK vs ±1 ══════════
ax2 = fig.add_subplot(gs[0, 1])
for i in range(len(names)):
    ax2.scatter(vals[i], acc[i] * 100, s=24, color=tier(vals[i]),
                edgecolor="white", linewidth=0.5, alpha=0.9, zorder=3)
# 相邻一级"完全随机"的参照：等级数 7 时，随机命中 ±1 的概率
ax2.axhline(3 / 7 * 100, color=GREY, lw=0.8, ls=(0, (4, 2)), zorder=2)
ax2.axvline(mean_qwk, color=GREY, lw=0.8, ls=(0, (4, 2)), zorder=2)
ax2.set_xlim(-0.03, 0.90)
ax2.set_ylim(38, 88)
ax2.set_xlabel("折外 QWK")
ax2.set_ylabel("±1 级准确率（%）")
ax2.grid(color="#F3F3F3", lw=0.4, zorder=0)
ax2.set_axisbelow(True)
# 标出右上两个端点（未重叠，保留）；左下与点重叠的弱信号维标签已省略
pick = [0, 1]
for i in pick:
    ax2.annotate(dim_zh(names[i]), (vals[i], acc[i] * 100),
                 xytext=(4, 5), textcoords="offset points", fontsize=6.0, color="#333333")

tag_panels([ax, ax2])

fig.savefig(os.path.join(ROOT, "figures", "fig_q1_pred_perf.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; strong=%d weak=%d mean=%.4f" % (int((vals >= 0.55).sum()),
      int((vals < 0.30).sum()), mean_qwk))
