# -*- coding: utf-8 -*-
"""fig_q1_model_bar — 多模型折外平均 QWK 对比（ModelViz 模板版式重做）

沿用模板 02_CMP_005「渐变单因子条形图」的版式语言：水平条 + 条尾数值标注 +
按数值排序；但把模板的彩虹渐变改为论文统一的单色系，以符合朴素配色要求。
数据源：problem_1_results.json::summary.by_model。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import matplotlib.pyplot as plt
import numpy as np

from _figbase import P1, save_fig, set_paper_placement, declutter_axes

bm = P1["summary"]["by_model"]
ORDER = [
    ("lightgbm", "LightGBM（本文主模型）"),
    ("knn_impute", "KNN 插补 + LightGBM"),
    ("rf", "随机森林"),
    ("elasticnet", "弹性网"),
    ("mean_baseline", "逐维均值基线"),
]
names = [n for _, n in ORDER]
vals = [bm[k]["mean_qwk"] for k, _ in ORDER]

rest = sorted(range(1, len(vals)), key=lambda i: -vals[i])
idx = [0] + rest
names = [names[i] for i in idx]
vals = [vals[i] for i in idx]

colors = ["#2E5C8A"] + ["#A9C3DD"] * (len(vals) - 1)

fig, ax = plt.subplots(figsize=(6.9, 3.9))
set_paper_placement(fig, width_fraction=0.95)
yy = np.arange(len(vals))[::-1]
bars = ax.barh(yy, vals, color=colors, edgecolor="white", linewidth=0.8,
               height=0.62, zorder=2)

for bar, v in zip(bars, vals):
    ax.text(v + 0.006, bar.get_y() + bar.get_height() / 2, "%.4f" % v,
            va="center", ha="left", fontsize=7.8, color="#222222")

ax.set_yticks(yy)
ax.set_yticklabels(names, fontsize=8.0)
ax.set_xlabel("50 维平均 QWK（分层 5 折折外）", fontsize=8.6)
ax.set_xlim(0, max(vals) * 1.22)
ax.tick_params(axis="x", labelsize=7.6)
declutter_axes(ax, grid_axis="x")
fig.tight_layout()
save_fig(fig, "figures/fig_q1_model_bar.png")
print("fig_q1_model_bar done; best=%.4f" % max(vals))
