#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Визуальный QA экрана или страницы: измерение computed styles, сверка с токенами ДС и порогами базы ui, отчёт.

Проверки собраны из базы ui: пороги приёмки формы и глубины (`04-shape-elevation/03-tools-checks-and-ai-errors.md`
§2, §6, §8), раскладки (`05-layout-grid/06-ai-errors-and-checks.md` §3), типографики
(`02-typography/06-localization-and-ai-errors.md` §5), состояний (`06-components-visual/07-states-matrix.md` §12), нормы
практики (`10-design-systems-atlas/04-live-products-measured.md` §8), токены (`09-design-tokens/05-anti-patterns-and-pipeline.md`
§3). Расчёты цвета — `scripts/lib/color.py` (WCAG 2, APCA, OKLCH, ΔE, композитинг альфы).

Использование:
    python3 ui_audit.py ПУТЬ_ИЛИ_URL [ключи]
    python3 ui_audit.py экран.html --tokens docs/projects/<slug>/design/system.tokens.json --scheme both --hover --tab 20
    python3 ui_audit.py экран.html --acceptance --touch      # все ширины приёмки, вылет на 320 и тач-прогон
    python3 ui_audit.py --batch список.txt --preset admin
    python3 ui_audit.py страница.html --surface page        # страница сайта: пороги профиля marketing
    python3 ui_audit.py --slop-params [--tokens ФАЙЛ]       # параметры скрипта маркеров ui 11/04 §3 (JSON)
    python3 ui_audit.py --selftest                          # парсеры, пороги и проверки на синтетике, без браузера
    python3 ui_audit.py --selftest --browser                # и код страницы в Chromium: строки абзацев (H8)

Ключи:
    --preset admin|consumer|marketing
                              пресет порогов: admin — A (плотная админка), consumer — B (кабинет клиента) — ui 14/11;
                              marketing — профиль страницы сайта (`scripts/ui/data/marketing-profile.yaml`). Без ключа:
                              у страницы сайта — marketing, у экрана приложения — admin
    --surface page|app        поверхность цели: страница сайта или экран приложения. Без ключа у статичной копии
                              артборда её называет манифест входа холста (`route` в `design/<surface>/input/INPUT.md`),
                              у другой цели — экран приложения
    --tokens ФАЙЛ             токены ДС проекта: DTCG `system.tokens.json` или CSS `system.tokens.css`. Шкалы
                              отступов (`space.*`), кеглей, радиусов, высот, слоёв, длительностей и набор цветов берутся
                              из них. Без ключа у admin — эталонные токены ui (`kb/ui/14-recipes/examples/tokens.css`),
                              у consumer и marketing — шкалы пресета; источник шкал записан в отчёте. Отступ со шкалы токенов
                              прогона — не находка A2 («кратные 5 и не кратные 4»)
    --viewport WxH            окно прогона (повторять ключ для нескольких); по умолчанию — первая ширина приёмки
    --acceptance              все ширины приёмки из `kb/common/acceptance-widths.yaml` и прогон вылета на `overflow_only`
    --scheme light|dark|both  цветовая схема (по умолчанию light)
    --reduced-motion          дополнительный прогон с `prefers-reduced-motion: reduce`
    --hover                   прогон hover по выборке интерактивных элементов (до 12 штук)
    --tab N                   пройти Tab N раз и проверить индикатор фокуса (по умолчанию 0, рекомендуется 20)
    --touch                   прогон с эмуляцией тача (`pointer: coarse`) на самой широкой ширине приёмки уже первого
                              брейкпоинта ДС: F3 — зона нажатия каждой цели ≥ 44×44
    --out КАТАЛОГ             куда писать отчёт (по умолчанию $DDD_HOME/out/ui/audit)
    --name ИМЯ                имя файлов отчёта вместо автогенерации
    --strict-border           требовать контраст границы контрола >= 3:1 (WCAG 1.4.11) вместо режима практики
    --max-elements N          предел числа разбираемых узлов (по умолчанию 4000)
    --wait N                  ожидание после загрузки, мс (по умолчанию 400 для файлов, 2000 для URL)
    --fail-on blocker|serious|any   код возврата 1, если есть нарушения такого уровня
    --quiet                   не печатать таблицу в stdout
    --json                    JSON отчёта в stdout вместо таблицы, одна цель (без --batch); его читает код-репо: пункты
                              D5 и V1 критериев приёмки после сборки, `kb/common/acceptance-criteria.yaml`

Проверки — 14 групп: A отступы, B размеры, C форма, D глубина, E слои, F цели, G фокус, H типографика, I цвет,
J раскладка, K движение, L приметы вида, M сокращённое движение, S состояния. Визуально скрытое (clip, 1×1, вне предка с
`overflow: hidden`) в проверки текста и целей не входит. Потолок длительностей (K2) — из пресета; соседние карточки
ряда выровнены (J9). Находка несёт id приметы реестра `kb/common/tells.yaml` (раздел `checks`, ключ
`ui_audit:<id проверки>`), отчёт сводит приметы без повторов.

Длина строки абзаца (H8) — знаков в самой длинной строке, как строки разложил браузер. У каждого `p`, `li`, `dd` и
`blockquote` страница читает прямоугольник каждого знака: знак — графема (эмодзи, флаг, буква с комбинирующим знаком —
один знак), нарисованная с ненулевой шириной (схлопнутый пробел — нет); знак продолжает строку, когда по вертикали
перекрывает предыдущий знак не меньше чем на половину высоты меньшего из двух (инлайн-код, сдвинутые слова и буквица
строку не рвут); висящий пробел у переноса не считается; текст вложенного абзаца, пункта или цитаты — их строки,
визуально скрытый текст не считается. H8 судит абзацы длиннее 120 знаков; порог — `measure_chars`
пресета, в окне уже первого брейкпоинта — `measure_chars_narrow`. Данные без строк (синтетика вызывающей утилиты) —
ширина абзаца против `para_max_width`.

Профиль страницы сайта — `marketing` (`scripts/ui/data/marketing-profile.yaml`): пресет страницы (шкалы отступов,
радиусов, высот, кеглей, слоёв и длительностей `preset.*` — их читают проверки, когда токены ДС не переданы) и таблица
действий по проверкам. Прогон с пресетом marketing применяет профиль сам: перенастройка, серьёзность, «информативно»;
проверки с пересчётом по узлам страницы (кроме D3, D4, L4) получают серьёзность профиля, а сам пересчёт делает
`scripts/creative/marketing_audit.py` (load_profile и apply_profile). Числа D3 — лимиты `glass-panel` каталога
эффектов creative. Общие пороги нескольких утилит — `scripts/ui/data/thresholds.yaml`.

Что на выходе:
    <out>/<name>.md    таблица «правило | найдено | порог | вердикт | серьёзность» + примеры узлов + приметы
    <out>/<name>.json  те же данные машиночитаемо (для цикла «прогнал -> вернул модели -> правки»): tool, skill_version
                       (файл VERSION скилла), target, preset, tokens, runs, findings[] {id, verdict, severity, run, …},
                       tells; с --json — тот же JSON в stdout

Ограничения (важно для чтения результата):
  * computed styles — это применение токенов на конкретном экране, а не сами токены;
  * скрипт не видит смысл: `bg-subtle` вместо `bg-component` он пропустит (это ловится только ревью);
  * иерархия, осмысленность метрик, «ложное дно» и вкус не проверяются в принципе;
  * кросс-доменные iframe и canvas не разбираются;
  * контраст текста на градиенте и на полупрозрачной подложке считается по цвету ближайшего непрозрачного предка —
    значение недостоверно, вердикт WARN (I1b); текст над картинкой, видео или canvas — WARN «проверить F83» (I1m):
    контраст по буквам считает `scripts/ai-media/page_accept.py --contrast`.

Замок браузера утилита берёт сама на время работы браузера: kbpaths.lock("browser"), реентерабельный по дереву процессов —
утилита, запущенная из утилиты с тем же замком, его не ждёт.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "lib"))
import kbpaths  # noqa: E402
ROOT = str(kbpaths.kb("ui"))
DEFAULT_OUT = str(kbpaths.out("ui", "audit", create=False))
THRESHOLDS = kbpaths.data("ui", "thresholds.yaml")
REFERENCE_TOKENS = kbpaths.kb("ui", "14-recipes", "examples", "tokens.css")
WIDTHS_FILE = kbpaths.kb(None, "common", "acceptance-widths.yaml")
TELLS_FILE = kbpaths.kb(None, "common", "tells.yaml")
EFFECTS_FILE = kbpaths.kb("creative", "06-effects-catalog", "effects.yaml")
TELL_KEY = "ui_audit:"          # ключ проверки в tells.yaml#checks: ui_audit:<id проверки>

import yaml  # noqa: E402
from color import hex2oklch, wcag, apca, composite, dE_oklab  # noqa: E402


def load_thresholds(path=THRESHOLDS):
    """Общие пороги проверок (`scripts/ui/data/thresholds.yaml`)."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


TH = load_thresholds()

# =====================================================================================
# 1. Пресеты: разрешённые значения и пороги
# =====================================================================================

PRESET_ADMIN = {
    "name": "admin",
    "title": "плотная админка (база 14 px, контрол 32)",
    "ds_preset": "A",                 # пресет ui/14-recipes/11-presets.md
    "reference_tokens": True,         # эталонные токены ui — токены этого пресета
    # шкалы значений
    "spacing": [0, 2, 4, 6, 8, 12, 16, 24, 32, 40, 48, 64, 96],
    "radius": [0, 2, 4, 6, 8, 9999],
    "heights": [24, 28, 32, 36, 40, 48],
    "font_sizes": [11, 12, 14, 16, 20, 24, 28, 32],
    "font_weights": [400, 500, 600, 700],
    "icon_sizes": [12, 14, 16, 20, 24],
    "zindex": [0, 10, 100, 200, 1000, 1100, 1200, 1300, 1400, 1500],
    "durations": [0, 50, 100, 150, 200, 300, 400, 600],
    "border_widths": [0, 1, 2],
    # пороги
    "spacing_in_scale_min": 0.95,
    "unique_gap_max": 6,
    "fraction_values_max": 0.03,
    "unique_spacing_max": 15,
    "unique_heights_max": 3,
    "unique_radius_max": 6,
    "unique_shadow_max": 7,
    "shadow_share_max": 0.15,
    "glass_max": 2,
    "unique_font_sizes_max": TH["font_sizes"]["norm"][1],
    "unique_font_weights_max": 4,
    "unique_text_colors_max": 9,   # практика: медиана 7.5, потолок 8; полный ролевой набор схемы — 9
    "unique_bg_colors_max": 10,
    "unique_border_colors_max": 5,
    "para_max_width": 720,
    "form_max_width": 640,
    "sidebar_max": 300,
    "sidebar_min": 200,
    "content_min": 640,
    "sticky_sum_max": 192,
    "page_header_max": 120,
    "body_leading": (1.28, 1.55),
    # длина строки абзаца в знаках: 45–75, в узкой колонке и на телефоне 40–60, не больше 80
    # (ux/03-layout-placement/02-grid-spacing-density.md §4); узкое окно — уже первого брейкпоинта ДС
    "measure_chars": (45, 75),
    "measure_chars_narrow": (40, 60),
    "measure_chars_max": 80,
    "target_min": 24,
    "target_min_touch": 44,           # на таче каждая цель ≥ 44×44 зоной нажатия (ux/08-accessibility/01-… §12.4)
    "target_gap_min": 4,
    "focus_width_min": 2,
    "duration_300_share_max": 0.20,
    # потолок длительностей пресета; исключение — подложка (скрим) у A, онбординг у B
    # (ui/14-recipes/11-presets.md, «Потолок движения»; ui/09-design-tokens/04-reference-token-schema.md §2.10)
    "duration_max": 200,
    "duration_max_exception": 250,
    "dark_bg_L": (0.13, 0.22),        # коридор светлоты фона тёмной темы OKLCH (I8, I10)
    "neutral_C_max": 0.05,            # хрома нейтрали (I7, I10)
    "text_contrast_min": 4.5,
    "large_text_contrast_min": 3.0,
    "border_contrast_min": 3.0,       # при --strict-border
    "border_contrast_practice": 1.20,  # медиана практики 1.30, ниже 1.2 граница не видна совсем
    "nesting_shadow_max": 1,
    "hover_delta_L": (0.02, 0.08),
}

PRESET_CONSUMER = dict(PRESET_ADMIN)
PRESET_CONSUMER.update({
    "name": "consumer",
    "title": "клиентский сервис (база 16 px, контрол 40)",
    "ds_preset": "B",
    "reference_tokens": False,        # эталонных токенов пресета B нет: шкалы — из пресета или токенов ДС
    "duration_max": 400,
    "duration_max_exception": 600,
    "radius": [0, 6, 10, 14, 20, 9999],
    "heights": [24, 32, 36, 40, 44, 48],
    "font_sizes": [12, 14, 16, 18, 20, 24, 32, 40],
    "icon_sizes": [16, 20, 24],
    "unique_font_sizes_max": 8,
    "unique_shadow_max": 7,
    "shadow_share_max": 0.25,
    "sidebar_max": 300,
    "form_max_width": 640,
    "body_leading": (1.4, 1.65),
})

PRESETS = {"admin": PRESET_ADMIN, "consumer": PRESET_CONSUMER}

SEV_BLOCKER, SEV_SERIOUS, SEV_POLISH = "блокер", "серьёзно", "полировка"
SEV_ORDER = {SEV_BLOCKER: 0, SEV_SERIOUS: 1, SEV_POLISH: 2}

# Эмодзи — пиктограммы из блоков эмодзи, с необязательным селектором вида U+FE0F. Сам селектор не считается: иначе
# «©️» и «↔️» — обычные знаки текста — попали бы в счёт (claude-design/06-design-process/05-default-look.md §7).
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF⬀-⯿]️?"
)
TITLE_CASE_RU_RE = re.compile(r"\b[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+")
EN_NUMBER_RE = re.compile(r"\d,\d{3}\b")
PERCENT_GLUED_RE = re.compile(r"\d%")


# =====================================================================================
# 2. Чтение набора токенов DTCG (необязательно)
# =====================================================================================

def load_dtcg(path):
    """Достать из DTCG-файла множества разрешённых значений: отступы, радиусы, высоты, кегли, цвета, z, длительности.

    Шкала отступов — только токены `space.*` с их режимами плотности: шкала одна
    (ui/09-design-tokens/04-reference-token-schema.md §1.3); размерный ряд `primitive.size.*` отступом не считается."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    flat = {}

    def walk(node, prefix):
        if not isinstance(node, dict):
            return
        if "$value" in node:
            flat[".".join(prefix)] = node
            return
        for k, v in node.items():
            if k.startswith("$"):
                continue
            walk(v, prefix + [k])

    walk(data, [])

    def resolve(val, depth=0):
        if depth > 8:
            return val
        if isinstance(val, str) and val.startswith("{") and val.endswith("}"):
            ref = val[1:-1]
            tgt = flat.get(ref)
            return resolve(tgt["$value"], depth + 1) if tgt else val
        return val

    out = {"spacing": set(), "radius": set(), "sizes": set(), "font_sizes": set(),
           "colors": set(), "zindex": set(), "durations": set(), "font_weights": set(), "breakpoints": set()}
    for path_name, node in flat.items():
        v = resolve(node.get("$value"))
        t = node.get("$type")
        if t is None:
            # тип наследуется от группы: восстановим по имени ветки
            head = path_name.split(".")[0]
            t = {"space": "dimension", "size": "dimension", "radius": "dimension",
                 "color": "color", "z": "number", "motion": "duration"}.get(head)
        if isinstance(v, dict) and "value" in v and "unit" in v:
            px = float(v["value"]) * (16.0 if v["unit"] == "rem" else 1.0)
            if path_name.startswith("space"):
                out["spacing"].add(round(px, 2))
            if path_name.startswith("radius"):
                out["radius"].add(round(px, 2))
            if path_name.startswith("size"):
                out["sizes"].add(round(px, 2))
            if "font.size" in path_name or path_name.startswith("primitive.font.size"):
                out["font_sizes"].add(round(px, 2))
            if v["unit"] in ("ms", "s"):
                out["durations"].add(round(px, 2))
        if isinstance(v, dict) and "unit" in v and v["unit"] in ("ms", "s"):
            out["durations"].add(float(v["value"]) * (1000 if v["unit"] == "s" else 1))
        if isinstance(v, dict) and "hex" in v:
            out["colors"].add(v["hex"].lower())
        # переопределения режимов лежат внутри токена ($extensions.<ns>.modes.dark и т. п.)
        for ns, ext in (node.get("$extensions") or {}).items():
            if not isinstance(ext, dict) or not ns.endswith("modes"):
                continue
            for mode, mv in ext.items():
                mv = resolve(mv)
                if isinstance(mv, dict) and "hex" in mv:
                    out["colors"].add(mv["hex"].lower())
                elif isinstance(mv, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", mv):
                    out["colors"].add(mv.lower())
                elif isinstance(mv, dict) and "value" in mv and "unit" in mv:
                    pxm = float(mv["value"]) * (16.0 if mv["unit"] == "rem" else 1.0)
                    if path_name.startswith("space"):
                        out["spacing"].add(round(pxm, 2))
                    elif path_name.startswith("size"):
                        out["sizes"].add(round(pxm, 2))
        if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v):
            out["colors"].add(v.lower())
        if t == "number" and isinstance(v, (int, float)) and path_name.startswith("z"):
            out["zindex"].add(int(v))
        if "font.weight" in path_name and isinstance(v, (int, float)):
            out["font_weights"].add(int(v))
        if path_name.startswith("breakpoint") and isinstance(v, dict) and "value" in v:
            out["breakpoints"].add(round(float(v["value"]) * (16.0 if v.get("unit") == "rem" else 1.0), 2))
    return {k: sorted(v) for k, v in out.items()}


