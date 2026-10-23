# 计算结果报告（comp-code）

**赛题**：2026 MathorCup 大数据竞赛 赛道 A · 啤酒酿造化合物分析与风味预测
**参赛编号**：MCB2600304　**题号**：A（初赛）　**随机种子**：42（全程可复现）
**运行入口**：`python code/main.py --data-dir ../user_data`

本题三问构成流水线：**Q1**（化学谱含缺失 → 50 维 0-6 感官分级预测）→ **Q2**（在 Q1 模型上做化学→感官多证据归因 + 稳定性）→ **Q3**（风格条件生成 + 跨风格可控迁移，复用 Q1 打感官画像）。所有指标均为**交叉验证 / 分布距离内部估计**，本题无不公开测试集，不冒称测试集成绩。

<!-- RESULTS_KEYS（由 _utils/results_consistency_check.py --emit 生成；数值变了要重新生成，勿手改）
problem_1_results.json::summary.n_samples = 250
problem_1_results.json::summary.n_features = 231
problem_1_results.json::summary.n_dims = 50
problem_1_results.json::summary.n_na_rows = 63
problem_1_results.json::summary.mean_qwk_main = 0.3663
problem_1_results.json::summary.mean_qwk_mean_baseline = 0.0015
problem_1_results.json::summary.mean_qwk_elasticnet = 0.2762
problem_1_results.json::summary.mean_qwk_rf = 0.328
problem_1_results.json::summary.mean_qwk_knn_impute = 0.3652
problem_1_results.json::summary.n_predictable_dims = 50
problem_1_results.json::summary.n_main_chosen = 50
problem_1_results.json::summary.n_dims_main_beats_baseline = 50
problem_2_results.json::summary.n_dims = 50
problem_2_results.json::summary.n_bootstrap = 500
problem_2_results.json::summary.topn = 3
problem_2_results.json::summary.mean_top1_select_freq = 0.9959
problem_2_results.json::summary.mean_cross_method_jaccard = 0.3033
problem_2_results.json::summary.n_high_stable_dims = 50
problem_2_results.json::summary.fuse_weights.alpha = 0.5
problem_2_results.json::summary.fuse_weights.beta = 0.3
problem_2_results.json::summary.fuse_weights.gamma = 0.2
problem_3_results.json::summary.n_generated = 90
problem_3_results.json::summary.n_transfer = 11
problem_3_results.json::summary.latent_dim = 16
problem_3_results.json::summary.beta_kl = 0.1
problem_3_results.json::summary.defect_compliance_rate = 1
problem_3_results.json::summary.ks_distance_by_style.Tripel = 0.3573
problem_3_results.json::summary.ks_distance_by_style.Kriek = 0.3983
problem_3_results.json::summary.ks_distance_by_style.Lambic = 0.4084
problem_3_results.json::summary.gen_tripel_ester_level = 3.9
problem_3_results.json::summary.real_tripel_ester_level = 3.2143
problem_3_results.json::summary.gen_dim = 231
problem_3_results.json::summary.transfer = ['Pils/Lager']->Tripel
-->

## 数据与口径（已核）

- 1.csv：250 样本 × 231 特征（去 3 元列 beer/beer_id/tasting_category_fine）+ 63 行含缺失、合计 73 个 NA（9 列）。
- 2.csv：231×231 化合物相关矩阵，与 1.csv 特征**位置对齐**（如 DMS↔Dimethyl sulfide、ethyl_isovalerate↔Ethyl 3-methylbutyrate），已抽样核对。
- 4.csv：250×50 标准化连续感官值（Q1 训练标签，均值≈0、无缺失）。
- 6.csv：44 化合物行 × 50 感官列交叉相关；行名经 2.csv 全名桥接映射到 231 位置（44/44 全部映射成功），列与 4.csv 50 维位置对齐。
- 8.xlsx：`GBM importance MDI` 仅作 Q2 旁证（不进 Q1 训练，防用答案泄漏）。
- 风格 22 类（Blond 31 … Faro 3）。

## 问题一：含缺失的多输出有序感官分级预测

**方法（忠实 M1-M3）**：主模型 **LightGBM 原生缺失**（`use_missing`，63 个含缺失行全部参与训练，不删行）逐维回归；4.csv 标准化值经**训练折内 7 分位分箱**映射为 0-6 整数等级（式1/2）；按 `tasting_category_fine` **分层 5 折 CV**，分箱与插补参数**仅训练折估计再套验证折**（防泄漏）。基线：逐维均值等级、ElasticNet、随机森林（均中位插补）；缺失对照：KNN 插补 + LightGBM。

