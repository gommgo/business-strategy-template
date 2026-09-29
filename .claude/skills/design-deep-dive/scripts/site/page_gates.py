#!/usr/bin/env python3
"""page_gates.py — ворота собранной страницы: вердикт PASS / S / B по `page-gates.yaml` с порогами профиля бюджета.

Профиль `<page_type>@L<n>` — `07-seo-geo-performance-analytics/budgets.yaml` (исходы и вес уровня, исключения типа
`overrides`); умолчание уровня по типу страницы и правило лидогенерации услуг — `creative/01-creative-direction/
ambition-levels.yaml` (`defaults_by_page_type`, `levels[L0].appropriate_for.lead_services`). Браузер утилита не запускает,
она сводит JSON других утилит ворот. Метрику страницы воротами ставит только она; те же метрики, измеренные соседями,
идут в отчёт зеркалом (серьёзность D) и на вердикт не влияют; ворота эффектов и 3D — отдельными слоями отчёта.
  page_anatomy.py  → anatomy_desktop.json, anatomy_mobile.json (--anatomy DIR): LCP, CLS, TBT, INP-сценарий, вес, сторонние,
                     текст без JS, мета, формы и согласия, баннер cookie, призывы первого экрана, телефон, показ H1 во времени
  page_accept.py   → accept_<режим>.json (--accept DIR): LCP с троттлингом телефона, lazy и fetchpriority LCP-картинки,
                     постер видео первого экрана, размеры картинок, движение на 6-й секунде и петли всей страницы, reduce,
                     консоль
  motion_check.py  → results.json и gates.json (--motion DIR): петли всей страницы (2.2.2), вспышки (2.3.1), reduce записью
                     всей страницы; ворота эффектов — слоем; LCP, TBT, CLS и вес — зеркалом
  gate_check.py    → JSON ключа --json (--gate3d FILE …): ворота 3D — слоем, их провал — SG-WEIGHT-08 (D), ошибки консоли —
                     SG-CONTENT-04; LCP, CLS, TBT и вес страницы — зеркалом
  geo_probe.py     → <id>.json (--geo): флаги head-kit.yaml — коды, robots, боты, SSR, canonical, JSON-LD, OG
  ia_probe.py      → ia.json (--ia): мягкая 404 на шаблонах, меню в HTML, sitemap, hreflang, крошки (строки scope: site)
  axe-core         → JSON с violations (--axe): формат run_axe_targets.py (адреса узлов) или axe.run
  page-plan.yaml   → first_screen_policy, seo.indexable, x-gate-exception[{id, why, who, until}] (--plan)
  HTML и CSS       → заглушки и маркеры «ИИ-лендинга», признаки невидимого H1, clamp() кеглей (--html, --css)
Числа строк без профиля (доля текста без JS, вылет телефона, clamp, энтропия постера) — поле `limits` строки page-gates.yaml.
Строки без данных — SKIP: их проверяет человек, судья или соседняя утилита.

Код репозитория запускает утилиту соседним чекаутом: ../strategy/.claude/skills/design-deep-dive/scripts/site/page_gates.py.
  page_gates.py --profile landing-lead-services@L1 --anatomy DIR [--accept DIR] [--motion DIR] [--gate3d FILE …]
      [--geo FILE] [--ia FILE] [--axe FILE] [--plan FILE] [--html FILE] [--css FILE …] [--jurisdiction ru|eu|none]
      [--ai-bots-policy allow-all] [--ads-google] [--site-level L1] [--hot-mobile-share 0.6 --price-band mid] [--json]
  page_gates.py --resolve landing-lead-services@L1 [--site-level L1]   # профиль (JSON): id, level, page_type, outcome,
                                                                        # weight, all_levels, log
  page_gates.py --conditions        # условия замера budgets.yaml: окно первого экрана, телефон, десктоп, замок тишины
  page_gates.py --selftest [--gates FILE]
Код выхода: 1 — есть B; 0 — нет B; 2 — ошибка вызова. Замер без троттлинга сети помечается `lab-unthrottled`.

Модуль для утилит замера (kbpaths.use("site"); import page_gates): resolve_profile(), profile_value(), conditions(),
cdp_network(), mobile_device(), heavy_lock() — условия замера и тишина машины из budgets.yaml, одно место на все ворота;
PAUSE_LABELS и pause_label_re_js() — подписи механизма паузы движения.
"""
import argparse
import contextlib
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
BUDGETS = os.path.join(DIR07, 'budgets.yaml')
GATES = os.path.join(DIR07, 'page-gates.yaml')
CHECKLIST = os.path.join(ROOT, '09-ai-generation-evaluation', 'site-checklist.yaml')
AMBITION = str(kbpaths.kb('creative', '01-creative-direction', 'ambition-levels.yaml'))
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
AXE_KEY = ('h1', 'cta', 'consent', 'lead')   # классы узлов color-contrast, провал которых — B (профиль I 08/03 §8)
AXE_S = {'target-size', 'image-alt', 'frame-title', 'html-has-lang', 'html-lang-valid'}     # SG-A11Y-02
PLACEHOLDER_RX = re.compile(r'lorem ipsum|\[placeholder\]|\bfeature [1-6]\b|\bjohn doe\b|\bjane doe\b|\bfictional (?:brand|company|demo)|'
                            r'\bdemo content\b|@example\.(?:com|org)|\bexample\.com\b|заглушк[аи] отзыв|\bтекст заглушк|вымышленн(?:ый|ая) (?:бренд|компани)', re.I)
FAKE_ACTIVITY_RX = re.compile(r'только что (?:купил|записал|оформил|заказал)|(?:\d+|несколько) (?:человек|посетител\w*) (?:смотр|сейчас)|'
                              r'сейчас смотр\w+ \d+|just (?:purchased|bought|signed up)|\d+ people are (?:viewing|looking)|someone in [A-Z]\w+ (?:just|recently)', re.I)
COUNTDOWN_RX = re.compile(r'(?:setDate\s*\(\s*\w+\.getDate\(\)\s*\+|getDate\(\)\s*\+\s*\d|countdown|обратн\w+ отсч)', re.I)
PROMO_RX = re.compile(r'акци|скидк|sale|offer ends|до конца', re.I)
# Подписи механизма паузы движения (кнопка, переключатель, выбор) — основы слов: по ним page_accept.py и motion_check.py
# узнают паузу для WCAG 2.2.2 (кнопка «Вращение» эталона blender — тоже пауза)
PAUSE_LABELS = ('пауз', 'останов', 'стоп', 'выключ', 'запуст', 'воспроизв', 'движени', 'анимац', 'вращени',
                'pause', 'stop', 'play', 'resume', 'motion', 'animation', 'rotat')


def pause_label_re_js():
    """Литерал регулярного выражения JS по PAUSE_LABELS (без учёта регистра) для кода страницы."""
    return '/(' + '|'.join(re.escape(x) for x in PAUSE_LABELS) + ')/i'


def load_yaml(path):
    import yaml
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


_LIMITS = {}


def use_gates(path=None):
    """Строки ворот для вердикта: page-gates.yaml или черновик (--gates). Поле `limits` строки — числа проверок, которые
    не берутся из профиля (доля текста без JS, вылет телефона, clamp, энтропия и площадь постера, прозрачность H1)."""
    doc = load_yaml(path or GATES)
    rows = [x for x in doc.get('gates') or [] if isinstance(x, dict) and x.get('id')]
    _LIMITS.clear()
    _LIMITS.update({x['id']: x.get('limits') or {} for x in rows})
    _LIMITS['_threshold'] = {x['id']: (x.get('threshold') or {}).get('S') for x in rows if isinstance(x.get('threshold'), dict)}
    _LIMITS['_path'] = path or GATES
    return doc


def gate_limit(gid, key):
    """Число из поля limits строки ворот; нет — ошибка с адресом (порога в коде нет)."""
    if not _LIMITS:
        use_gates()
    v = (_LIMITS.get(gid) or {}).get(key)
    if v is None:
        raise KeyError(f'нет limits.{key} у строки {gid} ({_LIMITS.get("_path")})')
    return v


def deep_merge(base, over):
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(out.get(k, {}), v) if isinstance(v, dict) and isinstance(out.get(k), dict) else copy.deepcopy(v)
    return out


def load_budgets():
    return load_yaml(BUDGETS)


def load_levels():
    """Уровни creative: таблица умолчаний по типу страницы и правило лидогенерации услуг. Нет файла — None (профиль с
    уровнем в id разрешается и без него)."""
    try:
        return load_yaml(AMBITION)
    except FileNotFoundError:
        return None


def level_defaults(levels):
    """Тип страницы → (уровень по умолчанию, раздел): таблица `defaults_by_page_type` и её раздел `proposed`."""
    out = {}
    dpt = (levels or {}).get('defaults_by_page_type') or {}
    for part, table in (('active', dpt), ('proposed', dpt.get('proposed') or {})):
        for lv, pts in table.items():
            if lv in LEVELS and isinstance(pts, list):
                for pt in pts:
                    out.setdefault(pt, (lv, part))
    return out