CSS_VAR_RE = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;{}]+);")
TOKEN_SETS = ("spacing", "radius", "sizes", "font_sizes", "colors", "zindex", "durations", "font_weights", "breakpoints")


def _hex6(h):
    h = h.lstrip("#").lower()
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    return "#" + h[:6]


def load_css_tokens(path):
    """Те же множества, что load_dtcg, из CSS-переменных ДС (`system.tokens.css`, эталон
    `kb/ui/14-recipes/examples/tokens.css`). Имя переменной — путь токена через дефис; объявления всех блоков (темы,
    плотности, сокращённое движение) входят в множества, ссылки var() разрешаются по первому объявлению."""
    with open(path, encoding="utf-8") as f:
        text = re.sub(r"/\*.*?\*/", "", f.read(), flags=re.S)
    decls = CSS_VAR_RE.findall(text)
    first = {}
    for name, val in decls:
        first.setdefault(name, val.strip())

    def resolve(v, depth=0):
        if depth > 8:
            return v
        return re.sub(r"var\(--([A-Za-z0-9_-]+)(?:\s*,\s*([^()]*))?\)",
                      lambda m: resolve(first.get(m.group(1), m.group(2) or ""), depth + 1), v)

    out = {k: set() for k in TOKEN_SETS}
    for name, raw in decls:
        v = resolve(raw.strip())
        for hx in re.findall(r"#[0-9a-fA-F]{3,8}\b", v):
            if len(hx) in (4, 5, 7, 9):
                out["colors"].add(_hex6(hx))
        for m in re.finditer(r"rgba?\(([^)]*)\)", v):
            p = [x for x in re.split(r"[,\s/]+", m.group(1)) if x]
            try:
                out["colors"].add("#%02x%02x%02x" % tuple(int(round(float(x))) for x in p[:3]))
            except (ValueError, TypeError):
                pass
        for num, unit in re.findall(r"(-?\d+(?:\.\d+)?)(ms|s)\b", v):
            out["durations"].add(float(num) * (1000 if unit == "s" else 1))
        m = re.fullmatch(r"(-?\d+(?:\.\d+)?)(px|rem)", v)
        if m:
            px = round(float(m.group(1)) * (16.0 if m.group(2) == "rem" else 1.0), 2)
            if name.startswith("space-"):
                out["spacing"].add(px)
            if name.startswith(("radius-", "corner-")):
                out["radius"].add(px)
            if name.startswith("size-"):
                out["sizes"].add(px)
            if "font-size" in name or (name.startswith("type-") and name.endswith("-size")):
                out["font_sizes"].add(px)
            if name.startswith(("bp-", "breakpoint-")):
                out["breakpoints"].add(px)
        if re.fullmatch(r"-?\d+", v):
            if name.startswith("z-"):
                out["zindex"].add(int(v))
            if "font-weight" in name or (name.startswith("type-") and name.endswith("-weight")):
                out["font_weights"].add(int(v))
    return {k: sorted(v) for k, v in out.items()}


def load_tokens(path):
    """Токены ДС: DTCG (.json) или CSS-переменные (.css) → множества значений (TOKEN_SETS)."""
    ext = os.path.splitext(str(path))[1].lower()
    if ext == ".json":
        ts = load_dtcg(path)
    elif ext == ".css":
        ts = load_css_tokens(path)
    else:
        raise ValueError(f"{path}: токены — DTCG .json или CSS .css")
    return {k: ts.get(k, []) for k in TOKEN_SETS}


def tokens_to_preset(preset, ts):
    """Шкалы пресета из токенов ДС: отступы (`space.*`), радиусы, кегли, слои, длительности, высоты контролов
    (размеры 20–64 px). Пустое множество оставляет шкалу пресета."""
    p = dict(preset)
    if ts["spacing"]:
        p["spacing"] = sorted(set(ts["spacing"]) | {0})
    if ts["radius"]:
        p["radius"] = sorted(set(ts["radius"]))
    if ts["font_sizes"]:
        p["font_sizes"] = sorted(set(ts["font_sizes"]))
    if ts["zindex"]:
        p["zindex"] = sorted(set(ts["zindex"]) | {0})
    if ts["durations"]:
        p["durations"] = sorted(set(ts["durations"]) | {0})
    heights = [v for v in ts["sizes"] if 20 <= v <= 64]
    if heights:
        p["heights"] = sorted(set(heights))
    return p


def load_widths(path=WIDTHS_FILE):
    """Ширины приёмки (kb/common/acceptance-widths.yaml): набор от широкой к узкой и ширина проверки вылета."""
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return {"widths": [int(w) for w in d["widths"]], "overflow_only": d.get("overflow_only")}


# Высота окна — параметр прогона, а не норма приёмки: у широких окон 900, у окон уже первого брейкпоинта — 844.
VIEW_H_WIDE, VIEW_H_NARROW = 900, 844


_REF_TOKENS = None


def reference_tokens():
    """Эталонные токены ui (kb/ui/14-recipes/examples/tokens.css), разобранные один раз."""
    global _REF_TOKENS
    if _REF_TOKENS is None:
        _REF_TOKENS = load_css_tokens(REFERENCE_TOKENS)
    return _REF_TOKENS


def first_breakpoint(ts):
    """Первый брейкпоинт ДС; без брейкпоинтов в токенах — эталонный ui."""
    return min((ts or {}).get("breakpoints") or reference_tokens()["breakpoints"])


def load_tells(path=TELLS_FILE):
    """id приметы по id проверки: раздел `checks` реестра примет, ключи `ui_audit:<id>`. Нет ключа — нет приметы."""
    try:
        with open(path, encoding="utf-8") as f:
            d = yaml.safe_load(f) or {}
    except OSError:
        return {}
    out = {}
    for key, v in (d.get("checks") or {}).items():
        if isinstance(key, str) and key.startswith(TELL_KEY) and isinstance(v, dict) and v.get("tell"):
            out[key[len(TELL_KEY):]] = v["tell"]
    return out


TELL_OF = None


def tell_of(cid):
    global TELL_OF
    if TELL_OF is None:
        TELL_OF = load_tells()
    return TELL_OF.get(cid)


def load_glass_limits(effect="glass-panel", path=EFFECTS_FILE):
    """Лимиты стекла из каталога эффектов creative (`limits` записи)."""
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with open(path, encoding="utf-8") as f:
        d = yaml.load(f, Loader=loader)
    for e in d.get("effects") or []:
        if isinstance(e, dict) and e.get("id") == effect:
            return dict(e.get("limits") or {})
    raise KeyError(f"{effect}: записи нет в {path}")


# =====================================================================================
# 3. Сбор данных в странице
# =====================================================================================

COLLECT_JS = r"""
(opts) => {
  const MAXN = opts.maxElements;
  const toHex = (s) => {
    if (!s) return null;
    const m = s.match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number);
    if (p.length < 3 || p.some(isNaN)) return null;
    const a = p.length > 3 ? p[3] : 1;
    const hex = '#' + p.slice(0, 3).map(v => Math.round(v).toString(16).padStart(2, '0')).join('');
    return { hex, a };
  };
  const px = v => (v && v.endsWith && v.endsWith('px')) ? Math.round(parseFloat(v) * 100) / 100 : null;

  // эффективный фон: первый непрозрачный предок, с композитингом полупрозрачных слоёв поверх него
  const effBg = (el) => {
    const stack = [];
    let node = el, gradient = false;
    while (node && node.nodeType === 1) {
      const cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') gradient = true;
      const c = toHex(cs.backgroundColor);
      if (c && c.a > 0) {
        stack.push(c);
        if (c.a >= 0.999) break;
      }
      node = node.parentElement;
    }
    if (!stack.length) return { hex: '#ffffff', gradient, guessed: true };
    const composited = stack.length > 1 || stack[stack.length - 1].a < 0.999;
    let base = stack[stack.length - 1];
    let cur = base.hex;
    for (let i = stack.length - 2; i >= 0; i--) {
      const s = stack[i];
      const f = s.hex.slice(1).match(/../g).map(h => parseInt(h, 16));
      const b = cur.slice(1).match(/../g).map(h => parseInt(h, 16));
      cur = '#' + [0, 1, 2].map(k => Math.round(f[k] * s.a + b[k] * (1 - s.a)).toString(16).padStart(2, '0')).join('');
    }
    return { hex: cur, gradient, guessed: composited };
  };

  const shortSel = (el) => {
    const id = el.id ? '#' + el.id : '';
    const cls = (typeof el.className === 'string' && el.className)
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return (el.tagName.toLowerCase() + id + cls).slice(0, 60);
  };

  // визуально скрытое: clip нулевой площади или clip-path inset ≥ 50 %, бокс 1×1, бокс вне предка с обрезкой переполнения
  const clipHidden = (cs) => {
    const m = (cs.clip || '').match(/rect\(([^)]*)\)/);
    if (m) {
      const v = m[1].split(/[,\s]+/).filter(Boolean).map(parseFloat);
      if (v.length === 4 && !v.some(isNaN) && (v[1] - v[3]) * (v[2] - v[0]) <= 1) return true;
    }
    return /inset\(\s*(50|100)%/.test(cs.clipPath || '');
  };
  const outsideClip = (el, r) => {
    let p = el.parentElement;
    while (p && p !== document.body) {
      const s = getComputedStyle(p);
      if (s.overflowX !== 'visible' || s.overflowY !== 'visible') {
        const pr = p.getBoundingClientRect();
        if (r.right <= pr.left || r.left >= pr.right || r.bottom <= pr.top || r.top >= pr.bottom) return true;
      }
      p = p.parentElement;
    }
    return false;
  };
  // зона нажатия: бокс элемента и абсолютно позиционированные ::before и ::after, если элемент — их контейнер
  const hitArea = (el, cs, r) => {
    let w = r.width, h = r.height;
    if (cs.position === 'static') return { w, h };
    for (const pe of ['::before', '::after']) {
      const s = getComputedStyle(el, pe);
      if (!s || s.content === 'none' || s.content === 'normal' || s.position !== 'absolute') continue;
      const num = v => (v && v.endsWith('px')) ? parseFloat(v) : null;
      const t = num(s.top), b = num(s.bottom), l = num(s.left), rt = num(s.right), pw = num(s.width), ph = num(s.height);
      const ew = (l !== null && rt !== null) ? r.width - l - rt : (pw !== null ? pw : 0);
      const eh = (t !== null && b !== null) ? r.height - t - b : (ph !== null ? ph : 0);
      w = Math.max(w, ew); h = Math.max(h, eh);
    }
    return { w: Math.round(w * 100) / 100, h: Math.round(h * 100) / 100 };
  };

  // строки абзаца, как их разложил браузер (H8): знаков в каждой строке. Знак — графема (эмодзи, флаг, буква с
  // комбинирующим знаком — один знак), нарисованная с ненулевой шириной (схлопнутый пробел — нет). Знак продолжает
  // строку, когда его прямоугольник по вертикали перекрывает прямоугольник предыдущего знака не меньше чем на половину
  // высоты меньшего из двух: строку не рвут инлайн-код, сдвинутые слова и буквица, а следующая строка с предыдущей не
  // перекрывается. Висящий пробел у переноса не считается. Текст вложенного абзаца, пункта или цитаты — их строки;
  // визуально скрытый (clip, 1×1) не считается
  const LINE_TAGS = ['p', 'li', 'dd', 'blockquote'];
  const graphemes = new Intl.Segmenter(undefined, { granularity: 'grapheme' });
  const lineChars = (el) => {
    const lines = [], range = document.createRange(), hidden = new Map();
    let prev = null;
    const hiddenHost = (host) => {
      if (!hidden.has(host)) {
        let h = false;
        for (let e = host; e && e !== el && !h; e = e.parentElement) {
          const s = getComputedStyle(e), b = e.getBoundingClientRect();
          h = s.visibility !== 'visible' || clipHidden(s) || (b.width <= 1.5 && b.height <= 1.5);
        }
        hidden.set(host, h);
      }
      return hidden.get(host);
    };
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode, host = node.parentElement;
      if (!host || host.closest(LINE_TAGS.join(',')) !== el || hiddenHost(host)) continue;
      for (const { segment, index } of graphemes.segment(node.textContent)) {
        range.setStart(node, index);
        range.setEnd(node, index + segment.length);
        // знак сразу за переносом по дефису несёт и прямоугольник дефиса на конце прошлой строки: свой — последний
        const b = Array.from(range.getClientRects()).filter(r => r.width > 0).pop();
        if (!b) continue;
        const same = prev && Math.min(b.bottom, prev.bottom) - Math.max(b.top, prev.top)
          >= Math.min(b.height, prev.height) / 2;
        if (same) lines[lines.length - 1].push(segment);
        else lines.push([segment]);
        prev = b;
      }
    }
    return lines.map(l => {
      let n = l.length;
      while (n > 0 && !l[n - 1].trim()) n--;
      return n;
    }).filter(n => n > 0);
  };

  const all = Array.from(document.querySelectorAll('body *')).slice(0, MAXN);
  const rows = [];
  const media = [], texts = [], glass = [];
  let idx = 0;
  for (const el of all) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') continue;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) continue;
    const tag = el.tagName.toLowerCase();
    const role = el.getAttribute('role') || '';
    const interactive = ['button', 'a', 'input', 'select', 'textarea', 'summary'].includes(tag)
      || el.hasAttribute('tabindex') || ['button', 'link', 'menuitem', 'tab', 'switch', 'checkbox'].includes(role);
    const ownText = Array.from(el.childNodes)
      .filter(n => n.nodeType === 3 && n.textContent.trim())
      .map(n => n.textContent.trim()).join(' ').slice(0, 120);
    const bg = effBg(el);
    const fg = toHex(cs.color);
    const bc = toHex(cs.borderTopColor);
    const hid = (ownText || interactive)
      ? (clipHidden(cs) || (r.width <= 1.5 && r.height <= 1.5) || outsideClip(el, r)) : false;
    const hit = interactive ? hitArea(el, cs, r) : null;
    const bgImg = cs.backgroundImage || 'none';
    if (['img', 'video', 'canvas'].includes(tag) || /url\(/.test(bgImg)) {
      if (r.width > 40 && r.height > 40) media.push({ el, tag: /url\(/.test(bgImg) && tag !== 'img' ? 'background' : tag, r });
    }
    el.setAttribute('data-uia', String(idx));
    if (ownText && !hid) texts.push({ i: idx, el, r });
    if (cs.backdropFilter && cs.backdropFilter !== 'none') glass.push({ i: idx, el, r });
    rows.push({
      i: idx++, tag, sel: shortSel(el), role,
      x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width * 100) / 100, h: Math.round(r.height * 100) / 100,
      pt: px(cs.paddingTop), pr: px(cs.paddingRight), pb: px(cs.paddingBottom), pl: px(cs.paddingLeft),
      mt: px(cs.marginTop), mr: px(cs.marginRight), mb: px(cs.marginBottom), ml: px(cs.marginLeft),
      rg: px(cs.rowGap), cg: px(cs.columnGap),
      r1: px(cs.borderTopLeftRadius), r2: px(cs.borderTopRightRadius),
      r3: px(cs.borderBottomRightRadius), r4: px(cs.borderBottomLeftRadius),
      bw: px(cs.borderTopWidth), bwr: px(cs.borderRightWidth), bwb: px(cs.borderBottomWidth), bwl: px(cs.borderLeftWidth),
      sh: cs.boxShadow === 'none' ? null : cs.boxShadow,
      z: cs.zIndex === 'auto' ? null : Number(cs.zIndex),
      bd: (cs.backdropFilter && cs.backdropFilter !== 'none') ? cs.backdropFilter : null,
      fs: px(cs.fontSize), lh: cs.lineHeight === 'normal' ? 'normal' : px(cs.lineHeight),
      fw: Number(cs.fontWeight) || null, ls: cs.letterSpacing === 'normal' ? 0 : px(cs.letterSpacing),
      ff: (cs.fontFamily || '').split(',')[0].replace(/["']/g, '').slice(0, 30),
      fvn: cs.fontVariantNumeric, tt: cs.textTransform, ta: cs.textAlign,
      col: fg ? fg.hex : null, cola: fg ? fg.a : 1,
      bg: bg.hex, bggrad: bg.gradient, bgguess: bg.guessed,
      bcol: bc && bc.a > 0 ? bc.hex : null, bcola: bc ? bc.a : 0,
      ow: px(cs.outlineWidth), ost: cs.outlineStyle, oc: toHex(cs.outlineColor) ? toHex(cs.outlineColor).hex : null,
      pos: cs.position, ov: cs.overflowX + ' ' + cs.overflowY,
      mw: cs.maxWidth === 'none' ? null : px(cs.maxWidth),
      gtc: cs.gridTemplateColumns && cs.gridTemplateColumns !== 'none' ? cs.gridTemplateColumns.slice(0, 120) : null,
      tp: cs.transitionProperty, td: cs.transitionDuration, an: cs.animationName,
      txt: ownText, inter: interactive, disp: cs.display,
      dis: el.hasAttribute('disabled') || el.getAttribute('aria-disabled') === 'true',
      inflow: (() => { const p = el.parentElement; if (!p) return false;
        const d = getComputedStyle(el).display;
        return (d === 'inline' || d === 'inline-block') &&
               Array.from(p.childNodes).some(n => n.nodeType === 3 && n.textContent.trim().length > 1); })(),
      par: el.parentElement && el.parentElement.hasAttribute('data-uia') ? Number(el.parentElement.getAttribute('data-uia')) : null,
      svg: tag === 'svg' ? { w: Math.round(r.width), h: Math.round(r.height), sw: cs.strokeWidth, vb: el.getAttribute('viewBox') || '' } : null,
      inline: el.getAttribute('style') || '',
      hid, hw: hit ? hit.w : null, hh: hit ? hit.h : null,
      tlen: LINE_TAGS.includes(tag) ? (el.textContent || '').replace(/\s+/g, ' ').trim().length : null,
      tl: LINE_TAGS.includes(tag) && !hid ? lineChars(el) : null,
      ai: cs.alignItems, as: cs.alignSelf, fd: cs.flexDirection,
      bgi: /gradient/.test(bgImg) ? bgImg.slice(0, 300) : null,
      bgclip: cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text',
      onmedia: null, bdmedia: null,
    });
  }

  // текст над медиа: центр текстового узла внутри картинки, видео, canvas или фона-картинки, которые не лежат в самом узле
  const byI = new Map(rows.map(x => [x.i, x]));
  for (const t of texts) {
    const cx = t.r.left + t.r.width / 2, cy = t.r.top + t.r.height / 2;
    const m = media.find(m => m.el !== t.el && !t.el.contains(m.el) && !m.el.contains(t.el)
      && cx >= m.r.left && cx <= m.r.right && cy >= m.r.top && cy <= m.r.bottom);
    if (m) byI.get(t.i).onmedia = m.tag;
  }
  // стекло над видео или WebGL (canvas)
  for (const g of glass) {
    const m = media.find(m => (m.tag === 'video' || m.tag === 'canvas') && m.el !== g.el && !g.el.contains(m.el)
      && g.r.left < m.r.right && g.r.right > m.r.left && g.r.top < m.r.bottom && g.r.bottom > m.r.top);
    if (m) byI.get(g.i).bdmedia = m.tag;
  }

  const html = document.documentElement;
  return {
    rows,
    meta: {
      lang: html.getAttribute('lang') || '',
      scrollW: html.scrollWidth, innerW: window.innerWidth, innerH: window.innerHeight,
      bodyBg: getComputedStyle(document.body).backgroundColor,
      title: document.title,
      text: (document.body.innerText || '').slice(0, 20000),
      viewportMeta: (document.querySelector('meta[name=viewport]') || {}).content || '',
      styleSheets: Array.from(document.styleSheets).length,
    },
  };
}
"""

