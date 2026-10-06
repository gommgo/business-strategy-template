#!/usr/bin/env python3
"""claims_check.py — сверка текстов сайта с белым списком фактов (facts.yaml): ядро «контура честности» базы text.

Модель не вызывается, сеть не нужна. Python 3.10+, PyYAML. Правовые правила (классы → требования → оговорки) — внешний
файл 08-russian-legal-typography/claims-rules.yaml (подхватывается сам; формат — `rules-schema`): право по юрисдикции
(--jurisdiction ru|eu|us, по умолчанию из facts.yaml или ru) и отрасли (--legal-category, из copy deck legal_category
или general); --legal-only — только находки права; условия снятия: оговорка рядом (unless, nearby, nearby_all), поля
факта, условия факта (qualifier, disclaimer), тип страницы (page_types, page_types_except).

Что делает (спецификация — 02-strategy-messaging/03-proof-and-facts.md §7):
  извлекает из текста числа (единицы, %, валюта, диапазоны, «от/до/более», «+», тыс./млн, «20-летний», разделитель
  тысяч по языку текста и факта), числительные словами («пять лет» — утверждение пишется цифрами: COPY-F-NUM-WORDS),
  даты, годы, рейтинги («4,9 из 5», звёзды; своя шкала бренда — не рейтинг), цитаты в «ёлочках» и "кавычках",
  счётчики, имена и названия (эвристика + сущности facts.yaml, падежи имён), маркеры 20 классов утверждений (лучший,
  № 1, гарантируем, бесплатно, вылечит, доход, «удвоит выручку», сборка, сертификат…) и термины свойств (датчик,
  аккумулятор, материал…); сопоставляет с фактами дословно и по нормализованному значению с единицей и объектом счёта
  (переводы translations.<lang> — со своим объектом счёта и оговоркой); проверяет сам факт: разрешение (и подпись
  отзыва против permission.shows), срок, основание (дословная выдержка источника), вывод вместо факта, проверку юриста
  для рискованных классов, демо-данные (example: true); never_claim (проектный + набор по умолчанию из
  facts.schema.yaml, на языке текста); места use (ориентир: вне их — COPY-F-USE warning, места x-use-always законны
  всегда); [PLACEHOLDER] — info со счётчиком. Вопрос (FAQ, предложение с «?») утверждением не считается. Цифры в
  именах сущностей facts.yaml (entities[].names: модель «Атлас Р 45») — часть имени, числом утверждения не считаются.
  Слово внутри имени продукта или услуги (сущность вида product: «Доставка обедов») — не маркер условий покупки.
  Орган власти (Роскомнадзор, ФНС) вне списка клиентов и подписи отзыва — не имя, которому нужен факт.

Входы (формат определяется сам или --format):
  copy deck (copy_deck.pages[].sections[].slots[] — slot_type, variants[].text, chosen, fact_ids, claim_flags) ·
  copy.md входа холста («## <section_id>» + «[<slot_id>] <status>: текст», синтаксис — copydeck.py) · Markdown ·
  текст · HTML (у статичной копии артборда служебный <title> не читается).
  Вход без слотов (HTML, Markdown, текст) привязывает к copy deck ключ --deck: единица, чей текст — текст слота,
  сверяется как этот слот — с его типом, секцией, страницей и fact_ids; текст, которого в copy deck нет, остаётся без
  привязки. У статичной копии артборда (строка происхождения dc_to_html в <head>) текст без привязки не знает слота и
  его фактов, поэтому находки эвристик сверки — число, дата, рейтинг, цитата, имя, маркер класса, свойство, место
  факта — у него info; право (COPY-L-…), запреты never_claim, «утверждение шире факта» и проблемы самих фактов
  (разрешение, срок, проверка, вывод, проверка юриста) уровня не меняют.

Подкоманды:
  [check] INPUT [--facts facts.yaml] [--format auto|deck|copy-md|md|text|html] [--rules FILE ...] [--no-external-rules]
          [--no-default-never] [--today ГГГГ-ММ-ДД] [--genre landing] [--all-variants] [--strict] [--final] [--verbose]
          [--json OUT] [--md OUT] [--quiet] [--jurisdiction ru|eu|us|other] [--legal-category finance,medical,…]
          [--legal-only] [--deck DECK] [--allow FILE]
          --final — ворота публикации: демо-данные (example: true у файла или факта) — error, без него — info;
          --all-variants — все варианты, кроме отклонённых; соседние варианты слота текстом «рядом» не считаются;
          --deck DECK — copy deck, к слотам которого по тексту привязывается вход без слотов; отрасль и юрисдикция —
          из его шапки;
          --allow FILE — обходы сверки, принятые человеком: JSON с полем allowed (вывод copydeck.py validate --final
          --json, check --json или claims --json) либо список записей {rule, where, reason, by[, value][, fragment]}.
          Находка под обходом — info с причиной и тем, кто решил. rule — COPY-F-CLASS, COPY-F-NUM (число без факта и
          число, не совпавшее с фактом) или COPY-F-NUM-MISMATCH (только несовпавшее число); запись без reason или by,
          с другим правилом или с value не числом не действует. Запись снимает находку, когда совпали место и снятое.
          Место — where записи: слот «страница/секция/слот», мета «страница/meta» (только тексты мета) или страница
          (вход — copy deck или привязка --deck). Снятое — value (число фрагмента находки) и fragment (слово или
          фраза фрагмента находки целиком); без них запись снимает все находки своего правила на своём месте. У
          единицы без привязки — запись с тем же фрагментом (fragment).
          exit 0 — нет error; 1 — есть error; 2 — ошибка вызова, входа или окружения
  lint-facts FACTS [--today …] [--final] — проверка самого инвентаря (вывод без основания, истёкшие, без разрешений,
          id мест use по словарю site, демо-данные); разрешение pending и демо-данные — warning, с --final (ворота
          публикации) — error; exit 0/1/2
  --selftest — офлайн-тесты извлечения, сопоставления, правил, калибровок и ложных срабатываний; exit 0/1

Обслуживание базы (в маршруте этапов проекта не участвует):
  inventory INPUT [--format …] [--json OUT] [--md OUT]  — без фактов: утверждения по классам и видимый ли источник на
          странице (метрика «доля утверждений с видимым источником» для замеров корпуса страниц); exit 0
  rules-schema — JSON Schema формата claims-rules.yaml

Идентификаторы правил — префикс COPY-F-; правила права — COPY-L-.
Правила ux: kb/ux/07-ux-writing/06-banned-words-and-patterns.md §5.2 (регулярки соцдоказательств),
kb/ux/06-feedback-states-motion/04-dark-patterns-and-ethics.md §8.1 п.10–12, 22.
Это не юридическое заключение: классы и флаги показывают, где нужна проверка права (юрист заказчика).
"""
import argparse, copy, datetime as dt, difflib, fnmatch, html.parser, json, os, re, sys, tempfile, unicodedata

VERSION = '1.0'
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb('text'))
SCHEMA_PATH = os.path.join(ROOT, '02-strategy-messaging', 'facts.schema.yaml')
RULES_PATH = os.path.join(ROOT, '08-russian-legal-typography', 'claims-rules.yaml')
VOCAB_PATH = str(kbpaths.kb('site', '02-site-types', 'vocabulary.yaml'))   # словарь id системы (site v1)

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

LEVELS = ('error', 'warning', 'info')

# ================================================================ нормализация текста
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
    # прилагательное через дефис: «20-летний опыт», «14-дневный возврат», «24-часовая поддержка», «5-кратный рост»
    (r'[-‑–]\s?лет(?:н|и)[а-я]*', 'years'), (r'[-‑–]\s?дневн[а-я]*', 'days'), (r'[-‑–]\s?недельн[а-я]*', 'weeks'),
    (r'[-‑–]\s?месячн[а-я]*', 'months'), (r'[-‑–]\s?часов[а-я]*', 'hours'), (r'[-‑–]\s?минутн[а-я]*', 'minutes'),
    (r'[-‑–]\s?процентн[а-я]*', '%'), (r'[-‑–]\s?кратн[а-я]*', 'times'),
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
# английский текст и факт: запятая перед тремя цифрами — разделитель тысяч («₽9,800», «1,380», «1,234,567»), дробь — точкой
NUM_RX_EN = re.compile(r'(?<![\w.,/:-])(\d{1,3}(?:,\d{3})+|\d{1,3}(?:[ \u00a0\u202f\u2009]\d{3})+|\d+)(?:\.(\d+))?(?![\w])', re.U)
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
    core = re.sub(r'[ \u00a0\u202f\u2009,]', '', intpart)
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


def extract_numbers(text, lang=None, skip=()):
    """Числа текста: [{raw, start, end, value | range, unit, noun[], cmp, kind}] без дат, телефонов, ссылок на законы,
    копирайта, времени и рейтингов (они извлекаются отдельно). lang — язык текста или факта: у «en» запятая перед тремя
    цифрами — разделитель тысяч при любой валюте; без языка — эвристика по латинице рядом. skip — места текста
    [(начало, конец)], где цифры числом не считаются (имена сущностей с цифрой — Facts.name_spans)."""
    s = text
    mask = [False] * len(s)

    def cover(m):
        for i in range(m.start(), m.end()):
            mask[i] = True
    for a, b in skip or ():
        for i in range(max(0, a), min(len(s), b)):
            mask[i] = True
    for rx in (URL_RX, EMAIL_RX, PHONE_RX, LAWREF_RX, COPYRIGHT_RX, TIME_RX, DATE_DMY, DATE_ISO, RATING_RX, PLACEHOLDER_RX):
        for m in rx.finditer(s):
            cover(m)
    for m in DATE_TEXT.finditer(s):
        if m.group(1) or m.group(3):
            cover(m)
    out = []
    ms = [m for m in (NUM_RX_EN if lang == 'en' else NUM_RX).finditer(s) if not mask[m.start()]]
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
        # «1,250» по-английски: тысячи через запятую (язык не задан — по латинице рядом)
        if lang is None and m.group(2) and len(m.group(2)) == 3 and ',' in s[m.start():m.end()] and 'value' in item and item['unit'] in ('USD', 'EUR', None) and re.search(r'[a-z]', low[max(0, raw_start - 30):raw_start + 30]):
            item['value'] = float(re.sub(r'[^\d]', '', s[m.start():m.end()]))
        item['noun'] = next_noun(s, end)
        item['raw'] = s[raw_start:end].strip()
        item['end'] = end
        out.append(item)
        i += 1
    return out


# числительные словами: в утверждении сайта число пишется цифрами; сверка разбирает и слова, чтобы утверждение
# «пять лет гарантии» не прошло мимо фактов, и ставит COPY-F-NUM-WORDS
RU_NUM_WORDS = [  # (регулярка основы с окончаниями, значение, вид: u — единицы и десятки, h — сотни, m — множитель)
    (r'одн?(?:ин|на|но|ого|ой|ому|им|ом|у)', 1, 'u'), (r'дв(?:а|е|ух|ум|умя)', 2, 'u'), (r'тр(?:и|[её]х|[её]м|емя)', 3, 'u'),
    (r'четыр(?:е|[её]х|[её]м|ьмя)', 4, 'u'), (r'пят(?:ь|и|ью)', 5, 'u'), (r'шест(?:ь|и|ью)', 6, 'u'), (r'сем(?:ь|и|ью)', 7, 'u'),
    (r'вос(?:емь|ьми|емью|ьмью)', 8, 'u'), (r'девят(?:ь|и|ью)', 9, 'u'), (r'десят(?:ь|и|ью)', 10, 'u'),
    (r'одиннадцат(?:ь|и|ью)', 11, 'u'), (r'двенадцат(?:ь|и|ью)', 12, 'u'), (r'тринадцат(?:ь|и|ью)', 13, 'u'),
    (r'четырнадцат(?:ь|и|ью)', 14, 'u'), (r'пятнадцат(?:ь|и|ью)', 15, 'u'), (r'шестнадцат(?:ь|и|ью)', 16, 'u'),
    (r'семнадцат(?:ь|и|ью)', 17, 'u'), (r'восемнадцат(?:ь|и|ью)', 18, 'u'), (r'девятнадцат(?:ь|и|ью)', 19, 'u'),
    (r'двадцат(?:ь|и|ью)', 20, 'u'), (r'тридцат(?:ь|и|ью)', 30, 'u'), (r'сорок(?:а)?', 40, 'u'),
    (r'пят(?:ьдесят|идесяти)', 50, 'u'), (r'шест(?:ьдесят|идесяти)', 60, 'u'), (r'сем(?:ьдесят|идесяти)', 70, 'u'),
    (r'вос(?:емьдесят|ьмидесяти)', 80, 'u'), (r'девяност(?:о|а)', 90, 'u'),
    (r'ст(?:о|а)', 100, 'h'), (r'дв(?:ести|ухсот)', 200, 'h'), (r'тр(?:иста|[её]хсот)', 300, 'h'),
    (r'четыр(?:еста|[её]хсот)', 400, 'h'), (r'пят(?:ьсот|исот)', 500, 'h'), (r'шест(?:ьсот|исот)', 600, 'h'),
    (r'сем(?:ьсот|исот)', 700, 'h'), (r'вос(?:емьсот|ьмисот)', 800, 'h'), (r'девят(?:ьсот|исот)', 900, 'h'),
    (r'полтор(?:а|ы|ух)', 1.5, 'u'),
    (r'тысяч(?:а|и|у|ей|ами|ах)?', 1e3, 'm'), (r'миллион(?:а|ов|ам|ами|ах)?', 1e6, 'm'), (r'миллиард(?:а|ов|ам|ами|ах)?', 1e9, 'm')]
EN_NUM_WORDS = [
    (r'one', 1, 'u'), (r'two', 2, 'u'), (r'three', 3, 'u'), (r'four', 4, 'u'), (r'five', 5, 'u'), (r'six', 6, 'u'),
    (r'seven', 7, 'u'), (r'eight', 8, 'u'), (r'nine', 9, 'u'), (r'ten', 10, 'u'), (r'eleven', 11, 'u'), (r'twelve', 12, 'u'),
    (r'thirteen', 13, 'u'), (r'fourteen', 14, 'u'), (r'fifteen', 15, 'u'), (r'sixteen', 16, 'u'), (r'seventeen', 17, 'u'),
    (r'eighteen', 18, 'u'), (r'nineteen', 19, 'u'), (r'twenty', 20, 'u'), (r'thirty', 30, 'u'), (r'forty', 40, 'u'),
    (r'fifty', 50, 'u'), (r'sixty', 60, 'u'), (r'seventy', 70, 'u'), (r'eighty', 80, 'u'), (r'ninety', 90, 'u'),
    (r'hundred', 100, 'x'), (r'thousand', 1e3, 'm'), (r'million', 1e6, 'm'), (r'billion', 1e9, 'm')]
_NUM_WORD_RX = {lg: [(re.compile(r'(?<![а-яёa-z0-9-])' + rx + r'(?![а-яёa-z0-9-])', re.I), v, k) for rx, v, k in tbl]
                for lg, tbl in (('ru', RU_NUM_WORDS), ('en', EN_NUM_WORDS))}


def extract_word_numbers(text, lang=None):
    """Числительные словами: [{raw, start, end, value, unit, noun[], cmp, kind: 'number', words: True}] — «пять лет»,
    «двадцать пять клиентов», «полторы тысячи», «five years». «Один» и «one» — только с единицей («один день»): иначе это
    не счёт («всё в одном месте», «one of»); «одна из», «ни одного» — не число."""
    s = soft(text)
    lang = lang or unit_lang(text) or 'ru'
    hits = []
    for rx, v, k in _NUM_WORD_RX.get(lang, []):
        for m in rx.finditer(s):
            hits.append((m.start(), m.end(), v, k))
    hits.sort()
    out, i = [], 0
    while i < len(hits):
        st, en, v, k = hits[i]
        group = [(st, en, v, k)]
        j = i + 1
        while j < len(hits) and re.fullmatch(r'\s+(?:и\s+|and\s+)?|-', s[group[-1][1]:hits[j][0]]):
            group.append(hits[j])
            j += 1
        total, cur = 0.0, 0.0
        for _st, _en, gv, gk in group:
            if gk == 'm':
                total += (cur or 1) * gv
                cur = 0.0
            elif gk == 'x':
                cur = (cur or 1) * gv
            else:
                cur += gv
        value = total + cur
        start, end = group[0][0], group[-1][1]
        i = j
        pre = s[max(0, start - 4):start]
        if re.search(r'(?:^|\s)ни\s$', pre) or re.match(r'\s+(?:из|of)\b', s[end:end + 5]):
            continue
        u, end2 = unit_at(s, end)
        if u and re.match(r'[а-яёa-z]', s[end2:end2 + 1]):
            u, end2 = None, end   # «в одном месте» — не «мес.»: единица словом целиком
        if value == 1 and not u:
            continue
        item = {'start': start, 'value': value, 'cmp': 'eq', 'unit': u, 'noun': [], 'kind': 'number', 'words': True}
        for rx_, c in PREFIX_CMP_RX:
            if rx_.search(s[max(0, start - 22):start]):
                item['cmp'] = c
                break
        end = end2 if u else end
        item['noun'] = next_noun(s, end)
        item['raw'] = text[start:end].strip() if len(text) == len(s) else s[start:end].strip()
        item['end'] = end
        out.append(item)
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


