#!/usr/bin/env python3
"""geo_probe.py — доступность страницы для поисковых и ИИ-ботов (site-research, агент H, волна 2, 2026-09-24).

Что меряет (по умолчанию — только HTTP, без браузера):
  1. robots.txt: код ответа, размер, BOM, группы, Sitemap, Crawl-delay, Clean-param/Host (Яндекс), Content-Signal
     (Cloudflare), Content-Usage (IETF draft-ietf-aipref-attach), блок «Cloudflare Managed»; для каждого бота из
     crawlers.yaml — разрешён ли URL страницы (RFC 9309 + особенности платформ: цепочки групп из crawlers.yaml —
     Яндекс «YandexBot → Yandex → *», Apple «Applebot → Googlebot → *», AdsBot-Google и YandexAdditional без группы *).
  2. /llms.txt и /llms-full.txt: код, тип, размер; Markdown по llmstxt.org (H1, ссылки) или HTML-заглушка (soft 404).
  3. Страница: код, цепочка редиректов, X-Robots-Tag, CDN и антибот-заглушка, размер несжатого HTML (Googlebot читает
     первые 2 МБ), смещения </head>, первого h1, последнего og:* (facebookexternalhit — OG в первых 1 МБ).
  4. head: title, meta description, robots/googlebot/yandex/bingbot/applebot, canonical, hreflang, lang, OG, Twitter.
  5. Текст без JS (определения как у M, page_anatomy.py nojs_compare): слова вне script/style/noscript/template/svg/
     iframe/object/head/canvas; h1; цены; признаки SPA-оболочки и платформы.
  6. JSON-LD: разбор JSON, @type (с @graph), базовые обязательные свойства (таблица REQ ниже), sameAs, @id; микроразметка.
  7. --render: Chromium без взаимодействия (берёт обе блокировки браузера сам, ждёт MemAvailable ≥ 3 ГБ): слова
     отрисованной страницы, доля текста без JS, h1 и главный призыв в сыром HTML, цены, JSON-LD только из JS.
  8. --ua-probe: запросы с UA ботов (Googlebot, YandexBot, OAI-SearchBot, PerplexityBot, ClaudeBot, GPTBot) — код и
     объём против браузерного UA. Только сигнал: WAF законно режет поддельный UA с чужого IP.

Запуск:
  python3 99-raw/tools/geo_probe.py URL [--out DIR] [--id ID] [--render] [--ua-probe] [--crawlers PATH]
  python3 99-raw/tools/geo_probe.py --batch pages.tsv --out DIR [--render] [--ua-probe] [--only a,b] [--skip-done]
      pages.tsv: колонки id и url (заголовок обязателен; остальные колонки — в поле meta), строки с # пропускаются
      --insecure-retry — при ошибке TLS-цепочки (например, сертификат НУЦ Минцифры «Russian Trusted Sub CA») прочитать
      страницу без проверки и пометить tls_untrusted (только чтение; данные никуда не отправляются)
  python3 99-raw/tools/geo_probe.py --summary DIR > summary.tsv
  python3 99-raw/tools/geo_probe.py --revalidate DIR      # пересчитать проверки JSON-LD и robots по сохранённым данным
  python3 99-raw/tools/geo_probe.py --selftest

Правила: ≤ 1 запроса в секунду на хост; формы не отправляет, ничего не вводит, по рекламе не ходит; браузер — только
с --render и только под блокировками $DDD_HOME/locks/browser.lock и $DDD_HOME/locks/site/browser.lock.
Зависимости: Python 3.13, requests, PyYAML; для --render — Playwright + Chromium.
"""
import json, os, re, sys, time, csv, fcntl, socket, hashlib
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit, urljoin, quote, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('site'))
CRAWLERS = os.path.join(ROOT, '07-seo-geo-performance-analytics', 'crawlers.yaml')
LOCKS = [kbpaths.lock_path('browser'), kbpaths.lock_path('browser', 'site')]
VERSION = '0.9 (2026-09-24)'

