#!/usr/bin/env python3
"""ds_coverage — покрытие типов компонентов дизайн-системой продукта: экраны и планы → карта решений → артефакт ДС.

Цепочка одна (канон — `docs/projects/_template/design/README.md`, «Покрытие компонентов», «Расширения словаря»; правила
чтения — шапка `kb/common/components.yaml`, правила 1–5): каждый тип, который называет продукт, — ключ `components` или
id `extensions` карты решений `design/system.yaml`; его компонент есть в артефакте Design System
`design/_design-system/project/components/<Компонент>/` (README.md и preview.html) и нарисовал обязательные состояния
типа (`states.required` словаря) и объявленные необязательные (`optional_states` сопоставления).

Набор типов по роду поверхности:
  кабинет (web рода app, admin, desktop, embed) — типы `ui:` stable-экранов с блоками их слотов и каркасом
      (`tree.ui_types`); у находки — экраны, где тип стоит;
  сайт и лендинг (web рода landing, site) — типы слотов `action` и форм планов `site/<surface>/plans/*.yaml`
      (`components.yaml#outside`, «Блоки каталога сайта»): действие без формы — Button, `style: link | channel` — Link;
      форма — Button отправки, Field и поля набора `lead-forms.yaml#<набор>` по `type` (FIELD_TYPES ниже), отдельная
      галочка согласия и рассылки — Checkbox.
Состояния в превью: образец состояния — атрибут `data-state="<состояние>[ <состояние>]"` (имена — `element_states`
словаря); `rest` — у любого образца. На поверхности без указателя (`type: mobile` или `core.pointer.<surface>: touch`
брифа на вид) `hover` не требуется. Карточка компонента — в группе словаря (`@dsCard group` = `components.yaml#groups`).

    ds_coverage check <slug> [<surface>] [--repo DIR] [--stage ds-components|mockup] [--json]   находки
    ds_coverage show  <slug> [<surface>] [--repo DIR] [--json]    таблица покрытия со строкой заголовка:
        поверхность, тип, ключ (components · extensions), компонент, итог (ok · нет в артефакте · нет: состояния ·
        нет ключа), где стоит (экраны или страницы)
    ds_coverage --selftest                                         фикстуры cabinet-ds, minimal и схемы форм, без сети
Без <surface> — все поверхности кабинета и сайта проекта. Из Python: `coverage(slug, repo, surface, stage, screens)` →
строки покрытия (screens — партия экранов кабинета: типы только этих stable-экранов), `form_errors(kind, data)` →
ошибки формы уровня продукта по схеме `kb/common/<kind>.schema.yaml` (brand · system · app-brief).

Правило R-COV-005 (`.claude/skills/design-audit/references/rules.md`), тяжесть:
  error    только у поверхности кабинета на макете — у неё вход холста этапа mockup (`design/<surface>/input/INPUT.md`,
           поле stage) или вызов `--stage mockup`: тип без ключа components или extensions, компонента нет в
           артефакте; форма карты решений — два компонента на один тип; расширение без keyboard или text_roles, id
           расширения совпал с типом словаря или его aka, не в PascalCase, состояния вне словаря, роли text_roles вне
           списка (форма и расширения — уровень продукта: error, когда кабинет продукта на макете)
  warning  те же находки до макета кабинета (этап ds-components впереди) и у сайта и лендинга на любом этапе; не
           нарисовано состояние — на любом этапе; ключ components вне словаря, optional_states не из states.optional
           типа
  hint     карточка компонента не в группе словаря
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

KIND = "design-system"
RULE = "R-COV-005"
STAGES = ("ds-components", "mockup")
# тип поля набора lead-forms.yaml → тип словаря
FIELD_TYPES = {"text": "TextInput", "tel": "TextInput", "email": "TextInput", "url": "TextInput",
               "password": "TextInput", "search": "TextInput", "number": "NumberInput", "textarea": "Textarea",
               "radio": "RadioGroup", "select": "Select", "checkbox": "Checkbox", "file": "FileUpload",
               "date": "DatePicker"}
DSCARD = re.compile(r"<!--\s*@dsCard\b([^>]*)-->")
DATA_STATE = re.compile(r"""data-state\s*=\s*(?:"([^"]*)"|'([^']*)')""")
STAGE_LINE = re.compile(r"^\s*[-*]?\s*\**(?:stage|этап)\**\s*[:—–-]\s*`?([a-z-]+)`?", re.I | re.M)
PASCAL = re.compile(r"^[A-Z][A-Za-z0-9]*$")
FORMS = ("brand", "system", "app-brief")


# ------------------------------------------------------------------ формы уровня продукта по схемам

def _yaml():
    return L._yaml()


def schema(kind):
    """Схема формы уровня продукта `kb/common/<kind>.schema.yaml`."""
    if kind not in FORMS:
        raise ValueError(f"формы: {', '.join(FORMS)}, не {kind!r}")
    return _yaml().safe_load(kbpaths.kb(None, "common", f"{kind}.schema.yaml").read_text(encoding="utf-8"))


