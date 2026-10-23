import json
m = json.load(open('_template_map.json', encoding='utf-8'))
del_set = set(m.get('delete_paragraph_indices') or [])
anchors = {k: m.get(k) for k in [
    'title_anchor_para_idx', 'abstract_anchor_para_idx', 'en_abstract_anchor_para_idx',
    'body_anchor_para_idx', 'references_anchor_para_idx',
    'appendix_anchor_para_idx',
]}
for k, v in anchors.items():
    if v is not None and v in del_set:
        print(f"❌ {k}={v} 在 delete_paragraph_indices 里 — 必须移除")
        import sys; sys.exit(1)
keep = set(m.get('keep_for_user_paragraph_indices') or [])
if keep & del_set:
    print(f"❌ 留给作者填的段 {sorted(keep & del_set)} 在 delete_paragraph_indices 里 — 必须移除")
    import sys; sys.exit(1)
print("OK: anchors、留给作者填的段与 delete_paragraph_indices 无冲突")
