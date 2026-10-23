import re, sys
LIMIT = 20
try:
    text = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
except FileNotFoundError:
    sys.exit(0)
m = re.search(r'(?m)^##\s*(附录|参考文献|Appendix|References)', text)
body_text = text[:m.start()] if m else text
bad = []
for alt in re.findall(r'!\[([^\]]*)\]\([^)]*\)', body_text):
    body = re.sub(r'^\s*[图表]\s*\d+\s*[:：.、]?\s*', '', alt)
    cn = re.findall(r'[一-鿿]', body)
    if len(cn) > LIMIT:
        bad.append((len(cn), ''.join(cn)[:30]))
if bad:
    for n, preview in bad:
        print(f"  X 图注主体 {n} 字(>{LIMIT}): {preview}...")
    sys.exit(3)
print("  OK: 图注长度合规")
