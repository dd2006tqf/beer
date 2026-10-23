# -*- coding: utf-8 -*-
"""Comprehensive format check for paper/main.md"""
import re
import sys
import os

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

TARGET = "paper/main.md"
content = open(TARGET, encoding="utf-8").read()
lines = content.split("\n")

issues = []
fixes = []

# =========================================================
# Check B: Code block balance
# =========================================================
triple_bt = [i+1 for i, ln in enumerate(lines) if ln.startswith("```")]
print(f"=== Check B: Code block markers ===")
print(f"  Count of ``` markers: {len(triple_bt)}")
if len(triple_bt) % 2 != 0:
    print(f"  ❌ Unbalanced! Line numbers: {triple_bt}")
    issues.append(("B", "Code block markers unbalanced"))
else:
    print(f"  ✅ Balanced")

# =========================================================
# Check A0: list items that should be headings
# =========================================================
print("\n=== Check A0: Fake headings / captions as list items ===")
fake_heading_re = re.compile(
    r'^- (第[一二三四五六七八九十百千零〇0-9]+[章节部篇]|'
    r'[一二三四五六七八九十]+、|'
    r'（[一二三四五六七八九十]+）|'
    r'[0-9]+(\.[0-9]+){0,4}\.?\s|'
    r'摘要|Abstract|关键词|Keywords|参考文献|References|致谢|附录|Appendix)'
)
fake_caption_re = re.compile(
    r'^- (图|表|Figure|Fig\.?|Table|Tab\.?)\s*[0-9A-Za-z][0-9A-Za-z\-\.]*\s*[：:、\.\-]'
)
fake_eq_re = re.compile(r'^- *[\[\(【] *[0-9]+(\.[0-9]+)? *[\]\)】] *$')

a0_found = []
for i, ln in enumerate(lines):
    if fake_heading_re.match(ln) or fake_caption_re.match(ln) or fake_eq_re.match(ln):
        a0_found.append((i+1, ln[:80]))
        issues.append(("A0", f"L{i+1}: {ln[:60]}"))

if a0_found:
    print(f"  ❌ Found {len(a0_found)} fake list items:")
    for ln_no, text in a0_found:
        print(f"    L{ln_no}: {text}")
else:
    print("  ✅ No fake list-item headings/captions")

# =========================================================
# Check D: Block formula with trailing content
# =========================================================
print("\n=== Check D: Block formulas with trailing content ===")
# Find $$ that close with trailing content
trailing_close_re = re.compile(r'^\s*\$\$\s*\S')
# Single-line $$...$$ with trailing
single_line_re = re.compile(r'\$\$.+\$\$\s*\S')
# Standalone equation numbers on their own line
standalone_eq_re = re.compile(r'^\s*[-*]?\s*[（(][0-9A-Za-z.\-′\'-]+[)）]\s*$')

d_found = []
for i, ln in enumerate(lines):
    # Check: closing $$ with trailing content
    if trailing_close_re.match(ln):
        # but not an opening $$ (which would be $$latex_content)
        stripped = ln.strip()
        if stripped.startswith('$$') and len(stripped) > 2:
            after = stripped[2:].strip()
            # If it's a pure opening line (content after $$), not a close
            # Check context: if there was an unclosed $$ before
            d_found.append(("trailing_after_$$", i+1, ln[:80]))
    if standalone_eq_re.match(ln):
        # Check if previous non-empty line ends with $$
        for j in range(i-1, max(i-5, -1), -1):
            if lines[j].strip():
                if lines[j].strip() == '$$':
                    d_found.append(("standalone_eq_num", i+1, ln[:80]))
                break

if d_found:
    for dtype, ln_no, text in d_found:
        print(f"  ⚠ {dtype} at L{ln_no}: {text}")
    # May be noisy - need to check manually
else:
    print("  ✅ No obvious trailing-content formula issues found")

# Check for \tag{} usage
tagged = [(i+1, ln.strip()[:60]) for i, ln in enumerate(lines) if r'\tag{' in ln]
print(f"\n  \\tag{{}} usage: {len(tagged)} lines")
for ln_no, text in tagged[:10]:
    print(f"    L{ln_no}: {text}")

# =========================================================
# Check E: Inline $$
# =========================================================
print("\n=== Check E: Inline double-dollar signs ===")
e_found = []
for i, ln in enumerate(lines):
    if re.search(r'\$\$.+\$\$', ln) and not ln.strip().startswith('$$'):
        e_found.append((i+1, ln[:80]))
        issues.append(("E", f"L{i+1}: inline $$ found"))

if e_found:
    print(f"  ❌ {len(e_found)} lines with inline $$:")
    for ln_no, text in e_found:
        print(f"    L{ln_no}: {text}")
