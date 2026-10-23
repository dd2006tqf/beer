# -*- coding: utf-8 -*-
"""supp_prep_eda.py — 从原始数据派生图所需数据（只读 user_data，输出 supp_eda.json）。
派生内容：
  1) style_counts   : 1.csv 22 风格样本量（EDA 面板 a）
  2) pca_chem       : 1.csv 231 化学维标准化后 PCA 前两主成分 + 按风格（EDA 面板 b）
  3) missing        : 1.csv 列缺失率 + 行缺失分布（问题一缺失模式图）
  4) chem_sensory_corr : Q2 关键化合物 × 12 感官维 Pearson 相关（问题二合理性证据）
不改上游结果，不重跑求解；仅做可追溯派生计算。"""
import json, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
UD = os.path.join(ROOT, 'user_data')

df1 = pd.read_csv(os.path.join(UD, '1.csv'))            # 化学谱 + 风格（含缺失）
df4 = pd.read_csv(os.path.join(UD, '4.csv'))            # 感官标准化值
meta_cols = ['beer', 'beer_id', 'tasting_category_fine']
chem_cols = [c for c in df1.columns if c not in meta_cols]
chem_num = df1[chem_cols].apply(pd.to_numeric, errors='coerce')

out = {}

# 1) 风格样本量
vc = df1['tasting_category_fine'].value_counts()
out['style_counts'] = [[str(k), int(v)] for k, v in vc.items()]

# 2) 化学谱 PCA（标准化 + 均值填补缺失，仅用于可视化降维）
X = chem_num.values.astype(float)
col_mean = np.nanmean(X, axis=0)
inds = np.where(np.isnan(X))
X[inds] = np.take(col_mean, inds[1])
mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd == 0] = 1.0
Xs = (X - mu) / sd
U, S, Vt = np.linalg.svd(Xs, full_matrices=False)
scores = Xs @ Vt[:2].T
ev = (S**2) / (S**2).sum()
styles = df1['tasting_category_fine'].astype(str).tolist()
out['pca_chem'] = {
    'x': [round(float(v), 4) for v in scores[:, 0]],
    'y': [round(float(v), 4) for v in scores[:, 1]],
    'style': styles,
    'explained_var': [round(float(ev[0]), 4), round(float(ev[1]), 4)],
}

# 3) 缺失模式
na_mask = chem_num.isna()
col_na_rate = na_mask.mean(axis=0)
nz = col_na_rate[col_na_rate > 0].sort_values(ascending=False)
out['missing'] = {
    'col_na_rate': [[str(k), round(float(v), 4)] for k, v in nz.items()],
    'row_na_counts': [int(x) for x in na_mask.sum(axis=1).values],
    'n_rows': int(len(df1)),
    'n_cols': int(len(chem_cols)),
    'n_na_rows': int((na_mask.sum(axis=1) > 0).sum()),
    # 含缺失列的行×列 0/1 矩阵（仅取有缺失的列，便于画缺失模式矩阵）
    'na_cols': list(nz.index),
    'na_matrix': na_mask[list(nz.index)].astype(int).values.tolist() if len(nz) > 0 else [],
}

# 4) 化学×感官交叉相关（Q2 关键化合物 × 12 感官维）
p2 = json.load(open(os.path.join(HERE, 'problem_2_results.json'), encoding='utf-8'))
dims12 = list(p2['per_dim'].keys())                     # 12 个被归因的感官维
comp_names = []
for d in dims12:
    comp_names += list(p2['per_dim'][d]['top3'])
# 统计出现频次，取存在于 1.csv 的、出现最多的若干化合物
from collections import Counter
cnt = Counter(comp_names)
key_comps = [c for c, _ in cnt.most_common() if c in chem_cols]
key_comps = key_comps[:14]
# 对齐 beer_id
m = df1[['beer_id'] + key_comps].merge(df4[['beer_id'] + dims12], on='beer_id', how='inner')
corr = np.full((len(dims12), len(key_comps)), np.nan)
for i, s in enumerate(dims12):
    for j, c in enumerate(key_comps):
        a = pd.to_numeric(m[s], errors='coerce')
        b = pd.to_numeric(m[c], errors='coerce')
        ok = a.notna() & b.notna()
        if ok.sum() >= 5 and a[ok].std() > 0 and b[ok].std() > 0:
            corr[i, j] = np.corrcoef(a[ok], b[ok])[0, 1]
out['chem_sensory_corr'] = {
    'sensory_dims': dims12,
    'compounds': key_comps,
    'matrix': [[None if np.isnan(v) else round(float(v), 3) for v in row] for row in corr],
}

with open(os.path.join(HERE, 'supp_eda.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('supp_eda.json written')
print('styles:', len(out['style_counts']), '| pca ev:', out['pca_chem']['explained_var'])
print('missing cols:', len(out['missing']['col_na_rate']), '| key_comps:', len(key_comps))
