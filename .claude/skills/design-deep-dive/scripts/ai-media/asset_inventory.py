#!/usr/bin/env python3
"""Обслуживание базы: этапы не зовут. asset_inventory.py — инвентарь визуальных ассетов живой страницы.

Что собирает (Playwright + Chromium, один браузер на прогон):
  * <img> и <picture>: currentSrc, srcset (число кандидатов, w/x), sizes, <source> с type/media (арт-дирекшн),
    loading, fetchpriority, decoding, alt (нет / пустой / текст), естественный и отрисованный размер, положение
    относительно первого экрана (в координатах документа), header/footer/ссылка, скругление (аватар);
  * CSS-фоны: background-image / mask-image из computed styles у элементов и ::before/::after (url() и градиенты);
  * <video>: источники и их type, poster, autoplay/muted/loop/playsinline/preload/controls, играет ли (событие
    playing), длительность, videoWidth/Height, кнопка паузы рядом (эвристика по aria-label/тексту);
  * SVG: inline (иконки / логотипы / иллюстрации по размеру, байты разметки, <image> внутри, SMIL/CSS-анимация),
    внешние .svg, спрайты <use>; Lottie (lottie-player, dotlottie, SVG lottie-web по __lottie_element, JSON-запросы с
    ключами v/fr/ip/op/layers, .lottie), Rive (.riv), canvas с типом контекста (перехват getContext), iframe-видео;
  * сеть: переданные байты каждого ответа — максимум из Playwright request.sizes и CDP Network (dataReceived /
    loadingFinished / loadingFailed: браузер обрывает Range-запросы видео, и requestfinished не приходит; HLS/DASH/CMAF-сегменты
    и blob: учитываются), формат по сигнатуре первых байт
    (JPEG, PNG, GIF, WebP, AVIF, HEIC, JXL, ICO, SVG, MP4/MOV, WebM, Lottie JSON, dotLottie, Rive, woff2),
    размеры картинки из самого файла (Pillow) — в том числе для CSS-фонов;
  * LCP с элементом (тег, url, текст) и привязкой к ассету, CLS, «движение в покое» (доля пикселей, изменившихся за
    1 с на первом экране), вес до прокрутки и после прокрутки, meta og:image (скачивается: байты, формат, размеры),
    фавиконы, preload картинок;
  * эвристика слота: hero (первый экран, ≥ 15 % площади вьюпорта) / logo-wall / avatar / icon / nav / footer /
    content-large / content-small — для ручной проверки по контактному листу;
  * библиотеки по рантайму: GSAP и ScrollTrigger — по window.gsapVersions, свойству _gsap у элементов и .pin-spacer
    (бандл глобал window.gsap не ставит; метод — kb/creative/03-live-sites-measured/01-effects-sites-measured.md
    §1.1), three.js, Lottie, Rive, Webflow, Framer, Next, Nuxt, Shopify.

Автоматизация не маскируется: UA — как есть (десктоп — строка Playwright с HeadlessChrome, телефон — дескриптор
Pixel 7 с HeadlessChrome), признак автоматизации Blink не выключается, navigator.webdriver не трогается; UA и
navigator.webdriver страницы пишутся в инвентарь. Вход, капча и антибот — отсев страницы, не обход.

Использование:
  python3 asset_inventory.py URL OUT_DIR [--mobile] [--reduced-motion] [--quick] [--throttle] [--wait 6000]
                             [--timeout 90] [--steps N] [--wait-until load|domcontentloaded|commit] [--keep-shots]
                             [--dpr 1] [--no-og]
  python3 asset_inventory.py --selftest      локальная страница file:// в Chromium Playwright: UA, webdriver, признаки
                                             GSAP, телефон; без сети
  --quick        без прокрутки (только первый экран): для парных прогонов reduce / обычный;
  --mobile       дескриптор Playwright "Pixel 7" (412×839 CSS, DPR 2.625, UA Android с HeadlessChrome);
  --throttle     CPU×4 + 150 мс RTT + 1,6 Мбит/с (как пресет Lighthouse; как site_probe.py).
Результат: OUT_DIR/inv[_mobile][_rm][_quick].json (полный инвентарь), sheet[...].jpg (контактный лист JPEG),
краткая сводка в stdout (JSON). Отдельные скриншоты удаляются (флаг --keep-shots оставляет).
Ограничения: headless Chromium Playwright: H.264/AV1/VP9 играет, HEVC — нет; куки-баннеры не закрываются; сайты с
защитой от ботов могут отдать заглушку (смотри title и контактный лист).
"""
import io, json, os, re, sys, time
from urllib.parse import urlparse

GPU_ARGS = ["--use-gl=angle", "--use-angle=gl", "--ignore-gpu-blocklist", "--enable-gpu",
            "--autoplay-policy=no-user-gesture-required"]

INIT = r"""(() => {
  if (window.__inv) return;
  const P = window.__inv = {lcp: [], cls: 0, ctx: [], playing: 0, lt: 0};
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) { const el = e.element; const i = P.lcp.length;
      if (el) { try { el.__lcpIdx = i; } catch (x) {} }
      let txt = null; try { if (el && !e.url) txt = (el.innerText || el.textContent || '').trim().slice(0, 80); } catch (x) {}
      let rect = null; try { if (el) { const r = el.getBoundingClientRect(); rect = [Math.round(r.left), Math.round(r.top + scrollY), Math.round(r.width), Math.round(r.height)]; } } catch (x) {}
      P.lcp.push({t: Math.round(e.startTime), render: Math.round(e.renderTime || 0), load: Math.round(e.loadTime || 0), size: e.size,
        tag: el ? el.tagName : null, url: (e.url || '').slice(0, 300), id: el && el.id ? el.id.slice(0, 60) : null,
        cls: el && typeof el.className === 'string' ? el.className.slice(0, 80) : null, text: txt, rect}); } })
    .observe({type: 'largest-contentful-paint', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) P.cls += e.value; }).observe({type: 'layout-shift', buffered: true}); } catch (e) {}
  try { new PerformanceObserver(l => { for (const e of l.getEntries()) P.lt += Math.max(0, e.duration - 50); }).observe({type: 'longtask', buffered: true}); } catch (e) {}
  const gc = HTMLCanvasElement.prototype.getContext;
  HTMLCanvasElement.prototype.getContext = function (type, attrs) { const r = gc.call(this, type, attrs);
    try { if (!this.__ctxType && r) { this.__ctxType = type; P.ctx.push(type); } } catch (e) {} return r; };
  if (HTMLCanvasElement.prototype.transferControlToOffscreen) { const tc = HTMLCanvasElement.prototype.transferControlToOffscreen;
    HTMLCanvasElement.prototype.transferControlToOffscreen = function () { this.__ctxType = 'offscreen'; P.ctx.push('offscreen'); return tc.call(this); }; }
  document.addEventListener('playing', e => { try { if (e.target && e.target.tagName === 'VIDEO') { if (!e.target.__played) P.playing++; e.target.__played = true; } } catch (x) {} }, true);
})();"""

