# -*- coding: utf-8 -*-
"""fig_q2_rho_sweep -- 建图阈值灵敏度：孤立与模块度是一对张力

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) edges / largest component vs rho  -> assets/figures/LineTrend -> param inherit
(b) isolated count and modularity vs rho -> assets/figures/LineTrend (twin axis) -> param inherit

图 11(b) 只用一张小表给了 0.40-0.60 的边数与孤立数，没有说明"为什么选 0.5"。
这里把两件事同时画出来：随阈值升高，边数按幂律塌缩、孤立点线性增加，
而模块度在 0.55-0.60 才见顶——0.5 是"仍有 159 节点连通"与"模块度已达 0.62"
的折中点。这张图把该选择从"取了个值"变成"有取舍依据"。
Data: _tmp/q2_rho_sweep.json（由 2.csv 重算，Louvain 与主流程同参）。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import ROOT, save_fig

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"],
    "font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
    "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 6.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "legend.frameon": False,
    "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
})
AXIS_BLACK = "#222222"   # 纵轴刻度与标题统一用黑色，曲线仍保留彩色
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

rows = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_rho_sweep.json"), encoding="utf-8"))
rho = np.array([r["rho"] for r in rows])
edges = np.array([r["edges"] for r in rows])
iso = np.array([r["iso"] for r in rows])
mod = np.array([r["mod"] for r in rows])
ncomm = np.array([r["ncomm"] for r in rows])
largest = np.array([r["largest"] for r in rows])
CHOSEN = 0.5

fig = plt.figure(figsize=(7.0, 3.05))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.30,
                      left=0.078, right=0.975, top=0.885, bottom=0.195)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# ---- (a) edges + largest component ----
ax1.plot(rho, edges, "-o", color=CATEGORICAL[0], ms=4.5, lw=1.6, zorder=3,
         label="边数")
ax1.tick_params(axis="y", colors=AXIS_BLACK)
ax1.spines["left"].set_color(AXIS_BLACK)
ax1.set_ylim(0, edges.max() * 1.12)
ax1.grid(color="#F3F3F3", lw=0.4, zorder=0)
ax1.set_axisbelow(True)

ax1b = ax1.twinx()
ax1b.plot(rho, largest, "--s", color=CATEGORICAL[3], ms=4, lw=1.4, zorder=3)
ax1b.tick_params(axis="y", colors=AXIS_BLACK)
ax1b.set_ylim(0, 235)
ax1b.spines["right"].set_visible(True)
ax1b.spines["right"].set_color(AXIS_BLACK)
ax1b.spines["left"].set_color(AXIS_BLACK)
ax1b.spines["top"].set_visible(False)

for ax in (ax1, ax1b):
    ax.axvline(CHOSEN, color="#222222", lw=0.9, ls=(0, (4, 3)), zorder=2)
ax1.legend(loc="upper right", handletextpad=0.4, borderaxespad=0.3)

# ---- (b) isolated + modularity ----
ax2.bar(rho, iso, width=0.028, color=CATEGORICAL[1], alpha=0.30,
        edgecolor="none", zorder=2)
ax2.plot(rho, iso, "-o", color=CATEGORICAL[1], ms=4, lw=1.4, zorder=3,
         label="孤立化合物数")
ax2.tick_params(axis="y", colors=AXIS_BLACK)
ax2.spines["left"].set_color(AXIS_BLACK)
ax2.set_ylim(0, iso.max() * 1.20)
ax2.grid(color="#F3F3F3", lw=0.4, zorder=0)
ax2.set_axisbelow(True)

ax2b = ax2.twinx()
ax2b.plot(rho, mod, "--^", color=CATEGORICAL[2], ms=4.5, lw=1.5, zorder=4,
          label="模块度 Q")
ax2b.tick_params(axis="y", colors=AXIS_BLACK)
ax2b.set_ylim(0.35, 0.78)
ax2b.spines["right"].set_visible(True)
ax2b.spines["right"].set_color(AXIS_BLACK)
ax2b.spines["left"].set_color(AXIS_BLACK)
ax2b.spines["top"].set_visible(False)

for ax in (ax2, ax2b):
    ax.axvline(CHOSEN, color="#222222", lw=0.9, ls=(0, (4, 3)), zorder=2)
k = int(np.argmin(np.abs(rho - CHOSEN)))
ax2.legend(loc="upper left", handletextpad=0.4, borderaxespad=0.3)
ax2b.legend(loc="lower right", handletextpad=0.4, borderaxespad=0.3)

for ax, tag in ((ax1, "(a)"), (ax2, "(b)")):
    bb = ax.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.028, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_rho_sweep.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; rho=0.5 -> edges=%d iso=%d Q=%.4f largest=%d"
      % (edges[k], iso[k], mod[k], largest[k]))
