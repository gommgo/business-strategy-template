#!/usr/bin/env python3
"""recipe_check.py — проверка рецептов 10-recipes/recipes/*.recipe.yaml (creative-research · J · волна 3 · 2026-09-25).

Запуск: 99-raw/tools/venv-J/bin/python 99-raw/experiments/J/03-recipes-check/recipe_check.py 10-recipes/recipes/*.recipe.yaml [--ledger OUT.md]
Проверяет: (1) схему recipe.schema.json; (2) block:<id> — есть в ../site-research/04-blocks/blocks.yaml; role — section_role словаря site;
page_type — page_type словаря; (3) effect:<id> — есть в 06-effects-catalog/effects.yaml; (4) cliche:<id> — в cliche-registry.yaml H;
(5) EG-… — в effect-gates.yaml K; (6) уровень секции ≤ уровня страницы, конверсия (lead-form, pricing, calculator, quiz, pricing-*, email-capture,
booking-widget) — L0; пиков по уровню (L0 0, L1 ≤ 2, L2 2–4); эффект секции не выше уровня секции (level_min F);
(7) журнал вариативности: каждая пара рецептов подряд различается ≥ 4 из 8 осей (H 02 §3.2), таблица всех пар — в --ledger.
Код выхода 0 — ошибок нет; 1 — есть ошибки.
"""
import argparse
import itertools
import json
import os
import sys

import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('creative'))
SITE = str(kbpaths.kb('site'))
LV = {'L0': 0, 'L1': 1, 'L2': 2}
CONV_BLOCKS = {'lead-form', 'calculator', 'quiz', 'pricing-cards', 'pricing-table', 'pricing-single', 'email-capture', 'booking-widget'}
AXES = ['paper', 'display_style', 'accent_hue', 'macrostructure', 'hero_architecture', 'main_technique', 'motion_signature', 'corner_language']


