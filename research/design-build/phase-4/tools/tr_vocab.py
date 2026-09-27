#!/usr/bin/env python3
"""Сверка словарей тройки site / text / creative для узла TR фазы 4 (сверка баз).

Читает большие файлы данных по ключам и печатает сводку — счёт, пересечения, пустые поля — вместо чтения целиком:
- site `02-site-types/vocabulary.yaml` (словарь системы v1) и `02-site-types/crosswalk.tsv` (соответствие словарей);
- text `99-raw/notes/temp-vocabulary-v0.yaml` (временный словарь) и `04-copy-by-block/copy-slots.yaml` (правила слотов);
- text `10-templates-recipes/examples/*.yaml` (поле `block` в примерах copy deck);
- creative `01-creative-direction/ambition-levels.yaml` (`defaults_by_page_type`), `06-effects-catalog/effects.yaml`.

Файлы только читает. Запуск (нужен PyYAML — venv скилла):
    ~/.cache/design-deep-dive/venv/bin/python tools/tr_vocab.py [--kb <путь к kb>] [--section A,B,...]
Разделы: A — словарь site; B — временный словарь text; C — copy-slots.yaml; D — crosswalk.tsv; E — поле `block` в
примерах copy deck; F — уровни creative по типам страниц; G — ссылки с префиксом пространства у сестёр.
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_KB = os.path.normpath(os.path.join(HERE, '..', '..', '..', '..', '.claude', 'skills', 'design-deep-dive', 'kb'))


def load_yaml(path):
    with open(path, encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def ids(values):
    return [v['id'] for v in values]


def short(items, n=40):
    items = list(items)
    tail = f' … (+{len(items) - n})' if len(items) > n else ''
    return ', '.join(str(x) for x in items[:n]) + tail


def section_a(kb, out):
    v = load_yaml(os.path.join(kb, 'site/02-site-types/vocabulary.yaml'))
    out.append('## A. Словарь site v1 (`vocabulary.yaml`)')
    out.append(f"version={v.get('version')} revision={v.get('revision')} status={v.get('status')}")
    total = 0
    for name, ns in v['namespaces'].items():
        vals = ns['values']
        total += len(vals)
        st = collections.Counter(x.get('status', 'active') for x in vals)
        out.append(f'- {name}: {len(vals)} {dict(st)}')
    out.append(f'- всего id: {total}; ref_prefixes: {len(v["ref_prefixes"])}; foreign_prefixes: {short(v["foreign_prefixes"])}')
    ns = v['namespaces']
    sr = ns['section_role']['values']
    out.append(f"- section_role не active: {short(x['id'] + ':' + x.get('status', 'active') for x in sr if x.get('status', 'active') != 'active')}")
    pt = ns['page_type']['values']
    out.append(f"- page_type не active: {short(x['id'] + ':' + x.get('status') for x in pt if x.get('status', 'active') != 'active')}")
    kinds = collections.Counter(x.get('kind') for x in ns['slot']['values'])
    out.append(f'- slot по kind: {dict(kinds)}')
    scopes = collections.Counter(x.get('scope', 'section') for x in ns['slot']['values'])
    out.append(f'- slot по scope: {dict(scopes)}')
    out.append('')
    return v


def section_b(kb, out, v):
    t = load_yaml(os.path.join(kb, 'text/99-raw/notes/temp-vocabulary-v0.yaml'))
    ns = v['namespaces']
    site_pt, site_sr, site_slot = set(ids(ns['page_type']['values'])), set(ids(ns['section_role']['values'])), set(ids(ns['slot']['values']))
    out.append('## B. Временный словарь text (`temp-vocabulary-v0.yaml`)')
    out.append(f"status={t.get('status')} version={t.get('version')}; owner: {t.get('owner')}")
    for key, site_set, label in (('page_types', site_pt, 'page_type'), ('section_roles', site_sr, 'section_role')):
        vals = t[key]
        tid = ids(vals)
        filled = [x['id'] for x in vals if str(x.get('site_id', '') or '').strip()]
        out.append(f'- {key}: {len(tid)}; нет в словаре site: [{short(sorted(set(tid) - site_set))}]; site_id заполнен: {len(filled)}')
        out.append(f'  в словаре site, но нет у text ({len(site_set - set(tid))}): {short(sorted(site_set - set(tid)))}')
    st = t['slot_types']
    tid = ids(st)
    ux = collections.Counter((x.get('ux_role') or '—') for x in st)
    site_id_filled = [x['id'] for x in st if str(x.get('site_id', '') or '').strip()]
    has_site_field = sum(1 for x in st if 'site_id' in x or 'site_slot' in x)
    out.append(f'- slot_types: {len(tid)}; нет в словаре site: [{short(sorted(set(tid) - site_slot))}]; поле site_id/site_slot есть у {has_site_field}, заполнено у {len(site_id_filled)}')
    out.append(f'  ux_role: {dict(ux)}')
    aw_site = set(ids(ns['awareness']['values']))
    aw_t = set(ids(t['awareness']))
    out.append(f'- awareness: text {sorted(aw_t)}; совпадает с site: {aw_t == aw_site}')
    temp = t['traffic'].get('temperature')
    src = t['traffic'].get('sources')
    temp_ids = [x['id'] if isinstance(x, dict) else x for x in (temp or [])]
    src_ids = [x['id'] if isinstance(x, dict) else x for x in (src or [])]
    out.append(f"- traffic.temperature text: {temp_ids}; site: {ids(ns['traffic_temperature']['values'])}")
    out.append(f"- traffic.sources text ({len(src_ids)}): нет у site: [{short(sorted(set(src_ids) - set(ids(ns['traffic_source']['values']))))}]")
    out.append('')
    return t


def section_c(kb, out, v, t):
    c = load_yaml(os.path.join(kb, 'text/04-copy-by-block/copy-slots.yaml'))
    ns = v['namespaces']
    site_slot = {x['id']: x for x in ns['slot']['values']}
    site_sr = set(ids(ns['section_role']['values']))
    st = c['slot_types']
    cid = ids(st)
    out.append('## C. Правила слотов text (`copy-slots.yaml`)')
    out.append(f"copy_slots_version={c.get('copy_slots_version')} status={c.get('status')}; vocabulary: {c.get('vocabulary')}")
    out.append(f"- slot_types: {len(cid)}; proposals: {c.get('proposals')}; composites: {list((c.get('composites') or {}).keys())}; renames: {c.get('renames')}")
    filled = [x['id'] for x in st if str(x.get('site_slot', '') or '').strip()]
    out.append(f'- site_slot заполнен: {len(filled)} из {len(cid)}')
    out.append(f'- slot_type нет в словаре site: [{short(sorted(set(cid) - set(site_slot)))}]')
    prop_status = {p: (site_slot[p].get('status', 'active') if p in site_slot else 'нет') for p in (c.get('proposals') or [])}
    out.append(f'- proposals в словаре site: {prop_status}')
    text_kind = sorted(k for k, x in site_slot.items() if x.get('kind') == 'text')
    no_rules = sorted(set(text_kind) - set(cid))
    out.append(f'- текстовых слотов site (kind=text): {len(text_kind)}; без правил в copy-slots.yaml ({len(no_rules)}): {short(no_rules, 60)}')
    other_kind_with_rules = sorted(k for k in cid if k in site_slot and site_slot[k].get('kind') != 'text')
    out.append(f'- правила text у слотов site другого kind: {short(k + ":" + site_slot[k].get("kind", "") for k in other_kind_with_rules)}')
    refs = collections.Counter()
    unknown = collections.Counter()
    for x in st:
        for r in x.get('section_roles') or []:
            refs[r] += 1
            if r not in site_sr:
                unknown[r] += 1
    out.append(f'- ссылок на роли секций: {sum(refs.values())}; неизвестных site: {dict(unknown)}')
    ux = collections.Counter((x.get('ux_role') or '—') for x in st)
    out.append(f'- ux_role (роль текста ux): {dict(ux)}')
    temp_ids = set(ids(t['slot_types']))
    out.append(f'- copy-slots ⊇ временный словарь: {temp_ids <= set(cid)}; сверх него: {sorted(set(cid) - temp_ids)}')
    out.append('')


def section_d(kb, out, v, t):
    path = os.path.join(kb, 'site/02-site-types/crosswalk.tsv')
    with open(path, encoding='utf-8') as fh:
        rows = [r for r in csv.DictReader(fh, delimiter='\t') if not (r.get('source_base') or '').startswith('#')]
    ns = v['namespaces']
    all_ids = {name: set(ids(x['values'])) for name, x in ns.items()}
    out.append('## D. `crosswalk.tsv`')
    out.append(f'- строк: {len(rows)}; колонки: {list(rows[0].keys())}')
    out.append(f"- по source_base: {dict(collections.Counter(r['source_base'] for r in rows))}")
    out.append(f"- по relation: {dict(collections.Counter(r['relation'] for r in rows))}")
    bad = [(r['source_base'], r['source_term'], r['namespace'], r['our_id']) for r in rows
           if r['our_id'] and r['namespace'] in all_ids and r['our_id'] not in all_ids[r['namespace']]]
    out.append(f'- our_id нет в словаре своего пространства: {len(bad)} {bad[:10]}')
    text_rows = [r for r in rows if r['source_base'].startswith('text')]
    out.append(f"- строк text: {len(text_rows)}; файлы: {dict(collections.Counter(r['source_file'] for r in text_rows))}")
    out.append(f"  разделы: {dict(collections.Counter(r['source_section'] for r in text_rows))}")
    out.append(f"  relation: {dict(collections.Counter(r['relation'] for r in text_rows))}; our_id пуст: {sum(1 for r in text_rows if not r['our_id'])}")
    cs = [r for r in text_rows if 'copy-slots' in r['source_file']]
    out.append(f'  строк по copy-slots.yaml: {len(cs)}')
    hc = [(r['source_term'], r['our_id'], r['relation']) for r in rows if r['source_term'] == 'hero-core']
    out.append(f'- hero-core: {hc}')
    hr = [(r['source_base'], r['source_term']) for r in rows if r['source_term'] == 'hr']
    out.append(f'- hr: {hr}')
    for term in ('landing-product', 'landing-campaign'):
        m = [(r['source_base'], r['source_term'], r['our_id'], r['relation']) for r in rows if term in (r['source_term'], r['our_id'])]
        out.append(f'- {term}: {len(m)} строк: {m[:12]}')
    new_pt = ['specialist-page', 'location-page', 'program-catalog-page', 'search-results-page', 'documents-page',
              'event-program-page', 'speakers-page', 'integrations-page', 'security-page', 'html-sitemap-page']
    aim = [(r['source_term'], r['our_id'], r['relation']) for r in rows if r['source_base'].startswith('ai-media') and r['our_id'] in new_pt]
    out.append(f'- ai-media ↔ 10 новых page_type v1: {len(aim)} строк: {aim}')
    by_base_ns = collections.Counter((r['source_base'], r['namespace']) for r in rows)
    out.append(f'- (база, пространство): {dict(by_base_ns)}')
    out.append('')


def section_e(kb, out, v):
    ns = v['namespaces']
    blocks, roles = set(ids(ns['block']['values'])), set(ids(ns['section_role']['values']))
    files = sorted(glob.glob(os.path.join(kb, 'text/10-templates-recipes/examples/*.yaml')))
    out.append('## E. Поле `block` в примерах copy deck text')
    tot = collections.Counter()
    distinct = collections.Counter()
    for f in files:
        d = load_yaml(f)
        vals = []

        def walk(o):
            if isinstance(o, dict):
                for k, val in o.items():
                    if k == 'block' and isinstance(val, str):
                        vals.append(val)
                    walk(val)
            elif isinstance(o, list):
                for i in o:
                    walk(i)
        walk(d)
        cl = collections.Counter(('обе' if x in roles else 'block') if x in blocks else ('роль' if x in roles else 'нет') for x in vals)
        tot.update(cl)
        distinct.update(vals)
        out.append(f'- {os.path.basename(f)}: {len(vals)} значений {dict(cl)}')
    out.append(f'- итого: {dict(tot)} (обе — id есть и среди ролей, и среди блоков)')
    out.append(f"- разные значения: {short(sorted(distinct), 60)}")
    out.append(f"- только id блока: {sorted(x for x in distinct if x in blocks and x not in roles)}")
    out.append('')


def section_f(kb, out, v):
    a = load_yaml(os.path.join(kb, 'creative/01-creative-direction/ambition-levels.yaml'))
    ns = v['namespaces']
    pt = {x['id']: x.get('status', 'active') for x in ns['page_type']['values']}
    d = a.get('defaults_by_page_type') or {}
    out.append('## F. Уровни creative по типам страниц (`ambition-levels.yaml` `defaults_by_page_type`)')
    seen = {}
    for lvl, lst in d.items():
        if isinstance(lst, list):
            for p in lst:
                if isinstance(p, str) and ID_RE.match(p):
                    seen[p] = lvl
        elif isinstance(lst, dict):
            for l2, l2lst in lst.items():
                if isinstance(l2lst, list):
                    for p in l2lst:
                        if isinstance(p, str) and ID_RE.match(p):
                            seen[p] = f'{lvl}.{l2}'
    in_scope = sorted(p for p, s in pt.items() if s in ('active', 'proposed'))
    out.append(f'- типов в рамках (active+proposed): {len(in_scope)}; с уровнем у creative: {len(set(in_scope) & set(seen))}')
    out.append(f'- без уровня: {sorted(set(in_scope) - set(seen))}; лишние у creative: {sorted(set(seen) - set(pt))}')
    out.append(f"- proposed: {[(p, seen.get(p)) for p, s in pt.items() if s == 'proposed']}")
    e = load_yaml(os.path.join(kb, 'creative/06-effects-catalog/effects.yaml'))
    effs = e.get('effects') if isinstance(e, dict) else e
    if isinstance(effs, dict):
        effs = list(effs.values())
    keys = collections.Counter()
    for x in effs or []:
        if isinstance(x, dict):
            keys.update(k for k in x.keys() if 'role' in k)
    out.append(f"- effects.yaml: записей {len(effs or [])}; ключи с «role»: {dict(keys)}; version={e.get('version') if isinstance(e, dict) else '—'}")
    out.append('')


ID_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
PREFIX_RE = re.compile(r'\b(block|slot|section-role|page-type|site-type|macrostructure|action|awareness|traffic-temperature|traffic-source|ambition|first-screen-policy|conversion-channel|step):([a-z0-9][a-z0-9-]*)')


def section_g(kb, out, v):
    ns = v['namespaces']
    pref = {p: set(ids(ns[n]['values'])) for p, n in v['ref_prefixes'].items()}
    out.append('## G. Ссылки с префиксом пространства site у сестёр (text, creative; YAML, JSON, TSV, без 99-raw)')
    found = collections.Counter()
    unknown = []
    for base in ('text', 'creative'):
        for f in glob.glob(os.path.join(kb, base, '**', '*'), recursive=True):
            if '/99-raw/' in f or not f.endswith(('.yaml', '.yml', '.json', '.tsv')):
                continue
            try:
                s = open(f, encoding='utf-8').read()
            except (UnicodeDecodeError, IsADirectoryError):
                continue
            for m in PREFIX_RE.finditer(s):
                p, i = m.group(1), m.group(2)
                found[(base, p)] += 1
                if i not in pref.get(p, set()):
                    unknown.append((base, os.path.relpath(f, kb), f'{p}:{i}'))
    out.append(f'- найдено: {dict(found)}')
    out.append(f'- неизвестных id ({len(unknown)}): {unknown[:15]}')
    out.append('')


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--kb', default=DEFAULT_KB)
    ap.add_argument('--section', default='A,B,C,D,E,F,G')
    a = ap.parse_args()
    want = set(a.section.upper().split(','))
    out = []
    v = section_a(a.kb, out if 'A' in want else [])
    t = load_yaml(os.path.join(a.kb, 'text/99-raw/notes/temp-vocabulary-v0.yaml'))
    if 'B' in want:
        section_b(a.kb, out, v)
    if 'C' in want:
        section_c(a.kb, out, v, t)
    if 'D' in want:
        section_d(a.kb, out, v, t)
    if 'E' in want:
        section_e(a.kb, out, v)
    if 'F' in want:
        section_f(a.kb, out, v)
    if 'G' in want:
        section_g(a.kb, out, v)
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
