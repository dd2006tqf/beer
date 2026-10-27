# -*- coding: utf-8 -*-
"""fig_q3_transfer_defect —— 跨风格迁移的缺陷控制（三臂斜率图）

每个缺陷化合物占一列，列内自上而下为三种状态：
  迁移前 → 严格投影后 → 无约束纯平移，
三点连成一条轨迹。蓝色段表示下降或持平，红色段表示升高；
顶端灰线为目标安全值 m_t 的位置。右侧一行给出两组的升高计数。

用斜率图而非横向哑铃，是因为四个缺陷的数值量级差异很大（DMS 1.16 vs
4-VG −2.01），横向同轴会挤在一起；按列归一后每条轨迹的走向清晰可见。

版式参考 ModelViz 09_REL_020（效应分解）与 02_CMP_003（相关堆叠）。
数据源：figures/problem_3_results.json::fig_data.defect_dumbbell。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from _figbase import P3, save_fig, declutter_axes

dd = P3['fig_data']['defect_dumbbell']
ctrl = P3['transfer_info'].get('unconstrained_control', {})

zh = {'DMS': 'DMS', 'X2.3.butanedione': '双乙酰', 'X4VG': '4-VG',
      'X.E..2.nonenal': '反-2-壬烯醛'}
sub = {'DMS': '煮玉米', 'X2.3.butanedione': '奶香', 'X4VG': '丁香',
       'X.E..2.nonenal': '纸板'}
names = list(dd.keys())

plt.rcParams.update({
    'axes.labelsize': 7.4,
    'xtick.labelsize': 7.0,
    'ytick.labelsize': 6.6,
    'legend.fontsize': 6.7,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'axes.unicode_minus': False,
})

BLUE, RED, GREEN, GRAY = '#2E5C8A', '#C0392B', '#2E8B57', '#9CA3AF'

fig, axes = plt.subplots(1, 4, figsize=(5.9, 2.75), sharey=False,
                         gridspec_kw={'wspace': 0.56}, layout='constrained')

STEP_Y = [3, 2, 1]          # 迁移前 / 严格投影后 / 无约束
STEP_LAB = ['迁移前', '严格后', '无约束']

for ax, k in zip(axes, names):
    v = dd[k]
    b, a, r, t = v['before_mean'], v['after_mean'], v['raw_after_mean'], v['m_t']
    vals = [b, a, r]
    # 目标安全值：横贯全列
    ax.axhline(t, color=GREEN, lw=1.0, ls=(0, (3, 3)), zorder=1)
    # 段 1：迁移前 → 严格投影后
    ax.plot([0, 0], [STEP_Y[0], STEP_Y[1]],
            color=BLUE if a <= b + 1e-6 else RED, lw=2.0, zorder=3,
            solid_capstyle='round')
    # 段 2：严格投影后 → 无约束
    ax.plot([0, 0], [STEP_Y[1], STEP_Y[2]],
            color=RED if r > a + 1e-6 else BLUE, lw=2.0, zorder=3,
            solid_capstyle='round', ls=(0, (3, 2)) if r > a else '-')
    for yv, val, col in zip(STEP_Y, vals, [GRAY, BLUE, RED]):
        ax.plot(0, yv, 'o', ms=5.5, color=col, markeredgecolor='white',
                markeredgewidth=0.6, zorder=5)
        ax.text(0.16, yv, '%.2f' % val, fontsize=6.2, va='center', ha='left',
                color='#374151')
    ax.set_xlim(-0.30, 0.92)
    ax.set_ylim(0.42, 3.72)
    ax.set_xticks([])
    ax.set_yticks(STEP_Y)
    ax.set_yticklabels(STEP_LAB, fontsize=6.4)
    ax.tick_params(axis='y', length=0, pad=2)
    for s in ('top', 'right', 'bottom', 'left'):
        ax.spines[s].set_visible(False)
    ax.grid(axis='y', color='#EDEFF2', lw=0.6, zorder=0)
    ax.set_axisbelow(True)
    title = zh.get(k, k)
    ax.set_title(title + '\n' + sub.get(k, ''), fontsize=7.4, pad=4,
                 linespacing=1.3)
    nr = v['n_rise_unconstrained']
    ax.text(0.0, 0.40, '升高 %d/11' % nr, transform=ax.transAxes,
            ha='center', va='top', fontsize=6.2, color=RED)
    ax.text(0.0, -0.07, '严格 0/11', transform=ax.transAxes,
            ha='center', va='top', fontsize=6.2, color=BLUE)

fig.legend(handles=[
    Line2D([], [], marker='o', ls='', color=GRAY, markersize=5, label='迁移前'),
    Line2D([], [], marker='o', ls='', color=BLUE, markersize=5, label='严格投影后'),
    Line2D([], [], marker='o', ls='', color=RED, markersize=5, label='无约束纯平移'),
    Line2D([], [], color=GREEN, lw=1.0, ls=(0, (3, 3)), label='目标安全值 $'),
], loc='outside lower center', ncol=4, frameon=False, handletextpad=0.4,
   columnspacing=1.3, borderaxespad=0.1)

save_fig(fig, 'figures/fig_q3_transfer_defect.png')
print('done; unc=%d/%d' % (ctrl.get('n_defect_rise_unconstrained', 0),
                           ctrl.get('n_total', 44)))
