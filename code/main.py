# -*- coding: utf-8 -*-
"""一键入口：依次运行 Q1→Q2→Q3，并汇总 figures/all_results.json。

用法：
    python main.py --data-dir ../user_data        # 原始数据目录（默认 user_data）
结果：
    submission/q1_sensory_scores.csv  q2_top3_compounds.csv  q3_generated_profiles.csv
    figures/problem_{1,2,3}_results.json, figures/all_results.json
"""
import os
import sys
import json
import argparse

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_ROOT = os.path.dirname(_HERE)

import numpy as np
import pandas as pd

import params as P
import utils as U
import problem1
import problem2
import problem3


def _default_data_dir():
    for cand in (os.path.join(_ROOT, "user_data"), os.path.join(_HERE, "..", "user_data"),
                 "user_data"):
        if os.path.isdir(cand):
            return cand
    return "user_data"


def aggregate(out_dir):
    fig = os.path.join(out_dir, "figures")
    r1 = U.load_json(os.path.join(fig, "problem_1_results.json"))
    r2 = U.load_json(os.path.join(fig, "problem_2_results.json"))
    r3 = U.load_json(os.path.join(fig, "problem_3_results.json"))

    # 跨问一致性：Q2 高稳定维度数 <= Q1 可预测维度数
    n_pred = r1["summary"]["n_predictable_dims"]
    n_stable = r2["summary"]["n_high_stable_dims"]

    allr = {
        "problem_id": "A", "team_id": "MCB2600304",
        "seed": P.SEED,
        "q1": r1["summary"], "q2": r2["summary"], "q3": r3["summary"],
        # 逻辑合同回填键（供 logic_audit / cross_problem_check）
        "q3_defect_compliance_rate": r3["summary"]["defect_compliance_rate"],
        "gen_tripel_ester_level": r3["summary"]["gen_tripel_ester_level"],
        "real_tripel_ester_level": r3["summary"]["real_tripel_ester_level"],
        "logic_probes": {"bounds": [], "monotonic": []},
        "cross_problem": {
            "n_predictable_dims_Q1": n_pred,
            "n_high_stable_dims_Q2": n_stable,
            "Q2_stable_le_Q1_predictable": bool(n_stable <= n_pred),
        },
    }
    U.save_json(allr, os.path.join(fig, "all_results.json"))
    print(f"[main] 汇总写入 figures/all_results.json  "
          f"(Q1可预测维={n_pred}, Q2高稳定维={n_stable}, 合规率={allr['q3_defect_compliance_rate']})")
    _update_ledger(out_dir, n_pred, n_stable, allr["q3_defect_compliance_rate"])
    return allr


def _update_ledger(out_dir, n_pred, n_stable, compliance):
    """把实际结果回填 CROSS_PROBLEM_LEDGER.json 的 observed。"""
    pth = os.path.join(out_dir, "CROSS_PROBLEM_LEDGER.json")
    if not os.path.exists(pth):
        return
    led = json.load(open(pth, encoding="utf-8"))
    for pb in led.get("problems", []):
        if pb["id"] == "Q1":
            pb["observed"] = {"n_predictable_dims": n_pred}
        elif pb["id"] == "Q2":
            pb["observed"] = {"n_high_stable_dims": n_stable}
        elif pb["id"] == "Q3":
            pb["observed"] = {"defect_compliance_rate": compliance}
    with open(pth, "w", encoding="utf-8") as f:
        json.dump(led, f, ensure_ascii=False, indent=2)
    print("[main] 已回填 CROSS_PROBLEM_LEDGER.json observed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=None, help="原始数据目录（含 1.csv..8.xlsx）")
    ap.add_argument("--skip", default="", help="跳过的步骤，逗号分隔，如 q1,q2")
    args = ap.parse_args()
    data_dir = args.data_dir or _default_data_dir()
    skip = set(s.strip().lower() for s in args.skip.split(",") if s.strip())
    print(f"[main] data_dir={data_dir}  seed={P.SEED}")

    U.set_all_seeds(P.SEED)
    if "q1" not in skip:
        print("\n===== 问题一：含缺失多输出感官分级预测 =====")
        problem1.run(data_dir, _ROOT)
    if "q2" not in skip:
        print("\n===== 问题二：共表达图 + Top-3 + 稳定性 =====")
        problem2.run(data_dir, _ROOT)
    if "q3" not in skip:
        print("\n===== 问题三：CVAE 风格条件生成 + 迁移 =====")
        problem3.run(data_dir, _ROOT)
    print("\n===== 汇总 =====")
    aggregate(_ROOT)
    print("[main] 全部完成。")


if __name__ == "__main__":
    main()