def registry():
    """Схемы, на которые ссылаются формы: brand, system, app-brief, meaning (text), site-brief (site)."""
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT202012
    docs = [schema(k) for k in FORMS]
    docs.append(_yaml().safe_load(kbpaths.kb("text", "02-strategy-messaging", "meaning.schema.yaml").read_text(
        encoding="utf-8")))
    docs.append(json.loads(kbpaths.kb("site", "10-playbooks-contracts", "schemas", "site-brief.schema.json").read_text(
        encoding="utf-8")))
    return Registry().with_resources([(d["$id"], Resource.from_contents(d, default_specification=DRAFT202012))
                                      for d in docs])


def form_errors(kind, data, reg=None):
    """Ошибки формы по схеме: [(JSON Pointer, сообщение)]; пусто — форма проходит."""
    import jsonschema
    v = jsonschema.Draft202012Validator(schema(kind), registry=reg or registry())
    out = []
    for e in sorted(v.iter_errors(data), key=lambda e: list(e.absolute_path)):
        ptr = "/" + "/".join(str(p) for p in e.absolute_path)
        out.append((ptr, e.message if len(e.message) < 200 else e.message[:197] + "…"))
    return out


# ------------------------------------------------------------------ чтение карты решений и артефакта

@dataclass
class System:
    path: Path
    data: dict = field(default_factory=dict)
    error: str | None = None
    duplicates: list = field(default_factory=list)          # [(тип, строка)] — дубли ключей components

    @property
    def exists(self):
        return self.path.is_file()

    @property
    def components(self):
        c = self.data.get("components")
        return {k: v for k, v in c.items() if isinstance(k, str) and not L.PLACEHOLDER.match(k)} \
            if isinstance(c, dict) else {}

    @property
    def extensions(self):
        out = {}
        items = self.data.get("extensions")
        for i, e in enumerate(items if isinstance(items, list) else []):
            if isinstance(e, dict) and isinstance(e.get("id"), str) and not L.PLACEHOLDER.match(e["id"]):
                out[e["id"]] = (i, e)
        return out


def load_system(path):
    s = System(Path(path))
    if not s.exists:
        return s
    text = s.path.read_text(encoding="utf-8")
    try:
        data = _yaml().safe_load(text)
    except Exception as e:                                    # noqa: BLE001 — yaml.YAMLError и ошибки конструктора
        s.error = "не разбирается как YAML: " + str(e).splitlines()[0]
        return s
    if not isinstance(data, dict):
        s.error = "не словарь YAML"
        return s
    s.data = data
    try:
        root = _yaml().compose(text)
    except Exception:                                         # noqa: BLE001
        root = None
    for k, v in (root.value if root is not None and hasattr(root, "value") and isinstance(root.value, list) else []):
        if getattr(k, "value", None) == "components" and hasattr(v, "value") and isinstance(v.value, list):
            seen = {}
            for kn, _ in v.value:
                if not hasattr(kn, "value"):
                    continue
                if kn.value in seen:
                    s.duplicates.append((kn.value, kn.start_mark.line + 1))
                seen[kn.value] = True
    return s


@dataclass
class Card:
    name: str
    folder: Path
    readme: bool
    preview: bool
    group: str | None = None
    states: set = field(default_factory=set)

    @property
    def exists(self):
        return self.readme and self.preview


def load_card(art_dir, name):
    d = Path(art_dir) / "components" / name
    c = Card(name, d, (d / "README.md").is_file(), (d / "preview.html").is_file())
    if c.preview:
        text = (d / "preview.html").read_text(encoding="utf-8", errors="replace")
        m = DSCARD.search(text)
        if m:
            g = re.search(r'group\s*=\s*"([^"]*)"', m.group(1))
            c.group = g.group(1) if g else None
        for a, b in DATA_STATE.findall(text):
            c.states.update(x for x in re.split(r"[\s,]+", a or b) if x)
        c.states.add("rest")
    return c


# ------------------------------------------------------------------ набор типов

@dataclass
class Use:
    type: str
    surface: str
    where: list                                             # экраны или страницы, где тип стоит
    touch: bool = False
    part_of: str = "screens"                                # screens · plans


def input_stage(slug, surface, repo):
    """Этап входа холста поверхности из input/INPUT.md: поле stage передней части или строка «этап: …»."""
    p = docpaths.design(slug, "input", surface=surface, repo=repo) / "INPUT.md"
    if not p.is_file():
        return None
    text = p.read_text(encoding="utf-8", errors="replace")
    m = re.match(r"^---[ \t]*\r?\n(.*?)\r?\n---", text, re.S)
    if m:
        s = re.search(r"^stage:\s*['\"]?([a-z-]+)", m.group(1), re.M)
        if s:
            return s.group(1)
    s = STAGE_LINE.search(text)
    return s.group(1).lower() if s else None


def touch_only(slug, surf, repo):
    if surf.type == "mobile":
        return True
    p = docpaths.design(slug, "app-brief", repo=repo)
    if not p.is_file():
        return False
    try:
        data = _yaml().safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:                                         # noqa: BLE001 — битый бриф проверяет его аудит
        return False
    ptr = ((data.get("core") or {}).get("pointer") or {}) if isinstance(data, dict) else {}
    return isinstance(ptr, dict) and ptr.get(surf.slug) == "touch"


