# HTML 流程/架构图产出报告（paper-figure-html）

**引擎**：HTML+CSS → Electron printToPDF（矢量）→ 350 DPI PNG（Word 模式，不能嵌 PDF）
**风格族**：C 纯黑白线稿（mono，STYLE_FAMILY=2），衬线印刷体、纯白底、直角细黑边、零彩色
**图内文字语言**：中文（与论文一致）

## 产出清单（对账 FIGURE_MANIFEST «HTML 流程/架构图» 段，3/3 全产出）

| 图名 | 文件 | 内容 | 章节 |
|---|---|---|---|
| fig_roadmap | figures/fig_roadmap.png | 整体技术路线图：数据基础→问题一化学→感官预测→问题二可解释归因→问题三风格生成迁移→综合输出，含跨问依赖标注 | 问题重述末尾 |
| fig_arch_q1 | figures/fig_arch_q1.png | 问题一感官评分 pipeline：缺失感知梯度提升→多输出有序回归→0-6 分箱映射→分层五折交叉验证，含防泄漏侧栏与基线对比 | 问题一模型 |
| fig_arch_q3 | figures/fig_arch_q3.png | 问题三 CVAE 风格条件生成：编码器→隐空间→条件解码器→缺陷阈值投影→生成谱，含训练目标、跨风格迁移、感官画像下游应用 | 问题三模型 |

## 质检结果（每张三道确定性闸 + 视觉自检）

| 图 | html_pdf_check（单页/矢量） | 几何自检（溢出/越界/重叠/对齐） | 规范自检（字号/占页/内容/对比度） | 视觉自检 |
|---|---|---|---|---|
| fig_roadmap | 单页 ✓ | PASS | PASS（548×519px，最小字 8.7pt，占页 54%） | PASS |
| fig_arch_q1 | 单页 ✓ | PASS | PASS（526×424px，最小字 9.0pt，占页 46%） | PASS |
| fig_arch_q3 | 单页 ✓ | PASS | PASS（540×465px，最小字 8.8pt，占页 49%） | PASS |

视觉自检（vision_ledger，kind=drawio）：3 张全通过，逐条核对连线均「接好」。

## 说明

- TikZ 几何图：无（本题为数据/ML 题，FIGURE_MANIFEST 明确「无几何构造图」）。
- 公式处理：架构图中的符号（如 ŷᵢⱼ、R²、Δ=μₜ−μₛ、q(z｜x,s)）用 Unicode 直接书写，不走 KaTeX，保证出图稳定单页。
- 产物均已转 350 DPI PNG（≥230KB）并删除中间 PDF，符合 Word 导出要求。
- latex_includes.tex 已追加三张图的引用与图注（引用 .png）。
- 所有节点文字均为本题真实方法/对象/判据，无占位、无结果数值、无工程语汇/元内容。
