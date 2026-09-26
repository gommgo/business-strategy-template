#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""copy_extract.py — страница (URL или сохранённый HTML) → структурированный текст по слотам (JSON).

text-research · волна 1 · агент D · 2026-09-24. Метод — 03-corpus-measured/01-corpus-method.md §4.

Два шага.
  1) Браузер (Playwright/Chromium, одна страница за раз): загрузка, медленная прокрутка до конца и назад, затем в
     странице собираются видимые текстовые блоки: текст (без text-transform), тег, уровень заголовка, ориентиры
     (header/nav/main/article/aside/footer/form), ссылка или кнопка, координаты в документе, кегль, насыщенность,
     text-transform, трекинг, фон и скругление (кнопка), верхнеуровневая секция. Пропускаются script/style/svg/iframe,
     скрытое (checkVisibility), клоны каруселей, aria-hidden, фиксированные слои не у верха (cookie, чаты, модалки,
     бейдж хостинга Kimi). Cookie-баннеры НЕ нажимаются. Мета, OG, JSON-LD — отдельно.
  2) Классификация в Python (перезапускается офлайн по сохранённым блокам, --reclassify): hero (надзаголовок, H1,
     подзаголовок, кнопки, микродоказательство), секции по заголовкам H2 (или визуальным заголовкам, если тегов мало),
     роль секции по словарю, слоты из временного словаря 99-raw/notes/temp-vocabulary-v0.yaml (headline,
     section-title, card-title, card-body, list-item, testimonial-quote, faq-q, faq-a, pricing-*, stat-*, cta-label,
     form-*, nav-label, article-*…), отзывы, FAQ.

Выход JSON: tool, version, date, page{url, final_url, status, title, html_lang, blocked, insecure, fetched_at,
viewport, hash}, lang, meta{title, description, og_title, og_description, og_image_alt, og_site_name, canonical,
twitter_title, twitter_description}, hero{eyebrow, headline, subheadline, cta[], proof[]}, sections[{index, heading,
level, eyebrow, role_guess, texts[], ctas[]}], testimonials[{quote, attribution}], faq[{q, a}], jsonld[{type, text}],
units[{slot_type, text, section, role, tag, y, above_fold}], stats{…}. Рядом (с --save-blocks) — *.blocks.json.

Запуск:
  python3 99-raw/tools/copy_extract.py URL [-o out.json] [--genre landing|site-page|article] [--lang ru|en]
          [--md out.md] [--shot shot.jpg] [--save-blocks] [--lock] [--insecure] [--wait 1200] [--timeout 45]
  python3 99-raw/tools/copy_extract.py --html saved.html [--base-url URL] -o out.json
  python3 99-raw/tools/copy_extract.py --reclassify out.blocks.json -o out.json [--genre …]
  python3 99-raw/tools/copy_extract.py --batch targets.tsv --outdir DIR [--skip-existing] [--lock]
          (TSV с колонками id, url, genre, lang[, page_type]; строки с # пропускаются)
  python3 99-raw/tools/copy_extract.py --selftest

--lock — браузер только под двумя блокировками: общая $DDD_HOME/locks/browser.lock, затем своя
$DDD_HOME/locks/text/browser.lock (ожидание до 900 с); перед страницей проверяется MemAvailable (< 2 ГБ — ожидание).
Ограничения: эвристики, а не разметка человеком (ручная проверка — опыт D/02); страницы за антиботом отмечаются
page.blocked; A/B-варианты и гео (VPN) меняют текст; один прогон.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

VERSION = "0.3.0"
DATE = "2026-09-24"
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = kbpaths.kb("text")
VOCAB_PATH = ROOT / "99-raw" / "notes" / "temp-vocabulary-v0.yaml"
GLOBAL_LOCK = Path(kbpaths.lock_path("browser"))
LOCAL_LOCK = Path(kbpaths.lock_path("browser", "text"))
UA_TMPL = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major}.0.0.0 "
           "Safari/537.36")
VW, VH = 1440, 900

# ---------------------------------------------------------------------------------------------------------------------
# 1. Сбор блоков в странице
# ---------------------------------------------------------------------------------------------------------------------
BLOCKS_JS = r"""
() => {
  const VH = innerHeight, VW = innerWidth;
  const SKIP = new Set(['SCRIPT','STYLE','NOSCRIPT','TEMPLATE','SVG','IFRAME','CANVAS','VIDEO','AUDIO','OBJECT','EMBED',
                        'SELECT','OPTION','TEXTAREA','MATH','HEAD','META','LINK','DIALOG']);
  const BLOCKY = new Set(['block','flex','grid','list-item','table','table-cell','table-row','table-caption','flow-root',
                          'inline-table']);
  const BOXY = new Set(['inline-block','inline-flex','inline-grid']);
  const JUNK = /(^|[\s_-])(cookie|cookies|onetrust|cookiebot|usercentrics|didomi|trustarc|gdpr|cc-banner|cc-window|jivo|jdiv|livechat|chat-widget|b24-widget|bx-livechat|tawk|crisp-client|drift-|intercom-|carrotquest|kimi-badge|sdk-seed|tilda-cookie|t-cookie|wm-ipp|wm-toolbar|donato|wb-autocomplete)/i;
  const CLONE = /(slick-cloned|swiper-slide-duplicate|splide__slide--clone|glide__slide--clone|owl-item cloned|marquee-clone|is-clone)/i;
  const csCache = new Map();
  const cs = el => { let v = csCache.get(el); if (!v) { v = getComputedStyle(el); csCache.set(el, v); } return v; };
  const clsOf = el => (typeof el.className === 'string' ? el.className : (el.getAttribute && el.getAttribute('class')) || '');
  // корень содержимого: main или body; спуск по единственной большой обёртке
  let root = document.querySelector('main') || document.body;
  if (root === document.body) {
    for (let k = 0; k < 6; k++) {
      const kids = Array.from(root.children).filter(c => !SKIP.has(c.tagName) && c.getBoundingClientRect().height > 50);
      if (kids.length === 1 && kids[0].getBoundingClientRect().height > 0.5 * document.documentElement.scrollHeight) root = kids[0]; else break;
    }
  }
  const topIdx = new Map(); Array.from(root.children).forEach((c, i) => topIdx.set(c, i));
  function topOf(el) { let c = el; while (c && c.parentElement && c.parentElement !== root) c = c.parentElement; return (c && topIdx.has(c)) ? topIdx.get(c) : -1; }
  function rejectEl(el) {
    if (SKIP.has(el.tagName)) return true;
    if (el.getAttribute('aria-hidden') === 'true') return true;
    if (el.hidden) return true;
    const c = clsOf(el) + ' ' + (el.id || '');
    if (CLONE.test(c)) return true;
    if (JUNK.test(c)) return true;
    if (el.checkVisibility && !el.checkVisibility({checkVisibilityCSS: true})) return true;
    const st = cs(el);
    if (st.display === 'none' || st.visibility === 'hidden') return true;
    if (st.position === 'fixed') {
      const r = el.getBoundingClientRect();
      const modal = el.getAttribute('role') === 'dialog' || el.getAttribute('aria-modal') === 'true' ||
                    /(modal|popup|pop-up|overlay|dialog|lightbox|cookie|consent|banner-bottom|chat)/i.test(c);
      if (modal) return true;                                  // модалки, попапы, cookie
      if (r.top > 120 && r.height < 0.45 * VH) return true;    // нижние полосы, чаты, бейджи (Kimi)
    }
    return false;
  }
  const regIds = new Map(); let regN = 0;
  function regionOf(el) {   // ближайший крупный предок (≥ 250×400): для поиска плотных «макетов интерфейса»
    let c = el;
    while (c && c !== document.body) {
      if (regIds.has(c)) return regIds.get(c);
      const r = c.getBoundingClientRect();
      if (r.height >= 250 && r.width >= 400) { regIds.set(c, ++regN); return regN; }
      c = c.parentElement;
    }
    return 0;
  }
  const PROMO = /(^|[\s_-])(promo|banner|advert|adv|ads?|teaser|related|recommend\w*|subscri\w*|widget|sponsor\w*|native|incut|inset-card|product-card|lead-magnet|read-also|readalso|see-also|more-articles|comments?)([\s_-]|$)/i;
  const promoCache = new Map();
  function promoOf(el) {
    let c = el, k = 0;
    while (c && c !== document.body && k < 10) {
      if (promoCache.has(c)) return promoCache.get(c);
      const m = PROMO.exec(clsOf(c) + ' ' + (c.id || ''));
      if (m) { promoCache.set(c, m[2].toLowerCase()); return m[2].toLowerCase(); }
      c = c.parentElement; k++;
    }
    return '';
  }
  const groups = new Map(); const order = [];
  function groupOf(el) {
    const h = el.closest('h1,h2,h3,h4,h5,h6,[role=heading]');
    if (h) return h;
    let cur = el;
    while (cur && cur !== document.body && cur !== document.documentElement) {
      const tg = cur.tagName;
      if (tg === 'BUTTON' || tg === 'P' || tg === 'LI' || tg === 'LABEL' || tg === 'SUMMARY' || tg === 'DT' || tg === 'DD'
          || tg === 'TD' || tg === 'TH' || tg === 'FIGCAPTION' || tg === 'BLOCKQUOTE' || tg === 'CAPTION' || tg === 'LEGEND') return cur;
      const d = cs(cur).display;
      if (BLOCKY.has(d)) return cur;
      if (BOXY.has(d) && (tg === 'A' || cur.getAttribute('role') === 'button')) return cur;
      cur = cur.parentElement;
    }
    return document.body;
  }
  function addText(n) {
    const p = n.parentElement || (n.parentNode && n.parentNode.host); if (!p) return;
    const g = groupOf(p);
    let rec = groups.get(g);
    if (!rec) { rec = {el: g, t: ''}; groups.set(g, rec); order.push(g); }
    let piece = n.nodeValue;
    if (rec.t && rec.lastP && rec.lastP !== p && !/\s$/.test(rec.t) && !/^\s/.test(piece)) {
      const d1 = cs(p).display, d2 = cs(rec.lastP).display;
      if (BOXY.has(d1) || BOXY.has(d2) || BLOCKY.has(d1) || BLOCKY.has(d2) || /[.!?:;,»”)]$/.test(rec.t)) piece = ' ' + piece;
    }
    rec.t += piece; rec.lastP = p;
  }
  let shadowHosts = 0;
  function visit(node, depth) {
    if (depth > 200) return;
    for (let c = node.firstChild; c; c = c.nextSibling) {
      if (c.nodeType === 3) { if (/\S/.test(c.nodeValue)) addText(c); continue; }
      if (c.nodeType !== 1) continue;
      if (rejectEl(c)) continue;
      if (c.tagName === 'BR') { const pe = c.parentElement; if (pe) { const rec = groups.get(groupOf(pe)); if (rec) rec.t += ' '; } continue; }
      if (c.tagName === 'INPUT') {
        if (/^(submit|button)$/i.test(c.type || '') && c.value) { groups.set(c, {el: c, t: c.value}); order.push(c); }
        continue;
      }
      if (c.shadowRoot) { shadowHosts++; visit(c.shadowRoot, depth + 1); }
      visit(c, depth + 1);
    }
  }
  visit(document.body, 0);
  const out = [];
  let idx = 0;
  for (const g of order) {
    const rec = groups.get(g);
    const text = rec.t.replace(/\s+/g, ' ').trim();
    if (!text) continue;
    const el = rec.el;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const st = cs(el);
    const tag = el.tagName.toLowerCase();
    let lvl = 0;
    const hm = /^h([1-6])$/.exec(tag);
    if (hm) lvl = +hm[1]; else if (el.getAttribute('role') === 'heading') lvl = +(el.getAttribute('aria-level') || 2);
    const a = el.closest('a');
    const isA = tag === 'a' || (a && el.contains(a) === false && a.contains(el) && (a.textContent || '').trim().length <= text.length + 2);
    const bg = st.backgroundColor;
    const hasBg = bg && bg !== 'transparent' && !/rgba\(\s*\d+,\s*\d+,\s*\d+,\s*0\s*\)/.test(bg);
    const border = parseFloat(st.borderTopWidth || '0') > 0 && st.borderTopStyle !== 'none';
    const isBtn = tag === 'button' || tag === 'input' || el.getAttribute('role') === 'button' ||
      (isA && (hasBg || border) && text.split(/\s+/).length <= 8 && parseFloat(st.paddingLeft || '0') >= 8) ||
      (isA && /(^|[\s_-])(btn|button|cta)([\s_-]|$)/i.test(clsOf(el) + ' ' + (a ? clsOf(a) : '')));
    out.push({
      i: idx++, t: text, tag, lvl, role: el.getAttribute('role') || '',
      hdr: !!el.closest('header,[role=banner]'), nav: !!el.closest('nav,[role=navigation]'),
      ftr: !!el.closest('footer,[role=contentinfo]'), form: !!el.closest('form'), main: !!el.closest('main,[role=main]'),
      art: !!el.closest('article'), aside: !!el.closest('aside'), li: !!el.closest('li'),
      bq: !!el.closest('blockquote,q'), fig: !!el.closest('figure,figcaption'), dl: !!el.closest('dl'), det: !!el.closest('details'),
      promo: promoOf(el), tab: !!el.closest('[role=tab],[role=tablist]'),
      btn: !!isBtn, a: !!isA, href: (tag === 'a' ? el.getAttribute('href') : (a ? a.getAttribute('href') : '')) || '',
      x: Math.round(r.left + scrollX), y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height),
      fs: parseFloat(st.fontSize) || 0, fw: parseInt(st.fontWeight) || 400, tt: st.textTransform,
      ls: parseFloat(st.letterSpacing) || 0, bg: !!hasBg, rad: parseFloat(st.borderTopLeftRadius) || 0, pos: st.position,
      cls: (clsOf(el) || '').slice(0, 80), id: (el.id || '').slice(0, 40), top: topOf(el), reg: regionOf(el),
      cur: st.cursor === 'pointer' && !(el.parentElement && cs(el.parentElement).cursor === 'pointer'),
      inert: !!el.closest('[inert]'),
      itp: (el.closest('[itemprop]') || {getAttribute: () => ''}).getAttribute('itemprop') || ''
    });
  }
  const metas = {};
  document.querySelectorAll('meta').forEach(m => {
    const k = (m.getAttribute('property') || m.getAttribute('name') || '').toLowerCase();
    if (k && !(k in metas)) metas[k] = (m.getAttribute('content') || '').trim();
  });
  const canon = document.querySelector('link[rel=canonical]');
  const ld = [];
  document.querySelectorAll('script[type="application/ld+json"]').forEach(s => { ld.push(s.textContent.slice(0, 60000)); });
  return {blocks: out, meta: metas, canonical: canon ? canon.href : '', title: document.title,
          html_lang: document.documentElement.lang || '', ld, doc_h: document.documentElement.scrollHeight,
          vw: VW, vh: VH, url: location.href, shadow_hosts: shadowHosts};
}
"""