def cabinet_uses(slug, surf, repo, screens=None):
    """{тип: Use} — типы `ui:` stable-экранов поверхности кабинета с экранами, где они стоят; screens — только эти
    экраны (партия входа холста)."""
    kbpaths.use("project")
    import tree as T
    lay = L.Layer(slug, surf.slug, repo)
    trees = T.parse_layer(lay)
    out = {}
    touch = touch_only(slug, surf, repo)
    for screen, p in trees.screens.items():
        if not p.record.stable or screens is not None and screen not in screens:
            continue
        types = {n.ui_type for n in T.screen_nodes(trees, screen) if n.ui_type}
        shell = trees.shells.get(str(p.record.fm.get("shell") or ""))
        if shell is not None:
            types |= {n.ui_type for n, _ in T.walk(shell.nodes) if n.ui_type}
        for t in types:
            out.setdefault(t, Use(t, surf.slug, [], touch)).where.append(screen)
    return out


def site_uses(slug, surf, repo):
    """{тип: Use} — типы слотов action и форм планов страниц сайта или лендинга."""
    plans = docpaths.site(slug, surf.slug, "plans", repo=repo)
    files = sorted(plans.glob("*.yaml")) if plans.is_dir() else []
    if not files:
        return {}
    forms = _lead_forms()
    out = {}
    touch = touch_only(slug, surf, repo)

    def add(t, page):
        u = out.setdefault(t, Use(t, surf.slug, [], touch, "plans"))
        if page not in u.where:
            u.where.append(page)

    for f in files:
        try:
            plan = _yaml().safe_load(f.read_text(encoding="utf-8")) or {}
        except Exception:                                     # noqa: BLE001 — битый план проверяет site_validate
            continue
        page = str(((plan.get("page") or {}) if isinstance(plan, dict) else {}).get("id") or f.stem)
        for sec in plan.get("sections") or [] if isinstance(plan, dict) else []:
            for a in ((sec or {}).get("slots") or {}).get("action") or []:
                if not isinstance(a, dict):
                    continue
                form = a.get("form")
                if isinstance(form, dict):
                    add("Button", page)
                    add("Field", page)
                    ref = str(form.get("ref") or "")
                    fset = forms["sets"].get(ref.split("#", 1)[1]) if "#" in ref else None
                    for fld in (fset or {}).get("fields") or []:
                        ftype = (forms["fields"].get((fld or {}).get("field")) or {}).get("type")
                        if ftype in FIELD_TYPES:
                            add(FIELD_TYPES[ftype], page)
                    if form.get("consent") == "separate-checkbox" or form.get("marketing_consent") is True:
                        add("Checkbox", page)
                elif a.get("style") in ("link", "channel"):
                    add("Link", page)
                else:
                    add("Button", page)
    return out


_FORMS = None


def _lead_forms():
    global _FORMS
    if _FORMS is None:
        data = _yaml().safe_load(kbpaths.kb("site", "05-conversion-funnels", "lead-forms.yaml").read_text(
            encoding="utf-8")) or {}
        _FORMS = {"fields": data.get("fields") or {},
                  "sets": {s.get("id"): s for s in data.get("form_sets") or [] if isinstance(s, dict)}}
    return _FORMS


# ------------------------------------------------------------------ сверка

@dataclass
class Row:
    """Строка покрытия: тип на поверхности → ключ карты решений → компонент артефакта → состояния."""
    use: Use
    key: str | None = None                                  # components · extensions · None
    component: str | None = None
    card: Card | None = None
    need: list = field(default_factory=list)                # состояния, которые нужно нарисовать
    missing: list = field(default_factory=list)