FOCUS_REST_JS = r"""
() => {
  const sel = 'a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])';
  const out = {};
  document.querySelectorAll(sel).forEach((el, n) => {
    el.setAttribute('data-uiafocus', String(n));
    const cs = getComputedStyle(el);
    out[n] = { ow: cs.outlineWidth, ost: cs.outlineStyle, oc: cs.outlineColor,
               sh: cs.boxShadow, bc: cs.borderTopColor, bg: cs.backgroundColor,
               sel: el.tagName.toLowerCase() + (el.id ? '#' + el.id : ''),
               txt: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 40) };
  });
  return out;
}
"""

FOCUS_NOW_JS = r"""
() => {
  const el = document.activeElement;
  if (!el || el === document.body) return null;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  return { n: el.getAttribute('data-uiafocus'), tag: el.tagName.toLowerCase(),
           ow: cs.outlineWidth, ost: cs.outlineStyle, oc: cs.outlineColor, oo: cs.outlineOffset,
           sh: cs.boxShadow, bc: cs.borderTopColor, bg: cs.backgroundColor,
           around: (() => { let p = el.parentElement;
             while (p) { const c = getComputedStyle(p).backgroundColor;
               const m = c.match(/rgba?\(([^)]+)\)/);
               if (m) { const v = m[1].split(/[,\s\/]+/).filter(Boolean).map(Number);
                 if (v.length < 4 || v[3] > 0.9) return c; }
               p = p.parentElement; } return 'rgb(255,255,255)'; })(),
           w: Math.round(r.width), h: Math.round(r.height),
           txt: (el.innerText || el.getAttribute('aria-label') || '').trim().slice(0, 40),
           clipped: (() => {
             const ring = (parseFloat(cs.outlineWidth) || 0) + Math.max(0, parseFloat(cs.outlineOffset) || 0);
             if (ring <= 0) return false;
             const box = { l: r.left - ring, t: r.top - ring, rt: r.right + ring, b: r.bottom + ring };
             let p = el.parentElement;
             while (p && p !== document.body) {
               const s = getComputedStyle(p);
               if (s.overflow !== 'visible' || s.overflowX !== 'visible' || s.overflowY !== 'visible') {
                 const pr = p.getBoundingClientRect();
                 if (box.l < pr.left - 0.5 || box.t < pr.top - 0.5 ||
                     box.rt > pr.right + 0.5 || box.b > pr.bottom + 0.5) return true;
               }
               p = p.parentElement;
             }
             return false; })() };
}
"""


# =====================================================================================
# 4. Вспомогательное
# =====================================================================================

def parse_shadows(css):
    """Разбить строку box-shadow на слои и вернуть список (offsetX, offsetY, blur, spread, inset)."""
    if not css or css == "none":
        return []
    parts, depth, cur = [], 0, ""
    for ch in css:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    layers = []
    for p in parts:
        inset = "inset" in p
        nums = [float(x) for x in re.findall(r"(-?\d+(?:\.\d+)?)px", p)]
        while len(nums) < 4:
            nums.append(0.0)
        layers.append((nums[0], nums[1], nums[2], nums[3], inset))
    return layers


def parse_durations(css):
    if not css:
        return []
    out = []
    for token in css.split(","):
        token = token.strip()
        m = re.match(r"^(-?\d+(?:\.\d+)?)(ms|s)$", token)
        if m:
            out.append(float(m.group(1)) * (1000 if m.group(2) == "s" else 1))
    return out


def in_scale(v, scale, tol=0.51):
    return any(abs(v - s) <= tol for s in scale)


def is_fraction(v, tol=0.01):
    return abs(v - round(v)) > tol


def gap_between(a, b):
    dx = max(0, max(a["x"] - (b["x"] + b["w"]), b["x"] - (a["x"] + a["w"])))
    dy = max(0, max(a["y"] - (b["y"] + b["h"]), b["y"] - (a["y"] + a["h"])))
    return math.hypot(dx, dy)


def okl(h):
    try:
        return hex2oklch(h)[0]
    except Exception:
        return None


TOP_ALIGN = ("normal", "stretch", "start", "flex-start", "self-start")


def misaligned_rows(rows, by_i):
    """Соседи одного ряда сетки или flex-строки со сдвигом по верху. Проверяются дети grid и flex-row контейнеров,
    выровненные по верху (align-items и align-self — normal, stretch, start); одним рядом считаются соседи, чьи боксы
    перекрываются по вертикали больше чем наполовину меньшего, а верх расходится больше чем на 1 px, но меньше
    половины меньшей высоты (дальше — это уже следующий ряд или соседи через строки сетки)."""
    kids = defaultdict(list)
    for r in rows:
        if r["par"] is not None and r["w"] >= 40 and r["h"] >= 20 and r["pos"] not in ("absolute", "fixed") \
                and not r.get("hid"):
            kids[r["par"]].append(r)
    out = []
    for pi, ks in kids.items():
        p = by_i.get(pi)
        if not p or len(ks) < 2:
            continue
        disp = p.get("disp") or ""
        if "grid" not in disp and not ("flex" in disp and (p.get("fd") or "row").startswith("row")):
            continue
        top = [k for k in ks if ((k.get("as") or "auto") if (k.get("as") or "auto") != "auto"
                                 else (p.get("ai") or "normal")) in TOP_ALIGN]
        for a, b in itertools.combinations(top, 2):
            mh = min(a["h"], b["h"])
            overlap = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            dy = abs(a["y"] - b["y"])
            if overlap > 0.5 * mh and 1 < dy < 0.5 * mh:
                out.append(f"{p['sel']}: {a['sel']} y={a['y']} и {b['sel']} y={b['y']} (сдвиг {dy} px)")
                break
    return out


# =====================================================================================
# 5. Проверки
# =====================================================================================

class Report:
    def __init__(self, target, preset, context):
        self.target = target
        self.preset = preset
        self.context = context      # {'scheme': 'light', 'viewport': '1440x900', ...}
        self.findings = []

    def add(self, cid, group, rule, found, threshold, ok, severity, examples=None, note=None):
        self.findings.append({
            "id": cid, "group": group, "rule": rule,
            "found": found, "threshold": threshold,
            "verdict": "OK" if ok is True else ("WARN" if ok is None else "FAIL"),
            "severity": severity,
            "examples": (examples or [])[:6],
            "note": note,
            "tell": tell_of(cid),
        })


def tells_summary(findings):
    """Приметы без повторов: одна запись на id приметы — какими проверками и на каких прогонах она найдена
    (вердикт FAIL или WARN). Одна примета из нескольких проверок и прогонов считается один раз."""
    out = {}
    for f in findings:
        t = f.get("tell")
        if not t or f["verdict"] == "OK":
            continue
        e = out.setdefault(t, {"checks": [], "runs": []})
        if f["id"] not in e["checks"]:
            e["checks"].append(f["id"])
        run = f.get("run")
        if run and run not in e["runs"]:
            e["runs"].append(run)
    return out


SEV_BY_CODE = {"B": SEV_BLOCKER, "S": SEV_SERIOUS, "D": SEV_POLISH}


