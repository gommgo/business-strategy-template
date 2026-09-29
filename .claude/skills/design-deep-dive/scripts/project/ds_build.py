#!/usr/bin/env python3
"""ds_build — производные дизайн-системы продукта из токенов DTCG и проверка их свежести и формата токенов.

Источник правды значений ДС — токены `docs/projects/<slug>/design/system.tokens.json` (DTCG 2025.10); проза —
`design/DESIGN.md`. Из них в одну сторону собираются производные (канон — `docs/projects/_template/design/README.md`,
разделы «ДС» и «Производные»); руками их не правят:

  design/system.tokens.css                   CSS-переменные для kit и кода: имя переменной — путь токена через дефис
                                             (`color.bg.canvas` → `--color-bg-canvas`); алиасы разрешены до значения;
                                             составной типографический токен — пять переменных `-family`, `-size`,
                                             `-leading`, `-weight`, `-tracking`; режимы — блоки темы
                                             (`[data-theme]` и `prefers-color-scheme`), сокращённого движения
                                             (`[data-motion]` и `prefers-reduced-motion`), плотности (`[data-density]`),
                                             в блок режима идут все токены, чьё значение в режиме другое (ui 09/04 §5)
  design/DESIGN.md — передняя часть          YAML между метками `---` в начале файла (формат DESIGN.md, ui 12/04 §2.3):
                                             colors, typography, rounded, spacing, прочие токены `x-tokens`, режимы
                                             `x-modes`, узкая ширина `x-narrow`; проза после меток не трогается
  design/_design-system/project/tokens.json  токены артефакта Design System списками по семействам (cd 05/01 §3.2):
                                             color с темами, type (families → `--font-<ключ>`, groups со стилями),
                                             spacing, radius, shadow и свои семейства по первому сегменту пути
  design/_design-system/project/README.md    бренд-бук артефакта — проза DESIGN.md без передней части

Узкая ширина: ниже первой границы `breakpoint.*` основной текст `type.body` — не меньше 16 px в любом пресете
(ux/09-mobile/03-mobile-content-tables-forms-dashboards.md §7.1, строка NU-15 `kb/common/canon.tsv`): сборка кладёт это
значение в блок `@media (width < <граница>)` CSS и в `x-narrow` передней части; мобильное приложение берёт основной
кегль оттуда же.

Что не идёт в артефакт: примитивы (`primitive.*` — холст и компоненты берут значения ролей) и движение (группы
`motion*`, типы duration, cubicBezier, transition — у формата токенов артефакта нет семейства движения, длительности и
кривые задаёт `components/bundle.css`). Поля артефакта, которых нет в DTCG, — расширение
`$extensions["org.design-deep-dive.artifact"]`: у токена `family` (семейство артефакта), у типографического токена
`group` и `sample`; в корне `name` (имя системы) и `families.<семейство>.note`. `usage` токена артефакта —
`$description`
токена DTCG. `example: true` в корне токенов — пометка иллюстрации (фикстуры), она переходит в производный tokens.json.

    ds_build build <slug> [--repo DIR] [--out DIR] [--json]    собрать производные; --out DIR → DIR/docs/projects/…
    ds_build check <slug> [--repo DIR] [--json]                формат DTCG и свежесть производных; ничего не пишет
    ds_build show  <slug> [--repo DIR] [--json]                токены: путь, имя переменной, тип, значения по режимам
    ds_build --selftest                                        без сети: разбор, сборка, фикстура cabinet-ds

Правила (`.claude/skills/design-audit/references/rules.md`):
  R-STRUCT-006  формат DTCG схемой (группы, `$type`, форма `$value` по типу, алиасы `{…}` ведут в токен того же типа,
                без циклов; значения режимов; одна шкала space.*)         error; warning — вторая шкала, лимит семейств
  R-FRESH-001   system.tokens.css, передняя часть DESIGN.md, tokens.json и README артефакта равны сборке байт в байт
                (хвост README, который дописывает страница артефакта, — не расхождение)   error; нет прозы — warning
Код выхода: 0 — нет error, 1 — есть error, 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402
import findings as F  # noqa: E402

EXT_MODES = "org.ui-research.modes"
EXT_LLM = "org.ui-research.llm"
EXT_REDUCE = "org.creative-research.reduce"                 # сокращённое движение расширения страниц сайта
EXT_FLUID = "org.creative-research.fluid"                   # fluid-значение clamp() расширения страниц
EXT_CSS = "org.creative-research.css"                       # готовое CSS-значение расширения страниц
EXT_ART = "org.design-deep-dive.artifact"                   # поля артефакта Design System, которых нет в DTCG

NARROW_BODY_MIN_PX = 16     # ux/09-mobile/03-mobile-content-tables-forms-dashboards.md §7.1 (canon.tsv, NU-15)
REM_PX = 16

TYPES = ("color", "dimension", "fontFamily", "fontWeight", "duration", "cubicBezier", "number", "strokeStyle", "border",
         "transition", "shadow", "gradient", "typography")
MOTION_TYPES = ("duration", "cubicBezier", "transition")
THEMES = {"light": "Светлая", "dark": "Тёмная"}
DENSITY = ("compact", "comfortable")
REDUCED = "reduced"
BASE_FAMILIES = ("color", "type", "spacing", "radius", "shadow")
FAMILY_OF_GROUP = {"color": "color", "space": "spacing", "radius": "radius", "shadow": "shadow", "elevation": "shadow"}
OWN_FAMILIES_MAX = 12                                        # своих семейств у артефакта (cd 05/01 §3.2)
GENERIC_FONTS = ("serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "emoji", "math", "fangsong",
                 "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded")
FONT_WEIGHTS = {"thin": 100, "hairline": 100, "extra-light": 200, "ultra-light": 200, "light": 300, "normal": 400,
                "regular": 400, "book": 400, "medium": 500, "semi-bold": 600, "demi-bold": 600, "bold": 700,
                "extra-bold": 800, "ultra-bold": 800, "black": 900, "heavy": 900, "extra-black": 950,
                "ultra-black": 950}
ALIAS = re.compile(r"^\{([^{}]+)\}$")
NAME = re.compile(r"^[^$.{}][^.{}]*$")
PAGE_TAIL = "Consuming this system"                         # хвост README, который дописывает страница артефакта
FM = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
KIND = "design-system"


# ------------------------------------------------------------------ схема формата DTCG 2025.10

def _alias():
    return {"type": "string", "pattern": r"^\{[^{}]+\}$"}


def _v(t):
    return {"$ref": f"#/$defs/v-{t}"}


def _or_alias(schema):
    return {"anyOf": [{"$ref": "#/$defs/alias"}, schema]}


_LAYER = {"type": "object", "required": ["color", "offsetX", "offsetY", "blur", "spread"],
          "additionalProperties": False,
          "properties": {"color": _v("color"), "offsetX": _v("dimension"), "offsetY": _v("dimension"),
                         "blur": _v("dimension"), "spread": _v("dimension"), "inset": {"type": "boolean"}}}
_ROOT_NAME = r"^(?!example$)[^$.{}][^.{}]*$"                # в корне `example` — пометка иллюстрации, не токен
_NODE_NAME = r"^[^$.{}][^.{}]*$"
_META = {"$type": {"enum": list(TYPES)}, "$description": {"type": "string"}, "$extensions": {"type": "object"},
         "$deprecated": {"type": ["boolean", "string"]}}

DTCG_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "urn:app-design:design-deep-dive:dtcg-format:2025.10",
    "title": "Формат токенов DTCG 2025.10: группы, токены, форма $value по типу",
    "$ref": "#/$defs/root",
    "$defs": {
        "root": {"type": "object", "additionalProperties": False,
                 "properties": {"$schema": {"type": "string"}, "$description": {"type": "string"},
                                "$extensions": {"type": "object"}, "example": {"type": "boolean"}},
                 "patternProperties": {_ROOT_NAME: {"$ref": "#/$defs/node"}}},
        "node": {"if": {"type": "object", "required": ["$value"]}, "then": {"$ref": "#/$defs/token"},
                 "else": {"$ref": "#/$defs/group"}},
        "token": {"type": "object", "required": ["$value"], "additionalProperties": False,
                  "properties": dict(_META, **{"$value": {}})},
        "group": {"type": "object", "additionalProperties": False,
                  "properties": dict(_META, **{"$extends": {"$ref": "#/$defs/alias"}}),
                  "patternProperties": {_NODE_NAME: {"$ref": "#/$defs/node"}}},
        "alias": _alias(),
        "v-color": _or_alias({
            "type": "object", "required": ["colorSpace", "components"], "additionalProperties": False,
            "properties": {
                "colorSpace": {"enum": ["srgb", "srgb-linear", "hsl", "hwb", "lab", "lch", "oklab", "oklch",
                                        "display-p3", "a98-rgb", "prophoto-rgb", "rec2020", "xyz-d65", "xyz-d50"]},
                "components": {"type": "array", "minItems": 3, "maxItems": 3,
                               "items": {"anyOf": [{"type": "number"}, {"const": "none"}]}},
                "alpha": {"type": "number", "minimum": 0, "maximum": 1},
                "hex": {"type": "string", "pattern": "^#[0-9a-fA-F]{6}$"}}}),
        "v-dimension": _or_alias({"type": "object", "required": ["value", "unit"], "additionalProperties": False,
                                  "properties": {"value": {"type": "number"}, "unit": {"enum": ["px", "rem"]}}}),
        "v-duration": _or_alias({"type": "object", "required": ["value", "unit"], "additionalProperties": False,
                                 "properties": {"value": {"type": "number"}, "unit": {"enum": ["ms", "s"]}}}),
        "v-fontFamily": _or_alias({"anyOf": [{"type": "string", "minLength": 1},
                                             {"type": "array", "minItems": 1,
                                              "items": {"type": "string", "minLength": 1}}]}),
        "v-fontWeight": _or_alias({"anyOf": [{"type": "number", "minimum": 1, "maximum": 1000},
                                             {"enum": sorted(FONT_WEIGHTS)}]}),
        "v-cubicBezier": _or_alias({"type": "array", "minItems": 4, "maxItems": 4,
                                    "prefixItems": [{"type": "number", "minimum": 0, "maximum": 1}, {"type": "number"},
                                                    {"type": "number", "minimum": 0, "maximum": 1},
                                                    {"type": "number"}]}),
        "v-number": _or_alias({"type": "number"}),
        "v-strokeStyle": _or_alias({"anyOf": [
            {"enum": ["solid", "dashed", "dotted", "double", "groove", "ridge", "outset", "inset"]},
            {"type": "object", "required": ["dashArray", "lineCap"], "additionalProperties": False,
             "properties": {"dashArray": {"type": "array", "items": _v("dimension")},
                            "lineCap": {"enum": ["round", "butt", "square"]}}}]}),
        "v-border": _or_alias({"type": "object", "required": ["color", "width", "style"], "additionalProperties": False,
                               "properties": {"color": _v("color"), "width": _v("dimension"),
                                              "style": _v("strokeStyle")}}),
        "v-transition": _or_alias({"type": "object", "required": ["duration", "delay", "timingFunction"],
                                   "additionalProperties": False,
                                   "properties": {"duration": _v("duration"), "delay": _v("duration"),
                                                  "timingFunction": _v("cubicBezier")}}),
        "v-shadow": _or_alias({"anyOf": [_LAYER, {"type": "array", "items": {"anyOf": [{"$ref": "#/$defs/alias"},
                                                                                        _LAYER]}}]}),
        "v-gradient": _or_alias({"type": "array", "items": {"anyOf": [{"$ref": "#/$defs/alias"}, {
            "type": "object", "required": ["color", "position"], "additionalProperties": False,
            "properties": {"color": _v("color"), "position": _or_alias({"type": "number", "minimum": 0,
                                                                        "maximum": 1})}}]}}),
        "v-typography": _or_alias({"type": "object", "additionalProperties": False,
                                   "required": ["fontFamily", "fontSize", "fontWeight", "letterSpacing", "lineHeight"],
                                   "properties": {"fontFamily": _v("fontFamily"), "fontSize": _v("dimension"),
                                                  "fontWeight": _v("fontWeight"), "letterSpacing": _v("dimension"),
                                                  "lineHeight": _v("number")}}),
    },
}
# тип подзначения составного токена — для сверки алиасов внутри значения
SUBTYPES = {"typography": {"fontFamily": "fontFamily", "fontSize": "dimension", "fontWeight": "fontWeight",
                           "letterSpacing": "dimension", "lineHeight": "number"},
            "border": {"color": "color", "width": "dimension", "style": "strokeStyle"},
            "transition": {"duration": "duration", "delay": "duration", "timingFunction": "cubicBezier"},
            "shadow": {"color": "color", "offsetX": "dimension", "offsetY": "dimension", "blur": "dimension",
                       "spread": "dimension"},
            "gradient": {"color": "color", "position": "number"}}


def _jsonschema():
    try:
        import jsonschema  # noqa: F401
        return jsonschema
    except ImportError as e:
        raise F.ToolError("нужен jsonschema: $DDD_HOME/venv/bin/python (scripts/install.sh)") from e


def _reexec_venv(script=None):
    """Без jsonschema в текущем Python — перезапуск утилиты script в Python окружения скилла (один раз)."""
    import importlib.util
    if importlib.util.find_spec("jsonschema") is not None:
        return
    py = kbpaths.python()
    in_venv = Path(sys.prefix).resolve() == kbpaths.venv().resolve()   # у venv python — ссылка на системный
    if os.environ.get("DDD_DS_VENV") or not Path(py).exists() or in_venv:
        return
    os.environ["DDD_DS_VENV"] = "1"
    os.execv(py, [py, str(Path(script or __file__).resolve())] + sys.argv[1:])


# ------------------------------------------------------------------ модель токенов

def esc(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def pointer(path, *more):
    return "/" + "/".join(esc(p) for p in tuple(path) + more)


@dataclass
class Issue:
    pointer: str
    message: str
    severity: str = "error"


@dataclass
class Token:
    path: tuple
    raw: dict
    type: str | None = None
    ancestors: list = field(default_factory=list)          # группы от корня к токену (словари)

    @property
    def name(self):
        """Имя CSS-переменной без «--» — путь через дефис."""
        return "-".join(self.path)

    @property
    def pointer(self):
        return pointer(self.path)

    @property
    def value(self):
        return self.raw.get("$value")

    @property
    def description(self):
        d = self.raw.get("$description")
        return d if isinstance(d, str) else ""

    def ext(self, key):
        e = self.raw.get("$extensions")
        return e.get(key) if isinstance(e, dict) else None

    def mode_entries(self):
        """[(режим, значение, место)]: `org.ui-research.modes` и сокращённое движение расширения страниц."""
        out = []
        m = self.ext(EXT_MODES)
        if isinstance(m, dict):
            out += [(k, v, f"$extensions/{EXT_MODES}/{esc(k)}") for k, v in m.items()]
        r = self.ext(EXT_REDUCE)
        if r is not None and not any(k == REDUCED for k, _, _ in out):
            out.append((REDUCED, r, f"$extensions/{EXT_REDUCE}"))
        return out

    def modes(self):
        """{режим: значение} (`reduced` — и из расширения страниц)."""
        return {k: v for k, v, _ in self.mode_entries()}

    def art(self, key):
        """Поле артефакта: у токена, иначе у ближайшей группы (`$extensions.org.design-deep-dive.artifact`)."""
        for node in [self.raw] + list(reversed(self.ancestors)):
            e = node.get("$extensions") if isinstance(node, dict) else None
            a = e.get(EXT_ART) if isinstance(e, dict) else None
            if isinstance(a, dict) and key in a:
                return a[key]
        return None


class Tokens:
    """Разобранный файл токенов DTCG: токены по порядку документа, разрешение алиасов и режимов."""

    def __init__(self, data):
        self.data = data if isinstance(data, dict) else {}
        self.list = []
        self.by_path = {}
        self.groups = {}                                     # путь группы → словарь
        self.structure = []                                  # замечания обхода (не токен и не группа)
        self._walk(self.data, (), [], None)
        for t in self.list:
            if t.type is None:
                t.type = self._alias_type(t, set())

    def _walk(self, node, path, ancestors, inherited):
        for key, val in node.items():
            if key.startswith("$") or (not path and key == "example"):
                continue
            p = path + (key,)
            if not isinstance(val, dict):
                self.structure.append(Issue(pointer(p), f"`{'.'.join(p)}` — не токен и не группа: ожидается объект"))
                continue
            if "$value" in val:
                ty = val.get("$type") if val.get("$type") in TYPES else inherited
                t = Token(p, val, ty, list(ancestors))
                self.list.append(t)
                self.by_path[p] = t
            else:
                self.groups[p] = val
                ty = val.get("$type") if val.get("$type") in TYPES else inherited
                self._walk(val, p, ancestors + [val], ty)

    def get(self, ref):
        """Токен по пути `a.b.c` (или None)."""
        return self.by_path.get(tuple(str(ref).split(".")))

    def _alias_type(self, t, seen):
        m = ALIAS.match(t.value) if isinstance(t.value, str) else None
        if not m or t.path in seen:
            return None
        seen.add(t.path)
        target = self.get(m.group(1))
        if target is None:
            return None
        return target.type or self._alias_type(target, seen)

    # -- разрешение значений

    def in_mode(self, t, mode):
        if mode:
            modes = t.modes()
            if mode in modes:
                return modes[mode]
        return t.value

    def resolve(self, value, mode=None, stack=()):
        """Значение без алиасов: алиас → значение цели в том же режиме (транзитивно); составные — по частям.
        Алиас в пустоту или цикл — ValueError."""
        if isinstance(value, str):
            m = ALIAS.match(value)
            if m:
                ref = m.group(1)
                if ref in stack:
                    raise ValueError("цикл алиасов: " + " → ".join(stack + (ref,)))
                target = self.get(ref)
                if target is None:
                    raise ValueError(f"алиас {{{ref}}} ведёт в пустоту")
                return self.resolve(self.in_mode(target, mode), mode, stack + (ref,))
            return value
        if isinstance(value, dict):
            if "colorSpace" in value:                        # цвет — лист
                return value
            if set(value) == {"value", "unit"}:
                return value
            return {k: self.resolve(v, mode, stack) for k, v in value.items()}
        if isinstance(value, list):
            return [self.resolve(v, mode, stack) for v in value]
        return value

    def value(self, t, mode=None):
        return self.resolve(self.in_mode(t, mode), mode, (".".join(t.path),))

    def mode_names(self):
        out = []
        for t in self.list:
            for m in t.modes():
                if m not in out:
                    out.append(m)
        return out


# ------------------------------------------------------------------ проверка формата (R-STRUCT-006)

def validate(data):
    """Замечания формата DTCG: структура схемой, тип каждого токена, форма значений по типу, алиасы, режимы."""
    js = _jsonschema()
    issues = []
    if not isinstance(data, dict):
        return [Issue("", "корень файла токенов — не объект JSON")]
    validator = js.Draft202012Validator(DTCG_SCHEMA)
    for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        issues.append(Issue(pointer(tuple(str(p) for p in e.absolute_path)), "форма DTCG: " + _schema_message(e)))
    toks = Tokens(data)
    issues += toks.structure
    value_validators = {t: js.Draft202012Validator({"$ref": f"#/$defs/v-{t}", "$defs": DTCG_SCHEMA["$defs"]})
                        for t in TYPES}
    for t in toks.list:
        if t.type is None:
            m = ALIAS.match(t.value) if isinstance(t.value, str) else None
            why = f"алиас {t.value} не даёт типа" if m else "нет $type у токена и у его групп"
            issues.append(Issue(t.pointer, f"`{'.'.join(t.path)}` — тип не определён: {why} (DTCG: тип не угадывают "
                                           "по значению)"))
            continue
        values = [(None, t.value, "$value")] + t.mode_entries()
        for mode, v, where in values:
            errs = list(value_validators[t.type].iter_errors(v))
            if errs:
                best = min(errs, key=lambda e: len(list(e.absolute_path)))
                issues.append(Issue(t.pointer + "/" + where,
                                    f"`{'.'.join(t.path)}` ({t.type}) — {where}: не по форме типа "
                                    f"({_schema_message(best)})"))
                continue
            issues += _alias_issues(toks, t, v, t.type, t.pointer + "/" + where, mode)
    tops = [k for k in data if not k.startswith("$") and k != "example"]
    for second in ("spacing", "spacer", "spaces"):
        if second in tops and "space" in tops:
            issues.append(Issue(pointer((second,)), f"вторая шкала отступов `{second}.*` рядом с `space.*`: шкала одна",
                                "warning"))
    return issues


def _schema_message(e):
    msg = e.message
    if len(msg) > 160:
        msg = msg[:157] + "…"
    return msg


def _alias_issues(toks, t, value, ty, where, mode=None):
    """Алиасы значения: ведут в токен (не в группу и не в пустоту), тип цели = ожидаемый, без циклов в своём режиме."""
    out = []
    if isinstance(value, str):
        m = ALIAS.match(value)
        if not m:
            return out
        ref = m.group(1)
        target = toks.get(ref)
        if target is None:
            kind = "в группу" if tuple(ref.split(".")) in toks.groups else "в пустоту"
            out.append(Issue(where, f"`{'.'.join(t.path)}` — алиас {{{ref}}} ведёт {kind}"))
            return out
        if target.type and ty and target.type != ty:
            out.append(Issue(where, f"`{'.'.join(t.path)}` — алиас {{{ref}}}: тип цели {target.type}, нужен {ty}"))
        try:
            toks.resolve(value, mode, (".".join(t.path),))
        except ValueError as e:
            out.append(Issue(where, f"`{'.'.join(t.path)}` — {e}" + (f" (режим {mode})" if mode else "")))
        return out
    sub = SUBTYPES.get(ty)
    if sub and isinstance(value, dict):
        for k, v in value.items():
            if k in sub:
                out += _alias_issues(toks, t, v, sub[k], f"{where}/{k}", mode)
    elif sub and isinstance(value, list):
        for i, item in enumerate(value):
            if isinstance(item, dict):
                for k, v in item.items():
                    if k in sub:
                        out += _alias_issues(toks, t, v, sub[k], f"{where}/{i}/{k}", mode)
            else:
                out += _alias_issues(toks, t, item, ty, f"{where}/{i}", mode)
    return out


# ------------------------------------------------------------------ значения CSS

def num(x):
    """Число для CSS и JSON артефакта: целое без «.0», дробное — кратчайшей записью."""
    if isinstance(x, bool):
        return "1" if x else "0"
    if isinstance(x, int):
        return str(x)
    if isinstance(x, float):
        return str(int(x)) if x.is_integer() else repr(x)
    return str(x)


def dim(v):
    return f"{num(v['value'])}{v['unit']}"


def px_of(v):
    """dimension → px (rem по 16 px) или None."""
    if isinstance(v, dict) and isinstance(v.get("value"), (int, float)):
        return v["value"] * (REM_PX if v.get("unit") == "rem" else 1)
    return None


def color_css(v):
    if not isinstance(v, dict):
        return str(v)
    alpha = v.get("alpha")
    hexv = v.get("hex") or _hex_from(v)
    if alpha is not None and alpha < 1:
        if hexv:
            r, g, b = (int(hexv[i:i + 2], 16) for i in (1, 3, 5))
            return f"rgb({r} {g} {b} / {num(alpha)})"
        return _color_fn(v, alpha)
    return hexv or _color_fn(v, None)


def _hex_from(v):
    comps = v.get("components") or []
    if any(c == "none" for c in comps) or len(comps) != 3:
        return None
    space = v.get("colorSpace")
    if space == "srgb":
        return "#" + "".join(f"{max(0, min(255, round(c * 255))):02x}" for c in comps)
    if space == "oklch":
        sys.path.insert(0, str(HERE.parent / "lib"))
        from color import oklch2hex
        return oklch2hex(*comps)
    return None


def _color_fn(v, alpha):
    comps = " ".join(num(c) for c in v.get("components") or [])
    a = f" / {num(alpha)}" if alpha is not None and alpha < 1 else ""
    space = v.get("colorSpace")
    if space in ("oklch", "oklab", "lab", "lch", "hsl", "hwb"):
        return f"{space}({comps}{a})"
    return f"color({space} {comps}{a})"


def font_css(v):
    if isinstance(v, str):
        return v if "," in v or " " not in v else json.dumps(v)
    out = []
    for name in v:
        out.append(name if name in GENERIC_FONTS or " " not in name else json.dumps(name, ensure_ascii=False))
    return ", ".join(out)


def weight_num(v):
    return FONT_WEIGHTS.get(v, v) if isinstance(v, str) else v


def bezier(v):
    return "cubic-bezier(" + ", ".join(num(x) for x in v) + ")"


def shadow_css(v):
    layers = v if isinstance(v, list) else [v]
    if not layers:
        return "none"
    out = []
    for layer in layers:
        s = f"{dim(layer['offsetX'])} {dim(layer['offsetY'])} {dim(layer['blur'])} {dim(layer['spread'])} " \
            f"{color_css(layer['color'])}"
        out.append(("inset " if layer.get("inset") else "") + s)
    return ", ".join(out)


def css_value(ty, v):
    """Разрешённое значение токена → строка CSS (ui 09/04 §5.1)."""
    if ty == "color":
        return color_css(v)
    if ty in ("dimension", "duration"):
        return dim(v)
    if ty == "fontFamily":
        return font_css(v)
    if ty == "fontWeight":
        return num(weight_num(v))
    if ty == "number":
        return num(v)
    if ty == "cubicBezier":
        return bezier(v)
    if ty == "strokeStyle":
        return v if isinstance(v, str) else "dashed"
    if ty == "border":
        return f"{dim(v['width'])} {css_value('strokeStyle', v['style'])} {color_css(v['color'])}"
    if ty == "transition":
        delay = "" if not v["delay"]["value"] else " " + dim(v["delay"])
        return f"{dim(v['duration'])} {bezier(v['timingFunction'])}{delay}"
    if ty == "shadow":
        return shadow_css(v)
    if ty == "gradient":
        stops = ", ".join(f"{color_css(s['color'])} {num(round(s['position'] * 100, 4))}%" for s in v)
        return f"linear-gradient({stops})"
    return json.dumps(v, ensure_ascii=False)


def _ext_css(t):
    """Готовое CSS-значение расширения страниц: fluid.css или css-строка / одно свойство."""
    fl = t.ext(EXT_FLUID)
    if isinstance(fl, dict) and isinstance(fl.get("css"), str):
        return fl["css"]
    c = t.ext(EXT_CSS)
    if isinstance(c, str):
        return c
    if isinstance(c, dict) and len(c) == 1 and isinstance(next(iter(c.values())), str):
        return next(iter(c.values()))
    return None


TYPO_PARTS = (("family", "fontFamily"), ("size", "fontSize"), ("leading", "lineHeight"), ("weight", "fontWeight"),
              ("tracking", "letterSpacing"))


def token_vars(toks, t, mode=None):
    """[(имя переменной, значение CSS)] токена в режиме; типографический токен — пять переменных."""
    v = toks.value(t, mode)
    if t.type == "typography":
        sub = SUBTYPES["typography"]
        out = []
        fluid = _ext_css(t) if mode is None or mode not in t.modes() else None
        for suffix, key in TYPO_PARTS:
            val = fluid if key == "fontSize" and fluid else css_value(sub[key], v[key])
            out.append((f"{t.name}-{suffix}", val))
        return out
    if mode is None or mode not in t.modes():
        ext = _ext_css(t)
        if ext is not None and (mode is None or toks.in_mode(t, mode) == t.value):
            return [(t.name, ext)]
    return [(t.name, css_value(t.type, v))]


# ------------------------------------------------------------------ узкая ширина (NU-15)

def narrow(toks):
    """{"below": граница, "breakpoint": путь, "size": значение, "base": значение} — если основной текст type.body
    ниже первой границы надо поднять до минимума; иначе None. Нет границ или type.body — None."""
    body = toks.get("type.body")
    bps = [t for t in toks.list if t.path[0] == "breakpoint" and t.type == "dimension"]
    if body is None or body.type != "typography" or not bps:
        return None
    try:
        size = toks.value(body)["fontSize"]
        first = min(bps, key=lambda t: px_of(toks.value(t)) or 0)
        first_v = toks.value(first)
    except (ValueError, KeyError, TypeError):
        return None
    base_px = px_of(size)
    if base_px is None or base_px >= NARROW_BODY_MIN_PX:
        return None
    unit = size.get("unit", "px")
    target = {"value": NARROW_BODY_MIN_PX / REM_PX if unit == "rem" else NARROW_BODY_MIN_PX, "unit": unit}
    return {"below": dim(first_v), "breakpoint": ".".join(first.path), "size": dim(target), "base": dim(size)}


# ------------------------------------------------------------------ system.tokens.css

CSS_HEAD = ("/* Производный файл: собирает scripts/project/ds_build.py из system.tokens.json — руками не правится.\n"
            "   Имя переменной — путь токена DTCG через дефис; алиасы разрешены до значения. */\n")


def build_css(toks):
    base = []
    for t in toks.list:
        base += token_vars(toks, t)
    base_map = dict(base)
    modes = toks.mode_names()
    themes = [m for m in modes if m not in DENSITY and m != REDUCED]
    lines = [CSS_HEAD, ":root {", f"  color-scheme: {'light dark' if themes else 'light'};"]
    lines += [f"  {_var(n)}: {v};" for n, v in base]
    lines.append("}")

    def block(mode):
        out = []
        for t in toks.list:
            for n, v in token_vars(toks, t, mode):
                if base_map.get(n) != v:
                    out.append((n, v))
        return out

    nar = narrow(toks)
    if nar:
        lines += ["", f"/* Узкая ширина: ниже {nar['breakpoint']} основной текст не меньше {NARROW_BODY_MIN_PX} px "
                      "(ux 09/03 §7.1). */",
                  f"@media (width < {nar['below']}) {{", "  :root {", f"    --type-body-size: {nar['size']};", "  }",
                  "}"]
    for mode in themes:
        rows = block(mode)
        if not rows:
            continue
        label = THEMES.get(mode, mode)
        lines += ["", f"/* Тема «{label}» ({mode}): на :root, где объявлены переменные, иначе алиасы "
                      "не пересчитаются. */"]
        if mode == "dark":
            lines += ["@media (prefers-color-scheme: dark) {", '  :root:not([data-theme="light"]) {',
                      "    color-scheme: dark;"] + [f"    {_var(n)}: {v};" for n, v in rows] + ["  }", "}", ""]
        lines += [f':root[data-theme="{mode}"] {{'] + (["  color-scheme: dark;"] if mode == "dark" else []) + \
                 [f"  {_var(n)}: {v};" for n, v in rows] + ["}"]
    if REDUCED in modes:
        rows = block(REDUCED)
        if rows:
            lines += ["", "/* Сокращённое движение: только токены движения. */",
                      "@media (prefers-reduced-motion: reduce) {",
                      "  :root {"] + [f"    {_var(n)}: {v};" for n, v in rows] + ["  }", "}", "",
                                                                             ':root[data-motion="reduced"] {'] + \
                     [f"  {_var(n)}: {v};" for n, v in rows] + ["}"]
    for mode in DENSITY:
        if mode in modes:
            rows = block(mode)
            if rows:
                lines += ["", f"/* Плотность {mode}: переопределяются роли, режим включается и на поддереве. */",
                          f'[data-density="{mode}"] {{'] + [f"  {_var(n)}: {v};" for n, v in rows] + ["}"]
    return "\n".join(lines) + "\n"


def _var(name):
    return "--" + name


# ------------------------------------------------------------------ передняя часть DESIGN.md

def _y(v):
    """Скаляр YAML: числа как есть, строки — в двойных кавычках (JSON-запись — допустимая строка YAML)."""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return num(v)
    return json.dumps(str(v), ensure_ascii=False)


def _typo(toks, t, mode=None):
    v = toks.value(t, mode)
    sub = SUBTYPES["typography"]
    return {"fontFamily": css_value("fontFamily", v["fontFamily"]), "fontSize": _ext_css(t) or dim(v["fontSize"]),
            "fontWeight": weight_num(v["fontWeight"]), "lineHeight": v["lineHeight"],
            "letterSpacing": css_value(sub["letterSpacing"], v["letterSpacing"])}


def in_artifact(t):
    return t.path[0] != "primitive"


def front_matter(toks, name, description):
    colors, typo, rounded, spacing, other = {}, {}, {}, {}, {}
    for t in toks.list:
        if not in_artifact(t):
            continue
        if t.type == "color":
            colors[t.name] = token_vars(toks, t)[0][1]
        elif t.type == "typography":
            typo[t.name] = _typo(toks, t)
        elif t.path[0] == "radius" and t.type == "dimension":
            rounded[t.name] = token_vars(toks, t)[0][1]
        elif t.path[0] == "space" and t.type == "dimension":
            spacing[t.name] = token_vars(toks, t)[0][1]
        else:
            for n, v in token_vars(toks, t):
                other[n] = v
    modes = {}
    for mode in toks.mode_names():
        rows = {}
        for t in toks.list:
            if not in_artifact(t):
                continue
            for (n, v), (_, b) in zip(token_vars(toks, t, mode), token_vars(toks, t)):
                if v != b:
                    rows[n] = v
        if rows:
            modes[mode] = rows
    lines = ["---", "version: alpha", f"name: {_y(name)}", f"description: {_y(description)}"]

    def section(title, d, nested=False):
        if not d:
            return
        lines.append(f"{title}:")
        for k, v in d.items():
            if isinstance(v, dict):
                lines.append(f"  {k}:")
                for k2, v2 in v.items():
                    if isinstance(v2, dict):
                        lines.append(f"    {k2}:")
                        lines.extend(f"      {k4}: {_y(v4)}" for k4, v4 in v2.items())
                    else:
                        lines.append(f"    {k2}: {_y(v2)}")
            else:
                lines.append(f"  {k}: {_y(v)}")

    section("colors", colors)
    section("typography", typo)
    section("rounded", rounded)
    section("spacing", spacing)
    section("x-tokens", other)
    section("x-modes", modes)
    nar = narrow(toks)
    if nar:
        section("x-narrow", {"below": nar["below"], "type-body": {"fontSize": nar["size"]}})
    lines.append("---")
    return "\n".join(lines) + "\n"


def with_front_matter(text, fm):
    m = FM.match(text)
    if m:
        return fm + text[m.end():]
    return fm + ("" if text.startswith("\n") else "\n") + text


def prose(text):
    """Проза DESIGN.md без передней части и начальных пустых строк."""
    m = FM.match(text)
    body = text[m.end():] if m else text
    return body.lstrip("\n")


def title_of(text):
    for line in prose(text).splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line)
        if m:
            return m.group(1)
    return None


# ------------------------------------------------------------------ артефакт Design System

def family_of(t):
    """Семейство токена в tokens.json артефакта или None (не идёт в артефакт)."""
    if not in_artifact(t) or t.type in MOTION_TYPES or t.path[0].startswith("motion"):
        return None
    explicit = t.art("family")
    if isinstance(explicit, str) and explicit:
        return explicit
    if t.type == "color":
        return "color"
    if t.type == "typography":
        return "type"
    if t.type == "fontFamily" and t.path[0] == "font":
        return "font"
    if t.type == "shadow":
        return "shadow"
    return FAMILY_OF_GROUP.get(t.path[0], t.path[0])


def font_key(t):
    """Ключ `type.families` для токена гарнитуры: переменная артефакта — `--font-<ключ>`."""
    p = list(t.path)
    if p[0] == "font":
        return "-".join(p[1:]) or p[0]
    if "family" in p and p.index("family") < len(p) - 1:
        return "-".join(p[p.index("family") + 1:])
    return p[-1]


def artifact_tokens(toks, name, example=False):
    """tokens.json артефакта: имя, версия, источник, семейства по порядку первого появления."""
    art_root = (toks.data.get("$extensions") or {}).get(EXT_ART) if isinstance(toks.data.get("$extensions"),
                                                                                dict) else None
    art_root = art_root if isinstance(art_root, dict) else {}
    notes = {k: (v or {}).get("note") for k, v in (art_root.get("families") or {}).items() if isinstance(v, dict)}
    doc = {"name": name}
    if example:
        doc["example"] = True
    doc.update({"version": 1, "meta": {"source": "system.tokens.json (DTCG) — сборка ds_build"}})
    order, fam_tokens = [], {}
    for t in toks.list:
        f = family_of(t)
        if f is None:
            continue
        f = "type" if f == "font" else f
        if f not in fam_tokens:
            order.append(f)
            fam_tokens[f] = []
        fam_tokens[f].append(t)
    themes = ["light"] + [m for m in toks.mode_names() if m not in DENSITY and m != REDUCED and m != "light"]
    for f in order:
        ts = fam_tokens[f]
        if f == "color":
            doc["color"] = {"themes": [{"id": m, "name": THEMES.get(m, m)} for m in themes],
                            "tokens": [{"name": t.name,
                                        "value": {m: token_vars(toks, t, None if m == "light" else m)[0][1]
                                                  for m in themes},
                                        "usage": t.description} for t in ts]}
        elif f == "type":
            doc["type"] = _type_family(toks, ts)
        else:
            body = {}
            note = notes.get(f) or _group_note(toks, f)
            if note:
                body["note"] = note
            body["tokens"] = [{"name": n, "value": v, "usage": t.description}
                              for t in ts for n, v in token_vars(toks, t)]
            doc[f] = body
    return doc


def _group_note(toks, family):
    for g, f in FAMILY_OF_GROUP.items():
        if f == family and (g,) in toks.groups:
            d = toks.groups[(g,)].get("$description")
            if isinstance(d, str) and d:
                return d
    if (family,) in toks.groups:
        d = toks.groups[(family,)].get("$description")
        if isinstance(d, str) and d:
            return d
    return None


def _type_family(toks, ts):
    families, groups, keyed = {}, [], {}
    fonts = [t for t in ts if t.type == "fontFamily"]
    for t in fonts:
        families[font_key(t)] = css_value("fontFamily", toks.value(t))
    for t in ts:
        if t.type != "typography":
            continue
        v = toks.value(t)
        fam_ref = t.value.get("fontFamily") if isinstance(t.value, dict) else None
        m = ALIAS.match(fam_ref) if isinstance(fam_ref, str) else None
        key = None
        if m and toks.get(m.group(1)) is not None:
            key = font_key(toks.get(m.group(1)))
            families.setdefault(key, css_value("fontFamily", v["fontFamily"]))
        else:
            stack = css_value("fontFamily", v["fontFamily"])
            key = next((k for k, s in families.items() if s == stack), None)
            if key is None:
                key = re.sub(r"[^a-z0-9]+", "-", str(v["fontFamily"][0] if isinstance(v["fontFamily"], list)
                                                     else stack.split(",")[0]).lower().strip('"')).strip("-")
                families[key] = stack
        gname = t.art("group") if isinstance(t.art("group"), str) else None
        if not gname:
            gname = families[key].split(",")[0].strip().strip('"')
        if (gname, key) not in keyed:
            keyed[(gname, key)] = {"name": gname, "family": key, "styles": []}
            groups.append(keyed[(gname, key)])
        style = {"name": "-".join(t.path[1:]) if t.path[0] == "type" and len(t.path) > 1 else t.name,
                 "fontSize": _ext_css(t) or dim(v["fontSize"]), "lineHeight": v["lineHeight"],
                 "fontWeight": weight_num(v["fontWeight"])}
        sample = t.art("sample")
        if isinstance(sample, str) and sample:
            style["sample"] = sample
        style["usage"] = t.description
        keyed[(gname, key)]["styles"].append(style)
    out = {"families": families}
    if groups:
        out["groups"] = groups
    return out


INLINE_LISTS = ("tokens", "themes", "styles")


def _inline(v):
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{json.dumps(k, ensure_ascii=False)}: {_inline(x)}" for k, x in v.items()) + " }" \
            if v else "{}"
    if isinstance(v, list):
        return "[" + ", ".join(_inline(x) for x in v) + "]"
    return json.dumps(v, ensure_ascii=False)


def dump_artifact(obj):
    """JSON артефакта: записи списков tokens, themes, styles — строкой на запись, остальное — с отступом 2."""

    def pretty(v, ind, key=None):
        pad = "  " * ind
        if isinstance(v, dict):
            if not v:
                return "{}"
            items = [f"{pad}  {json.dumps(k, ensure_ascii=False)}: {pretty(x, ind + 1, k)}" for k, x in v.items()]
            return "{\n" + ",\n".join(items) + f"\n{pad}}}"
        if isinstance(v, list):
            if not v:
                return "[]"
            items = [f"{pad}  {_inline(x) if key in INLINE_LISTS else pretty(x, ind + 1)}" for x in v]
            return "[\n" + ",\n".join(items) + f"\n{pad}]"
        return json.dumps(v, ensure_ascii=False)

    return pretty(obj, 0) + "\n"


def readme(design_md_text, slug):
    return (f"<!-- Производный файл: собирает ds_build из docs/projects/{slug}/design/DESIGN.md — правка в прозе ДС, "
            "не здесь. -->\n\n" + prose(design_md_text).rstrip("\n") + "\n")


def readme_fresh(disk, built):
    """README на диске равен сборке; хвост, который дописывает страница артефакта, — не расхождение."""
    if disk == built:
        return True
    head = built.rstrip("\n")
    return disk.startswith(head) and PAGE_TAIL in disk[len(head):]


# ------------------------------------------------------------------ сборка проекта

@dataclass
class Project:
    slug: str
    repo: Path
    tokens_path: Path
    css_path: Path
    design_md_path: Path
    art_dir: Path
    brand_path: Path

    @classmethod
    def of(cls, slug, repo):
        d = lambda key: docpaths.design(slug, key, repo=repo)  # noqa: E731
        return cls(slug, repo, d("tokens"), d("tokens-css"), d("design-md"), d("ds-project"), d("brand"))

    @property
    def art_tokens(self):
        return self.art_dir / "tokens.json"

    @property
    def art_readme(self):
        return self.art_dir / "README.md"

    def rel(self, p):
        return docpaths.rel(p, self.repo)


def load_tokens(path):
    """(данные, ошибка): JSON файла токенов."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")), None
    except (OSError, UnicodeDecodeError) as e:
        return None, f"файл не читается: {e}"
    except ValueError as e:
        return None, f"не JSON: {e}"