DOM = r"""(() => {
  const VW = innerWidth, VH = innerHeight, SX = scrollX, SY = scrollY;
  const abs = u => { if (!u) return u; try { return new URL(u, location.href).href; } catch (e) { return u; } };
  const box = el => { const r = el.getBoundingClientRect(); return {x: Math.round(r.left + SX), y: Math.round(r.top + SY), w: Math.round(r.width), h: Math.round(r.height)}; };
  const vis = (el, b) => { if (!b || b.w < 2 || b.h < 2) return false;
    try { if (el.checkVisibility) return el.checkVisibility({opacityProperty: true, visibilityProperty: true}); } catch (e) {}
    const cs = getComputedStyle(el); return cs.visibility !== 'hidden' && cs.display !== 'none' && +cs.opacity > 0.01; };
  const fold = b => b.y < VH && b.y + b.h > 0;
  const vpArea = b => { const x0 = Math.max(0, b.x), y0 = Math.max(0, b.y), x1 = Math.min(VW, b.x + b.w), y1 = Math.min(VH, b.y + b.h);
    return Math.max(0, x1 - x0) * Math.max(0, y1 - y0) / (VW * VH) * 100; };
  const ctx = el => { const s = el.closest('section,[class*="hero" i],[id*="hero" i]');
    return {hdr: !!el.closest('header,[role=banner]'), nav: !!el.closest('nav'), ftr: !!el.closest('footer,[role=contentinfo]'),
      link: !!el.closest('a[href]'), heroHint: !!el.closest('[class*="hero" i],[id*="hero" i],[data-hero]'),
      sec: s ? (s.tagName.toLowerCase() + (s.id ? '#' + s.id.slice(0, 30) : '') + (typeof s.className === 'string' && s.className ? '.' + s.className.trim().split(/\s+/).slice(0, 2).join('.').slice(0, 50) : '')) : null}; };
  const round = (el, b) => { const r = parseFloat(getComputedStyle(el).borderTopLeftRadius) || 0; return r >= 0.4 * Math.min(b.w, b.h) && b.w > 0; };
  const parseSrcset = s => { if (!s) return null; const c = s.split(/,\s+(?=\S)/).map(x => x.trim()).filter(Boolean);
    const d = c.map(x => { const p = x.split(/\s+/); return p[1] || '1x'; }); const kind = d.some(x => /w$/.test(x)) ? 'w' : 'x';
    const maxw = Math.max(0, ...d.filter(x => /w$/.test(x)).map(x => parseInt(x))); return {n: c.length, kind, maxw: maxw || null}; };
  const urlsIn = v => { const out = []; if (!v || v === 'none') return out; const re = /url\(\s*(['"]?)(.*?)\1\s*\)/g; let m; while ((m = re.exec(v))) { if (m[2] && !m[2].startsWith('#') && !(m[2].startsWith(location.href.split('#')[0] + '#'))) out.push(m[2]); } return out; };
  const R = {vw: VW, vh: VH, dpr: devicePixelRatio, doc_h: Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0),
    title: document.title, lang: document.documentElement.lang || null, h1: [...document.querySelectorAll('h1')].slice(0, 2).map(h => (h.innerText || '').trim().slice(0, 120)),
    text_chars: (document.body && document.body.innerText || '').length};
  // ---------- <img>
  R.img = [...document.images].map(im => { const b = box(im); const pic = im.parentElement && im.parentElement.tagName === 'PICTURE' ? im.parentElement : null;
    const srcs = pic ? [...pic.querySelectorAll('source')].map(s => ({type: s.type || null, media: s.media || null, srcset: parseSrcset(s.srcset || s.getAttribute('data-srcset'))})) : [];
    const cs = getComputedStyle(im);
    return Object.assign({kind: 'img', src: abs(im.currentSrc || im.src || im.getAttribute('data-src') || ''), attr_src: (im.getAttribute('src') || '').slice(0, 200),
      nat: [im.naturalWidth, im.naturalHeight], box: b, vis: vis(im, b), fold: fold(b), vp_pct: +vpArea(b).toFixed(1),
      loading: im.getAttribute('loading'), fetchpriority: im.getAttribute('fetchpriority'), decoding: im.getAttribute('decoding'),
      srcset: parseSrcset(im.getAttribute('srcset') || im.getAttribute('data-srcset')), sizes: im.getAttribute('sizes'),
      picture: pic ? {sources: srcs, art: srcs.some(s => s.media), types: [...new Set(srcs.map(s => s.type).filter(Boolean))]} : null,
      alt: im.hasAttribute('alt') ? im.getAttribute('alt').slice(0, 140) : null, role: im.getAttribute('role'), aria_hidden: im.closest('[aria-hidden="true"]') ? true : false,
      fit: cs.objectFit, round: round(im, b), complete: im.complete, lcp: im.__lcpIdx ?? null,
      wh_attr: [im.getAttribute('width'), im.getAttribute('height')], ratio_css: cs.aspectRatio !== 'auto' ? cs.aspectRatio : null}, ctx(im)); });
  // ---------- CSS backgrounds (элементы и псевдоэлементы)
  R.bg = []; R.grad = []; let nEl = 0;
  for (const el of document.querySelectorAll('body *')) { nEl++; if (nEl > 25000) break;
    for (const pseudo of [null, '::before', '::after']) { let cs; try { cs = getComputedStyle(el, pseudo); } catch (e) { continue; }
      if (pseudo && (cs.content === 'none' || cs.content === 'normal') && cs.backgroundImage === 'none' && cs.maskImage === 'none') continue;
      const bi = cs.backgroundImage, mi = cs.maskImage || cs.webkitMaskImage;
      if ((!bi || bi === 'none') && (!mi || mi === 'none')) continue;
      const b = box(el); if (!vis(el, b)) continue;
      for (const u of urlsIn(bi)) R.bg.push(Object.assign({kind: 'css-bg', pseudo, prop: 'background', src: abs(u), box: b, fold: fold(b), vp_pct: +vpArea(b).toFixed(1),
        size: cs.backgroundSize, pos: cs.backgroundPosition, lcp: el.__lcpIdx ?? null, round: round(el, b)}, ctx(el)));
      for (const u of urlsIn(mi)) R.bg.push(Object.assign({kind: 'css-mask', pseudo, prop: 'mask', src: abs(u), box: b, fold: fold(b), vp_pct: +vpArea(b).toFixed(1), lcp: null, round: false}, ctx(el)));
      if (/gradient\(/.test(bi) && b.w * b.h > 0.05 * VW * VH) R.grad.push({pseudo, box: b, fold: fold(b), vp_pct: +vpArea(b).toFixed(1), kinds: [...new Set((bi.match(/(repeating-)?(linear|radial|conic)-gradient/g) || []))]});
    } }
  R.elements = nEl;
  // ---------- <video>
  R.video = [...document.querySelectorAll('video')].map(v => { const b = box(v); let pause = null;
    let anc = v.parentElement; for (let i = 0; i < 5 && anc && !pause; i++, anc = anc.parentElement) {
      for (const btn of anc.querySelectorAll('button,[role=button]')) { const lab = ((btn.getAttribute('aria-label') || '') + ' ' + (btn.getAttribute('title') || '') + ' ' + (btn.innerText || '')).trim();
        if (/pause|play|stop|пауз|воспр|останов|stopp|arrêt/i.test(lab)) { pause = lab.slice(0, 60); break; } } }
    return Object.assign({kind: 'video', src: abs(v.currentSrc || v.src || ''), sources: [...v.querySelectorAll('source')].map(s => ({src: abs(s.getAttribute('src') || s.getAttribute('data-src') || ''), type: s.type || null, media: s.media || null})),
      poster: v.getAttribute('poster') ? abs(v.getAttribute('poster')) : null, autoplay: v.autoplay, muted: v.muted, loop: v.loop, playsinline: v.playsInline,
      preload: v.getAttribute('preload'), loading: v.getAttribute('loading'), controls: v.controls, paused: v.paused, t: +v.currentTime.toFixed(2), dur: isFinite(v.duration) ? +v.duration.toFixed(2) : null,
      ready: v.readyState, net: v.networkState, err: v.error ? v.error.code : null, vwh: [v.videoWidth, v.videoHeight], box: b, vis: vis(v, b), fold: fold(b), vp_pct: +vpArea(b).toFixed(1),
      played: !!v.__played, pause_btn: pause, aria_hidden: v.closest('[aria-hidden="true"]') ? true : false, lcp: v.__lcpIdx ?? null, round: false}, ctx(v)); });
  // ---------- SVG
  const svgs = [...document.querySelectorAll('svg')].filter(s => !s.parentElement || !s.parentElement.closest('svg'));
  R.svg = svgs.map(s => { const b = box(s); const html = s.outerHTML.length; const lot = !!s.querySelector('[id^="__lottie_element"]');
    const useRef = s.querySelector('use') ? (s.querySelector('use').getAttribute('href') || s.querySelector('use').getAttribute('xlink:href') || '').slice(0, 120) : null;
    const cls = b.w <= 48 && b.h <= 48 ? 'icon' : (b.w >= 200 || b.h >= 200) ? 'illustration' : 'mid';
    const lbl = ((s.getAttribute('aria-label') || '') + ' ' + (s.querySelector('title') ? s.querySelector('title').textContent : '') + ' ' + (typeof s.className === 'object' ? s.className.baseVal : '')).toLowerCase();
    return Object.assign({kind: 'svg-inline', box: b, vis: vis(s, b), fold: fold(b), vp_pct: +vpArea(b).toFixed(1), bytes: html, paths: s.querySelectorAll('path,circle,rect,polygon,line,polyline,ellipse').length,
      raster: s.querySelectorAll('image').length, smil: s.querySelectorAll('animate,animateTransform,animateMotion,set').length, lottie: lot, use: useRef,
      logo: /logo|brand|wordmark/.test(lbl) || !!s.closest('a[href="/"],a[href="' + location.origin + '/"]'), cls, lcp: s.__lcpIdx ?? null, round: false}, ctx(s)); });
  R.svg_image_href = [...document.querySelectorAll('svg image')].slice(0, 40).map(i => abs(i.getAttribute('href') || i.getAttribute('xlink:href') || ''));
  R.embeds = [...document.querySelectorAll('object[data],embed[src]')].slice(0, 20).map(o => ({src: abs(o.getAttribute('data') || o.getAttribute('src')), type: o.type || null, box: box(o)}));
  // ---------- canvas, lottie/rive-элементы, iframe
  R.canvas = [...document.querySelectorAll('canvas')].slice(0, 30).map(c => { const b = box(c); return Object.assign({kind: 'canvas', ctx: c.__ctxType || null, w: c.width, h: c.height, box: b, vis: vis(c, b), fold: fold(b), vp_pct: +vpArea(b).toFixed(1), lcp: null, round: false}, ctx(c)); });
  R.lottie_el = [...document.querySelectorAll('lottie-player,dotlottie-player,dotlottie-wc,dotlottie-web,[data-lottie],[data-animation-path],[data-lottie-src]')].slice(0, 30).map(e => { const b = box(e);
    return {tag: e.tagName.toLowerCase(), src: abs(e.getAttribute('src') || e.getAttribute('data-animation-path') || e.getAttribute('data-lottie-src') || ''), box: b, fold: fold(b)}; });
  R.rive_el = document.querySelectorAll('rive-canvas,[data-rive],[data-rive-src]').length;
  R.iframe = [...document.querySelectorAll('iframe')].slice(0, 20).map(f => { const b = box(f); return {src: (f.src || f.getAttribute('data-src') || '').slice(0, 200), box: b, fold: fold(b), vis: vis(f, b)}; });
  // ---------- meta, иконки, preload
  const meta = n => { const m = document.querySelector('meta[property="' + n + '"],meta[name="' + n + '"]'); return m ? m.getAttribute('content') : null; };
  R.meta = {og_image: meta('og:image') ? abs(meta('og:image')) : null, og_w: meta('og:image:width'), og_h: meta('og:image:height'), og_type: meta('og:type'),
    tw_card: meta('twitter:card'), tw_image: meta('twitter:image') ? abs(meta('twitter:image')) : null, theme_color: meta('theme-color'), color_scheme: meta('color-scheme'),
    icons: [...document.querySelectorAll('link[rel~="icon"],link[rel="apple-touch-icon"],link[rel="apple-touch-icon-precomposed"],link[rel="mask-icon"],link[rel="manifest"]')].slice(0, 20)
      .map(l => ({rel: l.getAttribute('rel'), href: abs(l.getAttribute('href')), sizes: l.getAttribute('sizes'), type: l.getAttribute('type'), media: l.getAttribute('media')}))};
  R.preload = [...document.querySelectorAll('link[rel="preload"],link[rel="prefetch"],link[rel="modulepreload"]')].filter(l => ['image', 'video', 'fetch'].includes(l.getAttribute('as')))
    .slice(0, 30).map(l => ({rel: l.getAttribute('rel'), as: l.getAttribute('as'), href: abs(l.getAttribute('href') || ''), imagesrcset: !!l.getAttribute('imagesrcset'), fetchpriority: l.getAttribute('fetchpriority'), media: l.getAttribute('media'), type: l.getAttribute('type')}));
  const P = window.__inv || {};
  R.lcp = (P.lcp || []).slice(-6); R.cls = +(P.cls || 0).toFixed(3); R.tbt_ms = Math.round(P.lt || 0); R.ctx_created = P.ctx || []; R.playing_events = P.playing || 0;
  // GSAP — по рантайму: бандл глобал window.gsap не ставит; признаки — gsapVersions, _gsap у элементов, .pin-spacer
  const gv = Array.isArray(window.gsapVersions) ? window.gsapVersions.slice(0, 4).map(String) : [];
  let gt = 0; try { for (const el of document.querySelectorAll('body *')) { if (el._gsap) gt++; if (gt >= 500) break; } } catch (e) {}
  const pins = document.querySelectorAll('.pin-spacer').length;
  R.libs = {lottie: !!(window.lottie || window.bodymovin), dotlottie: !!(window.DotLottie || customElements.get('dotlottie-player') || customElements.get('dotlottie-wc')),
    three: window.__THREE__ || null, gsap: !!(window.gsap || gv.length || gt || pins), gsap_versions: gv, gsap_targets: gt, pin_spacers: pins,
    scrolltrigger: !!(window.ScrollTrigger || pins), webflow: !!window.Webflow, framer: !!document.querySelector('[data-framer-hydrate-v2],#__framer-badge-container,[data-framer-name]'),
    next: !!(window.__NEXT_DATA__ || self.__next_f), nuxt: !!(window.__NUXT__), rive: !!(window.rive || customElements.get('rive-canvas')), shopify: !!window.Shopify};
  return R; })()"""

