#!/usr/bin/env python3
"""claims_check.py — сверка текстов сайта с белым списком фактов (facts.yaml): ядро «контура честности» text-research.

Агент B2 (волна 1), 2026-09-24. Модель не вызывается; сеть не нужна. Python 3.10+, PyYAML (системный или
99-raw/tools/venv-B2). Правовые правила (классы → требования → оговорки) добавляет H в волне 2 внешним файлом
08-russian-legal-typography/claims-rules.yaml (подхватывается сам, если есть; формат — `rules-schema`).
Правовой модуль H (волна 2, 2026-09-24): правила права по юрисдикции (--jurisdiction ru|eu|us, по умолчанию из
facts.yaml или ru) и отрасли (--legal-category, из copy deck legal_category или general); --legal-only — только находки
права; условия снятия: оговорка рядом (unless, nearby, nearby_all), поля факта, условия факта (qualifier, disclaimer).

Что делает (спецификация — 02-strategy-messaging/03-proof-and-facts.md §7):
  извлекает из текста числа (единицы, %, валюта, диапазоны, «от/до/более», «+», тыс./млн), даты, годы, рейтинги
  («4,9 из 5», звёзды), цитаты в «ёлочках» и "кавычках", счётчики, имена и названия (эвристика + сущности facts.yaml),
  маркеры 20 классов утверждений (лучший, № 1, гарантируем, бесплатно, вылечит, доход, сборка, сертификат…) и термины
  свойств (датчик, аккумулятор, материал…); сопоставляет с фактами дословно и по нормализованному значению с единицей и
  объектом счёта; проверяет сам факт: разрешение, срок, основание (дословная выдержка источника), вывод вместо факта,
  проверку юриста для рискованных классов; never_claim (проектный + набор по умолчанию из facts.schema.yaml);
  [PLACEHOLDER] — info со счётчиком.

Входы (формат определяется сам или --format):
  copy deck v0 (PLAN.md «Как всё сочетается»: copy_deck.pages[].sections[].slots[] — slot_type, variants[].text, chosen,
  fact_ids, claim_flags) · copy.md пакета kimi («## секция» + «[ключ]: текст») · Markdown · текст · HTML.

Подкоманды:
  [check] INPUT [--facts facts.yaml] [--format auto|deck|kimi-md|md|text|html] [--rules FILE ...] [--no-external-rules]
          [--no-default-never] [--today ГГГГ-ММ-ДД] [--genre landing] [--all-variants] [--strict] [--verbose]
          [--json OUT] [--md OUT] [--quiet] [--jurisdiction ru|eu|us|other] [--legal-category finance,medical,…]
          [--legal-only]
          exit 0 — нет error; 2 — есть error; 1 — ошибка входа или утилиты
  inventory INPUT [--format …] [--json OUT] [--md OUT]  — без фактов: утверждения по классам и видимый ли источник на
          странице (метрика «доля утверждений с видимым источником», опыт B2/04); exit 0
  lint-facts FACTS [--today …] — проверка самого инвентаря (вывод без основания, истёкшие, без разрешений); exit 0/2/1
  import-kimi FACTS.md [-o facts.yaml] [--site slug] [--date ГГГГ-ММ-ДД] — facts.md пакета kimi → facts.yaml v1
          (черновик для сверки; обратный экспорт facts.yaml → facts.md пишет J в copydeck.py)
  rules-schema — JSON Schema формата claims-rules.yaml (для H)
  --selftest — офлайн-тесты извлечения, сопоставления, правил и ложных срабатываний; exit 0/1

Идеи и часть кода взяты из ../kimi-research/99-raw/tools/k3_checks.py (агент G kimi, 2026-09-24): нормализация кавычек
и тире (QUOTES, norm_text), разбор чисел с разделителями тысяч (NUM_RX, extract_numbers), логика F-NUMBERS (число
страницы против чисел колонок «Fact…» facts.md) и F-QUOTE (цитата ≥ 5 слов без источника), разбор таблиц facts.md
(fact_text) — переписаны: у числа здесь есть единица, объект счёта и сравнение, у цитаты — многоточия и правки.
Правила ux: ../ux-research/07-ux-writing/06-banned-words-and-patterns.md §5.2 (регулярки соцдоказательств),
../ux-research/06-feedback-states-motion/04-dark-patterns-and-ethics.md §8.1 п.10–12, 22.

Идентификаторы правил — префикс COPY-F- (контракт тройки v2 §3 п.16); правила H — свои id (рекомендация COPY-L-).
Это не юридическое заключение: классы и флаги показывают, где нужна проверка права (H, юрист заказчика).
"""
import argparse, copy, datetime as dt, difflib, fnmatch, html.parser, json, os, re, sys, tempfile, unicodedata

VERSION = '1.0'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))  # перенос: scripts/lib
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('text'))
SCHEMA_PATH = os.path.join(ROOT, '02-strategy-messaging', 'facts.schema.yaml')
RULES_PATH = os.path.join(ROOT, '08-russian-legal-typography', 'claims-rules.yaml')
VOCAB_PATH = os.path.join(ROOT, '99-raw', 'notes', 'temp-vocabulary-v0.yaml')

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

LEVELS = ('error', 'warning', 'info')

# ================================================================ нормализация текста (идея — k3_checks.norm_text)
SPACES = {'\u00a0': ' ', '\u202f': ' ', '\u2009': ' ', '\u2007': ' ', '\u2002': ' ', '\u2003': ' ', '\u200b': ''}
DASHES = {'—': '-', '–': '-', '‑': '-', '−': '-', '‒': '-'}
QUOTES = {'«': '"', '»': '"', '“': '"', '”': '"', '„': '"', '‟': '"', '’': "'", '‘': "'", '‚': "'"}
_SOFT = str.maketrans({**SPACES, **DASHES, 'ё': 'е', 'Ё': 'Е'})
_HARD = str.maketrans({**SPACES, **DASHES, **QUOTES, 'ё': 'е', 'Ё': 'Е'})


def soft(s):
    """Для маркеров: пробелы и тире приведены, ё → е, нижний регистр; кавычки и знаки (№, ₽, ★) сохранены."""
    return re.sub(r'[ \t]+', ' ', (s or '').translate(_SOFT)).lower()


