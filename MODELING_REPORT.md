# 建模与求解报告

**赛题**：2026 年 MathorCup 大数据竞赛 · 赛道 A（啤酒酿造化合物分析与啤酒风味预测）
**题号**：A（初赛）；**参赛编号**：MCB2600304；**语言**：中文；**输出**：Word（docx）
**上游依据**：`PROBLEM_ANALYSIS.md`、`DATA_FACTS.json`、`DATA_PROFILE.json`、`SUBMISSION_SPEC.json`、`CAPABILITY_CHECKLIST.json`。本报告为每条能力项给出建模方案（标注能力 id），并给出验证方案、泄漏清单、计算预算、方法声称与逻辑合同，供 comp-code 按合同实现。

本题是**大数据 / 机器学习题**（非参数密集型机理题）。三问构成一条流水线：**Q1**（化学谱含缺失 → 约 40 个感官维度 0-6 分级，判别式预测）→ **Q2**（在 Q1 模型上做化学→感官的可解释归因：共表达图 + 多证据 Top-3 + 稳定性）→ **Q3**（反向的风格→化学条件生成 + 跨风格可控迁移，复用 Q1 做感官画像）。

---

## 一、对赛题分析「升级结论」的审视（Step 1，三段式）

赛题分析《经典问题升级判定表》给出 7 条升级，逐条走「审视 → 必需性判定 → 采纳/异议」：

| 初步映射 → 最终模型 | 触发句 | 本问原文必需性 | 本报告决定 |
|---|---|---|---|
| 普通回归 → 缺失感知建模（不删行） | S6「数据缺失条件下」 | **必需**：Q1 原文明写缺失条件，1.csv 真实 73 个 NA/63 行 | **采纳**，M1 用原生缺失的 GBDT，并以插补法作对照（§六 Q1） |
| 单输出 → 多输出预测 | S5「约 40 维」 | **必需**：需同时交付约 40（全 50）维 | **采纳**，逐维回归器 + 维度共享特征（§六 Q1） |
| 连续回归 → 回归 + 有序分箱映射 | S5「0-6 分级」 | **必需**：交付物必须是 0-6 整数等级 | **采纳**，训练折内估分箱阈值再套验证折（§六 Q1） |
| 单次重要性 → bootstrap + 跨方法 | S8「入选频率 / Jaccard」 | **必需**：题面明示两法量化稳定性 | **采纳**，B≥500 次重采样 + ≥2 方法 Jaccard（§七 Q2） |
| 无条件 → 风格条件生成 | S9「风格条件」 | **必需**：Q3 核心 | **采纳**，CVAE 以风格 one-hot 为条件（§八 Q3） |
| 自由生成 → 约束生成（缺陷不恶化） | S10「不恶化」 | **必需**：硬约束 C6 | **采纳**，缺陷在原始空间做阈值/源值投影（§八 Q3） |
| 单风格 → 跨风格隐空间平移 | S10「跨风格迁移」 | **必需**：Pils/Lager→Tripel | **采纳**，隐空间风格向量平移 + 解码（§八 Q3） |

**无异议、无跳过**：7 条升级全部为当前问原文明确要求的机制，全部采纳。采纳时对小样本风格（Faro=3、Brut=4）辅以按风格分布采样作兜底与对照（见 §八），这是对「极小样本下 CVAE 不可训」的工程补充，不改变升级机制本身。

**覆盖度缺口审视**：赛题分析覆盖度检查无 ❌/⚠ 遗留机制；S1–S4 为纯背景句，S14（Kaggle）为题面允许的可选增强（能力 P3-C4，optional）。

**反向对照**：模型各组件均可溯源到题目句子（见 §十二 目标/约束溯源表），无题目未提组件。

---

## 二、模型假设（参数化）

> 关键假设均做成代码可切换参数，发现假设错误改参数即可修正，不必重写求解逻辑。

**假设 1：以 4.csv 标准化连续感官值为 Q1 训练目标，再按训练折内分布单调映射回 0-6 整数等级。**
- 理由：3.xlsx 的 summary sheet 数值为全 0 模板（已核 `DATA_PROFILE.json`），原始 0-6 分卡数值不可用；4.csv 是「全部 250 样本感官分析结果」（范围 −2.15~6.17、均值≈0，无缺失，已核），是唯一完整可用标签。分位/等距分箱单调可逆，既产出题面要求的 0-6 等级又不丢信息。
- 参数化：`LABEL_BINNING ∈ {"quantile","uniform"}`（默认 quantile）、`N_LEVELS = 7`（0..6）。
- 替代假设：若判为分类任务（解释 B）则无可用原始分卡标签、Q1 不可训——故不取。

**假设 2：约 40 维以 Aroma(A_*) 15 维 + Flavour(F_*) 15 维为核心交付，同时输出全 50 维。**
- 理由：题面明说「Aroma 与 Flavour 两套」；「约 40」介于 30（仅 A_/F_）与 50（含口感/缺陷/总体）之间，全 50 维一并给出覆盖任一解读。
- 参数化：`CORE_DIMS`（30 个 A_/F_ 列）、`ALL_DIMS`（50 列）；`REPORT_SCOPE = "all50"`。
- 替代假设：仅 30 维（`REPORT_SCOPE="core30"`），指标口径不变。

**假设 3：1.csv 化合物列为原始浓度的对数变换（底数待核），理化列为标准化值；建模统一在 1.csv「原生数值空间」内进行，不反变换。**
- 理由：实测 `ethyl_acetate∈[-0.599,2.117]`（负值=原浓度<1，符合对数变换），`ethanol..v.v.∈[-1.456,1.066]`（已标准化，非原始 %v/v）。底数 log10/ln 不影响树模型（单调变换下分裂不变），故 Q1 可不反变换；Q3 生成与缺陷约束同样在该空间内比较，口径自洽。
- 参数化：`LOG_BASE ∈ {"log10","ln","unknown"}`（默认 unknown，仅用于论文叙述，不进入数值路径）；`FEATURE_SPACE = "native"`。
- 替代假设：反变换到原始浓度空间（`FEATURE_SPACE="raw"`），需先定底数，对树模型结论无影响，对距离型模型才有影响。

**假设 4：缺陷「不恶化」在 1.csv 原生空间判定，取严口径 $x^{def}_{after}\le\min(\tau^{\*}_k,\ \max(x^{def}_{before},\,m^{t}_k))$。**
- 理由：8.xlsx 阈值（如 DMS=17.25）是原始浓度 µg/L，1.csv 的 DMS∈[0.046,2.716] 为对数/标准化空间，二者**单位不可直接比**。故以**相对判据为主**（不高于源值、不高于目标风格典型值 $m^t_k$），阈值 $\tau^{\*}_k$ 仅在可换算时作辅助上界；无法换算的缺陷（Stale hops 为陈化标记）只用相对判据。
- 参数化：`DEFECT_RULE = "strict_min"`、`USE_ABS_THRESHOLD`（默认 False，仅可换算时置 True）、`TARGET_TYPICAL_Q = 0.5`（目标风格典型分位）。
- 替代假设：仅阈值判据（解释 A）或仅源值判据（解释 B）；取严口径同时满足二者，最稳妥。

