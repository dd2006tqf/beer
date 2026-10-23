import json, os, glob
def summarize(v, depth=0):
    if isinstance(v, list):
        n=len(v); nums=[x for x in v if isinstance(x,(int,float))]
        if nums: return f'list[{n}] range=[{min(nums):.4g},{max(nums):.4g}] sample={v[:3]}'
        if v and isinstance(v[0], (list,dict)): return f'list[{n}] of {type(v[0]).__name__}, first_shape={len(v[0]) if hasattr(v[0],"__len__") else "?"}'
        return f'list[{n}] sample={str(v[:3])[:80]}'
    if isinstance(v, dict) and depth<3:
        return 'dict{'+', '.join(f'{k}: {summarize(x,depth+1)}' for k,x in list(v.items())[:40])+'}'
    return f'{type(v).__name__}={str(v)[:80]}'
for f in sorted(glob.glob('figures/*_results.json')):
    sz=os.path.getsize(f); d=json.load(open(f,encoding='utf-8'))
    print(f'\n=== {os.path.basename(f)} ({sz//1024}KB) ===')
    if isinstance(d, dict):
        for k,v in d.items(): print(f'  {k}: {summarize(v)}')
    else: print(f'  {summarize(d)}')
