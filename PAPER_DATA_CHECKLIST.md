# 论文数据真实性核对清单（数据原料）

**模式**: DOCX
**JSON 源**: all_results.json, problem_1_results.json, problem_2_results.json, problem_3_results.json
**JSON 数据条目**: 1997
**已生成的 TABLE 文件**: 5 个

---

## 自检步骤（请你按以下顺序执行）

**重要原则**：本工作区的实验/分析阶段已经把所有真实数据存到 `figures/*.json`，
并由 paper-figure 步骤渲染成 `figures/TABLE_*.tex|md`。
**论文数据应能追溯到这些文件或题设，并允许有明确计算依据的派生量、单位换算及舍入。未直接匹配不等于编造。**

### 第 1 步：识别论文中的「数据性数字」

打开你的论文文件，逐章扫描：

- ✅ **需要核对的**：表格里的所有单元格数字、正文里引用实验结果的数字（如 "RMSE 达到 0.023"、"准确率 94%"、"最优解 295.83"、"R² 为 0.94"）
- ⏭️ **不需要核对的**（叙述里自然出现的数字）：
    - 章节编号、列号、引用 [1][2,3]、图编号「图 3-1」
    - 年份「2024 年」、日期「3 月 5 日」
    - 公式本身的数学常数与下标（如 `$\frac{1}{2}$`、`$x_1$`）；但写在公式里的结果值（如 `$R^2=0.94$`、`$Z^*=295.83$`）仍要核对
    - 算法描述里的步骤数「分 5 步」
    - 文献综述里别人论文的数字

### 第 2 步：对每个「数据性数字」核对

对照下方的 JSON 数据清单和 TABLE 文件全文：

1. **能在数据清单/TABLE 文件里找到一致的数字（含正常舍入）** → ✅ 真实，跳过
2. **清单里同一数据字段的值与论文不一致**（如 RMSE 真实是 0.023，论文写的 0.999） → 以 JSON 原值为准改正文，**禁止反向操作**（禁止改 JSON）
3. **清单里没找到这个数字** → 按顺序排除，不要直接删：
   - 清单标了「省略中间 N 项」的列表 → 直接读原 JSON 该路径核对
   - 有明确公式的派生量（百分比 = 子集/总数 ×100、差值、比值、单位换算）或题设参数 → 检查派生是否正确
   - 以上都不是 → 才是无依据的数字：改成有依据的值，或删掉该说法
   - ⛔ 不要为了「对上清单」把正确的数改成清单里的近似值或别的字段的值

### 第 3 步：表格优先用预生成的 TABLE 文件

如果论文里手抄了表格内容，**优先改成** `cat figures/TABLE_*.md >> paper/main.md` 直接嵌入（已经从 JSON 渲染好，不会出错）。

### 第 4 步：自检完成后登记独立回执

后置自检使用本轮任务指定的 `.mh/quality/data-review-ack-*.txt` 和确认值；不要将确认值写入论文。
如果本轮写作上下文仍明确要求兼容旧注释，必须在最终编译之前完成；编译之后不得为登记状态再次改源码。
没有本轮确认值时不要复制旧回执或自行编造；系统只接受与当前内容绑定的有效核对。

**判断原则**：
- 以 JSON 为准修论文，禁止反向修 JSON
- 不必把 JSON 中的每个数字都搬到论文里——只关心论文里出现的数字是否真实
- 不确定某个数字是不是数据 → 当成数据核对一遍，确认能找到来源就行

---

## 图表来源与论断对应（并入本次核对，不启动额外模型轮次）

数字出现过不等于支持当前论断。逐图核对数据所属问题、场景、参数、样本量和统计量；
跨问题引用允许，但必须解释可迁移的结论。一个概率水平的收敛曲线不能直接证明另一个临界点可靠。
下面仅列静态识别的真实文件引用，不代表已经验证数学结论；动态路径请按生成脚本补查。

| 图 | 生成脚本 | 可观察的数据来源 |
|---|---|---|
| fig_eda_style_pca | figures/gen_fig_eda_style_pca.py | 动态来源，需按脚本定位 |
| fig_q1_calibration | figures/gen_fig_q1_calibration.py | 动态来源，需按脚本定位 |
| fig_q1_missing_pattern | figures/gen_fig_q1_missing_pattern.py | 动态来源，需按脚本定位 |
| fig_q1_pred_perf | figures/gen_fig_q1_pred_perf.py | 动态来源，需按脚本定位 |
| fig_q2_chem_sensory_corr | figures/gen_fig_q2_chem_sensory_corr.py | 动态来源，需按脚本定位 |
| fig_q2_coexpr_network | figures/gen_fig_q2_coexpr_network.py | 动态来源，需按脚本定位 |
| fig_q2_stability | figures/gen_fig_q2_stability.py | 动态来源，需按脚本定位 |
| fig_q2_top3_heatmap | figures/gen_fig_q2_top3_heatmap.py | 动态来源，需按脚本定位 |
| fig_q3_realvsgen | figures/gen_fig_q3_realvsgen.py | 动态来源，需按脚本定位 |
| fig_q3_style_radar | figures/gen_fig_q3_style_radar.py | 动态来源，需按脚本定位 |
| fig_q3_transfer_defect | figures/gen_fig_q3_transfer_defect.py | 动态来源，需按脚本定位 |
| tables | figures/gen_tables.py | figures/problem_1_results.json, figures/problem_2_results.json, figures/problem_3_results.json |

## JSON 真实数据清单

### `all_results.json`（45 条）

| 数据路径 | 数值 |
|---|---|
| `problem_id` | `A` |
| `team_id` | `MCB2600304` |
| `seed` | 42 |
| `q1.n_samples` | 250 |
| `q1.n_features` | 231 |
| `q1.n_dims` | 50 |
| `q1.n_na_rows` | 63 |
| `q1.mean_qwk_main` | 0.3663 |
| `q1.mean_qwk_mean_baseline` | 0.0015 |
| `q1.mean_qwk_elasticnet` | 0.2762 |
| `q1.mean_qwk_rf` | 0.328 |
| `q1.mean_qwk_knn_impute` | 0.3652 |
| `q1.n_predictable_dims` | 50 |
| `q1.n_main_chosen` | 50 |
| `q1.n_dims_main_beats_baseline` | 50 |
| `q2.n_dims` | 50 |
| `q2.n_bootstrap` | 500 |
| `q2.topn` | 3 |
| `q2.mean_top1_select_freq` | 0.9959 |
| `q2.mean_cross_method_jaccard` | 0.3033 |
| `q2.n_high_stable_dims` | 50 |
| `q2.fuse_weights.alpha` | 0.5 |
| `q2.fuse_weights.beta` | 0.3 |
| `q2.fuse_weights.gamma` | 0.2 |
| `q3.n_generated` | 90 |
| `q3.n_transfer` | 11 |
| `q3.gen_styles[0]` | `Tripel` |
| `q3.gen_styles[1]` | `Kriek` |
| `q3.gen_styles[2]` | `Lambic` |
| `q3.transfer` | `['Pils/Lager']->Tripel` |
| `q3.latent_dim` | 16 |
| `q3.beta_kl` | 0.1 |
| `q3.defect_compliance_rate` | 1 |
| `q3.ks_distance_by_style.Tripel` | 0.3573 |
| `q3.ks_distance_by_style.Kriek` | 0.3983 |
| `q3.ks_distance_by_style.Lambic` | 0.4084 |
| `q3.gen_tripel_ester_level` | 3.9 |
| `q3.real_tripel_ester_level` | 3.2143 |
| `q3.gen_dim` | 231 |
| `q3_defect_compliance_rate` | 1 |
| `gen_tripel_ester_level` | 3.9 |
| `real_tripel_ester_level` | 3.2143 |
| `cross_problem.n_predictable_dims_Q1` | 50 |
| `cross_problem.n_high_stable_dims_Q2` | 50 |
| `cross_problem.Q2_stable_le_Q1_predictable` | True |

