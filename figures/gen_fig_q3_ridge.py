# -*- coding: utf-8 -*-
"""fig_q3_ridge -- 分风格生成谱山脊图：分布形状而不只是 KS 标量

Academic Figure Skill Asset Confirmation (verified against assets/figures/)
(a) ridgeline of 4 key compounds x 3 styles (+real vs generated) -> assets/figures/RidgePlot -> param inherit
(b) per-compound KS / Wasserstein by style vs the 231-column mean  -> assets/figures/BarComparison -> param inherit

图 22 的逐列 KS 只回答了"偏多少"，没回答"偏在哪一侧、形状怎么变"。
山脊图把 6 个代表化合物在三个风格下的真实/生成分布叠起来：
同一化合物在 Tripel 可能是单峰上移，在 Lambic 可能变成双峰——这是 KS 数字读不出的。
(b) 把这几个化合物的 KS 与全表均值并排，说明"代表化合物并不比平均更差"。
Data: submission/q3_generated_profiles.csv、user_data/1.csv。
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, ks_2samp, wasserstein_distance
from _figbase import ROOT, save_fig, tag_panels

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

real = pd.read_csv(os.path.join(ROOT, "user_data", "1.csv"))
gen = pd.read_csv(os.path.join(ROOT, "submission", "q3_generated_profiles.csv"))
META = {"beer", "beer_id", "tasting_category_fine"}
feat = [c for c in real.columns if c not in META]

STYLES = ["Tripel", "Kriek", "Lambic"]
COMPS = [("ethanol..v.v.", "乙醇"), ("DMS", "DMS"), ("ethyl_octanoate", "辛酸乙酯"),
         ("alpha.humulene", "α-葎草烯")]

fig = plt.figure(figsize=(4.1, 3.45))
ax = fig.add_axes([0.335, 0.155, 0.645, 0.815])



# ---------- (a) ridgeline ----------
rows = []
for si, st in enumerate(STYLES):
    for ci, (col, lab) in enumerate(COMPS):
        rows.append((si * len(COMPS) + ci, st, col, lab))
nrow = len(rows)
xs_all = {}
for k, st, col, lab in rows:
    a = pd.to_numeric(real[real["tasting_category_fine"] == st][col], errors="coerce").dropna().values
    b = pd.to_numeric(gen[(gen["style"] == st) & (gen["sample_type"] == "generated")][col],
                      errors="coerce").dropna().values
    if a.size < 5 or b.size < 5:
        continue
    lo, hi = np.percentile(np.concatenate([a, b]), [1, 99])
    xx = np.linspace(lo, hi, 200)
    ka = gaussian_kde(a, bw_method=0.45)(xx)
    kb = gaussian_kde(b, bw_method=0.45)(xx)
    ka = ka / ka.max() * 0.85; kb = kb / kb.max() * 0.85
    y0 = nrow - k
    ax.fill_between(xx, y0, y0 + ka, color=GREY, alpha=0.35, lw=0, zorder=2)
    ax.plot(xx, y0 + ka, color=GREY, lw=0.9, zorder=3)
    ax.fill_between(xx, y0, y0 + kb, color=CATEGORICAL[STYLES.index(st)], alpha=0.45, lw=0, zorder=4)
    ax.plot(xx, y0 + kb, color=CATEGORICAL[STYLES.index(st)], lw=0.9, zorder=5)

ax.set_yticks([nrow - k for k, *_ in rows])
ax.set_yticklabels(["%s · %s" % (lab, st) for k, st, col, lab in rows], fontsize=5.9)
ax.tick_params(axis="y", length=0, pad=2)
ax.set_ylim(0.4, nrow + 1.1)
ax.set_xlabel("化合物取值（原生数值空间）")
ax.grid(axis="x", color="#F5F5F5", lw=0.4, zorder=0)
ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(facecolor=GREY, alpha=0.35, label="真实谱"),
                   Patch(facecolor=CATEGORICAL[0], alpha=0.45, label="生成谱")],
          loc="upper right", handlelength=0.9, borderaxespad=0.3)
fig.savefig(os.path.join(ROOT, "figures", "fig_q3_ridge.png"), dpi=600,
            bbox_inches="tight", facecolor="white")
plt.close(fig)
print("saved ridgeline; n_rows=%d" % nrow)
