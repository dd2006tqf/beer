# -*- coding: utf-8 -*-
"""supp_preprocess_eda.py — 数据预处理章节 EDA（只读 user_data，输出 supp_preprocess.json）。
覆盖任务书 §2：
  1) 附件概况（8 附件 sheet/行×列/用途，实测）
  2) 题面 vs 实测差异所需的实测数字
  3) 231 化学指标三分类（理化/汇总/化合物集 C）
  4) 对数底核实：用 8.xlsx「Calibrated chemical dataset」逐样本校准绝对浓度，
     在 c>0 样本上比较 1.csv 取值 x 与 log10(c)/c/ln(c) 的中位残差，判定常用对数/原值/自然对数
  5) 未检出（≤列下限）vs 真正缺失（NA）区分；指示变量适用列（未检出比例 5%–95%）
  6) 四联图 / 缺失模式图所需数据
不改任何上游结果，不重跑求解模型。
"""
import json, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UD = os.path.join(ROOT, "user_data")
import sys
sys.path.insert(0, os.path.join(ROOT, "code"))
import params as P

out = {}

# ---------- 1) 附件概况 ----------
def csv_shape(fn):
    d = pd.read_csv(os.path.join(UD, fn))
    return d, {"rows": int(d.shape[0]), "cols": int(d.shape[1])}

df1, sh1 = csv_shape("1.csv")
df2, sh2 = csv_shape("2.csv")
df4, sh4 = csv_shape("4.csv")
df5, sh5 = csv_shape("5.csv")
df6, sh6 = csv_shape("6.csv")
df7, sh7 = csv_shape("7.csv")

xl3 = pd.ExcelFile(os.path.join(UD, "3.xlsx"))
xl8 = pd.ExcelFile(os.path.join(UD, "8.xlsx"))
sh3 = {s: list(pd.read_excel(os.path.join(UD, "3.xlsx"), sheet_name=s).shape) for s in xl3.sheet_names}
sh8 = {s: list(pd.read_excel(os.path.join(UD, "8.xlsx"), sheet_name=s).shape) for s in xl8.sheet_names}

out["attachment_overview"] = {
    "1.csv": {"rows": sh1["rows"], "cols": sh1["cols"], "content": "化学组成谱（含风格）"},
    "2.csv": {"rows": sh2["rows"], "cols": sh2["cols"], "content": "化合物相关系数矩阵（标称 Pearson）"},
    "3.xlsx": {"n_sheets": len(xl3.sheet_names), "sheets": xl3.sheet_names,
               "shapes": sh3, "content": "12 张空白评分卡 + 1 个 summary（Q1 填分模板）"},
    "4.csv": {"rows": sh4["rows"], "cols": sh4["cols"], "content": "品评标准化分（小组 0–6 等级）"},
    "5.csv": {"rows": sh5["rows"], "cols": sh5["cols"], "content": "感官维之间相关"},
    "6.csv": {"rows": sh6["rows"], "cols": sh6["cols"], "content": "化学-感官相关（化学行 × 感官列）"},
    "7.csv": {"rows": sh7["rows"], "cols": sh7["cols"], "content": "论坛/评论文本属性"},
    "8.xlsx": {"n_sheets": len(xl8.sheet_names), "sheets": xl8.sheet_names,
               "shapes": sh8, "content": "参考表（阈值/校准浓度/MDI/SHAP/价格）"},
}

# 附件7 全缺失列
allna7 = [c for c in df7.columns if df7[c].isna().all()]
out["attachment7"] = {"rows": sh7["rows"], "cols": sh7["cols"],
                      "n_all_missing_cols": len(allna7), "all_missing_cols": allna7[:50]}

# ---------- 3) 231 化学指标三分类 ----------
meta = P.META_COLS
chem_cols = [c for c in df1.columns if c not in meta]
phys = [c for c in chem_cols if c in P.PHYSICOCHEM_COLS]
agg = [c for c in chem_cols if c in P.AGG_COLS]
compC = [c for c in chem_cols if c not in P.PHYSICOCHEM_COLS and c not in P.AGG_COLS]
out["three_class"] = {"n_total": len(chem_cols),
                      "physicochemical": sorted(phys), "n_physicochemical": len(phys),
                      "aggregate": sorted(agg), "n_aggregate": len(agg),
                      "compound_C": sorted(compC), "n_compound_C": len(compC)}

