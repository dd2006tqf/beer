# 交接文档 · MathorCup 大数据 A 题论文

最后更新 2026-10-27｜分支 `main`，已推送，与 origin/main 同步｜最新提交 `0a397f3`

## 一、当前状态

| 项目 | 状态 |
|---|---|
| LaTeX 论文 | `paper/main.pdf`，84 页，编译无错误、无未定义引用 |
| Markdown 稿 | `paper/main.md`，正文 21233 汉字，29 图、15 表 |
| 图表编号 | 图 1-29、表 1-15，连续无重复 |
| 目录 | 在第 3 页，不合格，官方要求第 2 页 |
| 正文页数 | 40 页，不合格，官方要求 30 页内 |
| Word 稿 | `paper/main.docx` 停在 10-26 23:33，未含本轮任何改动 |
| 分支残留 | `experiment/generative-eval`、`experiment/q1-adaptive`，均已合并可删 |
| stash | 2 条旧记录，`stash@{0}` 旧 PDF，`stash@{1}` 可视化 WIP |

## 二、核心结果

| 环节 | 指标 | 数值 |
|---|---|---|
| 问题一 | 50 维平均 QWK | **0.3830**（分维选型前 0.3663，+4.6%） |
| 问题一 | 折外 Spearman | 0.4109 |
| 问题一 | ±1 级准确率 | **0.5729** |
| 问题二 | Top-1 入选频率均值 | 0.9907 |
| 问题二 | 上榜配对入选频率中位数 | **1.000**，≥0.8 占 91.3%，137/150 |
| 问题二 | 跨方法 Jaccard | 0.186，为随机基线 0.0086 的 21.7 倍 |
| 问题二 | 来源完全一致率 | 14%，7 一致 / 16 部分 / 27 不一致 |
| 问题三 | KS 距离 | Tripel 0.3503、Kriek 0.4069、Lambic 0.4102 |
| 问题三 | 画像 Spearman | **0.65-0.92**，即 0.653 / 0.924 / 0.751 |
| 问题三 | 风格 Top-3 识别率 | 100% |
| 问题三 | 缺陷合规 | 相对 44/44；绝对阈值 DMS 3/11、Diacetyl 2/11 超标 |

## 三、本轮完成的工作

**1. 问题一分维选型接入主流水线**，改的是 `code/problem1.py`

分箱退化诊断：前 5 个分位切点跨度小于极差 5% 即判为退化；退化维改用类加权阈值分解有序回归。自动识别出 orange、coriander、clove、lactic、acetic 共 5 维。判据只看标签分布形态、建模前即可确定、全程不接触验证信息；切换是单侧的，其余 45 维完全不变。

试过但未采用：嵌套 CV 逐维自适应（0.3856，无偏，但 17 个原良好维度退化）、等级回归（0.3805）、两者集成（0.3826）。中间数据留在 `_tmp/` 下的 `ordinal_full.csv`、`nested_select.csv`、`ordinal_v2/v3/ens.csv`。

**2. 问题二补两项统计**

融合消融，新增 7.4 节、表 9、图 21：仅相关 2.30 提升到三路融合 2.92 模块覆盖，+27.0%。归因集中度：acetaldehyde 16 维、MeSH 12 维、ethyl_octanoate 10 维，Top-1 与 overall 的中位 |r| 为 0.228。7.3 节补上榜频率中位数，1.000 与 91.3%。

**3. 问题三改「适用边界」框架**

三维评估，即分布保真、新颖性、结构保真，另加两个基线。结论是重采样分布最准但重复率 100%、无迁移能力；CVAE 分布保真较弱，但唯一支持条件迁移。补上 CVAE 值域截断，对齐论文假设 5，实测修正 3.29% 越界单元格。缺陷改两层报告，另补 Stale hops 感官代理。

**4. 数据核对**

题面 226 实际 250，以实测为准；3.xlsx 是空模板，仅作填分模板；4.csv 是标准化值非 0-6，用分位分箱折内估计，不做逆变换；名称映射仅 1 个精确匹配，改按位置对齐并用 Spearman 复核；对数底 37 列 log10、33 列原值；负值 175 列共 10797 个是浓度小于 1 的正常结果，本轮补写；关联键 `beer_id` 只能对上 37/250，改按 `beer` 与行序，本轮补写。

**5. 第 9、10 章重写**

9.2 新增「方法增益的消融汇总」，表 15 与图 29：缺失处理 +0.3%、分级方式 +4.6%、融合 +27.0%、截断 +1.6%。第 10 章压到 3 节 847 字，独占第 45 页。

**6. 可视化**

用 modelviz-skill 重做 4 张，即图 9、10、14、22；新增 4 张，即图 8 分箱退化、图 21 融合消融、图 25 生成对比、图 29 增益汇总；图 14-16 由一张 50×14 大热图拆成三张整宽图。

## 四、遗留问题

### P0 必须解决

**正文 40 页对 30 页上限。** 29 张图里多张占 0.86-0.92 版心宽，第 7 章 11 张最密。纯删文字最多挤出 5-6 页，必须配合缩图：把 0.92 降到 0.78-0.82；第 7 章的图 15-17 可合并或移入附录；第 5 章 5 张可移 2 张。

**目录在第 3 页。** 摘要溢出到第 2 页所致，修法：摘要行距从 1.35 改到 1.15，或删 100-150 字，摘要现为 803 字。

### P1 建议解决

**摘要的 KS 区间是旧值。** 现写「0.357 至 0.408」，重跑后实际为 0.350 至 0.410。

**表 15 在正文里没有引用句。** 9.2 节直接出现表题，前面缺一句「如表 15 所示」。

**「同类研究的约 0.48」没有出处。** 在 7.3 节末尾，需补文献或改成中性表述。

### P2 可选

**Word 稿未同步**，仍是 10-26 版本。要出 Word 需走 `_tmp/md2docx.py` 加目录实测收敛流程，见 README 第 2 节。

**分支与 stash 可清理。** 两个 experiment 分支都已合并。

**4 个图脚本依赖 `_tmp` 里未入库的中间数据**，即 `gen_fig_q1_binning_degeneracy.py`、`gen_fig_q2_ablation.py`、`gen_fig_q3_gen_compare.py`、`gen_fig_q9_gain_summary.py`。clone 后重画这几张需先复算，或把这些 csv 挪进 `figures/` 入库。

## 五、复现命令

```powershell
# 建模，约 20 分钟，在仓库根目录运行并传数据目录
python code\problem1.py user_data
python code\problem2.py user_data
python code\problem3.py user_data

# 编译 LaTeX，必须两遍
cd paper
xelatex -interaction=nonstopmode -output-directory="..\_tmp\lx" main.tex
xelatex -interaction=nonstopmode -output-directory="..\_tmp\lx" main.tex
Copy-Item ..\_tmp\lx\main.pdf main.pdf -Force
cd ..

# 校验目录单页、正文从 1 起
pdfinfo paper\main.pdf | Select-String Pages
pdftotext -f 3 -l 4 paper\main.pdf -
```

## 六、环境备注

- Python 3.12，miniconda；已装 torch 2.6.0+cpu、lightgbm 4.6.0、shap 0.51.0、openpyxl 3.1.5
- MiKTeX 与 XeLaTeX 可用；输出末尾那句「MiKTeX requires Windows 10」是正常噪声
- Codex 模型目录 `C:\Users\40461\.codex\model-catalogs\relay-mvf8zd4x.json` 已加 `deepseek-v4.1-flash-1017`，CLI 可用，桌面端需重启才看得到；同目录有 `.bak` 备份
