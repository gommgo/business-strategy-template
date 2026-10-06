#!/usr/bin/env python3
"""Обслуживание базы: этапы не зовут. channel_diff.py — разница двух снимков каталогов RouterAI и Gen-API (дополнение
к polza_catalog.py diff).

Запуск: python3 channel_diff.py [--ra A B] [--ga A B]  (имена папок снимков в $DDD_HOME/cache/ai-media/routerai и
$DDD_HOME/cache/ai-media/genapi; по умолчанию два последних)
Печатает Markdown: новые и удалённые модели (у RouterAI — только image/video по output_modalities), изменения цены
картинки/видео > 0,1 %, изменения supported_parameters; у Gen-API — новые/удалённые сети и изменения cost.
"""
import argparse, json, pathlib
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib')); import kbpaths  # scripts/lib: kbpaths
CACHE = kbpaths.cache('ai-media')

def last_two(sub, fname):
    ds = sorted(d for d in (CACHE / sub).iterdir() if (d / fname).exists())
    return ds[-2].name, ds[-1].name

def ra_load(name):
    d = json.loads((CACHE / 'routerai' / name / 'api-v1-models.json').read_text())
    return {m['id']: m for m in (d.get('data', d) if isinstance(d, dict) else d)}

def media(m):
    return any(x in ('image', 'video') for x in (m.get('architecture') or {}).get('output_modalities') or [])

def price(m):
    ip = (m.get('image_pricing') or [{}])
    ip = ip[0] if ip else {}
    return (ip.get('unit'), float(ip['price'])) if ip.get('price') is not None else (None, None)

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument('--ra', nargs=2)
ap.add_argument('--ga', nargs=2)
a = ap.parse_args()
ra_a, ra_b = a.ra or last_two('routerai', 'api-v1-models.json')
A, B = ra_load(ra_a), ra_load(ra_b)
print(f'# RouterAI: {ra_a} → {ra_b}\n')
new = [k for k in B if k not in A]
gone = [k for k in A if k not in B]
print(f'- новые (всего {len(new)}): ' + ', '.join(f'`{k}`' + (' (медиа)' if media(B[k]) else '') for k in sorted(new)))
print(f'- удалённые (всего {len(gone)}): ' + ', '.join(f'`{k}`' for k in sorted(gone)))
print('\n| Модель (медиа) | Было ₽ | Стало ₽ | Δ % | Параметры изменились |\n|---|---|---|---|---|')
ratios = []
for k in sorted(set(A) & set(B)):
    if not media(B[k]):
        continue
    (ua, pa), (ub, pb) = price(A[k]), price(B[k])
    sp_a, sp_b = set(A[k].get('supported_parameters') or []), set(B[k].get('supported_parameters') or [])
    if pa and pb and abs(pb / pa - 1) > 0.001:
        ratios.append(pb / pa)
    if (pa and pb and abs(pb / pa - 1) > 0.01) or sp_a != sp_b or ua != ub:
        d = f'{(pb / pa - 1) * 100:+.2f}' if pa and pb else '—'
        print(f'| `{k}` | {pa} | {pb} | {d} | {sorted(sp_b ^ sp_a) or ""} |')
if ratios:
    ratios.sort()
    print(f'\nСдвиг цен медиа-моделей > 0,1 %: {len(ratios)} моделей, медиана {(ratios[len(ratios)//2] - 1) * 100:+.2f} % '
          f'(мин {(ratios[0] - 1) * 100:+.2f}, макс {(ratios[-1] - 1) * 100:+.2f}) — курс, а не решение вендора, если сдвиг одинаков.')
ga_a, ga_b = a.ga or last_two('genapi', 'networks-include-parameters.json')
ga = lambda n: {x['slug']: x for x in json.loads((CACHE / 'genapi' / n / 'networks-include-parameters.json').read_text())['data']}
GA, GB = ga(ga_a), ga(ga_b)
print(f'\n# Gen-API: {ga_a} → {ga_b}\n')
print('- новые сети: ' + ', '.join(f'`{k}`' for k in sorted(set(GB) - set(GA))))
print('- удалённые сети: ' + ', '.join(f'`{k}`' for k in sorted(set(GA) - set(GB))))
ch = [(k, GA[k].get('cost'), GB[k].get('cost')) for k in sorted(set(GA) & set(GB)) if GA[k].get('cost') != GB[k].get('cost')]
print(f'- изменения cost: {len(ch)}' + (': ' + ', '.join(f'`{k}` {x} → {y}' for k, x, y in ch) if ch else ''))
