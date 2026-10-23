# -*- coding: utf-8 -*-
"""fig_q3_style_radar — 问题三：三代表风格生成谱感官画像对比（single，雷达图）
取在三风格间区分度最高的 12 个感官维，比较 CVAE 生成样本经 Q1 模型打分得到的画像。
数据源：problem_3_results.json::fig_data.radar.{dims, by_style}（Tripel/Kriek/Lambic）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P3, PALETTE, save_fig, set_paper_placement, dim_zh

rd = P3['fig_data']['radar']
dims = rd['dims']
by_style = rd['by_style']
styles = list(by_style.keys())

M = np.array([[by_style[s][d] for d in dims] for s in styles])   # (3, 30)
var = M.var(axis=0)
sel = np.argsort(-var)[:12]
sel = sorted(sel)                                                # 稳定顺序
dsel = [dims[i] for i in sel]
cats = [dim_zh(d) for d in dsel]
vals = {s: [by_style[s][d] for d in dsel] for s in styles}

n = len(cats)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(6.0, 5.6), subplot_kw={'projection': 'polar'})
set_paper_placement(fig)
for i, s in enumerate(styles):
    v = vals[s] + vals[s][:1]
    ax.plot(angles, v, 'o-', lw=1.6, ms=3.5, color=PALETTE[i % len(PALETTE)], label=s)
    ax.fill(angles, v, alpha=0.12, color=PALETTE[i % len(PALETTE)])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(cats, fontsize=7.0)
ax.tick_params(axis='y', labelsize=6.5)
ax.set_rlabel_position(90)
ax.legend(loc='upper right', bbox_to_anchor=(1.22, 1.10), fontsize=8, framealpha=0.9)

fig.tight_layout()
save_fig(fig, 'figures/fig_q3_style_radar.png')
print('fig_q3_style_radar done; dims=%d' % n)
