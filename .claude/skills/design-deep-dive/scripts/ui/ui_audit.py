#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Объединённый прогон визуального QA страницы: измерение + сверка с токенами и порогами базы + отчёт.

Написано агентом I волны 3 проекта ui-research. Сводит в один запуск то, что раньше было разнесено:
  * скрипт computed styles и пороги приёмки  — `04-shape-elevation/03-tools-checks-and-ai-errors.md` §2, §6, §8;
  * 12 проверок раскладки                    — `05-layout-grid/06-ai-errors-and-checks.md` §3;
  * 19 проверок типографики                  — `02-typography/06-localization-and-ai-errors.md` §5;
  * псевдокод проверок состояний             — `06-components-visual/07-states-matrix.md` §12;
  * нормы практики 24 живых продуктов        — `10-design-systems-atlas/04-live-products-measured.md` §8;
  * проверки токенов и пять грепов           — `09-design-tokens/05-anti-patterns-and-pipeline.md` §3.
Расчёты цвета берутся из соседнего `color.py` (WCAG 2, APCA, OKLCH, ΔE, композитинг альфы).

Использование:
    python3 ui_audit.py ПУТЬ_ИЛИ_URL [ключи]
    python3 ui_audit.py 14-recipes/examples/01-table.html --preset admin --scheme both --reduced-motion --hover --tab 20
    python3 ui_audit.py --batch список.txt --preset admin --out 99-raw/cache/audit
    python3 ui_audit.py --selftest        # проверка порогов и парсеров без браузера

Ключи:
    --preset admin|consumer   набор разрешённых значений и порогов (по умолчанию admin)
    --tokens ФАЙЛ.json        DTCG-набор токенов: шкалы берутся из него, а не из пресета
    --viewport WxH            окно, по умолчанию 1440x900 (повторять ключ для нескольких прогонов)
    --scheme light|dark|both  цветовая схема (по умолчанию light)
    --reduced-motion          дополнительный прогон с `prefers-reduced-motion: reduce`
    --hover                   прогон hover по выборке интерактивных элементов (до 12 штук)
    --tab N                   пройти Tab N раз и проверить индикатор фокуса (по умолчанию 0, рекомендуется 20)
    --touch                   дополнительный прогон 390x844 с `pointer: coarse` и порогом целей 44
    --out КАТАЛОГ             куда писать отчёт (по умолчанию 99-raw/cache/audit)
    --name ИМЯ                имя файлов отчёта вместо автогенерации
    --strict-border           требовать контраст границы контрола >= 3:1 (WCAG 1.4.11) вместо режима практики
    --max-elements N          предел числа разбираемых узлов (по умолчанию 4000)
    --wait N                  ожидание после загрузки, мс (по умолчанию 400 для файлов, 2000 для URL)
    --fail-on blocker|serious|any   код возврата 1, если есть нарушения такого уровня
    --quiet                   не печатать таблицу в stdout

Каталог проверок: 81 идентификатор в 14 группах (A отступы, B размеры, C форма, D глубина, E слои,
F цели, G фокус, H типографика, I цвет, J раскладка, K движение, L антислоп, M сокращённое движение,
S состояния). На одном прогоне срабатывают 55–66: часть зависит от режима.

Что на выходе:
    <out>/<name>.md    таблица «правило | найдено | порог | вердикт | серьёзность» + примеры узлов
    <out>/<name>.json  те же данные машиночитаемо (для цикла «прогнал -> вернул модели -> правки»)

Ограничения (важно для чтения результата):
  * computed styles — это применение токенов на конкретном экране, а не сами токены;
  * скрипт не видит смысл: `bg-subtle` вместо `bg-component` он пропустит (это ловится только ревью);
  * иерархия, осмысленность метрик, «ложное дно» и вкус не проверяются в принципе;
  * кросс-доменные iframe и canvas не разбираются;
  * контраст текста на градиенте и на картинке считается по цвету ближайшего непрозрачного предка,
    то есть в этом случае значение недостоверно и помечается как `warn`.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("ui"))
DEFAULT_OUT = str(kbpaths.out("ui", "audit"))

from color import hex2oklch, wcag, apca, composite, dE_oklab  # noqa: E402

# =====================================================================================
# 1. Пресеты: разрешённые значения и пороги
# =====================================================================================

PRESET_ADMIN = {
    "name": "admin",
    "title": "плотная админка (база 14 px, контрол 32)",
    # шкалы значений
    "spacing": [0, 2, 4, 6, 8, 12, 16, 24, 32, 40, 48, 64, 96],
    "radius": [0, 2, 4, 6, 8, 9999],
    "heights": [24, 28, 32, 36, 40, 48],
    "font_sizes": [11, 12, 14, 16, 20, 24, 28, 32],
    "font_weights": [400, 500, 600, 700],
    "icon_sizes": [12, 14, 16, 20, 24],
    "zindex": [0, 10, 100, 200, 1000, 1100, 1200, 1300, 1400, 1500],
    "durations": [0, 50, 100, 150, 200, 300, 400, 600],
    "border_widths": [0, 1, 2],
    # пороги
    "spacing_in_scale_min": 0.95,
    "unique_gap_max": 6,
    "fraction_values_max": 0.03,
    "unique_spacing_max": 15,
    "unique_heights_max": 3,
    "unique_radius_max": 6,
    "unique_shadow_max": 7,
    "shadow_share_max": 0.15,
    "glass_max": 2,
    "unique_font_sizes_max": 8,
    "unique_font_weights_max": 4,
    "unique_text_colors_max": 9,   # практика: медиана 7.5, потолок 8; полный ролевой набор схемы — 9
    "unique_bg_colors_max": 10,
    "unique_border_colors_max": 5,
    "para_max_width": 720,
    "form_max_width": 640,
    "sidebar_max": 300,
    "sidebar_min": 200,
    "content_min": 640,
    "sticky_sum_max": 192,
    "page_header_max": 120,
    "body_leading": (1.28, 1.55),
    "target_min": 24,
    "target_gap_min": 4,
    "focus_width_min": 2,
    "duration_300_share_max": 0.20,
    "text_contrast_min": 4.5,
    "large_text_contrast_min": 3.0,
    "border_contrast_min": 3.0,       # при --strict-border
    "border_contrast_practice": 1.20,  # медиана практики 1.30, ниже 1.2 граница не видна совсем
    "nesting_shadow_max": 1,
    "hover_delta_L": (0.02, 0.08),
}

PRESET_CONSUMER = dict(PRESET_ADMIN)
PRESET_CONSUMER.update({
    "name": "consumer",
    "title": "клиентский сервис (база 16 px, контрол 40)",
    "radius": [0, 6, 10, 14, 20, 9999],
    "heights": [24, 32, 36, 40, 44, 48],
    "font_sizes": [12, 14, 16, 18, 20, 24, 32, 40],
    "icon_sizes": [16, 20, 24],
    "unique_font_sizes_max": 8,
    "unique_shadow_max": 7,
    "shadow_share_max": 0.25,
    "sidebar_max": 300,
    "form_max_width": 640,
    "body_leading": (1.4, 1.65),
})

PRESETS = {"admin": PRESET_ADMIN, "consumer": PRESET_CONSUMER}

