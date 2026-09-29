#!/usr/bin/env python3
"""tree — разбор деревьев слоя экранов по грамматике канона и проверки узлов.

Грамматика — канон `docs/projects/_template/screens/README.md` («Нотация дерева», «Узлы», «Атрибуты»; управляемая
копия — `.claude/skills/screen-deep-dive/references/tree-notation.md`). Дерево — блок ```yaml``` в теле записи: узел
без детей — строка-голова, узел с детьми — словарь из одного ключа-головы со списком детей, узел со структурой —
словарь атрибутов (`items`, `columns`, `areas`, `fill`, `children`). Голова — `<префикс>:<имя>` и пары
`атрибут=значение` через пробел; префиксы `ui`, `layout`, `block`, `data`, `text`, `icon`. Корни: у экрана
`slot-fills` (слот → `block:<slug>` | дети | `—`) и `states` (ключ → слот → дети | `'не применимо: причина'`), у блока
`tree` (внутренние области `block-header` · `block-body` · `block-footer` · `block-aside`) и `states` (у блока со своим
источником), у каркаса `tree` (дети). Компоненты — типы `kb/common/components.yaml` (`types`, части — `parts`, имена
`aka` не принимаются) и расширения карты решений `design/system.yaml#extensions`; `gap` — имя токена группы `space`
(есть `design/system.tokens.json` — сверка с ним, нет — только форма имени); `text:<ключ>` — строка `texts.md`.

    tree check <slug> [<surface>] [--repo DIR] [--json]     находки (строки JSON — модуль findings)
    tree show  <slug> [<surface>] [--repo DIR] [--json]     разобранные деревья; JSON — для соседних утилит
    tree --selftest                                          грамматика и фикстуры кабинета, без сети

Без <surface> — все поверхности проекта с маршрутом кабинета. Из Python: `parse_layer(Layer)` → разобранные записи,
`dump(...)` → JSON, `ui_types(...)` → типы `ui:` экранов, `composition(...)` → узлы и блоки экрана.

Правила (`.claude/skills/screen-audit/references/rules.md`):
  R-STRUCT-020  дерево не парсится: YAML блока, форма узла, голова, корни              error
  R-STRUCT-021  компонент вне словаря и расширений; имя из aka (находка называет тип); часть вне parts   error
  R-SEM-014     атрибут или ключ структуры вне списка; значения level, justify, align, wrap; gap — имя
                токена space; illustration — только у EmptyState; fills — только в каркасе; атрибут дважды   warning
  R-TX-001      ключ text: без строки texts.md (деревья, «Состояния приложения», form[].error, tiles[].no-data)  error
  R-TX-002      роль строки ≠ роль части компонента (text_roles словаря) или ≠ последнему сегменту ключа   error
  R-TX-003      литерал текста в дереве (строка-лист, label колонки)                     error у stable, hint у draft
  R-TX-004      ключ stable-экрана (с блоками слотов и каркасом) — строка ниже checked; находка — одна на ключ,
                в месте его употребления, со списком stable-экранов                     error
  R-TX-005      реестр не по форме: колонки и порядок, ключ, дубли, роль, статус, maxlen у checked   error
  R-TX-006      строка реестра без ключа в деревьях                                     hint
  R-STRUCT-010  блок без block-body с узлом                                             error
  R-STRUCT-011  слот slot-fills или дельты состояния не объявлен в slots каркаса        error
  R-STRUCT-012  содержимое слота не по accepts                                          error
  R-STRUCT-013  обязательный слот каркаса пуст                                          warning, error у stable
  R-STRUCT-025  основной каркас (с навигацией items=nav) без раздела «Состояния приложения»   warning, error у stable
  R-STRUCT-001  block:<slug> узлов и tiles[].link — нет записи этой поверхности          error
  R-STRUCT-002  data:<датум> узлов, атрибутов, block.data, form, tiles — нет строки data-items.md   error
  R-STRUCT-023  data:<датум>.<атрибут> — нет атрибута у объекта датума; action=, bulk, tiles[].action,
                колонка action реестра — нет действия action.md; колонка object — нет объекта   error
Ссылки в interface и продукт проверяются, когда файл-источник есть (data-items.md, object.md, action.md).
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

PREFIXES = ("ui", "layout", "block", "data", "text", "icon")
LAYOUTS = ("row", "stack", "grid", "layer")
AREAS = ("block-header", "block-body", "block-footer", "block-aside")
ATTRS = {"ui": ("level", "action", "illustration", "items", "columns", "value", "fills"),
         "layout": ("gap", "justify", "align", "wrap", "columns", "areas", "fill", "span", "fills")}
STRUCT_KEYS = ("items", "columns", "areas", "fill", "children")
VALUES = {"level": ("primary", "secondary", "tertiary"), "justify": ("start", "center", "end", "between"),
          "align": ("start", "center", "stretch"), "wrap": ("true", "false")}
ACCEPTS = ("block", "tree", "block | tree", "block (modal/drawer)")
NAV_TYPES = ("Sidebar", "TopBar", "BottomNav")
# строки раздела «Состояния приложения» основного каркаса — форма docs/projects/_template/screens/_template/shell.md
APP_STATES = ("service-unavailable", "maintenance", "session-expiry", "connection-lost", "demo-mode")
TEXT_STATUSES = ("assumed", "checked", "approved")

HEAD = re.compile(r"^(?P<prefix>[a-z][a-z-]*):(?P<name>[^\s=]+)(?P<attrs>(?: [a-z][a-z0-9-]*=\S+)*)$")
PREFIX_LIKE = re.compile(r"^(?P<prefix>[a-z][a-z-]*):\S")
NA = re.compile(r"^не применимо\b\s*:?\s*(?P<reason>.*)$", re.S)
UI_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)?$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DATA_NAME = re.compile(r"^(?P<item>[a-z0-9]+(?:-[a-z0-9]+)*)(?:\.(?P<attr>[a-z0-9]+(?:-[a-z0-9]+)*))?$")
TEXT_KEY = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)+$")
KEY_FORM = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*){3,}$")
SPACE_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+(?:-[a-z0-9]+)*)*$")


def esc(key):
    """Сегмент JSON Pointer."""
    return str(key).replace("~", "~0").replace("/", "~1")


# ------------------------------------------------------------------ модель разбора

@dataclass
class Issue:
    rule: str
    pointer: str
    message: str
    severity: str | None = None                         # None — по правилу и статусу записи


@dataclass
class Node:
    pointer: str                                        # JSON Pointer места узла в разобранном YAML тела
    head: str | None = None                             # голова как в файле; у литерала — None
    prefix: str | None = None
    name: str | None = None                             # ui: Тип[.Часть]; data: датум[.атрибут]; text: ключ; …
    attrs: dict = field(default_factory=dict)
    struct: dict = field(default_factory=dict)          # items, columns, areas — как в YAML; fill — {область: [Node]}
    children: list = field(default_factory=list)
    literal: str | None = None                          # литерал текста вместо узла
    valid: bool = True                                  # голова разобрана по грамматике

    @property
    def ui_type(self):
        return self.name.split(".", 1)[0] if self.prefix == "ui" and self.name and self.valid else None

    @property
    def ui_part(self):
        if self.prefix == "ui" and self.name and "." in self.name and self.valid:
            return self.name.split(".", 1)[1]
        return None

    def kids(self):
        """Дети и узлы областей сетки (`fill`)."""
        out = list(self.children)
        for nodes in (self.struct.get("fill") or {}).values():
            out += nodes
        return out

    def as_dict(self):
        d = {"pointer": self.pointer}
        if self.literal is not None:
            d["literal"] = self.literal
            return d
        d.update({"head": self.head, "prefix": self.prefix, "name": self.name, "valid": self.valid})
        if self.prefix == "ui" and self.valid:
            d["type"], d["part"] = self.ui_type, self.ui_part
        if self.attrs:
            d["attrs"] = dict(self.attrs)
        if self.struct:
            s = {k: v for k, v in self.struct.items() if k != "fill"}
            if "fill" in self.struct:
                s["fill"] = {k: [n.as_dict() for n in v] for k, v in self.struct["fill"].items()}
            d["struct"] = s
        if self.children:
            d["children"] = [n.as_dict() for n in self.children]
        return d


@dataclass
class Fill:
    """Содержимое слота или области: block — ссылка на блок, tree — узлы, empty — `—`."""
    kind: str
    pointer: str
    block: str | None = None
    nodes: list = field(default_factory=list)

    def as_dict(self):
        if self.kind == "block":
            return {"block": self.block}
        if self.kind == "tree":
            return {"nodes": [n.as_dict() for n in self.nodes]}
        return None


@dataclass
class StateVal:
    pointer: str
    na: str | None = None                               # причина «не применимо» (может быть пустой)
    slots: dict = field(default_factory=dict)           # слот или область → Fill
    empty: bool = False                                 # пустая секция

    @property
    def not_applicable(self):
        return self.na is not None

    def as_dict(self):
        if self.na is not None:
            return {"na": self.na}
        return {"slots": {k: v.as_dict() for k, v in self.slots.items()}}


@dataclass
class Parsed:
    """Разобранная запись: корни и замечания разбора."""
    record: L.Record
    fills: dict = field(default_factory=dict)           # экран: слот → Fill
    areas: dict = field(default_factory=dict)           # блок: область → Fill
    nodes: list = field(default_factory=list)           # каркас: дети корня
    states: dict = field(default_factory=dict)          # экран и блок: ключ → StateVal
    issues: list = field(default_factory=list)
    broken: bool = False                                # файл, frontmatter или блок YAML не разбираются

    @property
    def kind(self):
        return self.record.kind

    @property
    def slug(self):
        return self.record.slug

    def roots(self, with_states=True):
        """(указатель корня, узлы) всех деревьев записи."""
        out = []
        for d in (self.fills, self.areas):
            for fill in d.values():
                if fill.kind == "tree":
                    out.append((fill.pointer, fill.nodes))
        if self.nodes:
            out.append(("/tree", self.nodes))
        if with_states:
            for sv in self.states.values():
                for fill in sv.slots.values():
                    if fill.kind == "tree":
                        out.append((fill.pointer, fill.nodes))
        return out


# ------------------------------------------------------------------ разбор

def _head_problem(text):
    if re.search(r"\s=|=\s", text):
        return "пробелы вокруг «=»: пары атрибут=значение пишутся без пробелов"
    if re.search(r"\s-\s", text) or "\n" in text:
        return "узлы склеились в строку: у узла с детьми голова кончается двоеточием, дети — списком ниже"
    if "(fills" in text:
        return "слот каркаса — атрибут fills=$<слот> в голове узла"
    return "голова не по грамматике: <префикс>:<имя> и пары атрибут=значение через пробел"


def parse_head(text, pointer, issues):
    """Строка-голова → Node (литерал текста — Node.literal)."""
    text = str(text).strip()
    node = Node(pointer=pointer, head=text)
    m = HEAD.match(text)
    pm = PREFIX_LIKE.match(text)
    if not m:
        if pm and pm.group("prefix") in PREFIXES:
            node.prefix, node.valid = pm.group("prefix"), False
            issues.append(Issue("R-STRUCT-020", pointer, f"`{text}` — {_head_problem(text)}"))
        else:
            node.head, node.literal = None, text
        return node
    prefix, name = m.group("prefix"), m.group("name")
    node.prefix, node.name = prefix, name
    if prefix not in PREFIXES:
        node.valid = False
        issues.append(Issue("R-STRUCT-020", pointer, f"`{text}` — префикс `{prefix}:` вне списка "
                                                     f"({', '.join(p + ':' for p in PREFIXES)})"))
        return node
    for pair in m.group("attrs").split():
        k, v = pair.split("=", 1)
        if k in node.attrs:
            issues.append(Issue("R-SEM-014", pointer, f"`{text}` — атрибут `{k}` дважды"))
        node.attrs[k] = v
    bad = None
    if prefix == "ui" and not UI_NAME.match(name):
        bad = "ui:<Тип> или ui:<Тип>.<Часть>"
    elif prefix == "layout" and name not in LAYOUTS:
        bad = "layout:" + "|".join(LAYOUTS)
    elif prefix in ("block", "icon") and not SLUG.match(name):
        bad = f"{prefix}:<slug> в kebab-case"
    elif prefix == "data" and not DATA_NAME.match(name):
        bad = "data:<датум>[.<атрибут>]"
    elif prefix == "text" and not TEXT_KEY.match(name):
        bad = "text:<ключ реестра> — сегменты латиницей через точку"
    if bad:
        node.valid = False
        issues.append(Issue("R-STRUCT-020", pointer, f"`{text}` — имя не по форме {bad}"))
    return node


def parse_list(value, pointer, issues):
    if not isinstance(value, list):
        issues.append(Issue("R-STRUCT-020", pointer, "ждали список узлов"))
        return []
    return [parse_item(v, f"{pointer}/{i}", issues) for i, v in enumerate(value)]


def parse_item(item, pointer, issues):
    if isinstance(item, str):
        return parse_head(item, pointer, issues)
    if isinstance(item, dict) and len(item) == 1:
        (key, val), = item.items()
        if not isinstance(key, str):
            issues.append(Issue("R-STRUCT-020", pointer, f"голова узла — строка, не {type(key).__name__}"))
            return Node(pointer=pointer, valid=False)
        node = parse_head(key, pointer, issues)
        sub = f"{pointer}/{esc(key)}"
        if node.literal is not None:
            issues.append(Issue("R-STRUCT-020", pointer, f"`{key}` — у узла с детьми голова <префикс>:<имя>"))
            node.literal, node.head, node.valid = None, key, False
        if isinstance(val, list):
            node.children = parse_list(val, sub, issues)
        elif isinstance(val, dict):
            _parse_struct(node, val, sub, issues)
        elif val is None:
            issues.append(Issue("R-STRUCT-020", pointer, f"`{key}:` — двоеточие без детей: у листа двоеточия нет"))
        else:
            issues.append(Issue("R-STRUCT-020", pointer, f"`{key}:` — значение узла — список детей или словарь "
                                                         "структуры"))
        return node
    what = "словарь из нескольких ключей" if isinstance(item, dict) else type(item).__name__
    issues.append(Issue("R-STRUCT-020", pointer, f"узел — строка-голова или словарь из одного ключа, а не {what}"))
    return Node(pointer=pointer, valid=False)


def _parse_struct(node, val, pointer, issues):
    for k, v in val.items():
        sp = f"{pointer}/{esc(k)}"
        if k == "children":
            node.children = parse_list(v, sp, issues)
            continue
        if k not in STRUCT_KEYS:
            issues.append(Issue("R-SEM-014", sp, f"`{node.head}` — ключ структуры `{k}` вне списка "
                                                 f"({', '.join(STRUCT_KEYS)})"))
            node.struct[k] = v
            continue
        if k in node.attrs:
            issues.append(Issue("R-SEM-014", sp, f"`{node.head}` — атрибут `{k}` и в голове, и в структуре: "
                                                 "один атрибут — в одном месте узла"))
        if k == "fill":
            fill = {}
            if isinstance(v, dict):
                for area, x in v.items():
                    ap = f"{sp}/{esc(area)}"
                    fill[str(area)] = parse_list(x, ap, issues) if isinstance(x, list) else [parse_item(x, ap, issues)]
            else:
                issues.append(Issue("R-STRUCT-020", sp, "fill — словарь «область сетки: узел или список узлов»"))
            node.struct["fill"] = fill
        else:
            node.struct[k] = v


def parse_fill(value, pointer, issues):
    if value is None or (isinstance(value, str) and L.is_empty(value)):
        return Fill("empty", pointer)
    if isinstance(value, str):
        node = parse_head(value, pointer, issues)
        if node.valid and node.prefix == "block" and not node.attrs:
            return Fill("block", pointer, block=node.name)
        if node.literal is None and node.valid:
            issues.append(Issue("R-STRUCT-020", pointer, f"`{value}` — значение слота: block:<slug>, список узлов "
                                                         "или «—»"))
        elif node.literal is not None:
            issues.append(Issue("R-STRUCT-020", pointer, f"«{value}» — значение слота: block:<slug>, список узлов "
                                                         "или «—»"))
        return Fill("empty", pointer)
    if isinstance(value, list):
        return Fill("tree", pointer, nodes=parse_list(value, pointer, issues))
    issues.append(Issue("R-STRUCT-020", pointer, "значение слота: block:<slug>, список узлов или «—»"))
    return Fill("empty", pointer)


def parse_states(value, pointer, issues):
    out = {}
    if value is None:
        return out
    if not isinstance(value, dict):
        issues.append(Issue("R-STRUCT-020", pointer, "states — словарь «ключ состояния: дельта или "
                                                     "'не применимо: причина'»"))
        return out
    for key, v in value.items():
        sp = f"{pointer}/{esc(key)}"
        key = str(key)
        if isinstance(v, str):
            m = NA.match(v.strip())
            if m:
                out[key] = StateVal(sp, na=m.group("reason").strip())
            else:
                issues.append(Issue("R-STRUCT-020", sp, f"`{key}` — значение: дельта слотов или "
                                                        "'не применимо: причина'"))
                out[key] = StateVal(sp, empty=True)
        elif isinstance(v, dict) and v:
            out[key] = StateVal(sp, slots={str(s): parse_fill(x, f"{sp}/{esc(s)}", issues) for s, x in v.items()})
        else:
            issues.append(Issue("R-STRUCT-020", sp, f"`{key}` — пустая секция: дельта слотов или "
                                                    "'не применимо: причина'"))
            out[key] = StateVal(sp, empty=True)
    return out


def parse_record(rec):
    p = Parsed(record=rec)
    if rec.error or rec.md is None:
        p.issues.append(Issue("R-STRUCT-020", "", f"файл не читается: {rec.error}"))
        p.broken = True
        return p
    if rec.md.fm_error:
        p.issues.append(Issue("R-STRUCT-020", "", rec.md.fm_error))
        p.broken = True
    for blk in rec.md.yaml_blocks:
        if blk.error:
            p.issues.append(Issue("R-STRUCT-020", "", f"блок YAML тела не разбирается: {blk.error}"))
            p.broken = True
        elif blk.data is not None and not isinstance(blk.data, dict):
            p.issues.append(Issue("R-STRUCT-020", "", f"блок YAML тела (стр. {blk.line}) — словарь корней "
                                                      "(tree, slot-fills, states)"))
    data = rec.data
    if rec.kind == "block":
        tree = data.get("tree")
        if isinstance(tree, dict):
            for area, v in tree.items():
                ap = f"/tree/{esc(area)}"
                if area not in AREAS:
                    p.issues.append(Issue("R-STRUCT-020", ap, f"`{area}` — корень дерева блока: внутренние области "
                                                              f"{', '.join(AREAS)}"))
                p.areas[str(area)] = parse_fill(v, ap, p.issues)
        elif tree is not None:
            p.issues.append(Issue("R-STRUCT-020", "/tree", "дерево блока — словарь внутренних областей "
                                                           f"({', '.join(AREAS)})"))
        p.states = parse_states(data.get("states"), "/states", p.issues)
    elif rec.kind == "shell":
        tree = data.get("tree")
        if isinstance(tree, list):
            p.nodes = parse_list(tree, "/tree", p.issues)
        elif tree is not None:
            p.issues.append(Issue("R-STRUCT-020", "/tree", "дерево каркаса — список узлов"))
    elif rec.kind == "screen":
        sf = data.get("slot-fills")
        if isinstance(sf, dict):
            p.fills = {str(s): parse_fill(v, f"/slot-fills/{esc(s)}", p.issues) for s, v in sf.items()}
        elif sf is not None:
            p.issues.append(Issue("R-STRUCT-020", "/slot-fills", "slot-fills — словарь «слот: содержимое»"))
        p.states = parse_states(data.get("states"), "/states", p.issues)
    return p


class Trees:
    """Разобранные записи поверхности: screens, blocks, shells (Parsed по slug)."""

    def __init__(self, lay):
        self.lay = lay
        self.screens = {s: parse_record(r) for s, r in lay.screens.items()}
        self.blocks = {s: parse_record(r) for s, r in lay.blocks.items()}
        self.shells = {s: parse_record(r) for s, r in lay.shells.items()}

    def all(self):
        yield from self.screens.values()
        yield from self.blocks.values()
        yield from self.shells.values()


def parse_layer(lay):
    """Разобранные деревья поверхности (кэш на объекте Layer)."""
    t = getattr(lay, "_trees", None)
    if t is None:
        t = Trees(lay)
        lay._trees = t
    return t


def walk(nodes, ancestors=()):
    """(узел, предки) в глубину, включая узлы областей сетки."""
    for n in nodes:
        yield n, ancestors
        yield from walk(n.kids(), ancestors + (n,))


def is_nav(n):
    """Узел навигации приложения: `ui:Sidebar|TopBar|BottomNav items=nav`."""
    return n.ui_type in NAV_TYPES and n.attrs.get("items") == "nav"


def main_shells(trees):
    """Основные каркасы — каркасы с узлом навигации."""
    return [p for p in trees.shells.values() if any(is_nav(n) for n, _ in walk(p.nodes))]


def nav_node(trees):
    """(каркас, узел навигации) основного каркаса или (None, None)."""
    for p in main_shells(trees):
        for n, _ in walk(p.nodes):
            if is_nav(n):
                return p, n
    return None, None


# ------------------------------------------------------------------ состав экрана

def fill_blocks(fill):
    """Блоки, на которые ссылается содержимое слота: `block:` слота и узлы `block:` дерева."""
    if fill.kind == "block":
        return [fill.block]
    out = []
    for n, _ in walk(fill.nodes):
        if n.prefix == "block" and n.valid:
            out.append(n.name)
    return out


def is_own(trees, block):
    """Блок со своим источником данных (`source: own`)."""
    rec = trees.lay.blocks.get(block)
    return rec is not None and str(rec.fm.get("source") or "screen").strip() == "own"


def block_closure(trees, slugs, skip=None):
    """Блоки и вложенные в них блоки (узлы `block:` в деревьях блоков) — по порядку, без повторов; skip(slug) —
    блок и его вложенные не берутся."""
    seen, out, queue = set(), [], list(slugs)
    while queue:
        b = queue.pop(0)
        if b in seen:
            continue
        seen.add(b)
        if skip is not None and skip(b):
            continue
        out.append(b)
        p = trees.blocks.get(b)
        if p is None:
            continue
        for fill in p.areas.values():
            queue += fill_blocks(fill)
    return out


def composition(trees, screen, with_states=True, with_own=True):
    """Состав экрана: {"blocks": [slug …], "fills": [(pointer, узлы)], "block_trees": {slug: [(pointer, узлы)]}}.
    with_own=False — без блоков со своим источником (`source: own`) и их вложенных блоков."""
    p = trees.screens[screen]
    direct = []
    fills = []
    for fill in p.fills.values():
        direct += fill_blocks(fill)
        if fill.kind == "tree":
            fills.append((fill.pointer, fill.nodes))
    if with_states:
        for sv in p.states.values():
            for fill in sv.slots.values():
                direct += fill_blocks(fill)
                if fill.kind == "tree":
                    fills.append((fill.pointer, fill.nodes))
    blocks = block_closure(trees, direct, skip=None if with_own else (lambda b: is_own(trees, b)))
    block_trees = {}
    for b in blocks:
        bp = trees.blocks.get(b)
        if bp is not None:
            block_trees[b] = [(f.pointer, f.nodes) for f in bp.areas.values() if f.kind == "tree"]
    return {"blocks": blocks, "fills": fills, "block_trees": block_trees}


def screen_nodes(trees, screen, with_states=True, with_own=True):
    """Все узлы состава экрана (деревья слотов и блоков)."""
    comp = composition(trees, screen, with_states, with_own)
    out = []
    for _, nodes in comp["fills"]:
        out += [n for n, _ in walk(nodes)]
    for roots in comp["block_trees"].values():
        for _, nodes in roots:
            out += [n for n, _ in walk(nodes)]
    return out


def ui_types(trees, stable_only=True):
    """Типы `ui:` экранов поверхности (с блоками их слотов и каркасами) — для покрытия ДС."""
    types = set()
    for slug, p in trees.screens.items():
        if stable_only and not p.record.stable:
            continue
        for n in screen_nodes(trees, slug):
            if n.ui_type:
                types.add(n.ui_type)
        shell = trees.shells.get(str(p.record.fm.get("shell") or ""))
        if shell is not None:
            types.update(n.ui_type for n, _ in walk(shell.nodes) if n.ui_type)
    return sorted(types)


# ------------------------------------------------------------------ тексты: ключи, роли, места

@dataclass
class TextUse:
    key: str
    parsed: Parsed
    pointer: str
    roles: list                                         # роли части компонента, пусто — роль по месту
    where: str                                          # tree · column · form · tiles · app-states


def app_state_rows(rec):
    """Строки таблицы раздела «Состояния приложения» каркаса: [(состояние, Row)]."""
    if rec.md is None:
        return None
    line, body = rec.md.section("Состояния приложения")
    if body is None:
        return None
    t = L.find_table(body, ("состояние",), first_line=(line or 0) + 1)
    return [(L.cell(r.get("состояние")), r) for r in (t.rows if t else [])]


def columns_of(node):
    cols = node.struct.get("columns")
    return cols if isinstance(cols, list) else []


def text_uses(trees, comps):
    uses = []
    for p in trees.all():
        for _, nodes in p.roots():
            for n, anc in walk(nodes):
                if n.prefix == "text" and n.valid:
                    uses.append(TextUse(n.name, p, n.pointer, _roles_of(anc, comps), "tree"))
                for col_i, col in enumerate(columns_of(n)):
                    if isinstance(col, dict) and isinstance(col.get("label"), str) and \
                            col["label"].startswith("text:"):
                        roles = comps.roles(n.ui_type, "Header") if n.ui_type else []
                        uses.append(TextUse(col["label"][5:], p, f"{n.pointer}/{esc(n.head)}/columns/{col_i}/label",
                                            roles, "column"))
        fm = p.record.fm
        for i, f in enumerate(fm.get("form") or [] if isinstance(fm.get("form"), list) else []):
            if isinstance(f, dict) and isinstance(f.get("error"), str) and f["error"].startswith("text:"):
                uses.append(TextUse(f["error"][5:], p, f"/form/{i}/error", ["error"], "form"))
        for i, t in enumerate(fm.get("tiles") or [] if isinstance(fm.get("tiles"), list) else []):
            if isinstance(t, dict) and isinstance(t.get("no-data"), str) and t["no-data"].startswith("text:"):
                uses.append(TextUse(t["no-data"][5:], p, f"/tiles/{i}/no-data", [], "tiles"))
        if p.kind == "shell":
            for state, row in app_state_rows(p.record) or []:
                for key in re.findall(r"text:([A-Za-z0-9_.-]+)", row.raw):
                    uses.append(TextUse(key, p, f"#Состояния приложения/{state}", [], "app-states"))
    return uses


def _roles_of(ancestors, comps):
    """Роли текста ближайшего компонента-предка (узлы раскладки пропускаются); пусто — роль по месту."""
    for a in reversed(ancestors):
        if a.prefix == "layout":
            continue
        if a.prefix == "ui" and a.valid:
            return comps.roles(a.ui_type, a.ui_part)
        return []
    return []


def _literals(p):
    """(указатель, текст) литералов записи: строки-листы и label колонок."""
    out = []
    for _, nodes in p.roots():
        for n, _ in walk(nodes):
            if n.literal is not None:
                out.append((n.pointer, n.literal))
            for i, col in enumerate(columns_of(n)):
                if isinstance(col, dict) and isinstance(col.get("label"), str) and \
                        not col["label"].startswith("text:"):
                    out.append((f"{n.pointer}/{esc(n.head)}/columns/{i}/label", col["label"]))
    return out


# ------------------------------------------------------------------ проверки

class Checker:
    def __init__(self, lay, trees=None):
        self.lay = lay
        self.trees = trees or parse_layer(lay)
        self.comps = lay.components
        self.rep = F.Report()
        self.ext = lay.design.extensions
        self.space = lay.design.space_tokens

    def add(self, rule, severity, parsed, pointer, message, fix=None):
        rec = parsed.record if parsed is not None else None
        if rec is None:
            self.rep.add(rule, severity, surface=self.lay.surface, kind="surface", ref=self.lay.surface,
                         path=self.lay.rel(self.lay.folder), message=message, fix=fix or "")
            return
        ref = rec.slug + (f"#{pointer}" if pointer else "")
        if fix is None:
            fix = f"/screen-deep-dive {self.lay.slug} {self.lay.surface} {rec.kind}:{rec.slug}"
        self.rep.add(rule, severity, surface=self.lay.surface, kind=rec.kind, ref=ref, path=self.lay.rel(rec.path),
                     message=message, fix=fix)

    def texts_fix(self):
        return f"/screen-deep-dive {self.lay.slug} {self.lay.surface} texts"

    def run(self):
        for p in self.trees.all():
            for iss in p.issues:
                sev = iss.severity or ("warning" if iss.rule == "R-SEM-014" else "error")
                self.add(iss.rule, sev, p, iss.pointer, iss.message)
            self.nodes(p)
            self.literals(p)
        for p in self.trees.blocks.values():
            self.block(p)
        for p in self.trees.screens.values():
            self.slots(p)
        for p in main_shells(self.trees):
            self.app_states(p)
        self.texts()
        return self.rep

    # --- узлы
    def nodes(self, p):
        in_shell = p.kind == "shell"
        for _, roots in p.roots():
            for n, anc in walk(roots):
                if n.literal is not None or not n.valid:
                    continue
                if n.prefix == "ui":
                    self.ui(p, n)
                self.attrs(p, n, anc, in_shell)
                if n.prefix == "block":
                    self.block_ref(p, n.pointer, n.name)
                if n.prefix == "data":
                    self.data_ref(p, n.pointer, n.name)
                for k in ("items", "value"):
                    v = n.attrs.get(k)
                    if isinstance(v, str) and v.startswith("data:"):
                        self.data_ref(p, n.pointer, v[5:])
                if isinstance(n.struct.get("items"), str) and n.struct["items"].startswith("data:"):
                    self.data_ref(p, n.pointer, n.struct["items"][5:])
                for col in columns_of(n):
                    if isinstance(col, dict) and isinstance(col.get("field"), str) and \
                            col["field"].startswith("data:"):
                        self.data_ref(p, n.pointer, col["field"][5:])
                if "action" in n.attrs:
                    self.action_ref(p, n.pointer, n.attrs["action"], f"`{n.head}`")
        fm = p.record.fm
        if p.kind == "block":
            data = fm.get("data")
            for k, v in (data.items() if isinstance(data, dict) else []):
                if isinstance(v, str) and v.startswith("data:"):
                    self.data_ref(p, f"/data/{esc(k)}", v[5:])
            for i, f in enumerate(fm.get("form") or [] if isinstance(fm.get("form"), list) else []):
                if isinstance(f, dict) and isinstance(f.get("field"), str) and f["field"].startswith("data:"):
                    self.data_ref(p, f"/form/{i}/field", f["field"][5:])
            coll = fm.get("collection")
            if isinstance(coll, dict):
                bulk = coll.get("bulk")
                for a in bulk if isinstance(bulk, list) else []:
                    self.action_ref(p, "/collection/bulk", str(a), "collection.bulk")
            for i, t in enumerate(fm.get("tiles") or [] if isinstance(fm.get("tiles"), list) else []):
                if not isinstance(t, dict):
                    continue
                if isinstance(t.get("value"), str) and t["value"].startswith("data:"):
                    self.data_ref(p, f"/tiles/{i}/value", t["value"][5:])
                if isinstance(t.get("action"), str) and not L.is_empty(t["action"]):
                    self.action_ref(p, f"/tiles/{i}/action", t["action"], "tiles[].action")
                if isinstance(t.get("link"), str) and not L.is_empty(t["link"]) and \
                        t["link"] not in self.lay.screens:
                    self.add("R-STRUCT-001", "error", p, f"/tiles/{i}/link",
                             f"tiles[].link `{t['link']}` — экрана нет на этой поверхности")

    def ui(self, p, n):
        t, part = n.ui_type, n.ui_part
        types = self.comps.types
        if t in types:
            if part and part not in self.comps.parts(t):
                have = ", ".join(self.comps.parts(t)) or "частей нет"
                self.add("R-STRUCT-021", "error", p, n.pointer,
                         f"`ui:{n.name}` — части `{part}` нет у типа {t} (parts: {have})")
            return
        if t in self.ext:
            parts = list(self.ext[t].get("parts") or [])
            if part and part not in parts:
                self.add("R-STRUCT-021", "error", p, n.pointer,
                         f"`ui:{n.name}` — части `{part}` нет у расширения {t} (parts: {', '.join(parts) or '—'})")
            return
        aka = self.comps.type_of(t)
        if aka:
            self.add("R-STRUCT-021", "error", p, n.pointer,
                     f"`ui:{n.name}` — имя из aka словаря компонентов; тип словаря — {aka}",
                     f"заменить на `ui:{aka}{'.' + part if part else ''}` — /screen-deep-dive {self.lay.slug} "
                     f"{self.lay.surface} {p.kind}:{p.slug}")
            return
        near = [k for k in types if k.lower() == t.lower()]
        hint = f"; есть тип {near[0]}" if near else ""
        self.add("R-STRUCT-021", "error", p, n.pointer,
                 f"`ui:{n.name}` — типа нет в словаре компонентов и в расширениях проекта{hint}",
                 "тип словаря kb/common/components.yaml; потребность, которой в словаре нет, — расширение "
                 f"design/system.yaml (/design-deep-dive {self.lay.slug})")

    def attrs(self, p, n, anc, in_shell):
        allowed = ATTRS.get(n.prefix, ())
        parent = anc[-1] if anc else None
        under_grid = parent is not None and parent.prefix == "layout" and parent.name == "grid"
        for k, v in n.attrs.items():
            if k not in allowed and not (k == "span" and under_grid):
                where = f"у узла {n.prefix}:" if allowed else f"у узла {n.prefix}: атрибутов нет"
                lst = f" ({', '.join(allowed)})" if allowed else ""
                self.add("R-SEM-014", "warning", p, n.pointer,
                         f"`{n.head}` — атрибут `{k}` вне списка {where}{lst}")
                continue
            if k in VALUES and v not in VALUES[k]:
                self.add("R-SEM-014", "warning", p, n.pointer,
                         f"`{n.head}` — `{k}={v}` вне списка: {' · '.join(VALUES[k])}")
            if k == "gap":
                self.gap(p, n, v)
            if k == "illustration" and n.ui_type != "EmptyState":
                self.add("R-SEM-014", "warning", p, n.pointer, f"`{n.head}` — illustration только у ui:EmptyState")
            if k == "fills":
                if not in_shell:
                    self.add("R-SEM-014", "warning", p, n.pointer,
                             f"`{n.head}` — fills только в дереве каркаса: экран заполняет слот в slot-fills")
                elif not re.fullmatch(r"\$[a-z0-9]+(?:-[a-z0-9]+)*", v):
                    self.add("R-SEM-014", "warning", p, n.pointer, f"`{n.head}` — fills=$<слот каркаса>, не `{v}`")
                else:
                    slots = p.record.fm.get("slots")
                    if isinstance(slots, dict) and v[1:] not in slots:
                        self.add("R-SEM-014", "warning", p, n.pointer,
                                 f"`{n.head}` — слота `{v[1:]}` нет в slots каркаса")
            if k == "span" and not under_grid:
                self.add("R-SEM-014", "warning", p, n.pointer, f"`{n.head}` — span только у дочернего узла сетки")

    def gap(self, p, n, v):
        if re.fullmatch(r"-?\d+(?:[.,]\d+)?(?:px|rem|em|%)?", v):
            self.add("R-SEM-014", "warning", p, n.pointer,
                     f"`{n.head}` — gap числом: размер намерения — имя токена группы space дизайн-системы (gap=md)")
        elif self.space is not None:
            if v not in self.space:
                shown = ", ".join(sorted(self.space)[:12]) or "—"
                self.add("R-SEM-014", "warning", p, n.pointer,
                         f"`{n.head}` — токена space.{v} нет в design/system.tokens.json (есть: {shown})")
        elif not SPACE_NAME.match(v):
            self.add("R-SEM-014", "warning", p, n.pointer,
                     f"`{n.head}` — gap={v}: имя токена группы space (xs, sm, md, lg …)")

    def block_ref(self, p, pointer, slug):
        if slug not in self.lay.blocks:
            self.add("R-STRUCT-001", "error", p, pointer, f"`block:{slug}` — блока нет на этой поверхности")

    def data_ref(self, p, pointer, name):
        m = DATA_NAME.match(name)
        if not m or not self.lay.interface.exists("data-items"):
            return
        item, attr = m.group("item"), m.group("attr")
        rows = self.lay.interface.table("data-items")
        if item not in rows:
            self.add("R-STRUCT-002", "error", p, pointer,
                     f"`data:{name}` — датума `{item}` нет в interface/{self.lay.surface}/data-items.md")
            return
        if attr is None or not self.lay.product.has_objects:
            return
        obj = rows[item].value("object")
        obj = obj.split(".", 1)[0] if obj else None
        if not obj:
            self.add("R-STRUCT-023", "error", p, pointer,
                     f"`data:{name}` — у датума `{item}` нет объекта (data-items.object: —): атрибуту `{attr}` не на "
                     "что сослаться", f"/interface-deep-dive {self.lay.slug} {self.lay.surface}")
        elif attr not in self.lay.product.attributes(obj):
            have = ", ".join(self.lay.product.attributes(obj)) or "атрибутов нет"
            self.add("R-STRUCT-023", "error", p, pointer,
                     f"`data:{name}` — атрибута `{attr}` нет у объекта `{obj}` (object.md: {have})",
                     f"/project-deep-dive {self.lay.slug}")

    def action_ref(self, p, pointer, action, where):
        if not self.lay.product.has_actions or L.is_empty(action):
            return
        if action not in self.lay.product.actions:
            self.add("R-STRUCT-023", "error", p, pointer, f"{where}: действия `{action}` нет в action.md",
                     f"/project-deep-dive {self.lay.slug}")

    def literals(self, p):
        for pointer, text in _literals(p):
            sev = F.severity_for(p.record.status, draft="hint", stable="error")
            self.add("R-TX-003", sev, p, pointer, f"литерал текста «{text}» в дереве: текст — ключ text:<ключ> со "
                                                  "строкой реестра")

    # --- блок, слоты, каркас
    def block(self, p):
        if p.broken:
            return                                      # дерево не разобрано — находка R-STRUCT-020 уже есть
        body = p.areas.get("block-body")
        if body is None or body.kind != "tree" or not body.nodes:
            self.add("R-STRUCT-010", "error", p, "/tree", "в дереве блока нет block-body с узлом")

    def slots(self, p):
        rec = p.record
        shell_slug = rec.fm.get("shell")
        shell = self.lay.shells.get(str(shell_slug)) if shell_slug else None
        if shell is None:
            return
        slots = shell.fm.get("slots")
        if not isinstance(slots, dict):
            return
        for slot, fill in p.fills.items():
            self._slot(p, shell, slots, slot, fill)
        for key, sv in p.states.items():
            for slot, fill in sv.slots.items():
                self._slot(p, shell, slots, slot, fill)
        for slot, spec in slots.items():
            if isinstance(spec, dict) and spec.get("required") is True:
                fill = p.fills.get(str(slot))
                if fill is None or fill.kind == "empty":
                    self.add("R-STRUCT-013", F.severity_for(rec.status), p, f"/slot-fills/{esc(slot)}",
                             f"обязательный слот `{slot}` каркаса `{shell.slug}` не заполнен")

    def _slot(self, p, shell, slots, slot, fill):
        if slot not in slots:
            self.add("R-STRUCT-011", "error", p, fill.pointer,
                     f"слота `{slot}` нет в slots каркаса `{shell.slug}` ({', '.join(map(str, slots))})")
            return
        spec = slots[slot] if isinstance(slots[slot], dict) else {}
        acc = str(spec.get("accepts") or "").strip()
        if acc not in ACCEPTS or fill.kind == "empty":
            return
        if acc in ("block", "block (modal/drawer)") and fill.kind != "block":
            self.add("R-STRUCT-012", "error", p, fill.pointer,
                     f"слот `{slot}` принимает `{acc}`: только block:<slug> или «—», а не дерево")
        elif acc == "tree" and fill.kind != "tree":
            self.add("R-STRUCT-012", "error", p, fill.pointer,
                     f"слот `{slot}` принимает `tree`: только дерево или «—», а не block:<slug>")

    def app_states(self, p):
        rows = app_state_rows(p.record)
        sev = F.severity_for(p.record.status)
        if rows is None:
            self.add("R-STRUCT-025", sev, p, "", "у основного каркаса нет раздела «Состояния приложения»: "
                                                 + ", ".join(APP_STATES))
            return
        have = {s: r for s, r in rows if s}
        for s in APP_STATES:
            r = have.get(s)
            if r is None:
                self.add("R-STRUCT-025", sev, p, f"#Состояния приложения/{s}",
                         f"«Состояния приложения»: нет строки `{s}`")
                continue
            cells = [v for k, v in r.cells.items() if k != "состояние"]
            na = any(re.search(r"не применимо\s*:\s*\S", c or "") for c in cells)
            if not na and any(L.is_empty(c) for c in cells):
                self.add("R-STRUCT-025", sev, p, f"#Состояния приложения/{s}",
                         f"«Состояния приложения», `{s}`: где видно, форма и тексты — или «не применимо: причина»")

    # --- тексты
    def texts(self):
        texts = self.lay.texts
        uses = text_uses(self.trees, self.comps)
        used = {}
        for u in uses:
            used.setdefault(u.key, []).append(u)
        closed = L.text_roles_closed()
        # R-TX-001, R-TX-002
        for u in uses:
            row = texts.rows.get(u.key)
            if row is None:
                self.add("R-TX-001", "error", u.parsed, u.pointer,
                         f"`text:{u.key}` — строки нет в реестре {self.lay.rel(texts.path)}", self.texts_fix())
                continue
            last = u.key.rsplit(".", 1)[-1]
            problems = []
            if row.role and last != row.role:
                problems.append(f"последний сегмент ключа `{last}` ≠ роль строки `{row.role}`")
            if u.roles and row.role not in u.roles:
                part = "части" if u.where != "form" else "поля формы (error)"
                problems.append(f"роль строки `{row.role}` ≠ роль {part} ({' · '.join(u.roles)})")
            if problems:
                self.add("R-TX-002", "error", u.parsed, u.pointer, f"`text:{u.key}` — " + "; ".join(problems),
                         self.texts_fix())
        # R-TX-004 — stable-экраны с блоками их слотов и каркасом: находка на ключ, в месте его употребления
        stable_of = {}
        for slug, p in self.trees.screens.items():
            if p.record.stable:
                for key in self._screen_keys(slug, used):
                    stable_of.setdefault(key, []).append(slug)
        for key in sorted(stable_of):
            row = texts.rows.get(key)
            if row is not None and row.status not in ("checked", "approved"):
                u = used[key][0]
                self.add("R-TX-004", "error", u.parsed, u.pointer,
                         f"`text:{key}` — строка `{row.status or '—'}`: у stable-экранов "
                         f"{', '.join(stable_of[key])} строки не ниже checked", self.texts_fix())
        if not texts.exists:
            return
        tpath = self.lay.rel(texts.path)

        def tadd(rule, sev, ref, message):
            self.rep.add(rule, sev, surface=self.lay.surface, kind="texts", ref=ref, path=tpath, message=message,
                         fix=self.texts_fix())

        # R-TX-005 — форма реестра
        t = texts.table
        if t is None:
            tadd("R-TX-005", "error", "texts", "в texts.md нет таблицы реестра с колонкой key")
            return
        cols = t.columns
        head, rest = cols[:len(L.TEXT_COLUMNS)], cols[len(L.TEXT_COLUMNS):]
        if tuple(head) != L.TEXT_COLUMNS or any(not c.startswith("text-") for c in rest):
            tadd("R-TX-005", "error", "texts", f"колонки реестра: {' · '.join(L.TEXT_COLUMNS)}, затем text-<locale>; "
                                               f"сейчас: {' · '.join(cols)}")
        for dup in texts.duplicates:
            tadd("R-TX-005", "error", f"texts#{dup.key}", f"ключ `{dup.key}` дважды (строки {texts.rows[dup.key].line}"
                                                           f" и {dup.line})")
        for key, row in texts.rows.items():
            problems = []
            if not KEY_FORM.match(key):
                problems.append("ключ не по форме {раздел}.{экран}.{элемент}.{роль} (латиница, сегменты через точку)")
            if not row.role or row.role not in closed:
                problems.append(f"роль `{row.role or '—'}` вне закрытого списка ux 07/06 §7.2 и body")
            if row.status not in TEXT_STATUSES:
                problems.append(f"статус `{row.status or '—'}` вне {' · '.join(TEXT_STATUSES)}")
            elif row.status in ("checked", "approved") and not re.fullmatch(r"\d+", row.maxlen or ""):
                problems.append(f"у `{row.status}` maxlen — число знаков")
            if row.action and self.lay.product.has_actions and row.action not in self.lay.product.actions:
                self.rep.add("R-STRUCT-023", "error", surface=self.lay.surface, kind="texts", ref=f"texts#{key}",
                             path=tpath, message=f"колонка action: действия `{row.action}` нет в action.md",
                             fix=f"/project-deep-dive {self.lay.slug}")
            if row.object and self.lay.product.has_objects and row.object not in self.lay.product.objects:
                self.rep.add("R-STRUCT-023", "error", surface=self.lay.surface, kind="texts", ref=f"texts#{key}",
                             path=tpath, message=f"колонка object: объекта `{row.object}` нет в object.md",
                             fix=f"/project-deep-dive {self.lay.slug}")
            if problems:
                tadd("R-TX-005", "error", f"texts#{key}", f"строка {row.line}: " + "; ".join(problems))
            if key not in used:
                tadd("R-TX-006", "hint", f"texts#{key}", f"ключа `{key}` нет ни в одном дереве, form, tiles и "
                                                          "«Состояниях приложения»")

    def _screen_keys(self, screen, used):
        comp = composition(self.trees, screen)
        places = {self.trees.screens[screen].record.path}
        places |= {self.lay.blocks[b].path for b in comp["blocks"] if b in self.lay.blocks}
        shell = self.lay.shells.get(str(self.trees.screens[screen].record.fm.get("shell") or ""))
        if shell is not None:
            places.add(shell.path)
        keys = set()
        for key, us in used.items():
            for u in us:
                if u.parsed.record.path in places:
                    if u.parsed.kind == "screen" and u.parsed.slug != screen:
                        continue
                    keys.add(key)
        return keys


def check_layer(lay):
    """Находки проверок деревьев одной поверхности."""
    return Checker(lay).run().items


# ------------------------------------------------------------------ вывод

def dump(lay, trees=None):
    trees = trees or parse_layer(lay)

    def rec(p):
        d = {"status": p.record.status, "path": lay.rel(p.record.path)}
        return d

    out = {"project": lay.slug, "surface": lay.surface, "screens": {}, "blocks": {}, "shells": {}}
    for s, p in trees.screens.items():
        d = rec(p)
        d["shell"] = p.record.fm.get("shell")
        d["slot_fills"] = {k: v.as_dict() for k, v in p.fills.items()}
        d["states"] = {k: v.as_dict() for k, v in p.states.items()}
        d["blocks"] = composition(trees, s)["blocks"]
        out["screens"][s] = d
    for s, p in trees.blocks.items():
        d = rec(p)
        d["source"] = str(p.record.fm.get("source") or "screen")
        d["tree"] = {k: v.as_dict() for k, v in p.areas.items()}
        if p.states:
            d["states"] = {k: v.as_dict() for k, v in p.states.items()}
        out["blocks"][s] = d
    for s, p in trees.shells.items():
        d = rec(p)
        d["slots"] = p.record.fm.get("slots")
        d["tree"] = [n.as_dict() for n in p.nodes]
        d["main"] = p in main_shells(trees)
        out["shells"][s] = d
    out["ui_types"] = ui_types(trees, stable_only=False)
    out["ui_types_stable"] = ui_types(trees, stable_only=True)
    return out


def _print_tree(nodes, indent, out):
    for n in nodes:
        label = f"«{n.literal}»" if n.literal is not None else \
            (n.head or "?") + ("" if n.valid else "   ← не по грамматике")
        print(" " * indent + "- " + label, file=out)
        for k, v in n.struct.items():
            if k == "fill":
                for area, sub in v.items():
                    print(" " * (indent + 4) + f"fill.{area}:", file=out)
                    _print_tree(sub, indent + 6, out)
            else:
                print(" " * (indent + 4) + f"{k}: {json.dumps(v, ensure_ascii=False)}", file=out)
        _print_tree(n.children, indent + 4, out)


def show(lay, as_json=False, out=None):
    out = out or sys.stdout
    trees = parse_layer(lay)
    if as_json:
        print(json.dumps(dump(lay, trees), ensure_ascii=False, indent=1), file=out)
        return
    for title, group in (("экраны", trees.screens), ("блоки", trees.blocks), ("каркасы", trees.shells)):
        print(f"== {lay.surface}: {title} ({len(group)})", file=out)
        for slug, p in group.items():
            print(f"{p.kind} {slug} [{p.record.status or '—'}]", file=out)
            for name, fill in list(p.fills.items()) + list(p.areas.items()):
                if fill.kind == "block":
                    print(f"  {name}: block:{fill.block}", file=out)
                elif fill.kind == "empty":
                    print(f"  {name}: —", file=out)
                else:
                    print(f"  {name}:", file=out)
                    _print_tree(fill.nodes, 4, out)
            if p.nodes:
                _print_tree(p.nodes, 2, out)
            for key, sv in p.states.items():
                if sv.na is not None:
                    print(f"  states.{key}: не применимо: {sv.na}", file=out)
                else:
                    print(f"  states.{key}: {', '.join(sv.slots)}", file=out)


# ------------------------------------------------------------------ вызов

def layers_of(call):
    """Layer каждой поверхности вызова: названная или все поверхности кабинета проекта."""
    surfs = [call.surf] if call.surf else [s for s in call.surfaces if s.app]
    return [L.Layer(call.slug, s.slug, call.repo) for s in surfs]


def run(argv=None, prog="tree", description=None, commands=("check", "show"), check=check_layer, show_fn=show):
    """Общий вызов утилит, которые проверяют и показывают слой экранов (tree, states)."""
    ap = docpaths.parser(prog, description or __doc__, commands=commands, surface="optional",
                         accept=lambda s: s.app)
    call = docpaths.parse(ap, argv)
    if call.selftest:
        return None
    try:
        lays = layers_of(call)
        if not lays:
            print(f"{prog}: у проекта {call.slug} нет поверхностей кабинета (web рода app, admin, desktop, embed)",
                  file=sys.stderr)
            return F.EXIT_USAGE
        if call.command == "check":
            items = []
            for lay in lays:
                items += check(lay)
            F.print_findings(items, as_json=call.json)
            return F.exit_code(items)
        for lay in lays:
            show_fn(lay, as_json=call.json)
        return F.EXIT_OK
    except (F.ToolError, docpaths.DocPathError, RuntimeError, OSError) as e:
        print(f"{prog}: {e}", file=sys.stderr)
        return F.EXIT_USAGE


# ------------------------------------------------------------------ самопроверка

EXPECT_DEFECTS = [                                      # фикстура cabinet-defects: правила tree и их число
    ("R-STRUCT-020", "error", 1), ("R-STRUCT-021", "error", 2), ("R-SEM-014", "warning", 2),
    ("R-TX-001", "error", 1), ("R-TX-003", "error", 1)]


def selftest_grammar(check):
    """Грамматика на синтетических образцах (без файлов)."""
    iss = []
    n = parse_head("ui:Button level=primary action=create", "/0", iss)
    check("голова: префикс, тип, пары атрибутов", n.valid and n.ui_type == "Button" and
          n.attrs == {"level": "primary", "action": "create"} and not iss)
    iss = []
    n = parse_head("ui:Button level = primary", "/0", iss)
    check("голова с пробелами вокруг «=» — R-STRUCT-020", not n.valid and [i.rule for i in iss] == ["R-STRUCT-020"]
          and "пробелы" in iss[0].message)
    iss = []
    n = parse_head("Новое", "/0", iss)
    check("строка вне грамматики головы — литерал", n.literal == "Новое" and not iss)
    iss = []
    parse_head("widget:Foo", "/0", iss)
    check("префикс вне списка — R-STRUCT-020", [i.rule for i in iss] == ["R-STRUCT-020"])
    iss = []
    parse_head("layout:column", "/0", iss)
    check("layout: только row|stack|grid|layer", [i.rule for i in iss] == ["R-STRUCT-020"])
    iss = []
    n = parse_item({"ui:Table items=data:study": {"columns": [{"field": "data:study.name",
                                                                "label": "text:s.l.name.column-header"}],
                                                   "rows": 3}}, "/0", iss)
    check("структура: columns — ключ, rows — R-SEM-014", "columns" in n.struct and [i.rule for i in iss] ==
          ["R-SEM-014"])
    iss = []
    n = parse_item({"layout:grid": {"areas": [["a", "b"]], "fill": {"a": "ui:SearchInput",
                                                                    "b": ["block:list"]}}}, "/0", iss)
    check("сетка: fill — узел или список узлов", not iss and len(n.kids()) == 2)
    iss = []
    parse_item({"ui:Button": None}, "/0", iss)
    check("двоеточие без детей — R-STRUCT-020", [i.rule for i in iss] == ["R-STRUCT-020"])
    iss = []
    parse_item({"ui:A": [], "ui:B": []}, "/0", iss)
    check("узел из двух ключей — R-STRUCT-020", [i.rule for i in iss] == ["R-STRUCT-020"])
    iss = []
    n = parse_head("layout:stack - 'Пока пусто'", "/0", iss)
    check("склеенные дети — R-STRUCT-020 с подсказкой про двоеточие", not n.valid and "двоеточием" in iss[0].message)
    iss = []
    st = parse_states({"loading-initial": {"main": ["ui:Skeleton"]}, "partial-few": "не применимо: одна строка",
                       "success": "не применимо", "error-load": None, "timeout": "позже"}, "/states", iss)
    check("states: дельта, «не применимо», пустая секция и чужая строка",
          st["partial-few"].na == "одна строка" and st["success"].na == "" and st["error-load"].empty and
          [i.rule for i in iss] == ["R-STRUCT-020", "R-STRUCT-020"])
    iss = []
    f1 = parse_fill("block:studies-list", "/slot-fills/main", iss)
    f2 = parse_fill("—", "/slot-fills/detail", iss)
    f3 = parse_fill(["ui:Skeleton"], "/slot-fills/side", iss)
    check("слот: block, «—», дерево", (f1.kind, f1.block, f2.kind, f3.kind) == ("block", "studies-list", "empty",
                                                                             "tree") and not iss)


def _count(items, rule=None, severity=None):
    return sum(1 for f in items if (rule is None or f.rule == rule) and (severity is None or f.severity == severity))


def selftest_fixtures(check, run_check=check_layer, expect=None, tool="tree", extra=None):
    """Фикстуры кабинета: чистый слой — 0 error и 0 warning, слой дефектов — ровно ожидаемые находки."""
    import subprocess
    import tempfile
    kbpaths.use("tests")
    import fixture_project
    expect = EXPECT_DEFECTS if expect is None else expect
    with fixture_project.built("cabinet") as fx:
        lay = L.Layer(fx.slug, "office", fx.root)
        items = run_check(lay)
        bad = [f for f in items if f.severity in ("error", "warning")]
        check(f"{tool}: чистый слой фикстуры cabinet — 0 error, 0 warning"
              + (f" (есть: {'; '.join(f.rule + ' ' + f.ref + ' ' + f.message for f in bad[:4])})" if bad else ""),
              not bad)
        if extra:
            extra(check, fx, lay)
        script = HERE / f"{tool}.py"
        with tempfile.TemporaryDirectory(prefix="ddd-tree-cwd-") as cwd:
            r = subprocess.run([sys.executable, str(script), "check", fx.slug, "office", "--repo", str(fx.root),
                                "--json"], cwd=cwd, capture_output=True, text=True)
        try:
            lines = F.parse_lines(r.stdout)
        except ValueError:
            lines = None
        check(f"{tool} check --json из чужой рабочей папки с --repo — код 0, строки находок", r.returncode == 0 and
              lines is not None and not [f for f in lines if f.severity == "error"])
    with fixture_project.built("cabinet-defects") as fx:
        lay = L.Layer(fx.slug, "office", fx.root)
        items = run_check(lay)
        for rule, sev, n in expect:
            got = _count(items, rule, sev)
            check(f"{tool}: дефекты — {rule} {sev}: {got} из {n}", got == n)
        want = sum(n for _, s, n in expect)
        loud = [f for f in items if f.severity in ("error", "warning")]
        check(f"{tool}: дефекты — лишних error и warning нет ({len(loud)} из {want})"
              + ("" if len(loud) == want else ": " + "; ".join(f"{f.rule} {f.ref}" for f in loud
                                                                 if (f.rule, f.severity) not in
                                                                 {(r, s) for r, s, _ in expect})), len(loud) == want)
        return items


def _selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    selftest_grammar(check)

    def extra(check, fx, lay):
        comps = lay.components
        check("словарь: TopBar по имени Navbar из aka", comps.type_of("Navbar") == "TopBar")
        roles = L.text_roles_closed()
        check("роли текста: закрытый список ux 07/06 §7.2 и body", {"action", "column-header", "empty",
                                                                    "body"} <= roles and len(roles) >= 30)
        d = dump(lay)
        check("show: JSON — экраны, блоки, каркасы и типы ui", d["screens"] and d["blocks"] and d["shells"] and
              "Table" in d["ui_types"])
        check("ui_types stable: типы stable-экранов с блоками и каркасом", "Sidebar" in d["ui_types_stable"])
        # расширение проекта и токены ДС — на копии фикстуры
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory(prefix="ddd-tree-ext-") as td:
            root = Path(td) / "r"
            shutil.copytree(fx.root, root)
            proj = root / "docs" / "projects" / fx.slug
            (proj / "design").mkdir(exist_ok=True)
            (proj / "design" / "system.yaml").write_text(
                "example: true\nextensions:\n  - {id: Kanban, parts: [Column]}\n", encoding="utf-8")
            (proj / "design" / "system.tokens.json").write_text(json.dumps(
                {"space": {"$type": "dimension", "sm": {"$value": "8px"}, "md": {"$value": "16px"}}}),
                encoding="utf-8")
            blk = proj / "screens" / "office" / "blocks" / "requests-list" / "index.md"
            text = blk.read_text(encoding="utf-8")
            text = text.replace("    - ui:Pagination", "    - ui:Kanban.Column\n    - ui:Kanban.Lane", 1)
            blk.write_text(text.replace("layout:row gap=sm:", "layout:row gap=xl:", 1), encoding="utf-8")
            lay2 = L.Layer(fx.slug, "office", root)
            items = check_layer(lay2)
            ext = [f for f in items if f.rule == "R-STRUCT-021"]
            check("расширение карты решений — тип и части", len(ext) == 1 and "Lane" in ext[0].message)
            gaps = [f for f in items if f.rule == "R-SEM-014" and "space." in f.message]
            check("gap сверяется с токенами space.* ДС: gap=xl — находка, gap=md и gap=sm — нет",
                  len(gaps) == 1 and "space.xl" in gaps[0].message)
        # остальные правила дерева и реестра — синтетикой на копии чистого слоя
        with tempfile.TemporaryDirectory(prefix="ddd-tree-syn-") as td:
            root = Path(td) / "r"
            shutil.copytree(fx.root, root)
            base = root / "docs" / "projects" / fx.slug / "screens" / "office"

            def edit(rel, old, new):
                p = base / rel
                text = p.read_text(encoding="utf-8")
                assert old in text, (rel, old)
                p.write_text(text.replace(old, new, 1), encoding="utf-8")

            edit("texts.md", "| `requests.list.retry.action` | `action` |", "| `requests.list.retry.action` | `link` |")
            edit("texts.md", "| `requests.card.retry.action` | `action` | Повторить | 16 | — | — | — | повтор загрузки "
                             "карточки | `checked` |",
                 "| `requests.card.retry.action` | `action` | Повторить | 16 | — | — | — | повтор загрузки карточки | "
                 "`assumed` |")
            edit("texts.md", "| `system.not-found.to-requests.link` | `link` | К заявкам | 24 |",
                 "| `system.not-found.to-requests.link` | `hyperlink` | К заявкам | — |")
            edit("blocks/plan-tile/index.md", "tree:\n  block-body:\n    - ui:KpiTile value=data:plan.done\n",
                 "tree:\n  block-header:\n    - ui:KpiTile value=data:plan.done\n")
            edit("screens/request-new/index.md", "  main: block:request-form\n  overlay: —\n",
                 "  main: —\n  overlay:\n    - ui:Spinner\n  side: block:request-form\n")
            edit("screens/not-found/index.md", "        - ui:Link:\n",
                 "        - block:no-such-block\n        - ui:Link:\n")
            edit("blocks/request-details/index.md", "ui:DescriptionList items=data:request",
                 "ui:DescriptionList items=data:order.total value=data:request.price")
            edit("blocks/requests-list/index.md", "ui:Button level=primary action=create:",
                 "ui:Button level=primary action=publish:")
            edit("shells/app-shell/index.md", "## Состояния приложения", "## Прочее")
            got = {(f.rule, f.severity) for f in check_layer(L.Layer(fx.slug, "office", root))}
            want = {("R-TX-002", "error"), ("R-TX-004", "error"), ("R-TX-005", "error"), ("R-STRUCT-010", "error"),
                    ("R-STRUCT-011", "error"), ("R-STRUCT-012", "error"), ("R-STRUCT-013", "error"),
                    ("R-STRUCT-001", "error"), ("R-STRUCT-002", "error"), ("R-STRUCT-023", "error"),
                    ("R-STRUCT-025", "error")}
            check("синтетика: R-TX-002, 004, 005, R-STRUCT-001, 002, 010, 011, 012, 013, 023, 025 срабатывают"
                  + (f" (нет: {sorted(want - got)})" if want - got else ""), want <= got)

    selftest_fixtures(check, extra=extra)
    print("tree selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return _selftest()
    return run(argv)


if __name__ == "__main__":
    sys.exit(main())