def load(p):
    return yaml.safe_load(open(p, encoding='utf-8'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--ledger')
    a = ap.parse_args()
    schema = json.load(open(os.path.join(ROOT, '10-recipes/recipes/recipe.schema.json'), encoding='utf-8'))
    val = Draft202012Validator(schema)
    blocks = set(load(os.path.join(SITE, '04-blocks/blocks.yaml'))['blocks'].keys())
    voc = load(os.path.join(SITE, '02-site-types/vocabulary.yaml'))['namespaces']
    roles = set(voc['section_role']['values'].keys()) if isinstance(voc['section_role']['values'], dict) else {x['id'] for x in voc['section_role']['values']}
    ptypes = set(voc['page_type']['values'].keys()) if isinstance(voc['page_type']['values'], dict) else {x['id'] for x in voc['page_type']['values']}
    eff = {e['id']: e for e in load(os.path.join(ROOT, '06-effects-catalog/effects.yaml'))['effects']}
    cl = {e['id'] for e in load(os.path.join(ROOT, '08-uniqueness-anti-slop/cliche-registry.yaml'))['entries']}
    gates = {g['id'] for g in load(os.path.join(ROOT, '09-ai-execution-evaluation/effect-gates.yaml'))['gates']}
    errs, warns, recs = [], [], []
    for f in a.files:
        r = load(f)
        name = os.path.basename(f)
        recs.append((name, r))
        for e in sorted(val.iter_errors(r), key=lambda e: list(e.path)):
            errs.append(f'{name}: схема: {"/".join(map(str, e.path))}: {e.message[:160]}')
        if not isinstance(r, dict):
            continue
        lvl = LV.get(r.get('level'), 2)
        if r.get('page_type') not in ptypes:
            errs.append(f'{name}: page_type {r.get("page_type")} нет в словаре site')
        peaks = 0
        for s in (r.get('page_plan') or {}).get('sections') or []:
            b = (s.get('block') or '').split(':', 1)[-1]
            if b not in blocks:
                errs.append(f'{name}: {s.get("id")}: block:{b} нет в blocks.yaml site')
            if s.get('role') not in roles:
                errs.append(f'{name}: {s.get("id")}: role {s.get("role")} нет в section_role site')
            sl = LV.get(s.get('level'), 0)
            if sl > lvl:
                errs.append(f'{name}: {s.get("id")}: уровень секции {s.get("level")} выше страницы {r.get("level")}')
            if (b in CONV_BLOCKS or s.get('role') in ('lead-form', 'pricing')) and sl > 0:
                errs.append(f'{name}: {s.get("id")}: секция конверсии не L0')
            if s.get('visual_role') == 'peak':
                peaks += 1
            for x in s.get('effects') or []:
                i = x.split(':', 1)[1]
                if i not in eff:
                    errs.append(f'{name}: {s.get("id")}: {x} нет в effects.yaml')
                else:
                    lm = eff[i].get('level_min')
                    if lm in LV and LV[lm] > sl:
                        warns.append(f'{name}: {s.get("id")}: {x} level_min {lm} выше уровня секции {s.get("level")}')
        pmax = {0: (0, 0), 1: (0, 2), 2: (2, 4)}[lvl]
        if not pmax[0] <= peaks <= pmax[1]:
            errs.append(f'{name}: пиков {peaks}, норма {pmax[0]}–{pmax[1]} для {r.get("level")} (E 05/01 §5.5)')
        mt = ((r.get('ledger') or {}).get('main_technique') or '').split(':', 1)[-1]
        if mt and mt not in eff:
            errs.append(f'{name}: ledger.main_technique effect:{mt} нет в effects.yaml')
        for d in r.get('decisions') or []:
            ns, _, i = (d.get('technique') or '').partition(':')
            if ns == 'cliche' and i not in cl:
                errs.append(f'{name}: {d.get("id")}: cliche:{i} нет в реестре H')
            if ns == 'effect' and i not in eff:
                errs.append(f'{name}: {d.get("id")}: effect:{i} нет в effects.yaml')
        for g in (r.get('gates') or {}).get('must_pass') or []:
            if g.startswith('EG-') and g not in gates:
                errs.append(f'{name}: ворота {g} нет в effect-gates.yaml')
    # журнал вариативности
    rows = []

    def ax(r, k):
        v = (r.get('ledger') or {}).get(k)
        return json.dumps(v, sort_keys=True, ensure_ascii=False) if isinstance(v, dict) else v
    for (n1, r1), (n2, r2) in itertools.combinations(recs, 2):
        diff = [k for k in AXES if ax(r1, k) != ax(r2, k)]
        rows.append((n1, n2, len(diff), diff))
    for (n1, r1), (n2, r2) in zip(recs, recs[1:]):
        d = sum(ax(r1, k) != ax(r2, k) for k in AXES)
        if d < 4:
            errs.append(f'журнал: {n1} → {n2}: различий {d} из 8 (< 4)')
    close = [x for x in rows if x[2] < 4]
    if a.ledger:
        with open(a.ledger, 'w', encoding='utf-8') as fh:
            fh.write('# Журнал вариативности рецептов (8 осей H) · recipe_check.py · 2026-09-25\n\n')
            fh.write('| Рецепт | ' + ' | '.join(AXES) + ' |\n|' + '---|' * (len(AXES) + 1) + '\n')
            for n, r in recs:
                fh.write(f'| {n.replace(".recipe.yaml", "")} | ' + ' | '.join(str(ax(r, k)).replace('|', '/') for k in AXES) + ' |\n')
            fh.write(f'\nПары с различием < 4 осей: {len(close)} из {len(rows)}\n\n')
            for n1, n2, d, diff in sorted(rows, key=lambda x: x[2])[:12]:
                fh.write(f'- {n1} ↔ {n2}: {d} ({", ".join(diff)})\n')
    for w in warns:
        print('warning', w)
    for e in errs:
        print('error  ', e)
    print(f'== рецептов {len(recs)}: error {len(errs)}, warning {len(warns)}; пар < 4 осей: {len(close)} из {len(rows)}')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
