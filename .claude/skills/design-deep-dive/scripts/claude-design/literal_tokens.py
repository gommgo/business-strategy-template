#!/usr/bin/env python3
"""literal_tokens — «литерал ∈ значений токенов ДС»: облик артбордов холста и адаптивных копий против токенов продукта.

На артбордах типа Design значения облика — литералы, и каждый литерал берётся из токенов ДС (так требует тип, а свой
цвет или отступ на артборде — облик вне системы); на адаптивной копии — только переменные `system.tokens.css`
(`references/claude-design.md § Приёмка`, пункт C2; правило R-VIS-004 `design-audit`). Утилита читает исходники
холста без браузера:
  - литералы — инлайн-стили и `<style>` артборда, цветовые атрибуты SVG (`fill`, `stroke`, `stop-color`, `color`),
    умолчания и образцы цветовых твиков `data-props`; дырки `{{…}}` получают значения `renderVals()` на умолчаниях
    твиков (как в статичной копии, `dc_to_html.py`); рамка артборда (ширина и высота корня) не литерал облика;
  - семейства: цвет; кегль, интерлиньяж, насыщенность, гарнитура, разрядка; отступы (padding, margin, gap); радиусы;
    толщина границы; размеры (width, height, min-, max-: сверка с размерами и отступами ДС); тени; длительности;
    относительные единицы (%, em, ch, vw, fr) и ключевые слова (auto, none, inherit, transparent, currentColor) —
    не литералы облика;
  - значения ДС — из токенов: `system.tokens.css` (сборка `ds_build.py`), DTCG `system.tokens.json` (через сборку CSS
    `ds_build`), `tokens.json` артефакта Design System (списки по семействам, значения по темам); семейство токена —
    по имени (`space`, `radius`, `size`, `font-size`/`fs-`, `leading`/`lh-`, `weight`/`fw-`, `family`/`font-`,
    `shadow`/`elevation`, `duration`, `border-w`) и по семейству артефакта; у цвета — любой цветовой токен любой темы.
    Семейства, которого в ДС нет, утилита не сверяет и говорит об этом заметкой: требовать значение токена, которого
    нет, — пробел ДС, а не литерал;
  - сверяются артборды страниц холста этапа макета («Макет и прототип», «Состояния»); «Направления» и «Вайрфрейм» —
    до ДС или без облика, их берёт ключ --all-stages.
Находка — литерал со счётом мест и строками исходника и ближайшее значение токена (цвет — по расстоянию OKLab);
решение по литералу — уровень правки (элемент, компонент, токен) решает заказчик (`references/claude-design.md §
Правки токенов`).

Команды (файлы проекта — через lib/docpaths.py):
  literal_tokens.py check <slug> <surface> [--repo DIR] [--accepted] [--all-stages] [--json]
      исходники design/<surface>/canvas/project/ против токенов продукта (system.tokens.css, иначе system.tokens.json,
      иначе tokens.json артефакта; плюс копия ДС, установленная в холст, `canvas/project/ds/*/tokens.json`); адаптивные
      копии design/<surface>/canvas/html/<page-id>.html — значения облика только через var(--…) из system.tokens.css.
      Тяжесть — warning, у принятого макета (--accepted) — error. Ничего не пишет.
  literal_tokens.py scan <файл.dc.html | папка project> … --tokens ФАЙЛ [--tokens ФАЙЛ …] [--all-stages] [--json]
      то же вне проекта (пример базы, снимок живой версии).
  literal_tokens.py tokens ФАЙЛ … [--json]      значения токенов по семействам, темы и брейкпоинты — для разбора
  literal_tokens.py --selftest                  самопроверка на примере базы claude-design и фикстурах, без сети
Находки — строки JSON {rule, severity, surface, kind, ref, path, message, fix} (контракт утилит project/). Коды выхода:
0 — ошибок нет; 1 — есть находки error; 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402
import dc_to_html as DC  # noqa: E402

kbpaths.use("project")
import findings as FND  # noqa: E402

RULE = "R-VIS-004"
FAMILIES = ("color", "font-size", "line-height", "weight", "family", "letter-spacing", "spacing", "radius", "border",
            "size", "shadow", "duration")
FAMILY_RU = {"color": "цвет", "font-size": "кегль", "line-height": "интерлиньяж", "weight": "насыщенность",
             "family": "гарнитура", "letter-spacing": "разрядка", "spacing": "отступ", "radius": "радиус",
             "border": "толщина границы", "size": "размер", "shadow": "тень", "duration": "длительность"}
# семейство токена по имени: первое совпадение по порядку (кегль раньше размера, толщина границы раньше цвета)
TOKEN_CATS = (
    ("breakpoint", re.compile(r"(^|-)(bp|breakpoint)(-|$)")),
    ("duration", re.compile(r"duration|(^|-)dur(-|$)|delay")),
    ("easing", re.compile(r"easing|(^|-)ease(-|$)|bezier")),
    ("shadow", re.compile(r"shadow|elevation")),
    ("radius", re.compile(r"radius|corner|rounded")),
    ("line-height", re.compile(r"line-height|leading|(^|-)lh(-|$)")),
    ("weight", re.compile(r"weight|(^|-)fw(-|$)")),
    ("letter-spacing", re.compile(r"tracking|letter")),
    ("font-size", re.compile(r"font-size|(^|-)fs(-|$)|^type-.+-size$|typescale")),
    ("family", re.compile(r"family|(^|-)font(-|$)")),
    ("border", re.compile(r"border-w|border-width|stroke-w")),
    ("spacing", re.compile(r"space|spacing|gap|gutter|inset|padding|margin")),
    ("size", re.compile(r"size|control|height|width|(^|-)(max|min)(-|$)|panel|row")),
)
SIZE_OK = ("size", "spacing")                          # размер элемента берёт значения размеров и шкалы отступов
KEYWORDS = {"auto", "none", "inherit", "initial", "unset", "revert", "transparent", "currentcolor", "normal", "0",
            "0px", "100%", "fit-content", "min-content", "max-content"}
NAMED = {"white": "#ffffff", "black": "#000000", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
         "gray": "#808080", "grey": "#808080", "silver": "#c0c0c0", "yellow": "#ffff00", "orange": "#ffa500"}
COLOR_RX = re.compile(r"#[0-9a-fA-F]{3,8}\b|(?:rgba?|hsla?|oklch)\([^()]*\)", re.I)
LEN_RX = re.compile(r"(?<![\w.#-])(-?\d*\.?\d+)(px|rem)\b", re.I)
NUM_RX = re.compile(r"^-?\d*\.?\d+$")
DUR_RX = re.compile(r"(?<![\w.])(\d*\.?\d+)(ms|s)\b")
SVG_COLOR_ATTRS = ("fill", "stroke", "stop-color", "color", "flood-color", "lighting-color")
COLOR_PROPS = {"color", "background-color", "border-color", "outline-color", "fill", "stroke", "stop-color",
               "caret-color", "accent-color", "text-decoration-color", "column-rule-color", "flood-color"}


class ToolError(RuntimeError):
    """Ошибка вызова или окружения — код выхода 2."""


# ------------------------------------------------------------------ цвет

def _clamp(x):
    return max(0.0, min(1.0, x))


def _pct(s, scale=1.0):
    s = s.strip()
    return float(s[:-1]) / 100.0 * scale if s.endswith("%") else float(s)


def _oklch_to_rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, \
        L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return tuple(_clamp(1.055 * c ** (1 / 2.4) - 0.055 if c > 0.0031308 else 12.92 * c) for c in lin)


def norm_color(s):
    """Цвет → '#rrggbb' или '#rrggbbaa' (строчными); не цвет — None."""
    s = (s or "").strip().lower()
    if s in NAMED:
        return NAMED[s]
    m = re.fullmatch(r"#([0-9a-f]{3,8})", s)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) not in (6, 8):
            return None
        return "#" + (h[:6] if h[6:] in ("", "ff") else h)
    m = re.fullmatch(r"(rgba?|hsla?|oklch)\((.*)\)", s)
    if not m:
        return None
    fn, body = m.group(1), m.group(2)
    parts = [p for p in re.split(r"[\s,/]+", body.strip()) if p]
    try:
        if fn.startswith("rgb") and len(parts) >= 3:
            rgb = [_pct(p, 255.0) / 255.0 if p.endswith("%") else float(p) / 255.0 for p in parts[:3]]
        elif fn.startswith("hsl") and len(parts) >= 3:
            h = float(parts[0].replace("deg", "")) / 360.0
            rgb = list(colorsys.hls_to_rgb(h % 1.0, _pct(parts[2]), _pct(parts[1])))
        elif fn == "oklch" and len(parts) >= 3:
            rgb = list(_oklch_to_rgb(_pct(parts[0]), float(parts[1]), float(parts[2].replace("deg", ""))))
        else:
            return None
        alpha = _pct(parts[3]) if len(parts) > 3 else 1.0
    except ValueError:
        return None
    out = "#" + "".join("%02x" % round(_clamp(c) * 255) for c in rgb)
    return out if alpha >= 0.999 else out + "%02x" % round(_clamp(alpha) * 255)


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(hexs):
    r, g, b = (_lin(int(hexs[i:i + 2], 16) / 255.0) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


# ------------------------------------------------------------------ значения

def px(value):
    """'24px' / '1.5rem' → 24.0 / 24.0; иначе None."""
    m = re.fullmatch(r"(-?\d*\.?\d+)(px|rem)", (value or "").strip().lower())
    if not m:
        return None
    return round(float(m.group(1)) * (16.0 if m.group(2) == "rem" else 1.0), 2)


def ms(value):
    m = re.fullmatch(r"(\d*\.?\d+)(ms|s)", (value or "").strip().lower())
    return None if not m else round(float(m.group(1)) * (1000.0 if m.group(2) == "s" else 1.0), 2)


def first_family(stack):
    return (stack or "").split(",")[0].strip().strip("\"'").strip().lower()


def weight_of(v):
    v = (v or "").strip().lower()
    return {"normal": 400.0, "bold": 700.0}.get(v, float(v) if NUM_RX.match(v) else None)


def norm_shadow(v):
    s = COLOR_RX.sub(lambda m: norm_color(m.group(0)) or m.group(0), (v or "").strip().lower())
    return re.sub(r"\s+", " ", re.sub(r"\s*,\s*", ", ", s))


def fmt(x):
    return ("%g" % x) if isinstance(x, float) else str(x)


# ------------------------------------------------------------------ токены ДС

@dataclass
class TokenSet:
    colors: dict = field(default_factory=dict)         # '#rrggbb' → [имена]
    lengths: dict = field(default_factory=dict)        # семейство → {px: [имена]}
    numbers: dict = field(default_factory=dict)        # line-height, weight → {число: [имена]}
    families: dict = field(default_factory=dict)       # первая гарнитура → [имена]
    shadows: dict = field(default_factory=dict)
    durations: dict = field(default_factory=dict)
    names: set = field(default_factory=set)            # имена CSS-переменных (адаптивная копия)
    themes: list = field(default_factory=list)
    breakpoints: list = field(default_factory=list)
    sources: list = field(default_factory=list)

    def put(self, bucket, key, name, cat=None):
        d = getattr(self, bucket)
        if cat is not None:
            d = d.setdefault(cat, {})
        d.setdefault(key, [])
        if name not in d[key]:
            d[key].append(name)

    def has(self, fam):
        if fam == "color":
            return bool(self.colors)
        if fam == "family":
            return bool(self.families)
        if fam == "shadow":
            return bool(self.shadows)
        if fam == "duration":
            return bool(self.durations)
        if fam in ("weight",):
            return bool(self.numbers.get("weight"))
        if fam == "line-height":
            return bool(self.numbers.get("line-height") or self.lengths.get("line-height"))
        if fam == "size":
            return any(self.lengths.get(c) for c in SIZE_OK)
        return bool(self.lengths.get(fam))


def token_cat(name):
    n = (name or "").lower().lstrip("-")
    for cat, rx in TOKEN_CATS:
        if rx.search(n):
            return cat
    return None


def add_value(ts, name, value, cat=None):
    """Значение токена по его виду: цвет, длина, число, длительность, тень, гарнитура."""
    v = (value or "").strip() if isinstance(value, str) else value
    cat = cat or token_cat(name)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if cat in ("line-height", "weight"):
            ts.put("numbers", round(float(v), 4), name, cat)
        elif cat in ("font-size", "spacing", "radius", "size", "border", "letter-spacing"):
            ts.put("lengths", round(float(v), 2), name, cat)
        return
    if not isinstance(v, str) or not v:
        return
    c = norm_color(v)
    if c:
        ts.put("colors", c, name)
        return
    if cat == "breakpoint":
        p = px(v)
        if p is not None and p not in ts.breakpoints:
            ts.breakpoints.append(p)
        return
    d = ms(v)
    if d is not None and cat in ("duration", None):
        ts.put("durations", d, name)
        return
    if cat == "shadow":
        ts.put("shadows", norm_shadow(v), name)
        for m in COLOR_RX.finditer(v):
            cc = norm_color(m.group(0))
            if cc:
                ts.put("colors", cc, name)
        return
    if cat == "family" or ("," in v and not re.search(r"\d", v.split(",")[0])):
        ts.put("families", first_family(v), name)
        return
    p = px(v)
    if p is not None and cat:
        ts.put("lengths", p, name, cat)
        return
    if NUM_RX.match(v) and cat in ("line-height", "weight"):
        ts.put("numbers", round(float(v), 4), name, cat)


def load_css_tokens(text, ts, source):
    """CSS-переменные всех блоков (темы, плотность, узкая ширина): значения, имена, темы, брейкпоинты."""
    decl = re.findall(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;{}]+);", text)
    raw = {}
    for name, val in decl:
        raw.setdefault(name, val.strip())
    for name, val in decl:
        v = val.strip()
        for _ in range(8):                               # var(--x) → значение x
            m = re.search(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,[^()]*)?\)", v)
            if not m or m.group(1) not in raw:
                break
            v = v[:m.start()] + raw[m.group(1)] + v[m.end():]
        ts.names.add(name)
        add_value(ts, name[2:], v)
    _theme(ts, "light")
    if re.search(r"data-theme=\"?dark|prefers-color-scheme:\s*dark", text):
        _theme(ts, "dark")
    ts.sources.append(source)


def _theme(ts, t):
    if t not in ts.themes:
        ts.themes.append(t)


def load_artifact_tokens(data, ts, source):
    """tokens.json артефакта Design System: списки {name, value} по семействам, цвет по темам, стили текста."""
    by_name = {}
    for fam, block in data.items():
        if isinstance(block, dict) and isinstance(block.get("tokens"), list):
            for t in block["tokens"]:
                if isinstance(t, dict) and t.get("name"):
                    by_name[t["name"]] = t.get("value")

    def resolve(v, theme=None, depth=0):
        if isinstance(v, dict):
            v = v.get(theme) if theme in v else next(iter(v.values()), None)
        if isinstance(v, str) and re.fullmatch(r"\{[^{}]+\}", v.strip()) and depth < 8:
            return resolve(by_name.get(v.strip()[1:-1]), theme, depth + 1)
        return v

    color = data.get("color") if isinstance(data.get("color"), dict) else {}
    themes = [str(t.get("id")) for t in color.get("themes") or [] if isinstance(t, dict) and t.get("id")]
    for t in themes or ["light"]:
        _theme(ts, t)
    fam_cat = {"spacing": "spacing", "radius": "radius", "shadow": "shadow"}     # прочие семейства — по имени токена
    for fam, block in data.items():
        if not isinstance(block, dict) or not isinstance(block.get("tokens"), list):
            continue
        for t in block["tokens"]:
            if not isinstance(t, dict) or not t.get("name"):
                continue
            name, value = t["name"], t.get("value")
            ts.names.add("--" + name)
            cat = fam_cat.get(fam) or token_cat(name)
            if isinstance(value, dict):
                for th in value:
                    add_value(ts, name, resolve(value, th), cat)
            else:
                add_value(ts, name, resolve(value), cat)
    typ = data.get("type") if isinstance(data.get("type"), dict) else {}
    for key, stack in (typ.get("families") or {}).items():
        ts.names.add(f"--font-{key}")
        ts.put("families", first_family(str(stack)), f"font-{key}")
    for grp in typ.get("groups") or []:
        for st in (grp or {}).get("styles") or []:
            nm = str(st.get("name") or "style")
            if st.get("fontSize") is not None:
                add_value(ts, nm, str(st["fontSize"]) if isinstance(st["fontSize"], str) else st["fontSize"], "font-size")
            if st.get("lineHeight") is not None:
                lh = st["lineHeight"]
                if isinstance(lh, str) and px(lh) is not None:
                    ts.put("lengths", px(lh), nm, "line-height")
                else:
                    add_value(ts, nm, float(lh) if not isinstance(lh, str) else lh, "line-height")
            if st.get("fontWeight") is not None:
                add_value(ts, nm, float(st["fontWeight"]) if not isinstance(st["fontWeight"], str) else st["fontWeight"],
                          "weight")
            if st.get("letterSpacing") is not None:
                add_value(ts, nm, st["letterSpacing"], "letter-spacing")
    ts.sources.append(source)


def is_dtcg(data):
    def walk(x, depth=0):
        if isinstance(x, dict):
            if "$value" in x:
                return True
            return depth < 6 and any(walk(v, depth + 1) for k, v in x.items() if not str(k).startswith("$"))
        return False
    return walk(data)


def load_tokens(paths):
    """Токены ДС из файлов: .css — переменные; .json — DTCG (через сборку CSS ds_build) или tokens.json артефакта."""
    ts = TokenSet()
    for p in paths:
        p = Path(p)
        if not p.is_file():
            raise ToolError(f"нет файла токенов: {p}")
        text = p.read_text(encoding="utf-8")
        if p.suffix.lower() == ".css":
            load_css_tokens(text, ts, str(p))
            continue
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ToolError(f"{p}: не JSON ({e})") from e
        if isinstance(data, dict) and is_dtcg(data):
            import ds_build
            load_css_tokens(ds_build.build_css(ds_build.Tokens(data)), ts, str(p))
        elif isinstance(data, dict):
            load_artifact_tokens(data, ts, str(p))
        else:
            raise ToolError(f"{p}: не токены ДС (ожидается DTCG, tokens.json артефакта или CSS)")
    ts.breakpoints.sort()
    return ts


# ------------------------------------------------------------------ литералы

@dataclass
class Literal:
    family: str
    raw: str
    key: object                                        # нормализованное значение
    line: int
    prop: str
    where: str = "style"                               # style · attr · tweak · css


def declarations(style):
    """'a: b; c: d' → [(свойство, значение)]; точка с запятой внутри скобок и кавычек не делит."""
    out, buf, depth, q = [], "", 0, None
    for ch in (style or "") + ";":
        if q:
            buf += ch
            q = None if ch == q else q
            continue
        if ch in "\"'":
            q = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch == ";" and depth == 0:
            if ":" in buf:
                k, v = buf.split(":", 1)
                if k.strip():
                    out.append((k.strip().lower(), v.strip()))
            buf = ""
            continue
        buf += ch
    return out


def css_rules(text):
    """Объявления блоков CSS (без @-правил с вложенностью глубже одного уровня): [(свойство, значение, смещение)]."""
    out = []
    for m in re.finditer(r"\{([^{}]*)\}", text or ""):
        for k, v in declarations(m.group(1)):
            out.append((k, v, m.start(1)))
    return out


def lengths_in(v):
    return [(m.group(0), round(float(m.group(1)) * (16.0 if m.group(2).lower() == "rem" else 1.0), 2))
            for m in LEN_RX.finditer(v)]


def literals_of(prop, value, line, where="style"):
    """Литералы облика в одном объявлении CSS."""
    v = value.strip()
    low = v.lower()
    if not v or low in KEYWORDS or "var(" in low and not COLOR_RX.search(v) and not LEN_RX.search(v):
        return []
    out = []

    def colors(s):
        for m in COLOR_RX.finditer(s):
            c = norm_color(m.group(0))
            if c:
                out.append(Literal("color", m.group(0), c, line, prop, where))
        for w in re.findall(r"(?<![\w#-])([a-z]+)(?![\w(-])", s.lower()):
            if w in NAMED and prop in COLOR_PROPS | {"background", "border", "outline"}:
                out.append(Literal("color", w, NAMED[w], line, prop, where))

    def lens(s, fam):
        for raw, p in lengths_in(s):
            if p != 0:
                out.append(Literal(fam, raw, p, line, prop, where))

    base = prop.split("-")[0]
    if prop in COLOR_PROPS:
        colors(v)
    elif prop in ("background", "background-image"):
        colors(re.sub(r"url\([^)]*\)", "", v))
    elif prop in ("box-shadow", "text-shadow"):
        out.append(Literal("shadow", v, norm_shadow(v), line, prop, where))
        colors(v)
    elif base in ("border", "outline") and "radius" not in prop:
        colors(v)
        if not prop.endswith("-color") and not prop.endswith("-style"):
            lens(COLOR_RX.sub(" ", v), "border")
    elif "radius" in prop:
        lens(v, "radius")
    elif base in ("padding", "margin") or prop in ("gap", "row-gap", "column-gap", "grid-gap", "grid-row-gap",
                                                     "grid-column-gap"):
        lens(v, "spacing")
    elif prop in ("width", "height", "min-width", "min-height", "max-width", "max-height", "inline-size", "block-size"):
        lens(v, "size")
    elif prop == "font-size":
        lens(v, "font-size")
    elif prop == "line-height":
        if NUM_RX.match(low):
            out.append(Literal("line-height", v, round(float(low), 4), line, prop, where))
        else:
            lens(v, "line-height")
    elif prop == "font-weight":
        w = weight_of(low)
        if w is not None:
            out.append(Literal("weight", v, w, line, prop, where))
    elif prop == "font-family":
        f = first_family(v)
        if f and f not in ("inherit", "system-ui", "sans-serif", "serif", "monospace"):
            out.append(Literal("family", v.split(",")[0].strip(), f, line, prop, where))
    elif prop == "letter-spacing":
        lens(v, "letter-spacing")
    elif prop == "font":
        m = re.match(r"^\s*(?:(italic|oblique|normal)\s+)?(?:(\d{3}|bold|normal)\s+)?(\d*\.?\d+(?:px|rem))"
                     r"(?:\s*/\s*(\d*\.?\d+(?:px|rem)?))?\s+(.+)$", v, re.I)
        if m:
            if m.group(2):
                out.append(Literal("weight", m.group(2), weight_of(m.group(2)), line, prop, where))
            out.append(Literal("font-size", m.group(3), px(m.group(3)), line, prop, where))
            if m.group(4):
                lh = m.group(4)
                out.append(Literal("line-height", lh, px(lh) if px(lh) is not None else round(float(lh), 4), line,
                                   prop, where))
            f = first_family(m.group(5))
            if f:
                out.append(Literal("family", m.group(5).split(",")[0].strip(), f, line, prop, where))
    elif prop in ("transition", "transition-duration", "animation", "animation-duration", "transition-delay",
                  "animation-delay"):
        for m in DUR_RX.finditer(low):
            out.append(Literal("duration", m.group(0), ms(m.group(0)), line, prop, where))
    return out


def in_tokens(lit, ts):
    """(в токенах, семейство есть в ДС)."""
    f = lit.family
    if not ts.has(f):
        return False, False
    if f == "color":
        return lit.key in ts.colors, True
    if f == "family":
        return lit.key in ts.families, True
    if f == "shadow":
        return lit.key in ts.shadows, True
    if f == "duration":
        return lit.key in ts.durations, True
    if f == "weight":
        return lit.key in ts.numbers.get("weight", {}), True
    if f == "line-height":
        return (lit.key in ts.numbers.get("line-height", {}) or lit.key in ts.lengths.get("line-height", {})), True
    if f == "size":
        return any(lit.key in ts.lengths.get(c, {}) for c in SIZE_OK), True
    return lit.key in ts.lengths.get(f, {}), True


def nearest(lit, ts):
    """Ближайшее значение токена: цвет — по OKLab, длина и число — по модулю разности."""
    try:
        if lit.family == "color":
            if not ts.colors or len(lit.key) < 7:
                return None
            a = oklab(lit.key[:7])
            best = min(ts.colors, key=lambda c: sum((x - y) ** 2 for x, y in zip(a, oklab(c[:7]))))
            return f"{', '.join(ts.colors[best][:2])} {best}"
        pool = {}
        if lit.family == "size":
            for c in SIZE_OK:
                pool.update(ts.lengths.get(c, {}))
        elif lit.family in ("weight",):
            pool = ts.numbers.get("weight", {})
        elif lit.family == "line-height":
            pool = dict(ts.numbers.get("line-height", {}))
            pool.update(ts.lengths.get("line-height", {}))
        elif lit.family == "duration":
            pool = ts.durations
        else:
            pool = ts.lengths.get(lit.family, {})
        nums = [k for k in pool if isinstance(k, (int, float))]
        if not nums or not isinstance(lit.key, (int, float)):
            return None
        best = min(nums, key=lambda k: abs(k - lit.key))
        unit = "px" if lit.family not in ("weight", "line-height", "duration") else ("ms" if lit.family == "duration" else "")
        if lit.family == "line-height" and best in ts.lengths.get("line-height", {}):
            unit = "px"
        return f"{', '.join(pool[best][:2])} {fmt(best)}{unit}"
    except (ValueError, TypeError):
        return None


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def artboard_literals(ab, vals, props):
    """Литералы облика артборда: стили элементов, <style>, цветовые атрибуты SVG, твики. Рамка — не литерал."""
    text = ab.text
    lits = []
    tr = DC.Translator(ab, vals, props)
    scope = [vals, props]
    offsets = _offsets(ab.root)
    for node in DC.walk(ab.root):
        if not isinstance(node, DC.El) or node.tag == "#root" or DC.is_logic(node):
            continue
        line = line_of(text, offsets.get(id(node), 0))
        style = node.attrs.get("style")
        if style:
            style = DC.HOLE.sub(lambda m: DC.as_text(tr.value(m.group(1), scope)), style)
            for prop, value in declarations(style):
                if node is ab.frame and prop in ("width", "height"):
                    continue
                lits += literals_of(prop, value, line)
        for attr in SVG_COLOR_ATTRS:
            if attr in node.attrs and node.tag not in ("html", "body", "meta"):
                v = DC.HOLE.sub(lambda m: DC.as_text(tr.value(m.group(1), scope)), node.attrs[attr])
                lits += [x for x in literals_of("fill" if attr != "color" else "color", v, line, "attr")]
        if node.tag == "style":
            css = "".join(c.raw for c in node.children if isinstance(c, DC.Tx))
            base = offsets.get(id(node), 0) + len(node.raw)
            for prop, value, off in css_rules(css):
                lits += literals_of(prop, value, line_of(text, base + off), "css")
    if ab.logic is not None:
        line = line_of(text, offsets.get(id(ab.logic), 0))
        for name, spec in ab.props_spec.items():
            if name.startswith("$") or not isinstance(spec, dict) or spec.get("editor") != "color":
                continue
            for i, v in enumerate([spec.get("default")] + list(spec.get("options") or [])):
                c = norm_color(str(v)) if v is not None else None
                if c:
                    lits.append(Literal("color", str(v), c, line, f"твик {name}" + (" (умолчание)" if i == 0 else ""),
                                        "tweak"))
    return lits


def _offsets(root):
    out, pos = {}, 0

    def rec(n):
        nonlocal pos
        if isinstance(n, DC.Tx):
            pos += len(n.raw)
            return
        if n.tag != "#root":
            out[id(n)] = pos
            pos += len(n.raw)
        for c in n.children:
            rec(c)
        if n.tag != "#root":
            pos += len(n.end)
    rec(root)
    return out


# ------------------------------------------------------------------ сверка

@dataclass
class Group:
    family: str
    raw: str
    key: object
    lines: list
    props: list
    where: set
    near: str | None = None
    count: int = 0


def compare(lits, ts):
    """Литералы вне токенов, сгруппированные по (семейство, значение); семейства без токенов в ДС — заметкой."""
    groups, skipped = {}, set()
    for lit in lits:
        ok, known = in_tokens(lit, ts)
        if not known:
            skipped.add(lit.family)
            continue
        if ok:
            continue
        g = groups.get((lit.family, lit.key))
        if g is None:
            g = groups[(lit.family, lit.key)] = Group(lit.family, lit.raw, lit.key, [], [], set(), nearest(lit, ts))
        g.count += 1
        if lit.line not in g.lines:
            g.lines.append(lit.line)
        if lit.prop not in g.props:
            g.props.append(lit.prop)
        g.where.add(lit.where)
    return sorted(groups.values(), key=lambda g: (FAMILIES.index(g.family), g.lines[0])), sorted(skipped)


def message(g):
    count = g.count
    lines = ", ".join(str(x) for x in sorted(g.lines)[:8]) + (" …" if len(g.lines) > 8 else "")
    where = "; ".join(g.props[:4])
    near = f"; ближайший токен — {g.near}" if g.near else ""
    return (f"{FAMILY_RU[g.family]} `{g.raw}` вне токенов ДС ({where}): мест {count}, строки {lines}{near}")


FIX = ("литерал → значение токена ДС: разовая правка — ближайший токен, системная — токен или ручка DTCG; решает "
       "заказчик как владелец облика (references/claude-design.md § Правки токенов)")


def scan_boards(files, ts, canvas=None, all_stages=False):
    """[(артборд, этап, группы, пропущенные семейства)] для файлов .dc.html."""
    boards = [DC.load(p) for p in files]
    out = []
    for ab, (vals, props) in zip(boards, DC.render_values(boards)):
        board = (canvas or {}).get("boards", {}).get(ab.name) if canvas else None
        stage = DC.stage_of(board, canvas)
        if stage != "mockup" and not all_stages:
            out.append((ab, stage, None, []))
            continue
        lits = artboard_literals(ab, vals, props)
        groups, skipped = compare(lits, ts)
        out.append((ab, stage, groups, skipped))
    return out


def adaptive_findings(path, ts, rep, surface, repo, severity):
    """Адаптивная копия: значения облика — только var(--…) из system.tokens.css."""
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    root, _notes = DC.parse(text)
    offs = _offsets(root)
    bad, unknown = {}, {}
    for node in DC.walk(root):
        if not isinstance(node, DC.El) or node.tag == "#root":
            continue
        decls = []
        if node.attrs.get("style"):
            decls += [(k, v, offs.get(id(node), 0)) for k, v in declarations(node.attrs["style"])]
        if node.tag == "style":
            css = "".join(c.raw for c in node.children if isinstance(c, DC.Tx))
            base = offs.get(id(node), 0) + len(node.raw)
            decls += [(k, v, base + o) for k, v, o in css_rules(css) if not k.startswith("--")]
        for prop, value, off in decls:
            for m in re.finditer(r"var\(\s*(--[A-Za-z0-9_-]+)", value):
                if m.group(1) not in ts.names:
                    unknown.setdefault(m.group(1), []).append(line_of(text, off))
            plain = re.sub(r"var\([^()]*(?:\([^()]*\)[^()]*)*\)", " ", value)
            for lit in literals_of(prop, plain, line_of(text, off), "css"):
                if ts.has(lit.family):
                    bad.setdefault((lit.family, lit.raw), []).append(lit.line)
    rel = docpaths.rel(path, repo)
    name = Path(path).name
    for (fam, raw), lines in sorted(bad.items(), key=lambda x: (FAMILIES.index(x[0][0]), x[1][0])):
        rep.add(RULE, severity, surface=surface, kind="copy", ref=f"{name}#{fam}:{raw}", path=rel,
                message=f"адаптивная копия: {FAMILY_RU[fam]} `{raw}` литералом, а не var(--…) system.tokens.css "
                        f"(мест {len(lines)}, строки {', '.join(str(x) for x in sorted(set(lines))[:8])})",
                fix="значение облика адаптивной копии — переменная system.tokens.css")
    for var, lines in sorted(unknown.items()):
        rep.add(RULE, severity, surface=surface, kind="copy", ref=f"{name}#{var}", path=rel,
                message=f"адаптивная копия: переменной {var} нет в system.tokens.css "
                        f"(строки {', '.join(str(x) for x in sorted(set(lines))[:8])})",
                fix="имя переменной — путь токена DTCG через дефис (ds_build show)")


def project_tokens(call):
    """Файлы токенов продукта по старшинству и копия ДС, установленная в холст."""
    css = docpaths.design(call.slug, "tokens-css", repo=call.repo)
    dtcg = docpaths.design(call.slug, "tokens", repo=call.repo)
    art = docpaths.design(call.slug, "ds-project", repo=call.repo) / "tokens.json"
    files = [css] if css.is_file() else [dtcg] if dtcg.is_file() else [art] if art.is_file() else []
    src = docpaths.design(call.slug, "canvas-project", surface=call.surface, repo=call.repo)
    files += sorted(src.glob("ds/*/tokens.json")) if src.is_dir() else []
    return files


def cmd_check(call):
    rep = FND.Report()
    sev = "error" if call.args.accepted else "warning"
    src = docpaths.design(call.slug, "canvas-project", surface=call.surface, repo=call.repo)
    html_dir = docpaths.design(call.slug, "canvas-html", surface=call.surface, repo=call.repo)
    tok_files = project_tokens(call)
    if not src.is_dir():
        FND.print_findings([], as_json=call.json)
        return 0
    if not tok_files:
        rep.add(RULE, "hint", surface=call.surface, kind="canvas", ref=call.surface,
                path=docpaths.rel(docpaths.design(call.slug, repo=call.repo), call.repo),
                message="нет токенов ДС продукта (system.tokens.css, system.tokens.json, tokens.json артефакта): литералы "
                        "холста сверять не с чем", fix="этап design-system — /design-deep-dive " + call.slug)
        FND.print_findings(rep.items, as_json=call.json)
        return rep.exit_code()
    ts = load_tokens(tok_files)
    canvas = DC.load_canvas(src)
    for ab, stage, groups, skipped in scan_boards(DC.artboard_files(src, canvas), ts, canvas, call.args.all_stages):
        if groups is None:
            continue
        rel = docpaths.rel(ab.path, call.repo)
        for g in groups:
            rep.add(RULE, sev, surface=call.surface, kind="artboard", ref=f"{ab.name}#{g.family}:{g.raw}", path=rel,
                    message=message(g), fix=FIX)
        for fam in skipped:
            rep.add(RULE, "hint", surface=call.surface, kind="artboard", ref=f"{ab.name}#{fam}", path=rel,
                    message=f"{FAMILY_RU[fam]}: в ДС нет токенов этого семейства — литералы не сверялись",
                    fix="пробел ДС — этап design-system")
    if html_dir.is_dir() and any(n.startswith("--") for n in ts.names):
        for p in sorted(html_dir.glob("*.html")):
            if not DC.copy_source(p.read_text(encoding="utf-8", errors="replace")):
                adaptive_findings(p, ts, rep, call.surface, call.repo, sev)
    FND.print_findings(rep.items, as_json=call.json,
                       title=None if call.json else f"literal_tokens check {call.slug} {call.surface}")
    return rep.exit_code()


def cmd_scan(a):
    ts = load_tokens(a.tokens)
    rep = FND.Report()
    for s in a.source:
        s = Path(s)
        if s.is_dir():
            canvas = DC.load_canvas(s)
            files = DC.artboard_files(s, canvas)
        elif s.is_file():
            canvas, files = DC.load_canvas(s.parent), [s]
        else:
            raise ToolError(f"нет файла или папки: {s}")
        for ab, stage, groups, skipped in scan_boards(files, ts, canvas, a.all_stages):
            if groups is None:
                continue
            for g in groups:
                rep.add(RULE, "warning", surface=None, kind="artboard", ref=f"{ab.name}#{g.family}:{g.raw}",
                        path=str(ab.path), message=message(g), fix=FIX)
            for fam in skipped:
                rep.add(RULE, "hint", surface=None, kind="artboard", ref=f"{ab.name}#{fam}", path=str(ab.path),
                        message=f"{FAMILY_RU[fam]}: в ДС нет токенов этого семейства — литералы не сверялись",
                        fix="пробел ДС — этап design-system")
    FND.print_findings(rep.items, as_json=a.json, title=None if a.json else "literal_tokens scan")
    return rep.exit_code()


def cmd_tokens(a):
    ts = load_tokens(a.files)
    d = {"sources": ts.sources, "themes": ts.themes, "breakpoints": ts.breakpoints,
         "colors": {k: v for k, v in sorted(ts.colors.items())},
         "lengths": {c: {fmt(k): v for k, v in sorted(d.items())} for c, d in sorted(ts.lengths.items())},
         "numbers": {c: {fmt(k): v for k, v in sorted(d.items())} for c, d in sorted(ts.numbers.items())},
         "families": ts.families, "shadows": ts.shadows,
         "durations": {fmt(k): v for k, v in sorted(ts.durations.items())}}
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=1))
    else:
        for k in ("themes", "breakpoints"):
            print(f"{k}: {d[k]}")
        print("цвета:", len(d["colors"]), "· длины:", {c: len(v) for c, v in d["lengths"].items()}, "· числа:",
              {c: len(v) for c, v in d["numbers"].items()}, "· гарнитуры:", sorted(d["families"]), "· тени:",
              len(d["shadows"]), "· длительности:", sorted(d["durations"]))
    return 0


# ------------------------------------------------------------------ самопроверка

def selftest():
    import subprocess
    import tempfile
    ok = True

    def check(name, got, want=True):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"{'OK  ' if good else 'FAIL'} {name}" + ("" if good else f": {got!r} (ожидалось {want!r})"))

    check("цвет #ABC → #aabbcc", norm_color("#ABC"), "#aabbcc")
    check("rgb(2 6 23 / 0.08) → #02061714", norm_color("rgb(2 6 23 / 0.08)"), "#02061714")
    check("rgba(255, 255, 255, 1) → #ffffff", norm_color("rgba(255, 255, 255, 1)"), "#ffffff")
    check("hsl(0, 0%, 100%) → #ffffff", norm_color("hsl(0, 0%, 100%)"), "#ffffff")
    check("oklch(1 0 0) → #ffffff", norm_color("oklch(1 0 0)"), "#ffffff")
    check("семейство токена: --type-title-size → кегль", token_cat("type-title-size"), "font-size")
    check("семейство токена: --size-control-md → размер", token_cat("size-control-md"), "size")
    check("семейство токена: border-w → толщина", token_cat("border-w"), "border")
    check("семейство токена: --motion-duration-fast → длительность", token_cat("motion-duration-fast"), "duration")
    check("font: 600 17px/1.3 'Golos Text' → 4 литерала",
          sorted((x.family, x.key) for x in literals_of("font", "600 17px/1.3 'Golos Text', system-ui", 1)),
          [("family", "golos text"), ("font-size", 17.0), ("line-height", 1.3), ("weight", 600.0)])
    check("border: 1px solid #CFD6DF → толщина и цвет",
          sorted((x.family, x.key) for x in literals_of("border", "1px solid #CFD6DF", 1)),
          [("border", 1.0), ("color", "#cfd6df")])
    check("padding: 0 120px → один отступ", [(x.family, x.key) for x in literals_of("padding", "0 120px", 1)],
          [("spacing", 120.0)])
    check("проценты и ch — не литералы", literals_of("max-width", "34ch", 1) + literals_of("width", "95%", 1), [])
    ex = DC.EXAMPLE
    art = ex / "design-system" / "project" / "tokens.json"
    ts = load_tokens([art])
    check("артефакт «Спицы»: темы light и dark", ts.themes, ["light", "dark"])
    check("артефакт: тёмный фон #0C0F14 в цветах", "#0c0f14" in ts.colors, True)
    check("артефакт: отступы 4…104 и gutter 40", sorted(ts.lengths.get("spacing", {})),
          [4.0, 8.0, 12.0, 16.0, 24.0, 32.0, 40.0, 48.0, 64.0, 104.0])
    check("артефакт: кегли стилей и typescale", sorted(ts.lengths.get("font-size", {})),
          [14.0, 17.0, 20.0, 21.0, 36.0, 60.0])
    check("артефакт: гарнитуры", sorted(ts.families), ["golos text", "unbounded"])
    check("артефакт: толщина границы border-w 1px", sorted(ts.lengths.get("border", {})), [1.0])
    src = ex / "canvas" / "project"
    res = {ab.name: (stage, groups) for ab, stage, groups, _s in scan_boards(DC.artboard_files(src), ts, DC.load_canvas(src))}
    check("сверяются артборды макета: Main, Landing-Phone, Booking",
          sorted(n for n, (st, g) in res.items() if g is not None), ["Booking.dc.html", "Landing-Phone.dc.html",
                                                                      "Main.dc.html"])
    main = {(g.family, g.raw) for g in res["Main.dc.html"][1]}
    check("Main: отступ 120px вне шкалы", ("spacing", "120px") in main, True)
    check("Main: образец твика #0B6E4F вне палитры", ("color", "#0B6E4F") in main, True)
    check("Main: цвета фона и текста из токенов", any(f == "color" and r in ("#EEF2F6", "#11151C") for f, r in main), False)
    check("Main: радиусы твика 6 и 12 — токены", any(f == "radius" for f, _ in main), False)
    bk = {(g.family, g.raw) for g in res["Booking.dc.html"][1]}
    check("Booking: тёмная палитра renderVals — токены", any(f == "color" and r.startswith("#0C0F14") for f, r in bk), False)
    fx_css = kbpaths.scripts("tests", "fixtures", "cabinet-ds", "files", "design", "system.tokens.css")
    tc = load_tokens([fx_css])
    check("CSS фикстуры cabinet-ds: брейкпоинты", tc.breakpoints, [640.0, 1024.0, 1440.0])
    check("CSS: темы light и dark", tc.themes, ["light", "dark"])
    check("CSS: длительности", sorted(tc.durations), [100.0, 150.0, 200.0])
    check("CSS: тень elevation-raised", len(tc.shadows) >= 1, True)
    fx_dtcg = kbpaths.scripts("tests", "fixtures", "cabinet-ds", "files", "design", "system.tokens.json")
    td_ = load_tokens([fx_dtcg])
    check("DTCG через ds_build: те же значения, что CSS", (sorted(td_.colors), td_.breakpoints),
          (sorted(tc.colors), tc.breakpoints))
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "Page.dc.html"
        p.write_text('<!doctype html><html><head><script src="./support.js"></script></head><body><x-dc><helmet>'
                     '<style>a{color:#2146D8}</style></helmet><div style="width: 300px; height: 200px; background: '
                     '#EEF2F6; padding: 24px 30px; box-shadow: 0 1px 2px #000;"><p style="font-size: 17px; '
                     'color: #123456;">т</p></div></x-dc></body></html>', encoding="utf-8")
        (Path(td) / "canvas.json").write_text(json.dumps({"boards": {"Page.dc.html": {"w": 300, "h": 200, "page": "hifi"}},
                                                          "order": ["Page.dc.html"], "pages": [{"id": "hifi"}]}),
                                              encoding="utf-8")
        r = subprocess.run([sys.executable, __file__, "scan", td, "--tokens", str(art), "--json"], capture_output=True,
                           text=True)
        items = FND.parse_lines(r.stdout)
        got = sorted((f.severity, f.ref.split("#", 1)[1]) for f in items)
        check("scan: отступ 30px, цвета #123456 и #000 тени — находки, тень без токенов — заметка",
              got, [("hint", "shadow"), ("warning", "color:#000"), ("warning", "color:#123456"),
                    ("warning", "spacing:30px")])
        check("scan: ближайший токен названа", any("ближайший токен" in f.message for f in items), True)
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("canvas") as fx:
        argv = [fx.slug, "promo", "--repo", str(fx.root)]
        r = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json"], capture_output=True, text=True)
        items = FND.parse_lines(r.stdout)
        check("фикстура canvas: check — код 0 (warning не ошибка)", r.returncode, 0)
        check("фикстура canvas: находки только warning и hint", {f.severity for f in items} <= {"warning", "hint"}, True)
        check("фикстура canvas: все находки — R-VIS-004", {f.rule for f in items}, {RULE})
        r2 = subprocess.run([sys.executable, __file__, "check"] + argv + ["--json", "--accepted"], capture_output=True,
                            text=True)
        check("--accepted: литералы — error, код 1", (r2.returncode, any(f.severity == "error" for f in
                                                                           FND.parse_lines(r2.stdout))), (1, True))
    print("selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if argv[:1] in (["scan"], ["tokens"]):
            ap = argparse.ArgumentParser(prog=f"literal_tokens.py {argv[0]}")
            ap.add_argument("cmd")
            if argv[0] == "scan":
                ap.add_argument("source", nargs="+", help="файл .dc.html или папка исходников холста")
                ap.add_argument("--tokens", action="append", required=True,
                                help="токены ДС: system.tokens.css, DTCG .json или tokens.json артефакта; повтором")
                ap.add_argument("--all-stages", action="store_true", help="сверять и «Направления», и «Вайрфрейм»")
            else:
                ap.add_argument("files", nargs="+")
            ap.add_argument("--json", action="store_true")
            a = ap.parse_args(argv)
            return cmd_scan(a) if argv[0] == "scan" else cmd_tokens(a)
        ap = docpaths.parser("literal_tokens.py", __doc__, commands=("check",), surface="required",
                             accept=lambda s: s.design)
        ap.add_argument("--accepted", action="store_true", help="макет принят: литерал вне токенов — error")
        ap.add_argument("--all-stages", action="store_true", help="сверять и «Направления», и «Вайрфрейм»")
        call = docpaths.parse(ap, argv)
        if call.selftest:
            return selftest()
        return cmd_check(call)
    except (ToolError, DC.ToolError) as e:
        print(f"literal_tokens: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
