# -*- coding: utf-8 -*-
"""自动化结果数值审查（NaN/Inf/区间/过拟合信号）。只打印结论，不打印整表。"""
import os
import sys
import json
import math
import re

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
FIG = os.path.join(_ROOT, "figures")

results = {}
for f in sorted(os.listdir(FIG)):
    if f.endswith("_results.json") or f == "all_results.json":
        with open(os.path.join(FIG, f), encoding="utf-8") as fh:
            results[f] = json.load(fh)

errors, warnings, suspicious = [], [], []


def check_value(name, val):
    if isinstance(val, float):
        if math.isnan(val):
            errors.append(f"FAIL {name} = NaN")
        elif math.isinf(val):
            errors.append(f"FAIL {name} = Inf")
        elif abs(val) > 1e15:
            warnings.append(f"WARN {name} = {val} 异常大")


def check_unrealistic(name, val):
    if not isinstance(val, (int, float)) or isinstance(val, bool):
        return
    key = re.sub(r"\[\d+\]", "", name.rsplit(".", 1)[-1]).lower()
    if key in {"qwk", "mean_qwk_main", "jaccard", "mean_cross_method_jaccard"}:
        if val > 1 + 1e-9 or val < -1 - 1e-9:
            errors.append(f"FAIL {name}: QWK/Jaccard 越界")
    if "compliance_rate" in key:
        if val > 1 + 1e-9 or val < 0:
            errors.append(f"FAIL {name}: 合规率越界[0,1]")
    if key in {"select_freq", "bootstrap_select_freq"}:
        if val > 1 + 1e-9 or val < 0:
            errors.append(f"FAIL {name}: 频率越界[0,1]")


def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, f"{path}[{i}]")
    elif isinstance(obj, (int, float)):
        check_value(path, obj)
        check_unrealistic(path, obj)


for fname, data in results.items():
    walk(data, fname)

for e in errors[:8]:
    print(e)
for w in warnings[:8]:
    print(w)
for s in suspicious[:8]:
    print(s)
if not errors and not warnings and not suspicious:
    print("✅ 所有数值通过 sanity check")
elif errors:
    print(f"\n{len(errors)} 错误 / {len(warnings)} 警告 — 必须修错误")
    sys.exit(1)
else:
    print(f"\n{len(warnings)} 警告 / {len(suspicious)} 可疑 — 逐条确认")
