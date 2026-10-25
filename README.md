# 2026 MathorCup 大数据竞赛 · 赛道 A · 啤酒风味建模

**参赛编号** MCB2600304 ｜ **赛道** A

**论文题目**：面向啤酒酿造化合物的感官分级预测、关键化合物归因与风格条件生成

本仓库包含：论文（Word 定稿 + Markdown 源 + LaTeX 存档版）、建模源码、图表、竞赛提交结果。

---

## ⚠️ 交付物优先级（先看这条）

| 位置 | 角色 | 说明 |
|---|---|---|
| `paper/main.md` | **正式稿源文件** | 全部内容以它为准，`_tmp/md2docx.py` 由它生成 Word |
| `paper/main.docx` | **正式交付稿** | 由 `main.md` 自动排版，官方格式（封面表、目录、正文页码从 1） |
| `提交包/AMCB2600304.docx` / `.pdf` | **提交包** | 最终提交用 |
| `paper/main.tex` / `main.pdf` | **历史存档副本** | LaTeX 版，供阅读与二次编译；**不是交付稿**，不随 `main.md` 自动同步 |

改论文请改 `paper/main.md` 后重新生成 docx；`main.tex` 只在需要 LaTeX 版本时单独维护。

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
│   ├── main.tex / main.pdf    #   LaTeX 存档版（不自动同步）
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
└── 提交包/                     # 📦 最终提交打包
```

---

## ✅ 快速开始

### 1️⃣ 阅读论文

- **Word 定稿**：`paper/main.docx`
- Markdown 源：`paper/main.md`
- LaTeX 存档版：`paper/main.pdf`

### 2️⃣ 重新生成 Word（改完 main.md 之后）

```powershell
# 依赖：python-docx、lxml、latex2mathml
python _tmp\md2docx.py paper\main.docx
```

目录页的页码是**实测**出来的，不是估算的。`md2docx.py` 生成的目录页码来自
`_tmp/toc_entries.json`，后者由「Word 打开 docx → Repaginate → 逐段记显示页码」
实测得到：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File _tmp\pagemap.ps1   # 生成 _tmp/pagemap.tsv
python _tmp\make_toc.py                                                # 生成 _tmp/toc_entries.json
python _tmp\md2docx.py paper\main.docx                                 # 重排目录
```

正文内容有增删时按此顺序走一遍，否则目录页码会与实际分页不符。

### 3️⃣ 编译 LaTeX 存档版（可选）

需要 MiKTeX / TeX Live + XeLaTeX。

```powershell
cd paper
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex   # 第二遍填目录与交叉引用
```

目录压到单页的设置在 `main.tex` 的「目录」注释块里：`\l@section` 段前距改为
0.30em，目录局部行距 1.05（正文仍为 1.35）。

### 4️⃣ 复现建模

```bash
cd code
pip install -r requirements.txt
python main.py --data-dir ../user_data
```

固定随机种子 `SEED=42`。`CODE_CHECK.json` 记录各文件是否可独立运行。

---

## 🛠️ 技术栈

| 用途 | 工具 |
|------|------|
| 正式稿排版 | Markdown → python-docx（`_tmp/md2docx.py`） |
| LaTeX 存档版 | XeLaTeX + ctexart + cumcm2026 |
| 公式 | LaTeX → latex2mathml → OMML（Word 原生公式） |
| 建模 | Python（LightGBM / CatBoost / XGBoost / PyTorch） |
| 图表 | matplotlib / seaborn（350 DPI PNG） |

---

## 📝 提交说明

- 论文以 `提交包/AMCB2600304.docx`（含同名 PDF）提交
- 三个结果 CSV 在 `submission/`：`q1_sensory_scores.csv`、`q2_top3_compounds.csv`、`q3_generated_profiles.csv`
- 承诺书需队员本人在官方模板上手写或电子签名后扫描，**不由软件代签**
