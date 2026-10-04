import json, sys

def walk(n, depth=0):
    a = n.get('attributes') or {}
    rid = a.get('resource-id', '')
    if rid.startswith('com.android.systemui') or 'navigationBar' in rid:
        return
    print('{}{}|id={}|acc={}|text={}|click={}|checked={}|selected={}'.format(
        '  ' * depth,
        a.get('class', '?').split('.')[-1],
        rid, a.get('accessibilityText', ''), a.get('text', ''),
        a.get('clickable'), a.get('checked'), a.get('selected')))
    for c in (n.get('children') or []):
        walk(c, depth + 1)

walk(json.load(open(sys.argv[1])))