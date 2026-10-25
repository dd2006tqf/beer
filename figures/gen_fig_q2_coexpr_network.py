# -*- coding: utf-8 -*-
"""fig_q2_coexpr_network — 化合物集 C(211) 共表达网络（仅显示度最高的 60 个主要节点）
节点=化合物，颜色=Louvain 社区（前 6 大模块着色，其余灰）；大小=度；
边=|Spearman|≥0.5 的显著共表达；枢纽节点名引到画布四周避免重叠。
数据源：problem_2_results.json::fig_data.network_nodes / network_edges, graph。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from _figbase import P2, PALETTE, save_fig, set_paper_placement

fd = P2['fig_data']
nodes = fd['network_nodes']; edges = fd['network_edges']; g = P2['graph']
node_ids = [n['id'] for n in nodes]; id_set = set(node_ids)

# 社区按规模排序，前 6 大着色，其余统一灰
import collections
comm_count = collections.Counter(n['comm'] for n in nodes)
big = [c for c, _ in comm_count.most_common(6)]
comm_col = {c: PALETTE[i % 6] for i, c in enumerate(big)}
comm_name = {c: f'模块{i+1}（社区{c}，{comm_count[c]}个）' for i, c in enumerate(big)}

try:
    import networkx as nx
    G = nx.Graph()
    for n in nodes:
        G.add_node(n['id'])
    for e in edges:
        if e['s'] in id_set and e['t'] in id_set:
            G.add_edge(e['s'], e['t'], weight=e.get('w', 1))
    pos = nx.spring_layout(G, seed=42, k=1.05, iterations=220, weight='weight')
except Exception:
    rng = np.random.default_rng(42)
    pos = {i: rng.normal(size=2) for i in node_ids}

fig, ax = plt.subplots(figsize=(8.6, 6.0))
set_paper_placement(fig)
wmax = max((e.get('w', 1) for e in edges), default=1)
for e in edges:
    if e['s'] in pos and e['t'] in pos:
        x0, y0 = pos[e['s']]; x1, y1 = pos[e['t']]
        ax.plot([x0, x1], [y0, y1], color='#D9DEE5', alpha=0.45,
                lw=0.4 + 1.2 * e.get('w', 1) / wmax, zorder=1)

degs = np.array([n['deg'] for n in nodes], float)
dmin, dmax = degs.min(), degs.max()
for n in nodes:
    if n['id'] not in pos:
        continue
    x, y = pos[n['id']]
    s = 55 + 380 * (n['deg'] - dmin) / ((dmax - dmin) or 1)
    ax.scatter(x, y, s=s, color=comm_col.get(n['comm'], '#C9CED6'),
               edgecolors='white', linewidths=0.7, alpha=0.92, zorder=3)

# 枢纽名引到画布四周（6 个锚点，按节点 x 左右、y 上下分配，避免重叠）
top = sorted(nodes, key=lambda z: -z['deg'])[:6]
anchors = [(0.015, 0.98, 'left', 'top'), (0.985, 0.98, 'right', 'top'),
           (0.015, 0.62, 'left', 'center'), (0.985, 0.62, 'right', 'center'),
           (0.015, 0.20, 'left', 'center'), (0.985, 0.20, 'right', 'center')]
order = sorted(range(len(top)), key=lambda i: pos[top[i]['id']][0])
for k, i in enumerate(order):
    n = top[i]
    cx, cy, ha, va = anchors[k]
    ax.annotate(n['name'], xy=pos[n['id']], xycoords='data',
                xytext=(cx, cy), textcoords='axes fraction',
                ha=ha, va=va, fontsize=8, color='#222',
                arrowprops=dict(arrowstyle='->', color='#777', lw=0.7, alpha=0.8),
                zorder=6)

ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_visible(False)
handles = [Patch(facecolor=comm_col[c], label=comm_name[c]) for c in big]
ax.legend(handles=handles, loc='lower center', fontsize=7.5, ncol=2, frameon=True,
          framealpha=0.92, edgecolor='#DDD')
fig.tight_layout()
save_fig(fig, 'figures/fig_q2_coexpr_network.png')
print('fig_q2_coexpr_network done; nodes=%d edges=%d' % (len(nodes), len(edges)))