UA_BROWSER = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/140.0.0.0 Safari/537.36')
# Строки UA ботов — из документации владельцев (crawlers.yaml, проверено 2026-09-24). Для --ua-probe.
UA_BOTS = {
    'Googlebot': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/140.0.0.0 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'YandexBot': 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    'OAI-SearchBot': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/131.0.0.0 Safari/537.36; compatible; OAI-SearchBot/1.4; +https://openai.com/searchbot',
    'GPTBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; GPTBot/1.4; +https://openai.com/gptbot',
    'PerplexityBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; '
                     '+https://perplexity.ai/perplexitybot)',
    'ClaudeBot': 'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)',
}
HDRS = {'User-Agent': UA_BROWSER, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8', 'Accept-Encoding': 'gzip, deflate, br'}

GOOGLEBOT_HTML_LIMIT = 2 * 1024 * 1024      # Googlebot: первые 2 МБ несжатого файла (страница Googlebot, 2026-02-03)
FB_OG_LIMIT = 1024 * 1024                   # facebookexternalhit: OG в первых 1 МБ (Meta, 2026-05-21)
ROBOTS_LIMIT = 500 * 1024                   # Google: 500 KiB (robots.txt spec, 2026-08-31)

SKIP = {'script', 'style', 'noscript', 'template', 'svg', 'iframe', 'object', 'head', 'canvas'}   # = M nojs_compare
WORD_RE = re.compile(r'[^\W_]+', re.U)
PRICE_RE = re.compile(r'\d[\d\s .,]{0,12}\s?(?:₽|руб\.?|р\.)|[$€£]\s?\d[\d.,]*', re.I)   # = M
CTA_RE = re.compile(r'(заказ|оставить заявк|отправить заявк|получить|записат|рассчитат|узнать цен|консультац|позвонит|'
                    r'купить|оформить|подключит|попробовать|начать|скачать|зарегистр|вызвать|забронир|'
                    r'get started|start|try|sign up|book|request|contact sales|talk to|buy|order|download|get a quote|'
                    r'schedule|demo|join|subscribe|apply)', re.I)

SPA_MARKERS = {
    'next': r'id="__next"|__NEXT_DATA__', 'nuxt': r'window\.__NUXT__|id="__nuxt"', 'react-root': r'<div id="root">\s*</div>',
    'vue-app': r'<div id="app">\s*</div>', 'gatsby': r'id="___gatsby"', 'angular': r'ng-version=', 'astro': r'<astro-island',
    'svelte': r'__sveltekit|data-sveltekit', 'remix': r'__remixContext', 'qwik': r'q:container',
}
PLATFORM_MARKERS = {
    'tilda': r'data-tilda-|tildacdn|t-records', 'webflow': r'data-wf-page|webflow\.js', 'wix': r'wixstatic|_wixCssImports|wix-',
    'framer': r'framerusercontent|data-framer-', 'wordpress': r'wp-content|wp-includes', 'bitrix': r'bitrix/(?:js|templates)',
    'squarespace': r'squarespace\.com|static1\.squarespace', 'hubspot': r'hs-scripts|hubspotusercontent', 'shopify': r'cdn\.shopify',
    'readymag': r'readymag', 'lpmotor': r'lpmotor', 'nethouse': r'nethouse', 'ukit': r'ukit\.',
}
CHALLENGE_RE = re.compile(r'cf-chl|challenge-platform|Just a moment\.\.\.|ddos-guard|__qrator|qrator|Проверка браузера|'
                          r'Checking your browser|captcha-delivery|px-captcha|smartcaptcha|js-challenge|servicepipe|variti|'
                          r'<noscript>\s*<meta[^>]+http-equiv=["\']?refresh', re.I)

# Базовые обязательные свойства JSON-LD. Источник — документация Google «Search gallery» по типам и schema.org;
# уточняется в head-kit.yaml (раздел jsonld). any: хотя бы одно из списка. Пустой required — у Google нет обязательных.
REQ = {
    'Organization': {'required': [], 'recommended': ['name', 'url', 'logo', 'sameAs']},
    'LocalBusiness': {'required': ['name', 'address'], 'recommended': ['telephone', 'url', 'openingHoursSpecification', 'geo', 'priceRange']},
    'Product': {'required': ['name'], 'any': [['offers', 'review', 'aggregateRating']], 'recommended': ['image', 'description', 'brand']},
    'Offer': {'required': [], 'any': [['price', 'priceSpecification']], 'recommended': ['priceCurrency', 'availability', 'url']},
    'FAQPage': {'required': ['mainEntity'], 'recommended': []},
    'Question': {'required': ['name', 'acceptedAnswer'], 'recommended': []},
    'BreadcrumbList': {'required': ['itemListElement'], 'recommended': []},
    'ListItem': {'required': ['position'], 'recommended': ['name', 'item']},
    'Event': {'required': ['name', 'startDate', 'location'], 'recommended': ['endDate', 'eventStatus', 'image', 'offers', 'organizer']},
    'Course': {'required': ['name', 'description'], 'recommended': ['provider']},
    'Article': {'required': [], 'recommended': ['headline', 'image', 'datePublished', 'dateModified', 'author']},
    'SoftwareApplication': {'required': ['name', 'offers'], 'any': [['aggregateRating', 'review']], 'recommended': ['applicationCategory', 'operatingSystem']},
    'VideoObject': {'required': ['name', 'thumbnailUrl', 'uploadDate'], 'recommended': ['description', 'contentUrl', 'duration']},
    'WebSite': {'required': [], 'recommended': ['name', 'url', 'alternateName']},
    'Review': {'required': ['itemReviewed', 'reviewRating', 'author'], 'recommended': []},
    'AggregateRating': {'required': ['ratingValue'], 'any': [['ratingCount', 'reviewCount']], 'recommended': ['itemReviewed']},
    'Service': {'required': [], 'recommended': ['name', 'provider', 'areaServed', 'serviceType']},
}
SUBTYPES = {  # подтипы → базовый тип для проверки
    'LocalBusiness': ['ProfessionalService', 'HomeAndConstructionBusiness', 'MedicalBusiness', 'Dentist', 'LegalService',
                      'AccountingService', 'FinancialService', 'AutomotiveBusiness', 'HealthAndBeautyBusiness', 'Store',
                      'FoodEstablishment', 'Restaurant', 'EducationalOrganization', 'RealEstateAgent', 'TravelAgency',
                      'MovingCompany', 'Plumber', 'RoofingContractor', 'Electrician', 'GeneralContractor', 'HVACBusiness',
                      'HousePainter', 'Locksmith', 'EmploymentAgency', 'InsuranceAgency', 'Attorney', 'Notary', 'LodgingBusiness',
                      'SportsActivityLocation', 'ChildCare', 'DryCleaningOrLaundry', 'EntertainmentBusiness'],
    'Article': ['NewsArticle', 'BlogPosting', 'TechArticle', 'Report'],
    'Organization': ['Corporation', 'NGO', 'EducationalOrganization', 'OnlineBusiness', 'OnlineStore'],
    'SoftwareApplication': ['WebApplication', 'MobileApplication'],
    'Event': ['BusinessEvent', 'EducationEvent', 'Festival', 'MusicEvent', 'SocialEvent', 'ExhibitionEvent', 'SaleEvent'],
}


def base_type(t):
    if t in REQ:
        return t
    for b, subs in SUBTYPES.items():
        if t in subs:
            return b
    return None


# ------------------------------------------------------------------------------------------------ HTTP
_last_hit = {}


def polite(host, gap=1.0):
    t = _last_hit.get(host)
    if t:
        d = time.time() - t
        if d < gap:
            time.sleep(gap - d)
    _last_hit[host] = time.time()


INSECURE_RETRY = False     # --insecure-retry: при ошибке проверки TLS повторить без проверки (только чтение), пометить tls_untrusted


def http_get(url, ua=None, max_redirects=10, timeout=30, retries=1):
    """GET с вежливой паузой. Сетевые сбои — один повтор через 5 с. Ошибка TLS-цепочки фиксируется в tls_error;
    с --insecure-retry страница всё же читается (verify=False), а результат помечается tls_untrusted=True."""
    import requests, urllib3
    s = requests.Session()
    s.max_redirects = max_redirects
    h = dict(HDRS)
    if ua:
        h['User-Agent'] = ua
    t0 = time.time()
    tls_error = None
    for attempt in range(retries + 1):
        polite(urlsplit(url).hostname or '')
        try:
            r = s.get(url, headers=h, timeout=timeout, allow_redirects=True)
            break
        except requests.exceptions.SSLError as ex:
            tls_error = str(ex)[:200]
            if INSECURE_RETRY:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                try:
                    r = s.get(url, headers=h, timeout=timeout, allow_redirects=True, verify=False)
                    break
                except Exception as ex2:
                    return {'error': type(ex2).__name__ + ': ' + str(ex2)[:160], 'url': url, 'tls_error': tls_error,
                            't': round(time.time() - t0, 2)}
            return {'error': 'SSLError: ' + tls_error[:160], 'url': url, 'tls_error': tls_error, 't': round(time.time() - t0, 2)}
        except Exception as ex:
            if attempt < retries:
                time.sleep(5)
                continue
            return {'error': type(ex).__name__ + ': ' + str(ex)[:160], 'url': url, 't': round(time.time() - t0, 2)}
    chain = [{'status': x.status_code, 'url': x.url, 'location': x.headers.get('location')} for x in r.history]
    body = r.content or b''
    return {'url': url, 'final_url': r.url, 'status': r.status_code, 'chain': chain, 'headers': {k.lower(): v for k, v in r.headers.items()},
            'body': body, 'bytes': len(body), 't': round(time.time() - t0, 2), 'tls_untrusted': bool(tls_error), 'tls_error': tls_error}


def decode_html(body, headers):
    ct = (headers or {}).get('content-type', '')
    m = re.search(r'charset=([\w-]+)', ct, re.I)
    enc = m.group(1) if m else None
    if not enc:
        m = re.search(rb'<meta[^>]+charset=["\']?([\w-]+)', body[:4096], re.I)
        enc = m.group(1).decode('ascii', 'ignore') if m else 'utf-8'
    try:
        return body.decode(enc, errors='replace')
    except LookupError:
        return body.decode('utf-8', errors='replace')


# ------------------------------------------------------------------------------------------------ robots.txt (RFC 9309)
def parse_robots(text):
    """Группы RFC 9309: список {'agents': [...], 'rules': [(allow:bool, path)], 'crawl_delay': ...}; прочие записи."""
    text = text.lstrip('﻿')
    groups, cur, in_rules = [], None, False
    other = {'sitemap': [], 'content-signal': [], 'content-usage': [], 'clean-param': [], 'host': [], 'unknown': []}
    for raw in text.splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or ':' not in line:
            continue
        k, v = line.split(':', 1)
        k, v = k.strip().lower(), v.strip()
        if k in ('user-agent', 'useragent', 'user agent'):
            if cur is None or in_rules:
                cur = {'agents': [], 'rules': [], 'crawl_delay': None, 'content_signal': [], 'content_usage': []}
                groups.append(cur); in_rules = False
            cur['agents'].append(v)
        elif k in ('allow', 'disallow'):
            if cur is None:
                continue                      # правило вне группы — игнор (RFC 9309 §2.2.2)
            in_rules = True
            if v == '':
                continue                      # пустой путь — правило игнорируется (Google)
            cur['rules'].append((k == 'allow', v))
        elif k == 'crawl-delay':
            if cur is not None:
                cur['crawl_delay'] = v
        elif k in ('content-signal', 'content-usage'):
            other[k].append(v)
            if cur is not None:
                cur['content_signal' if k == 'content-signal' else 'content_usage'].append(v)
        elif k in ('sitemap', 'clean-param', 'host'):
            other[k].append(v)
        else:
            other['unknown'].append(k)
    return groups, other


def _norm_token(v):
    v = v.strip()
    m = re.match(r'[A-Za-z_*\-]+', v)            # «googlebot/1.2» и «googlebot*» ≡ «googlebot» (Google spec)
    t = (m.group(0) if m else v).lower()
    if t != '*' and t.endswith('*'):
        t = t.rstrip('*')
    return t


def _pct(p):
    # процент-кодирование не-ASCII и нормализация уже закодированных непривилегированных символов (RFC 9309 §2.2.2)
    try:
        p = quote(unquote(p), safe="/?=&%:@!$&'()*+,;~-._")
    except Exception:
        pass
    return p


def _rule_regex(path):
    anchored = path.endswith('$')
    core = path[:-1] if anchored else path
    rx = ''.join('.*' if ch == '*' else re.escape(ch) for ch in _pct(core))
    return re.compile('^' + rx + ('$' if anchored else ''))


def robots_decision(groups, chain, path):
    """chain — токены в порядке приоритета (свой → запасные → '*'). Возвращает (allowed, matched_group_token, rule)."""
    if path == '/robots.txt':
        return True, None, None
    target = _pct(path)
    for tok in chain:
        t = tok.lower()
        rules = []
        for g in groups:
            if any(_norm_token(a) == t for a in g['agents']):
                rules.extend(g['rules'])
        if not any(_norm_token(a) == t for g in groups for a in g['agents']):
            continue                          # группы для этого токена нет — к следующему в цепочке
        best = None                           # (длина шаблона, allow, шаблон)
        for allow, pat in rules:
            if _rule_regex(pat).match(target):
                key = (len(pat), allow)       # самое длинное совпадение; при равенстве — allow
                if best is None or key > (best[0], best[1]):
                    best = (len(pat), allow, pat)
        if best is None:
            return True, tok, None
        return best[1], tok, ('allow: ' if best[1] else 'disallow: ') + best[2]
    return True, None, None                   # ни одной подходящей группы — ограничений нет


def load_crawlers(path=CRAWLERS):
    import yaml
    d = yaml.safe_load(open(path, encoding='utf-8'))
    bots = []
    for b in d['bots']:
        tok = b['user_agent_token']
        chain = [tok] + [x for x in (b.get('robots_fallback') or []) if not x.startswith('(')]
        if b.get('star_group_applies', True):
            chain.append('*')
        bots.append({'id': b['id'], 'token': tok, 'purpose': b['purpose'], 'kind': b.get('kind'),
                     'respects': str(b.get('respects_robots')), 'chain': chain, 'priority': b.get('priority'),
                     'feeds': b.get('feeds') or []})
    return bots, d


def robots_report(rb, page_path, bots):
    if 'error' in rb:
        return {'status': None, 'error': rb['error'], 'effective': 'unreachable-assume-disallow'}
    st = rb['status']
    rep = {'status': st, 'final_url': rb.get('final_url'), 'bytes': rb.get('bytes'), 'redirects': len(rb.get('chain') or []),
           'content_type': (rb.get('headers') or {}).get('content-type')}
    if 500 <= st <= 599:
        rep['effective'] = 'unreachable-assume-disallow'      # RFC 9309 §2.3.1.4; Google — стоп 12 ч
        return rep
    if 400 <= st <= 499 and st != 429:
        rep['effective'] = 'unavailable-allow-all'            # RFC 9309 §2.3.1.3; Google — «as if … didn't exist»
        rep['bots'] = {b['id']: {'allowed': True, 'by': None} for b in bots}
        return rep
    if st == 429:
        rep['effective'] = 'rate-limited'
        return rep
    text = decode_html(rb['body'], rb.get('headers'))
    looks_html = bool(re.search(r'<(?:!doctype|html|head|body)\b', text[:2000], re.I))
    groups, other = parse_robots(text[:ROBOTS_LIMIT])
    rep.update({'effective': 'parsed', 'looks_html': looks_html, 'bom': rb['body'][:3] == b'\xef\xbb\xbf',
                'over_500kib': (rb.get('bytes') or 0) > ROBOTS_LIMIT, 'groups': len(groups),
                'agents': sorted({a for g in groups for a in g['agents']}, key=str.lower)[:80],
                'sitemaps': other['sitemap'][:10], 'content_signal': other['content-signal'][:5],
                'content_usage': other['content-usage'][:5], 'clean_param_n': len(other['clean-param']),
                'host': other['host'][:2], 'crawl_delay': [g['crawl_delay'] for g in groups if g['crawl_delay']][:5],
                'cloudflare_managed': bool(re.search(r'BEGIN Cloudflare Managed', text, re.I)),
                'star_disallow_all': any(any(_norm_token(a) == '*' for a in g['agents']) and (False, '/') in g['rules'] for g in groups),
                'unknown_fields': sorted(set(other['unknown']))[:10], 'sha1': hashlib.sha1(rb['body']).hexdigest()[:12],
                'text_head': text[:4000]})
    res = {}
    for b in bots:
        if b['respects'] == 'no':
            res[b['id']] = {'allowed': None, 'by': 'robots.txt не используется ботом'}
            continue
        allowed, by, rule = robots_decision(groups, b['chain'], page_path)
        res[b['id']] = {'allowed': allowed, 'by': by, 'rule': rule}
    rep['bots'] = res
    return rep


# ------------------------------------------------------------------------------------------------ llms.txt
def llms_report(r):
    if 'error' in r:
        return {'status': None, 'error': r['error']}
    txt = decode_html(r['body'][:200000], r.get('headers')).lstrip('\ufeff')     # BOM допустим (llmstxt.org v2)
    first = next((l.strip() for l in txt.splitlines() if l.strip()), '')
    is_html = bool(re.search(r'<(?:!doctype|html|head|body)\b', txt[:2000], re.I))
    links = len(re.findall(r'\[[^\]]+\]\((?:https?://|/)[^)]+\)', txt))
    same_path = urlsplit(r.get('final_url') or '').path.rstrip('/').endswith(('llms.txt', 'llms-full.txt'))
    ok = r['status'] == 200 and not is_html and first.startswith('# ') and same_path
    return {'status': r['status'], 'final_url': r.get('final_url'), 'bytes': r.get('bytes'),
            'content_type': (r.get('headers') or {}).get('content-type'), 'is_html': is_html, 'first_line': first[:120],
            'h1': first.startswith('# '), 'h2_n': len(re.findall(r'^## ', txt, re.M)), 'md_links': links,
            'blockquote': bool(re.search(r'^> ', txt, re.M)), 'redirected_away': not same_path, 'valid': ok}


# ------------------------------------------------------------------------------------------------ HTML
class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0; self.parts = []; self.nos = []; self._nos = 0
        self.h = {'h1': [], 'h2': [], 'h3': []}; self._h = None; self._hbuf = []
        self.title = ''; self._title = False; self.meta = []; self.links = []; self.lang = None
        self.jsonld = []; self._ld = False; self._ldbuf = []
        self.itemtypes = []; self.rdfa = 0; self.forms = 0; self.inputs = 0; self.buttons = []; self._btn = None
        self.a_href = 0; self.canvas = 0; self.imgs = 0; self.imgs_noalt = 0; self.iframes = 0

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or '') for k, v in attrs}
        if tag == 'html':
            self.lang = a.get('lang') or a.get('xml:lang')
        elif tag == 'title':
            self._title = True
        elif tag == 'meta':
            self.meta.append(a)
        elif tag == 'link':
            self.links.append(a)
        elif tag == 'script' and a.get('type', '').lower().strip() == 'application/ld+json':
            self._ld = True; self._ldbuf = []
        elif tag == 'form':
            self.forms += 1
        elif tag in ('input', 'textarea', 'select'):
            if a.get('type', '').lower() not in ('hidden', 'submit', 'button'):
                self.inputs += 1
        elif tag == 'a' and a.get('href') and not a['href'].startswith(('javascript:', '#')):
            self.a_href += 1
        elif tag == 'canvas':
            self.canvas += 1
        elif tag == 'img':
            self.imgs += 1
            if 'alt' not in a:
                self.imgs_noalt += 1
        elif tag == 'iframe':
            self.iframes += 1
        if 'itemtype' in a:
            self.itemtypes.append(a['itemtype'].rsplit('/', 1)[-1][:40])
        if 'typeof' in a or 'vocab' in a:
            self.rdfa += 1
        if tag == 'noscript':
            self._nos += 1
        if tag in SKIP:
            self.depth += 1
        if tag in self.h and self.depth == 0:
            self._h = tag; self._hbuf = []
        if self.depth == 0 and (tag == 'button' or (tag == 'a' and ('btn' in a.get('class', '').lower() or 'button' in a.get('class', '').lower()
                                                             or a.get('role') == 'button'))):
            self._btn = []
        if tag == 'input' and a.get('type', '').lower() == 'submit' and a.get('value'):
            self.buttons.append(a['value'].strip()[:60])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._title = False
        elif tag == 'script' and self._ld:
            self._ld = False; self.jsonld.append(''.join(self._ldbuf))
        if tag == 'noscript' and self._nos:
            self._nos -= 1
        if tag in SKIP and self.depth > 0:
            self.depth -= 1
        if self._h == tag:
            self.h[tag].append(re.sub(r'\s+', ' ', ''.join(self._hbuf)).strip()); self._h = None
        if self._btn is not None and tag in ('button', 'a'):
            t = re.sub(r'\s+', ' ', ''.join(self._btn)).strip()
            if t:
                self.buttons.append(t[:60])
            self._btn = None

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._ld:
            self._ldbuf.append(data)
        if self._nos and not self._ld:
            self.nos.append(data)
        if self.depth == 0:
            self.parts.append(data)
            if self._h:
                self._hbuf.append(data)
            if self._btn is not None:
                self._btn.append(data)


