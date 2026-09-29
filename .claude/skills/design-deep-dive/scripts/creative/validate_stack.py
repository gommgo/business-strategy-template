#!/usr/bin/env python3
"""Проверка каталога стека подачи kb/creative/07-stack-implementation/stack.yaml.

Что проверяет: YAML читается; у записи есть обязательные поля; id уникальны; kind и status — из словаря файла; условная
запись (conditional) называет условие when; уровни — L0, L1, L2; alternatives ведут на записи каталога (или словами
«свой …», «CSS …»); платформы заказчика — полный набор. Ссылки с префиксом разрешаются: use_for — только effect:<id>
каталога эффектов kb/creative/06-effects-catalog/effects.yaml. Вес: size_br — число (сценарий «типовая инициализация»)
или словарь «сцена → КБ» (у three, R3F, model-viewer, paper-shaders — обязательно), null — не замерено; size_net_kb — вес по
сети на странице в той же форме; значение сцены — КБ, null (не замерено) или части {js, wasm}. Печатает покрытие эффектов
записями default и conditional.

  python3 validate_stack.py [--file stack.yaml]    код выхода: 0 — ошибок нет, 1 — есть
  python3 validate_stack.py --selftest             каталог базы без ошибок и подброшенные ошибки ловятся
"""
import argparse
import copy
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import kbpaths  # noqa: E402

STACK = kbpaths.kb('creative', '07-stack-implementation', 'stack.yaml')
EFFECTS = kbpaths.kb('creative', '06-effects-catalog', 'effects.yaml')
REQ = ['id', 'name', 'kind', 'version', 'license', 'size_br', 'init_tbt_ms', 'levels', 'status', 'alternatives', 'risks', 'alive', 'refs']
PLATFORMS = {'tilda', 'wordpress', '1c-bitrix', 'webflow', 'framer', 'custom', 'static', 'none'}
KEY = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
EFFECT_REF = re.compile(r'^effect:([a-z0-9]+(?:-[a-z0-9]+)*)$')


