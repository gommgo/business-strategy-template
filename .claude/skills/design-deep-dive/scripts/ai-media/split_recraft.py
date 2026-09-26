#!/usr/bin/env python3
"""B/14 (сессия 4, 25.09.2026) — нарезка сетки иконок Recraft (CM-01 icons Pro, агент A) на отдельные SVG для лендинга.
Фон-прямоугольник (путь на весь холст) удаляется; пути группируются по пересечению рамок (+ отступ), группа → свой SVG с
viewBox по рамке группы; сюжет группы — по ближайшему центру к раскладке брифа. Тяжёлый манифест C2PA из <metadata> в каждую
иконку не копируется (подпись производной всё равно недействительна): мастер с манифестом лежит рядом в _source/, в каждой
иконке — комментарий о происхождении. Затем svgo (preset-default). Окружение — 99-raw/tools/venv-G (svgelements).
Запуск: 99-raw/tools/venv-G/bin/python split_recraft.py SRC.svg OUT_DIR"""
import os, re, shutil, subprocess, sys
from svgelements import SVG, Path

LAYOUT = {  # центр иконки на рендере 1600×914 брифа CM-01 → слот этапа (масштаб к исходнику 2688×1536 = ×1,68)
    'plan': (610, 190), 'pregnancy': (980, 180), 'postpartum': (250, 465), 'burnout': (620, 450),
    'loss': (990, 455), 'partner': (1350, 460), 'menopause': (612, 732), 'relations': (987, 730)}
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
SVGO = str(kbpaths.node_modules('.bin', 'svgo'))


def main(src, out):
    os.makedirs(f'{out}/_source', exist_ok=True)
    shutil.copy2(src, f'{out}/_source/{os.path.basename(src)}')
    raw = open(src).read()
    vb = [float(x) for x in re.search(r'viewBox="([^"]+)"', raw).group(1).split()]
    W, H = vb[2], vb[3]
    tags = re.findall(r'<path\b[^>]*/>', raw)
    doc = SVG.parse(src)
    paths = [e for e in doc.elements() if isinstance(e, Path)]
    assert len(paths) == len(tags), (len(paths), len(tags))
    boxes = []
    for p, t in zip(paths, tags):
        bb = p.bbox()
        if bb is None: continue
        x0, y0, x1, y1 = bb
        if (x1 - x0) > 0.9 * W and (y1 - y0) > 0.9 * H: continue          # фон-прямоугольник
        boxes.append([x0, y0, x1, y1, t])
    # объединение по пересечению рамок с отступом
    m = 60; parent = list(range(len(boxes)))
    def find(i):
        while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            a, b = boxes[i], boxes[j]
            if a[0] - m <= b[2] and b[0] - m <= a[2] and a[1] - m <= b[3] and b[1] - m <= a[3]:
                parent[find(i)] = find(j)
    groups = {}
    for i, b in enumerate(boxes): groups.setdefault(find(i), []).append(b)
    k = W / 1600
    used = set()
    for g in groups.values():
        x0 = min(b[0] for b in g); y0 = min(b[1] for b in g); x1 = max(b[2] for b in g); y1 = max(b[3] for b in g)
        cx, cy = (x0 + x1) / 2 / k, (y0 + y1) / 2 / k
        slug = min(LAYOUT, key=lambda s: (LAYOUT[s][0] - cx) ** 2 + (LAYOUT[s][1] - cy) ** 2)
        if slug in used: slug += '-2'
        used.add(slug)
        side = max(x1 - x0, y1 - y0) * 1.12; mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{mx - side / 2:.1f} {my - side / 2:.1f} {side:.1f} {side:.1f}">'
               f'<desc>Recraft V4.1 Pro Vector (RouterAI), CM-01 агента A, 25.09.2026; ИИ-генерация (trainedAlgorithmicMedia); '
               f'иконка «{slug}» нарезана из сетки (B/14 split_recraft.py); мастер с манифестом C2PA — _source/</desc>' + ''.join(b[4] for b in g) + '</svg>\n')
        fn = f'{out}/stage-{slug}.svg'; open(fn, 'w').write(svg)
        before = os.path.getsize(fn)
        subprocess.run([SVGO, fn, '-o', fn, '--multipass', '-q'], check=False)
        print(slug, len(g), 'путей', f'{before} → {os.path.getsize(fn)} Б', f'центр {cx:.0f},{cy:.0f}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