class Coverage:
    def __init__(self, slug, repo, surfaces, stage=None, screens=None):
        self.slug, self.repo, self.stage = slug, repo, stage
        self.surfaces = surfaces
        self.comps = L.components()
        self.groups = _yaml().safe_load(self.comps.path.read_text(encoding="utf-8")).get("groups") or {}
        self.element_states = set(_yaml().safe_load(self.comps.path.read_text(encoding="utf-8")).get(
            "element_states") or {})
        self.system = load_system(docpaths.design(slug, "system", repo=repo))
        self.art_dir = docpaths.design(slug, "ds-project", repo=repo)
        self.rep = F.Report()
        self.rows = []
        self.uses = {}
        for s in surfaces:
            u = cabinet_uses(slug, s, repo, screens) if s.app else site_uses(slug, s, repo) if s.page else {}
            if u:
                self.uses[s.slug] = u
        self._cards = {}

    def rel(self, p):
        return docpaths.rel(p, self.repo)

    def card(self, name):
        if name not in self._cards:
            self._cards[name] = load_card(self.art_dir, name)
        return self._cards[name]

    def gate(self, surface):
        """Покрытие держит макет только у кабинета: поверхность кабинета с входом mockup или вызов --stage mockup."""
        s = next((x for x in self.surfaces if x.slug == surface), None)
        return s is not None and s.app and (self.stage == "mockup"
                                            or input_stage(self.slug, surface, self.repo) == "mockup")

    def severity(self, surface):
        """Тип без ключа или компонента: error — у кабинета на макете, иначе warning (у сайта — всегда)."""
        return "error" if self.gate(surface) else "warning"

    def form_severity(self):
        """Форма карты решений и расширения — уровень продукта: error, когда кабинет продукта на макете (его вход mockup
        или вызов --stage mockup с кабинетом в проверке), иначе warning — одна тяжесть при любом охвате вызова."""
        if self.stage == "mockup" and any(s.app for s in self.surfaces):
            return "error"
        return "error" if any(s.app and input_stage(self.slug, s.slug, self.repo) == "mockup"
                              for s in docpaths.surfaces(self.slug, self.repo)) else "warning"

    def add(self, sev, ref, path, message, surface=None, fix=""):
        self.rep.add(RULE, sev, surface=surface, kind=KIND, ref=ref, path=self.rel(path), message=message, fix=fix)

    def run(self):
        sysp = self.system.path
        if not self.uses and not self.system.exists:
            return self
        if self.system.error:
            self.rep.add("R-STRUCT-008", "error", surface=None, kind=KIND, ref="system", path=self.rel(sysp),
                         message=f"system.yaml {self.system.error}", fix=f"/design-deep-dive {self.slug}")
            return self
        self.map_checks()
        for surface, uses in self.uses.items():
            if not self.system.exists:
                listed = ", ".join(sorted(uses))
                self.add(self.severity(surface), "system", sysp, f"нет карты решений design/system.yaml: "
                         f"типы без компонента ДС — {len(uses)} ({listed})", surface,
                         f"карта решений — этап design-system / ds-components: /design-deep-dive {self.slug}")
                continue
            for t in sorted(uses):
                self.use_checks(uses[t])
        return self

    # -- карта решений целиком

    def map_checks(self):
        sysp = self.system.path
        types = self.comps.types
        fsev = self.form_severity()
        for t, line in self.system.duplicates:
            self.add(fsev, f"system#/components/{t}", sysp, f"`{t}` — ключ components дважды (строка {line}): "
                     "два компонента ДС на один тип — две реализации одной потребности", fix="оставить один компонент")
        exts = self.system.extensions
        for t, spec in self.system.components.items():
            ref = f"system#/components/{t}"
            if not isinstance(spec, dict) or not isinstance(spec.get("component"), str) or \
                    L.PLACEHOLDER.match(spec.get("component") or ""):
                kind = "списком" if isinstance(spec, dict) and isinstance(spec.get("component"), list) else "не задан"
                sev = fsev if kind == "списком" else "warning"
                self.add(sev, ref, sysp, f"`{t}` — компонент ДС {kind}" + (": два компонента на один тип — дефект"
                                                                          if kind == "списком" else ""))
                continue
            if t not in types and t not in exts:
                aka = self.comps.type_of(t)
                self.add("warning", ref, sysp, f"`{t}` — ключ components вне словаря и расширений"
                         + (f": имя из aka, тип словаря — {aka}" if aka else ""),
                         fix="ключ — тип kb/common/components.yaml" + (f" ({aka})" if aka else "") +
                         " или id расширения")
            if t in exts and spec["component"] != t:
                self.add(fsev, ref, sysp, f"`{t}` — и расширение, и ключ components с компонентом "
                         f"{spec['component']}: два компонента на один тип")
            opt = spec.get("optional_states") or []
            tstates = (types.get(t) or {}).get("states") or (exts.get(t, (0, {}))[1].get("states") or {})
            for st in opt if isinstance(opt, list) else []:
                if st not in self.element_states:
                    self.add("warning", ref + "/optional_states", sysp,
                             f"`{t}` — optional_states: `{st}` — не состояние элемента словаря (element_states)")
                elif st in (tstates.get("required") or []):
                    self.add("warning", ref + "/optional_states", sysp,
                             f"`{t}` — optional_states: `{st}` обязательное у типа — обязательные сюда не копируются")
                elif st not in (tstates.get("optional") or []):
                    self.add("warning", ref + "/optional_states", sysp,
                             f"`{t}` — optional_states: `{st}` нет в states.optional типа "
                             f"({', '.join(tstates.get('optional') or []) or 'пусто'})")
        roles = L.text_roles_closed()
        for eid, (i, e) in exts.items():
            ref = f"system#/extensions/{i}"
            if eid in types or self.comps.type_of(eid):
                self.add(fsev, ref + "/id", sysp, f"расширение `{eid}` совпало с типом словаря "
                         f"{eid if eid in types else self.comps.type_of(eid)}: подходит тип словаря — берут его",
                         fix="ui: экрана — тип словаря; расширение снять")
            elif not PASCAL.match(eid):
                self.add(fsev, ref + "/id", sysp, f"расширение `{eid}` — id не в PascalCase")
            st = e.get("states") if isinstance(e.get("states"), dict) else {}
            for k in ("required", "optional"):
                bad = [x for x in st.get(k) or [] if x not in self.element_states]
                if bad:
                    self.add(fsev, ref + f"/states/{k}", sysp, f"расширение `{eid}` — states.{k}: "
                             f"{', '.join(bad)} — не состояния элемента словаря; своё состояние проект не заводит")
            if not st.get("required"):
                self.add("warning", ref + "/states/required", sysp, f"расширение `{eid}` — нет states.required")
            kb = e.get("keyboard")
            if not isinstance(kb, str) or not kb.strip() or L.PLACEHOLDER.match(kb.strip()):
                self.add(fsev, ref + "/keyboard", sysp,
                         f"расширение `{eid}` без клавиатурного контракта (keyboard): без него тип не принимается",
                         fix="keyboard — клавиши, порядок фокуса, роль ARIA")
            tr = e.get("text_roles")
            if not isinstance(tr, dict):
                self.add(fsev, ref + "/text_roles", sysp, f"расширение `{eid}` без text_roles: не работает проверка "
                         "«роль ключа текста = роль части»", fix="text_roles: {<Тип>.<Часть>: [<роль>]}; без текстовых "
                                                                "частей — {}")
                continue
            parts = [p for p in e.get("parts") or [] if isinstance(p, str)]
            for k, rl in tr.items():
                head, _, part = str(k).partition(".")
                if head != eid or (part and part not in parts):
                    self.add(fsev, ref + f"/text_roles/{k}", sysp, f"расширение `{eid}` — text_roles: ключ `{k}` — "
                             f"не тип и не его часть (parts: {', '.join(parts) or '—'})")
                bad = [r for r in (rl if isinstance(rl, list) else [rl]) if r not in roles]
                if bad:
                    self.add(fsev, ref + f"/text_roles/{k}", sysp, f"расширение `{eid}` — text_roles `{k}`: роли "
                             f"{', '.join(map(str, bad))} вне закрытого списка ux 07/06 §7.2 и body")

    # -- тип на поверхности

    def use_checks(self, u):
        sysp = self.system.path
        t = u.type
        types = self.comps.types
        exts = self.system.extensions
        spec = self.system.components.get(t)
        row = Row(u)
        self.rows.append(row)
        sev = self.severity(u.surface)
        where = f"{'экраны' if u.part_of == 'screens' else 'страницы'}: {', '.join(u.where)} ({u.surface})"
        if not isinstance(spec, dict) and t not in exts:
            aka_keys = [k for k in self.system.components if self.comps.type_of(k) == t]
            hint = f"; в components есть {aka_keys[0]} — имя из aka, тип словаря {t}" if aka_keys else ""
            outside = "" if t in types else "; типа нет и в словаре — tree check"
            self.add(sev, f"system#/components/{t}", sysp, f"`ui:{t}` — нет компонента ДС: ключа нет в components и "
                     f"extensions карты решений{hint}{outside}; {where}", u.surface,
                     f"сопоставить тип компоненту ДС — этап ds-components: /design-deep-dive {self.slug} {u.surface}")
            return
        if isinstance(spec, dict) and not isinstance(spec.get("component"), str):
            return                                            # форма ключа — находка map_checks
        row.key = "components" if isinstance(spec, dict) else "extensions"
        row.component = spec["component"] if isinstance(spec, dict) else t
        card = self.card(row.component)
        row.card = card
        if not card.exists:
            lack = [n for n, ok in (("README.md", card.readme), ("preview.html", card.preview)) if not ok]
            self.add(sev, f"artifact#components/{row.component}", self.art_dir / "components" / row.component,
                     f"`ui:{t}` → компонент {row.component}: его нет в артефакте ДС (нет {', '.join(lack)} в "
                     f"components/{row.component}/); {where}", u.surface,
                     f"компонент с превью состояний — этап ds-components: /design-deep-dive {self.slug}")
            return
        if t in types:
            st = types[t].get("states") or {}
        else:
            st = exts[t][1].get("states") or {}
        need = list(st.get("required") or [])
        declared = list((spec or {}).get("optional_states") or []) if isinstance(spec, dict) else []
        need += [x for x in declared if x not in need and x in (st.get("optional") or [])]   # прочее — map_checks
        if u.touch:
            need = [x for x in need if x != "hover"]
        row.need = need
        row.missing = [x for x in need if x not in card.states]
        if row.missing:
            req = [x for x in row.missing if x in (st.get("required") or [])]
            opt = [x for x in row.missing if x not in req]
            parts = ([f"обязательные типа {t}: {', '.join(req)}"] if req else []) + \
                    ([f"объявленные в optional_states: {', '.join(opt)}"] if opt else [])
            # не нарисованное в превью состояние — доклад на любом этапе: макет держат тип без ключа или компонента
            self.add("warning", f"artifact#components/{row.component}", card.folder / "preview.html",
                     f"`ui:{t}` → компонент {row.component}: в превью не нарисованы состояния — {'; '.join(parts)} "
                     f"(образец состояния — атрибут data-state); {where}", u.surface,
                     f"превью состояний компонента — этап ds-components: /design-deep-dive {self.slug}")
        if t in types:
            want = self.groups.get(types[t].get("group"))
            if want and card.group != want:
                self.add("hint", f"artifact#components/{row.component}", card.folder / "preview.html",
                         f"карточка {row.component} в группе «{card.group or '—'}», у типа {t} группа словаря — "
                         f"«{want}»",
                         u.surface, f'@dsCard group="{want}"')