### `problem_1_results.json`（572 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 1 |
| `method` | `LightGBM(native missing) + 7级分位分箱 + 分层5折CV` |
| `summary.n_samples` | 250 |
| `summary.n_features` | 231 |
| `summary.n_dims` | 50 |
| `summary.n_na_rows` | 63 |
| `summary.mean_qwk_main` | 0.3663 |
| `summary.mean_qwk_mean_baseline` | 0.0015 |
| `summary.mean_qwk_elasticnet` | 0.2762 |
| `summary.mean_qwk_rf` | 0.328 |
| `summary.mean_qwk_knn_impute` | 0.3652 |
| `summary.n_predictable_dims` | 50 |
| `summary.n_main_chosen` | 50 |
| `summary.n_dims_main_beats_baseline` | 50 |
| `per_dim.A_malt_all.qwk_main` | 0.6006 |
| `per_dim.A_malt_all.qwk_mean_baseline` | 0.0122 |
| `per_dim.A_malt_all.qwk_elasticnet` | 0.5106 |
| `per_dim.A_malt_all.qwk_rf` | 0.5475 |
| `per_dim.A_malt_all.qwk_knn_impute` | 0.5809 |
| `per_dim.A_malt_all.mae_main` | 1.22 |
| `per_dim.A_malt_all.r2_main` | 0.4467 |
| `per_dim.A_malt_all.chosen_model` | `lightgbm` |
| `per_dim.A_malt_all.is_core` | True |
| `per_dim.A_malt_grain.qwk_main` | 0.1721 |
| `per_dim.A_malt_grain.qwk_mean_baseline` | -0.0037 |
| `per_dim.A_malt_grain.qwk_elasticnet` | 0.2079 |
| `per_dim.A_malt_grain.qwk_rf` | 0.1718 |
| `per_dim.A_malt_grain.qwk_knn_impute` | 0.1814 |
| `per_dim.A_malt_grain.mae_main` | 1.748 |
| `per_dim.A_malt_grain.r2_main` | -0.0318 |
| `per_dim.A_malt_grain.chosen_model` | `lightgbm` |
| `per_dim.A_malt_grain.is_core` | True |
| `per_dim.A_malt_bread.qwk_main` | 0.2753 |
| `per_dim.A_malt_bread.qwk_mean_baseline` | 0 |
| `per_dim.A_malt_bread.qwk_elasticnet` | 0.1314 |
| `per_dim.A_malt_bread.qwk_rf` | 0.2124 |
| `per_dim.A_malt_bread.qwk_knn_impute` | 0.2876 |
| `per_dim.A_malt_bread.mae_main` | 1.676 |
| `per_dim.A_malt_bread.r2_main` | 0.0517 |
| `per_dim.A_malt_bread.chosen_model` | `lightgbm` |
| `per_dim.A_malt_bread.is_core` | True |
| `per_dim.A_malt_cara.qwk_main` | 0.5193 |
| `per_dim.A_malt_cara.qwk_mean_baseline` | 0 |
| `per_dim.A_malt_cara.qwk_elasticnet` | 0.3542 |
| `per_dim.A_malt_cara.qwk_rf` | 0.4661 |
| `per_dim.A_malt_cara.qwk_knn_impute` | 0.508 |
| `per_dim.A_malt_cara.mae_main` | 1.332 |
| `per_dim.A_malt_cara.r2_main` | 0.3401 |
| `per_dim.A_malt_cara.chosen_model` | `lightgbm` |
| `per_dim.A_malt_cara.is_core` | True |
| `per_dim.A_malt_burn.qwk_main` | 0.1474 |
| `per_dim.A_malt_burn.qwk_mean_baseline` | -0.0092 |
| `per_dim.A_malt_burn.qwk_elasticnet` | 0.2181 |
| `per_dim.A_malt_burn.qwk_rf` | 0.1351 |
| `per_dim.A_malt_burn.qwk_knn_impute` | 0.1581 |
| `per_dim.A_malt_burn.mae_main` | 1.888 |
| `per_dim.A_malt_burn.r2_main` | 0.2669 |
| `per_dim.A_malt_burn.chosen_model` | `lightgbm` |
| `per_dim.A_malt_burn.is_core` | True |
| `per_dim.A_hops_all.qwk_main` | 0.5729 |
| `per_dim.A_hops_all.qwk_mean_baseline` | 0 |
| `per_dim.A_hops_all.qwk_elasticnet` | 0.3916 |
| `per_dim.A_hops_all.qwk_rf` | 0.5341 |
| `per_dim.A_hops_all.qwk_knn_impute` | 0.574 |
| `per_dim.A_hops_all.mae_main` | 1.244 |
| `per_dim.A_hops_all.r2_main` | 0.3283 |
| `per_dim.A_hops_all.chosen_model` | `lightgbm` |
| `per_dim.A_hops_all.is_core` | True |
| `per_dim.A_hops_citrus.qwk_main` | 0.3113 |
| `per_dim.A_hops_citrus.qwk_mean_baseline` | 0 |
| `per_dim.A_hops_citrus.qwk_elasticnet` | 0.2541 |
| `per_dim.A_hops_citrus.qwk_rf` | 0.2635 |
| `per_dim.A_hops_citrus.qwk_knn_impute` | 0.2877 |
| `per_dim.A_hops_citrus.mae_main` | 1.592 |
| `per_dim.A_hops_citrus.r2_main` | 0.0786 |
| `per_dim.A_hops_citrus.chosen_model` | `lightgbm` |
| `per_dim.A_hops_citrus.is_core` | True |
| `per_dim.A_hops_tropical.qwk_main` | 0.2002 |
| `per_dim.A_hops_tropical.qwk_mean_baseline` | 0 |
| `per_dim.A_hops_tropical.qwk_elasticnet` | 0.1242 |
| `per_dim.A_hops_tropical.qwk_rf` | 0.1938 |
| `per_dim.A_hops_tropical.qwk_knn_impute` | 0.1974 |
| `per_dim.A_hops_tropical.mae_main` | 1.768 |
| `per_dim.A_hops_tropical.r2_main` | 0.017 |
| `per_dim.A_hops_tropical.chosen_model` | `lightgbm` |
| `per_dim.A_hops_tropical.is_core` | True |
| `per_dim.A_hops_noble.qwk_main` | 0.5241 |
| `per_dim.A_hops_noble.qwk_mean_baseline` | 0 |
| `per_dim.A_hops_noble.qwk_elasticnet` | 0.3603 |
| `per_dim.A_hops_noble.qwk_rf` | 0.5236 |
| `per_dim.A_hops_noble.qwk_knn_impute` | 0.5289 |
| `per_dim.A_hops_noble.mae_main` | 1.312 |
| `per_dim.A_hops_noble.r2_main` | 0.292 |
| `per_dim.A_hops_noble.chosen_model` | `lightgbm` |
| `per_dim.A_hops_noble.is_core` | True |
| `per_dim.A_hops_woody.qwk_main` | 0.1958 |
| `per_dim.A_hops_woody.qwk_mean_baseline` | 0 |
| `per_dim.A_hops_woody.qwk_elasticnet` | 0.1541 |
| `per_dim.A_hops_woody.qwk_rf` | 0.1728 |
| `per_dim.A_hops_woody.qwk_knn_impute` | 0.2171 |
| `per_dim.A_hops_woody.mae_main` | 1.768 |
| `per_dim.A_hops_woody.r2_main` | 0.0499 |
| `per_dim.A_hops_woody.chosen_model` | `lightgbm` |
| `per_dim.A_hops_woody.is_core` | True |
| `per_dim.A_esters_all.qwk_main` | 0.4327 |
| `per_dim.A_esters_all.qwk_mean_baseline` | 0 |
| `per_dim.A_esters_all.qwk_elasticnet` | 0.2645 |
| `per_dim.A_esters_all.qwk_rf` | 0.375 |
| `per_dim.A_esters_all.qwk_knn_impute` | 0.432 |
| `per_dim.A_esters_all.mae_main` | 1.504 |
| `per_dim.A_esters_all.r2_main` | 0.232 |
| `per_dim.A_esters_all.chosen_model` | `lightgbm` |
| `per_dim.A_esters_all.is_core` | True |
| `per_dim.A_esters_ethac.qwk_main` | 0.2989 |
| `per_dim.A_esters_ethac.qwk_mean_baseline` | 0 |
| `per_dim.A_esters_ethac.qwk_elasticnet` | 0.231 |
| `per_dim.A_esters_ethac.qwk_rf` | 0.2766 |
| `per_dim.A_esters_ethac.qwk_knn_impute` | 0.3033 |
| `per_dim.A_esters_ethac.mae_main` | 1.588 |
| `per_dim.A_esters_ethac.r2_main` | 0.0949 |
| `per_dim.A_esters_ethac.chosen_model` | `lightgbm` |
| `per_dim.A_esters_ethac.is_core` | True |
| `per_dim.A_esters_isoaa.qwk_main` | 0.2912 |
| `per_dim.A_esters_isoaa.qwk_mean_baseline` | -0.019 |
| `per_dim.A_esters_isoaa.qwk_elasticnet` | 0.1459 |
| `per_dim.A_esters_isoaa.qwk_rf` | 0.27 |
| `per_dim.A_esters_isoaa.qwk_knn_impute` | 0.2613 |
| `per_dim.A_esters_isoaa.mae_main` | 1.596 |
| `per_dim.A_esters_isoaa.r2_main` | 0.0581 |
| `per_dim.A_esters_isoaa.chosen_model` | `lightgbm` |
| `per_dim.A_esters_isoaa.is_core` | True |
| `per_dim.A_esters_flower.qwk_main` | 0.1469 |
| `per_dim.A_esters_flower.qwk_mean_baseline` | 0 |
| `per_dim.A_esters_flower.qwk_elasticnet` | 0.1601 |
| `per_dim.A_esters_flower.qwk_rf` | 0.1139 |
| `per_dim.A_esters_flower.qwk_knn_impute` | 0.1366 |
| `per_dim.A_esters_flower.mae_main` | 1.76 |
| `per_dim.A_esters_flower.r2_main` | -0.0589 |
| `per_dim.A_esters_flower.chosen_model` | `lightgbm` |
| `per_dim.A_esters_flower.is_core` | True |
| `per_dim.A_esters_fruity.qwk_main` | 0.1408 |
| `per_dim.A_esters_fruity.qwk_mean_baseline` | 0 |
| `per_dim.A_esters_fruity.qwk_elasticnet` | 0.1507 |
| `per_dim.A_esters_fruity.qwk_rf` | 0.0927 |
| `per_dim.A_esters_fruity.qwk_knn_impute` | 0.1534 |
| `per_dim.A_esters_fruity.mae_main` | 1.816 |
| `per_dim.A_esters_fruity.r2_main` | 0.0245 |
| `per_dim.A_esters_fruity.chosen_model` | `lightgbm` |
| `per_dim.A_esters_fruity.is_core` | True |
| `per_dim.F_malt_all.qwk_main` | 0.6163 |
| `per_dim.F_malt_all.qwk_mean_baseline` | 0 |
| `per_dim.F_malt_all.qwk_elasticnet` | 0.516 |
| `per_dim.F_malt_all.qwk_rf` | 0.6323 |
| `per_dim.F_malt_all.qwk_knn_impute` | 0.6268 |
| `per_dim.F_malt_all.mae_main` | 1.22 |
| `per_dim.F_malt_all.r2_main` | 0.4563 |
| `per_dim.F_malt_all.chosen_model` | `lightgbm` |
| `per_dim.F_malt_all.is_core` | True |
| `per_dim.F_malt_grain.qwk_main` | 0.1784 |
| `per_dim.F_malt_grain.qwk_mean_baseline` | 0.0183 |
| `per_dim.F_malt_grain.qwk_elasticnet` | 0.1722 |
| `per_dim.F_malt_grain.qwk_rf` | 0.1461 |
| `per_dim.F_malt_grain.qwk_knn_impute` | 0.1672 |
| `per_dim.F_malt_grain.mae_main` | 1.772 |
| `per_dim.F_malt_grain.r2_main` | -0.0164 |
| `per_dim.F_malt_grain.chosen_model` | `lightgbm` |
| `per_dim.F_malt_grain.is_core` | True |
| `per_dim.F_malt_bread.qwk_main` | 0.5101 |
| `per_dim.F_malt_bread.qwk_mean_baseline` | 0 |
| `per_dim.F_malt_bread.qwk_elasticnet` | 0.363 |
| `per_dim.F_malt_bread.qwk_rf` | 0.4057 |
| `per_dim.F_malt_bread.qwk_knn_impute` | 0.541 |
| `per_dim.F_malt_bread.mae_main` | 1.364 |
| `per_dim.F_malt_bread.r2_main` | 0.2686 |
| `per_dim.F_malt_bread.chosen_model` | `lightgbm` |
| `per_dim.F_malt_bread.is_core` | True |
| `per_dim.F_malt_cara.qwk_main` | 0.4592 |
| `per_dim.F_malt_cara.qwk_mean_baseline` | 0 |
| `per_dim.F_malt_cara.qwk_elasticnet` | 0.2158 |
| `per_dim.F_malt_cara.qwk_rf` | 0.4266 |
| `per_dim.F_malt_cara.qwk_knn_impute` | 0.4493 |
| `per_dim.F_malt_cara.mae_main` | 1.416 |
| `per_dim.F_malt_cara.r2_main` | 0.2457 |
| `per_dim.F_malt_cara.chosen_model` | `lightgbm` |
| `per_dim.F_malt_cara.is_core` | True |
| `per_dim.F_malt_burn.qwk_main` | 0.4186 |
| `per_dim.F_malt_burn.qwk_mean_baseline` | 0 |
| `per_dim.F_malt_burn.qwk_elasticnet` | 0.3706 |
| `per_dim.F_malt_burn.qwk_rf` | 0.3494 |
| `per_dim.F_malt_burn.qwk_knn_impute` | 0.3972 |
| `per_dim.F_malt_burn.mae_main` | 1.512 |
| `per_dim.F_malt_burn.r2_main` | 0.39 |
| `per_dim.F_malt_burn.chosen_model` | `lightgbm` |
| `per_dim.F_malt_burn.is_core` | True |
| `per_dim.F_hops_all.qwk_main` | 0.6704 |
| `per_dim.F_hops_all.qwk_mean_baseline` | 0 |
| `per_dim.F_hops_all.qwk_elasticnet` | 0.5227 |
| `per_dim.F_hops_all.qwk_rf` | 0.6681 |
| `per_dim.F_hops_all.qwk_knn_impute` | 0.6834 |
| `per_dim.F_hops_all.mae_main` | 1.12 |
| `per_dim.F_hops_all.r2_main` | 0.5055 |
| `per_dim.F_hops_all.chosen_model` | `lightgbm` |
| `per_dim.F_hops_all.is_core` | True |
| `per_dim.F_hops_citrus.qwk_main` | 0.188 |
| `per_dim.F_hops_citrus.qwk_mean_baseline` | 0 |
| `per_dim.F_hops_citrus.qwk_elasticnet` | 0.186 |
| `per_dim.F_hops_citrus.qwk_rf` | 0.1463 |
| `per_dim.F_hops_citrus.qwk_knn_impute` | 0.1965 |
| `per_dim.F_hops_citrus.mae_main` | 1.748 |
| `per_dim.F_hops_citrus.r2_main` | 0.0642 |
| `per_dim.F_hops_citrus.chosen_model` | `lightgbm` |
| `per_dim.F_hops_citrus.is_core` | True |
| `per_dim.F_hops_tropical.qwk_main` | 0.2531 |
| `per_dim.F_hops_tropical.qwk_mean_baseline` | 0 |
| `per_dim.F_hops_tropical.qwk_elasticnet` | 0.1354 |
| `per_dim.F_hops_tropical.qwk_rf` | 0.1761 |
| `per_dim.F_hops_tropical.qwk_knn_impute` | 0.2149 |
| `per_dim.F_hops_tropical.mae_main` | 1.72 |
| `per_dim.F_hops_tropical.r2_main` | 0.0805 |
| `per_dim.F_hops_tropical.chosen_model` | `lightgbm` |
| `per_dim.F_hops_tropical.is_core` | True |
| `per_dim.F_hops_noble.qwk_main` | 0.6021 |
| `per_dim.F_hops_noble.qwk_mean_baseline` | 0.0506 |
| `per_dim.F_hops_noble.qwk_elasticnet` | 0.4771 |
| `per_dim.F_hops_noble.qwk_rf` | 0.6063 |
| `per_dim.F_hops_noble.qwk_knn_impute` | 0.6096 |
| `per_dim.F_hops_noble.mae_main` | 1.24 |
| `per_dim.F_hops_noble.r2_main` | 0.3911 |
| `per_dim.F_hops_noble.chosen_model` | `lightgbm` |
| `per_dim.F_hops_noble.is_core` | True |
| `per_dim.F_hops_woody.qwk_main` | 0.3606 |
| `per_dim.F_hops_woody.qwk_mean_baseline` | 0 |
| `per_dim.F_hops_woody.qwk_elasticnet` | 0.2273 |
| `per_dim.F_hops_woody.qwk_rf` | 0.333 |
| `per_dim.F_hops_woody.qwk_knn_impute` | 0.3774 |
| `per_dim.F_hops_woody.mae_main` | 1.58 |
| `per_dim.F_hops_woody.r2_main` | 0.1493 |
| `per_dim.F_hops_woody.chosen_model` | `lightgbm` |
| `per_dim.F_hops_woody.is_core` | True |
| `per_dim.F_esters_all.qwk_main` | 0.5442 |
| `per_dim.F_esters_all.qwk_mean_baseline` | 0 |
| `per_dim.F_esters_all.qwk_elasticnet` | 0.3594 |
| `per_dim.F_esters_all.qwk_rf` | 0.4968 |
| `per_dim.F_esters_all.qwk_knn_impute` | 0.5357 |
| `per_dim.F_esters_all.mae_main` | 1.312 |
| `per_dim.F_esters_all.r2_main` | 0.3343 |
| `per_dim.F_esters_all.chosen_model` | `lightgbm` |
| `per_dim.F_esters_all.is_core` | True |
| `per_dim.F_esters_ethac.qwk_main` | 0.4967 |
| `per_dim.F_esters_ethac.qwk_mean_baseline` | 0 |
| `per_dim.F_esters_ethac.qwk_elasticnet` | 0.3621 |
| `per_dim.F_esters_ethac.qwk_rf` | 0.4672 |
| `per_dim.F_esters_ethac.qwk_knn_impute` | 0.4835 |
| `per_dim.F_esters_ethac.mae_main` | 1.408 |
| `per_dim.F_esters_ethac.r2_main` | 0.2537 |
| `per_dim.F_esters_ethac.chosen_model` | `lightgbm` |
| `per_dim.F_esters_ethac.is_core` | True |
| `per_dim.F_esters_isoaa.qwk_main` | 0.321 |
| `per_dim.F_esters_isoaa.qwk_mean_baseline` | 0 |
| `per_dim.F_esters_isoaa.qwk_elasticnet` | 0.1921 |
| `per_dim.F_esters_isoaa.qwk_rf` | 0.3317 |
| `per_dim.F_esters_isoaa.qwk_knn_impute` | 0.362 |
| `per_dim.F_esters_isoaa.mae_main` | 1.616 |
| `per_dim.F_esters_isoaa.r2_main` | 0.1091 |
| `per_dim.F_esters_isoaa.chosen_model` | `lightgbm` |
| `per_dim.F_esters_isoaa.is_core` | True |
| `per_dim.F_esters_flower.qwk_main` | 0.1353 |
| `per_dim.F_esters_flower.qwk_mean_baseline` | 0 |
| `per_dim.F_esters_flower.qwk_elasticnet` | 0.1559 |
| `per_dim.F_esters_flower.qwk_rf` | 0.0542 |
| `per_dim.F_esters_flower.qwk_knn_impute` | 0.1547 |
| `per_dim.F_esters_flower.mae_main` | 1.804 |
| `per_dim.F_esters_flower.r2_main` | -0.0126 |
| `per_dim.F_esters_flower.chosen_model` | `lightgbm` |
| `per_dim.F_esters_flower.is_core` | True |
| `per_dim.F_esters_fruity.qwk_main` | 0.2392 |
| `per_dim.F_esters_fruity.qwk_mean_baseline` | 0 |
| `per_dim.F_esters_fruity.qwk_elasticnet` | 0.156 |
| `per_dim.F_esters_fruity.qwk_rf` | 0.2228 |
| `per_dim.F_esters_fruity.qwk_knn_impute` | 0.22 |
| `per_dim.F_esters_fruity.mae_main` | 1.772 |
| `per_dim.F_esters_fruity.r2_main` | 0.1076 |
| `per_dim.F_esters_fruity.chosen_model` | `lightgbm` |
| `per_dim.F_esters_fruity.is_core` | True |
| `per_dim.acidity.qwk_main` | 0.4397 |
| `per_dim.acidity.qwk_mean_baseline` | 0 |
| `per_dim.acidity.qwk_elasticnet` | 0.3431 |
| `per_dim.acidity.qwk_rf` | 0.3626 |
| `per_dim.acidity.qwk_knn_impute` | 0.4352 |
| `per_dim.acidity.mae_main` | 1.432 |
| `per_dim.acidity.r2_main` | 0.702 |
| `per_dim.acidity.chosen_model` | `lightgbm` |
| `per_dim.acidity.is_core` | False |
| `per_dim.bitternes.qwk_main` | 0.7762 |
| `per_dim.bitternes.qwk_mean_baseline` | 0 |
| `per_dim.bitternes.qwk_elasticnet` | 0.6288 |
| `per_dim.bitternes.qwk_rf` | 0.7806 |
| `per_dim.bitternes.qwk_knn_impute` | 0.7683 |
| `per_dim.bitternes.mae_main` | 0.896 |
| `per_dim.bitternes.r2_main` | 0.6341 |
| `per_dim.bitternes.chosen_model` | `lightgbm` |
| `per_dim.bitternes.is_core` | False |
| `per_dim.sweetness.qwk_main` | 0.5996 |
| `per_dim.sweetness.qwk_mean_baseline` | 0 |
| `per_dim.sweetness.qwk_elasticnet` | 0.3571 |
| `per_dim.sweetness.qwk_rf` | 0.5413 |
| `per_dim.sweetness.qwk_knn_impute` | 0.5758 |
| `per_dim.sweetness.mae_main` | 1.216 |
| `per_dim.sweetness.r2_main` | 0.3901 |
| `per_dim.sweetness.chosen_model` | `lightgbm` |
| `per_dim.sweetness.is_core` | False |
| `per_dim.X4vg.qwk_main` | 0.468 |
| `per_dim.X4vg.qwk_mean_baseline` | -0.0155 |
| `per_dim.X4vg.qwk_elasticnet` | 0.3305 |
| `per_dim.X4vg.qwk_rf` | 0.415 |
| `per_dim.X4vg.qwk_knn_impute` | 0.4555 |
| `per_dim.X4vg.mae_main` | 1.488 |
| `per_dim.X4vg.r2_main` | 0.2001 |
| `per_dim.X4vg.chosen_model` | `lightgbm` |
| `per_dim.X4vg.is_core` | False |
| `per_dim.diacetyl.qwk_main` | 0.2588 |
| `per_dim.diacetyl.qwk_mean_baseline` | 0 |
| `per_dim.diacetyl.qwk_elasticnet` | 0.2128 |
| `per_dim.diacetyl.qwk_rf` | 0.1546 |
| `per_dim.diacetyl.qwk_knn_impute` | 0.247 |
| `per_dim.diacetyl.mae_main` | 1.696 |
| `per_dim.diacetyl.r2_main` | 0.0752 |
| `per_dim.diacetyl.chosen_model` | `lightgbm` |
| `per_dim.diacetyl.is_core` | False |
| `per_dim.dms.qwk_main` | 0.3161 |
| `per_dim.dms.qwk_mean_baseline` | -0.0065 |
| `per_dim.dms.qwk_elasticnet` | 0.1713 |
| `per_dim.dms.qwk_rf` | 0.2129 |
| `per_dim.dms.qwk_knn_impute` | 0.2492 |
| `per_dim.dms.mae_main` | 1.584 |
| `per_dim.dms.r2_main` | 0.1376 |
| `per_dim.dms.chosen_model` | `lightgbm` |
| `per_dim.dms.is_core` | False |
| `per_dim.metallic.qwk_main` | 0.2463 |
| `per_dim.metallic.qwk_mean_baseline` | 0.0043 |
| `per_dim.metallic.qwk_elasticnet` | 0.1337 |
| `per_dim.metallic.qwk_rf` | 0.1909 |
| `per_dim.metallic.qwk_knn_impute` | 0.2573 |
| `per_dim.metallic.mae_main` | 1.652 |
| `per_dim.metallic.r2_main` | 0.0885 |
| `per_dim.metallic.chosen_model` | `lightgbm` |
| `per_dim.metallic.is_core` | False |
| `per_dim.stale_hops.qwk_main` | 0.1466 |
| `per_dim.stale_hops.qwk_mean_baseline` | 0 |
| `per_dim.stale_hops.qwk_elasticnet` | 0.1566 |
| `per_dim.stale_hops.qwk_rf` | 0.1226 |
| `per_dim.stale_hops.qwk_knn_impute` | 0.1329 |
| `per_dim.stale_hops.mae_main` | 1.804 |
| `per_dim.stale_hops.r2_main` | 0.0661 |
| `per_dim.stale_hops.chosen_model` | `lightgbm` |
| `per_dim.stale_hops.is_core` | False |
| `per_dim.t2n.qwk_main` | 0.1535 |
| `per_dim.t2n.qwk_mean_baseline` | 0.0421 |
| `per_dim.t2n.qwk_elasticnet` | 0.1525 |
| `per_dim.t2n.qwk_rf` | 0.1374 |
| `per_dim.t2n.qwk_knn_impute` | 0.1664 |
| `per_dim.t2n.mae_main` | 1.728 |
| `per_dim.t2n.r2_main` | 0.0339 |
| `per_dim.t2n.chosen_model` | `lightgbm` |
| `per_dim.t2n.is_core` | False |
| `per_dim.orange.qwk_main` | 0.2046 |
| `per_dim.orange.qwk_mean_baseline` | 0 |
| `per_dim.orange.qwk_elasticnet` | 0.1595 |
| `per_dim.orange.qwk_rf` | 0.1427 |
| `per_dim.orange.qwk_knn_impute` | 0.1804 |
| `per_dim.orange.mae_main` | 2.008 |
| `per_dim.orange.r2_main` | 0.1455 |
| `per_dim.orange.chosen_model` | `lightgbm` |
| `per_dim.orange.is_core` | False |
| `per_dim.coriander.qwk_main` | 0.0925 |
| `per_dim.coriander.qwk_mean_baseline` | 0 |
| `per_dim.coriander.qwk_elasticnet` | 0.0862 |
| `per_dim.coriander.qwk_rf` | 0.0321 |
| `per_dim.coriander.qwk_knn_impute` | 0.1215 |
| `per_dim.coriander.mae_main` | 2.264 |
| `per_dim.coriander.r2_main` | 0.1146 |
| `per_dim.coriander.chosen_model` | `lightgbm` |
| `per_dim.coriander.is_core` | False |
| `per_dim.clove.qwk_main` | 0.1273 |
| `per_dim.clove.qwk_mean_baseline` | 0 |
| `per_dim.clove.qwk_elasticnet` | 0.1763 |
| `per_dim.clove.qwk_rf` | 0.0291 |
| `per_dim.clove.qwk_knn_impute` | 0.1786 |
| `per_dim.clove.mae_main` | 2.236 |
| `per_dim.clove.r2_main` | 0.0579 |
| `per_dim.clove.chosen_model` | `lightgbm` |
| `per_dim.clove.is_core` | False |
| `per_dim.lactic.qwk_main` | 0.3153 |
| `per_dim.lactic.qwk_mean_baseline` | 0 |
| `per_dim.lactic.qwk_elasticnet` | 0.2985 |
| `per_dim.lactic.qwk_rf` | 0.2443 |
| `per_dim.lactic.qwk_knn_impute` | 0.3203 |
| `per_dim.lactic.mae_main` | 1.856 |
| `per_dim.lactic.r2_main` | 0.6751 |
| `per_dim.lactic.chosen_model` | `lightgbm` |
| `per_dim.lactic.is_core` | False |
| `per_dim.acetic.qwk_main` | 0.2863 |
| `per_dim.acetic.qwk_mean_baseline` | 0 |
| `per_dim.acetic.qwk_elasticnet` | 0.2295 |
| `per_dim.acetic.qwk_rf` | 0.1978 |
| `per_dim.acetic.qwk_knn_impute` | 0.271 |
| `per_dim.acetic.mae_main` | 2.012 |
| `per_dim.acetic.r2_main` | 0.5878 |
| `per_dim.acetic.chosen_model` | `lightgbm` |
| `per_dim.acetic.is_core` | False |
| `per_dim.barnyard.qwk_main` | 0.1436 |
| `per_dim.barnyard.qwk_mean_baseline` | 0 |
| `per_dim.barnyard.qwk_elasticnet` | 0.153 |
| `per_dim.barnyard.qwk_rf` | 0.1225 |
| `per_dim.barnyard.qwk_knn_impute` | 0.1384 |
| `per_dim.barnyard.mae_main` | 1.796 |
| `per_dim.barnyard.r2_main` | 0.0954 |
| `per_dim.barnyard.chosen_model` | `lightgbm` |
| `per_dim.barnyard.is_core` | False |
| `per_dim.alcohol.qwk_main` | 0.8185 |
| `per_dim.alcohol.qwk_mean_baseline` | 0 |
| `per_dim.alcohol.qwk_elasticnet` | 0.6387 |
| `per_dim.alcohol.qwk_rf` | 0.8217 |
| `per_dim.alcohol.qwk_knn_impute` | 0.8174 |
| `per_dim.alcohol.mae_main` | 0.852 |
| `per_dim.alcohol.r2_main` | 0.7128 |
| `per_dim.alcohol.chosen_model` | `lightgbm` |
| `per_dim.alcohol.is_core` | False |
| `per_dim.aftertaste.qwk_main` | 0.6513 |
| `per_dim.aftertaste.qwk_mean_baseline` | 0 |
| `per_dim.aftertaste.qwk_elasticnet` | 0.4936 |
| `per_dim.aftertaste.qwk_rf` | 0.6165 |
| `per_dim.aftertaste.qwk_knn_impute` | 0.6205 |
| `per_dim.aftertaste.mae_main` | 1.172 |
| `per_dim.aftertaste.r2_main` | 0.4684 |
| `per_dim.aftertaste.chosen_model` | `lightgbm` |
| `per_dim.aftertaste.is_core` | False |
| `per_dim.body.qwk_main` | 0.6817 |
| `per_dim.body.qwk_mean_baseline` | 0 |
| `per_dim.body.qwk_elasticnet` | 0.5292 |
| `per_dim.body.qwk_rf` | 0.6775 |
| `per_dim.body.qwk_knn_impute` | 0.687 |
| `per_dim.body.mae_main` | 1.076 |
| `per_dim.body.r2_main` | 0.525 |
| `per_dim.body.chosen_model` | `lightgbm` |
| `per_dim.body.is_core` | False |
| `per_dim.co2.qwk_main` | 0.5373 |
| `per_dim.co2.qwk_mean_baseline` | 0 |
| `per_dim.co2.qwk_elasticnet` | 0.3834 |
| `per_dim.co2.qwk_rf` | 0.5373 |
| `per_dim.co2.qwk_knn_impute` | 0.5374 |
| `per_dim.co2.mae_main` | 1.356 |
| `per_dim.co2.r2_main` | 0.3137 |
| `per_dim.co2.chosen_model` | `lightgbm` |
| `per_dim.co2.is_core` | False |
| `per_dim.overall.qwk_main` | 0.2303 |
| `per_dim.overall.qwk_mean_baseline` | 0 |
| `per_dim.overall.qwk_elasticnet` | 0.1073 |
| `per_dim.overall.qwk_rf` | 0.2498 |
| `per_dim.overall.qwk_knn_impute` | 0.2712 |
| `per_dim.overall.mae_main` | 1.696 |
| `per_dim.overall.r2_main` | 0.057 |
| `per_dim.overall.chosen_model` | `lightgbm` |
| `per_dim.overall.is_core` | False |
| `predictable_dims[0]` | `A_malt_all` |
| `predictable_dims[1]` | `A_malt_grain` |
| `predictable_dims[2]` | `A_malt_bread` |
| `predictable_dims[49]` | `overall` |
| `predictable_dims[3..48]` | `<省略中间 46 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `sensory_cols[0]` | `A_malt_all` |
| `sensory_cols[1]` | `A_malt_grain` |
| `sensory_cols[2]` | `A_malt_bread` |
| `sensory_cols[49]` | `overall` |
| `sensory_cols[3..48]` | `<省略中间 46 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `chosen_model.A_malt_all` | `lightgbm` |
| `chosen_model.A_malt_grain` | `lightgbm` |
| `chosen_model.A_malt_bread` | `lightgbm` |
| `chosen_model.A_malt_cara` | `lightgbm` |
| `chosen_model.A_malt_burn` | `lightgbm` |
| `chosen_model.A_hops_all` | `lightgbm` |
| `chosen_model.A_hops_citrus` | `lightgbm` |
| `chosen_model.A_hops_tropical` | `lightgbm` |
| `chosen_model.A_hops_noble` | `lightgbm` |
| `chosen_model.A_hops_woody` | `lightgbm` |
| `chosen_model.A_esters_all` | `lightgbm` |
| `chosen_model.A_esters_ethac` | `lightgbm` |
| `chosen_model.A_esters_isoaa` | `lightgbm` |
| `chosen_model.A_esters_flower` | `lightgbm` |
| `chosen_model.A_esters_fruity` | `lightgbm` |
| `chosen_model.F_malt_all` | `lightgbm` |
| `chosen_model.F_malt_grain` | `lightgbm` |
| `chosen_model.F_malt_bread` | `lightgbm` |
| `chosen_model.F_malt_cara` | `lightgbm` |
| `chosen_model.F_malt_burn` | `lightgbm` |
| `chosen_model.F_hops_all` | `lightgbm` |
| `chosen_model.F_hops_citrus` | `lightgbm` |
| `chosen_model.F_hops_tropical` | `lightgbm` |
| `chosen_model.F_hops_noble` | `lightgbm` |
| `chosen_model.F_hops_woody` | `lightgbm` |
| `chosen_model.F_esters_all` | `lightgbm` |
| `chosen_model.F_esters_ethac` | `lightgbm` |
| `chosen_model.F_esters_isoaa` | `lightgbm` |
| `chosen_model.F_esters_flower` | `lightgbm` |
| `chosen_model.F_esters_fruity` | `lightgbm` |
| `chosen_model.acidity` | `lightgbm` |
| `chosen_model.bitternes` | `lightgbm` |
| `chosen_model.sweetness` | `lightgbm` |
| `chosen_model.X4vg` | `lightgbm` |
| `chosen_model.diacetyl` | `lightgbm` |
| `chosen_model.dms` | `lightgbm` |
| `chosen_model.metallic` | `lightgbm` |
| `chosen_model.stale_hops` | `lightgbm` |
| `chosen_model.t2n` | `lightgbm` |
| `chosen_model.orange` | `lightgbm` |
| `chosen_model.coriander` | `lightgbm` |
| `chosen_model.clove` | `lightgbm` |
| `chosen_model.lactic` | `lightgbm` |
| `chosen_model.acetic` | `lightgbm` |
| `chosen_model.barnyard` | `lightgbm` |
| `chosen_model.alcohol` | `lightgbm` |
| `chosen_model.aftertaste` | `lightgbm` |
| `chosen_model.body` | `lightgbm` |
| `chosen_model.co2` | `lightgbm` |
| `chosen_model.overall` | `lightgbm` |
| `validation.scheme` | `StratifiedKFold` |
| `validation.n_folds` | 5 |
| `validation.binning` | `quantile` |
| `validation.leakage_control` | `分箱/插补仅训练折fit` |
| `calibration.dim` | `F_hops_all` |
| `calibration.true_level[0]` | 3 |
| `calibration.true_level[1]` | 0 |
| `calibration.true_level[2]` | 0 |
| `calibration.true_level[249]` | 6 |
| `calibration.true_level[3..248]` | `<省略中间 246 项；数值范围 [0, 6]；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `calibration.pred_level[0]` | 0 |
| `calibration.pred_level[1]` | 2 |
| `calibration.pred_level[2]` | 1 |
| `calibration.pred_level[249]` | 4 |
| `calibration.pred_level[3..248]` | `<省略中间 246 项；数值范围 [0, 6]；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `calibration.true_cont[0]` | -0.0709 |
| `calibration.true_cont[1]` | -0.906 |
| `calibration.true_cont[2]` | -0.912 |
| `calibration.true_cont[249]` | 0.9599 |
| `calibration.true_cont[3..248]` | `<省略中间 246 项；数值范围 [-1.2656, 2.2011]；论文引用的值不在上面时，直接读原 JSO...` |
| `calibration.pred_cont[0]` | -0.8847 |
| `calibration.pred_cont[1]` | -0.3793 |
| `calibration.pred_cont[2]` | -0.6588 |
| `calibration.pred_cont[249]` | 0.2404 |
| `calibration.pred_cont[3..248]` | `<省略中间 246 项；数值范围 [-1.0159, 1.2285]；论文引用的值不在上面时，直接读原 JSO...` |
| `fig_data.missing_rate_by_col[0][0]` | `amyl.acetate` |
| `fig_data.missing_rate_by_col[0][1]` | 0.108 |
| `fig_data.missing_rate_by_col[1][0]` | `aroma_hops_sum` |
| `fig_data.missing_rate_by_col[1][1]` | 0.052 |
| `fig_data.missing_rate_by_col[2][0]` | `methylpyrazine` |
| `fig_data.missing_rate_by_col[2][1]` | 0.048 |
| `fig_data.missing_rate_by_col[8][0]` | `phenylacetaldehyde` |
| `fig_data.missing_rate_by_col[8][1]` | 0.004 |
| `fig_data.missing_rate_by_col[3..7]` | `<省略中间 5 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.n_na_rows` | 63 |
| `fig_data.qwk_ranked[0][0]` | `alcohol` |
| `fig_data.qwk_ranked[0][1]` | 0.8185 |
| `fig_data.qwk_ranked[1][0]` | `bitternes` |
| `fig_data.qwk_ranked[1][1]` | 0.7762 |
| `fig_data.qwk_ranked[2][0]` | `body` |
| `fig_data.qwk_ranked[2][1]` | 0.6817 |
| `fig_data.qwk_ranked[49][0]` | `coriander` |
| `fig_data.qwk_ranked[49][1]` | 0.0925 |
| `fig_data.qwk_ranked[3..48]` | `<省略中间 46 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.rep_dim` | `F_hops_all` |
| `submission.path` | `submission/q1_sensory_scores.csv` |
| `submission.rows` | 250 |
| `submission.cols` | 51 |