MAGIC_IMG = ("jpeg", "png", "gif", "webp", "avif", "heic", "heif", "jxl", "ico", "svg", "bmp", "apng", "webp-anim", "gif-anim", "avif-seq")


def sniff(head, url="", ctype=""):
    """Формат по первым байтам (не по расширению). Возвращает строку или None."""
    if not head:
        return None
    h = head
    if h.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "apng" if b"acTL" in h[:200] else "png"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        if h[12:16] == b"VP8X" and len(h) > 20 and (h[20] & 0x02):
            return "webp-anim"
        return "webp"
    if h[4:8] == b"ftyp":
        brand = h[8:12]
        compat = h[16:64]
        if brand == b"avif":
            return "avif"
        if brand == b"avis":
            return "avif-seq"
        if brand in (b"mif1", b"msf1"):
            return "avif" if b"avif" in compat else "heif"
        if brand in (b"heic", b"heix", b"heim", b"heis", b"hevc", b"hevx"):
            return "heic"
        if brand == b"qt  ":
            return "mov"
        if brand in (b"isom", b"iso2", b"iso4", b"iso5", b"iso6", b"mp41", b"mp42", b"avc1", b"dash", b"M4V ", b"MSNV", b"3gp4", b"3gp5", b"cmfc", b"hvc1"):
            return "mp4"
        return "isobmff:" + brand.decode("latin1", "replace").strip()
    if h[:4] == b"\x1a\x45\xdf\xa3":
        return "webm"
    if h[:2] == b"\xff\x0a" or h[:12] == b"\x00\x00\x00\x0cJXL \r\n\x87\n":
        return "jxl"
    if h[:4] == b"\x00\x00\x01\x00":
        return "ico"
    if h[:2] == b"BM":
        return "bmp"
    if h[:4] == b"RIVE":
        return "riv"
    if h[:4] == b"PK\x03\x04":
        return "dotlottie" if url.split("?")[0].lower().endswith(".lottie") else "zip"
    if h[:4] in (b"wOF2", b"wOFF"):
        return "woff2" if h[:4] == b"wOF2" else "woff"
    if h[:4] == b"\x00asm":
        return "wasm"
    if h[:7] == b"#EXTM3U":
        return "m3u8"
    low = h[:400].lstrip().lower()
    if low.startswith(b"<svg") or (low.startswith(b"<?xml") and b"<svg" in low) or (b"<svg" in low[:300] and b"<html" not in low[:300]):
        return "svg"
    if low[:1] in (b"{", b"["):
        return "json"
    if low.startswith(b"<!doctype") or low.startswith(b"<html"):
        return "html"
    return None