def lead_rule(levels):
    """Правило лидогенерации услуг — поля `levels[id=L0].appropriate_for.lead_services`."""
    for row in (levels or {}).get('levels') or []:
        if isinstance(row, dict) and row.get('id') == 'L0':
            return ((row.get('appropriate_for') or {}).get('lead_services')) or {}
    return {}


def resolve_profile(profile_id, budgets=None, site_level=None, hot_mobile_share=None, price_band=None, levels=None):
    """<page_type>@L<n> → профиль (outcome, weight, all_levels) + журнал решений. Без уровня в id — умолчание типа и
    правило лидогенерации из ambition-levels.yaml; уровень страницы не выше уровня сайта; исключения типа — overrides."""
    budgets = budgets if budgets is not None else load_budgets()
    levels = levels if levels is not None else load_levels()
    log = []
    if '@' in profile_id:
        page_type, level = profile_id.split('@', 1)
    else:
        page_type, level = profile_id, None
    known = level_defaults(levels)
    if levels is None:
        if level is None:
            raise ValueError('уровня в профиле нет, а таблицы умолчаний (creative ambition-levels.yaml) нет рядом')
        log.append('тип страницы не сверен: нет creative ambition-levels.yaml')
    elif page_type not in known:
        raise ValueError(f'page_type {page_type!r} нет в таблице умолчаний ambition-levels.yaml#defaults_by_page_type')
    elif known[page_type][1] == 'proposed':
        log.append(f'тип {page_type} — proposed (таблица creative, раздел proposed)')
    if level is None:
        level = known[page_type][0]
        log.append(f'уровень по умолчанию для {page_type}: {level} (ambition-levels.yaml#defaults_by_page_type)')
        rule = lead_rule(levels)
        if rule and page_type == rule.get('page_type'):
            share_min, bands = rule.get('hot_mobile_share_min'), rule.get('price_bands') or []
            if hot_mobile_share is None or price_band is None:
                level = rule.get('no_data') or level
                log.append(f'лидогенерация услуг: данных о трафике или цене нет → {level} и вопрос в бриф')
            elif share_min is not None and hot_mobile_share >= share_min and price_band in bands:
                level = 'L0'
                log.append(f'горячий трафик с телефонов {hot_mobile_share:.0%} ≥ {share_min:.0%} и price_band {price_band} '
                           f'→ L0 (правило лидогенерации услуг)')
            else:
                level = rule.get('otherwise') or level
                log.append(f'правило лидогенерации услуг не выполнено → {level}')
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


def profile_value(prof, path, device=None, key='goal'):
    """Порог профиля по пути через точку ('outcome.lcp_ms_lab.<device>.goal', 'weight.first_screen_kb'): метка <device>
    заменяется устройством; узел {mobile, desktop} — значением устройства; узел {goal, poor} — ключом key (goal)."""
    cur = prof
    for part in path.replace('<device>', device or '').split('.'):
        if not part:
            continue
        cur = cur.get(part) if isinstance(cur, dict) else None
        if cur is None:
            return None
    if isinstance(cur, dict) and device in cur:
        cur = cur[device]
    if isinstance(cur, dict):
        cur = cur.get(key, cur.get('max'))
    return cur if isinstance(cur, (int, float)) and not isinstance(cur, bool) else None


# ---------------------------------------------------------------- условия замера (budgets.yaml conditions)
def conditions(budgets=None):
    """Условия лаборатории для утилит замера: окно первого экрана, телефон (дескриптор, CPU, сеть), десктоп (окно, DPR),
    замок тишины. Одно место — budgets.yaml conditions."""
    c = (budgets if budgets is not None else load_budgets()).get('conditions') or {}
    mob, desk = c.get('lab_mobile') or {}, c.get('lab_desktop') or {}
    net = mob.get('network') or {}
    vp = desk.get('viewport') or {}
    return {'window_after_load_s': (c.get('first_screen') or {}).get('window_after_load_s'),
            'mobile': {'descriptor': mob.get('descriptor'), 'cpu_slowdown': mob.get('cpu_slowdown'),
                       'down_kbps': net.get('down_kbps'), 'up_kbps': net.get('up_kbps'), 'rtt_ms': net.get('rtt_ms')},
            'desktop': {'width': vp.get('width'), 'height': vp.get('height'), 'dpr': vp.get('dpr'),
                        'cpu_slowdown': desk.get('cpu_slowdown')},
            'lock': (c.get('quiet') or {}).get('lock')}


def window_ms(budgets=None):
    """Окно первого экрана после load, мс (conditions.first_screen.window_after_load_s)."""
    return int(round(float(conditions(budgets)['window_after_load_s']) * 1000))


def cdp_network(cond=None):
    """Параметры CDP Network.emulateNetworkConditions телефона из conditions.lab_mobile.network (кбит/с → байт/с)."""
    m = (cond or conditions())['mobile']
    return {'offline': False, 'latency': m['rtt_ms'], 'downloadThroughput': m['down_kbps'] * 1000 / 8,
            'uploadThroughput': m['up_kbps'] * 1000 / 8}


def mobile_device(pw, cond=None):
    """Дескриптор телефона Playwright (conditions.lab_mobile.descriptor): размер, DPR, касание; в UA — HeadlessChrome, как
    у самого браузера. Автоматизацию утилиты не маскируют (без подмены UA и без --disable-blink-features)."""
    dev = dict(pw.devices[(cond or conditions())['mobile']['descriptor']])
    dev['user_agent'] = dev['user_agent'].replace('Chrome/', 'HeadlessChrome/')
    return dev


def _ancestor_flock(path):
    """Держит ли замок процесс-предок через flock(1) (`flock … <замок> python3 утилита.py`): повторная блокировка того же
    файла из дочернего процесса ждала бы родителя до таймаута. Только Linux (/proc); ошибка — False."""
    name = os.path.basename(path)
    try:
        pid = os.getppid()
        for _ in range(16):
            if pid <= 1:
                break
            with open(f'/proc/{pid}/cmdline', 'rb') as fh:
                args = [x.decode('utf-8', 'replace') for x in fh.read().split(b'\0') if x]
            if args and os.path.basename(args[0]) == 'flock' and any(x.endswith(name) for x in args[1:]):
                return True
            with open(f'/proc/{pid}/stat', encoding='utf-8', errors='replace') as fh:
                pid = int(fh.read().rsplit(')', 1)[1].split()[1])
    except (OSError, ValueError, IndexError):
        return False
    return False


@contextlib.contextmanager
def heavy_lock(domains=(), timeout=900.0, budgets=None):
    """Тихая машина для замера времени (conditions.quiet): общий тяжёлый замок (тот же, что slot_run.py --heavy), затем
    общий замок браузера, затем замки браузера доменов — порядок slot_run. Замок, который уже держит обёртка (slot_run.py
    передаёт SLOT_RUN_HOLDS, flock — процесс-предок), повторно не берётся. Отдаёт список взятых замков."""
    taken = []
    with contextlib.ExitStack() as st:
        for name, dom in lock_plan(domains, budgets=budgets):
            path = kbpaths.lock_path(name, dom)
            if _ancestor_flock(path):
                continue
            st.enter_context(kbpaths.lock(name, dom, timeout=timeout))
            taken.append(path)
        yield taken


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
    """accept_<режим>.json page_accept.py → {(устройство, троттлинг): отчёт}. Устройство и троттлинг — поля `device` и
    `throttle` отчёта; у отчёта без них — по имени режима (mobile…, …_thr…). Прогоны с кликом (…_click) и тёмной темой
    (…_dark) — не основной замер: в сводку не идут."""
    out = {}
    for fp in sorted(glob.glob(os.path.join(dirpath or '', 'accept_*.json'))):
        with open(fp, encoding='utf-8') as f:
            d = json.load(f)
        mode = str(d.get('mode') or os.path.basename(fp)[7:-5])          # accept_<mode>.json
        if '_click' in mode or '_dark' in mode:
            continue
        dev = d.get('device') or ('mobile' if 'mobile' in mode else 'desktop')
        thr = d.get('throttle') if isinstance(d.get('throttle'), bool) else '_thr' in mode
        out[(dev, thr)] = d
    return out


def accept_main(acc):
    """Основной прогон отчёта page_accept (без reduce): раздел no_preference."""
    return (acc or {}).get('no_preference') or {}


def load_motion(path):
    """Отчёт motion_check.py: папка --out (results.json и gates.json) → {'results', 'gates', 'level'}; нет — None."""
    if not path:
        return None
    d = path if os.path.isdir(path) else os.path.dirname(path)
    res, gts = os.path.join(d, 'results.json'), os.path.join(d, 'gates.json')
    if not os.path.exists(res):
        return None
    with open(res, encoding='utf-8') as f:
        results = json.load(f)
    gates = {}
    if os.path.exists(gts):
        with open(gts, encoding='utf-8') as f:
            gates = json.load(f)
    return {'results': results, 'gates': gates, 'level': gates.get('level') or (results.get('_meta') or {}).get('level'),
            'path': d}