def load_profile(name="marketing"):
    """Профиль проверок из `scripts/ui/data/<name>-profile.yaml` → (пресет, таблица профиля). Пресет — base профиля с
    его значениями и лимитами стекла из каталога эффектов; таблица — id проверки → action, severity, threshold,
    landing, basis (серьёзность — строкой отчёта)."""
    with open(kbpaths.data("ui", f"{name}-profile.yaml"), encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    preset = dict(PRESETS[spec["base"]])
    preset.update(spec.get("preset") or {})
    preset.update(name=spec.get("name", name), title=spec.get("title", preset["title"]), reference_tokens=False)
    glass = spec.get("glass")
    if glass:
        lim = load_glass_limits(glass["effect"])
        for key, field in glass["fields"].items():
            preset[key] = lim[field]
    table = {cid: dict(row, severity=SEV_BY_CODE[row["severity"]]) for cid, row in (spec.get("checks") or {}).items()}
    return preset, table


PROFILES = ("marketing",)            # профили данными: scripts/ui/data/<имя>-profile.yaml
RECOMPUTED_HERE = ("D3", "D4", "L4")  # пересчёт по узлам, который run_checks делает при пресете профиля


def preset_of(name):
    """Пресет прогона по имени → (пресет, таблица профиля или None): admin и consumer — пресеты кода, marketing —
    профиль данными."""
    return load_profile(name) if name in PROFILES else (PRESETS[name], None)


def default_preset(target, surface=None):
    """Пресет без ключа --preset: у страницы сайта — профиль marketing, у экрана приложения — admin. Поверхность —
    ключ --surface; без него у статичной копии артборда — манифест входа холста, у другой цели — экран приложения."""
    if surface is None and target:
        kbpaths.use("claude-design")
        from mockup_checks import input_surface
        surface = input_surface(str(target))
    return "marketing" if surface == "page" else "admin"


def apply_profile_alone(rep, table):
    """Профиль в прогоне самой утилиты: общие действия таблицы (apply_profile), а у проверок с пересчётом по узлам,
    которого здесь нет, — серьёзность профиля и пометка, кто считает порог страницы."""
    apply_profile(rep, table)
    for f in rep.findings:
        row = table.get(f["id"])
        if row and row["action"] == "recompute" and f["id"] not in RECOMPUTED_HERE:
            f["severity"] = row["severity"]
            f["threshold"] = f"{f['threshold']} (порог страницы — marketing_audit.py: {row['threshold']})"
    return rep


def apply_profile(rep, table, base="consumer"):
    """Общие действия таблицы профиля: keep, retune, severity, info. Пересчёт (recompute) — у кода профиля: D3, D4, L4
    считает run_checks при пресете профиля, остальные — scripts/creative/marketing_audit.py."""
    for f in rep.findings:
        row = table.get(f["id"])
        f["profile"] = row["action"] if row else "keep"
        f["base"] = row["basis"] if row else f"как в {base}"
        if not row:
            continue
        if row["action"] in ("retune", "severity"):
            f["severity"] = row["severity"]
        elif row["action"] == "info":
            f["verdict"] = "WARN"
            f["severity"] = row["severity"]
            f["threshold"] = "информативно (профиль marketing)"
    return rep


def run_checks(data, preset, opts, ctx):
    rows = data["rows"]
    meta = data["meta"]
    rep = Report(ctx["target"], preset["name"], ctx)
    by_i = {r["i"]: r for r in rows}
    # визуально скрытое (sr-only, 1×1, вне предка с обрезкой) — не текст на экране и не цель нажатия
    text_rows = [r for r in rows if r["txt"] and not r.get("hid")]
    interactive = [r for r in rows if r["inter"]]
    dark = ctx.get("scheme") == "dark"

    # ---------------------------------------------------------------- A. Отступы
    sp_vals = []
    for r in rows:
        for k in ("pt", "pr", "pb", "pl", "mt", "mr", "mb", "ml", "rg", "cg"):
            v = r[k]
            if v is not None and v != 0:
                sp_vals.append(v)
    n_sp = len(sp_vals) or 1
    in_sc = [v for v in sp_vals if in_scale(v, preset["spacing"])]
    share = len(in_sc) / n_sp
    bad = sorted({v for v in sp_vals if not in_scale(v, preset["spacing"])})
    rep.add("A1", "Отступы", "Доля padding/margin/gap из шкалы",
            f"{share*100:.1f} %", f"≥ {preset['spacing_in_scale_min']*100:.0f} %",
            share >= preset["spacing_in_scale_min"], SEV_SERIOUS,
            [f"вне шкалы: {', '.join(str(v) for v in bad[:12])}"] if bad else [])

    # значение со шкалы отступов токенов прогона (ДС проекта или эталон пресета) — решение ДС, а не «шкала десятками»
    ds_spacing = (getattr(opts, "tokens_set", None) or {}).get("spacing") or []
    five = sorted({v for v in sp_vals if abs(v % 5) < 0.01 and abs(v % 4) > 0.01 and not in_scale(v, ds_spacing)})
    rep.add("A2", "Отступы", "Значения, кратные 5 и не кратные 4 («шкала десятками»)",
            len(five), "0", not five, SEV_SERIOUS, [str(v) for v in five[:8]],
            note="значения со шкалы отступов токенов — не находка" if ds_spacing else None)

    gaps = sorted({r["rg"] for r in rows if r["rg"]} | {r["cg"] for r in rows if r["cg"]})
    rep.add("A3", "Отступы", "Уникальных значений gap", len(gaps), f"≤ {preset['unique_gap_max']}",
            len(gaps) <= preset["unique_gap_max"], SEV_POLISH, [", ".join(str(g) for g in gaps)])

    frac = [v for v in sp_vals if is_fraction(v)]
    rep.add("A4", "Отступы", "Доля дробных значений отступа",
            f"{len(frac)/n_sp*100:.1f} %", f"≤ {preset['fraction_values_max']*100:.0f} %",
            len(frac) / n_sp <= preset["fraction_values_max"], SEV_POLISH,
            [", ".join(str(v) for v in sorted(set(frac))[:8])])

    uniq_sp = sorted(set(sp_vals))
    rep.add("A5", "Отступы", "Уникальных значений отступа", len(uniq_sp),
            f"≤ {preset['unique_spacing_max']}", len(uniq_sp) <= preset["unique_spacing_max"],
            SEV_POLISH, [", ".join(str(v) for v in uniq_sp[:20])])

    # внешний padding контейнера >= внутренних gap
    bad_nest = []
    LAYOUT_GAP = 12   # зазоры мельче относятся к внутренностям компонента (иконка-текст), а не к раскладке
    for r in rows:
        kids_gap = max([max(c["rg"] or 0, c["cg"] or 0) for c in rows if c["par"] == r["i"]] + [0])
        own_pad = min([v for v in (r["pt"], r["pb"]) if v is not None] or [0])
        if kids_gap >= LAYOUT_GAP and own_pad and kids_gap > own_pad + 0.5:
            bad_nest.append(f"{r['sel']}: padding {own_pad}, зазор внутри {kids_gap}")
    rep.add("A6", "Отступы", "Внешний padding контейнера ≥ внутренних зазоров", len(bad_nest), "0",
            not bad_nest, SEV_POLISH, bad_nest)

    # ---------------------------------------------------------------- B. Размеры
    ctrl = [r for r in interactive if r["tag"] in ("button", "input", "select")
            or r["role"] == "button"]
    ctrl = [r for r in ctrl if r["h"] >= 12 and r["w"] >= 12
            and r["role"] != "switch"
            and not (r["tag"] == "input" and r["h"] <= 24 and r["w"] <= 48)]
    heights = sorted({round(r["h"]) for r in ctrl})
    rep.add("B1", "Размеры", "Уникальных высот контролов", len(heights),
            f"≤ {preset['unique_heights_max']}", len(heights) <= preset["unique_heights_max"],
            SEV_SERIOUS, [", ".join(str(h) for h in heights)])

    off_row = [h for h in heights if not in_scale(h, preset["heights"], tol=0.51)]
    rep.add("B2", "Размеры", f"Высоты вне ряда {'/'.join(str(x) for x in preset['heights'])}",
            len(off_row), "0", not off_row, SEV_SERIOUS, [", ".join(str(h) for h in off_row)])

    # одна высота в горизонтальном ряду
    rowsy = defaultdict(list)
    for r in ctrl:
        rowsy[round(r["y"] / 4) * 4].append(r)
    bad_rows = []
    for y, group in rowsy.items():
        if len(group) < 2:
            continue
        hs = {round(g["h"]) for g in group}
        if len(hs) > 1:
            bad_rows.append(f"y≈{y}: {sorted(hs)} ({', '.join(g['sel'] for g in group[:4])})")
    rep.add("B3", "Размеры", "Одна высота контролов в горизонтальном ряду", len(bad_rows), "0",
            not bad_rows, SEV_SERIOUS, bad_rows)

    icon_btn = [r for r in ctrl if not r["txt"] and r["w"] <= 56 and r["h"] <= 56
                and r["tag"] == "button" and r["role"] != "switch"]
    not_square = [f"{r['sel']} {r['w']}×{r['h']}" for r in icon_btn if abs(r["w"] - r["h"]) > 1]
    rep.add("B4", "Размеры", "Иконочные кнопки квадратные", len(not_square), "0",
            not not_square, SEV_POLISH, not_square)

    svgs_all = [r for r in rows if r["svg"]]
    svgs = [r for r in svgs_all if max(r["svg"]["w"], r["svg"]["h"]) <= 32]
    big_svg = [f"{r['sel']} {round(r['svg']['w'])}×{round(r['svg']['h'])}" for r in svgs_all if r not in svgs]
    svg_sizes = sorted({round(r["svg"]["w"]) for r in svgs})
    off_icons = [s for s in svg_sizes if s not in preset["icon_sizes"]]
    rep.add("B5", "Размеры", f"Размеры иконок из ряда {preset['icon_sizes']}", len(off_icons), "0",
            not off_icons, SEV_POLISH, [", ".join(str(s) for s in off_icons)] if off_icons else [])

    sw = sorted({r["svg"]["sw"] for r in svgs if r["svg"]["sw"] and r["svg"]["sw"] != "1px"})
    vb = sorted({r["svg"]["vb"] for r in svgs if r["svg"]["vb"]})
    rep.add("B5b", "Размеры", "Пиктограммы и иллюстрации (svg крупнее 32 px)", len(big_svg),
            "информативно", None, SEV_POLISH, big_svg,
            note="граница классов: до 32 px иконка, 48–96 пиктограмма, от 120 иллюстрация "
                 "(07-iconography-imagery/02 §4.2)")
    rep.add("B6", "Размеры", "Один набор иконок (один viewBox, одна толщина штриха)",
            f"viewBox: {len(vb)}, stroke-width: {max(len(sw), 1)}", "1 / 1",
            len(vb) <= 1, SEV_POLISH, [", ".join(vb[:4]), ", ".join(sw[:4])])

    # строки таблиц и списков одной высоты
    bad_lists = []
    for parent in {r["par"] for r in rows if r["par"] is not None}:
        kids = [r for r in rows if r["par"] == parent and r["tag"] in ("tr", "li")]
        if len(kids) >= 3:
            hs = {round(k["h"]) for k in kids}
            if len(hs) > 1:
                p = by_i.get(parent)
                bad_lists.append(f"{p['sel'] if p else parent}: высоты {sorted(hs)}")
    rep.add("B7", "Размеры", "Строки одного списка/таблицы одной высоты", len(bad_lists), "0",
            not bad_lists, SEV_POLISH, bad_lists)

    # ---------------------------------------------------------------- C. Форма
    radii = []
    for r in rows:
        for k in ("r1", "r2", "r3", "r4"):
            v = r[k]
            if v:
                radii.append(v)
    uniq_r = sorted(set(radii))
    rep.add("C1", "Форма", "Уникальных значений border-radius", len(uniq_r),
            f"≤ {preset['unique_radius_max']}", len(uniq_r) <= preset["unique_radius_max"],
            SEV_POLISH, [", ".join(str(v) for v in uniq_r)])

    off_r = [v for v in uniq_r if not in_scale(v, preset["radius"], tol=0.51)]
    rep.add("C2", "Форма", "Радиусы вне шкалы", len(off_r), "0", not off_r, SEV_POLISH,
            [", ".join(str(v) for v in off_r)])

    bad_nested_r = []
    for r in rows:
        if not r["r1"] or r["r1"] >= 900:
            continue
        p = by_i.get(r["par"])
        while p is not None and not p["r1"]:
            p = by_i.get(p["par"])
        if p and p["r1"] < 900 and r["r1"] > p["r1"] + 0.5:
            bad_nested_r.append(f"{r['sel']} r={r['r1']} внутри {p['sel']} r={p['r1']}")
    rep.add("C3", "Форма", "Вложенный радиус не больше внешнего", len(bad_nested_r), "0",
            not bad_nested_r, SEV_POLISH, bad_nested_r)

    bws = sorted({v for r in rows for v in (r["bw"], r["bwr"], r["bwb"], r["bwl"]) if v})
    off_bw = [v for v in bws if v not in preset["border_widths"]]
    rep.add("C4", "Форма", "Толщины границ только 0 / 1 / 2 px", len(off_bw), "0", not off_bw,
            SEV_POLISH, [", ".join(str(v) for v in off_bw)])

    too_round = [f"{r['sel']} r={r['r1']} при {r['w']}×{r['h']}"
                 for r in rows if r["r1"] and r["r1"] < 900 and r["r1"] > 0.25 * min(r["w"], r["h"]) + 0.5]
    rep.add("C5", "Форма", "Радиус ≤ 25 % меньшей стороны элемента", len(too_round), "0",
            not too_round, SEV_POLISH, too_round)

    # ---------------------------------------------------------------- D. Глубина
    shadows = [r["sh"] for r in rows if r["sh"]]
    uniq_sh = sorted(set(shadows))
    rep.add("D1", "Глубина", "Уникальных значений box-shadow", len(uniq_sh),
            f"≤ {preset['unique_shadow_max']}", len(uniq_sh) <= preset["unique_shadow_max"],
            SEV_POLISH, [s[:90] for s in uniq_sh[:4]])

    dirs = set()
    for s in uniq_sh:
        for (ox, oy, blur, spread, inset) in parse_shadows(s):
            if inset or (ox == 0 and oy == 0):
                continue
            dirs.add((0 if ox == 0 else (1 if ox > 0 else -1), 0 if oy == 0 else (1 if oy > 0 else -1)))
    rep.add("D2", "Глубина", "Один источник света (одинаковое направление теней)",
            len(dirs) if dirs else 0, "≤ 1", len(dirs) <= 1, SEV_POLISH,
            [str(sorted(dirs))] if len(dirs) > 1 else [])

    glass_rows = [r for r in rows if r["bd"]]
    glass = [r["sel"] for r in glass_rows]
    if preset.get("glass_view_max") is not None:
        # профиль страницы сайта: лимиты стекла — запись glass-panel каталога эффектов creative
        in_view = [r for r in glass_rows if r["y"] < meta["innerH"] and r["y"] + r["h"] > 0]
        over_media = [r for r in in_view if r.get("bdmedia")]

        def blur_px(r):
            m = re.search(r"blur\((-?\d+(?:\.\d+)?)px\)", r["bd"] or "")
            return float(m.group(1)) if m else 0.0
        bad_glass = []
        if len(glass_rows) > preset["glass_max"]:
            bad_glass.append(f"на странице {len(glass_rows)} > {preset['glass_max']}")
        if len(in_view) > preset["glass_view_max"]:
            bad_glass.append(f"в первом экране {len(in_view)} > {preset['glass_view_max']}")
        if len(over_media) > preset["glass_view_max_media"]:
            bad_glass.append(f"над видео или WebGL {len(over_media)} > {preset['glass_view_max_media']}")
        bad_glass += [f"{r['sel']}: blur {blur_px(r):g} px > {preset['glass_blur_max']}" for r in glass_rows
                      if blur_px(r) > preset["glass_blur_max"]]
        rep.add("D3", "Глубина", "Стекло: на странице, в первом экране, над видео или WebGL, размытие",
                f"{len(glass_rows)} (в первом экране {len(in_view)}, над видео или WebGL {len(over_media)})",
                f"≤ {preset['glass_max']} · ≤ {preset['glass_view_max']} · ≤ {preset['glass_view_max_media']} · "
                f"blur ≤ {preset['glass_blur_max']}", not bad_glass, SEV_POLISH, bad_glass + glass,
                note="лимиты — creative/06-effects-catalog/effects.yaml#glass-panel; цена кадра — замером")
    else:
        rep.add("D3", "Глубина", "Элементов с backdrop-filter", len(glass), f"≤ {preset['glass_max']}",
                len(glass) <= preset["glass_max"], SEV_POLISH, glass)

    glow = []
    for s in uniq_sh:
        for (ox, oy, blur, spread, inset) in parse_shadows(s):
            if not inset and ox == 0 and oy == 0 and blur > 8:
                glow.append(s[:70])
    if preset.get("glow_max") is not None:
        # профиль страницы сайта: свечение — только shadow.cta-glow у одной кнопки по решению арт-дирекции
        glow_el = [r["sel"] for r in rows if r["sh"] and any(
            not inset and ox == 0 and oy == 0 and blur > 8 for (ox, oy, blur, spread, inset) in parse_shadows(r["sh"]))]
        rep.add("D4", "Глубина", "Элементов со свечением (нулевое смещение, blur > 8)", len(glow_el),
                f"≤ {preset['glow_max']}", len(glow_el) <= preset["glow_max"], SEV_POLISH, glow_el,
                note="больше — примета neon-glow (creative/04-visual-language/03-color-surfaces-product.md §4.3)")
    else:
        rep.add("D4", "Глубина", "Свечения (тень с нулевым смещением и blur > 8)", len(glow), "0",
                not glow, SEV_SERIOUS, glow)

    n_blocks = max(len([r for r in rows if r["w"] > 40 and r["h"] > 20]), 1)
    sh_share = len(shadows) / n_blocks
    rep.add("D5", "Глубина", "Доля блоков с тенью", f"{sh_share*100:.1f} %",
            f"≤ {preset['shadow_share_max']*100:.0f} %", sh_share <= preset["shadow_share_max"],
            SEV_POLISH)

    deep = []
    for r in rows:
        if not r["sh"]:
            continue
        d, p = 0, by_i.get(r["par"])
        while p is not None:
            if p["sh"]:
                d += 1
            p = by_i.get(p["par"])
        if d > preset["nesting_shadow_max"]:
            deep.append(f"{r['sel']} (вложенность теней {d + 1})")
    rep.add("D6", "Глубина", "Глубина вложенности элементов с тенью", len(deep),
            f"≤ {preset['nesting_shadow_max'] + 1}", not deep, SEV_POLISH, deep)

    # ---------------------------------------------------------------- E. Слои
    zs = sorted({r["z"] for r in rows if r["z"] is not None})
    off_z = [z for z in zs if z not in preset["zindex"]]
    rep.add("E1", "Слои", "z-index вне шкалы", len(off_z), "0", not off_z, SEV_SERIOUS,
            [", ".join(str(z) for z in off_z)])
    big_z = [z for z in zs if z > 1500]
    rep.add("E2", "Слои", "z-index больше 1500", len(big_z), "0", not big_z, SEV_SERIOUS,
            [", ".join(str(z) for z in big_z)])

    # ---------------------------------------------------------------- F. Цели нажатия
    # Цель — зона нажатия: бокс элемента или его абсолютно позиционированный ::before/::after (hw × hh).
    tmin = preset["target_min"]
    targets = [r for r in interactive if r["w"] > 0 and r["h"] > 0 and not r.get("hid")]
    hit_w = lambda r: max(r["w"], r.get("hw") or 0)  # noqa: E731
    hit_h = lambda r: max(r["h"], r.get("hh") or 0)  # noqa: E731
    # SC 2.5.8, исключение «Inline»: ссылка внутри строки текста размером не нормируется
    inline_links = [r for r in targets if r["tag"] == "a" and (r.get("inflow") or r.get("disp") == "inline")]
    targets_sized = [r for r in targets if r not in inline_links]
    small = [r for r in targets_sized if min(hit_w(r), hit_h(r)) < tmin - 0.5]
    bad_small = []
    for t in small:
        near = any(gap_between(t, o) < preset["target_gap_min"] for o in targets if o["i"] != t["i"])
        if near:
            bad_small.append(f"{t['sel']} {hit_w(t)}×{hit_h(t)} «{t['txt'][:20]}»")
    rep.add("F1", "Цели", f"Цели меньше {tmin}×{tmin} без зазора {preset['target_gap_min']} px",
            len(bad_small), "0", not bad_small, SEV_BLOCKER, bad_small)
    rep.add("F2", "Цели", f"Всего целей меньше {tmin}×{tmin} (включая разнесённые)",
            f"{len(small)} из {len(targets_sized)} (ещё {len(inline_links)} инлайновых ссылок вне нормы)", "информативно",
            True if not small else None, SEV_SERIOUS,
            [f"{t['sel']} {hit_w(t)}×{hit_h(t)}" for t in small[:6]],
            note="SC 2.5.8 допускает недоразмерную цель, если круги диаметром 24 px вокруг центров "
                 "соседних целей не пересекаются; нарушение этого условия ловит F1")
    if ctx.get("touch"):
        tt = preset.get("target_min_touch", 44)
        under = [r for r in targets_sized if min(hit_w(r), hit_h(r)) < tt - 0.5]
        rep.add("F3", "Цели", f"На таче зона нажатия каждой цели ≥ {tt}×{tt}", len(under), "0", not under,
                SEV_SERIOUS, [f"{t['sel']} {hit_w(t)}×{hit_h(t)} «{t['txt'][:20]}»" for t in under],
                note="видимый контрол может быть меньше: зону добирают padding или ::before; плотность её не "
                     "уменьшает; ссылка внутри строки текста — исключение 2.5.8 "
                     "(ux/08-accessibility/01-wcag22-as-build-rules.md §12.4)")

    # ---------------------------------------------------------------- G. Фокус
    no_focus = []
    for r in interactive:
        if r["ost"] == "none" and not r["sh"]:
            no_focus.append(r["sel"])
    rep.add("G1", "Фокус", "Интерактивные элементы без outline и без box-shadow в покое",
            len(no_focus), "информативно", None, SEV_POLISH, no_focus[:6],
            note="сам по себе не дефект: кольцо может появляться только в :focus-visible, см. G3")

    # ---------------------------------------------------------------- H. Типографика
    fss = sorted({r["fs"] for r in text_rows if r["fs"]})
    rep.add("H1", "Типографика", "Уникальных размеров шрифта (у элементов с собственным текстом)",
            len(fss), f"≤ {preset['unique_font_sizes_max']}",
            len(fss) <= preset["unique_font_sizes_max"], SEV_SERIOUS,
            [", ".join(str(v) for v in fss)])

    off_fs = [v for v in fss if not in_scale(v, preset["font_sizes"], tol=0.51)]
    rep.add("H2", "Типографика", "Кегли вне шкалы", len(off_fs), "0", not off_fs, SEV_SERIOUS,
            [", ".join(str(v) for v in off_fs)])

    fws = sorted({r["fw"] for r in text_rows if r["fw"]})
    rep.add("H3", "Типографика", "Уникальных весов шрифта", len(fws),
            f"≤ {preset['unique_font_weights_max']}", len(fws) <= preset["unique_font_weights_max"],
            SEV_POLISH, [", ".join(str(v) for v in fws)])
    light = [v for v in fws if v < 400]
    rep.add("H4", "Типографика", "Веса легче 400", len(light), "0", not light, SEV_POLISH,
            [", ".join(str(v) for v in light)])

    normal_lh = [r["sel"] for r in text_rows if r["lh"] == "normal"]
    rep.add("H5", "Типографика", "line-height: normal", len(normal_lh), "0", not normal_lh,
            SEV_POLISH, normal_lh[:6])

    frac_lh = sorted({r["lh"] for r in text_rows if isinstance(r["lh"], (int, float)) and is_fraction(r["lh"])})
    rep.add("H6", "Типографика", "Дробные line-height в px", len(frac_lh), "0", not frac_lh,
            SEV_POLISH, [", ".join(str(v) for v in frac_lh)])

    body = [r for r in text_rows if r["fs"] and 13 <= r["fs"] <= 17
            and isinstance(r["lh"], (int, float)) and len(r["txt"]) > 40]
    lo, hi = preset["body_leading"]
    bad_lead = [f"{r['sel']} {r['fs']}/{r['lh']} = {r['lh']/r['fs']:.2f}" for r in body
                if not (lo <= r["lh"] / r["fs"] <= hi)]
    rep.add("H7", "Типографика", f"Интерлиньяж тела в коридоре {lo}–{hi}", len(bad_lead), "0",
            not bad_lead, SEV_POLISH, bad_lead)

    # длина строки абзаца в знаках — самая длинная строка, как её разложил браузер (`tl`: знаков в каждой строке)
    narrow = meta["innerW"] < (ctx.get("first_bp") or first_breakpoint(None))
    lo_c, hi_c = preset["measure_chars_narrow"] if narrow else preset["measure_chars"]
    long_lines = []
    for r in rows:
        if r["tag"] not in ("p", "li", "dd", "blockquote") or r.get("hid"):
            continue
        lines = r.get("tl")
        if lines is None:
            # данные без строк (синтетика вызывающей утилиты): ширина абзаца против пресета
            if r["txt"] and len(r["txt"]) >= 120 and r["w"] > preset["para_max_width"]:
                long_lines.append(f"{r['sel']} {r['w']}px > {preset['para_max_width']}px")
            continue
        if (r.get("tlen") or 0) <= 120 or not lines:
            continue
        if max(lines) > hi_c:
            shown = ", ".join(str(n) for n in lines[:8]) + (", …" if len(lines) > 8 else "")
            long_lines.append(f"{r['sel']} — {max(lines)} знаков в самой длинной строке (строки: {shown})")
    rep.add("H8", "Типографика", f"Длина строки абзаца ≤ {hi_c} знаков" + (" (окно уже первого брейкпоинта)" if narrow else ""),
            len(long_lines), "0", not long_lines, SEV_SERIOUS, long_lines,
            note=f"норма {lo_c}–{hi_c} знаков, не больше {preset['measure_chars_max']}; ширину задают в ch "
                 "(ux/03-layout-placement/02-grid-spacing-density.md §4)")

    rep.add("H9", "Типографика", "Атрибут lang на <html>", meta["lang"] or "нет", "задан",
            bool(meta["lang"]), SEV_SERIOUS)

    caps = [r["sel"] for r in text_rows if r["tt"] in ("uppercase", "capitalize")]
    rep.add("H10", "Типографика", "text-transform: uppercase / capitalize", len(caps),
            "0 (кроме осознанных капс-лейблов)", not caps, SEV_POLISH, caps[:6])

    just = [r["sel"] for r in text_rows if r["ta"] == "justify"]
    rep.add("H11", "Типографика", "text-align: justify", len(just), "0", not just, SEV_POLISH, just)

    # табличные цифры в числовых колонках
    num_cells = [r for r in rows if r["tag"] == "td" and re.fullmatch(r"[\d\s.,+\-%₽$€]+", (r["txt"] or "x"))]
    no_tnum = [r["sel"] for r in num_cells if "tabular-nums" not in (r["fvn"] or "")]
    rep.add("H12", "Типографика", "tabular-nums в числовых ячейках таблиц",
            f"{len(num_cells) - len(no_tnum)} из {len(num_cells)}", "все",
            not no_tnum if num_cells else True, SEV_SERIOUS, no_tnum[:6])

    # русская типографика по видимому тексту
    page_text = meta.get("text", "")
    en_nums = EN_NUMBER_RE.findall(page_text)
    rep.add("H13", "Типографика", "Английский формат разрядов (1,234) в русском тексте",
            len(en_nums), "0", not en_nums, SEV_POLISH, en_nums[:6])
    glued = PERCENT_GLUED_RE.findall(page_text)
    rep.add("H14", "Типографика", "Знак % слитно с числом", len(glued), "0", not glued,
            SEV_POLISH, glued[:6])
    straight = re.findall(r'"[А-Яа-яЁё][^"]{0,40}"', page_text)
    rep.add("H15", "Типографика", "Программистские кавычки в русском тексте", len(straight), "0",
            not straight, SEV_POLISH, straight[:4])

    # ---------------------------------------------------------------- I. Цвет и контраст
    fails, warns, media_warns, disabled_bad = [], [], [], []
    for r in text_rows:
        if not r["col"] or not r["fs"]:
            continue
        if r.get("onmedia"):
            # фон берётся от предка, а под буквами — картинка, видео или canvas: число недостоверно в обе стороны
            media_warns.append(f"{r['sel']} над {r['onmedia']} «{r['txt'][:24]}»")
            continue
        if r.get("dis"):
            lc = abs(apca(r["col"] if r["cola"] >= 0.999 else composite(r["col"], r["cola"], r["bg"]), r["bg"]))
            if not (30 <= lc <= 60):
                disabled_bad.append(f"{r['sel']} Lc {lc:.1f} «{r['txt'][:20]}»")
            continue
        fg = r["col"] if r["cola"] >= 0.999 else composite(r["col"], r["cola"], r["bg"])
        ratio = wcag(fg, r["bg"])
        large = r["fs"] >= 24 or (r["fs"] >= 18.66 and (r["fw"] or 400) >= 700)
        need = preset["large_text_contrast_min"] if large else preset["text_contrast_min"]
        if ratio < need - 0.005:
            item = f"{r['sel']} {fg} на {r['bg']} = {ratio:.2f} (нужно {need}) «{r['txt'][:24]}»"
            (warns if (r["bggrad"] or r["bgguess"]) else fails).append(item)
    rep.add("I1", "Цвет", f"Контраст текста ≥ {preset['text_contrast_min']}:1 "
            f"(крупный ≥ {preset['large_text_contrast_min']}:1)", len(fails), "0",
            not fails, SEV_BLOCKER, fails)
    rep.add("I1c", "Цвет", "Отключённые элементы в коридоре APCA Lc 30–60 "
            "(WCAG 1.4.3 их не нормирует, но невидимая кнопка — тоже дефект)",
            len(disabled_bad), "0", not disabled_bad, SEV_POLISH, disabled_bad)
    if warns:
        rep.add("I1b", "Цвет", "Текст на градиенте или на полупрозрачной подложке (значение недостоверно)",
                len(warns), "проверить глазами", None, SEV_SERIOUS, warns)
    if media_warns:
        rep.add("I1m", "Цвет", "Текст над картинкой, видео или canvas: контраст по фону предка недостоверен",
                len(media_warns), "проверить F83", None, SEV_SERIOUS, media_warns,
                note="F83 — худший пиксель под буквами и кадры видео, 4,5 : 1 (крупный 3 : 1): "
                     "scripts/ai-media/page_accept.py --contrast (ai-media/10-web-integration/03-text-over-media-and-effects.md §1)")

    # граница контрола к своему фону
    border_min = preset["border_contrast_min"] if opts.strict_border else preset["border_contrast_practice"]
    bad_border = []
    for r in rows:
        if r["tag"] not in ("input", "select", "textarea") or not r["bcol"] or not r["bw"]:
            continue
        parent = by_i.get(r["par"])
        around = parent["bg"] if parent else r["bg"]
        ratio = wcag(r["bcol"], around)
        if ratio < border_min - 0.005:
            bad_border.append(f"{r['sel']} {r['bcol']} на {around} = {ratio:.2f}")
    rep.add("I2", "Цвет", f"Контраст границы поля ввода ≥ {border_min}:1 "
            f"({'WCAG 1.4.11' if opts.strict_border else 'режим практики'})",
            len(bad_border), "0", not bad_border, SEV_SERIOUS, bad_border)

    tcolors = sorted({r["col"] for r in text_rows if r["col"]})
    bgcolors = sorted({r["bg"] for r in rows})
    bcolors = sorted({r["bcol"] for r in rows if r["bcol"] and r["bw"]})
    rep.add("I3", "Цвет", "Уникальных цветов текста", len(tcolors),
            f"≤ {preset['unique_text_colors_max']}", len(tcolors) <= preset["unique_text_colors_max"],
            SEV_POLISH, [", ".join(tcolors[:12])])
    rep.add("I4", "Цвет", "Уникальных цветов фона", len(bgcolors),
            f"≤ {preset['unique_bg_colors_max']}", len(bgcolors) <= preset["unique_bg_colors_max"],
            SEV_POLISH, [", ".join(bgcolors[:12])])
    rep.add("I5", "Цвет", "Уникальных цветов границ", len(bcolors),
            f"≤ {preset['unique_border_colors_max']}", len(bcolors) <= preset["unique_border_colors_max"],
            SEV_POLISH, [", ".join(bcolors[:12])])

    if opts.tokens_set:
        allowed = set(opts.tokens_set["colors"])
        composited = {r["bg"] for r in rows if r["bgguess"]}   # результат наложения альфы, а не токен
        stray = sorted({c for c in tcolors + bgcolors + bcolors
                        if c and c.lower() not in allowed and c not in composited})
        rep.add("I6", "Цвет", "Цвета, которых нет в наборе токенов", len(stray), "0", not stray,
                SEV_SERIOUS, [", ".join(stray[:12])],
                note="полупрозрачные слои (скрим, границы через альфу) исключены: их результат "
                     "вычисляется, а не хранится в наборе")
        # «фирменный чёрный»: тёмная нейтраль литералом вне токенов. Светлота в коридоре тёмного фона сама не примета —
        # примета значение вне шкалы ДС (ui/01-color/04-dark-theme.md §2.1)
        dark_hi = preset.get("dark_bg_L", (0.13, 0.22))[1]
        near_black = []
        for c in stray:
            try:
                L, C, H = hex2oklch(c)
            except Exception:
                continue
            if L <= dark_hi and C <= preset.get("neutral_C_max", 0.05):
                near_black.append(c)
        rep.add("I10", "Цвет", "Тёмная нейтраль литералом вне токенов («фирменный чёрный»)", len(near_black), "0",
                not near_black, SEV_POLISH, [", ".join(near_black[:12])])

    # нейтрали: одно семейство
    # статусные подложки (#dcfce7, #ffe2e2) тоже низкохроматичны, поэтому семейство нейтрали
    # считается только по цветам текста и границ: там статусные оттенки насыщеннее порога
    neutrals = [c for c in tcolors + bcolors if c]
    hues, chromas = [], []
    for c in neutrals:
        try:
            L, C, H = hex2oklch(c)
        except Exception:
            continue
        if C <= preset.get("neutral_C_max", 0.05) and 0.02 < L < 0.99:
            hues.append(H); chromas.append(C)
    spread = (max(hues) - min(hues)) if len(hues) > 1 else 0
    tinted = [h for h, c in zip(hues, chromas) if c > 0.002]
    spread_t = (max(tinted) - min(tinted)) if len(tinted) > 1 else 0
    rep.add("I7", "Цвет", "Нейтраль одного семейства (разброс оттенка тонированных серых)",
            f"{spread_t:.0f}°", "≤ 40°", spread_t <= 40, SEV_POLISH,
            [f"хрома до {max(chromas):.3f}" if chromas else ""])

    if dark:
        bgl = okl(meta_bg_hex(meta, rows))
        dlo, dhi = preset.get("dark_bg_L", (0.13, 0.22))
        rep.add("I8", "Цвет", f"Фон тёмной темы в коридоре OKLCH L {dlo*100:.0f}–{dhi*100:.0f} %",
                f"{bgl*100:.1f} %" if bgl else "?", f"{dlo*100:.0f}–{dhi*100:.0f} %",
                bool(bgl and dlo <= bgl <= dhi), SEV_SERIOUS)
        pure_white = [r["sel"] for r in text_rows if r["col"] and r["col"].lower() == "#ffffff" and (r["fs"] or 0) >= 20]
        rep.add("I9", "Цвет", "Чистый белый текст крупным кеглем в тёмной теме", len(pure_white),
                "0", not pure_white, SEV_POLISH, pure_white[:5])

    # ---------------------------------------------------------------- J. Раскладка
    forms = [r for r in rows if r["tag"] == "form" or
             (len([k for k in rows if k["par"] == r["i"] and k["tag"] in ("input", "select", "textarea")]) >= 3)]
    wide_forms = [f"{r['sel']} {r['w']}px" for r in forms if r["w"] > preset["form_max_width"]]
    rep.add("J1", "Раскладка", f"Формы не шире {preset['form_max_width']} px", len(wide_forms), "0",
            not wide_forms, SEV_SERIOUS, wide_forms)

    sidebars = [r for r in rows if r["x"] < 8 and r["h"] > meta["innerH"] * 0.45
                and 120 < r["w"] < 480]
    sidebars.sort(key=lambda r: -r["h"])
    sw_ = round(sidebars[0]["w"]) if sidebars else None
    rep.add("J2", "Раскладка", f"Сайдбар в коридоре {preset['sidebar_min']}–{preset['sidebar_max']} px",
            sw_ if sw_ else "не найден", f"{preset['sidebar_min']}–{preset['sidebar_max']}",
            True if sw_ is None else (preset["sidebar_min"] <= sw_ <= preset["sidebar_max"]),
            SEV_SERIOUS, [sidebars[0]["sel"]] if sidebars else [])

    mains = [r for r in rows if r["tag"] == "main" or r["role"] == "main"]
    mw_ = round(mains[0]["w"]) if mains else None
    rep.add("J3", "Раскладка", f"Контентной области остаётся ≥ {preset['content_min']} px",
            mw_ if mw_ else "main не найден", f"≥ {preset['content_min']}",
            True if mw_ is None else mw_ >= preset["content_min"], SEV_SERIOUS)

    sticky = [r for r in rows if r["pos"] in ("sticky", "fixed")
              and r["y"] < meta["innerH"] * 0.5 and r["w"] > meta["innerW"] * 0.4
              and r["h"] <= meta["innerH"] * 0.25]
    ssum = round(sum(r["h"] for r in sticky))
    rep.add("J4", "Раскладка", f"Сумма прилипших полос ≤ {preset['sticky_sum_max']} px", ssum,
            f"≤ {preset['sticky_sum_max']}", ssum <= preset["sticky_sum_max"], SEV_POLISH,
            [f"{r['sel']} {round(r['h'])}px" for r in sticky])

    hscroll = meta["scrollW"] > meta["innerW"] + 1
    rep.add("J5", "Раскладка", "Нет горизонтальной прокрутки документа",
            f"{meta['scrollW']} vs {meta['innerW']}", "scrollWidth ≤ innerWidth", not hscroll,
            SEV_BLOCKER)

    rigid = []
    for r in rows:
        g = r["gtc"]
        if not g:
            continue
        tracks = g.split()
        if len(tracks) >= 3 and len(set(tracks)) == 1 and "minmax" not in g:
            rigid.append(f"{r['sel']}: {g[:50]}")
    rep.add("J6", "Раскладка", "Сетки с жёстко заданным числом равных колонок", len(rigid), "≤ 2",
            len(rigid) <= 2, SEV_POLISH, rigid)

    centered = []
    if sidebars and mains:
        m = mains[0]
        if abs(m["ml"] or 0) > 24 and abs((m["ml"] or 0) - (m["mr"] or 0)) < 2:
            centered.append(m["sel"])
    rep.add("J7", "Раскладка", "Контент не центрирован при наличии сайдбара", len(centered), "0",
            not centered, SEV_POLISH, centered)

    headers = [r for r in rows if r["tag"] == "header" and r["w"] > meta["innerW"] * 0.4]
    tall = [f"{r['sel']} {round(r['h'])}px" for r in headers if r["h"] > preset["page_header_max"]]
    rep.add("J8", "Раскладка", f"Шапка страницы не выше {preset['page_header_max']} px", len(tall),
            "0", not tall, SEV_POLISH, tall)

    mis = misaligned_rows(rows, by_i)
    rep.add("J9", "Раскладка", "Соседи в ряду сетки или flex-строки выровнены по верху", len(mis), "0", not mis,
            SEV_SERIOUS, mis, note="сдвиг внутри ряда даёт отступ одного из соседей (например, margin-top правила "
                                   "стопки `.card + .card` у карточки в сетке), а не решение раскладки")

    # ---------------------------------------------------------------- K. Движение
    all_props = [r["tp"] for r in rows if r["tp"] and r["tp"] != "all 0s ease 0s"]
    trans_all = [r["sel"] for r in rows if r["tp"] and "all" in r["tp"].split(",")[0]
                 and parse_durations(r["td"]) and max(parse_durations(r["td"])) > 0]
    rep.add("K1", "Движение", "transition: all", len(trans_all), "0", not trans_all, SEV_POLISH,
            trans_all[:6])

    durs = []
    for r in rows:
        durs.extend([d for d in parse_durations(r["td"]) if d > 0])
    uniq_d = sorted(set(durs))
    off_d = [d for d in uniq_d if not in_scale(d, preset["durations"], tol=1)]
    cap, exc = preset.get("duration_max"), preset.get("duration_max_exception")
    over = [d for d in uniq_d if cap is not None and d > cap + 0.5 and not (exc is not None and d <= exc + 0.5)]
    near = [d for d in uniq_d if cap is not None and exc is not None and cap + 0.5 < d <= exc + 0.5]
    rep.add("K2", "Движение", "Длительности в шкале токенов" + (f" и не длиннее потолка пресета {cap} мс" if cap else ""),
            len(off_d) + len(over), "0", False if (off_d or over) else (None if near else True), SEV_POLISH,
            ([f"вне шкалы: {', '.join(f'{d:.0f}ms' for d in off_d)}"] if off_d else [])
            + ([f"длиннее потолка: {', '.join(f'{d:.0f}ms' for d in over)}"] if over else [])
            + ([f"до {exc} мс — только исключение пресета: {', '.join(f'{d:.0f}ms' for d in near)}"] if near else []),
            note=(f"потолок пресета {preset.get('ds_preset', preset['name'])} — {cap} мс, исключение до {exc} мс: подложка "
                  "у A, онбординг и полноэкранный шаг у B (ui/14-recipes/11-presets.md)") if cap else None)
    share300 = (len([d for d in durs if abs(d - 300) < 1]) / len(durs)) if durs else 0
    rep.add("K3", "Движение", "Доля длительностей 300 ms", f"{share300*100:.1f} %",
            f"≤ {preset['duration_300_share_max']*100:.0f} %",
            share300 <= preset["duration_300_share_max"], SEV_POLISH)

    # ---------------------------------------------------------------- L. Антислоп
    emoji = EMOJI_RE.findall(page_text)
    rep.add("L1", "Антислоп", "Эмодзи в интерфейсе", len(emoji), "0", not emoji, SEV_SERIOUS,
            ["".join(dict.fromkeys(emoji))[:20]] if emoji else [])

    # «почти, но не совсем»: пары близких, но не равных значений
    def almost(vals, scale, lo=1, hi=3):
        """Пара близких значений считается дефектом, только если хотя бы одно из них вне шкалы:
        соседние ступени объявленной шкалы (11 и 12, 6 и 8) — это решение, а не «почти, но не совсем»."""
        vals = sorted(set(round(v, 1) for v in vals))
        out = []
        for a, b in zip(vals, vals[1:]):
            if lo <= b - a <= hi and not (in_scale(a, scale) and in_scale(b, scale)):
                out.append(f"{a} / {b}")
        return out
    almost_fs = almost(fss, preset["font_sizes"])
    almost_r = almost([v for v in uniq_r if v < 900], preset["radius"])
    almost_h = almost([float(h) for h in heights], preset["heights"])
    almost_all = almost_fs + almost_r + almost_h
    rep.add("L2", "Антислоп", "«Почти, но не совсем»: пары величин с разницей 1–3 px",
            len(almost_all), "0", not almost_all, SEV_POLISH,
            [f"кегли: {', '.join(almost_fs)}" if almost_fs else "",
             f"радиусы: {', '.join(almost_r)}" if almost_r else "",
             f"высоты: {', '.join(almost_h)}" if almost_h else ""])

    inline_hex = [f"{r['sel']}: {r['inline'][:50]}" for r in rows
                  if r["inline"] and re.search(r"#[0-9a-fA-F]{3,8}|rgba?\(", r["inline"])]
    rep.add("L3", "Антислоп", "Литералы цвета в inline-стилях", len(inline_hex), "0",
            not inline_hex, SEV_POLISH, inline_hex[:6])

    band = preset.get("purple_band")
    if band:
        # профиль страницы сайта: градиентный фон и mesh — приём при концепции; примета — градиентный текст и
        # hero-градиент первого экрана в фиолетовой полосе (creative/08-uniqueness-anti-slop/01-cliche-policy.md §4.1)
        def in_band(css):
            for m in re.finditer(r"rgba?\(([^)]*)\)", css or ""):
                p = [x for x in re.split(r"[,\s/]+", m.group(1)) if x]
                try:
                    L, C, H = hex2oklch("#%02x%02x%02x" % tuple(int(round(float(x))) for x in p[:3]))
                except Exception:
                    continue
                if C >= band["chroma_min"] and band["hue"][0] <= H <= band["hue"][1]:
                    return True
            return False
        grad_text = [r["sel"] for r in rows if r.get("bgclip") and r.get("bgi")]
        hero = [r["sel"] for r in rows if r.get("bgi") and not r.get("bgclip") and r["y"] < meta["innerH"]
                and r["w"] >= meta["innerW"] * 0.5 and r["h"] >= meta["innerH"] * 0.25 and in_band(r["bgi"])]
        rep.add("L4", "Антислоп", "Градиентный текст и фиолетовый hero-градиент первого экрана",
                len(grad_text) + len(hero), "0 без решения арт-дирекции", True if not (grad_text or hero) else None,
                SEV_POLISH, ([f"градиентный текст: {', '.join(grad_text[:4])}"] if grad_text else [])
                + ([f"hero в полосе {band['hue'][0]}–{band['hue'][1]}°: {', '.join(hero[:4])}"] if hero else []))
    else:
        grads = [r["sel"] for r in rows if r["bggrad"] and r["w"] > 80 and r["h"] > 40]
        rep.add("L4", "Антислоп", "Крупные градиентные заливки", len(grads), "информативно", None,
                SEV_POLISH, grads[:6],
                note="фиолетово-синий градиент — главный цветовой маркер генерации, см. 01-color/06 §4.2")

    fams = sorted({r["ff"] for r in text_rows if r["ff"]})
    rep.add("L5", "Антислоп", "Гарнитур в интерфейсе", len(fams), "≤ 2 (текстовая + моно)",
            len(fams) <= 2, SEV_POLISH, [", ".join(fams)])

    return rep


def meta_bg_hex(meta, rows):
    m = re.match(r"rgba?\(([^)]+)\)", meta.get("bodyBg", "") or "")
    if m:
        p = [float(x) for x in re.split(r"[,\s/]+", m.group(1)) if x]
        if len(p) >= 3:
            return "#%02x%02x%02x" % tuple(int(round(v)) for v in p[:3])
    return rows[0]["bg"] if rows else "#ffffff"


# =====================================================================================
# 6. Динамические прогоны: hover, Tab, reduced motion
# =====================================================================================

def check_focus(page, rep, preset, n_tabs):
    rest = page.evaluate(FOCUS_REST_JS)
    if not rest:
        rep.add("G2", "Фокус", "Фокусируемых элементов на странице", 0, "> 0", None, SEV_POLISH)
        return
    seen, no_ring, thin, clipped, low = [], [], [], [], []
    page.evaluate("() => { document.body.focus && document.body.focus(); }")
    for _ in range(n_tabs):
        page.keyboard.press("Tab")
        cur = page.evaluate(FOCUS_NOW_JS)
        if not cur or cur["n"] is None:
            continue
        key = cur["n"]
        if key in seen:
            continue
        seen.append(key)
        base = rest.get(key) or rest.get(str(key)) or {}
        ow = float((cur["ow"] or "0px").replace("px", "") or 0)
        changed = (cur["ost"] != "none" and ow > 0) or (cur["sh"] != base.get("sh")) \
            or (cur["bc"] != base.get("bc")) or (cur["bg"] != base.get("bg"))
        label = f"{cur['tag']} «{cur['txt'][:24]}»"
        if not changed:
            no_ring.append(label)
        elif cur["ost"] != "none" and 0 < ow < preset["focus_width_min"]:
            thin.append(f"{label}: outline {ow}px")
        if changed and cur["clipped"]:
            clipped.append(label)
        if cur["ost"] != "none" and ow > 0 and cur["oc"]:
            ring, _ = _to_hex(cur["oc"])
            offset = float((cur.get("oo") or "0px").replace("px", "") or 0)
            # кольцо с положительным offset лежит на фоне вокруг элемента, с отрицательным — на самом элементе
            surface_css = cur.get("around") if offset > 0.5 else cur["bg"]
            surface, alpha = _to_hex(surface_css)
            if ring and surface and alpha > 0.9:
                ratio = wcag(ring, surface)
                if ratio < 2.995:
                    where = "фону вокруг" if offset > 0.5 else "элементу"
                    low.append(f"{label}: кольцо {ring} к {where} {surface} = {ratio:.2f}")
    rep.add("G2", "Фокус", f"Видимый индикатор фокуса при обходе Tab ({len(seen)} остановок)",
            len(no_ring), "0", not no_ring, SEV_BLOCKER, no_ring)
    rep.add("G3", "Фокус", f"Толщина индикатора ≥ {preset['focus_width_min']} px", len(thin), "0",
            not thin, SEV_SERIOUS, thin)
    rep.add("G4", "Фокус", "Индикатор не обрезан предком с overflow", len(clipped), "0",
            not clipped, SEV_SERIOUS, clipped)
    rep.add("G5", "Фокус", "Контраст кольца фокуса к элементу ≥ 3:1", len(low), "0", not low,
            SEV_SERIOUS, low)


HOVER_READ_JS = r"""
(i) => {
  const el = document.querySelector('[data-uia="' + i + '"]');
  if (!el) return null;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  const top = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height / 2, 12));
  return { bg: cs.backgroundColor, col: cs.color, bc: cs.borderTopColor,
           sh: cs.boxShadow, tr: cs.transform, cur: cs.cursor,
           ol: cs.outlineStyle + ' ' + cs.outlineWidth + ' ' + cs.outlineColor,
           hit: !!(top && (top === el || el.contains(top) || top.contains(el))) };
}
"""


def _to_hex(css):
    m = re.match(r"rgba?\(([^)]+)\)", css or "")
    if not m:
        return None, 1.0
    p = [float(x) for x in re.split(r"[,\s/]+", m.group(1)) if x]
    if len(p) < 3:
        return None, 1.0
    a = p[3] if len(p) > 3 else 1.0
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in p[:3]), a


