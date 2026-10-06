#!/usr/bin/env python3
# Проверка вёрстки текстового шаблона по DOM (до OCR): прямоугольники строк текста (Range.getClientRects) не выходят
# за холст и не заходят на непрозрачную часть товара (рамка альфы выреза, не рамка <img>), нет переполнения блоков и нет
# nowrap-элементов, ставших отдельными флекс-элементами; плюс рендер «только текст» (товар скрыт) — вход OCR без склейки
# строк колонки с этикеткой товара.
#   шаблон карточки: python3 layout_check.py ШАБЛОН.html ВЫРЕЗ.png — товар в шаблоне — элемент .tin, вырез — его PNG с альфой
#   страница целиком: python3 layout_check.py page ФАЙЛ.html [1440x900 412x915] (переполнения, nowrap-флекс; строки за
#   холстом по высоте — это прокрутка, считаются только выходы по ширине)
# Выходы — $DDD_HOME/out/ai-media/layout_check/ (results_layout*.json, слой текста marketplace_textlayer.png). Браузер
# работает под общим замком kbpaths.lock('browser'): утилита берёт его сама (реентерабельно по дереву процессов).
# Вариант «before» шаблона карточки — подпись без обёртки, nowrap-«1–2 дня» отдельным флекс-элементом; строится, когда
# шаблон содержит эти подписи. Код 2 — нет входного файла.
import json, os
from PIL import Image
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, os.path.join(HERE, "..", "lib")); import kbpaths  # scripts/lib: kbpaths
OUT = str(kbpaths.out("ai-media", "layout_check"))
JS = r"""() => {
  const W = document.documentElement.clientWidth, H = document.documentElement.clientHeight;
  const lines = [], overflow = [], nowrapFlex = [];
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = tw.nextNode())) {
    if (!n.textContent.trim()) continue;
    const r = document.createRange(); r.selectNodeContents(n);
    for (const b of r.getClientRects()) {
      if (b.width < 1 || b.height < 1) continue;
      lines.push({text: n.textContent.trim().slice(0, 40), x0: b.left, y0: b.top, x1: b.right, y1: b.bottom});
    }
  }
  for (const e of document.querySelectorAll('li, span, div, h1, h2, p')) {
    if (e.clientWidth > 0 && e.scrollWidth > e.clientWidth + 1)
      overflow.push({tag: e.tagName, cls: String(e.className), sw: e.scrollWidth, cw: e.clientWidth, text: e.textContent.trim().slice(0, 40)});
    const par = e.parentElement;
    if (par && getComputedStyle(par).display.includes('flex') && getComputedStyle(e).whiteSpace === 'nowrap')
      nowrapFlex.push({tag: e.tagName, text: e.textContent.trim()});
  }
  const t = document.querySelector('.tin'); const tr = t ? t.getBoundingClientRect() : null;
  return {W, H, lines, overflow, nowrapFlex,
          tin: t ? {x0: tr.left, y0: tr.top, w: tr.width, h: tr.height, nw: t.naturalWidth, nh: t.naturalHeight} : null};
}"""

def opaque_box(tin, png):
    a = Image.open(png).getchannel('A').point(lambda v: 255 if v > 16 else 0)
    bx = a.getbbox()                        # непрозрачная часть выреза в пикселях файла
    sx, sy = tin['w'] / tin['nw'], tin['h'] / tin['nh']
    return (tin['x0'] + bx[0] * sx, tin['y0'] + bx[1] * sy, tin['x0'] + bx[2] * sx, tin['y0'] + bx[3] * sy)

def analyse(r, png):
    P = opaque_box(r['tin'], png) if r['tin'] else (0, 0, 0, 0)
    hits = [dict(L, overlap_px=round((min(L['x1'], P[2]) - max(L['x0'], P[0])) * (min(L['y1'], P[3]) - max(L['y0'], P[1]))))
            for L in r['lines'] if min(L['x1'], P[2]) > max(L['x0'], P[0]) and min(L['y1'], P[3]) > max(L['y0'], P[1])]
    outside = [L for L in r['lines'] if L['x0'] < 0 or L['y0'] < 0 or L['x1'] > r['W'] or L['y1'] > r['H']]
    bad = hits or outside or r['overflow'] or r['nowrapFlex']
    rnd = lambda L: {k: (round(v) if isinstance(v, float) else v) for k, v in L.items()}
    return {'verdict': 'fail' if bad else 'pass', 'product_box': [round(v) for v in P], 'n_line_boxes': len(r['lines']),
            'hits': [rnd(h) for h in hits], 'outside': [rnd(o) for o in outside], 'overflow': r['overflow'], 'nowrap_flex_items': r['nowrapFlex']}

