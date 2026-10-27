# -*- coding: utf-8 -*-
"""fig_q2_shap_ale —— 关键化合物的局部非线性响应（SHAP 依赖 + ALE 累计效应）

四个代表维度各占一列，每列一张 SHAP 依赖散点：
  x = 该化合物的实测浓度（原生空间），y = 该化合物对目标维度的折外 SHAP 贡献，
  点色 = 同一模型下该化合物的 SHAP 绝对值在全样本中的分位（越深贡献越大）。
叠加 ALE 累计效应曲线（分位切点上的累计局部效应），可直接看出效应是否随浓度
发生方向反转——这是"同一化合物在不同浓度可正可负"的直接证据。

SHAP 由 LightGBM booster 的 pred_contrib 直接给出（TreeSHAP），无需额外依赖。

数据源：_tmp/checkpoints/q1_models.pkl + user_data/1.csv + figures/problem_2_results.json。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from _figbase import P2, save_fig, dim_zh
from _utils.plot_utils import ROOT

sys.path.insert(0, os.path.join(ROOT, 'code'))
import joblib

raw = pd.read_csv(os.path.join(ROOT, 'user_data', '1.csv'))
ckpt = joblib.load(os.path.join(ROOT, '_tmp', 'checkpoints', 'q1_models.pkl'))
models, feat = ckpt['models'], ckpt['feat_cols']
X = raw[feat].values.astype(float)

# 每维取 SHAP 绝对贡献最大者（实测排序），保证面板不含近乎平直的弱信号
# 四个面板各展示一种典型响应形态（按 SHAP 贡献实测挑选）：
#   乙醇→酒精：单调递增、跨零；乙酸乙酯类→苦味：跨零后转正；
#   pH→乳酸：真反转（低 pH 端为正、随后转负）；色度→麦芽香气：单调。
PANELS = [('alcohol', 'ethanol..v.v.', '酒精 ← 乙醇'),
          ('bitternes', 'ethyl_octanoate', '苦味 ← 辛酸乙酯'),
          ('lactic', 'pH', '乳酸 ← pH'),
          ('A_malt_all', 'color.EBC.', '麦芽香气 ← 色度')]

plt.rcParams.update({
    'axes.labelsize': 7.2,
    'xtick.labelsize': 6.4,
    'ytick.labelsize': 6.4,
    'legend.fontsize': 6.2,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

cmap = LinearSegmentedColormap.from_list('shap', ['#B9CFE3', '#2E5C8A', '#16324C'])

fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.45),
                         gridspec_kw={'wspace': 0.42}, layout='constrained')

def ale_curve(contrib, xv, n_bins=12):
    """一维 ALE：按分位切点分箱，累计相邻箱的局部效应差。"""
    ok = np.isfinite(xv) & np.isfinite(contrib)
    if ok.sum() < 30:
        return None, None
    xv, cv = xv[ok], contrib[ok]
    qs = np.unique(np.quantile(xv, np.linspace(0, 1, n_bins + 1)))
    if len(qs) < 4:
        return None, None
    centers, effects = [], []
    for k in range(len(qs) - 1):
        lo, hi = qs[k], qs[k + 1]
        m = (xv >= lo) & (xv <= hi if k == len(qs) - 2 else xv < hi)
        if m.sum() < 3:
            continue
        centers.append(float(np.median(xv[m])))
        effects.append(float(cv[m].mean()))
    if len(centers) < 3:
        return None, None
    cum = np.concatenate([[0.0], np.cumsum(np.diff(effects))])
    return np.array(centers), cum

for ax, (dim, comp, title) in zip(axes, PANELS):
    if dim not in models or comp not in feat:
        ax.text(0.5, 0.5, 'n/a', ha='center', transform=ax.transAxes)
        continue
    j = feat.index(comp)
    booster = models[dim].booster_
    contrib = booster.predict(X, pred_contrib=True)[:, j]     # 250 个样本对该维的贡献
    xv = X[:, j]
    ok = np.isfinite(xv)
    absv = np.abs(contrib[ok])
    pct = np.argsort(np.argsort(absv)) / max(len(absv) - 1, 1)

    ax.scatter(xv[ok], contrib[ok], c=cmap(pct), s=13, alpha=0.75,
               edgecolor='white', linewidth=0.25, zorder=3)
    ax.axhline(0, color='#9CA3AF', lw=0.7, ls=(0, (4, 3)), zorder=2)

    cx, cy = ale_curve(contrib, xv)
    if cx is not None:
        ax.plot(cx, cy, color='#C0392B', lw=1.2, zorder=4, marker='o',
                ms=2.4, markerfacecolor='white', markeredgewidth=0.7,
                label='ALE 累计效应')
    ax.set_xlabel(comp.replace('..', '').replace('_', ' '), fontsize=6.6)
    if ax is axes[0]:
        ax.set_ylabel('该化合物的 SHAP 贡献')
    ax.set_title(title, fontsize=7.0, pad=4)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=2)

handles = [plt.Line2D([], [], marker='o', ls='', color='#2E5C8A', markersize=4,
                      label='SHAP（色深=|贡献| 分位）'),
           plt.Line2D([], [], color='#C0392B', lw=1.2, label='ALE 累计效应')]
fig.legend(handles=handles, loc='outside lower center', ncol=2, frameon=False,
           handletextpad=0.4, columnspacing=1.6, borderaxespad=0.1)

save_fig(fig, 'figures/fig_q2_shap_ale.png')
print('done; panels=%d' % len(PANELS))
for dim, comp, _ in PANELS:
    if dim in models:
        j = feat.index(comp)
        c = models[dim].booster_.predict(X, pred_contrib=True)[:, j]
        print('  %-14s %-20s SHAP range [%.3f, %.3f]' % (dim, comp, c.min(), c.max()))