**假设 5：各子问题样本独立同分布，风格标签 `tasting_category_fine` 为 Q3 唯一条件变量。**
- 理由：附件为商用啤酒截面数据，无时间序列结构，交叉验证可用（分层）随机折而非时序折。
- 参数化：`CV_SCHEME = "stratified_kfold"`、`CONDITION_VAR = "tasting_category_fine"`。
- 替代假设：若存在复测重复样本（226 独立啤酒 vs 250 样本），用按组切分 `group_kfold` 防复测泄漏（见 §九泄漏清单）。

---

## 三、符号说明表

| 符号 | 含义 | 单位/取值 | 首次出现 |
|------|------|----------|----------|
| $N$ | 啤酒样本数 | 250 | Q1 |
| $P$ | 化合物/理化特征数 | 231 | Q1 |
| $J$ | 感官维度数（A_/F_ 为核心共 50） | 50 | Q1 |
| $S$ | 风格类别数 | 22 | Q3 |
| $X\in\mathbb{R}^{N\times P}$ | 化学谱矩阵（含缺失，对数/标准化混合） | 原生空间 | Q1 |
| $M\in\{0,1\}^{N\times P}$ | 缺失掩码（1=缺失） | 0/1 | Q1 |
| $x_i$ | 第 $i$ 款啤酒化学谱向量 | — | Q1 |
| $Y\in\mathbb{R}^{N\times J}$ | 4.csv 标准化感官值（训练标签） | 标准化 | Q1 |
| $\tilde y_{ij}$ | 分箱后 0-6 等级（交付目标） | $\{0,\dots,6\}$ | Q1 |
| $\hat y_{ij}$ | 第 $i$ 样本第 $j$ 维预测等级 | $\{0,\dots,6\}$ | Q1 |
| $g_j(\cdot)$ | 维度 $j$ 的连续值→0-6 单调分箱映射 | — | Q1 |
| $R\in[-1,1]^{P\times P}$ | 2.csv 化合物相关矩阵 | 相关系数 | Q2 |
| $G=(V,E)$ | 化合物共表达图（节点=化合物） | — | Q2 |
| $w_{pq}$ | 化合物 $p,q$ 边权（=相关系数） | $[-1,1]$ | Q2 |
| $\rho$ | 建图相关阈值 | $[0,1]$ | Q2 |
| $\phi_{jp}$ | 化合物 $p$ 对维度 $j$ 的关键度得分 | 实数 | Q2 |
| $\mathrm{Top3}(j)$ | 维度 $j$ 的前 3 关键化合物集合 | 3 元集 | Q2 |
| $f_{jp}$ | bootstrap 下 $p$ 进 $\mathrm{Top3}(j)$ 的频率 | $[0,1]$ | Q2 |
| $\mathrm{Jac}(A,B)$ | 两组 Top-3 集合的 Jaccard 系数 | $[0,1]$ | Q2 |
| $C\in[-1,1]^{44\times50}$ | 6.csv 化学×感官交叉相关 | 相关系数 | Q2 |
| $z_i\in\mathbb{R}^d$ | CVAE 隐编码 | — | Q3 |
| $s$ | 风格 one-hot 条件 | $\{0,1\}^S$ | Q3 |
| $p_\theta(x\mid z,s)$ | 条件解码分布 | — | Q3 |
| $q_\phi(z\mid x,s)$ | 条件编码分布 | — | Q3 |
| $x^{def}_k$ | 第 $k$ 个缺陷化合物浓度 | 原生空间 | Q3 |
| $\tau^{\*}_k$ | 缺陷 $k$ 的（可换算时）阈值上界 | 原生空间 | Q3 |
| $m^t_k$ | 目标风格 $t$ 的缺陷 $k$ 典型分位值 | 原生空间 | Q3 |
| $\Delta_{s\to t}$ | 隐空间风格迁移向量 | $\mathbb{R}^d$ | Q3 |

---

## ⓪ 参数口径表（全篇一致性基准，comp-code 按此校验）

| 物理量 | 定义值 | 单位 | 语义标签 | 用于哪些子问题 |
|--------|--------|------|---------|--------------|
| 样本数 | 250 | 行 | n_samples | Q1/Q2/Q3 |
| 特征数 | 231 | 列 | n_features | Q1/Q2/Q3 |
| 感官维度数 | 50（核心 30 为 A_/F_） | 列 | n_sensory_dims | Q1/Q2 |
| 风格类别数 | 22 | 类 | n_styles | Q3 |
| 分级刻度 | 0..6（7 级整数，有序） | 级 | level_scale | Q1（交付）/Q2（归因对象） |
| Top-N | 3 | 个/维度 | topn | Q2 |
| 缺陷化合物 | DMS / X2.3.butanedione / X4VG / X.E..2.nonenal / Stale hops | 列名 | defect_cols | Q3 |
| 代表风格 | Tripel / Kriek / Lambic | 类 | gen_styles | Q3 |
| 迁移对 | Pils/Lager → Tripel | 类对 | transfer_pair | Q3 |
| CV 折数 | 5 | 折 | n_folds | Q1 |
| bootstrap 次数 | 500 | 次 | n_bootstrap | Q2 |
| 建图相关阈值 | 0.5（灵敏度扫 0.4/0.6） | 相关系数 | coexpr_rho | Q2 |

> ⛔ 一致性约束：`level_scale` 全篇恒为 0-6 整数有序；`defect_cols` 五项列名固定（映射见 `DATA_FACTS.json` given 段），不得改名或增删；`n_sensory_dims` 的核心 30 维恒指 A_/F_ 前缀列。缺失统计全篇以 NA 总数=73、含 NA 行=63 为准（已核）。

---

## 六、问题一：含缺失的多输出有序感官分级预测（能力 P1-C1/C2/C3/C4）

### 6.1 任务与方法选择

针对能力 **P1-C1**（多输出分级交付）/ **P1-C2**（缺失条件建模，不删行）/ **P1-C3**（0-6 有序输出）/ **P1-C4**（去泄漏独立验证）。给定含缺失的化学谱 $X$，为每个样本、每个感官维度输出 0-6 整数等级 $\hat y_{ij}$。

**方法选择与理由**（调研方法族：「含缺失的多输出有序预测」）：主模型用**原生支持缺失的梯度提升树**（LightGBM，`use_missing=True` 走默认分裂方向）。依据：(1) 树模型对单调变换（对数底数未定）不敏感，免除反变换口径风险（假设 3）；(2) 原生缺失分裂直接在 63 个含缺失行上学习缺失方向，避免插补偏差，正面回应 S6；(3) 对高维（231）稀疏信号稳健，且输出特征重要性直接服务 Q2。候选对比：多输出随机森林、ElasticNet（线性基线）、均值基线、KNN。缺失处理对照：IterativeImputer/KNNImputer + 同模型，量化插补偏差。