def load_gate3d(paths):
    """JSON gate_check.py --json (файл на прогон: телефон, десктоп, reduce) → список отчётов."""
    out = []
    for p in paths or []:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        d['_path'] = p
        out.append(d)
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
    """Строка вердикта. source — утилита-источник замера; mirror — метрика страницы, измеренная соседом: серьёзность не
    выше D, на вердикт не влияет."""
    def __init__(self, gid, device, status, value, threshold, severity, note='', source=None, mirror=False):
        self.__dict__.update(id=gid, device=device, status=status, value=value, threshold=threshold, severity=severity,
                             note=note, source=source, mirror=mirror)


def cmp_outcome(gid, dev, value, node, note='', source=None):
    goal, poor = dev_val(node, dev, 'goal'), dev_val(node, dev, 'poor')
    if value is None:
        return Gate(gid, dev, 'SKIP', None, f'S>{goal} B>{poor}', '-', note or 'нет данных', source)
    if poor is not None and value > poor:
        return Gate(gid, dev, 'FAIL', value, poor, 'B', note, source)
    if goal is not None and value > goal:
        return Gate(gid, dev, 'FAIL', value, goal, 'S', note, source)
    return Gate(gid, dev, 'PASS', value, goal, '-', note, source)


def cmp_weight(gid, dev, value, limit, note='', source=None):
    if value is None or limit is None:
        return Gate(gid, dev, 'SKIP', value, limit, '-', note or 'нет данных', source)
    return Gate(gid, dev, 'FAIL' if value > limit else 'PASS', round(value, 1), limit, 'S' if value > limit else '-', note,
                source)


def mirror_gate(gid, dev, value, limit, source, note=''):
    """Метрика страницы, которую измерил сосед: сравнение с тем же порогом профиля, серьёзность — D (зеркало), вердикт
    ставит строка-владелец по своему методу."""
    note = f'зеркало: {source}' + (f'; {note}' if note else '')
    if value is None or limit is None:
        return Gate(gid, dev, 'SKIP', value, limit, '-', note, source, mirror=True)
    bad = value > limit
    return Gate(gid, dev, 'FAIL' if bad else 'PASS', round(value, 3) if isinstance(value, float) else value, limit,
                'D' if bad else '-', note, source, mirror=True)


def accept_weight(acc):
    """Вес первого экрана из прогона page_accept без замедления сети: (КБ, источник) или (None, None)."""
    a = accept_main(acc)
    if not a or a.get('weight_measured') is False or a.get('first_screen_total_kb') is None:
        return None, None
    return a['first_screen_total_kb'], 'page_accept'


def lcp_element_gate(dev, tag, has_lcp, acc, h1item):
    """SG-PERF-06: LCP есть и не canvas; LCP-картинка без lazy (B) и с fetchpriority=high (S — page_accept); H1 не
    выпадает из LCP (признаки в HTML, CSS и показе H1)."""
    if not has_lcp:
        return Gate('SG-PERF-06', dev, 'FAIL', 'нет LCP', 'LCP есть', 'B')
    if tag == 'CANVAS':
        return Gate('SG-PERF-06', dev, 'FAIL', tag, 'не canvas', 'B')
    lcp = g(acc, 'lcp') or {}
    rsev, rwhat = h1item
    if lcp.get('lazy'):
        return Gate('SG-PERF-06', dev, 'FAIL', 'lazy', 'LCP-картинка без lazy', 'B', source='page_accept')
    if rwhat:
        # H1 первого кадра невидим → в Chromium выпадает из LCP (creative E/01; поле CrUX — Chrome)
        return Gate('SG-PERF-06', dev, 'FAIL', rwhat[:90], 'H1 без opacity 0, маски строк, скрытия скриптом', rsev,
                    'creative E/01 (Chromium 153): честно — только transform; opacity ≥ 0,01 и clip-path — LCP раньше показа')
    if (lcp.get('tag') or '').upper() == 'IMG' and lcp.get('fp') != 'high':
        return Gate('SG-PERF-06', dev, 'FAIL', 'без fetchpriority=high', 'LCP-картинка с fetchpriority=high', 'S',
                    source='page_accept')
    return Gate('SG-PERF-06', dev, 'PASS', tag or '?', 'H1/картинка/постер', '-',
                'lazy/fetchpriority — только из page_accept' if not acc else '')


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
    """Чем подтверждён трекинг до выбора — запросы, отправляющие данные (не загрузка скрипта), и cookie трекинга."""
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
    """«H1 только после JS» — B, только если H1 нет в сыром HTML. Если H1 в HTML есть, а сравнение текста упало (innerText
    склеивает слова на скрытых <br> — опыт K/03: ru-matemarketing, телефон), текст сверяется без пробелов и регистра."""
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


# ---------------------------------------------------------------- H1 и LCP (creative E/01), контраст по узлам
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


def h1_reveal_evidence(raw, css='', near_zero=None):
    """Признаки «H1 первого кадра невидим» в сыром HTML и CSS (creative E/01): hidden — opacity 0 (стиль, класс opacity-0,
    правило CSS, анимация из 0), visibility: hidden, класс invisible у H1 или 4 ближайших предков, скрипт разбивки с маской
    строк; near_zero — opacity 0 < x < near_zero (SG-PERF-06 limits.opacity_near_zero; Framer appear 0.001) или clip-path —
    H1 остаётся кандидатом, но LCP раньше показа."""
    near_zero = near_zero if near_zero is not None else gate_limit('SG-PERF-06', 'opacity_near_zero')
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
                elif v is not None and v < near_zero:
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


def h1_runtime(d, near_zero):
    """Показ H1 во времени (page_anatomy.py, поле h1_paint): признак для страниц, где HTML и CSS признаков не несут
    (скрытие скриптом в SPA). → (hidden, near_zero) — строка признака или None."""
    hp = d.get('h1_paint') or {}
    op = hp.get('first_op')
    if not isinstance(op, (int, float)) or hp.get('in_first_screen') is False:
        return None, None
    seen = f", виден с {hp['t_visible']} мс" if hp.get('t_visible') is not None else ', до конца замера не виден'
    if op <= 0 or hp.get('first_hidden'):
        return f'показ H1: первый кадр невидим (opacity {op}{seen})', None
    if op < near_zero:
        return None, f'показ H1: первый кадр opacity {op}{seen}'
    return None, None


def lcp_h1_item(d, rv, near_zero=None):
    """SG-PERF-06: H1 первого экрана не стал кандидатом LCP, а LCP — другой текст (лид, H2): S при признаке невидимого
    первого кадра в HTML, CSS или в показе H1 во времени (page_anatomy), D без признака (лид может быть больше H1 по площади);
    H1 — кандидат, но проявляется из opacity ≈ 0 или clip-path — D (время LCP раньше видимости; допустимо при раскрытии
    ≤ 800 мс)."""
    near_zero = near_zero if near_zero is not None else gate_limit('SG-PERF-06', 'opacity_near_zero')
    rt_hidden, rt_near = h1_runtime(d, near_zero)
    rv = {'hidden': rv['hidden'] + ([rt_hidden] if rt_hidden else []), 'near_zero': rv['near_zero'] + ([rt_near] if rt_near else [])}
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
        return ('D', what + '; признаков в HTML и показе H1 нет — проверить появление H1 (или лид больше H1)')
    if cand and rv['near_zero']:
        return ('D', 'H1 проявляется: ' + rv['near_zero'][0] + ' — время LCP раньше видимости')
    return ('-', '')


