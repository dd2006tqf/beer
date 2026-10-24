# -*- coding: utf-8 -*-
"""fig_q3_style_radar — 三代表风格生成谱感官画像（雷达）
实线+填充=CVAE 生成谱经 Q1 打分的画像；虚线=同风格真实啤酒画像均值。
取在三风格间区分度最高的 12 个感官维（生成谱口径）。
数据源：problem_3_results.json::fig_data.radar.{dims, by_style, real_by_style}。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P3, PALETTE, save_fig, set_paper_placement, dim_zh

rd = P3['fig_data']['radar']
dims = rd['dims']; by_style = rd['by_style']; real = rd.get('real_by_style', {})
styles = list(by_style.keys())
M = np.array([[by_style[s][d] for d in dims] for s in styles])
sel = sorted(np.argsort(-M.var(axis=0))[:12])
dsel = [dims[i] for i in sel]
cats = [dim_zh(d) for d in dsel]
vals = {s: [by_style[s][d] for d in dsel] for s in styles}
rval = {s: [real.get(s, {}).get(d, np.nan) for d in dsel] for s in styles}

n = len(cats)
angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist(); angles += angles[:1]
fig, ax = plt.subplots(figsize=(6.8, 6.0), subplot_kw={'projection': 'polar'})
set_paper_placement(fig)
for i, s in enumerate(styles):
    c = PALETTE[i % len(PALETTE)]
    v = vals[s] + vals[s][:1]
    ax.plot(angles, v, 'o-', lw=1.8, ms=3.5, color=c, label=f'{s} 生成')
    ax.fill(angles, v, alpha=0.10, color=c)
    if real:
        rv = rval[s] + rval[s][:1]
        ax.plot(angles, rv, '^--', lw=1.3, ms=3.2, color=c, label=f'{s} 真实均值', alpha=0.85)
ax.set_xticks(angles[:-1]); ax.set_xticklabels(cats, fontsize=7.0)
ax.tick_params(axis='y', labelsize=6.5)
ax.set_rlabel_position(90)
ax.legend(loc='upper right', bbox_to_anchor=(1.32, 1.12), fontsize=7.2,
          framealpha=0.9, ncol=1)
fig.tight_layout()
save_fig(fig, 'figures/fig_q3_style_radar.png')
print('fig_q3_style_radar done; dims=%d real=%s' % (n, bool(real)))
