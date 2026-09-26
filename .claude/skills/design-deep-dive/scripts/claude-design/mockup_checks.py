#!/usr/bin/env python3
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
# mockup_checks.py — копия БЕЗ ПРАВОК КОДА (26.09.2026) утилиты проверок макета v1.0 от 24.09.2026, md5 оригинала 7dde044e876c83b9ad6e5a03d212af5c.
# Описание и пороги — claude-design-research/06-design-process/04-checks.md (§3, §4); бан-лист — 05-default-look.md.
# Брать: `page` (приметы «дефолтного вида» с ключами --allow; честность: числа против фактов, текст против copy deck, подписи и
#   alt против списка ассетов, сток и хотлинк, «рыба», отзывы; мобильная: навигация, тело 16 px, вылет, строки h1; наложения
#   текста; контраст тёплых палитр), `resize` (1440 → 390 → 1440 без перезагрузки), `selftest`.
# Что убрать при адаптации:
#   1. Подкоманда `watch` — сторож потока CLI другого исполнителя, НЕ НУЖЕН: функции resolve_stream, watch, cmd_watch, парсер
#      `watch` в main(), раздел `watch` в докстринге, проверки разбора потока в cmd_selftest.
#   2. id проверок K3-* и F-* ПЕРЕИМЕНОВАТЬ при уборке по таблице соответствий: на них опираются маркеры site
#      (09-ai-generation-evaluation/ai-landing-markers.yaml, 07-seo-geo-performance-analytics/page-gates.yaml) и реестр клише creative
#      (08-uniqueness-anti-slop/cliche-registry.yaml, 09-ai-execution-evaluation/effect-gates.yaml). Значения ALLOW_KEYS не менять —
#      их использует арт-дирекция creative (разрешённые брифом приметы).
#   3. Имя исполнителя в докстринге, help и текстах находок; пример --ignore-selector для бейджа хостинга публичных страниц; ссылки на
#      документы и опыты старой базы (08-director-loop-qa/…, ACCEPTANCE H5, E/01, W1–W3, G/01–G/04) → 06-design-process/04-checks.md.
#   4. safe_root: список служебных папок привести к нужным (в нём есть папка настроек другого CLI).
#   5. Входы --facts / --assets-readme ждут markdown-таблицы (колонка «Факт…», колонки «Файл», «Подпись», «Alt»); YAML фактов text —
#      переводить в таблицу или научить утилиту.
# Зависимости: Python 3.10+, Playwright + Chromium; браузер — один за раз, свободная память ≥ 2 ГБ (--min-free-gb).
# ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
"""k3_checks.py — проверки арт-директора для сборок Kimi K3: приметы K3, выдумки, мобильная версия, сторож потока.

Агент G (волна 2), 2026-09-24. Модель не вызывается. Python 3.10+; для `page` — playwright (Chromium) из системы.
Место в цикле: `08-director-loop-qa/02-checks-k3.md` (что ловит, пороги, что делать при провале).
Дополняет, а не дублирует: shot.py v3 (F) — вылет, битые/внешние картинки, alt, мелкий текст, цели, шрифты, lang, h1;
ui_audit.py (ui-research) — отступы, контраст, состояния, фокус; Gesso `anti-slop` и `impeccable detect` — слоп-признаки.
Здесь — то, чего нет у них: почерк K3 и выдумки по брифу.

Подкоманды:
  page <url|file.html|dir> [--views 1440x900,390x844] [--facts brief/facts.md] [--copy brief/copy.md]
       [--assets-readme assets/README.md] [--src DIR] [--allow warm,serif,...] [--ignore-selector CSS]
       [--block-external | --allow-external] [--shots DIR] [--json OUT.json] [--md OUT.md] [--min-free-gb 2]
       приметы K3 (K3-*), выдумки (F-*), мобильная версия (M-*), контраст тёплых палитр; exit 0 — нет critical/major,
       2 — есть, 1 — ошибка, 3 — мало свободной памяти (браузер не запускался)
  watch <stream.jsonl | <проект>.runs/> [--running] [--idle-warn 600] [--idle-act 1200] [--loop 4] [--churn 8]
       [--iter N] [--frames K] [--allowed-packages a,b] [--expect-first Read,Skill,...] [--forbid-tools ...]
       разбор потока `kimi -p --output-format stream-json` (идёт или закончен): первый вызов, запрещённые инструменты
       и команды, петли, долгие шаги, чтение кадров итерации; вердикт ok | warn | act | done; exit 0/0/2/0
  resize <url|file> [--desktop 1440x900] [--mobile 390x844] [--wait-ms 1000] [--shots DIR]
       ресайз без перезагрузки 1440 → 390 → 1440 (ACCEPTANCE H5; W3: hero ≥ 4 с чёрный после ресайза): вылет, навигация,
       медиа первого экрана показано за 1 с, кадр после возврата совпадает с исходным; exit 0 pass / 2 fail
  selftest  офлайн-проверки (цвет, контраст, числа, текст, разбор потока)

Приметы K3 (источники: E/01 Kilo 9 задач, W1–W3, ui 11/04; `--allow` снимает примету, если бриф её заказал):
  K3-BG-WARM warm        тонированный тёплый фон страницы/секций (OKLCH h 45–115°, C 0.006–0.08, L ≥ 0.88 или ≤ 0.30)
  K3-ACCENT-WORD accent-word  одно слово заголовка выделено (курсив, цвет, градиент, другой шрифт, подчёркивание)
  K3-SERIF-DISPLAY serif антиква в h1/h2 (+ пара с Inter/Geist/Roboto — «Fraunces + Inter»)
  K3-EYEBROW eyebrow     капс-надзаголовок с разрядкой над > 1/3 заголовков (ui 11/04 m30)
  K3-HERO-OVERLAY photo-hero  фото или видео на весь hero под тёмной вуалью
  K3-HERO-CENTER center-hero  hero ≥ 90 % высоты окна, всё по центру (Hallmark гейт 6; не ловит ни один детектор D/02)
  K3-STATS-ROW stats     ряд из 3–5 крупных чисел (+ числа уходят в сверку с facts.md)
  K3-THREE-CARDS cards   три одинаковые карточки в ряд (m17)
  K3-GRADIENT-TEXT gradient, K3-GLASS glass, K3-PILL pill, K3-META-DOTS dots, K3-ARROWS arrows, K3-MONO-LABELS mono,
  K3-NUMBERED numbered, K3-MARQUEE marquee, K3-DRAWN-CHROME chrome, K3-CAPS caps — шаблонный хром (m3, m8, m15,
  m30–m34), K3-WARM-CONTRAST — текст на тёплом фоне или тёплым цветом ниже 4.5:1 (3:1 крупный).
Выдумки: F-UNSPLASH и F-STOCK (ID фото Unsplash и стоковые/заглушечные хосты в DOM и исходниках), F-HOTLINK, F-CAPTION
  (подпись/alt против assets/README.md), F-NUMBERS (число на странице, которого нет в facts.md и copy.md), F-COPY (текст не из
  copy.md), F-FILLER (lorem, Feature 1, John Doe, example.com), F-QUOTE (отзыв без источника).
Мобильная (вьюпорт < 768): M-NAV (навигация не видна), M-BODY-16 (тело < 16 px), M-OVERFLOW (горизонтальная прокрутка),
  M-H1-LINES (h1 > 4 строк). Вёрстка: V-OVERLAP (строки текста накладываются ≥ 30 % — плашка на H1, W2; календарь K3, E/01).
Слепая зона: E-LOW-DOM — < 12 текстовых узлов или canvas/видео > 50 % первого экрана: проверки по разметке неполны.
Публичные страницы Kimi (*.kimi.page, *.ok.kimi.link): --ignore-selector '[class*=kimi-brand], [class*=kimi-badge]' (бейдж хостинга).
Проверено: 99-raw/experiments/G/01 (свои страницы: 36 из 37 подброшенных, 0 ложных на чистой), G/02 (Gesso 4, impeccable 12
  из 36), G/03 (4 публичные страницы K3), G/04 (watch: 9 потоков).
Приватность: статический обход только внутри указанной папки; `/`, домашняя папка и её служебные подпапки отклоняются
  (урок B2/05). Для локальных целей внешние запросы по умолчанию блокируются (детерминизм, ничего не уходит в сеть).
"""
import argparse, colorsys, json, math, os, re, statistics, sys, time, unicodedata
from datetime import datetime, timezone
from urllib.parse import urlparse

VERSION = '1.0'

# ---------------------------------------------------------------- справочники
SERIF_FAMILIES = {  # display-антиквы, типичные для LLM-лендингов 2025–2026 и K3 (E/01, W2, taste-skill, impeccable)
    'fraunces', 'instrument serif', 'playfair display', 'playfair', 'cormorant', 'cormorant garamond', 'dm serif display',
    'dm serif text', 'newsreader', 'eb garamond', 'garamond', 'libre caslon', 'libre caslon display', 'libre baskerville',
    'lora', 'merriweather', 'crimson pro', 'crimson text', 'source serif', 'source serif 4', 'source serif pro', 'pt serif',
    'noto serif', 'georgia', 'times new roman', 'times', 'bodoni moda', 'bodoni', 'didot', 'spectral', 'literata',
    'young serif', 'gloock', 'bitter', 'roboto serif', 'ibm plex serif', 'tinos', 'liberation serif', 'dejavu serif',
    'gelasio', 'petrona', 'besley', 'rufina', 'marcellus', 'cinzel', 'prata', 'yeseva one', 'abril fatface', 'alice',
    'lusitana', 'sorts mill goudy', 'goudy', 'baskerville', 'caslon', 'canela', 'tiempos', 'gt sectra', 'editorial new',
    'pp editorial new', 'ogg', 'recoleta', 'zodiak', 'erode', 'sentient', 'gambetta', 'boska', 'amiri', 'playfair display sc',
}
SANS_DEFAULTS = {'inter', 'geist', 'roboto', 'sora', 'space grotesk', 'plus jakarta sans', 'manrope', 'dm sans', 'poppins',
                 'outfit', 'urbanist', 'montserrat', 'open sans', 'helvetica', 'arial', 'system-ui', '-apple-system',
                 'segoe ui', 'lato', 'nunito', 'work sans'}
MONO_FAMILIES = {'jetbrains mono', 'ibm plex mono', 'geist mono', 'space mono', 'dm mono', 'fira code', 'fira mono',
                 'roboto mono', 'source code pro', 'ubuntu mono', 'courier new', 'courier', 'menlo', 'monaco', 'consolas',
                 'sf mono', 'dejavu sans mono', 'liberation mono', 'monospace', 'ui-monospace', 'berkeley mono',
                 'commit mono', 'martian mono', 'azeret mono', 'overpass mono', 'red hat mono'}
STOCK_PATTERNS = [  # (id, regex) — хотлинк стоковых фото и сервисов-заглушек (W2: «Amalfi Coast», DesignArena: ID по памяти)
    ('unsplash', r'(?:images|plus)\.unsplash\.com/(?:photo|premium_photo)-[0-9]+-[0-9a-f]{6,}|source\.unsplash\.com/[^\s"\')]+'
                 r'|unsplash\.com/photos/[\w-]+|unsplash\.it/[^\s"\')]+'),
    ('pexels', r'images\.pexels\.com/photos/\d+|pexels\.com/photo/[\w-]+'),
    ('pixabay', r'cdn\.pixabay\.com/[^\s"\')]+|pixabay\.com/get/[^\s"\')]+'),
    ('picsum', r'picsum\.photos/[^\s"\')]*'),
    ('placeholder', r'(?:via\.)?placeholder\.com/[^\s"\')]*|placehold\.(?:co|it)/[^\s"\')]*|dummyimage\.com/[^\s"\')]*'
                    r'|fakeimg\.pl/[^\s"\')]*|placekitten\.com/[^\s"\')]*|loremflickr\.com/[^\s"\')]*|lorempixel\.com/[^\s"\')]*'),
    ('avatar-service', r'i\.pravatar\.cc/[^\s"\')]*|pravatar\.cc/[^\s"\')]*|randomuser\.me/api/portraits/[^\s"\')]+'
                       r'|ui-avatars\.com/api[^\s"\')]*|api\.dicebear\.com/[^\s"\')]+|thispersondoesnotexist\.com'),
    ('stock-site', r'(?:media\.)?istockphoto\.com/[^\s"\')]+|(?:image\.)?shutterstock\.com/[^\s"\')]+'
                   r'|media\.gettyimages\.com/[^\s"\')]+|(?:img\.|image\.)?freepik\.com/[^\s"\')]+|stock\.adobe\.com/[^\s"\')]+'
                   r'|burst\.shopifycdn\.com/[^\s"\')]+|cdn\.stocksnap\.io/[^\s"\')]+'),
]
FILLER_PATTERNS = [r'\blorem ipsum\b', r'\bdolor sit amet\b', r'\bFeature [1-9]\b', r'\bJohn Doe\b', r'\bJane Doe\b',
                   r'\bexample@(?:example|email|mail)\.com\b', r'\bAcme (?:Inc|Corp)\b', r'\bYour Company\b', r'\bCompany Name\b',
                   r'\bTrusted by\b', r'\bComing soon\b', r'\bTODO\b', r'Название компании', r'Текст-заглушка', r'Иван Иванов',
                   r'\$1,234\.56', r'\b123 Main St']
