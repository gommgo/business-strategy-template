#!/usr/bin/env python3
"""kit/diffshots.py — «изменилось только то, что просили»: сравнение двух снимков shot.py по меткам #N.

Агент D базы claude-design-research, 2026-09-25, v2. Браузер не нужен: читает marks.json и кадры без меток двух папок.

Использование:
  python3 diffshots.py <папка до> <папка после> [--expect 16,22,38 | --expect all] [--tolerance 0.01] [--strict]
  --expect all — для правки токенов («применить ко всему»): отчёт = какие метки задело.

Два уровня сигнала для каждой метки в каждом кадре (ширина × тема):
  1. DOM (точно, без шума): sh — вычисленные стили самой метки; own — текст и стили её непомеченных потомков (абзацы, подписи).
     Отличие = «метка изменилась сама» (self).
  2. Пиксели (вторично): вырез метки до и после с допуском ±1 px по размеру, дробным сдвигом по вертикали (шаг 0,25 px),
     размытием 3×3 и долей отличий --tolerance. Отличие без self у метки, её потомков и предков — дробный сдвиг раскладки (шум).
Итог: same · moved (сдвиг раскладки) · changed (self или картинка, объяснённая правкой внутри/снаружи) · added · removed.
Почему: «просили» (номер в --expect), «внутри правки» (предок в --expect), «содержит правку» (правка у потомка), «от контейнера»
(правка у предка, например фон), «НЕОЖИДАННО» — метка изменилась сама, а её не просили и она не внутри просьбы.
Пишет <папка после>/diff.json и diff.md. Код выхода: 0; 5 — --strict и есть неожиданные изменения.
"""
import argparse, json, os, sys

import numpy as np
from PIL import Image


def load(d):
    m = json.load(open(os.path.join(d, 'marks.json'), encoding='utf-8'))
    frames = {f['id']: f for f in m.get('frames', [])}
    marks = {(x['file'], x['n']): x for x in m.get('marks', [])}
    return m, frames, marks


def crop(img, r):
    x, y, w, h = r['x'], r['y'], r['w'], r['h']
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(img.width, x + w), min(img.height, y + h)
    if x1 <= x0 or y1 <= y0:
        return None
    return np.asarray(img.crop((x0, y0, x1, y1)).convert('RGB'), dtype=np.int16)


def _blur(g):
    p = np.pad(g, 1, mode='edge')
    return sum(p[dy:dy + g.shape[0], dx:dx + g.shape[1]] for dy in range(3) for dx in range(3)) / 9.0


def pixel_share(a, b, shift=1):
    """Доля отличающихся пикселей (после размытия и лучшего дробного сдвига); 1.0 — размеры разные или выреза нет."""
    if a is None or b is None or abs(a.shape[0] - b.shape[0]) > 1 or abs(a.shape[1] - b.shape[1]) > 1:
        return 1.0
    h, w = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    ga, gb = _blur(a[:h, :w].mean(axis=2)), _blur(b[:h, :w].mean(axis=2))
    m = shift + 1
    if h <= 2 * m + 2 or w <= 2 * shift + 2:
        d = np.abs(ga - gb) > 24
        return float(d.mean()) if d.size else 0.0
    core = ga[m:h - m, shift:w - shift]
    best = 1.0
    for sy in np.arange(-shift, shift + 0.001, 0.25):
        k = int(np.floor(sy)); f = sy - k
        r0, r1 = gb[m + k:h - m + k], gb[m + k + 1:h - m + k + 1]
        if r0.shape[0] != core.shape[0] or r1.shape[0] != core.shape[0]:
            continue
        shifted = (1 - f) * r0 + f * r1
        for dx in range(-shift, shift + 1):
            d = np.abs(core - shifted[:, shift + dx:w - shift + dx]) > 24
            best = min(best, float(d.mean()) if d.size else 0.0)
            if best == 0.0:
                return 0.0
    return best