def coverage(slug, repo=None, surface=None, stage=None, screens=None):
    """Покрытие ДС продукта: объект Coverage после сверки (`rows`, `rep.items`); screens — партия экранов кабинета."""
    r = docpaths.root(repo)
    surfs = [s for s in docpaths.surfaces(slug, r) if (s.app or s.page) and (surface is None or s.slug == surface)]
    return Coverage(slug, r, surfs, stage, screens).run()


def show(cov, as_json=False, out=None):
    out = out or sys.stdout
    rows = [{"surface": x.use.surface, "type": x.use.type, "where": x.use.where, "key": x.key,
             "component": x.component, "artifact": bool(x.card and x.card.exists), "states": x.need,
             "missing": x.missing} for x in cov.rows]
    uncovered = [{"surface": s, "type": t, "where": u.where} for s, us in cov.uses.items() for t, u in us.items()
                 if not any(x.use is u for x in cov.rows)]
    if as_json:
        print(json.dumps({"project": cov.slug, "rows": rows, "uncovered": uncovered}, ensure_ascii=False, indent=1),
              file=out)
        return
    line = "{:<12} {:<16} {:<11} {:<16} {:<16} {}"
    print(line.format("поверхность", "тип", "ключ", "компонент", "итог", "где стоит"), file=out)
    for r in rows:
        mark = "ok" if r["artifact"] and not r["missing"] else ("нет в артефакте" if not r["artifact"] else
                                                                  "нет: " + ", ".join(r["missing"]))
        print(line.format(r["surface"], r["type"], r["key"] or "—", r["component"] or "—", mark,
                          ", ".join(r["where"])), file=out)
    for u in uncovered:
        print(line.format(u["surface"], u["type"], "—", "—", "нет ключа", ", ".join(u["where"])), file=out)


