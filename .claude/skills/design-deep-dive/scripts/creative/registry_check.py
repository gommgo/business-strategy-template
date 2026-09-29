#!/usr/bin/env python3
"""Проверка реестра клише kb/creative/08-uniqueness-anti-slop/cliche-registry.yaml и его стыков.

Реестр не правит — печатает находки:
  ошибки       — обязательные поля и словари записи, id, кластеры с обеих сторон, id_aliases, коды обнаружения, уровни,
                 даты; ссылки cliche:<id> в файлах базы разрешаются; ключ k3_allow есть среди ключей --allow проверок
                 утилиты макета (kb/common/tells.yaml, раздел checks, поле allow);
  расхождения  — k3_allow ↔ checks: ключ записи снимает проверку, которая ловит другую примету, или проверка с ключом
                 ловит примету записи, а у записи ключа нет (примета записи — её id или запись tells, чьё поле also ведёт
                 на cliche-registry.yaml#<id>; составную запись снимает ключ одной из её проверок); статусы — у эффекта kb/creative/06-effects-catalog/effects.yaml со
                 ссылкой cliche.registry_id слово статуса (fresh, saturated, dated) в cliche.status расходится со статусом
                 записи реестра, ссылка ведёт в пустоту или запись реестра названа только текстом.

  python3 registry_check.py [--refs DIR ...] [--json]   код выхода: 0 — ни ошибок, ни расхождений; 1 — есть
  python3 registry_check.py --selftest                  подброшенные ошибки и расхождения ловятся; у реестра базы —
                                                        0 ошибок структуры (расхождения печатаются)
"""
import argparse
import collections
import copy
import glob
import json
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import kbpaths  # noqa: E402

ROOT = str(kbpaths.kb('creative'))
REG = os.path.join(ROOT, '08-uniqueness-anti-slop', 'cliche-registry.yaml')
EFFECTS = os.path.join(ROOT, '06-effects-catalog', 'effects.yaml')
TELLS = str(kbpaths.kb(None, 'common', 'tells.yaml'))
REQ = ['id', 'name_ru', 'family', 'sign', 'signals', 'detect', 'threshold', 'first_seen', 'saturated_since', 'status', 'severity',
       'risk', 'levels', 'justify_if', 'twists', 'replace_with', 'cluster', 'k3_allow', 'neighbors', 'evidence', 'checked_at', 'review_by']
ENUM = {'status': {'fresh', 'saturated', 'dated'}, 'severity': {'B', 'S', 'D'}, 'risk': {'high', 'mid', 'low'},
        'family': {'color', 'surface', 'background', '3d', 'type', 'chrome', 'layout', 'motion', 'interaction', 'product', 'imagery', 'meta'}}
STATUS_WORDS = ('fresh', 'saturated', 'dated')
ID = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*')
REG_LINK = re.compile(r'cliche-registry\.yaml#([a-z0-9]+(?:-[a-z0-9]+)*)')
CLICHE_REF = re.compile(r'cliche:([a-z0-9]+(?:-[a-z0-9]+)*)')


def load(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def structure(d, allow_keys):
    err = []
    ids = [e.get('id') for e in d['entries']]
    for i in sorted({i for i in ids if ids.count(i) > 1}):
        err.append(f'дубль id {i}')
    codes = set(d['detect_codes'])
    for e in d['entries']:
        for k in REQ:
            if k not in e:
                err.append(f"{e.get('id')}: нет поля {k}")
        if not ID.fullmatch(e.get('id') or ''):
            err.append(f"{e.get('id')}: id не kebab-case")
        for k, allowed in ENUM.items():
            if e.get(k) not in allowed:
                err.append(f"{e['id']}: {k}={e.get(k)}")
        if e.get('k3_allow') is not None and e['k3_allow'] not in allow_keys:
            err.append(f"{e['id']}: k3_allow={e['k3_allow']} — такого ключа --allow нет у проверок (tells.yaml#checks)")
        for m in (e.get('detect') or {}).get('method', []):
            if m not in codes:
                err.append(f"{e['id']}: код обнаружения {m} не в detect_codes")
        for lv in ('L0', 'L1', 'L2'):
            if lv not in (e.get('levels') or {}):
                err.append(f"{e['id']}: levels без {lv}")
        for f in ('checked_at', 'review_by'):
            if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(e.get(f))):
                err.append(f"{e['id']}: {f} не дата")
    declared = {c['id'] for c in d['clusters']}
    members = {c['id']: set(c['members']) for c in d['clusters']}
    by = {e['id']: e for e in d['entries']}
    for e in d['entries']:
        for c in e.get('cluster') or []:
            if c not in declared:
                err.append(f"{e['id']}: кластер {c} не объявлен")
            elif e['id'] not in members[c]:
                err.append(f"{e['id']}: указан кластер {c}, но не в его members")
    for c in d['clusters']:
        for m in c['members']:
            if m not in by:
                err.append(f"кластер {c['id']}: нет записи {m}")
            elif c['id'] not in (by[m].get('cluster') or []):
                err.append(f"кластер {c['id']}: у {m} нет его в поле cluster")
    for a, t in (d.get('id_aliases') or {}).items():
        if t not in by:
            err.append(f'id_aliases: {a} → {t} нет записи')
    return err


