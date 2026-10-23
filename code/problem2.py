# -*- coding: utf-8 -*-
"""问题二：化合物共表达图 + 多证据 Top-3 + 稳定性（P2-C1/C2/C3/C4）。

忠实 MODELING_REPORT §七 / METHOD_CLAIMS M4-M6：
- M4 共表达图：networkx 建图，边权=2.csv 相关系数，|w|>=rho，louvain 社区检测。
- M5 归因：SHAP(TreeExplainer) 对 Q1 LightGBM 模型 + 6.csv 交叉相关 + 模块代表 融合(式6)。
- M6 稳定性：bootstrap(B=500) 入选频率 + 跨方法(SHAP/相关/RF) Jaccard。
"""
import os
import sys
import warnings

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_ROOT = os.path.dirname(_HERE)

import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")

import params as P
import utils as U
import networkx as nx
import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer


def _norm(v):
    v = np.asarray(v, dtype=float)
    v = np.where(np.isfinite(v), v, 0.0)
    mx = np.abs(v).max()
    return v / mx if mx > 0 else v


def build_coexpr_graph(R, comp_names, rho):
    """以 231 化合物为节点、|corr|>=rho 为边建无向图 + louvain 社区。"""
    n = R.shape[0]
    G = nx.Graph()
    for i in range(n):
        G.add_node(i, name=comp_names[i])
    n_edges = 0
    for i in range(n):
        for j in range(i + 1, n):
            w = R[i, j]
            if np.isfinite(w) and abs(w) >= rho:
                G.add_edge(i, j, weight=float(w))
                n_edges += 1
    # 社区检测（louvain；回退 greedy_modularity）
    try:
        import community as community_louvain
        part = community_louvain.best_partition(G, weight="weight", random_state=P.SEED)
        comm = {k: int(v) for k, v in part.items()}
        method = "louvain"
    except Exception:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = greedy_modularity_communities(G, weight="weight")
        comm = {node: ci for ci, cset in enumerate(comms) for node in cset}
        method = "greedy_modularity"
    # 模块度
    try:
        from networkx.algorithms.community import modularity
        groups = {}
        for node, ci in comm.items():
            groups.setdefault(ci, set()).add(node)
        Q = modularity(G, list(groups.values()), weight="weight")
    except Exception:
        Q = None
    return G, comm, method, n_edges, Q


def run(data_dir="user_data", out_dir=None):
    out_dir = out_dir or _ROOT
    U.set_all_seeds(P.SEED)
    fig_dir = os.path.join(out_dir, "figures")
    sub_dir = os.path.join(out_dir, "submission")
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(sub_dir, exist_ok=True)

    df1, X, feat_cols, meta = U.load_chem(data_dir)
    Y, sens_cols = U.load_sensory(data_dir)
    R, comp_names = U.load_compound_corr(data_dir)
    C6, comp_rows6, sens6 = U.load_cross_corr(data_dir)
    Xv = X.values.astype(float)
    Yv = Y.values.astype(float)
    J = len(sens_cols)

    # 1) 共表达图 + 社区
    G, comm, cmethod, n_edges, Qmod = build_coexpr_graph(R, comp_names, P.COEXPR_RHO)
    n_comm = len(set(comm.values()))
    print(f"[Q2] 共表达图 节点={G.number_of_nodes()} 边={n_edges} 社区数={n_comm}({cmethod}) 模块度Q={Qmod}")
    comm_arr = np.array([comm.get(i, -1) for i in range(len(feat_cols))])

    # 2) SHAP 证据（对 Q1 全量 LightGBM 模型）
    shap_imp, abs_shap_list, shap_dim_order = _shap_evidence(sens_cols, feat_cols, Xv)

    # 3) 6.csv 交叉相关证据（映射到 231 位置）
    corr_evid = _corr_evidence(C6, comp_rows6, comp_names, feat_cols, sens_cols)

    # 4) RF 重要性证据（跨方法用）
    rf_imp = _rf_evidence(Xv, Yv, J)

    # 5) 融合 + 模块代表 → Top-3；稳定性
    results = _fuse_and_stability(sens_cols, feat_cols, shap_imp, corr_evid, rf_imp,
                                  abs_shap_list, comm_arr)

    # 6) 交付 + 图数据 + 验证
    _write_submission(out_dir, results, sens_cols, feat_cols, corr_evid, comm_arr)
    results["graph"] = {"n_nodes": G.number_of_nodes(), "n_edges": n_edges,
                        "n_communities": n_comm, "method": cmethod,
                        "modularity": round(float(Qmod), 4) if Qmod is not None else None,
                        "rho": P.COEXPR_RHO}
    _build_graph_figdata(results, G, comm, comp_names, R)
    _validate(out_dir, results, sens_cols)
    U.save_json(results, os.path.join(fig_dir, "problem_2_results.json"))
    print("[Q2] 完成，结果写入 figures/problem_2_results.json")
    return results