def _nrm(s):
    return re.sub(r'[\s ​]+', ' ', (s or '')).strip().lower()


def jsonld_walk(o, out, d=0, parent=None):
    """Узлы с @type; parent — тип ближайшего родителя-узла (None — верхний уровень или элемент @graph)."""
    if d > 8 or o is None:
        return
    if isinstance(o, list):
        for x in o:
            jsonld_walk(x, out, d + 1, parent)
        return
    if not isinstance(o, dict):
        return
    me = parent
    if '@type' in o:
        out.append((o, parent))
        me = o['@type'] if not isinstance(o['@type'], list) else (o['@type'][0] if o['@type'] else None)
    for k, v in o.items():
        if k == '@context':
            continue
        if isinstance(v, (dict, list)):
            jsonld_walk(v, out, d + 1, None if k == '@graph' else me)


def jsonld_check(blobs):
    res = {'blocks': len(blobs), 'parse_errors': 0, 'types': [], 'issues': [], 'same_as': [], 'ids': 0, 'graph': False,
           'relative_urls': 0, 'nodes': 0}
    for b in blobs:
        raw = b.strip()
        raw = re.sub(r'^\s*<!--|-->\s*$', '', raw).strip()
        raw = re.sub(r'^//\s*<!\[CDATA\[|//\s*\]\]>$', '', raw).strip()
        try:
            data = json.loads(raw)
        except Exception as ex:
            res['parse_errors'] += 1
            res['issues'].append('JSON не разбирается: ' + str(ex)[:80])
            continue
        if isinstance(data, dict) and '@graph' in data:
            res['graph'] = True
        nodes = []
        jsonld_walk(data, nodes)
        res['nodes'] += len(nodes)
        for n, parent in nodes:
            ts = n['@type'] if isinstance(n['@type'], list) else [n['@type']]
            for t in ts:
                t = str(t).replace('http://schema.org/', '').replace('https://schema.org/', '')
                res['types'].append(t)
                bt = base_type(t)
                if not bt:
                    continue
                spec = REQ[bt]
                miss = [p for p in spec['required'] if p not in n
                        and not (p == 'itemReviewed' and parent)]      # вложенный отзыв: объект — родитель
                for grp in spec.get('any', []):
                    if not any(p in n for p in grp):
                        miss.append('|'.join(grp))
                if miss:
                    res['issues'].append(f'{t}: нет {", ".join(miss)}')
                if bt == 'FAQPage':
                    me = n.get('mainEntity')
                    me = me if isinstance(me, list) else [me] if me else []
                    def _ans_ok(a):
                        a = a if isinstance(a, list) else [a]
                        return any(isinstance(x, dict) and x.get('text') for x in a)
                    bad = [q for q in me if not (isinstance(q, dict) and q.get('name') and _ans_ok(q.get('acceptedAnswer')))]
                    if bad:
                        res['issues'].append(f'FAQPage: {len(bad)} вопросов без name или acceptedAnswer.text')
            if '@id' in n:
                res['ids'] += 1
            sa = n.get('sameAs')
            if sa:
                res['same_as'].extend(sa if isinstance(sa, list) else [sa])
            for k in ('url', 'logo', 'image', 'item'):
                v = n.get(k)
                if isinstance(v, str) and v and not v.startswith(('http://', 'https://', 'data:')):
                    res['relative_urls'] += 1
    res['types'] = sorted(set(res['types']))
    res['same_as'] = sorted(set(map(str, res['same_as'])))[:20]
    res['issues'] = res['issues'][:20]
    return res


