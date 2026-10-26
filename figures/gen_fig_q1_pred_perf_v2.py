# -*- coding: utf-8 -*-
"""fig_q1_pred_perf — 50 维交叉验证 QWK 排序（ModelViz 模板版式重做）

沿用模板 02_CMP「单因子排序条形」的分组版式：两列水平条、按值降序、
条尾标数值；配色统一为单色系，与论文其余图一致。
数据源：problem_1_results.json::fig_data.qwk_ranked。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt

from _figbase import P1, save_fig, set_paper_placement, declutter_axes, dim_zh

ranked = P1["fig_data"]["qwk_ranked"]
mean_qwk = P1["summary"]["mean_qwk_main"]
names = [r[0] for r in ranked]
vals = [r[1] for r in ranked]
n = len(names)
half = (n + 1) // 2

BAR = "#2E5C8A"
REF = "#444444"

fig, axes = plt.subplots(1, 2, figsize=(7.0, 5.5))
set_paper_placement(fig, width_fraction=0.98)

for col, ax in enumerate(axes):
    idx = list(range(col * half, min((col + 1) * half, n)))
    yy = np.arange(len(idx))[::-1]
    ax.axvline(mean_qwk, color=REF, ls="--", lw=0.9, alpha=0.7, zorder=1)
    ax.barh(yy, [vals[i] for i in idx], height=0.66, color=BAR,
            edgecolor="white", linewidth=0.4, zorder=2)
    ax.set_yticks(yy)
    ax.set_yticklabels([dim_zh(names[i]) for i in idx], fontsize=6.9)
    ax.set_xlabel("交叉验证 QWK", fontsize=8.2)
    ax.set_xlim(0, max(vals) * 1.14)
    ax.tick_params(axis="x", labelsize=7.2)
    declutter_axes(ax, grid_axis="x")

axes[0].text(mean_qwk + 0.012, half - 0.6, "全维均值 %.3f" % mean_qwk,
             fontsize=7.2, color=REF, va="top", ha="left")
fig.tight_layout()
save_fig(fig, "figures/fig_q1_pred_perf.png")
print("fig_q1_pred_perf done; n=%d mean=%.4f" % (n, mean_qwk))