SEV_BLOCKER, SEV_SERIOUS, SEV_POLISH = "блокер", "серьёзно", "полировка"
SEV_ORDER = {SEV_BLOCKER: 0, SEV_SERIOUS: 1, SEV_POLISH: 2}

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⬀-⯿️]"
)
TITLE_CASE_RU_RE = re.compile(r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+")
EN_NUMBER_RE = re.compile(r"\d,\d{3}\b")
PERCENT_GLUED_RE = re.compile(r"\d%")


# =====================================================================================
# 2. Чтение набора токенов DTCG (необязательно)
# =====================================================================================

def load_dtcg(path):
    """Достать из DTCG-файла множества разрешённых значений: отступы, радиусы, высоты, кегли, цвета, z, длительности."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    flat = {}

    def walk(node, prefix):
        if not isinstance(node, dict):
            return
        if "$value" in node:
            flat[".".join(prefix)] = node
            return
        for k, v in node.items():
            if k.startswith("$"):
                continue
            walk(v, prefix + [k])

    walk(data, [])

    def resolve(val, depth=0):
        if depth > 8:
            return val
        if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
            ref = val[1:-1]
            tgt = flat.get(ref)
            return resolve(tgt["$value"], depth + 1) if tgt else val
        return val

    out = {"spacing": set(), "radius": set(), "sizes": set(), "font_sizes": set(),
           "colors": set(), "zindex": set(), "durations": set(), "font_weights": set()}
    for path_name, node in flat.items():
        v = resolve(node.get("$value"))
        t = node.get("$type")
        if t is None:
            # тип наследуется от группы: восстановим по имени ветки
            head = path_name.split(".")[0]
            t = {"space": "dimension", "size": "dimension", "radius": "dimension",
                 "color": "color", "z": "number", "motion": "duration"}.get(head)
        if isinstance(v, dict) and "value" in v and "unit" in v:
            px = float(v["value"]) * (16.0 if v["unit"] == "rem" else 1.0)
            if path_name.startswith("space") or path_name.startswith("primitive.size"):
                out["spacing"].add(round(px, 2))
            if path_name.startswith("radius"):
                out["radius"].add(round(px, 2))
            if path_name.startswith("size"):
                out["sizes"].add(round(px, 2))
            if "font.size" in path_name or path_name.startswith("primitive.font.size"):
                out["font_sizes"].add(round(px, 2))
            if v["unit"] in ("ms", "s"):
                out["durations"].add(round(px, 2))
        if isinstance(v, dict) and "unit" in v and v["unit"] in ("ms", "s"):
            out["durations"].add(float(v["value"]) * (1000 if v["unit"] == "s" else 1))
        if isinstance(v, dict) and "hex" in v:
            out["colors"].add(v["hex"].lower())
        # переопределения режимов лежат внутри токена ($extensions.<ns>.modes.dark и т. п.)
        for ns, ext in (node.get("$extensions") or {}).items():
            if not isinstance(ext, dict) or not ns.endswith("modes"):
                continue
            for mode, mv in ext.items():
                mv = resolve(mv)
                if isinstance(mv, dict) and "hex" in mv:
                    out["colors"].add(mv["hex"].lower())
                elif isinstance(mv, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", mv):
                    out["colors"].add(mv.lower())
                elif isinstance(mv, dict) and "value" in mv and "unit" in mv:
                    pxm = float(mv["value"]) * (16.0 if mv["unit"] == "rem" else 1.0)
                    if path_name.startswith("space"):
                        out["spacing"].add(round(pxm, 2))
                    elif path_name.startswith("size"):
                        out["sizes"].add(round(pxm, 2))
        if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v):
            out["colors"].add(v.lower())
        if t == "number" and isinstance(v, (int, float)) and path_name.startswith("z"):
            out["zindex"].add(int(v))
        if "font.weight" in path_name and isinstance(v, (int, float)):
            out["font_weights"].add(int(v))
    return {k: sorted(v) for k, v in out.items()}


# =====================================================================================
# 3. Сбор данных в странице
# =====================================================================================

COLLECT_JS = r"""
(opts) => {
  const MAXN = opts.maxElements;
  const toHex = (s) => {
    if (!s) return null;
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number);
    if (p.length < 3 || p.some(isNaN)) return null;
    const a = p.length > 3 ? p[3] : 1;
    const hex = '#' + p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
    return { hex, a };
  };
  const px = v => (v && v.endsWith && v.endsWith('px')) ? Math.round(parseFloat(v) * 100) / 100 : null;

  // эффективный фон: первый непрозрачный предок, с композитингом полупрозрачных слоёв поверх него
  const effBg = (el) => {
    const stack = [];
    let node = el, gradient = false;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') gradient = true;
      const c = toHex(cs.backgroundColor);
      if (c && c.a > 0) {
        stack.push(c);
        if (c.a >= 0.999) break;
      }
      node = node.parentElement;
    }
    if (!stack.length) return { hex: '#ffffff', gradient, guessed: true };
    const composited = stack.length > 1 || stack[stack.length - 1].a < 0.999;
    let base = stack[stack.length - 1];
    let cur = base.hex;
    for (let i = stack.length - 2; i >= 0; i--) {
      const s = stack[i];
      const f = s.hex.slice(1).match(/../g).map(h => parseInt(h, 16));
      const b = cur.slice(1).match(/../g).map(h => parseInt(h, 16));
      cur = '#' + [0, 1, 2].map(k => Math.round(f[k] * s.a + b[k] * (1 - s.a)).toString(16).padStart(2, '0')).join('');
    }
    return { hex: cur, gradient, guessed: composited };
  };

  const shortSel = (el) => {
    const id = el.id ? '#' + el.id : '';
    const cls = (typeof el.className === 'string' && el.className)
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return (el.tagName.toLowerCase() + id + cls).slice(0, 60);
  };

  const all = Array.from(document.querySelectorAll('body *')).slice(0, MAXN);
  const rows = [];
  let idx = 0;
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || '';
    const interactive = ['button', 'a', 'input', 'select', 'textarea', 'summary'].includes(tag)
      || el.hasAttribute('tabindex') || ['button', 'link', 'menuitem', 'tab', 'switch', 'checkbox'].includes(role);
    const ownText = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3 && n.textContent.trim())
      .map(n => n.textContent.trim()).join(' ').slice(0, 120);
    const bg = effBg(el);
    const fg = toHex(cs.color);
    const bc = toHex(cs.borderTopColor);
    el.setAttribute('data-uia', String(idx));
    rows.push({
      i: idx++, tag, sel: shortSel(el), role,
      x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width * 100) / 100, h: Math.round(r.height * 100) / 100,
      pt: px(cs.paddingTop), pr: px(cs.paddingRight), pb: px(cs.paddingBottom), pl: px(cs.paddingLeft),
      mt: px(cs.marginTop), mr: px(cs.marginRight), mb: px(cs.marginBottom), ml: px(cs.marginLeft),
      rg: px(cs.rowGap), cg: px(cs.columnGap),
      r1: px(cs.borderTopLeftRadius), r2: px(cs.borderTopRightRadius),
      r3: px(cs.borderBottomRightRadius), r4: px(cs.borderBottomLeftRadius),
      bw: px(cs.borderTopWidth), bwr: px(cs.borderRightWidth), bwb: px(cs.borderBottomWidth), bwl: px(cs.borderLeftWidth),
      sh: cs.boxShadow === 'none' ? null : cs.boxShadow,
      z: cs.zIndex === 'auto' ? null : Number(cs.zIndex),
      bd: (cs.backdropFilter && cs.backdropFilter !== 'none') ? cs.backdropFilter : null,
      fs: px(cs.fontSize), lh: cs.lineHeight === 'normal' ? 'normal' : px(cs.lineHeight),
      fw: Number(cs.fontWeight) || null, ls: cs.letterSpacing === 'normal' ? 0 : px(cs.letterSpacing),
      ff: (cs.fontFamily || '').split(',')[0].replace(/["']/g, '').slice(0, 30),
      fvn: cs.fontVariantNumeric, tt: cs.textTransform, ta: cs.textAlign,
      col: fg ? fg.hex : null, cola: fg ? fg.a : 1,
      bg: bg.hex, bggrad: bg.gradient, bgguess: bg.guessed,
      bcol: bc && bc.a > 0 ? bc.hex : null, bcola: bc ? bc.a : 0,
      ow: px(cs.outlineWidth), ost: cs.outlineStyle, oc: toHex(cs.outlineColor) ? toHex(cs.outlineColor).hex : null,
      pos: cs.position, ov: cs.overflowX + ' ' + cs.overflowY,
      mw: cs.maxWidth === 'none' ? null : px(cs.maxWidth),
      gtc: cs.gridTemplateColumns && cs.gridTemplateColumns !== 'none' ? cs.gridTemplateColumns.slice(0, 120) : null,
      tp: cs.transitionProperty, td: cs.transitionDuration, an: cs.animationName,
      txt: ownText, inter: interactive, disp: cs.display,
      dis: el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true',
      inflow: (() => { const p = el.parentElement; if (!p) return false;
        const d = getComputedStyle(el).display;
        return (d === 'inline' || d === 'inline-block') &&
               Array.from(p.childNodes).some(n => n.nodeType === 3 && n.textContent.trim().length > 1); })(),
      par: el.parentElement && el.parentElement.hasAttribute('data-uia') ? Number(el.parentElement.getAttribute('data-uia')) : null,
      svg: tag === 'svg' ? { w: Math.round(r.width), h: Math.round(r.height), sw: cs.strokeWidth, vb: el.getAttribute('viewBox') || '' } : null,
      inline: el.getAttribute('style') || '',
    });
  }

  const html = document.documentElement;
  return {
    rows,
    meta: {
      lang: html.getAttribute('lang') || '',
      scrollW: html.scrollWidth, innerW: window.innerWidth, innerH: window.innerHeight,
      bodyBg: getComputedStyle(document.body).backgroundColor,
      title: document.title,
      text: (document.body.innerText || '').slice(0, 20000),
      viewportMeta: (document.querySelector('meta[name=viewport]') || {}).content || '',
      styleSheets: Array.from(document.styleSheets).length,
    },
  };
}
"""

FOCUS_REST_JS = r"""
() => {
  const sel = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  const out = {};
  document.querySelectorAll(sel).forEach((el, n) => {
    el.setAttribute('data-uiafocus', String(n));
    const cs = getComputedStyle(el);
    out[n] = { ow: cs.outlineWidth, ost: cs.outlineStyle, oc: cs.outlineColor,
               sh: cs.boxShadow, bc: cs.borderTopColor, bg: cs.backgroundColor,
               sel: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
               txt: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 40) };
  });
  return out;
}
"""

FOCUS_NOW_JS = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  return { n: el.getAttribute('data-uiafocus'), tag: el.tagName.toLowerCase(),
           ow: cs.outlineWidth, ost: cs.outlineStyle, oc: cs.outlineColor, oo: cs.outlineOffset,
           sh: cs.boxShadow, bc: cs.borderTopColor, bg: cs.backgroundColor,
           around: (() => { let p = el.parentElement;
             while (p) { const c = getComputedStyle(p).backgroundColor;
               const m = c.match(/rgba?\(([^)]+)\)/);
               if (m) { const v = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number);
                 if (v.length < 4 || v[3] > 0.9) return c; }
               p = p.parentElement; } return 'rgb(255,255,255)'; })(),
           w: Math.round(r.width), h: Math.round(r.height),
           txt: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 40),
           clipped: (() => {
             const ring = (parseFloat(cs.outlineWidth) || 0) + Math.max(0, parseFloat(cs.outlineOffset) || 0);
             if (ring <= 0) return false;
             const box = { l: r.left - ring, t: r.top - ring, rt: r.right + ring, b: r.bottom + ring };
             let p = el.parentElement;
             while (p && p !== document.body) {
               const s = getComputedStyle(p);
               if (s.overflow !== 'visible' || s.overflowX !== 'visible' || s.overflowY !== 'visible') {
                 const pr = p.getBoundingClientRect();
                 if (box.l < pr.left - 0.5 || box.t < pr.top - 0.5 ||
                     box.rt > pr.right + 0.5 || box.b > pr.bottom + 0.5) return true;
               }
               p = p.parentElement;
             }
             return false; })() };
}
"""