def head_report(p, final_url, headers):
    metas = {}
    for m in p.meta:
        k = (m.get('name') or m.get('property') or m.get('http-equiv') or '').lower().strip()
        if k:
            metas.setdefault(k, []).append(m.get('content', ''))
    canon = [l.get('href') for l in p.links if 'canonical' in l.get('rel', '').lower().split()]
    alts = [{'hreflang': l.get('hreflang'), 'href': l.get('href')} for l in p.links
            if 'alternate' in l.get('rel', '').lower().split() and l.get('hreflang')]
    xrt = headers.get('x-robots-tag')
    robots_meta = {k: metas[k] for k in ('robots', 'googlebot', 'yandex', 'bingbot', 'applebot', 'googlebot-news') if k in metas}
    all_rm = ' '.join(v for vs in robots_meta.values() for v in vs).lower() + ' ' + (xrt or '').lower()
    c0 = canon[0] if canon else None
    c_abs = urljoin(final_url, c0) if c0 else None
    def _strip(u):
        s = urlsplit(u or '')
        return urlunsplit((s.scheme, s.netloc.lower(), s.path.rstrip('/') or '/', s.query, ''))
    og = {k: v[0][:200] for k, v in metas.items() if k.startswith('og:')}
    tw = {k: v[0][:200] for k, v in metas.items() if k.startswith('twitter:')}
    title = re.sub(r'\s+', ' ', p.title).strip()
    desc = (metas.get('description') or [''])[0].strip()
    return {'title': title[:200], 'title_len': len(title), 'description_len': len(desc), 'description': desc[:300],
            'lang': p.lang, 'viewport': bool(metas.get('viewport')), 'robots_meta': robots_meta, 'x_robots_tag': xrt,
            'noindex': 'noindex' in all_rm or 'none' in re.findall(r'\bnone\b', all_rm),
            'nosnippet': 'nosnippet' in all_rm, 'max_snippet': re.findall(r'max-snippet:\s*(-?\d+)', all_rm),
            'noarchive': 'noarchive' in all_rm, 'nocache': 'nocache' in all_rm,
            'canonical_n': len(canon), 'canonical': c_abs, 'canonical_relative': bool(c0 and not c0.startswith('http')),
            'canonical_self': (_strip(c_abs) == _strip(final_url)) if c_abs else None,
            'hreflang_n': len(alts), 'hreflang': alts[:12], 'hreflang_xdefault': any((a['hreflang'] or '').lower() == 'x-default' for a in alts),
            'og': og, 'og_image_abs': bool(og.get('og:image', '').startswith('http')), 'twitter': tw,
            'md_alternate': [l.get('href') for l in p.links if 'alternate' in l.get('rel', '').lower().split()
                             and 'markdown' in l.get('type', '').lower()][:3],
            'favicon': any('icon' in l.get('rel', '').lower() for l in p.links),
            'manifest': any('manifest' in l.get('rel', '').lower() for l in p.links)}


