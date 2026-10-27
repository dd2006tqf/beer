# -*- coding: utf-8 -*-
"""fig_q3_transfer_heat —— 跨风格迁移的化合物级扰动方向与幅度

11 条 Pils/Lager→Tripel 迁移样本（行）× 12 个关键化合物（列），
格内为该化合物相对源款的变化 Δ，按训练集该列标准差标准化（Δ/σ），
橙红=上调、蓝=下调，零中心；右侧一列标注缺陷化合物的约束生效情况。

相比只报 4 个缺陷均值的哑铃图，这张图回答"迁移到底改了哪些化合物、
改了多少"，并能看出风味骨架（酯醇）被整体上调、缺陷被压回。

数据源：submission/q3_generated_profiles.csv（transfer 行）+ user_data/1.csv。
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from _figbase import save_fig
from _utils.plot_utils import ROOT

raw = pd.read_csv(os.path.join(ROOT, 'user_data', '1.csv'))
gen = pd.read_csv(os.path.join(ROOT, 'submission', 'q3_generated_profiles.csv'))
feat = [c for c in gen.columns if c in raw.columns]

KEYS = [('ethanol..v.v.', '乙醇'), ('ethyl_octanoate', '辛酸乙酯'),
        ('ethyl_acetate', '乙酸乙酯'), ('ethyl_isovalerate', '异戊酸乙酯'),
        ('ethyl_decanoate', '癸酸乙酯'), ('acetaldehyde', '乙醛'),
        ('glycerol', '甘油'), ('linalool', '芳樟醇'),
        ('DMS', 'DMS'), ('X2.3.butanedione', '双乙酰'),
        ('X4VG', '4-VG'), ('X.E..2.nonenal', '反-2-壬烯醛')]
KEYS = [(c, n) for c, n in KEYS if c in feat]
defects = ['DMS', 'X2.3.butanedione', 'X4VG', 'X.E..2.nonenal']

tr = gen[gen['sample_type'] == 'transfer'].reset_index(drop=True)
n_tr = len(tr)
# 源款：按 style 中的 "A->B" 找不到具体行，改用迁移前后差值 =
# 迁移谱 − 源风格（Pils/Lager）均值；这是题目口径下的整体位移
src_mean = raw[raw['tasting_category_fine'] == 'Pils/Lager'][feat].mean()
sd = raw[feat].std().replace(0, np.nan)

D = np.zeros((n_tr, len(KEYS)))
for j, (c, _) in enumerate(KEYS):
    D[:, j] = (tr[c].values - src_mean[c]) / (sd[c] if np.isfinite(sd[c]) and sd[c] > 1e-9 else 1.0)

plt.rcParams.update({
    'axes.labelsize': 7.6,
    'xtick.labelsize': 6.6,
    'ytick.labelsize': 6.4,
    'axes.unicode_minus': False,
})

fig, (ax, axb) = plt.subplots(1, 2, figsize=(6.5, 3.5),
                              gridspec_kw={'width_ratios': [3.05, 0.75], 'wspace': 0.06},
                              layout='constrained')

lim = np.nanpercentile(np.abs(D), 96)
norm = TwoSlopeNorm(vmin=-lim, vcenter=0, vmax=lim)
im = ax.imshow(D, cmap='RdBu_r', norm=norm, aspect='auto', interpolation='nearest')
ax.set_xticks(np.arange(len(KEYS)))
ax.set_xticklabels([n for _, n in KEYS], rotation=48, ha='right', fontsize=6.6)
ax.set_yticks([0, n_tr - 1])
ax.set_yticklabels(['1', str(n_tr)], fontsize=6.4)
ax.set_ylabel('迁移样本（%d 条）' % n_tr)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
# 缺陷列加框，突显被约束的列
for j, (c, _) in enumerate(KEYS):
    if c in defects:
        ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1, n_tr, fill=False,
                                   edgecolor='#1F3B5C', lw=1.0, zorder=5))

# 右：每个关键化合物的平均标准化位移，正负分色
mean_d = np.nanmean(D, axis=0)
yy = np.arange(len(KEYS))
cols = ['#C0392B' if v > 0 else '#2E5C8A' for v in mean_d]
axb.barh(yy, mean_d, height=0.62, color=cols, edgecolor='none', zorder=3)
axb.axvline(0, color='#6B7280', lw=0.8, zorder=4)
axb.set_yticks(yy)
axb.set_yticklabels([])
axb.set_ylim(len(KEYS) - 0.5, -0.5)
axb.set_xlabel('平均 Δ/σ', fontsize=7.0)
axb.set_xlim(min(mean_d.min() * 1.35, -0.1), max(mean_d.max() * 1.35, 0.1))
for s in ('top', 'right', 'left'):
    axb.spines[s].set_visible(False)
axb.tick_params(axis='y', length=0)
axb.grid(axis='x', color='#E5E7EB', lw=0.6, zorder=0)
axb.set_axisbelow(True)

cb = fig.colorbar(im, ax=[ax, axb], fraction=0.022, pad=0.015)
cb.outline.set_visible(False)
cb.set_label('相对源风格的标准化位移 Δ/σ', fontsize=6.8)
cb.ax.tick_params(labelsize=6.2, length=2)

save_fig(fig, 'figures/fig_q3_transfer_heat.png')
print('done; n_tr=%d  cols=%d  深框=缺陷列' % (n_tr, len(KEYS)))
