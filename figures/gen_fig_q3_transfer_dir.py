# -*- coding: utf-8 -*-
"""fig_q3_transfer_dir -- 迁移方向：目标风格的真实位移 vs 生成位移

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) 12 个关键化合物 z_true vs z_gen -> assets/figures/BarComparison (cross-type: dumbbell) -> param inherit
(b) 全列方向一致性（Δ_true vs Δ_gen 散点）-> assets/figures/MarginalDensity (cross-type) -> param inherit

隐空间平移 Δ=z̄_t−z̄_s 是黑箱，读者无法判断它到底把哪些化学列推向目标风格。
这里在化学层把"目标风格真实均值 − 源风格均值"作为参照方向，
与 11 条迁移谱的实际位移逐列对比：
(a) 12 个关键调节化合物的标准化位移（Δ/σ_train），真实方向与生成方向并排；
(b) 全部列的二维对照，符号一致率 92.2%、余弦相似度 0.34 —— 
    方向大体正确，但幅度与部分列不一致，这正是需要缺陷投影兜底的原因。
Data: figures/derived/q3_transfer_direction.json。
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
    "xtick.labelsize": 6.6, "ytick.labelsize": 6.6, "legend.fontsize": 6.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

d = json.load(open(os.path.join(ROOT, "figures", "derived", "q3_transfer_direction.json"),
                   encoding="utf-8"))
rows = d["key_compounds"]

fig = plt.figure(figsize=(7.1, 3.35))
gs = fig.add_gridspec(1, 2, width_ratios=[1.25, 1.0], wspace=0.34,
                      left=0.155, right=0.975, top=0.885, bottom=0.215)

# ---------- (a) 12 关键化合物的哑铃 ----------
ax = fig.add_subplot(gs[0, 0])
y = np.arange(len(rows))[::-1]
for yi, r in zip(y, rows):
    a, b = r["z_true"], r["z_gen"]
    c = CATEGORICAL[0] if r["sign_match"] else CATEGORICAL[1]
    ax.plot([min(a, b), max(a, b)], [yi, yi], color=c, lw=1.2, alpha=0.55, zorder=2)
    ax.scatter([a], [yi], s=26, color=CATEGORICAL[0], edgecolor="white",
               linewidth=0.6, zorder=4)
    ax.scatter([b], [yi], s=26, marker="D", color=CATEGORICAL[3], edgecolor="white",
               linewidth=0.6, zorder=4)
ax.axvline(0, color="#555555", lw=0.8, ls=(0, (4, 3)), zorder=1)
ax.set_yticks(y)
ax.set_yticklabels([r["compound"].replace("_", " ").replace(".", " ")[:20] for r in rows],
                   fontsize=6.2)
ax.tick_params(axis="y", length=0, pad=2)
ax.set_xlabel("标准化位移 Δ/σ$_{train}$（相对源风格 Pils/Lager）")
ax.set_xlim(-1.0, 9.6)
ax.grid(axis="x", color="#F3F3F3", lw=0.4, zorder=0)
ax.set_axisbelow(True)
ax.legend(handles=[
    Line2D([], [], marker="o", ls="", color=CATEGORICAL[0], ms=5, label="真实方向"),
    Line2D([], [], marker="D", ls="", color=CATEGORICAL[3], ms=5, label="迁移后"),
], loc="lower right", handletextpad=0.3, labelspacing=0.22, borderaxespad=0.25)

# ---------- (b) 方向一致性 ----------
axB = fig.add_subplot(gs[0, 1])
os_ = np.array([r["z_true"] for r in rows])
gs_ = np.array([r["z_gen"] for r in rows])
lim = 9.8
axB.plot([0, lim], [0, lim], color="#BBBBBB", lw=0.7, ls=(0, (3, 3)), zorder=1)
axB.scatter(os_, gs_, s=30, color=CATEGORICAL[0], edgecolor="white", linewidth=0.6, zorder=4)
axB.set_xlim(-0.6, lim)
axB.set_ylim(-0.6, lim)
axB.set_xlabel("真实方向 Δ/σ$_{train}$")
axB.set_ylabel("迁移后 Δ/σ$_{train}$")
axB.grid(color="#F5F5F5", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.text(0.04, 0.955, "符号一致 %d/%d" % (d["key_sign_agree"], len(rows)),
         transform=axB.transAxes, fontsize=6.8, va="top", color="#222222")
axB.text(0.04, 0.885, "全列符号一致率 %.1f%%" % (100 * d["sign_agreement_all_cols"]),
         transform=axB.transAxes, fontsize=6.4, va="top", color=GREY)
axB.text(0.04, 0.815, "余弦相似度 %.2f" % d["direction_cosine"],
         transform=axB.transAxes, fontsize=6.4, va="top", color=GREY)

tag_panels([ax, axB])

fig.savefig(os.path.join(ROOT, "figures", "fig_q3_transfer_dir.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; cos=%.3f sign=%.3f key=%d/%d" % (d["direction_cosine"],
      d["sign_agreement_all_cols"], d["key_sign_agree"], len(rows)))