def offsets(raw_bytes):
    def pos(rx):
        m = re.search(rx, raw_bytes, re.I)
        return m.start() if m else None
    ogs = [m.start() for m in re.finditer(rb'<meta[^>]+property=["\']og:', raw_bytes, re.I)]
    return {'head_end': pos(rb'</head\s*>'), 'h1': pos(rb'<h1[\s>]'), 'og_last': max(ogs) if ogs else None,
            'jsonld_first': pos(rb'application/ld\+json')}


def text_report(p, raw_html):
    text = _nrm(' '.join(p.parts))
    words = len(WORD_RE.findall(text))
    nos = _nrm(' '.join(p.nos))
    prices = sorted(set(_nrm(m.group(0)) for m in PRICE_RE.finditer(text)))[:30]
    spa = [k for k, rx in SPA_MARKERS.items() if re.search(rx, raw_html[:400000])]
    plat = [k for k, rx in PLATFORM_MARKERS.items() if re.search(rx, raw_html[:400000], re.I)]
    ctas = [b for b in p.buttons if CTA_RE.search(b)]
    return {'words': words, 'noscript_words': len(WORD_RE.findall(nos)), 'h1_n': len(p.h['h1']), 'h1': p.h['h1'][:3],
            'h2_n': len(p.h['h2']), 'h3_n': len(p.h['h3']), 'prices_n': len(prices), 'prices': prices[:8],
            'cta_texts': ctas[:8], 'buttons_n': len(p.buttons), 'forms': p.forms, 'inputs': p.inputs, 'a_href': p.a_href,
            'canvas': p.canvas, 'imgs': p.imgs, 'imgs_noalt': p.imgs_noalt, 'iframes': p.iframes,
            'spa_markers': spa, 'platform': plat, 'microdata_types': sorted(set(p.itemtypes))[:15], 'rdfa_attrs': p.rdfa,
            'text_sample': text[:600]}


def cdn_of(headers):
    h = headers or {}
    s = (h.get('server') or '').lower()
    out = []
    if 'cf-ray' in h or 'cloudflare' in s:
        out.append('cloudflare')
    if 'ddos-guard' in s or any(k.startswith('ddg') for k in h):
        out.append('ddos-guard')
    if 'qrator' in s or 'x-qrator' in ' '.join(h):
        out.append('qrator')
    if 'x-amz-cf-id' in h or 'cloudfront' in s:
        out.append('cloudfront')
    if 'x-vercel-id' in h:
        out.append('vercel')
    if 'x-nf-request-id' in h or 'netlify' in s:
        out.append('netlify')
    if 'akamai' in s or 'x-akamai-transformed' in h:
        out.append('akamai')
    if 'x-served-by' in h and 'cache' in (h.get('x-served-by') or '').lower():
        out.append('fastly')
    if 'ngenix' in s:
        out.append('ngenix')
    return out


# ------------------------------------------------------------------------------------------------ отрисовка (опция)
def mem_available_gb():
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) / 1024 / 1024
    except Exception:
        return None


class BrowserLocks:
    def __init__(self, wait=900):
        self.wait = wait; self.fhs = []

    def __enter__(self):
        t0 = time.time()
        for p in LOCKS:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            fh = open(p, 'a+')
            while True:
                try:
                    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB); break
                except BlockingIOError:
                    if time.time() - t0 > self.wait:
                        raise TimeoutError('блокировка браузера занята > %d с: %s' % (self.wait, p))
                    time.sleep(2)
            self.fhs.append(fh)
        self.waited = round(time.time() - t0, 1)
        return self

    def __exit__(self, *a):
        for fh in reversed(self.fhs):
            try:
                fcntl.flock(fh, fcntl.LOCK_UN); fh.close()
            except Exception:
                pass


RENDER_JS = r"""() => {
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  const vis = el => { const r = el.getBoundingClientRect(); const cs = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0.05; };
  const words = (norm(document.body ? document.body.innerText : '').match(/[\p{L}\p{N}]+/gu) || []).length;
  const h1 = [...document.querySelectorAll('h1')].map(e => norm(e.innerText)).filter(Boolean).slice(0, 3);
  const vh = innerHeight;
  const cands = [...document.querySelectorAll('a[href],button,[role=button],input[type=submit]')].filter(vis)
    .map(e => ({t: norm(e.innerText || e.value || ''), y: e.getBoundingClientRect().top + scrollY}))
    .filter(c => c.t && c.t.length <= 60 && c.y < vh * 1.5);
  const ld = [...document.querySelectorAll('script[type="application/ld+json"]')].map(s => s.textContent);
  return {words, h1, cta_first_screen: cands.map(c => c.t).slice(0, 12), jsonld: ld, text: norm(document.body ? document.body.innerText : '').slice(0, 200000)};
}"""


def render(url, timeout=60):
    from playwright.sync_api import sync_playwright
    for _ in range(60):
        m = mem_available_gb()
        if m is None or m >= 3.0:
            break
        time.sleep(10)
    with BrowserLocks() as lk:
        t0 = time.time()
        with sync_playwright() as pw:
            b = pw.chromium.launch(headless=True)
            try:
                pg = b.new_page(user_agent=UA_BROWSER, viewport={'width': 1440, 'height': 900}, locale='ru-RU')
                pg.goto(url, wait_until='domcontentloaded', timeout=timeout * 1000)
                try:
                    pg.wait_for_load_state('networkidle', timeout=15000)
                except Exception:
                    pass
                pg.wait_for_timeout(1500)
                d = pg.evaluate(RENDER_JS)
            finally:
                b.close()
        d['lock_wait_s'] = lk.waited; d['render_s'] = round(time.time() - t0, 1)
        return d


def nojs_compare(raw_text_norm, raw_jsonld_types, rd):
    """Как M (nojs_compare): доля слов, h1 и главный призыв в сыром тексте, цены, JSON-LD только из JS."""
    rw = len(WORD_RE.findall(raw_text_norm))
    rendw = rd.get('words') or 0
    h1d = [_nrm(h) for h in rd.get('h1') or []]
    ctas = [c for c in rd.get('cta_first_screen') or [] if CTA_RE.search(c)]
    main_cta = ctas[0] if ctas else None
    rtext = _nrm(rd.get('text'))
    prices = sorted(set(_nrm(m.group(0)) for m in PRICE_RE.finditer(rtext)))[:30]
    raw_c = re.sub(r'\s', '', raw_text_norm)
    pf = sum(1 for x in prices if re.sub(r'\s', '', x) in raw_c)
    ld_dom = jsonld_check(rd.get('jsonld') or [])['types']
    return {'raw_words': rw, 'rendered_words': rendw, 'ratio': round(rw / rendw, 2) if rendw else None,
            'h1_rendered': h1d[:2], 'h1_match': bool(h1d and any(h[:40] in raw_text_norm for h in h1d)),
            'main_cta': main_cta, 'main_cta_in_raw': (_nrm(main_cta)[:40] in raw_text_norm) if main_cta else None,
            'prices_rendered': len(prices), 'prices_in_raw': pf,
            'jsonld_js_only': sorted(set(ld_dom) - set(raw_jsonld_types)),
            'lock_wait_s': rd.get('lock_wait_s'), 'render_s': rd.get('render_s')}