### `problem_2_results.json`（1172 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 2 |
| `method` | `共表达图(networkx+louvain) + SHAP/相关/模块代表融合 + bootstrap频率 +...` |
| `summary.n_dims` | 50 |
| `summary.n_bootstrap` | 500 |
| `summary.topn` | 3 |
| `summary.mean_top1_select_freq` | 0.9959 |
| `summary.mean_cross_method_jaccard` | 0.3033 |
| `summary.n_high_stable_dims` | 50 |
| `summary.fuse_weights.alpha` | 0.5 |
| `summary.fuse_weights.beta` | 0.3 |
| `summary.fuse_weights.gamma` | 0.2 |
| `per_dim.A_malt_all.top3[0]` | `color.EBC.` |
| `per_dim.A_malt_all.top3[1]` | `kcalperc` |
| `per_dim.A_malt_all.top3[2]` | `pH` |
| `per_dim.A_malt_all.top3_idx[0]` | 24 |
| `per_dim.A_malt_all.top3_idx[1]` | 36 |
| `per_dim.A_malt_all.top3_idx[2]` | 29 |
| `per_dim.A_malt_all.phi[0]` | 1 |
| `per_dim.A_malt_all.phi[1]` | 0.5199 |
| `per_dim.A_malt_all.phi[2]` | 0.4732 |
| `per_dim.A_malt_all.shap_norm[0]` | 1 |
| `per_dim.A_malt_all.shap_norm[1]` | 0.2121 |
| `per_dim.A_malt_all.shap_norm[2]` | 0.146 |
| `per_dim.A_malt_all.corr_abs[0]` | 1 |
| `per_dim.A_malt_all.corr_abs[1]` | 0.7129 |
| `per_dim.A_malt_all.corr_abs[2]` | 0.6673 |
| `per_dim.A_malt_all.select_freq[0]` | 1 |
| `per_dim.A_malt_all.select_freq[1]` | 1 |
| `per_dim.A_malt_all.select_freq[2]` | 0.998 |
| `per_dim.A_malt_all.module[0]` | 0 |
| `per_dim.A_malt_all.module[1]` | 2 |
| `per_dim.A_malt_all.module[2]` | 8 |
| `per_dim.A_malt_all.jaccard_cross_method` | 0.6667 |
| `per_dim.A_malt_grain.top3[0]` | `Z.nerolidol` |
| `per_dim.A_malt_grain.top3[1]` | `terpinen.4.ol` |
| `per_dim.A_malt_grain.top3[2]` | `GFS` |
| `per_dim.A_malt_grain.top3_idx[0]` | 178 |
| `per_dim.A_malt_grain.top3_idx[1]` | 114 |
| `per_dim.A_malt_grain.top3_idx[2]` | 32 |
| `per_dim.A_malt_grain.phi[0]` | 0.7006 |
| `per_dim.A_malt_grain.phi[1]` | 0.7 |
| `per_dim.A_malt_grain.phi[2]` | 0.665 |
| `per_dim.A_malt_grain.shap_norm[0]` | 0.6655 |
| `per_dim.A_malt_grain.shap_norm[1]` | 1 |
| `per_dim.A_malt_grain.shap_norm[2]` | 0.3957 |
| `per_dim.A_malt_grain.corr_abs[0]` | 0.5594 |
| `per_dim.A_malt_grain.corr_abs[1]` | 0 |
| `per_dim.A_malt_grain.corr_abs[2]` | 0.8906 |
| `per_dim.A_malt_grain.select_freq[0]` | 0.998 |
| `per_dim.A_malt_grain.select_freq[1]` | 1 |
| `per_dim.A_malt_grain.select_freq[2]` | 0.884 |
| `per_dim.A_malt_grain.module[0]` | 50 |
| `per_dim.A_malt_grain.module[1]` | 4 |
| `per_dim.A_malt_grain.module[2]` | 19 |
| `per_dim.A_malt_grain.jaccard_cross_method` | 0 |
| `per_dim.A_malt_bread.top3[0]` | `glycerol` |
| `per_dim.A_malt_bread.top3[1]` | `color.EBC.` |
| `per_dim.A_malt_bread.top3[2]` | `acetaldehyde` |
| `per_dim.A_malt_bread.top3_idx[0]` | 27 |
| `per_dim.A_malt_bread.top3_idx[1]` | 24 |
| `per_dim.A_malt_bread.top3_idx[2]` | 0 |
| `per_dim.A_malt_bread.phi[0]` | 0.9428 |
| `per_dim.A_malt_bread.phi[1]` | 0.9227 |
| `per_dim.A_malt_bread.phi[2]` | 0.6416 |
| `per_dim.A_malt_bread.shap_norm[0]` | 1 |
| `per_dim.A_malt_bread.shap_norm[1]` | 0.8454 |
| `per_dim.A_malt_bread.shap_norm[2]` | 0.6606 |
| `per_dim.A_malt_bread.corr_abs[0]` | 0.8093 |
| `per_dim.A_malt_bread.corr_abs[1]` | 1 |
| `per_dim.A_malt_bread.corr_abs[2]` | 0.7045 |
| `per_dim.A_malt_bread.select_freq[0]` | 1 |
| `per_dim.A_malt_bread.select_freq[1]` | 1 |
| `per_dim.A_malt_bread.select_freq[2]` | 0.61 |
| `per_dim.A_malt_bread.module[0]` | 2 |
| `per_dim.A_malt_bread.module[1]` | 0 |
| `per_dim.A_malt_bread.module[2]` | 2 |
| `per_dim.A_malt_bread.jaccard_cross_method` | 0.3 |
| `per_dim.A_malt_cara.top3[0]` | `color.EBC.` |
| `per_dim.A_malt_cara.top3[1]` | `GFS` |
| `per_dim.A_malt_cara.top3[2]` | `protein.g.L.` |
| `per_dim.A_malt_cara.top3_idx[0]` | 24 |
| `per_dim.A_malt_cara.top3_idx[1]` | 32 |
| `per_dim.A_malt_cara.top3_idx[2]` | 30 |
| `per_dim.A_malt_cara.phi[0]` | 1 |
| `per_dim.A_malt_cara.phi[1]` | 0.64 |
| `per_dim.A_malt_cara.phi[2]` | 0.5551 |
| `per_dim.A_malt_cara.shap_norm[0]` | 1 |
| `per_dim.A_malt_cara.shap_norm[1]` | 0.5525 |
| `per_dim.A_malt_cara.shap_norm[2]` | 0.449 |
| `per_dim.A_malt_cara.corr_abs[0]` | 1 |
| `per_dim.A_malt_cara.corr_abs[1]` | 0.5456 |
| `per_dim.A_malt_cara.corr_abs[2]` | 0.7687 |
| `per_dim.A_malt_cara.select_freq[0]` | 1 |
| `per_dim.A_malt_cara.select_freq[1]` | 1 |
| `per_dim.A_malt_cara.select_freq[2]` | 0.996 |
| `per_dim.A_malt_cara.module[0]` | 0 |
| `per_dim.A_malt_cara.module[1]` | 19 |
| `per_dim.A_malt_cara.module[2]` | 0 |
| `per_dim.A_malt_cara.jaccard_cross_method` | 0.3 |
| `per_dim.A_malt_burn.top3[0]` | `color.EBC.` |
| `per_dim.A_malt_burn.top3[1]` | `pH` |
| `per_dim.A_malt_burn.top3[2]` | `kcalperc` |
| `per_dim.A_malt_burn.top3_idx[0]` | 24 |
| `per_dim.A_malt_burn.top3_idx[1]` | 29 |
| `per_dim.A_malt_burn.top3_idx[2]` | 36 |
| `per_dim.A_malt_burn.phi[0]` | 1 |
| `per_dim.A_malt_burn.phi[1]` | 0.636 |
| `per_dim.A_malt_burn.phi[2]` | 0.5205 |
| `per_dim.A_malt_burn.shap_norm[0]` | 1 |
| `per_dim.A_malt_burn.shap_norm[1]` | 0.3818 |
| `per_dim.A_malt_burn.shap_norm[2]` | 0.2467 |
| `per_dim.A_malt_burn.corr_abs[0]` | 1 |
| `per_dim.A_malt_burn.corr_abs[1]` | 0.817 |
| `per_dim.A_malt_burn.corr_abs[2]` | 0.6574 |
| `per_dim.A_malt_burn.select_freq[0]` | 1 |
| `per_dim.A_malt_burn.select_freq[1]` | 1 |
| `per_dim.A_malt_burn.select_freq[2]` | 1 |
| `per_dim.A_malt_burn.module[0]` | 0 |
| `per_dim.A_malt_burn.module[1]` | 8 |
| `per_dim.A_malt_burn.module[2]` | 2 |
| `per_dim.A_malt_burn.jaccard_cross_method` | 0.5 |
| `per_dim.A_hops_all.top3[0]` | `ethyl_octanoate` |
| `per_dim.A_hops_all.top3[1]` | `DMS` |
| `per_dim.A_hops_all.top3[2]` | `linalool` |
| `per_dim.A_hops_all.top3_idx[0]` | 9 |
| `per_dim.A_hops_all.top3_idx[1]` | 3 |
| `per_dim.A_hops_all.top3_idx[2]` | 94 |
| `per_dim.A_hops_all.phi[0]` | 1 |
| `per_dim.A_hops_all.phi[1]` | 0.7012 |
| `per_dim.A_hops_all.phi[2]` | 0.5533 |
| `per_dim.A_hops_all.shap_norm[0]` | 1 |
| `per_dim.A_hops_all.shap_norm[1]` | 0.6894 |
| `per_dim.A_hops_all.shap_norm[2]` | 0.1734 |
| `per_dim.A_hops_all.corr_abs[0]` | 1 |
| `per_dim.A_hops_all.corr_abs[1]` | 0.8548 |
| `per_dim.A_hops_all.corr_abs[2]` | 0.8886 |
| `per_dim.A_hops_all.select_freq[0]` | 1 |
| `per_dim.A_hops_all.select_freq[1]` | 1 |
| `per_dim.A_hops_all.select_freq[2]` | 0.756 |
| `per_dim.A_hops_all.module[0]` | 2 |
| `per_dim.A_hops_all.module[1]` | 2 |
| `per_dim.A_hops_all.module[2]` | 4 |
| `per_dim.A_hops_all.jaccard_cross_method` | 0.2 |
| `per_dim.A_hops_citrus.top3[0]` | `CO2.PSI.` |
| `per_dim.A_hops_citrus.top3[1]` | `protein.g.L.` |
| `per_dim.A_hops_citrus.top3[2]` | `aroma_hops_sum` |
| `per_dim.A_hops_citrus.top3_idx[0]` | 34 |
| `per_dim.A_hops_citrus.top3_idx[1]` | 30 |
| `per_dim.A_hops_citrus.top3_idx[2]` | 228 |
| `per_dim.A_hops_citrus.phi[0]` | 0.9625 |
| `per_dim.A_hops_citrus.phi[1]` | 0.701 |
| `per_dim.A_hops_citrus.phi[2]` | 0.7 |
| `per_dim.A_hops_citrus.shap_norm[0]` | 0.9906 |
| `per_dim.A_hops_citrus.shap_norm[1]` | 0.5768 |
| `per_dim.A_hops_citrus.shap_norm[2]` | 1 |
| `per_dim.A_hops_citrus.corr_abs[0]` | 0.8909 |
| `per_dim.A_hops_citrus.corr_abs[1]` | 0.7086 |
| `per_dim.A_hops_citrus.corr_abs[2]` | 0 |
| `per_dim.A_hops_citrus.select_freq[0]` | 1 |
| `per_dim.A_hops_citrus.select_freq[1]` | 1 |
| `per_dim.A_hops_citrus.select_freq[2]` | 0.886 |
| `per_dim.A_hops_citrus.module[0]` | 20 |
| `per_dim.A_hops_citrus.module[1]` | 0 |
| `per_dim.A_hops_citrus.module[2]` | 4 |
| `per_dim.A_hops_citrus.jaccard_cross_method` | 0.3 |
| `per_dim.A_hops_tropical.top3[0]` | `DMS` |
| `per_dim.A_hops_tropical.top3[1]` | `isopentyl.butanoate` |
| `per_dim.A_hops_tropical.top3[2]` | `geraniol` |
| `per_dim.A_hops_tropical.top3_idx[0]` | 3 |
| `per_dim.A_hops_tropical.top3_idx[1]` | 75 |
| `per_dim.A_hops_tropical.top3_idx[2]` | 127 |
| `per_dim.A_hops_tropical.phi[0]` | 0.804 |
| `per_dim.A_hops_tropical.phi[1]` | 0.7 |
| `per_dim.A_hops_tropical.phi[2]` | 0.48 |
| `per_dim.A_hops_tropical.shap_norm[0]` | 0.6079 |
| `per_dim.A_hops_tropical.shap_norm[1]` | 1 |
| `per_dim.A_hops_tropical.shap_norm[2]` | 0.111 |
| `per_dim.A_hops_tropical.corr_abs[0]` | 1 |
| `per_dim.A_hops_tropical.corr_abs[1]` | 0 |
| `per_dim.A_hops_tropical.corr_abs[2]` | 0.7483 |
| `per_dim.A_hops_tropical.select_freq[0]` | 1 |
| `per_dim.A_hops_tropical.select_freq[1]` | 1 |
| `per_dim.A_hops_tropical.select_freq[2]` | 0.91 |
| `per_dim.A_hops_tropical.module[0]` | 2 |
| `per_dim.A_hops_tropical.module[1]` | 1 |
| `per_dim.A_hops_tropical.module[2]` | 4 |
| `per_dim.A_hops_tropical.jaccard_cross_method` | 0.1333 |
| `per_dim.A_hops_noble.top3[0]` | `ethyl_octanoate` |
| `per_dim.A_hops_noble.top3[1]` | `ethyl_decanoate` |
| `per_dim.A_hops_noble.top3[2]` | `iron` |
| `per_dim.A_hops_noble.top3_idx[0]` | 9 |
| `per_dim.A_hops_noble.top3_idx[1]` | 6 |
| `per_dim.A_hops_noble.top3_idx[2]` | 28 |
| `per_dim.A_hops_noble.phi[0]` | 1 |
| `per_dim.A_hops_noble.phi[1]` | 0.5942 |
| `per_dim.A_hops_noble.phi[2]` | 0.4824 |
| `per_dim.A_hops_noble.shap_norm[0]` | 1 |
| `per_dim.A_hops_noble.shap_norm[1]` | 0.2041 |
| `per_dim.A_hops_noble.shap_norm[2]` | 0.1473 |
| `per_dim.A_hops_noble.corr_abs[0]` | 1 |
| `per_dim.A_hops_noble.corr_abs[1]` | 0.974 |
| `per_dim.A_hops_noble.corr_abs[2]` | 0.696 |
| `per_dim.A_hops_noble.select_freq[0]` | 1 |
| `per_dim.A_hops_noble.select_freq[1]` | 1 |
| `per_dim.A_hops_noble.select_freq[2]` | 1 |
| `per_dim.A_hops_noble.module[0]` | 2 |
| `per_dim.A_hops_noble.module[1]` | 1 |
| `per_dim.A_hops_noble.module[2]` | 18 |
| `per_dim.A_hops_noble.jaccard_cross_method` | 0.3 |
| `per_dim.A_hops_woody.top3[0]` | `alloaromadendrene.epoxide` |
| `per_dim.A_hops_woody.top3[1]` | `ethyl_2.methyl_butyrate` |
| `per_dim.A_hops_woody.top3[2]` | `isobutanol` |
| `per_dim.A_hops_woody.top3_idx[0]` | 188 |
| `per_dim.A_hops_woody.top3_idx[1]` | 4 |
| `per_dim.A_hops_woody.top3_idx[2]` | 13 |
| `per_dim.A_hops_woody.phi[0]` | 0.7 |
| `per_dim.A_hops_woody.phi[1]` | 0.6431 |
| `per_dim.A_hops_woody.phi[2]` | 0.5531 |
| `per_dim.A_hops_woody.shap_norm[0]` | 1 |
| `per_dim.A_hops_woody.shap_norm[1]` | 0.2861 |
| `per_dim.A_hops_woody.shap_norm[2]` | 0.3543 |
| `per_dim.A_hops_woody.corr_abs[0]` | 0 |
| `per_dim.A_hops_woody.corr_abs[1]` | 1 |
| `per_dim.A_hops_woody.corr_abs[2]` | 0.5864 |
| `per_dim.A_hops_woody.select_freq[0]` | 1 |
| `per_dim.A_hops_woody.select_freq[1]` | 1 |
| `per_dim.A_hops_woody.select_freq[2]` | 0.77 |
| `per_dim.A_hops_woody.module[0]` | 1 |
| `per_dim.A_hops_woody.module[1]` | 0 |
| `per_dim.A_hops_woody.module[2]` | 2 |
| `per_dim.A_hops_woody.jaccard_cross_method` | 0.0667 |
| `per_dim.A_esters_all.top3[0]` | `n.hexanol` |
| `per_dim.A_esters_all.top3[1]` | `protein.g.L.` |
| `per_dim.A_esters_all.top3[2]` | `acetaldehyde` |
| `per_dim.A_esters_all.top3_idx[0]` | 54 |
| `per_dim.A_esters_all.top3_idx[1]` | 30 |
| `per_dim.A_esters_all.top3_idx[2]` | 0 |
| `per_dim.A_esters_all.phi[0]` | 0.7 |
| `per_dim.A_esters_all.phi[1]` | 0.6958 |
| `per_dim.A_esters_all.phi[2]` | 0.5568 |
| `per_dim.A_esters_all.shap_norm[0]` | 1 |
| `per_dim.A_esters_all.shap_norm[1]` | 0.4773 |
| `per_dim.A_esters_all.shap_norm[2]` | 0.334 |
| `per_dim.A_esters_all.corr_abs[0]` | 0 |
| `per_dim.A_esters_all.corr_abs[1]` | 0.8571 |
| `per_dim.A_esters_all.corr_abs[2]` | 0.9661 |
| `per_dim.A_esters_all.select_freq[0]` | 1 |
| `per_dim.A_esters_all.select_freq[1]` | 1 |
| `per_dim.A_esters_all.select_freq[2]` | 0.956 |
| `per_dim.A_esters_all.module[0]` | 2 |
| `per_dim.A_esters_all.module[1]` | 0 |
| `per_dim.A_esters_all.module[2]` | 2 |
| `per_dim.A_esters_all.jaccard_cross_method` | 0.0667 |
| `per_dim.A_esters_ethac.top3[0]` | `ethyl_acetate` |
| `per_dim.A_esters_ethac.top3[1]` | `kcalperc` |
| `per_dim.A_esters_ethac.top3[2]` | `phenethyl_alcohol` |
| `per_dim.A_esters_ethac.top3_idx[0]` | 5 |
| `per_dim.A_esters_ethac.top3_idx[1]` | 36 |
| `per_dim.A_esters_ethac.top3_idx[2]` | 19 |
| `per_dim.A_esters_ethac.phi[0]` | 1 |
| `per_dim.A_esters_ethac.phi[1]` | 0.8353 |
| `per_dim.A_esters_ethac.phi[2]` | 0.7925 |
| `per_dim.A_esters_ethac.shap_norm[0]` | 1 |
| `per_dim.A_esters_ethac.shap_norm[1]` | 0.9214 |
| `per_dim.A_esters_ethac.shap_norm[2]` | 0.8667 |
| `per_dim.A_esters_ethac.corr_abs[0]` | 1 |
| `per_dim.A_esters_ethac.corr_abs[1]` | 0.9153 |
| `per_dim.A_esters_ethac.corr_abs[2]` | 0.5303 |
| `per_dim.A_esters_ethac.select_freq[0]` | 1 |
| `per_dim.A_esters_ethac.select_freq[1]` | 1 |
| `per_dim.A_esters_ethac.select_freq[2]` | 1 |
| `per_dim.A_esters_ethac.module[0]` | 2 |
| `per_dim.A_esters_ethac.module[1]` | 2 |
| `per_dim.A_esters_ethac.module[2]` | 13 |
| `per_dim.A_esters_ethac.jaccard_cross_method` | 0.3 |
| `per_dim.A_esters_isoaa.top3[0]` | `isopentyl_acetate` |
| `per_dim.A_esters_isoaa.top3[1]` | `n.hexanol` |
| `per_dim.A_esters_isoaa.top3[2]` | `lactic_acid.mg.L.` |
| `per_dim.A_esters_isoaa.top3_idx[0]` | 15 |
| `per_dim.A_esters_isoaa.top3_idx[1]` | 54 |
| `per_dim.A_esters_isoaa.top3_idx[2]` | 26 |
| `per_dim.A_esters_isoaa.phi[0]` | 0.8478 |
| `per_dim.A_esters_isoaa.phi[1]` | 0.6 |
| `per_dim.A_esters_isoaa.phi[2]` | 0.568 |
| `per_dim.A_esters_isoaa.shap_norm[0]` | 0.6957 |
| `per_dim.A_esters_isoaa.shap_norm[1]` | 1 |
| `per_dim.A_esters_isoaa.shap_norm[2]` | 0.4535 |
| `per_dim.A_esters_isoaa.corr_abs[0]` | 1 |
| `per_dim.A_esters_isoaa.corr_abs[1]` | 0 |
| `per_dim.A_esters_isoaa.corr_abs[2]` | 0.471 |
| `per_dim.A_esters_isoaa.select_freq[0]` | 1 |
| `per_dim.A_esters_isoaa.select_freq[1]` | 1 |
| `per_dim.A_esters_isoaa.select_freq[2]` | 1 |
| `per_dim.A_esters_isoaa.module[0]` | 2 |
| `per_dim.A_esters_isoaa.module[1]` | 2 |
| `per_dim.A_esters_isoaa.module[2]` | 0 |
| `per_dim.A_esters_isoaa.jaccard_cross_method` | 0.3 |
| `per_dim.A_esters_flower.top3[0]` | `ethyl.lactate` |
| `per_dim.A_esters_flower.top3[1]` | `geraniol` |
| `per_dim.A_esters_flower.top3[2]` | `isobutyl_acetate` |
| `per_dim.A_esters_flower.top3_idx[0]` | 52 |
| `per_dim.A_esters_flower.top3_idx[1]` | 127 |
| `per_dim.A_esters_flower.top3_idx[2]` | 14 |
| `per_dim.A_esters_flower.phi[0]` | 0.7 |
| `per_dim.A_esters_flower.phi[1]` | 0.6577 |
| `per_dim.A_esters_flower.phi[2]` | 0.6528 |
| `per_dim.A_esters_flower.shap_norm[0]` | 1 |
| `per_dim.A_esters_flower.shap_norm[1]` | 0.3907 |
| `per_dim.A_esters_flower.shap_norm[2]` | 0.3055 |
| `per_dim.A_esters_flower.corr_abs[0]` | 0 |
| `per_dim.A_esters_flower.corr_abs[1]` | 0.8745 |
| `per_dim.A_esters_flower.corr_abs[2]` | 1 |
| `per_dim.A_esters_flower.select_freq[0]` | 0.994 |
| `per_dim.A_esters_flower.select_freq[1]` | 0.98 |
| `per_dim.A_esters_flower.select_freq[2]` | 0.88 |
| `per_dim.A_esters_flower.module[0]` | 24 |
| `per_dim.A_esters_flower.module[1]` | 4 |
| `per_dim.A_esters_flower.module[2]` | 2 |
| `per_dim.A_esters_flower.jaccard_cross_method` | 0.1667 |
| `per_dim.A_esters_fruity.top3[0]` | `beta.phellandrene` |
| `per_dim.A_esters_fruity.top3[1]` | `lactic_acid.mg.L.` |
| `per_dim.A_esters_fruity.top3[2]` | `iron` |
| `per_dim.A_esters_fruity.top3_idx[0]` | 77 |
| `per_dim.A_esters_fruity.top3_idx[1]` | 26 |
| `per_dim.A_esters_fruity.top3_idx[2]` | 28 |
| `per_dim.A_esters_fruity.phi[0]` | 0.7 |
| `per_dim.A_esters_fruity.phi[1]` | 0.5555 |
| `per_dim.A_esters_fruity.phi[2]` | 0.5494 |
| `per_dim.A_esters_fruity.shap_norm[0]` | 1 |
| `per_dim.A_esters_fruity.shap_norm[1]` | 0.1195 |
| `per_dim.A_esters_fruity.shap_norm[2]` | 0.2957 |
| `per_dim.A_esters_fruity.corr_abs[0]` | 0 |
| `per_dim.A_esters_fruity.corr_abs[1]` | 0.9858 |
| `per_dim.A_esters_fruity.corr_abs[2]` | 0.6718 |
| `per_dim.A_esters_fruity.select_freq[0]` | 1 |
| `per_dim.A_esters_fruity.select_freq[1]` | 1 |
| `per_dim.A_esters_fruity.select_freq[2]` | 1 |
| `per_dim.A_esters_fruity.module[0]` | 4 |
| `per_dim.A_esters_fruity.module[1]` | 0 |
| `per_dim.A_esters_fruity.module[2]` | 18 |
| `per_dim.A_esters_fruity.jaccard_cross_method` | 0 |
| `per_dim.F_malt_all.top3[0]` | `color.EBC.` |
| `per_dim.F_malt_all.top3[1]` | `kcalperc` |
| `per_dim.F_malt_all.top3[2]` | `pH` |
| `per_dim.F_malt_all.top3_idx[0]` | 24 |
| `per_dim.F_malt_all.top3_idx[1]` | 36 |
| `per_dim.F_malt_all.top3_idx[2]` | 29 |
| `per_dim.F_malt_all.phi[0]` | 0.9896 |
| `per_dim.F_malt_all.phi[1]` | 0.7363 |
| `per_dim.F_malt_all.phi[2]` | 0.6091 |
| `per_dim.F_malt_all.shap_norm[0]` | 1 |
| `per_dim.F_malt_all.shap_norm[1]` | 0.4727 |
| `per_dim.F_malt_all.shap_norm[2]` | 0.2697 |
| `per_dim.F_malt_all.corr_abs[0]` | 0.9654 |
| `per_dim.F_malt_all.corr_abs[1]` | 1 |
| `per_dim.F_malt_all.corr_abs[2]` | 0.9144 |
| `per_dim.F_malt_all.select_freq[0]` | 1 |
| `per_dim.F_malt_all.select_freq[1]` | 1 |
| `per_dim.F_malt_all.select_freq[2]` | 1 |
| `per_dim.F_malt_all.module[0]` | 0 |
| `per_dim.F_malt_all.module[1]` | 2 |
| `per_dim.F_malt_all.module[2]` | 8 |
| `per_dim.F_malt_all.jaccard_cross_method` | 0.6667 |
| `per_dim.F_malt_grain.top3[0]` | `acetaldehyde` |
| `per_dim.F_malt_grain.top3[1]` | `octyl_acetate` |
| `per_dim.F_malt_grain.top3[2]` | `X2.3.butanedione` |
| `per_dim.F_malt_grain.top3_idx[0]` | 0 |
| `per_dim.F_malt_grain.top3_idx[1]` | 17 |
| `per_dim.F_malt_grain.top3_idx[2]` | 38 |
| `per_dim.F_malt_grain.phi[0]` | 0.8037 |
| `per_dim.F_malt_grain.phi[1]` | 0.7072 |
| `per_dim.F_malt_grain.phi[2]` | 0.6953 |
| `per_dim.F_malt_grain.shap_norm[0]` | 0.6328 |
| `per_dim.F_malt_grain.shap_norm[1]` | 0.5132 |
| `per_dim.F_malt_grain.shap_norm[2]` | 0.3907 |
| `per_dim.F_malt_grain.corr_abs[0]` | 0.9577 |
| `per_dim.F_malt_grain.corr_abs[1]` | 0.8355 |
| `per_dim.F_malt_grain.corr_abs[2]` | 1 |
| `per_dim.F_malt_grain.select_freq[0]` | 1 |
| `per_dim.F_malt_grain.select_freq[1]` | 0.672 |
| `per_dim.F_malt_grain.select_freq[2]` | 0.976 |
| `per_dim.F_malt_grain.module[0]` | 2 |
| `per_dim.F_malt_grain.module[1]` | 0 |
| `per_dim.F_malt_grain.module[2]` | 5 |
| `per_dim.F_malt_grain.jaccard_cross_method` | 0.0667 |
| `per_dim.F_malt_bread.top3[0]` | `glycerol` |
| `per_dim.F_malt_bread.top3[1]` | `pH` |
| `per_dim.F_malt_bread.top3[2]` | `protein.g.L.` |
| `per_dim.F_malt_bread.top3_idx[0]` | 27 |
| `per_dim.F_malt_bread.top3_idx[1]` | 29 |
| `per_dim.F_malt_bread.top3_idx[2]` | 30 |
| `per_dim.F_malt_bread.phi[0]` | 0.9914 |
| `per_dim.F_malt_bread.phi[1]` | 0.5708 |
| `per_dim.F_malt_bread.phi[2]` | 0.5407 |
| `per_dim.F_malt_bread.shap_norm[0]` | 1 |
| `per_dim.F_malt_bread.shap_norm[1]` | 0.3497 |
| `per_dim.F_malt_bread.shap_norm[2]` | 0.3407 |
| `per_dim.F_malt_bread.corr_abs[0]` | 0.9712 |
| `per_dim.F_malt_bread.corr_abs[1]` | 0.6531 |
| `per_dim.F_malt_bread.corr_abs[2]` | 0.5677 |
| `per_dim.F_malt_bread.select_freq[0]` | 1 |
| `per_dim.F_malt_bread.select_freq[1]` | 1 |
| `per_dim.F_malt_bread.select_freq[2]` | 1 |
| `per_dim.F_malt_bread.module[0]` | 2 |
| `per_dim.F_malt_bread.module[1]` | 8 |
| `per_dim.F_malt_bread.module[2]` | 0 |
| `per_dim.F_malt_bread.jaccard_cross_method` | 0.1667 |
| `per_dim.F_malt_cara.top3[0]` | `color.EBC.` |
| `per_dim.F_malt_cara.top3[1]` | `kcalperc` |
| `per_dim.F_malt_cara.top3[2]` | `GFS` |
| `per_dim.F_malt_cara.top3_idx[0]` | 24 |
| `per_dim.F_malt_cara.top3_idx[1]` | 36 |
| `per_dim.F_malt_cara.top3_idx[2]` | 32 |
| `per_dim.F_malt_cara.phi[0]` | 1 |
| `per_dim.F_malt_cara.phi[1]` | 0.7998 |
| `per_dim.F_malt_cara.phi[2]` | 0.6503 |
| `per_dim.F_malt_cara.shap_norm[0]` | 1 |
| `per_dim.F_malt_cara.shap_norm[1]` | 0.6101 |
| `per_dim.F_malt_cara.shap_norm[2]` | 0.5842 |
| `per_dim.F_malt_cara.corr_abs[0]` | 1 |
| `per_dim.F_malt_cara.corr_abs[1]` | 0.9825 |
| `per_dim.F_malt_cara.corr_abs[2]` | 0.5271 |
| `per_dim.F_malt_cara.select_freq[0]` | 1 |
| `per_dim.F_malt_cara.select_freq[1]` | 1 |
| `per_dim.F_malt_cara.select_freq[2]` | 1 |
| `per_dim.F_malt_cara.module[0]` | 0 |
| `per_dim.F_malt_cara.module[1]` | 2 |
| `per_dim.F_malt_cara.module[2]` | 19 |
| `per_dim.F_malt_cara.jaccard_cross_method` | 0.6667 |
| `per_dim.F_malt_burn.top3[0]` | `color.EBC.` |
| `per_dim.F_malt_burn.top3[1]` | `pH` |
| `per_dim.F_malt_burn.top3[2]` | `ethanol..v.v.` |
| `per_dim.F_malt_burn.top3_idx[0]` | 24 |
| `per_dim.F_malt_burn.top3_idx[1]` | 29 |
| `per_dim.F_malt_burn.top3_idx[2]` | 33 |
| `per_dim.F_malt_burn.phi[0]` | 0.9528 |
| `per_dim.F_malt_burn.phi[1]` | 0.7718 |
| `per_dim.F_malt_burn.phi[2]` | 0.6825 |
| `per_dim.F_malt_burn.shap_norm[0]` | 1 |
| `per_dim.F_malt_burn.shap_norm[1]` | 0.5761 |
| `per_dim.F_malt_burn.shap_norm[2]` | 0.365 |
| `per_dim.F_malt_burn.corr_abs[0]` | 0.8428 |
| `per_dim.F_malt_burn.corr_abs[1]` | 0.9459 |
| `per_dim.F_malt_burn.corr_abs[2]` | 1 |
| `per_dim.F_malt_burn.select_freq[0]` | 1 |
| `per_dim.F_malt_burn.select_freq[1]` | 0.922 |
| `per_dim.F_malt_burn.select_freq[2]` | 0.99 |
| `per_dim.F_malt_burn.module[0]` | 0 |
| `per_dim.F_malt_burn.module[1]` | 8 |
| `per_dim.F_malt_burn.module[2]` | 2 |
| `per_dim.F_malt_burn.jaccard_cross_method` | 0.6667 |
| `per_dim.F_hops_all.top3[0]` | `bitterness` |
| `per_dim.F_hops_all.top3[1]` | `ethyl_octanoate` |
| `per_dim.F_hops_all.top3[2]` | `ethanol..v.v.` |
| `per_dim.F_hops_all.top3_idx[0]` | 31 |
| `per_dim.F_hops_all.top3_idx[1]` | 9 |
| `per_dim.F_hops_all.top3_idx[2]` | 33 |
| `per_dim.F_hops_all.phi[0]` | 1 |
| `per_dim.F_hops_all.phi[1]` | 0.9288 |
| `per_dim.F_hops_all.phi[2]` | 0.509 |
| `per_dim.F_hops_all.shap_norm[0]` | 1 |
| `per_dim.F_hops_all.shap_norm[1]` | 0.9031 |
| `per_dim.F_hops_all.shap_norm[2]` | 0.324 |
| `per_dim.F_hops_all.corr_abs[0]` | 1 |
| `per_dim.F_hops_all.corr_abs[1]` | 0.924 |
| `per_dim.F_hops_all.corr_abs[2]` | 0.8234 |
| `per_dim.F_hops_all.select_freq[0]` | 1 |
| `per_dim.F_hops_all.select_freq[1]` | 1 |
| `per_dim.F_hops_all.select_freq[2]` | 0.9 |
| `per_dim.F_hops_all.module[0]` | 8 |
| `per_dim.F_hops_all.module[1]` | 2 |
| `per_dim.F_hops_all.module[2]` | 2 |
| `per_dim.F_hops_all.jaccard_cross_method` | 0.6667 |
| `per_dim.F_hops_citrus.top3[0]` | `protein.g.L.` |
| `per_dim.F_hops_citrus.top3[1]` | `citronellol` |
| `per_dim.F_hops_citrus.top3[2]` | `CO2.PSI.` |
| `per_dim.F_hops_citrus.top3_idx[0]` | 30 |
| `per_dim.F_hops_citrus.top3_idx[1]` | 120 |
| `per_dim.F_hops_citrus.top3_idx[2]` | 34 |
| `per_dim.F_hops_citrus.phi[0]` | 1 |
| `per_dim.F_hops_citrus.phi[1]` | 0.6427 |
| `per_dim.F_hops_citrus.phi[2]` | 0.6289 |
| `per_dim.F_hops_citrus.shap_norm[0]` | 1 |
| `per_dim.F_hops_citrus.shap_norm[1]` | 0.4146 |
| `per_dim.F_hops_citrus.shap_norm[2]` | 0.4232 |
| `per_dim.F_hops_citrus.corr_abs[0]` | 1 |
| `per_dim.F_hops_citrus.corr_abs[1]` | 0.7846 |
| `per_dim.F_hops_citrus.corr_abs[2]` | 0.7243 |
| `per_dim.F_hops_citrus.select_freq[0]` | 1 |
| `per_dim.F_hops_citrus.select_freq[1]` | 1 |
| `per_dim.F_hops_citrus.select_freq[2]` | 1 |
| `per_dim.F_hops_citrus.module[0]` | 0 |
| `per_dim.F_hops_citrus.module[1]` | 4 |
| `per_dim.F_hops_citrus.module[2]` | 20 |
| `per_dim.F_hops_citrus.jaccard_cross_method` | 0.3 |
| `per_dim.F_hops_tropical.top3[0]` | `DMS` |
| `per_dim.F_hops_tropical.top3[1]` | `nerol.oxide` |
| `per_dim.F_hops_tropical.top3[2]` | `germacrene.D` |
| `per_dim.F_hops_tropical.top3_idx[0]` | 3 |
| `per_dim.F_hops_tropical.top3_idx[1]` | 107 |
| `per_dim.F_hops_tropical.top3_idx[2]` | 170 |
| `per_dim.F_hops_tropical.phi[0]` | 0.8693 |
| `per_dim.F_hops_tropical.phi[1]` | 0.7 |
| `per_dim.F_hops_tropical.phi[2]` | 0.6857 |
| `per_dim.F_hops_tropical.shap_norm[0]` | 0.7583 |
| `per_dim.F_hops_tropical.shap_norm[1]` | 1 |
| `per_dim.F_hops_tropical.shap_norm[2]` | 0.9714 |
| `per_dim.F_hops_tropical.corr_abs[0]` | 0.9669 |
| `per_dim.F_hops_tropical.corr_abs[1]` | 0 |
| `per_dim.F_hops_tropical.corr_abs[2]` | 0 |
| `per_dim.F_hops_tropical.select_freq[0]` | 1 |
| `per_dim.F_hops_tropical.select_freq[1]` | 0.978 |
| `per_dim.F_hops_tropical.select_freq[2]` | 0.934 |
| `per_dim.F_hops_tropical.module[0]` | 2 |
| `per_dim.F_hops_tropical.module[1]` | 1 |
| `per_dim.F_hops_tropical.module[2]` | 0 |
| `per_dim.F_hops_tropical.jaccard_cross_method` | 0 |
| `per_dim.F_hops_noble.top3[0]` | `ethyl_octanoate` |
| `per_dim.F_hops_noble.top3[1]` | `bitterness` |
| `per_dim.F_hops_noble.top3[2]` | `iron` |
| `per_dim.F_hops_noble.top3_idx[0]` | 9 |
| `per_dim.F_hops_noble.top3_idx[1]` | 31 |
| `per_dim.F_hops_noble.top3_idx[2]` | 28 |
| `per_dim.F_hops_noble.phi[0]` | 0.9953 |
| `per_dim.F_hops_noble.phi[1]` | 0.8555 |
| `per_dim.F_hops_noble.phi[2]` | 0.6177 |
| `per_dim.F_hops_noble.shap_norm[0]` | 1 |
| `per_dim.F_hops_noble.shap_norm[1]` | 0.7111 |
| `per_dim.F_hops_noble.shap_norm[2]` | 0.3375 |
| `per_dim.F_hops_noble.corr_abs[0]` | 0.9844 |
| `per_dim.F_hops_noble.corr_abs[1]` | 1 |
| `per_dim.F_hops_noble.corr_abs[2]` | 0.83 |
| `per_dim.F_hops_noble.select_freq[0]` | 1 |
| `per_dim.F_hops_noble.select_freq[1]` | 1 |
| `per_dim.F_hops_noble.select_freq[2]` | 1 |
| `per_dim.F_hops_noble.module[0]` | 2 |
| `per_dim.F_hops_noble.module[1]` | 8 |
| `per_dim.F_hops_noble.module[2]` | 18 |
| `per_dim.F_hops_noble.jaccard_cross_method` | 0.5 |
| `per_dim.F_hops_woody.top3[0]` | `bitterness` |
| `per_dim.F_hops_woody.top3[1]` | `isobutanol` |
| `per_dim.F_hops_woody.top3[2]` | `X.E..2.nonenal` |
| `per_dim.F_hops_woody.top3_idx[0]` | 31 |
| `per_dim.F_hops_woody.top3_idx[1]` | 13 |
| `per_dim.F_hops_woody.top3_idx[2]` | 108 |
| `per_dim.F_hops_woody.phi[0]` | 1 |
| `per_dim.F_hops_woody.phi[1]` | 0.9574 |
| `per_dim.F_hops_woody.phi[2]` | 0.5815 |
| `per_dim.F_hops_woody.shap_norm[0]` | 1 |
| `per_dim.F_hops_woody.shap_norm[1]` | 0.9829 |
| `per_dim.F_hops_woody.shap_norm[2]` | 0.7629 |
| `per_dim.F_hops_woody.corr_abs[0]` | 1 |
| `per_dim.F_hops_woody.corr_abs[1]` | 0.8866 |
| `per_dim.F_hops_woody.corr_abs[2]` | 0 |
| `per_dim.F_hops_woody.select_freq[0]` | 1 |
| `per_dim.F_hops_woody.select_freq[1]` | 1 |
| `per_dim.F_hops_woody.select_freq[2]` | 0.406 |
| `per_dim.F_hops_woody.module[0]` | 8 |
| `per_dim.F_hops_woody.module[1]` | 2 |
| `per_dim.F_hops_woody.module[2]` | 1 |
| `per_dim.F_hops_woody.jaccard_cross_method` | 0.6667 |
| `per_dim.F_esters_all.top3[0]` | `kcalperc` |
| `per_dim.F_esters_all.top3[1]` | `protein.g.L.` |
| `per_dim.F_esters_all.top3[2]` | `ethyl_acetate` |
| `per_dim.F_esters_all.top3_idx[0]` | 36 |
| `per_dim.F_esters_all.top3_idx[1]` | 30 |
| `per_dim.F_esters_all.top3_idx[2]` | 5 |
| `per_dim.F_esters_all.phi[0]` | 1 |
| `per_dim.F_esters_all.phi[1]` | 0.7984 |
| `per_dim.F_esters_all.phi[2]` | 0.6089 |
| `per_dim.F_esters_all.shap_norm[0]` | 1 |
| `per_dim.F_esters_all.shap_norm[1]` | 0.684 |
| `per_dim.F_esters_all.shap_norm[2]` | 0.5387 |
| `per_dim.F_esters_all.corr_abs[0]` | 1 |
| `per_dim.F_esters_all.corr_abs[1]` | 0.8548 |
| `per_dim.F_esters_all.corr_abs[2]` | 0.7983 |
| `per_dim.F_esters_all.select_freq[0]` | 1 |
| `per_dim.F_esters_all.select_freq[1]` | 1 |
| `per_dim.F_esters_all.select_freq[2]` | 1 |
| `per_dim.F_esters_all.module[0]` | 2 |
| `per_dim.F_esters_all.module[1]` | 0 |
| `per_dim.F_esters_all.module[2]` | 2 |
| `per_dim.F_esters_all.jaccard_cross_method` | 0.5 |
| `per_dim.F_esters_ethac.top3[0]` | `ethyl_acetate` |
| `per_dim.F_esters_ethac.top3[1]` | `glycerol` |
| `per_dim.F_esters_ethac.top3[2]` | `acetaldehyde` |
| `per_dim.F_esters_ethac.top3_idx[0]` | 5 |
| `per_dim.F_esters_ethac.top3_idx[1]` | 27 |
| `per_dim.F_esters_ethac.top3_idx[2]` | 0 |
| `per_dim.F_esters_ethac.phi[0]` | 1 |
| `per_dim.F_esters_ethac.phi[1]` | 0.821 |
| `per_dim.F_esters_ethac.phi[2]` | 0.586 |
| `per_dim.F_esters_ethac.shap_norm[0]` | 1 |
| `per_dim.F_esters_ethac.shap_norm[1]` | 0.914 |
| `per_dim.F_esters_ethac.shap_norm[2]` | 0.579 |
| `per_dim.F_esters_ethac.corr_abs[0]` | 1 |
| `per_dim.F_esters_ethac.corr_abs[1]` | 0.88 |
| `per_dim.F_esters_ethac.corr_abs[2]` | 0.7661 |
| `per_dim.F_esters_ethac.select_freq[0]` | 1 |
| `per_dim.F_esters_ethac.select_freq[1]` | 1 |
| `per_dim.F_esters_ethac.select_freq[2]` | 1 |
| `per_dim.F_esters_ethac.module[0]` | 2 |
| `per_dim.F_esters_ethac.module[1]` | 2 |
| `per_dim.F_esters_ethac.module[2]` | 2 |
| `per_dim.F_esters_ethac.jaccard_cross_method` | 0.5 |
| `per_dim.F_esters_isoaa.top3[0]` | `protein.g.L.` |
| `per_dim.F_esters_isoaa.top3[1]` | `isopentyl_acetate` |
| `per_dim.F_esters_isoaa.top3[2]` | `phenethyl_alcohol` |
| `per_dim.F_esters_isoaa.top3_idx[0]` | 30 |
| `per_dim.F_esters_isoaa.top3_idx[1]` | 15 |
| `per_dim.F_esters_isoaa.top3_idx[2]` | 19 |
| `per_dim.F_esters_isoaa.phi[0]` | 0.8679 |
| `per_dim.F_esters_isoaa.phi[1]` | 0.8509 |
| `per_dim.F_esters_isoaa.phi[2]` | 0.8027 |
| `per_dim.F_esters_isoaa.shap_norm[0]` | 0.7906 |
| `per_dim.F_esters_isoaa.shap_norm[1]` | 0.7573 |
| `per_dim.F_esters_isoaa.shap_norm[2]` | 0.926 |
| `per_dim.F_esters_isoaa.corr_abs[0]` | 0.9086 |
| `per_dim.F_esters_isoaa.corr_abs[1]` | 0.9074 |
| `per_dim.F_esters_isoaa.corr_abs[2]` | 0.4657 |
| `per_dim.F_esters_isoaa.select_freq[0]` | 1 |
| `per_dim.F_esters_isoaa.select_freq[1]` | 0.73 |
| `per_dim.F_esters_isoaa.select_freq[2]` | 0.99 |
| `per_dim.F_esters_isoaa.module[0]` | 0 |
| `per_dim.F_esters_isoaa.module[1]` | 2 |
| `per_dim.F_esters_isoaa.module[2]` | 13 |
| `per_dim.F_esters_isoaa.jaccard_cross_method` | 0.0667 |
| `per_dim.F_esters_flower.top3[0]` | `delta.terpinyl.acetate` |
| `per_dim.F_esters_flower.top3[1]` | `ethyl_2.methyl_butyrate` |
| `per_dim.F_esters_flower.top3[2]` | `iron` |
| `per_dim.F_esters_flower.top3_idx[0]` | 137 |
| `per_dim.F_esters_flower.top3_idx[1]` | 4 |
| `per_dim.F_esters_flower.top3_idx[2]` | 28 |
| `per_dim.F_esters_flower.phi[0]` | 0.7 |
| `per_dim.F_esters_flower.phi[1]` | 0.6214 |
| `per_dim.F_esters_flower.phi[2]` | 0.6144 |
| `per_dim.F_esters_flower.shap_norm[0]` | 1 |
| `per_dim.F_esters_flower.shap_norm[1]` | 0.5949 |
| `per_dim.F_esters_flower.shap_norm[2]` | 0.2288 |
| `per_dim.F_esters_flower.corr_abs[0]` | 0 |
| `per_dim.F_esters_flower.corr_abs[1]` | 0.4132 |
| `per_dim.F_esters_flower.corr_abs[2]` | 1 |
| `per_dim.F_esters_flower.select_freq[0]` | 1 |
| `per_dim.F_esters_flower.select_freq[1]` | 0.818 |
| `per_dim.F_esters_flower.select_freq[2]` | 0.53 |
| `per_dim.F_esters_flower.module[0]` | 38 |
| `per_dim.F_esters_flower.module[1]` | 0 |
| `per_dim.F_esters_flower.module[2]` | 18 |
| `per_dim.F_esters_flower.jaccard_cross_method` | 0.0667 |
| `per_dim.F_esters_fruity.top3[0]` | `GFS` |
| `per_dim.F_esters_fruity.top3[1]` | `acetic_acid.g.L.` |
| `per_dim.F_esters_fruity.top3[2]` | `MeSH` |
| `per_dim.F_esters_fruity.top3_idx[0]` | 32 |
| `per_dim.F_esters_fruity.top3_idx[1]` | 22 |
| `per_dim.F_esters_fruity.top3_idx[2]` | 16 |
| `per_dim.F_esters_fruity.phi[0]` | 0.8642 |
| `per_dim.F_esters_fruity.phi[1]` | 0.7598 |
| `per_dim.F_esters_fruity.phi[2]` | 0.7481 |
| `per_dim.F_esters_fruity.shap_norm[0]` | 1 |
| `per_dim.F_esters_fruity.shap_norm[1]` | 0.6174 |
| `per_dim.F_esters_fruity.shap_norm[2]` | 0.666 |
| `per_dim.F_esters_fruity.corr_abs[0]` | 0.5473 |
| `per_dim.F_esters_fruity.corr_abs[1]` | 0.837 |
| `per_dim.F_esters_fruity.corr_abs[2]` | 0.717 |
| `per_dim.F_esters_fruity.select_freq[0]` | 1 |
| `per_dim.F_esters_fruity.select_freq[1]` | 1 |
| `per_dim.F_esters_fruity.select_freq[2]` | 0.996 |
| `per_dim.F_esters_fruity.module[0]` | 19 |
| `per_dim.F_esters_fruity.module[1]` | 0 |
| `per_dim.F_esters_fruity.module[2]` | 2 |
| `per_dim.F_esters_fruity.jaccard_cross_method` | 0.0667 |
| `per_dim.acidity.top3[0]` | `acids_sum` |
| `per_dim.acidity.top3[1]` | `pH` |
| `per_dim.acidity.top3[2]` | `lactic_acid.mg.L.` |
| `per_dim.acidity.top3_idx[0]` | 229 |
| `per_dim.acidity.top3_idx[1]` | 29 |
| `per_dim.acidity.top3_idx[2]` | 26 |
| `per_dim.acidity.phi[0]` | 0.7 |
| `per_dim.acidity.phi[1]` | 0.5976 |
| `per_dim.acidity.phi[2]` | 0.4805 |
| `per_dim.acidity.shap_norm[0]` | 1 |
| `per_dim.acidity.shap_norm[1]` | 0.1952 |
| `per_dim.acidity.shap_norm[2]` | 0.3794 |
| `per_dim.acidity.corr_abs[0]` | 0 |
| `per_dim.acidity.corr_abs[1]` | 1 |
| `per_dim.acidity.corr_abs[2]` | 0.6359 |
| `per_dim.acidity.select_freq[0]` | 1 |
| `per_dim.acidity.select_freq[1]` | 1 |
| `per_dim.acidity.select_freq[2]` | 1 |
| `per_dim.acidity.module[0]` | 0 |
| `per_dim.acidity.module[1]` | 8 |
| `per_dim.acidity.module[2]` | 0 |
| `per_dim.acidity.jaccard_cross_method` | 0.1667 |
| `per_dim.bitternes.top3[0]` | `bitterness` |
| `per_dim.bitternes.top3[1]` | `ethyl_octanoate` |
| `per_dim.bitternes.top3[2]` | `ethyl_decanoate` |
| `per_dim.bitternes.top3_idx[0]` | 31 |
| `per_dim.bitternes.top3_idx[1]` | 9 |
| `per_dim.bitternes.top3_idx[2]` | 6 |
| `per_dim.bitternes.phi[0]` | 1 |
| `per_dim.bitternes.phi[1]` | 0.7737 |
| `per_dim.bitternes.phi[2]` | 0.5252 |
| `per_dim.bitternes.shap_norm[0]` | 1 |
| `per_dim.bitternes.shap_norm[1]` | 0.6261 |
| `per_dim.bitternes.shap_norm[2]` | 0.1589 |
| `per_dim.bitternes.corr_abs[0]` | 1 |
| `per_dim.bitternes.corr_abs[1]` | 0.8688 |
| `per_dim.bitternes.corr_abs[2]` | 0.8193 |
| `per_dim.bitternes.select_freq[0]` | 1 |
| `per_dim.bitternes.select_freq[1]` | 1 |
| `per_dim.bitternes.select_freq[2]` | 1 |
| `per_dim.bitternes.module[0]` | 8 |
| `per_dim.bitternes.module[1]` | 2 |
| `per_dim.bitternes.module[2]` | 1 |
| `per_dim.bitternes.jaccard_cross_method` | 0.5 |
| `per_dim.sweetness.top3[0]` | `GFS` |
| `per_dim.sweetness.top3[1]` | `ethyl_decanoate` |
| `per_dim.sweetness.top3[2]` | `protein.g.L.` |
| `per_dim.sweetness.top3_idx[0]` | 32 |
| `per_dim.sweetness.top3_idx[1]` | 6 |
| `per_dim.sweetness.top3_idx[2]` | 30 |
| `per_dim.sweetness.phi[0]` | 0.986 |
| `per_dim.sweetness.phi[1]` | 0.6832 |
| `per_dim.sweetness.phi[2]` | 0.6098 |
| `per_dim.sweetness.shap_norm[0]` | 1 |
| `per_dim.sweetness.shap_norm[1]` | 0.3663 |
| `per_dim.sweetness.shap_norm[2]` | 0.2664 |
| `per_dim.sweetness.corr_abs[0]` | 0.9535 |
| `per_dim.sweetness.corr_abs[1]` | 1 |
| `per_dim.sweetness.corr_abs[2]` | 0.9219 |
| `per_dim.sweetness.select_freq[0]` | 1 |
| `per_dim.sweetness.select_freq[1]` | 1 |
| `per_dim.sweetness.select_freq[2]` | 0.614 |
| `per_dim.sweetness.module[0]` | 19 |
| `per_dim.sweetness.module[1]` | 1 |
| `per_dim.sweetness.module[2]` | 0 |
| `per_dim.sweetness.jaccard_cross_method` | 0.4 |
| `per_dim.X4vg.top3[0]` | `X4VG` |
| `per_dim.X4vg.top3[1]` | `delta.terpinyl.acetate` |
| `per_dim.X4vg.top3[2]` | `ethyl_isovalerate` |
| `per_dim.X4vg.top3_idx[0]` | 20 |
| `per_dim.X4vg.top3_idx[1]` | 137 |
| `per_dim.X4vg.top3_idx[2]` | 8 |
| `per_dim.X4vg.phi[0]` | 1 |
| `per_dim.X4vg.phi[1]` | 0.5968 |
| `per_dim.X4vg.phi[2]` | 0.4814 |
| `per_dim.X4vg.shap_norm[0]` | 1 |
| `per_dim.X4vg.shap_norm[1]` | 0.7936 |
| `per_dim.X4vg.shap_norm[2]` | 0.1004 |
| `per_dim.X4vg.corr_abs[0]` | 1 |
| `per_dim.X4vg.corr_abs[1]` | 0 |
| `per_dim.X4vg.corr_abs[2]` | 0.7707 |
| `per_dim.X4vg.select_freq[0]` | 1 |
| `per_dim.X4vg.select_freq[1]` | 1 |
| `per_dim.X4vg.select_freq[2]` | 1 |
| `per_dim.X4vg.module[0]` | 14 |
| `per_dim.X4vg.module[1]` | 38 |
| `per_dim.X4vg.module[2]` | 0 |
| `per_dim.X4vg.jaccard_cross_method` | 0.3 |
| `per_dim.diacetyl.top3[0]` | `eugenol` |
| `per_dim.diacetyl.top3[1]` | `ethyl_octanoate` |
| `per_dim.diacetyl.top3[2]` | `ethyl_decanoate` |
| `per_dim.diacetyl.top3_idx[0]` | 145 |
| `per_dim.diacetyl.top3_idx[1]` | 9 |
| `per_dim.diacetyl.top3_idx[2]` | 6 |
| `per_dim.diacetyl.phi[0]` | 0.7 |
| `per_dim.diacetyl.phi[1]` | 0.6481 |
| `per_dim.diacetyl.phi[2]` | 0.5878 |
| `per_dim.diacetyl.shap_norm[0]` | 1 |
| `per_dim.diacetyl.shap_norm[1]` | 0.4136 |
| `per_dim.diacetyl.shap_norm[2]` | 0.1756 |
| `per_dim.diacetyl.corr_abs[0]` | 0 |
| `per_dim.diacetyl.corr_abs[1]` | 0.8045 |
| `per_dim.diacetyl.corr_abs[2]` | 1 |
| `per_dim.diacetyl.select_freq[0]` | 1 |
| `per_dim.diacetyl.select_freq[1]` | 1 |
| `per_dim.diacetyl.select_freq[2]` | 1 |
| `per_dim.diacetyl.module[0]` | 39 |
| `per_dim.diacetyl.module[1]` | 2 |
| `per_dim.diacetyl.module[2]` | 1 |
| `per_dim.diacetyl.jaccard_cross_method` | 0.2333 |
| `per_dim.dms.top3[0]` | `protein.g.L.` |
| `per_dim.dms.top3[1]` | `color.EBC.` |
| `per_dim.dms.top3[2]` | `glycerol` |
| `per_dim.dms.top3_idx[0]` | 30 |
| `per_dim.dms.top3_idx[1]` | 24 |
| `per_dim.dms.top3_idx[2]` | 27 |
| `per_dim.dms.phi[0]` | 1 |
| `per_dim.dms.phi[1]` | 0.7816 |
| `per_dim.dms.phi[2]` | 0.5362 |
| `per_dim.dms.shap_norm[0]` | 1 |
| `per_dim.dms.shap_norm[1]` | 0.9017 |
| `per_dim.dms.shap_norm[2]` | 0.5278 |
| `per_dim.dms.corr_abs[0]` | 1 |
| `per_dim.dms.corr_abs[1]` | 0.7691 |
| `per_dim.dms.corr_abs[2]` | 0.2411 |
| `per_dim.dms.select_freq[0]` | 1 |
| `per_dim.dms.select_freq[1]` | 1 |
| `per_dim.dms.select_freq[2]` | 1 |
| `per_dim.dms.module[0]` | 0 |
| `per_dim.dms.module[1]` | 0 |
| `per_dim.dms.module[2]` | 2 |
| `per_dim.dms.jaccard_cross_method` | 0.5 |
| `per_dim.metallic.top3[0]` | `iron` |
| `per_dim.metallic.top3[1]` | `ethyl_isovalerate` |
| `per_dim.metallic.top3[2]` | `alpha.calacorene` |
| `per_dim.metallic.top3_idx[0]` | 28 |
| `per_dim.metallic.top3_idx[1]` | 8 |
| `per_dim.metallic.top3_idx[2]` | 180 |
| `per_dim.metallic.phi[0]` | 0.9925 |
| `per_dim.metallic.phi[1]` | 0.7693 |
| `per_dim.metallic.phi[2]` | 0.6219 |
| `per_dim.metallic.shap_norm[0]` | 1 |
| `per_dim.metallic.shap_norm[1]` | 0.5386 |
| `per_dim.metallic.shap_norm[2]` | 0.8439 |
| `per_dim.metallic.corr_abs[0]` | 0.9751 |
| `per_dim.metallic.corr_abs[1]` | 1 |
| `per_dim.metallic.corr_abs[2]` | 0 |
| `per_dim.metallic.select_freq[0]` | 1 |
| `per_dim.metallic.select_freq[1]` | 1 |
| `per_dim.metallic.select_freq[2]` | 1 |
| `per_dim.metallic.module[0]` | 18 |
| `per_dim.metallic.module[1]` | 0 |
| `per_dim.metallic.module[2]` | 1 |
| `per_dim.metallic.jaccard_cross_method` | 0.3 |
| `per_dim.stale_hops.top3[0]` | `GFS` |
| `per_dim.stale_hops.top3[1]` | `alloaromadendrene.epoxide` |
| `per_dim.stale_hops.top3[2]` | `ethyl_2.methyl_butyrate` |
| `per_dim.stale_hops.top3_idx[0]` | 32 |
| `per_dim.stale_hops.top3_idx[1]` | 188 |
| `per_dim.stale_hops.top3_idx[2]` | 4 |
| `per_dim.stale_hops.phi[0]` | 0.7234 |
| `per_dim.stale_hops.phi[1]` | 0.7 |
| `per_dim.stale_hops.phi[2]` | 0.5551 |
| `per_dim.stale_hops.shap_norm[0]` | 0.557 |
| `per_dim.stale_hops.shap_norm[1]` | 1 |
| `per_dim.stale_hops.shap_norm[2]` | 0.1102 |
| `per_dim.stale_hops.corr_abs[0]` | 0.8165 |
| `per_dim.stale_hops.corr_abs[1]` | 0 |
| `per_dim.stale_hops.corr_abs[2]` | 1 |
| `per_dim.stale_hops.select_freq[0]` | 1 |
| `per_dim.stale_hops.select_freq[1]` | 1 |
| `per_dim.stale_hops.select_freq[2]` | 1 |
| `per_dim.stale_hops.module[0]` | 19 |
| `per_dim.stale_hops.module[1]` | 1 |
| `per_dim.stale_hops.module[2]` | 0 |
| `per_dim.stale_hops.jaccard_cross_method` | 0.1333 |
| `per_dim.t2n.top3[0]` | `glycerol` |
| `per_dim.t2n.top3[1]` | `geraniol` |
| `per_dim.t2n.top3[2]` | `phenethyl_alcohol` |
| `per_dim.t2n.top3_idx[0]` | 27 |
| `per_dim.t2n.top3_idx[1]` | 127 |
| `per_dim.t2n.top3_idx[2]` | 19 |
| `per_dim.t2n.phi[0]` | 0.9666 |
| `per_dim.t2n.phi[1]` | 0.7831 |
| `per_dim.t2n.phi[2]` | 0.7362 |
| `per_dim.t2n.shap_norm[0]` | 1 |
| `per_dim.t2n.shap_norm[1]` | 0.5662 |
| `per_dim.t2n.shap_norm[2]` | 0.6136 |
| `per_dim.t2n.corr_abs[0]` | 0.8887 |
| `per_dim.t2n.corr_abs[1]` | 1 |
| `per_dim.t2n.corr_abs[2]` | 0.7646 |
| `per_dim.t2n.select_freq[0]` | 1 |
| `per_dim.t2n.select_freq[1]` | 1 |
| `per_dim.t2n.select_freq[2]` | 0.996 |
| `per_dim.t2n.module[0]` | 2 |
| `per_dim.t2n.module[1]` | 4 |
| `per_dim.t2n.module[2]` | 13 |
| `per_dim.t2n.jaccard_cross_method` | 0.2 |
| `per_dim.orange.top3[0]` | `ethyl..E..linalool` |
| `per_dim.orange.top3[1]` | `bitterness` |
| `per_dim.orange.top3[2]` | `aroma_hops_sum` |
| `per_dim.orange.top3_idx[0]` | 118 |
| `per_dim.orange.top3_idx[1]` | 31 |
| `per_dim.orange.top3_idx[2]` | 228 |
| `per_dim.orange.phi[0]` | 0.7 |
| `per_dim.orange.phi[1]` | 0.5186 |
| `per_dim.orange.phi[2]` | 0.5106 |
| `per_dim.orange.shap_norm[0]` | 1 |
| `per_dim.orange.shap_norm[1]` | 0.241 |
| `per_dim.orange.shap_norm[2]` | 0.8211 |
| `per_dim.orange.corr_abs[0]` | 0 |
| `per_dim.orange.corr_abs[1]` | 0.6604 |
| `per_dim.orange.corr_abs[2]` | 0 |
| `per_dim.orange.select_freq[0]` | 1 |
| `per_dim.orange.select_freq[1]` | 0.948 |
| `per_dim.orange.select_freq[2]` | 0.554 |
| `per_dim.orange.module[0]` | 4 |
| `per_dim.orange.module[1]` | 8 |
| `per_dim.orange.module[2]` | 4 |
| `per_dim.orange.jaccard_cross_method` | 0 |
| `per_dim.coriander.top3[0]` | `ethyl..E..linalool` |
| `per_dim.coriander.top3[1]` | `acetaldehyde` |
| `per_dim.coriander.top3[2]` | `X4VG` |
| `per_dim.coriander.top3_idx[0]` | 118 |
| `per_dim.coriander.top3_idx[1]` | 0 |
| `per_dim.coriander.top3_idx[2]` | 20 |
| `per_dim.coriander.phi[0]` | 0.7 |
| `per_dim.coriander.phi[1]` | 0.6051 |
| `per_dim.coriander.phi[2]` | 0.596 |
| `per_dim.coriander.shap_norm[0]` | 1 |
| `per_dim.coriander.shap_norm[1]` | 0.2103 |
| `per_dim.coriander.shap_norm[2]` | 0.1977 |
| `per_dim.coriander.corr_abs[0]` | 0 |
| `per_dim.coriander.corr_abs[1]` | 1 |
| `per_dim.coriander.corr_abs[2]` | 0.9906 |
| `per_dim.coriander.select_freq[0]` | 0.804 |
| `per_dim.coriander.select_freq[1]` | 0.974 |
| `per_dim.coriander.select_freq[2]` | 0.75 |
| `per_dim.coriander.module[0]` | 4 |
| `per_dim.coriander.module[1]` | 2 |
| `per_dim.coriander.module[2]` | 14 |
| `per_dim.coriander.jaccard_cross_method` | 0.1667 |
| `per_dim.clove.top3[0]` | `X2.3.butanedione` |
| `per_dim.clove.top3[1]` | `X4VG` |
| `per_dim.clove.top3[2]` | `eucalyptol` |
| `per_dim.clove.top3_idx[0]` | 38 |
| `per_dim.clove.top3_idx[1]` | 20 |
| `per_dim.clove.top3_idx[2]` | 79 |
| `per_dim.clove.phi[0]` | 0.7721 |
| `per_dim.clove.phi[1]` | 0.7333 |
| `per_dim.clove.phi[2]` | 0.7 |
| `per_dim.clove.shap_norm[0]` | 0.5442 |
| `per_dim.clove.shap_norm[1]` | 0.5317 |
| `per_dim.clove.shap_norm[2]` | 1 |
| `per_dim.clove.corr_abs[0]` | 1 |
| `per_dim.clove.corr_abs[1]` | 0.8915 |
| `per_dim.clove.corr_abs[2]` | 0 |
| `per_dim.clove.select_freq[0]` | 1 |
| `per_dim.clove.select_freq[1]` | 0.96 |
| `per_dim.clove.select_freq[2]` | 0.648 |
| `per_dim.clove.module[0]` | 5 |
| `per_dim.clove.module[1]` | 14 |
| `per_dim.clove.module[2]` | 30 |
| `per_dim.clove.jaccard_cross_method` | 0.0667 |
| `per_dim.lactic.top3[0]` | `pH` |
| `per_dim.lactic.top3[1]` | `lactic_acid.mg.L.` |
| `per_dim.lactic.top3[2]` | `isopentyl_acetate` |
| `per_dim.lactic.top3_idx[0]` | 29 |
| `per_dim.lactic.top3_idx[1]` | 26 |
| `per_dim.lactic.top3_idx[2]` | 15 |
| `per_dim.lactic.phi[0]` | 0.9942 |
| `per_dim.lactic.phi[1]` | 0.7898 |
| `per_dim.lactic.phi[2]` | 0.5906 |
| `per_dim.lactic.shap_norm[0]` | 1 |
| `per_dim.lactic.shap_norm[1]` | 0.5796 |
| `per_dim.lactic.shap_norm[2]` | 0.2318 |
| `per_dim.lactic.corr_abs[0]` | 0.9807 |
| `per_dim.lactic.corr_abs[1]` | 1 |
| `per_dim.lactic.corr_abs[2]` | 0.9159 |
| `per_dim.lactic.select_freq[0]` | 1 |
| `per_dim.lactic.select_freq[1]` | 1 |
| `per_dim.lactic.select_freq[2]` | 0.988 |
| `per_dim.lactic.module[0]` | 8 |
| `per_dim.lactic.module[1]` | 0 |
| `per_dim.lactic.module[2]` | 2 |
| `per_dim.lactic.jaccard_cross_method` | 0.6667 |
| `per_dim.acetic.top3[0]` | `pH` |
| `per_dim.acetic.top3[1]` | `acids_sum` |
| `per_dim.acetic.top3[2]` | `ethyl_isovalerate` |
| `per_dim.acetic.top3_idx[0]` | 29 |
| `per_dim.acetic.top3_idx[1]` | 229 |
| `per_dim.acetic.top3_idx[2]` | 8 |
| `per_dim.acetic.phi[0]` | 0.7424 |
| `per_dim.acetic.phi[1]` | 0.7 |
| `per_dim.acetic.phi[2]` | 0.5878 |
| `per_dim.acetic.shap_norm[0]` | 0.5713 |
| `per_dim.acetic.shap_norm[1]` | 1 |
| `per_dim.acetic.shap_norm[2]` | 0.3756 |
| `per_dim.acetic.corr_abs[0]` | 0.856 |
| `per_dim.acetic.corr_abs[1]` | 0 |
| `per_dim.acetic.corr_abs[2]` | 1 |
| `per_dim.acetic.select_freq[0]` | 1 |
| `per_dim.acetic.select_freq[1]` | 0.998 |
| `per_dim.acetic.select_freq[2]` | 0.846 |
| `per_dim.acetic.module[0]` | 8 |
| `per_dim.acetic.module[1]` | 0 |
| `per_dim.acetic.module[2]` | 0 |
| `per_dim.acetic.jaccard_cross_method` | 0.4 |
| `per_dim.barnyard.top3[0]` | `alloaromadendrene.epoxide` |
| `per_dim.barnyard.top3[1]` | `GFS` |
| `per_dim.barnyard.top3[2]` | `ethyl_2.methyl_butyrate` |
| `per_dim.barnyard.top3_idx[0]` | 188 |
| `per_dim.barnyard.top3_idx[1]` | 32 |
| `per_dim.barnyard.top3_idx[2]` | 4 |
| `per_dim.barnyard.phi[0]` | 0.7 |
| `per_dim.barnyard.phi[1]` | 0.6623 |
| `per_dim.barnyard.phi[2]` | 0.5071 |
| `per_dim.barnyard.shap_norm[0]` | 1 |
| `per_dim.barnyard.shap_norm[1]` | 0.4164 |
| `per_dim.barnyard.shap_norm[2]` | 0.0142 |
| `per_dim.barnyard.corr_abs[0]` | 0 |
| `per_dim.barnyard.corr_abs[1]` | 0.847 |
| `per_dim.barnyard.corr_abs[2]` | 1 |
| `per_dim.barnyard.select_freq[0]` | 1 |
| `per_dim.barnyard.select_freq[1]` | 1 |
| `per_dim.barnyard.select_freq[2]` | 0.99 |
| `per_dim.barnyard.module[0]` | 1 |
| `per_dim.barnyard.module[1]` | 19 |
| `per_dim.barnyard.module[2]` | 0 |
| `per_dim.barnyard.jaccard_cross_method` | 0.0667 |
| `per_dim.alcohol.top3[0]` | `ethanol..v.v.` |
| `per_dim.alcohol.top3[1]` | `kcalperc` |
| `per_dim.alcohol.top3[2]` | `CO2.PSI.` |
| `per_dim.alcohol.top3_idx[0]` | 33 |
| `per_dim.alcohol.top3_idx[1]` | 36 |
| `per_dim.alcohol.top3_idx[2]` | 34 |
| `per_dim.alcohol.phi[0]` | 1 |
| `per_dim.alcohol.phi[1]` | 0.5686 |
| `per_dim.alcohol.phi[2]` | 0.4842 |
| `per_dim.alcohol.shap_norm[0]` | 1 |
| `per_dim.alcohol.shap_norm[1]` | 0.4014 |
| `per_dim.alcohol.shap_norm[2]` | 0.2398 |
| `per_dim.alcohol.corr_abs[0]` | 1 |
| `per_dim.alcohol.corr_abs[1]` | 0.893 |
| `per_dim.alcohol.corr_abs[2]` | 0.5478 |
| `per_dim.alcohol.select_freq[0]` | 1 |
| `per_dim.alcohol.select_freq[1]` | 1 |
| `per_dim.alcohol.select_freq[2]` | 0.978 |
| `per_dim.alcohol.module[0]` | 2 |
| `per_dim.alcohol.module[1]` | 2 |
| `per_dim.alcohol.module[2]` | 20 |
| `per_dim.alcohol.jaccard_cross_method` | 0.6667 |
| `per_dim.aftertaste.top3[0]` | `ethyl_octanoate` |
| `per_dim.aftertaste.top3[1]` | `bitterness` |
| `per_dim.aftertaste.top3[2]` | `ethyl_decanoate` |
| `per_dim.aftertaste.top3_idx[0]` | 9 |
| `per_dim.aftertaste.top3_idx[1]` | 31 |
| `per_dim.aftertaste.top3_idx[2]` | 6 |
| `per_dim.aftertaste.phi[0]` | 0.8076 |
| `per_dim.aftertaste.phi[1]` | 0.8024 |
| `per_dim.aftertaste.phi[2]` | 0.5385 |
| `per_dim.aftertaste.shap_norm[0]` | 0.6151 |
| `per_dim.aftertaste.shap_norm[1]` | 1 |
| `per_dim.aftertaste.shap_norm[2]` | 0.2117 |
| `per_dim.aftertaste.corr_abs[0]` | 1 |
| `per_dim.aftertaste.corr_abs[1]` | 0.3415 |
| `per_dim.aftertaste.corr_abs[2]` | 0.7754 |
| `per_dim.aftertaste.select_freq[0]` | 1 |
| `per_dim.aftertaste.select_freq[1]` | 1 |
| `per_dim.aftertaste.select_freq[2]` | 0.69 |
| `per_dim.aftertaste.module[0]` | 2 |
| `per_dim.aftertaste.module[1]` | 8 |
| `per_dim.aftertaste.module[2]` | 1 |
| `per_dim.aftertaste.jaccard_cross_method` | 0.4 |
| `per_dim.body.top3[0]` | `ethanol..v.v.` |
| `per_dim.body.top3[1]` | `kcalperc` |
| `per_dim.body.top3[2]` | `ethyl_decanoate` |
| `per_dim.body.top3_idx[0]` | 33 |
| `per_dim.body.top3_idx[1]` | 36 |
| `per_dim.body.top3_idx[2]` | 6 |
| `per_dim.body.phi[0]` | 1 |
| `per_dim.body.phi[1]` | 0.7052 |
| `per_dim.body.phi[2]` | 0.4926 |
| `per_dim.body.shap_norm[0]` | 1 |
| `per_dim.body.shap_norm[1]` | 0.7008 |
| `per_dim.body.shap_norm[2]` | 0.018 |
| `per_dim.body.corr_abs[0]` | 1 |
| `per_dim.body.corr_abs[1]` | 0.8492 |
| `per_dim.body.corr_abs[2]` | 0.9453 |
| `per_dim.body.select_freq[0]` | 1 |
| `per_dim.body.select_freq[1]` | 1 |
| `per_dim.body.select_freq[2]` | 0.972 |
| `per_dim.body.module[0]` | 2 |
| `per_dim.body.module[1]` | 2 |
| `per_dim.body.module[2]` | 1 |
| `per_dim.body.jaccard_cross_method` | 0.3 |
| `per_dim.co2.top3[0]` | `ethyl_octanoate` |
| `per_dim.co2.top3[1]` | `CO2.PSI.` |
| `per_dim.co2.top3[2]` | `ethyl_hexanoate` |
| `per_dim.co2.top3_idx[0]` | 9 |
| `per_dim.co2.top3_idx[1]` | 34 |
| `per_dim.co2.top3_idx[2]` | 7 |
| `per_dim.co2.phi[0]` | 0.9019 |
| `per_dim.co2.phi[1]` | 0.7865 |
| `per_dim.co2.phi[2]` | 0.5292 |
| `per_dim.co2.shap_norm[0]` | 0.9609 |
| `per_dim.co2.shap_norm[1]` | 1 |
| `per_dim.co2.shap_norm[2]` | 0.3956 |
| `per_dim.co2.corr_abs[0]` | 0.7381 |
| `per_dim.co2.corr_abs[1]` | 0.2882 |
| `per_dim.co2.corr_abs[2]` | 0.7713 |
| `per_dim.co2.select_freq[0]` | 1 |
| `per_dim.co2.select_freq[1]` | 1 |
| `per_dim.co2.select_freq[2]` | 1 |
| `per_dim.co2.module[0]` | 2 |
| `per_dim.co2.module[1]` | 20 |
| `per_dim.co2.module[2]` | 2 |
| `per_dim.co2.jaccard_cross_method` | 0.2333 |
| `per_dim.overall.top3[0]` | `ethyl_acetate` |
| `per_dim.overall.top3[1]` | `cis.linalool.oxide` |
| `per_dim.overall.top3[2]` | `unfermentables` |
| `per_dim.overall.top3_idx[0]` | 5 |
| `per_dim.overall.top3_idx[1]` | 91 |
| `per_dim.overall.top3_idx[2]` | 35 |
| `per_dim.overall.phi[0]` | 0.9459 |
| `per_dim.overall.phi[1]` | 0.6733 |
| `per_dim.overall.phi[2]` | 0.6 |
| `per_dim.overall.shap_norm[0]` | 0.8918 |
| `per_dim.overall.shap_norm[1]` | 0.9465 |
| `per_dim.overall.shap_norm[2]` | 1 |
| `per_dim.overall.corr_abs[0]` | 1 |
| `per_dim.overall.corr_abs[1]` | 0 |
| `per_dim.overall.corr_abs[2]` | 0 |
| `per_dim.overall.select_freq[0]` | 1 |
| `per_dim.overall.select_freq[1]` | 1 |
| `per_dim.overall.select_freq[2]` | 0.576 |
| `per_dim.overall.module[0]` | 2 |
| `per_dim.overall.module[1]` | 31 |
| `per_dim.overall.module[2]` | 2 |
| `per_dim.overall.jaccard_cross_method` | 0.3 |
| `sensory_cols[0]` | `A_malt_all` |
| `sensory_cols[1]` | `A_malt_grain` |
| `sensory_cols[2]` | `A_malt_bread` |
| `sensory_cols[49]` | `overall` |
| `sensory_cols[3..48]` | `<省略中间 46 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `submission.path` | `submission/q2_top3_compounds.csv` |
| `submission.rows` | 150 |
| `graph.n_nodes` | 231 |
| `graph.n_edges` | 645 |
| `graph.n_communities` | 62 |
| `graph.method` | `greedy_modularity` |
| `graph.modularity` | 0.6382 |
| `graph.rho` | 0.5 |
| `fig_data.network_nodes[0].id` | 131 |
| `fig_data.network_nodes[0].name` | `Neryl formate` |
| `fig_data.network_nodes[0].deg` | 11 |
| `fig_data.network_nodes[0].comm` | 0 |
| `fig_data.network_nodes[1].id` | 5 |
| `fig_data.network_nodes[1].name` | `Ethyl acetate` |
| `fig_data.network_nodes[1].deg` | 11 |
| `fig_data.network_nodes[1].comm` | 2 |
| `fig_data.network_nodes[2].id` | 134 |
| `fig_data.network_nodes[2].name` | `Trans-dihydro-α-terpinyl acetate` |
| `fig_data.network_nodes[2].deg` | 22 |
| `fig_data.network_nodes[2].comm` | 1 |
| `fig_data.network_nodes[59].id` | 126 |
| `fig_data.network_nodes[59].name` | `Isopentyl hexanoate` |
| `fig_data.network_nodes[59].deg` | 21 |
| `fig_data.network_nodes[59].comm` | 1 |
| `fig_data.network_nodes[3..58]` | `<省略中间 56 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.network_edges[0].s` | 131 |
| `fig_data.network_edges[0].t` | 66 |
| `fig_data.network_edges[0].w` | 0.562 |
| `fig_data.network_edges[1].s` | 131 |
| `fig_data.network_edges[1].t` | 68 |
| `fig_data.network_edges[1].w` | 0.506 |
| `fig_data.network_edges[2].s` | 131 |
| `fig_data.network_edges[2].t` | 84 |
| `fig_data.network_edges[2].w` | 0.621 |
| `fig_data.network_edges[344].s` | 114 |
| `fig_data.network_edges[344].t` | 118 |
| `fig_data.network_edges[344].w` | 0.759 |
| `fig_data.network_edges[3..343]` | `<省略中间 341 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.community_sizes[0]` | 47 |
| `fig_data.community_sizes[1]` | 37 |
| `fig_data.community_sizes[2]` | 23 |
| `fig_data.community_sizes[61]` | 1 |
| `fig_data.community_sizes[3..60]` | `<省略中间 58 项；数值范围 [1, 47]；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.top1_freq_ranked[0][0]` | `A_malt_all` |
| `fig_data.top1_freq_ranked[0][1]` | 1 |
| `fig_data.top1_freq_ranked[0][2]` | 0.6667 |
| `fig_data.top1_freq_ranked[1][0]` | `A_malt_bread` |
| `fig_data.top1_freq_ranked[1][1]` | 1 |
| `fig_data.top1_freq_ranked[1][2]` | 0.3 |
| `fig_data.top1_freq_ranked[2][0]` | `A_malt_cara` |
| `fig_data.top1_freq_ranked[2][1]` | 1 |
| `fig_data.top1_freq_ranked[2][2]` | 0.3 |
| `fig_data.top1_freq_ranked[49][0]` | `coriander` |
| `fig_data.top1_freq_ranked[49][1]` | 0.804 |
| `fig_data.top1_freq_ranked[49][2]` | 0.1667 |
| `fig_data.top1_freq_ranked[3..48]` | `<省略中间 46 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |

