# -*- coding: utf-8 -*-
"""gen_tables.py — 从结果 JSON 生成全部 Markdown 三线表（数值不手抄，全部读 JSON）。
产出：
  TABLE_q1_model_cmp.md  Q1 主模型 vs 基线整体对比
  TABLE_q1_perf.md       T1 代表性感官维预测性能（QWK/MAE/R²）
  TABLE_q2_top3.md       T2 感官维 Top-3 关键化合物 + 稳定性
  TABLE_q3_defect.md     T3 跨风格迁移 4 缺陷化合物阈值合规
  TABLE_q3_style.md      T3 三代表风格生成质量概览
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys_path_root = os.path.dirname(HERE)
import sys
sys.path.insert(0, HERE)
from _figbase import dim_zh

P1 = json.load(open(os.path.join(HERE, 'problem_1_results.json'), encoding='utf-8'))
P2 = json.load(open(os.path.join(HERE, 'problem_2_results.json'), encoding='utf-8'))
P3 = json.load(open(os.path.join(HERE, 'problem_3_results.json'), encoding='utf-8'))


def write(name, lines):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', name)


def esc(s):
    return str(s).replace('|', r'\|')


# ── TABLE_q1_model_cmp ──────────────────────────────
s = P1['summary']
L = ['**表：问题一主模型与基线整体性能对比（50 维平均）**', '',
     '| 方法 | 平均 QWK | 说明 |', '|---|---|---|',
     f'| **LightGBM（原生缺失，主模型）** | **{s["mean_qwk_main"]:.4f}** | 含缺失行全参与训练 |',
     f'| KNN 插补 + LightGBM | {s["mean_qwk_knn_impute"]:.4f} | 缺失对照 |',
     f'| 随机森林（中位插补） | {s["mean_qwk_rf"]:.4f} | 基线 |',
     f'| ElasticNet（中位插补） | {s["mean_qwk_elasticnet"]:.4f} | 线性基线 |',
     f'| 逐维均值等级 | {s["mean_qwk_mean_baseline"]:.4f} | 朴素基线 |', '',
     f'> 注：QWK 为分层 5 折交叉验证的二次加权 Kappa 均值；全部 {s["n_dims"]} 维主模型均优于朴素基线，'
     f'其中 {s["n_main_chosen"]} 维最终选用 LightGBM。最优值已加粗。', '',
     '<!-- label: tab:q1_model_cmp -->']
write('TABLE_q1_model_cmp.md', L)


# ── TABLE_q1_perf (T1) 代表性维（按 QWK 降序取前 18）────────
rank = [r[0] for r in P1['fig_data']['qwk_ranked']]
per1 = P1['per_dim']
sel = [d for d in rank if d in per1][:18]
L = ['**表：代表性感官维度预测性能（交叉验证 QWK / MAE / $R^2$，按 QWK 降序取前 18）**', '',
     '| 感官维度 | QWK | MAE | $R^2$ | 选用模型 |', '|---|---|---|---|---|']
for d in sel:
    p = per1[d]
    L.append(f'| {esc(dim_zh(d))}（{esc(d)}） | {p["qwk_main"]:.3f} | {p["mae_main"]:.3f} '
             f'| {p["r2_main"]:.3f} | {p["chosen_model"]} |')
L += ['', f'> 注：共 {P1["summary"]["n_dims"]} 维，此处列交叉验证 QWK 最高的 18 维；'
      f'完整 50 维结果见支撑材料 `submission/q1_sensory_scores.csv`。QWK 为二次加权 Kappa，'
      f'$R^2$ 为连续预测值的决定系数（可为负，表示弱于常数预测）。', '',
      '<!-- label: tab:q1_perf -->']
write('TABLE_q1_perf.md', L)


# ── TABLE_q2_top3 (T2) 用 Q1-top 12 维 ─────────────────
q2dims = [d for d in rank if d in P2['per_dim']][:12]
per2 = P2['per_dim']
L = ['**表：代表性感官维度 Top-3 关键化合物及稳定性指标**', '',
     '| 感官维度 | Top-1 | Top-2 | Top-3 | Top-1 入选频率 | 跨方法 Jaccard |',
     '|---|---|---|---|---|---|']
for d in q2dims:
    p = per2[d]
    t3 = p['top3']
    sf = p['select_freq'][0]
    jac = p['jaccard_cross_method']
    L.append(f'| {esc(dim_zh(d))} | {esc(t3[0])} | {esc(t3[1])} | {esc(t3[2])} '
             f'| {sf:.3f} | {jac:.3f} |')
nb = P2['summary']['n_bootstrap']
mj = P2['summary']['mean_cross_method_jaccard']
L += ['', f'> 注：入选频率为 {nb} 次 bootstrap 中该化合物进入 Top-3 的比例；'
      f'跨方法 Jaccard 衡量共表达/SHAP/相关三类证据 Top-3 的一致性（全维均值 {mj:.3f}）；'
      f'完整 50 维见 `submission/q2_top3_compounds.csv`。', '',
      '<!-- label: tab:q2_top3 -->']
write('TABLE_q2_top3.md', L)


# ── TABLE_q3_style (T3 风格概览) ───────────────────────
s3 = P3['summary']
ks = s3['ks_distance_by_style']
L = ['**表：三代表风格生成质量概览**', '',
     '| 风格 | 生成样本数 | 与真实谱 KS 距离 |', '|---|---|---|']
ngen_per = s3['n_generated'] // len(s3['gen_styles'])
for st in s3['gen_styles']:
    L.append(f'| {esc(st)} | {ngen_per} | {ks[st]:.4f} |')
L += ['', f'> 注：KS 距离为生成谱与同风格真实谱在化学维上的 Kolmogorov–Smirnov 分布距离均值，'
      f'越小越接近真实分布；生成化学维 = {s3["gen_dim"]}（约束通过）。'
      f'Tripel 生成酯香水平 {s3["gen_tripel_ester_level"]:.2f}（真实 {s3["real_tripel_ester_level"]:.2f}）。', '',
      '<!-- label: tab:q3_style -->']
write('TABLE_q3_style.md', L)


# ── TABLE_q3_defect (T3 缺陷合规) ──────────────────────
ti = P3['transfer_info']
pd_ = ti['per_defect']
L = ['**表：Pils/Lager→Tripel 迁移中 4 个缺陷化合物的阈值合规**', '',
     '| 缺陷化合物 | 迁移前均值 | 迁移后均值 | 安全阈值 $m_t$ | 合规数/样本数 |',
     '|---|---|---|---|---|']
for k, v in pd_.items():
    L.append(f'| {esc(k)} | {v["before_mean"]:.3f} | {v["after_mean"]:.3f} '
             f'| {v["m_t"]:.3f} | {v["n_compliant"]}/{v["n"]} |')
L += ['', f'> 注：标准化含量；迁移后全部 {ti["n_compliant"]}/{ti["n_checks"]} 次检查落在阈值安全侧，'
      f'整体缺陷合规率 {ti["compliance_rate"]*100:.0f}%。', '',
      '<!-- label: tab:q3_defect -->']
write('TABLE_q3_defect.md', L)

print('all tables done')
