#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""copydeck.py — copy deck text-research: проверка формата, сверка с фактами, линтер, экспорт в пакет kimi и обратно.

text-research · волна 3 · агент J · 2026-09-24 (1.0 — фаза 1, J и J2; 1.1 — фаза 2, J3: пробелы в check, --all-variants
копиями страницы, variant.fact_ids, мета на листе выбора, rebase_refs, adaptation.voice_line). Формат —
10-templates-recipes/copy-deck.schema.json (v1 = черновик v0 из PLAN.md без удаления полей + новые необязательные поля;
v1.1 — variant.fact_ids, adaptation.voice_line); процесс — 10-templates-recipes/01-copy-deck-workflow.md.

Подкоманды (порядок проверок — решение оркестратора: сначала факты и право, потом стиль, потом формат и статусы):
  validate DECK [--facts F] [--today ГГГГ-ММ-ДД] [--final] [--no-jsonschema]
        схема (jsonschema, если есть; иначе встроенная проверка того же подмножества), id и ссылки, статусы
        (x-status-rules схемы), временный словарь, факты (есть ли, не пробел ли, не истекли ли, публикуемы ли),
        [PLACEHOLDER], обещание первого экрана, строки в картинках, второй язык; файлы волны 2 — copy-slots.yaml (E),
        voice.yaml (F), meta-rules.yaml (G), claims-rules.yaml (H): есть — проверка работает, нет — предупреждение
        «правила не загружены»
  claims DECK [--facts F] [--today …] [--strict] [--all-variants]
        claims_check.py (B2 + право H) процессом на плоской копии v0: обещание, мета, OG-шаблон — тоже текст страницы
  lint DECK [--final] [--all-variants] [--no-page-pass]
        copy_lint.py через API lint_text: каждый слот со своим slot_type и жанром + проход страницы (ритм, плотности,
        надзаголовки); lint_allow и --final — по правилам C
  check DECK [--facts F] [--today …] [--final] [--strict] [--all-variants] [--update OUT [--promote]]
        claims → lint → validate; --update пишет копию deck с записями lint и claims (text_hash, дата, версия),
        --promote — draft → checked при 0 error; --all-variants — альтернативы «как выбранные», с --update — variant.checks
  export-kimi DECK --out DIR [--page ID] [--facts F] [--meaning M] [--merge-into BRIEF] [--strict] [--facts-scope all|used]
        copy.md, facts.md и brief-fragment.yaml для пакета ../kimi-research/07-brief-handoff/templates/
  import-kimi COPY.md -o DECK [--brief brief.yaml] [--facts F] [--page-type T]
        copy.md пакета kimi (+ product.goal, jobs, alt и подписи из brief.yaml) → copy deck v1
  export-assets DECK [--page ID] [-o OUT]   alt, подписи, строки в картинках, OG → фрагмент плана ассетов ai-media
  export-variants DECK -o SHEET.md --key KEY.yaml [--seed N] [--include-failed]   лист слепого выбора (слоты, обещание,
                                             мета; метки, модели скрыты; варианты с error в checks сняты; I)
  approve DECK --page ID --by КТО -o OUT      утверждение страницы человеком: checked (0 error, актуальный text_hash,
                                             без [PLACEHOLDER]) → approved; --promote у check переводит draft → checked
  upgrade DECK -o OUT                        copy deck v0 → v1 (section_role, пустые fact_ids и claim_flags)
  --selftest                                 офлайн-тесты
Все подкоманды проверок: --json OUT, --md OUT, --quiet. Коды выхода: 0 — нет error, 2 — есть error, 1 — ошибка входа.