### 6.2 标签构建与 0-6 分箱映射

以 4.csv 标准化值 $Y$ 为回归目标。对维度 $j$，在**训练折内**估计 7 分位点 $\{q^{(j)}_1,\dots,q^{(j)}_6\}$（或等距点），定义单调映射

$$
g_j(y)=\sum_{\ell=1}^{6}\mathbb{1}\!\left[y> q^{(j)}_\ell\right],\qquad \tilde y_{ij}=g_j(Y_{ij})\in\{0,\dots,6\}. \tag{1}
$$

预测时对回归输出 $r_{ij}$ 施加同一映射并截断取整：

$$
\hat y_{ij}=\min\!\Big(6,\ \max\!\big(0,\ \mathrm{round}(g_j(r_{ij}))\big)\Big). \tag{2}
$$

分位点、标准化参数**只由训练折估计**，套到验证折（防泄漏，能力 P1-C4、约束 C8）。

### 6.3 预测模型

逐维回归器 $h_j$，对维度 $j$：

$$
r_{ij}=h_j(x_i;\,\Theta_j),\qquad
\Theta_j=\arg\min_{\Theta}\ \sum_{i\in\mathcal{D}_{tr}}\big(Y_{ij}-h_j(x_i;\Theta)\big)^2+\Omega(\Theta), \tag{3}
$$

其中 $h_j$ 为 LightGBM 回归树集成，$x_i$ 的缺失分量由树的默认分裂方向处理（不插补、不删行，$|\mathcal{D}_{tr}|$ 含全部训练折样本含缺失行）；$\Omega$ 为叶子数/学习率/L2 等正则。50 维共享同一特征矩阵 $X$，可选多输出包装共享分裂结构。

### 6.4 求解过程（按执行顺序）

1. **初始化**：读 1.csv → 分出 231 特征列与元列；读 4.csv → 50 标签列。固定随机种子 `SEED=42`。
2. **分层 K 折**：按 `tasting_category_fine` 分层 5 折（`StratifiedKFold`）；若检出复测组则改 `GroupKFold`（§九）。
3. **折内拟合**：在每训练折上——估分箱分位点 $g_j$、拟合 $h_j$（含缺失）、记录特征重要性。
4. **折内预测**：验证折上出 $r_{ij}$ → 经 (2) 得 $\hat y_{ij}$；累计逐维 QWK/MAE/R²。
5. **基线对比**：同折同口径跑均值预测、ElasticNet、随机森林，记 ΔQWK。
6. **全量重训**：全部 250 样本重训一次 $h_j$ 与 $g_j$，对全样本出 $\hat y_{ij}$ → 写 `submission/q1_sensory_scores.csv`（250 行，`beer_id` + 50 维 0-6 整数，无缺失）。
7. **缺失对照**：插补法重跑步骤 3-4，与原生缺失比 QWK（量化插补偏差）。

### 6.5 为何可信（独立复核）

逐维 QWK（二次加权 Kappa，有序分级首选）、MAE、R² 均来自验证折；与均值基线、线性基线比较（主模型应整体不劣于基线，弱信号维度允许接近基线——这是正确现象，见 §十一预期）。本题无不公开测试集，所有指标如实标注为「交叉验证指标」，不冒称测试集成绩。**提交模型由验证结果决定**：若某维度主模型 CV 不超过基线，该维度交付基线或二者集成结果（规则写入代码与论文）。

---

## 七、问题二：共表达图 + 多证据 Top-3 + 稳定性（能力 P2-C1/C2/C3/C4）

### 7.1 任务与方法选择

针对能力 **P2-C1**（共表达图）/ **P2-C2**（每维 Top-3 交付）/ **P2-C3**（稳定性量化）/ **P2-C4**（化学合理性）。为每个感官维度给出 Top-3 关键化合物，并证其稳健与化学合理。

**方法选择与理由**（方法族：「相关网络 + 可解释特征归因」）：许多化合物在 2.csv 中高度相关、成模块，单一重要性受共线性干扰，故先用共表达图揭示模块结构，再在「模块意识」下做多证据融合归因，最后用题面指定的两种口径量化稳定性。

### 7.2 共表达图构建（P2-C1）

以 2.csv 的 231 个化合物为节点、相关系数为边权建无向图，阈值化去弱边：

$$
E=\big\{(p,q):\ |R_{pq}|\ge \rho\big\},\qquad w_{pq}=R_{pq},\quad \rho=0.5. \tag{4}
$$

对 $G=(V,E)$ 做 Louvain/贪心模块度社区检测得化合物模块 $\{\mathcal{M}_1,\dots,\mathcal{M}_K\}$，模块度

$$
Q_{mod}=\frac{1}{2m}\sum_{p,q}\Big(w_{pq}-\frac{k_p k_q}{2m}\Big)\,\delta(c_p,c_q),\quad k_p=\sum_q w_{pq},\ 2m=\sum_{p,q}w_{pq}. \tag{5}
$$

相关口径冲突（题面称 Pearson、数据说明称 Spearman）在图注中注明，边权按附件 2.csv 数值直接用（约束 C5）。$\rho$ 扫 0.4/0.6 做灵敏度。

### 7.3 多证据 Top-3 归因（P2-C2）

对每个感官维度 $j$，融合三类证据给化合物 $p$ 的关键度：

$$
\phi_{jp}=\alpha\,\widetilde{\mathrm{SHAP}}_{jp}+\beta\,\big|\tilde C_{pj}\big|+\gamma\,\mathrm{rep}_{jp},\qquad \alpha+\beta+\gamma=1. \tag{6}
$$

其中 $\widetilde{\mathrm{SHAP}}_{jp}$ 为 Q1 模型对维度 $j$ 的归一化 SHAP/置换重要性（预测贡献，非线性）；$\tilde C_{pj}$ 为 6.csv 化学×感官交叉相关的归一化绝对值（线性证据，仅覆盖 44 化合物行，缺失化合物该项记 0）；$\mathrm{rep}_{jp}$ 为模块代表加权——同模块内多个可互替化合物只保留关键度最高者进入候选，避免 Top-3 被单一模块占满。取

$$
\mathrm{Top3}(j)=\operatorname*{arg\,top3}_{p}\ \phi_{jp}. \tag{7}
$$

默认 $\alpha{=}0.5,\beta{=}0.3,\gamma{=}0.2$（权重做灵敏度）。交付 `submission/q2_top3_compounds.csv`：每个维度恰好 3 行（约束 C3）。

### 7.4 稳定性量化（P2-C3，严格按题面两法）

**(a) Bootstrap 入选频率**：对样本做 $B=500$ 次有放回重采样，每次重算 $\mathrm{Top3}^{(b)}(j)$，统计