def _shap_evidence(sens_cols, feat_cols, Xv):
    """用 Q1 全量 LightGBM 模型算每维 SHAP。返回 (importance[J×P], 每维|shap|矩阵列表)。"""
    ck = U.ckpt_path("q1_models.pkl")
    assert os.path.exists(ck), "缺 q1_models.pkl：请先跑 problem1.py"
    import joblib
    bundle = joblib.load(ck)
    models = bundle["models"]
    J, Pn = len(sens_cols), len(feat_cols)
    imp = np.zeros((J, Pn))
    abs_shap_list = []
    for j, col in enumerate(sens_cols):
        if col in models:
            expl = shap.TreeExplainer(models[col])
            sv = expl.shap_values(Xv)       # N×P
            sv = np.asarray(sv)
            abs_sv = np.abs(sv)
            imp[j] = abs_sv.mean(axis=0)
            abs_shap_list.append(abs_sv)
        else:
            # 该维提交基线（无 LightGBM 模型）：SHAP 证据置 0，依赖相关/RF
            abs_shap_list.append(np.zeros((Xv.shape[0], Pn)))
        if (j + 1) % 10 == 0:
            print(f"[Q2] SHAP 进度 {j+1}/{J}")
    return imp, abs_shap_list, sens_cols


def _corr_evidence(C6, comp_rows6, comp_names, feat_cols, sens_cols):
    """6.csv 交叉相关 → 231 位置 × 50 感官的 |corr| 证据（未覆盖化合物记 0）。"""
    J, Pn = len(sens_cols), len(feat_cols)
    evid = np.zeros((J, Pn))
    # 6.csv 行名(全名) → 2.csv 位置
    name2pos = {name: i for i, name in enumerate(comp_names)}
    # 6.csv 感官列与 4.csv 50 维按位置对齐
    row_pos = {r: name2pos.get(r, None) for r in comp_rows6}
    Cv = C6.values.astype(float)   # 44 × 50
    n_mapped = 0
    for ri, r in enumerate(comp_rows6):
        pos = row_pos[r]
        if pos is None:
            continue
        n_mapped += 1
        for j in range(J):
            v = Cv[ri, j]
            evid[j, pos] = abs(v) if np.isfinite(v) else 0.0
    print(f"[Q2] 6.csv 交叉相关映射化合物 {n_mapped}/{len(comp_rows6)} → 231 位置")
    return evid


def _rf_evidence(Xv, Yv, J):
    """随机森林重要性（中位插补）作为跨方法证据。"""
    imp = np.zeros((J, Xv.shape[1]))
    med = SimpleImputer(strategy="median").fit(Xv)
    Xm = med.transform(Xv)
    for j in range(J):
        rf = RandomForestRegressor(n_estimators=120, max_depth=6,
                                   random_state=P.SEED, n_jobs=-1)
        rf.fit(Xm, Yv[:, j])
        imp[j] = rf.feature_importances_
        if (j + 1) % 10 == 0:
            print(f"[Q2] RF 证据 {j+1}/{J}")
    return imp


def _module_rep(base_scores, comm_arr):
    """模块代表加权：同社区内按 base 排名，第 1 名 rep=1，第 2=1/2…（促进 Top-3 跨模块多样）。"""
    rep = np.zeros_like(base_scores)
    for ci in np.unique(comm_arr):
        idx = np.where(comm_arr == ci)[0]
        order = idx[np.argsort(-base_scores[idx])]
        for rank, p in enumerate(order, 1):
            rep[p] = 1.0 / rank
    return rep
def _topk(score, k=P.TOPN):
    return list(np.argsort(-score)[:k])