OWN_SCALE_RX = re.compile(r'(?:остр|жгуч|сложн|уров|интенсивн|крепост|сладост|кислотн|плотност|ж[её]сткост|мягкост|спелост|'
                          r'spic|heat|level|difficulty|intensity|strength|sweetness|firmness)\w*[^.!?;\n]{0,25}$', re.I)


def extract_ratings(text):
    """Рейтинги: «4,9 из 5», «4.8/5», звёзды. Своя шкала бренда («острота 5 из 5», «уровень 3 из 5») — свойство продукта,
    а не рейтинг площадки: пропускается."""
    out = []
    for m in RATING_RX.finditer(text):
        if OWN_SCALE_RX.search(soft(text[max(0, m.start() - 40):m.start()])):
            continue
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
        r'\b(?:fastest|cheapest|easiest|safest|biggest|largest|smartest|strongest|lowest|highest|hottest|finest|greatest|freshest|tastiest|healthiest|quickest)\b',
        r"\b[a-z]+est\s+(?:[a-z]+\s+){1,2}you(?:'ll|\s+will|'ve|\s+have)\s+ever\b"),
    'comparison': R(
        B + r'(?:быстрее|дешевле|дороже|выгоднее|надежнее|надёжнее|точнее|мощнее|эффективнее|долговечнее|экономичнее|прочнее|тише|легче|лучше)\s*,?\s*(?:чем|в\s+\d|на\s+\d|аналог\w*|конкурент\w*|других|обычн\w*|традиционн\w*|у\s+(?:других|конкурент))',
        B + r'в\s+\d+(?:[.,]\d+)?\s+раз(?:а)?' + E, B + r'в\s+(?:два|три|четыре|пять|десять|несколько)\s+раз(?:а)?' + E,
        B + r'на\s+\d+(?:[.,]\d+)?\s?%\s+(?:быстрее|дешевле|больше|меньше|выше|ниже|эффективнее|дольше|точнее)',
        B + r'по\s+сравнению\s+с' + E, B + r'в\s+отличие\s+от' + E, B + r'(?:больше|меньше|выше|ниже)\s*,?\s*чем\s+(?:у|в)\s',
        r'\b(?:faster|cheaper|better|easier|safer|stronger|lighter|quieter|more\s+\w+|less\s+\w+)\s+than\b',
        r'\b\d+(?:\.\d+)?x\s+(?:faster|more|better|cheaper|higher|less)\b', r'\bcompared\s+(?:to|with)\b', r'\bunlike\s+(?:other|competitor)', r'\bvs\.?\s'),
    'guarantee': R(
        B + r'гарант(?:ия|ии|ию|ией|ируем|ирует|ируют|ированн\w*|ийн\w*)', B + r'верн[её]м\s+деньги', B + r'возврат\w*\s+(?:денег|средств|оплаты)',
        B + r'деньги\s+назад', B + r'без\s+риска' + E, B + r'или\s+верн[её]м', B + r'без\s+исключени[йя]' + E,
        r'\bguarante\w*', r'\bmoney[- ]back\b', r'\brisk[- ]free\b', r'\bwarranty\b', r'\bor\s+your\s+money\s+back\b'),
    'health': R(
        B + r'(?:леч(?:ит|ат|ение|ебн\w*|ить)|вылеч\w*|исцел\w*|оздоров\w*|профилакти\w*|иммунитет\w*|похуд\w*|сжига\w*\s+жир|детокс\w*|омолаж\w*)',
        B + r'(?:здоров(?:ье|ья|ью|ый|ая|ое|ые|ого|ую)|самочувстви\w*|зрени(?:е|я|ю|ем)|бессонниц\w*|усталост\w*|утомлени\w*\s+глаз|утомля\w*)' + E,
        B + r'(?<!на\s)глаз(?:а|ам|ами|ах|у)?' + E, B + r'безопасн\w*\s+для\s+(?:здоровья|детей|кожи|глаз)', B + r'гипоаллерген\w*',
        B + r'(?:клинически|научно)\s+доказ\w*', B + r'врач\w*\s+рекоменд\w*', B + r'рекомендова\w*\s+врач\w*',
        r'\b(?:cures?|heals?|treat(?:s|ment)?|prevents?\s+(?:disease|illness)|immun\w+|weight\s+loss|lose\s+weight|detox|anti-?aging|eye\s*strain|eyesight|clinically\s+proven|doctor[- ]recommended|hypoallergenic|sleep\s+better)\b'),
    'income-finance': R(
        B + r'(?:доход\w*|прибыл[а-я]*|дивиденд\w*|пассивн\w*\s+доход\w*|инвестиц\w*|кэшб[эе]к\w*|кешб[эе]к\w*)' + E,
        # кредит, ипотека, заём — предложение денег (ставка, условие, одобрение), а не ситуация клиента («аренда и ипотека»)
        B + r'в\s+(?:кредит|ипотеку|заём|займ)' + E, B + r'(?:кредит\w*|ипотек\w*|за[йё]м\w*)\s+(?:от|под|без|до)\s+(?:\d|перепл|процент|первоначальн|залог|справ)',
        B + r'(?:одобр\w*|оформ\w*|выда\w*|предлага\w*)\s+(?:[а-яё]+\s+)?(?:кредит\w*|ипотек\w*|за[йё]м\w*)',
        B + r'(?:кредит\w*|ипотек\w*|за[йё]м\w*)\s+(?:за|через)\s+\d',
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
        B + r'(?:удво|утро|учетвер|приумнож|повыс|нараст)\w*?(?:ит|ят|ите|ишь)\s+(?:ваш\w*\s+|свою\s+|свой\s+)?(?:продаж\w*|выручк\w*|прибыл\w*|конверси\w*|доход\w*|трафик\w*|заявк\w*|оборот\w*)',
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

PLATFORM_WORDS = {'rustore', 'appgallery', 'app store', 'appstore', 'google play', 'telegram', 'телеграм', 'whatsapp', 'viber',
                  'vk', 'вконтакте', 'youtube', 'rutube', 'dzen', 'дзен', 'max', 'android', 'ios', 'ipados', 'macos', 'windows',
                  'linux', 'яндекс', 'yandex', 'google', 'apple', 'сбп', 'мир', 'visa', 'mastercard', 'госуслуги'}
TECH_WORDS = {'usb', 'usb-c', 'type-c', 'led', 'hdmi', 'wi-fi', 'wifi', 'gps', 'nfc', 'ip', 'seo', 'crm', 'api', 'ai', 'ии',
              'sms', 'pdf', 'faq', 'cta', 'hr', 'it', 'b2b', 'b2c', 'saas', 'erp', 'ux', 'ui', 'ok', 'ооо', 'ип', 'ао',
              'пао', 'рф', 'сми', 'ндс', 'фз', 'гост', 'iso', 'сро', 'инн', 'огрн', 'кпп', 'бик', 'q', 'a', 'k', 'w', 'kw'}
NAME_OK = {'вы', 'вас', 'вам', 'ваш', 'ваша', 'ваше', 'ваши', 'вами', 'мы', 'я', 'monday', 'tuesday', 'wednesday',
           'thursday', 'friday', 'saturday', 'sunday', 'i', 'we', 'you', 'our', 'the', 'a',
           # частые служебные и местоименные слова, которые встают с заглавной после знаков и в подписях
           'все', 'всё', 'это', 'как', 'что', 'наш', 'наша', 'наши', 'для', 'при', 'без', 'или', 'если', 'когда', 'где',
           'почему', 'зачем', 'только', 'уже', 'еще', 'ещё', 'сейчас', 'здесь', 'там', 'да', 'нет', 'не', 'и', 'а', 'но',
           'права', 'защищены', 'политика', 'конфиденциальности', 'согласие', 'оферта', 'главная', 'контакты', 'меню'}
# органы власти: имя ведомства в тексте (политика, документы, порядок жалобы) — не клиент и не человек, факт ему не нужен;
# в списке клиентов и в подписи отзыва имя ведомства сверяется как любое другое
PUBLIC_BODIES = ('роскомнадзор', 'роспотребнадзор', 'росздравнадзор', 'росреестр', 'росстандарт', 'росаккредитация', 'фас', 'фнс',
                 'мвд', 'гибдд', 'мчс', 'минздрав', 'минцифры', 'минюст')
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


def in_question(text, pos):
    """Позиция внутри предложения-вопроса («Сколько стоит замер? Бесплатно…»): вопрос FAQ — не утверждение."""
    for a, b in sentence_spans(text):
        if a <= pos < b:
            return text[a:b].rstrip().endswith('?')
    return False


# ================================================================ имена
NAME_RX = re.compile(r'(?<![\w@./-])((?:[A-Z][a-z]*[A-Z]\w*|[A-ZА-ЯЁ][a-zа-яё]+|[A-ZА-ЯЁ]{2,}[a-zа-яё]*)(?:[ -](?:[A-ZА-ЯЁ][a-zа-яё]+|[A-ZА-ЯЁ]{2,}))*)')


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
        if low in NAME_OK or low in TECH_WORDS or low in PLATFORM_WORDS or first.lower() in NAME_OK:
            continue   # площадки и магазины приложений («RuStore», «Google Play») — место, а не клиент
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
QUOTE_SLOTS = {'testimonial-quote'}
ATTRIB_SLOTS = {'testimonial-attribution', 'logos-caption', 'case-title', 'case-summary', 'case-result'}
QUESTION_SLOTS = {'faq-q'}


def unit(uid, text, **loc):
    return {'id': uid, 'text': text, 'page': loc.get('page'), 'page_type': loc.get('page_type'), 'alt': False,
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
            role = s.get('section_role') or s.get('role') or role_guess(sid)
            for sl in s.get('slots', []) or []:
                variants = sl.get('variants') or []
                chosen = sl.get('chosen')
                main = next((v for v in variants if v.get('id') == chosen), None) or (variants[0] if variants else None)
                pick = variants if all_variants else ([main] if main else [])
                for v in pick:
                    if v.get('status') == 'rejected' and v is not main:
                        continue   # отклонённый вариант — история правки, не текст страницы
                    txt = v.get('text') or ''
                    if not str(txt).strip():
                        continue
                    lint = sl.get('lint') or {}
                    uu = unit(f"{pid}/{sid}/{sl.get('slot_id')}/{v.get('id')}", str(txt), page=pid, page_type=ptype,
                              section=sid, section_role=role, slot=sl.get('slot_id'), slot_type=sl.get('slot_type'),
                              variant=v.get('id'), fact_ids=v.get('fact_ids') if isinstance(v.get('fact_ids'), list) else sl.get('fact_ids'),
                              claim_flags=sl.get('claim_flags'), genre=lint.get('profile') or genre_default, block=s.get('block'))
                    uu['alt'] = v is not main   # невыбранный вариант: сверяется, но текстом «рядом» для соседей не считается
                    units.append(uu)
    return units, {'site': deck.get('site'), 'lang': deck.get('lang'), 'facts_ref': deck.get('facts_ref'),
                   'jurisdiction': deck.get('jurisdiction'), 'legal_category': deck.get('legal_category')}


_VOCAB = {}


def site_vocab():
    """Словарь id системы — site vocabulary.yaml v1: {'page_types': {id: запись}, 'section_roles': {…}, 'slots': {…},
    'text_slots': {id}, 'status': {id: статус}}; нет файла или PyYAML — пустые словари."""
    if 'v' not in _VOCAB:
        v = {}
        if yaml is not None and os.path.exists(VOCAB_PATH):
            with open(VOCAB_PATH, encoding='utf-8') as fh:
                v = (yaml.safe_load(fh) or {}).get('namespaces') or {}
        vals = lambda ns: {str(x['id']): x for x in (v.get(ns) or {}).get('values') or [] if isinstance(x, dict) and x.get('id')}
        out = {'page_types': vals('page_type'), 'section_roles': vals('section_role'), 'slots': vals('slot'), 'blocks': vals('block')}
        out['text_slots'] = {k for k, x in out['slots'].items() if x.get('kind') == 'text'}
        _VOCAB['v'] = out
    return _VOCAB['v']


def _id_guess(ident, pool):
    """id плана → id словаря: как есть, без номера экземпляра («case-studies-2», «step-1-title»), по префиксу («testimonials-reviews»)."""
    if not ident or not pool:
        return None
    cands = [ident, re.sub(r'-\d+$', '', ident), re.sub(r'-\d+(?=-|$)', '', ident)]
    parts = ident.split('-')
    cands += ['-'.join(parts[:k]) for k in range(len(parts) - 1, 0, -1)]
    return next((c for c in cands if c in pool), None)


def role_guess(section_id):
    return _id_guess(str(section_id or ''), site_vocab()['section_roles'])


def slot_guess(slot_id):
    return _id_guess(str(slot_id or ''), site_vocab()['text_slots'])


def load_copy_md(text):
    """copy.md входа холста (синтаксис — copydeck.py: «## <section_id>», «[<slot_id>] <status>: текст») → единицы;
    роль секции и тип слота угадываются по id плана и словарю site; тексты без секции или слота плана — «?»."""
    kbpaths.use('text')
    import copydeck  # noqa: E402 — владелец формата copy.md
    sections, _notes = copydeck.parse_copy_md(text)
    units = []
    for sec in sections:
        sid = sec.get('section_id')
        for sl in sec.get('slots') or []:
            slid = sl.get('slot_id')
            units.append(unit(f"{sid or '?'}/{slid or '?'}", sl.get('text') or '', section=sid or '?', section_role=role_guess(sid),
                              slot=slid, slot_type=slot_guess(slid), line=sl.get('line')))
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

    def __init__(self, skip_title=False):
        super().__init__(convert_charrefs=True)
        self.units, self.stack, self.buf, self.skip, self.section = [], [], [], 0, None
        self.n = 0
        if skip_title:
            self.SKIP = self.SKIP | {'title'}

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


CANVAS_COPY_RX = re.compile(r'<!--\s*dc_to_html:')   # строка происхождения статичной копии артборда в <head>


def is_canvas_copy(text):
    """HTML — статичная копия артборда: строка происхождения dc_to_html в <head>."""
    end = re.search(r'</head\s*>', text, re.I)
    return bool(CANVAS_COPY_RX.search(text[:end.start()] if end else text[:4000]))


def load_html(text):
    """HTML → единицы текста. У статичной копии артборда <title> — служебное имя артборда («Главная · 1440»), а не
    заголовок страницы: он не читается, иначе ширина и номер из имени сверяются как числа утверждения."""
    p = _HTMLUnits(skip_title=is_canvas_copy(text))
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
    if re.search(r'^\[(?:\?|[\w\-]+)[^\]\n]*\](?:\s+[a-z-]+)?:\s', text, re.M) and re.search(r'^##\s+\S+', text, re.M):
        return 'copy-md'
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
            raise SystemExit('нужен PyYAML: Python окружения скилла ($DDD_HOME/venv, scripts/install.sh)')
        data = deep_dates(yaml.safe_load(text) if not path.lower().endswith('.json') else json.loads(text))
        units, meta = load_deck(data, all_variants)
    elif fmt == 'copy-md':
        units = load_copy_md(text)
    elif fmt == 'md':
        units = load_md(text)
    elif fmt == 'html':
        units = load_html(text)
        meta['canvas_copy'] = is_canvas_copy(text)
    else:
        units = load_text(text)
    return units, fmt, meta


def _flat(s):
    """Текст для привязки к слоту: вид пробелов, тире и кавычек приведён, регистр сохранён."""
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', (s or '').translate(_HARD)).replace('…', '...')).strip()


def bind_units(units, deck_units):
    """Привязка единиц входа без слотов к слотам copy deck по тексту. Единица с текстом слота (без регистра, вида
    пробелов, тире и кавычек) получает его страницу, секцию, слот, тип и fact_ids; единица, в которой тексты
    нескольких слотов стоят подряд (строка без блочных тегов), делится на привязанные части и остаток без привязки.
    Текст, которого в copy deck нет, остаётся как был. → (единицы, число привязанных)."""
    by_text = {}
    for d in deck_units:
        k = _flat(d['text']).lower()
        if k and not d.get('alt'):
            by_text.setdefault(k, d)
    parts_rx = [(re.compile(r'(?<!\w)' + re.escape(k) + r'(?!\w)'), d) for k, d in sorted(by_text.items(), key=lambda x: -len(x[0]))]

    def bound(u, d, text, uid):
        return dict(d, id=uid, text=text, line=u.get('line'), alt=False, bound=True)

    out, n = [], 0
    for u in units:
        t = _flat(u['text'])
        low = t.lower()
        d = by_text.get(low)
        if d is not None:
            out.append(bound(u, d, u['text'], u['id']))
            n += 1
            continue
        hits = []
        if len(low) == len(t):   # позиции в тексте без регистра те же, что в исходном
            taken = [False] * len(t)
            for rx, d in parts_rx:
                m = rx.search(low)
                while m and any(taken[m.start():m.end()]):
                    m = rx.search(low, m.end())
                if m:
                    hits.append((m.start(), m.end(), d))
                    taken[m.start():m.end()] = [True] * (m.end() - m.start())
        if not hits:
            out.append(u)
            continue
        for i, (a, b, d) in enumerate(sorted(hits, key=lambda x: x[0]), 1):
            out.append(bound(u, d, t[a:b], f"{u['id']}.{i}"))
            n += 1
        rest = re.sub(r'\s+', ' ', ''.join(' ' if taken[i] else ch for i, ch in enumerate(t))).strip()
        if re.search(r'\w', rest):
            out.append(dict(u, id=f"{u['id']}.0", text=rest))
    return out, n


# Обход эвристик сверки — как claims_allow слота, мета и страницы copy deck. rule записи — семейство или id находки:
# COPY-F-CLASS — маркер класса без факта; COPY-F-NUM — число без факта и число, не совпавшее с фактом;
# COPY-F-NUM-MISMATCH — только несовпавшее число. Право (COPY-L-…), never_claim, «утверждение шире факта» и остальная
# сверка не обходятся.
ALLOW_FAMILIES = {'COPY-F-CLASS': ('COPY-F-CLASS',), 'COPY-F-NUM': ('COPY-F-NUM', 'COPY-F-NUM-MISMATCH'),
                  'COPY-F-NUM-MISMATCH': ('COPY-F-NUM-MISMATCH',)}
ALLOW_SCOPES = ('slot', 'meta', 'page')
ALLOW_NUMBER_RX = re.compile(r'\d+(?:[.,]\d+)?')


def allow_number(s):
    """Число записи обхода и фрагмента находки одним видом: «7 900» = «7900», «4,9» = «4.9», «12.0» = «12»; не число —
    None."""
    t = re.sub(r'(?<=\d)\s(?=\d)', '', str(s).strip()).replace(',', '.')
    if not re.fullmatch(r'\d+(?:\.\d+)?', t):
        return None
    return t.rstrip('0').rstrip('.') if '.' in t else t


def fragment_numbers(fragment):
    """Числа фрагмента находки (разряды через пробел — одно число) видом allow_number."""
    t = re.sub(r'(?<=\d)\s(?=\d{3}(?!\d))', '', str(fragment or ''))
    return {allow_number(x) for x in ALLOW_NUMBER_RX.findall(t)}


def allow_scope(where):
    """Место записи обхода по её where: slot — «страница/секция/слот» (у текста мета — «страница/meta/поле»), meta —
    «страница/meta» (все тексты мета страницы), page — «страница»; другое — None."""
    parts = str(where or '').split('/')
    if not all(parts):
        return None
    if len(parts) == 3:
        return 'slot'
    if len(parts) == 2:
        return 'meta' if parts[1] == 'meta' else None
    return 'page' if len(parts) == 1 else None


def load_allow(path):
    """Обходы сверки из JSON: поле allowed вывода copydeck.py (validate --final, check, claims) или список записей
    {rule, where, reason, by[, scope][, value][, fragment]}. → (действующие записи, заметки о недействующих). Действует
    запись с правилом из ALLOW_FAMILIES, причиной (reason) и тем, кто решил (by); value — число и только у обхода
    числа. Место записи — её where: слот, мета или страница; scope записи (где решение записано в copy deck) места не
    меняет, без него scope — по виду where."""
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    raw = data.get('allowed') if isinstance(data, dict) else data
    if not isinstance(raw, list):
        raise SystemExit(f'{path}: нет списка обходов (поле allowed или список записей)')
    ok, notes = [], []
    for e in raw:
        e = e if isinstance(e, dict) else {'rule': e}
        rule, where, reason, by = (str(e.get(k) or '').strip() for k in ('rule', 'where', 'reason', 'by'))
        value = '' if e.get('value') in (None, '') or isinstance(e.get('value'), bool) else str(e['value']).strip()
        if rule not in ALLOW_FAMILIES:
            notes.append(f"обход «{rule or '—'}» ({where or '—'}) не действует: обходятся только {', '.join(ALLOW_FAMILIES)}")
        elif not reason or not by:
            notes.append(f"обход {rule} ({where or '—'}) не действует: нет reason или by")
        elif value and (rule == 'COPY-F-CLASS' or allow_number(value) is None):
            notes.append(f"обход {rule} ({where or '—'}) не действует: value «{value}» — число и только у обхода числа; "
                         'слово или фразу называет fragment')
        else:
            rec = {'rule': rule, 'where': where, 'scope': e.get('scope') if e.get('scope') in ALLOW_SCOPES else allow_scope(where),
                   'reason': reason, 'by': by, 'value': allow_number(value) if value else '',
                   'fragment': norm(str(e.get('fragment') or ''))}
            if rec not in ok:
                ok.append(rec)
    return ok, notes


def unit_place(u):
    """Место единицы в copy deck: «страница/секция/слот» или None — у единицы без слота."""
    return '/'.join(str(u[k]) for k in ('page', 'section', 'slot')) if all(u.get(k) for k in ('page', 'section', 'slot')) else None


def unit_places(u):
    """Места обхода единицы со слотом — от ближнего к дальнему: слот, мета страницы (у текста мета), страница; у единицы
    без слота — пусто."""
    place = unit_place(u)
    if not place:
        return []
    page = str(u['page'])
    return [place] + ([f'{page}/meta'] if str(u.get('section')) == 'meta' else []) + [page]


def allow_names(e, fragment):
    """Называет ли запись обхода эту находку: value — число фрагмента находки, fragment — слово или фраза фрагмента
    целиком (без регистра, «ё» = «е»). Запись без value и fragment подходит любой находке своего правила."""
    if e['value'] and e['value'] not in fragment_numbers(fragment):
        return False
    if e['fragment'] and not re.search(r'(?<![0-9a-zа-я])' + re.escape(e['fragment']) + r'(?![0-9a-zа-я])', norm(str(fragment))):
        return False
    return True


def apply_allow(F, units, entries):
    """Находка под обходом → info с причиной и тем, кто решил. Запись снимает находку, когда совпали место и снятое:
    место — слот единицы, мета её страницы (у текста мета) или страница; снятое — правило записи (семейство или id
    находки) и, если запись их называет, число value и фрагмент fragment. Из подходящих записей берётся ближняя: слот,
    мета, страница. У единицы без слота места нет — запись с тем же фрагментом. → (число обойдённых находок, число
    записей, которым не нашлось места: слот, мета или страница без единиц со слотами во входе)."""
    by_id = {u['id']: u for u in units}
    places = {p for u in units for p in unit_places(u)}
    n = 0
    for f in F:
        spots, frag = unit_places(by_id.get(f['unit']) or {}), str(f['fragment'])
        fits = [e for e in entries if f['rule'] in ALLOW_FAMILIES[e['rule']] and allow_names(e, frag)]
        if spots:
            e = next((e for spot in spots for e in fits if e['where'] == spot), None)
        else:
            e = next((e for e in fits if e['fragment'] and e['fragment'] == norm(frag)), None)
        if e is None:
            continue
        if f['level'] != 'info':
            f['level_was'], f['level'] = f['level'], 'info'
        f['allowed'] = {k: e[k] for k in ('rule', 'where', 'reason', 'by', 'scope') if k != 'scope' or e[k]}
        f['message'] += f" — обход claims_allow: {e['reason']} ({e['by']})"
        n += 1
    return n, sum(1 for e in entries if e['where'] not in places and not e['fragment'])


# Эвристики сверки, которым нужен слот и его факты: у текста статичной копии артборда без привязки к copy deck они —
# info. Право, never_claim, «утверждение шире факта» и проблемы самих фактов в список не входят.
UNBOUND_SOFT = {'COPY-F-NUM', 'COPY-F-NUM-MISMATCH', 'COPY-F-NUM-WORDS', 'COPY-F-DATE', 'COPY-F-RATING', 'COPY-F-QUOTE',
                'COPY-F-QUOTE-EDIT', 'COPY-F-QUOTE-RECUT', 'COPY-F-NAME', 'COPY-F-CLASS', 'COPY-F-PROPERTY', 'COPY-F-USE',
                'COPY-F-NEARBY', 'COPY-F-UNSUPPORTED', 'COPY-F-PLACEHOLDER-UNLISTED'}


def soften_unbound(F, units):
    """Статичная копия артборда: находки эвристик у единиц без привязки к слоту copy deck → info. → число смягчённых."""
    bound = {u['id'] for u in units if u.get('bound')}
    n = 0
    for f in F:
        if f['unit'] in bound or f['rule'] not in UNBOUND_SOFT or f['level'] == 'info':
            continue
        f['level_was'], f['level'] = f['level'], 'info'
        f['message'] += ' — копия артборда: текст не привязан к слоту copy deck (сверка по слотам — ключ --deck)'
        n += 1
    return n


# ================================================================ факты
def fact_texts(f):
    parts = list(f.get('verbatim') or []) + [f.get('canonical') or '']
    for v in f.get('values') or []:
        parts += [str(v.get('what') or ''), str(v.get('qualifier') or '')]
    for lang, tr in (f.get('translations') or {}).items():
        parts += list(tr.get('verbatim') or []) + [tr.get('canonical') or '']
    return [p for p in parts if p]


def fact_lang_texts(f):
    """Формулировки факта с их языком: [(текст, язык)] — verbatim и canonical на языке факта, translations.<lang>."""
    base = (f.get('lang') or 'ru').split('-')[0]
    out = [(t, base) for t in list(f.get('verbatim') or []) + [f.get('canonical') or ''] if t]
    for lg, tr in (f.get('translations') or {}).items():
        out += [(t, str(lg).split('-')[0]) for t in list((tr or {}).get('verbatim') or []) + [(tr or {}).get('canonical') or ''] if t]
    return out


def fact_values(f):
    """Числа факта: из values[] и из чисел verbatim/canonical (с единицей и объектом счёта). Числа формулировок
    разбираются по языку формулировки (разделитель тысяч), объект счёта values[] дополняют what и qualifier переводов."""
    out = []
    tr_what = set()
    for tr in (f.get('translations') or {}).values():
        tr_what |= stems((tr or {}).get('what') or '') | stems((tr or {}).get('qualifier') or '')
    for v in f.get('values') or []:
        unit_ = UNIT_SYNONYMS.get(str(v.get('unit') or '').lower(), v.get('unit'))
        d = {'unit': unit_, 'what': stems(v.get('what') or '') | stems(v.get('qualifier') or '') | tr_what, 'cmp': v.get('comparator', 'eq'),
             'approx': bool(v.get('approx')), 'src': 'values'}
        if 'value' in v and v['value'] is not None:
            out.append(dict(d, value=float(v['value']), scale=v.get('scale'), count=v.get('count')))
        if v.get('range'):
            out.append(dict(d, range=[float(x) for x in v['range']]))
        if v.get('date'):
            out.append(dict(d, date=parse_iso(v['date'])))
        if v.get('as_of') and parse_iso(v['as_of']):   # «по данным на 1 сентября», «as of September 2026» — дата снимка
            out.append(dict(d, date=parse_iso(v['as_of'])))
        if unit_ in ('year',) and 'value' in v:
            out.append(dict(d, date=(int(v['value']), None, None)))
    for t, lg in fact_lang_texts(f):
        for n in extract_numbers(t, lg) + extract_word_numbers(t, lg):
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
        self.digit_names = [name_rx(str(n)) for e in self.entities for n in e.get('names') or [] if re.search(r'\d', str(n))]
        self.product_names = [name_rx(str(n)) for e in self.entities if e.get('type') == 'product' for n in e.get('names') or []]
        self.all_stems = set().union(*self.stems.values()) if self.stems else set()
        self.never = []
        for r in data.get('never_claim') or []:
            self.never.append(dict(r, origin='project'))
        self.class_info = {}
        self.use_always = [e for e in (schema or {}).get('x-use-always') or [] if isinstance(e, dict)]
        if schema:
            self.class_info = {c['id']: c for c in schema.get('x-claim-classes') or []}
            if use_defaults and data.get('never_claim_defaults', 'ru-default-1') != 'none':
                for r in schema.get('x-never-claim-defaults') or []:
                    self.never.append(dict(r, origin='default'))

    def text_has_stem(self, fid, st):
        return st in self.stems.get(fid, set())

    def name_spans(self, text):
        """Места имён сущностей с цифрой в названии (entities[].names: модель «Атлас Р 45», серия «707»):
        [(начало, конец)]. Цифра там — часть имени, а не число утверждения: сверка чисел такие места пропускает, как
        телефоны и даты. Написание заявил владелец фактов, поэтому имя из одних цифр закрывает это число в любом месте
        текста."""
        return [m.span() for rx in self.digit_names for m in rx.finditer(text or '')]

    def product_spans(self, text):
        """Места имён продуктов и услуг (entities[] вида product): [(начало, конец)]. Слово внутри имени — часть
        названия, а не условие покупки: услуга «Доставка обедов» — не условие доставки, «Обмен валюты» — не обмен
        товара."""
        return [m.span() for rx in self.product_names for m in rx.finditer(text or '')]


def name_rx(name):
    """Имя сущности в тексте: без регистра, целым словом; пробел имени — любой пробел (в том числе неразрывный), дефис —
    любое тире."""
    parts = []
    for p in re.split(r'(\s+|[-‐‑–—−])', name.strip()):
        if not p:
            continue
        parts.append(r'\s+' if p.isspace() else r'[-‐‑–—−]' if p in '-‐‑–—−' else re.escape(p))
    return re.compile(r'(?<!\w)' + ''.join(parts) + r'(?!\w)', re.I)


def load_facts(path, schema, use_defaults=True):
    if not path:
        return Facts({}, schema, use_defaults)
    if yaml is None:
        raise SystemExit('нужен PyYAML')
    with open(path, encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict) or 'facts' not in data:
        raise SystemExit(f'{path}: не facts.yaml (нет ключа facts)')
    return Facts(data, schema, use_defaults, path=path)


def load_schema(path=SCHEMA_PATH):
    if yaml is None or not os.path.exists(path):
        return {}
    with open(path, encoding='utf-8') as f:
        return deep_dates(yaml.safe_load(f) or {})


# ================================================================ внешние правила: правовой модуль
# Правила — 08-russian-legal-typography/claims-rules.yaml (подхватывается сам) и --rules. Право формулировок
# проверяется только здесь: copy_lint.py этот файл не подключает. Формат правила совместим с линтером: `pattern` в его
# синтаксисе (макросы %B% %E% %W%), `unless`, `examples: {bad, good}` строками; поля линтера (group, count_as_marker,
# priority…) claims_check не читает. Это не юридическое заключение.
LEGAL_MODULE_VERSION = '2.1'
JURISDICTIONS = ('ru', 'eu', 'us', 'other')
LEGAL_CATEGORIES = ('finance', 'medical', 'dietary-supplements', 'alcohol', 'education', 'real-estate', 'other', 'general')
_MACROS = (('%B%', r'(?<![A-Za-zА-Яа-яЁё0-9_])'), ('%E%', r'(?![A-Za-zА-Яа-яЁё0-9_])'), ('%W%', r'[A-Za-zА-Яа-яЁё0-9_]*'))


def expand_macros(p):
    """Макросы границ слова copy_lint (спецификация линтера §2.2) → Python re."""
    for k, v in _MACROS:
        p = p.replace(k, v)
    return p


_STR = {'type': 'string'}
_STRS = {'type': 'array', 'items': {'type': 'string'}}
RULES_SCHEMA = {
    '$schema': 'https://json-schema.org/draft/2020-12/schema',
    '$id': 'urn:app-design:text:claims-rules:1',
    'title': 'claims-rules.yaml — правовые правила формулировок для claims_check.py; формат правила совместим с copy_lint.py',
    'type': 'object', 'required': ['version', 'date', 'rules'], 'additionalProperties': True,
    'properties': {
        'version': {'const': 1}, 'date': {'type': 'string'}, 'jurisdiction': {'type': 'string'},
        'defaults': {'type': 'object', 'description': 'сливаются в каждое правило файла (как в copy_lint); поля правила сильнее'},
        'overrides': {'type': 'array', 'description': 'поправки уровней для copy_lint (спецификация линтера §2.4); claims_check их не читает'},
        'rules': {'type': 'array', 'items': {
            'type': 'object', 'required': ['id', 'level', 'message'], 'additionalProperties': False,
            'properties': {
                'id': {'type': 'string', 'pattern': '^[A-Z][A-Z0-9-]+$', 'description': 'рекомендуется COPY-L-…'},
                'title': _STR, 'level': {'enum': ['error', 'warning', 'info']},
                'claim_class': {'type': 'array', 'items': {'type': 'string'}, 'description': 'классы x-claim-classes: маркер класса (trigger class|any) и отбор фактов для requires'},
                'patterns': {'type': 'array', 'items': {'type': 'string'}, 'description': 'Python re, регистр не важен; ищутся в soft-тексте (ё→е, тире→«-», NBSP→пробел)'},
                'pattern': {'type': 'string', 'description': 'одна регулярка в синтаксисе copy_lint (макросы %B% %E% %W%)'},
                'unless': {'type': 'string', 'description': 'исключение — найдено в том же предложении, что и срабатывание, — правило молчит (как в copy_lint)'},
                'trigger': {'enum': ['pattern', 'class', 'any'], 'description': 'pattern — только регулярки; class — только маркеры claim_class; any (по умолчанию) — регулярки, затем маркеры'},
                'lang': {'enum': ['ru', 'en', 'any'], 'description': 'язык единицы (кириллица против латиницы)'},
                'genres': {'type': 'array', 'items': {'type': 'string'}}, 'slot_types': {'type': 'array', 'items': {'type': 'string'}},
                'exclude_slot_types': _STRS,
                'jurisdiction': {'type': 'array', 'items': {'enum': list(JURISDICTIONS)}, 'description': 'правило действует, если активная юрисдикция в списке (--jurisdiction, facts.yaml jurisdiction; по умолчанию ru)'},
                'legal_category': {'type': 'array', 'items': {'enum': list(LEGAL_CATEGORIES)}, 'description': 'только для отраслей (meaning.legal_category; --legal-category)'},
                'legal_category_except': {'type': 'array', 'items': {'enum': list(LEGAL_CATEGORIES)}, 'description': 'кроме отраслей'},
                'page_types': _STRS, 'page_types_except': _STRS,
                'forbid': {'type': 'boolean', 'description': 'true — любое срабатывание = находка (запрещённая формулировка)'},
                'once': {'enum': ['unit', 'page'], 'description': 'page — одна находка правила на страницу (обязательные оговорки)'},
                'requires': {'type': 'object', 'additionalProperties': False, 'properties': {
                    'fact': {'type': 'boolean', 'description': 'нужен публикуемый факт с классом правила'},
                    'fact_fields': {'type': 'array', 'items': {'type': 'string'}, 'description': 'поля, которые обязаны быть у найденного факта: basis.criterion, legal.disclaimer… (проверяются, только если факт найден; «нет факта» — при fact: true)'},
                    'nearby': {'type': 'array', 'items': {'type': 'string'}, 'description': 'регулярки, из которых хотя бы одна должна найтись рядом (оговорка, условие, источник)'},
                    'nearby_all': {'type': 'array', 'items': {'type': 'string'}, 'description': 'регулярки, которые все должны найтись рядом (обязательные тексты оговорок)'},
                    'nearby_scope': {'enum': ['unit', 'section', 'page'], 'description': 'где искать nearby: единица, секция (по умолчанию), страница'},
                    'fact_conditions': {'type': 'boolean', 'description': 'условия найденного факта (values[].qualifier, legal.disclaimer) обязаны стоять рядом; нет факта — проверяется nearby'},
                    'legal_review': {'enum': ['approved']}}},
                'message': {'type': 'string'}, 'fix': {'type': 'string'}, 'replacement': {'type': 'string', 'description': 'как править (формат линтера); claims_check берёт его, если нет fix'},
                'source': {'type': 'string'},
                'law': {'type': 'array', 'items': {'type': 'object', 'required': ['ref'], 'additionalProperties': False, 'properties': {
                    'ref': {'type': 'string', 'description': 'норма: «38-ФЗ ст. 5 ч. 3 п. 1», «Пленум ВАС № 58 п. 29», «ФАС, приказ № 1079/23, прил. 2 разд. II»'},
                    'edition': {'type': 'string', 'description': 'редакция: «ред. от 04.08.2026»'},
                    'checked': {'type': 'string', 'description': 'дата сверки с первоисточником ГГГГ-ММ-ДД'},
                    'in_force': {'type': 'string', 'description': 'дата вступления, если норма новая или не вступила'},
                    'url': {'type': 'string'}, 'note': {'type': 'string'}}}},
                'date': _STR, 'evidence': _STR, 'note': _STR,
                'examples': {'type': 'object', 'description': 'bad / good — строки (их проверяет --selftest); bad_en, good_en; контекст теста: slot_type, legal_category, jurisdiction, genre'},
                # поля формата copy_lint (06-anti-slop/02-linter-spec-and-profiles.md §2.1): claims_check их не читает
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
            for k in ('jurisdiction', 'legal_category', 'legal_category_except', 'genres', 'slot_types', 'exclude_slot_types', 'page_types', 'page_types_except'):
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
    pt = u.get('page_type')   # тип страницы известен у copy deck; у текста без типа правило действует
    if pt and r.get('page_types') and pt not in r['page_types']:
        return False
    if pt and r.get('page_types_except') and pt in r['page_types_except']:
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
    """soft-текст зоны «рядом»: единица, секция (page + section, как у сверки фактов) или страница."""
    if scope == 'unit':
        return soft(u['text'])
    if u.get('alt'):   # невыбранный вариант: рядом с ним — выбранные тексты других слотов, не соседние варианты
        if scope == 'page':
            return soft(' '.join([u['text']] + [x['text'] for x in units if x.get('page') == u.get('page') and not x.get('alt') and x.get('slot') != u.get('slot')]))
        return soft(' '.join(near_units(u, units)))
    key = (scope, u.get('page'), u.get('section') if scope == 'section' else None)
    z = ctx['_zones'].get(key)
    if z is None:
        if scope == 'page':
            z = soft(' '.join(x['text'] for x in units if x.get('page') == u.get('page') and not x.get('alt')))
        else:
            z = soft(' '.join(near_units(u, units)))
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
    """Что не выполнено для сработавшего правила: [причина]. Факты — найденные в единице (strong ∪ related)."""
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
    """Правовой модуль: правила claims-rules.yaml (и --rules) для одной единицы текста."""
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
        out.append(('error', 'COPY-F-PERMISSION', f"fact:{f['id']}: показывается имя или фото без согласия на распространение ПДн", 'Нужно согласие по 152-ФЗ ст. 10.1 (форма — 08-russian-legal-typography) или подпись инициалами без фото.'))
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
        lg = (f.get('lang') or 'ru').split('-')[0]
        qn = {round(n['value'], 6) for n in extract_numbers(q, lg) if 'value' in n} | {x for n in extract_numbers(q, lg) if 'range' in n for x in n['range']}
        for n in extract_numbers(t, lg):
            vals = [n['value']] if 'value' in n else n['range']
            for v in vals:
                if round(v, 6) not in qn and not (n['kind'] == 'year' and str(int(v)) in qs):
                    gap.append(n['raw'])
    return sorted(set(gap))


def check_units(units, facts, today, rules=(), strict=False, genre=None, verbose=False, ctx=None, final=False):
    """Сверка единиц текста с фактами. final — ворота публикации: демо-данные (example) — error, без final — info."""
    F, ok_claims = [], []
    lctx = ctx or legal_ctx()   # правовой модуль: юрисдикция и отрасль (по умолчанию ru, general)
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
        # ---- числа (цифрами и словами; разделитель тысяч — по языку текста)
        ulang = unit_lang(body)
        nums = sorted(extract_numbers(body, ulang, facts.name_spans(body)) + extract_word_numbers(body, ulang), key=lambda x: x['start'])
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
            nq = q_unit or in_question(body, n['start'])
            if n.get('words') and not nq:
                add(F, 'warning', 'COPY-F-NUM-WORDS', u, n['raw'], 'fact-number', 'число в утверждении написано словами' + ('' if best else ' и не найдено в фактах'),
                    'В утверждении сайта число пишется цифрами (сверка и читатель видят цифры); словами — только счёт без утверждения («два шага»).',
                    [best[0]['id']] if best else [])
            if best:
                for fid in match_ids[:3]:
                    strong.setdefault(fid, 'number')
                    strong_pos.append((fid, n['start']))
                ok_claims.append({'unit': u['id'], 'fragment': n['raw'], 'fact': best[0]['id'], 'how': best[1]})
            elif why_bad:
                f, why = why_bad[0]
                add(F, 'info' if nq else 'error', 'COPY-F-NUM-MISMATCH', u, n['raw'], 'fact-number', f"не совпадает с fact:{f['id']}: {why}",
                    f"Приведите число к факту дословно («{(f.get('verbatim') or [''])[0][:60]}») или заведите новый факт с источником.", [f['id']])
            else:
                lvl = 'info' if nq else 'error'
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
                add(F, 'info' if (q_unit or in_question(body, d['start'])) else 'error', 'COPY-F-DATE', u, d['raw'], 'fact-number', 'дата без факта',
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
            if not ctx and is_public_body(name):
                continue   # орган власти вне списка клиентов и подписи отзыва — не имя, которому нужен факт
            add(F, 'error' if ctx else 'warning', 'COPY-F-NAME', u, name, 'client-logo' if ctx else None,
                'имя или название не найдено в facts.yaml (entities, факты)',
                'Проверьте, что это реальный клиент, человек или место с фактом и разрешением; иначе уберите или замените на [PLACEHOLDER].')
        # ---- подпись отзыва, цитаты, человека: показано не больше, чем разрешено (permission.shows)
        for fid in list(strong):
            f = facts.by_id.get(fid)
            if not f or not f.get('attribution') or f.get('kind') not in ('testimonial', 'expert-quote', 'person', 'case'):
                continue
            if strong.get(fid) != 'name' and u.get('slot_type') not in ATTRIB_SLOTS:
                continue
            perm = f.get('permission') or {}
            allowed = set(perm.get('shows') or [])
            if 'full-name' in allowed:
                allowed |= {'first-name', 'initials'}
            extra = sorted(x for x in attribution_shown(body, f) if x not in allowed)
            if extra:
                add(F, 'error', 'COPY-F-PERMISSION', u, ', '.join(extra), 'testimonial-quote',
                    f"подпись fact:{fid} показывает {', '.join(extra)}, а разрешено: {', '.join(sorted(perm.get('shows') or [])) or 'ничего'}",
                    'Подпишите так, как разрешил человек (permission.shows: имя, инициалы, должность, город), или получите письменное согласие и согласие на распространение ПДн.', [fid])
        # ---- маркеры классов
        markers = find_markers(body)
        if 'purchase-terms' in markers and facts.product_names:
            # корень условия покупки внутри имени услуги или продукта из entities — название, а не условие
            pspans = facts.product_spans(soft(body))
            kept = [(frag, pos) for frag, pos in markers['purchase-terms'] if not any(a <= pos < b for a, b in pspans)]
            if kept:
                markers['purchase-terms'] = kept
            else:
                del markers['purchase-terms']
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
                        lvl = 'info' if ((q_unit or in_question(body, pos)) and not never_hit(body, cl, facts)) else 'error'
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
                    lvl = 'info' if ((q_unit or in_question(body, pos)) and not never_hit(body, cl, facts)) else 'error'
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
                add(F, 'info' if (q_unit or in_question(body, pos)) else 'error', 'COPY-F-PROPERTY', u, term, 'fact-property', f'свойство «{term}» без факта',
                    'Уберите свойство или спросите заказчика (missing) — свойства продукта не выводятся из описания.')
        # ---- never_claim
        quote_spans = []   # цитаты, совпавшие с публикуемым отзывом: (начало, конец, факт)
        for qd in quotes:
            if qd['words'] >= 3:
                res_q = match_quote(qd['text'], facts)
                if res_q['status'] in ('exact', 'recut', 'typo') and res_q['fact'] and not [x for x in publishable_issues(res_q['fact'], facts, today) if x[0] == 'error']:
                    quote_spans.append((qd['start'], qd['start'] + len(qd['raw']), res_q['fact']))
        for r in facts.never:
            rl = str(r.get('lang') or 'any').split('-')[0]
            tr = ((r.get('translations') or {}).get(ulang) or {}) if ulang else {}
            if rl not in ('any', ulang) and not tr:
                continue   # запрет на другом языке: его слова в этом тексте не ищутся
            pats = list(tr.get('patterns') or []) + (list(r.get('patterns') or []) if rl in ('any', ulang) else [])
            hit, hit_pos = never_match(pats, body, relax=r.get('origin') == 'project')
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
                f"never_claim {r['id']}: {(tr.get('text') or r.get('text', ''))[:120]}" + (' (снимается только фактом)' if lift == 'with-fact' else ' (не снимается)' if lift == 'never' else ' (только после проверки юриста)'),
                'Уберите утверждение; вопросом тоже нельзя («Хотите … без …?» — то же обещание).')
        # ---- проблемы использованных фактов
        for fid, how in list(strong.items()) + [(k, v) for k, v in related.items() if k not in strong]:
            f = facts.by_id.get(fid)
            if not f:
                continue
            for lvl, rule, msg, fix in publishable_issues(f, facts, today):
                add(F, lvl, rule, u, fid, ','.join(f.get('claim_class') or []), msg, fix, [fid])
            use = f.get('use') or {}
            if f.get('example') or facts.data.get('example'):
                add(F, 'error' if final else 'info', 'COPY-F-EXAMPLE', u, fid, None,
                    f"fact:{fid} — демо-данные (example: true" + (' у файла фактов)' if facts.data.get('example') and not f.get('example') else ')')
                    + ': на макете допустимы, в публикацию не идут',
                    'До публикации замените демо-факт настоящим с источником или уберите утверждение (validate --final).', [fid])
            if use and not use.get('any') and not q_unit and not use_always(facts, u, f):
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
            req_near = nearby_requirement(f, ulang)
            if req_near and how in ('number', 'rating', 'fact_ids', 'marker', 'date') and not nearby_ok(req_near, u, units):
                add(F, 'warning', 'COPY-F-NEARBY', u, fid, None, f"fact:{fid}: рядом должно стоять: {req_near}", 'Добавьте источник или оговорку в тот же блок (slot stat-source, cta-note).', [fid])
        # ---- флаги copy deck
        declared = set(u.get('claim_flags') or [])
        found_cl = set(markers) | ({'fact-number'} if nums else set())
        missing_flags = sorted((found_cl - declared) - {'fact-number', 'purchase-terms', 'company-details'}) if u.get('claim_flags') is not None and u.get('slot_type') else []
        if missing_flags and u['id'].count('/') >= 3:
            add(F, 'info', 'COPY-F-FLAGS', u, ','.join(missing_flags), None, 'в claim_flags слота нет найденных классов', 'Добавьте классы в claim_flags (их читают проверка права и copydeck.py).')
        # ---- строгий режим: утверждения без опоры
        if strict and u.get('slot_type') in (None, 'body', 'card-body', 'step-body', 'subheadline', 'spec-row', 'faq-a', 'case-summary', 'case-result', 'pricing-feature', 'guarantee-text', 'objection-answer') and not q_unit:
            covered = [fid for fid in list(strong) + list(related) if fid in facts.by_id]
            if not covered and len(tokens(body)) >= 5:
                us = stems(body)
                best = max(((len(us & facts.stems[f['id']]) / max(1, len(us)), f['id']) for f in facts.facts), default=(0, None))
                if best[0] < 0.34:
                    add(F, 'warning', 'COPY-F-UNSUPPORTED', u, body[:80], 'fact-property', f'в тексте утверждение без опоры на факт (перекрытие слов с лучшим фактом {best[0]:.0%})',
                        'Строгий режим: у содержательного утверждения о продукте или услуге должен быть факт; иначе — голос клиента без обещаний или [PLACEHOLDER].')
        # ---- внешние правила: правовой модуль — apply_legal_rules
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


JOB_TITLE_RX = re.compile(r'директор|руководител|начальник|менеджер|основател|совладел|владел|партн[её]р|глав[аы]|заведующ|инженер|'
                          r'бухгалтер|юрист|врач|специалист|консультант|аналитик|дизайнер|архитектор|маркетолог|ceo|cto|cfo|coo|'
                          r'founder|owner|head\b|manager|director|lead\b|engineer|designer|consultant|officer|president|partner', re.I)


def attribution_shown(body, f):
    """Что подпись показывает из attribution факта: first-name, full-name (фамилия целиком), position (роль — должность:
    «генеральный директор», «владелец кофейни»; описание заказа клиента — не должность), company, city."""
    att = f.get('attribution') or {}
    words = {stem(w) for w in WORD_RX.findall(norm(body))}
    shown = set()
    name = [w for w in WORD_RX.findall(norm(att.get('name') or '')) if len(w) > 1]
    if name and any(stem_like(stem(name[0]), w) for w in words):
        shown.add('first-name')
    if len(name) >= 2 and any(stem_like(stem(name[-1]), w) for w in words):
        shown.add('full-name')
    for key, what in (('role', 'position'), ('company', 'company'), ('city', 'city')):
        if key == 'role' and not JOB_TITLE_RX.search(att.get('role') or ''):
            continue
        st = {stem(w) for w in WORD_RX.findall(norm(att.get(key) or '')) if w not in STOP and len(w) > 2}
        if st and len(st & words) >= max(1, (len(st) + 1) // 2):
            shown.add(what)
    return shown


def never_match(patterns, body, relax=False):
    """Первое срабатывание регулярок запрета в soft-тексте: (фрагмент, позиция) или (None, None). relax — запрет проекта из
    слов («смет\\w*\\s+не\\s+вырос»): ищется и пересказ с вставкой до пяти слов между словами внутри одного предложения
    («смета, которую составили, не выросла»)."""
    sb = soft(body)
    for p in patterns:
        try:
            m = re.search(p, sb, re.I)
        except re.error:
            m = None
        if m:
            return m.group(0), m.start()
    if relax:
        for p in patterns:
            parts = re.split(r'\\s[+*]', p)
            if len(parts) < 2 or any('\\s' in x or not x for x in parts):
                continue
            try:
                rx = re.compile(r'(?:[\s,]+[^\s.!?;]+){0,5}?[\s,]+'.join(parts), re.I)
            except re.error:
                continue
            for a, b in sentence_spans(sb):
                m = rx.search(sb, a, b)
                if m:
                    return m.group(0), m.start()
    return None, None


def near_units(u, units):
    """Тексты «рядом» с единицей: сама единица и выбранные тексты других слотов той же секции. Невыбранные варианты
    (--all-variants) и соседние варианты того же слота рядом не считаются: они не стоят на странице одновременно."""
    out = [u['text']]
    for x in units:
        if x is u or x.get('alt') or x.get('section') != u.get('section') or x.get('page') != u.get('page'):
            continue
        if x.get('slot') and x.get('slot') == u.get('slot'):
            continue
        out.append(x['text'])
    return out


def words_in(frag, zone_words):
    """Слова фрагмента стоят в зоне подряд и в том же порядке; знаки препинания и вид пробелов не сравниваются (тире
    вместо запятой, неразрывный пробел — та же формулировка). Фрагмент без слов — False."""
    fw = WORD_RX.findall(norm(frag))
    n = len(fw)
    return bool(n) and any(zone_words[i:i + n] == fw for i in range(len(zone_words) - n + 1))


def nearby_ok(req, u, units):
    """Выполнено ли требование «рядом должно стоять» (use.requires_nearby): альтернативы через « или » — достаточно одной;
    в альтернативе фрагменты в «ёлочках» — теми же словами подряд (без регистра, знаков препинания и вида пробелов) в
    единице или её секции; «источник, дата» — признак источника рядом (по данным, на дату, площадка); иначе половина
    значимых слов требования."""
    zone = soft(' '.join(near_units(u, units)))
    zone_words = WORD_RX.findall(norm(zone))
    alts = [a.strip(' ,;') for a in re.split(r'\s+или\s+|\s+or\s+', req) if a.strip(' ,;')] or [req]
    for alt in alts:
        if re.search(r'источник|по данным|дат[аы]|source|as of', alt, re.I) and SOURCE_HINT_RX.search(zone):
            return True
        frags = re.findall(r'«([^»]+)»', alt)
        if frags:
            if all(soft(f_) in zone or words_in(f_, zone_words) for f_ in frags):
                return True
            continue
        st = {stem(w) for w in WORD_RX.findall(norm(alt)) if w not in STOP and len(w) > 2}
        zs = {stem(w) for w in WORD_RX.findall(norm(zone))}
        if st and len(st & zs) >= max(1, len(st) // 2):
            return True
    return False


def use_always(facts, u, f):
    """Место, где любой факт законен (facts.schema.yaml x-use-always): место — слот или секция, как в use; условия
    (page_types, claim_classes, fact_kinds, requires) — все сразу. → запись или None."""
    for e in facts.use_always:
        places = [(u.get('slot_type'), e.get('slot_types')), (u.get('section_role'), e.get('section_roles'))]
        places = [(v, lst) for v, lst in places if lst]
        if places and not any(v and v in lst for v, lst in places):
            continue
        if e.get('page_types') and u.get('page_type') not in e['page_types']:
            continue
        if e.get('claim_classes') and not set(e['claim_classes']) & set(f.get('claim_class') or []):
            continue
        if e.get('fact_kinds') and f.get('kind') not in e['fact_kinds']:
            continue
        if e.get('requires') and not get_path(f, e['requires']):
            continue
        return e
    return None


def nearby_requirement(f, lang):
    """Что должно стоять рядом с фактом на языке текста: translations.<lang>.requires_nearby, иначе use.requires_nearby."""
    base = (f.get('lang') or 'ru').split('-')[0]
    if lang and lang != base:
        tr = (f.get('translations') or {}).get(lang) or {}
        if tr.get('requires_nearby'):
            return tr['requires_nearby']
    return (f.get('use') or {}).get('requires_nearby')


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
    return f'Нужен факт класса {cl} ({needs})' + (f'; нормы права: {law}' if law else '') + '; до этого — убрать утверждение или [PLACEHOLDER].'


def is_public_body(name):
    """Имя — орган власти из PUBLIC_BODIES (в любом падеже, с «России» или «РФ» рядом), а не название с тем же словом."""
    ws = [soft(w) for w in re.split(r'[\s-]+', name) if w]
    body = [w for w in ws if w not in ('россии', 'рф')]
    return bool(body) and all(w in PUBLIC_BODIES or any(stem_like(stem(w), stem(b)) for b in PUBLIC_BODIES if len(b) > 4) for w in body)


def stem_like(a, b):
    """Основы одного имени в разных падежах: «серге» (Сергея) и «серг» (Сергей), «лапин» и «лапин»."""
    return a == b or (min(len(a), len(b)) >= 4 and (a.startswith(b) or b.startswith(a)) and abs(len(a) - len(b)) <= 2)


def name_stem_hit(st, facts):
    if st in facts.name_stems:
        return facts.name_stems[st]
    return next((v for k, v in facts.name_stems.items() if stem_like(st, k)), None)


def name_known(name, facts):
    n = norm(name).strip('"').strip()
    if not n:
        return None
    if n in facts.names:
        return facts.names[n]
    ws = WORD_RX.findall(n)
    if ws and all(name_stem_hit(stem(w), facts) for w in ws):
        return name_stem_hit(stem(ws[0]), facts)
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
    if res.get('binding'):
        b = res['binding']
        L += ['', f"Привязка к copy deck `{b['deck']}`: единиц {b['units']}, со слотом {b['bound']}, без привязки {b['unbound']}"]
    if res.get('softened'):
        L += ['', f"Копия артборда: {res['softened']} находок эвристик у текста без привязки к слоту — info (сверка по слотам — ключ --deck)"]
    if res.get('allow'):
        L += ['', f"Обходы `{res['allow']['file']}`: записей {res['allow']['entries']}, находок под обходом {res['allow']['applied']}"]
    if res.get('rules_loaded'):
        L += ['', f"Внешние правила: {', '.join(res['rules_loaded'])}"]
    lg = res.get('legal')
    if lg:
        L += [f"Право (модуль {lg.get('module')}): юрисдикция {lg.get('jurisdiction')} · отрасль "
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
    binding = None
    if a.deck:
        if fmt == 'deck':
            raise SystemExit('--deck: вход — copy deck, его единицы уже со слотами; ключ нужен HTML, Markdown и тексту')
        dunits, _dfmt, dmeta = load_input(a.deck, 'deck')
        units, n_bound = bind_units(units, dunits)
        meta = dict({k: v for k, v in dmeta.items() if k in ('jurisdiction', 'legal_category')}, **meta)
        binding = {'deck': a.deck, 'units': len(units), 'bound': n_bound, 'unbound': sum(1 for u in units if not u.get('bound'))}
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
    F, ok_claims, stats = check_units(units, facts, today, rules, a.strict, a.genre, a.verbose, ctx, final=a.final)
    rule_ids = {r['id'] for r in rules}
    allow = None
    if a.allow:
        entries, anotes = load_allow(a.allow)
        n_allowed, n_lost = apply_allow(F, units, entries)
        if n_lost:
            anotes.append(f'обходов без места во входе: {n_lost} — слот, мета или страница copy deck; у входа без слотов нужен ключ '
                          '--deck или записи с фрагментом (copydeck.py check --json)')
        if not a.quiet:
            for x in anotes:
                print('обходы:', x, file=sys.stderr)
        allow = {'file': a.allow, 'entries': len(entries), 'applied': n_allowed, 'notes': anotes}
    softened = soften_unbound(F, units) if meta.get('canvas_copy') else 0
    if a.legal_only:
        F = [f for f in F if f['rule'] in rule_ids]
    res = {'tool': 'claims_check.py', 'command': 'check', 'skill_version': kbpaths.skill_version(), 'version': VERSION,
           'today': today.isoformat(), 'input': a.input, 'format': fmt,
           'facts': a.facts, 'schema': os.path.relpath(a.schema, ROOT) if os.path.exists(a.schema) else None,
           'rules_loaded': [os.path.relpath(p, ROOT) if p.startswith(ROOT) else p for p in rule_paths if os.path.exists(p)],
           'summary': summarize(F, stats), 'findings': F, 'supported': ok_claims if a.verbose else [], 'verbose': a.verbose, 'final': bool(a.final),
           'canvas_copy': bool(meta.get('canvas_copy')), 'softened': softened, 'binding': binding, 'allow': allow,
           'legal': {'module': LEGAL_MODULE_VERSION, 'jurisdiction': ctx['jurisdiction'], 'legal_category': sorted(ctx['categories']),
                     'rules': len(rules), 'findings': sum(1 for f in F if f['rule'] in rule_ids), 'legal_only': bool(a.legal_only)}}
    write_outputs(res, a)
    if not a.quiet:
        s = res['summary']
        print(f"claims_check: {s['error']} error, {s['warning']} warning, {s['info']} info; утверждений {s['claims']}, подтверждено {s['supported']}; [PLACEHOLDER] {s['placeholders']}")
        if binding:
            print(f"  привязка к copy deck: единиц {binding['units']}, со слотом {binding['bound']}, без привязки {binding['unbound']}")
        if softened:
            print(f"  копия артборда: {softened} находок эвристик у текста без привязки к слоту — info (сверка по слотам — ключ --deck)")
        if allow:
            print(f"  обходы {os.path.basename(a.allow)}: записей {allow['entries']}, находок под обходом {allow['applied']}")
        for f in F:
            if f['level'] == 'error' or a.verbose:
                print(f"  {f['level'].upper():7} {f['rule']:26} {loc_str(f['location'])[:40]:40} «{str(f['fragment'])[:50]}» — {f['message'][:110]}")
    return 1 if res['summary']['error'] else 0


def cmd_inventory(a):
    units, fmt, meta = load_input(a.input, a.format, True)
    rows = []
    for i, u in enumerate(units):
        body = PLACEHOLDER_RX.sub(' ', u['text'])
        neigh = ' '.join(x['text'] for x in units[max(0, i - 1):i + 2])
        src_vis = bool(SOURCE_HINT_RX.search(neigh))
        claims = []
        for n in extract_numbers(body, unit_lang(body)) + extract_word_numbers(body):
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
    res = {'tool': 'claims_check.py', 'command': 'inventory', 'skill_version': kbpaths.skill_version(), 'version': VERSION,
           'input': a.input, 'format': fmt, 'units': len(units),
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
    if facts.data.get('example'):
        add(F, 'error' if a.final else 'warning', 'COPY-F-EXAMPLE', unit('facts', a.input), 'example', None,
            'файл фактов — демо-данные (example: true): на макете допустимы, публикация — нет',
            'До публикации — настоящий facts.yaml заказчика с источниками.')
    for f in facts.facts:
        u = unit(f"fact:{f['id']}", (f.get('verbatim') or [''])[0])
        if f.get('example') and not facts.data.get('example'):
            add(F, 'error' if a.final else 'warning', 'COPY-F-EXAMPLE', u, f['id'], None, f"fact:{f['id']} — демо-данные (example: true)",
                'До публикации замените настоящим фактом с источником.', [f['id']])
        for lvl, rule, msg, fix in publishable_issues(f, facts, today):
            if rule == 'COPY-F-PERMISSION' and msg == f"fact:{f['id']}: разрешение pending" and not a.final:
                # разрешение запрошено — обычное состояние сбора фактов; ворота публикации — --final
                lvl, fix = 'warning', 'Разрешение запрошено: до публикации нужен ответ granted (ворота — lint-facts --final); до ответа на странице — [PLACEHOLDER].'
            add(F, lvl, rule, u, f['id'], ','.join(f.get('claim_class') or []), msg, fix, [f['id']])
        if f.get('kind') in ('testimonial', 'person', 'client', 'partner', 'case', 'expert-quote') and (f.get('permission') or {}).get('status') == 'not-required':
            add(F, 'error', 'COPY-F-PERMISSION', u, f['id'], f.get('kind'), f"fact:{f['id']}: вид {f.get('kind')} требует разрешения третьего лица, а стоит not-required", 'Укажите разрешение субъекта (permission.subject, form, document).')
        if vocab:
            use = f.get('use') or {}
            for key, vk in (('page_types', 'page_types'), ('section_roles', 'section_roles'), ('slot_types', 'slot_types')):
                for x in use.get(key) or []:
                    if x not in vocab.get(vk, set()):
                        add(F, 'warning', 'COPY-F-VOCAB', u, x, None, f'{key}: «{x}» нет в словаре site', 'Возьмите id из kb/site/02-site-types/vocabulary.yaml (page_type, section_role, slot).')
    for m in facts.missing:
        if not PLACEHOLDER_RX.fullmatch(m.get('placeholder') or ''):
            add(F, 'error', 'COPY-F-PLACEHOLDER', unit(f"missing:{m.get('id')}", m.get('what', '')), m.get('placeholder'), None, 'placeholder не в форме [PLACEHOLDER: …]', 'Исправьте текст заглушки.')
    res = {'tool': 'claims_check.py', 'command': 'lint-facts', 'skill_version': kbpaths.skill_version(), 'version': VERSION,
           'today': today.isoformat(), 'input': a.input,
           'summary': {lv: sum(1 for f in F if f['level'] == lv) for lv in LEVELS}, 'findings': F}
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
    if not a.quiet:
        s = res['summary']
        print(f"lint-facts: {s['error']} error, {s['warning']} warning, {s['info']} info")
        for f in F:
            print(f"  {f['level'].upper():7} {f['rule']:22} {f['unit']:34} {f['message'][:120]}")
    return 1 if res['summary']['error'] else 0


def load_vocab():
    """id мест use по словарю site: page_types, section_roles, slot_types (слоты вида text)."""
    v = site_vocab()
    if not v['page_types']:
        return {}
    return {'page_types': set(v['page_types']), 'section_roles': set(v['section_roles']), 'slot_types': set(v['text_slots'])}


def cmd_rules_schema(a):
    print(json.dumps(RULES_SCHEMA, ensure_ascii=False, indent=1))
    return 0


# ================================================================ selftest
FP_PHRASES = [  # лозунги, вопросы, призывы — не утверждения о фактах
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


LEGAL_FP_PHRASES = FP_PHRASES + [  # нейтральные строки лендинга: правила права не дают ни error, ни warning
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
    """Тесты правового модуля: механика требований на встроенных правилах, затем claims-rules.yaml."""
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
    check('право: встроенные правила загружены (defaults, pattern с макросами)', len(rules) == 6 and not errs, errs)
    R = {r['id']: r for r in rules}
    # превосходная степень: unless, nearby в секции, fact_fields у найденного факта
    check('право: «Лучшая доставка» без критерия → T-SUP', ids(run([unit('a', 'Лучшая доставка в городе')], empty, [R['T-SUP']]), 'T-SUP'))
    check('право: критерий в том же предложении (unless) → тишина', not ids(run([unit('a', 'Лучшая доставка в городе по данным замера агентства X')], empty, [R['T-SUP']]), 'T-SUP'))
    two = [unit('a', 'Лучшая доставка в городе', section='s', page='p'), unit('b', '* По замеру агентства X, май 2026', section='s', page='p')]
    check('право: критерий в той же секции (nearby) → тишина', not ids(run(two, empty, [R['T-SUP']]), 'T-SUP'))
    fdata = {'facts': [{'id': 'best-noproof', 'kind': 'property', 'claim_class': ['superlative'], 'verbatim': ['лучшая доставка в городе'],
                        'canonical': 'Лучшая доставка в городе.', 'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'},
                        'verification': {'status': 'stated'}, 'permission': {'status': 'not-required'}, 'lang': 'ru'}], 'never_claim_defaults': 'none'}
    fx = Facts(fdata, schema, False)
    two_f = [unit('a', 'Лучшая доставка в городе', section='s', page='p', fact_ids=['best-noproof']), two[1]]
    F_ = ids(run(two_f, fx, [R['T-SUP']]), 'T-SUP')
    check('право: факт без basis.criterion → T-SUP «у факта нет basis.criterion»', F_ and 'basis.criterion' in F_[0]['message'], F_)
    facts_b2, _ = _selftest_facts()
    two_ok = [unit('a', 'Самая быстрая доставка в городе', section='s', page='p'), unit('b', '* По замеру агентства X, май 2026', section='s', page='p')]
    rs = dict(R['T-SUP'], _rx=[re.compile(expand_macros(r'%B%сам\w+\s+быстр\w+'), re.I)])
    check('право: факт с basis (best-study, найден маркером) + критерий рядом → тишина', not ids(run(two_ok, facts_b2, [rs]), 'T-SUP'))
    # «бесплатно»: условие факта рядом
    ffree = Facts({'facts': [{'id': 'estimate-free', 'kind': 'price', 'claim_class': ['price-discount'], 'verbatim': ['Смета и выезд замерщика — бесплатно'],
                              'canonical': 'Смета и выезд замерщика бесплатно в пределах города.', 'values': [{'value': 0, 'unit': 'RUB', 'what': 'смета', 'qualifier': 'в пределах города'}],
                              'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
                              'permission': {'status': 'not-required'}, 'lang': 'ru'}], 'never_claim_defaults': 'none'}, schema, False)
    u1 = unit('a', 'Смета и выезд замерщика — бесплатно', section='s', page='p', fact_ids=['estimate-free'])
    F_ = ids(run([u1], ffree, [R['T-FREE']]), 'T-FREE')
    check('право: «бесплатно» без условия из факта («в пределах города») → T-FREE', F_ and 'в пределах города' in F_[0]['message'], F_)
    check('право: условие факта в той же секции → тишина', not ids(run([u1, unit('b', 'Выезжаем в пределах города', section='s', page='p')], ffree, [R['T-FREE']]), 'T-FREE'))
    check('право: «бесплатно» без факта и без условия → T-FREE', ids(run([unit('a', 'Доставка бесплатно')], empty, [R['T-FREE']]), 'T-FREE'))
    check('право: «бесплатно, без условий» → тишина', not ids(run([unit('a', 'Доставка бесплатно, без условий')], empty, [R['T-FREE']]), 'T-FREE'))
    # юрисдикция, отрасль, язык, once
    check('право: правило ЕС молчит при ru', not ids(run([unit('a', 'Скидка 20 % на всё')], empty, [R['T-EU']], 'ru'), 'T-EU'))
    check('право: правило ЕС работает при --jurisdiction eu', ids(run([unit('a', 'Скидка 20 % на всё')], empty, [R['T-EU']], 'eu'), 'T-EU'))
    med = [unit('a', 'Лечение кариеса', page='p1', section='s1'), unit('b', 'Лечение пульпита', page='p1', section='s2')]
    check('право: оговорка медицины молчит для general', not ids(run(med, empty, [R['T-MED']]), 'T-MED'))
    F_ = ids(run(med, empty, [R['T-MED']], cats=['medical']), 'T-MED')
    check('право: medical без оговорки → одна находка на страницу (once: page)', len(F_) == 1, F_)
    med_ok = med + [unit('c', 'Имеются противопоказания, необходима консультация специалиста', page='p1', section='footer')]
    check('право: оговорка на странице (nearby_all, scope page) → тишина', not ids(run(med_ok, empty, [R['T-MED']], cats=['medical']), 'T-MED'))
    med_half = med + [unit('c', 'Имеются противопоказания', page='p1', section='footer')]
    check('право: половина обязательной оговорки → находка', ids(run(med_half, empty, [R['T-MED']], cats=['medical']), 'T-MED'))
    check('право: lang en — английская единица', ids(run([unit('a', 'Get it free today')], empty, [R['T-LANG']]), 'T-LANG'))
    check('право: lang en — русская единица молчит', not ids(run([unit('a', 'Доставка бесплатно, free')], empty, [R['T-LANG']]), 'T-LANG'))
    check('право: запрет вне медицины → T-FORBID', ids(run([unit('a', 'Вылечит спину за месяц')], empty, [R['T-FORBID']]), 'T-FORBID'))
    check('право: legal_category_except medical → тишина', not ids(run([unit('a', 'Вылечит спину за месяц')], empty, [R['T-FORBID']], cats=['medical']), 'T-FORBID'))
    # --- claims-rules.yaml
    if not os.path.exists(RULES_PATH):
        check('право: 08-russian-legal-typography/claims-rules.yaml существует', False, RULES_PATH)
        return
    rules, errs = load_rules([RULES_PATH])
    check(f'право: claims-rules.yaml загружен без ошибок ({len(rules)} правил)', rules and not errs, errs)
    props = RULES_SCHEMA['properties']['rules']['items']['properties']
    rprops = props['requires']['properties']
    with open(RULES_PATH, encoding='utf-8') as f:
        raw_rules = (yaml.safe_load(f) or {}).get('rules') or []
    extra = sorted({k for r in raw_rules for k in r if k not in props} | {k for r in raw_rules for k in (r.get('requires') or {}) if k not in rprops})
    check('право: поля правил ⊆ rules-schema', not extra, extra)
    bad_meta = [r['id'] for r in rules if not (r['id'].startswith('COPY-L-') and law_refs(r) and r.get('source') and (r.get('examples') or {}).get('bad') and (r.get('examples') or {}).get('good'))]
    check('право: у каждого правила COPY-L-id, law, source и пара примеров', not bad_meta, bad_meta)
    classes = {c['id'] for c in schema.get('x-claim-classes') or []}
    bad_cls = sorted({c for r in rules for c in r.get('claim_class') or [] if c not in classes})
    check('право: claim_class правил ⊆ x-claim-classes', not bad_cls, bad_cls)
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
    check('право: каждый «плохой» пример ловится своим правилом', not miss_bad, miss_bad)
    check('право: ни один «хороший» пример не ловится своим правилом', not hit_good, hit_good)
    fp = []
    for p in LEGAL_FP_PHRASES:
        F_ = [f for f in run([unit('t', p)], empty, rules) if f['level'] in ('error', 'warning') and f['rule'].startswith('COPY-L-')]
        if F_:
            fp.append((p, [(f['rule'], f['fragment']) for f in F_]))
    check(f'право: {len(LEGAL_FP_PHRASES)} нейтральных фраз — ни error, ни warning правил права', not fp, fp)
    # CLI: --legal-only
    with tempfile.TemporaryDirectory() as td:
        pin, pout = os.path.join(td, 'in.txt'), os.path.join(td, 'out.json')
        with open(pin, 'w', encoding='utf-8') as f:
            f.write('Лучший сервис в городе\n')
        code = main(['check', pin, '--legal-only', '--quiet', '--json', pout, '--today', '2026-09-24'])
        with open(pout, encoding='utf-8') as f:
            res = json.load(f)
        check('--json для кода: tool claims_check.py, command check, skill_version — VERSION скилла, summary.error',
              res.get('tool') == 'claims_check.py' and res.get('command') == 'check'
              and res.get('skill_version') == kbpaths.skill_version() and isinstance(res['summary'].get('error'), int),
              {k: res.get(k) for k in ('tool', 'command', 'skill_version')})
        check('право: CLI --legal-only: только COPY-L, код 1, блок legal', code == 1 and res['findings'] and all(x['rule'].startswith('COPY-L-') for x in res['findings']) and res['legal']['jurisdiction'] == 'ru', (code, res.get('legal'), [x['rule'] for x in res['findings']]))
        check('право: одно нарушение — одна находка права', [(x['rule'], x['level']) for x in res['findings']] == [('COPY-L-SUP-01', 'error')], [(x['rule'], x['level']) for x in res['findings']])


def _selftest_binding(check, facts):
    """Привязка входа без слотов к copy deck, обходы --allow, статичная копия артборда, имена услуг и ведомств."""
    today = dt.date(2026, 9, 24).isoformat()
    deck = {'copy_deck': {'version': 0, 'pages': [{'page_id': 'home', 'page_type': 'landing-waitlist', 'sections': [
        {'section_id': 'hero', 'section_role': 'hero', 'slots': [
            {'slot_id': 'h1', 'slot_type': 'headline', 'variants': [{'id': 'a', 'text': 'Лампа для чтения'}], 'chosen': 'a', 'fact_ids': []},
            {'slot_id': 'sub', 'slot_type': 'subheadline', 'variants': [{'id': 'a', 'text': 'Первые 300 ламп — 8 900 ₽'}], 'chosen': 'a', 'fact_ids': ['price']},
            {'slot_id': 'note', 'slot_type': 'cta-note', 'variants': [{'id': 'a', 'text': 'Зарплата мастера — в смете'}], 'chosen': 'a', 'fact_ids': []}]}]}]}}
    head = '<!doctype html><html><head><title>Главная · 1440</title>\n<!-- dc_to_html: статичная копия артборда Home-1440.dc.html -->'
    copy_html = (head + '</head><body><h1>Лампа для чтения</h1><p>Первые 300\u00a0ламп — 8 900 ₽</p><div><span>Зарплата мастера — в смете</span> '
                 '<span>Ещё 5 000 довольных клиентов</span></div><p>Лампа бережёт глаза</p></body></html>')
    with tempfile.TemporaryDirectory() as td:
        fp, dp, hp, jp = (os.path.join(td, x) for x in ('facts.yaml', 'deck.yaml', 'Home-1440.html', 'out.json'))
        with open(fp, 'w', encoding='utf-8') as fo:
            yaml.safe_dump(facts.data, fo, allow_unicode=True, sort_keys=False)
        with open(dp, 'w', encoding='utf-8') as fo:
            yaml.safe_dump(deck, fo, allow_unicode=True, sort_keys=False)
        with open(hp, 'w', encoding='utf-8') as fo:
            fo.write(copy_html)

        def run(inp, *keys):
            code = main(['check', inp, '--facts', fp, '--today', today, '--quiet', '--no-external-rules', '--json', jp, *keys])
            with open(jp, encoding='utf-8') as fi:
                return code, json.load(fi)

        def lv(res, rule):
            return sorted({f['level'] for f in res['findings'] if f['rule'] == rule})
        code, res = run(hp)
        soft_rules = {f['rule'] for f in res['findings'] if f.get('level_was')}
        check('копия артборда без --deck: находки эвристик — info, never_claim остаётся error',
              res['canvas_copy'] and res['softened'] >= 2 and {'COPY-F-CLASS', 'COPY-F-NUM'} <= soft_rules and lv(res, 'COPY-F-NEVER') == ['error']
              and not [f for f in res['findings'] if f['level'] == 'error' and f['rule'] != 'COPY-F-NEVER'], (code, [(f['rule'], f['level']) for f in res['findings']]))
        with open(hp, 'w', encoding='utf-8') as fo:
            fo.write(copy_html.replace('<p>Лампа бережёт глаза</p>', ''))
        code, res = run(hp)
        check('копия артборда без --deck и без запретов: 0 error, код 0', code == 0 and res['summary']['error'] == 0 and res['softened'] >= 2,
              (code, [(f['rule'], f['level']) for f in res['findings']]))
        code, res = run(hp, '--deck', dp)
        bound = {(f['rule'], f['location'].get('slot'), f['level']) for f in res['findings']}
        check('копия артборда с --deck: текст слота сверяется как слот (страница, секция, тип, fact_ids), текст вне copy deck — без привязки',
              res['binding'] and res['binding']['bound'] == 3 and res['binding']['unbound'] == 1
              and ('COPY-F-CLASS', 'note', 'error') in bound and not [x for x in bound if x[1] == 'sub' and x[2] == 'error']
              and lv(res, 'COPY-F-NUM') == ['info'] and code == 1, (code, res.get('binding'), sorted(bound, key=str)))
        ap = os.path.join(td, 'allowed.json')
        with open(ap, 'w', encoding='utf-8') as fo:
            json.dump({'allowed': [{'rule': 'COPY-F-CLASS', 'where': 'home/hero/note', 'reason': 'зарплата — строка сметы, не доход клиента', 'by': 'заказчик', 'scope': 'slot'},
                                   {'rule': 'COPY-L-SUP-01', 'where': 'home', 'reason': 'слоган', 'by': 'заказчик', 'scope': 'page'},
                                   {'rule': 'COPY-F-NUM', 'where': 'home/hero/sub', 'reason': '', 'by': 'заказчик'}]}, fo, ensure_ascii=False)
        code_a, res_a = run(hp, '--deck', dp, '--allow', ap)
        fa = [f for f in res_a['findings'] if f.get('allowed')]
        check('--allow: находка слота под обходом — info с причиной и тем, кто решил; без файла она error',
              code_a == 0 and len(fa) == 1 and fa[0]['rule'] == 'COPY-F-CLASS' and fa[0]['level'] == 'info' and fa[0]['level_was'] == 'error'
              and 'строка сметы' in fa[0]['message'] and fa[0]['allowed']['by'] == 'заказчик' and res_a['allow']['applied'] == 1,
              (code_a, [(f['rule'], f['level'], f.get('allowed')) for f in res_a['findings']]))
        check('--allow: запись с правилом права и запись без reason не действуют',
              res_a['allow']['entries'] == 1 and len(res_a['allow']['notes']) == 2, res_a['allow'])
        code_d, res_d = run(dp, '--allow', ap)
        check('--allow на copy deck: место обхода — слот страницы', code_d == 0 and res_d['allow']['applied'] == 1
              and [f['location'].get('slot') for f in res_d['findings'] if f.get('allowed')] == ['note'], (code_d, res_d['allow']))
        tp = os.path.join(td, 'page.txt')
        with open(tp, 'w', encoding='utf-8') as fo:
            fo.write('Зарплата мастера — в смете\n')
        with open(ap, 'w', encoding='utf-8') as fo:
            json.dump([{'rule': 'COPY-F-CLASS', 'where': 'home/hero/note', 'fragment': 'Зарплата', 'reason': 'строка сметы', 'by': 'аналитик'}], fo, ensure_ascii=False)
        code_t0, res_t0 = run(tp)
        code_t, res_t = run(tp, '--allow', ap)
        check('--allow у текста без слотов: обход по фрагменту записи; без файла находка есть',
              code_t0 == 1 and lv(res_t0, 'COPY-F-CLASS') == ['error'] and code_t == 0 and lv(res_t, 'COPY-F-CLASS') == ['info'], (code_t0, code_t, res_t['findings']))
        with open(ap, 'w', encoding='utf-8') as fo:
            json.dump([{'rule': 'COPY-F-CLASS', 'where': 'home/hero/note', 'reason': 'строка сметы', 'by': 'аналитик'}], fo, ensure_ascii=False)
        code_t, res_t = run(tp, '--allow', ap)
        check('--allow у текста без слотов: записи слота без фрагмента не находится места — находка остаётся',
              code_t == 1 and res_t['allow']['applied'] == 0 and any('без места' in x for x in res_t['allow']['notes']), (code_t, res_t['allow']))
        # место и снятое записи обхода: мета, число value, id находки, фрагмент; запись без scope — по виду where
        deck_m = {'copy_deck': {'version': 0, 'pages': [{'page_id': 'home', 'page_type': 'landing-waitlist',
                                                         'meta': {'title': 'Лампа для чтения — 12 лет работы'}, 'sections': [
            {'section_id': 'hero', 'section_role': 'hero', 'slots': [
                {'slot_id': 'h1', 'slot_type': 'headline', 'variants': [{'id': 'a', 'text': '12 лет делаем лампы'}], 'chosen': 'a', 'fact_ids': []},
                {'slot_id': 'sub', 'slot_type': 'subheadline', 'variants': [{'id': 'a', 'text': 'Собрали 340 ламп для библиотек за 12 лет'}], 'chosen': 'a', 'fact_ids': []},
                {'slot_id': 'note', 'slot_type': 'cta-note', 'variants': [{'id': 'a', 'text': '10 000 клиентов доверяют нам'}], 'chosen': 'a', 'fact_ids': []}]}]}]}}
        mp = os.path.join(td, 'deck-meta.yaml')
        with open(mp, 'w', encoding='utf-8') as fo:
            yaml.safe_dump(deck_m, fo, allow_unicode=True, sort_keys=False)
        t12, h12, s12, s340, n10k = (('home/meta/title', 'COPY-F-NUM', '12 лет'), ('home/hero/h1', 'COPY-F-NUM', '12 лет'), ('home/hero/sub', 'COPY-F-NUM', '12 лет'),
                                     ('home/hero/sub', 'COPY-F-NUM-MISMATCH', '340'), ('home/hero/note', 'COPY-F-NUM-MISMATCH', '10 000'))
        why = {'reason': 'считаем от года основания мастерской', 'by': 'аналитик'}

        def allow_run(records):
            """Сверка copy deck с записями обхода → (находки под обходом, оставшиеся error — тройками «место, правило,
            фрагмент»; результат)."""
            with open(ap, 'w', encoding='utf-8') as fo:
                json.dump(records, fo, ensure_ascii=False)
            _code, r = run(mp, '--allow', ap) if records is not None else run(mp)
            key = lambda f: ('/'.join(f['unit'].split('/')[:3]), f['rule'], f['fragment'])
            return ({key(f) for f in r['findings'] if f.get('allowed')}, {key(f) for f in r['findings'] if f['level'] == 'error'}, r)
        _got, left, _r = allow_run(None)
        check('обходы: без файла пять находок чисел — error (мета, заголовок, две в подзаголовке, сноска)', left == {t12, h12, s12, s340, n10k}, left)
        got, left, r_m = allow_run({'allowed': [dict(why, rule='COPY-F-NUM', where='home/meta', scope='meta')]})
        check('обход мета (where «страница/meta») снимает находку только в мета: то же число в слотах остаётся error',
              got == {t12} and left == {h12, s12, s340, n10k} and not r_m['allow']['notes']
              and [f['allowed']['scope'] for f in r_m['findings'] if f.get('allowed')] == ['meta'], (got, left, r_m['allow']))
        got, left, r_m = allow_run([dict(why, rule='COPY-F-NUM', where='home', reason='запись страницы'), dict(why, rule='COPY-F-NUM', where='home/meta')])
        check('обход: из записей страницы и мета тексту мета достаётся ближняя — запись мета',
              [f['allowed']['where'] for f in r_m['findings'] if f['unit'] == 'home/meta/title'] == ['home/meta'] and got == {t12, h12, s12, s340, n10k}, (got, left))
        got, left, _r = allow_run({'allowed': [dict(why, rule='COPY-F-NUM', where='home', scope='page', value=12)]})
        check('обход с value снимает находки только этого числа: 12 — снято на всей странице, 340 и 10 000 остаются error',
              got == {t12, h12, s12} and left == {s340, n10k}, (got, left))
        got, left, _r = allow_run([dict(why, rule='COPY-F-NUM', where='home', value='10000')])
        check('обход с value: число записи и фрагмент находки сравниваются без разрядов — «10000» снимает «10 000»', got == {n10k} and left == {t12, h12, s12, s340}, (got, left))
        got, left, _r = allow_run([dict(why, rule='COPY-F-NUM-MISMATCH', where='home')])
        check('обход с id находки COPY-F-NUM-MISMATCH: сняты только несовпавшие числа, числа без факта остаются error',
              got == {s340, n10k} and left == {t12, h12, s12}, (got, left))
        got, left, r_m = allow_run([dict(why, rule='COPY-F-NUM', where='home/hero/sub')])
        check('обход без scope, value и fragment — на своём слоте: сняты обе находки семейства в слоте, соседние слоты и мета — error',
              got == {s12, s340} and left == {t12, h12, n10k} and {f['allowed']['scope'] for f in r_m['findings'] if f.get('allowed')} == {'slot'}, (got, left))
        got, left, _r = allow_run([dict(why, rule='COPY-F-NUM', where='home/hero/sub', fragment='12 лет')])
        check('обход с fragment: в слоте снята находка с этим фрагментом, вторая находка слота остаётся error', got == {s12} and left == {t12, h12, s340, n10k}, (got, left))
        got, left, r_m = allow_run({'allowed': [dict(why, rule='COPY-F-NUM', where='home/hero/h1', fragment='12 лет', scope='page', message='число без факта')]})
        check('обход записью находки (copydeck.py check --json): место — слот из where, scope «page» его не расширяет',
              got == {h12} and left == {t12, s12, s340, n10k} and [f['allowed']['scope'] for f in r_m['findings'] if f.get('allowed')] == ['page'], (got, left))
        got, left, r_m = allow_run([dict(why, rule='COPY-F-NUM', where='home', value='двенадцать'), dict(why, rule='COPY-F-CLASS', where='home', value=12)])
        check('обход: value не число и value у маркера класса — записи не действуют',
              not got and r_m['allow']['entries'] == 0 and len(r_m['allow']['notes']) == 2 and all('value' in x for x in r_m['allow']['notes']), r_m['allow'])
        check('обход: число записи против фрагмента находки — разряды, запятая, число целиком',
              allow_number('7 900') == '7900' and allow_number('4,90') == '4.9' and allow_number('12.0') == '12' and allow_number('двенадцать') is None
              and fragment_numbers('от 7 900 ₽ за 12 лет') == {'7900', '12'} and '12' not in fragment_numbers('120 лет')
              and [allow_scope(x) for x in ('home', 'home/meta', 'home/hero/h1', 'home/hero', '')] == ['page', 'meta', 'slot', None, None],
              (allow_number('4,90'), fragment_numbers('от 7 900 ₽ за 12 лет')))
    schema = load_schema()
    svc = Facts({'facts': [], 'never_claim_defaults': 'none',
                 'entities': [{'id': 'svc-lunch', 'type': 'product', 'names': ['Доставка обедов', 'доставки обедов']}]}, schema, False)

    def classes(text, fx):
        F_, _, _ = check_units([unit('t', text)], fx, dt.date(2026, 9, 24))
        return [(f['fragment'], f['claim_class']) for f in F_ if f['rule'] == 'COPY-F-CLASS']
    check('имя услуги из entities вида product с корнем условия покупки — не маркер класса',
          not classes('Доставка обедов в офис — наша главная услуга', svc) and not classes('У доставки обедов есть меню на неделю', svc),
          classes('Доставка обедов в офис — наша главная услуга', svc))
    check('тот же корень вне имени услуги — находка класса purchase-terms',
          [c for _f, c in classes('Доставка по городу — в день заказа', svc)] == ['purchase-terms']
          and [c for _f, c in classes('Доставка обедов в офис — наша главная услуга', Facts({'facts': [], 'never_claim_defaults': 'none'}, schema, False))] == ['purchase-terms'],
          classes('Доставка по городу — в день заказа', svc))

    def names(text, **kw):
        F_, _, _ = check_units([unit('t', text, **kw)], facts, dt.date(2026, 9, 24))
        return [(f['fragment'], f['level']) for f in F_ if f['rule'] == 'COPY-F-NAME']
    check('ведомство в тексте (жалоба в Роскомнадзор, сведения ФНС) — не имя без факта',
          not names('Жалобу на обработку данных можно подать в Роскомнадзор') and not names('Реквизиты проверены по сведениям ФНС'),
          names('Жалобу на обработку данных можно подать в Роскомнадзор') + names('Реквизиты проверены по сведениям ФНС'))
    check('название со словом ведомства и другим словом — имя без факта', [n for n, _l in names('Поставщик плитки — завод ФАС Керамика')] == ['ФАС Керамика'],
          names('Поставщик плитки — завод ФАС Керамика'))
    check('ведомство в списке клиентов — имя без факта, error',
          ('Роскомнадзор', 'error') in names('Нам доверяют Роскомнадзор и другие заказчики'), names('Нам доверяют Роскомнадзор и другие заказчики'))
    check('город из сущности вида place и неизвестный город: первый известен, второй — имя без факта',
          not names('Собираем и отправляем из Казани') and [n for n, _l in names('Собираем и отправляем из Самары')] == ['Самары'],
          (names('Собираем и отправляем из Казани'), names('Собираем и отправляем из Самары')))


EXAMPLE_DECKS = os.path.join(ROOT, '10-templates-recipes', 'examples')
USE_WARNINGS_MAX = 8   # COPY-F-USE на 8 примерах copy deck с местами x-use-always


def _selftest_calibration(check, facts, schema):
    """Калибровки сверки и демо-данные: числа, варианты, «рядом», подпись, классы, языки, слепые зоны."""
    today = dt.date(2026, 9, 24)

    def run(units_, facts_=facts, **kw):
        F_, _, _ = check_units(units_, facts_, today, **kw)
        return F_

    def rules(F_, level=None):
        return {f['rule'] for f in F_ if level is None or f['level'] == level}

    def fx(fact, **extra):
        base = {'kind': 'metric', 'claim_class': ['fact-number'], 'verbatim': ['x'], 'canonical': 'x',
                'source': {'type': 'customer-system', 'who': 'CRM', 'date': '2026-09-01'}, 'verification': {'status': 'verified'},
                'permission': {'status': 'not-required'}, 'lang': 'ru'}
        base.update(fact)
        return Facts(dict({'facts': [base], 'never_claim_defaults': 'none'}, **extra), schema, False)
    # разделитель тысяч по языку, «20-летний», числительные словами
    fen = fx({'id': 'price-m2', 'kind': 'price', 'claim_class': ['price-discount'], 'verbatim': ['₽9,800 per m²'], 'canonical': 'From ₽9,800 per m².',
              'values': [{'value': 9800, 'unit': 'RUB', 'what': 'price per m2', 'comparator': 'gte'}], 'lang': 'en'})
    check('«₽9,800» в английском тексте и факте — 9 800 ₽, подтверждено', not rules(run([unit('e', 'Renovation from ₽9,800 per m²')], fen), 'error'),
          run([unit('e', 'Renovation from ₽9,800 per m²')], fen))
    fen2 = fx({'id': 'flats-en', 'verbatim': ['1,380 apartments'], 'canonical': '1,380 apartments.', 'values': [{'value': 1380, 'unit': 'pcs', 'what': 'apartments'}], 'lang': 'en'})
    check('«1,380 apartments» — тысячи, а не 1,38', not rules(run([unit('e', 'We have renovated 1,380 apartments')], fen2), 'error'))
    f20 = fx({'id': 'exp-20', 'verbatim': ['20 лет в ремонте'], 'canonical': '20 лет в ремонте.', 'values': [{'value': 20, 'unit': 'years', 'what': 'опыт'}]})
    check('«20-летний опыт» — число с единицей лет, подтверждено', not rules(run([unit('r', 'Бригада с 20-летним опытом')], f20), 'error'),
          run([unit('r', 'Бригада с 20-летним опытом')], f20))
    fg5 = fx({'id': 'guar-5', 'kind': 'guarantee', 'claim_class': ['guarantee'], 'verbatim': ['Гарантия 5 лет по договору'], 'canonical': 'Гарантия 5 лет по договору.',
              'values': [{'value': 5, 'unit': 'years', 'what': 'гарантия'}], 'source': {'type': 'contract', 'who': 'заказчик', 'date': '2026-01-15', 'document': 'dogovor.pdf'}})
    F_ = run([unit('r', 'Гарантия пять лет по договору')], fg5)
    check('«пять лет» словами — подтверждено фактом, но COPY-F-NUM-WORDS (пишите цифрами)', 'COPY-F-NUM-WORDS' in rules(F_, 'warning') and not rules(F_, 'error'), F_)
    F_ = run([unit('r', 'Гарантия семь лет по договору')], fg5)
    check('«семь лет» без факта — error, как цифрами', rules(F_, 'error') & {'COPY-F-NUM', 'COPY-F-NUM-MISMATCH'}, F_)
    check('счёт без утверждения («два шага») — без находок', not run([unit('r', 'Два шага до заявки')], fg5))
    # невыбранные варианты — не текст «рядом»
    fnear = fx({'id': 'rating-x', 'kind': 'rating', 'claim_class': ['rating'], 'verbatim': ['4,8 из 5 на Яндекс Картах'], 'canonical': 'Рейтинг 4,8 из 5.',
                'values': [{'value': 4.8, 'unit': 'stars', 'scale': 5, 'count': 214, 'as_of': '2026-09-01'}], 'valid': {'until': '2026-12-01'},
                'source': {'type': 'platform', 'who': 'Яндекс Карты', 'date': '2026-09-01', 'url': 'https://example.org'},
                'use': {'requires_nearby': '«по данным Яндекс Карт»'}})
    deck = {'copy_deck': {'version': 1, 'pages': [{'page_id': 'p', 'page_type': 'landing-lead-services', 'sections': [{'section_id': 'hero', 'section_role': 'hero', 'slots': [
        {'slot_id': 'proof', 'slot_type': 'hero-proof', 'chosen': 'a', 'fact_ids': ['rating-x'], 'variants': [
            {'id': 'a', 'text': 'Рейтинг 4,8 из 5', 'status': 'draft'}, {'id': 'b', 'text': 'Рейтинг 4,8 из 5 по данным Яндекс Карт', 'status': 'draft'}]}]}]}]}}
    us, _ = load_deck(deck, all_variants=True)
    F_ = run(us, fnear)
    check('соседний вариант слота не закрывает «рядом» у выбранного', any(f['rule'] == 'COPY-F-NEARBY' and f['location'].get('variant') == 'a' for f in F_)
          and not any(f['rule'] == 'COPY-F-NEARBY' and f['location'].get('variant') == 'b' for f in F_), [(f['rule'], f['location'].get('variant')) for f in F_])
    # канонические формулировки демо-фактов проходят своё «рядом» («или», признак источника)
    b2p = os.path.join(ROOT, '02-strategy-messaging', 'examples', 'facts-service-renovation.yaml')
    if os.path.exists(b2p):
        fb2 = load_facts(b2p, schema)
        for fid in ('rating-yandex-maps', 'estimate-free'):
            f = fb2.by_id.get(fid)
            F_ = run([unit('c', f['canonical'], fact_ids=[fid], section='s', page='p')], fb2) if f else [{'rule': 'нет факта'}]
            check(f'canonical {fid} проходит своё requires_nearby', f is not None and 'COPY-F-NEARBY' not in rules(F_), [(x['rule'], x['message'][:80]) for x in F_])
    # подпись отзыва против permission.shows
    fatt = fx({'id': 'rev-anna', 'kind': 'testimonial', 'claim_class': ['testimonial-quote'], 'verbatim': ['«Сдали вовремя»'], 'canonical': 'Анна: «Сдали вовремя».',
               'attribution': {'name': 'Анна Кузнецова', 'role': 'генеральный директор'}, 'original_ref': 'x',
               'permission': {'status': 'granted', 'subject': 'Анна', 'form': 'written-email', 'shows': ['first-name']}})
    F_ = run([unit('a', 'Анна Кузнецова, генеральный директор', slot_type='testimonial-attribution', fact_ids=['rev-anna'])], fatt)
    check('подпись с фамилией и должностью при shows [first-name] → COPY-F-PERMISSION', any(f['rule'] == 'COPY-F-PERMISSION' and 'full-name' in f['message'] and 'position' in f['message'] for f in F_), F_)
    F_ = run([unit('a', 'Анна', slot_type='testimonial-attribution', fact_ids=['rev-anna'])], fatt)
    check('подпись в пределах разрешения — без находки', not any(f['rule'] == 'COPY-F-PERMISSION' for f in F_), F_)
    # обещание дохода в будущем без числа, английская превосходная степень
    check('«удвоит выручку» — класс forecast (маркер)', 'forecast' in find_markers('Сервис удвоит вашу выручку'))
    check('«the hottest sauce you\'ll ever taste» — превосходная степень', 'superlative' in find_markers("The hottest sauce you'll ever taste"))
    # вопрос, ипотека в ситуации клиента, падежи имён, площадки, своя шкала
    F_ = run([unit('q', 'Какая гарантия на работы? Спросите прораба.', slot_type='faq-a')])
    check('маркер в вопросе FAQ — не утверждение (info)', not rules(F_, 'error'), F_)
    check('«ипотека» в ситуации клиента — не маркер дохода', 'income-finance' not in find_markers('Аренда и ипотека идут одновременно, бюджет ограничен'))
    check('«ипотека от 5,9 %» — предложение денег, маркер', 'income-finance' in find_markers('Ипотека от 5,9 % на новостройки'))
    fname = Facts({'facts': [{'id': 'foreman', 'kind': 'person', 'claim_class': ['fact-property'], 'verbatim': ['Прораб Сергей Лапин'], 'canonical': 'Прораб Сергей Лапин.',
                              'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
                              'permission': {'status': 'granted', 'subject': 'Сергей Лапин', 'form': 'written-email', 'shows': ['full-name', 'position']}, 'lang': 'ru'}],
                   'entities': [{'id': 'p-lapin', 'type': 'person', 'names': ['Сергей Лапин'], 'fact_id': 'foreman'}], 'never_claim_defaults': 'none'}, schema, False)
    F_ = run([unit('n', 'Работу принимает у Сергея Лапина технадзор')], fname)
    check('имя в падеже («Сергея Лапина») — известно', not any(f['rule'] == 'COPY-F-NAME' for f in F_), F_)
    check('площадка CamelCase («RuStore») — не имя клиента', not any(f['rule'] == 'COPY-F-NAME' for f in run([unit('n', 'Приложение есть в RuStore и Google Play')])))
    check('своя шкала бренда («острота 5 из 5») — не рейтинг', not any(f['rule'] == 'COPY-F-RATING' for f in run([unit('n', 'Острота 5 из 5, соус на хабанеро')])))
    # перевод факта с объектом счёта и оговоркой; запрет на языке страницы
    ftr = fx({'id': 'flats', 'verbatim': ['1 146 квартир'], 'canonical': '1 146 квартир.', 'values': [{'value': 1146, 'unit': 'pcs', 'what': 'квартиры', 'as_of': '2026-09'}],
              'use': {'requires_nearby': '«по данным CRM»'},
              'translations': {'en': {'verbatim': ['1,146 apartments handed over'], 'what': 'apartments', 'requires_nearby': '«as of September 2026»'}}})
    F_ = run([unit('e', '1,146 apartments handed over, as of September 2026', fact_ids=['flats'], section='s', page='p')], ftr)
    check('английский текст — объект счёта и «рядом» из translations.en', not rules(F_, 'error') and 'COPY-F-NEARBY' not in rules(F_), F_)
    F_ = run([unit('e', '1,146 apartments handed over', fact_ids=['flats'], section='s', page='p')], ftr)
    check('без английской оговорки — COPY-F-NEARBY с требованием translations.en', any(f['rule'] == 'COPY-F-NEARBY' and 'as of' in f['message'] for f in F_), F_)
    fnv = Facts({'facts': [], 'never_claim_defaults': 'none', 'never_claim': [
        {'id': 'nc-eyes', 'text': 'обещания про зрение', 'claim_class': ['health'], 'patterns': ['глаз', 'зрени'], 'lang': 'ru', 'lift': 'never',
         'translations': {'en': {'text': 'eye promises', 'patterns': ['\\beye']}}}]}, schema, False)
    check('запрет на языке страницы — английский перевод ловит «eye strain»', 'COPY-F-NEVER' in rules(run([unit('e', 'No more eye strain in the evening')], fnv), 'error'))
    check('русский запрет не ищется в английском тексте', 'COPY-F-NEVER' not in rules(run([unit('e', 'Glazed ceramic tiles')], Facts({'facts': [], 'never_claim_defaults': 'none', 'never_claim': [
        {'id': 'nc-x', 'text': 'x', 'patterns': ['glaz'], 'lang': 'ru', 'lift': 'never'}]}, schema, False))))
    # безглагольное обещание, пересказ запрета с придаточным
    check('«Каждый вечер. Без исключений.» — обещание (класс guarantee)', 'guarantee' in find_markers('Фото. Каждый вечер. Без исключений.'))
    fpar = Facts({'facts': [], 'never_claim_defaults': 'none', 'never_claim': [{'id': 'nc-budget', 'text': 'смета никогда не меняется', 'claim_class': ['guarantee'],
                                                                                'patterns': ['смет\\w*\\s+не\\s+вырос'], 'lift': 'never'}]}, schema, False)
    check('пересказ запрета с придаточным («смета, которую мы составили, не выросла») → COPY-F-NEVER',
          'COPY-F-NEVER' in rules(run([unit('p', 'Смета, которую мы составили, не выросла ни разу')], fpar), 'error'))
    # правила права
    rs, _e = load_rules([RULES_PATH])
    R = {r['id']: r for r in rs}
    if R:
        empty = Facts({'facts': [], 'never_claim_defaults': 'none'}, schema, False)
        F_ = run([unit('f', 'Замер и смета — бесплатно в черте города')], empty, rules=[R['COPY-L-FREE-01']], ctx=legal_ctx())
        check('«бесплатно в черте города» — условие рядом, COPY-L-FREE-01 молчит', 'COPY-L-FREE-01' not in rules(F_), F_)
        check('COPY-L-RET-02 — error', R['COPY-L-RET-02']['level'] == 'error')
        u_srv = unit('o', 'Информация на сайте не является публичной офертой', page_type='landing-lead-services')
        u_prd = unit('o', 'Информация на сайте не является публичной офертой', page_type='landing-product')
        check('COPY-L-OFFER-01 не на услугах, на товарах — сигнал',
              'COPY-L-OFFER-01' not in rules(run([u_srv], empty, rules=[R['COPY-L-OFFER-01']], ctx=legal_ctx()))
              and 'COPY-L-OFFER-01' in rules(run([u_prd], empty, rules=[R['COPY-L-OFFER-01']], ctx=legal_ctx())))
        check('COPY-L-JOB-01 — вакансия с полом, возрастом, пропиской → error', 'COPY-L-JOB-01' in rules(run([unit('j', 'Требуется девушка до 35 лет с пропиской', page_type='careers-page')], empty,
                                                                                                                 rules=[R['COPY-L-JOB-01']], ctx=legal_ctx()), 'error'))
        check('COPY-L-JOB-01 не на странице другого типа', 'COPY-L-JOB-01' not in rules(run([unit('j', 'Требуется девушка до 35 лет с пропиской', page_type='landing-product')], empty,
                                                                                                    rules=[R['COPY-L-JOB-01']], ctx=legal_ctx())))
    # демо-данные (example: true) — без --final сигнал, с --final error
    fdemo = fx({'id': 'demo-n', 'verbatim': ['120 клиентов'], 'canonical': '120 клиентов.', 'values': [{'value': 120, 'unit': 'pcs', 'what': 'клиенты'}], 'example': True})
    F0 = run([unit('d', '120 клиентов', fact_ids=['demo-n'])], fdemo)
    F1 = run([unit('d', '120 клиентов', fact_ids=['demo-n'])], fdemo, final=True)
    check('демо-факт example: true — info без --final, error с --final (COPY-F-EXAMPLE)',
          any(f['rule'] == 'COPY-F-EXAMPLE' and f['level'] == 'info' for f in F0) and any(f['rule'] == 'COPY-F-EXAMPLE' and f['level'] == 'error' for f in F1), (F0, F1))
    fdemo_file = fx({'id': 'n', 'verbatim': ['120 клиентов'], 'canonical': '120 клиентов.', 'values': [{'value': 120, 'unit': 'pcs', 'what': 'клиенты'}]}, example=True)
    check('демо-файл фактов (example у файла) — --final error', any(f['rule'] == 'COPY-F-EXAMPLE' and f['level'] == 'error' for f in run([unit('d', '120 клиентов', fact_ids=['n'])], fdemo_file, final=True)))
    # места use — ориентир; x-use-always; 8 примеров copy deck
    fuse = fx({'id': 'g3', 'kind': 'guarantee', 'claim_class': ['guarantee'], 'verbatim': ['гарантия 3 года'], 'canonical': 'Гарантия 3 года.',
               'values': [{'value': 3, 'unit': 'years', 'what': 'гарантия'}], 'source': {'type': 'contract', 'who': 'заказчик', 'date': '2026-01-15', 'document': 'd.pdf'},
               'use': {'section_roles': ['guarantee'], 'slot_types': ['guarantee-text']}})
    check('use: факт вне use — warning COPY-F-USE, не error', 'COPY-F-USE' in rules(run([unit('u', 'Гарантия 3 года', fact_ids=['g3'], slot_type='body', section_role='benefits')], fuse), 'warning'))
    check('use: мета, FAQ, статья — места x-use-always, COPY-F-USE нет',
          not any('COPY-F-USE' in rules(run([unit('u', 'Гарантия 3 года', fact_ids=['g3'], slot_type=st, section_role=ro)], fuse))
                  for st, ro in (('meta-description', None), ('faq-a', 'faq'), ('article-paragraph', 'article-body'), ('body', 'how-it-works'))))
    if os.path.isdir(EXAMPLE_DECKS):
        n_use, n_err, n = 0, [], 0
        for fn in sorted(os.listdir(EXAMPLE_DECKS)):
            if not fn.endswith('.yaml'):
                continue
            path = os.path.join(EXAMPLE_DECKS, fn)
            units_, _fmt, meta = load_input(path, 'deck')
            fp = os.path.normpath(os.path.join(EXAMPLE_DECKS, meta.get('facts_ref') or ''))
            if not os.path.exists(fp):
                continue
            n += 1
            ctx_ = legal_ctx(meta.get('jurisdiction'), _as_list(meta.get('legal_category') or ['general']))
            F_, _, _ = check_units(units_, load_facts(fp, schema), today, load_rules([RULES_PATH])[0], ctx=ctx_)
            n_use += sum(1 for f in F_ if f['rule'] == 'COPY-F-USE')
            n_err += [(fn, f['rule'], f['fragment']) for f in F_ if f['level'] == 'error']
        check(f'use: 8 примеров copy deck — COPY-F-USE ≤ {USE_WARNINGS_MAX}, 0 error', n == 8 and n_use <= USE_WARNINGS_MAX and not n_err, (n, n_use, n_err[:6]))


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
    F, _, _ = check_units([unit('d', 'Цена — 8 900 ₽', fact_ids=['F1'], slot_type='card-body')], facts, dt.date(2026, 9, 24))
    check('алиас F1 принят; слот вне use → COPY-F-USE warning', errs(F) == [] and any(f['rule'] == 'COPY-F-USE' for f in F), F)
    f3 = Facts(dict(facts.data, facts=list(facts.data['facts']) + [{'id': 'clients-approx', 'kind': 'metric', 'claim_class': ['fact-number'],
        'verbatim': ['около 200 клиентов'], 'canonical': 'Около 200 клиентов.', 'values': [{'value': 200, 'unit': 'pcs', 'what': 'клиенты', 'approx': True}],
        'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
        'permission': {'status': 'not-required'}, 'lang': 'ru'}]), schema, True)
    check('приблизительный факт «около 200» → точное «200 клиентов» — ошибка', errs(rules_of('200 клиентов', f3)) != [], rules_of('200 клиентов', f3))
    check('приблизительный факт → «около 200 клиентов» — ок', errs(rules_of('Около 200 клиентов', f3)) == [], rules_of('Около 200 клиентов', f3))
    # --- регрессии сверки
    F = rules_of('−10 % до 31 октября 2026 года', facts)
    check('регрессия: минус U+2212 в дословном факте — без EXTENDS', not [f for f in F if f['rule'] == 'COPY-F-EXTENDS'], F)
    f2 = Facts(dict(facts.data, never_claim=list(facts.data['never_claim']) + [{'id': 'nc-budget', 'text': 'смета никогда не меняется', 'claim_class': ['guarantee'], 'patterns': ['смет\\w*\\s+не\\s+вырос'], 'lift': 'with-fact'}]), schema, True)
    F = rules_of('«Сдали за 47 рабочих дней… Смета не выросла ни на рубль»', f2)
    check('регрессия: запрет голоса компании в цитате отзыва с разрешением → warning COPY-F-TYPICALITY, не error',
          not errs(F) and any(f['rule'] == 'COPY-F-TYPICALITY' for f in F), F)
    F = rules_of('Смета не выросла ни на рубль — гарантируем!', f2)
    check('тот же запрет голосом компании → COPY-F-NEVER', 'COPY-F-NEVER' in errs(F), F)
    # --- цифры в именах сущностей — часть имени, а не число утверждения
    addr = {'id': 'office', 'kind': 'company', 'claim_class': ['company-details'], 'verbatim': ['Садовая улица, 12'], 'canonical': 'Офис — Садовая улица, 12.',
            'source': {'type': 'customer-message', 'who': 'заказчик', 'date': '2026-09-24'}, 'verification': {'status': 'stated'},
            'permission': {'status': 'not-required'}, 'lang': 'ru'}
    f_addr = Facts(dict(facts.data, facts=list(facts.data['facts']) + [addr]), schema, True)
    f_ent = Facts(dict(f_addr.data, entities=list(facts.data['entities']) + [{'id': 'atlas', 'type': 'brand', 'names': ['Атлас', 'Атлас Р 45', 'Р 45', 'К45 С']},
                                                                              {'id': 'vega', 'type': 'brand', 'names': ['Вега', '707']}]), schema, True)
    num_rules = lambda F: sorted({f['rule'] for f in F if f['rule'] in ('COPY-F-NUM', 'COPY-F-NUM-MISMATCH')})
    check('число из имени модели без сущности → сверяется с числом другого факта (контроль)',
          num_rules(rules_of('Атлас Р 45 — подготовка к сезону', f_addr)) != [], rules_of('Атлас Р 45 — подготовка к сезону', f_addr))
    got = [num_rules(rules_of(t, f_ent)) for t in ('Атлас Р 45 — подготовка к сезону', 'Атлас Р\u00a045 в цехе', 'Вега 707 после сборки', 'К45 С — новая серия')]
    check('цифры внутри имён сущностей entities[].names числом не считаются (пробел любой, имя из одних цифр)', got == [[], [], [], []], got)
    F = rules_of('Атлас Р 45 — 15 лет на рынке', f_ent)
    check('число рядом с именем сущности сверяется как раньше', [f['fragment'] for f in F if f['rule'] in ('COPY-F-NUM', 'COPY-F-NUM-MISMATCH')] == ['15 лет'], F)
    check('имя сущности — целым словом: «Р 450» и «1707» под маску не попадают',
          f_ent.name_spans('Р 450 и 1707, а ещё Р 45.') == [(20, 24)], f_ent.name_spans('Р 450 и 1707, а ещё Р 45.'))
    # --- «рядом должно стоять»: фрагмент сравнивается словами, без знаков препинания и вида пробелов
    req = '«за сезон, на май 2026»'
    check('requires_nearby: тире вместо запятой и неразрывный пробел — та же формулировка',
          nearby_ok(req, unit('n', 'Сдали 120 объектов за сезон — на\u00a0май 2026'), []) and nearby_ok(req, unit('n', 'Сдали 120 объектов за сезон, на май 2026'), []))
    check('requires_nearby: другие слова или другой порядок — требование не выполнено',
          not nearby_ok(req, unit('n', 'Сдали 120 объектов за месяц — на май 2026'), []) and not nearby_ok(req, unit('n', 'На май 2026 — 120 объектов за сезон'), []))
    # --- ложные срабатывания
    bad = []
    for p in FP_PHRASES:
        F = rules_of(p, facts)
        if any(f['level'] in ('error', 'warning') for f in F):
            bad.append((p, [(f['rule'], f['fragment']) for f in F]))
    check(f'{len(FP_PHRASES)} фраз без фактов — ни error, ни warning', not bad, bad)
    # --- входы
    cmd_ = '# Тексты страницы home\n\n## hero\n[headline] approved: Лампа\n[cta-label] assumed: Забронировать за 990 ₽\n\n## specs\n[spec-row]: Сборка — Казань\n## ?\n[?]: Новинка\n'
    check('copy.md входа холста: формат узнан', detect_format('copy.md', cmd_) == 'copy-md')
    us = load_copy_md(cmd_)
    check('copy.md: 4 единицы, роль и тип слота — по словарю site', [(u['section'], u['section_role'], u['slot_type']) for u in us] ==
          [('hero', 'hero', 'headline'), ('hero', 'hero', 'cta-label'), ('specs', 'specs', 'spec-row'), ('?', None, None)], us)
    deck = {'copy_deck': {'version': 0, 'pages': [{'page_id': 'home', 'page_type': 'landing-waitlist', 'sections': [
        {'section_id': 'hero', 'slots': [{'slot_id': 'h1', 'slot_type': 'headline', 'variants': [{'id': 'a', 'text': 'A'}, {'id': 'b', 'text': 'B'},
                                                                                                  {'id': 'c', 'text': 'C', 'status': 'rejected'}], 'chosen': 'b', 'fact_ids': [], 'claim_flags': []}]}]}]}}
    us, _ = load_deck(deck)
    check('copy deck v0: берётся chosen', [u['text'] for u in us] == ['B'], us)
    us, _ = load_deck(deck, all_variants=True)
    check('copy deck --all-variants: живые варианты, отклонённый не сверяется, невыбранные помечены',
          [(u['text'], u['alt']) for u in us] == [('A', True), ('B', False)], [(u['text'], u['alt']) for u in us])
    us = load_html('<html><head><title>Кварц</title><meta name="description" content="Лампа за 8 900 ₽"></head><body><h1>Лампа</h1><p>Цена 8 900 ₽</p><blockquote>Отличная лампа, всем советую</blockquote><script>var x=5</script></body></html>')
    check('HTML: title, description, h1, p, blockquote; без script', [u['slot_type'] for u in us] == ['meta-title', 'meta-description', 'headline', 'body', 'testimonial-quote'], [(u['slot_type'], u['text']) for u in us])
    us = load_html('<!doctype html><html><head><title>Главная · 1440</title>\n<!-- dc_to_html: статичная копия артборда Home-1440.dc.html; рамка 1440×900 -->'
                   '<style>h1{margin:0}</style></head><body><h1>Лампа</h1><p>Цена 8 900 ₽</p></body></html>')
    check('HTML статичной копии артборда: служебный title не читается, текст страницы — читается',
          [(u['slot_type'], u['text']) for u in us] == [('headline', 'Лампа'), ('body', 'Цена 8 900 ₽')], [(u['slot_type'], u['text']) for u in us])
    check('словарь site: id мест use (lint-facts) — типы страниц, роли, слоты вида text', {'faq-page', 'case-page'} <= load_vocab().get('page_types', set())
          and 'offer' in load_vocab().get('section_roles', set()) and 'disclaimer' in load_vocab().get('slot_types', set()))
    lf = {}
    with tempfile.TemporaryDirectory() as td:
        fp, jp = os.path.join(td, 'facts.yaml'), os.path.join(td, 'lint-facts.json')
        with open(fp, 'w', encoding='utf-8') as fo:
            yaml.safe_dump(facts.data, fo, allow_unicode=True, sort_keys=False)
        for final in (False, True):
            cmd_lint_facts(argparse.Namespace(input=fp, schema=SCHEMA_PATH, today='2026-09-24', final=final, json=jp, quiet=True))
            with open(jp, encoding='utf-8') as fi:
                lf[final] = {(x['rule'], x['level']) for x in json.load(fi)['findings'] if x['unit'] == 'fact:review-pending'}
    check('lint-facts: разрешение pending — warning до --final, с --final — error',
          lf[False] == {('COPY-F-PERMISSION', 'warning')} and lf[True] == {('COPY-F-PERMISSION', 'error')}, lf)
    _selftest_calibration(check, facts, schema)
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
    _selftest_binding(check, facts)   # привязка к copy deck, обходы, копия артборда, имена услуг и ведомств
    _selftest_legal(check)   # правовой модуль
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


# ================================================================ CLI
def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if '--selftest' in argv:
        return cmd_selftest()
    cmds = {'check', 'inventory', 'lint-facts', 'rules-schema'}
    cmd = argv.pop(0) if argv and argv[0] in cmds else 'check'
    p = argparse.ArgumentParser(prog=f'claims_check.py {cmd}', description=__doc__.split('\n')[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog='подкоманды: check INPUT (по умолчанию) — сверка текста с фактами; lint-facts FACTS — проверка инвентаря фактов\n'
                                       'обслуживание базы (в маршруте этапов проекта не участвует): inventory INPUT — утверждения по классам и\n'
                                       '  доля с видимым источником (замеры корпуса страниц); rules-schema — JSON Schema правил права')
    if cmd == 'rules-schema':
        return cmd_rules_schema(p.parse_args(argv))
    p.add_argument('input')
    p.add_argument('--json')
    p.add_argument('--md')
    p.add_argument('--quiet', action='store_true')
    p.add_argument('--today')
    p.add_argument('--schema', default=SCHEMA_PATH)
    if cmd in ('check', 'inventory'):
        p.add_argument('--format', default='auto', choices=['auto', 'deck', 'copy-md', 'md', 'text', 'html'])
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
        p.add_argument('--legal-only', action='store_true', help='в отчёт — только находки правил права (claims-rules.yaml, --rules)')
        p.add_argument('--deck', help='copy deck: вход без слотов (HTML, Markdown, текст) привязывается к его слотам по тексту')
        p.add_argument('--allow', help='обходы сверки: JSON с полем allowed (вывод copydeck.py validate --final --json) или список '
                                       'записей {rule, where, reason, by[, value][, fragment]}; место записи — слот, мета или '
                                       'страница (where); находка под обходом — info с причиной')
    if cmd in ('check', 'lint-facts'):
        p.add_argument('--final', action='store_true', help='ворота публикации: демо-данные (example: true) — error; '
                                                            'у lint-facts ещё разрешение pending — error')
    a = p.parse_args(argv)
    try:
        if cmd == 'check':
            return cmd_check(a)
        if cmd == 'inventory':
            return cmd_inventory(a)
        if cmd == 'lint-facts':
            return cmd_lint_facts(a)
    except SystemExit as e:
        if isinstance(e.code, str):             # текст вместо кода — ошибка вызова, входа или окружения
            print('claims_check:', e.code, file=sys.stderr)
            return 2
        raise
    except (OSError, ValueError) as e:
        print('claims_check:', e, file=sys.stderr)
        return 2
    return 2


if __name__ == '__main__':
    sys.exit(main())