$$
f_{jp}=\frac{1}{B}\sum_{b=1}^{B}\mathbb{1}\!\left[p\in\mathrm{Top3}^{(b)}(j)\right]\in[0,1]. \tag{8}
$$

**(b) 跨方法 Jaccard**：对「SHAP 法」「6.csv 交叉相关法」「随机森林重要性法」两两比较 Top-3 集合：

$$
\mathrm{Jac}(A,B)=\frac{|A\cap B|}{|A\cup B|}\in[0,1]. \tag{9}
$$

$f_{jp}$ 高=单方法稳健，$\mathrm{Jac}$ 高=方法间一致（约束 C4：两指标 $\in[0,1]$）。

### 7.5 求解过程与可信性（P2-C4）

1. 建图 (4)(5) → 得模块；2. 用 §六全量 Q1 模型算各维 SHAP；3. 读 6.csv 交叉相关；4. 融合 (6) 排 Top-3；5. bootstrap 循环算 $f_{jp}$，跨方法算 Jaccard。
**化学合理性**：对每维 Top-3 对照酿造机理（酯类→果香/溶剂、萜类→酒花花果香、硫化物/DMS→蔬菜硫味、醛酮/双乙酰→缺陷、麦芽类→焦糖/面包）逐条解释，并与 6.csv 交叉相关的**符号与量级**一致（P2-C4 可证伪判据），与 8.xlsx 的 GBM 参考重要性对照佐证。**预期正确现象**：强信号维度（如 A_hops_citrus、酯香）Top-3 入选频率高、Jaccard 大；弱信号/缺陷维度不稳定——如实报告并解释，不强行制造稳定（§十一）。

---

## 八、问题三：风格条件生成 + 可控迁移（能力 P3-C1/C2/C3，P3-C4 可选）

### 8.1 任务与方法选择

针对能力 **P3-C1**（风格条件生成）/ **P3-C2**（生成谱 + 感官画像交付）/ **P3-C3**（跨风格迁移且缺陷不恶化）/ **P3-C4**（Kaggle 外部增强，optional）。

**方法选择与理由**（方法族：「条件生成 + 隐空间可控迁移」）：主模型用**条件变分自编码器（CVAE）**，把 231 维化学谱编码进低维隐空间、以风格 one-hot 为条件解码，兼顾生成多样性与风格可控；隐维 $d$ 取 8–16 以适配 250 小样本。极小样本风格（Faro=3、Brut=4、Scotch=5）CVAE 不可训，辅以**按风格多元高斯/Copula 分布采样**作兜底与对照（捕捉化合物共表达相关结构）。感官画像复用 §六 Q1 模型形成「生成化学谱→预测感官」闭环。

### 8.2 CVAE 模型（P3-C1）

编码器 $q_\phi(z\mid x,s)=\mathcal{N}(\mu_\phi(x,s),\,\mathrm{diag}\,\sigma^2_\phi(x,s))$，解码器 $p_\theta(x\mid z,s)$。证据下界（最大化）：

$$
\mathcal{L}(\theta,\phi)=\mathbb{E}_{q_\phi(z\mid x,s)}\big[\log p_\theta(x\mid z,s)\big]-\beta_{KL}\,\mathrm{KL}\!\big(q_\phi(z\mid x,s)\,\big\|\,p(z)\big),\quad p(z)=\mathcal{N}(0,I). \tag{10}
$$

重参数化 $z=\mu_\phi+\sigma_\phi\odot\epsilon,\ \epsilon\sim\mathcal{N}(0,I)$；重构项对连续化学谱用高斯/MSE。缺失输入在训练时用掩码 $M$ 排除重构损失中的缺失分量（不让缺失位置污染梯度）：

$$
\log p_\theta(x\mid z,s)\ \propto\ -\tfrac12\sum_{p:\,M_{ip}=0}\big(x_{ip}-\hat x_{ip}\big)^2. \tag{11}
$$

生成：给定风格 $t$ 采 $z\sim\mathcal{N}(0,I)$，解码 $\hat x=p_\theta(\cdot\mid z,\mathrm{onehot}(t))$。不同风格条件产出不同分布（P3-C1 可证伪判据：降维后按风格可分）。

### 8.3 跨风格迁移（P3-C3）

隐空间估计源→目标风格平移向量，对源样本编码后平移再解码：

$$
\Delta_{s\to t}=\bar z_t-\bar z_s,\qquad \bar z_c=\frac{1}{|c|}\sum_{i\in c}\mu_\phi(x_i,\mathrm{onehot}(c)),\qquad
\hat x_{t}=p_\theta\big(z_s+\Delta_{s\to t}\,\big|\,\mathrm{onehot}(t)\big). \tag{12}
$$

**缺陷不恶化硬约束（C6，机动）**：对每个缺陷化合物 $k\in\{$DMS, Diacetyl, 4VG, t2n, Stale hops$\}$ 逐样本投影回安全区

$$
x^{def}_{k,after}\ \leftarrow\ \min\!\Big(x^{def}_{k,after},\ \min\big(\tau^{\*}_k,\ \max(x^{def}_{k,before},\,m^t_k)\big)\Big), \tag{13}
$$

$m^t_k$ 为目标风格 $t$ 缺陷 $k$ 的典型分位值（默认中位，`TARGET_TYPICAL_Q=0.5`）；$\tau^{\*}_k$ 仅在 8.xlsx 阈值可换算到原生空间时启用（`USE_ABS_THRESHOLD`，默认 False），否则只用相对判据（假设 4）。投影后阈值合规率应为 100%（P3-C3 可证伪判据）。

### 8.4 感官画像与交付（P3-C2）

对生成/迁移谱 $\hat x$ 套 §六 Q1 模型得 50 维 0-6 感官画像（雷达图）。交付 `submission/q3_generated_profiles.csv`：代表风格 Tripel/Kriek/Lambic 的生成谱（维度数=231，约束 C7）+ 其 Q1 感官画像 + 迁移前后缺陷对照与合规标记。

### 8.5 求解过程与可信性

1. 预处理化学谱（缺失掩码）；2. 训练 CVAE（Adam，早停，固定种子）；3. 各代表风格条件采样生成；4. 极小样本风格走高斯/Copula 兜底；5. 迁移 (12) + 缺陷投影 (13)；6. Q1 打画像。
**独立复核**：(a) 生成 vs 真实同风格谱的**分布距离**（逐化合物 KS 距离、整体能量距离/MMD）；(b) PCA/t-SNE 降维看生成样本是否落入对应真实风格簇（重叠度）；(c) 迁移后缺陷阈值合规率（应 100%）；(d) 生成 Tripel 经 Q1 画像应呈酯/酒精强的风格特征（闭环一致，见 §十一逻辑合同 equivalence）。

### 8.6 可选增强（P3-C4，optional）

Kaggle `top-beer-information` 公开集可作生成谱外部合理性旁证或 Q1 额外特征；标 optional、相对路径缓存，不作主结论依据，缺失不影响核心交付。若未使用，论文不声称其为成果。

