# 2026 MathorCup 大数据竞赛 赛道 A · 啤酒风味建模

参赛编号 **MCB2600304**　赛道 **A**
论文题目：**面向啤酒酿造化合物的感官分级预测、关键化合物归因与风格条件生成**

本仓库包含该参赛论文的全部内容：论文正文、建模源代码、结果数据、图表、提交文件，以及用于排版的 LaTeX 模板。

---

## 一、目录结构

| 目录 / 文件 | 说明 |
|---|---|
| `paper/` | 论文目录。`main.md` 为**内容唯一权威源**；`main.tex` 为 LaTeX 排版稿，`main.pdf` 为编译产物（82 页） |
| `code/` | 建模与提交代码（Python，问题一/二/三），运行方式见 [`code/README.md`](code/README.md) |
| `figures/` | 论文全部插图（23 张 PNG，由建模代码生成） |
| `submission/` | 三个提交结果：`q1_sensory_scores.csv`、`q2_top3_compounds.csv`、`q3_generated_profiles.csv` |
| `templates/` | 第三方模板。**含本次新引入的 `cumcm-latex-template/`（见下）** |
| `user_data/` | 赛题原始附件（`1.csv … 8.xlsx`） |
| `_tmp/` | 中间产物与 `md → tex` 转换脚本 `gen_tex_cumcm.py` |
| `提交包/` | 最终提交包：Word 定稿（docx/pdf）、附件 zip、三个 CSV |

---

## 二、论文 LaTeX 排版（新引入 CUMCM 模板）

本项目论文已改用 **CUMCM（全国大学生数学建模竞赛）LaTeX 模板** 的版式样式排版。

- **模板来源**：<https://github.com/yifengchen07/cumcm-latex-template.git>
- **引入位置**：`templates/cumcm-latex-template/`（完整模板原件，请勿删改；含 `cumcm.tex`、`cumcm2026.sty`、`references.bib`、`fonts/`、`README.md`、`LICENSE` 等）
- **适配说明**：本文是 **MathorCup 论文**，仅**借用 CUMCM 模板的排版样式**（页面、字体、三线表、代码块样式等），并非真正向 CUMCM 投稿。
- **内容与排版分离**：论文文字、数字、图表、公式、参考文献、附录代码均以 `paper/main.md` 为准（一字不改）；`paper/main.tex` 由转换脚本 `_tmp/gen_tex_cumcm.py` 从 `main.md` 自动生成，不在 tex 里手工改正文。
- **样式与字体副本**：`paper/cumcm2026.sty` 与 `paper/fonts/`（Times New Roman、SimSun、SimHei）是从模板复制到论文目录的本地副本，**必须与 `main.tex` 同目录**。
- **封面表格保留**：按要求保留原封面的信息表格（队伍编号 `MCB2600304`、赛道 `A`），位于 `\maketitle` 之前；目录（两页）也保留。

### 编译方式

需要 **XeLaTeX + ctex**（本机为 MiKTeX）。本机没有安装 perl，`latexmk` 不可用，因此直接调用 `xelatex` 连续编译两遍（第二遍用于生成目录与交叉引用）：

```powershell
cd paper
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

- 字体由模板显式从 `paper/fonts/` 加载：正文中文宋体、标题黑体、英文 Times New Roman。
- 代码块（listings）等宽使用 Consolas，中文注释走宋体；附录代码中少量特殊符号（`✅`、`❌`、`∈`）Consolas/SimSun 未覆盖，经 listings 字符转义映射到 Segoe UI Symbol 渲染。

### 内容改动后重新生成

正文一律改 `paper/main.md`，然后重新生成并编译：

```powershell
python _tmp/gen_tex_cumcm.py
cd paper
xelatex -interaction=nonstopmode main.tex
xelatex -interaction=nonstopmode main.tex
```

---

## 三、建模复现

完整说明见 [`code/README.md`](code/README.md)，一键运行：

```bash
cd code
python main.py --data-dir ../user_data
```

固定随机种子 `SEED=42`；本题无公开测试集，所有指标均为交叉验证 / bootstrap / 分布距离的内部估计。

---

## 四、提交物

- 论文 PDF（LaTeX 版）：`paper/main.pdf`
- 论文 Word 定稿：`提交包/` 内的 `AMCB2600304.docx` / `.pdf`（内容与 LaTeX 版一致）
- 源代码：`code/`
- 三个提交结果 CSV：`submission/`
