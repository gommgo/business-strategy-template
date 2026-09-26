#!/usr/bin/env python3
"""page_gates.py — единые ворота страницы по профилю бюджета (P v0, волна 2; K v1, волна 3; site-research, 2026-09-24).

Сводит готовые замеры страницы в вердикт PASS / S / B по `07-seo-geo-performance-analytics/page-gates.yaml` с порогами
профиля `<page_type>@L<n>` из `budgets.yaml`. Браузер не запускает: берёт JSON утилит
  page_anatomy.py  → anatomy_desktop.json, anatomy_mobile.json  (LCP, CLS, TBT, INP-сценарий, вес, сторонние, текст без JS,
                     мета, формы и согласия, баннер cookie, призывы первого экрана, переполнение и меню телефона)
  page_accept.py   → accept_*.json (LCP с троттлингом телефона, lazy/fetchpriority LCP, пауза, reduce, консоль)
  geo_probe.py     → <id>.json (флаги head-kit.yaml checks: коды, robots, боты, SSR, canonical, JSON-LD, OG) — v1
  ia_probe.py      → ia.json (мягкая 404 на шаблонах, меню в HTML, sitemap, hreflang, крошки; scope: site) — v1
  axe-core         → JSON с violations (формат run_axe.py опыта I/02 или axe.run) — v1
  page-plan.yaml   → first_screen_policy, seo.indexable, x-gate-exception[{id, why, who, until}] — v1
  сохранённый HTML → заглушки и автоматические маркеры «ИИ-лендинга» (SG-CONTENT-05, 06) — v1
  CSS (--css) и <style> → clamp() кеглей ≤ 2,5 × (SG-A11Y-08); видео первого экрана отдельно (SG-WEIGHT-09) — v1.1 (K2)
v1.2 (K3, калибровка опыта K/03 на 8 страницах): SG-PERF-03 — CLS окна сессии web-vitals вместо суммы сдвигов; SG-GEO-01 —
«H1 только после JS» B только при отсутствии H1 в сыром HTML; SG-MOB-01 — B при расширенной области телефона, скрытое
переполнение — D; SG-LEGAL-01 (ЕС) — S, если до выбора загружены только библиотеки без событий и cookie; SG-LEGAL-04 — ЕС S.
v1.2 (K4, строки page-gates.yaml v1.2): SG-A11Y-01 — color-contrast B только у ключевых узлов (H1, лид первого экрана, призыв,
согласие и баннер cookie — профиль I 08/03 §8; нужен axe с адресами узлов, формат run_axe_targets.py опыта K/03), прочие узлы — S,
без адресов узлов — S, которое исключение не снимает; SG-PERF-06 — H1 первого экрана выпал из LCP (появление из opacity: 0,
маской строк, скрытием скриптом — creative E/01, Chromium 153): S при признаке в HTML или CSS, D без признака; H1 из
opacity ≈ 0,001–0,09 или clip-path — D (время LCP раньше видимости).
Строки ворот без данных помечаются SKIP (их проверяет человек, судья или соседняя утилита).

Запуск:
  python3 99-raw/tools/page_gates.py --profile landing-lead-services@L1 --anatomy DIR [--accept DIR] [--geo FILE]
         [--ia FILE] [--axe FILE] [--plan FILE] [--html FILE] [--css FILE …] [--jurisdiction ru|eu|none] [--ai-bots-policy allow-all]
         [--ads-google] [--site-level L1] [--hot-mobile-share 0.6 --price-band mid] [--json]
  python3 99-raw/tools/page_gates.py --resolve landing-lead-services@L1        # показать профиль
  python3 99-raw/tools/page_gates.py --selftest [--gates FILE]
Код выхода: 1 — есть B; 0 — нет B. Замер без троттлинга сети (как у M) помечается `lab-unthrottled`.
"""
import argparse
import copy
import datetime
import glob
import html as htmlmod
import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('site'))
DIR07 = os.path.join(ROOT, '07-seo-geo-performance-analytics')
CHECKLIST = os.path.join(ROOT, '09-ai-generation-evaluation', 'site-checklist.yaml')
LEVELS = ('L0', 'L1', 'L2')
FOREIGN_VENDORS = {'ga4', 'gtm', 'meta-pixel', 'youtube', 'google-fonts', 'recaptcha', 'google-ads', 'google-maps',
                   'microsoft-ads', 'hotjar', 'intercom', 'onetrust'}   # SG-LEGAL-07 (I): зарубежные сервисы
GATE_ID = re.compile(r'^SG-(PERF|WEIGHT|SEO|GEO|A11Y|LEGAL|CONTENT|NAV|MOB)-\d{2}$')
SEV_RANK = {'-': 0, 'D': 1, 'S': 2, 'B': 3}

# geo_probe флаг → ворота (серьёзность — из head-kit.yaml checks; условия — ниже)
GEO_FLAG_GATE = {
    'page-status-': 'SG-SEO-01', 'html-over-2mb': 'SG-SEO-01',
    'noindex': 'SG-SEO-02', 'nosnippet': 'SG-SEO-02', 'noarchive-or-nocache': 'SG-SEO-02', 'no-canonical': 'SG-SEO-02',
    'multiple-canonical': 'SG-SEO-02', 'canonical-elsewhere': 'SG-SEO-02', 'no-title': 'SG-SEO-02',
    'no-description': 'SG-SEO-02', 'no-lang': 'SG-SEO-02',
    'no-h1-in-raw': 'SG-SEO-03', 'multiple-h1': 'SG-SEO-03',
    'no-jsonld': 'SG-SEO-04', 'jsonld-parse-error': 'SG-SEO-04', 'jsonld-missing-required': 'SG-SEO-04', 'jsonld-js-only': 'SG-SEO-04',
    'og-after-1mb': 'SG-SEO-05', 'no-og-image': 'SG-SEO-05', 'og-image-relative': 'SG-SEO-05',
    'csr-shell': 'SG-GEO-01', 'raw-text-under-50-words': 'SG-GEO-01', 'raw-text-under-200-words': 'SG-GEO-01',
    'h1-js-only': 'SG-GEO-01', 'cta-js-only': 'SG-GEO-01', 'prices-js-only': 'SG-GEO-01', 'nojs-ratio-under-0.5': 'SG-GEO-01',
    'robots-5xx-or-unreachable': 'SG-GEO-02', 'robots-is-html': 'SG-GEO-02', 'robots-star-disallow-all': 'SG-GEO-02',
    'blocked-': 'SG-GEO-02', 'antibot-challenge': 'SG-GEO-02', 'tls-untrusted-chain': 'SG-GEO-02', 'ua-': 'SG-GEO-02',
}
HK_DEFAULT = {  # запасная копия head-kit.yaml 1.0 checks (флаг → серьёзность), если файл не прочитан
    'page-status-*': 'B', 'antibot-challenge': 'B', 'tls-untrusted-chain': 'B', 'html-over-2mb': 'B',
    'robots-5xx-or-unreachable': 'B', 'robots-is-html': 'B', 'blocked-google-googlebot': 'B', 'blocked-yandex-yandexbot': 'B',
    'blocked-yandex-additional': 'S', 'blocked-openai-oai-searchbot': 'S', 'blocked-perplexity-perplexitybot': 'S',
    'blocked-google-adsbot': 'B', 'csr-shell': 'B', 'raw-text-under-50-words': 'B', 'no-h1-in-raw': 'S', 'multiple-h1': 'D',
    'noindex': 'B', 'nosnippet': 'S', 'noarchive-or-nocache': 'S', 'no-canonical': 'S', 'multiple-canonical': 'S',
    'canonical-elsewhere': 'S', 'no-title': 'S', 'no-description': 'D', 'no-lang': 'D', 'no-og-image': 'D',
    'og-image-relative': 'D', 'og-after-1mb': 'S', 'no-jsonld': 'D', 'jsonld-parse-error': 'S', 'jsonld-missing-required': 'D',
    'nojs-ratio-under-0.5': 'S', 'h1-js-only': 'B', 'cta-js-only': 'S', 'prices-js-only': 'S', 'jsonld-js-only': 'S',
    'raw-text-under-200-words': 'D', 'robots-star-disallow-all': 'S', 'blocked-anthropic-claude-searchbot': 'S',
    'blocked-microsoft-bingbot': 'S', 'ua-<бот>-status-<код>': 'S', 'ua-<бот>-text-differs': 'S',
}
AI_SURFACE_BLOCKS = ('blocked-yandex-additional', 'blocked-openai-oai-searchbot', 'blocked-perplexity-perplexitybot',
                     'blocked-anthropic-claude-searchbot', 'blocked-microsoft-bingbot')
AXE_B = {'color-contrast', 'link-name', 'button-name', 'label', 'meta-viewport'}            # SG-A11Y-01 (I 08/03 §8)
AXE_KEY = ('h1', 'cta', 'consent', 'lead')   # v1.2 (K4): классы узлов color-contrast, провал которых — B (профиль I 08/03 §8)
AXE_S = {'target-size', 'image-alt', 'frame-title', 'html-has-lang', 'html-lang-valid'}     # SG-A11Y-02
PLACEHOLDER_RX = re.compile(r'lorem ipsum|\[placeholder\]|\bfeature [1-6]\b|\bjohn doe\b|\bjane doe\b|\bfictional (?:brand|company|demo)|'
                            r'\bdemo content\b|@example\.(?:com|org)|\bexample\.com\b|заглушк[аи] отзыв|\bтекст заглушк|вымышленн(?:ый|ая) (?:бренд|компани)', re.I)
FAKE_ACTIVITY_RX = re.compile(r'только что (?:купил|записал|оформил|заказал)|(?:\d+|несколько) (?:человек|посетител\w*) (?:смотр|сейчас)|'
                              r'сейчас смотр\w+ \d+|just (?:purchased|bought|signed up)|\d+ people are (?:viewing|looking)|someone in [A-Z]\w+ (?:just|recently)', re.I)
