#!/usr/bin/env python3
"""ds_sync — правки токенов с claude.ai обратно в DTCG: «имя ДС → путь DTCG» и сверка живого tokens.json артефакта.

Артефакт Design System собирается из токенов DTCG продукта в одну сторону (`ds_build`). Правка заказчика на странице
артефакта без подъёма в DTCG стёрлась бы следующей сборкой, поэтому по протоколу холста
(`references/claude-design.md § Правки заказчика`, «Правки токенов») живой `project/tokens.json` читается с claude.ai,
сохраняется файлом и сверяется со сборкой из `docs/projects/<slug>/design/system.tokens.json`:

  - изменилось значение известного имени — правка его пути DTCG в своей теме: имя CSS-переменной совпадает с путём
    токена через дефис (`color-accent-solid` ↔ `color.accent.solid`), тема `light` — `$value`, другая —
    `$extensions["org.design-deep-dive.modes"].<тема>`; поле стиля текста — поле составного `$value`; `usage` —
    `$description`; образец стиля — `$extensions["org.design-deep-dive.artifact"].sample`;
  - новое или удалённое имя, значение, которое не переводится в тип токена, — вопрос заказчику: роль и назначение или
    отказ; сами они в DTCG не пишутся.
Правка токена-алиаса — развилка для владельца, предложение называет обе дороги и соседей на том же примитиве: роль —
`build --write` пишет литерал в её путь (ссылка на примитив рвётся); примитив — значение пути `primitive.…` в
`system.tokens.json` правится руками (команды у этой дороги нет), за ним меняются все роли-ссылки. После любой дороги —
пересчёт контраста пар токенов проекта (`lib/color.py contrast`), пересборка производных (`ds_build build`) и
публикация ДС.

Нет токенов DTCG (артефакт пришёл без исходников) — `build` восстанавливает их из живого tokens.json: путь — имя по
дефисам, первый сегмент — группа семейства (`color-bg` → `color.bg`, `space-4` → `space.4`, `radius-sm` → `radius.sm`,
семейство `type`: гарнитура `display` → `font.display`, стиль `h2` → `type.h2`); имя без префикса группы — токен
верхнего уровня (`gutter`) с семейством в `$extensions["org.design-deep-dive.artifact"].family`. Имя системы и заметки
семейств — там же в корне. Сборка `ds_build` из восстановленных токенов даёт те же имена и значения.

    ds_sync check <slug> --live FILE [--repo DIR] [--json]                 расхождения живого tokens.json со сборкой
    ds_sync build <slug> --live FILE [--repo DIR] [--write | --out DIR] [--json]
                        правки DTCG: без ключа — предложение, --write — запись по месту (дифф — только правленые
                        значения), --out DIR — копия в DIR/docs/projects/…
    ds_sync show  <slug> [--live FILE] [--repo DIR] [--json]               соответствие «имя ДС → путь DTCG»
    ds_sync --selftest                                                    без сети: сверка, правки, круг на примере cd

Правило `check`: R-FRESH-001 — правка заказчика на странице артефакта, не поднятая в токены (живой tokens.json ≠
сборка из токенов), error на каждое расхождение; расхождение, где новее токены (примитив правлен руками, ДС ещё не
опубликована), сходится публикацией ДС.
Код выхода: 0 — расхождений нет (у build — предложение готово), 1 — есть расхождения, 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from json.decoder import scanstring
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402
import findings as F  # noqa: E402
import ds_build as B  # noqa: E402

KIND = B.KIND
CANON_GROUP = {"color": "color", "spacing": "space", "radius": "radius", "shadow": "shadow"}
NUMBER = re.compile(r"^-?\d+(?:\.\d+)?$")
DIMENSION = re.compile(r"^(-?\d+(?:\.\d+)?)(px|rem)$")
DURATION = re.compile(r"^(-?\d+(?:\.\d+)?)(ms|s)$")
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
RGB = re.compile(r"^rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)\s*(?:[/,]\s*([\d.]+))?\s*\)$")
BEZIER = re.compile(r"^cubic-bezier\(([^)]*)\)$")


# ------------------------------------------------------------------ плоский вид tokens.json артефакта

@dataclass
class Entry:
    """Запись tokens.json артефакта: семейство, имя, значение, usage и поля стиля."""
    family: str                                            # color · type.families · type.styles · <семейство>
    name: str
    value: object
    usage: str = ""
    extra: dict = field(default_factory=dict)              # у стиля: group, family, sample

    @property
    def key(self):
        return (self.family, self.name)

    @property
    def label(self):
        return f"--font-{self.name}" if self.family == "type.families" else \
            (f".{self.name}" if self.family == "type.styles" else f"--{self.name}")


def flatten(doc):
    """tokens.json артефакта → [Entry] по порядку; нераспознанное — ValueError."""
    if not isinstance(doc, dict):
        raise ValueError("tokens.json артефакта — не объект JSON")
    out = []
    for fam, body in doc.items():
        if fam in ("name", "version", "meta", "example") or not isinstance(body, dict):
            continue
        if fam == "color":
            for t in body.get("tokens") or []:
                out.append(Entry("color", t.get("name"), t.get("value"), t.get("usage") or ""))
        elif fam == "type":
            for k, v in (body.get("families") or {}).items():
                out.append(Entry("type.families", k, v))
            for g in body.get("groups") or []:
                for s in g.get("styles") or []:
                    val = {k: s.get(k) for k in ("fontSize", "lineHeight", "fontWeight") if k in s}
                    out.append(Entry("type.styles", s.get("name"), val, s.get("usage") or "",
                                     {"group": g.get("name"), "family": g.get("family"), "sample": s.get("sample")}))
        else:
            for t in body.get("tokens") or []:
                out.append(Entry(fam, t.get("name"), t.get("value"), t.get("usage") or ""))
    return out


def themes_of(doc):
    return [t.get("id") for t in ((doc.get("color") or {}).get("themes") or []) if isinstance(t, dict)]


# ------------------------------------------------------------------ «имя ДС → путь DTCG»

def name_map(toks):
    """{(семейство, имя): (путь DTCG, режим-ключ)} из токенов: обратное сопоставление без эвристики."""
    out = {}
    for t in toks.list:
        fam = B.family_of(t)
        if fam is None:
            continue
        path = ".".join(t.path)
        if fam == "color":
            out[("color", t.name)] = path
        elif fam == "font" or (fam == "type" and t.type == "fontFamily"):
            out[("type.families", B.font_key(t))] = path
        elif fam == "type":
            out[("type.styles", "-".join(t.path[1:]) if t.path[0] == "type" and len(t.path) > 1 else t.name)] = path
        else:
            out[(fam, t.name)] = path
    return out


def guess_path(family, name):
    """Путь DTCG для имени, которого в токенах нет: первый сегмент — группа семейства, иначе токен верхнего уровня.
    → (путь, семейство в расширении или None)."""
    if family == "type.families":
        return f"font.{name}", None
    if family == "type.styles":
        return f"type.{name}", None
    group = CANON_GROUP.get(family, family)
    if name.startswith(group + "-") and len(name) > len(group) + 1:
        return f"{group}.{name[len(group) + 1:]}", None if B.FAMILY_OF_GROUP.get(group, group) == family else family
    return name, family


# ------------------------------------------------------------------ значения артефакта → DTCG

def parse_color(s, like=None):
    """Строка цвета артефакта → значение DTCG (пространство — как у прежнего значения, по умолчанию srgb) или None."""
    if not isinstance(s, str):
        return None
    s = s.strip()
    alpha = None
    if HEX.match(s):
        hexv = s
    else:
        m = RGB.match(s)
        if not m:
            return None
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        hexv = f"#{r:02x}{g:02x}{b:02x}"
        alpha = float(m.group(4)) if m.group(4) else None
        if alpha is not None and alpha > 1:
            alpha = alpha / 100
    space = like.get("colorSpace") if isinstance(like, dict) else "srgb"
    if space == "oklch":
        from color import hex2oklch
        comps = [round(x, 4) for x in hex2oklch(hexv)]
        v = {"colorSpace": "oklch", "components": comps}
    else:
        h = hexv.lstrip("#")
        v = {"colorSpace": "srgb", "components": [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]}
    if alpha is not None and alpha < 1:
        v["alpha"] = alpha
    v["hex"] = hexv
    return v


def _n(x):
    f = float(x)
    return int(f) if f.is_integer() else f


def parse_value(ty, s, like=None):
    """Строка или число артефакта → значение DTCG типа ty; не переводится — None."""
    if ty == "color":
        return parse_color(s, like)
    txt = str(s).strip() if isinstance(s, (str, int, float)) else None
    if txt is None:
        return None
    if ty == "dimension":
        m = DIMENSION.match(txt)
        return {"value": _n(m.group(1)), "unit": m.group(2)} if m else None
    if ty == "duration":
        m = DURATION.match(txt)
        return {"value": _n(m.group(1)), "unit": m.group(2)} if m else None
    if ty in ("number", "fontWeight"):
        return _n(txt) if NUMBER.match(txt) else (txt if ty == "fontWeight" and txt in B.FONT_WEIGHTS else None)
    if ty == "fontFamily":
        return split_stack(txt)
    if ty == "cubicBezier":
        m = BEZIER.match(txt)
        try:
            vals = [_n(x) for x in m.group(1).split(",")] if m else None
        except ValueError:
            vals = None
        return vals if vals and len(vals) == 4 else None
    if ty == "shadow":
        return parse_shadow(txt)
    return None


def split_stack(s):
    """CSS-стек гарнитур → список имён без кавычек."""
    out, cur, q = [], [], None
    for ch in s:
        if q:
            if ch == q:
                q = None
            else:
                cur.append(ch)
        elif ch in "\"'":
            q = ch
        elif ch == ",":
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur).strip())
    return [x for x in out if x]


def _split_top(s):
    out, depth, cur = [], 0, []
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur).strip())
    return [x for x in out if x]


def parse_shadow(s):
    if s.strip() == "none":
        return []
    layers = []
    for part in _split_top(s):
        inset = part.startswith("inset ")
        part = part[6:] if inset else part
        m = re.match(r"^((?:-?\d+(?:\.\d+)?(?:px|rem)?\s+){2,4})(.+)$", part.strip())
        if not m:
            return None
        lens = [x for x in m.group(1).split() if x]
        color = parse_color(m.group(2).strip())
        dims = [parse_value("dimension", x if re.search(r"(px|rem)$", x) else x + "px") for x in lens]
        if color is None or any(d is None for d in dims):
            return None
        dims += [{"value": 0, "unit": "px"}] * (4 - len(dims))
        layer = {"color": color, "offsetX": dims[0], "offsetY": dims[1], "blur": dims[2], "spread": dims[3]}
        if inset:
            layer["inset"] = True
        layers.append(layer)
    return layers


def infer_type(value):
    """Тип DTCG для значения своего семейства артефакта без токена-образца."""
    txt = str(value).strip()
    if HEX.match(txt) or RGB.match(txt):
        return "color"
    if DIMENSION.match(txt):
        return "dimension"
    if DURATION.match(txt):
        return "duration"
    if NUMBER.match(txt):
        return "number"
    if BEZIER.match(txt):
        return "cubicBezier"
    if parse_shadow(txt):
        return "shadow"
    return None


# ------------------------------------------------------------------ сверка живого со сборкой

@dataclass
class Change:
    """Расхождение живого tokens.json со сборкой."""
    kind: str                                              # value · usage · sample · new · removed · theme · name
    entry: Entry | None
    path: str | None = None                                # путь DTCG
    theme: str | None = None                               # тема цвета или поле стиля
    old: object = None
    new: object = None
    pointer: str | None = None                             # место правки в JSON токенов
    value: object = None                                   # значение DTCG для записи; None — вопрос заказчику
    note: str = ""
    alias: str | None = None                               # путь примитива, если значение было алиасом: вторая дорога


def compare(live_doc, built_doc, toks):
    """[Change]: что изменилось на странице артефакта и куда это поднять в DTCG."""
    live = {e.key: e for e in flatten(live_doc)}
    built = {e.key: e for e in flatten(built_doc)}
    names = name_map(toks)
    out = []
    lt, bt = themes_of(live_doc), themes_of(built_doc)
    if lt and lt != bt:
        out.append(Change("theme", None, old=bt, new=lt, note="набор тем артефакта изменился — вопрос заказчику"))
    if live_doc.get("name") != built_doc.get("name"):
        out.append(Change("name", None, old=built_doc.get("name"), new=live_doc.get("name"),
                          note="имя системы — заголовок прозы DESIGN.md или поле name расширения артефакта"))
    for key, e in live.items():
        b = built.get(key)
        if b is None:
            path, fam = guess_path(e.family, e.name)
            out.append(Change("new", e, path=path, new=e.value,
                              note="новое имя — вопрос заказчику: роль и назначение или отказ"))
            continue
        path = names.get(key)
        t = toks.get(path) if path else None
        if e.family == "color":
            lv = e.value if isinstance(e.value, dict) else {}
            bv = b.value if isinstance(b.value, dict) else {}
            first = B.base_theme(toks.data)
            for theme in sorted(set(lv) | set(bv), key=lambda x: (x != first, x)):
                if lv.get(theme) != bv.get(theme):
                    out.append(_value_change(e, t, path, theme, bv.get(theme), lv.get(theme), toks))
        elif e.family == "type.styles":
            lv, bv = e.value or {}, b.value or {}
            for fld in ("fontSize", "lineHeight", "fontWeight"):
                if lv.get(fld) != bv.get(fld):
                    out.append(_style_change(e, t, path, fld, bv.get(fld), lv.get(fld)))
            if (e.extra.get("sample") or None) != (b.extra.get("sample") or None) and t is not None:
                out.append(Change("sample", e, path=path, old=b.extra.get("sample"), new=e.extra.get("sample"),
                                  pointer=t.pointer + f"/$extensions/{B.EXT_ART}/sample", value=e.extra.get("sample")))
        elif e.value != b.value:
            out.append(_value_change(e, t, path, None, b.value, e.value, toks))
        if e.family != "type.families" and (e.usage or "") != (b.usage or "") and t is not None:
            out.append(Change("usage", e, path=path, old=b.usage, new=e.usage, pointer=t.pointer + "/$description",
                              value=e.usage))
    for key, b in built.items():
        if key not in live:
            out.append(Change("removed", b, path=names.get(key), old=b.value,
                              note="имени нет на странице артефакта — вопрос заказчику: удалить роль или вернуть"))
    return out


def _mode_slot(t, theme, first="light"):
    """Место значения темы в токене: `$value` — у темы значений first, иначе режим."""
    if theme in (None, first):
        return t.pointer + "/$value", t.value
    modes = t.modes()
    return t.pointer + f"/$extensions/{B.EXT_MODES}/{B.esc(theme)}", modes.get(theme)


def _value_change(e, t, path, theme, old, new, toks):
    ch = Change("value", e, path=path, theme=theme, old=old, new=new)
    if t is None:
        ch.note = "путь DTCG не найден — вопрос заказчику"
        return ch
    first = B.base_theme(toks.data)
    ch.pointer, current = _mode_slot(t, theme, first)
    like = toks.resolve(current, theme if theme not in (None, first) else None) if current is not None else None
    if t.type == "typography":
        ch.note = "стиль текста правится по полям"
        return ch
    ch.value = parse_value(t.type, new, like if isinstance(like, dict) else None)
    if ch.value is None:
        ch.note = f"значение «{new}» не переводится в тип {t.type} — вопрос заказчику"
        return ch
    m = B.ALIAS.match(current) if isinstance(current, str) else None
    if m:
        peers = [".".join(x.path) for x in toks.list if x is not t and B.in_artifact(x) and
                 _slot_value(x, theme, first) == current]
        ch.alias = m.group(1)
        ch.note = _roads(current, path, ch.alias, peers)
    return ch


def _roads(current, path, prim, peers=()):
    """Две дороги правки алиаса: литерал в путь роли или значение примитива руками — за ним все ссылки."""
    peers = list(peers)
    who = f": на него же ссылаются {', '.join(peers[:6])}" + (f" и ещё {len(peers) - 6}" if len(peers) > 6 else "") \
        if peers else ""
    return (f"был алиас {current} — две дороги: роль — литерал в {path} (--write, ссылка на примитив рвётся); "
            f"примитив — правка пути {prim} в system.tokens.json руками, меняет все ссылки на него{who}")


def _slot_value(t, theme, first="light"):
    if theme in (None, first):
        return t.value
    return t.modes().get(theme, t.value)


def _style_change(e, t, path, fld, old, new):
    ch = Change("value", e, path=path, theme=fld, old=old, new=new)
    if t is None or not isinstance(t.value, dict):
        ch.note = "путь DTCG не найден или стиль — алиас целиком: вопрос заказчику"
        return ch
    ch.pointer = t.pointer + f"/$value/{fld}"
    sub = B.SUBTYPES["typography"][fld]
    ch.value = parse_value(sub, new)
    cur = t.value.get(fld)
    if ch.value is None:
        ch.note = f"значение «{new}» не переводится в {sub} — вопрос заказчику"
    elif isinstance(cur, str) and B.ALIAS.match(cur):
        ch.alias = B.ALIAS.match(cur).group(1)
        ch.note = _roads(cur, f"{path} ({fld})", ch.alias)
    return ch


# ------------------------------------------------------------------ правка JSON по месту

@dataclass
class Span:
    start: int
    end: int
    kind: str                                              # object · array · scalar
    members: list = field(default_factory=list)            # object: [(ключ, начало ключа, Span)]; array: [Span]


_WS = re.compile(r"[ \t\n\r]*")
_SCALAR = re.compile(r"-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null")


def parse_spans(text, i=0):
    """Разбор JSON с позициями значений (для правки по месту без переформатирования)."""
    i = _WS.match(text, i).end()
    ch = text[i]
    if ch == "{":
        span = Span(i, i, "object")
        i = _WS.match(text, i + 1).end()
        if text[i] == "}":
            span.end = i + 1
            return span
        while True:
            kstart = i
            key, i = scanstring(text, i + 1)
            i = _WS.match(text, i).end()
            assert text[i] == ":", f"ожидалось «:» на позиции {i}"
            val = parse_spans(text, i + 1)
            span.members.append((key, kstart, val))
            i = _WS.match(text, val.end).end()
            if text[i] == ",":
                i = _WS.match(text, i + 1).end()
                continue
            assert text[i] == "}", f"ожидалось «}}» на позиции {i}"
            span.end = i + 1
            return span
    if ch == "[":
        span = Span(i, i, "array")
        i = _WS.match(text, i + 1).end()
        if text[i] == "]":
            span.end = i + 1
            return span
        while True:
            val = parse_spans(text, i)
            span.members.append(val)
            i = _WS.match(text, val.end).end()
            if text[i] == ",":
                i = _WS.match(text, i + 1).end()
                continue
            assert text[i] == "]", f"ожидалось «]» на позиции {i}"
            span.end = i + 1
            return span
    if ch == '"':
        _, end = scanstring(text, i + 1)
        return Span(i, end, "scalar")
    m = _SCALAR.match(text, i)
    if not m:
        raise ValueError(f"не JSON на позиции {i}")
    return Span(i, m.end(), "scalar")


def _unesc(seg):
    return seg.replace("~1", "/").replace("~0", "~")


def _compact(v):
    return json.dumps(v, ensure_ascii=False, separators=(", ", ": "))


def set_pointer(text, ptr, value):
    """Записать значение по JSON Pointer в тексте JSON: замена найденного значения или вставка ключа в ближайший
    существующий объект (недостающие уровни — вложенным значением). Остальной текст не меняется."""
    segs = [_unesc(s) for s in ptr.strip("/").split("/")]
    root = parse_spans(text)
    node, depth = root, 0
    for depth, seg in enumerate(segs):
        nxt = None
        if node.kind == "object":
            nxt = next((v for k, _, v in node.members if k == seg), None)
        elif node.kind == "array" and seg.isdigit() and int(seg) < len(node.members):
            nxt = node.members[int(seg)]
        if nxt is None:
            break
        node = nxt
    else:
        return text[:node.start] + _compact(value) + text[node.end:]
    if node.kind != "object":
        raise ValueError(f"{ptr}: на пути не объект — вставка невозможна")
    rest = segs[depth + 1:]
    nested = value
    for seg in reversed(rest):
        nested = {seg: nested}
    entry = f"{json.dumps(segs[depth], ensure_ascii=False)}: {_compact(nested)}"
    if not node.members:
        return text[:node.start + 1] + entry + text[node.end - 1:]
    _, kstart, last = node.members[-1]
    line_start = text.rfind("\n", 0, kstart) + 1
    indent = text[line_start:kstart]
    sep = ",\n" + indent if indent.strip() == "" and line_start > node.start else ", "
    return text[:last.end] + sep + entry + text[last.end:]


def apply_changes(text, changes):
    """Записать в текст токенов все правки со значением; → (текст, [записанные])."""
    done = []
    for ch in changes:
        if ch.pointer and ch.value is not None and ch.kind in ("value", "usage", "sample"):
            text = set_pointer(text, ch.pointer, ch.value)
            done.append(ch)
    json.loads(text)                                         # правка не ломает JSON
    return text, done


# ------------------------------------------------------------------ восстановление DTCG из живого tokens.json

def restore(live_doc):
    """DTCG из tokens.json артефакта → (документ, [вопросы]) — когда исходников токенов нет."""
    doc = {"$schema": "https://www.designtokens.org/schemas/2025.10/format.json"}
    art_root = {}
    if isinstance(live_doc.get("name"), str):
        art_root["name"] = live_doc["name"]
    notes = {}
    questions = []
    themes = themes_of(live_doc) or ["light"]
    first = "light" if "light" in themes else themes[0]      # тема значений `$value`
    fonts = {}

    def put(path, token, ty=None, family=None):
        parts = path.split(".")
        node = doc
        for p in parts[:-1]:
            node = node.setdefault(p, {})
        if ty and len(parts) > 1 and "$type" not in node and not any(k for k in node if not k.startswith("$")):
            node["$type"] = ty
        if ty and node.get("$type") != ty:
            token = {"$type": ty, **token}
        if family:
            token.setdefault("$extensions", {})[B.EXT_ART] = {"family": family}
        node[parts[-1]] = token

    for fam, body in live_doc.items():
        if not isinstance(body, dict) or fam in ("meta",):
            continue
        if body.get("note"):
            notes[fam] = body["note"]
    for e in flatten(live_doc):
        path, family = guess_path(e.family, e.name)
        if e.family == "color":
            vals = e.value if isinstance(e.value, dict) else {first: e.value}
            base = parse_color(vals.get(first))
            if base is None:
                questions.append(f"{e.label}: цвет «{vals}» не переводится в DTCG")
                continue
            tok = {"$value": base}
            if e.usage:
                tok["$description"] = e.usage
            modes = {th: parse_color(v) for th, v in vals.items() if th != first and v != vals.get(first)}
            if any(v is None for v in modes.values()):
                questions.append(f"{e.label}: значение темы не переводится в DTCG")
                modes = {k: v for k, v in modes.items() if v is not None}
            if modes:
                tok["$extensions"] = {B.EXT_MODES: modes}
            put(path, tok, "color", family)
        elif e.family == "type.families":
            fonts[e.name] = path
            put(path, {"$value": split_stack(e.value)}, "fontFamily")
        elif e.family == "type.styles":
            v = e.value or {}
            fam_path = fonts.get(e.extra.get("family"))
            size = parse_value("dimension", v.get("fontSize"))
            if fam_path is None or size is None:
                questions.append(f"{e.label}: гарнитура группы или кегль не переводятся в DTCG")
                continue
            tok = {"$value": {"fontFamily": "{" + fam_path + "}", "fontSize": size,
                              "fontWeight": v.get("fontWeight", 400), "letterSpacing": {"value": 0, "unit": "px"},
                              "lineHeight": v.get("lineHeight", 1)}}
            if e.usage:
                tok["$description"] = e.usage
            art = {k: e.extra[k] for k in ("group", "sample") if e.extra.get(k)}
            if art:
                tok["$extensions"] = {B.EXT_ART: art}
            put(path, tok, "typography")
        else:
            ty = infer_type(e.value)
            val = parse_value(ty, e.value) if ty else None
            if val is None:
                questions.append(f"{e.label} ({e.family}): значение «{e.value}» не переводится в тип DTCG")
                continue
            tok = {"$value": val}
            if e.usage:
                tok["$description"] = e.usage
            put(path, tok, ty, family)
    if notes:
        art_root["families"] = {k: {"note": v} for k, v in notes.items()}
    if art_root:
        doc["$extensions"] = {B.EXT_ART: art_root}
    if first != "light" and first in B.THEMES:
        doc.setdefault("$extensions", {})[B.EXT_MODES] = {"base": first}
    return doc, questions


def dump_dtcg(obj, ind=0):
    """JSON токенов: группы с отступом 2, поля токена — строкой на поле, значения — компактно."""
    pad = "  " * ind
    items = []
    for k, v in obj.items():
        key = json.dumps(k, ensure_ascii=False)
        if isinstance(v, dict) and "$value" not in v and not k.startswith("$"):
            items.append(f"{pad}  {key}: {dump_dtcg(v, ind + 1)}")
        elif isinstance(v, dict) and "$value" in v:
            inner = ",\n".join(f"{pad}    {json.dumps(k2, ensure_ascii=False)}: {_compact(v2)}" for k2, v2 in v.items())
            items.append(f"{pad}  {key}: {{\n{inner}\n{pad}  }}")
        else:
            items.append(f"{pad}  {key}: {_compact(v)}")
    return "{\n" + ",\n".join(items) + f"\n{pad}}}"


# ------------------------------------------------------------------ вызов

def load_json(path, what):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as e:
        raise F.ToolError(f"{what} не читается: {e}") from e
    except ValueError as e:
        raise F.ToolError(f"{what} — не JSON: {e}") from e


def built_doc(prj, data):
    toks = B.Tokens(data)
    return B.artifact_tokens(toks, B.ds_name(toks, prj), example=data.get("example") is True), toks


def _describe(ch):
    e = ch.entry
    where = f"{e.label} ({e.family})" if e else ch.kind
    if ch.kind == "value":
        th = f" [{ch.theme}]" if ch.theme else ""
        return f"{where}{th}: сборка «{ch.old}» → на странице «{ch.new}»"
    if ch.kind in ("usage", "sample"):
        return f"{where}: {ch.kind} «{ch.old}» → «{ch.new}»"
    if ch.kind == "new":
        return f"{where}: нового имени нет в токенах (предложенный путь {ch.path})"
    if ch.kind == "removed":
        return f"{where}: имя сборки удалено на странице (путь {ch.path})"
    return f"{ch.kind}: сборка «{ch.old}» → на странице «{ch.new}»"


def after_lift(slug):
    """Общий хвост обеих дорог — протокол «Правки токенов»: контраст пар, производные, публикация."""
    return (f"пересчёт контраста пар токенов проекта (lib/color.py contrast), ds_build build {slug}, публикация "
            "ДС")


def to_findings(prj, changes):
    rep = F.Report()
    write = f"ds_sync build {prj.slug} --live FILE --write"
    for ch in changes:
        e = ch.entry
        ref = "artifact#" + (f"{e.family}/{e.name}" if e else ch.kind)
        if ch.value is None:
            fix = ch.note or "вопрос заказчику"
        elif ch.alias:
            fix = (f"роль: {write} (литерал в {ch.path}); примитив: правка пути {ch.alias} в system.tokens.json "
                   f"руками (меняет все ссылки на него); затем {after_lift(prj.slug)}")
        else:
            fix = f"поднять в {ch.path}: {write}; затем {after_lift(prj.slug)}"
        rep.add("R-FRESH-001", "error", surface=None, kind=KIND, ref=ref, path=prj.rel(prj.tokens_path),
                message="правка заказчика на странице артефакта не поднята в токены: " + _describe(ch)
                        + (f" — {ch.note}" if ch.note and ch.value is not None else ""), fix=fix)
    return rep.items


def run_check(prj, live_path):
    live = load_json(live_path, "живой tokens.json")
    if not prj.tokens_path.is_file():
        return [F.Finding("R-FRESH-001", "error", None, KIND, "tokens", prj.rel(prj.tokens_path),
                          "нет токенов DTCG: живой артефакт не с чем сверить",
                          f"восстановить токены: ds_sync build {prj.slug} --live FILE --write")]
    data = load_json(prj.tokens_path, "system.tokens.json")
    errors = [i for i in B.validate(data) if i.severity == "error"]
    if errors:
        raise F.ToolError(f"токены с ошибками формата: ds_build check {prj.slug}")
    built, toks = built_doc(prj, data)
    return to_findings(prj, compare(live, built, toks))


def run_build(prj, live_path, write=False, out=None, as_json=False, stream=None):
    stream = stream or sys.stdout
    live = load_json(live_path, "живой tokens.json")
    target = prj.tokens_path if out is None else Path(out) / prj.rel(prj.tokens_path)
    if not prj.tokens_path.is_file():
        doc, questions = restore(live)
        text = dump_dtcg(doc) + "\n"
        errs = [i for i in B.validate(doc) if i.severity == "error"]
        if errs:
            raise F.ToolError(f"восстановленные токены не проходят формат: {errs[0].pointer} — {errs[0].message}")
        wrote = None
        if write or out is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8")
            wrote = target
        mapping = [{"name": e.label, "family": e.family, "path": guess_path(e.family, e.name)[0]}
                   for e in flatten(live)]
        if as_json:
            print(json.dumps({"mode": "restore", "mapping": mapping, "questions": questions,
                              "written": str(wrote) if wrote else None}, ensure_ascii=False, indent=1), file=stream)
        else:
            print(f"токенов DTCG нет — восстановление из живого tokens.json (имён — {len(mapping)}):", file=stream)
            for m in mapping:
                print(f"  {m['name']:<28} {m['family']:<14} → {m['path']}", file=stream)
            for q in questions:
                print(f"вопрос: {q}", file=stream)
            print(f"записано: {wrote}" if wrote else "без записи: --write — в проект, --out DIR — в копию", file=stream)
        return F.EXIT_OK
    text = prj.tokens_path.read_text(encoding="utf-8")
    data = json.loads(text)
    errors = [i for i in B.validate(data) if i.severity == "error"]
    if errors:
        raise F.ToolError(f"токены с ошибками формата: ds_build check {prj.slug}")
    built, toks = built_doc(prj, data)
    changes = compare(live, built, toks)
    new_text, done = apply_changes(text, changes)
    questions = [c for c in changes if c not in done]
    wrote = None
    if done and (write or out is not None):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(new_text, encoding="utf-8")
        wrote = target
    if as_json:
        print(json.dumps({"mode": "sync", "edits": [{"path": c.path, "pointer": c.pointer, "theme": c.theme,
                                                     "old": c.old, "new": c.new, "value": c.value, "note": c.note}
                                                    for c in done],
                          "questions": [{"kind": c.kind, "name": c.entry.label if c.entry else None,
                                         "family": c.entry.family if c.entry else None, "path": c.path,
                                         "old": c.old, "new": c.new, "note": c.note} for c in questions],
                          "written": str(wrote) if wrote else None}, ensure_ascii=False, indent=1), file=stream)
    else:
        if not changes:
            print("расхождений нет: живой tokens.json равен сборке из токенов", file=stream)
        for c in done:
            print(f"правка  {c.pointer} = {_compact(c.value)}", file=stream)
            print(f"        {_describe(c)}" + (f"; {c.note}" if c.note else ""), file=stream)
        for c in questions:
            print(f"вопрос  {_describe(c)}" + (f" — {c.note}" if c.note else ""), file=stream)
        if done:
            print(f"записано: {wrote}; дальше — {after_lift(prj.slug)}" if wrote else
                  "без записи: --write — по месту, --out DIR — в копию", file=stream)
    return F.EXIT_OK


def run_show(prj, live_path=None, as_json=False, stream=None):
    stream = stream or sys.stdout
    rows = []
    if prj.tokens_path.is_file():
        data = load_json(prj.tokens_path, "system.tokens.json")
        built, toks = built_doc(prj, data)
        names = name_map(toks)
        for e in flatten(built):
            rows.append({"name": e.label, "family": e.family, "path": names.get(e.key), "source": "tokens"})
        known = {(r["family"], r["name"]) for r in rows}
    else:
        known = set()
    if live_path:
        for e in flatten(load_json(live_path, "живой tokens.json")):
            if (e.family, e.label) not in known:
                rows.append({"name": e.label, "family": e.family, "path": guess_path(e.family, e.name)[0],
                             "source": "live (предложение)"})
    if as_json:
        print(json.dumps({"project": prj.slug, "map": rows}, ensure_ascii=False, indent=1), file=stream)
    else:
        for r in rows:
            print(f"{r['name']:<30} {r['family']:<14} {r['path'] or '—':<34} {r['source']}", file=stream)
    return F.EXIT_OK


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    B._reexec_venv(__file__)
    if "--selftest" in argv:
        try:
            return _selftest()
        except F.ToolError as e:
            print(f"ds_sync: {e}", file=sys.stderr)
            return F.EXIT_USAGE
    ap = docpaths.parser("ds_sync", __doc__, commands=("build", "check", "show"), surface="none")
    ap.add_argument("--live", metavar="FILE", help="живой tokens.json артефакта, прочитанный с claude.ai и сохранённый")
    ap.add_argument("--write", action="store_true", help="build: записать правки в system.tokens.json проекта")
    call = docpaths.parse(ap, argv)
    a = call.args
    if call.command in ("build", "check") and not a.live:
        ap.error(f"{call.command}: нужен --live FILE — tokens.json артефакта, прочитанный с claude.ai")
    prj = B.Project.of(call.slug, call.repo)
    try:
        if call.command == "check":
            items = run_check(prj, a.live)
            F.print_findings(items, as_json=call.json)
            return F.exit_code(items)
        if call.command == "show":
            return run_show(prj, a.live, call.json)
        return run_build(prj, a.live, write=a.write, out=call.out, as_json=call.json)
    except (F.ToolError, docpaths.DocPathError, OSError, ValueError) as e:
        print(f"ds_sync: {e}", file=sys.stderr)
        return F.EXIT_USAGE


# ------------------------------------------------------------------ самопроверка

KNOWN_ROUNDTRIP = {("meta", "source"), ("type.families", "display")}   # расхождения круга на примере cd


def roundtrip(live_doc):
    """Круг «tokens.json → DTCG → tokens.json»: → (восстановленный DTCG, собранный tokens.json, [расхождения])."""
    doc, questions = restore(live_doc)
    toks = B.Tokens(doc)
    art = B.artifact_tokens(toks, (doc.get("$extensions") or {}).get(B.EXT_ART, {}).get("name") or "—")
    diffs = []
    if live_doc.get("meta") != art.get("meta"):
        diffs.append(("meta", "source"))
    live_e, art_e = {e.key: e for e in flatten(live_doc)}, {e.key: e for e in flatten(art)}
    for key in sorted(set(live_e) | set(art_e)):
        a, b = live_e.get(key), art_e.get(key)
        if a is None or b is None or a.value != b.value or a.usage != b.usage or a.extra != b.extra:
            diffs.append(key)
    if [k for k in live_doc if k not in ("meta", "example")] != [k for k in art if k not in ("meta", "example")]:
        diffs.append(("order", "families"))
    for fam in live_doc:
        if isinstance(live_doc[fam], dict) and live_doc[fam].get("note") != (art.get(fam) or {}).get("note") \
                and fam not in ("meta",):
            diffs.append(("note", fam))
    return doc, art, diffs, questions


def _selftest():
    import copy
    import subprocess
    import tempfile
    ok = True

    def check_(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    B._jsonschema()
    # 1. разбор значений
    check_("цвет #hex → srgb, rgb(… / a) → альфа", parse_color("#2146D8")["hex"] == "#2146D8" and
           parse_color("rgb(2 6 24 / 0.32)")["alpha"] == 0.32)
    check_("размер, длительность, число, кривая, стек гарнитур", parse_value("dimension", "1.5rem") ==
           {"value": 1.5, "unit": "rem"} and parse_value("duration", "150ms") == {"value": 150, "unit": "ms"}
           and parse_value("number", "1.08") == 1.08 and parse_value("cubicBezier", "cubic-bezier(.2, .7, .2, 1)") ==
           [0.2, 0.7, 0.2, 1]
           and split_stack('"Golos Text", Arial, sans-serif') == ["Golos Text", "Arial", "sans-serif"])
    check_("тень: слои и цвет", parse_shadow("0px 1px 2px 0px rgb(2 6 23 / 0.08), 0 4px 8px -2px #020617")[1]["spread"]
           == {"value": -2, "unit": "px"})
    check_("путь по имени: префикс группы семейства или токен верхнего уровня",
           guess_path("color", "color-accent-hover") == ("color.accent-hover", None) and
           guess_path("spacing", "space-4") == ("space.4", None)
           and guess_path("spacing", "gutter") == ("gutter", "spacing")
           and guess_path("size", "control-h") == ("control-h", "size")
           and guess_path("type.styles", "h2") == ("type.h2", None))
    text = '{\n  "a": {\n    "$value": 1\n  },\n  "b": {"c": 2}\n}\n'
    t2 = set_pointer(text, "/a/$value", 5)
    t3 = set_pointer(t2, "/a/$description", "описание")
    t4 = set_pointer(t3, "/b/$extensions/x/y", [1, 2])
    check_("правка JSON по месту: замена, вставка ключа и вложенного значения, остальное не тронуто",
           json.loads(t4) == {"a": {"$value": 5, "$description": "описание"},
                              "b": {"c": 2, "$extensions": {"x": {"y": [1, 2]}}}}
           and t4.startswith('{\n  "a": {\n    "$value": 5,\n    "$description": "описание"\n  },'))
    # 2. круг на примере cd
    ex_path = kbpaths.kb("claude-design", "05-design-artifacts", "example", "design-system", "project", "tokens.json")
    ex = json.loads(ex_path.read_text(encoding="utf-8"))
    doc, art, diffs, questions = roundtrip(ex)
    errs = [i for i in B.validate(doc) if i.severity == "error"]
    check_("пример cd: восстановленные токены проходят формат DTCG" + (f" ({errs[0].message})" if errs else ""),
           not errs and not questions)
    check_("пример cd: пути DTCG восстановлены (color-bg → color.bg, space-4 → space.4, gutter, control-h, "
           "fs-display, font.display, type.h2)",
           B.Tokens(doc).get("color.bg") and B.Tokens(doc).get("space.4") and "gutter" in doc and "control-h" in doc
           and "fs-display" in doc and B.Tokens(doc).get("font.display") and B.Tokens(doc).get("type.h2"))
    check_(f"пример cd: круг «tokens.json → DTCG → tokens.json» — имена и значения те же, кроме известных "
           f"{sorted(KNOWN_ROUNDTRIP)} (есть: {diffs})", set(diffs) == KNOWN_ROUNDTRIP)
    same_bytes = B.dump_artifact(art).splitlines()
    ex_lines = ex_path.read_text(encoding="utf-8").splitlines()
    differ = [i for i, (x, y) in enumerate(zip(ex_lines, same_bytes)) if x != y]
    check_(f"пример cd: tokens.json круга расходится с примером в {len(differ)} строках (источник и кавычки Unbounded)",
           len(ex_lines) == len(same_bytes) and len(differ) == 2)
    # 3. фикстура cabinet-ds: живой = собранный; правка на странице → находки и подъём в DTCG
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("cabinet-ds") as fx:
        prj = B.Project.of(fx.slug, fx.root)
        with tempfile.TemporaryDirectory(prefix="ddd-sync-") as td:
            live_p = Path(td) / "tokens.json"
            live = json.loads(prj.art_tokens.read_text(encoding="utf-8"))
            live_p.write_text(json.dumps(live, ensure_ascii=False), encoding="utf-8")
            check_("живой tokens.json = сборка → check без находок", run_check(prj, live_p) == [])
            edited = copy.deepcopy(live)
            for t in edited["color"]["tokens"]:
                if t["name"] == "color-accent-solid":
                    t["value"]["light"] = "#1E40AF"
                if t["name"] == "color-bg-canvas":
                    t["value"]["dark"] = "#111827"
            for f_ in edited["type"]["groups"]:
                for s in f_["styles"]:
                    if s["name"] == "body":
                        s["fontSize"] = "15px"
            edited["radius"]["tokens"][0]["usage"] = "Кнопки и поля (правка заказчика)."
            edited["spacing"]["tokens"].append({"name": "space-3xl", "value": "48px", "usage": "новое"})
            edited["size"]["tokens"] = [t for t in edited["size"]["tokens"] if t["name"] != "size-control-lg"]
            live_p.write_text(json.dumps(edited, ensure_ascii=False), encoding="utf-8")
            items = run_check(prj, live_p)
            msgs = " | ".join(f.message for f in items)
            check_("правки на странице → R-FRESH-001: значение светлой и тёмной темы, кегль стиля, usage, новое и "
                   f"удалённое имя ({len(items)})",
                   len(items) == 6 and all(f.rule == "R-FRESH-001" and f.severity == "error" for f in items)
                   and "--color-accent-solid" in msgs and "[dark]" in msgs and ".body" in msgs and "space-3xl" in msgs
                   and "size-control-lg" in msgs)
            acc = next((f for f in items if "--color-accent-solid" in f.message and "[light]" in f.message), None)
            check_("алиас роли: сообщение — правка заказчика, не поднятая в токены, с обеими дорогами; совет — роль "
                   "(--write), примитив (руками) и хвост: контраст пар, ds_build build, публикация ДС",
                   acc is not None and acc.message.startswith("правка заказчика на странице артефакта не поднята в "
                                                              "токены: ") and "две дороги" in acc.message
                   and "роль: ds_sync build" in acc.fix and "примитив: правка пути primitive." in acc.fix
                   and all(x in acc.fix for x in ("контраста пар", "ds_build build", "публикация ДС")))
            before = prj.tokens_path.read_text(encoding="utf-8")
            buf = __import__("io").StringIO()
            run_build(prj, live_p, stream=buf)
            check_("build без --write — только предложение с обеими дорогами у алиаса, токены не тронуты",
                   prj.tokens_path.read_text(encoding="utf-8") == before and "правка" in buf.getvalue()
                   and "вопрос" in buf.getvalue() and "две дороги" in buf.getvalue())
            buf = __import__("io").StringIO()
            run_build(prj, live_p, write=True, stream=buf)
            check_("build --write: дальше — контраст пар, ds_build build, публикация ДС",
                   "дальше — пересчёт контраста пар" in buf.getvalue() and "публикация ДС" in buf.getvalue())
            after = prj.tokens_path.read_text(encoding="utf-8")
            changed = [ln for ln in after.splitlines() if ln not in before.splitlines()]
            check_(f"build --write: правится только поднятое ({len(changed)} строк), алиас роли → литерал",
                   len(changed) <= 5 and '"hex": "#1E40AF"' in after
                   and '"fontSize": {"value": 15, "unit": "px"}' in after)
            data = json.loads(after)
            check_("после подъёма токены проходят формат", not [i for i in B.validate(data) if i.severity == "error"])
            B.build(prj)
            left = run_check(prj, live_p)
            check_("после подъёма и ds_build build остаются только вопросы (новое и удалённое имя)",
                   len(left) == 2 and all(("space-3xl" in f.message or "size-control-lg" in f.message) for f in left))
            with tempfile.TemporaryDirectory(prefix="ddd-sync-cwd-") as cwd:
                r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "check", fx.slug, "--repo",
                                    str(fx.root), "--live", str(live_p), "--json"], cwd=cwd, capture_output=True,
                                   text=True)
            check_("check --json из чужой рабочей папки — код 1 при расхождении, строки находок",
                   r.returncode == 1 and len(F.parse_lines(r.stdout)) == 2)
        # 4. восстановление, когда токенов нет
        prj.tokens_path.unlink()
        with tempfile.TemporaryDirectory(prefix="ddd-sync-rs-") as td:
            live_p = Path(td) / "tokens.json"
            live_p.write_text(ex_path.read_text(encoding="utf-8"), encoding="utf-8")
            run_build(prj, live_p, write=True, stream=__import__("io").StringIO())
            restored = json.loads(prj.tokens_path.read_text(encoding="utf-8"))
            check_("нет токенов: build --write восстанавливает их из живого tokens.json",
                   isinstance(restored.get("color", {}).get("bg"), dict) and
                   not [i for i in B.validate(restored) if i.severity == "error"])
            B.build(prj)
            left = run_check(prj, live_p)
            check_(f"после восстановления и ds_build build живой tokens.json отличается только кавычками Unbounded "
                   f"({len(left)})", len(left) == 1 and "--font-display" in left[0].message)
    print("ds_sync selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
