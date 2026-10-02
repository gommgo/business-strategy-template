#!/usr/bin/env python3
"""fixture_project — сборщик демо-проекта во временную папку для прогонов и самопроверок утилит `scripts/project/`.

Фикстура — папка `scripts/tests/fixtures/<имя>/` с манифестом `manifest.yaml` и своими файлами. Сборщик раскладывает
дерево `docs/projects/<project>/…` в корень сборки из слоёв манифеста — по порядку, поздний слой перекрывает ранний.
Источники фикстуры — только её файлы и файлы фикстур, которые она продолжает (`extends`): из `kb/` сборщик ничего не
берёт, поэтому правка примера базы фикстуру не меняет. Корень сборки — корень данных утилит: `<утилита> <команда>
<slug> --repo <корень>` (или переменная DDD_REPO, модуль `lib/docpaths.py`).

Манифест (YAML):

    example: true                   # фикстура — иллюстрация, не данные проекта
    description: <одна фраза>       # что за проект и для каких прогонов
    project: <slug>                 # папка docs/projects/<slug>/; пути назначения — от неё
    extends: [<фикстура>, …]        # по желанию: эти фикстуры собираются раньше в тот же корень (их проекты — рядом,
                                    # тот же slug — слои продолжают тот же проект); общая база нескольких extends
                                    # собирается один раз; цепочка extends — не длиннее двух звеньев
    unmarked: [<путь>, …]           # по желанию: свои файлы и папки без пометки иллюстрации — пути от папки фикстуры
    layers:                         # по порядку; у слоя один ключ
      - files: files                # свои файлы: папка фикстуры раскладывается от папки проекта
      - files:                      # или поштучно: путь назначения ← путь от папки фикстуры (файл или папка)
          design/promo/ready.yaml: seeded/ready-stale.yaml
      - replace:                    # правка положенного файла: find встречается ровно count раз (по умолчанию 1)
          site/promo/plans/home.yaml:
            - {find: "status: proposed", to: "status: approved"}
      - drop: [voice.yaml]          # убрать положенный раньше файл или папку

Пути назначения — относительные, без «..». Правка `replace` меняет файл основы или свой файл, положенный слоем раньше.
Свои файлы — иллюстрация: машинные (.yaml, .yml, .json) несут `example: true` на верхнем уровне, md — слово
«иллюстрация» в первых десяти строках. Файл, формат которого пометку не несёт (исходники холста и артефакт ДС, файл в
форме, которую читает утилита проекта), назван в `unmarked` манифеста. Самопроверка сверяет пометки, манифесты и длину
цепочек `extends` у всех фикстур папки.

    python3 scripts/tests/fixture_project.py list [--json]
    python3 scripts/tests/fixture_project.py build <имя> [--out DIR] [--json]   # печатает корень сборки
    python3 scripts/tests/fixture_project.py --selftest

Без --out сборка ложится в $DDD_HOME/out/tests/fixtures/<имя>/ и пересобирается там же; папка --out — пустая или
прежняя сборка (файл .ddd-fixture.json в корне). Код выхода: 0 — собрано; 1 — самопроверка не прошла; 2 — ошибка вызова
или манифеста. Для самопроверок других утилит — контекст с временной папкой, которая убирается после блока:

    kbpaths.use("tests"); import fixture_project
    with fixture_project.built("minimal") as fx:          # fx.root — корень данных, fx.slug — проект
        subprocess.run([sys.executable, tool, "check", fx.slug, "--repo", str(fx.root)])

Опорная дата фикстур — `fixture_project.today()`: сроки фактов, записи проверок и одобрения в файлах фикстур считаются
от неё, поэтому прогон на фикстуре получает её ключом `--today`. Дата записана один раз — ключ `today` файла
`scripts/maint/data/sync.yaml`.
"""
import argparse
import contextlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402

FIXTURES = HERE / "fixtures"
SENTINEL = ".ddd-fixture.json"
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
KEYS = ("example", "description", "project", "extends", "unmarked", "layers")
LAYER_KEYS = ("files", "replace", "drop")
MAX_EXTENDS = 2                                         # звеньев extends в цепочке: фикстура → основа → её основа
MACHINE = (".yaml", ".yml", ".json")
MARK = "иллюстрац"                                      # пометка своих md-файлов фикстуры
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class FixtureError(ValueError):
    """Ошибка манифеста, фикстуры или папки сборки (код выхода 2)."""


