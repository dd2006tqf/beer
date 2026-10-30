# 2026 MathorCup 大数据竞赛 · 赛道 A · 啤酒风味建模

**参赛编号** MCB2600304 ｜ **赛道** A

**论文题目**：面向啤酒酿造化合物的感官分级预测、关键化合物归因与风格条件生成

本仓库包含：LaTeX 论文及其 PDF、建模源码、图表与图表数据源、竞赛提交结果。

---

## ⚠️ 交付物优先级（先看这条）

| 位置 | 角色 | 说明 |
|---|---|---|
| `paper/main.tex` | **正式稿源文件** | 全部内容以它为准；图表、正文、附录都在这里 |
| `paper/main.pdf` | **正式交付稿** | 由 `main.tex` 两遍 `xelatex` 编译得到 |
| `figures/derived/*.json` | 图的数据源 | 新增图的中间结果已入库，重画图只需跑 `figures/gen_fig_*.py` |
| `paper/main.md` / `main.docx` | **已废弃（历史副本）** | 停在 2026-10-27，与 `main.tex` 脱节，勿再据其修改 |

**只维护 `paper/main.tex`。** 改完必须两遍 `xelatex` 重新编译 `main.pdf`（见「快速开始」）。

## 重画图与缺失依赖

正文 29 张图的「脚本 → 数据源」映射见 `figures/FIGURE_SOURCES.json`（另含几条未入正文的备用图条目）。绝大多数图只需：

```bash
python figures/gen_fig_<name>.py
```

数据都在仓内（`figures/derived/`、`figures/*.json`、`submission/`、`user_data/`）。

两处例外需要先补外部依赖：

| 图 | 缺什么 | 怎么补 |
|---|---|---|
| `fig_prep_kaggle.png` | `_tmp/kaggle/extracted/beer_data_set.csv`（Kaggle 原始集，因体积与许可未入库） | 从 Kaggle `stephenpolozoff/top-beer-information` 下载后解压到该路径 |
| `fig_q2_shap_ale.png` | `_tmp/checkpoints/q1_models.pkl`（7.4 MB 模型检查点，已忽略） | 运行 `python code/problem1.py user_data` 重建 |

`fig_roadmap.png` 没有 Python 脚本，由同名 HTML 手工导出；PNG 已入库，不影响编译。问题三的 CVAE 架构图已从正文移除，改用 8.1/8.2 节的推导公式。

`figures/gen_fig_q3_ks_ridge.py` 与 `fig_q3_ks_ridge.png` 是一次版式尝试的中间产物，正文未引用，可安全忽略。