# ------------------------------------------------------------------------------------------------ одна страница
def probe(url, pid=None, do_render=False, ua_probe=False, crawlers=CRAWLERS, meta=None):
    bots, _ = load_crawlers(crawlers)
    out = {'id': pid, 'url': url, 'tool': 'geo_probe.py ' + VERSION, 'at': time.strftime('%Y-%m-%d %H:%M'), 'meta': meta or {}}
    pg = http_get(url)
    if 'error' in pg:
        out['page'] = {'error': pg['error']}
        return out
    hdr = pg['headers']
    raw_html = decode_html(pg['body'], hdr)
    out['page'] = {'status': pg['status'], 'final_url': pg['final_url'], 'redirects': [c['status'] for c in pg['chain']],
                   'content_type': hdr.get('content-type'), 'content_encoding': hdr.get('content-encoding'),
                   'server': hdr.get('server'), 'cdn': cdn_of(hdr), 'html_bytes': pg['bytes'],
                   'over_googlebot_2mb': pg['bytes'] > GOOGLEBOT_HTML_LIMIT, 'offsets': offsets(pg['body']),
                   'challenge': (bool(CHALLENGE_RE.search(raw_html[:30000])) and len(WORD_RE.findall(raw_html[:30000])) < 400)
                                or (pg['bytes'] < 6000 and any(c in ('qrator', 'ddos-guard') for c in cdn_of(hdr))),
                   'tls_untrusted': pg.get('tls_untrusted'), 'tls_error': (pg.get('tls_error') or '')[:160] or None,
                   't': pg['t']}
    o = out['page']['offsets']
    out['page']['og_after_1mb'] = bool(o.get('og_last') and o['og_last'] > FB_OG_LIMIT)
    p = Page()
    try:
        p.feed(raw_html); p.close()
    except Exception as ex:
        out['parse_error'] = str(ex)[:120]
    out['head'] = head_report(p, pg['final_url'], hdr)
    out['text'] = text_report(p, raw_html)
    out['jsonld'] = jsonld_check(p.jsonld)
    out['jsonld_raw'] = [b[:20000] for b in p.jsonld[:10]]          # для --revalidate
    fu = urlsplit(pg['final_url'])
    origin = f'{fu.scheme}://{fu.netloc}'
    page_path = (fu.path or '/') + (('?' + fu.query) if fu.query else '')
    rb = http_get(origin + '/robots.txt', max_redirects=5)
    out['robots'] = robots_report(rb, page_path, bots)
    out['robots_path'] = page_path
    out['llms'] = llms_report(http_get(origin + '/llms.txt', max_redirects=5))
    out['llms_full'] = llms_report(http_get(origin + '/llms-full.txt', max_redirects=5))
    if ua_probe:
        base_words = out['text']['words']
        up = {}
        for name, ua in UA_BOTS.items():
            r = http_get(url, ua=ua)
            if 'error' in r:
                up[name] = {'error': r['error'][:80]}
                continue
            h2 = decode_html(r['body'], r['headers']); q = Page()
            try:
                q.feed(h2); q.close()
            except Exception:
                pass
            w = len(WORD_RE.findall(_nrm(' '.join(q.parts))))
            up[name] = {'status': r['status'], 'bytes': r['bytes'], 'words': w,
                        'words_vs_browser': round(w / base_words, 2) if base_words else None,
                        'challenge': bool(CHALLENGE_RE.search(h2[:30000]))}
        out['ua_probe'] = up
    if do_render:
        try:
            rd = render(pg['final_url'])
            out['render'] = nojs_compare(_nrm(' '.join(p.parts)), out['jsonld']['types'], rd)
        except Exception as ex:
            out['render'] = {'error': type(ex).__name__ + ': ' + str(ex)[:160]}
    out['flags'] = flags(out)
    return out


def flags(o):
    f = []
    pg, hd, tx, rb, js = o.get('page', {}), o.get('head', {}), o.get('text', {}), o.get('robots', {}), o.get('jsonld', {})
    if pg.get('status') and pg['status'] != 200:
        f.append(f"page-status-{pg['status']}")
    if pg.get('challenge'):
        f.append('antibot-challenge')
    if pg.get('tls_untrusted') or 'SSLError' in str(pg.get('error') or ''):
        f.append('tls-untrusted-chain')
    if pg.get('over_googlebot_2mb'):
        f.append('html-over-2mb')
    if pg.get('og_after_1mb'):
        f.append('og-after-1mb')
    if hd.get('noindex'):
        f.append('noindex')
    if hd.get('nosnippet'):
        f.append('nosnippet')
    if hd.get('noarchive') or hd.get('nocache'):
        f.append('noarchive-or-nocache')
    if not hd.get('title'):
        f.append('no-title')
    if not hd.get('description_len'):
        f.append('no-description')
    if hd.get('canonical_n', 0) == 0:
        f.append('no-canonical')
    elif hd.get('canonical_n', 0) > 1:
        f.append('multiple-canonical')
    elif hd.get('canonical_self') is False:
        f.append('canonical-elsewhere')
    if not hd.get('lang'):
        f.append('no-lang')
    if not hd.get('og', {}).get('og:image'):
        f.append('no-og-image')
    elif not hd.get('og_image_abs'):
        f.append('og-image-relative')
    if tx.get('h1_n', 0) == 0:
        f.append('no-h1-in-raw')
    elif tx.get('h1_n', 0) > 1:
        f.append('multiple-h1')
    if tx.get('words', 0) < 50:
        f.append('raw-text-under-50-words')
    elif tx.get('words', 0) < 200:
        f.append('raw-text-under-200-words')
    if tx.get('spa_markers') and tx.get('words', 0) < 150:
        f.append('csr-shell')
    if js.get('blocks', 0) == 0:
        f.append('no-jsonld')
    if js.get('parse_errors'):
        f.append('jsonld-parse-error')
    if js.get('issues'):
        f.append('jsonld-missing-required')
    eff = rb.get('effective')
    if eff == 'unreachable-assume-disallow':
        f.append('robots-5xx-or-unreachable')
    if eff == 'parsed':
        if rb.get('looks_html'):
            f.append('robots-is-html')
        if rb.get('star_disallow_all'):
            f.append('robots-star-disallow-all')
        bots = rb.get('bots') or {}
        for bid in ('google-googlebot', 'yandex-yandexbot'):
            if bots.get(bid, {}).get('allowed') is False:
                f.append('blocked-' + bid)
        for bid, v in bots.items():
            if v.get('allowed') is False and bid in ('yandex-additional', 'openai-oai-searchbot', 'perplexity-perplexitybot',
                                                     'anthropic-claude-searchbot', 'microsoft-bingbot', 'google-adsbot'):
                f.append('blocked-' + bid)
        if rb.get('content_signal'):
            f.append('content-signal')
        if rb.get('cloudflare_managed'):
            f.append('cloudflare-managed-robots')
    if (o.get('llms') or {}).get('valid'):
        f.append('llms-txt')
    rr = o.get('render') or {}
    if rr.get('ratio') is not None and rr['ratio'] < 0.5:
        f.append('nojs-ratio-under-0.5')
    if rr.get('h1_match') is False:
        f.append('h1-js-only')
    if rr.get('main_cta_in_raw') is False:
        f.append('cta-js-only')
    if rr.get('prices_rendered') and rr.get('prices_in_raw', 0) < rr['prices_rendered']:
        f.append('prices-js-only')
    if rr.get('jsonld_js_only'):
        f.append('jsonld-js-only')
    for name, v in (o.get('ua_probe') or {}).items():
        if v.get('status') and pg.get('status') and v['status'] != pg['status']:
            f.append(f'ua-{name}-status-{v["status"]}')
        elif v.get('words_vs_browser') is not None and (v['words_vs_browser'] < 0.7 or v['words_vs_browser'] > 1.43):
            f.append(f'ua-{name}-text-differs')
    return f


# ------------------------------------------------------------------------------------------------ партия, сводка
def read_pages(path):
    with open(path, encoding='utf-8') as fh:
        lines = [l for l in fh if l.strip() and not l.startswith('#')]
    return list(csv.DictReader(lines, delimiter='\t'))


SUMMARY_COLS = ['id', 'group', 'page_type', 'status', 'final_host', 'cdn', 'challenge', 'tls_untrusted', 'html_kb', 'over_2mb', 'title_len',
                'desc_len', 'lang', 'canonical', 'noindex', 'nosnippet', 'hreflang_n', 'og_image', 'h1_raw', 'words_raw',
                'spa', 'platform', 'jsonld_blocks', 'jsonld_types', 'jsonld_issues', 'same_as_n', 'microdata',
                'robots_status', 'robots_effective', 'robots_agents_n', 'content_signal', 'cf_managed',
                'allow_googlebot', 'allow_google_extended', 'allow_yandexbot', 'allow_yandex_additional',
                'allow_oai_searchbot', 'allow_gptbot', 'allow_chatgpt_user', 'allow_perplexitybot', 'allow_claudebot',
                'allow_claude_searchbot', 'allow_bingbot', 'allow_applebot', 'allow_applebot_extended', 'allow_ccbot',
                'allow_meta_externalagent', 'allow_adsbot', 'llms_txt', 'llms_status', 'llms_full', 'nojs_ratio',
                'nojs_h1', 'nojs_cta', 'nojs_prices', 'jsonld_js_only', 'flags']
