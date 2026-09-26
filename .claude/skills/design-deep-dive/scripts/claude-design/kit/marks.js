/* kit/marks.js — нумерованные метки #N поверх артборда для правок из чата.
   Агент D базы claude-design-research, 2026-09-25, v1. Открытый код; к закрытым текстам Anthropic отношения не имеет.

   Подключают ТОЛЬКО инструменты kit: canvas.html вкалывает файл в same-origin iframe артборда (страница открыта по http),
   shot.py — через Playwright. В файлы проекта ничего не пишется, раскладку метки не меняют (оверлей в shadow DOM на <html>).

   API (window.__kitMarks):
     collect()                 → кандидаты в порядке DOM: {selector, kind, tag, text, th (хэш всего текста), visible, rect{x,y,w,h}}
     number(cands, {base, pin}) → те же объекты + n; pin = {селектор: номер} закрепляет номера (между кадрами и итерациями),
                                 незакреплённые получают следующие свободные номера после max(закреплённых, base)
     draw(numbered)            → рисует бейджи у видимых; возвращает {badges:[{n,x,y,w,h,pos}], overlaps:[…]}
     clear()                   → убрать оверлей
     run({base, pin})          → collect + number + draw; результат — объект для marks.json
   Что нумеруется: области (header, nav, section, footer, aside, form), заголовки, кнопки, ссылки, поля, картинки и карточки
   ([data-mark], article, классы card/tile как блок БЭМ, либо контейнер с фоном/рамкой/тенью и ≥ 2 дочерними элементами).
   Номер не зависит от ширины и темы: кандидаты — все подходящие элементы (и скрытые на этой ширине); бейдж — только у видимых. */
