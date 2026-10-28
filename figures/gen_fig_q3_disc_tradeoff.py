# -*- coding: utf-8 -*-
"""fig_q3_disc_tradeoff —— 判别辅助损失的权衡曲线

横轴 λ（对数刻度），左轴：隐空间风格线性分类准确率（0~1）；右轴：生成谱 KS 均值。
核心信息：λ 从 0 增大时，隐空间风格可辨识性从随机水平跃升到近 100%，
但生成分布保真单调变差——这是"隐空间解耦"与"分布保真"的直接权衡。

数据源：figures/derived/q3_disc_lambda_*.json（seed 42，600 轮）。
"""
import os
import sys
import glob
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from _figbase import ROOT, PALETTE, save_fig

recs = []
for f in glob.glob(os.path.join(ROOT, "figures", "derived", "q3_disc_lambda_*_seed42.json")):
    recs.append(json.load(open(f, encoding="utf-8")))
# 兼容未带 seed 后缀的早期文件名
for f in glob.glob(os.path.join(ROOT, "figures", "derived", "q3_disc_lambda_*.json")):
    if "_seed" not in os.path.basename(f):
        d = json.load(open(f, encoding="utf-8"))
        if d.get("seed", 42) == 42:
            recs.append(d)

seen = {}
for d in recs:
    seen[d["lam"]] = d
recs = [seen[k] for k in sorted(seen)]
lams = np.array([d["lam"] for d in recs])
acc = np.array([d["latent"]["lin_acc"] for d in recs])
ks = np.array([d["ks_mean_3style"] for d in recs])
recon = np.array([d["recon_mse"] for d in recs])

plt.rcParams.update({"axes.unicode_minus": False, "font.size": 7.2})
fig, ax = plt.subplots(figsize=(5.6, 2.9), layout="constrained")

x = np.arange(len(lams))
ax.bar(x, acc, width=0.52, color=PALETTE_LIGHT[0] if False else "#A9C3DD",
       edgecolor="white", label="隐空间风格分类准确率", zorder=2)
ax.axhline(1 / 22, color="#888888", ls=":", lw=1.0, zorder=3)
ax.text(len(lams) - 0.45, 1 / 22 + 0.03, "随机基线 1/22", fontsize=6.0, ha="right", color="#666666")
for xi, a in zip(x, acc):
    ax.text(xi, a + 0.02, "%.0f%%" % (a * 100), ha="center", fontsize=6.6)

ax.set_xticks(x)
ax.set_xticklabels(["0\n(现状)"] + ["%.2f" % v for v in lams[1:]])
ax.set_xlabel("判别辅助损失权重 λ")
ax.set_ylabel("隐空间风格分类准确率")
ax.set_ylim(0, 1.18)

ax2 = ax.twinx()
ax2.plot(x, ks, "o-", color=PALETTE[2], lw=1.6, ms=4.6, label="生成谱 KS（越低越好）", zorder=4)
for xi, v in zip(x, ks):
    ax2.annotate("%.3f" % v, (xi, v), textcoords="offset points", xytext=(0, -12),
                 ha="center", fontsize=6.2, color=PALETTE[2])
ax2.set_ylabel("生成谱 KS 均值", color=PALETTE[2])
ax2.tick_params(axis="y", colors=PALETTE[2])
ax2.set_ylim(0.34, 0.50)

ax.grid(axis="y", color="#E6E9ED", lw=0.5, zorder=0)
ax.set_axisbelow(True)
for sp in ("top",):
    ax.spines[sp].set_visible(False)
    ax2.spines[sp].set_visible(False)

h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=6.4, frameon=False)

save_fig(fig, "figures/fig_q3_disc_tradeoff.png")
print("lams", list(lams))
print("acc", list(np.round(acc, 3)))
print("ks", list(np.round(ks, 4)))
print("recon", list(np.round(recon, 4)))
