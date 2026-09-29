"""check_icons.py — проверка линейных SVG-иконок кодом, без глаз: нормы ui 07/01 и спецификация Lucide.

  python check_icons.py DIR [--ref DIR_LUCIDE] [--set lucide|НАБОР] [--json out.json] [--md out.md] [--title T]

Python окружения скилла, группа svg (svgelements, cairosvg — ему нужна системная libcairo2; numpy, scipy, scikit-image):
`scripts/install.sh --groups svg`; без пакетов — одна строка с этой командой и код 2.
Пороги откалиброваны на 20 иконках Lucide 1.47 + circle/square (вес 0,75–1,5, пик размытия 0,58–0,87, доля узлов
на целой сетке 23–100 %, смещение центра масс до 3,1 px у download): флаг ставится только за пределами этого коридора.
Проверки: шапка (viewBox 0 0 24 24, width/height 24, fill none, stroke currentColor, stroke-width 2, round cap/join),
нет жёстких цветов, поле ≥ 1 px (по растру 10×), доля узлов на целой сетке, центры дуг на сетке, число сегментов,
минимальный зазор между раздельными элементами (≥ 2 px), «узкие» участки фона < 2 px (приём Lucide с кругом ⌀2),
покрытие (вес) против эталонных circle/square Lucide, пик размытия (плотность), смещение центра масс,
IoU с одноимённой иконкой Lucide.
Набор (--set, по умолчанию lucide; у продукта — conventions.icons.set карты решений) задаёт уровень флага — поле levels
записи JSON: жёсткий цвет — брак (fail) у любого набора: перекраска через currentColor не работает; шапка и штрих Lucide
(24×24, stroke 2, round) — брак только у набора Lucide, у другого набора — предупреждение (warn): сверить шапку и штрих
со спецификацией набора, иконки под Lucide не подгонять; остальные флаги — предупреждения."""
import argparse, io, json, math, os, re, sys
try:
    import numpy as np
    from PIL import Image
    import cairosvg
    from scipy import ndimage
    from skimage.morphology import convex_hull_image  # noqa: F401 — narrow_background
    from svgelements import SVG, Shape, Path, Move, Close, Arc, Line, CubicBezier, QuadraticBezier, Circle, Ellipse, Rect
    DEPS_ERROR = None
except (ImportError, OSError) as e:   # OSError — cairocffi не нашёл системную libcairo2
    DEPS_ERROR = e

S_HI = 240  # 10× для геометрических замеров
HEADER_RULES = {
    'viewBox': '0 0 24 24', 'width': '24', 'height': '24', 'fill': 'none', 'stroke': 'currentColor',
    'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round'}
COLOR_RE = re.compile(r'#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(|\b(?:black|white|red|blue|green|gray|grey)\b')
SHAPE_TAGS = ('path', 'circle', 'rect', 'line', 'polyline', 'polygon', 'ellipse')
LUCIDE = 'lucide'
HARD_FLAGS = {'цвет'}         # брак у любого набора
LUCIDE_FLAGS = {'шапка'}      # шапка и штрих Lucide — брак только у набора Lucide

def is_lucide(icon_set):
    """Набор Lucide (lucide, Lucide, lucide-static …): шапка и штрих Lucide для него — правило набора, а не совет."""
    return str(icon_set or LUCIDE).strip().lower().startswith(LUCIDE)

def flag_levels(flags, icon_set=LUCIDE):
    """Уровень каждого флага по набору: {первое слово флага: fail | warn}."""
    lucide = is_lucide(icon_set)
    keys = [f.split()[0] for f in flags]
    return {k: 'fail' if k in HARD_FLAGS or (lucide and k in LUCIDE_FLAGS) else 'warn' for k in keys}

def deps_hint(e):
    """Одна строка вместо трассировки: чего нет в окружении и чем поставить."""
    if isinstance(e, ImportError):
        return (f'нет пакета {e.name or "группы svg"} (группа svg: svgelements, cairosvg, scikit-image) — поставьте '
                '`scripts/install.sh --groups svg`')
    return 'нет системной libcairo2 для cairosvg — поставьте её пакетом ОС и `scripts/install.sh --groups svg`'