TEXT_EXT = ('.html', '.htm', '.css', '.scss', '.sass', '.less', '.js', '.mjs', '.cjs', '.jsx', '.ts', '.tsx', '.vue',
            '.svelte', '.astro', '.md', '.mdx', '.json', '.txt')
SKIP_DIRS = {'node_modules', '.git', '.next', '.nuxt', '.svelte-kit', '.venv', 'venv', '__pycache__', '.cache',
             'screenshots', '.turbo', 'coverage'}
ALLOW_KEYS = {'warm', 'accent-word', 'serif', 'eyebrow', 'photo-hero', 'center-hero', 'stats', 'cards', 'gradient', 'glass',
              'pill', 'dots', 'arrows', 'mono', 'numbered', 'marquee', 'chrome', 'caps', 'external'}
SEV_ORDER = {'critical': 0, 'major': 1, 'minor': 2, 'info': 3}


# ---------------------------------------------------------------- цвет: sRGB → OKLab/OKLCH, контраст WCAG 2
def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklch(rgb):
    r, g, b = (_lin(x) for x in rgb[:3])
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    A = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    B = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    C = math.hypot(A, B)
    H = math.degrees(math.atan2(B, A)) % 360
    return round(L, 4), round(C, 4), round(H, 1)


def hexs(rgb):
    return '#%02x%02x%02x' % tuple(int(round(x)) for x in rgb[:3])


def luminance(rgb):
    r, g, b = (_lin(x) for x in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg, bg):
    """WCAG 2 contrast; fg может быть RGBA — альфа компонуется поверх bg (ui 13: контраст после композитинга)."""
    if len(fg) > 3 and fg[3] < 1:
        a = fg[3]
        fg = [fg[i] * a + bg[i] * (1 - a) for i in range(3)]
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return round((hi + 0.05) / (lo + 0.05), 2)


def warm_class(rgb):
    """'light' (крем, беж, тёплый off-white), 'dark' (коричнево-чёрный) или None. Пороги — по E/01 (#f4f4ec h≈107,
    #14140c) и ui 11/04 (#F4F1EA h≈84); насыщенный брендовый цвет (C > 0.08) — не «тонировка»."""
    L, C, H = oklch(rgb)
    if not (45 <= H <= 115 and 0.006 <= C <= 0.08):
        return None
    if L >= 0.88:
        return 'light'
    if L <= 0.30:
        return 'dark'
    return None


def warm_hue_text(rgb):
    """Тёплый «латунный/терракотовый» цвет текста или акцента: h 25–95°, C ≥ 0.05."""
    L, C, H = oklch(rgb)
    return 25 <= H <= 95 and C >= 0.05


# ---------------------------------------------------------------- текст и числа
QUOTES = str.maketrans({'«': '"', '»': '"', '“': '"', '”': '"', '„': '"', '’': "'", '‘': "'", '—': '-', '–': '-',
                        '‑': '-', ' ': ' ', ' ': ' ', ' ': ' ', ' ': ' '})


def norm_text(s):
    s = unicodedata.normalize('NFKC', s or '').translate(QUOTES).lower()
    s = re.sub(r'[*_`#>|]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


NUM_RX = re.compile(r'(?<![\w.,])([$€£₽]?\s?\d[\d\s   ]*(?:[.,]\d+)?)(\s?(?:%|\+|k\b|K\b|M\b|млн|тыс|млрд|x\b|×|₽|\$|€|£))?')


def extract_numbers(text):
    """[(исходная строка, нормализованное значение)] — '12 000+' → '12000', '4,9' → '4.9', '98 %' → '98'."""
    out = []
    for m in NUM_RX.finditer(text or ''):
        raw = (m.group(1) + (m.group(2) or '')).strip()
        core = re.sub(r'[$€£₽\s   ]', '', m.group(1))
        if re.fullmatch(r'\d{1,3}(?:[.,]\d{3})+', core) and not re.fullmatch(r'\d+[.,]\d{1,2}', core):
            core = re.sub(r'[.,]', '', core)          # 12.000 / 12,000 → 12000
        core = core.replace(',', '.')
        try:
            val = float(core)
        except ValueError:
            continue
        v = ('%f' % val).rstrip('0').rstrip('.')
        out.append((raw, v))
    return out


def md_plain(text):
    text = re.sub(r'\{#.*?#\}', ' ', text, flags=re.S)           # комментарии шаблонов F
    text = re.sub(r'^\s*\|?\s*-{3,}.*$', ' ', text, flags=re.M)   # разделители таблиц
    return text


def fact_text(path):
    """Текст фактов для сверки чисел: из таблиц facts.md (шаблон F) — только колонки «Fact…» и «Text on the page…»
    (даты источников и номера строк не делают число «известным»); без таблиц — весь текст."""
    raw = md_plain(open(path, encoding='utf-8').read())
    keep, header, tables = [], None, False
    for line in raw.splitlines():
        st = line.strip()
        if not st.startswith('|'):
            header = None
            continue
        cells = [c.strip() for c in st.strip('|').split('|')]
        low = [c.lower() for c in cells]
        if header is None:
            header = low
            tables = True
            continue
        idx = [i for i, h in enumerate(header) if h.startswith(('fact', 'факт')) or 'text on the page' in h or 'текст на странице' in h]
        keep += [cells[i] for i in idx if i < len(cells)]
    return '\n'.join(keep) if tables else raw


def load_numbers_file(path):
    if not path:
        return None
    try:
        txt = fact_text(path)
    except OSError as e:
        raise SystemExit(f'не читается {path}: {e}')
    return {v for _, v in extract_numbers(txt)}


def parse_assets_readme(path):
    """Таблица assets/README.md (шаблон F): колонки File / Caption / Alt → {stem: {caption, alt, file}}."""
    rows = {}
    if not path:
        return None
    text = open(path, encoding='utf-8').read()
    header = None
    for line in text.splitlines():
        if not line.strip().startswith('|'):
            header = None if not line.strip() else header
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-{3,}:?', c) for c in cells if c):
            continue
        low = [c.lower() for c in cells]
        if any(h.startswith(('file', 'файл')) for h in low) and any(('caption' in h or 'подпис' in h) for h in low):
            header = low
            continue
        if not header:
            continue
        rec = dict(zip(header, cells))
        f = next((rec[h] for h in header if h.startswith(('file', 'файл'))), '')
        cap = next((rec[h] for h in header if 'caption' in h or 'подпис' in h), '')
        alt = next((rec[h] for h in header if h.startswith('alt')), '')
        f = f.strip('` ')
        if f:
            rows[os.path.splitext(os.path.basename(f))[0].lower()] = {'file': f, 'caption': cap.strip('"« »'),
                                                                      'alt': alt.strip('"« »')}
    return rows


def family_first(ff):
    return (ff or '').split(',')[0].strip().strip('"\'').lower()


def family_kind(ff):
    """serif | sans | mono | unknown по объявленному стеку (намерение исполнителя важнее запасного шрифта)."""
    stack = [x.strip().strip('"\'').lower() for x in (ff or '').split(',') if x.strip()]
    if not stack:
        return 'unknown'
    first = stack[0]
    if first in MONO_FAMILIES or 'mono' in first:
        return 'mono'
    if first in SERIF_FAMILIES or re.search(r'\bserif\b', first) and 'sans' not in first:
        return 'serif'
    if first in SANS_DEFAULTS or 'sans' in first or 'grotesk' in first or 'grotesque' in first:
        return 'sans'
    generic = stack[-1]
    if generic == 'serif':
        return 'serif'
    if generic in ('sans-serif', 'system-ui'):
        return 'sans'
    if generic == 'monospace':
        return 'mono'
    return 'unknown'


# ---------------------------------------------------------------- статический обход исходников (без выхода за папку)
def safe_root(path):
    real = os.path.realpath(path)
    home = os.path.realpath(os.path.expanduser('~'))
    if real in ('/', home, os.path.dirname(home)):
        raise SystemExit(f'отказ: {real} — корень или домашняя папка; укажите папку проекта (--src)')
    for bad in ('.ssh', '.kimi-code', '.claude', '.config', '.gnupg', '.local'):
        if real == os.path.join(home, bad) or real.startswith(os.path.join(home, bad) + os.sep):
            raise SystemExit(f'отказ: {real} внутри ~/{bad}')
    return real


def scan_sources(root, max_bytes=20_000_000, max_files=5000):
    root = safe_root(root)
    hits, fonts, trans_all, files, total = [], {}, 0, 0, 0
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith('.')]
        for fn in fns:
            if not fn.lower().endswith(TEXT_EXT):
                continue
            p = os.path.join(dp, fn)
            try:
                size = os.path.getsize(p)
                if size > 3_000_000:
                    continue
                txt = open(p, encoding='utf-8', errors='replace').read()
            except OSError:
                continue
            files += 1
            total += size
            rel = os.path.relpath(p, root)
            for kind, rx in STOCK_PATTERNS:
                for m in re.finditer(rx, txt, re.I):
                    hits.append({'kind': kind, 'url': m.group(0)[:160], 'file': rel,
                                 'line': txt.count('\n', 0, m.start()) + 1})
            for m in re.finditer(r'family=([A-Za-z0-9+ %]+?)(?::|&|"|\'|\))', txt):
                fam = m.group(1).replace('+', ' ').replace('%20', ' ').strip().lower()
                fonts[fam] = fonts.get(fam, 0) + 1
            for m in re.finditer(r'font-family\s*:\s*([^;}{]+)', txt, re.I):
                fam = family_first(m.group(1))
                if fam and not fam.startswith('var('):
                    fonts[fam] = fonts.get(fam, 0) + 1
            trans_all += len(re.findall(r'transition\s*:\s*all\b', txt, re.I))
            if files >= max_files or total >= max_bytes:
                break
        if files >= max_files or total >= max_bytes:
            break
    return {'root': root, 'files': files, 'bytes': total, 'stock_hits': hits[:200], 'declared_fonts': fonts,
            'transition_all': trans_all}


