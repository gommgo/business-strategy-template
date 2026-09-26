#!/usr/bin/env python3
"""B2/01 — проверка схем B2: загрузка yaml.safe_load, метасхема draft 2020-12, валидация примеров и отрицательных случаев.

Запуск: 99-raw/tools/venv-B2/bin/python 99-raw/experiments/B2/01-schema-validate/validate.py
Выход: 0 — всё сошлось, 1 — есть расхождения. Даты YAML (datetime.date) приводятся к строке ISO до валидации.
"""
import copy, datetime, glob, os, sys
import yaml
from jsonschema import Draft202012Validator

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('text'))
SM = os.path.join(ROOT, '02-strategy-messaging')


def norm(x):
    if isinstance(x, dict):
        return {str(k): norm(v) for k, v in x.items()}
    if isinstance(x, list):
        return [norm(v) for v in x]
    if isinstance(x, (datetime.date, datetime.datetime)):
        return x.isoformat()
    return x


def load(p):
    with open(p, encoding='utf-8') as f:
        return norm(yaml.safe_load(f))


def errors(v, doc):
    return sorted(v.iter_errors(doc), key=lambda e: list(e.path))


ok = True


def check(name, cond, detail=''):
    global ok
    ok &= bool(cond)
    print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else f' → {detail}'))


# ---- facts
fs = load(os.path.join(SM, 'facts.schema.yaml'))
Draft202012Validator.check_schema(fs)
check('facts.schema.yaml: метасхема 2020-12', True)
check('facts.schema.yaml: поле date', fs.get('date') == '2026-09-24')
check('x-claim-classes = enum claim-class', [c['id'] for c in fs['x-claim-classes']] == fs['$defs']['claim-class']['enum'])
enum_classes = set(fs['$defs']['claim-class']['enum'])
check('x-never-claim-defaults: классы из enum',
      all(set(d['claim_class']) <= enum_classes for d in fs['x-never-claim-defaults']))
check('x-kinds = enum kind', set(fs['x-kinds']) == set(fs['$defs']['kind']['enum']))
fv = Draft202012Validator(fs)
examples = sorted(glob.glob(os.path.join(SM, 'examples', 'facts-*.yaml')))
check('примеров facts-*.yaml ≥ 2', len(examples) >= 2, examples)
for p in examples:
    doc = load(p)
    errs = errors(fv, doc)
    check(f'{os.path.basename(p)}: валиден', not errs, [f'{list(e.path)}: {e.message[:160]}' for e in errs[:8]])
    ids = [f['id'] for f in doc.get('facts', [])] + [m['id'] for m in doc.get('missing', [])]
    check(f'{os.path.basename(p)}: id уникальны', len(ids) == len(set(ids)))
    ents = {e['id'] for e in doc.get('entities', [])}
    bad = [(f['id'], e) for f in doc.get('facts', []) for e in f.get('entities', []) if e not in ents]
    check(f'{os.path.basename(p)}: ссылки entities существуют', not bad, bad)
    rel = {f['id'] for f in doc.get('facts', [])}
    badr = [(f['id'], r) for f in doc.get('facts', []) for r in f.get('related', []) if r not in rel]
    check(f'{os.path.basename(p)}: ссылки related существуют', not badr, badr)

# ---- отрицательные случаи: каждая мутация должна дать ошибку валидации
base = load(examples[0]) if examples else None
if base:
    def mutate(fn):
        d = copy.deepcopy(base)
        fn(d)
        return errors(fv, d)
    negs = {
        'факт без source': lambda d: d['facts'][0].pop('source'),
        'id не kebab-case': lambda d: d['facts'][0].__setitem__('id', 'Price_1'),
        'source.type = модель (нет в enum)': lambda d: d['facts'][0]['source'].__setitem__('type', 'model'),
        'пустой verbatim': lambda d: d['facts'][0].__setitem__('verbatim', []),
        'неизвестный класс': lambda d: d['facts'][0].__setitem__('claim_class', ['best-ever']),
        'дата не ISO': lambda d: d['facts'][0]['source'].__setitem__('date', '24.09.2026'),
        'placeholder без скобок': lambda d: d['missing'][0].__setitem__('placeholder', 'юрлицо'),
        'superlative без basis': lambda d: d['facts'][0].__setitem__('claim_class', ['superlative']),
        'health без legal.review': lambda d: d['facts'][0].__setitem__('claim_class', ['health']),
        'promo-deadline без valid.until': lambda d: (d['facts'][1].__setitem__('claim_class', ['promo-deadline']), d['facts'][1].pop('valid', None)),
        'testimonial без attribution': lambda d: d['facts'][0].__setitem__('kind', 'testimonial'),
        'rating без count/scale': lambda d: (d['facts'][0].__setitem__('kind', 'rating'), d['facts'][0]['source'].__setitem__('url', 'https://example.org')),
        'лишнее поле в факте': lambda d: d['facts'][0].__setitem__('confidence', 0.9),
        'facts_version 2': lambda d: d.__setitem__('facts_version', 2),
    }
    for name, fn in negs.items():
        errs = mutate(fn)
        check(f'отрицательный: {name} → ошибка', bool(errs), 'валидатор пропустил')

# ---- voc (если уже есть)
vp = os.path.join(SM, 'voc.schema.yaml')
if os.path.exists(vp):
    vs = load(vp)
    Draft202012Validator.check_schema(vs)
    check('voc.schema.yaml: метасхема 2020-12', True)
    ex = vs.get('examples') or []
    vv = Draft202012Validator(vs)
    for i, e in enumerate(ex):
        errs = errors(vv, e)
        check(f'voc.schema.yaml: examples[{i}] валиден', not errs, [f'{list(x.path)}: {x.message[:160]}' for x in errs[:6]])
        sn = {x['id'] for x in e.get('snippets', [])}
        th = {x['id'] for x in e.get('themes', [])}
        check(f'voc examples[{i}]: ссылки snippet↔theme существуют',
              all(s_ in sn for t in e.get('themes', []) for s_ in t['snippet_ids']) and all(t in th for x in e.get('snippets', []) for t in x.get('theme_ids', [])))
    if ex:
        vbase = ex[0]
        vnegs = {
            'источник без legal': lambda d: d['sources'][0].pop('legal'),
            'фрагмент длиннее 400 знаков': lambda d: d['snippets'][0].__setitem__('text', 'а' * 401),
            'тема без snippet_ids': lambda d: d['themes'][0].pop('snippet_ids'),
            'важность без метода': lambda d: d['themes'][0].__setitem__('importance', {'value': 3}),
            'неизвестная сила JTBD': lambda d: d['snippets'][0].__setitem__('force', 'fear'),
        }
        for name, fn in vnegs.items():
            d = copy.deepcopy(vbase)
            fn(d)
            check(f'voc отрицательный: {name} → ошибка', bool(errors(vv, d)))

print('validate:', 'OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