# =====================================================================================
# 4. Вспомогательное
# =====================================================================================

def parse_shadows(css):
    """Разбить строку box-shadow на слои и вернуть список (offsetX, offsetY, blur, spread, inset)."""
    if not css or css == "none":
        return []
    parts, depth, cur = [], 0, ""
    for ch in css:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    layers = []
    for p in parts:
        inset = "inset" in p
        nums = [float(x) for x in re.findall(r"(-?\d+(?:\.\d+)?)px", p)]
        while len(nums) < 4:
            nums.append(0.0)
        layers.append((nums[0], nums[1], nums[2], nums[3], inset))
    return layers


def parse_durations(css):
    if not css:
        return []
    out = []
    for token in css.split(","):
        token = token.strip()
        m = re.match(r"^(-?\d+(?:\.\d+)?)(ms|s)$", token)
        if m:
            out.append(float(m.group(1)) * (1000 if m.group(2) == "s" else 1))
    return out


def in_scale(v, scale, tol=0.51):
    return any(abs(v - s) <= tol for s in scale)


def is_fraction(v, tol=0.01):
    return abs(v - round(v)) > tol


def gap_between(a, b):
    dx = max(0, max(a["x"] - (b["x"] + b["w"]), b["x"] - (a["x"] + a["w"])))
    dy = max(0, max(a["y"] - (b["y"] + b["h"]), b["y"] - (a["y"] + a["h"])))
    return math.hypot(dx, dy)


def okl(h):
    try:
        return hex2oklch(h)[0]
    except Exception:
        return None


# =====================================================================================
# 5. Проверки
# =====================================================================================

class Report:
    def __init__(self, target, preset, context):
        self.target = target
        self.preset = preset
        self.context = context      # {'scheme': 'light', 'viewport': '1440x900', ...}
        self.findings = []

    def add(self, cid, group, rule, found, threshold, ok, severity, examples=None, note=None):
        self.findings.append({
            "id": cid, "group": group, "rule": rule,
            "found": found, "threshold": threshold,
            "verdict": "OK" if ok is True else ("WARN" if ok is None else "FAIL"),
            "severity": severity,
            "examples": (examples or [])[:6],
            "note": note,
        })