# ------------------------------------------------------------------ вызов

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        import ds_build as B
        B._reexec_venv(__file__)                              # схемы форм проверяет jsonschema окружения скилла
        return _selftest()
    ap = docpaths.parser("ds_coverage", __doc__, commands=("check", "show"), surface="optional", stages=STAGES,
                         accept=lambda s: s.app or s.page)
    call = docpaths.parse(ap, argv)
    try:
        cov = coverage(call.slug, call.repo, call.surface, call.stage)
        if call.command == "show":
            show(cov, as_json=call.json)
            return F.EXIT_OK
        items = cov.rep.items
        F.print_findings(items, as_json=call.json)
        return F.exit_code(items)
    except (F.ToolError, docpaths.DocPathError, RuntimeError, OSError) as e:
        print(f"ds_coverage: {e}", file=sys.stderr)
        return F.EXIT_USAGE


# ------------------------------------------------------------------ самопроверка

FILL = {"<дата>": "2026-09", "<роль>": "владелец продукта", "<компонент ДС>": "Button", "<ИмяТипа>": "AddressMap",
        "<Тип>": "Button", "<стиль>": "body", "<набор>": "lucide", "<толщина>": 1.5, "<object>": "request",
        "<status>": "new", "<роль цвета>": "color.status.info", "<иконка>": "clipboard", "<surface>": "office",
        "<screen-slug>": "requests-list", "<имя бренда>": "Отвес", "<путь>": "docs/business/material.md",
        "<файл>": "logo.svg", "<значение>": "#1d4ed8", "<семейство>": "Golos Text", "<лицензия>": "SIL OFL 1.1",
        "<slug>": "otves-office", "<категория>": "general", "<цель>": "wcag22-aa", "<тип>": "admin",
        "<user-slug>": "manager", "<surface или —>": "—", "<постура>": "sovereign", "<режим>": "compact",
        "<температура>": "cool", "<id>": "tile-a", "<id карточки>": "tile-a", "<число разделов>": 2, "<число>": 3,
        "<…>": 240, "<состояние>": "rest"}
FILL_BY_KEY = {("brand", "role"): "body", ("app-brief", "role"): "composition", ("brand", "roles"): "accent",
               ("system", "text_styles"): "body", ("system", "components"): "Button", ("system", "status_colors"):
               "request.new", ("system", "object_markers"): "request", ("app-brief", "pointer"): "office",
               ("app-brief", "surfaces"): "office", ("system", "required"): ["rest"]}


def fill_form(form, node, key=None):
    """Форма с плейсхолдерами `<…>` → экземпляр: значения по таблице, ключи — по родительскому ключу."""
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            kk = FILL_BY_KEY.get((form, key), FILL.get(k, "x")) if isinstance(k, str) and L.PLACEHOLDER.match(k) else \
                (re.sub(r"<[^<>]+>", lambda m: str(FILL.get(m.group(0), "x")), k) if isinstance(k, str) else k)
            out[kk] = fill_form(form, v, k)
        return out
    if isinstance(node, list):
        if not node and (form, key) in FILL_BY_KEY and isinstance(FILL_BY_KEY[(form, key)], list):
            return list(FILL_BY_KEY[(form, key)])
        return [fill_form(form, x, key) for x in node]
    if isinstance(node, str):
        if L.PLACEHOLDER.match(node.strip()):
            if (form, key) in FILL_BY_KEY and not isinstance(FILL_BY_KEY[(form, key)], list):
                return FILL_BY_KEY[(form, key)]
            return FILL.get(node.strip(), node.strip("<>"))
        return re.sub(r"<[^<>]+>", lambda m: str(FILL.get(m.group(0), m.group(0).strip("<>"))), node)
    return node


