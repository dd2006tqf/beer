
"""Q1-1 + Q1-2 特征增广实验（不改主流水线，先离线评估）。

Q1-1 阈值超限先验：对有阈值的 43 列，按尺度换算到与 1.csv 同一空间后，
      生成 (a) 是否超阈二值列 (b) 该样本在全部有阈值列上的超阈比例。全部折内拟合。
Q1-2 模块 PC1：用 Q2 的 Louvain 社区成员，对每个大模块（成员>=5）取第一主成分。
      为避免泄漏，PCA 只在训练折上 fit，再变换验证折。

评估：与现有主模型同折、同分箱、同指标，逐维 QWL 对比，报告平均 QWK 变化。
"""
import os, sys, json
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import cohen_kappa_score

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'code'))
import params as P, utils as U, problem1 as Q1

df1, X, feat, meta = U.load_chem(os.path.join(ROOT, 'user_data'))
Y, sens = U.load_sensory(os.path.join(ROOT, 'user_data'))
styles = meta[P.STYLE_COL].values
Xv = np.asarray(X.values, dtype=float)
Yv = np.asarray(Y.values, dtype=float)
J = len(sens)

scale = json.load(open(os.path.join(ROOT, 'figures', 'derived', 'q1_col_scale.json'), encoding='utf-8'))
th = pd.read_excel(os.path.join(ROOT, 'user_data', '8.xlsx'), sheet_name='Sensory thresholds')
idx = {c: i for i, c in enumerate(feat)}

# 阈值列：换算到 1.csv 空间
thr_cols = []
for _, r in th.iterrows():
    if not pd.notna(r['threshold_mean']): continue
    c = r['field_name_R']
    if c not in idx: continue
    t = float(r['threshold_mean'])
    kind = scale.get(c)
    # 未在校准清单里的列按原值处理（保守）
    t_use = np.log10(t) if (kind == 'log10' and t > 0) else t
    thr_cols.append((idx[c], t_use, c))
print('[Q1-1] 阈值列 %d 个' % len(thr_cols), flush=True)

# 模块 PC1：用 Q2 全图社区
net = json.load(open(os.path.join(ROOT, 'figures', 'derived', 'q2_full_network.json'), encoding='utf-8'))
name2pos = {n['name']: n['id'] for n in net['nodes']}
comm_members = {}
for n in net['nodes']:
    comm_members.setdefault(n['comm'], []).append(n['id'])
mods = [(c, m) for c, m in comm_members.items() if len(m) >= 5]
mods.sort(key=lambda t: -len(t[1]))
mods = mods[:11]
print('[Q1-2] 模块 PC1 取 %d 个（成员 >=5）' % len(mods), flush=True)

vc = pd.Series(styles).value_counts()
strat = np.array([s if vc[s] >= P.N_FOLDS else '_rare' for s in styles])
skf = StratifiedKFold(n_splits=P.N_FOLDS, shuffle=True, random_state=P.SEED)
folds = list(skf.split(Xv, strat))

def run_variant(use_thr, use_pc1):
    oof = np.full((len(Xv), J), np.nan)
    true_lvl = np.full((len(Xv), J), -1, dtype=int)
    for tr, va in folds:
        Xtr, Xva = Xv[tr], Xv[va]
        extra_tr, extra_va = [], []
        if use_thr:
            # 超阈二值（逐列）+ 超阈比例（1 列）
            Btr = np.column_stack([Xtr[:, p] >= t for p, t, _ in thr_cols]).astype(float)
            Bva = np.column_stack([Xva[:, p] >= t for p, t, _ in thr_cols]).astype(float)
            extra_tr.append(Btr); extra_va.append(Bva)
            extra_tr.append(Btr.mean(1, keepdims=True))
            extra_va.append(Bva.mean(1, keepdims=True))
        if use_pc1:
            cols_tr, cols_va = [], []
            for c, mem in mods:
                sub_tr = Xtr[:, mem]
                sub_va = Xva[:, mem]
                med = np.nanmedian(sub_tr, axis=0)
                sub_tr = np.where(np.isnan(sub_tr), med, sub_tr)
                sub_va = np.where(np.isnan(sub_va), med, sub_va)
                pca = PCA(n_components=1).fit(sub_tr)
                cols_tr.append(pca.transform(sub_tr)[:, 0])
                cols_va.append(pca.transform(sub_va)[:, 0])
            extra_tr.append(np.column_stack(cols_tr))
            extra_va.append(np.column_stack(cols_va))
        Atr = np.hstack([Xtr] + extra_tr) if extra_tr else Xtr
        Ava = np.hstack([Xva] + extra_va) if extra_va else Xva
        for j in range(J):
            ytr, yva = Yv[tr, j], Yv[va, j]
            b = U.Binner().fit(ytr)
            true_lvl[va, j] = b.transform(yva)
            m = Q1._fit_lgb(Atr, ytr)
            rc = m.predict(Ava)
            oof[va, j] = (Q1._fit_ordinal(Atr, ytr, Ava) if Q1.binning_degenerate(ytr)
                          else b.transform_continuous(rc))
    qwk = [cohen_kappa_score(true_lvl[:, j], oof[:, j].astype(int), weights='quadratic')
           for j in range(J)]
    return float(np.mean(qwk)), qwk

print('\n=== 运行 4 个变体 ===', flush=True)
results = {}
for name, (t, p) in {'baseline': (False, False), 'thr': (True, False),
                     'pc1': (False, True), 'thr+pc1': (True, True)}.items():
    m, q = run_variant(t, p)
    results[name] = {'mean_qwk': round(m, 4), 'qwk': [round(x, 4) for x in q]}
    print('  %-8s mean QWK = %.4f' % (name, m), flush=True)

base = np.array(results['baseline']['qwk'])
for k in results:
    if k == 'baseline': continue
    d = np.array(results[k]['qwk']) - base
    print('  %-8s Δmean=%+.4f  改善维=%d  退化维=%d'
          % (k, d.mean(), int((d > 0.001).sum()), int((d < -0.001).sum())), flush=True)

out = {
    'n_threshold_cols': len(thr_cols),
    'n_module_pc1': len(mods),
    'module_sizes': [len(m) for _, m in mods],
    'results': {k: {'mean_qwk': v['mean_qwk']} for k, v in results.items()},
    'per_dim_qwk': {k: v['qwk'] for k, v in results.items()},
    'dims': sens,
}
path = os.path.join(ROOT, 'figures', 'derived', 'q1_feature_aug.json')
json.dump(out, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nsaved', path)