def cliche_refs(d, dirs):
    known = {e['id'] for e in d['entries']} | set(d.get('id_aliases') or {})
    refs, unresolved = collections.Counter(), collections.Counter()
    for dd in dirs:
        for f in glob.glob(os.path.join(dd, '**', '*'), recursive=True):
            if not os.path.isfile(f) or not f.endswith(('.json', '.yaml', '.yml', '.md')):
                continue
            for m in CLICHE_REF.finditer(open(f, encoding='utf-8', errors='replace').read()):
                refs[m.group(1)] += 1
                if m.group(1) not in known:
                    unresolved[(os.path.relpath(f, ROOT), m.group(1))] += 1
    return refs, unresolved


def allow_vs_checks(d, tells):
    """Расхождения k3_allow записей с проверками tells.yaml#checks, у которых есть ключ --allow."""
    reg = {e['id']: e for e in d['entries']}
    by_tell = {t['id']: t for t in tells.get('tells') or []}

    def entries_of(tell):
        out = {tell} & set(reg)
        for a in (by_tell.get(tell) or {}).get('also') or []:
            out |= set(REG_LINK.findall(str(a))) & set(reg)
        return out
    checks = {k: v for k, v in (tells.get('checks') or {}).items() if isinstance(v, dict) and v.get('allow')}
    out = []
    for e in d['entries']:
        key = e.get('k3_allow')
        if key is None:
            continue
        mine = {cid: c for cid, c in checks.items() if c['allow'] == key}
        if mine and not any(e['id'] in entries_of(c.get('tell')) for c in mine.values()):
            caught = ', '.join(f"{cid} → {c.get('tell')}" for cid, c in sorted(mine.items()))
            out.append({'kind': 'k3_allow', 'entry': e['id'], 'key': key,
                        'message': f"k3_allow {key} снимает проверку другой приметы ({caught}), а не {e['id']}"})
    for cid, c in sorted(checks.items()):
        for rid in sorted(entries_of(c.get('tell'))):
            if reg[rid].get('k3_allow') is None:
                out.append({'kind': 'k3_allow', 'entry': rid, 'key': c['allow'],
                            'message': f"{cid} (ключ {c['allow']}) ловит примету {rid}, а у записи ключа нет"})
    return out


def statuses(d, effects):
    """Статус приёма живёт в реестре клише; effects.yaml ссылается на запись (cliche.registry_id)."""
    reg = {e['id']: e for e in d['entries']}
    alias = d.get('id_aliases') or {}
    out = []
    for e in effects.get('effects') or []:
        c = e.get('cliche') or {}
        rid, text = c.get('registry_id'), str(c.get('status') or '')
        words = {w for w in STATUS_WORDS if re.search(rf'\b{w}\b', text)}
        if rid:
            m = CLICHE_REF.fullmatch(str(rid))
            key = alias.get(m.group(1), m.group(1)) if m else None
            if key not in reg:
                out.append({'kind': 'status', 'entry': e['id'], 'message': f"cliche.registry_id {rid} — записи нет в реестре"})
                continue
            want = reg[key]['status']
            if words and want not in words:
                out.append({'kind': 'status', 'entry': e['id'],
                            'message': f"статус «{text}» расходится с записью {key}: {want}"})
        else:
            named = sorted(set(CLICHE_REF.findall(text)) & (set(reg) | set(alias)))
            if named:
                out.append({'kind': 'status', 'entry': e['id'],
                            'message': f"запись реестра {', '.join(named)} названа в тексте статуса, а cliche.registry_id пуст"})
    return out


def run(d, tells, effects, dirs):
    allow_keys = {v['allow'] for v in (tells.get('checks') or {}).values() if isinstance(v, dict) and v.get('allow')}
    err = structure(d, allow_keys)
    refs, unresolved = cliche_refs(d, dirs)
    err += [f'ссылка cliche:{i} ← {f} — записи нет' for (f, i) in unresolved]
    diffs = allow_vs_checks(d, tells) + statuses(d, effects)
    return err, diffs, refs