# ---------------------------------------------------------------- сбор с отрисованной страницы
COLLECT_JS = r"""
(conf) => {
  const vw = conf.vw, vh = conf.vh, LIM = 6000;
  const out = {vw, vh, url: location.href, lang: document.documentElement.getAttribute('lang') || ''};
  const ign = conf.ignore ? Array.from(document.querySelectorAll(conf.ignore)) : [];
  const isIgn = (el) => ign.some(g => g === el || g.contains(el));
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', {willReadFrequently: true});
  const cache = new Map();
  const rgba = (c) => {
    if (!c) return [0, 0, 0, 0];
    if (cache.has(c)) return cache.get(c);
    let v = [0, 0, 0, 0];
    if (c !== 'transparent' && c !== 'rgba(0, 0, 0, 0)') {
      cx.clearRect(0, 0, 1, 1); cx.fillStyle = '#000'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1);
      const d = cx.getImageData(0, 0, 1, 1).data; v = [d[0], d[1], d[2], +(d[3] / 255).toFixed(3)];
    }
    cache.set(c, v); return v;
  };
  const desc = (el) => {
    let s = el.tagName.toLowerCase(); if (el.id) s += '#' + el.id;
    const cl = (typeof el.className === 'string') ? el.className.trim().split(/\s+/).filter(Boolean).slice(0, 2) : [];
    if (cl.length) s += '.' + cl.join('.'); return s;
  };
  const visible = (el) => {
    const r = el.getBoundingClientRect(); if (r.width < 1 || r.height < 1) return false;
    let o = 1;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.display === 'none' || s.visibility === 'hidden') return false;
      o *= parseFloat(s.opacity || '1');
    }
    return o >= 0.1;
  };
  const effBg = (el) => {
    const layers = []; let img = false;
    for (let e = el; e && e.nodeType === 1; e = e.parentElement) {
      const s = getComputedStyle(e);
      if (s.backgroundImage && s.backgroundImage !== 'none') img = true;
      const c = rgba(s.backgroundColor);
      if (c[3] > 0.02) { layers.push(c); if (c[3] >= 0.99) break; }
    }
    let r = 255, g = 255, b = 255;
    for (let i = layers.length - 1; i >= 0; i--) { const [lr, lg, lb, la] = layers[i];
      r = lr * la + r * (1 - la); g = lg * la + g * (1 - la); b = lb * la + b * (1 - la); }
    return {rgb: [Math.round(r), Math.round(g), Math.round(b)], img};
  };
  const fam1 = (ff) => (ff || '').split(',')[0].trim().replace(/^["']|["']$/g, '').toLowerCase();
  const clean = (t) => (t || '').replace(/\s+/g, ' ').trim();
  const main = document.querySelector('main');

  // --- заголовки: акцентное слово, надзаголовок, пилюля
  const heads = Array.from(document.querySelectorAll('h1, h2, h3')).filter(h => !isIgn(h) && visible(h));
  out.headings = heads.slice(0, 80).map(h => {
    const cs = getComputedStyle(h); const r = h.getBoundingClientRect(); const txt = clean(h.innerText);
    const hc = rgba(cs.color);
    let accent = null;
    for (const d of h.querySelectorAll('em, i, span, strong, b, mark, u, sup, a')) {
      if (!visible(d)) continue;
      const dt = clean(d.innerText); if (!dt || dt.length >= txt.length * 0.6) continue;
      const ds = getComputedStyle(d); const dc = rgba(ds.color); const reasons = [];
      if (ds.fontStyle !== cs.fontStyle && ds.fontStyle !== 'normal') reasons.push('italic');
      if (Math.hypot(dc[0] - hc[0], dc[1] - hc[1], dc[2] - hc[2]) > 40) reasons.push('colour');
      const clip = ds.webkitBackgroundClip || ds.backgroundClip;
      if (clip === 'text' && /gradient/.test(ds.backgroundImage)) reasons.push('gradient');
      if (fam1(ds.fontFamily) !== fam1(cs.fontFamily)) reasons.push('font');
      if (/underline/.test(ds.textDecorationLine) && !/underline/.test(cs.textDecorationLine) && d.tagName !== 'A') reasons.push('underline');
      if (rgba(ds.backgroundColor)[3] > 0.2) reasons.push('highlight');
      if (reasons.length) { accent = {text: dt.slice(0, 40), el: desc(d), reasons}; break; }
    }
    const clipH = cs.webkitBackgroundClip || cs.backgroundClip;
    let eyebrow = null, pill = null;
    const prev = h.previousElementSibling;
    if (prev && !isIgn(prev) && visible(prev)) {
      const ps = getComputedStyle(prev); const pt = clean(prev.innerText);
      const fs = parseFloat(ps.fontSize), hfs = parseFloat(cs.fontSize);
      const ls = ps.letterSpacing === 'normal' ? 0 : parseFloat(ps.letterSpacing);
      const letters = pt.replace(/[^A-Za-zА-Яа-яЁё]/g, '');
      const caps = ps.textTransform === 'uppercase' || (letters.length >= 3 && letters === letters.toUpperCase());
      if (pt && pt.length <= 70 && caps && fs <= Math.min(15, hfs * 0.7) && ls / fs >= 0.04)
        eyebrow = {text: pt.slice(0, 40), fs, ls_em: +(ls / fs).toFixed(3), el: desc(prev)};
      const pr = prev.getBoundingClientRect(); const rad = parseFloat(ps.borderTopLeftRadius) || 0;
      const box = rgba(ps.backgroundColor)[3] > 0.05 || parseFloat(ps.borderTopWidth) > 0;
      if (h.tagName === 'H1' && pt && pt.length <= 70 && pr.height <= 48 && rad >= pr.height * 0.45 && box && pr.width < vw * 0.7)
        pill = {text: pt.slice(0, 50), el: desc(prev)};
    }
    const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.2;
    return {tag: h.tagName.toLowerCase(), el: desc(h), text: txt.slice(0, 120), ff: cs.fontFamily,
            fs: parseFloat(cs.fontSize), fw: cs.fontWeight, style: cs.fontStyle, align: cs.textAlign,
            x: r.left, w: r.width, top: r.top + scrollY, h: r.height, lines: Math.max(1, Math.round(r.height / lh)),
            color: hc, accent, grad: clipH === 'text' && /gradient/.test(cs.backgroundImage), eyebrow, pill};
  });

  // --- текстовые узлы: шрифты, капс, моно, «·», стрелки, контраст
  const leaves = []; const seen = new Set();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode() && leaves.length < 3000) {
    const t = walker.currentNode; if (!clean(t.textContent)) continue;
    const el = t.parentElement; if (!el || seen.has(el)) continue; seen.add(el);
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName) || el.closest('svg')) continue;
    if (isIgn(el) || !visible(el)) continue;
    const cs = getComputedStyle(el); const bg = effBg(el);
    const own = clean(Array.from(el.childNodes).filter(c => c.nodeType === 3).map(c => c.textContent).join(' '));
    leaves.push({el: desc(el), tag: el.tagName.toLowerCase(), text: own.slice(0, 160), fs: parseFloat(cs.fontSize),
                 fw: parseInt(cs.fontWeight) || 400, ff: cs.fontFamily, tt: cs.textTransform,
                 ls: cs.letterSpacing === 'normal' ? 0 : parseFloat(cs.letterSpacing), color: rgba(cs.color), bg: bg.rgb,
                 bg_img: bg.img, in_btn: !!el.closest('button, a, [role=button]')});
  }
  out.leaves = leaves;

  // --- наложение текста: прямоугольники строк текстовых узлов (Range.getClientRects), не контейнеров
  const rects = []; const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let tn = 0;
  while (tw.nextNode() && rects.length < 1500) {
    const t = tw.currentNode; const txt = clean(t.textContent); if (txt.length < 2) continue;
    const el = t.parentElement; if (!el || isIgn(el) || el.closest('svg') || ['SCRIPT', 'STYLE', 'NOSCRIPT'].includes(el.tagName)) continue;
    if (!visible(el)) continue;
    tn++;
    const rg = document.createRange(); rg.selectNodeContents(t);
    const cr = Array.from(rg.getClientRects()).filter(r => r.width >= 3 && r.height >= 3).slice(0, 6);
    for (const r of cr) rects.push({n: tn, x: r.left, y: r.top + scrollY, w: r.width, h: r.height, text: txt.slice(0, 30), el: desc(el)});
  }
  const overlaps = [];
  for (let i = 0; i < rects.length && overlaps.length < 12; i++) {
    const a = rects[i];
    for (let j = i + 1; j < rects.length; j++) {
      const b = rects[j]; if (a.n === b.n) continue;
      const ix = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x); if (ix <= 0) continue;
      const iy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y); if (iy <= 0) continue;
      const inter = ix * iy, small = Math.min(a.w * a.h, b.w * b.h);
      if (inter >= 0.3 * small) { overlaps.push({a: a.text, a_el: a.el, b: b.text, b_el: b.el, y: Math.round(Math.min(a.y, b.y)), share: +(inter / small).toFixed(2)}); break; }
    }
  }
  out.text_overlaps = overlaps;

  // --- блоки текста для сверки с copy.md и facts.md
  const blocks = []; const BLK = 'h1,h2,h3,h4,h5,h6,p,li,button,figcaption,blockquote,td,th,dt,dd,label';
  for (const el of document.querySelectorAll(BLK + ',a,small,strong,span,q,cite')) {
    if (blocks.length >= 1500) break;
    if (isIgn(el) || !visible(el)) continue;
    if (el.querySelector('h1,h2,h3,h4,h5,h6,p,li,figcaption,blockquote,td,dd')) continue;
    if (['A', 'SMALL', 'STRONG', 'SPAN', 'Q', 'CITE'].includes(el.tagName) && el.parentElement && el.parentElement.closest(BLK)) continue;
    const t = clean(el.innerText); if (!t) continue;
    blocks.push({el: desc(el), tag: el.tagName.toLowerCase(), text: t.slice(0, 400),
                 quote: !!el.closest('blockquote, q, [class*=testimonial i], [class*=review i], [class*=quote i]')});
  }
  out.blocks = blocks;

  // --- картинки, фоны, источники
  out.images = Array.from(document.querySelectorAll('img')).filter(im => !isIgn(im)).slice(0, 200).map(im => {
    const r = im.getBoundingClientRect(); const fig = im.closest('figure');
    const cap = fig && fig.querySelector('figcaption') ? clean(fig.querySelector('figcaption').innerText) : null;
    return {el: desc(im), src: im.currentSrc || im.src || '', srcset: im.getAttribute('srcset') || '', alt: im.getAttribute('alt'),
            w: r.width, h: r.height, visible: visible(im), caption: cap};
  });
  const bgs = []; let k = 0;
  for (const el of document.querySelectorAll('body *')) {
    if (++k > LIM || bgs.length >= 120) break; if (isIgn(el)) continue;
    for (const ps of [null, '::before', '::after']) {
      const s = getComputedStyle(el, ps);
      if (s.backgroundImage && s.backgroundImage.includes('url(')) bgs.push({el: desc(el) + (ps || ''), value: s.backgroundImage.slice(0, 500)});
    }
  }
  out.bg_images = bgs;
  out.media_src = Array.from(document.querySelectorAll('source[srcset], source[src], video[poster], video[src]')).slice(0, 60)
      .map(s => s.getAttribute('srcset') || s.getAttribute('src') || s.getAttribute('poster') || '');

  // --- фон страницы и секций
  const cands = [...document.body.children, ...(main ? main.children : [])];
  out.sections = cands.filter(el => !isIgn(el) && visible(el)).map(el => {
    const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return {el: desc(el), top: r.top + scrollY, h: r.height, w: r.width, bg: effBg(el).rgb, bg_img: s.backgroundImage !== 'none'};
  }).filter(s => s.h >= 120).slice(0, 60);
  let cvArea = 0;
  for (const c of document.querySelectorAll('canvas, video')) {
    if (isIgn(c) || !visible(c)) continue; const r = c.getBoundingClientRect();
    const w = Math.max(0, Math.min(r.right, vw) - Math.max(r.left, 0)), hh = Math.max(0, Math.min(r.bottom, vh) - Math.max(r.top, 0));
    cvArea += w * hh;
  }
  out.canvas_share = Math.min(1, cvArea / (vw * vh));
  out.page_bg = effBg(document.body).rgb;
  out.page_h = document.documentElement.scrollHeight;
  out.scroll_w = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);

  // --- hero: высота, центрирование, фото под вуалью
  const h1 = heads.find(h => h.tagName === 'H1') || null;
  out.hero = null;
  if (h1) {
    let hero = h1;
    while (hero.parentElement && hero.parentElement !== document.body && hero.parentElement !== main) hero = hero.parentElement;
    const hr = hero.getBoundingClientRect(); const hs = getComputedStyle(hero); const h1s = getComputedStyle(h1); const h1r = h1.getBoundingClientRect();
    const area = Math.max(1, hr.width * Math.min(hr.height, Math.max(vh, 1)));
    const media = [], bgUrl = [], overlays = [];
    const all = [hero, ...hero.querySelectorAll('*')].slice(0, 500);
    for (const m of all) {
      const r = m.getBoundingClientRect(); const s = getComputedStyle(m);
      const big = r.width >= hr.width * 0.85 && r.height >= Math.min(hr.height, vh) * 0.5;
      if (big && ['IMG', 'VIDEO', 'PICTURE', 'CANVAS'].includes(m.tagName)) media.push({el: desc(m), tag: m.tagName.toLowerCase()});
      if (big && s.backgroundImage.includes('url(')) bgUrl.push({el: desc(m), veil_in_same: /gradient/.test(s.backgroundImage)});
      for (const ps of [null, '::before', '::after']) {
        const q = getComputedStyle(m, ps);
        if (ps && (q.content === 'none' || q.content === 'normal')) continue;
        if (!ps && !(q.position === 'absolute' || q.position === 'fixed')) continue;
        if (ps && !(q.position === 'absolute' || q.position === 'fixed')) continue;
        const cover = (r.width * r.height) / area;
        const c = rgba(q.backgroundColor);
        const lum = (0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]) / 255;
        const darkFill = c[3] >= 0.15 && c[3] <= 0.95 && lum < 0.45;
        const gradDark = /gradient/.test(q.backgroundImage) && /rgba?\(\s*\d{1,2},\s*\d{1,2},\s*\d{1,2}|#000|black|rgba\(0, 0, 0/.test(q.backgroundImage);
        if ((darkFill || gradDark) && cover >= 0.6) overlays.push({el: desc(m) + (ps || ''), alpha: c[3], grad: gradDark});
      }
    }
    out.hero = {el: desc(hero), h: hr.height, w: hr.width, top: hr.top + scrollY, h1_align: h1s.textAlign, hero_align: hs.textAlign,
                h1_cx: (h1r.left + h1r.width / 2) / vw, h1_w: h1r.width / vw, min_height: hs.minHeight,
                h1_lines: Math.max(1, Math.round(h1r.height / (parseFloat(h1s.lineHeight) || parseFloat(h1s.fontSize) * 1.2))),
                media: media.slice(0, 5), bg_url: bgUrl.slice(0, 5), overlays: overlays.slice(0, 5)};
  }

  // --- ряды: ряд цифр, три одинаковые карточки
  const rows = []; k = 0;
  for (const p of document.querySelectorAll('body *')) {
    if (++k > LIM || rows.length > 200) break; if (isIgn(p)) continue;
    const kids = Array.from(p.children).filter(c => visible(c));
    if (kids.length < 3 || kids.length > 6) continue;
    const rs = kids.map(c => c.getBoundingClientRect()); const t0 = rs[0].top;
    if (!rs.every(r => Math.abs(r.top - t0) < 10)) continue;
    const pr = p.getBoundingClientRect(); if (pr.width < vw * 0.5) continue;
    const ws = rs.map(r => r.width), hs2 = rs.map(r => r.height);
    const sig = kids.map(c => c.tagName + ':' + c.children.length);
    const nums = kids.map(c => {
      let best = null;
      for (const e of [c, ...c.querySelectorAll('*')]) {
        if (e.children.length) continue; const t = clean(e.innerText); const fs = parseFloat(getComputedStyle(e).fontSize);
        if (t && t.length <= 14 && /\d/.test(t) && /^[~≈<>]?\s*[$€£₽]?\s*[\d\s.,]+\s*(%|\+|k|K|M|x|×|млн|тыс|₽|\$|€|£|ч|h|min|мин|\/\s*\d+)?\s*\+?$/.test(t) && fs >= 28)
          if (!best || fs > best.fs) best = {t, fs};
      }
      return best;
    }).filter(Boolean);
    rows.push({el: desc(p), n: kids.length, top: t0 + scrollY, w_ratio: Math.max(...ws) / Math.max(1, Math.min(...ws)),
               h_ratio: Math.max(...hs2) / Math.max(1, Math.min(...hs2)), min_w: Math.min(...ws) / pr.width, min_h: Math.min(...hs2),
               same: sig.every(s => s === sig[0]), content: kids.every(c => !!c.querySelector('h2,h3,h4,h5,p,strong')),
               nums: nums.length, num_texts: nums.map(x => x.t), in_chrome: !!p.closest('nav, header, footer')});
  }
  out.rows = rows;

  // --- стекло, градиентный текст, бегущая строка, нарисованный хром
  const glass = [], gradText = [], marquee = [], dots = []; k = 0;
  for (const e of document.querySelectorAll('body *')) {
    if (++k > LIM) break; if (isIgn(e)) continue;
    const s = getComputedStyle(e);
    if (/blur/.test(s.backdropFilter || s.webkitBackdropFilter || '') && visible(e)) glass.push(desc(e));
    const clip = s.webkitBackgroundClip || s.backgroundClip;
    if (clip === 'text' && /gradient/.test(s.backgroundImage) && visible(e)) gradText.push({el: desc(e), text: clean(e.innerText).slice(0, 40)});
    if (e.tagName === 'MARQUEE') marquee.push(desc(e));
    else if (s.animationName && s.animationName !== 'none' && s.animationIterationCount === 'infinite' && e.parentElement &&
             e.scrollWidth > e.parentElement.clientWidth * 1.5) marquee.push(desc(e));
    const kids = e.children;
    if (kids.length >= 3 && kids.length <= 4) {
      let small = 0;
      for (const c of kids) { const r = c.getBoundingClientRect(); const cs2 = getComputedStyle(c);
        if (r.width > 4 && r.width <= 16 && Math.abs(r.width - r.height) <= 2 && parseFloat(cs2.borderTopLeftRadius) >= r.width * 0.45 && rgba(cs2.backgroundColor)[3] > 0.3) small++; }
      if (small >= 3) dots.push(desc(e));
    }
  }
  out.glass = glass.slice(0, 20); out.grad_text = gradText.slice(0, 20); out.marquee = marquee.slice(0, 10); out.drawn_dots = dots.slice(0, 10);

  // --- навигация
  const navs = [];
  for (const n of document.querySelectorAll('nav, header')) {
    if (isIgn(n) || !visible(n)) continue;
    navs.push({el: desc(n), links: Array.from(n.querySelectorAll('a[href], button')).filter(a => visible(a)).length});
  }
  const toggles = [];
  for (const b of document.querySelectorAll('button, [role=button], a, label, [aria-expanded], [aria-controls], [class*=menu i], [class*=burger i], [id*=menu i], [class*=toggle i]')) {
    if (toggles.length >= 10) break; if (isIgn(b) || !visible(b)) continue;
    const idc = ((b.id || '') + ' ' + (typeof b.className === 'string' ? b.className : '') + ' ' + (b.getAttribute('aria-label') || '')).toLowerCase();
    if (b.hasAttribute('aria-expanded') || b.hasAttribute('aria-controls') || /(menu|burger|hamburger|nav-?toggle|navbar-toggler|меню)/.test(idc)) {
      const r = b.getBoundingClientRect(); toggles.push({el: desc(b), top: r.top, w: r.width, h: r.height});
    }
  }
  out.nav = {navs: navs.slice(0, 10), toggles};

  if (conf.full) {
    let css = '';
    for (const sh of Array.from(document.styleSheets)) { try { for (const r of Array.from(sh.cssRules)) { css += r.cssText + '\n'; if (css.length > 2e6) break; } } catch (e) {} }
    out.html = document.documentElement.outerHTML.slice(0, 3e6); out.css = css.slice(0, 2e6);
  }
  return out;
}
"""


