# 研究项目: MathorCup 大数据 A题 - 2026年MathorCup大数据挑战赛-赛道A初赛

## 项目说明
这是一个自动化研究管理的工作流引擎，当前正在执行「MathorCup 大数据竞赛」流水线。

## 流水线步骤
  1. 赛题分析 (comp-prob-analysis)
  2. 建模求解 (comp-modeling)
  3. 编程实现 (comp-code)
  4. 图表生成 (paper-figure)
  5. 流程与架构图绘制 (paper-figure-html)
  6. 竞赛论文撰写（Word 稿） (comp-paper-zh-docx)
  7. 解析格式要求 (format-profile)
  8. 识别 Word 模板占位 (docx-template-map)
  9. Markdown 格式自检与修复 (docx-format-check)
  10. 格式检查与 Word 导出 (docx-export)

## 重要规则
- 所有产出文件都写入当前工作目录（不要写到其他位置）
- 用 Write 工具创建文件、Edit 工具修改；文件太长就先 Write 第一段（末尾留一行占位注释），再用 Edit 把占位换成下一段，每段不超过 150 行
- 不要用 Bash heredoc（cat << 'EOF'）写文件：本机 Bash 会把成对的反斜杠吃成一个，加了引号也一样
- 可能跑很久的脚本（模型拟合、Bootstrap、大循环）用 timeout 包着跑，如 `timeout 900 python code/xxx.py`：命令跑久了会被转到后台，卡住的后台进程不结束，这一步就一直等它。要停后台进程，先按命令行查出真实进程号再结束：`powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object CommandLine -like '*xxx.py*' | Select-Object ProcessId,CommandLine"`，不要凭记忆写进程号
- 每个步骤完成后至少产出一个文件
- 读取工作区中已有的文件，在前步骤的基础上继续工作
- 使用中文撰写论文（除非是 LaTeX 代码）

## 工作区文件
- CUSTOM_REQUIREMENTS.md
- FORMAT_REQUIREMENTS.md
- _problem_file.txt
- user_data/1.csv
- user_data/2.csv
- user_data/2026年MathorCup大数据挑战赛-赛道A初赛.pdf
- user_data/2026年MathorCup大数据挑战赛-赛道A初赛_extracted.txt
- user_data/3.xlsx
- user_data/4.csv
- user_data/5.csv
- user_data/6.csv
- user_data/7.csv
- user_data/8.xlsx
- user_data/PROBLEM_STATEMENT.md
- user_data/数据说明.txt
`user_data/` 下是用户上传的原始材料，请完整阅读并作为研究基础；其余是前面步骤的产物，按需读取，未经本步核对不要当成题目事实。目录摘要只压缩重复路径，不允许把全量数据分析降级为抽样分析。

## 📋 用户自定义需求/大纲（最高优先级）
用户上传了自定义要求或大纲文档 `CUSTOM_REQUIREMENTS.md`。
**请仔细按此文档的要求和思路执行工作流，此文档具有最高优先级指导。**
**当与文档内容发生冲突，以此文档为准。**

### 文档内容
```
附件数据为给出的数据集，如果需要更多的数据，可
以参考公开数据集
https://www.kaggle.com/datasets/stephenpolozoff/top-beer-information;对于这个数据集，你按需收集，在已有数据的基础上可以进一步使用这个kaggle里面的数据集；
```

## 参数
- 研究主题: MathorCup 大数据 A题 - 2026年MathorCup大数据挑战赛-赛道A初赛
- template: comp_mathorcup_bigdata
- problem_statement: 附件数据为给出的数据集，如果需要更多的数据，可
以参考公开数据集
https://www.kaggle.com/datasets/stephenpolozoff/top-beer-information;对于这个数据集，你按需收集，在已有数据的基础上可以进一步使用这个kaggle里面的数据集
- template_files: ['user_template/2026年MathorCup数学应用挑战赛—大数据竞赛论文模板.docx']
- template_file: user_template/2026年MathorCup数学应用挑战赛—大数据竞赛论文模板.docx
- format_text: （较长，全文见工作区 FORMAT_REQUIREMENTS.md）
- competition: mathorcup_bigdata
- language: zh
- output_format: docx
- flowchart_engine: html
- problem_id: A
- contest_stage: preliminary
- team_id: MCB2600304
- tools: python
- custom_requirements: 附件数据为给出的数据集，如果需要更多的数据，可
以参考公开数据集
https://www.kaggle.com/datasets/stephenpolozoff/top-beer-information;对于这个数据集，你按需收集，在已有数据的基础上可以进一步使用这个kaggle里面的数据集；
- min_figures: auto
- min_tables: auto
- min_models: auto
- diagram_style: mono

