# -*- coding: utf-8 -*-
"""fig_prep_logbase —— 对数底与检出结构核实（两张整图，每图两子图）

fig_prep_logbase_a.png  左：22 种风格样本量；右：三类特征的检出/未检出/缺失构成
fig_prep_logbase_b.png  左：1.csv 取值对校准浓度；右：70 个可校准列的中位残差

版式约定：
- 子图不写标题、不加角标，含义全部由论文正文说明；
- 图宽按最终排版宽度（0.94 版心 ≈ 5.9 in）1:1 设定，使图内字号即纸面字号。

参考模板（ModelViz）：02_CMP_006 横轴百分比堆叠图、09_REL_017 回归散点图。
数据源：supp_preprocess.json（由 8.xlsx Calibrated chemical dataset 逐样本实算）。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, NullFormatter
from matplotlib.lines import Line2D
from _figbase import load, PALETTE, save_fig, declutter_axes

PP = load('supp_preprocess.json')
LB = PP['log_base_audit']
D = chr(36)

plt.rcParams.update({
    'axes.labelsize': 8.2,
    'xtick.labelsize': 7.2,
    'ytick.labelsize': 7.2,
    'legend.fontsize': 6.9,
    'axes.edgecolor': '#6B7280',
    'axes.labelcolor': '#1F2933',
    'xtick.color': '#4B5563',
    'ytick.color': '#4B5563',
    'axes.unicode_minus': False,
    'mathtext.fontset': 'dejavusans',
    'hatch.linewidth': 0.45,
})

BLUE, ORANGE, RED, GREEN = PALETTE[0], PALETTE[1], PALETTE[2], PALETTE[3]
GRID = '#9CA3AF'


def frame(ax, axis='x'):
    declutter_axes(ax, grid_axis=axis)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color('#9CA3AF')
    ax.tick_params(axis='y', length=0)


# ═══════════════════════════════════════════════════════════════
# 图 A：风格样本量 | 检出构成     （5.9 in 宽 ≈ 0.94 版心）
# ═══════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(5.9, 3.85),
                               gridspec_kw={'width_ratios': [1.12, 1.0],
                                            'wspace': 0.30},
                               layout='constrained')

sc = sorted(PP['style_counts'], key=lambda z: z[1])
names = [s[0] for s in sc]
vals = [s[1] for s in sc]
y = np.arange(len(names))
colors = [BLUE if v >= 10 else ORANGE for v in vals]
ax1.barh(y, vals, color=colors, height=0.66, edgecolor='white',
         linewidth=0.4, zorder=3)
ax1.set_yticks(y)
ax1.set_yticklabels(names, fontsize=6.6)
ax1.set_xlim(0, max(vals) * 1.16)
ax1.set_ylim(-0.70, len(names) - 0.30)
ax1.set_xlabel('样本款数')
for i, v in enumerate(vals):
    ax1.text(v + max(vals) * 0.022, i, str(v), va='center', ha='left',
             fontsize=6.4, color='#4B5563')
ax1.axvline(10, color=GRID, lw=0.9, ls=(0, (4, 2)), zorder=2)
frame(ax1, 'x')
ax1.legend(handles=[
    Line2D([], [], color=GRID, lw=0.9, ls=(0, (4, 2)), label='10 款'),
    Line2D([], [], marker='s', ls='', color=ORANGE, markersize=5,
           label='不足 10 款'),
], loc='lower right', frameon=False, handletextpad=0.5,
    borderaxespad=0.25, labelspacing=0.25)

gs = PP['missing_vs_belowlod']['group_stats']
grp = ['physicochemical', 'aggregate', 'compound_C']
lab = ['理化/过程\n参数 16 列', '多化合物\n汇总 4 列', '单一化合物集 C\n211 列']
det = np.array([gs[g]['detected'] for g in grp]) * 100
bl = np.array([gs[g]['below_lod'] for g in grp]) * 100
ms = np.array([gs[g]['missing'] for g in grp]) * 100
yb = np.arange(len(grp))[::-1]
ax2.barh(yb, det, height=0.48, color=BLUE, edgecolor='white',
         linewidth=0.6, label='检出', zorder=3)
ax2.barh(yb, bl, left=det, height=0.48, color=ORANGE, edgecolor='white',
         linewidth=0.6, label='未检出（≤列下限）', zorder=3)
ax2.barh(yb, ms, left=det + bl, height=0.48, color=RED, edgecolor='white',
         linewidth=0.6, hatch='////', label='真实缺失', zorder=3)
ax2.set_yticks(yb)
ax2.set_yticklabels(lab, fontsize=7.0, linespacing=1.35)
ax2.set_xlim(0, 100)
ax2.set_xticks([0, 25, 50, 75, 100])
ax2.set_xticklabels(['0', '25', '50', '75', '100%'])
ax2.set_xlabel('占该组单元格比例')
ax2.set_ylim(-0.55, len(grp) - 0.45)
for i in range(len(grp)):
    yy = yb[i]
    if det[i] >= 12:
        ax2.text(det[i] / 2, yy, '%.1f%%' % det[i], ha='center', va='center',
                 fontsize=7.0, color='white')
    if bl[i] >= 8:
        ax2.text(det[i] + bl[i] / 2, yy, '%.1f%%' % bl[i], ha='center',
                 va='center', fontsize=6.7, color='white')
ax2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.155), ncol=3,
           frameon=False, handlelength=1.2, columnspacing=1.1,
           handletextpad=0.45)
frame(ax2, 'x')

save_fig(fig, 'figures/fig_prep_logbase_a.png')


# ═══════════════════════════════════════════════════════════════
# 图 B：校准散点 | 70 列中位残差
# ═══════════════════════════════════════════════════════════════
fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(5.9, 3.05),
                               gridspec_kw={'width_ratios': [1.0, 1.0],
                                            'wspace': 0.30},
                               layout='constrained')

scat = LB['scatter']
demo = [('DMS', BLUE, 'o'), ('acetaldehyde', ORANGE, 's'),
        ('ethyl_acetate', GREEN, '^'), ('pH', RED, 'D')]
lo, hi = -1.2, 3.2
ax3.plot([lo, hi], [lo, hi], color='#6B7280', lw=0.8, ls=(0, (5, 3)), zorder=2)
for name, col, mk in demo:
    if name not in scat:
        continue
    xv = np.asarray(scat[name]['log10_c'], float)
    yv = np.asarray(scat[name]['x_in_1csv'], float)
    ax3.scatter(xv, yv, s=11, color=col, alpha=0.55, marker=mk,
                edgecolor='white', linewidth=0.25, label=name, zorder=3)
ax3.set_xlim(lo, hi)
ax3.set_ylim(lo, hi)
ax3.set_xlabel('校准绝对浓度 ' + D + r'\log_{10}(c)' + D + '  [mg/L]')
ax3.set_ylabel('1.csv 取值 ' + D + 'x' + D)
ax3.text(hi - 0.10, hi - 0.22, D + 'y=x' + D, ha='right', va='top',
         fontsize=7.6, color='#4B5563', rotation=41)
ax3.legend(loc='upper left', frameon=False, ncol=2, handletextpad=0.25,
           columnspacing=0.7, borderaxespad=0.12)
ax3.set_aspect('equal', adjustable='box')
frame(ax3, 'both')

pc = LB['per_col']
lx, ly, rx, ry = [], [], [], []
for v in pc.values():
    a, b = v['median_abs_res_log10'], v['median_abs_res_raw']
    if v['verdict'].startswith('log10'):
        lx.append(a); ly.append(b)
    else:
        rx.append(a); ry.append(b)
eps = 2e-3
ax4.scatter(np.array(rx) + eps, np.array(ry) + eps, s=26, color=ORANGE,
            alpha=0.72, edgecolor='white', linewidth=0.4, marker='s',
            label='原值列 ' + D + 'n=%d' % len(rx) + D, zorder=3)
ax4.scatter(np.array(lx) + eps, np.array(ly) + eps, s=26, color=BLUE,
            alpha=0.72, edgecolor='white', linewidth=0.4, marker='o',
            label='常用对数列 ' + D + 'n=%d' % len(lx) + D, zorder=4)
ax4.set_xscale('log')
ax4.set_yscale('log')
lim = (4e-4, 6e3)
ax4.set_xlim(*lim)
ax4.set_ylim(*lim)
ax4.plot(lim, lim, color='#D1D5DB', lw=0.8, ls=(0, (4, 2)), zorder=2)
ax4.xaxis.set_major_formatter(FuncFormatter(lambda v, p: '%g' % v))
ax4.yaxis.set_major_formatter(FuncFormatter(lambda v, p: '%g' % v))
ax4.xaxis.set_minor_formatter(NullFormatter())
ax4.yaxis.set_minor_formatter(NullFormatter())
ax4.set_xlabel('与 ' + D + r'\log_{10}(c)' + D + ' 的中位残差')
ax4.set_ylabel('与原值 ' + D + 'c' + D + ' 的中位残差')
ax4.legend(loc='center', frameon=False, handletextpad=0.3, borderaxespad=0.1)
frame(ax4, 'both')

save_fig(fig, 'figures/fig_prep_logbase_b.png')
print('log10=%d raw=%d' % (len(lx), len(rx)))
