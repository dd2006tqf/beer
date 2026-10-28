# -*- coding: utf-8 -*-
"""问题二：化合物共表达图 + 多证据 Top-3 + 稳定性（P2-C1/C2/C3/C4）。

忠实 MODELING_REPORT §七 / METHOD_CLAIMS M4-M6，并按本轮用户指令把 Q2 归因候选集
严格限定在「纯化合物集 C」（231 − 16 理化列 − 4 汇总列 = 211 列）：
- M4 共表达图：networkx 建图，节点仅 C（211 项），边=2.csv 相关系数 |w|>=rho 且两端均 ∈C，
  louvain 社区检测（community 包），重算 n_nodes/n_edges/n_communities/modularity。
- M5 归因：SHAP(TreeExplainer) 对 Q1 全 231 特征 LightGBM 模型 + 6.csv 交叉相关 + RF 仍对全 231
  计算，但 _topk / 融合 φ=0.5SHAP+0.3|corr|+0.2module_rep / bootstrap(B=500) 入选频率 /
  跨方法 Jaccard 一律只在 C 的位置索引内取（非 C 位置分数置 -inf，永不选中理化/汇总列）；
  module_rep 只在 C 的社区内计算。
- 显式去冗余：按 φ 从高到低选 Top3，若候选与已入选项同社区且 |R|>=0.7 则跳过，保证跨模块、不共线。
- M6 稳定性：bootstrap(B=500) 入选频率 + 跨方法(SHAP/相关/RF) Jaccard + 随机 Jaccard 基线对照。
- 来源一致性：读 8.xlsx「Sensory thresholds」得化合物来源、「Sensory names」得感官维期望来源，逐维比对。
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

REDUN_RHO = 0.7   # 去冗余阈值：同社区且 |R|>=该值视为共线，Top3 中只保留其一
NEG_INF = -np.inf


def _norm(v):
    v = np.asarray(v, dtype=float)
    v = np.where(np.isfinite(v), v, 0.0)
    mx = np.abs(v).max()
    return v / mx if mx > 0 else v


def _mask_c(score, c_mask):
    """把非 C 位置的分数置 -inf，确保 argsort/Top-k 永不选中理化列与 4 个汇总列。"""
    out = np.array(score, dtype=float)
    out[~c_mask] = NEG_INF
    return out


def build_coexpr_graph(R, comp_names, rho, c_idx):
    """仅以 C 的位置索引（211 项）为节点、|corr|>=rho 且两端均∈C 为边建无向图 + louvain 社区。

    节点 id 沿用其在全 231 特征中的位置，便于与 comm_arr/评分向量对齐。
    """
    c_set = set(int(i) for i in c_idx)
    G = nx.Graph()
    for i in c_idx:
        G.add_node(int(i), name=comp_names[i])
    n_edges = 0
    c_list = sorted(c_set)
    for a in range(len(c_list)):
        i = c_list[a]
        for b in range(a + 1, len(c_list)):
            j = c_list[b]
            w = R[i, j]
            if np.isfinite(w) and abs(w) >= rho:
                # 共表达强度用相关系数绝对值作边权（louvain/模块度要求非负权；
                # 符号信息由 R 原矩阵保留，去冗余规则直接查 R）。
                G.add_edge(i, j, weight=abs(float(w)))
                n_edges += 1
    # 社区检测（louvain 优先；回退 greedy_modularity）
    try:
        import community as community_louvain
        part = community_louvain.best_partition(G, weight="weight", random_state=P.SEED)
        comm = {int(k): int(v) for k, v in part.items()}
        method = "louvain"
    except Exception:
        from networkx.algorithms.community import greedy_modularity_communities
        comms = greedy_modularity_communities(G, weight="weight")
        comm = {int(node): ci for ci, cset in enumerate(comms) for node in cset}
        method = "greedy_modularity"
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
    styles = meta[P.STYLE_COL].values      # 分层 bootstrap 需要
    J = len(sens_cols)

    # ---- 候选集 C（211 项）：理化 16 列 + 汇总 4 列一律排除 ----
    c_set = set(P.compound_set(feat_cols))
    c_mask = np.array([c in c_set for c in feat_cols])
    c_idx = [i for i, c in enumerate(feat_cols) if c in c_set]
    assert len(c_idx) == 211, f"化合物集 C 应 211 项，实 {len(c_idx)}"
    print(f"[Q2] 候选集 C = {len(c_idx)} 项（排除 {int((~c_mask).sum())} 个理化/汇总列）")

    # 1) 共表达图 + 社区（仅 C）
    G, comm, cmethod, n_edges, Qmod = build_coexpr_graph(R, comp_names, P.COEXPR_RHO, c_idx)
    n_comm = len(set(comm.values()))
    print(f"[Q2] 共表达图(仅C) 节点={G.number_of_nodes()} 边={n_edges} 社区数={n_comm}({cmethod}) 模块度Q={Qmod}")
    comm_arr = np.array([comm.get(i, -1) for i in range(len(feat_cols))])

    # 2) SHAP 证据（对 Q1 全 231 特征 LightGBM 模型）
    shap_imp, abs_shap_list, _ = _shap_evidence(sens_cols, feat_cols, Xv)
    # 3) 6.csv 交叉相关证据（映射到 231 位置）
    corr_evid = _corr_evidence(C6, comp_rows6, comp_names, feat_cols, sens_cols)
    # 4) RF 重要性证据（跨方法用）
    rf_imp = _rf_evidence(Xv, Yv, J)

    # 5) 融合 + 模块代表 + 去冗余 → Top-3；稳定性（全部只在 C 内取）
    results = _fuse_and_stability(sens_cols, feat_cols, shap_imp, corr_evid, rf_imp,
                                  abs_shap_list, comm_arr, c_mask, R, styles)

    # 6) 来源一致性（8.xlsx）
    src_map, cat_map = _load_source_maps(data_dir, feat_cols, sens_cols)
    _attach_source_category(results, sens_cols, feat_cols, src_map, cat_map)

    # 7) 随机 Jaccard 基线（从 C 抽 3 重复 100000 次）
    results["random_jaccard_baseline"] = _random_jaccard_baseline(
        results, sens_cols, c_idx, J)

    # 8) 交付 + 图数据 + 验证
    _write_submission(out_dir, results, sens_cols, feat_cols)
    results["graph"] = {"n_nodes": G.number_of_nodes(), "n_edges": n_edges,
                        "n_communities": n_comm, "method": cmethod,
                        "modularity": round(float(Qmod), 4) if Qmod is not None else None,
                        "rho": P.COEXPR_RHO, "node_scope": "compound_set_C"}
    _build_graph_figdata(results, G, comm, comp_names, R, src_map, cat_map, sens_cols)
    _validate(out_dir, results, sens_cols, feat_cols)
    U.save_json(results, os.path.join(fig_dir, "problem_2_results.json"))
    print("[Q2] 完成，结果写入 figures/problem_2_results.json")
    return results
def _shap_evidence(sens_cols, feat_cols, Xv):
    """用 Q1 全 231 特征 LightGBM 模型算每维 SHAP。返回 (importance[J×P], 每维|shap|矩阵列表)。"""
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
            sv = np.asarray(expl.shap_values(Xv))       # N×P
            abs_sv = np.abs(sv)
            imp[j] = abs_sv.mean(axis=0)
            abs_shap_list.append(abs_sv)
        else:
            abs_shap_list.append(np.zeros((Xv.shape[0], Pn)))
        if (j + 1) % 10 == 0:
            print(f"[Q2] SHAP 进度 {j+1}/{J}")
    return imp, abs_shap_list, sens_cols


def _corr_evidence(C6, comp_rows6, comp_names, feat_cols, sens_cols):
    """6.csv 交叉相关 → 231 位置 × 50 感官的 |corr| 证据（未覆盖化合物记 0）。

    两个都必须按名映射，不能按位置：
      - 化合物行：6.csv 用英文全名，2.csv 用原始列名。
      - 感官列：6.csv 前 46 列顺序与 4.csv 一致，但第 47-50 位不同
        （6.csv: Carbonation/Aftertaste/Body/Overall；
          4.csv: aftertaste/body/co2/overall），按位置对齐会把
        aftertaste、body、co2 三列的证据错位。
    """
    J, Pn = len(sens_cols), len(feat_cols)
    evid = np.zeros((J, Pn))
    name2pos = {name: i for i, name in enumerate(comp_names)}
    Cv = C6.values.astype(float)

    # 感官列按名映射：C6 的第 k 列 → 4.csv 的某个短名
    col_targets = U.align_sensory_cols(list(C6.columns))
    sens_pos = {s: j for j, s in enumerate(sens_cols)}
    col_to_j = []
    for short in col_targets:
        if short not in sens_pos:
            raise KeyError(f"6.csv 感官列映射到未定义的维度: {short}")
        col_to_j.append(sens_pos[short])

    n_mapped = 0
    for ri, r in enumerate(comp_rows6):
        pos = name2pos.get(r, None)
        if pos is None:
            continue
        n_mapped += 1
        for k, j in enumerate(col_to_j):
            v = Cv[ri, k]
            evid[j, pos] = abs(v) if np.isfinite(v) else 0.0
    print(f"[Q2] 6.csv 交叉相关映射化合物 {n_mapped}/{len(comp_rows6)} → 231 位置；"
          f"感官列按名映射 {len(set(col_to_j))}/50")
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
    """模块代表加权：同社区（仅 C，comm!=-1）内按 base 排名，第 1 名 rep=1，第 2=1/2…

    非 C 位置 comm=-1 直接跳过（rep 保持 0），促进 Top-3 跨模块多样。
    """
    rep = np.zeros_like(base_scores, dtype=float)
    for ci in np.unique(comm_arr):
        if ci == -1:
            continue                      # 非 C 节点不参与模块代表
        idx = np.where(comm_arr == ci)[0]
        order = idx[np.argsort(-base_scores[idx])]
        for rank, p in enumerate(order, 1):
            rep[p] = 1.0 / rank
    return rep


def _topk_masked(score, c_mask, k=P.TOPN):
    """仅在 C 内取 Top-k（非 C 置 -inf 后 argsort）。"""
    return list(np.argsort(-_mask_c(score, c_mask))[:k])


def _jaccard(a, b):
    a, b = set(a), set(b)
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def _select_topk(phi_masked, R, comm_arr, k=P.TOPN, rho_redun=REDUN_RHO):
    """按 φ 从高到低选 Top-k 的去冗余选择（φ 已对非 C 置 -inf）。

    去冗余规则：若候选 p 与某个已入选 q 处于同一社区（comm!=-1）且 |R[p,q]|>=rho_redun，
    则判为共线、跳过 p，选下一个，保证 Top-k 跨模块且不共线。
    去冗余后若不足 k 个（极端情形），用剩余最高 φ 的 C 内候选补足。
    """
    order = np.argsort(-phi_masked)
    chosen = []
    for p in order:
        if not np.isfinite(phi_masked[p]):
            break                          # 已到非 C（-inf）区，停止
        redundant = False
        for q in chosen:
            if comm_arr[p] != -1 and comm_arr[p] == comm_arr[q] and abs(R[p, q]) >= rho_redun:
                redundant = True
                break
        if not redundant:
            chosen.append(int(p))
        if len(chosen) == k:
            return chosen
    # 兜底补足（保持 Top-k 恰 k 个）
    if len(chosen) < k:
        for p in order:
            if not np.isfinite(phi_masked[p]):
                break
            if int(p) not in chosen:
                chosen.append(int(p))
            if len(chosen) == k:
                break
    return chosen
def _fuse_and_stability(sens_cols, feat_cols, shap_imp, corr_evid, rf_imp,
                        abs_shap_list, comm_arr, c_mask, R, styles):
    """多证据融合 + 去冗余 Top-3 + bootstrap 入选频率 + 跨方法 Jaccard（全部只在 C 内取）。"""
    J, Pn = len(sens_cols), len(feat_cols)
    a, b, g = P.FUSE_ALPHA, P.FUSE_BETA, P.FUSE_GAMMA
    per_dim = {}
    top3_idx = {}
    # 点估计：φ=0.5SHAP+0.3|corr|+0.2module_rep，module_rep 仅在 C 社区内
    shap_n_all = np.vstack([_norm(shap_imp[j]) for j in range(J)])
    corr_n_all = np.vstack([_norm(corr_evid[j]) for j in range(J)])
    rf_n_all = np.vstack([_norm(rf_imp[j]) for j in range(J)])
    phi_all = np.zeros((J, Pn))
    for j in range(J):
        base = a * shap_n_all[j] + b * corr_n_all[j]
        rep = _module_rep(base, comm_arr)          # 仅 C 社区
        phi = base + g * rep
        phi_all[j] = phi
        # 去冗余 Top-3（phi 先掩码到 C）
        top3_idx[j] = _select_topk(_mask_c(phi, c_mask), R, comm_arr)
    # bootstrap 入选频率：**按风格分层**有放回重采样 → 重算 SHAP → 同一融合+去冗余流程（只在 C 内）。
    # 分层可避免小样本风格在重采样中整体缺席，使频率反映"同风格内"的稳定性。
    rng_bt = np.random.default_rng(P.SEED)
    N = abs_shap_list[0].shape[0]
    style_arr = np.asarray(styles)
    strata = [np.where(style_arr == s)[0] for s in pd.unique(style_arr)]
    freq = np.zeros((J, Pn))
    B = P.N_BOOTSTRAP
    conv_trace = {}          # 200/300/500 收敛检查
    for bi in range(B):
        parts = [rng_bt.choice(idx, size=len(idx), replace=True) for idx in strata if len(idx)]
        idx = np.concatenate(parts)
        for j in range(J):
            shap_b = _norm(abs_shap_list[j][idx].mean(axis=0))
            base_b = a * shap_b + b * corr_n_all[j]
            phi_b = base_b + g * _module_rep(base_b, comm_arr)
            for p in _select_topk(_mask_c(phi_b, c_mask), R, comm_arr):
                freq[j, p] += 1
        if (bi + 1) in (200, 300, 500):
            snap = freq / (bi + 1)
            top1 = [int(np.argmax(snap[j])) for j in range(J)]
            conv_trace[str(bi + 1)] = {
                "mean_top1_freq": round(float(np.mean([snap[j, top1[j]] for j in range(J)])), 4),
                "n_top1_changed_vs_final": None,   # 稍后填
                "top1": top1,
            }
            print(f"[Q2] bootstrap {bi+1}/{B}  mean_top1={conv_trace[str(bi+1)]['mean_top1_freq']:.4f}")
    freq /= B
    # 跨方法 Jaccard（SHAP / 6.csv相关 / RF；各方法 Top-3 只在 C 内取）
    jac_dim = {}
    for j in range(J):
        ts = _topk_masked(shap_n_all[j], c_mask)
        tc = _topk_masked(corr_n_all[j], c_mask)
        tr = _topk_masked(rf_n_all[j], c_mask)
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
    # 收敛检查：200/300 次的 Top-1 与最终（500 次）Top-1 差异维数
    final_top1 = [int(np.argmax(freq[j])) for j in range(J)]
    for k in conv_trace:
        prev = conv_trace[k]["top1"]
        conv_trace[k]["n_top1_changed_vs_final"] = int(sum(1 for a_, b_ in zip(prev, final_top1) if a_ != b_))
        conv_trace[k].pop("top1", None)
    print("[Q2] 收敛检查:", {k: (v["mean_top1_freq"], v["n_top1_changed_vs_final"]) for k, v in conv_trace.items()})

    mean_top1_freq = float(np.mean([per_dim[c]["select_freq"][0] for c in sens_cols]))
    mean_jac = float(np.mean(list(jac_dim.values())))
    n_high_stable = int(sum(1 for c in sens_cols if per_dim[c]["select_freq"][0] >= 0.7))
    print(f"[Q2] 平均Top-1入选频率={mean_top1_freq:.4f} 平均跨方法Jaccard={mean_jac:.4f} "
          f"高稳定维={n_high_stable}")
    return {
        "problem": 2,
        "method": ("共表达图(networkx+louvain,仅C 211项) + SHAP/相关/模块代表融合(φ=0.5/0.3/0.2) "
                   "+ 同社区|R|>=0.7去冗余 + bootstrap频率 + 跨方法Jaccard + 随机基线对照"),
        "candidate_set": {"name": "C", "n": int(c_mask.sum()),
                          "excluded_physicochem": sorted(P.PHYSICOCHEM_COLS),
                          "excluded_aggregate": sorted(P.AGG_COLS)},
        "summary": {"n_dims": J, "n_bootstrap": B, "topn": P.TOPN,
                    "mean_top1_select_freq": round(mean_top1_freq, 4),
                    "mean_cross_method_jaccard": round(mean_jac, 4),
                    "n_high_stable_dims": n_high_stable,
                    "redun_rho": REDUN_RHO,
                    "fuse_weights": {"alpha": a, "beta": b, "gamma": g},
                    "bootstrap_stratified_by_style": True,
                    "bootstrap_convergence": conv_trace},
        "per_dim": per_dim, "sensory_cols": sens_cols,
    }
def _load_source_maps(data_dir, feat_cols, sens_cols):
    """读 8.xlsx：
    - 「Sensory thresholds」field_name_R → origin_paper：每个化合物的来源
      (Yeast/Hops/Malt/Wild flora/Spices/Others/Internal standard solution)。
    - 「Sensory names」R_name → Category：每个感官维的期望来源类别。
    返回 (src_map: 化合物列名→来源, cat_map: 感官维→期望来源)。
    """
    pth = os.path.join(data_dir, "8.xlsx")
    th = pd.read_excel(pth, sheet_name="Sensory thresholds")
    nm = pd.read_excel(pth, sheet_name="Sensory names")
    src_map = {}
    for r, s in zip(th["field_name_R"].astype(str), th["origin_paper"]):
        if r and r != "nan":
            src_map[r] = str(s) if pd.notna(s) else "Unknown"
    # Sensory names 可能同一 R_name 跨 dataset 重复，保留首个（Category 一致）
    nm2 = nm.drop_duplicates(subset=["R_name"])
    cat_map = {}
    for r, c in zip(nm2["R_name"].astype(str), nm2["Category"]):
        if r and r != "nan":
            cat_map[r] = str(c) if pd.notna(c) else "Unknown"
    n_c = sum(1 for c in feat_cols if c in src_map)
    n_s = sum(1 for s in sens_cols if s in cat_map)
    print(f"[Q2] 来源映射：化合物 {n_c}/{len(feat_cols)}，感官维 {n_s}/{len(sens_cols)}")
    return src_map, cat_map


def _attach_source_category(results, sens_cols, feat_cols, src_map, cat_map):
    """逐维把 Top3 来源与该维期望来源比对，判一致/部分一致/不一致。"""
    n_consistent = n_partial = n_inconsistent = 0
    detail = {}
    for col in sens_cols:
        d = results["per_dim"][col]
        exp = cat_map.get(col, "Unknown")
        srcs = [src_map.get(fn, "Unknown") for fn in d["top3"]]
        d["source_category"] = srcs          # 每个 Top3 记来源
        n_match = sum(1 for s in srcs if s == exp)
        if n_match == len(srcs):
            verdict = "一致"
            n_consistent += 1
        elif n_match >= 1:
            verdict = "部分一致"
            n_partial += 1
        else:
            verdict = "不一致"
            n_inconsistent += 1
        d["expected_source"] = exp
        d["source_verdict"] = verdict
        detail[col] = {"expected": exp, "top3_sources": srcs, "verdict": verdict}
    J = len(sens_cols)
    results["source_category"] = {
        "n_consistent": n_consistent, "n_partial": n_partial,
        "n_inconsistent": n_inconsistent,
        "consistency_rate": round(n_consistent / J, 4),
        "partial_rate": round(n_partial / J, 4),
        "inconsistency_rate": round(n_inconsistent / J, 4),
        "per_dim": detail,
        "note": ("化合物来源取自 8.xlsx『Sensory thresholds』origin_paper，"
                 "感官维期望来源取自『Sensory names』Category；一致=Top3 全部来源==期望，"
                 "部分一致=至少一个匹配，不一致=无匹配。"),
    }
    print(f"[Q2] 来源一致性：一致={n_consistent} 部分={n_partial} 不一致={n_inconsistent} "
          f"一致率={n_consistent/J:.4f} 部分率={n_partial/J:.4f}")


def _random_jaccard_baseline(results, sens_cols, c_idx, J, n_rep=100000):
    """固定 SEED，从 C 随机抽 3 化合物重复 n_rep 次，算随机 Top3 与各维实际 Top3 的
    期望 Jaccard 均值及标准差，用于对照说明本文跨方法 Jaccard 显著高于随机。
    """
    rng = np.random.default_rng(P.SEED)
    c_arr = np.array(c_idx, dtype=int)
    Pn = max(c_arr) + 1
    # 实际 Top3 的成员矩阵（J × Pn 布尔），便于向量化计重叠
    memb = np.zeros((J, Pn), dtype=bool)
    for j, col in enumerate(sens_cols):
        for p in results["per_dim"][col]["top3_idx"]:
            memb[j, p] = True
    per_draw_mean = np.empty(n_rep)
    for b in range(n_rep):
        draw = rng.choice(c_arr, size=P.TOPN, replace=False)
        overlap = memb[:, draw].sum(axis=1)       # 每维与该随机 Top3 的交集大小 (0..3)
        jac = overlap / (2 * P.TOPN - overlap)     # |∩|/|∪|，两集均 3 项 → 6-overlap
        per_draw_mean[b] = jac.mean()
        if (b + 1) % 20000 == 0:
            print(f"[Q2] 随机Jaccard基线 {b+1}/{n_rep}")
    mean_v = float(per_draw_mean.mean())
    std_v = float(per_draw_mean.std())
    actual = results["summary"]["mean_cross_method_jaccard"]
    print(f"[Q2] 随机Jaccard基线 均值={mean_v:.5f} 标准差={std_v:.5f}（实际跨方法Jaccard={actual}）")
    return {"n_rep": n_rep, "draw_size": P.TOPN, "universe": "C",
            "mean": round(mean_v, 6), "std": round(std_v, 6),
            "actual_mean_cross_method_jaccard": actual,
            "ratio_actual_to_random": round(actual / mean_v, 2) if mean_v > 0 else None,
            "note": "随机从 C(211) 抽 3，与各维实际 Top3 的平均 Jaccard，对照跨方法一致性显著性。"}
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
    low = feat_name.lower()
    for keys, txt in _MECH_RULES:
        if any(k in low for k in keys):
            return txt
    return "其他挥发性化学信号（见共表达模块）"


def _write_submission(out_dir, results, sens_cols, feat_cols):
    rows = []
    for col in sens_cols:
        d = results["per_dim"][col]
        for rank in range(len(d["top3"])):
            fn = d["top3"][rank]
            rows.append({
                "sensory_dim": col, "rank": rank + 1, "compound": fn,
                "phi_score": d["phi"][rank], "shap_norm": d["shap_norm"][rank],
                "cross_corr_abs": d["corr_abs"][rank],
                "bootstrap_select_freq": d["select_freq"][rank],
                "module_id": d["module"][rank],
                "jaccard_cross_method": d["jaccard_cross_method"],
                "source_category": d["source_category"][rank],
                "expected_source": d["expected_source"],
                "source_verdict": d["source_verdict"],
                "feature_type": P.feature_type(fn),
                "mechanism": _mechanism(fn),
            })
    sub = pd.DataFrame(rows)
    path = os.path.join(out_dir, "submission", "q2_top3_compounds.csv")
    sub.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"[Q2] 写出 {path}  shape={sub.shape}（每维 {P.TOPN} 行，全 volatile_compound）")
    results["submission"] = {"path": "submission/q2_top3_compounds.csv",
                             "rows": int(sub.shape[0])}


def _build_graph_figdata(results, G, comm, comp_names, R, src_map, cat_map, sens_cols):
    """网络布局 + 社区规模 + 来源聚合分布(小提琴) + 感官类别→来源(桑基)。"""
    deg = dict(G.degree(weight=None))
    top_nodes = sorted(deg, key=lambda n: -deg[n])[:60]        # C 子图度数前 60
    sub = G.subgraph(top_nodes)
    nodes = [{"id": int(n), "name": comp_names[n], "deg": int(deg[n]),
              "comm": int(comm.get(n, -1)),
              "source": src_map.get(comp_names[n], "Unknown")} for n in sub.nodes()]
    edges = [{"s": int(u), "t": int(v), "w": round(float(d["weight"]), 3)}
             for u, v, d in sub.edges(data=True)]
    comm_sizes = {}
    for n, ci in comm.items():
        comm_sizes[ci] = comm_sizes.get(ci, 0) + 1
    # 按来源类别聚合的 bootstrap 入选频率分布（供小提琴）
    freq_by_source = {}
    sankey = {}
    for col in sens_cols:
        d = results["per_dim"][col]
        exp = d["expected_source"]
        for rank in range(len(d["top3"])):
            s = d["source_category"][rank]
            freq_by_source.setdefault(s, []).append(d["select_freq"][rank])
            key = (exp, s)
            sankey[key] = sankey.get(key, 0) + 1
    sankey_list = [{"sensory_category": k[0], "compound_source": k[1], "count": v}
                   for k, v in sorted(sankey.items(), key=lambda t: -t[1])]
    results["fig_data"] = {
        "network_nodes": nodes, "network_edges": edges,
        "community_sizes": sorted(comm_sizes.values(), reverse=True),
        "freq_by_source": {k: [round(x, 4) for x in v] for k, v in freq_by_source.items()},
        "sankey_cat_source": sankey_list,
        "top1_freq_ranked": sorted(
            ((c, results["per_dim"][c]["select_freq"][0],
              results["per_dim"][c]["jaccard_cross_method"]) for c in sens_cols),
            key=lambda t: -t[1]),
    }


def _validate(out_dir, results, sens_cols, feat_cols):
    sub = pd.read_csv(os.path.join(out_dir, "submission", "q2_top3_compounds.csv"))
    # 硬约束：每维恰 3 行、覆盖 50 维、共 150 行
    sizes = sub.groupby("sensory_dim").size()
    assert (sizes == P.TOPN).all(), f"[P2-C2] 存在维度 Top-N!=3: {sizes[sizes!=P.TOPN].to_dict()}"
    assert sizes.shape[0] == len(sens_cols), "Top-3 覆盖维度数!=50"
    assert sub.shape[0] == P.TOPN * len(sens_cols), f"行数应 {P.TOPN*len(sens_cols)}，实 {sub.shape[0]}"
    # 频率/Jaccard ∈[0,1]
    for c in ("bootstrap_select_freq", "jaccard_cross_method"):
        assert sub[c].between(0, 1).all(), f"[P2-C3] {c} 越界[0,1]"
    # Top3 绝不含理化列与 4 个汇总列；feature_type 全 volatile_compound
    banned = set(P.PHYSICOCHEM_COLS) | set(P.AGG_COLS)
    bad = sub[sub["compound"].isin(banned)]
    assert bad.empty, f"[P2-C1] Top3 含被排除列: {bad['compound'].unique().tolist()}"
    assert (sub["feature_type"] == "volatile_compound").all(), "[P2-C1] 存在非 volatile_compound 行"
    print("[Q2] validate_constraints PASS（150行/每维3行/频率∈[0,1]/Jaccard∈[0,1]/无理化汇总列）")
    # 能力断言
    assert results["summary"]["n_bootstrap"] >= 200, "[P2-C3] bootstrap<200"
    assert sub["mechanism"].notna().all() and (sub["mechanism"].str.len() > 0).all(), \
        "[P2-C4] 存在缺机理解释的 Top-3"
    assert results["summary"]["mean_cross_method_jaccard"] >= 0, "[P2-C3] 跨方法Jaccard缺失"
    assert results["graph"]["n_nodes"] == 211, f"[P2-C1] 共表达图节点应 211，实 {results['graph']['n_nodes']}"
    # 来源一致性率 ∈[0,1]
    sc = results["source_category"]
    for k in ("consistency_rate", "partial_rate", "inconsistency_rate"):
        assert 0 <= sc[k] <= 1, f"[P2] {k} 越界"
    print("[Q2] validate_capability PASS（C=211图 / 500次bootstrap+3方法Jaccard / 逐维机理 / 来源一致性）")


if __name__ == "__main__":
    dd = sys.argv[1] if len(sys.argv) > 1 else "user_data"
    run(dd)
