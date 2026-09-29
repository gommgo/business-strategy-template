#!/usr/bin/env python3
"""demo_data — производный демо-набор поверхности кабинета для входа холста: записи объектов глоссария, наборы
коллекций и крайние случаи значений. Каждая запись, каждый набор и документ целиком — `example: true`: макет на
демо-данных допустим, публикация — нет. Набор только производный: авторский файл фикстур стал бы вторым источником
данных продукта (канон — `docs/projects/_template/screens/README.md`, «Что слой отдаёт макету»).

Источники:
  object.md                      объекты (имя, статусы, синонимы, examples) и атрибуты (ранг, тип, обязательность,
                                 length — мин / тип / макс, values)
  interface/<surface>/data-items.md   датум → объект (колонка object)
  screens/<surface>/             какие датумы на поверхности; коллекции — ui:Table · List · TreeView и ui:Card items=
                                 в деревьях блоков и экранов; объём — collection.volume блока {typical, max}
  screens/<surface>/texts.md     самая длинная строка каждой роли на каждом языке реестра
  scripts/project/data/demo.yaml нормы с адресом базы: окно записей, «мало», объёмы без volume, классы крайних случаев

Значения детерминированы: одинаковый вход и зерно — тот же JSON байт в байт. Случай — хэш от зерна, объекта, записи
и атрибута, а не генератор с состоянием: новый атрибут не сдвигает значения соседних. Узнающий атрибут (text с
наименьшим рангом 1–3) — ведущая часть examples («З-0412 — Сормово» → «З-0412»), дальше — те же образцы с другими
цифрами; прочий text — образец по имени атрибута (телефон, почта, ссылка) или видимая подпись «<имя атрибута> <n>»
со словами объекта до длины из length; number и money — масштаб чисел из examples; enum — из values, каждое значение
хоть раз; date и datetime — вокруг опорной даты; ref — записи целевого объекта. Недостающее — генерацией по типу;
пробел источника — в разделе gaps документа и находкой check.

Документ (JSON):
  example, demo_data_version, note, project, surface, seed, anchor, window, sources, norms
  objects.<object>    example, name, description, aliases, statuses [{slug, name}], examples, attributes,
                      records — записи набора (`_id` `<object>-<n>`, у каждой example: true);
                      edge_cases — записи крайних случаев (`_case`, `_decide`, `_source`);
                      not_applicable — классы без атрибутов нужного типа, с причиной
  collections.<id>    id — slug блока или `<экран>#<указатель узла>`: example, kind (block · screen), object, item,
                      screens, volume, counts_from, sets.{empty, few, typical, max} — example, count, states
                      (ключи состояний экрана, которым набор нужен), records (`_id` записей объекта, не больше окна)
  localization        самая длинная строка роли реестра текстов: role, key, column, text, length, maxlen
  gaps                пробелы источников: rule, severity, path, message

    demo_data build <slug> <surface> [--repo DIR] [--seed S] [--anchor ГГГГ-ММ-ДД] [--out DIR] [--json]
    demo_data check <slug> [<surface>] [--repo DIR] [--json]
    demo_data --selftest

`build` печатает JSON набора; `--out DIR` пишет DIR/demo-data.json и печатает путь (`--json` — сводку JSON). В
репозиторий проекта утилита не пишет: вход холста собирает `canvas_input`. `check` — пробелы источников находками
(модуль findings), ничего не пишет; без <surface> — все поверхности кабинета. Из Python: `build(Layer, seed=None,
anchor=None)` → документ, `dumps(doc)` → текст JSON, `gaps(Layer)` → находки.

Правила находок (`.claude/skills/design-audit/references/rules.md`):
  R-MAT-011   пункт PRE-14 не заполнен: у коллекции нет collection.volume или он не {typical, max} целыми
              числами (typical ≤ max) — набор берёт объёмы ux 13/04 §12; доклад, закрывает аналитик     warning
  R-DEBT-002  заглушки набора: у объекта поверхности пусто examples, нет атрибутов; у text нет length, у enum —
              values; тип атрибута вне перечня; ref в объект, которого нет; коллекция без объекта глоссария  hint
Код выхода: 0 — нет error, 1 — есть error, 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
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
import states as S  # noqa: E402

DATA = kbpaths.data("project", "demo.yaml")
NORMS_REF = "scripts/project/data/demo.yaml"
VERSION = 1
BASE_TYPES = ("text", "number", "money", "date", "datetime", "enum", "bool", "file")
NUMERIC = ("number", "money")
DATES = ("date", "datetime")
DATA_REF = re.compile(r"data:([a-z0-9]+(?:-[a-z0-9]+)*)")
NUM = re.compile(r"\d+(?:[.,]\d+)?")
WORD = re.compile(r"[A-Za-zА-Яа-яЁё]{3,}")
SET_STATES = {"empty": ["empty-first-run", "empty-filtered"], "few": ["partial-few"], "typical": [],
              "max": ["overflow-many"]}
NA_WHY = {"text": "нет атрибутов text без образца по имени", "optional": "все атрибуты обязательны",
          "number": "нет атрибутов number и money", "date": "нет атрибутов date и datetime",
          "datetime": "нет атрибутов datetime", "ref": "нет связей — атрибутов ref:<object>",
          "ref-many": "нет атрибутов ref:<object>[]", "ident": "нет узнающего атрибута text рангов 1–3",
          "file": "нет атрибутов file"}

_NORMS = None


def norms():
    """Нормы и параметры набора — `scripts/project/data/demo.yaml`."""
    global _NORMS
    if _NORMS is None:
        try:
            data = L._yaml().safe_load(DATA.read_text(encoding="utf-8")) or {}
        except Exception as e:                          # noqa: BLE001 — битые данные утилиты — ошибка окружения
            raise F.ToolError(f"{DATA}: не читается — {e}") from e
        need = ("window", "few", "fallback", "relations_many", "large_number", "exotic", "dates", "params", "cases")
        miss = [k for k in need if not isinstance(data, dict) or k not in data]
        if miss:
            raise F.ToolError(f"{DATA}: нет ключей {', '.join(miss)}")
        _NORMS = data
    return _NORMS


def _u(*keys):
    """Случай в [0, 1) — хэш ключей: детерминированно на любой версии Python."""
    h = hashlib.sha256("\x1f".join(str(k) for k in keys).encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") / 2.0 ** 64


# ------------------------------------------------------------------ глоссарий объектов

@dataclass
class Attr:
    obj: str
    slug: str
    name: str
    rank: int
    type: str                                           # как в файле: text, enum[], ref:request[] …
    base: str                                           # text · number · … · ref; «?» — тип вне перечня формы
    many: bool
    target: str | None
    required: bool
    length: tuple | None                                # (мин, тип, макс)
    values: list
    line: int


@dataclass
class Obj:
    slug: str
    name: str
    description: str
    purpose: str
    examples: list
    statuses: list                                      # [(slug, имя)]
    aliases: list
    status: str | None
    line: int
    attrs: list = field(default_factory=list)


def _type(raw):
    t = (L.cell(raw) or "").strip()
    many = t.endswith("[]")
    core = t[:-2] if many else t
    if core.startswith("ref:"):
        return t, "ref", many, core[4:].strip() or None
    return t, core if core in BASE_TYPES else "?", many, None


def _length(raw):
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*/\s*(\d+)", raw or "")
    return tuple(int(x) for x in m.groups()) if m else None


def _list(raw):
    v = L.cell(raw)
    return [x.strip() for x in v.split(",") if x.strip()] if v else []


def _examples(raw):
    """Экземпляры examples через «;»; пометка в скобках в конце экземпляра — не его часть."""
    v = (raw or "").strip()
    if L.is_empty(v):
        return []
    out = []
    for part in v.split(";"):
        s = re.sub(r"\s*\([^()]*\)\s*$", "", part.strip()).strip()
        if s and not L.is_empty(s):
            out.append(s)
    return out


def _statuses(raw):
    v = (raw or "").strip()
    if v.startswith("``") and v.endswith("``"):
        v = v[2:-2]
    out = []
    for part in re.split(r"\s*·\s*", v):
        m = re.match(r"`([^`]+)`\s*[—–-]\s*(.+)$", part.strip())
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
    return out


def objects(lay):
    """{slug: Obj} глоссария в порядке object.md; атрибуты — по рангу."""
    out = {}
    for slug, r in lay.product.objects.items():
        o = Obj(slug=slug, name=(r.get("name") or "").strip(), description=(r.get("description") or "").strip(),
                purpose=(r.get("purpose") or "").strip(), examples=_examples(r.get("examples")),
                statuses=_statuses(r.get("statuses")), aliases=_list(r.get("aliases")), status=r.value("status"),
                line=r.line)
        for a, row in lay.product.attributes(slug).items():
            t, base, many, target = _type(row.get("type"))
            rank = row.value("rank") or ""
            o.attrs.append(Attr(obj=slug, slug=a, name=(row.get("name") or a).strip(),
                                rank=int(rank) if rank.isdigit() else 99, type=t, base=base, many=many, target=target,
                                required=row.value("required") == "true", length=_length(row.get("length")),
                                values=_list(row.get("values")), line=row.line))
        o.attrs.sort(key=lambda x: (x.rank, x.line))
        out[slug] = o
    return out


def used_items(parsed):
    """Датумы, которые называют деревья и контракты разобранных записей (`trees.all()` — вся поверхность)."""
    items = []

    def add(value):
        for m in DATA_REF.finditer(str(value)):
            if m.group(1) not in items:
                items.append(m.group(1))

    for p in parsed:
        for _, nodes in p.roots():
            for n, _ in T.walk(nodes):
                if n.prefix == "data" and n.valid:
                    add("data:" + str(n.name))
                for v in n.attrs.values():
                    add(v)
                for k, v in n.struct.items():
                    if k != "fill":
                        add(json.dumps(v, ensure_ascii=False))
        for key in ("data", "form", "tiles", "collection"):
            add(json.dumps(p.record.fm.get(key), ensure_ascii=False, default=str))
    return items


def obj_of(items, item):
    """Объект глоссария датума: колонка object строки data-items (`<object>.<атрибут>` — тот же объект)."""
    row = items.get(item) if item else None
    v = row.value("object") if row else None
    return v.split(".", 1)[0] if v else None


def items_of(lay, parsed):
    """Объекты глоссария датумов, которые называют разобранные записи, — по порядку."""
    items = lay.interface.table("data-items")
    return [o for o in dict.fromkeys(obj_of(items, i) for i in used_items(parsed)) if o]


def surface_objects(lay, trees, objs):
    """Объекты поверхности: объекты датумов деревьев и поле object экранов — в порядке object.md."""
    items = lay.interface.table("data-items")
    used = {obj_of(items, i) for i in used_items(trees.all())}
    used |= {L.cell(str(p.record.fm.get("object") or "")) for p in trees.screens.values()}
    return [o for o in objs if o in used]


# ------------------------------------------------------------------ коллекции

@dataclass
class Coll:
    id: str
    kind: str                                           # block · screen
    rec: L.Record
    pointer: str
    item: str | None
    obj: str | None
    has_contract: bool
    volume: dict | None
    problem: str | None                                 # volume не по форме
    screens: list


def _is_coll(n):
    return n.ui_type in S.COLLECTION_TYPES or (n.ui_type == "Card" and "items" in n.attrs)


def _item_of(value):
    m = DATA_REF.search(str(value or ""))
    return m.group(1) if m else None


def _volume(c):
    if not isinstance(c, dict) or L.is_empty(c.get("volume")):
        return None, None
    v = c["volume"]
    if not isinstance(v, dict):
        return None, "volume — словарь {typical, max}"
    t, m = v.get("typical"), v.get("max")
    if not all(isinstance(x, int) and not isinstance(x, bool) and x >= 0 for x in (t, m)):
        return None, f"volume — {{typical, max}} целыми числами, а не {json.dumps(v, ensure_ascii=False)}"
    if t > m:
        return None, f"typical {t} больше max {m}"
    return {"typical": t, "max": m}, None


def collections(lay, trees):
    """{id: Coll}: блоки с коллекцией или контрактом collection, затем коллекции прямо в slot-fills экранов."""
    items = lay.interface.table("data-items")
    uses = {}
    for s in trees.screens:
        for b in T.composition(trees, s)["blocks"]:
            uses.setdefault(b, []).append(s)
    out = {}
    for slug, p in trees.blocks.items():
        nodes = [n for f in p.areas.values() if f.kind == "tree" for n, _ in T.walk(f.nodes) if _is_coll(n)]
        c = p.record.fm.get("collection")
        if not nodes and not isinstance(c, dict):
            continue
        item = _item_of(nodes[0].attrs.get("items")) if nodes else None
        if item is None and isinstance(p.record.fm.get("data"), dict):
            item = next((_item_of(v) for v in p.record.fm["data"].values() if _item_of(v)), None)
        vol, problem = _volume(c)
        out[slug] = Coll(id=slug, kind="block", rec=p.record, pointer=nodes[0].pointer if nodes else "/collection",
                         item=item, obj=obj_of(items, item), has_contract=isinstance(c, dict), volume=vol,
                         problem=problem, screens=sorted(uses.get(slug, [])))
    for s, p in trees.screens.items():
        for f in p.fills.values():
            for n, _ in T.walk(f.nodes if f.kind == "tree" else []):
                if _is_coll(n):
                    item = _item_of(n.attrs.get("items"))
                    out[f"{s}#{n.pointer}"] = Coll(id=f"{s}#{n.pointer}", kind="screen", rec=p.record,
                                                   pointer=n.pointer, item=item, obj=obj_of(items, item),
                                                   has_contract=False, volume=None, problem=None, screens=[s])
    return out


# ------------------------------------------------------------------ значения

@dataclass
class Ctx:
    obj: Obj
    ident: Attr | None                                  # узнающий атрибут: text с наименьшим рангом 1–3
    heads: list                                         # ведущие части examples
    words: list                                         # слова объекта — заполнение подписи до длины
    scale: float | None                                 # масштаб чисел из examples


def context(o):
    texts = [a for a in o.attrs if a.base == "text" and a.rank <= 3]
    heads, nums, words = [], [], []
    for ex in o.examples:
        parts = re.split(r"\s+[—–]\s+", ex, maxsplit=1)
        heads.append(parts[0].strip())
        nums += [float(x.replace(",", ".")) for x in NUM.findall(parts[1] if len(parts) > 1 else "")]
    for s in o.examples + [o.description]:
        for w in WORD.findall(s or ""):
            if w not in words:
                words.append(w)
    return Ctx(obj=o, ident=texts[0] if texts else None, heads=heads, words=words,
               scale=statistics.median(nums) if nums else None)


def _slugify(text):
    s = re.sub(r"[^0-9a-zа-яё]+", "-", str(text).lower()).strip("-")
    return s or "file"


class Gen:
    """Значения набора: случай — хэш от зерна и места значения."""

    def __init__(self, seed, anchor):
        n = norms()
        self.seed, self.anchor = seed, anchor
        self.p, self.d = n["params"], n["dates"]
        self.patterns = [(re.compile(x["match"], re.I), x["value"]) for x in n.get("patterns") or []]
        self.ext = [(re.compile(x["match"], re.I), x["ext"]) for x in (n.get("files") or {}).get("by_name") or []]
        self.ext_default = (n.get("files") or {}).get("default", "pdf")
        self.pool = {}                                  # объект → число записей набора

    def u(self, *keys):
        return _u(self.seed, *keys)

    def tri(self, lo, mode, hi, *keys):
        """Треугольное распределение [lo, hi] с модой mode — длины вокруг типичной."""
        if hi <= lo:
            return lo
        mode = min(max(mode, lo), hi)
        u, c = self.u(*keys), (mode - lo) / (hi - lo)
        x = lo + math.sqrt(u * (hi - lo) * (mode - lo)) if u < c else hi - math.sqrt((1 - u) * (hi - lo) * (hi - mode))
        return int(round(x))

    def pattern(self, a):
        return next((v for rx, v in self.patterns if rx.search(a.name) or rx.search(a.slug)), None)

    def _digits(self, template, a, i, salt, ch="#"):
        out, k = [], 0
        for c in template:
            if (c == ch) or (ch == "0" and c.isdigit()):
                out.append(str(int(self.u(a.obj, a.slug, i, salt, "digit", k) * 10) % 10))
                k += 1
            else:
                out.append(c)
        return "".join(out)

    def text(self, ctx, a, i, target=None, exact=False, salt=""):
        pat = self.pattern(a)
        if pat:
            return self._digits(pat, a, i, salt)
        lo, typ, hi = a.length or tuple(self.p["text_length"])
        if a is ctx.ident and ctx.heads:
            head = ctx.heads[(i - 1) % len(ctx.heads)]
            if not exact and i <= len(ctx.heads):
                return head
            if re.search(r"\d", head):
                value = self._digits(head, a, i, salt, ch="0")
                if exact:                               # крайняя длина образца: цифры дописаны или сняты с конца
                    value = value + self._digits("0" * max(0, target - len(value)), a, i, salt + "pad", ch="0")
                    value = value[:max(1, target)]
                return value
        if target is None:
            target = self.tri(lo, typ, hi, a.obj, a.slug, i, salt, "len")
        return self.filler(ctx, a, i, target, exact)

    def filler(self, ctx, a, i, target, exact=False):
        """Видимая подпись «<имя атрибута> <n>» и слова объекта до длины target (exact — ровно target знаков)."""
        if target <= 0:
            return ""
        base = f"{a.name} {i}"
        if len(base) >= target:
            if not exact:
                return base
            num = str(i)
            short = f"{a.name[:target - len(num) - 1].rstrip()} {num}" if target >= len(num) + 2 else a.name[:target]
            return short[:target] if len(short) >= target else short + "".join(
                str(int(self.u(a.obj, a.slug, i, "pad", k) * 10) % 10) for k in range(target - len(short)))
        words = ctx.words or [w for w in a.name.lower().split() if w] or ["пример"]
        k = int(self.u(a.obj, a.slug, i, "words") * len(words))
        s = base
        while len(s) + 1 + len(words[k % len(words)]) <= target and len(s) < 10000:
            s += " " + words[k % len(words)]
            k += 1
        if not exact or len(s) == target:
            return s
        long = s
        while len(long) <= target:
            long += " " + words[k % len(words)]
            k += 1
        cut = long[:target]
        return cut if not cut.endswith(" ") else long[:target - 1] + long[target]

    def number(self, ctx, a, i, salt=""):
        scale = ctx.scale or self.p["number_scale" if a.base == "number" else "money_scale"]
        return max(0, int(round(scale * (0.5 + self.u(a.obj, a.slug, i, salt)))))

    def when(self, a, i, days=None, time=None, tz=None, salt=""):
        if days is None:
            spread = int(self.d["spread_days"])
            days = int(self.u(a.obj, a.slug, i, salt, "day") * (2 * spread + 1)) - spread
        d = self.anchor + timedelta(days=days)
        if a.base == "date":
            return d.isoformat()
        if time is None:
            h = 9 + int(self.u(a.obj, a.slug, i, salt, "h") * 10)
            time = f"{h:02d}:{30 * int(self.u(a.obj, a.slug, i, salt, 'm') * 2):02d}"
        return f"{d.isoformat()}T{time}:00{tz or self.d['tz']}"

    def enum(self, a, i, salt=""):
        if not a.values:
            return None
        if a.many:
            k = 1 + int(self.u(a.obj, a.slug, i, salt, "k") * min(int(self.p["many_max"]), len(a.values)))
            chosen = set(sorted(a.values, key=lambda v: self.u(a.obj, a.slug, i, salt, v))[:k])
            return [v for v in a.values if v in chosen]
        return a.values[int(self.u(a.obj, a.slug, i, salt) * len(a.values))]

    def ref(self, a, i, salt="", count=None):
        n = self.pool.get(a.target) or 3
        if count is not None:
            return [f"{a.target}-{x}" for x in range(1, count + 1)]
        if not a.many:
            return f"{a.target}-{1 + int(self.u(a.obj, a.slug, i, salt) * n)}"
        k = 1 + int(self.u(a.obj, a.slug, i, salt, "k") * min(int(self.p["many_max"]), n))
        return [f"{a.target}-{x}" for x in sorted(sorted(range(1, n + 1),
                                                         key=lambda x: self.u(a.obj, a.slug, i, salt, x))[:k])]

    def file(self, a, i):
        ext = next((e for rx, e in self.ext if rx.search(a.name) or rx.search(a.slug)), self.ext_default)
        return f"{_slugify(a.name)}-{i}.{ext}"

    def value(self, ctx, a, i, salt=""):
        if a.base == "text":
            return self.text(ctx, a, i, salt=salt)
        if a.base in NUMERIC:
            return self.number(ctx, a, i, salt)
        if a.base in DATES:
            return self.when(a, i, salt=salt)
        if a.base == "enum":
            return self.enum(a, i, salt)
        if a.base == "bool":
            return self.u(a.obj, a.slug, i, salt, "bool") < float(self.p["bool_true"])
        if a.base == "file":
            return self.file(a, i)
        if a.base == "ref" and a.target:
            return self.ref(a, i, salt)
        return None

    def record(self, ctx, i):
        o = ctx.obj
        rec = {"example": True, "_id": f"{o.slug}-{i}"}
        for a in o.attrs:
            empty = not a.required and a.rank > 3 and \
                self.u(o.slug, a.slug, i, "empty") < float(self.p["optional_empty"])
            rec[a.slug] = None if empty else self.value(ctx, a, i)
        return rec

    def records(self, ctx, n):
        pool = [self.record(ctx, i) for i in range(1, n + 1)]
        for a in ctx.obj.attrs:                         # каждое значение перечня — хоть раз в наборе
            if a.base != "enum" or a.many or not a.values:
                continue
            have = {r[a.slug] for r in pool}
            for k, v in enumerate(x for x in a.values if x not in have):
                if k < len(pool):
                    pool[-1 - k][a.slug] = v
        return pool

    def edges(self, ctx, pool):
        """Записи крайних случаев объекта и классы, которых у него нет."""
        o, n = ctx.obj, norms()
        texts = [a for a in o.attrs if a.base == "text" and not self.pattern(a)]
        groups = {"text": texts, "optional": [a for a in o.attrs if not a.required],
                  "number": [a for a in o.attrs if a.base in NUMERIC],
                  "date": [a for a in o.attrs if a.base in DATES],
                  "datetime": [a for a in o.attrs if a.base == "datetime"],
                  "ref": [a for a in o.attrs if a.base == "ref" and a.target],
                  "ref-many": [a for a in o.attrs if a.base == "ref" and a.target and a.many],
                  "ident": [ctx.ident] if ctx.ident else [], "file": [a for a in o.attrs if a.base == "file"]}
        base = pool[0]
        out, na = [], []
        for case in n["cases"]:
            cid = str(case["id"])
            attrs = groups.get(case["applies"], [])
            if not attrs:
                na.append({"case": cid, "why": NA_WHY.get(case["applies"], case["applies"])})
                continue
            rec = {"example": True, "_id": f"{o.slug}-{cid}", "_case": cid, "_decide": case["decide"],
                   "_source": case["source"]}
            src = dict(base)
            if cid == "duplicate":
                twin = pool[1] if len(pool) > 1 else base
                src = dict(twin)
                src[ctx.ident.slug] = base[ctx.ident.slug]
                rec["_twin"] = base["_id"]
            for k, v in src.items():
                if k not in ("example", "_id"):
                    rec[k] = v
            for a in attrs:
                lo, _, hi = a.length or tuple(self.p["text_length"])
                if cid == "longest":
                    rec[a.slug] = self.text(ctx, a, 1, target=hi, exact=True, salt=cid)
                elif cid == "shortest":
                    rec[a.slug] = self.text(ctx, a, 1, target=lo, exact=True, salt=cid)
                elif cid == "exotic":
                    rec[a.slug] = str(n["exotic"]["value"])[:hi]
                elif cid == "missing":
                    rec.pop(a.slug, None)
                elif cid in ("null", "no-file"):
                    rec[a.slug] = None
                elif cid == "zero":
                    rec[a.slug] = 0
                elif cid == "negative":
                    rec[a.slug] = -max(1, self.number(ctx, a, 1, cid))
                elif cid == "large":
                    rec[a.slug] = int(n["large_number"]["value"])
                elif cid == "date-past":
                    rec[a.slug] = self.when(a, 1, days=-int(self.d["past_days"]), salt=cid)
                elif cid == "date-future":
                    rec[a.slug] = self.when(a, 1, days=int(self.d["future_days"]), salt=cid)
                elif cid == "date-today":
                    rec[a.slug] = self.when(a, 1, days=0, salt=cid)
                elif cid == "timezone":
                    rec[a.slug] = self.when(a, 1, days=0, time=self.d["tz_other_time"], tz=self.d["tz_other"])
                elif cid == "no-relations":
                    rec[a.slug] = [] if a.many else None
                elif cid == "many-relations":
                    rec[a.slug] = self.ref(a, 1, count=int(n["relations_many"]["value"]))
            out.append(rec)
        return out, na


# ------------------------------------------------------------------ набор

def localization(lay):
    """Самая длинная строка каждой роли реестра — по всем колонкам текста (text, text-<locale>)."""
    t = lay.texts
    best = {}
    for key, row in (t.rows.items() if t.exists else []):
        variants = [("text", row.text)] + [(c, (v or "").strip()) for c, v in sorted(row.locales.items())
                                           if (v or "").strip()]
        col, text = max(variants, key=lambda x: len(x[1]))
        role = row.role or "—"
        if role not in best or len(text) > best[role]["length"]:
            best[role] = {"role": role, "key": key, "column": col, "text": text, "length": len(text),
                          "maxlen": int(row.maxlen) if (row.maxlen or "").isdigit() else None}
    return [best[r] for r in sorted(best)]


def build(lay, seed=None, anchor=None, trees=None):
    """Документ демо-набора поверхности (словарь в порядке вывода)."""
    trees = trees or T.parse_layer(lay)
    n = norms()
    window, few, fallback = int(n["window"]["value"]), int(n["few"]["value"]), n["fallback"]["value"]
    anchor_d = date.fromisoformat(str(anchor or n["dates"]["anchor"]))
    seed = str(seed or lay.slug)
    objs = objects(lay)
    surf = surface_objects(lay, trees, objs)
    colls = collections(lay, trees)
    g = Gen(seed, anchor_d)
    need = {o: max(1, len(objs[o].examples)) for o in surf}
    for c in colls.values():
        if c.obj in need:
            vol = c.volume or fallback
            need[c.obj] = max(need[c.obj], min(window, int(vol["max"])), min(window, few))
    g.pool = dict(need)
    doc_objects = {}
    for o in surf:
        ctx = context(objs[o])
        pool = g.records(ctx, need[o])
        edge, na = g.edges(ctx, pool)
        ob = objs[o]
        doc_objects[o] = {
            "example": True, "name": ob.name, "description": ob.description, "aliases": ob.aliases,
            "statuses": [{"slug": s, "name": nm} for s, nm in ob.statuses], "examples": ob.examples,
            "attributes": [{"slug": a.slug, "name": a.name, "rank": a.rank, "type": a.type, "required": a.required,
                            "length": list(a.length) if a.length else None, "values": a.values or None}
                           for a in ob.attrs],
            "records": pool, "edge_cases": edge, "not_applicable": na}
    doc_colls = {}
    for cid, c in colls.items():
        vol = c.volume or fallback
        counts = {"empty": 0, "few": min(few, int(vol["max"])), "typical": int(vol["typical"]), "max": int(vol["max"])}
        sets = {}
        for name, count in counts.items():
            shown = min(count, window) if c.obj in doc_objects else 0
            sets[name] = {"example": True, "count": count, "states": SET_STATES[name],
                          "records": [f"{c.obj}-{k}" for k in range(1, shown + 1)]}
        doc_colls[cid] = {"example": True, "kind": c.kind, "object": c.obj, "item": c.item, "screens": c.screens,
                          "volume": c.volume, "counts_from": "collection.volume" if c.volume else
                          f"{n['fallback']['source']} (объёма у коллекции нет)", "sets": sets}
    sources = [docpaths.project(lay.slug, "object.md", repo=lay.repo),
               lay.interface.path("data-items")] + [c.rec.path for c in colls.values()] + [lay.texts_path]
    seen = []
    for p in sources:
        r = lay.rel(p)
        if Path(p).is_file() and r not in seen:
            seen.append(r)
    return {
        "example": True, "demo_data_version": VERSION,
        "note": "демо-набор — пример для макета, а не данные продукта: макет на нём допустим, публикация — нет",
        "project": lay.slug, "surface": lay.surface, "seed": seed, "anchor": anchor_d.isoformat(), "window": window,
        "sources": seen, "norms": NORMS_REF, "objects": doc_objects, "collections": doc_colls,
        "localization": localization(lay),
        "gaps": [{"rule": f.rule, "severity": f.severity, "path": f.path, "message": f.message}
                 for f in gaps(lay, trees)]}


def dumps(doc):
    """Текст JSON набора — детерминированный."""
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


# ------------------------------------------------------------------ пробелы

def gaps(lay, trees=None):
    """Пробелы источников набора — находки (контракт findings)."""
    trees = trees or T.parse_layer(lay)
    rep = F.Report()
    n = norms()
    fb = n["fallback"]["value"]
    for cid, c in collections(lay, trees).items():
        rec = c.rec
        where = f"блока `{rec.slug}`" if c.kind == "block" else f"в дереве экрана `{rec.slug}` ({c.pointer})"
        fix = (f"/screen-deep-dive {lay.slug} {lay.surface} {c.kind}:{rec.slug} — объём коллекции даёт аналитик")
        ref = f"{rec.slug}#/collection/volume" if c.kind == "block" else f"{rec.slug}#{c.pointer}"
        if c.problem:
            rep.add("R-MAT-011", "warning", surface=lay.surface, kind=c.kind, ref=ref, path=lay.rel(rec.path),
                    message=f"PRE-14: collection.volume {where} не по форме: {c.problem}", fix=fix)
        elif c.volume is None:
            what = "нет collection.volume {typical, max}" if c.has_contract else \
                "нет контракта collection с объёмом {typical, max}"
            rep.add("R-MAT-011", "warning", surface=lay.surface, kind=c.kind, ref=ref, path=lay.rel(rec.path),
                    message=f"PRE-14: у коллекции {where} {what} — демо-набор берёт {fb['typical']} и {fb['max']} "
                            "записей (ux 13/04 §12)", fix=fix)
        if c.obj is None:
            rep.add("R-DEBT-002", "hint", surface=lay.surface, kind=c.kind, ref=f"{rec.slug}#{c.pointer}",
                    path=lay.rel(rec.path), message=f"коллекция {where}: у датума `{c.item or '?'}` нет объекта "
                                                    "глоссария (data-items.object) — записей набора нет",
                    fix=f"/interface-deep-dive {lay.slug} {lay.surface}")
    objs = objects(lay)
    opath = lay.rel(docpaths.project(lay.slug, "object.md", repo=lay.repo))
    ofix = f"/project-deep-dive {lay.slug} object:"

    def hint(ref, message, obj):
        rep.add("R-DEBT-002", "hint", surface=lay.surface, kind="object", ref=ref, path=opath, message=message,
                fix=ofix + obj)

    for o in surface_objects(lay, trees, objs):
        ob = objs[o]
        if not ob.examples:
            hint(f"object#{o}/examples", f"у объекта `{o}` пусто examples: узнающий атрибут в наборе — подписи "
                                         "«<имя> <n>», а не экземпляры из материалов клиента", o)
        if not ob.attrs:
            hint(f"object#{o}", f"у объекта `{o}` нет атрибутов: записи набора — только `_id`", o)
        for a in ob.attrs:
            at = f"object#{o}.{a.slug}"
            if a.base == "?":
                hint(at + "/type", f"тип `{a.type}` атрибута `{o}.{a.slug}` вне перечня формы — значение null", o)
            if a.base == "text" and a.length is None:
                lo, typ, hi = n["params"]["text_length"]
                hint(at + "/length", f"у `{o}.{a.slug}` (text) нет length — длины значений {lo} / {typ} / {hi}", o)
            if a.base == "enum" and not a.values:
                hint(at + "/values", f"у `{o}.{a.slug}` ({a.type}) нет values — значение null", o)
            if a.base == "ref" and a.target not in objs:
                hint(at + "/type", f"`{o}.{a.slug}` ссылается на объект `{a.target}`, которого нет в object.md", o)
    return rep.items


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return _selftest()
    ap = docpaths.parser("demo_data", __doc__, commands=("build", "check"), surface="optional",
                         accept=lambda s: s.app)
    ap.add_argument("--seed", help="зерно набора (по умолчанию — slug проекта)")
    ap.add_argument("--anchor", metavar="ГГГГ-ММ-ДД", help="опорная дата «сегодня» набора (по умолчанию — "
                                                           "data/demo.yaml)")
    call = docpaths.parse(ap, argv)
    try:
        lays = T.layers_of(call)
        if not lays:
            print(f"demo_data: у проекта {call.slug} нет поверхностей кабинета (web рода app, admin, desktop, embed)",
                  file=sys.stderr)
            return F.EXIT_USAGE
        if call.command == "check":
            items = []
            for lay in lays:
                items += gaps(lay)
            F.print_findings(items, as_json=call.json)
            return F.exit_code(items)
        if len(lays) != 1:
            ap.error("build — одна поверхность: demo_data build <slug> <surface>; поверхности кабинета: "
                     + ", ".join(x.surface for x in lays))
        lay = lays[0]
        doc = build(lay, call.args.seed, call.args.anchor)
        text = dumps(doc)
        if call.out is None:
            sys.stdout.write(text)
            return F.EXIT_OK
        target = Path(call.out) / "demo-data.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        if call.json:
            print(json.dumps({"surface": lay.surface, "path": str(target), "objects": len(doc["objects"]),
                              "collections": len(doc["collections"]), "gaps": len(doc["gaps"])}, ensure_ascii=False))
        else:
            print(f"{lay.surface}: {target}")
        return F.EXIT_OK
    except (F.ToolError, docpaths.DocPathError, RuntimeError, OSError, ValueError) as e:
        print(f"demo_data: {e}", file=sys.stderr)
        return F.EXIT_USAGE


# ------------------------------------------------------------------ самопроверка

def _walk_examples(doc):
    """Записи и наборы документа без example: true."""
    bad = [] if doc.get("example") is True else ["документ"]
    for o, ob in doc["objects"].items():
        bad += [f"{o}:{r.get('_id')}" for r in ob["records"] + ob["edge_cases"] if r.get("example") is not True]
    for cid, c in doc["collections"].items():
        bad += [f"{cid}" for _ in [0] if c.get("example") is not True]
        bad += [f"{cid}.{k}" for k, s in c["sets"].items() if s.get("example") is not True]
    return bad


def _selftest():
    import shutil
    import subprocess
    import tempfile
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    n = norms()
    ids = {str(c["id"]) for c in n["cases"]}
    check("нормы: окно 50, «мало» 1, объёмы 20 и 5 000 без volume; у норм и классов — адрес базы",
          n["window"]["value"] == 50 and n["few"]["value"] == 1 and n["fallback"]["value"] == {"typical": 20,
                                                                                             "max": 5000}
          and all(c.get("source") and c.get("decide") for c in n["cases"]))
    check("классы крайних случаев ux 06/01 §6.2 и ux 13/04 §12", {"longest", "shortest", "exotic", "missing", "null",
                                                                  "zero", "negative", "large", "date-past",
                                                                  "date-future", "timezone", "no-relations",
                                                                  "many-relations", "duplicate"} <= ids)
    check("случай — хэш: тот же ключ — то же число в [0, 1)", _u("a", 1) == _u("a", 1) and 0 <= _u("a", 2) < 1)
    check("examples: экземпляры через «;», пометка в скобках снята",
          _examples("З-1 — a, b; З-2 — c (демо)") == ["З-1 — a, b", "З-2 — c"] and _examples("—") == [])
    check("статусы и тип атрибута", _statuses("`` `new` — новая · `done` — готово ``") == [("new", "новая"),
                                                                                         ("done", "готово")]
          and _type("`ref:plan[]`") == ("ref:plan[]", "ref", True, "plan") and _type("`enum`")[1] == "enum")
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("cabinet-demo") as fx:
        lay = L.Layer(fx.slug, "office", fx.root)
        doc = build(lay)
        text = dumps(doc)
        check("повторная сборка — тот же JSON байт в байт", dumps(build(L.Layer(fx.slug, "office", fx.root))) == text)
        check("каждая запись, набор и документ — example: true", not _walk_examples(doc))
        coll = doc["collections"].get("requests-list") or {"sets": {}}
        counts = {k: v["count"] for k, v in coll["sets"].items()}
        check("коллекция списка: empty 0, few 1, typical 60 и max 3 000 из volume",
              counts == {"empty": 0, "few": 1, "typical": 60, "max": 3000})
        check("записей в наборе — не больше окна 50; few — первая запись",
              len(coll["sets"]["typical"]["records"]) == 50 and len(coll["sets"]["max"]["records"]) == 50
              and coll["sets"]["few"]["records"] == ["request-1"] and coll["sets"]["empty"]["records"] == [])
        check("наборы называют свои состояния", coll["sets"]["empty"]["states"] == ["empty-first-run", "empty-filtered"]
              and coll["sets"]["max"]["states"] == ["overflow-many"])
        req, plan = doc["objects"]["request"], doc["objects"]["plan"]
        check("объекты поверхности — заявка и план, записей 50 и 2",
              list(doc["objects"]) == ["request", "plan"] and len(req["records"]) == 50 and len(plan["records"]) == 2)
        nums = [r["number"] for r in req["records"]]
        check("узнающий атрибут — из examples, дальше — тот же образец с другими цифрами",
              nums[:2] == ["З-0412", "З-0415"] and all(re.fullmatch(r"З-\d{4}", x) for x in nums))
        phones = [r["phone"] for r in req["records"]]
        check("text по образцу имени: телефон", all(re.fullmatch(r"\+7 9\d\d \d{3}-\d\d-\d\d", x) for x in phones))
        check("перечень: каждое значение статуса хоть раз",
              {r["status"] for r in req["records"]} == {"новая", "замер назначен", "замер проведён", "отказ"})
        check("enum[] — подмножество values по порядку; bool, money, file",
              all(r["rooms"] is None or (r["rooms"] and set(r["rooms"]) <= {"кухня", "санузел", "комната", "коридор"})
                  for r in req["records"])
              and any(r["urgent"] is True for r in req["records"]) and any(isinstance(r["budget"], int)
                                                                          for r in req["records"])
              and any(str(r["photo"] or "").endswith(".jpg") for r in req["records"]))
        check("number плана — масштаб чисел examples (40 и 45)", all(20 <= r["target"] <= 68 for r in plan["records"]))
        e = {x["_case"]: x for x in req["edge_cases"]}
        check("длина строки: самое длинное — max, самое короткое — min из length",
              len(e["longest"]["client"]) == 60 and len(e["shortest"]["client"]) == 2 and
              len(e["longest"]["address"]) == 120 and len(e["shortest"]["address"]) == 10)
        check("крайние длины узнающего атрибута — по образцу examples",
              re.fullmatch(r"З-\d{6}", e["longest"]["number"]) and re.fullmatch(r"З-\d{4}", e["shortest"]["number"]))
        check("подпись обычной записи не обрезается: «<имя> <n>» и слова объекта",
              all(str(r["client"]).startswith(f"Клиент {k}") for k, r in enumerate(req["records"], 1)))
        check("экзотика, пусто, null, ноль, минус, очень большое",
              "’" in e["exotic"]["client"] and "visit-date" not in e["missing"] and e["null"]["budget"] is None
              and e["zero"]["budget"] == 0 and e["negative"]["budget"] < 0 and e["large"]["budget"] == 1234567890)
        check("даты: в прошлом, в будущем, сегодня, другой пояс",
              e["date-past"]["visit-date"].startswith("2016-") and e["date-future"]["visit-date"] > "2026-10-01"
              and e["date-today"]["visit-date"].startswith("2026-10-01T")
              and e["timezone"]["visit-date"].endswith("+10:00"))
        check("дубликат — имя первой записи у другой записи", e["duplicate"]["number"] == "З-0412"
              and e["duplicate"]["_twin"] == "request-1" and e["duplicate"]["client"] != req["records"][0]["client"])
        pe = {x["_case"]: x for x in plan["edge_cases"]}
        check("50 связей у ref:request[] и объект без связей",
              len(pe["many-relations"]["requests"]) == 50 and pe["no-relations"]["requests"] == [])
        check("класс без атрибутов нужного типа — не применимо с причиной",
              {"case": "many-relations", "why": NA_WHY["ref-many"]} in req["not_applicable"])
        loc = {x["role"]: x for x in doc["localization"]}
        check("локализация: самая длинная строка каждой роли", loc.get("empty", {}).get("key") ==
              "requests.list.empty-first-run.empty" and loc["empty"]["length"] == len(loc["empty"]["text"]))
        check("зерно и опорная дата меняют значения", dumps(build(lay, seed="x")) != text and
              build(lay, anchor="2027-01-01")["anchor"] == "2027-01-01")
        check("источники — файлы проекта, пути существуют", doc["sources"] and
              all((fx.root / p).is_file() for p in doc["sources"]))
        check("check: чистая фикстура — 0 находок", not gaps(lay) and doc["gaps"] == [])
        script = HERE / "demo_data.py"
        with tempfile.TemporaryDirectory(prefix="ddd-demo-") as td:
            r = subprocess.run([sys.executable, str(script), "build", fx.slug, "office", "--repo", str(fx.root)],
                               cwd=td, capture_output=True, text=True)
            check("build из чужой рабочей папки с --repo — тот же JSON", r.returncode == 0 and r.stdout == text)
            r = subprocess.run([sys.executable, str(script), "build", fx.slug, "office", "--repo", str(fx.root),
                                "--out", str(Path(td) / "in")], cwd=td, capture_output=True, text=True)
            check("build --out: DIR/demo-data.json", r.returncode == 0 and
                  (Path(td) / "in" / "demo-data.json").read_text(encoding="utf-8") == text)
            r = subprocess.run([sys.executable, str(script), "check", fx.slug, "--repo", str(fx.root), "--json"],
                               cwd=td, capture_output=True, text=True)
            check("check --json без поверхности — все поверхности кабинета, код 0", r.returncode == 0 and
                  F.parse_lines(r.stdout) == [])
            r = subprocess.run([sys.executable, str(script), "build", fx.slug, "office", "--repo", str(fx.root),
                                "--anchor", "01.10.2026"], cwd=td, capture_output=True, text=True)
            check("неверная опорная дата — код 2", r.returncode == 2)
            root = Path(td) / "r"
            shutil.copytree(fx.root, root)
            proj = root / "docs" / "projects" / fx.slug
            blk = proj / "screens" / "office" / "blocks" / "requests-list" / "index.md"
            blk.write_text(blk.read_text(encoding="utf-8").replace("  volume: {typical: 60, max: 3000}\n", "", 1),
                           encoding="utf-8")
            obj = proj / "object.md"
            obj.write_text(obj.read_text(encoding="utf-8").replace(
                "З-0412 — Сормово, двухкомнатная; З-0415 — Верхние Печёры, санузел (демо)", "—", 1), encoding="utf-8")
            lay2 = L.Layer(fx.slug, "office", root)
            items = gaps(lay2)
            vol = [f for f in items if f.rule == "R-MAT-011"]
            ex = [f for f in items if f.rule == "R-DEBT-002" and "examples" in f.ref]
            check("снятый volume — R-MAT-011 warning с путём блока", len(vol) == 1 and vol[0].severity == "warning" and
                  vol[0].path.endswith("screens/office/blocks/requests-list/index.md"))
            check("пустые examples — R-DEBT-002 с путём object.md", len(ex) == 1 and ex[0].path.endswith("object.md"))
            doc2 = build(lay2)
            c2 = doc2["collections"]["requests-list"]
            check("без volume — объёмы ux 13/04 §12 (20 и 5 000), пробел — в gaps документа",
                  c2["sets"]["typical"]["count"] == 20 and c2["sets"]["max"]["count"] == 5000 and c2["volume"] is None
                  and len(doc2["gaps"]) == 2)
            check("без examples — подписи «<имя> <n>» у узнающего атрибута",
                  doc2["objects"]["request"]["records"][0]["number"].startswith("Номер заявки"[:3]))
            r = subprocess.run([sys.executable, str(script), "check", fx.slug, "office", "--repo", str(root)],
                               cwd=td, capture_output=True, text=True)
            check("check с пробелом объёма — доклад, код 0", r.returncode == 0 and "R-MAT-011" in r.stdout)
    print("demo_data selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
