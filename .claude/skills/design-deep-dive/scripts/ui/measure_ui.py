#!/usr/bin/env python3
"""Измерить визуальный слой живой веб-страницы через headless-браузер (Playwright/Chromium).

Снимает `getComputedStyle` и геометрию всех видимых элементов документа и считает частоты: размеры шрифта,
интерлиньяж, веса, трекинг, цвета (текст, фон, границы) в hex и OKLCH, радиусы, тени, толщины границ, отступы
(padding / margin / gap) с долей кратных 4 и 8, высоты контролов, размеры целей нажатия, каркас страницы
(сайдбар, шапка, max-width контента, поля), таблицы (высота строки, padding ячейки, кегль), размеры иконок (svg),
z-index, длительности переходов, кольцо фокуса. Результат: JSON + скриншот. Цвета считает `scripts/lib/color.py`.

Высоту шапки утилита сверяет с порогом своей поверхности (примета header-height): страница сайта — порог липкой
шапки site/03-page-structure/03-first-screen-and-mobile.md §4.2 (телефон ≤ 64, десктоп ≤ 80 px; телефон — окно уже
первого брейкпоинта ДС), экран приложения — высота шапки пресета ui/14-recipes/11-presets.md (A 48, B 64, C 56,
D 40 px; ui/CONTRADICTIONS.md §[C3]). Числа — `scripts/ui/data/thresholds.yaml#header_height`, общий порог утилит.

Использование:
    python3 measure_ui.py URL [--viewport 1440x900] [--surface app|page] [--preset A|B|C|D] [--wait 3000]
                              [--click "СЕЛЕКТОР"] [--scheme light|dark|both] [--slug ИМЯ] [--scroll] [--full-page]
                              [--exclude "СЕЛ,СЕЛ"] [--focus N] [--quiet] [--timeout 60000]
    python3 measure_ui.py --batch targets.jsonl        # построчно {"slug":…, "url":…, "viewport":…, "surface":…, …}
    python3 measure_ui.py --summary path/to.json       # напечатать сводку по готовому JSON
    python3 measure_ui.py --selftest                   # порог шапки по поверхности на синтетике, без браузера

Ключи:
    --viewport WxH   размер окна, по умолчанию 1440x900 (окно шириной до 500 — мобильный профиль: тач и DPR 2)
    --surface        поверхность для порога шапки: app — экран приложения (по умолчанию), page — страница сайта
    --preset         пресет ui 14/11 экрана приложения для порога шапки: A (по умолчанию), B, C, D
    --wait N         ожидание после networkidle, мс (по умолчанию 2500)
    --click SEL      кликнуть по селектору после загрузки (закрыть баннер, открыть демо, переключить вкладку);
                     можно повторять: --click A --click B
    --scheme         light (по умолчанию), dark или both (два прогона: контекст создаётся с нужным color_scheme)
    --scroll         прокрутить до низа и вернуться наверх (ленивая подгрузка) перед измерением
    --full-page      скриншот всей страницы вместо видимой области
    --exclude SEL    исключить поддеревья (виджеты третьих сторон, куки-баннеры); к списку по умолчанию
    --focus N        пройти Tab N раз и снять кольцо фокуса (по умолчанию 8; 0 отключает)
    --slug ИМЯ       имя файлов вместо автогенерации из URL

Файлы: `$DDD_HOME/out/ui/measurements/<slug>_<W>x<H>[_dark].json`, `$DDD_HOME/out/ui/screens/<slug>_<W>x<H>[_dark].png`.

Ограничения (важно для выводов): computed styles — это не токены дизайн-системы, а их применение на конкретном
экране; SPA догружают разметку, поэтому часть значений зависит от момента снятия; кросс-доменные iframe не
измеряются; проценты и `em` уже разрешены в px; элементы под `display:none` и нулевые боксы не считаются.

Замок браузера утилита берёт сама на время работы браузера: kbpaths.lock("browser"), реентерабельный по дереву процессов —
утилита, запущенная из утилиты с тем же замком, его не ждёт.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import kbpaths  # noqa: E402
import yaml  # noqa: E402
ROOT = str(kbpaths.kb("ui"))
MEAS_DIR = str(kbpaths.out("ui", "measurements"))
SCREEN_DIR = str(kbpaths.out("ui", "screens"))
os.makedirs(MEAS_DIR, exist_ok=True)
os.makedirs(SCREEN_DIR, exist_ok=True)
THRESHOLDS = kbpaths.data("ui", "thresholds.yaml")
REFERENCE_TOKENS = kbpaths.kb("ui", "14-recipes", "examples", "tokens.css")
HEADER_SOURCE = {"page": "site/03-page-structure/03-first-screen-and-mobile.md §4.2",
                 "app": "ui/CONTRADICTIONS.md §[C3]; ui/14-recipes/11-presets.md"}


def first_breakpoint():
    """Первый брейкпоинт эталонных токенов ui (`--bp-*` в kb/ui/14-recipes/examples/tokens.css)."""
    with open(REFERENCE_TOKENS, encoding="utf-8") as fh:
        return min(float(v) for v in re.findall(r"--bp-[a-z-]+:\s*(\d+(?:\.\d+)?)px", fh.read()))


def header_limit(surface, preset, vw):
    """Порог высоты шапки поверхности: (px, адрес нормы). Страница сайта — телефон или десктоп по окну."""
    with open(THRESHOLDS, encoding="utf-8") as fh:
        hh = yaml.safe_load(fh)["header_height"]
    if surface == "page":
        return hh["page"]["phone" if vw < first_breakpoint() else "desktop"], HEADER_SOURCE["page"]
    return hh["app"][preset], HEADER_SOURCE["app"]

try:
    from color import hex2oklch, wcag, apca, composite
except Exception:  # pragma: no cover
    hex2oklch = wcag = apca = composite = None

UA_DESKTOP = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/140.0.0.0 Safari/537.36")
UA_MOBILE = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
             "Version/17.5 Mobile/15E148 Safari/604.1")

# Поддеревья, которые исключаются всегда: виджеты третьих сторон и куки-баннеры не относятся к продукту.
DEFAULT_EXCLUDE = [
    "#onetrust-consent-sdk", "#onetrust-banner-sdk", "[id*='cookie' i][class*='banner' i]",
    "[class*='cookie-banner' i]", "[class*='CookieBanner' i]", "[id*='cookiebanner' i]",
    "[class*='cookie-consent' i]", "[id*='cookie-consent' i]", "[aria-label*='cookie' i]",
    "#intercom-container", ".intercom-lightweight-app", "#hubspot-messages-iframe-container",
    "#drift-widget-container", "#crisp-chatbox", "#launcher", "#beacon-container",
    "[id*='usercentrics' i]", "[class*='cmp-banner' i]", "#CybotCookiebotDialog",
]

# ---------------------------------------------------------------------------
# JS: сбор сырых данных в странице
# ---------------------------------------------------------------------------

COLLECT_JS = r"""
(opts) => {
  const vw = window.innerWidth, vh = window.innerHeight;
  const round2 = (x) => Math.round(x * 100) / 100;
  const inc = (m, k) => { if (k === null || k === undefined || k === '') return; m[k] = (m[k] || 0) + 1; };
  const add = (m, k, v) => { if (k === null || k === undefined || k === '') return; m[k] = (m[k] || 0) + v; };
  const num = (k) => (k === '' || k === null || isNaN(+k)) ? k : +k;
  const top = (m, n) => {
    const e = Object.entries(m).sort((a, b) => b[1] - a[1]);
    return (n ? e.slice(0, n) : e).map(([k, v]) => [num(k), v]);
  };
  const bykey = (m) => Object.entries(m)
      .sort((a, b) => (isNaN(+a[0]) ? 1e9 : +a[0]) - (isNaN(+b[0]) ? 1e9 : +b[0]))
      .map(([k, v]) => [num(k), v]);

  // ---- нормализация цвета через canvas: работает с rgb/rgba/color(srgb)/oklch/… ----
  const cvs = document.createElement('canvas'); cvs.width = 1; cvs.height = 1;
  const ctx = cvs.getContext('2d', { willReadFrequently: true });
  const cCache = new Map();
  function colorKey(str) {
    if (!str) return null;
    if (cCache.has(str)) return cCache.get(str);
    let out = null;
    try {
      ctx.fillStyle = 'rgba(0, 0, 0, 0)';
      ctx.fillStyle = str;                      // невалидное значение оставит прежний fillStyle (альфа 0)
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillRect(0, 0, 1, 1);
      const d = ctx.getImageData(0, 0, 1, 1).data;
      const a = Math.round((d[3] / 255) * 1000) / 1000;
      out = a === 0 ? null : (d[0] + ',' + d[1] + ',' + d[2] + ',' + a);
    } catch (e) { out = null; }
    cCache.set(str, out);
    return out;
  }
  const normLen = (v) => {
    if (!v) return null;
    const first = String(v).split(' ')[0];
    if (first.indexOf('%') >= 0) return first;
    const f = parseFloat(first);
    if (isNaN(f)) return null;
    // `border-radius: 9999px` и `calc(infinity * 1px)` Chromium сериализует как огромное число — это «pill»
    if (f >= 500) return 'pill';
    return round2(f);
  };
  function hasOwnText(el) {
    for (let i = 0; i < el.childNodes.length; i++) {
      const n = el.childNodes[i];
      if (n.nodeType === 3 && n.nodeValue && n.nodeValue.trim().length > 0) return true;
    }
    return false;
  }
  function vis(el, cs, r) {
    if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const op = parseFloat(cs.opacity);
    if (!isNaN(op) && op < 0.05) return false;
    if (r.width < 1 || r.height < 1) return false;
    return true;
  }
  function desc(el) {
    const id = el.id ? '#' + el.id : '';
    let cl = '';
    if (typeof el.className === 'string' && el.className.trim()) {
      cl = '.' + el.className.trim().split(/\s+/).slice(0, 4).join('.');
    }
    return (el.tagName.toLowerCase() + id + cl).slice(0, 120);
  }

  // ---- исключённые поддеревья ----
  const excluded = new WeakSet();
  const exSel = (opts.exclude || []).join(',');
  if (exSel) {
    try {
      document.querySelectorAll(exSel).forEach(n => {
        excluded.add(n);
        n.querySelectorAll('*').forEach(m => excluded.add(m));
      });
    } catch (e) {}
  }
  const isExcluded = (el) => {
    let n = el;
    while (n) { if (excluded.has(n)) return true; n = n.parentElement; }
    return false;
  };

  const A = {
    fontSizeAll: {}, fontSizeText: {}, fontFamilyAll: {}, fontFamilyText: {}, fontWeight: {},
    fontSizeWeight: {}, lineHeight: {}, lineHeightRatio: {}, letterSpacing: {}, textTransform: {},
    fontFeature: {}, fontVariantNumeric: {},
    textColor: {}, bgColor: {}, bgArea: {}, borderColor: {}, borderWidth: {}, borderStyle: {},
    radius: {}, radiusPerEl: {}, boxShadow: {}, textShadow: {}, backdrop: {},
    padding: {}, paddingX: {}, paddingY: {}, margin: {}, gap: {}, gapRow: {}, gapCol: {},
    zIndex: {}, transitionDur: {}, transitionEase: {}, maxWidth: {}, position: {}, cursorPointer: 0,
    overflowScroll: 0,
  };
  const cards = [];

  const nodes = document.body ? document.body.querySelectorAll('*') : [];
  let visCount = 0, textCount = 0;
  for (let i = 0; i < nodes.length; i++) {
    const el = nodes[i];
    const tag = el.tagName.toLowerCase();
    if (tag === 'script' || tag === 'style' || tag === 'noscript' || tag === 'template' ||
        tag === 'link' || tag === 'meta' || tag === 'br' || tag === 'head') continue;
    if (el.ownerSVGElement) continue;                 // внутренности svg не считаем
    if (isExcluded(el)) continue;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) continue;
    visCount++;

    // типографика
    const fs = round2(parseFloat(cs.fontSize));
    if (!isNaN(fs)) inc(A.fontSizeAll, fs);
    const fam = (cs.fontFamily || '').split(',')[0].trim().replace(/^['"]|['"]$/g, '');
    inc(A.fontFamilyAll, fam);
    if (hasOwnText(el)) {
      textCount++;
      inc(A.fontSizeText, fs);
      inc(A.fontFamilyText, fam);
      inc(A.fontWeight, cs.fontWeight);
      inc(A.fontSizeWeight, fs + '/' + cs.fontWeight);
      if (cs.textTransform && cs.textTransform !== 'none') inc(A.textTransform, cs.textTransform);
      if (cs.fontFeatureSettings && cs.fontFeatureSettings !== 'normal') inc(A.fontFeature, cs.fontFeatureSettings);
      if (cs.fontVariantNumeric && cs.fontVariantNumeric !== 'normal') inc(A.fontVariantNumeric, cs.fontVariantNumeric);
      const lhRaw = cs.lineHeight;
      if (lhRaw === 'normal') { inc(A.lineHeight, 'normal'); }
      else {
        const lh = round2(parseFloat(lhRaw));
        if (!isNaN(lh)) { inc(A.lineHeight, lh); if (fs > 0) inc(A.lineHeightRatio, Math.round(lh / fs * 100) / 100); }
      }
      const ls = cs.letterSpacing;
      inc(A.letterSpacing, (ls === 'normal' || ls === '' ) ? 'normal' : round2(parseFloat(ls)));
      const ck = colorKey(cs.color); if (ck) inc(A.textColor, ck);
    }

    // цвет фона: считаем и по числу элементов, и по площади (площадь показывает фон страницы и карточек)
    const bk = colorKey(cs.backgroundColor);
    if (bk) { inc(A.bgColor, bk); add(A.bgArea, bk, Math.round(r.width * r.height)); }

    // границы
    const sides = ['Top', 'Right', 'Bottom', 'Left'];
    let maxBorder = 0;
    for (let s = 0; s < 4; s++) {
      const side = sides[s];
      const w = parseFloat(cs['border' + side + 'Width']);
      const st = cs['border' + side + 'Style'];
      if (w > 0 && st !== 'none' && st !== 'hidden') {
        inc(A.borderWidth, round2(w)); inc(A.borderStyle, st);
        maxBorder = Math.max(maxBorder, w);
        const bc = colorKey(cs['border' + side + 'Color']); if (bc) inc(A.borderColor, bc);
      }
    }

    // радиусы по углам
    const corners = ['borderTopLeftRadius', 'borderTopRightRadius', 'borderBottomRightRadius', 'borderBottomLeftRadius'];
    for (let c = 0; c < 4; c++) {
      const v = cs[corners[c]];
      if (v && v !== '0px') { const nv = normLen(v); if (nv !== null && nv !== 0) inc(A.radius, nv); }
    }
    // радиус «как у элемента»: один раз на элемент, по верхнему левому углу — для распределения по компонентам
    {
      const nv = normLen(cs.borderTopLeftRadius);
      if (nv !== null && nv !== 0) inc(A.radiusPerEl, nv);
    }

    // тени и стекло
    if (cs.boxShadow && cs.boxShadow !== 'none') inc(A.boxShadow, cs.boxShadow);
    if (cs.textShadow && cs.textShadow !== 'none') inc(A.textShadow, cs.textShadow);
    const bf = cs.backdropFilter || cs.webkitBackdropFilter;
    if (bf && bf !== 'none') inc(A.backdrop, bf);

    // отступы
    for (let s = 0; s < 4; s++) {
      const side = sides[s];
      const p = parseFloat(cs['padding' + side]);
      if (p > 0) { inc(A.padding, round2(p)); inc((s % 2 === 0) ? A.paddingY : A.paddingX, round2(p)); }
      const m = parseFloat(cs['margin' + side]);
      if (m && Math.abs(m) > 0.4) inc(A.margin, round2(m));
    }
    const dsp = cs.display;
    if (dsp.indexOf('flex') >= 0 || dsp.indexOf('grid') >= 0) {
      const rg = cs.rowGap, cg = cs.columnGap;
      if (rg && rg !== 'normal') { const v = round2(parseFloat(rg)); if (v > 0) { inc(A.gap, v); inc(A.gapRow, v); } }
      if (cg && cg !== 'normal') { const v = round2(parseFloat(cg)); if (v > 0) { inc(A.gap, v); inc(A.gapCol, v); } }
    }

    if (cs.zIndex && cs.zIndex !== 'auto') inc(A.zIndex, cs.zIndex);
    if (cs.position && cs.position !== 'static') inc(A.position, cs.position);
    if (cs.transitionDuration && cs.transitionDuration !== '0s') {
      inc(A.transitionDur, cs.transitionDuration.split(',')[0].trim());
      inc(A.transitionEase, (cs.transitionTimingFunction || '').split(',')[0].trim());
    }
    if (cs.maxWidth && cs.maxWidth !== 'none' && r.width >= 200) inc(A.maxWidth, cs.maxWidth);
    if (cs.cursor === 'pointer') A.cursorPointer++;
    if (cs.overflowY === 'auto' || cs.overflowY === 'scroll') A.overflowScroll++;

    // кандидаты в карточки/панели: крупный бокс с тенью или с границей и радиусом
    const brad = parseFloat(cs.borderTopLeftRadius) || 0;
    const hasShadow = cs.boxShadow && cs.boxShadow !== 'none';
    if (cards.length < 400 && r.width >= 120 && r.height >= 56 && (hasShadow || (maxBorder > 0 && brad >= 2))) {
      cards.push({
        sel: desc(el), w: Math.round(r.width), h: Math.round(r.height),
        radius: round2(brad), border: round2(maxBorder), shadow: hasShadow ? cs.boxShadow : null,
        bg: colorKey(cs.backgroundColor),
        pad: [round2(parseFloat(cs.paddingTop)), round2(parseFloat(cs.paddingRight)),
              round2(parseFloat(cs.paddingBottom)), round2(parseFloat(cs.paddingLeft))]
      });
    }
  }

  // ---- интерактивные элементы и цели нажатия ----
  const INTERACTIVE = 'a[href], button, input:not([type=hidden]), select, textarea, summary,' +
    '[role=button], [role=link], [role=tab], [role=menuitem], [role=menuitemcheckbox], [role=menuitemradio],' +
    '[role=option], [role=switch], [role=checkbox], [role=radio], [role=combobox], [tabindex]:not([tabindex="-1"])';
  const targets = [];
  let hiddenTechnical = 0;
  document.querySelectorAll(INTERACTIVE).forEach(el => {
    if (isExcluded(el)) return;
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) return;
    // технические и визуально скрытые элементы (sr-only, 1×1 прокси-инпуты, aria-hidden) целями не считаются
    if (r.width <= 2 || r.height <= 2) { hiddenTechnical++; return; }
    if (el.getAttribute('aria-hidden') === 'true') { hiddenTechnical++; return; }
    if (cs.position === 'absolute' && ((cs.clipPath && cs.clipPath !== 'none') || (cs.clip && cs.clip !== 'auto'))) {
      hiddenTechnical++; return;
    }
    targets.push({
      tag: el.tagName.toLowerCase(), role: el.getAttribute('role') || '', type: el.getAttribute('type') || '',
      w: round2(r.width), h: round2(r.height), display: cs.display,
      fs: round2(parseFloat(cs.fontSize)), fw: cs.fontWeight,
      pad: [round2(parseFloat(cs.paddingTop)), round2(parseFloat(cs.paddingRight)),
            round2(parseFloat(cs.paddingBottom)), round2(parseFloat(cs.paddingLeft))],
      radius: normLen(cs.borderTopLeftRadius), border: round2(parseFloat(cs.borderTopWidth)) || 0,
      bg: colorKey(cs.backgroundColor), fg: colorKey(cs.color), bc: colorKey(cs.borderTopColor),
      shadow: (cs.boxShadow && cs.boxShadow !== 'none') ? cs.boxShadow : null,
      sel: desc(el)
    });
  });

  // ---- контролы по типам ----
  const CTRL_SEL = {
    button: 'button:not([type=hidden]), [role=button]',
    text_input: "input[type=text], input[type=search], input[type=email], input[type=password], input[type=number], input[type=url], input[type=tel], input[type=date], input:not([type]), [role=textbox], [contenteditable=true]",
    select: 'select, [role=combobox], [role=listbox]',
    textarea: 'textarea',
    checkbox: 'input[type=checkbox], [role=checkbox]',
    radio: 'input[type=radio], [role=radio]',
    switch: '[role=switch]',
    tab: '[role=tab]',
    menuitem: '[role=menuitem], [role=option]',
    link: 'a[href]'
  };
  const controls = {};
  for (const k in CTRL_SEL) {
    const heights = {}, widths = {}, fsz = {}, rad = {}, padx = {}, pady = {};
    let n = 0;
    let list;
    try { list = document.querySelectorAll(CTRL_SEL[k]); } catch (e) { continue; }
    list.forEach(el => {
      if (isExcluded(el)) return;
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (!vis(el, cs, r)) return;
      n++;
      inc(heights, Math.round(r.height * 2) / 2);
      inc(widths, Math.round(r.width));
      inc(fsz, round2(parseFloat(cs.fontSize)));
      const nv = normLen(cs.borderTopLeftRadius); if (nv !== null) inc(rad, nv);
      inc(padx, round2(parseFloat(cs.paddingLeft)));
      inc(pady, round2(parseFloat(cs.paddingTop)));
    });
    if (n) controls[k] = { n: n, heights: bykey(heights), widths: top(widths, 12), font_size: bykey(fsz),
                           radius: bykey(rad), padding_x: bykey(padx), padding_y: bykey(pady) };
  }

  // ---- каркас ----
  function cand(sel, filt, n) {
    const out = [];
    let list;
    try { list = document.querySelectorAll(sel); } catch (e) { return out; }
    list.forEach(el => {
      if (isExcluded(el)) return;
      const cs = getComputedStyle(el);
      const r = el.getBoundingClientRect();
      if (!vis(el, cs, r)) return;
      if (!filt(r, cs, el)) return;
      out.push({ sel: desc(el), x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height),
                 bg: colorKey(cs.backgroundColor), position: cs.position,
                 border_right: round2(parseFloat(cs.borderRightWidth)) || 0,
                 border_bottom: round2(parseFloat(cs.borderBottomWidth)) || 0,
                 pad: [round2(parseFloat(cs.paddingTop)), round2(parseFloat(cs.paddingRight)),
                       round2(parseFloat(cs.paddingBottom)), round2(parseFloat(cs.paddingLeft))] });
    });
    out.sort((a, b) => (b.w * b.h) - (a.w * a.h));
    return out.slice(0, n || 6);
  }

  const sidebarSel = "aside, nav, [class*='sidebar' i], [class*='side-nav' i], [class*='sidenav' i], [data-sidebar]," +
                     "[data-slot='sidebar'], [class*='leftnav' i], [class*='left-nav' i], [class*='SideBar']," +
                     "[id*='sidebar' i], [class*='Sider'], [class*='menu' i]";
  const sidebars = cand(sidebarSel, (r, cs, el) => r.x <= 16 && r.width >= 40 && r.width <= 520 && r.height >= vh * 0.45);
  // запасной проход: левая колонка внутри демо-каркаса (когда приложение вложено в страницу-обёртку)
  const leftCols = cand(sidebarSel + ", div", (r, cs, el) =>
      r.x > 16 && r.x < 420 && r.width >= 150 && r.width <= 420 && r.height >= vh * 0.35 &&
      (parseFloat(cs.borderRightWidth) > 0 || colorKey(cs.backgroundColor) !== null), 6);
  const headerSel = "header, [role=banner], [class*='header' i], [class*='topbar' i], [class*='top-bar' i]," +
                    "[class*='navbar' i], [class*='masthead' i], [class*='appbar' i], [id*='header' i], nav";
  const headers = cand(headerSel, (r, cs, el) => r.y <= 16 && r.width >= vw * 0.5 && r.height >= 24 && r.height <= 180);

  const mainEl = document.querySelector('main, [role=main], #main, #content, #main-content, .main-content');
  let mainInfo = null;
  if (mainEl && !isExcluded(mainEl)) {
    const cs = getComputedStyle(mainEl), r = mainEl.getBoundingClientRect();
    mainInfo = { sel: desc(mainEl), x: Math.round(r.x), w: Math.round(r.width),
                 max_width: cs.maxWidth, bg: colorKey(cs.backgroundColor),
                 pad: [round2(parseFloat(cs.paddingTop)), round2(parseFloat(cs.paddingRight)),
                       round2(parseFloat(cs.paddingBottom)), round2(parseFloat(cs.paddingLeft))] };
  }

  // ширины текстовых блоков: элементы с собственным текстом от 60 знаков (оценка measure — длины строки)
  const textBlockW = {};
  let best = null;
  for (let i = 0; i < nodes.length; i++) {
    const el = nodes[i];
    if (isExcluded(el)) continue;
    if (!hasOwnText(el)) continue;
    let own = 0;
    for (let k = 0; k < el.childNodes.length; k++) {
      const n = el.childNodes[k];
      if (n.nodeType === 3 && n.nodeValue) own += n.nodeValue.trim().length;
    }
    if (own < 60) continue;
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) continue;
    inc(textBlockW, Math.round(r.width / 10) * 10);
    if (own >= 200 && r.width <= vw * 0.98 && (!best || r.width > best.w)) {
      best = { sel: desc(el), w: Math.round(r.width), x: Math.round(r.x),
               max_width: cs.maxWidth, chars: own, font_size: round2(parseFloat(cs.fontSize)) };
    }
  }

  // ---- таблицы ----
  const rowH = {}, cellPadX = {}, cellPadY = {}, cellFs = {}, headFs = {}, headFw = {}, headTransform = {}, headH = {};
  let rowN = 0, cellN = 0, headN = 0;
  document.querySelectorAll('tr, [role=row]').forEach(el => {
    if (isExcluded(el)) return;
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) return;
    const isHead = el.closest('thead') || el.querySelector('th, [role=columnheader]');
    if (isHead) { headN++; inc(headH, Math.round(r.height * 2) / 2); }
    else { rowN++; inc(rowH, Math.round(r.height * 2) / 2); }
  });
  document.querySelectorAll('td, [role=gridcell], [role=cell]').forEach(el => {
    if (isExcluded(el)) return;
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) return;
    cellN++;
    inc(cellPadX, round2(parseFloat(cs.paddingLeft)));
    inc(cellPadY, round2(parseFloat(cs.paddingTop)));
    inc(cellFs, round2(parseFloat(cs.fontSize)));
  });
  document.querySelectorAll('th, [role=columnheader]').forEach(el => {
    if (isExcluded(el)) return;
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) return;
    inc(headFs, round2(parseFloat(cs.fontSize)));
    inc(headFw, cs.fontWeight);
    inc(headTransform, cs.textTransform);
  });

  // ---- иконки ----
  const svgSizes = {}, svgStroke = {};
  document.querySelectorAll('svg').forEach(el => {
    if (isExcluded(el)) return;
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (!vis(el, cs, r)) return;
    inc(svgSizes, Math.round(r.width) + 'x' + Math.round(r.height));
    const sw = cs.strokeWidth;
    if (sw && sw !== '0px' && sw !== '1px' || (sw && parseFloat(sw) > 0)) inc(svgStroke, sw);
    const path = el.querySelector('path');
    if (path) { const psw = getComputedStyle(path).strokeWidth; if (psw && parseFloat(psw) > 0) inc(svgStroke, psw); }
  });

  // ---- заголовки и роли ----
  const roles = {};
  const roleSel = { h1: 'h1', h2: 'h2', h3: 'h3', h4: 'h4', label: 'label', th: 'th, [role=columnheader]',
                    p: 'p', li: 'li', code: 'code, pre' };
  for (const k in roleSel) {
    const fsz = {}, fw = {}, lh = {}, col = {};
    let n = 0;
    document.querySelectorAll(roleSel[k]).forEach(el => {
      if (isExcluded(el)) return;
      const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
      if (!vis(el, cs, r)) return;
      n++;
      inc(fsz, round2(parseFloat(cs.fontSize)));
      inc(fw, cs.fontWeight);
      inc(lh, cs.lineHeight === 'normal' ? 'normal' : round2(parseFloat(cs.lineHeight)));
      const c = colorKey(cs.color); if (c) inc(col, c);
    });
    if (n) roles[k] = { n: n, font_size: bykey(fsz), font_weight: top(fw, 5), line_height: bykey(lh), color: top(col, 4) };
  }

  const htmlCs = getComputedStyle(document.documentElement);
  const bodyCs = document.body ? getComputedStyle(document.body) : htmlCs;

  return {
    page: {
      url: location.href, title: document.title, vw: vw, vh: vh,
      scroll_height: document.documentElement.scrollHeight,
      html_font_size: round2(parseFloat(htmlCs.fontSize)),
      body_font_size: round2(parseFloat(bodyCs.fontSize)),
      body_font_family: bodyCs.fontFamily,
      body_line_height: bodyCs.lineHeight,
      body_bg: colorKey(bodyCs.backgroundColor), html_bg: colorKey(htmlCs.backgroundColor),
      body_color: colorKey(bodyCs.color),
      color_scheme: htmlCs.colorScheme,
      html_class: (document.documentElement.className || '').slice(0, 160),
      html_data_theme: document.documentElement.getAttribute('data-theme') || '',
      prefers_dark: window.matchMedia('(prefers-color-scheme: dark)').matches,
      font_smoothing: bodyCs.webkitFontSmoothing || '',
      iframes: document.querySelectorAll('iframe').length
    },
    counts: { visible: visCount, with_text: textCount, interactive: targets.length,
              hidden_technical_targets: hiddenTechnical,
              table_rows: rowN, table_head_rows: headN, table_cells: cellN,
              cursor_pointer: A.cursorPointer, scroll_containers: A.overflowScroll },
    typography: {
      font_family_text: top(A.fontFamilyText, 12), font_family_all: top(A.fontFamilyAll, 12),
      font_size_text: bykey(A.fontSizeText), font_size_all: bykey(A.fontSizeAll),
      font_weight: bykey(A.fontWeight), font_size_weight: top(A.fontSizeWeight, 30),
      line_height: bykey(A.lineHeight), line_height_ratio: bykey(A.lineHeightRatio),
      letter_spacing: bykey(A.letterSpacing), text_transform: top(A.textTransform, 6),
      font_feature_settings: top(A.fontFeature, 6), font_variant_numeric: top(A.fontVariantNumeric, 6)
    },
    color_raw: {
      text: top(A.textColor, 40), bg: top(A.bgColor, 40), bg_by_area: top(A.bgArea, 20),
      border: top(A.borderColor, 40),
      unique: { text: Object.keys(A.textColor).length, bg: Object.keys(A.bgColor).length,
                border: Object.keys(A.borderColor).length }
    },
    shape: {
      radius: bykey(A.radius), radius_per_element: bykey(A.radiusPerEl),
      box_shadow: top(A.boxShadow, 25), text_shadow: top(A.textShadow, 5),
      border_width: bykey(A.borderWidth), border_style: top(A.borderStyle, 6), backdrop_filter: top(A.backdrop, 6)
    },
    spacing: {
      padding: bykey(A.padding), padding_x: bykey(A.paddingX), padding_y: bykey(A.paddingY),
      margin: bykey(A.margin), gap: bykey(A.gap), gap_row: bykey(A.gapRow), gap_col: bykey(A.gapCol)
    },
    controls: controls,
    targets: targets,
    frame: { sidebars: sidebars, left_columns: leftCols, headers: headers, main: mainInfo, text_column: best,
             text_block_widths: bykey(textBlockW),
             max_widths: top(A.maxWidth, 15), positions: top(A.position, 8) },
    tables: { row_height: bykey(rowH), head_height: bykey(headH), cell_padding_x: bykey(cellPadX),
              cell_padding_y: bykey(cellPadY), cell_font_size: bykey(cellFs),
              head_font_size: bykey(headFs), head_font_weight: top(headFw, 5), head_transform: top(headTransform, 5) },
    icons: { svg_sizes: top(svgSizes, 25), svg_stroke: top(svgStroke, 8) },
    z_index: bykey(A.zIndex),
    motion: { transition_duration: top(A.transitionDur, 15), transition_easing: top(A.transitionEase, 10) },
    roles: roles,
    cards: cards
  };
}
"""

FOCUS_JS = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  let d = el.tagName.toLowerCase();
  if (el.id) d += '#' + el.id;
  if (typeof el.className === 'string' && el.className.trim())
    d += '.' + el.className.trim().split(/\s+/).slice(0, 3).join('.');
  return {
    sel: d.slice(0, 100), w: Math.round(r.width), h: Math.round(r.height),
    outline_width: cs.outlineWidth, outline_style: cs.outlineStyle, outline_color: cs.outlineColor,
    outline_offset: cs.outlineOffset, box_shadow: cs.boxShadow === 'none' ? null : cs.boxShadow,
    border_color: cs.borderTopColor, border_width: cs.borderTopWidth
  };
}
"""

