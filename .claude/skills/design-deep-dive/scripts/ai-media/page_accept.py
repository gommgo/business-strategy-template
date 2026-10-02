#!/usr/bin/env python3
"""page_accept.py — приёмка страницы с ассетами в Chromium: вес, LCP, CLS, картинки, видео и постер, движение, reduce, F83.

Что меряет (одна команда — один JSON-отчёт accept_<режим>.json и вердикт FAIL / WARN):
  • вес первого экрана по CDP (картинки, видео, JS, CSS, шрифты) за окно первого экрана — load + window_after_load_s
    (budgets.yaml site, conditions.first_screen); с --throttle вес не сравнивается: вес — прогон без замедления сети
    (conditions.lab_weight);
  • LCP: элемент, файл, размер, время; флаги LCP-картинки (lazy, fetchpriority); CLS; TBT (сумма долгих задач − 50 мс);
  • картинки: alt, width/height, переотдача пикселей (естественная ширина / (CSS-ширина × DPR)), формат;
  • медиа первого экрана (для SG-PERF-16 ворот страницы): видео — poster, байты постера × 8 / видимая площадь (бит на
    пиксель), доля площади медиа, которую закрывает постер (poster или картинка поверх видео и холста 3D);
  • видео: autoplay/muted/loop/playsinline/poster/preload, играет ли, длительность, видимая кнопка паузы с именем;
  • 2.2.2 поведением: первый экран на 6-й секунде после load (движение или видео) и петли всей страницы — каждая найденная
    петля ставится в экран и через 6 с проверяется, движется ли она; без механизма паузы (подписи — общий список
    page_gates.PAUSE_LABELS) — провал. С --first-screen-only — только первый экран, отчёт помечает это (петли ниже —
    motion_check.py);
  • prefers-reduced-motion: второй прогон с reduce записью всей страницы — байты видео (нужно 0), движение первого экрана и
    каждой паузы прокрутки, % пикселей за 1 с в двух парах кадров подряд — непрерывное движение есть в обеих, разовое
    появление или подмена постера — в одной (порог — ворота эффектов creative EG-A11Y-06);
  • контраст текста поверх медиа по WCAG F83 «по буквам» (--contrast SELECTOR …): снимок с текстом и с прозрачным текстом,
    маска букв — их разница, контраст цвета текста к каждому пикселю фона под буквами (худший, p1, p5); у видео-фона — по
    кадрам 0, 25, 50, 75 % длительности, итог — худший кадр;
  • фавиконы и og:image (есть ли, размеры в разметке); --acceptance — картинки и горизонтальный вылет на ширинах приёмки
    (kb/common/acceptance-widths.yaml; ширины не больше окна телефона лаборатории — с DPR и касанием его дескриптора, шире —
    с DPR десктопа, явный --dpr задаёт DPR на всех ширинах; вылет больше limits.overflow_px строки SG-MOB-01 — WARN; с
    --dark — тёмная тема).
Пороги: с --budget-profile <page_type>@L<n> — профиль site (page_gates.py): вес первого экрана выше профиля — WARN; LCP
выше цели — WARN, выше «плохо» — FAIL; CLS так же. Без профиля вес не сравнивается, а LCP и CLS — только по порогам, общим
для всех уровней. Условия лаборатории (телефон — дескриптор Pixel 7, CPU ×4, сеть; десктоп — окно и DPR) — budgets.yaml
conditions; UA — как у браузера (HeadlessChrome), автоматизация не маскируется.
Замер времени — на тихой машине: утилита берёт общий тяжёлый замок, потом замок браузера (page_gates.heavy_lock); замки,
которые уже держит обёртка (slot_run.py, flock), повторно не берутся.

Запуск (код-репо — соседним чекаутом ../strategy/.claude/skills/design-deep-dive/scripts/ai-media/page_accept.py):
  page_accept.py PAGE.html|URL --out DIR [--budget-profile landing-saas@L1] [--mobile] [--throttle] [--no-rm] [--root DIR]
      [--contrast SELECTOR …] [--dark] [--click SELECTOR …] [--wait MS] [--first-screen-only] [--loops 3] [--acceptance]
      [--width W --height H --dpr D] [--no-lock] [--strict]
  page_accept.py --selftest
  PAGE.html — локальный файл: корень раздачи — --root или подъём по ссылкам ../ в HTML (как у motion_check.py); сервер с Range
  для видео закрывается после прогона.
Код выхода: 0 — замер выполнен (находки — в отчёте и в выводе; вердикт страницы решает page_gates.py по отчёту), 2 — ошибка
вызова или запуска, прочий ненулевой — сбой замера. С --strict — выход по находкам: 1 — есть провалы (verdict.fail).
Зависимости: Playwright (Chromium), numpy, Pillow, PyYAML."""
import argparse, contextlib, http.server, io, json, math, os, re, socketserver, sys, threading, time, urllib.parse
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))  # перенос: scripts/lib
import kbpaths  # noqa: E402
kbpaths.use('site')
import page_gates as PG  # noqa: E402  профиль бюджета, условия замера, тишина машины
EFFECT_GATES = str(kbpaths.kb('creative', '09-ai-execution-evaluation', 'effect-gates.yaml'))
WIDTHS = str(kbpaths.kb(None, 'common', 'acceptance-widths.yaml'))
MIME = {'.avif': 'image/avif', '.webp': 'image/webp', '.jxl': 'image/jxl', '.webm': 'video/webm', '.mp4': 'video/mp4',
        '.svg': 'image/svg+xml', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
        '.html': 'text/html; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon',
        '.json': 'application/json', '.webmanifest': 'application/manifest+json', '.woff2': 'font/woff2'}
MOTION_PX = 12   # изменённый пиксель — разница > 12/255 хотя бы в одном канале (метод motion_check.py и F effect_bench)
OVERSERVE_MAX = 2.0   # переотдача картинки первого экрана (естественная ширина / CSS-ширина × DPR) выше — WARN; строки ворот нет


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


