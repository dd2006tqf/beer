# -*- coding: utf-8 -*-
"""fig_q2_modules -- 共表达网络：模块结构 + 孤立节点的成因

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) community-spread network -> assets/figures/heatmap (cross-type: network) -> param inherit
(b) max|r| distribution vs threshold -> assets/figures/DensityHeatmap (cross-type) -> param inherit

左图放大并做模块外推（每个社区沿全局质心方向外移），让 5 个主模块之间留出空白；
右图回答"为什么有 44 个孤立节点"：每个节点的最大 |r| 分布，孤立者全部堆在
阈值 0.5 下方，说明孤立是硬阈值截断的产物，而不是这些化合物真的与其余 210 个无关。
附图给出阈值灵敏度（0.40-0.60 的边数与孤立数）。
"""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import networkx as nx
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from _figbase import ROOT, save_fig

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

net = json.load(open(os.path.join(ROOT, "_tmp", "q2_full_network.json"), encoding="utf-8"))
diag = json.load(open(os.path.join(ROOT, "_tmp", "q2_iso_diag.json"), encoding="utf-8"))
nodes, edges = net["nodes"], net["edges"]
comm_sizes = collections.Counter(n["comm"] for n in nodes)

G = nx.Graph()
for n in nodes:
    G.add_node(n["id"], deg=n["deg"], comm=n["comm"], name=n["name"])
for e in edges:
    G.add_edge(e["s"], e["t"], weight=e["w"])

fig = plt.figure(figsize=(7.2, 3.5))
gs = fig.add_gridspec(1, 2, width_ratios=[1.62, 1.0], wspace=0.14,
                      left=0.02, right=0.975, top=0.90, bottom=0.135)
ax1 = fig.add_subplot(gs[0, 0])
ax2 = fig.add_subplot(gs[0, 1])

# ══════════ (a) community-spread network ══════════
comps = sorted(nx.connected_components(G), key=len, reverse=True)
main = comps[0]
H = G.subgraph(main)
pos = nx.spring_layout(H, seed=42, k=1.9, iterations=600, weight="weight")

# 把每个社区沿"全局质心 -> 社区质心"方向外推，制造模块间空白
gc = np.mean([pos[n] for n in H.nodes()], axis=0)
shift = 0.42
for c in set(nx.get_node_attributes(H, "comm").values()):
    mem = [n for n in H.nodes() if H.nodes[n]["comm"] == c]
    if len(mem) < 3:
        continue
    cc = np.mean([pos[n] for n in mem], axis=0)
    d = cc - gc
    nrm = np.linalg.norm(d)
    if nrm < 1e-9:
        continue
    for n in mem:
        pos[n] = pos[n] + shift * d / nrm * min(nrm, 1.0)

xs = np.array([pos[n][0] for n in H.nodes()]); ys = np.array([pos[n][1] for n in H.nodes()])
sx = (xs - xs.min()); sy = (ys - ys.min())
sx = sx / max(sx.max(), 1e-9); sy = sy / max(sy.max(), 1e-9)

for u, v, d in H.edges(data=True):
    ax1.plot([sx[list(H.nodes()).index(u)], sx[list(H.nodes()).index(v)]],
             [sy[list(H.nodes()).index(u)], sy[list(H.nodes()).index(v)]],
             color="#C8D3DE", lw=0.25 + 0.9 * d["weight"], alpha=0.42, zorder=1)

big = [c for c, _ in comm_sizes.most_common(5)]
ccol = {c: CATEGORICAL[i] for i, c in enumerate(big)}
node_list = list(H.nodes())
for k, n in enumerate(node_list):
    d = H.nodes[n]["deg"]
    ax1.scatter(sx[k], sy[k], s=9 + 3.4 * d, color=ccol.get(H.nodes[n]["comm"], "#CBD5E1"),
                edgecolors="white", linewidths=0.45, alpha=0.95, zorder=3)