# ---------------------------------------------------------------------------
# Постобработка на Python
# ---------------------------------------------------------------------------


def parseable(v):
    try:
        return float(str(v).replace("px", "").strip())
    except Exception:
        return None


def key_to_hex(key):
    """'34,197,94,1' -> ('#22c55e', alpha)."""
    if not key:
        return None, None
    parts = key.split(",")
    try:
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        a = float(parts[3]) if len(parts) > 3 else 1.0
    except Exception:
        return None, None
    return "#%02x%02x%02x" % (r, g, b), a


def enrich_colors(pairs):
    """[[key, count], …] -> [{hex, alpha, count, oklch}]."""
    out = []
    for key, cnt in pairs:
        hx, a = key_to_hex(key)
        if hx is None:
            continue
        item = {"hex": hx, "alpha": a, "count": cnt}
        if hex2oklch:
            L, C, H = hex2oklch(hx)
            item["oklch"] = [round(L * 100, 1), round(C, 4), round(H, 1)]
        out.append(item)
    return out


def mult_stats(pairs):
    """Доли кратности 4 / 8 / 2 по вхождениям и по различным значениям. Одинаковые значения складываются."""
    occ = Counter()
    for v, c in pairs:
        if not isinstance(v, (int, float)):
            continue
        occ[float(v)] += c
    vals = sorted(occ.items())
    total = sum(c for _, c in vals)
    if not total:
        return {}

    def share(pred):
        return round(100.0 * sum(c for v, c in vals if pred(v)) / total, 1)

    def is_int(v):
        return abs(v - round(v)) < 0.02

    def mult(v, n):
        return is_int(v) and round(v) % n == 0

    foreign = sorted(((v, c) for v, c in vals if not mult(v, 4)), key=lambda x: -x[1])[:12]
    return {
        "occurrences": total,
        "distinct": len(set(v for v, _ in vals)),
        "share_mult4_pct": share(lambda v: mult(v, 4)),
        "share_mult8_pct": share(lambda v: mult(v, 8)),
        "share_mult2_pct": share(lambda v: mult(v, 2)),
        "share_fractional_pct": share(lambda v: not is_int(v)),
        "share_foreign_pct": round(100.0 - share(lambda v: mult(v, 4)), 1),
        "top_foreign": [[v, c] for v, c in foreign],
        "top_values": [[v, c] for v, c in sorted(vals, key=lambda x: -x[1])[:15]],
    }