def is_lottie(body):
    try:
        if len(body) > 12_000_000:
            return False
        j = json.loads(body)
        return isinstance(j, dict) and "layers" in j and ("fr" in j or "ip" in j) and ("v" in j or "op" in j)
    except Exception:
        return False


def img_dims(body, fmt):
    if fmt == "svg":
        try:
            t = body[:4000].decode("utf-8", "ignore")
            m = re.search(r"<svg[^>]*>", t, re.S | re.I)
            if not m:
                return None
            tag = m.group(0)
            w = re.search(r'\swidth="([\d.]+)', tag); hh = re.search(r'\sheight="([\d.]+)', tag)
            vb = re.search(r'viewBox="([^"]+)"', tag)
            if w and hh:
                return [round(float(w.group(1))), round(float(hh.group(1)))]
            if vb:
                p = [float(x) for x in re.split(r"[\s,]+", vb.group(1).strip())[:4]]
                return [round(p[2]), round(p[3])]
        except Exception:
            return None
        return None
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(body))
        return [im.size[0], im.size[1]] + ([getattr(im, "n_frames", 1)] if getattr(im, "is_animated", False) else [])
    except Exception:
        return None


def category(url, ctype, rtype, fmt):
    u = url.split("?")[0].split("#")[0].lower()
    ct = (ctype or "").lower()
    if fmt in ("svg",):
        return "svg"
    if fmt in MAGIC_IMG:
        return "image"
    if fmt in ("mp4", "mov", "webm", "m3u8") or (fmt or "").startswith("isobmff"):
        return "video"
    if fmt in ("lottie", "dotlottie"):
        return "lottie"
    if fmt == "riv":
        return "rive"
    if fmt in ("woff2", "woff"):
        return "font"
    if fmt == "wasm":
        return "wasm"
    if u.endswith(".svg") or "svg" in ct:
        return "svg"
    if u.endswith((".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif", ".ico", ".jxl", ".heic")) or ct.startswith("image/"):
        return "image"
    if u.endswith((".mp4", ".webm", ".mov", ".m3u8", ".m4s", ".ts")) or ct.startswith("video/") or rtype == "media":
        return "video"
    if u.endswith((".glb", ".gltf", ".drc", ".ktx2", ".splat", ".spz", ".sog", ".splinecode", ".hdr", ".exr")):
        return "model3d"
    if u.endswith(".riv"):
        return "rive"
    if u.endswith(".lottie"):
        return "lottie"
    if u.endswith((".woff2", ".woff", ".ttf", ".otf")) or "font" in ct:
        return "font"
    if u.endswith((".js", ".mjs")) or "javascript" in ct or rtype == "script":
        return "js"
    if u.endswith(".css") or "css" in ct or rtype == "stylesheet":
        return "css"
    if "json" in ct or u.endswith(".json"):
        return "json"
    if "html" in ct or rtype == "document":
        return "html"
    if u.endswith(".wasm") or "wasm" in ct:
        return "wasm"
    if ct.startswith("audio/") or u.endswith((".mp3", ".ogg", ".wav", ".m4a", ".aac", ".opus")):
        return "audio"
    return "other"


def opt(a, name, default=None):
    return a[a.index(name) + 1] if name in a else default


def frame_diff(a_png, b_png, thr=8):
    try:
        from PIL import Image, ImageChops
        a = Image.open(io.BytesIO(a_png)).convert("RGB"); b = Image.open(io.BytesIO(b_png)).convert("RGB")
        if a.size != b.size:
            return None
        d = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > thr else 0)
        return round(100.0 * d.histogram()[255] / (a.size[0] * a.size[1]), 2)
    except Exception:
        return None


def contact_sheet(pngs, out, cell_w=480, quality=70):
    from PIL import Image
    ims = [Image.open(io.BytesIO(p)).convert("RGB") for p in pngs]
    ims = [im.resize((cell_w, max(1, int(im.height * cell_w / im.width)))) for im in ims]
    h = max(i.height for i in ims)
    s = Image.new("RGB", (cell_w * len(ims) + 8 * (len(ims) - 1), h), (255, 255, 255))
    x = 0
    for im in ims:
        s.paste(im, (x, 0)); x += cell_w + 8
    s.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
    return out