# ---------- 4) 对数底核实：Calibrated chemical dataset ----------
cal = pd.read_excel(os.path.join(UD, "8.xlsx"), sheet_name="Calibrated chemical dataset")
thr = pd.read_excel(os.path.join(UD, "8.xlsx"), sheet_name="Sensory thresholds")
m = df1.merge(cal, on="beer_id", suffixes=("", "_cal"))
per_col = {}
for c in cal.columns:
    if c in ("beer", "beer_id", "tasting_category_fine"):
        continue
    if c not in df1.columns:
        continue
    x = pd.to_numeric(df1.set_index("beer_id").reindex(cal["beer_id"])[c], errors="coerce").values \
        if False else None
    # 按 beer_id 对齐取值
    xmap = df1.set_index("beer_id")[c]
    x = pd.to_numeric(cal["beer_id"].map(xmap), errors="coerce").values.astype(float)
    cv = pd.to_numeric(cal[c], errors="coerce").values.astype(float)
    pos = (cv > 0) & np.isfinite(cv) & np.isfinite(x)
    if pos.sum() < 5:
        per_col[c] = {"verdict": "insufficient_positive", "n_positive": int(pos.sum())}
        continue
    lg = np.log10(cv[pos]); ln = np.log(cv[pos]); xx = x[pos]
    r_log10 = float(np.median(np.abs(xx - lg)))
    r_raw = float(np.median(np.abs(xx - cv[pos])))
    r_ln = float(np.median(np.abs(xx - ln)))
    if r_log10 < 1e-6:
        verdict = "log10"
    elif r_raw < 1e-6:
        verdict = "raw"
    else:
        verdict = "log10" if r_log10 <= r_raw else "raw"
        verdict = verdict + "_approx"
    # 相关旁证
    corr_log = float(np.corrcoef(xx, lg)[0, 1]) if xx.std() > 0 and lg.std() > 0 else None
    per_col[c] = {"verdict": verdict, "n_positive": int(pos.sum()),
                  "median_abs_res_log10": round(r_log10, 5),
                  "median_abs_res_raw": round(r_raw, 5),
                  "median_abs_res_ln": round(r_ln, 5),
                  "corr_x_log10c": round(corr_log, 4) if corr_log is not None else None}
counts = {}
for v in per_col.values():
    counts[v["verdict"]] = counts.get(v["verdict"], 0) + 1
strict_log10 = [c for c, v in per_col.items() if v["verdict"] == "log10"]
strict_raw = [c for c, v in per_col.items() if v["verdict"] == "raw"]
approx_log10 = [c for c, v in per_col.items() if v["verdict"] == "log10_approx"]
approx_raw = [c for c, v in per_col.items() if v["verdict"] == "raw_approx"]
out["log_base_audit"] = {
    "n_audited_cols": len(per_col),
    "counts": counts,
    "strict_log10": strict_log10,
    "strict_raw": strict_raw,
    "approx_log10": approx_log10,
    "approx_raw": approx_raw,
    "per_col": per_col,
    "calibrated_threshold_sheet": {
        "n_rows": int(thr.shape[0]),
        "calibrated_values": [str(x) for x in thr["calibrated"].dropna().unique().tolist()],
        "origin_counts": {str(k): int(v) for k, v in thr["origin_paper"].value_counts().items()},
    },
}

# 散点数据（代表化合物 + 代表理化，c>0 采样）
demo_compounds = ["DMS", "acetaldehyde", "ethyl_acetate", "X4VG", "X.E..2.nonenal", "X2.3.butanedione"]
demo_phys = ["pH", "color.EBC.", "bitterness", "ethanol..v.v.", "SO2.mg.L.", "lactic_acid.mg.L."]
scatter = {}
for c in demo_compounds + demo_phys:
    if c not in df1.columns or c not in cal.columns:
        continue
    xmap = df1.set_index("beer_id")[c]
    x = pd.to_numeric(cal["beer_id"].map(xmap), errors="coerce").values.astype(float)
    cv = pd.to_numeric(cal[c], errors="coerce").values.astype(float)
    pos = (cv > 0) & np.isfinite(cv) & np.isfinite(x)
    idx = np.where(pos)[0]
    if len(idx) > 60:
        rng = np.random.default_rng(P.SEED); idx = rng.choice(idx, 60, replace=False)
    scatter[c] = {"x_in_1csv": [round(float(x[i]), 4) for i in idx],
                  "log10_c": [round(float(np.log10(cv[i])), 4) for i in idx],
                  "c_raw": [round(float(cv[i]), 5) for i in idx]}