COUNTDOWN_RX = re.compile(r'(?:setDate\s*\(\s*\w+\.getDate\(\)\s*\+|getDate\(\)\s*\+\s*\d|countdown|обратн\w+ отсч)', re.I)
PROMO_RX = re.compile(r'акци|скидк|sale|offer ends|до конца', re.I)


def load_yaml(path):
    import yaml
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(out.get(k, {}), v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def resolve_profile(profile_id, budgets, site_level=None, hot_mobile_share=None, price_band=None):
    """<page_type>@L<n> → профиль (outcome, weight, all_levels) + журнал решений."""
    log = []
    if '@' in profile_id:
        page_type, level = profile_id.split('@', 1)
    else:
        page_type, level = profile_id, None
    defaults = budgets['page_type_levels']['default']
    known = {pt: lv for lv, pts in defaults.items() for pt in pts}
    if page_type not in known:
        raise ValueError(f'page_type {page_type!r} нет в budgets.yaml page_type_levels (словарь B)')
    if level is None:
        level = known[page_type]
        log.append(f'уровень по умолчанию для {page_type}: {level} (PLAN решение 20)')
        if page_type == 'landing-lead-services' and hot_mobile_share is not None and hot_mobile_share >= 0.5 \
                and price_band in ('low', 'mid'):
            level = 'L0'
            log.append('горячий трафик с телефонов ≥ 50 % и price_band low/mid → L0 (решение 20)')
    if level not in LEVELS:
        raise ValueError(f'уровень {level!r} не из {LEVELS}')
    if site_level and LEVELS.index(level) > LEVELS.index(site_level):
        log.append(f'уровень страницы {level} выше уровня сайта {site_level} → понижен до {site_level}')
        level = site_level
    prof = deep_merge({'outcome': budgets['levels'][level]['outcome'], 'weight': budgets['levels'][level]['weight']}, {})
    key = f'{page_type}@{level}'
    ov = (budgets.get('overrides') or {}).get(key)
    if ov:
        prof = deep_merge(prof, {k: v for k, v in ov.items() if k in ('outcome', 'weight')})
        log.append(f'исключение {key}: {ov.get("why", "")[:120]}')
    prof['all_levels'] = budgets.get('all_levels', {})
    prof.update({'id': key, 'page_type': page_type, 'level': level, 'log': log})
    return prof


def dev_val(node, device, key='goal'):
    """Порог из узла профиля: {mobile: X, desktop: Y} | {mobile: {goal, poor}} | {goal, poor} | {max}."""
    if node is None:
        return None
    if device in node:
        v = node[device]
        return v.get(key) if isinstance(v, dict) else (v if key in ('goal', 'max') else None)
    return node.get(key)


def g(d, *path, default=None):
    for p in path:
        if not isinstance(d, dict):
            return default
        d = d.get(p)
        if d is None:
            return default
    return d


def load_anatomy(dirpath):
    out = {}
    for dev in ('desktop', 'mobile'):
        fp = os.path.join(dirpath, f'anatomy_{dev}.json')
        if os.path.exists(fp):
            with open(fp, encoding='utf-8') as f:
                out[dev] = json.load(f)
    return out


def load_accept(dirpath):
    out = {}
    for fp in glob.glob(os.path.join(dirpath or '', 'accept_*.json')):
        with open(fp, encoding='utf-8') as f:
            d = json.load(f)
        mode = os.path.basename(fp)[7:-5]          # accept_<mode>.json
        dev = 'mobile' if 'mobile' in mode else 'desktop'
        thr = 'throttle' in mode
        out[(dev, thr)] = d
    return out


def load_json(path):
    if not path:
        return None
    if os.path.isdir(path):
        fs = sorted(glob.glob(os.path.join(path, '*.json')))
        path = fs[0] if fs else None
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def load_headkit(path):
    try:
        hk = load_yaml(path)
        return {c['flag']: c.get('severity') for c in (hk.get('checks') or []) if c.get('flag')}
    except Exception:  # noqa: BLE001
        return dict(HK_DEFAULT)


class Gate:
    def __init__(self, gid, device, status, value, threshold, severity, note=''):
        self.__dict__.update(id=gid, device=device, status=status, value=value, threshold=threshold, severity=severity,
                             note=note)


def cmp_outcome(gid, dev, value, node, note=''):
    goal, poor = dev_val(node, dev, 'goal'), dev_val(node, dev, 'poor')
    if value is None:
        return Gate(gid, dev, 'SKIP', None, f'S>{goal} B>{poor}', '-', note or 'нет данных')
    if poor is not None and value > poor:
        return Gate(gid, dev, 'FAIL', value, poor, 'B', note)
    if goal is not None and value > goal:
        return Gate(gid, dev, 'FAIL', value, goal, 'S', note)
    return Gate(gid, dev, 'PASS', value, goal, '-', note)


def cmp_weight(gid, dev, value, limit, note=''):
    if value is None or limit is None:
        return Gate(gid, dev, 'SKIP', value, limit, '-', note or 'нет данных')
    return Gate(gid, dev, 'FAIL' if value > limit else 'PASS', round(value, 1), limit, 'S' if value > limit else '-', note)


def worst(items):
    """[(sev, what)] → (худшая серьёзность, список)."""
    items = [x for x in items if x[0] in ('B', 'S', 'D')]
    if not items:
        return '-', []
    top = max(items, key=lambda x: SEV_RANK[x[0]])[0]
    return top, [w for _, w in items]


TRACK_COOKIE = re.compile(r'^(?:_ga|_gid|_gcl|_fbp|_fbc|_uetsid|_uetvid|MUID|_ym_uid|_ym_d|_ym_isad|_hj|AMP_|ajs_|_clck|_clsk|'
                          r'_ttp|_pin_unauth|_tt_enable|tmr_|_scid|_rdt_uuid|li_|bcookie|IDE|NID|test_cookie)', re.I)
SCRIPT_URL = re.compile(r'\.js(?:\.gz)?(?:$|\?)|/gtm\.js|/gtag/js|/libs/|/tag\.js|/sdk', re.I)


def tracking_evidence(d):
    """v1.2 (K3): чем подтверждён трекинг до выбора — запросы, отправляющие данные (не загрузка скрипта), и cookie трекинга."""
    reqs = g(d, 'network', 'tracking_requests', default=[]) or []
    sent = sorted({r.get('vendor') or '?' for r in reqs if r.get('phase') in ('load', 'scroll', 'pre')
                   and not SCRIPT_URL.search(r.get('u') or '')})
    cookies = []
    for c in d.get('cookies_before') or []:
        name = c[0] if isinstance(c, (list, tuple)) and c else (c.get('name') if isinstance(c, dict) else str(c))
        if name and TRACK_COOKIE.match(name):
            cookies.append(name)
    return sent, sorted(set(cookies))


def letters(t):
    return re.sub(r'[^0-9a-zа-яё]', '', (t or '').lower())


def h1_nojs_item(d, s):
    """v1.2 (K3): «H1 только после JS» — B, только если H1 нет в сыром HTML. Если H1 в HTML есть, а сравнение текста упало
    (innerText склеивает слова на скрытых <br> — опыт K/03: ru-matemarketing, телефон), текст сверяется без пробелов и регистра."""
    if s.get('nojs_h1') or (s.get('h1_n') or 0) < 1:
        return ('-', '')
    nj = d.get('nojs') or {}
    if nj.get('h1_raw_n') is None:
        return ('B', 'h1-js-only')
    if nj.get('h1_raw_n', 0) == 0:
        return ('B', 'h1-js-only')
    shown = [letters(x) for x in (g(d, 'dom', 'headings', 'h1', default=[]) or [])]
    raw = [letters(x) for x in (nj.get('h1_raw') or [])]
    if any(a and b and (a[:30] in b or b[:30] in a) for a in shown for b in raw):
        return ('-', '')
    return ('D', 'h1 в HTML есть, текст отличается от видимого')


# ---------------------------------------------------------------- v1.2 (K4): H1 и LCP (creative E/01), контраст по узлам
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
OPACITY_RX = re.compile(r'opacity\s*:\s*([\d.]+)', re.I)
ZERO_OPACITY_RX = re.compile(r'(?:^|[;{\s])opacity\s*:\s*0(?:\.0+)?\s*(?:;|}|$|!)', re.I)
SPLIT_MASK_RX = re.compile(r'SplitText|SplitType|split-type|Splitting\(|mask\s*:\s*["\']lines', re.I)


class _H1Chain(HTMLParser):
    """Цепочки «H1 + 4 ближайших предка» (тег, атрибуты) из сырого HTML."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.chains = [], []

    def handle_starttag(self, tag, attrs):
        if tag in VOID_TAGS:
            return
        a = {k: (v or '') for k, v in attrs}
        if tag == 'h1':
            self.chains.append([(tag, a)] + list(reversed(self.stack[-4:])))
        self.stack.append((tag, a))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def hidden_selectors(css):
    """Классы и теги, которые CSS прячет в начальном состоянии: правило с opacity: 0 или анимация из @keyframes с 0%/from
    opacity: 0 (субъект селектора — последний простой селектор). Lovable-подобное «из opacity: .35» признаком не считается."""
    kf = {m.group(1) for m in re.finditer(r'@keyframes\s+([\w-]+)\s*\{\s*(?:from|0%)\s*\{([^{}]*)\}', css or '')
          if ZERO_OPACITY_RX.search(' ' + m.group(2))}
    out = set()
    for m in re.finditer(r'([^{}@;]+)\{([^{}]*)\}', css or ''):
        sel, body = m.group(1), ' ' + m.group(2)
        hid = ZERO_OPACITY_RX.search(body) or any(re.search(r'animation(?:-name)?\s*:[^;]*\b' + re.escape(k) + r'\b', body) for k in kf)
        if not hid:
            continue
        for part in sel.split(','):
            subj = re.split(r'[\s>+~]+', part.strip())[-1] if part.strip() else ''
            subj = re.sub(r':{1,2}[\w-]+(?:\([^)]*\))?', '', subj)   # без :not(), ::before и т. п.
            for c in re.findall(r'\.([\w-]+)', subj):
                out.add('.' + c)
            t = re.match(r'^([a-z][a-z0-9]*)', subj)
            if t:
                out.add(t.group(1))
    return out


def h1_reveal_evidence(raw, css=''):
    """Признаки «H1 первого кадра невидим» в сыром HTML и CSS (creative E/01): hidden — opacity 0 (стиль, класс opacity-0,
    правило CSS, анимация из 0), visibility: hidden, класс invisible у H1 или 4 ближайших предков, скрипт разбивки с маской
    строк; near_zero — opacity 0 < x < 0,1 (Framer appear 0.001) или clip-path — H1 остаётся кандидатом, но LCP раньше показа."""
    res = {'hidden': [], 'near_zero': []}
    if not raw and not css:
        return res
    styles = ' '.join(re.findall(r'(?is)<style\b[^>]*>(.*?)</style>', raw or ''))
    hid = hidden_selectors((css or '') + '\n' + styles)
    p = _H1Chain()
    try:
        p.feed(raw or '')
    except Exception:  # noqa: BLE001
        pass
    for chain in p.chains[:6]:
        for depth, (tag, a) in enumerate(chain):
            who = 'H1' if depth == 0 else f'предок {depth} <{tag}>'
            st = a.get('style', '')
            cls = a.get('class', '').split()
            m = OPACITY_RX.search(st)
            if m:
                try:
                    v = float(m.group(1))
                except ValueError:
                    v = None
                if v == 0:
                    res['hidden'].append(f'{who}: style opacity 0')
                elif v is not None and v < 0.1:
                    res['near_zero'].append(f'{who}: style opacity {m.group(1)}' + (' (Framer appear)' if a.get('data-framer-appear-id') else ''))
            if re.search(r'visibility\s*:\s*hidden', st, re.I):
                res['hidden'].append(f'{who}: visibility hidden')
            if re.search(r'clip-path\s*:', st, re.I):
                res['near_zero'].append(f'{who}: clip-path')
            bad = [c for c in cls if c in ('opacity-0', 'invisible') or '.' + c in hid]
            if bad:
                res['hidden'].append(f'{who}: класс {bad[0]}')
            if depth == 0 and 'h1' in hid:
                res['hidden'].append('H1: правило CSS h1 {opacity: 0}')
    if SPLIT_MASK_RX.search(raw or ''):
        res['hidden'].append('скрипт разбивки строк (SplitText, mask lines)')
    res['hidden'] = sorted(set(res['hidden']))
    res['near_zero'] = sorted(set(res['near_zero']))
    return res


def lcp_h1_item(d, rv):
    """SG-PERF-06 (v1.2, K4): H1 первого экрана не стал кандидатом LCP, а LCP — другой текст (лид, H2): S при признаке
    невидимого первого кадра в HTML или CSS, D без признака (лид может быть больше H1 по площади); H1 — кандидат, но
    проявляется из opacity ≈ 0 или clip-path — D (время LCP раньше видимости; допустимо при раскрытии ≤ 800 мс)."""
    h = g(d, 'dom', 'headings', default={}) or {}
    lcps = (g(d, 'pre', 'lcp', default=[]) or []) + (g(d, 'fin', 'lcp', default=[]) or [])
    if not lcps or not h.get('h1_first_screen'):
        return ('-', '')
    h1s = [letters(x)[:24] for x in h.get('h1') or [] if letters(x)]

    def is_h1(e):
        if (e.get('tag') or '').upper() == 'H1':
            return True
        t = letters(e.get('text'))
        return bool(t) and any(x in t or t[:24] in x for x in h1s)

    final = (g(d, 'fin', 'lcp', default=[]) or g(d, 'pre', 'lcp', default=[]) or [{}])[-1]
    cand = any(is_h1(e) for e in lcps)
    if not cand and not final.get('url') and final.get('text'):
        what = f"LCP — {final.get('tag')} «{(final.get('text') or '')[:24]}», H1 не кандидат"
        if rv['hidden']:
            return ('S', what + '; ' + rv['hidden'][0])
        return ('D', what + '; признаков в HTML нет — проверить появление H1 (или лид больше H1)')
    if cand and rv['near_zero']:
        return ('D', 'H1 проявляется: ' + rv['near_zero'][0] + ' — время LCP раньше видимости')
    return ('-', '')


def cta_texts(anatomy):
    """Тексты призывов (кнопки filled и outline) из анатомии — для класса узла cta (как axe_classify.py опыта K/03)."""
    out = set()
    for d in (anatomy or {}).values():
        for c in g(d, 'dom', 'ctas', default=[]) or []:
            if isinstance(c, dict) and c.get('style') in ('filled', 'outline'):
                t = norm_label(c.get('t'))
                if t:
                    out.add(t)
    return out


def norm_label(t):
    return re.sub(r'\s+', ' ', re.sub(r'[\[\]→›»«"“”↗]', ' ', (t or '').lower())).strip()


def axe_node_class(n, ctas):
    """Класс узла color-contrast (формат run_axe_targets.py K/03: in_h1, cookie, in_form, action, first_screen, in_header,
    in_footer, text); узел axe.run без флагов — по тегу из html (<h1 → h1), иначе unknown."""
    if not isinstance(n, dict):
        return 'unknown'
    if not any(k in n for k in ('in_h1', 'action', 'first_screen', 'in_form', 'cookie')):
        return 'h1' if re.match(r'\s*<h1\b', n.get('html') or '', re.I) else 'unknown'
    if n.get('in_h1'):
        return 'h1'
    # баннер cookie — ключевой; строка «мы используем cookie» в подвале ниже первого экрана — нет (K/03: ru-matemarketing)
    if n.get('in_form') or (n.get('cookie') and (not n.get('in_footer') or n.get('first_screen'))):
        return 'consent'
    if n.get('action'):
        if ctas:
            return 'cta' if norm_label(n.get('text')) in ctas else 'other'
        return 'cta' if n.get('first_screen') and not n.get('in_header') else 'other'
    if n.get('first_screen') and not n.get('in_header') and not n.get('in_footer'):
        return 'lead'
    return 'other'


def plan_info(plan):
    pg = (plan or {}).get('page') or {}
    seo = pg.get('seo') or {}
    return {'policy': pg.get('first_screen_policy'), 'indexable': seo.get('indexable', True),
            'structured_data': seo.get('structured_data') or [],
            'exceptions': pg.get('x-gate-exception') or pg.get('x_gate_exception') or []}


def evaluate(prof, anatomy, accept=None, jurisdiction='ru', geo=None, ia=None, axe=None, plan=None, html_text=None,
             headkit=None, ai_bots_policy='allow-all', ads_google=False, css_text=None):
    accept = accept or {}
    headkit = headkit or dict(HK_DEFAULT)
    pi = plan_info(plan)
    R = []
    oc, wt, al = prof['outcome'], prof['weight'], prof['all_levels']
    cta_fs = {}
    rv = h1_reveal_evidence(html_text, css_text) if (html_text or css_text) else {'hidden': [], 'near_zero': []}
    for dev, d in anatomy.items():
        s = d.get('summary') or {}
        # SG-PERF-01/02: LCP — сначала page_accept с троттлингом (телефон), иначе анатомия как диагностика
        acc = accept.get((dev, dev == 'mobile'))
        if acc and g(acc, 'lcp', 't') is not None:
            R.append(cmp_outcome('SG-PERF-01' if dev == 'mobile' else 'SG-PERF-02', dev, g(acc, 'lcp', 't'),
                                 oc['lcp_ms_lab'], 'page_accept' + (' --throttle' if dev == 'mobile' else '')))
        else:
            R.append(cmp_outcome('SG-PERF-01' if dev == 'mobile' else 'SG-PERF-02', dev, s.get('lcp_ms'), oc['lcp_ms_lab'],
                                 'lab-unthrottled: диагностика, не приёмка' if dev == 'mobile' else 'anatomy, без троттлинга'))
        # SG-PERF-03 (v1.2, K3): CLS — окно сессии web-vitals (fin.wv_cls), а не сумма всех сдвигов (summary.cls_session):
        # сумма завышала CLS прокрутки (опыт K/03: ru-azbukaokon телефон — сумма 0,42, web-vitals 0,15)
        wv_cls = g(d, 'fin', 'wv_cls')
        if isinstance(wv_cls, (int, float)):
            R.append(cmp_outcome('SG-PERF-03', dev, wv_cls, oc['cls_lab'], 'web-vitals CLS (окно сессии)'))
        else:
            R.append(cmp_outcome('SG-PERF-03', dev, s.get('cls_session', s.get('cls')), oc['cls_lab'], 'сумма сдвигов — верхняя оценка'))
        inp = s.get('inp_wv_ms') if s.get('inp_wv_ms') is not None else s.get('inp_lab_ms')
        R.append(cmp_outcome('SG-PERF-04', dev, inp, oc['inp_ms_lab_scenario'], 'сценарий после загрузки — занижает'))
        tbt_goal = dev_val(oc['tbt_ms_lab'], dev, 'goal')
        R.append(cmp_weight('SG-PERF-05', dev, s.get('tbt_ms'), tbt_goal, 'TBT до прокрутки'))
        # SG-PERF-06: LCP-элемент
        lcp_list = g(d, 'fin', 'lcp', default=[]) or g(d, 'pre', 'lcp', default=[]) or []
        last = lcp_list[-1] if lcp_list else {}
        tag = (last.get('tag') or '').upper()
        if not lcp_list:
            R.append(Gate('SG-PERF-06', dev, 'FAIL', 'нет LCP', 'LCP есть', 'B'))
        elif tag == 'CANVAS':
            R.append(Gate('SG-PERF-06', dev, 'FAIL', tag, 'не canvas', 'B'))
        else:
            lazy = g(acc or {}, 'lcp', 'lazy')
            rsev, rwhat = lcp_h1_item(d, rv)
            if lazy:
                R.append(Gate('SG-PERF-06', dev, 'FAIL', 'lazy', 'LCP-картинка без lazy', 'B'))
            elif rwhat:
                # v1.2 (K4): H1 первого кадра невидим → в Chromium выпадает из LCP (creative E/01; поле CrUX — Chrome)
                R.append(Gate('SG-PERF-06', dev, 'FAIL', rwhat[:90], 'H1 без opacity 0, маски строк, скрытия скриптом', rsev,
                              'creative E/01 (Chromium 153): честно — только transform; opacity ≥ 0,01 и clip-path — LCP раньше показа'))
            else:
                R.append(Gate('SG-PERF-06', dev, 'PASS', tag or '?', 'H1/картинка/постер', '-',
                              'lazy/fetchpriority — только из page_accept' if not acc else ''))
        # SG-PERF-09: тяжёлые виджеты до ввода
        fs_t = g(d, 'first_screen', 't', default=None)
        tp = g(d, 'network', 'third_party', default=[]) or []
        widgets = [t['domain'] for t in tp if set(t.get('cats') or []) & {'chat', 'maps', 'video', 'booking', 'social'}
                   and (fs_t is None or (t.get('first_t') or 0) <= fs_t)]
        R.append(Gate('SG-PERF-09', dev, 'FAIL' if widgets else 'PASS', ','.join(widgets) or '—', 'по видимости/нажатию',
                      'S' if widgets else '-'))
        # WEIGHT
        R.append(cmp_weight('SG-WEIGHT-01', dev, s.get('first_screen_kb'), dev_val(wt['first_screen_kb'], dev)))
        R.append(cmp_weight('SG-WEIGHT-02', dev, s.get('session_kb'), dev_val(wt['session_kb'], dev)))
        R.append(cmp_weight('SG-WEIGHT-03', dev, g(d, 'first_screen', 'by_type_kb', 'script'), dev_val(wt['js_first_screen_kb'], dev)))
        R.append(cmp_weight('SG-WEIGHT-04', dev, g(d, 'network', 'by_type_kb', 'font'), dev_val(wt['fonts_kb'], dev)))
        before = [t for t in tp if fs_t is None or (t.get('first_t') or 0) <= fs_t]
        R.append(cmp_weight('SG-WEIGHT-05', dev, len(before), wt['third_party_origins_before_input']['max'],
                            'сторонние eTLD+1 в окне первого экрана'))
        R.append(cmp_weight('SG-WEIGHT-06', dev, sum(t.get('kb') or 0 for t in before), wt['third_party_first_screen_kb']['max'],
                            'КБ домена за сессию — верхняя оценка'))
        R.append(cmp_weight('SG-WEIGHT-07', dev, g(d, 'nav', 'html_kb'), al.get('html_transfer_kb', {}).get('goal'), 'HTML по сети'))
        # SG-WEIGHT-09 (K2, v1.1): видео первого экрана без действия — отдельной цифрой (замечание creative 2026-09-24, п.3)
        vid = g(d, 'first_screen', 'by_type_kb', 'media') or 0
        fs_lim = dev_val(wt['first_screen_kb'], dev)
        if not vid:
            R.append(Gate('SG-WEIGHT-09', dev, 'PASS', 0, 'видео отдельно', '-', 'видео в окне первого экрана нет'))
        elif fs_lim is not None and vid > fs_lim:
            R.append(Gate('SG-WEIGHT-09', dev, 'FAIL', round(vid, 1), fs_lim, 'S', 'одно видео больше бюджета первого экрана профиля'))
        else:
            R.append(Gate('SG-WEIGHT-09', dev, 'FAIL', round(vid, 1), 'видео отдельно', 'D',
                          'есть видео без действия: постер, reduce = 0 байт, вертикальный файл телефону (SITE-PERF-13)'))
        # SG-SEO-02 (строка H2 v1): noindex при индексируемой — B; нет title или canonical — S; нет lang — D
        if s.get('noindex'):
            R.append(Gate('SG-SEO-02', dev, 'FAIL' if pi['indexable'] else 'PASS', 'noindex', 'по seo.indexable',
                          'B' if pi['indexable'] else '-', 'индексируемая по плану' if pi['indexable'] else 'noindex по плану'))
        else:
            sev, what = worst([('S', 'title') if not s.get('title_len') else ('-', ''),
                               ('S', 'canonical') if not s.get('canonical') else ('-', ''),
                               ('D', 'lang') if not s.get('lang') else ('-', '')])
            R.append(Gate('SG-SEO-02', dev, 'FAIL' if what else 'PASS', ','.join(what) or 'ok', 'title, canonical (S); lang (D)', sev))
        # SG-SEO-03 (строка H2 v1): нет H1 — S; больше одного — D
        h1 = s.get('h1_n')
        if h1 is None:
            R.append(Gate('SG-SEO-03', dev, 'SKIP', None, 'ровно 1', '-'))
        else:
            R.append(Gate('SG-SEO-03', dev, 'PASS' if h1 == 1 else 'FAIL', h1, 'нет H1 — S; > 1 — D',
                          '-' if h1 == 1 else ('S' if h1 == 0 else 'D')))
        # SG-GEO-01 (строка H2 v1): H1 только после JS — B; CTA или цены после JS — S; доля < 0,5 — S; < 0,8 — D
        if s.get('nojs_h1') is None:
            R.append(Gate('SG-GEO-01', dev, 'SKIP', None, 'H1, CTA, цены в HTML', '-'))
        else:
            ratio = s.get('nojs_text_ratio')
            items = [h1_nojs_item(d, s), ('S', 'cta-js-only') if not s.get('nojs_cta') else ('-', '')]
            if s.get('nojs_prices') is False:
                items.append(('S', 'prices-js-only'))
            if ratio is not None:
                items.append(('S', f'ratio {ratio:.2f} < 0,5') if ratio < 0.5 else (('D', f'ratio {ratio:.2f} < 0,8') if ratio < 0.8 else ('-', '')))
            sev, what = worst(items)
            R.append(Gate('SG-GEO-01', dev, 'FAIL' if what else 'PASS', ','.join(what) or (f'ratio {ratio}' if ratio is not None else 'ok'),
                          'H1 — B; CTA, цены, < 0,5 — S; < 0,8 — D', sev, f"цены: {s.get('nojs_prices')}"))
        # SG-MOB-01, 02 (K v1)
        if dev == 'mobile':
            ov = s.get('overflow_x_px')
            zoomed = s.get('layout_zoomed')
            if ov is None and zoomed is None:
                R.append(Gate('SG-MOB-01', dev, 'SKIP', None, 'нет переполнения', '-'))
            elif zoomed or ((ov or 0) > 2 and zoomed is None):
                R.append(Gate('SG-MOB-01', dev, 'FAIL', f'{ov} px, zoomed={zoomed}', 'область телефона не расширена', 'B'))
            elif (ov or 0) > 2:
                # v1.2 (K3): scrollWidth больше экрана, но область не расширена — переполнение скрыто overflow-x (опыт K/03:
                # en-headspace — дорожка карусели 1 307 px под html,body{overflow-x:hidden}); прокрутки у человека нет
                R.append(Gate('SG-MOB-01', dev, 'FAIL', f'{ov} px, zoomed=False', 'область телефона не расширена', 'D',
                              'переполнение скрыто overflow-x — проверить свайпом на iOS'))
            else:
                R.append(Gate('SG-MOB-01', dev, 'PASS', f'{ov} px, zoomed={zoomed}', '≤ 2 px', '-'))
            if s.get('burger') is None and s.get('header_nav_links') is None:
                R.append(Gate('SG-MOB-02', dev, 'SKIP', None, 'меню или ≥ 2 ссылки', '-'))
            else:
                ok = bool(s.get('burger')) or (s.get('header_nav_links') or 0) >= 2
                R.append(Gate('SG-MOB-02', dev, 'PASS' if ok else 'FAIL', f"burger={s.get('burger')} links={s.get('header_nav_links')}",
                              'меню или ≥ 2 ссылки', '-' if ok else 'S', 'подтвердить кадром; не для одноэкранной арт-страницы'))
        cta_fs[dev] = s.get('cta_first_screen')
        # LEGAL (I); jurisdiction none — строки права пропускаются
        if jurisdiction == 'none':
            continue
        tb = s.get('tracking_before_action')
        if tb:
            sent, cookies = tracking_evidence(d)
            if jurisdiction == 'eu' and not sent and not cookies and g(d, 'network', 'tracking_requests') is not None:
                # v1.2 (K3): до выбора только загрузка библиотек (gtm.js, SDK) без отправки событий и без cookie трекинга —
                # S [спорно]: передача IP поставщику, не хранение на устройстве (опыт K/03: en-headspace)
                R.append(Gate('SG-LEGAL-01', dev, 'FAIL', tb, 'после согласия', 'S',
                              'до выбора загружены только библиотеки: событий и cookie трекинга нет [спорно]; грузить после согласия'))
            else:
                R.append(Gate('SG-LEGAL-01', dev, 'FAIL', tb, 'после согласия', 'B' if jurisdiction == 'eu' else 'S',
                              'ЕС — блокер; РФ — позиция I [спорно]' + (f'; события: {",".join(sent[:3])}' if sent else '') +
                              (f'; cookie: {",".join(cookies[:3])}' if cookies else '')))
        else:
            R.append(Gate('SG-LEGAL-01', dev, 'PASS', '—', 'после согласия', '-'))
        if s.get('cmp') not in (None, 'none'):
            bad = [k for k in ('cmp_reject_first_layer', 'cmp_reject_equal') if s.get(k) is False or s.get(k) == 0]
            R.append(Gate('SG-LEGAL-02', dev, 'FAIL' if bad else 'PASS', ','.join(bad) or 'ok', 'отказ на 1-м уровне, равный',
                          ('B' if jurisdiction == 'eu' else 'S') if bad else '-', 'cmp_reject_equal у M ненадёжен — подтвердить кадром'))
        if s.get('forms_n'):
            bad = [k for k, v in (('consent_separate', s.get('consent_separate') is False),
                                  ('consent_prechecked', s.get('consent_prechecked') is True)) if v]
            if jurisdiction == 'ru':
                R.append(Gate('SG-LEGAL-03', dev, 'FAIL' if bad else 'PASS', ','.join(bad) or 'ok', 'отдельное согласие без checked',
                              'B' if bad else '-', '152-ФЗ в ред. 156-ФЗ, с 01.09.2025'))
            pol = s.get('policy_link_in_form')
            # v1.2 (K3): РФ — B (LR-RU-05, 152-ФЗ ст. 18.1); ЕС — S (LR-EU-06: уведомление при сборе, serious)
            R.append(Gate('SG-LEGAL-04', dev, 'FAIL' if pol is False else 'PASS', pol, 'ссылка на политику в форме',
                          ('B' if jurisdiction == 'ru' else 'S') if pol is False else '-',
                          'ЕС: LR-EU-06 (serious)' if pol is False and jurisdiction != 'ru' else ''))
        if jurisdiction == 'ru':
            ogrn = s.get('footer_ogrn')
            R.append(Gate('SG-LEGAL-05', dev, 'FAIL' if not ogrn else 'PASS', ogrn, 'ОГРН/ОГРНИП в подвале', 'B' if not ogrn else '-',
                          'B2C; реквизиты могут стоять на странице контактов — подтвердить'))
            foreign = sorted({v for t in tp for v in (t.get('vendors') or [])} & FOREIGN_VENDORS)
            R.append(Gate('SG-LEGAL-07', dev, 'FAIL' if foreign else 'PASS', ','.join(foreign) or '—', 'нет или уведомление РКН',
                          'S' if foreign else '-'))
    # SG-CONTENT-07 (K v1): призыв в первом экране по политике плана
    if cta_fs:
        pol = pi['policy'] or 'offer-cta'
        zero = [dev for dev, n in cta_fs.items() if n is not None and n == 0]
        known_n = [dev for dev, n in cta_fs.items() if n is not None]
        if not known_n:
            R.append(Gate('SG-CONTENT-07', 'page', 'SKIP', None, 'призыв в первом экране', '-'))
        elif pol == 'poster':
            R.append(Gate('SG-CONTENT-07', 'page', 'PASS', f'poster; {cta_fs}', 'призыв в шапке + продолжение', '-', 'шапку проверить кадром'))
        else:
            sev = 'B' if len(zero) == len(known_n) and len(known_n) == 2 else ('S' if zero else '-')
            R.append(Gate('SG-CONTENT-07', 'page', 'FAIL' if zero else 'PASS', str(cta_fs), f'{pol}: ≥ 1 на каждом устройстве', sev,
                          'распознавание призыва — эвристика M; провал подтверждать кадром' + ('' if pi['policy'] else '; политика не задана — offer-cta')))
    # SG-CONTENT-04: консоль (page_accept)
    cons = [m for acc in accept.values() for m in (acc.get('console') or []) if str(m).startswith('error')]
    if accept:
        R.append(Gate('SG-CONTENT-04', 'page', 'FAIL' if cons else 'PASS', len(cons), '0 ошибок консоли', 'S' if cons else '-',
                      '; '.join(str(c)[:60] for c in cons[:2])))
    # geo_probe (сырой HTML и robots): флаги → ворота с серьёзностью head-kit
    if geo is not None:
        R.extend(eval_geo(geo, headkit, pi, ai_bots_policy, ads_google))
    if ia is not None:
        R.extend(eval_ia(ia))
    if axe is not None:
        R.extend(eval_axe(axe, cta_texts(anatomy)))
    if html_text is not None:
        R.extend(eval_html(html_text, css_text or ''))
    elif css_text:
        R.append(eval_clamp('', css_text))
    return apply_exceptions(R, pi['exceptions'])


def eval_geo(geo, headkit, pi, ai_bots_policy='allow-all', ads_google=False):
    flags = geo.get('flags') or []
    per_gate = {}
    for f in flags:
        gate = next((gid for pre, gid in GEO_FLAG_GATE.items() if f == pre or (pre.endswith('-') and f.startswith(pre))), None)
        if gate is None:
            continue
        key = 'page-status-*' if f.startswith('page-status-') else f
        if f.startswith('ua-'):
            key = 'ua-<бот>-text-differs' if f.endswith('text-differs') else 'ua-<бот>-status-<код>'
        sev = headkit.get(key) or HK_DEFAULT.get(key) or 'S'
        if f == 'noindex' and not pi['indexable']:
            continue
        if f in AI_SURFACE_BLOCKS and ai_bots_policy == 'deny-all':
            continue
        if f == 'blocked-google-adsbot' and not ads_google:
            continue
        if f == 'no-jsonld' and not pi['structured_data']:
            continue
        per_gate.setdefault(gate, []).append((sev, f))
    out = []
    for gid in ('SG-SEO-01', 'SG-SEO-02', 'SG-SEO-03', 'SG-SEO-04', 'SG-SEO-05', 'SG-GEO-01', 'SG-GEO-02'):
        sev, what = worst(per_gate.get(gid, []))
        out.append(Gate(gid, 'raw', 'FAIL' if what else 'PASS', ','.join(what) or 'нет флагов', 'head-kit.yaml checks', sev,
                        'geo_probe: сырой HTML и robots'))
    return out


def eval_ia(ia):
    s = ia.get('summary') or {}
    out = []
    nf = str(s.get('not_found') or (ia.get('not_found') or {}).get('verdict') or '')
    if nf:
        ok = nf.startswith('ok')
        out.append(Gate('SG-SEO-01', 'site', 'PASS' if ok else 'FAIL', nf, 'несуществующий URL → 404', '-' if ok else 'B', 'ia_probe: мягкая 404'))
    sm = ia.get('sitemap') or {}
    if sm:
        urls = sm.get('urls') or 0
        declared = bool((ia.get('robots') or {}).get('sitemaps'))
        bad = [x for x, c in (('нет URL', urls == 0), ('не объявлен в robots.txt', not declared)) if c]
        out.append(Gate('SG-SEO-06', 'site', 'FAIL' if bad else 'PASS', ','.join(bad) or f'{urls} URL', 'sitemap объявлен, URL есть',
                        'S' if bad else '-'))
    if s.get('lang_switch') is not None:
        bad = bool(s.get('lang_switch')) and not s.get('hreflang_pages')
        out.append(Gate('SG-SEO-08', 'site', 'FAIL' if bad else 'PASS', f"switch={s.get('lang_switch')} hreflang={s.get('hreflang_pages')}",
                        'hreflang при языках', 'S' if bad else '-'))
    if 'home_header_items' in s:
        items = s.get('home_header_items') or []
        out.append(Gate('SG-NAV-01', 'site', 'PASS' if items else 'FAIL', len(items), 'меню в сыром HTML', '-' if items else 'S',
                        'ia_probe без JS; если браузер меню видит — меню собирает скрипт'))
    ci, bl = s.get('crumbs_inner_pct'), s.get('breadcrumb_ld_pct')
    if ci is not None and bl is not None:
        bad = abs((ci or 0) - (bl or 0)) > 50
        out.append(Gate('SG-NAV-02', 'site', 'FAIL' if bad else 'PASS', f'крошки {ci} %, разметка {bl} %', 'разметка = видимому', 'D' if bad else '-'))
    return out


def eval_axe(axe, ctas=None):
    """SG-A11Y-01, 02. v1.2 (K4): color-contrast — B только у ключевых узлов (H1, лид первого экрана, призыв, согласие и
    баннер cookie; профиль I 08/03 §8), прочие узлы — S; без адресов узлов (счётчики I/02) — S, которое исключение не снимает:
    сначала проверить ключевые элементы (axe с адресами узлов, page_accept.py --contrast <селекторы> или кадр)."""
    v = (axe.get('axe') or axe).get('violations') or []
    ids = {x.get('id') for x in v}
    b, s = sorted((ids & AXE_B) - {'color-contrast'}), sorted(ids & AXE_S)
    items = [('B', x) for x in b]
    unknown = False
    for x in v:
        if x.get('id') != 'color-contrast':
            continue
        nodes = x.get('nodes')
        cls = {}
        for n in nodes if isinstance(nodes, list) else []:
            c = axe_node_class(n, ctas or set())
            cls[c] = cls.get(c, 0) + 1
        key = {k: cls[k] for k in AXE_KEY if cls.get(k)}
        if key:
            items.append(('B', 'color-contrast[' + ' '.join(f'{k} {n}' for k, n in key.items()) + ']'))
        elif cls.get('unknown') or not isinstance(nodes, list):
            unknown = True
            items.append(('S', f"color-contrast[{x.get('nodes_n') or (nodes if isinstance(nodes, int) else len(nodes or []))} без адресов]"))
        else:
            items.append(('S', f"color-contrast[прочие {cls.get('other', 0)}]"))
    sev, what = worst(items)
    note = ''
    if any(w.startswith('color-contrast[') and s_ == 'B' for s_, w in items):
        note = 'класс узла — эвристика (адрес, текст призыва из анатомии): ключевой провал подтвердить кадром'
    if unknown:
        note = (note + '; ' if note else '') + 'контраст без адресов узлов: проверить H1, лид, призыв, согласие (page_accept.py --contrast, кадр)'
    g1 = Gate('SG-A11Y-01', 'axe', 'FAIL' if what else 'PASS', ','.join(what) or '—',
              'B: имена, подписи, масштаб, контраст ключевых узлов; S: контраст прочих', sev, note)
    if unknown and sev == 'S':
        g1.no_exception = True
    return [g1, Gate('SG-A11Y-02', 'axe', 'FAIL' if s else 'PASS', ','.join(s) or '—', '0 или обосновано', 'S' if s else '-')]


def visible_text(raw):
    t = re.sub(r'(?is)<(script|style|noscript|template)\b.*?</\1>', ' ', raw)
    t = re.sub(r'(?s)<!--.*?-->', ' ', t)
    t = re.sub(r'(?s)<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', htmlmod.unescape(t))


def eval_html(raw, css=''):
    out = []
    text = visible_text(raw)
    ph = sorted({m.group(0).lower() for m in PLACEHOLDER_RX.finditer(text)})
    hash_cta = len(re.findall(r'(?is)<a\b[^>]*href=["\']#["\'][^>]*class=["\'][^"\']*(?:btn|button|cta)[^"\']*["\']', raw)) + \
        len(re.findall(r'(?is)<a\b[^>]*class=["\'][^"\']*(?:btn|button|cta)[^"\']*["\'][^>]*href=["\']#["\']', raw))
    items = ph + ([f'href="#" у призыва ×{hash_cta}'] if hash_cta else [])
    out.append(Gate('SG-CONTENT-05', 'html', 'FAIL' if items else 'PASS', '; '.join(items)[:120] or '—', 'нет заглушек', 'B' if items else '-'))
    marks = []
    if FAKE_ACTIVITY_RX.search(text):
        marks.append(('B', 'AIL-16 фальшивая активность'))
    scripts = ' '.join(re.findall(r'(?is)<script\b[^>]*>(.*?)</script>', raw))
    if COUNTDOWN_RX.search(scripts) and PROMO_RX.search(text):
        marks.append(('S', 'AIL-13 таймер или срок от «сегодня» — проверить перезагрузкой'))
    zero_counters = len(re.findall(r'(?is)<[^>]+data-(?:count|target|to|value)=["\']\d[^"\']*["\'][^>]*>\s*0\s*<', raw))
    if zero_counters:
        marks.append(('S', f'AIL-20 счётчик с 0 в HTML ×{zero_counters}'))
    div_btn = len(re.findall(r'(?is)<(?:div|span)\b[^>]*(?:onclick=|role=["\']button["\'])', raw))
    if div_btn:
        marks.append(('S', f'AIL-46 кнопки-div ×{div_btn}'))
    sev, what = worst(marks)
    out.append(Gate('SG-CONTENT-06', 'html', 'FAIL' if what else 'PASS', '; '.join(what)[:160] or '—', 'нет автоматических маркеров B', sev,
                    'маркеры S снимаются разрешением брифа (allow)'))
    out.append(eval_clamp(raw, css))
    return out


CLAMP_RX = re.compile(r'font(?:-size)?\s*:[^;{}]*?clamp\(\s*([\d.]+)(px|rem|em)\s*,[^,()]*(?:\([^()]*\)[^,()]*)*,\s*([\d.]+)(px|rem|em)\s*\)', re.I)


def eval_clamp(css_or_html, extra_css=''):
    """SG-A11Y-08 (K2, v1.1): кегли на clamp() — максимум ≤ 2,5 × минимума, иначе при зуме 200 % текст не растёт
    вдвое (WCAG 1.4.4; замечание creative 2026-09-24, п.9). Читает <style>, атрибуты style и файлы --css; var() не раскрывает."""
    text = (css_or_html or '') + '\n' + (extra_css or '')
    px = {'px': 1.0, 'rem': 16.0, 'em': 16.0}
    found, bad = 0, []
    for m in CLAMP_RX.finditer(text):
        lo, hi = float(m.group(1)) * px[m.group(2).lower()], float(m.group(3)) * px[m.group(4).lower()]
        if lo <= 0:
            continue
        found += 1
        if hi / lo > 2.5:
            bad.append(f'{m.group(1)}{m.group(2)}→{m.group(3)}{m.group(4)} (×{hi / lo:.1f})')
    if not found:
        return Gate('SG-A11Y-08', 'css', 'SKIP', 0, 'max ≤ 2,5 × min', '-', 'clamp() кеглей не найден; внешние CSS — передать --css')
    return Gate('SG-A11Y-08', 'css', 'FAIL' if bad else 'PASS', '; '.join(bad[:3]) or f'{found} clamp', 'max ≤ 2,5 × min',
                'S' if bad else '-', 'var() не раскрывается — проверить вычисленный кегль при зуме 200 %')


def apply_exceptions(results, exceptions):
    today = datetime.date.today().isoformat()
    ex = {e.get('id'): e for e in exceptions or [] if isinstance(e, dict) and e.get('id')}
    for r in results:
        e = ex.get(r.id)
        if not e or r.status != 'FAIL':
            continue
        until = str(e.get('until') or '')
        if r.severity == 'B':
            r.note = (r.note + '; ' if r.note else '') + 'исключение для B не действует'
        elif getattr(r, 'no_exception', False):
            # v1.2 (K4): S, которое снимается только проверкой (контраст без адресов узлов), а не записью в плане
            r.note = (r.note + '; ' if r.note else '') + 'исключение не действует: сначала проверить ключевые узлы'
        elif until and until < today:
            r.note = (r.note + '; ' if r.note else '') + f'исключение просрочено ({until})'
        else:
            r.excepted = True
            r.note = (r.note + '; ' if r.note else '') + f"исключение: {e.get('why', '')} ({e.get('who', '')}{', до ' + until if until else ''})"
    return results


def verdict(results):
    b = [r for r in results if r.status == 'FAIL' and r.severity == 'B']
    sv = [r for r in results if r.status == 'FAIL' and r.severity == 'S']
    return 'blocked' if b else ('accepted_with_notes' if sv else 'accepted'), len(b), len(sv)


def gate_meta(gates_yaml):
    try:
        y = load_yaml(gates_yaml)
        return {x['id']: {'site_checklist': x.get('site_checklist') or [], 'scope': x.get('scope', 'page')} for x in y['gates']}
    except Exception:  # noqa: BLE001
        return {}


def print_table(prof, results):
    print(f"профиль {prof['id']} (уровень {prof['level']})" + ('; ' + '; '.join(prof['log']) if prof['log'] else ''))
    for r in results:
        print(f"{r.status:4} {r.severity}  {r.id:13} {r.device:7}  значение {str(r.value)[:40]:>14}  порог {str(r.threshold)[:34]:>10}  {r.note}")
    v, nb, ns = verdict(results)
    print(f'вердикт: {v} (B: {nb}, S: {ns})')


# ---------------------------------------------------------------- самопроверка
def selftest(gates_path=None):
    budgets = load_yaml(os.path.join(DIR07, 'budgets.yaml'))
    gates = load_yaml(gates_path or os.path.join(DIR07, 'page-gates.yaml'))
    ok = True
    checks = []

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        checks.append(('PASS' if cond else 'FAIL', name))

    ids = [x['id'] for x in gates['gates']]
    check('page-gates.yaml: id уникальны', len(ids) == len(set(ids)))
    check('page-gates.yaml: формат SG-<CAT>-<NN>', all(GATE_ID.match(i) for i in ids))
    check('page-gates.yaml: у каждой строки владелец и порог', all(x.get('owner') and x.get('threshold') for x in gates['gates']))
    check('page-gates.yaml v1: у строк статус v1 и поле site_checklist', all(x.get('status') == 'v1' and 'site_checklist' in x for x in gates['gates']))
    if os.path.exists(CHECKLIST):
        known = {i['id'] for i in (load_yaml(CHECKLIST).get('items') or [])}
        miss = sorted({c for x in gates['gates'] for c in x.get('site_checklist') or []} - known)
        check(f'site_checklist ссылается на существующие SITE-* (нет: {miss[:4]})', not miss)
    p = resolve_profile('landing-lead-services@L1', budgets)
    check('lead-services@L1: первый экран телефона 1500 (исключение)', p['weight']['first_screen_kb']['mobile'] == 1500)
    check('lead-services@L1: TBT телефона 300 (уровень L1)', p['outcome']['tbt_ms_lab']['mobile']['goal'] == 300)
    p = resolve_profile('landing-lead-services', budgets, hot_mobile_share=0.7, price_band='mid')
    check('lead-services без уровня, горячий мобильный, mid → L0', p['level'] == 'L0')
    p = resolve_profile('landing-campaign@L2', budgets, site_level='L1')
    check('уровень страницы не выше сайта: L2 → L1', p['level'] == 'L1')
    p = resolve_profile('service-page', budgets)
    check('service-page по умолчанию L0', p['level'] == 'L0')
    try:
        resolve_profile('web-app-screen@L0', budgets)
        check('тип вне рамок отвергается', False)
    except ValueError:
        check('тип вне рамок отвергается', True)
    prof = resolve_profile('landing-lead-services@L1', budgets)
    fake = {'mobile': {'summary': {'lcp_ms': 5000, 'cls_session': 0.05, 'inp_wv_ms': 40, 'tbt_ms': 150, 'first_screen_kb': 1800,
                                   'session_kb': 2500, 'title_len': 40, 'canonical': True, 'lang': 'ru', 'h1_n': 1,
                                   'nojs_h1': True, 'nojs_cta': True, 'nojs_text_ratio': 1.1, 'tracking_before_action': 'yandex-metrika',
                                   'forms_n': 1, 'consent_separate': True, 'consent_prechecked': False, 'policy_link_in_form': True,
                                   'footer_ogrn': True, 'cmp': 'none', 'overflow_x_px': 0, 'layout_zoomed': False, 'burger': True,
                                   'header_nav_links': 0, 'cta_first_screen': 1},
                       'fin': {'lcp': [{'tag': 'H1', 'text': 'x'}]}, 'first_screen': {'t': 10, 'by_type_kb': {'script': 200}},
                       'network': {'by_type_kb': {'font': 100}, 'third_party': [{'domain': 'yandex.ru', 'kb': 120, 'cats': ['analytics'], 'first_t': 1.2}]},
                       'nav': {'html_kb': 40}}}
    res = evaluate(prof, fake, jurisdiction='ru')
    byid = {r.id: r for r in res}
    check('LCP 5 000 мс > poor 4 000 → B', byid['SG-PERF-01'].severity == 'B')
    check('первый экран 1 800 > 1 500 → S, не B', byid['SG-WEIGHT-01'].severity == 'S')
    check('трекинг до согласия в РФ → S', byid['SG-LEGAL-01'].severity == 'S')
    res_eu = evaluate(prof, fake, jurisdiction='eu')
    check('трекинг до согласия в ЕС → B', {r.id: r for r in res_eu}['SG-LEGAL-01'].severity == 'B')
    check('вердикт blocked при B', verdict(res)[0] == 'blocked')
    f2 = copy.deepcopy(fake)
    f2['mobile']['summary'].update({'lcp_ms': 1200, 'first_screen_kb': 900, 'tracking_before_action': None})
    check('чистая страница → accepted', verdict(evaluate(prof, f2))[0] == 'accepted')
    # v1: строки H2
    f3 = copy.deepcopy(f2)
    f3['mobile']['summary'].update({'lang': None})
    r3 = {r.id: r for r in evaluate(prof, f3)}
    check('SG-SEO-02: нет lang → D (строка H2)', r3['SG-SEO-02'].severity == 'D')
    f3['mobile']['summary'].update({'lang': 'ru', 'h1_n': 2})
    check('SG-SEO-03: H1 > 1 → D', {r.id: r for r in evaluate(prof, f3)}['SG-SEO-03'].severity == 'D')
    f3['mobile']['summary'].update({'h1_n': 0})
    check('SG-SEO-03: нет H1 → S', {r.id: r for r in evaluate(prof, f3)}['SG-SEO-03'].severity == 'S')
    f3['mobile']['summary'].update({'h1_n': 1, 'nojs_cta': False})
    check('SG-GEO-01: CTA только после JS → S (не B)', {r.id: r for r in evaluate(prof, f3)}['SG-GEO-01'].severity == 'S')
    f3['mobile']['summary'].update({'nojs_cta': True, 'nojs_text_ratio': 0.7})
    check('SG-GEO-01: доля 0,7 → D', {r.id: r for r in evaluate(prof, f3)}['SG-GEO-01'].severity == 'D')
    f3['mobile']['summary'].update({'nojs_text_ratio': 0.4})
    check('SG-GEO-01: доля 0,4 → S', {r.id: r for r in evaluate(prof, f3)}['SG-GEO-01'].severity == 'S')
    f3['mobile']['summary'].update({'nojs_text_ratio': 1.0, 'nojs_h1': False})
    check('SG-GEO-01: H1 только после JS → B', {r.id: r for r in evaluate(prof, f3)}['SG-GEO-01'].severity == 'B')
    # v1: geo флаги и условия брифа
    hk = load_headkit(os.path.join(DIR07, 'head-kit.yaml'))
    gr = {r.id: r for r in eval_geo({'flags': ['noindex', 'blocked-openai-oai-searchbot', 'no-lang']}, hk, plan_info({}))}
    check('geo: noindex на индексируемой → B', gr['SG-SEO-02'].severity == 'B')
    check('geo: закрыт OAI-SearchBot → S', gr['SG-GEO-02'].severity == 'S')
    gr = {r.id: r for r in eval_geo({'flags': ['noindex', 'blocked-openai-oai-searchbot']}, hk,
                                    plan_info({'page': {'seo': {'indexable': False}}}), ai_bots_policy='deny-all')}
    check('geo: noindex по плану и deny-all → PASS', gr['SG-SEO-02'].status == 'PASS' and gr['SG-GEO-02'].status == 'PASS')
    gr = {r.id: r for r in eval_geo({'flags': ['csr-shell', 'ua-googlebot-text-differs']}, hk, plan_info({}))}
    check('geo: csr-shell → B; ua-*-text-differs → S в GEO-02', gr['SG-GEO-01'].severity == 'B' and gr['SG-GEO-02'].severity == 'S')
    # v1: ia, axe, html
    ir = {r.id: r for r in eval_ia({'summary': {'not_found': 'soft 404 (200)', 'lang_switch': True, 'hreflang_pages': 0,
                                                'home_header_items': []}, 'sitemap': {'urls': 0}, 'robots': {'sitemaps': []}})}
    check('ia: мягкая 404 → B', ir['SG-SEO-01'].severity == 'B')
    check('ia: sitemap пуст → S; hreflang нет → S; меню не в HTML → S',
          ir['SG-SEO-06'].severity == 'S' and ir['SG-SEO-08'].severity == 'S' and ir['SG-NAV-01'].severity == 'S')
    ar = {r.id: r for r in eval_axe({'axe': {'violations': [{'id': 'link-name'}, {'id': 'target-size'}]}})}
    check('axe: link-name → B, target-size → S', ar['SG-A11Y-01'].severity == 'B' and ar['SG-A11Y-02'].severity == 'S')
    hr = {r.id: r for r in eval_html('<html><body><h1>Окна</h1><p>Lorem ipsum dolor</p><div class="toast">Мария только что купила</div>'
                                     '<a class="btn" href="#">Заказать</a><span data-count="1200">0</span></body></html>')}
    check('html: заглушки → B', hr['SG-CONTENT-05'].severity == 'B')
    check('html: фальшивая активность → B', hr['SG-CONTENT-06'].severity == 'B')
    hr = {r.id: r for r in eval_html('<html><body><h1>Окна</h1><p>Честный текст</p></body></html>')}
    check('html: чистая страница → PASS', hr['SG-CONTENT-05'].status == 'PASS' and hr['SG-CONTENT-06'].status == 'PASS')
    # v1: исключения, телефон, первый экран
    f4 = copy.deepcopy(f2)
    f4['mobile']['summary'].update({'first_screen_kb': 1800, 'overflow_x_px': 30, 'layout_zoomed': True})
    plan = {'page': {'x-gate-exception': [{'id': 'SG-WEIGHT-01', 'why': 'видео кампании', 'who': 'заказчик', 'until': '2099-01-01'},
                                          {'id': 'SG-MOB-01', 'why': 'x', 'who': 'y'}]}}
    r4 = {r.id: r for r in evaluate(prof, f4, plan=plan)}
    check('исключение снимает S с пометкой', getattr(r4['SG-WEIGHT-01'], 'excepted', False))
    check('исключение для B не действует (MOB-01)', r4['SG-MOB-01'].severity == 'B' and not getattr(r4['SG-MOB-01'], 'excepted', False))
    f5 = copy.deepcopy(f2)
    f5['desktop'] = copy.deepcopy(f2['mobile'])
    f5['mobile']['summary']['cta_first_screen'] = 0
    f5['desktop']['summary']['cta_first_screen'] = 0
    check('offer-cta и 0 призывов на обоих устройствах → B', {r.id: r for r in evaluate(prof, f5)}['SG-CONTENT-07'].severity == 'B')
    check('poster → PASS первого экрана', {r.id: r for r in evaluate(prof, f5, plan={'page': {'first_screen_policy': 'poster'}})}['SG-CONTENT-07'].status == 'PASS')
    # v1.1 (K2): видео первого экрана отдельно; clamp кеглей (замечания creative 2026-09-24)
    f6 = copy.deepcopy(f2)
    f6['mobile']['first_screen']['by_type_kb']['media'] = 2000
    check('видео первого экрана 2 000 > бюджета 1 500 → S (SG-WEIGHT-09)', {r.id: r for r in evaluate(prof, f6)}['SG-WEIGHT-09'].severity == 'S')
    f6['mobile']['first_screen']['by_type_kb']['media'] = 300
    check('видео первого экрана 300 КБ → D отдельной цифрой', {r.id: r for r in evaluate(prof, f6)}['SG-WEIGHT-09'].severity == 'D')
    check('clamp 40px→160px (×4) → S (SG-A11Y-08)', eval_clamp('<style>h1{font-size:clamp(40px, 8vw, 160px)}</style>').severity == 'S')
    check('clamp 2rem→4rem (×2) → PASS', eval_clamp('<p style="font-size: clamp(2rem, 1rem + 3vw, 4rem)">x</p>').status == 'PASS')
    check('clamp не найден → SKIP', eval_clamp('<p>x</p>').status == 'SKIP')
    # v1.2 (K3): калибровка опыта K/03 — ложные B из прогона на 8 страницах
    f7 = copy.deepcopy(f2)
    f7['mobile']['summary'].update({'cls_session': 0.42})
    f7['mobile']['fin']['wv_cls'] = 0.15
    check('CLS: берётся окно web-vitals 0,15 (S), а не сумма 0,42 (B)', {r.id: r for r in evaluate(prof, f7)}['SG-PERF-03'].severity == 'S')
    f7['mobile']['summary'].update({'nojs_h1': False, 'h1_n': 1})
    f7['mobile']['nojs'] = {'h1_raw_n': 1, 'h1_raw': ['крупнейшая техническая конференция']}
    f7['mobile']['dom'] = {'headings': {'h1': ['КРУПНЕЙШАЯ ТЕХНИЧЕСКАЯКОНФЕРЕНЦИЯ']}}
    check('H1 в сыром HTML, слова склеены на <br> → не B', {r.id: r for r in evaluate(prof, f7)}['SG-GEO-01'].severity != 'B')
    f7['mobile']['nojs'] = {'h1_raw_n': 0, 'h1_raw': []}
    check('H1 нет в сыром HTML → B', {r.id: r for r in evaluate(prof, f7)}['SG-GEO-01'].severity == 'B')
    f8 = copy.deepcopy(f2)
    f8['mobile']['summary'].update({'overflow_x_px': 1307, 'layout_zoomed': False})
    check('переполнение скрыто overflow-x (область не расширена) → D', {r.id: r for r in evaluate(prof, f8)}['SG-MOB-01'].severity == 'D')
    f8['mobile']['summary'].update({'overflow_x_px': 45, 'layout_zoomed': True})
    check('область телефона расширена → B', {r.id: r for r in evaluate(prof, f8)}['SG-MOB-01'].severity == 'B')
    f9 = copy.deepcopy(f2)
    f9['mobile']['summary'].update({'tracking_before_action': 'gtm;amplitude', 'forms_n': 1, 'policy_link_in_form': False})
    f9['mobile']['network']['tracking_requests'] = [{'u': 'https://www.googletagmanager.com/gtm.js', 'vendor': 'gtm', 'phase': 'load'},
                                                    {'u': 'https://cdn.amplitude.com/libs/analytics-browser-2.25.1-min.js.gz', 'vendor': 'amplitude', 'phase': 'load'}]
    r9 = {r.id: r for r in evaluate(prof, f9, jurisdiction='eu')}
    check('ЕС: до выбора только библиотеки → S; нет ссылки на уведомление → S', r9['SG-LEGAL-01'].severity == 'S' and r9['SG-LEGAL-04'].severity == 'S')
    f9['mobile']['network']['tracking_requests'].append({'u': 'https://region1.google-analytics.com/g/collect', 'vendor': 'ga4', 'phase': 'load'})
    check('ЕС: событие GA4 до выбора → B', {r.id: r for r in evaluate(prof, f9, jurisdiction='eu')}['SG-LEGAL-01'].severity == 'B')
    check('РФ: нет ссылки на политику в форме → B', {r.id: r for r in evaluate(prof, f9, jurisdiction='ru')}['SG-LEGAL-04'].severity == 'B')
    # v1.2 (K4): контраст по классам узлов (профиль I 08/03 §8; опыт K/03 axe_classes.tsv) и H1 в LCP (creative E/01)
    def node(**k):
        base = {'in_h1': False, 'action': False, 'in_form': False, 'cookie': False, 'first_screen': False,
                'in_header': False, 'in_footer': False, 'text': 'x'}
        base.update(k)
        return base
    ax = {'axe': {'violations': [{'id': 'color-contrast', 'nodes_n': 2, 'nodes': [node(in_footer=True), node(action=True, text='Меню')]}]}}
    check('контраст только прочих узлов (подвал, меню) → S, не B', eval_axe(ax, {'заказать'})[0].severity == 'S')
    ax['axe']['violations'][0]['nodes'].append(node(action=True, text='ЗАКАЗАТЬ', first_screen=True))
    check('контраст призыва → B', eval_axe(ax, {'заказать'})[0].severity == 'B')
    check('контраст строки согласия (в форме) → B', eval_axe({'violations': [{'id': 'color-contrast', 'nodes': [node(in_form=True)]}]})[0].severity == 'B')
    check('текст о cookie в подвале ниже первого экрана → S; баннер cookie в первом экране → B',
          eval_axe({'violations': [{'id': 'color-contrast', 'nodes': [node(cookie=True, in_footer=True)]}]})[0].severity == 'S'
          and eval_axe({'violations': [{'id': 'color-contrast', 'nodes': [node(cookie=True, in_footer=True, first_screen=True)]}]})[0].severity == 'B')
    r10 = eval_axe({'axe': {'violations': [{'id': 'color-contrast', 'nodes': 12}]}})[0]
    check('контраст без адресов узлов (счётчик I/02) → S', r10.severity == 'S')
    r10 = apply_exceptions([r10], [{'id': 'SG-A11Y-01', 'why': 'x', 'who': 'y'}])[0]
    check('контраст без адресов: исключение S не снимает', not getattr(r10, 'excepted', False))
    check('контраст прочих + link-name → B', eval_axe({'violations': [{'id': 'color-contrast', 'nodes': [node()]}, {'id': 'link-name'}]})[0].severity == 'B')
    f11 = copy.deepcopy(f2)
    f11['mobile']['dom'] = {'headings': {'h1_first_screen': True, 'h1': ['A Good Clean, Naturally']}}
    f11['mobile']['fin'] = {'lcp': [{'tag': 'P', 'text': 'Sparkling clean homes are our specialty', 'size': 52966, 'url': ''}]}
    hid = '<section><div class="transition-all opacity-0 translate-y-8"><h1 class="x">A Good Clean, Naturally</h1></div></section>'
    check('H1 не кандидат LCP + обёртка opacity-0 → S', {r.id: r for r in evaluate(prof, f11, html_text=hid)}['SG-PERF-06'].severity == 'S')
    check('H1 не кандидат LCP, признаков в HTML нет → D', {r.id: r for r in evaluate(prof, f11, html_text='<h1>A Good Clean, Naturally</h1>')}['SG-PERF-06'].severity == 'D')
    f11['mobile']['fin'] = {'lcp': [{'tag': 'H1', 'text': 'A Good Clean, Naturally', 'size': 90000, 'url': ''}]}
    fr = '<div data-framer-appear-id="x" style="opacity:0.001;transform:translateY(48px)"><h1>A Good Clean, Naturally</h1></div>'
    check('H1 — LCP, но проявляется из opacity 0.001 (Framer appear) → D', {r.id: r for r in evaluate(prof, f11, html_text=fr)}['SG-PERF-06'].severity == 'D')
    check('H1 — LCP без признаков → PASS', {r.id: r for r in evaluate(prof, f11, html_text='<h1>A Good Clean</h1>')}['SG-PERF-06'].status == 'PASS')
    check('анимация из @keyframes opacity .35 — не признак (Lovable)',
          not h1_reveal_evidence('<style>@keyframes r{0%{opacity:.35}} .rv{animation:.7s both r}</style><div class="rv"><h1>x</h1></div>')['hidden'])
    check('анимация из @keyframes opacity 0 и html.js .h1{opacity:0} — признак',
          bool(h1_reveal_evidence('<style>@keyframes r{from{opacity:0}} .rv{animation:.7s both r}</style><div class="rv"><h1>x</h1></div>')['hidden'])
          and bool(h1_reveal_evidence('<h1 class="h1">x</h1>', 'html.js .h1{opacity:0}')['hidden']))
    for st, name in checks:
        print(st, name)
    print(f"итог: {sum(c[0] == 'PASS' for c in checks)}/{len(checks)} PASS")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--profile')
    ap.add_argument('--resolve')
    ap.add_argument('--anatomy')
    ap.add_argument('--accept')
    ap.add_argument('--geo', help='JSON geo_probe.py (файл или папка с одним JSON)')
    ap.add_argument('--ia', help='ia.json ia_probe.py (строки scope: site)')
    ap.add_argument('--axe', help='JSON axe (run_axe.py опыта I/02 или результат axe.run)')
    ap.add_argument('--plan', help='page-plan.yaml (first_screen_policy, seo.indexable, x-gate-exception)')
    ap.add_argument('--html', help='сохранённый HTML страницы (заглушки и автоматические маркеры)')
    ap.add_argument('--css', nargs='*', help='файлы CSS страницы для SG-A11Y-08 (clamp кеглей), если стили внешние')
    ap.add_argument('--jurisdiction', default='ru', choices=['ru', 'eu', 'none'])
    ap.add_argument('--ai-bots-policy', default='allow-all', choices=['allow-all', 'allow-search-deny-training', 'deny-all'])
    ap.add_argument('--ads-google', action='store_true', help='посадочная под Google Ads: закрытый AdsBot — B')
    ap.add_argument('--site-level', choices=LEVELS)
    ap.add_argument('--hot-mobile-share', type=float)
    ap.add_argument('--price-band', choices=['low', 'mid', 'high', 'premium'])
    ap.add_argument('--gates', help='другой page-gates.yaml (самопроверка черновика)')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest(a.gates)
    budgets = load_yaml(os.path.join(DIR07, 'budgets.yaml'))
    if a.resolve:
        p = resolve_profile(a.resolve, budgets, a.site_level, a.hot_mobile_share, a.price_band)
        print(json.dumps(p, ensure_ascii=False, indent=1))
        return 0
    if not a.profile or not (a.anatomy or a.geo or a.ia or a.axe or a.html or a.css):
        ap.print_help()
        return 2
    prof = resolve_profile(a.profile, budgets, a.site_level, a.hot_mobile_share, a.price_band)
    plan = load_yaml(a.plan) if a.plan else None
    raw = open(a.html, encoding='utf-8', errors='replace').read() if a.html else None
    css = '\n'.join(open(f, encoding='utf-8', errors='replace').read() for f in (a.css or []))
    res = evaluate(prof, load_anatomy(a.anatomy) if a.anatomy else {}, load_accept(a.accept) if a.accept else {}, a.jurisdiction,
                   geo=load_json(a.geo), ia=load_json(a.ia), axe=load_json(a.axe), plan=plan, html_text=raw,
                   headkit=load_headkit(os.path.join(DIR07, 'head-kit.yaml')), ai_bots_policy=a.ai_bots_policy,
                   ads_google=a.ads_google, css_text=css or None)
    meta = gate_meta(a.gates or os.path.join(DIR07, 'page-gates.yaml'))
    if a.json:
        v, nb, ns = verdict(res)
        rows = []
        for r in res:
            d = dict(r.__dict__)
            d.update(meta.get(r.id, {}))
            rows.append(d)
        print(json.dumps({'profile': prof['id'], 'level': prof['level'], 'log': prof['log'], 'verdict': v, 'B': nb, 'S': ns,
                          'gates': rows}, ensure_ascii=False, indent=1, default=str))
    else:
        print_table(prof, res)
    return 1 if verdict(res)[0] == 'blocked' else 0


if __name__ == '__main__':
    sys.exit(main())
