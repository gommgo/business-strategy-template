#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""marketing_audit.py — профиль визуальных проверок `marketing` поверх ui_audit.py (creative-research, волна 3, агент K).

Зачем. ui_audit.py (ui-research; пресеты только admin и consumer) на лендинге даёт ложные «серьёзно»: display-кегли 48–160
(H1/H2), отступы секций 64–160 (A1), hero-CTA 52–64 (B1/B2), свечение CTA (D4), слои эффектов с z-index вне шкалы (E1/E2),
колонка-картинка во всю высоту как «сайдбар» (J2) — UI-report §4.3, PLAN «Поправки». Файл ui_audit.py не меняется: обёртка
импортирует его функции (COLLECT_JS, run_checks, check_focus, check_hover, check_reduced), ОДИН раз собирает computed styles
на прогон и считает на тех же данных два набора порогов:
  * consumer — как есть (для сравнения и доли ложных срабатываний);
  * marketing — пресет PRESET_MARKETING + таблица PROFILE (перенастройка, пересчёт по узлам, смена серьёзности,
    отключение в «информативно») + свои проверки MKT-* (clamp ≤ 2,5, строки H1, трекинг и интерлиньяж кириллического display,
    висячие предлоги, хроматические цвета по уровню, появление «на каждой секции», анимация свойств раскладки, linear у
    перемещений, петли без паузы, горизонтальная прокрутка на 360) + приметы реестра клише `cliche:<id>` (H, v0.1).
Таблица профиля — `--profile-md` и 09-ai-execution-evaluation/03-verification-loop-and-gates.md §4.

Использование:
  python3 99-raw/tools/marketing_audit.py URL|ФАЙЛ.html [--level L0|L1|L2] [--out DIR] [--name ИМЯ]
          [--viewport 1440x900 ...] [--no-mobile] [--no-reduced] [--tab 20] [--hover] [--allow cliche:a,cliche:b]
          [--fail-on blocker|serious|any] [--wait МС] [--no-lock] [--quiet]
  python3 99-raw/tools/marketing_audit.py --batch список.tsv [ключи]    # строка: URL|файл<TAB>уровень<TAB>имя (2–3 поля — по желанию)
  python3 99-raw/tools/marketing_audit.py --selftest                   # без браузера: пресет, профиль, парсеры, синтетика
  python3 99-raw/tools/marketing_audit.py --profile-md                 # таблица PROFILE в Markdown

Выход (DIR, по умолчанию 99-raw/cache/audit): <имя>.marketing.md (сводка, группы, «consumer → marketing», что править),
<имя>.marketing.json (все находки обоих наборов, сравнение, сырьё MKT), <имя>.fix.txt (блок «правило → найдено → порог → где»
для промта правки, ui 12/04 §3.6). Код выхода: 0; 1 — есть нарушения уровня --fail-on; 2 — ошибка запуска.

