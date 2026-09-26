#!/usr/bin/env python3
"""J/08: все проверки примеров 10-templates-recipes/examples/*.yaml в порядке E и I: claims_check.py --legal-category →
copy_lint.py → copydeck.py check → copydeck.py validate (+ validate библиотекой jsonschema из venv-J). JSON — в out/,
сводка — таблицей Markdown (для 02-examples-ru.md и 03-examples-en.md) и out/summary.json. Запуск из корня базы:
python3 99-raw/experiments/J/08-examples/run_checks.py [пример.yaml …] [--md out/table.md]"""
import json, os, subprocess, sys, time, yaml
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('text'))
EX = os.path.join(ROOT, '10-templates-recipes', 'examples')
OUT = str(kbpaths.out('text', 'run_checks'))
T = str(kbpaths.scripts('text'))
TODAY = '2026-09-24'
VENV = kbpaths.python()


def run(cmd):
    t = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return p.returncode, round(time.time() - t, 1), p


def counts(js, key='summary'):
    s = (js or {}).get(key) or {}
    return s.get('error', 0), s.get('warning', 0), s.get('info', 0)


def main(argv):
    md_out = None
    if '--md' in argv:
        i = argv.index('--md'); md_out = argv[i + 1]; argv = argv[:i] + argv[i + 2:]
    files = argv or sorted(os.path.join(EX, f) for f in os.listdir(EX) if f.endswith('.yaml'))
    os.makedirs(OUT, exist_ok=True)
    rows, summ = [], {}
    for path in files:
        name = os.path.splitext(os.path.basename(path))[0]
        deck = yaml.safe_load(open(path, encoding='utf-8'))['copy_deck']
        facts = os.path.normpath(os.path.join(os.path.dirname(path), deck['facts_ref']))
        cats = deck.get('legal_category') or ['general']
        cats = ','.join(cats if isinstance(cats, list) else [cats])
        r = {}
        j = os.path.join(OUT, f'{name}.claims.json')
        code, sec, _p = run([sys.executable, os.path.join(T, 'claims_check.py'), 'check', path, '--facts', facts, '--legal-category', cats,
                             '--today', TODAY, '--json', j, '--quiet'])
        r['claims'] = (code, sec, counts(json.load(open(j))) if os.path.exists(j) else None)
        j = os.path.join(OUT, f'{name}.lint.json')
        code, sec, p = run([sys.executable, os.path.join(T, 'copy_lint.py'), path, '--json'])
        try:
            lj = json.loads(p.stdout)
            open(j, 'w', encoding='utf-8').write(json.dumps(lj, ensure_ascii=False, indent=1))
            res = lj.get('results') or [{}]
            s = lj.get('summary') or (res[0] if isinstance(res, list) else res).get('summary') or {}
            r['lint'] = (code, sec, (s.get('error', 0), s.get('warning', 0), s.get('info', 0)))
        except Exception:  # noqa: BLE001
            r['lint'] = (code, sec, None)
        for cmd, key in (('check', 'check'), ('validate', 'validate')):
            j = os.path.join(OUT, f'{name}.{key}.json')
            code, sec, _p = run([sys.executable, os.path.join(T, 'copydeck.py'), cmd, path, '--today', TODAY, '--json', j, '--quiet'])
            r[key] = (code, sec, counts(json.load(open(j))) if os.path.exists(j) else None)
        if os.path.exists(VENV):
            j = os.path.join(OUT, f'{name}.validate-jsonschema.json')
            code, sec, _p = run([VENV, os.path.join(T, 'copydeck.py'), 'validate', path, '--today', TODAY, '--json', j, '--quiet'])
            r['jsonschema'] = (code, sec, counts(json.load(open(j))) if os.path.exists(j) else None)
        summ[name] = {k: {'exit': v[0], 'sec': v[1], 'error': (v[2] or (None,))[0], 'warning': (v[2] or (None, None))[1],
                          'info': (v[2] or (None, None, None))[2]} for k, v in r.items()}
        cell = lambda v: '—' if v[2] is None else f'{v[2][0]} / {v[2][1]} / {v[2][2]}'
        rows.append(f"| `{name}` | {cell(r['claims'])} | {cell(r['lint'])} | {cell(r['check'])} | {cell(r['validate'])} | "
                    f"{cell(r['jsonschema']) if 'jsonschema' in r else '—'} |")
        print(name, {k: (v[0], v[2]) for k, v in r.items()}, flush=True)
    head = ['| Пример | claims_check (error / warning / info) | copy_lint | copydeck check | copydeck validate | validate + jsonschema |',
            '|---|---|---|---|---|---|']
    table = '\n'.join(head + rows) + '\n'
    print(table)
    json.dump(summ, open(os.path.join(OUT, 'summary.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    if md_out:
        open(md_out, 'w', encoding='utf-8').write(table)
    return 0 if all(v['error'] in (0, None) for s in summ.values() for v in s.values()) else 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
