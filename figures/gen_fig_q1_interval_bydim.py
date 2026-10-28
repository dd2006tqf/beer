# -*- coding: utf-8 -*-
"""fig_q1_interval_bydim —— 逐维 90% 区间的覆盖率与宽度（对标标杆图5）

左：(a) 50 维覆盖率，按香气/风味/口感三行分组、组内按覆盖率排序，
    分位数回归与 split-conformal 两色点并列，0.90 名义水平虚线；
右：(b) 对应逐维区间宽度，同序。

数据源：figures/derived/q1_prediction_interval.json::by_dim（两种口径各 50 维）。
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from _figbase import ROOT, PALETTE, dim_zh, save_fig

d = json.load(open(os.path.join(ROOT, "figures", "derived", "q1_prediction_interval.json"),
                   encoding="utf-8"))
q, c = d["quantile_regression"]["by_dim"], d["conformal"]["by_dim"]
sens = list(c.keys())

def grp(s):
    return "A" if s.startswith("A_") else ("F" if s.startswith("F_") else "X")

GROUPS = [("A", "香气 (15)", PALETTE[0]), ("F", "风味 (15)", PALETTE[1]), ("X", "口感/缺陷 (20)", PALETTE[3])]

fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.9), layout="constrained")
plt.rcParams.update({"axes.unicode_minus": False, "font.size": 6.6})

for ax, key, ttl, unit in ((axes[0], "coverage", "(a) 逐维覆盖率", "coverage"),
                           (axes[1], "width", "(b) 逐维区间宽度", "width")):
    y0 = 0
    ticks, labels, sep = [], [], []
    for g, gname, col in GROUPS:
        ks = [s for s in sens if grp(s) == g]
        ks = sorted(ks, key=lambda s: -c[s][key])
        ys = np.arange(y0, y0 + len(ks))
        ax.scatter([q[s][key] for s in ks], ys, s=13, color=PALETTE[2], alpha=0.85,
                   label="分位数回归" if y0 == 0 else None, zorder=3, linewidths=0)
        ax.scatter([c[s][key] for s in ks], ys, s=15, color=col, alpha=0.95,
                   label="共形校准" if y0 == 0 else None, zorder=4, linewidths=0)
        ticks += list(ys)
        labels += [dim_zh(s) for s in ks]
        y0 += len(ks)
        sep.append(y0 - 0.5)
    ax.set_yticks(ticks)
    ax.set_yticklabels(labels, fontsize=4.5)
    ax.invert_yaxis()
    for s in sep[:-1]:
        ax.axhline(s, color="#CCCCCC", lw=0.7, ls="--", zorder=1)
    if key == "coverage":
        ax.axvline(0.90, color=PALETTE[1], lw=1.2, ls="--", zorder=2)
        ax.set_xlim(0.55, 1.02)
        ax.set_xlabel("实测覆盖率（虚线 = 名义 90%）")
    else:
        ax.set_xlabel("区间宽度（标准化单位）")
    ax.set_title(ttl, fontsize=8.0, loc="left", pad=4)
    ax.grid(axis="x", color="#E6E9ED", lw=0.5, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)

axes[0].legend(loc="lower left", fontsize=6.2, frameon=False, markerscale=1.4)
save_fig(fig, "figures/fig_q1_interval_bydim.png")
print("dims", len(sens))
print("cov min/max conformal", min(c[s]["coverage"] for s in sens), max(c[s]["coverage"] for s in sens))
print("width max dim", max(sens, key=lambda s: c[s]["width"]), max(c[s]["width"] for s in sens))
print("width min dim", min(sens, key=lambda s: c[s]["width"]), min(c[s]["width"] for s in sens))