def norm(s):
    """Для сравнения текстов: NFKC, кавычки → ", тире → -, ё → е, многоточие → ..., нижний регистр, один пробел."""
    s = unicodedata.normalize('NFKC', (s or '').translate(_HARD))
    s = s.translate(_HARD).replace('…', '...')
    s = re.sub(r'[*_`#>|]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


WORD_RX = re.compile(r"[a-zа-я0-9]+(?:[-'][a-zа-я0-9]+)*")
RU_END = sorted(['иями', 'ями', 'ами', 'ого', 'его', 'ому', 'ему', 'ыми', 'ими', 'ых', 'их', 'ой', 'ей', 'ий', 'ый',
                 'ая', 'яя', 'ое', 'ее', 'ые', 'ие', 'ую', 'юю', 'ов', 'ев', 'ам', 'ям', 'ах', 'ях', 'ом', 'ем', 'ия',
                 'ья', 'ье', 'ии', 'ью', 'ию', 'ть', 'ет', 'ит', 'ут', 'ют', 'ат', 'ят', 'ешь', 'ишь', 'ем', 'им',
                 'ла', 'ло', 'ли', 'а', 'я', 'о', 'е', 'и', 'ы', 'у', 'ю', 'ь', 'й'], key=len, reverse=True)
EN_END = ['ings', 'ing', 'ies', 'ied', 'es', 'ed', 's']


def stem(w):
    w = w.lower().replace('ё', 'е')
    if re.fullmatch(r'[0-9]+', w):
        return w
    if re.search(r'[а-я]', w):
        if len(w) <= 3:
            return w
        for e in RU_END:
            if w.endswith(e) and len(w) - len(e) >= 3:
                return w[:-len(e)][:7]
        return w[:7]
    if len(w) <= 3:
        return w
    for e in EN_END:
        if w.endswith(e) and len(w) - len(e) >= 3:
            return w[:-len(e)][:7]
    return w[:7]


STOP = set('''а и в во на по с со к ко о об обо от до из за для у же ли бы не ни но да или как что это эта этот эти то
так там тут вот где когда кто чем при над под про через без между уже еще ещё все всё всех весь вся мы вы вас вам ваш
ваша ваше ваши наш наша наше наши нас нам он она оно они его ее её их им ими ей ему себя свой своя свое свои который
которая которое которые быть был была было были будет будут есть сам сама само сами также только даже очень более
менее можно нужно надо мы—
the a an and or of to in on for with by from at as is are be been was were it its this that these those your our you we
they he she them his her not no yes do does did can will just than then so if into about over under more less'''.split())


def tokens(s):
    return WORD_RX.findall(norm(s))


def stems(s, drop_stop=True):
    return {stem(t) for t in tokens(s) if not (drop_stop and t in STOP) and not t.isdigit()}


def as_str_date(v):
    if isinstance(v, (dt.date, dt.datetime)):
        return v.isoformat()[:10]
    return v


def deep_dates(x):
    if isinstance(x, dict):
        return {str(k): deep_dates(v) for k, v in x.items()}
    if isinstance(x, list):
        return [deep_dates(v) for v in x]
    return as_str_date(x)


def parse_iso(s):
    """'2026-12-31' → (2026,12,31); '2026-12' → (2026,12,None); иначе None."""
    s = as_str_date(s)
    if not isinstance(s, str):
        return None
    m = re.fullmatch(r'(\d{4})-(\d{2})(?:-(\d{2}))?', s.strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), (int(m.group(3)) if m.group(3) else None)


def date_end(t):
    """Последний день периода кортежа (г, м, д|None) → date."""
    y, m, d = t
    if d:
        return dt.date(y, m, d)
    nm = dt.date(y + (m == 12), (m % 12) + 1, 1)
    return nm - dt.timedelta(days=1)


# ================================================================ единицы, числа, даты, рейтинги
MONTHS = {
    'январ': 1, 'феврал': 2, 'март': 3, 'апрел': 4, 'мая': 5, 'май': 5, 'мае': 5, 'июн': 6, 'июл': 7, 'август': 8,
    'сентябр': 9, 'октябр': 10, 'ноябр': 11, 'декабр': 12,
    'january': 1, 'jan': 1, 'february': 2, 'feb': 2, 'march': 3, 'mar': 3, 'april': 4, 'apr': 4, 'may': 5, 'june': 6,
    'jun': 6, 'july': 7, 'jul': 7, 'august': 8, 'aug': 8, 'september': 9, 'sept': 9, 'sep': 9, 'october': 10,
    'oct': 10, 'november': 11, 'nov': 11, 'december': 12, 'dec': 12}
MONTH_RX = (r'(январ[ьяе]|феврал[ьяе]|март[ае]?|апрел[ьяе]|ма[йяе]|июн[ьяе]|июл[ьяе]|август[ае]?|сентябр[ьяе]|'
            r'октябр[ьяе]|ноябр[ьяе]|декабр[ьяе]|january|february|march|april|may|june|july|august|september|'
            r'october|november|december|jan|feb|mar|apr|jun|jul|aug|sept|sep|oct|nov|dec)\.?')

UNIT_MAP = [  # (регулярка единицы сразу после числа, нормализованная единица) — порядок важен
    (r'₽|руб\.?(?:л[а-я]*)?|р\.(?!\w)|rub\b', 'RUB'),
    (r'\$|usd\b|долл\.?(?:ар[а-я]*)?', 'USD'),
    (r'€|eur\b|евро\b', 'EUR'),
    (r'%|процент[а-я]*|п\.\s?п\.', '%'),
    (r'квт\b|kw\b', 'kW'), (r'вт\b|w\b', 'W'),
    (r'мач\b|mah\b', 'mAh'), (r'гб\b|gb\b', 'GB'), (r'мб\b|mb\b', 'MB'), (r'тб\b|tb\b', 'TB'),
    (r'ггц\b|ghz\b', 'GHz'), (r'гц\b|hz\b', 'Hz'),
    (r'м²|м2\b|кв\.\s?м\.?|sq\.?\s?m\b', 'm2'), (r'км\b|km\b', 'km'), (r'мм\b|mm\b', 'mm'), (r'см\b|cm\b', 'cm'),
    (r'м\b(?!\w)', 'm'), (r'кг\b|kg\b', 'kg'), (r'г\b(?!\.?\s?\d)', 'g'), (r'мл\b|ml\b', 'ml'), (r'л\b', 'l'),
    (r'k\b(?!\w)', 'K'),  # кельвин, только если отделено пробелом (слитное 10k — тысячи)
    (r'дн[а-я]*\.?|день|суток|сутки|days?\b', 'days'), (r'рабоч[а-я]+\s+дн[а-я]*', 'days'),
    (r'час[а-я]*|ч\b\.?|hours?\b|hrs?\b', 'hours'), (r'мин[а-я]*\.?|minutes?\b|mins?\b', 'minutes'),
    (r'сек[а-я]*\.?|seconds?\b|secs?\b', 'seconds'), (r'недел[а-я]*|weeks?\b', 'weeks'),
    (r'месяц[а-я]*|мес\.?|months?\b', 'months'), (r'лет\b|год[а-я]*|years?\b|yrs?\b', 'years'),
    (r'шт\.?|штук[а-я]*|pcs\b|pieces?\b', 'pcs'), (r'раз[а]?\b|times\b', 'times'),
    (r'звезд[а-я]*|stars?\b', 'stars'), (r'человек[а-я]*|чел\.?|people\b|persons?\b', 'people'),
]
UNIT_RX = [(re.compile(r'\s?(?:' + rx + r')', re.I), u) for rx, u in UNIT_MAP]
UNIT_SYNONYMS = {'rub': 'RUB', '₽': 'RUB', 'руб': 'RUB', 'usd': 'USD', '$': 'USD', 'eur': 'EUR', '€': 'EUR',
                 '%': '%', 'percent': '%', 'k': 'K', 'kelvin': 'K', 'w': 'W', 'вт': 'W', 'kw': 'kW', 'day': 'days',
                 'days': 'days', 'дней': 'days', 'hour': 'hours', 'hours': 'hours', 'minute': 'minutes',
                 'minutes': 'minutes', 'year': 'year', 'years': 'years', 'лет': 'years', 'month': 'months',
                 'months': 'months', 'pcs': 'pcs', 'шт': 'pcs', 'items': 'pcs', 'star': 'stars', 'stars': 'stars',
                 'm2': 'm2', 'м2': 'm2', 'sqm': 'm2', 'people': 'people', 'times': 'times', 'weeks': 'weeks',
                 'kg': 'kg', 'km': 'km', 'mm': 'mm', 'cm': 'cm', 'm': 'm', 'mah': 'mAh', 'gb': 'GB'}
MONEY = {'RUB', 'USD', 'EUR'}
COUNT_UNITS = {None, 'pcs', 'people'}

STRUCT_NOUNS = {stem(w) for w in 'шаг шага шагов пункт пункта причина причины причин способ способа способов совет '
                'совета советов вопрос вопроса вопросов этап этапа этапов step steps reason reasons tip tips way ways '
                'question questions минуты чтения'.split()}

MULT = [(r'\s?(?:тыс\.?|тысяч[а-я]*)', 1e3), (r'\s?(?:млн\.?|миллион[а-я]*)', 1e6), (r'\s?(?:млрд\.?|миллиард[а-я]*)', 1e9),
        (r'(?:k|к)(?=\+|\b)', 1e3), (r'(?:m)(?=\+|\b)', 1e6), (r'(?:b)(?=\+|\b)', 1e9), (r'\s(?:thousand|million|billion)', None)]
MULT_RX = [(re.compile(rx, re.I), f) for rx, f in MULT]
EN_BIG = {'thousand': 1e3, 'million': 1e6, 'billion': 1e9}

NUM_RX = re.compile(r'(?<![\w.,/:-])(\d{1,3}(?:[ \u00a0\u202f\u2009]\d{3})+|\d+)(?:[.,](\d+))?(?![\w])', re.U)
PREFIX_CMP = [
    (r'(?:от|с)\s*$', 'gte'), (r'(?:до|вплоть до|up to|within|в течение|в пределах)\s*$', 'lte'),
    (r'(?:более|больше|свыше|over|more than|above|>)\s*$', 'gt'),
    (r'(?:не менее|не меньше|минимум|at least|min\.?|≥)\s*$', 'gte'),
    (r'(?:менее|меньше|under|less than|below|<)\s*$', 'lt'), (r'(?:не более|не больше|максимум|at most|≤)\s*$', 'lte'),
    (r'(?:около|примерно|почти|порядка|приблизительно|about|around|nearly|approximately|~|≈)\s*$', 'approx')]
PREFIX_CMP_RX = [(re.compile(rx, re.I), c) for rx, c in PREFIX_CMP]

DATE_DMY = re.compile(r'(?<!\d)(\d{1,2})\.(\d{1,2})\.(\d{4}|\d{2})(?!\d)')
DATE_ISO = re.compile(r'(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)')
DATE_TEXT = re.compile(r'(?<!\d)(?:(\d{1,2})\s+)?' + MONTH_RX + r'(?:\s+(\d{4}))?(?:\s*(?:г\.|года|году|год))?', re.I)
YEAR_RX = re.compile(r'(?<!\d)((?:19|20)\d{2})(?:\s*(?:г\.|года|году|год|гг\.))?(?!\d)')
TIME_RX = re.compile(r'(?<!\d)\d{1,2}:\d{2}(?:\s*[-–—]\s*\d{1,2}:\d{2})?')
PHONE_RX = re.compile(r'(?:\+7|(?<!\d)8)[\s(\-]*\d{3}[\s)\-]*\d{3}[\s\-]*\d{2}[\s\-]*\d{2}(?!\d)|\+\d{1,3}[\s(\-]*\d{2,4}[\s)\-]*\d{3}[\s\-]*\d{2,4}(?:[\s\-]*\d{2,4})?')
EMAIL_RX = re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+')
URL_RX = re.compile(r'https?://\S+|www\.\S+')
LAWREF_RX = re.compile(r'\d+(?:\.\d+)?-ФЗ|ФЗ-\d+|\b(?:ст|ч|п|пп|стр|гл|разд)\.\s?\d+(?:\.\d+)*|\b(?:пункт[а-я]*|раздел[а-я]*|стать[а-я]*|глав[а-я]*|част[а-я]*|приложени[а-я]*|clause|section|article)\s+\d+(?:\.\d+)*|№\s?\d[\d\-/]*\d|№\s?\d(?=\D)(?!\s*(?:в|на|среди|по)\b)|\bГОСТ(?:\s?Р)?\s?[\d.\-]+|\bISO\s?\d+(?::\d+)?|\bIP\s?\d{2}\b|\bТУ\s?[\d.\-]+|\bSOC\s?[12]\b|\bAES-?\d{3}\b|\bPCI\s?DSS\b|\bWi-?Fi\s?\d\b|\bUSB\s?\d(?:\.\d)?\b|\bHTTP/\d(?:\.\d)?\b|\b[245]G\b', re.I)
COPYRIGHT_RX = re.compile(r'(?:©|\(c\)|copyright)\s*(?:\d{4}\s*[-–—]\s*)?\d{4}', re.I)
RATING_RX = re.compile(
    r'(?<![\d.,])(\d(?:[.,]\d{1,2})?)\s*(?:из|/|out of)\s*(5|10|100)(?!\d)|'
    r'(?<![\d.,])(\d(?:[.,]\d{1,2})?)\s*(?:★|⭐|звезд[а-я]*|stars?\b)|'
    r'(?:рейтинг[а-я]*|оценк[а-я]*|rated|rating)\s*(?:[—:\-–]\s*)?(\d(?:[.,]\d{1,2})?)(?:\s*(?:из|/|out of)\s*(5|10|100))?(?![\d])|'
    r'(★{3,5}|⭐{3,5})', re.I)
ORDINAL_LINE_RX = re.compile(r'^\s*(?:\d{1,2}[.)]\s|0\d\b|шаг\s+\d+\b|step\s+\d+\b|этап\s+\d+\b)', re.I)
PLACEHOLDER_RX = re.compile(r'\[PLACEHOLDER(?::\s*([^\]]*))?\]', re.I)


def parse_num(intpart, frac):
    core = re.sub(r'[ \u00a0\u202f\u2009]', '', intpart)
    if frac is not None:
        return float(core + '.' + frac)
    return float(core)


def unit_at(text, pos):
    """Единица сразу после pos: (норм. единица, конец) или (None, pos)."""
    for rx, u in UNIT_RX:
        m = rx.match(text, pos)
        if m:
            if u == 'K' and not text[pos:pos + 1].isspace():
                continue  # «10k» — тысячи, не кельвины
            return u, m.end()
    return None, pos


def next_noun(text, pos, k=2):
    """Существительное после числа или единицы (объект счёта): до k слов, без предлогов и кавычек; до первого знака
    препинания («4, переключение касанием» — объекта счёта нет)."""
    rest = re.split(r'[,.;:!?()«»"]|\s[—–-]\s', text[pos:pos + 60])[0]
    words = WORD_RX.findall(norm(rest))
    out = []
    for w in words[:k + 1]:
        if w in STOP or w.isdigit():
            if out:
                break
            continue
        out.append(w)
        if len(out) >= k:
            break
    return out


def extract_numbers(text):
    """Числа текста: [{raw, start, end, value | range, unit, noun[], cmp, kind}] без дат, телефонов, ссылок на законы,
    копирайта, времени и рейтингов (они извлекаются отдельно)."""
    s = text
    mask = [False] * len(s)

    def cover(m):
        for i in range(m.start(), m.end()):
            mask[i] = True
    for rx in (URL_RX, EMAIL_RX, PHONE_RX, LAWREF_RX, COPYRIGHT_RX, TIME_RX, DATE_DMY, DATE_ISO, RATING_RX, PLACEHOLDER_RX):
        for m in rx.finditer(s):
            cover(m)
    for m in DATE_TEXT.finditer(s):
        if m.group(1) or m.group(3):
            cover(m)
    out = []
    ms = [m for m in NUM_RX.finditer(s) if not mask[m.start()]]
    i = 0
    low = s.lower()
    while i < len(ms):
        m = ms[i]
        raw_start, end = m.start(), m.end()
        v = parse_num(m.group(1), m.group(2))
        item = {'start': raw_start, 'value': v, 'cmp': 'eq', 'unit': None, 'noun': [], 'kind': 'number'}
        pre = low[max(0, raw_start - 22):raw_start]
        for rx, c in PREFIX_CMP_RX:
            if rx.search(pre):
                item['cmp'] = c
                break
        # диапазон «2700–5000», «от 2700 до 5000», «3-5»
        rng = re.match(r'\s?(?:[-–—]|до|to)\s?', s[end:end + 5], re.I)
        if rng and i + 1 < len(ms) and ms[i + 1].start() == end + rng.end():
            m2 = ms[i + 1]
            v2 = parse_num(m2.group(1), m2.group(2))
            if v2 > v:
                item['range'] = [v, v2]
                item.pop('value')
                item['cmp'] = 'eq'
                end = m2.end()
                i += 1
        # год: «с 2014 года», «в 2026 году», «2019 г.», «Итоги 2026»
        if 'value' in item and float(v).is_integer() and 1900 <= v <= 2100:
            ym = re.match(r'\s*(?:г\.|гг\.?|год[а-я]*)(?![а-я])', low[end:end + 8])
            if ym or (re.search(r'(?:^|\s)(?:с|в|до|от|к|since|in|from|by)\s*$', pre) and not next_noun(s, end)) or (not next_noun(s, end) and not unit_at(s, end)[0]):
                item.update(kind='year', unit='year', cmp='eq')
                if ym:
                    end += ym.end()
                item['raw'] = s[raw_start:end].strip()
                item['end'] = end
                item['noun'] = []
                out.append(item)
                i += 1
                continue
        # множители
        for rx, f in MULT_RX:
            mm = rx.match(s, end)
            if mm:
                if f is None:
                    f = EN_BIG.get(mm.group(0).strip().lower(), 1)
                if 'value' in item:
                    item['value'] *= f
                else:
                    item['range'] = [x * f for x in item['range']]
                end = mm.end()
                break
        if s[end:end + 1] == '+':
            item['cmp'] = 'gte'
            end += 1
        u, end2 = unit_at(s, end)
        if u:
            item['unit'] = u
            end = end2
            if s[end:end + 1] == '+':
                item['cmp'] = 'gte'
                end += 1
        # валюта перед числом: «$1,250», «€ 20»
        if not item['unit'] and raw_start > 0 and s[raw_start - 1] in '$€₽':
            item['unit'] = {'$': 'USD', '€': 'EUR', '₽': 'RUB'}[s[raw_start - 1]]
            raw_start -= 1
        # «1,250» по-английски: тысячи через запятую
        if m.group(2) and len(m.group(2)) == 3 and ',' in s[m.start():m.end()] and 'value' in item and item['unit'] in ('USD', 'EUR', None) and re.search(r'[a-z]', low[max(0, raw_start - 30):raw_start + 30]):
            item['value'] = float(re.sub(r'[^\d]', '', s[m.start():m.end()]))
        item['noun'] = next_noun(s, end)
        item['raw'] = s[raw_start:end].strip()
        item['end'] = end
        out.append(item)
        i += 1
    return out


def extract_dates(text):
    """Даты: [{raw, date:(г,м,д|None), start, end}] — ДД.ММ.ГГГГ, ISO, «31 октября 2026», «декабрь 2026», «до 31 октября»."""
    out = []
    for m in DATE_DMY.finditer(text):
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        y = y + 2000 if y < 100 else y
        if 1 <= mo <= 12 and 1 <= d <= 31:
            out.append({'raw': m.group(0), 'date': (y, mo, d), 'start': m.start(), 'end': m.end()})
    for m in DATE_ISO.finditer(text):
        out.append({'raw': m.group(0), 'date': (int(m.group(1)), int(m.group(2)), int(m.group(3))), 'start': m.start(), 'end': m.end()})
    for m in DATE_TEXT.finditer(text):
        day, mon, year = m.group(1), m.group(2), m.group(3)
        if not (day or year):
            continue  # одно слово-месяц без числа — не дата («май» как имя, «March» в тексте)
        mkey = soft(mon).rstrip('.')
        mo = None
        for k, v in MONTHS.items():
            if mkey.startswith(k):
                mo = v
                break
        if not mo:
            continue
        out.append({'raw': m.group(0).strip(), 'date': (int(year) if year else None, mo, int(day) if day else None),
                    'start': m.start(), 'end': m.end()})
    out.sort(key=lambda x: x['start'])
    return out


PLATFORMS = {'yandex-maps': r'яндекс[ .]?карт|yandex\s+maps', '2gis': r'2\s?гис|2gis', 'google': r'google(?!\s+play)',
             'g2': r'\bg2\b', 'capterra': r'capterra', 'trustpilot': r'trustpilot', 'app-store': r'app\s?store',
             'google-play': r'google\s+play', 'otzovik': r'отзовик|otzovik', 'irecommend': r'irecommend', 'flamp': r'flamp|фламп',
             'zoon': r'\bzoon\b|зун', 'profi': r'профи\.?ру|profi\.ru', 'avito': r'авито|avito', 'ozon': r'\bozon\b|озон',
             'wildberries': r'wildberries|вайлдберриз', 'market': r'яндекс[ .]?маркет', 'prodoctorov': r'продокторов|prodoctorov'}
PLATFORM_RX = {k: re.compile(v, re.I) for k, v in PLATFORMS.items()}


def platforms_in(text):
    st = soft(text)
    return {k for k, rx in PLATFORM_RX.items() if rx.search(st)}


def extract_ratings(text):
    out = []
    for m in RATING_RX.finditer(text):
        if m.group(1):
            out.append({'raw': m.group(0), 'value': float(m.group(1).replace(',', '.')), 'scale': float(m.group(2)), 'start': m.start()})
        elif m.group(3):
            out.append({'raw': m.group(0), 'value': float(m.group(3).replace(',', '.')), 'scale': 5.0, 'start': m.start()})
        elif m.group(4):
            v = float(m.group(4).replace(',', '.'))
            sc = float(m.group(5)) if m.group(5) else (5.0 if v <= 5 else 10.0)
            if v <= 10:
                out.append({'raw': m.group(0), 'value': v, 'scale': sc, 'start': m.start()})
        elif m.group(6):
            out.append({'raw': m.group(0), 'value': float(len(m.group(6))), 'scale': 5.0, 'start': m.start(), 'stars_only': True})
    return out


QUOTE_RX = re.compile(r'«([^«»]{2,600})»|“([^“”]{2,600})”|"([^"]{2,600})"|„([^“”„]{2,600})“')


def extract_quotes(text):
    out = []
    for m in QUOTE_RX.finditer(text):
        q = next(g for g in m.groups() if g is not None)
        out.append({'raw': m.group(0), 'text': q.strip(), 'start': m.start(), 'words': len(tokens(q))})
    return out


# ================================================================ маркеры классов (RU, EN) и термины свойств
def R(*alts):
    return [re.compile(a, re.I | re.U) for a in alts]


B = r'(?<![а-яa-z0-9])'   # граница слова для кириллицы (\b в Python для кириллицы работает, но так явно)
E = r'(?![а-яa-z0-9])'
CLASS_MARKERS = {
    'superlative': R(
        B + r'лучш(?:ий|ая|ее|ие|его|ей|ему|им|их|ую|ими)' + E, B + r'№\s?1' + E, B + r'номер\s+один' + E,
        B + r'(?:перв\w*|1)[- ]?(?:е|ое|ым)?\s+мест\w*', B + r'перв(?:ый|ая|ое|ые|ой)\s+(?:в|на)\s+(?:росси\w*|мир\w*|рынк\w*|город\w*|стран\w*|регион\w*|рунет\w*)',
        B + r'лидер(?:ом|а|ы|ов)?' + E, B + r'единствен(?:ный|ная|ное|ные|ного|ной|ным)' + E,
        B + r'уникальн\w*', B + r'непревзойд\w*', B + r'беспрецедентн\w*', B + r'не\s+имеющ\w+\s+аналог\w*', B + r'без\s+аналогов',
        B + r'сам(?:ый|ая|ое|ые|ого|ой|ом|ым|ых|ую)\s+(?!част|популярн\w*\s+вопрос|главн|важн|обычн|перв|конц|начал|дел)\w{3,}(?:ый|ий|ой|ая|яя|ое|ее|ые|ие|ого|ей|ую|ым)' + E,
        r'\bbest\b(?!\s+(?:regards|wishes|practices?))', r'#\s?1\b', r'\bnumber\s+one\b', r'\bno\.\s?1\b',
        r'\bleading\b', r'\bmarket\s+leader\b', r'\bindustry[- ]leading\b', r'\bthe\s+only\b', r'\bunique\b', r"\bworld'?s\s+first\b",
        r'\bunmatched\b', r'\bunrivall?ed\b', r'\bmost\s+(?:popular|trusted|advanced|powerful|reliable|affordable|accurate|secure|loved)\b',
        r'\b(?:fastest|cheapest|easiest|safest|biggest|largest|smartest|strongest|lowest|highest)\b'),
    'comparison': R(
        B + r'(?:быстрее|дешевле|дороже|выгоднее|надежнее|надёжнее|точнее|мощнее|эффективнее|долговечнее|экономичнее|прочнее|тише|легче|лучше)\s*,?\s*(?:чем|в\s+\d|на\s+\d|аналог\w*|конкурент\w*|других|обычн\w*|традиционн\w*|у\s+(?:других|конкурент))',
        B + r'в\s+\d+(?:[.,]\d+)?\s+раз(?:а)?' + E, B + r'в\s+(?:два|три|четыре|пять|десять|несколько)\s+раз(?:а)?' + E,
        B + r'на\s+\d+(?:[.,]\d+)?\s?%\s+(?:быстрее|дешевле|больше|меньше|выше|ниже|эффективнее|дольше|точнее)',
        B + r'по\s+сравнению\s+с' + E, B + r'в\s+отличие\s+от' + E, B + r'(?:больше|меньше|выше|ниже)\s*,?\s*чем\s+(?:у|в)\s',
        r'\b(?:faster|cheaper|better|easier|safer|stronger|lighter|quieter|more\s+\w+|less\s+\w+)\s+than\b',
        r'\b\d+(?:\.\d+)?x\s+(?:faster|more|better|cheaper|higher|less)\b', r'\bcompared\s+(?:to|with)\b', r'\bunlike\s+(?:other|competitor)', r'\bvs\.?\s'),
    'guarantee': R(
        B + r'гарант(?:ия|ии|ию|ией|ируем|ирует|ируют|ированн\w*|ийн\w*)', B + r'верн[её]м\s+деньги', B + r'возврат\w*\s+(?:денег|средств|оплаты)',
        B + r'деньги\s+назад', B + r'без\s+риска' + E, B + r'или\s+верн[её]м',
        r'\bguarante\w*', r'\bmoney[- ]back\b', r'\brisk[- ]free\b', r'\bwarranty\b', r'\bor\s+your\s+money\s+back\b'),
    'health': R(
        B + r'(?:леч(?:ит|ат|ение|ебн\w*|ить)|вылеч\w*|исцел\w*|оздоров\w*|профилакти\w*|иммунитет\w*|похуд\w*|сжига\w*\s+жир|детокс\w*|омолаж\w*)',
        B + r'(?:здоров(?:ье|ья|ью|ый|ая|ое|ые|ого|ую)|самочувстви\w*|зрени(?:е|я|ю|ем)|бессонниц\w*|усталост\w*|утомлени\w*\s+глаз|утомля\w*)' + E,
        B + r'(?<!на\s)глаз(?:а|ам|ами|ах|у)?' + E, B + r'безопасн\w*\s+для\s+(?:здоровья|детей|кожи|глаз)', B + r'гипоаллерген\w*',
        B + r'(?:клинически|научно)\s+доказ\w*', B + r'врач\w*\s+рекоменд\w*', B + r'рекомендова\w*\s+врач\w*',
        r'\b(?:cures?|heals?|treat(?:s|ment)?|prevents?\s+(?:disease|illness)|immun\w+|weight\s+loss|lose\s+weight|detox|anti-?aging|eye\s*strain|eyesight|clinically\s+proven|doctor[- ]recommended|hypoallergenic|sleep\s+better)\b'),
    'income-finance': R(
        B + r'(?:доход\w*|прибыл[а-я]*|дивиденд\w*|пассивн\w*\s+доход\w*|инвестиц\w*|кредит\w*|ипотек\w*|займ\w*|кэшб[эе]к\w*|кешб[эе]к\w*)' + E,
        B + r'(?:заработ(?:ок|ка|ку|ком|ать|аете|аешь|ают|аем|али)|зарабатыва\w*)' + E, B + r'процент\w*\s+годовых', B + r'ставк\w*\s+(?:от\s+)?\d',
        B + r'зарплат\w*', B + r'(?:удвоил|утроил|увеличил|подняли?)\w*\s+(?:нашу\s+|свою\s+)?(?:выручк|продаж|прибыл|доход|оборот)\w*',
        r'\bsalar(?:y|ies)\b', r'\b(?:doubl|tripl|quadrupl)\w*\s+(?:our\s+|their\s+|my\s+)?(?:revenue|sales|income|profit)\w*',
        r'\b(?:earn(?:ings)?|income|profit\w*|roi|return\s+on\s+investment|passive\s+income|make\s+money|interest\s+rate|apr|loans?|invest(?:ment)?s?)\b'),
    'price-discount': R(
        B + r'бесплатн\w*', B + r'скидк\w*', B + r'в\s+подарок' + E, B + r'даром' + E, B + r'распродаж\w*',
        B + r'(?:-|−)\s?\d+\s?%', B + r'выгод\w*\s+(?:до\s+)?\d', B + r'пробн\w*\s+(?:период|доступ|урок|заняти)\w*',
        r'(?<!feel\s)(?<!-)\bfree\b(?!-)', r'\bdiscount\w*', r'\b\d+%\s+off\b', r'\bsave\s+(?:up\s+to\s+)?\d', r'\bfree\s+trial\b', r'\bsale\b'),
    'purchase-terms': R(
        B + r'доставк\w*', B + r'отгрузк\w*', B + r'возврат\w*', B + r'возвращ\w*', B + r'верн[её]м' + E, B + r'предоплат\w*',
        B + r'доплат\w*', B + r'рассрочк\w*', B + r'брон[ьяи]\w*' + E, B + r'брониров\w*', B + r'забронир\w*', B + r'обмен\w*' + E,
        B + r'под\s+заказ' + E, B + r'срок\w*\s+(?:выполнения|доставки|изготовления|работ|поставки)',
        r'\bshipping\b', r'\bdelivery\b', r'\brefunds?\b', r'\breturns?\s+(?:policy|within)\b', r'\bprepay\w*', r'\binstallments?\b',
        r'\bships?\s+in\b', r'\bcancel\s+any\s?time\b', r'\bpre-?order\w*'),
    'availability-scarcity': R(
        B + r'в\s+наличии' + E, B + r'остал(?:ось|ись|ась|ся)' + E, B + r'последн(?:ие|яя|ий|их)\s+(?:\d|мест\w*|штук\w*|экземпляр\w*|шанс\w*|дн\w*)',
        B + r'ограниченн\w*\s+(?:парти\w*|тираж\w*|количеств\w*|сери\w*|предложени\w*|числ\w*)', B + r'парти(?:я|и|ю|ей)' + E,
        B + r'дефицит\w*', B + r'раскупа\w*', B + r'быстро\s+разбира\w*', B + r'мест\s+(?:осталось|нет)',
        r'\bin\s+stock\b', r'\bonly\s+\d+\s+left\b', r'\blimited\s+(?:edition|stock|spots|seats|batch|quantit\w+|supply)\b',
        r'\bselling\s+fast\b', r'\bsold\s+out\b', r'\blast\s+chance\b'),
    'promo-deadline': R(
        B + r'до\s+\d{1,2}\s+(?:январ|феврал|март|апрел|ма[яй]|июн|июл|август|сентябр|октябр|ноябр|декабр)\w*',
        B + r'до\s+\d{1,2}\.\d{1,2}(?:\.\d{2,4})?', B + r'только\s+(?:сегодня|до|в\s+этом|на\s+этой|сейчас)', B + r'успей(?:те)?' + E,
        B + r'остал(?:ось|ся)\s+\d+\s+(?:дн|час|минут)', B + r'акци(?:я|и)\s+(?:действует|продлится|заканчива)', B + r'предложени\w*\s+(?:действует|ограничен)',
        B + r'таймер\w*', r'\buntil\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*', r'\bends?\s+(?:today|tonight|soon|on)\b',
        r'\blimited[- ]time\b', r'\bonly\s+today\b', r'\bhurry\b', r'\blast\s+day\b'),
    'award-press': R(
        B + r'преми(?:я|и|ю|ей)' + E, B + r'лауреат\w*', B + r'победител\w*', B + r'наград\w*', B + r'награжд\w*', B + r'диплом\w*',
        B + r'номинант\w*', B + r'при[зз]ер\w*|призёр\w*', B + r'о\s+нас\s+(?:пишут|писали|говорят|рассказ\w*)', B + r'в\s+(?:сми|прессе)' + E,
        B + r'(?:входим|вошли|вош[её]л|вошла)\s+в\s+(?:топ|рейтинг|число|список|сотню|десятку)',
        r'\baward\w*', r'\bwinner\b', r'\bas\s+seen\s+(?:in|on)\b', r'\bfeatured\s+(?:in|on)\b', r'\bnominee\b', r'\brecogni[sz]ed\s+by\b'),
    'client-logo': R(
        B + r'нам\s+доверя\w*', B + r'наши\s+(?:клиенты|партн[её]ры|заказчики)', B + r'среди\s+(?:наших\s+)?(?:клиентов|партн[её]ров|заказчиков)',
        B + r'(?:с\s+нами\s+работа\w*|нас\s+выбира\w*|выбирают\s+нас)', B + r'официальн\w*\s+(?:партн\w*|дилер\w*|дистрибьют\w*|представител\w*)',
        B + r'рекомендуют' + E, B + r'по\s+рекомендаци\w*',
        r'\btrusted\s+by\b', r'\bused\s+by\b', r'\bloved\s+by\b', r'\bour\s+(?:customers|clients|partners)\b', r'\bcustomers\s+include\b',
        r'\bofficial\s+(?:partner|reseller|dealer)\b', r'\bjoin\s+\d'),
    'testimonial-quote': R(B + r'(?:говорят|рассказыва\w*|пишут)\s+(?:наши\s+)?(?:клиент\w*|покупател\w*|ученик\w*|пациент\w*)', r'\bwhat\s+(?:our\s+)?(?:customers|clients|users)\s+say\b'),
    'rating': R(B + r'рейтинг\w*\s+(?:на|в)\s+', B + r'оценк\w*\s+(?:на|в)\s+(?:яндекс|2гис|google|app|отзовик)', r'\brated\b', r'\b(?:stars?|rating)\s+on\b'),
    'forecast': R(
        B + r'сэконом(?:ите|ишь|ят|ит)' + E, B + r'окуп(?:ится|ятся|аемост\w*|ит)' + E,
        B + r'увелич(?:ит|ите|ат|ивает)\s+(?:ваш\w*\s+)?(?:продаж\w*|выручк\w*|прибыл\w*|конверси\w*|доход\w*|трафик\w*|заявк\w*)',
        B + r'выраст(?:ет|ут|ит)' + E, B + r'принес(?:[её]т|ут)\s+(?:доход|прибыль|клиент\w*|заявк\w*)',
        B + r'(?:результат|эффект)\w*\s+через\s+\d', B + r'гарантированн\w*\s+результат\w*',
        r"\byou(?:'ll|\s+will)\s+(?:save|earn|get|grow|increase|double)\b", r'\bwill\s+(?:increase|boost|double|grow|triple)\b', r'\bpays\s+for\s+itself\b', r'\bguaranteed\s+results?\b'),
    'origin': R(
        B + r'сделан\w*\s+в' + E, B + r'произвед[её]н\w*\s+в' + E, B + r'производ\w*\s+в\s+(?:росси|казан|китае|германи|москв|итали|япони|европ)\w*',
        B + r'собственн\w*\s+производств\w*', B + r'сборк\w*', B + r'собран\w*\s+в' + E, B + r'собира(?:ем|ют|ется)\s+в' + E,
        B + r'(?:российск|отечественн|немецк|японск|итальянск|европейск)\w*\s+(?:производств|сборк|качеств)\w*', B + r'стран\w*\s+(?:производства|происхождения)',
        r'\bmade\s+in\b', r'\bmanufactured\s+in\b', r'\bassembled\s+in\b', r'\bproduced\s+in\b', r'\bdesigned\s+in\b'),
    'certification': R(
        B + r'сертифик(?:ат\w*|ован\w*|ац\w*)', B + r'декларац\w*\s+соответстви\w*', B + r'гост' + E, B + r'iso\s?\d+',
        B + r'лиценз(?:ия|ии|ией|ию|ирован\w*)' + E, B + r'аккредит\w*', B + r'сро' + E, B + r'одобрен\w*',
        B + r'рекомендован\w*\s+(?:минздрав\w*|роспотреб\w*|стоматолог\w*|педиатр\w*|специалист\w*)', B + r'соответству\w*\s+(?:требованиям|стандарт\w*|гост)',
        B + r'запатентован\w*', B + r'патент\w*',
        r'\bcertified\b', r'\bcertification\b', r'\bliscen[cs]ed\b|\blicensed\b', r'\baccredited\b', r'\bapproved\s+by\b', r'\bpatent\w*',
        r'\bcompliant\b', r'\bsoc\s?2\b', r'\bhipaa\b'),
    'eco-natural': R(
        B + r'эко(?:логичн\w*|логически\s+чист\w*|-|' + E + r')', B + r'натуральн\w*', B + r'органическ\w*', B + r'без\s+химии' + E,
        B + r'биоразлага\w*', B + r'без\s+(?:консервант|гмо|красител|парабен|сульфат|пальмов)\w*', B + r'углеродн\w*\s+нейтральн\w*',
        r'\beco-?friendly\b', r'\bnatural\b', r'\borganic\b', r'\bsustainabl\w*\b', r'\bcarbon[- ]neutral\b', r'\bbiodegradable\b',
        r'\bnon-?toxic\b', r'\bchemical-?free\b'),
    'company-details': R(
        r'\bинн\s*\d', r'\bогрн(?:ип)?\s*\d', B + r'ооо\s+["«]', B + r'ао\s+["«]', B + r'ип\s+[а-я]{3,}', B + r'юридическ\w*\s+адрес',
        B + r'(?:работаем|на\s+рынке|основан\w*|существуем)\s+(?:с|в)\s+(?:19|20)\d{2}', r'\bsince\s+(?:19|20)\d{2}\b', r'\bfounded\s+in\b'),
    'fact-number': R(
        B + r'(?:тысяч[иа]?|сотн[иям]\w*|миллион\w*|десятк\w*)\s+(?:довольн\w+\s+|счастлив\w+\s+|постоянн\w+\s+)?(?:клиент|покупател|пользовател|компани|заказ|проект|семей|учеников|студент|пациент|гостей|читател)\w*',
        B + r'(?:много|множество)\s+(?:довольн\w+\s+)?(?:клиент|покупател|пользовател)\w*',
        r'\b(?:thousands|hundreds|millions)\s+of\s+(?:happy\s+|satisfied\s+)?(?:customers|users|clients|teams|companies|businesses)\b'),
}
NEGATION_RX = re.compile(r'(?:^|[\s,(])(?:не|нет|без|ни|no|not|never|without)\s+(?:\w+\s+){0,1}$', re.I)
NEG_CLASSES = {'guarantee', 'health', 'superlative', 'income-finance', 'forecast', 'comparison'}

PROPERTY_TERMS = R(
    B + r'датчик\w*', B + r'сенсор\w*', B + r'аккумулятор\w*', B + r'батаре(?:я|и|ей|ю|йк\w*)', r'\bbluetooth\b', r'\bwi-?fi\b',
    B + r'нейросет\w*', B + r'искусственн\w*\s+интеллект\w*', B + r'алгоритм\w*', B + r'касани\w*', B + r'сенсорн\w*', B + r'пульт\w*',
    B + r'голосов\w*\s+(?:управлени|команд|помощник)\w*', B + r'жест(?:ом|ами|ы)' + E, B + r'приложени(?:е|я|и|ем)' + E,
    B + r'алюмини\w*', B + r'нержаве\w*', B + r'титан\w*', B + r'керамик\w*', B + r'закал[её]нн\w*', B + r'дубов\w*|' + B + r'массив\w*',
    B + r'натуральн\w*\s+кож\w*', B + r'хлопк\w*|' + B + r'хлопок', B + r'шерст\w*', B + r'шелк\w*|' + B + r'шёлк\w*', B + r'силикон\w*',
    B + r'латун\w*', B + r'водонепроница\w*', B + r'влагозащ\w*', B + r'пылезащ\w*', B + r'ударопрочн\w*', B + r'беспроводн\w*',
    B + r'светодиод\w*', r'\bled\b', r'\boled\b', r'\bhdr\b', B + r'процессор\w*', r'\bnfc\b', r'\bgps\b', B + r'камер(?:а|ы|ой)' + E,
    B + r'микрофон\w*', B + r'шумоподав\w*', B + r'энергосберега\w*', B + r'автоматическ\w*', B + r'самоочист\w*',
    B + r'круглосуточн\w*', r'24/7', B + r'без\s+выходных', B + r'собственн\w*\s+(?:склад|автопарк|лаборатори|цех|бригад)\w*',
    B + r'штатн\w*\s+(?:юрист|инженер|дизайнер|врач|психолог)\w*', B + r'личн\w*\s+(?:менеджер|куратор)\w*',
    r'\bsensor\w*', r'\bbattery\b', r'\baluminium\b|\baluminum\b', r'\bstainless\b', r'\bwaterproof\b', r'\bwireless\b', r'\bai-powered\b')

TECH_WORDS = {'usb', 'usb-c', 'type-c', 'led', 'hdmi', 'wi-fi', 'wifi', 'gps', 'nfc', 'ip', 'seo', 'crm', 'api', 'ai', 'ии',
              'sms', 'pdf', 'faq', 'cta', 'hr', 'it', 'b2b', 'b2c', 'saas', 'erp', 'ux', 'ui', 'ok', 'ооо', 'ип', 'ао',
              'пао', 'рф', 'сми', 'ндс', 'фз', 'гост', 'iso', 'сро', 'инн', 'огрн', 'кпп', 'бик', 'q', 'a', 'k', 'w', 'kw'}
NAME_OK = {'вы', 'вас', 'вам', 'ваш', 'ваша', 'ваше', 'ваши', 'вами', 'мы', 'я', 'monday', 'tuesday', 'wednesday',
           'thursday', 'friday', 'saturday', 'sunday', 'i', 'we', 'you', 'our', 'the', 'a',
           # частые служебные и местоименные слова, которые встают с заглавной после знаков и в подписях
           'все', 'всё', 'это', 'как', 'что', 'наш', 'наша', 'наши', 'для', 'при', 'без', 'или', 'если', 'когда', 'где',
           'почему', 'зачем', 'только', 'уже', 'еще', 'ещё', 'сейчас', 'здесь', 'там', 'да', 'нет', 'не', 'и', 'а', 'но',
           'права', 'защищены', 'политика', 'конфиденциальности', 'согласие', 'оферта', 'главная', 'контакты', 'меню'}
SOURCE_HINT_RX = re.compile(
    r'по\s+данным|источник|согласно|по\s+(?:итогам|результатам|оценке|версии|опросу)|на\s+\d{1,2}\.\d{1,2}\.\d{2,4}|'
    r'as\s+of|according\s+to|source:|data\s+from|survey|исследовани|опрос|\bg2\b|capterra|trustpilot|яндекс[ .]?карт|2гис|'
    r'отзовик|irecommend|app\s?store|google\s+play|forbes|рбк|коммерсант|ведомост|techcrunch|\(\s*(?:19|20)\d{2}\s*\)|(?<=[\d%»a-zа-я])\*(?!\*)|¹|²|³|\[\d+\]', re.I)


CONCEPTS = [  # корень понятия маркера: маркер покрыт фактом, если в тексте факта есть то же понятие (синонимы, приставки)
    ('брон', r'брон|заброн'), ('возврат', r'верн[её]м|верну|возвра[тщ]|refund'), ('доставк', r'достав|deliver|shipping'),
    ('отгруз', r'отгруз|ships?\b'), ('гарант', r'гарант|guarante|warrant'), ('парти', r'парти[яиюей]|batch'),
    ('сборк', r'сборк|собран|собира|assembl'), ('производ', r'производ|произвед|manufactur|made in'),
    ('скидк', r'скидк|discount|% off|(?<![\w])[-−]\s?\d+(?:[.,]\d+)?\s?%'), ('бесплатн', r'бесплатн|\bfree\b|0\s?₽'), ('подарок', r'подар|gift'),
    ('предоплат', r'предоплат|prepay'), ('доплат', r'доплат'), ('рассрочк', r'рассрочк|installment'), ('наличи', r'наличи|in stock'),
    ('лучш', r'лучш|best'), ('лидер', r'лидер|leader'), ('перв', r'перв|first'), ('сертиф', r'сертифи|certif'),
    ('лиценз', r'лиценз|licen[cs]'), ('наград', r'наград|премия|преми[ию]|award|лауреат|победител'),
    ('клиент', r'клиент|заказчик|customer|client'), ('отзыв', r'отзыв|review|testimonial'), ('рейтинг', r'рейтинг|rating|rated'),
    ('здоров', r'здоров|health'), ('глаз', r'глаз|зрени|eye|vision'), ('доход', r'доход|заработ|прибыл|income|earn|profit'),
    ('эконом', r'эконом|сэконом|save'), ('натурал', r'натурал|natural'), ('органик', r'органи|organic'), ('эко', r'\bэко|eco'),
]
CONCEPT_RX = [(c, re.compile(rx, re.I)) for c, rx in CONCEPTS]


def concept_of(fragment):
    st = soft(fragment)
    for c, rx in CONCEPT_RX:
        if rx.search(st):
            return c, rx
    return None, None


def covers(fact_soft, fact_stems, fragment):
    """Покрывает ли текст факта фрагмент-маркер: по понятию (синонимы, приставки) или по основам всех слов."""
    c, rx = concept_of(fragment)
    if c:
        return bool(rx.search(fact_soft))
    fr_st = {stem(w) for w in WORD_RX.findall(norm(fragment)) if w not in STOP and not w.isdigit()}
    if not fr_st:  # фрагмент из чисел и знаков («−10 %»): ищем его нормализованную форму в тексте факта
        f = re.sub(r'\s+', '', soft(fragment))
        return bool(f) and f in re.sub(r'\s+', '', fact_soft)
    return fr_st <= fact_stems or all(x in fact_soft for x in fr_st)


def find_markers(text, classes=None):
    """{class: [(fragment, start)]} с учётом отрицания («не гарантируем»)."""
    st = soft(text)
    out = {}
    for cl, rxs in CLASS_MARKERS.items():
        if classes and cl not in classes:
            continue
        for rx in rxs:
            for m in rx.finditer(st):
                if cl in NEG_CLASSES and NEGATION_RX.search(st[max(0, m.start() - 14):m.start()]):
                    continue
                out.setdefault(cl, []).append((text[m.start():m.end()] if len(text) == len(st) else m.group(0), m.start()))
    return out


def find_property_terms(text):
    st = soft(text)
    hits = []
    for rx in PROPERTY_TERMS:
        for m in rx.finditer(st):
            hits.append((m.group(0), m.start()))
    return hits


def is_question(text):
    return bool(re.search(r'\?\s*$', (text or '').strip()))


# ================================================================ имена
NAME_RX = re.compile(r'(?<![\w@./-])((?:[A-ZА-ЯЁ][a-zа-яё]+|[A-ZА-ЯЁ]{2,}[a-zа-яё]*|[A-Z][a-z]*[A-Z]\w*)(?:[ -](?:[A-ZА-ЯЁ][a-zа-яё]+|[A-ZА-ЯЁ]{2,}))*)')


def sentence_starts(text):
    starts = {0}
    for m in re.finditer(r'(?:[.!?…:]\s+|^\s*[-–—•*]\s*|\n\s*|[«"„“(]\s*|—\s+(?=[А-ЯЁA-Z])|©\s*(?:\d{4}\s*[-–—]?\s*)*|\|\s*)', text):
        starts.add(m.end())
    return starts


def extract_names(text):
    """Кандидаты в имена и названия: слова с заглавной не в начале предложения, латинские бренды в русском тексте,
    короткие строки в кавычках. Возвращает [(name, start)]."""
    out = []
    starts = sentence_starts(text)
    for m in NAME_RX.finditer(text):
        w = m.group(1)
        first = w.split()[0].split('-')[0]
        low = w.lower()
        if low in NAME_OK or low in TECH_WORDS or first.lower() in NAME_OK:
            continue
        if re.fullmatch(r'[A-ZА-ЯЁ]{1,2}', w):
            continue
        at_start = m.start() in starts or any(abs(m.start() - s) <= 1 for s in starts)
        if at_start and len(w.split()) > 1:
            rest = w.split(' ', 1)[1]
            if all(x.lower() in TECH_WORDS or x.lower() in NAME_OK for x in re.split(r'[ ]', rest)):
                continue
            w = rest
            low = w.lower()
            if low in TECH_WORDS:
                continue
        latin_in_ru = bool(re.search(r'[A-Za-z]', w)) and bool(re.search(r'[а-яё]', text, re.I))
        if at_start and not latin_in_ru and len(w.split()) == 1:
            continue
        if soft(first).rstrip('.') in MONTHS or first.lower() in {'promise', 'voice', 'what', 'who', 'the', 'screens', 'language'}:
            continue
        out.append((w, m.start()))
    for q in extract_quotes(text):
        if 1 <= q['words'] <= 3 and re.match(r'[A-ZА-ЯЁ0-9]', q['text']):
            out.append((q['text'], q['start']))
    return out


# ================================================================ загрузка входа → единицы текста
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
                     'stats': 'proof-stats', 'cases': 'case-studies', 'team': 'team', 'about': 'about',
                     'guarantee': 'guarantee', 'contacts': 'contacts', 'form': 'lead-form', 'benefits': 'benefits',
                     'features': 'benefits', 'solution': 'solution', 'cta': 'cta-band', 'final': 'final-cta',
                     'case': 'case-studies', 'stats': 'proof-stats', 'proof': 'proof-stats', 'how-it-works': 'how-it-works',
                     'hero-proof': 'hero', 'objections': 'objections', 'lead-form': 'lead-form'}
