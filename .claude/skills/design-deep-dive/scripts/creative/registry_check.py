#!/usr/bin/env python3
"""H/03: проверка cliche-registry.yaml — обязательные поля и словари, кластеры, id; разрешение ссылок cliche:<id> в файлах базы.
python3 registry_check.py [--refs <папка> ...]   → печать; exit 0 — ок, 1 — ошибки."""
import sys, re, glob, os, yaml, collections
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('creative'))
REG = os.path.join(ROOT, '08-uniqueness-anti-slop/cliche-registry.yaml')
REQ = ['id', 'name_ru', 'family', 'sign', 'signals', 'detect', 'threshold', 'first_seen', 'saturated_since', 'status', 'severity',
       'risk', 'levels', 'justify_if', 'twists', 'replace_with', 'cluster', 'k3_allow', 'neighbors', 'evidence', 'checked_at', 'review_by']
ENUM = {'status': {'fresh', 'saturated', 'dated'}, 'severity': {'B', 'S', 'D'}, 'risk': {'high', 'mid', 'low'},
        'family': {'color', 'surface', 'background', '3d', 'type', 'chrome', 'layout', 'motion', 'interaction', 'product', 'imagery', 'meta'}}
K3 = {'warm', 'accent-word', 'serif', 'eyebrow', 'photo-hero', 'center-hero', 'stats', 'cards', 'gradient', 'glass', 'pill', 'dots', 'arrows', 'mono', 'numbered', 'marquee', 'chrome', 'caps', None}
d = yaml.safe_load(open(REG, encoding='utf-8'))
err = []
ids = [e.get('id') for e in d['entries']]
for i in set(ids):
    if ids.count(i) > 1: err.append(f'дубль id {i}')
codes = set(d['detect_codes'])
for e in d['entries']:
    for k in REQ:
        if k not in e: err.append(f"{e.get('id')}: нет поля {k}")
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', e.get('id', '')): err.append(f"{e.get('id')}: id не kebab-case")
    for k, allowed in ENUM.items():
        if e.get(k) not in allowed: err.append(f"{e['id']}: {k}={e.get(k)}")
    if e.get('k3_allow') not in K3: err.append(f"{e['id']}: k3_allow={e.get('k3_allow')} нет в ALLOW_KEYS k3_checks")
    for m in (e.get('detect') or {}).get('method', []):
        if m not in codes: err.append(f"{e['id']}: код обнаружения {m} не в detect_codes")
    for L in ('L0', 'L1', 'L2'):
        if L not in (e.get('levels') or {}): err.append(f"{e['id']}: levels без {L}")
    for f in ('checked_at', 'review_by'):
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(e.get(f))): err.append(f"{e['id']}: {f} не дата")
cl = {c['id'] for c in d['clusters']}
for e in d['entries']:
    for c in e.get('cluster') or []:
        if c not in cl: err.append(f"{e['id']}: кластер {c} не объявлен")
for c in d['clusters']:
    for m in c['members']:
        if m not in ids: err.append(f"кластер {c['id']}: нет записи {m}")
        elif c['id'] not in (next(e for e in d['entries'] if e['id'] == m).get('cluster') or []): err.append(f"кластер {c['id']}: у {m} нет его в поле cluster")
mem = {c['id']: set(c['members']) for c in d['clusters']}
for e in d['entries']:
    for c in e.get('cluster') or []:
        if c in mem and e['id'] not in mem[c]: err.append(f"{e['id']}: указан кластер {c}, но не в его members")
alias = d.get('id_aliases') or {}
for a, t in alias.items():
    if t not in ids: err.append(f'id_aliases: {a} → {t} нет записи')
known = set(ids) | set(alias)
refs = collections.Counter(); unresolved = collections.Counter()
dirs = sys.argv[sys.argv.index('--refs') + 1:] if '--refs' in sys.argv else [os.path.join(ROOT, '01-creative-direction'), os.path.join(ROOT, '08-uniqueness-anti-slop')]
for dd in dirs:
    for f in glob.glob(os.path.join(dd, '**/*'), recursive=True):
        if not os.path.isfile(f) or not f.endswith(('.json', '.yaml', '.yml', '.md')): continue
        for m in re.finditer(r'cliche:([a-z0-9]+(?:-[a-z0-9]+)*)', open(f, encoding='utf-8', errors='replace').read()):
            refs[m.group(1)] += 1
            if m.group(1) not in known: unresolved[(os.path.relpath(f, ROOT), m.group(1))] += 1
print('записей', len(ids), '| статусы', dict(collections.Counter(e['status'] for e in d['entries'])), '| серьёзность', dict(collections.Counter(e['severity'] for e in d['entries'])), '| риск', dict(collections.Counter(e['risk'] for e in d['entries'])))
print('семейства', dict(collections.Counter(e['family'] for e in d['entries'])))
print('ссылок cliche:', sum(refs.values()), '| неразрешённых', sum(unresolved.values()))
for (f, i), n in unresolved.items(): print('  нет в реестре:', i, '←', f)
for x in err: print('ОШИБКА', x)
sys.exit(1 if err or unresolved else 0)