out["log_base_audit"]["scatter"] = scatter

# ---------- 5) 未检出 vs 真正缺失 ----------
chem_num = df1[chem_cols].apply(pd.to_numeric, errors="coerce")
na_mask = chem_num.isna()
na_by_col = {c: int(na_mask[c].sum()) for c in chem_cols if int(na_mask[c].sum()) > 0}
na_total = int(na_mask.values.sum())
# 未检出：取列内最小值（检出限编码/半下限），统计等于最小值的比例
below = {}
for c in chem_cols:
    v = chem_num[c].dropna().values
    if len(v) < 10:
        continue
    lod = np.min(v)
    rate = float(np.mean(np.abs(v - lod) < 1e-9))
    below[c] = {"lod": round(float(lod), 4), "min_rate": round(rate, 4)}
indicator_cols = [c for c, b in below.items() if 0.05 <= b["min_rate"] <= 0.95]
# 三组（理化/汇总/化合物）检出/未检出/缺失占比
def group_stats(cols):
    n = len(cols)
    cell_tot = 0; na_cnt = 0; lod_cnt = 0
    for c in cols:
        v = chem_num[c]
        cell_tot += len(v)
        na_cnt += int(v.isna().sum())
        vv = v.dropna().values
        if len(vv):
            lod = np.min(vv); lod_cnt += int(np.sum(np.abs(vv - lod) < 1e-9))
    det = cell_tot - na_cnt - lod_cnt
    return {"detected": round(det / cell_tot, 4), "below_lod": round(lod_cnt / cell_tot, 4),
            "missing": round(na_cnt / cell_tot, 4), "n_cells": int(cell_tot)}
out["missing_vs_belowlod"] = {
    "na_total_cells": na_total,
    "na_by_col": na_by_col,
    "n_cols_with_na": len(na_by_col),
    "below_lod_by_col": below,
    "indicator_cols_5_95": {"n": len(indicator_cols), "cols": indicator_cols},
    "group_stats": {"physicochemical": group_stats(phys),
                    "aggregate": group_stats(agg),
                    "compound_C": group_stats(compC)},
}

# ---------- 6) 风格样本量（四联图 a） ----------
vc = df1["tasting_category_fine"].value_counts()
out["style_counts"] = [[str(k), int(v)] for k, v in vc.items()]

with open(os.path.join(HERE, "supp_preprocess.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

print("=== 附件概况 ===")
for k, v in out["attachment_overview"].items():
    print(k, v.get("rows", v.get("n_sheets")), "x", v.get("cols", ""), v.get("sheets", ""))
print("\n=== 三分类 ===")
print("总", len(chem_cols), "理化", len(phys), "汇总", len(agg), "化合物C", len(compC))
print("\n=== 对数底核实 ===")
print("可核实列数", len(per_col), "判定计数", counts)
print("严格log10", len(strict_log10), "严格raw", len(strict_raw),
      "近似log10", len(approx_log10), "近似raw", len(approx_raw))
print("\n=== 未检出 vs 缺失 ===")
print("NA单元格总数", na_total, "含NA列数", len(na_by_col))
print("指示变量(5%-95%)列数", len(indicator_cols))
print("分组", out["missing_vs_belowlod"]["group_stats"])
print("\nthr calibrated", out["log_base_audit"]["calibrated_threshold_sheet"]["calibrated_values"])
print("origin", out["log_base_audit"]["calibrated_threshold_sheet"]["origin_counts"])
print("\n样例残差:")
for c in demo_compounds + demo_phys:
    if c in per_col:
        print(" ", c, per_col[c])
print("\nwritten supp_preprocess.json")
