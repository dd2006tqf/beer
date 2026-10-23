# -*- coding: utf-8 -*-
"""全局参数与命名常数（赛道 A 啤酒风味）。

数值常数来源：DATA_FACTS.json（题面硬事实）+ MODELING_REPORT.md ⓪参数口径表。
行数等数据规模基准从 DATA_PROFILE.json 读取（若存在），禁止手写魔数行数。
本文件不 import _utils（评委机无该目录）。
"""
import os
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

# ---------- 随机种子（可复现）----------
SEED = 42

# ---------- 数据规模基准（优先取 DATA_PROFILE.json）----------
_PROFILE_PATH = os.path.join(_ROOT, "DATA_PROFILE.json")
N_SAMPLES = 250
N_FEATURES = 231
N_SENSORY = 50
try:
    if os.path.exists(_PROFILE_PATH):
        _prof = json.load(open(_PROFILE_PATH, encoding="utf-8"))["files"]
        N_SAMPLES = int(_prof["1.csv"]["total_rows"])
        N_FEATURES = int(_prof["2.csv"]["total_rows"])
except Exception:
    pass

# ---------- 元列（主键/分组/风格，不进特征矩阵）----------
META_COLS = ["beer", "beer_id", "tasting_category_fine"]
KEY_COL = "beer_id"
STYLE_COL = "tasting_category_fine"

# ---------- Q1：分级与验证 ----------
N_LEVELS = 7            # 0..6，7 个有序等级（0-6 分制）
LEVEL_MIN, LEVEL_MAX = 0, 6
LABEL_BINNING = "quantile"   # {"quantile","uniform"}
N_FOLDS = 5
CV_SCHEME = "stratified_kfold"
# 核心 30 维（A_/F_ 前缀）；全 50 维一并交付
REPORT_SCOPE = "all50"

# ---------- Q2：共表达图 + 归因 + 稳定性 ----------
TOPN = 3
COEXPR_RHO = 0.5               # 建图相关阈值
COEXPR_RHO_SENS = [0.4, 0.6]   # 灵敏度
N_BOOTSTRAP = 500
# 多证据融合权重 α*SHAP + β*|cross-corr| + γ*module-rep
FUSE_ALPHA, FUSE_BETA, FUSE_GAMMA = 0.5, 0.3, 0.2

# ---------- Q3：条件生成 + 迁移 ----------
LATENT_DIM = 16                # 隐维 ∈ 8..16（小样本取上界增容量）
BETA_KL = 0.1                  # 小样本降低 KL 权重防后验坍塌（MODELING 异常③）
KL_ANNEAL_EPOCHS = 120         # KL 退火：前若干轮 β 线性 0→BETA_KL
FREE_BITS = 0.5                # free-bits：每维至少保留的 KL（nats），进一步防坍塌
CVAE_EPOCHS = 600
CVAE_LR = 1e-3
CVAE_BATCH = 64
MIN_STYLE_FOR_CVAE = 6         # 低于此样本量的风格走高斯兜底
TARGET_TYPICAL_Q = 0.5         # 目标风格缺陷典型分位（中位）
USE_ABS_THRESHOLD = False      # 8.xlsx 绝对阈值单位不可直接比，默认关闭

GEN_STYLES = ["Tripel", "Kriek", "Lambic"]       # 代表风格
TRANSFER_SOURCES = ["Pils/Lager"]  # 迁移源（实际风格名，含斜杠）
TRANSFER_TARGET = "Tripel"

# 缺陷化合物 → 1.csv 列名（来自 DATA_FACTS.json given 段）
# Stale hops 无对应化学列（陈化标记），化学空间投影只作用于下列 4 列。
DEFECT_COL_MAP = {
    "DMS": "DMS",
    "Diacetyl": "X2.3.butanedione",
    "4VG": "X4VG",
    "trans-2-nonenal": "X.E..2.nonenal",
}
DEFECT_COLS = list(DEFECT_COL_MAP.values())
DEFECT_NO_CHEM = ["Stale hops"]   # 无化学列，仅记录

# 核心感官维前缀
CORE_PREFIXES = ("A_", "F_")

# 理化/过程参数列（非挥发性芳香化合物；来源 DATA_FACTS.json「ethanol/color/bitterness/pH/CO2 等理化列」）
# 用于 Q2 给 Top-3 标注 feature_type，供化学合理性论证区分「挥发性化合物」与「理化指标」。
PHYSICOCHEM_COLS = {
    "SO2.mg.L.", "acetic_acid.g.L.", "ammonia.mg.L.", "color.EBC.", "betaglucan.mg.L.",
    "lactic_acid.mg.L.", "glycerol", "iron", "pH", "protein.g.L.", "bitterness", "GFS",
    "ethanol..v.v.", "CO2.PSI.", "unfermentables", "kcalperc",
}


def feature_type(name):
    return "physicochemical" if name in PHYSICOCHEM_COLS else "volatile_compound"


def core_sensory(sens_cols):
    """从 50 维中取核心 30 维（A_/F_ 前缀）。"""
    return [c for c in sens_cols if c.startswith(CORE_PREFIXES)]