def local_root(page_path, root=None):
    """Корень раздачи локальной страницы: --root или подъём на глубину самых длинных ссылок «../» в HTML."""
    if root:
        return os.path.abspath(root)
    d = os.path.dirname(os.path.abspath(page_path))
    try:
        html = open(page_path, encoding='utf-8', errors='ignore').read()
    except OSError:
        return d
    depth = max([len(m.group(1)) // 3 for m in re.finditer(r"""(?:src|href|url|poster)\s*[=(]\s*["']?((?:\.\./)+)""", html)] + [0])
    for _ in range(min(depth, 6)):
        d = os.path.dirname(d)
    return d


# ---------------------------------------------------------------- данные: профиль, окно, пороги
def load_yaml(path):
    import yaml
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def common_outcome(budgets, key, device, part):
    """Порог исхода, общий для всех уровней (LCP «плохо», CLS цель и «плохо»): одно значение у L0–L2 или None."""
    vals = {PG.profile_value({'outcome': lv.get('outcome') or {}}, f'outcome.{key}', device, part)
            for lv in (budgets.get('levels') or {}).values()}
    return vals.pop() if len(vals) == 1 else None


def thresholds(a, budgets, device):
    """Пороги прогона: из профиля (--budget-profile) или общие для всех уровней; вес — только с профилем."""
    out = {'profile': None}
    if a.budget_profile:
        prof = PG.resolve_profile(a.budget_profile, budgets)
        out['profile'] = {'id': prof['id'], 'level': prof['level'], 'log': prof['log']}
        pv = lambda path, part='goal': PG.profile_value(prof, path, device, part)  # noqa: E731
        out.update(first_screen_kb=pv('weight.first_screen_kb.<device>'),
                   lcp_goal=pv('outcome.lcp_ms_lab.<device>'), lcp_poor=pv('outcome.lcp_ms_lab.<device>', 'poor'),
                   cls_goal=pv('outcome.cls_lab'), cls_poor=pv('outcome.cls_lab', 'poor'))
    else:
        out.update(first_screen_kb=None, lcp_goal=None, lcp_poor=common_outcome(budgets, 'lcp_ms_lab', device, 'poor'),
                   cls_goal=common_outcome(budgets, 'cls_lab', device, 'goal'),
                   cls_poor=common_outcome(budgets, 'cls_lab', device, 'poor'))
    return out


def effect_gate(gid):
    """Строка ворот эффектов creative (effect-gates.yaml) по id."""
    for g in (load_yaml(EFFECT_GATES).get('gates') or []):
        if g.get('id') == gid:
            return g
    raise KeyError(f'нет строки {gid} в {EFFECT_GATES}')


def acceptance_widths():
    d = load_yaml(WIDTHS)
    return [int(w) for w in d['widths']], d.get('overflow_only')


# ---------------------------------------------------------------- JS-сборщики
INSTALL = """() => { window.__lcp = []; window.__cls = 0; window.__lt = [];
  window.__paSel = (el) => { if (!el || !el.tagName) return ''; const id = el.id ? '#' + el.id : '';
    const c = (typeof el.className === 'string' && el.className.trim()) ? '.' + el.className.trim().split(/\\s+/).slice(0, 2).join('.') : '';
    return (el.tagName.toLowerCase() + id + c).slice(0, 80); };
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lcp.push({t: e.startTime, size: e.size,
     tag: e.element && e.element.tagName, id: e.element && (e.element.id || e.element.className || ''),
     url: e.url || '', lazy: e.element && e.element.loading === 'lazy',
     fp: e.element && (e.element.getAttribute('fetchpriority') || '')}); }).observe({type: 'largest-contentful-paint', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; }).observe({type: 'layout-shift', buffered: true});
  new PerformanceObserver(l => { for (const e of l.getEntries()) window.__lt.push(e.duration); }).observe({type: 'longtask', buffered: true});
  try { const orig = HTMLCanvasElement.prototype.getContext;
    HTMLCanvasElement.prototype.getContext = function (type, ...a) { const ctx = orig.call(this, type, ...a);
      if (ctx && /webgl/i.test(String(type)) && !ctx.__pa) { ctx.__pa = 1; const cv = this;
        for (const fn of ['drawArrays', 'drawElements', 'drawArraysInstanced', 'drawElementsInstanced', 'drawRangeElements']) {
          const o = ctx[fn]; if (typeof o === 'function') ctx[fn] = function (...x) { cv.__paCalls = (cv.__paCalls || 0) + 1; return o.apply(this, x); }; } }
      return ctx; }; } catch (e) {}
}"""

DOM = r"""() => {
  const dpr = devicePixelRatio, vh = innerHeight, vw = innerWidth;
  const imgs = [...document.images].map(i => { const r = i.getBoundingClientRect();
    return {src: (i.currentSrc || i.src).split('/').slice(-2).join('/'), url: i.currentSrc || i.src, alt: i.hasAttribute('alt') ? i.alt : null,
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
  return {imgs, vids, icons, og, svgInlineChars: svgInline, vw, vh, dpr, lang: document.documentElement.lang,
          ua: navigator.userAgent, webdriver: navigator.webdriver,
          overflow_px: Math.max(0, document.documentElement.scrollWidth - innerWidth)};
}"""

# Медиа первого экрана (SG-PERF-16): видео и холсты с площадью; постер — атрибут poster видео или самая крупная видимая
# картинка поверх медиа (пересечение ≥ 50 % её площади); cover_share — площадь постера к площади медиа.
MEDIA = r"""() => { const vh = innerHeight, vw = innerWidth, sel = window.__paSel || (e => e.tagName);
  const vis = (el) => { const s = getComputedStyle(el); return s.display !== 'none' && s.visibility !== 'hidden'; };
  const area = (r) => Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0)) * Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
  const inter = (a, b) => Math.max(0, Math.min(a.right, b.right) - Math.max(a.left, b.left)) * Math.max(0, Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top));
  const imgs = [...document.images].filter(i => vis(i)).map(i => ({i, r: i.getBoundingClientRect()})).filter(x => area(x.r) > 0);
  const out = [];
  for (const el of [...document.querySelectorAll('video, canvas')]) { const r = el.getBoundingClientRect(); const A = area(r);
    if (!vis(el) || A < vw * vh * 0.05) continue;
    let best = null; for (const x of imgs) { const ia = x.r.width * x.r.height; if (ia > 0 && inter(x.r, r) >= 0.5 * ia && (!best || ia > best.a)) best = {a: ia, url: x.i.currentSrc || x.i.src}; }
    const isV = el.tagName === 'VIDEO'; const poster = isV ? (el.getAttribute('poster') || '') : '';
    const posterUrl = poster ? new URL(poster, location.href).href : (best ? best.url : '');
    const cover = isV && poster ? 1 : (best ? +(best.a / (r.width * r.height)).toFixed(3) : null);
    out.push({kind: isV ? 'video' : 'canvas', sel: sel(el), src: isV ? (el.currentSrc || '').split('/').pop() : '', poster: !!poster || !!best,
              poster_attr: !!poster, poster_url: posterUrl, area_css: Math.round(r.width * r.height), cover_share: cover,
              autoplay: isV ? el.autoplay : null, playing: isV ? (!el.paused && el.readyState > 2) : null}); }
  return out; }"""

PAUSE = r"""() => [...document.querySelectorAll('button, [role=button], [role=switch], input[type=checkbox], [aria-pressed], [data-motion-toggle], [data-motion-set]')]
  .some(b => { const s = getComputedStyle(b); if (b.hidden || s.display === 'none' || s.visibility === 'hidden') return false;
    return b.hasAttribute('data-motion-toggle') || b.hasAttribute('data-motion-set')
      || __PAUSE_RE__.test((b.getAttribute('aria-label') || '') + ' ' + (b.textContent || '')); })""".replace('__PAUSE_RE__', PG.pause_label_re_js())

# Петли в видимой зоне: бесконечные анимации (CSS и WAAPI), играющие видео, холсты WebGL с вызовами отрисовки с прошлого
# вызова (первый вызов в позиции только отмечает счётчики).
LOOPS = r"""(prime) => { const IH = innerHeight, IW = innerWidth, sel = window.__paSel || (e => e.tagName);
  const inV = (r) => r.bottom > 0 && r.top < IH && r.right > 0 && r.left < IW && r.width >= 24 && r.height >= 24;
  const out = [];
  if (!prime) { try { for (const a of document.getAnimations()) { let t = {}; try { t = a.effect.getTiming(); } catch (e) {}
      if (a.playState !== 'running' || t.iterations !== Infinity) continue; const tg = a.effect && a.effect.target;
      if (!tg || !tg.getBoundingClientRect || !inV(tg.getBoundingClientRect())) continue;
      out.push({kind: 'anim', sel: sel(tg), y: Math.round(tg.getBoundingClientRect().top + scrollY)}); } } catch (e) {}
    document.querySelectorAll('video').forEach(v => { const r = v.getBoundingClientRect();
      if (!v.paused && !v.ended && v.readyState > 2 && inV(r)) out.push({kind: 'video', sel: sel(v), y: Math.round(r.top + scrollY)}); }); }
  document.querySelectorAll('canvas').forEach(c => { const n = c.__paCalls || 0; const d = n - (c.__paPrev || 0); c.__paPrev = n;
    const r = c.getBoundingClientRect(); if (!prime && d > 0 && inV(r)) out.push({kind: 'webgl', sel: sel(c), y: Math.round(r.top + scrollY)}); });
  return out; }"""

LOOP_6S = r"""async (o) => { const sel = window.__paSel || (e => e.tagName);
  const el = [...document.querySelectorAll('*')].find(e => sel(e) === o.sel); if (!el) return {sel: o.sel, found: false};
  el.scrollIntoView({block: 'center'}); await new Promise(r => setTimeout(r, o.wait));
  const an = el.getAnimations ? el.getAnimations({subtree: true}).filter(a => a.playState === 'running').length : 0;
  const vid = el.tagName === 'VIDEO' ? !el.paused : false; const c0 = el.__paCalls || 0; await new Promise(r => setTimeout(r, 500));
  return {sel: o.sel, found: true, running_anims: an, video_playing: vid, webgl_calls_0_5s: (el.__paCalls || 0) - c0}; }"""


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


def shot_rgb(page):
    return np.asarray(Image.open(io.BytesIO(page.screenshot())).convert('RGB')).astype(np.int16)


def motion_pct(a, b):
    """Доля изменённых пикселей, % (разница > MOTION_PX хотя бы в одном канале)."""
    if a.shape != b.shape:
        return None
    return round(float((np.abs(a - b).max(axis=2) > MOTION_PX).mean() * 100), 3)


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


# ---------------------------------------------------------------- прогон
def context_kw(p, a, cond, reduce):
    if a.mobile:
        kw = PG.mobile_device(p, cond)
    else:
        kw = {'viewport': {'width': a.width, 'height': a.height}, 'device_scale_factor': a.dpr}
    kw['reduced_motion'] = 'reduce' if reduce else 'no-preference'
    kw['color_scheme'] = 'dark' if a.dark else 'light'
    return kw


def scroll_steps(page, H, max_steps=12):
    total = page.evaluate("Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0) - innerHeight")
    return max(0, min(max_steps, math.ceil(max(total, 0) / (0.8 * H)))), int(0.8 * H)


def page_loops(page, a, H):
    """Петли всей страницы (2.2.2): прокрутка шагами, в каждой позиции — петли в зоне видимости; первые --loops петель —
    в экран и через 6 с: движется ли ещё."""
    seen, found = [], []
    steps, delta = scroll_steps(page, H)
    page.evaluate("() => window.scrollTo(0, 0)")
    for step in range(steps + 1):
        if step:
            page.mouse.wheel(0, delta)
        page.wait_for_timeout(350)
        page.evaluate(LOOPS, True)
        page.wait_for_timeout(500)
        for lp in page.evaluate(LOOPS, False):
            if lp['sel'] not in seen:
                seen.append(lp['sel']); found.append(lp)
    checked = []
    for lp in found[:a.loops]:
        try:
            r = page.evaluate(LOOP_6S, {'sel': lp['sel'], 'wait': 6000})
        except Exception as e:
            r = {'sel': lp['sel'], 'error': str(e)[:100]}
        r['kind'] = lp['kind']
        r['moving'] = bool(r.get('running_anims') or r.get('video_playing') or (r.get('webgl_calls_0_5s') or 0) > 0)
        checked.append(r)
    page.evaluate("() => window.scrollTo(0, 0)")
    return found, checked


def reduce_pauses(page, H):
    """Reduce записью всей страницы: в каждой паузе прокрутки — доля изменённых пикселей за 1 с в двух парах кадров подряд;
    непрерывное движение — в обеих (меньшая из двух), разовое появление или подмена постера — в одной."""
    out = []
    steps, delta = scroll_steps(page, H)
    for step in range(1, steps + 1):
        page.mouse.wheel(0, delta)
        page.wait_for_timeout(500)
        s1 = shot_rgb(page)
        page.wait_for_timeout(1000)
        s2 = shot_rgb(page)
        page.wait_for_timeout(1000)
        s3 = shot_rgb(page)
        pair = [motion_pct(s1, s2), motion_pct(s2, s3)]
        out.append({'step': step, 'y': page.evaluate('Math.round(scrollY)'), 'pct_1s': min(x for x in pair if x is not None) if any(x is not None for x in pair) else None,
                    'pairs': pair})
    return out


def run_once(p, url, a, reduce, cond, rm_limit, moving_min):
    b = p.chromium.launch(channel='chromium', headless=True)
    ctx = b.new_context(**context_kw(p, a, cond, reduce))
    page = ctx.new_page()
    cdp = ctx.new_cdp_session(page)
    cdp.send('Network.enable'); cdp.send('Network.setCacheDisabled', {'cacheDisabled': True})
    if a.throttle:
        cdp.send('Network.emulateNetworkConditions', PG.cdp_network(cond))
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': cond['mobile']['cpu_slowdown'] if a.mobile else cond['desktop']['cpu_slowdown']})
    elif a.mobile:
        cdp.send('Emulation.setCPUThrottlingRate', {'rate': cond['mobile']['cpu_slowdown']})
    ev = {}
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
    bytes_by_url = {}
    for t, u, n in (tuple(v) for v in ev.values()):
        bytes_by_url[u] = bytes_by_url.get(u, 0) + n
    reqs = sorted(((t, u.split('?')[0].split('/')[-1], round(n / 1024, 1)) for t, u, n in (tuple(v) for v in ev.values()) if n), key=lambda x: -x[2])
    H = (page.viewport_size or {}).get('height') or a.height
    s1 = shot_rgb(page)
    page.wait_for_timeout(1000)
    shot = page.screenshot()
    s2 = np.asarray(Image.open(io.BytesIO(shot)).convert('RGB')).astype(np.int16)
    idle_motion = motion_pct(s1, s2)
    # движение дольше 5 с (WCAG 2.2.2): что ещё движется на 6-й секунде после load
    page.wait_for_timeout(max(0, 6000 - a.wait - 1000))
    late1 = shot_rgb(page)
    page.wait_for_timeout(1000)
    late2 = shot_rgb(page)
    late_motion = motion_pct(late1, late2)
    late_playing = page.evaluate("() => [...document.querySelectorAll('video')].filter(v => !v.paused && v.readyState > 2).length")
    any_pause_btn = page.evaluate(PAUSE)
    lcp = page.evaluate('window.__lcp'); cls = page.evaluate('window.__cls'); lt = page.evaluate('window.__lt')
    dom = page.evaluate(DOM)
    media = page.evaluate(MEDIA)
    for m in media:
        n = bytes_by_url.get(m.get('poster_url') or '')
        m['poster_kb'] = round(n / 1024, 1) if n else None
        m['poster_bpp'] = round(n * 8 / m['area_css'], 4) if n and m.get('area_css') else None
    res = {'reduce': reduce, 'first_screen_kb': first, 'first_screen_total_kb': round(sum(first.values()), 1),
           'weight_measured': not a.throttle, 'requests': reqs[:40],
           'lcp': lcp[-1] if lcp else None, 'lcp_candidates': [(x['tag'], x['size'], round(x['t'])) for x in lcp],
           'cls': round(cls, 4), 'tbt_ms': round(sum(max(0, d - 50) for d in lt)), 'idle_motion_pct': idle_motion,
           'motion_after_6s_pct': late_motion, 'videos_playing_after_6s': late_playing, 'pause_control': any_pause_btn,
           'motion_6s': {'pct': late_motion, 'videos_playing': late_playing, 'pause_control': any_pause_btn,
                         'moving': bool(late_playing or (late_motion or 0) >= moving_min)},
           'dom': dom, 'media_first': media, 'secs': None, 'screenshot': shot}
    if a.contrast and not reduce:
        res['contrast'] = f83(page, a.contrast)
    if not reduce:
        if a.first_screen_only:
            res['loops'] = {'scope': 'first_screen', 'found': [], 'checked': [], 'without_pause': []}
        else:
            found, checked = page_loops(page, a, H)
            moving = [c['sel'] for c in checked if c.get('moving')]
            res['loops'] = {'scope': 'page', 'found': found[:12], 'checked': checked, 'pause_control': any_pause_btn,
                            'without_pause': [] if any_pause_btn else moving}
    else:
        pauses = [] if a.first_screen_only else reduce_pauses(page, H)
        sess = {k: round(v / 1024, 1) for k, v in cdp_bytes({k: tuple(v) for k, v in ev.items()}).items()}
        fail = []
        pair = [x for x in (idle_motion, late_motion) if x is not None]
        still = min(pair) if pair else None            # первый экран: две пары кадров подряд, непрерывное — в обеих
        if still is not None and still > rm_limit:
            fail.append(f'первый экран {still} %/с > {rm_limit}')
        fail += [f"пауза {x['step']} (y {x['y']}): {x['pct_1s']} %/с > {rm_limit}" for x in pauses
                 if x['pct_1s'] is not None and x['pct_1s'] > rm_limit]
        res['media_kb'] = sess.get('media', 0)
        res['session_kb'] = sess
        res['motion'] = {'scope': 'first_screen' if a.first_screen_only else 'page', 'threshold_pct_s': rm_limit,
                         'first_pct_1s': still, 'first_pairs': [idle_motion, late_motion], 'pauses': pauses,
                         'max_pct_1s': max([x['pct_1s'] or 0 for x in pauses] + [still or 0]), 'fail': fail}
    res['console'] = msgs[:20]
    res['secs'] = round(time.time() - t0, 1)
    browser = b.version
    ctx.close(); b.close()
    return res, browser


def acceptance_context(w, a, phone):
    """Окно ширины приёмки: ширина не больше окна телефона лаборатории — телефон (DPR, касание, UA и высота окна
    дескриптора conditions.lab_mobile), шире — окно десктопа лаборатории (высота и DPR прогона); явный --dpr — DPR на всех
    ширинах; с --dark — тёмная тема."""
    if w <= phone['viewport']['width']:
        kw = dict(phone, viewport={'width': w, 'height': phone['viewport']['height']})
    else:
        kw = {'viewport': {'width': w, 'height': a.height}, 'device_scale_factor': a.dpr}
    if getattr(a, 'dpr_set', False):
        kw['device_scale_factor'] = a.dpr
    kw['color_scheme'] = 'dark' if a.dark else 'light'
    return kw


def acceptance_run(p, url, a, cond):
    """Ширины приёмки (kb/common/acceptance-widths.yaml): переотдача картинок, картинки без размеров, горизонтальный вылет;
    на ширине overflow_only — только вылет. Окно ширины — acceptance_context (узкие ширины — телефон лаборатории). Вылет —
    ширина документа минус ширина приёмки: телефон расширяет область раскладки под широкое содержимое, и innerWidth
    вылета не показывает."""
    widths, over_only = acceptance_widths()
    phone = PG.mobile_device(p, cond)
    out = []
    b = p.chromium.launch(channel='chromium', headless=True)
    try:
        for w in widths + ([over_only] if over_only else []):
            kw = acceptance_context(w, a, phone)
            ctx = b.new_context(**kw)
            page = ctx.new_page()
            page.goto(url, wait_until='load', timeout=120000)
            page.wait_for_timeout(800)
            d = page.evaluate(DOM)
            row = {'width': w, 'device': 'mobile' if kw.get('is_mobile') else 'desktop', 'dpr': d['dpr'],
                   'overflow_px': max(0, d['overflow_px'] + d['vw'] - w)}
            if w != over_only:
                row['over'] = [f"{i['src']} ×{i['over']}" for i in d['imgs'] if i['above'] and i['over'] and i['over'] > OVERSERVE_MAX]
                row['no_wh'] = [i['src'] for i in d['imgs'] if not i['wh']][:6]
            out.append(row)
            ctx.close()
    finally:
        b.close()
    return out


def verdict(no, rm, th, acc_rows=None):
    fail, warn, ok = [], [], []
    tot = no['first_screen_total_kb']
    if not no.get('weight_measured', True):
        ok.append(f'первый экран {tot} КБ — с замедлением сети не сравнивается (вес — прогон без --throttle)')
    elif th.get('first_screen_kb') is None:
        ok.append(f'первый экран {tot} КБ — без --budget-profile не сравнивается')
    else:
        (ok if tot <= th['first_screen_kb'] else warn).append(f"первый экран {tot} КБ ≤ {th['first_screen_kb']} (профиль)")
    l = no['lcp']
    if l:
        (fail if l.get('lazy') else ok).append(f"LCP-элемент {l['tag']} без loading=lazy" if not l.get('lazy') else 'LCP-картинка с loading=lazy')
        if l['tag'] == 'IMG' and l.get('fp') != 'high':
            warn.append('LCP-картинка без fetchpriority="high"')
        t = round(l['t'])
        if th.get('lcp_poor') is not None and t > th['lcp_poor']:
            fail.append(f"LCP {t} мс > {th['lcp_poor']} (плохо)")
        elif th.get('lcp_goal') is not None and t > th['lcp_goal']:
            warn.append(f"LCP {t} мс > {th['lcp_goal']} (цель профиля)")
        else:
            ok.append(f'LCP {t} мс')
    else:
        fail.append('нет ни одной записи LCP (всё появляется из opacity 0?)')
    c = no['cls']
    if th.get('cls_poor') is not None and c > th['cls_poor']:
        fail.append(f"CLS {c} > {th['cls_poor']} (плохо)")
    elif th.get('cls_goal') is not None and c > th['cls_goal']:
        warn.append(f"CLS {c} > {th['cls_goal']} (цель)")
    else:
        ok.append(f'CLS {c}')
    for im in no['dom']['imgs']:
        if im['alt'] is None: fail.append(f"нет alt: {im['src']}")
        if not im['wh']: warn.append(f"нет width/height: {im['src']}")
        if im['above'] and im['over'] and im['over'] > OVERSERVE_MAX: warn.append(f"переотдача ×{im['over']}: {im['src']}")
    for v in no['dom']['vids']:
        if v['above'] and (v['autoplay'] or v['playing']):
            if not (v['muted'] and v['playsinline']): fail.append(f"видео без muted/playsinline: {v['src']}")
            if (v['duration'] or 0) > 5 and not v['pause_button']: fail.append(f"петля > 5 с без кнопки паузы: {v['src']} (WCAG 2.2.2)")
    m6 = no['motion_6s']
    if m6['moving'] and not m6['pause_control']:
        fail.append(f"движение дольше 5 с без кнопки паузы (видео {m6['videos_playing']}, пикселей {m6['pct']} %) — WCAG 2.2.2")
    lp = no.get('loops') or {}
    if lp.get('without_pause'):
        fail.append('петли без механизма паузы через 6 с после показа: ' + ', '.join(lp['without_pause'][:3]) + ' — WCAG 2.2.2')
    if lp.get('scope') == 'first_screen':
        ok.append('петли — только первый экран (--first-screen-only): ниже — motion_check.py')
    if rm is not None:
        vb = rm.get('media_kb', 0)
        (ok if vb == 0 else fail).append(f"reduce: видео за прокрутку {vb} КБ (нужно 0)")
        mt = rm.get('motion') or {}
        if mt.get('fail'):
            fail += [f'reduce: {x}' for x in mt['fail']]
        else:
            ok.append(f"reduce: движение ≤ {mt.get('threshold_pct_s')} %/с ({mt.get('scope')})")
    for c_ in no.get('contrast', []):
        (ok if c_['pass_f83'] else fail).append(f"F83 «{c_['text'][:28]}»: худший {c_['f83_min']} (нужно {c_['need']})")
    ov_max = PG.gate_limit('SG-MOB-01', 'overflow_px') if acc_rows else None   # вылет — число строки ворот страницы
    for row in acc_rows or []:
        if (row.get('overflow_px') or 0) > ov_max:
            warn.append(f"ширина {row['width']}: горизонтальный вылет {row['overflow_px']} px > {ov_max} (SG-MOB-01)")
        warn += [f"ширина {row['width']}: переотдача {x}" for x in row.get('over') or []]
    if not any('icon' in x for x in no['dom']['icons']): warn.append('нет <link rel=icon>')
    return {'pass': not fail, 'fail': fail, 'warn': warn, 'ok': ok}


def exit_code(v, strict=False):
    """Код выхода по вердикту замера: замер выполнен — 0, находки остаются в отчёте (вердикт страницы решает page_gates.py);
    с --strict — 1 при провалах."""
    return 1 if strict and not v['pass'] else 0


def run(a):
    budgets = PG.load_budgets()
    cond = PG.conditions(budgets)
    a.wait = a.wait if a.wait is not None else PG.window_ms(budgets)
    a.width = a.width or cond['desktop']['width']
    a.height = a.height or cond['desktop']['height']
    a.dpr_set = a.dpr is not None                    # явный --dpr — DPR и на всех ширинах приёмки
    a.dpr = a.dpr or cond['desktop']['dpr']
    device = 'mobile' if a.mobile else 'desktop'
    th = thresholds(a, budgets, device)
    rm_row = effect_gate('EG-A11Y-06')
    rm_limit = float(rm_row['threshold'])
    moving_min = float((effect_gate('EG-A11Y-01').get('limits') or {})['moving_pct_min'])
    os.makedirs(a.out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    local = os.path.exists(a.target)
    tag = ('mobile' if a.mobile else f'{a.width}x{a.height}') + ('_thr' if a.throttle else '') + ('_dark' if a.dark else '') + ('_click' if a.click else '')
    lock = contextlib.nullcontext() if a.no_lock else PG.heavy_lock(domains=('ai-media',))
    with lock, contextlib.ExitStack() as st:
        if local:
            root = local_root(a.target, a.root)
            base = st.enter_context(serve(root))
            url = base + '/' + urllib.parse.quote(os.path.relpath(os.path.abspath(a.target), root))
        else:
            url = a.target
        p = st.enter_context(sync_playwright())
        no, browser = run_once(p, url, a, False, cond, rm_limit, moving_min)
        rm = None if a.no_rm else run_once(p, url, a, True, cond, rm_limit, moving_min)[0]
        acc_rows = acceptance_run(p, url, a, cond) if a.acceptance else None
    for r, nm in ((no, 'shot'), (rm, 'shot_rm')):
        if r:
            Image.open(io.BytesIO(r.pop('screenshot'))).convert('RGB').save(os.path.join(a.out, f'{nm}_{tag}.jpg'), quality=82)
    out = {'tool': 'page_accept.py', 'target': a.target, 'url': url, 'mode': tag, 'device': device, 'throttle': bool(a.throttle),
           'viewport': [no['dom']['vw'], no['dom']['vh']], 'window_after_load_s': round(a.wait / 1000, 3), 'profile': th['profile'],
           'thresholds': {k: v for k, v in th.items() if k != 'profile'}, 'date': time.strftime('%Y-%m-%d %H:%M'),
           'chromium': browser, 'no_preference': no, 'reduce': rm, 'acceptance': acc_rows, 'verdict': verdict(no, rm, th, acc_rows)}
    with open(os.path.join(a.out, f'accept_{tag}.json'), 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    v = out['verdict']
    print(json.dumps({'mode': tag, 'profile': (th['profile'] or {}).get('id'), 'pass': v['pass'], 'fail': v['fail'], 'warn': v['warn'][:6],
                      'lcp': no['lcp'] and {k: (round(no['lcp'][k]) if k == 't' else no['lcp'][k]) for k in ('tag', 'url', 't', 'size')},
                      'first_kb': no['first_screen_total_kb'], 'cls': no['cls']}, ensure_ascii=False))
    return out


# ---------------------------------------------------------------- самопроверка
SELFTEST_HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>page_accept selftest</title><link rel="icon" href="data:,">
<style>body{margin:0;font:18px/1.5 sans-serif} header{padding:24px} h1{margin:0 0 12px;font-size:40px}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:24px;padding:0 24px} .hero img,.hero video{width:100%;height:auto;display:block}
main{padding:24px} .spacer{height:1400px;background:linear-gradient(#fff,#eef)} .loop{width:260px;height:260px;background:#c33;animation:spin 2s linear infinite}
.wide{width:340px;height:8px;background:#ccd}
@keyframes spin{to{transform:rotate(360deg)}}</style></head><body>
<header><h1>Проверка приёмки</h1><p>Картинка героя с размерами и приоритетом, видео с гладким постером, петля ниже первого экрана.</p></header>
<section class="hero"><img src="hero.png" width="600" height="400" alt="Картинка героя" fetchpriority="high">
<video poster="poster.png" width="600" height="400" muted playsinline></video></section>
<main><div class="wide"></div><div class="spacer"></div><div class="loop" aria-hidden="true"></div><p>Петля без кнопки паузы и без ветки reduce.</p></main>
</body></html>"""


def selftest():
    """Локальная страница в Chromium Playwright без сети: окно первого экрана и условия — из budgets.yaml, пороги — профиль
    site; честный UA; постер видео (энтропия); петля ниже первого экрана без паузы — провал 2.2.2 по всей странице; reduce
    записью всей страницы — порог ворот эффектов EG-A11Y-06; ширины приёмки и вылет по строке SG-MOB-01; в коде нет
    маскировки автоматизации."""
    import subprocess
    import tempfile
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(('OK   ' if cond else 'FAIL ') + msg)
    src = open(os.path.abspath(__file__), encoding='utf-8').read().split('\ndef selftest')[0]
    check('в коде нет --disable-blink-features и подмены UA на строку без Headless',
          '--disable-blink-' not in src and 'user_agent=' not in src and 'AppleWebKit' not in src)
    ap = parser()
    d = ap.parse_args(['x.html', '--out', 'o'])
    check('без ключей: окно и окно десктопа — из budgets.yaml, вес без профиля не сравнивается',
          d.wait is None and d.width is None and d.budget_profile is None)
    budgets = PG.load_budgets()
    th0 = thresholds(d, budgets, 'mobile')
    check('без профиля: LCP «плохо» и CLS — общие для всех уровней, цели LCP и веса нет',
          th0['lcp_poor'] == 4000 and th0['cls_goal'] == 0.1 and th0['cls_poor'] == 0.25 and th0['lcp_goal'] is None and th0['first_screen_kb'] is None)
    d.budget_profile = 'landing-lead-services@L1'
    th1 = thresholds(d, budgets, 'mobile')
    check('профиль landing-lead-services@L1: первый экран телефона 1 500 (overrides), LCP цель 2 500',
          th1['first_screen_kb'] == 1500 and th1['lcp_goal'] == 2500 and th1['profile']['id'] == 'landing-lead-services@L1')
    no = {'first_screen_total_kb': 1800.0, 'weight_measured': True, 'lcp': {'tag': 'IMG', 'lazy': False, 'fp': 'high', 't': 2700},
          'cls': 0.12, 'dom': {'imgs': [], 'vids': [], 'icons': ['icon']}, 'motion_6s': {'moving': False, 'pause_control': False, 'pct': 0, 'videos_playing': 0},
          'loops': {'scope': 'page', 'without_pause': []}}
    v1 = verdict(no, None, th1)
    check('вес 1 800 > 1 500 и LCP 2 700 > цели → WARN, не FAIL; CLS 0,12 → WARN', v1['pass'] and len(v1['warn']) == 3)
    no2 = dict(no, cls=0.3, lcp=dict(no['lcp'], t=4500))
    v2 = verdict(no2, None, th1)
    check('CLS 0,3 и LCP 4 500 → FAIL (плохо)', not v2['pass'] and len(v2['fail']) == 2)
    v3 = verdict(dict(no, weight_measured=False), None, th1)
    check('прогон с --throttle: вес не сравнивается', not any('первый экран' in x for x in v3['warn']))
    ov = PG.gate_limit('SG-MOB-01', 'overflow_px')
    v4 = verdict(no, None, th1, [{'width': 360, 'overflow_px': ov, 'over': [], 'no_wh': []}, {'width': 320, 'overflow_px': ov + 1}])
    check(f'ширины приёмки: вылет {ov} px — норма, {ov + 1} px — WARN (limits.overflow_px строки SG-MOB-01)',
          [x for x in v4['warn'] if 'вылет' in x] == [f'ширина 320: горизонтальный вылет {ov + 1} px > {ov} (SG-MOB-01)'])
    check('код выхода: замер с провалом — 0, с --strict — 1; без провалов — 0 и со --strict',
          (exit_code(v2), exit_code(v2, True), exit_code(v1), exit_code(v1, True)) == (0, 1, 0, 0)
          and ap.parse_args(['x.html', '--out', 'o', '--strict']).strict and not ap.parse_args(['x.html', '--out', 'o']).strict)
    check('подписи механизма паузы — page_gates.PAUSE_LABELS: выражение подставлено в PAUSE',
          PG.pause_label_re_js() in PAUSE and '__PAUSE_RE__' not in PAUSE)
    from types import SimpleNamespace
    ph = {'viewport': {'width': 412, 'height': 839}, 'device_scale_factor': 2.625, 'is_mobile': True, 'has_touch': True,
          'user_agent': 'x HeadlessChrome/1'}
    a0 = SimpleNamespace(height=900, dpr=1, dpr_set=False, dark=False)
    k412, k413 = acceptance_context(412, a0, ph), acceptance_context(413, a0, ph)
    check('ширины приёмки: до окна телефона (412) — телефон (DPR, касание, высота окна), шире — окно десктопа (DPR прогона)',
          (k412['viewport'], k412['device_scale_factor'], k412['is_mobile'], k412['has_touch'])
          == ({'width': 412, 'height': 839}, 2.625, True, True)
          and (k413['viewport'], k413['device_scale_factor'], k413.get('is_mobile')) == ({'width': 413, 'height': 900}, 1, None))
    a2 = SimpleNamespace(height=900, dpr=2.0, dpr_set=True, dark=True)
    check('явный --dpr — DPR на всех ширинах приёмки; --dark — тёмная тема',
          [acceptance_context(w, a2, ph)['device_scale_factor'] for w in (360, 1440)] == [2.0, 2.0]
          and acceptance_context(360, a2, ph)['color_scheme'] == 'dark')
    with tempfile.TemporaryDirectory() as td:
        pg = os.path.join(td, 'site', 'page')
        os.makedirs(pg)
        with open(os.path.join(pg, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(SELFTEST_HTML)
        im = np.zeros((400, 600, 3), np.uint8)
        im[..., 0] = np.linspace(40, 200, 600, dtype=np.uint8)[None, :]
        im[..., 2] = 120
        Image.fromarray(im).save(os.path.join(pg, 'poster.png'))            # гладкий градиент — низкая энтропия
        rnd = (np.random.default_rng(7).integers(0, 255, (400, 600, 3))).astype(np.uint8)
        Image.fromarray(rnd).save(os.path.join(pg, 'hero.png'))              # шум — высокая энтропия
        out = os.path.join(td, 'out')
        r = subprocess.run([sys.executable, os.path.abspath(__file__), os.path.join(pg, 'index.html'), '--out', out, '--root',
                            os.path.join(td, 'site'), '--budget-profile', 'thank-you-page@L0', '--wait', '1500', '--loops', '1',
                            '--acceptance'],
                           capture_output=True, text=True, timeout=300, env=kbpaths.playwright_env())
        js = [f for f in os.listdir(out) if f.startswith('accept_') and f.endswith('.json')] if os.path.isdir(out) else []
        rep = json.load(open(os.path.join(out, js[0]), encoding='utf-8')) if js else {}
        check(f'прогон на локальной странице: отчёт есть, провал в отчёте (петля без паузы), код замера 0 ({r.returncode}) '
              f'{r.stderr[-200:] if not js else ""}',
              bool(rep) and r.returncode == 0 and rep['verdict']['pass'] is False)
        if rep:
            npf = rep['no_preference']
            check('контракт: device, throttle, profile, window_after_load_s, no_preference, reduce',
                  rep['device'] == 'desktop' and rep['throttle'] is False and rep['profile']['id'] == 'thank-you-page@L0'
                  and rep['window_after_load_s'] == 1.5 and isinstance(rep.get('reduce'), dict))
            check('--root: страница раздана от корня, путь страницы — site/page/…', rep['url'].endswith('/page/index.html'))
            check('UA как есть — HeadlessChrome, navigator.webdriver виден', 'HeadlessChrome/' in (npf['dom'].get('ua') or '')
                  and npf['dom'].get('webdriver') is True)
            vid = [m for m in npf.get('media_first') or [] if m.get('kind') == 'video']
            check('медиа первого экрана: видео с постером, бит на пиксель посчитан и ниже 0,05 (гладкий градиент)',
                  vid and vid[0]['poster_attr'] and vid[0]['poster_bpp'] is not None and vid[0]['poster_bpp'] < 0.05 and vid[0]['cover_share'] == 1)
            lp = npf.get('loops') or {}
            check('петли всей страницы: петля ниже первого экрана найдена и движется через 6 с без паузы',
                  lp.get('scope') == 'page' and any('div.loop' in s for s in lp.get('without_pause') or []))
            mt = (rep['reduce'] or {}).get('motion') or {}
            check('reduce записью всей страницы: порог EG-A11Y-06, пауза с петлёй выше порога',
                  mt.get('threshold_pct_s') == float(effect_gate('EG-A11Y-06')['threshold']) and mt.get('scope') == 'page' and mt.get('fail'))
            check('вес первого экрана сравнён с профилем thank-you-page@L0 (1 200 КБ десктоп)',
                  rep['thresholds']['first_screen_kb'] == 1200 and any('первый экран' in x for x in rep['verdict']['ok']))
            widths, over_only = acceptance_widths()
            acc = rep.get('acceptance') or []
            check('--acceptance: строка на каждую ширину acceptance-widths.yaml (width, device, dpr, overflow_px, over[], '
                  'no_wh[]), на overflow_only — без картинок', [x['width'] for x in acc] == widths + [over_only]
                  and all(set(x) == {'width', 'device', 'dpr', 'overflow_px', 'over', 'no_wh'} for x in acc[:-1])
                  and set(acc[-1]) == {'width', 'device', 'dpr', 'overflow_px'})
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                phone = PG.mobile_device(p)
            narrow = [x for x in acc if x['width'] <= phone['viewport']['width']]
            wide = [x for x in acc if x['width'] > phone['viewport']['width']]
            byd = {x['width']: (x['device'], x['dpr']) for x in acc}
            ddpr = PG.conditions()['desktop']['dpr']
            check(f"--acceptance: узкие ширины — телефон лаборатории (DPR {phone['device_scale_factor']}), шире — десктоп "
                  f"(DPR {ddpr}): {byd}",
                  narrow and wide and all(x['device'] == 'mobile' and x['dpr'] == phone['device_scale_factor'] for x in narrow)
                  and all(x['device'] == 'desktop' and x['dpr'] == ddpr for x in wide))
            check('--acceptance: картинка героя 600 px в колонке ≈ 150 px — на телефонных ширинах без переотдачи (при DPR 1 '
                  'было бы ×4)', all(not x.get('over') for x in narrow if 'over' in x))
            byw = {x['width']: x['overflow_px'] for x in acc}
            check(f'--acceptance: блок 340 px вылетает только на узких ширинах (390 — {byw.get(390)}, 360 — {byw.get(360)}, '
                  f'{over_only} — {byw.get(over_only)} px) → WARN по SG-MOB-01',
                  byw.get(390) == 0 and byw.get(360, 0) > ov and byw.get(over_only, 0) > ov
                  and any(x.startswith('ширина 360: горизонтальный вылет') for x in rep['verdict']['warn']))
    print('page_accept selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def parser():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('target'); ap.add_argument('--out', required=True)
    ap.add_argument('--budget-profile', help='профиль бюджета <page_type>@L<n> (budgets.yaml site): вес — WARN, LCP и CLS — WARN и FAIL')
    ap.add_argument('--mobile', action='store_true'); ap.add_argument('--throttle', action='store_true')
    ap.add_argument('--no-rm', action='store_true'); ap.add_argument('--dark', action='store_true')
    ap.add_argument('--root', help='корень раздачи локальной страницы (по умолчанию — по ссылкам ../ в HTML)')
    ap.add_argument('--contrast', nargs='*', default=[])
    ap.add_argument('--click', nargs='*', default=[], help='селекторы, по которым кликнуть после load (состояние)')
    ap.add_argument('--width', type=int); ap.add_argument('--height', type=int)
    ap.add_argument('--dpr', type=float, help='DPR окна десктопа (по умолчанию — budgets.yaml); заданный явно — DPR и на всех ширинах приёмки')
    ap.add_argument('--wait', type=int, help='окно первого экрана после load, мс (по умолчанию — budgets.yaml conditions.first_screen)')
    ap.add_argument('--first-screen-only', action='store_true', help='2.2.2 и reduce — только первый экран (отчёт помечает)')
    ap.add_argument('--loops', type=int, default=3, help='сколько найденных петель проверить через 6 с после показа')
    ap.add_argument('--acceptance', action='store_true', help='картинки и вылет на ширинах приёмки (kb/common/acceptance-widths.yaml)')
    ap.add_argument('--no-lock', action='store_true', help='не брать замки тишины (обёртка их уже держит)')
    ap.add_argument('--strict', action='store_true', help='выход по находкам: код 1 при провалах (без ключа замер возвращает 0)')
    return ap


def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--selftest':
        sys.exit(selftest())
    a = parser().parse_args()
    try:
        out = run(a)
    except (ValueError, KeyError) as e:
        print(f'page_accept.py: {e}', file=sys.stderr)
        sys.exit(2)
    sys.exit(exit_code(out['verdict'], a.strict))


if __name__ == '__main__':
    main()