def free_gb():
    try:
        for line in open('/proc/meminfo'):
            if line.startswith('MemAvailable:'):
                return int(line.split()[1]) / 1024 / 1024
    except OSError:
        pass
    return None


def make_router(host, blocked):
    """Обработчик page.route с одним параметром (Playwright передаёт (route, request), если параметров два)."""
    def handler(route):
        u = urlparse(route.request.url)
        if u.scheme in ('data', 'blob') or u.netloc == host:
            return route.continue_()
        blocked.append(route.request.url[:200])
        return route.abort()
    return handler


def collect(target, views, ignore, block_external, shots_dir):
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    import functools, http.server, socketserver, threading
    httpd, url, local_host = None, target, None
    if not target.startswith(('http://', 'https://', 'file://')):
        path = os.path.abspath(target)
        if not os.path.exists(path):
            raise SystemExit(f'нет файла или папки: {path}')
        root, name = (path, '') if os.path.isdir(path) else (os.path.dirname(path), os.path.basename(path))
        safe_root(root)

        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *a):
                pass
        httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=root))
        httpd.daemon_threads = True
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{httpd.server_address[1]}/{name}'
        local_host = f'127.0.0.1:{httpd.server_address[1]}'
    results, blocked = [], []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                for i, spec in enumerate(views):
                    w, h = (int(x) for x in spec.lower().split('x'))
                    ctx = browser.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1,
                                              is_mobile=w < 768, has_touch=w < 1024, reduced_motion='reduce')
                    page = ctx.new_page()
                    if block_external:
                        page.route('**/*', make_router(local_host or urlparse(url).netloc, blocked))
                    try:
                        page.goto(url, wait_until='networkidle', timeout=60000)
                    except PWTimeout:
                        pass
                    page.wait_for_timeout(400)
                    total = page.evaluate('document.documentElement.scrollHeight')
                    y = 0
                    while y < total and y < 40000:           # догрузить lazy и отыграть reveal-анимации
                        page.evaluate(f'window.scrollTo(0, {y})'); page.wait_for_timeout(100); y += h
                    page.evaluate('window.scrollTo(0, 0)'); page.wait_for_timeout(300)
                    data = page.evaluate(COLLECT_JS, {'vw': w, 'vh': h, 'ignore': ignore or '', 'full': i == 0})
                    data['viewport'] = spec
                    if shots_dir:
                        os.makedirs(shots_dir, exist_ok=True)
                        kind = 'desktop' if w >= 1024 else ('tablet' if w >= 768 else 'mobile')
                        fn = os.path.join(shots_dir, f'{kind}-{w}x{h}-00.jpg')
                        try:                              # WebGL-страницы бывают «нестабильны» для скриншота — не ронять прогон
                            page.screenshot(path=fn, type='jpeg', quality=80, animations='disabled', timeout=15000)
                            data['shot'] = os.path.abspath(fn)
                        except Exception as e:  # noqa: BLE001
                            data['shot_error'] = f'{type(e).__name__}: {str(e)[:120]}'
                    results.append(data)
                    ctx.close()
            finally:
                browser.close()
    finally:
        if httpd:
            httpd.shutdown(); httpd.server_close()
    return url, results, sorted(set(blocked))[:50]


# ---------------------------------------------------------------- анализ
def add(findings, fid, sev, view, msg, evidence=None, fix=None, allow=None, allowed=()):
    if allow and allow in allowed:
        sev = 'info'
        msg += f' (разрешено брифом: --allow {allow})'
    findings.append({'id': fid, 'severity': sev, 'view': view, 'message': msg, 'evidence': evidence or {},
                     'fix_en': fix or ''})


def urls_in(text):
    return re.findall(r'url\(["\']?([^"\')]+)["\']?\)', text or '')


def stock_kind(u):
    for kind, rx in STOCK_PATTERNS:
        if re.search(rx, u or '', re.I):
            return kind
    return None


