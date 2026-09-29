#!/usr/bin/env python3
"""screen_map — свод `map.md` поверхности кабинета: генерируемые разделы по полям экранов и проверки карты экранов и
маршрутов.

Форма — `docs/projects/_template/screens/_template/map.md`. Свод — разделы «Карта экранов», «Маршруты», «Навигация»:
их собирает утилита из полей экранов (`screens/<surface>/screens/*/index.md`), зон interface
(`interface/<surface>/zone.md`: `parent-zone`, `order`), дерева основного каркаса (узел навигации `items=nav`), постуры
пользователей (`user.md`) и блоков со своим источником. Решения поверхности — «Переход», «События», «Конвенции»,
«Узкий экран», «Решения» — пишет аналитик; утилита их не трогает и только проверяет.

Выводимые колонки (форма map.md, «Свод»):
  density           постура пользователей экрана (самая высокая плотность `user.md`, «Постура») с потолком типа:
                    формы — не выше средней, мастер — низкая; без постуры — по типу (данные `data/screens.yaml`)
  entry-points      старт (entrypoint: true), навигация (зона экрана — пункт навигации), `экран` — переход с другого
                    экрана или из потока; прочие пункты ячейки (письмо, уведомление, ссылка) — слова аналитика,
                    сборка их сохраняет
  independent-blocks  блоки экрана со своим источником (source: own)
  Навигация         пункты уровня 1 — корневые зоны с order, уровня 2 — их дочерние с order; строка — пункты одного
                    уровня с одинаковой видимостью; who — роли экранов зоны и её дочерних; active и narrow — слова
                    аналитика, сборка их сохраняет

    screen_map build <slug> [<surface>] [--repo DIR] [--out DIR] [--json]   пересобрать генерируемые разделы map.md
    screen_map check <slug> [<surface>] [--repo DIR] [--json]               проверки; ничего не пишет
    screen_map --selftest                                                    фикстуры кабинета, без сети

`build` пишет только генерируемые разделы (нет файла — создаёт его по форме с пустыми таблицами решений); `--out DIR`
кладёт результат в DIR/<surface>/map.md, не трогая проект. Из Python: `derive(Layer)` — строки свода, `graph(Layer)` —
переходы и достижимость, `render(Layer)` — текст map.md.

Правила (`.claude/skills/screen-audit/references/rules.md`):
  R-RT-001   маршрут не уникален на вьюпорте (кроме экранов одного потока на разных вьюпортах); нет строки-запрета
             «маршрутов вне списка нет»                                                       error
  R-RT-002   тупик: нет исходящих переходов и меньше двух действий «что дальше» (action=, ui:Link) в дереве;
             служебный экран — не тупик, если в нём есть путь                                  warning, error у stable
  R-RT-003   переход без обратного пути: back пуст                                            warning
  R-RT-004   навигация глубже нормы (error); пункт в двух панелях, узел items=nav в дереве экрана (warning)
  R-RT-005   list или master-detail без url-state                                             warning, error у stable
  R-RT-006   «Переход» пуст или у строки нет где живёт, срока, что переживает, как проверить
                                                                                             warning, error у stable map
  R-RT-007   при N и больше экранах все одного типа; экран без объекта без строки «Решений» с его `slug`   warning
  R-RT-008   свод map.md расходится с экранами: frontmatter, разделы, строки и значения     warning, error у stable map
  R-RT-009   строка авторского раздела без решения и основания; пустой раздел у stable-свода  hint, error у stable map
  R-COV-003  экран недостижим от стартовых экранов своих ролей (переходы, поток, навигация); нет ни одного
             стартового экрана — error                                                         hint, error у stable
  R-STRUCT-006  поле экрана вне перечня: type, access, url-state, indexed, entrypoint, viewport, записи переходов
                                                                                             error
  R-STRUCT-023  поле экрана в продуктовый слой в пустоту: object, тип параметра, main-task, key-action   error
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

SECTIONS = ("Карта экранов", "Маршруты", "Навигация", "Переход", "События", "Конвенции", "Узкий экран", "Решения")
GENERATED = SECTIONS[:3]
AUTHOR = SECTIONS[3:]
MAP_COLS = ("screen", "type", "object", "who", "main-task", "key-action", "density", "entry-points",
            "independent-blocks")
ROUTE_COLS = ("route", "screen", "params", "access", "url-state", "indexed")
NAV_COLS = ("level", "element", "items", "who", "active", "narrow")
TYPES = ("dashboard", "list", "object", "edit", "wizard", "settings", "master-detail", "canvas", "auth", "service")
ACCESS = ("public", "authenticated", "roles")
URL_STATE = ("tab", "page", "filters", "sort", "view", "panel")
VIEWPORTS = ("desktop", "mobile", "any")
TRANSITION_KEYS = ("to", "trigger", "keeps", "back")
DENSITY_RANK = {"low": 1, "medium": 2, "high": 3}
START, NAV = "старт", "навигация"
DATA = kbpaths.data("project", "screens.yaml")


_NORMS = None


def norms():
    """Числа норм утилиты — `scripts/project/data/screens.yaml`."""
    global _NORMS
    if _NORMS is None:
        try:
            _NORMS = L._yaml().safe_load(DATA.read_text(encoding="utf-8")) or {}
        except Exception as e:                          # noqa: BLE001 — битые данные утилиты — ошибка окружения
            raise F.ToolError(f"{DATA}: не разбирается — {L._yaml_err(e)}") from e
    return _NORMS


# ------------------------------------------------------------------ форма map.md

def form_parts():
    """Из формы канона: {раздел: {"tables": [(заголовок, разделитель)], "text": [строки вне таблиц]}} и порядок."""
    path = docpaths.template("screens", "_template", "map.md")
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^```markdown\n(.*?)^```", text, re.S | re.M)
    if not m:
        raise F.ToolError(f"{path}: нет блока формы ```markdown")
    out = {}
    for title, _, body in L.sections(m.group(1)):
        lines = body.splitlines()
        tables, other = [], []
        for i, line in enumerate(lines):
            if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|(\s*:?-{2,}:?\s*\|)+\s*$", lines[i + 1]):
                tables.append((line, lines[i + 1]))
            elif line.strip() and not line.startswith("|"):
                other.append(line)
        out[title] = {"tables": tables, "text": other}
    return out


_FORM = None


def form():
    global _FORM
    if _FORM is None:
        _FORM = form_parts()
    return _FORM


def forbid_line():
    lines = form().get("Маршруты", {}).get("text") or []
    return next((x for x in lines if x.startswith("Маршрутов вне")), "Маршрутов вне этого списка нет.")


# ------------------------------------------------------------------ вывод свода

def _list(v):
    if isinstance(v, list):
        return [str(x).strip() for x in v if not L.is_empty(x)]
    if isinstance(v, str) and not L.is_empty(v):
        return [x.strip() for x in v.strip("[]").split(",") if x.strip() and not L.is_empty(x.strip())]
    return []


def _scalar(v):
    return None if L.is_empty(v) else str(v).strip()


def _params(v):
    if isinstance(v, dict) and v:
        return {str(k): str(x) for k, x in v.items()}
    return None


def transitions(fm):
    """Записи переходов экрана: [{to, trigger, keeps, back}] (строка — запись только с to)."""
    out = []
    for t in fm.get("transitions-to-screen") or [] if isinstance(fm.get("transitions-to-screen"), list) else []:
        if isinstance(t, dict):
            out.append({k: t.get(k) for k in t})
        elif isinstance(t, str) and not L.is_empty(t):
            out.append({"to": t.strip()})
    return out


@dataclass
class Derived:
    screens: dict = field(default_factory=dict)         # slug → строка «Карты экранов» (значения)
    routes: dict = field(default_factory=dict)          # slug → строка «Маршрутов»
    nav: list = field(default_factory=list)             # строки «Навигации»
    nav_zones: dict = field(default_factory=dict)       # зона → {"level", "order", "who"}
    zone_levels: dict = field(default_factory=dict)     # зона с order → уровень (и глубже нормы)
    edges: dict = field(default_factory=dict)           # slug → [цели]
    incoming: dict = field(default_factory=dict)        # slug → {источники}
    element: str | None = None


def zones_tree(lay):
    z = lay.interface.table("zone")
    parent = {s: r.value("parent-zone") for s, r in z.items()}
    order = {}
    for s, r in z.items():
        v = r.value("order")
        order[s] = int(v) if v and re.fullmatch(r"\d+", v) else None
    return z, parent, order


def subtree(zone, parent):
    out = {zone}
    changed = True
    while changed:
        changed = False
        for s, p in parent.items():
            if p in out and s not in out:
                out.add(s)
                changed = True
    return out


def _density(lay, fm, spec):
    who = _list(fm.get("who"))
    whos = lay.interface.table("who")
    users = []
    for w in who:
        row = whos.get(w)
        users += row.refs("users") if row else []
    best = 0
    for u, surf, row in lay.product.postures:
        if u in users and (surf is None or surf == lay.surface):
            best = max(best, DENSITY_RANK.get(str(row.value("density") or ""), 0))
    typ = str(fm.get("type") or "")
    if best == 0:
        best = DENSITY_RANK.get((spec.get("by_type") or {}).get(typ, ""), 0)
    cap = DENSITY_RANK.get((spec.get("cap") or {}).get(typ, ""), 3)
    best = min(best, cap) if best else 0
    words = spec.get("words") or {}
    inv = {v: k for k, v in DENSITY_RANK.items()}
    return words.get(inv.get(best), None) if best else None


def derive(lay, trees=None):
    trees = trees or T.parse_layer(lay)
    d = Derived()
    spec = (norms() or {}).get("density") or {}
    zrows, parent, order = zones_tree(lay)
    # уровни навигации: корневые зоны с order — 1, их дочерние с order — 2, глубже — дальше
    level = {}
    for s in zrows:
        if parent.get(s) is None and order.get(s) is not None:
            level[s] = 1
    changed = True
    while changed:
        changed = False
        for s in zrows:
            p = parent.get(s)
            if s not in level and p in level and order.get(s) is not None:
                level[s] = level[p] + 1
                changed = True
    d.zone_levels = level
    screens = lay.screens
    for slug, rec in screens.items():
        fm = rec.fm
        d.edges[slug] = [t["to"] for t in transitions(fm) if isinstance(t.get("to"), str) and t["to"].strip()]
    for rec in lay.flows.values():
        for t in rec.fm.get("transitions") or [] if isinstance(rec.fm.get("transitions"), list) else []:
            if isinstance(t, dict) and isinstance(t.get("from"), str) and isinstance(t.get("to"), str):
                d.edges.setdefault(t["from"], []).append(t["to"])
    for src, targets in d.edges.items():
        for t in targets:
            d.incoming.setdefault(t, set()).add(src)
    # навигация
    for z, lv in level.items():
        who = set()
        sub = subtree(z, parent)
        for slug, rec in screens.items():
            if _scalar(rec.fm.get("zone")) in sub:
                who |= set(_list(rec.fm.get("who")))
        d.nav_zones[z] = {"level": lv, "order": order[z], "who": who}
    _, nav = T.nav_node(trees)
    d.element = f"ui:{nav.name}" if nav is not None else None
    groups = {}
    for z, info in d.nav_zones.items():
        groups.setdefault((info["level"], frozenset(info["who"])), []).append(z)
    rows = []
    for (lv, who), zs in groups.items():
        zs.sort(key=lambda z: (d.nav_zones[z]["order"], z))
        rows.append({"level": lv, "element": d.element, "items": zs, "who": sorted(who),
                     "_order": min(d.nav_zones[z]["order"] for z in zs)})
    rows.sort(key=lambda r: (r["level"], r["_order"], r["items"]))
    d.nav = rows
    for slug, rec in screens.items():
        fm = rec.fm
        comp = T.composition(trees, slug, with_states=False) if slug in trees.screens else {"blocks": []}
        entry = []
        if fm.get("entrypoint") is True:
            entry.append(START)
        if _scalar(fm.get("zone")) in level:
            entry.append(NAV)
        entry += [f"`{s}`" for s in sorted(d.incoming.get(slug, ()))]
        d.screens[slug] = {
            "screen": slug, "type": _scalar(fm.get("type")), "object": _scalar(fm.get("object")),
            "who": _list(fm.get("who")), "main-task": _scalar(fm.get("main-task")),
            "key-action": _scalar(fm.get("key-action")), "density": _density(lay, fm, spec), "entry-points": entry,
            "independent-blocks": [b for b in comp["blocks"] if T.is_own(trees, b)]}
        d.routes[slug] = {
            "route": _scalar(fm.get("route")), "screen": slug, "params": _params(fm.get("params")),
            "access": _scalar(fm.get("access")), "url-state": _list(fm.get("url-state")),
            "indexed": "true" if fm.get("indexed") is True else "false"}
    return d


# ------------------------------------------------------------------ ячейки

def c(v):
    return f"`{v}`" if v else "—"


def clist(vs):
    return "`` [" + ", ".join(f"`{v}`" for v in vs) + "] ``" if vs else "—"


def cparams(p):
    return "`{" + ", ".join(f"{k}: {v}" for k, v in p.items()) + "}`" if p else "—"


def cplain(vs):
    return "[" + ", ".join(vs) + "]" if vs else "—"


def entry_items(cell):
    """Ячейка entry-points → пункты по порядку (текст как есть)."""
    v = (cell or "").strip()
    if L.is_empty(v):
        return []
    v = v[1:-1] if v.startswith("[") and v.endswith("]") else v
    return [x.strip() for x in v.split(",") if x.strip() and not L.is_empty(x.strip())]


def is_derived_entry(item):
    return item in (START, NAV) or bool(re.fullmatch(r"`[a-z0-9-]+`", item))


def parse_params(cell):
    v = L.cell(cell)
    if not v:
        return None
    try:
        data = L._yaml().safe_load(v)
    except Exception:                                   # noqa: BLE001 — нечитаемая ячейка сравнивается текстом
        return {"?": v}
    return {str(k): str(x) for k, x in data.items()} if isinstance(data, dict) and data else None


# ------------------------------------------------------------------ разбор и сборка файла

def split_file(text):
    """Текст map.md → (преамбула — строки до первого `## `, [(строка заголовка, строки раздела)])."""
    lines = text.split("\n")
    pre, secs, cur, fence = [], [], None, False
    for line in lines:
        if line.strip().startswith("```"):
            fence = not fence
        if not fence and line.startswith("## "):
            cur = (line, [])
            secs.append(cur)
            continue
        (cur[1] if cur else pre).append(line)
    return pre, secs


def join_file(pre, secs):
    lines = list(pre)
    for head, body in secs:
        lines.append(head)
        lines += body
    return "\n".join(lines)


def existing_rows(body_lines, key):
    """Строки первой таблицы раздела → {ключ: Row}; key(Row) → ключ или None."""
    out = {}
    for t in L.tables("\n".join(body_lines))[:1]:
        for r in t.rows:
            k = key(r)
            if k is not None:
                out[k] = r
    return out


def _nav_key(level, items):
    return (str(level), frozenset(items))


def _map_body(d, old):
    rows = existing_rows(old, lambda r: L.cell(r.get("screen")))
    head, sep = form()["Карта экранов"]["tables"][0]
    out = ["", head, sep]
    for slug in sorted(d.screens):
        s = d.screens[slug]
        authored = [x for x in entry_items(rows[slug].get("entry-points")) if not is_derived_entry(x)] \
            if slug in rows else []
        out.append("| " + " | ".join([c(slug), c(s["type"]), c(s["object"]), clist(s["who"]), c(s["main-task"]),
                                      c(s["key-action"]), s["density"] or "—", cplain(s["entry-points"] + authored),
                                      clist(s["independent-blocks"])]) + " |")
    return out + [""]


def _routes_body(d, old):
    head, sep = form()["Маршруты"]["tables"][0]
    out = ["", head, sep]
    for slug in sorted(d.routes, key=lambda s: (d.routes[s]["route"] or "", s)):
        r = d.routes[slug]
        out.append("| " + " | ".join([c(r["route"]), c(slug), cparams(r["params"]), c(r["access"]),
                                      cplain(r["url-state"]), c(r["indexed"])]) + " |")
    return out + ["", forbid_line(), ""]


def _nav_body(d, old):
    rows = existing_rows(old, lambda r: _nav_key(L.cell(r.get("level")), L.refs(r.get("items"))))
    head, sep = form()["Навигация"]["tables"][0]
    out = ["", head, sep]
    for n in d.nav:
        prev = rows.get(_nav_key(n["level"], n["items"]))
        active = (prev.get("active") or "").strip() if prev else ""
        narrow = (prev.get("narrow") or "").strip() if prev else ""
        out.append("| " + " | ".join([str(n["level"]), c(n["element"]), clist(n["items"]), clist(n["who"]),
                                      active, narrow]) + " |")
    return out + [""]


BUILDERS = {"Карта экранов": _map_body, "Маршруты": _routes_body, "Навигация": _nav_body}


def render(lay, trees=None):
    """Текст map.md с пересобранными генерируемыми разделами (нет файла — по форме)."""
    d = derive(lay, trees)
    if lay.map is not None:
        pre, secs = split_file(lay.map.text)
    else:
        pre = ["---", f"surface: {lay.surface}", "status: draft", "---", "", "# map", ""]
        secs = []
        for title in AUTHOR:
            body = [""]
            for h, s in form()[title]["tables"]:
                body += [h, s, ""]
            secs.append((f"## {title}", body))
    have = [h[3:].strip() for h, _ in secs]
    for title in GENERATED:
        if title in have:
            continue
        later = [i for i, t in enumerate(have) if t in SECTIONS and SECTIONS.index(t) > SECTIONS.index(title)]
        at = later[0] if later else len(secs)
        secs.insert(at, (f"## {title}", []))
        have.insert(at, title)
    new = []
    for h, body in secs:
        title = h[3:].strip()
        if title in BUILDERS:
            body = BUILDERS[title](d, body)
        new.append((h, body))
    text = join_file(pre, new)
    if not text.endswith("\n"):
        text += "\n"
    return text


def build(lay, out_dir=None):
    """Пересобрать map.md → {"path", "changed", "created"}."""
    text = render(lay)
    target = lay.map_path if out_dir is None else Path(out_dir) / lay.surface / "map.md"
    old = target.read_text(encoding="utf-8") if target.is_file() else None
    changed = old != text
    if changed:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return {"surface": lay.surface, "path": lay.rel(target), "changed": changed, "created": old is None}


# ------------------------------------------------------------------ проверки

class MapChecker:
    def __init__(self, lay):
        self.lay = lay
        self.trees = T.parse_layer(lay)
        self.chk = T.Checker(lay, self.trees)
        self.d = derive(lay, self.trees)
        self.norms = norms() or {}
        self.map_status = str((lay.map.fm or {}).get("status") or "") if lay.map is not None else None
        self.sections = {}
        if lay.map is not None:
            _, secs = split_file(lay.map.text)
            self.sections = {h[3:].strip(): body for h, body in secs}

    # находка по map.md
    def madd(self, rule, severity, ref, message):
        path = self.lay.rel(self.lay.map_path) if self.lay.map is not None else self.lay.rel(self.lay.folder)
        self.chk.rep.add(rule, severity, surface=self.lay.surface, kind="map", ref=f"map#{ref}", path=path,
                         message=message, fix=f"/screen-deep-dive {self.lay.slug} {self.lay.surface} map")

    def sadd(self, rule, severity, slug, pointer, message):
        self.chk.add(rule, severity, self.trees.screens[slug], pointer, message)

    def run(self):
        for slug in self.trees.screens:
            self.fields(slug)
        self.routes()
        self.dead_ends()
        self.nav()
        self.template_and_object()
        self.map_sync()
        self.transition_section()
        self.author_sections()
        self.reachability()
        return self.chk.rep.items

    # R-STRUCT-006, R-STRUCT-023, R-RT-003, R-RT-005
    def fields(self, slug):
        rec = self.lay.screens[slug]
        fm = rec.fm
        prod = self.lay.product
        bad = []
        for key, allowed in (("type", TYPES), ("access", ACCESS), ("viewport", VIEWPORTS)):
            v = fm.get(key)
            if v is not None and not L.is_empty(v) and str(v) not in allowed:
                bad.append(f"{key}: {v} — вне {' · '.join(allowed)}")
        us = fm.get("url-state")
        if us is not None and not L.is_empty(us):
            extra = [x for x in _list(us) if x not in URL_STATE]
            if not isinstance(us, list) or extra:
                bad.append(f"url-state: подмножество [{', '.join(URL_STATE)}] или «—», не {us}")
        for key in ("indexed", "entrypoint"):
            v = fm.get(key)
            if v is not None and not isinstance(v, bool):
                bad.append(f"{key}: true или false, не {v}")
        tts = fm.get("transitions-to-screen")
        if tts is not None and not L.is_empty(tts):
            if not isinstance(tts, list):
                bad.append("transitions-to-screen — список записей {to, trigger, keeps, back}")
            else:
                for i, t in enumerate(tts):
                    if not isinstance(t, dict):
                        bad.append(f"transitions-to-screen[{i}] `{t}` — запись {{to, trigger, keeps, back}}")
                    elif set(t) - set(TRANSITION_KEYS) or "to" not in t:
                        bad.append(f"transitions-to-screen[{i}] — ключи {', '.join(TRANSITION_KEYS)} (to обязателен)")
        for b in bad:
            self.sadd("R-STRUCT-006", "error", slug, "", b)
        # поля экрана в продуктовый слой
        obj = _scalar(fm.get("object"))
        if obj and prod.has_objects and obj not in prod.objects:
            self.sadd("R-STRUCT-023", "error", slug, "", f"object: объекта `{obj}` нет в object.md")
        params = fm.get("params")
        if isinstance(params, dict):
            import states as S
            for name, typ in params.items():
                t = str(typ or "").strip()
                base = t[4:] if t.startswith("ref:") else t
                if prod.has_objects and base not in prod.objects and base not in S.PRIMITIVE_TYPES:
                    self.sadd("R-STRUCT-023", "error", slug, "", f"params.{name}: `{t}` — не объект object.md и не "
                                                                  "тип атрибута")
        mt = _scalar(fm.get("main-task"))
        cap_file = docpaths.layer(self.lay.slug, "capability", self.lay.surface, self.lay.repo)
        if mt and cap_file.is_file() and mt not in prod.capabilities:
            self.sadd("R-STRUCT-023", "error", slug, "", f"main-task: возможности `{mt}` нет в "
                                                          f"capability/{self.lay.surface}.md")
        ka = _scalar(fm.get("key-action"))
        if ka and prod.has_actions and ka not in prod.actions:
            self.sadd("R-STRUCT-023", "error", slug, "", f"key-action: действия `{ka}` нет в action.md")
        # R-RT-003
        for i, t in enumerate(transitions(fm)):
            if L.is_empty(t.get("back")):
                self.sadd("R-RT-003", "warning", slug, f"/transitions-to-screen/{i}",
                          f"переход в `{t.get('to')}` без обратного пути: back пуст — как вернуться или irreversible")
        # R-RT-005
        if str(fm.get("type") or "") in ("list", "master-detail") and not _list(fm.get("url-state")):
            self.sadd("R-RT-005", F.severity_for(rec.status), slug, "",
                      f"экран `{fm.get('type')}` без url-state: фильтры, сортировка, страница, панель — что есть на "
                      "экране")

    # R-RT-001
    def routes(self):
        by_route = {}
        for slug, r in self.d.routes.items():
            if r["route"]:
                by_route.setdefault(r["route"], []).append(slug)
        flows = self.lay.flows
        for route, slugs in sorted(by_route.items()):
            if len(slugs) < 2:
                continue
            ok = False
            for f in flows.values():
                desk, mob = set(_list(f.fm.get("desktop"))), set(_list(f.fm.get("mobile")))
                if set(slugs) <= desk | mob and len(set(slugs) & desk) <= 1 and len(set(slugs) & mob) <= 1:
                    ok = True
            if not ok:
                self.madd("R-RT-001", "error", f"Маршруты/{route}",
                          f"маршрут `{route}` у экранов {', '.join(f'`{s}`' for s in sorted(slugs))}: один маршрут — "
                          "один экран на вьюпорт (общий — только у экранов одного потока на разных вьюпортах)")
        if self.lay.map is not None and "Маршруты" in self.sections:
            if not any(line.startswith("Маршрутов вне") for line in self.sections["Маршруты"]):
                self.madd("R-RT-001", "error", "Маршруты", f"нет строки-запрета: «{forbid_line()}»")

    # R-RT-002
    def dead_ends(self):
        mobile_series = set()
        for f in self.lay.flows.values():
            for t in f.fm.get("transitions") or [] if isinstance(f.fm.get("transitions"), list) else []:
                if isinstance(t, dict) and isinstance(t.get("from"), str):
                    mobile_series.add(t["from"])
        for slug, p in self.trees.screens.items():
            if self.d.edges.get(slug) or slug in mobile_series:
                continue
            nodes = T.screen_nodes(self.trees, slug, with_states=False)
            nxt = [n.head for n in nodes if "action" in n.attrs or n.ui_type == "Link"]
            service = str(p.record.fm.get("type") or "") == "service"
            if (service and nxt) or len(nxt) >= 2:
                continue
            self.sadd("R-RT-002", F.severity_for(p.record.status), slug, "",
                      "тупик: у экрана нет исходящих переходов, а в дереве "
                      + (f"одно действие «что дальше» ({nxt[0]})" if nxt else "нет действий «что дальше»")
                      + " — назвать переходы или два и больше действий (action=, ui:Link)")

    # R-RT-004
    def nav(self):
        norm = int(((self.norms.get("nav_levels_max") or {}).get("value")) or 2)
        deep = {z: lv for z, lv in self.d.zone_levels.items() if lv > norm}
        if deep:
            self.madd("R-RT-004", "error", "Навигация", f"видимых уровней навигации больше нормы ({norm}): "
                      + ", ".join(f"`{z}` — уровень {lv}" for z, lv in sorted(deep.items()))
                      + " — поднять в зоны выше или во вкладки объекта")
        rows = []
        for t in L.tables("\n".join(self.sections.get("Навигация", [])))[:1]:
            rows = t.rows
        seen = {}
        for r in rows:
            el = L.cell(r.get("element"))
            for z in L.refs(r.get("items")):
                if z in seen and seen[z] != el:
                    self.madd("R-RT-004", "warning", f"Навигация/{z}",
                              f"пункт `{z}` в двух панелях ({seen[z]}, {el}): один путь к разделу")
                seen.setdefault(z, el)
        for slug, p in self.trees.screens.items():
            for _, nodes in p.roots():
                for n, _ in T.walk(nodes):
                    if T.is_nav(n):
                        self.sadd("R-RT-004", "warning", slug, n.pointer,
                                  f"`{n.head}` — навигация в дереве экрана: узел навигации живёт в основном каркасе")

    # R-RT-007
    def template_and_object(self):
        n_min = int(((self.norms.get("same_type_min_screens") or {}).get("value")) or 4)
        types = [str(r.fm.get("type") or "") for r in self.lay.screens.values()]
        if len(types) >= n_min and len(set(types)) == 1:
            self.madd("R-RT-007", "warning", "Карта экранов", f"все {len(types)} экранов — `{types[0]}`: типы по "
                                                             "задачам, одинаковая структура — признак шаблона")
        decisions = "\n".join(self.sections.get("Решения", []))
        for slug, rec in self.lay.screens.items():
            if _scalar(rec.fm.get("object")):
                continue
            if f"`{slug}`" in decisions:
                continue
            no_role = not _list(rec.fm.get("who"))
            self.sadd("R-RT-007", "warning", slug, "",
                      "экран без объекта" + (" и без роли" if no_role else "") + f": нет строки «Решений» map.md с "
                      f"`{slug}` и причиной")

    # R-RT-008
    def map_sync(self):
        lay = self.lay
        screens = self.lay.screens
        if not screens:
            return
        if lay.map is None:
            sev = "error" if any(r.stable for r in screens.values()) else "warning"
            self.madd("R-RT-008", sev, "", "нет map.md у поверхности с экранами — собрать свод: screen_map build")
            return
        sev = F.severity_for(self.map_status)
        fm = lay.map.fm or {}
        if lay.map.fm_error:
            self.madd("R-RT-008", sev, "", lay.map.fm_error)
        if str(fm.get("surface") or "") != lay.surface:
            self.madd("R-RT-008", sev, "", f"frontmatter: surface — `{lay.surface}` (slug папки), не "
                                           f"`{fm.get('surface')}`")
        if str(fm.get("status") or "") not in ("draft", "stable"):
            self.madd("R-RT-008", sev, "", f"frontmatter: status — draft или stable, не `{fm.get('status')}`")
        missing = [s for s in SECTIONS if s not in self.sections]
        if missing:
            self.madd("R-RT-008", sev, "", "нет разделов формы: " + ", ".join(f"«{s}»" for s in missing))
        # Карта экранов
        rows = existing_rows(self.sections.get("Карта экранов", []), lambda r: L.cell(r.get("screen")))
        for slug, want in self.d.screens.items():
            r = rows.get(slug)
            if r is None:
                self.madd("R-RT-008", sev, f"Карта экранов/{slug}", f"нет строки экрана `{slug}`")
                continue
            got = {"type": L.cell(r.get("type")), "object": L.cell(r.get("object")),
                   "who": sorted(L.refs(r.get("who"))),
                   "main-task": L.cell(r.get("main-task")), "key-action": L.cell(r.get("key-action")),
                   "density": L.cell(r.get("density")),
                   "entry-points": sorted(x for x in entry_items(r.get("entry-points")) if is_derived_entry(x)),
                   "independent-blocks": sorted(L.refs(r.get("independent-blocks")))}
            exp = dict(want, who=sorted(want["who"]), **{"entry-points": sorted(want["entry-points"]),
                                                          "independent-blocks": sorted(want["independent-blocks"])})
            diff = [f"{k}: в своде {self._show(got[k])}, у экрана {self._show(exp[k])}"
                    for k in got if got[k] != exp[k]]
            if diff:
                self.madd("R-RT-008", sev, f"Карта экранов/{slug}", f"строка `{slug}` расходится с экраном — "
                                                                    + "; ".join(diff))
        for slug in rows:
            if slug not in self.d.screens:
                self.madd("R-RT-008", sev, f"Карта экранов/{slug}", f"строка `{slug}` без экрана")
        # Маршруты
        rows = existing_rows(self.sections.get("Маршруты", []), lambda r: L.cell(r.get("screen")))
        for slug, want in self.d.routes.items():
            r = rows.get(slug)
            if r is None:
                self.madd("R-RT-008", sev, f"Маршруты/{slug}", f"нет строки маршрута экрана `{slug}`")
                continue
            got = {"route": L.cell(r.get("route")), "params": parse_params(r.get("params")),
                   "access": L.cell(r.get("access")), "url-state": sorted(L.refs(r.get("url-state"))),
                   "indexed": L.cell(r.get("indexed")) or "false"}
            exp = {"route": want["route"], "params": want["params"], "access": want["access"],
                   "url-state": sorted(want["url-state"]), "indexed": want["indexed"]}
            diff = [f"{k}: в своде {self._show(got[k])}, у экрана {self._show(exp[k])}"
                    for k in got if got[k] != exp[k]]
            if diff:
                self.madd("R-RT-008", sev, f"Маршруты/{slug}", f"маршрут экрана `{slug}` расходится — "
                                                               + "; ".join(diff))
        for slug in rows:
            if slug not in self.d.routes:
                self.madd("R-RT-008", sev, f"Маршруты/{slug}", f"строка маршрута `{slug}` без экрана")
        # Навигация
        rows = existing_rows(self.sections.get("Навигация", []),
                             lambda r: _nav_key(L.cell(r.get("level")), L.refs(r.get("items"))))
        want_keys = {}
        for n in self.d.nav:
            want_keys[_nav_key(n["level"], n["items"])] = n
        for k, n in want_keys.items():
            r = rows.get(k)
            items = ", ".join(n["items"])
            if r is None:
                self.madd("R-RT-008", sev, f"Навигация/{items}", f"нет строки навигации уровня {n['level']}: "
                                                                 f"{items} для {', '.join(n['who']) or '—'}")
                continue
            diff = []
            if L.cell(r.get("element")) != n["element"]:
                diff.append(f"element: в своде {L.cell(r.get('element'))}, в каркасе {n['element']}")
            if sorted(L.refs(r.get("who"))) != n["who"]:
                diff.append(f"who: в своде {sorted(L.refs(r.get('who')))}, у экранов зон {n['who']}")
            if diff:
                self.madd("R-RT-008", sev, f"Навигация/{items}", f"строка навигации {items} — " + "; ".join(diff))
        for k in rows:
            if k not in want_keys:
                self.madd("R-RT-008", sev, f"Навигация/{', '.join(sorted(k[1]))}",
                          f"строка навигации уровня {k[0]} ({', '.join(sorted(k[1]))}) без зон с order")

    @staticmethod
    def _show(v):
        if v is None or v == [] or v == {}:
            return "—"
        if isinstance(v, list):
            return "[" + ", ".join(v) + "]"
        if isinstance(v, dict):
            return "{" + ", ".join(f"{k}: {x}" for k, x in v.items()) + "}"
        return str(v)

    # R-RT-006
    def transition_section(self):
        if self.lay.map is None:
            return
        sev = F.severity_for(self.map_status)
        body = self.sections.get("Переход")
        if body is None:
            return                                      # нет раздела — R-RT-008
        ts = L.tables("\n".join(body))
        rows = ts[0].rows if ts else []
        if not rows:
            self.madd("R-RT-006", sev, "Переход", "раздел «Переход» пуст: что переживает переход, где живёт, срок и "
                                                  "как проверить")
            return
        for r in rows:
            empty = [col for col, v in r.cells.items() if L.is_empty(v)]
            if empty:
                what = L.cell(r.get("что")) or "?"
                self.madd("R-RT-006", sev, f"Переход/{what}", f"строка «{what}»: пусто — {', '.join(empty)}")

    # R-RT-009
    def author_sections(self):
        if self.lay.map is None:
            return
        sev = F.severity_for(self.map_status, draft="hint", stable="error")
        for title in ("События", "Конвенции", "Узкий экран", "Решения"):
            body = self.sections.get(title)
            if body is None:
                continue
            ts = L.tables("\n".join(body))
            if not any(t.rows for t in ts):
                if self.map_status == "stable":
                    self.madd("R-RT-009", sev, title, f"раздел «{title}» пуст у stable-свода")
                continue
            for ti, t in enumerate(ts):
                for r in t.rows:
                    vals = list(r.cells.items())
                    first = L.cell(vals[0][1]) if vals else None
                    if title == "Узкий экран" and ti == 0:
                        rest = [v for _, v in vals[1:]]
                        if not first or all(L.is_empty(v) for v in rest):
                            self.madd("R-RT-009", sev, f"{title}/{first or '?'}",
                                      f"«{title}», строка «{first or '?'}»: нет решения по пяти вопросам")
                        continue
                    empty = [col for col, v in vals if L.is_empty(v)]
                    if empty:
                        self.madd("R-RT-009", sev, f"{title}/{first or '?'}",
                                  f"«{title}», строка «{first or '?'}»: пусто — {', '.join(empty)} (решение и "
                                  "основание" + (", кто теряет" if title == "Решения" else "") + ")")

    # R-COV-003
    def reachability(self):
        screens = self.lay.screens
        if not screens:
            return
        starts = {}
        for slug, rec in screens.items():
            if rec.fm.get("entrypoint") is True:
                for w in _list(rec.fm.get("who")):
                    starts.setdefault(w, []).append(slug)
        if not starts:
            self.chk.add("R-COV-003", "error", None, "", "у поверхности с экранами нет ни одного стартового экрана "
                                                         "(entrypoint: true)",
                         f"/screen-deep-dive {self.lay.slug} {self.lay.surface}")
            return
        reach = {}
        for role, st in starts.items():
            seeds = list(st)
            for slug, rec in screens.items():
                z = _scalar(rec.fm.get("zone"))
                info = self.d.nav_zones.get(z)
                if info and role in info["who"] and role in _list(rec.fm.get("who")):
                    seeds.append(slug)
            seen, queue = set(), list(seeds)
            while queue:
                s = queue.pop(0)
                if s in seen:
                    continue
                seen.add(s)
                queue += [t for t in self.d.edges.get(s, []) if t not in seen]
            reach[role] = seen
        for slug, rec in screens.items():
            if str(rec.fm.get("type") or "") == "service":
                continue
            who = _list(rec.fm.get("who"))
            if any(slug in reach.get(w, ()) for w in who):
                continue
            why = "у экрана нет ролей (who)" if not who else \
                f"обход от стартовых экранов ролей {', '.join(who)} (переходы, поток, навигация) до него не дошёл"
            self.sadd("R-COV-003", F.severity_for(rec.status, draft="hint", stable="error"), slug, "",
                      f"экран недостижим: {why}")


def check_layer(lay):
    return MapChecker(lay).run()


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return _selftest()
    ap = docpaths.parser("screen_map", __doc__, commands=("build", "check"), surface="optional",
                         accept=lambda s: s.app)
    call = docpaths.parse(ap, argv)
    try:
        lays = T.layers_of(call)
        if not lays:
            print(f"screen_map: у проекта {call.slug} нет поверхностей кабинета", file=sys.stderr)
            return F.EXIT_USAGE
        if call.command == "check":
            items = []
            for lay in lays:
                items += check_layer(lay)
            F.print_findings(items, as_json=call.json)
            return F.exit_code(items)
        results = []
        for lay in lays:
            if not lay.screens and lay.map is None:
                results.append({"surface": lay.surface, "path": None, "changed": False, "created": False,
                                "note": "экранов нет — свод не собирается"})
                continue
            results.append(build(lay, call.out))
        if call.json:
            print(json.dumps(results, ensure_ascii=False, indent=1))
        else:
            for r in results:
                if r.get("path") is None:
                    print(f"{r['surface']}: {r['note']}")
                else:
                    state = "создан" if r["created"] else ("пересобран" if r["changed"] else "без изменений")
                    print(f"{r['surface']}: {r['path']} — {state}")
        return F.EXIT_OK
    except (F.ToolError, docpaths.DocPathError, RuntimeError, OSError) as e:
        print(f"screen_map: {e}", file=sys.stderr)
        return F.EXIT_USAGE


# ------------------------------------------------------------------ самопроверка

EXPECT_DEFECTS = [("R-RT-001", "error", 1), ("R-RT-002", "error", 1), ("R-RT-008", "error", 1),
                  ("R-COV-003", "error", 1)]


def _selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    fp = form()
    check("форма map.md: восемь разделов, строка-запрет маршрутов", all(s in fp for s in SECTIONS) and
          forbid_line().startswith("Маршрутов вне этого списка нет"))
    check("ячейки: список, параметры, пункты входа", clist(["a", "b"]) == "`` [`a`, `b`] ``" and
          parse_params("`{id: request}`") == {"id": "request"} and
          entry_items("[старт, навигация, `a`, письмо]") == [START, NAV, "`a`", "письмо"])

    def extra(check, fx, lay):
        text = render(lay)
        check("build на чистом слое — без изменений (байт в байт)", text == lay.map.text)
        d = derive(lay)
        row = d.screens["requests-list"]
        check("карта: плотность по постуре и типу, пункты входа из графа", row["density"] == "высокая" and
              d.screens["request-new"]["density"] == "средняя" and START in row["entry-points"] and
              "`plan-dashboard`" in row["entry-points"])
        check("навигация: уровни зон с order, видимость по ролям экранов",
              [(n["level"], n["items"], n["who"]) for n in d.nav] ==
              [(1, ["requests"], ["manager", "surveyor"]), (1, ["plan"], ["manager"])])
        import tempfile
        with tempfile.TemporaryDirectory(prefix="ddd-map-") as td:
            res = build(lay, td)
            check("build --out: файл в DIR/<surface>/map.md, проект не тронут",
                  (Path(td) / "office" / "map.md").read_text(encoding="utf-8") == lay.map.text and res["created"])
            # без map.md — файл по форме; слова аналитика в сохраняемых ячейках переживают пересборку
            import shutil
            root = Path(td) / "r"
            shutil.copytree(fx.root, root)
            mp = root / "docs" / "projects" / fx.slug / "screens" / "office" / "map.md"
            mp.unlink()
            lay2 = L.Layer(fx.slug, "office", root)
            built = build(lay2)
            new = mp.read_text(encoding="utf-8")
            check("нет map.md — build создаёт его по форме: восемь разделов, status: draft",
                  built["created"] and all(f"## {s}" in new for s in SECTIONS) and "status: draft" in new)
            lay3 = L.Layer(fx.slug, "office", root)
            items = check_layer(lay3)
            check("созданный свод совпадает с экранами (R-RT-008 нет)", not [f for f in items if f.rule == "R-RT-008"])
            check("пустые разделы решений у draft-свода — подсказки, не error",
                  not [f for f in items if f.rule in ("R-RT-006", "R-RT-009") and f.severity == "error"])
            # остальные правила карты — синтетикой на копии чистого слоя
            root = Path(td) / "s"
            shutil.copytree(fx.root, root)
            base = root / "docs" / "projects" / fx.slug

            def edit(rel, old, new):
                p = base / rel
                text = p.read_text(encoding="utf-8")
                assert old in text, (rel, old)
                p.write_text(text.replace(old, new, 1), encoding="utf-8")

            scr = "screens/office/screens/"
            edit(scr + "requests-list/index.md", "url-state: [filters, sort, page]\n", "")
            edit(scr + "requests-list/index.md", "back: 'отмена возвращает сюда'", "back: ''")
            edit(scr + "request-new/index.md", "type: edit", "type: page")
            edit(scr + "request-card/index.md", "key-action: schedule", "key-action: publish")
            edit(scr + "request-card/index.md", "  loading-initial:\n    main:\n",
                 "  loading-initial:\n    main:\n      - ui:Sidebar items=nav\n")
            edit("interface/office/zone.md", "| `plan` | План замеров |",
                 "| `plan-week` | Неделя | План недели | `request-card` | 1 | `plan` | `draft` |\n"
                 "| `plan` | План замеров |")
            edit("interface/office/zone.md", "Одна заявка: данные и замер | `requests` | — |",
                 "Одна заявка: данные и замер | `requests` | 1 |")
            edit("screens/office/map.md", "| экран `not-found` без объекта |", "| служебный экран без объекта |")
            edit("screens/office/map.md", "| ошибку отправки | вызвать ошибку отправки: ни одно поле не очищено |",
                 "| ошибку отправки | — |")
            edit("screens/office/map.md", "| никто: разделов два |", "| — |")
            got = {(f.rule, f.severity) for f in check_layer(L.Layer(fx.slug, "office", root))}
            want = {("R-RT-003", "warning"), ("R-RT-004", "error"), ("R-RT-004", "warning"), ("R-RT-005", "error"),
                    ("R-RT-006", "error"), ("R-RT-007", "warning"), ("R-RT-009", "error"), ("R-STRUCT-006", "error"),
                    ("R-STRUCT-023", "error")}
            check("синтетика: R-RT-003, 004, 005, 006, 007, 009, R-STRUCT-006, R-STRUCT-023 срабатывают"
                  + (f" (нет: {sorted(want - got)})" if want - got else ""), want <= got)

    T.selftest_fixtures(check, run_check=check_layer, expect=EXPECT_DEFECTS, tool="screen_map", extra=extra)
    print("screen_map selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
