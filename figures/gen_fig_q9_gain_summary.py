# -*- coding: utf-8 -*-
"""fig_gain_summary — 方法增益汇总（第 9 章新增，ModelViz 模板版式）

四个环节的消融/对照增益并列：
  问题一 缺失处理：KNN 插补 → 原生缺失
  问题一 分级方式：回归+分位 → 分箱退化维改用有序回归
  问题二 证据融合：仅相关 → 三路融合（模块覆盖数）
  问题三 值域约束：截断前 → 截断后（观测区间内比例）
各环节量纲不同，统一换算为「相对改进百分比」，只表达方向与幅度，不跨环节比较绝对值。
数据源：problem_1_results.json、_tmp/ordinal_full.csv、_tmp/q2_ablation.json、_tmp/gen_eval_compare.csv。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from _figbase import save_fig, set_paper_placement, declutter_axes

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    p1 = json.load(open(os.path.join(ROOT, "figures", "problem_1_results.json"), encoding="utf-8"))
    base_qwk = p1["summary"]["by_model"]["lightgbm"]["mean_qwk"]
    knn_qwk = p1["summary"]["by_model"]["knn_impute"]["mean_qwk"]

    ordi = pd.read_csv(os.path.join(ROOT, "_tmp", "ordinal_full.csv"))
    ord_base, ord_best = ordi.qwk_base.mean(), ordi.qwk_best.mean()

    abl = json.load(open(os.path.join(ROOT, "_tmp", "q2_ablation.json"), encoding="utf-8"))
    cov = {v["variant"]: v["mean_module_coverage"] for v in abl["variants"]}

    gen = pd.read_csv(os.path.join(ROOT, "_tmp", "gen_eval_compare.csv"))
    g = gen.groupby("method")["in_range"].mean()

    items = [
        ("缺失处理\nKNN 插补 → 原生缺失", (base_qwk - knn_qwk) / knn_qwk * 100),
        ("分级方式\n统一分箱 → 分维选型", (ord_best - ord_base) / ord_base * 100),
        ("证据融合\n仅相关 → 三路融合", (cov["full (3-way)"] - cov["corr only"]) / cov["corr only"] * 100),
        ("值域约束\n截断前 → 截断后", (g["CVAE-clipped"] - g["CVAE-raw"]) / g["CVAE-raw"] * 100),
    ]
    labels = [x[0] for x in items]
    vals = [x[1] for x in items]

    fig, ax = plt.subplots(figsize=(7.0, 3.4))
    set_paper_placement(fig, width_fraction=0.96)
    x = np.arange(len(vals))
    colors = ["#A9C3DD", "#2E5C8A", "#2E5C8A", "#7BA7CF"]
    bars = ax.bar(x, vals, width=0.58, color=colors, edgecolor="white", linewidth=0.6, zorder=2)

    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + max(vals) * 0.03, "+%.1f%%" % v,
                ha="center", va="bottom", fontsize=8.2, color="#222")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=7.4)
    ax.set_ylabel("相对改进（%）", fontsize=8.4)
    ax.set_ylim(0, max(vals) * 1.22)
    ax.tick_params(axis="y", labelsize=7.4)
    declutter_axes(ax, grid_axis="y")
    fig.tight_layout()
    save_fig(fig, "figures/fig_q9_gain_summary.png")
    print("gain summary:", [(l.replace("\n", " "), round(v, 2)) for l, v in items])


if __name__ == "__main__":
    main()
