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
from _figbase import ROOT, PALETTE, save_fig, tag_panels

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

BLACK = "#000000"
plt.rcParams.update({"axes.unicode_minus": False, "font.size": 7.2,
                     "axes.labelcolor": BLACK, "xtick.color": BLACK,
                     "ytick.color": BLACK, "text.color": BLACK,
                     "axes.edgecolor": BLACK, "mathtext.fontset": "dejavusans",
                     "font.sans-serif": ["SimHei", "Arial", "DejaVu Sans"]})

# 左右并排的两张权衡曲线：左面板看隐空间是否被修好，右面板看保真付出的代价；
# 两图共用 x 轴（λ 的五个取值），并在 λ=0.02 处同时画推荐折中档的竖线。
fig, (axA, axB) = plt.subplots(1, 2, figsize=(6.9, 2.85),
                               gridspec_kw={"width_ratios": [1.0, 1.0],
                                            "wspace": 0.30},
                               layout="constrained")

x = np.arange(len(lams))
labels = ["0\n(现状)"] + ["%.2f" % v for v in lams[1:]]
ACC_C, KS_C = "#3B6EA5", "#B45309"

# ---- (a) 隐空间风格可分性 ----
axA.plot(x, acc, "-o", color=ACC_C, lw=1.7, ms=5.2, mfc="white", mew=1.1, zorder=4)
axA.fill_between(x, 0, acc, color=ACC_C, alpha=0.13, zorder=2)
axA.axhline(1 / 22, color=BLACK, lw=0.7, ls=(0, (4, 2)), zorder=3)
axA.text(len(x) - 0.55, 1 / 22 + 0.035, "随机基线 1/22", fontsize=6.0,
         ha="right", color=BLACK)
axA.set_xticks(x)
axA.set_xticklabels(labels)
axA.set_xlabel("判别辅助损失权重 $\\lambda$")
axA.set_ylabel("隐空间风格分类准确率")
axA.set_ylim(0, 1.14)
axA.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
axA.set_yticklabels(["0", "25%", "50%", "75%", "100%"])
axA.grid(axis="y", color="#E9ECEF", lw=0.5, zorder=0)
axA.set_axisbelow(True)
for sp in ("top", "right"):
    axA.spines[sp].set_visible(False)

# ---- (b) 生成谱保真代价 ----
axB.plot(x, ks, "-s", color=KS_C, lw=1.7, ms=4.8, mfc="white", mew=1.1, zorder=4)
axB.fill_between(x, ks.min() - 0.02, ks, color=KS_C, alpha=0.12, zorder=2)
axB.set_xticks(x)
axB.set_xticklabels(labels)
axB.set_xlabel("判别辅助损失权重 $\\lambda$")
axB.set_ylabel("生成谱逐列 KS 均值（越低越保真）")
axB.set_ylim(ks.min() - 0.02, ks.max() + 0.03)
axB.grid(axis="y", color="#E9ECEF", lw=0.5, zorder=0)
axB.set_axisbelow(True)
for sp in ("top", "right"):
    axB.spines[sp].set_visible(False)

# 推荐折中档 λ=0.02 在两张图上同时标出（虚线 + 底部注记）
j = int(np.argmin(np.abs(lams - 0.02)))
for a in (axA, axB):
    a.axvline(j, color="#6B7280", lw=0.8, ls=(0, (3, 3)), zorder=1)
axA.annotate("推荐折中档\n$\\lambda$=0.02", xy=(j, acc[j]),
             xytext=(j + 0.55, 0.44), fontsize=6.2, color=BLACK,
             arrowprops=dict(arrowstyle="-", lw=0.6, color="#6B7280"))

tag_panels([axA, axB])

save_fig(fig, "figures/fig_q3_disc_tradeoff.png")
print("lams", list(lams))
print("acc", list(np.round(acc, 3)))
print("ks", list(np.round(ks, 4)))
print("recon", list(np.round(recon, 4)))
