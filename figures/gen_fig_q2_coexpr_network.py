# -*- coding: utf-8 -*-
"""fig_q2_coexpr_network — 问题二：化合物共表达网络（single）
节点=化合物（取度最高的 60 个），颜色=社区模块，大小=度；边=显著共表达。
展示网络的模块化结构（modularity=0.638，62 个社区）。
数据源：problem_2_results.json::fig_data.network_nodes / network_edges, graph。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from _figbase import P2, PALETTE, COLORS, save_fig, set_paper_placement

fd = P2['fig_data']
nodes = fd['network_nodes']
edges = fd['network_edges']
g = P2['graph']

node_ids = [n['id'] for n in nodes]
id_set = set(node_ids)
comms = sorted({n['comm'] for n in nodes})
comm_col = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(comms)}

try:
    import networkx as nx
    G = nx.Graph()
    for n in nodes:
        G.add_node(n['id'])
    for e in edges:
        if e['s'] in id_set and e['t'] in id_set:
            G.add_edge(e['s'], e['t'], weight=e.get('w', 1))
    pos = nx.spring_layout(G, seed=42, k=0.6, iterations=120, weight='weight')
except Exception:
    rng = np.random.default_rng(42)
    pos = {i: rng.normal(size=2) for i in node_ids}

fig, ax = plt.subplots(figsize=(6.4, 5.4))
set_paper_placement(fig)

# 边（浅灰，粗细随权重）
wmax = max((e.get('w', 1) for e in edges), default=1)
for e in edges:
    if e['s'] in pos and e['t'] in pos:
        x0, y0 = pos[e['s']]; x1, y1 = pos[e['t']]
        ax.plot([x0, x1], [y0, y1], color=COLORS['grid'], alpha=0.28,
                lw=0.4 + 1.2 * e.get('w', 1) / wmax, zorder=1)

# 节点
degs = np.array([n['deg'] for n in nodes], float)
dmin, dmax = degs.min(), degs.max()
for n in nodes:
    if n['id'] not in pos:
        continue
    x, y = pos[n['id']]
    s = 40 + 320 * (n['deg'] - dmin) / ((dmax - dmin) or 1)
    ax.scatter(x, y, s=s, color=comm_col[n['comm']], edgecolors='white',
               linewidths=0.6, alpha=0.92, zorder=3)

# 用引线把度最高的 4 个枢纽节点名标到画布四周空白处（避开密集点云）
top_nodes = [n for n in sorted(nodes, key=lambda n: -n['deg'])[:4] if n['id'] in pos]
xs = np.array([pos[n['id']][0] for n in top_nodes])
ys = np.array([pos[n['id']][1] for n in top_nodes])
xmn, xmx = xs.min(), xs.max()
corners = [(0.02, 0.98, 'left', 'top'), (0.98, 0.98, 'right', 'top'),
           (0.02, 0.02, 'left', 'bottom'), (0.98, 0.02, 'right', 'bottom')]
for k, n in enumerate(top_nodes):
    cx, cy, ha, va = corners[k]
    nm = n['name'] if len(n['name']) <= 16 else n['name'][:15] + '…'
    ax.annotate(nm, xy=pos[n['id']], xycoords='data',
                xytext=(cx, cy), textcoords='axes fraction',
                ha=ha, va=va, fontsize=6.6, color=COLORS['text'],
                arrowprops=dict(arrowstyle='-', color=COLORS['text'], lw=0.5, alpha=0.6),
                zorder=5)

ax.set_xticks([]); ax.set_yticks([])
for sp in ax.spines.values():
    sp.set_visible(False)
# 节点大小随度、颜色随社区（模块度/社区数写入图注，不占图内图例避免空数据代理）

fig.tight_layout()
save_fig(fig, 'figures/fig_q2_coexpr_network.png')
print('fig_q2_coexpr_network done; nodes=%d edges=%d' % (len(nodes), len(edges)))
