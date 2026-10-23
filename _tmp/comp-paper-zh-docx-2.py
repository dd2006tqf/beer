import re, sys
try:
    t = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
except FileNotFoundError:
    sys.exit(0)
imgs = list(re.finditer(r'!\[[^\]]*\]\([^)]*\)', t))
bad = 0
for i in range(len(imgs) - 1):
    gap = t[imgs[i].end():imgs[i+1].start()]
    body = re.sub(r'\s+', '', gap)
    if len(body) < 80:
        bad += 1
if bad:
    print("  X paper/main.md: 有 %d 处图间正文过少（<80字）" % bad)
