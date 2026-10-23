import re, sys
try:
    text = open(sys.argv[1], encoding='utf-8', errors='ignore').read().replace('\r\n', '\n')
except FileNotFoundError:
    sys.exit(0)
m = re.search(r'\n##\s*(附录|参考文献|Appendix|References)', text)
body = text[:m.start()] if m else text
open_re = re.compile(r'^(图|表)\s*\d')
def is_prose(p):
    s = p.strip()
    if len(s) < 15:
        return False
    if s[0] in '#>|`!*-\\%{}$&':
        return False
    if re.match(r'^\d+\.', s):
        return False
    return True
sections = re.split(r'(?m)^##\s', body)
adj_pairs = 0
heavy_secs = []
for sec in sections:
    flags = [bool(open_re.match(p.strip())) for p in re.split(r'\n\s*\n', sec) if is_prose(p)]
    adj_pairs += sum(1 for i in range(len(flags) - 1) if flags[i] and flags[i + 1])
    n_open = sum(flags)
    if n_open >= 3:
        heavy_secs.append(n_open)
bad = adj_pairs > 0 or bool(heavy_secs)
if bad:
    if adj_pairs:
        print(f"  X {adj_pairs} 处相邻段落都以图号起句")
    if heavy_secs:
        print(f"  X {len(heavy_secs)} 个章节图号起句段 >=3（{heavy_secs}）")
    sys.exit(3)
print("  OK: 图号引用句式无套路化")
