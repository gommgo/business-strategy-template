#!/usr/bin/env python3
"""normalize — приведение заполненного слоя экранов к канону: механические правки в терминах канона, смысловые поля
остаются пустыми для владельца и перечисляются.

Вход — вольная запись поверхности (`screens/<surface>/`: экраны, блоки, каркасы, `map.md`, `texts.md`), выход — форма
канона `docs/projects/_template/screens/`. Механически, по данным канона:
  дерево          узел с детьми — голова с двоеточием; `(fills: $слот)` → `fills=$слот` в голове; пары атрибутов без
                  пробелов вокруг «=»; простое значение структуры (`items: data:…`) — в голову узла
  ui:             имя из `aka` словаря `kb/common/components.yaml` → тип словаря; тип в другом регистре → тип словаря
  атрибуты        синонимы входа `variant=accent · outline · ghost` → `level=primary · secondary · tertiary`
                  (уровень действия — проверить владельцу); `size` и атрибуты вне закрытого списка снимаются
  states          ключ вне словаря → ключ словаря по таблице ключей мобильного слоя (`docs/projects/_template/mobile/
                  README.md`, «Состояния экрана и словарь»); ключ, за которым несколько состояний, — первое, и вопрос
                  владельцу; «здесь не применимо» → `'не применимо: причина'` (причина — из комментария строки)
  тексты          литерал в дереве и label колонки → `text:<ключ>` по месту и роли `{раздел}.{экран}.{элемент}.{роль}`
                  (раздел — корневая зона записи, элемент — действие узла, атрибут колонки или ключ состояния, роль — по
                  части компонента `text_roles`) и строка `texts.md` со статусом `assumed`; строка с тем же ключом и
                  текстом переиспользуется
  переходы        `transitions-to-screen: [a]` → `[{to: a}]`
  свод и реестр   нет `texts.md` или `map.md` — из формы; генерируемые разделы `map.md` — по экранам (screen_map)
Смысловые поля (тип, объект, главная задача, ключевое действие, зона, параметры, доступ и состояние в адресе экрана;
чем вызван переход, что сохраняется, как вернуться; текст и роль новой строки; выбор между состояниями словаря)
нормализатор не заполняет: прочерк — решение владельца, пустое поле аудит видит как пробел. Блок YAML, который после
механических правок не разбирается, остаётся как был — пунктом владельцу «привести вручную».

    normalize check <slug> [<surface>] [--repo DIR] [--json]              дифф и список для владельца; не пишет
    normalize build <slug> [<surface>] [--repo DIR] [--write] [--json]    с --write — правка файлов проекта по месту
    normalize build <slug> [<surface>] --out DIR                          приведённые файлы — в DIR/docs/projects/…
    normalize --selftest                                                   фикстуры кабинета, без сети
Без --write и --out команда build только показывает дифф. Код выхода: check — 0, если править нечего, 1 — есть
правки; build — 0; 2 — ошибка вызова или окружения. JSON: {files, changes, owner, diff, written}; changes и owner —
находки формата модуля findings (правило канона, которое правка закрывает или которым аудит покажет пробел).
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import sys
import tempfile
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
import states as S  # noqa: E402
import screen_map as M  # noqa: E402

# синонимы входа: вид действия → уровень действия (T.VALUES["level"])
VARIANT_LEVEL = {"accent": "primary", "outline": "secondary", "ghost": "tertiary"}
SCREEN_FIELDS = ("type", "object", "main-task", "key-action", "zone", "params", "access")
NA_INPUT = re.compile(r"^(?:здесь\s+)?не\s+применимо\b[\s:—–-]*(?P<reason>.*)$", re.I | re.S)
TEXT_HEADER = "| key | role | text | maxlen | action | object | group | context | status |"
TEXT_SEP = "|---|---|---|---|---|---|---|---|---|"


def kebab(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "-", str(name)).lower().replace(".", "-")


def scalar(v):
    """Значение YAML в одну строку: токен (slug, `data:…`, `text:…`, `$слот`) — как есть, иначе в одинарных кавычках."""
    s = str(v)
    if re.fullmatch(r"[A-Za-z0-9_$][A-Za-z0-9_$./-]*(?::[A-Za-z0-9_$./-]+)*", s):
        return s
    return "'" + s.replace("'", "''") + "'"


# ------------------------------------------------------------------ свободная запись: строки и узлы

@dataclass
class FLine:
    no: int
    indent: int
    text: str                                           # без отступа и хвостового комментария
    comment: str                                        # «# …» или ""


@dataclass
class FNode:
    line: int
    col: int                                            # колонка дефиса
    content: str
    children: list = field(default_factory=list)
    struct: list = field(default_factory=list)          # [FEntry]


@dataclass
class FEntry:
    line: int
    col: int
    key: str
    value: str | None = None                            # значение в той же строке
    seq: list | None = None                             # [FNode]
    map: list | None = None                             # [FEntry]


def split_comment(s):
    q = None
    for i, ch in enumerate(s):
        if q:
            if ch == q:
                q = None
        elif ch in ("'", '"'):
            q = ch
        elif ch == "#" and (i == 0 or s[i - 1] in " \t"):
            return s[:i].rstrip(), s[i:]
    return s.rstrip(), ""


def lex(lines):
    out = []
    for no, raw in enumerate(lines):
        if not raw.strip():
            continue
        body = raw.lstrip(" ")
        text, comment = split_comment(body)
        if not text:
            continue                                    # строка-комментарий
        out.append(FLine(no, len(raw) - len(body), text, comment))
    return out


def _is_item(fl):
    return fl.text == "-" or fl.text.startswith("- ")


def parse_map(fls, i, indent):
    out = []
    while i < len(fls):
        fl = fls[i]
        if fl.indent != indent or _is_item(fl):
            break
        m = re.match(r"^(?P<key>'[^']*'|\"[^\"]*\"|[^\s:'\"][^:]*?)\s*:(?:\s+(?P<val>.*))?$", fl.text)
        if not m:
            break
        key = m.group("key").strip("'\"")
        val = m.group("val")
        e = FEntry(fl.no, indent, key, value=val if val not in (None, "") else None)
        i += 1
        if e.value is None and i < len(fls):
            nxt = fls[i]
            if nxt.indent > indent or (nxt.indent == indent and _is_item(nxt)):
                if _is_item(nxt):
                    e.seq, i = parse_seq(fls, i, nxt.indent)
                else:
                    e.map, i = parse_map(fls, i, nxt.indent)
        out.append(e)
    return out, i


def parse_seq(fls, i, indent):
    out = []
    while i < len(fls):
        fl = fls[i]
        if fl.indent != indent or not _is_item(fl):
            break
        node = FNode(fl.no, indent, fl.text[1:].strip())
        i += 1
        while i < len(fls) and fls[i].indent > indent:
            base = fls[i].indent
            if _is_item(fls[i]):
                sub, i = parse_seq(fls, i, base)
                node.children += sub
            else:
                sub, j = parse_map(fls, i, base)
                if j == i:                              # строка вне формы — дальше не разобрать
                    i += 1
                    continue
                node.struct += sub
                i = j
        out.append(node)
    return out, i


# ------------------------------------------------------------------ контекст нормализации

@dataclass
class Item:
    """Правка или пункт для владельца — строка формата findings."""
    rule: str
    kind: str
    ref: str
    path: str
    message: str
    fix: str = ""


class Run:
    """Нормализация одной поверхности в копии проекта."""

    def __init__(self, lay):
        self.lay = lay
        self.comps = lay.components
        self.syn = S.synonyms_cached()
        self.dict = S.dictionary()
        self.texts = lay.texts
        self.new_rows = {}                              # ключ → (роль, текст, действие)
        self.changes = []
        self.owner = []
        zones = lay.interface.table("zone")
        self.zone_parent = {z: r.value("parent-zone") for z, r in zones.items()}
        self.iblocks = lay.interface.table("block")

    def change(self, rule, rec, ref, message):
        self.changes.append(Item(rule, rec.kind, ref, self.lay.rel(rec.path), message))

    def todo(self, rule, rec, ref, message, fix=""):
        self.owner.append(Item(rule, rec.kind, ref, self.lay.rel(rec.path), message,
                               fix or f"/screen-deep-dive {self.lay.slug} {self.lay.surface} {rec.kind}:{rec.slug}"))

    # --- ключ текста
    def root_zone(self, z):
        seen = set()
        while z and self.zone_parent.get(z) and z not in seen:
            seen.add(z)
            z = self.zone_parent[z]
        return z

    def place(self, rec):
        if rec.kind == "screen":
            zone = L.cell(str(rec.fm.get("zone") or ""))
        elif rec.kind == "block":
            row = self.iblocks.get(rec.slug)
            zone = row.value("zone") if row else None
        else:
            zone = None
        section = self.root_zone(zone) if zone else "app"
        screen = rec.slug[len(section) + 1:] if rec.slug.startswith(section + "-") else rec.slug
        return section, screen or rec.slug

    def key_for(self, rec, element, role, text, action):
        section, screen = self.place(rec)
        base = f"{section}.{screen}.{element}"
        n = 1
        while True:
            key = f"{base}{'' if n == 1 else '-' + str(n)}.{role}"
            have = self.texts.rows.get(key)
            new = self.new_rows.get(key)
            if have is not None:
                if have.text.strip() == text.strip():
                    return key, False
            elif new is not None:
                if new[1] == text:
                    return key, False
            else:
                self.new_rows[key] = (role, text, action)
                return key, True
            n += 1


# ------------------------------------------------------------------ правки узлов

def _tokens(head):
    """Голова → (имя, [(ключ, значение)]); пары склеиваются через пробелы вокруг «=»."""
    parts = head.split()
    name, rest = parts[0], " ".join(parts[1:])
    rest = re.sub(r"\s*=\s*", "=", rest)
    pairs = []
    for tok in rest.split():
        if "=" in tok:
            k, v = tok.split("=", 1)
            pairs.append((k, v))
        else:
            pairs.append((tok, None))
    return name, pairs


class NodeFix:
    """Правки одного блока YAML — построчно: отступы, порядок строк и комментарии аналитика остаются как были."""

    def __init__(self, run, rec, lines):
        self.run, self.rec = run, rec
        self.lines = list(lines)
        self.edit = {}                                  # номер строки → новый текст (None — удалить)

    def set_line(self, no, text):
        self.edit[no] = text

    def line_parts(self, no):
        raw = self.lines[no]
        body = raw.lstrip(" ")
        text, comment = split_comment(body)
        return raw[:len(raw) - len(body)], text, comment

    def rewrite_item(self, node, content):
        pad, _, comment = self.line_parts(node.line)
        self.set_line(node.line, f"{pad}- {content}" + (f"  {comment}" if comment else ""))

    def fix_nodes(self, nodes, ptr, anc, state=None):
        for i, n in enumerate(nodes):
            self.fix_node(n, f"{ptr}/{i}", anc, state)

    def fix_node(self, n, ptr, anc, state):
        run, rec = self.run, self.rec
        s = n.content
        parent = anc[-1] if anc else None
        if s.startswith("{") and s.endswith("}"):
            return                                      # запись структуры (колонка) — у владельца структуры
        literal = None
        if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
            try:
                literal = L._yaml().safe_load(s)
            except Exception:                           # noqa: BLE001
                literal = s[1:-1]
        colon = s.endswith(":") and literal is None
        head = s[:-1].rstrip() if colon else s
        fills = None
        m = re.search(r"\s*\(\s*fills\s*:\s*(\$[A-Za-z0-9_-]+)\s*\)\s*$", head)
        if m and literal is None:
            fills, head = m.group(1), head[:m.start()]
        if literal is None and not T.PREFIX_LIKE.match(head):
            literal = head
        if literal is not None:
            if n.children or n.struct:
                run.todo("R-STRUCT-020", rec, f"{rec.slug}#{ptr}", f"«{literal}» — узел с детьми без головы "
                                                                   "<префикс>:<имя>: привести вручную")
                return
            role = self.role(anc, state)
            element = self.element(anc, state)
            action = next((a.get("action") for a in reversed(anc) if isinstance(a, dict) and a.get("action")), None)
            key, new = run.key_for(rec, element, role, str(literal), action)
            self.rewrite_item(n, f"text:{key}")
            run.change("R-TX-003", rec, f"{rec.slug}#{ptr}",
                       f"литерал «{literal}» → text:{key}" + (" (новая строка texts.md, assumed)" if new
                                                              else " (строка texts.md с тем же текстом)"))
            return
        new_head = self.fix_head(head, fills, parent, ptr)
        # простые значения структуры — в голову
        keep_struct = []
        name, pairs = _tokens(new_head)
        prefix = name.split(":", 1)[0]
        allowed = T.ATTRS.get(prefix, ())
        moved = []
        for e in n.struct:
            if e.key in allowed and e.value is not None and not e.value.startswith(("[", "{", "'", '"')) and \
                    " " not in e.value.strip() and e.key not in dict(pairs):
                pairs.append((e.key, e.value.strip()))
                self.set_line(e.line, None)
                moved.append(e.key)
            else:
                keep_struct.append(e)
        if moved:
            new_head = name + "".join(f" {k}={v}" for k, v in pairs if v is not None)
            run.change("R-SEM-014", rec, f"{rec.slug}#{ptr}", f"`{', '.join(moved)}` — простое значение в голову "
                                                              f"узла: `{new_head}`")
        need_colon = bool(n.children or keep_struct)
        content = new_head + (":" if need_colon else "")
        if content != s:
            self.rewrite_item(n, content)
            if need_colon and not colon:
                run.change("R-STRUCT-020", rec, f"{rec.slug}#{ptr}", f"`{new_head}` — узел с детьми: голова с "
                                                                      "двоеточием")
        me = {"head": new_head}
        me.update({k: v for k, v in pairs if v is not None})
        me["type"] = name.split(":", 1)[1].split(".")[0] if prefix == "ui" else None
        me["part"] = name.split(":", 1)[1].split(".")[1] if prefix == "ui" and "." in name else None
        me["prefix"] = prefix
        for e in keep_struct:
            if e.key == "columns" and e.seq:
                self.fix_columns(e, me, ptr, anc + [me])
            if e.key == "children" and e.seq:
                self.fix_nodes(e.seq, f"{ptr}/children", anc + [me], state)
            if e.key == "fill" and e.map:
                for fe in e.map:
                    if fe.seq:
                        self.fix_nodes(fe.seq, f"{ptr}/fill/{fe.key}", anc + [me], state)
        self.fix_nodes(n.children, f"{ptr}/{T.esc(new_head)}", anc + [me], state)

    def fix_head(self, head, fills, parent, ptr):
        run, rec = self.run, self.rec
        name, pairs = _tokens(head)
        if ":" not in name:
            return head
        prefix, nm = name.split(":", 1)
        if prefix == "ui":
            t, _, part = nm.partition(".")
            types = run.comps.types
            ext = run.lay.design.extensions
            if t not in types and t not in ext:
                fixed = run.comps.type_of(t) or next((k for k in types if k.lower() == t.lower()), None)
                if fixed:
                    to = fixed + ("." + part if part else "")
                    run.change("R-STRUCT-021", rec, f"{rec.slug}#{ptr}", f"ui:{nm} → ui:{to}"
                               + (" (имя из aka словаря)" if run.comps.type_of(t) else " (регистр типа словаря)"))
                    nm = fixed + (f".{part}" if part else "")
                else:
                    run.todo("R-STRUCT-021", rec, f"{rec.slug}#{ptr}", f"ui:{nm} — типа нет в словаре и расширениях: "
                                                                       "выбрать тип словаря или завести расширение")
        allowed = T.ATTRS.get(prefix, ())
        under_grid = parent is not None and parent.get("head", "").startswith("layout:grid")
        out, keys = [], set()
        for k, v in pairs:
            if v is None:
                run.todo("R-STRUCT-020", rec, f"{rec.slug}#{ptr}",
                         f"`{head}` — «{k}» без значения: пара атрибут=значение")
                continue
            if prefix == "ui" and k == "variant":
                lvl = VARIANT_LEVEL.get(v)
                if lvl and not any(kk == "level" for kk, _ in pairs):
                    out.append(("level", lvl))
                    run.change("R-SEM-014", rec, f"{rec.slug}#{ptr}", f"variant={v} → level={lvl}")
                    run.todo("R-SEM-014", rec, f"{rec.slug}#{ptr}", f"level={lvl} из variant={v}: уровень действия — "
                                                                    "проверить по матрице действий (ux 04/10 §1.2)")
                else:
                    run.change("R-SEM-014", rec, f"{rec.slug}#{ptr}", f"снят variant={v}: вид решает дизайн-система")
                continue
            if k not in allowed and not (k == "span" and under_grid):
                run.change("R-SEM-014", rec, f"{rec.slug}#{ptr}", f"снят {k}={v}: атрибута нет в закрытом списке "
                                                                  f"узла {prefix}:")
                if k != "size":
                    run.todo("R-SEM-014", rec, f"{rec.slug}#{ptr}", f"снят {k}={v} — если он нёс смысл, где ему место "
                                                                    "(облик — слой дизайна, уровень действия — level)")
                continue
            if k in keys:
                continue
            keys.add(k)
            out.append((k, v))
        if fills and "fills" not in keys:
            out.append(("fills", fills))
            run.change("R-STRUCT-020", rec, f"{rec.slug}#{ptr}", f"(fills: {fills}) → fills={fills} в голове узла")
        return f"{prefix}:{nm}" + "".join(f" {k}={v}" for k, v in out)

    def fix_columns(self, entry, owner_node, ptr, anc):
        run, rec = self.run, self.rec
        for i, n in enumerate(entry.seq):
            s = n.content
            if not (s.startswith("{") and s.endswith("}")):
                continue
            try:
                col = L._yaml().safe_load(s)
            except Exception:                           # noqa: BLE001
                continue
            if not isinstance(col, dict) or not isinstance(col.get("label"), str) or col["label"].startswith("text:"):
                continue
            field_ = str(col.get("field") or "")
            m = re.match(r"^data:[a-z0-9-]+\.([a-z0-9-]+)$", field_)
            element = m.group(1) if m else f"column-{i + 1}"
            roles = run.comps.roles(owner_node.get("type"), "Header") if owner_node.get("type") else []
            role = roles[0] if roles else "column-header"
            key, new = run.key_for(rec, element, role, col["label"], None)
            literal = col["label"]
            col["label"] = f"text:{key}"
            self.rewrite_item(n, "{" + ", ".join(f"{k}: {scalar(v)}" for k, v in col.items()) + "}")
            run.change("R-TX-003", rec, f"{rec.slug}#{ptr}/columns/{i}/label",
                       f"label «{literal}» → text:{key}" + (" (новая строка texts.md, assumed)" if new else
                                                            " (строка texts.md с тем же текстом)"))

    def role(self, anc, state):
        for a in reversed(anc):
            if a.get("prefix") == "layout":
                continue
            if a.get("prefix") == "ui" and a.get("type"):
                roles = self.run.comps.roles(a["type"], a.get("part"))
                if roles:
                    return roles[0]
            break
        return {"loading-initial": "status", "generating": "status", "error-load": "inline-message",
                "empty-first-run": "empty", "empty-filtered": "empty", "empty-cleared": "empty",
                "no-permission": "title", "not-found": "title"}.get(state or "", "body")

    def element(self, anc, state):
        for a in reversed(anc):
            if a.get("action"):
                return a["action"]
        if state:
            return state
        for a in reversed(anc):
            if a.get("prefix") == "ui" and a.get("type"):
                return kebab(a["type"] + (f".{a['part']}" if a.get("part") else ""))
        return "text"

    def result(self):
        out = []
        for no, line in enumerate(self.lines):
            if no in self.edit:
                if self.edit[no] is not None:
                    out.append(self.edit[no])
            else:
                out.append(line)
        return out


def normalize_block(run, rec, lines):
    """Строки блока YAML записи → строки после механических правок (правки и пункты владельцу — в run)."""
    fx = NodeFix(run, rec, lines)
    fls = lex(lines)
    top, _ = parse_map(fls, 0, fls[0].indent if fls else 0)
    for e in top:
        if e.key == "tree":
            if e.seq is not None:
                fx.fix_nodes(e.seq, "/tree", [])
            for area in e.map or []:
                if area.seq:
                    fx.fix_nodes(area.seq, f"/tree/{area.key}", [])
        elif e.key == "slot-fills":
            for slot in e.map or []:
                if slot.seq:
                    fx.fix_nodes(slot.seq, f"/slot-fills/{slot.key}", [])
        elif e.key == "states":
            siblings = {st.key for st in e.map or []}
            for st in e.map or []:
                key = fix_state_key(fx, st, siblings)
                if st.map:
                    for slot in st.map:
                        if slot.seq:
                            _state_nodes(fx, slot.seq, f"/states/{key}/{slot.key}", key)
                else:
                    fix_na(fx, st, key)
    return fx.result()


def _state_nodes(fx, nodes, ptr, key):
    """Узлы дельты: тексты вне компонента в no-permission и not-found — первый title, следующие body."""
    if key in ("no-permission", "not-found"):
        seen = [0]
        orig_role = fx.role

        def role(anc, state):
            r = orig_role(anc, state)
            if r == "title" and not any(a.get("prefix") == "ui" for a in anc):
                seen[0] += 1
                return "title" if seen[0] == 1 else "body"
            return r
        fx.role = role
        fx.fix_nodes(nodes, ptr, [], key)
        fx.role = orig_role
    else:
        fx.fix_nodes(nodes, ptr, [], key)


def fix_state_key(fx, st, siblings=()):
    run, rec = fx.run, fx.rec
    key = st.key
    if key in run.dict.key2id:
        return key
    syn = run.syn.get(key)
    if syn and syn["kind"] == "state":
        new = syn["to"][0]
        if new in siblings:
            run.todo("R-STRUCT-022", rec, f"{rec.slug}#/states/{key}", f"`{key}` и `{new}` оба в states: свести в "
                                                                       f"один ключ словаря вручную")
            return key
        pad, text, comment = fx.line_parts(st.line)
        rest = text.split(":", 1)[1] if ":" in text else ""
        fx.set_line(st.line, f"{pad}{new}:{rest}" + (f"  {comment}" if comment else ""))
        run.change("R-STRUCT-022", rec, f"{rec.slug}#/states/{key}", f"ключ `{key}` → `{new}` (таблица ключей "
                                                                     "мобильного слоя)")
        if len(syn["to"]) > 1:
            run.todo("R-STRUCT-022", rec, f"{rec.slug}#/states/{new}",
                     f"`{key}` → `{new}` по умолчанию; за ключом `{key}` и {', '.join(syn['to'][1:])} — проверить по "
                     "смыслу дельты")
        return new
    if syn and syn["kind"] == "ideal":
        run.todo("R-STRUCT-022", rec, f"{rec.slug}#/states/{key}",
                 f"`{key}` — идеальное состояние: у экрана это slot-fills; ключ убрать, дельту сверить со slot-fills")
    elif syn and syn["kind"] == "app" or key in T.APP_STATES:
        run.todo("R-STRUCT-022", rec, f"{rec.slug}#/states/{key}", f"`{key}` — состояние приложения: перенести в "
                                                                   "раздел «Состояния приложения» основного каркаса")
    else:
        run.todo("R-STRUCT-022", rec, f"{rec.slug}#/states/{key}",
                 f"`{key}` вне словаря состояний экрана: выбрать ключ словаря (ux 06/01 §2)")
    return key


def fix_na(fx, st, key):
    """«здесь не применимо» → 'не применимо: причина' (причина — из значения или комментария строки)."""
    run, rec = fx.run, fx.rec
    pad, text, comment = fx.line_parts(st.line)
    raw = st.value
    val = None
    if raw is not None:
        try:
            val = L._yaml().safe_load(raw)
        except Exception:                               # noqa: BLE001
            val = raw
    src = val if isinstance(val, str) else (comment.lstrip("#").strip() if raw is None and comment else None)
    if not isinstance(src, str):
        return
    m = NA_INPUT.match(src.strip())
    if not m:
        return
    reason = m.group("reason").strip()
    canon = f"не применимо: {reason}" if reason else "не применимо:"
    if isinstance(val, str) and val.strip() == canon:
        return
    new = f"{pad}{key}: '{canon.replace(chr(39), chr(39) * 2)}'"
    keep_comment = comment if raw is not None else ""
    fx.set_line(st.line, new + (f"  {keep_comment}" if keep_comment else ""))
    run.change("R-STRUCT-020", rec, f"{rec.slug}#/states/{key}", f"«{src.strip()}» → '{canon}'")
    if not reason:
        run.todo("R-SEM-011", rec, f"{rec.slug}#/states/{key}", f"`{key}`: «не применимо» без причины — причину пишет "
                                                                "аналитик")


# ------------------------------------------------------------------ записи, frontmatter, реестр, свод

def fences(lines):
    """Диапазоны блоков ```yaml``` тела: [(начало содержимого, конец)]."""
    out, i = [], 0
    start = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                start = j + 1
                break
    i = start
    while i < len(lines):
        if L.FENCE_OPEN.match(lines[i].strip()) and not lines[i].startswith((" ", "\t")):
            j = i + 1
            while j < len(lines) and lines[j].strip() != "```":
                j += 1
            out.append((i + 1, j))
            i = j + 1
            continue
        i += 1
    return out


def fm_range(lines):
    if lines and lines[0].strip() == "---":
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                return 1, j
    return None


def fix_transitions(run, rec, lines):
    fm = rec.fm
    t = fm.get("transitions-to-screen")
    if not isinstance(t, list) or not any(isinstance(x, str) for x in t):
        return lines
    r = fm_range(lines)
    if r is None:
        return lines
    a, b = r
    start = next((i for i in range(a, b) if lines[i].startswith("transitions-to-screen:")), None)
    if start is None:
        return lines
    end = start + 1
    while end < b and (lines[end].startswith((" ", "\t", "- ")) or not lines[end].strip()):
        end += 1
    items = [x if isinstance(x, dict) else {"to": x} for x in t]
    new = ["transitions-to-screen:"] + ["  - {" + ", ".join(f"{k}: {scalar(v)}" for k, v in x.items()) + "}"
                                        for x in items]
    run.change("R-STRUCT-006", rec, rec.slug, "transitions-to-screen: slug → запись {to: …}")
    for x in items:
        miss = [k for k in ("trigger", "keeps", "back") if L.is_empty(x.get(k)) and k not in x]
        if miss:
            run.todo("R-RT-003" if "back" in miss else "R-STRUCT-006", rec, rec.slug,
                     f"переход в `{x.get('to')}`: {', '.join(miss)} — пусто: чем вызван, что сохраняется, "
                     "как вернуться")
    return lines[:start] + new + lines[end:]


def screen_owner(run, rec):
    fm = rec.fm
    miss = [k for k in SCREEN_FIELDS if k not in fm or fm.get(k) is None or (isinstance(fm.get(k), str)
                                                                            and not fm[k].strip())]
    if str(fm.get("type") or "") in ("list", "master-detail") and ("url-state" not in fm or fm["url-state"] is None):
        miss.append("url-state")
    if miss:
        run.todo("R-SEM-008", rec, rec.slug, f"поля экрана пусты: {', '.join(miss)} — решает аналитик (прочерк — "
                                             "тоже его решение)")
    for i, x in enumerate(fm.get("transitions-to-screen") or [] if isinstance(fm.get("transitions-to-screen"),
                                                                                list) else []):
        if isinstance(x, dict):
            miss = [k for k in ("trigger", "keeps", "back") if k not in x]
            if miss:
                run.todo("R-RT-003" if "back" in miss else "R-STRUCT-006", rec,
                         f"{rec.slug}#/transitions-to-screen/{i}",
                         f"переход в `{x.get('to')}`: {', '.join(miss)} — пусто")


def normalize_record(run, rec):
    if rec.md is None:
        return None
    lines = rec.md.text.split("\n")
    for a, b in reversed(fences(lines)):
        block = lines[a:b]
        new = normalize_block(run, rec, block)
        if new != block:
            text = "\n".join(new) + "\n"
            try:
                data = L._yaml().safe_load(text)
            except Exception as e:                      # noqa: BLE001
                run.todo("R-STRUCT-020", rec, rec.slug, f"дерево после механических правок не разбирается "
                                                        f"({L._yaml_err(e)}) — привести вручную")
                continue
            if not isinstance(data, dict):
                continue
            lines = lines[:a] + new + lines[b:]
    if rec.kind == "screen":
        lines = fix_transitions(run, rec, lines)
        screen_owner(run, rec)
    if rec.kind == "shell":
        md = rec.md
        if "items=nav" not in md.text and re.search(r"ui:(Sidebar|TopBar|BottomNav)\b", md.text):
            run.todo("R-RT-004", rec, rec.slug, "у каркаса нет узла навигации items=nav: навигация основного каркаса — "
                                                "ui:Sidebar, ui:TopBar или ui:BottomNav с items=nav; боковая панель "
                                                "экрана — слот side")
    return "\n".join(lines)


def write_texts(run, path):
    """Новые строки реестра — в конец таблицы texts.md (нет файла — по форме)."""
    if not run.new_rows:
        return None
    rows = []
    for key, (role, text, action) in run.new_rows.items():
        cells = [f"`{key}`", f"`{role}`", text.replace("|", "\\|"), "", f"`{action}`" if action else "—", "—", "—",
                 "", "`assumed`"]
        rows.append("| " + " | ".join(cells) + " |")
    if path.is_file():
        lines = path.read_text(encoding="utf-8").split("\n")
        md = L.Md(path)
        t = md.table(("key",))
        if t is not None:
            last = (t.rows[-1].line if t.rows else t.line + 1) - 1
            lines = lines[:last + 1] + rows + lines[last + 1:]
        else:
            lines += ["", TEXT_HEADER, TEXT_SEP] + rows + [""]
        text = "\n".join(lines)
    else:
        text = "\n".join(["# texts", "", f"> Реестр текстов интерфейса поверхности `{run.lay.surface}` — форма "
                          "`docs/projects/_template/screens/_template/texts.md`.", "", TEXT_HEADER, TEXT_SEP]
                         + rows) + "\n"
    path.write_text(text, encoding="utf-8")
    return text


# ------------------------------------------------------------------ прогон в копии проекта

def plan(slug, surfaces, repo):
    """Нормализация в копии проекта → (временная папка, корень копии, изменения, пункты владельцу, [(путь, старый,
    новый)])."""
    src_root = docpaths.root(repo)
    src = docpaths.project(slug, repo=src_root)
    td = tempfile.TemporaryDirectory(prefix="ddd-normalize-")
    root = Path(td.name) / "root"
    shutil.copytree(src, root / "docs" / "projects" / slug)
    changes, owner = [], []
    for surf in surfaces:
        lay = L.Layer(slug, surf, root)
        run = Run(lay)
        for rec in list(lay.records(("shell", "block", "screen"))):
            new = normalize_record(run, rec)
            if new is not None and new != rec.md.text:
                rec.path.write_text(new, encoding="utf-8")
        write_texts(run, lay.texts_path)
        lay2 = L.Layer(slug, surf, root)
        if lay2.screens:
            text = M.render(lay2)
            if lay2.map is None or lay2.map.text != text:
                lay2.map_path.write_text(text, encoding="utf-8")
                run.changes.append(Item("R-RT-008", "map", "map", lay2.rel(lay2.map_path),
                                        "map.md " + ("создан по форме, свод собран по экранам" if lay2.map is None else
                                                     "— генерируемые разделы пересобраны по экранам")))
        if run.new_rows:
            run.owner.append(Item("R-TX-004", "texts", "texts", lay2.rel(lay2.texts_path),
                                  f"новые строки texts.md ({len(run.new_rows)}) — `assumed`: текст, maxlen и роль по "
                                  "месту проверить; утверждает владелец продукта",
                                  f"/screen-deep-dive {slug} {surf} texts"))
        for it in run.changes:
            changes.append((surf, it))
        for it in run.owner:
            owner.append((surf, it))
    diffs = []
    new_proj = root / "docs" / "projects" / slug
    for f in sorted(p for p in new_proj.rglob("*") if p.is_file()):
        rel = f.relative_to(new_proj)
        old = src / rel
        a = old.read_text(encoding="utf-8") if old.is_file() else None
        b = f.read_text(encoding="utf-8")
        if a != b:
            diffs.append((Path("docs", "projects", slug, rel).as_posix(), a, b))
    return td, root, changes, owner, diffs


def unified(diffs):
    out = []
    for path, a, b in diffs:
        out += difflib.unified_diff((a or "").splitlines(keepends=True), b.splitlines(keepends=True),
                                    fromfile=f"a/{path}" if a is not None else "/dev/null", tofile=f"b/{path}")
    return "".join(out)


def as_findings(items, severity):
    out = []
    for surf, it in items:
        out.append(F.Finding(it.rule, severity, surf, it.kind, it.ref, it.path, it.message, it.fix))
    return out


def run_cli(call):
    surfs = [call.surf.slug] if call.surf else [s.slug for s in call.surfaces if s.app]
    if not surfs:
        print(f"normalize: у проекта {call.slug} нет поверхностей кабинета", file=sys.stderr)
        return F.EXIT_USAGE
    td, root, changes, owner, diffs = plan(call.slug, surfs, call.repo)
    try:
        write = call.command == "build" and bool(getattr(call.args, "write", False))
        out = call.out if call.command == "build" else None
        written = False
        if write or out:
            base = call.repo if write else Path(out)
            for path, a, b in diffs:
                target = Path(base) / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(b, encoding="utf-8")
            written = bool(diffs)
        text = unified(diffs)
        if call.json:
            print(json.dumps({"project": call.slug, "surfaces": surfs,
                              "files": [{"path": p, "status": "created" if a is None else "changed"}
                                        for p, a, _ in diffs],
                              "changes": [f.as_dict() for f in as_findings(changes, "hint")],
                              "owner": [f.as_dict() for f in as_findings(owner, "warning")],
                              "diff": text, "written": written}, ensure_ascii=False, indent=1))
        else:
            if text:
                print(text, end="" if text.endswith("\n") else "\n")
            print(f"== механические правки: {len(changes)}")
            for surf, it in changes:
                print(f"  {it.rule:<13} {it.ref}: {it.message}")
            print(f"== владельцу: {len(owner)}")
            for surf, it in owner:
                print(f"  {it.rule:<13} {it.ref}: {it.message}")
            if not diffs:
                print("править нечего: слой по канону")
            elif written:
                print(f"записано файлов: {len(diffs)}" + (f" в {out}" if out and not write else ""))
            elif call.command == "build":
                print("дифф показан; записать — build … --write (или --out DIR)")
        if call.command == "check":
            return F.EXIT_FINDINGS if diffs else F.EXIT_OK
        return F.EXIT_OK
    finally:
        td.cleanup()


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return _selftest()
    ap = docpaths.parser("normalize", __doc__, commands=("check", "build"), surface="optional", accept=lambda s: s.app)
    ap.add_argument("--write", action="store_true", help="build: править файлы проекта по месту")
    call = docpaths.parse(ap, argv)
    try:
        return run_cli(call)
    except (F.ToolError, docpaths.DocPathError, RuntimeError, OSError) as e:
        print(f"normalize: {e}", file=sys.stderr)
        return F.EXIT_USAGE


# ------------------------------------------------------------------ самопроверка

def _selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    # разбор свободной записи: отступная запись и компактная — одно дерево
    old = ["tree:", "  block-header:   # шапка", "    - layout:row justify=between", "      - ui:Search",
           "      - ui:Button variant=accent size=lg", "        - icon:plus", "        - 'Новое'", "  block-body:",
           "    - ui:Table", "        items: data:study", "        columns:",
           "          - {field: data:study.name, label: 'Имя'}"]
    top, _ = parse_map(lex(old), 0, 0)
    hdr = top[0].map[0].seq[0]
    check("свободная запись: дети по отступу, структура под узлом",
          hdr.content == "layout:row justify=between" and [c.content for c in hdr.children] ==
          ["ui:Search", "ui:Button variant=accent size=lg"] and top[0].map[1].seq[0].struct[0].key == "items")
    check("комментарий строки отделяется", split_comment("block-header:   # шапка") == ("block-header:", "# шапка"))
    check("пары атрибутов склеиваются через «=»", _tokens("ui:Button level = primary action=x")[1] ==
          [("level", "primary"), ("action", "x")])
    check("значение YAML в строку: токен — как есть, фраза — в кавычках", scalar("requests-list") == "requests-list"
          and scalar("назад, крошки") == "'назад, крошки'" and scalar("data:study.name") == "data:study.name")
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("cabinet") as fx:
        td, root, changes, owner, diffs = plan(fx.slug, ["office"], fx.root)
        td.cleanup()
        check("чистый слой — пустой дифф, правок и пунктов владельцу нет", not diffs and not changes and not owner)
    with fixture_project.built("cabinet-freeform") as fx:
        td, root, changes, owner, diffs = plan(fx.slug, ["office"], fx.root)
        try:
            rules = {it.rule for _, it in changes}
            check("вольная форма: дифф в терминах канона — дерево, aka, атрибуты, состояния, тексты, переходы, свод",
                  diffs and {"R-STRUCT-020", "R-STRUCT-021", "R-SEM-014", "R-STRUCT-022", "R-TX-003", "R-STRUCT-006",
                             "R-RT-008"} <= rules)
            text = unified(diffs)
            check("дифф: ui:Search → ui:SearchInput, variant → level, (fills: …) → fills=, loading → loading-initial",
                  "ui:SearchInput" in text and "level=primary" in text and "fills=$main" in text and
                  "loading-initial:" in text)
            omsg = " ".join(it.message for _, it in owner)
            check("владельцу: пустые поля экрана, переход без back, выбор состояния, новые строки texts.md",
                  "type" in omsg and "back" in omsg and "loading" in omsg and "assumed" in omsg)
            lay = L.Layer(fx.slug, "office", root)
            items = T.check_layer(lay)
            errs = [f for f in items if f.severity == "error"]
            check("после записи во временной копии: tree check — 0 error"
                  + (f" (есть: {'; '.join(f.rule + ' ' + f.ref + ' ' + f.message for f in errs[:4])})" if errs else ""),
                  not errs)
            td2, root2, changes2, owner2, diffs2 = plan(fx.slug, ["office"], root)
            td2.cleanup()
            check("повторная нормализация приведённого слоя — пустой дифф", not diffs2)
        finally:
            td.cleanup()
        import subprocess
        with tempfile.TemporaryDirectory(prefix="ddd-norm-cwd-") as cwd:
            r = subprocess.run([sys.executable, str(HERE / "normalize.py"), "check", fx.slug, "office", "--repo",
                                str(fx.root), "--json"], cwd=cwd, capture_output=True, text=True)
            try:
                data = json.loads(r.stdout)
            except ValueError:
                data = {}
            check("check --json из чужой рабочей папки: код 1, дифф и списки, ничего не записано",
                  r.returncode == 1 and data.get("diff") and data.get("owner") and data.get("written") is False and
                  [F.Finding.from_dict(x) for x in data["changes"]])
            r = subprocess.run([sys.executable, str(HERE / "normalize.py"), "build", fx.slug, "office", "--repo",
                                str(fx.root), "--write"], cwd=cwd, capture_output=True, text=True)
            lay = L.Layer(fx.slug, "office", fx.root)
            errs = [f for f in T.check_layer(lay) if f.severity == "error"]
            check("build --write правит проект по месту: после записи tree check — 0 error", r.returncode == 0 and
                  not errs)
    print("normalize selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