def analyze(url, views, static, facts_nums, copy_text, copy_nums, assets, allowed, blocked):
    F = []
    desk = next((v for v in views if int(v['viewport'].split('x')[0]) >= 1024), views[0])
    target_host = urlparse(url).netloc

    # ---------- K3-BG-WARM: фон страницы и секций
    for v in views[:1] if len(views) else []:
        page_w = warm_class(v['page_bg'])
        secs = v['sections']
        total_h = max(1, v['page_h'])
        warm_secs = [s for s in secs if warm_class(s['bg'])]
        share = min(1.0, sum(s['h'] for s in warm_secs) / total_h)
        ev = {'page_bg': hexs(v['page_bg']), 'page_bg_oklch': oklch(v['page_bg']), 'warm_share_of_page': round(share, 2),
              'warm_sections': [{'el': s['el'], 'bg': hexs(s['bg']), 'oklch': oklch(s['bg'])} for s in warm_secs[:6]]}
        if page_w or share >= 0.25:
            add(F, 'K3-BG-WARM', 'major', v['viewport'],
                f"тёплый тонированный фон ({'страница ' + hexs(v['page_bg']) if page_w else 'секции'}; доля {share:.0%})",
                ev, 'Use the neutral paper from DESIGN.md (--color-bg) for the page and every section; no cream, beige or brown-black tints.',
                'warm', allowed)
        elif warm_secs:
            add(F, 'K3-BG-WARM', 'minor', v['viewport'], f'тёплая тонированная секция ({len(warm_secs)} шт., доля {share:.0%})',
                ev, 'Replace the tinted section background with a DESIGN.md surface token.', 'warm', allowed)

    # ---------- заголовки: акцентное слово, антиква, надзаголовки, пилюля, градиент
    heads = desk['headings']
    h1s = [h for h in heads if h['tag'] == 'h1']
    acc_h1 = [h for h in h1s if h['accent']]
    acc_h2 = [h for h in heads if h['tag'] != 'h1' and h['accent']]
    if acc_h1:
        a = acc_h1[0]['accent']
        add(F, 'K3-ACCENT-WORD', 'major', desk['viewport'],
            f"в h1 выделено слово «{a['text']}» ({', '.join(a['reasons'])})",
            {'h1': acc_h1[0]['text'], 'accent': a, 'h2_with_accent': len(acc_h2)},
            f"H1 {acc_h1[0]['el']}: render \"{a['text']}\" exactly like the rest of the headline (same font, style, colour); "
            'build hierarchy with size, weight and placement.', 'accent-word', allowed)
    elif len(acc_h2) >= 2:
        add(F, 'K3-ACCENT-WORD', 'minor', desk['viewport'], f'выделенное слово в {len(acc_h2)} подзаголовках',
            {'examples': [h['accent'] for h in acc_h2[:3]]}, 'Remove accent words from section headings.', 'accent-word', allowed)
    serif_heads = [h for h in heads if family_kind(h['ff']) == 'serif']
    h2s = [h for h in heads if h['tag'] == 'h2']
    serif_h1 = any(family_kind(h['ff']) == 'serif' for h in h1s)
    serif_h2 = h2s and sum(family_kind(h['ff']) == 'serif' for h in h2s) / len(h2s) >= 0.5
    body_leaves = [l for l in desk['leaves'] if l['tag'] in ('p', 'li') and len(l['text'].split()) >= 6]
    body_fam = statistics.mode([family_first(l['ff']) for l in body_leaves]) if body_leaves else ''
    if serif_h1 or serif_h2:
        disp = family_first((h1s or serif_heads)[0]['ff']) if (h1s or serif_heads) else ''
        pair = body_fam in SANS_DEFAULTS
        italic = any(h['style'] == 'italic' for h in serif_heads if h['tag'] == 'h1')
        add(F, 'K3-SERIF-DISPLAY', 'major', desk['viewport'],
            f"антиква в заголовках: {disp or '?'}" + (f" + {body_fam} в тексте (пара «антиква + дефолтный гротеск», как Fraunces + Inter)" if pair else '')
            + (' курсивом' if italic else ''),
            {'display': disp, 'body': body_fam, 'serif_headings': len(serif_heads), 'headings': len(heads)},
            'Use the display and text faces from DESIGN.md only; no serif display face unless DESIGN.md names it.',
            'serif', allowed)
    eyebrowed = [h for h in heads if h['eyebrow']]
    if heads and len(eyebrowed) >= 2 and len(eyebrowed) / len(heads) > 1 / 3:
        add(F, 'K3-EYEBROW', 'major', desk['viewport'],
            f'капс-надзаголовки над {len(eyebrowed)} из {len(heads)} заголовков (> 1/3; ui 11/04 m30)',
            {'examples': [h['eyebrow'] for h in eyebrowed[:4]]},
            'Delete the uppercase letter-spaced labels above headings; keep at most one per three sections, sentence case.',
            'eyebrow', allowed)
    elif eyebrowed:
        add(F, 'K3-EYEBROW', 'minor', desk['viewport'], f'капс-надзаголовок: {len(eyebrowed)} шт.',
            {'examples': [h['eyebrow'] for h in eyebrowed[:3]]}, 'Remove the eyebrow label unless the brief asks for it.',
            'eyebrow', allowed)
    pills = [h['pill'] for h in h1s if h['pill']]
    if pills:
        add(F, 'K3-PILL', 'minor', desk['viewport'], f"пилюля над h1: «{pills[0]['text']}»", {'pill': pills[0]},
            'Remove the pill badge above the H1.', 'pill', allowed)
    grad = desk['grad_text']
    if grad:
        in_head = any(h['grad'] or (h['accent'] and 'gradient' in h['accent']['reasons']) for h in heads)
        add(F, 'K3-GRADIENT-TEXT', 'major' if in_head else 'minor', desk['viewport'],
            f'градиентный текст: {len(grad)} эл.', {'examples': grad[:3]},
            'Remove background-clip:text gradients; use a solid colour token.', 'gradient', allowed)

    # ---------- hero
    hero = desk.get('hero')
    if hero:
        vh = desk['vh']
        centered = hero['h1_align'] == 'center' or (abs(hero['h1_cx'] - 0.5) < 0.05 and hero['h1_w'] < 0.9 and hero['hero_align'] == 'center')
        if hero['h'] >= 0.9 * vh and centered:
            add(F, 'K3-HERO-CENTER', 'major', desk['viewport'],
                f"hero {hero['h']:.0f} px при окне {vh} (≥ 90 %), всё по центру (Hallmark гейт 6)",
                {'hero': hero['el'], 'h': round(hero['h']), 'vh': vh, 'h1_align': hero['h1_align']},
                f"Hero {hero['el']}: not a centred full-viewport stack; left-align the headline block and let the hero end "
                'below the fold line with the next section visible at 1440x900.', 'center-hero', allowed)
        if (hero['media'] or hero['bg_url']) and (hero['overlays'] or any(b['veil_in_same'] for b in hero['bg_url'])):
            add(F, 'K3-HERO-OVERLAY', 'major', desk['viewport'], 'фото/видео на весь hero под тёмной вуалью',
                {'media': hero['media'][:2] + hero['bg_url'][:2], 'overlays': hero['overlays'][:2]},
                'Drop the full-bleed photo under a dark overlay; use the hero asset from assets/README.md at its natural '
                'contrast, or a solid surface.', 'photo-hero', allowed)

    # ---------- ряды: цифры, три карточки
    rows = desk['rows']
    stats = [r for r in rows if r['nums'] >= 3 and not r['in_chrome']]
    if stats:
        add(F, 'K3-STATS-ROW', 'major', desk['viewport'], f"ряд крупных чисел: {', '.join(stats[0]['num_texts'][:5])}",
            {'rows': [{'el': r['el'], 'numbers': r['num_texts']} for r in stats[:3]]},
            'Remove the stats row unless every number is in brief/facts.md and the brief asks for it.', 'stats', allowed)
    cards = [r for r in rows if r['n'] == 3 and r['w_ratio'] <= 1.06 and r['h_ratio'] <= 1.25 and r['same'] and
             r['min_w'] >= 0.2 and r['min_h'] >= 120 and r['content'] and not r['in_chrome']]
    if cards:
        add(F, 'K3-THREE-CARDS', 'major', desk['viewport'], f'три одинаковые карточки в ряд: {len(cards)} ряд(а) (m17)',
            {'rows': [c['el'] for c in cards[:3]]},
            f"Section {cards[0]['el']}: replace the three equal cards with an asymmetric layout (one lead item wider) or a list.",
            'cards', allowed)

    # ---------- шаблонный хром по текстовым узлам
    leaves = desk['leaves']
    n_leaves = max(1, len(leaves))
    caps = [l for l in leaves if l['tt'] == 'uppercase' and re.search(r'[A-Za-zА-Яа-яЁё]{2,}', l['text'])]
    if len(caps) / n_leaves > 0.02 and len(caps) >= 3:
        add(F, 'K3-CAPS', 'minor', desk['viewport'], f'капс у {len(caps)} из {n_leaves} текстовых узлов ({len(caps) / n_leaves:.1%} > 2 %, m8)',
            {'examples': [l['text'][:30] for l in caps[:5]]}, 'Use sentence case; uppercase at most for one small role.', 'caps', allowed)
    dots = [l for l in leaves if re.search(r'[·•]', l['text']) and len(l['text']) <= 90]
    if len(dots) > 5:
        add(F, 'K3-META-DOTS', 'minor', desk['viewport'], f'мета-строки через «·»: {len(dots)} (> 5, m32)',
            {'examples': [l['text'][:50] for l in dots[:4]]}, 'Replace "A · B · C" meta lines with plain labels separated by space.',
            'dots', allowed)
    arrows = [l for l in leaves if l['in_btn'] and re.search(r'[→↗⟶➝➜⇢↘»]', l['text'])]
    if arrows:
        add(F, 'K3-ARROWS', 'minor', desk['viewport'], f'стрелки в кнопках и ссылках: {len(arrows)} (m34)',
            {'examples': [l['text'][:30] for l in arrows[:4]]}, 'Remove arrow glyphs from button and link labels.', 'arrows', allowed)
    mono = [l for l in leaves if l['fs'] < 14 and family_kind(l['ff']) == 'mono' and not re.search(r'\d', l['text'])]
    if len(mono) >= 3:
        add(F, 'K3-MONO-LABELS', 'minor', desk['viewport'], f'моноширинные подписи без данных: {len(mono)} (m33)',
            {'examples': [l['text'][:30] for l in mono[:4]]}, 'Use the text face for small labels; monospace only for code and data.',
            'mono', allowed)
    numbered = [l for l in leaves if re.match(r'^\s*0[1-9](?:\b|[.·/—-])', l['text']) and len(l['text']) <= 24]
    if len(numbered) >= 3:
        add(F, 'K3-NUMBERED', 'minor', desk['viewport'], f'нумерация 01/02/03: {len(numbered)} (m31 — только для настоящей последовательности)',
            {'examples': [l['text'] for l in numbered[:4]]}, 'Remove 01/02/03 labels unless the content is a real sequence.',
            'numbered', allowed)
    if len(desk['glass']) > 2:
        add(F, 'K3-GLASS', 'minor', desk['viewport'], f"стекло (backdrop-filter): {len(desk['glass'])} эл. (> 2, m15)",
            {'examples': desk['glass'][:4]}, 'Keep backdrop blur on at most one overlay layer; use solid surfaces.', 'glass', allowed)
    elif desk['glass']:
        add(F, 'K3-GLASS', 'info', desk['viewport'], f"стекло: {len(desk['glass'])} эл.", {'examples': desk['glass'][:2]})
    if desk['marquee']:
        add(F, 'K3-MARQUEE', 'minor', desk['viewport'], f"бегущая строка: {len(desk['marquee'])}", {'examples': desk['marquee'][:3]},
            'Remove the marquee or make it static; if kept, add a pause control (WCAG 2.2.2).', 'marquee', allowed)
    if desk['drawn_dots']:
        add(F, 'K3-DRAWN-CHROME', 'minor', desk['viewport'], f"нарисованный браузерный хром (три точки): {len(desk['drawn_dots'])}",
            {'examples': desk['drawn_dots'][:3]}, 'Remove drawn browser or phone frames; show the real screenshot asset only.',
            'chrome', allowed)

    # ---------- контраст тёплых палитр
    bad = []
    for v in views:
        for l in v['leaves']:
            if l['bg_img'] or not l['text'] or l['color'][3] == 0:
                continue
            large = l['fs'] >= 24 or (l['fs'] >= 18.66 and l['fw'] >= 700)
            cr = contrast(l['color'], l['bg'])
            need = 3.0 if large else 4.5
            if cr < need and (warm_class(l['bg']) or warm_hue_text(l['color'])):
                bad.append({'view': v['viewport'], 'el': l['el'], 'text': l['text'][:30], 'ratio': cr, 'need': need,
                            'fg': hexs(l['color']), 'bg': hexs(l['bg'])})
    if bad:
        uniq_bad = {}
        for b in bad:
            uniq_bad.setdefault((b['el'], b['text'], b['ratio']), b)
        bad = sorted(uniq_bad.values(), key=lambda x: x['ratio'])
        add(F, 'K3-WARM-CONTRAST', 'major', bad[0]['view'],
            f"текст тёплой палитры ниже порога: {len(bad)} узл., худший {bad[0]['ratio']}:1 ({bad[0]['fg']} на {bad[0]['bg']})",
            {'worst': bad[:6]}, f"Raise contrast of {bad[0]['el']} to >= {bad[0]['need']}:1 using a darker text token.")

    # ---------- выдумки: сток и хотлинк
    stock, hot = [], []
    for v in views:
        srcs = [(im['src'], im['el']) for im in v['images']] + [(s, 'srcset') for im in v['images'] for s in re.split(r',\s*', im['srcset']) if s]
        srcs += [(u, b['el']) for b in v['bg_images'] for u in urls_in(b['value'])] + [(s, 'source') for s in v['media_src'] if s]
        for s, el in srcs:
            s = s.strip().split(' ')[0]
            if not s or s.startswith(('data:', 'blob:')):
                continue
            kind = stock_kind(s)
            host = urlparse(s).netloc
            if kind:
                stock.append({'kind': kind, 'url': s[:160], 'el': el, 'view': v['viewport']})
            elif host and host != target_host and not host.startswith('127.0.0.1'):
                hot.append({'url': s[:160], 'el': el})
    raw = (desk.get('html') or '') + '\n' + (desk.get('css') or '')
    for kind, rx in STOCK_PATTERNS:
        for m in re.finditer(rx, raw, re.I):
            stock.append({'kind': kind, 'url': m.group(0)[:160], 'el': 'html/css', 'view': desk['viewport']})
    for h in (static or {}).get('stock_hits', []):
        stock.append({'kind': h['kind'], 'url': h['url'], 'el': f"{h['file']}:{h['line']}", 'view': 'source'})
    uniq = {}
    for s in stock:
        uniq.setdefault(s['url'], s)
    unsplash = [s for s in uniq.values() if s['kind'] == 'unsplash']
    other = [s for s in uniq.values() if s['kind'] != 'unsplash']
    if unsplash:
        ids = sorted({re.sub(r'^.*?(photo-[0-9]+-[0-9a-f]+).*$', r'\1', s['url']) for s in unsplash})
        add(F, 'F-UNSPLASH', 'critical', 'all', f'фото Unsplash по памяти (хотлинк): {len(unsplash)} адрес(ов)',
            {'ids': ids[:10], 'where': [s['el'] for s in unsplash[:6]]},
            'Remove every Unsplash URL; use only files from assets/ with captions from assets/README.md; empty slots get a '
            'placeholder captioned "placeholder".')
    if other:
        add(F, 'F-STOCK', 'critical', 'all', f"стоковые/заглушечные сервисы: {', '.join(sorted({s['kind'] for s in other}))}",
            {'urls': [s['url'] for s in other[:8]], 'where': [s['el'] for s in other[:6]]},
            'Remove hotlinked stock and placeholder-service images; use assets/ files or a local placeholder.')
    hot_u = sorted({h['url'] for h in hot})
    if hot_u:
        add(F, 'F-HOTLINK', 'major', 'all', f'внешние картинки (не сток): {len(hot_u)}', {'urls': hot_u[:8]},
            'Copy approved assets into public/assets/ and reference them locally; no external image URLs.', 'external', allowed)

    # ---------- подписи и alt против assets/README.md
    caps_all = []
    for im in desk['images']:
        if not im['visible']:
            continue
        stem = os.path.splitext(os.path.basename(urlparse(im['src']).path))[0].lower()
        if im['src'].startswith('data:'):
            continue
        caps_all.append({'el': im['el'], 'file': stem, 'src': im['src'][:160], 'alt': im['alt'], 'caption': im['caption']})
    if assets is not None:
        for c in caps_all:
            if not c['file'] or stock_kind(c.get('src') or ''):
                continue
            row = assets.get(c['file']) or next((r for k, r in assets.items() if c['file'].startswith(k) or k.startswith(c['file'])), None)
            if not row:
                add(F, 'F-CAPTION', 'major', desk['viewport'], f"картинка «{c['file']}» не описана в assets/README.md",
                    {'img': c}, f"Image {c['el']}: use only files listed in assets/README.md.")
                continue
            if c['caption'] is not None and row['caption'] and norm_text(c['caption']) != norm_text(row['caption']):
                add(F, 'F-CAPTION', 'critical', desk['viewport'], f"подпись не из README: «{c['caption'][:60]}»",
                    {'expected': row['caption'], 'found': c['caption'], 'file': row['file']},
                    f"Figure with {row['file']}: caption must be exactly \"{row['caption']}\" (assets/README.md).")
            if c['alt'] is not None and row['alt'] and norm_text(c['alt']) != norm_text(row['alt']):
                add(F, 'F-CAPTION', 'major', desk['viewport'], f"alt не из README: «{(c['alt'] or '')[:60]}»",
                    {'expected': row['alt'], 'found': c['alt'], 'file': row['file']},
                    f"Image {row['file']}: alt must be exactly \"{row['alt']}\" (assets/README.md).")
    elif caps_all:
        sus = [c for c in caps_all if c['caption'] and re.search(r'\b(1[89]|20)\d{2}\b|[A-ZА-Я][a-zа-я]+,\s*[A-ZА-Я]', c['caption'])]
        add(F, 'F-CAPTION', 'info', desk['viewport'], f'подписей/alt без README для сверки: {len(caps_all)}'
            + (f'; с местом/датой (проверить глазами): {len(sus)}' if sus else ''), {'captions': caps_all[:8]})

    # ---------- числа против facts.md и copy.md
    seen_nums, page_nums = set(), []
    for v in views:
        for l in v['leaves']:
            if '[PLACEHOLDER' in l['text'].upper():
                continue
            for rawn, val in extract_numbers(l['text']):
                if re.fullmatch(r'0\d', rawn.strip()):
                    continue                       # 01/02/03 — это K3-NUMBERED, не факт
                key = (val, rawn)
                if key in seen_nums:
                    continue
                seen_nums.add(key)
                page_nums.append({'raw': rawn, 'value': val, 'el': l['el'], 'context': l['text'][:80]})
    if facts_nums is not None or copy_nums is not None:
        known = (facts_nums or set()) | (copy_nums or set())
        unknown = [n for n in page_nums if n['value'] not in known]
        if unknown:
            add(F, 'F-NUMBERS', 'critical', desk['viewport'], f'чисел нет в facts.md/copy.md: {len(unknown)}',
                {'numbers': unknown[:12]},
                'Every number must come from brief/facts.md; replace invented numbers with [PLACEHOLDER] and list them in REPORT.md: '
                + ', '.join(n['raw'] for n in unknown[:6]) + '.')
    elif page_nums:
        big = [n for n in page_nums if not (re.fullmatch(r'\d', n['raw']))]
        if big:
            add(F, 'F-NUMBERS', 'info', desk['viewport'], f'чисел на странице (нет facts.md для сверки): {len(big)}',
                {'numbers': big[:12]})

    # ---------- текст против copy.md, заглушки, отзывы
    if copy_text is not None:
        cn = norm_text(copy_text)
        cand = [b for b in desk['blocks'] if len(b['text'].split()) >= 3 and '[PLACEHOLDER' not in b['text'].upper()]
        miss = [b for b in cand if norm_text(b['text']) not in cn]
        if cand and len(miss) / len(cand) > 0.10:
            add(F, 'F-COPY', 'major', desk['viewport'],
                f'текст не из copy.md: {len(miss)} из {len(cand)} блоков ({len(miss) / len(cand):.0%} > 10 %)',
                {'examples': [{'el': b['el'], 'text': b['text'][:90]} for b in miss[:10]]},
                'Use brief/copy.md verbatim: do not rewrite, shorten or add copy; missing copy becomes [PLACEHOLDER: what].')
    filler = []
    alltext = ' \n'.join(b['text'] for b in desk['blocks'])
    for rx in FILLER_PATTERNS:
        for m in re.finditer(rx, alltext, re.I):
            filler.append(m.group(0))
    if filler:
        add(F, 'F-FILLER', 'critical', desk['viewport'], f"текст-заглушка: {', '.join(sorted(set(filler))[:6])}",
            {'hits': sorted(set(filler))[:10]}, 'Replace filler text with copy from brief/copy.md or [PLACEHOLDER: what].')
    quotes = [b for b in desk['blocks'] if b['quote'] and len(b['text'].split()) >= 5]
    if quotes:
        if copy_text is not None or facts_nums is not None:
            src = norm_text(copy_text or '')
            unsourced = [q for q in quotes if norm_text(q['text']) not in src]
            if unsourced:
                add(F, 'F-QUOTE', 'critical', desk['viewport'], f'отзыв/цитата без источника: {len(unsourced)}',
                    {'examples': [q['text'][:90] for q in unsourced[:4]]},
                    'Remove testimonials that are not in brief/copy.md or brief/facts.md.')
        else:
            add(F, 'F-QUOTE', 'info', desk['viewport'], f'отзывы/цитаты — проверить источник: {len(quotes)}',
                {'examples': [q['text'][:90] for q in quotes[:4]]})

    # ---------- наложение текста (E/01: календарь K3; W2: плашка навигации на H1)
    ov = [dict(o, view=v['viewport']) for v in views for o in v.get('text_overlaps', [])]
    if ov:
        add(F, 'V-OVERLAP', 'major', ov[0]['view'], f"текст накладывается на текст: {len(ov)} пар(ы), напр. «{ov[0]['a']}» × «{ov[0]['b']}»",
            {'pairs': ov[:8]}, f"At {ov[0]['view']}: \"{ov[0]['a']}\" ({ov[0]['a_el']}) overlaps \"{ov[0]['b']}\" ({ov[0]['b_el']}) "
            f"near y={ov[0]['y']}px; separate them (at least 8 px) without changing their sizes.")

    # ---------- мобильная версия
    for v in views:
        w = int(v['viewport'].split('x')[0])
        if w >= 768:
            continue
        nav_ok = any(n['links'] >= 2 for n in v['nav']['navs']) or any(t['top'] < v['vh'] * 0.3 for t in v['nav']['toggles'])
        if not nav_ok:
            add(F, 'M-NAV', 'critical', v['viewport'], 'навигация не видна (нет меню-кнопки и нет ≥ 2 ссылок в nav/header)',
                {'navs': v['nav']['navs'][:3], 'toggles': v['nav']['toggles'][:3]},
                f"At {v['viewport']}: show navigation — a menu button in the header (>= 44x44 px) that opens the section links, "
                'or visible anchor links.')
        paras = [l for l in v['leaves'] if l['tag'] in ('p', 'li', 'dd', 'blockquote') and len(l['text'].split()) >= 8]
        if paras:
            small = [l for l in paras if l['fs'] < 16]
            med = statistics.median(l['fs'] for l in paras)
            if len(small) / len(paras) > 0.25:
                add(F, 'M-BODY-16', 'major', v['viewport'], f'тело текста < 16 px: {len(small)} из {len(paras)} абзацев, медиана {med:.1f} px',
                    {'examples': [{'el': l['el'], 'fs': l['fs']} for l in small[:5]]},
                    f"At {v['viewport']}: body text at least 16 px (line-height 1.4–1.6); keep desktop sizes unchanged.")
        if v['scroll_w'] > w + 1:
            add(F, 'M-OVERFLOW', 'critical', v['viewport'], f"горизонтальная прокрутка: {v['scroll_w'] - w} px",
                {'scroll_width': v['scroll_w']}, f"At {v['viewport']}: remove horizontal overflow (find the element wider than the "
                'viewport; see shot.py overflow_elements).')
        hero_m = v.get('hero')
        if hero_m and hero_m['h1_lines'] > 4:
            add(F, 'M-H1-LINES', 'minor', v['viewport'], f"h1 занимает {hero_m['h1_lines']} строк (> 4)",
                {'lines': hero_m['h1_lines']}, f"At {v['viewport']}: fit the H1 in at most 4 lines (reduce size with clamp()).")

    # ---------- слепая зона DOM: canvas/WebGL или почти пустая разметка
    if len(desk['leaves']) < 12 or desk.get('canvas_share', 0) > 0.5:
        add(F, 'E-LOW-DOM', 'minor', desk['viewport'],
            f"мало текста в DOM ({len(desk['leaves'])} узл.) или canvas/видео {desk.get('canvas_share', 0):.0%} первого экрана — "
            'проверки по разметке неполны, смотреть кадры глазами', {'leaves': len(desk['leaves']), 'canvas_share': desk.get('canvas_share')})

    # ---------- справочно: шрифты и цвета
    fam = {}
    for l in desk['leaves']:
        f = family_first(l['ff'])
        fam[f] = fam.get(f, 0) + 1
    add(F, 'I-FONTS', 'info', desk['viewport'], 'шрифты по числу текстовых узлов',
        {'families': dict(sorted(fam.items(), key=lambda x: -x[1])[:8]),
         'declared_in_source': dict(sorted(((static or {}).get('declared_fonts') or {}).items(), key=lambda x: -x[1])[:10])})
    if blocked:
        add(F, 'I-BLOCKED', 'info', 'all', f'внешних запросов заблокировано: {len(blocked)}', {'urls': blocked[:10]})
    return F


