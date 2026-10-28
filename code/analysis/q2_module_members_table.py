# -*- coding: utf-8 -*-
"""C3b：Louvain 模块成员清单 + 孤立节点名单（附录表 B.3 的数据源）。"""
import os
import json

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
net = json.load(open(os.path.join(ROOT, "figures", "derived", "q2_full_network.json"), encoding="utf-8"))

comm = {}
for n in net["nodes"]:
    comm.setdefault(n["comm"], []).append(n)

mods = [(c, v) for c, v in comm.items() if c != ""]
mods.sort(key=lambda kv: -len(kv[1]))

out = {"n_nodes": len(net["nodes"]), "n_edges": net.get("n_edges"),
       "modularity": net.get("modularity"), "n_communities": len(mods), "modules": []}
for rank, (cid, nodes) in enumerate(mods, 1):
    nodes_sorted = sorted(nodes, key=lambda d: -d["deg"])
    out["modules"].append({
        "id": "M%02d" % rank,
        "comm": cid,
        "n_members": len(nodes),
        "deg_min": min(d["deg"] for d in nodes),
        "deg_max": max(d["deg"] for d in nodes),
        "representatives": [d["name"] for d in nodes_sorted[:3]],
        "members": [d["name"] for d in nodes_sorted],
    })

iso = [n["name"] for n in net["nodes"] if n["deg"] == 0]
out["n_isolated"] = len(iso)
out["isolated"] = iso

json.dump(out, open(os.path.join(ROOT, "figures", "derived", "q2_module_members.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("communities", len(mods), "isolated", len(iso))
for m in out["modules"][:6]:
    print(" ", m["id"], m["n_members"], m["deg_min"], "-", m["deg_max"], m["representatives"])
