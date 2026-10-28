# -*- coding: utf-8 -*-
"""D1 方案 A 的配对 bootstrap：主模型 vs 分组堆叠，2000 次重采样。"""
import os, sys, json
import numpy as np, pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "code"))
import utils as U

d = pd.read_csv(os.path.join(ROOT, "submission", "q1_oof_predictions.csv"), encoding="utf-8-sig")
sens = [c.split("__", 1)[1] for c in d.columns if c.startswith("true__")]
true = d[["true__" + s for s in sens]].values.astype(int)
main = d[["main__" + s for s in sens]].values.astype(int)

pack = np.load(os.path.join(ROOT, "_tmp", "q1_group_stack_oof.npy"))
t2, p2 = pack[0].astype(int), pack[1].astype(int)
assert np.array_equal(true, t2), "真实标签不一致"

k = U.quadratic_weighted_kappa
n = true.shape[0]
rng = np.random.default_rng(7)
deltas = np.empty(2000)
for b in range(2000):
    idx = rng.integers(0, n, n)
    a = np.mean([k(true[idx, j], main[idx, j]) for j in range(len(sens))])
    c = np.mean([k(true[idx, j], p2[idx, j]) for j in range(len(sens))])
    deltas[b] = a - c
lo, hi = np.percentile(deltas, [2.5, 97.5])
pi = float(np.mean(deltas > 0))
print("mean delta %.4f  CI [%.4f, %.4f]  pi=%.3f" % (deltas.mean(), lo, hi, pi))

out = {"mean_delta_ci": [round(float(deltas.mean()), 4), round(float(lo), 4), round(float(hi), 4)],
       "pi_main_better": round(pi, 3), "n_boot": 2000}
p = os.path.join(ROOT, "figures", "derived", "q1_group_stack_boot.json")
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("saved", out)