def check_hover(page, rep, preset, rows, limit=12, viewport_h=900):
    by_i = {r["i"]: r for r in rows}

    def in_tbody(r):
        p = by_i.get(r["par"])
        return bool(p and p["tag"] == "tbody")

    visible = lambda r: 0 <= r["y"] and r["y"] + min(r["h"], 24) < viewport_h - 8
    cands = [r for r in rows if r["inter"] and r["w"] >= 24 and r["h"] >= 20 and visible(r)]
    cands += [r for r in rows if r["tag"] == "tr" and r["h"] >= 20 and in_tbody(r) and visible(r)][:3]
    seen, picked = set(), []
    for r in cands:
        key = (r["tag"], round(r["h"]), r["col"], r["bg"])
        if key in seen:
            continue
        seen.add(key)
        picked.append(r)
        if len(picked) >= limit:
            break
    no_change, too_small, too_big, covered = [], [], [], []
    lo, hi = preset["hover_delta_L"]
    if rep.context.get("scheme") == "dark":
        hi = max(hi, 0.12)   # в тёмной теме шаг между поверхностями больше (09-design-tokens/03 §3.5)
    for r in picked:
        before = page.evaluate(HOVER_READ_JS, r["i"])
        try:
            page.mouse.move(r["x"] + r["w"] / 2, r["y"] + min(r["h"] / 2, 12))
            page.wait_for_timeout(120)
        except Exception:
            continue
        after = page.evaluate(HOVER_READ_JS, r["i"])
        if not before or not after:
            continue
        label = f"{r['sel']} «{(r['txt'] or '')[:20]}»"
        if not after.get("hit"):
            covered.append(label)     # элемент перекрыт оверлеем: hover до него не доходит
            continue
        same = all(before[k] == after[k] for k in ("bg", "col", "bc", "sh", "tr", "ol"))
        if same:
            no_change.append(label)
            continue
        b, ba = _to_hex(before["bg"]); a, aa = _to_hex(after["bg"])
        if b and a and aa > 0.05 and ba > 0.05:
            dl = abs((okl(a) or 0) - (okl(b) or 0))
            if dl and dl < lo:
                too_small.append(f"{label}: ΔL {dl*100:.1f} п.п.")
            elif dl > hi:
                too_big.append(f"{label}: ΔL {dl*100:.1f} п.п.")
        if after["tr"] and after["tr"] != "none" and "matrix" in after["tr"]:
            nums = [float(x) for x in re.findall(r"-?\d+\.?\d*", after["tr"])]
            if nums and abs(nums[0] - 1) > 0.005:
                too_big.append(f"{label}: hover меняет масштаб ({nums[0]:.3f})")
    page.mouse.move(0, 0)
    rep.add("S1", "Состояния", f"У интерактивных элементов есть hover (проверено {len(picked) - len(covered)})",
            len(no_change), "0", not no_change, SEV_SERIOUS, no_change)
    if covered:
        rep.add("S3", "Состояния", "Элементы под оверлеем (hover не проверялся)", len(covered),
                "информативно", None, SEV_POLISH, covered)
    rep.add("S2", "Состояния", f"ΔL hover в коридоре {lo*100:.0f}–{hi*100:.0f} п.п. светлоты",
            len(too_small) + len(too_big), "0", not (too_small or too_big), SEV_POLISH,
            too_small + too_big)