def run_checks(data, preset, opts, ctx):
    rows = data["rows"]
    meta = data["meta"]
    rep = Report(ctx["target"], preset["name"], ctx)
    by_i = {r["i"]: r for r in rows}
    text_rows = [r for r in rows if r["txt"]]
    interactive = [r for r in rows if r["inter"]]
    dark = ctx.get("scheme") == "dark"

    # ---------------------------------------------------------------- A. Отступы
    sp_vals = []
    for r in rows:
        for k in ("pt", "pr", "pb", "pl", "mt", "mr", "mb", "ml", "rg", "cg"):
            v = r[k]
            if v is not None and v != 0:
                sp_vals.append(v)
    n_sp = len(sp_vals) or 1
    in_sc = [v for v in sp_vals if in_scale(v, preset["spacing"])]
    share = len(in_sc) / n_sp
    bad = sorted({v for v in sp_vals if not in_scale(v, preset["spacing"])})
    rep.add("A1", "Отступы", "Доля padding/margin/gap из шкалы",
            f"{share*100:.1f} %", f"≥ {preset['spacing_in_scale_min']*100:.0f} %",
            share >= preset["spacing_in_scale_min"], SEV_SERIOUS,
            [f"вне шкалы: {', '.join(str(v) for v in bad[:12])}"] if bad else [])

    five = sorted({v for v in sp_vals if abs(v % 5) < 0.01 and abs(v % 4) > 0.01})
    rep.add("A2", "Отступы", "Значения, кратные 5 и не кратные 4 («шкала десятками»)",
            len(five), "0", not five, SEV_SERIOUS, [str(v) for v in five[:8]])

    gaps = sorted({r["rg"] for r in rows if r["rg"]} | {r["cg"] for r in rows if r["cg"]})
    rep.add("A3", "Отступы", "Уникальных значений gap", len(gaps), f"≤ {preset['unique_gap_max']}",
            len(gaps) <= preset["unique_gap_max"], SEV_POLISH, [", ".join(str(g) for g in gaps)])

    frac = [v for v in sp_vals if is_fraction(v)]
    rep.add("A4", "Отступы", "Доля дробных значений отступа",
            f"{len(frac)/n_sp*100:.1f} %", f"≤ {preset['fraction_values_max']*100:.0f} %",
            len(frac) / n_sp <= preset["fraction_values_max"], SEV_POLISH,
            [", ".join(str(v) for v in sorted(set(frac))[:8])])

    uniq_sp = sorted(set(sp_vals))
    rep.add("A5", "Отступы", "Уникальных значений отступа", len(uniq_sp),
            f"≤ {preset['unique_spacing_max']}", len(uniq_sp) <= preset["unique_spacing_max"],
            SEV_POLISH, [", ".join(str(v) for v in uniq_sp[:20])])

    # внешний padding контейнера >= внутренних gap
    bad_nest = []
    LAYOUT_GAP = 12   # зазоры мельче относятся к внутренностям компонента (иконка-текст), а не к раскладке
    for r in rows:
        kids_gap = max([max(c["rg"] or 0, c["cg"] or 0) for c in rows if c["par"] == r["i"]] + [0])
        own_pad = min([v for v in (r["pt"], r["pb"]) if v is not None] or [0])
        if kids_gap >= LAYOUT_GAP and own_pad and kids_gap > own_pad + 0.5:
            bad_nest.append(f"{r['sel']}: padding {own_pad}, зазор внутри {kids_gap}")
    rep.add("A6", "Отступы", "Внешний padding контейнера ≥ внутренних зазоров", len(bad_nest), "0",
            not bad_nest, SEV_POLISH, bad_nest)

    # ---------------------------------------------------------------- B. Размеры
    ctrl = [r for r in interactive if r["tag"] in ("button", "input", "select")
            or r["role"] == "button"]
    ctrl = [r for r in ctrl if r["h"] >= 12 and r["w"] >= 12
            and r["role"] != "switch"
            and not (r["tag"] == "input" and r["h"] <= 24 and r["w"] <= 48)]
    heights = sorted({round(r["h"]) for r in ctrl})
    rep.add("B1", "Размеры", "Уникальных высот контролов", len(heights),
            f"≤ {preset['unique_heights_max']}", len(heights) <= preset["unique_heights_max"],
            SEV_SERIOUS, [", ".join(str(h) for h in heights)])

    off_row = [h for h in heights if not in_scale(h, preset["heights"], tol=0.51)]
    rep.add("B2", "Размеры", f"Высоты вне ряда {'/'.join(str(x) for x in preset['heights'])}",
            len(off_row), "0", not off_row, SEV_SERIOUS, [", ".join(str(h) for h in off_row)])

    # одна высота в горизонтальном ряду
    rowsy = defaultdict(list)
    for r in ctrl:
        rowsy[round(r["y"] / 4) * 4].append(r)
    bad_rows = []
    for y, group in rowsy.items():
        if len(group) < 2:
            continue
        hs = {round(g["h"]) for g in group}
        if len(hs) > 1:
            bad_rows.append(f"y≈{y}: {sorted(hs)} ({', '.join(g['sel'] for g in group[:4])})")
    rep.add("B3", "Размеры", "Одна высота контролов в горизонтальном ряду", len(bad_rows), "0",
            not bad_rows, SEV_SERIOUS, bad_rows)

    icon_btn = [r for r in ctrl if not r["txt"] and r["w"] <= 56 and r["h"] <= 56
                and r["tag"] == "button" and r["role"] != "switch"]
    not_square = [f"{r['sel']} {r['w']}×{r['h']}" for r in icon_btn if abs(r["w"] - r["h"]) > 1]
    rep.add("B4", "Размеры", "Иконочные кнопки квадратные", len(not_square), "0",
            not not_square, SEV_POLISH, not_square)

    svgs_all = [r for r in rows if r["svg"]]
    svgs = [r for r in svgs_all if max(r["svg"]["w"], r["svg"]["h"]) <= 32]
    big_svg = [f"{r['sel']} {round(r['svg']['w'])}×{round(r['svg']['h'])}" for r in svgs_all if r not in svgs]
    svg_sizes = sorted({round(r["svg"]["w"]) for r in svgs})
    off_icons = [s for s in svg_sizes if s not in preset["icon_sizes"]]
    rep.add("B5", "Размеры", f"Размеры иконок из ряда {preset['icon_sizes']}", len(off_icons), "0",
            not off_icons, SEV_POLISH, [", ".join(str(s) for s in off_icons)] if off_icons else [])

    sw = sorted({r["svg"]["sw"] for r in svgs if r["svg"]["sw"] and r["svg"]["sw"] != "1px"})
    vb = sorted({r["svg"]["vb"] for r in svgs if r["svg"]["vb"]})
    rep.add("B5b", "Размеры", "Пиктограммы и иллюстрации (svg крупнее 32 px)", len(big_svg),
            "информативно", None, SEV_POLISH, big_svg,
            note="граница классов: до 32 px иконка, 48–96 пиктограмма, от 120 иллюстрация "
                 "(07-iconography-imagery/02 §4.2)")
    rep.add("B6", "Размеры", "Один набор иконок (один viewBox, одна толщина штриха)",
            f"viewBox: {len(vb)}, stroke-width: {max(len(sw), 1)}", "1 / 1",
            len(vb) <= 1, SEV_POLISH, [", ".join(vb[:4]), ", ".join(sw[:4])])

    # строки таблиц и списков одной высоты
    bad_lists = []
    for parent in {r["par"] for r in rows if r["par"] is not None}:
        kids = [r for r in rows if r["par"] == parent and r["tag"] in ("tr", "li")]
        if len(kids) >= 3:
            hs = {round(k["h"]) for k in kids}
            if len(hs) > 1:
                p = by_i.get(parent)
                bad_lists.append(f"{p['sel'] if p else parent}: высоты {sorted(hs)}")
    rep.add("B7", "Размеры", "Строки одного списка/таблицы одной высоты", len(bad_lists), "0",
            not bad_lists, SEV_POLISH, bad_lists)

    # ---------------------------------------------------------------- C. Форма
    radii = []
    for r in rows:
        for k in ("r1", "r2", "r3", "r4"):
            v = r[k]
            if v:
                radii.append(v)
    uniq_r = sorted(set(radii))
    rep.add("C1", "Форма", "Уникальных значений border-radius", len(uniq_r),
            f"≤ {preset['unique_radius_max']}", len(uniq_r) <= preset["unique_radius_max"],
            SEV_POLISH, [", ".join(str(v) for v in uniq_r)])

    off_r = [v for v in uniq_r if not in_scale(v, preset["radius"], tol=0.51)]
    rep.add("C2", "Форма", "Радиусы вне шкалы", len(off_r), "0", not off_r, SEV_POLISH,
            [", ".join(str(v) for v in off_r)])

    bad_nested_r = []
    for r in rows:
        if not r["r1"] or r["r1"] >= 900:
            continue
        p = by_i.get(r["par"])
        while p is not None and not p["r1"]:
            p = by_i.get(p["par"])
        if p and p["r1"] < 900 and r["r1"] > p["r1"] + 0.5:
            bad_nested_r.append(f"{r['sel']} r={r['r1']} внутри {p['sel']} r={p['r1']}")
    rep.add("C3", "Форма", "Вложенный радиус не больше внешнего", len(bad_nested_r), "0",
            not bad_nested_r, SEV_POLISH, bad_nested_r)

    bws = sorted({v for r in rows for v in (r["bw"], r["bwr"], r["bwb"], r["bwl"]) if v})
    off_bw = [v for v in bws if v not in preset["border_widths"]]
    rep.add("C4", "Форма", "Толщины границ только 0 / 1 / 2 px", len(off_bw), "0", not off_bw,
            SEV_POLISH, [", ".join(str(v) for v in off_bw)])

    too_round = [f"{r['sel']} r={r['r1']} при {r['w']}×{r['h']}"
                 for r in rows if r["r1"] and r["r1"] < 900 and r["r1"] > 0.25 * min(r["w"], r["h"]) + 0.5]
    rep.add("C5", "Форма", "Радиус ≤ 25 % меньшей стороны элемента", len(too_round), "0",
            not too_round, SEV_POLISH, too_round)

    # ---------------------------------------------------------------- D. Глубина
    shadows = [r["sh"] for r in rows if r["sh"]]
    uniq_sh = sorted(set(shadows))
    rep.add("D1", "Глубина", "Уникальных значений box-shadow", len(uniq_sh),
            f"≤ {preset['unique_shadow_max']}", len(uniq_sh) <= preset["unique_shadow_max"],
            SEV_POLISH, [s[:90] for s in uniq_sh[:4]])

    dirs = set()
    for s in uniq_sh:
        for (ox, oy, blur, spread, inset) in parse_shadows(s):
            if inset or (ox == 0 and oy == 0):
                continue
            dirs.add((0 if ox == 0 else (1 if ox > 0 else -1), 0 if oy == 0 else (1 if oy > 0 else -1)))
    rep.add("D2", "Глубина", "Один источник света (одинаковое направление теней)",
            len(dirs) if dirs else 0, "≤ 1", len(dirs) <= 1, SEV_POLISH,
            [str(sorted(dirs))] if len(dirs) > 1 else [])

    glass = [r["sel"] for r in rows if r["bd"]]
    rep.add("D3", "Глубина", "Элементов с backdrop-filter", len(glass), f"≤ {preset['glass_max']}",
            len(glass) <= preset["glass_max"], SEV_POLISH, glass)

    glow = []
    for s in uniq_sh:
        for (ox, oy, blur, spread, inset) in parse_shadows(s):
            if not inset and ox == 0 and oy == 0 and blur > 8:
                glow.append(s[:70])
    rep.add("D4", "Глубина", "Свечения (тень с нулевым смещением и blur > 8)", len(glow), "0",
            not glow, SEV_SERIOUS, glow)

    n_blocks = max(len([r for r in rows if r["w"] > 40 and r["h"] > 20]), 1)
    sh_share = len(shadows) / n_blocks
    rep.add("D5", "Глубина", "Доля блоков с тенью", f"{sh_share*100:.1f} %",
            f"≤ {preset['shadow_share_max']*100:.0f} %", sh_share <= preset["shadow_share_max"],
            SEV_POLISH)

    deep = []
    for r in rows:
        if not r["sh"]:
            continue
        d, p = 0, by_i.get(r["par"])
        while p is not None:
            if p["sh"]:
                d += 1
            p = by_i.get(p["par"])
        if d > preset["nesting_shadow_max"]:
            deep.append(f"{r['sel']} (вложенность теней {d + 1})")
    rep.add("D6", "Глубина", "Глубина вложенности элементов с тенью", len(deep),
            f"≤ {preset['nesting_shadow_max'] + 1}", not deep, SEV_POLISH, deep)

    # ---------------------------------------------------------------- E. Слои
    zs = sorted({r["z"] for r in rows if r["z"] is not None})
    off_z = [z for z in zs if z not in preset["zindex"]]
    rep.add("E1", "Слои", "z-index вне шкалы", len(off_z), "0", not off_z, SEV_SERIOUS,
            [", ".join(str(z) for z in off_z)])
    big_z = [z for z in zs if z > 1500]
    rep.add("E2", "Слои", "z-index больше 1500", len(big_z), "0", not big_z, SEV_SERIOUS,
            [", ".join(str(z) for z in big_z)])

    # ---------------------------------------------------------------- F. Цели нажатия
    tmin = ctx.get("target_min", preset["target_min"])
    targets = [r for r in interactive if r["w"] > 0 and r["h"] > 0]
    # SC 2.5.8, исключение «Inline»: ссылка внутри строки текста размером не нормируется
    inline_links = [r for r in targets if r["tag"] == "a" and (r.get("inflow") or r.get("disp") == "inline")]
    targets_sized = [r for r in targets if r not in inline_links]
    small = [r for r in targets_sized if min(r["w"], r["h"]) < tmin - 0.5]
    bad_small = []
    for t in small:
        near = any(gap_between(t, o) < preset["target_gap_min"] for o in targets if o["i"] != t["i"])
        if near:
            bad_small.append(f"{t['sel']} {t['w']}×{t['h']} «{t['txt'][:20]}»")
    rep.add("F1", "Цели", f"Цели меньше {tmin}×{tmin} без зазора {preset['target_gap_min']} px",
            len(bad_small), "0", not bad_small, SEV_BLOCKER, bad_small)
    rep.add("F2", "Цели", f"Всего целей меньше {tmin}×{tmin} (включая разнесённые)",
            f"{len(small)} из {len(targets_sized)} (ещё {len(inline_links)} инлайновых ссылок вне нормы)", "информативно",
            True if not small else None, SEV_SERIOUS,
            [f"{t['sel']} {t['w']}×{t['h']}" for t in small[:6]],
            note="SC 2.5.8 допускает недоразмерную цель, если круги диаметром 24 px вокруг центров "
                 "соседних целей не пересекаются; нарушение этого условия ловит F1")

    # ---------------------------------------------------------------- G. Фокус
    no_focus = []
    for r in interactive:
        if r["ost"] == "none" and not r["sh"]:
            no_focus.append(r["sel"])
    rep.add("G1", "Фокус", "Интерактивные элементы без outline и без box-shadow в покое",
            len(no_focus), "информативно", None, SEV_POLISH, no_focus[:6],
            note="сам по себе не дефект: кольцо может появляться только в :focus-visible, см. G3")

    # ---------------------------------------------------------------- H. Типографика
    fss = sorted({r["fs"] for r in text_rows if r["fs"]})
    rep.add("H1", "Типографика", "Уникальных размеров шрифта (у элементов с собственным текстом)",
            len(fss), f"≤ {preset['unique_font_sizes_max']}",
            len(fss) <= preset["unique_font_sizes_max"], SEV_SERIOUS,
            [", ".join(str(v) for v in fss)])

    off_fs = [v for v in fss if not in_scale(v, preset["font_sizes"], tol=0.51)]
    rep.add("H2", "Типографика", "Кегли вне шкалы", len(off_fs), "0", not off_fs, SEV_SERIOUS,
            [", ".join(str(v) for v in off_fs)])

    fws = sorted({r["fw"] for r in text_rows if r["fw"]})
    rep.add("H3", "Типографика", "Уникальных весов шрифта", len(fws),
            f"≤ {preset['unique_font_weights_max']}", len(fws) <= preset["unique_font_weights_max"],
            SEV_POLISH, [", ".join(str(v) for v in fws)])
    light = [v for v in fws if v < 400]
    rep.add("H4", "Типографика", "Веса легче 400", len(light), "0", not light, SEV_POLISH,
            [", ".join(str(v) for v in light)])

    normal_lh = [r["sel"] for r in text_rows if r["lh"] == "normal"]
    rep.add("H5", "Типографика", "line-height: normal", len(normal_lh), "0", not normal_lh,
            SEV_POLISH, normal_lh[:6])

    frac_lh = sorted({r["lh"] for r in text_rows if isinstance(r["lh"], (int, float)) and is_fraction(r["lh"])})
    rep.add("H6", "Типографика", "Дробные line-height в px", len(frac_lh), "0", not frac_lh,
            SEV_POLISH, [", ".join(str(v) for v in frac_lh)])

    body = [r for r in text_rows if r["fs"] and 13 <= r["fs"] <= 17
            and isinstance(r["lh"], (int, float)) and len(r["txt"]) > 40]
    lo, hi = preset["body_leading"]
    bad_lead = [f"{r['sel']} {r['fs']}/{r['lh']} = {r['lh']/r['fs']:.2f}" for r in body
                if not (lo <= r["lh"] / r["fs"] <= hi)]
    rep.add("H7", "Типографика", f"Интерлиньяж тела в коридоре {lo}–{hi}", len(bad_lead), "0",
            not bad_lead, SEV_POLISH, bad_lead)

    paras = [r for r in text_rows if r["tag"] in ("p", "li", "dd") and len(r["txt"]) > 120]
    wide_p = [f"{r['sel']} {r['w']}px" for r in paras if r["w"] > preset["para_max_width"]]
    rep.add("H8", "Типографика", f"Абзацы шире {preset['para_max_width']} px", len(wide_p), "0",
            not wide_p, SEV_SERIOUS, wide_p)

    rep.add("H9", "Типографика", "Атрибут lang на <html>", meta["lang"] or "нет", "задан",
            bool(meta["lang"]), SEV_SERIOUS)

    caps = [r["sel"] for r in text_rows if r["tt"] in ("uppercase", "capitalize")]
    rep.add("H10", "Типографика", "text-transform: uppercase / capitalize", len(caps),
            "0 (кроме осознанных капс-лейблов)", not caps, SEV_POLISH, caps[:6])

    just = [r["sel"] for r in text_rows if r["ta"] == "justify"]
    rep.add("H11", "Типографика", "text-align: justify", len(just), "0", not just, SEV_POLISH, just)

    # табличные цифры в числовых колонках
    num_cells = [r for r in rows if r["tag"] == "td" and re.fullmatch(r"[\d\s.,+\-%₽$€]+", (r["txt"] or "x"))]
    no_tnum = [r["sel"] for r in num_cells if "tabular-nums" not in (r["fvn"] or "")]
    rep.add("H12", "Типографика", "tabular-nums в числовых ячейках таблиц",
            f"{len(num_cells) - len(no_tnum)} из {len(num_cells)}", "все",
            not no_tnum if num_cells else True, SEV_SERIOUS, no_tnum[:6])

    # русская типографика по видимому тексту
    page_text = meta.get("text", "")
    en_nums = EN_NUMBER_RE.findall(page_text)
    rep.add("H13", "Типографика", "Английский формат разрядов (1,234) в русском тексте",
            len(en_nums), "0", not en_nums, SEV_POLISH, en_nums[:6])
    glued = PERCENT_GLUED_RE.findall(page_text)
    rep.add("H14", "Типографика", "Знак % слитно с числом", len(glued), "0", not glued,
            SEV_POLISH, glued[:6])
    straight = re.findall(r'"[А-Яа-яЁё][^"]{0,40}"', page_text)
    rep.add("H15", "Типографика", "Программистские кавычки в русском тексте", len(straight), "0",
            not straight, SEV_POLISH, straight[:4])

    # ---------------------------------------------------------------- I. Цвет и контраст
    fails, warns, disabled_bad = [], [], []
    for r in text_rows:
        if not r["col"] or not r["fs"]:
            continue
        if r.get("dis"):
            lc = abs(apca(r["col"] if r["cola"] >= 0.999 else composite(r["col"], r["cola"], r["bg"]), r["bg"]))
            if not (30 <= lc <= 60):
                disabled_bad.append(f"{r['sel']} Lc {lc:.1f} «{r['txt'][:20]}»")
            continue
        fg = r["col"] if r["cola"] >= 0.999 else composite(r["col"], r["cola"], r["bg"])
        ratio = wcag(fg, r["bg"])
        large = r["fs"] >= 24 or (r["fs"] >= 18.66 and (r["fw"] or 400) >= 700)
        need = preset["large_text_contrast_min"] if large else preset["text_contrast_min"]
        if ratio < need - 0.005:
            item = f"{r['sel']} {fg} на {r['bg']} = {ratio:.2f} (нужно {need}) «{r['txt'][:24]}»"
            (warns if (r["bggrad"] or r["bgguess"]) else fails).append(item)
    rep.add("I1", "Цвет", f"Контраст текста ≥ {preset['text_contrast_min']}:1 "
            f"(крупный ≥ {preset['large_text_contrast_min']}:1)", len(fails), "0",
            not fails, SEV_BLOCKER, fails)
    rep.add("I1c", "Цвет", "Отключённые элементы в коридоре APCA Lc 30–60 "
            "(WCAG 1.4.3 их не нормирует, но невидимая кнопка — тоже дефект)",
            len(disabled_bad), "0", not disabled_bad, SEV_POLISH, disabled_bad)
    if warns:
        rep.add("I1b", "Цвет", "Текст на градиенте или на полупрозрачной подложке (значение недостоверно)",
                len(warns), "проверить глазами", None, SEV_SERIOUS, warns)

    # граница контрола к своему фону
    border_min = preset["border_contrast_min"] if opts.strict_border else preset["border_contrast_practice"]
    bad_border = []
    for r in rows:
        if r["tag"] not in ("input", "select", "textarea") or not r["bcol"] or not r["bw"]:
            continue
        parent = by_i.get(r["par"])
        around = parent["bg"] if parent else r["bg"]
        ratio = wcag(r["bcol"], around)
        if ratio < border_min - 0.005:
            bad_border.append(f"{r['sel']} {r['bcol']} на {around} = {ratio:.2f}")
    rep.add("I2", "Цвет", f"Контраст границы поля ввода ≥ {border_min}:1 "
            f"({'WCAG 1.4.11' if opts.strict_border else 'режим практики'})",
            len(bad_border), "0", not bad_border, SEV_SERIOUS, bad_border)

    tcolors = sorted({r["col"] for r in text_rows if r["col"]})
    bgcolors = sorted({r["bg"] for r in rows})
    bcolors = sorted({r["bcol"] for r in rows if r["bcol"] and r["bw"]})
    rep.add("I3", "Цвет", "Уникальных цветов текста", len(tcolors),
            f"≤ {preset['unique_text_colors_max']}", len(tcolors) <= preset["unique_text_colors_max"],
            SEV_POLISH, [", ".join(tcolors[:12])])
    rep.add("I4", "Цвет", "Уникальных цветов фона", len(bgcolors),
            f"≤ {preset['unique_bg_colors_max']}", len(bgcolors) <= preset["unique_bg_colors_max"],
            SEV_POLISH, [", ".join(bgcolors[:12])])
    rep.add("I5", "Цвет", "Уникальных цветов границ", len(bcolors),
            f"≤ {preset['unique_border_colors_max']}", len(bcolors) <= preset["unique_border_colors_max"],
            SEV_POLISH, [", ".join(bcolors[:12])])

    if opts.tokens_set:
        allowed = set(opts.tokens_set["colors"])
        composited = {r["bg"] for r in rows if r["bgguess"]}   # результат наложения альфы, а не токен
        stray = sorted({c for c in tcolors + bgcolors + bcolors
                        if c and c.lower() not in allowed and c not in composited})
        rep.add("I6", "Цвет", "Цвета, которых нет в наборе токенов", len(stray), "0", not stray,
                SEV_SERIOUS, [", ".join(stray[:12])],
                note="полупрозрачные слои (скрим, границы через альфу) исключены: их результат "
                     "вычисляется, а не хранится в наборе")

    # нейтрали: одно семейство
    # статусные подложки (#dcfce7, #ffe2e2) тоже низкохроматичны, поэтому семейство нейтрали
    # считается только по цветам текста и границ: там статусные оттенки насыщеннее порога
    neutrals = [c for c in tcolors + bcolors if c]
    hues, chromas = [], []
    for c in neutrals:
        try:
            L, C, H = hex2oklch(c)
        except Exception:
            continue
        if C <= 0.05 and 0.02 < L < 0.99:
            hues.append(H); chromas.append(C)
    spread = (max(hues) - min(hues)) if len(hues) > 1 else 0
    tinted = [h for h, c in zip(hues, chromas) if c > 0.002]
    spread_t = (max(tinted) - min(tinted)) if len(tinted) > 1 else 0
    rep.add("I7", "Цвет", "Нейтраль одного семейства (разброс оттенка тонированных серых)",
            f"{spread_t:.0f}°", "≤ 40°", spread_t <= 40, SEV_POLISH,
            [f"хрома до {max(chromas):.3f}" if chromas else ""])

    if dark:
        bgl = okl(meta_bg_hex(meta, rows))
        rep.add("I8", "Цвет", "Фон тёмной темы в коридоре OKLCH L 13–22 %",
                f"{bgl*100:.1f} %" if bgl else "?", "13–22 %",
                bool(bgl and 0.13 <= bgl <= 0.22), SEV_SERIOUS)
        pure_white = [r["sel"] for r in text_rows if r["col"] and r["col"].lower() == "#ffffff" and (r["fs"] or 0) >= 20]
        rep.add("I9", "Цвет", "Чистый белый текст крупным кеглем в тёмной теме", len(pure_white),
                "0", not pure_white, SEV_POLISH, pure_white[:5])

    # ---------------------------------------------------------------- J. Раскладка
    forms = [r for r in rows if r["tag"] == "form" or
             (len([k for k in rows if k["par"] == r["i"] and k["tag"] in ("input", "select", "textarea")]) >= 3)]
    wide_forms = [f"{r['sel']} {r['w']}px" for r in forms if r["w"] > preset["form_max_width"]]
    rep.add("J1", "Раскладка", f"Формы не шире {preset['form_max_width']} px", len(wide_forms), "0",
            not wide_forms, SEV_SERIOUS, wide_forms)

    sidebars = [r for r in rows if r["x"] < 8 and r["h"] > meta["innerH"] * 0.45
                and 120 < r["w"] < 480]
    sidebars.sort(key=lambda r: -r["h"])
    sw_ = round(sidebars[0]["w"]) if sidebars else None
    rep.add("J2", "Раскладка", f"Сайдбар в коридоре {preset['sidebar_min']}–{preset['sidebar_max']} px",
            sw_ if sw_ else "не найден", f"{preset['sidebar_min']}–{preset['sidebar_max']}",
            True if sw_ is None else (preset["sidebar_min"] <= sw_ <= preset["sidebar_max"]),
            SEV_SERIOUS, [sidebars[0]["sel"]] if sidebars else [])

    mains = [r for r in rows if r["tag"] == "main" or r["role"] == "main"]
    mw_ = round(mains[0]["w"]) if mains else None
    rep.add("J3", "Раскладка", f"Контентной области остаётся ≥ {preset['content_min']} px",
            mw_ if mw_ else "main не найден", f"≥ {preset['content_min']}",
            True if mw_ is None else mw_ >= preset["content_min"], SEV_SERIOUS)

    sticky = [r for r in rows if r["pos"] in ("sticky", "fixed")
              and r["y"] < meta["innerH"] * 0.5 and r["w"] > meta["innerW"] * 0.4
              and r["h"] <= meta["innerH"] * 0.25]
    ssum = round(sum(r["h"] for r in sticky))
    rep.add("J4", "Раскладка", f"Сумма прилипших полос ≤ {preset['sticky_sum_max']} px", ssum,
            f"≤ {preset['sticky_sum_max']}", ssum <= preset["sticky_sum_max"], SEV_POLISH,
            [f"{r['sel']} {round(r['h'])}px" for r in sticky])

    hscroll = meta["scrollW"] > meta["innerW"] + 1
    rep.add("J5", "Раскладка", "Нет горизонтальной прокрутки документа",
            f"{meta['scrollW']} vs {meta['innerW']}", "scrollWidth ≤ innerWidth", not hscroll,
            SEV_BLOCKER)

    rigid = []
    for r in rows:
        g = r["gtc"]
        if not g:
            continue
        tracks = g.split()
        if len(tracks) >= 3 and len(set(tracks)) == 1 and "minmax" not in g:
            rigid.append(f"{r['sel']}: {g[:50]}")
    rep.add("J6", "Раскладка", "Сетки с жёстко заданным числом равных колонок", len(rigid), "≤ 2",
            len(rigid) <= 2, SEV_POLISH, rigid)

    centered = []
    if sidebars and mains:
        m = mains[0]
        if abs(m["ml"] or 0) > 24 and abs((m["ml"] or 0) - (m["mr"] or 0)) < 2:
            centered.append(m["sel"])
    rep.add("J7", "Раскладка", "Контент не центрирован при наличии сайдбара", len(centered), "0",
            not centered, SEV_POLISH, centered)

    headers = [r for r in rows if r["tag"] == "header" and r["w"] > meta["innerW"] * 0.4]
    tall = [f"{r['sel']} {round(r['h'])}px" for r in headers if r["h"] > preset["page_header_max"]]
    rep.add("J8", "Раскладка", f"Шапка страницы не выше {preset['page_header_max']} px", len(tall),
            "0", not tall, SEV_POLISH, tall)

    # ---------------------------------------------------------------- K. Движение
    all_props = [r["tp"] for r in rows if r["tp"] and r["tp"] != "all 0s ease 0s"]
    trans_all = [r["sel"] for r in rows if r["tp"] and "all" in r["tp"].split(",")[0]
                 and parse_durations(r["td"]) and max(parse_durations(r["td"])) > 0]
    rep.add("K1", "Движение", "transition: all", len(trans_all), "0", not trans_all, SEV_POLISH,
            trans_all[:6])

    durs = []
    for r in rows:
        durs.extend([d for d in parse_durations(r["td"]) if d > 0])
    uniq_d = sorted(set(durs))
    off_d = [d for d in uniq_d if not in_scale(d, preset["durations"], tol=1)]
    rep.add("K2", "Движение", "Длительности вне шкалы", len(off_d), "0", not off_d, SEV_POLISH,
            [", ".join(f"{d:.0f}ms" for d in off_d)])
    share300 = (len([d for d in durs if abs(d - 300) < 1]) / len(durs)) if durs else 0
    rep.add("K3", "Движение", "Доля длительностей 300 ms", f"{share300*100:.1f} %",
            f"≤ {preset['duration_300_share_max']*100:.0f} %",
            share300 <= preset["duration_300_share_max"], SEV_POLISH)

    # ---------------------------------------------------------------- L. Антислоп
    emoji = EMOJI_RE.findall(page_text)
    rep.add("L1", "Антислоп", "Эмодзи в интерфейсе", len(emoji), "0", not emoji, SEV_SERIOUS,
            ["".join(dict.fromkeys(emoji))[:20]] if emoji else [])

    # «почти, но не совсем»: пары близких, но не равных значений
    def almost(vals, scale, lo=1, hi=3):
        """Пара близких значений считается дефектом, только если хотя бы одно из них вне шкалы:
        соседние ступени объявленной шкалы (11 и 12, 6 и 8) — это решение, а не «почти, но не совсем»."""
        vals = sorted(set(round(v, 1) for v in vals))
        out = []
        for a, b in zip(vals, vals[1:]):
            if lo <= b - a <= hi and not (in_scale(a, scale) and in_scale(b, scale)):
                out.append(f"{a} / {b}")
        return out
    almost_fs = almost(fss, preset["font_sizes"])
    almost_r = almost([v for v in uniq_r if v < 900], preset["radius"])
    almost_h = almost([float(h) for h in heights], preset["heights"])
    almost_all = almost_fs + almost_r + almost_h
    rep.add("L2", "Антислоп", "«Почти, но не совсем»: пары величин с разницей 1–3 px",
            len(almost_all), "0", not almost_all, SEV_POLISH,
            [f"кегли: {', '.join(almost_fs)}" if almost_fs else "",
             f"радиусы: {', '.join(almost_r)}" if almost_r else "",
             f"высоты: {', '.join(almost_h)}" if almost_h else ""])

    inline_hex = [f"{r['sel']}: {r['inline'][:50]}" for r in rows
                  if r["inline"] and re.search(r"#[0-9a-fA-F]{3,8}|rgba?\(", r["inline"])]
    rep.add("L3", "Антислоп", "Литералы цвета в inline-стилях", len(inline_hex), "0",
            not inline_hex, SEV_POLISH, inline_hex[:6])

    grads = [r["sel"] for r in rows if r["bggrad"] and r["w"] > 80 and r["h"] > 40]
    rep.add("L4", "Антислоп", "Крупные градиентные заливки", len(grads), "информативно", None,
            SEV_POLISH, grads[:6],
            note="фиолетово-синий градиент — главный цветовой маркер генерации, см. 01-color/06 §4.2")

    fams = sorted({r["ff"] for r in text_rows if r["ff"]})
    rep.add("L5", "Антислоп", "Гарнитур в интерфейсе", len(fams), "≤ 2 (текстовая + моно)",
            len(fams) <= 2, SEV_POLISH, [", ".join(fams)])

    return rep