### `problem_3_results.json`（208 条）

| 数据路径 | 数值 |
|---|---|
| `problem` | 3 |
| `method` | `CVAE条件生成(torch,重参数化+KL,掩码重构) + 隐空间迁移 + 缺陷投影 + 高斯兜底` |
| `summary.n_generated` | 90 |
| `summary.n_transfer` | 11 |
| `summary.gen_styles[0]` | `Tripel` |
| `summary.gen_styles[1]` | `Kriek` |
| `summary.gen_styles[2]` | `Lambic` |
| `summary.transfer` | `['Pils/Lager']->Tripel` |
| `summary.latent_dim` | 16 |
| `summary.beta_kl` | 0.1 |
| `summary.defect_compliance_rate` | 1 |
| `summary.ks_distance_by_style.Tripel` | 0.3573 |
| `summary.ks_distance_by_style.Kriek` | 0.3983 |
| `summary.ks_distance_by_style.Lambic` | 0.4084 |
| `summary.gen_tripel_ester_level` | 3.9 |
| `summary.real_tripel_ester_level` | 3.2143 |
| `summary.gen_dim` | 231 |
| `transfer_info.compliance_rate` | 1 |
| `transfer_info.n_checks` | 44 |
| `transfer_info.n_compliant` | 44 |
| `transfer_info.per_defect.DMS.n` | 11 |
| `transfer_info.per_defect.DMS.n_compliant` | 11 |
| `transfer_info.per_defect.DMS.before_mean` | 1.1577 |
| `transfer_info.per_defect.DMS.after_mean` | 1.5556 |
| `transfer_info.per_defect.DMS.m_t` | 1.5873 |
| `transfer_info.per_defect.DMS.delta_mean` | 0.3979 |
| `transfer_info.per_defect.Diacetyl.n` | 11 |
| `transfer_info.per_defect.Diacetyl.n_compliant` | 11 |
| `transfer_info.per_defect.Diacetyl.before_mean` | 0.169 |
| `transfer_info.per_defect.Diacetyl.after_mean` | -2.2602 |
| `transfer_info.per_defect.Diacetyl.m_t` | 0.2896 |
| `transfer_info.per_defect.Diacetyl.delta_mean` | -2.4292 |
| `transfer_info.per_defect.4VG.n` | 11 |
| `transfer_info.per_defect.4VG.n_compliant` | 11 |
| `transfer_info.per_defect.4VG.before_mean` | -1.8794 |
| `transfer_info.per_defect.4VG.after_mean` | -1.9755 |
| `transfer_info.per_defect.4VG.m_t` | -2.0132 |
| `transfer_info.per_defect.4VG.delta_mean` | -0.0962 |
| `transfer_info.per_defect.trans-2-nonenal.n` | 11 |
| `transfer_info.per_defect.trans-2-nonenal.n_compliant` | 11 |
| `transfer_info.per_defect.trans-2-nonenal.before_mean` | 0.0039 |
| `transfer_info.per_defect.trans-2-nonenal.after_mean` | -0.017 |
| `transfer_info.per_defect.trans-2-nonenal.m_t` | 0.0114 |
| `transfer_info.per_defect.trans-2-nonenal.delta_mean` | -0.0209 |
| `transfer_info.defect_cols[0]` | `DMS` |
| `transfer_info.defect_cols[1]` | `X2.3.butanedione` |
| `transfer_info.defect_cols[2]` | `X4VG` |
| `transfer_info.defect_cols[3]` | `X.E..2.nonenal` |
| `transfer_info.defect_no_chem[0]` | `Stale hops` |
| `transfer_info.m_t.DMS` | 1.5873 |
| `transfer_info.m_t.Diacetyl` | 0.2896 |
| `transfer_info.m_t.4VG` | -2.0132 |
| `transfer_info.m_t.trans-2-nonenal` | 0.0114 |
| `fig_data.pca.real[0].x` | 1.249 |
| `fig_data.pca.real[0].y` | -3.762 |
| `fig_data.pca.real[0].style` | `Pils/Lager` |
| `fig_data.pca.real[1].x` | 1.42 |
| `fig_data.pca.real[1].y` | -4.201 |
| `fig_data.pca.real[1].style` | `Kriek` |
| `fig_data.pca.real[2].x` | 0.192 |
| `fig_data.pca.real[2].y` | -1.714 |
| `fig_data.pca.real[2].style` | `Pils/Lager` |
| `fig_data.pca.real[59].x` | -35.12 |
| `fig_data.pca.real[59].y` | 0.856 |
| `fig_data.pca.real[59].style` | `Tripel` |
| `fig_data.pca.real[3..58]` | `<省略中间 56 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.pca.gen[0].x` | -2.236 |
| `fig_data.pca.gen[0].y` | 3.574 |
| `fig_data.pca.gen[0].style` | `Tripel` |
| `fig_data.pca.gen[1].x` | -1.19 |
| `fig_data.pca.gen[1].y` | 4.455 |
| `fig_data.pca.gen[1].style` | `Tripel` |
| `fig_data.pca.gen[2].x` | 0.137 |
| `fig_data.pca.gen[2].y` | 3.757 |
| `fig_data.pca.gen[2].style` | `Tripel` |
| `fig_data.pca.gen[89].x` | 2.938 |
| `fig_data.pca.gen[89].y` | -6.42 |
| `fig_data.pca.gen[89].style` | `Lambic` |
| `fig_data.pca.gen[3..88]` | `<省略中间 86 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.pca.explained_var[0]` | 0.1396 |
| `fig_data.pca.explained_var[1]` | 0.0789 |
| `fig_data.radar.dims[0]` | `A_malt_all` |
| `fig_data.radar.dims[1]` | `A_malt_grain` |
| `fig_data.radar.dims[2]` | `A_malt_bread` |
| `fig_data.radar.dims[29]` | `F_esters_fruity` |
| `fig_data.radar.dims[3..28]` | `<省略中间 26 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `fig_data.radar.by_style.Tripel.A_malt_all` | 2.733 |
| `fig_data.radar.by_style.Tripel.A_malt_grain` | 3.5 |
| `fig_data.radar.by_style.Tripel.A_malt_bread` | 3.833 |
| `fig_data.radar.by_style.Tripel.A_malt_cara` | 3.167 |
| `fig_data.radar.by_style.Tripel.A_malt_burn` | 1.867 |
| `fig_data.radar.by_style.Tripel.A_hops_all` | 3.733 |
| `fig_data.radar.by_style.Tripel.A_hops_citrus` | 3.767 |
| `fig_data.radar.by_style.Tripel.A_hops_tropical` | 4.2 |
| `fig_data.radar.by_style.Tripel.A_hops_noble` | 3.733 |
| `fig_data.radar.by_style.Tripel.A_hops_woody` | 2.833 |
| `fig_data.radar.by_style.Tripel.A_esters_all` | 3.9 |
| `fig_data.radar.by_style.Tripel.A_esters_ethac` | 3.967 |
| `fig_data.radar.by_style.Tripel.A_esters_isoaa` | 4.133 |
| `fig_data.radar.by_style.Tripel.A_esters_flower` | 3.167 |
| `fig_data.radar.by_style.Tripel.A_esters_fruity` | 3.2 |
| `fig_data.radar.by_style.Tripel.F_malt_all` | 2.933 |
| `fig_data.radar.by_style.Tripel.F_malt_grain` | 3.733 |
| `fig_data.radar.by_style.Tripel.F_malt_bread` | 4.1 |
| `fig_data.radar.by_style.Tripel.F_malt_cara` | 2.9 |
| `fig_data.radar.by_style.Tripel.F_malt_burn` | 3 |
| `fig_data.radar.by_style.Tripel.F_hops_all` | 4.1 |
| `fig_data.radar.by_style.Tripel.F_hops_citrus` | 3.567 |
| `fig_data.radar.by_style.Tripel.F_hops_tropical` | 3.8 |
| `fig_data.radar.by_style.Tripel.F_hops_noble` | 4.067 |
| `fig_data.radar.by_style.Tripel.F_hops_woody` | 4.033 |
| `fig_data.radar.by_style.Tripel.F_esters_all` | 3.567 |
| `fig_data.radar.by_style.Tripel.F_esters_ethac` | 4.233 |
| `fig_data.radar.by_style.Tripel.F_esters_isoaa` | 4.067 |
| `fig_data.radar.by_style.Tripel.F_esters_flower` | 3.3 |
| `fig_data.radar.by_style.Tripel.F_esters_fruity` | 1.933 |
| `fig_data.radar.by_style.Kriek.A_malt_all` | 1.233 |
| `fig_data.radar.by_style.Kriek.A_malt_grain` | 3.233 |
| `fig_data.radar.by_style.Kriek.A_malt_bread` | 2.5 |
| `fig_data.radar.by_style.Kriek.A_malt_cara` | 1.5 |
| `fig_data.radar.by_style.Kriek.A_malt_burn` | 3.133 |
| `fig_data.radar.by_style.Kriek.A_hops_all` | 0.9 |
| `fig_data.radar.by_style.Kriek.A_hops_citrus` | 2.4 |
| `fig_data.radar.by_style.Kriek.A_hops_tropical` | 3.2 |
| `fig_data.radar.by_style.Kriek.A_hops_noble` | 1.167 |
| `fig_data.radar.by_style.Kriek.A_hops_woody` | 3.5 |
| `fig_data.radar.by_style.Kriek.A_esters_all` | 5.067 |
| `fig_data.radar.by_style.Kriek.A_esters_ethac` | 2.733 |
| `fig_data.radar.by_style.Kriek.A_esters_isoaa` | 4.633 |
| `fig_data.radar.by_style.Kriek.A_esters_flower` | 5.033 |
| `fig_data.radar.by_style.Kriek.A_esters_fruity` | 5.9 |
| `fig_data.radar.by_style.Kriek.F_malt_all` | 0.367 |
| `fig_data.radar.by_style.Kriek.F_malt_grain` | 2.3 |
| `fig_data.radar.by_style.Kriek.F_malt_bread` | 1 |
| `fig_data.radar.by_style.Kriek.F_malt_cara` | 1.267 |
| `fig_data.radar.by_style.Kriek.F_malt_burn` | 3.433 |
| `fig_data.radar.by_style.Kriek.F_hops_all` | 0.733 |
| `fig_data.radar.by_style.Kriek.F_hops_citrus` | 2.4 |
| `fig_data.radar.by_style.Kriek.F_hops_tropical` | 3.967 |
| `fig_data.radar.by_style.Kriek.F_hops_noble` | 0.8 |
| `fig_data.radar.by_style.Kriek.F_hops_woody` | 3.733 |
| `fig_data.radar.by_style.Kriek.F_esters_all` | 4.467 |
| `fig_data.radar.by_style.Kriek.F_esters_ethac` | 4.167 |
| `fig_data.radar.by_style.Kriek.F_esters_isoaa` | 3.5 |
| `fig_data.radar.by_style.Kriek.F_esters_flower` | 5.2 |
| `fig_data.radar.by_style.Kriek.F_esters_fruity` | 5.867 |
| `fig_data.radar.by_style.Lambic.A_malt_all` | 2.533 |
| `fig_data.radar.by_style.Lambic.A_malt_grain` | 3.6 |
| `fig_data.radar.by_style.Lambic.A_malt_bread` | 2.267 |
| `fig_data.radar.by_style.Lambic.A_malt_cara` | 2.733 |
| `fig_data.radar.by_style.Lambic.A_malt_burn` | 3.067 |
| `fig_data.radar.by_style.Lambic.A_hops_all` | 1.667 |
| `fig_data.radar.by_style.Lambic.A_hops_citrus` | 2.533 |
| `fig_data.radar.by_style.Lambic.A_hops_tropical` | 2.333 |
| `fig_data.radar.by_style.Lambic.A_hops_noble` | 2.7 |
| `fig_data.radar.by_style.Lambic.A_hops_woody` | 3.767 |
| `fig_data.radar.by_style.Lambic.A_esters_all` | 2.8 |
| `fig_data.radar.by_style.Lambic.A_esters_ethac` | 2.767 |
| `fig_data.radar.by_style.Lambic.A_esters_isoaa` | 2.733 |
| `fig_data.radar.by_style.Lambic.A_esters_flower` | 3.167 |
| `fig_data.radar.by_style.Lambic.A_esters_fruity` | 3.7 |
| `fig_data.radar.by_style.Lambic.F_malt_all` | 1.5 |
| `fig_data.radar.by_style.Lambic.F_malt_grain` | 2.967 |
| `fig_data.radar.by_style.Lambic.F_malt_bread` | 1.533 |
| `fig_data.radar.by_style.Lambic.F_malt_cara` | 1.6 |
| `fig_data.radar.by_style.Lambic.F_malt_burn` | 2.233 |
| `fig_data.radar.by_style.Lambic.F_hops_all` | 1.6 |
| `fig_data.radar.by_style.Lambic.F_hops_citrus` | 3.4 |
| `fig_data.radar.by_style.Lambic.F_hops_tropical` | 3 |
| `fig_data.radar.by_style.Lambic.F_hops_noble` | 2.3 |
| `fig_data.radar.by_style.Lambic.F_hops_woody` | 3.1 |
| `fig_data.radar.by_style.Lambic.F_esters_all` | 2.2 |
| `fig_data.radar.by_style.Lambic.F_esters_ethac` | 2.433 |
| `fig_data.radar.by_style.Lambic.F_esters_isoaa` | 2.467 |
| `fig_data.radar.by_style.Lambic.F_esters_flower` | 3.267 |
| `fig_data.radar.by_style.Lambic.F_esters_fruity` | 2.667 |
| `fig_data.defect_dumbbell.DMS.n` | 11 |
| `fig_data.defect_dumbbell.DMS.n_compliant` | 11 |
| `fig_data.defect_dumbbell.DMS.before_mean` | 1.1577 |
| `fig_data.defect_dumbbell.DMS.after_mean` | 1.5556 |
| `fig_data.defect_dumbbell.DMS.m_t` | 1.5873 |
| `fig_data.defect_dumbbell.DMS.delta_mean` | 0.3979 |
| `fig_data.defect_dumbbell.Diacetyl.n` | 11 |
| `fig_data.defect_dumbbell.Diacetyl.n_compliant` | 11 |
| `fig_data.defect_dumbbell.Diacetyl.before_mean` | 0.169 |
| `fig_data.defect_dumbbell.Diacetyl.after_mean` | -2.2602 |
| `fig_data.defect_dumbbell.Diacetyl.m_t` | 0.2896 |
| `fig_data.defect_dumbbell.Diacetyl.delta_mean` | -2.4292 |
| `fig_data.defect_dumbbell.4VG.n` | 11 |
| `fig_data.defect_dumbbell.4VG.n_compliant` | 11 |
| `fig_data.defect_dumbbell.4VG.before_mean` | -1.8794 |
| `fig_data.defect_dumbbell.4VG.after_mean` | -1.9755 |
| `fig_data.defect_dumbbell.4VG.m_t` | -2.0132 |
| `fig_data.defect_dumbbell.4VG.delta_mean` | -0.0962 |
| `fig_data.defect_dumbbell.trans-2-nonenal.n` | 11 |
| `fig_data.defect_dumbbell.trans-2-nonenal.n_compliant` | 11 |
| `fig_data.defect_dumbbell.trans-2-nonenal.before_mean` | 0.0039 |
| `fig_data.defect_dumbbell.trans-2-nonenal.after_mean` | -0.017 |
| `fig_data.defect_dumbbell.trans-2-nonenal.m_t` | 0.0114 |
| `fig_data.defect_dumbbell.trans-2-nonenal.delta_mean` | -0.0209 |
| `sensory_cols[0]` | `A_malt_all` |
| `sensory_cols[1]` | `A_malt_grain` |
| `sensory_cols[2]` | `A_malt_bread` |
| `sensory_cols[49]` | `overall` |
| `sensory_cols[3..48]` | `<省略中间 46 项；论文引用的值不在上面时，直接读原 JSON 的这个路径核对>` |
| `submission.path` | `submission/q3_generated_profiles.csv` |
| `submission.rows` | 101 |
| `submission.cols` | 284 |

---

## 已生成的 TABLE 文件（论文应直接嵌入这些表，不要自己手抄）

### `figures/TABLE_q1_model_cmp.md` (642 字节)

```markdown
**表：问题一主模型与基线整体性能对比（50 维平均）**