def _selftest():
    import shutil
    import subprocess
    import tempfile
    ok = True

    def check_(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    try:
        import jsonschema
    except ImportError:
        print("ds_coverage: нужен jsonschema — $DDD_HOME/venv/bin/python", file=sys.stderr)
        return F.EXIT_USAGE
    # 1. схемы форм уровня продукта
    reg = registry()
    for k in FORMS:
        try:
            jsonschema.Draft202012Validator.check_schema(schema(k))
            good = True
        except jsonschema.SchemaError:
            good = False
        check_(f"схема {k}: метасхема Draft 2020-12, $id {schema(k).get('$id')}", good)
    for k in FORMS:
        form = _yaml().safe_load(docpaths.template("design", "_template", f"{k}.yaml").read_text(encoding="utf-8"))
        errs = form_errors(k, fill_form(k, form), reg)
        check_(f"форма _template/design/_template/{k}.yaml с заполненными плейсхолдерами проходит схему"
               + (f" (есть: {errs[:2]})" if errs else ""), not errs)
    bad = {"system_version": 1, "status": "approved", "extensions": [{"id": "Map", "name": "м", "purpose": "ппп",
                                                                      "why_not": "ппп", "behavior": "ппп",
                                                                      "states": {"required": ["rest"]}}]}
    msgs = " ".join(m for _, m in form_errors("system", bad, reg))
    check_("схема system: approved без approval и conventions, расширение без keyboard и text_roles — ошибки",
           "approval" in msgs and "conventions" in msgs and "keyboard" in msgs and "text_roles" in msgs)
    check_("схема brand: verified без approval, роль цвета вне списка — ошибки",
           len(form_errors("brand", {"name": "Б", "status": "verified", "colors": {"roles": {"primary": "#000"}}},
                           reg)) == 2)
    kbpaths.use("tests")
    import fixture_project
    with fixture_project.built("cabinet-ds") as fx:
        root, slug = fx.root, fx.slug
        for k in FORMS:
            data = _yaml().safe_load(docpaths.design(slug, k, repo=root).read_text(encoding="utf-8"))
            errs = form_errors(k, data, reg)
            check_(f"фикстура cabinet-ds: design/{k}.yaml проходит схему" + (f" (есть: {errs[:2]})" if errs else ""),
                   not errs)
        # 2. чистая фикстура
        cov = coverage(slug, root)
        loud = [f for f in cov.rep.items if f.severity in ("error", "warning")]
        check_("cabinet-ds: каждый тип ui: stable-экранов сопоставлен — 0 error, 0 warning"
               + (f" (есть: {'; '.join(f.message[:90] for f in loud[:3])})" if loud else ""), not loud)
        check_("набор кабинета: 18 типов с расширением AddressMap, у Table — экран requests-list",
               len(cov.uses.get("office", {})) == 18 and "AddressMap" in cov.uses["office"]
               and cov.uses["office"]["Table"].where == ["requests-list"])
        check_("одна карточка Callout закрывает Alert и Banner; AddressMap — через extensions",
               {r.use.type for r in cov.rows if r.component == "Callout"} == {"Alert", "Banner"}
               and any(r.key == "extensions" and r.use.type == "AddressMap" for r in cov.rows))
        buf = __import__("io").StringIO()
        show(cov, out=buf)
        lines = buf.getvalue().splitlines()
        table = next((x for x in lines if x.split()[1:2] == ["Table"]), "")
        check_("show: строка заголовка с колонками справки, у строки типа — экраны, где он стоит",
               lines and lines[0].split() == ["поверхность", "тип", "ключ", "компонент", "итог", "где", "стоит"]
               and len(lines) == 19 and table.split()[-2:] == ["ok", "requests-list"])
        with tempfile.TemporaryDirectory(prefix="ddd-cov-cwd-") as cwd:
            r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "check", slug, "--repo", str(root),
                                "--json"], cwd=cwd, capture_output=True, text=True)
        check_("check --json из чужой рабочей папки с --repo — код 0, строки находок",
               r.returncode == 0 and not [f for f in F.parse_lines(r.stdout) if f.severity == "error"])
        sysp = docpaths.design(slug, "system", repo=root)
        base = sysp.read_text(encoding="utf-8")

        def with_system(text, stage=None):
            sysp.write_text(text, encoding="utf-8")
            return coverage(slug, root, stage=stage).rep.items

        # 3. снятое сопоставление типа
        items = with_system(base.replace("  Pagination: {component: Pagination}\n", ""))
        got = [f for f in items if f.rule == RULE and "Pagination" in f.message]
        check_("снятое сопоставление Pagination → R-COV-005 warning с именем типа и экранами",
               len(got) == 1 and got[0].severity == "warning" and "requests-list" in got[0].message
               and got[0].surface == "office")
        inp = docpaths.design(slug, "input", surface="office", repo=root)
        inp.mkdir(parents=True, exist_ok=True)
        (inp / "INPUT.md").write_text("---\nstage: mockup\n---\n\n# Вход холста\n", encoding="utf-8")
        got = [f for f in coverage(slug, root).rep.items if "Pagination" in f.message]
        check_("вход холста этапа mockup → та же находка error", got and got[0].severity == "error")
        shutil.rmtree(inp)
        got = [f for f in coverage(slug, root, stage="mockup").rep.items if "Pagination" in f.message]
        check_("--stage mockup → error", got and got[0].severity == "error")
        pd = [f for f in coverage(slug, root, "office", "mockup", ["plan-dashboard"]).rep.items
              if "Pagination" in f.message]
        rl = [f for f in coverage(slug, root, "office", "mockup", ["requests-list"]).rep.items
              if "Pagination" in f.message]
        check_("партия экранов: тип чужого экрана находки не даёт, своего — error на макете",
               not pd and rl and rl[0].severity == "error")
        # 4. компонент без обязательного состояния
        sysp.write_text(base, encoding="utf-8")
        prev = docpaths.design(slug, "ds-project", repo=root) / "components" / "Button" / "preview.html"
        ptext = prev.read_text(encoding="utf-8")
        prev.write_text("\n".join(ln for ln in ptext.splitlines() if 'data-state="loading"' not in ln) + "\n",
                        encoding="utf-8")
        got = [f for f in coverage(slug, root).rep.items if f.rule == RULE and "loading" in f.message]
        mk = [f for f in coverage(slug, root, stage="mockup").rep.items if f.rule == RULE and "loading" in f.message]
        check_("компонент Button без состояния loading → находка warning и на макете (не нарисованное состояние — "
               "доклад)", len(got) == 1 and "Button" in got[0].message and len(mk) == 1
               and {got[0].severity, mk[0].severity} == {"warning"})
        prev.write_text(ptext, encoding="utf-8")
        # 5. указатель touch: hover не требуется
        ab = docpaths.design(slug, "app-brief", repo=root)
        abt = ab.read_text(encoding="utf-8")
        ab.write_text(abt.replace("pointer: {office: both}", "pointer: {office: touch}"), encoding="utf-8")
        prev.write_text("\n".join(ln for ln in ptext.splitlines() if 'data-state="hover"' not in ln) + "\n",
                        encoding="utf-8")
        check_("поверхность touch (core.pointer брифа): hover не требуется",
               not [f for f in coverage(slug, root).rep.items if "hover" in f.message])
        ab.write_text(abt, encoding="utf-8")
        check_("поверхность с указателем: без hover — находка",
               [f for f in coverage(slug, root).rep.items if "hover" in f.message])
        prev.write_text(ptext, encoding="utf-8")
        # 6. расширение без keyboard, без text_roles; два компонента на тип; ключ из aka
        nokb = base.replace('    keyboard: "Tab', '    x-keyboard: "Tab', 1)
        items, early = with_system(nokb, "mockup"), with_system(nokb)
        check_("расширение без keyboard → R-COV-005 error на макете кабинета, до макета — warning",
               [f for f in items if f.severity == "error" and "keyboard" in f.message]
               and [f for f in early if f.severity == "warning" and "keyboard" in f.message]
               and not [f for f in early if f.severity == "error"])
        items = with_system(base.replace("    text_roles: {AddressMap.Pin: [label]}\n", ""), "mockup")
        check_("расширение без text_roles → R-COV-005 error на макете кабинета",
               [f for f in items if f.severity == "error" and "text_roles" in f.message])
        items = with_system(base.replace("  Button: {component: Button}\n",
                                         "  Button: {component: Button}\n  Button: {component: ActionButton}\n"),
                            "mockup")
        check_("два компонента на один тип (ключ дважды) → error на макете кабинета",
               [f for f in items if f.severity == "error" and "дважды" in f.message])
        items = with_system(base.replace("  TopBar: {component: TopBar}\n", "  Navbar: {component: TopBar}\n"))
        check_("ключ Navbar (aka) → предупреждение с типом TopBar и непокрытый TopBar с подсказкой",
               [f for f in items if "Navbar" in f.message and "TopBar" in f.message and f.severity == "warning"]
               and [f for f in items if "ui:TopBar" in f.message and "Navbar" in f.message])
        items = with_system(base.replace("  Field: {component: Field}\n",
                                         "  Field: {component: Field, optional_states: [invalid, pressed]}\n"))
        check_("optional_states: обязательное и не состояние словаря → предупреждения",
               len([f for f in items if "optional_states" in f.message]) == 2)
        sysp.write_text(base, encoding="utf-8")
        # 7. нет карты решений
        sysp.unlink()
        items = coverage(slug, root).rep.items
        check_("нет system.yaml → одна находка на поверхность со списком типов",
               len(items) == 1 and "типы без компонента ДС — 18" in items[0].message)
    # 8. сайт: типы слотов действий и форм планов
    with fixture_project.built("minimal") as fx:
        cov = coverage(fx.slug, fx.root, surface="promo")
        want = {"Button", "Link", "Field", "TextInput", "Checkbox"}
        got = set(cov.uses.get("promo", {}))
        check_(f"сайт: набор из слотов action и форм плана ({', '.join(sorted(got))})", want <= got)
        items = cov.rep.items
        check_("сайт без карты решений: находка со списком типов страниц",
               len(items) == 1 and "Checkbox" in items[0].message and items[0].surface == "promo")
        mk = coverage(fx.slug, fx.root, surface="promo", stage="mockup").rep.items
        check_("сайт: R-COV-005 — warning и на макете", mk and all(f.severity == "warning" for f in mk))
    print("ds_coverage selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