def check_reduced(page_rows_normal, page_rows_reduced, rep):
    def sig(rows):
        d = []
        for r in rows:
            d.extend([x for x in parse_durations(r["td"]) if x > 0])
        anims = {r["an"] for r in rows if r["an"] and r["an"] != "none"}
        transforms = {r["sel"] for r in rows if r.get("tp") and "transform" in r["tp"]}
        return d, anims, transforms
    d0, a0, t0 = sig(page_rows_normal)
    d1, a1, t1 = sig(page_rows_reduced)
    max0 = max(d0) if d0 else 0
    max1 = max(d1) if d1 else 0
    rep.add("M1", "Сокращённое движение", "Длительности сокращаются при prefers-reduced-motion",
            f"{max0:.0f} ms → {max1:.0f} ms", "меньше или равно, и не 0",
            (max1 <= max0) and not (max0 > 0 and max1 == 0), SEV_SERIOUS,
            note="«reduce, not remove»: обнуление ломает компоненты, ждущие transitionend")
    still = sorted(a1 - {"none"})
    rep.add("M2", "Сокращённое движение", "Циклические анимации выключены", len(still),
            "0 (кроме спиннера, если он единственный сигнал загрузки)", not still, SEV_POLISH,
            [", ".join(still[:6])])


# =====================================================================================
# 7. Отчёт
# =====================================================================================

GROUP_ORDER = ["Отступы", "Размеры", "Форма", "Глубина", "Слои", "Цели", "Фокус", "Типографика",
               "Цвет", "Раскладка", "Движение", "Сокращённое движение", "Состояния", "Антислоп"]


def merge_reports(reports):
    out = []
    for rep in reports:
        tag = f"{rep.context.get('scheme','light')}/{rep.context.get('viewport','')}"
        for f in rep.findings:
            g = dict(f)
            g["run"] = tag
            out.append(g)
    return out


def render_md(target, preset, findings, runs, tokens_note=""):
    fails = [f for f in findings if f["verdict"] == "FAIL"]
    by_sev = Counter(f["severity"] for f in fails)
    lines = []
    lines.append(f"# Визуальный QA: {os.path.basename(target)}")
    lines.append("")
    lines.append(f"Инструмент: `scripts/ui/ui_audit.py`. Пресет: **{preset['name']}** ({preset['title']}).")
    if tokens_note:
        lines.append(f"Шкалы и значения: {tokens_note}.")
    lines.append(f"Прогоны: {', '.join(runs)}.")
    lines.append("")
    total = len(findings)
    okc = len([f for f in findings if f["verdict"] == "OK"])
    warnc = len([f for f in findings if f["verdict"] == "WARN"])
    lines.append(f"**Итог: {okc} OK, {len(fails)} FAIL, {warnc} информативных из {total} проверок.** "
                 f"Блокеров {by_sev.get(SEV_BLOCKER,0)}, серьёзных {by_sev.get(SEV_SERIOUS,0)}, "
                 f"полировки {by_sev.get(SEV_POLISH,0)}.")
    lines.append("")
    groups = defaultdict(list)
    for f in findings:
        groups[f["group"]].append(f)
    for g in GROUP_ORDER:
        if g not in groups:
            continue
        lines.append(f"## {g}")
        lines.append("")
        lines.append("| # | Правило | Найдено | Порог | Вердикт | Серьёзность | Прогон |")
        lines.append("|---|---|---|---|---|---|---|")
        for f in groups[g]:
            lines.append(f"| {f['id']} | {f['rule']} | {f['found']} | {f['threshold']} | "
                         f"{f['verdict']} | {f['severity']} | {f['run']} |")
        lines.append("")
        det = [f for f in groups[g] if f["examples"] and any(f["examples"]) and f["verdict"] != "OK"]
        if det:
            for f in det:
                ex = [e for e in f["examples"] if e]
                if not ex:
                    continue
                lines.append(f"- **{f['id']}** {f['rule']} ({f['run']}):")
                for e in ex:
                    lines.append(f"  - `{e}`")
                if f["note"]:
                    lines.append(f"  - примечание: {f['note']}")
            lines.append("")
    tells = tells_summary(findings)
    if tells:
        lines.append("## Приметы дефолтного вида")
        lines.append("")
        lines.append("Одна строка на примету реестра `kb/common/tells.yaml`, сколько бы проверок и прогонов её ни нашли.")
        lines.append("")
        lines.append("| Примета | Проверки | Прогоны |")
        lines.append("|---|---|---|")
        for t, e in tells.items():
            lines.append(f"| {t} | {', '.join(e['checks'])} | {', '.join(e['runs'])} |")
        lines.append("")
    if fails:
        lines.append("## Что править в первую очередь")
        lines.append("")
        for sev in (SEV_BLOCKER, SEV_SERIOUS, SEV_POLISH):
            part = [f for f in fails if f["severity"] == sev]
            if not part:
                continue
            lines.append(f"**{sev}:**")
            for f in part:
                lines.append(f"- {f['id']} — {f['rule']}: найдено {f['found']}, порог {f['threshold']} ({f['run']}).")
            lines.append("")
    return "\n".join(lines)


# =====================================================================================
# 8. Прогон
# =====================================================================================

def to_url(target):
    if re.match(r"^https?://", target) or target.startswith("file://"):
        return target
    return "file://" + os.path.abspath(target)


def resolve_tokens(opts):
    """Токены прогона → (множества значений или None, строка для отчёта). Ключ --tokens — токены ДС проекта; без него
    у пресета с эталоном (admin) — эталонные токены ui, у прочих (consumer, профиль marketing) — шкалы пресета."""
    if getattr(opts, "tokens", None):
        return load_tokens(opts.tokens), f"токены ДС проекта `{opts.tokens}`"
    if preset_of(opts.preset)[0].get("reference_tokens"):
        return load_tokens(REFERENCE_TOKENS), ("эталонные токены ui `kb/ui/14-recipes/examples/tokens.css` "
                                               "(токены ДС проекта не переданы)")
    return None, f"шкалы пресета {opts.preset} (токены ДС проекта не переданы, эталонных токенов у пресета нет)"


def run_plan(opts, first_bp):
    """Прогоны: окна, схема, движение, тач. Ширины — из kb/common/acceptance-widths.yaml, если окно не задано ключом."""
    aw = load_widths()
    height = lambda w: VIEW_H_WIDE if w >= first_bp else VIEW_H_NARROW  # noqa: E731
    if opts.viewports:
        vps = opts.viewports
    elif opts.acceptance:
        vps = [(w, height(w)) for w in aw["widths"]]
    else:
        vps = [(aw["widths"][0], height(aw["widths"][0]))]
    schemes = ["light", "dark"] if opts.scheme == "both" else [opts.scheme]
    base_scheme = opts.scheme if opts.scheme != "both" else "light"
    combos = [(vp, scheme, "no-preference", False) for vp in vps for scheme in schemes]
    if opts.reduced_motion:
        combos.append((vps[0], base_scheme, "reduce", False))
    if opts.touch:
        phone = [w for w in aw["widths"] if w < first_bp] or [min(aw["widths"])]
        combos.append(((max(phone), VIEW_H_NARROW), base_scheme, "no-preference", True))
    overflow = (aw["overflow_only"], VIEW_H_NARROW) if opts.acceptance and aw.get("overflow_only") else None
    return combos, overflow


