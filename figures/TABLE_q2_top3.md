**表：代表性感官维度 Top-3 关键化合物、稳定性与来源类别判定（仅化合物集 $C=211$）**

| 感官维度 | Top-1 | Top-2 | Top-3 | Top-1 频率 | Jaccard | 期望来源 | 判定 |
|---|---|---|---|---|---|---|---|
| 酒精 | ethyl_octanoate | acetaldehyde | MeSH | 1.000 | 0.400 | Yeast | 一致 |
| 苦味 | ethyl_octanoate | MeSH | DMS | 1.000 | 0.667 | Others | 不一致 |
| 酒体 | isobutanol | ethyl_octanoate | MeSH | 1.000 | 0.133 | Unknown | 不一致 |
| 味·酒花 | ethyl_octanoate | DMS | ethyl_hexanoate | 1.000 | 0.400 | Hops | 不一致 |
| 余味 | ethyl_octanoate | acetaldehyde | ethyl_isovalerate | 1.000 | 0.400 | Unknown | 不一致 |
| 味·麦芽 | acetaldehyde | MeSH | ethyl_decanoate | 1.000 | 0.200 | Malt | 不一致 |
| 味·贵族花 | ethyl_octanoate | ethyl_hexanoate | DMS | 1.000 | 0.300 | Hops | 不一致 |
| 香·麦芽 | acetaldehyde | octyl_acetate | MeSH | 1.000 | 0.167 | Malt | 不一致 |
| 甜味 | ethyl_decanoate | octyl_acetate | alpha.humulene | 1.000 | 0.200 | Others | 不一致 |
| 香·酒花 | ethyl_octanoate | DMS | linalool | 1.000 | 0.200 | Hops | 部分一致 |
| 味·酯 | ethyl_acetate | phenethyl_alcohol | acetaldehyde | 1.000 | 0.400 | Yeast | 一致 |
| 碳酸 | ethyl_octanoate | ethyl_hexanoate | MeSH | 1.000 | 0.500 | Yeast | 一致 |

> 注：Top-1 频率为 500 次 bootstrap 入选比例；Jaccard 为共表达/SHAP/相关三法 Top-3 的一致性（全维均值 0.186）；期望来源与判定依据 8.xlsx 化合物来源标注，完整 50 维见 `submission/q2_top3_compounds.csv`。

<!-- label: tab:q2_top3 -->
