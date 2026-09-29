#!/usr/bin/env python3
"""states — обязательные наборы состояний экрана и блока по правилам канона и проверка ключей `states`.

Словарь состояний, приоритет и матрица «экран или компонент × состояние» — производный YAML базы
`kb/ux/06-feedback-states-motion/screen-states.yaml` (генератор `scripts/ux/states_export.py`); строки матрицы по
типу экрана — таблица типов канона `docs/projects/_template/screens/README.md` («Экран: тип, карта и маршрут»); ключи
состояний мобильного слоя — таблица `docs/projects/_template/mobile/README.md` («Состояния экрана и словарь»). Код их
не копирует — читает.

Набор экрана — объединение условий канона (README экранов, «Обязательный набор»; правило R-SEM-011):
  loading-initial, error-load   экран грузит данные: `data:` в дереве, `data` блока, параметры маршрута
  empty-first-run, partial-few  на экране коллекция: контракт collection, ui:Table · List · TreeView, ui:Card items=
  empty-filtered                поиск или фильтр: ui:SearchInput, collection.filters, `filters` в url-state
  строки матрицы                строка типа экрана (с условием «при поиске», «при вложениях» таблицы типов) и строка
                                «Экран или маршрут целиком»; обязательные состояния строки (колонка «обязательные»)
  строки компонентов            типы с ключом screen_states словаря компонентов в блоках экрана
  no-permission                 access: roles (у строк матрицы — только при этом условии: «база для систем с ролями»)
  not-found                     параметр маршрута с типом-объектом глоссария (params)
  отказы ситуаций               refusals ситуаций экрана (interface/<surface>/situation.md)
  in-progress-background        main-task или возможность ситуации экрана с duration: background в паспорте
Блоки со своим источником (`source: own`) в условия экрана не входят: у такого блока свой набор — loading-initial,
error-load, у коллекции ещё empty-first-run, empty-filtered, partial-few. Работа без сети (`offline`) и живые данные
(`stale`) — решения поверхности в разделе «Решения» `map.md`, их утилита показывает для чтения («по решению
поверхности»), а не требует. Приоритет — одно правило канона (S18 > S16 > S23 > S13 > S07 > S02 > S01; S06 и S21
поверх): его утилита показывает, у экрана не требует.

    states check <slug> [<surface>] [--repo DIR] [--json]     находки
    states show  <slug> [<surface>] [--repo DIR] [--json]     набор каждого экрана и блока: ключ — почему — покрыт ли
    states --selftest                                          словарь, расчёт наборов и фикстуры кабинета, без сети

Из Python: `screen_set(Layer, slug)`, `block_set(Layer, slug)` → [Item(key, id, reasons, covered, na)],
`Dictionary()` — словарь и матрица, `input_synonyms()` — ключи мобильного слоя → ключи словаря.

Правила (`.claude/skills/screen-audit/references/rules.md`):
  R-STRUCT-022  ключ states экрана или блока вне словаря (подсказка — ключ словаря по таблице мобильного слоя;
                состояние приложения — раздел основного каркаса)                          error
  R-SEM-011     обязательное состояние набора не покрыто: нет дельты или «не применимо» без причины
                                                                                          warning, error у stable
  R-SEM-015     механическая часть: главная кнопка шапки повторена главной кнопкой в пустом состоянии; при двух
                и больше пустых состояниях на экране — не только текст и третичные кнопки  warning
Код выхода: 0 — нет error, 1 — есть error, 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import json
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
import layer as L  # noqa: E402
import tree as T  # noqa: E402

DICT_PATH = kbpaths.kb("ux", "06-feedback-states-motion", "screen-states.yaml")
# условия строк таблицы типов README экранов → признак экрана
ROW_CONDITIONS = {"при поиске": "search", "при вложениях": "file"}
COLLECTION_TYPES = ("Table", "List", "TreeView")
PRIMITIVE_TYPES = ("text", "number", "money", "date", "datetime", "enum", "bool", "file", "string", "int", "uuid", "id")


class Dictionary:
    """Словарь состояний экрана и матрица из производного YAML базы."""

    def __init__(self, path=DICT_PATH):
        self.path = Path(path)
        if not self.path.is_file():
            raise F.ToolError(f"нет словаря состояний {self.path} — соберите: scripts/ux/states_export.py")
        data = L._yaml().safe_load(self.path.read_text(encoding="utf-8")) or {}
        self.states = data.get("states") or {}
        self.key2id = {v["key"]: sid for sid, v in self.states.items() if isinstance(v, dict) and v.get("key")}
        self.priority = [self.states[s]["key"] for s in data.get("priority") or [] if s in self.states]
        self.overlays = [self.states[s]["key"] for s in data.get("overlays") or [] if s in self.states]
        self.matrix = data.get("matrix") or {}
        self.by_title = {str(v.get("title")): k for k, v in self.matrix.items() if isinstance(v, dict)}
        if not self.key2id or not self.matrix:
            raise F.ToolError(f"{self.path}: нет разделов states или matrix")

    def key(self, sid):
        return self.states[sid]["key"]

    def scoped(self, sid):
        """Обязательность «база» с сужением круга экранов (scope) — у строки матрицы условие канона."""
        s = self.states.get(sid) or {}
        return s.get("obligation") == "base" and bool(str(s.get("scope") or "").strip())


_DICT = None


def dictionary():
    global _DICT
    if _DICT is None:
        _DICT = Dictionary()
    return _DICT


def type_rows(readme=None):
    """Таблица типов README экранов → {type: [(название строки матрицы, условие | None)]}; условие — ключ
    ROW_CONDITIONS или «?текст» (условие, которое утилита не решает)."""
    path = Path(readme) if readme else docpaths.template("screens", "README.md")
    md = L.Md(path)
    t = md.table(("type", "каркас"))
    out = {}
    if t is None:
        raise F.ToolError(f"{path}: нет таблицы типов экрана (колонки type, каркас)")
    col = next((c for c in t.columns if c.startswith("строки матрицы")), None)
    for r in t.rows:
        typ = L.cell(r.get("type"))
        if not typ:
            continue
        rows = []
        for part in (r.get(col) or "").split(";"):
            titles = re.findall(r"«([^»]+)»", part)
            if not titles or re.match(r"^\s*строки нет", part):
                continue                                # «строки нет: позиция …» — у типа строки матрицы нет
            rest = part.rsplit("»", 1)[-1]
            cond = None
            m = re.search(r"\bпри\s+[^,;—]+", rest)
            if m:
                phrase = m.group(0).strip()
                cond = ROW_CONDITIONS.get(phrase, "?" + phrase)
            rows += [(title, cond) for title in titles]
        out[typ] = rows
    return out


_TYPE_ROWS = None


def type_rows_cached():
    global _TYPE_ROWS
    if _TYPE_ROWS is None:
        _TYPE_ROWS = type_rows()
    return _TYPE_ROWS


def input_synonyms(readme=None):
    """Ключи states мобильного слоя (они же ключи экрана вне словаря) → ключи словаря по таблице канона mobile:
    {ключ: {"kind": "state" | "ideal" | "app", "to": [ключи словаря по порядку]}}."""
    path = Path(readme) if readme else docpaths.template("mobile", "README.md")
    out = {}
    if not path.is_file():
        return out
    md = L.Md(path)
    line, body = md.section("Состояния экрана и словарь")
    t = L.find_table(body or "", ("состояния словаря",))
    if t is None:
        return out
    key_col = next((c for c in t.columns if c.startswith("ключ")), None)
    for r in t.rows:
        keys = re.findall(r"`([a-z-]+)`", r.get(key_col) or "")
        target = r.get("состояния словаря") or ""
        to = re.findall(r"S\d\d\s+`([a-z-]+)`", target)
        kind = "state" if to else ("ideal" if "идеальн" in target else "app")
        for k in keys:
            out[k] = {"kind": kind, "to": to}
    return out


_SYN = None


def synonyms_cached():
    global _SYN
    if _SYN is None:
        _SYN = input_synonyms()
    return _SYN


# ------------------------------------------------------------------ набор

@dataclass
class Item:
    key: str
    id: str | None
    reasons: list = field(default_factory=list)
    covered: str | None = None                          # delta · na; None — не покрыто
    na: str | None = None

    def as_dict(self):
        d = {"key": self.key, "id": self.id, "reasons": list(self.reasons), "covered": self.covered}
        if self.na is not None:
            d["na"] = self.na
        return d


@dataclass
class SetResult:
    slug: str
    kind: str
    status: str | None
    items: list = field(default_factory=list)           # обязательные по порядку словаря
    optional: list = field(default_factory=list)        # ключи states сверх набора (из словаря)
    unknown: list = field(default_factory=list)         # ключи вне словаря
    manual: list = field(default_factory=list)          # условия по решению поверхности — для чтения
    notes: list = field(default_factory=list)           # условия строк, которые утилита не решает

    def as_dict(self):
        return {"slug": self.slug, "kind": self.kind, "status": self.status,
                "required": [i.as_dict() for i in self.items], "optional": self.optional, "unknown": self.unknown,
                "manual": self.manual, "notes": self.notes}


class _Acc:
    """Накопитель набора: ключ → причины, в порядке словаря."""

    def __init__(self, d):
        self.d = d
        self.reasons = {}

    def add(self, key_or_id, reason):
        key = self.d.key(key_or_id) if key_or_id in self.d.states else key_or_id
        if key not in self.d.key2id:
            return
        lst = self.reasons.setdefault(key, [])
        if reason not in lst:
            lst.append(reason)

    def items(self):
        order = {k: i for i, k in enumerate(self.d.key(s) for s in self.d.states)}
        return [Item(k, self.d.key2id.get(k), r) for k, r in sorted(self.reasons.items(), key=lambda x: order[x[0]])]


def _fm_list(v):
    if isinstance(v, list):
        return [str(x) for x in v if not L.is_empty(x)]
    if isinstance(v, str) and not L.is_empty(v):
        return [x.strip() for x in v.strip("[]").split(",") if x.strip() and not L.is_empty(x.strip())]
    return []


def _nodes(roots):
    out = []
    for _, nodes in roots:
        out += [n for n, _ in T.walk(nodes)]
    return out


def _has_data(n):
    if n.prefix == "data" and n.valid:
        return True
    if any(isinstance(v, str) and v.startswith("data:") for v in n.attrs.values()):
        return True
    items = n.struct.get("items")
    return isinstance(items, str) and items.startswith("data:")


def _object_param(lay, params):
    """(имя, тип) параметра маршрута с объектным типом или None."""
    if not isinstance(params, dict):
        return None
    objects = lay.product.objects
    for name, typ in params.items():
        t = str(typ or "").strip()
        base = t[4:] if t.startswith("ref:") else t
        if lay.product.has_objects:
            if base in objects:
                return name, base
        elif base and base not in PRIMITIVE_TYPES:
            return name, base
    return None


def _decisions(lay):
    """Строки раздела «Решения» map.md (текст ячеек) — для условий по решению поверхности."""
    if lay.map is None:
        return []
    line, body = lay.map.section("Решения")
    out = []
    for t in L.tables(body or ""):
        for r in t.rows:
            out.append(" · ".join(v for v in r.cells.values() if v))
    return out


def screen_set(lay, slug, trees=None):
    """Обязательный набор состояний экрана с причинами и покрытием."""
    d = dictionary()
    trees = trees or T.parse_layer(lay)
    p = trees.screens[slug]
    rec = p.record
    fm = rec.fm
    acc = _Acc(d)
    res = SetResult(slug=slug, kind="screen", status=rec.status)
    comp = T.composition(trees, slug, with_states=False, with_own=False)
    roots = list(comp["fills"])
    for b in comp["blocks"]:
        roots += comp["block_trees"].get(b, [])
    nodes = _nodes(roots)
    blocks = {b: lay.blocks[b] for b in comp["blocks"] if b in lay.blocks}
    typ = str(fm.get("type") or "").strip()
    access = str(fm.get("access") or "").strip()
    url_state = _fm_list(fm.get("url-state"))

    def matrix_row(row_key, why):
        row = d.matrix.get(row_key)
        if not isinstance(row, dict):
            return
        for sid in row.get("required") or []:
            if sid not in d.states:
                continue
            if d.key(sid) == "no-permission" and access != "roles":
                continue                                # «база для систем с ролями» — канон: access: roles
            note = (row.get("notes") or {}).get(sid)
            acc.add(sid, why + (f" ({note})" if note else ""))

    # данные
    data_where = [n.head for n in nodes if _has_data(n)][:1]
    data_where += [f"data блока {b}" for b, r in blocks.items() if isinstance(r.fm.get("data"), dict)][:1]
    if isinstance(fm.get("params"), dict):
        data_where.append("параметры маршрута")
    if data_where:
        for k in ("loading-initial", "error-load"):
            acc.add(k, f"экран грузит данные ({data_where[0]})")
    # коллекция, поиск и фильтр
    coll = [f"ui:{n.ui_type} ({n.head})" for n in nodes if n.ui_type in COLLECTION_TYPES]
    coll += [f"ui:Card items= ({n.head})" for n in nodes if n.ui_type == "Card" and "items" in n.attrs]
    coll += [f"collection блока {b}" for b, r in blocks.items() if isinstance(r.fm.get("collection"), dict)]
    if coll:
        for k in ("empty-first-run", "partial-few"):
            acc.add(k, f"на экране коллекция: {coll[0]}")
    search = [n.head for n in nodes if n.ui_type == "SearchInput"]
    filt = [f"collection.filters блока {b}" for b, r in blocks.items()
            if isinstance(r.fm.get("collection"), dict) and _fm_list(r.fm["collection"].get("filters"))]
    if "filters" in url_state:
        filt.append("filters в url-state")
    if search or filt:
        acc.add("empty-filtered", "поиск или фильтр: " + ("ui:SearchInput" if search else filt[0]))
    has_file = any(n.ui_type == "FileUpload" for n in nodes)
    # строки матрицы по типу экрана и строка «Экран или маршрут целиком»
    rows = type_rows_cached().get(typ)
    if rows == []:
        res.notes.append(f"у типа `{typ}` строки матрицы нет (таблица типов канона) — набор по условиям и строке "
                         "маршрута")
    if rows is not None:
        for title, cond in rows:
            key = d.by_title.get(title)
            if key is None:
                res.notes.append(f"строки матрицы «{title}» нет в {d.path.name}")
                continue
            if cond and cond.startswith("?"):
                res.notes.append(f"строка «{title}» — {cond[1:]}: условие чтением")
                continue
            if cond == "search" and not search:
                continue
            if cond == "file" and not has_file:
                continue
            if key != "route":
                matrix_row(key, f"строка типа экрана «{title}»")
    elif typ:
        res.notes.append(f"тип `{typ}` вне таблицы типов канона")
    matrix_row("route", f"строка «{d.matrix.get('route', {}).get('title', 'route')}» — у каждого экрана")
    # строки компонентов со screen_states
    comps = lay.components
    for n in nodes:
        row_key = comps.screen_states(n.ui_type) if n.ui_type else None
        if row_key:
            title = d.matrix.get(row_key, {}).get("title", row_key)
            matrix_row(row_key, f"компонент ui:{n.ui_type} — строка «{title}»")
    # доступ и параметр объекта
    if access == "roles":
        acc.add("no-permission", "доступ к маршруту ограничен ролями (access: roles)")
    op = _object_param(lay, fm.get("params"))
    if op:
        acc.add("not-found", f"у маршрута параметр объекта ({op[0]}: {op[1]})")
    # отказы ситуаций
    sits = lay.interface.table("situation")
    for s in _fm_list(fm.get("situations")):
        row = sits.get(s)
        for key in row.refs("refusals") if row else []:
            if key in d.key2id:
                acc.add(key, f"отказ ситуации {s}")
            else:
                res.notes.append(f"отказ `{key}` ситуации {s} вне словаря")
    # длительность возможностей
    caps = []
    mt = fm.get("main-task")
    if isinstance(mt, str) and not L.is_empty(mt):
        caps.append(mt.strip())
    for s in _fm_list(fm.get("situations")):
        row = sits.get(s)
        caps += row.refs("capabilities") if row else []
    for c in dict.fromkeys(caps):
        pas = lay.product.passports.get(c) or {}
        if str(pas.get("duration") or "").strip() == "background":
            acc.add("in-progress-background", f"возможность {c} с duration: background")
    # решения поверхности — для чтения
    dec = _decisions(lay)
    off = [x for x in dec if re.search(r"без сети|офлайн|offline", x, re.I)]
    if off:
        res.manual.append({"key": "offline", "why": "работа без сети — решение поверхности («Решения» map.md): "
                                                   + off[0][:160]})
    live = [x for x in dec if re.search(r"живы[ех] данн|stale|свежест", x, re.I)]
    if live or typ == "dashboard":
        res.manual.append({"key": "stale", "why": "живые данные — решение поверхности" +
                                                  (f": {live[0][:160]}" if live else " (дашборд)")})
    res.items = acc.items()
    _cover(res, p.states, d)
    return res


def block_set(lay, slug, trees=None):
    """Набор блока со своим источником (`source: own`); у остальных блоков — пустой набор."""
    d = dictionary()
    trees = trees or T.parse_layer(lay)
    p = trees.blocks[slug]
    rec = p.record
    res = SetResult(slug=slug, kind="block", status=rec.status)
    if not T.is_own(trees, slug):
        _cover(res, p.states, d)
        return res
    acc = _Acc(d)
    for k in ("loading-initial", "error-load"):
        acc.add(k, "блок со своим источником (source: own)")
    nodes = _nodes([(f.pointer, f.nodes) for f in p.areas.values() if f.kind == "tree"])
    coll = [n.head for n in nodes if n.ui_type in COLLECTION_TYPES or (n.ui_type == "Card" and "items" in n.attrs)]
    if coll or isinstance(rec.fm.get("collection"), dict):
        for k in ("empty-first-run", "empty-filtered", "partial-few"):
            acc.add(k, "блок со своим источником и коллекцией")
    res.items = acc.items()
    _cover(res, p.states, d)
    return res


def _cover(res, states, d):
    need = {i.key for i in res.items}
    for i in res.items:
        sv = states.get(i.key)
        if sv is None or sv.empty:
            continue
        if sv.na is not None:
            i.na = sv.na
            i.covered = "na" if sv.na.strip() else None
        elif sv.slots:
            i.covered = "delta"
    for key in states:
        if key in need:
            continue
        (res.optional if key in d.key2id else res.unknown).append(key)


# ------------------------------------------------------------------ проверки

EMPTY_KEYS = ("empty-first-run", "empty-filtered", "empty-cleared")


def _unknown_message(key):
    syn = synonyms_cached().get(key)
    if key in T.APP_STATES:
        return (f"ключ `{key}` — состояние приложения: его объявляет раздел «Состояния приложения» основного каркаса, "
                "экран его не повторяет")
    if syn and syn["kind"] == "state":
        more = f" (за ним и {', '.join(syn['to'][1:])} — выбрать по смыслу)" if len(syn["to"]) > 1 else ""
        return f"ключ `{key}` вне словаря состояний экрана; ключ словаря — `{syn['to'][0]}`{more}"
    if syn and syn["kind"] == "ideal":
        return f"ключ `{key}` — идеальное состояние: у экрана это slot-fills, ключа в states нет"
    if syn and syn["kind"] == "app":
        return f"ключ `{key}` — состояние приложения: оверлей каркаса, а не состояние экрана"
    return f"ключ `{key}` вне словаря состояний экрана (ux 06/01 §2: empty-first-run … generating)"


def check_layer(lay):
    d = dictionary()
    trees = T.parse_layer(lay)
    chk = T.Checker(lay, trees)                         # add() с путями и подсказкой исполнителя
    for group in (trees.screens, trees.blocks):
        for slug, p in group.items():
            for key, sv in p.states.items():
                if key not in d.key2id:
                    chk.add("R-STRUCT-022", "error", p, sv.pointer, _unknown_message(key))
    for slug, p in trees.screens.items():
        res = screen_set(lay, slug, trees)
        _missing(chk, p, res)
        _sem015(chk, lay, trees, slug, p)
    for slug, p in trees.blocks.items():
        if T.is_own(trees, slug):
            _missing(chk, p, block_set(lay, slug, trees))
    return chk.rep.items


def _missing(chk, p, res):
    sev = F.severity_for(p.record.status)
    for i in res.items:
        if i.covered:
            continue
        why = "; ".join(i.reasons)
        if i.na is not None:
            msg = f"обязательное состояние `{i.key}` ({i.id}): «не применимо» без причины — {why}"
        else:
            msg = f"обязательное состояние `{i.key}` ({i.id}) не покрыто: нет дельты и «не применимо: причина» — {why}"
        chk.add("R-SEM-011", sev, p, f"/states/{T.esc(i.key)}", msg)


def _sem015(chk, lay, trees, slug, p):
    comp = T.composition(trees, slug, with_states=False, with_own=False)
    header_primary = False
    for b in comp["blocks"]:
        bp = trees.blocks.get(b)
        fill = bp.areas.get("block-header") if bp else None
        if fill and fill.kind == "tree" and any(n.attrs.get("level") == "primary" for n, _ in T.walk(fill.nodes)):
            header_primary = True
    groups = []                                         # пустые состояния, видимые одновременно
    for key in EMPTY_KEYS:
        sv = p.states.get(key)
        if sv is None or sv.na is not None:
            continue
        nodes = []
        for fill in sv.slots.values():
            if fill.kind == "tree":
                nodes += [n for n, _ in T.walk(fill.nodes)]
        if header_primary and any(n.attrs.get("level") == "primary" for n in nodes):
            chk.add("R-SEM-015", "warning", p, sv.pointer,
                    f"`{key}`: главная кнопка видна в шапке блока, а пустое состояние повторяет её главной кнопкой — "
                    "текстом или level=tertiary")
        groups.append([(p, sv.pointer, n) for n in nodes if n.ui_type == "EmptyState"])
    own = []                                            # блоки со своим источником пустеют независимо — вместе
    for b in T.composition(trees, slug, with_states=False)["blocks"]:
        bp = trees.blocks.get(b)
        if bp is None or not T.is_own(trees, b):
            continue
        found = []
        for key in EMPTY_KEYS:
            sv = bp.states.get(key)
            if sv is None or sv.na is not None:
                continue
            for fill in sv.slots.values():
                if fill.kind == "tree":
                    found += [(bp, sv.pointer, n) for n, _ in T.walk(fill.nodes) if n.ui_type == "EmptyState"]
        if found:
            own.append(found)
    if len(own) >= 2:
        groups.append([x for f in own for x in f])
    for group in groups:
        if len(group) >= 2:
            _only_text(chk, slug, group)


def _only_text(chk, slug, empties):
    for rec_p, ptr, es in empties:
        bad = [n.head for n, _ in T.walk([es]) if n is not es and n.prefix == "ui" and
               (n.ui_type not in ("Button", "Link") or (n.ui_type == "Button" and n.attrs.get("level") != "tertiary"))]
        if "illustration" in es.attrs:
            bad.insert(0, f"illustration={es.attrs['illustration']}")
        if bad:
            chk.add("R-SEM-015", "warning", rec_p, ptr,
                    f"на экране {slug} несколько пустых состояний: в каждом только текст и третичные кнопки, "
                    f"а здесь {', '.join(bad)}")


# ------------------------------------------------------------------ вывод

def dump(lay):
    d = dictionary()
    trees = T.parse_layer(lay)
    out = {"project": lay.slug, "surface": lay.surface, "priority": d.priority, "overlays": d.overlays,
           "screens": {s: screen_set(lay, s, trees).as_dict() for s in trees.screens},
           "blocks": {s: block_set(lay, s, trees).as_dict() for s in trees.blocks if T.is_own(trees, s)}}
    return out


def show(lay, as_json=False, out=None):
    out = out or sys.stdout
    data = dump(lay)
    if as_json:
        print(json.dumps(data, ensure_ascii=False, indent=1), file=out)
        return
    print(f"== {lay.surface}: наборы состояний; приоритет {' > '.join(data['priority'])}; поверх — "
          f"{', '.join(data['overlays'])}", file=out)
    for group in ("screens", "blocks"):
        for slug, s in data[group].items():
            print(f"{s['kind']} {slug} [{s['status'] or '—'}]", file=out)
            for i in s["required"]:
                mark = {"delta": "дельта", "na": "не применимо"}.get(i["covered"], "НЕТ")
                print(f"  {i['key']:<24} {i['id'] or '':<4} {mark:<13} {'; '.join(i['reasons'])}", file=out)
            if s["optional"]:
                print(f"  сверх набора: {', '.join(s['optional'])}", file=out)
            if s["unknown"]:
                print(f"  вне словаря: {', '.join(s['unknown'])}", file=out)
            for m in s["manual"]:
                print(f"  чтением: {m['key']} — {m['why']}", file=out)
            for n in s["notes"]:
                print(f"  заметка: {n}", file=out)


# ------------------------------------------------------------------ самопроверка

EXPECT_DEFECTS = [("R-STRUCT-022", "error", 1), ("R-SEM-011", "error", 2)]


def _selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    d = dictionary()
    check("словарь: 24 состояния, приоритет и наложения из YAML базы",
          len(d.key2id) == 24 and d.priority[:3] == ["no-permission", "offline", "not-found"] and
          d.overlays == ["stale", "limit-reached"])
    rows = type_rows()
    check("таблица типов README: 10 типов, у list — «Список и таблица» и «Поиск» при поиске",
          len(rows) == 10 and ("Список и таблица", None) in rows["list"] and ("Поиск", "search") in rows["list"])
    check("строки типов находятся в матрице по названию",
          all(d.by_title.get(t) for rs in rows.values() for t, c in rs))
    check("canvas — строки нет; master-detail — две строки", rows["canvas"] == [] and len(rows["master-detail"]) == 2)
    syn = input_synonyms()
    check("таблица ключей mobile: loading → loading-initial (и ещё два), populated — идеальное, maintenance — "
          "приложение", syn["loading"]["to"][0] == "loading-initial" and len(syn["loading"]["to"]) == 3 and
          syn["populated"]["kind"] == "ideal" and syn["maintenance"]["kind"] == "app")
    check("сообщение R-STRUCT-022 подсказывает ключ словаря", "`loading-initial`" in _unknown_message("loading"))

    def extra(check, fx, lay):
        res = screen_set(lay, "requests-list")
        keys = [i.key for i in res.items]
        check("набор списка: строка типа, коллекция, фильтр, роли, отказы ситуаций",
              keys == ["empty-first-run", "empty-filtered", "partial-few", "overflow-many", "loading-initial",
                       "loading-refresh", "error-load", "error-action", "no-permission"])
        why = {i.key: i.reasons for i in res.items}
        check("причины: «почему в наборе»", any("коллекция" in r for r in why["empty-first-run"]) and
              any("ролями" in r for r in why["no-permission"]) and any("create-request" in r
                                                                      for r in why["error-action"]))
        card = {i.key: i for i in screen_set(lay, "request-card").items}
        check("карточка: not-found по параметру объекта, offline по отказу ситуации",
              "not-found" in card and "offline" in card and card["not-found"].covered == "delta")
        dash = [i.key for i in screen_set(lay, "plan-dashboard").items]
        check("дашборд: строка «Дашборд и плитка показателя»; плитка своего источника — свой набор",
              "partial-failure" in dash and [i.key for i in block_set(lay, "plan-tile").items] ==
              ["loading-initial", "error-load"])
        nf = [i.key for i in screen_set(lay, "not-found").items]
        check("служебный экран: строка маршрута без no-permission при access: authenticated",
              nf == ["loading-initial", "error-load"])
        check("приоритет у экрана не требуется: ключа priority в наборе нет",
              "priority" not in json.dumps(screen_set(lay, "requests-list").as_dict()))
        data = dump(lay)
        check("show --json: наборы экранов и блоков, приоритет", data["screens"] and "plan-tile" in data["blocks"]
              and data["priority"][0] == "no-permission")
        # канонический пример master-detail формы screen.md: набор совпадает с его ключами
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory(prefix="ddd-states-") as td:
            root = Path(td) / "r"
            shutil.copytree(fx.root, root)
            scr = root / "docs" / "projects" / fx.slug / "screens" / "office" / "screens" / "requests-list" / "index.md"
            text = scr.read_text(encoding="utf-8").replace("type: list", "type: master-detail")
            scr.write_text(text, encoding="utf-8")
            cap = root / "docs" / "projects" / fx.slug / "capability" / "office.md"
            cap.write_text(cap.read_text(encoding="utf-8").replace("duration: instant", "duration: background"),
                           encoding="utf-8")
            lay2 = L.Layer(fx.slug, "office", root)
            keys2 = [i.key for i in screen_set(lay2, "requests-list").items]
            check("master-detail: строки «Список и таблица» и «Карточка объекта» — success и error-action",
                  "success" in keys2 and "error-action" in keys2)
            check("duration: background возможности — in-progress-background", "in-progress-background" in keys2)
        with tempfile.TemporaryDirectory(prefix="ddd-states-syn-") as td:
            root = Path(td) / "r"
            shutil.copytree(fx.root, root)
            base = root / "docs" / "projects" / fx.slug / "screens" / "office" / "screens"
            p = base / "requests-list" / "index.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "          - text:requests.list.empty-first-run.empty\n",
                "          - text:requests.list.empty-first-run.empty\n"
                "          - ui:Button level=primary action=create:\n"
                "              - text:requests.list.create.action\n", 1), encoding="utf-8")
            p = base / "plan-dashboard" / "index.md"
            p.write_text(p.read_text(encoding="utf-8").replace(
                "          - text:plan.dashboard.empty-first-run.empty\n",
                "          - text:plan.dashboard.empty-first-run.empty\n      - ui:EmptyState illustration=empty-box:\n"
                "          - text:plan.dashboard.plan-tile.empty\n", 1), encoding="utf-8")
            sem = [f for f in check_layer(L.Layer(fx.slug, "office", root)) if f.rule == "R-SEM-015"]
            check("синтетика R-SEM-015: главная кнопка шапки в пустом состоянии; два пустых сразу — иллюстрация",
                  len(sem) == 2 and any("шапке" in f.message for f in sem) and
                  any("illustration" in f.message for f in sem))

    T.selftest_fixtures(check, run_check=check_layer, expect=EXPECT_DEFECTS, tool="states", extra=extra)
    print("states selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return _selftest()
    return T.run(argv, prog="states", description=__doc__, check=check_layer, show_fn=show)


if __name__ == "__main__":
    sys.exit(main())