@dataclass
class Built:
    """Итог сборки: корень данных, проект фикстуры и разложенные файлы."""
    name: str
    root: Path
    slug: str
    projects: list = field(default_factory=list)
    files: dict = field(default_factory=dict)           # путь от корня → откуда: fixtures/<имя>/…, replace

    @property
    def project(self):
        return self.root / "docs" / "projects" / self.slug


def today():
    """Опорная дата фикстур `ГГГГ-ММ-ДД` — ключ today данных сверки обслуживания (FixtureError — даты нет)."""
    import yaml
    path = kbpaths.data("maint", "sync.yaml")
    value = str((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("today", ""))
    if not DATE.match(value):
        raise FixtureError(f"{path}: нужна опорная дата фикстур today (ГГГГ-ММ-ДД)")
    return value


def names(fixtures=FIXTURES):
    """Имена фикстур: папки с manifest.yaml."""
    d = Path(fixtures)
    return sorted(p.name for p in d.iterdir() if (p / "manifest.yaml").is_file()) if d.is_dir() else []


def load(name, fixtures=FIXTURES):
    """Манифест фикстуры, проверенный по форме (FixtureError)."""
    import yaml
    path = Path(fixtures) / name / "manifest.yaml"
    if not path.is_file():
        raise FixtureError(f"нет фикстуры {name!r}: {path} (есть: {', '.join(names(fixtures)) or '—'})")
    try:
        m = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise FixtureError(f"{path}: YAML не разбирается: {e}") from e
    if not isinstance(m, dict):
        raise FixtureError(f"{path}: манифест — словарь")
    extra = sorted(set(m) - set(KEYS))
    if extra:
        raise FixtureError(f"{path}: неизвестные ключи {extra} (есть: {', '.join(KEYS)})")
    if m.get("example") is not True:
        raise FixtureError(f"{path}: нужен example: true — фикстура иллюстрация")
    if not SLUG.match(str(m.get("project") or "")):
        raise FixtureError(f"{path}: project — slug проекта (kebab-case), не {m.get('project')!r}")
    ext = m.get("extends") or []
    m["extends"] = [ext] if isinstance(ext, str) else list(ext)
    plain = m.get("unmarked") or []
    if not (isinstance(plain, list) and all(isinstance(u, str) for u in plain)):
        raise FixtureError(f"{path}: unmarked — список путей от папки фикстуры")
    m["unmarked"] = plain
    layers = m.get("layers") or []
    if not isinstance(layers, list):
        raise FixtureError(f"{path}: layers — список слоёв")
    for i, lay in enumerate(layers, 1):
        if not (isinstance(lay, dict) and len(lay) == 1 and next(iter(lay)) in LAYER_KEYS):
            raise FixtureError(f"{path}: слой {i} — словарь с одним ключом из {', '.join(LAYER_KEYS)}")
    m["layers"] = layers
    return m


def _dest(path, rel_path):
    p = str(rel_path).strip()
    parts = Path(p).parts
    if not p or Path(p).is_absolute() or ".." in parts or p.startswith("~"):
        raise FixtureError(f"{path}: путь назначения {rel_path!r} — относительный, без «..»")
    return Path(*parts)


def _expand(src, dest):
    """Файл → [(dest, src)]; папка → все её файлы по порядку, с той же раскладкой под dest."""
    if src.is_file():
        return [(dest, src)]
    return [(dest / f.relative_to(src), f) for f in sorted(src.rglob("*"))
            if f.is_file() and "__pycache__" not in f.parts]


def chain(name, fixtures=FIXTURES, _stack=()):
    """Самая длинная цепочка extends от фикстуры: [фикстура, основа, основа основы, …] (FixtureError — цикл)."""
    if name in _stack:
        raise FixtureError(f"цикл extends: {' → '.join(_stack + (name,))}")
    tails = [chain(base, fixtures, _stack + (name,)) for base in load(name, fixtures)["extends"]]
    return [name] + (max(tails, key=len) if tails else [])


def plan(name, fixtures=FIXTURES, _stack=(), _done=None):
    """Операции сборки по порядку: ("copy", путь от docs/projects, источник, откуда), ("replace", путь, правки),
    ("drop", путь). Сначала фикстуры extends, затем свои слои; фикстура, которая входит через несколько extends
    (общая база двух слоёв), собирается один раз — первой по порядку. Цепочка extends длиннее MAX_EXTENDS звеньев —
    ошибка: такую фикстуру собирают своими файлами."""
    if _done is None:
        links = chain(name, fixtures)
        if len(links) - 1 > MAX_EXTENDS:
            raise FixtureError(f"цепочка extends длиннее {MAX_EXTENDS} звеньев: {' → '.join(links)}")
    done = set() if _done is None else _done
    fdir = Path(fixtures) / name
    m = load(name, fixtures)
    mpath = fdir / "manifest.yaml"
    ops = []
    for base in m["extends"]:
        if base not in done:
            ops += plan(base, fixtures, _stack + (name,), done)
    done.add(name)
    proj = Path(m["project"])
    for lay in m["layers"]:
        (kind, body), = lay.items()
        if kind == "files":
            pairs = {".": body} if isinstance(body, str) else body
            if not isinstance(pairs, dict):
                raise FixtureError(f"{mpath}: files — папка фикстуры или словарь «путь назначения: путь от фикстуры»")
            for dest, src in pairs.items():
                s = fdir / _dest(mpath, src)
                if not s.exists():
                    raise FixtureError(f"{mpath}: нет своего файла {s.relative_to(fdir)}")
                for d, f in _expand(s, proj / _dest(mpath, dest)):
                    ops.append(("copy", d, f, "fixtures/" + f.relative_to(Path(fixtures)).as_posix()))
        elif kind == "replace":
            if not isinstance(body, dict):
                raise FixtureError(f"{mpath}: replace — словарь «путь: [{{find, to, count}}]»")
            for dest, edits in body.items():
                edits = [edits] if isinstance(edits, dict) else edits
                if not edits or not all(isinstance(e, dict) and "find" in e and "to" in e for e in edits):
                    raise FixtureError(f"{mpath}: replace {dest}: правки — {{find, to[, count]}}")
                ops.append(("replace", proj / _dest(mpath, dest), edits, "replace"))
        else:
            items = [body] if isinstance(body, str) else body
            for dest in items or []:
                ops.append(("drop", proj / _dest(mpath, dest), None, "drop"))
    return ops


def _prepare(out):
    out = Path(out).expanduser()
    if out.exists() and not out.is_dir():
        raise FixtureError(f"{out}: не папка")
    if out.is_dir() and any(out.iterdir()):
        if not (out / SENTINEL).is_file():
            raise FixtureError(f"{out}: папка не пуста и не собрана сборщиком (нет {SENTINEL})")
        for p in out.iterdir():
            shutil.rmtree(p) if p.is_dir() and not p.is_symlink() else p.unlink()
    out.mkdir(parents=True, exist_ok=True)
    return out.resolve()


def build(name, out=None, fixtures=FIXTURES):
    """Собрать фикстуру в out (по умолчанию $DDD_HOME/out/tests/fixtures/<имя>/) → Built."""
    ops = plan(name, fixtures)
    m = load(name, fixtures)
    root = _prepare(out if out is not None else kbpaths.out("tests", "fixtures", name))
    base = root / "docs" / "projects"
    files = {}
    for kind, dest, src, origin in ops:
        target = base / dest
        key = (Path("docs", "projects") / dest).as_posix()
        if kind == "copy":
            if target.is_dir():
                shutil.rmtree(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
            files[key] = origin
        elif kind == "replace":
            if not target.is_file():
                raise FixtureError(f"{name}: replace — нет файла {key}")
            text = target.read_text(encoding="utf-8")
            for e in src:
                want = int(e.get("count", 1))
                got = text.count(str(e["find"]))
                if got != want:
                    raise FixtureError(f"{name}: replace {key}: «{e['find']}» встречается {got} раз, ждали {want}")
                text = text.replace(str(e["find"]), str(e["to"]))
            target.write_text(text, encoding="utf-8")
            files[key] = files.get(key, "") + " + replace"
        else:
            if not target.exists():
                raise FixtureError(f"{name}: drop — нет {key}")
            if target.is_dir():
                shutil.rmtree(target)
                files = {k: v for k, v in files.items() if not k.startswith(key + "/")}
            else:
                target.unlink()
                files.pop(key, None)
    projs = sorted(p.name for p in base.iterdir() if p.is_dir()) if base.is_dir() else []
    (root / SENTINEL).write_text(json.dumps({"fixture": name, "project": m["project"], "projects": projs},
                                            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return Built(name=name, root=root, slug=m["project"], projects=projs, files=dict(sorted(files.items())))


@contextlib.contextmanager
def built(name, fixtures=FIXTURES):
    """Собрать фикстуру во временную папку на время блока `with` → Built; папка убирается после блока."""
    with tempfile.TemporaryDirectory(prefix=f"ddd-fixture-{name}-") as td:
        yield build(name, td, fixtures)


def mark_issue(f):
    """Пометка иллюстрации своего файла: example: true у машинного, «иллюстрация» в md. → замечание или ""."""
    import yaml
    f = Path(f)
    if f.suffix in MACHINE:
        try:
            data = json.loads(f.read_text(encoding="utf-8")) if f.suffix == ".json" else \
                yaml.safe_load(f.read_text(encoding="utf-8"))
        except (ValueError, yaml.YAMLError) as e:
            return f"не разбирается ({str(e).splitlines()[0][:80]})"
        if not (isinstance(data, dict) and data.get("example") is True):
            return "нет example: true на верхнем уровне"
    elif f.suffix == ".md":
        head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:10]).lower()
        if MARK not in head:
            return "нет пометки «иллюстрация» в первых строках"
    return ""


def lint(name, fixtures=FIXTURES):
    """Пометки своих файлов фикстуры, кроме названных в unmarked манифеста. → список замечаний."""
    fdir = Path(fixtures) / name
    mpath = fdir / "manifest.yaml"
    plain = [(u, fdir / _dest(mpath, u)) for u in load(name, fixtures)["unmarked"]]
    issues = [f"{name}: unmarked «{u}» — такого файла или папки в фикстуре нет" for u, p in plain if not p.exists()]
    for f in sorted(fdir.rglob("*")):
        if not f.is_file() or f.name == "manifest.yaml" or "__pycache__" in f.parts:
            continue
        if any(f == p or p in f.parents for _, p in plain):
            continue
        issue = mark_issue(f)
        if issue:
            issues.append(f"{f.relative_to(Path(fixtures)).as_posix()}: {issue}")
    return issues


def _selftest():
    import yaml
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    def raises(fn):
        try:
            fn()
        except FixtureError:
            return True
        return False

    all_names = names()
    check(f"фикстуры папки: {', '.join(all_names) or '—'} (есть minimal)", "minimal" in all_names)
    check(f"опорная дата фикстур: {today()}", bool(DATE.match(today())))
    for n in all_names:
        try:
            ops = plan(n)
            check(f"{n}: манифест и источники слоёв на месте ({len(ops)} операций)", bool(ops))
        except FixtureError as e:
            check(f"{n}: манифест — {e}", False)
        issues = lint(n)
        check(f"{n}: свои файлы помечены иллюстрацией" + (f" — {'; '.join(issues[:3])}" if issues else ""), not issues)
    with tempfile.TemporaryDirectory(prefix="ddd-fixture-selftest-") as td:
        out = Path(td) / "root"
        fx = build("minimal", out)
        proj = fx.project
        check("build minimal: корень и проект", proj.is_dir() and (out / SENTINEL).is_file() and fx.slug == "otves-remont-nn")
        m = load("minimal")
        same = True
        for key, origin in fx.files.items():
            if "replace" in origin:
                continue
            same = same and (out / key).read_bytes() == (FIXTURES / origin[len("fixtures/"):]).read_bytes()
        check(f"build minimal: {len(fx.files)} файлов — байт в байт как свои файлы фикстуры", same and fx.files)
        own = FIXTURES / "minimal" / "files"
        want = {(Path("docs/projects") / m["project"] / f.relative_to(own)).as_posix() for f in own.rglob("*")
                if f.is_file()}
        check("build minimal: все свои файлы папки files разложены", want and want == set(fx.files))
        again = build("minimal", out)
        check("повторная сборка в ту же папку — тот же набор файлов", again.files == fx.files)
        busy = Path(td) / "busy"
        busy.mkdir()
        (busy / "note.txt").write_text("чужое", encoding="utf-8")
        check("чужая непустая папка --out — ошибка", raises(lambda: build("minimal", busy)))
        kbpaths.use("lib")
        import docpaths
        check("docpaths --repo <корень сборки>: проект и две поверхности",
              docpaths.projects(out) == [fx.slug] and len(docpaths.surfaces(fx.slug, out)) == 2)
        # слои манифеста: порядок, extends, replace, drop, папка своих файлов, защита путей — на синтетических фикстурах
        fx_dir = Path(td) / "fixtures"
        (fx_dir / "base" / "own" / "plans").mkdir(parents=True)
        (fx_dir / "base" / "own" / "note.md").write_text("# note\n> Иллюстрация.\nпервый\n", encoding="utf-8")
        for page in ("home", "contacts"):
            (fx_dir / "base" / "own" / "plans" / f"{page}.yaml").write_text(f"example: true\npage_id: {page}\n",
                                                                             encoding="utf-8")
        (fx_dir / "base" / "own" / "voice.yaml").write_text("voice_version: 1\n", encoding="utf-8")
        (fx_dir / "base" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "база", "project": "demo-a", "unmarked": ["own/voice.yaml"],
            "layers": [{"files": "own"}]}, allow_unicode=True), encoding="utf-8")
        (fx_dir / "top" / "own").mkdir(parents=True)
        (fx_dir / "top" / "own" / "note.md").write_text("# note\n> Иллюстрация.\nвторой\n", encoding="utf-8")
        (fx_dir / "top" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "поверх базы", "project": "demo-a", "extends": ["base", "other"],
            "layers": [{"files": {"note.md": "own/note.md"}},
                       {"replace": {"note.md": [{"find": "второй", "to": "третий"}]}},
                       {"drop": ["voice.yaml"]}]}, allow_unicode=True), encoding="utf-8")
        (fx_dir / "other").mkdir()
        (fx_dir / "other" / "facts.yaml").write_text("example: true\nfacts: []\n", encoding="utf-8")
        (fx_dir / "other" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "второй проект", "project": "demo-b",
            "layers": [{"files": {"facts.yaml": "facts.yaml"}}]}, allow_unicode=True), encoding="utf-8")
        t = build("top", Path(td) / "t", fx_dir)
        a = t.root / "docs" / "projects" / "demo-a"
        check("extends: оба проекта в одном корне", t.projects == ["demo-a", "demo-b"])
        check("files: папка своих файлов целиком, с вложенными папками",
              sorted(p.name for p in (a / "plans").glob("*")) == ["contacts.yaml", "home.yaml"])
        check("пометки: файл из unmarked не проверяется, остальные помечены", lint("base", fx_dir) == [])
        (fx_dir / "base" / "own" / "plans" / "home.yaml").write_text("page_id: home\n", encoding="utf-8")
        found = lint("base", fx_dir)
        check("пометки: машинный файл без example: true — замечание с путём",
              len(found) == 1 and "base/own/plans/home.yaml" in found[0])
        (fx_dir / "base" / "own" / "plans" / "home.yaml").write_text("example: true\npage_id: home\n", encoding="utf-8")
        (fx_dir / "base" / "own" / "voice.yaml").unlink()
        check("пометки: путь unmarked без файла — замечание", any("unmarked" in x for x in lint("base", fx_dir)))
        check("поздний слой перекрывает ранний, replace правит текст", "третий" in (a / "note.md").read_text("utf-8"))
        check("drop убирает положенный раньше файл", not (a / "voice.yaml").exists() and "docs/projects/demo-a/voice.yaml"
              not in t.files)
        for n, ext, lay in (("dia-base", [], [{"files": {"n.md": "own/n.md"}},
                                               {"replace": {"n.md": [{"find": "первый", "to": "база"}]}}]),
                            ("dia-a", ["dia-base"], []), ("dia-b", ["dia-base"], []),
                            ("dia-top", ["dia-a", "dia-b"], [])):
            (fx_dir / n / "own").mkdir(parents=True)
            (fx_dir / n / "own" / "n.md").write_text("# n\n> Иллюстрация.\nпервый\n", encoding="utf-8")
            (fx_dir / n / "manifest.yaml").write_text(yaml.safe_dump({
                "example": True, "description": "ромб", "project": "demo-d", "extends": ext, "layers": lay},
                allow_unicode=True), encoding="utf-8")
        check("ромб extends: общая база собирается один раз", not raises(lambda: build("dia-top", Path(td) / "d", fx_dir))
              and "база" in (Path(td) / "d" / "docs" / "projects" / "demo-d" / "n.md").read_text("utf-8"))
        check("цепочка extends из двух звеньев — собирается",
              chain("dia-top", fx_dir) == ["dia-top", "dia-a", "dia-base"])
        (fx_dir / "dia-over").mkdir()
        (fx_dir / "dia-over" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "третье звено", "project": "demo-d", "extends": ["dia-top"], "layers": []},
            allow_unicode=True), encoding="utf-8")
        check("цепочка extends из трёх звеньев — ошибка", raises(lambda: plan("dia-over", fx_dir)))
        (fx_dir / "dia-over" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "слой базы", "project": "demo-d",
            "layers": [{"kb": {"facts.yaml": "text/facts.yaml"}}]}, allow_unicode=True), encoding="utf-8")
        check("слой kb — ошибка: источники фикстуры — её файлы", raises(lambda: load("dia-over", fx_dir)))
        (fx_dir / "top" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "плохая правка", "project": "demo-a", "extends": ["base"],
            "layers": [{"replace": {"note.md": [{"find": "нет такого", "to": "x"}]}}]}, allow_unicode=True),
            encoding="utf-8")
        check("replace без вхождения — ошибка", raises(lambda: build("top", Path(td) / "t2", fx_dir)))
        (fx_dir / "top" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "побег", "project": "demo-a",
            "layers": [{"files": {"../escape.md": "own/note.md"}}]}, allow_unicode=True), encoding="utf-8")
        check("путь назначения с «..» — ошибка", raises(lambda: plan("top", fx_dir)))
        (fx_dir / "top" / "manifest.yaml").write_text(yaml.safe_dump({
            "example": True, "description": "цикл", "project": "demo-a", "extends": ["top"], "layers": []},
            allow_unicode=True), encoding="utf-8")
        check("цикл extends — ошибка", raises(lambda: plan("top", fx_dir)))
        (fx_dir / "other" / "manifest.yaml").write_text("description: x\nproject: demo-b\nlayers: []\n",
                                                        encoding="utf-8")
        check("нет example: true — ошибка", raises(lambda: load("other", fx_dir)))
    with built("minimal") as fx:
        tmp_root = fx.root
        check("built(): временная сборка на время блока", fx.project.is_dir())
    check("built(): папка убрана после блока", not tmp_root.exists())
    print("fixture_project selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true",
                    help="самопроверка: манифесты, цепочки extends и пометки всех фикстур, сборка minimal")
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="собрать фикстуру; печатает корень сборки (корень данных для --repo)")
    b.add_argument("name")
    b.add_argument("--out", metavar="DIR", help="папка сборки (пустая или прежняя сборка); по умолчанию "
                   "$DDD_HOME/out/tests/fixtures/<имя>/")
    b.add_argument("--json", action="store_true", help="корень, проекты и файлы с источниками")
    ls = sub.add_parser("list", help="фикстуры: имя, проект, описание")
    ls.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    try:
        if a.cmd == "build":
            fx = build(a.name, a.out)
            if a.json:
                print(json.dumps({"fixture": fx.name, "root": str(fx.root), "project": fx.slug, "projects": fx.projects,
                                  "files": [{"path": k, "from": v} for k, v in fx.files.items()]},
                                 ensure_ascii=False, indent=1))
            else:
                print(fx.root)
            return 0
        if a.cmd == "list":
            rows = [(n, load(n)) for n in names()]
            if a.json:
                print(json.dumps([{"name": n, "project": m["project"], "extends": m["extends"],
                                   "description": m.get("description", "")} for n, m in rows],
                                 ensure_ascii=False, indent=1))
            else:
                for n, m in rows:
                    print(f"{n:<20} {m['project']:<24} {m.get('description', '')}")
            return 0
    except FixtureError as e:
        print(f"fixture_project: {e}", file=sys.stderr)
        return 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