BOTCOL = {'allow_googlebot': 'google-googlebot', 'allow_google_extended': 'google-extended', 'allow_yandexbot': 'yandex-yandexbot',
          'allow_yandex_additional': 'yandex-additional', 'allow_oai_searchbot': 'openai-oai-searchbot', 'allow_gptbot': 'openai-gptbot',
          'allow_chatgpt_user': 'openai-chatgpt-user', 'allow_perplexitybot': 'perplexity-perplexitybot',
          'allow_claudebot': 'anthropic-claudebot', 'allow_claude_searchbot': 'anthropic-claude-searchbot',
          'allow_bingbot': 'microsoft-bingbot', 'allow_applebot': 'apple-applebot', 'allow_applebot_extended': 'apple-applebot-extended',
          'allow_ccbot': 'commoncrawl-ccbot', 'allow_meta_externalagent': 'meta-externalagent', 'allow_adsbot': 'google-adsbot'}


def summary_row(o):
    pg, hd, tx, js, rb = o.get('page', {}), o.get('head', {}), o.get('text', {}), o.get('jsonld', {}), o.get('robots', {})
    rr = o.get('render') or {}
    bots = rb.get('bots') or {}
    def yn(v):
        return '' if v is None else ('1' if v else '0')
    row = {'id': o.get('id'), 'group': (o.get('meta') or {}).get('group', ''), 'page_type': (o.get('meta') or {}).get('page_type', ''),
           'status': pg.get('status', pg.get('error', '')), 'final_host': urlsplit(pg.get('final_url') or '').hostname or '',
           'cdn': ','.join(pg.get('cdn') or []), 'challenge': yn(pg.get('challenge')),
           'tls_untrusted': yn(pg.get('tls_untrusted') or ('SSLError' in str(pg.get('error') or '')) or None),
           'html_kb': round((pg.get('html_bytes') or 0) / 1024, 1), 'over_2mb': yn(pg.get('over_googlebot_2mb')),
           'title_len': hd.get('title_len'), 'desc_len': hd.get('description_len'), 'lang': hd.get('lang') or '',
           'canonical': ('none' if not hd.get('canonical_n') else 'multi' if hd.get('canonical_n', 0) > 1 else
                         'self' if hd.get('canonical_self') else 'other'),
           'noindex': yn(hd.get('noindex')), 'nosnippet': yn(hd.get('nosnippet')), 'hreflang_n': hd.get('hreflang_n'),
           'og_image': ('abs' if hd.get('og_image_abs') else 'rel' if (hd.get('og') or {}).get('og:image') else 'none'),
           'h1_raw': tx.get('h1_n'), 'words_raw': tx.get('words'), 'spa': ','.join(tx.get('spa_markers') or []),
           'platform': ','.join(tx.get('platform') or []), 'jsonld_blocks': js.get('blocks'),
           'jsonld_types': ','.join(js.get('types') or [])[:200], 'jsonld_issues': len(js.get('issues') or []),
           'same_as_n': len(js.get('same_as') or []), 'microdata': ','.join(tx.get('microdata_types') or [])[:120],
           'robots_status': rb.get('status'), 'robots_effective': rb.get('effective'), 'robots_agents_n': len(rb.get('agents') or []),
           'content_signal': ' | '.join(rb.get('content_signal') or [])[:80], 'cf_managed': yn(rb.get('cloudflare_managed')),
           'llms_txt': yn((o.get('llms') or {}).get('valid')), 'llms_status': (o.get('llms') or {}).get('status'),
           'llms_full': yn((o.get('llms_full') or {}).get('valid')), 'nojs_ratio': rr.get('ratio'),
           'nojs_h1': yn(rr.get('h1_match')), 'nojs_cta': yn(rr.get('main_cta_in_raw')),
           'nojs_prices': f"{rr.get('prices_in_raw')}/{rr.get('prices_rendered')}" if rr.get('prices_rendered') else '',
           'jsonld_js_only': ','.join(rr.get('jsonld_js_only') or []), 'flags': ' '.join(o.get('flags') or [])}
    for col, bid in BOTCOL.items():
        row[col] = yn((bots.get(bid) or {}).get('allowed'))
    return row


