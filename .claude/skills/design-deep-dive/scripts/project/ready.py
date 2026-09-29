#!/usr/bin/env python3
"""ready — манифест готовности поверхности к сборке `docs/projects/<slug>/design/<surface>/ready.yaml` для репозитория
кода и проверка его свежести.

Форма — `docs/projects/_template/design/_template/ready.yaml`; канон — `docs/projects/_template/design/README.md`,
«Пакет для кода»; этап — `references/phases.md`, `package`. Манифест производный: его собирает эта утилита из закрытых
файлов стратегии, он коммитится вместе с источниками и руками не правится. Репозиторий кода собирает единицы с
`ready: true` и читает из манифеста пункты «после сборки».

    ready build <slug> <surface> [--repo DIR] [--out DIR] [--today ГГГГ-ММ-ДД] [--json]
        собрать и записать design/<surface>/ready.yaml (--out DIR — в DIR/ready.yaml); --json — манифест JSON в stdout
    ready check <slug> [<surface>] [--repo DIR] [--today …] [--json]
        свежесть: файл равен сборке по текущим источникам (R-FRESH-006); без <surface> — все поверхности с ready.yaml
    ready show  <slug> <surface> [--repo DIR] [--today …] [--json]
        единицы: статусы, вердикт REVIEW.md, отпечаток одобрения из REVIEW.md и текущий — по артбордам строки «Приёмка»
        и источникам единицы; текущий этап acceptance пишет в колонку «отпечаток» REVIEW.md
    ready --selftest                  фикстуры package-landing, input-landing и package-cabinet, без сети

Поверхности — с маршрутом дизайна и холстом: web рода landing, site или app; admin, desktop, embed.

Что собирается (поля формы):
  surface, type, web_kind, consumer   реестр surface.md: landing и site → <org>/site; app, admin, desktop, embed →
                                      <org>/frontend; web_kind у admin, desktop, embed — «—»
  sources                             файлы, которые читает код, со статусом и sha256 (путь — от папки проекта): сайт —
                                      бриф, карта, планы, copy deck, факты, голос, ДС (статус токенов, CSS и прозы —
                                      статус system.yaml), бренд, манифест ассетов продукта, арт-дирекция, спецификации
                                      движения, манифест ассетов поверхности, адаптивные HTML-копии, REVIEW.md,
                                      integration.md; кабинет — экраны, блоки, каркасы, map.md, texts.md, FSD-карта, ДС,
                                      бриф на вид, продуктовый паспорт, манифесты ассетов, адаптивные копии, REVIEW.md
  units                               сайт — страницы планов site/<surface>/plans/ (порядок build_order карты или
                                      pages.list брифа); кабинет — экраны screens/<surface>/screens/
    composition                       сайт — статус плана; кабинет — статус экрана
    texts                             сайт — статус страницы copy deck (none — текстов нет); кабинет — наименьший статус
                                      строк texts.md, которые экран называет (draft < assumed < checked < approved)
    mockup                            вердикт строки «Приёмка» review/REVIEW.md, если отпечаток одобрения совпал с
                                      текущим; не совпал или строки нет — none; skipped — строка «макет пропущен»
                                      заметки пропусков поверхности (<state>/design/<surface>/_phase-jump.md)
    budget_profile, gate_exceptions   сайт — page.budget_profile и id x-gate-exception плана; кабинет — «—» и []
    after_build                       пункты input/ACCEPTANCE.md с местом «после сборки» (ST-<экран>-… — только у
                                      своего экрана)
    open                              заглушки [PLACEHOLDER] выбранных текстов и демо-факты (example: true), которые
                                      страница называет; затем строки «решение заказчика: …» — ДС не утверждена, у
                                      кабинета ещё покрытие ДС типов своего экрана не полное (ds_coverage) и FSD-карта
                                      не stable: готовность они не держат, решает заказчик
    ready                             композиция закрыта (план approved, экран stable), тексты approved, факты
                                      публикуемы или пробел назван, макет принят с совпавшим отпечатком (или пропущен
                                      решением заказчика)
  факты единицы сайта — ссылки fact: и missing: слотов данных плана и fact_ids выбранных текстов copy deck: демо-факт —
  строка open (пробел назван), missing: со строкой пробела в facts.yaml — названный пробел; готовность единицы они не
  держат, публикацию сайта с демо-фактом держит copydeck.py validate --final; в blockers («факты: …») — факт, которого
  нет в facts.yaml, missing: без строки пробела и факт, который claims_check не допускает к публикации (разрешение,
  срок, проверка)
  perf                                сайт — plans; кабинет — {field: p75, rum: true, lab: [AC-PRF-04, AC-PRF-05,
                                      AC-PRF-06]}
  frontend_design                     сайт — род, уровень и потолок движения брифа (потолок без поля брифа — уровень
                                      движения ambition-levels.yaml); кабинет — поправки ui/CONTRADICTIONS.md §[C25]
  status, blockers                    ready — готовы все единицы, partial — часть, not-ready — ни одной; blockers —
                                      строка на причину, по которой единица или поверхность не готова

Отпечаток одобрения единицы — sha256 двух строк: «артборды:<`dc_to_html.fingerprint` её артбордов>» (колонка
«артборды» таблицы «Приёмка», `canvas/project/<Имя>.dc.html`) и «источники:<`canvas_input.unit_fingerprint`>» —
источники единицы: у страницы план, её тексты в copy deck, план ассетов и файлы слотов, спецификация движения, записи
фактов, бренд и арт-дирекция; у экрана файл экрана, его блоки и каркас, его строки texts.md, бриф на вид; у обеих
токены ДС и system.yaml. Правка артборда или источника единицы снимает одобрение; пересборка входа (вход motion тоже),
дата в ARTIFACTS.md, поля записи решения (статус, утверждение, starter) и правка соседней единицы — нет.

Проверка (check): манифест на диске против сборки в памяти по тем же источникам; ключ `example` (пометка иллюстрации
у фикстур) не сравнивается. Находка — строка контракта `findings.py`: R-FRESH-006, error, kind ready. Файла нет —
проверять нечего. Форма файла (R-STRUCT-008) — `form_errors(data)`, её зовёт design_audit.
Код выхода: 0 — ошибок нет; 1 — есть error; 2 — ошибка вызова или окружения.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402
import docpaths  # noqa: E402
import findings as F  # noqa: E402

TOOL = "ready"
KIND = "ready"
RULE = "R-FRESH-006"
FILE = "ready.yaml"
CONSUMER = {"page": "<org>/site", "app": "<org>/frontend"}
PERF_APP = {"field": "p75", "rum": True, "lab": ["AC-PRF-04", "AC-PRF-05", "AC-PRF-06"]}
C25 = ("ui/CONTRADICTIONS.md §[C25]: фон сплошной, градиент только в названных местах, без оркестрованной загрузки, "
       "гарнитура с проверенной кириллицей")
VERDICTS = ("accepted", "accepted_with_notes", "blocked", "none", "skipped")
ACCEPTED = ("accepted", "accepted_with_notes")
TEXT_ORDER = ("draft", "assumed", "checked", "approved")
STATE = (".claude", "skills", "entrypoint", "state", "projects")
SKIP_LINE = re.compile(r"макет\s+пропущен", re.I)
DECIDE = "решение заказчика: "                          # строка open: готовность не держит, решает заказчик
FORM_KEYS = ("surface", "type", "web_kind", "consumer", "status", "sources", "units", "perf", "frontend_design",
             "blockers")
UNIT_KEYS = ("id", "ready", "composition", "texts", "mockup", "budget_profile", "gate_exceptions", "after_build",
             "open")
FD_KEYS = ("surface", "ambition", "motion_cap", "app_screens")
HEADER = ("# ready.yaml — готовность поверхности {surface} к сборке для репозитория кода.",
          "# Производный файл: собирает `scripts/project/ready.py build {slug} {surface}` из файлов стратегии; руками "
          "не правится.",
          "# Форма — docs/projects/_template/design/_template/ready.yaml.")


# ------------------------------------------------------------------ окружение и модули соседей

def _reexec_venv():
    """Без PyYAML в текущем Python — один перезапуск в Python окружения скилла."""
    import importlib.util
    if importlib.util.find_spec("yaml") is not None:
        return
    py = kbpaths.python()
    if os.environ.get("DDD_READY_VENV") or not Path(py).exists():
        return
    os.environ["DDD_READY_VENV"] = "1"
    os.execv(py, [py, str(Path(__file__).resolve())] + sys.argv[1:])


_MOD = {}


def mod(name):
    """Модуль соседней утилиты: dc_to_html (claude-design), claims_check (text), утилиты project/ — по имени."""
    if name not in _MOD:
        import importlib
        if name == "dc_to_html":
            kbpaths.use("claude-design")
        elif name == "claims_check":
            kbpaths.use("text")
        _MOD[name] = importlib.import_module(name)
    return _MOD[name]


def yaml_mod():
    import yaml
    return yaml


def load(path):
    """YAML или JSON файла; нет файла или он не разбирается — None."""
    p = Path(path)
    if not p.is_file():
        return None
    try:
        text = p.read_text(encoding="utf-8")
        return json.loads(text) if p.suffix == ".json" else yaml_mod().safe_load(text)
    except Exception:                                       # noqa: BLE001 — битый файл ловят валидаторы его вида
        return None


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(d, *path, default=None):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def dash(v):
    return "—" if v in (None, "", [], {}) else v


# ------------------------------------------------------------------ статусы источников

def md_rows_status(path):
    """Статус md-файла таблиц со столбцом status (FSD-карта, texts.md): все строки stable/approved — он же, иначе
    наименьший; нет строк — None."""
    L = mod("layer")
    try:
        md = L.Md(path)
    except Exception:                                       # noqa: BLE001
        return None
    vals = []
    for t in md.tables():
        if "status" in t.columns:
            vals += [L.cell(r.get("status")) for r in t.rows if not L.is_empty(r.get("status"))]
    if not vals:
        return None
    for order in (TEXT_ORDER, ("draft", "stable")):
        if all(v in order for v in vals):
            return min(vals, key=order.index)
    return vals[0]


def file_status(path, ds_status=None):
    p = Path(path)
    if p.name in ("system.tokens.json", "system.tokens.css", "DESIGN.md") and p.parent.name == "design":
        return ds_status or "—"
    st = docpaths.status(p)
    if st is None and p.suffix == ".md":
        st = md_rows_status(p)
    return st or "—"


# ------------------------------------------------------------------ сборка

class Build:
    """Сборка манифеста одной поверхности в памяти: data — словарь формы, blockers, units."""

    def __init__(self, slug, surf, repo, today=None):
        self.slug, self.surf = slug, surf
        self.repo = docpaths.root(repo)
        self.surface = surf.slug
        self.project = docpaths.project(slug, repo=self.repo)
        self.today = today or dt.date.today()
        self.blockers = []
        self._facts = None
        self._src = {}

    # пути
    def prel(self, p):
        return Path(p).resolve().relative_to(self.project.resolve()).as_posix()

    def dsurf(self, *parts):
        return docpaths.design(self.slug, *parts, surface=self.surface, repo=self.repo)

    def dprod(self, *parts):
        return docpaths.design(self.slug, *parts, repo=self.repo)

    # общее
    @property
    def ds_status(self):
        return docpaths.status(self.dprod("system")) if self.dprod("system").is_file() else None

    def review(self):
        """Строки «Приёмка» REVIEW.md: {единица: {artboards, verdict, fingerprint, by, date, open}}."""
        p = self.dsurf("review") / "REVIEW.md"
        if not p.is_file():
            return {}
        L = mod("layer")
        t = L.Md(p).table(("вердикт",))
        out = {}
        for r in t.rows if t else []:
            unit = L.cell(r.get("страница или экран"))
            if L.is_empty(unit):
                continue
            abs_ = [a.strip().strip("`") for a in re.split(r"[,;]", str(r.get("артборды") or "")) if a.strip()]
            out[unit] = {"artboards": [a for a in abs_ if a and not L.is_empty(a)],
                         "verdict": L.cell(r.get("вердикт")), "by": L.cell(r.get("одобрил")),
                         "date": L.cell(r.get("дата")), "fingerprint": L.cell(r.get("отпечаток")),
                         "open": L.cell(r.get("открыто"))}
        return out

    def fingerprint(self, unit, artboards):
        """Отпечаток одобрения единицы: sha256 строк «артборды:<отпечаток её артбордов>» и «источники:<отпечаток
        источников единицы>»; нет артборда или единицы — None."""
        if not artboards:
            return None
        proj = self.dsurf("canvas-project")
        paths = [proj / a for a in artboards]
        if any(not p.is_file() for p in paths):
            return None
        if unit not in self._src:
            self._src[unit] = mod("canvas_input").unit_fingerprint(self.slug, self.surface, unit, self.repo)
        if self._src[unit] is None:
            return None
        lines = (f"артборды:{mod('dc_to_html').fingerprint(paths)}", f"источники:{self._src[unit]}")
        return "sha256:" + hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()

    def jump_note(self):
        return docpaths.root(self.repo).joinpath(*STATE, self.slug, "design", self.surface, "_phase-jump.md")

    def skipped(self, unit, units):
        """Решение заказчика «макет пропущен» в заметке пропусков поверхности: строка называет единицу или ни одну."""
        p = self.jump_note()
        if not p.is_file():
            return False
        for line in p.read_text(encoding="utf-8").splitlines():
            if not SKIP_LINE.search(line):
                continue
            named = [u for u in units if re.search(rf"(?<![\w-]){re.escape(u)}(?![\w-])", line)]
            if not named or unit in named:
                return True
        return False

    def after_build(self):
        p = self.dsurf("input") / "ACCEPTANCE.md"
        if not p.is_file():
            return []
        rows, _heads = mod("canvas_input").parse_acceptance(p.read_text(encoding="utf-8"))
        seen, out = set(), []
        for r in rows:
            i = r.get("id")
            if r.get("где") == "после сборки" and i and i not in seen:
                seen.add(i)
                out.append(i)
        return out

    def mockup(self, unit, rev, units):
        """(вердикт для манифеста, причина блокера или None)."""
        row = rev.get(unit)
        if row is None:
            if self.skipped(unit, units):
                return "skipped", None
            return "none", "макета нет: строки в REVIEW.md и решения «макет пропущен» нет"
        verdict = row["verdict"] if row["verdict"] in ACCEPTED + ("blocked",) else "none"
        if verdict == "blocked":
            return "blocked", "вердикт blocked — есть непройденный пункт B"
        if verdict == "none":
            return "none", f"вердикт REVIEW.md «{row['verdict']}» вне формы"
        now = self.fingerprint(unit, row["artboards"])
        if now is None:
            return "none", ("одобрение не проверить: нет артбордов "
                            + (", ".join(row["artboards"]) or "в колонке «артборды»") + " или источников единицы")
        if now != row["fingerprint"]:
            return "none", "одобрение снято: отпечаток артбордов и источников единицы не совпал с REVIEW.md"
        return verdict, None

    # факты
    def facts(self):
        """(факты по id, id пробелов, демо у файла, claims_check.Facts или None)."""
        if self._facts is None:
            p = docpaths.facts(self.slug, repo=self.repo)
            data = load(p) if p.is_file() else None
            obj = None
            if isinstance(data, dict):
                try:
                    cc = mod("claims_check")
                    obj = cc.load_facts(str(p), cc.load_schema(), True)
                except (Exception, SystemExit):                 # noqa: BLE001 — форму фактов проверяет R-STRUCT-003
                    obj = None
            facts = {f.get("id"): f for f in (data or {}).get("facts") or [] if isinstance(f, dict)}
            missing = {m.get("id") for m in (data or {}).get("missing") or [] if isinstance(m, dict)}
            self._facts = (facts, missing, bool((data or {}).get("example")), obj)
        return self._facts

    def fact_problems(self, refs):
        """Ссылки fact:/missing: единицы → ([непубликуемые или нет], [демо])."""
        facts, missing, demo_file, obj = self.facts()
        bad, demo = [], []
        for kind, fid in sorted(refs):
            if kind == "missing":
                if fid not in missing:
                    bad.append(f"missing:{fid} (пробел не назван)")
                continue
            f = facts.get(fid)
            if f is None:
                bad.append(f"fact:{fid} (нет в facts.yaml)")
                continue
            if demo_file or f.get("example"):
                demo.append(fid)
            if obj is not None:
                try:
                    issues = mod("claims_check").publishable_issues(f, obj, self.today)
                except Exception:                           # noqa: BLE001
                    issues = []
                if any(lv == "error" for lv, *_ in issues):
                    bad.append(f"fact:{fid} ({'; '.join(m for lv, _r, m, _f in issues if lv == 'error')[:120]})")
        return bad, demo

    # сайт
    def site_units(self):
        plans_dir = docpaths.site(self.slug, self.surface, "plans", repo=self.repo)
        plans = {}
        for p in sorted(plans_dir.glob("*.yaml")) if plans_dir.is_dir() else []:
            d = load(p)
            pid = str(get(d, "page", "id", default=p.stem) or p.stem)
            plans[pid] = (p, d if isinstance(d, dict) else {})
        order = []
        smap = load(docpaths.site(self.slug, self.surface, "site-map", repo=self.repo))
        for x in (smap or {}).get("build_order") or [] if isinstance(smap, dict) else []:
            x = x.get("id") if isinstance(x, dict) else x
            if isinstance(x, str) and x in plans and x not in order:
                order.append(x)
        brief = load(docpaths.site(self.slug, self.surface, "brief", repo=self.repo))
        for x in get(brief, "pages", "list", default=[]) or []:
            x = x.get("id") if isinstance(x, dict) else None
            if x in plans and x not in order:
                order.append(x)
        order += [x for x in sorted(plans) if x not in order]
        return [(x,) + plans[x] for x in order], brief if isinstance(brief, dict) else {}

    def deck_page(self, pid):
        p = docpaths.site(self.slug, self.surface, "copy", f"{pid}.yaml", repo=self.repo)
        d = load(p)
        for pg in get(d, "copy_deck", "pages", default=[]) or []:
            if isinstance(pg, dict) and pg.get("page_id") == pid:
                return p, pg
        return (p if p.is_file() else None), None

    @staticmethod
    def chosen_texts(page):
        """[(место, текст, fact_ids)] выбранных вариантов страницы copy deck."""
        out = []
        for key, val in (get(page, "meta") or {}).items() if isinstance(get(page, "meta"), dict) else []:
            if isinstance(val, str):
                out.append((f"meta/{key}", val, []))
        for s in page.get("sections") or []:
            for sl in s.get("slots") or [] if isinstance(s, dict) else []:
                if not isinstance(sl, dict):
                    continue
                var = next((v for v in sl.get("variants") or [] if isinstance(v, dict)
                            and v.get("id") == sl.get("chosen")), None)
                if var is not None:
                    out.append((f"{s.get('section_id')}/{sl.get('slot_id')}", str(var.get("text") or ""),
                                list(sl.get("fact_ids") or []) + list(var.get("fact_ids") or [])))
        mf = get(page, "meta", "fact_ids")
        if isinstance(mf, list):
            out.append(("meta", "", mf))
        return out

    @staticmethod
    def plan_fact_refs(plan):
        refs = set()
        for s in plan.get("sections") or []:
            for sl in get(s, "slots", "data", default=[]) or [] if isinstance(s, dict) else []:
                for ref in [sl.get("fact")] + list(sl.get("facts") or []) if isinstance(sl, dict) else []:
                    m = re.match(r"^(fact|missing):([a-z0-9][a-z0-9_-]*)$", str(ref or ""))
                    if m:
                        refs.add((m.group(1), m.group(2)))
        return refs

    def site(self):
        units, brief = self.site_units()
        rev = self.review()
        after = self.after_build()
        ds = self.ds_status
        ids = [u[0] for u in units]
        out = []
        for pid, path, plan in units:
            why = []
            comp = docpaths.status(path) or "draft"
            if comp != "approved":
                why.append(f"план {comp}")
            deck_path, page = self.deck_page(pid)
            texts = str(page.get("status") or "draft") if page else "none"
            if texts != "approved":
                why.append("текстов нет" if texts == "none" else f"тексты {texts}")
            verdict, mwhy = self.mockup(pid, rev, ids)
            if mwhy:
                why.append(mwhy)
            refs = self.plan_fact_refs(plan)
            opened = []
            for where, text, fids in self.chosen_texts(page) if page else []:
                refs |= {("fact", f) for f in fids if isinstance(f, str)}
                if "[PLACEHOLDER" in text:
                    opened.append(f"[PLACEHOLDER]: {where}")
            bad, demo = self.fact_problems(refs)
            if bad:
                why.append("факты: " + ", ".join(bad[:4]) + (f" и ещё {len(bad) - 4}" if len(bad) > 4 else ""))
            opened += [f"демо-факт: {x}" for x in sorted(set(demo))]
            decide = [] if ds == "approved" else [f"ДС не утверждена (system.yaml {ds or 'нет'})"]
            exc = [str(e.get("id")) for e in get(plan, "page", "x-gate-exception", default=[]) or []
                   if isinstance(e, dict) and e.get("id")]
            out.append(({"id": pid, "ready": not why, "composition": comp, "texts": texts, "mockup": verdict,
                         "budget_profile": dash(get(plan, "page", "budget_profile")), "gate_exceptions": exc,
                         "after_build": list(after), "open": self.open_list(opened, decide)}, why))
        return out, brief

    @staticmethod
    def open_list(opened, decide):
        """Строки open единицы: заглушки и демо-факты по алфавиту, затем решения заказчика (ДС, покрытие, FSD)."""
        return sorted(set(opened)) + [DECIDE + d for d in decide]

    # кабинет
    def app(self):
        L, T = mod("layer"), mod("tree")
        lay = L.Layer(self.slug, self.surface, self.repo)
        trees = T.parse_layer(lay)
        comps = lay.components
        uses = T.text_uses(trees, comps)
        rows = lay.texts.rows if lay.texts.exists else {}
        rev = self.review()
        after = self.after_build()
        ds = self.ds_status
        cov, cov_err = None, None
        try:
            cov = mod("ds_coverage").coverage(self.slug, self.repo, self.surface)
        except Exception as e:                              # noqa: BLE001 — покрытие не посчитать — решение заказчика
            cov_err = (str(e).splitlines() or [type(e).__name__])[0][:120]
        fsd = self.fsd_status()
        ids = sorted(trees.screens)
        out = []
        for slug in ids:
            rec = lay.screens[slug]
            why = []
            comp = rec.status or "draft"
            if comp != "stable":
                why.append(f"экран {comp}")
            comp_recs = {slug} | set(T.composition(trees, slug)["blocks"])
            shell = str(rec.fm.get("shell") or "")
            keys = sorted({u.key for u in uses if u.parsed.record.slug in comp_recs | {shell}})
            sts = []
            opened = []
            for k in keys:
                r = rows.get(k)
                sts.append(str(r.status) if r is not None and r.status else "draft")
                if r is not None and "[PLACEHOLDER" in str(r.text or ""):
                    opened.append(f"[PLACEHOLDER]: {k}")
            known = [s for s in sts if s in TEXT_ORDER]
            texts = min(known, key=TEXT_ORDER.index) if known else ("none" if not keys else sts[0])
            if texts != "approved":
                why.append("строк текстов нет" if texts == "none" else f"тексты {texts}")
            verdict, mwhy = self.mockup(slug, rev, ids)
            if mwhy:
                why.append(mwhy)
            decide = [] if ds == "approved" else [f"ДС не утверждена (system.yaml {ds or 'нет'})"]
            if cov_err:
                decide.append(f"покрытие ДС не посчитано ({cov_err})")
            elif cov is not None:
                bad = self.cov_of(cov, slug)
                if bad:
                    decide.append(f"покрытие ДС типов экрана не полное (ds_coverage: {len(bad)} — "
                                  f"{', '.join(sorted({t for _f, ts in bad for t in ts}))})")
            if fsd != "stable":
                decide.append("FSD-карты нет" if fsd == "none" else f"FSD-карта {fsd}")
            ab = [a for a in after if not (a.startswith("ST-") and a != "ST-DYN"
                                           and not a.startswith(f"ST-{slug}-"))]
            out.append(({"id": slug, "ready": not why, "composition": comp, "texts": texts, "mockup": verdict,
                         "budget_profile": "—", "gate_exceptions": [], "after_build": ab,
                         "open": self.open_list(opened, decide)}, why))
        return out, lay

    def cov_of(self, cov, screen):
        """Находки покрытия ДС (R-COV-005, error и warning) о типах экрана: [(находка, [типы])]. Тип находки — по ref:
        ключ карты решений (или его тип словаря по aka), расширение, компонент артефакта; карты решений нет — все типы
        экрана. Экран вне сверки покрытия (не stable) — []."""
        types = {t for t, u in (cov.uses.get(self.surface) or {}).items() if screen in u.where}
        if not types:
            return []
        by_comp = {}
        for r in cov.rows:
            if r.component:
                by_comp.setdefault(r.component, set()).add(r.use.type)
        by_ext = {i: eid for eid, (i, _e) in cov.system.extensions.items()}
        out = []
        for f in cov.rep.items:
            if f.rule != "R-COV-005" or f.severity not in ("error", "warning"):
                continue
            m = re.match(r"^system#/components/([^/]+)", f.ref)
            e = re.match(r"^system#/extensions/(\d+)", f.ref)
            c = re.match(r"^artifact#components/(.+)$", f.ref)
            if m:
                hit = {m.group(1), cov.comps.type_of(m.group(1))} & types
            elif e:
                hit = {by_ext.get(int(e.group(1)))} & types
            elif c:
                hit = by_comp.get(c.group(1), set()) & types
            else:
                hit = set(types)
            if hit:
                out.append((f, sorted(hit)))
        return out

    def fsd_status(self):
        d = docpaths.layer(self.slug, "fsd", self.surface, self.repo)
        files = sorted(d.glob("*.md")) if d.is_dir() else []
        if not files:
            return "none"
        sts = [md_rows_status(f) or "draft" for f in files]
        return "stable" if all(s == "stable" for s in sts) else "draft"

    # источники
    def source_files(self, units_extra=()):
        p = []
        sdir = docpaths.layer(self.slug, "site", self.surface, self.repo) if self.surf.page else None
        if self.surf.page:
            p += [docpaths.site(self.slug, self.surface, "brief", repo=self.repo),
                  docpaths.site(self.slug, self.surface, "site-map", repo=self.repo)]
            for sub in ("plans", "copy"):
                d = sdir / sub
                p += sorted(d.glob("*.yaml")) if d.is_dir() else []
            prod = docpaths.product_files(self.slug, repo=self.repo)
            p += prod["facts"] + [x for x in prod["voice"] if x.name == "voice.yaml"]
            p.append(docpaths.project(self.slug, "integration.md", repo=self.repo))
        else:
            folder = docpaths.layer(self.slug, "screens", self.surface, self.repo)
            p += [folder / "map.md", folder / "texts.md"]
            for sub in ("screens", "blocks", "shells"):
                d = folder / sub
                p += sorted(d.glob("*/index.md")) if d.is_dir() else []
            fsd = docpaths.layer(self.slug, "fsd", self.surface, self.repo)
            p += sorted(fsd.glob("*.md")) if fsd.is_dir() else []
            p += [self.dprod("app-brief"), self.dprod("visual-dna"),
                  docpaths.voice(self.slug, product=True, repo=self.repo)]
        p += [self.dprod(k) for k in ("tokens", "tokens-css", "design-md", "system", "brand")]
        p.append(self.dprod("assets") / "manifest.yaml")
        if self.surf.page:
            p.append(self.dsurf("art-direction"))
            md = self.dsurf("motion")
            p += sorted(md.glob("*.motion-spec.yaml")) if md.is_dir() else []
        p.append(self.dsurf("assets") / "manifest.yaml")
        html = self.dsurf("canvas-html")
        if html.is_dir():
            dc = mod("dc_to_html")
            for f in sorted(html.glob("*.html")):
                if dc.copy_source(f.read_text(encoding="utf-8", errors="replace")) is None:
                    p.append(f)
        p.append(self.dsurf("review") / "REVIEW.md")
        return [x for x in dict.fromkeys(p) if x is not None and Path(x).is_file()]

    def run(self):
        page = self.surf.page
        if page:
            units, brief = self.site()
        else:
            units, _lay = self.app()
            brief = {}
        ds = self.ds_status
        sources = [{"path": self.prel(f), "status": file_status(f, ds), "sha256": sha(f)}
                   for f in self.source_files()]
        sources.sort(key=lambda s: s["path"])
        ready = [u for u, _ in units if u["ready"]]
        status = "ready" if units and len(ready) == len(units) else ("partial" if ready else "not-ready")
        blockers = []
        if not units:
            blockers.append("единиц нет: " + ("планов страниц нет" if page else "экранов нет"))
        for u, why in units:
            blockers += [f"{u['id']}: {w}" for w in why]
        if page:
            amb = brief.get("ambition") if isinstance(brief.get("ambition"), dict) else {}
            level = amb.get("level")
            cap = amb.get("motion_cap") or self.level_motion(level)
            fd = {"surface": self.surf.web_kind, "ambition": dash(level), "motion_cap": dash(cap),
                  "app_screens": "—"}
        else:
            fd = {"surface": self.surf.web_kind if self.surf.type == "web" else self.surf.type, "ambition": "—",
                  "motion_cap": "—", "app_screens": C25}
        self.data = {"surface": self.surface, "type": self.surf.type,
                     "web_kind": self.surf.web_kind if self.surf.type == "web" and self.surf.web_kind else "—",
                     "consumer": CONSUMER["page" if page else "app"], "status": status, "sources": sources,
                     "units": [u for u, _ in units], "perf": "plans" if page else dict(PERF_APP),
                     "frontend_design": fd, "blockers": blockers}
        return self

    @staticmethod
    def level_motion(level):
        if not level:
            return None
        lv = load(kbpaths.kb("creative", "01-creative-direction", "ambition-levels.yaml"))
        for row in (lv or {}).get("levels") or []:
            if isinstance(row, dict) and row.get("id") == level:
                return get(row, "maps_to", "claude_design", "motion_level")
        return None


def build(slug, surf, repo=None, today=None):
    """Манифест поверхности в памяти → словарь формы."""
    return Build(slug, surf, repo, today).run().data


# ------------------------------------------------------------------ запись и форма

def _flow(v):
    s = yaml_mod().safe_dump(v, default_flow_style=True, allow_unicode=True, sort_keys=False, width=10 ** 6).strip()
    return s[:-4].strip() if s.endswith("\n...") else (s[:-3].strip() if s.endswith("...") else s)


def render(slug, data):
    """Текст ready.yaml: ключи — в порядке формы, источники и списки — в строку."""
    out = [h.format(slug=slug, surface=data["surface"]) for h in HEADER] + [""]
    for k in ("surface", "type", "web_kind", "consumer", "status"):
        out.append(f"{k}: {_flow(data[k])}")
    out.append("")
    out.append("sources:" + ("" if data["sources"] else " []"))
    out += [f"  - {_flow(s)}" for s in data["sources"]]
    out.append("")
    out.append("units:" + ("" if data["units"] else " []"))
    for u in data["units"]:
        out.append(f"  - id: {_flow(u['id'])}")
        for k in UNIT_KEYS[1:]:
            out.append(f"    {k}: {_flow(u[k])}")
    out.append("")
    out.append(f"perf: {_flow(data['perf'])}")
    out.append(f"frontend_design: {_flow(data['frontend_design'])}")
    out.append("blockers:" + ("" if data["blockers"] else " []"))
    out += [f"  - {_flow(b)}" for b in data["blockers"]]
    return "\n".join(out) + "\n"


def form_errors(data):
    """Форма ready.yaml (R-STRUCT-008): [(JSON Pointer, сообщение, тяжесть)] — нет ключа или значение вне перечня —
    error; ключ вне формы — warning; `example` — пометка иллюстрации, не ключ формы."""
    out = []
    if not isinstance(data, dict):
        return [("", "ready.yaml — не словарь формы", "error")]
    for k in FORM_KEYS:
        if k not in data:
            out.append((f"/{k}", f"нет ключа {k}", "error"))
    for k in data:
        if k not in FORM_KEYS and k != "example":
            out.append((f"/{k}", f"ключ {k} вне формы", "warning"))
    if "status" in data and data["status"] not in ("ready", "partial", "not-ready"):
        out.append(("/status", f"status «{data['status']}» — ready · partial · not-ready", "error"))
    if "consumer" in data and data["consumer"] not in CONSUMER.values():
        out.append(("/consumer", f"consumer «{data['consumer']}» — {' · '.join(CONSUMER.values())}", "error"))
    if "web_kind" in data and data["web_kind"] not in ("landing", "site", "app", "—"):
        out.append(("/web_kind", f"web_kind «{data['web_kind']}» — landing · site · app · —", "error"))
    for i, s in enumerate(data.get("sources") or [] if isinstance(data.get("sources"), list) else []):
        if not (isinstance(s, dict) and all(k in s for k in ("path", "status", "sha256"))):
            out.append((f"/sources/{i}", "источник — {path, status, sha256}", "error"))
    if "sources" in data and not isinstance(data["sources"], list):
        out.append(("/sources", "sources — список", "error"))
    units = data.get("units")
    if "units" in data and not isinstance(units, list):
        out.append(("/units", "units — список", "error"))
    for i, u in enumerate(units if isinstance(units, list) else []):
        if not isinstance(u, dict):
            out.append((f"/units/{i}", "единица — словарь формы", "error"))
            continue
        for k in UNIT_KEYS:
            if k not in u:
                out.append((f"/units/{i}/{k}", f"у единицы {u.get('id', i)} нет ключа {k}", "error"))
        for k in u:
            if k not in UNIT_KEYS:
                out.append((f"/units/{i}/{k}", f"ключ единицы {k} вне формы", "warning"))
        if "mockup" in u and u["mockup"] not in VERDICTS:
            out.append((f"/units/{i}/mockup", f"mockup «{u['mockup']}» — {' · '.join(VERDICTS)}", "error"))
        if "ready" in u and not isinstance(u["ready"], bool):
            out.append((f"/units/{i}/ready", "ready — true или false", "error"))
    fd = data.get("frontend_design")
    if "frontend_design" in data:
        if not isinstance(fd, dict):
            out.append(("/frontend_design", "frontend_design — {surface, ambition, motion_cap, app_screens}", "error"))
        else:
            out += [(f"/frontend_design/{k}", f"нет ключа frontend_design.{k}", "error") for k in FD_KEYS
                    if k not in fd]
    if "blockers" in data and not isinstance(data["blockers"], list):
        out.append(("/blockers", "blockers — список строк", "error"))
    return out


def _diff(old, new):
    """Расхождения манифеста на диске и сборки — строки для сообщения."""
    out = []
    old = {k: v for k, v in (old or {}).items() if k != "example"}
    for k in FORM_KEYS:
        a, b = old.get(k), new.get(k)
        if a == b:
            continue
        if k == "sources" and isinstance(a, list):
            am = {s.get("path"): s for s in a if isinstance(s, dict)}
            bm = {s["path"]: s for s in b}
            for p in sorted(set(am) | set(bm)):
                if p not in bm:
                    out.append(f"источник {p} больше не читается")
                elif p not in am:
                    out.append(f"новый источник {p}")
                elif am[p] != bm[p]:
                    what = ", ".join(x for x in ("status", "sha256") if am[p].get(x) != bm[p].get(x)) or "поля"
                    out.append(f"источник {p}: {what} не совпадает с файлом")
        elif k == "units" and isinstance(a, list):
            am = {u.get("id"): u for u in a if isinstance(u, dict)}
            bm = {u["id"]: u for u in b}
            for i in list(dict.fromkeys(list(bm) + list(am))):
                if i not in bm:
                    out.append(f"единицы {i} больше нет")
                elif i not in am:
                    out.append(f"новая единица {i}")
                elif am[i] != bm[i]:
                    for f in UNIT_KEYS[1:]:
                        if am[i].get(f) != bm[i].get(f):
                            out.append(f"{i}.{f}: {_flow(am[i].get(f))} → {_flow(bm[i].get(f))}")
        else:
            out.append(f"{k}: {_flow(a)} → {_flow(b)}")
    return out


def check_surface(slug, surf, repo=None, today=None):
    """Находки R-FRESH-006 одной поверхности: манифест на диске против сборки; файла нет — []."""
    r = docpaths.root(repo)
    p = docpaths.design(slug, "ready", surface=surf.slug, repo=r)
    if not p.is_file():
        return []
    rep = F.Report()
    kw = dict(surface=surf.slug, kind=KIND, ref=surf.slug, path=docpaths.rel(p, r),
              fix=f"ready build {slug} {surf.slug} — на этапе package, после отчёта /design-audit (его error закрывает "
                  "или принимает заказчик)")
    try:
        old = yaml_mod().safe_load(p.read_text(encoding="utf-8"))
    except Exception as e:                                  # noqa: BLE001
        rep.add(RULE, "error", message=f"ready.yaml не разбирается: {str(e).splitlines()[0][:120]}", **kw)
        return rep.items
    new = build(slug, surf, r, today)
    diff = _diff(old if isinstance(old, dict) else {}, new)
    if diff:
        more = f" и ещё {len(diff) - 5}" if len(diff) > 5 else ""
        rep.add(RULE, "error", message="манифест готовности отстал от источников: " + "; ".join(diff[:5]) + more,
                **kw)
    return rep.items


def show_units(slug, surf, repo=None, today=None):
    """Единицы с отпечатками одобрения (артборды строки «Приёмка» и источники единицы): [{id, composition, texts,
    verdict, artboards, review, current, match}]."""
    b = Build(slug, surf, repo, today)
    rev = b.review()
    data = b.run().data
    out = []
    for u in data["units"]:
        row = rev.get(u["id"]) or {}
        cur = b.fingerprint(u["id"], row.get("artboards") or [])
        out.append({"id": u["id"], "composition": u["composition"], "texts": u["texts"],
                    "verdict": row.get("verdict") or "—", "artboards": row.get("artboards") or [],
                    "review": row.get("fingerprint") or "—", "current": cur or "—",
                    "match": bool(cur and cur == row.get("fingerprint")), "mockup": u["mockup"]})
    return out


# ------------------------------------------------------------------ вызов

def _today(ap, s):
    if not s:
        return None
    try:
        return dt.date.fromisoformat(s)
    except ValueError:
        ap.error("--today: ГГГГ-ММ-ДД")


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    _reexec_venv()
    if "--selftest" in argv:
        return _selftest()
    ap = docpaths.parser(TOOL, __doc__, commands=("build", "check", "show"), surface="optional",
                         accept=lambda s: s.design and (s.page or s.app))
    ap.add_argument("--today", metavar="ГГГГ-ММ-ДД", help="дата для сроков фактов (по умолчанию сегодня)")
    call = docpaths.parse(ap, argv)
    today = _today(ap, call.args.today)
    if call.command in ("build", "show") and call.surf is None:
        ap.error(f"{call.command}: нужна поверхность — {call.command} <slug> <surface>")
    try:
        if call.command == "check":
            surfs = [call.surf] if call.surf else [s for s in call.surfaces if s.design and (s.page or s.app)]
            items = []
            for s in surfs:
                items += check_surface(call.slug, s, call.repo, today)
            F.print_findings(items, as_json=call.json)
            return F.exit_code(items)
        if call.command == "show":
            rows = show_units(call.slug, call.surf, call.repo, today)
            if call.json:
                print(json.dumps(rows, ensure_ascii=False, indent=1))
            else:
                for r in rows:
                    mark = "совпал" if r["match"] else ("нет одобрения" if r["review"] == "—" else "не совпал")
                    print(f"{r['id']:<22} {r['composition']:<9} тексты {r['texts']:<9} макет {r['mockup']:<20} "
                          f"{mark}")
                    boards = ", ".join(r["artboards"]) or "— (колонка «артборды» строки «Приёмка»)"
                    print(f"{'':<22} артборды: {boards}")
                    print(f"{'':<22} отпечаток одобрения сейчас: {r['current']}")
            return F.EXIT_OK
        data = build(call.slug, call.surf, call.repo, today)
        text = render(call.slug, data)
        dest = (call.out / FILE) if call.out is not None else docpaths.design(call.slug, "ready",
                                                                             surface=call.surface, repo=call.repo)
        dest.parent.mkdir(parents=True, exist_ok=True)
        old = dest.read_text(encoding="utf-8") if dest.is_file() else None
        if old != text:
            dest.write_text(text, encoding="utf-8")
        if call.json:
            print(json.dumps(data, ensure_ascii=False, indent=1))
        else:
            n = len(data["units"])
            print(f"{docpaths.rel(dest, call.repo)} — {'записан' if old != text else 'без изменений'}: "
                  f"{data['status']}, единиц {n}, готовы {sum(1 for u in data['units'] if u['ready'])}, "
                  f"источников {len(data['sources'])}")
            for b in data["blockers"][:12]:
                print(f"  блокер: {b}")
            if len(data["blockers"]) > 12:
                print(f"  … и ещё {len(data['blockers']) - 12}")
            decide = {}
            for u in data["units"]:
                for o in u["open"]:
                    if o.startswith(DECIDE):
                        decide.setdefault(o[len(DECIDE):], []).append(u["id"])
            for what, ids in decide.items():
                print(f"  {DECIDE}{what} — {', '.join(ids)}")
        return F.EXIT_OK
    except (F.ToolError, docpaths.DocPathError, OSError) as e:
        print(f"{TOOL}: {e}", file=sys.stderr)
        return F.EXIT_USAGE


def _selftest():
    """Фикстуры package-landing (лендинг) и package-cabinet (кабинет) сборщика fixture_project, без сети."""
    import shutil
    import subprocess
    import tempfile
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    today = dt.date(2026, 9, 29)
    me = str(Path(__file__).resolve())
    kbpaths.use("tests")
    import fixture_project

    def cli(*args, cwd):
        return subprocess.run([sys.executable, me, *map(str, args)], cwd=cwd, capture_output=True, text=True)

    with fixture_project.built("package-landing") as fx, tempfile.TemporaryDirectory(prefix="ddd-ready-cwd-") as cwd:
        root, slug = fx.root, fx.slug
        surf = docpaths.surface(slug, "promo", root)
        r = cli("build", slug, "promo", "--repo", root, "--today", "2026-09-29", cwd=cwd)
        path = docpaths.design(slug, "ready", surface="promo", repo=root)
        check("build из чужой рабочей папки с --repo — код 0, файл design/promo/ready.yaml записан",
              r.returncode == 0 and path.is_file())
        data = yaml_mod().safe_load(path.read_text(encoding="utf-8"))
        check("лендинг: type web, web_kind landing, consumer <org>/site, perf plans",
              (data["type"], data["web_kind"], data["consumer"], data["perf"]) == ("web", "landing", "<org>/site",
                                                                                   "plans"))
        check("единицы — страницы планов (home, spasibo), budget_profile — из планов",
              [u["id"] for u in data["units"]] == ["home", "spasibo"]
              and [u["budget_profile"] for u in data["units"]] == ["landing-lead-services@L1", "thank-you-page@L0"])
        check("frontend_design лендинга: surface landing, ambition L1, motion_cap expressive (уровень движения L1)",
              data["frontend_design"] == {"surface": "landing", "ambition": "L1", "motion_cap": "expressive",
                                          "app_screens": "—"})
        check("источники — путь от папки проекта, статус и sha256 файла",
              any(s["path"] == "site/promo/plans/spasibo.yaml" and s["status"] == "approved"
                  and s["sha256"] == sha(docpaths.site(slug, "promo", "plans", "spasibo.yaml", repo=root))
                  for s in data["sources"]))
        check("status not-ready: макета нет — блокеры называют единицы",
              data["status"] == "not-ready" and any(b.startswith("spasibo: макета нет") for b in data["blockers"]))
        check("форма ready.yaml (R-STRUCT-008) — без замечаний", not form_errors(data))
        r = cli("check", slug, "--repo", root, "--today", "2026-09-29", "--json", cwd=cwd)
        check("check сразу после build — код 0, находок нет", r.returncode == 0 and not F.parse_lines(r.stdout))
        text = path.read_text(encoding="utf-8")
        r = cli("build", slug, "promo", "--repo", root, "--today", "2026-09-29", cwd=cwd)
        check("повторная сборка — те же байты («без изменений»)",
              path.read_text(encoding="utf-8") == text and "без изменений" in r.stdout)
        path.write_text(text.replace("surface: promo\n", "example: true\nsurface: promo\n"), encoding="utf-8")
        check("пометка иллюстрации example: true — не расхождение и не ключ вне формы",
              not check_surface(slug, surf, root, today)
              and not form_errors(yaml_mod().safe_load(path.read_text(encoding="utf-8"))))
        path.write_text(text, encoding="utf-8")
        plan = docpaths.site(slug, "promo", "plans", "spasibo.yaml", repo=root)
        ptext = plan.read_text(encoding="utf-8")
        plan.write_text(ptext.replace("goal: подтвердить заявку", "goal: подтвердить заявку на замер"),
                        encoding="utf-8")
        items = check_surface(slug, surf, root, today)
        check("правка источника без build → R-FRESH-006 error с путём манифеста и источником в сообщении",
              len(items) == 1 and items[0].rule == RULE and items[0].severity == "error"
              and items[0].path == docpaths.rel(path, root) and "site/promo/plans/spasibo.yaml" in items[0].message)
        check("совет R-FRESH-006: пересборка на этапе package после отчёта аудита, его error — решение заказчика",
              items and "на этапе package" in items[0].fix and "принимает заказчик" in items[0].fix
              and "без error" not in items[0].fix)
        plan.write_text(ptext, encoding="utf-8")
        bad = dict(data, status="done", units=[dict(data["units"][0], mockup="ok", extra=1)])
        bad.pop("blockers")
        errs = form_errors(bad)
        check("форма: нет ключа и значение вне перечня — error, ключ вне формы — warning",
              any(p == "/blockers" and s == "error" for p, _m, s in errs)
              and any(p == "/status" and s == "error" for p, _m, s in errs)
              and any(p == "/units/0/mockup" and s == "error" for p, _m, s in errs)
              and any(p == "/units/0/extra" and s == "warning" for p, _m, s in errs))
        # одобрение с отпечатком по артбордам и источникам единицы (вход собирается и с ошибкой проверки: главная в
        # работе)
        def ci(stage):
            return subprocess.run([sys.executable, str(HERE / "canvas_input.py"), "build", slug, "promo", "--stage",
                                   stage, "--repo", str(root), "--today", "2026-09-29"], capture_output=True, text=True,
                                  cwd=cwd)

        ci("wireframe")
        proj = docpaths.design(slug, "canvas-project", surface="promo", repo=root)
        proj.mkdir(parents=True, exist_ok=True)
        (proj / "Spasibo.dc.html").write_text("<section id='confirmation'>Заявка на замер принята</section>\n",
                                              encoding="utf-8")
        (proj / "Home.dc.html").write_text("<section id='hero'>Главная</section>\n", encoding="utf-8")
        b = Build(slug, surf, root, today)
        fp_sp, fp_home = b.fingerprint("spasibo", ["Spasibo.dc.html"]), b.fingerprint("home", ["Home.dc.html"])
        rv = docpaths.design(slug, "review", surface="promo", repo=root)
        rv.mkdir(parents=True, exist_ok=True)
        (rv / "REVIEW.md").write_text(
            "# REVIEW\n\nИллюстрация самопроверки.\n\n## Приёмка\n\n"
            "| страница или экран | артборды | вердикт | одобрил | дата | отпечаток | открыто |\n"
            "|---|---|---|---|---|---|---|\n"
            f"| `spasibo` | `Spasibo.dc.html` | `accepted_with_notes` | владелец продукта | 2026-09-29 | {fp_sp} "
            "| — |\n"
            f"| `home` | `Home.dc.html` | `accepted` | владелец продукта | 2026-09-29 | {fp_home} | — |\n",
            encoding="utf-8")
        units = {u["id"]: u for u in build(slug, surf, root, today)["units"]}
        check("вердикт REVIEW.md с совпавшим отпечатком артбордов и источников единицы → mockup accepted_with_notes; "
              "отпечаток — sha256, у единиц разный",
              units["spasibo"]["mockup"] == "accepted_with_notes" and units["home"]["mockup"] == "accepted"
              and str(fp_sp).startswith("sha256:") and fp_sp != fp_home)
        art = docpaths.design(slug, "artifacts", repo=root)
        at = art.read_text(encoding="utf-8")
        art.write_text(at.replace("| 2026-09-29 | аналитик |", "| 2026-10-02 | аналитик |"), encoding="utf-8")
        re_wire = ci("wireframe")
        sysp = docpaths.design(slug, "system", repo=root)
        st = sysp.read_text(encoding="utf-8")
        sysp.write_text(st.replace("status: approved", "status: proposed", 1).replace("starter: []",
                                                                                     "starter: [spasibo]"),
                        encoding="utf-8")
        d = build(slug, surf, root, today)
        units = {u["id"]: u for u in d["units"]}
        check("дата «последнего чтения» в ARTIFACTS.md, пересборка входа, starter и статус system.yaml — одобрение то "
              "же; ДС не утверждена — строка open «решение заказчика», не блокер",
              at.count("| 2026-09-29 | аналитик |") == 2 and re_wire.returncode in (0, 1)
              and "starter: [spasibo]" in sysp.read_text(encoding="utf-8")
              and units["spasibo"]["mockup"] == "accepted_with_notes" and units["home"]["mockup"] == "accepted"
              and f"{DECIDE}ДС не утверждена (system.yaml proposed)" in units["spasibo"]["open"]
              and not any("ДС" in x for x in d["blockers"]))
        mo = ci("motion")
        inp = docpaths.design(slug, "input", surface="promo", repo=root) / "INPUT.md"
        units = {u["id"]: u for u in build(slug, surf, root, today)["units"]}
        check("вход motion заменяет вход макета — одобрение то же",
              mo.returncode in (0, 1) and "stage: motion" in inp.read_text(encoding="utf-8")
              and units["spasibo"]["mockup"] == "accepted_with_notes" and units["home"]["mockup"] == "accepted")
        dk = docpaths.site(slug, "promo", "copy", "spasibo.yaml", repo=root)
        dtext = dk.read_text(encoding="utf-8")
        dk.write_text(dtext.replace("text: 'Вызвать замерщика'", "text: 'Позвать замерщика'", 1), encoding="utf-8")
        d = build(slug, surf, root, today)
        units = {u["id"]: u for u in d["units"]}
        check("правка своего текста в copy deck снимает одобрение единицы (spasibo — mockup none, блокер); правка "
              "copy deck соседней страницы одобрение home не снимает",
              "Позвать замерщика" in dk.read_text(encoding="utf-8") and units["spasibo"]["mockup"] == "none"
              and units["home"]["mockup"] == "accepted" and any("spasibo: одобрение снято" in x for x in d["blockers"]))
        dk.write_text(dtext, encoding="utf-8")
        (proj / "Spasibo.dc.html").write_text("<section id='confirmation'>Заявка принята</section>\n",
                                              encoding="utf-8")
        d = build(slug, surf, root, today)
        units = {u["id"]: u for u in d["units"]}
        check("правка артборда единицы снимает её одобрение (mockup none, блокер), соседней — нет",
              units["spasibo"]["mockup"] == "none" and units["home"]["mockup"] == "accepted"
              and any("spasibo: одобрение снято" in x for x in d["blockers"]))
        rows = show_units(slug, surf, root, today)
        check("show: у единицы — отпечаток из REVIEW.md и текущий, совпадение",
              {r["id"]: r["match"] for r in rows} == {"home": True, "spasibo": False}
              and next(r["current"] for r in rows if r["id"] == "home") == fp_home)
        note = docpaths.root(root).joinpath(*STATE, slug, "design", "promo", "_phase-jump.md")
        note.parent.mkdir(parents=True, exist_ok=True)
        (rv / "REVIEW.md").unlink()
        note.write_text("---\nkind: phase-jump\nref: docs/projects/otves-remont-nn/design/promo/\n---\n\n"
                        "## Доменные решения\n- `mockup` для `spasibo` — макет пропущен: сборка по ДС и плану.\n",
                        encoding="utf-8")
        units = {u["id"]: u for u in build(slug, surf, root, today)["units"]}
        check("решение «макет пропущен» в заметке пропусков → mockup skipped у названной единицы",
              units["spasibo"]["mockup"] == "skipped" and units["home"]["mockup"] == "none")
        shutil.rmtree(note.parents[3])
        r = cli("build", "nope", "promo", "--repo", root, cwd=cwd)
        r2 = cli("build", slug, "--repo", root, cwd=cwd)
        check("нет проекта — код 2; build без поверхности — код 2", r.returncode == 2 and r2.returncode == 2)
    with fixture_project.built("input-landing") as fx, tempfile.TemporaryDirectory(prefix="ddd-ready-cwd-") as cwd:
        root, slug = fx.root, fx.slug
        surf = docpaths.surface(slug, "promo", root)
        ci = subprocess.run([sys.executable, str(HERE / "canvas_input.py"), "build", slug, "promo", "--stage",
                             "wireframe", "--repo", str(root), "--today", "2026-09-29"], capture_output=True, text=True,
                            cwd=cwd)
        r = cli("build", slug, "promo", "--repo", root, "--today", "2026-09-29", cwd=cwd)
        data = yaml_mod().safe_load(docpaths.design(slug, "ready", surface="promo", repo=root).read_text(
            encoding="utf-8"))
        ab = data["units"][0]["after_build"]
        check("лендинг input-landing со входом wireframe: after_build — пункты ACCEPTANCE.md места «после сборки» "
              "(I2, K1, L2 …), единица home, профиль landing-lead-services@L1",
              ci.returncode == 0 and r.returncode == 0 and {"I2", "K1", "L2"} <= set(ab) and "A1" not in ab
              and data["units"][0]["id"] == "home" and data["units"][0]["budget_profile"] == "landing-lead-services@L1")
        r = cli("check", slug, "promo", "--repo", root, "--today", "2026-09-29", cwd=cwd)
        check("input-landing: check сразу после build — код 0", r.returncode == 0 and "0 error" in r.stdout)
    with fixture_project.built("package-cabinet") as fx:
        root, slug = fx.root, fx.slug
        surf = docpaths.surface(slug, "office", root)
        data = build(slug, surf, root, today)
        check("кабинет: consumer <org>/frontend, web_kind app, единицы — пять экранов",
              data["consumer"] == "<org>/frontend" and data["web_kind"] == "app" and len(data["units"]) == 5)
        check("кабинет: perf — поле p75, RUM и сценарии AC-PRF-04…06; budget_profile «—»",
              data["perf"] == PERF_APP and all(u["budget_profile"] == "—" for u in data["units"]))
        check("кабинет: frontend_design — поправки ui C25, уровней нет",
              data["frontend_design"]["app_screens"].startswith("ui/CONTRADICTIONS.md §[C25]")
              and data["frontend_design"]["ambition"] == "—")
        check("кабинет: тексты утверждены — у единиц approved; FSD-карты нет — строка open «решение заказчика» у "
              "каждой единицы, не блокер",
              {u["texts"] for u in data["units"]} == {"approved"}
              and all(f"{DECIDE}FSD-карты нет" in u["open"] for u in data["units"])
              and not any("FSD" in b for b in data["blockers"]))
        dest = docpaths.design(slug, "ready", surface="office", repo=root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(render(slug, data), encoding="utf-8")
        check("кабинет: check сразу после записи — 0", not check_surface(slug, surf, root, today))
        tp = docpaths.project(slug, "screens", "office", "texts.md", repo=root)
        lines = tp.read_text(encoding="utf-8").splitlines(keepends=True)
        k = next(i for i, x in enumerate(lines) if x.startswith("| `requests.new.client.label` |"))
        lines[k] = lines[k].replace("| `approved` |", "| `checked` |")
        tp.write_text("".join(lines), encoding="utf-8")
        low = {u["id"]: u["texts"] for u in build(slug, surf, root, today)["units"]}
        check("кабинет: тексты единицы — наименьший статус её строк texts.md (подпись поля бланка checked → "
              "request-new checked, прочие approved)",
              low.get("request-new") == "checked" and {v for u, v in low.items() if u != "request-new"} == {"approved"})
        # готовность — гейты 2–4 и закрытая композиция: ДС, покрытие ДС типов экрана и FSD-карта — решения заказчика
        sysp = docpaths.design(slug, "system", repo=root)
        st = sysp.read_text(encoding="utf-8")
        sysp.write_text(st.replace("  KpiTile: {component: KpiTile}\n",
                                   "  KpiTile: {component: KpiTile, optional_states: [bogus]}\n"), encoding="utf-8")
        proj = docpaths.design(slug, "canvas-project", surface="office", repo=root)
        proj.mkdir(parents=True, exist_ok=True)
        (proj / "PlanDashboard.dc.html").write_text("<main data-screen='plan-dashboard'>План</main>\n",
                                                    encoding="utf-8")
        fp = Build(slug, surf, root, today).fingerprint("plan-dashboard", ["PlanDashboard.dc.html"])
        rv = docpaths.design(slug, "review", surface="office", repo=root)
        rv.mkdir(parents=True, exist_ok=True)
        (rv / "REVIEW.md").write_text(
            "# REVIEW\n\nИллюстрация самопроверки.\n\n## Приёмка\n\n"
            "| страница или экран | артборды | вердикт | одобрил | дата | отпечаток | открыто |\n"
            "|---|---|---|---|---|---|---|\n"
            f"| `plan-dashboard` | `PlanDashboard.dc.html` | `accepted` | владелец продукта | 2026-09-29 | {fp} "
            "| — |\n", encoding="utf-8")
        sysp.write_text(sysp.read_text(encoding="utf-8").replace("status: approved", "status: proposed", 1)
                        + "starter: [plan-dashboard]\n", encoding="utf-8")
        d = build(slug, surf, root, today)
        units = {u["id"]: u for u in d["units"]}
        pd = units["plan-dashboard"]
        cov_lines = {u: [o for o in x["open"] if o.startswith(f"{DECIDE}покрытие ДС")] for u, x in units.items()}
        check("кабинет: FSD-карты нет, ДС не утверждена, у KpiTile optional_states вне словаря — plan-dashboard готова "
              "(макет принят, отпечаток совпал после starter и статуса ДС), решения заказчика — строки open; "
              "покрытие — только у экрана с KpiTile; блокеров о ДС, покрытии и FSD нет; статус partial",
              pd["ready"] and pd["mockup"] == "accepted" and d["status"] == "partial"
              and f"{DECIDE}FSD-карты нет" in pd["open"]
              and f"{DECIDE}ДС не утверждена (system.yaml proposed)" in pd["open"]
              and len(cov_lines["plan-dashboard"]) == 1 and "KpiTile" in cov_lines["plan-dashboard"][0]
              and not any(v for u, v in cov_lines.items() if u != "plan-dashboard")
              and not any(w in x for x in d["blockers"] for w in ("ДС", "FSD", "покрытие")))
        r = subprocess.run([sys.executable, me, "build", slug, "office", "--repo", str(root), "--today", "2026-09-29"],
                           capture_output=True, text=True)
        check("build: решения заказчика — строками «решение заказчика: …» с единицами",
              r.returncode == 0 and f"{DECIDE}FSD-карты нет — not-found, plan-dashboard" in r.stdout)
    print("ready selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
