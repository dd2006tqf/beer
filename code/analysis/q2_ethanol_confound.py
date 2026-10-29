# -*- coding: utf-8 -*-
"""酒精度混杂复核：用 8.xlsx 的 chemical_name <-> field_name_R 映射 6.csv 行名。"""
import sys, json
sys.path.insert(0, "code")
import numpy as np, pandas as pd
import utils as U

th = pd.read_excel("user_data/8.xlsx", sheet_name="Sensory thresholds")
name2R = {}
for _, r in th.iterrows():
    cn, fr = r.get("chemical_name"), r.get("field_name_R")
    if pd.notna(cn) and pd.notna(fr):
        name2R[str(cn).strip()] = str(fr).strip()
print("mapped names:", len(name2R))

df1, X, feat, meta = U.load_chem("user_data")
Y, sens = U.load_sensory("user_data")
Xv = np.asarray(X.values, float); Yv = np.asarray(Y.values, float)
pos = {c: i for i, c in enumerate(feat)}
eth = Xv[:, pos["ethanol..v.v."]]

C6, rows6, sens6 = U.load_cross_corr("user_data")
cols_short = U.align_sensory_cols([str(c) for c in C6.columns])
print("6.csv rows:", len(rows6), "| cols mapped:", len(cols_short))

def rank(a):
    return pd.Series(a).rank().values

def partial(a, b, z):
    ok = np.isfinite(a) & np.isfinite(b) & np.isfinite(z)
    if ok.sum() < 30:
        return np.nan, np.nan
    ra, rb, rz = rank(a[ok]), rank(b[ok]), rank(z[ok])
    Z = np.column_stack([np.ones_like(rz), rz])
    ra = ra - Z @ np.linalg.lstsq(Z, ra, rcond=None)[0]
    rb = rb - Z @ np.linalg.lstsq(Z, rb, rcond=None)[0]
    return float(np.corrcoef(rank(a[ok]), rank(b[ok]))[0,1]), float(np.corrcoef(ra, rb)[0,1])

rows = []
n_unmapped = 0
for ri, cname in enumerate(rows6):
    R = name2R.get(str(cname).strip())
    if R is None or R not in pos:
        n_unmapped += 1
        continue
    a = Xv[:, pos[R]]
    for k, s in enumerate(cols_short):
        if s not in sens:
            continue
        b = Yv[:, sens.index(s)]
        rr, rp = partial(a, b, eth)
        if np.isfinite(rr) and np.isfinite(rp):
            rows.append({"compound": str(cname), "R": R, "sensory": s, "r": rr, "r_eth": rp})
print("unmapped rows:", n_unmapped, "| pairs:", len(rows))

df = pd.DataFrame(rows)
df.to_csv("figures/derived/q2_ethanol_confound_pairs.csv", index=False, encoding="utf-8-sig")
print()
print("median |r|        = %.4f" % df.r.abs().median())
print("median |r|eth     = %.4f" % df.r_eth.abs().median())
print("frac |r|>=0.3     = %.3f -> %.3f" % ((df.r.abs()>=0.3).mean(), (df.r_eth.abs()>=0.3).mean()))
print("sign agreement    = %.3f" % (np.sign(df.r)==np.sign(df.r_eth)).mean())
print("median shrink     = %.3f" % (df.r_eth.abs() - df.r.abs()).median())
print()
top = df.reindex(df.r.abs().sort_values(ascending=False).index).head(8)
for _, r in top.iterrows():
    print("%-26s %-16s r=%+.3f -> r|eth=%+.3f" % (r["compound"][:26], r["sensory"], r["r"], r["r_eth"]))

json.dump({"n_pairs": int(len(df)),
           "median_abs_raw": round(float(df.r.abs().median()),4),
           "median_abs_partial": round(float(df.r_eth.abs().median()),4),
           "frac_ge_0_3_raw": round(float((df.r.abs()>=0.3).mean()),4),
           "frac_ge_0_3_partial": round(float((df.r_eth.abs()>=0.3).mean()),4),
           "sign_agreement": round(float((np.sign(df.r)==np.sign(df.r_eth)).mean()),4),
           "n_rows_unmapped": n_unmapped},
          open("figures/derived/q2_ethanol_confound.json","w",encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\nsaved q2_ethanol_confound.json")