def norm_url(u):
    return (u or "").split("#")[0]


def mobile_device(pw):
    """Дескриптор Playwright «Pixel 7»: размер, DPR, касание; в UA — HeadlessChrome, как у самого браузера."""
    dev = dict(pw.devices["Pixel 7"])
    dev["user_agent"] = dev["user_agent"].replace("Chrome/", "HeadlessChrome/")
    return dev


SELFTEST_HTML = """<!doctype html><html lang="ru"><head><meta charset="utf-8"><title>asset_inventory selftest</title>
<style>body{margin:0;font:16px sans-serif} .hero{height:480px;background:linear-gradient(90deg,#123,#456)}</style></head>
<body><header><svg width="32" height="32" aria-label="logo"><rect width="32" height="32"/></svg></header>
<section class="hero"><h1>Проверка инвентаря</h1><div class="pin-spacer"><div id="pinned">закреплённый блок</div></div></section>
<script>window.gsapVersions = ["3.12.5"]; document.getElementById("pinned")._gsap = {id: 1};</script>
</body></html>"""


def selftest():
    """Локальная страница file:// в Chromium Playwright, без сети: UA как есть, navigator.webdriver, признаки GSAP по
    рантайму (gsapVersions, _gsap, .pin-spacer), телефонный дескриптор с HeadlessChrome; в коде нет маскировки."""
    import subprocess
    import tempfile
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "lib"))
    import kbpaths
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)
    src = open(os.path.abspath(__file__), encoding="utf-8").read().split("\ndef selftest")[0]
    check("в коде нет --disable-blink-features и подмены UA на строку без Headless",
          "--disable-blink-" not in src and "user_agent=" not in src and "AppleWebKit" not in src)
    with tempfile.TemporaryDirectory() as td:
        page = os.path.join(td, "page.html")
        with open(page, "w", encoding="utf-8") as f:
            f.write(SELFTEST_HTML)
        url = "file://" + page
        env = kbpaths.playwright_env()
        with kbpaths.lock("browser"):
            for mode, extra in (("desktop", []), ("mobile", ["--mobile"])):
                out = os.path.join(td, mode)
                r = subprocess.run([sys.executable, os.path.abspath(__file__), url, out, "--quick", "--wait", "300", "--no-og"]
                                   + extra, capture_output=True, text=True, timeout=180, env=env)
                name = "inv_mobile_quick.json" if extra else "inv_quick.json"
                inv = json.load(open(os.path.join(out, name), encoding="utf-8")) if os.path.exists(os.path.join(out, name)) else {}
                check(f"{mode}: прогон на file:// — код 0 и инвентарь ({r.returncode})", r.returncode == 0 and inv)
                ua = inv.get("ua") or ""
                tok = next((t for t in ua.split() if t.startswith("HeadlessChrome/")), "нет HeadlessChrome")
                check(f"{mode}: UA как есть — {tok}", "HeadlessChrome/" in ua)
                check(f"{mode}: navigator.webdriver = true — автоматизация видна сайту", inv.get("webdriver") is True)
                libs = (inv.get("dom") or {}).get("libs") or {}
                if mode == "desktop":
                    check("GSAP по рантайму: gsapVersions, _gsap, .pin-spacer без window.gsap",
                          libs.get("gsap") is True and libs.get("gsap_versions") == ["3.12.5"] and libs.get("gsap_targets", 0) >= 1
                          and libs.get("pin_spacers") == 1 and libs.get("scrolltrigger") is True)
                else:
                    check("телефон: Pixel 7 — Android и ширина 412", "Android" in ua and inv.get("viewport") == [412, 839])
    print("asset_inventory selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main():
    a = sys.argv[1:]
    if a and a[0] == "--selftest":
        sys.exit(selftest())
    if len(a) < 2 or a[0] in ("-h", "--help"):
        print(__doc__); sys.exit(0)
    url, out = a[0], os.path.abspath(a[1])
    os.makedirs(out, exist_ok=True)
    mobile, rm, quick, throttle = "--mobile" in a, "--reduced-motion" in a, "--quick" in a, "--throttle" in a
    wait = int(opt(a, "--wait", 6000)); nav_timeout = int(opt(a, "--timeout", 90)) * 1000
    suffix = ("_mobile" if mobile else "") + ("_thr" if throttle else "") + ("_rm" if rm else "") + ("_quick" if quick else "")
    from playwright.sync_api import sync_playwright
    net, logs, creq = {}, [], {}
    accept_img = {"v": None}
    st = {"url": url, "mode": suffix.strip("_") or "desktop", "date": time.strftime("%Y-%m-%d %H:%M"), "tool": "asset_inventory.py"}
    shots = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=GPU_ARGS)
        st["browser"] = b.version
        if mobile:
            dev = mobile_device(pw)
            ctx = b.new_context(**dev, reduced_motion="reduce" if rm else "no-preference", locale="en-US")
        else:
            ctx = b.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=float(opt(a, "--dpr", 1)),
                                reduced_motion="reduce" if rm else "no-preference", locale="en-US")
        ctx.add_init_script(INIT)
        p = ctx.new_page()
        W, H = p.viewport_size["width"], p.viewport_size["height"]
        st["viewport"] = [W, H]
        phase = {"v": "load"}

        def on_request(req):
            try:
                if accept_img["v"] is None and req.resource_type == "image":
                    accept_img["v"] = (req.all_headers() or {}).get("accept")
            except Exception:
                pass

        def on_finished(req):
            try:
                resp = req.response()
                if resp is None:
                    return
                enc = (req.sizes() or {}).get("responseBodySize", 0) or 0
                hdr = resp.headers
                ct = hdr.get("content-type", "")
                rtype = req.resource_type
                u = norm_url(req.url)
                head, fmt, dims, blen = None, None, None, None
                want = rtype in ("image", "media", "fetch", "xhr", "other") or re.search(r"\.(svg|json|lottie|riv|mp4|webm|mov|avif|webp|jpe?g|png|gif)(\?|$)", u.lower())
                if want and resp.status < 400 and enc < 40_000_000 and not u.startswith("data:"):
                    try:
                        body = resp.body(); blen = len(body); head = body[:512]
                        fmt = sniff(head, u, ct)
                        if fmt == "json" and ("json" in ct or u.lower().split("?")[0].endswith(".json")) and is_lottie(body):
                            fmt = "lottie"
                        if fmt in MAGIC_IMG and blen < 25_000_000:
                            dims = img_dims(body, fmt)
                    except Exception:
                        pass
                cat = category(u, ct, rtype, fmt)
                e = net.get(u)
                if e is None:
                    net[u] = e = {"url": u[:400], "status": resp.status, "ctype": ct[:60], "rtype": rtype, "cat": cat, "fmt": fmt, "enc": 0, "n": 0,
                                  "body": blen, "dims": dims, "encoding": hdr.get("content-encoding"), "cache": hdr.get("cache-control", "")[:80],
                                  "phase": phase["v"], "server": (hdr.get("server") or "")[:30], "cdn": (hdr.get("x-cache") or hdr.get("cf-cache-status") or hdr.get("x-vercel-cache") or "")[:30]}
                e["enc"] += enc; e["n"] += 1
                if e["fmt"] is None and fmt:
                    e["fmt"] = fmt; e["cat"] = cat
                if e["dims"] is None and dims:
                    e["dims"] = dims
            except Exception as ex:
                logs.append(f"net: {str(ex)[:160]}")
        p.on("request", on_request)
        p.on("requestfinished", on_finished)
        p.on("pageerror", lambda e: logs.append(f"pageerror: {str(e)[:200]}"))
        # CDP Network: байты «на проводе» для всех запросов главной цели, включая прерванные медиазапросы
        # (видео: браузер обрывает Range-запрос, когда буфер полон, — requestfinished тогда не приходит)
        cdp = ctx.new_cdp_session(p)
        cdp.send("Network.enable")

        def c_will(e):
            try:
                rid = e["requestId"]; r = creq.get(rid)
                if r is None:
                    creq[rid] = {"url": norm_url(e["request"]["url"]), "type": (e.get("type") or "").lower(), "data": 0, "final": None,
                                 "failed": None, "status": None, "mime": None, "sw": False, "phase": phase["v"]}
                else:
                    r["url"] = norm_url(e["request"]["url"])
            except Exception:
                pass

        def c_resp(e):
            r = creq.get(e.get("requestId"))
            if r is not None:
                rs = e.get("response") or {}
                r["status"] = rs.get("status"); r["mime"] = rs.get("mimeType"); r["sw"] = bool(rs.get("fromServiceWorker"))

        def c_data(e):
            r = creq.get(e.get("requestId"))
            if r is not None:
                r["data"] += e.get("encodedDataLength", 0) or 0

        def c_fin(e):
            r = creq.get(e.get("requestId"))
            if r is not None:
                r["final"] = e.get("encodedDataLength")

        def c_fail(e):
            r = creq.get(e.get("requestId"))
            if r is not None:
                r["failed"] = (e.get("errorText") or "")[:60] + (" canceled" if e.get("canceled") else "")
        cdp.on("Network.requestWillBeSent", c_will)
        cdp.on("Network.responseReceived", c_resp)
        cdp.on("Network.dataReceived", c_data)
        cdp.on("Network.loadingFinished", c_fin)
        cdp.on("Network.loadingFailed", c_fail)
        if throttle:
            cdp.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6 * 1024 * 1024 / 8, "uploadThroughput": 750 * 1024 / 8})
            cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
        t0 = time.time()
        try:
            resp = p.goto(url, wait_until=opt(a, "--wait-until", "load"), timeout=nav_timeout)
            st["status"] = resp.status if resp else None
        except Exception as ex:
            logs.append(f"goto: {str(ex)[:200]}")
            if p.url in ("about:blank", ""):
                try:
                    resp = p.goto(url, wait_until="commit", timeout=60000)
                    st["status"] = resp.status if resp else None; st["goto_retry"] = "commit"
                    p.wait_for_timeout(8000)
                except Exception as ex2:
                    logs.append(f"goto2: {str(ex2)[:200]}")
        st["load_event_sec"] = round(time.time() - t0, 2)
        p.wait_for_timeout(wait)
        st["final_url"] = p.url
        try:     # как страница видит клиента: UA и navigator.webdriver — без подмены
            st["ua"], st["webdriver"] = p.evaluate("() => [navigator.userAgent, navigator.webdriver]")
        except Exception:
            st["ua"] = st["webdriver"] = None
        try:
            st["nav"] = p.evaluate("""(() => { const n = performance.getEntriesByType('navigation')[0]; if (!n) return null;
              return {ttfb: Math.round(n.responseStart), dcl: Math.round(n.domContentLoadedEventEnd), load: Math.round(n.loadEventEnd), html_kb: Math.round(n.transferSize / 1024)}; })()""")
        except Exception:
            st["nav"] = None
        # первый экран: два кадра через 1 с — движение в покое
        try:
            s0 = p.screenshot(type="png"); p.wait_for_timeout(1000); s1 = p.screenshot(type="png")
            st["idle_motion_pct"] = frame_diff(s0, s1); shots.append(s0)
        except Exception as ex:
            logs.append(f"shot: {str(ex)[:120]}")
        st["bytes_before_scroll_kb"] = round(sum((r["final"] if r["final"] is not None else r["data"]) for r in list(creq.values())) / 1024, 1)
        st["bytes_before_scroll_kb_pw"] = round(sum(e["enc"] for e in net.values()) / 1024, 1)
        try:
            st["pre_scroll"] = p.evaluate("(() => { const P = window.__inv || {}; return {lcp: (P.lcp || []).slice(), n: (P.lcp || []).length, cls: +(P.cls || 0).toFixed(3), tbt_ms: Math.round(P.lt || 0), playing: P.playing || 0}; })()")
        except Exception:
            st["pre_scroll"] = None
        phase["v"] = "scroll"
        if not quick:
            try:
                total = p.evaluate("Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0) - innerHeight")
            except Exception:
                total = 0
            st["doc_scrollable_px"] = total
            steps = int(opt(a, "--steps", max(8, min(40, int(total / (0.8 * H)) + 1 if total else 8))))
            delta = max(200, int(total / steps)) if total > H * 0.5 else 500
            marks = {round(steps / 3), round(2 * steps / 3), steps}
            try:
                p.mouse.move(W / 2, H / 2)
                for s in range(1, steps + 1):
                    p.mouse.wheel(0, delta); p.wait_for_timeout(250)
                    if s in marks:
                        p.wait_for_timeout(600)
                        try:
                            shots.append(p.screenshot(type="png"))
                        except Exception:
                            pass
                p.wait_for_timeout(1200)
                p.evaluate("window.scrollTo(0, 0)"); p.keyboard.press("Home"); p.wait_for_timeout(1500)
            except Exception as ex:
                logs.append(f"scroll: {str(ex)[:160]}")
        try:
            st["dom"] = p.evaluate(DOM)
        except Exception as ex:
            st["dom"] = {"error": str(ex)[:300]}; logs.append(f"dom: {str(ex)[:200]}")
        # og:image и apple-touch-icon — отдельным запросом (байты, формат, размеры)
        st["og"] = None
        dm = st.get("dom") or {}
        ogu = (dm.get("meta") or {}).get("og_image")
        if ogu and "--no-og" not in a:
            try:
                r = ctx.request.get(ogu, timeout=30000)
                body = r.body()
                fmt = sniff(body[:512], ogu, r.headers.get("content-type", ""))
                st["og"] = {"url": ogu[:300], "status": r.status, "bytes": len(body), "fmt": fmt, "dims": img_dims(body, fmt) if fmt in MAGIC_IMG else None}
            except Exception as ex:
                st["og"] = {"url": ogu[:300], "error": str(ex)[:120]}
        st["accept_image"] = accept_img["v"]
        st["console"] = logs[:40]
        b.close()
    # ---------- слияние сети: байты из CDP (включая прерванные медиазапросы), формат из тела (Playwright)
    cdp_by = {}
    for r in creq.values():
        if not r["url"] or r["url"].startswith("data:"):
            continue
        b = r["final"] if r["final"] is not None else r["data"]
        c = cdp_by.setdefault(r["url"], {"bytes": 0, "n": 0, "type": r["type"], "mime": r["mime"], "status": r["status"], "failed": 0, "sw": r["sw"], "phase": r["phase"]})
        c["bytes"] += b; c["n"] += 1; c["failed"] += 1 if r["failed"] else 0
        if not c["mime"] and r["mime"]:
            c["mime"] = r["mime"]
    for u, c in cdp_by.items():
        e = net.get(u)
        if e is None:
            cat = category(u, c["mime"] or "", "media" if c["type"] == "media" else c["type"], None)
            vf = None
            if cat == "video":
                mm = (c["mime"] or "").lower(); ul = u.split("?")[0].lower()
                vf = ("mp4" if ("mp4" in mm or ul.endswith(".mp4") or ul.endswith(".m4v")) else "webm" if ("webm" in mm or ul.endswith(".webm"))
                      else "mov" if ("quicktime" in mm or ul.endswith(".mov")) else "m3u8" if ("mpegurl" in mm or ul.endswith(".m3u8")) else "m4s/ts" if ul.endswith((".m4s", ".ts")) else None)
            net[u] = {"url": u[:400], "status": c["status"], "ctype": (c["mime"] or "")[:60], "rtype": c["type"], "cat": cat, "fmt": vf, "enc": c["bytes"], "n": c["n"],
                      "body": None, "dims": None, "encoding": None, "cache": "", "phase": c["phase"], "server": "", "cdn": "", "src": "cdp", "aborted": c["failed"]}
        else:
            e["enc_pw"] = e["enc"]; e["enc"] = max(e["enc"], c["bytes"]); e["n_cdp"] = c["n"]; e["aborted"] = c["failed"]; e["src"] = "cdp+pw"
    st["cdp_requests"] = len(creq)
    items = list(net.values())
    by = {}
    for n in items:
        c = by.setdefault(n["cat"], {"n": 0, "kb": 0.0})
        c["n"] += 1; c["kb"] += n["enc"] / 1024
    fmts = {}
    for n in items:
        if n["cat"] in ("image", "svg") and n["fmt"]:
            f = fmts.setdefault(n["fmt"], {"n": 0, "kb": 0.0}); f["n"] += 1; f["kb"] += n["enc"] / 1024
    vfmt = {}
    for n in items:
        if n["cat"] == "video":
            f = vfmt.setdefault(n["fmt"] or n["ctype"] or "?", {"n": 0, "kb": 0.0}); f["n"] += 1; f["kb"] += n["enc"] / 1024
    st["network"] = {"requests": len(items), "transfer_kb": round(sum(n["enc"] for n in items) / 1024, 1),
                     "by_category": {k: {"n": v["n"], "kb": round(v["kb"], 1)} for k, v in sorted(by.items(), key=lambda kv: -kv[1]["kb"])},
                     "image_formats": {k: {"n": v["n"], "kb": round(v["kb"], 1)} for k, v in sorted(fmts.items(), key=lambda kv: -kv[1]["kb"])},
                     "video_formats": {k: {"n": v["n"], "kb": round(v["kb"], 1)} for k, v in vfmt.items()},
                     "heaviest": [{k: n[k] for k in ("cat", "fmt", "enc", "dims", "url", "phase")} for n in sorted(items, key=lambda n: -n["enc"])[:15]]}
    dm = st.get("dom") or {}
    VH = (dm.get("vh") or 900); VW = (dm.get("vw") or 1440)

    def attach(it):
        u = norm_url(it.get("src") or "")
        n = net.get(u)
        if u.startswith("data:"):
            it["bytes"] = len(u); it["fmt"] = (re.match(r"data:image/([\w+.-]+)", u) or [None, "data"])[1]; it["inline"] = True
        elif n:
            it["bytes"] = n["enc"]; it["fmt"] = n["fmt"]; it["file_dims"] = n["dims"]
        else:
            it["bytes"] = None; it["fmt"] = None
        if it.get("src", "").startswith("data:"):
            it["src"] = it["src"][:60] + "…"
        nat = it.get("nat") or it.get("file_dims") or None
        bx = it.get("box") or {}
        if nat and nat[0] and bx.get("w"):
            it["over"] = round(nat[0] / bx["w"], 2)
        return it

    def slot(it):
        bx = it.get("box") or {}
        w, h = bx.get("w", 0), bx.get("h", 0)
        s = (it.get("src") or "") + " " + str(it.get("alt") or "") + " " + str(it.get("sec") or "")
        if it.get("ftr"):
            return "footer"
        if (it.get("hdr") or it.get("nav")) and h <= 120:
            return "nav"
        if it.get("fold") and it.get("vp_pct", 0) >= 15:
            return "hero"
        if re.search(r"logo|client|customer|partner|brand|trusted", s, re.I) and h <= 100:
            return "logo-wall"
        if it.get("round") and w <= 160:
            return "avatar"
        if w <= 64 and h <= 64:
            return "icon"
        if w * h >= 0.05 * VW * VH:
            return "content-large"
        return "content-small"
    vis_items = []
    for key in ("img", "bg", "video", "canvas"):
        for it in dm.get(key, []) or []:
            if key != "canvas":
                attach(it)
            if key == "video":
                pn = net.get(norm_url(it.get("poster") or "")) if it.get("poster") else None
                it["poster_bytes"] = pn["enc"] if pn else None; it["poster_fmt"] = pn["fmt"] if pn else None; it["poster_dims"] = pn["dims"] if pn else None
                vb = 0; vf = []; seen = set()
                for src in [it.get("src")] + [s.get("src") for s in it.get("sources", [])]:
                    k = norm_url(src or "")
                    n = net.get(k)
                    if n and n["cat"] == "video" and k not in seen:
                        seen.add(k); vb += n["enc"]; vf.append(n["fmt"])
                it["video_bytes"] = vb or None; it["video_fmt"] = vf
            if key in ("img", "video", "canvas") and not it.get("vis"):
                it["slot"] = "hidden"
                continue
            it["slot"] = "icon-mask" if it.get("kind") == "css-mask" else slot(it)
            vis_items.append(it)
    for it in dm.get("svg", []) or []:
        it["slot"] = slot(it) if it.get("cls") != "icon" else ("nav" if it.get("hdr") else "icon")
    # hero: самый крупный видимый визуальный элемент первого экрана
    cands = [it for it in vis_items + (dm.get("svg") or []) if it.get("fold") and (it.get("vis", True)) and it.get("vp_pct", 0) >= 8]
    hero = max(cands, key=lambda it: it.get("vp_pct", 0), default=None)
    pre = st.get("pre_scroll") or {}
    lcp = (pre.get("lcp") or [None])[-1] if pre.get("lcp") else ((dm.get("lcp") or [None])[-1] if dm.get("lcp") else None)
    lcp_idx = (len(pre.get("lcp")) - 1) if pre.get("lcp") else None
    lcp_asset = None
    if lcp_idx is not None:
        for it in (dm.get("img") or []) + (dm.get("bg") or []) + (dm.get("video") or []) + (dm.get("svg") or []):
            if it.get("lcp") == lcp_idx:
                lcp_asset = {k: it.get(k) for k in ("kind", "fmt", "bytes", "nat", "box", "vp_pct", "loading", "fetchpriority", "slot")}
                break
    imgs = [i for i in dm.get("img", []) or [] if i.get("vis")]
    n_img = len(imgs) or 1

    def pct(f):
        return round(100.0 * sum(1 for i in imgs if f(i)) / n_img, 1) if imgs else None
    svgs = dm.get("svg") or []
    st["summary"] = {
        "total_kb": st["network"]["transfer_kb"], "before_scroll_kb": st.get("bytes_before_scroll_kb"),
        "img_kb": round(by.get("image", {}).get("kb", 0), 1), "svg_kb": round(by.get("svg", {}).get("kb", 0), 1), "video_kb": round(by.get("video", {}).get("kb", 0), 1),
        "lottie_kb": round(by.get("lottie", {}).get("kb", 0), 1), "rive_kb": round(by.get("rive", {}).get("kb", 0), 1), "model3d_kb": round(by.get("model3d", {}).get("kb", 0), 1),
        "font_kb": round(by.get("font", {}).get("kb", 0), 1), "js_kb": round(by.get("js", {}).get("kb", 0), 1), "css_kb": round(by.get("css", {}).get("kb", 0), 1), "html_kb": round(by.get("html", {}).get("kb", 0), 1),
        "n_img_dom": len(dm.get("img", []) or []), "n_img_visible": len(imgs), "n_css_bg": len([b for b in dm.get("bg", []) or [] if b["kind"] == "css-bg"]), "n_css_mask": len([b for b in dm.get("bg", []) or [] if b["kind"] == "css-mask"]),
        "n_big_gradients": len(dm.get("grad", []) or []), "n_video": len(dm.get("video", []) or []), "n_video_playing": sum(1 for v in dm.get("video", []) or [] if v.get("played")),
        "n_svg_inline": len(svgs), "svg_inline_kb": round(sum(s.get("bytes", 0) for s in svgs) / 1024, 1), "n_svg_icons": sum(1 for s in svgs if s.get("cls") == "icon"),
        "n_svg_illustr": sum(1 for s in svgs if s.get("cls") == "illustration" and s.get("vis")), "n_lottie_svg": sum(1 for s in svgs if s.get("lottie")),
        "n_lottie_el": len(dm.get("lottie_el", []) or []), "n_lottie_json": sum(1 for n in items if n["fmt"] in ("lottie", "dotlottie")),
        "n_canvas_visible": sum(1 for c in dm.get("canvas", []) or [] if c.get("vis")), "ctx": sorted(set(dm.get("ctx_created") or [])),
        "n_iframe_video": sum(1 for f in dm.get("iframe", []) or [] if re.search(r"youtube|vimeo|wistia|loom|mux|vidyard", f.get("src", ""), re.I)),
        "pct_lazy": pct(lambda i: i.get("loading") == "lazy"), "pct_srcset": pct(lambda i: bool(i.get("srcset"))), "pct_picture": pct(lambda i: bool(i.get("picture"))),
        "n_picture_art": sum(1 for i in imgs if i.get("picture") and i["picture"].get("art")), "n_picture_types": sum(1 for i in imgs if i.get("picture") and i["picture"].get("types")),
        "n_fetchpriority_high": sum(1 for i in imgs if i.get("fetchpriority") == "high"), "n_preload_image": sum(1 for pl in dm.get("preload", []) or [] if pl.get("as") == "image"),
        "pct_alt_missing": pct(lambda i: i.get("alt") is None), "pct_alt_empty": pct(lambda i: i.get("alt") == ""), "pct_lazy_above_fold": round(100.0 * sum(1 for i in imgs if i.get("fold") and i.get("loading") == "lazy") / max(1, sum(1 for i in imgs if i.get("fold"))), 1),
        "over_median": (lambda xs: sorted(xs)[len(xs) // 2] if xs else None)([i.get("over") for i in imgs if i.get("over") and (i.get("box") or {}).get("w", 0) >= 100]),
        "img_formats": st["network"]["image_formats"], "video_formats": st["network"]["video_formats"],
        "lcp": lcp, "lcp_asset": lcp_asset, "lcp_final": (dm.get("lcp") or [None])[-1] if dm.get("lcp") else None,
        "cls": (pre.get("cls") if pre else dm.get("cls")), "tbt_ms": (pre.get("tbt_ms") if pre else dm.get("tbt_ms")), "idle_motion_pct": st.get("idle_motion_pct"),
        "hero": ({k: hero.get(k) for k in ("kind", "src", "fmt", "bytes", "nat", "file_dims", "over", "box", "vp_pct", "loading", "fetchpriority", "srcset", "picture", "alt", "lcp",
                                           "autoplay", "muted", "loop", "playsinline", "poster", "poster_bytes", "poster_fmt", "poster_dims", "video_bytes", "video_fmt", "dur", "vwh", "played", "pause_btn", "ctx", "cls", "paths", "size")}
                 if hero else None),
        "lcp_is_hero": bool(hero is not None and lcp_idx is not None and hero.get("lcp") == lcp_idx),
        "og": st.get("og"), "icons": [(i.get("rel"), i.get("type"), i.get("sizes")) for i in (dm.get("meta") or {}).get("icons", [])],
        "title": dm.get("title"), "h1": dm.get("h1"), "libs": {k: v for k, v in (dm.get("libs") or {}).items() if v},
        "slots": {},
    }
    sl = {}
    for it in vis_items + [s for s in svgs if s.get("vis")]:
        s = sl.setdefault(it.get("slot"), {"n": 0, "kb": 0.0})
        s["n"] += 1; s["kb"] += (it.get("bytes") or 0) / 1024 if it.get("kind") != "svg-inline" else it.get("bytes", 0) / 1024
    st["summary"]["slots"] = {k: {"n": v["n"], "kb": round(v["kb"], 1)} for k, v in sl.items()}
    # контактный лист
    if shots:
        try:
            st["sheet"] = contact_sheet(shots, os.path.join(out, f"sheet{suffix}.jpg"))
        except Exception as ex:
            st["sheet"] = f"не собран: {ex}"
        if "--keep-shots" in a:
            for i, s in enumerate(shots):
                open(os.path.join(out, f"shot{suffix}_{i}.png"), "wb").write(s)
    st["net_items"] = sorted(items, key=lambda n: -n["enc"])
    json.dump(st, open(os.path.join(out, f"inv{suffix}.json"), "w"), ensure_ascii=False, indent=1)
    sm = dict(st["summary"])
    sm.pop("img_formats", None)
    print(json.dumps({"url": url, "mode": st["mode"], "status": st.get("status"), "load_s": st.get("load_event_sec"), **sm}, ensure_ascii=False, indent=1)[:6000])


if __name__ == "__main__":
    main()
