#!/usr/bin/env python3
"""prompt_compile.py — компилятор промтов: спецификация ассета → промт в диалекте модели + параметры задания.

Спецификация — схема kb/ai-media/05-prompting/asset-spec.schema.json, диалекты семейств моделей —
kb/ai-media/05-prompting/dialects.yaml. Компилятор проверяет спецификацию и собирает промт в диалекте семейства: правки
и маски с полярностью модели, референсы с ролями, серии, продукт из 7 блоков, видео (i2v, первый и последний кадр,
мульти-шот, запреты движения, фоновое движение), бюджет длины, линты (кириллица в описании, слоп, слова качества,
сравнительные правки). Ценовые параметры ставятся явно, вход и цена проверяются той же библиотекой, что у polza.py
(`polza_catalog`: coerce_input, validate, estimate). Паспорт компиляции уходит в `meta.compile` задания, оттуда — в
паспорт генерации polza.py. Задания — JSONL для polza.py или список .routerai.json / .genapi.json для mp_client.py.

Команды:
  prompt_compile.py validate SPEC.json [--model ID] [--channel polza|routerai|genapi]
  prompt_compile.py compile  SPEC.json --model ID [--dialect D] [--channel C] [--opt k=v …] [--json]
  prompt_compile.py jobs     SPEC.json [SPEC …] --models ID[,ID …] [--out jobs.jsonl] [--channel C] [--opt k=v …]
                             [--dialects D[,D …]] [--repeats N] [--seeds S[,S …]] [--tag T] [--agent A] [--test ID]
                             [--meta '{json}'] [--no-provider] [--allow-missing-inputs]
  prompt_compile.py chain    SPEC.json --model ID           правка порциями (≤ edit.max_changes за вызов)
  prompt_compile.py ratios   SPEC.json                      варианты соотношений: генерация / кадр мастера / аутпейнт
  prompt_compile.py matrix   SPEC.json [SPEC …] [--models …] длины и ошибки по моделям и диалектам (таблица)

`jobs` без ключей формы — одно задание на спецификацию и модель: диалект семейства, один вариант, без seed, тега и
агента; его цену считает `polza.py estimate` по файлу заданий. Сравнение форм промта (A/B) — только явными ключами:
--dialects (несколько форм), --repeats и --seeds (повторы с сидами), --tag, --agent, --test.

Снимок каталога polza читают только команды, которым он нужен: compile, jobs, chain, matrix и validate с --model;
--help, ratios и validate без --model отвечают без снимка. Снимок — POLZA_CATALOG (имя папки или путь), иначе последний в
$DDD_HOME/cache/ai-media/polza/ (ставит `scripts/install.sh --catalogs`, обновляет `polza_catalog.py snapshot`).

Формат файла в задании канала routerai (output_format) — из варианта маршрута задачи для этой модели
(kb/ai-media/13-routing-matrix/routing.yaml), иначе из записи модели в dialects.yaml, иначе png; формат вне списка
каталога канала заменяется поддерживаемым (у векторных моделей — svg). Снимок каталога канала — ROUTERAI_CATALOG (имя
папки или путь), иначе последний в $DDD_HOME/cache/ai-media/routerai/ (`mp_client.py snapshot --channel routerai`); без
снимка формат решают маршрут и dialects.yaml.

Опции --opt (как поле compile спецификации): order=family|product7|shuffled|custom, length=full|short,
text_zone_style=base|vendor|google|openai|copyspace, negation=family|positive|sentence, palette_form=family|hex|names,
fit=fail|drop, language=en|ru, quality_words=true, enhancer=on|off, labels=global|family, refs=declare|silent,
anti_average=true, seed=101, shuffle_seed=7, i2v=motion_only|full, forbid_style=sentence|positive,
max_changes=10.

Вход проверяется до вызова модели. Спецификация, которая не проходит схему, даёт строки ошибок и код 1 — без
трассировки и у спецификации без обязательного поля (`edit.operation`). Картинки входа — референсы, исходник правки,
кадры — сверяются с минимальным размером модели (`min_input_px` записи модели в dialects.yaml): меньшая сторона ниже
минимума — ошибка. `output.resolution` у модели, в каталоге которой нет параметра разрешения, в задание не идёт —
предупреждение с именем модели.

Правка (`edit`): инструкция собирается из `changes`; у `extend` в неё идут и `changes` (что видно в новых областях), и
зона текста `composition.text_zone` — кадрирование нового кадра; цель `remove` пишется с одним артиклем. Запрет текста в
правке — «No added text.»: надписи исходника остаются. Фраза контекста структурного промта — из `role.page_class`.

Запуск — Python окружения скилла ($DDD_HOME/venv/bin/python, scripts/install.sh): PyYAML; jsonschema и Pillow —
необязательно (без jsonschema схема не проверяется — предупреждение; без Pillow маска не инвертируется — ошибка, размер
входа не сверяется — предупреждение). Сеть не используется. Код выхода: 0 — без ошибок; 1 — ошибки спецификации или
компиляции (validate, compile); 2 — ошибка одной строкой: файл спецификации не читается, компиляция невозможна (модель вне
dialects.yaml, правка без `edit.operation` и т. п.) или нет снимка каталога.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import re
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("нужен PyYAML: запуск — Python окружения скилла ($DDD_HOME/venv/bin/python, scripts/install.sh)")
try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

TOOLS = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(TOOLS.parent / "lib"))  # scripts/lib: kbpaths
import kbpaths  # noqa: E402
import polza_catalog as pcat  # noqa: E402  (coerce_input, validate, estimate — одна точка истины с polza.py)

VERSION = "2.2"
ROOT = kbpaths.kb("ai-media")
SCHEMA = ROOT / "05-prompting/asset-spec.schema.json"
DIALECTS = ROOT / "05-prompting/dialects.yaml"
ROUTING = ROOT / "13-routing-matrix/routing.yaml"
CHANNEL_CATALOGS = {"routerai": ("ROUTERAI_CATALOG", "api-v1-models.json")}   # канал → (переменная снимка, файл)

# оценочные слова без видимого содержания (базовый список; расширенный — dialects.yaml defaults.slop_words)
SLOP_WORDS = {"luminous", "radiant", "vibrant", "lush", "dynamic", "glowing", "gorgeous", "stunning", "breathtaking",
              "mesmerizing", "masterpiece", "8k", "ultra-detailed", "hyperrealistic", "epic", "cinematic"}
SHOT_WORDS = {"extreme-close-up": "extreme close-up", "close-up": "close-up", "medium": "medium shot",
              "medium-wide": "medium-wide shot", "wide": "wide shot", "establishing": "wide establishing shot",
              "top-down": "top-down shot", "macro": "macro shot", "flat-lay": "flat lay",
              "full-bleed-abstract": "full-bleed abstract composition"}
ANGLE_WORDS = {"eye-level": "at eye level", "low-angle": "from a low angle", "high-angle": "from a high angle",
               "top-down": "from directly above", "45-degree": "from above at a 45-degree angle",
               "over-the-shoulder": "over the shoulder", "dutch": "with a slight dutch tilt"}
REGION_WORDS = {"left-third": "left third of the frame", "right-third": "right third of the frame",
                "center": "center of the frame", "top": "upper part of the frame", "bottom": "lower part of the frame",
                "full-frame": "whole frame"}
SIDE_WORDS = {"left": "left", "right": "right", "top": "top", "bottom": "bottom", "center": "central",
              "top-left": "top-left", "top-right": "top-right", "bottom-left": "bottom-left",
              "bottom-right": "bottom-right"}
MOVE_WORDS = {"static": "stays locked", "dolly-in": "slowly dollies in", "dolly-out": "slowly dollies out",
              "pan-left": "pans left", "pan-right": "pans right", "tilt-up": "tilts up", "tilt-down": "tilts down",
              "truck-left": "trucks left", "truck-right": "trucks right", "pedestal-up": "rises on a pedestal",
              "pedestal-down": "lowers on a pedestal", "orbit": "orbits the subject", "tracking": "tracks the subject",
              "crane-up": "cranes up", "crane-down": "cranes down", "zoom-in": "zooms in", "zoom-out": "zooms out"}
# MiniMax H3: «тип + амплитуда + скорость» (01 §9)
H3_MOVES = {"dolly-in": "pushes in", "dolly-out": "pulls out", "pan-left": "pans left", "pan-right": "pans right",
            "tilt-up": "tilts up", "tilt-down": "tilts down", "truck-left": "trucks left", "truck-right": "trucks right",
            "pedestal-up": "pedestals up", "pedestal-down": "pedestals down", "orbit": "arcs around the subject",
            "tracking": "tracks the subject", "crane-up": "cranes up", "crane-down": "cranes down",
            "zoom-in": "zooms in", "zoom-out": "zooms out"}
MOVING_CAMERA_WORDS = ("tracking", "orbit", "pan ", "pans", "dolly", "truck", "crane", "handheld", "push-in",
                       "push in", "zoom")
NUMBER_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
                11: "eleven", 12: "twelve"}
DETERMINERS = {"a", "an", "the", "one", "two", "three", "four", "five", "six", "some", "several", "many"}
SIZE_WORDS = {"small": "small", "medium": "medium", "large": "large", "xl": "very large"}
SERVICE_SENTENCES = {"text": "No text.", "watermark": "No watermark.", "logo": "No logos.",
                     "subtitles": "No subtitles.", "music": "No background music.", "dialogue": "No dialogue."}
# правка настоящего кадра: надписи исходника остаются («No text.» велит их стереть) — запрещается только новый текст
EDIT_SERVICE_SENTENCES = {"text": "No added text."}
CYR = re.compile(r"[А-Яа-яЁё]")
DESCRIPTIVE_PATHS = ("subject", "composition", "camera", "light", "palette", "materials", "style", "mood",
                     "exclusions", "motion", "product", "series", "edit", "references")
FRAME_ROLES = ("first_frame", "last_frame", "mask", "edit_source")
# первые слова элемента edit.keep, перед которыми «the» не ставится («Keep all other objects unchanged»)
KEEP_OWN_DETERMINERS = {"its", "their", "his", "her", "our", "your", "this", "these", "those", "all", "every", "each", "both",
                        "any", "everything"}


class CompileError(Exception):
    pass


def cap(text):
    """Заглавная первая буква без понижения остальных (str.capitalize портит hex и имена)."""
    return text[:1].upper() + text[1:] if text else text


def sentence(text):
    text = (text or "").strip()
    if not text:
        return None
    return cap(text if text[-1] in ".!?" else text + ".")


def _period(text):
    """Точка в конце без смены регистра (для отрезков таймлайна и планов)."""
    text = (text or "").strip()
    return text if not text or text[-1] in ".!?;" else text + "."


# ---------------------------------------------------------------- загрузка

_CACHE: dict = {}


def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def _merge_video(d):
    for fname, extra in (d.get("video") or {}).items():
        fam = (d.get("families") or {}).get(fname)
        if fam is not None:
            for k, v in extra.items():
                fam.setdefault(k, v)
    return d


def load_dialects(path=DIALECTS):
    return _merge_video(yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8")))


def snapshot_dir():
    """Папка снимка каталога polza: POLZA_CATALOG (имя папки или путь), иначе последний снимок в
    $DDD_HOME/cache/ai-media/polza/. Читается при первой команде, которой нужен каталог; снимка нет — строка с командой
    установки в stderr и код 2."""
    if "snapshot" not in _CACHE:
        try:
            _CACHE["snapshot"] = pcat.find_snapshot(os.environ.get("POLZA_CATALOG") or None)
        except SystemExit as e:
            print(f"{e} — снимок каталога polza: scripts/install.sh --catalogs или polza_catalog.py snapshot "
                  f"(бесплатный GET); другой снимок — POLZA_CATALOG", file=sys.stderr)
            raise SystemExit(2) from None
    return _CACHE["snapshot"]


def catalog_file():
    return snapshot_dir() / "api-v1-models.json"


def load_catalog(path=None):
    data = load_json(path or catalog_file())
    items = data["data"] if isinstance(data, dict) and "data" in data else data
    return {m["id"]: m for m in items if m.get("type") in ("image", "video")}


def load_normalized(path=None):
    path = path or snapshot_dir() / "media-models.normalized.json"
    key = ("norm", str(path))
    if key not in _CACHE:
        try:
            _CACHE[key] = {m["id"]: m for m in load_json(path)["models"]}
        except FileNotFoundError:
            _CACHE[key] = {}
    return _CACHE[key]


def file_sha256(path):
    key = ("sha", str(path))
    if key not in _CACHE:
        p = pathlib.Path(path)
        _CACHE[key] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
    return _CACHE[key]


def family_of(model_id, dialects, channel=None):
    """(имя семейства, семейство). channel=routerai|genapi — модель из раздела channels (копия семейства с её данными)."""
    if channel and channel != "polza":
        ch = (dialects.get("channels") or {}).get(channel) or {}
        info = (ch.get("models") or {}).get(model_id)
        if info is None:
            raise CompileError(f"модели {model_id} нет в channels.{channel} (dialects.yaml)")
        fam = copy.deepcopy(dialects["families"][info["family"]])
        fam["models"] = {model_id: info}
        fam["in_polza"] = False
        fam["channel"] = channel
        return info["family"], fam
    for name, fam in dialects["families"].items():
        if model_id in (fam.get("models") or {}):
            return name, fam
    raise CompileError(f"модель {model_id} не описана в dialects.yaml")


def defaults(dialects):
    return (dialects or {}).get("defaults") or {}


# ---------------------------------------------------------------- спецификация: опции, ссылки, язык

def compile_options(spec, options=None):
    o = dict(spec.get("compile") or {})
    for k, v in (options or {}).items():
        if v is not None:
            o[k] = v
    return o


def ref_by_id(spec, rid):
    for r in spec.get("references", []):
        if r.get("id") == rid or r.get("src") == rid:
            return r
    return None


def iter_strings(obj, path=""):
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_strings(v, f"{path}/{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_strings(v, f"{path}[{i}]")


def cyrillic_in_description(spec):
    """Пути описательных полей с кириллицей (кроме дословных надписей text.strings[].text и путей к файлам)."""
    bad = []
    for top in DESCRIPTIVE_PATHS:
        for path, s in iter_strings(spec.get(top), top):
            if path.endswith(("/src", "/source", "/start_frame", "/end_frame", "/source_video", "/id")) or "/src" in path:
                continue
            if CYR.search(s):
                bad.append(path)
    return bad


def words_in(text, words):
    low = (text or "").lower()
    return sorted({w for w in words if re.search(rf"(?<![\w-]){re.escape(w.lower())}(?![\w-])", low)})


# ---------------------------------------------------------------- проверки спецификации

def validate_spec(spec, model_id=None, dialects=None, catalog=None, *, channel=None, options=None, spec_path=None):
    """Возвращает (errors, warnings). Вызов: validate_spec(spec, model_id, dialects, catalog).
    spec_path — файл спецификации: от его папки считаются пути картинок входа при сверке их размера. Спецификация,
    которая не проходит схему и на которой смысловые проверки обрываются (нет обязательного поля, не тот тип значения),
    получает ошибку строкой, а не исключение."""
    errors, warnings = [], []
    if jsonschema is None:
        warnings.append("jsonschema не установлен — схема не проверена")
    else:
        v = jsonschema.Draft202012Validator(load_json(SCHEMA))
        for e in sorted(v.iter_errors(spec), key=lambda e: list(e.path)):
            errors.append(f"схема: {'/'.join(map(str, e.path)) or '(корень)'}: {e.message}")
    by_schema = len(errors)
    try:
        _meaning_checks(spec, model_id, dialects, catalog, errors, warnings, channel=channel, options=options,
                        spec_path=spec_path)
    except (KeyError, TypeError, AttributeError, IndexError) as e:
        if jsonschema is not None and not by_schema:
            raise                     # схема пройдена, а проверка упала — ошибка кода, а не входа
        why = "спецификация не проходит схему" if by_schema else "схема не проверена (нет jsonschema)"
        errors.append(f"смысловые проверки остановлены: {why} — {type(e).__name__}: {e}")
    return errors, warnings


def _meaning_checks(spec, model_id, dialects, catalog, errors, warnings, *, channel=None, options=None, spec_path=None):
    """Смысловые проверки validate_spec — сверх схемы: палитра, зоны, движение, язык, серия, правка, текст, модель.
    Пишет в errors и warnings; рассчитаны на спецификацию, прошедшую схему."""
    dfl = defaults(dialects)
    opts = compile_options(spec, options)
    comp = spec.get("composition", {})
    # палитра
    pal = spec.get("palette", [])
    total = sum(c.get("share", 0) for c in pal)
    if total > 1.05:
        errors.append(f"палитра: сумма долей {total:.2f} > 1")
    if len(pal) > 5:
        warnings.append(f"палитра: {len(pal)} цветов — больше 5 модели выполняют хуже (BFL)")
    # прямоугольники
    for name, rect in [("text_zone", (comp.get("text_zone") or {}).get("rect"))] + \
                      [(f"safe_zone {z['ratio']}", z["keep_rect"]) for z in comp.get("safe_zones", [])]:
        if rect and not (rect[0] < rect[2] and rect[1] < rect[3]):
            errors.append(f"{name}: неверный прямоугольник {rect}")
    fp, tz = _point(comp.get("focal_point")), comp.get("text_zone")
    if comp.get("focal_point") is not None and fp is None and jsonschema is None:
        errors.append("composition.focal_point: нужен объект {\"x\": доля, \"y\": доля}, а не список")
    if fp and tz and _inside(fp, tz["rect"]):
        errors.append("фокусная точка внутри зоны под текст")
    if tz and comp.get("subject_region"):
        side, reg = tz["side"], comp["subject_region"]
        if (side.startswith("left") and reg == "left-third") or (side.startswith("right") and reg == "right-third") \
                or (side == "center" and reg == "center"):
            errors.append(f"субъект ({reg}) и зона под текст ({side}) на одной стороне")
    for z in comp.get("safe_zones", []):
        if fp and not _inside(fp, z["keep_rect"]):
            errors.append(f"фокусная точка вне безопасной зоны {z['ratio']}")
    # противоречия движения (BFL prompt-doctor, 01 §5.9)
    mo = spec.get("motion")
    if mo:
        move = mo["camera"]["move"]
        motion_text = " ".join(filter(None, [mo.get("subject_motion"), mo.get("environment_motion")] +
                                      [b.get("motion", "") for b in mo.get("background_motion", [])])).lower()
        if move == "static" and any(w in motion_text for w in MOVING_CAMERA_WORDS):
            errors.append("противоречие: неподвижная камера + движение камеры в тексте движения")
        if mo.get("loop") == "first_last_same" and mo.get("cuts") == "allowed":
            errors.append("противоречие: петля по одному кадру + склейки")
        if mo.get("loop") == "first_last_same" and mo.get("start_frame") and mo.get("end_frame") \
                and mo["start_frame"] != mo["end_frame"]:
            errors.append("петля first_last_same: start_frame и end_frame различаются")
        for b in mo.get("timeline", []):
            if b["t1"] <= b["t0"] or b["t1"] > mo["duration_s"] + 1e-6:
                errors.append(f"таймлайн: неверный интервал {b['t0']}–{b['t1']} при длительности {mo['duration_s']}")
        forbid = set(mo.get("forbid", []))
        if "zoom" in forbid and move in ("zoom-in", "zoom-out"):
            errors.append(f"противоречие: запрет zoom + движение камеры {move}")
        if "camera_move" in forbid and move != "static":
            errors.append(f"противоречие: запрет движения камеры + движение {move}")
        if "cuts" in forbid and mo.get("shots"):
            errors.append("противоречие: запрет склеек + мульти-шот")
        still = {s.lower() for s in mo.get("still", [])}
        for b in mo.get("background_motion", []):
            if b["element"].lower() in still:
                errors.append(f"противоречие: «{b['element']}» и движется, и неподвижен")
        shots = mo.get("shots") or []
        if shots:
            if mo.get("loop") == "first_last_same":
                errors.append("противоречие: петля по одному кадру + мульти-шот")
            span = sum(s["t1"] - s["t0"] for s in shots)
            if abs(span - mo["duration_s"]) > 0.01:
                errors.append(f"мульти-шот: сумма планов {span:g} с ≠ длительности {mo['duration_s']:g} с")
            for s in shots:
                if s["t1"] - s["t0"] < 1 - 1e-6:
                    errors.append(f"мульти-шот: план {s['t0']}–{s['t1']} короче 1 с")
        if mo.get("kind") in ("loop", "cinemagraph") and not (mo.get("background_motion") or mo.get("environment_motion")
                                                              or mo.get("subject_motion")):
            warnings.append("петля/синемаграф без перечня движения: «что не названо — не движется» [V:OA4xB5EY02g 32:46]")
        qw = words_in(motion_text, dfl.get("quality_words", []))
        if qw and not opts.get("quality_words"):
            warnings.append(f"слова качества в движении ({', '.join(qw)}) — не работают (W3), убрать")
    if comp.get("shot") == "extreme-close-up" and "establishing" in json.dumps(spec).lower():
        errors.append("противоречие: extreme close-up + establishing")
    # слоп и «warm» как грейд
    words = " ".join(spec.get("mood", []) + (spec.get("style") or {}).get("anchors", []) +
                     [spec["subject"].get("summary", "")] if spec.get("subject") else [])
    slop = sorted(w for w in SLOP_WORDS if re.search(rf"\b{re.escape(w)}\b", words.lower()))
    extra = [w for w in words_in(words, dfl.get("slop_words", [])) if w not in slop]
    if slop or extra:
        warnings.append(f"оценочные слова без видимого содержания: {', '.join(slop + extra)}")
    gw = words_in(" ".join([json.dumps(spec.get("light") or {}), json.dumps(spec.get("style") or {}),
                            " ".join(spec.get("mood", []))]), dfl.get("grading_words", []))
    if gw:
        warnings.append("«warm» как грейд даёт «янтарный ИИ-вид» (Ideogram) — задай источник света (candle flame, "
                        "golden-hour sun)")
    # язык описания (03 §12.3 п. 7)
    cyr = cyrillic_in_description(spec)
    if cyr and opts.get("language", "en") != "ru":
        errors.append(f"кириллица в описательных полях ({', '.join(cyr[:4])}{'…' if len(cyr) > 4 else ''}): описание — "
                      f"по-английски, русский — только в text.strings[].text (или compile.language: ru для плеча A/B)")
    # серия
    ser = spec.get("series") or {}
    sb = (spec.get("style") or {}).get("series_block")
    if ser.get("block") and sb and ser["block"] != sb:
        errors.append("серия: series.block и style.series_block различаются — блок должен быть дословно одинаковым")
    if (ser.get("avoid_average") or opts.get("anti_average")) and comp.get("subject_region") == "center":
        errors.append("противоречие: «против среднего вида» (субъект вне центра) + composition.subject_region: center")
    # правка
    ed = spec.get("edit")
    if ed:
        op = ed.get("operation")
        if not op and jsonschema is None:
            errors.append("правка: нет edit.operation")
        if op and op not in ("extend", "restyle", "relight") and not ed.get("changes"):
            errors.append("правка: нет changes (что → на что)")
        comps = set(dfl.get("comparatives", []))
        for ch in ed.get("changes", []):
            cw = words_in(ch["to"], comps)
            if cw and not ch.get("value"):
                warnings.append(f"правка «{ch['target']}»: сравнительная формулировка ({', '.join(cw)}) — задай целевое "
                                f"значение value (#1F5E3B, 2700 K) [V:8kM5aDD5gLI 25:38]")
        src = ed.get("source")
        if src and not ref_by_id(spec, src) and not re.search(r"\.(png|jpe?g|webp)$|^https?://", src, re.I):
            errors.append(f"правка: источник {src!r} не найден среди references (id/src) и не похож на файл")
        if op == "extend" and not ed.get("target_ratio"):
            errors.append("аутпейнт (extend): нужен edit.target_ratio")
    # текст
    t = spec.get("text", {})
    if t.get("mode") == "in_image":
        for s in t.get("strings", []):
            if len(s["text"].split()) > 4:
                warnings.append(f"надпись «{s['text']}»: > 4 слов — надёжно 1–4 (BFL)")
    # модель
    if model_id and dialects and catalog is not None:
        name, fam = family_of(model_id, dialects, channel)
        text = spec.get("text", {})
        if text.get("mode") == "in_image":
            scripts = {s["script"] for s in text["strings"]}
            ok = (fam.get("text") or {}).get("scripts_ok")
            if ok and not scripts <= set(ok):
                errors.append(f"{name}: письменность {sorted(scripts)} не поддерживается ({ok})")
            if "Cyrillic" in scripts:
                warnings.append("кириллица в картинке: обязательна проверка OCR; запасной путь — HTML-слой")
        if mo and not fam.get("video"):
            errors.append(f"{name}: спецификация с движением, а модель — картинка")
        if not mo and fam.get("video"):
            errors.append(f"{name}: видео-модель, а в спецификации нет motion")
        if ed and fam.get("video"):
            errors.append(f"{name}: правка картинки на видео-модели")
        refs = [r for r in spec.get("references", []) if r["role"] not in ("mask",)]
        mref = (fam["models"][model_id] or {}).get("max_refs")
        if mref is not None and len(refs) > mref:
            errors.append(f"{model_id}: референсов {len(refs)} > {mref}")
        input_size_check(spec, fam, model_id, spec_path, errors, warnings)


def image_size(path):
    """(ширина, высота) локальной картинки; None — файла нет или он не читается как картинка. Нужен Pillow."""
    from PIL import Image
    try:
        with Image.open(path) as im:
            return im.size
    except (OSError, ValueError, Image.DecompressionBombError):
        return None


def input_size_check(spec, fam, model_id, spec_path, errors, warnings):
    """Картинки входа против минимального размера модели — `min_input_px` записи модели в dialects.yaml: меньшая
    сторона референса, исходника правки или кадра ниже минимума — ошибка до вызова (вход меньше минимума модель не
    принимает). URL и отсутствующие файлы не сверяются: о них говорит сборка заданий."""
    need = ((fam.get("models") or {}).get(model_id) or {}).get("min_input_px")
    if not need:
        return
    images = collect_inputs(spec, fam, model_id, detect_mode(spec), spec_path)[0]
    local = [p for p in dict.fromkeys(images) if p and not re.match(r"^(https?|data):", p) and pathlib.Path(p).exists()]
    if not local:
        return
    try:
        sizes = [(p, image_size(p)) for p in local]
    except ImportError:
        warnings.append(f"{model_id}: размер входа не сверен с min_input_px {need} — нет Pillow")
        return
    for p, size in sizes:
        name = pathlib.Path(p).name
        if size is None:
            warnings.append(f"{model_id}: вход {name} не читается как картинка — размер не сверен с min_input_px {need}")
        elif min(size) < need:
            errors.append(f"{model_id}: вход {name} — {size[0]}×{size[1]} px, меньшая сторона {min(size)} < {need} "
                          f"(min_input_px модели): такой вход модель не принимает — увеличить картинку или взять другую")


def _point(p):
    """Фокусная точка {"x", "y"} или None (список [x, y] — ошибка схемы, а не TypeError)."""
    return p if isinstance(p, dict) and isinstance(p.get("x"), (int, float)) and isinstance(p.get("y"), (int, float)) else None


def _inside(p, r):
    return r[0] <= p["x"] <= r[2] and r[1] <= p["y"] <= r[3]


# ---------------------------------------------------------------- фразы из полей

def pct(x):
    return f"{round(x * 100)} percent"


def subject_phrase(spec, short=False):
    s = spec["subject"]
    parts = [cap(s["summary"].rstrip("."))]
    for e in s.get("elements", []):
        what = e["what"]
        if e.get("count", 1) > 1:
            head = f"{NUMBER_WORDS.get(e['count'], str(e['count']))} {what}"
        elif what.split()[0].lower() in DETERMINERS or (what.split()[-1].endswith("s") and not what.split()[-1].endswith("ss")) \
                or " with " in what and what.split(" with ")[0].split()[-1].endswith("s"):
            head = what
        else:
            head = ("An " if what[:1].lower() in "aeiou" else "A ") + what
        if short:
            parts.append(cap(head + (f" in the {e['position']}" if e.get("position") else "")))
            continue
        if e.get("attributes"):
            head += " " + " ".join(e["attributes"])
        tail = []
        if e.get("relation"):
            tail.append(e["relation"])
        if e.get("position"):
            tail.append(f"in the {e['position']}")
        if e.get("action"):
            tail.append(e["action"])
        parts.append(cap(head + (" " + ", ".join(tail) if tail else "")))
    return parts


def composition_phrase(spec, short=False):
    c = spec["composition"]
    out = [SHOT_WORDS[c["shot"]]]
    if c.get("angle"):
        out.append(ANGLE_WORDS[c["angle"]])
    if c.get("subject_region") and c["subject_region"] != "full-frame":
        out.append(f"main subject in the {REGION_WORDS[c['subject_region']]}")
    if short:
        return ", ".join(out)
    if c.get("depth_layers"):
        out.append("layers: " + "; ".join(c["depth_layers"]))
    if c.get("layout_note"):
        out.append(c["layout_note"])
    return ", ".join(out)


def _zone_frac(tz):
    x0, y0, x1, y1 = tz["rect"]
    return (x1 - x0) if tz["side"] in ("left", "right") else (y1 - y0) if tz["side"] in ("top", "bottom") else (x1 - x0)


def text_zone_phrase(spec, fam, style="base", short=False):
    tz = spec["composition"].get("text_zone")
    if not tz:
        return None
    frac = _zone_frac(tz)
    side = SIDE_WORDS[tz["side"]]
    # поверхность — без артикля («an empty, uncluttered a long lawn»)
    surface = re.sub(r"^(a|an|the)\s+", "", tz.get("surface", "plain background").strip(), flags=re.I)
    # «empty»/«uncluttered» в начале поверхности уже есть во фразе → «an empty, uncluttered empty wall» (демо 14-recipes)
    surface = re.sub(r"^(?:(?:empty|uncluttered)(?:\s*,\s*|\s+and\s+|\s+))+", "", surface, flags=re.I) or surface
    tone = tz.get("tone", "even and low in contrast")
    positive_only = (fam.get("negative") or {}).get("object") == "positive"
    empty = "empty, uncluttered" if positive_only else "empty"
    if short and style == "base":
        return f"The {side} {pct(frac)} of the frame is an {empty} {surface} for a {tz['purpose']}."
    if style == "google":      # Gemini API «Minimalist & negative space» [S2 файла 01]
        return f"The {side} {pct(frac)} of the frame is a vast, empty {surface}, creating significant negative space for text."
    if style == "openai":      # OpenAI «subject centered with negative space on left»
        return f"Clean negative space on the {side} ({pct(frac)} of the frame) for a {tz['purpose']}."
    if style == "copyspace":   # жаргон фотостоков — плечо A/B (01 §12.6)
        return f"Copy space on the {side}."
    if style == "vendor" and (fam.get("text_zone") or {}).get("template"):
        region = REGION_WORDS.get(spec["composition"].get("subject_region") or "", "frame")
        t = fam["text_zone"]["template"]
        t = re.sub(r"^\{subject\}[^.;]*[.;]\s*", "", t).replace("Subject {region}, with ", "")
        return cap(t.format(subject="the subject", region=region, side_words=f"{side} {pct(frac)}", side=side,
                            surface=surface, percent=pct(frac)))
    return (f"The {side} {pct(frac)} of the frame is an {empty} {surface}, {tone}, "
            f"creating clean negative space for a {tz['purpose']}.")


def camera_phrase(spec, short=False):
    cam = spec.get("camera") or {}
    bits = []
    if cam.get("capture"):
        bits.append(f"shot as a {cam['capture']}")
    if short:
        return ", ".join(bits) or None
    if cam.get("lens_mm"):
        bits.append(f"{cam['lens_mm']:g}mm lens")
    if cam.get("aperture"):
        bits.append(cam["aperture"])
    if cam.get("depth_of_field"):
        bits.append(f"{cam['depth_of_field']} depth of field")
    if cam.get("film_stock"):
        bits.append(cam["film_stock"])
    return ", ".join(bits) or None


def light_phrase(spec, short=False):
    li = spec.get("light") or {}
    if not li:
        return None
    bits = []
    q = li.get("quality")
    src = li.get("source")
    if src:
        bits.append(f"{q + ' ' if q and q not in src else ''}{src}")
    if li.get("direction"):
        d = li["direction"]
        bits.append({"top": "light from above", "back": "backlight", "ambient": "ambient light"}.get(d, f"light from the {d}"))
    if short:
        return ", ".join(bits)
    if li.get("time_of_day"):
        bits.append(li["time_of_day"])
    if li.get("interaction"):
        bits.append(li["interaction"])
    return ", ".join(bits)


def palette_phrases(spec, fam, form="family", short=False):
    pf = fam.get("palette") or {}
    use_hex = pf.get("hex") in ("documented", "untested") and "{hex}" in pf.get("form", "")
    fmt = pf.get("form", "{name}")
    if form == "hex" and not use_hex:
        use_hex, fmt = True, "{name} ({hex})"
    elif form == "names":
        use_hex = False
    if short:
        cols = sorted(spec["palette"][:5], key=lambda c: -(c.get("share") or 0))
        names = [c["name"] for c in cols]
        return [", ".join(names[:1]) + (" with " + " and ".join(names[1:3]) + " accents" if len(names) > 1 else "")]
    out = []
    for c in spec["palette"][:5]:
        name = c["name"]
        col = fmt.format(name=name, hex=c["hex"].upper()) if use_hex else name
        target = c.get("applies_to")
        share = c.get("share")
        if share is not None and share >= 0.45:
            amount = "dominates, filling most of the frame"
        elif share is not None and share >= 0.2:
            amount = "covers a large secondary area"
        elif share is not None:
            amount = "is used only" if target else "appears only as a small accent"
        else:
            amount = "is used"
        out.append(f"{col} {amount}{' on the ' + target if target else ''}")
    return out


def style_phrase(spec, short=False):
    st = spec.get("style") or {}
    bits = []
    if st.get("medium"):
        bits.append(st["medium"].replace("-", " "))
    anchors = st.get("anchors", [])
    bits += anchors[:1] if short else anchors
    if not short:
        for k in ("line", "finish", "grain"):
            if st.get(k):
                bits.append(st[k])
    return ", ".join(bits) or None


def exclusion_sentences(spec, fam, warnings, negation="family", edit=False):
    """(позитивные замены, предложения-запреты). edit — запреты для правки настоящего кадра: служебный запрет текста
    пишется «No added text.» — надписи исходника остаются."""
    neg = fam.get("negative") or {}
    service_mode, object_mode = neg.get("service", "sentence"), neg.get("object", "positive")
    if negation == "sentence":
        service_mode = object_mode = "sentence"
    elif negation == "positive":
        service_mode, object_mode = "positive", "positive"
    repl = neg.get("replacements") or {}
    out, positive = [], []
    excl = list(spec.get("exclusions", []))
    tmode = spec.get("text", {}).get("mode")
    if tmode in ("none", "html_overlay") and not any(e["what"] == "text" for e in excl):
        excl.append({"what": "text", "kind": "service"})
    for e in excl:
        what = e["what"].lower()
        if e["kind"] == "service":
            if service_mode == "sentence":
                out.append((edit and EDIT_SERVICE_SENTENCES.get(what)) or SERVICE_SENTENCES.get(what, f"No {what}."))
            elif service_mode == "positive":
                r = e.get("replace_with") or repl.get(what)
                if r:
                    positive.append(r)
                else:
                    warnings.append(f"служебный запрет «{what}» опущен: у семейства только позитивные формулировки")
        else:
            if negation == "sentence":
                out.append(f"No {what}.")
            elif e.get("replace_with"):
                positive.append(e["replace_with"])
            elif object_mode == "sentence":
                out.append(f"Do not include {what}.")
            else:
                warnings.append(f"запрет «{what}» опущен: нужна позитивная замена replace_with")
    return _dedupe(positive), _dedupe(out)   # без повтора («clean unmarked surfaces» ×2)


def _dedupe(items):
    seen, res = set(), []
    for x in items:
        k = re.sub(r"\s+", " ", x.strip().lower().rstrip("."))
        if k and k not in seen:
            seen.add(k)
            res.append(x)
    return res


def text_sentences(spec, fam, dfl=None):
    t = spec.get("text", {})
    if t.get("mode") != "in_image":
        return []
    tf = fam.get("text") or {}
    q = tf.get("quote", "\"")
    out = []
    for s in t["strings"]:
        lang = {"ru": "Russian", "en": "English"}.get(s["language"], s["language"])
        bits = [f"The {s['role']} reads {q}{s['text']}{q}"]
        if s["script"] != "Latin" or tf.get("language_tag"):
            bits.append(f"in {lang} ({s['script']} script)")
        if s.get("typography"):
            bits.append(f"set in {s['typography']}")
        if s.get("color"):
            bits.append(f"in color {s['color'].upper()}")
        if s.get("size"):
            bits.append(f"{SIZE_WORDS.get(s['size'], s['size'])} size")
        bits.append(f"placed {s['position']}")
        if s.get("surface"):
            bits.append(s["surface"])
        out.append(", ".join(bits) + ".")
    if tf.get("exactly_once"):
        out.append("Render each text exactly once, clearly and legibly.")
    if t.get("strict_spelling"):   # блок типографики продукта [V:XLHTLJhzDyQ 03:05]
        ss = (dfl or {}).get("strict_spelling") or {}
        positive = (fam.get("negative") or {}).get("service") == "positive"
        out.append(ss.get("positive" if positive else "sentence", "No misspellings, no extra letters, and no warped glyphs."))
    out.append(tf.get("closing") or "No other text.")
    return out


# ---------------------------------------------------------------- референсы, продукт, серия, против «среднего»

def ref_syntax(fam):
    return ((fam.get("references") or {}).get("syntax")) or "Image {n}"


def ref_label(fam, n):
    syn = ref_syntax(fam)
    if "IMAGE_REF" in syn:          # Omni: нумерация с нуля
        return syn.format(n=n - 1)
    if "{n}" not in syn:
        return syn
    return syn.format(n=n)


ROLE_DEFAULT_NOTE = {"style": "rendering style, line weight and palette", "identity": "key features",
                     "subject": "shape and key details", "character": "same look", "product": "exact appearance",
                     "composition": "placement of the main masses", "layout": "positions of all elements",
                     "palette": "colors only", "background": "same place", "material": "texture and finish",
                     "effect": "same treatment", "pose": "body position", "video_motion": "motion only"}


def declared_refs(spec, mode):
    """Референсы, которые объявляются в тексте, в порядке images[] (после исходника правки)."""
    refs = spec.get("references", [])
    mo = spec.get("motion") or {}
    out = []
    for r in refs:
        if r["role"] in ("first_frame", "last_frame", "mask", "edit_source"):
            continue
        if mode in ("i2v", "flf") and mo.get("reference_mode", "frames") == "frames" and r.get("kind") != "video":
            continue
        out.append(r)
    return out


def _group_label(fam, idxs):
    """Метка группы референсов: «Images 1-3» (синтаксис Image {n}) или перечисление меток семейства."""
    syn = ref_syntax(fam)
    if syn in ("Image {n}", "image {n}"):
        word = "Images" if syn[0] == "I" else "images"
        return f"{word} {idxs[0]} and {idxs[1]}" if len(idxs) == 2 else f"{word} {idxs[0]}-{idxs[-1]}"
    if "{n}" not in syn:                       # «the provided image» (Grok)
        return syn.replace("image", "images")
    labels = [ref_label(fam, i) for i in idxs]
    return ", ".join(labels[:-1]) + " and " + labels[-1]


def _ref_note(r):
    return r.get("note") or ROLE_DEFAULT_NOTE.get(r["role"], r["role"])


def references_phrase(spec, fam, dfl, mode, start_index=1):
    refs = declared_refs(spec, mode)
    if not refs:
        return None
    roles = dfl.get("reference_roles") or {}
    groups = dfl.get("reference_group") or {}
    out, i, k = [], start_index, 0
    while k < len(refs):
        r, note = refs[k], _ref_note(refs[k])
        j = k + 1          # подряд идущие референсы одной роли с одной заметкой — одной фразой
        while j < len(refs) and refs[j]["role"] == r["role"] and _ref_note(refs[j]) == note:
            j += 1
        n = j - k
        if n >= 2 and groups:
            tpl = groups.get(r["role"]) or groups.get("default", "{refs}: {note}.")
            s = tpl.format(refs=_group_label(fam, list(range(i, i + n))), note=note)
        else:
            n = 1
            s = roles.get(r["role"], "{ref}: {note}.").format(ref=ref_label(fam, i), note=note)
        out.append(cap(s.replace(" ()", "")))
        i += n
        k += n
    return " ".join(out)


PEOPLE_WORDS = re.compile(r"\b(person|people|woman|women|man|men|girl|boy|child|children|kid|face|portrait|character|"
                          r"hiker|hikers|model|couple|family|team|worker|he|she|they|customer|user)\b", re.I)


def anti_average_phrase(spec, dfl):
    """«Против среднего» по частям — взгляд только у людей, несовершенства только у фото («gaze» у предмета)."""
    parts = dfl.get("anti_average_parts")
    if not parts:
        return dfl.get("anti_average")
    subj = spec.get("subject") or {}
    text = " ".join([subj.get("summary", "")] + [e.get("what", "") for e in subj.get("elements", [])])
    bits = [parts["base"]]
    if PEOPLE_WORDS.search(text) or any(r.get("role") in ("character", "identity", "pose") for r in spec.get("references", [])):
        bits.append(parts["people"])
    medium = (spec.get("style") or {}).get("medium")
    drawn = re.search(r"illustrat|vector|flat |3d|render|icon|clay|cartoon|anime|painting|drawing|isometric",
                      " ".join([text, (spec.get("series") or {}).get("block") or "", (spec.get("style") or {}).get("series_block") or ""]), re.I)
    if medium == "photograph" or (not medium and not drawn):
        bits.append(parts["photo"])
    return ", ".join(bits) + "."


def product_phrases(spec):
    p = spec.get("product") or {}
    if not p:
        return None, None
    ident = []
    if p.get("identity"):
        ident.append(sentence(f"The product is {p['identity']}"))
    if p.get("locks"):
        ident.append(sentence(f"Keep the {_join(p['locks'])} exactly as on the real product"))
    if p.get("dimensions"):
        ident.append(sentence(f"Scale: {p['dimensions']}"))
    cols = [f"the {x['part']} is {x['color']}" + (f" ({x['hex'].upper()})" if x.get("hex") else "")
            for x in p.get("parts", [])]
    return (" ".join(ident) or None), (sentence("; ".join(cols)) if cols else None)


def _join(items):
    items = [x for x in items if x]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1] if items else ""


# ---------------------------------------------------------------- движение (фон, неподвижное, запреты, темп, планы)

def _ordinal(n):
    n = int(round(n))
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def motion_sentences(spec, fam, warnings, dfl=None, fname=None):
    mo = spec.get("motion")
    if not mo:
        return []
    dfl = dfl or {}
    cam = mo["camera"]
    fcam = fam.get("camera") or {}
    out = []
    if cam["move"] == "static":
        target = cam.get("target") or "the subject"    # Kling «The camera remains fixed on {target}»
        out.append(sentence(fcam.get("static", "Locked camera. The camera remains still.")
                            .replace("{target}", target).replace(" as …", ".")))
    elif fname == "minimax-h3":
        amp = cam.get("amplitude", "small")
        spd = cam.get("speed", "slow")
        out.append(f"The camera {H3_MOVES.get(cam['move'], MOVE_WORDS[cam['move']])} with {amp} amplitude at {spd} speed.")
    else:
        amp = f" with {cam['amplitude']} amplitude" if cam.get("amplitude") else ""
        spd = f" at {cam['speed']} speed" if cam.get("speed") else ""
        out.append(f"The camera {MOVE_WORDS[cam['move']]}{amp}{spd}.")
    if mo.get("subject_motion"):          # с заглавной («… still. the beans turn»)
        out.append(cap(mo["subject_motion"].rstrip(".") + "."))
    if mo.get("environment_motion"):
        out.append(cap(mo["environment_motion"].rstrip(".") + "."))
    for b in mo.get("background_motion", []):          # «что не названо — не движется»
        out.append(sentence(f"{b['element']} {b['motion']}"))
    if mo.get("still"):
        out.append(sentence(f"{_join(mo['still'])} {'stays' if len(mo['still']) == 1 else 'stay'} perfectly still"))
    if mo.get("tempo"):
        out.append((dfl.get("tempo_words") or {}).get(mo["tempo"], ""))
    if mo.get("frame_annotations"):
        out.append("Perform the actions shown by the arrows and notes drawn on the first frame; the drawings disappear "
                   "within the first second.")
    ts = fam.get("timestamps") or {}
    tpl = fam.get("timestamps_template")
    tl = sorted(mo.get("timeline", []), key=lambda x: x["t0"])
    if tl and ts.get("supported") and ts.get("unit_s"):   # Seedance 2.5 — целые секунды, без разрывов [27][31]
        u = float(ts["unit_s"])
        if any(abs(x / u - round(x / u)) > 1e-6 for b in tl for x in (b["t0"], b["t1"])):
            warnings.append(f"таймлайн {fname}: границы не кратны {u:g} с — вендор: «Do not claim precision to 0.5 seconds»")
        if ts.get("no_gaps") and any(abs(tl[i + 1]["t0"] - tl[i]["t1"]) > 1e-6 for i in range(len(tl) - 1)):
            warnings.append(f"таймлайн {fname}: разрывы или наложения между отрезками — вендор: «avoid gaps such as 0-3s… 5-6s»")
    for b in mo.get("timeline", []):
        beat = _period(b["beat"])     # отрезки — законченными предложениями (иначе «…cup [00:02-00:04] the curtain…»)
        if ts.get("supported"):
            if tpl:
                out.append(tpl.format(t0=b["t0"], t1=b["t1"], beat=beat, t0_ord=_ordinal(b["t0"])))
            else:
                out.append(f"[{b['t0']:g}-{b['t1']:g}s] {beat}")
        else:
            warnings.append("таймлайн опущен: семейство не держит таймкоды")
            break
    shots = mo.get("shots") or []
    if shots:
        ms = fam.get("multishot")
        if not ms:
            warnings.append(f"мульти-шот: у семейства {fname} нет грамматики планов — планы опущены (делите на клипы)")
        else:
            parts = []
            for n, s in enumerate(shots, 1):
                words = ", ".join(x for x in (s.get("framing"), s.get("camera"), s["action"]) if x)
                if ms.get("cut_word") and n > 1:
                    words = f"{ms['cut_word']} {words[:1].lower() + words[1:]}"
                if ms["template"].rstrip().endswith("{words}"):   # точка в конце плана (у Kling — «;» в шаблоне)
                    words = _period(words)
                parts.append(ms["template"].format(n=n, m=s["t1"] - s["t0"], t0=s["t0"], t1=s["t1"], words=words))
            out.append(ms.get("joiner", " ").join(parts))
            if ms.get("note"):
                warnings.append(f"мульти-шот {fname}: {ms['note']}")
    forbid = mo.get("forbid") or []
    if forbid:
        style = fam.get("motion_forbid", "positive")
        table = dfl.get("motion_forbid") or {}
        out.append(" ".join(table[f][style] for f in forbid if f in table))
    if mo.get("cuts", "none") == "none" and not shots:
        out.append(fam.get("single_shot_phrase") or "One continuous shot, same set and geometry, no cuts.")
    if mo.get("loop") == "first_last_same":
        out.append("The camera must start and end on the exact same frame to create a perfect loop.")
    return [x for x in out if x]


# ---------------------------------------------------------------- блоки и порядок

def detect_mode(spec):
    if spec.get("edit"):
        return "outpaint" if spec["edit"].get("operation") == "extend" else "edit"
    mo = spec.get("motion")
    if not mo:
        return "t2i"
    if mo.get("source_video"):
        return "v2v"
    if mo.get("reference_mode") == "references":
        return "ref2v"
    if mo.get("start_frame") and mo.get("end_frame"):
        return "flf"
    if mo.get("start_frame"):
        return "i2v"
    return "t2v"


def blocks(spec, fam, warnings, opts=None, dfl=None, fname=None, mode="t2i"):
    """Словарь смысловых блоков (по-английски) → из него собираются все диалекты."""
    opts, dfl = opts or {}, dfl or {}
    short = opts.get("length") == "short"
    positive_excl, neg_sentences = exclusion_sentences(spec, fam, warnings, opts.get("negation", "family"))
    ser = spec.get("series") or {}
    product, product_colors = product_phrases(spec)
    cam, li, st = camera_phrase(spec, short), light_phrase(spec, short), style_phrase(spec, short)
    b = {
        "subject": ". ".join(subject_phrase(spec, short)) + ".",
        "environment": (cap(spec["subject"].get("environment", "").rstrip(".")) + ".") if spec["subject"].get("environment") and not short else None,
        "culture": (f"Cultural context: {spec['subject']['culture']}.") if spec["subject"].get("culture") and not short else None,
        "composition": cap(composition_phrase(spec, short)) + ".",
        "text_zone": text_zone_phrase(spec, fam, opts.get("text_zone_style", "base"), short),
        "camera": (cap(cam) + ".") if cam else None,
        "light": (cap(li) + ".") if li else None,
        "palette": cap("; ".join(palette_phrases(spec, fam, opts.get("palette_form", "family"), short))) + ".",
        "materials": ("Materials: " + ", ".join(spec["materials"]) + ".") if spec.get("materials") and not short else None,
        "style": (cap(st) + ".") if st else None,
        "series_block": ser.get("block") or (spec.get("style") or {}).get("series_block"),
        "effect_block": ser.get("effect_block"),
        "mood": ("Mood: " + ", ".join(spec["mood"]) + ".") if spec.get("mood") and not short else None,
        "text": " ".join(text_sentences(spec, fam, dfl)) or None,
        "motion": " ".join(motion_sentences(spec, fam, warnings, dfl, fname)) or None,
        "positive_constraints": (cap(", ".join(positive_excl)) + ".") if positive_excl else None,
        "constraints": " ".join(neg_sentences) or None,
        "references": references_phrase(spec, fam, dfl, mode) if opts.get("refs", "declare") == "declare" else None,
        "product": product,
        "product_colors": product_colors,
        "anti_average": anti_average_phrase(spec, dfl) if (opts.get("anti_average") or ser.get("avoid_average")) else None,
        "quality": ("Cinematic, 4K, masterpiece, ultra-detailed, high quality." if opts.get("quality_words") else None),
    }
    return b


ORDER_MAP = {"subject": ["subject"], "scene": ["environment", "culture"], "environment": ["environment", "culture"],
             "composition": ["composition"], "cinematography": ["composition", "camera"], "text_zone": ["text_zone"],
             "camera": ["camera"], "light": ["light"], "aesthetic": ["light", "palette"], "palette": ["palette"],
             "materials": ["materials"], "details": ["materials"], "style": ["style"], "mood": ["mood"],
             "text": ["text"], "action": ["motion"], "motion": ["motion"],
             "constraints": ["positive_constraints", "constraints"]}
PROSE_ORDER = ["series_block", "subject", "environment", "culture", "composition", "text_zone", "motion", "light",
               "camera", "palette", "materials", "style", "mood", "text", "positive_constraints", "constraints"]
# где стоят новые блоки относительно якорей (у спецификаций v0.1 они пусты — текст не меняется)
NEW_BLOCK_ANCHORS = [("effect_block", "after", "series_block"), ("references", "after", "effect_block"),
                     ("product", "after", "subject"), ("anti_average", "after", "composition"),
                     ("product_colors", "after", "palette"), ("quality", "before", "positive_constraints")]
PRODUCT7_ORDER = ["series_block", "effect_block", "references", "composition", "anti_average", "text_zone", "subject",
                  "product", "environment", "culture", "motion", "text", "product_colors", "palette", "light", "camera",
                  "materials", "style", "mood", "quality", "positive_constraints", "constraints"]
SECTION_LABELS = [("series_block", "Series style (keep identical)"), ("effect_block", "Effect (keep identical)"),
                  ("references", "References"), ("subject", "Subject"), ("product", "Product"),
                  ("environment", "Setting"), ("culture", None), ("composition", "Composition"),
                  ("anti_average", "Composition rules"), ("text_zone", "Negative space"), ("motion", "Motion"),
                  ("light", "Lighting"), ("camera", "Camera"), ("palette", "Color palette"),
                  ("product_colors", "Product colors"), ("materials", None), ("style", "Style"), ("mood", None),
                  ("text", "Text (exact)"), ("quality", None), ("positive_constraints", "Requirements"),
                  ("constraints", "Constraints")]
FAMILY_LABEL_KEYS = {"subject": "subject", "environment": "environment", "composition": "composition",
                     "camera": "camera", "light": "light", "palette": "palette", "style": "style", "text": "text",
                     "constraints": "constraints", "positive_constraints": "constraints", "materials": "details"}


def ordered_keys(fam, opts=None):
    """Порядок блоков: order семейства (dialects.yaml); серия — всегда первой; остальное — по PROSE_ORDER."""
    opts = opts or {}
    order = opts.get("order", "family")
    if order == "product7":
        return list(PRODUCT7_ORDER)
    if order == "custom" and opts.get("custom_order"):
        keys = [k for k in opts["custom_order"]]
        return keys + [k for k in PRODUCT7_ORDER if k not in keys]
    keys = ["series_block"]
    for token in fam.get("order") or []:
        for k in ORDER_MAP.get(token, []):
            if k not in keys:
                keys.append(k)
    keys += [k for k in PROSE_ORDER if k not in keys]
    for new, where, anchor in NEW_BLOCK_ANCHORS:
        if new in keys:
            continue
        i = keys.index(anchor) if anchor in keys else len(keys) - 1
        keys.insert(i + 1 if where == "after" else i, new)
    # у видео-семейств запреты — в конце (иначе у Omni блоки вне order встают после «No text.»); у картинок — порядок
    # order семейства: на нём держатся регрессионные случаи тестов компилятора и задания стенда
    if fam.get("video"):
        tail = [k for k in ("quality", "positive_constraints", "constraints") if k in keys]
        keys = [k for k in keys if k not in tail] + tail
    if order == "shuffled":   # те же блоки вперемешку (серия и ограничения — на месте)
        fixed_head = [k for k in keys if k in ("series_block", "effect_block", "references")]
        fixed_tail = [k for k in keys if k in ("positive_constraints", "constraints")]
        mid = [k for k in keys if k not in fixed_head and k not in fixed_tail]
        random.Random(int(opts.get("shuffle_seed", 7))).shuffle(mid)
        keys = fixed_head + mid + fixed_tail
    return keys


def to_prose(b, fam, opts=None):
    return " ".join(b[k] for k in ordered_keys(fam, opts) if b.get(k))


def to_sections(b, fam, opts=None):
    opts = opts or {}
    labels = dict(SECTION_LABELS)
    if opts.get("labels") == "family" and fam.get("labels"):
        for k, token in FAMILY_LABEL_KEYS.items():
            if token in fam["labels"]:
                labels[k] = fam["labels"][token]
        if "scene" in fam["labels"]:
            labels["environment"] = fam["labels"]["scene"]
    if opts.get("labels") == "family" and fam.get("sections"):     # Seedance 2.5: разделы вендора
        return to_vendor_sections(b, fam)
    lines = []
    for k in ordered_keys(fam, opts):
        if b.get(k):
            label = labels.get(k)
            if label and k in ("series_block", "effect_block") and \
                    b[k].lower().startswith(label.split("(")[0].strip().lower()):
                label = None       # блок сам начинается с «Series style…» — без второй метки
            lines.append(b[k] if label is None else f"{label}: {b[k]}")
    return "\n".join(lines)


def to_vendor_sections(b, fam):
    """Seedance 2.5: Asset Referencing → One-Sentence Summary → Detailed Plot → Additional Notes (01 §6.4)."""
    s = fam["sections"]
    summary = " ".join(x for x in (b.get("subject"), b.get("environment"), b.get("composition"), b.get("style")) if x)
    notes = " ".join(x for x in (b.get("light"), b.get("palette"), b.get("series_block"), b.get("positive_constraints"),
                                 b.get("constraints")) if x)
    parts = [(s[0], b.get("references")), (s[1], summary or None), (s[2], b.get("motion")), (s[3], notes or None)]
    return "\n".join(f"{k}: {v}" for k, v in parts if v)


def to_json(spec, b):
    """Визуальные поля по базовой схеме BFL (scene, subjects, style, color_palette, lighting, mood, background,
    composition, camera) + text и constraints; служебные поля спецификации не попадают."""
    s = spec["subject"]
    obj = {"scene": s["summary"]}
    subs = [{"description": e["what"] + (f", {', '.join(e['attributes'])}" if e.get("attributes") else ""),
             **({"count": e["count"]} if e.get("count", 1) > 1 else {}),
             **({"position": e["position"]} if e.get("position") else {}),
             **({"relation": e["relation"]} if e.get("relation") else {}),
             **({"action": e["action"]} if e.get("action") else {})} for e in s.get("elements", [])]
    if subs:
        obj["subjects"] = subs
    if s.get("environment"):
        obj["background"] = s["environment"]
    if b.get("style"):
        obj["style"] = b["style"].rstrip(".")
    obj["color_palette"] = [f"{c['hex'].upper()} {c['name']}" + (f" ({pct(c['share'])})" if c.get("share") is not None else "")
                            + (f" on {c['applies_to']}" if c.get("applies_to") else "") for c in spec["palette"][:5]]
    if b.get("light"):
        obj["lighting"] = b["light"].rstrip(".")
    if spec.get("mood"):
        obj["mood"] = ", ".join(spec["mood"])
    if b.get("composition"):
        comp = {"framing": b["composition"].rstrip(".")}
        if b.get("text_zone"):
            comp["negative_space"] = b["text_zone"].rstrip(".")
        obj["composition"] = comp
    if b.get("camera"):
        obj["camera"] = b["camera"].rstrip(".")
    if spec.get("materials"):
        obj["materials"] = spec["materials"]
    if b.get("motion"):
        obj["motion"] = b["motion"]
    t = spec.get("text", {})
    if t.get("mode") == "in_image":
        obj["text"] = [{"content": x["text"], "language": x["language"], "position": x["position"],
                        **({"typography": x["typography"]} if x.get("typography") else {})} for x in t["strings"]]
    cons = " ".join(filter(None, [b.get("positive_constraints"), b.get("constraints")]))
    if cons:
        obj["constraints"] = cons
    # только при наличии новых полей
    for k in ("series_block", "effect_block", "references", "product", "product_colors", "anti_average", "quality"):
        if b.get(k):
            obj[k] = b[k]
    return json.dumps(obj, ensure_ascii=False, separators=(", ", ": "))


def to_ir(spec, b, fam):
    """MiniMax H3: «ключ: проза» (01 §9). Одна сцена (или [Shot n] из motion.shots), без реплик."""
    desc = [f"[Shot 1] {' '.join(x for x in (b.get('style'), b.get('composition'), b.get('subject')) if x)}".strip()]
    for k in ("environment", "light", "palette", "motion"):
        if b.get(k):
            desc.append(b[k])
    mo = spec.get("motion") or {}
    lines = []
    if mo.get("start_frame") and mo.get("end_frame"):
        lines.append(fam["fl2va_line"].format(end=float(mo["duration_s"])))
    elif mo.get("start_frame") and fam.get("i2va_line"):
        lines.append(fam["i2va_line"])
    body = " ".join(desc)
    if mo.get("shots"):
        body = body.replace("[Shot 1] [Shot 1] ", "[Shot 1] ")
    lines.append("integrated_multimodal_description: " + body)
    lines.append("overall_soundscape: " + ("quiet ambient room tone" if mo.get("audio") else "N/A"))
    lines.append("non_diegetic_music: N/A")
    return "\n".join(lines)


def _bbox(rect):
    x0, y0, x1, y1 = rect
    return [round(y0 * 1000), round(x0 * 1000), round(y1 * 1000), round(x1 * 1000)]


REGION_RECT = {"left-third": [0, 0, 0.34, 1], "right-third": [0.66, 0, 1, 1], "center": [0.25, 0.2, 0.75, 0.8],
               "top": [0, 0, 1, 0.34], "bottom": [0, 0.66, 1, 1], "full-frame": [0, 0, 1, 1]}


def to_ideogram_json(spec, b):
    """Ideogram 4: HLD → style_description → compositional_deconstruction (01 §11.4). Вне polza.
    bbox [y_min, x_min, y_max, x_max] 0–1000 из зоны текста и области субъекта; photo из камеры."""
    comp = spec["composition"]
    style = {"aesthetics": b["style"].rstrip(".") if b.get("style") else "", "lighting": (b.get("light") or "").rstrip("."),
             "medium": (spec.get("style") or {}).get("medium", "photograph"),
             "color_palette": [c["hex"].upper() for c in spec["palette"]][:16]}
    if b.get("camera") and (spec.get("style") or {}).get("medium", "photograph") == "photograph":
        style["photo"] = b["camera"].rstrip(".")
    elements = []
    region = comp.get("subject_region")
    for e in spec["subject"].get("elements", []):
        el = {"type": "obj", "desc": e["what"]}
        if region and region != "full-frame" and e.get("position"):
            el["bbox"] = _bbox(REGION_RECT[region])
        elements.append(el)
    t = spec.get("text", {})
    tz = comp.get("text_zone")
    if t.get("mode") == "in_image":
        for s in t["strings"]:
            el = {"type": "text", "text": s["text"].replace(" ", "\n") if len(s["text"]) > 14 else s["text"],
                  "desc": f"{s.get('typography', 'sans-serif')} {s['role']}, {s['position']}"}
            if tz and s["role"] == "headline":
                el["bbox"] = _bbox(tz["rect"])
            elements.append(el)
    bg = spec["subject"].get("environment", "")
    if tz:
        bg += f"; minimal, sparse, empty negative space on the {tz['side']}"
    obj = {"high_level_description": " ".join((b.get("subject") or spec["subject"]["summary"]).split()[:50]),
           "style_description": style,
           "compositional_deconstruction": {"background": bg, "elements": elements}}
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def context_phrase(spec):
    """Фраза контекста структурного промта: секция и класс страницы — `role.page_class` (слово контекста; в
    `role.page_type` лежит id типа страницы словаря site, в промт он не идёт). Без класса и у класса other — «a website»."""
    role = spec["role"]
    cls = role.get("page_class")
    if not cls or cls == "other":
        return f"{role['section']} image for a website"
    return f"{role['section']} image for {'an' if cls[:1] in 'aeiou' else 'a'} {cls} website"


def fibo_object(spec, b):
    """Bria FIBO structured_prompt (ключи — по значению по умолчанию Gen-API bria-fibo) [не проверено]."""
    s = spec["subject"]
    li = spec.get("light") or {}
    cam = spec.get("camera") or {}
    objs = []
    for e in s.get("elements", []):
        o = {"description": e["what"] + (f", {', '.join(e['attributes'])}" if e.get("attributes") else "")}
        if e.get("position") or e.get("relation"):
            o["location"] = e.get("position") or e.get("relation")
        if e.get("relation"):
            o["relationship"] = e["relation"]
        if e.get("action"):
            o["action"] = e["action"]
        cols = [c for c in spec["palette"] if c.get("applies_to") and c["applies_to"].split()[0] in e["what"]]
        if cols:
            o["shape_and_color"] = ", ".join(f"{c['name']} ({c['hex'].upper()})" for c in cols)
        objs.append(o)
    bg = s.get("environment", "")
    if b.get("text_zone"):
        bg = (bg + ". " if bg else "") + b["text_zone"]
    obj = {"short_description": " ".join(x for x in (b.get("subject"),) if x)[:600],
           "objects": objs,
           "background_setting": bg,
           "lighting": {k: v for k, v in {"conditions": " ".join(x for x in (li.get("quality"), li.get("source"), li.get("time_of_day")) if x),
                                          "direction": li.get("direction"), "shadows": li.get("interaction")}.items() if v},
           "aesthetics": {k: v for k, v in {"composition": (b.get("composition") or "").rstrip("."),
                                            "color_scheme": (b.get("palette") or "").rstrip("."),
                                            "mood_atmosphere": ", ".join(spec.get("mood", []))}.items() if v},
           "photographic_characteristics": {k: v for k, v in {"depth_of_field": cam.get("depth_of_field"),
                                                              "camera_angle": ANGLE_WORDS.get(spec["composition"].get("angle", ""), None),
                                                              "lens_focal_length": f"{cam['lens_mm']:g}mm" if cam.get("lens_mm") else None}.items() if v},
           "style_medium": (spec.get("style") or {}).get("medium", "photograph").replace("-", " "),
           "context": context_phrase(spec),
           "artistic_style": ", ".join((spec.get("style") or {}).get("anchors", []))}
    return {k: v for k, v in obj.items() if v}


# ---------------------------------------------------------------- правки

EDIT_CLOSINGS = {"nano-banana": "Keep everything else in the image exactly the same, preserving the original style, lighting, and composition.",
                 "gpt-image": "Keep all other aspects of the image unchanged."}


def _the(noun):
    """Именная группа с одним определителем: свой артикль снимается и ставится «the» («the floor lamp» не даёт
    «the the floor lamp»); своё местоимение или квантор (its, all, every …) остаётся как есть."""
    words = noun.split()
    first = words[0].lower() if words else ""
    if first in KEEP_OWN_DETERMINERS:
        return noun.strip()
    if first in ("the", "a", "an") and len(words) > 1:
        noun = noun.split(None, 1)[1]
    return f"the {noun.strip()}"


def extend_framing(spec, fam, opts, changes):
    """Кадрирование аутпейнта — предложения после инструкции extend: что видно в новых областях (`edit.changes`:
    target — область нового кадра, to — что в ней) и зона текста нового кадра (`composition.text_zone`)."""
    out = []
    for ch in changes:
        where = f" {ch['where']}" if ch.get("where") else ""
        val = f" ({ch['value']})" if ch.get("value") else ""
        out.append(sentence(f"{_the(ch['target'])}{where} shows {ch['to']}{val}"))
    zone = text_zone_phrase(spec, fam, opts.get("text_zone_style", "base"))
    if zone:
        out.append(zone)
    return out


def edit_prompt(spec, fam, fname, dfl, opts, warnings, changes=None):
    ed = spec["edit"]
    e = dfl.get("edit") or {}
    op = ed["operation"]
    changes = ed.get("changes", []) if changes is None else changes
    src_label = "the provided image" if not declared_refs(spec, "edit") else ref_label(fam, 1)
    out = []
    if op == "extend":
        cap_ = ed.get("caption") or spec["subject"]["summary"]
        framing = extend_framing(spec, fam, opts, changes)
        if fname == "qwen-image":     # шаблон переписчика Qwen: кадрирование — предложениями после описания исходника
            lead = "Extend the image beyond its boundaries using outpainting. The original caption is:"
            return " ".join([f"{lead} {_period(cap_)}"] + framing) if framing else f"{lead} {cap_}"
        out.append(f"Extend the scene of {src_label} to fill a {ed['target_ratio']} frame; keep the original image content "
                   f"unchanged and continue {cap_} naturally at the new edges.")
        out += framing
    elif op == "inpaint" and fname == "qwen-image":
        return f"Perform inpainting on this image. The original caption is: {ed.get('caption') or spec['subject']['summary']}"
    elif op == "restyle":
        out.append(f"Preserve the original composition of {src_label} but render it as {changes[0]['to'] if changes else spec['subject']['summary']}.")
    elif len(changes) > 1 and op in ("replace", "recolor", "add", "remove") and any(ch.get("op") for ch in changes):
        # явный op хотя бы у одного изменения → формула «make only these changes» (одинаковая во всех порциях цепочки)
        # смешанная правка — у каждого изменения свой глагол («change the sill to a fern» заменило бы подоконник)
        items = []
        for ch in changes:
            cop = ch.get("op") or op
            where = f" {ch['where']}" if ch.get("where") else ""
            val = f" ({ch['value']})" if ch.get("value") else ""
            if cop == "add":
                items.append(f"add {ch['to']}{val}{where}")
            elif cop == "remove":
                items.append(f"remove {_the(ch['target'])}{where}, showing {ch['to']} in its place")
            else:
                items.append(f"change the {ch['target']}{where} to {ch['to']}{val}")
        lead = "Using the provided image, make only these changes" if fname == "nano-banana" and src_label == "the provided image" \
            else "Make only these changes"
        out.append(f"{lead}: {'; '.join(items)}.")
        if any((ch.get("op") or op) in ("replace", "recolor") for ch in changes):
            out.append("Keep the position and size of every changed element exactly the same.")
    elif op in ("replace", "recolor") and len(changes) > 1:
        items = [f"the {ch['target']}{' ' + ch['where'] if ch.get('where') else ''} to {ch['to']}"
                 f"{' (' + ch['value'] + ')' if ch.get('value') else ''}" for ch in changes]
        lead = "Using the provided image, change only these elements" if fname == "nano-banana" and src_label == "the provided image" \
            else "Change only these elements"
        out.append(f"{lead}: {'; '.join(items)}.")
        out.append("Keep their positions and sizes exactly the same.")
    else:
        replaced_object = False          # «Keep its position…» — только после «Change only the X to Y»
        for ch in changes:
            where = f" {ch['where']}" if ch.get("where") else ""
            val = f" ({ch['value']})" if ch.get("value") else ""
            cop = ch.get("op") or op     # одиночное изменение со своей операцией
            if cop == "remove":
                out.append(f"Remove {_the(ch['target'])}{where}; in its place the frame shows {ch['to']}.")
            elif cop == "add":
                out.append(f"Add {ch['to']}{val}{where}.")
            elif op in ("text_replace",):
                out.append(f"Replace the text \"{ch['target']}\" with \"{ch['to']}\", keeping the same font, size, color and position.")
            elif op == "translate_text":
                out.append(f"Translate the {ch['target']} into {ch['to']}, keeping everything else the same.")
            elif op == "background_swap":
                out.append(f"Replace the background with {ch['to']}{val}; keep the subject, its edges and the lighting direction unchanged.")
            elif op == "relight":
                out.append(f"Relight the scene: {ch['to']}{val}.")
            else:   # replace / recolor
                prefix = "Using the provided image, change only" if fname == "nano-banana" and len(out) == 0 and src_label == "the provided image" else "Change only"
                out.append(f"{prefix} the {ch['target']}{where} to {ch['to']}{val}.")
                replaced_object = True
        # у «add»/«remove» прежнего места нет; у relight / background_swap / текста — тоже (свет — «replace»)
        if replaced_object:
            out.append(e.get("keep_position", "Keep its position and size exactly the same."))
    refs = references_phrase(spec, fam, dfl, "edit", start_index=2) if opts.get("refs", "declare") == "declare" else None
    if refs:
        out.insert(0, refs)
    if ed.get("visible_after"):
        out.append(sentence(f"After the change, the frame shows {ed['visible_after']}"))
    if ed.get("keep"):                  # артикль/местоимение в первом элементе — без своего «the» («Keep the the cup»)
        keep = list(ed["keep"])
        first = keep[0].split()[0].lower() if keep and keep[0].split() else ""
        if first in ("the", "a", "an"):
            keep[0] = keep[0].split(None, 1)[1] if len(keep[0].split()) > 1 else keep[0]
        lead = "Keep" if first in KEEP_OWN_DETERMINERS else "Keep the"
        out.append(sentence(f"{lead} {_join(keep)} unchanged"))
    out.append(EDIT_CLOSINGS.get(fname, e.get("closing", "Change nothing else.")))
    if ed.get("preserve_suffix", True) and op not in ("extend",):
        out.append(e.get("suffix", "Maintain the original composition and subject."))
    positive_excl, neg = exclusion_sentences(spec, fam, warnings, opts.get("negation", "family"), edit=True)
    if neg:
        out.append(" ".join(neg))
    return " ".join(x for x in out if x)


def edit_chain(spec, dialects=None):
    """Правка порциями ≤ defaults.edit.max_changes: список спецификаций-шагов."""
    dialects = dialects or load_dialects()
    mx = int((defaults(dialects).get("edit") or {}).get("max_changes", 5))
    ed = spec.get("edit") or {}
    ch = ed.get("changes", [])
    if len(ch) <= mx:
        return [spec]
    steps = []
    for i in range(0, len(ch), mx):
        s = copy.deepcopy(spec)
        s["edit"]["changes"] = ch[i:i + mx]
        s["id"] = f"{spec['id']}-step{i // mx + 1}"[:64]
        steps.append(s)
    return steps


# ---------------------------------------------------------------- параметры запроса polza (unified + явные ценовые)

def _res_num(v):
    m = re.match(r"(\d+(?:\.\d+)?)\s*([kKpP]?)", str(v))
    if not m:
        return 0.0
    n = float(m.group(1))
    return n * 1000 if m.group(2).lower() == "k" else n


def _nearest(vals, want):
    return min(vals, key=lambda v: (abs(_res_num(v) - _res_num(want)), _res_num(v)))


def resolution_dropped(model_id, res, channel=None):
    """Предупреждение: разрешение спецификации в задание не идёт — у модели нет такого параметра."""
    where = f" ({channel})" if channel else ""
    return (f"{model_id}{where}: output.resolution {res} в задание не идёт — в каталоге модели нет параметра разрешения; "
            f"модель отдаст своё разрешение, оно может быть ниже запрошенного")


def build_params(spec, model_id, fam, catalog, errors, warnings, mode=None, opts=None, prompt=None):
    """Параметры запроса polza только из тех, что есть в каталоге модели (01 §1.2); ценовые — явно (B §4)."""
    opts = opts or {}
    if fam.get("in_polza") is False:
        warnings.append(f"{model_id}: модель вне polza — параметры запроса не собираются")
        return {"aspect_ratio": spec["output"]["primary_ratio"]}
    m = catalog.get(model_id)
    if m is None:
        errors.append(f"{model_id} нет в снимке каталога")
        return {}
    cp = m.get("parameters") or {}
    out = {}
    ratio = spec["output"]["primary_ratio"]
    if mode == "outpaint" and (spec.get("edit") or {}).get("target_ratio"):
        ratio = spec["edit"]["target_ratio"]
    if "aspect_ratio" in cp:
        vals = cp["aspect_ratio"].get("values")
        if vals and ratio not in vals:
            errors.append(f"{model_id}: соотношение {ratio} не поддерживается ({vals})")
        else:
            out["aspect_ratio"] = ratio
    res = spec["output"].get("resolution")
    for key in ("image_resolution", "resolution"):
        if key in cp:
            vals = cp[key].get("values") or []
            if res and res in vals:
                out[key] = res
            elif res and vals:
                pick = _nearest(vals, res)
                warnings.append(f"{model_id}: {key} {res} нет в {vals}, беру {pick}")
                out[key] = pick
            elif vals:   # ценовой параметр — явно, самая дешёвая ступень
                out[key] = min(vals, key=_res_num)
    rmap = pcat.RESOLUTION_MAP.get(model_id)
    if res and not any(k in cp for k in ("image_resolution", "resolution")) and not (rmap and rmap[0] in cp):
        warnings.append(resolution_dropped(model_id, res))
    for key in ("quality", "mode"):
        if key in cp and (cp[key].get("values")):
            vals = cp[key]["values"]
            pick = None
            if rmap and rmap[0] == key and res:
                inv = {v: k for k, v in rmap[1].items()}
                pick = inv.get(res) or (inv.get(_nearest(list(inv), res)) if inv else None)
            if key == "mode" and opts.get("kling_mode"):
                pick = opts["kling_mode"]
            out[key] = pick if pick in vals else (cp[key].get("default") if cp[key].get("default") in vals else vals[0])
    mo = spec.get("motion")
    if mo:
        if "duration" in cp:
            vals = cp["duration"].get("values")
            d = str(int(mo["duration_s"]))
            lo, hi = cp["duration"].get("min"), cp["duration"].get("max")
            if vals and d not in vals:
                errors.append(f"{model_id}: длительность {d} с не из {vals}")
            elif (lo is not None and float(d) < lo) or (hi is not None and float(d) > hi):
                errors.append(f"{model_id}: длительность {d} с вне {lo}–{hi}")
            else:
                out["duration"] = d
        for key in ("generate_audio", "sound"):
            if key in cp:
                out[key] = "true" if mo.get("audio") else "false"
        if not mo.get("audio") and not any(k in cp for k in ("generate_audio", "sound")):
            # Veo (Gemini API «Always on»), Omni, Wan 2.5/2.6 («Only wan2.2 and wan2.1… silent»), Grok, H3 Max
            warnings.append(f"{model_id}: звук параметром не выключается (в каталоге нет generate_audio/sound) — дорожку "
                            f"снимать при кодировании (-an); словами — только уточнения (No dialogue. No music.)")
        if "fixed_lens" in cp:
            out["fixed_lens"] = "true" if mo["camera"]["move"] == "static" else "false"
        if "multi_shots" in cp:
            out["multi_shots"] = "true" if mo.get("shots") else "false"
        if "generationType" in cp:
            out["generationType"] = {"flf": "FIRST_AND_LAST_FRAMES_2_VIDEO", "i2v": "FIRST_AND_LAST_FRAMES_2_VIDEO",
                                     "ref2v": "REFERENCE_2_VIDEO"}.get(mode, "TEXT_2_VIDEO")
    if "enableTranslation" in cp:
        if prompt and CYR.search(prompt):
            warnings.append("Veo: кириллица в промте — enableTranslation оставлен true (KIE: «Only English prompts»); "
                            "надпись в кадре будет переведена")
            out["enableTranslation"] = "true"
        else:
            out["enableTranslation"] = "false"   # английский промт — без автоперевода терминов камеры (B, C2, D)
    for key in ("enhance_prompt", "enable_prompt_expansion", "isEnhance"):
        if key in cp:
            default = cp[key].get("default")
            on = opts.get("enhancer") == "on"
            out[key] = on if isinstance(default, bool) else ("true" if on else "false")
    if "negative_prompt" in cp:
        nouns = [e["what"] for e in spec.get("exclusions", []) if e["kind"] in ("object", "style", "artifact")]
        if nouns:
            out["negative_prompt"] = ", ".join(nouns)[: cp["negative_prompt"].get("max_length", 500)]
    if spec["output"].get("alpha"):
        if "background" in cp:
            out["background"] = "transparent"
            if "output_format" in cp:
                out["output_format"] = "png"
        else:
            errors.append(f"{model_id}: прозрачность не поддерживается в polza")
    seed = opts.get("seed")
    if seed is not None:
        if "seed" in cp:
            out["seed"] = int(seed)
        elif "seeds" in cp:
            out["seeds"] = 10000 + int(seed) % 90000
    # ступени нет в модели и ближайшая ниже запрошенной — если ступень ≥ запрошенной стоит столько же, берём её
    # (GA Omni: 360p = 720p = 1080p = 48 ₽ за 4 с; запрос 480p → 720p, а не 360p)
    for key in ("resolution", "image_resolution"):
        vals = (cp.get(key) or {}).get("values") or []
        picked = out.get(key)
        if not (res and picked and vals and res not in vals and _res_num(picked) < _res_num(res)):
            continue
        ups = sorted((v for v in vals if _res_num(v) >= _res_num(res)), key=_res_num)
        try:
            base = pcat.estimate(m, {"prompt": "x", **out}).get("rub")
            up = pcat.estimate(m, {"prompt": "x", **out, key: ups[0]}).get("rub") if ups else None
        except Exception:  # noqa: BLE001
            base = up = None
        if base is not None and up is not None and abs(up - base) < 1e-9:
            warnings.append(f"{model_id}: {key} {ups[0]} стоит столько же, сколько {picked} ({base:g} ₽) — беру {ups[0]} (≥ {res})")
            out[key] = ups[0]
    return out


def _abs_src(src, spec_path):
    if not src or re.match(r"^(https?|data):", src):
        return src
    p = pathlib.Path(src)
    if not p.is_absolute() and spec_path:
        p = pathlib.Path(spec_path).resolve().parent / p
    return str(p)


def collect_inputs(spec, fam, model_id, mode, spec_path=None):
    """images[] в порядке ссылок промта + маска. Возвращает (images, videos, mask, errors)."""
    mo = spec.get("motion") or {}
    images, videos, errs = [], [], []
    if mode in ("edit", "outpaint"):
        src = spec["edit"]["source"]
        r = ref_by_id(spec, src)
        images.append(_abs_src(r["src"] if r else src, spec_path))
    elif mode in ("flf",):
        images += [_abs_src(mo["start_frame"], spec_path), _abs_src(mo["end_frame"], spec_path)]
    elif mode == "i2v":
        images.append(_abs_src(mo["start_frame"], spec_path))
    for r in declared_refs(spec, mode):
        (videos if r.get("kind") == "video" else images).append(_abs_src(r["src"], spec_path))
    mask = None
    em = (spec.get("edit") or {}).get("mask")
    if em:
        want = ((fam.get("models") or {}).get(model_id) or {}).get("mask") or ""
        want_pol = "black=change" if want.startswith("black") else "white=change" if want.startswith("white") else \
            "alpha=change" if "alpha" in want or "прозрач" in want else None
        if not want_pol:
            errs.append(f"{model_id}: маска не поддерживается (нет mask в dialects/каталоге)")
        else:
            mask = {"src": _abs_src(em["src"], spec_path), "file_polarity": em["polarity"], "model_polarity": want_pol,
                    "invert": em["polarity"] != want_pol}
    return images, videos, mask, errs


def derive_mask(mask, out_dir):
    """Приводит маску к полярности модели (инверсия или альфа) — файл рядом с заданиями: masks/<имя>.<pol>.png."""
    src = pathlib.Path(mask["src"])
    if not mask["invert"]:
        return str(src)
    try:
        from PIL import Image, ImageOps
    except ImportError as e:  # pragma: no cover
        raise CompileError("инверсия маски требует Pillow (Python окружения скилла, scripts/install.sh)") from e
    out_dir = pathlib.Path(out_dir) / "masks"
    out_dir.mkdir(parents=True, exist_ok=True)
    dst = out_dir / f"{src.stem}.{mask['model_polarity'].split('=')[0]}.png"
    with Image.open(src) as im:
        if mask["file_polarity"] == "alpha=change":
            g = im.convert("RGBA").split()[-1]                      # альфа 0 = менять → белое = менять
            g = ImageOps.invert(g)
        else:
            g = im.convert("L")
            if {"white=change", "black=change"} == {mask["file_polarity"], mask["model_polarity"]}:
                g = ImageOps.invert(g)
        if mask["model_polarity"] == "alpha=change":
            white_change = g if mask["file_polarity"] != "black=change" else ImageOps.invert(g)
            rgba = Image.new("RGBA", g.size, (0, 0, 0, 255))
            rgba.putalpha(ImageOps.invert(white_change))
            rgba.save(dst)
        else:
            g.save(dst)
    return str(dst)


def catalog_check(model_raw, inp):
    """Та же проверка, что у polza.py estimate: coerce_input → validate → estimate."""
    params = model_raw.get("parameters") or (model_raw.get("top_provider") or {}).get("parameters") or {}
    inp2, notes = pcat.coerce_input(params, inp)
    issues = pcat.validate(model_raw, inp2, strict=True)
    try:
        est = pcat.estimate(model_raw, inp2)
    except Exception as e:  # noqa: BLE001
        est = {"rub": None, "warnings": [f"оценка не удалась: {e}"]}
    return inp2, issues, est, notes


# ---------------------------------------------------------------- каналы вне Media API polza

def route_params(task, channel, model_id):
    """Параметры варианта маршрута задачи для этой модели канала (routing.yaml: routes.<код>.options[].params)."""
    key = ("routing", str(ROUTING))
    if key not in _CACHE:
        try:
            _CACHE[key] = (yaml.safe_load(ROUTING.read_text(encoding="utf-8")) or {}).get("routes") or {}
        except FileNotFoundError:
            _CACHE[key] = {}
    for o in (_CACHE[key].get(task) or {}).get("options") or []:
        if o.get("channel") == channel and o.get("model") == model_id:
            return o.get("params") or {}
    return {}


def channel_catalog(channel):
    """Модели последнего снимка каталога канала: id → запись. Снимок — переменная из CHANNEL_CATALOGS (имя папки или
    путь), иначе последний в $DDD_HOME/cache/ai-media/<канал>/; снимка нет — пусто, и формат вывода решают маршрут и
    dialects.yaml."""
    if channel not in CHANNEL_CATALOGS:
        return {}
    env, fname = CHANNEL_CATALOGS[channel]
    ref = os.environ.get(env) or None
    key = ("channel-catalog", channel, ref)
    if key not in _CACHE:
        root = kbpaths.cache("ai-media", channel, create=False)
        if ref:
            cands = [pathlib.Path(ref), pathlib.Path(ref) / fname, root / ref / fname]
            path = next((c for c in cands if c.is_file()), None)
            if path is None:
                raise CompileError(f"снимок каталога канала {channel} не найден: {env}={ref}")
        else:
            dirs = sorted(d for d in root.iterdir() if (d / fname).is_file()) if root.is_dir() else []
            path = dirs[-1] / fname if dirs else None
        models = {}
        if path is not None:
            raw = load_json(path)
            models = {m["id"]: m for m in (raw["data"] if isinstance(raw, dict) else raw) if m.get("id")}
        _CACHE[key] = models
    return _CACHE[key]


def channel_output_format(channel, info, model_id, spec, errors, warnings):
    """Формат файла, который отдаёт канал: вариант маршрута задачи для этой модели, иначе запись модели в dialects.yaml,
    иначе png. Последнее слово — за каталогом канала: формат вне supported_output_formats модели канал отклоняет
    (векторная модель отдаёт только svg), поэтому он заменяется поддерживаемым."""
    route = route_params(spec.get("task"), channel, model_id).get("output_format")
    fmt = route or info.get("output_format") or "png"
    supported = (channel_catalog(channel).get(model_id) or {}).get("supported_output_formats") or []
    if supported and fmt not in supported:
        if route:
            warnings.append(f"{model_id} ({channel}): output_format {route} из маршрута {spec.get('task')} нет в каталоге "
                            f"канала {supported} — беру {supported[0]}; маршрут сверить с каталогом")
        fmt = supported[0]
    want = spec["output"].get("format")
    if want == "svg" and fmt != "svg":
        errors.append(f"{model_id} ({channel}): спецификация ждёт svg, модель отдаёт {fmt} — нужна векторная модель "
                      f"маршрута задачи")
    return fmt


def genapi_dims(ratio, max_px=1_000_000, step=16):
    a, b = (int(x) for x in ratio.split(":"))
    r = a / b
    w = int((max_px * r) ** 0.5) // step * step
    h = int(w / r) // step * step
    while w * h > max_px:
        w -= step
        h = int(w / r) // step * step
    return w, h


def channel_body(channel, chcfg, info, model_id, spec, prompt, dialect, b, images, mask, opts, errors, warnings):
    params = set(info.get("params") or [])
    ratio = spec["output"]["primary_ratio"]
    seed = opts.get("seed")
    body = {}
    if channel == "routerai":
        body = {"model": model_id, "prompt": prompt}
        if "n" in params:
            body["n"] = 1
        if "aspect_ratio" in params:
            body["aspect_ratio"] = ratio
        if "resolution" in params:
            body["resolution"] = spec["output"].get("resolution") or "1K"
        elif spec["output"].get("resolution"):
            warnings.append(resolution_dropped(model_id, spec["output"]["resolution"], channel))
        if "seed" in params and seed is not None:
            body["seed"] = int(seed)
        elif seed is not None:
            warnings.append(f"{model_id} (routerai): seed не поддерживается — повторы независимые")
        if "output_format" in params:
            body["output_format"] = channel_output_format(channel, info, model_id, spec, errors, warnings)
        if "quality" in params:
            body["quality"] = opts.get("quality", "medium")
        if spec["output"].get("alpha"):
            if "background" in params:
                body["background"] = "transparent"
            else:
                errors.append(f"{model_id} (routerai): прозрачность не поддерживается")
        if images:
            if "input_references" in params:
                body["input_references"] = [{"type": "image_url", "image_url": {"url": s}} for s in images]
            else:
                errors.append(f"{model_id} (routerai): референсы не поддерживаются")
        if mask:
            errors.append(f"{model_id} (routerai): маска — только openai/gpt-image-* (документация RouterAI)")
    elif channel == "genapi":
        if dialect == "fibo_json":
            body["structured_prompt"] = fibo_object(spec, b)
        else:
            body["prompt"] = prompt
        if "width" in params and "height" in params:
            body["width"], body["height"] = genapi_dims(ratio)
        if spec["output"].get("resolution") and "resolution" not in params:
            warnings.append(resolution_dropped(model_id, spec["output"]["resolution"], channel))
        if "aspect_ratio" in params:
            body["aspect_ratio"] = ratio
        if "seed" in params and seed is not None:
            body["seed"] = int(seed)
        for k, v in (info.get("fixed") or {}).items():
            if k in params:
                body[k] = v
        if images:
            if "image_urls" in params:
                body["image_urls"] = images
            elif "image_url" in params and len(images) == 1:
                body["image_url"] = images[0]
            else:
                errors.append(f"{model_id} (genapi): референсов {len(images)} — не поддерживается")
        if mask:
            if "mask_url" in params:
                body["mask_url"] = mask["src"]
                warnings.append(f"{model_id} (genapi): полярность маски не документирована [не проверено]")
            else:
                errors.append(f"{model_id} (genapi): маска не поддерживается")
        if "negative_prompt" in params:
            nouns = [e["what"] for e in spec.get("exclusions", []) if e["kind"] in ("object", "style", "artifact")]
            if nouns:
                body["negative_prompt"] = ", ".join(nouns)
    extra = opts.get("extra_body") or {}
    for k, v in extra.items():
        body[k] = v
        warnings.append(f"{model_id} ({channel}): «{k}» вне документированных параметров — гипотеза passthrough")
    unknown = [k for k in body if k not in params and k not in ("model", "prompt") and k not in extra]
    if unknown:
        errors.append(f"{model_id} ({channel}): параметры вне списка канала: {unknown}")
    return body


# ---------------------------------------------------------------- компиляция

DROP_PRIORITY = ["mood", "materials", "culture", "camera", "anti_average", "quality", "product_colors", "style",
                 "environment", "light"]


def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def render(spec, b, fam, fname, dialect, opts):
    if dialect == "prose":
        return to_prose(b, fam, opts)
    if dialect == "sections":
        return to_sections(b, fam, opts)
    if dialect == "json":
        return to_json(spec, b)
    if dialect == "ir":
        return to_ir(spec, b, fam)
    if dialect == "ideogram_json":
        return to_ideogram_json(spec, b)
    if dialect == "fibo_json":
        return json.dumps(fibo_object(spec, b), ensure_ascii=False, separators=(",", ":"))
    raise CompileError(f"неизвестный диалект {dialect}")


def compile_prompt(spec, model_id, dialect=None, dialects=None, catalog=None, *, channel="polza", options=None,
                   spec_path=None):
    dialects = dialects or load_dialects()
    catalog = catalog if catalog is not None else load_catalog()
    dfl = defaults(dialects)
    opts = compile_options(spec, options)
    channel = channel or "polza"
    ch = None if channel == "polza" else channel
    fname, fam = family_of(model_id, dialects, ch)
    errors, warnings = validate_spec(spec, model_id, dialects, catalog, channel=ch, options=options, spec_path=spec_path)
    if any(e.startswith("смысловые проверки остановлены") for e in errors):   # промт из такой спецификации не собрать
        raise CompileError(f"спецификация {spec.get('id')} не проходит схему — {'; '.join(errors[:3])}")
    if spec.get("edit") is not None and not (spec["edit"] or {}).get("operation"):
        raise CompileError(f"спецификация {spec.get('id')}: у edit нет operation — инструкция правки не собирается")
    dialect = dialect or fam["format"]
    allowed = [fam["format"]] + list(fam.get("alt_formats") or [])
    if dialect not in allowed:
        warnings.append(f"диалект {dialect} не входит в {allowed} для {fname}")
    mode = detect_mode(spec)
    mo = spec.get("motion") or {}
    rules, notes = [], []
    if opts.get("forbid_style") in ("sentence", "positive"):
        fam = {**fam, "motion_forbid": opts["forbid_style"]}
    b = blocks(spec, fam, warnings, opts=opts, dfl=dfl, fname=fname, mode=mode)
    if mo.get("start_frame") and (fam.get("i2v") or {}).get("motion_only", True) and opts.get("i2v", "motion_only") != "full":
        # image-to-video: только движение — сцену, свет и внешность задаёт стартовый кадр
        # (Vertex «Prompt for motion only», Wan «Motion + Camera movement», BFL «redescribing visible pixels invites
        # re-imagination», Runway «almost exclusively on motion»; 01 §12.2)
        b = {k: (v if k in ("motion", "positive_constraints", "constraints", "references", "quality") else None)
             for k, v in b.items()}
        warnings.append("i2v: в промт идёт только движение (сцена — из стартового кадра)")
        rules.append("i2v_motion_only")
    elif mo.get("start_frame"):
        warnings.append("i2v: плечо «пересказ сцены» (compile.i2v=full) — сцена описана вместе с движением")
        rules.append("i2v_full")
    dropped = []
    limit_list = []
    info = (fam["models"].get(model_id) or {}) if fam.get("models") else {}
    frames_via = info.get("frames_via")        # GA Omni — кадры полями *_url, теги preview не пишутся
    ms_cfg = fam.get("multishot") or {}
    if mo.get("shots") and ms_cfg:             # Kling API — n = 1–6, words ≤ 512, в мульти-шоте только стартовый кадр
        if ms_cfg.get("max_shots") and len(mo["shots"]) > ms_cfg["max_shots"]:
            errors.append(f"мульти-шот {fname}: {len(mo['shots'])} планов > {ms_cfg['max_shots']}")
        for n_, s_ in enumerate(mo["shots"], 1):
            w_ = ", ".join(x for x in (s_.get("framing"), s_.get("camera"), s_["action"]) if x)
            if ms_cfg.get("shot_max_chars") and len(w_) > ms_cfg["shot_max_chars"]:
                errors.append(f"мульти-шот {fname}: план {n_} — {len(w_)} символов > {ms_cfg['shot_max_chars']}")
        if ms_cfg.get("start_frame_only") and mo.get("end_frame"):
            errors.append(f"мульти-шот {fname}: только стартовый кадр (каталог: «start frame (multi-shot)»), end_frame убрать")
    for x in (info.get("max_prompt_chars"), fam.get("safe_max_prompt_chars"), info.get("doc_limit")):
        if x:
            limit_list.append(x)
    limit = min(limit_list) if limit_list else None

    def assemble(bb):
        if mode in ("edit", "outpaint"):
            return edit_prompt(spec, fam, fname, dfl, opts, warnings)
        try:
            p = render(spec, bb, fam, fname, dialect, opts)
        except (AttributeError, TypeError, KeyError) as e:   # JSON + motion у моделей картинок — ошибка, а не падение
            errors.append(f"диалект {dialect} не собирается для этой спецификации ({type(e).__name__}: {e})")
            return ""
        refs_cfg = fam.get("references") or {}
        if refs_cfg.get("declare") and mo.get("loop") == "first_last_same" and not frames_via:
            # Omni: объявление ролей медиа и закрывающая фраза (01 §3.9); через KIE — не проверено
            p = f"{refs_cfg['declare']}\n{p}\n{refs_cfg.get('closing_loop', '')}".strip()
        return p

    if mode in ("edit", "outpaint") and dialect != "prose":
        warnings.append(f"правка: диалект {dialect} заменён прозой (инструкция правки — связный текст)")
        dialect = "prose"
    prompt = assemble(b)
    if limit and len(prompt) > limit and opts.get("fit") == "drop" and mode not in ("edit", "outpaint"):
        for k in opts.get("drop_priority") or DROP_PRIORITY:
            if len(prompt) <= limit:
                break
            if b.get(k):
                b[k] = None
                dropped.append(k)
                prompt = assemble(b)
        if dropped:
            warnings.append(f"бюджет длины: выброшены блоки {dropped} → {len(prompt)} ≤ {limit}")
            rules.append("fit_drop")
    if limit and len(prompt) > limit:
        errors.append(f"длина промта {len(prompt)} > {limit} символов ({model_id}); не обрезаю")
    words = len(re.findall(r"[A-Za-zА-Яа-яЁё0-9#']+", prompt))
    if fam.get("max_words") and words > fam["max_words"]:
        errors.append(f"{words} слов > {fam['max_words']} (рекомендация вендора)")
    elif fam.get("target_words") and words > 300:
        warnings.append(f"{words} слов — длиннее «длинного» промта BFL (80–300)")
    refs_doc = fam.get("references") or {}
    if mode == "flf" and not (refs_doc.get("first_last") or refs_doc.get("last_frame")):
        if fname in ("seedance-2", "seedance-2-5"):
            warnings.append(f"{fname}: images — «референсы», строгий первый/последний кадр не гарантирован")
        else:
            warnings.append(f"{fname}: последний кадр в polza не документирован — i2v по первому кадру, петля — постобработкой")
            mode = "i2v"
            rules.append("flf_undocumented_to_i2v")
    if mode == "flf":   # модель без последнего кадра (images ≤ 1) — i2v по первому кадру, петля — постобработкой
        mimg = (((catalog.get(model_id) or {}).get("parameters") or {}).get("images") or {}).get("max") \
            if channel == "polza" else info.get("max_refs")
        if mimg is not None and mimg < 2:
            warnings.append(f"{model_id}: images ≤ {mimg} — последний кадр не передаётся; режим i2v по первому кадру, "
                            f"замыкание петли — постобработкой")
            mode = "i2v"
            rules.append("flf_to_i2v")
    images, videos, mask, in_errs = collect_inputs(spec, fam, model_id, mode, spec_path)
    errors += in_errs
    frame_fields = {}
    if frames_via and mode in ("flf", "i2v") and images:
        frame_fields[frames_via["first"]] = images[0]
        if mode == "flf" and len(images) > 1:
            frame_fields[frames_via["last"]] = images[1]
        images = images[len(frame_fields):]
        if images or videos:
            errors.append(f"{model_id}: {frames_via['first']} не сочетается с {', '.join(frames_via.get('exclusive_with', []))} "
                          f"(каталог) — референсы убрать или reference_mode: references без кадров")
        rules.append("frames_via_fields")
    if mode in ("edit", "outpaint"):
        n_ch = len((spec.get("edit") or {}).get("changes", []))
        mx = int(opts.get("max_changes") or (dfl.get("edit") or {}).get("max_changes", 5))
        if n_ch > mx:
            errors.append(f"правка: {n_ch} изменений > {mx} за вызов — разбей цепочкой (команда chain) [V:H6ZXujE1qBA 15:16]")
    result = {"model": model_id, "family": fname, "dialect": dialect, "prompt": prompt, "chars": len(prompt),
              "limit": limit, "params": {}, "errors": errors, "warnings": warnings,
              "mode": mode, "channel": channel, "images": images, "videos": videos, "mask": mask,
              "frame_fields": frame_fields, "price_rub": None, "catalog_issues": [], "notes": notes,
              "dropped_blocks": dropped}
    if frame_fields:
        warnings.append(f"{model_id}: кадры — полями {', '.join(frame_fields)}; локальный файл в поле polza.py загружает "
                        f"в хранилище сам перед отправкой")
    if channel == "polza":
        params = build_params(spec, model_id, fam, catalog, errors, warnings, mode=mode, opts=opts, prompt=prompt)
        result["params"] = params
        m = catalog.get(model_id)
        if m is not None and fam.get("in_polza") is not False:
            inp = {"prompt": prompt, **params, **frame_fields}
            if images:
                inp["images"] = list(images)
            if videos:
                inp["videos"] = list(videos)
            if mask:
                inp["mask_url"] = mask["src"]
            _, issues, est, cnotes = catalog_check(m, inp)
            result["catalog_issues"] = issues
            for i in issues:
                msg = f"каталог: {i['param']}: {i['msg']}"
                if i["level"] == "error":
                    errors.append(msg)
                elif i["level"] == "warn":
                    warnings.append(msg)
                else:
                    notes.append(msg)
            result["price_rub"] = est.get("rub")
            result["price_formula"] = est.get("formula")
    else:
        chcfg = dialects["channels"][channel]
        result["body"] = channel_body(channel, chcfg, info, model_id, spec, prompt, dialect, b, images, mask, opts,
                                      errors, warnings)
        result["price_rub"] = info.get("price_rub")
        result["params"] = {k: v for k, v in result["body"].items() if k not in ("prompt", "structured_prompt", "model")}
    result["passport"] = {
        "schema": "prompt-compile-passport/1", "compiler": VERSION, "compiled_at": dt.date.today().isoformat(),
        "spec_id": spec.get("id"), "spec_version": spec.get("spec_version"), "spec_sha256": canonical_sha(spec),
        "task": spec.get("task"), "mode": mode, "model": model_id, "channel": channel, "family": fname,
        "family_class": fam.get("class"), "dialect": dialect, "dialects_version": dialects.get("version"),
        "dialects_sha256": file_sha256(DIALECTS), "catalog_snapshot": _rootrel(catalog_file()),
        "catalog_sha256": file_sha256(catalog_file()),
        "options": {k: v for k, v in opts.items() if k not in ("extra_body",)}, "rules": rules,
        "dropped_blocks": dropped, "chars": len(prompt), "limit": limit, "words": words,
        "mask": ({k: v for k, v in mask.items() if k != "src"} if mask else None),
        "errors": len(errors), "warnings": len(warnings)}
    return result


def _rootrel(p):
    p = pathlib.Path(p).resolve()
    return str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)


def price_hint(fam, model_id, params):
    p = (fam["models"][model_id] or {}).get("price_rub")
    if isinstance(p, (int, float)):
        return p
    if isinstance(p, dict):
        r = params.get("image_resolution")
        if r in p:
            return p[r]
        nums = [v for v in p.values() if isinstance(v, (int, float))]
        return max(nums) if nums else None
    return None


# ---------------------------------------------------------------- варианты соотношений

def _ratio(r):
    a, b = (float(x) for x in r.split(":"))
    return a / b


def crop_box(master_ratio, target_ratio, focal, keep):
    """Прямоугольник кадра target внутри мастера (доли мастера) с фокусом по центру, внутри keep; None — не влезает.
    keep=None — ограничения нет, кадр по фокусной точке (не [0, 0, 1, 1]: иначе любой кроп — «аутпейнт»)."""
    r0, r1 = _ratio(master_ratio), _ratio(target_ratio)
    if abs(r0 - r1) < 1e-6:
        return [0.0, 0.0, 1.0, 1.0]
    focal = _point(focal)
    fx, fy = (focal or {}).get("x", 0.5), (focal or {}).get("y", 0.5)
    kx0, ky0, kx1, ky1 = keep or [fx, fy, fx, fy]
    if r1 < r0:                                  # уже мастера: полная высота, ширина r1/r0
        w = r1 / r0
        if kx1 - kx0 > w + 1e-9:
            return None
        x0 = min(max(fx - w / 2, kx1 - w, 0.0), kx0, 1 - w)
        x0 = max(0.0, min(x0, 1 - w))
        return [round(x0, 4), 0.0, round(x0 + w, 4), 1.0]
    h = r0 / r1                                  # шире мастера: полная ширина, высота r0/r1
    if ky1 - ky0 > h + 1e-9:
        return None
    y0 = min(max(fy - h / 2, ky1 - h, 0.0), ky0, 1 - h)
    y0 = max(0.0, min(y0, 1 - h))
    return [0.0, round(y0, 4), 1.0, round(y0 + h, 4)]


def _kept_share(zone, box):
    """Доля площади прямоугольника zone внутри box (доли мастера)."""
    w = max(0.0, min(zone[2], box[2]) - max(zone[0], box[0]))
    h = max(0.0, min(zone[3], box[3]) - max(zone[1], box[1]))
    area = (zone[2] - zone[0]) * (zone[3] - zone[1])
    return w * h / area if area > 0 else 1.0


def ratio_variants(spec):
    out = spec["output"]
    comp = spec.get("composition", {})
    master = out["primary_ratio"]
    safe = {z["ratio"]: z["keep_rect"] for z in comp.get("safe_zones", [])}
    plans = {v["ratio"]: v for v in out.get("variants", [])}
    ratios = list(out.get("aspect_ratios") or [master])
    ratios += [r for r in plans if r not in ratios]          # соотношения из output.variants тоже (4:5 generate)
    tz = (comp.get("text_zone") or {}).get("rect")
    fp = _point(comp.get("focal_point"))
    res = []
    for r in ratios:
        v = plans.get(r, {})
        strat = v.get("strategy") or ("generate" if r == master else "crop")
        box, with_tz = None, False
        if strat == "crop" and r not in safe and tz:
            # без safe_zone — сначала зона текста вместе с фокусом (телефонный мастер: текст сверху), не влезает — только фокус
            union = [min(tz[0], fp["x"]), min(tz[1], fp["y"]), max(tz[2], fp["x"]), max(tz[3], fp["y"])] if fp else list(tz)
            box = crop_box(master, r, fp, union)
            with_tz = box is not None
            box = box or crop_box(master, r, fp, None)
        elif strat == "crop":
            box = crop_box(master, r, comp.get("focal_point"), safe.get(r))
        note = ""
        if strat == "crop" and box is None:
            strat, note = "outpaint", "безопасная зона не помещается в кадр — аутпейнт"
        elif strat == "crop" and r not in safe:
            note = ("нет safe_zone для соотношения — кадр по " + ("фокусной точке" if fp else "центру")
                    + (" и зоне текста" if with_tz else ""))
        if strat == "crop" and box and tz and _kept_share(tz, box) < 0.9 - 1e-6:   # потеря зоны текста — видна, а не молча
            note = (note + "; " if note else "") + (f"в кадре {int(_kept_share(tz, box) * 100)} % зоны текста — "
                                                    "текст шаблоном или отдельная генерация")
        if strat == "crop" and r not in safe and comp.get("focal_point") is not None and _point(comp["focal_point"]) is None:
            note = (note + "; " if note else "") + "focal_point не объект {x, y} — кадр по центру"
        res.append({"ratio": r, "strategy": strat, "crop_box": box, "note": note})
    return res


# ---------------------------------------------------------------- задания

def _rel(path, out_dir):
    if not path or re.match(r"^(https?|data):", str(path)) or not out_dir:
        return path
    return os.path.relpath(path, out_dir)


def _topprovider(catalog, model_id):
    return ((catalog.get(model_id) or {}).get("top_provider") or {}).get("name")


def make_jobs(spec_paths, models, dialects_list=None, repeats=1, seeds=(), tag=None, agent=None, *,
              channel="polza", options=None, out_path=None, test=None, meta=None, variant_opts=None,
              provider=True, allow_missing_inputs=False, notes=None):
    """Задания для polza.py (JSONL) или каналов (.routerai.json / .genapi.json — список заданий).
    По умолчанию — одно задание на спецификацию и модель: диалект семейства, один вариант, без seed, тега и агента.
    dialects_list — формы промта (несколько — сравнение форм); repeats и seeds — повторы с сидами; tag — префикс тега,
    agent — поле agent задания (папка выходов polza.py); variant_opts — список словарей опций (плечи формы при одной
    спецификации): [{"order": "family"}, {"order": "shuffled"}]."""
    dialects, catalog = load_dialects(), load_catalog()
    out_dir = str(pathlib.Path(out_path).resolve().parent) if out_path else None
    jobs, skipped, series_blocks = [], [], {}
    for sp in spec_paths:
        spec = load_json(sp)
        sid = (spec.get("series") or {}).get("id") or (spec.get("role") or {}).get("series_id")
        blk = (spec.get("series") or {}).get("block") or (spec.get("style") or {}).get("series_block")
        if sid and blk:
            if sid in series_blocks and series_blocks[sid] != blk:
                skipped.append({"spec": spec["id"], "errors": [f"серия {sid}: блок стиля отличается от других "
                                                               f"спецификаций серии — дословно одинаковый блок"]})
                continue
            series_blocks[sid] = blk
        for mid in models:
            fname, fam = family_of(mid, dialects, None if channel == "polza" else channel)
            for d in (dialects_list or [fam["format"]]):
                for vo in (variant_opts or [{}]):
                    vo_all = {**(options or {}), **vo}
                    for k in range(repeats):
                        o = dict(vo_all)
                        seed = seeds[k % len(seeds)] if seeds else None
                        if seed is not None:
                            o["seed"] = seed
                        r = compile_prompt(spec, mid, d, dialects, catalog, channel=channel, options=o, spec_path=sp)
                        ff = r.get("frame_fields") or {}
                        missing = [s for s in r["images"] + r["videos"] + list(ff.values())
                                   if s and not re.match(r"^(https?|data):", s) and not pathlib.Path(s).exists()]
                        errs = list(r["errors"])
                        if missing and not allow_missing_inputs:
                            errs.append(f"нет входных файлов: {missing}")
                        if errs:
                            skipped.append({"spec": spec["id"], "model": mid, "dialect": d, "options": vo,
                                            "errors": errs})
                            break
                        vtag = "-".join(f"{v}" for v in vo.values()) if vo else ""
                        jtag = "-".join(x for x in (tag, spec["id"], d, vtag, mid.split("/")[-1], str(k + 1)) if x)
                        m = {"test": test, "spec": spec["id"], "dialect": d, "options": vo or None,
                             "compile": r["passport"], **(meta or {})}
                        if missing:
                            m["inputs_missing"] = [_rel(s, out_dir) for s in missing]
                        price = r.get("price_rub")
                        if channel == "polza":
                            inp = {"prompt": r["prompt"], **r["params"]}
                            if r["images"]:
                                inp["images"] = [_rel(s, out_dir) for s in r["images"]]
                            if r["videos"]:
                                inp["videos"] = [_rel(s, out_dir) for s in r["videos"]]
                            if r["mask"]:
                                inp["mask_url"] = _rel(derive_mask(r["mask"], out_dir or "."), out_dir)
                            if ff:   # кадры полями *_url: в задании — локальный путь от файла заданий
                                inp.update({k: _rel(v, out_dir) for k, v in ff.items()})
                                m["url_fields"] = {k: _rel(v, out_dir) for k, v in ff.items()}
                                m["prepare"] = ("подготовка не нужна: локальный файл в поле *_url polza.py загружает в "
                                                "хранилище сам перед отправкой; путь — от файла заданий")
                            if seed is not None and "seed" not in inp and "seeds" not in inp:
                                m["seed_note"] = "у модели нет seed в каталоге — повторы независимые (variant)"
                            if price is None:
                                price = price_hint(fam, mid, r["params"])
                            job = {"model": mid, "input": inp, "tag": jtag[:80], "agent": agent,
                                   "notes": notes or f"{spec['id']}: диалект {d}, вариант {k + 1}",
                                   "variant": k + 1, "max_rub": round(price * 1.25, 2) if price else None}
                            tp = _topprovider(catalog, mid)
                            if provider and tp:
                                job["provider"] = {"only": [tp], "allow_fallbacks": False}
                            job["meta"] = m
                        else:
                            chcfg = dialects["channels"][channel]
                            body = dict(r["body"])
                            for key in ("image_urls",):
                                if key in body:
                                    body[key] = [_rel(s, out_dir) for s in body[key]]
                            if "image_url" in body:
                                body["image_url"] = _rel(body["image_url"], out_dir)
                            if "input_references" in body:
                                for it in body["input_references"]:
                                    it["image_url"]["url"] = _rel(it["image_url"]["url"], out_dir)
                            path = chcfg["path"].replace("{network}", mid)
                            info = chcfg["models"][mid]
                            job = {"channel": channel, "method": chcfg.get("method", "POST"), "path": path, "body": body,
                                   "tag": jtag[:80], "agent": agent, "variant": k + 1,
                                   "max_rub": round((price or 0) * 1.25, 2) or None, "price_rub": price,
                                   "price_source": f"{chcfg.get('price_source')}; {info.get('price_unit', '')}".strip("; "),
                                   "docs": chcfg.get("docs"),
                                   "notes": notes or f"{spec['id']}: диалект {d}, вариант {k + 1}", "meta": m}
                        if not agent:           # без агента polza.py и mp_client.py берут свой (--agent, иначе unknown)
                            job.pop("agent")
                        jobs.append(job)
    return jobs, skipped


def write_jobs(jobs, out, channel="polza"):
    p = pathlib.Path(out)
    p.parent.mkdir(parents=True, exist_ok=True)
    if channel == "polza":
        p.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in jobs) + "\n", encoding="utf-8")
    else:
        p.write_text(json.dumps(jobs, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- CLI

def parse_opts(items):
    out = {}
    for it in items or []:
        k, _, v = it.partition("=")
        if v.lower() in ("true", "false"):
            v = v.lower() == "true"
        elif re.fullmatch(r"-?\d+", v):
            v = int(v)
        elif v.startswith(("{", "[")):
            v = json.loads(v)
        out[k] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("validate"); a.add_argument("spec"); a.add_argument("--model"); a.add_argument("--channel", default="polza")
    c = sub.add_parser("compile"); c.add_argument("spec"); c.add_argument("--model", required=True)
    c.add_argument("--dialect"); c.add_argument("--json", action="store_true"); c.add_argument("--channel", default="polza")
    c.add_argument("--opt", action="append")
    j = sub.add_parser("jobs", help="задания для polza.py или каналов: по умолчанию одно на спецификацию и модель")
    j.add_argument("specs", nargs="+"); j.add_argument("--models", required=True, help="модели через запятую")
    j.add_argument("--dialects", help="формы промта через запятую (по умолчанию — диалект семейства модели)")
    j.add_argument("--repeats", type=int, default=1, help="вариантов на форму (по умолчанию 1)")
    j.add_argument("--seeds", help="сиды повторов через запятую (по умолчанию без seed)")
    j.add_argument("--tag", help="префикс тега задания"); j.add_argument("--out", help="файл заданий (без ключа — stdout)")
    j.add_argument("--agent", help="поле agent задания — папка выходов polza.py (по умолчанию — агент polza.py)")
    j.add_argument("--channel", default="polza"); j.add_argument("--opt", action="append")
    j.add_argument("--test", help="метка meta.test задания"); j.add_argument("--meta", help="JSON в meta задания")
    j.add_argument("--no-provider", action="store_true"); j.add_argument("--allow-missing-inputs", action="store_true")
    ch = sub.add_parser("chain"); ch.add_argument("spec"); ch.add_argument("--model", required=True)
    rt = sub.add_parser("ratios"); rt.add_argument("spec")
    mx = sub.add_parser("matrix"); mx.add_argument("specs", nargs="+"); mx.add_argument("--models")
    args = ap.parse_args(argv)
    if args.cmd == "validate":
        dialects, catalog = load_dialects(), (load_catalog() if args.model else None)
        ch_ = None if args.channel == "polza" else args.channel
        errs, warns = validate_spec(load_json(args.spec), args.model, dialects, catalog, channel=ch_, spec_path=args.spec)
        for w in warns:
            print("предупреждение:", w)
        for e in errs:
            print("ошибка:", e)
        print("OK" if not errs else f"ошибок: {len(errs)}")
        return 0 if not errs else 1
    if args.cmd == "compile":
        r = compile_prompt(load_json(args.spec), args.model, args.dialect, channel=args.channel,
                           options=parse_opts(args.opt), spec_path=args.spec)
        if args.json:
            print(json.dumps(r, ensure_ascii=False, indent=1))
        else:
            print(f"// {r['model']} · {r['family']} · {r['dialect']} · {r['chars']}/{r['limit']} символов")
            print(r["prompt"])
            print("params:", json.dumps(r["params"], ensure_ascii=False))
            if r.get("images"):
                print("images:", json.dumps(r["images"], ensure_ascii=False))
            if r.get("price_rub") is not None:
                print(f"цена по каталогу: {r['price_rub']} ₽")
            for w in r["warnings"]:
                print("предупреждение:", w)
            for e in r["errors"]:
                print("ошибка:", e)
        return 0 if not r["errors"] else 1
    if args.cmd == "jobs":
        seeds = tuple(int(x) for x in args.seeds.split(",")) if args.seeds else ()
        dialects_list = args.dialects.split(",") if args.dialects else None
        jobs, skipped = make_jobs(args.specs, args.models.split(","), dialects_list, args.repeats, seeds,
                                  args.tag, args.agent, channel=args.channel, options=parse_opts(args.opt),
                                  out_path=args.out, test=args.test, meta=json.loads(args.meta) if args.meta else None,
                                  provider=not args.no_provider, allow_missing_inputs=args.allow_missing_inputs)
        if args.out:
            write_jobs(jobs, args.out, args.channel)
        else:
            sys.stdout.write("\n".join(json.dumps(x, ensure_ascii=False) for x in jobs) + "\n")
        for s in skipped:
            print("пропущено:", json.dumps(s, ensure_ascii=False), file=sys.stderr)
        print(f"заданий: {len(jobs)}, пропущено плеч: {len(skipped)}", file=sys.stderr)
        return 0
    if args.cmd == "chain":
        spec = load_json(args.spec)
        steps = edit_chain(spec)
        for i, s in enumerate(steps, 1):
            r = compile_prompt(s, args.model, spec_path=args.spec)
            src = "исходник" if i == 1 or spec["edit"].get("chain") == "from_source" else f"результат шага {i - 1}"
            print(f"// шаг {i}/{len(steps)} · вход: {src} · {r['chars']} симв.")
            print(r["prompt"])
            for e in r["errors"]:
                print("ошибка:", e)
        return 0
    if args.cmd == "ratios":
        for v in ratio_variants(load_json(args.spec)):
            print(json.dumps(v, ensure_ascii=False))
        return 0
    if args.cmd == "matrix":
        dialects, catalog = load_dialects(), load_catalog()
        models = args.models.split(",") if args.models else [m for f in dialects["families"].values()
                                                             if f.get("in_polza") is not False for m in f["models"]]
        print("| spec | model | dialect | chars | limit | errors |")
        print("|---|---|---|---|---|---|")
        for sp in args.specs:
            spec = load_json(sp)
            for mid in models:
                fname, fam = family_of(mid, dialects)
                for d in [fam["format"]] + list(fam.get("alt_formats") or []):
                    r = compile_prompt(spec, mid, d, dialects, catalog, spec_path=sp)
                    print(f"| {spec['id']} | `{mid}` | {d} | {r['chars']} | {r['limit']} | "
                          f"{'; '.join(r['errors'])[:120] or '—'} |")
        return 0


if __name__ == "__main__":
    # ошибка компиляции (модель канала вне dialects.yaml и т. п.) и нечитаемый файл входа — сообщением, без трассировки
    try:
        sys.exit(main())
    except CompileError as e:
        print(f"ошибка компиляции: {e}", file=sys.stderr)
        sys.exit(2)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ошибка входа: {e}", file=sys.stderr)
        sys.exit(2)
