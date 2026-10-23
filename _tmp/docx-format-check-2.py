import re, sys
text = open(sys.argv[1], encoding='utf-8', errors='ignore').read().replace('\r\n', '\n')
m = re.search(r'\n##\s*(附录|参考文献|Appendix|References)', text)
body = text[:m.start()] if m else text
# 中文"图/表 N…"起句，或英文"Figure/Fig./Table/Tab. N…"起句
open_re = re.compile(r'^(图|表)\s*\d|^(Figure|Fig\.?|Table|Tab\.?)\s*\d', re.IGNORECASE)
# 英文带出式
leadin_re = re.compile(r'^(as\s|in\s|from\s|observing\b|see\b|per\b|following\b|according)', re.IGNORECASE)
def is_prose(p):
    s = p.strip()
    if len(s) < 15 or s[0] in '#>|`!*-\\%{}$&': return False
    if re.match(r'^\d+\.', s): return False
    return True
def is_opener(p):
    s = p.strip()
    return bool(open_re.match(s)) and not bool(leadin_re.match(s))
sections = re.split(r'(?m)^##\s', body)
adj, heavy = 0, []
tot_open, tot_ref = 0, 0
for sec in sections:
    proses = [p for p in re.split(r'\n\s*\n', sec) if is_prose(p)]
    flags = [is_opener(p) for p in proses]
    adj += sum(1 for i in range(len(flags)-1) if flags[i] and flags[i+1])
    if sum(flags) >= 3: heavy.append(sum(flags))
    tot_open += sum(flags)
    tot_ref += sum(1 for p in proses if re.search(r'(图|表)\s*\d|(Figure|Fig\.?|Table|Tab\.?)\s*\d', p, re.I))
ratio = (tot_open / tot_ref) if tot_ref else 0
pervasive = tot_ref >= 5 and ratio > 0.35
if adj or heavy or pervasive:
    if adj:   print(f"  X {adj} 处相邻段落都以「图 N…/表 N…」起句")
    if heavy: print(f"  X {len(heavy)} 个章节图号起句段 >=3（{heavy}）")
    if pervasive: print(f"  X 全文 {tot_open}/{tot_ref} 段以「图N/表N」起句（{ratio:.0%}>35%）")
    print("  修复：把点名的段落改成括号旁注/动词引导/后置印证，「图作主语」整节最多一次")
    sys.exit(3)
print("  ✅ 图号引用句式无套路化")