def cta_texts(anatomy):
    """Тексты призывов (кнопки filled и outline) из анатомии — для класса узла cta."""
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
    """Класс узла color-contrast (формат run_axe_targets.py: in_h1, cookie, in_form, action, first_screen, in_header,
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
             headkit=None, ai_bots_policy='allow-all', ads_google=False, css_text=None, motion=None, gate3d=None):
    accept = accept or {}
    headkit = headkit or dict(HK_DEFAULT)
    pi = plan_info(plan)
    R = []
    oc, wt, al = prof['outcome'], prof['weight'], prof['all_levels']
    cta_fs = {}
    nz = gate_limit('SG-PERF-06', 'opacity_near_zero')
    rv = h1_reveal_evidence(html_text, css_text, nz) if (html_text or css_text) else {'hidden': [], 'near_zero': []}
    for dev, d in anatomy.items():
        s = d.get('summary') or {}
        # SG-PERF-01/02: LCP — сначала page_accept с троттлингом (телефон), иначе анатомия как диагностика
        acc = accept_main(accept.get((dev, dev == 'mobile')))
        if g(acc, 'lcp', 't') is not None:
            R.append(cmp_outcome('SG-PERF-01' if dev == 'mobile' else 'SG-PERF-02', dev, g(acc, 'lcp', 't'),
                                 oc['lcp_ms_lab'], 'page_accept' + (' --throttle' if dev == 'mobile' else ''), source='page_accept'))
        else:
            R.append(cmp_outcome('SG-PERF-01' if dev == 'mobile' else 'SG-PERF-02', dev, s.get('lcp_ms'), oc['lcp_ms_lab'],
                                 'lab-unthrottled: диагностика, не приёмка' if dev == 'mobile' else 'anatomy, без троттлинга'))
        # SG-PERF-03: CLS — окно сессии web-vitals (fin.wv_cls), а не сумма всех сдвигов (summary.cls_session): сумма
        # завышает CLS прокрутки (опыт K/03: ru-azbukaokon телефон — сумма 0,42, web-vitals 0,15)
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
        R.append(lcp_element_gate(dev, (last.get('tag') or '').upper(), bool(lcp_list), acc, lcp_h1_item(d, rv, nz)))
        # SG-PERF-09: тяжёлые виджеты до ввода
        fs_t = g(d, 'first_screen', 't', default=None)
        tp = g(d, 'network', 'third_party', default=[]) or []
        widgets = [t['domain'] for t in tp if set(t.get('cats') or []) & {'chat', 'maps', 'video', 'booking', 'social'}
                   and (fs_t is None or (t.get('first_t') or 0) <= fs_t)]
        R.append(Gate('SG-PERF-09', dev, 'FAIL' if widgets else 'PASS', ','.join(widgets) or '—', 'по видимости/нажатию',
                      'S' if widgets else '-'))
        # WEIGHT: вес — анатомия (без замедления сети); нет её числа — прогон page_accept без --throttle
        fs_kb, fs_src = s.get('first_screen_kb'), None
        if fs_kb is None:
            fs_kb, fs_src = accept_weight(accept.get((dev, False)))
        R.append(cmp_weight('SG-WEIGHT-01', dev, fs_kb, dev_val(wt['first_screen_kb'], dev), source=fs_src))
        R.append(cmp_weight('SG-WEIGHT-02', dev, s.get('session_kb'), dev_val(wt['session_kb'], dev)))
        R.append(cmp_weight('SG-WEIGHT-03', dev, g(d, 'first_screen', 'by_type_kb', 'script'), dev_val(wt['js_first_screen_kb'], dev)))
        R.append(cmp_weight('SG-WEIGHT-04', dev, g(d, 'network', 'by_type_kb', 'font'), dev_val(wt['fonts_kb'], dev)))
        before = [t for t in tp if fs_t is None or (t.get('first_t') or 0) <= fs_t]
        R.append(cmp_weight('SG-WEIGHT-05', dev, len(before), wt['third_party_origins_before_input']['max'],
                            'сторонние eTLD+1 в окне первого экрана'))
        R.append(cmp_weight('SG-WEIGHT-06', dev, sum(t.get('kb') or 0 for t in before), wt['third_party_first_screen_kb']['max'],
                            'КБ домена за сессию — верхняя оценка'))
        R.append(cmp_weight('SG-WEIGHT-07', dev, g(d, 'nav', 'html_kb'), al.get('html_transfer_kb', {}).get('goal'), 'HTML по сети'))
        # SG-WEIGHT-09: видео первого экрана без действия — отдельной цифрой, только D (порог по уровню — EG-WEIGHT-04 ворот
        # эффектов, вес первого экрана целиком — SG-WEIGHT-01)
        vid = g(d, 'first_screen', 'by_type_kb', 'media') or 0
        if not vid:
            R.append(Gate('SG-WEIGHT-09', dev, 'PASS', 0, 'видео отдельно', '-', 'видео в окне первого экрана нет'))
        else:
            R.append(Gate('SG-WEIGHT-09', dev, 'FAIL', round(vid, 1), 'видео отдельно', 'D',
                          'есть видео без действия: постер, reduce = 0 байт, вертикальный файл телефону (SITE-PERF-13); '
                          'порог по уровню — EG-WEIGHT-04'))
        # SG-SEO-02: noindex при индексируемой — B; нет title или canonical — S; нет lang — D
        if s.get('noindex'):
            R.append(Gate('SG-SEO-02', dev, 'FAIL' if pi['indexable'] else 'PASS', 'noindex', 'по seo.indexable',
                          'B' if pi['indexable'] else '-', 'индексируемая по плану' if pi['indexable'] else 'noindex по плану'))
        else:
            sev, what = worst([('S', 'title') if not s.get('title_len') else ('-', ''),
                               ('S', 'canonical') if not s.get('canonical') else ('-', ''),
                               ('D', 'lang') if not s.get('lang') else ('-', '')])
            R.append(Gate('SG-SEO-02', dev, 'FAIL' if what else 'PASS', ','.join(what) or 'ok', 'title, canonical (S); lang (D)', sev))
        # SG-SEO-03: нет H1 — S; больше одного — D
        h1 = s.get('h1_n')
        if h1 is None:
            R.append(Gate('SG-SEO-03', dev, 'SKIP', None, 'ровно 1', '-'))
        else:
            R.append(Gate('SG-SEO-03', dev, 'PASS' if h1 == 1 else 'FAIL', h1, 'нет H1 — S; > 1 — D',
                          '-' if h1 == 1 else ('S' if h1 == 0 else 'D')))
        # SG-GEO-01: H1 только после JS — B; CTA или цены после JS — S; доля текста без JS ниже limits — S или D
        if s.get('nojs_h1') is None:
            R.append(Gate('SG-GEO-01', dev, 'SKIP', None, 'H1, CTA, цены в HTML', '-'))
        else:
            ratio = s.get('nojs_text_ratio')
            items = [h1_nojs_item(d, s), ('S', 'cta-js-only') if not s.get('nojs_cta') else ('-', '')]
            if s.get('nojs_prices') is False:
                items.append(('S', 'prices-js-only'))
            r_s, r_d = gate_limit('SG-GEO-01', 'nojs_ratio_s'), gate_limit('SG-GEO-01', 'nojs_ratio_d')
            if ratio is not None:
                items.append(('S', f'ratio {ratio:.2f} < {r_s}') if ratio < r_s else (('D', f'ratio {ratio:.2f} < {r_d}') if ratio < r_d else ('-', '')))
            sev, what = worst(items)
            R.append(Gate('SG-GEO-01', dev, 'FAIL' if what else 'PASS', ','.join(what) or (f'ratio {ratio}' if ratio is not None else 'ok'),
                          f'H1 — B; CTA, цены, < {r_s} — S; < {r_d} — D', sev, f"цены: {s.get('nojs_prices')}"))
        # SG-MOB-01, 02
        if dev == 'mobile':
            ov = s.get('overflow_x_px')
            zoomed = s.get('layout_zoomed')
            ov_max = gate_limit('SG-MOB-01', 'overflow_px')
            if ov is None and zoomed is None:
                R.append(Gate('SG-MOB-01', dev, 'SKIP', None, 'нет переполнения', '-'))
            elif zoomed or ((ov or 0) > ov_max and zoomed is None):
                R.append(Gate('SG-MOB-01', dev, 'FAIL', f'{ov} px, zoomed={zoomed}', 'область телефона не расширена', 'B'))
            elif (ov or 0) > ov_max:
                # scrollWidth больше экрана, но область не расширена — переполнение скрыто overflow-x (опыт K/03:
                # en-headspace — дорожка карусели 1 307 px под html,body{overflow-x:hidden}); прокрутки у человека нет
                R.append(Gate('SG-MOB-01', dev, 'FAIL', f'{ov} px, zoomed=False', 'область телефона не расширена', 'D',
                              'переполнение скрыто overflow-x — проверить свайпом на iOS'))
            else:
                R.append(Gate('SG-MOB-01', dev, 'PASS', f'{ov} px, zoomed={zoomed}', f'≤ {ov_max} px', '-'))
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
                # до выбора только загрузка библиотек (gtm.js, SDK) без отправки событий и без cookie трекинга —
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
            # РФ — B (LR-RU-05, 152-ФЗ ст. 18.1); ЕС — S (LR-EU-06: уведомление при сборе, serious)
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
    # SG-CONTENT-07: призыв в первом экране по политике плана
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
    # устройства без анатомии: LCP и LCP-элемент — по page_accept, вес — его прогон без замедления сети
    for dev in sorted({k[0] for k in accept} - set(anatomy)):
        acc = accept_main(accept.get((dev, dev == 'mobile')) or accept.get((dev, dev != 'mobile')))
        lcp = g(acc, 'lcp') or {}
        gid = 'SG-PERF-01' if dev == 'mobile' else 'SG-PERF-02'
        R.append(cmp_outcome(gid, dev, lcp.get('t'), oc['lcp_ms_lab'], 'page_accept', source='page_accept'))
        if acc:
            R.append(lcp_element_gate(dev, (lcp.get('tag') or '').upper(), bool(lcp), acc, ('-', '')))
        kb, src = accept_weight(accept.get((dev, False)))
        R.append(cmp_weight('SG-WEIGHT-01', dev, kb, dev_val(wt['first_screen_kb'], dev), source=src))
    # SG-PERF-14, SG-PERF-16: размеры картинок и постер видео первого экрана (page_accept)
    R.extend(eval_media(accept))
    # SG-A11Y-03, -04, -07: движение и reduce — методы page_accept и motion_check
    R.extend(eval_motion_a11y(accept, motion))
    # SG-CONTENT-04: консоль (page_accept; зонд 3D site_probe.py — строка WEB-07 отчёта gate_check.py)
    cons = [m for acc in accept.values() for m in (accept_main(acc).get('console') or []) if str(m).startswith(('error', 'pageerror'))]
    probe_err = sum(int(r.get('value') or 0) for rep in gate3d or [] for r in rep.get('rows') or []
                    if r.get('id') == 'WEB-07' and isinstance(r.get('value'), (int, float)))
    if accept or gate3d:
        n = len(cons) + probe_err
        src = '+'.join(x for x, on in (('page_accept', bool(accept)), ('site_probe', bool(gate3d))) if on)
        R.append(Gate('SG-CONTENT-04', 'page', 'FAIL' if n else 'PASS', n, '0 ошибок консоли', 'S' if n else '-',
                      '; '.join(str(c)[:60] for c in cons[:2]) + (f'; зонд 3D: {probe_err}' if probe_err else ''), src))
    # SG-WEIGHT-08: ворота 3D — у владельца ассета, страница за чужие байты не блокируется (D)
    if gate3d:
        R.append(eval_weight08(gate3d))
    # метрики страницы, измеренные соседями, — зеркалом (D)
    R.extend(neighbour_mirrors(prof, motion, gate3d))
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


def eval_media(accept):
    """SG-PERF-14 (картинки первого экрана с размерами) и SG-PERF-16 (видео первого экрана и LCP: LCP — не VIDEO, у видео
    есть poster, энтропия постера и площадь постера против видео и холста — limits строки) по отчёту page_accept."""
    out = []
    for dev in sorted({k[0] for k in accept}):
        a = accept_main(accept.get((dev, dev == 'mobile')) or accept.get((dev, dev != 'mobile')))
        if not a:
            continue
        noimg = [i for i in (g(a, 'dom', 'imgs') or []) if i.get('above') and not i.get('wh')]
        out.append(Gate('SG-PERF-14', dev, 'FAIL' if noimg else 'PASS', ', '.join(str(i.get('src')) for i in noimg[:3]) or '—',
                        'картинки первого экрана с width/height', 'S' if noimg else '-', source='page_accept'))
        media = a.get('media_first')
        if media is None:
            continue
        bpp_min, area_min = gate_limit('SG-PERF-16', 'poster_bpp_min'), gate_limit('SG-PERF-16', 'poster_area_min')
        items = []
        if ((a.get('lcp') or {}).get('tag') or '').upper() == 'VIDEO':
            items.append('LCP первого экрана — VIDEO')
        for m in media:
            if m.get('kind') == 'video' and not m.get('poster'):
                items.append(f"видео {m.get('src') or m.get('sel')}: нет poster")
            elif m.get('kind') == 'video' and m.get('poster_bpp') is not None and m['poster_bpp'] < bpp_min:
                items.append(f"постер {m.get('poster_src') or ''} {m['poster_bpp']:.3f} бит/пикс < {bpp_min}")
            if m.get('cover_share') is not None and m['cover_share'] < area_min:
                items.append(f"{'видео' if m.get('kind') == 'video' else 'холст'} {m.get('sel')}: постер {m['cover_share']:.2f} "
                             f"его площади < {area_min}")
        if media or items:
            out.append(Gate('SG-PERF-16', dev, 'FAIL' if items else 'PASS', '; '.join(items)[:170] or f'медиа первого экрана: {len(media)}',
                            f'LCP не VIDEO; poster ≥ {bpp_min} бит/пикс; постер ≥ {area_min} площади видео и холста',
                            'S' if items else '-', 'энтропия — байты постера × 8 / видимая площадь (порог Chromium)', 'page_accept'))
    return out


MODE_DEV = (('desk', 'desktop'), ('mob', 'mobile'))


def motion_verdicts(motion):
    """gates.json motion_check → {(id, режим): строка}."""
    return {(r.get('id'), r.get('mode')): r for r in ((motion or {}).get('gates') or {}).get('rows') or []}


def eval_motion_a11y(accept, motion):
    """SG-A11Y-03 (2.2.2, B): первый экран на 6-й секунде и петли всей страницы — page_accept и motion_check; SG-A11Y-04
    (2.3.1, B): вспышки покадрово — motion_check, сомнительное — глазами; SG-A11Y-07 (reduce, S): видео, движение
    первого экрана и пауз записи всей страницы — page_accept и motion_check (порог — creative EG-A11Y-06)."""
    out = []
    res = (motion or {}).get('results') or {}
    mv = motion_verdicts(motion)
    for mode, dev in MODE_DEV:
        md = (res.get(mode) or {}).get('derived') or {}
        a = accept_main(accept.get((dev, False)) or accept.get((dev, True)))
        items, src, whole = [], [], False
        if a:
            src.append('page_accept')
            m6 = a.get('motion_6s') or {}
            if m6.get('moving') and not m6.get('pause_control'):
                items.append(f"первый экран движется на 6-й с без паузы ({m6.get('pct')} %, видео {m6.get('videos_playing')})")
            lp = a.get('loops') or {}
            whole = whole or lp.get('scope') == 'page'
            if lp.get('without_pause'):
                items.append('петли без паузы: ' + ', '.join(str(x) for x in lp['without_pause'][:3]))
        if md:
            src.append('motion_check')
            whole = True
            if md.get('moving_6s_without_pause'):
                items.append('первый экран на 6-й с без паузы (motion_check)')
            if md.get('loops_without_pause'):
                items.append('петли без паузы (motion_check): ' + ', '.join(str(x) for x in md['loops_without_pause'][:3]))
        if not src:
            continue
        out.append(Gate('SG-A11Y-03', dev, 'FAIL' if items else 'PASS', '; '.join(items)[:170] or 'движения > 5 с без паузы нет',
                        'пауза с именем или стоп ≤ 5 с', 'B' if items else '-',
                        '' if whole else 'только первый экран: петли ниже — motion_check или page_accept без --first-screen-only',
                        '+'.join(src)))
    for mode, dev in MODE_DEV:
        md = (res.get(mode) or {}).get('derived') or {}
        if not md:
            continue
        ff = md.get('flash_fail')
        if ff is None:
            out.append(Gate('SG-A11Y-04', dev, 'SKIP', None, '≤ 3 вспышек/с', '-', 'запись не разобрана — проверить глазами',
                            'motion_check'))
        else:
            out.append(Gate('SG-A11Y-04', dev, 'FAIL' if ff else 'PASS', f"доля поля {md.get('flash_area_frac')}", '≤ 3 вспышек/с',
                            'B' if ff else '-', 'сомнительное (глитч ИИ-видео, заставка) — глазами', 'motion_check'))
    items, src = [], []
    for (dev, thr), acc in sorted(accept.items()):
        rm = (acc or {}).get('reduce') or {}
        if not rm:
            continue
        src.append('page_accept')
        if (rm.get('media_kb') or 0) > 0:
            items.append(f"{dev}: видео в reduce {rm['media_kb']} КБ")
        items += [f'{dev}: {x}' for x in ((rm.get('motion') or {}).get('fail') or [])]
    for gid in ('EG-A11Y-05', 'EG-A11Y-06', 'EG-A11Y-07'):
        r = mv.get((gid, 'rm'))
        if r:
            src.append('motion_check')
            if r.get('verdict') == 'FAIL':
                items.append(f"{gid}: {r.get('found')} (порог {r.get('threshold')})")
    if src:
        out.append(Gate('SG-A11Y-07', 'page', 'FAIL' if items else 'PASS', '; '.join(items)[:170] or 'reduce чистый',
                        '0 байт видео; движение ≤ порога creative EG-A11Y-06 на записи всей страницы', 'S' if items else '-',
                        '', '+'.join(sorted(set(src)))))
    return out


def eval_weight08(gate3d):
    """SG-WEIGHT-08 (D): провал ворот 3D (доля 3D, вызовы, reduce) — исправляет владелец ассета; страница блокируется
    только исходами SG-PERF."""
    bad = [f"{r.get('id')} {r.get('check')}: {r.get('value')} > {r.get('limit')}" for rep in gate3d for r in rep.get('rows') or []
           if not r.get('mirror') and r.get('status') == 'FAIL' and r.get('severity') in ('B', 'S')]
    return Gate('SG-WEIGHT-08', 'page', 'FAIL' if bad else 'PASS', '; '.join(bad)[:170] or 'ворота 3D пройдены',
                'ворота 3D — у владельца ассета', 'D' if bad else '-', 'страница блокируется только исходами SG-PERF', 'gate_check')


MIRROR_MOTION = (   # метрика results.json motion_check → строка-владелец
    ('vitals.lcp_ms', {'desktop': 'SG-PERF-02', 'mobile': 'SG-PERF-01'}, 'без замедления сети'),
    ('vitals.tbt_ms', 'SG-PERF-05', 'TBT после FCP'),
    ('cls.window_max', 'SG-PERF-03', 'наибольшее окно сессии'),
    ('net.first_kb', 'SG-WEIGHT-01', 'окно первого экрана'),
    ('net.session_kb', 'SG-WEIGHT-02', 'сессия после прокрутки'),
    ('net.font_kb', 'SG-WEIGHT-04', 'шрифты за сессию'),
)


def owner_threshold(prof, gid, dev):
    """Порог строки-владельца (threshold.S вида «profile.<путь>» в page-gates.yaml) для зеркала."""
    if not _LIMITS:
        use_gates()
    ref = str((_LIMITS.get('_threshold') or {}).get(gid) or '')
    return profile_value(prof, ref[len('profile.'):], dev) if ref.startswith('profile.') else None


def dig(d, path):
    cur = d
    for k in path.split('.'):
        cur = cur.get(k) if isinstance(cur, dict) else None
        if cur is None:
            return None
    return cur


def neighbour_mirrors(prof, motion, gate3d):
    """Зеркала: LCP, TBT, CLS и вес страницы, измеренные motion_check и зондом 3D, — против того же профиля, D."""
    out = []
    res = (motion or {}).get('results') or {}
    for mode, dev in MODE_DEV:
        r = res.get(mode)
        if not isinstance(r, dict) or r.get('error'):
            continue
        for path, gid, note in MIRROR_MOTION:
            gid = gid[dev] if isinstance(gid, dict) else gid
            out.append(mirror_gate(gid, dev, dig(r, path), owner_threshold(prof, gid, dev), 'motion_check', note))
    for rep in gate3d or []:
        dev = 'mobile' if rep.get('mode') == 'mobile' else 'desktop'
        for row in rep.get('rows') or []:
            gid = row.get('mirror')
            if gid and isinstance(row.get('value'), (int, float)):
                out.append(mirror_gate(gid, dev, row['value'], owner_threshold(prof, gid, dev), 'site_probe',
                                       f"{row.get('check')}{' (reduce)' if rep.get('reduced') else ''}"))
    return out


def layers(motion, gate3d):
    """Слои отчёта: ворота эффектов (motion_check) и ворота 3D (gate_check) — итог по серьёзности."""
    out = {}
    if motion:
        rows = (motion.get('gates') or {}).get('rows') or []
        fails = [r for r in rows if r.get('verdict') == 'FAIL']
        out['effects'] = {'tool': 'motion_check.py', 'level': motion.get('level'), 'path': motion.get('path'),
                          **{k: sum(1 for r in fails if r.get('severity') == k) for k in ('B', 'S', 'D')},
                          'na': sum(1 for r in rows if r.get('verdict') == 'N/A'),
                          'fails': [f"{r.get('id')} {r.get('mode')} {r.get('severity')}" for r in fails][:16]}
    if gate3d:
        out['three_d'] = [{'probe': rep.get('probe'), 'mode': rep.get('mode'), 'reduced': rep.get('reduced'),
                           **(rep.get('summary') or {})} for rep in gate3d]
    return out


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
        bad = abs((ci or 0) - (bl or 0)) > gate_limit('SG-NAV-02', 'crumbs_vs_markup_pct')
        out.append(Gate('SG-NAV-02', 'site', 'FAIL' if bad else 'PASS', f'крошки {ci} %, разметка {bl} %', 'разметка = видимому', 'D' if bad else '-'))
    return out


def eval_axe(axe, ctas=None):
    """SG-A11Y-01, 02. color-contrast — B только у ключевых узлов (H1, лид первого экрана, призыв, согласие и
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
    """SG-A11Y-08: кегли на clamp() — максимум не больше limits.clamp_ratio_max × минимума, иначе при зуме 200 % текст не
    растёт вдвое (WCAG 1.4.4). Читает <style>, атрибуты style и файлы --css; var() не раскрывает."""
    text = (css_or_html or '') + '\n' + (extra_css or '')
    px = {'px': 1.0, 'rem': 16.0, 'em': 16.0}
    kmax = gate_limit('SG-A11Y-08', 'clamp_ratio_max')
    found, bad = 0, []
    for m in CLAMP_RX.finditer(text):
        lo, hi = float(m.group(1)) * px[m.group(2).lower()], float(m.group(3)) * px[m.group(4).lower()]
        if lo <= 0:
            continue
        found += 1
        if hi / lo > kmax:
            bad.append(f'{m.group(1)}{m.group(2)}→{m.group(3)}{m.group(4)} (×{hi / lo:.1f})')
    if not found:
        return Gate('SG-A11Y-08', 'css', 'SKIP', 0, f'max ≤ {kmax} × min', '-', 'clamp() кеглей не найден; внешние CSS — передать --css')
    return Gate('SG-A11Y-08', 'css', 'FAIL' if bad else 'PASS', '; '.join(bad[:3]) or f'{found} clamp', f'max ≤ {kmax} × min',
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
            # S, которое снимается только проверкой (контраст без адресов узлов), а не записью в плане
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


def print_table(prof, results, lay=None):
    print(f"профиль {prof['id']} (уровень {prof['level']})" + ('; ' + '; '.join(prof['log']) if prof['log'] else ''))
    for r in results:
        print(f"{r.status:4} {r.severity}  {r.id:13} {r.device:7}  значение {str(r.value)[:40]:>14}  порог {str(r.threshold)[:34]:>10}  "
              f"{r.note}" + (f' [{r.source}]' if r.source and not r.mirror else ''))
    for k, v in (lay or {}).items():
        items = v if isinstance(v, list) else [v]
        for x in items:
            print(f"слой {k}: " + ', '.join(f'{a}={b}' for a, b in x.items() if a not in ('fails', 'path', 'probe')) +
                  (f"; провалы: {', '.join(x.get('fails') or [])}" if x.get('fails') else ''))
    v, nb, ns = verdict(results)
    print(f'вердикт: {v} (B: {nb}, S: {ns})')


def lock_plan(domains=(), holds=None, budgets=None):
    """Порядок замков тихой машины: тяжёлый, общий браузера, браузера доменов; без тех, что держит обёртка."""
    held = {x.strip() for x in (holds if holds is not None else os.environ.get('SLOT_RUN_HOLDS', '')).split(',') if x.strip()}
    plan = [(conditions(budgets)['lock'], None), ('browser', None)] + [('browser', d) for d in domains]
    return [(n, d) for n, d in plan if not (d is None and n in held)]


# ---------------------------------------------------------------- самопроверка
def selftest(gates_path=None):
    budgets = load_budgets()
    gates = use_gates(gates_path)
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
    # видео первого экрана отдельно; clamp кеглей
    f6 = copy.deepcopy(f2)
    f6['mobile']['first_screen']['by_type_kb']['media'] = 2000
    check('видео первого экрана 2 000 > бюджета 1 500 → только D (SG-WEIGHT-09; S — у SG-WEIGHT-01 и EG-WEIGHT-04)',
          {r.id: r for r in evaluate(prof, f6)}['SG-WEIGHT-09'].severity == 'D')
    f6['mobile']['first_screen']['by_type_kb']['media'] = 300
    check('видео первого экрана 300 КБ → D отдельной цифрой', {r.id: r for r in evaluate(prof, f6)}['SG-WEIGHT-09'].severity == 'D')
    check('clamp 40px→160px (×4) → S (SG-A11Y-08)', eval_clamp('<style>h1{font-size:clamp(40px, 8vw, 160px)}</style>').severity == 'S')
    check('clamp 2rem→4rem (×2) → PASS', eval_clamp('<p style="font-size: clamp(2rem, 1rem + 3vw, 4rem)">x</p>').status == 'PASS')
    check('clamp не найден → SKIP', eval_clamp('<p>x</p>').status == 'SKIP')
    # калибровка опыта K/03 — ложные B из прогона на 8 страницах
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
    # контраст по классам узлов (профиль I 08/03 §8; опыт K/03) и H1 в LCP (creative E/01)
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
    selftest_sources(check, budgets, gates, prof, f2)
    for st, name in checks:
        print(st, name)
    print(f"итог: {sum(c[0] == 'PASS' for c in checks)}/{len(checks)} PASS")
    return 0 if ok else 1


def selftest_sources(check, budgets, gates, prof, clean):
    """Самопроверка сводки соседей, правила лидогенерации из данных, лимитов строк и условий замера."""
    global AMBITION
    levels = load_levels()
    # таблица умолчаний и правило лидогенерации — из ambition-levels.yaml; в budgets.yaml — ссылка на таблицу, без копии
    ptl = budgets.get('page_type_levels') or {}
    rfile, _, rkey = str(ptl.get('ref') or '').partition('#')
    check('budgets.yaml page_type_levels.ref ведёт в ambition-levels.yaml#defaults_by_page_type, копии таблицы нет',
          os.path.normpath(os.path.join(DIR07, rfile)) == os.path.normpath(AMBITION) and rkey in (levels or {})
          and 'default' not in ptl and any(level_defaults(levels)))
    rule = lead_rule(levels)
    check('правило лидогенерации — поля ambition-levels.yaml (доля, полосы цены, otherwise, no_data)',
          all(k in rule for k in ('page_type', 'hot_mobile_share_min', 'price_bands', 'otherwise', 'no_data')))
    share = rule.get('hot_mobile_share_min')
    check('доля = порогу и полоса из данных → L0', resolve_profile('landing-lead-services', budgets, None, share, rule['price_bands'][0], levels)['level'] == 'L0')
    check('полоса вне списка → otherwise', resolve_profile('landing-lead-services', budgets, None, 0.9, 'premium', levels)['level'] == rule['otherwise'])
    check('данных о трафике нет → no_data', resolve_profile('landing-lead-services', budgets, None, None, None, levels)['level'] == rule['no_data'])
    lv2 = copy.deepcopy(levels)
    lead_rule(lv2)['hot_mobile_share_min'] = 0.99
    check('порог доли читается из данных, а не из кода (0,99 → 0,7 не проходит)',
          resolve_profile('landing-lead-services', budgets, None, 0.7, 'mid', lv2)['level'] == rule['otherwise'])
    pr = [pt for pt, (lv, part) in level_defaults(levels).items() if part == 'proposed']
    check('тип раздела proposed разрешается с пометкой', bool(pr) and any('proposed' in x for x in resolve_profile(pr[0], budgets, levels=levels)['log']))
    keep, AMBITION = AMBITION, os.path.join(DIR07, 'нет-такого-файла.yaml')
    try:
        p0 = resolve_profile('landing-lead-services@L1', budgets)
        check('без таблицы creative рядом: профиль с уровнем разрешается (соседний чекаут с одной базой site)',
              p0['level'] == 'L1' and any('не сверен' in x for x in p0['log']))
        try:
            resolve_profile('service-page', budgets)
            check('без таблицы creative: профиль без уровня — ошибка', False)
        except ValueError:
            check('без таблицы creative: профиль без уровня — ошибка', True)
    finally:
        AMBITION = keep
    # лимиты строк и условия замера
    for gid, key in (('SG-PERF-06', 'opacity_near_zero'), ('SG-PERF-16', 'poster_bpp_min'), ('SG-PERF-16', 'poster_area_min'),
                     ('SG-GEO-01', 'nojs_ratio_s'), ('SG-GEO-01', 'nojs_ratio_d'), ('SG-MOB-01', 'overflow_px'),
                     ('SG-NAV-02', 'crumbs_vs_markup_pct'), ('SG-A11Y-08', 'clamp_ratio_max')):
        try:
            gate_limit(gid, key)
            check(f'{gid}: limits.{key} есть', True)
        except KeyError:
            check(f'{gid}: limits.{key} есть', False)
    c = conditions(budgets)
    check('условия замера: окно первого экрана 5 с, телефон — дескриптор и CPU, сеть кбит/с → байт/с',
          window_ms(budgets) == 5000 and c['mobile']['descriptor'] == 'Pixel 7' and c['mobile']['cpu_slowdown'] == 4
          and cdp_network(c)['downloadThroughput'] == c['mobile']['down_kbps'] * 125 and c['desktop']['width'] == 1440)
    check('тишина: тяжёлый замок, затем браузер, затем домены; удержанное обёрткой не берётся',
          lock_plan(('ai-media',), holds='', budgets=budgets) == [(c['lock'], None), ('browser', None), ('browser', 'ai-media')]
          and lock_plan((), holds=f"{c['lock']},browser", budgets=budgets) == [])
    js = pause_label_re_js()
    rx = re.compile(js[1:-2], re.I)
    check('подписи паузы: одно выражение JS из PAUSE_LABELS — «Вращение», «Пауза», «Stop animation» да, «Купить» нет',
          js.startswith('/(') and js.endswith(')/i') and all(rx.search(x) for x in ('Вращение', 'Пауза', 'Stop animation'))
          and not rx.search('Купить'))
    # page_accept (контракт accept_<режим>.json)
    base_np = {'lcp': {'t': 900, 'tag': 'IMG', 'lazy': False, 'fp': 'high', 'size': 90000}, 'cls': 0.01, 'console': [],
               'first_screen_total_kb': 900.0, 'weight_measured': True, 'dom': {'imgs': [{'src': 'a/hero.avif', 'wh': True, 'above': True}]},
               'media_first': [], 'motion_6s': {'moving': False, 'pause_control': False, 'pct': 0.0, 'videos_playing': 0},
               'loops': {'scope': 'page', 'without_pause': []}}
    acc = {('mobile', True): {'device': 'mobile', 'throttle': True, 'mode': 'mobile_thr', 'no_preference': copy.deepcopy(base_np),
                              'reduce': {'media_kb': 0, 'motion': {'fail': []}}}}
    r0 = {r.id: r for r in evaluate(prof, clean, accept=acc)}
    check('page_accept: LCP телефона — из прогона --throttle, чисто → PASS', r0['SG-PERF-01'].status == 'PASS' and r0['SG-PERF-01'].source == 'page_accept')
    a1 = copy.deepcopy(acc)
    np1 = a1[('mobile', True)]['no_preference']
    np1['lcp'].update({'t': 3000, 'lazy': True})
    np1['dom']['imgs'].append({'src': 'a/card.png', 'wh': False, 'above': True})
    np1['media_first'] = [{'kind': 'video', 'sel': 'video.hero', 'src': 'hero.mp4', 'poster': True, 'poster_bpp': 0.02, 'cover_share': 1.0},
                          {'kind': 'canvas', 'sel': 'canvas.stage', 'cover_share': 0.98}]
    np1['motion_6s'] = {'moving': True, 'pause_control': False, 'pct': 2.1, 'videos_playing': 1}
    np1['loops'] = {'scope': 'first_screen', 'without_pause': []}
    a1[('mobile', True)]['reduce'] = {'media_kb': 120.0, 'motion': {'fail': ['пауза 3: 0,9 %/с > 0,3']}}
    r1 = {r.id: r for r in evaluate(prof, clean, accept=a1)}
    check('LCP 3 000 мс > цели 2 500 телефона → S', r1['SG-PERF-01'].severity == 'S')
    check('LCP-картинка с lazy → B (SG-PERF-06)', r1['SG-PERF-06'].severity == 'B')
    check('картинка первого экрана без размеров → S (SG-PERF-14)', r1['SG-PERF-14'].severity == 'S')
    check('постер 0,02 бит/пикс и постер холста 0,98 площади → S (SG-PERF-16: энтропия и площадь)',
          r1['SG-PERF-16'].severity == 'S' and 'бит/пикс' in str(r1['SG-PERF-16'].value) and 'площади' in str(r1['SG-PERF-16'].value))
    check('движение на 6-й секунде без паузы → B (SG-A11Y-03), пометка «только первый экран»',
          r1['SG-A11Y-03'].severity == 'B' and 'только первый экран' in r1['SG-A11Y-03'].note)
    check('reduce: видео 120 КБ и движение паузы → S (SG-A11Y-07)', r1['SG-A11Y-07'].severity == 'S')
    a2 = copy.deepcopy(acc)
    a2[('mobile', True)]['no_preference']['lcp'].update({'tag': 'VIDEO', 'fp': ''})
    a2[('mobile', True)]['no_preference']['media_first'] = [{'kind': 'video', 'sel': 'video.hero', 'poster': False}]
    r2 = {r.id: r for r in evaluate(prof, clean, accept=a2)}
    check('LCP — VIDEO и видео без poster → S (SG-PERF-16)', r2['SG-PERF-16'].severity == 'S' and 'VIDEO' in str(r2['SG-PERF-16'].value))
    a3 = copy.deepcopy(acc)
    a3[('mobile', True)]['no_preference']['lcp']['fp'] = ''
    check('LCP-картинка без fetchpriority=high → S', {r.id: r for r in evaluate(prof, clean, accept=a3)}['SG-PERF-06'].severity == 'S')
    a4 = {('desktop', False): {'device': 'desktop', 'throttle': False, 'mode': '1440x900', 'no_preference': copy.deepcopy(base_np)}}
    a4[('desktop', False)]['no_preference']['first_screen_total_kb'] = 4000.0
    r4 = [r for r in evaluate(prof, {}, accept=a4) if r.id == 'SG-WEIGHT-01' and r.device == 'desktop']
    check('без анатомии вес — прогон page_accept без замедления: 4 000 > 2 500 → S', r4 and r4[0].severity == 'S' and r4[0].source == 'page_accept')
    a4[('desktop', False)]['no_preference']['weight_measured'] = False
    r4 = [r for r in evaluate(prof, {}, accept=a4) if r.id == 'SG-WEIGHT-01' and r.device == 'desktop']
    check('вес из прогона с замедлением сети не сравнивается → SKIP', r4 and r4[0].status == 'SKIP')
    lk = {('mobile', True), ('mobile', False)}
    check('load_accept: устройство и троттлинг — поля отчёта или имя режима', lk == set(_selftest_accept_dir(load_accept)))
    # motion_check (results.json + gates.json)
    mot = {'results': {'desk': {'vitals': {'lcp_ms': 3100, 'tbt_ms': 90}, 'cls': {'window_max': 0.02}, 'net': {'first_kb': 1200.0, 'session_kb': 2000.0, 'font_kb': 90.0},
                                'derived': {'moving_6s_without_pause': False, 'loops_without_pause': ['div.marquee'], 'flash_fail': True, 'flash_area_frac': 0.4}},
                       'mob': {'vitals': {'lcp_ms': 1200}, 'derived': {'moving_6s_without_pause': False, 'loops_without_pause': [], 'flash_fail': False}}},
           'gates': {'level': 'L1', 'rows': [{'id': 'EG-A11Y-06', 'mode': 'rm', 'verdict': 'FAIL', 'severity': 'S', 'found': 0.8, 'threshold': '<= 0.3'},
                                             {'id': 'EG-A11Y-04', 'mode': 'desk', 'verdict': 'FAIL', 'severity': 'B'},
                                             {'id': 'EG-PERF-06', 'mode': 'desk', 'verdict': 'FAIL', 'severity': 'D'}]}, 'level': 'L1'}
    rm_ = evaluate(prof, clean, motion=mot)
    byd = {(r.id, r.device, r.mirror): r for r in rm_}
    check('motion_check: петля без паузы → B (SG-A11Y-03, вся страница)', byd[('SG-A11Y-03', 'desktop', False)].severity == 'B'
          and not byd[('SG-A11Y-03', 'desktop', False)].note)
    check('motion_check: вспышки → B (SG-A11Y-04); телефон без вспышек → PASS', byd[('SG-A11Y-04', 'desktop', False)].severity == 'B'
          and byd[('SG-A11Y-04', 'mobile', False)].status == 'PASS')
    check('motion_check: reduce EG-A11Y-06 → S (SG-A11Y-07)', byd[('SG-A11Y-07', 'page', False)].severity == 'S')
    mir = byd[('SG-PERF-02', 'desktop', True)]
    check('зеркало: LCP десктопа motion_check 3 100 > 2 500 → D, на вердикт не влияет', mir.severity == 'D' and mir.status == 'FAIL'
          and verdict([mir])[0] == 'accepted')
    lay = layers(mot, None)
    check('слой эффектов: B 1, S 1, D 1', (lay['effects']['B'], lay['effects']['S'], lay['effects']['D']) == (1, 1, 1))
    # gate_check (ворота 3D)
    g3 = [{'mode': 'desktop', 'reduced': False, 'probe': 'probe_quick.json', 'summary': {'B': 1, 'S': 0, 'D': 1},
           'rows': [{'id': 'WEB-04', 'check': '3D-ассеты, КБ', 'value': 1700, 'limit': 1536, 'severity': 'B', 'status': 'FAIL'},
                    {'id': 'WEB-07', 'check': 'ошибки консоли', 'value': 2, 'limit': 0, 'severity': 'B', 'status': 'FAIL'},
                    {'id': 'WEB-01', 'check': 'LCP страницы, мс', 'value': 3000, 'severity': 'D', 'status': 'FAIL', 'mirror': 'SG-PERF-02'}]}]
    r3 = evaluate(prof, clean, gate3d=g3)
    by3 = {(r.id, r.mirror): r for r in r3}
    check('ворота 3D: доля 3D провалена → SG-WEIGHT-08 D; страница не блокируется', by3[('SG-WEIGHT-08', False)].severity == 'D'
          and verdict([by3[('SG-WEIGHT-08', False)]])[0] == 'accepted')
    check('зонд 3D: 2 ошибки консоли → SG-CONTENT-04 S', by3[('SG-CONTENT-04', False)].severity == 'S')
    check('зонд 3D: LCP страницы — зеркало D строки SG-PERF-02', by3[('SG-PERF-02', True)].severity == 'D')
    # показ H1 во времени (page_anatomy h1_paint) — признак без HTML
    f12 = copy.deepcopy(clean)
    f12['mobile']['dom'] = {'headings': {'h1_first_screen': True, 'h1': ['A Good Clean, Naturally']}}
    f12['mobile']['fin'] = {'lcp': [{'tag': 'P', 'text': 'Sparkling clean homes are our specialty', 'size': 52966, 'url': ''}]}
    f12['mobile']['h1_paint'] = {'first_op': 0.0, 't_visible': 820, 'in_first_screen': True}
    check('H1 не кандидат LCP, в HTML признаков нет, показ H1: первый кадр невидим → S',
          {r.id: r for r in evaluate(prof, f12, html_text='<h1>A Good Clean, Naturally</h1>')}['SG-PERF-06'].severity == 'S')
    f12['mobile']['fin'] = {'lcp': [{'tag': 'H1', 'text': 'A Good Clean, Naturally', 'size': 90000, 'url': ''}]}
    f12['mobile']['h1_paint'] = {'first_op': 0.001, 't_visible': 700, 'in_first_screen': True}
    check('H1 — LCP, показ H1: первый кадр opacity 0,001 → D', {r.id: r for r in evaluate(prof, f12)}['SG-PERF-06'].severity == 'D')


def _selftest_accept_dir(loader):
    """Два отчёта page_accept во временной папке: новый (поля device, throttle) и по имени режима."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, 'accept_mobile_thr.json'), 'w', encoding='utf-8') as f:
            json.dump({'device': 'mobile', 'throttle': True, 'no_preference': {}}, f)
        with open(os.path.join(td, 'accept_mobile.json'), 'w', encoding='utf-8') as f:
            json.dump({'mode': 'mobile', 'no_preference': {}}, f)
        with open(os.path.join(td, 'accept_1440x900_click.json'), 'w', encoding='utf-8') as f:
            json.dump({'mode': '1440x900_click', 'no_preference': {}}, f)
        return loader(td)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--profile', help='профиль бюджета <page_type>@L<n> (page-plan page.budget_profile)')
    ap.add_argument('--resolve', help='показать профиль (JSON: id, level, page_type, outcome, weight, all_levels, log)')
    ap.add_argument('--conditions', action='store_true', help='условия замера budgets.yaml (JSON)')
    ap.add_argument('--anatomy', help='папка anatomy_<устройство>.json page_anatomy.py')
    ap.add_argument('--accept', help='папка accept_<режим>.json page_accept.py')
    ap.add_argument('--motion', help='папка --out motion_check.py (results.json, gates.json)')
    ap.add_argument('--gate3d', nargs='*', help='JSON gate_check.py --json (файл на прогон зонда 3D)')
    ap.add_argument('--geo', help='JSON geo_probe.py (файл или папка с одним JSON)')
    ap.add_argument('--ia', help='ia.json ia_probe.py (строки scope: site)')
    ap.add_argument('--axe', help='JSON axe (run_axe_targets.py — адреса узлов — или результат axe.run)')
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
    budgets = load_budgets()
    if a.conditions:
        print(json.dumps(conditions(budgets), ensure_ascii=False, indent=1))
        return 0
    try:
        if a.resolve:
            p = resolve_profile(a.resolve, budgets, a.site_level, a.hot_mobile_share, a.price_band)
            print(json.dumps(p, ensure_ascii=False, indent=1))
            return 0
        if not a.profile or not (a.anatomy or a.accept or a.motion or a.gate3d or a.geo or a.ia or a.axe or a.html or a.css):
            ap.print_help()
            return 2
        prof = resolve_profile(a.profile, budgets, a.site_level, a.hot_mobile_share, a.price_band)
    except ValueError as e:
        print(f'page_gates.py: {e}', file=sys.stderr)
        return 2
    use_gates(a.gates)
    plan = load_yaml(a.plan) if a.plan else None
    raw = open(a.html, encoding='utf-8', errors='replace').read() if a.html else None
    css = '\n'.join(open(f, encoding='utf-8', errors='replace').read() for f in (a.css or []))
    motion, gate3d = load_motion(a.motion), load_gate3d(a.gate3d)
    res = evaluate(prof, load_anatomy(a.anatomy) if a.anatomy else {}, load_accept(a.accept) if a.accept else {}, a.jurisdiction,
                   geo=load_json(a.geo), ia=load_json(a.ia), axe=load_json(a.axe), plan=plan, html_text=raw,
                   headkit=load_headkit(os.path.join(DIR07, 'head-kit.yaml')), ai_bots_policy=a.ai_bots_policy,
                   ads_google=a.ads_google, css_text=css or None, motion=motion, gate3d=gate3d)
    meta = gate_meta(a.gates or GATES)
    lay = layers(motion, gate3d)
    if a.json:
        v, nb, ns = verdict(res)
        rows = []
        for r in res:
            d = dict(r.__dict__)
            d.update(meta.get(r.id, {}))
            rows.append(d)
        src = {k: bool(x) for k, x in (('anatomy', a.anatomy), ('accept', a.accept), ('motion', motion), ('gate3d', gate3d),
                                       ('geo', a.geo), ('ia', a.ia), ('axe', a.axe), ('plan', a.plan), ('html', a.html))}
        print(json.dumps({'profile': prof['id'], 'level': prof['level'], 'log': prof['log'], 'verdict': v, 'B': nb, 'S': ns,
                          'gates': rows, 'layers': lay, 'sources': src}, ensure_ascii=False, indent=1, default=str))
    else:
        print_table(prof, res, lay)
    return 1 if verdict(res)[0] == 'blocked' else 0


if __name__ == '__main__':
    sys.exit(main())