def render_alpha(svg_text, size):
    png = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=size, output_height=size)
    im = Image.open(io.BytesIO(png)).convert('RGBA')
    return np.asarray(im)[:, :, 3].astype(np.float32) / 255.0

def split_elements(svg_text):
    m = re.search(r'(<svg\b[^>]*>)(.*)</svg>', svg_text, re.S)
    head, body = m.group(1), m.group(2)
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    els = re.findall(r'<(?:%s)\b[^>]*/>' % '|'.join(SHAPE_TAGS), body)
    return head, els

def header_check(svg_text):
    head = re.search(r'<svg\b([^>]*)>', svg_text).group(1)
    bad = []
    for k, v in HEADER_RULES.items():
        mm = re.search(r'(?<![\w:-])' + re.escape(k) + r'="([^"]*)"', head)   # width — не хвост stroke-width
        if not mm or mm.group(1).strip() != v:
            bad.append(f'{k}={mm.group(1) if mm else "нет"}')
    body = svg_text[svg_text.find('>') + 1:]
    colors = COLOR_RE.findall(body) + COLOR_RE.findall(head.replace('currentColor', ''))
    return bad, colors

def geometry(path):
    svg = SVG.parse(path)
    pts, centers, nseg, kinds = [], [], 0, {}
    for el in svg.elements():
        if not isinstance(el, Shape):
            continue
        if isinstance(el, Circle) or isinstance(el, Ellipse):
            centers.append((el.cx, el.cy)); nseg += 4; kinds['circle'] = kinds.get('circle', 0) + 1
            pts += [(el.cx - el.rx, el.cy), (el.cx + el.rx, el.cy), (el.cx, el.cy - el.ry), (el.cx, el.cy + el.ry)]
            continue
        p = Path(el)
        for seg in p:
            if isinstance(seg, Move):
                pts.append((seg.end.x, seg.end.y)); continue
            if isinstance(seg, Close):
                continue
            nseg += 1
            kinds[type(seg).__name__] = kinds.get(type(seg).__name__, 0) + 1
            pts.append((seg.end.x, seg.end.y))
            if isinstance(seg, Arc):
                try:
                    centers.append((seg.center.x, seg.center.y))
                except Exception:
                    pass
    on = lambda v: abs(v - round(v)) < 0.011
    half = lambda v: abs(2 * v - round(2 * v)) < 0.021
    coords = [c for pt in pts for c in pt]
    ccoords = [c for pt in centers for c in pt]
    return {
        'segments': nseg, 'kinds': kinds, 'points': len(pts),
        'grid_int_pct': round(100 * sum(on(c) for c in coords) / max(len(coords), 1), 1),
        'grid_half_pct': round(100 * sum(half(c) for c in coords) / max(len(coords), 1), 1),
        'arc_centers': len(centers),
        'arc_centers_int_pct': round(100 * sum(on(c) for c in ccoords) / max(len(ccoords), 1), 1) if ccoords else None,
    }

def min_gap(head, els):
    """Минимальный видимый зазор между раздельными элементами. Пиксели, закрытые третьими элементами, не считаются
    (иначе два элемента, соединённые через третий — ручка и стенка корзины через крышку, — дают ложный зазор)."""
    if len(els) < 2:
        return None
    masks = [render_alpha(head + e + '</svg>', S_HI) > 0.5 for e in els]
    best = None
    for i in range(len(masks)):
        for j in range(i + 1, len(masks)):
            others = np.zeros_like(masks[0])
            for k in range(len(masks)):
                if k not in (i, j):
                    others |= masks[k]
            a, b = masks[i] & ~others, masks[j] & ~others
            if not a.any() or not b.any():
                continue
            # если a и b соединены внутри объединения всех элементов — это одна фигура, зазора нет
            union = masks[i] | masks[j] | others
            lab, _ = ndimage.label(union)
            la = set(np.unique(lab[a])) - {0}; lb = set(np.unique(lab[b])) - {0}
            touching = ndimage.distance_transform_edt(~masks[j])[masks[i]].min() <= 1.5
            if touching:
                continue
            dist_to_b = ndimage.distance_transform_edt(~b)
            d = dist_to_b[a].min() / 10.0  # в пикселях иконки
            if d <= 0.15:  # элементы соединены намеренно
                continue
            best = d if best is None else min(best, d)
    return None if best is None else round(best, 2)