---

## 九、大数据竞赛专项：验证 / 基线 / 泄漏 / 预算 / 结果去向

### 9.1 验证方案（与官方「结论量化」一致）

- **Q1**：按 `tasting_category_fine` **分层 5 折交叉验证**。同一风格同比例进训练/验证折，保证各折风格分布一致。逐维报告 **QWK（主）、MAE、R²**。**分箱分位点 $g_j$、标准化参数仅由训练折估计再套验证折**——这是本题最易踩的泄漏点。
- **Q2**：稳定性本身即验证——bootstrap（$B{=}500$）入选频率 + ≥2 方法 Jaccard；化学合理性以 6.csv 交叉相关符号/量级与机理双重佐证。
- **Q3**：无监督生成用**分布距离（KS/能量距离）+ 降维簇重叠度**评估；迁移用**缺陷阈值合规率**（硬指标，应 100%）；闭环用 Q1 画像核风格特征。
- **测试集纪律**：本题**无不公开测试集**，所有数字为交叉验证内部估计，论文如实标注，不冒称测试集成绩；不用任何验证折信息调参（调参在训练折内嵌套或用默认稳健超参）。

### 9.2 基线与改进（提交模型由验证决定）

| 子问题 | 基线 | 主模型 | 改进点（可在验证集对比） |
|--------|------|--------|------------------------|
| Q1 | 逐维**均值等级**预测 / ElasticNet 线性 | 原生缺失 LightGBM 多输出 | 缺失感知、非线性、维度共享特征 |
| Q2 | 单一 6.csv 交叉相关排序 | SHAP+相关+模块 多证据融合 | 去共线性冗余、模块代表、跨方法一致 |
| Q3 | 按风格**多元高斯**采样 | CVAE 条件生成 + 隐空间迁移 | 可控迁移、缺陷投影、小样本兜底 |

**规则**：主模型在验证指标上不超过基线的维度/风格，交付基线或二者集成（写入代码与论文）。基线、按风格高斯兜底、ImageNet 式预训练均为正当候选，不进 METHOD_CLAIMS 的 forbid。

### 9.3 泄漏风险清单（逐条列防法）

1. **全量标准化/分箱后再切分** → 分箱分位点、标准化参数只在训练折 fit，validate 折 transform（约束 C8）。
2. **复测样本跨折泄漏**：226 独立啤酒 vs 250 样本，若同一啤酒有复测行同时进训练/验证折会高估。防法：检出复测组（按 `beer` 名或近重复行）则改 `GroupKFold`（假设 5 参数化 `CV_SCHEME`）。
3. **标签维度互泄漏**：50 维共享特征 $X$ 是输入共享，不是用其他维度标签当特征；Q1 不把 4.csv 其他维度作为自变量。
4. **8.xlsx 的 GBM SHAP/importance 泄漏**：8.xlsx 的参考重要性由主办方模型算出，**只作 Q2 旁证对照，不作 Q1 训练特征**（否则等于用答案）。
5. **编号/文件名带标签**：`beer_id`、`beer` 仅作主键与分组，**不进特征矩阵**。
6. **目标编码泄漏**：不对 `tasting_category_fine` 做目标编码进 Q1 特征（Q1 不应知道风格，否则泄漏风格→感官的捷径）；风格仅在 Q3 作条件。

### 9.4 计算预算（已跑 `dl_env.py check`）

本机有 **NVIDIA RTX 4050 Laptop GPU（6 GB，算力 8.9）**；软件自带 CPU 版 torch 2.13、lightgbm 4.6、xgboost 3.2、catboost、sklearn 1.8。

| 模型 | 库 | CPU 预计 | GPU 预计 | 控时做法 |
|------|-----|---------|---------|---------|
| Q1 LightGBM×50 维×5 折 | lightgbm（CPU 即可） | 约 5–12 min | 约 3–6 min | 早停、叶子数上限、特征子采样 |
| Q1 基线/插补对照 | sklearn | 约 3–6 min | — | 共用折缓存 |
| Q2 bootstrap 500×SHAP | shap/sklearn | 约 10–20 min | — | SHAP 用 Q1 树模型 TreeExplainer（快）、按维度并行 |
| Q3 CVAE | torch | 约 5–15 min | 约 2–5 min | 隐维小、早停、batch 全量可载入内存 |

单模型训练均 < 60 min，无需 60 min 检查点；CVAE 若用 GPU 需先 `install torch` 显卡版（约 2 GB），CPU 版亦足够（样本仅 250）。固定 `SEED=42`，只用相对路径。全部流程全量数据，不抽样。

### 9.5 结果去向

| 结果文件 | 由哪一问/模型生成 | 对应能力 |
|---------|-----------------|---------|
| `submission/q1_sensory_scores.csv` | Q1 全量重训 LightGBM → 0-6 分级 | P1-C1 |
| `submission/q2_top3_compounds.csv` | Q2 多证据融合 + 稳定性 | P2-C2 |
| `submission/q3_generated_profiles.csv` | Q3 CVAE 生成 + 迁移 + Q1 画像 | P3-C2 |

| 正文表 | 由哪一问给出 |
|--------|------------|
| T1 各感官维度 CV 的 QWK/MAE/R² | Q1 |
| T2 每维 Top-3 + 入选频率/Jaccard | Q2 |
| T3 代表风格生成谱 + 感官画像 + 缺陷合规 | Q3 |

---

## 十、模型检验与灵敏度分析设计

- **Q1 检验**：分层 5 折 CV 的 QWK/MAE/R² 逐维；残差分析（预测 vs 实际的校准图、残差零均值等方差核对）；插补 vs 原生缺失对照。**灵敏度**：`LABEL_BINNING`（quantile/uniform）、GBDT 关键超参、`REPORT_SCOPE`（30/50 维）对指标的影响。
- **Q2 检验**：bootstrap 入选频率给单方法稳健性，跨方法 Jaccard 给一致性。**灵敏度**：建图阈值 $\rho\in\{0.4,0.5,0.6\}$、融合权重 $(\alpha,\beta,\gamma)$ 对 Top-3 的影响；报告 Top-3 随 $\rho$/权重的变化幅度。
- **Q3 检验**：分布距离（KS/能量距离）、降维簇重叠度、缺陷合规率、Q1 画像风格一致性。**灵敏度**：隐维 $d\in\{8,12,16\}$、$\beta_{KL}$、`TARGET_TYPICAL_Q` 对生成质量与迁移缺陷的影响。
- **鲁棒性**：对化学谱加小噪声（数据扰动）看 Q1 分级与 Q2 Top-3 的稳定性；CVAE 多次采样看生成分布稳定性（固定种子可复现）。

---

## 十一、合理性预验证（Step 5.5，comp-code 对照执行）

> 核心原则：物理/题设约束 > 数据忠实度 > 计算正确性。本题无传统物理边界，硬边界集中在输出值域、交付完整性、Top-3 基数、缺陷不恶化、验证无泄漏。

