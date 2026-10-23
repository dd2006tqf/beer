# -*- coding: utf-8 -*-
"""fig_q3_transfer_defect — 问题三跨风格迁移缺陷控制（single，哑铃图）
Pils/Lager→Tripel 隐空间迁移：4 个缺陷化合物迁移前(before)→迁移后(after)标准化均值，
菱形标记为该缺陷的安全阈值 m_t；迁移后全部落在阈值安全侧（合规率 100%）。
数据源：problem_3_results.json::fig_data.defect_dumbbell（before_mean/after_mean/m_t ×4）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P3, PALETTE, COLORS, save_fig, set_paper_placement, declutter_axes

dd = P3['fig_data']['defect_dumbbell']
tinfo = P3['transfer_info']
names = list(dd.keys())
before = np.array([dd[k]['before_mean'] for k in names])
after = np.array([dd[k]['after_mean'] for k in names])
mt = np.array([dd[k]['m_t'] for k in names])
cr = tinfo['compliance_rate'] * 100

fig, ax = plt.subplots(figsize=(6.4, 3.4))
set_paper_placement(fig)
y = np.arange(len(names))[::-1]

for i, yi in zip(range(len(names)), y):
    ax.hlines(yi, min(before[i], after[i]), max(before[i], after[i]),
              color=PALETTE[2], lw=2.0, zorder=2)
    ax.annotate('', xy=(after[i], yi), xytext=(before[i], yi),
                arrowprops=dict(arrowstyle='-|>', color=PALETTE[2], lw=0.1), zorder=2)

ax.scatter(before, y, s=70, color=PALETTE[3], edgecolors='white', linewidths=0.8,
           zorder=3, label='迁移前')
ax.scatter(after, y, s=70, color=PALETTE[0], edgecolors='white', linewidths=0.8,
           zorder=3, label='迁移后')
ax.scatter(mt, y, s=95, marker='D', facecolors='none', edgecolors=COLORS['down'],
           linewidths=1.4, zorder=4, label='安全阈值 $m_t$')

lo_all = float(min(before.min(), after.min(), mt.min()))
hi_all = float(max(before.max(), after.max(), mt.max()))
span = hi_all - lo_all
xcol = hi_all + span * 0.14
for i, yi in zip(range(len(names)), y):
    dv = after[i] - before[i]
    ax.text(xcol, yi, f'Δ={dv:+.2f}', ha='left', va='center',
            fontsize=7, color=PALETTE[0])
ax.set_xlim(lo_all - span * 0.08, xcol + span * 0.22)

ax.set_yticks(y)
ax.set_yticklabels(names, fontsize=8)
ax.set_xlabel('标准化含量（迁移前后均值）')
declutter_axes(ax, grid_axis='x')
ax.legend(loc='lower left', fontsize=7.4, framealpha=0.9, ncol=2,
          title=f'缺陷合规率 {cr:.0f}%', title_fontsize=7.5)

fig.tight_layout()
save_fig(fig, 'figures/fig_q3_transfer_defect.png')
print('fig_q3_transfer_defect done; defects=%d cr=%.0f' % (len(names), cr))