QUOTE_SLOTS = {'testimonial-quote'}
ATTRIB_SLOTS = {'testimonial-attribution', 'logos-caption', 'case-title', 'case-summary', 'case-result'}
QUESTION_SLOTS = {'faq-q'}


def kimi_slot(key):
    for rx, st in KIMI_KEY_SLOT:
        if re.match(rx, key):
            return st
    return None


def unit(uid, text, **loc):
    return {'id': uid, 'text': text, 'page': loc.get('page'), 'page_type': loc.get('page_type'),
            'section': loc.get('section'), 'section_role': loc.get('section_role'), 'slot': loc.get('slot'),
            'slot_type': loc.get('slot_type'), 'variant': loc.get('variant'), 'line': loc.get('line'),
            'fact_ids': list(loc.get('fact_ids') or []), 'claim_flags': list(loc.get('claim_flags') or []),
            'genre': loc.get('genre'), 'block': loc.get('block')}


def load_deck(data, all_variants=False):
    deck = data.get('copy_deck', data)
    units = []
    genre_default = None
    for p in deck.get('pages', []) or []:
        pid, ptype = p.get('page_id'), p.get('page_type')
        meta = p.get('meta') or {}
        for k, st in (('title', 'meta-title'), ('description', 'meta-description'), ('og_title', 'og-title'), ('og_description', 'og-description')):
            if meta.get(k):
                units.append(unit(f'{pid}/meta/{k}', str(meta[k]), page=pid, page_type=ptype, section='meta', slot=k, slot_type=st, genre='meta'))
        for s in p.get('sections', []) or []:
            sid = s.get('section_id')
            role = s.get('section_role') or s.get('role') or KIMI_SECTION_ROLE.get(str(sid), None)
            for sl in s.get('slots', []) or []:
                variants = sl.get('variants') or []
                chosen = sl.get('chosen')
                pick = variants if all_variants else [v for v in variants if v.get('id') == chosen] or variants[:1]
                for v in pick:
                    if v.get('status') == 'rejected' and not all_variants:
                        continue
                    txt = v.get('text') or ''
                    if not str(txt).strip():
                        continue
                    lint = sl.get('lint') or {}
                    units.append(unit(f"{pid}/{sid}/{sl.get('slot_id')}/{v.get('id')}", str(txt), page=pid, page_type=ptype,
                                      section=sid, section_role=role, slot=sl.get('slot_id'), slot_type=sl.get('slot_type'),
                                      variant=v.get('id'), fact_ids=sl.get('fact_ids'), claim_flags=sl.get('claim_flags'),
                                      genre=lint.get('profile') or genre_default, block=s.get('block')))
    return units, {'site': deck.get('site'), 'lang': deck.get('lang'), 'facts_ref': deck.get('facts_ref'),
                   'jurisdiction': deck.get('jurisdiction'), 'legal_category': deck.get('legal_category')}


def load_kimi_md(text):
    units, sec = [], None
    for i, line in enumerate(text.splitlines(), 1):
        st = line.strip()
        if not st or st.startswith('{#') or st.startswith('<!--'):
            continue
        m = re.match(r'^##\s+(\S+)', st)
        if m:
            sec = m.group(1)
            continue
        if st.startswith('# ') or st.lower().startswith(('voice:', 'keys in square brackets')):
            continue
        m = re.match(r'^\[([\w\-]+)\]:\s*(.*)$', st)
        if m:
            key, txt = m.group(1), m.group(2)
            units.append(unit(f'{sec}/{key}', txt, section=sec, section_role=KIMI_SECTION_ROLE.get(sec or '', sec),
                              slot=key, slot_type=kimi_slot(key), line=i))
        else:
            units.append(unit(f'L{i}', st, section=sec, section_role=KIMI_SECTION_ROLE.get(sec or '', sec), line=i))
    return units


def load_md(text):
    units, sec, in_code = [], None, False
    for i, line in enumerate(text.splitlines(), 1):
        st = line.strip()
        if st.startswith('```'):
            in_code = not in_code
            continue
        if in_code or not st or re.fullmatch(r'[-|:\s]{3,}', st) or st.startswith('<!--'):
            continue
        slot_type = None
        m = re.match(r'^(#{1,6})\s+(.*)$', st)
        if m:
            sec = m.group(2)[:60]
            slot_type = 'headline' if len(m.group(1)) == 1 else 'section-title'
            st = m.group(2)
        elif st.startswith('>'):
            st = st.lstrip('> ').strip()
            slot_type = 'testimonial-quote'
        st = re.sub(r'^\s*(?:[-*+]|\d+[.)])\s+', '', st)
        st = re.sub(r'!\[([^\]]*)\]\([^)]*\)', r'\1', st)
        st = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', st)
        st = st.replace('**', '').replace('__', '')
        if st.startswith('|'):
            cells = [c.strip() for c in st.strip('|').split('|')]
            st = ' — '.join(c for c in cells if c)
        if st:
            units.append(unit(f'L{i}', st, section=sec, slot_type=slot_type, line=i))
    return units


def load_text(text):
    units = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.strip():
            units.append(unit(f'L{i}', line.strip(), line=i))
    return units


class _HTMLUnits(html.parser.HTMLParser):
    BLOCK = {'h1': 'headline', 'h2': 'section-title', 'h3': 'card-title', 'h4': 'card-title', 'h5': 'card-title',
             'h6': 'card-title', 'p': 'body', 'li': 'list-item', 'blockquote': 'testimonial-quote', 'q': 'testimonial-quote',
             'figcaption': 'body', 'button': 'cta-label', 'td': 'spec-row', 'th': 'spec-row', 'dt': 'faq-q',
             'dd': 'faq-a', 'label': 'body', 'summary': 'faq-q', 'caption': 'body', 'cite': 'testimonial-attribution',
             'title': 'meta-title', 'div': None, 'section': None, 'article': None, 'span': None, 'a': None, 'small': None}
    SKIP = {'script', 'style', 'noscript', 'svg', 'template', 'iframe', 'canvas'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.units, self.stack, self.buf, self.skip, self.section = [], [], [], 0, None
        self.n = 0

    def flush(self, tag=None):
        txt = re.sub(r'\s+', ' ', ''.join(self.buf)).strip()
        self.buf = []
        if txt:
            st = self.BLOCK.get(tag) if tag else None
            self.n += 1
            if tag in ('h1', 'h2'):
                self.section = txt[:60]
            self.units.append(unit(f'H{self.n}', txt, section=self.section, slot_type=st, line=self.getpos()[0]))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
            return
        if tag == 'meta':
            name = (a.get('name') or a.get('property') or '').lower()
            st = {'description': 'meta-description', 'og:title': 'og-title', 'og:description': 'og-description'}.get(name)
            if st and a.get('content'):
                self.n += 1
                self.units.append(unit(f'H{self.n}', a['content'].strip(), section='meta', slot_type=st, genre='meta'))
            return
        if tag == 'img' and a.get('alt'):
            self.n += 1
            self.units.append(unit(f'H{self.n}', a['alt'].strip(), section=self.section, slot_type='image-alt'))
            return
        if tag in self.BLOCK and self.BLOCK[tag]:
            self.flush(self.stack[-1] if self.stack else None)
            self.stack.append(tag)
        elif tag == 'br':
            self.buf.append(' ')

    def handle_endtag(self, tag):
        if tag in self.SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if tag in self.BLOCK and self.BLOCK[tag]:
            self.flush(tag)
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)

    def close(self):
        super().close()
        self.flush(self.stack[-1] if self.stack else None)


def load_html(text):
    p = _HTMLUnits()
    p.feed(text)
    p.close()
    seen, out = set(), []
    for u in p.units:
        k = (u['text'], u['slot_type'])
        if k in seen and len(u['text']) < 40:
            continue
        seen.add(k)
        out.append(u)
    return out


def detect_format(path, text):
    low = path.lower()
    if low.endswith(('.yaml', '.yml', '.json')):
        return 'deck'
    if low.endswith(('.html', '.htm')) or re.match(r'\s*<(?:!doctype|html)', text, re.I):
        return 'html'
    if re.search(r'^\[[\w\-]+\]:\s', text, re.M) and re.search(r'^##\s+\S+', text, re.M):
        return 'kimi-md'
    if low.endswith('.md') or re.search(r'^#{1,6}\s', text, re.M):
        return 'md'
    return 'text'


def load_input(path, fmt='auto', all_variants=False):
    with open(path, encoding='utf-8') as f:
        text = f.read()
    fmt = detect_format(path, text) if fmt == 'auto' else fmt
    meta = {}
    if fmt == 'deck':
        if yaml is None:
            raise SystemExit('нужен PyYAML: python3 -m pip … или 99-raw/tools/venv-B2/bin/python')
        data = deep_dates(yaml.safe_load(text) if not path.lower().endswith('.json') else json.loads(text))
        units, meta = load_deck(data, all_variants)
    elif fmt == 'kimi-md':
        units = load_kimi_md(text)
    elif fmt == 'md':
        units = load_md(text)
    elif fmt == 'html':
        units = load_html(text)
    else:
        units = load_text(text)
    return units, fmt, meta


# ================================================================ факты
def fact_texts(f):
    parts = list(f.get('verbatim') or []) + [f.get('canonical') or '']
    for v in f.get('values') or []:
        parts += [str(v.get('what') or ''), str(v.get('qualifier') or '')]
    for lang, tr in (f.get('translations') or {}).items():
        parts += list(tr.get('verbatim') or []) + [tr.get('canonical') or '']
    return [p for p in parts if p]


def fact_values(f):
    """Числа факта: из values[] и из чисел verbatim/canonical (с единицей и объектом счёта)."""
    out = []
    for v in f.get('values') or []:
        unit_ = UNIT_SYNONYMS.get(str(v.get('unit') or '').lower(), v.get('unit'))
        d = {'unit': unit_, 'what': stems(v.get('what') or '') | stems(v.get('qualifier') or ''), 'cmp': v.get('comparator', 'eq'),
             'approx': bool(v.get('approx')), 'src': 'values'}
        if 'value' in v and v['value'] is not None:
            out.append(dict(d, value=float(v['value']), scale=v.get('scale'), count=v.get('count')))
        if v.get('range'):
            out.append(dict(d, range=[float(x) for x in v['range']]))
        if v.get('date'):
            out.append(dict(d, date=parse_iso(v['date'])))
        if unit_ in ('year',) and 'value' in v:
            out.append(dict(d, date=(int(v['value']), None, None)))
    for t in fact_texts(f):
        for n in extract_numbers(t):
            d = {'unit': n['unit'], 'what': {stem(w) for w in n['noun']}, 'cmp': n['cmp'], 'approx': n['cmp'] == 'approx', 'src': 'text'}
            if 'range' in n:
                out.append(dict(d, range=n['range']))
            else:
                out.append(dict(d, value=n['value']))
                if n['kind'] == 'year':
                    out.append(dict(d, date=(int(n['value']), None, None)))
        for dd in extract_dates(t):
            out.append({'date': dd['date'], 'unit': None, 'what': set(), 'cmp': 'eq', 'approx': False, 'src': 'text'})
        for r in extract_ratings(t):
            out.append({'value': r['value'], 'scale': r['scale'], 'unit': 'stars', 'what': set(), 'cmp': 'eq', 'approx': False, 'src': 'text', 'rating': True})
    return out


class Facts:
    def __init__(self, data=None, schema=None, use_defaults=True, path=None):
        data = deep_dates(data or {})
        self.path = path
        self.data = data
        self.facts = [f for f in data.get('facts') or [] if isinstance(f, dict) and f.get('id')]
        self.by_id = {}
        for f in self.facts:
            self.by_id[str(f['id'])] = f
            for a in f.get('aliases') or []:
                self.by_id.setdefault(str(a), f)
        self.missing = data.get('missing') or []
        self.missing_ids = {str(m.get('id')) for m in self.missing} | {str(a) for m in self.missing for a in m.get('aliases') or []}
        self.placeholders = {norm(m.get('placeholder') or '') for m in self.missing}
        self.entities = data.get('entities') or []
        self.values = {f['id']: fact_values(f) for f in self.facts}
        self.stems = {f['id']: set().union(*[stems(t) for t in fact_texts(f)]) if fact_texts(f) else set() for f in self.facts}
        self.softtext = {f['id']: soft(' '.join(fact_texts(f))) for f in self.facts}
        self.names = {}  # норм. имя → (entity|None, fact id|None)
        for e in self.entities:
            for n in e.get('names') or []:
                self.names[norm(n).strip('"')] = (e, e.get('fact_id'))
        for f in self.facts:
            att = f.get('attribution') or {}
            for n in (att.get('name'), att.get('company')):
                if n:
                    self.names[norm(n)] = (None, f['id'])
        self.name_stems = {}
        for n, v in self.names.items():
            for w in WORD_RX.findall(n):
                self.name_stems.setdefault(stem(w), v)
        self.all_stems = set().union(*self.stems.values()) if self.stems else set()
        self.never = []
        for r in data.get('never_claim') or []:
            self.never.append(dict(r, origin='project'))
        self.class_info = {}
        if schema:
            self.class_info = {c['id']: c for c in schema.get('x-claim-classes') or []}
            if use_defaults and data.get('never_claim_defaults', 'ru-default-1') != 'none':
                for r in schema.get('x-never-claim-defaults') or []:
                    self.never.append(dict(r, origin='default'))

    def text_has_stem(self, fid, st):
        return st in self.stems.get(fid, set())