def load(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def effect_ids(path=EFFECTS):
    return {e['id'] for e in load(path)['effects']}


SCENE_KEYED = ('three', 'react-three-fiber', 'model-viewer', 'paper-shaders')   # вес зависит от сцены и способа загрузки


def is_kb(n):
    return n is None or (isinstance(n, (int, float)) and not isinstance(n, bool))


def size_errors(eid, field, v):
    """size_br и size_net_kb: КБ, null или словарь «сцена → КБ | null | {часть: КБ}»."""
    if field == 'size_br' and is_kb(v):
        return [] if eid not in SCENE_KEYED or v is None else [f'{eid}: {field} — словарь «сцена → КБ»: вес зависит от сцены']
    if not isinstance(v, dict) or not v:
        return [f'{eid}: {field} — число или словарь «сцена → КБ»']
    out = []
    for k, n in v.items():
        if not isinstance(k, str) or not k.strip():
            out.append(f'{eid}: {field}: пустой ключ сцены')
        elif field == 'size_net_kb' and not KEY.match(k):
            out.append(f'{eid}: {field}: ключ {k!r} не kebab-case')
        if isinstance(n, dict):
            out += [f'{eid}: {field}.{k}.{part} — не число' for part, x in n.items() if not is_kb(x)]
        elif not is_kb(n):
            out.append(f'{eid}: {field}.{k} — не число')
    return out


def check(d, effects):
    errs = []
    ids = [e.get('id') for e in d['entries']]
    dups = sorted({i for i in ids if ids.count(i) > 1})
    if dups:
        errs.append(f'дубли id: {dups}')
    kinds, stats = set(d['vocab']['kind']), set(d['vocab']['status'])
    for e in d['entries']:
        eid = e.get('id')
        for k in REQ:
            if k not in e:
                errs.append(f'{eid}: нет поля {k}')
        if e.get('kind') not in kinds:
            errs.append(f'{eid}: kind {e.get("kind")}')
        if e.get('status') not in stats:
            errs.append(f'{eid}: status {e.get("status")}')
        for u in e.get('use_for') or []:
            m = EFFECT_REF.match(str(u))
            if not m:
                errs.append(f'{eid}: use_for {u!r} — не ссылка effect:<id>')
            elif m.group(1) not in effects:
                errs.append(f'{eid}: {u} нет в каталоге эффектов')
        for a in e.get('alternatives') or []:
            if ' ' not in a and a not in ids and not a.startswith('свой'):
                errs.append(f'{eid}: alternative {a} не в entries')
        if e.get('status') == 'conditional' and 'when' not in e:
            errs.append(f'{eid}: conditional без when')
        for lv in e.get('levels') or []:
            if lv not in ('L0', 'L1', 'L2'):
                errs.append(f'{eid}: уровень {lv}')
        if 'size_br' in e:
            errs += size_errors(eid, 'size_br', e['size_br'])
        if 'size_net_kb' in e:
            errs += size_errors(eid, 'size_net_kb', e['size_net_kb'])
    cms = {p['id'] for p in d['platforms']}
    if cms != PLATFORMS:
        errs.append(f'platforms: {sorted(cms ^ PLATFORMS)}')
    return errs


def coverage(d, effects):
    covered = {EFFECT_REF.match(u).group(1) for e in d['entries'] if e['status'] in ('default', 'conditional')
               for u in (e.get('use_for') or []) if EFFECT_REF.match(str(u))}
    return covered & effects, sorted(effects - covered)


def selftest():
    ok = True

    def expect(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f'{"OK  " if cond else "FAIL"} {name}')
    d, eff = load(STACK), effect_ids()
    expect('каталог базы без ошибок', not check(d, eff))
    by = {e['id']: e for e in d['entries']}
    expect('size_br у three, R3F, model-viewer, paper-shaders — с ключом сцены',
           all(isinstance(by[i]['size_br'], dict) for i in ('three', 'react-three-fiber', 'model-viewer', 'paper-shaders')))
    cases = [
        ('эффект без префикса', lambda x: x['entries'][0]['use_for'].append('marquee-logos'), 'не ссылка effect:'),
        ('префикс с неизвестным id', lambda x: x['entries'][0]['use_for'].append('effect:no-such-effect'), 'нет в каталоге'),
        ('чужой префикс вместо effect:', lambda x: x['entries'][0]['use_for'].append('cliche:marquee-strip'), 'не ссылка effect:'),
        ('вес three одним числом', lambda x: by_id(x, 'three').update({'size_br': 158}), 'вес зависит от сцены'),
        ('вес по сети с ключом не kebab-case', lambda x: by_id(x, 'model-viewer')['size_net_kb'].update({'jsDelivr min': 282}), 'не kebab-case'),
        ('вес словом', lambda x: by_id(x, 'model-viewer').update({'size_br': 'около 240'}), 'число или словарь'),
        ('дубль id', lambda x: x['entries'].append(copy.deepcopy(x['entries'][0])), 'дубли id'),
        ('conditional без when', lambda x: by_id(x, 'three').pop('when'), 'conditional без when'),
    ]
    for name, mut, want in cases:
        x = copy.deepcopy(d)
        mut(x)
        errs = check(x, eff)
        expect(f'ловит: {name}', any(want in m for m in errs))
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def by_id(d, eid):
    return next(e for e in d['entries'] if e['id'] == eid)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--file', default=str(STACK), help='каталог стека (по умолчанию — файл базы)')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    d, eff = load(a.file), effect_ids()
    errs = check(d, eff)
    cov, missing = coverage(d, eff)
    print('entries', len(d['entries']), '| platforms', len(d['platforms']), '| effects covered', len(cov), 'of', len(eff), '| без записи стека:', missing)
    print('checked_at', d['checked_at'], type(d['checked_at']).__name__)
    print('ERRORS' if errs else 'OK', *errs, sep='\n')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
