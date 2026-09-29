#!/usr/bin/env python3
"""shot_v3.py — кадры страницы или сборки по экранам и проверки, которых не видно на ужатом кадре (любой URL или папка).

Рядом с kit/shot.py: kit снимает HTML-копии холста по манифесту (полный кадр PNG, метки #N, --prev, --set, serve), а этот
скрипт — любую страницу или сборку по адресу или папке: --views (окна в командной строке), --routes (несколько маршрутов
приложения за запуск, префикс r<N>-<slug> в именах кадров), --expect-fonts (семейства ДС → поле fonts_unexpected), кадры
по экранам JPEG в бюджете байт и не длиннее 2000 px, --selector (кадры секций), --map (карта страницы DPR 0.25),
--motion, --strict (код 4). Проверки страницы те же, что у kit: вылет, шрифты, битые и внешние картинки, alt, невидимый
текст, цели < 24 и < 44 px, h1, lang, [PLACEHOLDER].

Кадры: по экранам (не full-page) в JPEG, каждый ≤ --budget байт и ≤ 2000 px по длинной стороне; если кадр больше —
пересъёмка с качеством ниже (80 → 70 → … → 40). Мобильная эмуляция с горизонтальным вылетом растягивает окно раскладки
(390 → 849 px) — остаток страницы снимается по координатам документа (mode: clip).
  * окна по умолчанию 1440x900,768x1024,390x844 (десктоп, планшет, телефон); ширины приёмки — kb/common/acceptance-widths.yaml;
  * --routes "/,/orders,/settings": несколько экранов приложения за один запуск;
  * проверки: lang, число h1, внешние (хотлинк) картинки, картинки без alt, невидимый после прокрутки текст
    (накопленная opacity < 0.1 — «reveal-ловушка»), цели < 24 и < 44 px на тач-окнах, [PLACEHOLDER] на странице,
    шрифты в работе и реально отрисованные (CDP CSS.getPlatformFontsForNode) → fonts_missing (объявлен, а рисуется
    запасной), --expect-fonts → fonts_unexpected;
  * stdout — краткая сводка (пути кадров и проверки по видам), полный манифест — в <outdir>/shots.json;
  * --strict: код 4, если какая-либо проверка не пройдена.
Использование:
  python3 shot_v3.py <url|path> <outdir> [--views 1440x900,768x1024,390x844] [--routes /,/x] [--selector "main > section"]
         [--max-elements 8] [--max-screens 12] [--quality 80] [--budget 262144] [--map] [--motion] [--wait-ms 400]
         [--expect-fonts "Golos Text,Unbounded"] [--strict] [--print-manifest]
Коды выхода: 0 — кадры есть; 2 — страница не открылась; 3 — кадров нет; 4 — --strict и есть непройденные проверки.
Зависимости: Python 3.10+, playwright (Chromium). Модель не вызывается; сеть — только к цели. Фоновых процессов не
оставляет: сервер статики — поток этого процесса, браузер закрывается в finally.
Где описан: claude-design/06-design-process/04-checks.md (§3 B, §4).
"""
import argparse, functools, http.server, json, os, re, socketserver, sys, threading, time
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

MAX_EDGE = 2000  # длинная сторона кадра по экранам, px
GENERIC = {'serif', 'sans-serif', 'monospace', 'cursive', 'fantasy', 'system-ui', 'ui-sans-serif', 'ui-serif',
           'ui-monospace', 'ui-rounded', '-apple-system', 'blinkmacsystemfont', 'emoji', 'math', 'fangsong'}

