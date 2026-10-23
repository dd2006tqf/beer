# -*- coding: utf-8 -*-
"""数据读取验证：确认 1/2/4/6.csv、8.xlsx 读取正确 + 231/50 维位置对齐。

先跑本脚本，确认无误再写求解代码。只打印结论，不打印整表。
"""
import os
import sys
import glob

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import numpy as np
import pandas as pd


def _read_csv(path):
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc), enc
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"无法解码 {path}")


def main(data_dir="user_data"):
    print(f"[data_check] data_dir = {data_dir}")
    files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))
    for f in files:
        df, enc = _read_csv(f)
        na_total = int(df.isnull().sum().sum())
        print(f"  {os.path.basename(f)}: shape={df.shape} enc={enc} NA总数={na_total}")

    # 位置对齐核对：1.csv 231 特征列 vs 2.csv 231 相关矩阵行/列
    d1, _ = _read_csv(os.path.join(data_dir, "1.csv"))
    d2, _ = _read_csv(os.path.join(data_dir, "2.csv"))
    d4, _ = _read_csv(os.path.join(data_dir, "4.csv"))
    d6, _ = _read_csv(os.path.join(data_dir, "6.csv"))

    meta = ["beer", "beer_id", "tasting_category_fine"]
    feat1 = [c for c in d1.columns if c not in meta]
    comp2 = list(d2.columns[1:])          # 去掉首列化合物名
    sens4 = [c for c in d4.columns if c not in meta]
    sens6 = list(d6.columns[1:])          # 去掉首列
    print(f"\n[对齐] 1.csv特征数={len(feat1)}  2.csv化合物数={len(comp2)}  "
          f"4.csv感官维={len(sens4)}  6.csv感官列={len(sens6)}  6.csv化合物行={d6.shape[0]}")
    assert len(feat1) == 231, f"1.csv 特征数应 231，实为 {len(feat1)}"
    assert len(comp2) == 231, f"2.csv 化合物数应 231，实为 {len(comp2)}"
    assert len(sens4) == 50, f"4.csv 感官维应 50，实为 {len(sens4)}"
    assert len(sens6) == 50, f"6.csv 感官列应 50，实为 {len(sens6)}"

    # 抽样核对位置对齐（1.csv短名 ↔ 2.csv全名，同序）
    pairs = [(3, "DMS", "Dimethyl sulfide"), (8, "ethyl_acetate", "Ethyl acetate")]
    for idx, n1, n2 in pairs:
        print(f"  pos{idx}: 1.csv='{feat1[idx]}' ({n1})  2.csv='{comp2[idx]}' ({n2})")

    # 缺陷列存在性
    defects = ["DMS", "X2.3.butanedione", "X4VG", "X.E..2.nonenal"]
    for dcol in defects:
        print(f"  缺陷列 {dcol}: {'存在' if dcol in feat1 else '缺失!!'}")

    # 风格分布
    vc = d1["tasting_category_fine"].value_counts()
    print(f"\n[风格] 共 {vc.shape[0]} 类；最大 {vc.iloc[0]}({vc.index[0]}) 最小 {vc.iloc[-1]}({vc.index[-1]})")

    # 含缺失行统计
    na_rows = int(d1[feat1].isnull().any(axis=1).sum())
    na_total = int(d1[feat1].isnull().sum().sum())
    print(f"[缺失] 1.csv 含NA行={na_rows}/250  NA总数={na_total}")
    assert na_total == 73, f"NA 总数应 73，实为 {na_total}"
    assert na_rows == 63, f"含NA行应 63，实为 {na_rows}"

    # 8.xlsx 显式 sheet
    x8 = os.path.join(data_dir, "8.xlsx")
    if os.path.exists(x8):
        thr = pd.read_excel(x8, sheet_name="Sensory thresholds")
        mdi = pd.read_excel(x8, sheet_name="GBM importance MDI")
        print(f"[8.xlsx] Sensory thresholds={thr.shape}  GBM importance MDI={mdi.shape}")

    print("\n[data_check] 全部核对通过 ✅")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "user_data")