def ds_name(toks, prj):
    art = (toks.data.get("$extensions") or {}).get(EXT_ART) if isinstance(toks.data.get("$extensions"), dict) else None
    if isinstance(art, dict) and isinstance(art.get("name"), str) and art["name"]:
        return art["name"]
    if prj.design_md_path.is_file():
        t = title_of(prj.design_md_path.read_text(encoding="utf-8"))
        if t:
            return t
    if prj.brand_path.is_file():
        try:
            import yaml
            b = yaml.safe_load(prj.brand_path.read_text(encoding="utf-8")) or {}
            if isinstance(b, dict) and isinstance(b.get("name"), str) and not b["name"].startswith("<"):
                return b["name"]
        except Exception:                                     # noqa: BLE001 — битый бренд проверяет его аудит
            pass
    return prj.slug


def derive(prj, data):
    """{путь: текст} производных из разобранных токенов; DESIGN.md — только если проза есть."""
    toks = Tokens(data)
    name = ds_name(toks, prj)
    desc = data.get("$description") if isinstance(data.get("$description"), str) else ""
    out = {prj.css_path: build_css(toks),
           prj.art_tokens: dump_artifact(artifact_tokens(toks, name, example=data.get("example") is True))}
    if prj.design_md_path.is_file():
        text = prj.design_md_path.read_text(encoding="utf-8")
        out[prj.design_md_path] = with_front_matter(text, front_matter(toks, name, desc))
        out[prj.art_readme] = readme(text, prj.slug)
    return out, toks