CHECKS_JS = r"""
(conf) => {
  const vw = conf.vw || document.documentElement.clientWidth;   // ширина из заданного вьюпорта: innerWidth при вылете растянут
  const touch = conf.touch;
  const sw = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);
  const desc = (el) => el.tagName.toLowerCase() + (el.id ? '#' + el.id : '') +
      ((el.className && typeof el.className === 'string' && el.className.trim()) ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  const off = [];
  if (sw > vw + 1) {
    for (const el of document.querySelectorAll('body *')) {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.right > vw + 1) {
        const inner = [...el.children].some(c => c.getBoundingClientRect().right > vw + 1);
        if (!inner) off.push({el: desc(el), right: Math.round(r.right), width: Math.round(r.width)});
      }
      if (off.length >= 5) break;
    }
  }
  const host = location.host;
  const imgs = [...document.images];
  const broken = imgs.filter(i => i.complete && i.naturalWidth === 0).slice(0, 10).map(i => i.getAttribute('src'));
  const external = imgs.map(i => i.currentSrc || i.src).filter(s => {
      if (!s || s.startsWith('data:') || s.startsWith('blob:')) return false;
      try { return new URL(s, location.href).host !== host; } catch (e) { return false; } }).slice(0, 10);
  const noAlt = imgs.filter(i => !i.hasAttribute('alt')).length;
  const opacityChain = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const cs = getComputedStyle(e); o *= parseFloat(cs.opacity); if (cs.visibility === 'hidden') return 0; } return o; };
  let small = 0, minFont = 999; const fonts = {}; const invisible = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while (walker.nextNode()) {
    const t = walker.currentNode; if (!t.textContent.trim()) continue;
    const el = t.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (cs.display === 'none' || r.width === 0 || r.height === 0) continue;
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName)) continue;
    if (opacityChain(el) < 0.1) { if (invisible.length < 8) invisible.push({el: desc(el), text: t.textContent.trim().slice(0, 40)}); continue; }
    const fs = parseFloat(cs.fontSize); if (fs < minFont) minFont = fs; if (fs < 12) small++;
    const fam = cs.fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '');
    fonts[fam] = (fonts[fam] || 0) + 1;
  }
  const targets24 = [], targets44 = [];
  if (touch) {
    const sel = 'a[href], button, input:not([type=hidden]), select, textarea, [role=button], [role=link], [tabindex]:not([tabindex="-1"])';
    for (const el of document.querySelectorAll(sel)) {
      const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
      if (r.width === 0 || r.height === 0 || cs.visibility === 'hidden') continue;
      const p = el.parentElement;   // ссылка внутри предложения — исключение WCAG 2.5.8
      const inlineText = el.tagName === 'A' && cs.display.startsWith('inline') && p &&
          (p.textContent || '').trim().length > (el.textContent || '').trim().length + 20;
      const m = Math.min(r.width, r.height);
      const item = {el: desc(el), w: Math.round(r.width), h: Math.round(r.height), inline_text_link: inlineText};
      if (m < 24 && !inlineText) { if (targets24.length < 8) targets24.push(item); }
      else if (m < 44) { if (targets44.length < 8) targets44.push(item); }
    }
  }
  const text = document.body ? document.body.innerText : '';
  const placeholders = (text.match(/\[PLACEHOLDER[^\]]*\]/g) || []).length;
  return {viewport_width: vw, inner_width: window.innerWidth, scroll_width: sw, overflow_px: Math.max(0, sw - vw),
          overflow_elements: off, page_height: document.documentElement.scrollHeight,
          lang: document.documentElement.getAttribute('lang') || '', h1_count: document.querySelectorAll('h1').length,
          broken_images: broken, external_images: external, images_without_alt: noAlt,
          invisible_text: invisible, small_text_elements: small, min_font_px: minFont === 999 ? null : minFont,
          small_targets_24: targets24, small_targets_44: targets44, placeholders: placeholders, fonts_used: fonts};
}
"""

SAMPLE_JS = r"""
(sels) => sels.map(s => { const el = [...document.querySelectorAll(s)].find(e => {
    const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && e.textContent.trim(); });
  if (!el) return null; el.setAttribute('data-shot-sample', s);
  return {selector: s, declared: getComputedStyle(el).fontFamily.split(',')[0].trim().replace(/^["']|["']$/g, '')}; })
"""


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):  # не засорять stdout/stderr журналом запросов
        pass


def serve_path(path):
    """Локальный файл/папка → (httpd, url). Сервер живёт в демон-потоке этого процесса."""
    path = os.path.abspath(path)
    root, name = (path, '') if os.path.isdir(path) else (os.path.dirname(path), os.path.basename(path))
    handler = functools.partial(QuietHandler, directory=root)
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f'http://127.0.0.1:{httpd.server_address[1]}/{name}'


def jpeg_within_budget(shoot, quality, budget):
    """shoot(q) -> bytes. Понижает качество, пока кадр не влезет в бюджет (не ниже 40)."""
    q = quality
    data = shoot(q)
    while len(data) > budget and q > 40:
        q -= 10
        data = shoot(q)
    return data, q


