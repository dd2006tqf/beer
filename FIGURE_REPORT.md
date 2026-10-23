# 图表生成报告（paper-figure）

本步骤为 MathorCup 大数据 A 题（啤酒化学-感官建模）生成 **11 张数据图（350 DPI PNG）** 与
**5 张 Markdown 三线表**。所有数值均从 `figures/*.json` 真实结果读取，无手抄、无编造。
输出格式为 Word（.docx），故全部图为 PNG、全部表为 .md。

机器可读的图-数据绑定见 `figures/FIGURE_SOURCES.json`（已逐字段校验存在）。

## 一、数据图清单与证据溯源

| 图名 | 图型 | 问题/场景 | 生成脚本 | 数据文件::字段 | 统计量/不确定性 |
|---|---|---|---|---|---|
| fig_eda_style_pca | PCA 双标图(2 panel) | 数据探索：风格分布 + 化学谱可分性 | gen_fig_eda_style_pca.py | supp_eda.json::style_counts / pca_chem | 22 风格计数；231 维标准化后 SVD 前 2 主成分（方差解释 14.0%/7.9%） |
| fig_q1_missing_pattern | 缺失矩阵+条形 | 问题一数据处理：缺失结构 | gen_fig_q1_missing_pattern.py | supp_eda.json::missing | 列缺失率、63/250 含缺失行的 0/1 缺失矩阵 |
| fig_q1_pred_perf | 棒棒糖(双列) | 问题一结果：50 维可预测性排序 | gen_fig_q1_pred_perf.py | problem_1_results.json::fig_data.qwk_ranked / summary.mean_qwk_main | 分层 5 折 CV 的 QWK；参考线=全维均值 0.3663 |
| fig_q1_calibration | 散点+混淆热力(2 panel) | 问题一验证：代表维 F_hops_all | gen_fig_q1_calibration.py | problem_1_results.json::calibration | 250 样本连续预测 vs 真实（Pearson r）；0-6 等级混淆计数 |
| fig_q2_coexpr_network | 网络图 | 问题二模型：共表达图模块结构 | gen_fig_q2_coexpr_network.py | problem_2_results.json::fig_data.network_nodes/edges, graph | 度最高 60 节点 + 345 边；颜色=社区，大小=度（模块度 0.638） |
| fig_q2_top3_heatmap | 矩阵热力图 | 问题二结果：维×关键化合物重要度 | gen_fig_q2_top3_heatmap.py | problem_2_results.json::per_dim（Q1-top 12 维） | 融合入选权重 φ（仅 Top-3 命中处着色） |
| fig_q2_stability | 点+置信区间(双列) | 问题二稳定性 | gen_fig_q2_stability.py | problem_2_results.json::fig_data.top1_freq_ranked / summary.n_bootstrap | 500 次 bootstrap 入选频率 + Wilson 95% CI；跨方法 Jaccard |
| fig_q2_chem_sensory_corr | 相关矩阵热力图 | 问题二分析：化学-感官关联 | gen_fig_q2_chem_sensory_corr.py | supp_eda.json::chem_sensory_corr | 12 感官维 × 14 化合物 Pearson 相关（按 beer_id 对齐，n≥5） |
| fig_q3_style_radar | 雷达图 | 问题三结果：三风格感官画像 | gen_fig_q3_style_radar.py | problem_3_results.json::fig_data.radar | 取风格间方差最大的 12 感官维；CVAE 生成经 Q1 打分 |
| fig_q3_realvsgen | PCA 散点(2 panel) | 问题三验证：真实 vs 生成 | gen_fig_q3_realvsgen.py | problem_3_results.json::fig_data.pca / summary.ks_distance_by_style | 60 真实 + 90 生成样本同坐标系；KS≈0.36~0.41 |
| fig_q3_transfer_defect | 哑铃图 | 问题三迁移：缺陷阈值合规 | gen_fig_q3_transfer_defect.py | problem_3_results.json::fig_data.defect_dumbbell / transfer_info | 4 缺陷迁移前后均值 + 阈值 m_t；合规率 100% |

## 二、派生数据说明（supp_eda.json）

`figures/supp_prep_eda.py` 仅读取只读原始数据（`user_data/1.csv` 化学谱、`user_data/4.csv`
感官标准化值）与 `problem_2_results.json`，派生出 EDA 所需量（风格计数、化学谱 PCA、缺失模式、
化学-感官相关矩阵），输出到新文件 `figures/supp_eda.json`。**未修改任何上游结果，未重跑求解**。

## 三、结果表清单

| 表文件 | 对应 SPEC | 内容 | 数据来源 |
|---|---|---|---|
| TABLE_q1_model_cmp.md | — | Q1 主模型 vs 4 基线整体 QWK | problem_1_results.json::summary |
| TABLE_q1_perf.md | T1 | 代表性感官维 QWK/MAE/R²（前 18） | problem_1_results.json::per_dim |
| TABLE_q2_top3.md | T2 | 感官维 Top-3 化合物 + 稳定性（12 维） | problem_2_results.json::per_dim |
| TABLE_q3_style.md | T3 | 三风格 KS 距离 + 酯香水平 | problem_3_results.json::summary |
| TABLE_q3_defect.md | T3 | 迁移 4 缺陷阈值合规 | problem_3_results.json::transfer_info |

> 完整 50 维结果、150 行 Top-3、101 行生成谱见 `submission/` 下交付 CSV（正文表为代表性子集）。

## 四、质量检查

- `figure_check.sh` 代码检查：RC=0（无 CRITICAL 违规）。
- `figure_pdf_quality_check.py` 版面检查：RC=0（字体嵌入、印刷字号、文字边界、对比度通过）。
- 表格：无 .tex 残留，5 张 .md 均含分隔行、列对齐。
- 图内文字仅含必要数值/短锚点，解释性内容留给正文。

未发现需记录的上游问题（UPSTREAM_ISSUES.md 未创建）。
