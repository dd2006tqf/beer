# 2026 MathorCup 大数据竞赛 赛道 A · 啤酒风味建模 源代码

参赛编号 MCB2600304　题号 A　语言 Python 3.11

## 1. 运行环境

- Python 3.11（已在 3.11.9 验证）
- 依赖见 `requirements.txt`，安装：
  ```bash
  pip install -r requirements.txt
  ```
- **无需 GPU**：CVAE 样本仅 250，CPU 版 PyTorch 即可（代码按 `torch.cuda.is_available()` 自动选设备，有显卡会自动用）。
- 固定随机种子 `SEED=42`（`params.py`），结果可复现。

## 2. 原始数据放置

把赛题附件放到一个目录（默认 `../user_data`，即工作区的 `user_data/`），需包含：
`1.csv 2.csv 4.csv 6.csv 8.xlsx`（以及 3/5/7.csv，可选）。
运行时用 `--data-dir` 指定该目录；代码只用相对路径、只读数据。

## 3. 一键运行

```bash
cd code
python main.py --data-dir ../user_data
```

依次执行：问题一（预测）→ 问题二（归因）→ 问题三（生成），并汇总结果。
可用 `--skip q1,q2` 跳过已完成步骤（Q2 依赖 Q1 的模型缓存 `_tmp/checkpoints/q1_models.pkl`，Q3 依赖同缓存做感官画像；首次请完整跑 Q1）。

## 4. 各源文件作用

| 文件 | 作用 |
|------|------|
| `main.py` | 一键入口，串联三问 + 汇总 `figures/all_results.json` + 回填跨问台账 |
| `params.py` | 全局常数（种子、维度、缺陷列、风格、CVAE 超参）；数值来自 DATA_FACTS/建模报告 |
| `utils.py` | 数据加载（含 DATA_PROFILE 行数核对）、0-6 分箱映射、二次加权 Kappa、随机种子、轻量检查点 |
| `data_check.py` | 数据读取与 231/50 维位置对齐自检（建议先跑） |
| `problem1.py` | 问题一：LightGBM 原生缺失多输出回归 + 7 级分位分箱 + 分层 5 折 CV + 基线/插补对照 |
| `problem2.py` | 问题二：networkx 共表达图 + louvain 社区 + SHAP/相关/模块代表融合 Top-3 + bootstrap 频率 + 跨方法 Jaccard |
| `problem3.py` | 问题三：torch CVAE 条件生成（重参数化+KL+掩码重构）+ 隐空间迁移 + 缺陷投影 + 高斯兜底 + Q1 感官画像 |
| `constraint_audit.py` | 从落盘结果重算全部硬约束（0-6 整数/Top-3 基数/缺陷合规/生成维度） |
| `sanity_check.py` | 结果数值自动审查（NaN/Inf/区间/过拟合信号） |

## 5. 预计耗时（CPU，250 样本）

- 问题一 ≈ 1.5–3 min（50 维 × 5 折 × 主模型+3 基线+KNN 插补对照）
- 问题二 ≈ 1–2 min（50 维 SHAP + RF + 500 次 bootstrap）
- 问题三 ≈ 1–2 min（CVAE 600 epoch 早停）
- 全流程 ≈ 5 min 内

## 6. 输出位置

- 结果文件（提交用）：`submission/q1_sensory_scores.csv`、`q2_top3_compounds.csv`、`q3_generated_profiles.csv`
- 过程数据（供论文作图）：`figures/problem_{1,2,3}_results.json`、`figures/all_results.json`
- 模型缓存：`_tmp/checkpoints/q1_models.pkl`

## 7. 验证指标说明（如实）

本题**无不公开测试集**，所有数字均为**交叉验证/分布距离内部估计**：
- 问题一：分层 5 折 CV 的 QWK/MAE/R²（分箱与插补参数仅训练折估计，防泄漏）；
- 问题二：500 次 bootstrap 入选频率 + SHAP/相关/RF 三法 Jaccard；
- 问题三：生成 vs 真实同风格的 KS 分布距离、迁移缺陷阈值合规率。
不冒称"测试集准确率"。
