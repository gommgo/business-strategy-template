#!/usr/bin/env python3
# M/10 — проверка 14-recipes/recipes/*.yaml: схема (jsonschema, venv-D2), существование файлов (doc, spec.example,
# spec.ancestors — примеры D и брифы E, sources — дайджесты и транскрипты роликов, задания, доказательства, шаблоны),
# коды задач таксономии, код маршрута в routing.yaml (v1; до поправки X2 24.09.2026 — routing.v0.yaml), ключи порогов в thresholds.yaml,
# цена шагов маршрута против калькулятора каталога polza (polza_catalog.py price, снимок «последний»).
# Сессия 5 (25.09.2026, агент Q): routing.yaml — v2 (агент U; коды маршрутов те же), снимок каталога «последний» — 2026-09-25_1411
# (id Flare — openai/gpt-image-2.5-flare); итог 17/17, 29 цен (+ шаг 1080p в hero-loop и видео по кадру в abstract-background).
import glob, json, os, re, subprocess, sys
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('ai-media'))
os.chdir(ROOT)
TAX = set('IMG-HERO-PHOTO IMG-PRODUCT IMG-ILLUSTR IMG-SERIES IMG-ICON3D IMG-CUTOUT IMG-BG-ABSTRACT IMG-TEXTURE IMG-TEXT-LATIN IMG-TEXT-CYR IMG-EDIT '
          'IMG-OUTPAINT IMG-MOCKUP IMG-UPSCALE IMG-DRAFT VID-HERO-LOOP VID-CINEMAGRAPH VID-I2V-PRODUCT VID-ABSTRACT VID-CAMERA VID-CHARACTER VID-LONG '
          'VID-V2V VID-ALPHA VID-SCROLL VID-UPSCALE VEC-ICON-LINE VEC-ICON-FILLED VEC-ILLUSTR VEC-PATTERN VEC-ANIM VEC-TRACE'.split())
routes = yaml.safe_load(open('13-routing-matrix/routing.yaml'))['routes']   # v2 (U, сессия 5); v1 — routing.v1.yaml, v0 заменена
th = yaml.safe_load(open('11-evaluation-qa/thresholds.yaml'))['thresholds']
def th_has(key):
    d = th
    for k in key.split('.'):
        if not isinstance(d, dict) or k not in d: return False
        d = d[k]
    return True
try:
    import jsonschema
    schema = json.load(open('14-recipes/recipes/recipe.schema.json')); V = jsonschema.Draft202012Validator(schema)
except ImportError:
    V = None
report, bad = [], 0
for p in sorted(glob.glob('14-recipes/recipes/*.yaml')):
    r = yaml.safe_load(open(p)); errs, warns, prices = [], [], []
    if V: errs += [f'схема: {e.message} @ {"/".join(map(str, e.path))}' for e in V.iter_errors(r)]
    if not os.path.exists(r['doc'].split('#')[0]): errs.append(f"нет doc {r['doc']}")
    for c in r.get('task_codes', []):
        if c not in TAX: errs.append(f'код вне таксономии: {c}')
    if r['route']['source'] not in routes: errs.append(f"маршрута {r['route']['source']} нет в routing.yaml")
    ex = (r.get('spec') or {}).get('example')
    if ex and not os.path.exists(ex): errs.append(f'нет spec.example {ex}')
    for a in (r.get('spec') or {}).get('ancestors', []):
        if not os.path.exists(a): errs.append(f'нет предка спецификации {a}')
    for src in r.get('sources', []):
        if not os.path.exists(src): errs.append(f'нет источника {src}')
    for j in (r.get('phase5') or {}).get('jobs', []):
        if not os.path.exists(j): errs.append(f'нет задания {j}')
    for s in r['steps']:
        ev = s.get('evidence')
        if ev and not os.path.exists(ev): errs.append(f"шаг {s['id']}: нет доказательства {ev}")
        for tool in re.findall(r'(?<![/\w-])99-raw/tools/[\w./-]+\.(?:py|sh)', s['cmd']):
            if not os.path.exists(tool): errs.append(f"шаг {s['id']}: нет утилиты {tool}")
    tpl = (r.get('delivery') or {}).get('template')
    if tpl and not os.path.exists(tpl): errs.append(f'нет шаблона {tpl}')
    for k in (r.get('accept') or {}).get('thresholds', []):
        if not th_has(k): errs.append(f'порога {k} нет в thresholds.yaml')
    for st in r['route']['steps']:
        m = st['model']
        if not re.fullmatch(r'[a-z0-9._-]+(/[a-z0-9._-]+)?', m) or 'channel' in st: continue
        args = [f'{k}={v}' for k, v in (st.get('params') or {}).items()]
        out = subprocess.run([sys.executable, str(kbpaths.scripts('ai-media', 'polza_catalog.py')), 'price', m, *args], capture_output=True, text=True)
        try:
            rub = json.loads(out.stdout)['rub']
        except Exception:
            warns.append(f'цена {m}: калькулятор не ответил ({(out.stderr or out.stdout)[-120:].strip()})'); continue
        prices.append((m, st['price_rub'], rub))
        if abs(rub - st['price_rub']) > 0.01: errs.append(f"цена {m} {args}: в рецепте {st['price_rub']}, каталог {rub}")
    bad += bool(errs)
    report.append({'file': p, 'ok': not errs, 'errors': errs, 'warnings': warns, 'prices_checked': len(prices)})
    print(('OK  ' if not errs else 'ERR ') + os.path.basename(p) + f' · цен сверено {len(prices)}' + ''.join(f'\n    - {e}' for e in errs + warns))
json.dump(report, open(str(kbpaths.out('ai-media', 'validate_recipes') / 'validate_report.json'), 'w'), ensure_ascii=False, indent=1)
print(f'итого: {len(report)} рецептов, с ошибками {bad}; валидатор схемы: {"jsonschema" if V else "нет (только ссылки)"}')
sys.exit(1 if bad else 0)
