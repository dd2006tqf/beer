# -*- coding: utf-8 -*-
"""公共工具：数据加载、0-6 分箱映射、QWK、随机种子、轻量检查点。

不 import _utils（评委机无该目录）。所有路径相对 --data-dir。
"""
import os
import sys
import json
import random

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_ROOT = os.path.dirname(_HERE)

import numpy as np
import pandas as pd

import params as P


# ---------------- 随机种子 ----------------
def set_all_seeds(seed=P.SEED):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


# ---------------- 读取 + DATA_PROFILE 核对 ----------------
def _read_csv(path):
    for enc in ("utf-8", "utf-8-sig", "gbk", "gb2312", "latin-1"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise RuntimeError(f"无法解码 {path}")


def _check_rows(fname, n):
    """若 DATA_PROFILE.json 存在则核对原始读取行数（评委机无此文件则跳过）。"""
    pth = os.path.join(_ROOT, "DATA_PROFILE.json")
    if not os.path.exists(pth):
        return
    prof = json.load(open(pth, encoding="utf-8"))["files"].get(fname, {})
    if "total_rows" in prof:
        assert n == prof["total_rows"], (
            f"[摄入不全] {fname} 实读 {n} 行 ≠ 建档 {prof['total_rows']} 行")
        print(f"[data_ingest] {fname} 全量 {n} 行 已核对通过")


def load_chem(data_dir):
    """1.csv：返回 (df_full, X 特征矩阵DataFrame[含缺失], feat_cols, meta_df)。"""
    df = _read_csv(os.path.join(data_dir, "1.csv"))
    _check_rows("1.csv", len(df))
    feat_cols = [c for c in df.columns if c not in P.META_COLS]
    assert len(feat_cols) == P.N_FEATURES, f"特征数应 {P.N_FEATURES}，实 {len(feat_cols)}"
    X = df[feat_cols].apply(pd.to_numeric, errors="coerce")
    meta = df[P.META_COLS].copy()
    return df, X, feat_cols, meta


def load_sensory(data_dir):
    """4.csv：返回 (Y 标签DataFrame[50维连续], sens_cols)。"""
    df = _read_csv(os.path.join(data_dir, "4.csv"))
    _check_rows("4.csv", len(df))
    sens_cols = [c for c in df.columns if c not in P.META_COLS]
    assert len(sens_cols) == P.N_SENSORY, f"感官维应 {P.N_SENSORY}，实 {len(sens_cols)}"
    Y = df[sens_cols].apply(pd.to_numeric, errors="coerce")
    return Y, sens_cols


def load_compound_corr(data_dir):
    """2.csv：返回 (R 相关矩阵 np[231x231], comp_names)。与 1.csv 特征同序（位置对齐）。"""
    df = _read_csv(os.path.join(data_dir, "2.csv"))
    _check_rows("2.csv", len(df))
    comp_names = list(df.columns[1:])
    R = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce").values.astype(float)
    assert R.shape[0] == R.shape[1] == P.N_FEATURES, f"2.csv 应 {P.N_FEATURES} 方阵，实 {R.shape}"
    return R, comp_names


def load_cross_corr(data_dir):
    """6.csv：返回 (C 交叉相关 DataFrame[44化合物 x 50感官], comp_rows, sens_cols6)。"""
    df = _read_csv(os.path.join(data_dir, "6.csv"))
    _check_rows("6.csv", len(df))
    comp_rows = df.iloc[:, 0].astype(str).tolist()
    sens_cols6 = list(df.columns[1:])
    C = df.iloc[:, 1:].apply(pd.to_numeric, errors="coerce")
    C.index = comp_rows
    return C, comp_rows, sens_cols6


def align_sensory_cols(sens6):
    """把 6.csv 的感官列名映射到 4.csv 的 50 个短名。

    6.csv 用英文全名（Malt aroma - overall / Carbonation / ...），4.csv 用
    A_/F_ 前缀短名。前 46 列顺序一致，但 **第 47-50 位不同**：
        6.csv: 46 Carbonation, 47 Aftertaste, 48 Body, 49 Overall
        4.csv: 46 aftertaste,  47 body,       48 co2,   49 overall
    因此必须先按名映射，不能按位置对齐。返回 4.csv 列名列表（与 6.csv 同序）。
    """
    NAME_MAP = [
        ("Malt aroma - overall", "A_malt_all"),
        ("Malt aroma - grain", "A_malt_grain"),
        ("Malt aroma - bread", "A_malt_bread"),
        ("Malt aroma - caramel", "A_malt_cara"),
        ("Malt aroma - smoked", "A_malt_burn"),
        ("Hops aroma - overall", "A_hops_all"),
        ("Hops aroma - citrus", "A_hops_citrus"),
        ("Hops aroma - tropical fruit", "A_hops_tropical"),
        ("Hops aroma - grassy", "A_hops_noble"),
        ("Hops aroma - woody", "A_hops_woody"),
        ("Esters aroma - overall", "A_esters_all"),
        ("Esters aroma - nail polish", "A_esters_ethac"),
        ("Esters aroma - banana", "A_esters_isoaa"),
        ("Esters aroma - floral", "A_esters_flower"),
        ("Esters aroma - fruity", "A_esters_fruity"),
        ("Malt taste - overall", "F_malt_all"),
        ("Malt taste - grain", "F_malt_grain"),
        ("Malt taste - bread", "F_malt_bread"),
        ("Malt taste - caramel", "F_malt_cara"),
        ("Malt taste - smoked", "F_malt_burn"),
        ("Hops taste - overall", "F_hops_all"),
        ("Hops taste - citrus", "F_hops_citrus"),
        ("Hops taste - tropical fruit", "F_hops_tropical"),
        ("Hops taste - grassy", "F_hops_noble"),
        ("Hops taste - woody", "F_hops_woody"),
        ("Esters taste - overall", "F_esters_all"),
        ("Esters taste - nail polish", "F_esters_ethac"),
        ("Esters taste - banana", "F_esters_isoaa"),
        ("Esters taste - floral", "F_esters_flower"),
        ("Esters taste - fruity", "F_esters_fruity"),
        ("Acidity", "acidity"),
        ("Bitterness", "bitternes"),
        ("Sweetness", "sweetness"),
        ("4-vinyl guaiacol", "X4vg"),
        ("Diacetyl", "diacetyl"),
        ("Dimethyl sulfide", "dms"),
        ("Metallic", "metallic"),
        ("Stale hops", "stale_hops"),
        ("Trans-2-nonenal", "t2n"),
        ("Orange", "orange"),
        ("Coriander", "coriander"),
        ("Clove", "clove"),
        ("Lactic acid", "lactic"),
        ("Acetic acid", "acetic"),
        ("Barnyard", "barnyard"),
        ("Alcohol", "alcohol"),
        ("Carbonation", "co2"),
        ("Aftertaste", "aftertaste"),
        ("Body", "body"),
        ("Overall appreciation", "overall"),
    ]
    m = {}
    for full, short in NAME_MAP:
        m[full.lower()] = short
    out = []
    for raw in sens6:
        key = " ".join(str(raw).replace("\r", " ").replace("\n", " ").split()).lower()
        key = key.replace("(trained panel)", "").strip()
        hit = m.get(key)
        if hit is None:
            for full, short in NAME_MAP:
                if full.lower().split(" - ")[0] == key.split(" - ")[0] and \
                        full.lower().split(" - ")[-1].startswith(key.split(" - ")[-1]):
                    hit = short
                    break
        if hit is None:
            raise KeyError("无法映射 6.csv 感官列: %r" % raw)
        out.append(hit)
    assert len(set(out)) == len(out), "6.csv 感官列映射出现重复"
    return out


def load_gbm_reference(data_dir):
    """8.xlsx：GBM importance MDI（参考重要性，仅 Q2 旁证，不进 Q1 训练）。显式 sheet_name。"""
    pth = os.path.join(data_dir, "8.xlsx")
    if not os.path.exists(pth):
        return None
    mdi = pd.read_excel(pth, sheet_name="GBM importance MDI")
    return mdi


# ---------------- 0-6 分箱映射 ----------------
class Binner:
    """对单个感官维，训练折内估分位点，映射连续值 -> 0..6 整数等级。"""

    def __init__(self, scheme=P.LABEL_BINNING, n_levels=P.N_LEVELS):
        self.scheme = scheme
        self.n_levels = n_levels
        self.edges = None   # 6 个内部切点

    def fit(self, y):
        y = np.asarray(y, dtype=float)
        y = y[np.isfinite(y)]
        q = self.n_levels  # 7 级 -> 6 个内部分位点
        if self.scheme == "quantile":
            probs = np.linspace(0, 1, q + 1)[1:-1]  # 6 点
            self.edges = np.quantile(y, probs)
        else:  # uniform 等距
            lo, hi = y.min(), y.max()
            self.edges = np.linspace(lo, hi, q + 1)[1:-1]
        # 去重保证单调（极端退化时）
        self.edges = np.maximum.accumulate(self.edges)
        return self

    def transform(self, y):
        y = np.asarray(y, dtype=float)
        lvl = np.searchsorted(self.edges, y, side="right")  # 0..6
        return np.clip(np.round(lvl), P.LEVEL_MIN, P.LEVEL_MAX).astype(int)

    def transform_continuous(self, r):
        """对回归连续输出施加同一映射 + clip + round（式2）。"""
        return self.transform(r)


def quadratic_weighted_kappa(y_true, y_pred, n_levels=P.N_LEVELS):
    """二次加权 Kappa（有序分级首选）。手写实现，避免 sklearn 对缺等级的边界问题。"""
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)
    N = n_levels
    O = np.zeros((N, N), dtype=float)
    for a, b in zip(y_true, y_pred):
        O[a, b] += 1
    w = np.zeros((N, N), dtype=float)
    for i in range(N):
        for j in range(N):
            w[i, j] = (i - j) ** 2 / (N - 1) ** 2
    act = O.sum(axis=1)
    pred = O.sum(axis=0)
    E = np.outer(act, pred) / O.sum()
    denom = (w * E).sum()
    if denom == 0:
        return 1.0 if (w * O).sum() == 0 else 0.0
    return 1.0 - (w * O).sum() / denom


# ---------------- 轻量检查点（code/ 内自带，不依赖 _utils）----------------
def ckpt_path(name):
    d = os.path.join(_ROOT, "_tmp", "checkpoints")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, name)


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, default=_json_default)
    os.replace(tmp, path)


def _json_default(o):
    import numpy as _np
    if isinstance(o, (_np.integer,)):
        return int(o)
    if isinstance(o, (_np.floating,)):
        return float(o)
    if isinstance(o, (_np.ndarray,)):
        return o.tolist()
    raise TypeError(f"not serializable: {type(o)}")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)