def platform_fonts(ctx, page):
    """Какие шрифты реально отрисованы у образцов (h1, h2, p, button, a): CDP CSS.getPlatformFontsForNode.
    Возвращает список {selector, declared, rendered: [{family, custom, glyphs}]} или [] (не Chromium, сбой CDP)."""
    try:
        samples = [s for s in page.evaluate(SAMPLE_JS, ['h1', 'h2', 'p', 'button', 'nav a', 'a']) if s]
        cdp = ctx.new_cdp_session(page)
        cdp.send('DOM.enable'); cdp.send('CSS.enable')
        root = cdp.send('DOM.getDocument', {'depth': -1})['root']['nodeId']
        out = []
        for s in samples:
            nid = cdp.send('DOM.querySelector', {'nodeId': root, 'selector': f'[data-shot-sample="{s["selector"]}"]'})['nodeId']
            if not nid:
                continue
            fonts = cdp.send('CSS.getPlatformFontsForNode', {'nodeId': nid}).get('fonts', [])
            fonts = sorted(fonts, key=lambda f: -f.get('glyphCount', 0))
            out.append({**s, 'rendered': [{'family': f.get('familyName'), 'custom': f.get('isCustomFont'),
                                           'glyphs': f.get('glyphCount')} for f in fonts[:3]]})
        cdp.detach()
        return out
    except Exception as e:  # noqa: BLE001 — проверка шрифтов не должна ронять съёмку
        return [{'error': f'{type(e).__name__}: {str(e)[:120]}'}]


def font_verdicts(samples, fonts_used, expect):
    """fonts_missing: объявлен не-generic шрифт, а рисуется системный с другим именем (веб-шрифт не загрузился или не
    подключён). fonts_unexpected: при --expect-fonts — семейства в работе, которых нет в ожидаемых."""
    missing = []
    for s in samples:
        if 'error' in s or not s.get('rendered'):
            continue
        dec = (s.get('declared') or '').lower()
        if not dec or dec in GENERIC:
            continue
        top = s['rendered'][0]
        fam = (top.get('family') or '').lower()
        if top.get('custom') or fam.startswith(dec) or dec in fam:
            continue
        missing.append({'selector': s['selector'], 'declared': s['declared'], 'rendered': top.get('family')})
    unexpected = []
    if expect:
        exp = [e.lower() for e in expect]
        for fam, n in fonts_used.items():
            f = fam.lower()
            if f in GENERIC or any(f == e or f.startswith(e) for e in exp):
                continue
            unexpected.append({'family': fam, 'text_elements': n})
        for e in expect:
            if not any(k.lower() == e.lower() or k.lower().startswith(e.lower()) for k in fonts_used):
                missing.append({'expected': e, 'reason': 'not used on this screen'})
    return missing, unexpected


def slug(route):
    s = re.sub(r'[^a-z0-9]+', '-', route.lower()).strip('-')
    return s or 'home'