def batch(pages_tsv, out, do_render=False, ua_probe=False, only=None, skip_done=False, crawlers=CRAWLERS):
    os.makedirs(out, exist_ok=True)
    rows = read_pages(pages_tsv)
    log = open(os.path.join(out, 'batch.log'), 'a', encoding='utf-8')
    for r in rows:
        pid, url = r.get('id'), r.get('url') or r.get('final_url')
        if not pid or not url or (only and pid not in only):
            continue
        fn = os.path.join(out, pid + '.json')
        if skip_done and os.path.exists(fn):
            continue
        t0 = time.time()
        try:
            o = probe(url, pid, do_render, ua_probe, crawlers, meta={k: v for k, v in r.items() if k not in ('id', 'url')})
        except Exception as ex:
            o = {'id': pid, 'url': url, 'error': type(ex).__name__ + ': ' + str(ex)[:200]}
        json.dump(o, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
        log.write(f"{time.strftime('%H:%M:%S')}\t{pid}\t{round(time.time() - t0, 1)}s\t{' '.join(o.get('flags') or [])[:200]}\n"); log.flush()
        print(pid, round(time.time() - t0, 1), (o.get('page') or {}).get('status'), ' '.join(o.get('flags') or [])[:160], flush=True)


def summary(out):
    w = csv.DictWriter(sys.stdout, fieldnames=SUMMARY_COLS, delimiter='\t', extrasaction='ignore')
    w.writeheader()
    for fn in sorted(os.listdir(out)):
        if fn.endswith('.json'):
            try:
                w.writerow(summary_row(json.load(open(os.path.join(out, fn), encoding='utf-8'))))
            except Exception as ex:
                print('# ошибка', fn, ex, file=sys.stderr)


def revalidate(out, crawlers=CRAWLERS):
    bots, _ = load_crawlers(crawlers)
    for fn in sorted(os.listdir(out)):
        if not fn.endswith('.json'):
            continue
        path = os.path.join(out, fn)
        o = json.load(open(path, encoding='utf-8'))
        if o.get('jsonld_raw') is not None:
            o['jsonld'] = jsonld_check(o['jsonld_raw'])
        rb = o.get('robots') or {}
        if rb.get('effective') == 'parsed' and rb.get('text_head') is not None and not rb.get('over_500kib'):
            groups, _ = parse_robots(rb['text_head'])
            if len(rb['text_head']) < 4000:          # файл целиком в text_head — можно пересчитать решения
                rb['bots'] = {b['id']: ({'allowed': None, 'by': 'robots.txt не используется ботом'} if b['respects'] == 'no' else
                                        dict(zip(('allowed', 'by', 'rule'), robots_decision(groups, b['chain'], o.get('robots_path') or '/'))))
                              for b in bots}
        o['flags'] = flags(o)
        json.dump(o, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
    print('пересчитано:', out)


# ------------------------------------------------------------------------------------------------ самопроверка
def selftest():
    ok = 0; bad = 0
    def ck(name, got, exp):
        nonlocal ok, bad
        if got == exp:
            ok += 1; print('PASS', name)
        else:
            bad += 1; print('FAIL', name, 'got', got, 'expected', exp)
    rt = """User-agent: *
Disallow: /private
Allow: /private/public
Disallow: /*.pdf$

User-agent: Googlebot
Disallow: /nogoogle

User-agent: Yandex
Disallow: /noyandex

User-agent: YandexAdditional
Disallow: /

User-agent: GPTBot
User-agent: ClaudeBot
Disallow: /
Sitemap: https://ex.ru/sitemap.xml
Content-Signal: search=yes, ai-train=no
"""
    g, other = parse_robots(rt)
    ck('groups', len(g), 5)
    ck('sitemap не рвёт группу GPTBot+ClaudeBot', g[-1]['agents'], ['GPTBot', 'ClaudeBot'])
    ck('content-signal', other['content-signal'], ['search=yes, ai-train=no'])
    ck('* longest: /private запрещён', robots_decision(g, ['SomeBot', '*'], '/private/x')[0], False)
    ck('* longest: /private/public разрешён', robots_decision(g, ['SomeBot', '*'], '/private/public/a')[0], True)
    ck('$: /a.pdf запрещён', robots_decision(g, ['SomeBot', '*'], '/a.pdf')[0], False)
    ck('$: /a.pdf?x разрешён', robots_decision(g, ['SomeBot', '*'], '/a.pdf?x=1')[0], True)
    ck('своя группа Googlebot заменяет *', robots_decision(g, ['Googlebot', '*'], '/private/x')[0], True)
    ck('Googlebot /nogoogle', robots_decision(g, ['Googlebot', '*'], '/nogoogle')[0], False)
    ck('Applebot → группа Googlebot', robots_decision(g, ['Applebot', 'Googlebot', '*'], '/nogoogle')[0], False)
    ck('YandexBot → группа Yandex', robots_decision(g, ['YandexBot', 'Yandex', '*'], '/noyandex')[0], False)
    ck('YandexBot → группа Yandex, * не действует', robots_decision(g, ['YandexBot', 'Yandex', '*'], '/private/x')[0], True)
    ck('YandexAdditional свой запрет', robots_decision(g, ['YandexAdditional'], '/')[0], False)
    ck('AdsBot без группы * — разрешён', robots_decision(g, ['AdsBot-Google'], '/private/x')[0], True)
    ck('GPTBot запрет', robots_decision(g, ['GPTBot', '*'], '/')[0], False)
    ck('регистр токена', robots_decision(g, ['gptbot', '*'], '/')[0], False)
    g2, _ = parse_robots("User-agent: *\nDisallow: /page\nAllow: /page\n")
    ck('равенство allow/disallow → allow', robots_decision(g2, ['X', '*'], '/page')[0], True)
    g3, _ = parse_robots("Disallow: /x\nUser-agent: *\nAllow: /\n")
    ck('правило вне группы игнорируется', robots_decision(g3, ['X', '*'], '/x')[0], True)
    g4, _ = parse_robots("User-agent: googlebot/1.2\nDisallow: /a\n")
    ck('googlebot/1.2 ≡ googlebot', robots_decision(g4, ['Googlebot', '*'], '/a')[0], False)
    ck('/robots.txt всегда разрешён', robots_decision(parse_robots("User-agent: *\nDisallow: /\n")[0], ['X', '*'], '/robots.txt')[0], True)
    g5, _ = parse_robots("User-agent: *\nDisallow: /каталог\n")
    ck('кириллица в пути', robots_decision(g5, ['X', '*'], quote('/каталог/1'))[0], False)
    html = """<!doctype html><html lang="ru"><head><title>Тест</title><meta name="description" content="Описание">
<link rel="canonical" href="/p"><meta property="og:image" content="https://ex.ru/og.png">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","name":"О","sameAs":["https://vk.com/o"]},
{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Q?","acceptedAnswer":{"@type":"Answer","text":"A"}},{"@type":"Question","name":"Q2"}]},
{"@type":"Product","name":"P"}]}</script></head>
<body><h1>Ремонт квартир</h1><p>Цена от 9 800 ₽ за м²</p><a class="btn" href="/order">Оставить заявку</a>
<script>var x="невидимый текст";</script><noscript>Включите JS</noscript></body></html>"""
    p = Page(); p.feed(html); p.close()
    hr = head_report(p, 'https://ex.ru/p', {})
    ck('canonical self', hr['canonical_self'], True)
    ck('canonical relative', hr['canonical_relative'], True)
    tr = text_report(p, html)
    ck('h1', tr['h1'], ['Ремонт квартир'])
    ck('script и noscript не в словах', 'невидимый' in tr['text_sample'] or 'включите' in tr['text_sample'], False)
    ck('цена', tr['prices_n'], 1)
    ck('призыв', tr['cta_texts'], ['Оставить заявку'])
    js = jsonld_check(p.jsonld)
    ck('типы @graph', js['types'], ['Answer', 'FAQPage', 'Organization', 'Product', 'Question'])
    ck('FAQ без ответа и Product без offers', sorted(js['issues']),
       sorted(['FAQPage: 1 вопросов без name или acceptedAnswer.text', 'Product: нет offers|review|aggregateRating', 'Question: нет acceptedAnswer']))
    ck('sameAs', js['same_as'], ['https://vk.com/o'])
    js2 = jsonld_check(['{"@type":"Product","name":"P","offers":{"@type":"Offer","price":"1"},"review":[{"@type":"Review",'
                        '"reviewRating":{"@type":"Rating","ratingValue":5},"author":{"@type":"Person","name":"И"}}]}',
                        '{"@type":"FAQPage","mainEntity":[{"@type":"Question","name":"Q","acceptedAnswer":[{"@type":"Answer","text":"A"}]}]}',
                        '{"@type":"Review","reviewRating":{"@type":"Rating","ratingValue":5},"author":"И"}'])
    ck('вложенный Review без itemReviewed — норма; верхний — нет; ответ списком — норма', js2['issues'], ['Review: нет itemReviewed'])
    lr = llms_report({'status': 200, 'final_url': 'https://ex.ru/llms.txt', 'bytes': 50, 'headers': {'content-type': 'text/plain'},
                      'body': '# Ex\n> Кратко\n## Docs\n- [A](https://ex.ru/a.md)\n'.encode()})
    ck('llms.txt валиден', lr['valid'], True)
    lr2 = llms_report({'status': 200, 'final_url': 'https://ex.ru/', 'bytes': 50, 'headers': {'content-type': 'text/html'},
                       'body': b'<!doctype html><html><body>home</body></html>'})
    ck('llms.txt как HTML-заглушка', (lr2['valid'], lr2['is_html'], lr2['redirected_away']), (False, True, True))
    print(f'итог: {ok} PASS, {bad} FAIL')
    return bad == 0


def main():
    global INSECURE_RETRY
    a = sys.argv[1:]
    if not a or '-h' in a or '--help' in a:
        print(__doc__); return
    def opt(name, default=None):
        return a[a.index(name) + 1] if name in a else default
    crawlers = opt('--crawlers', CRAWLERS)
    if '--selftest' in a:
        sys.exit(0 if selftest() else 1)
    if '--summary' in a:
        summary(opt('--summary')); return
    if '--revalidate' in a:
        revalidate(opt('--revalidate'), crawlers); return
    INSECURE_RETRY = '--insecure-retry' in a
    if '--batch' in a:
        only = set(opt('--only').split(',')) if opt('--only') else None
        batch(opt('--batch'), opt('--out', 'geo_probe_out'), '--render' in a, '--ua-probe' in a, only, '--skip-done' in a, crawlers)
        return
    url = a[0]
    o = probe(url, opt('--id'), '--render' in a, '--ua-probe' in a, crawlers)
    out = opt('--out')
    if out:
        os.makedirs(out, exist_ok=True)
        fn = os.path.join(out, (opt('--id') or re.sub(r'\W+', '_', urlsplit(url).netloc + urlsplit(url).path).strip('_')[:80]) + '.json')
        json.dump(o, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
        print(fn)
    s = {k: o.get(k) for k in ('id', 'url', 'flags')}
    s['robots_bots'] = {k: v.get('allowed') for k, v in ((o.get('robots') or {}).get('bots') or {}).items()}
    print(json.dumps(s, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
