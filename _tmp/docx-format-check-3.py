import re, sys
t = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
m = re.search(r'\n##\s*(附录|参考文献|Appendix|References)', t)
body = t[:m.start()] if m else t
imgs = list(re.finditer(r'!\[[^\]]*\]\([^)]*\)', body))
bad = []
for i in range(len(imgs) - 1):
    gap = body[imgs[i].end():imgs[i+1].start()]
    prose = re.sub(r'(?m)^#{1,6}\s.*$', '', gap)
    prose = re.sub(r'\s+', '', prose)
    if len(prose) < 80:
        alt = re.match(r'!\[([^\]]*)\]', imgs[i].group(0))
        tag = (alt.group(1)[:20] if alt else '?')
        bad.append(tag)
if bad:
    print(f"  X {len(bad)} 处两图之间正文不足 80 字（图叠图）：{bad}")
    print("  修复：在这两张图之间补一段充分正文")
    sys.exit(3)
print("  ✅ 无两图连排")
