# -*- coding: utf-8 -*-
"""fig_q1_calibration — 问题一校准（2 panel，代表维 F_hops_all）
(a) 连续预测值 vs 真实标准化值散点 + 对角线（校准度）
(b) 预测等级 vs 真实等级混淆热力（0-6 级分箱映射后的整数等级）
数据源：problem_1_results.json::calibration（true_cont/pred_cont/true_level/pred_level ×250）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P1, PALETTE, COLORS, save_fig, set_paper_placement, declutter_axes, panel
from _utils.plot_utils import draw_vector_heatmap

cal = P1['calibration']
dim = cal['dim']
tc = np.array(cal['true_cont']); pc = np.array(cal['pred_cont'])
tl = np.array(cal['true_level']); pl = np.array(cal['pred_level'])

fig, axes = plt.subplots(1, 2, figsize=(6.6, 3.5), gridspec_kw={'width_ratios': [1, 1.08]})
set_paper_placement(fig)

# ── (a) 连续校准散点 ───────────────────────
ax = axes[0]
lo = min(tc.min(), pc.min()); hi = max(tc.max(), pc.max())
pad = (hi - lo) * 0.06
ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], ls='--', lw=1.1,
        color=COLORS['ref_line'], zorder=1, label='理想校准 y=x')
ax.scatter(tc, pc, s=18, color=PALETTE[0], alpha=0.55, edgecolors='white',
           linewidths=0.3, zorder=2)
r = np.corrcoef(tc, pc)[0, 1]
ax.set_xlabel('真实标准化值（代表维）')
ax.set_ylabel('模型预测值')
ax.set_xlim(lo - pad, hi + pad); ax.set_ylim(lo - pad, hi + pad)
ax.legend(loc='upper left', fontsize=7, framealpha=0.9)
ax.text(0.97, 0.05, f'Pearson r={r:.2f}', transform=ax.transAxes, ha='right',
        va='bottom', fontsize=8, color=COLORS['text'])
declutter_axes(ax)

# ── (b) 等级混淆热力 0-6 ───────────────────
ax = axes[1]
L = 7
cm = np.zeros((L, L))
for t, p in zip(tl, pl):
    cm[int(t), int(p)] += 1
draw_vector_heatmap(ax, cm, xlabels=list(range(L)), ylabels=list(range(L)),
                    annot='auto', fmt='.0f', cmap='YlOrRd', cbar=True,
                    cbar_label='样本数', origin='lower')
ax.set_xlabel('预测等级')
ax.set_ylabel('真实等级')

fig.tight_layout()
save_fig(fig, 'figures/fig_q1_calibration.png')
print('fig_q1_calibration done; dim=%s r=%.3f' % (dim, r))