| 方法 | 平均 QWK | 说明 |
|---|---|---|
| **LightGBM（原生缺失，主模型）** | **0.3663** | 含缺失行全参与训练 |
| KNN 插补 + LightGBM | 0.3652 | 缺失对照 |
| 随机森林（中位插补） | 0.3280 | 基线 |
| ElasticNet（中位插补） | 0.2762 | 线性基线 |
| 逐维均值等级 | 0.0015 | 朴素基线 |

> 注：QWK 为分层 5 折交叉验证的二次加权 Kappa 均值；全部 50 维主模型均优于朴素基线，其中 50 维最终选用 LightGBM。最优值已加粗。

<!-- label: tab:q1_model_cmp -->
```

### `figures/TABLE_q1_perf.md` (1652 字节)

```markdown
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
```

### `figures/TABLE_q2_top3.md` (1312 字节)

```markdown
**表：代表性感官维度 Top-3 关键化合物及稳定性指标**

| 感官维度 | Top-1 | Top-2 | Top-3 | Top-1 入选频率 | 跨方法 Jaccard |
|---|---|---|---|---|---|
| 酒精 | ethanol..v.v. | kcalperc | CO2.PSI. | 1.000 | 0.667 |
| 苦味 | bitterness | ethyl_octanoate | ethyl_decanoate | 1.000 | 0.500 |
| 酒体 | ethanol..v.v. | kcalperc | ethyl_decanoate | 1.000 | 0.300 |
| 味·酒花 | bitterness | ethyl_octanoate | ethanol..v.v. | 1.000 | 0.667 |
| 余味 | ethyl_octanoate | bitterness | ethyl_decanoate | 1.000 | 0.400 |
| 味·麦芽 | color.EBC. | kcalperc | pH | 1.000 | 0.667 |
| 味·贵族花 | ethyl_octanoate | bitterness | iron | 1.000 | 0.500 |
| 香·麦芽 | color.EBC. | kcalperc | pH | 1.000 | 0.667 |
| 甜味 | GFS | ethyl_decanoate | protein.g.L. | 1.000 | 0.400 |
| 香·酒花 | ethyl_octanoate | DMS | linalool | 1.000 | 0.200 |
| 味·酯 | kcalperc | protein.g.L. | ethyl_acetate | 1.000 | 0.500 |
| 碳酸 | ethyl_octanoate | CO2.PSI. | ethyl_hexanoate | 1.000 | 0.233 |