def summarize(F, allowed):
    counts = {s: 0 for s in SEV_ORDER}
    for f in F:
        counts[f['severity']] += 1
    sig = sorted({f['id'] for f in F if f['id'].startswith('K3-') and f['severity'] in ('major', 'minor')})
    sig_major = sorted({f['id'] for f in F if f['id'].startswith('K3-') and f['severity'] == 'major'})
    fab = sorted({f['id'] for f in F if f['id'].startswith('F-') and f['severity'] in ('critical', 'major')})
    mob = sorted({f['id'] for f in F if f['id'].startswith('M-') and f['severity'] in ('critical', 'major')})
    m1104 = {'K3-ACCENT-WORD': 'm7', 'K3-CAPS': 'm8', 'K3-GLASS': 'm15', 'K3-THREE-CARDS': 'm17', 'K3-EYEBROW': 'm30',
             'K3-NUMBERED': 'm31', 'K3-META-DOTS': 'm32', 'K3-MONO-LABELS': 'm33', 'K3-ARROWS': 'm34', 'K3-GRADIENT-TEXT': 'm3'}
    markers = sorted({m1104[f['id']] for f in F if f['id'] in m1104 and f['severity'] in ('major', 'minor')})
    return {'counts': counts, 'k3_signatures': sig, 'k3_signatures_major': sig_major, 'fabrications': fab, 'mobile': mob,
            'ui1104_markers_hit': markers,
            'acceptance_hint': {'H2_no_k3_signature': not sig_major, 'B_honesty': not fab, 'D2_mobile': not mob},
            'allowed_by_brief': sorted(allowed)}


def to_md(res):
    s = res['summary']
    L = [f"# k3_checks · {res['target']} · {res['created']}", '',
         f"Итог: critical {s['counts']['critical']} · major {s['counts']['major']} · minor {s['counts']['minor']} · info {s['counts']['info']}; "
         f"приметы K3 (major): {', '.join(s['k3_signatures_major']) or '—'}; выдумки: {', '.join(s['fabrications']) or '—'}; "
         f"мобильная: {', '.join(s['mobile']) or '—'}; маркеры ui 11/04: {', '.join(s['ui1104_markers_hit']) or '—'}.", '',
         '| Проверка | Тяжесть | Вид | Найдено | Правка для NOTES (EN) |', '|---|---|---|---|---|']
    for f in sorted(res['findings'], key=lambda x: (SEV_ORDER[x['severity']], x['id'])):
        if f['severity'] == 'info':
            continue
        L.append(f"| {f['id']} | {f['severity']} | {f['view']} | {f['message'].replace('|', '/')} | {f['fix_en'].replace('|', '/')} |")
    return '\n'.join(L) + '\n'


