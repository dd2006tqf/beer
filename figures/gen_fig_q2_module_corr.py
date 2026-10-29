# -*- coding: utf-8 -*-
"""fig_q2_module_corr -- 按模块排序的相关矩阵：模块是真实的相关块

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) module-ordered correlation heatmap -> assets/figures/GroupedCorrelationMatrix -> param inherit
(b) within vs between module |r| distribution -> assets/figures/GroupedViolin -> param inherit

图 11 用布局和模块度 Q=0.6246 说明"存在模块"，但那是算法输出的自证。
这张图换一个角度：把 211x211 的相关矩阵按模块成员重排，如果模块是真的，
对角线附近应出现成片的高相关方块，块间应明显变淡。
(b) 把"块内 |r|"与"块间 |r|"的分布并排，用中位数与检验把这件事量化。
Data: 2.csv + _tmp/q2_full_network.json（模块归属）。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
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
CATEGORICAL = ["#2166AC", "#B2182C", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

sys.path.insert(0, os.path.join(ROOT, "code"))
import utils as U, params as P

df1, X, feat, _ = U.load_chem(os.path.join(ROOT, "user_data"))
raw = pd.read_csv(os.path.join(ROOT, "user_data", "2.csv"))
R = raw.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").values.astype(float)
net = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_full_network.json"), encoding="utf-8"))
comm = {n["name"]: n["comm"] for n in net["nodes"]}

c_idx = [i for i, f in enumerate(feat) if f not in P.PHYSICOCHEM_COLS and f not in P.AGG_COLS]
import collections
cnt = collections.Counter(comm.values())
big = [c for c, _ in cnt.most_common(5)]

order, blocks = [], []
for c in big:
    mem = [i for i in c_idx if comm.get(feat[i], -1) == c]
    order += mem; blocks.append((len(order) - len(mem), len(order)))
rest = [i for i in c_idx if i not in set(order)]
order += rest; blocks.append((len(order) - len(rest), len(order)))

Rm = R[np.ix_(order, order)]
fig = plt.figure(figsize=(7.2, 3.45))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 0.78], wspace=0.34,
                      left=0.045, right=0.975, top=0.885, bottom=0.175)
ax = fig.add_subplot(gs[0, 0])
cmap = LinearSegmentedColormap.from_list("div", ["#2166AC", "#F7F7F7", "#B2182C"])
im = ax.imshow(Rm, cmap=cmap, vmin=-0.8, vmax=0.8, interpolation="nearest", aspect="equal")
ax.set_xticks([]); ax.set_yticks([])
for i, (a, b) in enumerate(blocks):
    col = CATEGORICAL[i] if i < 5 else "#CCCCCC"
    ax.add_patch(plt.Rectangle((a - 0.5, a - 0.5), b - a, b - a, fill=False,
                               edgecolor=col, lw=1.0, zorder=5))
    if i < 5:
        ax.text((a + b) / 2 - 0.5, -6, "M%d" % (i + 1), ha="center", va="bottom",
                fontsize=6.4, color=col)
ax.set_title("按 Louvain 模块重排后的 211×211 相关矩阵", fontsize=7.6, pad=10)
cb = fig.colorbar(im, ax=ax, fraction=0.040, pad=0.02)
cb.outline.set_visible(False)
cb.set_label("Pearson r", fontsize=6.8)
cb.ax.tick_params(labelsize=6.0, length=2)

# ---------- (b) 块内 vs 块间 ----------
axB = fig.add_subplot(gs[0, 1])
inside, between = [], []
sets = {}
for i, (a, b) in enumerate(blocks[:5]):
    sets[i] = list(range(a, b))
for i in range(5):
    for j in range(i, 5):
        idx_i = np.array(sets[i]); idx_j = np.array(sets[j])
        sub = np.abs(Rm[np.ix_(idx_i, idx_j)])
        if i == j:
            tri = sub[np.triu_indices_from(sub, 1)]
            inside.extend(tri[np.isfinite(tri)])
        else:
            v = sub[np.isfinite(sub)]
            between.extend(v)
inside = np.array(inside); between = np.array(between)

parts = axB.violinplot([inside, between], positions=[0, 1], widths=0.66,
                       showextrema=False, showmedians=False)
for k, body in enumerate(parts["bodies"]):
    body.set_facecolor(CATEGORICAL[[0, 1][k]])
    body.set_alpha(0.30); body.set_edgecolor("none")
rng = np.random.default_rng(3)
for k, v in enumerate([inside, between]):
    s = rng.choice(v, size=min(2500, v.size), replace=False)
    axB.scatter(k + rng.normal(0, 0.045, s.size), s, s=1.4,
                color=CATEGORICAL[[0, 1][k]], alpha=0.20, edgecolor="none", zorder=3)
    axB.plot([k - 0.24, k + 0.24], [np.median(v)] * 2, color="#222222", lw=1.3, zorder=5)
axB.set_xticks([0, 1])
axB.set_xticklabels(["模块内", "模块间"], fontsize=7.2)
axB.set_ylabel("|Pearson r|")
axB.set_ylim(0, 1.05)
axB.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
axB.set_axisbelow(True)
ratio = np.median(inside) / max(np.median(between), 1e-9)

for ax_, tag in ((ax, "(a)"), (axB, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.026, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_module_corr.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; within med=%.3f between med=%.3f ratio=%.2f"
      % (np.median(inside), np.median(between), ratio))