def meta_bg_hex(meta, rows):
    m = re.match(r"rgba?\(([^)]+)\)", meta.get("bodyBg", "") or "")
    if m:
        p = [float(x) for x in re.split(r"[,\s/]+", m.group(1)) if x]
        if len(p) >= 3:
            return "#%02x%02x%02x" % tuple(int(round(v)) for v in p[:3])
    return rows[0]["bg"] if rows else "#ffffff"


# =====================================================================================
# 6. Динамические прогоны: hover, Tab, reduced motion
# =====================================================================================

def check_focus(page, rep, preset, n_tabs):
    rest = page.evaluate(FOCUS_REST_JS)
    if not rest:
        rep.add("G2", "Фокус", "Фокусируемых элементов на странице", 0, "> 0", None, SEV_POLISH)
        return
    seen, no_ring, thin, clipped, low = [], [], [], [], []
    page.evaluate("() => { document.body.focus && document.body.focus(); }")
    for _ in range(n_tabs):
        page.keyboard.press("Tab")
        cur = page.evaluate(FOCUS_NOW_JS)
        if not cur or cur["n"] is None:
            continue
        key = cur["n"]
        if key in seen:
            continue
        seen.append(key)
        base = rest.get(key) or rest.get(str(key)) or {}
        ow = float((cur["ow"] or "0px").replace("px", "") or 0)
        changed = (cur["ost"] != "none" and ow > 0) or (cur["sh"] != base.get("sh")) \
            or (cur["bc"] != base.get("bc")) or (cur["bg"] != base.get("bg"))
        label = f"{cur['tag']} «{cur['txt'][:24]}»"
        if not changed:
            no_ring.append(label)
        elif cur["ost"] != "none" and 0 < ow < preset["focus_width_min"]:
            thin.append(f"{label}: outline {ow}px")
        if changed and cur["clipped"]:
            clipped.append(label)
        if cur["ost"] != "none" and ow > 0 and cur["oc"]:
            ring, _ = _to_hex(cur["oc"])
            offset = float((cur.get("oo") or "0px").replace("px", "") or 0)
            # кольцо с положительным offset лежит на фоне вокруг элемента, с отрицательным — на самом элементе
            surface_css = cur.get("around") if offset > 0.5 else cur["bg"]
            surface, alpha = _to_hex(surface_css)
            if ring and surface and alpha > 0.9:
                ratio = wcag(ring, surface)
                if ratio < 2.995:
                    where = "фону вокруг" if offset > 0.5 else "элементу"
                    low.append(f"{label}: кольцо {ring} к {where} {surface} = {ratio:.2f}")
    rep.add("G2", "Фокус", f"Видимый индикатор фокуса при обходе Tab ({len(seen)} остановок)",
            len(no_ring), "0", not no_ring, SEV_BLOCKER, no_ring)
    rep.add("G3", "Фокус", f"Толщина индикатора ≥ {preset['focus_width_min']} px", len(thin), "0",
            not thin, SEV_SERIOUS, thin)
    rep.add("G4", "Фокус", "Индикатор не обрезан предком с overflow", len(clipped), "0",
            not clipped, SEV_SERIOUS, clipped)
    rep.add("G5", "Фокус", "Контраст кольца фокуса к элементу ≥ 3:1", len(low), "0", not low,
            SEV_SERIOUS, low)