def contrast_pair(fg_hex, bg_hex, alpha=1.0):
    """Контраст переднего плана к фону; при alpha < 1 цвет сначала накладывается на фон."""
    if not (fg_hex and bg_hex and wcag and apca):
        return None
    try:
        eff = fg_hex
        if alpha is not None and alpha < 0.999 and composite:
            eff = composite(fg_hex, alpha, bg_hex)
        return {"fg": fg_hex, "fg_effective": eff, "alpha": alpha, "bg": bg_hex,
                "wcag": round(wcag(eff, bg_hex), 2),
                "apca_Lc": round(apca(eff, bg_hex), 1)}
    except Exception:
        return None


def postprocess(raw, meta):
    d = {"meta": meta, "page": raw["page"], "counts": raw["counts"], "typography": raw["typography"]}

    # ---- цвета ----
    col = raw["color_raw"]
    page_bg_hex, _ = key_to_hex(raw["page"].get("body_bg") or raw["page"].get("html_bg"))
    if not page_bg_hex and col["bg_by_area"]:
        page_bg_hex, _ = key_to_hex(col["bg_by_area"][0][0])
    d["color"] = {
        "page_bg": page_bg_hex,
        "page_bg_oklch": [round(x, 4) for x in hex2oklch(page_bg_hex)] if (page_bg_hex and hex2oklch) else None,
        "text": enrich_colors(col["text"][:20]),
        "bg": enrich_colors(col["bg"][:20]),
        "bg_by_area": enrich_colors(col["bg_by_area"][:12]),
        "border": enrich_colors(col["border"][:20]),
        "unique": col["unique"],
    }
    if d["color"]["page_bg_oklch"]:
        L, C, H = d["color"]["page_bg_oklch"]
        d["color"]["page_bg_oklch"] = [round(L * 100, 1), round(C, 4), round(H, 1)]

    # контрасты основных цветов текста и границ к фону страницы
    contrasts = []
    if page_bg_hex:
        for item in d["color"]["text"][:8]:
            c = contrast_pair(item["hex"], page_bg_hex, item.get("alpha", 1.0))
            if c:
                c["count"] = item["count"]
                c["role"] = "text"
                contrasts.append(c)
        for item in d["color"]["border"][:5]:
            c = contrast_pair(item["hex"], page_bg_hex, item.get("alpha", 1.0))
            if c:
                c["count"] = item["count"]
                c["role"] = "border"
                contrasts.append(c)
    d["color"]["contrast_to_page_bg"] = contrasts

    # хрома нейтралей: цвета с C < 0.04 считаем нейтральными; тонированность = медианная C
    neutrals = [i for i in d["color"]["text"] + d["color"]["bg"] if i.get("oklch") and i["oklch"][1] < 0.04]
    if neutrals:
        chromas = sorted(i["oklch"][1] for i in neutrals)
        d["color"]["neutral_chroma"] = {
            "n": len(chromas), "median": round(chromas[len(chromas) // 2], 4),
            "max": round(chromas[-1], 4),
            "tinted": bool(chromas[len(chromas) // 2] > 0.004),
        }

    # ---- форма ----
    d["shape"] = raw["shape"]
    d["shape"]["radius_stats"] = mult_stats(raw["shape"]["radius"])

    # ---- отступы ----
    sp = raw["spacing"]
    d["spacing"] = {k: sp[k] for k in sp}
    d["spacing"]["stats"] = {
        "padding": mult_stats(sp["padding"]),
        "margin": mult_stats(sp["margin"]),
        "gap": mult_stats(sp["gap"]),
        "padding_gap": mult_stats(sp["padding"] + sp["gap"]),   # основной показатель: осознанные отступы
        "all": mult_stats(sp["padding"] + sp["margin"] + sp["gap"]),
    }

    # ---- контролы и цели ----
    d["controls"] = raw["controls"]
    tg = raw["targets"]
    d["counts"]["targets"] = len(tg)
    non_inline = [t for t in tg if not (t["tag"] == "a" and t["display"].startswith("inline") and t["h"] < 24)]
    small = [t for t in tg if t["w"] < 24 or t["h"] < 24]
    small_block = [t for t in non_inline if t["w"] < 24 or t["h"] < 24]
    small44 = [t for t in non_inline if t["w"] < 44 or t["h"] < 44]
    heights = Counter(round(t["h"] * 2) / 2 for t in tg if t["h"] >= 12)
    d["targets"] = {
        "n": len(tg),
        "n_non_inline": len(non_inline),
        "min_side_px": round(min([min(t["w"], t["h"]) for t in tg]), 1) if tg else None,
        "under_24_pct": round(100.0 * len(small) / len(tg), 1) if tg else None,
        "under_24_pct_excl_inline_links": round(100.0 * len(small_block) / len(non_inline), 1) if non_inline else None,
        "under_44_pct_excl_inline_links": round(100.0 * len(small44) / len(non_inline), 1) if non_inline else None,
        "height_hist": sorted(heights.items()),
        "smallest_examples": sorted(({"sel": t["sel"], "w": t["w"], "h": t["h"]} for t in small_block),
                                    key=lambda x: x["w"] * x["h"])[:10],
    }
    # высоты кнопок и полей: только «настоящие» контролы (не ссылки-иконки в тексте)
    btn = [t for t in tg if t["tag"] == "button" or t["role"] == "button"]
    inp = [t for t in tg if t["tag"] in ("input", "select", "textarea")
           and t["type"] not in ("checkbox", "radio", "hidden")]
    d["targets"]["button_height_hist"] = sorted(Counter(round(t["h"] * 2) / 2 for t in btn if t["h"] >= 16).items())
    d["targets"]["input_height_hist"] = sorted(Counter(round(t["h"] * 2) / 2 for t in inp if t["h"] >= 16).items())
    d["targets"]["button_padding_x_hist"] = sorted(Counter(t["pad"][3] for t in btn).items())
    # текстовая кнопка: ширина заметно больше высоты; иконочная: квадрат
    btn_text = [t for t in btn if t["w"] >= 64 and t["h"] >= 20 and t["w"] > t["h"] * 1.4]
    btn_sq = [t for t in btn if abs(t["w"] - t["h"]) <= 2 and t["h"] >= 14]
    inp_real = [t for t in inp if t["w"] >= 80 and t["h"] >= 18]
    d["targets"]["button_text_height_hist"] = sorted(Counter(round(t["h"] * 2) / 2 for t in btn_text).items())
    d["targets"]["button_square_size_hist"] = sorted(Counter(round(t["h"] * 2) / 2 for t in btn_sq).items())
    d["targets"]["input_real_height_hist"] = sorted(Counter(round(t["h"] * 2) / 2 for t in inp_real).items())
    d["targets"]["button_text_padding_x_hist"] = sorted(Counter(t["pad"][3] for t in btn_text).items())
    d["targets"]["button_radius_hist"] = sorted(Counter(str(t["radius"]) for t in btn_text).items(),
                                                key=lambda x: -x[1])[:6]
    d["targets"]["input_radius_hist"] = sorted(Counter(str(t["radius"]) for t in inp_real).items(),
                                               key=lambda x: -x[1])[:6]

    # ---- каркас ----
    fr = raw["frame"]
    d["frame"] = fr
    sidebar = fr["sidebars"][0] if fr["sidebars"] else None
    header = fr["headers"][0] if fr["headers"] else None
    d["frame"]["picked"] = {
        "sidebar_w": sidebar["w"] if sidebar else None,
        "sidebar_sel": sidebar["sel"] if sidebar else None,
        "header_h": header["h"] if header else None,
        "header_sel": header["sel"] if header else None,
        "main_w": fr["main"]["w"] if fr["main"] else None,
        "main_max_width": fr["main"]["max_width"] if fr["main"] else None,
        "main_padding_x": fr["main"]["pad"][3] if fr["main"] else None,
        "text_column_w": fr["text_column"]["w"] if fr["text_column"] else None,
    }

    d["tables"] = raw["tables"]
    d["icons"] = raw["icons"]
    d["z_index"] = raw["z_index"]
    d["motion"] = raw["motion"]
    d["roles"] = raw["roles"]

    # карточки: сводка по радиусу / тени / padding
    cards = raw["cards"]
    d["cards"] = {
        "n": len(cards),
        "with_shadow": sum(1 for c in cards if c["shadow"]),
        "with_border_only": sum(1 for c in cards if not c["shadow"] and c["border"]),
        "radius_hist": sorted(Counter(c["radius"] for c in cards).items()),
        "padding_hist": sorted(Counter(c["pad"][0] for c in cards).items()),
        "shadow_top": Counter(c["shadow"] for c in cards if c["shadow"]).most_common(8),
        "examples": cards[:25],
    }
    d["derived"] = derive(d)
    return d


def _top1(pairs, exclude=()):
    """Самое частое значение списка [[v, count], …]."""
    best = None
    for v, c in pairs:
        if v in exclude:
            continue
        if best is None or c > best[1]:
            best = (v, c)
    return best


def derive(d):
    """Краткая сводка для таблицы «продукт × параметр»: одно число на каждый параметр."""
    out = {}
    t = d["typography"]
    fs = t["font_size_text"]
    total_fs = sum(c for _, c in fs) or 1
    base = _top1(fs)
    out["font_family"] = (t["font_family_text"][0][0] if t["font_family_text"] else None)
    out["base_font_size"] = base[0] if base else None
    out["base_font_share_pct"] = round(100.0 * base[1] / total_fs, 1) if base else None
    out["font_sizes_distinct"] = len(fs)
    out["font_sizes_top5"] = [[v, round(100.0 * c / total_fs, 1)] for v, c in sorted(fs, key=lambda x: -x[1])[:5]]
    out["font_sizes_min_max"] = [min(v for v, _ in fs), max(v for v, _ in fs)] if fs else None
    fw = t["font_weight"]
    out["font_weights"] = sorted(v for v, _ in fw)
    out["font_weights_distinct"] = len(fw)
    lhr = _top1(t["line_height_ratio"])
    out["line_height_ratio_top"] = lhr[0] if lhr else None
    ls_non_normal = [(v, c) for v, c in t["letter_spacing"] if v != "normal" and isinstance(v, (int, float))]
    out["letter_spacing_used"] = sorted(ls_non_normal, key=lambda x: -x[1])[:4]
    out["html_font_size"] = d["page"]["html_font_size"]

    c = d["color"]
    out["page_bg"] = c["page_bg"]
    out["page_bg_is_white"] = (c["page_bg"] or "").lower() in ("#ffffff", "#fff")
    out["unique_colors"] = c["unique"]
    txt = [x for x in c.get("contrast_to_page_bg", []) if x.get("role") == "text"]
    if txt:
        out["text_primary"] = {"hex": txt[0]["fg"], "wcag": txt[0]["wcag"], "apca": txt[0]["apca_Lc"]}
        if len(txt) > 1:
            out["text_secondary"] = {"hex": txt[1]["fg"], "wcag": txt[1]["wcag"], "apca": txt[1]["apca_Lc"]}
    brd = [x for x in c.get("contrast_to_page_bg", []) if x.get("role") == "border"]
    if brd:
        out["border_primary"] = {"hex": brd[0]["fg"], "wcag": brd[0]["wcag"], "apca": brd[0]["apca_Lc"]}
    out["neutral_chroma"] = c.get("neutral_chroma")

    sh = d["shape"]
    rad = [(v, n) for v, n in sh["radius_per_element"] if isinstance(v, (int, float))]
    top_rad = _top1(rad)
    out["radius_top"] = top_rad[0] if top_rad else 0
    out["radius_distinct"] = len(rad)
    out["radius_values"] = sorted(v for v, _ in rad)[:14]
    out["radius_pill_count"] = next((n for v, n in sh["radius_per_element"] if v == "pill"), 0)
    bw = _top1(sh["border_width"])
    out["border_width_top"] = bw[0] if bw else None
    out["border_widths"] = sorted(v for v, _ in sh["border_width"])[:8]
    out["box_shadow_distinct"] = len(sh["box_shadow"])
    out["backdrop_filter_used"] = len(sh.get("backdrop_filter") or []) > 0

    st = d["spacing"]["stats"]
    out["spacing_mult4_pct"] = st["padding_gap"].get("share_mult4_pct")
    out["spacing_mult8_pct"] = st["padding_gap"].get("share_mult8_pct")
    out["spacing_fractional_pct"] = st["padding_gap"].get("share_fractional_pct")
    out["spacing_distinct"] = st["padding_gap"].get("distinct")
    out["spacing_top_foreign"] = st["padding_gap"].get("top_foreign", [])[:5]
    out["gap_values"] = [v for v, _ in sorted(d["spacing"]["gap"], key=lambda x: -x[1])[:6]]

    tg = d["targets"]
    bh = _top1(tg["button_text_height_hist"]) or _top1(tg["button_height_hist"])
    ih = _top1(tg["input_real_height_hist"]) or _top1(tg["input_height_hist"])
    bs = _top1(tg["button_square_size_hist"])
    out["button_height_top"] = bh[0] if bh else None
    out["button_heights"] = [v for v, _ in sorted(tg["button_text_height_hist"], key=lambda x: -x[1])[:5]]
    out["button_square_top"] = bs[0] if bs else None
    out["button_padding_x_top"] = (_top1(tg["button_text_padding_x_hist"]) or (None,))[0]
    out["button_radius_top"] = tg["button_radius_hist"][0][0] if tg["button_radius_hist"] else None
    out["input_height_top"] = ih[0] if ih else None
    out["input_heights"] = [v for v, _ in sorted(tg["input_real_height_hist"], key=lambda x: -x[1])[:4]]
    out["input_radius_top"] = tg["input_radius_hist"][0][0] if tg["input_radius_hist"] else None
    out["min_target_side"] = tg["min_side_px"]
    out["targets_under_24_pct"] = tg["under_24_pct_excl_inline_links"]
    out["targets_under_44_pct"] = tg["under_44_pct_excl_inline_links"]

    f = d["frame"]["picked"]
    out["sidebar_w"] = f["sidebar_w"]
    out["header_h"] = f["header_h"]
    out["main_max_width"] = f["main_max_width"]
    out["main_w"] = f["main_w"]
    out["main_padding_x"] = f["main_padding_x"]
    out["content_column_w"] = f["text_column_w"]
    mw = [v for v, _ in sorted(d["frame"]["max_widths"], key=lambda x: -x[1])[:5]]
    out["max_width_values"] = mw
    tbw = d["frame"].get("text_block_widths") or []
    if tbw:
        widths = sorted(v for v, c in tbw for _ in range(c))
        out["text_block_width_median"] = widths[len(widths) // 2]
        out["text_block_width_max"] = widths[-1]

    tb = d["tables"]
    rh = _top1(tb["row_height"])
    out["table_row_h"] = rh[0] if rh else None
    cpx = _top1(tb["cell_padding_x"])
    cpy = _top1(tb["cell_padding_y"])
    out["table_cell_pad"] = [cpy[0] if cpy else None, cpx[0] if cpx else None]
    cfs = _top1(tb["cell_font_size"])
    out["table_cell_font"] = cfs[0] if cfs else None
    hfw = _top1(tb["head_font_weight"])
    out["table_head_weight"] = hfw[0] if hfw else None
    out["table_head_transform"] = _top1([p for p in tb["head_transform"] if p[0] != "none"])

    icons = [(v, n) for v, n in d["icons"]["svg_sizes"]
             if isinstance(v, str) and "x" in v and
             all(p.isdigit() and int(p) <= 64 for p in v.split("x"))]
    ic = _top1(icons)
    out["icon_size_top"] = ic[0] if ic else None
    out["icon_sizes"] = [v for v, _ in sorted(icons, key=lambda x: -x[1])[:5]]

    out["z_index_distinct"] = len(d["z_index"])
    out["z_index_max"] = max((v for v, _ in d["z_index"] if isinstance(v, (int, float))), default=None)

    cd = d["cards"]
    out["cards_n"] = cd["n"]
    out["cards_with_shadow_pct"] = round(100.0 * cd["with_shadow"] / cd["n"], 1) if cd["n"] else None
    cr = _top1(cd["radius_hist"])
    out["card_radius_top"] = cr[0] if cr else None
    cp = _top1(cd["padding_hist"], exclude=(0,))
    out["card_padding_top"] = cp[0] if cp else None

    fo = d.get("focus") or []
    if fo:
        first = fo[0]
        out["focus_ring"] = {
            "outline": "%s %s %s offset %s" % (first["outline_width"], first["outline_style"],
                                               first["outline_color"], first["outline_offset"]),
            "via_box_shadow": bool(first.get("box_shadow")) and first["outline_style"] == "none",
            "box_shadow": (first.get("box_shadow") or "")[:200],
        }
    out["transition_top"] = (d["motion"]["transition_duration"][0][0]
                             if d["motion"]["transition_duration"] else None)
    out["visible_elements"] = d["counts"]["visible"]
    out["density_elements_per_1000px2"] = round(
        1000.0 * d["counts"]["visible"] / max(1, d["page"]["vw"] * d["page"]["scroll_height"] / 1000), 2)
    return out


def fmt_hist(pairs, limit=14, unit=""):
    items = [(v, c) for v, c in pairs][:limit]
    return " ".join("%s%s×%d" % (v, unit if isinstance(v, (int, float)) else "", c) for v, c in items)


def print_summary(d, fh=sys.stdout):
    m, p = d["meta"], d["page"]
    w = fh.write
    w("\n=== %s  [%s, %s] ===\n" % (m["slug"], m["viewport"], m["scheme"]))
    w("URL: %s\n" % p["url"])
    w("title: %s\n" % (p["title"] or "")[:90])
    w("элементов видимых %d, с текстом %d, интерактивных %d\n"
      % (d["counts"]["visible"], d["counts"]["with_text"], d["counts"].get("interactive", 0)))
    w("html %s px / body %s px; семейство: %s\n"
      % (p["html_font_size"], p["body_font_size"], (p["body_font_family"] or "")[:70]))
    t = d["typography"]
    w("font-size (текст): %s\n" % fmt_hist(sorted(t["font_size_text"], key=lambda x: -x[1]), 12))
    w("font-weight: %s\n" % fmt_hist(sorted(t["font_weight"], key=lambda x: -x[1]), 8))
    w("line-height: %s\n" % fmt_hist(sorted(t["line_height"], key=lambda x: -x[1]), 8))
    w("letter-spacing: %s\n" % fmt_hist(sorted(t["letter_spacing"], key=lambda x: -x[1]), 6))
    c = d["color"]
    w("фон страницы: %s  уникальных цветов: текст %d, фон %d, границы %d\n"
      % (c["page_bg"], c["unique"]["text"], c["unique"]["bg"], c["unique"]["border"]))
    w("топ текста: %s\n" % " ".join("%s%s×%d" % (i["hex"], "" if i["alpha"] >= 0.999 else "@%.2f" % i["alpha"],
                                                 i["count"]) for i in c["text"][:6]))
    w("контрасты к фону: %s\n" % " ".join("%s %s %.1f/%.0f" % (x["role"][:1], x["fg_effective"], x["wcag"],
                                                               x["apca_Lc"])
                                          for x in c.get("contrast_to_page_bg", [])[:7]))
    sh = d["shape"]
    w("радиусы (на элемент): %s\n" % fmt_hist(sorted(sh["radius_per_element"], key=lambda x: -x[1]), 10, "px"))
    w("границы: %s; теней различных: %d\n" % (fmt_hist(sorted(sh["border_width"], key=lambda x: -x[1]), 6, "px"),
                                              len(sh["box_shadow"])))
    st = d["spacing"]["stats"]["padding_gap"]
    if st:
        w("padding+gap: кратны 4 — %.1f%%, кратны 8 — %.1f%%, дробных %.1f%%, различных %d; чужие: %s\n"
          % (st["share_mult4_pct"], st["share_mult8_pct"], st["share_fractional_pct"], st["distinct"],
             " ".join("%s×%d" % (v, n) for v, n in st["top_foreign"][:6])))
        w("padding+gap топ: %s\n" % " ".join("%s×%d" % (v, n) for v, n in st["top_values"][:10]))
    tgt = d["targets"]
    w("кнопки текстовые: %s; квадратные: %s\n"
      % (fmt_hist(sorted(tgt["button_text_height_hist"], key=lambda x: -x[1]), 6),
         fmt_hist(sorted(tgt["button_square_size_hist"], key=lambda x: -x[1]), 6)))
    w("поля: %s; padding кнопки x: %s\n"
      % (fmt_hist(sorted(tgt["input_real_height_hist"], key=lambda x: -x[1]), 6),
         fmt_hist(sorted(tgt["button_text_padding_x_hist"], key=lambda x: -x[1]), 5)))
    w("целей %d, < 24 px: %s%% (без инлайн-ссылок %s%%), < 44 px: %s%%, минимальная сторона %s px\n"
      % (tgt["n"], tgt["under_24_pct"], tgt["under_24_pct_excl_inline_links"],
         tgt["under_44_pct_excl_inline_links"], tgt["min_side_px"]))
    f = d["frame"]["picked"]
    w("каркас: сайдбар %s (%s), шапка %s (%s), main %s max-width %s pad %s, текстовый блок медиана %s макс %s\n"
      % (f["sidebar_w"], (f["sidebar_sel"] or "")[:40], f["header_h"], (f["header_sel"] or "")[:40],
         f["main_w"], f["main_max_width"], f["main_padding_x"],
         d["derived"].get("text_block_width_median"), d["derived"].get("text_block_width_max")))
    dv = d["derived"]
    if dv.get("header_limit") is not None:
        where = ("страница сайта" if d["meta"].get("surface") == "page"
                 else "экран приложения, пресет %s" % d["meta"].get("preset"))
        verdict = ("шапка не найдена" if dv.get("header_over") is None
                   else "выше порога — примета header-height" if dv["header_over"] else "в пороге")
        w("шапка: %s px, порог %s px (%s; %s) — %s\n"
          % (f["header_h"], dv["header_limit"], where, dv.get("header_norm"), verdict))
    tb = d["tables"]
    if tb["row_height"]:
        w("таблица: строки %s; padding ячейки x %s y %s; кегль %s\n"
          % (fmt_hist(sorted(tb["row_height"], key=lambda x: -x[1]), 5),
             fmt_hist(sorted(tb["cell_padding_x"], key=lambda x: -x[1]), 4),
             fmt_hist(sorted(tb["cell_padding_y"], key=lambda x: -x[1]), 4),
             fmt_hist(sorted(tb["cell_font_size"], key=lambda x: -x[1]), 4)))
    w("иконки svg: %s\n" % fmt_hist(sorted(d["icons"]["svg_sizes"], key=lambda x: -x[1]), 8))
    w("z-index: %s\n" % fmt_hist(sorted(d["z_index"], key=lambda x: -x[1]), 10))
    cd = d["cards"]
    w("карточки: %d (с тенью %d, только граница %d), радиусы %s, padding %s\n"
      % (cd["n"], cd["with_shadow"], cd["with_border_only"],
         fmt_hist(sorted(cd["radius_hist"], key=lambda x: -x[1]), 5),
         fmt_hist(sorted(cd["padding_hist"], key=lambda x: -x[1]), 5)))
    if d.get("focus"):
        for fo in d["focus"][:3]:
            if fo["outline_style"] not in ("none", None):
                w("фокус %s: outline %s %s %s offset %s\n"
                  % (fo["sel"][:36], fo["outline_width"], fo["outline_style"], fo["outline_color"],
                     fo["outline_offset"]))
            elif fo.get("box_shadow"):
                w("фокус %s: кольцо через box-shadow %s\n" % (fo["sel"][:36], fo["box_shadow"][:150]))
    w("\n")


# ---------------------------------------------------------------------------
# Прогон
# ---------------------------------------------------------------------------


def slugify(url):
    s = re.sub(r"^https?://(www\.)?", "", url).strip("/")
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s)[:60].strip("-")
    return s or hashlib.md5(url.encode()).hexdigest()[:8]


def header_verdict(d, surface="app", preset="A"):
    """Высота шапки против порога поверхности → d["derived"]: header_limit, header_over, header_norm."""
    vw = int(str(d["meta"]["viewport"]).lower().split("x")[0])
    limit, norm = header_limit(surface, preset, vw)
    h = d["derived"].get("header_h")
    d["meta"].update(surface=surface, preset=preset if surface == "app" else None)
    d["derived"].update(header_limit=limit, header_norm=norm,
                        header_over=(None if h is None else bool(h > limit)))
    return d


def measure(pw, url, viewport="1440x900", scheme="light", wait=2500, clicks=(), slug=None,
            scroll=False, full_page=False, exclude=(), focus=8, timeout=60000, quiet=False,
            surface="app", preset="A"):
    vw, vh = (int(x) for x in viewport.lower().split("x"))
    slug = slug or slugify(url)
    mobile = vw <= 500
    suffix = "%s_%dx%d%s" % (slug, vw, vh, "_dark" if scheme == "dark" else "")
    json_path = os.path.join(MEAS_DIR, suffix + ".json")
    png_path = os.path.join(SCREEN_DIR, suffix + ".png")

    browser = pw.chromium.launch(headless=True, args=["--disable-dev-shm-usage", "--font-render-hinting=none"])
    ctx_kwargs = dict(viewport={"width": vw, "height": vh},
                      user_agent=UA_MOBILE if mobile else UA_DESKTOP,
                      color_scheme=scheme, locale="en-US", timezone_id="Europe/Moscow",
                      device_scale_factor=2 if mobile else 1,
                      is_mobile=mobile, has_touch=mobile)
    context = browser.new_context(**ctx_kwargs)
    context.set_default_timeout(timeout)
    page = context.new_page()
    meta = {"slug": slug, "url": url, "viewport": "%dx%d" % (vw, vh), "scheme": scheme,
            "wait_ms": wait, "clicks": list(clicks), "scrolled": scroll,
            "measured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "tool": "measure_ui.py", "exclude": list(exclude)}
    err = None
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        page.wait_for_timeout(wait)
        for sel in clicks:
            try:
                page.locator(sel).first.click(timeout=8000)
                page.wait_for_timeout(1200)
            except Exception as e:
                meta.setdefault("click_errors", []).append("%s: %s" % (sel, str(e)[:120]))
        if scroll:
            for _ in range(12):
                page.mouse.wheel(0, vh)
                page.wait_for_timeout(180)
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(700)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(250)
        page.screenshot(path=png_path, full_page=full_page)
        raw = page.evaluate(COLLECT_JS, {"exclude": list(DEFAULT_EXCLUDE) + list(exclude)})
        d = header_verdict(postprocess(raw, meta), surface, preset)
        # кольцо фокуса
        focus_data = []
        if focus:
            try:
                page.evaluate("window.scrollTo(0, 0)")
                for _ in range(focus):
                    page.keyboard.press("Tab")
                    page.wait_for_timeout(120)
                    f = page.evaluate(FOCUS_JS)
                    if not f:
                        continue
                    visible_outline = f.get("outline_style") not in (None, "none") and \
                        (parseable(f.get("outline_width")) or 0) > 0
                    if visible_outline or f.get("box_shadow"):
                        focus_data.append(f)
            except Exception:
                pass
        # оставить различные варианты
        seen, uniq = set(), []
        for f in focus_data:
            k = (f["outline_width"], f["outline_style"], f["outline_color"], f["outline_offset"], f["box_shadow"])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(f)
        d["focus"] = uniq[:6]
        d["focus_probed"] = focus
        d["derived"]["focus_ring"] = d["derived"].get("focus_ring")
        if uniq:
            first = uniq[0]
            d["derived"]["focus_ring"] = {
                "outline": "%s %s %s offset %s" % (first["outline_width"], first["outline_style"],
                                                   first["outline_color"], first["outline_offset"]),
                "via_box_shadow": bool(first.get("box_shadow")) and first["outline_style"] == "none",
                "box_shadow": (first.get("box_shadow") or "")[:220],
            }
        d["meta"]["screenshot"] = os.path.relpath(png_path, ROOT)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        d = {"meta": meta, "error": err}
    finally:
        try:
            context.close(); browser.close()
        except Exception:
            pass

    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=1)
    if not quiet:
        if err:
            print("ОШИБКА %s [%s]: %s" % (slug, viewport, err))
        else:
            print_summary(d)
        print("JSON: %s" % json_path)
        if not err:
            print("PNG:  %s" % png_path)
    return d, json_path


def selftest():
    """Порог шапки по поверхности на синтетике, без браузера."""
    ok = True

    def check(name, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print("%s %s: %r%s" % ("OK  " if good else "FAIL", name, got, "" if good else " (ожидалось %r)" % (want,)))

    check("первый брейкпоинт эталонных токенов", first_breakpoint(), 640.0)
    check("страница сайта: телефон 64, десктоп 80",
          (header_limit("page", "A", 390)[0], header_limit("page", "A", 1440)[0]), (64, 80))
    check("экран приложения: A 48, B 64, C 56, D 40", [header_limit("app", k, 1440)[0] for k in "ABCD"], [48, 64, 56, 40])

    def synth(h, viewport):
        return {"meta": {"viewport": viewport}, "derived": {"header_h": h}}
    d = header_verdict(synth(72, "390x844"), "page")
    check("шапка 72 на телефоне страницы — выше 64", (d["derived"]["header_limit"], d["derived"]["header_over"]), (64, True))
    d = header_verdict(synth(72, "1440x900"), "page")
    check("шапка 72 на десктопе страницы — в пороге 80", d["derived"]["header_over"], False)
    d = header_verdict(synth(56, "1440x900"), "app", "A")
    check("шапка 56 у приложения A — выше 48", d["derived"]["header_over"], True)
    check("шапки нет — вердикта нет", header_verdict(synth(None, "1440x900"))["derived"]["header_over"], None)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("url", nargs="?")
    ap.add_argument("--viewport", default="1440x900")
    ap.add_argument("--surface", default="app", choices=["app", "page"])
    ap.add_argument("--preset", default="A", choices=["A", "B", "C", "D"])
    ap.add_argument("--wait", type=int, default=2500)
    ap.add_argument("--click", action="append", default=[])
    ap.add_argument("--scheme", default="light", choices=["light", "dark", "both"])
    ap.add_argument("--slug")
    ap.add_argument("--scroll", action="store_true")
    ap.add_argument("--full-page", action="store_true")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--focus", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=60000)
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--batch")
    ap.add_argument("--summary")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    a = ap.parse_args()

    if a.help or (not a.url and not a.batch and not a.summary and not a.selftest):
        print(__doc__)
        return
    if a.selftest:
        sys.exit(selftest())

    if a.summary:
        with open(a.summary, encoding="utf-8") as fh:
            d = json.load(fh)
        if "error" in d:
            print("ОШИБКА: %s" % d["error"])
        else:
            print_summary(d)
        return

    from playwright.sync_api import sync_playwright

    jobs = []
    if a.batch:
        with open(a.batch, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                jobs.append(json.loads(line))
    else:
        jobs.append({"url": a.url, "viewport": a.viewport, "scheme": a.scheme, "wait": a.wait,
                     "click": a.click, "slug": a.slug, "scroll": a.scroll,
                     "full_page": a.full_page, "exclude": a.exclude, "focus": a.focus,
                     "surface": a.surface, "preset": a.preset})

    ok, bad = 0, []
    with kbpaths.lock("browser"), sync_playwright() as pw:
        for j in jobs:
            schemes = ["light", "dark"] if j.get("scheme") == "both" else [j.get("scheme", "light")]
            for sc in schemes:
                excl = j.get("exclude") or ""
                excl = [s.strip() for s in excl.split(",") if s.strip()] if isinstance(excl, str) else list(excl)
                try:
                    d, _ = measure(pw, j["url"], viewport=j.get("viewport", "1440x900"), scheme=sc,
                                   wait=int(j.get("wait", 2500)), clicks=j.get("click") or [],
                                   slug=j.get("slug"), scroll=bool(j.get("scroll")),
                                   full_page=bool(j.get("full_page")), exclude=excl,
                                   focus=int(j.get("focus", 8)), timeout=int(j.get("timeout", 60000)),
                                   quiet=a.quiet, surface=j.get("surface", a.surface),
                                   preset=j.get("preset", a.preset))
                    if "error" in d:
                        bad.append((j.get("slug") or j["url"], sc, d["error"]))
                    else:
                        ok += 1
                except Exception as e:
                    bad.append((j.get("slug") or j["url"], sc, "%s: %s" % (type(e).__name__, str(e)[:200])))
                    print("СБОЙ %s [%s]: %s" % (j.get("slug") or j["url"], sc, str(e)[:200]))
    if len(jobs) > 1 or bad:
        print("\n--- итог: успешно %d, сбоев %d ---" % (ok, len(bad)))
        for s, sc, e in bad:
            print("  ! %s [%s] %s" % (s, sc, e))


if __name__ == "__main__":
    main()