(function () {
  'use strict';
  if (window.__kitMarks) { return; }

  var VERSION = '1';
  var KINDS = [
    ['region', 'header, nav, main > section, section, footer, aside, form'],
    ['heading', 'h1, h2, h3, h4, h5, h6, [role="heading"]'],
    ['button', 'button, summary, [role="button"], input[type="submit"], input[type="button"], input[type="reset"]'],
    ['link', 'a[href]'],
    ['field', 'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]), select, textarea'],
    ['image', 'img, svg[role="img"], picture, video, canvas, [role="img"]'],
    ['card', '[data-mark], article']
  ];
  var SKIP_CLASS = /(^|\s)(sr-only|visually-hidden|screen-reader-text)(\s|$)/;
  var CARD_CLASS = /^(card|tile)(--[\w-]+)?$|[-_](card|tile)(--[\w-]+)?$/i;   // блок БЭМ и модификатор, но не элемент card__x
  var COLOR = '#e5006a';

  function esc(s) { return (window.CSS && CSS.escape) ? CSS.escape(s) : String(s).replace(/[^\w-]/g, '\\$&'); }

  function cssPath(el) {
    if (el.id && document.querySelectorAll('#' + esc(el.id)).length === 1) { return '#' + esc(el.id); }
    var parts = [];
    var cur = el;
    while (cur && cur.nodeType === 1 && cur !== document.documentElement) {
      if (cur !== el && cur.id && document.querySelectorAll('#' + esc(cur.id)).length === 1) {
        parts.unshift('#' + esc(cur.id));
        break;
      }
      var part = cur.tagName.toLowerCase();
      var parent = cur.parentElement;
      if (parent) {
        var same = [];
        for (var i = 0; i < parent.children.length; i++) {
          if (parent.children[i].tagName === cur.tagName) { same.push(parent.children[i]); }
        }
        if (same.length > 1) { part += ':nth-of-type(' + (same.indexOf(cur) + 1) + ')'; }
      }
      parts.unshift(part);
      if (parent === document.body) { parts.unshift('body'); break; }
      cur = parent;
    }
    return parts.join(' > ');
  }

  function hiddenForever(el) {
    for (var e = el; e && e.nodeType === 1; e = e.parentElement) {
      if (e.hasAttribute('hidden') || e.getAttribute('aria-hidden') === 'true') { return true; }
      if (typeof e.className === 'string' && SKIP_CLASS.test(e.className)) { return true; }
      var tag = e.tagName;
      if (tag === 'TEMPLATE' || tag === 'SCRIPT' || tag === 'STYLE' || tag === 'NOSCRIPT') { return true; }
    }
    return false;
  }

  function looksLikeCard(el) {
    if (typeof el.className === 'string') {
      var cls = el.className.trim().split(/\s+/);
      for (var i = 0; i < cls.length; i++) { if (CARD_CLASS.test(cls[i])) { return true; } }
    }
    return false;
  }

  function boxedContainer(el) {
    // Контейнер с собственной «коробкой»: фон, рамка или тень + ≥ 2 дочерних элемента. Признаки берутся из стилей, а не из
    // размеров, чтобы номер не зависел от ширины кадра.
    var tag = el.tagName;
    if (/^(HTML|BODY|MAIN|SECTION|HEADER|FOOTER|NAV|ASIDE|FORM|A|BUTTON|UL|OL|TABLE|TBODY|THEAD|TR|LABEL|FIELDSET|SVG|PICTURE|FIGURE)$/.test(tag)) { return false; }
    if (el.children.length < 2) { return false; }
    var cs = getComputedStyle(el);
    var bg = cs.backgroundColor;
    var hasBg = bg && bg !== 'transparent' && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(bg);
    var hasBorder = ['Top', 'Right', 'Bottom', 'Left'].filter(function (s) {
      return parseFloat(cs['border' + s + 'Width']) > 0 && cs['border' + s + 'Style'] !== 'none';
    }).length >= 3;
    var hasShadow = cs.boxShadow && cs.boxShadow !== 'none';
    if (!(hasBg || hasBorder || hasShadow)) { return false; }
    // не обёртка над областями и не прямой ребёнок body
    if (el.querySelector('section, header, footer, nav, main')) { return false; }
    if (el.parentElement === document.body) { return false; }
    return true;
  }

  function kindOf(el) {
    for (var i = 0; i < KINDS.length; i++) { if (el.matches(KINDS[i][1])) { return KINDS[i][0]; } }
    if (looksLikeCard(el) || boxedContainer(el)) { return 'card'; }
    return null;
  }

  function textOf(el, kind) {
    var t = '';
    if (kind === 'field') {
      var lab = el.id ? document.querySelector('label[for="' + esc(el.id) + '"]') : null;
      if (!lab && el.closest) { lab = el.closest('label'); }
      t = (lab && lab.innerText) || el.getAttribute('aria-label') || el.getAttribute('placeholder') || el.getAttribute('name') || '';
    } else if (kind === 'image') {
      t = el.getAttribute('alt') || el.getAttribute('aria-label') || (el.querySelector && el.querySelector('title') ? el.querySelector('title').textContent : '') || '';
    } else if (kind === 'region' || kind === 'card') {
      var h = el.querySelector('h1, h2, h3, h4, h5, h6, [role="heading"]');
      t = el.getAttribute('aria-label') || (h ? h.innerText || h.textContent : '') || el.innerText || el.textContent || '';
    } else {
      t = el.innerText || el.textContent || el.getAttribute('aria-label') || el.getAttribute('value') || '';
    }
    t = String(t).replace(/\s+/g, ' ').trim();
    return t.length > 70 ? t.slice(0, 69) + '…' : t;
  }

  // FNV-1a 32 по нормализованному полному тексту элемента: сверка «текст внутри поменялся» без пиксельного шума
  function textHash(el) {
    return hashStr(String(el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim());
  }

  // Отпечатки для проверки «изменилось только то, что просили» (kit/diffshots.py): sh — вычисленные стили самого элемента,
  // own — текст и стили его «собственных» (непомеченных) потомков. Ширину и высоту не берём: они меняются от соседей.
  var STYLE_PROPS = ['color', 'backgroundColor', 'backgroundImage', 'fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'lineHeight',
    'letterSpacing', 'textTransform', 'textDecorationLine', 'textAlign', 'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
    'marginTop', 'marginRight', 'marginBottom', 'marginLeft', 'borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth',
    'borderTopStyle', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor', 'borderTopLeftRadius',
    'borderTopRightRadius', 'borderBottomRightRadius', 'borderBottomLeftRadius', 'boxShadow', 'opacity', 'display', 'position',
    'flexDirection', 'flexWrap', 'justifyContent', 'alignItems', 'alignSelf', 'rowGap', 'columnGap', 'minHeight', 'minWidth', 'maxWidth',
    'visibility', 'outlineStyle', 'accentColor', 'transform', 'filter'];
  function styleSig(el) {
    var cs = getComputedStyle(el);
    return STYLE_PROPS.map(function (k) { return cs[k]; }).join('|');
  }
  function hashStr(t) {
    var h = 0x811c9dc5;
    for (var i = 0; i < t.length; i++) { h ^= t.charCodeAt(i); h = (h + ((h << 1) + (h << 4) + (h << 7) + (h << 8) + (h << 24))) >>> 0; }
    return ('00000000' + h.toString(16)).slice(-8);
  }
  function ownSig(el, candSet) {
    var parts = [];
    var walker = document.createTreeWalker(el, NodeFilter.SHOW_ELEMENT | NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        if (n.nodeType === 1 && n !== el && candSet.has(n)) { return NodeFilter.FILTER_REJECT; }   // поддерево другой метки
        return NodeFilter.FILTER_ACCEPT;
      }
    });
    var n = walker.nextNode();
    while (n) {
      if (n.nodeType === 3) {
        var t = n.textContent.replace(/\s+/g, ' ').trim();
        if (t) { parts.push('t:' + t); }
      } else if (!/^(SCRIPT|STYLE|TEMPLATE)$/.test(n.tagName)) {
        parts.push(n.tagName + ':' + styleSig(n));
      }
      n = walker.nextNode();
    }
    return hashStr(parts.join('\n'));
  }

  function opacityChain(el) {
    var o = 1;
    for (var e = el; e && e.nodeType === 1; e = e.parentElement) {
      var cs = getComputedStyle(e);
      if (cs.visibility === 'hidden' || cs.display === 'none') { return 0; }
      o *= parseFloat(cs.opacity);
    }
    return o;
  }

  function docRect(el) {
    var r = el.getBoundingClientRect();
    return { x: Math.round(r.left + window.scrollX), y: Math.round(r.top + window.scrollY), w: Math.round(r.width), h: Math.round(r.height) };
  }

  function collect() {
    var out = [];
    var all = document.body ? document.body.querySelectorAll('*') : [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.closest && el.closest('#kit-marks-host')) { continue; }
      var kind = kindOf(el);
      if (!kind) { continue; }
      if (hiddenForever(el)) { continue; }
      // картинка внутри <picture> — метим только <picture>
      if (kind === 'image' && el.tagName === 'IMG' && el.parentElement && el.parentElement.tagName === 'PICTURE') { continue; }
      var rect = docRect(el);
      var visible = rect.w > 0 && rect.h > 0 && opacityChain(el) > 0.05 && rect.x + rect.w > 0 && rect.y + rect.h > 0;
      out.push({ selector: cssPath(el), kind: kind, tag: el.tagName.toLowerCase(), text: textOf(el, kind), th: textHash(el), visible: visible, rect: rect, _el: el });
    }
    var candSet = new Set(out.map(function (c) { return c._el; }));
    out.forEach(function (c) { c.sh = hashStr(styleSig(c._el)); c.own = ownSig(c._el, candSet); });
    return out;
  }

  function number(cands, opts) {
    opts = opts || {};
    var base = opts.base || 0;
    var pin = opts.pin || null;
    var used = {};
    var max = base;
    if (pin) {
      Object.keys(pin).forEach(function (sel) { var n = pin[sel]; used[n] = true; if (n > max) { max = n; } });
    }
    var next = max;
    cands.forEach(function (c) {
      if (pin && Object.prototype.hasOwnProperty.call(pin, c.selector)) {
        c.n = pin[c.selector];
      } else {
        next += 1;
        while (used[next]) { next += 1; }
        c.n = next;
        used[next] = true;
        if (pin) { c.unpinned = true; }
      }
    });
    // родитель: ближайший помеченный предок
    cands.forEach(function (c) {
      for (var p = c._el.parentElement; p && p !== document.body; p = p.parentElement) {
        var hit = cands.find ? cands.find(function (x) { return x._el === p; }) : null;
        if (hit) { c.parent = hit.n; break; }
      }
      if (c.n - base >= 100) { c.overflow = true; }
    });
    return cands;
  }

  function intersects(a, b) {
    return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
  }
  function area(a, b) {
    var w = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
    var h = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
    return (w > 0 && h > 0) ? w * h : 0;
  }

  // Строки видимого текста (в координатах документа): бейдж не должен закрывать ни одну из них.
  function textRects() {
    var out = [];
    if (!document.body) { return out; }
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    var range = document.createRange();
    while (walker.nextNode()) {
      var t = walker.currentNode;
      if (!t.textContent.trim()) { continue; }
      var p = t.parentElement;
      if (!p || (p.closest && p.closest('#kit-marks-host'))) { continue; }
      if (/^(SCRIPT|STYLE|NOSCRIPT|TEMPLATE|TITLE|OPTION)$/.test(p.tagName)) { continue; }
      range.selectNodeContents(t);
      var list = range.getClientRects();
      for (var i = 0; i < list.length; i++) {
        var r = list[i];
        if (r.width > 0 && r.height > 0) {
          out.push({ x: Math.round(r.left + window.scrollX), y: Math.round(r.top + window.scrollY), w: Math.round(r.width), h: Math.round(r.height) });
        }
      }
      if (out.length > 6000) { break; }
    }
    return out;
  }

  // Видимые ::before/::after с содержимым (счётчики шагов, значки): их нет в DOM, поэтому оцениваем место по полям
  // элемента и первому/последнему ребёнку.
  function pseudoRects() {
    var out = [];
    var all = document.body ? document.body.querySelectorAll('*') : [];
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      if (el.closest && el.closest('#kit-marks-host')) { continue; }
      ['::before', '::after'].forEach(function (pe) {
        var ps = getComputedStyle(el, pe);
        var c = ps && ps.content;
        if (!c || c === 'none' || c === 'normal' || c === '""' || c === "''" || ps.display === 'none') { return; }
        var r = el.getBoundingClientRect();
        if (!r.width || !r.height) { return; }
        var cs = getComputedStyle(el);
        var left = r.left + parseFloat(cs.borderLeftWidth) + parseFloat(cs.paddingLeft);
        var right = r.right - parseFloat(cs.borderRightWidth) - parseFloat(cs.paddingRight);
        var top, bottom;
        if (pe === '::before') {
          top = r.top + parseFloat(cs.borderTopWidth) + parseFloat(cs.paddingTop);
          bottom = el.firstElementChild ? el.firstElementChild.getBoundingClientRect().top : top + (parseFloat(ps.fontSize) || 16) * 1.3;
        } else {
          bottom = r.bottom - parseFloat(cs.borderBottomWidth) - parseFloat(cs.paddingBottom);
          top = el.lastElementChild ? el.lastElementChild.getBoundingClientRect().bottom : bottom - (parseFloat(ps.fontSize) || 16) * 1.3;
        }
        if (bottom - top > 2 && right - left > 2) {
          out.push({ x: Math.round(left + window.scrollX), y: Math.round(top + window.scrollY), w: Math.round(right - left), h: Math.round(bottom - top) });
        }
      });
    }
    return out;
  }

  function clear() {
    var host = document.getElementById('kit-marks-host');
    if (host) { host.remove(); }
  }

  function draw(numbered) {
    clear();
    var host = document.createElement('div');
    host.id = 'kit-marks-host';
    host.setAttribute('aria-hidden', 'true');
    host.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;z-index:2147483647;pointer-events:none;margin:0;padding:0;border:0;';
    var root = host.attachShadow ? host.attachShadow({ mode: 'open' }) : host;
    var style = document.createElement('style');
    style.textContent =
      '.o{position:absolute;box-sizing:border-box;border:1px dashed ' + COLOR + ';opacity:.55;border-radius:2px}' +
      '.o.r{border-style:dotted;opacity:.35}' +
      '.b{position:absolute;box-sizing:border-box;height:16px;padding:0 4px;font:700 11px/16px system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;' +
      'letter-spacing:0;color:#fff;background:' + COLOR + ';border-radius:3px;box-shadow:0 0 0 1px #fff,0 1px 3px rgba(0,0,0,.45);white-space:nowrap;text-align:center}' +
      '.b.r{color:' + COLOR + ';background:#fff;box-shadow:0 0 0 1px ' + COLOR + ',0 1px 3px rgba(0,0,0,.35)}';
    root.appendChild(style);
    var docW = Math.max(document.documentElement.scrollWidth, document.documentElement.clientWidth);
    var docH = Math.max(document.documentElement.scrollHeight, document.documentElement.clientHeight);
    var placed = [];
    var obstacles = numbered.filter(function (c) { return c.visible && c.kind !== 'region' && c.kind !== 'card'; }).map(function (c) { return { n: c.n, r: c.rect }; });
    var texts = textRects().concat(pseudoRects());
    var textOverlaps = [];
    var badges = [];
    var overlaps = [];
    numbered.forEach(function (c) {
      if (!c.visible) { return; }
      var r = c.rect;
      var isRegion = c.kind === 'region';
      var o = document.createElement('div');
      o.className = 'o' + (isRegion ? ' r' : '');
      o.style.cssText = 'left:' + r.x + 'px;top:' + r.y + 'px;width:' + r.w + 'px;height:' + r.h + 'px';
      root.appendChild(o);
      var label = String(c.n);
      var bw = 9 + label.length * 7;
      var bh = 16;
      var cands = [
        ['above', r.x, r.y - bh - 1],
        ['left', r.x - bw - 2, r.y],
        ['above-right', r.x + r.w - bw, r.y - bh - 1],
        ['left-below', r.x - bw - 2, r.y + Math.max(0, r.h - bh)],
        ['below', r.x, r.y + r.h + 1],
        ['inside', r.x + 1, r.y + 1],
        ['inside-right', r.x + r.w - bw - 1, r.y + 1],
        ['right', r.x + r.w + 2, r.y]
      ];
      if (isRegion) { cands = [['inside', r.x + 2, r.y + 2], ['inside-right', r.x + r.w - bw - 2, r.y + 2], ['left', r.x - bw - 2, r.y + 2]].concat(cands); }
      var chosen = null;
      var fallback = null;
      for (var i = 0; i < cands.length; i++) {
        var b = { x: Math.round(cands[i][1]), y: Math.round(cands[i][2]), w: bw, h: bh };
        if (b.x < 0 || b.y < 0 || b.x + b.w > docW || b.y + b.h > docH) { continue; }
        var hitBadge = placed.some(function (p) { return intersects(p, b); });
        if (hitBadge) { continue; }
        if (!fallback) { fallback = { pos: cands[i][0], b: b }; }
        var hitText = obstacles.some(function (ob) { return ob.n !== c.n && intersects(ob.r, b); }) ||
            texts.some(function (tr) { return intersects(tr, b); });
        if (hitText) { continue; }
        chosen = { pos: cands[i][0], b: b };
        break;
      }
      if (!chosen) { chosen = fallback || { pos: 'forced', b: { x: Math.max(0, r.x), y: Math.max(0, r.y), w: bw, h: bh } }; }
      var el = document.createElement('div');
      el.className = 'b' + (isRegion ? ' r' : '');
      el.textContent = label;
      el.style.cssText = 'left:' + chosen.b.x + 'px;top:' + chosen.b.y + 'px;width:' + bw + 'px';
      root.appendChild(el);
      placed.push(chosen.b);
      var rec = { n: c.n, x: chosen.b.x, y: chosen.b.y, w: bw, h: bh, pos: chosen.pos };
      badges.push(rec);
      obstacles.forEach(function (ob) {
        if (ob.n === c.n) { return; }
        var a = area(ob.r, chosen.b);
        if (a > 0) { overlaps.push({ badge: c.n, covers: ob.n, px: a }); }
      });
      var tpx = 0;
      texts.forEach(function (tr) { tpx += area(tr, chosen.b); });
      if (tpx > 0) { textOverlaps.push({ badge: c.n, px: tpx, pos: chosen.pos }); }
    });
    document.documentElement.appendChild(host);
    return { badges: badges, overlaps: overlaps, textOverlaps: textOverlaps };
  }

  function contains(outer, inner) {
    return inner.x >= outer.x && inner.y >= outer.y && inner.x + inner.w <= outer.x + outer.w && inner.y + inner.h <= outer.y + outer.h;
  }

  function strip(c) {
    var o = {};
    for (var k in c) { if (k !== '_el' && Object.prototype.hasOwnProperty.call(c, k)) { o[k] = c[k]; } }
    return o;
  }

  function run(opts) {
    var cands = number(collect(), opts || {});
    var drawn = draw(cands);
    return {
      version: VERSION,
      url: location.pathname,
      viewport: { w: document.documentElement.clientWidth, h: window.innerHeight },
      theme: document.documentElement.getAttribute('data-theme') || '',
      marks: cands.map(strip),
      badges: drawn.badges,
      overlaps: drawn.overlaps,
      textOverlaps: drawn.textOverlaps
    };
  }

  window.__kitMarks = { version: VERSION, collect: collect, number: number, draw: draw, clear: clear, run: run };

  // Самостоятельный режим: артборд открыт напрямую с ?marks=1 (номера — в порядке DOM с base из ?base=)
  try {
    var q = new URLSearchParams(location.search);
    if (q.get('marks') === '1' && !window.__kitMarksManual) {
      var go = function () { window.__kitMarksResult = run({ base: parseInt(q.get('base') || '0', 10) || 0 }); };
      if (document.readyState === 'complete') { go(); } else { window.addEventListener('load', go); }
    }
  } catch (e) { /* no-op */ }
})();