## Bash 环境变量（页数/字数等检查脚本会用到）
工作区已自动生成 `.env_skill`，含以下数值参数：

```bash
export SUBMISSION_PAGE_REFERENCE=30
```

**说明**：`SUBMISSION_PAGE_REFERENCE` 只供最终报告提示；正文不设页数目标，不据此扩写或压缩。其他数值按用户内容要求使用。脚本读取参数时，在 bash 块开头加一行 `source .env_skill 2>/dev/null || true` 就能让数值设置正确取到值。
**最终以论文实际质量为准**，不要为了凑页数刻意注水。

## ⛔ 流程图/架构图引擎 = HTML（用户选定，全程遵守）
- 本工作流的流程图 / 技术路线图 / 系统架构图**一律用 HTML+CSS 绘制**（`paper-figure-html` skill：flex/grid 自动布局 → Electron printToPDF 转矢量 PDF），**不使用 DrawIO**。
- 规划阶段（paper-plan / paper-plan-zh 等）写 FIGURE_MANIFEST 时，流程/架构图那一类的**章节标题请写「HTML 流程/架构图」**（不要写「DrawIO 流程/架构图」），与实际引擎保持一致，避免误导后续写作。图名前缀（fig_arch / fig_flow / fig_roadmap 等）不变。
- 写作阶段按 `figures/latex_includes.tex` 里已生成的 `fig_*.pdf` 直接引用即可，**无需也不要提及 DrawIO / .drawio 文件**（本工作流不产生任何 .drawio 文件）。

## HTML 流程图/架构图风格 = C 纯黑白线稿（仅限非数据图）
- `paper-figure-html` 的 Step 1 计算风格种子时，**强制 `STYLE_FAMILY=2`**，跳过配色随机分配（识别标记：`MH_DIAGRAM_STYLE=2`）。
- 仅这些流程图/架构图遵守该族：mono 使用黑白；plain 使用暖棕强调；modern 使用靛蓝强调。不得跨族换色。
- 此设置不适用于 matplotlib/seaborn 数据图；不得因 diagram_style=mono 把数据图、热力图或论文中的全部图片转成灰度。数据图使用下方独立配置。
- LAYOUT/ARROW 等只允许在语义等价时改变结构或连线；同篇统一视觉 token，异篇差异来自题目真实依赖。

<!-- INJECT:USER_TEMPLATE -->

## ⛔ 用户上传的 Word 模板（最高优先级）
- 模板文件：`user_template/2026年MathorCup数学应用挑战赛—大数据竞赛论文模板.docx`（识别报告：`user_template/模板识别报告.md`）。Word 输出时按它排版：保留原封面、页眉页脚和样式，内容填进占位处。
- 中图分类号、文献标识码、文章编号、收稿日期、基金项目、作者简介、作者姓名和单位这类事实，软件不编：模板里原样留着，交付时列出来请用户填。
- 模板包里的说明文档只供参考，不是研究资料，不要引用、不要当数据。
<!-- /INJECT:USER_TEMPLATE -->

## ⛔ 输出格式：Word（DOCX）
- **本工作流将导出为 Word 文档（.docx），不编译 LaTeX**
- 写作步骤产出 **纯 Markdown 文件**，不要写 LaTeX 代码
- 论文写作步骤产出 `paper/main.md`（不是 main.tex）
- 竞赛论文写作步骤产出 `paper/main.md`（不是 main.tex）
- 所有公式用 Markdown 格式：行内 `$E=mc^2$`，块级 `$$...$$`
- 表格使用 Markdown 表格语法（`| 表头 | ... |\n|---|---|\n`），**优先用 `cat figures/TABLE_xxx.md >> paper/main.md` 嵌入已生成的表格**（数据真实，杜绝编造）
- 图片使用 Markdown 图片语法 `![描述](figures/xxx.png)`
- 参考文献用 `[1] 作者. 题名[J]. 期刊, 年, 卷(期): 页码.` 格式
- 编译相关步骤会自动跳过，最后一步会把 Markdown 转 Word