def main(tpl, cutout):
    src = open(tpl, encoding='utf-8').read()
    before = (src.replace('</svg><span>Обжарка раз в&nbsp;неделю</span></li>', '</svg>Обжарка раз в&nbsp;неделю</li>')
                 .replace('</svg><span>Средняя обжарка: орех и&nbsp;какао</span></li>', '</svg>Средняя обжарка: орех и&nbsp;какао</li>')
                 .replace('</svg><span>Доставка за <span style="white-space:nowrap">1–2&nbsp;дня</span></span></li>',
                          '</svg>Доставка за <span style="white-space:nowrap">1–2 дня</span></li>'))
    bpath = os.path.join(os.path.dirname(os.path.abspath(tpl)), '_before.html')   # рядом с шаблоном: те же ссылки
    variants = ([('before', bpath)] if before != src else []) + [('after', os.path.abspath(tpl))]
    if before != src:
        open(bpath, 'w', encoding='utf-8').write(before)
    res = {}
    try:
        with kbpaths.lock('browser'), sync_playwright() as p:
            b = p.chromium.launch(channel='chromium', headless=True)
            for name, path in variants:
                pg = b.new_page(viewport={'width': 900, 'height': 1200}, device_scale_factor=1)
                pg.goto('file://' + path); pg.wait_for_timeout(500)
                res[name] = analyse(pg.evaluate(JS), cutout)
                if name == 'after':   # слой текста без товара — вход OCR
                    pg.add_style_tag(content='.tin{visibility:hidden}')
                    pg.screenshot(path=os.path.join(OUT, 'marketplace_textlayer.png'))
                pg.close()
            b.close()
    finally:
        if os.path.exists(bpath):
            os.remove(bpath)
    json.dump(res, open(os.path.join(OUT, 'results_layout.json'), 'w'), ensure_ascii=False, indent=1)
    for k, v in res.items():
        print(k, v['verdict'], '| товар', v['product_box'], '| пересечений', len(v['hits']), '| за холстом', len(v['outside']),
              '| переполнений', len(v['overflow']), '| nowrap-флекс', len(v['nowrap_flex_items']))
        for h in v['hits'][:4]: print('   hit', h)
        for o in v['overflow'][:4]: print('   overflow', o)
        for o in v['nowrap_flex_items'][:4]: print('   nowrap-flex', o)

def page(path, sizes):
    """Любая страница (демо): переполнения и nowrap-флекс-элементы на нескольких ширинах; товара нет."""
    out = {}
    with kbpaths.lock('browser'), sync_playwright() as p:
        b = p.chromium.launch(channel='chromium', headless=True)
        for wh in sizes:
            w, h = map(int, wh.split('x'))
            pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
            pg.goto('file://' + os.path.abspath(path)); pg.wait_for_timeout(500)
            r = analyse(pg.evaluate(JS), None)
            r['outside'] = [o for o in r['outside'] if o['x0'] < 0 or o['x1'] > w]      # по высоте — прокрутка, не брак
            r['verdict'] = 'fail' if (r['outside'] or r['overflow'] or r['nowrap_flex_items']) else 'pass'
            out[wh] = {k: r[k] for k in ('verdict', 'n_line_boxes', 'outside', 'overflow', 'nowrap_flex_items')}
            print(wh, r['verdict'], '| переполнений', len(r['overflow']), '| nowrap-флекс', len(r['nowrap_flex_items']),
                  '| за холстом по ширине', len(r['outside']))
            for o in (r['overflow'] + r['nowrap_flex_items'])[:6]: print('   ', o)
            pg.close()
        b.close()
    return out

if __name__ == '__main__':
    args = sys.argv[1:]
    files = args[1:2] if args[:1] == ['page'] else args[:2]
    if (args[:1] == ['page'] and not files) or (args[:1] != ['page'] and len(files) < 2):
        print('вызов: layout_check.py ШАБЛОН.html ВЫРЕЗ.png | layout_check.py page ФАЙЛ.html [ШxВ …]', file=sys.stderr)
        sys.exit(2)
    absent = [f for f in files if not os.path.isfile(f)]
    if absent:
        print(f"нет файла: {', '.join(absent)}", file=sys.stderr)
        sys.exit(2)
    if args[0] == 'page':
        res = page(args[1], args[2:] or ['1440x900', '412x915'])
        json.dump(res, open(os.path.join(OUT, 'results_layout_page.json'), 'w'), ensure_ascii=False, indent=1)
    else:
        main(args[0], args[1])