for i, c in enumerate(big):
    mem = [k for k, n in enumerate(node_list) if H.nodes[n]["comm"] == c]
    if len(mem) < 5:
        continue
    mx_, my_ = sx[mem].mean(), sy[mem].mean()
    r = max(sx[mem].max() - sx[mem].min(), sy[mem].max() - sy[mem].min()) / 2 + 0.045
    ax1.add_patch(plt.Circle((mx_, my_), r, fill=True, facecolor=ccol[c], alpha=0.055,
                             edgecolor=ccol[c], lw=0.8, ls=(0, (3, 2)), zorder=0))
    hub = max((n for n in node_list if H.nodes[n]["comm"] == c),
              key=lambda n: H.nodes[n]["deg"])
    nm = H.nodes[hub]["name"]
    ax1.text(mx_, my_ + r + 0.03, "M%d·%s" % (i + 1, nm if len(nm) <= 13 else nm[:12] + "…"),
             ha="center", va="bottom", fontsize=6.0, color=ccol[c], zorder=6)

ax1.set_xticks([]); ax1.set_yticks([])
for sp in ax1.spines.values():
    sp.set_visible(False)
ax1.set_xlim(-0.10, 1.10); ax1.set_ylim(-0.10, 1.10)
ax1.set_aspect("equal")
ax1.set_title("(a) 最大连通分量：%d 节点 / %d 条边 / 模块外推后布局"
              % (len(main), H.number_of_edges()), loc="left", fontsize=8,
              fontweight="bold", pad=4)

legend = [Patch(facecolor=ccol[c], label="M%d (%d)" % (i + 1, comm_sizes[c]))
          for i, c in enumerate(big)]
legend.append(Patch(facecolor="#CBD5E1", label="小社区"))
ax1.legend(handles=legend, loc="lower left", ncol=3, fontsize=5.9,
           handlelength=0.8, columnspacing=0.7, handletextpad=0.28,
           borderaxespad=0.15, labelspacing=0.22)

# ══════════ (b) 孤立节点的成因 ══════════
allmax = np.array(diag["all_maxr"])
mx = allmax[allmax < float(diag.get("rho", 0.5))]
rho_star = float(diag.get("rho", 0.5))

# 全部 211 个节点的 max|r|；孤立者（<0.5）标红
if allmax is None:
    allmax = np.concatenate([mx, np.full(len(nodes) - len(mx), np.nan)])
    allmax = allmax[np.isfinite(allmax)]

bins = np.arange(0.10, 0.92, 0.04)
ax2.hist(allmax, bins=bins, color="#D6DEE7", edgecolor="white", linewidth=0.5, zorder=2)
below = allmax[allmax < rho_star]
ax2.hist(below, bins=bins, color=CATEGORICAL[1], alpha=0.85, edgecolor="white",
         linewidth=0.5, zorder=3)
ax2.axvline(rho_star, color="#222222", lw=1.0, ls=(0, (4, 3)), zorder=5)
ax2.set_xlim(0.10, 0.90)
ax2.set_xlabel("该化合物与其余 210 个化合物的最大 |r|")
ax2.set_ylabel("化合物数")
ax2.grid(axis="y", color="#F0F0F0", lw=0.4, zorder=0)
ax2.set_axisbelow(True)
ax2.annotate("阈值 ρ = 0.5\n左侧即孤立（%d 个）" % net["n_isolated"],
             xy=(rho_star, ax2.get_ylim()[1] * 0.55), xytext=(0.13, ax2.get_ylim()[1] * 0.80),
             fontsize=6.5, color="#333333", va="center",
             arrowprops=dict(arrowstyle="->", lw=0.6, color="#888888"))
ax2.text(0.555, ax2.get_ylim()[1] * 0.30, "孤立者最大 |r|\n中位 0.444", fontsize=6.2,
         color=CATEGORICAL[1], va="center", ha="left")
ax2.set_title("(b) 为什么有 %d 个孤立节点" % net["n_isolated"], loc="left",
              fontsize=8, fontweight="bold", pad=4)

# 阈值灵敏度小表
sens = diag["rho_sens"]
lines = ["rho   edges  iso"]
for k in ["0.40", "0.45", "0.50", "0.55", "0.60"]:
    v = sens[k]
    mark = "  <-" if abs(float(k) - rho_star) < 1e-9 else ""
    lines.append("%-5s %5d %5d%s" % (k, v["edges"], v["isolated"], mark))
ax2.text(0.985, 0.965, "\n".join(lines), transform=ax2.transAxes, ha="right", va="top",
         fontsize=5.7, color="#444444",
         bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#DDDDDD", lw=0.5))

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_modules.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; main=%d iso=%d" % (len(main), net["n_isolated"]))