## 竞赛规则（MathorCup 数学应用挑战赛—大数据竞赛）
- 语言: 中文
- 页数策略: 本地生成不设硬上限；最终提交参考为 30 页。超过只提醒，不失败、不删核心推导、不缩字号、不压小图；低于参考值也不按比例强制扩写。
- LaTeX 模板: MathorCupmodeling
- 机理题写作：原始定律/几何关系 → 关键代入与变形 → 完整方程及初边值 → 与代码一致的离散、事件切换和停止准则 → 真实结果与误差依据。先写数学骨架再嵌图；不以图表数量代替推导，通用算法科普可省但本题求解过程不能省。
- 官方提交四项：论文 PDF（题号+参赛编号，如 AMCB2600001.pdf）、承诺书（队员手写或电子签名后扫描成 PDF 或 JPG，AI 不代签）、支撑材料压缩包（程序、结果数据、操作说明，不含赛题原始数据）、按题目要求上传的计算结果文件
- 官方评分四项：论文质量；代码完整、正确、高效并附详细操作说明；不公开测试集上的准确率/召回率等指标；创新性
- 官方格式（不符合取消评奖资格）：第一页写题目、摘要和关键词（页首“队伍编号/赛道”表格）；第二页为目录页；目录之后开始正文，从正文开始编页码，页脚居中、从 1 连续编号；不能有页眉，不能出现队员姓名和学校
- 正文控制在 30 页以内、附录页数不限；本地生成超出只提醒，不设硬上限
- 摘要简明写出解决问题的核心思想与效果（模型/算法与真实验证指标），只写中文摘要
- 正文写清数据处理、模型与算法细节、求解过程和结果分析；按本题依赖链自适应组织
- 参考文献按正文引用次序编号，正文用方括号标编号；书籍：[编号] 作者，书名，出版地：出版社，出版年；期刊：[编号] 作者，论文名，杂志名，卷期号：起止页码，出版年；网上资源：[编号] 作者，资源标题，网址，访问时间（年月日）；引用书籍要写页码
- 附录写明实际使用的软件名称、运行命令和自己编写的全部源程序（官方要求），源程序同时作为支撑材料提交
- 题目要求放进正文的结果表原样出现在正文；题目要求的结果文件按规定的文件名、列名和格式生成
- 使用大数据专用的 MathorCupmodeling 模板（\bianhao 参赛编号、\tihao 赛道、\timu 题目；\end{abstract} 之后那一行生成目录页，不能删），XeLaTeX 编译
- 题号: A
- 编程工具: python

