#!/usr/bin/env python3
"""layer — чтение файлов проекта для утилит `scripts/project/`: слой экранов поверхности, interface той же поверхности,
продуктовый слой, карта решений и токены ДС, словарь компонентов. Одна копия разбора для всех утилит раздела.

Формы — по канону `docs/projects/_template/`: у записей экранов (`screens/<surface>/{screens,blocks,shells,flows}/
<slug>/index.md`) — frontmatter YAML и блоки ```yaml``` в теле; `map.md` и `texts.md` — свод и реестр таблицами;
interface и продукт — таблицы md (ячейки: `` `slug` ``, `` [`a`, `b`] ``, `—`); паспорта возможностей — разделы
`### <slug>` с блоком YAML; `design/system.yaml` — расширения словаря (`extensions`); `design/system.tokens.json` —
токены DTCG (шкала `space.*`).

    lay = layer.Layer("otves-office", "office", repo=None)   # корень данных — docpaths: --repo → DDD_REPO → скилл
    lay.screens["requests-list"].fm["route"]                 # записи экранов: kind, slug, path, fm, data, status
    lay.texts.rows["requests.list.create.action"].status     # реестр текстов
    lay.interface.table("situation")                         # строки таблицы interface по slug
    lay.product.attributes("request")                        # атрибуты объекта глоссария
    lay.components.type_of("Navbar")                         # словарь компонентов: тип по имени из aka

Файлы читаются лениво, при первом обращении. Ошибка разбора файла — не исключение: запись несёт `error`, её
показывает утилита находкой своего правила.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402

KIND_DIRS = {"screen": "screens", "block": "blocks", "shell": "shells", "flow": "flows"}
DASH = ("—", "–", "-", "")
FENCE_OPEN = re.compile(r"^```ya?ml\s*$")
FENCE_ANY = re.compile(r"^```")
PLACEHOLDER = re.compile(r"^<[^>]*>$")


def _yaml():
    try:
        import yaml
    except ImportError as e:                                  # окружение без PyYAML — код 2 у утилиты
        raise RuntimeError("нужен PyYAML: $DDD_HOME/venv/bin/python или pip install pyyaml") from e
    return yaml


# ------------------------------------------------------------------ ячейки таблиц md

def is_empty(value):
    """Пусто: None, «—», «-», пустая строка, заготовка `<…>`."""
    if value is None:
        return True
    s = str(value).strip().strip("`").strip()
    return s in DASH or bool(PLACEHOLDER.match(s))


def cell(value):
    """`web` → web; «—», пусто и заготовка `<…>` → None."""
    v = (value or "").strip()
    if v.startswith("``") and v.endswith("``") and len(v) > 4:
        v = v[2:-2].strip()
    m = re.fullmatch(r"`([^`]*)`", v)
    if m:
        v = m.group(1).strip()
    return None if is_empty(v) else v


def refs(value):
    """`` [`a`, `b`] ``, `[a, b]`, `a` → ['a', 'b']; «—» → []."""
    v = (value or "").strip()
    if v.startswith("``") and v.endswith("``") and len(v) > 4:
        v = v[2:-2].strip()
    if is_empty(v):
        return []
    found = re.findall(r"`([^`]+)`", v)
    if found:
        return [x.strip() for x in found if x.strip() and not is_empty(x)]
    v = v.strip("[] ")
    return [x.strip().strip("`") for x in v.split(",") if x.strip() and not is_empty(x.strip())]


def split_row(line):
    s = line.strip()
    if not (s.startswith("|") and s.endswith("|") and len(s) > 1):
        return None
    parts, cur, tick = [], [], False
    body = s[1:-1]
    i = 0
    while i < len(body):
        ch = body[i]
        if ch == "\\" and i + 1 < len(body) and body[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if ch == "`":
            tick = not tick
        if ch == "|" and not tick:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append("".join(cur).strip())
    return parts


@dataclass
class Row:
    line: int                                           # номер строки в файле (с 1)
    cells: dict                                         # колонка → текст ячейки как есть
    raw: str = ""

    def get(self, col, default=None):
        return self.cells.get(col, default)

    def value(self, col):
        return cell(self.cells.get(col))

    def refs(self, col):
        return refs(self.cells.get(col))


@dataclass
class Table:
    columns: list
    rows: list
    line: int                                           # строка заголовка таблицы
    section: str | None = None                          # заголовок ## или ###, под которым таблица


def tables(text, first_line=1):
    """Все таблицы md текста по порядку (с разделом, под которым стоят)."""
    out, cur, section = [], None, None
    lines = str(text).splitlines()
    in_fence = False
    for i, line in enumerate(lines):
        no = first_line + i
        if FENCE_ANY.match(line.strip()):
            in_fence = not in_fence
            cur = None
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{2,4})\s+(.*?)\s*$", line)
        if m:
            section = m.group(2)
            cur = None
            continue
        cells = split_row(line)
        if cells is None:
            cur = None
            continue
        if cur is None:
            nxt = split_row(lines[i + 1]) if i + 1 < len(lines) else None
            if nxt and all(re.fullmatch(r":?-{2,}:?", c) for c in nxt if c):
                cur = Table(columns=[c.strip().strip("`").strip() for c in cells], rows=[], line=no, section=section)
                out.append(cur)
            continue
        if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
            continue
        row = {c: (cells[j] if j < len(cells) else "") for j, c in enumerate(cur.columns)}
        cur.rows.append(Row(line=no, cells=row, raw=line))
    return out


def find_table(text, need, section=None, first_line=1):
    """Первая таблица, в заголовке которой есть все колонки need (и раздел section, если задан)."""
    for t in tables(text, first_line):
        if set(need) <= set(t.columns) and (section is None or (t.section or "").strip() == section):
            return t
    return None


def sections(text, level=2):
    """Разделы `## …` текста → [(заголовок, номер строки заголовка, текст раздела)]."""
    out = []
    lines = str(text).splitlines()
    marks = []
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_ANY.match(line.strip()):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{%d})\s+(.*?)\s*$" % level, line)
        if m:
            marks.append((i, m.group(2)))
    for k, (i, title) in enumerate(marks):
        end = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
        out.append((title, i + 1, "\n".join(lines[i + 1:end])))
    return out


def section(text, title, level=2):
    for t, line, body in sections(text, level):
        if t.strip() == title:
            return line, body
    return None, None


# ------------------------------------------------------------------ markdown с frontmatter и блоками YAML

@dataclass
class YamlBlock:
    text: str
    line: int                                           # номер первой строки содержимого блока в файле
    data: object = None
    error: str | None = None


class Md:
    """Файл md: frontmatter, тело, блоки ```yaml```, разделы и таблицы."""

    def __init__(self, path):
        self.path = Path(path)
        self.text = self.path.read_text(encoding="utf-8")
        self.fm = None
        self.fm_error = None
        self.fm_text = None
        self.body = self.text
        self.body_line = 1
        m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(\r?\n|$)", self.text, re.S)
        if m:
            self.fm_text = m.group(1)
            self.body = self.text[m.end():]
            self.body_line = self.text[:m.end()].count("\n") + 1
            try:
                data = _yaml().safe_load(self.fm_text)
                if data is None:
                    data = {}
                if isinstance(data, dict):
                    self.fm = data
                else:
                    self.fm_error = "frontmatter — не словарь YAML"
            except Exception as e:                      # noqa: BLE001 — yaml.YAMLError и ошибки конструктора
                self.fm_error = "frontmatter не разбирается как YAML: " + _yaml_err(e)

    @cached_property
    def yaml_blocks(self):
        out = []
        lines = self.body.splitlines()
        i = 0
        while i < len(lines):
            if FENCE_OPEN.match(lines[i].strip()) and not lines[i].startswith((" ", "\t")):
                j = i + 1
                while j < len(lines) and lines[j].strip() != "```":
                    j += 1
                text = "\n".join(lines[i + 1:j]) + "\n"
                blk = YamlBlock(text=text, line=self.body_line + i + 1)
                try:
                    blk.data = _yaml().safe_load(text)
                except Exception as e:                  # noqa: BLE001
                    blk.error = _yaml_err(e, blk.line)
                out.append(blk)
                i = j + 1
                continue
            i += 1
        return out

    def sections(self, level=2):
        return sections(self.body, level)

    def section(self, title, level=2):
        return section(self.body, title, level)

    def tables(self):
        return tables(self.body, self.body_line)

    def table(self, need, section_title=None):
        return find_table(self.body, need, section_title, self.body_line)


def _yaml_err(e, first_line=None):
    mark = getattr(e, "problem_mark", None) or getattr(e, "context_mark", None)
    head = str(getattr(e, "problem", None) or e).splitlines()[0]
    if mark is not None and first_line is not None:
        return f"{head} (стр. {first_line + mark.line})"
    if mark is not None:
        return f"{head} (стр. {mark.line + 1} блока)"
    return head


# ------------------------------------------------------------------ записи слоя экранов

@dataclass
class Record:
    """Запись слоя экранов: screen · block · shell · flow."""
    kind: str
    slug: str                                           # имя папки
    path: Path
    md: Md | None = None
    error: str | None = None                            # файл не читается

    @property
    def fm(self):
        return (self.md.fm if self.md else None) or {}

    @property
    def status(self):
        s = self.fm.get("status")
        return str(s).strip() if s is not None else None

    @property
    def stable(self):
        return self.status == "stable"

    @cached_property
    def data(self):
        """Верхние ключи всех блоков YAML тела (tree, slot-fills, states …) — поздний блок перекрывает ранний."""
        out = {}
        for blk in self.md.yaml_blocks if self.md else []:
            if isinstance(blk.data, dict):
                out.update(blk.data)
        return out

    def block_of(self, key):
        """Блок YAML, в котором лежит верхний ключ key (для номеров строк)."""
        for blk in reversed(self.md.yaml_blocks if self.md else []):
            if isinstance(blk.data, dict) and key in blk.data:
                return blk
        return None


def load_records(folder, kind):
    out = {}
    d = Path(folder)
    if not d.is_dir():
        return out
    for sub in sorted(p for p in d.iterdir() if p.is_dir()):
        f = sub / "index.md"
        if not f.is_file():
            continue
        try:
            out[sub.name] = Record(kind=kind, slug=sub.name, path=f, md=Md(f))
        except (OSError, UnicodeDecodeError) as e:
            out[sub.name] = Record(kind=kind, slug=sub.name, path=f, error=str(e))
    return out


# ------------------------------------------------------------------ реестр текстов

TEXT_COLUMNS = ("key", "role", "text", "maxlen", "action", "object", "group", "context", "status")


@dataclass
class TextRow:
    key: str
    role: str | None
    text: str
    maxlen: str | None
    action: str | None
    object: str | None
    group: str | None
    context: str | None
    status: str | None
    line: int
    locales: dict = field(default_factory=dict)


class Texts:
    """Реестр `texts.md` поверхности: строки по ключу; порядок колонок — для проверки формы."""

    def __init__(self, path):
        self.path = Path(path)
        self.exists = self.path.is_file()
        self.md = Md(self.path) if self.exists else None
        self.table = self.md.table(("key",)) if self.md else None
        self.rows = {}
        self.duplicates = []
        for r in self.table.rows if self.table else []:
            key = cell(r.get("key"))
            if not key:
                continue
            row = TextRow(key=key, role=cell(r.get("role")), text=(r.get("text") or "").strip(),
                          maxlen=cell(r.get("maxlen")), action=cell(r.get("action")), object=cell(r.get("object")),
                          group=cell(r.get("group")), context=cell(r.get("context")), status=cell(r.get("status")),
                          line=r.line, locales={c: r.get(c) for c in r.cells if c.startswith("text-")})
            if key in self.rows:
                self.duplicates.append(row)
            else:
                self.rows[key] = row


# ------------------------------------------------------------------ interface поверхности

INTERFACE_FILES = ("who", "stage", "situation", "zone", "block", "ux-substrate", "data-items")


class Interface:
    """Таблицы interface поверхности: строки по slug."""

    def __init__(self, folder):
        self.folder = Path(folder)
        self._cache = {}

    def path(self, name):
        return self.folder / f"{name}.md"

    def table(self, name):
        """{slug: Row} таблицы файла name (who, zone, situation, block, ux-substrate, data-items, stage)."""
        if name not in self._cache:
            rows = {}
            p = self.path(name)
            if p.is_file():
                t = Md(p).table(("slug",))
                for r in t.rows if t else []:
                    s = cell(r.get("slug"))
                    if s and docpaths.SLUG.match(s):
                        rows[s] = r
            self._cache[name] = rows
        return self._cache[name]

    def exists(self, name):
        return self.path(name).is_file()

    def scenario_text(self):
        p = self.path("scenario")
        return p.read_text(encoding="utf-8") if p.is_file() else ""


# ------------------------------------------------------------------ продуктовый слой

class Product:
    """Продуктовый слой проекта: объекты и атрибуты, действия, возможности поверхности с паспортами, постура, vision."""

    def __init__(self, slug, surface, repo):
        self.slug, self.surface, self.repo = slug, surface, repo

    def _md(self, *parts):
        p = docpaths.project(self.slug, *parts, repo=self.repo)
        return Md(p) if p.is_file() else None

    @cached_property
    def objects(self):
        md = self._md("object.md")
        t = md.table(("slug", "purpose")) if md else None
        return {cell(r.get("slug")): r for r in (t.rows if t else []) if cell(r.get("slug"))
                and docpaths.SLUG.match(cell(r.get("slug")))}

    @cached_property
    def _attributes(self):
        md = self._md("object.md")
        t = md.table(("object", "slug", "type")) if md else None
        out = {}
        for r in t.rows if t else []:
            o, a = cell(r.get("object")), cell(r.get("slug"))
            if o and a and not PLACEHOLDER.match(o):
                out.setdefault(o, {})[a] = r
        return out

    def attributes(self, obj):
        return self._attributes.get(obj, {})

    @cached_property
    def has_objects(self):
        return docpaths.project(self.slug, "object.md", repo=self.repo).is_file()

    @cached_property
    def actions(self):
        md = self._md("action.md")
        t = md.table(("slug", "verb")) if md else None
        return {cell(r.get("slug")): r for r in (t.rows if t else []) if cell(r.get("slug"))
                and docpaths.SLUG.match(cell(r.get("slug")))}

    @cached_property
    def has_actions(self):
        return docpaths.project(self.slug, "action.md", repo=self.repo).is_file()

    @cached_property
    def _capability_md(self):
        p = docpaths.layer(self.slug, "capability", self.surface, self.repo)
        return Md(p) if p.is_file() else None

    @cached_property
    def capabilities(self):
        md = self._capability_md
        t = md.table(("slug", "priority")) if md else None
        return {cell(r.get("slug")): r for r in (t.rows if t else []) if cell(r.get("slug"))
                and docpaths.SLUG.match(cell(r.get("slug")))}

    @cached_property
    def passports(self):
        """{slug возможности: словарь паспорта} из раздела «Паспорта»."""
        md = self._capability_md
        out = {}
        if not md:
            return out
        _, body = md.section("Паспорта")
        for title, _, text in sections(body or "", level=3):
            slug = title.strip().strip("`")
            m = re.search(r"^```ya?ml\s*\n(.*?)^```", text, re.S | re.M)
            if not m:
                continue
            try:
                data = _yaml().safe_load(m.group(1))
            except Exception:                           # noqa: BLE001 — битый паспорт читается как пустой
                data = None
            if isinstance(data, dict):
                out[slug] = data
        return out

    @cached_property
    def users(self):
        md = self._md("user.md")
        t = md.table(("slug", "jobs")) if md else None
        return {cell(r.get("slug")): r for r in (t.rows if t else []) if cell(r.get("slug"))}

    @cached_property
    def postures(self):
        """[(user, surface|None, Row)] таблицы «Постура»."""
        md = self._md("user.md")
        t = md.table(("user", "posture", "density")) if md else None
        return [(cell(r.get("user")), cell(r.get("surface")), r) for r in (t.rows if t else []) if cell(r.get("user"))]

    @cached_property
    def vision(self):
        return self._md("vision.md")


# ------------------------------------------------------------------ слой дизайна: расширения словаря и токены

class Design:
    def __init__(self, slug, repo):
        self.slug, self.repo = slug, repo

    @cached_property
    def system_path(self):
        return docpaths.design(self.slug, "system", repo=self.repo)

    @cached_property
    def extensions(self):
        """{id: запись расширения} из `design/system.yaml#extensions`; нет файла — {}."""
        p = self.system_path
        if not p.is_file():
            return {}
        try:
            data = _yaml().safe_load(p.read_text(encoding="utf-8")) or {}
        except Exception:                               # noqa: BLE001 — битую карту решений проверяет её аудит
            return {}
        out = {}
        for e in data.get("extensions") or [] if isinstance(data, dict) else []:
            if isinstance(e, dict) and isinstance(e.get("id"), str) and not PLACEHOLDER.match(e["id"]):
                out[e["id"]] = e
        return out

    @cached_property
    def tokens_path(self):
        return docpaths.design(self.slug, "tokens", repo=self.repo)

    @cached_property
    def space_tokens(self):
        """Имена токенов группы `space` из `design/system.tokens.json` (`md`, `inset.card` …); нет файла — None."""
        p = self.tokens_path
        if not p.is_file():
            return None
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except ValueError:
            return None
        space = data.get("space") if isinstance(data, dict) else None
        names = set()

        def walk(node, prefix):
            if not isinstance(node, dict):
                return
            if "$value" in node:
                names.add(".".join(prefix))
                return
            for k, v in node.items():
                if not k.startswith("$"):
                    walk(v, prefix + [k])

        walk(space, [])
        return names


# ------------------------------------------------------------------ словарь компонентов

class Components:
    """kb/common/components.yaml: типы, части, имена из aka, роли текста частей, строки матрицы состояний."""

    def __init__(self, path=None):
        self.path = Path(path) if path else kbpaths.kb(None, "common", "components.yaml")
        data = _yaml().safe_load(self.path.read_text(encoding="utf-8"))
        self.types = data.get("types") or {}
        self.text_roles = data.get("text_roles") or {}
        self.aka = {}
        for t, spec in self.types.items():
            for name in (spec or {}).get("aka") or []:
                self.aka.setdefault(str(name), t)

    def parts(self, t):
        return list((self.types.get(t) or {}).get("parts") or [])

    def type_of(self, name):
        """Тип словаря по имени из aka (или None)."""
        return self.aka.get(name)

    def roles(self, t, part=None):
        key = f"{t}.{part}" if part else t
        return list(self.text_roles.get(key) or [])

    def screen_states(self, t):
        """Ключ строки матрицы состояний экрана у типа (`list-table` …) или None."""
        ref = (self.types.get(t) or {}).get("screen_states")
        return str(ref).split("#", 1)[1] if ref and "#" in str(ref) else None


_COMPONENTS = None


def components():
    global _COMPONENTS
    if _COMPONENTS is None:
        _COMPONENTS = Components()
    return _COMPONENTS


_ROLES = None


def text_roles_closed():
    """Закрытый список ролей текста ux 07/06 §7.2 и `body` — читается из базы."""
    global _ROLES
    if _ROLES is None:
        p = kbpaths.kb("ux", "07-ux-writing", "06-banned-words-and-patterns.md")
        roles = set()
        if p.is_file():
            _, body = section(p.read_text(encoding="utf-8"), "7.2. Роли узлов", level=3)
            for line in (body or "").splitlines():
                s = line.strip()
                if s.startswith("`") and "·" in s:
                    roles.update(re.findall(r"`([a-z-]+)`", s))
        roles.add("body")
        for vals in components().text_roles.values():
            roles.update(vals)
        _ROLES = roles
    return _ROLES


# ------------------------------------------------------------------ слой поверхности

class Layer:
    """Слой экранов одной поверхности и всё, что читают его утилиты."""

    def __init__(self, slug, surface, repo=None):
        self.slug = slug
        self.surface = surface
        self.repo = docpaths.root(repo)
        self.surf = docpaths.surface(slug, surface, self.repo)
        self.folder = docpaths.layer(slug, "screens", surface, self.repo)
        self.product = Product(slug, surface, self.repo)
        self.design = Design(slug, self.repo)
        self.interface = Interface(docpaths.layer(slug, "interface", surface, self.repo))

    def rel(self, path):
        return docpaths.rel(path, self.repo)

    @cached_property
    def screens(self):
        return load_records(self.folder / "screens", "screen")

    @cached_property
    def blocks(self):
        return load_records(self.folder / "blocks", "block")

    @cached_property
    def shells(self):
        return load_records(self.folder / "shells", "shell")

    @cached_property
    def flows(self):
        return load_records(self.folder / "flows", "flow")

    def records(self, kinds=("screen", "block", "shell", "flow")):
        for kind in kinds:
            yield from getattr(self, KIND_DIRS[kind]).values()

    @cached_property
    def map_path(self):
        return docpaths.screens(self.slug, self.surface, "map", repo=self.repo)

    @cached_property
    def map(self):
        return Md(self.map_path) if self.map_path.is_file() else None

    @cached_property
    def texts_path(self):
        return docpaths.screens(self.slug, self.surface, "texts", repo=self.repo)

    @cached_property
    def texts(self):
        return Texts(self.texts_path)

    @property
    def components(self):
        return components()


def app_surfaces(slug, repo=None):
    """Поверхности проекта с маршрутом кабинета (экраны есть у web рода app, admin, desktop, embed)."""
    return [s for s in docpaths.surfaces(slug, repo) if s.app]


def describe(lay):
    """Сводка слоя поверхности: записи со статусами, реестр, свод, interface и продукт — что прочитано."""
    return {"project": lay.slug, "surface": lay.surface, "folder": lay.rel(lay.folder),
            "records": {k: {s: r.status for s, r in getattr(lay, d).items()} for k, d in KIND_DIRS.items()},
            "map": lay.rel(lay.map_path) if lay.map is not None else None,
            "texts": len(lay.texts.rows) if lay.texts.exists else None,
            "interface": {n: len(lay.interface.table(n)) for n in INTERFACE_FILES if lay.interface.exists(n)},
            "product": {"objects": sorted(lay.product.objects), "actions": sorted(lay.product.actions),
                        "capabilities": sorted(lay.product.capabilities), "passports": sorted(lay.product.passports)},
            "design": {"extensions": sorted(lay.design.extensions),
                       "space_tokens": None if lay.design.space_tokens is None else sorted(lay.design.space_tokens)}}


def _selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    check("ячейки: `` [`a`, `b`] ``, [a, b], «—»", refs("`` [`a`, `b`] ``") == ["a", "b"] and refs("[a, b]") ==
          ["a", "b"] and refs("—") == [] and cell("`x`") == "x" and cell("<slug>") is None)
    check("строка таблицы: | внутри кода не делит ячейку", split_row("| `a|b` | c |") == ["`a|b`", "c"])
    t = tables("## Раздел\n\n| k | v |\n|---|---|\n| `a` | 1 |\n")[0]
    check("таблица: колонки, строки, раздел", t.columns == ["k", "v"] and t.rows[0].value("k") == "a" and
          t.section == "Раздел")
    comps = components()
    check("словарь компонентов: 65 типов, aka → тип, роли частей", len(comps.types) >= 60 and
          comps.type_of("Dialog") == "Modal" and comps.roles("Table", "Header") == ["column-header"])
    check("роли текста ux 07/06 §7.2 читаются из базы",
          {"title", "empty", "column-header", "body"} <= text_roles_closed())
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("cabinet") as fx:
        lay = Layer(fx.slug, "office", fx.root)
        d = describe(lay)
        check("слой кабинета: 5 экранов, 4 блока, каркас, свод и реестр", len(d["records"]["screen"]) == 5 and
              len(d["records"]["block"]) == 4 and d["map"] and d["texts"] and d["texts"] > 40)
        check("interface и продукт: ситуации, зоны, объекты, действия, паспорта",
              d["interface"].get("situation") == 5 and "request" in d["product"]["objects"] and
              "schedule-visit" in d["product"]["passports"])
        check("атрибуты объекта и постура", "visit-date" in lay.product.attributes("request") and
              any(u == "manager" for u, _, _ in lay.product.postures))
        check("frontmatter и блоки YAML тела", lay.screens["request-card"].fm["params"] == {"id": "request"} and
              "states" in lay.screens["request-card"].data)
    print("layer selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", nargs="?", help="slug проекта")
    ap.add_argument("surface", nargs="?", help="slug поверхности кабинета")
    ap.add_argument("--repo", metavar="DIR", help="корень данных (по умолчанию DDD_REPO или репозиторий скилла)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true", help="самопроверка на фикстуре cabinet, без сети")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if not (a.slug and a.surface):
        ap.print_help()
        return 2
    try:
        d = describe(Layer(a.slug, a.surface, a.repo))
    except (docpaths.DocPathError, RuntimeError, OSError) as e:
        print(f"layer: {e}", file=sys.stderr)
        return 2
    print(json.dumps(d, ensure_ascii=False, indent=None if a.json else 1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