### ① 结果约束清单

**硬边界（题设，可机器审计）**：
- `q1_level`：$\forall i,j,\ \hat y_{ij}\in\{0,1,2,3,4,5,6\}$，依据 S5「0-6 分制」。审计：`((pred==pred.round()) & (pred>=0) & (pred<=6)).all()`。
- `q1_delivery`：`q1_sensory_scores.csv` 形状 $=(250,\,1{+}J)$ 且无 NA，依据交付完整性。审计：`df.shape[0]==250 and df.drop(columns=['beer_id']).notna().all().all()`。
- `q2_top3_card`：每个感官维度恰好 3 个化合物，依据 S7「Top-3」。审计：`q2.groupby('sensory_dim').size().eq(3).all()`。
- `q2_stat_range`：$0\le f_{jp}\le1$ 且 $0\le \mathrm{Jac}\le1$，依据定义。审计：`((s>=0)&(s<=1)).all()`。
- `q2_edge_from_R`：图边权 $=$ 2.csv 对应元素且 $|w|\ge\rho$，依据 S7。审计：边权与 R 矩阵对应元素逐一相等。
- `q3_defect_nonworse`：$\forall k,i,\ x^{def}_{k,after}\le\min(\tau^{\*}_k,\max(x^{def}_{k,before},m^t_k))$（可换算时含 $\tau^{\*}$，否则相对判据），依据 S10。审计：逐缺陷逐样本从 `q3_generated_profiles.csv` 重算，合规率==1.0。
- `q3_gen_dim`：生成谱化合物维度 $==231$，依据交付一致。审计：`gen.shape[1]==231`。
- `no_leakage`：分箱/标准化参数仅由训练折估计。审计：代码审查 fit/transform 分离（过程约束）。

**预期范围（经验估计，仅供核对，不作代码错误证据）**：
- Q1 逐维 QWK：强信号维度（酒花柑橘/酯香）约 0.4–0.7，弱信号/缺陷维度可能接近 0 甚至略负——正常现象。
- Q2 强信号维度 Top-1 入选频率约 ≥0.7，弱信号维度可能 <0.5——正常现象。
- Q3 生成谱各化合物落在真实观测该列的 min–max 附近（±少量）。

### ② 预期行为描述

- **Q1**：主模型整体 QWK 不低于均值基线；酯/酒花等化学信号明确的维度比噪声型缺陷维度更可预测（可预测性随信号强度单调）。
- **Q2**：强信号维度 Top-3 稳定（高频率、高 Jaccard），弱信号维度不稳定且其 Q1 可预测性也低（两问一致，见逻辑合同）。
- **Q3**：不同风格条件生成不同分布；生成 Tripel 的酯香画像应偏高；迁移后缺陷单调不升（投影保证）。

### ③ 异常处理预案

- **Q1 预测出现非 0-6 或连续值** → 原因：(2) 式截断取整未施加。修正：在输出前统一套 $g_j$+clip+round（调建模选择，不改题设）。禁止：直接改标签尺度。
- **Q1 训练样本 <250** → 原因：误 dropna 丢缺失行。修正：改回原生缺失/插补路径（P1-C2）。禁止：删行后声称缺失建模。
- **Q2 Top-3 全被单一模块占满** → 原因：模块代表加权 $\gamma$ 过小。修正：调 $\gamma$ 或模块内去冗余强度（建模选择）。禁止：手删化合物凑多样性。
- **Q2 某维稳定性极低** → 先核该维 Q1 可预测性；若其 QWK 也近 0，这是正确现象，如实报告，不调权重制造稳定。
- **Q3 迁移后缺陷升高超限** → 原因：投影 (13) 未对该缺陷生效或 $m^t_k$ 取值过松。修正：确认缺陷列映射正确、投影逐样本执行（调建模选择）。禁止：改 8.xlsx 阈值或源值让结果达标。
- **Q3 生成谱退化（各风格雷同）** → 原因：$\beta_{KL}$ 过大致后验坍塌。修正：降 $\beta_{KL}$ 或增隐维（建模选择）。

### ④ 方法指定（唯一方法 + 禁止替代）

- 缺失处理：主=LightGBM 原生缺失（`use_missing=True`）；对照=IterativeImputer/KNNImputer。禁止：dropna 丢训练行。
- 0-6 映射：训练折内 7 分位分箱 (1)+clip+round (2)。禁止：全量估分箱、输出连续值不分级。
- 验证切分：分层 5 折（检出复测改 GroupKFold）。禁止：普通随机 KFold 忽略风格分层、用验证折调参。
- 归因：SHAP(TreeExplainer)+6.csv 相关+模块代表 融合 (6)。禁止：仅单一相关排序冒充多证据。
- 稳定性：bootstrap $B{=}500$ 频率 + 跨 ≥2 方法 Jaccard。禁止：单次拟合无重采样。
- 生成：CVAE (10)(11)；小样本风格高斯/Copula 兜底。禁止：用风格均值常数当生成谱。
- 迁移：隐空间平移 (12) + 缺陷投影 (13)。禁止：无缺陷约束的自由生成冒充「不恶化」。

### ⑤ 验证检查点（编码阶段 pass/fail）

- □ `q1_sensory_scores.csv` 250 行、$\in\{0..6\}$、无 NA → fail 跳 ③「非 0-6」。
- □ Q1 训练用满 250 样本（含缺失行）→ fail 跳 ③「样本<250」。
- □ Q1 分箱/标准化仅训练折 fit → fail 跳 ④「验证切分」。
- □ `q2_top3_compounds.csv` 每维恰 3 行、$f,\mathrm{Jac}\in[0,1]$ → fail 跳 ③「Top-3 占满」/①。
- □ Q2 稳定性来自 ≥500 bootstrap 与 ≥2 方法 → fail 跳 ④「稳定性」。
- □ `q3_generated_profiles.csv` 231 维、缺陷合规率==1.0 → fail 跳 ③「缺陷超限」。
- □ Q3 各风格生成分布可区分（降维/分布距离）→ fail 跳 ③「退化」。
- □ 最终：所有硬边界满足；超预期范围的已核对输入/单位/假设并写明原因。

### ⑥ 结构性验证输入

本题三问均非 LP/MILP 式带决策变量与可行域的经典优化问题（Q1 为监督预测、Q2 为归因、Q3 为约束生成），不设目标函数的约束活跃性/影子价格检验。仍给出可控量的合理范围与预期行为供 comp-code 核对：

| 可控量 | 含义 | 合理范围 | 取到边界说明什么 |
|------|------|---------|------------------|
| GBDT 叶子数/深度 | Q1 复杂度 | 适中（防过拟合） | 过大且验证 QWK 下降=过拟合 |
| $\rho$ 建图阈值 | Q2 稀疏度 | 0.4–0.6 | 太高致图断裂、太低致全连通 |
| $(\alpha,\beta,\gamma)$ | Q2 证据权重 | 和为 1 | 某项=1 退化为单证据 |
| 隐维 $d$ | Q3 容量 | 8–16 | 过大=过拟合小样本、过小=坍塌 |
| $\beta_{KL}$ | Q3 正则 | 适中 | 过大=后验坍塌、各风格雷同 |

