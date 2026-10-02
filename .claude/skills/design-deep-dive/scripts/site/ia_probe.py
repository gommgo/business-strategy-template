#!/usr/bin/env python3
"""ia_probe.py — структура многостраничного сайта по HTTP: robots, sitemap, шаблоны URL, шапка и подвал, крошки, hreflang, 404.

Что меряет (один сайт или партия):
  robots.txt (статус, строки Sitemap, группы, Disallow для *, Crawl-delay) →
  sitemap.xml и индекс sitemap (число URL, lastmod, hreflang в sitemap) →
  типы URL по шаблонам путей, распределение глубины URL, языковые префиксы и поддомены →
  выборка страниц ТОЛЬКО из sitemap (+ корень сайта): шапка (пункты верхнего уровня, подменю, признаки мега-меню,
  поиск, телефон, переключатель языка, вход, кнопки), подвал (ссылки, группы, юридические ссылки, реквизиты, соцсети,
  HTML-карта сайта), хлебные крошки (разметкой HTML и BreadcrumbList в JSON-LD / microdata / RDFa), hreflang в <head>,
  контекстные ссылки и блоки «читайте также» →
  ответ на несуществующий адрес (код 404, «мягкая» 404, редирект на главную).

Вежливость: ≤ 1 запроса в секунду на хост (каждый редирект — отдельный запрос с паузой);
≤ 200 запросов на сайт (robots + sitemap + страницы + проба 404); страницы — только адреса из sitemap.xml и корень;
по ссылкам не ходим; robots.txt соблюдается (RFC 9309: 4xx — ограничений нет; 5xx или недоступен — страницы не
запрашиваем); Crawl-delay > 1 с — соблюдается (до 10 с); антибот-заглушка (Cloudflare, DDoS-Guard, Qrator) —
отметка blocked и остановка без обхода. Браузер не нужен: только стандартная библиотека Python 3.

Запуск (код-репо — соседним чекаутом ../strategy/.claude/skills/design-deep-dive/scripts/site/ia_probe.py):
  ia_probe.py https://example.ru [--out DIR] [--sample 14]    # по умолчанию DIR — $DDD_HOME/out/site/ia_probe
  ia_probe.py --summary DIR > summary.tsv                      # сводная таблица по ia.json
  ia_probe.py --selftest                                       # локальный сервер с фикстурами
Обслуживание базы — обход корпуса сайтов базы знаний (группа «обслуживание базы» в справке ключей); разбору сайта
проекта эти ключи не нужны:
  ia_probe.py --batch sites.tsv --out DIR [--skip-done]        # TSV: id, url, site_type, market, note

Выход: DIR/<id>/ia.json (всё), DIR/<id>/ia.md (коротко); ia.json читает page_gates.py --ia (строки scope: site).
"""

import argparse
import gzip
import hashlib
import html
import io
import json
import os
import random
import re
import socket
import ssl
import statistics
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET
from collections import Counter, OrderedDict, defaultdict
from html.parser import HTMLParser
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402

VERSION = "1.1"
UA_TOKEN = "ia_probe"
USER_AGENT = ("Mozilla/5.0 (compatible; ia_probe/%s; site-research structure probe; "
              "1 req/s, sitemap-only, no crawling)" % VERSION)
MAX_REQUESTS_DEFAULT = 200
MIN_DELAY = 1.0
MAX_HTML_BYTES = 6 * 1024 * 1024
MAX_SITEMAP_BYTES = 25 * 1024 * 1024
MAX_SITEMAP_URLS = 60000
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}

LANG_CODES = set("""ru en de fr es it pt zh ja ko ar tr pl uk kk be uz nl sv fi no nb da cs sk hu ro bg el he hi id th vi
sr hr sl lt lv et ka hy az ms fa ur bn ta ky tg mn""".split())
LANG_SEG_RE = re.compile(r"^([a-z]{2})(?:[-_]([a-z]{2}))?$", re.I)

# Тип раздела по сегменту пути (RU транслит + EN). Порядок проверки важен: первое совпадение.
SEG_TYPES = [
    ("legal", r"privacy|privacy-policy|policy|politika.*|politic.*|legal|terms|terms-.*|tos|oferta|publichnaya-oferta|"
              r"dogovor-oferty|soglasie.*|consent|personal-data|personalnye-dannye|pd|cookies?|cookie-policy|agreement|"
              r"user-agreement|pravila|rules|disclaimer|imprint|impressum|requisites|rekvizity"),
    ("account", r"login|signin|sign-in|log-in|signup|sign-up|register|registration|account|cabinet|kabinet|lk|my|"
                r"dashboard|auth|profile|cart|korzina|checkout"),
    ("search", r"search|poisk|find|naiti"),
    ("pagination", r"page|pages|p|stranica|\d+"),
    ("taxonomy", r"tag|tags|category|categories|rubric|rubrika|rubriki|kategorii|kategoriya|author|authors?|archive|"
                 r"arhiv|topics?|temy|tema|label|labels"),
    ("services", r"services?|uslugi|usluga|uslugi-i-ceny|napravleniya|napravlenie|directions|what-we-do|"
                 r"practice-areas?|practices?|treatments?|lechenie|specialties|specialnosti|expertise|capabilities|"
                 r"otrasli-uslug|remont|stroitelstvo|montazh"),
    ("pricing", r"prices?|pricing|ceny|tseny|price-list|prajs|prajs-list|prays|tarify|tariffs?|plans|stoimost|cost"),
    ("cases", r"cases?|case-studies|case-study|keysy|kejsy|kejs|keys|portfolio|portfolios|projects?|proekty|proekt|"
              r"raboty|works?|nashi-raboty|work|success-stories|stories|showcase|realizovannye-proekty|obekty"),
    ("customers", r"customers|clients?|klienty|klientam|clients-list"),
    ("about", r"about|about-us|about-me|o-nas|o-kompanii|company|kompaniya|o-klinike|o-shkole|ob-avtore|history|istoriya|"
              r"mission|missiya|who-we-are|kto-my|o-proekte|o-sebe|bio|biography"),
    ("team", r"team|komanda|people|staff|sotrudniki|specialists?|specialisty|vrachi|vrach|doctors?|experts?|eksperty|"
             r"prepodavateli|teachers|mentors|authors-list|leadership|rukovodstvo|nashi-specialisty|masters?|mastera"),
    ("contacts", r"contacts?|kontakty|kontakt|contact-us|svyaz|adresa|addresses|locations?|offices?|ofisy|filialy|"
                 r"filial|branches|kak-proehat|kak-dobratsya|clinics|kliniki"),
    ("reviews", r"reviews?|otzyvy|otzyv|testimonials|feedback"),
    ("faq", r"faq|faqs|voprosy|vopros-otvet|questions|chastye-voprosy|voprosy-i-otvety"),
    ("help", r"help|pomoshch|support|podderzhka|spravka|knowledge-base|kb|docs|documentation|dokumentaciya|api|"
             r"developers?|reference|manual|guides?"),
    ("careers", r"careers?|jobs|vacancies|vakansii|vakansiya|rabota|karera|join-us|hiring|job"),
    ("news", r"news|novosti|press|press-center|press-tsentr|presscenter|pressroom|press-releases|media|smi|smi-o-nas|"
             r"announcements|obyavleniya|updates|changelog"),
    ("blog", r"blog|blogs|articles?|stati|statya|journal|zhurnal|insights|resources|materials|materialy|knowledge|"
             r"baza-znanij|wiki|learn|library|posts?|publications|publikacii|polezno|poleznoe|sovety|tips|notes|"
             r"meanwhile|writing|essays"),
    ("events", r"events?|meropriyatiya|sobytiya|conferences?|webinars?|vebinary|schedule|raspisanie|talks|doklady|"
               r"speakers|spikery|agenda|venue|tickets|bilety|workshops?|masterklassy"),
    ("courses", r"courses?|kursy|kurs|programs?|programmy|programma|obuchenie|education|training|treningi|school|"
                r"shkola|bootcamps?|classes|lessons|uroki|curriculum|professii|professions|campus|campuses"),
    ("product", r"product|products|features?|platform|funkcii|vozmozhnosti|modules|moduli|tour|how-it-works|"
                r"kak-eto-rabotaet|product-tour|security|bezopasnost|enterprise|releases"),
    ("solutions", r"solutions?|resheniya|reshenie|use-cases?|industries|industry|otrasli|otrasl|for-.+|dlya-.+|"
                  r"segments|teams|by-role|by-industry"),
    ("integrations", r"integrations?|integracii|integraciya|apps|app-directory|marketplace|connectors"),
    ("partners", r"partners?|partnery|partneram|partnerstvo|resellers?|affiliates?|referral|referalnaya-programma"),
    ("promo", r"promo|lp|landing|landings|special|akcii|akciya|aktsii|offers?|spec|specpredlozheniya|sale|skidki"),
    ("shop", r"shop|store|catalog|katalog|magazin|tovary|goods|products-catalog"),
    ("geo", r"moskva|msk|moscow|spb|sankt-peterburg|saint-petersburg|piter|novosibirsk|nsk|ekaterinburg|ekb|kazan|"
            r"nizhniy-novgorod|nizhny-novgorod|chelyabinsk|samara|omsk|rostov-na-donu|rostov|ufa|krasnoyarsk|voronezh|"
            r"perm|volgograd|krasnodar|tyumen|tver|city|cities|goroda|gorod|regions?|regiony|region|oblast|"
            r"cities-.*|locations-.*"),
]
SEG_TYPES_RE = [(t, re.compile(r"^(?:%s)$" % rx, re.I)) for t, rx in SEG_TYPES]

LEGAL_TEXT_RE = re.compile(r"политик|конфиденциальн|персональн|обработк[аи]\s+(?:персональн|данн)|оферт|соглас|"
                           r"пользовательск.{0,5}соглашен|cookie|куки|privacy|terms|legal|imprint|disclaimer|"
                           r"правила|реквизит|раскрыти[ея] информац", re.I)
REQUISITES_RE = re.compile(r"\b(?:ИНН|ОГРН|ОГРНИП|КПП|ОКПО)\b|\bИП\s+[А-ЯЁ]", re.U)
COPYRIGHT_RE = re.compile(r"©|&copy;|\(c\)\s*\d{4}|copyright", re.I)
ADDRESS_RE = re.compile(r"\b(?:г\.|ул\.|улица|проспект|пр-т|пр\.|пер\.|шоссе|наб\.|д\.\s*\d|офис|street|st\.|ave|"
                        r"avenue|suite|floor|road|blvd)\b", re.I)
SOCIAL_HOSTS = ("vk.com", "vk.ru", "vkvideo.ru", "t.me", "telegram.me", "youtube.com", "youtu.be", "rutube.ru",
                "dzen.ru", "zen.yandex.ru", "ok.ru", "instagram.com", "facebook.com", "fb.com", "x.com", "twitter.com",
                "linkedin.com", "github.com", "behance.net", "dribbble.com", "tiktok.com", "pinterest.com",
                "vc.ru", "habr.com", "threads.net", "medium.com", "tenchat.ru")
MESSENGER_RE = re.compile(r"^(?:https?://)?(?:wa\.me|api\.whatsapp\.com|t\.me|telegram\.me|max\.ru|vk\.me|"
                          r"viber\.click|invite\.viber\.com)/", re.I)
LOGIN_TEXT_RE = re.compile(r"^\s*(?:войти|вход|личный кабинет|кабинет|log ?in|sign ?in|my account|аккаунт)\s*$", re.I)
SITEMAP_TEXT_RE = re.compile(r"карта сайта|site ?map", re.I)
RELATED_RE = re.compile(r"читайте также|читать также|похожие|смотрите также|см\. также|другие (?:услуги|статьи|кейсы|"
                        r"проекты|материалы)|вам (?:может|будет) (?:понравит|интерес)|рекомендуем|по теме|"
                        r"related|you (?:may|might) also|see also|more (?:from|like this|articles|posts|stories)|"
                        r"further reading|keep reading", re.I)