def check(prj):
    """Находки R-STRUCT-006 и R-FRESH-001 по ДС продукта."""
    rep = F.Report()
    derived = [prj.css_path, prj.design_md_path, prj.art_tokens, prj.art_readme]
    if not prj.tokens_path.is_file():
        present = [p for p in derived if p.is_file()]
        if present:
            rep.add("R-STRUCT-006", "error", surface=None, kind=KIND, ref="tokens", path=prj.rel(prj.tokens_path),
                    message="нет токенов DTCG, а производные ДС есть: " + ", ".join(p.name for p in present),
                    fix=f"токены — этап design-system: /design-deep-dive {prj.slug}")
        return rep.items
    data, err = load_tokens(prj.tokens_path)
    rel_tokens = prj.rel(prj.tokens_path)
    if err:
        rep.add("R-STRUCT-006", "error", surface=None, kind=KIND, ref="tokens", path=rel_tokens,
                message=f"system.tokens.json — {err}")
        return rep.items
    issues = validate(data)
    for i in issues:
        rep.add("R-STRUCT-006", i.severity, surface=None, kind=KIND, ref="tokens#" + i.pointer, path=rel_tokens,
                message=i.message, fix="" if i.severity != "error" else "правка токена в system.tokens.json, затем "
                                                                         f"ds_build build {prj.slug}")
    if any(i.severity == "error" for i in issues):
        rep.add("R-FRESH-001", "hint", surface=None, kind=KIND, ref="tokens", path=rel_tokens,
                message="свежесть производных не сверялась: токены не собираются, пока есть ошибки формата")
        return rep.items
    toks = Tokens(data)
    own = [f for f in dict.fromkeys(family_of(t) for t in toks.list) if f and f not in BASE_FAMILIES + ("font",)]
    if len(own) > OWN_FAMILIES_MAX:
        rep.add("R-STRUCT-006", "warning", surface=None, kind=KIND, ref="tokens", path=rel_tokens,
                message=f"в артефакт уходит {len(own)} своих семейств ({', '.join(own)}), формат типа принимает до "
                        f"{OWN_FAMILIES_MAX}: лишние сведите поле `family` расширения {EXT_ART}")
    if narrow(toks) is None and toks.get("type.body") is not None and \
            not [t for t in toks.list if t.path[0] == "breakpoint"]:
        rep.add("R-STRUCT-006", "warning", surface=None, kind=KIND, ref="tokens#/breakpoint", path=rel_tokens,
                message="нет breakpoint.*: граница узкой ширины для основного текста (ux 09/03 §7.1) не задана")
    built, _ = derive(prj, data)
    fix = f"ds_build build {prj.slug} — производные руками не правят"
    for path in (prj.css_path, prj.design_md_path, prj.art_tokens, prj.art_readme):
        ref = {prj.css_path: "tokens-css", prj.design_md_path: "design-md#front-matter", prj.art_tokens:
               "artifact#tokens.json", prj.art_readme: "artifact#README.md"}[path]
        if path not in built:
            rep.add("R-FRESH-001", "warning", surface=None, kind=KIND, ref="design-md",
                    path=prj.rel(prj.design_md_path),
                    message="нет прозы DESIGN.md: передняя часть и README артефакта не собираются",
                    fix=f"проза ДС — этап design-system: /design-deep-dive {prj.slug}")
            continue
        if not path.is_file():
            rep.add("R-FRESH-001", "error", surface=None, kind=KIND, ref=ref, path=prj.rel(path),
                    message=f"{path.name}: производного нет — сборка из токенов не запускалась", fix=fix)
            continue
        disk = path.read_text(encoding="utf-8")
        fresh = readme_fresh(disk, built[path]) if path == prj.art_readme else disk == built[path]
        if not fresh:
            rep.add("R-FRESH-001", "error", surface=None, kind=KIND, ref=ref, path=prj.rel(path),
                    message=f"{_what(path, prj)} от сборки: {_first_diff(disk, built[path])}", fix=fix)
    return rep.items


