#!/usr/bin/env python3
"""Проверка 07-stack-implementation/stack.yaml: YAML, обязательные поля, уникальность id, effect-id по treatment.v0, ссылки alternatives."""
import json, sys, yaml, datetime
import os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib')); import kbpaths  # перенос: scripts/lib
ROOT = str(kbpaths.kb('creative')) + '/'
d = yaml.safe_load(open(ROOT + '07-stack-implementation/stack.yaml'))
eff = set(json.load(open(ROOT + '01-creative-direction/drafts-for-site/treatment.v0.schema.json'))['x-effect-ids-v0'])
REQ = ['id', 'name', 'kind', 'version', 'license', 'size_br', 'init_tbt_ms', 'levels', 'status', 'alternatives', 'risks', 'alive', 'refs']
errs = []
ids = [e['id'] for e in d['entries']]
if len(ids) != len(set(ids)): errs.append('дубли id: ' + str([i for i in ids if ids.count(i) > 1]))
kinds, stats = set(d['vocab']['kind']), set(d['vocab']['status'])
for e in d['entries']:
    for k in REQ:
        if k not in e: errs.append(f"{e.get('id')}: нет поля {k}")
    if e.get('kind') not in kinds: errs.append(f"{e['id']}: kind {e.get('kind')}")
    if e.get('status') not in stats: errs.append(f"{e['id']}: status {e.get('status')}")
    for u in e.get('use_for', []) or []:
        if u not in eff: errs.append(f"{e['id']}: неизвестный эффект {u}")
    for a in e.get('alternatives', []) or []:
        if ' ' not in a and a not in ids and not a.startswith('свой'): errs.append(f"{e['id']}: alternative {a} не в entries")
    if e.get('status') == 'conditional' and 'when' not in e: errs.append(f"{e['id']}: conditional без when")
    for l in e.get('levels', []):
        if l not in ('L0', 'L1', 'L2'): errs.append(f"{e['id']}: уровень {l}")
cms = {p['id'] for p in d['platforms']}
need = {'tilda', 'wordpress', '1c-bitrix', 'webflow', 'framer', 'custom', 'static', 'none'}
if cms != need: errs.append(f'platforms: {sorted(cms ^ need)}')
covered = {u for e in d['entries'] if e['status'] in ('default', 'conditional') for u in (e.get('use_for') or [])}
print('entries', len(ids), '| platforms', len(cms), '| effects covered', len(covered), 'of', len(eff), '| missing:', sorted(eff - covered))
print('checked_at', d['checked_at'], type(d['checked_at']).__name__)
print('ERRORS' if errs else 'OK', *errs, sep='\n')
sys.exit(1 if errs else 0)
