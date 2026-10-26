# -*- coding: utf-8 -*-
"""fig_q1_binning — 分位分箱退化诊断与有序回归增益（新增）

左图：50 维的“前 5 个切点跨度 / 极差”，低于 5% 判为退化；
右图：退化维与其余维在两种方法下的 QWK 对比。
数据源：_tmp/ordinal_full.csv（本轮复算）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "code"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams["axes.unicode_minus"] = False

from _figbase import save_fig, set_paper_placement, declutter_axes, dim_zh
import utils as U

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, "_tmp", "ordinal_full.csv"))
Y, sens_cols = U.load_sensory("user_data")

tight = {}
for _, r in df.iterrows():
    y = Y[r["dim"]].values
    y = y[np.isfinite(y)]
    bn = U.Binner().fit(y)
    rng = y.max() - y.min()
    tight[r["dim"]] = (bn.edges[4] - bn.edges[0]) / rng if rng > 0 else 1.0

df["tight"] = df["dim"].map(tight)
df["degenerate"] = df["tight"] < 0.05

fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.6),
                         gridspec_kw={"width_ratios": [1.25, 1]})
set_paper_placement(fig, width_fraction=0.98)

# 左：退化程度分布
ax = axes[0]
ds = df.sort_values("tight")
xx = np.arange(len(ds))
cols = ["#C0392B" if d else "#A9C3DD" for d in ds["degenerate"]]
ax.scatter(ds["tight"], np.zeros(len(ds)) + 0.5, s=26, c=cols,
           edgecolors="white", linewidths=0.4, zorder=3)
for _, r in ds.head(5).iterrows():
    ax.annotate(dim_zh(r["dim"]), (r["tight"], 0.5), textcoords="offset points",
                xytext=(0, 8), ha="center", fontsize=6.6, color="#C0392B")
ax.axvline(0.05, color="#444", ls="--", lw=0.9)
ax.set_xscale("log")
ax.set_xlim(0.003, 2.0)
ax.set_ylim(0, 1)
ax.set_yticks([])
ax.set_xlabel("前 5 个分位切点跨度 / 该维极差", fontsize=8.2)
ax.text(0.055, 0.85, "退化阈值 5%", fontsize=7.2, color="#444")

# 右：两种方法的分组对比
ax = axes[1]
groups = [("退化维\n(n=5)", df[df.degenerate]), ("其余维\n(n=45)", df[~df.degenerate])]
xpos = np.arange(len(groups))
base = [g[1]["qwk_base"].mean() for g in groups]
ordv = [g[1]["qwk_ordinal"].mean() for g in groups]
w = 0.34
ax.bar(xpos - w / 2, base, w, color="#A9C3DD", edgecolor="white", label="回归+分位分箱", zorder=2)
ax.bar(xpos + w / 2, ordv, w, color="#2E5C8A", edgecolor="white", label="有序回归", zorder=2)
for i in range(len(groups)):
    ax.text(xpos[i] - w / 2, base[i] + 0.008, "%.3f" % base[i], ha="center", fontsize=7)
    ax.text(xpos[i] + w / 2, ordv[i] + 0.008, "%.3f" % ordv[i], ha="center", fontsize=7)
ax.set_xticks(xpos)
ax.set_xticklabels([g[0] for g in groups], fontsize=7.8)
ax.set_ylabel("折外 QWK", fontsize=8.2)
ax.set_ylim(0, 0.46)
ax.tick_params(axis="y", labelsize=7.2)
ax.legend(fontsize=7, frameon=False, loc="upper left")
declutter_axes(ax, grid_axis="y")

fig.tight_layout()
save_fig(fig, "figures/fig_q1_binning_degeneracy.png")
print("fig_q1_binning done; degenerate=%d" % int(df.degenerate.sum()))
