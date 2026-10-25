# 本地集成说明（本仓库特有，非上游文件）

本目录是 [hrdZhu/modelviz-skill](https://github.com/hrdZhu/modelviz-skill) 的项目级副本，
迁入本论文仓库，供 Claude Code 通过 `Skill` 工具调用。

- **上游提交**：`cd9eac0`（main，2026-07-19，"Swap README preview image order"）
- **落位**：`<repo>/.claude/skills/modelviz-skill/`，项目级 Skill，随仓库提交
- **查看方式**：Claude Code 新开会话后 `Skill` 列表里出现 `modelviz-skill`（当前会话不刷新）

## 相对上游做过的改动

| 改动 | 原因 |
|---|---|
| 删除 89 个 `templates/*/*/output/preview.png` | 与同目录 `assets/preview.png` 逐字节相同（已 md5 校验），纯副本，109.6 MB |
| 89 张 `assets/preview.png` 长边压到 1600px | 原图最大 14830×7107、单张 10.9 MB，选模板只需分辨版式；109.6 MB → 39.1 MB |
| 删除根目录 `1.jpg`/`2.jpg`/`3.jpg` | 与 `docs/assets/readme-preview-*.jpg` 逐字节相同 |
| `README.md` 内 16 处 `output/preview.png` → `assets/preview.png` | 上一条删除后的链接修复 |
| 新增本文件 | 记录迁移与裁剪 |

`SKILL.md`、`src/`、`docs/`、`schemas/`、`templates/**/*.py` 与 `templates/**/data/` **未改动**。

## 运行约定

工作目录必须是本目录（所有工具用 `docs/template_catalog.yaml`、`workspace/`、`outputs/` 这类相对路径）：

```powershell
cd .claude\skills\modelviz-skill
.venv\Scripts\python.exe -c "import sys; sys.path.insert(0,'.'); from src.tools import load_template_catalog; print(load_template_catalog.invoke({'catalog_path':'docs/template_catalog.yaml'})['total_templates'])"
```

依赖已装在 `.venv/`（`--system-site-packages`，继承系统 python 的 numpy/pandas/matplotlib/scipy/seaborn）。
`.venv/` 不入库，别的机器 clone 后按下节重建。

```powershell
python -m venv --system-site-packages .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 与主流水线的边界

- `templates/` 只读；改写产物落 `workspace/adapted_plot.py`，图落 `outputs/`。
- ModelViz 出的图不直接进论文：需另存到仓库根 `figures/fig_xxx.png`（350 DPI）并在 `paper/main.md` 引用，
  否则违反本仓库「PNG 350 DPI + `figures/` 统一目录」的约定。
- `workspace/`、`outputs/` 的运行产物不入库（上游 `.gitignore` 已处理）。

## 已知问题

上游自带测试 `tests/test_readme_release.py` 有 2 条失败（`test_readme_exists_and_matches_skill_project_positioning`、
`test_readme_referenced_project_paths_exist`），**迁移前在原始 clone 上同样失败**——测试期望的 README 文案
（"面向数学建模竞赛和科研报告的科学可视化 Skill"）和 `docs/package_name_mapping.yaml` 字样在上游 README 中本就不存在。
其余 69 条通过。不改上游测试，也不为过测试去编 README。