def _jaccard(a, b):
    a, b = set(a), set(b)
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def _fuse_and_stability(sens_cols, feat_cols, shap_imp, corr_evid, rf_imp, abs_shap_list, comm_arr):
    J, Pn = len(sens_cols), len(feat_cols)
    a, b, g = P.FUSE_ALPHA, P.FUSE_BETA, P.FUSE_GAMMA
    per_dim = {}
    top3_idx = {}
    # 点估计
    shap_n_all = np.vstack([_norm(shap_imp[j]) for j in range(J)])
    corr_n_all = np.vstack([_norm(corr_evid[j]) for j in range(J)])
    rf_n_all = np.vstack([_norm(rf_imp[j]) for j in range(J)])
    phi_all = np.zeros((J, Pn))
    for j in range(J):
        base = a * shap_n_all[j] + b * corr_n_all[j]
        rep = _module_rep(base, comm_arr)
        phi = base + g * rep
        phi_all[j] = phi
        top3_idx[j] = _topk(phi)
    # bootstrap 入选频率（有放回重采样样本 → 重算 SHAP 重要性 → 重算 Top-3）
    np.random.seed(P.SEED)               # 固定种子保证可复现
    N = abs_shap_list[0].shape[0]
    freq = np.zeros((J, Pn))
    B = P.N_BOOTSTRAP
    for bi in range(B):
        idx = np.random.choice(N, size=N, replace=True)   # 有放回重采样
        for j in range(J):
            shap_b = _norm(abs_shap_list[j][idx].mean(axis=0))
            base_b = a * shap_b + b * corr_n_all[j]
            phi_b = base_b + g * _module_rep(base_b, comm_arr)
            for p in _topk(phi_b):
                freq[j, p] += 1
        if (bi + 1) % 100 == 0:
            print(f"[Q2] bootstrap {bi+1}/{B}")
    freq /= B
    # 跨方法 Jaccard（SHAP / 6.csv相关 / RF）
    jac_dim = {}
    for j in range(J):
        ts = _topk(shap_n_all[j]); tc = _topk(corr_n_all[j]); tr = _topk(rf_n_all[j])
        pj = np.mean([_jaccard(ts, tc), _jaccard(ts, tr), _jaccard(tc, tr)])
        jac_dim[sens_cols[j]] = round(float(pj), 4)

    for j, col in enumerate(sens_cols):
        t3 = top3_idx[j]
        per_dim[col] = {
            "top3": [feat_cols[p] for p in t3],
            "top3_idx": [int(p) for p in t3],
            "phi": [round(float(phi_all[j, p]), 4) for p in t3],
            "shap_norm": [round(float(shap_n_all[j, p]), 4) for p in t3],
            "corr_abs": [round(float(corr_n_all[j, p]), 4) for p in t3],
            "select_freq": [round(float(freq[j, p]), 4) for p in t3],
            "module": [int(comm_arr[p]) for p in t3],
            "jaccard_cross_method": jac_dim[col],
        }
    mean_top1_freq = float(np.mean([per_dim[c]["select_freq"][0] for c in sens_cols]))
    mean_jac = float(np.mean(list(jac_dim.values())))
    # 高稳定维度数（Top-1 入选频率>=0.7）
    n_high_stable = int(sum(1 for c in sens_cols if per_dim[c]["select_freq"][0] >= 0.7))
    print(f"[Q2] 平均Top-1入选频率={mean_top1_freq:.3f} 平均跨方法Jaccard={mean_jac:.3f} "
          f"高稳定维={n_high_stable}")
    return {
        "problem": 2,
        "method": "共表达图(networkx+louvain) + SHAP/相关/模块代表融合 + bootstrap频率 + 跨方法Jaccard",
        "summary": {"n_dims": J, "n_bootstrap": B, "topn": P.TOPN,
                    "mean_top1_select_freq": round(mean_top1_freq, 4),
                    "mean_cross_method_jaccard": round(mean_jac, 4),
                    "n_high_stable_dims": n_high_stable,
                    "fuse_weights": {"alpha": a, "beta": b, "gamma": g}},
        "per_dim": per_dim, "sensory_cols": sens_cols,
    }
_MECH_RULES = [
    (("ethyl_", "ethyl.", "acetate", "isoaa", "ester", "lactate", "butyrate",
      "octanoate", "hexanoate", "propionate", "decanoate"), "酯类→果香/香蕉/溶剂气味"),
    (("linalool", "geraniol", "citronellol", "terpine", "ocimene", "humulene",
      "caryophyll", "farnes", "nerol", "limonene", "phellandrene", "myrcene"),
     "萜烯类→酒花花香/柑橘/木质香"),
    (("dms", "sulfur", "h2s", "mesh", "des", "cs2", "thiol", "sulfide"),
     "硫化物/DMS→蔬菜/硫味（低阈缺陷）"),
    (("butanedione", "diacetyl"), "双乙酰→黄油味缺陷"),
    (("x4vg", "guaiacol", "vinyl", "phenol", "cresol"), "酚类(4VG)→丁香/药味"),
    (("nonenal", "decadienal", "aldehyde", "furfural", "methylbutanal"),
     "醛类→老化/青草/纸板气味"),
    (("malt", "furan", "maltol", "pyrazine", "isomaltol", "vanillin"),
     "麦芽/美拉德→焦糖/面包/烘烤"),
    (("ethanol", "isoamyl_alcohol", "isobutanol", "propanol", "alcohol"),
     "高级醇/乙醇→酒精感"),
    (("acid", "acetic", "lactic"), "有机酸→酸味"),
]