- **稳定性预期**：Q1 树模型固定种子后结果完全可复现（CV<1%）；Q2 bootstrap 频率有抽样波动但 Top-1 应稳定；Q3 CVAE 不同种子生成分布应相近（风格可分性稳定）。
- **资源利用率预期**：50 维全部被预测（无闲置维度）；231 特征中 Q1 特征重要性应集中在少数化学信号列（符合稀疏信号）。

### ⑦ 方法声称清单（METHOD_CLAIMS）

| 编号 | 正文将声称的方法 | 代码里必须真实现的特征（可核查） |
|------|---------------------|-------------------------------|
| M1 | 原生缺失感知的多输出梯度提升预测 | 用 LGBMRegressor/XGBRegressor，含缺失行参与训练（不 dropna 丢训练行），训练样本=250 |
| M2 | 回归 + 7 级有序分箱映射到 0-6 | 有分位/等距分箱 + clip[0,6] + 取整，输出整数等级 |
| M3 | 分层 K 折交叉验证的 QWK | 用 StratifiedKFold + cohen_kappa_score(weights='quadratic')，分箱参数折内估计 |
| M4 | 化合物共表达图 + 社区检测 | 用 networkx 建图、边权取自 2.csv、louvain/贪心模块度分社区 |
| M5 | SHAP/置换重要性归因 | 用 shap.TreeExplainer 或 permutation_importance 对 Q1 模型 |
| M6 | bootstrap 入选频率 + 跨方法 Jaccard | 有 ≥500 次有放回重采样循环 + Jaccard 集合运算 |
| M7 | CVAE 条件生成（重参数化 + KL） | 用 torch nn.Module，含 mu/logvar 重参数化 + KL 散度项 |
| M8 | 隐空间迁移 + 缺陷阈值投影 | 隐空间平移 + 对缺陷列逐样本 min/clip 投影 |

```
<!-- METHOD_CLAIMS_MACHINE
M1 | must: LGBMRegressor|XGBRegressor|HistGradientBoostingRegressor | forbid: X_train\s*=.*dropna|train.*\.dropna\(
M2 | must: qcut|digitize|KBinsDiscretizer|searchsorted, clip\(, astype\(int|round\( | forbid: 
M3 | must: StratifiedKFold|StratifiedGroupKFold, cohen_kappa_score, quadratic | forbid: 
M4 | must: networkx|import nx|nx\., louvain|greedy_modularity|best_partition|community | forbid: 
M5 | must: shap|TreeExplainer|permutation_importance | forbid: 
M6 | must: resample|np\.random\.choice|\.sample\(.*replace=True, jaccard | forbid: 
M7 | must: nn\.Module|torch, logvar|log_var|reparameter, kl|KLD|kl_div | forbid: 
M8 | must: np\.minimum|np\.clip|clip\(|np\.where, DMS|X4VG|butanedione|nonenal | forbid: 
-->
```

（M1–M8 与上表逐条对应。M2/M3/M4/M5/M6/M7/M8 的 forbid 留空——这些方法的降级无单一关键词可唯一锁定，由 CAPABILITY_CHECKLIST 的 falsifiable_check 与运行证据判定；仅 M1 的典型降级「删缺失行」有明确签名。）

### 逻辑合同（LOGIC_CONTRACT_MACHINE，下游 logic_audit.py 机器核）

```json
{"LOGIC_CONTRACT_MACHINE":{
  "bounds":[],
  "no_double_count":[],
  "must_features":["ethyl_acetate","isoamyl_alcohol","linalool","DMS","X2.3.butanedione","X4VG"],
  "train_range":{"q1_level":[0,6],"ethyl_acetate":[-0.599,2.117]},
  "monotonic":[],
  "constraints_with_margin":[{"quantity":"q3_defect_compliance_rate","limit":1.0,"kind":"ge","min_margin":0}],
  "calibration_anchors":[],
  "equivalence_claims":[{"claim":"生成Tripel经Q1画像的酯香水平与真实Tripel一致(闭环)","quantity_a":"gen_tripel_ester_level","quantity_b":"real_tripel_ester_level","rel_tol":0.25,"explanation":"CVAE生成为匹配风格分布的随机采样,允许采样波动,只要求同量级一致"}]
}}
```

> 说明：本题无「反解/取界」方向问题（bounds 空）、无总量吸收分项的重复计量（no_double_count 空）、无单点标定缩放（calibration_anchors 空）、无干净的决策资源→目标单调关系（monotonic 空）——均按实情留空，logic_audit 软跳过。`must_features` 断言 6 个关键化学信号列确实进入 Q1 设计矩阵（含 3 个缺陷列）；`train_range` 防 Q3 生成谱外推过远、Q1 分级越界；`constraints_with_margin` 核 Q3 缺陷合规率==1；`equivalence_claims` 核 Q1↔Q3 闭环一致（带解释，WARN 级）。上述 `q3_*`/`gen_*`/`real_*` 键由 comp-code 在 `figures/all_results.json` 回填实际值。

### 假设问责表（无数据只能假设的参数）

| 假设参数 | (a) 为何无数据只能假设 | (b) 取值依据 | (c) 灵敏度：该假设变化时关键结论变多少 | (d) 假设若错，结论还成立吗 |
|---|---|---|---|---|
| 对数变换底数 LOG_BASE | 题面明言「参赛者需自行核实」，附件未给底数 | 由数据分布反推（comp-code）；树模型对单调变换不变 | **低**：Q1 树模型结论与底数无关；仅影响论文叙述的浓度换算 | **成立**：主结论（分级、Top-3）不依赖底数 |
| 0-6 分箱映射口径 LABEL_BINNING | 原始 0-6 分卡（3.xlsx）为全 0 模板不可用，只能由 4.csv 标准化值重建 | 训练小组分布的 7 分位；单调可逆 | **中**：quantile vs uniform 会改变各等级样本数，QWK 量级可变但维度相对可预测性排序稳定 | 部分依赖：绝对分级依赖映射，相对结论（哪些维可预测）稳健 |
| 缺陷阈值口径（绝对 τ 是否可用） | 8.xlsx 阈值为原始 µg/L，1.csv 为对数/标准化空间，换算关系未知 | 默认只用相对判据（不高于源值/目标典型值），阈值仅可换算时辅助 | **低**：取严口径下相对判据已保证不恶化，绝对阈值只会更紧 | **成立**：相对判据独立于阈值换算 |
| Kaggle 外部数据（optional） | 非本地附件，题面允许「按需」参考 | 仅作旁证，不改核心结论 | **无**：不使用则结论不变 | **成立**：核心交付不依赖外部数据 |