## 计算质量与有界验证
- 题设硬约束、真实数据、计算正确性必须同时满足，不通过改数据/放宽题设让结果显得合理。
- 编程实现步骤每问执行 validate_constraints()，从实际保存的结果核对必要条件、有限数值和任务能力。
- 编程实现步骤发现真实违例须定位并修受影响实现；模型变更要有依据，不能凭空加接触/公平性约束。
- 步骤授权边界：每一步只改本步产物。数据图/流程图/论文撰写/编译导出步骤不得修改 code/、figures/*_results.json、figures/all_results.json、output/、RESULTS.md、MODELING_REPORT.md、PROBLEM_ANALYSIS.md、PROBLEM_FACTS.json，也不重跑求解；发现上游结果有问题，写进 UPSTREAM_ISSUES.md（问题、证据、影响哪一问）后按现有结果完成本步。后台会在这些步骤结束时核对上游产物，被改动的会还原。
- 高分、负测试 R²、相同最优值、闲置资源、边界解仅是待解释现象，不单凭现象重算。
- 跨问单调比较须同目标同口径且可行域包含；最优值允许相等，启发式结果不冒充最优性证明。
- 用完整物理几何与正确单位；等价简化需要依据。全覆盖题不得以中心覆盖替代，局部覆盖题也不升级任务。
- 方法、步长、误差和验证次数按题设/建模方案确定，不统一强制 1e-6、双算法、五个种子或十维降维。
- 有可核对求解证书、解析对照或真实独立验证时可复用；必须做的验证不能以文件存在或关键词代替。
- 编程保存完整结果数据，图表排版在绘图步骤，章节在撰写步骤，最终排版/编译在导出步骤。
- 同版本输入、源码、参数和验证器的检查点可复用；变化只重验受影响算例，不在每层各跑一次全量求解。
- 本地检查失败先区分真实错误、缺证据与环境故障；缺说明补说明，环境故障修环境，不自动调用付费生成。
- 使用工作流统一的返修与时间预算；耗尽时保存进展、如实报告未完成，不假报成功也不无限重试。

## 等计算时的单次等待上限
- 等后台任务（TaskOutput、sleep、轮询）单次最多 4 分钟（TaskOutput 的 timeout ≤ 240000 毫秒），没结束就再等同一个任务；不要一次等 10 分钟，也不要在一次前台调用里阻塞超过 4 分钟。超过 5 分钟没有新消息，提示缓存失效，下一轮要按全价重读整段上下文。
- 两次等待之间只看进度（日志末几行、已完成算例数），不重读大文件，不另起第二份求解。
- 赛题分析、建模步骤里的验证性试算单次不超过 3 分钟（命令前加 timeout 180），更长的求解留给编程实现步骤。

<!-- MH_BIGDATA=1 -->
## MathorCup 大数据竞赛专项（各步骤按本段和本步骤 SKILL 的 MH_BIGDATA 段执行）
- 赛段：初赛；题号：A；参赛编号：MCB2600304
- 评分四项同等重要：论文质量；代码完整、能运行并附操作说明；结果在不公开测试集上的指标；创新性。不要只顾论文，结果文件和代码同样要交、同样计分。
- 赛题分析：除常规产物外写出 `SUBMISSION_SPEC.json`（题目要求的结果文件、要放进正文的结果表、评价指标，每项附题面原文），后台在本步结束时会核对它。
- 建模：写清与官方评价指标一致的验证方案（交叉验证/按时间切分/留出集）、基线对比和泄漏风险；不拿测试集调参，不把验证集分数说成测试集成绩。
- 编程：结果文件写到 `submission/`，文件名、列名、行数、编号与 `SUBMISSION_SPEC.json` 一致；`code/` 里要有一键入口 `main.py`、操作说明 `README.md`、依赖清单 `requirements.txt`，固定随机种子、只用相对路径，不引用 Modex 内部工具。后台在本步结束时会核对结果文件和代码说明。
- 论文：选了 Word 输出，只写 `paper/main.md`；导出 Word 时后台按官方格式自动排版（第一页最上方“队伍编号 / 赛道”信息表和题目、摘要、关键词，第二页目录，正文从第 1 页编页码，不能有页眉；不写队员姓名和学校；不符合官方格式会被取消评奖资格）；main.md 里不要手写信息表、目录和分页符，附录里的程序用代码块原样贴入；摘要写核心思想和真实验证指标；题目要求的结果表放正文；参考文献按官方格式；附录写明使用的软件名称、运行命令和自己写的全部程序；只写真实跑出来的数，没有标准答案的测试集不写"准确率"。
- 导出：Word 检查通过后，本机有 Word 就同时导出同内容的 `paper/main.pdf`（官方只收 PDF）；流程收尾整理提交包（按官方命名的论文 PDF——没有 PDF 时放 Word 并提醒另存、支撑材料压缩包、单独上传的计算结果、提交说明，并核对论文格式）。承诺书需每个队员在官方模板上手写或电子签名后扫描成 PDF 或 JPG，AI 不代签、不伪造签名。
- 数据：`user_data/` 只读；大文件分块读取；训练/推理要持续打印进度（每轮或每 1–2 分钟一行），单次训练不超过 60 分钟并保存检查点；软件自带 CPU 版 PyTorch、lightgbm、xgboost 等，要用显卡或自带里缺的库时按编程步骤 SKILL 的说明装进独立文件夹，不往软件自带的 Python 里装包。

## 文档原文（已自动提取，按需读取）
用户上传的文档已经在 `user_data/` 目录下提取为文本/markdown 文件，**用 Read 工具按需读取，不要尝试一次性读所有文件**。
- 每个提取文件的第一行括号写明来源：`Vision OCR` / `部分识别` 是图像逐字转录（PDF 或赛题图片），`PDF 文本层` 是还没做图像识别的临时文本（上下标、公式会丢），`pandoc 转换` 基本保真，`python-docx 兜底` / `旧版 .doc 兜底解析` 会丢公式或符号
- 同名的 `*_extracted_check.md` 是图像识别与 PDF 原文的数字核对清单，有就要逐条核对

文件清单（按字符数排序）：

- **2026年MathorCup大数据挑战赛-赛道A初赛** → `user_data/2026年MathorCup大数据挑战赛-赛道A初赛_extracted.txt` (1,934 字符)
  - 开头: # 2026年MathorCup大数据挑战赛-赛道A初赛.pdf 内容提取（PDF 文本层，尚未图像识别：上下标、公式和表格可能丢失或错位，系统完成图像识别后会覆盖本文件） 2026年MathorCup数学应用挑战赛——大数据竞赛 赛道A：…

**用法示例**: 如果你需要某篇论文的内容, 用 `Read` 工具读对应的 `user_data/xxx_extracted.md` 文件。可以用 `Grep` 工具按关键词搜索定位特定信息。

## 数据图配色与版式（仅限数据图，与流程图独立）
<!-- MH_DATA_FIG_ENGINE=default -->
数据图只读取 MH_DATA_FIG_* 配置，不读取 diagram_style / MH_DIAGRAM_STYLE。默认配色按工作区固定种子选择；Nature 引擎保留 Nature 版式。黑白打印可辨认是可读性要求，不等于必须导出灰度。除非用户明确选择数据图灰阶，不得用灰阶列表覆盖配色或将正式 PNG/PDF 强制转灰。黑色文字、参考线和合理的中性区域仍可使用；不要求每张图必须出现彩色。质检核对所属图种的配置，不得自行增加全图灰阶断言；更改颜色不得更改原始数值。

<!-- MH_DATA_FIG_PALETTE=random -->
数据图配色：未指定固定色卡，使用对应引擎的工作区稳定默认配色；不继承流程图的黑白选择。

<!-- INJECT:COURSE_DOCX_PNG_ONLY -->


## ⛔ 输出格式：仅 PNG（Word 导出工作流）
本工作流最终导出 Word 文档（.docx），Word **不能嵌入 PDF**，因此：
**所有图表只输出 PNG，不要输出 PDF**：
```python
from _utils.plot_utils import setup_style, save_fig; setup_style()
# ⛔ Word 模式：只用 .png 扩展名（save_fig 会自动 350 DPI 防中文糊）
save_fig(fig, 'figures/fig_xxx.png')
# ⛔ 不要再调用 save_fig(fig, 'xxx.pdf') 或 fig.savefig('xxx.pdf')
```
**对于 drawio/GPT Image/TikZ 等只有 PDF 的图，必须立刻转 PNG 并删除原 PDF**：
```bash
# 包含 fig_*.pdf 和 tikz_*.pdf（TikZ 几何/算法图编译产出，最容易被漏）
for pdf in figures/fig_*.pdf figures/tikz_*.pdf; do
    [ -f "$pdf" ] || continue
    bn=$(basename "$pdf" .pdf)
    png="figures/${bn}.png"
    if [ ! -f "$png" ]; then
        # DPI=350（含中文小字时；250 以下会糊）
        python -c "import fitz; doc=fitz.open('$pdf'); pix=doc[0].get_pixmap(matrix=fitz.Matrix(350/72, 350/72), alpha=False); pix.save('$png')" 2>/dev/null || \
        python -c "from pdf2image import convert_from_path; convert_from_path('$pdf', dpi=350)[0].save('$png','PNG')" 2>/dev/null || \
        echo "⚠ $pdf → PNG 转换失败"
    fi
    # 转完后删除 PDF（Word 不需要，避免冗余）
    [ -f "$png" ] && rm -f "$pdf"
done
```
**⛔ TikZ 多页 PDF（一个 tikz_diagrams.tex 画了多张图）**：先拆页再转 PNG：
```bash
for tpdf in figures/tikz_diagrams.pdf figures/tikz_*.pdf; do
    [ -f "$tpdf" ] || continue
    pages=$(python -c "import fitz; print(fitz.open('$tpdf').page_count)" 2>/dev/null || echo 1)
    bn=$(basename "$tpdf" .pdf)
    if [ "$pages" -gt 1 ]; then
        # 多页：每页转一张 PNG（tikz_diagrams_1.png, _2.png ...），供 main.md 分别引用
        python -c "import fitz; d=fitz.open('$tpdf'); [d[i].get_pixmap(matrix=fitz.Matrix(350/72,350/72),alpha=False).save(f'figures/${bn}_{i+1}.png') for i in range(d.page_count)]" 2>/dev/null && rm -f "$tpdf"
    fi
done
```
**核查清单**（写完所有图后必须跑）：
```bash
# 1. figures/ 不应有 fig_*.pdf / tikz_*.pdf 残留
remaining_pdf=$(find figures/ \( -name 'fig_*.pdf' -o -name 'tikz_*.pdf' \) 2>/dev/null | wc -l)
[ "$remaining_pdf" -gt 0 ] && echo "❌ 还残留 $remaining_pdf 个 PDF，需删除"
# 2. 每个 PNG 不应过小
for png in figures/fig_*.png figures/tikz_*.png; do
    [ -f "$png" ] || continue
    sz=$(wc -c < "$png" 2>/dev/null || stat -c%s "$png" 2>/dev/null)
    if [ "$sz" -lt 30000 ]; then
        echo "⚠ $(basename $png) 仅 ${sz} 字节，可能模糊（应 ≥ 50KB），建议提高 DPI 重新生成"
    fi
done
```
**任何 ❌ 或 ⚠ 都必须修复**（重新生成或转换）。
**⛔ 转 PNG 后，确保 paper/main.md 用 `![](figures/tikz_xxx.png)` 引用了每张 TikZ 图（几何示意图、算法流程图），不能因为转了 PNG 却没在正文引用而丢图。**

<!-- /INJECT:COURSE_DOCX_PNG_ONLY -->

<!-- INJECT:COURSE_DOCX_TABLE_MD -->


## ⛔ 表格输出格式：仅 Markdown 三线表（.md）
本工作流最终导出 Word，**所有结果表格必须输出为 `.md`，不要再生成 `.tex`**：

**为什么这条铁律重要**：写作步骤会直接 `cat figures/TABLE_xxx.md >> paper/main.md`，完全跳过「从 JSON 抠数字到 Markdown 表格」这一步，从源头杜绝 AI 编造/记错表格数字。

**调用 stats_utils 时按 .md 后缀输出**：
```python
from _utils.stats_utils import regression_table, descriptive_table, correlation_table
# ⛔ Word 模式：表格全部输出 .md（Markdown 三线表）
regression_table(results, ['OLS', 'Logit'],
                 output='figures/TABLE_regression.md',
                 caption='回归结果')
descriptive_table(df, output='figures/TABLE_descriptive.md',
                  caption='描述性统计')
```

**手写表格时使用以下 Markdown 三线表标准格式**：
```markdown
**表 1：模型性能对比**

| 模型 | RMSE | MAE | R² |
|---|---|---|---|
| LSTM | 0.023 | 0.018 | 0.94 |
| Transformer | 0.019 | 0.015 | 0.96 |

> 注：所有指标基于测试集；最优值已加粗。

<!-- label: tab:model_perf -->
```

**表格生成铁律**：
- ⛔ **禁止**生成 `figures/TABLE_*.tex`（Word 模式根本不读 .tex 文件）
- ⛔ **禁止**写 `\begin{table}` / `\begin{tabular}` / `\toprule` / `\midrule` / `\bottomrule`
- ✅ 生成 `figures/TABLE_*.md`：每个表格一个文件，文件名见名知意（TABLE_regression.md / TABLE_descriptive.md / TABLE_model_perf.md...）
- ✅ 表格里的所有数值**必须**从 `figures/all_results.json` / `figures/*.json` / `RESULTS.md` 读取，禁止凭记忆填
- ✅ 表头单独一行 `| h1 | h2 |`，**接下来必须有分隔行** `|---|---|`
- ✅ 每行 `|` 数量必须一致（列数对齐）
- ✅ 单元格里的 `|` 必须转义为 `\|`
- ✅ 表注用 `> 注：xxx`（引用块）

**核查清单**（生成完所有表格后必须跑）：
```bash
echo '=== 表格格式核查 ==='
# 1. figures/ 不应有 TABLE_*.tex
tex_count=$(ls figures/TABLE_*.tex 2>/dev/null | wc -l)
[ "$tex_count" -gt 0 ] && echo "❌ 还残留 $tex_count 个 .tex 表格，必须删除并改用 .md"
# 2. .md 表格列数对齐 + 必有分隔行
for md in figures/TABLE_*.md; do
    [ -f "$md" ] || continue
    if ! grep -qE '^\|[\s\-:|]+\|\s*$' "$md"; then
        echo "❌ $(basename $md) 缺少分隔行 |---|---| ，Word 不会渲染成表格"
    fi
done
echo '=== 表格生成完成 ==='
ls -1 figures/TABLE_*.md 2>/dev/null
```
**任何 ❌ 都必须修复**（删除 .tex / 补全分隔行 / 重新生成）。

<!-- /INJECT:COURSE_DOCX_TABLE_MD -->

<!-- INJECT:PAPER_PLAN_BACKLINK -->


## ⛔ 撰写阶段强制规则（基于用户开关 + figures/ 实际产物）
**figures/ 中已有 14 张图，必须全部嵌入正文：**
- fig_arch_q1.png
- fig_arch_q3.png
- fig_eda_style_pca.png
- fig_q1_calibration.png
- fig_q1_missing_pattern.png
- fig_q1_pred_perf.png
- fig_q2_chem_sensory_corr.png
- fig_q2_coexpr_network.png
- fig_q2_stability.png
- fig_q2_top3_heatmap.png
- fig_q3_realvsgen.png
- fig_q3_style_radar.png
- fig_q3_transfer_defect.png
- fig_roadmap.png

**铁律：**
1. 建立 figure use plan，把每张图分配到建模/求解/结果/验证过程并全部嵌入
2. **必须用 `.png` 扩展名**（Word 模式只支持 PNG）；不要写 `.pdf` 路径
3. 引用语「如图 X-Y 所示」必须有对应的图片嵌入
4. 每张正文图都要有图前问题/判断和图后完整解释；禁止连续贴图；任何生成图未嵌入都阻断

<!-- /INJECT:PAPER_PLAN_BACKLINK -->

<!-- MH_MEMO:BEGIN -->
## ⛔ 本工作区的记忆（引擎自动维护，每步刷新）

### 已确认的决定（贯穿全程，不得推翻）
- **重修任务书执行方式（定稿v2 自包含）**：方案A：以 paper/main.md→Word导出docx 为唯一正式稿，main.tex/main.pdf 作历史副本不同步不重编，最终PDF由定稿docx另存。A→B→C→D 一次性全部做完再导出Word，不逐批停下等确认。全程SEED=42；防泄漏（标准化/KNN/未检出下限ℓ_k/指示变量入选/分箱切点只在训练折拟合）；风格标签不进Q1特征；Q1主模型保留全231特征；仅Q2归因候选集限（⛔ 用户已否决：方案B（main.md与main.tex两套同步、PDF重编）；逐批停下等用户确认后再进下一批，不要加回来）

### 已完成的工作（局部完成不等于整步完成）
- comp-code [局部完成：按拆开的来] → 已完成「改 problem1.py 补 Q1 指标 + params.py 加化合物集C，跑 problem1.py 重算」：修改源文件 code/params.py、code/problem1.py、figures/problem_1_results.json。只写入了这次说好的文件，写入前后都核对过；不满意可以撤销。
这次只做了说好的部分，已有成果都保留；整个步骤的完成状态不变。
- comp-code [局部完成：好的，继续q2吧] → 已完成「改 problem2.py 候选集限定化合物集C重算Q2全套，跑 problem2.py」：修改源文件 code/problem2.py、figures/problem_2_results.json、submission/q2_top3_compounds.csv。只写入了这次说好的文件，写入前后都核对过；不满意可以撤销。
这次只做了说好的部分，已有成果都保留；整个步骤的完成状态不变。

### ⛔ 已经踩过的坑（别重犯）
- comp-code 失败：聚焦任务没有产生任何实际产物变化
- comp-code 失败：MHcoding Key 所在账户额度不足：技能内容只在能正常调用模型时下发，这次没有领取

（另有 2 次失败运行，详见 `.mh/JOURNAL.md`）

### ⚠ 6 个产物的依赖已过期（用它们之前先确认要不要重跑）
- **comp-code** 的 3 个产物：上游变更（code/params.py）
- **comp-code** 的 3 个产物：上游变更（code/problem2.py）

完整历史 → `.mh/JOURNAL.md`；结构化状态 → `.mh/STATE.json`（要溯源某个数字来自哪次运行时读它）
<!-- MH_MEMO:END -->