def selftest():
    ok = True

    def expect(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f'{"OK  " if cond else "FAIL"} {name}')
    d, tells, effects = load(REG), load(TELLS), load(EFFECTS)
    err, diffs, _ = run(d, tells, effects, [])
    expect('реестр базы: 0 ошибок структуры', not err)
    for m in diffs:
        print('     расхождение:', m['entry'], '—', m['message'])
    syn_reg = {'detect_codes': ['DOM'], 'id_aliases': {}, 'clusters': [{'id': 'k', 'members': ['a-tell', 'b-tell']}],
               'entries': []}
    base = {k: None for k in REQ}
    for i, key, st in (('a-tell', 'x', 'saturated'), ('b-tell', 'y', 'dated'), ('c-tell', None, 'fresh')):
        e = dict(base, id=i, name_ru=i, family='color', status=st, severity='S', risk='mid', k3_allow=key,
                 levels={'L0': '', 'L1': '', 'L2': ''}, cluster=['k'] if i != 'c-tell' else [], detect={'method': ['DOM']},
                 checked_at='2026-09-24', review_by='2027-03-24')
        syn_reg['entries'].append(e)
    syn_tells = {'tells': [{'id': 'a-tell', 'also': []}, {'id': 'other', 'also': ['creative/08-uniqueness-anti-slop/cliche-registry.yaml#c-tell']}],
                 'checks': {'CHK-A': {'tell': 'a-tell', 'allow': 'x'}, 'CHK-B': {'tell': 'other', 'allow': 'y'}}}
    syn_eff = {'effects': [{'id': 'e1', 'cliche': {'registry_id': 'cliche:b-tell', 'status': 'saturated (ряд)'}},
                           {'id': 'e2', 'cliche': {'registry_id': 'cliche:no-such', 'status': 'dated'}},
                           {'id': 'e3', 'cliche': {'registry_id': None, 'status': 'маскот — cliche:a-tell'}},
                           {'id': 'e4', 'cliche': {'registry_id': 'cliche:a-tell', 'status': 'saturated'}}]}
    err, diffs, _ = run(syn_reg, syn_tells, syn_eff, [])
    msgs = [m['message'] for m in diffs]
    expect('синтетика: 0 ошибок структуры', not err)
    expect('ловит: ключ снимает проверку другой приметы (b-tell → y ловит c-tell)', any('b-tell' in m and 'снимает проверку другой приметы' in m for m in msgs))
    expect('ловит: проверка ловит примету записи без ключа (CHK-B → c-tell)', any('CHK-B (ключ y) ловит примету c-tell' in m for m in msgs))
    expect('не шумит: ключ записи совпадает с её проверкой (a-tell → x)', not any(m.startswith('k3_allow x') for m in msgs))
    expect('ловит: статус эффекта расходится с записью', any('e1' == m['entry'] for m in diffs))
    expect('ловит: registry_id в пустоту', any('e2' == m['entry'] for m in diffs))
    expect('ловит: запись реестра только в тексте статуса', any('e3' == m['entry'] for m in diffs))
    expect('не шумит: статус совпадает', not any('e4' == m['entry'] for m in diffs))
    bad = copy.deepcopy(syn_reg)
    bad['entries'][0]['k3_allow'] = 'no-such-key'
    err, _, _ = run(bad, syn_tells, syn_eff, [])
    expect('ошибка: ключа --allow нет у проверок', any('такого ключа --allow нет' in m for m in err))
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--refs', nargs='+', help='папки, где искать ссылки cliche:<id> (по умолчанию — 01-creative-direction и 08-uniqueness-anti-slop)')
    ap.add_argument('--json', action='store_true', help='итог одним JSON в stdout')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    d, tells, effects = load(REG), load(TELLS), load(EFFECTS)
    dirs = a.refs or [os.path.join(ROOT, '01-creative-direction'), os.path.join(ROOT, '08-uniqueness-anti-slop')]
    err, diffs, refs = run(d, tells, effects, dirs)
    if a.json:
        print(json.dumps({'entries': len(d['entries']), 'errors': err, 'discrepancies': diffs, 'cliche_refs': sum(refs.values())},
                         ensure_ascii=False, indent=1))
        return 1 if err or diffs else 0
    print('записей', len(d['entries']), '| статусы', dict(collections.Counter(e['status'] for e in d['entries'])),
          '| серьёзность', dict(collections.Counter(e['severity'] for e in d['entries'])),
          '| риск', dict(collections.Counter(e['risk'] for e in d['entries'])))
    print('семейства', dict(collections.Counter(e['family'] for e in d['entries'])))
    print('ссылок cliche:', sum(refs.values()))
    for x in err:
        print('ОШИБКА', x)
    for m in diffs:
        print('РАСХОЖДЕНИЕ', m['kind'], m['entry'], '—', m['message'])
    print('итог: ошибок', len(err), '| расхождений', len(diffs))
    return 1 if err or diffs else 0


if __name__ == '__main__':
    sys.exit(main())
