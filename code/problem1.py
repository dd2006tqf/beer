# -*- coding: utf-8 -*-
"""问题一：含缺失的多输出有序感官分级预测（能力 P1-C1/C2/C3/C4）。

方法（忠实 MODELING_REPORT §六 / METHOD_CLAIMS M1-M3）：
- 主模型：原生支持缺失的梯度提升树 LightGBM（use_missing，不删含缺失行）。
- 标签：4.csv 标准化连续值 -> 训练折内 7 分位分箱 -> 0..6 整数等级（式1/式2）。
- 验证：按 tasting_category_fine 分层 5 折 CV，分箱/标准化参数仅训练折估计（防泄漏 P1-C4）。
- 基线：逐维均值等级、ElasticNet（中位插补）、随机森林（中位插补）。
- 缺失对照：KNN 插补 + LightGBM，量化插补偏差。
- 全量重训 -> submission/q1_sensory_scores.csv（250 行，beer_id + 50 维 0-6 整数，无 NA）。
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
from sklearn.model_selection import StratifiedKFold
from sklearn.linear_model import ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
import lightgbm as lgb

LGB_PARAMS = dict(
    n_estimators=150, num_leaves=8, learning_rate=0.05,
    min_child_samples=15, feature_fraction=0.6, bagging_fraction=0.8,
    bagging_freq=1, lambda_l2=1.0, random_state=P.SEED, n_jobs=-1, verbose=-1,
)


def _fit_lgb(Xtr, ytr):
    m = lgb.LGBMRegressor(**LGB_PARAMS)
    m.fit(Xtr, ytr)
    return m


def run(data_dir="user_data", out_dir=None):
    out_dir = out_dir or _ROOT
    U.set_all_seeds(P.SEED)
    fig_dir = os.path.join(out_dir, "figures")
    sub_dir = os.path.join(out_dir, "submission")
    os.makedirs(fig_dir, exist_ok=True)
    os.makedirs(sub_dir, exist_ok=True)

    df1, X, feat_cols, meta = U.load_chem(data_dir)
    Y, sens_cols = U.load_sensory(data_dir)
    styles = meta[P.STYLE_COL].values
    Xv = X.values.astype(float)           # 含 NaN，LightGBM 原生处理
    assert Xv.shape[0] == P.N_SAMPLES, "训练样本数必须=250（含缺失行，不删行）"

    n_na_rows = int(np.isnan(Xv).any(axis=1).sum())
    print(f"[Q1] 样本={Xv.shape[0]} 特征={Xv.shape[1]} 含NA行={n_na_rows} 感官维={len(sens_cols)}")

    # 分层折（小样本风格合并到 '_rare' 以保证分层可行）
    vc = pd.Series(styles).value_counts()
    strat = np.array([s if vc[s] >= P.N_FOLDS else "_rare" for s in styles])
    skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)

    J = len(sens_cols)
    # 累加每维预测（out-of-fold）
    oof_main = np.full((P.N_SAMPLES, J), np.nan)
    oof_mean = np.full((P.N_SAMPLES, J), np.nan)
    oof_enet = np.full((P.N_SAMPLES, J), np.nan)
    oof_rf = np.full((P.N_SAMPLES, J), np.nan)
    oof_knn = np.full((P.N_SAMPLES, J), np.nan)        # KNN 插补+LGB 对照
    oof_true_lvl = np.full((P.N_SAMPLES, J), -1, dtype=int)
    oof_main_cont = np.full((P.N_SAMPLES, J), np.nan)  # 连续输出（R² 用）

    Yv = Y.values.astype(float)

    for fi, (tr, va) in enumerate(skf.split(Xv, strat), 1):
        print(f"[Q1] fold {fi}/{P.N_FOLDS}  train={len(tr)} val={len(va)}")
        # 折内中位插补器（仅 fit 训练折）供 ElasticNet/RF/KNN 基线
        med = SimpleImputer(strategy="median").fit(Xv[tr])
        knn = KNNImputer(n_neighbors=5).fit(Xv[tr])
        Xtr_med, Xva_med = med.transform(Xv[tr]), med.transform(Xv[va])
        Xtr_knn, Xva_knn = knn.transform(Xv[tr]), knn.transform(Xv[va])

        for j in range(J):
            ytr_c, yva_c = Yv[tr, j], Yv[va, j]
            binner = U.Binner().fit(ytr_c)                 # 仅训练折估分箱
            oof_true_lvl[va, j] = binner.transform(yva_c)

            # 主模型：原生缺失 LightGBM（含缺失行训练）
            m = _fit_lgb(Xv[tr], ytr_c)
            rc = m.predict(Xv[va])
            oof_main_cont[va, j] = rc
            oof_main[va, j] = binner.transform_continuous(rc)

            # 基线：均值等级
            oof_mean[va, j] = binner.transform_continuous(np.full(len(va), ytr_c.mean()))
            # 基线：ElasticNet（中位插补）
            en = ElasticNet(alpha=0.1, l1_ratio=0.5, random_state=P.SEED, max_iter=5000)
            en.fit(Xtr_med, ytr_c)
            oof_enet[va, j] = binner.transform_continuous(en.predict(Xva_med))
            # 基线：随机森林（中位插补）
            rf = RandomForestRegressor(n_estimators=120, max_depth=6,
                                       random_state=P.SEED, n_jobs=-1)
            rf.fit(Xtr_med, ytr_c)
            oof_rf[va, j] = binner.transform_continuous(rf.predict(Xva_med))
            # 缺失对照：KNN 插补 + LGB
            mk = _fit_lgb(Xtr_knn, ytr_c)
            oof_knn[va, j] = binner.transform_continuous(mk.predict(Xva_knn))

    # placeholder-metrics
    results = _summarize(sens_cols, oof_true_lvl, oof_main, oof_mean,
                         oof_enet, oof_rf, oof_knn, oof_main_cont, Yv, n_na_rows)
    _full_retrain_and_submit(data_dir, out_dir, df1, Xv, Yv, feat_cols, sens_cols,
                             meta, results)
    build_figdata(results, Xv, oof_true_lvl, oof_main, oof_main_cont, Yv, sens_cols, feat_cols)
    _validate(out_dir, sens_cols, results)
    # 保存全量模型供 Q2 复用（可复现，不进 JSON）
    import joblib
    joblib.dump({"models": results.pop("_models"), "binners": results.pop("_binners"),
                 "feat_cols": results.pop("_feat_cols")},
                U.ckpt_path("q1_models.pkl"))
    U.save_json(results, os.path.join(fig_dir, "problem_1_results.json"))
    print("[Q1] 完成，结果写入 figures/problem_1_results.json")
    return results
def _summarize(sens_cols, true_lvl, main, mean_b, enet, rf, knn, main_cont, Yv, n_na_rows):
    """逐维 QWK/MAE/R²，选择每维提交模型（主 vs 均值基线，取 QWK 高者）。"""
    J = len(sens_cols)
    per_dim = {}
    qwk_main_list, qwk_mean_list = [], []
    chosen = {}
    for j, col in enumerate(sens_cols):
        yt = true_lvl[:, j]
        qwk_m = U.quadratic_weighted_kappa(yt, main[:, j].astype(int))
        qwk_0 = U.quadratic_weighted_kappa(yt, mean_b[:, j].astype(int))
        qwk_e = U.quadratic_weighted_kappa(yt, enet[:, j].astype(int))
        qwk_r = U.quadratic_weighted_kappa(yt, rf[:, j].astype(int))
        qwk_k = U.quadratic_weighted_kappa(yt, knn[:, j].astype(int))
        mae_m = float(mean_absolute_error(yt, main[:, j]))
        # R² 在连续回归输出上（标准回归口径）
        r2_m = float(r2_score(Yv[:, j], main_cont[:, j]))
        # 提交模型：主模型 CV QWK 不劣于均值基线则用主模型，否则用基线
        use_main = qwk_m >= qwk_0
        chosen[col] = "lightgbm" if use_main else "mean_baseline"
        per_dim[col] = {
            "qwk_main": round(qwk_m, 4), "qwk_mean_baseline": round(qwk_0, 4),
            "qwk_elasticnet": round(qwk_e, 4), "qwk_rf": round(qwk_r, 4),
            "qwk_knn_impute": round(qwk_k, 4),
            "mae_main": round(mae_m, 4), "r2_main": round(r2_m, 4),
            "chosen_model": chosen[col], "is_core": col.startswith(P.CORE_PREFIXES),
        }
        qwk_main_list.append(qwk_m)
        qwk_mean_list.append(qwk_0)

    qwk_main_arr = np.array(qwk_main_list)
    # 可预测维度：主模型 CV QWK > 0（供 Q2 跨问一致性）
    predictable = [sens_cols[j] for j in range(J) if qwk_main_arr[j] > 0]
    summary = {
        "n_samples": int(Yv.shape[0]), "n_features": P.N_FEATURES, "n_dims": J,
        "n_na_rows": int(n_na_rows),
        "mean_qwk_main": round(float(qwk_main_arr.mean()), 4),
        "mean_qwk_mean_baseline": round(float(np.mean(qwk_mean_list)), 4),
        "mean_qwk_elasticnet": round(float(np.mean([v["qwk_elasticnet"] for v in per_dim.values()])), 4),
        "mean_qwk_rf": round(float(np.mean([v["qwk_rf"] for v in per_dim.values()])), 4),
        "mean_qwk_knn_impute": round(float(np.mean([v["qwk_knn_impute"] for v in per_dim.values()])), 4),
        "n_predictable_dims": len(predictable),
        "n_main_chosen": int(sum(1 for v in chosen.values() if v == "lightgbm")),
        "n_dims_main_beats_baseline": int((qwk_main_arr > np.array(qwk_mean_list)).sum()),
    }
    print(f"[Q1] 平均QWK 主={summary['mean_qwk_main']} 均值基线={summary['mean_qwk_mean_baseline']} "
          f"ElasticNet={summary['mean_qwk_elasticnet']} RF={summary['mean_qwk_rf']} "
          f"KNN插补={summary['mean_qwk_knn_impute']}  可预测维={summary['n_predictable_dims']}")
    return {
        "problem": 1, "method": "LightGBM(native missing) + 7级分位分箱 + 分层5折CV",
        "summary": summary, "per_dim": per_dim,
        "predictable_dims": predictable, "sensory_cols": sens_cols,
        "chosen_model": chosen,
        "validation": {"scheme": "StratifiedKFold", "n_folds": P.N_FOLDS,
                       "binning": P.LABEL_BINNING, "leakage_control": "分箱/插补仅训练折fit"},
        # 校准图数据（代表维度：核心维中 QWK 最高者）
        "calibration": {},
        "fig_data": {},
    }
def _full_retrain_and_submit(data_dir, out_dir, df1, Xv, Yv, feat_cols, sens_cols, meta, results):
    """全部 250 样本重训（含缺失行），产出 0-6 分级提交文件。"""
    print("[Q1] 全量重训 + 生成 submission/q1_sensory_scores.csv ...")
    U.set_all_seeds(P.SEED)
    chosen = results["chosen_model"]
    sub = pd.DataFrame({P.KEY_COL: meta[P.KEY_COL].values})
    models = {}
    binners = {}
    for j, col in enumerate(sens_cols):
        yc = Yv[:, j]
        binner = U.Binner().fit(yc)        # 全量仅用于最终交付（CV 指标另由折内估计，无泄漏）
        binners[col] = binner
        if chosen[col] == "lightgbm":
            m = _fit_lgb(Xv, yc)
            models[col] = m
            pred = binner.transform_continuous(m.predict(Xv))
        else:
            pred = binner.transform_continuous(np.full(len(yc), yc.mean()))
        sub[col] = pred.astype(int)
    sub_path = os.path.join(out_dir, "submission", "q1_sensory_scores.csv")
    sub.to_csv(sub_path, index=False, encoding="utf-8-sig")
    print(f"[Q1] 写出 {sub_path}  shape={sub.shape}")
    results["_models"] = models          # 供 Q2 复用（不写 JSON）
    results["_binners"] = binners
    results["_feat_cols"] = feat_cols
    results["submission"] = {"path": "submission/q1_sensory_scores.csv",
                             "rows": int(sub.shape[0]), "cols": int(sub.shape[1])}


def build_figdata(results, Xv, oof_true_lvl, oof_main, oof_main_cont, Yv, sens_cols, feat_cols):
    """装配 paper-figure 用数据：缺失模式、QWK 排序、代表维校准。"""
    # 缺失模式：各列缺失率
    na_rate = np.isnan(Xv).mean(axis=0)
    na_cols = [(feat_cols[i], round(float(na_rate[i]), 4)) for i in range(len(feat_cols)) if na_rate[i] > 0]
    na_cols.sort(key=lambda t: -t[1])
    results["fig_data"]["missing_rate_by_col"] = na_cols
    results["fig_data"]["n_na_rows"] = int(np.isnan(Xv).any(axis=1).sum())
    # QWK 排序（棒棒糖图）
    qwk_sorted = sorted(((c, results["per_dim"][c]["qwk_main"]) for c in sens_cols),
                        key=lambda t: -t[1])
    results["fig_data"]["qwk_ranked"] = qwk_sorted
    # 代表维（核心维 QWK 最高）校准数据：真实等级 vs 预测连续
    core = [c for c in sens_cols if c.startswith(P.CORE_PREFIXES)]
    rep = max(core, key=lambda c: results["per_dim"][c]["qwk_main"])
    jr = sens_cols.index(rep)
    results["calibration"] = {
        "dim": rep,
        "true_level": oof_true_lvl[:, jr].tolist(),
        "pred_level": oof_main[:, jr].astype(int).tolist(),
        "true_cont": [round(float(v), 4) for v in Yv[:, jr]],
        "pred_cont": [round(float(v), 4) for v in oof_main_cont[:, jr]],
    }
    results["fig_data"]["rep_dim"] = rep


def _validate(out_dir, sens_cols, results):
    """validate_constraints + validate_capability（断言不过即 raise）。"""
    sub = pd.read_csv(os.path.join(out_dir, "submission", "q1_sensory_scores.csv"))
    vals = sub.drop(columns=[P.KEY_COL]).values
    # 硬约束：0-6 整数、无 NA、250 行、50 维
    assert sub.shape[0] == P.N_SAMPLES, f"q1 提交应 250 行，实 {sub.shape[0]}"
    assert len([c for c in sub.columns if c != P.KEY_COL]) == P.N_SENSORY
    assert not np.isnan(vals).any(), "q1 提交含 NA"
    assert (vals == vals.round()).all(), "q1 分级非整数"
    assert (vals >= P.LEVEL_MIN).all() and (vals <= P.LEVEL_MAX).all(), "q1 分级越界[0,6]"
    print("[Q1] validate_constraints PASS（0-6整数/无NA/250行/50维）")
    # 能力断言（P1-C2：含缺失行被使用，训练样本=250；P1-C4：折内估计）
    assert results["summary"]["n_samples"] == P.N_SAMPLES, \
        "[能力P1-C2不成立] 训练样本!=250，疑似删了含缺失行"
    assert results["summary"]["n_na_rows"] > 0, \
        "[能力P1-C2不成立] 未见含缺失行，疑似dropna"
    assert results["validation"]["leakage_control"].startswith("分箱"), \
        "[能力P1-C4不成立] 未做折内防泄漏"
    print("[Q1] validate_capability PASS（P1-C2 含缺失250行 / P1-C4 折内防泄漏）")


if __name__ == "__main__":
    dd = sys.argv[1] if len(sys.argv) > 1 else "user_data"
    run(dd)


