# -*- coding: utf-8 -*-
"""fig_q2_evidence -- 条件增量 vs 模块增量：独立驱动还是模块内替代

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) paired dumbbell (cond vs mod per candidate) -> assets/figures/PairedBoxScatter -> param inherit
(b) module-share scatter (mod/(cond+mod) vs cond) -> assets/figures/MarginalDensity (cross-type) -> param inherit

原来把 18 个点塞进一张二维散点，标注互相遮挡，也看不出 A/B/C 分级。
改为两个互补视图：
(a) 每个候选一对点，蓝=条件增量（单独置换）、橙=模块增量（整社区置换），
    连线长度就是"这个化合物有多少作用被同模块伙伴分担"；
(b) 把分担比例做成横轴，条件增量做纵轴，分级用颜色，频率用点径，
    左上＝独立驱动，右上＝模块整体贡献，左下＝可替代。
统计口径：置换后 50 维平均预测值的绝对变化；模块增量为空表示该化合物所在社区
没有其他成员，此时无法定义，只画条件增量并在 (a) 中标注。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from _figbase import ROOT, save_fig, dim_zh

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

ev = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_evidence_permutation.json"), encoding="utf-8"))
abc = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_abc_grades.json"), encoding="utf-8"))
GRADE = {(r["dim"], r["rank"]): r["grade"] for r in abc}
GCOL = {"A": CATEGORICAL[0], "B": CATEGORICAL[3], "C": GREY}

rows = []
for dim, recs in ev.items():
    top_cond = max(r["cond"] for r in recs)
    for r in recs:
        rows.append(dict(dim=dim, rank=r["rank"], comp=r["compound"],
                         cond=r["cond"], mod=r["mod"], freq=r["freq"],
                         n_mates=r["n_mates"], top=top_cond,
                         grade=GRADE.get((dim, r["rank"]), "C")))

fig = plt.figure(figsize=(7.0, 3.55))
gs = fig.add_gridspec(1, 2, width_ratios=[1.30, 1.0], wspace=0.42,
                      left=0.115, right=0.985, top=0.90, bottom=0.155)

# ══════════ (a) dumbbell ══════════
ax = fig.add_subplot(gs[0, 0])
ypos = []
labels = []
ylab_dim = []
y = 0.0
dim_order = list(ev.keys())
for dim in dim_order:
    recs = [r for r in rows if r["dim"] == dim]
    for r in recs:
        ypos.append(y); labels.append(r); y += 1.0
    ylab_dim.append((y - len(recs) / 2.0 - 0.5, dim))
    y += 0.95   # separator between dimensions

for yi, r in zip(ypos, labels):
    c = GCOL[r["grade"]]
    cond = r["cond"] * 100
    if r["mod"] is None:
        ax.scatter([cond], [yi], s=30, marker="o", facecolor="white", edgecolor=c,
                   linewidth=1.1, zorder=4)
        ax.plot([cond - 1.1, cond], [yi, yi], color=c, lw=1.0, zorder=3)
        ax.text(cond + 1.4, yi, "单点模块", fontsize=5.6, color=GREY, va="center")
    else:
        mod = r["mod"] * 100
        ax.plot([min(cond, mod), max(cond, mod)], [yi, yi], color=c, lw=1.1,
                alpha=0.45, zorder=2)
        ax.scatter([cond], [yi], s=26, color=CATEGORICAL[0], edgecolor="white",
                   linewidth=0.6, zorder=5)
        ax.scatter([mod], [yi], s=26, marker="s", color=CATEGORICAL[3],
                   edgecolor="white", linewidth=0.6, zorder=5)
    ax.text(-0.45, yi, "%d·%s" % (r["rank"], r["comp"].replace("_", " ")),
            ha="right", va="center", fontsize=5.9, color="#333333")

for yy, dim in ylab_dim:
    ax.text(-9.2, yy + 0.28, dim_zh(dim), ha="left", va="center", fontsize=6.9,
            fontweight="bold", color="#111111")

ax.set_yticks([])
ax.set_ylim(-1.0, max(ypos) + 0.9)
ax.set_xlim(-9.0, 15.0)
ax.set_xlabel("置换后 50 维平均预测变化（%）")
ax.grid(axis="x", color="#EFEFEF", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.spines["left"].set_visible(False)

from matplotlib.lines import Line2D
ax.legend(handles=[
    Line2D([], [], marker="o", ls="", color=CATEGORICAL[0], ms=5, label="条件增量"),
    Line2D([], [], marker="s", ls="", color=CATEGORICAL[3], ms=5, label="模块增量"),
    Line2D([], [], marker="o", ls="", markerfacecolor="white", markeredgecolor=GREY,
           ms=5, label="模块不可定义"),
], loc="lower right", handletextpad=0.35, labelspacing=0.25, borderaxespad=0.2)

# ══════════ (b) module-share scatter ══════════
axB = fig.add_subplot(gs[0, 1])
for r in rows:
    if r["mod"] is None:
        continue
    share = r["mod"] / (r["cond"] + r["mod"])
    c = GCOL[r["grade"]]
    axB.scatter(share, r["cond"] * 100, s=18 + 90 * r["freq"], color=c,
                edgecolor="white", linewidth=0.6, alpha=0.9, zorder=4)
axB.axvline(0.5, color=GREY, lw=0.7, ls=(0, (4, 3)), zorder=2)
axB.axhline(np.median([r["cond"] for r in rows if r["mod"] is not None]) * 100,
            color=GREY, lw=0.7, ls=(0, (2, 3)), zorder=2)
axB.set_xlim(-0.02, 1.02)
axB.set_xlabel("模块分担比例 = 模块增量 / (条件 + 模块)")
axB.set_ylabel("条件增量（%）")
axB.grid(color="#F3F3F3", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.text(0.03, 0.94, "独立驱动", transform=axB.transAxes, fontsize=6.4,
         color=CATEGORICAL[0], va="top")
axB.text(0.97, 0.94, "模块整体贡献", transform=axB.transAxes, fontsize=6.4,
         color=CATEGORICAL[3], va="top", ha="right")
axB.text(0.97, 0.06, "可替代", transform=axB.transAxes, fontsize=6.4,
         color=GREY, va="bottom", ha="right")

axB.legend(handles=[Line2D([], [], marker="o", ls="", color=GCOL[g], ms=5,
                           label="%s 级（%d 个）" % (g, sum(1 for r in rows if r["grade"] == g)))
                    for g in ("A", "B", "C")],
           loc="lower left", handletextpad=0.35, labelspacing=0.25,
           borderaxespad=0.25)

for ax_, tag in ((ax, "(a)"), (axB, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.028, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_evidence.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
nA = sum(1 for r in rows if r["grade"] == "A")
print("saved; rows=%d A=%d B=%d C=%d" % (len(rows), nA,
      sum(1 for r in rows if r["grade"] == "B"), sum(1 for r in rows if r["grade"] == "C")))