def _what(path, prj):
    return {prj.css_path: "system.tokens.css отстал", prj.design_md_path: "передняя часть DESIGN.md отстала",
            prj.art_tokens: "tokens.json артефакта отстал", prj.art_readme: "README артефакта отстал"}.get(
        path, path.name + " отстал")


def _first_diff(a, b):
    la, lb = a.splitlines(), b.splitlines()
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else "∅"
        y = lb[i] if i < len(lb) else "∅"
        if x != y:
            return f"строка {i + 1}: в файле «{x[:70]}», в сборке «{y[:70]}»"
    return "различаются концы строк"


def build(prj, out=None):
    """Записать производные (по месту или в out/docs/projects/<slug>/…) → [(путь, записан ли)]."""
    data, err = load_tokens(prj.tokens_path)
    if err:
        raise F.ToolError(f"{prj.rel(prj.tokens_path)} — {err}")
    errors = [i for i in validate(data) if i.severity == "error"]
    if errors:
        raise F.ToolError(f"токены с ошибками формата ({len(errors)}), первая: {errors[0].pointer} — "
                          f"{errors[0].message}"
                          f"; ds_build check {prj.slug}")
    built, _ = derive(prj, data)
    done = []
    for path, text in built.items():
        target = path if out is None else Path(out) / Path(prj.rel(path))
        same = target.is_file() and target.read_text(encoding="utf-8") == text
        if not same:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
        done.append((target, not same))
    return done