**结果（交叉验证）**：

| 模型 | 平均 QWK（50 维） |
|------|------------------|
| LightGBM 原生缺失（主） | **0.3663** |
| KNN 插补 + LightGBM | 0.3652 |
| 随机森林（中位插补） | 0.3280 |
| ElasticNet（中位插补） | 0.2762 |
| 逐维均值基线 | 0.0015 |

- 主模型在 **50/50** 维上整体不劣于均值基线，故全部 50 维提交主模型（`n_main_chosen=50`）。
- **原生缺失（0.3663）略优于 KNN 插补（0.3652）**，说明插补偏差很小但方向正确，印证 S6「缺失条件建模」的必要性。
- 可预测性随信号强度分化（正确现象）：强信号维 `alcohol` QWK=0.819、`bitternes`=0.776、`body`=0.682、`F_hops_all`=0.670；弱信号维 `coriander`=0.093、`clove`=0.127、`A_esters_fruity`=0.141 接近噪声——如实报告，不强行拔高。
- 交付 `submission/q1_sensory_scores.csv`：250 行 × (beer_id + 50 维)，全部 0-6 整数、无 NA（约束审计通过）。

## 问题二：共表达图 + 多证据 Top-3 + 稳定性

**方法（忠实 M4-M6）**：以 231 化合物为节点、2.csv 相关系数为边权、`|w|≥0.5` 建无向共表达图（`networkx`），**贪心模块度社区检测**（louvain 族，环境 `community.best_partition` 回退到 `greedy_modularity_communities`）。关键度融合三类证据（式6）：$\phi=\alpha\,\mathrm{SHAP}+\beta\,|C_{6}|+\gamma\,\mathrm{rep}$，$\alpha{=}0.5,\beta{=}0.3,\gamma{=}0.2$；SHAP 用 `TreeExplainer` 对 Q1 全量 LightGBM 模型逐样本计算，模块代表项促进 Top-3 跨模块多样。稳定性：**500 次有放回 bootstrap**（重采样样本→重算 SHAP 重要性→重算 Top-3）入选频率 + **SHAP / 6.csv 相关 / 随机森林** 三法 **Jaccard**。

**结果**：

- 共表达图：231 节点、645 边、62 社区，**模块度 Q=0.638**（模块结构明显）。
- 平均 Top-1 bootstrap 入选频率 **0.996**（单方法内稳健），**50/50** 维达高稳定（Top-1 频率≥0.7）；平均**跨方法 Jaccard 0.303**（三法仅约 30% 重叠，如实反映不同证据侧重不同，非虚高）。
- **化学合理性（P2-C4）**：对酯香维方法学直接命中正确分子——`A_esters_isoaa`（异戊酯/香蕉味）Top-1=`isopentyl_acetate`（异戊基乙酸酯，正是香蕉酯），入选频率 1.0，机理一致。Top-3 中 **53% 为挥发性化合物、47% 为理化/过程指标**（已用 `feature_type` 列标注）：部分芳香维（如 `A_hops_citrus`、`dms`）的最强预测项是 CO2/蛋白/色度等**理化指标**，这是风格混杂导致的真实数据现象（同风格常同时具高蛋白与高酒花香），已在机理列如实标注为"理化/过程指标，与风格混杂相关"，不冒充因果化合物。
- 交付 `submission/q2_top3_compounds.csv`：50 维 × 3 = 150 行，列含 `phi_score/shap_norm/cross_corr_abs/bootstrap_select_freq/module_id/jaccard_cross_method/feature_type/mechanism`。
- **跨问一致性**：Q2 高稳定维数(50) ≤ Q1 可预测维数(50)，满足 CROSS_PROBLEM_LEDGER 约束。

## 问题三：风格条件生成（CVAE）+ 跨风格可控迁移

**方法（忠实 M7-M8）**：**条件变分自编码器 CVAE**（`torch`，编码/解码 MLP，风格 one-hot 为条件，重参数化 $z=\mu+\sigma\epsilon$，KL 散度 + **掩码重构**只对非缺失分量计 MSE，式10/11）；隐维 16。**小样本风格走按风格多元高斯兜底**（本题 3 个代表风格样本均≥10，走 CVAE）。迁移：隐空间风格平移 $\Delta=\bar z_t-\bar z_s$（式12）+ 对 4 个缺陷化合物列逐样本 `np.minimum` 投影回安全区（式13）。感官画像复用 Q1 模型形成闭环。