HOVER_READ_JS = r"""
(i) => {
  const el = document.querySelector('[data-uia="' + i + '"]');
  if (!el) return null;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const top = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height / 2, 12));
  return { bg: cs.backgroundColor, col: cs.color, bc: cs.borderTopColor,
           sh: cs.boxShadow, tr: cs.transform, cur: cs.cursor,
           ol: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor,
           hit: !!(top && (top === el || el.contains(top) || top.contains(el))) };
}
"""


def _to_hex(css):
    m = re.match(r"rgba?\(([^)]+)\)", css or "")
    if not m:
        return None, 1.0
    p = [float(x) for x in re.split(r"[,\s/]+", m.group(1)) if x]
    if len(p) < 3:
        return None, 1.0
    a = p[3] if len(p) > 3 else 1.0
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in p[:3]), a


def check_hover(page, rep, preset, rows, limit=12, viewport_h=900):
    by_i = {r["i"]: r for r in rows}

    def in_tbody(r):
        p = by_i.get(r["par"])
        return bool(p and p["tag"] == "tbody")

    visible = lambda r: 0 <= r["y"] and r["y"] + min(r["h"], 24) < viewport_h - 8
    cands = [r for r in rows if r["inter"] and r["w"] >= 24 and r["h"] >= 20 and visible(r)]
    cands += [r for r in rows if r["tag"] == "tr" and r["h"] >= 20 and in_tbody(r) and visible(r)][:3]
    seen, picked = set(), []
    for r in cands:
        key = (r["tag"], round(r["h"]), r["col"], r["bg"])
        if key in seen:
            continue
        seen.add(key)
        picked.append(r)
        if len(picked) >= limit:
            break
    no_change, too_small, too_big, covered = [], [], [], []
    lo, hi = preset["hover_delta_L"]
    if rep.context.get("scheme") == "dark":
        hi = max(hi, 0.12)   # в тёмной теме шаг между поверхностями больше (09-design-tokens/03 §3.5)
    for r in picked:
        before = page.evaluate(HOVER_READ_JS, r["i"])
        try:
            page.mouse.move(r["x"] + r["w"] / 2, r["y"] + min(r["h"] / 2, 12))
            page.wait_for_timeout(120)
        except Exception:
            continue
        after = page.evaluate(HOVER_READ_JS, r["i"])
        if not before or not after:
            continue
        label = f"{r['sel']} «{(r['txt'] or '')[:20]}»"
        if not after.get("hit"):
            covered.append(label)     # элемент перекрыт оверлеем: hover до него не доходит
            continue
        same = all(before[k] == after[k] for k in ("bg", "col", "bc", "sh", "tr", "ol"))
        if same:
            no_change.append(label)
            continue
        b, ba = _to_hex(before["bg"]); a, aa = _to_hex(after["bg"])
        if b and a and aa > 0.05 and ba > 0.05:
            dl = abs((okl(a) or 0) - (okl(b) or 0))
            if dl and dl < lo:
                too_small.append(f"{label}: ΔL {dl*100:.1f} п.п.")
            elif dl > hi:
                too_big.append(f"{label}: ΔL {dl*100:.1f} п.п.")
        if after["tr"] and after["tr"] != "none" and "matrix" in after["tr"]:
            nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", after["tr"])]
            if nums and abs(nums[0] - 1) > 0.005:
                too_big.append(f"{label}: hover меняет масштаб ({nums[0]:.3f})")
    page.mouse.move(0, 0)
    rep.add("S1", "Состояния", f"У интерактивных элементов есть hover (проверено {len(picked) - len(covered)})",
            len(no_change), "0", not no_change, SEV_SERIOUS, no_change)
    if covered:
        rep.add("S3", "Состояния", "Элементы под оверлеем (hover не проверялся)", len(covered),
                "информативно", None, SEV_POLISH, covered)
    rep.add("S2", "Состояния", f"ΔL hover в коридоре {lo*100:.0f}–{hi*100:.0f} п.п. светлоты",
            len(too_small) + len(too_big), "0", not (too_small or too_big), SEV_POLISH,
            too_small + too_big)