def show(prj, as_json=False, out=None):
    out = out or sys.stdout
    data, err = load_tokens(prj.tokens_path)
    if err:
        raise F.ToolError(f"{prj.rel(prj.tokens_path)} — {err}")
    toks = Tokens(data)
    rows = []
    for t in toks.list:
        try:
            base = token_vars(toks, t)
            modes = {m: token_vars(toks, t, m) for m in t.modes()}
        except (ValueError, KeyError, TypeError) as e:
            base, modes = [(t.name, f"не разрешается: {e}")], {}
        rows.append({"path": ".".join(t.path), "var": "--" + t.name, "type": t.type, "family": family_of(t),
                     "value": dict(base), "modes": {m: dict(v) for m, v in modes.items()}})
    if as_json:
        print(json.dumps({"project": prj.slug, "tokens": rows, "narrow": narrow(toks)}, ensure_ascii=False, indent=1),
              file=out)
        return
    for r in rows:
        vals = "; ".join(f"{k}: {v}" for k, v in r["value"].items())
        print(f"{r['path']:<34} {r['type'] or '?':<11} {(r['family'] or '—'):<10} {vals}", file=out)
        for m, v in r["modes"].items():
            print(f"{'':<34} {'':<11} {'':<10} [{m}] " + "; ".join(f"{k}: {x}" for k, x in v.items()), file=out)