LANG_WORD_RE = re.compile(r"^\s*(?:ru|rus|рус|русский|en|eng|english|de|deutsch|fr|français|francais|es|español|"
                          r"espanol|it|italiano|pt|português|zh|中文|简体中文|日本語|ja|한국어|kk|қаз|қазақша|казахский|"
                          r"uk|українська|be|беларуская|uz|o['ʻ]?zbekcha|tr|türkçe|ar|العربية|pl|polski|nl|nederlands)\s*$",
                          re.I)
SEARCH_INPUT_NAMES = {"q", "query", "search", "s", "text", "searchtext", "search_text", "keyword", "keywords", "poisk",
                      "search_query", "term", "k", "searchstring", "find", "ask"}
BLOCK_MARKERS = re.compile(r"<title>\s*(?:Just a moment|Attention Required|DDoS-Guard|Checking your browser|"
                           r"Access denied|Доступ запрещ|Проверка браузера|Вы не робот)|cf-chl-|"
                           r"/cdn-cgi/challenge-platform|__qrator|ddos-guard\.net/js|servicepipe\.ru/|"
                           r"showcaptcha|captcha-page|g-recaptcha-response.{0,200}challenge", re.I)
NOT_FOUND_TEXT_RE = re.compile(r"не найден|не существует|нет такой страницы|страница удалена|ошибка 404|404|"
                               r"not found|page not found|doesn['’]t exist|does not exist|no longer available", re.I)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr",
             "param", "keygen", "command"}
HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
CLASS_HEADER_RE = re.compile(r"(?:^|[\s_-])(?:site-?header|page-?header|header|navbar|top-?menu|topmenu|main-?menu|"
                             r"mainmenu|t-menu|t228|t451|t456|uc-header|js-header)(?:$|[\s_-])", re.I)
CLASS_FOOTER_RE = re.compile(r"(?:^|[\s_-])(?:site-?footer|page-?footer|footer|t-footer|uc-footer|bottom-?menu)"
                             r"(?:$|[\s_-])", re.I)
NEG_HEADER_RE = re.compile(r"(?:card|modal|section|block|table|article|post|entry|widget|panel|accordion|tab|popup|"
                           r"dialog|form|list|item|slider|product|news|page-title|content|sidebar|menu-item|dropdown)"
                           r"[-_]?(?:header|footer)", re.I)
CLASS_CRUMB_RE = re.compile(r"breadcrumb|crumbs|b-crumbs|navigation-chain|nav-chain|kroshki|path-nav", re.I)
ARIA_CRUMB_RE = re.compile(r"breadcrumb|крошк|цепоч|путь|навигационная цепочка|you are here|вы здесь", re.I)
CLASS_MEGA_RE = re.compile(r"mega", re.I)


# ----------------------------------------------------------------------------------------------------------------
# Сеть
# ----------------------------------------------------------------------------------------------------------------

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Resp:
    __slots__ = ("url", "final_url", "status", "headers", "body", "error", "redirects", "elapsed_ms", "requests",
                 "retried")

    def __init__(self, url):
        self.url = url
        self.final_url = url
        self.status = None
        self.headers = {}
        self.body = b""
        self.error = None
        self.redirects = []
        self.elapsed_ms = 0
        self.requests = 0
        self.retried = False

    def text(self):
        return decode_body(self.body, self.headers.get("content-type", ""))

    def to_min(self):
        return {"url": self.url, "final_url": self.final_url, "status": self.status, "error": self.error,
                "redirects": self.redirects, "bytes": len(self.body), "ms": self.elapsed_ms,
                "content_type": self.headers.get("content-type", "")}


def decode_body(body, content_type=""):
    if not body:
        return ""
    cs = None
    m = re.search(r"charset=([\w-]+)", content_type or "", re.I)
    if m:
        cs = m.group(1).lower()
    if not cs:
        m = re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", body[:4096], re.I)
        if m:
            cs = m.group(1).decode("ascii", "ignore").lower()
    for enc in [cs, "utf-8", "cp1251"]:
        if not enc:
            continue
        try:
            return body.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("utf-8", "replace")


class Fetcher:
    """Последовательные запросы с паузой ≥ delay на хост и бюджетом запросов на сайт."""

    def __init__(self, delay=MIN_DELAY, budget=MAX_REQUESTS_DEFAULT, timeout=20, user_agent=USER_AGENT, log=None):
        self.delay = delay
        self.budget = budget
        self.timeout = timeout
        self.ua = user_agent
        self.used = 0
        self.last = {}
        self.log = log if log is not None else []
        ctx = ssl.create_default_context()
        self.opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPSHandler(context=ctx))

    def _wait(self, host):
        d = self.delay
        if host in LOCAL_HOSTS:
            d = 0.0
        last = self.last.get(host)
        if last is not None:
            gap = time.monotonic() - last
            if gap < d:
                time.sleep(d - gap)
        self.last[host] = time.monotonic()

    def get(self, url, max_bytes=MAX_HTML_BYTES, accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            max_redirects=5, retries=1, timeout=None):
        r = self._get(url, max_bytes, accept, max_redirects, timeout)
        while r.error and r.error != "budget-exhausted" and retries > 0 and self.used < self.budget:
            retries -= 1
            time.sleep(5.0 if (urllib.parse.urlsplit(url).hostname or "") not in LOCAL_HOSTS else 0.0)
            r2 = self._get(url, max_bytes, accept, max_redirects, timeout)
            r2.requests += r.requests
            r2.retried = True
            r = r2
        return r

    def _get(self, url, max_bytes, accept, max_redirects, timeout=None):
        r = Resp(url)
        cur = url
        t0 = time.monotonic()
        for hop in range(max_redirects + 1):
            if self.used >= self.budget:
                r.error = "budget-exhausted"
                break
            host = urllib.parse.urlsplit(cur).hostname or ""
            self._wait(host)
            self.used += 1
            r.requests += 1
            req = urllib.request.Request(cur, headers={
                "User-Agent": self.ua, "Accept": accept, "Accept-Language": "ru,en;q=0.8",
                "Accept-Encoding": "gzip"})
            status, headers, body, err = None, {}, b"", None
            try:
                resp = self.opener.open(req, timeout=timeout or self.timeout)
                status = resp.status
                headers = {k.lower(): v for k, v in resp.headers.items()}
                body = resp.read(max_bytes + 1)
            except urllib.error.HTTPError as e:
                status = e.code
                headers = {k.lower(): v for k, v in (e.headers.items() if e.headers else [])}
                try:
                    body = e.read(max_bytes + 1)
                except Exception:
                    body = b""
            except (urllib.error.URLError, socket.timeout, TimeoutError, ssl.SSLError, ConnectionError, OSError) as e:
                err = "%s: %s" % (type(e).__name__, getattr(e, "reason", e))
            except Exception as e:  # noqa: BLE001 — любая ошибка сети фиксируется, прогон продолжается
                err = "%s: %s" % (type(e).__name__, e)
            if len(body) > max_bytes:
                body = body[:max_bytes]
                headers["x-ia-truncated"] = "1"
            if body[:2] == b"\x1f\x8b" or headers.get("content-encoding", "").lower() == "gzip":
                try:
                    body = gzip.GzipFile(fileobj=io.BytesIO(body)).read(max_bytes * 3)
                except Exception:
                    pass
            self.log.append({"url": cur, "status": status, "error": err, "t": round(time.monotonic() - t0, 2)})
            r.status, r.headers, r.body, r.error = status, headers, body, err
            if err:
                break
            if status in (301, 302, 303, 307, 308) and headers.get("location"):
                nxt = urllib.parse.urljoin(cur, headers["location"])
                r.redirects.append({"from": cur, "to": nxt, "status": status})
                cur = nxt
                continue
            break
        r.final_url = cur
        r.elapsed_ms = int((time.monotonic() - t0) * 1000)
        return r


# ----------------------------------------------------------------------------------------------------------------
# robots.txt и sitemap
# ----------------------------------------------------------------------------------------------------------------

def parse_robots(text):
    groups, cur_agents, sitemaps = [], None, []
    star = {"disallow": [], "allow": [], "crawl_delay": None}
    in_star = False
    last_was_agent = False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip().lower(), v.strip()
        if k == "sitemap":
            if v:
                sitemaps.append(v)
            continue
        if k == "user-agent":
            if not last_was_agent:
                cur_agents = []
                groups.append(cur_agents)
                in_star = False
            cur_agents.append(v)
            if v == "*":
                in_star = True
            last_was_agent = True
            continue
        last_was_agent = False
        if in_star:
            if k == "disallow" and v:
                star["disallow"].append(v)
            elif k == "allow" and v:
                star["allow"].append(v)
            elif k == "crawl-delay":
                try:
                    star["crawl_delay"] = float(v)
                except ValueError:
                    pass
    agents = [a for g in groups for a in g]
    return {"groups": len(groups), "agents": agents[:60], "agents_total": len(agents), "sitemaps": sitemaps,
            "star": star}


def local(tag):
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def parse_sitemap_bytes(body):
    """→ (kind, entries) — kind: 'index' | 'urlset' | 'text' | 'error'; entries: [{loc, lastmod, alternates:[(hreflang, href)]}]"""
    if not body:
        return "error", [], "empty"
    head = body[:512].lstrip()
    if not head.startswith(b"<"):
        urls = []
        for line in body.decode("utf-8", "ignore").splitlines():
            line = line.strip()
            if line.startswith("http"):
                urls.append({"loc": line, "lastmod": None, "alternates": []})
        return ("text", urls, None) if urls else ("error", [], "not-xml")
    kind, entries, cur, err = None, [], None, None
    try:
        for ev, el in ET.iterparse(io.BytesIO(body), events=("start", "end")):
            t = local(el.tag)
            if ev == "start":
                if kind is None and t in ("sitemapindex", "urlset"):
                    kind = "index" if t == "sitemapindex" else "urlset"
                if t in ("url", "sitemap"):
                    cur = {"loc": None, "lastmod": None, "alternates": []}
                elif t == "link" and cur is not None:
                    rel = el.attrib.get("rel", "")
                    hl = el.attrib.get("hreflang")
                    if rel == "alternate" and hl:
                        cur["alternates"].append((hl, el.attrib.get("href", "")))
            else:
                ns = el.tag[1:].split("}", 1)[0] if isinstance(el.tag, str) and el.tag.startswith("{") else ""
                sm_ns = (ns == "" or "sitemaps.org" in ns)
                if cur is not None and sm_ns:
                    if t == "loc" and cur["loc"] is None:
                        cur["loc"] = (el.text or "").strip()
                    elif t == "lastmod" and cur["lastmod"] is None:
                        cur["lastmod"] = (el.text or "").strip()
                elif cur is not None and t == "loc":
                    cur["media"] = cur.get("media", 0) + 1
                if t in ("url", "sitemap") and cur is not None:
                    if cur["loc"]:
                        entries.append(cur)
                    cur = None
                    if len(entries) >= MAX_SITEMAP_URLS:
                        err = "truncated-at-%d" % MAX_SITEMAP_URLS
                        break
                el.clear()
    except ET.ParseError as e:
        err = "xml-parse-error: %s" % e
        if not entries:
            return "error", [], err
    return (kind or "urlset"), entries, err


# ----------------------------------------------------------------------------------------------------------------
# Разбор URL
# ----------------------------------------------------------------------------------------------------------------

def registrable(host):
    host = (host or "").lower().split(":")[0]
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in ("com", "co", "org", "net", "spb", "msk") and len(parts[-1]) == 2:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def norm_url(u):
    try:
        p = urllib.parse.urlsplit(u.strip())
    except ValueError:
        return None
    if p.scheme not in ("http", "https") or not p.hostname:
        return None
    path = p.path or "/"
    return urllib.parse.urlunsplit((p.scheme, p.netloc.lower(), path, p.query, ""))


