#!/usr/bin/env python3
"""page_accept.py — приёмка страницы с ИИ-ассетами в Chromium (агент J, волна 3, 23.09.2026).

Что меряет (одна команда — один JSON-вердикт):
  • вес первого экрана по CDP (картинки, видео, JS, CSS, шрифты) и за сессию без прокрутки;
  • LCP: элемент, файл, размер, время; флаги LCP-картинки (lazy, fetchpriority); CLS; TBT (сумма долгих задач − 50 мс);
  • картинки: alt есть, width/height заданы, переотдача пикселей (естественная ширина / (CSS-ширина × DPR)), формат;
  • видео: autoplay/muted/loop/playsinline/poster/preload, играет ли, длительность, есть ли видимая кнопка паузы с
    доступным именем (WCAG 2.2.2 для петли > 5 с);
  • prefers-reduced-motion: второй прогон с reduce — байты видео (должно быть 0) и «движение в покое» (доля пикселей,
    изменившихся за 1 с);
  • контраст текста поверх медиа по WCAG F83 «по буквам»: два снимка — с текстом и с прозрачным текстом, маска букв =
    разница снимков, контраст цвета текста к КАЖДОМУ пикселю фона под буквами (худший, p1, p5); для видео-фона — по
    кадрам (пауза + перемотка на 0, 25, 50, 75 % длительности), итог — худший кадр;
  • фавиконы и og:image (есть ли, размеры в разметке).
Запуск (браузер берёт блокировку сам — 99-raw/tools/.locks/browser.lock, ждёт до 900 с; если утилиту обернули во внешний
flock на тот же замок, повторно не берёт — проверка предка через /proc, X2 24.09.2026):
  python3 99-raw/tools/page_accept.py PAGE.html|URL --out DIR [--mobile] [--throttle] [--no-rm] [--contrast SELECTOR ...]
     [--budget-first-kb 2500] [--dark] [--wait 4000] [--click SELECTOR ...]
  PAGE.html — локальный файл: папка раздаётся встроенным HTTP-сервером (Range для видео) и закрывается после прогона.
Код выхода 0 — все проверки прошли, 1 — есть провалы (список в verdict.fail), 2 — ошибка запуска.
Зависимости: Python 3.13, Playwright 1.63 (Chromium 153 CfT, channel="chromium"), numpy, Pillow."""
import argparse, contextlib, fcntl, http.server, io, json, os, socketserver, sys, threading, time, urllib.parse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
LOCK = kbpaths.lock_path('browser', 'ai-media')
MIME = {'.avif': 'image/avif', '.webp': 'image/webp', '.jxl': 'image/jxl', '.webm': 'video/webm', '.mp4': 'video/mp4',
        '.svg': 'image/svg+xml', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
        '.html': 'text/html; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon',
        '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.woff2': 'font/woff2'}


# ---------------------------------------------------------------- сервер для локальных файлов
def _handler(root):
    class H(http.server.SimpleHTTPRequestHandler):
        protocol_version = 'HTTP/1.1'
        def __init__(self, *a, **k): super().__init__(*a, directory=root, **k)
        def log_message(self, *a): pass
        def guess_type(self, p): return MIME.get(os.path.splitext(p)[1].lower(), 'application/octet-stream')
        def end_headers(self):
            self.send_header('Cache-Control', 'no-store'); super().end_headers()
        def do_GET(self):
            fs = self.translate_path(self.path); rng = self.headers.get('Range')
            if rng and os.path.isfile(fs):
                size = os.path.getsize(fs); a, _, b = rng.replace('bytes=', '').partition('-')
                a = int(a or 0); b = min(int(b) if b else size - 1, size - 1)
                with open(fs, 'rb') as f: f.seek(a); data = f.read(b - a + 1)
                self.send_response(206); self.send_header('Content-Type', self.guess_type(fs))
                self.send_header('Content-Range', f'bytes {a}-{b}/{size}'); self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Content-Length', str(len(data))); self.end_headers()
                try: self.wfile.write(data)
                except (BrokenPipeError, ConnectionResetError): pass
                return
            try: super().do_GET()
            except (BrokenPipeError, ConnectionResetError): pass
    return H


