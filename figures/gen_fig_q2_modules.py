# -*- coding: utf-8 -*-
"""fig_q2_modules —— 共表达网络：最大连通分量 + 其余节点点阵

左：最大连通分量（159 节点）的布局图。节点按 Louvain 社区着色、大小=度；
    前 5 大模块用淡色椭圆圈出，并标出各自度最高的代表化合物。
右：其余节点按社区规模与度排序的点阵，直观呈现"少量大模块 + 大量孤立点"。

原网络图只画了度最高的 60 个节点，读者看不到 211 个节点里有 44 个完全孤立
这一结构事实；这张图把它摆出来。

数据源：_tmp/q2_full_network.json（按 code/problem2.py 同一口径重算的全图）。
"""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Ellipse
from _figbase import PALETTE, save_fig
from _utils.plot_utils import ROOT

net = json.load(open(os.path.join(ROOT, '_tmp', 'q2_full_network.json'), encoding='utf-8'))
nodes = net['nodes']; edges = net['edges']
comm_sizes = collections.Counter(n['comm'] for n in nodes)

import networkx as nx
G = nx.Graph()
for n in nodes:
    G.add_node(n['id'], deg=n['deg'], comm=n['comm'], name=n['name'])
for e in edges:
    G.add_edge(e['s'], e['t'], weight=e['w'])

plt.rcParams.update({
    'axes.labelsize': 7.2,
    'xtick.labelsize': 6.2,
    'ytick.labelsize': 6.2,
    'legend.fontsize': 6.3,
    'axes.unicode_minus': False,
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.6, 3.55),
                               gridspec_kw={'width_ratios': [1.9, 1.0], 'wspace': 0.06},
                               layout='constrained')

# ══ 左：最大连通分量 ══════════════════════════════════════
comps = sorted(nx.connected_components(G), key=len, reverse=True)
main = comps[0]
H = G.subgraph(main)
pos = nx.spring_layout(H, seed=42, k=0.75, iterations=300, weight='weight')

for u, v, d in H.edges(data=True):
    x0, y0 = pos[u]; x1, y1 = pos[v]
    ax1.plot([x0, x1], [y0, y1], color='#C7D2DE',
             lw=0.35 + 1.1 * d['weight'], alpha=0.5, zorder=1)

big = [c for c, _ in comm_sizes.most_common(5)]
ccol = {c: PALETTE[i] for i, c in enumerate(big)}

for n in nodes:
    if n['id'] not in pos:
        continue
    x, y = pos[n['id']]
    ax1.scatter(x, y, s=14 + 4.6 * n['deg'], color=ccol.get(n['comm'], '#CBD5E1'),
                edgecolors='white', linewidths=0.5, alpha=0.95, zorder=3)

for i, c in enumerate(big):
    mem = [n for n in nodes if n['comm'] == c and n['id'] in pos]
    if len(mem) < 5:
        continue
    xs = np.array([pos[m['id']][0] for m in mem]); ys = np.array([pos[m['id']][1] for m in mem])
    cx, cy = xs.mean(), ys.mean()
    ax1.add_patch(Ellipse((cx, cy), (xs.max()-xs.min())*0.85+0.1,
                          (ys.max()-ys.min())*0.85+0.1, fill=True,
                          facecolor=ccol[c], alpha=0.06, edgecolor=ccol[c],
                          lw=0.9, zorder=0))
    hub = max(mem, key=lambda m: m['deg'])
    name = hub['name']
    ax1.annotate('M%d %s' % (i + 1, name if len(name) <= 14 else name[:13] + '…'),
                 xy=pos[hub['id']], xytext=(cx, cy + 0.10),
                 ha='center', fontsize=5.9, color=ccol[c], zorder=6,
                 bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.8))

ax1.set_xticks([]); ax1.set_yticks([])
for s in ax1.spines.values():
    s.set_visible(False)
ax1.set_aspect('equal'); ax1.margins(0.05)

# ══ 右：其余节点 ══════════════════════════════════════════
rest = [n for n in nodes if n['id'] not in pos]
rest.sort(key=lambda n: (-comm_sizes[n['comm']], -n['deg']))
cols = 11
for k, n in enumerate(rest):
    r, c = divmod(k, cols)
    ax2.scatter(c, -r, s=7 + 2.0 * n['deg'], color=ccol.get(n['comm'], '#CBD5E1'),
                edgecolors='white', linewidths=0.3, alpha=0.9, zorder=3)
nrow = (len(rest) + cols - 1) // cols
ax2.set_xlim(-0.8, cols - 0.2)
ax2.set_ylim(-nrow + 0.2, 1.6)
ax2.set_xticks([]); ax2.set_yticks([])
for s in ax2.spines.values():
    s.set_visible(False)
ax2.text(cols / 2 - 0.5, 1.15,
         '其余 %d 节点：%d 个完全孤立' % (len(rest), net['n_isolated']),
         ha='center', fontsize=6.5, color='#374151')
ax2.text(cols / 2 - 0.5, -nrow - 0.05,
         '%d 节点 | %d 边 | %d 社区 | Q=%.4f'
         % (net['n_nodes'], net['n_edges'], net['n_communities'], net['modularity']),
         ha='center', fontsize=5.9, color='#6B7280')

legend = [Patch(facecolor=ccol[c], label='M%d (%d)' % (i + 1, comm_sizes[c]))
          for i, c in enumerate(big)]
legend.append(Patch(facecolor='#CBD5E1', label='其余'))
fig.legend(handles=legend, loc='outside lower center', ncol=len(legend),
           frameon=False, handlelength=0.9, columnspacing=1.0,
           handletextpad=0.35, borderaxespad=0.05)

save_fig(fig, 'figures/fig_q2_modules.png')
print('done; main=%d rest=%d iso=%d comms=%d Q=%.4f'
      % (len(main), len(rest), net['n_isolated'], net['n_communities'], net['modularity']))