def load_facts(path, schema, use_defaults=True):
    if not path:
        return Facts({}, schema, use_defaults)
    if yaml is None:
        raise SystemExit('нужен PyYAML')
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict) or 'facts' not in data:
        raise SystemExit(f'{path}: не facts.yaml (нет ключа facts); facts.md kimi — сначала `claims_check.py import-kimi`')
    return Facts(data, schema, use_defaults, path=path)


def load_schema(path=SCHEMA_PATH):
    if yaml is None or not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return deep_dates(yaml.safe_load(f) or {})


# ================================================================ внешние правила (H): правовой модуль
# Волна 2, агент H, 2026-09-24. Правила — 08-russian-legal-typography/claims-rules.yaml (подхватывается сам) и --rules.
# Файл правил общий с copy_lint.py (C): у правила есть `pattern` в синтаксисе C (макросы %B% %E% %W%), `unless`,
# `examples: {bad, good}` строками, поля C (group, count_as_marker, priority…) claims_check не читает; поля права
# (claim_class, requires, jurisdiction, legal_category, law) не читает copy_lint. Это не юридическое заключение.
LEGAL_MODULE_VERSION = '2.0 (H, 2026-09-24)'
JURISDICTIONS = ('ru', 'eu', 'us', 'other')
LEGAL_CATEGORIES = ('finance', 'medical', 'dietary-supplements', 'alcohol', 'education', 'real-estate', 'other', 'general')
_MACROS = (('%B%', r'(?<![A-Za-zА-Яа-яЁё0-9_])'), ('%E%', r'(?![A-Za-zА-Яа-яЁё0-9_])'), ('%W%', r'[A-Za-zА-Яа-яЁё0-9_]*'))


def expand_macros(p):
    """Макросы границ слова copy_lint (C, спецификация §2.2) → Python re."""
    for k, v in _MACROS:
        p = p.replace(k, v)
    return p


_STR = {'type': 'string'}
_STRS = {'type': 'array', 'items': {'type': 'string'}}
RULES_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': 'urn:app-design:text-research:claims-rules:1',
    'title': 'claims-rules.yaml — правовые правила формулировок для claims_check.py (H, волна 2); файл читает и copy_lint.py (C)',
    'type': 'object', 'required': ['version', 'date', 'rules'], 'additionalProperties': True,
    'properties': {
        'version': {'const': 1}, 'date': {'type': 'string'}, 'jurisdiction': {'type': 'string'},
        'defaults': {'type': 'object', 'description': 'сливаются в каждое правило файла (как в copy_lint); поля правила сильнее'},
        'overrides': {'type': 'array', 'description': 'поправки уровней для copy_lint (C, спецификация §2.4); claims_check их не читает'},
        'rules': {'type': 'array', 'items': {
            'type': 'object', 'required': ['id', 'level', 'message'], 'additionalProperties': False,
            'properties': {
                'id': {'type': 'string', 'pattern': '^[A-Z][A-Z0-9-]+$', 'description': 'рекомендуется COPY-L-…'},
                'title': _STR, 'level': {'enum': ['error', 'warning', 'info']},
                'claim_class': {'type': 'array', 'items': {'type': 'string'}, 'description': 'классы x-claim-classes: маркер класса (trigger class|any) и отбор фактов для requires'},
                'patterns': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Python re, регистр не важен; ищутся в soft-тексте (ё→е, тире→«-», NBSP→пробел)'},
                'pattern': {'type': 'string', 'description': 'H: одна регулярка в синтаксисе copy_lint (макросы %B% %E% %W%) — её читают обе утилиты'},
                'unless': {'type': 'string', 'description': 'H: исключение — найдено в том же предложении, что и срабатывание, — правило молчит (как в copy_lint)'},
                'trigger': {'enum': ['pattern', 'class', 'any'], 'description': 'H: pattern — только регулярки; class — только маркеры claim_class; any (по умолчанию B2) — регулярки, затем маркеры'},
                'lang': {'enum': ['ru', 'en', 'any'], 'description': 'H: язык единицы (кириллица против латиницы)'},
                'genres': {'type': 'array', 'items': {'type': 'string'}}, 'slot_types': {'type': 'array', 'items': {'type': 'string'}},
                'exclude_slot_types': _STRS,
                'jurisdiction': {'type': 'array', 'items': {'enum': list(JURISDICTIONS)}, 'description': 'H: правило действует, если активная юрисдикция в списке (--jurisdiction, facts.yaml jurisdiction; по умолчанию ru)'},
                'legal_category': {'type': 'array', 'items': {'enum': list(LEGAL_CATEGORIES)}, 'description': 'H: только для отраслей (meaning.legal_category; --legal-category)'},
                'legal_category_except': {'type': 'array', 'items': {'enum': list(LEGAL_CATEGORIES)}, 'description': 'H: кроме отраслей'},
                'forbid': {'type': 'boolean', 'description': 'true — любое срабатывание = находка (запрещённая формулировка)'},
                'once': {'enum': ['unit', 'page'], 'description': 'H: page — одна находка правила на страницу (обязательные оговорки)'},
                'requires': {'type': 'object', 'additionalProperties': False, 'properties': {
                    'fact': {'type': 'boolean', 'description': 'нужен публикуемый факт с классом правила'},
                    'fact_fields': {'type': 'array', 'items': {'type': 'string'}, 'description': 'поля, которые обязаны быть у найденного факта: basis.criterion, legal.disclaimer… (H: проверяются, только если факт найден; «нет факта» — при fact: true)'},
                    'nearby': {'type': 'array', 'items': {'type': 'string'}, 'description': 'регулярки, из которых хотя бы одна должна найтись рядом (оговорка, условие, источник)'},
                    'nearby_all': {'type': 'array', 'items': {'type': 'string'}, 'description': 'H: регулярки, которые все должны найтись рядом (обязательные тексты оговорок)'},
                    'nearby_scope': {'enum': ['unit', 'section', 'page'], 'description': 'H: где искать nearby: единица, секция (по умолчанию), страница'},
                    'fact_conditions': {'type': 'boolean', 'description': 'H: условия найденного факта (values[].qualifier, legal.disclaimer) обязаны стоять рядом; нет факта — проверяется nearby'},
                    'legal_review': {'enum': ['approved']}}},
                'message': {'type': 'string'}, 'fix': {'type': 'string'}, 'replacement': {'type': 'string', 'description': 'как править (формат C); claims_check берёт его, если нет fix'},
                'source': {'type': 'string'},
                'law': {'type': 'array', 'items': {'type': 'object', 'required': ['ref'], 'additionalProperties': False, 'properties': {
                    'ref': {'type': 'string', 'description': 'норма: «38-ФЗ ст. 5 ч. 3 п. 1», «Пленум ВАС № 58 п. 29», «ФАС, приказ № 1079/23, прил. 2 разд. II»'},
                    'edition': {'type': 'string', 'description': 'редакция: «ред. от 04.08.2026»'},
                    'checked': {'type': 'string', 'description': 'дата сверки с первоисточником ГГГГ-ММ-ДД'},
                    'in_force': {'type': 'string', 'description': 'дата вступления, если норма новая или не вступила'},
                    'url': {'type': 'string'}, 'note': {'type': 'string'}}}},
                'date': _STR, 'evidence': _STR, 'note': _STR,
                'examples': {'type': 'object', 'description': 'bad / good — строки (их проверяют selftest обеих утилит); bad_en, good_en; контекст теста: slot_type, legal_category, jurisdiction, genre'},
                # поля формата copy_lint (C, 06-anti-slop/02-linter-spec-and-profiles.md §2.1): claims_check их не читает
                'group': _STR, 'marker_id': _STR, 'count_as_marker': {'type': 'boolean'}, 'flags': _STR,
                'priority': {'type': 'integer'}, 'levels': {'type': 'object'}, 'slot_levels': {'type': 'object'},
                'requires_no_fact': {'type': 'boolean'}, 'min_count': {'type': 'integer'}, 'scope': _STR,
                'mask_quotes': {'type': 'boolean'}, 'appliesTo': _STRS, 'excludes': _STRS, 'kind': _STR,
                'words': _STRS, 'threshold_ref': _STR}}}}}


def _as_list(x):
    if x is None:
        return None
    return [x] if isinstance(x, str) else list(x)


def load_rules(paths):
    """Правила из файлов YAML → [rule] с откомпилированными регулярками; ошибки — списком строк (утилита не падает)."""
    rules, errs = [], []
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        try:
            with open(p, encoding='utf-8') as f:
                data = deep_dates(yaml.safe_load(f) or {})
        except Exception as e:  # noqa
            errs.append(f'{p}: {e}')
            continue
        defaults = data.get('defaults') or {}
        for raw in data.get('rules') or []:
            if not isinstance(raw, dict):
                errs.append(f'{p}: правило не словарь: {str(raw)[:80]}')
                continue
            r = copy.deepcopy(defaults)
            r.update(raw)
            if not r.get('id') or r.get('level') not in LEVELS:
                errs.append(f'{p}: правило без id или level: {str(raw)[:80]}')
                continue
            if r.get('kind') in ('manual', 'analyzer'):
                continue  # ручные проверки и анализаторы copy_lint — не для сверки
            try:
                pats = list(r.get('patterns') or [])
                if r.get('pattern'):
                    pats.insert(0, r['pattern'])
                req = r.get('requires') or {}
                r['_rx'] = [re.compile(expand_macros(x), re.I | re.U) for x in pats]
                r['_near'] = [re.compile(expand_macros(x), re.I | re.U) for x in req.get('nearby') or []]
                r['_near_all'] = [re.compile(expand_macros(x), re.I | re.U) for x in req.get('nearby_all') or []]
                r['_unless'] = re.compile(expand_macros(r['unless']), re.I | re.U) if r.get('unless') else None
            except re.error as e:
                errs.append(f"{p}: {r['id']}: регулярка: {e}")
                continue
            for k in ('jurisdiction', 'legal_category', 'legal_category_except', 'genres', 'slot_types', 'exclude_slot_types'):
                if r.get(k) is not None:
                    r[k] = _as_list(r[k])
            r['_file'] = p
            rules.append(r)
    return rules, errs


def unit_lang(text):
    """ru | en | None (нет букв) — по числу кириллических и латинских букв, как detect_lang в copy_lint."""
    c = len(re.findall(r'[А-Яа-яЁё]', text or ''))
    l_ = len(re.findall(r'[A-Za-z]', text or ''))
    if not c and not l_:
        return None
    return 'ru' if c >= l_ else 'en'


def legal_ctx(jurisdiction=None, categories=None):
    """Контекст правового модуля: активная юрисдикция и отрасли (meaning.legal_category)."""
    cats = {c.strip() for c in (categories or []) if c and c.strip()} or {'general'}
    return {'jurisdiction': (jurisdiction or 'ru').strip().lower(), 'categories': cats, '_once': set(), '_zones': {}}


def legal_rule_applies(r, u, genre, ctx):
    g = u.get('genre') or genre
    if r.get('genres') and g and g not in r['genres']:
        return False
    st = u.get('slot_type')
    if r.get('slot_types') and not (st and any(fnmatch.fnmatch(st, s) for s in r['slot_types'])):
        return False
    if r.get('exclude_slot_types') and st and any(fnmatch.fnmatch(st, s) for s in r['exclude_slot_types']):
        return False
    if r.get('jurisdiction') and ctx['jurisdiction'] not in r['jurisdiction']:
        return False
    if r.get('legal_category') and not (ctx['categories'] & set(r['legal_category'])):
        return False
    if r.get('legal_category_except') and (ctx['categories'] & set(r['legal_category_except'])):
        return False
    lang = r.get('lang') or 'any'
    if lang in ('ru', 'en'):
        ul = unit_lang(u.get('text'))
        if ul and ul != lang:
            return False
    return True


def _sentence_of(sb, pos):
    return next(((a, b) for a, b in sentence_spans(sb) if a <= pos < b), (0, len(sb)))


def legal_hit(r, body, markers):
    """Срабатывание правила в единице: (фрагмент, позиция) или (None, None). Регулярки — по soft-тексту; `unless` —
    в том же предложении снимает срабатывание (как в copy_lint)."""
    sb = soft(body)
    trig = r.get('trigger') or 'any'
    if trig in ('pattern', 'any'):
        for rx in r['_rx']:
            for m in rx.finditer(sb):
                if m.end() == m.start():
                    continue
                if r['_unless'] is not None:
                    a, b = _sentence_of(sb, m.start())
                    if r['_unless'].search(sb[a:b]):
                        continue
                frag = body[m.start():m.end()] if len(body) == len(sb) else m.group(0)
                return frag, m.start()
    if trig in ('class', 'any'):
        for cl in r.get('claim_class') or []:
            for frag, pos in markers.get(cl, []):
                if r['_unless'] is not None:
                    a, b = _sentence_of(sb, pos)
                    if r['_unless'].search(sb[a:b]):
                        continue
                return frag, pos
    return None, None


def legal_zone(u, units, scope, ctx):
    """soft-текст зоны «рядом»: единица, секция (page + section, как у B2) или страница."""
    if scope == 'unit':
        return soft(u['text'])
    key = (scope, u.get('page'), u.get('section') if scope == 'section' else None)
    z = ctx['_zones'].get(key)
    if z is None:
        if scope == 'page':
            z = soft(' '.join(x['text'] for x in units if x.get('page') == u.get('page')))
        else:
            z = soft(' '.join(x['text'] for x in units if x.get('section') == u.get('section') and x.get('page') == u.get('page')))
        ctx['_zones'][key] = z
    return z


def fact_conditions(sup):
    """Условия фактов, которые обязаны стоять рядом с утверждением: values[].qualifier и legal.disclaimer."""
    out = []
    for f in sup:
        for v in f.get('values') or []:
            q = str(v.get('qualifier') or '').strip()
            if q and q not in out:
                out.append(q)
        d = str(((f.get('legal') or {}).get('disclaimer')) or '').strip()
        if d and d not in out:
            out.append(d)
    return out