> 注：入选频率为 500 次 bootstrap 中该化合物进入 Top-3 的比例；跨方法 Jaccard 衡量共表达/SHAP/相关三类证据 Top-3 的一致性（全维均值 0.303）；完整 50 维见 `submission/q2_top3_compounds.csv`。

<!-- label: tab:q2_top3 -->
```

### `figures/TABLE_q3_defect.md` (535 字节)

```markdown
**表：Pils/Lager→Tripel 迁移中 4 个缺陷化合物的阈值合规**

| 缺陷化合物 | 迁移前均值 | 迁移后均值 | 安全阈值 $m_t$ | 合规数/样本数 |
|---|---|---|---|---|
| DMS | 1.158 | 1.556 | 1.587 | 11/11 |
| Diacetyl | 0.169 | -2.260 | 0.290 | 11/11 |
| 4VG | -1.879 | -1.976 | -2.013 | 11/11 |
| trans-2-nonenal | 0.004 | -0.017 | 0.011 | 11/11 |

> 注：标准化含量；迁移后全部 44/44 次检查落在阈值安全侧，整体缺陷合规率 100%。

<!-- label: tab:q3_defect -->
```

### `figures/TABLE_q3_style.md` (463 字节)

```markdown
**表：三代表风格生成质量概览**

| 风格 | 生成样本数 | 与真实谱 KS 距离 |
|---|---|---|
| Tripel | 30 | 0.3573 |
| Kriek | 30 | 0.3983 |
| Lambic | 30 | 0.4084 |

> 注：KS 距离为生成谱与同风格真实谱在化学维上的 Kolmogorov–Smirnov 分布距离均值，越小越接近真实分布；生成化学维 = 231（约束通过）。Tripel 生成酯香水平 3.90（真实 3.21）。

<!-- label: tab:q3_style -->
```
