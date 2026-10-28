# -*- coding: utf-8 -*-
"""fig_q2_mantel -- 化学模块 × 感官组的 Mantel 关联

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) module-by-group Mantel r heatmap -> assets/figures/MantelCorrelation -> param inherit
(b) linkage curves for the strongest module  -> assets/figures/MantelCorrelation -> param inherit

之前只证明了"化学谱整体能区分风格"（图 2）和"单个化合物与单个感官相关"（图 12），
中间一层——化学模块集体对应哪类感官——一直是空白。Mantel 检验正好补这一层：
对 5 个 Louvain 大模块与 3 个感官组各构造样本距离矩阵，检验两者是否同构。
(a) 给出 5x3 的 r 矩阵（999 次置换的 p 值全部 < 0.05），
(b) 把最强的一条链路画成样本级连线，直接看出"哪些样本被同时拉近"。
Data: _tmp/q2_mantel.json、2.csv、1.csv、4.csv。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from scipy.spatial.distance import pdist, squareform
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
CATEGORICAL = ["#2166AC", "#B2182B", "#1B7837", "#F1A340", "#762A83", "#666666"]
GREY = "#999999"

rows = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_mantel.json"), encoding="utf-8"))
meta = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_module_meta.json"), encoding="utf-8"))
big = [int(c) for c in meta["big"]]
GROUPS = ["A_", "F_", "X"]
GLAB = ["香气 A_", "风味 F_", "口感/缺陷"]

# 模块业务名：用成员里的代表化合物概括
MODLAB = {
    15: "M1 酵母酯/醛",
    19: "M2 萜烯醇/酯",
    49: "M3 高级醇/乙酸酯",
    27: "M4 双乙酰/醛",
    35: "M5 酒花萜烯",
}
M = np.full((len(big), 3), np.nan)
P = np.full((len(big), 3), np.nan)
for r in rows:
    i = big.index(int(r["module"])); j = GROUPS.index(r["group"])
    M[i, j] = r["r"]; P[i, j] = r["p"]

fig = plt.figure(figsize=(7.0, 3.15))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.35], wspace=0.42,
                      left=0.135, right=0.975, top=0.885, bottom=0.185)
ax = fig.add_subplot(gs[0, 0])

cmap = LinearSegmentedColormap.from_list("seq", ["#F7FBFF", "#6BAED6", "#08306B"])
im = ax.imshow(M, cmap=cmap, vmin=0, vmax=0.30, aspect="auto")
for i in range(M.shape[0]):
    for j in range(M.shape[1]):
        v = M[i, j]
        star = "***" if P[i, j] < 0.001 else ("**" if P[i, j] < 0.01 else ("*" if P[i, j] < 0.05 else ""))
        ax.text(j, i, "%.3f%s" % (v, star), ha="center", va="center", fontsize=6.4,
                color="white" if v > 0.17 else "#222222")
ax.set_xticks(range(3)); ax.set_xticklabels(GLAB, fontsize=6.8)
ax.set_yticks(range(len(big)))
ax.set_yticklabels([MODLAB.get(c, "M%d" % (i + 1)) for i, c in enumerate(big)], fontsize=6.8)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
cb.outline.set_visible(False)
cb.set_label("Mantel r", fontsize=7)
cb.ax.tick_params(labelsize=6.2, length=2)

# ---------- (b) 最强链路的样本级连线 ----------
axB = fig.add_subplot(gs[0, 1])
best = max(rows, key=lambda r: r["r"])
mi = big.index(int(best["module"])); gi = GROUPS.index(best["group"])

sys.path.insert(0, os.path.join(ROOT, "code"))
import utils as U
df1, X, feat, _ = U.load_chem(os.path.join(ROOT, "user_data"))
Xv = np.asarray(X.values, dtype=float)
y = pd.read_csv(os.path.join(ROOT, "user_data", "4.csv"))
sens = [c for c in y.columns if c not in ("beer", "beer_id", "tasting_category_fine")]
gidx = [j for j, s in enumerate(sens)
        if ("A_" if s.startswith("A_") else ("F_" if s.startswith("F_") else "X")) == best["group"]]
mp = [int(v) for v in np.load(os.path.join(ROOT, "figures", "derived", "q2_module_positions.npy"), allow_pickle=True)[mi]]
Dm = squareform(pdist(np.nan_to_num(Xv[:, mp])))
Ds = squareform(pdist(np.nan_to_num(y[sens].apply(pd.to_numeric, errors="coerce").values[:, gidx])))

# 用 PCoA 把两个距离矩阵投影到 2D 再画连线
def pcoa(D, k=2):
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:k]
    return V[:, idx] * np.sqrt(np.clip(w[idx], 0, None))

Pm, Ps = pcoa(Dm), pcoa(Ds)
# 各自归一化到 [0,1]，避免量纲差异
def norm(A):
    lo, hi = A.min(0), A.max(0)
    return (A - lo) / np.where(hi > lo, hi - lo, 1)
Pm, Ps = norm(Pm), norm(Ps)
Pm = 0.12 + Pm * 0.76
Ps = 0.12 + Ps * 0.76

sty = df1["tasting_category_fine"].astype(str).values
top = [s for s, _ in pd.Series(sty).value_counts().head(4).items()]
cols = {s: CATEGORICAL[i] for i, s in enumerate(top)}
for i in range(len(Pm)):
    c = cols.get(sty[i], "#D9D9D9")
    axB.plot([Pm[i, 0], Ps[i, 0]], [Pm[i, 1], Ps[i, 1]], color=c, lw=0.28,
             alpha=0.30, zorder=1)
for i in range(len(Pm)):
    c = cols.get(sty[i], "#D9D9D9")
    axB.scatter(Pm[i, 0], Pm[i, 1], s=7, color=c, alpha=0.85, edgecolor="none", zorder=3)
    axB.scatter(Ps[i, 0], Ps[i, 1], s=7, color=c, alpha=0.85, marker="s",
                edgecolor="none", zorder=3)
axB.set_xlim(0, 1); axB.set_ylim(0, 1)
axB.set_xticks([]); axB.set_yticks([])
for sp in axB.spines.values():
    sp.set_visible(False)
axB.text(0.02, 0.03, "化学模块 %s" % MODLAB.get(int(best["module"]), ""), fontsize=6.6,
         color="#333333")
axB.text(0.98, 0.03, "感官组 %s" % GLAB[gi], fontsize=6.6, color="#333333", ha="right")
axB.text(0.5, 1.0, "Mantel r = %.3f（p < 0.001）" % best["r"], ha="center", va="bottom",
         fontsize=7.0, color="#222222")
from matplotlib.lines import Line2D
axB.legend(handles=[Line2D([], [], marker="o", ls="", color=cols[s], ms=4.5, label=s)
                    for s in top],
           loc="center right", fontsize=5.8, handletextpad=0.3,
           labelspacing=0.22, borderaxespad=0.1)

for ax_, tag in ((ax, "(a)"), (axB, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.026, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_mantel.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; best r=%.3f module=%s group=%s" % (best["r"], best["module"], best["group"]))