def condition_nearby(cond, zone):
    c = soft(cond)
    if c and c in zone:
        return True
    st = {stem(w) for w in WORD_RX.findall(norm(cond)) if w not in STOP and len(w) > 2}
    if not st:
        return True
    zs = {stem(w) for w in WORD_RX.findall(norm(zone))}
    return len(st & zs) >= max(1, (len(st) + 1) // 2)


def legal_requirements(r, u, units, facts, strong, related, ctx):
    """Что не выполнено для сработавшего правила: [причина]. Факты — найденные в единице (strong ∪ related, B2)."""
    req = r.get('requires') or {}
    fail = []
    if r.get('forbid'):
        fail.append('запрещённая формулировка')
    classes = set(r.get('claim_class') or [])
    sup = []
    for fid in dict.fromkeys(list(strong) + list(related)):
        f = facts.by_id.get(fid)
        if f and (not classes or classes & set(f.get('claim_class') or [])) and f not in sup:
            sup.append(f)
    if req.get('fact') and not sup:
        fail.append('нет факта класса правила')
    if req.get('fact_fields') and sup and not any(all(get_path(f, fld) for fld in req['fact_fields']) for f in sup):
        miss = sorted({fld for f in sup for fld in req['fact_fields'] if not get_path(f, fld)})
        fail.append('у факта нет ' + ', '.join(miss))
    if req.get('legal_review') and sup and not any(((f.get('legal') or {}).get('review') or {}).get('status') == 'approved' for f in sup):
        fail.append('нет проверки юриста')
    zone = None
    if r['_near'] or r['_near_all'] or req.get('fact_conditions'):
        zone = legal_zone(u, units, req.get('nearby_scope') or 'section', ctx)
    decided = False
    if req.get('fact_conditions') and sup:
        decided = True
        miss = [c for c in fact_conditions(sup) if not condition_nearby(c, zone)]
        if miss:
            fail.append('условие из facts.yaml не указано рядом: ' + '; '.join(f'«{c[:60]}»' for c in miss[:2]))
    if r['_near'] and not decided and not any(rx.search(zone) for rx in r['_near']):
        fail.append('рядом нет условия, оговорки или источника')
    if r['_near_all']:
        miss = [rx for rx in r['_near_all'] if not rx.search(zone)]
        if miss:
            fail.append(f'рядом нет обязательной оговорки ({len(miss)} из {len(r["_near_all"])})')
    if not fail and not r.get('forbid') and not req:
        fail.append('сигнал: проверить формулировку')   # правило без условий снятия: срабатывание и есть находка
    return fail


def law_refs(r):
    out = []
    for x in r.get('law') or []:
        if isinstance(x, dict) and x.get('ref'):
            out.append(x['ref'] + (f" ({x['edition']})" if x.get('edition') else ''))
        elif isinstance(x, str):
            out.append(x)
    return out


def apply_legal_rules(F, u, body, markers, strong, related, facts, units, rules, genre, ctx):
    """Правовой модуль H: правила claims-rules.yaml (и --rules) для одной единицы текста."""
    for r in rules:
        if not legal_rule_applies(r, u, genre, ctx):
            continue
        hit, _pos = legal_hit(r, body, markers)
        if not hit:
            continue
        fail = legal_requirements(r, u, units, facts, strong, related, ctx)
        if not fail:
            continue
        if r.get('once') == 'page':
            key = (r['id'], u.get('page'))
            if key in ctx['_once']:
                continue
            ctx['_once'].add(key)
        refs = law_refs(r)
        msg = f"{r['message']} ({'; '.join(fail)})" + (f" [{refs[0].split(' (')[0]}]" if refs else '')
        add(F, r['level'], r['id'], u, hit, ','.join(r.get('claim_class') or []) or None, msg,
            r.get('fix') or r.get('replacement') or '',
            extra={'rule_source': r.get('source', ''), 'law': refs,
                   'rule_file': os.path.relpath(r['_file'], ROOT) if r.get('_file') else ''})


# ================================================================ сопоставление
def unit_ok(tu, fu, tnoun=None):
    """Совместимы ли единицы текста и факта. Число без единицы совместимо только с «штучной» единицей факта или
    если у числа в тексте нет объекта счёта («5000» против «5000 K» — да; «1 200 квартир» против «2020 года» — нет)."""
    if tu == fu:
        return True
    if tu is None:
        return fu in COUNT_UNITS or not tnoun
    if fu is None:
        return tu in COUNT_UNITS
    return {tu, fu} <= {'pcs', 'people'}


def noun_ok(tn, fw):
    if not tn or not fw:
        return None  # нечего сравнивать
    return bool(set(tn) & set(fw))


def num_supported(n, fv):
    """Поддерживает ли значение факта fv число текста n. → (ok: bool|None, why)."""
    tcmp = n.get('cmp', 'eq')
    if 'range' in n:
        if 'range' in fv:
            a, b = n['range']
            c, d = fv['range']
            if abs(a - c) < 1e-9 and abs(b - d) < 1e-9:
                return True, 'диапазон совпал'
            if a >= c and b <= d:
                return True, 'диапазон внутри факта'
            return False, f'диапазон {a:g}–{b:g} шире или не совпадает с {c:g}–{d:g}'
        if 'value' in fv:
            return None, ''
        return None, ''
    if 'value' not in n:
        return None, ''
    v = n['value']
    if 'range' in fv:
        c, d = fv['range']
        if tcmp in ('eq', 'approx') and c <= v <= d:
            return True, 'в диапазоне факта'
        if tcmp in ('lte', 'lt') and abs(v - d) < 1e-9:
            return True, 'верхняя граница'
        if tcmp in ('gte', 'gt') and abs(v - c) < 1e-9:
            return True, 'нижняя граница'
        return False, f'{v:g} вне {c:g}–{d:g}'
    if 'value' not in fv:
        return None, ''
    f = fv['value']
    fcmp = fv.get('cmp', 'eq')
    money = n.get('unit') in MONEY or fv.get('unit') in MONEY
    if abs(v - f) < 1e-9:
        if tcmp == 'eq' and fv.get('approx') and not money:
            return False, f'в факте {f:g} — приблизительное значение, в тексте точное: нужен знак «около» или «более»'
        if tcmp in ('eq', 'approx') and fcmp in ('gte', 'gt') and not money:
            return False, f'в факте «{f:g}+» (не меньше), в тексте точное {v:g}'
        if tcmp in ('gt',) and fcmp == 'eq':
            return False, f'«более {v:g}» при факте ровно {f:g}'
        return True, 'совпало'
    if money:
        return False, f'сумма {v:g} ≠ {f:g}'
    if tcmp in ('gte', 'gt') and fcmp in ('eq', 'gte', 'gt') and (f > v or (tcmp == 'gte' and f >= v)) and not fv.get('approx') and fcmp == 'eq':
        return True, f'«от/более {v:g}» при факте {f:g}'
    if tcmp in ('gte', 'gt') and fcmp in ('gte', 'gt') and f >= v:
        return True, f'«{v:g}+» не больше факта «{f:g}+»'
    if tcmp in ('lte', 'lt') and fcmp in ('eq', 'lte', 'lt') and f <= v:
        return True, f'«до {v:g}» при факте {f:g}'
    if tcmp == 'approx' and f and abs(v - f) / abs(f) <= 0.05 and fcmp == 'eq':
        return True, f'«около {v:g}» при факте {f:g}'
    return False, f'{v:g} ≠ {f:g}'


def date_supported(t, fdate):
    if not fdate:
        return False
    ty, tm, td = t
    fy, fm, fd = fdate
    if ty and fy and ty != fy:
        return False
    if tm and fm and tm != fm:
        return False
    if td and fd and td != fd:
        return False
    if tm and not fm and fy and ty == fy and not td:
        return False
    return (ty is None or fy is not None) and (tm is None or fm is not None)


class Finding(dict):
    pass


def add(F, level, rule, u, fragment, cls, msg, fix, fact_ids=None, extra=None):
    F.append(Finding(level=level, rule=rule, unit=u['id'], location={k: u.get(k) for k in ('page', 'section', 'section_role', 'slot', 'slot_type', 'variant', 'line') if u.get(k) not in (None, '')},
                     text=u['text'][:240], fragment=fragment, claim_class=cls, message=msg, fix=fix, fact_ids=fact_ids or [], **(extra or {})))


def publishable_issues(f, facts, today, cls_hint=None):
    """Проблемы самого факта при использовании: [(level, rule, msg, fix)]."""
    out = []
    perm = f.get('permission') or {}
    ps = perm.get('status', 'unknown')
    if ps not in ('granted', 'not-required'):
        out.append(('error', 'COPY-F-PERMISSION', f"fact:{f['id']}: разрешение {ps}", 'Получите письменное разрешение (proof-intake.md §разрешения) или уберите утверждение; до ответа — [PLACEHOLDER].'))
    if perm.get('withdrawn'):
        out.append(('error', 'COPY-F-PERMISSION', f"fact:{f['id']}: разрешение отозвано {perm['withdrawn']}", 'Снимите факт со всех страниц.'))
    shows = set(perm.get('shows') or [])
    if ps == 'granted' and (shows & {'full-name', 'photo'}) and not perm.get('pd_consent'):
        out.append(('error', 'COPY-F-PERMISSION', f"fact:{f['id']}: показывается имя или фото без согласия на распространение ПДн", 'Нужно согласие по 152-ФЗ ст. 10.1 (форма — H) или подпись инициалами без фото.'))
    if perm.get('until'):
        pu = parse_iso(perm['until'])
        if pu and date_end(pu) < today:
            out.append(('error', 'COPY-F-PERMISSION', f"fact:{f['id']}: срок разрешения истёк {perm['until']}", 'Продлите разрешение или снимите факт.'))
    ver = (f.get('verification') or {}).get('status', 'unverified')
    classes = set(f.get('claim_class') or [])
    info = facts.class_info
    needs_doc = any(info.get(c, {}).get('needs_document') for c in classes)
    if ver == 'unverified':
        out.append(('error', 'COPY-F-UNVERIFIED', f"fact:{f['id']}: не проверен", 'Сверьте с документом или страницей источника (verification.status: verified) либо уберите утверждение.'))
    elif ver == 'stated' and needs_doc:
        lvl = 'error' if any(info.get(c, {}).get('legal') == 'required' for c in classes) else 'warning'
        out.append((lvl, 'COPY-F-UNVERIFIED', f"fact:{f['id']}: класс {', '.join(sorted(classes))} требует документа, а факт со слов", 'Запросите документ-основание (proof-intake.md) и отметьте verification.status: verified.'))
    src = f.get('source') or {}
    if src.get('derivation') == 'inferred':
        out.append(('error', 'COPY-F-INFERRED', f"fact:{f['id']}: выведен, а не сказан источником", 'Задайте вопрос заказчику (missing) и не публикуйте вывод.'))
    gap = evidence_gap(f)
    if gap:
        out.append(('error', 'COPY-F-INFERRED', f"fact:{f['id']}: слова факта «{', '.join(gap)}» не подтверждены выдержкой источника «{src.get('quote', '')[:80]}»", 'Факт шире основания: уточните у заказчика и исправьте verbatim или source.quote.'))
    val = f.get('valid') or {}
    if val.get('until'):
        vu = parse_iso(val['until'])
        if vu and date_end(vu) < today:
            out.append(('error', 'COPY-F-EXPIRED', f"fact:{f['id']}: срок действия истёк {val['until']}", 'Обновите факт у заказчика или уберите утверждение.'))
    if val.get('review_by'):
        rb = parse_iso(val['review_by'])
        if rb and date_end(rb) < today:
            out.append(('warning', 'COPY-F-STALE', f"fact:{f['id']}: пора пересмотреть (review_by {val['review_by']})", 'Подтвердите актуальность у заказчика и сдвиньте review_by.'))
    legal_req = [c for c in classes if info.get(c, {}).get('legal') == 'required']
    rv = ((f.get('legal') or {}).get('review') or {}).get('status')
    if legal_req and rv not in ('approved', 'not-needed'):
        out.append(('error', 'COPY-F-LEGAL', f"fact:{f['id']}: класс {', '.join(legal_req)} без проверки юриста (legal.review: {rv or 'нет'})", 'Нужна проверка H или юриста заказчика (legal.review.status: approved).'))
    return out


RISKY_FOR_EVIDENCE = ['origin', 'superlative', 'comparison', 'health', 'income-finance', 'certification', 'eco-natural',
                      'guarantee', 'availability-scarcity', 'award-press', 'client-logo', 'forecast']


def evidence_gap(f):
    """Маркеры рискованных классов и числа в verbatim, которых нет в source.quote → список (вывод шире основания)."""
    q = (f.get('source') or {}).get('quote')
    if not q:
        return []
    gap = []
    qs = soft(q)
    q_stems = {stem(w) for w in WORD_RX.findall(norm(q))}
    computed = (f.get('source') or {}).get('derivation') == 'computed'
    for t in list(f.get('verbatim') or [])[:1]:
        mk = find_markers(t, RISKY_FOR_EVIDENCE)
        for cl, hits in mk.items():
            for frag, _ in hits:
                c, rx = concept_of(frag)
                if c:
                    if not rx.search(qs):
                        gap.append(frag)
                    continue
                st = {stem(w) for w in WORD_RX.findall(norm(frag)) if w not in STOP}
                if st and not any(x in q_stems for x in st):
                    gap.append(frag)
        if computed:
            continue  # числа посчитаны: правило в source.computation
        qn = {round(n['value'], 6) for n in extract_numbers(q) if 'value' in n} | {x for n in extract_numbers(q) if 'range' in n for x in n['range']}
        for n in extract_numbers(t):
            vals = [n['value']] if 'value' in n else n['range']
            for v in vals:
                if round(v, 6) not in qn and not (n['kind'] == 'year' and str(int(v)) in qs):
                    gap.append(n['raw'])
    return sorted(set(gap))


def check_units(units, facts, today, rules=(), strict=False, genre=None, verbose=False, ctx=None):
    F, ok_claims = [], []
    lctx = ctx or legal_ctx()   # правовой модуль H: юрисдикция и отрасль (по умолчанию ru, general)
    stats = {'units': len(units), 'claims': 0, 'supported': 0, 'placeholders': 0, 'by_class': {}}
    placeholder_hits = []

    def mark_claim(cls, supported):
        stats['claims'] += 1
        stats['supported'] += int(bool(supported))
        c = stats['by_class'].setdefault(cls, {'claims': 0, 'supported': 0})
        c['claims'] += 1
        c['supported'] += int(bool(supported))

    for u in units:
        text = u['text']
        q_unit = is_question(text) or u.get('slot_type') in QUESTION_SLOTS
        # ---- заглушки
        for m in PLACEHOLDER_RX.finditer(text):
            stats['placeholders'] += 1
            placeholder_hits.append(m.group(0))
            if facts.missing and not placeholder_listed(m.group(0), facts):
                add(F, 'warning', 'COPY-F-PLACEHOLDER-UNLISTED', u, m.group(0), None, 'заглушка не заведена в missing[]',
                    'Заведите пробел в facts.yaml missing[] (что, кто даст, когда) — иначе его никто не закроет.')
        body = PLACEHOLDER_RX.sub(' ', text)
        # ---- ссылки на факты
        cand = {}
        for fid in u['fact_ids']:
            fid = str(fid).replace('fact:', '')
            f = facts.by_id.get(fid)
            if f is None:
                if fid in facts.missing_ids:
                    add(F, 'error', 'COPY-F-REF', u, fid, None, f'fact_ids ссылается на пробел missing:{fid} — факта ещё нет', 'Оставьте [PLACEHOLDER] до ответа заказчика.')
                else:
                    add(F, 'error', 'COPY-F-REF', u, fid, None, f'fact_ids: нет факта {fid}', 'Исправьте id или заведите факт в facts.yaml.')
                continue
            cand[f['id']] = 'fact_ids'
        strong = dict(cand)      # факты, найденные по числу, дате, цитате, имени, fact_ids — основа проверки «шире факта»
        related = {}             # факты, покрывшие маркер класса или термин свойства (проверяются на публикуемость)
        strong_pos = []          # (факт, позиция числа или даты) — для проверки утверждения внутри одного предложения
        # ---- числа
        nums = extract_numbers(body)
        spec_label = None
        mm = re.match(r'^\s*([^—:\-–]{2,40}?)\s*[—:–-]\s', body)
        if mm:
            spec_label = [w for w in WORD_RX.findall(norm(mm.group(1))) if w not in STOP]
        for n in nums:
            if ORDINAL_LINE_RX.match(body[max(0, n['start'] - 6):n['start'] + 4]) or re.match(r'^\s*0\d\s*$', n['raw']):
                continue
            noun_st = {stem(w) for w in n['noun']}
            if noun_st & STRUCT_NOUNS:
                continue
            if 'value' in n and n['value'] in (0, 1) and not n['unit'] and not n['noun']:
                continue
            if not noun_st and spec_label:
                noun_st = {stem(w) for w in spec_label}
            n_eff = dict(n, noun=list(noun_st))
            best, why_bad, match_ids = None, [], []
            ordered = sorted(facts.facts, key=lambda f: 0 if f['id'] in cand else 1)
            for f in ordered:
                for fv in facts.values.get(f['id'], []):
                    if n['kind'] == 'year' and fv.get('date') and 'value' in n:
                        if date_supported((int(n['value']), None, None), fv['date']):
                            match_ids.append(f['id'])
                            best = best or (f, 'год совпал')
                        continue
                    if fv.get('rating'):
                        continue
                    if not unit_ok(n['unit'], fv.get('unit'), noun_st):
                        continue
                    ok, why = num_supported(n, fv)
                    if ok is None:
                        continue
                    nk = noun_ok(noun_st, fv.get('what'))
                    if ok and nk is False and n['unit'] in COUNT_UNITS and fv.get('unit') in COUNT_UNITS:
                        why_bad.append((f, f"число совпало, объект счёта другой: «{' '.join(n['noun']) or '—'}» против «{', '.join(sorted(fv.get('what') or []))}»"))
                        continue
                    if ok:
                        match_ids.append(f['id'])
                        if best is None or (nk and best[1] != 'объект совпал'):
                            best = (f, 'объект совпал' if nk else why)
                    else:
                        if nk is not False:
                            why_bad.append((f, why))
            if any(fid in cand for fid in match_ids):   # явные fact_ids слота важнее случайных совпадений
                match_ids = [fid for fid in match_ids if fid in cand]
                if best and best[0]['id'] not in cand:
                    best = (facts.by_id[match_ids[0]], 'fact_ids')
            mark_claim('fact-number', best is not None)
            if best:
                for fid in match_ids[:3]:
                    strong.setdefault(fid, 'number')
                    strong_pos.append((fid, n['start']))
                ok_claims.append({'unit': u['id'], 'fragment': n['raw'], 'fact': best[0]['id'], 'how': best[1]})
            elif why_bad:
                f, why = why_bad[0]
                add(F, 'info' if q_unit else 'error', 'COPY-F-NUM-MISMATCH', u, n['raw'], 'fact-number', f"не совпадает с fact:{f['id']}: {why}",
                    f"Приведите число к факту дословно («{(f.get('verbatim') or [''])[0][:60]}») или заведите новый факт с источником.", [f['id']])
            else:
                lvl = 'info' if q_unit else 'error'
                add(F, lvl, 'COPY-F-NUM', u, n['raw'], 'fact-number', 'число без факта',
                    'Замените на [PLACEHOLDER: что за число] и заведите пробел в missing, либо добавьте факт с источником и датой.')
        # ---- даты
        for d in extract_dates(body):
            y, mo, dd = d['date']
            found = None
            for f in sorted(facts.facts, key=lambda f: 0 if f['id'] in cand else 1):
                for fv in facts.values.get(f['id'], []):
                    if fv.get('date') and date_supported((y, mo, dd), fv['date']):
                        found = f
                        break
                if not found and (set(f.get('claim_class') or []) & {'promo-deadline', 'availability-scarcity'} or f.get('kind') == 'promo'):
                    vu = parse_iso((f.get('valid') or {}).get('until'))
                    if vu and date_supported((y, mo, dd), vu):
                        found = f
                if found:
                    break
            mark_claim('date', found is not None)
            if found:
                strong.setdefault(found['id'], 'date')
                strong_pos.append((found['id'], d['start']))
                ok_claims.append({'unit': u['id'], 'fragment': d['raw'], 'fact': found['id'], 'how': 'дата'})
            else:
                add(F, 'info' if q_unit else 'error', 'COPY-F-DATE', u, d['raw'], 'fact-number', 'дата без факта',
                    'Дата срока, отгрузки, акции — только из facts.yaml (values.date или valid.until); иначе [PLACEHOLDER].')
            if y and mo and (y, mo, dd or 28) < (today.year, today.month, today.day) and re.search(r'до\s*$|until\s*$|по\s*$', soft(body[:d['start']])[-8:]):
                add(F, 'error', 'COPY-F-EXPIRED', u, d['raw'], 'promo-deadline', 'срок в тексте уже прошёл', 'Уберите истёкшую акцию или обновите дату по факту.')
        # ---- рейтинги
        for r in extract_ratings(body):
            found = None
            for f in facts.facts:
                for fv in facts.values.get(f['id'], []):
                    if 'value' in fv and fv.get('unit') in ('stars', None) and abs(fv['value'] - r['value']) < 1e-9 and (not fv.get('scale') or float(fv['scale']) == r['scale']) and (f.get('kind') == 'rating' or fv.get('rating')):
                        found = f
                        break
                if found:
                    break
            plat_t = platforms_in(body)
            if found and plat_t:
                plat_f = platforms_in(' '.join([str((found.get('source') or {}).get('who', '')), str((found.get('source') or {}).get('url', ''))] + fact_texts(found)))
                if plat_f and not (plat_t & plat_f):
                    add(F, 'error', 'COPY-F-RATING', u, r['raw'], 'rating', f"рейтинг совпал с fact:{found['id']}, но площадка другая: в тексте {', '.join(sorted(plat_t))}, в факте {', '.join(sorted(plat_f))}",
                        'Назовите площадку из факта или заведите отдельный факт рейтинга этой площадки.', [found['id']])
                    found = None
                    mark_claim('rating', False)
                    continue
            mark_claim('rating', found is not None)
            if found:
                strong.setdefault(found['id'], 'rating')
                ok_claims.append({'unit': u['id'], 'fragment': r['raw'], 'fact': found['id'], 'how': 'рейтинг'})
                for fv in facts.values.get(found['id'], []):
                    if fv.get('src') == 'values' and not fv.get('count'):
                        add(F, 'warning', 'COPY-F-RATING', u, r['raw'], 'rating', f"fact:{found['id']}: у рейтинга нет числа оценок", 'Добавьте count и as_of (снимок площадки).', [found['id']])
            else:
                add(F, 'error', 'COPY-F-RATING', u, r['raw'], 'rating', 'рейтинг без факта (площадка, шкала, число оценок, дата)',
                    'Уберите или добавьте факт kind: rating со ссылкой на площадку и снимком; рядом — источник и дата.')
        # ---- цитаты
        quotes = extract_quotes(body)
        if u.get('slot_type') in QUOTE_SLOTS and not quotes and len(tokens(body)) >= 3:
            quotes = [{'raw': body, 'text': body.strip().strip('«»"“”'), 'start': 0, 'words': len(tokens(body))}]
        for qd in quotes:
            if qd['words'] < 3:
                continue
            res = match_quote(qd['text'], facts)
            mark_claim('testimonial-quote', res['status'] in ('exact', 'recut'))
            if res['fact']:
                strong.setdefault(res['fact']['id'], 'quote')
            if res['status'] == 'exact':
                ok_claims.append({'unit': u['id'], 'fragment': qd['raw'][:60], 'fact': res['fact']['id'], 'how': 'цитата дословно'})
            elif res['status'] == 'recut':
                add(F, 'warning', 'COPY-F-QUOTE-RECUT', u, qd['raw'][:120], 'testimonial-quote', f"новая нарезка цитаты fact:{res['fact']['id']} (фрагменты есть в исходнике, но этой формы нет в verbatim)",
                    'Согласуйте сокращение с автором, добавьте форму в verbatim и запишите правку в edits.', [res['fact']['id']])
            elif res['status'] == 'edited':
                add(F, 'error', 'COPY-F-QUOTE-EDIT', u, qd['raw'][:120], 'testimonial-quote', f"цитата отличается от fact:{res['fact']['id']}: {res['diff']}",
                    'Верните слова автора дословно; допустимы многоточие, опечатка, пунктуация (edits) — не смена смысла.', [res['fact']['id']])
            elif res['status'] == 'typo':
                add(F, 'info', 'COPY-F-QUOTE-EDIT', u, qd['raw'][:120], 'testimonial-quote', f"мелкая правка цитаты fact:{res['fact']['id']}: {res['diff']}",
                    'Если это опечатка — запишите edits: {type: typo}.', [res['fact']['id']])
            else:
                if qd['words'] >= 3 and not name_known(qd['text'], facts):
                    add(F, 'error', 'COPY-F-QUOTE', u, qd['raw'][:120], 'testimonial-quote', 'цитата без факта (нет отзыва или цитаты с разрешением)',
                        'Уберите кавычки и цитату или добавьте факт kind: testimonial с original_ref, разрешением и attribution.')
        # ---- имена
        for name, pos in extract_names(body):
            kn = name_known(name, facts)
            if kn:
                ent, fid = kn
                if fid and fid in facts.by_id:
                    strong.setdefault(facts.by_id[fid]['id'], 'name')
                elif isinstance(kn, tuple) and kn[1] is None and ent and ent.get('type') in ('client', 'partner', 'person', 'publication', 'award') and not ent.get('fact_id'):
                    add(F, 'error', 'COPY-F-NAME', u, name, 'client-logo', f"сущность {ent.get('id')} ({ent.get('type')}) без факта с разрешением", 'Добавьте fact_id с разрешением или уберите имя.')
                continue
            ctx = u.get('slot_type') in ATTRIB_SLOTS or bool(find_markers(body, ['client-logo', 'testimonial-quote']))
            add(F, 'error' if ctx else 'warning', 'COPY-F-NAME', u, name, 'client-logo' if ctx else None,
                'имя или название не найдено в facts.yaml (entities, факты)',
                'Проверьте, что это реальный клиент, человек или место с фактом и разрешением; иначе уберите или замените на [PLACEHOLDER].')
        # ---- маркеры классов
        markers = find_markers(body)
        for cl in sorted(set(u.get('claim_flags') or []) - set(markers) - {'fact-number', 'fact-property'}):
            pass
        spans = sentence_spans(body)
        for cl, hits in markers.items():
            for frag, pos in hits[:3]:
                strong_ids = [fid for fid in strong if fid in facts.by_id]
                sp = next(((a, b) for a, b in spans if a <= pos < b), (0, len(body)))
                sent_ids = [fid for fid, p0 in strong_pos if sp[0] <= p0 < sp[1] and fid in facts.by_id] + [fid for fid in cand if fid in facts.by_id]
                if sent_ids:
                    # в одном предложении с числом или датой факта: часть утверждения обязана быть в том же факте
                    covered_by = next((facts.by_id[fid] for fid in sent_ids if covers(facts.softtext[fid], facts.stems.get(fid, set()), frag)), None)
                    if not covered_by:
                        mark_claim(cl, False)
                        lvl = 'info' if (q_unit and not never_hit(body, cl, facts)) else 'error'
                        near = ', '.join(f'fact:{x}' for x in dict.fromkeys(sent_ids))
                        add(F, lvl, 'COPY-F-EXTENDS', u, frag, cl, f'утверждение шире факта ({near}): «{frag}» в факте нет — похоже на вывод из другого факта',
                            'Спросите заказчика (missing) и уберите эту часть до ответа; факт не расширяется выводом.', list(dict.fromkeys(sent_ids))[:3])
                        continue
                    mark_claim(cl, True)
                    ok_claims.append({'unit': u['id'], 'fragment': frag, 'fact': covered_by['id'], 'how': f'класс {cl}'})
                    continue
                near_ids = strong_ids + [fid for fid in related if fid in facts.by_id and fid not in strong_ids]
                covered_by = next((facts.by_id[fid] for fid in near_ids if covers(facts.softtext[fid], facts.stems.get(fid, set()), frag)), None)
                if not covered_by:
                    pool = [f for f in facts.facts if cl in (f.get('claim_class') or []) and covers(facts.softtext[f['id']], facts.stems.get(f['id'], set()), frag)]
                    if cl in OBJECT_CLASSES:
                        obj = object_stems(body, frag)
                        if obj:
                            pool = [f for f in pool if obj & facts.stems.get(f['id'], set())]
                    covered_by = pool[0] if pool else None
                if not covered_by:
                    mark_claim(cl, False)
                    lvl = 'info' if (q_unit and not never_hit(body, cl, facts)) else 'error'
                    if strong_ids:
                        near = ', '.join(f'fact:{x}' for x in strong_ids[:3])
                        add(F, lvl, 'COPY-F-EXTENDS', u, frag, cl, f'утверждение шире факта ({near}): «{frag}» в факте нет — похоже на вывод из другого факта',
                            'Спросите заказчика (missing) и уберите эту часть до ответа; факт не расширяется выводом.', strong_ids[:3])
                    else:
                        rule_nc = next((r['id'] for r in facts.never if cl in (r.get('claim_class') or [])), None)
                        near = hint_facts(body, facts)
                        alt = [f for f in facts.facts if covers(facts.softtext[f['id']], facts.stems.get(f['id'], set()), frag)
                               and (cl not in OBJECT_CLASSES or not object_stems(body, frag) or object_stems(body, frag) & facts.stems.get(f['id'], set()))]
                        msg = f'утверждение класса {cl} без факта' + (f' (запрет по умолчанию {rule_nc})' if rule_nc else '')
                        if alt:
                            msg += f"; слова есть в fact:{alt[0]['id']}, но его класс — {', '.join(alt[0].get('claim_class') or [])}: проверьте основание и добавьте класс {cl}"
                            related.setdefault(alt[0]['id'], 'alt')
                        elif near:
                            msg += f"; рядом упомянут {', '.join('fact:' + x for x in near)} — он не подтверждает «{frag}» (вывод из другого факта?)"
                        add(F, lvl, 'COPY-F-CLASS', u, frag, cl, msg, class_fix(cl, facts), ([alt[0]['id']] if alt else []) + near)
                    continue
                if covered_by['id'] not in strong:
                    related.setdefault(covered_by['id'], 'marker')
                mark_claim(cl, True)
                ok_claims.append({'unit': u['id'], 'fragment': frag, 'fact': covered_by['id'], 'how': f'класс {cl}'})
        # ---- термины свойств
        for term, pos in find_property_terms(body):
            ts = {stem(w) for w in WORD_RX.findall(norm(term)) if w not in STOP}
            sup = [f for f in facts.facts if ts and (ts <= facts.stems.get(f['id'], set()) or all(s in facts.softtext[f['id']] for s in ts))]
            mark_claim('fact-property', bool(sup))
            if sup:
                related.setdefault(sup[0]['id'], 'property')
                ok_claims.append({'unit': u['id'], 'fragment': term, 'fact': sup[0]['id'], 'how': 'свойство'})
            else:
                add(F, 'info' if q_unit else 'error', 'COPY-F-PROPERTY', u, term, 'fact-property', f'свойство «{term}» без факта',
                    'Уберите свойство или спросите заказчика (missing) — свойства продукта не выводятся из описания.')
        # ---- never_claim
        quote_spans = []   # цитаты, совпавшие с публикуемым отзывом: (начало, конец, факт)
        for qd in quotes:
            if qd['words'] >= 3:
                res_q = match_quote(qd['text'], facts)
                if res_q['status'] in ('exact', 'recut', 'typo') and res_q['fact'] and not [x for x in publishable_issues(res_q['fact'], facts, today) if x[0] == 'error']:
                    quote_spans.append((qd['start'], qd['start'] + len(qd['raw']), res_q['fact']))
        for r in facts.never:
            hit, hit_pos = None, None
            for p in r.get('patterns') or []:
                try:
                    mm2 = re.search(p, soft(body), re.I)
                except re.error:
                    mm2 = None
                if mm2:
                    hit, hit_pos = mm2.group(0), mm2.start()
                    break
            if not hit and r.get('origin') == 'project' and not r.get('patterns'):
                for cl in r.get('claim_class') or []:
                    if cl in markers:
                        hit = markers[cl][0][0]
                        break
            if not hit:
                continue
            in_quote = next((q for q in quote_spans if hit_pos is not None and q[0] <= hit_pos < q[1]), None)
            if in_quote and r.get('voice', 'company') != 'any':
                add(F, 'warning', 'COPY-F-TYPICALITY', u, hit, ','.join(r.get('claim_class') or []) or None,
                    f"never_claim {r['id']} снят для цитаты клиента fact:{in_quote[2]['id']} (запрет — на голос компании): это опыт одного клиента",
                    'Оставьте цитату с подписью; не повторяйте её голосом компании; если это ключевое свойство (срок, бюджет, результат) — рядом обычный результат или оговорка о том, как бывает у других клиентов (FTC 16 CFR 255.2(b)).',
                    [in_quote[2]['id']])
                continue
            lift = r.get('lift', 'never')
            sup = None
            if lift != 'never':
                for fid in list(strong) + list(related):
                    f = facts.by_id.get(fid)
                    if f and set(r.get('claim_class') or []) & set(f.get('claim_class') or []):
                        iss = [x for x in publishable_issues(f, facts, today) if x[0] == 'error']
                        if lift == 'legal-review' and ((f.get('legal') or {}).get('review') or {}).get('status') != 'approved':
                            continue
                        if not iss:
                            sup = f
                            break
            if sup:
                continue
            if r.get('origin') == 'default' and not (r.get('patterns')) :
                continue  # запреты по умолчанию без своих регулярок уже выражены COPY-F-CLASS
            add(F, 'error', 'COPY-F-NEVER', u, hit, ','.join(r.get('claim_class') or []) or None,
                f"never_claim {r['id']}: {r.get('text', '')[:120]}" + (' (снимается только фактом)' if lift == 'with-fact' else ' (не снимается)' if lift == 'never' else ' (только после проверки юриста)'),
                'Уберите утверждение; вопросом тоже нельзя («Хотите … без …?» — то же обещание).')
        # ---- проблемы использованных фактов
        for fid, how in list(strong.items()) + [(k, v) for k, v in related.items() if k not in strong]:
            f = facts.by_id.get(fid)
            if not f:
                continue
            for lvl, rule, msg, fix in publishable_issues(f, facts, today):
                add(F, lvl, rule, u, fid, ','.join(f.get('claim_class') or []), msg, fix, [fid])
            use = f.get('use') or {}
            if use and not use.get('any') and not q_unit:
                st_, role = u.get('slot_type'), u.get('section_role')
                bad = []
                places = [x for x in ((st_, use.get('slot_types')), (role, use.get('section_roles'))) if x[0] and x[1]]
                if places and not any(v in lst for v, lst in places):
                    bad.append(' и '.join((f'слот {v}' if lst is use.get('slot_types') else f'секция {v}') for v, lst in places))
                if use.get('page_types') and u.get('page_type') and u['page_type'] not in use['page_types']:
                    bad.append(f"тип страницы {u['page_type']}")
                if bad:
                    add(F, 'warning', 'COPY-F-USE', u, fid, None, f"fact:{fid} стоит вне разрешённых мест: {', '.join(bad)}", 'Проверьте use в facts.yaml или перенесите утверждение.', [fid])
            if use.get('not_in') and not q_unit and ((u.get('slot_type') and u['slot_type'] in use['not_in']) or (u.get('section_role') and u['section_role'] in use['not_in'])):
                add(F, 'error', 'COPY-F-USE', u, fid, None, f"fact:{fid} стоит в запрещённом месте (use.not_in: {', '.join(use['not_in'])})" + (f" — {f.get('notes')[:100]}" if f.get('notes') else ''),
                    'Перенесите утверждение туда, где факт разрешён, или измените подачу (например, не зачёркнутой «старой» ценой).', [fid])
            if use.get('requires_nearby') and how in ('number', 'rating', 'fact_ids', 'marker', 'date') and not nearby_ok(use['requires_nearby'], u, units):
                add(F, 'warning', 'COPY-F-NEARBY', u, fid, None, f"fact:{fid}: рядом должно стоять: {use['requires_nearby']}", 'Добавьте источник или оговорку в тот же блок (slot stat-source, cta-note).', [fid])
        # ---- флаги copy deck
        declared = set(u.get('claim_flags') or [])
        found_cl = set(markers) | ({'fact-number'} if nums else set())
        missing_flags = sorted((found_cl - declared) - {'fact-number', 'purchase-terms', 'company-details'}) if u.get('claim_flags') is not None and u.get('slot_type') else []
        if missing_flags and u['id'].count('/') >= 3:
            add(F, 'info', 'COPY-F-FLAGS', u, ','.join(missing_flags), None, 'в claim_flags слота нет найденных классов', 'Добавьте классы в claim_flags (их читают H и copydeck.py).')
        # ---- строгий режим: утверждения без опоры
        if strict and u.get('slot_type') in (None, 'body', 'card-body', 'step-body', 'subheadline', 'spec-row', 'faq-a', 'case-summary', 'case-result', 'pricing-feature', 'guarantee-text', 'objection-answer') and not q_unit:
            covered = [fid for fid in list(strong) + list(related) if fid in facts.by_id]
            if not covered and len(tokens(body)) >= 5:
                us = stems(body)
                best = max(((len(us & facts.stems[f['id']]) / max(1, len(us)), f['id']) for f in facts.facts), default=(0, None))
                if best[0] < 0.34:
                    add(F, 'warning', 'COPY-F-UNSUPPORTED', u, body[:80], 'fact-property', f'в тексте утверждение без опоры на факт (перекрытие слов с лучшим фактом {best[0]:.0%})',
                        'Строгий режим: у содержательного утверждения о продукте или услуге должен быть факт; иначе — голос клиента без обещаний или [PLACEHOLDER].')
        # ---- внешние правила (H): правовой модуль — apply_legal_rules
        if rules:
            apply_legal_rules(F, u, body, markers, strong, related, facts, units, rules, genre, lctx)
    # дедупликация
    seen, out = set(), []
    for f in F:
        k = (f['unit'], f['rule'], str(f['fragment'])[:60], f['message'][:60])
        if k in seen:
            continue
        seen.add(k)
        out.append(f)
    return out, ok_claims, stats


OBJECT_CLASSES = {'price-discount', 'guarantee', 'fact-number', 'client-logo', 'award-press', 'certification', 'origin',
                  'eco-natural', 'superlative', 'comparison'}
GENERIC = {stem(w) for w in 'наш наша наши ваш ваша ваши весь вся всей всех все россия россии город городе мир мире '
           'клиент клиенты клиентов довольных довольный уже только сейчас всегда очень our your all every'.split()}


def object_stems(body, frag):
    """Слова единицы помимо маркера (объект утверждения: «консультация» в «Консультация бесплатно»)."""
    fr = {stem(w) for w in WORD_RX.findall(norm(frag))}
    return {stem(w) for w in WORD_RX.findall(norm(body)) if w not in STOP and not w.isdigit()} - fr - GENERIC


def sentence_spans(text):
    """Границы предложений: [(начало, конец)] по . ! ? … ; (не режет «8 900», «4,9», «2700–5000»)."""
    spans, start = [], 0
    for m in re.finditer(r'(?<!\d)[.!?…;]+(?=\s|$)|(?<=\d)[.!?…;]+(?=\s+[А-ЯЁA-Z]|$)', text):
        spans.append((start, m.end()))
        start = m.end()
    if start < len(text):
        spans.append((start, len(text)))
    return spans or [(0, len(text))]


def placeholder_listed(ph, facts):
    """Заглушка заведена в missing: дословно или половина значимых слов совпадает с what/placeholder пробела."""
    if norm(ph) in facts.placeholders:
        return True
    st = {stem(w) for w in WORD_RX.findall(norm(PLACEHOLDER_RX.sub(lambda m: m.group(1) or '', ph))) if w not in STOP and len(w) > 2}
    if not st:
        return False
    for mi in facts.missing:
        ms = {stem(w) for w in WORD_RX.findall(norm(str(mi.get('what', '')) + ' ' + str(mi.get('placeholder', ''))))}
        if len(st & ms) >= max(1, (len(st) + 1) // 2):
            return True
    return False


def nearby_ok(req, u, units):
    """Выполнено ли требование «рядом должно стоять»: фрагменты в «ёлочках» — дословно (без регистра) в единице или её
    секции; «источник/по данным/дата» — признак источника; иначе половина значимых слов требования."""
    same = [x['text'] for x in units if x.get('section') == u.get('section') and x.get('page') == u.get('page')] or [u['text']]
    zone = soft(' '.join(same))
    frags = re.findall(r'«([^»]+)»', req)
    if frags:
        return all(soft(f_) in zone for f_ in frags)
    if re.search(r'источник|по данным|дат[аы]|source', req, re.I) and SOURCE_HINT_RX.search(zone):
        return True
    st = {stem(w) for w in WORD_RX.findall(norm(req)) if w not in STOP and len(w) > 2}
    zs = {stem(w) for w in WORD_RX.findall(norm(zone))}
    return bool(st) and len(st & zs) >= max(1, len(st) // 2)


def hint_facts(body, facts):
    """Факты, чьи сущности (имена, места) упомянуты в тексте — для подсказки «вывод из другого факта»."""
    words = {stem(w) for w in WORD_RX.findall(norm(body))}
    out = []
    for e in facts.entities:
        if e.get('type') in ('product',):
            continue
        for n in e.get('names') or []:
            ws = [stem(w) for w in WORD_RX.findall(norm(n))]
            if ws and all(w in words for w in ws):
                for f in facts.facts:
                    if e['id'] in (f.get('entities') or []) and f['id'] not in out:
                        out.append(f['id'])
                break
    return out[:3]


def get_path(d, path):
    cur = d
    for p in path.split('.'):
        if not isinstance(cur, dict) or p not in cur:
            return None
        cur = cur[p]
    return cur


def never_hit(body, cl, facts):
    for r in facts.never:
        if r.get('origin') == 'project' and cl in (r.get('claim_class') or []):
            return True
    return False


def class_fix(cl, facts):
    info = facts.class_info.get(cl, {})
    needs = ', '.join(info.get('needs') or []) or 'факт с источником'
    law = info.get('law')
    return f'Нужен факт класса {cl} ({needs})' + (f'; ориентир права: {law} — H' if law else '') + '; до этого — убрать утверждение или [PLACEHOLDER].'


def name_known(name, facts):
    n = norm(name).strip('"').strip()
    if not n:
        return None
    if n in facts.names:
        return facts.names[n]
    ws = WORD_RX.findall(n)
    if ws and all(stem(w) in facts.name_stems for w in ws):
        return facts.name_stems[stem(ws[0])]
    if ws and all(stem(w) in facts.all_stems for w in ws):
        for f in facts.facts:
            if all(stem(w) in facts.stems[f['id']] for w in ws):
                return (None, f['id'])
    return None


def match_quote(q, facts):
    """Цитата против фактов-отзывов: exact | recut | typo | edited | none."""
    nq = norm(q).strip(' ."\'')
    frags = [x.strip(' .,;:-') for x in re.split(r'\.\.\.|…', nq) if x.strip(' .,;:-')]
    best = {'status': 'none', 'fact': None, 'diff': ''}
    best_ratio = 0.0
    for f in facts.facts:
        if f.get('kind') not in ('testimonial', 'expert-quote', 'case', 'press') and 'testimonial-quote' not in (f.get('claim_class') or []):
            continue
        verb = [norm(v).strip(' ."\'') for v in f.get('verbatim') or []] + [norm(f.get('canonical') or '')]
        orig = norm((f.get('source') or {}).get('quote') or '')
        for v in verb:
            if nq and nq in v:
                return {'status': 'exact', 'fact': f, 'diff': ''}
        pos, ok = 0, True
        for fr in frags:
            i = orig.find(fr, pos) if orig else -1
            if i < 0:
                ok = False
                break
            pos = i + len(fr)
        if ok and orig and frags:
            best = {'status': 'recut', 'fact': f, 'diff': ''}
            best_ratio = 1.0
            continue
        for v in verb + ([orig] if orig else []):
            a, b = tokens(nq), tokens(v)
            if not a or not b:
                continue
            sm = difflib.SequenceMatcher(a=b, b=a)
            ratio = sm.ratio()
            cover = sum(bl.size for bl in sm.get_matching_blocks()) / max(1, len(a))
            if cover >= 0.6 and ratio > best_ratio:
                ops = [(t, ' '.join(b[i1:i2]), ' '.join(a[j1:j2])) for t, i1, i2, j1, j2 in sm.get_opcodes() if t != 'equal']
                small = all(t == 'replace' and len(x.split()) == 1 and len(y.split()) == 1 and difflib.SequenceMatcher(a=x, b=y).ratio() >= 0.75 for t, x, y in ops)
                diff = '; '.join(f'«{x}» → «{y}»' if t == 'replace' else f'добавлено «{y}»' if t == 'insert' else f'убрано «{x}»' for t, x, y in ops[:4])
                best = {'status': 'typo' if (small and ops) else 'edited', 'fact': f, 'diff': diff}
                best_ratio = ratio
    return best


# ================================================================ отчёты
def summarize(F, stats):
    s = {lv: sum(1 for f in F if f['level'] == lv) for lv in LEVELS}
    s.update({'units': stats['units'], 'claims': stats['claims'], 'supported': stats['supported'],
              'supported_share': round(stats['supported'] / stats['claims'], 3) if stats['claims'] else None,
              'placeholders': stats['placeholders'], 'by_rule': {}, 'by_class': stats['by_class']})
    for f in F:
        s['by_rule'][f['rule']] = s['by_rule'].get(f['rule'], 0) + 1
    return s


def loc_str(loc):
    parts = [str(loc[k]) for k in ('page', 'section', 'slot') if loc.get(k)]
    if loc.get('variant'):
        parts.append(f"вар. {loc['variant']}")
    if loc.get('line'):
        parts.append(f"стр. {loc['line']}")
    return ' / '.join(parts) or '—'


def md_escape(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def to_md(res):
    s = res['summary']
    L = [f"# claims_check · {os.path.basename(res['input'])}", '',
         f"Дата сверки {res['today']} · facts: `{res.get('facts') or '—'}` · формат входа {res['format']} · версия {VERSION} · не юридическое заключение", '',
         f"**Итог:** {s['error']} error · {s['warning']} warning · {s['info']} info · утверждений {s['claims']}, подтверждено {s['supported']}"
         + (f" ({s['supported_share']:.0%})" if s['supported_share'] is not None else '') + f" · заглушек [PLACEHOLDER]: {s['placeholders']}", '']
    if res['findings']:
        L += ['| № | Где | Фрагмент | Класс | Правило | Уровень | Нарушение | Что сделать |', '|---|---|---|---|---|---|---|---|']
        order = {'error': 0, 'warning': 1, 'info': 2}
        for i, f in enumerate(sorted(res['findings'], key=lambda x: (order[x['level']], x['unit'])), 1):
            L.append(f"| {i} | {md_escape(loc_str(f['location']))} | {md_escape(str(f['fragment'])[:70])} | {f.get('claim_class') or '—'} | {f['rule']} | {f['level']} | {md_escape(f['message'][:180])} | {md_escape(f['fix'][:160])} |")
    else:
        L.append('Нарушений нет.')
    if res.get('verbose') and res.get('supported'):
        L += ['', '## Подтверждённые утверждения', '', '| Единица | Фрагмент | Факт | Как |', '|---|---|---|---|']
        for c in res['supported'][:200]:
            L.append(f"| {md_escape(c['unit'])} | {md_escape(str(c['fragment'])[:60])} | fact:{c['fact']} | {c['how']} |")
    if res.get('rules_loaded'):
        L += ['', f"Внешние правила: {', '.join(res['rules_loaded'])}"]
    lg = res.get('legal')
    if lg:
        L += [f"Право (модуль H {lg.get('module')}): юрисдикция {lg.get('jurisdiction')} · отрасль "
              f"{', '.join(lg.get('legal_category') or [])} · правил {lg.get('rules')} · находок {lg.get('findings')} · не юридическое заключение"]
    return '\n'.join(L) + '\n'


def write_outputs(res, a):
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1, default=str)
    if a.md:
        with open(a.md, 'w', encoding='utf-8') as f:
            f.write(to_md(res))


def today_of(a):
    if getattr(a, 'today', None):
        t = parse_iso(a.today)
        if not t or not t[2]:
            raise SystemExit('--today: ГГГГ-ММ-ДД')
        return dt.date(*t)
    return dt.date.today()


# ================================================================ команды
def cmd_check(a):
    schema = load_schema(a.schema)
    facts = load_facts(a.facts, schema, not a.no_default_never)
    units, fmt, meta = load_input(a.input, a.format, a.all_variants)
    rule_paths = list(a.rules or [])
    if not a.no_external_rules and os.path.exists(RULES_PATH):
        rule_paths.insert(0, RULES_PATH)
    rules, rerrs = load_rules(rule_paths)
    for e in rerrs:
        print('правила:', e, file=sys.stderr)
    today = today_of(a)
    jur = (a.jurisdiction or meta.get('jurisdiction') or facts.data.get('jurisdiction') or 'ru')
    cats = a.legal_category.split(',') if a.legal_category else _as_list(meta.get('legal_category') or facts.data.get('x-legal-category') or ['general'])
    ctx = legal_ctx(jur, cats)
    F, ok_claims, stats = check_units(units, facts, today, rules, a.strict, a.genre, a.verbose, ctx)
    rule_ids = {r['id'] for r in rules}
    if a.legal_only:
        F = [f for f in F if f['rule'] in rule_ids]
    res = {'tool': 'claims_check.py', 'version': VERSION, 'today': today.isoformat(), 'input': a.input, 'format': fmt,
           'facts': a.facts, 'schema': os.path.relpath(a.schema, ROOT) if os.path.exists(a.schema) else None,
           'rules_loaded': [os.path.relpath(p, ROOT) if p.startswith(ROOT) else p for p in rule_paths if os.path.exists(p)],
           'summary': summarize(F, stats), 'findings': F, 'supported': ok_claims if a.verbose else [], 'verbose': a.verbose,
           'legal': {'module': LEGAL_MODULE_VERSION, 'jurisdiction': ctx['jurisdiction'], 'legal_category': sorted(ctx['categories']),
                     'rules': len(rules), 'findings': sum(1 for f in F if f['rule'] in rule_ids), 'legal_only': bool(a.legal_only)}}
    write_outputs(res, a)
    if not a.quiet:
        s = res['summary']
        print(f"claims_check: {s['error']} error, {s['warning']} warning, {s['info']} info; утверждений {s['claims']}, подтверждено {s['supported']}; [PLACEHOLDER] {s['placeholders']}")
        for f in F:
            if f['level'] == 'error' or a.verbose:
                print(f"  {f['level'].upper():7} {f['rule']:26} {loc_str(f['location'])[:40]:40} «{str(f['fragment'])[:50]}» — {f['message'][:110]}")
    return 2 if res['summary']['error'] else 0


def cmd_inventory(a):
    units, fmt, meta = load_input(a.input, a.format, True)
    rows = []
    for i, u in enumerate(units):
        body = PLACEHOLDER_RX.sub(' ', u['text'])
        neigh = ' '.join(x['text'] for x in units[max(0, i - 1):i + 2])
        src_vis = bool(SOURCE_HINT_RX.search(neigh))
        claims = []
        for n in extract_numbers(body):
            if ORDINAL_LINE_RX.match(body[max(0, n['start'] - 6):n['start'] + 4]):
                continue
            if {stem(w) for w in n['noun']} & STRUCT_NOUNS:
                continue
            if 'value' in n and n['value'] in (0, 1) and not n['unit'] and not n['noun']:
                continue
            claims.append(('price-discount' if n.get('unit') in MONEY else 'fact-number', n['raw']))
        for d in extract_dates(body):
            claims.append(('date', d['raw']))
        for r in extract_ratings(body):
            claims.append(('rating', r['raw']))
        for q in extract_quotes(body):
            if q['words'] >= 3:
                claims.append(('testimonial-quote', q['raw'][:60]))
        if u.get('slot_type') in QUOTE_SLOTS and not extract_quotes(body) and len(tokens(body)) >= 3:
            claims.append(('testimonial-quote', body[:60]))
        for cl, hits in find_markers(body).items():
            for frag, _ in hits[:2]:
                claims.append((cl, frag))
        for term, _ in find_property_terms(body):
            claims.append(('fact-property', term))
        nxt = units[i + 1]['text'] if i + 1 < len(units) else ''
        attrib = bool(re.search(r'(?:^|\s)[—-]\s*[A-ZА-ЯЁ][a-zа-яё]+|[A-ZА-ЯЁ][a-zа-яё]+\s+[A-ZА-ЯЁ]\.?,', neigh)) or bool(
            len(nxt.split()) <= 14 and re.match(r'^\W*[A-ZА-ЯЁ][a-zа-яё]+\s+[A-ZА-ЯЁ][a-zа-яё]+', nxt) and re.search(r'CEO|Founder|Director|Manager|Head|директор|основатель|руководител|менеджер|владел', nxt, re.I))
        if attrib and u.get('slot_type') != 'testimonial-quote' and not extract_quotes(body) and len(tokens(body)) >= 8 and re.search(r'\b(I|we|my|our|мне|мы|нам|наш)\b', body, re.I):
            claims.append(('testimonial-quote', body[:60]))
        for cl, frag in claims:
            vis = src_vis or (cl == 'testimonial-quote' and attrib)
            rows.append({'unit': u['id'], 'section': u.get('section'), 'slot_type': u.get('slot_type'), 'class': cl,
                         'fragment': frag, 'source_visible': vis, 'text': u['text'][:160]})
    by = {}
    for r in rows:
        b = by.setdefault(r['class'], {'claims': 0, 'source_visible': 0})
        b['claims'] += 1
        b['source_visible'] += int(r['source_visible'])
    total = len(rows)
    vis = sum(r['source_visible'] for r in rows)
    res = {'tool': 'claims_check.py inventory', 'version': VERSION, 'input': a.input, 'format': fmt, 'units': len(units),
           'claims': total, 'source_visible': vis, 'source_visible_share': round(vis / total, 3) if total else None,
           'by_class': by, 'rows': rows}
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    if a.md:
        L = [f"# inventory · {os.path.basename(a.input)}", '', f"Единиц {len(units)} · утверждений {total} · с видимым источником {vis}" + (f" ({vis / total:.0%})" if total else ''), '',
             '| Класс | Утверждений | С видимым источником |', '|---|---|---|']
        for cl, b in sorted(by.items(), key=lambda x: -x[1]['claims']):
            L.append(f"| {cl} | {b['claims']} | {b['source_visible']} |")
        L += ['', '| Единица | Класс | Фрагмент | Источник виден | Текст |', '|---|---|---|---|---|']
        for r in rows:
            L.append(f"| {r['unit']} | {r['class']} | {md_escape(r['fragment'])[:50]} | {'да' if r['source_visible'] else 'нет'} | {md_escape(r['text'])[:100]} |")
        with open(a.md, 'w', encoding='utf-8') as f:
            f.write('\n'.join(L) + '\n')
    if not a.quiet:
        print(f"inventory: единиц {len(units)}, утверждений {total}, с видимым источником {vis}" + (f" ({vis / total:.0%})" if total else ''))
        for cl, b in sorted(by.items(), key=lambda x: -x[1]['claims']):
            print(f"  {cl:24} {b['claims']:4} видно источник: {b['source_visible']}")
    return 0


def cmd_lint_facts(a):
    schema = load_schema(a.schema)
    facts = load_facts(a.input, schema, True)
    today = today_of(a)
    F = []
    vocab = load_vocab()
    for f in facts.facts:
        u = unit(f"fact:{f['id']}", (f.get('verbatim') or [''])[0])
        for lvl, rule, msg, fix in publishable_issues(f, facts, today):
            add(F, lvl, rule, u, f['id'], ','.join(f.get('claim_class') or []), msg, fix, [f['id']])
        if f.get('kind') in ('testimonial', 'person', 'client', 'partner', 'case', 'expert-quote') and (f.get('permission') or {}).get('status') == 'not-required':
            add(F, 'error', 'COPY-F-PERMISSION', u, f['id'], f.get('kind'), f"fact:{f['id']}: вид {f.get('kind')} требует разрешения третьего лица, а стоит not-required", 'Укажите разрешение субъекта (permission.subject, form, document).')
        if vocab:
            use = f.get('use') or {}
            for key, vk in (('page_types', 'page_types'), ('section_roles', 'section_roles'), ('slot_types', 'slot_types')):
                for x in use.get(key) or []:
                    if x not in vocab.get(vk, set()) and x not in vocab.get('proposals', set()):
                        add(F, 'warning', 'COPY-F-VOCAB', u, x, None, f'{key}: «{x}» нет во временном словаре', 'Возьмите id из 99-raw/notes/temp-vocabulary-v0.yaml или оформите предложение к словарю.')
    for m in facts.missing:
        if not PLACEHOLDER_RX.fullmatch(m.get('placeholder') or ''):
            add(F, 'error', 'COPY-F-PLACEHOLDER', unit(f"missing:{m.get('id')}", m.get('what', '')), m.get('placeholder'), None, 'placeholder не в форме [PLACEHOLDER: …]', 'Исправьте текст заглушки.')
    res = {'tool': 'claims_check.py lint-facts', 'version': VERSION, 'today': today.isoformat(), 'input': a.input,
           'summary': {lv: sum(1 for f in F if f['level'] == lv) for lv in LEVELS}, 'findings': F}
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    if not a.quiet:
        s = res['summary']
        print(f"lint-facts: {s['error']} error, {s['warning']} warning, {s['info']} info")
        for f in F:
            print(f"  {f['level'].upper():7} {f['rule']:22} {f['unit']:34} {f['message'][:120]}")
    return 2 if res['summary']['error'] else 0


def load_vocab():
    if yaml is None or not os.path.exists(VOCAB_PATH):
        return {}
    with open(VOCAB_PATH, encoding='utf-8') as f:
        v = yaml.safe_load(f) or {}
    out = {'page_types': {x['id'] for x in v.get('page_types') or []}, 'section_roles': {x['id'] for x in v.get('section_roles') or []},
           'slot_types': {x['id'] for x in v.get('slot_types') or []}}
    sch = load_schema()
    props = sch.get('x-vocabulary-proposals') or {}
    out['proposals'] = {x['id'] for k in props for x in props[k]}
    return out


def phrase_rx(x):
    """Фраза запрета → регулярка: пробелы → \\s+, N → число («осталось N ламп» → осталось\\s+\\d+\\s+ламп)."""
    out = []
    for w in re.split(r'\s+', soft(x).strip()):
        out.append(r'\d+' if w in ('n', 'n+', 'x', 'х') else re.escape(w))
    return r'\s+'.join(out)


def import_kimi(text, site='imported', date=None):
    """facts.md kimi (шаблон F) → facts.yaml v1 (черновик). Столбцы: ID | Fact | Source | Where; Missing; Never claim."""
    date = date or dt.date.today().isoformat()
    facts, missing, never = [], [], []
    section = None
    header = None
    for line in text.splitlines():
        st = line.strip()
        if st.startswith('## '):
            section = st[3:].lower()
            header = None
            continue
        if section and section.startswith('never') and st.startswith('- '):
            t = st[2:].rstrip(';').strip()
            if t:
                never.append(t)
            continue
        if not st.startswith('|'):
            continue
        cells = [c.strip() for c in st.strip('|').split('|')]
        if header is None:
            header = [c.lower() for c in cells]
            continue
        if all(re.fullmatch(r'-{3,}|:?-+:?', c or '---') for c in cells):
            continue
        if section and section.startswith('facts') and len(cells) >= 4:
            fid, txt, src, where = cells[:4]
            qm = re.search(r'[(（]\s*[«"“]([^»"”]+)[»"”]\s*[)）]', src)
            dm = re.search(r'(\d{4}-\d{2}-\d{2})', src)
            who = re.split(r',', src)[0].strip() or 'заказчик'
            kind = 'price' if re.search(r'₽|руб|\$|€', txt) else ('date' if re.search(MONTH_RX + r'\s+\d{4}', txt, re.I) else 'property')
            cls = {'price': ['price-discount'], 'date': ['purchase-terms'], 'property': ['fact-property']}[kind]
            if re.search(r'\d', txt) and kind == 'property':
                cls = ['fact-property', 'fact-number']
            for mcl in find_markers(txt):
                if mcl not in cls:
                    cls.append(mcl)
            wl = [w.strip().lower() for w in where.split(',') if w.strip()]
            roles = [KIMI_SECTION_ROLE.get(w, w) for w in wl if w != 'cta']
            slots_ = ['cta-label', 'cta-note'] if 'cta' in wl else []
            f = {'id': 'f-' + fid.lower().replace('_', '-') if re.fullmatch(r'[A-Za-z]?\d+', fid) else re.sub(r'[^a-z0-9-]', '-', fid.lower()).strip('-'),
                 'aliases': [fid], 'kind': kind, 'claim_class': cls, 'verbatim': [txt], 'canonical': txt,
                 'source': {'type': 'customer-message', 'who': who, 'where': src, 'date': dm.group(1) if dm else date, 'derivation': 'direct'},
                 'verification': {'status': 'stated'}, 'permission': {'status': 'not-required'},
                 'use': dict({'section_roles': [r for r in roles if re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', r)]}, **({'slot_types': slots_} if slots_ else {})), 'lang': 'ru',
                 'tags': ['imported-from-kimi-facts-md']}
            if qm:
                f['source']['quote'] = qm.group(1)
            facts.append(f)
        elif section and section.startswith('missing') and len(cells) >= 4:
            mid, what, ph, who = cells[:4]
            missing.append({'id': 'm-' + mid.lower() if re.fullmatch(r'[A-Za-z]?\d+', mid) else re.sub(r'[^a-z0-9-]', '-', mid.lower()).strip('-'),
                            'aliases': [mid], 'what': what, 'placeholder': ph if PLACEHOLDER_RX.fullmatch(ph) else f'[PLACEHOLDER: {ph}]', 'who': who})
    nc = []
    for i, t in enumerate(never, 1):
        cls = []
        low = soft(t)
        qm = re.findall(r'[«"“]([^»"”]{3,80})[»"”]', t)
        if qm and i > 4:  # конкретная фраза заказчика: запрет по регулярке фразы, без маркеров класса
            pats = [phrase_rx(x) for x in qm]
            nc.append({'id': f'nc-imported-{i}', 'text': t, 'patterns': pats, 'lift': 'never'})
            continue
        for cl, kw in (('health', 'здоров|зрени|medical|health'), ('testimonial-quote', 'отзыв|testimonial'), ('rating', 'оценк|rating'),
                       ('award-press', 'сми|press|award'), ('availability-scarcity', 'осталось'), ('client-logo', 'logo|trusted'),
                       ('fact-number', 'count|growth'), ('price-discount', 'price|discount'), ('guarantee', 'guarantee')):
            if re.search(kw, low):
                cls.append(cl)
        item = {'id': f'nc-imported-{i}', 'text': t, 'lift': 'never' if i > 4 else 'with-fact'}
        if cls:
            item['claim_class'] = cls
        if 'здоров' in low or 'зрени' in low:
            item['patterns'] = ['глаз', 'зрени', 'здоров']
        nc.append(item)
    return {'facts_version': 1, 'date': date, 'site': site, 'lang': 'ru', 'jurisdiction': 'ru', 'status': 'draft',
            'collected_by': 'claims_check.py import-kimi (черновик: kind и класс угаданы, проверить руками)',
            'never_claim_defaults': 'ru-default-1', 'facts': facts, 'missing': missing, 'never_claim': nc}


def cmd_import_kimi(a):
    with open(a.input, encoding='utf-8') as f:
        data = import_kimi(f.read(), a.site, a.date)
    out = yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120) if yaml else json.dumps(data, ensure_ascii=False, indent=1)
    head = f"# facts.yaml — импорт из {os.path.basename(a.input)} (kimi facts.md) · claims_check.py {VERSION} · {dt.date.today().isoformat()}\n# kind и claim_class угаданы по тексту — проверить; строки Never claim шаблона kimi — первые 4 с lift: with-fact.\n"
    if a.output:
        with open(a.output, 'w', encoding='utf-8') as f:
            f.write(head + out)
        print(a.output)
    else:
        print(head + out)
    return 0


def cmd_rules_schema(a):
    print(json.dumps(RULES_SCHEMA, ensure_ascii=False, indent=1))
    return 0


# ================================================================ selftest
FP_PHRASES = [  # лозунги, вопросы, призывы — не утверждения о фактах (опыт B2/03 расширяет до 20+)
    'Свет, под который хочется читать', 'Ремонт, после которого хочется жить дома', 'Считаем смету честно и по пунктам',
    'Как выбрать лампу для чтения?', 'Сколько стоит ремонт двушки?', 'Что будет после заявки?', 'Оставить заявку',
    'Записаться на консультацию', 'Узнать подробнее', 'Скачать презентацию', 'Как это работает', 'Частые вопросы',
    'Самые частые вопросы', 'Первый шаг — заявка на сайте', 'Шаг 1. Оставьте заявку', 'Get started', 'How it works',
    'Book a demo', 'What happens after you sign up?', 'Read the docs']


def _selftest_facts():
    schema = load_schema()
    data = {
        'facts_version': 1, 'date': '2026-09-24', 'site': 'selftest', 'lang': 'ru',
        'entities': [{'id': 'p', 'type': 'product', 'names': ['Кварц']}, {'id': 'kzn', 'type': 'place', 'names': ['Казань', 'Казани']}],
        'facts': [
            {'id': 'price', 'aliases': ['F1'], 'kind': 'price', 'claim_class': ['price-discount'], 'verbatim': ['8 900 ₽ — цена для первых 300 ламп'],
             'canonical': 'Цена — 8 900 ₽ для первых 300 ламп.', 'values': [{'value': 8900, 'unit': 'RUB', 'what': 'цена'}, {'value': 300, 'unit': 'pcs', 'what': 'лампы'}],
             'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
             'permission': {'status': 'not-required'}, 'lang': 'ru', 'use': {'slot_types': ['pricing-price', 'subheadline']}},
            {'id': 'temp', 'kind': 'property', 'claim_class': ['fact-property'], 'verbatim': ['цветовая температура 2700–5000 K'],
             'canonical': 'Температура 2700–5000 K.', 'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'},
             'verification': {'status': 'stated'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'},
            {'id': 'orders', 'kind': 'metric', 'claim_class': ['fact-number'], 'verbatim': ['10 000 заказов'], 'canonical': '10 000 заказов с 2020 года.',
             'values': [{'value': 10000, 'unit': 'pcs', 'what': 'заказы'}], 'source': {'type': 'customer-system', 'who': 'CRM', 'date': '2026-09-01'},
             'verification': {'status': 'verified'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'},
            {'id': 'flats', 'kind': 'metric', 'claim_class': ['fact-number'], 'verbatim': ['1 146 квартир'], 'canonical': '1 146 квартир.',
             'values': [{'value': 1146, 'unit': 'pcs', 'what': 'квартиры'}], 'source': {'type': 'customer-system', 'who': 'CRM', 'date': '2026-09-01'},
             'verification': {'status': 'verified'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'},
            {'id': 'kazan', 'aliases': ['F9'], 'kind': 'property', 'claim_class': ['origin'], 'verbatim': ['сборка в Казани'], 'canonical': 'Сборка в Казани.',
             'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24', 'quote': 'стартап из Казани'},
             'verification': {'status': 'stated'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'},
            {'id': 'review', 'kind': 'testimonial', 'claim_class': ['testimonial-quote'],
             'verbatim': ['«Сдали за 47 рабочих дней… Смета не выросла ни на рубль»'], 'canonical': 'Анна К.: «Сдали за 47 рабочих дней… Смета не выросла ни на рубль».',
             'values': [{'value': 47, 'unit': 'days', 'what': 'рабочие дни'}],
             'source': {'type': 'platform', 'who': 'Анна К.', 'date': '2026-06-14', 'quote': 'Сдали за 47 рабочих дней, раньше срока. Прораб присылал фото. Смета не выросла ни на рубль'},
             'verification': {'status': 'verified'}, 'permission': {'status': 'granted', 'subject': 'Анна К.', 'form': 'written-email', 'shows': ['first-name', 'initials']},
             'attribution': {'name': 'Анна К.'}, 'original_ref': 'x', 'lang': 'ru'},
            {'id': 'review-pending', 'kind': 'testimonial', 'claim_class': ['testimonial-quote'], 'verbatim': ['«Бригада убирала за собой каждый день»'],
             'canonical': 'Игорь: «Бригада убирала за собой каждый день».', 'source': {'type': 'interview', 'who': 'Игорь', 'date': '2026-08-22'},
             'verification': {'status': 'verified'}, 'permission': {'status': 'pending', 'subject': 'Игорь', 'form': 'written-email', 'shows': ['first-name']},
             'attribution': {'name': 'Игорь'}, 'original_ref': 'y', 'lang': 'ru'},
            {'id': 'promo', 'kind': 'promo', 'claim_class': ['price-discount', 'promo-deadline'], 'verbatim': ['Скидка 10 % до 31 октября 2026 года'],
             'canonical': 'Скидка 10 % до 31 октября 2026 года.', 'values': [{'value': 10, 'unit': '%', 'what': 'скидка'}, {'date': '2026-10-31', 'what': 'окончание'}],
             'source': {'type': 'customer-document', 'who': 'заказчик', 'date': '2026-09-15', 'document': 'приказ'}, 'verification': {'status': 'verified'},
             'permission': {'status': 'not-required'}, 'valid': {'until': '2026-10-31'}, 'lang': 'ru'},
            {'id': 'rating', 'kind': 'rating', 'claim_class': ['rating'], 'verbatim': ['4,8 из 5 на Яндекс Картах'], 'canonical': 'Рейтинг 4,8 из 5 по 214 оценкам.',
             'values': [{'value': 4.8, 'unit': 'stars', 'scale': 5, 'count': 214, 'as_of': '2026-09-01'}],
             'source': {'type': 'platform', 'who': 'Яндекс Карты', 'date': '2026-09-01', 'url': 'https://example.org'}, 'verification': {'status': 'verified'},
             'permission': {'status': 'not-required'}, 'valid': {'until': '2026-12-01'}, 'lang': 'ru'},
            {'id': 'best-study', 'kind': 'research', 'claim_class': ['superlative'], 'verbatim': ['самая быстрая доставка в городе по замеру агентства X'],
             'canonical': 'По замеру агентства X (2026), самая быстрая доставка в городе.', 'basis': {'criterion': 'медиана времени доставки', 'document': 'отчёт'},
             'legal': {'review': {'status': 'approved'}},
             'source': {'type': 'research', 'who': 'агентство X', 'date': '2026-05-01', 'document': 'отчёт'}, 'verification': {'status': 'verified'},
             'permission': {'status': 'not-required'}, 'lang': 'ru'},
        ],
        'missing': [{'id': 'legal', 'what': 'юрлицо', 'placeholder': '[PLACEHOLDER: юрлицо]', 'who': 'заказчик'}],
        'never_claim': [{'id': 'nc-eyes', 'text': 'обещания про здоровье и зрение', 'claim_class': ['health'], 'patterns': ['глаз', 'зрени'], 'lift': 'never'}],
    }
    return Facts(data, schema, True), schema


LEGAL_FP_PHRASES = FP_PHRASES + [  # нейтральные строки лендинга: правила H не дают ни error, ни warning (H, волна 2)
    'Ремонт квартир под ключ в Нижнем Новгороде', 'Смета по пунктам до начала работ', 'Выезжаем на замер в день заявки',
    'Отвечаем в течение рабочего дня', 'Оплата по этапам, без предоплаты за весь ремонт', 'Кофе обжариваем по средам',
    'Лампа для чтения с тёплым светом', 'Записаться на пробный урок', 'Try it for 14 days', 'Pricing starts at $29 per seat',
    'Кто мы и как работаем', 'Самые частые вопросы о ремонте', 'Первый шаг — заявка на сайте']

_LEGAL_TEST_RULES = r'''
version: 1
date: "2026-09-24"
defaults: {trigger: pattern, jurisdiction: [ru], lang: any}
rules:
  - id: T-SUP
    level: error
    claim_class: [superlative]
    pattern: '%B%лучш\w+'
    unless: 'по\s+данным'
    requires: {nearby: ['по\s+данным|по\s+замеру'], fact_fields: [basis.criterion]}
    message: "тест: превосходная степень"
  - id: T-FREE
    level: warning
    claim_class: [price-discount]
    pattern: '%B%бесплатн\w*'
    requires: {nearby: ['без\s+условий|при\s+заказе'], fact_conditions: true}
    message: "тест: бесплатно"
  - id: T-EU
    level: error
    jurisdiction: [eu]
    pattern: '%B%скидк\w*'
    message: "тест: профиль ЕС"
  - id: T-MED
    level: error
    legal_category: [medical]
    pattern: '%B%лечени\w*'
    once: page
    requires: {nearby_all: ['противопоказан', 'консультац\w*\s+специалист'], nearby_scope: page}
    message: "тест: оговорка медицины"
  - id: T-LANG
    level: info
    lang: en
    pattern: '\bfree\b'
    message: "тест: язык"
  - id: T-FORBID
    level: error
    legal_category_except: [medical]
    forbid: true
    pattern: '%B%вылеч\w*'
    message: "тест: запрет"
'''


def _selftest_legal(check):
    """Тесты правового модуля H (волна 2): механика требований на встроенных правилах, затем claims-rules.yaml."""
    schema = load_schema()
    today = dt.date(2026, 9, 24)
    empty = Facts({'facts': [], 'never_claim_defaults': 'none'}, schema, False)

    def run(units_, facts_, rules_, jur='ru', cats=('general',)):
        F_, _, _ = check_units(units_, facts_, today, rules_, ctx=legal_ctx(jur, list(cats)))
        return F_

    def ids(F_, rid):
        return [f for f in F_ if f['rule'] == rid]

    with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False, encoding='utf-8') as t:
        t.write(_LEGAL_TEST_RULES)
    rules, errs = load_rules([t.name])
    os.unlink(t.name)
    check('H: встроенные правила загружены (defaults, pattern с макросами)', len(rules) == 6 and not errs, errs)
    R = {r['id']: r for r in rules}
    # превосходная степень: unless, nearby в секции, fact_fields у найденного факта
    check('H: «Лучшая доставка» без критерия → T-SUP', ids(run([unit('a', 'Лучшая доставка в городе')], empty, [R['T-SUP']]), 'T-SUP'))
    check('H: критерий в том же предложении (unless) → тишина', not ids(run([unit('a', 'Лучшая доставка в городе по данным замера агентства X')], empty, [R['T-SUP']]), 'T-SUP'))
    two = [unit('a', 'Лучшая доставка в городе', section='s', page='p'), unit('b', '* По замеру агентства X, май 2026', section='s', page='p')]
    check('H: критерий в той же секции (nearby) → тишина', not ids(run(two, empty, [R['T-SUP']]), 'T-SUP'))
    fdata = {'facts': [{'id': 'best-noproof', 'kind': 'property', 'claim_class': ['superlative'], 'verbatim': ['лучшая доставка в городе'],
                        'canonical': 'Лучшая доставка в городе.', 'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'},
                        'verification': {'status': 'stated'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'}], 'never_claim_defaults': 'none'}
    fx = Facts(fdata, schema, False)
    two_f = [unit('a', 'Лучшая доставка в городе', section='s', page='p', fact_ids=['best-noproof']), two[1]]
    F_ = ids(run(two_f, fx, [R['T-SUP']]), 'T-SUP')
    check('H: факт без basis.criterion → T-SUP «у факта нет basis.criterion»', F_ and 'basis.criterion' in F_[0]['message'], F_)
    facts_b2, _ = _selftest_facts()
    two_ok = [unit('a', 'Самая быстрая доставка в городе', section='s', page='p'), unit('b', '* По замеру агентства X, май 2026', section='s', page='p')]
    rs = dict(R['T-SUP'], _rx=[re.compile(expand_macros(r'%B%сам\w+\s+быстр\w+'), re.I)])
    check('H: факт с basis (best-study, найден маркером) + критерий рядом → тишина', not ids(run(two_ok, facts_b2, [rs]), 'T-SUP'))
    # «бесплатно»: условие факта рядом
    ffree = Facts({'facts': [{'id': 'estimate-free', 'kind': 'price', 'claim_class': ['price-discount'], 'verbatim': ['Смета и выезд замерщика — бесплатно'],
                              'canonical': 'Смета и выезд замерщика бесплатно в пределах города.', 'values': [{'value': 0, 'unit': 'RUB', 'what': 'смета', 'qualifier': 'в пределах города'}],
                              'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
                              'permission': {'status': 'not-required'}, 'lang': 'ru'}], 'never_claim_defaults': 'none'}, schema, False)
    u1 = unit('a', 'Смета и выезд замерщика — бесплатно', section='s', page='p', fact_ids=['estimate-free'])
    F_ = ids(run([u1], ffree, [R['T-FREE']]), 'T-FREE')
    check('H: «бесплатно» без условия из факта («в пределах города») → T-FREE', F_ and 'в пределах города' in F_[0]['message'], F_)
    check('H: условие факта в той же секции → тишина', not ids(run([u1, unit('b', 'Выезжаем в пределах города', section='s', page='p')], ffree, [R['T-FREE']]), 'T-FREE'))
    check('H: «бесплатно» без факта и без условия → T-FREE', ids(run([unit('a', 'Доставка бесплатно')], empty, [R['T-FREE']]), 'T-FREE'))
    check('H: «бесплатно, без условий» → тишина', not ids(run([unit('a', 'Доставка бесплатно, без условий')], empty, [R['T-FREE']]), 'T-FREE'))
    # юрисдикция, отрасль, язык, once
    check('H: правило ЕС молчит при ru', not ids(run([unit('a', 'Скидка 20 % на всё')], empty, [R['T-EU']], 'ru'), 'T-EU'))
    check('H: правило ЕС работает при --jurisdiction eu', ids(run([unit('a', 'Скидка 20 % на всё')], empty, [R['T-EU']], 'eu'), 'T-EU'))
    med = [unit('a', 'Лечение кариеса', page='p1', section='s1'), unit('b', 'Лечение пульпита', page='p1', section='s2')]
    check('H: оговорка медицины молчит для general', not ids(run(med, empty, [R['T-MED']]), 'T-MED'))
    F_ = ids(run(med, empty, [R['T-MED']], cats=['medical']), 'T-MED')
    check('H: medical без оговорки → одна находка на страницу (once: page)', len(F_) == 1, F_)
    med_ok = med + [unit('c', 'Имеются противопоказания, необходима консультация специалиста', page='p1', section='footer')]
    check('H: оговорка на странице (nearby_all, scope page) → тишина', not ids(run(med_ok, empty, [R['T-MED']], cats=['medical']), 'T-MED'))
    med_half = med + [unit('c', 'Имеются противопоказания', page='p1', section='footer')]
    check('H: половина обязательной оговорки → находка', ids(run(med_half, empty, [R['T-MED']], cats=['medical']), 'T-MED'))
    check('H: lang en — английская единица', ids(run([unit('a', 'Get it free today')], empty, [R['T-LANG']]), 'T-LANG'))
    check('H: lang en — русская единица молчит', not ids(run([unit('a', 'Доставка бесплатно, free')], empty, [R['T-LANG']]), 'T-LANG'))
    check('H: запрет вне медицины → T-FORBID', ids(run([unit('a', 'Вылечит спину за месяц')], empty, [R['T-FORBID']]), 'T-FORBID'))
    check('H: legal_category_except medical → тишина', not ids(run([unit('a', 'Вылечит спину за месяц')], empty, [R['T-FORBID']], cats=['medical']), 'T-FORBID'))
    # --- claims-rules.yaml
    if not os.path.exists(RULES_PATH):
        check('H: 08-russian-legal-typography/claims-rules.yaml существует', False, RULES_PATH)
        return
    rules, errs = load_rules([RULES_PATH])
    check(f'H: claims-rules.yaml загружен без ошибок ({len(rules)} правил)', rules and not errs, errs)
    props = RULES_SCHEMA['properties']['rules']['items']['properties']
    rprops = props['requires']['properties']
    with open(RULES_PATH, encoding='utf-8') as f:
        raw_rules = (yaml.safe_load(f) or {}).get('rules') or []
    extra = sorted({k for r in raw_rules for k in r if k not in props} | {k for r in raw_rules for k in (r.get('requires') or {}) if k not in rprops})
    check('H: поля правил ⊆ rules-schema', not extra, extra)
    bad_meta = [r['id'] for r in rules if not (r['id'].startswith('COPY-L-') and law_refs(r) and r.get('source') and (r.get('examples') or {}).get('bad') and (r.get('examples') or {}).get('good'))]
    check('H: у каждого правила COPY-L-id, law, source и пара примеров', not bad_meta, bad_meta)
    classes = {c['id'] for c in schema.get('x-claim-classes') or []}
    bad_cls = sorted({c for r in rules for c in r.get('claim_class') or [] if c not in classes})
    check('H: claim_class правил ⊆ x-claim-classes', not bad_cls, bad_cls)
    miss_bad, hit_good = [], []
    for r in rules:
        ex = r.get('examples') or {}
        jur = ex.get('jurisdiction') or (r.get('jurisdiction') or ['ru'])[0]
        cats = ex.get('legal_category') or (r.get('legal_category') or ['general'])
        st = ex.get('slot_type') or next((s for s in (r.get('slot_types') or []) if '*' not in s), None)
        fx_ex, fids = empty, []
        if isinstance(ex.get('fact'), dict):   # контекст примера: факт, без которого правило не проверить
            fd = {'kind': 'property', 'claim_class': list(r.get('claim_class') or ['fact-property']), 'verbatim': ['x'], 'canonical': 'x',
                  'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
                  'permission': {'status': 'not-required'}, 'lang': 'ru'}
            fd.update(ex['fact'])
            fx_ex, fids = Facts({'facts': [fd], 'never_claim_defaults': 'none'}, schema, False), [fd['id']]
        for bk, gk in (('bad', 'good'), ('bad_en', 'good_en')):
            if ex.get(bk) and not ex.get('skip_bad'):
                if not ids(run([unit('x', ex[bk], slot_type=st, genre=ex.get('genre'), fact_ids=fids)], fx_ex, [r], jur, _as_list(cats)), r['id']):
                    miss_bad.append(f"{r['id']}:{bk}")
            if ex.get(gk) and not ex.get('skip_good'):
                if ids(run([unit('x', ex[gk], slot_type=st, genre=ex.get('genre'), fact_ids=fids)], fx_ex, [r], jur, _as_list(cats)), r['id']):
                    hit_good.append(f"{r['id']}:{gk}")
    check('H: каждый «плохой» пример ловится своим правилом', not miss_bad, miss_bad)
    check('H: ни один «хороший» пример не ловится своим правилом', not hit_good, hit_good)
    fp = []
    for p in LEGAL_FP_PHRASES:
        F_ = [f for f in run([unit('t', p)], empty, rules) if f['level'] in ('error', 'warning') and f['rule'].startswith('COPY-L-')]
        if F_:
            fp.append((p, [(f['rule'], f['fragment']) for f in F_]))
    check(f'H: {len(LEGAL_FP_PHRASES)} нейтральных фраз — ни error, ни warning правил H', not fp, fp)
    # CLI: --legal-only
    with tempfile.TemporaryDirectory() as td:
        pin, pout = os.path.join(td, 'in.txt'), os.path.join(td, 'out.json')
        with open(pin, 'w', encoding='utf-8') as f:
            f.write('Лучший сервис в городе\n')
        code = main(['check', pin, '--legal-only', '--quiet', '--json', pout, '--today', '2026-09-24'])
        with open(pout, encoding='utf-8') as f:
            res = json.load(f)
        check('H: CLI --legal-only: только COPY-L, код 2, блок legal', code == 2 and res['findings'] and all(x['rule'].startswith('COPY-L-') for x in res['findings']) and res['legal']['jurisdiction'] == 'ru', (code, res.get('legal'), [x['rule'] for x in res['findings']]))


def cmd_selftest(_a=None):
    ok = True

    def check(name, cond, got=None):
        nonlocal ok
        ok &= bool(cond)
        print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else f' → {got}'))

    def rules_of(text, facts, today=dt.date(2026, 9, 24), **kw):
        F, _, _ = check_units([unit('t', text, **kw)], facts, today)
        return F

    def errs(F):
        return sorted({f['rule'] for f in F if f['level'] == 'error'})

    # --- извлечение
    n = extract_numbers('Первые 300 ламп — 8 900 ₽ вместо 11 900 ₽')
    check('числа: 300 ламп, 8 900 ₽, 11 900 ₽', [(x.get('value'), x['unit']) for x in n] == [(300, None), (8900, 'RUB'), (11900, 'RUB')], n)
    check('объект счёта «ламп»', n and n[0]['noun'][:1] == ['ламп'], n[:1])
    n = extract_numbers('Цветовая температура — 2700–5000 K')
    check('диапазон 2700–5000 K', n and n[0].get('range') == [2700, 5000] and n[0]['unit'] == 'K', n)
    n = extract_numbers('лампа выставляет температуру от 2700 до 5000 K')
    check('диапазон «от 2700 до 5000 K»', n and n[0].get('range') == [2700, 5000] and n[0]['unit'] == 'K', n)
    n = extract_numbers('Более 10 000+ клиентов, 98 %, 1,5 млн пользователей, 18 Вт, 14 дней, $1,250, 10k+ teams')
    vals = [(x.get('value'), x['unit'], x['cmp']) for x in n]
    check('10 000+ → 10000 gte', (10000, None, 'gte') in vals, vals)
    check('98 % → 98 %', (98, '%', 'eq') in vals, vals)
    check('1,5 млн → 1 500 000', any(v[0] == 1.5e6 for v in vals), vals)
    check('18 Вт → W, 14 дней → days', (18, 'W', 'eq') in vals and (14, 'days', 'eq') in vals, vals)
    check('$1,250 → 1250 USD', (1250, 'USD', 'eq') in vals, vals)
    check('10k+ → 10000 gte', (10000, None, 'gte') in vals, vals)
    n = extract_numbers('Закон 152-ФЗ, ст. 10.1, договор № 2026-041, © 2026, звоните +7 (831) 123-45-67 с 9:00 до 21:00')
    check('законы, №, ©, телефон, время — не числа', n == [], n)
    n = extract_numbers('Работаем с 2014 года')
    check('год «с 2014 года» → kind year', n and n[0]['kind'] == 'year' and n[0]['value'] == 2014, n)
    d = extract_dates('Отгрузка — декабрь 2026. Акция до 31 октября; оплата до 01.12.2026')
    check('даты: декабрь 2026, 31 октября, 01.12.2026', [x['date'] for x in d] == [(2026, 12, None), (None, 10, 31), (2026, 12, 1)], d)
    r = extract_ratings('Рейтинг 4,9 из 5 на Яндекс Картах; 4.8/5 on G2; ★★★★★')
    check('рейтинги 4,9/5, 4.8/5, 5 звёзд', [(x['value'], x['scale']) for x in r] == [(4.9, 5.0), (4.8, 5.0), (5.0, 5.0)], r)
    q = extract_quotes('Анна: «Сдали за 47 рабочих дней… Смета не выросла» и лампа «Кварц»')
    check('цитаты: длинная и короткая', [x['words'] for x in q] == [8, 1], q)
    nm = [x[0] for x in extract_names('Работаем с Газпромом и Kaspersky, офис в Казани. Мы рядом.')]
    check('имена: Газпромом, Kaspersky, Казани', {'Газпромом', 'Kaspersky', 'Казани'} <= set(nm), nm)
    mk = find_markers('Лучший сервис № 1 в России, гарантируем результат, бесплатно, вылечит спину, доход от 100 000')
    check('маркеры: superlative, guarantee, price, health, income', {'superlative', 'guarantee', 'price-discount', 'health', 'income-finance'} <= set(mk), sorted(mk))
    mk = find_markers('Мы не гарантируем результат и не лечим')
    check('отрицание снимает guarantee и health', 'guarantee' not in mk and 'health' not in mk, sorted(mk))
    check('«Самые частые вопросы» — не превосходная степень', 'superlative' not in find_markers('Самые частые вопросы'))
    check('термин свойства «датчик»', any('датчик' in t for t, _ in find_property_terms('Датчик меряет свет в комнате')))
    # --- сопоставление
    facts, schema = _selftest_facts()
    check('схема прочитана: 20 классов', len(facts.class_info) == 20, len(facts.class_info))
    check('классы маркеров ⊆ схемы', set(CLASS_MARKERS) <= set(facts.class_info), set(CLASS_MARKERS) - set(facts.class_info))
    check('«8 900 ₽» подтверждено', errs(rules_of('Цена — 8 900 ₽', facts)) == [], rules_of('Цена — 8 900 ₽', facts))
    check('«7 900 ₽» → COPY-F-NUM-MISMATCH|NUM', set(errs(rules_of('Цена — 7 900 ₽', facts))) & {'COPY-F-NUM', 'COPY-F-NUM-MISMATCH'}, rules_of('Цена — 7 900 ₽', facts))
    check('«Более 1 100 квартир» при 1 146 — ок', errs(rules_of('Более 1 100 квартир сдали', facts)) == [], rules_of('Более 1 100 квартир сдали', facts))
    check('«1 200+ квартир» при 1 146 — ошибка', errs(rules_of('1 200+ квартир сдали', facts)) != [], rules_of('1 200+ квартир', facts))
    check('«10 000 клиентов» при «10 000 заказов» → NUM-MISMATCH', 'COPY-F-NUM-MISMATCH' in errs(rules_of('10 000 клиентов доверяют нам', facts)), rules_of('10 000 клиентов', facts))
    check('диапазон «от 2700 до 5000 K» подтверждён', 'COPY-F-NUM' not in errs(rules_of('Температура от 2700 до 5000 K', facts)), rules_of('Температура от 2700 до 5000 K', facts))
    F = rules_of('Датчик меряет свет в комнате, лампа выставляет температуру от 2700 до 5000 K.', facts)
    check('«Датчик» → COPY-F-PROPERTY', 'COPY-F-PROPERTY' in errs(F), F)
    F = rules_of('Сборка — Казань', facts)
    check('«Сборка — Казань» при F9 из «стартап из Казани» → COPY-F-INFERRED', 'COPY-F-INFERRED' in errs(F), F)
    F = rules_of('Promise: читать вечером без усталости глаз', facts)
    check('обещание про глаза → COPY-F-NEVER', 'COPY-F-NEVER' in errs(F), F)
    F = rules_of('Хотите читать без усталости глаз?', facts)
    check('вопрос-обещание про глаза → всё равно COPY-F-NEVER', 'COPY-F-NEVER' in errs(F), F)
    F = rules_of('Первая партия — 300 ламп', facts)
    check('«Первая партия — 300 ламп» → COPY-F-EXTENDS', 'COPY-F-EXTENDS' in errs(F), F)
    F = rules_of('«Сдали за 47 рабочих дней… Смета не выросла ни на рубль»', facts)
    check('цитата дословно — ок', errs(F) == [], F)
    F = rules_of('«Сдали за 47 рабочих дней. Смета не выросла ни на рубль»', facts)
    check('цитата: новая нарезка без многоточия → RECUT или EDIT', {f['rule'] for f in F} & {'COPY-F-QUOTE-RECUT', 'COPY-F-QUOTE-EDIT'}, F)
    F = rules_of('«Сдали за 30 рабочих дней… Смета не выросла ни на рубль»', facts)
    check('цитата с изменённым числом → ошибка', errs(F) != [], F)
    F = rules_of('«Лучшая студия в городе, всем советую»', facts)
    check('выдуманная цитата → COPY-F-QUOTE', 'COPY-F-QUOTE' in errs(F), F)
    F = rules_of('«Бригада убирала за собой каждый день»', facts)
    check('отзыв без разрешения → COPY-F-PERMISSION', 'COPY-F-PERMISSION' in errs(F), F)
    F = rules_of('Скидка 10 % до 31 октября 2026 года', facts, today=dt.date(2026, 11, 2))
    check('истёкшая акция → COPY-F-EXPIRED', 'COPY-F-EXPIRED' in errs(F), F)
    F = rules_of('Скидка 10 % до 31 октября 2026 года', facts)
    check('действующая акция — ок', errs(F) == [], F)
    F = rules_of('Рейтинг 4,8 из 5 на Яндекс Картах', facts)
    check('рейтинг с фактом — ок', errs(F) == [], F)
    F = rules_of('Рейтинг 4,9 из 5', facts)
    check('рейтинг без факта → COPY-F-RATING', 'COPY-F-RATING' in errs(F), F)
    F = rules_of('Лучшая лампа для чтения', facts)
    check('«лучшая» без факта → COPY-F-CLASS', 'COPY-F-CLASS' in errs(F), F)
    F = rules_of('Самая быстрая доставка в городе по замеру агентства X', facts)
    check('превосходная степень с исследованием и юристом — ок', errs(F) == [], F)
    F = rules_of('Тысячи довольных клиентов', facts)
    check('«тысячи довольных клиентов» → COPY-F-CLASS', 'COPY-F-CLASS' in errs(F), F)
    F = rules_of('Кто производитель? [PLACEHOLDER: юрлицо]', facts)
    check('заглушка из missing → info, без ошибок', errs(F) == [], F)
    F = rules_of('Адрес: [PLACEHOLDER: адрес склада]', facts)
    check('заглушка вне missing → warning', any(f['rule'] == 'COPY-F-PLACEHOLDER-UNLISTED' for f in F), F)
    F, _, _ = check_units([unit('d', 'Цена — 8 900 ₽', fact_ids=['nope'], slot_type='pricing-price')], facts, dt.date(2026, 9, 24))
    check('fact_ids с неизвестным id → COPY-F-REF', 'COPY-F-REF' in errs(F), F)
    F, _, _ = check_units([unit('d', 'Цена — 8 900 ₽', fact_ids=['F1'], slot_type='footer-legal')], facts, dt.date(2026, 9, 24))
    check('алиас F1 принят; слот вне use → COPY-F-USE warning', errs(F) == [] and any(f['rule'] == 'COPY-F-USE' for f in F), F)
    f3 = Facts(dict(facts.data, facts=list(facts.data['facts']) + [{'id': 'clients-approx', 'kind': 'metric', 'claim_class': ['fact-number'],
        'verbatim': ['около 200 клиентов'], 'canonical': 'Около 200 клиентов.', 'values': [{'value': 200, 'unit': 'pcs', 'what': 'клиенты', 'approx': True}],
        'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
        'permission': {'status': 'not-required'}, 'lang': 'ru'}]), schema, True)
    check('приблизительный факт «около 200» → точное «200 клиентов» — ошибка', errs(rules_of('200 клиентов', f3)) != [], rules_of('200 клиентов', f3))
    check('приблизительный факт → «около 200 клиентов» — ок', errs(rules_of('Около 200 клиентов', f3)) == [], rules_of('Около 200 клиентов', f3))
    # --- регрессии, найденные B1 (опыт B1/02, 2026-09-24)
    F = rules_of('−10 % до 31 октября 2026 года', facts)
    check('B1: минус U+2212 в дословном факте — без EXTENDS', not [f for f in F if f['rule'] == 'COPY-F-EXTENDS'], F)
    f2 = Facts(dict(facts.data, never_claim=list(facts.data['never_claim']) + [{'id': 'nc-budget', 'text': 'смета никогда не меняется', 'claim_class': ['guarantee'], 'patterns': ['смет\\w*\\s+не\\s+вырос'], 'lift': 'with-fact'}]), schema, True)
    F = rules_of('«Сдали за 47 рабочих дней… Смета не выросла ни на рубль»', f2)
    check('B1: запрет голоса компании в цитате отзыва с разрешением → warning COPY-F-TYPICALITY, не error',
          not errs(F) and any(f['rule'] == 'COPY-F-TYPICALITY' for f in F), F)
    F = rules_of('Смета не выросла ни на рубль — гарантируем!', f2)
    check('тот же запрет голосом компании → COPY-F-NEVER', 'COPY-F-NEVER' in errs(F), F)
    # --- ложные срабатывания
    bad = []
    for p in FP_PHRASES:
        F = rules_of(p, facts)
        if any(f['level'] in ('error', 'warning') for f in F):
            bad.append((p, [(f['rule'], f['fragment']) for f in F]))
    check(f'{len(FP_PHRASES)} фраз без фактов — ни error, ни warning', not bad, bad)
    # --- входы
    kimi = '# COPY\n\n## hero\n[h1]: Лампа\n[cta]: Забронировать за 990 ₽\n\n## specs\n[row4]: Сборка — Казань\n'
    us = load_kimi_md(kimi)
    check('kimi copy.md: 3 единицы, слоты', [(u['section'], u['slot_type']) for u in us] == [('hero', 'headline'), ('hero', 'cta-label'), ('specs', 'spec-row')], us)
    deck = {'copy_deck': {'version': 0, 'pages': [{'page_id': 'home', 'page_type': 'landing-waitlist', 'sections': [
        {'section_id': 'hero', 'slots': [{'slot_id': 'h1', 'slot_type': 'headline', 'variants': [{'id': 'a', 'text': 'A'}, {'id': 'b', 'text': 'B'}], 'chosen': 'b', 'fact_ids': [], 'claim_flags': []}]}]}]}}
    us, _ = load_deck(deck)
    check('copy deck v0: берётся chosen', [u['text'] for u in us] == ['B'], us)
    us, _ = load_deck(deck, all_variants=True)
    check('copy deck v0: --all-variants', [u['text'] for u in us] == ['A', 'B'], us)
    us = load_html('<html><head><title>Кварц</title><meta name="description" content="Лампа за 8 900 ₽"></head><body><h1>Лампа</h1><p>Цена 8 900 ₽</p><blockquote>Отличная лампа, всем советую</blockquote><script>var x=5</script></body></html>')
    check('HTML: title, description, h1, p, blockquote; без script', [u['slot_type'] for u in us] == ['meta-title', 'meta-description', 'headline', 'body', 'testimonial-quote'], [(u['slot_type'], u['text']) for u in us])
    # --- импорт kimi
    fm = '| ID | Fact, exactly as it may appear | Source (who / where / date) | Where it may be used |\n|---|---|---|---|\n| F9 | сборка в Казани | заказчик, сообщение 2026-09-24 («стартап из Казани») | specs |\n'
    imp = import_kimi('## Facts\n\n' + fm + '\n## Never claim\n- любые обещания про здоровье и зрение;\n', 'x', '2026-09-24')
    check('import-kimi: F9 → quote «стартап из Казани»', imp['facts'][0]['source'].get('quote') == 'стартап из Казани', imp['facts'][0])
    check('import-kimi: never_claim здоровье → patterns', imp['never_claim'][0].get('patterns'), imp['never_claim'])
    # --- внешние правила
    with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False, encoding='utf-8') as t:
        t.write('version: 1\ndate: "2026-10-01"\nrules:\n  - id: COPY-L-TEST-01\n    level: error\n    patterns: ["\\\\bв\\\\s+кредит\\\\b"]\n    requires: {nearby: ["банк\\\\s+\\\\S+"]}\n    message: "кредит без названия банка"\n    fix: "Назовите банк"\n    source: "тест"\n')
    rules, rerr = load_rules([t.name])
    os.unlink(t.name)
    check('внешние правила загружены', len(rules) == 1 and not rerr, rerr)
    F, _, _ = check_units([unit('r', 'Купите в кредит без переплат')], facts, dt.date(2026, 9, 24), rules)
    check('внешнее правило сработало', any(f['rule'] == 'COPY-L-TEST-01' for f in F), F)
    F, _, _ = check_units([unit('r', 'Купите в кредит, банк Альфа')], facts, dt.date(2026, 9, 24), rules)
    check('внешнее правило: оговорка рядом снимает', not any(f['rule'] == 'COPY-L-TEST-01' for f in F), F)
    check('rules-schema — валидный JSON', bool(json.loads(json.dumps(RULES_SCHEMA))))
    _selftest_legal(check)   # правовой модуль H (волна 2)
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


# ================================================================ CLI
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--selftest' in argv:
        return cmd_selftest()
    cmds = {'check', 'inventory', 'lint-facts', 'import-kimi', 'rules-schema'}
    cmd = argv.pop(0) if argv and argv[0] in cmds else 'check'
    p = argparse.ArgumentParser(prog=f'claims_check.py {cmd}', description=__doc__.split('\n')[0])
    if cmd == 'rules-schema':
        return cmd_rules_schema(p.parse_args(argv))
    p.add_argument('input')
    p.add_argument('--json')
    p.add_argument('--md')
    p.add_argument('--quiet', action='store_true')
    p.add_argument('--today')
    p.add_argument('--schema', default=SCHEMA_PATH)
    if cmd in ('check', 'inventory'):
        p.add_argument('--format', default='auto', choices=['auto', 'deck', 'kimi-md', 'md', 'text', 'html'])
    if cmd == 'check':
        p.add_argument('--facts')
        p.add_argument('--rules', nargs='*')
        p.add_argument('--no-external-rules', action='store_true')
        p.add_argument('--no-default-never', action='store_true')
        p.add_argument('--genre')
        p.add_argument('--all-variants', action='store_true')
        p.add_argument('--strict', action='store_true')
        p.add_argument('--verbose', action='store_true')
        p.add_argument('--jurisdiction', choices=list(JURISDICTIONS), help='право: ru (по умолчанию), eu, us, other; иначе — из facts.yaml')
        p.add_argument('--legal-category', help='отрасль через запятую: finance, medical, dietary-supplements, alcohol, education, real-estate, other, general')
        p.add_argument('--legal-only', action='store_true', help='в отчёт — только находки правил H (claims-rules.yaml, --rules)')
    if cmd == 'import-kimi':
        p.add_argument('-o', '--output')
        p.add_argument('--site', default='imported')
        p.add_argument('--date')
    a = p.parse_args(argv)
    try:
        if cmd == 'check':
            return cmd_check(a)
        if cmd == 'inventory':
            return cmd_inventory(a)
        if cmd == 'lint-facts':
            return cmd_lint_facts(a)
        if cmd == 'import-kimi':
            return cmd_import_kimi(a)
    except SystemExit as e:
        if isinstance(e.code, str):
            print('claims_check:', e.code, file=sys.stderr)
            return 1
        raise
    except (OSError, ValueError) as e:
        print('claims_check:', e, file=sys.stderr)
        return 1
    return 1


if __name__ == '__main__':
    sys.exit(main())