def cmd_page(a):
    allowed = {x.strip() for x in (a.allow or '').split(',') if x.strip()}
    unknown = allowed - ALLOW_KEYS
    if unknown:
        raise SystemExit(f'неизвестные ключи --allow: {sorted(unknown)}; допустимые: {sorted(ALLOW_KEYS)}')
    fg = free_gb()
    if fg is not None and fg < a.min_free_gb:
        print(json.dumps({'error': f'свободно {fg:.1f} ГБ < {a.min_free_gb} ГБ — браузер не запускаю'}, ensure_ascii=False))
        return 3
    local = not a.target.startswith(('http://', 'https://'))
    block = a.block_external or (local and not a.allow_external)
    src = a.src or (os.path.dirname(os.path.abspath(a.target)) if local and os.path.isfile(a.target)
                    else (os.path.abspath(a.target) if local else None))
    static = scan_sources(src) if src else None
    facts_nums = load_numbers_file(a.facts)
    copy_text = md_plain(open(a.copy, encoding='utf-8').read()) if a.copy else None
    copy_nums = {v for _, v in extract_numbers(copy_text)} if copy_text is not None else None
    assets = parse_assets_readme(a.assets_readme)
    t0 = time.time()
    url, views, blocked = collect(a.target, [v.strip() for v in a.views.split(',') if v.strip()], a.ignore_selector,
                                  block, a.shots)
    F = analyze(url, views, static, facts_nums, copy_text, copy_nums, assets, allowed, blocked)
    res = {'tool': 'k3_checks.py', 'version': VERSION, 'target': a.target, 'url': url,
           'created': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'seconds': round(time.time() - t0, 1),
           'views': [v['viewport'] for v in views], 'inputs': {'facts': a.facts, 'copy': a.copy, 'assets_readme': a.assets_readme,
                                                              'src': (static or {}).get('root'), 'block_external': block},
           'static': {k: v for k, v in (static or {}).items() if k != 'stock_hits'} if static else None,
           'shots': [v.get('shot') for v in views if v.get('shot')],
           'summary': summarize(F, allowed),
           'findings': sorted(F, key=lambda x: (SEV_ORDER[x['severity']], x['id']))}
    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)), exist_ok=True)
        open(a.json, 'w', encoding='utf-8').write(json.dumps(res, ensure_ascii=False, indent=1))
    if a.md:
        os.makedirs(os.path.dirname(os.path.abspath(a.md)), exist_ok=True)
        open(a.md, 'w', encoding='utf-8').write(to_md(res))
    s = res['summary']
    print(json.dumps({'target': a.target, 'seconds': res['seconds'], 'summary': s,
                      'top': [f"{f['severity']} {f['id']}: {f['message']}" for f in res['findings'] if f['severity'] != 'info'][:14]},
                     ensure_ascii=False, indent=1))
    return 2 if (s['counts']['critical'] or s['counts']['major']) else 0


# ---------------------------------------------------------------- сторож потока stream-json
FORBID_TOOLS_DEFAULT = 'FetchURL,WebSearch,WebFetch,AgentSwarm,Agent,CronCreate,AskUserQuestion,EnterPlanMode'
FORBID_CMD = [
    ('global-install', r'\b(?:npm|pnpm|yarn|bun)\s+(?:i|install|add)\b[^\n;&|]*\s(?:-g|--global)\b|\bnpm\s+-g\b'),
    ('sudo', r'(?:^|[;&|]\s*|\s)sudo\s'),
    ('git-mutation', r'\bgit\s+(?:push|reset|checkout|clean|rebase|commit|restore|stash|rm)\b'),
    ('rm-rf-outside', r'\brm\s+-[a-z]*r[a-z]*f?\s+(?:/|~|\.\.)'),
    ('pipe-to-shell', r'\b(?:curl|wget)\b[^\n|]*\|\s*(?:ba|z)?sh\b'),
    ('home-access', r'(?:~|/home/[^/\s]+)/(?:\.ssh|\.kimi-code|\.claude|\.config|Документы|Documents)'),
    ('docker', r'\bdocker\s+(?:run|compose|build)\b'),
]
TOOL_WAIT_LIMIT = {'FetchURL': 60, 'WebSearch': 60, 'WebFetch': 60, 'ReadMediaFile': 120, 'Read': 60, 'Write': 120,
                   'Edit': 60, 'Grep': 60, 'Glob': 60, 'Bash': 360, 'TaskStop': 60, 'WaitFor': 660, 'Skill': 60}


def resolve_stream(path):
    if os.path.isdir(path):
        runs = sorted((d for d in os.listdir(path) if os.path.isfile(os.path.join(path, d, 'stream.jsonl'))), reverse=True)
        if runs:
            return os.path.join(path, runs[0], 'stream.jsonl')
        if os.path.isfile(os.path.join(path, 'stream.jsonl')):
            return os.path.join(path, 'stream.jsonl')
        raise SystemExit(f'в {path} нет stream.jsonl')
    return path


def watch(path, a, now=None):
    path = resolve_stream(path)
    calls, pending, retries, bad = [], {}, [], 0
    session_id, final_text, version = None, None, None
    with open(path, encoding='utf-8', errors='replace') as f:
        for n, raw in enumerate(f):
            raw = raw.strip()
            if not raw:
                continue
            try:
                m = json.loads(raw)
            except json.JSONDecodeError:
                bad += 1
                continue
            role, typ = m.get('role'), m.get('type')
            if role == 'meta' and typ == 'system.version':
                version = m.get('version')
            elif role == 'meta' and typ == 'turn.step.retrying':
                retries.append({'status': m.get('status_code'), 'attempt': m.get('failed_attempt'), 'msg': (m.get('error_message') or '')[:80]})
            elif role == 'meta' and typ == 'session.resume_hint':
                session_id = m.get('session_id')
            elif role == 'assistant':
                if m.get('content'):
                    final_text = m['content'][-600:]
                for c in m.get('tool_calls') or []:
                    fn = c.get('function') or {}
                    try:
                        args = json.loads(fn.get('arguments') or '{}')
                    except json.JSONDecodeError:
                        args = {'_raw': (fn.get('arguments') or '')[:200]}
                    rec = {'i': len(calls), 'line': n, 'id': c.get('id'), 'name': fn.get('name', '?'), 'args': args, 'result': None}
                    calls.append(rec)
                    pending[c.get('id')] = rec
            elif role == 'tool':
                rec = pending.pop(m.get('tool_call_id'), None)
                if rec:
                    content = m.get('content')
                    rec['result'] = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    running = a.running
    idle = round((now or time.time()) - os.path.getmtime(path)) if running else None
    reasons, verdict = [], 'ok'

    def flag(level, msg):
        nonlocal verdict
        reasons.append({'level': level, 'msg': msg})
        if level == 'act' or (level == 'warn' and verdict == 'ok'):
            verdict = level if verdict != 'act' else verdict

    def arg_text(c):
        return json.dumps(c['args'], ensure_ascii=False, sort_keys=True)[:400]

    expect = [x.strip() for x in a.expect_first.split(',') if x.strip()]
    first = calls[0] if calls else None
    if first and expect and first['name'] not in expect:
        flag('warn', f"первый вызов {first['name']} {arg_text(first)[:120]} — ожидали {'/'.join(expect)} (задача не прочитана?)")
    forbid = {x.strip() for x in a.forbid_tools.split(',') if x.strip()}
    for c in calls:
        if c['name'] in forbid:
            flag('act', f"запрещённый инструмент {c['name']} (вызов №{c['i'] + 1}): {arg_text(c)[:120]}")
            break
    installs, allowed_pk, kinds_seen = [], {x.strip().lower() for x in (a.allowed_packages or '').split(',') if x.strip()}, set()
    for c in calls:
        if c['name'] != 'Bash':
            continue
        cmd = str(c['args'].get('command') or c['args'].get('cmd') or c['args'].get('_raw') or '')
        for kind, rx in FORBID_CMD:
            if kind not in kinds_seen and re.search(rx, cmd, re.I):
                kinds_seen.add(kind)
                flag('act' if kind != 'docker' else 'warn', f'команда «{kind}» (вызов №{c["i"] + 1}): {cmd[:120]}')
        for m in re.finditer(r'\b(?:npm|pnpm|yarn|bun)\s+(?:i|install|add)\s+([^;&|\n]+)', cmd):
            pk = [p for p in m.group(1).split() if not p.startswith('-')]
            installs += pk
            if a.allowed_packages is not None:
                extra = [p for p in pk if re.sub(r'@[^/]*$', '', p).lower() not in allowed_pk]
                if extra:
                    flag('warn', f'установка вне разрешённого списка: {extra}')
    keyseq = [(c['name'], arg_text(c)) for c in calls]
    run, best = 1, (1, None)
    for i in range(1, len(keyseq)):
        run = run + 1 if keyseq[i] == keyseq[i - 1] else 1
        if run > best[0]:
            best = (run, keyseq[i])
    if best[0] >= a.loop:
        flag('act', f'петля: один и тот же вызов {best[1][0]} подряд ×{best[0]}: {best[1][1][:100]}')
    counts = {}
    for k in keyseq:
        counts[k] = counts.get(k, 0) + 1
    for k, v in counts.items():
        if v >= a.loop + 2 and k[0] not in ('ReadMediaFile',):
            flag('warn', f'повтор вызова {k[0]} ×{v} за прогон: {k[1][:100]}')
            break
    fails = {}
    for c in calls:
        if c['name'] == 'Bash' and c['result'] and re.search(r'(?i)\b(error|failed|not found|exit code:? [1-9]|ENOENT|EADDRINUSE)\b', c['result']):
            k = arg_text(c)
            fails[k] = fails.get(k, 0) + 1
    for k, v in fails.items():
        if v >= 3:
            flag('act', f'одна и та же команда падает ×{v}: {k[:100]}')
            break
    edits = {}
    for c in calls:
        if c['name'] in ('Write', 'Edit'):
            p = c['args'].get('path') or c['args'].get('file_path') or '?'
            edits[p] = edits.get(p, 0) + 1
    churn = {p: v for p, v in edits.items() if v >= a.churn}
    if churn:
        flag('warn', f'файл переписывается снова и снова: {churn}')
    rm = [str(c['args'].get('path')) for c in calls if c['name'] == 'ReadMediaFile']
    iter_frames = [p for p in rm if a.iter is not None and re.search(rf'iter-0*{a.iter}/', p or '')]
    shot_runs = [c for c in calls if c['name'] == 'Bash' and 'shot.py' in str(c['args'])]
    taskstop = any(c['name'] == 'TaskStop' for c in calls)
    phase = 'finished' if session_id else ('waiting_tool' if pending else 'generating')
    if running and idle is not None:
        if phase == 'waiting_tool':
            last = list(pending.values())[-1]
            lim = TOOL_WAIT_LIMIT.get(last['name'], 300)
            if idle > lim:
                flag('act', f"инструмент {last['name']} без результата {idle} с (> {lim} с): {arg_text(last)[:100]}")
        elif phase == 'generating':
            if idle > a.idle_act:
                flag('act', f'нет новых строк {idle} с (> {a.idle_act} с) — модель молчит или зависла')
            elif idle > a.idle_warn:
                flag('warn', f'нет новых строк {idle} с (> {a.idle_warn} с) — длинный шаг (запись большого файла?)')
    streak = 0
    for r in reversed(retries):
        if r['status'] == 429:
            streak += 1
        else:
            break
    if streak >= 5:
        flag('warn', f'подряд {streak} повторов 429 (перегрузка): готовиться продолжить сессию позже')
    if phase == 'finished':
        if a.iter is not None and not iter_frames:
            flag('warn', f'прогон закончен, но кадры screenshots/iter-{a.iter}/ не прочитаны ReadMediaFile — итерацию не принимать')
        if a.frames and len(set(iter_frames)) < a.frames:
            flag('warn', f'прочитано кадров итерации {len(set(iter_frames))} из {a.frames}')
        if shot_runs and not taskstop:
            flag('warn', 'dev-сервер мог остаться в фоне: TaskStop не вызывался')
        if not final_text:
            flag('warn', 'нет финального сообщения (только мышление?) — смотреть REPORT.md и git diff')
        if verdict == 'ok':
            verdict = 'done'
    nxt = {'ok': 'ждать; следующий взгляд через 1–3 мин',
           'warn': 'посмотреть причины; если повторится на следующем взгляде — действовать',
           'act': 'SIGTERM группе процессов kimi (или дождаться сторожа), затем продолжить ту же сессию (-S) коротким '
                  'сообщением STOP (03-critique-messages.md, «прерывание») или откатить git',
           'done': 'приёмка: summary.json → кадры Claude → проверки (01-loop-protocol.md, фаза 5)'}[verdict]
    return {'stream': path, 'version': version, 'verdict': verdict, 'phase': phase, 'idle_s': idle, 'reasons': reasons,
            'first_call': {'name': first['name'], 'args': arg_text(first)[:160]} if first else None,
            'calls_total': len(calls), 'calls_by_tool': {k: sum(1 for c in calls if c['name'] == k) for k in sorted({c['name'] for c in calls})},
            'read_media_total': len(rm), 'iter_frames_read': len(set(iter_frames)), 'shot_runs': len(shot_runs),
            'taskstop': taskstop, 'installs': installs, 'retries': len(retries), 'retries_429_streak': streak,
            'session_id': session_id, 'final_text_tail': (final_text or '')[-300:], 'bad_lines': bad, 'next': nxt}


