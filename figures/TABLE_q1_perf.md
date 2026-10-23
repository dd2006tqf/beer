**表：代表性感官维度预测性能（交叉验证 QWK / MAE / $R^2$，按 QWK 降序取前 18）**

| 感官维度 | QWK | MAE | $R^2$ | 选用模型 |
|---|---|---|---|---|
| 酒精（alcohol） | 0.819 | 0.852 | 0.713 | lightgbm |
| 苦味（bitternes） | 0.776 | 0.896 | 0.634 | lightgbm |
| 酒体（body） | 0.682 | 1.076 | 0.525 | lightgbm |
| 味·酒花（F_hops_all） | 0.670 | 1.120 | 0.505 | lightgbm |
| 余味（aftertaste） | 0.651 | 1.172 | 0.468 | lightgbm |
| 味·麦芽（F_malt_all） | 0.616 | 1.220 | 0.456 | lightgbm |
| 味·贵族花（F_hops_noble） | 0.602 | 1.240 | 0.391 | lightgbm |
| 香·麦芽（A_malt_all） | 0.601 | 1.220 | 0.447 | lightgbm |
| 甜味（sweetness） | 0.600 | 1.216 | 0.390 | lightgbm |
| 香·酒花（A_hops_all） | 0.573 | 1.244 | 0.328 | lightgbm |
| 味·酯（F_esters_all） | 0.544 | 1.312 | 0.334 | lightgbm |
| 碳酸（co2） | 0.537 | 1.356 | 0.314 | lightgbm |
| 香·贵族花（A_hops_noble） | 0.524 | 1.312 | 0.292 | lightgbm |
| 香·焦糖（A_malt_cara） | 0.519 | 1.332 | 0.340 | lightgbm |
| 味·面包（F_malt_bread） | 0.510 | 1.364 | 0.269 | lightgbm |
| 味·指甲油（F_esters_ethac） | 0.497 | 1.408 | 0.254 | lightgbm |
| 4VG（X4vg） | 0.468 | 1.488 | 0.200 | lightgbm |
| 味·焦糖（F_malt_cara） | 0.459 | 1.416 | 0.246 | lightgbm |

> 注：共 50 维，此处列交叉验证 QWK 最高的 18 维；完整 50 维结果见支撑材料 `submission/q1_sensory_scores.csv`。QWK 为二次加权 Kappa，$R^2$ 为连续预测值的决定系数（可为负，表示弱于常数预测）。

<!-- label: tab:q1_perf -->
