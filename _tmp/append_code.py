import io
order = ['main.py','params.py','utils.py','data_check.py','problem1.py',
         'problem2.py','problem3.py','constraint_audit.py','sanity_check.py']
md = open('paper/main.md', encoding='utf-8').read()
parts = []
for fn in order:
    path = 'code/' + fn
    try:
        src = open(path, encoding='utf-8').read()
    except Exception as e:
        print('skip', fn, e); continue
    src = src.replace('\r\n', '\n').rstrip('\n')
    # guard: if source contains a fenced ``` it would break; code shouldn't, but check
    if '```' in src:
        print('WARN triple-backtick in', fn)
    parts.append('**code/%s**\n\n```python\n%s\n```\n' % (fn, src))
block = '\n'.join(parts)
md = md.replace('<!-- CODE_APPEND -->', block)
open('paper/main.md', 'w', encoding='utf-8').write(md)
print('appended', len(order), 'files; main.md now', len(md), 'chars')