def _mem_available_gb() -> float:
    try:
        for ln in open("/proc/meminfo"):
            if ln.startswith("MemAvailable:"):
                return int(ln.split()[1]) / 1024 / 1024
    except Exception:
        pass
    return 99.0


class Locks:
    """Две блокировки браузера: общая (все базы тройки), затем своя (text-research)."""

    def __init__(self, enabled: bool, wait: int = 900):
        self.enabled, self.wait, self.fds = enabled, wait, []

    def __enter__(self):
        if not self.enabled:
            return self
        for p in (GLOBAL_LOCK, LOCAL_LOCK):
            p.parent.mkdir(parents=True, exist_ok=True)
            fd = open(p, "a+")
            t0 = time.time()
            while True:
                try:
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.time() - t0 > self.wait:
                        raise SystemExit(f"copy_extract: блокировка {p} не получена за {self.wait} с")
                    time.sleep(2)
            self.fds.append(fd)
        return self

    def __exit__(self, *exc):
        for fd in reversed(self.fds):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
            except Exception:
                pass
        self.fds = []


def wait_memory(min_gb: float = 2.0, max_wait: int = 900) -> float:
    t0 = time.time()
    while True:
        m = _mem_available_gb()
        if m >= min_gb or time.time() - t0 > max_wait:
            return m
        print(f"copy_extract: MemAvailable {m:.1f} ГБ < {min_gb} — жду 120 с", file=sys.stderr)
        time.sleep(120)


BLOCK_TITLE_RX = re.compile(
    r"access denied|доступ ограничен|just a moment|attention required|performing security verification|"
    r"are you a robot|вы робот|проверка браузера|captcha|too many requests|forbidden|403|404 not found|"
    r"page not found|страница не найдена|ошибка 404|site can.t be reached|DDoS-Guard|checking your browser|"
    r"проблема с ip|access to this page has been denied|request unsuccessful|такой страницы нет|страница не существует|"
    r"page doesn.t exist|не найдена|ничего не найдено|страница удалена|this page could not be found", re.I)


