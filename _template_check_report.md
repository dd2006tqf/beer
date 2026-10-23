# DOCX 模板占位映射报告

**模板**：`user_template/2026年MathorCup数学应用挑战赛—大数据竞赛论文模板.docx`
**源 markdown**：`paper/main.md`
**自检轮数**：1 / 3（含公式修复后重试）
**最终状态**：✅ 通过

## 额外修复：paper/main.md 公式

试填第一轮因 paper/main.md 第 326、329 行含 `\*`（非标准 LaTeX 命令）导致 Node 引擎报错。已将两处 `\tau^{\*}_k` 改为 `\tau^{*}_k`，重试后填充成功。

## anchor 映射

| 区域 | idx | 命中段文本 |
|------|-----|------------|
| 标题 | 3 | 论文题目 |
| 摘要 | 4 | 摘 要 |
| 正文起点 | 36 | （这里开始论文正文） |
| 参考文献 | null | 无独立锚点，safety-net 追加到正文尾 |
| 附录 | null | 无独立锚点，safety-net 追加到正文尾 |
| 英文摘要 | null | 无（竞赛模板，仅中文摘要） |

## 删除段（共 1 个）

- 说明性占位文字：[5]（"（摘要正文）"）

## 自检结果

- ✅ 占位符全部替换（"论文题目"、"（摘要正文）"、"（这里开始论文正文）"均已清除）
- ✅ 模板示例残留清除（无示例论文内容）
- ✅ 格式说明清除（无格式说明段）
- ✅ 应有正文章节齐全（除摘要节名外全部章节命中；摘要内容已正确插入"摘 要"标题之后）
- ✅ 封面表格保留（队伍编号 / 赛道信息表原样保留，待作者手填）

## 填充 log 摘要

```
Title replaced via template_map: '面向啤酒酿造化合物的感官分级预测、关键化合物归因与风格条件生成'
Abstract (5 paras) + keywords inserted
Body (161 elements) inserted (anchor_mode=delete)
WARNING: Safety-net: appended references (14 elems) at body tail
WARNING: Safety-net: appended appendix (1716 elems) at body tail
```

references 和 appendix 的 safety-net 警告属于正常行为：竞赛模板无独立参考文献/附录锚点，内容追加到正文尾，结构正确。

## 留给作者填写的项

本模板为竞赛模板，无中图分类号、文献标识码等学术期刊字段。以下项目原样保留，需作者手动填入最终提交文档：

- **队伍编号**：封面表格第一行右侧单元格（当前为 `MCB260XXXX`，应改为 `MCB2600304`）
- **赛道**：封面表格第二行右侧单元格（当前为 `（A/B）`，应改为 `A`）

## 仍需人工处理

- 封面表格中的队伍编号和赛道需手动修改（见上）
- 目录需在 Word 中右键更新字段以生成正确页码
