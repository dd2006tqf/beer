# 2026 MathorCup 大数据竞赛 · 赛道 A · 啤酒风味建模

**参赛编号** MCB2600304 ｜ **赛道** A

**论文题目**：面向啤酒酿造化合物的感官分级预测、关键化合物归因与风格条件生成

本仓库包含：论文（LaTeX + Word）、建模源码、图表、竞赛提交结果。

---

## 📁 目录结构

```
beer/
├── paper/                     # 📄 论文（可直接阅读 / 二次开发 / 编译）
│   ├── main.tex               #   LaTeX 源（主文件）
│   ├── main.pdf               #   编译好的 PDF（直接阅读）
│   ├── main.docx              #   原始 Word 定稿
│   ├── main.md                #   Markdown 参考
│   ├── cumcm2026.sty          #   CUMCM 样式（main.tex 依赖）
│   └── fonts/                 #   本地字体（Times New Roman / SimSun / SimHei）
│
├── figures/                   # 🖼️ 论文全部插图（LaTeX 编译依赖）
│   ├── fig_*.png              #   14 张正文引用的图
│   ├── TABLE_*.md             #   表格数据备份
│   ├── gen_*.py               #   绘图脚本
│   └── problem_*_results.json #   建模输出
│
├── code/                      # 💻 建模源码（可独立运行）
│   ├── main.py                #   入口
│   ├── params.py              #   全局参数 / 随机种子
│   ├── problem1.py            #   问题一：感官分级预测
│   ├── problem2.py            #   问题二：关键化合物归因
│   ├── problem3.py            #   问题三：风格条件生成
│   └── requirements.txt       #   Python 依赖
│
├── submission/                # 📊 竞赛提交结果
│   ├── q2_top3_compounds.csv
│   └── q3_generated_profiles.csv
│
└── 提交包/                     # 📦 最终提交打包（.gitignore）
```

---

## ✅ 快速开始

### 1️⃣ 阅读论文

直接打开 `paper/main.pdf` 即可（82 页）。也可以看 Word 版 `paper/main.docx` 或 Markdown 版 `paper/main.md`。

### 2️⃣ 修改 & 编译 LaTeX

**前提**：安装 TeX 发行版（MiKTeX 或 TeX Live），需要 XeLaTeX 引擎。

```powershell
# 进入论文目录
cd paper

# 连续编译两遍（第一遍生成 .aux，第二遍填充目录和交叉引用）
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

**字体依赖说明**：
- **本地字体**（已随仓库附带在 `paper/fonts/`）：Times New Roman、宋体 SimSun、黑体 SimHei
- **系统字体**（Windows 自带，无需额外安装）：Consolas（代码块等宽）、Segoe UI Symbol（emoji 渲染）
- 非 Windows 用户：Consolas 和 Segoe UI Symbol 可能需要单独安装，或在 `main.tex` 中替换为对应字体

**编译后产物**：`paper/main.aux`、`paper/main.log`、`paper/main.toc`、`paper/main.out` 等会自动生成，已在 `.gitignore` 中排除。

### 3️⃣ 修改论文内容

- **改文字 / 公式 / 结构**：直接编辑 `paper/main.tex`
- **改原始来源**：`paper/main.docx` 是 Word 定稿（一字一句对应 main.tex 的内容）；转换逻辑在 `_tmp/gen_main_tex.py`（被 gitignore 忽略，如需重新生成请联系原作者）

### 4️⃣ 复现建模

```bash
cd code
pip install -r requirements.txt
python main.py --data-dir ../user_data
```

固定随机种子 `SEED=42`。

---

## 🛠️ 技术栈

| 用途 | 工具 |
|------|------|
| 论文排版 | XeLaTeX + ctexart + cumcm2026 样式 |
| 字体 | Times New Roman / SimSun / SimHei / Consolas |
| 表格 | booktabs + tabularx + longtable |
| 代码块 | listings + xeCJK-listings |
| 交叉引用 | cleveref + hyperref |
| 建模 | Python (LightGBM / CatBoost / XGBoost / PyTorch) |

---

## 📝 提交说明

- 最终交付以 `paper/main.pdf`（LaTeX 版）和 `提交包/AMCB2600304.docx`（Word 版）为准
- 三个提交结果 CSV 在 `submission/` 目录