> ⛔ 软肋标注：`LABEL_BINNING` 是 Q1 绝对分级结论的软肋——论文中 0-6 分级报告须注明「基于 4.csv 标准化值的单调分位映射重建」，不冒称为原始品评分卡的直接复现。

### 目标/约束原文溯源表

| 建模对象 | 数学表达 | 对应题目原句/对齐表行 |
|---|---|---|
| Q1 目标 | 预测约 40(全 50)维 0-6 分级 $\hat y_{ij}$ | S5「给出…Aroma 与 Flavour…约 40 个感官维度的 0-6 分制分级评分」 |
| Q1 约束 | 缺失条件下建模不删行 | S6「数据缺失条件下的感官评分」 |
| Q1 约束 | $\hat y_{ij}\in\{0,\dots,6\}$ | S5「0-6 离散等级」 |
| Q2 目标 | 每维 Top-3 关键化合物 $\mathrm{Top3}(j)$ | S7「给出每个感官维度的 Top-3 关键因素化合物」 |
| Q2 约束 | 共表达图边权来自 2.csv | S7「利用 2.csv 的化合物相关数据构建化合物共表达图」 |
| Q2 目标 | 稳定性 $f_{jp}$/Jaccard | S8「bootstrap…入选频率、或…Jaccard 系数」 |
| Q3 目标 | 风格条件生成 $p_\theta(x\mid s)$ | S9「以 tasting_category_fine 为风格标签，学习风格条件生成模型」 |
| Q3 约束 | 缺陷不恶化 $x^{def}_{after}\le\min(\tau^{\*},\max(x^{def}_{before},m^t))$ | S10「保持缺陷化合物不恶化…DMS/Diacetyl/4VG/trans-2-nonenal/Stale hops」 |
| Q3 目标 | 跨风格迁移 Pils/Lager→Tripel | S10「把 Pils/Lager 的化合物谱迁移为 Tripel 风格」 |

> 方向核对：Q3 为**风格→化学**生成（非化学→风格分类）；「不恶化」=缺陷**不升高**（这些越低越好）；Q1 求**分级**（不只连续强度）；Q2 求**化合物清单+稳定性**（不只相关）。均与原句一致，无理解反/漏。

---

## 十三、编程实现要点（供 comp-code）

- **环境**：`/e/modex/Modex-MH-Agent-3/runtime/python/python.exe`；库 lightgbm/xgboost/sklearn/shap/networkx/python-louvain/torch（自带 CPU 版足够，CVAE 可选 GPU）。固定 `SEED=42`，只用相对路径，不引用 Modex 内部工具。
- **代码结构**：`code/main.py`（一键入口，依次跑 Q1→Q2→Q3）、`code/q1_*.py`/`q2_*.py`/`q3_*.py`、`code/README.md`（运行命令与操作说明）、`code/requirements.txt`（固定版本）。
- **数据摄入**：`user_data/` 只读；1.csv（250×234，分出 231 特征 + 3 元列）、2.csv（231×232 相关矩阵）、4.csv（250×53，50 标签）、6.csv（44×51 交叉相关）、8.xlsx（阈值/参考，只旁证）。
- **结果落盘**：`submission/q1_sensory_scores.csv`（250 行，utf-8-sig，beer_id+50 维 0-6 整数）、`submission/q2_top3_compounds.csv`（每维 3 行，含 $\phi$/频率/Jaccard/机理）、`submission/q3_generated_profiles.csv`（代表风格生成谱 231 维 + Q1 画像 + 迁移缺陷对照）；逐问结果写 `figures/problem_{1,2,3}_results.json`，汇总 `figures/all_results.json`（含 logic 合同回填键：`q3_defect_compliance_rate`、`gen_tripel_ester_level`、`real_tripel_ester_level`、`logic_probes`）。
- **进度打印**：Q1 每折、Q2 每 50 次 bootstrap、Q3 每若干 epoch 打一行进度。
- **审计**：comp-code 末尾跑 `constraint_audit.py`（按①硬边界）、`logic_audit.py`、`cross_problem_check.py`。

---

## 十四、图表预规划（带入 paper-figure，源自 PROBLEM_ANALYSIS.md FIGURE_MANIFEST）

**数据图（matplotlib，11 张）：**
- `fig_eda_style_pca` — PCA 双标图 [2-panel] — 22 风格样本量 + 化学谱按风格分离 — 数据探索（1.csv）
- `fig_q1_missing_pattern` — 缺失模式矩阵+列缺失率条形 [single] — 1.csv 缺失集中少数列、63/250 行 — 问题一数据处理
- `fig_q1_pred_perf` — 棒棒糖图 [single] — 各感官维 CV QWK 排序 — 问题一结果
- `fig_q1_calibration` — 预测vs实际+残差 [2-panel] — 代表维度 0-6 校准与误差 — 问题一验证
- `fig_q2_coexpr_network` — 网络图 [single] — 化合物共表达图模块结构 — 问题二模型
- `fig_q2_top3_heatmap` — 方法对比热力图 [single] — 感官维×关键化合物重要度 Top-3 高亮 — 问题二结果
- `fig_q2_stability` — 点图+置信区间 [single] — Top-3 bootstrap 入选频率 + 跨方法 Jaccard — 问题二稳定性
- `fig_q2_chem_sensory_corr` — 相关性矩阵图 [single] — 化学×感官交叉相关结构 — 问题二分析（6.csv）
- `fig_q3_style_radar` — 雷达图 [single] — Tripel/Kriek/Lambic 生成谱感官画像 — 问题三结果
- `fig_q3_realvsgen` — t-SNE/UMAP [2-panel] — 真实 vs 生成化学谱降维重叠 — 问题三验证
- `fig_q3_transfer_defect` — 哑铃图 [single] — 迁移前后缺陷化合物 vs 阈值 — 问题三迁移

**HTML 流程/架构图（mono 纯黑白线稿，3 张）：**
- `fig_roadmap` — 技术路线图（三问整体求解思路与依赖）— 问题重述章节末尾
- `fig_arch_q1` — 问题一感官评分 pipeline 架构 — 问题一模型
- `fig_arch_q3` — 问题三 CVAE 风格条件生成架构 — 问题三模型

**正文结果表：** T1（Q1 逐维 QWK/MAE/R²）、T2（Q2 Top-3+稳定性）、T3（Q3 代表风格生成谱+画像+缺陷合规）。

**本步无图表删减/调整**：赛题分析推荐方法均保留为主模型或正当对照（基线/插补对照/高斯兜底），无方法被降为仅交叉验证而需弃图，故不产出 `FIGURE_SKIPPED.json`。

**总数：DATA=11, HTML=3, TIKZ=0, GPTIMG=0, ALL=14。**

---

本题涉及题型：[数据挖掘/机器学习, 统计/回归/预测, 评价/决策(多证据融合排序), 图论(共表达图)]，已对照防错手册审查。