def check_reduced(page_rows_normal, page_rows_reduced, rep):
    def sig(rows):
        d = []
        for r in rows:
            d.extend([x for x in parse_durations(r["td"]) if x > 0])
        anims = {r["an"] for r in rows if r["an"] and r["an"] != "none"}
        transforms = {r["sel"] for r in rows if r.get("tp") and "transform" in r["tp"]}
        return d, anims, transforms
    d0, a0, t0 = sig(page_rows_normal)
    d1, a1, t1 = sig(page_rows_reduced)
    max0 = max(d0) if d0 else 0
    max1 = max(d1) if d1 else 0
    rep.add("M1", "Сокращённое движение", "Длительности сокращаются при prefers-reduced-motion",
            f"{max0:.0f} ms → {max1:.0f} ms", "меньше или равно, и не 0",
            (max1 <= max0) and not (max0 > 0 and max1 == 0), SEV_SERIOUS,
            note="«reduce, not remove»: обнуление ломает компоненты, ждущие transitionend")
    still = sorted(a1 - {"none"})
    rep.add("M2", "Сокращённое движение", "Циклические анимации выключены", len(still),
            "0 (кроме спиннера, если он единственный сигнал загрузки)", not still, SEV_POLISH,
            [", ".join(still[:6])])


# =====================================================================================
# 7. Отчёт
# =====================================================================================

GROUP_ORDER = ["Отступы", "Размеры", "Форма", "Глубина", "Слои", "Цели", "Фокус", "Типографика",
               "Цвет", "Раскладка", "Движение", "Сокращённое движение", "Состояния", "Антислоп"]


def merge_reports(reports):
    out = []
    for rep in reports:
        tag = f"{rep.context.get('scheme','light')}/{rep.context.get('viewport','')}"
        for f in rep.findings:
            g = dict(f)
            g["run"] = tag
            out.append(g)
    return out