class _TS(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True; allow_reuse_address = True


@contextlib.contextmanager
def serve(root):
    srv = _TS(('127.0.0.1', 0), _handler(root)); t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
    try: yield f'http://127.0.0.1:{srv.server_address[1]}'
    finally: srv.shutdown(); srv.server_close()


def _ancestor_holds_lock(lock_name):
    """Держит ли уже этот замок процесс-предок через flock(1) (`flock … browser.lock python3 page_accept.py …`).
    Повторная блокировка того же файла из дочернего процесса ждала бы родителя до таймаута (900 с) — самоблокировка.
    Перенесено из asset_audit.py (агент X2, 24.09.2026). Только Linux (/proc); при любой ошибке — False."""
    try:
        pid = os.getppid()
        for _ in range(16):
            if pid <= 1:
                break
            with open(f'/proc/{pid}/cmdline', 'rb') as fh:
                args = [x.decode('utf-8', 'replace') for x in fh.read().split(b'\0') if x]
            if args and os.path.basename(args[0]) == 'flock' and any(x.endswith(lock_name) for x in args[1:]):
                return True
            with open(f'/proc/{pid}/stat', encoding='utf-8', errors='replace') as fh:
                pid = int(fh.read().rsplit(')', 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return False
    return False


@contextlib.contextmanager
def browser_lock(timeout=900):
    if _ancestor_holds_lock(os.path.basename(LOCK)):   # обёрнуто во внешний flock — замок уже наш
        yield
        return
    os.makedirs(os.path.dirname(LOCK), exist_ok=True)
    f = open(LOCK, 'a'); t0 = time.time()
    while True:
        try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB); break
        except BlockingIOError:
            if time.time() - t0 > timeout: raise SystemExit('browser.lock занят > %d с' % timeout)
            time.sleep(2)
    try: yield
    finally: fcntl.flock(f, fcntl.LOCK_UN); f.close()


# ---------------------------------------------------------------- JS-сборщики
INSTALL = """() => { window.__lcp = []; window.__cls = 0; window.__lt = [];
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp.push({t: e.startTime, size: e.size,
     tag: e.element && e.element.tagName, id: e.element && (e.element.id || e.element.className || ''),
     url: e.url || '', lazy: e.element && e.element.loading === 'lazy',
     fp: e.element && (e.element.getAttribute('fetchpriority') || '')}); }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type: 'layout-shift', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push(e.duration); }).observe({type: 'longtask', buffered: true});
}"""

DOM = r"""() => {
  const dpr = devicePixelRatio, vh = innerHeight, vw = innerWidth;
  const imgs = [...document.images].map(i => { const r = i.getBoundingClientRect();
    return {src: (i.currentSrc || i.src).split('/').slice(-2).join('/'), alt: i.hasAttribute('alt') ? i.alt : null,
      wh: i.hasAttribute('width') && i.hasAttribute('height'), loading: i.loading, fp: i.getAttribute('fetchpriority') || '',
      natural: [i.naturalWidth, i.naturalHeight], css: [Math.round(r.width), Math.round(r.height)],
      above: r.top < vh && r.bottom > 0, over: (r.width && !/\.svg(\?|$)/.test(i.currentSrc || i.src)) ? +(i.naturalWidth / (r.width * dpr)).toFixed(2) : null,
      inPicture: !!i.closest('picture')}; });
  const vids = [...document.querySelectorAll('video')].map(v => { const r = v.getBoundingClientRect();
    const box = v.closest('section, header, main') || document.body;
    const btns = [...box.querySelectorAll('button')].filter(b => { const s = getComputedStyle(b); return !b.hidden && s.display !== 'none' && s.visibility !== 'hidden'; });
    const named = btns.filter(b => (b.getAttribute('aria-label') || b.textContent || b.title || '').trim().length > 0);
    return {src: (v.currentSrc || '').split('/').pop(), autoplay: v.autoplay, muted: v.muted, loop: v.loop,
      playsinline: v.playsInline, poster: !!v.getAttribute('poster'), preload: v.getAttribute('preload'),
      playing: !v.paused && v.readyState > 2, duration: isFinite(v.duration) ? +v.duration.toFixed(2) : null,
      above: r.top < vh && r.bottom > 0, pause_button: named.length > 0, opacity: getComputedStyle(v).opacity}; });
  const icons = [...document.querySelectorAll('link[rel~=icon], link[rel=apple-touch-icon]')].map(l => l.rel + ' ' + (l.type || '') + ' ' + (l.sizes && l.sizes.value || ''));
  const og = Object.fromEntries([...document.querySelectorAll('meta[property^="og:image"]')].map(m => [m.getAttribute('property'), m.content]));
  const svgInline = [...document.querySelectorAll('svg')].reduce((a, s) => a + s.outerHTML.length, 0);
  return {imgs, vids, icons, og, svgInlineChars: svgInline, vw, vh, dpr, lang: document.documentElement.lang};
}"""


def cdp_bytes(cdp_events):
    by = {}
    for rid, (typ, url, n) in cdp_events.items():
        by.setdefault(typ, 0); by[typ] += n
    return by


def contrast_ratio(l1, l2):
    hi, lo = np.maximum(l1, l2), np.minimum(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def rel_lum(rgb):   # rgb 0..255 массив (…, 3)
    c = rgb.astype(np.float64) / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    return c @ np.array([0.2126, 0.7152, 0.0722])


def parse_color(s):
    s = s.strip()
    if s.startswith('rgb'):
        v = [float(x) for x in s[s.index('(') + 1:s.index(')')].replace('/', ' ').replace(',', ' ').split()]
        return np.array(v[:3]), (v[3] if len(v) > 3 else 1.0)
    return np.array([0, 0, 0]), 1.0


def f83(page, selectors, video_frames=True):
    """Контраст по буквам: снимок с текстом и без (color: transparent) → маска букв → худший пиксель фона."""
    out = []
    els = []
    for sel in selectors:
        for i in range(page.locator(sel).count()):
            els.append((sel, i))
    if not els:
        return out
    has_video = page.evaluate("() => [...document.querySelectorAll('video')].some(v => v.readyState > 1 && getComputedStyle(v).opacity !== '0' && getComputedStyle(v).display !== 'none')")
    times = [None]
    if has_video and video_frames:
        dur = page.evaluate("() => { const v = [...document.querySelectorAll('video')].find(v => v.readyState > 1); return v && isFinite(v.duration) ? v.duration : 0; }")
        if dur:
            times = [0.0, dur * 0.25, dur * 0.5, dur * 0.75]
    page.add_style_tag(content='.__j_hide, .__j_hide * { color: transparent !important; text-shadow: none !important; -webkit-text-stroke: 0 !important; caret-color: transparent !important; }')
    for sel, i in els:
        loc = page.locator(sel).nth(i)
        try:
            loc.scroll_into_view_if_needed(timeout=3000); page.wait_for_timeout(150)
        except Exception:
            pass
        box = loc.bounding_box()
        vp = page.viewport_size or {'width': 1440, 'height': 900}
        if not box or box['width'] < 2:
            continue
        x0, y0 = max(box['x'] - 2, 0), max(box['y'] - 2, 0)
        x1, y1 = min(box['x'] + box['width'] + 2, vp['width']), min(box['y'] + box['height'] + 2, vp['height'])
        if x1 - x0 < 2 or y1 - y0 < 2:
            continue
        clip = {'x': x0, 'y': y0, 'width': x1 - x0, 'height': y1 - y0}
        info = loc.evaluate("e => { const s = getComputedStyle(e); return {color: s.color, size: parseFloat(s.fontSize), weight: parseInt(s.fontWeight), text: e.textContent.trim().slice(0, 60)}; }")
        rgb, a = parse_color(info['color'])
        large = info['size'] >= 24 or (info['size'] >= 18.66 and info['weight'] >= 700)
        need = 3.0 if large else 4.5
        worst = []
        for t in times:
            if t is not None:
                page.evaluate("(t) => new Promise(r => { const vs = [...document.querySelectorAll('video')]; let n = vs.length; if (!n) r();"
                              " vs.forEach(v => { v.pause(); v.currentTime = Math.min(t, (v.duration || 1) - 0.05); v.addEventListener('seeked', () => { if (--n === 0) r(); }, {once: true}); });"
                              " setTimeout(r, 1500); })", t)
                page.wait_for_timeout(120)
            with_text = np.asarray(Image.open(io.BytesIO(page.screenshot(clip=clip))).convert('RGB')).astype(np.int16)
            loc.evaluate("e => e.classList.add('__j_hide')")
            page.wait_for_timeout(60)
            bg = np.asarray(Image.open(io.BytesIO(page.screenshot(clip=clip))).convert('RGB')).astype(np.int16)
            loc.evaluate("e => e.classList.remove('__j_hide')")
            diff = np.abs(with_text - bg).max(-1)
            glyph = diff > 24                                   # пиксели, где буква заметно меняет фон
            if glyph.sum() < 10:
                continue
            # фон под буквой и её ореолом сглаживания: маска + 1 px
            from scipy.ndimage import binary_dilation
            m = binary_dilation(glyph, iterations=1)
            # цвет текста: вычисленный (computed) при непрозрачном тексте; при opacity/альфе < 1 — отрисованный
            # (медиана «сердцевины» букв: 30 % пикселей с наибольшей разницей)
            core = glyph & (diff >= np.percentile(diff[glyph], 70))
            rendered = np.median(with_text[core], axis=0)
            opaque = loc.evaluate("e => { let o = 1, n = e; while (n && n.nodeType === 1) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; } return o; }")
            tx = rgb if (a >= 0.999 and opaque >= 0.999) else rendered
            L_bg = rel_lum(bg[m]); L_tx = rel_lum(np.asarray(tx)[None, :])[0]
            cr = contrast_ratio(L_tx, L_bg)
            worst.append({'t': None if t is None else round(t, 2), 'text_rgb_used': [int(x) for x in tx], 'min': round(float(cr.min()), 2),
                          'p1': round(float(np.percentile(cr, 1)), 2), 'p5': round(float(np.percentile(cr, 5)), 2)})
        if worst:
            wmin = min(w['min'] for w in worst)
            out.append({'selector': sel, 'index': i, 'text': info['text'], 'color': info['color'], 'alpha': a,
                        'font_px': info['size'], 'large': large, 'need': need, 'frames': worst,
                        'f83_min': wmin, 'pass_f83': wmin >= need,
                        'pass_p1': min(w['p1'] for w in worst) >= need})
    if times != [None]:
        page.evaluate("() => document.querySelectorAll('video').forEach(v => v.play().catch(() => {}))")
    return out


def run_once(p, url, a, reduce):
    b = p.chromium.launch(channel='chromium', headless=True)
    ctx_kw = dict(p.devices['Pixel 7']) if a.mobile else {'viewport': {'width': a.width, 'height': a.height}, 'device_scale_factor': a.dpr}
    ctx_kw['reduced_motion'] = 'reduce' if reduce else 'no-preference'
    ctx_kw['color_scheme'] = 'dark' if a.dark else 'light'
    ctx = b.new_context(**ctx_kw)
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send('Network.enable'); cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    if a.throttle:
        cdp.send('Network.emulateNetworkConditions', {'offline': False, 'latency': 150, 'downloadThroughput': 1.6e6 / 8, 'uploadThroughput': 750e3 / 8})
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': 4})
    ev, phase = {}, {'first': True}
    first_bytes = {}
    fin = {}
    def on_resp(e):
        ev[e['requestId']] = [e['type'].lower(), e['response']['url'], 0]
    def on_data(e):                      # байты по кускам — для незавершённых (видео с Range, оборванные)
        r = ev.get(e['requestId'])
        if r and e['requestId'] not in fin: r[2] += e.get('encodedDataLength', 0)
    def on_fin(e):                       # итог запроса из loadingFinished — главный источник (без двойного счёта)
        r = ev.get(e['requestId'])
        if r and e.get('encodedDataLength'): fin[e['requestId']] = 1; r[2] = e['encodedDataLength']
    cdp.on('Network.responseReceived', on_resp); cdp.on('Network.dataReceived', on_data); cdp.on('Network.loadingFinished', on_fin)
    page.add_init_script('(' + INSTALL + ')()')
    msgs = []
    page.on('console', lambda m: msgs.append(f'{m.type}: {m.text}'[:200]) if m.type in ('error', 'warning') else None)
    page.on('pageerror', lambda e: msgs.append(f'pageerror: {e}'[:200]))
    t0 = time.time()
    page.goto(url, wait_until='load', timeout=120000)
    for sel in (a.click or []):                      # состояние страницы перед замером (кнопка «рассвет», вкладка и т. п.)
        try:
            page.click(sel, timeout=3000)
        except Exception as e:
            msgs.append(f'click {sel}: {e}'[:200])
    page.wait_for_timeout(a.wait)
    first = {k: round(v / 1024, 1) for k, v in cdp_bytes({k: tuple(v) for k, v in ev.items()}).items()}
    reqs = sorted(((t, u.split('?')[0].split('/')[-1], round(n / 1024, 1)) for t, u, n in (tuple(v) for v in ev.values()) if n), key=lambda x: -x[2])
    s1 = np.asarray(Image.open(io.BytesIO(page.screenshot())).convert('L')).astype(np.int16)
    page.wait_for_timeout(1000)
    shot = page.screenshot()
    s2 = np.asarray(Image.open(io.BytesIO(shot)).convert('L')).astype(np.int16)
    idle_motion = round(float((np.abs(s1 - s2) > 6).mean() * 100), 2)
    # движение дольше 5 с (WCAG 2.2.2): что ещё движется на 6-й секунде после load
    page.wait_for_timeout(max(0, 6000 - a.wait - 1000))
    late1 = np.asarray(Image.open(io.BytesIO(page.screenshot())).convert('L')).astype(np.int16)
    page.wait_for_timeout(1000)
    late2 = np.asarray(Image.open(io.BytesIO(page.screenshot())).convert('L')).astype(np.int16)
    late_motion = round(float((np.abs(late1 - late2) > 6).mean() * 100), 2)
    late_playing = page.evaluate("() => [...document.querySelectorAll('video')].filter(v => !v.paused && v.readyState > 2).length")
    any_pause_btn = page.evaluate("() => [...document.querySelectorAll('button')].some(b => !b.hidden && getComputedStyle(b).display !== 'none' && /пауз|останов|stop|pause|запуст|воспроизв|play/i.test((b.getAttribute('aria-label') || '') + ' ' + b.textContent))")
    lcp = page.evaluate('window.__lcp'); cls = page.evaluate('window.__cls'); lt = page.evaluate('window.__lt')
    dom = page.evaluate(DOM)
    res = {'reduce': reduce, 'first_screen_kb': first, 'first_screen_total_kb': round(sum(first.values()), 1), 'requests': reqs[:40],
           'lcp': lcp[-1] if lcp else None, 'lcp_candidates': [(x['tag'], x['size'], round(x['t'])) for x in lcp],
           'cls': round(cls, 4), 'tbt_ms': round(sum(max(0, d - 50) for d in lt)), 'idle_motion_pct': idle_motion,
           'motion_after_6s_pct': late_motion, 'videos_playing_after_6s': late_playing, 'pause_control': any_pause_btn,
           'dom': dom, 'console': msgs[:20], 'secs': round(time.time() - t0, 1), 'screenshot': shot}
    if a.contrast and not reduce:
        res['contrast'] = f83(page, a.contrast)
    ctx.close(); b.close()
    return res


def verdict(no, rm, a):
    fail, warn, ok = [], [], []
    budget = a.budget_first_kb or (1500 if a.mobile else 2500)
    (ok if no['first_screen_total_kb'] <= budget else fail).append(f"первый экран {no['first_screen_total_kb']} КБ ≤ {budget}")
    l = no['lcp']
    if l:
        (fail if l.get('lazy') else ok).append(f"LCP-элемент {l['tag']} без loading=lazy" if not l.get('lazy') else 'LCP-картинка с loading=lazy')
        if l['tag'] == 'IMG' and l.get('fp') != 'high':
            warn.append('LCP-картинка без fetchpriority="high"')
        if a.throttle:
            (ok if l['t'] <= 2500 else fail).append(f"LCP {round(l['t'])} мс ≤ 2500 (CPU×4, 1,6 Мбит/с)")
    else:
        fail.append('нет ни одной записи LCP (всё появляется из opacity 0?)')
    (ok if no['cls'] <= 0.1 else fail).append(f"CLS {no['cls']} ≤ 0,1")
    for im in no['dom']['imgs']:
        if im['alt'] is None: fail.append(f"нет alt: {im['src']}")
        if not im['wh']: warn.append(f"нет width/height: {im['src']}")
        if im['above'] and im['over'] and im['over'] > 2.0: warn.append(f"переотдача ×{im['over']}: {im['src']}")
    for v in no['dom']['vids']:
        if v['above'] and (v['autoplay'] or v['playing']):
            if not (v['muted'] and v['playsinline']): fail.append(f"видео без muted/playsinline: {v['src']}")
            if (v['duration'] or 0) > 5 and not v['pause_button']: fail.append(f"петля > 5 с без кнопки паузы: {v['src']} (WCAG 2.2.2)")
    if (no['videos_playing_after_6s'] or no['motion_after_6s_pct'] >= 0.5) and not no['pause_control']:
        fail.append(f"движение дольше 5 с без кнопки паузы (видео {no['videos_playing_after_6s']}, пикселей {no['motion_after_6s_pct']} %) — WCAG 2.2.2")
    if rm is not None:
        vb = rm['first_screen_kb'].get('media', 0)
        (ok if vb == 0 else fail).append(f"reduce: видео {vb} КБ (нужно 0)")
        (ok if rm['idle_motion_pct'] < 0.5 else fail).append(f"reduce: движение в покое {rm['idle_motion_pct']} % (< 0,5)")
    for c in no.get('contrast', []):
        (ok if c['pass_f83'] else fail).append(f"F83 «{c['text'][:28]}»: худший {c['f83_min']} (нужно {c['need']})")
    if not any('icon' in x for x in no['dom']['icons']): warn.append('нет <link rel=icon>')
    return {'pass': not fail, 'fail': fail, 'warn': warn, 'ok': ok}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('target'); ap.add_argument('--out', required=True)
    ap.add_argument('--mobile', action='store_true'); ap.add_argument('--throttle', action='store_true')
    ap.add_argument('--no-rm', action='store_true'); ap.add_argument('--dark', action='store_true')
    ap.add_argument('--contrast', nargs='*', default=[]); ap.add_argument('--budget-first-kb', type=int, default=0)
    ap.add_argument('--click', nargs='*', default=[], help='селекторы, по которым кликнуть после load (состояние)')
    ap.add_argument('--width', type=int, default=1440); ap.add_argument('--height', type=int, default=900)
    ap.add_argument('--dpr', type=float, default=1); ap.add_argument('--wait', type=int, default=4000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    local = os.path.exists(a.target)
    tag = ('mobile' if a.mobile else f'{a.width}x{a.height}') + ('_thr' if a.throttle else '') + ('_dark' if a.dark else '') + ('_click' if a.click else '')
    with browser_lock(), contextlib.ExitStack() as st:
        if local:
            base = st.enter_context(serve(os.path.dirname(os.path.abspath(a.target))))
            url = base + '/' + urllib.parse.quote(os.path.basename(a.target))
        else:
            url = a.target
        p = st.enter_context(sync_playwright())
        no = run_once(p, url, a, False)
        rm = None if a.no_rm else run_once(p, url, a, True)
    for r, nm in ((no, 'shot'), (rm, 'shot_rm')):
        if r:
            Image.open(io.BytesIO(r.pop('screenshot'))).convert('RGB').save(os.path.join(a.out, f'{nm}_{tag}.jpg'), quality=82)
    out = {'target': a.target, 'mode': tag, 'date': time.strftime('%Y-%m-%d %H:%M'), 'chromium': '153 CfT (channel=chromium)',
           'no_preference': no, 'reduce': rm, 'verdict': verdict(no, rm, a)}
    with open(os.path.join(a.out, f'accept_{tag}.json'), 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    v = out['verdict']
    print(json.dumps({'mode': tag, 'pass': v['pass'], 'fail': v['fail'], 'warn': v['warn'][:6],
                      'lcp': no['lcp'] and {k: (round(no['lcp'][k]) if k == 't' else no['lcp'][k]) for k in ('tag', 'url', 't', 'size')},
                      'first_kb': no['first_screen_total_kb'], 'cls': no['cls']}, ensure_ascii=False))
    sys.exit(0 if v['pass'] else 1)


if __name__ == '__main__':
    main()