Прогоны по умолчанию: 1440×900 (светлая схема), 390×844 тач (DPR 2, цели 24 px по WCAG 2.5.8 — не 44), тот же десктоп с
prefers-reduced-motion: reduce, быстрый замер ширины документа на 360×780. Браузер — Chromium Playwright; утилита сама берёт
две блокировки (общая тройки, затем наша; блокирующий flock ≤ 900 с) на один адрес и ждёт MemAvailable ≥ 3 ГБ; --no-lock —
только если блокировки уже держит вызывающий. Локальный файл раздаётся встроенным HTTP-сервером (CSSOM у file:// закрыт).

Ограничения: движение по времени (пауза на 6-й секунде, вспышки, reduce всей страницы, петли под текстом, LCP) здесь НЕ
проверяется — это motion_check.py; контраст на медиа по F83 — page_accept.py (ai-media); стили кросс-доменных CSS не
читаются (clamp в них не виден — счётчик sheetsBlocked); приметы клише — сигнал «нужно решение art-direction», а не дефект.
"""
from __future__ import annotations

import argparse
import fcntl
import functools
import http.server
import io
import json
import math
import os
import re
import signal
import socketserver
import sys
import threading
import time
from collections import Counter, defaultdict
from types import SimpleNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("creative"))
DEFAULT_OUT = str(kbpaths.out("creative", "audit"))
FONTS_YAML = os.path.join(ROOT, "04-visual-language", "cyrillic-display-fonts.yaml")
LOCKS = [kbpaths.lock_path("browser"), kbpaths.lock_path("browser", "creative")]
VERSION = "marketing_audit.py 0.1.1 (2026-09-25; S1: MKT-M2 — block-size/inline-size и исключение аккордеона <details>, X-11)"

kbpaths.use("ui")  # перенос: ui_audit.py — scripts/ui, color.py — scripts/lib
import ui_audit as U  # noqa: E402  (ui-research, копия kimi; файл не меняется)
from color import hex2oklch  # noqa: E402

SEV_B, SEV_S, SEV_D = U.SEV_BLOCKER, U.SEV_SERIOUS, U.SEV_POLISH
BSD = {SEV_B: "B", SEV_S: "S", SEV_D: "D"}

# =====================================================================================================================
# 1. Пресет marketing: только значения, которые run_checks читает из пресета
# =====================================================================================================================
PRESET_MARKETING = dict(U.PRESET_CONSUMER)
PRESET_MARKETING.update({
    "name": "marketing",
    "title": "маркетинговая страница: лендинг, промо, главная (creative-research 09/03 §4)",
    # компонентная шкала отступов + «этажи» секций 64–160 (D: marketing-tokens space.section-s/m/l = 64/112/160)
    "spacing": [0, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 56, 64, 72, 80, 96, 112, 120, 128, 144, 160, 192, 200, 240],
    "radius": [0, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 40, 48, 9999],  # D: media 16, card 24, pill 9999
    "heights": [24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64],                  # D: cta-hero-height 56; hero-CTA 52–64
    "unique_heights_max": 5,
    "font_sizes": [12, 13, 14, 15, 16, 17, 18, 20, 22, 24],                   # текстовые роли; display > 24 — отдельно
    "unique_font_sizes_max": 10,
    "unique_radius_max": 8,
    "glass_max": 6,                        # бюджет производительности, а не стиль (PLAN «Поправки»: стекло ≤ 2 — у приложений)
    "shadow_share_max": 0.40,
    "unique_text_colors_max": 10,
    "unique_bg_colors_max": 14,            # ритм фонов секций
    "page_header_max": 140,
    "para_max_width": 760,                 # D: measure-lead 748
    "zindex": [-1, 0, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100, 200, 500, 999, 1000, 1100, 1200, 1300, 1400, 1500, 9999],
    # E: motion.marketing.duration (feedback 120, hover 200, reveal 560, split 800, hero 900–1200, state 320, page 400)
    "durations": [0, 60, 80, 100, 120, 150, 160, 180, 200, 240, 250, 300, 320, 350, 400, 450, 480, 500, 560, 600, 700,
                  800, 900, 1000, 1200],
})

LEVELS = ("L0", "L1", "L2")
CHROMA_MAX = {"L0": 2, "L1": 3, "L2": 4}          # D 04/03 выжимка п.1 ([данные C] [мнение вендора])
DISPLAY_MIN_PX = 40
TEXT_MAX_PX = 24

# =====================================================================================================================
# 2. Таблица профиля: проверка ui_audit → на лендинге → новый порог или отключено → основание
#    action: keep (как есть) · retune (порог из PRESET_MARKETING) · recompute (пересчёт по узлам в apply_profile)
#            · severity (только серьёзность) · info (отключено как критерий: WARN «информативно»)
# =====================================================================================================================
PROFILE = {
    "A1": dict(action="recompute", sev=SEV_D, threshold="≥ 90 % значений ≤ 48 px из шкалы; > 48 px — ритм секций (информативно)",
               landing="секции 64–160 px и отступы на clamp() дают дробные значения вне шкалы",
               base="UI-report §4.3 (A1); PLAN «Поправки» (шкала до 96, section 24 → 64–160, D); D marketing-tokens space.section"),
    "A2": dict(action="recompute", sev=SEV_D, threshold="0 значений ≤ 48 px, кратных 5 и не кратных 4",
               landing="fluid-отступы (vw, clamp) дают 45, 75, 115 — это не «шкала десятками»",
               base="код ui_audit A2 (серьёзно); жидкие величины D 04/02"),
    "B1": dict(action="recompute", sev=SEV_D, threshold="≤ 5 уникальных высот контролов",
               landing="навигация 40, поле 44–48, hero-CTA 52–64, чипы 32",
               base="UI-report §4.3 (B1/B2); PLAN «Поправки» (роль hero-CTA 52–64, D); D cta-hero-height 56"),
    "B2": dict(action="recompute", sev=SEV_D, threshold="высоты из ряда 24…64 (шаг 4)",
               landing="hero-CTA 56 вне ряда 24–48", base="UI-report §4.3; D marketing-tokens size.cta-hero-height"),
    "C1": dict(action="retune", sev=SEV_D, threshold="≤ 8 радиусов", landing="крупные плашки, медиа 16, карточки 24, пилюли",
               base="UI-report §4.3 (C1/C2/C5); D marketing-tokens radius.*"),
    "C2": dict(action="retune", sev=SEV_D, threshold="шкала 0–48 + 9999", landing="то же", base="UI-report §4.3"),
    "C5": dict(action="info", sev=SEV_D, threshold="информативно", landing="круглые аватары, пилюли, крупные скругления плашек",
               base="UI-report §4.3 (C5); жанр лендинга"),
    "D3": dict(action="retune", sev=SEV_D, threshold="≤ 6 элементов с backdrop-filter на странице (стиль — cliche:glassmorphism-panels)",
               landing="стеклянные карточки над фото и видео", base="PLAN «Поправки» (лимит стекла — бюджет производительности); UI-report §4.3 (D3)"),
    "D4": dict(action="recompute", sev=SEV_D, threshold="≤ 2 свечений (glow-CTA и ореол); ≥ 3 цветных — cliche:neon-glow",
               landing="glow-CTA и ореолы допустимы по концепции", base="PLAN «Поправки» (свечение «серьёзно» у ui 13/01 Г5, D4); реестр H neon-glow (≥ 3 — D)"),
    "D5": dict(action="retune", sev=SEV_D, threshold="≤ 40 % блоков с тенью", landing="карточки фич с тенью", base="UI-report §4.3 (D5)"),
    "E1": dict(action="severity", sev=SEV_D, threshold="шкала слоёв с −1…5 и 9999", landing="слои эффектов: фон-canvas −1, оверлеи, курсор 9999",
               base="код ui_audit E1 (серьёзно; в UI-report §4.3 не указан — найдено K при чтении кода)"),
    "E2": dict(action="severity", sev=SEV_D, threshold="> 1500 — информативно", landing="баннеры cookie и виджеты третьих сторон (2147483647)",
               base="код ui_audit E2 (серьёзно); сторонние слои страница не выбирает"),
    "H1": dict(action="recompute", sev=SEV_D, threshold="≤ 10 кеглей текста ≤ 24 px; display > 24 — отдельно (информативно)",
               landing="display-роли 48–160 на clamp() дают по кеглю на ширину окна", base="UI-report §4.3 (H1/H2); PLAN «Поправки» (кегли до 32–40); D 04/01"),
    "H2": dict(action="recompute", sev=SEV_D, threshold="кегли ≤ 24 px из текстовой шкалы 12–24; display — MKT-T1…T5",
               landing="display 48–160", base="UI-report §4.3; D 04/01 (display-роли, clamp)"),
    "H4": dict(action="recompute", sev=SEV_D, threshold="0 весов < 400 у текста < 32 px", landing="светлый display — выбор гарнитуры",
               base="UI-report §4.3 (H4)"),
    "H8": dict(action="retune", sev=SEV_S, threshold="абзацы ≤ 760 px", landing="лид в колонке 748 (D measure-lead)", base="D marketing-tokens size.measure-lead"),
    "H10": dict(action="recompute", sev=SEV_D, threshold="0 абзацев капсом (> 40 знаков); капс-лейблы и надзаголовки — cliche:caps-eyebrow",
                landing="eyebrow капсом, капс-display", base="UI-report §4.3 (H10); реестр H caps-eyebrow"),
    "J2": dict(action="info", sev=SEV_D, threshold="информативно", landing="полноэкранная колонка-картинка принимается за сайдбар",
               base="UI-report §4.3 (J2: эвристика x < 8, h > 45 %, 120 < w < 480)"),
    "J6": dict(action="recompute", sev=SEV_D, threshold="≤ 6 сеток с равными колонками (однотипные плитки — cliche:bento-uniform-tiles)",
               landing="repeat(3, 1fr) фич, бенто — законные архетипы", base="UI-report §4.3 (J6); PLAN «Поправки» (три карточки и bento, D, H)"),
    "J8": dict(action="recompute", sev=SEV_D, threshold="шапка ≤ 140 px; header выше 50 % экрана — hero, не шапка",
               landing="hero, свёрстанный тегом header", base="UI-report §4.3 (J8)"),
    "K2": dict(action="retune", sev=SEV_D, threshold="длительности из motion.marketing (0–1200 мс)", landing="hero-сцены 600–1200 мс",
               base="UI-report §4.3 (K2/K3); PLAN «Поправки» (ui 08/01, 08/03 потолок 300–400 → hero 600–1200, E); E marketing-tokens"),
    "L5": dict(action="recompute", sev=SEV_D, threshold="≤ 3 гарнитуры (display + текстовая + моно для данных)",
               landing="display + text", base="UI-report §4.3 (L5); PLAN «Поправки» (ui 13/01 Я5 против маркера 6, D, K)"),
    "M1": dict(action="severity", sev=SEV_D, threshold="длительности при reduce ≤ обычных", landing="reduce-ветка лендинга обнуляет появление — это норма E (конечные состояния)",
               base="E 05/01 §4 (reduce, not remove: конечные состояния, crossfade 180 мс); проверка поведения — motion_check.py"),
    "F1": dict(action="keep", sev=SEV_B, threshold="цели ≥ 24 px (WCAG 2.5.8) и на тач-прогоне", landing="—",
               base="WCAG 2.2 SC 2.5.8; на тач-прогоне 24, а не 44 (44 — практика HIG, у ui_audit --touch)"),
}
KEEP_NOTE = "как в consumer"

# =====================================================================================================================
# 3. Сбор дополнительных данных в странице (после COLLECT_JS; узлы уже помечены data-uia)
# =====================================================================================================================
EXTRA_JS = r"""
(opts) => {
  const out = {v: 1};
  const IH = innerHeight, IW = innerWidth;
  const rootFs = parseFloat(getComputedStyle(document.documentElement).fontSize) || 16;
  const sel = (el) => { if (!el || !el.tagName) return ''; const id = el.id ? '#' + el.id : '';
    const cls = (typeof el.className === 'string' && el.className.trim()) ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return (el.tagName.toLowerCase() + id + cls).slice(0, 70); };
  const vis = (el) => { const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    const r = el.getBoundingClientRect(); return r.width >= 1 && r.height >= 1; };
  const effOp = (el) => { let o = 1, n = el, d = 0; while (n && n.nodeType === 1 && d < 40) { o *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; d++; } return o; };
  const ownText = (el) => Array.from(el.childNodes).filter(n => n.nodeType === 3 && n.textContent.trim()).map(n => n.textContent.trim()).join(' ');
  const txt = (el) => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim();
  const all = Array.from(document.body ? document.body.getElementsByTagName('*') : []).slice(0, opts.maxElements || 8000);

  // --- CSSOM: clamp() в font-size, медиазапросы reduce, animation-timeline
  const clamps = []; let sheetsBlocked = 0, rules = 0, sda = 0; const prm = {reduce: 0, noPref: 0};
  const splitTop = (s) => { const parts = []; let d = 0, cur = ''; for (const ch of s) { if (ch === '(') d++; if (ch === ')') d--;
    if (ch === ',' && d === 0) { parts.push(cur.trim()); cur = ''; } else cur += ch; } if (cur.trim()) parts.push(cur.trim()); return parts; };
  const toPx = (s) => { const m = String(s).trim().match(/^(-?[\d.]+)(px|rem|em)?$/); if (!m) return null; const v = parseFloat(m[1]);
    return (!m[2] || m[2] === 'px') ? v : v * rootFs; };
  const addClamp = (where, val) => { const i = val.indexOf('clamp('); if (i < 0) return; let d = 1, j = i + 6; const st = j;
    while (j < val.length && d > 0) { if (val[j] === '(') d++; else if (val[j] === ')') d--; j++; }
    const p = splitTop(val.slice(st, j - 1));
    if (p.length !== 3) { clamps.push({where, val: val.slice(0, 90), unresolved: true}); return; }
    const lo = toPx(p[0]), hi = toPx(p[2]);
    clamps.push({where: String(where).slice(0, 80), val: val.slice(0, 90), min: lo, max: hi,
                 ratio: (lo && hi) ? Math.round(hi / lo * 100) / 100 : null, unresolved: lo === null || hi === null}); };
  const mq = (t) => { if (!t || !/prefers-reduced-motion/.test(t)) return; if (/no-preference/.test(t)) prm.noPref++; else prm.reduce++; };
  const walk = (list) => { for (const r of list) { rules++; if (rules > 80000) return;
      try { if (r.media && r.media.mediaText) mq(r.media.mediaText); else if (r.conditionText) mq(r.conditionText);
        if (r.style) { const fs = r.style.getPropertyValue('font-size'); if (fs && fs.includes('clamp(')) addClamp(r.selectorText || '@', fs);
          if (r.style.getPropertyValue('animation-timeline')) sda++; }
        if (r.cssRules) walk(r.cssRules); } catch (e) {} } };
  for (const sh of Array.from(document.styleSheets)) { try { walk(sh.cssRules); } catch (e) { sheetsBlocked++; } }
  document.querySelectorAll('[style*="clamp("]').forEach(el => { const fs = el.style.getPropertyValue('font-size');
    if (fs && fs.includes('clamp(')) addClamp(sel(el), fs); });
  out.css = {rules, sheetsBlocked, prm, sda, clamps: clamps.slice(0, 200), sheets: document.styleSheets.length};

  // --- строки, висячие предлоги
  const lineCount = (el) => { const rg = document.createRange(); rg.selectNodeContents(el);
    const rects = Array.from(rg.getClientRects()).filter(r => r.width > 1 && r.height > 4); const mids = [];
    for (const r of rects) { const m = r.top + r.height / 2; if (!mids.some(t => Math.abs(t - m) < r.height * 0.45)) mids.push(m); }
    return mids.length; };
  const PREP = new Set(['в','во','с','со','к','ко','о','об','обо','у','и','а','но','на','по','за','от','до','из','без','для','при','про','над','под','не','ни','что','как','или','же']);
  const hanging = (el) => { const res = []; const tw = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); const words = []; let n;
    while ((n = tw.nextNode())) { const re = /[^\s ]+/g; let m;
      while ((m = re.exec(n.textContent))) { const rg = document.createRange(); rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
        const rc = rg.getClientRects()[0]; if (rc) words.push({w: m[0], top: rc.top, h: rc.height}); } if (words.length > 80) break; }
    for (let i = 0; i + 1 < words.length; i++) { const a = words[i], b = words[i + 1];
      const w = a.w.toLowerCase().replace(/[«»"'(),.:;!?–—\-]/g, '');
      if (PREP.has(w) && b.top - a.top > a.h * 0.5) res.push(a.w + ' ⏎ ' + b.w); }
    return res; };
  const isCaps = (el, t) => getComputedStyle(el).textTransform === 'uppercase' || (/[A-Za-zА-Яа-яЁё]{3}/.test(t) && t === t.toUpperCase());
  out.h1 = Array.from(document.querySelectorAll('h1')).filter(vis).slice(0, 4).map(el => { const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    return {sel: sel(el), text: txt(el).slice(0, 90), len: txt(el).length, lines: lineCount(el), fs: parseFloat(cs.fontSize),
            y: Math.round(r.top + scrollY), h: Math.round(r.height), w: Math.round(r.width), op: Math.round(effOp(el) * 100) / 100}; });
  const disp = [];
  for (const el of all) { if (disp.length >= 40) break; const t = ownText(el); if (t.length < 2) continue;
    const cs = getComputedStyle(el); const fs = parseFloat(cs.fontSize); if (fs < opts.displayMin) continue; if (!vis(el)) continue;
    const r = el.getBoundingClientRect(); const lh = cs.lineHeight === 'normal' ? null : parseFloat(cs.lineHeight) / fs;
    const ls = cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing) / fs;
    disp.push({sel: sel(el), tag: el.tagName.toLowerCase(), fs: Math.round(fs * 10) / 10, lh: lh === null ? null : Math.round(lh * 1000) / 1000,
               ls: Math.round(ls * 10000) / 10000, ff: (cs.fontFamily || '').split(',')[0].replace(/["']/g, '').trim(), fw: parseInt(cs.fontWeight) || 400,
               caps: isCaps(el, t), cyr: /[А-Яа-яЁё]/.test(t), text: t.slice(0, 60), hang: hanging(el).slice(0, 4), y: Math.round(r.top + scrollY),
               grad_text: (cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') && (cs.backgroundImage || '').includes('gradient')}); }
  out.display = disp;

  // --- анимации (снимок): тип, цель, длительность, повторы, кривая, свойства, таймлайн
  const anims = []; let animTotal = 0;
  try { for (const a of document.getAnimations()) { animTotal++; if (anims.length >= 300) continue;
      const ef = a.effect; let t = {}; try { t = ef.getTiming(); } catch (e) {}
      let props = [], kfEase = [];
      try { const kf = ef.getKeyframes(); const s = new Set(); kf.forEach(k => { Object.keys(k).forEach(p => { if (!['offset', 'easing', 'composite', 'computedOffset'].includes(p)) s.add(p); }); if (k.easing) kfEase.push(k.easing); }); props = [...s]; } catch (e) {}
      const tg = ef && ef.target; let inView = false, size = 0, textUnder = 0;
      if (tg && tg.getBoundingClientRect) { const r = tg.getBoundingClientRect(); inView = r.bottom > 0 && r.top < IH && r.right > 0 && r.left < IW; size = Math.round(Math.min(r.width, r.height)); }
      anims.push({type: a.constructor.name, name: (a.animationName || a.transitionProperty || a.id || '').slice(0, 40), target: tg ? sel(tg) : '',
                  dur: typeof t.duration === 'number' ? Math.round(t.duration) : null, delay: Math.round(t.delay || 0),
                  iter: t.iterations === Infinity ? 'inf' : (t.iterations || 1), easing: t.easing || '', kfEase: [...new Set(kfEase)].slice(0, 3),
                  props: props.slice(0, 8), state: a.playState, timeline: a.timeline ? a.timeline.constructor.name : 'none', inView, size,
                  tag: tg && tg.tagName ? tg.tagName.toLowerCase() : '', pseudo: (ef && ef.pseudoElement) || ''}); } } catch (e) {}
  out.anims = anims; out.animTotal = animTotal;

  // --- элементы управления движением, видео, курсор, плавная прокрутка, pin
  const ctrlRe = /(пауз|останов|стоп|выключ|движени|анимац|pause|stop|play|resume|motion|animation)/i;
  out.pause = Array.from(document.querySelectorAll('button, [role=button], [role=switch], input[type=checkbox], [aria-pressed]')).filter(vis).map(el => {
      const lb = el.getAttribute('aria-labelledby'); const labs = el.labels ? Array.from(el.labels).map(l => txt(l)).join(' ') : '';
      const wrap = el.closest('label') ? txt(el.closest('label')) : '';
      const name = [el.getAttribute('aria-label') || '', txt(el), el.title || '', labs, wrap,
        lb ? ((document.getElementById(lb) || {}).textContent || '') : ''].join(' ').trim();
      const r = el.getBoundingClientRect(); return {sel: sel(el), name: name.slice(0, 60), w: Math.round(r.width), h: Math.round(r.height), pressed: el.getAttribute('aria-pressed')}; })
    .filter(x => ctrlRe.test(x.name)).slice(0, 10);
  out.videos = Array.from(document.querySelectorAll('video')).slice(0, 12).map(v => { const r = v.getBoundingClientRect();
    return {src: (v.currentSrc || v.src || '').split('/').pop().slice(0, 60), autoplay: v.autoplay, loop: v.loop, muted: v.muted, paused: v.paused,
            poster: !!v.poster, dur: isFinite(v.duration) ? Math.round(v.duration * 10) / 10 : null, above: r.top < IH && r.bottom > 0,
            w: Math.round(r.width), h: Math.round(r.height)}; });
  const rootCur = getComputedStyle(document.documentElement).cursor, bodyCur = document.body ? getComputedStyle(document.body).cursor : '';
  out.cursorNone = rootCur === 'none' || bodyCur === 'none';
  const html = document.documentElement;
  out.smooth = {lenis: html.classList.contains('lenis') || !!document.querySelector('[data-lenis-prevent], .lenis'),
                smoother: !!document.querySelector('#smooth-wrapper, .smooth-wrapper, #smooth-content'),
                locomotive: !!document.querySelector('[data-scroll-container]'), cssSmooth: getComputedStyle(html).scrollBehavior === 'smooth'};
  out.pins = document.querySelectorAll('.pin-spacer').length;
  out.sticky = all.filter(el => { const cs = getComputedStyle(el); return cs.position === 'sticky' && el.getBoundingClientRect().height > IH * 0.5; }).length;

  // --- блоки страницы и скрытое до прокрутки (появление)
  let blocks = Array.from(document.querySelectorAll('section')).filter(s => !s.parentElement || !s.parentElement.closest('section'));
  if (blocks.length < 3) { const host = document.querySelector('main') || document.body; blocks = Array.from(host.children).filter(c => c.getBoundingClientRect().height >= 200); }
  const blockOf = (el) => { for (let i = 0; i < blocks.length; i++) if (blocks[i].contains(el)) return i; return -1; };
  const carriers = new Map(); let textBelow = 0;
  for (const el of all) { const r = el.getBoundingClientRect(); if (r.top < IH || r.width < 4 || r.height < 4) continue;
    const t = ownText(el); const media = /^(img|video|picture|svg|canvas)$/i.test(el.tagName); if (t.length < 3 && !media) continue;
    const cs = getComputedStyle(el); if (cs.display === 'none') continue; textBelow++;
    if (effOp(el) >= 0.05 && cs.visibility !== 'hidden') continue;
    let h = el; while (h && h.nodeType === 1 && parseFloat(getComputedStyle(h).opacity) >= 0.05 && getComputedStyle(h).visibility !== 'hidden') h = h.parentElement;
    if (!h || h.nodeType !== 1) h = el; if (carriers.has(h)) continue;
    const hs = getComputedStyle(h);
    const tr = hs.transform === 'none' ? 'none' : (hs.transform.match(/matrix\(([^)]+)\)/) ? ('ty' + Math.round(parseFloat(hs.transform.match(/matrix\(([^)]+)\)/)[1].split(',')[5] || 0))) : hs.transform.slice(0, 30));
    carriers.set(h, {sel: sel(h), sig: [tr, hs.transitionDuration, hs.animationName].join('|'), block: blockOf(h)}); }
  const groups = {}; for (const c of carriers.values()) { const g = groups[c.sig] || (groups[c.sig] = {sig: c.sig, n: 0, blocks: new Set(), ex: []});
    g.n++; g.blocks.add(c.block); if (g.ex.length < 4) g.ex.push(c.sel); }
  out.reveal = {blocks: blocks.length, textBelow, hidden: carriers.size,
                groups: Object.values(groups).map(g => ({sig: g.sig, n: g.n, blocks: g.blocks.size, ex: g.ex})).sort((a, b) => b.n - a.n).slice(0, 8)};

  // --- приметы реестра клише (DOM)
  const heads = Array.from(document.querySelectorAll('h1, h2, h3')).filter(vis);
  let eyebrows = 0; const eyeEx = [];
  for (const h of heads) { let p = h.previousElementSibling; if (!p && h.parentElement) p = h.parentElement.previousElementSibling;
    if (!p || !vis(p)) continue; const cs = getComputedStyle(p); const t = txt(p); const fs = parseFloat(cs.fontSize);
    const gap = h.getBoundingClientRect().top - p.getBoundingClientRect().bottom;
    if (fs <= 16 && t.length >= 2 && t.length <= 48 && isCaps(p, t) && gap >= -2 && gap <= 80) { eyebrows++; if (eyeEx.length < 4) eyeEx.push(sel(p) + ' «' + t.slice(0, 24) + '»'); } }
  const monoRe = /mono|courier|menlo|consolas|monaco|fira code|source code/i;
  const mono = all.filter(el => { const t = ownText(el); if (t.length < 3 || /^(code|pre|kbd|samp)$/i.test(el.tagName) || el.closest('pre, code')) return false;
      if (/^[\d\s.,:%+\-–—\/$€₽×x]+$/.test(t)) return false; return monoRe.test(getComputedStyle(el).fontFamily) && vis(el); }).slice(0, 20).map(el => sel(el) + ' «' + ownText(el).slice(0, 20) + '»');
  const accent = heads.filter(h => { const hc = getComputedStyle(h); return Array.from(h.querySelectorAll('span, em, i, strong, mark, b')).some(c => {
      const t = ownText(c); if (t.length < 2) return false; const cc = getComputedStyle(c);
      return cc.color !== hc.color || (cc.fontStyle === 'italic' && hc.fontStyle !== 'italic') || cc.fontFamily !== hc.fontFamily
        || ((cc.backgroundClip === 'text' || cc.webkitBackgroundClip === 'text') && cc.backgroundImage.includes('gradient')); }); }).map(sel).slice(0, 6);
  const splitH = heads.filter(h => { const sp = Array.from(h.querySelectorAll('span, div')).filter(s => { const cs = getComputedStyle(s);
      return (cs.display === 'inline-block' || cs.display === 'block' || cs.transform !== 'none') && txt(s).length > 0 && txt(s).length <= 14; }); return sp.length >= 4; }).map(sel);
  const gradText = all.filter(el => { const cs = getComputedStyle(el); return (cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text')
      && (cs.backgroundImage || '').includes('gradient') && txt(el).length > 1 && vis(el); }).map(sel).slice(0, 8);
  const blobs = [];
  for (const el of all) { if (blobs.length > 10) break; const r = el.getBoundingClientRect(); if (r.top > IH || r.bottom < 0 || r.width < 120 || r.height < 120) continue;
    if (txt(el).length > 0) continue; const cs = getComputedStyle(el); const m = (cs.filter || '').match(/blur\(([\d.]+)px\)/); const bl = m ? parseFloat(m[1]) : 0;
    const radial = (cs.backgroundImage || '').includes('radial-gradient'); const round = parseFloat(cs.borderTopLeftRadius) >= Math.min(r.width, r.height) * 0.3;
    if ((bl >= 30 && (round || radial)) || (radial && bl >= 20)) blobs.push(sel(el) + ' blur ' + bl); }
  const glassFirst = all.filter(el => { const cs = getComputedStyle(el); if (!cs.backdropFilter || cs.backdropFilter === 'none') return false;
      const r = el.getBoundingClientRect(); return r.top < IH && r.bottom > 0 && r.width > 40 && r.height > 20; }).map(sel).slice(0, 12);
  const bento = [];
  for (const el of all) { if (bento.length > 6) break; const cs = getComputedStyle(el); if (cs.display !== 'grid' && cs.display !== 'inline-grid') continue;
    const kids = Array.from(el.children).filter(vis); if (kids.length < 5) continue;
    const rad = kids.map(k => getComputedStyle(k).borderTopLeftRadius); const r0 = rad[0];
    const tile = kids.every(k => { const s = getComputedStyle(k); return s.backgroundColor !== 'rgba(0, 0, 0, 0)' || s.borderTopWidth !== '0px' || s.boxShadow !== 'none'; });
    if (parseFloat(r0) > 0 && rad.every(x => x === r0) && tile) bento.push(sel(el) + ' ×' + kids.length + ' r=' + r0); }
  let pill = null; const h1 = document.querySelector('h1');
  if (h1 && vis(h1)) { const hr = h1.getBoundingClientRect(); const zone = h1.parentElement || document.body;
    for (const el of Array.from(zone.querySelectorAll('*')).concat(Array.from((zone.parentElement || zone).children))) { if (el === h1 || h1.contains(el) || el.contains(h1)) continue;
      const r = el.getBoundingClientRect(); const cs = getComputedStyle(el); const t = txt(el);
      if (r.bottom <= hr.top + 2 && hr.top - r.bottom <= 160 && r.height >= 18 && r.height <= 44 && t.length >= 5 && t.length <= 60
          && parseFloat(cs.borderTopLeftRadius) >= r.height / 2 - 1 && (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || cs.borderTopWidth !== '0px')) { pill = sel(el) + ' «' + t.slice(0, 30) + '»'; break; } } }
  const grads = [];
  for (const el of all) { if (grads.length > 30) break; const r = el.getBoundingClientRect(); if (r.top > IH || r.bottom < 0) continue;
    if (r.width * r.height < IW * IH * 0.03) continue; const bi = getComputedStyle(el).backgroundImage;
    if (bi && bi.includes('gradient')) grads.push({sel: sel(el), cols: (bi.match(/rgba?\([^)]+\)/g) || []).slice(0, 8), area: Math.round(r.width * r.height / (IW * IH) * 100)}); }
  out.cliche = {headings: heads.length, eyebrows, eyeEx, mono, accent, splitH, gradText, blobs, glassFirst, bento, pill, grads};
  return out;
}
"""

NARROW_JS = "() => ({scrollW: document.documentElement.scrollWidth, innerW: innerWidth, bodyW: document.body ? document.body.scrollWidth : 0})"


# =====================================================================================================================
# 4. Вспомогательное
# =====================================================================================================================
def load_font_metrics(path=FONTS_YAML):
    """cyrillic-display-fonts.yaml (D) → {имя гарнитуры в нижнем регистре: metrics}; нет yaml или файла — {}."""
    try:
        import yaml
        d = yaml.safe_load(open(path, encoding="utf-8"))
    except Exception:
        return {}
    out = {}

    def visit(node):
        if isinstance(node, dict):
            name = node.get("family") or node.get("name")
            if isinstance(name, str) and isinstance(node.get("metrics"), dict):
                out[name.strip().lower()] = node["metrics"]
            for v in node.values():
                visit(v)
        elif isinstance(node, list):
            for v in node:
                visit(v)
    visit(d)
    return out


def rgb_css_to_hex(s):
    m = re.match(r"rgba?\(([^)]+)\)", s or "")
    if not m:
        return None, 0.0
    p = [float(x) for x in re.split(r"[,\s/]+", m.group(1).strip()) if x]
    if len(p) < 3:
        return None, 0.0
    a = p[3] if len(p) > 3 else 1.0
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(v)))) for v in p[:3]), a


def chromatic_hues(hexes, c_min=0.05, window=30.0):
    """Число различимых хроматических оттенков: C ≥ c_min и 0,1 < L < 0,98; кластеры по оттенку шириной window°."""
    hues = []
    for h in hexes:
        try:
            L, C, H = hex2oklch(h)
        except Exception:
            continue
        if C >= c_min and 0.1 < L < 0.98:
            hues.append(H % 360)
    hues.sort()
    clusters = []
    for h in hues:
        if clusters and (h - clusters[-1][-1]) <= window:
            clusters[-1].append(h)
        else:
            clusters.append([h])
    if len(clusters) > 1 and (clusters[0][0] + 360 - clusters[-1][-1]) <= window:   # замыкание круга
        clusters[0] = clusters[-1] + clusters[0]
        clusters.pop()
    return [round(sum(c) / len(c)) % 360 for c in clusters]


def oklch_share(png_bytes, h_lo=270.0, h_hi=320.0, c_min=0.06):
    """Доля пикселей кадра в полосе оттенка OKLCH (метрика MET реестра H: purple-neon-band)."""
    import numpy as np
    from PIL import Image
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    im.thumbnail((480, 480))
    a = np.asarray(im, dtype=np.float64) / 255.0
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    r, g, b = lin[..., 0], lin[..., 1], lin[..., 2]
    l_ = np.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m_ = np.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s_ = np.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    C = np.hypot(A, B)
    H = (np.degrees(np.arctan2(B, A)) + 360.0) % 360.0
    band = (C > c_min) & (H >= h_lo) & (H <= h_hi)
    return round(100.0 * float(band.mean()), 2)


def controls(rows):
    """Та же выборка контролов, что в ui_audit B1/B2 (чтобы пересчёт был сопоставим)."""
    ctrl = [r for r in rows if r["inter"] and (r["tag"] in ("button", "input", "select") or r["role"] == "button")]
    return [r for r in ctrl if r["h"] >= 12 and r["w"] >= 12 and r["role"] != "switch"
            and not (r["tag"] == "input" and r["h"] <= 24 and r["w"] <= 48)]


def replace_finding(rep, cid, **kw):
    for f in rep.findings:
        if f["id"] == cid:
            f.update(kw)
            return f
    return None


def verdict_of(ok):
    return "OK" if ok is True else ("WARN" if ok is None else "FAIL")


# =====================================================================================================================
# 5. Профиль: пересчёт и смена серьёзности на данных прогона
# =====================================================================================================================
def apply_profile(rep, data, ctx):
    rows, meta = data["rows"], data["meta"]
    P = PRESET_MARKETING
    text_rows = [r for r in rows if r["txt"]]
    for f in rep.findings:
        pr = PROFILE.get(f["id"])
        f["profile"] = pr["action"] if pr else "keep"
        f["base"] = pr["base"] if pr else KEEP_NOTE
        if pr and pr["action"] in ("retune", "severity"):
            f["severity"] = pr["sev"]
        if pr and pr["action"] == "info":
            f["verdict"] = "WARN"
            f["severity"] = pr["sev"]
            f["threshold"] = "информативно (профиль marketing)"

    # A1 / A2 — только компонентные отступы ≤ 48 px
    sp = []
    for r in rows:
        for k in ("pt", "pr", "pb", "pl", "mt", "mr", "mb", "ml", "rg", "cg"):
            v = r[k]
            if v is not None and v != 0:
                sp.append(abs(v))
    small = [v for v in sp if v <= 48]
    big = sorted({round(v) for v in sp if v > 48})
    share = (len([v for v in small if U.in_scale(v, P["spacing"])]) / len(small)) if small else 1.0
    bad = sorted({v for v in small if not U.in_scale(v, P["spacing"])})
    replace_finding(rep, "A1", rule="Доля padding/margin/gap ≤ 48 px из шкалы (секции > 48 — ритм, информативно)",
                    found=f"{share*100:.1f} % (секционных значений > 48: {len(big)})", threshold="≥ 90 %",
                    verdict=verdict_of(share >= 0.90), severity=SEV_D,
                    examples=([f"вне шкалы ≤ 48: {', '.join(str(v) for v in bad[:12])}"] if bad else [])
                    + ([f"> 48: {', '.join(str(v) for v in big[:14])}"] if big else []))
    five = sorted({v for v in small if abs(v % 5) < 0.01 and abs(v % 4) > 0.01})
    replace_finding(rep, "A2", rule="Значения ≤ 48 px, кратные 5 и не кратные 4", found=len(five), threshold="0",
                    verdict=verdict_of(not five), severity=SEV_D, examples=[str(v) for v in five[:8]])

    # B1 / B2 — высоты контролов
    ctrl = controls(rows)
    heights = sorted({round(r["h"]) for r in ctrl})
    replace_finding(rep, "B1", found=len(heights), threshold=f"≤ {P['unique_heights_max']}",
                    verdict=verdict_of(len(heights) <= P["unique_heights_max"]), severity=SEV_D,
                    examples=[", ".join(str(h) for h in heights)])
    off = [h for h in heights if not U.in_scale(h, P["heights"], tol=0.51)]
    replace_finding(rep, "B2", rule=f"Высоты вне ряда {'/'.join(str(x) for x in P['heights'])}", found=len(off), threshold="0",
                    verdict=verdict_of(not off), severity=SEV_D, examples=[", ".join(str(h) for h in off)])

    # D4 — свечения: ≤ 2; ≥ 3 цветных — примета neon-glow
    glow, colored = [], 0
    for s in sorted({r["sh"] for r in rows if r["sh"]}):
        for (ox, oy, blur, spread, inset) in U.parse_shadows(s):
            if not inset and ox == 0 and oy == 0 and blur > 8:
                glow.append(s[:70])
                hx, _a = rgb_css_to_hex((re.search(r"rgba?\([^)]+\)", s) or [None])[0] if re.search(r"rgba?\([^)]+\)", s) else "")
                try:
                    if hx and hex2oklch(hx)[1] >= 0.08:
                        colored += 1
                except Exception:
                    pass
                break
    replace_finding(rep, "D4", rule="Свечения (тень с нулевым смещением и blur > 8)", found=f"{len(glow)} (цветных {colored})",
                    threshold="≤ 2", verdict=verdict_of(len(glow) <= 2), severity=SEV_D, examples=glow[:6],
                    note="≥ 3 цветных свечения без источника света — cliche:neon-glow (реестр H, D)")

    # H1 / H2 / H4 / H10 — текст отдельно от display
    fs_text = sorted({r["fs"] for r in text_rows if r["fs"] and r["fs"] <= TEXT_MAX_PX})
    fs_disp = sorted({r["fs"] for r in text_rows if r["fs"] and r["fs"] > TEXT_MAX_PX})
    replace_finding(rep, "H1", rule=f"Уникальных кеглей текста ≤ {TEXT_MAX_PX} px (display — отдельно)", found=f"{len(fs_text)} (display: {len(fs_disp)})",
                    threshold=f"≤ {P['unique_font_sizes_max']}", verdict=verdict_of(len(fs_text) <= P["unique_font_sizes_max"]), severity=SEV_D,
                    examples=[", ".join(str(v) for v in fs_text), "display: " + ", ".join(str(v) for v in fs_disp[:12])])
    off_fs = [v for v in fs_text if not U.in_scale(v, P["font_sizes"], tol=0.51)]
    replace_finding(rep, "H2", rule=f"Кегли текста ≤ {TEXT_MAX_PX} px вне шкалы {P['font_sizes']}", found=len(off_fs), threshold="0",
                    verdict=verdict_of(not off_fs), severity=SEV_D, examples=[", ".join(str(v) for v in off_fs)])
    light = sorted({r["fw"] for r in text_rows if r["fw"] and r["fw"] < 400 and (r["fs"] or 0) < 32})
    replace_finding(rep, "H4", rule="Веса легче 400 у текста мельче 32 px", found=len(light), threshold="0",
                    verdict=verdict_of(not light), severity=SEV_D, examples=[", ".join(str(v) for v in light)])
    caps_par = [r["sel"] for r in text_rows if r["tt"] in ("uppercase", "capitalize") and len(r["txt"]) > 40]
    replace_finding(rep, "H10", rule="Абзацы капсом (> 40 знаков)", found=len(caps_par), threshold="0",
                    verdict=verdict_of(not caps_par), severity=SEV_D, examples=caps_par[:6])

    # J6 — равные колонки: ≤ 6
    rigid = []
    for r in rows:
        g = r["gtc"]
        if g:
            tr = g.split()
            if len(tr) >= 3 and len(set(tr)) == 1 and "minmax" not in g:
                rigid.append(f"{r['sel']}: {g[:50]}")
    replace_finding(rep, "J6", found=len(rigid), threshold="≤ 6", verdict=verdict_of(len(rigid) <= 6), severity=SEV_D, examples=rigid[:6])

    # J8 — шапка ≤ 140, header выше 50 % экрана — hero
    headers = [r for r in rows if r["tag"] == "header" and r["w"] > meta["innerW"] * 0.4 and r["h"] <= meta["innerH"] * 0.5]
    tall = [f"{r['sel']} {round(r['h'])}px" for r in headers if r["h"] > P["page_header_max"]]
    replace_finding(rep, "J8", rule=f"Шапка не выше {P['page_header_max']} px (header выше 50 % экрана — hero)", found=len(tall), threshold="0",
                    verdict=verdict_of(not tall), severity=SEV_D, examples=tall)

    # J3 — «контентной области ≥ 640» имеет смысл только на десктопе
    if meta["innerW"] < 1024:
        replace_finding(rep, "J3", verdict="WARN", severity=SEV_D, threshold="информативно на ширине < 1024 (профиль marketing)")

    # L5 — гарнитуры ≤ 3
    fams = sorted({r["ff"] for r in text_rows if r["ff"]})
    replace_finding(rep, "L5", rule="Гарнитур на странице", found=len(fams), threshold="≤ 3 (display + текстовая + моно)",
                    verdict=verdict_of(len(fams) <= 3), severity=SEV_D, examples=[", ".join(fams)])
    return rep


# =====================================================================================================================
# 6. Свои проверки MKT-* и приметы клише
# =====================================================================================================================
def add_mkt(rep, data, extra, ctx, level, allow, fonts, shot_png=None, narrow=None):
    rows, meta = data["rows"], data["meta"]
    W = meta["innerW"]
    G_T, G_C, G_M, G_L, G_X = "Типографика (маркетинг)", "Цвет (маркетинг)", "Движение (маркетинг)", "Раскладка (маркетинг)", "Приметы клише"
    add = rep.add

    def mk(cid, group, rule, found, thr, ok, sev, ex=None, note=None, base=""):
        add(cid, group, rule, found, thr, ok, sev, ex, note)
        rep.findings[-1]["profile"] = "new"
        rep.findings[-1]["base"] = base

    css = extra.get("css") or {}
    # MKT-T1 clamp ≤ 2,5
    cl = [c for c in css.get("clamps", []) if c.get("ratio")]
    badc = [c for c in cl if c["ratio"] > 2.5]
    unres = len([c for c in css.get("clamps", []) if c.get("unresolved")])
    mk("MKT-T1", G_T, "font-size: clamp(): max ≤ 2,5 × min (иначе WCAG 1.4.4 при зуме 200 %)",
       f"{len(badc)} из {len(cl)} (var()/calc не раскрыто: {unres}; чужих CSS не прочитано: {css.get('sheetsBlocked', 0)})", "0",
       not badc, SEV_S, [f"{c['where']}: {c['val']} → ×{c['ratio']}" for c in badc[:6]],
       "= site SG-A11Y-08 (S); здесь — самопроверка исполнителя", "D 04/01 выжимка п.3 [проверено: D/01]; WCAG 2.2 SC 1.4.4; Barvian")
    # MKT-T2 строки H1
    h1 = extra.get("h1") or []
    if h1:
        lim = 2 if W >= 1200 else (4 if W <= 480 else 3)
        badh = [f"{h['sel']} «{h['text'][:40]}» — {h['lines']} строк при {W} px" for h in h1 if h["lines"] > lim]
        mk("MKT-T2", G_T, f"H1 ≤ {lim} строк при ширине {W} px (≤ 2 при 1440, ≤ 4 при 390)", f"{max(h['lines'] for h in h1)} (H1: {len(h1)})",
           f"≤ {lim}", not badh, SEV_D, badh, None, "D 04/01 выжимка п.5 (правило text и kimi T8); k3_checks M-H1-LINES")
    else:
        mk("MKT-T2", G_T, "H1 на странице", "нет видимого H1", "1", None, SEV_D, [], "H1 в HTML — site SG-SEO-03", "site page-gates SG-SEO-03")
    # MKT-T3/T4/T5 display: трекинг, интерлиньяж, висячие предлоги
    disp = [d for d in (extra.get("display") or []) if d["fs"] >= DISPLAY_MIN_PX]
    trk, lhb, hang, unknown = [], [], [], set()
    for d in disp:
        met = fonts.get((d["ff"] or "").lower())
        if d["cyr"] and met:
            tt = met.get("tracking_touch")
            if tt is not None and d["ls"] < tt + 0.005 - 1e-4:
                trk.append(f"{d['sel']} {d['ff']} {d['fs']}px: {d['ls']:+.3f} em < {tt + 0.005:+.3f}")
            floor = met.get("lh_floor_caps") if d["caps"] else met.get("lh_floor_lc")
            if floor and d["lh"] is not None and d["lh"] < floor - 1e-3:
                lhb.append(f"{d['sel']} {d['ff']} {d['fs']}px: lh {d['lh']} < {floor}{' (капс)' if d['caps'] else ''}")
        elif d["cyr"]:
            unknown.add(d["ff"])
            if d["caps"] and d["lh"] is not None and d["lh"] < 1.12:
                lhb.append(f"{d['sel']} {d['ff']} {d['fs']}px: капс lh {d['lh']} < 1,12 (умолчание D)")
        for w in d.get("hang") or []:
            hang.append(f"{d['sel']}: «{w}»")
    mk("MKT-T3", G_T, "Трекинг кириллического display ≥ tracking_touch + 0,005 em", len(trk), "0", not trk, SEV_D, trk[:6],
       (f"гарнитуры без метрик в cyrillic-display-fonts.yaml: {', '.join(sorted(unknown))}" if unknown else None),
       "D 04/01 выжимка п.11 [проверено: D/02, тест «ухо»]")
    mk("MKT-T4", G_T, "Интерлиньяж display ≥ lh_floor_lc (капс — lh_floor_caps)", len(lhb), "0", not lhb, SEV_D, lhb[:6], None,
       "D 04/01 выжимка п.9–10 [проверено: D/02]")
    mk("MKT-T5", G_T, "Висячие предлоги и союзы в конце строки display (нужен неразрывный пробел)", len(hang), "0", not hang, SEV_D, hang[:6], None,
       "D 04/01 выжимка п.8 [проверено: D/01 глазами]")

    # MKT-C1 хроматические цвета первого экрана по уровню
    IH = meta["innerH"]
    cols = set()
    for r in rows:
        if r["y"] >= IH or r["y"] + r["h"] <= 0:
            continue
        if r["txt"] and r["col"]:
            cols.add(r["col"])
        if r["bg"] and r["w"] * r["h"] >= 0.002 * W * IH and not r["bgguess"]:
            cols.add(r["bg"])
        if r["bcol"] and r["bw"]:
            cols.add(r["bcol"])
    for g in (extra.get("cliche") or {}).get("grads", []):
        for c in g.get("cols", []):
            hx, a = rgb_css_to_hex(c)
            if hx and a >= 0.3:
                cols.add(hx)
    hues = chromatic_hues(sorted(cols))
    cap = CHROMA_MAX.get(level, 3)
    mk("MKT-C1", G_C, f"Хроматических оттенков в первом экране (CSS: текст, фон, границы, градиенты) — уровень {level}",
       f"{len(hues)} (оттенки ≈ {', '.join(str(h) + '°' for h in hues)})", f"≤ {cap}", len(hues) <= cap, SEV_D, [],
       "картинки и видео не учитываются: это палитра решений, а не пикселей",
       "D 04/03 выжимка п.1 (L0 ≤ 2, L1 ≤ 3, L2 ≤ 4) [данные: C] [мнение вендора]")
    if shot_png is not None:
        try:
            share = oklch_share(shot_png)
            mk("MKT-C2", G_C, "Доля пикселей первого экрана в полосе OKLCH 270–320° (C > 0,06)", f"{share} %", "≤ 3 % при бренде вне полосы",
               None if share > 3 else True, SEV_D, [], "> 3 % — cliche:purple-neon-band (S), если бренд этого цвета не задаёт: сверить с art-direction",
               "реестр H purple-neon-band (MET, H/01); ai-media 06/01 R3")
        except Exception as e:  # pragma: no cover
            mk("MKT-C2", G_C, "Полоса 270–320°", f"ошибка: {str(e)[:60]}", "—", None, SEV_D, [], None, "")

    # MKT-M* движение (статический снимок; поведение — motion_check.py)
    anims = extra.get("anims") or []
    rv = extra.get("reveal") or {}
    blocks = rv.get("blocks") or 0
    top = (rv.get("groups") or [{}])[0] if rv.get("groups") else {}
    cover = (top.get("blocks", 0) / blocks) if blocks else 0
    same_reveal = bool(top) and top.get("n", 0) >= 5 and blocks >= 4 and cover >= 0.6 and not ctx.get("motion") == "reduce"
    mk("MKT-M1", G_M, "Одинаковое появление у ≥ 5 блоков (скрыто до прокрутки одной подписью «сдвиг + проявление»)",
       (f"{top.get('n', 0)} узлов в {top.get('blocks', 0)} из {blocks} блоков, подпись {top.get('sig', '')[:40]}" if top else f"скрытых до прокрутки нет (блоков {blocks})"),
       "< 5 узлов или < 60 % блоков", not same_reveal, SEV_S if same_reveal else SEV_D,
       [f"{g['n']} × {g['sig'][:48]} ({g['blocks']} блоков): {', '.join(g['ex'][:2])}" for g in (rv.get("groups") or [])[:3]],
       "= cliche:section-fade-up (реестр H, S); система появления E 05/02 §2.2 (2–3 примитива на страницу) снимает примету решением",
       "ui 11/04 маркер 28 с порогом (PLAN «Поправки»); реестр H section-fade-up (≥ 5 блоков)")
    LAYOUT = {"width", "height", "blocksize", "inlinesize", "top", "left", "right", "bottom", "margin", "padding", "inset", "maxheight", "maxwidth", "minheight", "fontsize", "lineheight", "letterspacing", "gridtemplatecolumns", "gridtemplaterows"}
    # 0.1.1 (S1, X-11): аккордеон <details> (::details-content, interpolate-size: allow-keywords) — UI-отклик по клику, не сцена: не считается
    def norm(p):
        return re.sub(r"[^a-z]", "", p.lower())
    lay = [f"{a['target']} ({', '.join(a['props'][:3])}, {a['dur']} мс)" for a in anims
           if any(norm(p) in LAYOUT or norm(p).startswith(("margin", "padding", "inset")) for p in a.get("props") or [])
           and a.get("timeline") != "ScrollTimeline" and a.get("timeline") != "ViewTimeline" and a.get("tag") != "details"]
    mk("MKT-M2", G_M, "Анимация свойств раскладки (width/height/block-size/top/left/margin/padding/font-size) в снимке getAnimations(); аккордеон <details> — исключение (X-11)",
       len(lay), "0", not lay, SEV_D, lay[:6], "почерк K3 (13 из 13 работ); двигать transform/opacity/clip-path/filter",
       "kimi 05/03 §3.5 (через PLAN «Главные риски» п.4); E 05/03")
    MOVE = {"transform", "translate", "left", "top", "right", "bottom", "x", "y"}
    lin = [f"{a['target']} ({a['dur']} мс)" for a in anims if a.get("iter") != "inf" and a.get("timeline") in ("DocumentTimeline", "none")
           and any(norm(p) in MOVE for p in a.get("props") or []) and (a.get("easing") == "linear")
           and all(e == "linear" for e in (a.get("kfEase") or ["linear"])) and (a.get("dur") or 0) >= 150]
    mk("MKT-M3", G_M, "linear у разового перемещения (не петли и не скраб)", len(lin), "0", not lin, SEV_D, lin[:6], None,
       "W1 (волна 2): «нет linear у перемещений»; E 05/01 §7.2 (кривые: out-expo вход, in-out перемещение, linear — петли)")
    long_ = [f"{a['target']} {a['dur']}+{a['delay']} мс" for a in anims if a.get("iter") != "inf" and a.get("timeline") in ("DocumentTimeline", "none")
             and (a.get("dur") or 0) + (a.get("delay") or 0) > 1200 and a.get("type") in ("CSSAnimation", "Animation", "CSSTransition")]
    mk("MKT-M4", G_M, "Разовая анимация длиннее 1200 мс (с задержкой)", len(long_), "0", not long_, SEV_D, long_[:6],
       "исключения — счётчик 1200, интро ≤ 3000 по решению L2", "E 05/01 §7.1; marketing-tokens hero-scene-max 1200, intro-max 3000")
    loops = [a for a in anims if a.get("iter") == "inf" and a.get("state") == "running" and (a.get("size") or 0) >= 24]
    pause = extra.get("pause") or []
    vids = [v for v in (extra.get("videos") or []) if (v.get("autoplay") or not v.get("paused")) and (v.get("loop") or (v.get("dur") or 0) > 5)]
    n_loops = len({a["target"] for a in loops}) + len(vids)
    n_view = len({a["target"] for a in loops if a.get("inView")}) + len([v for v in vids if v.get("above")])
    bad_loop = n_loops > 0 and not pause and ctx.get("motion") != "reduce"
    mk("MKT-M5", G_M, "Петли на странице (бесконечные анимации ≥ 24 px, видео-петли) и видимая кнопка паузы",
       f"петель {n_loops} (в первом экране {n_view}), кнопок паузы {len(pause)}", "петля → кнопка паузы или стоп ≤ 5 с", (None if (n_loops and pause) else (not bad_loop)),
       SEV_S, [f"{a['target']} {a['name']} {a['dur']} мс" for a in loops[:4]] + [f"video {v['src']}" for v in vids[:2]],
       "поведение (движется ли на 6-й с) подтверждает motion_check.py → B по site SG-A11Y-03",
       "WCAG 2.2 SC 2.2.2; E 05/01 §3.3; CRV-AL-02")
    prm = css.get("prm") or {}
    has_motion = bool(anims) or bool(rv.get("hidden")) or bool(vids)
    mk("MKT-M6", G_M, "В CSS есть ветка prefers-reduced-motion (reduce или no-preference)",
       f"reduce: {prm.get('reduce', 0)}, no-preference: {prm.get('noPref', 0)}", "≥ 1, если есть движение",
       True if (prm.get("reduce") or prm.get("noPref") or not has_motion) else None, SEV_D, [],
       "может жить в JS (matchMedia, gsap.matchMedia) — поведение проверяет прогон reduce (M1/M2 и motion_check.py)",
       "E 05/01 §4.3 (анимации только в @media (prefers-reduced-motion: no-preference) или gsap.matchMedia)")

    # MKT-J1 горизонтальная прокрутка на 360
    if narrow:
        over = narrow["scrollW"] - narrow["innerW"]
        mk("MKT-J1", G_L, "Нет горизонтальной прокрутки на 360 px", f"{narrow['scrollW']} против {narrow['innerW']}", "scrollWidth ≤ innerWidth + 2",
           over <= 2, SEV_B, [], "site SG-MOB-01 различает расширение области (B) и скрытое переполнение (D)", "D (волна 1: автопроверка на 360); site SG-MOB-01")

    # приметы реестра клише (DOM): сигнал «нужно решение art-direction» (--allow cliche:<id> — решение есть)
    cz = extra.get("cliche") or {}

    def cl(cid, rule, found, thr, hit, sev, ex=None, note=None):
        allowed = f"cliche:{cid}" in allow
        ok = True if not hit else (True if allowed else False)
        mk(f"cliche:{cid}", G_X, rule, found, thr, ok, sev, ex, (note or "") + (" · решение есть (--allow)" if (hit and allowed) else ""),
           "08-uniqueness-anti-slop/cliche-registry.yaml v0.1 (H)")
    heads = cz.get("headings") or 0
    cl("caps-eyebrow", "Надзаголовки капсом над заголовками", f"{cz.get('eyebrows', 0)} из {heads}", f"≤ ceil({heads}/3)",
       cz.get("eyebrows", 0) > math.ceil(heads / 3) if heads else False, SEV_S, cz.get("eyeEx"))
    cl("mono-captions", "Моноширинные подписи без данных", len(cz.get("mono") or []), "< 3", len(cz.get("mono") or []) >= 3, SEV_S, (cz.get("mono") or [])[:4])
    cl("accent-word-headline", "Заголовки с выделенным словом (цвет, курсив, гарнитура)", len(cz.get("accent") or []), "0 без решения",
       bool(cz.get("accent")), SEV_S, (cz.get("accent") or [])[:4], "≥ 2 — всегда примета")
    cl("gradient-text", "Градиентная заливка текста", len(cz.get("gradText") or []), "0 без решения", bool(cz.get("gradText")), SEV_S, (cz.get("gradText") or [])[:4])
    cl("split-text-reveal", "Split у заголовков (≥ 4 обёрток слов или букв)", f"{len(cz.get('splitH') or [])} из {heads}", "≤ 50 % заголовков",
       heads > 0 and len(cz.get("splitH") or []) > heads / 2, SEV_D, (cz.get("splitH") or [])[:4])
    cl("aurora-blobs", "Размытые пятна за текстом первого экрана", len(cz.get("blobs") or []), "< 2", len(cz.get("blobs") or []) >= 2, SEV_S, (cz.get("blobs") or [])[:4])
    cl("glassmorphism-panels", "Стеклянные элементы в первом экране", len(cz.get("glassFirst") or []), "≤ 2", len(cz.get("glassFirst") or []) > 2, SEV_S,
       (cz.get("glassFirst") or [])[:4], "стиль; цена backdrop-filter — прогон motion_check (LoAF)")
    cl("bento-uniform-tiles", "Сетки из ≥ 5 однотипных плиток с одним радиусом", len(cz.get("bento") or []), "0 без решения", bool(cz.get("bento")), SEV_D, (cz.get("bento") or [])[:4])
    cl("pill-announcement-chip", "Пилюля-анонс над H1", "есть" if cz.get("pill") else "нет", "без реального анонса — нет", bool(cz.get("pill")), SEV_D,
       [cz["pill"]] if cz.get("pill") else [], "реальный ли анонс — судит человек или LNT")
    big_disp = [d for d in (extra.get("display") or []) if d["fs"] > 160]
    cl("giant-display-type", "Display крупнее 160 px", len(big_disp), "0 без роли poster", bool(big_disp), SEV_D, [f"{d['sel']} {d['fs']}px" for d in big_disp[:4]])
    cl("custom-cursor-follower", "Системный курсор скрыт (cursor: none на html/body)", "да" if extra.get("cursorNone") else "нет", "нет без концепции",
       bool(extra.get("cursorNone")), SEV_S, [], "на тач-устройствах — всегда примета")
    sm = extra.get("smooth") or {}
    smooth_on = sm.get("lenis") or sm.get("smoother") or sm.get("locomotive")
    cl("smooth-scroll-default", "Плавная прокрутка без pin- и скраб-сцен", ("да" if smooth_on else "нет") + f" (pin {extra.get('pins', 0)}, sticky-сцен {extra.get('sticky', 0)})",
       "плавная прокрутка только ради сцен", bool(smooth_on) and not extra.get("pins") and not extra.get("sticky"), SEV_D, [])
    return rep


# =====================================================================================================================
# 7. Прогон: сервер, блокировки, браузер
# =====================================================================================================================
class Locks:
    """Две блокировки (общая тройки, затем наша) блокирующим flock с тревогой 900 с; память ≥ 3 ГБ."""
    def __init__(self, enabled=True, timeout=900):
        self.enabled, self.fds, self.timeout = enabled, [], timeout

    def __enter__(self):
        if not self.enabled:
            return self
        for p in LOCKS:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            fd = open(p, "a")

            def _alarm(signum, frame, p=p):
                raise TimeoutError(f"блокировка {p} занята дольше {self.timeout} с")
            old = signal.signal(signal.SIGALRM, _alarm)
            signal.alarm(self.timeout)
            t0 = time.time()
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old)
            if time.time() - t0 > 5:
                print(f"  блокировка {p}: ждали {time.time() - t0:.0f} с", file=sys.stderr, flush=True)
            self.fds.append(fd)
        wait_memory()
        return self

    def __exit__(self, *a):
        for fd in reversed(self.fds):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
            except Exception:
                pass
        self.fds = []


def mem_available_gb():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) / 1024 / 1024
    except Exception:
        pass
    return 99.0


def wait_memory(min_gb=3.0, max_wait=1800):
    t0 = time.time()
    while mem_available_gb() < min_gb:
        if time.time() - t0 > max_wait:
            raise SystemExit(f"память < {min_gb} ГБ дольше {max_wait} с — прогон отложен")
        print(f"  ждём память: {mem_available_gb():.1f} ГБ", file=sys.stderr, flush=True)
        time.sleep(20)


def serve_dir(root):
    class H(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

    class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
        daemon_threads = True
        allow_reuse_address = True
    srv = S(("127.0.0.1", 0), functools.partial(H, directory=root))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def local_root_for(page_path, root=None):
    """Корень раздачи: --root или подъём на глубину самых длинных ссылок «../» в HTML (лаборатория F: ../_shared, ../_vendor)."""
    d = os.path.dirname(page_path)
    if root:
        return os.path.abspath(root)
    try:
        html = open(page_path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return d
    depth = max([len(m.group(1)) // 3 for m in re.finditer(r"""(?:src|href|url)\s*[=(]\s*["']?((?:\.\./)+)""", html)] + [0])
    for _ in range(min(depth, 6)):
        d = os.path.dirname(d)
    return d


def resolve_target(target, root=None):
    if re.match(r"^https?://", target):
        return target, None
    path = os.path.abspath(target)
    if os.path.isdir(path):
        path = os.path.join(path, "index.html")
    if not os.path.isfile(path):
        raise SystemExit(f"нет файла {path}")
    r = local_root_for(path, root)
    srv, base = serve_dir(r)
    return f"{base}/{os.path.relpath(path, r)}", srv


def audit_pair(target, a, fonts):
    from playwright.sync_api import sync_playwright
    url, srv = resolve_target(target, a.root)
    opts = SimpleNamespace(strict_border=False, tokens_set=None)
    reps_m, reps_c, runs, raw = [], [], [], {}
    normal_rows = reduced_rows = None
    combos = [((w, h), "no-preference", False) for (w, h) in a.viewports]
    if not a.no_mobile:
        combos.append(((390, 844), "no-preference", True))
    if not a.no_reduced:
        combos.append((a.viewports[0], "reduce", False))
    try:
        with Locks(not a.no_lock):
            with sync_playwright() as pw:
                browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
                raw["browser"] = browser.version
                narrow = None
                for (w, h), motion, touch in combos:
                    context = browser.new_context(viewport={"width": w, "height": h}, color_scheme="light", reduced_motion=motion,
                                                  device_scale_factor=2 if touch else 1, has_touch=touch, is_mobile=touch, locale=a.locale)
                    page = context.new_page()
                    try:
                        page.goto(url, wait_until="load", timeout=a.timeout)
                    except Exception as e:
                        raw.setdefault("errors", []).append(f"{w}x{h}/{motion}: {str(e)[:120]}")
                    page.wait_for_timeout(a.wait)
                    data = page.evaluate(U.COLLECT_JS, {"maxElements": a.max_elements})
                    extra = page.evaluate(EXTRA_JS, {"maxElements": 8000, "displayMin": DISPLAY_MIN_PX})
                    shot = None
                    if motion == "no-preference" and not touch and not reps_m:
                        try:
                            shot = page.screenshot(type="png")
                        except Exception:
                            shot = None
                    tag = f"light/{w}x{h}" + ("/reduced" if motion == "reduce" else "") + ("/touch" if touch else "")
                    ctx = {"target": target, "scheme": "light", "viewport": tag.split("/", 1)[1], "motion": motion, "touch": touch,
                           "target_min": 24 if touch else PRESET_MARKETING["target_min"]}
                    if motion == "reduce":
                        reduced_rows = data["rows"]
                    elif normal_rows is None:
                        normal_rows = data["rows"]
                    rc = U.run_checks(data, U.PRESET_CONSUMER, opts, dict(ctx, target_min=44 if touch else U.PRESET_CONSUMER["target_min"]))
                    rm = U.run_checks(data, PRESET_MARKETING, opts, ctx)
                    apply_profile(rm, data, ctx)
                    add_mkt(rm, data, extra, ctx, a.level, a.allow, fonts, shot, None)
                    if a.tab and not touch and motion != "reduce" and w >= 1000:
                        U.check_focus(page, rm, PRESET_MARKETING, a.tab)
                        for f in rm.findings:
                            if f["id"].startswith("G") and f["id"] != "G1":
                                rc.findings.append(dict(f))
                    if a.hover and not touch and motion != "reduce" and w >= 1000:
                        U.check_hover(page, rm, PRESET_MARKETING, data["rows"], viewport_h=h)
                    rc.context["viewport"] = rm.context["viewport"] = ctx["viewport"]
                    reps_c.append(rc)
                    reps_m.append(rm)
                    runs.append(tag)
                    raw[tag] = {"extra": extra, "meta": {k: v for k, v in data["meta"].items() if k != "text"}, "rows": len(data["rows"])}
                    context.close()
                if not a.no_mobile:
                    context = browser.new_context(viewport={"width": 360, "height": 780}, device_scale_factor=2, has_touch=True, is_mobile=True, locale=a.locale)
                    page = context.new_page()
                    try:
                        page.goto(url, wait_until="load", timeout=a.timeout)
                        page.wait_for_timeout(min(a.wait, 1500))
                        narrow = page.evaluate(NARROW_JS)
                    except Exception as e:
                        raw.setdefault("errors", []).append(f"360: {str(e)[:120]}")
                    context.close()
                    runs.append("light/360x780/touch (ширина)")
                    raw["narrow360"] = narrow
                    if narrow and reps_m:
                        rep_mob = next((r for r in reps_m if r.context.get("touch")), reps_m[0])
                        G = "Раскладка (маркетинг)"
                        over = narrow["scrollW"] - narrow["innerW"]
                        rep_mob.add("MKT-J1", G, "Нет горизонтальной прокрутки на 360 px", f"{narrow['scrollW']} против {narrow['innerW']}",
                                    "scrollWidth ≤ innerWidth + 2", over <= 2, SEV_B, [],
                                    "site SG-MOB-01 различает расширение области (B) и скрытое переполнение (D)")
                        rep_mob.findings[-1].update(profile="new", base="D (волна 1: автопроверка на 360); site SG-MOB-01")
                browser.close()
    finally:
        if srv:
            srv.shutdown()
    if normal_rows and reduced_rows:
        for reps, prof in ((reps_c, False), (reps_m, True)):
            extra_rep = U.Report(target, "marketing" if prof else "consumer", {"scheme": "light", "viewport": "reduced"})
            U.check_reduced(normal_rows, reduced_rows, extra_rep)
            if prof:
                for f in extra_rep.findings:
                    pr = PROFILE.get(f["id"])
                    f["profile"] = pr["action"] if pr else "keep"
                    f["base"] = pr["base"] if pr else KEEP_NOTE
                    if pr and pr["action"] == "severity":
                        f["severity"] = pr["sev"]
            reps.append(extra_rep)
    return U.merge_reports(reps_c), U.merge_reports(reps_m), runs, raw


# =====================================================================================================================
# 8. Сравнение и отчёт
# =====================================================================================================================
def compare(fc, fm):
    """Проверки ui_audit, давшие FAIL блокер/серьёзно в consumer, и что с ними стало в marketing (на тех же прогонах)."""
    idx = {(f["id"], f["run"]): f for f in fm}
    rows, serious_c, removed = [], 0, 0
    for f in fc:
        if f["verdict"] != "FAIL" or f["severity"] not in (SEV_B, SEV_S):
            continue
        serious_c += 1
        g = idx.get((f["id"], f["run"]))
        still = bool(g and g["verdict"] == "FAIL" and g["severity"] in (SEV_B, SEV_S))
        if not still:
            removed += 1
        rows.append({"id": f["id"], "run": f["run"], "consumer": f"{f['found']} / {f['threshold']} / {f['severity']}",
                     "marketing": (f"{g['found']} / {g['threshold']} / {g['verdict']} {g['severity']}" if g else "—"),
                     "still_serious": still, "action": (g or {}).get("profile", "keep")})
    new_serious = [f for f in fm if f["verdict"] == "FAIL" and f["severity"] in (SEV_B, SEV_S) and f.get("profile") == "new"]
    return {"consumer_serious_fail": serious_c, "removed_by_profile": removed, "kept": serious_c - removed,
            "marketing_new_serious": len(new_serious), "rows": rows,
            "marketing_serious_fail": len([f for f in fm if f["verdict"] == "FAIL" and f["severity"] in (SEV_B, SEV_S)])}


def render(target, level, runs, fm, cmp_, raw):
    fails = [f for f in fm if f["verdict"] == "FAIL"]
    by = Counter(f["severity"] for f in fails)
    L = [f"# Визуальный QA, профиль marketing: {os.path.basename(target.rstrip('/')) or target}", "",
         f"Инструмент: `99-raw/tools/marketing_audit.py` ({VERSION}) поверх `ui_audit.py`. Уровень: **{level}**. "
         f"Chromium {raw.get('browser', '?')}. Прогоны: {', '.join(runs)}.", "",
         f"**Итог marketing: FAIL {len(fails)} — блокеров {by.get(SEV_B, 0)}, серьёзных {by.get(SEV_S, 0)}, полировки {by.get(SEV_D, 0)}.** "
         f"Consumer на тех же данных: серьёзных и блокеров {cmp_['consumer_serious_fail']}, из них профиль снял {cmp_['removed_by_profile']} "
         f"(оставил {cmp_['kept']}); новых серьёзных MKT и примет: {cmp_['marketing_new_serious']}.", ""]
    if fails:
        L += ["## Что править (правило → найдено → порог → где; повторы по прогонам свёрнуты)", "", "```text"]
        for sev in (SEV_B, SEV_S, SEV_D):
            for f in [x for x in dedup_fails(fm) if x["severity"] == sev]:
                where = ("; ".join(e for e in (f.get("examples") or []) if e)[:150] or "") + f" [{', '.join(r.split('/', 1)[-1] for r in f['runs'])}]"
                L.append(f"[{BSD[sev]}] {f['id']:<24} → {str(f['found'])[:48]} → {str(f['threshold'])[:40]} → {where}")
        L += ["```", ""]
    L += ["## Consumer → marketing (FAIL блокер/серьёзно в consumer)", "", "| Проверка | Прогон | consumer (найдено / порог / серьёзность) | marketing | Осталась серьёзной | Действие профиля |",
          "|---|---|---|---|---|---|"]
    for r in cmp_["rows"]:
        L.append(f"| {r['id']} | {r['run']} | {r['consumer']} | {r['marketing']} | {'да' if r['still_serious'] else 'нет'} | {r['action']} |")
    L.append("")
    groups = defaultdict(list)
    for f in fm:
        groups[f["group"]].append(f)
    order = U.GROUP_ORDER + ["Типографика (маркетинг)", "Цвет (маркетинг)", "Движение (маркетинг)", "Раскладка (маркетинг)", "Приметы клише"]
    for g in order:
        if g not in groups:
            continue
        L += [f"## {g}", "", "| # | Правило | Найдено | Порог | Вердикт | Серьёзность | Прогон | Профиль |", "|---|---|---|---|---|---|---|---|"]
        for f in groups[g]:
            L.append(f"| {f['id']} | {f['rule']} | {f['found']} | {f['threshold']} | {f['verdict']} | {f['severity']} | {f['run']} | {f.get('profile', 'keep')} |")
        det = [f for f in groups[g] if f["verdict"] != "OK" and any(f.get("examples") or [])]
        for f in det:
            L.append(f"- **{f['id']}** ({f['run']}): " + "; ".join(f"`{e}`" for e in f["examples"] if e)[:600])
            if f.get("note"):
                L.append(f"  - примечание: {f['note']}")
        L.append("")
    return "\n".join(L)


def dedup_fails(fm):
    """FAIL без повторов по прогонам: одна строка на (id, найдено); прогоны — в поле runs."""
    seen, out = {}, []
    for f in fm:
        if f["verdict"] != "FAIL":
            continue
        key = (f["id"], str(f["found"]))
        if key in seen:
            seen[key]["runs"].append(f["run"])
            continue
        g = dict(f)
        g["runs"] = [f["run"]]
        seen[key] = g
        out.append(g)
    return out


def fix_text(target, fm):
    fails = dedup_fails(fm)
    out = [f"ОТЧЁТ ПРОВЕРОК (правило → найдено → порог → где) · {target} · профиль marketing · {time.strftime('%Y-%m-%d %H:%M')}"]
    for sev in (SEV_B, SEV_S, SEV_D):
        for f in [x for x in fails if x["severity"] == sev]:
            where = ("; ".join(e for e in (f.get("examples") or []) if e)[:200] or "") + f" [{', '.join(f['runs'])}]"
            out.append(f"  [{BSD[sev]}] {f['id']:<24} → {str(f['found'])[:60]} → {str(f['threshold'])[:48]} → {where}")
    if len(out) == 1:
        out.append("  нарушений нет")
    return "\n".join(out) + "\n"


def profile_md():
    L = ["| Проверка ui_audit | Порог consumer (код) | На лендинге | Профиль marketing | Серьёзность | Основание |", "|---|---|---|---|---|---|"]
    for cid, p in PROFILE.items():
        L.append(f"| {cid} | см. `ui_audit.py` | {p['landing']} | {p['action']}: {p['threshold']} | {p['sev']} | {p['base']} |")
    return "\n".join(L)


# =====================================================================================================================
# 9. Самопроверка без браузера
# =====================================================================================================================
def _row(i, **kw):
    base = dict(i=i, tag="div", sel=f"div.n{i}", role="", x=0, y=0, w=200, h=40, pt=None, pr=None, pb=None, pl=None, mt=None, mr=None,
                mb=None, ml=None, rg=None, cg=None, r1=None, r2=None, r3=None, r4=None, bw=None, bwr=None, bwb=None, bwl=None, sh=None,
                z=None, bd=None, fs=16, lh=24, fw=400, ls=0, ff="Golos Text", fvn="normal", tt="none", ta="start", col="#111111", cola=1,
                bg="#ffffff", bggrad=False, bgguess=False, bcol=None, bcola=0, ow=0, ost="none", oc=None, pos="static", ov="visible visible",
                mw=None, gtc=None, tp="all", td="0s", an="none", txt="", inter=False, disp="block", dis=False, inflow=False, par=None,
                svg=None, inline="")
    base.update(kw)
    return base


def selftest():
    ok = True

    def check(name, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'OK  ' if good else 'FAIL'} {name}: {got!r}" + ("" if good else f" (ожидалось {want!r})"))

    # пресет: те же ключи, что у consumer
    check("пресет marketing: ключи как у consumer", set(PRESET_MARKETING) == set(U.PRESET_CONSUMER), True)
    check("профиль: все id есть в каталоге ui_audit (кроме F1)", all(re.fullmatch(r"[A-M]\d+b?", k) for k in PROFILE), True)
    check("chromatic_hues: красный, синий, серый", len(chromatic_hues(["#e53935", "#1e40ff", "#777777", "#ffffff"])), 2)
    check("chromatic_hues: два близких синих = 1", len(chromatic_hues(["#1e40ff", "#2a4dff"])), 1)
    check("rgb_css_to_hex", rgb_css_to_hex("rgba(43, 59, 255, 0.35)"), ("#2b3bff", 0.35))
    fonts = load_font_metrics()
    check("cyrillic-display-fonts.yaml читается (≥ 10 гарнитур)", len(fonts) >= 10, True)
    # синтетический лендинг: display 96/64/48, секции 120/160, CTA 56, glow, z-index 9999, колонка-картинка 400×900
    rows = [
        _row(0, tag="header", y=0, w=1440, h=72, pt=16, pb=16, pl=48, pr=48),
        _row(1, tag="h1", y=180, w=1000, h=210, fs=96, lh=100.8, fw=700, ff="Onest", txt="Страховка для бизнеса без очередей", par=2),
        _row(2, tag="section", y=100, w=1440, h=800, pt=160, pb=160, gtc="1fr 1fr"),
        _row(3, tag="button", inter=True, y=600, w=220, h=56, txt="Рассчитать", sh="rgba(43, 59, 255, 0.35) 0px 0px 24px 0px",
             r1=9999, r2=9999, r3=9999, r4=9999),
        _row(4, tag="a", inter=True, y=20, w=120, h=40, txt="Войти", r1=8, r2=8, r3=8, r4=8),
        _row(5, tag="h2", y=1000, w=900, h=70, fs=64, lh=67, fw=700, ff="Onest", txt="Как это работает"),
        _row(6, tag="p", y=1100, w=700, h=60, fs=18, lh=28, txt="Три шага: заявка, осмотр, полис. Ничего лишнего и без визита в офис страховой."),
        _row(7, tag="section", y=1000, w=1440, h=900, pt=120, pb=120, mt=0),
        _row(8, tag="div", x=0, y=0, w=400, h=900, bg="#dddddd"),                       # колонка-картинка → J2 у consumer
        _row(9, tag="canvas", y=0, w=1440, h=900, z=-1),
        _row(10, tag="div", y=0, w=40, h=40, z=9999),
        _row(11, tag="h3", y=1300, w=400, h=40, fs=48, lh=50, fw=700, ff="Onest", txt="Шаг первый"),
        _row(12, tag="p", y=1400, w=400, h=40, fs=20, lh=30, txt="Короткое пояснение к шагу.", ff="JetBrains Mono"),
    ]
    data = {"rows": rows, "meta": {"lang": "ru", "scrollW": 1440, "innerW": 1440, "innerH": 900, "bodyBg": "rgb(255,255,255)",
                                   "title": "t", "text": "Страховка для бизнеса", "viewportMeta": "", "styleSheets": 1}}
    opts = SimpleNamespace(strict_border=False, tokens_set=None)
    ctx = {"target": "synthetic", "scheme": "light", "viewport": "1440x900", "motion": "no-preference", "touch": False, "target_min": 24}
    rc = U.run_checks(data, U.PRESET_CONSUMER, opts, ctx)
    rm = apply_profile(U.run_checks(data, PRESET_MARKETING, opts, ctx), data, ctx)
    fc = {f["id"]: f for f in rc.findings}
    fmk = {f["id"]: f for f in rm.findings}
    check("consumer H2 FAIL серьёзно (display 96/64/48)", (fc["H2"]["verdict"], fc["H2"]["severity"]), ("FAIL", SEV_S))
    check("marketing H2 OK", fmk["H2"]["verdict"], "OK")
    check("consumer A1 FAIL серьёзно (секции 120/160)", (fc["A1"]["verdict"], fc["A1"]["severity"]), ("FAIL", SEV_S))
    check("marketing A1 OK", fmk["A1"]["verdict"], "OK")
    check("consumer B2 FAIL (CTA 56)", fc["B2"]["verdict"], "FAIL")
    check("marketing B2 OK", fmk["B2"]["verdict"], "OK")
    check("consumer D4 FAIL серьёзно (glow-CTA)", (fc["D4"]["verdict"], fc["D4"]["severity"]), ("FAIL", SEV_S))
    check("marketing D4 OK (1 свечение)", fmk["D4"]["verdict"], "OK")
    check("consumer E1 FAIL серьёзно (z -1, 9999)", (fc["E1"]["verdict"], fc["E1"]["severity"]), ("FAIL", SEV_S))
    check("marketing E1 → полировка", fmk["E1"]["severity"], SEV_D)
    check("consumer J2 FAIL серьёзно (колонка 400)", (fc["J2"]["verdict"], fc["J2"]["severity"]), ("FAIL", SEV_S))
    check("marketing J2 информативно", fmk["J2"]["verdict"], "WARN")
    cmp_ = compare(U.merge_reports([rc]), U.merge_reports([rm]))
    check("сравнение: все серьёзные consumer сняты профилем", cmp_["kept"], 0)
    # MKT: clamp 40→160 (×4) и 32→64 (×2), H1 3 строки при 1440, трекинг Onest −0,04 < −0,025, висячий предлог
    extra = {"css": {"clamps": [{"where": "h1", "val": "clamp(40px, 8vw, 160px)", "min": 40, "max": 160, "ratio": 4.0},
                                {"where": "h2", "val": "clamp(2rem, 4vw, 4rem)", "min": 32, "max": 64, "ratio": 2.0}],
                     "sheetsBlocked": 0, "prm": {"reduce": 0, "noPref": 1}},
             "h1": [{"sel": "h1", "text": "Страховка для бизнеса без очередей", "lines": 3, "fs": 96}],
             "display": [{"sel": "h1", "fs": 96, "lh": 1.05, "ls": -0.04, "ff": "Onest", "caps": False, "cyr": True, "text": "Страховка",
                          "hang": ["без ⏎ очередей"], "y": 180}],
             "anims": [{"target": "div.ticker", "name": "marquee", "dur": 20000, "delay": 0, "iter": "inf", "easing": "linear", "kfEase": ["linear"],
                        "props": ["transform"], "state": "running", "timeline": "DocumentTimeline", "inView": True, "size": 60, "type": "CSSAnimation"},
                       {"target": "div.card", "name": "grow", "dur": 600, "delay": 0, "iter": 1, "easing": "ease", "kfEase": [], "props": ["height"],
                        "state": "finished", "timeline": "DocumentTimeline", "inView": True, "size": 100, "type": "CSSAnimation"},
                       {"target": "details.acc", "tag": "details", "pseudo": "::details-content", "name": "block-size", "dur": 250, "delay": 0, "iter": 1,
                        "easing": "ease", "kfEase": [], "props": ["blockSize", "contentVisibility"], "state": "running", "timeline": "DocumentTimeline",
                        "inView": True, "size": 64, "type": "CSSTransition"}],
             "reveal": {"blocks": 6, "textBelow": 30, "hidden": 12, "groups": [{"sig": "ty40|0.6s|none", "n": 10, "blocks": 5, "ex": ["div.reveal"]}]},
             "pause": [], "videos": [], "cliche": {"headings": 6, "eyebrows": 4, "mono": [], "accent": [], "splitH": [], "gradText": [],
                                                   "blobs": [], "glassFirst": [], "bento": [], "pill": None, "grads": []}}
    add_mkt(rm, data, extra, ctx, "L1", set(), fonts)
    fmk = {f["id"]: f for f in rm.findings}
    check("MKT-T1 находит clamp ×4", (fmk["MKT-T1"]["verdict"], fmk["MKT-T1"]["found"].split()[0]), ("FAIL", "1"))
    check("MKT-T2: 3 строки H1 при 1440 → FAIL", fmk["MKT-T2"]["verdict"], "FAIL")
    check("MKT-T3: трекинг Onest −0,04 → FAIL", fmk["MKT-T3"]["verdict"], "FAIL" if "onest" in fonts else "OK")
    check("MKT-T5: висячий «без»", fmk["MKT-T5"]["verdict"], "FAIL")
    check("MKT-M1: одинаковое появление в 5 из 6 блоков → FAIL серьёзно", (fmk["MKT-M1"]["verdict"], fmk["MKT-M1"]["severity"]), ("FAIL", SEV_S))
    check("MKT-M2: анимация height", fmk["MKT-M2"]["verdict"], "FAIL")
    check("MKT-M2: аккордеон <details> не считается (X-11)", str(fmk["MKT-M2"]["found"]).split()[0], "1")
    check("MKT-M5: петля без паузы → FAIL", fmk["MKT-M5"]["verdict"], "FAIL")
    check("cliche:caps-eyebrow 4 из 6 > 2 → FAIL", fmk["cliche:caps-eyebrow"]["verdict"], "FAIL")
    rm2 = apply_profile(U.run_checks(data, PRESET_MARKETING, opts, ctx), data, ctx)
    add_mkt(rm2, data, extra, ctx, "L1", {"cliche:caps-eyebrow"}, fonts)
    check("--allow снимает примету", {f["id"]: f for f in rm2.findings}["cliche:caps-eyebrow"]["verdict"], "OK")
    try:
        from PIL import Image
        b = io.BytesIO()
        Image.new("RGB", (100, 100), (124, 58, 237)).save(b, "PNG")
        check("oklch_share: фиолетовый #7c3aed → 100 %", oklch_share(b.getvalue()), 100.0)
    except Exception as e:
        check("oklch_share", str(e), "ok")
    txt = fix_text("synthetic", U.merge_reports([rm]))
    check("fix.txt: формат «→»", txt.count("→") >= 3, True)
    print(f"\n{VERSION}: профиль {len(PROFILE)} строк; ui_audit групп {len(U.GROUP_ORDER)}")
    return 0 if ok else 1


# =====================================================================================================================
# 10. CLI
# =====================================================================================================================
def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("target", nargs="?")
    p.add_argument("--level", default="L1", choices=LEVELS)
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--name")
    p.add_argument("--viewport", action="append", default=[])
    p.add_argument("--no-mobile", action="store_true")
    p.add_argument("--no-reduced", action="store_true")
    p.add_argument("--tab", type=int, default=20)
    p.add_argument("--hover", action="store_true")
    p.add_argument("--allow", default="")
    p.add_argument("--fail-on", choices=["blocker", "serious", "any"])
    p.add_argument("--wait", type=int)
    p.add_argument("--timeout", type=int, default=60000)
    p.add_argument("--max-elements", type=int, default=4000)
    p.add_argument("--locale", default="ru-RU")
    p.add_argument("--no-lock", action="store_true")
    p.add_argument("--root", help="корень раздачи локальной страницы (по умолчанию — по ссылкам ../ в HTML)")
    p.add_argument("--batch")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--profile-md", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    a = p.parse_args()
    if a.help or (not a.target and not a.batch and not a.selftest and not a.profile_md):
        print(__doc__)
        return 0
    if a.selftest:
        return selftest()
    if a.profile_md:
        print(profile_md())
        return 0
    a.viewports = [tuple(int(x) for x in v.lower().split("x")) for v in (a.viewport or ["1440x900"])]
    a.allow = {x.strip() if x.strip().startswith("cliche:") else "cliche:" + x.strip() for x in a.allow.split(",") if x.strip()}
    fonts = load_font_metrics()
    jobs = []
    if a.batch:
        for ln in open(a.batch, encoding="utf-8"):
            if not ln.strip() or ln.startswith("#"):
                continue
            parts = ln.rstrip("\n").split("\t")
            jobs.append((parts[0].strip(), (parts[1].strip() if len(parts) > 1 and parts[1].strip() in LEVELS else a.level),
                         parts[2].strip() if len(parts) > 2 and parts[2].strip() else None))
    else:
        jobs.append((a.target, a.level, a.name))
    worst = None
    wait_user = a.wait
    for target, level, name in jobs:
        a.level = level
        a.wait = wait_user if wait_user is not None else (2500 if re.match(r"^https?://", target) else 1200)
        name = name or re.sub(r"[^A-Za-z0-9._-]+", "_", re.sub(r"^https?://", "", target).strip("/"))[:60] or "page"
        t0 = time.time()
        try:
            fc, fm, runs, raw = audit_pair(target, a, fonts)
        except SystemExit:
            raise
        except Exception as e:
            print(f"ошибка: {target}: {e}", file=sys.stderr)
            if not a.batch:
                return 2
            continue
        cmp_ = compare(fc, fm)
        md = render(target, level, runs, fm, cmp_, raw)
        os.makedirs(a.out, exist_ok=True)
        base = os.path.join(a.out, name)
        open(base + ".marketing.md", "w", encoding="utf-8").write(md)
        open(base + ".fix.txt", "w", encoding="utf-8").write(fix_text(target, fm))
        json.dump({"tool": VERSION, "target": target, "level": level, "date": time.strftime("%Y-%m-%d %H:%M"), "runs": runs,
                   "seconds": round(time.time() - t0, 1), "compare": cmp_, "findings_marketing": fm, "findings_consumer": fc, "raw": raw},
                  open(base + ".marketing.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
        fails = [f for f in fm if f["verdict"] == "FAIL"]
        if fails:
            sev = min(U.SEV_ORDER[f["severity"]] for f in fails)
            worst = sev if worst is None else min(worst, sev)
        summ = {"target": target, "level": level, "consumer_serious": cmp_["consumer_serious_fail"], "removed": cmp_["removed_by_profile"],
                "marketing_serious": cmp_["marketing_serious_fail"], "new_serious": cmp_["marketing_new_serious"],
                "fails": dict(Counter(BSD[f["severity"]] for f in fails)), "s": round(time.time() - t0, 1)}
        if not a.quiet:
            print(md if not a.batch else json.dumps(summ, ensure_ascii=False))
        else:
            print(json.dumps(summ, ensure_ascii=False))
        print(f"→ {base}.marketing.md\n→ {base}.marketing.json\n→ {base}.fix.txt", file=sys.stderr)
    if a.fail_on and worst is not None and worst <= {"blocker": 0, "serious": 1, "any": 2}[a.fail_on]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
