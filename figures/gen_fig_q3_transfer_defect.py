# -*- coding: utf-8 -*-
"""fig_q3_transfer_defect — 跨风格迁移缺陷控制（哑铃图，含无约束对照）
Pils/Lager→Tripel 迁移 11 款，4 个缺陷化合物：
 橙点=迁移前；蓝点=严格投影 min(源值, m_t) 后；红×=无约束纯平移对照；绿菱形=目标安全值 m_t。
绿色水平线=严格投影（下降/持平），红色虚线=无约束对照的升高。
严格投影后 0/44 升高；无约束纯平移 32/44 升高，DMS/4VG/壬烯醛突破 m_t。
数据源：problem_3_results.json::fig_data.defect_dumbbell, transfer_info.unconstrained_control。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import P3, PALETTE, save_fig, set_paper_placement, declutter_axes

GREEN, RED, GRAY = '#2E8B57', '#C0392B', '#8A93A0'
dd = P3['fig_data']['defect_dumbbell']
tinfo = P3['transfer_info']; ctrl = tinfo.get('unconstrained_control', {})
zh = {'DMS': 'DMS（煮玉米）', 'X2.3.butanedione': '双乙酰（奶香）',
      'X4VG': '4-VG（丁香）', 'X.E..2.nonenal': '反-2-壬烯醛（纸板）'}
names = list(dd.keys())
before = np.array([dd[k]['before_mean'] for k in names])
after = np.array([dd[k]['after_mean'] for k in names])
raw = np.array([dd[k]['raw_after_mean'] for k in names])
mt = np.array([dd[k]['m_t'] for k in names])

fig, ax = plt.subplots(figsize=(9.8, 4.0))
set_paper_placement(fig)
y = np.arange(len(names))[::-1]
for i, yi in zip(range(len(names)), y):
    k = names[i]
    # 严格投影 before→after（下降绿、持平灰）
    line_col = GRAY if abs(after[i] - before[i]) < 1e-6 else GREEN
    ax.hlines(yi, min(before[i], after[i]), max(before[i], after[i]),
              color=line_col, lw=2.4, zorder=2)
    # 无约束升高红虚线
    if raw[i] > before[i] + 1e-6:
        ax.hlines(yi, before[i], raw[i], color=RED, lw=1.3,
                  linestyle=(0, (4, 3)), alpha=0.8, zorder=1)
    ax.scatter(before[i], yi, s=78, color=PALETTE[1], edgecolors='white',
               linewidths=0.8, zorder=4)
    ax.scatter(after[i], yi, s=78, color=PALETTE[0], edgecolors='white',
               linewidths=0.8, zorder=4)
    ax.scatter(raw[i], yi, s=86, marker='x', color=RED, lw=2.0, zorder=5)
    ax.scatter(mt[i], yi, s=105, marker='D', facecolors='none', edgecolors=GREEN,
               linewidths=1.7, zorder=4)
    breach = raw[i] > mt[i]
    nr = k and dd[k]['n_rise_unconstrained']
    txt = f'严格Δ={dd[k]["delta_mean"]:+.2f}　无约束Δ={dd[k]["delta_raw_mean"]:+.2f}（{nr}/11 升）'
    if breach:
        txt += '　★ 无约束超 m_t'
    ax.text(1.9, yi, txt, ha='left', va='center', fontsize=8.2,
            color=RED if breach else '#333',
            fontweight='bold' if breach else 'normal')

ax.set_yticks(y)
ax.set_yticklabels([zh.get(k, k) for k in names], fontsize=9)
ax.set_xlabel('标准化含量（迁移 11 款的均值）')
n_unc = ctrl.get('n_defect_rise_unconstrained', 0); n_tot = ctrl.get('n_total', 44)
n_c = ctrl.get('n_defect_rise_constrained', 0)
ax.set_title(f'严格投影 min(源值, m_t) 后缺陷升高 {n_c}/{n_tot}；'
             f'无约束纯平移 {n_unc}/{n_tot} 升高（{n_unc/n_tot:.0%}）',
             fontsize=11, fontweight='bold', loc='left', pad=4)
ax.set_xlim(-2.55, 5.7)
declutter_axes(ax, grid_axis='x')
handles = [
    Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE[1], markersize=9, label='迁移前'),
    Line2D([0], [0], marker='o', color='w', markerfacecolor=PALETTE[0], markersize=9, label='严格投影后'),
    Line2D([0], [0], marker='x', color=RED, markersize=9, lw=2, label='无约束纯平移（对照）'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor='none', markeredgecolor=GREEN,
           markersize=9, label='目标安全值 m_t'),
]
ax.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.13),
          fontsize=9, framealpha=0.95, ncol=4)
fig.tight_layout()
save_fig(fig, 'figures/fig_q3_transfer_defect.png')
print('fig_q3_transfer_defect done; unc=%d/%d' % (n_unc, n_tot))