排版基线取自上游模板仓库 [yifengchen07/cumcm-latex-template](https://github.com/yifengchen07/cumcm-latex-template.git)（CUMCM 2026 官方 LaTeX 模板），`paper/cumcm2026.sty` 与该模板保持一致。

| `paper/main.md` / `main.docx` | **已废弃** | 2026-10-27 的历史副本，与 `main.tex` 脱节，勿据其修改 |
| `提交包/` | **提交包** | 由 `paper/main.pdf` 与 `submission/*.csv` 组成；Word 版已停用 |
| `paper/main.tex` | **唯一正式稿源文件** | 全部内容以它为准；图、表、正文、附录都在这里 |
| `paper/main.pdf` | **`main.tex` 的编译产物** | **改了 `main.tex` 必须重编出新的 `main.pdf`**（见「快速开始 3️⃣」） |

改论文只改 `paper/main.tex`，改完必须两遍 `xelatex` 重新编译 `main.pdf`。

---

## 🧹 仓库清洁约定（重要）

**任务过程中产生的中间文件、以及只是为了绕开某个临时问题而写的脚本，一律不保留、不提交。**

判断标准：

- **该删**：一次性探针（`probe_*.py`、`dump_*.py`、`inspect*.py`）、调试日志（`*.log`、`*.txt` 的中间转储）、Word 分页实测的临时产物、旧版本的中间 docx/pdf、构建残留（`*.aux` / `*.toc` / `*.synctex.gz`）、已经完成使命的转格式脚本。
- **该留**：被现有代码真实 import 的模块、脚本运行所需的输入数据（`_tmp/checkpoints/`、`_tmp/kaggle/`）、论文正式引用的图表与字体。Word 流水线（`md2docx.py`、`make_toc.py`、`pagemap.*`）已停用，不再需要。

判断"要不要留"的方法：**顺着 import 和文件读取路径查一遍真实引用**，而不是看文件名像不像临时文件。查不到引用的才删。

---

## ❓ 有不确定的点要停下来问我

**执行任何删除、覆盖、提交、改格式之前，若存在以下任一情况，必须先停下来问，不要自行决定：**

1. 某个文件不确定是"中间产物"还是"最终交付的一部分"（例如打包用的 zip、模板填充的试验件）；
2. 两条要求互相冲突（例如"删掉目录"与官方"第二页为目录页"），或与既有决定冲突（例如既定"LaTeX 版不重编"但当前任务要求改 LaTeX）；
3. 需要重新编译 / 重新导出 / 重新求解才能验证的改动；
4. 论文里的某个数字找不到可追溯的来源文件；
5. 改动会波及交付物命名、页码、目录条目等全局一致性。

宁可多问一句，不要猜。

---

## 📁 目录结构

```
├── paper/                     # 📄 论文
│   ├── main.tex               #   唯一正式稿源文件（改这里）
│   ├── main.pdf               #   两遍 xelatex 的编译产物
│   ├── main.md / main.docx    #   已废弃的历史副本
│   ├── cumcm2026.sty          #   LaTeX 样式
│   └── fonts/                 #   本地字体（Times New Roman / SimSun / SimHei）
│
├── figures/                   # 🖼️ 全部插图与表格（38 张图全部进正文）
│   ├── fig_*.png              #   正文插图
│   ├── TABLE_*.md             #   三线表（历史格式，正文表格现写在 main.tex）
│   ├── gen_*.py / supp_*.py   #   绘图与补充分析脚本
│   ├── _figbase.py            #   绘图公共版式（被全部 gen_fig_*.py 引用）
│   └── problem_*_results.json #   建模输出
│
├── code/                      # 💻 建模源码（可独立运行）
│   ├── main.py                #   一键入口
│   ├── params.py              #   全局参数 / 随机种子 SEED=42
│   ├── problem1.py            #   问题一：含缺失的感官分级预测
│   ├── problem2.py            #   问题二：共表达图 + 关键化合物归因
│   ├── problem3.py            #   问题三：风格条件生成与跨风格迁移
│   └── requirements.txt       #   Python 依赖
│
├── _utils/                    # 🔧 绘图公共工具（plot_utils.py）
├── submission/                # 📊 竞赛提交结果（3 个 CSV）
├── user_data/                 # 📥 原始数据（只读，不入库）
├── .claude/skills/            # 🤖 项目级 Agent Skill（见下节）
│   ├── modelviz-skill/        #   ModelViz：科研绘图模板库（89 个模板）
│   ├── lieflat-less-ai-tone/  #   Less AI Tone：成稿去 AI 味检测与改写
│   ├── anti-defensive-writing/    #   Anti-Defensive：按发布会原则组织论文叙事
│   ├── anti-defensive-writing-en/ #   Anti-Defensive 英文版
│   └── oral-paper-skill/          #   Oral Paper：对照顶会 Oral 改进叙事与证据
└── 提交包/                     # 📦 最终提交打包
```

---

## ✅ 快速开始

### 1️⃣ 阅读论文

- **正式稿**：`paper/main.pdf`（由 `paper/main.tex` 两遍 `xelatex` 编译）
- 源文件：`paper/main.tex`

### 3️⃣ 编译（main.tex → main.pdf）

**硬规则：改了 `paper/main.tex` 就必须编译出新的 `paper/main.pdf`，不许留下与源码不符的旧 PDF。**
本仓库的 `paper/main.pdf` 不是「随手存的旧档」，它是 `main.tex` 的编译产物，两者必须同步。

需要 MiKTeX / TeX Live + XeLaTeX，**必须编两遍**（第一遍写目录与交叉引用，第二遍才填对页码）：

```powershell
cd paper
xelatex -interaction=nonstopmode -output-directory=..\_tmp\lx main.tex
xelatex -interaction=nonstopmode -output-directory=..\_tmp\lx main.tex   # 第二遍填目录与交叉引用
Copy-Item ..\_tmp\lx\main.pdf main.pdf -Force
```

编译产物先落在 `_tmp/lx/`，确认无误后再覆盖 `paper/main.pdf`，这样编坏了不会把好文件冲掉。

编完必须核对两件事（官方格式硬要求）：

```powershell
pdfinfo paper\main.pdf | Select-String Pages
pdftotext -f 3 -l 4 paper\main.pdf -    # 第 3 页应是完整目录（单页），第 4 页才是正文第 1 页
```

- 目录必须压进**单页**。相关设置在 `main.tex` 的「目录」注释块里：`\l@section` 段前距改为
  0.30em，目录局部行距 1.05（正文仍为 1.35）。若新增章节导致目录溢出到第二页，先压缩目录排版，
  不要靠删条目解决。
- 正文页码从 1 起连续编号、位于页脚中部，不能有页眉。

**`main.tex` 是唯一正式稿源。** `main.md` / `main.docx` 停在 2026-10-27，仅作历史留存，
不再同步，不要据其修改或交付。

### 4️⃣ 复现建模

```bash
cd code
pip install -r requirements.txt
python main.py --data-dir ../user_data
```

固定随机种子 `SEED=42`。`CODE_CHECK.json` 记录各文件是否可独立运行。

**补充分析脚本**（`code/analysis/`，产出 `figures/derived/` 下的表格与指标数据源）：

```powershell
python code\analysis\q1_ordinal_weighted_all.py    # 表 4 全维类加权有序回归（0.4089 / 0.4509 / 58.7%）
python code\analysis\q1_feature_aug.py             # 表 18 特征增广对照（0.3760 / 0.3747）
python code\analysis\q1_extra_metrics.py            # 表 5 的 MAE/RMSE/严格一致率/Pearson
python code\analysis\q1_r2_positive.py              # 表 5 的 R²>0 维数
python code\analysis\q1_prediction_interval.py      # 分位数回归 vs split-conformal（图 12）
python code\analysis\q1_sensory_matrix_stats.py     # 图 6 感官相关矩阵的分组统计
python code\analysis\q1_sensory_af_pairs.py         # 同名 A/F 跨通道配对相关
python code\analysis\q1_aug_feature_table.py        # 附录表 A.3 / A.4（阈值列与模块 PC1）
python code\analysis\q2_residual_and_q3_energy.py   # 7.1 残差相关 + 能量距离 + 画像 MAE
python code\analysis\q2_module_members_table.py     # 附录表 A.5（55 个社区成员）
python code\analysis\q2_appendix_grade_table.py     # 附录表 A.6（150 条分级）
python code\analysis\q3_multiseed.py                # 5 seed 稳定性
python code\analysis\q3_transfer_direction.py       # 图 28 迁移方向数据
python code\analysis\q1_group_stack.py             # 9.3 分组共享多输出（方案 A，负结果）
python code\analysis\q1_group_stack_boot.py         # 其配对 bootstrap
python code\analysis\q3_disc_cvae.py --lam 0.1      # 9.3 判别辅助损失（λ 可调）
python code\analysis\q3_fivefold.py                 # 表 19 按风格留出的生成对照
```

这些脚本此前散落在 `_tmp/`（已被 gitignore），clone 后无法复现；现统一入库。
`q3_multiseed.py` 会重训 5 次 CVAE，耗时较长；其余脚本依赖先跑过 `code/problem1.py`
（生成 `_tmp/checkpoints/q1_models.pkl`）与 `code/problem3.py`（生成
`submission/q3_generated_profiles.csv`）。

### 5️⃣ 用 ModelViz 画图（可选）

`.claude/skills/modelviz-skill/` 是从 [hrdZhu/modelviz-skill](https://github.com/hrdZhu/modelviz-skill)
迁入的项目级 Skill：89 个科研绘图模板，按「自然语言需求 + 真实数据」选模板、改写模板代码、执行、质检。

```powershell
cd .claude\skills\modelviz-skill

# 原生 Windows 不认 .venv/Scripts，用这个 python 跑
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); print('ok')"
```

首次在别的机器上 clone 后，先重建依赖（`requirements.txt` 只含编排核心库，
模板各自的 matplotlib/scipy/seaborn/shap 等按需安装）：

```powershell
cd .claude\skills\modelviz-skill
python -m venv --system-site-packages .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

使用要点（与主流水线的约定）：

- **模板库只读**：`templates/` 下的脚本不修改，改写产物落在 `workspace/adapted_plot.py`，图落在 `outputs/`。
- **输出要搬进 `figures/` 并转成论文规范**：ModelViz 默认按模板自身 DPI 出图，论文要求 350 DPI PNG、
  正文引用用 `figures/fig_xxx.png`，拿到 `outputs/` 的图后需另存到 `figures/` 并改 `paper/main.tex` 的引用。
- **管线入口是 Python**：`src/services/*_pipeline.py` 需要宿主传入支持 `with_structured_output` 的模型对象，
  不是纯命令行工具；在本仓库里由 Claude 按 `SKILL.md` 的分阶段流程调用。
- 模板库体积 145MB（其中模板示例数据 108MB、预览图 39MB），**随仓库提交**；`.venv/` 与
  `workspace/`、`outputs/` 的运行产物不入库。

### 6️⃣ 用 Less AI Tone 检查成稿（可选）

`.claude/skills/lieflat-less-ai-tone/` 是从 [larashero3-dotcom/lieflat-less-ai-tone](https://github.com/larashero3-dotcom/lieflat-less-ai-tone)
迁入的项目级 Skill：先跑脚本检测和语义判读，交付带例句与改法的改前报告，用户确认后再最小改动并复测。

```powershell
$env:PYTHONIOENCODING='utf-8'
python .claude\skills\lieflat-less-ai-tone\scripts\detect.py paper\main.md --max-hits 5
```

- `SKILL.md` 规定先检测、等用户回复、再改写，不要跳过改前报告直接润色。
- 检测只覆盖成稿；论文结构、图表和 `main.tex` 的编译流程不受影响。
- 运行 Python 时建议设置 `PYTHONIOENCODING=utf-8`，避免 Windows 默认 GBK 控制台把中文报告显示成乱码。

### 7️⃣ 用 Anti-Defensive Writing 组织论文叙事（可选）

`.claude/skills/anti-defensive-writing/` 是从 [Adkid-Zephyr/anti-defensive-writing-Skill](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill)
迁入的项目级 Skill（MIT），英文版在同目录的 `anti-defensive-writing-en/`：按「学术发布会」原则组织摘要、引言、
结论与实验，避免把论文写成工作汇报或提前替审稿人否定自己。

对 Agent 说「按发布会原则改这段摘要」即可触发。它按自身 `SKILL.md` 的完整规则工作：
围绕最强证据组织主线，该收缩主张、重排主结果或重构故事时照做。

### 8️⃣ 用 Oral Paper Skill 对照顶会 Oral 改稿（可选）

`.claude/skills/oral-paper-skill/` 是从 [Adkid-Zephyr/oral-paper-skill](https://github.com/Adkid-Zephyr/oral-paper-skill)
迁入的项目级 Skill：基于 883 篇 ICLR/ICML/NeurIPS Oral 摘要的语义提炼，按「研究张力 → 贡献增量 → 证据对应 →
有解释力的比较 → 条件紧随结论」给出带出处的改稿建议。**证据层级是摘要级**，不用于断言实验严谨性或预测录用。

只迁入了 Skill 本体（`SKILL.md`、`references/`、`agents/`）；上游 `research/` 的 999 个蒸馏过程文件（7.8MB）
未随仓库提交，需要溯源时按 `references/oral-patterns.md` 里的链接回上游仓库查阅。

两个写作 Skill 都只读 `paper/`，不参与 `code/` 求解和 `main.tex` 编译；改完照常重编 PDF。

#### 安装位置：项目内 + Codex 全局

同一份内容装了两份，因为两种 Agent 的查找路径不同：

| 位置 | 谁读它 |
|---|---|
| `.claude/skills/<name>/SKILL.md` | Claude 工作流；随仓库提交，clone 即可用 |
| `~/.codex/skills/<name>/SKILL.md` | Codex（`C:\Users\40461\.codex\skills\`）；只在本机生效，不入库 |

Codex 不扫描项目内的 `.claude/skills`，所以要单独装到全局目录。已装：
`anti-defensive-writing`、`anti-defensive-writing-en`、`oral-paper-skill`。

改完 skill 内容后同步两处，避免版本漂移：

```powershell
$names = "anti-defensive-writing","anti-defensive-writing-en","oral-paper-skill"
foreach ($n in $names) {
    Copy-Item -Recurse -Force ".claude\skills\$n" "$env:USERPROFILE\.codex\skills\$n"
}
```

目录名必须和 frontmatter 里的 `name` 一致，否则 Codex 加载时会对不上。

---

## 🛠️ 技术栈

| 用途 | 工具 |
|------|------|
| 正式稿排版 | XeLaTeX + ctexart（`paper/main.tex`） |
| 版式宏包 | cumcm2026.sty（对齐上游 CUMCM 模板） |
| 公式 | 原生 LaTeX 数学环境（XeLaTeX 直接排版） |
| 建模 | Python（LightGBM / scikit-learn / PyTorch） |
| 图表 | matplotlib / seaborn（350 DPI PNG） |
| 绘图模板 | ModelViz Skill（`.claude/skills/modelviz-skill`，89 个科研模板） |
| 成稿润色 | Less AI Tone Skill（`.claude/skills/lieflat-less-ai-tone`，检测 → 确认 → 改写 → 复测） |
| 叙事组织 | Anti-Defensive Writing Skill（`.claude/skills/anti-defensive-writing`，发布会原则，中/英双语） |
| 对照改稿 | Oral Paper Skill（`.claude/skills/oral-paper-skill`，883 篇顶会 Oral 摘要级提炼） |

---

## 📝 提交说明

- 论文以 `paper/main.pdf`（由 `paper/main.tex` 两遍 `xelatex` 编译）作为正式交付稿
- 三个结果 CSV 在 `submission/`：`q1_sensory_scores.csv`、`q2_top3_compounds.csv`、`q3_generated_profiles.csv`
- 承诺书需队员本人在官方模板上手写或电子签名后扫描，**不由软件代签**