def chain(marks, file, n):
    out, seen = [], set()
    cur = marks.get((file, n))
    while cur and cur.get('parent') and cur['parent'] not in seen:
        seen.add(cur['parent']); out.append(cur['parent'])
        cur = marks.get((file, cur['parent']))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('before'); ap.add_argument('after')
    ap.add_argument('--expect', default='', help='номера, которые просили изменить: "16,22,38"')
    ap.add_argument('--tolerance', type=float, default=0.01, help='доля отличающихся пикселей (после размытия), которую считаем шумом')
    ap.add_argument('--strict', action='store_true')
    a = ap.parse_args()
    expect_all = a.expect.strip().lower() == 'all'           # правка токена: отчёт = список затронутых меток
    expect = set() if expect_all else {int(x) for x in a.expect.replace(' ', '').split(',') if x and x != '0'}
    _, f0, k0 = load(a.before)
    _, f1, k1 = load(a.after)
    report = {'before': os.path.abspath(a.before), 'after': os.path.abspath(a.after), 'expect': sorted(expect),
              'frames': [], 'unexpected_total': 0}
    for fid in [x for x in f1 if x in f0]:
        file = fid.split('@')[0]
        p0, p1 = f0[fid].get('png'), f1[fid].get('png')
        if not (p0 and p1 and os.path.exists(p0) and os.path.exists(p1)):
            report['frames'].append({'id': fid, 'error': 'нет кадров без меток (shot.py без --no-plain)'})
            continue
        img0, img1 = Image.open(p0), Image.open(p1)
        whole_same = img0.size == img1.size and not (np.abs(np.asarray(img0.convert('RGB'), dtype=np.int16) -
                                                            np.asarray(img1.convert('RGB'), dtype=np.int16)).max(axis=2) > 16).any()
        nums = sorted({n for (f, n) in list(k0) + list(k1) if f == file})
        info = {}
        for n in nums:
            a0, a1 = k0.get((file, n)), k1.get((file, n))
            r0 = a0 and a0['frames'].get(fid)
            r1 = a1 and a1['frames'].get(fid)
            v0, v1 = bool(r0 and r0.get('visible')), bool(r1 and r1.get('visible'))
            if not v0 and not v1:
                continue
            rec = {'n': n, 'kind': (a1 or a0)['kind'], 'text': (a1 or a0)['text'][:48], 'from': r0['rect'] if v0 else None,
                   'to': r1['rect'] if v1 else None, 'self': [], 'pixels_changed': None}
            if v0 and not v1:
                rec['status'] = 'removed'
            elif v1 and not v0:
                rec['status'] = 'added'
            else:
                if r0.get('sh') and r1.get('sh') and r0['sh'] != r1['sh']:
                    rec['self'].append('стиль')
                if r0.get('own') and r1.get('own') and r0['own'] != r1['own']:
                    rec['self'].append('содержимое')
                share = pixel_share(crop(img0, r0['rect']), crop(img1, r1['rect']))
                rec['pixels_changed'] = round(share, 4)
                moved = abs(r0['rect']['x'] - r1['rect']['x']) > 1 or abs(r0['rect']['y'] - r1['rect']['y']) > 1
                resized = abs(r0['rect']['w'] - r1['rect']['w']) > 1 or abs(r0['rect']['h'] - r1['rect']['h']) > 1
                if rec['self'] or resized or share > a.tolerance:
                    rec['status'] = 'changed'
                else:
                    rec['status'] = 'moved' if moved else 'same'
            info[n] = rec
        kmap = {**k0, **k1}
        self_set = {n for n, r in info.items() if r['self'] or r['status'] in ('added', 'removed')}
        for n, r in info.items():
            anc = chain(kmap, file, n)
            desc = [m for m in info if m != n and n in chain(kmap, file, m)]
            r['why'] = ''
            if r['status'] in ('same', 'moved'):
                continue
            if expect_all or n in expect:
                r['why'] = 'просили'
            elif any(x in expect for x in anc):
                r['why'] = 'внутри правки'
            elif r['self'] or r['status'] in ('added', 'removed'):
                r['why'] = 'НЕОЖИДАННО'                    # метка изменилась сама (стиль, содержимое, появилась, исчезла)
            elif any(m in self_set for m in desc):
                r['why'] = 'содержит правку'               # картинка поменялась из-за правки у потомка
            elif any(x in self_set for x in anc):
                r['why'] = 'от контейнера'                 # фон или стиль предка
            else:                                          # только пиксели, DOM нигде не менялся — дробный сдвиг раскладки
                mv = r['from'] and r['to'] and abs(r['from']['y'] - r['to']['y']) > 1
                r['status'], r['why'] = ('moved' if mv else 'same'), ''
        rows = [info[n] for n in sorted(info)]
        unexpected = [r for r in rows if r['why'] == 'НЕОЖИДАННО']
        report['unexpected_total'] += len(unexpected)
        report['frames'].append({'id': fid, 'identical': whole_same, 'size_before': list(img0.size), 'size_after': list(img1.size),
                                 'changed': [r['n'] for r in rows if r['status'] == 'changed'],
                                 'moved': [r['n'] for r in rows if r['status'] == 'moved'],
                                 'added': [r['n'] for r in rows if r['status'] == 'added'],
                                 'removed': [r['n'] for r in rows if r['status'] == 'removed'],
                                 'unexpected': [r['n'] for r in unexpected], 'rows': rows})
    json.dump(report, open(os.path.join(a.after, 'diff.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    lines = [f"# Разница снимков: {os.path.basename(os.path.normpath(a.before))} → {os.path.basename(os.path.normpath(a.after))}",
             '', f"Просили: {', '.join('#' + str(n) for n in sorted(expect)) or '—'} · неожиданных изменений: {report['unexpected_total']}", '']
    for fr in report['frames']:
        if 'error' in fr:
            lines += [f"## {fr['id']}: {fr['error']}", '']
            continue
        lines += [f"## {fr['id']} · {'кадр не изменился' if fr['identical'] else 'кадр изменился'} · "
                  f"{fr['size_before'][0]}×{fr['size_before'][1]} → {fr['size_after'][0]}×{fr['size_after'][1]}", '',
                  f"изменились: {fr['changed'] or '—'} · сдвинулись: {fr['moved'] or '—'} · новые: {fr['added'] or '—'} · "
                  f"исчезли: {fr['removed'] or '—'} · **неожиданно: {fr['unexpected'] or '—'}**", '']
        rows = [r for r in fr['rows'] if r['status'] not in ('same', 'moved')]
        if rows:
            lines += ['| # | вид | текст | итог | что внутри | почему |', '|---|---|---|---|---|---|']
            for r in rows:
                lines.append(f"| {r['n']} | {r['kind']} | {r['text']} | {r['status']} | {', '.join(r['self']) or 'картинка'} | {r['why']} |")
            lines.append('')
    open(os.path.join(a.after, 'diff.md'), 'w', encoding='utf-8').write('\n'.join(lines))
    print(json.dumps({'unexpected_total': report['unexpected_total'],
                      'frames': [{k: fr.get(k) for k in ('id', 'identical', 'changed', 'moved', 'added', 'removed', 'unexpected')}
                                 for fr in report['frames']]}, ensure_ascii=False, indent=1))
    return 5 if (a.strict and report['unexpected_total']) else 0


if __name__ == '__main__':
    sys.exit(main())
