import re, sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):
    pass
content = open(sys.argv[1], encoding="utf-8").read()
# 过滤代码块（避免误报）。换成等量空行以保住行号
content_no_code = re.sub(r'```.*?```',
                         lambda m: "\n" * m.group(0).count("\n"),
                         content, flags=re.DOTALL)

TAIL_NUM = re.compile(r'[(（]\s*([^)）]{1,24}?)\s*[)）]|^([0-9][0-9A-Za-z.\-\u2019\']*)$')

CONT_START = re.compile(
    r'^\s*(?:[=+\-<>]|\\(?:leq|geq|le|ge|neq|approx|equiv|sim|simeq|cong'
    r'|propto|ll|gg|subset|supset|subseteq|supseteq|in|to|rightarrow'
    r'|Rightarrow|leftrightarrow|Leftrightarrow|quad|qquad|times|cdot'
    r'|pm|mp|div)\b)')

_ONLY_NUM_LINE = re.compile(r'^\s*[-*]?\s*[（(][0-9A-Za-z.\-\u2019\']+[)）]\s*$')

def is_continuation(body, start_line, prev_end_line, all_lines):
    if prev_end_line is None:
        return False
    if not CONT_START.match(body.strip()):
        return False
    for ln in range(prev_end_line + 1, start_line):
        if ln - 1 >= len(all_lines):
            break
        s = all_lines[ln - 1].strip()
        if s and not _ONLY_NUM_LINE.match(s):
            return False
    return True

tagged, outside, no_label, cont = [], [], [], []
_prev_end = None

def tail_label(tail):
    t = tail.strip()
    if not t:
        return None
    m = TAIL_NUM.search(t)
    if m:
        return (m.group(1) or m.group(2) or t).strip()
    return t

def record(kind, line, body, label=None):
    kind.append((line, body.strip()[:60], label))

blocks = []

for m in re.finditer(r'^[ \t]*\$\$[ \t]*$([\s\S]*?)^[ \t]*\$\$([^\n]*)$',
                     content_no_code, re.MULTILINE):
    s_ln = content_no_code[:m.start()].count('\n') + 1
    e_ln = content_no_code[:m.end()].count('\n') + 1
    blocks.append((s_ln, e_ln, m.group(1), m.group(2)))

covered = set()
for s_ln, e_ln, _, _ in blocks:
    covered.update(range(s_ln, e_ln + 1))

for m in re.finditer(r'^[ \t]*\$\$(.+?)\$\$([^\n]*)$',
                     content_no_code, re.MULTILINE):
    s_ln = content_no_code[:m.start()].count('\n') + 1
    if s_ln in covered:
        continue
    blocks.append((s_ln, s_ln, m.group(1), m.group(2)))

blocks.sort(key=lambda b: b[0])
_all_lines = content_no_code.split("\n")

for s_ln, e_ln, body, tail in blocks:
    itag = re.search(r'\\tag\{([^}]+)\}', body)
    lab = tail_label(tail)
    if itag:
        record(tagged, s_ln, body, itag.group(1))
        if lab:
            record(outside, s_ln, body, lab)
    elif lab:
        record(outside, s_ln, body, lab)
    elif is_continuation(body, s_ln, _prev_end, _all_lines):
        record(cont, s_ln, body)
    else:
        record(no_label, s_ln, body)
    _prev_end = e_ln

print("✅ 已用 \\tag{} 的公式 (%d)：%s"
      % (len(tagged), [l for _, _, l in tagged]))
print("⛔ 块外编号 %d 处（必改成 \\tag{}）：" % len(outside))
for line, sn, lab in outside[:15]:
    print("   L%d  编号 %s   %s..." % (line, lab, sn))
print("⛔ 完全未编号 %d 处（补 \\tag{n}）：" % len(no_label))
for line, sn, _ in no_label[:15]:
    print("   L%d  %s..." % (line, sn))
if cont:
    print("ℹ 续行块 %d 处（不要给它们补编号）：" % len(cont))
    for line, sn, _ in cont[:10]:
        print("   L%d  %s..." % (line, sn))
sys.exit(1 if (outside or no_label) else 0)