def render_md(target, preset, findings, runs):
    fails = [f for f in findings if f["verdict"] == "FAIL"]
    by_sev = Counter(f["severity"] for f in fails)
    lines = []
    lines.append(f"# Визуальный QA: {os.path.basename(target)}")
    lines.append("")
    lines.append(f"Инструмент: `99-raw/tools/ui_audit.py`. Пресет: **{preset['name']}** ({preset['title']}).")
    lines.append(f"Прогоны: {', '.join(runs)}.")
    lines.append("")
    total = len(findings)
    okc = len([f for f in findings if f["verdict"] == "OK"])
    warnc = len([f for f in findings if f["verdict"] == "WARN"])
    lines.append(f"**Итог: {okc} OK, {len(fails)} FAIL, {warnc} информативных из {total} проверок.** "
                 f"Блокеров {by_sev.get(SEV_BLOCKER,0)}, серьёзных {by_sev.get(SEV_SERIOUS,0)}, "
                 f"полировки {by_sev.get(SEV_POLISH,0)}.")
    lines.append("")
    groups = defaultdict(list)
    for f in findings:
        groups[f["group"]].append(f)
    for g in GROUP_ORDER:
        if g not in groups:
            continue
        lines.append(f"## {g}")
        lines.append("")
        lines.append("| # | Правило | Найдено | Порог | Вердикт | Серьёзность | Прогон |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in groups[g]:
            lines.append(f"| {f['id']} | {f['rule']} | {f['found']} | {f['threshold']} | "
                         f"{f['verdict']} | {f['severity']} | {f['run']} |")
        lines.append("")
        det = [f for f in groups[g] if f["examples"] and any(f["examples"]) and f["verdict"] != "OK"]
        if det:
            for f in det:
                ex = [e for e in f["examples"] if e]
                if not ex:
                    continue
                lines.append(f"- **{f['id']}** {f['rule']} ({f['run']}):")
                for e in ex:
                    lines.append(f"  - `{e}`")
                if f["note"]:
                    lines.append(f"  - примечание: {f['note']}")
            lines.append("")
    if fails:
        lines.append("## Что править в первую очередь")
        lines.append("")
        for sev in (SEV_BLOCKER, SEV_SERIOUS, SEV_POLISH):
            part = [f for f in fails if f["severity"] == sev]
            if not part:
                continue
            lines.append(f"**{sev}:**")
            for f in part:
                lines.append(f"- {f['id']} — {f['rule']}: найдено {f['found']}, порог {f['threshold']} ({f['run']}).")
            lines.append("")
    return "\n".join(lines)


# =====================================================================================
# 8. Прогон
# =====================================================================================

def to_url(target):
    if re.match(r"^https?://", target) or target.startswith("file://"):
        return target
    return "file://" + os.path.abspath(target)


def audit(target, opts):
    from playwright.sync_api import sync_playwright

    preset = PRESETS[opts.preset]
    if opts.tokens_set:
        ts = opts.tokens_set
        if ts["spacing"]:
            preset = dict(preset)
            preset["spacing"] = sorted(set(ts["spacing"]) | {0})
        if ts["radius"]:
            preset["radius"] = sorted(set(ts["radius"]))
        if ts["font_sizes"]:
            preset["font_sizes"] = sorted(set(ts["font_sizes"]))
        if ts["zindex"]:
            preset["zindex"] = sorted(set(ts["zindex"]) | {0})
        if ts["durations"]:
            preset["durations"] = sorted(set(ts["durations"]) | {0})
        if ts["sizes"]:
            heights = [v for v in ts["sizes"] if 20 <= v <= 64]
            if heights:
                preset["heights"] = sorted(set(heights))

    url = to_url(target)
    reports, runs, normal_rows, reduced_rows = [], [], None, None

    with sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
        combos = []
        for vp in opts.viewports:
            for scheme in (["light", "dark"] if opts.scheme == "both" else [opts.scheme]):
                combos.append((vp, scheme, "no-preference", False))
        if opts.reduced_motion:
            combos.append((opts.viewports[0], opts.scheme if opts.scheme != "both" else "light",
                           "reduce", False))
        if opts.touch:
            combos.append(((390, 844), opts.scheme if opts.scheme != "both" else "light",
                           "no-preference", True))

        for (w, h), scheme, motion, touch in combos:
            ctx_kwargs = dict(viewport={"width": w, "height": h}, color_scheme=scheme,
                              reduced_motion=motion, device_scale_factor=2 if touch else 1,
                              has_touch=touch, is_mobile=touch)
            context = browser.new_context(**ctx_kwargs)
            page = context.new_page()
            page.goto(url, wait_until="load", timeout=opts.timeout)
            page.wait_for_timeout(opts.wait)
            data = page.evaluate(COLLECT_JS, {"maxElements": opts.max_elements})
            tag = f"{scheme}/{w}x{h}" + ("/reduced" if motion == "reduce" else "") + ("/touch" if touch else "")
            ctx = {"target": target, "scheme": scheme, "viewport": f"{w}x{h}",
                   "motion": motion, "touch": touch,
                   "target_min": 44 if touch else preset["target_min"]}
            if motion == "reduce":
                reduced_rows = data["rows"]
            elif normal_rows is None and scheme == "light":
                normal_rows = data["rows"]
            rep = run_checks(data, preset, opts, ctx)
            rep.context["viewport"] = f"{w}x{h}" + ("/reduced" if motion == "reduce" else "") + ("/touch" if touch else "")
            if opts.tab and not touch and motion != "reduce":
                check_focus(page, rep, preset, opts.tab)
            if opts.hover and not touch and motion != "reduce":
                check_hover(page, rep, preset, data["rows"], viewport_h=h)
            reports.append(rep)
            runs.append(tag)
            if opts.screenshot:
                os.makedirs(opts.out, exist_ok=True)
                page.screenshot(path=os.path.join(
                    opts.out, f"{opts.name}_{scheme}_{w}x{h}.png"), full_page=True)
            context.close()
        browser.close()

    if normal_rows and reduced_rows:
        extra = Report(target, preset["name"], {"scheme": "light", "viewport": "reduced"})
        check_reduced(normal_rows, reduced_rows, extra)
        reports.append(extra)

    findings = merge_reports(reports)
    md = render_md(target, preset, findings, runs)
    os.makedirs(opts.out, exist_ok=True)
    md_path = os.path.join(opts.out, opts.name + ".md")
    js_path = os.path.join(opts.out, opts.name + ".json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(js_path, "w", encoding="utf-8") as f:
        json.dump({"target": target, "preset": preset["name"], "runs": runs, "findings": findings},
                  f, ensure_ascii=False, indent=1)
    return md, md_path, js_path, findings


# =====================================================================================
# 9. Самопроверка без браузера
# =====================================================================================

def selftest():
    ok = True

    def check(name, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'OK  ' if good else 'FAIL'} {name}: {got!r} (ожидалось {want!r})")

    check("parse_shadows: два слоя",
          len(parse_shadows("rgba(0,0,0,.06) 0px 1px 2px 0px, rgba(0,0,0,.08) 0px 4px 8px -2px")), 2)
    check("parse_shadows: inset", parse_shadows("inset 0 0 0 1px rgb(0 0 0 / .06)")[0][4], True)
    check("parse_shadows: свечение", parse_shadows("rgb(37 99 235) 0px 0px 20px 0px")[0][:3], (0.0, 0.0, 20.0))
    check("parse_durations", parse_durations("150ms, 0.3s"), [150.0, 300.0])
    check("in_scale 12 в шкале", in_scale(12, [0, 4, 8, 12, 16]), True)
    check("in_scale 13 вне шкалы", in_scale(13, [0, 4, 8, 12, 16]), False)
    check("is_fraction 19.6", is_fraction(19.6), True)
    check("is_fraction 20", is_fraction(20.0), False)
    check("gap_between соседей",
          round(gap_between({"x": 0, "y": 0, "w": 10, "h": 10}, {"x": 12, "y": 0, "w": 10, "h": 10}), 1), 2.0)
    check("wcag #767676 на белом", round(wcag("#767676", "#ffffff"), 2), 4.54)
    check("apca #fff на #000", round(apca("#ffffff", "#000000"), 1), -107.9)
    check("EMOJI_RE находит", bool(EMOJI_RE.search("Готово ✅")), True)
    check("EN_NUMBER_RE находит", bool(EN_NUMBER_RE.search("1,234")), True)
    check("PERCENT_GLUED_RE находит", bool(PERCENT_GLUED_RE.search("12%")), True)
    print("\nпресеты:", ", ".join(PRESETS))
    print("групп проверок:", len(GROUP_ORDER))
    return 0 if ok else 1


# =====================================================================================
# 10. CLI
# =====================================================================================

def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("target", nargs="?")
    p.add_argument("--preset", default="admin", choices=list(PRESETS))
    p.add_argument("--tokens")
    p.add_argument("--viewport", action="append", default=[])
    p.add_argument("--scheme", default="light", choices=["light", "dark", "both"])
    p.add_argument("--reduced-motion", action="store_true")
    p.add_argument("--hover", action="store_true")
    p.add_argument("--tab", type=int, default=0)
    p.add_argument("--touch", action="store_true")
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--name")
    p.add_argument("--strict-border", action="store_true")
    p.add_argument("--max-elements", type=int, default=4000)
    p.add_argument("--wait", type=int, default=None)
    p.add_argument("--timeout", type=int, default=45000)
    p.add_argument("--screenshot", action="store_true")
    p.add_argument("--batch")
    p.add_argument("--fail-on", default=None, choices=["blocker", "serious", "any"])
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    a = p.parse_args()

    if a.help or (not a.target and not a.batch and not a.selftest):
        print(__doc__)
        return 0
    if a.selftest:
        return selftest()

    a.viewports = []
    for v in a.viewport or ["1440x900"]:
        w, h = v.lower().split("x")
        a.viewports.append((int(w), int(h)))
    a.tokens_set = load_dtcg(a.tokens) if a.tokens else None
    if a.wait is None:
        a.wait = 2000 if (a.target and re.match(r"^https?://", a.target)) else 400

    targets = []
    if a.batch:
        with open(a.batch, encoding="utf-8") as f:
            targets = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    else:
        targets = [a.target]

    worst = None
    for t in targets:
        a.name = a.name if (a.name and len(targets) == 1) else \
            re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(t) or t)[:60]
        md, md_path, js_path, findings = audit(t, a)
        if not a.quiet:
            print(md)
        print(f"\n→ {md_path}\n→ {js_path}", file=sys.stderr)
        fails = [f for f in findings if f["verdict"] == "FAIL"]
        if fails:
            sev = min(SEV_ORDER[f["severity"]] for f in fails)
            worst = sev if worst is None else min(worst, sev)

    if a.fail_on and worst is not None:
        limit = {"blocker": 0, "serious": 1, "any": 2}[a.fail_on]
        if worst <= limit:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
