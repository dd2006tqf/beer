# -*- coding: utf-8 -*-
"""fig_q9_gain_summary — 四个环节的方法增益汇总（ModelViz 模板版式重做）

版式取自模板 02_CMP_005「渐变单因子条形图」：水平条、按数值降序、
条尾标注数值。在此基础上做三处适配，解决原图的实际问题：
  1) 标签分两行（环节名 / 做法变化），避免长标签挤成一行；
  2) 横轴取对数，使 +0.3% 与 +27% 同时可读（原图线性轴下 0.3% 几乎不可见）；
  3) 按性质分组配色：实质改进（深蓝）与正确性修正（浅蓝）区分，
     并在条尾标注归属，帮助读者判断“涨分”与“纠错”两类贡献。
数据源：problem_1_results.json、_tmp/ordinal_full.csv、_tmp/q2_ablation.json、
        _tmp/gen_eval_compare.csv。
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


def collect():
    p1 = json.load(open(os.path.join(ROOT, "figures", "problem_1_results.json"), encoding="utf-8"))
    base_qwk = p1["summary"]["by_model"]["lightgbm"]["mean_qwk"]
    knn_qwk = p1["summary"]["by_model"]["knn_impute"]["mean_qwk"]

    ordi = pd.read_csv(os.path.join(ROOT, "_tmp", "ordinal_full.csv"))
    ord_base, ord_best = ordi.qwk_base.mean(), ordi.qwk_best.mean()

    abl = json.load(open(os.path.join(ROOT, "_tmp", "q2_ablation.json"), encoding="utf-8"))
    cov = {v["variant"]: v["mean_module_coverage"] for v in abl["variants"]}

    gen = pd.read_csv(os.path.join(ROOT, "_tmp", "gen_eval_compare.csv"))
    g = gen.groupby("method")["in_range"].mean()

    return [
        dict(env="问题二  证据融合", change="仅交叉相关 → 三路融合",
             metric="模块覆盖数 2.30 → 2.92",
             gain=(cov["full (3-way)"] - cov["corr only"]) / cov["corr only"] * 100,
             kind="实质改进"),
        dict(env="问题一  分级方式", change="统一分箱 → 分维选型",
             metric="折外 QWK 0.3663 → 0.3953",
             gain=(ord_best - ord_base) / ord_base * 100, kind="实质改进"),
        dict(env="问题三  值域约束", change="解码后不截断 → 按区间截断",
             metric="区间内 89.1% → 90.5%",
             gain=(g["CVAE-clipped"] - g["CVAE-raw"]) / g["CVAE-raw"] * 100,
             kind="正确性修正"),
        dict(env="问题一  缺失处理", change="KNN 插补 → 原生缺失",
             metric="折外 QWK 0.3652 → 0.3663",
             gain=(base_qwk - knn_qwk) / knn_qwk * 100, kind="正确性修正"),
    ]


def main():
    rows = sorted(collect(), key=lambda r: r["gain"])
    gains = [r["gain"] for r in rows]
    labels = ["%s\n%s" % (r["env"], r["change"]) for r in rows]
    colors = ["#2E5C8A" if r["kind"] == "实质改进" else "#A9C3DD" for r in rows]

    # 图宽与论文中的占宽对齐（0.82\textwidth≈13cm），保证打印后字号不缩水
    fig, ax = plt.subplots(figsize=(5.15, 3.05))
    set_paper_placement(fig, width_fraction=0.97)
    yy = np.arange(len(rows))

    bars = ax.barh(yy, gains, height=0.58, color=colors,
                   edgecolor="white", linewidth=0.6, zorder=2)

    ax.set_xscale("log")
    top = max(gains)
    ax.set_xlim(0.15, top * 3.2)
    ax.set_xticks([0.3, 1, 3, 10, 30])
    ax.set_xticklabels(["0.3%", "1%", "3%", "10%", "30%"], fontsize=7.6)

    for bar, r in zip(bars, rows):
        ax.text(r["gain"] * 1.12, bar.get_y() + bar.get_height() / 2,
                "+%.1f%%" % r["gain"], va="center", ha="left",
                fontsize=8.4, color="#222222", fontweight="bold")
        ax.text(top * 2.05, bar.get_y() + bar.get_height() / 2, r["metric"],
                va="center", ha="left", fontsize=7.0, color="#555555")

    ax.set_yticks(yy)
    ax.set_yticklabels(labels, fontsize=7.6)
    ax.set_xlabel("相对改进幅度（对数轴）", fontsize=8.4)
    ax.set_ylim(-0.6, len(rows) - 0.4)
    declutter_axes(ax, grid_axis="x")

    # 分组图例：实质改进 / 正确性修正
    from matplotlib.patches import Patch
    handles = [Patch(facecolor="#2E5C8A", label="实质改进（提升主要指标）"),
               Patch(facecolor="#A9C3DD", label="正确性修正（消除偏差与外推）")]
    ax.legend(handles=handles, loc="lower right", fontsize=7.2, frameon=False)

    fig.tight_layout()
    save_fig(fig, "figures/fig_q9_gain_summary.png")
    for r in rows:
        print("%-22s %-28s %+6.1f%%  %s" % (r["env"], r["change"], r["gain"], r["kind"]))


if __name__ == "__main__":
    main()