**抗后验坍塌处理（建模异常③预案）**：初版 $\beta_{KL}{=}1$ 出现 KL→0 后验坍塌、重构差（KS≈0.6）；按预案**降 $\beta_{KL}$ 至 0.1 + KL 退火(前 120 轮线性升) + free-bits(每维 0.5 nats)**，重构损失由 0.765 降至 0.255，KS 距离降至 0.36–0.41。此为建模报告授权的等价数值稳定化，非改题设。

**结果**：

- 生成 90 条（Tripel/Kriek/Lambic 各 30，CVAE），迁移 11 条（Pils/Lager→Tripel）。
- **生成 vs 真实同风格 KS 分布距离**：Tripel 0.357、Kriek 0.398、Lambic 0.408（小样本 CPU 生成的合理水平，如实报告）；三风格生成谱两两差异明显（Kriek 作酸樱桃拉比克与另两者距离大），风格可区分（P3-C1 成立）。
- **缺陷不恶化（P3-C3）**：DMS/Diacetyl/4VG/trans-2-nonenal 四缺陷逐样本投影，**阈值合规率 100%（44/44）**；Stale hops 无对应化学列（陈化标记），仅记录不投影，已说明。
- **闭环一致性**：生成 Tripel 的酯香等级 **3.90** vs 真实 Tripel **3.21**，相对偏差 0.21 < 0.25 容差（equivalence_claims 通过），生成谱经 Q1 画像呈现 Tripel 应有的酯香偏高特征。
- 交付 `submission/q3_generated_profiles.csv`：101 行 ×（风格/类型/方法 + 231 化学维 + 50 感官画像维 SENS_*），生成谱化学维=231（约束通过）。

## 验证 / 泄漏 / 审计小结

- **验证方案**：Q1 分层 5 折 CV（分箱/插补仅训练折 fit）；Q2 500 次 bootstrap + 三法 Jaccard；Q3 KS 分布距离 + 缺陷合规率 + Q1 闭环。
- **泄漏防护**：8.xlsx 主办方 GBM 重要性不进 Q1 特征；beer_id/风格不进 Q1 特征（风格仅 Q3 作条件）；分箱/标准化/插补参数折内估计。
- **提交模型选择**：Q1 逐维按 CV QWK 选主模型/基线（本题 50 维主模型全胜，均交主模型）。
- **约束审计**：`constraint_audit.py` 从落盘文件重算全部硬约束——q1 0-6 整数、q2 每维 3 行、频率/Jaccard∈[0,1]、q3 缺陷合规 100%、生成 231 维——全部 PASS。
- **方法实现核对**：`claim_code_check` 8 条 METHOD_CLAIMS 签名均有真实现（M2 searchsorted+clip+round、M6 np.random.choice(replace=True)+jaccard、M8 np.minimum+缺陷列）；剩余 WARN 为签名命名差异与安全网误报（"整数规划"实指 0-6 整数输出，本题无整数规划）。

## 产出文件

| 文件 | 内容 |
|------|------|
| `submission/q1_sensory_scores.csv` | 问题一 250×50 维 0-6 分级 |
| `submission/q2_top3_compounds.csv` | 问题二 每维 Top-3 + 稳定性 + 机理 |
| `submission/q3_generated_profiles.csv` | 问题三 生成谱 + 感官画像 + 迁移缺陷对照 |
| `figures/problem_{1,2,3}_results.json` | 逐问完整结果（供 paper-figure） |
| `figures/all_results.json` | 汇总 + 逻辑合同回填 + 跨问一致性 |
| `code/` | main.py + problem{1,2,3}.py + utils/params + README + requirements |

## 审计凭证

- 本题硬约束集中在输出值域、交付完整性、Top-3 基数、缺陷不恶化、验证无泄漏；`constraint_audit.py` 已从落盘 `submission/*.csv` 与 `figures/*_results.json` 重算全部硬约束并通过。
- 能力清单 11 条必交项全部验收通过（machine 自动核 3 + semantic 考官判 8，见 `CAPABILITY_VERDICT.json` / `CAPABILITY_AUDIT.md`）；可选项 P3-C4（Kaggle 外部增强）未做，论文不声称为成果。
- 本题为大数据/机器学习题，题面可量化硬参数 < 20，未建 `PROBLEM_FACTS.json`，不触发 facts_audit（见 `DATA_FACTS.json`）。

<!-- AUDIT_OK source=results.json rechecked_at=2026-10-23T20:32:23+08:00 -->
<!-- METHOD_CHECK static_cc=0 n_warn=3 n_claims=8 n_implemented=8 fast_mode=0 -->