def browse(url: str | None, html_path: str | None, lang_hint: str, wait_ms: int, timeout_s: int, insecure: bool,
           shot: str | None, base_url: str | None) -> dict:
    from playwright.sync_api import sync_playwright
    res = {"status": None, "insecure": False, "errors": []}
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled",
                                                    "--autoplay-policy=no-user-gesture-required"])
        major = b.version.split(".")[0]
        res["browser"] = b.version
        locale = "ru-RU" if lang_hint == "ru" else ("en-US" if lang_hint == "en" else "ru-RU")
        attempts = [insecure] if insecure else [False, True]
        data = None
        for ins in attempts:
            ctx = b.new_context(viewport={"width": VW, "height": VH}, user_agent=UA_TMPL.format(major=major),
                                locale=locale, ignore_https_errors=ins, reduced_motion="reduce",
                                extra_http_headers={"Accept-Language": "ru-RU,ru;q=0.9,en;q=0.7" if locale == "ru-RU"
                                                    else "en-US,en;q=0.9"})
            page = ctx.new_page()
            try:
                if html_path:
                    page.goto(Path(html_path).resolve().as_uri(), wait_until="load", timeout=timeout_s * 1000)
                    res["status"] = 200
                else:
                    resp = page.goto(url, wait_until="domcontentloaded", timeout=timeout_s * 1000)
                    res["status"] = resp.status if resp else None
                try:
                    page.wait_for_load_state("load", timeout=20000)
                except Exception:
                    pass
                try:
                    page.wait_for_load_state("networkidle", timeout=6000)
                except Exception:
                    pass
                page.wait_for_timeout(800)
                # медленная прокрутка: ленивые блоки и анимации «по появлению»
                try:
                    total = page.evaluate("document.documentElement.scrollHeight")
                    steps = max(6, min(45, int(total / 1100) + 2))
                    page.mouse.move(VW / 2, VH / 2)
                    for _ in range(steps):
                        page.mouse.wheel(0, 1100)
                        page.wait_for_timeout(220)
                    page.wait_for_timeout(700)
                    page.evaluate("window.scrollTo(0, 0)")
                    page.wait_for_timeout(wait_ms)
                except Exception as ex:
                    res["errors"].append(f"scroll: {str(ex)[:120]}")
                if shot:
                    try:
                        png = page.screenshot(type="jpeg", quality=45)
                        Path(shot).parent.mkdir(parents=True, exist_ok=True)
                        try:
                            from PIL import Image
                            import io
                            im = Image.open(io.BytesIO(png))
                            im = im.resize((im.width // 2, im.height // 2))
                            im.save(shot, "JPEG", quality=55)
                        except Exception:
                            Path(shot).write_bytes(png)
                    except Exception as ex:
                        res["errors"].append(f"shot: {str(ex)[:120]}")
                data = page.evaluate(BLOCKS_JS)
                res["insecure"] = ins
                ctx.close()
                break
            except Exception as ex:
                msg = str(ex)
                res["errors"].append(msg[:240])
                try:
                    ctx.close()
                except Exception:
                    pass
                if "ERR_CERT" in msg or "SSL" in msg or "certificate" in msg.lower():
                    continue
                break
        b.close()
    res["data"] = data
    return res


# ---------------------------------------------------------------------------------------------------------------------
# 2. Классификация
# ---------------------------------------------------------------------------------------------------------------------
WORD_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9]+(?:[-’'][A-Za-zА-Яа-яЁё0-9]+)*")


def nwords(t: str) -> int:
    return len(WORD_RE.findall(t))


def detect_lang(t: str) -> str:
    c = len(re.findall(r"[А-Яа-яЁё]", t))
    l = len(re.findall(r"[A-Za-z]", t))
    return "ru" if c >= l else "en"


# роль секции по заголовку (порядок важен: первое совпадение); \b — начало слова (Python 3 понимает кириллицу)
ROLE_RX = [
    ("faq", r"\bвопрос|\bfaq\b|\bчаст(ые|о задаваемые)|\bспрашива|\bquestions\b|\basked\b|q&a|\bчто нужно знать"),
    ("testimonials", r"\bотзыв|говорят о нас|клиенты о нас|\bрекомендаци|\btestimonial|\breviews?\b|\bwhat .*(say|think)|\blove (us|it)\b|customers say|истори[ия] клиент|wall of love"),
    ("pricing", r"\bтариф|\bцен[аыу]?\b|\bцены\b|\bстоимост|\bпрайс|сколько стоит|\bpricing\b|\bplans?\b|\bprices?\b"),
    ("how-it-works", r"как (мы )?(это )?работа|как проходит|\bэтап|\bшаг(и|ов|а)?\b|\bпроцесс|как заказать|как начать|порядок работ|how it works|how to get started|\bsteps?\b|\bprocess\b|in \d+ steps|get started in"),
    ("case-studies", r"\bкейс|\bпроекты\b|наши работы|\bпортфолио|примеры работ|результаты клиентов|case stud|success stor|customer stor|\bour work\b|\bportfolio\b"),
    ("benefits", r"почему (нам доверяют|выбирают|мы|стоит)|why (choose|us|teams)"),
    ("proof-logos", r"нам доверяют|наши клиенты|с нами работают|работаем с|\bпартн[её]р|trusted by|used by|loved by|\bcompanies\b|teams (use|trust)|join .* (teams|companies)"),
    ("proof-stats", r"в цифрах|\bцифры\b|факты о нас|by the numbers|in numbers"),
    ("guarantee", r"\bгаранти|вернём деньги|без риска|\bguarantee|risk[- ]free|money[- ]back|\bwarrant"),
    ("comparison", r"\bсравн|чем мы отлича|почему не\b|\bvs\.?\b|\bversus\b|\bcompare|\bcomparison\b|\balternative"),
    ("team", r"\bкоманд[аыу]?\b|\bспециалист|\bэксперт|\bмастер[ао]в?\b|\bврачи\b|\bпреподавател|наши люди|\bteam\b|\bexperts\b|people behind|\bleadership\b|\bfounders?\b"),
    ("about", r"\bо (нас|компании|студии|школе|клинике|бюро|проекте)\b|кто мы|наша история|\babout\b|our story|who we are|\bmission\b|\bмисси"),
    ("integrations", r"\bинтеграци|\bintegrat|connects? with|works with"),
    ("event-program", r"\bпрограмм[аы]\b|\bспикер|\bрасписан|\bагенда|\bprogram\b|\bagenda\b|\bspeakers\b|\bschedule\b|\bcurriculum\b|\bмодул"),
    ("awards-press", r"\bнагра|\bпресса\b|сми о нас|\bсертификат|\bлицензи|\bawards?\b|\bpress\b|as seen|featured in|\brecogni"),
    ("objections", r"\bсомнева|\bбоитесь|\bвозражени|почему нам можно доверять|why trust"),
    ("problem", r"\bпроблем|\bзнакомо\b|\bустали\b|\bбол(ь|и|ей)\b|\bтрудност|\bсложност|\bproblems?\b|\bstruggl|tired of|\bpain\b"),
    ("contacts", r"\bконтакт|\bадрес|как (нас )?найти|\bсвяжитесь|\bcontact\b|find us|get in touch|visit us"),
    ("lead-form", r"оставьте заявку|оставить заявку|\bзаявк|\bзапишитесь|\bзаписаться|получите (консультац|расч[её]т|смет)|\bрассчита|\bкалькулятор|\bформ[ау]\b|request a|book a|get a quote|sign up|\bsubscribe|join the waitlist|\bwaitlist\b"),
    ("benefits", r"\bпреимуществ|почему (мы|выбирают|нас)|\bвыгод|\bвозможност|что (вы )?получ|что входит|\bуслуги\b|\bfeatures?\b|\bbenefits\b|\bwhy\b|what you get|\bcapabilit|everything you need|built for"),
    ("product-demo", r"\bдемо|\bпосмотрите|как выглядит|\bинтерфейс|\bdemo\b|see it in action|\btour\b"),
    ("solution", r"\bрешени|мы предлагаем|что мы делаем|\bsolutions?\b|\bmeet\b|\bintroducing\b"),
    ("related", r"читайте также|\bпохожие|ещё по теме|\brelated\b|read more|more from|\brecommended\b|\bблог\b|\bстатьи\b|\bnews\b|\bновости\b|\binsights\b"),
    ("final-cta", r"\bготовы\b|\bначните\b|остались вопросы|\bпопробуйте|start (now|today|building|your)|ready to|get started|try .* free|let.s talk|\bjoin\b"),
]
ROLE_RX = [(r, re.compile(p, re.I)) for r, p in ROLE_RX]
LINK_RX = re.compile(r"^(подробнее|узнать (больше|подробнее|как)|читать (далее|дальше|полностью)|смотреть (все|всё|больше)|"
                     r"все (статьи|кейсы|отзывы|услуги|проекты|новости|работы)|ещё|показать (ещё|все)|перейти|"
                     r"learn more|read more|see (all|more|how)|view (all|more)|explore( all)?|more|details|show more|"
                     r"read the (story|case study)|watch (the )?(video|demo)|раскрыть|развернуть|свернуть|показать полностью|"
                     r"expand|show less|see details)\b", re.I)
ACCOUNT_RX = re.compile(r"^(войти|вход|личный кабинет|регистрация|зарегистрироваться|log ?in|sign ?in|sign ?up|my account|"
                        r"ru|en|рус|eng|ru en|en ru|рус eng|версия для слабовидящих|для слабовидящих|слабовидящим|"
                        r"главная|home|меню|menu|поиск|search|корзина|cart|избранное|"
                        r"opt[ -]?out|accept( all( cookies)?)?|reject( all)?|decline|got it|ok|okay|agree|i agree|"
                        r"согласен|согласна|принять( все)?|хорошо|ок|понятно|закрыть|close)$", re.I)
HOURS_ADDR_RX = re.compile(r"\d{1,2}[:.]\d{2}\s*[-–—]\s*\d{1,2}[:.]\d{2}|^ежедневно|без выходных|круглосуточно|^пн[\s–-]|"
                           r"\b(ул|пр|просп|пр-т|пер|д|г)\.\s?[А-ЯЁ0-9]|^адрес|mon[-–]fri|open (daily|24)|"
                           r"\d+ [A-Z][a-z]+ (ave|st|street|rd|road|blvd|dr|drive|way|ln)\b|\b[A-Z]{2} \d{5}\b", re.I)
PHONE_RX = re.compile(r"^(\+7|8|\+1|\+44|\(\d{3}\))[\d\s()‑–+-]{8,}$|^[\w.+-]+@[\w-]+\.[\w.]+$")
SKIP_LINK_RX = re.compile(r"^(skip to|перейти к (основному )?содерж|к содержанию|skip navigation)", re.I)
CONSENT_RX = re.compile(r"персональн|политик[аиу] конфиденц|согласи[ея]|обработк[уи] (моих )?данн|privacy|consent|terms of (service|use)|agree to|оферт|cookie", re.I)
NEXT_RX = re.compile(r"перезвоним|свяжемся|ответим|позвоним|в течение \d+|менеджер (свяжется|позвонит)|we.ll (get back|be in touch|contact|reply)|within \d+", re.I)
CTA_NOTE_RX = re.compile(r"бесплатн|без (предоплат|карт|обязательств|регистрац)|карта не нужна|отменить|гаранти|минут|за \d+|ответим|перезвоним|"
                         r"no credit card|cancel any ?time|free|trial|days|no commitment|setup in|takes \d+|guarantee|money-back", re.I)
PRICE_RX = re.compile(r"(\d[\d\s  .,]*\s?(₽|руб|р\.|\$|€|£|usd|eur)|(₽|\$|€|£)\s?\d|/\s?(мес|месяц|год|mo|month|yr|year|user|seat)|"
                      r"в месяц|per (month|user|seat|year)|бесплатно|free\b|\bот \d)", re.I)
STAT_RX = re.compile(r"^[~≈<>+−-]?\s?(\d[\d\s  .,]*)(\s?(%|\+|×|x|k|K|M|B|тыс\.?|млн|млрд|лет|года?|мин|ч|дн\w*|₽|\$|€|/7|/5|из 5|/10|★)\+?)?"
                     r"(\s?[+%])?$")
PROOF_RX = re.compile(r"\d[\d\s  .,]*\s?(\+|%|клиент|отзыв|компани|заказ|пользовател|проект|лет|года|★|звезд|из 5|/5|customers|users|companies|teams|reviews|stars|rating)|"
                      r"рейтинг|★|trusted by|used by|rated|\bG2\b|Capterra|Trustpilot|Яндекс[ .]?Карт|2ГИС|Google (reviews|рейтинг)", re.I)
BADGE_RX = re.compile(r"^(популярн\w*|хит|новинк\w*|новое|выгодно|рекоменду\w*|лучший выбор|скидка|акция|popular|most popular|new|best value|recommended|save \d+%|beta|sale|-?\d+ ?%)$", re.I)
SUMMARY_HEAD_RX = re.compile(r"^(коротко|кратко|главное|вкратце|что важно знать|в двух словах|суть|tl;?dr|key takeaways|summary|in short|in brief|the short version|at a glance)\b", re.I)
AUTHOR_RX = re.compile(r"^(автор|текст|author|by|written by|редактор|editor)\b[: ]", re.I)
DATE_ONLY_RX = re.compile(r"^(\d{1,2}[ .][а-яa-z]+[ .]\d{2,4}|\d{1,2}\.\d{1,2}\.\d{2,4}|[A-Z][a-z]+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})$", re.I)
COOKIE_TEXT_RX = re.compile(r"cookie|куки|файлы cookie|файлов cookie|we use cookies|используем cookies|используем куки|"
                            r"lithuania|литв|see what we offer|choose your (country|region)|you.re (in|visiting)|"
                            r"вы находитесь|выберите (регион|страну)|switch to (the )?(\w+ )?site", re.I)
NAME_RX = re.compile(r"^[A-ZА-ЯЁ][a-zа-яё]+(?:[- ][A-ZА-ЯЁ][a-zа-яё]+){0,2}\.?(,|$| [—–-] |\s*\|)")
LEGAL_RX = re.compile(r"©|\(c\)|все права|all rights reserved|инн|огрн|ооо |ип |privacy policy|terms|политика", re.I)


def base_font(blocks: list[dict]) -> float:
    sizes = []
    big_enough = [b for b in blocks if b.get("fs", 0) >= 14]
    for b in (big_enough if len(big_enough) >= 5 else blocks):
        n = nwords(b["t"])
        if n >= 10 and not b.get("hdr") and not b.get("nav") and not b.get("lvl"):
            sizes.extend([round(b["fs"])] * min(n, 60))
    if not sizes:
        return 16.0
    sizes.sort()
    return float(sizes[len(sizes) // 2])


def is_caps(b: dict) -> bool:
    t = b["t"]
    letters = re.findall(r"[A-Za-zА-Яа-яЁё]", t)
    if not letters:
        return False
    return b.get("tt") == "uppercase" or (sum(1 for c in letters if c.isupper()) / len(letters) > 0.85 and len(letters) >= 3)


def classify(raw: dict, genre: str = "landing", lang_hint: str = "") -> dict:
    blocks = [b for b in raw.get("blocks", []) if b.get("t")]
    for b in blocks:   # «revenue.Accept» — пропущенный пробел на стыке инлайновых элементов
        b["t"] = re.sub(r"([a-zа-яё0-9%)»])([.!?])([A-ZА-ЯЁ][a-zа-яё])", r"\1\2 \3", b["t"])
        b["t"] = re.sub(r"(?<=\w)\s+([.,!?;:](?:\s|$))", r"\1", b["t"]).strip()   # «kept .» — точка в отдельном span
    meta_raw = raw.get("meta", {}) or {}
    vh = raw.get("vh") or VH
    # отсев: cookie-тексты, дубли не-кнопок (бегущие строки), служебные
    seen, clean = set(), []
    for b in blocks:
        t = b["t"]
        if COOKIE_TEXT_RX.search(t) and nwords(t) <= 60 and (b.get("pos") in ("fixed", "sticky") or b.get("ftr") or
                                                           b["y"] > 0.6 * (raw.get("doc_h") or 1e9) or nwords(t) <= 40):
            continue
        if SKIP_LINK_RX.match(t):
            continue
        if not re.search(r"[A-Za-zА-Яа-яЁё0-9]", t):
            continue                      # «+», «−», «<», «·» — элементы управления, не текст
        vw_ = raw.get("vw") or VW
        if "x" in b and "w" in b and (b["x"] >= vw_ - 2 or b["x"] + b["w"] <= 2):
            continue                      # слайды карусели за краем экрана (translateX)
        if "x" in b and "w" in b and b["x"] + b["w"] > vw_ + 20 and b.get("pos") in ("absolute", "fixed"):
            continue                      # плавающие виджеты у правого края («Заказать звонок», чат)
        if b.get("tab"):
            b["nav"] = True               # вкладки (role=tab) — навигация внутри страницы, не CTA
        key = (t.lower(), b.get("btn"))
        if key in seen and not b.get("btn") and nwords(t) >= 3:
            continue
        seen.add(key)
        clean.append(b)
    blocks = clean
    all_text = " ".join(b["t"] for b in blocks)
    lang = lang_hint or detect_lang(all_text)
    bf = base_font(blocks)
    # макеты интерфейса в вёрстке (Linear, Notion…): плотные области мелкого текста — не маркетинговый текст
    from collections import Counter

    def micro(b):
        return (b["fs"] <= 13.5 or b["fs"] < 0.86 * bf) and nwords(b["t"]) <= 10 and not b.get("ftr") \
            and not (b.get("hdr") and b["y"] < 120)

    reg_total = Counter(b.get("reg", 0) for b in blocks)
    reg_micro = Counter(b.get("reg", 0) for b in blocks if micro(b))
    mock_regs = {r for r, c in reg_micro.items() if r and c >= 8 and c / max(1, reg_total[r]) >= 0.6}
    top_total = Counter(b.get("top", -1) for b in blocks)
    top_micro = Counter(b.get("top", -1) for b in blocks if micro(b))
    mock_tops = {r for r, c in top_micro.items() if r != -1 and c >= 25 and c / max(1, top_total[r]) >= 0.5}
    mock = []
    for b in blocks:
        if b.get("reg", 0) in mock_regs or (b.get("top", -1) in mock_tops and micro(b)):
            b["_mock"] = True
            mock.append(b)
    blocks = [b for b in blocks if not b.get("_mock")]
    n_h2 = sum(1 for b in blocks if b.get("lvl") == 2 and not b.get("ftr") and not b.get("nav"))
    n_h1 = sum(1 for b in blocks if b.get("lvl") == 1)

    # визуальные заголовки
    for b in blocks:
        n = nwords(b["t"])
        b["_vh"] = 0
        if b.get("lvl") or b.get("btn") or b.get("nav") or b.get("ftr") or n == 0 or n > 18 or b.get("li") and n > 8:
            continue
        if STAT_RX.match(b["t"].strip()):
            continue
        if b["fs"] >= 1.9 * bf and n <= 18:
            b["_vh"] = 2
        elif b["fs"] >= 1.3 * bf and b["fw"] >= 500 and n <= 14:
            b["_vh"] = 3
        elif b["fs"] >= 1.08 * bf and b["fw"] >= 600 and n <= 10 and not b["t"].rstrip().endswith((".", ",", ";")):
            b["_vh"] = 4

    def level(b: dict) -> int:
        if b.get("lvl"):
            return b["lvl"]
        return b.get("_vh", 0)

    # «заголовок-кнопка»: тег h1–h6 мелким кеглем внутри ссылки (Т-Банк: h3 «Оформить карту» 13 px) — это CTA
    cta_verb = re.compile(r"^(оформить|получить|заказать|купить|записаться|оставить|узнать|попробовать|начать|подключить|"
                          r"рассчитать|скачать|зарегистрироваться|открыть|выбрать|get|start|try|book|request|buy|sign|join|"
                          r"download|contact|order|shop)\b", re.I)
    for b in blocks:
        if b.get("lvl") and b["fs"] < bf and nwords(b["t"]) <= 5 and (b.get("a") or cta_verb.match(b["t"].strip())):
            b["lvl"] = 0
            b["_vh"] = 0
            b["btn"] = True
    use_visual = n_h2 < 3
    # H1 / заголовок hero
    h1 = None
    h1_tag_small = None
    cands = [b for b in blocks if b.get("lvl") == 1 and b["y"] < 1.6 * vh and nwords(b["t"]) >= 1]
    if cands and cands[0]["y"] > 0.85 * vh:
        # тег H1 ниже первого экрана, а в первом экране есть крупный заголовок (Qlean): hero — он
        first = [b for b in blocks if b["y"] < vh and 2 <= nwords(b["t"]) <= 25 and not b.get("btn") and not b.get("nav")
                 and b["fs"] >= 1.6 * bf and not STAT_RX.match(b["t"].strip())]
        if first:
            cands = [max(first, key=lambda b: (b["fs"], -b["y"]))]
    if cands:
        h1 = cands[0]
        # SEO-H1 мелким кеглем при крупном визуальном заголовке рядом (частый приём Рунета): заголовок — крупный
        big = [b for b in blocks if b is not h1 and abs(b["y"] - h1["y"]) < 420 and b["fs"] >= 1.3 * h1["fs"]
               and 2 <= nwords(b["t"]) <= 25 and not b.get("btn") and not b.get("nav") and b["y"] < 1.6 * vh
               and not STAT_RX.match(b["t"].strip())]
        if big:
            vis = max(big, key=lambda b: (b["fs"], -b["y"]))
            h1_tag_small = h1
            h1 = vis
            if nwords(h1_tag_small["t"]) <= 12:
                h1_tag_small["_eyebrow"] = True
    else:
        fs_cands = [b for b in blocks if b["y"] < 1.2 * vh and not b.get("nav") and not b.get("btn") and 2 <= nwords(b["t"]) <= 25
                    and not STAT_RX.match(b["t"].strip()) and not DATE_ONLY_RX.match(b["t"].strip())
                    and not re.match(r"^\d{1,2}[:.]\d{2}", b["t"].strip())
                    and not b.get("ftr") and not (b.get("hdr") and b["y"] < 110 and b["fs"] < 1.5 * bf)]
        if fs_cands:
            h1 = max(fs_cands, key=lambda b: (b["fs"], -b["y"]))
            if h1["fs"] < 1.4 * bf:
                h1 = None
    units: list[dict] = []
    sections: list[dict] = []
    hero = {"eyebrow": "", "headline": "", "subheadline": "", "cta": [], "proof": []}

    def add(b, st, sec, role=""):
        u = {"slot_type": st, "text": b["t"], "section": sec, "role": role, "tag": b["tag"], "y": b["y"],
             "above_fold": b["y"] < vh, "i": b["i"]}
        units.append(u)
        b["_slot"] = st
        return u

    # --- статьи
    if genre == "article":
        return classify_article(raw, blocks, lang, bf, h1, meta_raw, vh)

    # --- навигация и подвал
    body_blocks = []
    for b in blocks:
        n = nwords(b["t"])
        if ACCOUNT_RX.match(b["t"].strip()) or (b["y"] < 100 and n <= 3 and b["fs"] <= 16 and not (h1 and b is h1)):
            add(b, "nav-label", -1, "header")
            continue
        if PHONE_RX.match(b["t"].strip()) or (HOURS_ADDR_RX.search(b["t"]) and n <= 12 and not b.get("lvl")):
            add(b, "contact", -1, "contact")          # телефон, почта — не подпись кнопки
            continue
        if re.fullmatch(r"\d{1,2}[.)]?", b["t"].strip()):
            add(b, "number-label", -1, "decor")      # номера шагов, звёзды рейтинга — не текст
            continue
        if b.get("nav") and n <= 6 and not (h1 and b is h1):
            add(b, "nav-label", -1, "nav")
            continue
        if b.get("hdr") and b["y"] < 150 and n <= 6 and not (h1 and b is h1):
            add(b, "cta-secondary-label" if (b.get("btn") or b.get("bg")) else "nav-label", -1, "header")
            continue
        if b.get("ftr"):
            if LEGAL_RX.search(b["t"]):
                add(b, "footer-legal", -2, "footer")
            elif b.get("a") and n <= 6:
                add(b, "nav-label", -2, "footer")
            else:
                add(b, "footer-tagline" if n >= 3 else "nav-label", -2, "footer")
            continue
        body_blocks.append(b)
    # --- секции: границы по H2 (или визуальным заголовкам уровня 2–3, если тегов H2 мало)
    def is_section_head(b):
        if b is h1:
            return False
        if STAT_RX.match(b["t"].strip()) or (PRICE_RX.search(b["t"]) and nwords(b["t"]) <= 4 and re.search(r"\d", b["t"])):
            return False
        if nwords(b["t"]) <= 3 and re.match(r"^[~≈<>+−-]?\s?\d", b["t"].strip()):
            return False                  # «6,400+ Clients», «18 Years», «4.9 Stars» — числа ряда цифр, не заголовки секций
        lv = level(b)
        if b.get("lvl") == 2 and not b.get("li"):
            return True
        if use_visual and b.get("_vh") in (2, 3) and not b.get("li") and not b.get("btn"):
            return True
        if n_h2 == 0 and n_h1 > 1 and b.get("lvl") == 1:
            return True
        return False

    cur = {"index": 0, "heading": "", "level": 1, "eyebrow": "", "role_guess": "hero", "texts": [], "ctas": [], "_blocks": []}
    sections.append(cur)
    h1_seen = h1 is None
    for b in body_blocks:
        if h1 is not None and b is h1:
            h1_seen = True
            cur["_blocks"].append(b)
            continue
        if is_section_head(b) and (h1_seen or b["y"] > (h1["y"] if h1 else 0)):
            cur = {"index": len(sections), "heading": b["t"], "level": level(b) or 2, "eyebrow": "", "role_guess": "",
                   "texts": [], "ctas": [], "_blocks": [b], "_head": b}
            sections.append(cur)
            continue
        cur["_blocks"].append(b)
    # hero: всё до первой секции; если H1 нет — первый экран
    hero_sec = sections[0]
    # надзаголовки: короткая строка капсом/с трекингом/мелким кеглем прямо перед заголовком
    for s in sections:
        head = s.get("_head") if s["index"] else h1
        if not head:
            continue
        prev_sec = sections[s["index"] - 1] if s["index"] else None
        pool = (prev_sec["_blocks"] if prev_sec else []) + s["_blocks"]
        try:
            k = next(j for j, x in enumerate(pool) if x is head)
        except StopIteration:
            continue
        if k == 0:
            continue
        p = pool[k - 1]
        n = nwords(p["t"])
        if 1 <= n <= 8 and not p.get("btn") and not p.get("nav") and 0 <= head["y"] - p["y"] <= 220 and \
                (is_caps(p) or p.get("ls", 0) >= 0.5 or p["fs"] <= 0.95 * bf or p.get("rad", 0) >= 8 and p.get("bg")) and \
                p["fs"] < head["fs"] and not STAT_RX.match(p["t"].strip()):
            p["_eyebrow"] = True
            s["eyebrow"] = p["t"]
            if prev_sec and p in prev_sec["_blocks"]:
                prev_sec["_blocks"].remove(p)
                s["_blocks"].insert(0, p)
    # надзаголовки карточек: короткая метка капсом/трекингом прямо над заголовком карточки
    for k in range(1, len(body_blocks)):
        b, p = body_blocks[k], body_blocks[k - 1]
        if level(b) >= 3 and nwords(b["t"]) <= 14 and not p.get("_eyebrow") and 1 <= nwords(p["t"]) <= 5 \
                and not p.get("btn") and not p.get("nav") and 0 <= b["y"] - p["y"] <= 90 and not level(p) \
                and (is_caps(p) or p.get("ls", 0) >= 0.5 or (p["fs"] <= 0.9 * b["fs"] and p["fs"] <= bf)) \
                and not STAT_RX.match(p["t"].strip()) and not p.get("a") and not p.get("li"):
            p["_eyebrow"] = True
            p["_eb_level"] = "card"
    # роли секций
    for s in sections[1:]:
        h = s["heading"]
        role = ""
        for r, rx in ROLE_RX:
            if rx.search(h):
                role = r
                break
        texts = [x["t"] for x in s["_blocks"]]
        joined = " ".join(texts)
        if not role:
            if sum(1 for x in s["_blocks"] if x["t"].rstrip().endswith("?") and level(x) >= 3) >= 3 or \
                    sum(1 for x in s["_blocks"] if x.get("det")) >= 3:
                role = "faq"
            elif len(PRICE_RX.findall(joined)) >= 3:
                role = "pricing"
            elif any(x.get("bq") for x in s["_blocks"]) and sum(1 for x in s["_blocks"] if nwords(x["t"]) >= 12) >= 2:
                role = "testimonials"
            elif any(x.get("form") for x in s["_blocks"]):
                role = "lead-form"
            elif sum(1 for x in s["_blocks"] if STAT_RX.match(x["t"].strip())) >= 3:
                role = "proof-stats"
        if not role:
            role = "benefits" if sum(1 for x in s["_blocks"] if level(x) >= 3) >= 2 else "other"
        s["role_guess"] = role
    if sections and len(sections) > 1 and sections[-1]["role_guess"] in ("other", "lead-form", "benefits") and \
            sum(1 for x in sections[-1]["_blocks"] if x.get("btn")) >= 1 and \
            sum(nwords(x["t"]) for x in sections[-1]["_blocks"]) <= 80:
        sections[-1]["role_guess"] = "final-cta"

    # --- hero
    fold = vh
    if h1 is not None:
        add(h1, "headline", 0, "hero")
        hero["headline"] = h1["t"]
        fold = max(vh, h1["y"] + h1["h"] + 420)
    if h1_tag_small is not None:
        hero["h1_tag"] = h1_tag_small["t"]
    hb = [b for b in hero_sec["_blocks"] if b is not h1]
    # ограничим hero первым экраном (для страниц без H2 весь текст иначе ушёл бы в hero)
    hero_part = [b for b in hb if b["y"] < fold]
    rest = [b for b in hb if b["y"] >= fold]
    hero_has_btn = any(b.get("btn") for b in hero_part)
    # ряд из ≥ 3 коротких ссылок на одной высоте — меню, а не кнопки
    from collections import Counter as _C
    linkish = [b for b in hero_part if nwords(b["t"]) <= 4 and (b.get("a") or b.get("cur") or b.get("btn"))]
    rows_y = _C(round(b["y"] / 6) for b in linkish)
    for b in linkish:
        if rows_y[round(b["y"] / 6)] >= 3:
            b["_menu"] = True
    sub_done = False
    sub_open = True          # подзаголовок — первый текст после заголовка, не дальше 320 px и до карточек
    card_mode = False
    h1_bottom = (h1["y"] + h1["h"]) if h1 is not None else 0
    for b in hero_part:
        n = nwords(b["t"])
        lv = level(b)
        if b.get("_eyebrow"):
            add(b, "eyebrow", 0, "hero")
            hero["eyebrow"] = hero["eyebrow"] or b["t"]
            continue
        if b.get("_menu"):
            add(b, "nav-label", 0, "menu")
            continue
        if b.get("btn"):
            st = "cta-label" if not hero["cta"] else "cta-secondary-label"
            add(b, st, 0, "hero")
            hero["cta"].append({"text": b["t"], "href": b.get("href", ""), "kind": "primary" if st == "cta-label" else "secondary"})
            continue
        if n <= 5 and (LINK_RX.match(b["t"]) or ((b.get("a") or b.get("cur")) and not lv)) and not BADGE_RX.match(b["t"].strip()):
            st = "cta-label" if (not hero_has_btn and not hero["cta"]) else "cta-secondary-label"
            add(b, st, 0, "hero")
            hero["cta"].append({"text": b["t"], "href": b.get("href", ""), "kind": "link-primary" if st == "cta-label" else "link"})
            continue
        if h1 is not None and b["y"] < h1["y"] and n <= 10 and not sub_done and not (b.get("a") or b.get("cur") or b.get("btn")):
            # строка над H1, не распознанная как надзаголовок
            add(b, "eyebrow" if n <= 8 else "body", 0, "hero")
            if n <= 8 and not hero["eyebrow"]:
                hero["eyebrow"] = b["t"]
            continue
        if h1 is not None and b["y"] - h1_bottom > 320:
            sub_open = False
        if lv >= 3 and n <= 14 and not b.get("form"):
            add(b, "card-title", 0, "hero")
            card_mode = True
            sub_open = False
            continue
        if sub_open and not sub_done and n >= 4 and not b.get("form") and (h1 is None or (b["fs"] < h1["fs"]
                                                                                    and b["y"] >= h1["y"])):
            add(b, "subheadline", 0, "hero")
            hero["subheadline"] = b["t"]
            sub_done = True
            sub_open = False
            continue
        if h1 is None or b["y"] >= h1["y"]:
            sub_open = False
        if hero["cta"] and n <= 20 and CTA_NOTE_RX.search(b["t"]) and not PROOF_RX.search(b["t"]) and not card_mode:
            add(b, "cta-note", 0, "hero")
            continue
        if n <= 15 and PROOF_RX.search(b["t"]) and not card_mode:
            add(b, "hero-proof", 0, "hero")
            hero["proof"].append(b["t"])
            continue
        if b.get("form"):
            classify_form_block(b, add, 0)
            continue
        if b.get("li"):
            add(b, "list-item", 0, "hero")
            continue
        if STAT_RX.match(b["t"].strip()):
            add(b, "stat-value", 0, "hero")
            continue
        if n <= 3 and BADGE_RX.match(b["t"].strip()):
            add(b, "badge", 0, "hero")
            continue
        if card_mode:
            add(b, "card-body", 0, "hero")
            continue
        add(b, "body" if n >= 4 else "stat-label" if units and units[-1]["slot_type"] == "stat-value" else "body", 0, "hero")
    # хвост hero без H2 — как обычная секция без заголовка
    if rest:
        tail = {"index": len(sections), "heading": "", "level": 2, "eyebrow": "", "role_guess": "other", "texts": [],
                "ctas": [], "_blocks": rest}
        sections.append(tail)

    # --- секции
    testimonials, faq = [], []
    for s in sections[1:]:
        role = s["role_guess"]
        si = s["index"]
        last_card_title = None
        lead_done = False
        pending_q = None
        prev = None
        for b in s["_blocks"]:
            n = nwords(b["t"])
            lv = level(b)
            if b is s.get("_head"):
                add(b, "section-title", si, role)
                prev = b
                continue
            if b.get("_eyebrow"):
                add(b, "eyebrow", si, role)
                prev = b
                continue
            if b["t"].rstrip().endswith("?") and n >= 3 and (b.get("btn") or b.get("cur") or b.get("det") or role == "faq"):
                add(b, "faq-q", si, "faq")
                pending_q = {"q": b["t"], "a": ""}
                faq.append(pending_q)
                prev = b
                continue
            if b.get("btn"):
                st = "cta-label"
                if s["ctas"] and not b.get("form"):
                    st = "cta-secondary-label" if (prev is not None and prev.get("btn")) else "cta-label"
                add(b, st, si, role)
                s["ctas"].append(b["t"])
                prev = b
                continue
            if b.get("form"):
                classify_form_block(b, add, si)
                prev = b
                continue
            if n <= 5 and not lv and (LINK_RX.match(b["t"]) or b.get("a") or b.get("cur")) and not b.get("det") \
                    and not STAT_RX.match(b["t"].strip()) and not (role == "testimonials" and NAME_RX.match(b["t"])):
                add(b, "cta-secondary-label", si, role)
                s["ctas"].append(b["t"])
                prev = b
                continue
            if prev is not None and prev.get("_slot") == "faq-q" and pending_q is not None and n >= 5 and not lv \
                    and not b.get("btn"):
                add(b, "faq-a", si, "faq")
                pending_q["a"] = (pending_q["a"] + " " + b["t"]).strip()
                prev = b
                continue
            if role == "faq" or b.get("det"):
                if b["t"].rstrip().endswith("?") or (lv >= 3 and n <= 20) or b["tag"] == "summary" or b["tag"] == "dt":
                    add(b, "faq-q", si, "faq")
                    pending_q = {"q": b["t"], "a": ""}
                    faq.append(pending_q)
                    prev = b
                    continue
                if pending_q is not None and n >= 3:
                    add(b, "faq-a", si, "faq")
                    pending_q["a"] = (pending_q["a"] + " " + b["t"]).strip()
                    prev = b
                    continue
            if role == "testimonials":
                if n >= 10 and not (lv and n <= 12):
                    add(b, "testimonial-quote", si, role)
                    testimonials.append({"quote": b["t"], "attribution": ""})
                    prev = b
                    continue
                if n <= 12 and testimonials and (NAME_RX.match(b["t"]) or re.search(r"директор|основател|руководител|CEO|founder|head of|manager|менеджер|владел", b["t"], re.I)):
                    add(b, "testimonial-attribution", si, role)
                    testimonials[-1]["attribution"] = (testimonials[-1]["attribution"] + " " + b["t"]).strip()
                    prev = b
                    continue
            elif b.get("bq") and n >= 12 and role not in ("faq",):
                add(b, "testimonial-quote", si, role)
                testimonials.append({"quote": b["t"], "attribution": ""})
                prev = b
                continue
            if (STAT_RX.match(b["t"].strip()) and n <= 4) or (n <= 3 and re.match(r"^[~≈<>+−-]?\s?\d", b["t"].strip())
                                                               and not PRICE_RX.search(b["t"])):
                if role == "pricing" or PRICE_RX.search(b["t"]):
                    add(b, "pricing-price", si, role)
                else:
                    add(b, "stat-value", si, role)
                prev = b
                continue
            if prev is not None and prev.get("_slot") == "stat-value" and n <= 12:
                add(b, "stat-label", si, role)
                prev = b
                continue
            if n <= 3 and BADGE_RX.match(b["t"].strip()):
                add(b, "badge", si, role)
                prev = b
                continue
            if role == "pricing" and n <= 8 and PRICE_RX.search(b["t"]) and re.search(r"\d|бесплатн|free", b["t"], re.I):
                add(b, "pricing-price", si, role)
                prev = b
                continue
            if role == "pricing" and prev is not None and prev.get("_slot") == "pricing-price" and n <= 16:
                add(b, "pricing-price-note", si, role)
                prev = b
                continue
            if n <= 5 and PRICE_RX.search(b["t"]) and re.search(r"\d", b["t"]):
                add(b, "pricing-price", si, role)
                prev = b
                continue
            if lv >= 3 or (lv and lv >= 2 and b is not s.get("_head")):
                st = {"how-it-works": "step-title", "pricing": "pricing-plan-name", "case-studies": "case-title",
                      "faq": "faq-q"}.get(role, "card-title")
                add(b, st, si, role)
                last_card_title = b
                prev = b
                continue
            if b.get("li"):
                add(b, "pricing-feature" if role == "pricing" else "list-item", si, role)
                prev = b
                continue
            if prev is not None and prev.get("btn") and n <= 20 and CTA_NOTE_RX.search(b["t"]):
                add(b, "cta-note", si, role)
                prev = b
                continue
            if role == "proof-logos" and n <= 12:
                add(b, "logos-caption", si, role)
                prev = b
                continue
            if last_card_title is not None:
                st = {"how-it-works": "step-body", "pricing": "pricing-plan-summary", "case-studies": "case-summary",
                      "faq": "faq-a"}.get(role, "card-body")
                if role == "case-studies" and n <= 14 and re.search(r"\d", b["t"]):
                    st = "case-result"
                add(b, st, si, role)
                prev = b
                continue
            if not lead_done and n >= 5 and b["y"] - (s["_head"]["y"] if s.get("_head") else b["y"]) < 500:
                add(b, "section-lead" if s.get("_head") else "body", si, role)
                lead_done = True
                prev = b
                continue
            if role == "guarantee" and n >= 5:
                add(b, "guarantee-text", si, role)
                prev = b
                continue
            add(b, "body", si, role)
            prev = b
    # мета
    meta = {
        "title": (raw.get("title") or "").strip(),
        "description": meta_raw.get("description", ""),
        "og_title": meta_raw.get("og:title", ""),
        "og_description": meta_raw.get("og:description", ""),
        "og_image_alt": meta_raw.get("og:image:alt", ""),
        "og_site_name": meta_raw.get("og:site_name", ""),
        "twitter_title": meta_raw.get("twitter:title", ""),
        "twitter_description": meta_raw.get("twitter:description", ""),
        "canonical": raw.get("canonical", ""),
        "robots": meta_raw.get("robots", ""),
    }
    res = finish(raw, genre, lang, meta, hero, sections, units, testimonials, faq, bf)
    res["stats"]["ui_mock_blocks"] = len(mock)
    res["stats"]["ui_mock_words"] = sum(nwords(b["t"]) for b in mock)
    res["stats"]["h1_tag_small"] = h1_tag_small["t"] if h1_tag_small is not None else ""
    return res


def classify_form_block(b: dict, add, si: int):
    n = nwords(b["t"])
    if CONSENT_RX.search(b["t"]) and n >= 4:
        add(b, "form-consent", si, "lead-form")
    elif NEXT_RX.search(b["t"]) and n >= 4:
        add(b, "form-next-steps", si, "lead-form")
    elif b.get("lvl") or b.get("_vh"):
        add(b, "form-title", si, "lead-form")
    elif n >= 6:
        add(b, "form-lead", si, "lead-form")
    else:
        add(b, "form-field", si, "lead-form")   # подписи полей — микрокопи ux 07/02, не меряются


def classify_article(raw, blocks, lang, bf, h1, meta_raw, vh):
    units, sections = [], []
    in_art = [b for b in blocks if b.get("art")]
    in_main = [b for b in blocks if b.get("main")]
    pool = in_art if sum(nwords(b["t"]) for b in in_art) >= 200 else (in_main if sum(nwords(b["t"]) for b in in_main) >= 200 else blocks)
    pool = [b for b in pool if not b.get("nav") and not b.get("ftr") and not (b.get("hdr") and b["y"] < 120)]
    if h1 is None:
        hs = [b for b in pool if b.get("lvl") == 1] or [b for b in blocks if b.get("lvl") == 1 and not b.get("ftr")]
        h1 = hs[0] if hs else None
    cur_sec = 0
    sections.append({"index": 0, "heading": h1["t"] if h1 else "", "level": 1, "eyebrow": "", "role_guess": "article-body",
                     "texts": [], "ctas": []})
    started = h1 is None
    lead_done = False
    summary_mode = False
    faq, pending = [], None
    after_h1 = [b for b in pool if (h1 is None or b["y"] >= h1["y"] - 5)]
    if h1 is not None and not any(b is h1 for b in after_h1):
        after_h1 = [h1] + after_h1        # H1 вне <article>: заголовок снаружи, текст внутри
    stop_rx = re.compile(r"^(\d*\s*комментари|\d*\s*comments?\b|читайте также|похожие (статьи|материалы)|ещё по теме|"
                         r"related (articles|posts)|read (more|next)|подпишитесь|subscribe|поделиться|share this|"
                         r"вам может быть интересно|you (may|might) also like|рекомендуем|подобрано (специально )?для вас|"
                         r"вам может понравиться|читайте далее|more (articles|stories|posts)|popular (posts|articles))", re.I)
    meta_line = re.compile(r"врем[яи] (про)?чтения|мин(ут[ыа]?)? чтения|min read|прочтени[йя]|просмотр(ов|а)|views\b|"
                           r"^обновлено|^updated|^опубликовано|^published", re.I)
    for b in after_h1:
        n = nwords(b["t"])
        if h1 is not None and b is h1:
            units.append(dict(slot_type="article-title", text=b["t"], section=0, role="article-body", tag=b["tag"], y=b["y"],
                              above_fold=b["y"] < vh, i=b["i"]))
            started = True
            continue
        if not started:
            continue
        if b.get("aside") and n < 25:
            continue
        if b.get("promo") and not (b.get("lvl") in (2, 3) and not b.get("a")):
            continue
        if b.get("a") and n <= 14 and not b.get("lvl"):
            continue                      # абзац-ссылка: тизер другой статьи
        if b.get("fig") and not b.get("lvl"):
            units.append(dict(slot_type="image-caption", text=b["t"], section=cur_sec, role="article-body", tag=b["tag"],
                              y=b["y"], above_fold=b["y"] < vh, i=b["i"]))
            continue
        if stop_rx.search(b["t"]) and n <= 8 and not b.get("btn") and \
                sum(1 for u in units if u["slot_type"] == "article-paragraph") >= 5:
            break                         # хвост: комментарии, подписка, «читайте также»
        lv = b.get("lvl") or 0
        if lv in (2, 3, 4) or (b.get("_vh") in (2, 3) and n <= 16):
            if stop_rx.search(b["t"]):
                break
            cur_sec += 1
            sections.append({"index": cur_sec, "heading": b["t"], "level": lv or 2, "eyebrow": "",
                             "role_guess": "faq" if re.search(r"вопрос|faq|questions", b["t"], re.I) else "article-body",
                             "texts": [], "ctas": []})
            summary_mode = bool(SUMMARY_HEAD_RX.search(b["t"]))
            is_q = b["t"].rstrip().endswith("?")
            st = "faq-q" if (sections[-1]["role_guess"] == "faq" and lv >= 3) else "article-heading"
            units.append(dict(slot_type=st, text=b["t"], section=cur_sec, role="article-body", tag=b["tag"], y=b["y"],
                              above_fold=b["y"] < vh, i=b["i"]))
            if st == "faq-q":
                pending = {"q": b["t"], "a": ""}
                faq.append(pending)
            continue
        if b.get("btn"):
            units.append(dict(slot_type="cta-label", text=b["t"], section=cur_sec, role="article-body", tag=b["tag"],
                              y=b["y"], above_fold=b["y"] < vh, i=b["i"]))
            continue
        if AUTHOR_RX.search(b["t"]) or b.get("itp") in ("author", "name") and n <= 8:
            units.append(dict(slot_type="article-author", text=b["t"], section=cur_sec, role="article-body", tag=b["tag"],
                              y=b["y"], above_fold=b["y"] < vh, i=b["i"]))
            continue
        if (n <= 4 and DATE_ONLY_RX.match(b["t"].strip())) or (n <= 16 and meta_line.search(b["t"])):
            continue
        if SUMMARY_HEAD_RX.search(b["t"]) and n <= 4:
            summary_mode = True
            continue
        if b.get("li"):
            st = "article-summary" if summary_mode else "list-item"
            units.append(dict(slot_type=st, text=b["t"], section=cur_sec, role="article-body", tag=b["tag"], y=b["y"],
                              above_fold=b["y"] < vh, i=b["i"]))
            continue
        if b.get("bq") and n >= 8:
            units.append(dict(slot_type="article-paragraph", text=b["t"], section=cur_sec, role="quote", tag=b["tag"],
                              y=b["y"], above_fold=b["y"] < vh, i=b["i"]))
            continue
        if n >= 4:
            if summary_mode:
                st = "article-summary"
            elif not lead_done and cur_sec == 0:
                st = "article-lead"
                lead_done = True
            elif pending is not None and sections[-1]["role_guess"] == "faq":
                st = "faq-a"
                pending["a"] = (pending["a"] + " " + b["t"]).strip()
            else:
                st = "article-paragraph"
            units.append(dict(slot_type=st, text=b["t"], section=cur_sec, role="article-body", tag=b["tag"], y=b["y"],
                              above_fold=b["y"] < vh, i=b["i"]))
    meta = {
        "title": (raw.get("title") or "").strip(),
        "description": meta_raw.get("description", ""),
        "og_title": meta_raw.get("og:title", ""),
        "og_description": meta_raw.get("og:description", ""),
        "og_image_alt": meta_raw.get("og:image:alt", ""),
        "og_site_name": meta_raw.get("og:site_name", ""),
        "twitter_title": meta_raw.get("twitter:title", ""),
        "twitter_description": meta_raw.get("twitter:description", ""),
        "canonical": raw.get("canonical", ""),
        "robots": meta_raw.get("robots", ""),
    }
    hero = {"eyebrow": "", "headline": h1["t"] if h1 else "", "subheadline": "", "cta": [], "proof": []}
    lead = next((u["text"] for u in units if u["slot_type"] == "article-lead"), "")
    hero["subheadline"] = lead
    for s in sections:
        s["_blocks"] = []
    return finish(raw, "article", lang, meta, hero, sections, units, [], faq, bf)


def jsonld_texts(ld_list: list[str]) -> tuple[list[dict], list[dict]]:
    out, faq = [], []

    def walk(o):
        if isinstance(o, list):
            for x in o:
                walk(x)
            return
        if not isinstance(o, dict):
            return
        tp = o.get("@type")
        tp = ",".join(tp) if isinstance(tp, list) else (tp or "")
        txt = []
        for k in ("name", "headline", "description", "text", "slogan", "abstract"):
            v = o.get(k)
            if isinstance(v, str) and v.strip():
                txt.append(v.strip())
        if txt:
            out.append({"type": tp, "text": " | ".join(txt)[:600]})
        if tp == "Question" or "Question" in tp:
            ans = o.get("acceptedAnswer") or {}
            if isinstance(ans, list):
                ans = ans[0] if ans else {}
            a = ans.get("text", "") if isinstance(ans, dict) else ""
            faq.append({"q": o.get("name", ""), "a": re.sub(r"<[^>]+>", " ", a).strip()[:2000]})
        for k, v in o.items():
            if k in ("acceptedAnswer",):
                continue
            if isinstance(v, (dict, list)):
                walk(v)

    for s in ld_list or []:
        try:
            walk(json.loads(s))
        except Exception:
            continue
    return out, faq


def finish(raw, genre, lang, meta, hero, sections, units, testimonials, faq, bf) -> dict:
    ld, ld_faq = jsonld_texts(raw.get("ld", []))
    for s in sections:
        s["texts"] = [u["text"] for u in units if u["section"] == s["index"] and u["slot_type"] not in ("section-title",)][:400]
        s.pop("_blocks", None)
        s.pop("_head", None)
    units.sort(key=lambda u: u.get("i", 0))
    for k, u in enumerate(units):
        if u["slot_type"] == "eyebrow":
            nxt = next((v["slot_type"] for v in units[k + 1:k + 3] if v["slot_type"] != "eyebrow"), "")
            u["eb_level"] = "hero" if nxt == "headline" else "section" if nxt == "section-title" else "card"
    text_for_hash = "\n".join(u["text"] for u in units)
    words = nwords(text_for_hash)
    title = meta.get("title", "")
    blocked = None
    if BLOCK_TITLE_RX.search(title) and words < 400:
        blocked = "title: " + title[:80]
    elif words < 40:
        blocked = f"мало текста ({words} слов)"
    counts: dict = {}
    for u in units:
        counts[u["slot_type"]] = counts.get(u["slot_type"], 0) + 1
    return {
        "tool": "copy_extract.py", "version": VERSION, "date": DATE,
        "page": {"url": raw.get("req_url") or raw.get("url", ""), "final_url": raw.get("url", ""),
                 "status": raw.get("status"), "title": title, "html_lang": raw.get("html_lang", ""),
                 "blocked": blocked, "insecure": raw.get("insecure", False), "fetched_at": raw.get("fetched_at", ""),
                 "viewport": [raw.get("vw") or VW, raw.get("vh") or VH], "doc_height": raw.get("doc_h"),
                 "hash": hashlib.sha1(text_for_hash.encode("utf-8")).hexdigest()[:16], "genre": genre,
                 "base_font_px": bf, "browser": raw.get("browser", "")},
        "lang": lang, "meta": meta, "hero": hero, "sections": sections, "testimonials": testimonials,
        "faq": faq or ld_faq, "faq_jsonld": ld_faq, "jsonld": ld[:60], "units": units,
        "stats": {"words": words, "units": len(units), "sections": len(sections), "slot_counts": counts,
                  "errors": raw.get("errors", [])},
    }


def to_markdown(res: dict) -> str:
    """Читаемый вид для ручной проверки и для A: слот в квадратных скобках, секции заголовками."""
    L = [f"# {res['meta'].get('title','')}", "", f"URL: {res['page']['url']}  ", f"Снято: {res['page'].get('fetched_at','')} "
         f"· copy_extract {res['version']} · язык {res['lang']} · жанр {res['page'].get('genre')} · слов {res['stats']['words']}", ""]
    m = res["meta"]
    for k in ("description", "og_title", "og_description"):
        if m.get(k):
            L.append(f"[meta-{k.replace('_', '-')}] {m[k]}")
    L.append("")
    cur = None
    for u in res["units"]:
        if u["section"] != cur:
            cur = u["section"]
            sec = next((s for s in res["sections"] if s["index"] == cur), None)
            if sec is not None:
                L.append(f"\n## § {cur} · {sec.get('role_guess','')} · {sec.get('heading','')[:80]}\n")
            elif cur == -1:
                L.append("\n## (шапка и навигация)\n")
            elif cur == -2:
                L.append("\n## (подвал)\n")
        L.append(f"[{u['slot_type']}] {u['text']}")
    return "\n".join(L) + "\n"


def to_plain(res: dict) -> str:
    """Сплошной текст страницы без навигации и подвала (для формул читаемости у A)."""
    keep = [u["text"] for u in res["units"] if u["section"] >= 0 and u["slot_type"] not in ("nav-label", "form-field")]
    return "\n\n".join(keep) + "\n"


# ---------------------------------------------------------------------------------------------------------------------
# 3. CLI
# ---------------------------------------------------------------------------------------------------------------------
def extract_one(url: str | None, out: str | None, genre: str, lang: str, html: str | None = None, base_url: str | None = None,
                md: str | None = None, shot: str | None = None, save_blocks: bool = False, lock: bool = False,
                insecure: bool = False, wait_ms: int = 1200, timeout_s: int = 45, txt: str | None = None) -> dict:
    with Locks(lock):
        if lock:
            wait_memory(2.0)
        t0 = time.time()
        br = browse(url, html, lang, wait_ms, timeout_s, insecure, shot, base_url)
    raw = br.get("data") or {"blocks": [], "meta": {}, "title": "", "url": url or html}
    raw["status"] = br.get("status")
    raw["insecure"] = br.get("insecure")
    raw["errors"] = br.get("errors")
    raw["browser"] = br.get("browser", "")
    raw["req_url"] = url or base_url or html
    raw["fetched_at"] = time.strftime("%Y-%m-%d %H:%M")
    raw["seconds"] = round(time.time() - t0, 1)
    res = classify(raw, genre, lang if lang in ("ru", "en") else "")
    res["page"]["seconds"] = raw["seconds"]
    # защита: неудачный повторный снимок (антибот, таймаут) не затирает прежний удачный
    if out and Path(out).exists() and (res["page"].get("blocked") or res["stats"]["words"] < 40):
        try:
            prev = json.loads(Path(out).read_text(encoding="utf-8"))
            if not prev.get("page", {}).get("blocked") and prev.get("stats", {}).get("words", 0) >= 80:
                fp = re.sub(r"\.json$", "", out) + ".failed.json"
                Path(fp).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
                prev.setdefault("page", {})["refetch_failed"] = raw["fetched_at"]
                return prev
        except Exception:
            pass
    if save_blocks and out:
        bp = re.sub(r"\.json$", "", out) + ".blocks.json"
        Path(bp).write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    if md:
        Path(md).write_text(to_markdown(res), encoding="utf-8")
    if txt:
        Path(txt).write_text(to_plain(res), encoding="utf-8")
    return res


def summary_line(pid: str, res: dict) -> str:
    st = res["stats"]
    h = res["hero"]
    return (f"{pid}\t{res['page'].get('status')}\t{res['lang']}\twords={st['words']}\tunits={st['units']}\tsec={st['sections']}"
            f"\tblocked={res['page'].get('blocked')}\tH1={h.get('headline','')[:60]!r}\tCTA={[c['text'] for c in h.get('cta', [])][:2]}"
            f"\t{res['page'].get('seconds','')}s")


def run_batch(tsv: str, outdir: str, skip_existing: bool, lock: bool, wait_ms: int, timeout_s: int, shots: bool) -> None:
    od = Path(outdir)
    od.mkdir(parents=True, exist_ok=True)
    rows = []
    with open(tsv, encoding="utf-8") as f:
        header = None
        for ln in f:
            if not ln.strip() or ln.startswith("#"):
                if ln.startswith("#") and header is None and "\t" in ln:
                    header = ln.lstrip("#").strip().split("\t")
                continue
            parts = ln.rstrip("\n").split("\t")
            if header is None:
                header = ["id", "url", "genre", "lang", "page_type"]
            rows.append(dict(zip(header, parts)))
    for r in rows:
        pid, url = r.get("id"), r.get("url")
        if not pid or not url:
            continue
        out = od / f"{pid}.json"
        if skip_existing and out.exists():
            continue
        genre = r.get("genre") or "landing"
        genre = {"site-page": "site-page", "article": "article"}.get(genre, "landing" if genre != "site-page" else genre)
        try:
            res = extract_one(url, str(out), genre, r.get("lang", ""), md=str(od / f"{pid}.md"),
                              shot=str(od / "shots" / f"{pid}.jpg") if shots else None, save_blocks=True, lock=lock,
                              wait_ms=wait_ms, timeout_s=timeout_s, txt=str(od / f"{pid}.txt"))
            print(summary_line(pid, res), flush=True)
        except SystemExit as ex:
            print(f"{pid}\tERROR\t{ex}", flush=True)
        except Exception as ex:
            print(f"{pid}\tERROR\t{str(ex)[:200]}", flush=True)


def selftest() -> int:
    raw = {"vh": 900, "doc_h": 3000, "title": "Ремонт квартир в Казани — «Отвес»", "meta": {"description": "Ремонт под ключ"},
           "blocks": [
               {"i": 0, "t": "Услуги", "tag": "a", "lvl": 0, "nav": True, "hdr": True, "a": True, "btn": False, "y": 20, "h": 20, "fs": 15, "fw": 400},
               {"i": 1, "t": "РЕМОНТ ПОД КЛЮЧ", "tag": "div", "lvl": 0, "y": 200, "h": 20, "fs": 13, "fw": 600, "tt": "uppercase", "ls": 1.5},
               {"i": 2, "t": "Ремонт квартиры за 60 дней с фиксированной сметой", "tag": "h1", "lvl": 1, "y": 230, "h": 120, "fs": 56, "fw": 700},
               {"i": 3, "t": "Смета не меняется после подписания договора, прораб присылает фотоотчёт каждый вечер.", "tag": "p", "lvl": 0, "y": 380, "h": 50, "fs": 20, "fw": 400},
               {"i": 4, "t": "Рассчитать смету", "tag": "a", "lvl": 0, "btn": True, "a": True, "y": 460, "h": 50, "fs": 16, "fw": 600},
               {"i": 5, "t": "Выезд замерщика бесплатно, ответим за 15 минут", "tag": "p", "lvl": 0, "y": 520, "h": 20, "fs": 14, "fw": 400},
               {"i": 6, "t": "Как проходит ремонт", "tag": "h2", "lvl": 2, "y": 1000, "h": 50, "fs": 40, "fw": 700},
               {"i": 7, "t": "Замер", "tag": "h3", "lvl": 3, "y": 1100, "h": 30, "fs": 22, "fw": 700},
               {"i": 8, "t": "Инженер приезжает в удобное время и снимает размеры за час.", "tag": "p", "lvl": 0, "y": 1140, "h": 40, "fs": 16, "fw": 400},
               {"i": 9, "t": "Частые вопросы", "tag": "h2", "lvl": 2, "y": 1600, "h": 50, "fs": 40, "fw": 700},
               {"i": 10, "t": "Сколько стоит ремонт?", "tag": "summary", "lvl": 0, "det": True, "y": 1700, "h": 30, "fs": 18, "fw": 600},
               {"i": 11, "t": "От 9 000 ₽ за квадратный метр, смету считаем после замера.", "tag": "p", "lvl": 0, "det": True, "y": 1740, "h": 30, "fs": 16, "fw": 400},
               {"i": 12, "t": "© 2026 ООО «Отвес», ИНН 1234567890", "tag": "p", "lvl": 0, "ftr": True, "y": 2900, "h": 20, "fs": 12, "fw": 400},
           ]}
    res = classify(raw, "landing", "")
    slots = [(u["slot_type"], u["text"][:20]) for u in res["units"]]
    want = {"nav-label", "eyebrow", "headline", "subheadline", "cta-label", "cta-note", "section-title", "step-title",
            "step-body", "faq-q", "faq-a", "footer-legal"}
    got = {s for s, _ in slots}
    ok = want <= got and res["hero"]["headline"].startswith("Ремонт квартиры") and res["faq"] and res["lang"] == "ru"
    ok = ok and res["hero"]["eyebrow"] == "РЕМОНТ ПОД КЛЮЧ" and res["sections"][1]["role_guess"] == "how-it-works"
    art_raw = {"vh": 900, "title": "Как выбрать ламинат", "meta": {}, "blocks": [
        {"i": 0, "t": "Как выбрать ламинат для кухни", "tag": "h1", "lvl": 1, "art": True, "y": 100, "h": 50, "fs": 40, "fw": 700},
        {"i": 1, "t": "Ламинат на кухне живёт пять–семь лет, если выбрать класс 33 и влагостойкий замок.", "tag": "p", "art": True, "y": 180, "h": 40, "fs": 18, "fw": 400},
        {"i": 2, "t": "Класс износостойкости", "tag": "h2", "lvl": 2, "art": True, "y": 300, "h": 40, "fs": 28, "fw": 700},
        {"i": 3, "t": "Для кухни берут 33 класс: он выдерживает каблуки и стулья на колёсиках без следов.", "tag": "p", "art": True, "y": 360, "h": 40, "fs": 18, "fw": 400},
    ]}
    ares = classify(art_raw, "article", "")
    aslots = [u["slot_type"] for u in ares["units"]]
    ok = ok and aslots == ["article-title", "article-lead", "article-heading", "article-paragraph"]
    print("selftest:", "OK" if ok else "FAIL", slots if not ok else "", aslots if not ok else "")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Страница → текст по слотам (JSON).")
    ap.add_argument("url", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--genre", default="landing", choices=["landing", "site-page", "article"])
    ap.add_argument("--lang", default="", choices=["", "ru", "en"])
    ap.add_argument("--html", help="сохранённый HTML (грузится в браузер из файла)")
    ap.add_argument("--base-url")
    ap.add_argument("--reclassify", help="*.blocks.json → классификация без браузера")
    ap.add_argument("--md")
    ap.add_argument("--txt")
    ap.add_argument("--shot")
    ap.add_argument("--save-blocks", action="store_true")
    ap.add_argument("--lock", action="store_true", help="две блокировки браузера и проверка памяти")
    ap.add_argument("--insecure", action="store_true", help="игнорировать ошибки сертификата сразу")
    ap.add_argument("--wait", type=int, default=1200)
    ap.add_argument("--timeout", type=int, default=45)
    ap.add_argument("--batch")
    ap.add_argument("--outdir")
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--shots", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.reclassify:
        raw = json.loads(Path(a.reclassify).read_text(encoding="utf-8"))
        res = classify(raw, a.genre, a.lang)
        s = json.dumps(res, ensure_ascii=False, indent=1)
        if a.out:
            Path(a.out).write_text(s, encoding="utf-8")
        else:
            print(s)
        if a.md:
            Path(a.md).write_text(to_markdown(res), encoding="utf-8")
        if a.txt:
            Path(a.txt).write_text(to_plain(res), encoding="utf-8")
        return 0
    if a.batch:
        if not a.outdir:
            ap.error("--batch требует --outdir")
        run_batch(a.batch, a.outdir, a.skip_existing, a.lock, a.wait, a.timeout, a.shots)
        return 0
    if not a.url and not a.html:
        ap.error("нужен URL, --html, --reclassify или --batch")
    res = extract_one(a.url, a.out, a.genre, a.lang, a.html, a.base_url, a.md, a.shot, a.save_blocks, a.lock, a.insecure,
                      a.wait, a.timeout, a.txt)
    if not a.out:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        print(summary_line(Path(a.out).stem, res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