def cmp_key(u):
    """Ключ сравнения URL: без схемы, без www., без хвостового слэша и фрагмента."""
    try:
        p = urllib.parse.urlsplit((u or "").strip())
    except ValueError:
        return None
    if not p.hostname:
        return None
    h = p.netloc.lower()
    h = h[4:] if h.startswith("www.") else h
    path = (p.path or "/").rstrip("/") or "/"
    return h + path + (("?" + p.query) if p.query else "")


def path_segments(path):
    segs = [urllib.parse.unquote(s) for s in path.split("/") if s]
    if segs and re.search(r"\.(?:html?|php|aspx?|jsp)$", segs[-1], re.I):
        segs[-1] = re.sub(r"\.(?:html?|php|aspx?|jsp)$", "", segs[-1], flags=re.I)
    return segs


def seg_type(seg):
    s = seg.lower()
    for t, rx in SEG_TYPES_RE:
        if rx.match(s):
            return t
    return None


def lang_of_segment(seg):
    m = LANG_SEG_RE.match(seg or "")
    if not m:
        return None
    code = m.group(1).lower()
    return code if code in LANG_CODES else None


def analyse_urls(urls, main_host):
    """Статистика URL из sitemap без сетевых запросов."""
    main_reg = registrable(main_host)
    hosts = Counter()
    rows = []
    for u in urls:
        n = norm_url(u)
        if not n:
            continue
        p = urllib.parse.urlsplit(n)
        hosts[p.hostname] += 1
        rows.append((n, p))
    total = len(rows)
    main_rows = [(n, p) for n, p in rows if p.hostname == main_host or p.hostname == "www." + main_host
                 or "www." + p.hostname == main_host]
    first = Counter()
    for n, p in main_rows:
        segs = path_segments(p.path)
        if segs:
            first[segs[0].lower()] += 1
    # языковые префиксы: код языка как первый сегмент у ≥ 3 URL или ≥ 2 %
    lang_prefix = {}
    for seg, c in first.items():
        code = lang_of_segment(seg)
        if code and (c >= 3 or (total and c / total >= 0.02)):
            lang_prefix[seg] = c
    depth_raw, depth_nolang = Counter(), Counter()
    templates = OrderedDict()
    q_count = slash_count = upper_count = underscore_count = ext_count = nonascii_count = files_count = 0
    lengths = []
    for n, p in main_rows:
        segs = path_segments(p.path)
        raw = p.path
        lengths.append(len(n))
        if p.query:
            q_count += 1
        if raw.endswith("/") and raw != "/":
            slash_count += 1
        if re.search(r"[A-Z]", raw):
            upper_count += 1
        if "_" in raw:
            underscore_count += 1
        if re.search(r"\.(?:html?|php|aspx?|jsp)$", raw, re.I):
            ext_count += 1
        if re.search(r"%[89A-F][0-9A-F]", raw, re.I) or re.search(r"[^\x00-\x7f]", raw):
            nonascii_count += 1
        if NON_HTML_EXT_RE.search(raw):
            files_count += 1
        depth_raw[min(len(segs), 6)] += 1
        s2 = segs[1:] if segs and segs[0].lower() in lang_prefix else segs
        depth_nolang[min(len(s2), 6)] += 1
        key, ttype = template_key(s2)
        t = templates.setdefault(key, {"count": 0, "type": ttype, "examples": [], "depth": len(s2)})
        t["count"] += 1
        if len(t["examples"]) < 3:
            t["examples"].append(n)
    main_total = len(main_rows)

    def pct(x):
        return round(100.0 * x / main_total, 1) if main_total else 0.0

    tpl_sorted = sorted(templates.items(), key=lambda kv: -kv[1]["count"])
    type_counts = Counter()
    for k, v in templates.items():
        type_counts[v["type"] or "other"] += v["count"]
    depths_list = []
    for d, c in depth_nolang.items():
        depths_list += [d] * c
    return {
        "total": total,
        "hosts": dict(hosts.most_common(12)),
        "main_host_share": round(100.0 * main_total / total, 1) if total else 0.0,
        "main_total": main_total,
        "lang_prefixes": lang_prefix,
        "depth_raw": {str(k): v for k, v in sorted(depth_raw.items())},
        "depth": {str(k): v for k, v in sorted(depth_nolang.items())},
        "depth_median": statistics.median(depths_list) if depths_list else None,
        "depth_p90": sorted(depths_list)[int(0.9 * (len(depths_list) - 1))] if depths_list else None,
        "depth_max": max(depths_list) if depths_list else None,
        "top_first_segments": dict(first.most_common(25)),
        "templates_total": len(templates),
        "templates": [{"pattern": k, **v} for k, v in tpl_sorted[:40]],
        "type_counts": dict(type_counts.most_common()),
        "url_hygiene": {"query_pct": pct(q_count), "trailing_slash_pct": pct(slash_count), "uppercase_pct": pct(upper_count),
                        "underscore_pct": pct(underscore_count), "file_ext_pct": pct(ext_count),
                        "non_ascii_pct": pct(nonascii_count), "files_pct": pct(files_count),
                        "len_median": statistics.median(lengths) if lengths else None,
                        "len_max": max(lengths) if lengths else None},
    }


def template_key(segs):
    """Шаблон пути: литерал первого (и второго, если первый — город) сегмента + число слагов после него."""
    if not segs:
        return "/", "home"
    t0 = seg_type(segs[0])
    if len(segs) == 1:
        return "/{page}", ("root:" + t0) if t0 else "root-page"
    head = [segs[0].lower()]
    rest = segs[1:]
    ttype = t0
    if t0 == "geo" and rest:
        t1 = seg_type(rest[0])
        head.append(rest[0].lower() if t1 else "{slug}")
        ttype = "geo/" + (t1 or "page")
        rest = rest[1:]
    key = "/" + "/".join(head) + "".join("/{slug}" for _ in rest)
    return key, ttype


# ----------------------------------------------------------------------------------------------------------------
# Разбор HTML
# ----------------------------------------------------------------------------------------------------------------

class PageParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base = base_url
        self.stack = []          # [tag, attrs, uid, flags]
        self.uid = 0
        self.lang = None
        self.title = ""
        self.in_title = False
        self.meta_robots = None
        self.canonical = None
        self.hreflang = []
        self.jsonld_raw = []
        self.in_jsonld = False
        self.jsonld_buf = []
        self.itemtypes = []
        self.rdfa_types = []
        self.links = []
        self.cur_link = None
        self.forms = []
        self.cur_form = None
        self.inputs = []
        self.selects = []
        self.headings = []
        self.cur_heading = None
        self.text_by_region = defaultdict(list)
        self.skip_text = 0
        self.header_found = None     # способ: header-tag | role-banner | class | nav
        self.region_uids = {"header": None, "footer": None}
        self.footer_candidates = []
        self.header_candidates = []
        self.crumb_uids = set()
        self.mega_class = False
        self.aria_expanded = 0
        self.words = 0
        self.h1_seen = False
        self.cur_button = None
        self.header_semantic_issue = False

    # --- регионы
    def flags(self):
        return self.stack[-1][3] if self.stack else {}

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()
        if tag == "li" and self.stack and self.stack[-1][0] == "li":
            self._pop_to("li")
        if tag == "p" and self.stack and self.stack[-1][0] == "p":
            self._pop_to("p")
        parent = dict(self.flags())
        self.uid += 1
        uid = self.uid
        f = parent
        role = a.get("role", "").lower()
        cls = (a.get("class", "") + " " + a.get("id", "")).strip()
        aria_label = a.get("aria-label", "") + " " + a.get("aria-labelledby", "")
        if tag == "html":
            self.lang = a.get("lang") or self.lang
        if tag in ("header",) or role == "banner":
            if not f.get("article") and not f.get("footer"):
                self.header_candidates.append((uid, "header-tag" if tag == "header" else "role-banner"))
                f["header_any"] = uid
        elif cls and CLASS_HEADER_RE.search(cls) and not NEG_HEADER_RE.search(cls) and not f.get("header_any") \
                and not f.get("footer_any") and not f.get("main") and not f.get("article") \
                and tag in ("div", "section", "nav", "ul") and not self.h1_seen:
            self.header_candidates.append((uid, "class"))
            f["header_any"] = uid
        if tag == "footer" or role == "contentinfo":
            if not f.get("article"):
                self.footer_candidates.append((uid, "footer-tag" if tag == "footer" else "role-contentinfo"))
                f["footer_any"] = uid
        elif cls and CLASS_FOOTER_RE.search(cls) and not NEG_HEADER_RE.search(cls) and not f.get("footer_any") \
                and not f.get("header_any") and not f.get("article") and tag in ("div", "section", "ul"):
            self.footer_candidates.append((uid, "class"))
            f["footer_any"] = uid
        if tag == "nav" or role == "navigation":
            f["nav"] = uid
            if not f.get("nav_top"):
                f["nav_top"] = uid
        if tag == "main" or role == "main":
            f["main"] = True
        if tag == "article":
            f["article"] = True
        if tag in ("ul", "ol", "menu"):
            f["list_depth"] = f.get("list_depth", 0) + 1
            f["list_chain"] = tuple(f.get("list_chain", ())) + (uid,)
        if tag == "li":
            f["li_chain"] = tuple(f.get("li_chain", ())) + ((f.get("list_depth", 0), uid),)
        is_crumb = False
        if ARIA_CRUMB_RE.search(aria_label) and (tag in ("nav", "ol", "ul", "div") or role == "navigation"):
            is_crumb = True
        if cls and CLASS_CRUMB_RE.search(cls):
            is_crumb = True
        it = a.get("itemtype", "")
        if it:
            self.itemtypes.append(it.rsplit("/", 1)[-1])
            if it.lower().endswith("breadcrumblist"):
                is_crumb = True
        if a.get("typeof"):
            self.rdfa_types += a["typeof"].split()
            if "breadcrumblist" in a["typeof"].lower():
                is_crumb = True
        if is_crumb and not f.get("crumb"):
            f["crumb"] = uid
            self.crumb_uids.add(uid)
        if cls and CLASS_MEGA_RE.search(cls) and (f.get("header_any") or f.get("nav")):
            self.mega_class = True
        if a.get("aria-expanded") is not None and (f.get("header_any") or f.get("nav")):
            self.aria_expanded += 1
        if tag in ("script", "style", "noscript", "template", "svg"):
            if tag == "script" and a.get("type", "").lower() == "application/ld+json":
                self.in_jsonld = True
                self.jsonld_buf = []
            self.skip_text += 1
        if tag == "title" and not f.get("svg"):
            self.in_title = True
        if tag == "meta":
            name = a.get("name", "").lower()
            if name == "robots":
                self.meta_robots = a.get("content", "")
        if tag == "link":
            rel = a.get("rel", "").lower().split()
            if "canonical" in rel:
                self.canonical = urllib.parse.urljoin(self.base, a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append((a.get("hreflang"), urllib.parse.urljoin(self.base, a.get("href", ""))))
        if tag in HEADING_TAGS:
            self.cur_heading = {"tag": tag, "text": [], "region": self._region(f)}
            if tag == "h1":
                self.h1_seen = True
        if tag == "a":
            href = a.get("href", "")
            self.cur_link = {"href": href, "text": [], "rel": a.get("rel", ""), "hreflang": a.get("hreflang"),
                             "cls": a.get("class", ""), "aria": a.get("aria-label", ""), "title": a.get("title", ""),
                             "region": self._region(f), "crumb": bool(f.get("crumb")), "nav": bool(f.get("nav")),
                             "list_depth": f.get("list_depth", 0), "li_chain": f.get("li_chain", ()),
                             "list_chain": f.get("list_chain", ()), "main": bool(f.get("main")),
                             "article": bool(f.get("article")), "header_uid": f.get("header_any"),
                             "footer_uid": f.get("footer_any"), "nav_uid": f.get("nav")}
        if tag == "form":
            self.cur_form = {"action": a.get("action", ""), "role": role, "cls": cls, "region": self._region(f),
                             "inputs": []}
            self.forms.append(self.cur_form)
        if tag == "input":
            inp = {"type": a.get("type", "text").lower(), "name": a.get("name", "").lower(),
                   "placeholder": a.get("placeholder", ""), "aria": a.get("aria-label", ""), "region": self._region(f)}
            self.inputs.append(inp)
            if self.cur_form is not None:
                self.cur_form["inputs"].append(inp)
        if tag == "select":
            self.selects.append({"name": (a.get("name", "") + " " + a.get("id", "") + " " + cls).lower(),
                                 "region": self._region(f)})
        if tag == "button" and (f.get("header_any") or f.get("nav")):
            self.cur_button = {"href": "", "text": [], "button": True, "cls": a.get("class", ""),
                               "region": self._region(f), "crumb": False, "nav": bool(f.get("nav")),
                               "list_depth": f.get("list_depth", 0), "li_chain": f.get("li_chain", ()),
                               "list_chain": f.get("list_chain", ()), "main": False, "article": False,
                               "aria": a.get("aria-label", ""), "rel": "", "hreflang": None, "title": a.get("title", ""),
                               "header_uid": f.get("header_any"), "footer_uid": f.get("footer_any"),
                               "nav_uid": f.get("nav")}
        if tag in VOID_TAGS:
            return
        self.stack.append([tag, a, uid, f])

    def _region(self, f):
        if f.get("crumb"):
            return "crumb"
        if f.get("header_any"):
            return "header"
        if f.get("footer_any"):
            return "footer"
        if f.get("nav") and not f.get("main") and not f.get("article"):
            return "nav"
        if f.get("main") or f.get("article"):
            return "main"
        return "body"

    def _pop_to(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                popped = self.stack[i:]
                del self.stack[i:]
                for p in popped:
                    self._on_close(p)
                return True
        return False

    def _on_close(self, item):
        tag = item[0]
        if tag in ("script", "style", "noscript", "template", "svg"):
            self.skip_text = max(0, self.skip_text - 1)
            if tag == "script" and self.in_jsonld:
                self.jsonld_raw.append("".join(self.jsonld_buf))
                self.in_jsonld = False
        if tag == "title":
            self.in_title = False
        if tag == "a" and self.cur_link is not None:
            self.cur_link["text"] = " ".join(" ".join(self.cur_link["text"]).split())
            self.links.append(self.cur_link)
            self.cur_link = None
        if tag in HEADING_TAGS and self.cur_heading is not None:
            self.cur_heading["text"] = " ".join(" ".join(self.cur_heading["text"]).split())
            self.headings.append(self.cur_heading)
            self.cur_heading = None
        if tag == "form":
            self.cur_form = None
        if tag == "button" and self.cur_button is not None:
            b = self.cur_button
            b["text"] = " ".join((" ".join(b["text"]) + " " + b.get("aria", "")).split())
            self.links.append(b)
            self.cur_button = None

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID_TAGS:
            return
        self._pop_to(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data):
        if self.in_jsonld:
            self.jsonld_buf.append(data)
            return
        if self.skip_text:
            return
        if self.in_title:
            self.title += data
        if self.cur_link is not None:
            self.cur_link["text"].append(data)
        if self.cur_button is not None:
            self.cur_button["text"].append(data)
        if self.cur_heading is not None:
            self.cur_heading["text"].append(data)
        f = self.flags()
        reg = self._region(f)
        t = data.strip()
        if t:
            self.text_by_region[reg].append(t)
            self.words += len(t.split())

    def close(self):
        super().close()
        while self.stack:
            self._on_close(self.stack.pop())
        if self.cur_link is not None:
            self.cur_link["text"] = " ".join(" ".join(self.cur_link["text"]).split())
            self.links.append(self.cur_link)
            self.cur_link = None


def jsonld_types(raw_list):
    types, crumbs, search_action, errors = Counter(), [], False, 0

    def walk(o):
        nonlocal search_action
        if isinstance(o, dict):
            t = o.get("@type")
            tl = t if isinstance(t, list) else [t]
            for x in tl:
                if isinstance(x, str):
                    types[x] += 1
                    if x == "BreadcrumbList":
                        items = o.get("itemListElement") or []
                        crumbs.append(len(items) if isinstance(items, list) else 1)
            pa = o.get("potentialAction")
            for p in (pa if isinstance(pa, list) else [pa]):
                if isinstance(p, dict) and "SearchAction" in str(p.get("@type", "")):
                    search_action = True
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for raw in raw_list:
        s = raw.strip()
        s = re.sub(r"^\s*<!\[CDATA\[|\]\]>\s*$", "", s)
        s = re.sub(r"^\s*<!--|-->\s*$", "", s)
        try:
            walk(json.loads(s))
        except Exception:
            errors += 1
    return dict(types), crumbs, search_action, errors


def same_site(u, host):
    h = (urllib.parse.urlsplit(u).hostname or "").lower()
    return h == host or registrable(h) == registrable(host)


def analyse_page(resp, site_host):
    text = resp.text()
    p = PageParser(resp.final_url)
    try:
        p.feed(text)
        p.close()
    except Exception as e:  # noqa: BLE001
        return {"url": resp.final_url, "error": "parse: %s" % e}
    out = {"url": resp.url, "final_url": resp.final_url, "status": resp.status, "lang": p.lang,
           "title": " ".join(p.title.split())[:160], "meta_robots": p.meta_robots, "canonical": p.canonical,
           "hreflang": p.hreflang[:60], "words": p.words}
    types, crumbs_ld, search_action, ld_err = jsonld_types(p.jsonld_raw)
    out["jsonld_types"] = types
    out["jsonld_errors"] = ld_err
    out["microdata_types"] = dict(Counter(p.itemtypes).most_common(15))
    out["rdfa_types"] = dict(Counter(p.rdfa_types).most_common(10))
    out["breadcrumb_ld_items"] = crumbs_ld
    out["website_search_action"] = search_action
    out["h1"] = [h["text"][:120] for h in p.headings if h["tag"] == "h1"][:3]
    out["h1_count"] = sum(1 for h in p.headings if h["tag"] == "h1")
    out["h2_count"] = sum(1 for h in p.headings if h["tag"] == "h2")
    # абсолютные ссылки
    for ln in p.links:
        href = (ln.get("href") or "").strip()
        ln["abs"] = urllib.parse.urldefrag(urllib.parse.urljoin(resp.final_url, href))[0] \
            if href and not href.startswith(("javascript:", "#")) else ("#" if href.startswith("#") else "")
        ln["kind"] = link_kind(ln["abs"], href, site_host)
    # шапка: выбрать кандидата (первый header-tag или role-banner; иначе class; иначе первый nav вне footer)
    header_uid, header_method = pick_header(p)
    footer_uid, footer_method = pick_footer(p)
    hl = [ln for ln in p.links if header_uid and ln.get("header_uid") == header_uid]
    if header_method == "first-nav":
        hl = [ln for ln in p.links if ln.get("nav_uid") == header_uid]
    fl = [ln for ln in p.links if footer_uid and ln.get("footer_uid") == footer_uid]
    out["header"] = header_metrics(hl, p, header_method, site_host, resp.final_url)
    out["header"]["semantic_issue"] = p.header_semantic_issue
    out["nav_elements"] = len({ln.get("nav_uid") for ln in p.links if ln.get("nav_uid")})
    out["footer"] = footer_metrics(fl, p, footer_method, site_host)
    crumb_links = [ln for ln in p.links if ln.get("crumb")]
    out["breadcrumbs"] = {"html": bool(p.crumb_uids), "html_links": len(crumb_links),
                          "html_texts": [ln["text"][:40] for ln in crumb_links[:8]],
                          "ld_items": crumbs_ld[:3], "microdata": "BreadcrumbList" in p.itemtypes,
                          "rdfa": any("breadcrumblist" in t.lower() for t in p.rdfa_types)}
    body_links = [ln for ln in p.links if ln.get("region") in ("main", "body") and not ln.get("button")]
    internal_body = [ln for ln in body_links if ln["kind"] == "internal"]
    rel_heads = [h["text"][:60] for h in p.headings if RELATED_RE.search(h["text"] or "")]
    out["content_links"] = {"internal": len(internal_body),
                            "internal_unique": len({ln["abs"] for ln in internal_body}),
                            "in_main_or_article": sum(1 for ln in internal_body if ln.get("main") or ln.get("article")),
                            "related_block_headings": rel_heads[:5]}
    all_internal = [ln["abs"] for ln in p.links if ln.get("kind") == "internal"]
    out["internal_links_total"] = len(all_internal)
    out["internal_links_unique"] = sorted(set(all_internal))[:2000]
    out["search"] = search_presence(p)
    out["lang_switch"] = lang_switch(p, resp.final_url)
    marker = bool(BLOCK_MARKERS.search(text[:30000]))
    out["blocked"] = (marker and p.words < 400 and len(p.links) < 15) or (
        resp.status in (403, 429, 503) and p.words < 200)
    return out


def link_kind(abs_url, href, site_host):
    h = (href or "").strip().lower()
    if h.startswith("tel:"):
        return "tel"
    if h.startswith("mailto:"):
        return "mailto"
    if h.startswith("#") or abs_url == "#":
        return "anchor"
    if not abs_url:
        return "none"
    if MESSENGER_RE.match(abs_url.split("://", 1)[-1]) or MESSENGER_RE.match(abs_url):
        return "messenger"
    host = (urllib.parse.urlsplit(abs_url).hostname or "").lower()
    if any(host == s or host.endswith("." + s) for s in SOCIAL_HOSTS):
        return "social"
    if same_site(abs_url, site_host):
        return "internal"
    return "external"


def pick_header(p):
    """Шапка: первый <header>/role=banner с ≥ 2 внутренними ссылками; иначе класс; иначе самый «ссылочный» <nav> до
    основного содержимого. Если <header> есть, но пустой, а меню в <nav> снаружи — отметка semantic_issue."""
    cnt = Counter(ln.get("header_uid") for ln in p.links if ln.get("kind") == "internal" and not ln.get("button"))
    ncnt = Counter(ln.get("nav_uid") for ln in p.links if ln.get("kind") == "internal" and not ln.get("button")
                   and not ln.get("footer_uid"))
    tag_cands = [(u, m) for u, m in p.header_candidates if m in ("header-tag", "role-banner")]
    for uid, method in tag_cands:
        if cnt.get(uid, 0) >= 2:
            return uid, method
    for uid, method in p.header_candidates:
        if method == "class" and cnt.get(uid, 0) >= 2:
            p.header_semantic_issue = bool(tag_cands)
            return uid, "class"
    navs = [u for u, c in ncnt.most_common() if u and c >= 2]
    if navs:
        p.header_semantic_issue = bool(tag_cands)
        return navs[0], "first-nav"
    if tag_cands:
        return tag_cands[0]
    return None, "none"


def pick_footer(p):
    tags = [(u, m) for u, m in p.footer_candidates if m in ("footer-tag", "role-contentinfo")]
    if tags:
        return tags[-1]
    cls = [(u, m) for u, m in p.footer_candidates if m == "class"]
    if cls:
        return cls[-1]
    return None, "none"


def header_metrics(hl, p, method, site_host, page_url):
    links = [ln for ln in hl if not ln.get("button")]
    buttons = [ln for ln in hl if ln.get("button")]
    internal = [ln for ln in links if ln["kind"] == "internal"]
    in_lists = [ln for ln in internal if ln.get("list_depth", 0) > 0]
    top, sub, top_items = [], [], []
    mega_like = False
    max_sub = 0
    groups_max = 0
    if in_lists:
        def is_root(ln):
            pth = urllib.parse.urlsplit(ln["abs"]).path or "/"
            return pth == "/" or bool(re.match(r"^/[a-z]{2}(?:-[a-z]{2})?/?$", pth))
        by_depth = defaultdict(set)
        for ln in in_lists:
            if not is_root(ln):
                by_depth[ln["list_depth"]].add(ln["abs"])
        cand = sorted(d for d, st in by_depth.items() if len(st) >= 2)
        min_d = cand[0] if cand else min(ln["list_depth"] for ln in in_lists)
        in_lists = [ln for ln in in_lists if ln["list_depth"] >= min_d]
        top = [ln for ln in in_lists if ln["list_depth"] == min_d]
        sub = [ln for ln in in_lists if ln["list_depth"] > min_d]
        by_top = defaultdict(list)
        for ln in sub:
            anc = [uid for d, uid in ln.get("li_chain", ()) if d == min_d]
            by_top[anc[0] if anc else None].append(ln)
        for k, lst in by_top.items():
            uniq = {ln["abs"] for ln in lst}
            groups = {ln["list_chain"][min_d] if len(ln.get("list_chain", ())) > min_d else None for ln in lst}
            max_sub = max(max_sub, len(uniq))
            groups_max = max(groups_max, len(groups))
            if len(uniq) >= 10 and len(groups) >= 2:
                mega_like = True
        seen = set()
        for ln in top:
            key = (ln["abs"], ln["text"].lower())
            if key in seen:
                continue
            seen.add(key)
            top_items.append(ln["text"][:40] or ln.get("aria", "")[:40] or ln["abs"][-40:])
    else:
        seen = set()
        for ln in internal:
            key = (ln["abs"], ln["text"].lower())
            if key in seen or not ln["text"]:
                continue
            seen.add(key)
            top_items.append(ln["text"][:40])
    # логотип: первая внутренняя ссылка на корень
    root_links = [ln for ln in internal if urllib.parse.urlsplit(ln["abs"]).path in ("", "/") or
                  re.match(r"^/[a-z]{2}(?:-[a-z]{2})?/?$", urllib.parse.urlsplit(ln["abs"]).path or "")]
    home_text = any(re.match(r"^\s*(?:главная|home|на главную)\s*$", ln["text"] or "", re.I) for ln in links)
    cta = [ln["text"][:40] for ln in links if re.search(r"btn|button|cta|_btn|-btn", ln.get("cls", ""), re.I)
           and ln["text"]]
    return {
        "method": method,
        "links": len(links),
        "internal_unique": len({ln["abs"] for ln in internal}),
        "top_items": top_items[:30],
        "top_count": len(top_items),
        "sub_links": len({ln["abs"] for ln in sub}),
        "max_sub_per_item": max_sub,
        "sub_groups_max": groups_max,
        "dropdown": bool(sub),
        "mega": mega_like or (p.mega_class and len({ln["abs"] for ln in sub}) >= 8),
        "mega_class": p.mega_class,
        "aria_expanded": p.aria_expanded,
        "logo_to_home": bool(root_links),
        "home_text_link": home_text,
        "phone": any(ln["kind"] == "tel" for ln in links),
        "email": any(ln["kind"] == "mailto" for ln in links),
        "messenger": any(ln["kind"] == "messenger" for ln in links),
        "login": any(LOGIN_TEXT_RE.match(ln["text"] or "") for ln in links + buttons),
        "cta_texts": cta[:5],
        "buttons": len(buttons),
    }


def footer_metrics(fl, p, method, site_host):
    links = [ln for ln in fl if not ln.get("button")]
    internal = [ln for ln in links if ln["kind"] == "internal"]
    lists = Counter()
    for ln in internal:
        ch = ln.get("list_chain", ())
        if ch:
            lists[ch[-1]] += 1
    groups = sum(1 for c in lists.values() if c >= 2)
    heads = [h for h in p.headings if h["region"] == "footer"]
    text = " ".join(p.text_by_region.get("footer", []))
    legal = [ln["text"][:50] for ln in links if LEGAL_TEXT_RE.search((ln["text"] or "") + " " + (ln["abs"] or ""))]
    return {
        "method": method,
        "links": len(links),
        "internal_unique": len({ln["abs"] for ln in internal}),
        "groups_lists": max(groups, len([h for h in heads if len((h["text"] or "").split()) <= 5])),
        "headings": [h["text"][:40] for h in heads][:12],
        "legal_links": legal[:8],
        "requisites": bool(REQUISITES_RE.search(text)),
        "copyright": bool(COPYRIGHT_RE.search(text)),
        "address_hint": bool(ADDRESS_RE.search(text)),
        "phone": any(ln["kind"] == "tel" for ln in links),
        "email": any(ln["kind"] == "mailto" for ln in links),
        "messenger": any(ln["kind"] == "messenger" for ln in links),
        "social": len({(urllib.parse.urlsplit(ln["abs"]).hostname or "") for ln in links if ln["kind"] == "social"}),
        "html_sitemap_link": any(SITEMAP_TEXT_RE.search(ln["text"] or "") for ln in links),
        "words": len(text.split()),
    }


def search_presence(p):
    by_region = Counter()
    for f in p.forms:
        act = (f.get("action") or "").lower()
        names = {i["name"] for i in f["inputs"]}
        types = {i["type"] for i in f["inputs"]}
        if f.get("role") == "search" or "search" in types or (names & SEARCH_INPUT_NAMES and
                                                              not ({"email", "tel", "phone"} & names)) \
                or re.search(r"search|poisk|/find", act):
            by_region[f["region"]] += 1
    for i in p.inputs:
        if i["type"] == "search" or re.search(r"поиск|search|найти", (i["placeholder"] + " " + i["aria"]), re.I):
            by_region[i["region"] + ":input"] += 1
    btn = any(ln.get("button") and re.search(r"поиск|search|найти", str(ln.get("text") or "") + " " +
                                             str(ln.get("aria") or ""), re.I) for ln in p.links)
    link = any(re.search(r"/(?:search|poisk)(?:/|$|\?)", urllib.parse.urlsplit(ln.get("abs") or "").path + "/")
               for ln in p.links if ln.get("kind") == "internal")
    return {"forms_or_inputs": dict(by_region), "any": bool(by_region) or btn or link, "button_only": btn and not by_region,
            "link_to_search_page": link}


def lang_switch(p, page_url):
    found = []
    for ln in p.links:
        if ln.get("region") not in ("header", "footer", "nav", "body"):
            continue
        t = ln.get("text") or ""
        if ln.get("hreflang") or (LANG_WORD_RE.match(t) and ln.get("kind") in ("internal", "external")):
            found.append({"text": t[:20], "href": ln.get("abs"), "region": ln.get("region"),
                          "hreflang": ln.get("hreflang")})
    sel = [s for s in p.selects if re.search(r"lang|язык|locale|country", s["name"])]
    same_page = None
    if found:
        cur = urllib.parse.urlsplit(page_url).path.strip("/").split("/")
        sp = 0
        for f in found:
            if not f["href"]:
                continue
            tp = urllib.parse.urlsplit(f["href"]).path.strip("/").split("/")
            if len(tp) >= 2 and len(cur) >= 1 and (tp[1:] == cur or tp[1:] == cur[1:]):
                sp += 1
        same_page = sp
    return {"links": found[:8], "count": len(found), "select": bool(sel), "same_page_links": same_page}


# ----------------------------------------------------------------------------------------------------------------
# Сайт целиком
# ----------------------------------------------------------------------------------------------------------------

NON_HTML_EXT_RE = re.compile(r"\.(?:png|jpe?g|gif|webp|avif|svg|ico|pdf|docx?|xlsx?|pptx?|zip|rar|7z|xml|txt|json|"
                             r"csv|mp4|webm|mov|mp3|wav|woff2?|ttf|otf|css|js)$", re.I)


def pick_sample(url_stats_rows, main_host, n):
    """Выбор страниц для загрузки: по одной из крупнейших шаблонов, потом вторые, плюс самая глубокая."""
    by_tpl = defaultdict(list)
    for u in url_stats_rows:
        nu = norm_url(u)
        if not nu or NON_HTML_EXT_RE.search(urllib.parse.urlsplit(nu).path):
            continue
        pp = urllib.parse.urlsplit(nu)
        if pp.hostname not in (main_host, "www." + main_host) and "www." + (pp.hostname or "") != main_host:
            continue
        segs = path_segments(pp.path)
        if segs and lang_of_segment(segs[0]):
            segs2 = segs[1:]
        else:
            segs2 = segs
        if not segs2:
            continue
        key, _ = template_key(segs2)
        by_tpl[key].append(nu)
    order = sorted(by_tpl.items(), key=lambda kv: -len(kv[1]))
    chosen = []
    for rnd in range(3):
        for key, lst in order:
            if len(chosen) >= n:
                break
            lst_sorted = sorted(lst)
            if rnd < len(lst_sorted):
                idx = (len(lst_sorted) // 2 + rnd * 7) % len(lst_sorted)
                u = lst_sorted[idx]
                if u not in chosen:
                    chosen.append(u)
        if len(chosen) >= n:
            break
    deepest = sorted((u for lst in by_tpl.values() for u in lst),
                     key=lambda u: (-len(path_segments(urllib.parse.urlsplit(u).path)), u))
    if deepest and deepest[0] not in chosen:
        if len(chosen) >= n and chosen:
            chosen[-1] = deepest[0]
        else:
            chosen.append(deepest[0])
    return chosen


def probe_site(url, out_dir, site_id=None, sample=14, delay=MIN_DELAY, budget=MAX_REQUESTS_DEFAULT,
               max_sitemaps=12, timeout=20, meta=None, save_html=True):
    started = time.strftime("%Y-%m-%d %H:%M:%S")
    parts = urllib.parse.urlsplit(url if "://" in url else "https://" + url)
    origin = "%s://%s" % (parts.scheme, parts.netloc)
    host = (parts.hostname or "").lower()
    site_id = site_id or re.sub(r"[^a-z0-9.-]", "-", host)
    delay = max(MIN_DELAY, delay) if host not in LOCAL_HOSTS else delay
    log = []
    fx = Fetcher(delay=delay, budget=budget, timeout=timeout, log=log)
    res = OrderedDict()
    res["tool"] = "ia_probe %s" % VERSION
    res["id"] = site_id
    res["input_url"] = url
    res["origin"] = origin
    res["started"] = started
    res["meta"] = meta or {}
    res["politeness"] = {"delay_s": delay, "budget": budget, "user_agent": USER_AGENT}
    # 1. robots.txt
    rr = fx.get(origin + "/robots.txt", max_bytes=512 * 1024, accept="text/plain,*/*;q=0.5")
    robots = {"status": rr.status, "error": rr.error, "final_url": rr.final_url, "redirects": rr.redirects}
    rp = urllib.robotparser.RobotFileParser()
    robots_text = rr.text() if rr.status and 200 <= rr.status < 300 else ""
    allow_pages = True
    crawl_delay = None
    if rr.status and 200 <= rr.status < 300:
        robots.update(parse_robots(robots_text))
        rp.parse(robots_text.splitlines())
        try:
            crawl_delay = rp.crawl_delay(UA_TOKEN) or rp.crawl_delay("*")
        except Exception:
            crawl_delay = None
    elif rr.status and 400 <= rr.status < 500:
        robots["note"] = "4xx — ограничений нет (RFC 9309 §2.3.1.3)"
        rp.parse([])
    else:
        robots["note"] = "robots.txt недоступен (5xx/ошибка) — страницы не запрашиваются (RFC 9309 §2.3.1.4)"
        allow_pages = False
    if crawl_delay:
        robots["crawl_delay_applied"] = min(float(crawl_delay), 10.0)
        fx.delay = max(fx.delay, robots["crawl_delay_applied"])
    res["robots"] = robots
    # 2. sitemap
    sm_urls = list(dict.fromkeys(robots.get("sitemaps", [])))
    guessed = False
    if not sm_urls:
        sm_urls = [origin + "/sitemap.xml", origin + "/sitemap_index.xml"]
        guessed = True
    files, all_entries, index_children_total = [], [], 0
    queue = list(sm_urls)
    fetched = 0
    seen_sm = set()
    while queue and fetched < max_sitemaps:
        su = queue.pop(0)
        if su in seen_sm:
            continue
        seen_sm.add(su)
        r = fx.get(su, max_bytes=MAX_SITEMAP_BYTES, accept="application/xml,text/xml,*/*;q=0.5")
        fetched += 1
        kind, entries, err = parse_sitemap_bytes(r.body if r.status and 200 <= r.status < 300 else b"")
        files.append({"url": su, "status": r.status, "kind": kind, "entries": len(entries), "error": err or r.error,
                      "redirects": len(r.redirects)})
        if kind == "index":
            children = [e["loc"] for e in entries]
            index_children_total += len(children)
            if len(children) > max_sitemaps:
                step = max(1, len(children) // max_sitemaps)
                children = children[::step]
            queue.extend(children)
        elif kind in ("urlset", "text"):
            all_entries.extend(entries)
            if guessed:
                queue = [q for q in queue if q not in (origin + "/sitemap_index.xml",)]
    sitemap = {"declared_in_robots": bool(robots.get("sitemaps")), "guessed": guessed, "files": files,
               "files_fetched": fetched, "index_children_total": index_children_total,
               "partial": bool(queue) or (index_children_total > max_sitemaps),
               "urls": len(all_entries),
               "lastmod_pct": round(100.0 * sum(1 for e in all_entries if e["lastmod"]) / len(all_entries), 1)
               if all_entries else 0.0,
               "hreflang_urls": sum(1 for e in all_entries if e["alternates"]),
               "hreflang_langs": sorted({hl for e in all_entries for hl, _ in e["alternates"]})[:40]}
    res["sitemap"] = sitemap
    rel = [e for e in all_entries if not re.match(r"^https?://", e["loc"] or "", re.I)]
    for e in rel:
        e["loc"] = urllib.parse.urljoin(origin + "/", e["loc"])
    sitemap["relative_locs"] = len(rel)
    urls = [e["loc"] for e in all_entries]
    main_host = host
    if urls:
        hc = Counter((urllib.parse.urlsplit(u).hostname or "").lower() for u in urls)
        top_host = hc.most_common(1)[0][0]
        if top_host and registrable(top_host) == registrable(host):
            main_host = top_host
    res["main_host"] = main_host
    res["urls"] = analyse_urls(urls, main_host) if urls else {"total": 0}
    url_set = {cmp_key(u) for u in urls}
    url_set.discard(None)
    os.makedirs(os.path.join(out_dir, site_id), exist_ok=True)
    with open(os.path.join(out_dir, site_id, "sitemap_urls.txt.gz"), "wb") as fh:
        fh.write(gzip.compress("\n".join(urls).encode("utf-8")))
    # 3. страницы
    pages = []
    blocked = False
    if allow_pages:
        home = origin + "/"
        cand = [home] + [u for u in pick_sample(urls, main_host, sample) if u.rstrip("/") != home.rstrip("/")]
        for u in cand:
            if fx.used >= fx.budget - 2:
                break
            try:
                ok = rp.can_fetch(UA_TOKEN, u)
            except Exception:
                ok = True
            if not ok:
                pages.append({"url": u, "skipped": "robots.txt disallow"})
                continue
            r = fx.get(u)
            if r.error or not r.status:
                pages.append({"url": u, "error": r.error, "status": r.status})
                continue
            ctype = r.headers.get("content-type", "")
            if "html" not in ctype and not r.body[:200].lstrip().lower().startswith((b"<!doctype html", b"<html")):
                pages.append({"url": u, "status": r.status, "skipped": "not-html " + ctype})
                continue
            pa = analyse_page(r, main_host)
            if save_html:
                pdir = os.path.join(out_dir, site_id, "pages")
                os.makedirs(pdir, exist_ok=True)
                fn = "%02d.html.gz" % len(pages)
                with open(os.path.join(pdir, fn), "wb") as fh:
                    fh.write(gzip.compress(r.body))
                pa["html_file"] = "pages/" + fn
                pa["content_type"] = r.headers.get("content-type", "")
            pa["redirects"] = r.redirects
            pa["in_sitemap"] = cmp_key(u) in url_set
            pa["url_depth"] = len(path_segments(urllib.parse.urlsplit(r.final_url).path))
            pages.append(pa)
            if pa.get("blocked"):
                blocked = True
                break
    res["pages"] = pages
    res["blocked"] = blocked
    # 4. проба 404
    nf = {}
    if allow_pages and not blocked and fx.used < fx.budget:
        token = hashlib.sha1((host + started).encode()).hexdigest()[:10]
        bogus = origin + "/ia-probe-%s-nonexistent" % token
        try:
            ok = rp.can_fetch(UA_TOKEN, bogus)
        except Exception:
            ok = True
        if ok:
            r = fx.get(bogus, timeout=max(30, fx.timeout))
            txt = r.text() if r.body else ""
            pp = PageParser(r.final_url)
            try:
                pp.feed(txt)
                pp.close()
            except Exception:
                pass
            final_path = urllib.parse.urlsplit(r.final_url).path
            nf = {"url": bogus, "status": r.status, "final_url": r.final_url, "redirects": r.redirects,
                  "error": r.error, "title": " ".join(pp.title.split())[:120],
                  "h1": [h["text"][:100] for h in pp.headings if h["tag"] == "h1"][:2],
                  "text_says_not_found": bool(NOT_FOUND_TEXT_RE.search(pp.title + " " + " ".join(
                      h["text"] for h in pp.headings[:6]))),
                  "redirect_to_home": bool(r.redirects) and final_path in ("", "/"),
                  "internal_links": sum(1 for ln in pp.links if ln.get("href") and not ln.get("button")),
                  "has_search": search_presence(pp)["any"] if pp.links or pp.forms else False}
            if r.status == 200:
                nf["verdict"] = "soft-404 (200)" + (" → главная" if nf["redirect_to_home"] else "")
            elif r.status in (404, 410):
                nf["verdict"] = "ok %d" % r.status
            else:
                nf["verdict"] = "other %s" % r.status
    res["not_found"] = nf
    # 5. сводка по сайту
    res["summary"] = summarise(res, url_set)
    res["requests_used"] = fx.used
    res["request_log"] = log
    res["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    os.makedirs(os.path.join(out_dir, site_id), exist_ok=True)
    with open(os.path.join(out_dir, site_id, "ia.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(out_dir, site_id, "ia.md"), "w", encoding="utf-8") as fh:
        fh.write(render_md(res))
    return res


def summarise(res, url_set):
    pages = [p for p in res.get("pages", []) if "header" in p]
    home = None
    for p in pages:
        if cmp_key(p["url"]) == cmp_key(res["origin"] + "/"):
            home = p
            break
    if home is None and pages:
        home = pages[0]
    inner = [p for p in pages if p is not home]
    deep = [p for p in inner if p.get("url_depth", 0) >= 2]
    s = OrderedDict()
    s["pages_ok"] = len(pages)
    s["home_header_top"] = home["header"]["top_count"] if home else None
    s["home_header_items"] = home["header"]["top_items"][:14] if home else []
    s["home_header_dropdown"] = home["header"]["dropdown"] if home else None
    s["home_header_mega"] = home["header"]["mega"] if home else None
    s["home_header_max_sub"] = home["header"]["max_sub_per_item"] if home else None
    s["home_header_method"] = home["header"]["method"] if home else None
    s["header_phone"] = home["header"]["phone"] if home else None
    s["header_login"] = home["header"]["login"] if home else None
    s["header_cta"] = home["header"]["cta_texts"][:3] if home else []
    s["search_any"] = any(p["search"]["any"] for p in pages) if pages else None
    s["search_in_header"] = bool(home and any(k.startswith("header") for k in home["search"]["forms_or_inputs"]))
    s["lang_switch"] = any(p["lang_switch"]["count"] or p["lang_switch"]["select"] for p in pages) if pages else None
    s["html_lang"] = home.get("lang") if home else None
    s["hreflang_pages"] = sum(1 for p in pages if p.get("hreflang"))
    s["hreflang_langs"] = sorted({h for p in pages for h, _ in p.get("hreflang", [])})[:20]
    s["footer_links"] = home["footer"]["links"] if home else None
    s["footer_groups"] = home["footer"]["groups_lists"] if home else None
    s["footer_headings"] = home["footer"]["headings"][:8] if home else []
    s["footer_legal"] = bool(home and home["footer"]["legal_links"])
    s["footer_requisites"] = home["footer"]["requisites"] if home else None
    s["footer_sitemap_link"] = home["footer"]["html_sitemap_link"] if home else None
    s["crumbs_inner_pct"] = round(100.0 * sum(1 for p in inner if p["breadcrumbs"]["html"] or p["breadcrumbs"]["ld_items"])
                                  / len(inner), 1) if inner else None
    s["crumbs_deep_pct"] = round(100.0 * sum(1 for p in deep if p["breadcrumbs"]["html"] or p["breadcrumbs"]["ld_items"])
                                 / len(deep), 1) if deep else None
    s["breadcrumb_ld_pct"] = round(100.0 * sum(1 for p in inner if p["breadcrumbs"]["ld_items"]) / len(inner), 1) \
        if inner else None
    s["related_block_pages"] = sum(1 for p in inner if p["content_links"]["related_block_headings"])
    s["content_links_median"] = statistics.median([p["content_links"]["internal_unique"] for p in inner]) \
        if inner else None
    # охват шаблонов sitemap ссылками главной (прокси «глубины клика 1»)
    tpls = res.get("urls", {}).get("templates", [])
    if home and tpls:
        home_links = set(home.get("internal_links_unique", []))
        covered = 0
        for t in tpls:
            ex_keys = t["pattern"]
            hit = False
            for hl in home_links:
                segs = path_segments(urllib.parse.urlsplit(hl).path)
                if segs and lang_of_segment(segs[0]):
                    segs = segs[1:]
                k, _ = template_key(segs)
                if k == ex_keys:
                    hit = True
                    break
            covered += 1 if hit else 0
        s["templates_linked_from_home_pct"] = round(100.0 * covered / len(tpls), 1)
        nav_links = {ln for ln in home_links}
        s["home_links_not_in_sitemap"] = len([u for u in nav_links if cmp_key(u) not in url_set]) if url_set else None
        s["home_internal_links"] = len(home_links)
    s["header_semantic_issue"] = bool(home and home["header"].get("semantic_issue"))
    s["sampled_redirecting"] = sum(1 for p in res.get("pages", []) if p.get("redirects"))
    s["sampled_errors"] = sum(1 for p in res.get("pages", []) if p.get("error"))
    s["not_found"] = res.get("not_found", {}).get("verdict")
    s["blocked"] = res.get("blocked")
    return s


def render_md(res):
    u = res.get("urls", {})
    s = res.get("summary", {})
    lines = ["# ia_probe — %s" % res["id"], "",
             "- Источник: %s · %s · запросов %s · ia_probe %s" % (res["origin"], res["started"], res.get("requests_used"),
                                                                VERSION),
             "- robots.txt: %s; Sitemap в robots: %s; групп: %s" % (
                 res["robots"].get("status"), len(res["robots"].get("sitemaps", []) or []), res["robots"].get("groups")),
             "- sitemap: файлов %s (индекс: %s детей), URL %s, lastmod %s %%, hreflang в sitemap у %s URL" % (
                 res["sitemap"]["files_fetched"], res["sitemap"]["index_children_total"], res["sitemap"]["urls"],
                 res["sitemap"]["lastmod_pct"], res["sitemap"]["hreflang_urls"]),
             "- URL: основной хост %s (%s %%); глубина (без языка) медиана %s, p90 %s, макс %s; шаблонов %s; языки: %s" % (
                 res.get("main_host"), u.get("main_host_share"), u.get("depth_median"), u.get("depth_p90"),
                 u.get("depth_max"), u.get("templates_total"), ", ".join(u.get("lang_prefixes", {}) or []) or "—"),
             "- Шапка: пунктов %s %s; подменю %s; мега %s; поиск %s; телефон %s; вход %s; язык %s" % (
                 s.get("home_header_top"), s.get("home_header_items"), s.get("home_header_dropdown"),
                 s.get("home_header_mega"), s.get("search_any"), s.get("header_phone"), s.get("header_login"),
                 s.get("lang_switch")),
             "- Подвал: ссылок %s, групп %s, юр. ссылки %s, реквизиты %s, карта сайта %s" % (
                 s.get("footer_links"), s.get("footer_groups"), s.get("footer_legal"), s.get("footer_requisites"),
                 s.get("footer_sitemap_link")),
             "- Крошки: внутренние %s %%, глубина ≥ 2 %s %%, BreadcrumbList %s %%; «читайте также» на %s стр." % (
                 s.get("crumbs_inner_pct"), s.get("crumbs_deep_pct"), s.get("breadcrumb_ld_pct"),
                 s.get("related_block_pages")),
             "- Шаблоны sitemap со ссылкой с главной: %s %%; ссылок главной вне sitemap: %s" % (
                 s.get("templates_linked_from_home_pct"), s.get("home_links_not_in_sitemap")),
             "- 404: %s" % s.get("not_found"), ""]
    if u.get("templates"):
        lines += ["| шаблон | тип | URL | пример |", "|---|---|---|---|"]
        for t in u["templates"][:15]:
            lines.append("| `%s` | %s | %s | %s |" % (t["pattern"], t["type"], t["count"], t["examples"][0]))
    return "\n".join(lines) + "\n"


# ----------------------------------------------------------------------------------------------------------------
# Партия и сводка
# ----------------------------------------------------------------------------------------------------------------

def run_batch(tsv, out_dir, skip_done=False, **kw):
    rows = []
    with open(tsv, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip() or line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if parts[0] == "id":
                continue
            rows.append(parts)
    for parts in rows:
        sid, url = parts[0], parts[1]
        meta = {"site_type": parts[2] if len(parts) > 2 else "", "market": parts[3] if len(parts) > 3 else "",
                "note": parts[4] if len(parts) > 4 else ""}
        if skip_done and os.path.exists(os.path.join(out_dir, sid, "ia.json")):
            print("skip", sid, flush=True)
            continue
        t0 = time.time()
        try:
            r = probe_site(url, out_dir, site_id=sid, meta=meta, **kw)
            print("%s\t%s\treq=%s\t%.0fs\turls=%s\tpages=%s\t404=%s" % (
                sid, url, r.get("requests_used"), time.time() - t0, r["sitemap"]["urls"], r["summary"]["pages_ok"],
                r["summary"]["not_found"]), flush=True)
        except Exception as e:  # noqa: BLE001
            print("%s\t%s\tERROR %s" % (sid, url, e), flush=True)


def reanalyse(out_dir):
    """Пересчёт разбора страниц из сохранённого HTML без сети (после правки эвристик)."""
    for sid in sorted(os.listdir(out_dir)):
        fp = os.path.join(out_dir, sid, "ia.json")
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as fh:
            res = json.load(fh)
        new_pages = []
        for p in res.get("pages", []):
            hf = p.get("html_file")
            if not hf:
                new_pages.append(p)
                continue
            with open(os.path.join(out_dir, sid, hf), "rb") as fh:
                body = gzip.decompress(fh.read())
            r = Resp(p["url"])
            r.final_url, r.status = p.get("final_url") or p["url"], p.get("status")
            r.headers = {"content-type": p.get("content_type", "text/html")}
            r.body = body
            pa = analyse_page(r, res.get("main_host") or urllib.parse.urlsplit(res["origin"]).hostname)
            for k in ("html_file", "content_type", "redirects", "in_sitemap", "url_depth"):
                if k in p:
                    pa[k] = p[k]
            new_pages.append(pa)
        res["pages"] = new_pages
        sm = os.path.join(out_dir, sid, "sitemap_urls.txt.gz")
        urls_set = set()
        if os.path.exists(sm):
            with open(sm, "rb") as fh:
                urls_set = {cmp_key(u) for u in gzip.decompress(fh.read()).decode("utf-8").splitlines() if u}
            urls_set.discard(None)
        res["summary"] = summarise(res, urls_set)
        res["reanalysed"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(fp, "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=1)
        with open(os.path.join(out_dir, sid, "ia.md"), "w", encoding="utf-8") as fh:
            fh.write(render_md(res))
        print("reanalysed", sid, flush=True)


SUMMARY_COLS = ["id", "site_type", "market", "robots", "sm_declared", "sm_files", "urls", "main_host_share", "depth_med",
                "depth_p90", "depth_max", "templates", "lang_prefixes", "sm_hreflang_urls", "hreflang_pages",
                "header_method", "header_top", "dropdown", "mega", "max_sub", "search_any", "search_in_header",
                "phone", "login", "lang_switch", "footer_links", "footer_groups", "footer_legal", "requisites",
                "sitemap_link", "crumbs_inner_pct", "crumbs_deep_pct", "bc_ld_pct", "related_pages",
                "content_links_med", "tpl_from_home_pct", "home_links_not_in_sm", "header_semantic_issue",
                "sm_relative_locs", "sampled_redirecting",
                "sampled_errors", "not_found", "blocked", "requests"]


def summary_table(out_dir):
    print("\t".join(SUMMARY_COLS))
    for sid in sorted(os.listdir(out_dir)):
        fp = os.path.join(out_dir, sid, "ia.json")
        if not os.path.exists(fp):
            continue
        with open(fp, encoding="utf-8") as fh:
            r = json.load(fh)
        s, u, m = r.get("summary", {}), r.get("urls", {}), r.get("meta", {})
        row = [sid, m.get("site_type", ""), m.get("market", ""), r["robots"].get("status"),
               r["sitemap"]["declared_in_robots"], r["sitemap"]["files_fetched"], r["sitemap"]["urls"],
               u.get("main_host_share"), u.get("depth_median"), u.get("depth_p90"), u.get("depth_max"),
               u.get("templates_total"), ",".join(u.get("lang_prefixes", {}) or []), r["sitemap"]["hreflang_urls"],
               s.get("hreflang_pages"), s.get("home_header_method"), s.get("home_header_top"),
               s.get("home_header_dropdown"), s.get("home_header_mega"), s.get("home_header_max_sub"),
               s.get("search_any"), s.get("search_in_header"), s.get("header_phone"), s.get("header_login"),
               s.get("lang_switch"), s.get("footer_links"), s.get("footer_groups"), s.get("footer_legal"),
               s.get("footer_requisites"), s.get("footer_sitemap_link"), s.get("crumbs_inner_pct"),
               s.get("crumbs_deep_pct"), s.get("breadcrumb_ld_pct"), s.get("related_block_pages"),
               s.get("content_links_median"), s.get("templates_linked_from_home_pct"),
               s.get("home_links_not_in_sitemap"), s.get("header_semantic_issue"),
               r["sitemap"].get("relative_locs"), s.get("sampled_redirecting"), s.get("sampled_errors"),
               s.get("not_found"), s.get("blocked"), r.get("requests_used")]
        print("\t".join("" if v is None else str(v) for v in row))


# ----------------------------------------------------------------------------------------------------------------
# Самопроверка: локальный сервер с фикстурами
# ----------------------------------------------------------------------------------------------------------------

FIX_HEADER = """<header class="site-header"><a href="/" class="logo"><img src="/l.svg" alt="Бренд"></a>
<nav aria-label="Главное меню"><ul>
<li><a href="/services/">Услуги</a><div class="mega-panel"><ul>
  <li><a href="/services/cleaning/">Уборка</a></li><li><a href="/services/windows/">Окна</a></li>
  <li><a href="/services/carpets/">Ковры</a></li><li><a href="/services/sofa/">Диваны</a></li>
  <li><a href="/services/office/">Офисы</a></li><li><a href="/services/after-repair/">После ремонта</a></li></ul>
  <ul><li><a href="/services/moscow/">Москва</a></li><li><a href="/services/spb/">Петербург</a></li>
  <li><a href="/services/kazan/">Казань</a></li><li><a href="/services/ufa/">Уфа</a></li></ul></div></li>
<li><a href="/prices/">Цены</a></li><li><a href="/cases/">Работы</a></li><li><a href="/about/">О компании</a></li>
<li><a href="/contacts/">Контакты</a></li></ul></nav>
<form role="search" action="/search/"><input type="search" name="q" placeholder="Поиск"></form>
<a href="tel:+78000000000">8 800 000-00-00</a><a class="btn btn-primary" href="/order/">Заказать уборку</a>
<a href="/en/" hreflang="en">English</a></header>"""

FIX_FOOTER = """<footer><div><h3>Услуги</h3><ul><li><a href="/services/cleaning/">Уборка</a></li>
<li><a href="/services/windows/">Окна</a></li></ul></div><div><h3>Компания</h3><ul><li><a href="/about/">О нас</a></li>
<li><a href="/contacts/">Контакты</a></li><li><a href="/sitemap/">Карта сайта</a></li></ul></div>
<p>ООО «Чисто», ИНН 7700000000, ОГРН 1027700000000, г. Москва, ул. Примерная, д. 1</p>
<a href="/privacy/">Политика обработки персональных данных</a> <a href="https://vk.com/x">VK</a> © 2026</footer>"""


def fixture_page(title, body, crumbs=None, ld=None, lang="ru", alt=True):
    head = '<meta charset="utf-8"><title>%s</title>' % title
    if alt:
        head += '<link rel="alternate" hreflang="ru" href="/"><link rel="alternate" hreflang="en" href="/en/">'
    if ld:
        head += '<script type="application/ld+json">%s</script>' % json.dumps(ld, ensure_ascii=False)
    cr = ""
    if crumbs:
        cr = '<nav aria-label="Хлебные крошки"><ol>' + "".join(
            '<li><a href="%s">%s</a></li>' % (h, t) for h, t in crumbs) + "</ol></nav>"
    return ('<!doctype html><html lang="%s"><head>%s</head><body>%s<main>%s%s</main>%s</body></html>'
            % (lang, head, FIX_HEADER, cr, body, FIX_FOOTER)).encode("utf-8")


def fixture_site():
    bl = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Главная", "item": "/"},
        {"@type": "ListItem", "position": 2, "name": "Услуги", "item": "/services/"},
        {"@type": "ListItem", "position": 3, "name": "Уборка"}]}
    site = {
        "/robots.txt": (200, "text/plain", b"User-agent: *\nDisallow: /admin/\nDisallow: /private-page/\n"
                                            b"Sitemap: http://HOST/sitemap_index.xml\n"),
        "/sitemap_index.xml": (200, "application/xml", b'<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/'
                                                       b'schemas/sitemap/0.9"><sitemap><loc>http://HOST/sm-pages.xml</loc>'
                                                       b'</sitemap><sitemap><loc>http://HOST/sm-blog.xml.gz</loc></sitemap>'
                                                       b'</sitemapindex>'),
        "/": (200, "text/html; charset=utf-8", fixture_page("Главная", '<h1>Уборка квартир</h1><a href="/services/cleaning/">'
                                                           'Уборка</a><a href="/blog/">Блог</a>')),
        "/services/": (200, "text/html; charset=utf-8", fixture_page("Услуги", "<h1>Услуги</h1>",
                                                                    crumbs=[("/", "Главная"), ("/services/", "Услуги")])),
        "/services/cleaning/": (200, "text/html; charset=utf-8", fixture_page(
            "Уборка", '<h1>Уборка</h1><p>Текст услуги со <a href="/prices/">ценами</a>.</p><h2>Читайте также</h2>'
                      '<a href="/blog/how-to-clean/">Как убрать</a>', crumbs=[("/", "Главная"), ("/services/", "Услуги"),
                                                                            ("/services/cleaning/", "Уборка")], ld=bl)),
        "/prices/": (200, "text/html; charset=utf-8", fixture_page("Цены", "<h1>Цены</h1>")),
        "/about/": (200, "text/html; charset=utf-8", fixture_page("О компании", "<h1>О компании</h1>")),
        "/contacts/": (200, "text/html; charset=utf-8", fixture_page("Контакты", "<h1>Контакты</h1>")),
        "/blog/": (200, "text/html; charset=utf-8", fixture_page("Блог", "<h1>Блог</h1>")),
        "/blog/how-to-clean/": (200, "text/html; charset=utf-8", fixture_page(
            "Как убрать", "<article><h1>Как убрать</h1><p>Текст</p></article>",
            crumbs=[("/", "Главная"), ("/blog/", "Блог")])),
        "/private-page/": (200, "text/html; charset=utf-8", fixture_page("Скрыто", "<h1>Скрыто</h1>")),
    }
    pages_xml = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                 'xmlns:xhtml="http://www.w3.org/1999/xhtml" '
                 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + "".join(
                     '<url><loc>http://HOST%s</loc><lastmod>2026-09-01</lastmod>'
                     '<image:image><image:loc>http://HOST/wp-content/uploads/pic.png</image:loc></image:image>'
                     '<xhtml:link rel="alternate" hreflang="en" href="http://HOST/en%s"/></url>' % (p, p)
                     for p in ["/", "/services/", "/services/cleaning/", "/prices/", "/about/", "/contacts/",
                               "/private-page/"]) + "</urlset>").encode()
    blog_xml = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(
        "<url><loc>http://HOST%s</loc></url>" % p for p in ["/blog/", "/blog/how-to-clean/"]) + "</urlset>").encode()
    site["/sm-pages.xml"] = (200, "application/xml", pages_xml)
    site["/sm-blog.xml.gz"] = (200, "application/x-gzip", blog_xml)   # сжимается после подстановки HOST
    return site


def selftest():
    import http.server
    site = fixture_site()
    soft404 = {"on": False}

    class H(http.server.BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            hostport = self.headers.get("Host", "")
            path = self.path.split("?", 1)[0]
            if path == "/old-services/":
                self.send_response(301)
                self.send_header("Location", "/services/")
                self.end_headers()
                return
            if path in site:
                code, ctype, body = site[path]
                body = body.replace(b"HOST", hostport.encode())
                if path.endswith(".gz"):
                    body = gzip.compress(body)
            elif soft404["on"]:
                code, ctype, body = 200, "text/html; charset=utf-8", fixture_page("Страница не найдена",
                                                                                  "<h1>Страница не найдена</h1>")
            else:
                code, ctype, body = 404, "text/html; charset=utf-8", fixture_page("Страница не найдена",
                                                                                  "<h1>Страница не найдена</h1>")
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    port = srv.server_address[1]
    out = str(kbpaths.out("site", "ia_probe", "selftest"))
    os.makedirs(out, exist_ok=True)
    checks = []

    def ok(name, cond, val=None):
        checks.append((name, bool(cond), val))

    try:
        r = probe_site("http://127.0.0.1:%d/" % port, out, site_id="fixture", sample=10, delay=0.0)
        s = r["summary"]
        ok("robots 200 и Sitemap из robots", r["robots"]["status"] == 200 and r["sitemap"]["declared_in_robots"])
        ok("индекс sitemap: 2 ребёнка, gzip читается", r["sitemap"]["index_children_total"] == 2 and r["sitemap"]["urls"] == 9,
           r["sitemap"]["urls"])
        ok("hreflang в sitemap: 7 URL, язык en", r["sitemap"]["hreflang_urls"] == 7 and "en" in r["sitemap"]["hreflang_langs"])
        ok("image:loc не подменяет loc страницы", not any(".png" in t["examples"][0] for t in r["urls"]["templates"]),
           [t["pattern"] for t in r["urls"]["templates"]])
        ok("lastmod 7 из 9", abs(r["sitemap"]["lastmod_pct"] - 77.8) < 0.2, r["sitemap"]["lastmod_pct"])
        ok("глубина: макс 2, медиана 1", r["urls"]["depth_max"] == 2 and r["urls"]["depth_median"] == 1,
           (r["urls"]["depth_max"], r["urls"]["depth_median"]))
        tp = {t["pattern"]: t for t in r["urls"]["templates"]}
        ok("шаблон /services/{slug} → services", tp.get("/services/{slug}", {}).get("type") == "services", list(tp))
        ok("robots.txt: /private-page/ в выборке и пропущена", any(p.get("skipped", "").startswith("robots") and
                                                                  "/private-page/" in p.get("url", "") for p in r["pages"])
           and not any("/private-page/" in (p.get("url") or "") and "header" in p for p in r["pages"]),
           [(p.get("url"), p.get("skipped")) for p in r["pages"]])
        ok("статья блога из gzip-sitemap попала в выборку", any("/blog/how-to-clean/" in (p.get("url") or "") and
                                                                 "header" in p for p in r["pages"]))
        ok("шапка: 5 пунктов верхнего уровня", s["home_header_top"] == 5, s["home_header_items"])
        ok("шапка: мега-меню (≥ 10 ссылок в 2 группах)", s["home_header_mega"] is True, s["home_header_max_sub"])
        ok("шапка: телефон, поиск, язык", s["header_phone"] and s["search_in_header"] and s["lang_switch"])
        ok("подвал: 2 группы, юр. ссылка, реквизиты, карта сайта", s["footer_groups"] == 2 and s["footer_legal"]
           and s["footer_requisites"] and s["footer_sitemap_link"], (s["footer_groups"], s["footer_legal"]))
        cl = [p for p in r["pages"] if p.get("final_url", "").endswith("/services/cleaning/")]
        ok("крошки: HTML (3 ссылки) + BreadcrumbList 3 элемента", cl and cl[0]["breadcrumbs"]["html_links"] == 3
           and cl[0]["breadcrumbs"]["ld_items"] == [3], cl and cl[0]["breadcrumbs"])
        ok("«Читайте также» найдено", cl and cl[0]["content_links"]["related_block_headings"])
        ok("404 честный", r["not_found"].get("verdict") == "ok 404", r["not_found"].get("verdict"))
        ok("пауза 0 только для localhost; бюджет не превышен", r["requests_used"] <= MAX_REQUESTS_DEFAULT)
        soft404["on"] = True
        r2 = probe_site("http://127.0.0.1:%d/" % port, out, site_id="fixture-soft", sample=2, delay=0.0)
        ok("мягкая 404 распознана", r2["not_found"].get("verdict", "").startswith("soft-404")
           and r2["not_found"].get("text_says_not_found"), r2["not_found"].get("verdict"))
        fx = Fetcher(delay=0.0)
        rr = fx.get("http://127.0.0.1:%d/old-services/" % port)
        ok("редирект 301 проходится вручную и считается запросом", rr.final_url.endswith("/services/") and
           rr.requests == 2, (rr.final_url, rr.requests))
        ok("минимальная пауза для внешних хостов = 1 с", max(MIN_DELAY, 0.2) == 1.0)
        rob = parse_robots("User-agent: Yandex\nDisallow: /a\n\nUser-agent: *\nCrawl-delay: 2\nDisallow: /b\n"
                           "Sitemap: https://x.ru/s.xml")
        ok("разбор robots: 2 группы, Crawl-delay 2, Sitemap", rob["groups"] == 2 and rob["star"]["crawl_delay"] == 2.0
           and rob["sitemaps"] == ["https://x.ru/s.xml"], rob)
        rx = Resp("https://ex.ru/")
        rx.final_url, rx.status = "https://ex.ru/", 200
        rx.headers = {"content-type": "text/html; charset=utf-8"}
        rx.body = ('<html><body><header><ul><li><a href="/">Лого</a><ul><li><a href="/a/">А</a></li>'
                   '<li><a href="/b/">Б</a></li><li><a href="/c/">В</a><ul><li><a href="/c/1/">В1</a></li>'
                   '<li><a href="/c/2/">В2</a></li></ul></li></ul></li></ul></header><main><h1>Т</h1></main>'
                   '<footer><h4>Раздел</h4><a href="/a/">А</a><h4>Ещё</h4><a href="/b/">Б</a></footer>'
                   '</body></html>').encode()
        pa = analyse_page(rx, "ex.ru")
        ok("логотип один на верхнем уровне списка: пункты — А, Б, В", pa["header"]["top_items"] == ["А", "Б", "В"]
           and pa["header"]["sub_links"] == 2, pa["header"]["top_items"])
        ok("группы подвала по заголовкам без списков", pa["footer"]["groups_lists"] == 2, pa["footer"]["groups_lists"])
        rx2 = Resp("https://ex.ru/")
        rx2.final_url, rx2.status = "https://ex.ru/", 200
        rx2.headers = {"content-type": "text/html; charset=utf-8"}
        rx2.body = ('<html><body><nav class="navbar"><a href="/">Лого</a><ul><li><a href="/a/">А</a></li>'
                    '<li><a href="/b/">Б</a></li><li><a href="/c/">В</a></li><li><a href="/d/">Г</a></li></ul></nav>'
                    '<header id="header"><h1>Главное обещание</h1><img src="x.jpg" alt=""></header><main></main>'
                    '</body></html>').encode()
        pb = analyse_page(rx2, "ex.ru")
        ok("hero в <header>, меню в <nav> снаружи: берётся nav, semantic_issue", pb["header"]["method"] in ("first-nav",
                                                                                                          "class")
           and pb["header"]["top_count"] == 4 and pb["header"]["semantic_issue"] is True,
           (pb["header"]["method"], pb["header"]["top_count"], pb["header"].get("semantic_issue")))
        k, e, _ = parse_sitemap_bytes(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>/a/</loc>'
                                      b'</url></urlset>')
        ok("относительный loc читается (флаг ставит probe_site)", k == "urlset" and e and e[0]["loc"] == "/a/")
        ok("язык-префикс /en/ распознаётся", lang_of_segment("en") == "en" and lang_of_segment("en-us") == "en"
           and lang_of_segment("xx") is None)
    finally:
        srv.shutdown()
    passed = sum(1 for c in checks if c[1])
    for name, good, val in checks:
        print(("PASS " if good else "FAIL ") + name + ("" if good else "  → %r" % (val,)))
    print("selftest: %d/%d PASS; вывод: %s" % (passed, len(checks), out))
    return 0 if passed == len(checks) else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url", nargs="?")
    ap.add_argument("--out", default=str(kbpaths.out("site", "ia_probe")))
    ap.add_argument("--id")
    ap.add_argument("--sample", type=int, default=14, help="страниц из sitemap (кроме корня), по умолчанию 14")
    ap.add_argument("--delay", type=float, default=MIN_DELAY, help="пауза между запросами, с (не меньше 1)")
    ap.add_argument("--budget", type=int, default=MAX_REQUESTS_DEFAULT, help="запросов на сайт (не больше 200)")
    ap.add_argument("--max-sitemaps", type=int, default=12)
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--summary")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--reanalyse", help="пересчитать разбор по сохранённому HTML в DIR без сети")
    ap.add_argument("--no-save-html", action="store_true")
    kbg = ap.add_argument_group("обслуживание базы", "обход корпуса сайтов базы знаний; разбору сайта проекта эти ключи "
                                                     "не нужны")
    kbg.add_argument("--batch", metavar="TSV", help="сайты списка (колонки id, url, site_type, market, note) — в папку --out")
    kbg.add_argument("--skip-done", action="store_true", help="с --batch: пропустить сайты с готовым ia.json")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.summary:
        summary_table(a.summary)
        return
    if a.reanalyse:
        reanalyse(a.reanalyse)
        return
    budget = min(a.budget, MAX_REQUESTS_DEFAULT)
    delay = max(a.delay, MIN_DELAY)
    kw = dict(sample=min(a.sample, budget - 20), delay=delay, budget=budget, max_sitemaps=a.max_sitemaps,
              timeout=a.timeout, save_html=not a.no_save_html)
    if a.batch:
        run_batch(a.batch, a.out, skip_done=a.skip_done, **kw)
        return
    if not a.url:
        ap.error("нужен URL, --batch, --summary или --selftest")
    r = probe_site(a.url, a.out, site_id=a.id, **kw)
    print(render_md(r))


if __name__ == "__main__":
    main()
