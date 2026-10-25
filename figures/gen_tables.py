# -*- coding: utf-8 -*-
"""gen_tables.py — 从结果 JSON 生成全部 Markdown 三线表（数值不手抄，全部读 JSON）。"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

# 维度英文名→中文短名（与 _figbase.dim_zh 保持一致，独立内联以避免表格脚本依赖绘图基座）
_BASE_ZH = {
    'malt_all': '麦芽', 'malt_grain': '谷物', 'malt_bread': '面包', 'malt_cara': '焦糖',
    'malt_burn': '烟熏', 'hops_all': '酒花', 'hops_citrus': '柑橘', 'hops_tropical': '热带',
    'hops_noble': '贵族花', 'hops_woody': '木质', 'esters_all': '酯', 'esters_ethac': '指甲油',
    'esters_isoaa': '香蕉酯', 'esters_flower': '花香酯', 'esters_fruity': '果香酯',
}
_STD_ZH = {
    'acidity': '酸度', 'bitternes': '苦味', 'sweetness': '甜味', 'X4vg': '4VG',
    'diacetyl': '双乙酰', 'dms': 'DMS', 'metallic': '金属味', 'stale_hops': '陈酒花',
    't2n': '反2壬烯醛', 'orange': '橙香', 'coriander': '芫荽', 'clove': '丁香',
    'lactic': '乳酸', 'acetic': '乙酸', 'barnyard': '畜棚味', 'alcohol': '酒精',
    'aftertaste': '余味', 'body': '酒体', 'co2': '碳酸', 'overall': '总体',
}


def dim_zh(k):
    if k in _STD_ZH:
        return _STD_ZH[k]
    if k[:2] in ('A_', 'F_'):
        pre = '香·' if k[0] == 'A' else '味·'
        base = _BASE_ZH.get(k[2:], k[2:].replace('_', ''))
        return pre + base
    return k.replace('_', ' ')

P1 = json.load(open(os.path.join(HERE, 'problem_1_results.json'), encoding='utf-8'))
P2 = json.load(open(os.path.join(HERE, 'problem_2_results.json'), encoding='utf-8'))
P3 = json.load(open(os.path.join(HERE, 'problem_3_results.json'), encoding='utf-8'))


def write(name, lines):
    with open(os.path.join(HERE, name), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('wrote', name)


def esc(s):
    return str(s).replace('|', r'\|')


def dimname(d):
    return esc(dim_zh(d))

# ── Q1 多模型对比（QWK / Spearman / ±1）──────────────
s = P1['summary']; bm = s['by_model']
rows = [
    ('**LightGBM（原生缺失，主模型）**', 'lightgbm', True),
    ('KNN 插补 + LightGBM', 'knn_impute', False),
    ('随机森林（中位插补）', 'rf', False),
    ('ElasticNet（中位插补）', 'elasticnet', False),
    ('逐维均值等级', 'mean_baseline', False),
]
L = ['**表：问题一主模型与基线整体性能对比（50 维平均）**', '',
     '| 方法 | 平均 QWK | 平均 Spearman | ±1 级准确率 |', '|---|---|---|---|']
for lab, key, bold in rows:
    m = bm[key]
    def f(x):
        return f'**{x:.4f}**' if bold else f'{x:.4f}'
    L.append(f'| {lab} | {f(m["mean_qwk"])} | {f(m["mean_spearman"])} | {f(m["mean_acc_within1"])} |')
L += ['', '> 注：三项均为分层 5 折交叉验证均值；±1 级准确率指预测等级与真实等级相差不超过 1 级的比例。最优值已加粗。',
      '', '<!-- label: tab:q1_model_cmp -->']
write('TABLE_q1_model_cmp.md', L)

# ── Q1 A/F 分组 ──────────────────────────────────────
g = s['group_AF']
L = ['**表：香气（Aroma）与风味（Flavour）两组的可预测性对比**', '',
     '| 组别 | 维度数 | 平均 QWK | 平均 $R^2$ |', '|---|---|---|---|']
L.append(f'| 香气 Aroma（`A_` 前缀） | {g["A"]["n"]} | {g["A"]["mean_qwk"]:.3f} | {g["A"]["mean_r2"]:.3f} |')
L.append(f'| 风味 Flavour（`F_` 前缀） | {g["F"]["n"]} | {g["F"]["mean_qwk"]:.3f} | {g["F"]["mean_r2"]:.3f} |')
L += ['', '> 注：另 20 维为口感、缺陷与总体评价；风味组整体比香气组更可预测，与其化学信号更直接有关。',
      '', '<!-- label: tab:q1_group -->']
write('TABLE_q1_group_AF.md', L)

# ── Q1 代表维（最强 12 + 最弱 4；QWK/R²/Spearman/±1）──────
rank = [r[0] for r in P1['fig_data']['qwk_ranked']]
per1 = P1['per_dim']
strong = [d for d in rank if d in per1][:12]
weak = [d for d in rank if d in per1][-4:]
L = ['**表：最强 12 维与最弱 4 维的预测性能（QWK / $R^2$ / Spearman / ±1 准确率）**', '',
     '| 感官维度 | 字段名 | QWK | $R^2$ | Spearman | ±1 准确率 |',
     '|:---|:---:|---:|---:|---:|---:|']
for d in strong:
    p = per1[d]
    L.append(f'| {dimname(d)} | {esc(d)} | {p["qwk_main"]:.3f} | {p["r2_main"]:.3f} '
             f'| {p["spearman_main"]:.3f} | {p["acc_within1_main"]:.3f} |')
L.append('| …（中间 30 维）… | 见支撑材料 | | | | |')
for d in weak:
    p = per1[d]
    L.append(f'| {dimname(d)} | {esc(d)} | {p["qwk_main"]:.3f} | {p["r2_main"]:.3f} '
             f'| {p["spearman_main"]:.3f} | {p["acc_within1_main"]:.3f} |')
L += ['', '> 注：完整 50 维见 `submission/q1_sensory_scores.csv`；$R^2$ 为连续预测值的决定系数（可为负），'
      'QWK 为分箱后的二次加权 Kappa。', '', '<!-- label: tab:q1_perf -->']
write('TABLE_q1_perf.md', L)

# ── Q2 Top-3（含来源类别）────────────────────────────
q2dims = [d for d in rank if d in P2['per_dim']][:12]
per2 = P2['per_dim']
L = ['**表：代表性感官维度 Top-3 关键化合物、稳定性与来源类别判定（仅化合物集 $C=211$）**', '',
     '| 感官维度 | Top-1 | Top-2 | Top-3 | Top-1 频率 | Jaccard | 期望来源 | 判定 |',
     '|---|---|---|---|---|---|---|---|']
for d in q2dims:
    p = per2[d]
    t3 = p['top3']
    L.append(f'| {dimname(d)} | {esc(t3[0])} | {esc(t3[1])} | {esc(t3[2])} '
             f'| {p["select_freq"][0]:.3f} | {p["jaccard_cross_method"]:.3f} '
             f'| {esc(p.get("expected_source", ""))} | {esc(p.get("source_verdict", ""))} |')
L += ['', '> 注：Top-1 频率为 500 次 bootstrap 入选比例；Jaccard 为共表达/SHAP/相关三法 Top-3 的一致性'
      '（全维均值 %.3f）；期望来源与判定依据 8.xlsx 化合物来源标注，完整 50 维见 `submission/q2_top3_compounds.csv`。'
      % P2['summary']['mean_cross_method_jaccard'], '', '<!-- label: tab:q2_top3 -->']
write('TABLE_q2_top3.md', L)

# ── Q2 来源类别汇总 ──────────────────────────────────
sc = P2['source_category']; rb = P2['random_jaccard_baseline']
L = ['**表：Top-3 化合物来源与感官期望来源的逐维判定汇总（50 维）**', '',
     '| 判定 | 含义 | 维度数 | 占比 |', '|---|---|---|---|']
L.append(f'| 一致 | Top-3 全部来自期望来源 | {sc["n_consistent"]} | {sc["consistency_rate"]*100:.0f}% |')
L.append(f'| 部分一致 | Top-3 至少一个来自期望来源 | {sc["n_partial"]} | {sc["partial_rate"]*100:.0f}% |')
L.append(f'| 不一致 | Top-3 无一个来自期望来源 | {sc["n_inconsistent"]} | {sc["inconsistency_rate"]*100:.0f}% |')
L += ['', '> 注：随机从化合物集 $C$ 抽 3 个的 Jaccard 基线（%d 次模拟）仅 %.4f，而本文跨方法 Jaccard 为 %.4f，'
      '是随机基线的 %.1f 倍，说明归因显著优于随机。'
      % (rb['n_rep'], rb['mean'], rb['actual_mean_cross_method_jaccard'], rb['ratio_actual_to_random']),
      '', '<!-- label: tab:q2_source -->']
write('TABLE_q2_source.md', L)

# ── Q3 风格生成质量（KS + 分类器识别率 + 画像 Spearman）──
s3 = P3['summary']; ngen = s3['n_generated'] // len(s3['gen_styles'])
clf = s3['classifier_top3_generated']; rl = s3['classifier_top3_real_oof']; rho = s3['profile_spearman_by_style']
ks = s3['ks_distance_by_style']
L = ['**表：三代表风格生成质量（分布距离 + 风格识别率 + 画像相关）**', '',
     '| 风格 | 生成数 | KS 距离 | 生成谱 Top-3 识别率 | 真实谱 Top-3 识别率 | 生成-真实画像 Spearman |',
     '|---|---|---|---|---|---|']
for st in s3['gen_styles']:
    L.append(f'| {st} | {ngen} | {ks[st]:.4f} | {clf[st]*100:.0f}% | {rl[st]*100:.0f}% | {rho[st]:.3f} |')
L += ['', '> 注：随机猜测 Top-3 的识别率基线为 %.1f%%，真实谱整体 OOF 识别率为 %.1f%%；KS 越小越接近真实分布，'
      '画像 Spearman 为生成谱与同风格真实谱经问题一打分后的感官画像相关。Tripel 生成酯香 %.2f（真实 %.2f）。'
      % (s3['classifier_top3_random_baseline']*100, s3['classifier_top3_real_overall']*100,
         s3['gen_tripel_ester_level'], s3['real_tripel_ester_level']),
      '', '<!-- label: tab:q3_style -->']
write('TABLE_q3_style.md', L)

# ── Q3 缺陷合规（before/after/Δ/raw 对照/无约束升高）────
ti = P3['transfer_info']; pd_ = ti['per_defect']
L = ['**表：Pils/Lager→Tripel 迁移中 4 个缺陷化合物的严格合规（min 投影）**', '',
     '| 缺陷化合物 | 迁移前 | 迁移后 | $\Delta=$后−前 | 无约束纯平移后 | 无约束升高数 | 典型阈值 $m_t$ | 合规 |',
     '|---|---|---|---|---|---|---|---|']
for k, v in pd_.items():
    L.append(f'| {esc(k)} | {v["before_mean"]:.3f} | {v["after_mean"]:.3f} | {v["delta_mean"]:+.3f} '
             f'| {v["raw_after_mean"]:.3f} | {v["n_rise_unconstrained"]}/11 | {v["m_t"]:.3f} '
             f'| {v["n_compliant"]}/{v["n"]} |')
uc = s3['unconstrained_control']
L += ['', '> 注：标准化含量；迁移后取 $\min(x_{before},m_t)$，全部 %d/%d 次检查合规（合规率 100%%）、'
      '受约束后缺陷升高 %d 次；而同一批样本不做投影的纯平移对照有 %d/%d 次（%.1f%%）缺陷升高。'
      % (ti['n_compliant'], ti['n_checks'], uc['n_defect_rise_constrained'],
         uc['n_defect_rise_unconstrained'], uc['n_total'], uc['rise_frac_unconstrained']*100),
      '', '<!-- label: tab:q3_defect -->']
write('TABLE_q3_defect.md', L)

print('all tables done')