else:
    print("  ✅ No inline $$ found")

# =========================================================
# Check F: Tables
# =========================================================
print("\n=== Check F: Table format ===")
in_table = False
table_start = -1
col_counts = []
has_sep = False
table_issues = []

for i, ln in enumerate(lines):
    stripped = ln.strip()
    if re.match(r'^\|.*\|', stripped):
        if not in_table:
            in_table = True
            table_start = i + 1
            col_counts = []
            has_sep = False
        cells = stripped.split('|')
        col_count = len([c for c in cells if c.strip() or True]) - 2  # remove empty first/last
        col_counts.append(col_count)
        if re.match(r'^\|[\s\-:|]+\|', stripped):
            has_sep = True
    else:
        if in_table:
            if not has_sep:
                table_issues.append(f"L{table_start}: table missing separator row")
                issues.append(("F", f"Table at L{table_start} missing separator row"))
            in_table = False
            col_counts = []
            has_sep = False

if table_issues:
    for ti in table_issues:
        print(f"  ❌ {ti}")
else:
    # Count tables
    table_count = len(re.findall(r'(?m)^\|[\s\-:|]+\|', content))
    print(f"  ✅ Found {table_count} table separators - all tables appear well-formed")

# =========================================================
# Check H: Image references
# =========================================================
print("\n=== Check H: Image references ===")
img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
missing_imgs = []
for alt, path in img_refs:
    if not os.path.exists(path):
        missing_imgs.append((alt[:30], path))
        issues.append(("H", f"Missing image: {path}"))

print(f"  Total image refs: {len(img_refs)}")
if missing_imgs:
    print(f"  ❌ {len(missing_imgs)} missing images:")
    for alt, path in missing_imgs:
        print(f"    [{alt}]({path})")
else:
    print("  ✅ All image files exist")

# Check for PDF/SVG refs
pdf_refs = [(alt, path) for alt, path in img_refs if path.endswith('.pdf') or path.endswith('.svg')]
if pdf_refs:
    print(f"  ❌ {len(pdf_refs)} PDF/SVG image refs (not supported in docx):")
    for alt, path in pdf_refs:
        print(f"    [{alt}]({path})")
    issues.append(("H", f"{len(pdf_refs)} PDF/SVG refs found"))
else:
    print("  ✅ No PDF/SVG image refs")

# =========================================================
# Check I: Escape characters
# =========================================================
print("\n=== Check I: Escape characters ===")
double_bs = [(i+1, ln[:80]) for i, ln in enumerate(lines)
             if '\\\\' in ln and not ln.strip().startswith('```')]
# Filter to non-code-block lines
in_code = False
real_double_bs = []
for i, ln in enumerate(lines):
    if ln.startswith('```'):
        in_code = not in_code
    if not in_code and '\\\\' in ln:
        real_double_bs.append((i+1, ln[:80]))

if real_double_bs:
    print(f"  ⚠ {len(real_double_bs)} lines with double backslash (possible LaTeX line-end):")
    for ln_no, text in real_double_bs[:5]:
        print(f"    L{ln_no}: {text}")
else:
    print("  ✅ No unexpected double backslashes")

# =========================================================
# Check J: HTML tags
# =========================================================
print("\n=== Check J: HTML tags ===")
html_tags = re.findall(r'<(div|span|p|h[1-6]|table|tr|td|thead|tbody)[^>]*>', content, re.IGNORECASE)
if html_tags:
    print(f"  ❌ Found {len(html_tags)} unsupported HTML tags: {set(html_tags)}")
    issues.append(("J", f"Unsupported HTML tags: {set(html_tags)}"))
else:
    print("  ✅ No unsupported HTML tags")

# =========================================================
# Check K: Bold overuse
# =========================================================
print("\n=== Check K: Bold overuse ===")
bold_full_lines = sum(1 for ln in lines if re.match(r'^\*\*[^*]+\*\*$', ln.strip()))
print(f"  Lines that are entirely bold: {bold_full_lines}")
if bold_full_lines > 20:
    print(f"  ⚠ High bold usage ({bold_full_lines} lines)")
else:
    print(f"  ✅ Bold usage acceptable")

# =========================================================
# Summary
# =========================================================
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
if not issues:
    print("✅ All checks passed - no issues found")
else:
    print(f"Issues found ({len(issues)}):")
    for cat, msg in issues:
        print(f"  [{cat}] {msg}")

print(f"\nTotal paper length: {len(lines)} lines")
print(f"Image refs: {len(img_refs)}")
sep_count = len(re.findall(r'(?m)^\|[\s\-:|]+\|', content))
print(f"Tables: {sep_count}")