def audit(target, opts):
    from playwright.sync_api import sync_playwright

    ts, tokens_note = resolve_tokens(opts)
    opts.tokens_set = ts
    base, profile = preset_of(opts.preset)
    preset = tokens_to_preset(base, ts) if ts else base
    first_bp = first_breakpoint(ts)
    combos, overflow = run_plan(opts, first_bp)

    url = to_url(target)
    reports, runs, normal_rows, reduced_rows = [], [], None, None

    with kbpaths.lock("browser"), sync_playwright() as pw:
        browser = pw.chromium.launch(args=["--force-color-profile=srgb", "--disable-lcd-text"])
        if overflow:
            # на ширине overflow_only — только горизонтальный вылет (WCAG 1.4.10)
            w, h = overflow
            context = browser.new_context(viewport={"width": w, "height": h}, color_scheme="light")
            page = context.new_page()
            page.goto(url, wait_until="load", timeout=opts.timeout)
            page.wait_for_timeout(opts.wait)
            sw = page.evaluate("() => document.documentElement.scrollWidth")
            rep = Report(target, preset["name"], {"scheme": "light", "viewport": f"{w}x{h}/overflow"})
            rep.add("J5", "Раскладка", "Нет горизонтальной прокрутки документа", f"{sw} vs {w}",
                    "scrollWidth ≤ innerWidth", sw <= w + 1, SEV_BLOCKER)
            reports.append(rep)
            runs.append(f"light/{w}x{h}/overflow")
            context.close()

        for (w, h), scheme, motion, touch in combos:
            ctx_kwargs = dict(viewport={"width": w, "height": h}, color_scheme=scheme,
                              reduced_motion=motion, device_scale_factor=2 if touch else 1,
                              has_touch=touch, is_mobile=touch)
            context = browser.new_context(**ctx_kwargs)
            page = context.new_page()
            page.goto(url, wait_until="load", timeout=opts.timeout)
            page.wait_for_timeout(opts.wait)
            data = page.evaluate(COLLECT_JS, {"maxElements": opts.max_elements})
            tag = f"{scheme}/{w}x{h}" + ("/reduced" if motion == "reduce" else "") + ("/touch" if touch else "")
            ctx = {"target": target, "scheme": scheme, "viewport": f"{w}x{h}",
                   "motion": motion, "touch": touch, "first_bp": first_bp}
            if motion == "reduce":
                reduced_rows = data["rows"]
            elif normal_rows is None and scheme == "light":
                normal_rows = data["rows"]
            rep = run_checks(data, preset, opts, ctx)
            if profile:
                apply_profile_alone(rep, profile)
            rep.context["viewport"] = f"{w}x{h}" + ("/reduced" if motion == "reduce" else "") + ("/touch" if touch else "")
            if opts.tab and not touch and motion != "reduce":
                check_focus(page, rep, preset, opts.tab)
            if opts.hover and not touch and motion != "reduce":
                check_hover(page, rep, preset, data["rows"], viewport_h=h)
            reports.append(rep)
            runs.append(tag)
            if opts.screenshot:
                os.makedirs(opts.out, exist_ok=True)
                page.screenshot(path=os.path.join(
                    opts.out, f"{opts.name}_{scheme}_{w}x{h}.png"), full_page=True)
            context.close()
        browser.close()

    if normal_rows and reduced_rows:
        extra = Report(target, preset["name"], {"scheme": "light", "viewport": "reduced"})
        check_reduced(normal_rows, reduced_rows, extra)
        reports.append(extra)

    findings = merge_reports(reports)
    md = render_md(target, preset, findings, runs, tokens_note)
    data = report_data(target, preset["name"], tokens_note, runs, findings)
    os.makedirs(opts.out, exist_ok=True)
    md_path = os.path.join(opts.out, opts.name + ".md")
    js_path = os.path.join(opts.out, opts.name + ".json")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(js_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return md, md_path, js_path, findings, data


def report_data(target, preset_name, tokens_note, runs, findings):
    """JSON отчёта (файл <out>/<name>.json и stdout с --json): какая утилита ответила и версия контракта скилла
    (`tool`, `skill_version`), цель, пресет, шкалы, прогоны, находки и приметы."""
    return {"tool": "ui_audit.py", "skill_version": kbpaths.skill_version(), "target": target, "preset": preset_name,
            "tokens": tokens_note, "runs": runs, "findings": findings, "tells": tells_summary(findings)}


# =====================================================================================
# 9. Самопроверка без браузера
# =====================================================================================

def slop_params(ts, preset_name="admin"):
    """Параметры скрипта маркеров ui/11-styles-trends/04-anti-slop-ui.md §3: порог кеглей — из данных, доля шкалы и цель
    нажатия — из пресета, шкала отступов и цвета — из токенов (ДС проекта или эталона)."""
    base = preset_of(preset_name)[0]
    preset = tokens_to_preset(base, ts) if ts else base
    return {"fontSizesTellAbove": TH["font_sizes"]["tell_above"],
            "spaceScale": [v for v in preset["spacing"] if v],
            "spaceInScaleMin": preset["spacing_in_scale_min"],
            "targetMin": preset["target_min"],
            "colors": list(ts["colors"]) if ts else []}


def _row(i, **kw):
    """Строка COLLECT_JS для синтетики самопроверки."""
    base = dict(i=i, tag="div", sel=f"div.n{i}", role="", x=0, y=0, w=200, h=40, pt=None, pr=None, pb=None, pl=None,
                mt=None, mr=None, mb=None, ml=None, rg=None, cg=None, r1=None, r2=None, r3=None, r4=None, bw=None,
                bwr=None, bwb=None, bwl=None, sh=None, z=None, bd=None, fs=14, lh=20, fw=400, ls=0, ff="Inter",
                fvn="normal", tt="none", ta="start", col="#0f172b", cola=1, bg="#ffffff", bggrad=False, bgguess=False,
                bcol=None, bcola=0, ow=0, ost="none", oc=None, pos="static", ov="visible visible", mw=None, gtc=None,
                tp="all", td="0s", an="none", txt="", inter=False, disp="block", dis=False, inflow=False, par=None,
                svg=None, inline="", hid=False, hw=None, hh=None, tlen=None, tl=None, ai="normal", as_="auto", fd="row",
                bgi=None, bgclip=False, onmedia=None, bdmedia=None)
    base["as"] = base.pop("as_")
    base.update(kw)
    return base


def _run(rows, preset, touch=False, text="", ts=None, w=1440, h=900):
    data = {"rows": rows, "meta": {"lang": "ru", "scrollW": w, "innerW": w, "innerH": h,
                                   "bodyBg": "rgb(255, 255, 255)", "title": "t", "text": text, "viewportMeta": "",
                                   "styleSheets": 1}}
    opts = argparse.Namespace(strict_border=False, tokens_set=ts)
    ctx = {"target": "synthetic", "scheme": "light", "viewport": f"{w}x{h}", "motion": "no-preference",
           "touch": touch, "first_bp": 640}
    return {f["id"]: f for f in run_checks(data, preset, opts, ctx).findings}


def selftest(browser=False):
    global TELL_OF
    ok = True

    def check(name, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'OK  ' if good else 'FAIL'} {name}: {got!r} (ожидалось {want!r})")

    check("parse_shadows: два слоя",
          len(parse_shadows("rgba(0,0,0,.06) 0px 1px 2px 0px, rgba(0,0,0,.08) 0px 4px 8px -2px")), 2)
    check("parse_shadows: inset", parse_shadows("inset 0 0 0 1px rgb(0 0 0 / .06)")[0][4], True)
    check("parse_shadows: свечение", parse_shadows("rgb(37 99 235) 0px 0px 20px 0px")[0][:3], (0.0, 0.0, 20.0))
    check("parse_durations", parse_durations("150ms, 0.3s"), [150.0, 300.0])
    check("in_scale 12 в шкале", in_scale(12, [0, 4, 8, 12, 16]), True)
    check("in_scale 13 вне шкалы", in_scale(13, [0, 4, 8, 12, 16]), False)
    check("is_fraction 19.6", is_fraction(19.6), True)
    check("is_fraction 20", is_fraction(20.0), False)
    check("gap_between соседей",
          round(gap_between({"x": 0, "y": 0, "w": 10, "h": 10}, {"x": 12, "y": 0, "w": 10, "h": 10}), 1), 2.0)
    check("wcag #767676 на белом", round(wcag("#767676", "#ffffff"), 2), 4.54)
    check("apca #fff на #000", round(apca("#ffffff", "#000000"), 1), -107.9)
    check("EMOJI_RE находит", bool(EMOJI_RE.search("Готово ✅")), True)
    check("EN_NUMBER_RE находит", bool(EN_NUMBER_RE.search("1,234")), True)
    check("PERCENT_GLUED_RE находит", bool(PERCENT_GLUED_RE.search("12%")), True)

    # эмодзи: «©» и «↔» — знаки текста, с селектором вида тоже; эмодзи с селектором считается один раз
    check("эмодзи: «©», «↔», «©️», «↔️» не считаются", EMOJI_RE.findall("© 2026 · A ↔ B · ©️ ↔️"), [])
    check("эмодзи: 🚀 и ✅️ — два", len(EMOJI_RE.findall("Старт 🚀 готово ✅️")), 2)

    # данные: пороги, ширины приёмки, токены
    check("порог кеглей из данных", (TH["font_sizes"]["norm"], PRESET_ADMIN["unique_font_sizes_max"]), ([6, 8], 8))
    aw = load_widths()
    check("ширины приёмки из файла", (aw["widths"][0], aw["overflow_only"], len(aw["widths"]) >= 2), (1440, 320, True))
    ref = reference_tokens()
    check("эталонные токены: шкала space.* с режимами плотности",
          all(v in ref["spacing"] for v in (2, 4, 6, 8, 10, 12, 16, 24)) and 13 not in ref["spacing"], True)
    check("эталонные токены: кегли, длительности, цвет, брейкпоинты",
          (ref["font_sizes"][:2], 150.0 in ref["durations"], "#155dfc" in ref["colors"], ref["breakpoints"][0]),
          ([11.0, 12.0], True, True, 640.0))
    plan, overflow = run_plan(argparse.Namespace(viewports=[], acceptance=False, scheme="light", reduced_motion=False,
                                                 touch=True), 640)
    check("прогон по умолчанию — первая ширина приёмки, тач — самая широкая уже брейкпоинта",
          [(c[0], c[3]) for c in plan], [((aw["widths"][0], VIEW_H_WIDE), False), ((390, VIEW_H_NARROW), True)])
    plan, overflow = run_plan(argparse.Namespace(viewports=[], acceptance=True, scheme="light", reduced_motion=False,
                                                 touch=False), 640)
    check("--acceptance: все ширины и вылет на overflow_only", ([c[0][0] for c in plan], overflow[0]),
          (aw["widths"], aw["overflow_only"]))
    import tempfile
    with tempfile.TemporaryDirectory(prefix="ui-audit-") as tmp:
        dtcg = os.path.join(tmp, "system.tokens.json")
        with open(dtcg, "w", encoding="utf-8") as f:
            json.dump({"space": {"$type": "dimension", "sm": {"$value": {"value": 12, "unit": "px"}}},
                       "primitive": {"size": {"13": {"$type": "dimension", "$value": {"value": 13, "unit": "px"}}}},
                       "breakpoint": {"$type": "dimension", "tablet": {"$value": {"value": 48, "unit": "rem"}}}}, f)
        td = load_tokens(dtcg)
        check("DTCG: отступы — только space.*, брейкпоинт в px", (td["spacing"], td["breakpoints"]), ([12.0], [768.0]))
        css = os.path.join(tmp, "system.tokens.css")
        with open(css, "w", encoding="utf-8") as f:
            f.write(":root{--space-sm: 12px; --radius-md: 6px; --type-body-size: var(--font-size-16);"
                    " --font-size-16: 1rem; --color-fg: #111; --motion-fast: 120ms ease;}")
        tc = load_tokens(css)
        check("CSS: var(), rem, короткий hex, длительность в составном значении",
              (tc["spacing"], tc["radius"], tc["font_sizes"], tc["colors"], tc["durations"]),
              ([12.0], [6.0], [16.0], ["#111111"], [120.0]))
    before = dict(PRESET_ADMIN)
    tokens_to_preset(PRESET_ADMIN, {**ref, "spacing": [3.0]})
    check("tokens_to_preset не меняет пресет", PRESET_ADMIN == before, True)
    A = tokens_to_preset(PRESET_ADMIN, ref)

    # скрытое вне I1 и H; текст над медиа — I1m «проверить F83»
    rows = [_row(0, tag="span", txt="Пропустить к содержимому", col="#bbbbbb", fs=11, hid=True, w=1, h=1),
            _row(1, tag="h1", txt="Заголовок над видео", col="#ffffff", fs=32, lh=40, onmedia="video"),
            _row(2, tag="p", txt="Обычный текст", col="#0f172b")]
    f = _run(rows, A, ts=ref)
    check("скрытое: вне I1, текст над видео: вне I1", (f["I1"]["verdict"], f["I1m"]["verdict"], f["I1m"]["found"]),
          ("OK", "WARN", 1))
    check("скрытое вне H: кегли считаются без него", f["H1"]["found"], 2)

    # цели: зона нажатия и тач 44
    rows = [_row(0, tag="button", inter=True, w=32, h=32, txt="Ок"),
            _row(1, tag="button", inter=True, x=100, w=32, h=32, txt="Да", hw=44, hh=44, pos="relative")]
    f = _run(rows, A, touch=True)
    check("F3 на таче: 32 без зоны — находка, 32 с ::before 44 — нет", (f["F3"]["verdict"], f["F3"]["found"]), ("FAIL", 1))
    check("F3 только на тач-прогоне", "F3" in _run(rows, A), False)

    # длина строки в знаках — самая длинная строка абзаца по раскладке браузера (`tl`); высота — как у этих строк:
    # оценка по высоте (знаков / (строк − 0,5)) дала бы первым двум ≈86 и ≈83, узкому — ≈81
    def para(i, tl, w=592, **kw):
        return _row(i, tag="p", txt="x" * 120, tlen=sum(tl) + len(tl) - 1, tl=tl, fs=16, lh=24, h=24 * len(tl), w=w,
                    **kw)
    f = _run([para(0, [58, 70]), para(1, [66, 69, 70])], A)
    check("H8: 2 и 3 строки по 58–70 знаков с полной последней — в норме 75", f["H8"]["verdict"], "OK")
    f = _run([para(0, [58, 70]), para(1, [110, 108, 31], w=1060), para(2, [75, 60]), para(3, [60, 76]),
              para(4, [130], w=1300)], A)
    check("H8: строки ≈110 знаков, строка 76 и абзац в одну строку 130 — находки с длиной самой длинной строки; "
          "75 — норма", (f["H8"]["verdict"], f["H8"]["found"],
                         [e.split(" — ")[1].split(" ")[0] for e in f["H8"]["examples"]]),
          ("FAIL", 3, ["110", "76", "130"]))
    f = _run([para(0, [58, 62], w=360)], A, w=390, h=844)
    check("H8 в узком окне — порог 60: самая длинная строка 62 (последняя) — находка", f["H8"]["verdict"], "FAIL")
    f = _run([para(0, [58, 60, 9], w=360)], A, w=390, h=844)
    check("H8 в узком окне: строки до 60 знаков — в норме", f["H8"]["verdict"], "OK")
    short = _row(0, tag="p", txt="x" * 100, tlen=100, tl=[100], fs=16, lh=24, h=24, w=900)
    quote = _row(1, tag="blockquote", txt="", tlen=300, tl=[], fs=16, lh=24, h=120, w=900)
    check("H8: абзац до 120 знаков и цитата без своих строк (строки — у вложенного абзаца) не судятся",
          _run([short, quote], A)["H8"]["verdict"], "OK")

    # шкала отступов и значения — из токенов; потолок длительностей пресета
    f = _run([_row(0, pt=13, pb=13, pl=16, pr=16), _row(1, pt=10, pb=6)], A, ts=ref)
    check("A1: 13 вне шкалы space.*, 6 и 10 — шаги режимов", (f["A1"]["verdict"], "13" in f["A1"]["examples"][0]),
          ("FAIL", True))
    f = _run([_row(0, pt=10, pb=30)], A)
    check("A2 без токенов: 10 и 30 — «шкала десятками»", (f["A2"]["verdict"], f["A2"]["found"]), ("FAIL", 2))
    f = _run([_row(0, pt=10, pb=30)], A, ts=ref)
    check("A2 с токенами: 10 со шкалы space.* — не находка, 30 вне шкалы — находка",
          (f["A2"]["verdict"], f["A2"]["found"], f["A2"]["examples"]), ("FAIL", 1, ["30"]))
    f = _run([_row(0, pt=10, pb=10)], A, ts={**ref, "spacing": [4.0, 8.0, 10.0]})
    check("A2: значение шкалы токенов ДС (--tokens) — OK", f["A2"]["verdict"], "OK")
    A250 = dict(A, durations=sorted(set(A["durations"]) | {250}))   # шкала ДС с токеном подложки
    f = _run([_row(0, td="0.15s"), _row(1, td="0.25s")], A250, ts=ref)
    check("K2: 250 мс у A — исключение подложки (WARN)", f["K2"]["verdict"], "WARN")
    f = _run([_row(0, td="0.3s")], A, ts=ref)
    check("K2: 300 мс у A длиннее потолка 200", f["K2"]["verdict"], "FAIL")
    f = _run([_row(0, td="0.3s")], tokens_to_preset(PRESET_CONSUMER, ref), ts=ref)
    check("K2: 300 мс у B в пределах потолка 400", f["K2"]["verdict"], "OK")
    f = _run([_row(0, tag="p", txt="Текст", col="#0b0b0b"), _row(1, tag="p", txt="Ещё", col="#0f172b")], A, ts=ref)
    check("I6 и I10: литерал #0b0b0b вне токенов ДС", (f["I6"]["found"], f["I10"]["found"]), (1, 1))

    # выравнивание соседних карточек (правило стопки .card + .card в сетке)
    grid = _row(0, disp="grid", w=1000, h=140, gtc="240px 240px 240px")
    cards = [_row(1, par=0, x=0, y=100, h=104), _row(2, par=0, x=256, y=116, h=88), _row(3, par=0, x=512, y=116, h=88)]
    f = _run([grid] + cards, A)
    check("J9: сдвиг соседа в ряду сетки на 16 px", (f["J9"]["verdict"], "сдвиг 16 px" in f["J9"]["examples"][0]),
          ("FAIL", True))
    f = _run([grid] + [dict(c, y=100, h=104) for c in cards], A)
    check("J9: ровный ряд", f["J9"]["verdict"], "OK")
    f = _run([dict(grid, disp="flex", ai="center")] + cards, A)
    check("J9: flex с align-items: center — не проверяется", f["J9"]["verdict"], "OK")

    # id приметы из tells.yaml#checks и сводка без повторов
    real = load_tells()
    TELL_OF = {"L1": "emoji-sparkle-ai", "H10": "caps-share"}
    try:
        f1 = run_checks({"rows": [_row(0, tag="span", txt="ЗАГОЛОВОК", tt="uppercase")],
                         "meta": {"lang": "ru", "scrollW": 1440, "innerW": 1440, "innerH": 900, "bodyBg": "",
                                  "title": "t", "text": "Готово ✅", "viewportMeta": "", "styleSheets": 1}},
                        A, argparse.Namespace(strict_border=False, tokens_set=None),
                        {"target": "s", "scheme": "light", "viewport": "1440x900", "first_bp": 640})
        f2 = Report("s", "admin", {"scheme": "dark", "viewport": "1440x900"})
        f2.findings = [dict(x) for x in f1.findings]
        f2.context["scheme"] = "dark"
        merged = merge_reports([f1, f2])
        by = {x["id"]: x for x in f1.findings}
        check("находка несёт id приметы", (by["L1"]["tell"], by["H10"]["tell"], by["A1"]["tell"]),
              ("emoji-sparkle-ai", "caps-share", None))
        s = tells_summary(merged)
        check("сводка примет: одна строка на примету, прогоны вместе",
              (sorted(s), s["emoji-sparkle-ai"]["runs"]), (["caps-share", "emoji-sparkle-ai"],
                                                            ["light/1440x900", "dark/1440x900"]))
    finally:
        TELL_OF = None
    check("реестр примет читается (ключей ui_audit: — по данным)", isinstance(real, dict), True)
    print(f"     ключей {TELL_KEY}<id> в tells.yaml#checks: {len(real)}")

    # профиль marketing — данными; E1, E2 — полировка только в профиле; D3 — лимиты glass-panel; L4 — узкий
    M, table = load_profile("marketing")
    check("профиль: пресет и таблица из data/marketing-profile.yaml",
          (M["name"], M["glass_max"], M["glass_view_max"], M["glass_view_max_media"], M["glass_blur_max"],
           table["E1"]["severity"]), ("marketing", 6, 2, 1, 24, SEV_POLISH))
    z_rows = [_row(0, tag="canvas", z=-1, w=1440, h=900), _row(1, z=9999, w=40, h=40)]
    fc = _run(z_rows, PRESET_CONSUMER)
    rm = Report("synthetic", "marketing", {"scheme": "light", "viewport": "1440x900"})
    rm.findings = [dict(x) for x in _run(z_rows, M).values()]
    apply_profile(rm, table)
    fm = {x["id"]: x for x in rm.findings}
    check("E1: consumer — серьёзно, marketing — полировка", (fc["E1"]["severity"], fm["E1"]["severity"]),
          (SEV_SERIOUS, SEV_POLISH))
    check("E2: consumer — серьёзно, marketing — полировка", (fc["E2"]["severity"], fm["E2"]["severity"]),
          (SEV_SERIOUS, SEV_POLISH))
    glass3 = [_row(i, bd="blur(12px)", y=100 * i, w=300, h=80) for i in range(3)]
    check("D3 consumer: 3 стекла > 2", _run(glass3, PRESET_CONSUMER)["D3"]["verdict"], "FAIL")
    check("D3 marketing: 3 в первом экране > 2 (glass-panel)", _run(glass3, M)["D3"]["verdict"], "FAIL")
    glass2 = [dict(g, y=100 * i + (1000 if i else 0)) for i, g in enumerate(glass3)]
    check("D3 marketing: 1 в первом экране, 3 на странице — норма", _run(glass2, M)["D3"]["verdict"], "OK")
    glow = [_row(0, tag="button", sh="rgb(43, 59, 255) 0px 0px 24px 0px"),
            _row(1, tag="button", sh="rgb(43, 59, 255) 0px 0px 24px 0px")]
    check("D4 marketing: два свечения > одной кнопки", _run(glow, M)["D4"]["verdict"], "FAIL")
    hero = [_row(0, y=0, w=1440, h=600, bgi="linear-gradient(135deg, rgb(99, 102, 241) 0%, rgb(139, 92, 246) 100%)"),
            _row(1, y=0, w=1440, h=600, bgi="linear-gradient(rgb(240, 200, 120), rgb(250, 240, 220))")]
    f = _run(hero, M)
    check("L4 marketing: фиолетовый hero — примета, тёплый градиент — приём", (f["L4"]["verdict"], f["L4"]["found"]),
          ("WARN", 1))
    f = _run([_row(0, tag="h1", txt="Скорость", bgi="linear-gradient(red, blue)", bgclip=True)], M)
    check("L4 marketing: градиентный текст", f["L4"]["found"], 1)
    check("L4 consumer: крупные градиенты — информативно", _run(hero, PRESET_CONSUMER)["L4"]["threshold"],
          "информативно")

    # пресет по умолчанию — по поверхности: страница сайта — профиль marketing, экран приложения — admin
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        for surf, route in (("promo", "landing"), ("office", "app")):
            os.makedirs(os.path.join(td, "design", surf, "canvas", "html"))
            os.makedirs(os.path.join(td, "design", surf, "input"))
            with open(os.path.join(td, "design", surf, "input", "INPUT.md"), "w", encoding="utf-8") as fh:
                fh.write(f"---\nstage: mockup\nroute: {route}\n---\n# Вход холста\n")
            with open(os.path.join(td, "design", surf, "canvas", "html", "Main.html"), "w", encoding="utf-8") as fh:
                fh.write("<p>т</p>")
        copy = lambda s: os.path.join(td, "design", s, "canvas", "html", "Main.html")  # noqa: E731
        check("пресет без ключа: копия поверхности сайта — marketing, кабинета — admin, цель без манифеста — admin; "
              "ключ --surface page — marketing",
              (default_preset(copy("promo")), default_preset(copy("office")), default_preset("https://example.test/"),
               default_preset("https://example.test/", "page"), default_preset(copy("promo"), "app")),
              ("marketing", "admin", "admin", "marketing", "admin"))
    pm, tm = preset_of("marketing")
    check("пресет marketing — профиль данными с таблицей; admin — пресет кода без таблицы",
          (pm["name"], bool(tm), preset_of("admin")[0]["name"], preset_of("admin")[1]),
          ("marketing", True, "admin", None))
    section = [_row(0, pt=96, pb=96, w=1440, h=600), _row(1, pt=160, pb=160, w=1440, h=600)]
    check("отступы секций 96 и 160: у экрана приложения — вне шкалы (A1), у страницы сайта — в шкале профиля",
          (_run(section, PRESET_ADMIN)["A1"]["verdict"], _run(section, M)["A1"]["verdict"]), ("FAIL", "OK"))
    dur = [_row(0, tp="opacity", td="0.56s"), _row(1, tp="transform", td="0.9s")]
    check("K2 читает шкалу длительностей профиля (preset.durations): 560 и 900 мс — в шкале marketing, вне шкалы "
          "consumer",
          (_run(dur, M)["K2"]["verdict"], _run(dur, PRESET_CONSUMER)["K2"]["verdict"]), ("OK", "FAIL"))
    ra = Report("synthetic", "marketing", {"scheme": "light", "viewport": "1440x900"})
    ra.findings = [dict(x) for x in _run([_row(i, tag="button", h=hh, inter=True) for i, hh in
                                          enumerate((30, 34, 38, 42, 46, 50, 54))], M).values()]
    apply_profile_alone(ra, table)
    fa = {x["id"]: x for x in ra.findings}
    check("профиль в прогоне утилиты: проверка с пересчётом по узлам (B1) — серьёзность профиля и адрес пересчёта",
          (fa["B1"]["severity"], "marketing_audit.py" in str(fa["B1"]["threshold"]), fa["B1"]["profile"]),
          (SEV_POLISH, True, "recompute"))
    idle = [_row(0, tp="all", td="0s"), _row(1, tp="all", td="0s, 0s"), _row(2, tp="all", td="0.2s")]
    check("K1: `transition-property: all` без длительности — умолчание узла, не находка; с длительностью — находка",
          _run(idle, PRESET_ADMIN)["K1"]["found"], 1)

    # синтетика без новых полей (строки вызывающей утилиты) не ломает проверки
    bare = [{k: v for k, v in _row(0, tag="p", txt="x" * 120, w=900).items()
             if k not in ("hid", "hw", "hh", "tlen", "tl", "ai", "as", "fd", "bgi", "bgclip", "onmedia", "bdmedia")}]
    check("строки без новых полей: H8 — по ширине в px", _run(bare, PRESET_CONSUMER)["H8"]["verdict"], "FAIL")

    sp = slop_params(ref, "admin")
    check("параметры скрипта ui 11/04 §3", (sp["fontSizesTellAbove"], sp["spaceInScaleMin"], sp["targetMin"],
                                             6.0 in sp["spaceScale"], "#155dfc" in sp["colors"]), (9, 0.95, 24, True, True))
    rep = report_data("https://example.test/", "marketing", "шкалы пресета", [{"run": 1}],
                      [{"id": "J5", "verdict": "OK", "severity": "блокер", "run": 1}])
    check("JSON отчёта (файл и stdout с --json): tool, skill_version — версия скилла, находки",
          (rep["tool"], rep["skill_version"], [f["id"] for f in rep["findings"]], "tells" in rep),
          ("ui_audit.py", kbpaths.skill_version(), ["J5"], True))
    if browser:
        selftest_browser(check)
    print("\nпресеты:", ", ".join(PRESETS), "; профиль данными:", ", ".join(PROFILES))
    print("групп проверок:", len(GROUP_ORDER))
    return 0 if ok else 1


def selftest_browser(check):
    """Код страницы COLLECT_JS в Chromium на синтетической странице (текст вымышлен): строки абзацев H8. Моноширинный
    шрифт и колонка в `ch` задают раскладку заранее — жадное заполнение строки словами; перевод строки с отступом в
    разметке, ссылка, сдвинутые на 4 px слова и визуально скрытая подпись строк не меняют, висящий пробел `pre-wrap` у
    переноса не считается, у цитаты с абзацем внутри своих строк нет; эмодзи, флаг, семья через ZWJ и буква с
    комбинирующим знаком — по знаку; буквица, интерлиньяж 1 и перенос по мягкому дефису строки не склеивают."""
    from playwright.sync_api import sync_playwright

    words = ("lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt ut labore et "
             "dolore magna aliqua ut enim ad minim veniam quis nostrud exercitation ullamco laboris nisi ut aliquip ex "
             "ea commodo consequat duis aute irure dolor in reprehenderit in voluptate velit esse cillum").split()

    def lay(width):
        out, cur = [], ""
        for w in words:
            if cur and len(cur) + 1 + len(w) > width:
                out.append(len(cur))
                cur = w
            else:
                cur = f"{cur} {w}" if cur else w
        return out + [len(cur)]

    text = " ".join(words)
    head, link, up, tail = (" ".join(words[:7]), " ".join(words[7:12]), " ".join(words[12:15]),
                            " ".join(words[15:]))
    marks = ["flag", "\U0001F1F7\U0001F1FA", "family", "\U0001F468\u200D\U0001F469\u200D\U0001F467", "smile",
             "\U0001F600", "\u0438\u0306"]
    indented = text.replace(" dolor ", " dolor\n        ", 1)
    html = ("<!doctype html><html lang='en'><head><style>body { margin: 0; font: 16px/24px monospace; } "
            ".n { width: 40.5ch; } .w { width: 110.5ch; } .pw { white-space: pre-wrap; } "
            ".up { position: relative; top: -4px; } .sr { position: absolute; width: 1px; height: 1px; "
            "overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; } "
            ".dc::first-letter { float: left; font-size: 3.4em; line-height: 1; }</style></head><body>"
            f"<p id='a' class='n'>{indented}</p>"
            f"<p id='b' class='n'>{head} <a href='#b'>{link}</a><span class='sr'>hidden link caption</span> "
            f"<span class='up'>{up}</span> {tail}</p>"
            f"<p id='pw' class='n pw'>{text}</p>"
            f"<blockquote id='q' class='n'><p id='qp'>{text}</p></blockquote>"
            f"<p id='w' class='w'>{text}</p>"
            f"<p id='g' class='w'>{' '.join(marks)}</p>"
            f"<p id='dc' class='n dc'>{text}</p>"
            f"<p id='t' class='n' style='line-height: 1'>{text}</p>"
            f"<p id='sh' class='n'>{'x' * 30} {'\u00ad'.join(['ex', 'er', 'ci', 'ta', 'tion', 'al', 'ly'])} {text}</p>"
            "</body></html>")
    with kbpaths.lock("browser"), sync_playwright() as pw:
        chromium = pw.chromium.launch()
        page = chromium.new_page(viewport={"width": 1440, "height": 900})
        page.set_content(html)
        data = page.evaluate(COLLECT_JS, {"maxElements": 4000})
        chromium.close()
    tl = {r["sel"].split(".")[0]: r["tl"] for r in data["rows"] if r["tag"] in ("p", "blockquote")}
    check("браузер: строки абзаца в колонке 40ch — жадная раскладка слов", tl.get("p#a"), lay(40))
    check("браузер: ссылка, сдвинутые на 4 px слова и визуально скрытая подпись строк не меняют", tl.get("p#b"),
          lay(40))
    check("браузер: pre-wrap — висящий пробел у переноса не считается", tl.get("p#pw"), lay(40))
    check("браузер: у цитаты своих строк нет, строки — у вложенного абзаца", (tl.get("blockquote#q"), tl.get("p#qp")),
          ([], lay(40)))
    check("браузер: колонка 110ch — строки до 110 знаков", tl.get("p#w"), lay(110))
    check("браузер: эмодзи, флаг, семья через ZWJ и буква с комбинирующим знаком — по знаку", tl.get("p#g"),
          [sum(len(m) if m.isascii() else 1 for m in marks) + len(marks) - 1])
    check("браузер: интерлиньяж 1 — соседние строки перекрываются краем и не склеиваются", tl.get("p#t"), lay(40))
    sh = tl.get("p#sh") or [0]
    check("браузер: перенос по мягкому дефису строки не склеивает", (len(sh) > 2, max(sh) <= 40), (True, True))
    dc = tl.get("p#dc") or [0]
    check("браузер: буквица строки не склеивает — строка не длиннее колонки, каждый знак посчитан один раз",
          (max(dc) <= 40, sum(dc)), (True, len(text) - (len(dc) - 1)))
    f = _run(data["rows"], PRESET_ADMIN)
    check("браузер: H8 — находка только у колонки 110ch", (f["H8"]["found"], f["H8"]["examples"][0].split(" ")[0]),
          (1, "p#w.w"))


# =====================================================================================
# 10. CLI
# =====================================================================================

def main():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("target", nargs="?")
    p.add_argument("--preset", default=None, choices=list(PRESETS) + list(PROFILES))
    p.add_argument("--surface", default=None, choices=["page", "app"])
    p.add_argument("--tokens")
    p.add_argument("--viewport", action="append", default=[])
    p.add_argument("--scheme", default="light", choices=["light", "dark", "both"])
    p.add_argument("--reduced-motion", action="store_true")
    p.add_argument("--hover", action="store_true")
    p.add_argument("--tab", type=int, default=0)
    p.add_argument("--touch", action="store_true")
    p.add_argument("--out", default=DEFAULT_OUT)
    p.add_argument("--name")
    p.add_argument("--strict-border", action="store_true")
    p.add_argument("--max-elements", type=int, default=4000)
    p.add_argument("--wait", type=int, default=None)
    p.add_argument("--timeout", type=int, default=45000)
    p.add_argument("--screenshot", action="store_true")
    p.add_argument("--batch")
    p.add_argument("--acceptance", action="store_true")
    p.add_argument("--fail-on", default=None, choices=["blocker", "serious", "any"])
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--browser", action="store_true")
    p.add_argument("--slop-params", action="store_true")
    p.add_argument("-h", "--help", action="store_true")
    a = p.parse_args()

    if a.help or (not a.target and not a.batch and not a.selftest and not a.slop_params):
        print(__doc__)
        return 0
    if a.selftest:
        return selftest(browser=a.browser)
    if a.json and a.batch:
        print("--json — JSON одной цели в stdout, без --batch", file=sys.stderr)
        return 2
    given = a.preset
    a.preset = given or default_preset(None if a.batch else a.target, a.surface)
    if a.slop_params:
        ts, note = resolve_tokens(a)
        print(json.dumps(slop_params(ts, a.preset), ensure_ascii=False))
        print(f"шкалы и значения: {note}", file=sys.stderr)
        return 0

    a.viewports = []
    for v in a.viewport:
        w, h = v.lower().split("x")
        a.viewports.append((int(w), int(h)))
    if a.wait is None:
        a.wait = 2000 if (a.target and re.match(r"^https?://", a.target)) else 400

    targets = []
    if a.batch:
        with open(a.batch, encoding="utf-8") as f:
            targets = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    else:
        targets = [a.target]

    worst = None
    for t in targets:
        if a.batch and not given:
            a.preset = default_preset(t, a.surface)
        a.name = a.name if (a.name and len(targets) == 1) else \
            re.sub(r"[^A-Za-z0-9._-]+", "_", os.path.basename(t) or t)[:60]
        md, md_path, js_path, findings, data = audit(t, a)
        if a.json:
            print(json.dumps(data, ensure_ascii=False, indent=1))
        elif not a.quiet:
            print(md)
        print(f"\n→ {md_path}\n→ {js_path}", file=sys.stderr)
        fails = [f for f in findings if f["verdict"] == "FAIL"]
        if fails:
            sev = min(SEV_ORDER[f["severity"]] for f in fails)
            worst = sev if worst is None else min(worst, sev)

    if a.fail_on and worst is not None:
        limit = {"blocker": 0, "serious": 1, "any": 2}[a.fail_on]
        if worst <= limit:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
