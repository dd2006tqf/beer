# 2026 MathorCup 大数据竞赛 · 赛道 A · 啤酒风味建模

**参赛编号** MCB2600304 ｜ **赛道** A

**论文题目**：面向啤酒酿造化合物的感官分级预测、关键化合物归因与风格条件生成

本仓库包含：论文（Word 定稿 + Markdown 源 + LaTeX 版及其 PDF）、建模源码、图表、竞赛提交结果。

---

## ⚠️ 交付物优先级（先看这条）

| 位置 | 角色 | 说明 |
|---|---|---|
| `paper/main.md` | **正式稿源文件** | 全部内容以它为准，`_tmp/md2docx.py` 由它生成 Word |
| `paper/main.docx` | **正式交付稿** | 由 `main.md` 自动排版，官方格式（封面表、目录、正文页码从 1） |
| `提交包/AMCB2600304.docx` / `.pdf` | **提交包** | 最终提交用 |
| `paper/main.tex` | **LaTeX 源** | 与 `main.md` 并行维护的第二套稿子，不是自动派生 |
| `paper/main.pdf` | **`main.tex` 的编译产物** | **改了 `main.tex` 必须重编出新的 `main.pdf`**（见「快速开始 3️⃣」） |

改论文请改 `paper/main.md` 后重新生成 docx；改 `paper/main.tex` 后必须两遍 `xelatex` 重新编译 `main.pdf`。
两套稿子互不自动同步，内容修改要么两边都做，要么明确只维护其中一套。

---

## 🧹 仓库清洁约定（重要）

**任务过程中产生的中间文件、以及只是为了绕开某个临时问题而写的脚本，一律不保留、不提交。**

判断标准：

- **该删**：一次性探针（`probe_*.py`、`dump_*.py`、`inspect*.py`）、调试日志（`*.log`、`*.txt` 的中间转储）、Word 分页实测的临时产物、旧版本的中间 docx/pdf、构建残留（`*.aux` / `*.toc` / `*.synctex.gz`）、已经完成使命的转格式脚本。
- **该留**：被现有代码真实 import 的模块、主流程脚本（`_tmp/md2docx.py`、`_tmp/make_toc.py`）、脚本运行所需的输入数据（`_tmp/pagemap.tsv`、`_tmp/toc_entries.json`、`_tmp/checkpoints/`、`_tmp/kaggle/`）、论文正式引用的图表、字体。

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
│   ├── main.md                #   正式稿源文件（Markdown，改这里）
│   ├── main.docx              #   由 main.md 生成的 Word 定稿
│   ├── main.tex / main.pdf    #   LaTeX 版源与编译产物（不自动同步）
│   ├── cumcm2026.sty          #   LaTeX 样式
│   └── fonts/                 #   本地字体（Times New Roman / SimSun / SimHei）
│
├── figures/                   # 🖼️ 全部插图与表格（23 张图全部进正文）
│   ├── fig_*.png              #   正文插图
│   ├── TABLE_*.md             #   三线表（写作时直接并入 main.md）
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
│   └── modelviz-skill/        #   ModelViz：科研绘图模板库（89 个模板）
└── 提交包/                     # 📦 最终提交打包
```

---

## ✅ 快速开始

### 1️⃣ 阅读论文

- **Word 定稿**：`paper/main.docx`
- Markdown 源：`paper/main.md`
- LaTeX 版 PDF：`paper/main.pdf`（由 `main.tex` 编译，改 tex 必须重编）

### 2️⃣ 重新生成 Word（改完 main.md 之后）

```powershell
# 依赖：python-docx、lxml、latex2mathml
# latex2mathml 装在 _tmp/pylibs 里，必须先把它加进 PYTHONPATH，否则 import 直接报错
$env:PYTHONPATH="$PWD\_tmp\pylibs"
python _tmp\md2docx.py paper\main.docx
```

目录页的页码是**实测**出来的，不是估算的。`md2docx.py` 生成的目录页码来自
`_tmp/toc_entries.json`，后者由「Word 打开 docx → Repaginate → 逐段记显示页码」
实测得到：

```powershell
& .\_tmp\pagemap.ps1            # 生成 _tmp/pagemap.tsv（正调 PowerShell，不要加 -ExecutionPolicy Bypass）
$env:PYTHONPATH="$PWD\_tmp\pylibs"
python _tmp\make_toc.py         # 生成 _tmp/toc_entries.json
python _tmp\md2docx.py paper\main.docx   # 重排目录
```

正文内容有增删时按此顺序走一遍，**并且要循环到目录收敛**：重排后分页会变，
页码跟着变，再探测一次、再比对 `toc_entries.json` 是否与上一轮完全一致；
一致才算稳定，否则再走一轮。

### 3️⃣ 编译 LaTeX 版（main.tex → main.pdf）

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

**`main.tex` 与 `main.md` 是两套并行的稿子，不互相自动同步。** 改哪一套就重新生成哪一套的产物：
改 `main.md` → 生成 `main.docx`；改 `main.tex` → 生成 `main.pdf`。内容修改要两边都做，
或者明确只维护其中一套。Word 是正式交付稿，LaTeX 版用于阅读与二次编译。

### 4️⃣ 复现建模

```bash
cd code
pip install -r requirements.txt
python main.py --data-dir ../user_data
```

固定随机种子 `SEED=42`。`CODE_CHECK.json` 记录各文件是否可独立运行。

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
  正文引用用 `figures/fig_xxx.png`，拿到 `outputs/` 的图后需另存到 `figures/` 并改 `paper/main.md` 的引用。
- **管线入口是 Python**：`src/services/*_pipeline.py` 需要宿主传入支持 `with_structured_output` 的模型对象，
  不是纯命令行工具；在本仓库里由 Claude 按 `SKILL.md` 的分阶段流程调用。
- 模板库体积 145MB（其中模板示例数据 108MB、预览图 39MB），**随仓库提交**；`.venv/` 与
  `workspace/`、`outputs/` 的运行产物不入库。

---

## 🛠️ 技术栈

| 用途 | 工具 |
|------|------|
| 正式稿排版 | Markdown → python-docx（`_tmp/md2docx.py`） |
| LaTeX 版 | XeLaTeX + ctexart + cumcm2026 |
| 公式 | LaTeX → latex2mathml → OMML（Word 原生公式） |
| 建模 | Python（LightGBM / CatBoost / XGBoost / PyTorch） |
| 图表 | matplotlib / seaborn（350 DPI PNG） |
| 绘图模板 | ModelViz Skill（`.claude/skills/modelviz-skill`，89 个科研模板） |

---

## 📝 提交说明

- 论文以 `提交包/AMCB2600304.docx`（含同名 PDF）提交
- 三个结果 CSV 在 `submission/`：`q1_sensory_scores.csv`、`q2_top3_compounds.csv`、`q3_generated_profiles.csv`
- 承诺书需队员本人在官方模板上手写或电子签名后扫描，**不由软件代签**