def narrow_background(alpha_hi):
    """Площадь фона уже 2 px (круг ⌀2 не проходит) внутри выпуклой оболочки рисунка, в px² иконки."""
    from skimage.morphology import convex_hull_image
    ink = alpha_hi > 0.5
    bg = ~ink
    if not ink.any():
        return 0.0
    box = convex_hull_image(ink)
    r = 9  # круг ⌀ ≈ 1,9 px иконки на 10× (допуск на сглаживание: канал ровно 2 px проходит)
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (xx ** 2 + yy ** 2) <= r * r
    opened = ndimage.binary_opening(bg, structure=disk)
    narrow = bg & ~opened & box
    # отбросить «углы»: оставить только компоненты площадью ≥ 0,3 px² иконки (30 px на 10×)
    lab, n = ndimage.label(narrow)
    if n == 0:
        return 0.0
    sizes = ndimage.sum(narrow, lab, range(1, n + 1))
    return round(float(sizes[sizes >= 30].sum()) / 100.0, 2)

def raster_metrics(svg_text):
    a24 = render_alpha(svg_text, 24)
    a16 = render_alpha(svg_text, 16)
    hi = render_alpha(svg_text, S_HI)
    ink = hi > 0.02
    ys, xs = np.where(ink)
    margin = min(xs.min(), ys.min(), S_HI - 1 - xs.max(), S_HI - 1 - ys.max()) / 10.0 if len(xs) else None
    yy, xx = np.mgrid[0:S_HI, 0:S_HI]
    w = hi.sum()
    cx = (xx * hi).sum() / w / 10.0; cy = (yy * hi).sum() / w / 10.0
    blur = ndimage.gaussian_filter(a24, sigma=1.2)
    return {
        'cover24': round(float(a24.mean()), 4), 'cover16': round(float(a16.mean()), 4),
        'blur_peak': round(float(blur.max()), 3),
        'margin_px': round(float(margin), 2) if margin is not None else None,
        'bbox_px': [round(xs.min() / 10, 1), round(ys.min() / 10, 1), round((xs.max() + 1) / 10, 1), round((ys.max() + 1) / 10, 1)] if len(xs) else None,
        'centroid_off': round(math.hypot(cx - 12, cy - 12), 2),
        'narrow_bg_px2': narrow_background(hi),
        '_mask': hi > 0.5,
    }

def iou(a, b):
    return round(float((a & b).sum()) / max(float((a | b).sum()), 1), 3)

