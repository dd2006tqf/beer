# -*- coding: utf-8 -*-
"""fig_prep_logbase — 数据预处理对数底核实四联图
(a) 22 风格样本量；(b) 三类指标 检出/未检出/缺失 占比；
(c) 校准散点：1.csv 取值 x 对 log10(校准绝对浓度)，点贴 y=x（常用对数列示例）；
(d) 70 个可校准列的中位残差：37 列 res_log10≈0（贴纵轴），33 列 res_raw≈0（贴横轴）。
数据源：supp_preprocess.json（由 8.xlsx Calibrated chemical dataset 逐样本实算）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import load, PALETTE, save_fig, set_paper_placement, declutter_axes, panel

PP = load('supp_preprocess.json')
lb = PP['log_base_audit']

fig, axes = plt.subplots(2, 2, figsize=(9.2, 7.2))
set_paper_placement(fig)

# ── (a) 风格样本量条形（降序）──────────────────────────
ax = axes[0, 0]
sc = sorted(PP['style_counts'], key=lambda z: z[1], reverse=True)
names = [s[0] for s in sc][::-1]; vals = [s[1] for s in sc][::-1]
ax.barh(np.arange(len(names)), vals, color=PALETTE[0], edgecolor='white', linewidth=0.4)
ax.set_yticks(np.arange(len(names)))
ax.set_yticklabels(names, fontsize=5.8)
ax.set_xlabel('样本款数')
for i, v in enumerate(vals):
    ax.text(v + 0.3, i, str(v), va='center', fontsize=5.4, color='#333')
ax.set_title(f'{len(names)} 种风格样本量（共 250 款）', fontsize=10, fontweight='bold', loc='left', pad=3)
declutter_axes(ax, grid_axis='x')

# ── (b) 三类指标 检出/未检出/缺失 占比堆叠 ────────────────
ax = axes[0, 1]
gs = PP['missing_vs_belowlod']['group_stats']
grp = ['physicochemical', 'aggregate', 'compound_C']
lab = ['理化/过程参数\n(16 列)', '多化合物汇总\n(4 列)', '单一化合物集 C\n(211 列)']
det = [gs[g]['detected'] * 100 for g in grp]
bl = [gs[g]['below_lod'] * 100 for g in grp]
ms = [gs[g]['missing'] * 100 for g in grp]
x = np.arange(len(grp))
ax.bar(x, det, color=PALETTE[0], label='检出')
ax.bar(x, bl, bottom=det, color=PALETTE[3], label='未检出(≤列下限)')
ax.bar(x, ms, bottom=np.array(det) + np.array(bl), color=PALETTE[2], label='真正缺失(NA)')
ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=8)
ax.set_ylabel('占比（%）'); ax.set_ylim(0, 100)
ax.legend(fontsize=7, loc='lower center', ncol=3, bbox_to_anchor=(0.5, -0.32), frameon=False)
ax.set_title('三类指标的检出/未检出/缺失构成', fontsize=10, fontweight='bold', loc='left', pad=3)
declutter_axes(ax, grid_axis='y')

# ── (c) 校准散点：x = log10(c) ──────────────────────────
ax = axes[1, 0]
scat = lb['scatter']
demo = ['DMS', 'acetaldehyde', 'ethyl_acetate', 'X4VG']
cols = [PALETTE[0], PALETTE[1], PALETTE[4], PALETTE[2]]
for c, col in zip(demo, cols):
    if c in scat:
        ax.scatter(scat[c]['log10_c'], scat[c]['x_in_1csv'], s=11, alpha=0.65,
                   color=col, edgecolor='white', linewidth=0.3, label=c)
lo, hi = -3.2, 1.2
ax.plot([lo, hi], [lo, hi], '--', color='#444', linewidth=1.1, label='y=x')
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
ax.set_xlabel('校准绝对浓度 log10(c)  [mg/L]')
ax.set_ylabel('1.csv 取值 x')
ax.legend(fontsize=6.6, loc='upper left', frameon=False, ncol=2)
ax.set_title('37 列严格满足 x = log10(c)（残差<1e-6，示例）', fontsize=10,
             fontweight='bold', loc='left', pad=3)
declutter_axes(ax)

# ── (d) 70 列中位残差散点（双对数 +1）────────────────────
ax = axes[1, 1]
pc = lb['per_col']
lx, ly, cx, cy = [], [], [], []
for c, v in pc.items():
    if 'median_abs_res_log10' not in v:
        continue
    if v['verdict'].startswith('log10'):
        lx.append(v['median_abs_res_log10'] + 1e-3); ly.append(v['median_abs_res_raw'] + 1e-3)
    else:
        cx.append(v['median_abs_res_log10'] + 1e-3); cy.append(v['median_abs_res_raw'] + 1e-3)
ax.scatter(lx, ly, s=16, color=PALETTE[0], alpha=0.75, edgecolor='white', linewidth=0.3,
           label=f'常用对数列 n={len(lx)}（贴纵轴）')
ax.scatter(cx, cy, s=16, color=PALETTE[3], alpha=0.75, edgecolor='white', linewidth=0.3,
           label=f'原值列 n={len(cx)}（贴横轴）')
ax.set_xscale('log'); ax.set_yscale('log')
ax.set_xlabel('与 log10(c) 的中位残差  +1e-3')
ax.set_ylabel('与原值 c 的中位残差  +1e-3')
ax.legend(fontsize=7, loc='upper center', frameon=False)
ax.set_title('70 个可校准列：无自然对数，呈混合尺度', fontsize=10,
             fontweight='bold', loc='left', pad=3)
declutter_axes(ax)

fig.tight_layout()
save_fig(fig, 'figures/fig_prep_logbase.png')
print('fig_prep_logbase done; log10=%d raw=%d' % (len(lx), len(cy)))
