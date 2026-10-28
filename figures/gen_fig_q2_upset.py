# -*- coding: utf-8 -*-
"""fig_q2_upset -- 三方法 Top-3 的一致结构（UpSet）

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) UpSet intersection bars + dot matrix -> UpSet via assets/figures/ConfusionMatrix -> param inherit
(b) per-dimension agreement strip          -> assets/figures/BarCategorical -> param inherit

图 14 用 0.186 这一个标量概括跨方法一致性，读者无从判断"不一致"到底长什么样。
把它拆成集合交集就一目了然：50 维里三法全一致 0 维、恰好两法重合 21 维、
两两有交集但三法不同 22 维、三法完全无交集 7 维。这说明 SHAP / 交叉相关 / RF
是从三种不同角度接近同一批化合物，而不是同一答案的三次重复。
Data: _tmp/q2_upset.json（三方法 Top-3 由 problem2.py 同一证据矩阵重算）。
"""
import os, sys, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
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

d = json.load(open(os.path.join(ROOT, "_tmp", "q2_upset.json"), encoding="utf-8"))
sens = d["sens"]
M = d["methods"]
TAGS = ["shap", "corr", "rf"]
LAB = {"shap": "SHAP", "corr": "交叉相关", "rf": "随机森林"}

# 每维：三方法交集大小
inter = []
pair = []
for j in range(len(sens)):
    s = {t: set(M[t][j]) for t in TAGS}
    inter.append(len(s["shap"] & s["corr"] & s["rf"]))
    pair.append(max(len(s[a] & s[b]) for a, b in itertools.combinations(TAGS, 2)))
inter = np.array(inter); pair = np.array(pair)

fig = plt.figure(figsize=(7.0, 3.35))
gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 1.0], height_ratios=[2.4, 1.0],
                      left=0.085, right=0.975, top=0.885, bottom=0.20,
                      wspace=0.34, hspace=0.10)

# ---------- (a) UpSet ----------
axT = fig.add_subplot(gs[0, 0])
combos = [("shap", "corr", "rf"), ("shap", "corr"), ("shap", "rf"), ("corr", "rf"),
          ("shap",), ("corr",), ("rf",)]
counts = []
for cb in combos:
    c = 0
    for j in range(len(sens)):
        s = {t: set(M[t][j]) for t in TAGS}
        inall = all((t in cb) for t in TAGS if t in cb)
        excl = all(t not in cb for t in TAGS if t not in cb)
        # 严格 a∩b∩c 组合：cb 中方法全有交集，cb 外方法无交集
        ok = True
        for t in cb:
            if not all(any(x in s[u] for u in cb) for x in s[t]):
                ok = False; break
        if not ok: continue
        for t in TAGS:
            if t not in cb:
                if any(len(s[t] & s[u]) > 0 for u in cb):
                    ok = False; break
        if ok: c += 1
    counts.append(c)
# 按"交集深度"分层（与 _tmp/q2_upset.json 的 counts 口径一致）
BARS = ["三法有共同候选", "两对各自重合", "仅一对重合", "三法互斥"]
BARV = [int((inter >= 1).sum()), int(((inter == 0) & (pair >= 2)).sum()),
        int(((inter == 0) & (pair == 1)).sum()), int((pair == 0).sum())]
xs = np.arange(len(BARS))
axT.bar(xs, BARV, width=0.58, color=[CATEGORICAL[0], CATEGORICAL[3], GREY, CATEGORICAL[1]],
        edgecolor="white", linewidth=0.6, zorder=3)
for x, v in zip(xs, BARV):
    axT.text(x, v + 0.4, str(v), ha="center", fontsize=7, color="#222222")
axT.set_xticks(xs); axT.set_xticklabels(BARS, fontsize=6.8)
axT.set_ylabel("感官维度数")
axT.set_ylim(0, max(BARV) * 1.22)
axT.grid(axis="y", color="#F3F3F3", lw=0.4, zorder=0)
axT.set_axisbelow(True)

# 点阵：三种典型组合
axM = fig.add_subplot(gs[1, 0], sharex=axT)
COMB = [[1, 1, 1], [1, 1, 0], [1, 0, 0], [0, 0, 0]]
for xi, cb in enumerate(COMB):
    for yi, on in enumerate(cb[::-1]):
        axM.scatter(xi, yi, s=32, color=CATEGORICAL[0] if on else "#DDDDDD",
                    edgecolor="white", linewidth=0.6, zorder=3)
    ys = [yi for yi, on in enumerate(cb[::-1]) if on]
    if len(ys) > 1:
        axM.plot([xi, xi], [min(ys), max(ys)], color=CATEGORICAL[0], lw=1.2, zorder=2)
axM.set_yticks([0, 1, 2]); axM.set_yticklabels([LAB[t] for t in TAGS[::-1]], fontsize=6.4)
axM.set_ylim(-0.7, 2.7)
axM.tick_params(axis="y", length=0, pad=2)
axM.tick_params(axis="x", labelbottom=False)
for s in axM.spines.values():
    s.set_visible(False)

# ---------- (b) 逐维一致度 ----------
axB = fig.add_subplot(gs[:, 1])
order = np.argsort(-(inter * 2 + pair))
vals = inter[order]
axB.barh(np.arange(len(vals)), vals, color=CATEGORICAL[0], alpha=0.85,
         edgecolor="none", height=0.72, zorder=3)
axB.barh(np.arange(len(vals)), pair[order] - vals, left=vals, color="#D8E2EC",
         edgecolor="none", height=0.72, zorder=2)
axB.set_yticks([])
axB.set_xlim(0, 3.4)
axB.set_xlabel("单维三方法 Top-3 的重合数")
axB.set_ylabel("50 个感官维度（按一致度降序）", fontsize=7.4)
axB.grid(axis="x", color="#F3F3F3", lw=0.4, zorder=0)
axB.set_axisbelow(True)
axB.invert_yaxis()
n0 = int((pair == 0).sum())
axB.axhspan(len(vals) - n0 - 0.5, len(vals) - 0.5, color=CATEGORICAL[1], alpha=0.06, lw=0)
axB.text(3.28, len(vals) - n0 / 2 - 0.5, "%d 维\n无交集" % n0, ha="right", va="center",
         fontsize=6.2, color=CATEGORICAL[1])
axB.text(0.02, 0.02, "浅色 = 次高的一对重合", transform=axB.transAxes, fontsize=6.2,
         color=GREY)

for ax_, tag in ((axT, "(a)"), (axB, "(b)")):
    bb = ax_.get_position()
    fig.text((bb.x0 + bb.x1) / 2, 0.028, tag, ha="center", va="bottom",
             fontsize=8.5, fontweight="bold", color="#222222")

axM.text(-0.62, 2.35, "上三行示意：哪种方法参与重合", fontsize=5.8, color=GREY,
         ha="left", va="top")

fig.savefig(os.path.join(ROOT, "figures", "fig_q2_upset.png"), dpi=400,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved; all3=%d exactly2=%d only-pair=%d none=%d" % tuple(BARV))