# ------------------------------------------------------------------ самопроверка

def reference_tokens():
    """Эталонный листинг DTCG ui 09/04 §4 (для самопроверки формата)."""
    text = kbpaths.kb("ui", "09-design-tokens", "04-reference-token-schema.md").read_text(encoding="utf-8")
    m = re.search(r"^## 4\..*?^```json\s*\n(.*?)^```", text, re.S | re.M)
    return json.loads(m.group(1)) if m else None


def _selftest():
    import copy
    import subprocess
    import tempfile
    ok = True

    def check_(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    _jsonschema()
    # 1. значения CSS и разрешение алиасов
    doc = {"primitive": {"color": {"$type": "color", "ink": {"$value": {"colorSpace": "srgb", "components": [0, 0, 0],
                                                                       "hex": "#000000"}},
                                   "paper": {"$value": {"colorSpace": "srgb", "components": [1, 1, 1],
                                                        "hex": "#FFFFFF"}}},
                         "size": {"$type": "dimension", "14": {"$value": {"value": 14, "unit": "px"}}}},
           "color": {"$type": "color",
                     "bg": {"$value": "{primitive.color.paper}",
                            "$extensions": {EXT_MODES: {"dark": "{primitive.color.ink}"}}},
                     "text": {"$value": "{primitive.color.ink}",
                              "$extensions": {EXT_MODES: {"dark": "{primitive.color.paper}"}}},
                     "on-bg": {"$value": "{color.text}"},
                     "scrim": {"$value": {"colorSpace": "srgb", "components": [0, 0, 0], "alpha": 0.5,
                                          "hex": "#000000"}}},
           "font": {"sans": {"$type": "fontFamily", "$value": ["Golos Text", "Arial", "sans-serif"]}},
           "breakpoint": {"$type": "dimension", "desktop": {"$value": {"value": 1024, "unit": "px"}},
                          "tablet": {"$value": {"value": 640, "unit": "px"}}},
           "motion": {"fast": {"$type": "duration", "$value": {"value": 100, "unit": "ms"},
                               "$extensions": {EXT_MODES: {"reduced": {"value": 0, "unit": "ms"}}}}},
           "type": {"$type": "typography",
                    "body": {"$value": {"fontFamily": "{font.sans}", "fontSize": "{primitive.size.14}",
                                        "fontWeight": 400,
                                        "letterSpacing": {"value": 0, "unit": "px"}, "lineHeight": 1.428571}}}}
    check_("формат DTCG: чистый документ — 0 замечаний", validate(doc) == [])
    toks = Tokens(doc)
    check_("алиас разрешается в режиме транзитивно: color.on-bg в dark = paper",
           color_css(toks.value(toks.get("color.on-bg"), "dark")) == "#FFFFFF")
    check_("цвет с альфой → rgb(R G B / A)", color_css(toks.value(toks.get("color.scrim"))) == "rgb(0 0 0 / 0.5)")
    check_("гарнитура: многословные — в кавычках", font_css(["Golos Text", "Arial", "sans-serif"]) ==
           '"Golos Text", Arial, sans-serif')
    css = build_css(toks)
    check_("CSS: имена = пути через дефис, типографика — пять переменных",
           "--color-bg: #FFFFFF;" in css and "--type-body-size: 14px;" in css
           and "--type-body-leading: 1.428571;" in css
           and "--font-sans: \"Golos Text\", Arial, sans-serif;" in css)
    check_("CSS: блок тёмной темы — транзитивное замыкание (color.on-bg без своего режима)",
           re.search(r':root\[data-theme="dark"\] \{[^}]*--color-on-bg: #FFFFFF;', css) is not None)
    check_("CSS: сокращённое движение и узкая ширина (type.body 14 → 16 ниже первой границы 640px)",
           "--motion-fast: 0ms;" in css and "@media (width < 640px)" in css and "--type-body-size: 16px;" in css)
    fm = front_matter(toks, "Проба", "описание")
    check_("передняя часть: colors, typography, x-modes, x-narrow",
           'color-bg: "#FFFFFF"' in fm and "type-body:" in fm and "x-modes:" in fm and "x-narrow:" in fm)
    art = artifact_tokens(toks, "Проба")
    check_("артефакт: без примитивов и движения; цвет по темам; type.families → font-sans",
           [t["name"] for t in art["color"]["tokens"]] == ["color-bg", "color-text", "color-on-bg", "color-scrim"]
           and art["color"]["tokens"][0]["value"] == {"light": "#FFFFFF", "dark": "#000000"}
           and art["type"]["families"] == {"sans": '"Golos Text", Arial, sans-serif'}
           and "motion" not in art and "breakpoint" in art)
    back = json.loads(dump_artifact(art))
    check_("tokens.json артефакта — валидный JSON той же структуры", back == art)
    # 2. дефекты формата
    bad = copy.deepcopy(doc)
    bad["color"]["bg"]["$value"] = "#fff"
    check_("битый $value цвета (строка вместо объекта) — ошибка",
           any("не по форме типа" in i.message for i in validate(bad)))
    bad = copy.deepcopy(doc)
    bad["color"]["text"]["$value"] = "{primitive.color.nope}"
    check_("алиас в пустоту — ошибка", any("в пустоту" in i.message for i in validate(bad)))
    bad = copy.deepcopy(doc)
    bad["color"]["bg"]["$value"] = "{color.on-bg}"
    bad["color"]["text"]["$value"] = "{color.bg}"
    check_("цикл алиасов — ошибка", any("цикл" in i.message for i in validate(bad)))
    bad = copy.deepcopy(doc)
    bad["color"]["bg"]["$extensions"][EXT_MODES]["dark"] = "{color.on-bg}"
    bad["color"]["text"]["$extensions"][EXT_MODES]["dark"] = "{color.bg}"
    check_("цикл алиасов только в режиме dark — ошибка", any("цикл" in i.message and "dark" in i.message
                                                             for i in validate(bad)))
    bad = copy.deepcopy(doc)
    bad["loose"] = {"x": {"$value": 3}}
    check_("токен без типа — ошибка (тип не угадывают)", any("тип не определён" in i.message for i in validate(bad)))
    bad = copy.deepcopy(doc)
    bad["type"]["body"]["$value"]["fontSize"] = "{color.bg}"
    check_("алиас подзначения другого типа — ошибка", any("тип цели color, нужен dimension" in i.message
                                                          for i in validate(bad)))
    bad = copy.deepcopy(doc)
    bad["spacing"] = {"$type": "dimension", "a": {"$value": {"value": 4, "unit": "px"}}}
    bad["space"] = {"$type": "dimension", "b": {"$value": {"value": 4, "unit": "px"}}}
    check_("вторая шкала отступов — предупреждение", any(i.severity == "warning" for i in validate(bad)))
    # 3. эталоны баз проходят формат
    ref = reference_tokens()
    check_("эталон ui 09/04 §4 проходит формат DTCG (0 ошибок)",
           ref is not None and not [i for i in validate(ref) if i.severity == "error"])
    mk = json.loads(kbpaths.kb("creative", "04-visual-language", "marketing-tokens.json").read_text(encoding="utf-8"))
    errs = [i for i in validate(mk) if i.severity == "error"]
    check_("токены страниц creative (marketing-tokens.json) проходят формат DTCG"
           + (f" (есть: {errs[0].pointer} {errs[0].message})" if errs else ""), not errs)
    rt = Tokens(ref)
    rcss = build_css(rt)
    check_("эталон ui: сборка CSS — плотность, тёмная тема и сокращённое движение",
           '[data-density="compact"]' in rcss and ':root[data-theme="dark"]' in rcss
           and "prefers-reduced-motion" in rcss
           and "--space-md: 16px;" in rcss and "@media (width < 640px)" in rcss)
    check_("README: хвост страницы артефакта — не расхождение",
           readme_fresh("# A\n\nтекст\n\n## Consuming this system\n…\n", "# A\n\nтекст\n")
           and not readme_fresh("# A\n\nдругой\n", "# A\n\nтекст\n"))
    # 4. фикстура cabinet-ds
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("cabinet-ds") as fx:
        prj = Project.of(fx.slug, fx.root)
        items = check(prj)
        loud = [f for f in items if f.severity in ("error", "warning")]
        check_("фикстура cabinet-ds: check — 0 error, 0 warning (производные свежие)"
               + (f" (есть: {'; '.join(f.rule + ' ' + f.ref + ' ' + f.message[:80] for f in loud[:3])})"
                  if loud else ""),
               not loud)
        done = build(prj)
        check_("build на свежей фикстуре ничего не меняет", done and not any(changed for _, changed in done))
        with tempfile.TemporaryDirectory(prefix="ddd-ds-cwd-") as cwd:
            r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "check", fx.slug, "--repo", str(fx.root),
                                "--json"], cwd=cwd, capture_output=True, text=True)
        try:
            lines = F.parse_lines(r.stdout)
        except ValueError:
            lines = None
        check_("check --json из чужой рабочей папки с --repo — код 0, строки находок",
               r.returncode == 0 and lines is not None and not [f for f in lines if f.severity == "error"])
        # правка значения без сборки
        raw = prj.tokens_path.read_text(encoding="utf-8")
        prj.tokens_path.write_text(raw.replace('"hex": "#1d4ed8"', '"hex": "#1e40af"', 1), encoding="utf-8")
        got = {(f.rule, f.ref) for f in check(prj) if f.severity == "error"}
        check_("правка значения токена без build → R-FRESH-001 (CSS, передняя часть, tokens.json)",
               {("R-FRESH-001", "tokens-css"), ("R-FRESH-001", "design-md#front-matter"),
                ("R-FRESH-001", "artifact#tokens.json")} <= got)
        with tempfile.TemporaryDirectory(prefix="ddd-ds-out-") as od:
            build(prj, out=od)
            outp = Path(od) / prj.rel(prj.css_path)
            check_("build --out пишет в DIR/docs/projects/<slug>/…, проект не трогает",
                   outp.is_file() and "#1e40af" in outp.read_text(encoding="utf-8")
                   and "#1e40af" not in prj.css_path.read_text(encoding="utf-8"))
        build(prj)
        check_("после build — снова 0 error", not [f for f in check(prj) if f.severity == "error"])
        prj.tokens_path.write_text(raw.replace('"$value": "{primitive.color.accent.700}"',
                                               '"$value": "{primitive.color.nope}"', 1), encoding="utf-8")
        got = [f for f in check(prj) if f.rule == "R-STRUCT-006" and f.severity == "error"]
        check_("алиас в пустоту в токенах фикстуры → R-STRUCT-006", got and "в пустоту" in got[0].message)
        prj.tokens_path.write_text(raw.replace('{"value": 16, "unit": "px"}', '"16px"', 1), encoding="utf-8")
        got = [f for f in check(prj) if f.rule == "R-STRUCT-006" and f.severity == "error"]
        check_("битый $value (строка «16px» вместо dimension) → R-STRUCT-006", got and "не по форме" in got[0].message)
        (prj.css_path).unlink()
        prj.tokens_path.write_text(raw, encoding="utf-8")
        got = [f for f in check(prj) if f.rule == "R-FRESH-001" and f.ref == "tokens-css"]
        check_("нет производного CSS → R-FRESH-001", got and "производного нет" in got[0].message)
    print("ds_build selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    _reexec_venv()
    if "--selftest" in argv:
        try:
            return _selftest()
        except F.ToolError as e:
            print(f"ds_build: {e}", file=sys.stderr)
            return F.EXIT_USAGE
    ap = docpaths.parser("ds_build", __doc__, commands=("build", "check", "show"), surface="none")
    call = docpaths.parse(ap, argv)
    prj = Project.of(call.slug, call.repo)
    try:
        if call.command == "check":
            items = check(prj)
            F.print_findings(items, as_json=call.json)
            return F.exit_code(items)
        if call.command == "show":
            show(prj, as_json=call.json)
            return F.EXIT_OK
        if not prj.tokens_path.is_file():
            raise F.ToolError(f"нет токенов DTCG: {prj.rel(prj.tokens_path)}")
        done = build(prj, call.out)
        if call.json:
            print(json.dumps([{"path": docpaths.rel(p, call.repo) if call.out is None else str(p), "written": w}
                              for p, w in done], ensure_ascii=False))
        else:
            for p, w in done:
                shown = docpaths.rel(p, call.repo) if call.out is None else p
                print(f"{'записан' if w else 'без изменений':<15} {shown}")
        return F.EXIT_OK
    except (F.ToolError, docpaths.DocPathError, OSError) as e:
        print(f"ds_build: {e}", file=sys.stderr)
        return F.EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