def cmd_watch(a):
    r = watch(a.stream, a)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 2 if r['verdict'] == 'act' else 0


# ---------------------------------------------------------------- ресайз без перезагрузки (ACCEPTANCE H5, W3: чёрный hero)
RESIZE_JS = r"""
() => {
  const vis = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && s.visibility !== 'hidden' && s.display !== 'none' && parseFloat(s.opacity || '1') > 0.1; };
  const vw = document.documentElement.clientWidth;
  const media = Array.from(document.querySelectorAll('video, img, canvas')).filter(m => { const r = m.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0 && r.width * r.height > vw * innerHeight * 0.15; });
  const mstate = media.slice(0, 4).map(m => ({tag: m.tagName.toLowerCase(), visible: vis(m),
    ready: m.tagName === 'VIDEO' ? m.readyState >= 2 : (m.tagName === 'IMG' ? (m.complete && m.naturalWidth > 0) : true),
    src: (m.currentSrc || m.src || '').slice(-60)}));
  const navLinks = Array.from(document.querySelectorAll('nav a[href], header a[href], nav button, header button')).filter(vis).length;
  const sw = Math.max(document.documentElement.scrollWidth, document.body ? document.body.scrollWidth : 0);
  return {vw, overflow_px: Math.max(0, sw - vw), nav_controls: navLinks, media: mstate};
}
"""


def cmd_resize(a):
    fg = free_gb()
    if fg is not None and fg < a.min_free_gb:
        print(json.dumps({'error': f'свободно {fg:.1f} ГБ < {a.min_free_gb} ГБ'}, ensure_ascii=False))
        return 3
    from playwright.sync_api import sync_playwright
    from PIL import Image, ImageChops, ImageStat
    import io
    target = a.target
    httpd = None
    if not target.startswith(('http://', 'https://')):
        import functools, http.server, socketserver, threading
        path = os.path.abspath(target)
        root, name = (path, '') if os.path.isdir(path) else (os.path.dirname(path), os.path.basename(path))
        safe_root(root)

        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *x):
                pass
        httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=root))
        httpd.daemon_threads = True
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        target = f'http://127.0.0.1:{httpd.server_address[1]}/{name}'
    big = [int(x) for x in a.desktop.split('x')]
    small = [int(x) for x in a.mobile.split('x')]
    steps, shots = [], []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            try:
                page = b.new_page(viewport={'width': big[0], 'height': big[1]})
                try:
                    page.goto(target, wait_until='networkidle', timeout=60000)
                except Exception:  # noqa: BLE001
                    pass
                page.wait_for_timeout(800)
                for label, (w, h) in (('desktop-before', big), ('mobile-after-resize', small), ('desktop-after-resize', big)):
                    if label != 'desktop-before':
                        page.set_viewport_size({'width': w, 'height': h})
                        page.wait_for_timeout(a.wait_ms)
                    st = page.evaluate(RESIZE_JS)
                    st['step'] = label
                    try:
                        png = page.screenshot(type='png', animations='disabled', timeout=15000)
                        shots.append(Image.open(io.BytesIO(png)).convert('RGB'))
                        if a.shots:
                            os.makedirs(a.shots, exist_ok=True)
                            shots[-1].save(os.path.join(a.shots, f'resize-{label}.jpg'), 'JPEG', quality=80)
                    except Exception as e:  # noqa: BLE001
                        st['shot_error'] = str(e)[:120]
                        shots.append(None)
                    steps.append(st)
            finally:
                b.close()
    finally:
        if httpd:
            httpd.shutdown(); httpd.server_close()
    problems = []
    for st in steps:
        if st['overflow_px'] > 0:
            problems.append(f"{st['step']}: горизонтальный вылет {st['overflow_px']} px")
        for m in st['media']:
            if not m['visible'] or not m['ready']:
                problems.append(f"{st['step']}: медиа первого экрана не показано через {a.wait_ms} мс ({m['tag']} {m['src']})")
    if steps and steps[1]['nav_controls'] == 0:
        problems.append('mobile-after-resize: навигация не видна после ресайза')
    diff = None
    if shots and shots[0] is not None and shots[-1] is not None and shots[0].size == shots[-1].size:
        diff = round(sum(ImageStat.Stat(ImageChops.difference(shots[0], shots[-1])).mean) / 3 / 255, 4)
        if diff > a.max_diff:
            problems.append(f'после возврата на {a.desktop} кадр отличается от исходного (средняя разница {diff} > {a.max_diff})')
    res = {'target': a.target, 'wait_ms': a.wait_ms, 'steps': steps, 'desktop_restore_diff': diff, 'problems': problems,
           'verdict': 'fail' if problems else 'pass'}
    print(json.dumps(res, ensure_ascii=False, indent=1))
    return 2 if problems else 0


# ---------------------------------------------------------------- самопроверка
def cmd_selftest(_a):
    ok = True

    def check(name, cond, got=None):
        nonlocal ok
        ok &= bool(cond)
        print(('PASS ' if cond else 'FAIL ') + name + ('' if cond else f' → {got}'))
    L, C, H = oklch((0xF4, 0xF1, 0xEA))
    check('oklch #F4F1EA ≈ (0.957, 0.010, 84)', abs(L - 0.957) < 0.01 and abs(C - 0.010) < 0.004 and 70 < H < 95, (L, C, H))
    check('warm light #F4F1EA', warm_class((0xF4, 0xF1, 0xEA)) == 'light')
    check('warm light #f4f4ec (E/01)', warm_class((0xf4, 0xf4, 0xec)) == 'light', oklch((0xf4, 0xf4, 0xec)))
    check('warm dark #14140c (E/01)', warm_class((0x14, 0x14, 0x0c)) == 'dark', oklch((0x14, 0x14, 0x0c)))
    check('neutral #fafafa not warm', warm_class((0xfa, 0xfa, 0xfa)) is None)
    check('cool #f4f6fb not warm', warm_class((0xf4, 0xf6, 0xfb)) is None, oklch((0xf4, 0xf6, 0xfb)))
    check('brand orange #e4002b not tint', warm_class((0xe4, 0x00, 0x2b)) is None)
    check('contrast #9ca3af/#fff = 2.54', contrast((0x9c, 0xa3, 0xaf), (255, 255, 255)) == 2.54, contrast((0x9c, 0xa3, 0xaf), (255, 255, 255)))
    check('contrast white on #6366f1 = 4.47', contrast((255, 255, 255), (0x63, 0x66, 0xf1)) == 4.47)
    nums = dict((r, v) for r, v in extract_numbers('Более 12 000+ клиентов, рейтинг 4,9 и 98 % довольных; с 2014 года; $1,250'))
    check('numbers 12 000+ → 12000', nums.get('12 000+') == '12000', nums)
    check('numbers 4,9 → 4.9', nums.get('4,9') == '4.9', nums)
    check('numbers 98 % → 98', any(v == '98' for v in nums.values()), nums)
    check('numbers $1,250 → 1250', any(v == '1250' for v in nums.values()), nums)
    check('norm_text quotes/dashes', norm_text('«Смена — за 5 минут»') == norm_text('"смена - за 5 минут"'))
    check('family_kind Fraunces serif', family_kind('"Fraunces", Georgia, serif') == 'serif')
    check('family_kind Inter sans', family_kind('Inter, system-ui, sans-serif') == 'sans')
    check('family_kind JetBrains mono', family_kind('"JetBrains Mono", monospace') == 'mono')
    check('family_kind unknown+serif fallback', family_kind('"Brand Display", serif') == 'serif')
    check('stock unsplash id', stock_kind('https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=1600') == 'unsplash')
    check('stock picsum', stock_kind('https://picsum.photos/800/600') == 'picsum')
    import tempfile
    lines = [{'role': 'meta', 'type': 'system.version', 'version': '2.0.2'},
             {'role': 'assistant', 'tool_calls': [{'id': 'c1', 'function': {'name': 'FetchURL', 'arguments': '{"url":"https://brand.example"}'}}]},
             {'role': 'tool', 'tool_call_id': 'c1', 'content': 'text'}]
    lines += [{'role': 'assistant', 'tool_calls': [{'id': f'd{i}', 'function': {'name': 'Bash', 'arguments': '{"command":"docker run x"}'}}]} for i in range(5)]
    with tempfile.NamedTemporaryFile('w', suffix='.jsonl', delete=False) as t:
        t.write('\n'.join(json.dumps(x) for x in lines))
    ns = argparse.Namespace(running=False, idle_warn=600, idle_act=1200, loop=4, churn=8, iter=None, frames=0,
                            allowed_packages=None, expect_first='Read,Skill,Glob,Grep,ReadMediaFile,TodoList', forbid_tools=FORBID_TOOLS_DEFAULT)
    r = watch(t.name, ns)
    os.unlink(t.name)
    check('watch: forbidden FetchURL → act', r['verdict'] == 'act' and any('FetchURL' in x['msg'] for x in r['reasons']), r['reasons'])
    check('watch: loop docker ×5 detected', any('петля' in x['msg'] for x in r['reasons']), r['reasons'])
    print('selftest:', 'OK' if ok else 'FAIL')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('page', help='приметы K3, выдумки, мобильная версия по отрисованной странице')
    p.add_argument('target')
    p.add_argument('--views', default='1440x900,390x844')
    p.add_argument('--facts'); p.add_argument('--copy'); p.add_argument('--assets-readme'); p.add_argument('--src')
    p.add_argument('--allow', default='', help='приметы, заказанные брифом: ' + ','.join(sorted(ALLOW_KEYS)))
    p.add_argument('--ignore-selector', default='', help='CSS-селектор чужих вставок (бейдж хостинга и т. п.)')
    p.add_argument('--block-external', action='store_true'); p.add_argument('--allow-external', action='store_true')
    p.add_argument('--shots', help='папка: первый экран каждого вьюпорта JPEG q80')
    p.add_argument('--json'); p.add_argument('--md'); p.add_argument('--min-free-gb', type=float, default=2.0)
    w = sub.add_parser('watch', help='сторож потока kimi -p stream-json')
    w.add_argument('stream')
    w.add_argument('--running', action='store_true', help='процесс ещё идёт: считать простой по mtime файла')
    w.add_argument('--idle-warn', type=int, default=600); w.add_argument('--idle-act', type=int, default=1200)
    w.add_argument('--loop', type=int, default=4); w.add_argument('--churn', type=int, default=8)
    w.add_argument('--iter', type=int); w.add_argument('--frames', type=int, default=0)
    w.add_argument('--allowed-packages')
    w.add_argument('--expect-first', default='Read,Skill,Glob,Grep,ReadMediaFile,TodoList')
    w.add_argument('--forbid-tools', default=FORBID_TOOLS_DEFAULT)
    r = sub.add_parser('resize', help='ресайз 1440 → 390 → 1440 без перезагрузки (ACCEPTANCE H5)')
    r.add_argument('target'); r.add_argument('--desktop', default='1440x900'); r.add_argument('--mobile', default='390x844')
    r.add_argument('--wait-ms', type=int, default=1000); r.add_argument('--max-diff', type=float, default=0.02)
    r.add_argument('--shots'); r.add_argument('--min-free-gb', type=float, default=2.0)
    sub.add_parser('selftest')
    a = ap.parse_args()
    return {'page': cmd_page, 'watch': cmd_watch, 'resize': cmd_resize, 'selftest': cmd_selftest}[a.cmd](a)


if __name__ == '__main__':
    sys.exit(main())
