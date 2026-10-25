# -*- coding: utf-8 -*-
"""从 pagemap.tsv 提取各标题的正文页码，生成 _tmp/toc_entries.json。
正文从第 1 页重新编号，故这里取的 disp（显示页码）就是目录要印的页码。
"""
import io, json, os, re, sys

ROOT = r"E:\华数数据\workspaces\b6875cacdc9d"

# 1) main.md 里的标题（## 一级、### 二级），摘要不算目录项
heads = []
for ln in io.open(os.path.join(ROOT, "paper", "main.md"), encoding="utf-8"):
    s = ln.rstrip("\n")
    if s.startswith("### "):
        heads.append((2, s[4:].strip()))
    elif s.startswith("## "):
        t = s[3:].strip()
        if t == "摘要":
            continue
        heads.append((1, t))

# 2) pagemap：段落 -> 显示页码
rows = []
for ln in io.open(os.path.join(ROOT, "_tmp", "pagemap.tsv"), encoding="utf-8-sig"):
    p = ln.rstrip("\n").split("\t")
    if len(p) >= 5 and p[0].isdigit():
        rows.append((int(p[0]), p[1], p[4].strip()))

# 正文段范围：从「1 问题重述」到「附录 C 核心源程序」标题段
start = next(i for i, r in enumerate(rows) if r[2].startswith(heads[0][1]))
body = [r for r in rows if r[0] >= rows[start][0]]

entries = []
cur = 0
for lvl, txt in heads:
    hit = None
    for j in range(cur, len(body)):
        if body[j][2] == txt:
            hit = j
            break
    if hit is None:
        print("MISS:", lvl, txt)
        continue
    entries.append({"level": lvl, "text": txt, "page": int(body[hit][1])})
    cur = hit + 1

print("entries:", len(entries), "of", len(heads))
out = os.path.join(ROOT, "_tmp", "toc_entries.json")
json.dump(entries, io.open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for e in entries[:8]:
    print(e)
print("...")
for e in entries[-4:]:
    print(e)