def failed_checks(v):
    f = []
    if v['overflow_px'] > 0: f.append('overflow_px')
    for k in ('console_errors', 'broken_images', 'external_images', 'invisible_text', 'small_targets_24',
              'fonts_missing', 'fonts_unexpected'):
        if v.get(k): f.append(k)
    if v['small_text_elements'] > 0: f.append('small_text_elements')
    if v['images_without_alt'] > 0: f.append('images_without_alt')
    if v['h1_count'] != 1: f.append('h1_count')
    if not v['lang']: f.append('lang')
    return f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('outdir')
    ap.add_argument('--views', default='1440x900,768x1024,390x844')
    ap.add_argument('--routes', default='', help='пути через запятую относительно цели: "/,/orders"')
    ap.add_argument('--max-screens', type=int, default=12)
    ap.add_argument('--quality', type=int, default=80)
    ap.add_argument('--budget', type=int, default=262144, help='байт на кадр: больше — пересъёмка с качеством ниже')
    ap.add_argument('--selector', default=None, help='CSS-селектор секций для отдельных кадров')
    ap.add_argument('--max-elements', type=int, default=8)
    ap.add_argument('--map', action='store_true', help='обзорная карта full-page при DPR 0.25 (для Claude)')
    ap.add_argument('--motion', action='store_true', help='не просить prefers-reduced-motion')
    ap.add_argument('--wait-ms', type=int, default=400, help='пауза после загрузки и после прокрутки')
    ap.add_argument('--expect-fonts', default='', help='семейства из DESIGN.md через запятую')
    ap.add_argument('--strict', action='store_true', help='код 4, если есть непройденные проверки')
    ap.add_argument('--print-manifest', action='store_true', help='печатать полный манифест, а не сводку')
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    os.makedirs(a.outdir, exist_ok=True)
    httpd = None
    base = a.target
    if not base.startswith(('http://', 'https://', 'file://')):
        if not os.path.exists(base):
            print(json.dumps({'error': f'not found: {base}'}), file=sys.stderr); return 2
        httpd, base = serve_path(base)
    routes = [r.strip() for r in a.routes.split(',') if r.strip()] or ['']
    expect = [e.strip() for e in a.expect_fonts.split(',') if e.strip()]
    manifest = {'tool': 'shot.py', 'version': '3.0', 'target': a.target, 'url': base, 'routes': routes,
                'created': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'budget_bytes': a.budget,
                'max_edge_px': MAX_EDGE, 'reduced_motion': not a.motion, 'views': [], 'shots': [], 'notes': []}
    t0 = time.time()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                for ri, route in enumerate(routes):
                    url = urljoin(base, route.lstrip('/')) if route else base
                    rprefix = f'r{ri}-{slug(route)}-' if len(routes) > 1 else ''
                    for spec in a.views.split(','):
                        w, h = (int(x) for x in spec.lower().strip().split('x'))
                        kind = 'desktop' if w >= 1024 else ('tablet' if w >= 768 else 'mobile')
                        mobile = w < 768
                        touch = w < 1024
                        ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1,
                                                  is_mobile=mobile, has_touch=touch,
                                                  reduced_motion=None if a.motion else 'reduce')
                        page = ctx.new_page()
                        console_errors, failed = [], []
                        page.on('console', lambda m: console_errors.append(m.text[:300]) if m.type == 'error' else None)
                        page.on('pageerror', lambda e: console_errors.append(('pageerror: ' + str(e))[:300]))
                        page.on('requestfailed', lambda r: failed.append({'url': r.url[:200], 'error': (r.failure or '')[:120]}))
                        page.on('response', lambda r: failed.append({'url': r.url[:200], 'status': r.status}) if r.status >= 400 else None)
                        try:
                            page.goto(url, wait_until='networkidle', timeout=60000)
                        except PWTimeout:
                            manifest['notes'].append(f'{route or "/"} {spec}: networkidle timeout, продолжаю после load')
                        try:
                            page.evaluate('document.fonts ? document.fonts.ready.then(() => true) : true')
                        except Exception:
                            pass
                        page.wait_for_timeout(a.wait_ms)
                        total = page.evaluate('document.documentElement.scrollHeight')
                        y = 0
                        while y < total:  # прокрутка до конца и обратно — догрузить lazy и запустить reveal-анимации
                            page.evaluate(f'window.scrollTo(0, {y})'); page.wait_for_timeout(120); y += h
                        page.evaluate('window.scrollTo(0, 0)'); page.wait_for_timeout(a.wait_ms)
                        checks = page.evaluate(CHECKS_JS, {'vw': w, 'touch': touch})
                        samples = platform_fonts(ctx, page)
                        missing, unexpected = font_verdicts(samples, checks['fonts_used'], expect)
                        total = checks['page_height']
                        view = {'route': route or '/', 'viewport': f'{w}x{h}', 'kind': kind, **checks,
                                'font_samples': samples, 'fonts_missing': missing, 'fonts_unexpected': unexpected,
                                'console_errors': console_errors[:10], 'failed_requests': failed[:10]}
                        y, i, clip_frames = 0, 0, 0
                        while y < total and i < a.max_screens:
                            page.evaluate(f'window.scrollTo(0, {y})'); page.wait_for_timeout(a.wait_ms // 2)
                            top = page.evaluate('window.visualViewport ? window.visualViewport.pageTop : window.scrollY')
                            if top + h < min(total, y + h) - 1:
                                # прокрутка упёрлась раньше конца (растянутый layout viewport) — кадр по документу
                                c = {'x': 0, 'y': y, 'width': w, 'height': min(h, total - y)}
                                shoot = lambda qq, c=c: page.screenshot(type='jpeg', quality=qq, full_page=True, clip=c)
                                mode = 'clip'; clip_frames += 1
                            else:
                                shoot = lambda qq: page.screenshot(type='jpeg', quality=qq)
                                mode = 'scroll'
                            data, q = jpeg_within_budget(shoot, a.quality, a.budget)
                            path = os.path.join(a.outdir, f'{rprefix}{kind}-{w}x{h}-{i:02d}.jpg')
                            open(path, 'wb').write(data)
                            manifest['shots'].append({'path': os.path.abspath(path), 'kind': 'screen', 'route': route or '/',
                                                      'viewport': f'{w}x{h}', 'index': i, 'scrollY': y, 'mode': mode,
                                                      'bytes': len(data), 'quality': q, 'over_budget': len(data) > a.budget})
                            y += h; i += 1
                        view['clip_frames'] = clip_frames
                        view['screens_taken'] = i
                        view['screens_total'] = -(-total // h)
                        if a.selector:
                            els = page.locator(a.selector)
                            n = min(els.count(), a.max_elements)
                            for k in range(n):
                                el = els.nth(k)
                                el.scroll_into_view_if_needed(); page.wait_for_timeout(a.wait_ms // 2)
                                # координаты документа через getBoundingClientRect()+scrollY: bounding_box() считает от
                                # visual viewport и при мобильной эмуляции с вылетом даёт неверный кадр
                                bb = el.evaluate('e => { const r = e.getBoundingClientRect(); '
                                                 'return {y: r.top + window.scrollY, height: r.height}; }')
                                if not bb or bb['height'] < 2:
                                    continue
                                clip = {'x': 0, 'y': max(0, bb['y']), 'width': w, 'height': min(bb['height'], MAX_EDGE)}
                                shoot = lambda qq, c=clip: page.screenshot(type='jpeg', quality=qq, full_page=True, clip=c)
                                data, q = jpeg_within_budget(shoot, a.quality, a.budget)
                                path = os.path.join(a.outdir, f'{rprefix}{kind}-{w}x{h}-sec{k:02d}.jpg')
                                open(path, 'wb').write(data)
                                manifest['shots'].append({'path': os.path.abspath(path), 'kind': 'section', 'route': route or '/',
                                                          'viewport': f'{w}x{h}', 'selector': a.selector, 'index': k,
                                                          'top': round(clip['y']), 'height': round(clip['height']),
                                                          'clipped': bb['height'] > MAX_EDGE, 'bytes': len(data), 'quality': q,
                                                          'over_budget': len(data) > a.budget})
                        view['failed_checks'] = failed_checks(view)
                        manifest['views'].append(view)
                        ctx.close()
                        if a.map:  # обзорная карта: отдельный контекст с DPR 0.25 (для Claude; мелочь не видна)
                            mctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=0.25,
                                                       is_mobile=mobile, has_touch=touch,
                                                       reduced_motion=None if a.motion else 'reduce')
                            mp = mctx.new_page()
                            try:
                                mp.goto(url, wait_until='networkidle', timeout=60000)
                            except PWTimeout:
                                pass
                            mp.wait_for_timeout(a.wait_ms)
                            data = mp.screenshot(type='jpeg', quality=70, full_page=True)
                            path = os.path.join(a.outdir, f'{rprefix}{kind}-{w}x{h}-map.jpg')
                            open(path, 'wb').write(data)
                            manifest['shots'].append({'path': os.path.abspath(path), 'kind': 'map', 'route': route or '/',
                                                      'viewport': f'{w}x{h}', 'dpr': 0.25, 'bytes': len(data), 'quality': 70,
                                                      'over_budget': len(data) > a.budget})
                            mctx.close()
            finally:
                browser.close()
    except Exception as e:  # страница не открылась, браузер не стартовал и т. п.
        manifest['error'] = f'{type(e).__name__}: {e}'[:500]
        print(json.dumps(manifest, ensure_ascii=False, indent=1))
        return 2
    finally:
        if httpd:
            httpd.shutdown(); httpd.server_close()
    manifest['seconds'] = round(time.time() - t0, 1)
    manifest['failed_checks_total'] = sum(len(v['failed_checks']) for v in manifest['views'])
    mpath = os.path.join(a.outdir, 'shots.json')
    open(mpath, 'w', encoding='utf-8').write(json.dumps(manifest, ensure_ascii=False, indent=1))
    if a.print_manifest:
        print(json.dumps(manifest, ensure_ascii=False, indent=1))
    else:
        summary = {'manifest': os.path.abspath(mpath), 'seconds': manifest['seconds'],
                   'frames': [s['path'] for s in manifest['shots'] if s['kind'] != 'map'],
                   'views': [{k: v[k] for k in ('route', 'viewport', 'overflow_px', 'failed_checks', 'fonts_missing',
                                                'external_images', 'invisible_text', 'small_targets_24', 'placeholders')}
                             for v in manifest['views']]}
        print(json.dumps(summary, ensure_ascii=False, indent=1))
    for v in manifest['views']:
        print(f"[shot] {v['route']} {v['viewport']}: кадров {v['screens_taken']}/{v['screens_total']}, вылет {v['overflow_px']} px, "
              f"не пройдено: {', '.join(v['failed_checks']) or '—'}", file=sys.stderr)
    if not manifest['shots']:
        return 3
    return 4 if (a.strict and manifest['failed_checks_total']) else 0


if __name__ == '__main__':
    sys.exit(main())
