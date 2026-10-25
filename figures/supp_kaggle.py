# -*- coding: utf-8 -*-
"""supp_kaggle — Kaggle 公开集（stephenpolozoff/top-beer-information）外部旁证分析
仅作宏观对照，不逐行合并、不进入建模：
1) 两库规模/口径对比（网友评分+规格 vs 实验室化学谱+小组标准化分）；
2) 可比风格的 ABV / IBU 区间，用 Kaggle 大众库的 IQR 区间校验本文风格还原值（10**log10）落位。
输出 figures/supp_kaggle.json。"""
import os, sys, json
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = pd.read_csv(os.path.join(ROOT, '_tmp/kaggle/extracted/beer_data_set.csv'))
k['IBU'] = (k['Min IBU'] + k['Max IBU']) / 2.0
ka = k[(k['ABV'] >= 0.1) & (k['ABV'] <= 20)]          # 剔除 0% / 57.5% 等异常
ki = k[k['IBU'] > 0]

c = pd.read_csv(os.path.join(ROOT, 'user_data/1.csv'))
eth = [col for col in c.columns if 'ethanol' in col.lower()][0]
c['ABV'] = 10 ** c[eth]
c['IBU'] = 10 ** c['bitterness']
loc = c.groupby('tasting_category_fine')[['ABV', 'IBU']].median()

# 本文风格 -> Kaggle 风格（仅取明确可比项，不强凑）
MAP = {
    'Tripel': ['Tripel'],
    'Dubbel': ['Dubbel'],
    'Strong ale': ['Strong Ale - Belgian Dark', 'Strong Ale - Belgian Pale'],
    'Blond': ['Blonde Ale - Belgian'],
    'Saison': ['Farmhouse Ale - Saison'],
    'Pils/Lager': ['Pilsner - German', 'Pilsner - Bohemian / Czech'],
    'Wheat': ['Wheat Beer - Witbier'],
    'Stout/Porter': ['Stout - English', 'Stout - Foreign / Export'],
    'Brown': ['Brown Ale - Belgian Dark'],
    'Amber': ['Red Ale - American Amber / Red'],
    'Hoppy': ['IPA - Belgian'],
    'Kriek': ['Lambic - Fruit'],
    'Lambic': ['Lambic - Traditional', 'Lambic - Gueuze'],
    'Faro': ['Lambic - Faro'],
    'Fruitbeer': ['Fruit and Field Beer'],
    'Brett/cofermented': ['Brett Beer'],
}
ZH = {
    'Tripel': 'Tripel', 'Dubbel': 'Dubbel', 'Strong ale': '比利时烈性', 'Blond': '金色艾尔',
    'Saison': '季节啤', 'Pils/Lager': '皮尔森/拉格', 'Wheat': '小麦白啤',
    'Stout/Porter': '世涛/波特', 'Brown': '棕色艾尔', 'Amber': '琥珀红啤',
    'Hoppy': '酒花(IPA)', 'Kriek': '克里克', 'Lambic': '兰比克', 'Faro': '法柔',
    'Fruitbeer': '果啤', 'Brett/cofermented': '布雷特混酿',
}


def five(df, col):
    x = df[col].dropna().values
    if len(x) == 0:
        return None
    return [round(float(np.percentile(x, q)), 2) for q in (5, 25, 50, 75, 95)]


mapping = {}
for ls, ks in MAP.items():
    d = ka[ka['Style'].isin(ks)]
    di = ki[ki['Style'].isin(ks)]
    if len(d) == 0 or ls not in loc.index:
        continue
    la, li = float(loc.loc[ls, 'ABV']), float(loc.loc[ls, 'IBU'])
    fa = five(d, 'ABV'); fi = five(di, 'IBU')
    mapping[ls] = {
        'zh': ZH[ls], 'kaggle_styles': ks, 'n': int(len(d)),
        'local_abv': round(la, 2), 'kaggle_abv_five': fa,
        'abv_hit_iqr': bool(fa[1] <= la <= fa[3]),
        'abv_hit_p95': bool(fa[0] <= la <= fa[4]),
        'local_ibu': round(li, 2),
        'kaggle_ibu_med': (fi[2] if fi else None),
    }
n = len(mapping)
# 跨风格秩相关：本文实测中位 vs Kaggle 大众库中位（验证排序一致性）
from scipy.stats import spearmanr
lsa = [m['local_abv'] for m in mapping.values()]
ksa = [m['kaggle_abv_five'][2] for m in mapping.values()]
abv_rho = round(float(spearmanr(lsa, ksa).statistic), 3)
ibu_pairs = [(m['local_ibu'], m['kaggle_ibu_med']) for m in mapping.values()
             if m['kaggle_ibu_med'] is not None]
ibu_rho = round(float(spearmanr([p[0] for p in ibu_pairs], [p[1] for p in ibu_pairs]).statistic), 3)
n_above = sum(1 for m in mapping.values() if m['local_abv'] > m['kaggle_abv_five'][2])
out = {
    'source': {
        'name': 'Top Beer Information - Tasting Profiles (Kaggle, stephenpolozoff)',
        'url': 'https://www.kaggle.com/datasets/stephenpolozoff/top-beer-information',
        'n_rows': int(len(k)), 'n_styles': int(k['Style'].nunique()),
        'abv_median': round(float(ka['ABV'].median()), 2),
        'ibu_median': round(float(ki['IBU'].median()), 2),
        'rating_median': round(float(k['Ave Rating'].median()), 2),
        'rating_min': round(float(k['Ave Rating'].min()), 2),
        'rating_max': round(float(k['Ave Rating'].max()), 2),
    },
    'local': {'n_rows': 250, 'n_styles': 22,
              'abv_median': round(float(c['ABV'].median()), 2),
              'ibu_median': round(float(c['IBU'].median()), 2)},
    'mapping': mapping,
    'abv_hit_iqr': round(sum(m['abv_hit_iqr'] for m in mapping.values()) / n, 3),
    'abv_hit_p95': round(sum(m['abv_hit_p95'] for m in mapping.values()) / n, 3),
    'abv_spearman': abv_rho, 'ibu_spearman': ibu_rho,
    'n_local_above_kaggle_median': n_above,
    'n_compared': n, 'n_ibu_compared': len(ibu_pairs),
}
with open(os.path.join(ROOT, 'figures', 'supp_kaggle.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('supp_kaggle written; compared=%d abv_iqr=%.2f abv_p95=%.2f abv_rho=%.2f ibu_rho=%.2f above=%d'
      % (n, out['abv_hit_iqr'], out['abv_hit_p95'], abv_rho, ibu_rho, n_above))
for ls, m in mapping.items():
    f5 = m['kaggle_abv_five']
    print('%-16s ABV loc %.2f kaggle[P5..P95] %.1f..%.1f med %.1f iqr=%s p95=%s'
          % (ls, m['local_abv'], f5[0], f5[4], f5[2], m['abv_hit_iqr'], m['abv_hit_p95']))