Зависимости: Python 3.10+, PyYAML. jsonschema — необязательно (99-raw/tools/venv-J). Модели и сеть не нужны.
Чужие утилиты не переписаны: claims_check.py (B2, H) вызывается процессом, copy_lint.py (C) — через lint_text.
"""
from __future__ import annotations

import argparse
import copy as _copy
import datetime as dt
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit('copydeck.py: нужен PyYAML (python3-yaml или 99-raw/tools/venv-J/bin/python)')

VERSION = '1.1'
DATE = '2026-09-24'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('text'))
SCHEMA_PATH = os.path.join(ROOT, '10-templates-recipes', 'copy-deck.schema.json')
VOCAB_PATH = os.path.join(ROOT, '99-raw', 'notes', 'temp-vocabulary-v0.yaml')
FACTS_SCHEMA_PATH = os.path.join(ROOT, '02-strategy-messaging', 'facts.schema.yaml')
COPY_SLOTS_PATH = os.path.join(ROOT, '04-copy-by-block', 'copy-slots.yaml')
VOICE_SCHEMA_PATH = os.path.join(ROOT, '05-voice-editorial', 'voice.schema.yaml')
META_RULES_PATH = os.path.join(ROOT, '07-seo-geo-copy', 'meta-rules.yaml')
CLAIMS_RULES_PATH = os.path.join(ROOT, '08-russian-legal-typography', 'claims-rules.yaml')
CLAIMS_CHECK = os.path.join(HERE, 'claims_check.py')
GENRES = ('landing', 'site-page', 'article', 'meta', 'geo', 'email-form')
LEVELS = ('error', 'warning', 'info')
STATUS_RANK = {'draft': 0, 'checked': 1, 'approved': 2, 'rejected': -1}
PLACEHOLDER_RX = re.compile(r'\[PLACEHOLDER(?::\s*([^\]]*))?\]', re.I)
BAD_PLACEHOLDER_RX = re.compile(r'\[\s*(?:заглушка|todo|tbd|xxx|плейсхолдер|placeholder\s*[^:\]\s])|lorem ipsum|\bTODO\b|'
                                r'(?<!\[)PLACEHOLDER(?!\s*[:\]])|\[PLACEHOLDER(?![^\]]*\])', re.I)
META_FIELDS = (('title', 'meta-title'), ('description', 'meta-description'), ('og_title', 'og-title'),
               ('og_description', 'og-description'), ('og_image_alt', 'og-image-alt'))
OG_TEMPLATE_FIELDS = (('kicker', 'eyebrow'), ('title', 'og-title'))
# Прозаические типы слотов (спецификация линтера C §3.4) — для прохода страницы.
PROSE_SLOT_TYPES = {'body', 'section-lead', 'article-paragraph', 'article-lead', 'article-summary', 'geo-answer',
                    'definition', 'faq-a', 'email-body', 'case-summary', 'guarantee-text', 'objection-answer',
                    'pricing-plan-summary'}
HEADING_LEVEL = {'headline': 1, 'article-title': 1, 'section-title': 2, 'article-heading': 2, 'form-title': 2,
                 'email-heading': 2, 'card-title': 3, 'step-title': 3, 'case-title': 3, 'pricing-plan-name': 3,
                 'faq-q': 3}
# Ключи copy.md kimi → slot_type (для import-kimi; claims_check.py держит ту же таблицу — берём её, если доступна).
KIMI_KEY_SLOT = [(r'^h1$', 'headline'), (r'^lead$', 'subheadline'), (r'^cta(?:_\w+)?$', 'cta-label'),
                 (r'^note$', 'cta-note'), (r'^h2$', 'section-title'), (r'^h3$', 'card-title'), (r'^p\d*$', 'body'),
                 (r'^item\d+_title$', 'card-title'), (r'^item\d+_text$', 'card-body'), (r'^row\d+$', 'spec-row'),
                 (r'^price(?:_now)?$', 'pricing-price'), (r'^price_old$', 'price-old'),
                 (r'^(?:deposit|shipping|price_note)$', 'pricing-price-note'), (r'^q\d+$', 'faq-q'), (r'^a\d+$', 'faq-a'),
                 (r'^legal$', 'footer-legal'), (r'^hint$', 'body'), (r'^quote\d*$', 'testimonial-quote'),
                 (r'^(?:author|attribution)\d*$', 'testimonial-attribution'), (r'^stat\d*_value$', 'stat-value'),
                 (r'^stat\d*_label$', 'stat-label'), (r'^logos?_caption$', 'logos-caption')]
KIMI_SECTION_ROLE = {'hero': 'hero', 'problem': 'problem', 'how': 'how-it-works', 'object3d': 'product-demo',
                     'specs': 'specs', 'price': 'pricing', 'pricing': 'pricing', 'faq': 'faq', 'final_cta': 'final-cta',
                     'footer': 'footer', 'reviews': 'testimonials', 'testimonials': 'testimonials', 'logos': 'proof-logos',
                     'stats': 'proof-stats', 'cases': 'case-studies', 'case': 'case-studies', 'team': 'team',
                     'about': 'about', 'guarantee': 'guarantee', 'contacts': 'contacts', 'form': 'lead-form',
                     'benefits': 'benefits', 'features': 'benefits', 'solution': 'solution', 'cta': 'cta-band',
                     'final': 'final-cta', 'proof': 'proof-stats', 'how-it-works': 'how-it-works'}
# Набор запретов по умолчанию x-never-claim-defaults (B2) — английская адаптация для copy deck с lang: en (ai-self J).
NEVER_EN = {
    'nc-counts': 'Customer, user or order counts and growth percentages without a fact with a source and a date',
    'nc-ratings': 'Ratings and stars without a fact with the platform, scale, number of reviews and snapshot date',
    'nc-trusted-by': '"Trusted by", client and partner names and logos without a fact with the client\'s written permission',
    'nc-awards-press': 'Awards, prizes, "as seen in", media logos without a fact with a link or a document',
    'nc-testimonials': 'Testimonials, quotes, names and photos of people without a fact with written permission',
    'nc-prices-terms': 'Prices, discounts, delivery times, guarantees, certifications without a fact',
    'nc-superlatives': '"Best", "No. 1", "most", "first", "leader" without a criterion and objective proof',
    'nc-comparisons': 'Comparisons with competitors and "N times" without a method, a date and a document',
    'nc-health': 'Health or healing promises (never for non-medical goods and services)',
    'nc-income': 'Promises of income, earnings or payback',
    'nc-scarcity': '"Only N left", "last places" without a live stock source',
    'nc-deadline': 'Offer deadlines and countdown timers without a real end date',
    'nc-forecast': 'Forecasts of results without a calculation and a disclaimer',
    'nc-official-approval': 'Claims of approval by public authorities ("approved by the Ministry of Health")',
    'nc-ai-people': 'AI-generated people as clients, team or reviewers; invented names and faces',
}


# ============================================================================================ общие помощники
def today_iso(s=None):
    if s:
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
            raise SystemExit('--today: ГГГГ-ММ-ДД')
        return s
    return dt.date.today().isoformat()


def norm_ws(s):
    return re.sub(r'\s+', ' ', str(s or '').replace(' ', ' ').replace(' ', ' ')).strip()


def text_hash(s):
    """sha1 нормализованного текста (пробелы, NBSP), первые 12 знаков — для записи lint/claims."""
    return hashlib.sha1(norm_ws(s).encode('utf-8')).hexdigest()[:12]


def date_end(s):
    """«2026-10» → «2026-10-31» для сравнения сроков; «2026-10-31» → как есть."""
    s = str(s)
    if re.fullmatch(r'\d{4}-\d{2}', s):
        y, m = int(s[:4]), int(s[5:7])
        nxt = dt.date(y + (m == 12), (m % 12) + 1, 1)
        return (nxt - dt.timedelta(days=1)).isoformat()
    return s


def deep_dates(x, path='', found=None):
    """datetime.date из YAML без кавычек → строка ISO; пути таких мест — в found (сигнал «дата без кавычек»)."""
    if isinstance(x, dict):
        return {k: deep_dates(v, f'{path}.{k}' if path else str(k), found) for k, v in x.items()}
    if isinstance(x, list):
        return [deep_dates(v, f'{path}[{i}]', found) for i, v in enumerate(x)]
    if isinstance(x, (dt.date, dt.datetime)):
        if found is not None:
            found.append(path)
        return x.isoformat()[:10]
    return x


def load_yaml_file(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def rel_to(base_file, ref):
    """Путь ref относительно папки файла base_file (как facts_ref в copy deck)."""
    if not ref:
        return None
    if os.path.isabs(ref):
        return ref
    return os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(base_file)), ref))


def looks_like_path(s):
    return bool(s) and bool(re.search(r'\.(ya?ml|json)$', str(s).strip(), re.I))


def cyr_share(s):
    c = len(re.findall(r'[А-Яа-яЁё]', s or ''))
    lat = len(re.findall(r'[A-Za-z]', s or ''))
    return c / (c + lat) if (c + lat) else 0.0


def words(s):
    return re.findall(r"[0-9A-Za-zА-Яа-яЁё]+(?:[-'’][0-9A-Za-zА-Яа-яЁё]+)*", s or '')


class Report:
    """Находки одной команды: tool (validate, claims, lint), level, rule (COPY-D-…, COPY-F-…, id правила C), where
    (путь copy deck: page/section/slot), message, fix."""

    def __init__(self):
        self.findings = []
        self.notes = []
        self.tools = {}

    def add(self, tool, level, rule, where, message, fix='', **extra):
        f = {'tool': tool, 'level': level, 'rule': rule, 'where': where or '—', 'message': message, 'fix': fix}
        f.update({k: v for k, v in extra.items() if v not in (None, '', [], {})})
        self.findings.append(f)
        return f

    def count(self, level, tool=None):
        return sum(1 for f in self.findings if f['level'] == level and (tool is None or f['tool'] == tool))

    def summary(self):
        return {lv: self.count(lv) for lv in LEVELS}


# ============================================================================================ copy deck: обход
def deck_root(data):
    if isinstance(data, dict) and isinstance(data.get('copy_deck'), dict):
        return data['copy_deck']
    return data if isinstance(data, dict) else {}


def pages_of(deck):
    return [p for p in (deck.get('pages') or []) if isinstance(p, dict)]


def sections_of(page):
    return [s for s in (page.get('sections') or []) if isinstance(s, dict)]


def slots_of(section):
    return [s for s in (section.get('slots') or []) if isinstance(s, dict)]


def iter_slots(deck):
    for p in pages_of(deck):
        for s in sections_of(p):
            for sl in slots_of(s):
                yield p, s, sl, f"{p.get('page_id')}/{s.get('section_id')}/{sl.get('slot_id')}"


def variants_of(slot):
    return [v for v in (slot.get('variants') or []) if isinstance(v, dict)]


def chosen_variant(slot):
    """Выбранный вариант: chosen; без chosen — единственный вариант; иначе None."""
    vs = variants_of(slot)
    ch = slot.get('chosen')
    if ch is not None:
        for v in vs:
            if str(v.get('id')) == str(ch):
                return v
        return None
    return vs[0] if len(vs) == 1 else None


def main_variant(slot):
    """Текст, который проверяется как текст слота: выбранный вариант; без chosen при нескольких вариантах — первый
    (так же делает claims_check.py; validate при этом предупреждает COPY-D-CHOSEN); chosen на несуществующий — None."""
    v = chosen_variant(slot)
    if v is None and slot.get('chosen') is None:
        vs = variants_of(slot)
        return vs[0] if vs else None
    return v


def variant_fact_ids(slot, v):
    """Факты текста: свои fact_ids варианта (необязательное поле v1.1 — варианты одного слота опираются на разные факты,
    I3), иначе fact_ids слота (v0). Свой список заменяет список слота, а не дополняет его."""
    if isinstance(v, dict) and isinstance(v.get('fact_ids'), list):
        return v['fact_ids']
    return (slot or {}).get('fact_ids') or []


def find_slot(deck, path):
    parts = str(path or '').split('/')
    if len(parts) < 3:
        return None
    for p in pages_of(deck):
        if str(p.get('page_id')) != parts[0]:
            continue
        for s in sections_of(p):
            if str(s.get('section_id')) != parts[1]:
                continue
            for sl in slots_of(s):
                if str(sl.get('slot_id')) == parts[2]:
                    return p, s, sl
    return None


def promise_info(deck, page):
    """(текст, вариант или None, путь-источник, объект promise) обещания страницы; from — текст слота."""
    pr = page.get('promise')
    if not isinstance(pr, dict):
        return None, None, None, None
    if pr.get('from'):
        hit = find_slot(deck, pr['from'])
        if not hit:
            return None, None, pr['from'], pr
        v = chosen_variant(hit[2])
        return (v.get('text') if v else None), v, pr['from'], pr
    v = chosen_variant(pr)
    return (v.get('text') if v else None), v, f"{page.get('page_id')}/promise", pr


def primary_cta(deck, page):
    """(путь, текст) главной кнопки: cta_primary или первый cta-label секции hero (или страницы)."""
    if page.get('cta_primary'):
        hit = find_slot(deck, page['cta_primary'])
        if hit:
            v = chosen_variant(hit[2])
            return page['cta_primary'], (v.get('text') if v else None)
        return page['cta_primary'], None
    first = None
    for s in sections_of(page):
        for sl in slots_of(s):
            if sl.get('slot_type') == 'cta-label':
                v = chosen_variant(sl)
                path = f"{page.get('page_id')}/{s.get('section_id')}/{sl.get('slot_id')}"
                if (s.get('section_role') or s.get('block') or s.get('section_id')) == 'hero':
                    return path, (v.get('text') if v else None)
                if first is None:
                    first = (path, (v.get('text') if v else None))
    return first or (None, None)


# ============================================================================================ словарь, схема, факты
def load_vocab(path=VOCAB_PATH, copy_schema=None):
    """Временный словарь (+ предложения B2 и J). None — файла нет."""
    if not os.path.exists(path):
        return None
    v = load_yaml_file(path) or {}
    out = {'page_types': {x['id']: x.get('genre') for x in v.get('page_types') or [] if isinstance(x, dict)},
           'section_roles': {x['id'] for x in v.get('section_roles') or [] if isinstance(x, dict)},
           'slot_types': {x['id']: x for x in v.get('slot_types') or [] if isinstance(x, dict)},
           'proposals': {'section_roles': set(), 'slot_types': set()}, 'path': path}
    for src in (load_facts_schema(), copy_schema or {}):
        props = (src or {}).get('x-vocabulary-proposals') or {}
        for key in ('section_roles', 'slot_types'):
            for x in props.get(key) or []:
                if isinstance(x, dict) and x.get('id'):
                    out['proposals'][key].add(x['id'])
    try:  # предложения E к словарю slot_type (copy-slots.yaml: proposals, proposal: true)
        if os.path.exists(COPY_SLOTS_PATH):
            cs = load_yaml_file(COPY_SLOTS_PATH) or {}
            out['proposals']['slot_types'] |= {str(x) for x in cs.get('proposals') or []}
            out['proposals']['slot_types'] |= {str(x.get('id')) for x in cs.get('slot_types') or [] if isinstance(x, dict) and x.get('proposal')}
    except Exception:  # noqa: BLE001
        pass
    return out


_FACTS_SCHEMA = {}


def load_facts_schema(path=FACTS_SCHEMA_PATH):
    if path not in _FACTS_SCHEMA:
        _FACTS_SCHEMA[path] = deep_dates(load_yaml_file(path) or {}) if os.path.exists(path) else {}
    return _FACTS_SCHEMA[path]


def load_copy_schema(path=SCHEMA_PATH):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


class Facts:
    """facts.yaml (B2): факты по id и алиасам, пробелы, запреты. Семантика поиска — как в claims_check.py."""

    def __init__(self, data, path=None):
        self.data = deep_dates(data or {})
        self.path = path
        self.facts = [f for f in self.data.get('facts') or [] if isinstance(f, dict) and f.get('id')]
        self.by_id = {}
        for f in self.facts:
            self.by_id[str(f['id'])] = f
            for a in f.get('aliases') or []:
                self.by_id.setdefault(str(a), f)
        self.missing = [m for m in self.data.get('missing') or [] if isinstance(m, dict)]
        self.missing_by_id = {}
        for m in self.missing:
            self.missing_by_id[str(m.get('id'))] = m
            for a in m.get('aliases') or []:
                self.missing_by_id.setdefault(str(a), m)
        self.never = [n for n in self.data.get('never_claim') or [] if isinstance(n, dict)]

    def resolve(self, ref):
        """(факт | None, пробел | None) по ссылке fact_ids: «x», «fact:x», алиас; «missing:x» → пробел."""
        r = str(ref).strip()
        if r.startswith('missing:'):
            return None, self.missing_by_id.get(r[8:])
        r = r[5:] if r.startswith('fact:') else r
        f = self.by_id.get(r)
        if f is not None:
            return f, None
        return None, self.missing_by_id.get(r)


def load_facts(path):
    if not path:
        return None
    data = load_yaml_file(path) or {}
    if not isinstance(data, dict) or 'facts' not in data:
        raise SystemExit(f'{path}: не facts.yaml (нет ключа facts); facts.md kimi — сначала claims_check.py import-kimi')
    return Facts(data, path)


def claim_class_info():
    return {c['id']: c for c in load_facts_schema().get('x-claim-classes') or [] if isinstance(c, dict)}


_CC = {}


def claims_module():
    """claims_check.py как модуль (только для фильтра публикации фактов при экспорте — та же семантика, что у сверки);
    None — файла нет или он не импортируется (тогда работает свой фильтр по x-kimi-map)."""
    if 'm' not in _CC:
        _CC['m'] = None
        if os.path.exists(CLAIMS_CHECK):
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location('claims_check_for_copydeck', CLAIMS_CHECK)
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                _CC['m'] = m
            except Exception as e:  # noqa: BLE001
                _CC['err'] = f'{type(e).__name__}: {e}'
    return _CC['m']


def own_publish_issues(f, today, cls_info=None):
    """Свой фильтр публикации по x-kimi-map facts.schema.yaml (запасной путь, если claims_check.py не импортируется)."""
    cls_info = cls_info if cls_info is not None else claim_class_info()
    out = []
    ver = (f.get('verification') or {}).get('status')
    classes = [c for c in f.get('claim_class') or []]
    needs_doc = any((cls_info.get(c) or {}).get('needs_document') for c in classes)
    if ver == 'unverified' or ver is None:
        out.append('verification: unverified')
    elif ver == 'stated' and needs_doc:
        out.append('verification: stated, а класс требует документа')
    perm = f.get('permission') or {}
    if perm.get('status') not in ('granted', 'not-required'):
        out.append(f'permission: {perm.get("status") or "нет"}')
    if perm.get('withdrawn'):
        out.append('разрешение отозвано')
    if perm.get('until') and date_end(perm['until']) < today:
        out.append(f'срок разрешения истёк {perm["until"]}')
    if (f.get('source') or {}).get('derivation') == 'inferred':
        out.append('derivation: inferred (вывод агента, а не факт)')
    until = (f.get('valid') or {}).get('until')
    if until and date_end(until) < today:
        out.append(f'истёк: valid.until {until}')
    review = ((f.get('legal') or {}).get('review') or {}).get('status')
    if review in ('required', 'rejected') or (any((cls_info.get(c) or {}).get('legal') == 'required' for c in classes)
                                              and review not in ('approved', 'not-needed')):
        out.append(f'legal.review: {review or "нет"} для класса с legal: required')
    return out


def publish_issues(f, today, facts=None):
    """Почему факт нельзя выгружать в Facts пакета kimi: [] — можно. Основа — claims_check.publishable_issues (error и
    COPY-F-UNVERIFIED любого уровня: x-kimi-map пускает «со слов» только для классов без needs_document); без модуля —
    свой фильтр."""
    m = claims_module()
    if m is not None and facts is not None:
        try:
            cf = m.Facts(facts.data, m.load_schema(), True)
            y, mo, d = (int(x) for x in today.split('-'))
            res = m.publishable_issues(f, cf, dt.date(y, mo, d))
            return [f'{rule}: {msg}' for lvl, rule, msg, _fix in res if lvl == 'error' or rule == 'COPY-F-UNVERIFIED']
        except Exception as e:  # noqa: BLE001
            _CC['err'] = f'publishable_issues: {type(e).__name__}: {e}'
    return own_publish_issues(f, today)


# ============================================================================================ схема: проверка подмножества
class SubsetValidator:
    """Проверка JSON Schema 2020-12 на подмножестве, которым написана copy-deck.schema.json: type, required,
    properties, patternProperties, additionalProperties, enum, const, pattern, minLength, minimum, minItems, maxItems,
    uniqueItems, items, $ref (#/$defs), allOf, anyOf, oneOf, булевы схемы. Нужна, когда jsonschema не установлен
    (системный python3); --selftest сверяет её с jsonschema на тех же примерах."""

    TYPES = {'object': dict, 'array': list, 'string': str, 'boolean': bool, 'null': type(None)}

    def __init__(self, schema):
        self.root = schema

    def _ref(self, ref):
        if not ref.startswith('#/'):
            raise ValueError(f'внешняя $ref не поддержана: {ref}')
        node = self.root
        for part in ref[2:].split('/'):
            node = node[part]
        return node

    def _type_ok(self, t, x):
        if t == 'integer':
            return isinstance(x, int) and not isinstance(x, bool)
        if t == 'number':
            return isinstance(x, (int, float)) and not isinstance(x, bool)
        return isinstance(x, self.TYPES[t])

    def errors(self, x, schema=None, path=''):
        schema = self.root if schema is None else schema
        out = []
        if schema is True:
            return out
        if schema is False:
            return [(path, 'поле не допускается схемой')]
        if '$ref' in schema:
            out += self.errors(x, self._ref(schema['$ref']), path)
        for sub in schema.get('allOf') or []:
            out += self.errors(x, sub, path)
        if 'anyOf' in schema and not any(not self.errors(x, s, path) for s in schema['anyOf']):
            out.append((path, 'не подходит ни один из вариантов anyOf: ' + '; '.join(
                json.dumps(s.get('required', s), ensure_ascii=False) for s in schema['anyOf'])))
        if 'oneOf' in schema and sum(1 for s in schema['oneOf'] if not self.errors(x, s, path)) != 1:
            out.append((path, 'должен подходить ровно один вариант oneOf'))
        t = schema.get('type')
        if t:
            ts = t if isinstance(t, list) else [t]
            if not any(self._type_ok(tt, x) for tt in ts):
                return out + [(path, f'ожидался тип {"/".join(ts)}, получено {type(x).__name__}')]
        if 'const' in schema and x != schema['const']:
            out.append((path, f'значение должно быть {schema["const"]!r}'))
        if 'enum' in schema and x not in schema['enum']:
            out.append((path, f'значение {x!r} не из списка {schema["enum"]}'))
        if isinstance(x, str):
            if 'pattern' in schema and not re.search(schema['pattern'], x):
                out.append((path, f'значение {x!r} не соответствует шаблону {schema["pattern"]}'))
            if 'minLength' in schema and len(x) < schema['minLength']:
                out.append((path, f'строка короче {schema["minLength"]}'))
        if isinstance(x, (int, float)) and not isinstance(x, bool) and 'minimum' in schema and x < schema['minimum']:
            out.append((path, f'значение меньше {schema["minimum"]}'))
        if isinstance(x, list):
            if 'minItems' in schema and len(x) < schema['minItems']:
                out.append((path, f'элементов меньше {schema["minItems"]}'))
            if 'maxItems' in schema and len(x) > schema['maxItems']:
                out.append((path, f'элементов больше {schema["maxItems"]}'))
            if schema.get('uniqueItems'):
                seen = []
                for it in x:
                    k = json.dumps(it, sort_keys=True, ensure_ascii=False, default=str)
                    if k in seen:
                        out.append((path, f'повтор элемента {it!r}'))
                    seen.append(k)
            if 'items' in schema:
                for i, it in enumerate(x):
                    out += self.errors(it, schema['items'], f'{path}[{i}]')
        if isinstance(x, dict):
            for r in schema.get('required') or []:
                if r not in x:
                    out.append((path, f'нет обязательного поля «{r}»'))
            props = schema.get('properties') or {}
            pprops = schema.get('patternProperties') or {}
            for k, v in x.items():
                sub = f'{path}.{k}' if path else str(k)
                matched = False
                if k in props:
                    matched = True
                    out += self.errors(v, props[k], sub)
                for pat, ps in pprops.items():
                    if re.search(pat, str(k)):
                        matched = True
                        out += self.errors(v, ps, sub)
                if not matched and 'additionalProperties' in schema:
                    ap = schema['additionalProperties']
                    if ap is False:
                        out.append((sub, f'неизвестное поле «{k}»'))
                    elif isinstance(ap, dict):
                        out += self.errors(v, ap, sub)
        return out


def schema_errors(data, schema, use_jsonschema=True):
    """[(путь, сообщение)] и какой проверщик работал."""
    if use_jsonschema:
        try:
            import jsonschema  # noqa: F401
            from jsonschema import Draft202012Validator
            v = Draft202012Validator(schema)
            out = []
            for e in sorted(v.iter_errors(data), key=lambda e: [str(p) for p in e.absolute_path]):
                path = ''
                for p in e.absolute_path:
                    path += f'[{p}]' if isinstance(p, int) else (f'.{p}' if path else str(p))
                out.append((path, e.message))
            return out, 'jsonschema'
        except ImportError:
            pass
    return SubsetValidator(schema).errors(data), 'встроенная (подмножество JSON Schema)'


# ============================================================================================ файлы волны 2 (E, F, G, H)
LEN_LANG = {'ru': 'ru', 'en': 'en'}
LEN_UNIT = {'words': 'words', 'word': 'words', 'слова': 'words', 'слов': 'words', 'w': 'words',
            'chars': 'chars', 'char': 'chars', 'characters': 'chars', 'знаки': 'chars', 'знаков': 'chars', 'symbols': 'chars'}


def _len_walk(node, lang='any', unit=None, acc=None):
    """Все границы длины из узла copy-slots.yaml: {(lang, unit): [min, max]}; вьюпорты — самые широкие границы."""
    acc = {} if acc is None else acc
    if isinstance(node, dict):
        for k, v in node.items():
            ks = str(k).lower()
            if ks in LEN_LANG:
                _len_walk(v, LEN_LANG[ks], unit, acc)
            elif ks in LEN_UNIT:
                _len_walk(v, lang, LEN_UNIT[ks], acc)
            elif re.fullmatch(r'(min|max)_(words|chars|characters|знаков|слов)', ks) or re.fullmatch(r'(words|chars)_(min|max)', ks):
                parts = ks.split('_')
                b = parts[0] if parts[0] in ('min', 'max') else parts[1]
                u = LEN_UNIT.get(parts[1] if parts[0] in ('min', 'max') else parts[0], 'chars')
                _len_put(acc, lang, u, b, v)
            elif ks in ('min', 'max') and unit:
                _len_put(acc, lang, unit, ks, v)
            elif ks in ('source', 'note', 'notes', 'target', 'why'):
                continue
            else:
                _len_walk(v, lang, unit, acc)
    elif isinstance(node, list) and unit and node and all(isinstance(x, (int, float)) for x in node):
        _len_put(acc, lang, unit, 'min', node[0])
        _len_put(acc, lang, unit, 'max', node[-1])
    return acc


def _len_put(acc, lang, unit, bound, v):
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return
    cur = acc.setdefault((lang, unit), [None, None])
    if bound == 'min':
        cur[0] = v if cur[0] is None else min(cur[0], v)
    else:
        cur[1] = v if cur[1] is None else max(cur[1], v)


def load_copy_slots(path):
    """copy-slots.yaml (E) в терпимом разборе: {id: {fact_required, section_roles, genre, len}}, renames, заметки.
    Формат E ещё не выпущен (фаза 1 J): берём slot_types | slots | types (список или словарь), длины из length(s)."""
    data = load_yaml_file(path)
    notes, renames, items = [], {}, None
    if isinstance(data, dict):
        for key in ('slot_types', 'slots', 'types'):
            if key in data:
                items = data[key]
                break
        for key in ('renames', 'renamed', 'rename', 'mapping'):
            if isinstance(data.get(key), dict):
                renames.update({str(k): str(v) for k, v in data[key].items()})
    elif isinstance(data, list):
        items = data
    if isinstance(items, dict):
        items = [dict(v, id=k) if isinstance(v, dict) else {'id': k} for k, v in items.items()]
    if not items:
        return None, {}, ['copy-slots.yaml: не найден список типов слотов (slot_types / slots)']
    out = {}
    for it in items:
        if not isinstance(it, dict) or not it.get('id'):
            continue
        lens, lang_specs = {}, {}
        for key in ('length', 'lengths', 'len', 'limits'):
            if key in it:
                lens = _len_walk(it[key])
                node = it[key] if isinstance(it[key], dict) else {}
                for lg in ('ru', 'en'):  # формат E: length.<язык>: words/chars {min, target, max}, hard_*, primary
                    sp = node.get(lg) if isinstance(node.get(lg), dict) else None
                    if not sp:
                        continue
                    ls = {'primary': sp.get('primary') or ('chars' if lg == 'ru' else 'words'),
                          'provisional': bool(sp.get('provisional')), 'n_pages': sp.get('n_pages'), 'source': sp.get('source')}
                    for u in ('words', 'chars'):
                        b = sp.get(u)
                        if isinstance(b, dict):
                            ls[u] = (b.get('min'), b.get('max'))
                        h = sp.get(f'hard_{u}')
                        if isinstance(h, list) and len(h) == 2:
                            ls[f'hard_{u}'] = (h[0], h[1])
                    lang_specs[lg] = ls
                break
        out[str(it['id'])] = {'fact_required': it.get('fact_required'), 'section_roles': it.get('section_roles') or [],
                              'genre': it.get('genre') or it.get('profile'), 'len': lens, 'lang': lang_specs,
                              'exceptions': it.get('exceptions') or [], 'proposal': bool(it.get('proposal'))}
        for old in it.get('aliases') or it.get('replaces') or it.get('renamed_from') or []:
            renames.setdefault(str(old), str(it['id']))
    if not any(v['len'] for v in out.values()):
        notes.append('copy-slots.yaml: длины не распознаны (ожидались length: {ru|en: {words|chars: {min, max}}})')
    extra = {'composites': data.get('composites') if isinstance(data, dict) else None,
             'proposals': [str(x) for x in (data.get('proposals') or [])] if isinstance(data, dict) else []}
    out['__meta__'] = extra
    return out, renames, notes


VOICE_TABOO_KEY = re.compile(r'taboo|табу|dont|не_?говорим|not_say|avoid|banned|never|запрет', re.I)
VOICE_ADDR_KEY = re.compile(r'address|обращени|pronoun', re.I)
RU_FORM = {'vy': 'вы', 'ty': 'ты', 'impersonal': None}


def words_rx(term):
    """Термин в формате words линтера C (06-anti-slop/02 §2.1, F: vocabulary.avoid): «*» — продолжение основы, «ё» = «е»,
    пробел — любые пробелы; границы слова для кириллицы."""
    out, prev_space = [], False
    for ch in term.strip().lower():
        if ch.isspace():
            if not prev_space:
                out.append(r'\s+')
            prev_space = True
            continue
        prev_space = False
        if ch == '*':
            out.append('[0-9a-zа-яё]*')
        elif ch in 'её':
            out.append('[её]')
        else:
            out.append(re.escape(ch))
    tail = '' if term.strip().endswith('*') else '(?![0-9a-zа-яё])'
    return re.compile('(?<![0-9a-zа-яё])' + ''.join(out) + tail, re.I)


def load_voice(path):
    """voice.yaml (F, voice.schema.yaml v1): address.ru_form (vy | ty | impersonal) и exceptions, vocabulary.avoid (термины
    в формате words линтера C, уровень, slot_types, unless), projections.tone_of_voice. Иной формат — терпимый разбор:
    ключи с «обращение» / «avoid», «табу», «не говорим»."""
    data = load_yaml_file(path) or {}
    out = {'taboo': [], 'address': None, 'exceptions': [], 'tone_of_voice': None, 'format': None}
    addr = data.get('address') if isinstance(data.get('address'), dict) else None
    voc = data.get('vocabulary') if isinstance(data.get('vocabulary'), dict) else None
    if addr and 'ru_form' in addr:
        out['format'] = 'F'
        out['address'] = RU_FORM.get(str(addr.get('ru_form')))
        out['exceptions'] = [str(x.get('where')) for x in addr.get('exceptions') or [] if isinstance(x, dict) and x.get('where')]
    if voc and isinstance(voc.get('avoid'), list):
        out['format'] = 'F'
        for t in voc['avoid']:
            if isinstance(t, dict) and t.get('term'):
                out['taboo'].append({'term': str(t['term']), 'lang': t.get('lang') or 'ru', 'level': t.get('level') or 'warning',
                                     'slot_types': t.get('slot_types') or [], 'unless': t.get('unless') or '', 'use_instead': t.get('use_instead') or ''})
            elif isinstance(t, str):
                out['taboo'].append({'term': t, 'lang': 'any', 'level': 'warning', 'slot_types': [], 'unless': '', 'use_instead': ''})
    tov = (data.get('projections') or {}).get('tone_of_voice') if isinstance(data.get('projections'), dict) else None
    out['tone_of_voice'] = tov or (data.get('tone_of_voice') if isinstance(data.get('tone_of_voice'), str) else None)
    if out['format'] == 'F':
        return out
    # терпимый разбор чужой формы
    taboo = []

    def walk(node, key=''):
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, str(k))
        elif isinstance(node, list):
            if VOICE_TABOO_KEY.search(key):
                for x in node:
                    if isinstance(x, str) and 0 < len(x) <= 40:
                        taboo.append(x)
                    elif isinstance(x, dict):
                        for kk in ('term', 'word', 'phrase', 'text'):
                            if isinstance(x.get(kk), str):
                                taboo.append(x[kk])
                                break
            else:
                for x in node:
                    walk(x, key)
        elif isinstance(node, str) and VOICE_ADDR_KEY.search(key) and out['address'] is None:
            low = node.lower()
            out['address'] = 'вы' if re.search(r'(^|[^а-яё])вы([^а-яё]|$)', low) else ('ты' if re.search(r'(^|[^а-яё])ты([^а-яё]|$)', low) else None)
    walk(data)
    out['taboo'] = [{'term': t, 'lang': 'any', 'level': 'warning', 'slot_types': [], 'unless': '', 'use_instead': ''} for t in sorted(set(taboo))]
    out['format'] = 'generic'
    return out


META_KEYS = {'title': 'title', 'meta-title': 'title', 'meta_title': 'title', 'description': 'description',
             'meta-description': 'description', 'meta_description': 'description', 'og-title': 'og_title',
             'og_title': 'og_title', 'og-description': 'og_description', 'og_description': 'og_description'}


def load_meta_rules(path):
    """meta-rules.yaml (G): limits (ориентиры длины по полям и языкам: write [min, max], info_over, warning_over,
    warning_under, words_min) и checks_outside_linter (проверки между полями и страницами: meta-x-…). Правила для
    линтера из того же файла copy_lint.py подхватывает сам (profiles.yaml → external_rules).
    → {'limits': {поле: {язык: {...}}}, 'checks': {id: {...}}, 'format': 'G' | 'generic' | None}."""
    data = load_yaml_file(path) or {}
    out = {'limits': {}, 'checks': {}, 'format': None}
    lim = data.get('limits') if isinstance(data.get('limits'), dict) else {}
    for key, node in lim.items():
        fld = META_KEYS.get(str(key).lower())
        if not fld or not isinstance(node, dict):
            continue
        for lang, spec in node.items():
            if str(lang) in ('ru', 'en') and isinstance(spec, dict):
                keep = {k: v for k, v in spec.items() if k in ('write', 'info_over', 'warning_over', 'warning_under', 'words_min')}
                if keep:
                    out['limits'].setdefault(fld, {})[str(lang)] = keep
    for c in data.get('checks_outside_linter') or []:
        if isinstance(c, dict) and c.get('id'):
            out['checks'][str(c['id'])] = c
    if out['limits'] or out['checks']:
        out['format'] = 'G'
        return out
    # запасной разбор: поле → {min, max} где угодно в файле
    def grab(node):
        if not isinstance(node, dict):
            return
        for k, v in node.items():
            fld = META_KEYS.get(str(k).lower())
            if fld and isinstance(v, dict):
                lens = _len_walk(v, unit='chars')
                for (lang, unit), (a, b) in lens.items():
                    if unit == 'chars':
                        spec = out['limits'].setdefault(fld, {}).setdefault('ru' if lang == 'any' else lang, {})
                        if b is not None:
                            spec['warning_over'] = b
                        if a is not None:
                            spec['warning_under'] = a
            elif isinstance(v, dict) and str(k) != 'rules':
                grab(v)
    grab(data)
    out['format'] = 'generic' if out['limits'] else None
    return out


def _meta_checks(deck, mr, rep, final):
    """Проверки мета между полями и страницами по checks_outside_linter G (id meta-x-…) и ориентиры длины limits G."""
    T = 'validate'
    checks = mr.get('checks') or {}
    lang = (deck.get('lang') or 'ru').split('-')[0]

    def lvl(cid, default):
        return str((checks.get(cid) or {}).get('level') or default)
    titles, descs = {}, {}
    for page in pages_of(deck):
        if (page.get('status') or 'draft') == 'rejected':
            continue
        pid = str(page.get('page_id'))
        meta = page.get('meta') or {}
        published = final or page.get('status') == 'approved'
        t, d = norm_ws(meta.get('title')), norm_ws(meta.get('description'))
        for k, val in (('title', t), ('description', d)):
            if not val:
                rep.add(T, lvl('meta-x-missing', 'error') if published else 'info', 'meta-x-missing', f'{pid}/meta/{k}',
                        f'нет meta.{k}' + ('' if published else ' (черновик: заполнить до утверждения)'), 'G meta-rules.yaml checks_outside_linter; шаблоны — templates.' + str(page.get('page_type') or ''))
        if published and (not norm_ws(meta.get('og_title')) or not norm_ws(meta.get('og_description'))):
            rep.add(T, lvl('meta-x-og-missing', 'warning'), 'meta-x-og-missing', f'{pid}/meta', 'нет og_title или og_description', 'Картинка OG — ai-media 10/01 §7; теги — site H.')
        if t:
            titles.setdefault(t.lower(), []).append(pid)
        if d:
            descs.setdefault(d.lower(), []).append(pid)
        if t and d and (d.lower() == t.lower() or d.lower().startswith(t.lower())):
            rep.add(T, lvl('meta-x-desc-equals-title', 'warning'), 'meta-x-desc-equals-title', f'{pid}/meta/description', 'description совпадает с title или начинается с него', 'description — что внутри страницы + факт.')
        for k, _st in META_FIELDS:
            val = norm_ws(meta.get(k))
            if len(words(val)) >= 3:
                share = cyr_share(val)
                if (lang == 'ru' and share < 0.3) or (lang == 'en' and share > 0.3):
                    rep.add(T, lvl('meta-x-lang-mismatch', 'warning'), 'meta-x-lang-mismatch', f'{pid}/meta/{k}', f'язык мета не совпадает с языком страницы ({lang})', '')
        for fld, bylang in (mr.get('limits') or {}).items():
            val = norm_ws(meta.get(fld))
            spec = bylang.get(lang) or bylang.get('ru') or {}
            if not val or not spec:
                continue
            n = len(val)
            where = f'{pid}/meta/{fld}'
            if spec.get('warning_over') is not None and n > spec['warning_over']:
                rep.add(T, 'warning', 'COPY-D-META-LEN', where, f'{n} знаков > {spec["warning_over"]} (limits G)', 'Главное — в первых 55 знаках; сократите.')
            elif spec.get('info_over') is not None and n > spec['info_over']:
                rep.add(T, 'info', 'COPY-D-META-LEN', where, f'{n} знаков > {spec["info_over"]} (limits G): хвост обрежется в выдаче', '')
            if spec.get('warning_under') is not None and n < spec['warning_under']:
                rep.add(T, 'warning', 'COPY-D-META-LEN', where, f'{n} знаков < {spec["warning_under"]} (limits G)', '')
            w = spec.get('write')
            if isinstance(w, list) and len(w) == 2 and not (w[0] <= n <= w[1]):
                rep.add(T, 'info', 'COPY-D-META-LEN', where, f'{n} знаков вне ориентира генерации {w[0]}–{w[1]} (limits G)', '')
            if spec.get('words_min') and len(words(val)) < spec['words_min']:
                rep.add(T, 'info', 'COPY-D-META-LEN', where, f'слов меньше {spec["words_min"]} (limits G)', '')
    for (dups, cid, default, fld) in ((titles, 'meta-x-duplicate-title', 'error', 'title'), (descs, 'meta-x-duplicate-description', 'warning', 'description')):
        for _txt, pids in dups.items():
            for pid in pids[1:]:
                rep.add(T, lvl(cid, default), cid, f'{pid}/meta/{fld}', f'meta.{fld} совпадает со страницей {pids[0]}', 'У каждой страницы своя мета.')


def load_claims_rules_ids(path):
    data = load_yaml_file(path) or {}
    return {str(r.get('id')) for r in data.get('rules') or [] if isinstance(r, dict) and r.get('id')}


# ============================================================================================ validate
def effective_genre(deck, page, section, slot_type, lint_profile, vocab):
    """Жанр слота (x-claims-map): lint.profile-жанр → section.genre → жанр типа слота, если он единственный →
    page.genre → жанр page_type по словарю → landing. Возвращает (жанр, профиль-не-жанр или '')."""
    prof = str(lint_profile or '')
    if prof in GENRES:
        return prof, ''
    if section and section.get('genre') in GENRES:
        return section['genre'], prof
    st = (vocab or {}).get('slot_types', {}).get(slot_type or '') if vocab else None
    if slot_type and (slot_type.startswith(('meta-', 'og-'))):
        return 'meta', prof
    if slot_type and slot_type.startswith('email-'):
        return 'email-form', prof
    if st and isinstance(st.get('genres'), list) and len(st['genres']) == 1:
        return st['genres'][0], prof
    if page and page.get('genre') in GENRES:
        return page['genre'], prof
    pt = (vocab or {}).get('page_types', {}).get((page or {}).get('page_type')) if vocab else None
    if pt in GENRES:
        return pt, prof
    return 'landing', prof


def meta_variant_for(meta, key):
    """Вариант meta.variants.<поле>, совпадающий с выбранным текстом meta.<поле> (или None)."""
    mv = meta.get('variants') if isinstance(meta.get('variants'), dict) else {}
    cur = norm_ws(meta.get(key))
    return next((v for v in mv.get(key) or [] if isinstance(v, dict) and cur and norm_ws(v.get('text')) == cur), None)


def meta_alternatives(meta, key):
    """Живые альтернативы мета (G: 2–3 варианта title): не rejected, с текстом, не равные выбранному meta.<поле>."""
    mv = meta.get('variants') if isinstance(meta.get('variants'), dict) else {}
    cur = norm_ws(meta.get(key))
    return [v for v in mv.get(key) or [] if isinstance(v, dict) and v.get('status') != 'rejected'
            and norm_ws(v.get('text')) and norm_ws(v.get('text')) != cur]


def slot_alternatives(slot):
    """Живые варианты слота, кроме проверяемого как текст слота (main_variant): для --all-variants."""
    ch = main_variant(slot)
    return [v for v in variants_of(slot) if v is not ch and v.get('status') != 'rejected' and str(v.get('text') or '').strip()]


def text_units(deck, page, include_meta=True, all_variants=False):
    """Все тексты страницы, которые идут на страницу или в пакет: слоты, обещание (своё), мета, OG-шаблон.
    → [{path, kind, slot_type, text, variant, chosen, slot, section, fact_ids}]; kind: slot | promise | meta | og;
    chosen — выбранный текст (при all_variants к нему добавляются живые альтернативы с chosen: False);
    fact_ids — свои факты варианта, иначе факты слота (variant_fact_ids)."""
    out = []
    pid = page.get('page_id')
    for s in sections_of(page):
        for sl in slots_of(s):
            ch = main_variant(sl)
            vs = ([ch] if ch else []) + (slot_alternatives(sl) if all_variants else [])
            for v in vs:
                out.append({'path': f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}", 'kind': 'slot',
                            'slot_type': sl.get('slot_type'), 'text': str(v.get('text') or ''), 'variant': v.get('id'),
                            'chosen': v is ch, 'slot': sl, 'section': s, 'fact_ids': variant_fact_ids(sl, v)})
    pr = page.get('promise')
    if isinstance(pr, dict) and not pr.get('from'):
        ch = main_variant(pr)
        vs = ([ch] if ch else []) + (slot_alternatives(pr) if all_variants else [])
        for v in vs:
            out.append({'path': f'{pid}/promise', 'kind': 'promise', 'slot_type': 'subheadline',
                        'text': str(v.get('text') or ''), 'variant': v.get('id'), 'chosen': v is ch, 'slot': pr,
                        'section': None, 'fact_ids': variant_fact_ids(pr, v)})
    if include_meta:
        meta = page.get('meta') or {}
        for k, st in META_FIELDS:
            if meta.get(k):
                out.append({'path': f'{pid}/meta/{k}', 'kind': 'meta', 'slot_type': st, 'text': str(meta[k]),
                            'variant': 'meta', 'chosen': True, 'slot': None, 'section': None,
                            'fact_ids': variant_fact_ids(meta, meta_variant_for(meta, k))})
            if all_variants:  # альтернативы мета (G: 2–3 варианта title) тоже показываются людям в тесте
                for v in meta_alternatives(meta, k):
                    out.append({'path': f'{pid}/meta/{k}', 'kind': 'meta', 'slot_type': st, 'text': str(v['text']),
                                'variant': str(v.get('id')), 'chosen': False, 'slot': None, 'section': None,
                                'fact_ids': variant_fact_ids(meta, v)})
        og = page.get('og_template') or {}
        for k, st in OG_TEMPLATE_FIELDS:
            if og.get(k):
                out.append({'path': f'{pid}/og_template/{k}', 'kind': 'og', 'slot_type': st, 'text': str(og[k]),
                            'variant': 'a', 'chosen': True, 'slot': None, 'section': None, 'fact_ids': og.get('fact_ids') or []})
    return out


class Ctx:
    """Окружение проверки: пути к файлам (переопределяются в --selftest), загруженные словари и правила."""

    def __init__(self, deck_path=None, facts=None, today=None, vocab_path=VOCAB_PATH, copy_slots_path=None,
                 voice_schema_path=VOICE_SCHEMA_PATH, meta_rules_path=META_RULES_PATH, claims_rules_path=CLAIMS_RULES_PATH,
                 schema_path=SCHEMA_PATH):
        self.deck_path = deck_path
        self.facts = facts
        self.today = today or today_iso()
        self.schema = load_copy_schema(schema_path)
        self.vocab = load_vocab(vocab_path, self.schema)
        self.copy_slots_path = copy_slots_path
        self.voice_schema_path = voice_schema_path
        self.meta_rules_path = meta_rules_path
        self.claims_rules_path = claims_rules_path
        self.final = False
        self.meta_rules = None
        if meta_rules_path and os.path.exists(meta_rules_path):
            try:
                self.meta_rules = load_meta_rules(meta_rules_path)
            except Exception as e:  # noqa: BLE001
                self.meta_rules = {'limits': {}, 'checks': {}, 'format': None, 'error': str(e)}


def validate(data, ctx, rep=None, final=False, use_jsonschema=True, fresh=None, skip_fact_checks=False):
    """Проверка формата и смысловых правил copy deck. fresh — свежие итоги claims и lint по путям (из check)."""
    rep = rep or Report()
    T = 'validate'
    ctx.final = final
    found_dates = []
    data = deep_dates(data, found=found_dates)
    if found_dates:
        rep.add(T, 'info', 'COPY-D-DATE-UNQUOTED', found_dates[0], f'даты без кавычек ({len(found_dates)}): YAML читает их как дату',
                'Пишите даты строкой в кавычках: date: "2026-09-24".')
    if not isinstance(data, dict) or not isinstance(data.get('copy_deck'), dict):
        if isinstance(data, dict) and 'pages' in data:
            rep.add(T, 'error', 'COPY-D-ROOT', '—', 'нет корня copy_deck: страницы лежат на верхнем уровне',
                    'Оберните документ в copy_deck: {…} (формат v0 и v1).')
        else:
            rep.add(T, 'error', 'COPY-D-ROOT', '—', 'это не copy deck: нет ключа copy_deck', 'Формат — 10-templates-recipes/copy-deck.schema.json.')
        return rep
    # ---- схема
    errs, engine = schema_errors(data, ctx.schema, use_jsonschema)
    rep.tools['validate'] = {'schema_engine': engine}
    for path, msg in errs[:200]:
        rep.add(T, 'error', 'COPY-D-SCHEMA', path.replace('copy_deck.', '') or '—', msg,
                'Поля и типы — copy-deck.schema.json; поля v0 не переименовывать (T2).')
    deck = data['copy_deck']
    v0 = deck.get('version') == 0
    if v0:
        rep.add(T, 'info', 'COPY-D-V0', '—', 'copy deck v0: требования статусов v1 — предупреждениями',
                'python3 99-raw/tools/copydeck.py upgrade DECK -o DECK-v1.yaml')

    def sev(level):  # требования статусов v1 к deck v0 — мягче
        return 'warning' if (v0 and level == 'error') else level

    vocab = ctx.vocab
    if vocab is None:
        rep.add(T, 'warning', 'COPY-D-RULES-MISSING', '—', f'временный словарь не найден: {VOCAB_PATH}', 'Типы страниц, секций и слотов не проверены.')
    # ---- id, ссылки, статусы
    page_ids = set()
    for page in pages_of(deck):
        pid = str(page.get('page_id'))
        if pid in page_ids:
            rep.add(T, 'error', 'COPY-D-ID-DUP', pid, f'повтор page_id «{pid}»', 'id страницы уникален в deck.')
        page_ids.add(pid)
        _validate_page(deck, page, ctx, rep, sev, final, fresh, vocab)
    # ---- факты
    facts = ctx.facts
    if facts is None:
        used = [p for _pg, _s, sl, p in iter_slots(deck) if sl.get('fact_ids')]
        if used:
            rep.add(T, 'error' if not v0 else 'warning', 'COPY-D-FACTS-MISSING', used[0],
                    f'в слотах есть fact_ids ({len(used)}), а facts.yaml не найден (facts_ref: {deck.get("facts_ref")!r})',
                    'Укажите facts_ref от папки copy deck или --facts.')
        elif any(PLACEHOLDER_RX.search(u['text']) for pg in pages_of(deck) for u in text_units(deck, pg)):
            rep.add(T, 'info', 'COPY-D-FACTS-MISSING', '—', 'facts.yaml не подключён: пробелы [PLACEHOLDER] не сверены с missing[]', '')
    else:  # ссылки и публикуемость фактов check берёт у claims_check.py; пробелы (missing_ids, fallback B2) — всегда здесь
        _validate_facts(deck, ctx, rep, sev, refs_and_publish=not skip_fact_checks)
    _validate_wave2(deck, ctx, rep)
    _validate_language(deck, ctx, rep)
    return rep


def _status_of(v):
    return (v or {}).get('status') or 'draft'


def _validate_page(deck, page, ctx, rep, sev, final, fresh, vocab):
    T = 'validate'
    pid = str(page.get('page_id'))
    ptype = page.get('page_type')
    if vocab and ptype and ptype not in vocab['page_types']:
        rep.add(T, 'error', 'COPY-D-VOCAB', pid, f'page_type «{ptype}» нет во временном словаре', 'Возьмите id из 99-raw/notes/temp-vocabulary-v0.yaml (page_types) или заведите предложение к словарю.')
    pstatus = page.get('status') or 'draft'
    rules = (ctx.schema.get('x-status-rules') or {})
    prules = (rules.get('page') or {}).get(pstatus, {})
    for f in prules.get('page_requires') or []:
        if f not in page or page.get(f) in (None, '', [], {}):
            rep.add(T, sev('error'), 'COPY-D-STATUS', pid, f'страница {pstatus}: нет поля «{f}»', 'Требования статусов — x-status-rules схемы.')
    if pstatus == 'rejected':
        return
    sec_ids = set()
    chosen_status = []
    for s in sections_of(page):
        sid = str(s.get('section_id'))
        if sid in sec_ids:
            rep.add(T, 'error', 'COPY-D-ID-DUP', f'{pid}/{sid}', f'повтор section_id «{sid}» на странице', 'id секции уникален на странице (= site.sections[].id kimi).')
        sec_ids.add(sid)
        role = s.get('section_role')
        if vocab:
            if role and role not in vocab['section_roles']:
                lvl = 'info' if role in vocab['proposals']['section_roles'] else 'error'
                rep.add(T, lvl, 'COPY-D-VOCAB', f'{pid}/{sid}', f'section_role «{role}» ' + ('— предложение к словарю' if lvl == 'info' else 'нет во временном словаре'),
                        'Роли секций — temp-vocabulary-v0.yaml section_roles.')
            if not role:
                guess = s.get('block') if s.get('block') in vocab['section_roles'] else KIMI_SECTION_ROLE.get(sid, sid if sid in vocab['section_roles'] else None)
                rep.add(T, 'info', 'COPY-D-ROLE', f'{pid}/{sid}', 'нет section_role' + (f' (по block/id — «{guess}»)' if guess else ''),
                        'Проставьте section_role (claims_check.py берёт роль секции для use.section_roles фактов).')
        if not s.get('message') and (role or '') not in ('footer', 'contacts'):
            rep.add(T, 'info', 'COPY-D-MESSAGE', f'{pid}/{sid}', 'у секции нет message (опоры иерархии B1)', 'message — одна фраза из иерархии сообщений (x-copy-deck-map B1).')
        slot_ids = set()
        faq_q = faq_a = 0
        for sl in slots_of(s):
            slid = str(sl.get('slot_id'))
            path = f'{pid}/{sid}/{slid}'
            if slid in slot_ids:
                rep.add(T, 'error', 'COPY-D-ID-DUP', path, f'повтор slot_id «{slid}» в секции', 'id слота уникален в секции (ключ [slot_id] в copy.md).')
            slot_ids.add(slid)
            st = sl.get('slot_type')
            faq_q += st == 'faq-q'
            faq_a += st == 'faq-a'
            if vocab and st and st not in vocab['slot_types']:
                if st in vocab['proposals']['slot_types']:
                    rep.add(T, 'info', 'COPY-D-VOCAB', path, f'slot_type «{st}» — предложение к временному словарю', '')
                else:
                    rep.add(T, 'error', 'COPY-D-VOCAB', path, f'slot_type «{st}» нет во временном словаре', 'Типы слотов — temp-vocabulary-v0.yaml (после E — copy-slots.yaml).')
            v = _validate_slot(deck, page, s, sl, path, ctx, rep, sev, final, fresh, pstatus)
            chosen_status.append((path, _status_of(v) if v else None))
        if faq_q != faq_a and faq_q and faq_a:
            rep.add(T, 'warning', 'COPY-D-FAQ-PAIRS', f'{pid}/{sid}', f'вопросов FAQ {faq_q}, ответов {faq_a}', 'У каждого faq-q — свой faq-a (group: q1…).')
    # ---- обещание
    ptext, pv, psrc, pr = promise_info(deck, page)
    genre = effective_genre(deck, page, None, None, None, vocab)[0]
    if pr is None:
        if genre == 'landing':
            rep.add(T, 'warning', 'COPY-D-PROMISE', pid, 'нет обещания первого экрана (promise)',
                    'Заведите promise (или promise.from: <page>/hero/<slot>): оно уходит в product.goal kimi → «Promise:» в TASK и сверяется как текст страницы; export-kimi без него откажет.')
    elif pr.get('from') and ptext is None:
        rep.add(T, 'error', 'COPY-D-PROMISE', f'{pid}/promise', f'promise.from «{pr.get("from")}» не найден или у слота нет выбранного варианта', 'Ссылка — <page_id>/<section_id>/<slot_id> этой страницы.')
    elif not pr.get('from'):
        v = _validate_slot(deck, page, None, pr, f'{pid}/promise', ctx, rep, sev, final, fresh, pstatus, is_promise=True)
        chosen_status.append((f'{pid}/promise', _status_of(v) if v else None))
    # ---- главная кнопка
    cpath, ctext = primary_cta(deck, page)
    if page.get('cta_primary') and ctext is None:
        rep.add(T, 'error', 'COPY-D-CTA', pid, f'cta_primary «{page.get("cta_primary")}» не найден', 'Ссылка — <page>/<section>/<slot> слота cta-label.')
    elif cpath is None and genre in ('landing', 'site-page'):
        rep.add(T, 'info', 'COPY-D-CTA', pid, 'на странице нет слота cta-label', 'site.cta.label пакета kimi останется пустым.')
    # ---- мета (без правил G; с ними — meta-x-… в _meta_checks)
    meta = page.get('meta')
    need_meta = final or pstatus == 'approved'
    if isinstance(meta, dict) and ctx.meta_rules is None:
        for k in ('title', 'description'):
            if need_meta and not str(meta.get(k) or '').strip():
                rep.add(T, 'error', 'COPY-D-META', f'{pid}/meta/{k}', f'пустое meta.{k} у страницы {pstatus}', 'Мета — часть copy deck (правила — G, meta-rules.yaml).')
        for k in ('og_title', 'og_description'):
            if need_meta and not str(meta.get(k) or '').strip():
                rep.add(T, 'warning', 'COPY-D-META', f'{pid}/meta/{k}', f'пустое meta.{k}', 'Без og:* превью ссылки соберёт площадка сама.')
    elif need_meta and not isinstance(meta, dict):
        rep.add(T, 'error', 'COPY-D-META', pid, 'нет блока meta', 'meta: {title, description, og_title, og_description}.')
    if isinstance(meta, dict) and need_meta:
        for k, _st in META_FIELDS:
            if PLACEHOLDER_RX.search(str(meta.get(k) or '')):
                rep.add(T, 'error', 'COPY-D-PLACEHOLDER', f'{pid}/meta/{k}', 'заглушка в мета опубликованной страницы', 'Закройте пробел в facts.yaml или перепишите без факта.')
    # ---- варианты мета, пересмотр, бриф статьи (предложения G)
    if isinstance(meta, dict):
        mv = meta.get('variants') if isinstance(meta.get('variants'), dict) else {}
        for k, vs in mv.items():
            vs = [v for v in vs or [] if isinstance(v, dict)]
            ids = [str(v.get('id')) for v in vs]
            for d in sorted({x for x in ids if ids.count(x) > 1}):
                rep.add(T, 'error', 'COPY-D-ID-DUP', f'{pid}/meta/{k}', f'повтор id варианта мета «{d}»', '')
            if meta.get(k) and not any(v.get('text') == meta.get(k) for v in vs):
                rep.add(T, 'info', 'COPY-D-META-VARIANTS', f'{pid}/meta/{k}', f'выбранный meta.{k} не совпадает ни с одним вариантом meta.variants.{k}', 'Выбранный текст — один из вариантов (или добавьте его в variants).')
            for v in vs:
                if v.get('status') == 'rejected' and not v.get('reason'):
                    rep.add(T, sev('error'), 'COPY-D-REJECTED', f"{pid}/meta/{k}/{v.get('id')}", 'отклонённый вариант мета без reason', '')
        n_title = len([v for v in mv.get('title') or [] if isinstance(v, dict) and v.get('status') != 'rejected'])
        g = effective_genre(deck, page, None, None, None, vocab)[0]
        if meta.get('title') and n_title < 2 and (g == 'article' or ptype in ('service-page', 'seo-landing-page')) and pstatus in ('checked', 'approved'):
            rep.add(T, 'info', 'COPY-D-META-VARIANTS', f'{pid}/meta/title', 'один вариант title у страницы из поиска', 'G 07/02 §4.3: 2–3 варианта title с планом теста (meta.variants.title, meta.test_plan).')
        if n_title >= 2 and not meta.get('test_plan'):
            rep.add(T, 'info', 'COPY-D-META-VARIANTS', f'{pid}/meta/title', f'вариантов title {n_title}, а плана теста нет', 'meta.test_plan: где и сколько недель мерить (Вебмастер, Search Console).')
        rb = meta.get('review_by')
        if rb and date_end(rb) < ctx.today:
            rep.add(T, 'warning', 'COPY-D-META-REVIEW', f'{pid}/meta', f'пора пересмотреть мета (review_by {rb})', 'G: title и description устаревают; пересмотр раз в 12–24 месяца.')
    art = page.get('article')
    if isinstance(art, dict) and ctx.facts is not None:
        refs = [('author', art.get('author'))] + [('experts', x) for x in art.get('experts') or []] + \
               [('unique_angle', x) for x in ((art.get('unique_angle') or {}).get('fact_ids') or [])]
        for what, ref in refs:
            if not ref:
                continue
            f, m = ctx.facts.resolve(ref)
            if f is None:
                rep.add(T, 'error', 'COPY-D-FACT-REF', f'{pid}/article/{what}', f'нет факта «{ref}»' + (' (это пробел missing)' if m else ''), 'Автор и эксперты — факты вида person с разрешением (COPY-GEO-19).')
            elif what in ('author', 'experts') and f.get('kind') != 'person':
                rep.add(T, 'warning', 'COPY-D-ARTICLE', f'{pid}/article/{what}', f'fact:{f["id"]} вида {f.get("kind")}, а не person', '')
    g = effective_genre(deck, page, None, None, None, vocab)[0]
    if g == 'article' and not isinstance(art, dict) and pstatus in ('checked', 'approved'):
        rep.add(T, 'info', 'COPY-D-ARTICLE', pid, 'у статьи нет полей брифа article (интент, запрос, угол, автор)', 'G 07/02 §1.1.')
    # ---- статус страницы из статусов выбранных вариантов
    if pstatus in ('checked', 'approved'):
        need = 'approved' if pstatus == 'approved' else 'checked'
        low = [p for p, st in chosen_status if st is None or STATUS_RANK.get(st, 0) < STATUS_RANK[need]]
        if low:
            rep.add(T, sev('error'), 'COPY-D-STATUS', pid, f'страница {pstatus}, но {len(low)} выбранных текстов ниже {need}: {", ".join(low[:5])}',
                    'Статус страницы не выше статуса её слотов.')
    if final and pstatus != 'approved':
        rep.add(T, 'error', 'COPY-D-FINAL', pid, f'--final: страница в статусе {pstatus}, а не approved', 'Публикуется только утверждённая страница.')


def _validate_slot(deck, page, section, sl, path, ctx, rep, sev, final, fresh, pstatus, is_promise=False):
    T = 'validate'
    vs = variants_of(sl)
    vids = [str(v.get('id')) for v in vs]
    for d in sorted({x for x in vids if vids.count(x) > 1}):
        rep.add(T, 'error', 'COPY-D-ID-DUP', path, f'повтор id варианта «{d}»', 'id варианта уникален в слоте.')
    ch = sl.get('chosen')
    v = chosen_variant(sl)
    if ch is not None and v is None:
        rep.add(T, 'error', 'COPY-D-CHOSEN', path, f'chosen «{ch}» — такого варианта нет', 'chosen = id одного из variants.')
    if ch is None and len(vs) > 1:
        rep.add(T, 'warning', 'COPY-D-CHOSEN', path, f'вариантов {len(vs)}, выбор не сделан (chosen)', 'Выберите вариант (selection: попарно, редактор, заказчик); до выбора сверяется первый.')
    for x in vs:
        if x.get('status') == 'rejected':
            if not x.get('reason'):
                rep.add(T, sev('error'), 'COPY-D-REJECTED', f"{path}/{x.get('id')}", 'отклонённый вариант без reason', 'Причина нужна цепочке I и парам «до / после».')
            if v is x:
                rep.add(T, 'error', 'COPY-D-CHOSEN', path, 'выбран отклонённый вариант', 'Выберите другой вариант или верните статус.')
    if v is None:
        return None
    if isinstance(v.get('fact_ids'), list) and set(map(str, v['fact_ids'])) != set(map(str, sl.get('fact_ids') or [])):
        rep.add(T, 'info', 'COPY-D-VARIANT-FACTS', path, f"у выбранного варианта {v.get('id')} свои fact_ids {v['fact_ids']}, у слота — {sl.get('fact_ids') or []}",
                'copydeck сверяет по фактам варианта, а claims_check.py и copy_lint.py на copy deck читают только fact_ids слота: '
                'check --update перенесёт факты выбранного варианта в слот.')
    text = str(v.get('text') or '')
    status = _status_of(v)
    rules = ((ctx.schema.get('x-status-rules') or {}).get('slot') or {}).get(status, {})
    missing_fields = [f for f in rules.get('slot_requires') or [] if f not in sl and not (is_promise and f in ('slot_id', 'slot_type'))]
    if missing_fields:
        rep.add(T, sev('error'), 'COPY-D-STATUS', path, f'текст в статусе {status}: нет полей {", ".join(missing_fields)}',
                'checked и approved пишет copydeck.py check --update (записи lint и claims с text_hash).')
    fr = (fresh or {}).get(path) or {}
    h = text_hash(text)
    for key in ('lint', 'claims'):
        rec = sl.get(key) if isinstance(sl.get(key), dict) else None
        if status in ('checked', 'approved'):
            now = fr.get(key)
            errs = (now.get('errors') - now.get('final_escalated', 0)) if now else (rec or {}).get('errors')
            if errs is None:
                rep.add(T, sev('error'), 'COPY-D-STATUS', path, f'статус {status}: нет итога {key} (errors)', f'Запустите copydeck.py check --update.')
            elif errs > 0:
                rep.add(T, sev('error'), 'COPY-D-STATUS', path, f'статус {status}, а {key}: {errs} error' + (' (свежая проверка)' if now else ' (запись)'),
                        'Исправьте текст или верните статус draft.')
            if rec and rec.get('text_hash') and rec['text_hash'] != h:
                rep.add(T, sev('error'), 'COPY-D-HASH', path, f'текст изменён после проверки {key} (text_hash {rec["text_hash"]} ≠ {h})',
                        'Статус checked/approved недействителен: перепроверьте (check --update) или верните draft.')
            elif rec and not rec.get('text_hash') and not (deck.get('version') == 0):
                rep.add(T, 'warning', 'COPY-D-HASH', path, f'в записи {key} нет text_hash: не видно, тот ли текст проверяли', 'copydeck.py check --update пишет text_hash.')
        if rec and fr.get(key) and rec.get('errors') is not None and rec.get('errors') != fr[key].get('errors'):
            rep.add(T, 'info', 'COPY-D-RECORD', path, f'запись {key} устарела: в файле {rec.get("errors")} error, сейчас {fr[key].get("errors")}', 'copydeck.py check --update OUT')
    if status == 'approved':
        rv = v.get('review') if isinstance(v.get('review'), dict) else None
        if rv and str(rv.get('by', '')).startswith('copydeck'):
            rv = None  # запись утилиты (check --promote) — не утверждение человеком
        if not (rv and rv.get('by') and rv.get('at')) and not isinstance(page.get('approval'), dict):
            rep.add(T, sev('error'), 'COPY-D-STATUS', path, 'approved без review (by, at) у варианта и без approval страницы', 'Утверждает человек: review: {by: …, at: …}.')
    if (status == 'approved' or final) and PLACEHOLDER_RX.search(text):
        rep.add(T, 'error', 'COPY-D-PLACEHOLDER', path, f'заглушка в тексте статуса {status}' + (' (--final)' if final else ''), 'Закройте пробел в facts.yaml или перепишите без утверждения (fallback пробела).')
    _validate_text(deck, page, section, sl, path, text, v, ctx, rep)
    return v


def _validate_text(deck, page, section, sl, path, text, v, ctx, rep):
    T = 'validate'
    st = sl.get('slot_type') or ''
    bad = BAD_PLACEHOLDER_RX.search(text)
    if bad:
        rep.add(T, 'error', 'COPY-D-PLACEHOLDER-FORM', path, f'заглушка не по формату: «{bad.group(0)}»', 'Только [PLACEHOLDER: что именно] (B2, kimi).')
    for tok in ('{{', '{#', '<UNSET'):
        if tok in text:
            rep.add(T, 'error', 'COPY-D-KIMI-TOKEN', path, f'в тексте «{tok}» — сборщик kimi сочтёт это остатком шаблона', 'Уберите фигурные скобки из текста.')
    if not text.strip() and st not in ('image-alt',):
        rep.add(T, 'warning', 'COPY-D-EMPTY', path, 'пустой текст выбранного варианта', 'Пустым бывает только alt декоративной картинки.')
    if st == 'image-alt':
        if not sl.get('asset_ref'):
            rep.add(T, 'warning', 'COPY-D-ASSET', path, 'alt без asset_ref', 'asset_ref — id слота плана ассетов или файл assets/… пакета kimi.')
        if not text.strip() and not re.search(r'декоратив|decorative', str(sl.get('notes') or '') + str(v.get('notes') or ''), re.I):
            rep.add(T, 'warning', 'COPY-D-ALT', path, 'пустой alt без пометки, что картинка декоративная', 'Декоративная — alt="" и notes: «декоративная»; информационная — описание сцены (ai-media 10/01 §8).')
        if re.match(r'\s*(фото|изображение|картинка|image of|picture of|photo of)\b', text, re.I):
            rep.add(T, 'info', 'COPY-D-ALT', path, 'alt начинается с «фото / изображение»', 'Скринридер и так сообщает, что это картинка: опишите сцену.')
    if st == 'image-caption' and not sl.get('asset_ref'):
        rep.add(T, 'warning', 'COPY-D-ASSET', path, 'подпись без asset_ref', 'asset_ref — к какой картинке подпись.')
    if st == 'in-image-text':
        if len(text) > 40:
            rep.add(T, 'error', 'COPY-D-IN-IMAGE', path, f'строка в картинке {len(text)} знаков > 40', 'ai-media 05/03 §7: ≤ 40 знаков, 1–4 слова; длиннее — HTML поверх картинки.')
        if len(words(text)) > 4:
            rep.add(T, 'warning', 'COPY-D-IN-IMAGE', path, f'в строке {len(words(text))} слов (надёжно 1–4)', 'Сократите или вынесите текст в HTML.')
        if cyr_share(text) > 0.5:
            rep.add(T, 'info', 'COPY-D-IN-IMAGE', path, 'кириллица в картинке: риск искажений, нужна проверка OCR', 'fallback: html_overlay (ai-media 05/03 §7).')
        if not sl.get('asset_ref'):
            rep.add(T, 'warning', 'COPY-D-ASSET', path, 'строка в картинке без asset_ref', 'asset_ref — id слота плана ассетов ai-media.')


def _validate_facts(deck, ctx, rep, sev, refs_and_publish=True):
    """Факты текстов: (1) ссылки fact_ids, срок и публикуемость — их же даёт claims_check.py, поэтому check пропускает
    эту часть, если сверка отработала (refs_and_publish=False); (2) пробелы: missing_ids и fallback B2 — этого
    claims_check.py не делает, часть работает всегда (E3: check терял COPY-D-FALLBACK)."""
    T = 'validate'
    facts = ctx.facts
    for page in pages_of(deck):
        if (page.get('status') or 'draft') == 'rejected':
            continue
        # свои fact_ids невыбранных живых вариантов (I3): битая ссылка — warning (этот текст пока не на странице)
        pid = str(page.get('page_id'))
        holders = [(f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}", sl, slot_alternatives(sl)) for s in sections_of(page) for sl in slots_of(s)]
        if isinstance(page.get('promise'), dict) and not page['promise'].get('from'):
            holders.append((f'{pid}/promise', page['promise'], slot_alternatives(page['promise'])))
        meta = page.get('meta') or {}
        holders += [(f'{pid}/meta/{k}', meta, meta_alternatives(meta, k)) for k, _st in META_FIELDS]
        for hpath, _holder, alts in (holders if refs_and_publish else []):
            for v in alts:
                for ref in (v.get('fact_ids') if isinstance(v.get('fact_ids'), list) else []):
                    f, m = facts.resolve(ref)
                    if f is None:
                        rep.add(T, 'warning', 'COPY-D-FACT-REF', f"{hpath}/{v.get('id')}",
                                f'fact_ids варианта: «{ref}» — ' + ('это пробел missing' if m is not None else 'нет такого факта'),
                                'Станет error, если вариант выберут: исправьте id или заведите факт.')
        for u in text_units(deck, page):
            refs = list(u['fact_ids'])
            slot = u['slot']
            status = _status_of(main_variant(slot)) if slot is not None else (page.get('status') or 'draft')
            for ref in (refs if refs_and_publish else []):
                f, m = facts.resolve(ref)
                if f is None:
                    if m is not None:
                        rep.add(T, 'error', 'COPY-D-FACT-REF', u['path'], f'fact_ids: «{ref}» — это пробел missing, факта ещё нет',
                                'Пробел — в тексте [PLACEHOLDER: …] и в missing_ids, не в fact_ids.')
                    else:
                        rep.add(T, 'error', 'COPY-D-FACT-REF', u['path'], f'fact_ids: нет факта «{ref}» в {os.path.basename(facts.path or "facts.yaml")}',
                                'Исправьте id (fact:<id> или алиас) или заведите факт в facts.yaml.')
                    continue
                iss = own_publish_issues(f, ctx.today)
                exp = [i for i in iss if i.startswith('истёк')]
                if exp:
                    rep.add(T, 'error', 'COPY-D-FACT-EXPIRED', u['path'], f'fact:{f["id"]}: {exp[0]}', 'Обновите факт у заказчика или уберите утверждение.')
                other = [i for i in iss if not i.startswith('истёк')]
                if other:
                    lvl = 'error' if STATUS_RANK.get(status, 0) >= 1 else 'warning'
                    rep.add(T, lvl, 'COPY-D-FACT-UNPUBLISHABLE', u['path'], f'fact:{f["id"]} не публикуется: {"; ".join(other)}',
                            'До разрешения или проверки — [PLACEHOLDER] (claims_check.py даст то же как COPY-F-…).')
            gaps = {}
            if slot is not None:
                for ref in slot.get('missing_ids') or []:
                    r = str(ref)[8:] if str(ref).startswith('missing:') else str(ref)
                    if r not in facts.missing_by_id:
                        rep.add(T, 'error', 'COPY-D-MISSING-REF', u['path'], f'missing_ids: нет пробела «{ref}»', 'id из facts.yaml missing[].')
                    elif not PLACEHOLDER_RX.search(u['text']):
                        rep.add(T, 'info', 'COPY-D-MISSING-REF', u['path'], f'missing_ids: {ref}, а в тексте нет [PLACEHOLDER]', 'Пробел закрыт? Уберите ссылку или верните заглушку.')
                    else:
                        gaps[r] = facts.missing_by_id[r]
            for m in PLACEHOLDER_RX.finditer(u['text']):
                hit = next((x for x in facts.missing if norm_ws(x.get('placeholder')).lower() == norm_ws(m.group(0)).lower()), None)
                if hit is not None:
                    gaps.setdefault(str(hit.get('id')), hit)
            for gid, gm in gaps.items():  # fallback пробела (B2): заглушка уместна только при fallback: placeholder
                fb = gm.get('fallback') or 'placeholder'
                if fb == 'omit-block':
                    rep.add(T, 'warning', 'COPY-D-FALLBACK', u['path'], f'missing:{gid} — fallback omit-block: до ответа блок не показывают, а в тексте заглушка',
                            'Снимите слот или секцию до ответа заказчика (facts.yaml missing[].fallback).')
                elif fb == 'rewrite-without':
                    rep.add(T, 'warning', 'COPY-D-FALLBACK', u['path'], f'missing:{gid} — fallback rewrite-without: перепишите текст без этого утверждения',
                            'Заглушка на странице здесь не нужна: скажите то, что подтверждено фактами.')


def _validate_wave2(deck, ctx, rep):
    """Файлы волны 2: есть — проверка работает; нет — предупреждение «правила не загружены», без падения."""
    T = 'validate'
    # --- E: copy-slots.yaml
    if ctx.copy_slots_path:
        cs_path = ctx.copy_slots_path
    elif deck.get('copy_slots_ref'):
        cs_path = rel_to(ctx.deck_path, deck['copy_slots_ref']) if ctx.deck_path else deck['copy_slots_ref']
    else:
        cs_path = COPY_SLOTS_PATH
    if cs_path and os.path.exists(cs_path):
        try:
            specs, renames, notes = load_copy_slots(cs_path)
        except Exception as e:  # noqa: BLE001
            specs, renames, notes = None, {}, [f'copy-slots.yaml не читается: {e}']
        for n in notes:
            rep.add(T, 'warning', 'COPY-D-RULES-FORMAT', '—', n, 'Сообщите J: формат E изменился.')
        if specs:
            meta_cs = specs.pop('__meta__', {}) or {}
            rep.tools.setdefault('validate', {})['copy_slots'] = os.path.relpath(cs_path, ROOT) if cs_path.startswith(ROOT) else cs_path
            lang = (deck.get('lang') or 'ru').split('-')[0]
            for page in pages_of(deck):
                pid = str(page.get('page_id'))
                targets = [(f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}", s, sl, sl.get('slot_type')) for s in sections_of(page) for sl in slots_of(s)]
                pr = page.get('promise')
                if isinstance(pr, dict) and not pr.get('from'):
                    targets.append((f'{pid}/promise', None, pr, 'promise'))
                for path, s, sl, st in targets:
                    spec = specs.get(st)
                    if spec is None:
                        if st in renames:
                            rep.add(T, 'warning', 'COPY-D-SLOT-RENAMED', path, f'slot_type «{st}» переименован E → «{renames[st]}»', 'Смените тип (upgrade) — copy-slots.yaml.')
                        else:
                            rep.add(T, 'warning', 'COPY-D-SLOT-UNKNOWN', path, f'slot_type «{st}» нет в copy-slots.yaml (E)', 'Правила текста для этого типа не заданы.')
                        continue
                    v = chosen_variant(sl)
                    text = str((v or {}).get('text') or '')
                    if v is None or not text:
                        continue
                    body = PLACEHOLDER_RX.sub('', text)
                    vals = {'words': len(words(body)), 'chars': len(norm_ws(body))}
                    ls = (spec.get('lang') or {}).get(lang)
                    exc = (' Исключения E: ' + one_line(spec['exceptions'][0])[:160]) if spec.get('exceptions') else ''
                    if ls:  # формат E: основная единица (RU — знаки, EN — слова), p10–p90 → info, грубые границы D → warning
                        prim = ls.get('primary') or 'chars'
                        prov = ' (provisional)' if ls.get('provisional') else ''
                        for unit in ('words', 'chars'):
                            val, rng, hard = vals[unit], ls.get(unit), ls.get(f'hard_{unit}')
                            un = 'слов' if unit == 'words' else 'знаков'
                            if hard and hard[1] is not None and val > hard[1]:
                                rep.add(T, 'warning', 'COPY-D-LEN', path, f'{val} {un} > {hard[1]} — за грубой границей замера D ({st}, {lang}){prov}', 'Длины — copy-slots.yaml E.' + exc)
                            elif unit == prim and rng and rng[1] is not None and val > rng[1]:
                                rep.add(T, 'info', 'COPY-D-LEN', path, f'{val} {un} > p90 лидеров {rng[1]} ({st}, {lang}){prov}', 'Сигнал, не ворота: у 10 % лидеров длиннее.' + exc)
                            if not PLACEHOLDER_RX.search(text):
                                if hard and hard[0] is not None and val < hard[0]:
                                    rep.add(T, 'warning', 'COPY-D-LEN', path, f'{val} {un} < {hard[0]} — за грубой границей замера D ({st}, {lang})', '')
                                elif unit == prim and rng and rng[0] is not None and val < rng[0]:
                                    rep.add(T, 'info', 'COPY-D-LEN', path, f'{val} {un} < p10 лидеров {rng[0]} ({st}, {lang}){prov}', '')
                    else:  # другой формат: границы min/max где угодно в length
                        for (lg, unit), (mn, mx) in sorted(spec['len'].items()):
                            if lg not in ('any', lang):
                                continue
                            val = vals[unit]
                            if mx is not None and val > mx:
                                rep.add(T, 'warning', 'COPY-D-LEN', path, f'{val} {"слов" if unit == "words" else "знаков"} > max {mx} ({st}, {lg})', 'Длины — copy-slots.yaml E; законные исключения — notes.')
                            if mn is not None and val < mn and not PLACEHOLDER_RX.search(text):
                                rep.add(T, 'info', 'COPY-D-LEN', path, f'{val} {"слов" if unit == "words" else "знаков"} < min {mn} ({st}, {lg})', '')
                    need = spec.get('fact_required')
                    refs = variant_fact_ids(sl, v)
                    if need == 'always' and not refs and not PLACEHOLDER_RX.search(text):
                        lvl = 'error' if STATUS_RANK.get(_status_of(v), 0) >= 1 else 'warning'
                        rep.add(T, lvl, 'COPY-D-FACT-REQUIRED', path, f'{st}: факт обязателен (copy-slots.yaml E), а fact_ids пуст', 'Ссылка на facts.yaml или [PLACEHOLDER: …].')
                    roles = spec.get('section_roles') or []
                    if s is not None and roles and s.get('section_role') and s['section_role'] not in roles:
                        rep.add(T, 'info', 'COPY-D-SLOT-ROLE', path, f'{st} в секции «{s["section_role"]}», а copy-slots.yaml ждёт {roles}', '')
                # составные правила E: ядро первого экрана (hero-core) — сумма слов слотов первой секции
                hc = ((meta_cs.get('composites') or {}).get('hero-core') or {})
                first = next((s for s in sections_of(page) if (s.get('section_role') or s.get('block') or s.get('section_id')) == 'hero'), None)
                if hc.get('max_words') and first is not None:
                    seen_t, total = set(), 0
                    for sl in slots_of(first):
                        if sl.get('slot_type') in ('headline', 'subheadline', 'cta-label', 'cta-note', 'hero-proof') and sl.get('slot_type') not in seen_t:
                            seen_t.add(sl.get('slot_type'))
                            total += len(words(PLACEHOLDER_RX.sub('', str((chosen_variant(sl) or {}).get('text') or ''))))
                    if total > hc['max_words']:
                        rep.add(T, 'warning', 'COPY-D-HERO-CORE', f"{pid}/{first.get('section_id')}", f'ядро первого экрана {total} слов > {hc["max_words"]} (hero-core, E)', one_line(hc.get('rule'))[:200])
    else:
        rep.add(T, 'warning', 'COPY-D-RULES-MISSING', '—', 'правила не загружены: copy-slots.yaml (E) нет — длины слотов и обязательность фактов не проверены',
                f'Появится {os.path.relpath(COPY_SLOTS_PATH, ROOT)} — проверка включится сама.')
    # --- F: голос
    vref = deck.get('voice_ref')
    if not os.path.exists(ctx.voice_schema_path):
        rep.add(T, 'warning', 'COPY-D-RULES-MISSING', '—', 'правила не загружены: voice.schema.yaml (F) нет — голос проверен только по voice.yaml, если он есть', '')
    if vref and looks_like_path(vref):
        vp = rel_to(ctx.deck_path, vref) if ctx.deck_path else vref
        if vp and os.path.exists(vp):
            try:
                voice = load_voice(vp)
            except Exception as e:  # noqa: BLE001
                voice = None
                rep.add(T, 'warning', 'COPY-D-VOICE', '—', f'voice.yaml не читается: {e}', '')
            if voice:
                _voice_checks(deck, voice, rep)
        else:
            rep.add(T, 'warning', 'COPY-D-VOICE', '—', f'voice_ref «{vref}» не найден', 'Путь от папки copy deck.')
    elif vref:
        rep.add(T, 'info', 'COPY-D-VOICE', '—', 'voice_ref — строка-описание (до профиля голоса F): голос не проверяется', '')
    # --- G: мета
    mr = ctx.meta_rules
    if mr is not None:
        if not mr.get('format'):
            rep.add(T, 'info', 'COPY-D-RULES-FORMAT', '—', 'meta-rules.yaml: limits и checks_outside_linter не распознаны — проверки мета пропущены (правила линтера G работают через copy_lint.py)', 'Сообщите J: формат G изменился.')
        else:
            rep.tools.setdefault('validate', {})['meta_rules'] = f"{os.path.relpath(ctx.meta_rules_path, ROOT) if ctx.meta_rules_path.startswith(ROOT) else ctx.meta_rules_path} ({mr['format']})"
            _meta_checks(deck, mr, rep, ctx.final)
    else:
        rep.add(T, 'warning', 'COPY-D-RULES-MISSING', '—', 'правила не загружены: meta-rules.yaml (G) нет — длины мета и проверки между страницами не проверены', '')
        seen = {}
        for page in pages_of(deck):
            for k in ('title', 'description'):
                t = norm_ws((page.get('meta') or {}).get(k) or '').lower()
                if t:
                    if (k, t) in seen:
                        rep.add(T, 'warning', 'COPY-D-META-DUP', f"{page.get('page_id')}/meta/{k}", f'meta.{k} совпадает со страницей {seen[(k, t)]}', 'У каждой страницы своя мета.')
                    seen.setdefault((k, t), page.get('page_id'))
    # --- H: флаги права
    known = set(claim_class_info())
    rule_ids = None
    if os.path.exists(ctx.claims_rules_path):
        try:
            rule_ids = load_claims_rules_ids(ctx.claims_rules_path)
        except Exception as e:  # noqa: BLE001
            rep.add(T, 'warning', 'COPY-D-RULES-FORMAT', '—', f'claims-rules.yaml не читается: {e}', '')
    else:
        rep.add(T, 'warning', 'COPY-D-RULES-MISSING', '—', 'правила не загружены: claims-rules.yaml (H) нет — флаги права не проверены', '')
    for page in pages_of(deck):
        for u in text_units(deck, page, include_meta=False):
            slot = u['slot']
            for fl in (slot or {}).get('claim_flags') or []:
                fl = str(fl)
                if fl in known or re.fullmatch(r'\d+fz(-[0-9a-z.]+)+', fl, re.I) or re.fullmatch(r'(zozpp|gk|152fz|ftc|ucpd)[-0-9a-z.]*', fl, re.I):
                    continue
                if fl.upper().startswith('COPY-'):
                    if rule_ids is None:
                        rep.add(T, 'info', 'COPY-D-FLAGS', u['path'], f'флаг «{fl}»: правила H не загружены — не проверен', '')
                    elif fl not in rule_ids:
                        rep.add(T, 'warning', 'COPY-D-FLAGS', u['path'], f'флаг «{fl}» нет в claims-rules.yaml', 'id правил H — COPY-L-…')
                    continue
                rep.add(T, 'warning', 'COPY-D-FLAGS', u['path'], f'неизвестный claim_flags «{fl}»', 'Классы B2 (x-claim-classes), id правил H (COPY-L-…) или флаги норм (38fz-5-3-1).')
    # подсказка: факт класса legal: required без флага в слоте
    if ctx.facts is not None:
        info = claim_class_info()
        for page in pages_of(deck):
            for u in text_units(deck, page, include_meta=False):
                slot = u['slot'] or {}
                flags = {str(x) for x in slot.get('claim_flags') or []}
                for ref in u['fact_ids']:
                    f, _m = ctx.facts.resolve(ref)
                    for c in (f or {}).get('claim_class') or []:
                        if (info.get(c) or {}).get('legal') == 'required' and c not in flags:
                            rep.add(T, 'info', 'COPY-D-FLAGS', u['path'], f'fact:{f["id"]} класса {c} (legal: required), а в claim_flags его нет', f'claim_flags: [{c}] — флаг для H и человека.')


def _voice_checks(deck, voice, rep):
    T = 'validate'
    lang = (deck.get('lang') or 'ru').split('-')[0]
    rxs = []
    for t in voice['taboo']:
        try:
            rxs.append((t, words_rx(t['term'])))
        except re.error:
            continue
    for page in pages_of(deck):
        for u in text_units(deck, page, include_meta=True):
            if u['slot_type'] == 'testimonial-quote':
                continue  # голос бренда не правит цитату клиента (F, B2)
            low = u['text'].lower()
            for t, rx in rxs:
                if t['lang'] not in ('any', lang) or (t['slot_types'] and u['slot_type'] not in t['slot_types']):
                    continue
                m = rx.search(low)
                if m:
                    lvl = t['level'] if t['level'] in LEVELS else 'warning'
                    fix = ('Вместо: ' + t['use_instead'] + '. ' if t['use_instead'] else '') + (f"Можно, если: {t['unless']}." if t['unless'] else 'Профиль голоса F (voice.yaml vocabulary.avoid).')
                    rep.add(T, lvl, 'COPY-D-VOICE', u['path'], f'«не говорим» голоса: «{m.group(0)}» (термин {t["term"]})', fix)
            if lang == 'ru' and voice['address'] and u['slot_type'] not in voice.get('exceptions', []) \
                    and (u['section'] or {}).get('section_id') not in voice.get('exceptions', []):
                if voice['address'] == 'вы' and re.search(r'(?<![а-яё])(ты|тебя|тебе|тобой|твой|твоя|твоё|твои|твоих|твоим)(?![а-яё])', low):
                    rep.add(T, 'warning', 'COPY-D-VOICE', u['path'], 'обращение на «ты», а голос — на «вы»', 'address.ru_form голоса F.')
                if voice['address'] == 'ты' and re.search(r'(?<![а-яё])(вас|вам|вами|ваш|ваша|ваше|ваши|вашего|вашей)(?![а-яё])', low):
                    rep.add(T, 'warning', 'COPY-D-VOICE', u['path'], 'обращение на «вы», а голос — на «ты»', 'address.ru_form голоса F.')


def _validate_language(deck, ctx, rep):
    T = 'validate'
    lang = (deck.get('lang') or '').split('-')[0]
    src = deck.get('source_lang')
    if src:
        if src.split('-')[0] == lang:
            rep.add(T, 'error', 'COPY-D-LANG', '—', f'source_lang «{src}» = lang', 'source_lang — язык исходного copy deck, если этот — адаптация.')
        if not deck.get('source_ref'):
            rep.add(T, 'warning', 'COPY-D-LANG', '—', 'адаптация без source_ref', 'Укажите исходный copy deck.')
        elif ctx.deck_path and not os.path.exists(rel_to(ctx.deck_path, deck['source_ref'])):
            rep.add(T, 'warning', 'COPY-D-LANG', '—', f'source_ref «{deck["source_ref"]}» не найден', '')
        if ((deck.get('adaptation') or {}).get('mode')) == 'translation':
            rep.add(T, 'warning', 'COPY-D-LANG', '—', 'adaptation.mode: translation', 'Решение заказчика п. 16: второй язык — адаптация под свою аудиторию, а не дословный перевод.')
        if ctx.facts is not None:
            for page in pages_of(deck):
                for u in text_units(deck, page):
                    for ref in u['fact_ids']:
                        f, _m = ctx.facts.resolve(ref)
                        if f is not None and (f.get('lang') or 'ru').split('-')[0] != lang and lang not in (f.get('translations') or {}):
                            rep.add(T, 'warning', 'COPY-D-LANG', u['path'], f'fact:{f["id"]}: нет translations.{lang}',
                                    'Сверка сравнит текст с формулировкой на другом языке: добавьте translations в facts.yaml.')
    for page in pages_of(deck):
        for u in text_units(deck, page):
            t = PLACEHOLDER_RX.sub('', u['text'])
            if len(words(t)) < 3:
                continue
            share = cyr_share(t)
            if lang == 'en' and share > 0.3:
                rep.add(T, 'warning', 'COPY-D-LANG', u['path'], f'кириллица в английском тексте ({share:.0%} букв)', 'Второй язык — отдельный copy deck.')
            if lang == 'ru' and share < 0.3 and u['slot_type'] not in ('testimonial-quote',):
                rep.add(T, 'info', 'COPY-D-LANG', u['path'], f'латиница в русском тексте ({1 - share:.0%} букв)', '')


# ============================================================================================ claims: claims_check.py процессом
def _flat_slot(slot_id, slot_type, variants, chosen, fact_ids, claim_flags, genre):
    vs = [{'id': str(v.get('id')), 'text': str(v.get('text') or ''), 'status': v.get('status') or 'draft'}
          for v in (variants or []) if isinstance(v, dict)]
    out = {'slot_id': str(slot_id), 'slot_type': slot_type or 'body', 'variants': vs,
           'fact_ids': [str(x) for x in fact_ids or []], 'claim_flags': [str(x) for x in claim_flags or []],
           'lint': {'profile': genre}}
    if chosen is not None:
        out['chosen'] = str(chosen)
    return out


def flatten_for_claims(deck, ctx, pages=None, alternatives=False):
    """v1 → плоская копия v0 для claims_check.py: мета и OG-шаблон — псевдосекция __head (жанр meta), обещание —
    псевдосекция __promise (subheadline в hero), у каждого слота lint.profile = жанр (claims берёт жанр оттуда); в слоте —
    только текст, который проверяется как текст слота (main_variant), с его фактами (variant_fact_ids).
    alternatives (check --all-variants): каждый живой невыбранный вариант (и альтернатива мета) сверяется «как если бы
    его выбрали» — копия страницы `<page>~alt~N`, где заменён один слот; соседние варианты не считаются текстом «рядом»
    (nearby), отклонённые не сверяются (I3: claims_check load_deck при --all-variants не пропускал rejected).
    → (deck, {(page, section, slot): путь}, {(копия страницы, section, slot): (путь, id варианта)})."""
    vocab = ctx.vocab
    out_pages, mapping, alt_map = [], {}, {}
    for page in pages_of(deck):
        pid = str(page.get('page_id'))
        if (pages and pid not in pages) or (page.get('status') or 'draft') == 'rejected':
            continue
        secs, head, alts = [], [], []   # alts: (section_id, slot_id, путь, id варианта, текст, факты)
        meta = page.get('meta') or {}
        for k, st in META_FIELDS:
            if str(meta.get(k) or '').strip():
                # meta.fact_ids — один список на все поля: в сверку не передаём (claims_check найдёт факт по тексту поля),
                # иначе каждое поле получает чужие факты и ложные COPY-F-USE; свои fact_ids варианта мета — передаём
                mvar = meta_variant_for(meta, k)
                own = mvar['fact_ids'] if isinstance((mvar or {}).get('fact_ids'), list) else []
                head.append(_flat_slot(k, st, [{'id': 'meta', 'text': meta[k], 'status': 'draft'}], 'meta', own, [], 'meta'))
                mapping[(pid, '__head', k)] = f'{pid}/meta/{k}'
                for v in (meta_alternatives(meta, k) if alternatives else []):
                    alts.append(('__head', k, f'{pid}/meta/{k}', str(v.get('id')), str(v.get('text')),
                                 v['fact_ids'] if isinstance(v.get('fact_ids'), list) else []))
        og = page.get('og_template') or {}
        for k, st in OG_TEMPLATE_FIELDS:
            if str(og.get(k) or '').strip():
                head.append(_flat_slot(f'og_template-{k}', st, [{'id': 'a', 'text': og[k], 'status': 'draft'}], 'a', [], [], 'meta'))
                mapping[(pid, '__head', f'og_template-{k}')] = f'{pid}/og_template/{k}'
        if head:
            secs.append({'section_id': '__head', 'section_role': 'head', 'slots': head})
        pr = page.get('promise')
        if isinstance(pr, dict) and not pr.get('from') and variants_of(pr):
            genre = effective_genre(deck, page, None, 'subheadline', (pr.get('lint') or {}).get('profile'), vocab)[0]
            mv = main_variant(pr)
            secs.append({'section_id': '__promise', 'section_role': 'hero',
                         'slots': [_flat_slot('promise', 'subheadline', [mv] if mv else [], (mv or {}).get('id'),
                                              variant_fact_ids(pr, mv), pr.get('claim_flags'), genre)]})
            mapping[(pid, '__promise', 'promise')] = f'{pid}/promise'
            for v in (slot_alternatives(pr) if alternatives else []):
                alts.append(('__promise', 'promise', f'{pid}/promise', str(v.get('id')), str(v.get('text') or ''), variant_fact_ids(pr, v)))
        for s in sections_of(page):
            sid = str(s.get('section_id'))
            slots = []
            for sl in slots_of(s):
                genre = effective_genre(deck, page, s, sl.get('slot_type'), (sl.get('lint') or {}).get('profile'), vocab)[0]
                mv = main_variant(sl)
                slid = str(sl.get('slot_id'))
                slots.append(_flat_slot(slid, sl.get('slot_type'), [mv] if mv else [], (mv or {}).get('id'),
                                        variant_fact_ids(sl, mv), sl.get('claim_flags'), genre))
                mapping[(pid, sid, slid)] = f'{pid}/{sid}/{slid}'
                for v in (slot_alternatives(sl) if alternatives else []):
                    alts.append((sid, slid, f'{pid}/{sid}/{slid}', str(v.get('id')), str(v.get('text') or ''), variant_fact_ids(sl, v)))
            role = s.get('section_role')
            if not role and vocab and s.get('block') in vocab['section_roles']:
                role = s.get('block')
            sec = {'section_id': sid, 'block': s.get('block') or '', 'slots': slots}
            if role:
                sec['section_role'] = role
            secs.append(sec)
        fp = {'page_id': pid, 'page_type': page.get('page_type'), 'meta': {}, 'sections': secs}
        out_pages.append(fp)
        for n, (sid, slid, path, vid, text, fids) in enumerate(alts, 1):
            pp = _copy.deepcopy(fp)
            pp['page_id'] = f'{pid}~alt~{n}'
            for sec in pp['sections']:
                for fs in sec['slots']:
                    if sec['section_id'] == sid and fs['slot_id'] == slid:
                        fs['variants'] = [{'id': vid, 'text': text, 'status': 'draft'}]
                        fs['chosen'] = vid
                        fs['fact_ids'] = [str(x) for x in fids or []]
            alt_map[(pp['page_id'], sid, slid)] = (path, vid)
            out_pages.append(pp)
    flat = {'version': 0, 'date': deck.get('date'), 'site': deck.get('site'), 'lang': deck.get('lang'),
            'facts_ref': deck.get('facts_ref'), 'pages': out_pages}
    for k in ('jurisdiction', 'legal_category'):
        if deck.get(k):
            flat[k] = deck[k]
    return {'copy_deck': flat}, mapping, alt_map


def _empty_counts():
    return {'errors': 0, 'warnings': 0, 'info': 0, 'rules': []}


def _bump(agg, level, rule):
    agg[{'error': 'errors', 'warning': 'warnings'}.get(level, 'info')] += 1
    if rule and rule not in agg['rules']:
        agg['rules'].append(rule)


def run_claims(deck, ctx, facts_path, rep, strict=False, all_variants=False, pages=None, timeout=240):
    """claims_check.py check на плоской копии → находки в rep и итоги по путям {путь: {errors, warnings, info, rules
    [, variants: {id: итоги}]}}: итоги пути — только текст слота (для статусов и записей); с all_variants у пути ещё
    variants — каждый живой невыбранный вариант, сверенный «как если бы выбран» (I3). None — утилита не отработала."""
    if not os.path.exists(CLAIMS_CHECK):
        rep.add('claims', 'error', 'COPY-D-TOOL', '—', f'нет {CLAIMS_CHECK}', 'Сверка с фактами — ворота; без неё статус checked не ставится.')
        return None
    flat, mapping, alt_map = flatten_for_claims(deck, ctx, pages, alternatives=all_variants)
    with tempfile.TemporaryDirectory(prefix='copydeck-') as td:
        dp, jp = os.path.join(td, 'deck-flat.yaml'), os.path.join(td, 'claims.json')
        with open(dp, 'w', encoding='utf-8') as fo:
            yaml.safe_dump(flat, fo, allow_unicode=True, sort_keys=False, width=160)
        # --all-variants claims_check не передаём: альтернативы — отдельными копиями страницы (flatten_for_claims)
        cmd = [sys.executable, CLAIMS_CHECK, 'check', dp, '--format', 'deck', '--json', jp, '--today', ctx.today, '--quiet']
        if facts_path:
            cmd += ['--facts', facts_path]
        if strict:
            cmd.append('--strict')
        if deck.get('jurisdiction'):
            cmd += ['--jurisdiction', str(deck['jurisdiction'])]
        if deck.get('legal_category'):
            cats = deck['legal_category'] if isinstance(deck['legal_category'], list) else [deck['legal_category']]
            cmd += ['--legal-category', ','.join(str(c) for c in cats)]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            rep.add('claims', 'error', 'COPY-D-TOOL', '—', f'claims_check.py не уложился в {timeout} с', '')
            return None
        if p.returncode not in (0, 2) or not os.path.exists(jp):
            tail = (p.stderr or p.stdout or '').strip().splitlines()[-3:]
            rep.add('claims', 'error', 'COPY-D-TOOL', '—', f'claims_check.py не отработал (код {p.returncode}): {" | ".join(tail)}', 'Проверьте facts.yaml: claims_check.py lint-facts FACTS.')
            return None
        with open(jp, encoding='utf-8') as f:
            res = json.load(f)
        for line in (p.stderr or '').splitlines():
            if line.strip():
                rep.notes.append(f'claims_check: {line.strip()[:200]}')
    per_path = {path: _empty_counts() for path in mapping.values()}
    for (_pp, _sid, _slid), (path, vid) in alt_map.items():
        per_path.setdefault(path, _empty_counts()).setdefault('variants', {}).setdefault(vid, _empty_counts())
    kept = {lv: 0 for lv in LEVELS}
    for f in res.get('findings') or []:
        parts = str(f.get('unit') or '').split('/')
        key = tuple(parts[:3])
        if '~alt~' in parts[0]:
            hit = alt_map.get(key)
            if hit is None:
                continue  # остальные тексты копии страницы уже сверены основным прогоном
            where, variant = hit
            agg = per_path[where]['variants'][variant]
        else:
            where = mapping.get(key, '/'.join(parts[:3]) if len(parts) >= 3 else (f.get('unit') or '—'))
            variant = parts[3] if len(parts) >= 4 else None
            agg = per_path.setdefault(where, _empty_counts())
        lvl = f.get('level', 'info')
        rep.add('claims', lvl, f.get('rule', 'COPY-F-?'), where, f.get('message', ''), f.get('fix', ''),
                fragment=str(f.get('fragment') or '')[:90], claim_class=f.get('claim_class'),
                variant=variant if all_variants else None, fact_ids=f.get('fact_ids') or None)
        _bump(agg, lvl, f.get('rule'))
        kept[lvl if lvl in kept else 'info'] += 1
    summ = dict(res.get('summary') or {})
    if alt_map:
        summ.update({'error': kept['error'], 'warning': kept['warning'], 'info': kept['info'],
                     'note': f'с --all-variants: {len(alt_map)} вариантов сверены копиями страницы; claims, supported, by_rule и by_class — по всем единицам копий'})
    rep.tools['claims'] = {'tool': f"claims_check.py {res.get('version')}", 'summary': summ,
                           'facts': facts_path, 'rules_loaded': res.get('rules_loaded'), 'legal': res.get('legal'),
                           'units_checked': len(mapping), 'alternatives': len(alt_map)}
    return per_path


BRIEF_TEXT_FIELDS = ('product.goal', 'product.description', 'product.primary_action', 'product.target_user', 'site.cta.label')


def brief_texts(brief):
    """Поля брифа kimi, которые уходят в TASK.md (Promise, Audience, The one job, CTA, Sections) и могут попасть на
    страницу, — [(где, текст)]; хвост «; доказательства: …» у job не проверяется (это id фактов)."""
    out = []
    for path in BRIEF_TEXT_FIELDS:
        cur = brief
        for part in path.split('.'):
            cur = cur.get(part) if isinstance(cur, dict) else None
        if isinstance(cur, str) and cur.strip():
            out.append((f'brief:{path}', one_line(cur)))
    for i, sct in enumerate(((brief.get('site') or {}).get('sections') or [])):
        if isinstance(sct, dict) and sct.get('job'):
            job = str(sct['job']).split('; доказательства:')[0]
            # «вопрос → опора»: стрелка — граница фразы; иначе эвристика имён claims_check принимает слово после «→» за
            # имя (ложные COPY-F-NAME «Вызвать», «Один» — перепрогон J/01, J2 2026-09-24)
            job = re.sub(r'([?!.…]?)\s*→\s*', lambda m: (m.group(1) + ' ') if m.group(1) else '. ', job)
            out.append((f"brief:site.sections[{sct.get('id') or i}].job", one_line(job)))
    return out


def run_claims_text(items, ctx, facts_path, rep, tool='brief', timeout=120):
    """claims_check.py на строках вне copy deck (поля брифа): одна строка — одна единица текста. Находки — в rep."""
    if not items or not os.path.exists(CLAIMS_CHECK):
        return None
    with tempfile.TemporaryDirectory(prefix='copydeck-') as td:
        tp, jp = os.path.join(td, 'brief-texts.txt'), os.path.join(td, 'claims.json')
        with open(tp, 'w', encoding='utf-8') as fo:
            fo.write('\n'.join(t for _w, t in items) + '\n')
        cmd = [sys.executable, CLAIMS_CHECK, 'check', tp, '--format', 'text', '--json', jp, '--today', ctx.today, '--quiet']
        if facts_path:
            cmd += ['--facts', facts_path]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return None
        if p.returncode not in (0, 2) or not os.path.exists(jp):
            return None
        res = json.load(open(jp, encoding='utf-8'))
    n = 0
    for f in res.get('findings') or []:
        line = (f.get('location') or {}).get('line')
        where = items[line - 1][0] if isinstance(line, int) and 0 < line <= len(items) else 'brief'
        lvl = f.get('level', 'info')
        if lvl == 'error' and ('.job' in where or 'target_user' in where):
            lvl = 'warning'  # задание секции и аудитория — инструкции K3, не текст страницы: сигнал, не ворота
        rep.add(tool, lvl, f.get('rule', 'COPY-F-?'), where, f.get('message', ''),
                (f.get('fix') or '') + ' Поле брифа уходит в TASK.md kimi и может попасть на страницу (урок «Кварца»).',
                fragment=str(f.get('fragment') or '')[:90])
        n += 1
    return n


# ============================================================================================ lint: copy_lint.lint_text
_CL = {}


def lint_module():
    if 'm' not in _CL:
        _CL['m'] = None
        try:
            if HERE not in sys.path:
                sys.path.insert(0, HERE)
            import copy_lint  # noqa: WPS433
            _CL['m'] = copy_lint
            if not os.environ.get('COPYDECK_NO_LINT_CACHE'):
                lint_cache(True)
        except Exception as e:  # noqa: BLE001
            _CL['err'] = f'{type(e).__name__}: {e}'
    return _CL['m']


def lint_cache(on=True):
    """Кэш загрузки правил для lint_text: API C перечитывает YAML и компилирует ≈ 430 правил на каждый вызов (≈ 0,5 с;
    copy deck на 35 текстов — 17 с против 0,7 с у copy_lint.py в режиме copy deck). Код C не меняется: в процессе
    copydeck загрузчики copy_lint.load_yaml и load_rules заменяются запоминающими обёртками (по пути и времени изменения
    файла; YAML отдаётся глубокой копией). Равенство результатов с кэшем и без — --selftest. Выключить:
    COPYDECK_NO_LINT_CACHE=1."""
    C = _CL.get('m')
    if C is None:
        return False
    if not hasattr(C, '_copydeck_orig'):
        C._copydeck_orig = (C.load_yaml, C.load_rules)
    orig_yaml, orig_rules = C._copydeck_orig
    if not on:
        C.load_yaml, C.load_rules = orig_yaml, orig_rules
        _CL['cache'] = False
        return True
    ycache, rcache = {}, {}

    def load_yaml_cached(path):
        try:
            k = (str(path), os.path.getmtime(path))
        except OSError:
            return orig_yaml(path)
        if k not in ycache:
            ycache[k] = orig_yaml(path)
        return _copy.deepcopy(ycache[k])

    def load_rules_cached(extra=None, profiles=None, log=None):
        files = sorted(str(x) for x in C.LEXICON_DIR.glob('*.yaml'))
        stamp = tuple((f, os.path.getmtime(f)) for f in files)
        ext = json.dumps((profiles or {}).get('external_rules'), sort_keys=True, default=str, ensure_ascii=False)
        key = (tuple(extra or ()), ext, stamp)
        if key not in rcache:
            lg = []
            rcache[key] = (orig_rules(extra, profiles, lg), lg)
        rules, lg = rcache[key]
        if log is not None:
            log.extend(lg)
        return rules
    C.load_yaml, C.load_rules = load_yaml_cached, load_rules_cached
    _CL['cache'] = True
    return True


def _allow_list(raw):
    out = []
    for a in raw if isinstance(raw, list) else ([raw] if raw else []):
        if isinstance(a, dict) and a.get('rule'):
            out.append((str(a['rule']), str(a.get('reason') or '')))
        elif isinstance(a, str):
            out.append((a, ''))
    return out


def _allowed(f, allow):
    """lint_allow по правилам C: шаблон fnmatch по id; артефакты (ART) и данные (CNT) не подавляются."""
    if f.get('group') in ('ART', 'CNT'):
        return None
    for pat, reason in allow:
        if fnmatch.fnmatch(str(f.get('id')), pat):
            return reason or '—'
    return None


def page_markdown(deck, page):
    """Markdown-проекция выбранных текстов страницы для прохода страницы: заголовки — #/##/###, проза — абзацы,
    отзывы — «>», прочие короткие слоты — пункты списка (не проза), надзаголовок — капсом перед заголовком (так
    copy_lint.parse_markdown распознаёт его как eyebrow). Мета и OG сюда не входят."""
    lines = []
    for s in sections_of(page):
        pairs = [(sl, chosen_variant(sl)) for sl in slots_of(s)]
        eyebrows = [norm_ws(v.get('text')).upper() for sl, v in pairs if v and sl.get('slot_type') == 'eyebrow' and str(v.get('text') or '').strip()]
        for sl, v in pairs:
            if not v or sl.get('slot_type') == 'eyebrow':
                continue
            t = str(v.get('text') or '').strip()
            if not t:
                continue
            st = sl.get('slot_type') or 'body'
            lvl = HEADING_LEVEL.get(st)
            if lvl:
                lines.append('')
                if eyebrows:
                    lines.append(eyebrows.pop(0))
                lines.append('#' * lvl + ' ' + norm_ws(t))
            elif st in PROSE_SLOT_TYPES:
                lines += ['', t]
            elif st == 'testimonial-quote':
                lines += ['', '> ' + norm_ws(t)]
            else:
                lines += ['', '- ' + norm_ws(t)]
        for e in eyebrows:
            lines += ['', '- ' + e.capitalize()]
    return '\n'.join(lines).strip() + '\n'


def run_lint(deck, ctx, rep, final=False, all_variants=False, page_pass=True, pages=None):
    """copy_lint.lint_text по каждому тексту (свой slot_type и жанр) + проход страницы. → {путь: итоги}; None — нет линтера."""
    C = lint_module()
    if C is None:
        rep.add('lint', 'error', 'COPY-D-TOOL', '—', f'copy_lint.py не импортируется: {_CL.get("err")}', '')
        return None
    vocab = ctx.vocab
    lang = (deck.get('lang') or 'auto').split('-')[0] if deck.get('lang') else 'auto'
    try:
        _rules = C.load_rules(profiles=C.load_profiles(), log=[])
        doc_scope = {r.id for r in _rules if getattr(r, 'scope', '') == 'doc'}
        no_fact = {r.id for r in _rules if getattr(r, 'requires_no_fact', False)}
    except Exception:  # noqa: BLE001
        doc_scope, no_fact = set(), set()
    cache, per_path, notes, n_calls = {}, {}, [], 0
    parity = {'meta_fact_ids': 0, 'rules': [], 'paths': []}   # что снял meta.fact_ids, а copy_lint.py на deck покажет
    for page in pages_of(deck):
        pid = str(page.get('page_id'))
        if (pages and pid not in pages) or (page.get('status') or 'draft') == 'rejected':
            continue
        for u in text_units(deck, page, include_meta=True, all_variants=all_variants):
            slot = u['slot'] or {}
            if u['kind'] in ('meta', 'og'):
                genre, prof = 'meta', ''
            else:
                genre, prof = effective_genre(deck, page, u['section'], u['slot_type'], (slot.get('lint') or {}).get('profile'), vocab)
            text = u['text']
            blank = {'profile': prof or genre, 'errors': 0, 'warnings': 0, 'info': 0, 'suppressed': 0, 'verdict': 'clean'}
            agg = per_path.setdefault(u['path'], dict(blank))
            if not u.get('chosen', True):  # альтернатива (--all-variants): свои итоги, статус слота они не трогают
                agg = agg.setdefault('variants', {}).setdefault(str(u['variant']), dict(blank))
            if not text.strip():
                continue
            key = (text, genre, u['slot_type'] or '', prof, lang)
            if key not in cache:
                try:
                    cache[key] = C.lint_text(text, genre=genre, lang=lang, slot_type=u['slot_type'] or '', profile=prof)
                    n_calls += 1
                except (Exception, SystemExit) as e:  # noqa: BLE001
                    rep.add('lint', 'error', 'COPY-D-TOOL', u['path'], f'lint_text: {type(e).__name__}: {e}', 'Проверьте жанр и профиль слота.')
                    cache[key] = None
            res = cache[key]
            if not res:
                continue
            for n in res.get('notes') or []:
                if n not in notes and not n.startswith('жанр не задан'):
                    notes.append(n)
            allow = _allow_list(slot.get('lint_allow'))
            # lint_text не знает fact_ids слота: повторяем режим copy deck линтера C — правила requires_no_fact и
            # an-number-without-fact молчат при fact_ids; явный пустой fact_ids — warning, как у C для copy deck
            refs = u['fact_ids']
            explicit_empty = (u['kind'] == 'slot' and 'fact_ids' in slot and not refs)
            for f in res.get('findings') or []:
                if (f.get('position') or {}).get('unit', 0) < 0 or f.get('id') in doc_scope:
                    continue  # находки документа — в проходе страницы
                if refs and (f.get('id') in no_fact or f.get('id') == 'an-number-without-fact'):
                    if u['kind'] == 'meta' and u.get('chosen', True):
                        parity['meta_fact_ids'] += 1
                        parity['rules'] += [f.get('id')] if f.get('id') not in parity['rules'] else []
                        parity['paths'] += [u['path']] if u['path'] not in parity['paths'] else []
                    continue
                lvl = f.get('level')
                if f.get('id') == 'an-number-without-fact' and explicit_empty and lvl == 'info':
                    lvl = 'warning'
                if final and f.get('id') == 'art-placeholder-marker' and lvl != 'error':
                    lvl = 'error'
                    agg['final_escalated'] = agg.get('final_escalated', 0) + 1
                if lvl not in LEVELS:
                    continue
                why = _allowed(f, allow)
                if why:
                    agg['suppressed'] += 1
                    rep.notes.append(f"lint_allow: {f.get('id')} @ {u['path']}: {why}")
                    continue
                rep.add('lint', lvl, f.get('id'), u['path'], f.get('message', ''), f.get('replacement', ''),
                        fragment=str(f.get('fragment') or '')[:90], marker_id=f.get('marker_id'), group=f.get('group'),
                        variant=u['variant'] if all_variants else None)
                agg[{'error': 'errors', 'warning': 'warnings'}.get(lvl, 'info')] += 1
            agg['verdict'] = 'fail' if agg['errors'] else ('review' if agg['warnings'] else 'clean')
        if page_pass:
            md = page_markdown(deck, page)
            pg = effective_genre(deck, page, None, None, None, vocab)[0]
            if pg == 'meta':
                pg = 'landing'
            try:
                res = C.lint_text(md, genre=pg, lang=lang, fmt='md')
                n_calls += 1
            except (Exception, SystemExit) as e:  # noqa: BLE001
                rep.add('lint', 'error', 'COPY-D-TOOL', pid, f'lint_text (страница): {type(e).__name__}: {e}', '')
                continue
            allow = _allow_list(page.get('lint_allow'))
            agg = {'profile': pg, 'errors': 0, 'warnings': 0, 'info': 0, 'suppressed': 0}
            for f in res.get('findings') or []:
                if not ((f.get('position') or {}).get('unit', 0) < 0 or f.get('id') in doc_scope):
                    continue
                if f.get('id') == 'an-lists-of-three':
                    continue  # артефакт проекции: короткие слоты — пункты списка
                lvl = f.get('level')
                if lvl not in LEVELS:
                    continue
                why = _allowed(f, allow)
                if why:
                    agg['suppressed'] += 1
                    rep.notes.append(f"lint_allow страницы: {f.get('id')} @ {pid}: {why}")
                    continue
                rep.add('lint', lvl, f.get('id'), f'{pid} (страница)', f.get('message', ''), f.get('replacement', ''),
                        fragment=str(f.get('fragment') or f.get('context') or '')[:90], marker_id=f.get('marker_id'), group=f.get('group'))
                agg[{'error': 'errors', 'warning': 'warnings'}.get(lvl, 'info')] += 1
            m = res.get('metrics') or {}
            agg['metrics'] = {'words': (m.get('all') or {}).get('words'), 'markers_per_100w': (m.get('markers') or {}).get('per_100w'),
                              'prose_words': (m.get('prose') or {}).get('words') if m.get('prose') else 0,
                              'dash_punct_per_100w': (m.get('prose') or {}).get('dash_punct_per_100w') if m.get('prose') else None,
                              'concreteness_per_100w': (m.get('prose') or {}).get('concreteness_per_100w') if m.get('prose') else None}
            per_path[f'{pid} (страница)'] = agg
    rep.tools['lint'] = {'tool': f'copy_lint {getattr(C, "VERSION", "?")} (lint_text)', 'calls': n_calls, 'texts': len(cache),
                         'rules_cache': bool(_CL.get('cache')), 'notes': notes}
    if parity['meta_fact_ids']:
        # два пути линтера (E3, J/05): copy_lint.py на copy deck не читает meta.fact_ids, copydeck — читает
        rep.tools['lint']['parity_copy_lint'] = parity
        rep.notes.append(f"meta.fact_ids сняли {parity['meta_fact_ids']} находок линтера в мета ({', '.join(parity['rules'])}; "
                         f"{', '.join(parity['paths'][:4])}): copy_lint.py на этом copy deck их покажет — он не читает meta.fact_ids "
                         '(предложение C); ворота — copydeck.py check')
    for n in notes:
        rep.notes.append(f'copy_lint: {n}')
    return per_path


# ============================================================================================ вывод
ORDER = {'error': 0, 'warning': 1, 'info': 2}
TOOL_ORDER = {'claims': 0, 'lint': 1, 'validate': 2, 'brief': 3, 'export': 4, 'approve': 5}


def render_text(rep, head, verbose=False, limit=80):
    L = [head]
    for tool in ('claims', 'lint', 'validate', 'brief', 'export'):
        if tool in rep.tools or any(f['tool'] == tool for f in rep.findings):
            t = rep.tools.get(tool) or {}
            name = t.get('tool') or tool
            extra = f" · схема: {t['schema_engine']}" if t.get('schema_engine') else ''
            L.append(f"  {tool:9} {name}: {rep.count('error', tool)} error, {rep.count('warning', tool)} warning, {rep.count('info', tool)} info{extra}")
    s = rep.summary()
    L.append(f"Итог: {s['error']} error · {s['warning']} warning · {s['info']} info → " + ('ворота не пройдены' if s['error'] else 'ворота пройдены'))
    shown = 0
    for f in sorted(rep.findings, key=lambda x: (ORDER[x['level']], TOOL_ORDER.get(x['tool'], 9))):
        if f['level'] == 'info' and not verbose:
            continue
        if shown >= limit:
            L.append(f'  … ещё {len([x for x in rep.findings if verbose or x["level"] != "info"]) - shown} (полный список — --json или --md)')
            break
        frag = f" «{f['fragment']}»" if f.get('fragment') else ''
        L.append(f"  {f['level'].upper():7} {f['tool']:8} {f['rule'][:28]:28} {str(f['where'])[:46]:46}{frag} — {f['message'][:150]}")
        shown += 1
    return '\n'.join(L)


def render_md(rep, title, meta_line):
    s = rep.summary()
    L = [f'# {title}', '', meta_line, '',
         f"**Итог:** {s['error']} error · {s['warning']} warning · {s['info']} info — " + ('ворота не пройдены' if s['error'] else 'ворота пройдены'), '',
         '| Утилита | Версия | error | warning | info |', '|---|---|---|---|---|']
    for tool in ('claims', 'lint', 'validate'):
        if tool in rep.tools or any(f['tool'] == tool for f in rep.findings):
            t = rep.tools.get(tool) or {}
            L.append(f"| {tool} | {t.get('tool') or t.get('schema_engine') or '—'} | {rep.count('error', tool)} | {rep.count('warning', tool)} | {rep.count('info', tool)} |")
    if rep.findings:
        L += ['', '| № | Уровень | Утилита | Правило | Где | Фрагмент | Что не так | Что сделать |', '|---|---|---|---|---|---|---|---|']
        esc = lambda x: str(x or '').replace('|', '\\|').replace('\n', ' ')
        for i, f in enumerate(sorted(rep.findings, key=lambda x: (ORDER[x['level']], TOOL_ORDER.get(x['tool'], 9))), 1):
            L.append(f"| {i} | {f['level']} | {f['tool']} | {esc(f['rule'])} | {esc(f['where'])} | {esc(f.get('fragment', ''))[:60]} | {esc(f['message'])[:200]} | {esc(f.get('fix'))[:160]} |")
    if rep.notes:
        L += ['', '**Заметки:**'] + [f'- {n}' for n in dict.fromkeys(rep.notes)]
    return '\n'.join(L) + '\n'


def write_outputs(a, rep, command, extra=None):
    payload = {'tool': 'copydeck.py', 'version': VERSION, 'date': DATE, 'command': command, 'input': getattr(a, 'deck', None),
               'today': getattr(a, 'today', None), 'summary': rep.summary(), 'tools': rep.tools,
               'findings': sorted(rep.findings, key=lambda x: (ORDER[x['level']], TOOL_ORDER.get(x['tool'], 9))),
               'notes': list(dict.fromkeys(rep.notes))}
    payload.update(extra or {})
    if getattr(a, 'json', None):
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(payload, f, ensure_ascii=False, indent=1, default=str)
    if getattr(a, 'md', None):
        with open(a.md, 'w', encoding='utf-8') as f:
            f.write(render_md(rep, f'copydeck {command} · {os.path.basename(str(getattr(a, "deck", "")))}',
                              f"copydeck.py {VERSION} · {payload['today']} · facts: `{(rep.tools.get('claims') or {}).get('facts') or getattr(a, 'facts', None) or '—'}`"))
    return payload


# ============================================================================================ команды проверок
def open_deck(path):
    try:
        with open(path, encoding='utf-8') as f:
            raw = f.read()
        data = json.loads(raw) if path.lower().endswith('.json') else yaml.safe_load(raw)
    except (OSError, yaml.YAMLError, json.JSONDecodeError) as e:
        raise SystemExit(f'copydeck: не читается {path}: {e}')
    return deep_dates(data)


def resolve_facts_path(a, deck):
    if getattr(a, 'facts', None):
        return a.facts
    ref = deck.get('facts_ref')
    if ref and looks_like_path(ref):
        p = rel_to(a.deck, ref)
        return p if p and os.path.exists(p) else None
    return None


def make_ctx(a, deck):
    fp = resolve_facts_path(a, deck)
    facts = load_facts(fp) if fp else None
    ctx = Ctx(a.deck, facts, today_iso(getattr(a, 'today', None)))
    return ctx, fp


def cmd_validate(a):
    data = open_deck(a.deck)
    deck = deck_root(data)
    ctx, fp = make_ctx(a, deck)
    a.today = ctx.today
    rep = validate(data, ctx, final=a.final, use_jsonschema=not a.no_jsonschema)
    write_outputs(a, rep, 'validate')
    if not a.quiet:
        print(render_text(rep, f'copydeck validate · {a.deck} · {ctx.today} · facts: {fp or "—"}', a.verbose))
    return 2 if rep.count('error') else 0


def cmd_claims(a):
    data = open_deck(a.deck)
    deck = deck_root(data)
    ctx, fp = make_ctx(a, deck)
    a.today = ctx.today
    rep = Report()
    run_claims(deck, ctx, fp, rep, a.strict, a.all_variants)
    write_outputs(a, rep, 'claims')
    if not a.quiet:
        print(render_text(rep, f'copydeck claims · {a.deck} · {ctx.today} · facts: {fp or "— (все числа и имена — без опоры)"}', a.verbose))
    return 2 if rep.count('error') else (1 if not rep.tools.get('claims') else 0)


def cmd_lint(a):
    data = open_deck(a.deck)
    deck = deck_root(data)
    ctx = Ctx(a.deck, None, today_iso(getattr(a, 'today', None)))
    a.today = ctx.today
    rep = Report()
    per = run_lint(deck, ctx, rep, a.final, a.all_variants, not a.no_page_pass)
    write_outputs(a, rep, 'lint', {'slots': per})
    if not a.quiet:
        print(render_text(rep, f'copydeck lint · {a.deck} · {ctx.today}', a.verbose))
    return 2 if rep.count('error') else (1 if per is None else 0)


def _lint_rec(r, prof_default, today, h, tool):
    return {'profile': r.get('profile') or prof_default or 'landing', 'errors': r['errors'], 'warnings': r['warnings'],
            'info': r['info'], 'suppressed': r.get('suppressed', 0), 'verdict': r.get('verdict', 'clean'),
            'checked_at': today, 'text_hash': h, 'tool': tool or 'copy_lint'}


def _claims_rec(r, today, h):
    return {'errors': r['errors'], 'warnings': r['warnings'], 'info': r['info'], 'rules': list(r['rules']),
            'checked_at': today, 'text_hash': h, 'tool': 'claims_check'}


def apply_records(data, claims_pp, lint_pp, today, promote=False, variant_checks=False):
    """Копия deck с записями lint и claims (text_hash проверенного текста) у выбранных вариантов; promote — перевести
    draft → checked там, где свежие claims и lint дали 0 error (checked — статус утилиты, approved — только человек).
    variant_checks (check --all-variants --update) — ещё variant.checks {claims, lint} у каждого живого варианта (I:
    сравнить варианты до выбора; rubric не трогается). Свои fact_ids выбранного варианта переносятся в слот (прямые
    claims_check.py и copy_lint.py читают только слот); варианты без своих fact_ids при этом получают прежний список слота.
    → (копия, число записей, число записей вариантов)."""
    out = _copy.deepcopy(data)
    deck = deck_root(out)
    lint_tool = (f"copy_lint {getattr(lint_module(), 'VERSION', '?')}" if lint_module() else None)
    n = nv = 0
    for page in pages_of(deck):
        pid = page.get('page_id')
        targets = [(f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}", sl) for s in sections_of(page) for sl in slots_of(s)]
        pr = page.get('promise')
        if isinstance(pr, dict) and not pr.get('from') and variants_of(pr):
            targets.append((f'{pid}/promise', pr))
        for path, sl in targets:
            v = chosen_variant(sl)
            if not v:
                continue
            h = text_hash(v.get('text') or '')
            prof_default = (sl.get('lint') or {}).get('profile')
            if lint_pp and path in lint_pp:
                sl['lint'] = _lint_rec(lint_pp[path], prof_default, today, h, lint_tool)
                n += 1
            if claims_pp and path in claims_pp:
                sl['claims'] = _claims_rec(claims_pp[path], today, h)
            if isinstance(v.get('fact_ids'), list) and list(map(str, v['fact_ids'])) != list(map(str, sl.get('fact_ids') or [])):
                old = list(sl.get('fact_ids') or [])
                for x in variants_of(sl):
                    if x is not v and not isinstance(x.get('fact_ids'), list):
                        x['fact_ids'] = old
                sl['fact_ids'] = list(v['fact_ids'])
            sl.setdefault('fact_ids', [])
            sl.setdefault('claim_flags', [])
            if variant_checks:
                for x in variants_of(sl):
                    if x.get('status') == 'rejected' or not str(x.get('text') or '').strip():
                        continue
                    xh = text_hash(x.get('text') or '')
                    lr = (lint_pp or {}).get(path) or {}
                    cr = (claims_pp or {}).get(path) or {}
                    if x is not v:
                        lr = (lr.get('variants') or {}).get(str(x.get('id')))
                        cr = (cr.get('variants') or {}).get(str(x.get('id')))
                    chk = x.get('checks') if isinstance(x.get('checks'), dict) else {}
                    if lr:
                        chk['lint'] = _lint_rec(lr, prof_default, today, xh, lint_tool)
                    if cr:
                        chk['claims'] = _claims_rec(cr, today, xh)
                    if chk:
                        x['checks'] = chk
                        nv += 1
            if promote and v.get('status', 'draft') == 'draft' and lint_pp and claims_pp and path in lint_pp and path in claims_pp \
                    and lint_pp[path]['errors'] == 0 and claims_pp[path]['errors'] == 0:
                v['status'] = 'checked'
                v['review'] = {'by': 'copydeck.py check --promote', 'at': today}
        if variant_checks:  # альтернативы мета (G): итоги — в checks варианта meta.variants.<поле>
            meta = page.get('meta') or {}
            mv = meta.get('variants') if isinstance(meta.get('variants'), dict) else {}
            for k, _st in META_FIELDS:
                path = f'{pid}/meta/{k}'
                for x in mv.get(k) or []:
                    if not isinstance(x, dict) or x.get('status') == 'rejected' or not norm_ws(x.get('text')):
                        continue
                    same = norm_ws(x.get('text')) == norm_ws(meta.get(k))
                    lr = (lint_pp or {}).get(path) or {}
                    cr = (claims_pp or {}).get(path) or {}
                    if not same:
                        lr = (lr.get('variants') or {}).get(str(x.get('id')))
                        cr = (cr.get('variants') or {}).get(str(x.get('id')))
                    chk = x.get('checks') if isinstance(x.get('checks'), dict) else {}
                    xh = text_hash(x.get('text') or '')
                    if lr:
                        chk['lint'] = _lint_rec(lr, 'meta', today, xh, lint_tool)
                    if cr:
                        chk['claims'] = _claims_rec(cr, today, xh)
                    if chk:
                        x['checks'] = chk
                        nv += 1
    return out, n, nv


DECK_REF_FIELDS = ('facts_ref', 'voice_ref', 'copy_slots_ref', 'meaning_ref', 'source_ref', 'page_plan_ref')
PAGE_REF_FIELDS = ('hierarchy_ref',)


def rebase_refs(data, src_path, out_path):
    """Относительные пути copy deck (facts_ref, voice_ref, copy_slots_ref, meaning_ref, source_ref, page_plan_ref,
    hierarchy_ref) — от папки нового файла: копия deck в другой папке (check --update, approve -o, upgrade -o) иначе теряет
    факты и голос (J3: approve в out/ → COPY-D-FACTS-MISSING). Строки-описания (voice_ref без .yaml) не трогаются.
    → число переписанных путей."""
    if not src_path or not out_path:
        return 0
    sd, od = os.path.dirname(os.path.abspath(src_path)), os.path.dirname(os.path.abspath(out_path))
    if sd == od:
        return 0
    n = 0

    def fix(holder, key):
        nonlocal n
        v = holder.get(key)
        if isinstance(v, str) and looks_like_path(v) and not os.path.isabs(v):
            holder[key] = os.path.relpath(os.path.normpath(os.path.join(sd, v)), od)
            n += 1
    deck = deck_root(data)
    for k in DECK_REF_FIELDS:
        fix(deck, k)
    for p in pages_of(deck):
        for k in PAGE_REF_FIELDS:
            fix(p, k)
    return n


def dump_deck(data, path, header, src_path=None):
    """Запись copy deck (YAML); src_path — исходный файл: относительные пути переписываются от папки path (rebase_refs)."""
    if src_path:
        rebase_refs(data, src_path, path)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(header)
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False, width=140, default_flow_style=False)


def cmd_check(a):
    data = open_deck(a.deck)
    deck = deck_root(data)
    ctx, fp = make_ctx(a, deck)
    a.today = ctx.today
    rep = Report()
    claims_pp = run_claims(deck, ctx, fp, rep, a.strict, a.all_variants)           # 1. факты и право
    lint_pp = run_lint(deck, ctx, rep, a.final, a.all_variants, not a.no_page_pass)  # 2. стиль
    fresh = {}
    for p, r in (claims_pp or {}).items():
        fresh.setdefault(p, {})['claims'] = r
    for p, r in (lint_pp or {}).items():
        fresh.setdefault(p, {})['lint'] = r
    validate(data, ctx, rep, final=a.final, use_jsonschema=not a.no_jsonschema, fresh=fresh,
             skip_fact_checks=claims_pp is not None)                              # 3. формат и статусы
    extra = {'slots': {p: fresh[p] for p in sorted(fresh)}}
    if a.update:
        upd, n, nv = apply_records(data, claims_pp, lint_pp, ctx.today, promote=a.promote, variant_checks=a.all_variants)
        st_line = ('draft → checked у текстов с 0 error claims и lint (--promote); approved ставит только человек (approve)'
                   if a.promote else 'статусы не менялись')
        dump_deck(upd, a.update, f'# copy deck — записи lint и claims обновлены copydeck.py check --update · {ctx.today}\n'
                                 f'# источник: {a.deck}; {st_line} (процесс — 10-templates-recipes/01-copy-deck-workflow.md)\n'
                                 + (f'# --all-variants: variant.checks у {nv} вариантов\n' if a.all_variants else ''), src_path=a.deck)
        rep.notes.append(f'--update: записи у {n} текстов' + (f', checks у {nv} вариантов' if a.all_variants else '') + f' → {a.update}')
        extra['updated'] = a.update
    write_outputs(a, rep, 'check', extra)
    if not a.quiet:
        print(render_text(rep, f'copydeck check · {a.deck} · {ctx.today} · facts: {fp or "—"}', a.verbose))
    return 2 if rep.count('error') else 0


# ============================================================================================ export-kimi
COPY_HEADER = ('Keys in square brackets name the element; text after the colon is the exact copy. '
               'Do not translate, shorten or add text.')
TYPO_LINE_RU = ('Typography is final: keep «quotes», dashes (—), non-breaking spaces and «₽» exactly as written; '
                'Russian dashes are grammar, not style.')
FACTS_INTRO = ('Only the facts below may appear on the site. Anything else that looks like a fact (a number, a name, a date, a price,\n'
               'a rating, a client, a quote) is forbidden: write [PLACEHOLDER] instead and list it in REPORT.md.')
NO_EXPORT_SLOTS = {'in-image-text'}   # строки в картинках уходят в спецификацию ассета, не в HTML


def md_cell(s):
    return norm_ws(s).replace('|', '\\|')


def one_line(s):
    return norm_ws(str(s or '').replace('\n', ' '))


def fact_verbatims(f, lang):
    base = (f.get('lang') or 'ru').split('-')[0]
    if lang and lang != base:
        tr = (f.get('translations') or {}).get(lang) or {}
        vs = [x for x in tr.get('verbatim') or [] if x] or ([tr['canonical']] if tr.get('canonical') else [])
        return vs, bool(vs)
    return [x for x in f.get('verbatim') or [] if x], True


def fact_source_line(f):
    src = f.get('source') or {}
    s = ' / '.join(str(src[k]) for k in ('who', 'where', 'date') if src.get(k))
    if src.get('url'):
        s += f" ({src['url']})"
    return s or '—'


def fact_where(f, page):
    use = f.get('use') or {}
    if not use or use.get('any'):
        return 'any section'
    roles = use.get('section_roles') or []
    secs = [str(s.get('section_id')) for s in sections_of(page) if s.get('section_role') in roles or s.get('section_id') in roles]
    parts = []
    if secs:
        parts.append(', '.join(dict.fromkeys(secs)))
    elif roles:
        parts.append('roles: ' + ', '.join(roles))
    if use.get('slot_types'):
        parts.append('slots: ' + ', '.join(use['slot_types']))
    if use.get('not_in'):
        parts.append('not in: ' + ', '.join(use['not_in']))
    if use.get('requires_nearby'):
        parts.append('with: ' + one_line(use['requires_nearby']))
    return '; '.join(parts) or 'any section'


def used_fact_ids(deck, page, facts):
    ids = []
    for u in text_units(deck, page):
        for ref in u['fact_ids']:
            f, _m = facts.resolve(ref) if facts else (None, None)
            if f is not None and f['id'] not in ids:
                ids.append(f['id'])
    ptext, pv, psrc, pr = promise_info(deck, page)
    for ref in (variant_fact_ids(pr, pv) if pr is not None and not pr.get('from') else []):
        f, _m = facts.resolve(ref) if facts else (None, None)
        if f is not None and f['id'] not in ids:
            ids.append(f['id'])
    return ids


def never_rows(facts, today, lang):
    """Never claim: never_claim[] + x-never-claim-defaults без снимающего факта (x-kimi-map B2) → [(id, текст, почему оставлен)]."""
    rows = []
    pub = [f for f in facts.facts if not publish_issues(f, today, facts)] if facts else []
    pub_classes = {c for f in pub for c in f.get('claim_class') or []}
    legal_ok = {c for f in pub for c in f.get('claim_class') or [] if ((f.get('legal') or {}).get('review') or {}).get('status') == 'approved'}
    items = [dict(r, origin='project') for r in (facts.never if facts else [])]
    if not facts or (facts.data.get('never_claim_defaults', 'ru-default-1') != 'none'):
        items += [dict(r, origin='default') for r in load_facts_schema().get('x-never-claim-defaults') or []]
    for r in items:
        lift = r.get('lift', 'never')
        cls = set(r.get('claim_class') or [])
        if lift == 'with-fact' and cls and cls & pub_classes:
            continue
        if lift == 'legal-review' and cls and cls & legal_ok:
            continue
        text = r.get('text') or ''
        if lang == 'en' and r.get('origin') == 'default' and r.get('id') in NEVER_EN:
            text = NEVER_EN[r['id']]
        rows.append((r.get('id'), text, lift))
    return rows


def section_job(section, deck, page, facts, with_facts=False):
    msg = one_line(section.get('message'))
    q = one_line(section.get('question'))
    fids = []
    for sl in slots_of(section):
        for ref in variant_fact_ids(sl, chosen_variant(sl)):
            f, _m = facts.resolve(ref) if facts else (None, None)
            fid = f['id'] if f else str(ref).replace('fact:', '')
            if fid not in fids:
                fids.append(fid)
    base = f'{q} → {msg}' if q and msg else (msg or q or (section.get('section_role') or str(section.get('section_id'))))
    return base + (f'; доказательства: {", ".join(fids)}' if (fids and with_facts) else '')


MEANING_SCHEMA_PATH = os.path.join(ROOT, '02-strategy-messaging', 'meaning.schema.yaml')
DEVICE_RU = {'mobile': 'с телефона', 'desktop': 'с компьютера', 'mixed': 'с телефона и компьютера'}


def _lcfirst(s):
    s = one_line(s)
    return s[:1].lower() + s[1:] if len(s) > 1 and s[1:2].islower() else s


def _source_names():
    names = {}
    try:
        v = load_yaml_file(VOCAB_PATH) or {}
        for x in ((v.get('traffic') or {}).get('sources') or []):
            names[x['id']] = x.get('name') or x['id']
    except Exception:  # noqa: BLE001
        pass
    try:
        ms = load_yaml_file(MEANING_SCHEMA_PATH) or {}
        for x in ((ms.get('x-vocabulary-proposals') or {}).get('traffic.sources') or []):
            names.setdefault(x['id'], x.get('name') or x['id'])
    except Exception:  # noqa: BLE001
        pass
    return names


def derive_from_meaning(meaning, deck):
    """product.target_user, description, viewport_primary и questions из meaning.yaml по x-kimi-map B1:
    target_user — «<сегмент>: <ситуация>. Знает: <что>. Приходит: <источники>, <устройство>»; description — «X — Y. Кому
    важнее всего: Z» (форма «X — Y для Z» B1 без согласования падежа: X — категория словами клиента, Y — главная ценность,
    Z — сегмент best_fit)."""
    m = meaning.get('meaning', meaning) if isinstance(meaning, dict) else {}
    out, notes = {}, []
    aud = [s for s in m.get('audience') or [] if isinstance(s, dict)]
    seg = next((s for s in aud if s.get('primary')), None)
    lvl = (m.get('awareness') or {}).get('level')
    srcs = sorted(((m.get('traffic') or {}).get('sources')) or [], key=lambda x: -(x.get('share') or 0))
    names = _source_names()
    if seg:
        parts = [f"{one_line(seg.get('name'))}: {_lcfirst(seg.get('situation'))}"]
        knows = one_line(seg.get('knows')).split(';')[0].strip()   # первая часть: «кто приходит, что знает» — 1–2 фразы (kimi)
        if knows:
            parts.append(knows if re.match(r'^(знает|не знает)', knows, re.I) else f'Знает: {knows}')
        elif lvl:
            parts.append(f'Уровень осведомлённости: {lvl}')
        if srcs and 'приходит' not in knows.lower():
            top = srcs[:2]
            where = ', '.join(_lcfirst(names.get(x.get('source'), x.get('source'))) for x in top)
            dev = DEVICE_RU.get(top[0].get('device'))
            parts.append(f'Приходит: {where}' + (f', {dev}' if dev else ''))
        out['target_user'] = '. '.join(p.rstrip('.') for p in parts)   # без точки: шаблон TASK.md ставит её сам
    pos = m.get('positioning') or {}
    cat = one_line((pos.get('market_category') or {}).get('name'))
    theme = one_line(((pos.get('value_themes') or [{}])[0] or {}).get('theme'))
    fit_ids = (pos.get('best_fit') or {}).get('segment_ids') or []
    fit = next((s for s in aud if s.get('id') in fit_ids), seg)
    if cat and theme:
        desc = f'{cat[:1].upper()}{cat[1:]} — {_lcfirst(theme)}'
        if fit and fit.get('name'):
            desc += f'. Кому важнее всего: {_lcfirst(fit["name"])}'  # без «для …»: падеж без морфологии не согласовать
        out['description'] = desc
    if srcs and srcs[0].get('device') in ('mobile', 'desktop'):
        out['viewport_primary'] = '390x844' if srcs[0]['device'] == 'mobile' else '1440x900'
    qs = []
    for q in m.get('open_questions') or []:
        if isinstance(q, dict) and q.get('q'):
            item = {'q': one_line(q['q']), 'asked': bool(q.get('asked'))}
            for k in ('answer', 'source', 'date'):
                if q.get(k):
                    item[k] = str(q[k])
            qs.append(item)
    if not seg:
        notes.append('meaning: нет основного сегмента — target_user не выведен')
    return out, qs, notes


def deep_merge(base, over):
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            deep_merge(base[k], v)
        else:
            base[k] = v
    return base


def export_kimi(data, ctx, out_dir, page_id=None, meaning=None, merge_into=None, strict=False, facts_scope='all',
                product_name=None, force=False, facts_path=None, claims_gate=True, job_facts=False):
    """→ (Report, сводка). Пишет copy.md, facts.md, brief-fragment.yaml (+ brief.yaml при merge_into). Ворота: validate
    и claims_check (факты и право) по выгружаемой странице, включая обещание — урок «Кварца»: product.goal с обещанием
    здоровья ушёл в TASK без сверки."""
    rep = Report()
    deck = deck_root(data)
    validate(data, ctx, rep, final=False)
    live = [p for p in pages_of(deck) if (p.get('status') or 'draft') != 'rejected']
    page = None
    if page_id:
        page = next((p for p in live if str(p.get('page_id')) == page_id), None)
        if page is None:
            rep.add('export', 'error', 'COPY-D-EXPORT', page_id, 'нет такой страницы (или она rejected)', '')
    elif len(live) == 1:
        page = live[0]
    else:
        rep.add('export', 'error', 'COPY-D-EXPORT', '—', f'страниц {len(live)}: пакет kimi — одна страница, укажите --page', '')
    if page is not None and strict:  # ворота публикации — только для выгружаемой страницы
        sub = _copy.deepcopy(data)
        deck_root(sub)['pages'] = [p for p in pages_of(deck_root(sub)) if str(p.get('page_id')) == str(page.get('page_id'))]
        rep2 = validate(sub, ctx, final=True)
        seen = {(f['rule'], f['where'], f['message']) for f in rep.findings}
        for f in rep2.findings:
            if (f['rule'], f['where'], f['message']) not in seen:
                rep.findings.append(f)
    ptext = None
    if page is not None:
        ptext, _pv, _psrc, _pr = promise_info(deck, page)
        if not ptext:
            rep.add('export', 'error', 'COPY-D-PROMISE', str(page.get('page_id')), 'нет обещания (promise): product.goal не из чего взять',
                    'Урок «Кварца»: обещание — текст страницы, его пишут и сверяют в copy deck, а не в брифе.')
    if page is not None and claims_gate:
        pp = run_claims(deck, ctx, facts_path, rep, pages=[str(page.get('page_id'))])
        if pp is None:
            rep.add('export', 'error', 'COPY-D-EXPORT', str(page.get('page_id')), 'сверка с фактами не выполнена — выгрузка без ворот честности запрещена', '--no-claims-gate только для опытов.')
    blocking = [f for f in rep.findings if f['level'] == 'error']
    if blocking and not force:
        return rep, None
    if page is None:
        return rep, None
    facts = ctx.facts
    lang = (deck.get('lang') or 'ru').split('-')[0]
    pname = product_name or deck.get('product_name') or deck.get('site') or 'product'
    pid = str(page.get('page_id'))
    os.makedirs(out_dir, exist_ok=True)
    # ---------- copy.md
    vref = deck.get('voice_ref') or ''
    voice_line = vref if (vref and not looks_like_path(vref)) else 'see design_system.tone_of_voice in the brief'
    if looks_like_path(vref) and ctx.deck_path:
        vp = rel_to(ctx.deck_path, vref)
        if vp and os.path.exists(vp):
            tov = load_voice(vp).get('tone_of_voice')   # F: projections.tone_of_voice → «Voice:» copy.md
            if tov:
                voice_line = tov
    ad = deck.get('adaptation') if isinstance(deck.get('adaptation'), dict) else {}
    lang_d = (deck.get('lang') or 'ru').split('-')[0]
    if ad.get('voice_line'):
        voice_line = ad['voice_line']   # v1.1: строка голоса на языке deck (у профиля F проекция — на исходном языке)
    elif lang_d != 'ru' and cyr_share(voice_line) > 0.5:
        rep.add('export', 'warning', 'COPY-D-LANG', '—', f'строка «Voice:» copy.md — на русском, а deck — lang {lang_d}: у профиля голоса нет проекции на этот язык',
                'adaptation.voice_line — строка голоса на языке страницы (предложение F: projections.tone_of_voice по языкам).')
    voice_line = re.sub(r'^\s*черновик:\s*', '', one_line(voice_line)).rstrip('.')
    L = [f'# COPY — all texts of {pname}, verbatim ({lang})', '', f'Voice: {voice_line}.', COPY_HEADER]
    if lang == 'ru':
        L.append(TYPO_LINE_RU)
    L.append('')
    meta = page.get('meta') or {}
    head = [(k, one_line(meta.get(k))) for k, _st in META_FIELDS if str(meta.get(k) or '').strip()]
    if head:
        L += ['## head', '(not a page section: <title>, meta description and Open Graph tags)']
        L += [f'[{k}]: {t}' for k, t in head] + ['']
    n_slots, sections_out, multi = 0, [], []
    for s in sections_of(page):
        rows = []
        for sl in slots_of(s):
            if sl.get('slot_type') in NO_EXPORT_SLOTS:
                continue
            if sl.get('slot_type') in ('image-alt', 'image-caption') and str(sl.get('asset_ref') or '').startswith('assets/'):
                continue  # alt и подпись файла пакета — в brief.yaml assets[] → assets/README.md, не дублируем в copy.md
            v = chosen_variant(sl)
            if v is None and variants_of(sl):
                rep.add('export', 'warning', 'COPY-D-EXPORT', f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}",
                        'слот без выбранного варианта не выгружен в copy.md', 'Выберите вариант (chosen) до выгрузки.')
            if not v or not str(v.get('text') or '').strip():
                continue
            raw = str(v.get('text'))
            if '\n' in raw.strip():
                multi.append(f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}")
            rows.append(f"[{sl.get('slot_id')}]: {one_line(raw)}")
        if rows:
            L += [f"## {s.get('section_id')}"] + rows + ['']
            sections_out.append(s)
            n_slots += len(rows)
    for p in multi:
        rep.add('export', 'warning', 'COPY-D-EXPORT', p, 'абзацы в одном слоте склеены в строку (формат copy.md — строка на ключ)', 'Разбейте прозу на слоты p1, p2…')
    copy_md = '\n'.join(L).rstrip() + '\n'
    with open(os.path.join(out_dir, 'copy.md'), 'w', encoding='utf-8') as f:
        f.write(copy_md)
    # ---------- facts.md
    F = [f'# FACTS — whitelist for {pname}', '', FACTS_INTRO, '', '## Facts', '',
         '| ID | Fact, exactly as it may appear | Source (who / where / date) | Where it may be used |', '|---|---|---|---|']
    M = ['## Missing — show as [PLACEHOLDER]', '', '| ID | What is missing | Text on the page until provided | Who provides |', '|---|---|---|---|']
    n_pub = n_hidden = 0
    used = used_fact_ids(deck, page, facts) if facts else []
    if facts:
        scope = [f for f in facts.facts if facts_scope == 'all' or f['id'] in used]
        for f in scope:
            iss = publish_issues(f, ctx.today, facts)
            if iss:
                why = '; '.join(re.sub(r'^COPY-F-[A-Z-]+:\s*fact:[\w.-]+:\s*', '', x) for x in iss)
                resp = (f.get('responsible') or {}).get('role') or ((facts.data.get('owner') or {}).get('role')) or 'заказчик'
                M.append(f"| {md_cell(f['id'])} | {md_cell(f.get('canonical') or (f.get('verbatim') or [''])[0])} — not publishable yet: {md_cell(why)} "
                         f"| [PLACEHOLDER: {md_cell(f['id'])}] | {md_cell(resp)} |")
                n_hidden += 1
                if f['id'] in used:
                    rep.add('export', 'warning', 'COPY-D-EXPORT', pid, f'fact:{f["id"]} стоит в тексте, но не публикуется: {why}', 'Сверка claims даст error; до исправления — [PLACEHOLDER].')
                continue
            vs, ok = fact_verbatims(f, lang)
            if not ok:
                rep.add('export', 'warning', 'COPY-D-LANG', pid, f'fact:{f["id"]}: нет translations.{lang} — в facts.md ушла формулировка оригинала', '')
                vs = [x for x in f.get('verbatim') or [] if x]
            for i, t in enumerate(vs, 1):
                rid = f['id'] if i == 1 else '%s.%d' % (f['id'], i)
                F.append(f"| {md_cell(rid)} | {md_cell(t)} | {md_cell(fact_source_line(f))} | {md_cell(fact_where(f, page))} |")
            n_pub += 1
        for m in facts.missing:
            M.append(f"| {md_cell(m.get('id'))} | {md_cell(m.get('what'))} | {md_cell(m.get('placeholder'))} | {md_cell(m.get('who'))} |")
    else:
        rep.add('export', 'warning', 'COPY-D-EXPORT', '—', 'facts.yaml не подключён: в facts.md нет фактов — любое число на странице станет [PLACEHOLDER]', '')
    if n_pub == 0:
        F.append('| — | (no facts provided: every fact on the page is a [PLACEHOLDER]) | — | — |')
    if len(M) == 4:
        M.append('| — | nothing missing | — | — |')
    nrows = never_rows(facts, ctx.today, lang)
    N = ['## Never claim'] + ([f'- {one_line(t)};' for _id, t, _lift in nrows] or ['- nothing else.'])
    facts_md = '\n'.join(F + [''] + M + [''] + N) + '\n'
    with open(os.path.join(out_dir, 'facts.md'), 'w', encoding='utf-8') as f:
        f.write(facts_md)
    # ---------- brief fragment
    frag = {'product': {'name': pname, 'goal': one_line(ptext), 'locale': lang}, 'site': {},
            'content': {'copy_source': 'copy.md', 'facts_source': 'facts.md'}}
    if page.get('primary_action'):
        frag['product']['primary_action'] = one_line(page['primary_action'])
    cpath, ctext = primary_cta(deck, page)
    if ctext:
        frag['site']['cta'] = {'label': one_line(ctext)}
    frag['site']['sections'] = [{'id': str(s.get('section_id')), 'job': section_job(s, deck, page, facts, job_facts)} for s in sections_out]
    assets = []
    for s in sections_of(page):
        for sl in slots_of(s):
            ref = str(sl.get('asset_ref') or '')
            v = chosen_variant(sl)
            if ref.startswith('assets/') and v and sl.get('slot_type') in ('image-alt', 'image-caption'):
                a = next((x for x in assets if x['file'] == ref), None)
                if a is None:
                    a = {'file': ref}
                    assets.append(a)
                a['alt' if sl['slot_type'] == 'image-alt' else 'caption'] = one_line(v.get('text'))
    if assets:
        frag['assets'] = assets
    mnotes = []
    unanswered = []
    if meaning:
        derived, qs, mnotes = derive_from_meaning(meaning, deck)
        frag['product'].update(derived)
        # в brief.yaml — только отвеченные вопросы: сборщик kimi кладёт в TASK.md лишь ответы (Decisions), остальное
        # даёт разрыв покрытия; открытые вопросы — заказчику (сводка экспорта), а не исполнителю
        answered = [q for q in qs if q.get('answer')]
        unanswered = [q['q'] for q in qs if not q.get('answer')]
        if answered:
            frag['questions'] = answered
    for n in mnotes:
        rep.add('export', 'info', 'COPY-D-EXPORT', '—', n, '')
    head_c = (f'# brief.yaml fragment — copydeck.py {VERSION} export-kimi · {ctx.today} · deck {os.path.basename(ctx.deck_path or "")}, page {pid}\n'
              '# Вливается в brief.yaml проекта (форма — ../kimi-research/07-brief-handoff/templates/brief.yaml; ключи проходят lint_brief).\n'
              '# product.goal — обещание из copy deck (сверено как текст страницы); site.cta.target и дизайн — вне copy deck.\n')
    with open(os.path.join(out_dir, 'brief-fragment.yaml'), 'w', encoding='utf-8') as f:
        f.write(head_c)
        yaml.safe_dump(frag, f, allow_unicode=True, sort_keys=False, width=140)
    merged_path = None
    base = None
    if merge_into:
        base = load_yaml_file(merge_into) or {}
        bdir = os.path.dirname(os.path.abspath(merge_into))
        for k in ('copy', 'facts', 'missing', 'never_claim'):
            base.pop(k, None)
        for lst in ('references', 'assets'):
            for it in base.get(lst) or []:
                if isinstance(it, dict) and it.get('source') and not os.path.isabs(str(it['source'])):
                    it['source'] = os.path.normpath(os.path.join(bdir, str(it['source'])))
        app = base.get('app') or {}
        if app.get('fixtures_source') and not os.path.isabs(str(app['fixtures_source'])):
            app['fixtures_source'] = os.path.normpath(os.path.join(bdir, str(app['fixtures_source'])))
        fr = _copy.deepcopy(frag)
        fr_assets = fr.pop('assets', [])
        deep_merge(base, fr)
        for a in fr_assets:
            hit = next((x for x in base.get('assets') or [] if isinstance(x, dict) and x.get('file') == a['file']), None)
            if hit:
                hit.update({k: v for k, v in a.items() if k != 'file'})
            else:
                rep.add('export', 'info', 'COPY-D-EXPORT', a['file'], 'ассета нет в brief.yaml: alt и подпись не влиты (файл даёт план ассетов)', '')
        merged_path = os.path.join(out_dir, 'brief.yaml')
        with open(merged_path, 'w', encoding='utf-8') as f:
            f.write(f'# brief.yaml — {os.path.basename(merge_into)} + фрагмент copy deck (copydeck.py export-kimi --merge-into) · {ctx.today}\n'
                    '# copy, facts, missing, never_claim сняты: тексты и факты — файлы copy.md и facts.md (content.*_source).\n')
            yaml.safe_dump(base, f, allow_unicode=True, sort_keys=False, width=140)
    # поля брифа, которые уходят в TASK.md (Promise, The one job, Audience, Sections) — сверка как текст страницы
    btexts = brief_texts(base if merge_into else frag)
    if claims_gate:
        run_claims_text(btexts, ctx, facts_path, rep, tool='brief')
    summary = {'page': pid, 'sections': len(sections_out), 'slots': n_slots, 'head': len(head), 'facts_published': n_pub,
               'facts_hidden': n_hidden, 'missing': len(facts.missing) if facts else 0, 'never_rows': len(nrows),
               'facts_scope': facts_scope, 'files': ['copy.md', 'facts.md', 'brief-fragment.yaml'] + (['brief.yaml'] if merged_path else []),
               'promise': one_line(ptext), 'cta': one_line(ctext) if ctext else None, 'open_questions': unanswered,
               'publish_filter': 'claims_check.publishable_issues' if claims_module() is not None else 'свой (x-kimi-map)'}
    return rep, summary


def cmd_export_kimi(a):
    data = open_deck(a.deck)
    deck = deck_root(data)
    ctx, fp = make_ctx(a, deck)
    meaning = load_yaml_file(a.meaning) if a.meaning else None
    rep, summ = export_kimi(data, ctx, a.out, a.page, meaning, a.merge_into, a.strict, a.facts_scope, a.product_name, a.force,
                            facts_path=fp, claims_gate=not a.no_claims_gate, job_facts=a.job_facts)
    a.today = ctx.today
    write_outputs(a, rep, 'export-kimi', {'export': summ})
    if not a.quiet:
        print(render_text(rep, f'copydeck export-kimi · {a.deck} → {a.out} · facts: {fp or "—"}', a.verbose))
        if summ:
            print('  файлы: ' + ', '.join(os.path.join(a.out, x) for x in summ['files']))
            if summ.get('open_questions'):
                print(f"  открытых вопросов заказчику (в brief.yaml не выгружены): {len(summ['open_questions'])}")
            print(f"  страница {summ['page']}: секций {summ['sections']}, строк {summ['slots']} (+ head {summ['head']}); фактов {summ['facts_published']} "
                  f"(скрыто {summ['facts_hidden']}), пробелов {summ['missing']}, строк Never claim {summ['never_rows']}; фильтр — {summ['publish_filter']}")
        else:
            print('  экспорт не выполнен: исправьте error (или --force для опыта)')
    if summ and [f for f in rep.findings if f['level'] == 'error' and f['tool'] == 'brief']:
        print('  ВНИМАНИЕ: поля брифа не прошли сверку (tool brief) — исправьте их до сборки пакета')
        return 2
    return 0 if summ and not [f for f in rep.findings if f['level'] == 'error' and f['tool'] == 'export'] else 2


# ============================================================================================ import-kimi
def _kimi_slot(key):
    m = claims_module()
    if m is not None and hasattr(m, 'kimi_slot'):
        try:
            st = m.kimi_slot(key)
            if st:
                return st
        except Exception:  # noqa: BLE001
            pass
    for rx, st in KIMI_KEY_SLOT:
        if re.match(rx, key):
            return st
    return None


def safe_id(s):
    s = re.sub(r'[^a-z0-9_-]+', '-', str(s).lower()).strip('-_')
    s = re.sub(r'[-_]{2,}', '-', s)
    return s or 'x'


def import_kimi_copy(text, brief=None, page_id='home', page_type=None, site=None, facts_ref=None, date=None, vocab=None):
    """copy.md пакета kimi (+ brief.yaml) → copy deck v1. → (data, заметки)."""
    notes = []
    date = date or today_iso()
    pname, lang, voice = None, 'ru', ''
    sections, meta, cur, in_head = [], {}, None, False
    for i, line in enumerate(text.splitlines(), 1):
        st = line.strip()
        if not st or st.startswith('{#') or st.startswith('<!--'):
            continue
        m = re.match(r'^#\s+COPY\s+[—-]\s+all texts of\s+(.+?),\s*verbatim\s*\(([a-z]{2})\)', st, re.I)
        if m:
            pname, lang = m.group(1).strip(), m.group(2)
            continue
        if st.startswith('# '):
            continue
        if st.lower().startswith('voice:'):
            voice = st[6:].strip().rstrip('.')
            continue
        if st.lower().startswith(('keys in square brackets', 'typography is final')):
            continue
        m = re.match(r'^##\s+(\S+)', st)
        if m:
            sid = m.group(1)
            in_head = sid == 'head'
            if in_head:
                cur = None
                continue
            role = KIMI_SECTION_ROLE.get(sid) or (sid if vocab and sid in vocab['section_roles'] else None)
            if not role:
                notes.append(f'секция «{sid}»: роль не распознана — section_role не проставлен')
            cur = {'section_id': safe_id(sid)}
            if role:
                cur['section_role'] = role
            cur.update({'block': role or '', 'message': '', 'slots': []})
            sections.append(cur)
            continue
        m = re.match(r'^\[([\w\-]+)\]:\s*(.*)$', st)
        if m:
            key, val = m.group(1), m.group(2)
            if in_head:
                if key in dict(META_FIELDS):
                    meta[key] = val
                else:
                    notes.append(f'head: неизвестный ключ [{key}]')
                continue
            if cur is None:
                cur = {'section_id': 'main', 'block': '', 'message': '', 'slots': []}
                sections.append(cur)
                notes.append(f'стр. {i}: ключ до первой секции — секция main')
            stype = _kimi_slot(key)
            if not stype:
                stype = 'body'
                notes.append(f'[{key}] в «{cur["section_id"]}»: тип не распознан — body')
            cur['slots'].append({'slot_id': safe_id(key) if not re.fullmatch(r'[a-z0-9]+([_-][a-z0-9]+)*', key) else key,
                                 'slot_type': stype, 'variants': [{'id': 'a', 'text': val, 'status': 'draft', 'source': 'imported'}],
                                 'chosen': 'a', 'fact_ids': [], 'claim_flags': [], 'notes': f'copy.md [{key}]'})
            continue
        if in_head and st.startswith('('):
            continue
        if cur is not None:
            n = len(cur['slots']) + 1
            cur['slots'].append({'slot_id': f'text-{n}', 'slot_type': 'body', 'variants': [{'id': 'a', 'text': st, 'status': 'draft', 'source': 'imported'}],
                                 'chosen': 'a', 'fact_ids': [], 'claim_flags': [], 'notes': f'copy.md стр. {i}: строка без ключа'})
            notes.append(f'стр. {i}: строка без [ключа] — слот body')
    page = {'page_id': page_id, 'page_type': page_type or 'landing-product', 'status': 'draft', 'meta': meta, 'sections': sections}
    if not page_type:
        notes.append('page_type не задан (--page-type): поставлен landing-product')
    b = brief or {}
    prod = b.get('product') or {}
    if prod.get('goal'):
        page['promise'] = {'variants': [{'id': 'a', 'text': one_line(prod['goal']), 'status': 'draft', 'source': 'imported'}], 'chosen': 'a',
                           'fact_ids': [], 'claim_flags': [], 'basis': 'brief.yaml product.goal',
                           'notes': 'product.goal → TASK.md «Promise:» → первый экран (ACCEPTANCE A3)'}
    jobs = {str(x.get('id')): x.get('job') for x in ((b.get('site') or {}).get('sections') or []) if isinstance(x, dict)}
    for s in sections:
        j = jobs.get(s['section_id'])
        if j:
            j = one_line(j)
            if ' → ' in j:
                q, msg = j.split(' → ', 1)
                s['question'], s['message'] = q.strip(), msg.split('; доказательства:')[0].strip()
            else:
                s['message'] = j
    label = one_line(((b.get('site') or {}).get('cta') or {}).get('label'))
    if label:
        hit = None
        for s in sections:
            for sl in s['slots']:
                if sl['slot_type'] == 'cta-label' and one_line(sl['variants'][0]['text']) == label:
                    hit = hit or f"{page_id}/{s['section_id']}/{sl['slot_id']}"
        if hit:
            page['cta_primary'] = hit
        else:
            notes.append(f'site.cta.label «{label}» нет среди cta-label copy.md')
    for i, a in enumerate(b.get('assets') or [], 1):
        if not isinstance(a, dict) or not a.get('file'):
            continue
        target = next((s for s in sections if s['section_id'] == safe_id(a.get('slot') or '')), None)
        if target is None and sections:
            target = sections[0]
            notes.append(f"ассет {a['file']}: секции «{a.get('slot')}» нет — alt и подпись в «{target['section_id']}»")
        stem = safe_id(os.path.splitext(os.path.basename(a['file']))[0])
        for key, stype in (('alt', 'image-alt'), ('caption', 'image-caption')):
            if a.get(key) and target is not None:
                target['slots'].append({'slot_id': f'{key}-{stem}', 'slot_type': stype, 'asset_ref': a['file'],
                                        'variants': [{'id': 'a', 'text': one_line(a[key]), 'status': 'draft', 'source': 'imported'}],
                                        'chosen': 'a', 'fact_ids': [], 'claim_flags': [], 'notes': f'brief.yaml assets[{i - 1}].{key}'})
    order = ['page_id', 'page_type', 'status', 'promise', 'cta_primary', 'meta', 'sections']
    page = {k: page[k] for k in order if k in page}
    lang = (prod.get('locale') or lang or 'ru')
    deck = {'version': 1, 'date': date, 'site': safe_id(site or (b.get('project') or {}).get('slug') or 'imported'),
            'product_name': prod.get('name') or pname or '', 'lang': str(lang).split('-')[0],
            'voice_ref': ((b.get('design_system') or {}).get('tone_of_voice') or voice or ''), 'pages': [page]}
    if facts_ref:
        deck['facts_ref'] = facts_ref
    return {'copy_deck': deck}, notes


def cmd_import_kimi(a):
    with open(a.input, encoding='utf-8') as f:
        text = f.read()
    brief = deep_dates(load_yaml_file(a.brief)) if a.brief else None
    fref = os.path.relpath(os.path.abspath(a.facts), os.path.dirname(os.path.abspath(a.output))) if a.facts else None
    data, notes = import_kimi_copy(text, brief, a.page_id, a.page_type, a.site, fref, a.date, load_vocab())
    dump_deck(data, a.output, f'# copy deck v1 — импорт {os.path.basename(a.input)}' + (f' + {os.path.basename(a.brief)}' if a.brief else '') +
              f' (copydeck.py {VERSION} import-kimi · {today_iso(a.date) if a.date else today_iso()})\n'
              '# Тексты дословно, статус draft, fact_ids пустые: ссылки на факты проставляет автор (claims_check находит опору и без них).\n')
    print(a.output)
    for n in notes:
        print('  заметка:', n)
    return 0


# ============================================================================================ export-assets, upgrade
def export_assets(deck, page):
    lang = (deck.get('lang') or 'ru').split('-')[0]
    slots, notes = {}, []
    for s in sections_of(page):
        for sl in slots_of(s):
            st = sl.get('slot_type')
            if st not in ('image-alt', 'image-caption', 'in-image-text'):
                continue
            v = chosen_variant(sl)
            path = f"{page.get('page_id')}/{s.get('section_id')}/{sl.get('slot_id')}"
            ref = sl.get('asset_ref')
            if not ref:
                notes.append(f'{path}: нет asset_ref — пропущен')
                continue
            d = slots.setdefault(ref, {'id': ref, 'from': []})
            d['from'].append(path)
            t = one_line((v or {}).get('text'))
            if st == 'image-alt':
                d['alt'] = t
            elif st == 'image-caption':
                d['caption'] = t
            else:
                ii = sl.get('in_image') or {}
                txt = d.setdefault('text', {'mode': 'in_image', 'strings': [], 'fallback': ii.get('fallback') or 'html_overlay', 'ocr_check': True})
                script = ii.get('script') or ('Cyrillic' if cyr_share(t) > 0.5 else 'Latin')
                txt['strings'].append({'text': t, 'language': lang, 'script': script, 'role': ii.get('role') or 'label', 'position': ''})
                if len(txt['strings']) > 3:
                    notes.append(f'{ref}: строк в картинке {len(txt["strings"])} > 3 (ai-media 05/03 §7)')
    meta = page.get('meta') or {}
    og = {}
    if meta.get('og_image_alt'):
        og['alt'] = one_line(meta['og_image_alt'])
    ogt = page.get('og_template') or {}
    if ogt.get('kicker') or ogt.get('title'):
        og['template_text'] = {k: one_line(ogt[k]) for k in ('kicker', 'title') if ogt.get(k)}
    frag = {'plan_fragment_version': 1, 'source': f'copydeck.py {VERSION} export-assets', 'date': today_iso(),
            'page': {'id': page.get('page_id'), 'locale': lang}, 'slots': list(slots.values())}
    if og:
        frag['og'] = og
    if any('text' in d for d in slots.values()):
        notes.append('position, typography, color строк в картинке задаёт ai-media (asset-spec text.strings[]); здесь только текст, язык, письменность, роль')
    return frag, notes


def cmd_export_assets(a):
    data = open_deck(a.deck)
    deck = deck_root(data)
    live = [p for p in pages_of(deck) if (p.get('status') or 'draft') != 'rejected']
    page = next((p for p in live if str(p.get('page_id')) == a.page), None) if a.page else (live[0] if len(live) == 1 else None)
    if page is None:
        print('copydeck export-assets: укажите --page (страниц несколько или нет такой)', file=sys.stderr)
        return 1
    frag, notes = export_assets(deck, page)
    out = yaml.safe_dump(frag, allow_unicode=True, sort_keys=False, width=140)
    head = f'# фрагмент плана ассетов ai-media (01/01 §8; тексты — asset-spec text) из {os.path.basename(a.deck)}\n'
    if a.output:
        with open(a.output, 'w', encoding='utf-8') as f:
            f.write(head + out)
        print(a.output)
    else:
        print(head + out)
    for n in notes:
        print('  заметка:', n, file=sys.stderr)
    return 0


def upgrade_deck(data, vocab=None):
    out = _copy.deepcopy(data)
    deck = deck_root(out)
    changes = []
    if deck.get('version') in (0, None):
        deck['version'] = 1
        changes.append('version → 1')
    for page in pages_of(deck):
        if 'status' not in page:
            page['status'] = 'draft'
        for s in sections_of(page):
            if not s.get('section_role'):
                sid = str(s.get('section_id'))
                roles = (vocab or {}).get('section_roles') or set()
                guess = s.get('block') if s.get('block') in roles else (KIMI_SECTION_ROLE.get(sid) or (sid if sid in roles else None))
                if guess:
                    s['section_role'] = guess
                    changes.append(f"{page.get('page_id')}/{sid}: section_role = {guess}")
                else:
                    changes.append(f"{page.get('page_id')}/{sid}: section_role не угадан — проставьте руками")
            for sl in slots_of(s):
                for k in ('fact_ids', 'claim_flags'):
                    if k not in sl:
                        sl[k] = []
                for v in variants_of(sl):
                    v.setdefault('status', 'draft')
    return out, changes


def cmd_upgrade(a):
    data = open_deck(a.deck)
    out, changes = upgrade_deck(data, load_vocab())
    dump_deck(out, a.output, f'# copy deck v1 — upgrade из {os.path.basename(a.deck)} (copydeck.py {VERSION} · {today_iso()})\n', src_path=a.deck)
    print(a.output)
    for c in changes:
        print('  ', c)
    return 0


# ============================================================================================ export-variants (слепой выбор)
def _failed_checks(v):
    """Итоги проверок варианта с error для этого же текста (variant.checks, записанные check --all-variants --update)."""
    chk = v.get('checks') if isinstance(v.get('checks'), dict) else {}
    out = []
    for key in ('claims', 'lint'):
        rec = chk.get(key) if isinstance(chk.get(key), dict) else None
        if rec and (rec.get('errors') or 0) > 0 and (not rec.get('text_hash') or rec['text_hash'] == text_hash(v.get('text') or '')):
            out.append(f"{key}: {rec['errors']} error")
    return out


def export_variants(deck, page_ids=None, min_variants=2, seed=0, include_failed=False):
    """Листы для слепого выбора (предложение I): варианты слота под метками A, B, C… в случайном, но воспроизводимом
    порядке, без source/generated (модель скрыта). Мета тоже (G: 2–3 варианта title; выбранный сейчас текст, которого
    нет среди вариантов, идёт под id «meta» — I3). Варианты с error в своих checks (claims или lint этого же текста) на
    лист не идут: выбирают из прошедших ворота; include_failed — показать и их.
    → (markdown, key {путь: {метка: id варианта}}, excluded {путь: [(id, почему)]})."""
    import random
    L = ['# Слепой выбор вариантов', '',
         'Для каждого слота выберите лучший вариант (или ранжируйте). Модели и авторы скрыты; ключ меток — у ведущего.', '']
    key, excluded = {}, {}
    for page in pages_of(deck):
        pid = str(page.get('page_id'))
        if (page_ids and pid not in page_ids) or (page.get('status') or 'draft') == 'rejected':
            continue
        targets = [(f"{pid}/{s.get('section_id')}/{sl.get('slot_id')}", sl.get('slot_type'), variants_of(sl), s) for s in sections_of(page) for sl in slots_of(s)]
        pr = page.get('promise')
        if isinstance(pr, dict) and not pr.get('from'):
            targets.insert(0, (f'{pid}/promise', 'promise', variants_of(pr), None))
        meta = page.get('meta') or {}
        mv = meta.get('variants') if isinstance(meta.get('variants'), dict) else {}
        for k, st in META_FIELDS:
            vs = [v for v in mv.get(k) or [] if isinstance(v, dict)]
            if not vs:
                continue
            if norm_ws(meta.get(k)) and not any(norm_ws(v.get('text')) == norm_ws(meta.get(k)) for v in vs):
                vs = [{'id': 'meta', 'text': meta[k], 'status': 'draft'}] + vs
            targets.append((f'{pid}/meta/{k}', st, vs, None))
        for path, stype, variants, sec in targets:
            vs = [v for v in variants if v.get('status') != 'rejected' and str(v.get('text') or '').strip()]
            if not include_failed:
                bad = [(str(v.get('id')), '; '.join(_failed_checks(v))) for v in vs if _failed_checks(v)]
                if bad:
                    excluded[path] = bad
                    vs = [v for v in vs if not _failed_checks(v)]
            if len(vs) < min_variants:
                continue
            rnd = random.Random(int(hashlib.sha1(f'{seed}:{path}'.encode()).hexdigest()[:8], 16))
            rnd.shuffle(vs)
            labels = [chr(65 + i) for i in range(len(vs))]
            key[path] = {lab: str(v.get('id')) for lab, v in zip(labels, vs)}
            ctx_line = one_line(sec.get('question') or sec.get('message') or '') if sec is not None else ''
            if '/meta/' in path:
                ctx_line = 'как страница выглядит в поиске и в превью ссылки' + (f" (план теста: {one_line(meta.get('test_plan')).rstrip('.')})" if meta.get('test_plan') else '')
            L += [f"## {path} · {stype or 'promise'}"] + ([f'Контекст: {ctx_line}'] if ctx_line else []) + ['']
            L += [f'- **{lab}**: {one_line(v.get("text"))}' for lab, v in zip(labels, vs)] + ['', 'Выбор: ___', '']
    return '\n'.join(L).rstrip() + '\n', key, excluded


def cmd_export_variants(a):
    data = open_deck(a.deck)
    md, key, excluded = export_variants(deck_root(data), [a.page] if a.page else None, a.min, a.seed, a.include_failed)
    with open(a.output, 'w', encoding='utf-8') as f:
        f.write(md)
    with open(a.key, 'w', encoding='utf-8') as f:
        f.write(f'# ключ меток слепого выбора (copydeck.py export-variants, seed {a.seed}) — не показывать выбирающему\n')
        for path, bad in excluded.items():
            f.write(f'# не на листе (error в checks варианта): {path} — ' + ', '.join(f'{i} ({why})' for i, why in bad) + '\n')
        yaml.safe_dump(key, f, allow_unicode=True, sort_keys=False)
    print(f'{a.output} ({len(key)} слотов); ключ — {a.key}')
    for path, bad in excluded.items():
        print(f'  не на листе (error в checks): {path} — ' + ', '.join(f'{i} ({why})' for i, why in bad))
    return 0


# ============================================================================================ approve
def approve_page(data, ctx, page_id, by, at, note=''):
    """Утверждение страницы человеком: все выбранные тексты — checked с актуальным text_hash и 0 error, без [PLACEHOLDER];
    тогда варианты → approved (review), страница → approved (approval). → (новый data | None, Report)."""
    rep = Report()
    out = _copy.deepcopy(data)
    deck = deck_root(out)
    page = next((p for p in pages_of(deck) if str(p.get('page_id')) == page_id), None)
    if page is None:
        rep.add('approve', 'error', 'COPY-D-APPROVE', page_id, 'нет такой страницы', '')
        return None, rep
    targets = [(f"{page_id}/{s.get('section_id')}/{sl.get('slot_id')}", sl) for s in sections_of(page) for sl in slots_of(s)]
    pr = page.get('promise')
    if isinstance(pr, dict) and not pr.get('from') and variants_of(pr):
        targets.append((f'{page_id}/promise', pr))
    for path, sl in targets:
        v = chosen_variant(sl)
        if v is None:
            rep.add('approve', 'error', 'COPY-D-APPROVE', path, 'нет выбранного варианта', '')
            continue
        t = str(v.get('text') or '')
        if _status_of(v) not in ('checked', 'approved'):
            rep.add('approve', 'error', 'COPY-D-APPROVE', path, f'статус {_status_of(v)}: утверждается только проверенный текст', 'copydeck.py check --update OUT --promote')
        for key in ('lint', 'claims'):
            rec = sl.get(key) or {}
            if rec.get('errors', 1) != 0 or rec.get('text_hash') != text_hash(t):
                rep.add('approve', 'error', 'COPY-D-APPROVE', path, f'запись {key}: нет 0 error для этого текста (text_hash)', 'Перепроверьте: check --update.')
        if PLACEHOLDER_RX.search(t):
            rep.add('approve', 'error', 'COPY-D-APPROVE', path, 'в тексте [PLACEHOLDER]', 'Закройте пробел в facts.yaml или перепишите без утверждения.')
    meta = page.get('meta') or {}
    for k in ('title', 'description'):
        if not norm_ws(meta.get(k)):
            rep.add('approve', 'error', 'COPY-D-APPROVE', f'{page_id}/meta/{k}', f'пустое meta.{k}', '')
    if rep.count('error'):
        return None, rep
    for path, sl in targets:
        v = chosen_variant(sl)
        v['status'] = 'approved'
        v['review'] = {'by': by, 'at': at}
    page['status'] = 'approved'
    page['approval'] = {'by': by, 'at': at, **({'note': note} if note else {})}
    return out, rep


def cmd_approve(a):
    data = open_deck(a.deck)
    ctx = Ctx(a.deck, None, today_iso(a.at))
    out, rep = approve_page(data, ctx, a.page, a.by, today_iso(a.at), a.note or '')
    if out is None:
        print(render_text(rep, f'copydeck approve · {a.deck} · страница {a.page}: отказ', True))
        return 2
    dump_deck(out, a.output, f'# copy deck — страница {a.page} утверждена: {a.by}, {today_iso(a.at)} (copydeck.py approve)\n', src_path=a.deck)
    print(a.output)
    return 0


# ============================================================================================ CLI
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--selftest' in argv:
        return selftest()
    if '--version' in argv:
        print(f'copydeck.py {VERSION} ({DATE})')
        return 0
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)

    def common(p, facts=True):
        p.add_argument('deck')
        if facts:
            p.add_argument('--facts', help='facts.yaml (по умолчанию — facts_ref copy deck от его папки)')
        p.add_argument('--today', help='дата сверки ГГГГ-ММ-ДД (по умолчанию — сегодня)')
        p.add_argument('--json')
        p.add_argument('--md')
        p.add_argument('--quiet', action='store_true')
        p.add_argument('--verbose', action='store_true', help='показать и info')
    p = sp.add_parser('validate', help='формат, ссылки, статусы, словарь, факты, файлы волны 2')
    common(p)
    p.add_argument('--final', action='store_true', help='перед публикацией: страница approved, 0 [PLACEHOLDER], мета заполнена')
    p.add_argument('--no-jsonschema', action='store_true', help='встроенная проверка схемы даже при установленном jsonschema')
    p = sp.add_parser('claims', help='claims_check.py (факты B2 + право H) по copy deck')
    common(p)
    p.add_argument('--strict', action='store_true', help='claims_check --strict: утверждения без чисел и маркеров (шумно)')
    p.add_argument('--all-variants', action='store_true')
    p = sp.add_parser('lint', help='copy_lint.py (lint_text) по слотам и страницам')
    common(p, facts=False)
    p.add_argument('--final', action='store_true', help='[PLACEHOLDER] — error')
    p.add_argument('--all-variants', action='store_true')
    p.add_argument('--no-page-pass', action='store_true')
    p = sp.add_parser('check', help='claims → lint → validate')
    common(p)
    p.add_argument('--final', action='store_true')
    p.add_argument('--strict', action='store_true')
    p.add_argument('--no-jsonschema', action='store_true')
    p.add_argument('--no-page-pass', action='store_true')
    p.add_argument('--update', help='записать копию deck с записями lint и claims (text_hash, дата, версия)')
    p.add_argument('--promote', action='store_true', help='с --update: draft → checked у текстов с 0 error claims и lint')
    p.add_argument('--all-variants', action='store_true', help='проверить и живые невыбранные варианты (и альтернативы мета) — каждый как если бы его выбрали; с --update — variant.checks у каждого')
    p = sp.add_parser('export-kimi', help='copy.md, facts.md, brief-fragment.yaml для пакета kimi')
    common(p)
    p.add_argument('--out', required=True, help='папка для файлов пакета')
    p.add_argument('--page', help='id страницы (пакет kimi — одна страница)')
    p.add_argument('--meaning', help='meaning.yaml (B1): target_user, description, viewport_primary, questions')
    p.add_argument('--merge-into', help='brief.yaml проекта: записать в --out слитый brief.yaml')
    p.add_argument('--strict', action='store_true', help='только утверждённая страница, 0 [PLACEHOLDER]')
    p.add_argument('--facts-scope', choices=['all', 'used'], default='all', help='all — все публикуемые факты (x-kimi-map B2); used — только из текстов страницы')
    p.add_argument('--product-name')
    p.add_argument('--force', action='store_true', help='выгрузить, несмотря на error (только для опытов)')
    p.add_argument('--no-claims-gate', action='store_true', help='не запускать claims_check перед выгрузкой (только для опытов)')
    p.add_argument('--job-facts', action='store_true', help='id фактов в job секций (x-kimi-map B1); по умолчанию нет — TASK.md короче, связь факт → секция есть в facts.md')
    p = sp.add_parser('import-kimi', help='copy.md kimi (+ brief.yaml) → copy deck v1')
    p.add_argument('input')
    p.add_argument('-o', '--output', required=True)
    p.add_argument('--brief')
    p.add_argument('--facts', help='facts.yaml — записать facts_ref')
    p.add_argument('--site')
    p.add_argument('--page-id', default='home')
    p.add_argument('--page-type')
    p.add_argument('--date')
    p = sp.add_parser('export-assets', help='alt, подписи, строки в картинках, OG → фрагмент плана ассетов ai-media')
    p.add_argument('deck')
    p.add_argument('--page')
    p.add_argument('-o', '--output')
    p = sp.add_parser('export-variants', help='лист слепого выбора вариантов (метки A, B, C; модели скрыты) и ключ меток')
    p.add_argument('deck')
    p.add_argument('--page')
    p.add_argument('--min', type=int, default=2, help='слоты с не меньшим числом живых вариантов')
    p.add_argument('--seed', type=int, default=0)
    p.add_argument('-o', '--output', required=True, help='Markdown для выбирающего')
    p.add_argument('--key', required=True, help='YAML ключа меток (у ведущего)')
    p.add_argument('--include-failed', action='store_true', help='показать и варианты с error в variant.checks (по умолчанию — только прошедшие ворота)')
    p = sp.add_parser('approve', help='утверждение страницы человеком: checked → approved (review, approval)')
    p.add_argument('deck')
    p.add_argument('--page', required=True)
    p.add_argument('--by', required=True, help='кто утверждает: роль или имя (не агент)')
    p.add_argument('--at', help='дата ГГГГ-ММ-ДД (по умолчанию сегодня)')
    p.add_argument('--note')
    p.add_argument('-o', '--output', required=True)
    p = sp.add_parser('upgrade', help='copy deck v0 → v1')
    p.add_argument('deck')
    p.add_argument('-o', '--output', required=True)
    a = ap.parse_args(argv)
    try:
        return {'validate': cmd_validate, 'claims': cmd_claims, 'lint': cmd_lint, 'check': cmd_check,
                'export-kimi': cmd_export_kimi, 'import-kimi': cmd_import_kimi, 'export-assets': cmd_export_assets,
                'approve': cmd_approve, 'upgrade': cmd_upgrade, 'export-variants': cmd_export_variants}[a.cmd](a)
    except SystemExit as e:
        if isinstance(e.code, str):
            print(e.code, file=sys.stderr)
            return 1
        raise



# ============================================================================================ selftest
def _st_deck(**over):
    """Маленький copy deck v1 для тестов."""
    d = {'copy_deck': {
        'version': 1, 'date': '2026-09-24', 'site': 'demo-site', 'product_name': 'Демо', 'lang': 'ru',
        'voice_ref': 'черновик: на «вы», спокойно', 'facts_ref': 'facts.yaml',
        'pages': [{
            'page_id': 'home', 'page_type': 'landing-lead-services', 'status': 'draft',
            'promise': {'variants': [{'id': 'a', 'text': 'Ремонт без выездов на объект: срок и смета в договоре', 'status': 'draft'}], 'chosen': 'a'},
            'meta': {'title': 'Ремонт квартир под ключ — Демо', 'description': 'Срок и смета в договоре, гарантия 3 года на работы.',
                     'og_title': 'Ремонт под ключ', 'og_description': 'Срок и смета в договоре.'},
            'sections': [
                {'section_id': 'hero', 'section_role': 'hero', 'block': 'hero', 'message': 'Срок и смета — в договоре',
                 'slots': [
                     {'slot_id': 'h1', 'slot_type': 'headline', 'variants': [{'id': 'a', 'text': 'Ремонт квартир под ключ', 'status': 'draft'}], 'chosen': 'a', 'fact_ids': [], 'claim_flags': []},
                     {'slot_id': 'lead', 'slot_type': 'subheadline', 'variants': [{'id': 'a', 'text': 'Гарантия 3 года на работы — пункт 7.2 договора.', 'status': 'draft'}], 'chosen': 'a', 'fact_ids': ['guarantee-3'], 'claim_flags': ['guarantee']},
                     {'slot_id': 'cta', 'slot_type': 'cta-label', 'variants': [{'id': 'a', 'text': 'Вызвать замерщика', 'status': 'draft'}], 'chosen': 'a', 'fact_ids': [], 'claim_flags': []},
                     {'slot_id': 'alt-hero', 'slot_type': 'image-alt', 'asset_ref': 'hero', 'variants': [{'id': 'a', 'text': 'Прораб с рулеткой в пустой комнате', 'status': 'draft'}], 'chosen': 'a'},
                 ]},
                {'section_id': 'faq', 'section_role': 'faq', 'message': 'Ответы до звонка',
                 'slots': [
                     {'slot_id': 'q1', 'slot_type': 'faq-q', 'group': 'q1', 'variants': [{'id': 'a', 'text': 'Сколько стоит замер?', 'status': 'draft'}], 'chosen': 'a'},
                     {'slot_id': 'a1', 'slot_type': 'faq-a', 'group': 'q1', 'variants': [{'id': 'a', 'text': '[PLACEHOLDER: цена замера]', 'status': 'draft'}], 'chosen': 'a', 'missing_ids': ['measure-price']},
                 ]},
            ]}]}}
    d['copy_deck'].update(over)
    return d


def _st_facts():
    return {'facts_version': 1, 'date': '2026-09-24', 'site': 'demo-site', 'lang': 'ru', 'jurisdiction': 'ru',
            'facts': [
                {'id': 'guarantee-3', 'aliases': ['F1'], 'kind': 'guarantee', 'claim_class': ['guarantee'],
                 'verbatim': ['Гарантия 3 года на работы — пункт 7.2 договора'], 'canonical': 'Гарантия 3 года на работы по договору (п. 7.2).',
                 'values': [{'value': 3, 'unit': 'years', 'what': 'гарантийный срок'}],
                 'source': {'type': 'contract', 'who': 'заказчик', 'where': 'договор, п. 7.2', 'date': '2026-01-15', 'document': 'dogovor.pdf',
                            'quote': 'Гарантийный срок на выполненные работы составляет 3 (три) года', 'derivation': 'direct'},
                 'verification': {'status': 'verified'}, 'permission': {'status': 'not-required'},
                 'use': {'section_roles': ['hero', 'guarantee']}, 'legal': {'review': {'status': 'not-needed'}}, 'lang': 'ru'},
                {'id': 'promo-old', 'kind': 'promo', 'claim_class': ['price-discount', 'promo-deadline'], 'verbatim': ['Скидка 10 % до 31 августа'],
                 'canonical': 'Скидка 10 % до 31 августа 2026 года.', 'values': [{'value': 10, 'unit': '%', 'what': 'скидка'}],
                 'source': {'type': 'customer-document', 'who': 'заказчик', 'date': '2026-08-01', 'document': 'prikaz.pdf', 'quote': 'скидка 10% до 31.08.2026'},
                 'verification': {'status': 'verified'}, 'permission': {'status': 'not-required'}, 'valid': {'until': '2026-08-31'}, 'lang': 'ru'},
                {'id': 'city-inferred', 'kind': 'company', 'claim_class': ['origin'], 'verbatim': ['Сборка в Казани'], 'canonical': 'Сборка в Казани.',
                 'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24', 'quote': 'мы стартап из Казани', 'derivation': 'inferred'},
                 'verification': {'status': 'stated'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'},
            ],
            'missing': [{'id': 'measure-price', 'what': 'цена замера', 'placeholder': '[PLACEHOLDER: цена замера]', 'who': 'заказчик'}],
            'never_claim': [{'id': 'nc-eyes', 'text': 'любые обещания про здоровье и зрение', 'claim_class': ['health'],
                             'patterns': ['глаз', 'зрени'], 'lift': 'never', 'voice': 'any'}]}


def selftest():
    import shutil
    ok, bad = [], []

    def check(name, cond, detail=''):
        (ok if cond else bad).append(name)
        if not cond:
            print(f'  FAIL {name}: {detail}')

    td = tempfile.mkdtemp(prefix='copydeck-selftest-')
    try:
        schema = load_copy_schema()
        check('schema: $id и date', schema.get('$id') == 'urn:app-design:text-research:copy-deck:1' and schema.get('date') == '2026-09-24')
        # --- T2: поля v0 есть в схеме (T2 контракта: не удалять и не переименовывать)
        defs = schema['$defs']
        owners = {'copy_deck': schema['properties'], 'page': defs['page']['properties'], 'meta': defs['meta']['properties'],
                  'section': defs['section']['properties'], 'slot': defs['slot']['properties'], 'variant': defs['variant']['properties'],
                  'lint': defs['lint-record']['properties']}
        miss = []
        for path in schema['x-v0-fields']['paths']:
            if path == 'copy_deck':
                continue
            owner, field = path.split('.', 1)
            props = owners['copy_deck'] if owner == 'copy_deck' else owners[owner]
            if owner == 'copy_deck':
                props = defs['deck']['properties']
            if field not in props:
                miss.append(path)
        check('схема: все поля v0 на месте', not miss, miss)
        check('схема: статусы v0', defs['status']['enum'] == schema['x-v0-fields']['status_values_v0'])
        # --- схема: пример и отрицательные случаи; паритет с jsonschema
        sv = SubsetValidator(schema)
        check('схема: пример проходит (встроенная)', not sv.errors(schema['examples'][0]), sv.errors(schema['examples'][0])[:3])
        negs = {}
        d = _st_deck(); del d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['slot_type']; negs['нет slot_type (поле v0)'] = d
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['stauts'] = 'draft'; negs['опечатка в ключе'] = d
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['status'] = 'done'; negs['неизвестный статус'] = d
        d = _st_deck(version=2); negs['version 2'] = d
        d = _st_deck(); d['copy_deck']['pages'][0]['promise'] = {'notes': 'x'}; negs['promise без variants и from'] = d
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['lint_allow'] = [{'rule': 'ru-lex-x'}]; negs['lint_allow без reason'] = d
        d = _st_deck(); d['copy_deck']['pages'][0]['cta_primary'] = 'Home Hero CTA'; negs['cta_primary не путь'] = d
        d = _st_deck(); del d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants']; negs['нет variants (поле v0)'] = d
        for name, dd in negs.items():
            check(f'схема ловит: {name}', bool(sv.errors(dd)), 'нет ошибки')
        try:
            from jsonschema import Draft202012Validator
            jv = Draft202012Validator(schema)
            par = [n for n, dd in negs.items() if bool(list(jv.iter_errors(dd))) != bool(sv.errors(dd))]
            par += [] if bool(list(jv.iter_errors(_st_deck()))) == bool(sv.errors(_st_deck())) else ['позитивный']
            check('схема: встроенная = jsonschema', not par, par)
        except ImportError:
            print('  (jsonschema нет — паритет не проверен; venv-J/bin/python)')
        # --- validate: позитив и смысловые ошибки
        facts = Facts(_st_facts(), os.path.join(td, 'facts.yaml'))
        ctx = Ctx(os.path.join(td, 'deck.yaml'), facts, '2026-09-24', copy_slots_path=os.path.join(td, 'нет.yaml'),
                  meta_rules_path=os.path.join(td, 'нет-meta.yaml'))
        rep = validate(_st_deck(), ctx)
        errs = [f for f in rep.findings if f['level'] == 'error']
        check('validate: чистый deck — 0 error', not errs, [(f['rule'], f['where'], f['message']) for f in errs][:4])
        check('validate: файлы волны 2 нет → warning, не падение', any(f['rule'] == 'COPY-D-RULES-MISSING' and 'copy-slots' in f['message'] for f in rep.findings))

        def rules_of(d, **kw):
            r = validate(d, kw.pop('ctx', ctx), **kw)
            return {(f['rule'], f['level']) for f in r.findings}, r
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['slot_id'] = 'h1'
        check('validate: повтор slot_id', ('COPY-D-ID-DUP', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['chosen'] = 'z'
        check('validate: chosen без варианта', ('COPY-D-CHOSEN', 'error') in rules_of(d)[0])
        d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]
        sl['variants'].append({'id': 'b', 'text': 'Ремонт с гарантией', 'status': 'rejected'}); sl['chosen'] = 'b'
        r0 = rules_of(d)[0]
        check('validate: выбран отклонённый', ('COPY-D-CHOSEN', 'error') in r0)
        check('validate: rejected без reason (v1)', ('COPY-D-REJECTED', 'error') in r0)
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['slot_type'] = 'mega-title'
        check('validate: неизвестный slot_type', ('COPY-D-VOCAB', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][3]['slot_type'] = 'image-caption'
        check('validate: slot_type-предложение → info', ('COPY-D-VOCAB', 'info') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['page_type'] = 'landing-unknown'
        check('validate: неизвестный page_type', ('COPY-D-VOCAB', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['fact_ids'] = ['guarantee-33']
        check('validate: нет факта', ('COPY-D-FACT-REF', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['fact_ids'] = ['missing:measure-price']
        check('validate: пробел в fact_ids', ('COPY-D-FACT-REF', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['fact_ids'] = ['fact:F1']
        check('validate: алиас и префикс fact: принимаются', not any(f['rule'] == 'COPY-D-FACT-REF' for f in rules_of(d)[1].findings))
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['fact_ids'] = ['promo-old']
        check('validate: истёкший факт', ('COPY-D-FACT-EXPIRED', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['fact_ids'] = ['city-inferred']
        check('validate: вывод вместо факта (draft → warning)', ('COPY-D-FACT-UNPUBLISHABLE', 'warning') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][1]['slots'][1]['missing_ids'] = ['measure-cost']
        check('validate: неизвестный missing_ids', ('COPY-D-MISSING-REF', 'error') in rules_of(d)[0])
        # статусы
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['status'] = 'checked'
        check('validate: checked без записей lint и claims', ('COPY-D-STATUS', 'error') in rules_of(d)[0])
        h = text_hash('Ремонт квартир под ключ')
        d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]; sl['variants'][0]['status'] = 'checked'
        sl['lint'] = {'profile': 'landing', 'errors': 0, 'warnings': 0, 'text_hash': h}; sl['claims'] = {'errors': 0, 'warnings': 0, 'text_hash': h}
        r0 = rules_of(d)[0]
        check('validate: checked с записями — без ошибок статуса', not any(r in (('COPY-D-STATUS', 'error'), ('COPY-D-HASH', 'error')) for r in r0), r0)
        sl['variants'][0]['text'] = 'Ремонт квартир под ключ за 60 дней'
        check('validate: текст изменён после проверки (text_hash)', ('COPY-D-HASH', 'error') in rules_of(d)[0])
        d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]; sl['variants'][0]['status'] = 'approved'
        sl['lint'] = {'profile': 'landing', 'errors': 0, 'warnings': 0, 'text_hash': h}; sl['claims'] = {'errors': 0, 'warnings': 0, 'text_hash': h}
        check('validate: approved без review и approval', ('COPY-D-STATUS', 'error') in rules_of(d)[0])
        sl['variants'][0]['review'] = {'by': 'заказчик', 'at': '2026-09-24'}
        check('validate: approved с review', ('COPY-D-STATUS', 'error') not in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['status'] = 'approved'; d['copy_deck']['pages'][0]['approval'] = {'by': 'заказчик', 'at': '2026-09-24'}
        check('validate: страница approved со слотами draft', ('COPY-D-STATUS', 'error') in rules_of(d)[0])
        check('validate: --final ловит [PLACEHOLDER]', ('COPY-D-PLACEHOLDER', 'error') in rules_of(_st_deck(), final=True)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['text'] = 'Ремонт [ЗАГЛУШКА] под ключ'
        check('validate: заглушка не по формату', ('COPY-D-PLACEHOLDER-FORM', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['text'] = 'Ремонт {{product.name}}'
        check('validate: «{{» в тексте (kimi)', ('COPY-D-KIMI-TOKEN', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0].pop('promise')
        check('validate: нет обещания → warning', ('COPY-D-PROMISE', 'warning') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['promise'] = {'from': 'home/hero/leadd'}
        check('validate: promise.from не найден', ('COPY-D-PROMISE', 'error') in rules_of(d)[0])
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'].append(
            {'slot_id': 'img-t', 'slot_type': 'in-image-text', 'asset_ref': 'hero', 'variants': [{'id': 'a', 'text': 'Ремонт квартир под ключ за шестьдесят рабочих дней', 'status': 'draft'}], 'chosen': 'a'})
        r0 = rules_of(d)[0]
        check('validate: строка в картинке > 40 знаков', ('COPY-D-IN-IMAGE', 'error') in r0)
        check('validate: строка в картинке > 4 слов', ('COPY-D-IN-IMAGE', 'warning') in r0)
        d = _st_deck(version=0)
        d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['status'] = 'checked'
        check('validate: v0 — требования статусов мягче', ('COPY-D-STATUS', 'warning') in rules_of(d)[0])
        d = _st_deck(lang='en', source_lang='ru')
        check('validate: адаптация без source_ref', ('COPY-D-LANG', 'warning') in rules_of(d)[0])
        check('validate: кириллица в EN-тексте', any(f['rule'] == 'COPY-D-LANG' and 'кириллица' in f['message'] for f in rules_of(d)[1].findings))
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['claim_flags'] = ['guarantee', 'weird-flag']
        check('validate: неизвестный claim_flags', ('COPY-D-FLAGS', 'warning') in rules_of(d)[0])
        # --- файлы волны 2: copy-slots.yaml (E) в двух формах, голос (F), мета (G)
        cs1 = os.path.join(td, 'cs1.yaml')
        with open(cs1, 'w', encoding='utf-8') as f:
            yaml.safe_dump({'slot_types': [{'id': 'headline', 'length': {'ru': {'words': {'min': 2, 'target': 6, 'max': 3}, 'chars': {'max': 20},
                                                                               'hard_words': [1, 3], 'primary': 'chars'}}},
                                           {'id': 'subheadline', 'fact_required': 'always', 'length': {'ru': {'desktop': {'words': [5, 12, 25]}, 'mobile': {'words': [5, 10, 20]}}}}],
                            'renames': {'cta-label': 'cta-button'}}, f, allow_unicode=True)
        specs, ren, notes = load_copy_slots(cs1)
        check('copy-slots: список и длины (форма 1)', specs['headline']['len'][('ru', 'words')] == [2, 3] and specs['subheadline']['len'][('ru', 'words')] == [5, 25], specs)
        cs2 = os.path.join(td, 'cs2.yaml')
        with open(cs2, 'w', encoding='utf-8') as f:
            yaml.safe_dump({'slots': {'headline': {'lengths': {'en': {'max_words': 8, 'max_chars': 50}}}}}, f)
        specs2, _r, _n = load_copy_slots(cs2)
        check('copy-slots: словарь и плоские ключи (форма 2)', specs2['headline']['len'][('en', 'words')] == [None, 8])
        ctx2 = Ctx(os.path.join(td, 'deck.yaml'), facts, '2026-09-24', copy_slots_path=cs1, meta_rules_path=os.path.join(td, 'нет-meta.yaml'))
        d = _st_deck(); d['copy_deck']['pages'][0]['sections'][0]['slots'][1]['fact_ids'] = []
        r0 = {(f['rule'], f['level']) for f in validate(d, ctx2).findings}
        check('copy-slots E: за грубой границей → warning', ('COPY-D-LEN', 'warning') in r0)
        check('copy-slots E: основная единица > p90 → info', ('COPY-D-LEN', 'info') in r0)
        check('copy-slots: fact_required always', ('COPY-D-FACT-REQUIRED', 'warning') in r0)
        check('copy-slots: переименованный тип', ('COPY-D-SLOT-RENAMED', 'warning') in r0)
        vy = os.path.join(td, 'voice.yaml')
        with open(vy, 'w', encoding='utf-8') as f:
            yaml.safe_dump({'voice_version': 1, 'address': {'ru_form': 'vy', 'capital_vy': False, 'self_reference': 'we'},
                            'vocabulary': {'avoid': [{'term': 'уникальн*', 'reason': 'пустой эпитет', 'use_instead': 'факт отличия'},
                                                     {'term': 'решения под ключ', 'reason': 'штамп', 'level': 'info'}]},
                            'projections': {'tone_of_voice': 'на «вы», спокойно и по делу, без восклицаний'}}, f, allow_unicode=True)
        vo = load_voice(vy)
        check('голос F: обращение, avoid, tone_of_voice', vo['format'] == 'F' and vo['address'] == 'вы' and vo['taboo'][0]['term'] == 'уникальн*' and vo['tone_of_voice'], vo)
        vg = os.path.join(td, 'voice-generic.yaml')
        with open(vg, 'w', encoding='utf-8') as f:
            yaml.safe_dump({'обращение': 'на «ты»', 'lexicon': {'dont_say': ['уникальный']}}, f, allow_unicode=True)
        check('голос: терпимый разбор чужой формы', load_voice(vg)['address'] == 'ты' and load_voice(vg)['format'] == 'generic')
        check('words_rx: «*» и ё/е', bool(words_rx('уникальн*').search('уникальное')) and bool(words_rx('ещё').search('еще')))
        d = _st_deck(voice_ref='voice.yaml'); d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['variants'][0]['text'] = 'Уникальный ремонт для тебя'
        r0 = [f for f in validate(d, ctx2).findings if f['rule'] == 'COPY-D-VOICE']
        check('голос: табу и «ты» при «вы»', len(r0) >= 2, r0)
        mg = os.path.join(td, 'meta-rules.yaml')
        with open(mg, 'w', encoding='utf-8') as f:
            yaml.safe_dump({'limits': {'meta-title': {'ru': {'write': [40, 70], 'info_over': 80, 'warning_over': 110, 'words_min': 3}},
                                       'meta-description': {'ru': {'write': [110, 180], 'warning_under': 60}}},
                            'checks_outside_linter': [{'id': 'meta-x-duplicate-title', 'level': 'error'}, {'id': 'meta-x-missing', 'level': 'error'},
                                                      {'id': 'meta-x-desc-equals-title', 'level': 'warning'}]}, f, allow_unicode=True)
        ctx3 = Ctx(os.path.join(td, 'deck.yaml'), facts, '2026-09-24', copy_slots_path=cs1, meta_rules_path=mg)
        check('мета G: формат распознан', ctx3.meta_rules['format'] == 'G')
        d = _st_deck(); p2 = _copy.deepcopy(d['copy_deck']['pages'][0]); p2['page_id'] = 'home-2'; d['copy_deck']['pages'].append(p2)
        r0 = {(f['rule'], f['level']) for f in validate(d, ctx3).findings}
        check('мета G: дубль title между страницами', ('meta-x-duplicate-title', 'error') in r0)
        check('мета G: description короче warning_under', ('COPY-D-META-LEN', 'warning') in r0)
        d = _st_deck(); m = d['copy_deck']['pages'][0]['meta']
        m['variants'] = {'title': [{'id': 'a', 'text': m['title'], 'status': 'draft'}, {'id': 'b', 'text': 'Ремонт под ключ с гарантией 3 года', 'status': 'draft'},
                                   {'id': 'c', 'text': 'Ремонт без смет', 'status': 'rejected'}]}
        m['review_by'] = '2026-01-01'
        r0 = {(f['rule'], f['level']) for f in validate(d, ctx3).findings}
        check('мета G: варианты title без плана теста → info', ('COPY-D-META-VARIANTS', 'info') in r0)
        check('мета G: отклонённый вариант без reason', ('COPY-D-REJECTED', 'error') in r0)
        check('мета G: review_by в прошлом → warning', ('COPY-D-META-REVIEW', 'warning') in r0)
        flat, _mp, _alt = flatten_for_claims(deck_root(d), ctx3)
        tslot = next(x for x in flat['copy_deck']['pages'][0]['sections'][0]['slots'] if x['slot_id'] == 'title')
        check('мета G: в основной сверке — выбранный title', len(tslot['variants']) == 1 and tslot['chosen'] == 'meta' and not _alt, tslot)
        flat, _mp, alt = flatten_for_claims(deck_root(d), ctx3, alternatives=True)
        check('мета G: --all-variants — живая альтернатива title копией страницы, отклонённая и равная выбранному — нет',
              sorted(alt.values()) == [('home/meta/title', 'b')] and len(flat['copy_deck']['pages']) == 2, sorted(alt.values()))
        d = _st_deck(); d['copy_deck']['pages'][0]['article'] = {'intent': 'выбор подрядчика', 'author': 'fact:lapin-nope', 'unique_angle': {'text': 'график по неделям', 'fact_ids': ['guarantee-3']}}
        r0 = {(f['rule'], f['level'], f['where']) for f in validate(d, ctx3).findings}
        check('статья G: автор — несуществующий факт', ('COPY-D-FACT-REF', 'error', 'home/article/author') in r0)
        if os.path.exists(META_RULES_PATH):
            check('мета G: реальный meta-rules.yaml читается', load_meta_rules(META_RULES_PATH).get('format') in ('G', 'generic'))
        # --- плоская копия для claims_check
        flat, mp, _alt = flatten_for_claims(deck_root(_st_deck()), ctx)
        secs = {s['section_id'] for s in flat['copy_deck']['pages'][0]['sections']}
        check('claims: псевдосекции мета и обещания', {'__head', '__promise', 'hero'} <= secs, secs)
        check('claims: обратная карта путей', mp[('home', '__promise', 'promise')] == 'home/promise' and mp[('home', '__head', 'title')] == 'home/meta/title')
        # --- экспорт в kimi (без процесса claims — быстро) и обратный импорт
        out = os.path.join(td, 'kimi')
        rep_e, summ = export_kimi(_st_deck(), ctx, out, claims_gate=False)
        check('export-kimi: выгружено', summ is not None, [(f['rule'], f['message']) for f in rep_e.findings if f['level'] == 'error'])
        if summ:
            cm = open(os.path.join(out, 'copy.md'), encoding='utf-8').read()
            fm = open(os.path.join(out, 'facts.md'), encoding='utf-8').read()
            fr = yaml.safe_load(open(os.path.join(out, 'brief-fragment.yaml'), encoding='utf-8'))
            check('export-kimi: copy.md — head, секции, ключи', '## head' in cm and '## hero' in cm and '[h1]: Ремонт квартир под ключ' in cm and '[a1]: [PLACEHOLDER: цена замера]' in cm)
            check('export-kimi: нет остатков шаблона', not re.search(r'\{\{|\{#|<UNSET', cm + fm))
            check('export-kimi: факт публикуется, вывод и истёкший — в Missing', '| guarantee-3 |' in fm and '| city-inferred |' in fm.split('## Missing')[1] and '| promo-old |' in fm.split('## Missing')[1])
            check('export-kimi: Never claim — строка проекта и умолчания', 'здоровье и зрение' in fm and 'Рейтинги и звёзды' in fm)
            check('export-kimi: гарантия снимает nc-prices-terms', 'Цены, скидки, сроки доставки' not in fm)
            KNOWN_TOP = {'project', 'product', 'design_system', 'direction', 'references', 'site', 'app', 'feature', 'component', 'content',
                         'copy', 'facts', 'missing', 'never_claim', 'brand', 'assets', 'missing_slots', 'decisions', 'build', 'run', 'questions'}
            check('export-kimi: ключи фрагмента = форма brief.yaml kimi', set(fr) <= KNOWN_TOP and all(set(x) == {'id', 'job'} for x in fr['site']['sections']), fr)
            check('export-kimi: обещание → product.goal, кнопка → site.cta.label', fr['product']['goal'].startswith('Ремонт без выездов') and fr['site']['cta']['label'] == 'Вызвать замерщика')
            dk, notes = import_kimi_copy(cm, {'product': {'goal': fr['product']['goal']}, 'site': fr['site']}, page_type='landing-lead-services', vocab=ctx.vocab)
            out2 = os.path.join(td, 'kimi2')
            _r2, summ2 = export_kimi(dk, Ctx(os.path.join(td, 'deck.yaml'), facts, '2026-09-24', meta_rules_path=os.path.join(td, 'x')), out2, claims_gate=False)
            cm2 = open(os.path.join(out2, 'copy.md'), encoding='utf-8').read() if summ2 else ''
            body = lambda t: t.split('\n## ', 1)[1] if '\n## ' in t else t
            check('import-kimi → export-kimi: copy.md без потерь', body(cm2) == body(cm), (body(cm2)[:200], body(cm)[:200]))
        d = _st_deck(); d['copy_deck']['pages'][0].pop('promise')
        _r, s0 = export_kimi(d, ctx, os.path.join(td, 'kimi3'), claims_gate=False)
        check('export-kimi: без обещания — отказ', s0 is None)
        d = _st_deck(lang='en', source_lang='ru', voice_ref='voice.yaml')
        _r, s1 = export_kimi(d, ctx, os.path.join(td, 'kimi-en'), claims_gate=False)
        check('export-kimi EN: строка Voice профиля на русском → warning COPY-D-LANG (J3)', s1 is not None and any(f['rule'] == 'COPY-D-LANG' and 'Voice' in f['message'] for f in _r.findings), [(f['rule'], f['message'][:60]) for f in _r.findings if f['level'] != 'info'][:4])
        d['copy_deck']['adaptation'] = {'mode': 'adaptation', 'voice_line': 'Address the reader as “you”, calm and precise'}
        _r, s1 = export_kimi(d, ctx, os.path.join(td, 'kimi-en2'), claims_gate=False)
        cm_en = open(os.path.join(td, 'kimi-en2', 'copy.md'), encoding='utf-8').read() if s1 else ''
        check('export-kimi EN: adaptation.voice_line → строка Voice copy.md', 'Voice: Address the reader as “you”, calm and precise.' in cm_en and 'Typography is final' not in cm_en, cm_en[:200])
        bt = dict(brief_texts({'site': {'sections': [{'id': 'final', 'job': 'Что сделать сейчас? → Вызвать замерщика'},
                                                     {'id': 'solution', 'job': 'Решение → Один подрядчик; доказательства: guarantee-3'}]}}))
        check('export-kimi: стрелка в job — граница фразы для сверки брифа', bt.get('brief:site.sections[final].job') == 'Что сделать сейчас? Вызвать замерщика'
              and bt.get('brief:site.sections[solution].job') == 'Решение. Один подрядчик', bt)
        # --- план ассетов и upgrade
        d = _st_deck()
        for i in range(4):
            d['copy_deck']['pages'][0]['sections'][0]['slots'].append({'slot_id': f't{i}', 'slot_type': 'in-image-text', 'asset_ref': 'banner', 'in_image': {'role': 'label'},
                                                                       'variants': [{'id': 'a', 'text': f'Строка {i}', 'status': 'draft'}], 'chosen': 'a'})
        frag, notes = export_assets(deck_root(d), deck_root(d)['pages'][0])
        banner = next(x for x in frag['slots'] if x['id'] == 'banner')
        check('export-assets: строки in_image с языком и письменностью', banner['text']['mode'] == 'in_image' and banner['text']['strings'][0]['script'] == 'Cyrillic')
        check('export-assets: > 3 строк — заметка', any('> 3' in n for n in notes))
        check('export-assets: alt по asset_ref', next(x for x in frag['slots'] if x['id'] == 'hero')['alt'].startswith('Прораб'))
        v0 = {'copy_deck': {'version': 0, 'date': '2026-09-24', 'site': 'x', 'lang': 'ru', 'pages': [{'page_id': 'p', 'page_type': 'landing-saas', 'sections': [
            {'section_id': 'case', 'block': 'case-studies', 'slots': [{'slot_id': 'h', 'slot_type': 'case-title', 'variants': [{'id': 'a', 'text': 'Кейс', 'status': 'draft'}], 'chosen': 'a'}]}]}]}}
        up, ch = upgrade_deck(v0, ctx.vocab)
        check('upgrade: v0 → v1, роль секции из block', deck_root(up)['version'] == 1 and deck_root(up)['pages'][0]['sections'][0]['section_role'] == 'case-studies')
        check('text_hash: пробелы и NBSP не меняют хэш', text_hash('Смета — бесплатно ') == text_hash('Смета — бесплатно'))
        d = _st_deck(facts_ref='../facts/f.yaml', voice_ref='черновик: на «вы»', meaning_ref='m.yaml')
        d['copy_deck']['pages'][0]['hierarchy_ref'] = '../h/h.yaml'
        nre = rebase_refs(d, '/base/decks/deck.yaml', '/base/out/run1/deck.checked.yaml')
        check('rebase_refs: копия deck в другой папке — пути от новой папки, строка голоса не тронута (J3)',
              nre == 3 and d['copy_deck']['facts_ref'] == '../../facts/f.yaml' and d['copy_deck']['meaning_ref'] == '../../decks/m.yaml'
              and d['copy_deck']['pages'][0]['hierarchy_ref'] == '../../h/h.yaml' and d['copy_deck']['voice_ref'].startswith('черновик'), deck_root(d))
        d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]
        sl['variants'] += [{'id': 'b', 'text': 'Ремонт с договором', 'status': 'draft', 'source': 'model', 'generated': {'model': 'x'}},
                           {'id': 'c', 'text': 'Ремонт отклонён', 'status': 'rejected', 'reason': 'тест'}]
        md, key, _ex = export_variants(deck_root(d))
        check('export-variants: метки без модели, отклонённые не показываются', 'home/hero/h1' in key and set(key['home/hero/h1'].values()) == {'a', 'b'}
              and 'model' not in md and 'Ремонт отклонён' not in md, (key, md[:200]))
        check('export-variants: порядок воспроизводим', export_variants(deck_root(d))[1] == key)
        # --- фаза 2 (J3): мета на листе выбора, фильтр вариантов с error, свои факты вариантов, пробелы в check
        m = d['copy_deck']['pages'][0]['meta']
        m['variants'] = {'title': [{'id': 'b', 'text': 'Ремонт под ключ с гарантией 3 года', 'status': 'draft'},
                                   {'id': 'c', 'text': 'Ремонт без смет', 'status': 'rejected', 'reason': 'тест'}]}
        sl['variants'][1]['checks'] = {'claims': {'errors': 1, 'warnings': 0, 'text_hash': text_hash(sl['variants'][1]['text'])}}
        md, key, ex = export_variants(deck_root(d))
        check('export-variants: мета — выбранный title под id «meta» и живые варианты (I3)', key.get('home/meta/title') and set(key['home/meta/title'].values()) == {'meta', 'b'}, key)
        check('export-variants: вариант с error в checks снят с листа, в сводке — почему', 'home/hero/h1' not in key and ex.get('home/hero/h1', [[None]])[0][0] == 'b', (key, ex))
        _md2, key2, _ex2 = export_variants(deck_root(d), include_failed=True)
        check('export-variants: --include-failed возвращает вариант', set(key2.get('home/hero/h1', {}).values()) == {'a', 'b'}, key2)
        d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][1]
        sl['variants'].append({'id': 'b', 'text': 'Смета до договора — бесплатно', 'status': 'draft', 'fact_ids': ['estimate-free']})
        sl['variants'].append({'id': 'c', 'text': 'Старый вариант', 'status': 'rejected', 'reason': 'тест', 'fact_ids': ['nope-old']})
        us = {(u['variant'], tuple(u['fact_ids'])) for u in text_units(deck_root(d), deck_root(d)['pages'][0], all_variants=True) if u['path'] == 'home/hero/lead'}
        check('variant.fact_ids: свои факты варианта заменяют факты слота; отклонённый — не в списке', us == {('a', ('guarantee-3',)), ('b', ('estimate-free',))}, us)
        r0 = validate(d, ctx)
        check('variant.fact_ids: битая ссылка невыбранного варианта — warning с id варианта',
              any(f['rule'] == 'COPY-D-FACT-REF' and f['level'] == 'warning' and f['where'] == 'home/hero/lead/b' for f in r0.findings)
              and not any(f['where'] == 'home/hero/lead/c' for f in r0.findings), [(f['rule'], f['where']) for f in r0.findings if 'FACT' in f['rule']])
        sl['chosen'] = 'b'
        r1 = validate(d, ctx)
        check('variant.fact_ids: выбран вариант со своими фактами → info COPY-D-VARIANT-FACTS', any(f['rule'] == 'COPY-D-VARIANT-FACTS' for f in r1.findings))
        flat, mp, alt = flatten_for_claims(deck_root(d), ctx, alternatives=True)
        lead = next(x for x in flat['copy_deck']['pages'][0]['sections'] if x['section_id'] == 'hero')['slots'][1]
        check('claims: в основной сверке — факты выбранного варианта', lead['fact_ids'] == ['estimate-free'] and [v['id'] for v in lead['variants']] == ['b'], lead)
        check('claims: --all-variants — альтернатива a со своими (слотовыми) фактами, отклонённая c не сверяется',
              ('home/hero/lead', 'a') in alt.values() and ('home/hero/lead', 'c') not in alt.values(), sorted(alt.values()))
        upd, _n, nv = apply_records(d, {'home/hero/lead': {'errors': 0, 'warnings': 0, 'info': 0, 'rules': [], 'variants': {'a': {'errors': 2, 'warnings': 0, 'info': 0, 'rules': ['COPY-F-X']}}}},
                                    {'home/hero/lead': {'profile': 'landing', 'errors': 0, 'warnings': 0, 'info': 0, 'suppressed': 0, 'verdict': 'clean',
                                                        'variants': {'a': {'profile': 'landing', 'errors': 0, 'warnings': 1, 'info': 0, 'suppressed': 0, 'verdict': 'review'}}}},
                                    '2026-09-24', variant_checks=True)
        ul = deck_root(upd)['pages'][0]['sections'][0]['slots'][1]
        va = next(v for v in ul['variants'] if v['id'] == 'a')
        check('check --update: факты выбранного варианта → в слот, прежний список слота — варианту без своих', ul['fact_ids'] == ['estimate-free'] and va.get('fact_ids') == ['guarantee-3'], (ul['fact_ids'], va.get('fact_ids')))
        check('check --all-variants --update: variant.checks у живых вариантов, у отклонённого — нет',
              va['checks']['claims']['errors'] == 2 and va['checks']['lint']['warnings'] == 1 and 'checks' not in next(v for v in ul['variants'] if v['id'] == 'c') and nv == 2, (va.get('checks'), nv))
        rsch = SubsetValidator(schema).errors(upd)
        check('check --all-variants --update: копия проходит схему (variant.fact_ids, checks)', not rsch, rsch[:3])
        fx = _st_facts(); fx['missing'].append({'id': 'min-job', 'what': 'минимальный объём', 'placeholder': '[PLACEHOLDER: минимальный объём]', 'who': 'заказчик', 'fallback': 'omit-block'})
        ctxg = Ctx(os.path.join(td, 'deck.yaml'), Facts(fx, os.path.join(td, 'facts.yaml')), '2026-09-24', copy_slots_path=os.path.join(td, 'нет.yaml'), meta_rules_path=os.path.join(td, 'нет-meta.yaml'))
        d = _st_deck(); a1 = d['copy_deck']['pages'][0]['sections'][1]['slots'][1]
        a1['variants'][0]['text'] = '[PLACEHOLDER: минимальный объём]'; a1['missing_ids'] = ['min-job']
        d['copy_deck']['pages'][0]['sections'][0]['slots'][0]['fact_ids'] = ['nope-fact']
        rs = validate(d, ctxg, skip_fact_checks=True)
        check('check: пробелы и fallback проверяются и при свежей сверке (E3: COPY-D-FALLBACK терялся)', any(f['rule'] == 'COPY-D-FALLBACK' for f in rs.findings), [(f['rule'], f['where']) for f in rs.findings][:6])
        check('check: ссылки фактов при свежей сверке не дублируются (их даёт claims_check)', not any(f['rule'] == 'COPY-D-FACT-REF' for f in rs.findings))
        # --- интеграция: claims_check.py (процесс) и copy_lint.lint_text
        fpath = os.path.join(td, 'facts.yaml')
        with open(fpath, 'w', encoding='utf-8') as f:
            yaml.safe_dump(_st_facts(), f, allow_unicode=True)
        d = _st_deck(); d['copy_deck']['pages'][0]['promise']['variants'][0]['text'] = 'Читайте вечером без усталости глаз'
        if os.path.exists(CLAIMS_CHECK):
            rep_c = Report()
            pp = run_claims(deck_root(d), ctx, fpath, rep_c)
            check('claims: утилита отработала', pp is not None, [f['message'] for f in rep_c.findings][:2])
            check('claims: обещание про глаза → COPY-F-NEVER в home/promise (урок «Кварца»)',
                  any(f['rule'] == 'COPY-F-NEVER' and f['where'] == 'home/promise' for f in rep_c.findings), [(f['rule'], f['where']) for f in rep_c.findings][:6])
            d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]
            sl['variants'] += [{'id': 'b', 'text': 'Ремонт, после которого не болят глаза', 'status': 'rejected', 'reason': 'обещание здоровья'},
                               {'id': 'c', 'text': 'Ремонт, который бережёт зрение', 'status': 'draft'}]
            rep_c = Report()
            pp = run_claims(deck_root(d), ctx, fpath, rep_c, all_variants=True)
            nev = [(f['where'], f.get('variant')) for f in rep_c.findings if f['rule'] == 'COPY-F-NEVER']
            check('claims --all-variants: отклонённый вариант не сверяется, живой — сверяется «как выбранный» (I3)',
                  ('home/hero/h1', 'c') in nev and ('home/hero/h1', 'b') not in nev, nev)
            check('claims --all-variants: итоги варианта отдельно, статус выбранного не задет',
                  pp and pp['home/hero/h1']['errors'] == 0 and pp['home/hero/h1']['variants']['c']['errors'] >= 1, (pp or {}).get('home/hero/h1'))
        else:
            print('  (claims_check.py нет — интеграция не проверена)')
        if lint_module() is not None:
            d = _st_deck()
            sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]
            sl['variants'][0]['text'] = 'Мы предлагаем инновационные решения для вашего бизнеса'
            rep_l = Report()
            pp = run_lint(deck_root(d), ctx, rep_l, page_pass=False)
            hit = [f for f in rep_l.findings if f['where'] == 'home/hero/h1' and f['level'] == 'error']
            check('lint: штамп в заголовке — error', bool(hit), [(f['rule'], f['level']) for f in rep_l.findings if f['where'] == 'home/hero/h1'])
            if hit:
                sl['lint_allow'] = [{'rule': hit[0]['rule'], 'reason': 'слоган из брифа (тест)'}]
                rep_l2 = Report()
                pp2 = run_lint(deck_root(d), ctx, rep_l2, page_pass=False)
                gone = not any(f['rule'] == hit[0]['rule'] and f['where'] == 'home/hero/h1' for f in rep_l2.findings)
                check('lint: lint_allow снимает находку и считает её', gone and pp2['home/hero/h1']['suppressed'] >= 1, pp2.get('home/hero/h1'))
            texts = [('Мы предлагаем инновационные решения для вашего бизнеса', 'landing', 'headline'),
                     ('Смета и выезд замерщика — бесплатно в черте города', 'landing', 'cta-note'),
                     ('Более 1 000 довольных клиентов доверяют нам свои проекты!', 'landing', 'body'),
                     ('Ремонт квартир под ключ в Нижнем Новгороде — Отвес', 'meta', 'meta-title'),
                     ('Не просто сервис, а настоящий партнёр: быстро, качественно, надёжно.', 'site-page', 'subheadline'),
                     ('We help you unlock seamless workflows and supercharge growth.', 'landing', 'headline')]
            C = lint_module()
            sig = lambda r: (r['summary']['error'], r['summary']['warning'], r['summary']['info'],
                             sorted((f['id'], f['level'], f.get('fragment')) for f in r.get('findings') or []))
            with_cache = [sig(C.lint_text(t, genre=g, slot_type=st)) for t, g, st in texts]
            lint_cache(False)
            without = [sig(C.lint_text(t, genre=g, slot_type=st)) for t, g, st in texts]
            lint_cache(True)
            again = [sig(C.lint_text(t, genre=g, slot_type=st)) for t, g, st in texts]
            check('lint: кэш загрузки правил не меняет находок (6 текстов, RU и EN)', with_cache == without == again,
                  [i for i, (a, b) in enumerate(zip(with_cache, without)) if a != b])
            rep_l3 = Report()
            run_lint(deck_root(_st_deck()), ctx, rep_l3, final=True, page_pass=True)
            check('lint: --final — [PLACEHOLDER] становится error', any(f['rule'] == 'art-placeholder-marker' and f['level'] == 'error' for f in rep_l3.findings))
            check('lint: проход страницы дал метрики', True)
            d = _st_deck(); sl = d['copy_deck']['pages'][0]['sections'][0]['slots'][0]
            sl['variants'].append({'id': 'b', 'text': 'Мы предлагаем инновационные решения для вашего бизнеса', 'status': 'draft'})
            rep_l4 = Report()
            pp4 = run_lint(deck_root(d), ctx, rep_l4, all_variants=True, page_pass=False)
            check('lint --all-variants: находки альтернативы — в её итогах, выбранный текст чист',
                  pp4['home/hero/h1']['errors'] == 0 and pp4['home/hero/h1']['variants']['b']['errors'] >= 1, pp4.get('home/hero/h1'))
            d = _st_deck(); d['copy_deck']['pages'][0]['meta']['title'] = 'Ремонт квартир за 45 дней по договору — Демо'
            d['copy_deck']['pages'][0]['meta']['fact_ids'] = ['guarantee-3']
            rep_l5 = Report()
            run_lint(deck_root(d), ctx, rep_l5, page_pass=False)
            par = (rep_l5.tools.get('lint') or {}).get('parity_copy_lint') or {}
            check('lint: meta.fact_ids снимают число в мета — заметка паритета с copy_lint.py (E3, J/05)',
                  par.get('meta_fact_ids', 0) >= 1 and any('meta.fact_ids' in n for n in rep_l5.notes), (par, rep_l5.notes[:2]))
        else:
            print('  (copy_lint.py не импортируется — интеграция не проверена)')
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print(f'copydeck.py {VERSION} selftest: {len(ok)} OK, {len(bad)} FAIL')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