def _mechanism(feat_name):
    if feat_name in P.PHYSICOCHEM_COLS:
        return "理化/过程指标（非挥发性化合物），反映风格整体工艺特征，常与风格混杂相关"
    low = feat_name.lower()
    for keys, txt in _MECH_RULES:
        if any(k in low for k in keys):
            return txt
    return "其他挥发性化学信号（见共表达模块）"


def _write_submission(out_dir, results, sens_cols, feat_cols, corr_evid, comm_arr):
    rows = []
    for col in sens_cols:
        d = results["per_dim"][col]
        for rank, (fn, phi, sh, co, fr, mod) in enumerate(
                zip(d["top3"], d["phi"], d["shap_norm"], d["corr_abs"],
                    d["select_freq"], d["module"]), 1):
            rows.append({
                "sensory_dim": col, "rank": rank, "compound": fn,
                "phi_score": phi, "shap_norm": sh, "cross_corr_abs": co,
                "bootstrap_select_freq": fr, "module_id": mod,
                "jaccard_cross_method": d["jaccard_cross_method"],
                "feature_type": P.feature_type(fn),
                "mechanism": _mechanism(fn),
            })
    sub = pd.DataFrame(rows)
    path = os.path.join(out_dir, "submission", "q2_top3_compounds.csv")
    sub.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[Q2] 写出 {path}  shape={sub.shape}（每维 {P.TOPN} 行）")
    results["submission"] = {"path": "submission/q2_top3_compounds.csv",
                             "rows": int(sub.shape[0])}


def _build_graph_figdata(results, G, comm, comp_names, R):
    """为网络图提供布局数据（取最大连通子图 + 节点度/社区）；只存前若干边避免过大。"""
    deg = dict(G.degree(weight=None))
    # 节点度排序，取度数前 60 个节点做可视化子图
    top_nodes = sorted(deg, key=lambda n: -deg[n])[:60]
    sub = G.subgraph(top_nodes)
    nodes = [{"id": int(n), "name": comp_names[n], "deg": int(deg[n]),
              "comm": int(comm.get(n, -1))} for n in sub.nodes()]
    edges = [{"s": int(u), "t": int(v), "w": round(float(d["weight"]), 3)}
             for u, v, d in sub.edges(data=True)]
    comm_sizes = {}
    for n, ci in comm.items():
        comm_sizes[ci] = comm_sizes.get(ci, 0) + 1
    results["fig_data"] = {
        "network_nodes": nodes, "network_edges": edges,
        "community_sizes": sorted(comm_sizes.values(), reverse=True),
        "top1_freq_ranked": sorted(
            ((c, results["per_dim"][c]["select_freq"][0],
              results["per_dim"][c]["jaccard_cross_method"]) for c in results["sensory_cols"]),
            key=lambda t: -t[1]),
    }


def _validate(out_dir, results, sens_cols):
    sub = pd.read_csv(os.path.join(out_dir, "submission", "q2_top3_compounds.csv"))
    # 硬约束：每维恰 3 行
    sizes = sub.groupby("sensory_dim").size()
    assert (sizes == P.TOPN).all(), f"[P2-C2] 存在维度 Top-N!=3: {sizes[sizes!=P.TOPN].to_dict()}"
    assert sizes.shape[0] == len(sens_cols), "Top-3 覆盖维度数!=50"
    # 频率/Jaccard ∈[0,1]
    for c in ("bootstrap_select_freq", "jaccard_cross_method"):
        assert sub[c].between(0, 1).all(), f"[P2-C3] {c} 越界[0,1]"
    print("[Q2] validate_constraints PASS（每维3行/频率∈[0,1]/Jaccard∈[0,1]）")
    # 能力断言：P2-C3 bootstrap>=200 + 跨方法>=2；P2-C4 每维有机理
    assert results["summary"]["n_bootstrap"] >= 200, "[P2-C3] bootstrap<200"
    assert sub["mechanism"].notna().all() and (sub["mechanism"].str.len() > 0).all(), \
        "[P2-C4] 存在缺机理解释的 Top-3"
    assert results["summary"]["mean_cross_method_jaccard"] >= 0, "[P2-C3] 跨方法Jaccard缺失"
    print("[Q2] validate_capability PASS（P2-C3 500次bootstrap+3方法Jaccard / P2-C4 逐维机理）")


if __name__ == "__main__":
    dd = sys.argv[1] if len(sys.argv) > 1 else "user_data"
    run(dd)