def check_dir(d, ref=None, icon_set=LUCIDE):
    if DEPS_ERROR is not None:
        raise ImportError(deps_hint(DEPS_ERROR))
    ref_cover = None
    if ref:
        rc = raster_metrics(open(os.path.join(ref, 'circle.svg')).read())
        rs = raster_metrics(open(os.path.join(ref, 'square.svg')).read())
        ref_cover = (rc['cover24'] + rs['cover24']) / 2
    out = {}
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.svg'):
            continue
        p = os.path.join(d, fn); name = fn[:-4]
        txt = open(p).read()
        bad, colors = header_check(txt)
        head, els = split_elements(txt)
        g = geometry(p)
        r = raster_metrics(txt)
        rec = {'bytes': len(txt.encode()), 'elements': len(els), 'header_bad': bad, 'hard_colors': colors, **g,
               **{k: v for k, v in r.items() if not k.startswith('_')}, 'min_gap_px': min_gap(head, els)}
        if ref_cover:
            rec['weight_vs_circle_square'] = round(r['cover24'] / ref_cover, 2)
        if ref and os.path.exists(os.path.join(ref, fn)):
            rr = raster_metrics(open(os.path.join(ref, fn)).read())
            rec['iou_vs_lucide'] = iou(r['_mask'], rr['_mask'])
            rec['cover24_lucide'] = rr['cover24']
            rec['blur_peak_lucide'] = rr['blur_peak']
        flags = []
        if bad: flags.append('шапка')
        if colors: flags.append('цвет')
        if r['margin_px'] is not None and r['margin_px'] < 0.95: flags.append('поле<1')
        if rec['min_gap_px'] is not None and rec['min_gap_px'] < 1.9: flags.append(f"зазор {rec['min_gap_px']}")
        if r['narrow_bg_px2'] > 3.0: flags.append(f"узко {r['narrow_bg_px2']}")
        if ref_cover and not (0.7 <= rec['weight_vs_circle_square'] <= 1.55): flags.append(f"вес {rec['weight_vs_circle_square']}")
        if r['centroid_off'] > 1.6: flags.append(f"центр {r['centroid_off']}")
        if g['grid_int_pct'] < 30: flags.append(f"сетка {g['grid_int_pct']}%")
        rec['flags'] = flags
        rec['set'] = icon_set
        rec['levels'] = flag_levels(flags, icon_set)
        out[name] = rec
    return out

def flags_md(r):
    """Флаги для таблицы: брак помечен, шапка другого набора — предупреждение с советом."""
    lv = r.get('levels') or {}
    out = []
    for f in r['flags']:
        k = f.split()[0]
        if lv.get(k) == 'fail':
            f += ' (брак)'
        elif k in LUCIDE_FLAGS:
            f += f" (правило Lucide; у набора «{r.get('set')}» — предупреждение: сверить со спецификацией набора)"
        out.append(f)
    return ', '.join(out) or 'ок'

def to_md(res, title):
    cols = ['bytes', 'elements', 'segments', 'grid_int_pct', 'margin_px', 'min_gap_px', 'narrow_bg_px2', 'cover24',
            'weight_vs_circle_square', 'blur_peak', 'centroid_off', 'iou_vs_lucide', 'flags']
    lines = [f'### {title}', '', '| иконка | ' + ' | '.join(cols) + ' |', '|' + '---|' * (len(cols) + 1)]
    for n, r in res.items():
        lines.append(f'| {n} | ' + ' | '.join(str(r.get(c, '')) if c != 'flags' else flags_md(r) for c in cols) + ' |')
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('dir', help='папка с SVG-иконками')
    ap.add_argument('--ref', help='эталоны Lucide (circle.svg, square.svg и одноимённые иконки): вес и IoU')
    ap.add_argument('--set', default=LUCIDE, metavar='НАБОР',
                    help='набор иконок продукта (conventions.icons.set), по умолчанию lucide: шапка и штрих Lucide — брак '
                         'только у набора Lucide')
    ap.add_argument('--json', help='записи по иконкам: замеры, flags, levels')
    ap.add_argument('--md', help='таблица Markdown в файл (в stdout она печатается всегда)')
    ap.add_argument('--title', default='', help='заголовок таблицы (по умолчанию — папка)')
    a = ap.parse_args()
    if DEPS_ERROR is not None:   # одна строка вместо трассировки, код 2 — окружение
        print(f'check_icons.py: {deps_hint(DEPS_ERROR)}', file=sys.stderr)
        sys.exit(2)
    res = check_dir(a.dir, a.ref, a.set)
    if a.json:
        json.dump(res, open(a.json, 'w'), ensure_ascii=False, indent=1)
    md = to_md(res, a.title or a.dir)
    if a.md:
        open(a.md, 'w').write(md)
    print(md)
