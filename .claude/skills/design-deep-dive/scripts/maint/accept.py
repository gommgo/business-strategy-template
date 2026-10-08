#!/usr/bin/env python3
"""accept — приёмка правки шаблона одним вызовом: файлы по маскам, разбор, ссылки, следы, смоук.

Для того, кто развивает шаблон и принимает работу нескольких исполнителей: у каждого свой набор файлов (зона), общих
файлов нет. Изменённые файлы — рабочее дерево против базового коммита (`--base`, по умолчанию `HEAD`) плюс
неотслеживаемые; скрытое `.gitignore` не считается. Проверки:
  • маски — путь каждого изменённого файла лежит под маской зоны (`--mask`, `--masks-file`); остальные пути идут
    отдельным списком «вне масок». Содержимое проверяется только у файлов под масками; без масок сверки путей нет и
    проверяются все изменённые файлы;
  • ссылки — `.md`: находки `refcheck.py --strict` (битые ссылки и следы forward-only) в новых и изменённых строках —
    по номерам строк диффа против базы; находки в нетронутых строках — счётом, приёмку они не роняют; md фикстур
    и материала к разбору не сверяются (маски `links_skip` данных). `.yaml`, `.yml`: путь файла в комментарии новой
    или изменённой строки, по которому файла нет (от папки файла, `kb/`, корня скилла и репозитория — правила путей
    `refcheck.py`), — находка, в нетронутых строках — счётом: шапка каталога не ссылается на снятый файл;
  • разбор — `.json`, `.yaml`, `.yml` читаются; `*.schema.json` и `*.schema.yaml` проходят метасхему Draft 2020-12;
  • код — `.py` компилируется;
  • следы — новые и изменённые строки `.py`: образцы `forward-only` из `scripts/maint/data/traces.tsv` (те же, что у
    текстов) — находка, в нетронутых строках — счётом; образцы, у которых в коде есть законные места, — список
    «на разбор» без отказа (`trace_review` и `trace_review_forward_only` данных); `--no-trace` — следы не искать;
  • смоук — `--smoke ПАПКА[,ПАПКА…]`: `scripts/tests/smoke.py --only ПАПКА` по каждой папке; FAIL и папка без единой
    строки смоука — находка.

Маска — glob от корня репозитория: `*` — любые знаки вместе с «/» (`.claude/skills/design-audit/*` — папка со всем
вложенным), `?` — один знак, `[…]` — набор; маска без знаков glob — файл или папка целиком. Ключ `--mask` повторяется;
`--masks-file` — файл масок: маска на строку, пустые строки и строки с «#» в начале пропускаются. Данные утилиты —
`scripts/maint/data/accept.yaml`: исключения сверки ссылок и образцы «на разбор» — строками данных, а не кодом.

    python3 .claude/skills/design-deep-dive/scripts/maint/accept.py [--base REF] --mask GLOB [--mask GLOB …]
                                                                     [--masks-file ФАЙЛ] [--smoke ПАПКА[,ПАПКА…]]
                                                                     [--no-trace] [--json]
    python3 .claude/skills/design-deep-dive/scripts/maint/accept.py --selftest

Итог — таблица проверок и списки находок в stdout; с `--json` — один документ JSON вместо таблицы. Репозиторий — тот,
в котором лежит скилл (`scripts/lib/kbpaths.py`): утилита работает из любой рабочей папки и из соседнего чекаута.
Нужны git, PyYAML и jsonschema: без модулей в текущем Python утилита один раз перезапускается в Python окружения скилла.
Код выхода: 0 — чисто; 1 — есть пути вне масок, ошибки разбора или компиляции, находки в новых и изменённых строках
или FAIL смоука; 2 — ошибка вызова или окружения (нет базового коммита, файла масок, git, модуля).
"""
from __future__ import annotations

import argparse
import contextlib
import fnmatch
import importlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

kbpaths.use("maint")
import refcheck  # noqa: E402

ROOT = kbpaths.repo()
SMOKE = kbpaths.scripts("tests", "smoke.py")
DATA = kbpaths.data("maint", "accept.yaml")
ENV_REEXEC = "DDD_ACCEPT_VENV"
DATA_EXT = (".json", ".yaml", ".yml")
SCHEMA_EXT = (".schema.json", ".schema.yaml")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)
YAML_COMMENT = re.compile(r"(?:^|\s)#(.*)$")                # комментарий строки YAML: «#» в начале или после пробела
YAML_PATH = re.compile(r"(?<![\w./:<>…*-])((?:\.{1,2}/)*(?:[\w.-]+/)+[\w.-]+\.(?:json|ya?ml|md|py|tsv|csv))(?![\w/-])")
SMOKE_COUNT = re.compile(r"\b(PASS|FAIL|XFAIL|XPASS) (\d+)")
SMOKE_STATUSES = ("PASS", "FAIL", "XFAIL", "XPASS")
# Переменные, которыми вызывающий процесс (хук, обёртка) направляет git в другой репозиторий: приёмка их не наследует.
GIT_ENV_DROP = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR", "GIT_OBJECT_DIRECTORY",
                "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE")
GIT_ENV: dict[str, str] = {}                             # добавка к окружению git: самопроверка снимает общие настройки
STATUS_WORD = {"A": "новый", "?": "новый", "D": "удалён"}
SKIP = "—"                                               # проверка не запускалась


class CallError(Exception):
    """Ошибка вызова или окружения (код выхода 2)."""


def _reexec_venv():
    """Без PyYAML или jsonschema в текущем Python — один перезапуск в Python окружения скилла."""
    import importlib.util
    if all(importlib.util.find_spec(m) is not None for m in ("yaml", "jsonschema")):
        return
    in_venv = Path(sys.prefix).resolve() == kbpaths.venv().resolve()   # у venv python — ссылка на системный
    if os.environ.get(ENV_REEXEC) or in_venv or not kbpaths.venv("bin", "python").exists():
        return
    os.environ[ENV_REEXEC] = "1"
    py = kbpaths.python()
    os.execv(py, [py, str(Path(__file__).resolve())] + sys.argv[1:])


def _module(name: str):
    """Модуль окружения скилла; нет модуля — ошибка окружения с подсказкой, чем его поставить."""
    try:
        return importlib.import_module(name)
    except ImportError as e:
        raise CallError(f"нужен модуль {name}: Python окружения скилла {kbpaths.venv('bin', 'python')} "
                        f"(ставит scripts/install.sh)") from e


# ─────────────────────────────── git: изменённые файлы и строки ───────────────────────────────

def git(root: Path, *args: str, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
    """git в репозитории root: пути без кавычек и экранирования, pathspec — буквально, без попутной записи индекса
    (рядом в том же дереве работают другие); код не из ok — ошибка вызова."""
    env = {k: v for k, v in os.environ.items() if k not in GIT_ENV_DROP}
    env.update(GIT_ENV, GIT_LITERAL_PATHSPECS="1", GIT_OPTIONAL_LOCKS="0")
    try:
        r = subprocess.run(["git", "-C", str(root), "-c", "core.quotepath=off", *args], env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
    except OSError as e:
        raise CallError(f"git не запускается: {e}") from e
    if r.returncode not in ok:
        tail = (r.stderr.strip().splitlines() or [f"код {r.returncode}"])[-1]
        raise CallError(f"git {args[0]}: {tail}")
    return r


def changed(root: Path, base: str) -> dict[str, str]:
    """Изменённые файлы → {путь от корня: статус}: «A» — новый против базы, «M» — изменён, «D» — удалён,
    «?» — неотслеживаемый. Переименование — удаление старого пути и новый файл: оба пути сверяются с масками."""
    if not base or base.startswith("-"):
        raise CallError(f"--base: «{base}» — не имя коммита")
    r = git(root, "rev-parse", "--is-inside-work-tree", ok=(0, 128))
    if r.returncode or r.stdout.strip() != "true":
        raise CallError(f"{root}: не рабочее дерево репозитория git")
    if git(root, "rev-parse", "--verify", "--quiet", f"{base}^{{commit}}", ok=(0, 1, 128)).returncode:
        raise CallError(f"--base: нет коммита «{base}»")
    parts = git(root, "diff", "--name-status", "-z", "--no-renames", "--relative", base, "--").stdout.split("\0")
    files = {p: st[:1] for st, p in zip(parts[0::2], parts[1::2]) if p}
    for p in git(root, "ls-files", "-z", "--others", "--exclude-standard").stdout.split("\0"):
        if p:
            files.setdefault(p, "?")
    return dict(sorted(files.items()))


def changed_lines(root: Path, base: str, path: str, status: str) -> set[int] | None:
    """Номера новых и изменённых строк файла рабочего дерева против базы; None — файл новый, считаются все строки."""
    if status in ("A", "?"):
        return None
    diff = git(root, "diff", "--no-color", "--no-ext-diff", "--no-textconv", "--text", "--no-renames", "--relative",
               "-U0", base, "--", path).stdout
    lines: set[int] = set()
    for m in HUNK.finditer(diff):
        start, count = int(m.group(1)), int(m.group(2) or 1)
        lines.update(range(start, start + count))
    return lines


# ─────────────────────────────── маски ───────────────────────────────

def read_masks(masks: list[str], files: list[str]) -> list[str]:
    """Маски ключей и файлов масок одним списком без повторов; `./` в начале маски снимается."""
    raw = list(masks)
    for f in files:
        p = Path(f)
        if not p.is_file():
            raise CallError(f"--masks-file: нет файла {f}")
        raw += [ln for ln in p.read_text(encoding="utf-8").splitlines() if not ln.lstrip().startswith("#")]
    out = []
    for m in (x.strip() for x in raw):
        m = m[2:] if m.startswith("./") else m
        if not m:
            continue
        if m.startswith("/"):
            raise CallError(f"маска «{m}»: путь пишется от корня репозитория, без «/» в начале")
        if m not in out:
            out.append(m)
    if raw and not out:
        raise CallError("масок нет: ключи и файлы масок пусты")
    return out


def under(path: str, masks: list[str]) -> bool:
    """Путь лежит под одной из масок: glob (`*` берёт и «/»), сам файл или папка, названная маской."""
    return any(fnmatch.fnmatchcase(path, m) or path.startswith(m.rstrip("/") + "/") for m in masks)


# ─────────────────────────────── проверки ───────────────────────────────

def finding(check: str, path: str, line: int, kind: str, message: str, severity: str = "error") -> dict:
    return {"check": check, "severity": severity, "path": path, "line": line, "kind": kind, "message": message}


def row(check: str, taken: int, findings: int, note: str = "", status: str | None = None, **extra) -> dict:
    return {"check": check, "taken": taken, "findings": findings, "status": status or ("FAIL" if findings else "OK"),
            "note": note, **extra}


def check_md(root: Path, files: list[str], lines_of) -> tuple[list[dict], int]:
    """Находки refcheck (битые ссылки и следы) в новых и изменённых строках md и число находок в нетронутых строках."""
    hits, untouched = [], 0
    for f in files:
        try:
            broken, traces, _ = refcheck.check_file((root / f).resolve())
        except (UnicodeDecodeError, OSError) as e:
            hits.append(finding("ссылки", f, 0, "чтение", str(e)))
            continue
        lines = lines_of(f)
        for kind, items in (("битая ссылка", broken), ("след", traces)):
            for item in items:
                n, _, message = item.partition(": ")
                if lines is None or int(n) in lines:
                    hits.append(finding("ссылки", f, int(n), kind, message))
                else:
                    untouched += 1
    return hits, untouched


def check_yaml_paths(root: Path, files: list[str], lines_of) -> tuple[list[dict], int]:
    """Пути файлов в комментариях YAML: файла по пути нет — находка в новой или изменённой строке, счёт — в нетронутой.
    Путь — слово комментария с «/» и расширением файла; образец с `<…>`, `…` или `*` и адрес в сети путём не считаются.
    Файл ищется как путь текста вне `kb/` у `refcheck.py`, у каталога базы — ещё от папки его базы (`kb/<база>/`);
    путь вне репозитория, имя из списка не-ссылок `refcheck.py` и путь раскладки проекта в форме слоя (первый сегмент
    — папка слоя в `docs/projects/_template/`) — не находка."""
    hits, untouched = [], 0
    for f in files:
        path = (root / f).resolve()
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            hits.append(finding("ссылки", f, 0, "чтение", str(e)))
            continue
        lines = lines_of(f)
        base = refcheck.KB / path.relative_to(refcheck.KB).parts[0] if path.is_relative_to(refcheck.KB) else None
        form = path.is_relative_to(refcheck.TEMPLATE)
        for n, line in enumerate(text.split("\n"), 1):
            m = YAML_COMMENT.search(line)
            for tok in YAML_PATH.findall(m.group(1)) if m else []:
                if refcheck.resolve_path(tok, path) or base is not None and (base / tok).exists() \
                        or form and (refcheck.TEMPLATE / tok.split("/")[0]).is_dir() \
                        or refcheck.not_a_file(tok) or refcheck.outside_repo(tok, path) or refcheck.elsewhere(tok):
                    continue
                if lines is None or n in lines:
                    hits.append(finding("ссылки", f, n, "битая ссылка", f"путь {tok} в комментарии"))
                else:
                    untouched += 1
    return hits, untouched


def check_data(root: Path, files: list[str]) -> tuple[list[dict], int]:
    """Разбор JSON и YAML; схемы — против метасхемы Draft 2020-12. → (находки, число схем)."""
    hits, schemas = [], 0
    for f in files:
        try:
            text = (root / f).read_text(encoding="utf-8")
            if f.endswith(".json"):
                docs = [json.loads(text)]
            else:
                docs = list(_module("yaml").safe_load_all(text))
        except CallError:
            raise
        except Exception as e:  # noqa: BLE001 — разбор файла: любая ошибка — находка, а не падение
            mark = getattr(e, "problem_mark", None)
            line = getattr(e, "lineno", 0) or (mark.line + 1 if mark else 0)
            hits.append(finding("разбор", f, line, "разбор", " ".join(str(e).split())[:200]))
            continue
        if not f.endswith(SCHEMA_EXT):
            continue
        schemas += 1
        validator = _module("jsonschema").Draft202012Validator
        for doc in docs:
            try:
                validator.check_schema(doc)
            except Exception as e:  # noqa: BLE001 — схема вне метасхемы: находка
                where = "/".join(map(str, getattr(e, "absolute_path", ()))) or "(корень)"
                message = " ".join(str(getattr(e, "message", e)).split())[:200]
                hits.append(finding("разбор", f, 0, "метасхема", f"{where}: {message}"))
    return hits, schemas


def check_py(root: Path, files: list[str]) -> list[dict]:
    """Компиляция `.py` без запуска."""
    hits = []
    for f in files:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                compile((root / f).read_bytes(), f, "exec", dont_inherit=True)
        except SyntaxError as e:
            hits.append(finding("код", f, e.lineno or 0, "синтаксис", e.msg or str(e)))
        except (ValueError, OSError) as e:
            hits.append(finding("код", f, 0, "синтаксис", str(e)))
    return hits


def load_data(path: Path = DATA) -> dict:
    """Данные `data/accept.yaml`: {links_skip: [маска], trace_review: [{label, pattern, example}],
    trace_review_forward_only: [имя образца]}."""
    try:
        d = _module("yaml").safe_load(path.read_text(encoding="utf-8"))
        review = [{k: str(r[k]) for k in ("label", "pattern", "example")} for r in d.get("trace_review") or []]
        for r in review:
            re.compile(r["pattern"])
        return {"links_skip": [str(x) for x in d.get("links_skip") or []], "trace_review": review,
                "trace_review_forward_only": [str(x) for x in d.get("trace_review_forward_only") or []]}
    except CallError:
        raise
    except Exception as e:  # noqa: BLE001 — данные утилиты не читаются: ошибка окружения, а не находка правки
        raise CallError(f"{path}: {' '.join(str(e).split())[:200] or type(e).__name__}") from e


def trace_patterns(data: dict) -> list[tuple[str, re.Pattern, bool]]:
    """Образцы следов для строк кода: [(имя, шаблон, роняет ли приёмку)] — общие forward-only и свои «на разбор»."""
    soft = set(data["trace_review_forward_only"])
    return ([(label, rx, label not in soft) for label, rx in refcheck.FWD]
            + [(r["label"], re.compile(r["pattern"]), False) for r in data["trace_review"]])


def check_traces(root: Path, files: list[str], lines_of, patterns) -> tuple[list[dict], int]:
    """Следы в строках `.py`: в новых и изменённых — находка или запись «на разбор», в нетронутых — счёт находок."""
    hits, untouched = [], 0
    for f in files:
        try:
            text = (root / f).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            hits.append(finding("следы", f, 0, "чтение", str(e)))
            continue
        lines = lines_of(f)
        for n, line in enumerate(text.split("\n"), 1):          # счёт строк — как у git: только по «\n»
            for label, rx, fails in patterns:
                m = rx.search(line)
                if not m:
                    continue
                if lines is None or n in lines:
                    hits.append(finding("следы", f, n, label, f"«{m.group(0)}» — {line.strip()[:120]}",
                                        "error" if fails else "warning"))
                elif fails:
                    untouched += 1
    return hits, untouched


def parse_smoke(folder: str, rc: int, out: str, err: str) -> dict:
    """Итог одного прогона смоука: счёт статусов, строки FAIL и причина, если прогон не состоялся."""
    lines = out.splitlines()
    total = next((x for x in reversed(lines) if x.startswith("итого:")), "")
    counts = dict.fromkeys(SMOKE_STATUSES, 0)
    counts.update({k: int(v) for k, v in SMOKE_COUNT.findall(total.split(";")[0])})
    problem = ""
    if not total:
        problem = (err.strip().splitlines() or out.strip().splitlines() or [f"код {rc}"])[-1][:240]
    elif not sum(counts.values()):
        problem = "ни одной строки смоука по этой подстроке пути"
    return {"folder": folder, "rc": rc, **counts, "fails": [x.rstrip() for x in lines if x.startswith("FAIL ")],
            "problem": problem}


def run_smoke(folder: str) -> dict:
    if not SMOKE.is_file():
        raise CallError(f"нет смоука {SMOKE}")
    print(f"смоук {folder} …", file=sys.stderr, flush=True)
    r = subprocess.run([sys.executable, str(SMOKE), "--only", folder], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return parse_smoke(folder, r.returncode, r.stdout, r.stderr)


# ─────────────────────────────── приёмка ───────────────────────────────

def accept(root: Path = ROOT, base: str = "HEAD", masks: list[str] | None = None, smoke: list[str] | None = None,
           trace: bool = True) -> dict:
    """Все проверки правки → отчёт: {base, repo, masks, changed, own, foreign, checks, findings, smoke, clean}."""
    masks, smoke = list(masks or []), list(smoke or [])
    cfg = load_data()
    files = changed(root, base)
    own = {p: st for p, st in files.items() if not masks or under(p, masks)}
    foreign = {p: st for p, st in files.items() if p not in own}
    live = [p for p in own if (root / p).is_file()]
    cache: dict[str, set[int] | None] = {}

    def lines_of(p: str):
        if p not in cache:
            cache[p] = changed_lines(root, base, p, own[p])
        return cache[p]

    rows, findings = [], []
    unused = [m for m in masks if not any(under(p, [m]) for p in files)]
    deleted = sum(st == "D" for st in own.values())
    note = "; ".join(x for x in (f"удалено под масками — {deleted}" if deleted else "",
                                 f"маски без изменённых файлов — {len(unused)}" if unused else "") if x)
    if masks:
        rows.append(row("маски", len(files), len(foreign), note))
    else:
        rows.append(row("маски", len(files), 0, "масок нет — пути не сверяются, проверяются все изменённые файлы",
                        SKIP))

    md = [p for p in live if p.endswith(".md")]
    skipped = [p for p in md if under(p, cfg["links_skip"])]
    md = [p for p in md if p not in skipped]
    hits, untouched = check_md(root, md, lines_of)
    yml = [p for p in live if p.endswith((".yaml", ".yml")) and not under(p, cfg["links_skip"])]
    more, quiet = check_yaml_paths(root, yml, lines_of)
    hits, untouched = hits + more, untouched + quiet
    findings += hits
    note = "; ".join(x for x in (f"в нетронутых строках — {untouched}" if untouched else "",
                                 f"не сверялись (маски links_skip данных) — {len(skipped)}" if skipped else "") if x)
    rows.append(row("ссылки", len(md) + len(yml), len(hits), note, untouched=untouched, skipped=len(skipped)))

    data = [p for p in live if p.endswith(DATA_EXT)]
    hits, schemas = check_data(root, data)
    findings += hits
    rows.append(row("разбор", len(data), len(hits), f"схем — {schemas}" if schemas else "", schemas=schemas))

    py = [p for p in live if p.endswith(".py")]
    hits = check_py(root, py)
    findings += hits
    rows.append(row("код", len(py), len(hits)))

    if trace:
        hits, untouched = check_traces(root, py, lines_of, trace_patterns(cfg))
        findings += hits
        errors = sum(h["severity"] == "error" for h in hits)
        review = len(hits) - errors
        note = "; ".join(x for x in (f"в нетронутых строках — {untouched}" if untouched else "",
                                     f"на разбор — {review}" if review else "") if x)
        rows.append(row("следы", len(py), errors, note, untouched=untouched, review=review))
    else:
        rows.append(row("следы", len(py), 0, "не искались: --no-trace", SKIP))

    runs = [run_smoke(f) for f in smoke]
    if runs:
        counts = {s: sum(r[s] for r in runs) for s in SMOKE_STATUSES}
        bad = counts["FAIL"] + sum(bool(r["problem"]) for r in runs)
        rows.append(row("смоук", sum(counts.values()), bad, ", ".join(f"{s} {counts[s]}" for s in SMOKE_STATUSES)))
    else:
        rows.append(row("смоук", 0, 0, "не запускался: --smoke ПАПКА", SKIP))

    return {"base": base, "repo": str(root), "masks": masks, "masks_unused": unused, "changed": len(files),
            "own": [{"path": p, "status": st} for p, st in own.items()],
            "foreign": [{"path": p, "status": st} for p, st in foreign.items()],
            "checks": rows, "findings": findings, "smoke": runs,
            "clean": all(r["status"] != "FAIL" for r in rows)}


def exit_code(rep: dict) -> int:
    return 0 if rep["clean"] else 1


def render(rep: dict) -> str:
    """Таблица проверок и списки: пути вне масок, находки по проверкам, записи «на разбор», строки FAIL смоука."""
    head = f"== приёмка правки: база {rep['base']}; изменено файлов {rep['changed']}"
    if rep["masks"]:
        head += f", под масками {len(rep['own'])}, вне масок {len(rep['foreign'])}"
    out = [head, f"{'итог':<6}{'проверка':<10}{'взято':>6}{'находок':>9}  заметка"]
    for r in rep["checks"]:
        out.append(f"{r['status']:<6}{r['check']:<10}{r['taken']:>6}{r['findings']:>9}  {r['note']}".rstrip())

    def line(f: dict) -> str:
        return f"  {f['path']}{':' + str(f['line']) if f['line'] else ''}: {f['kind']}: {f['message']}"

    if rep["foreign"]:
        out.append(f"== вне масок ({len(rep['foreign'])})")
        out += [f"  {STATUS_WORD.get(x['status'], 'изменён'):<8}{x['path']}" for x in rep["foreign"]]
    if rep["masks_unused"]:
        out.append(f"== маски без изменённых файлов ({len(rep['masks_unused'])})")
        out += [f"  {m}" for m in rep["masks_unused"]]
    for r in rep["checks"]:
        hits = [f for f in rep["findings"] if f["check"] == r["check"] and f["severity"] == "error"]
        if hits:
            out.append(f"== {r['check']}: находки ({len(hits)})")
            out += [line(f) for f in hits]
    review = [f for f in rep["findings"] if f["severity"] != "error"]
    if review:
        out.append(f"== на разбор, без отказа ({len(review)})")
        out += [line(f) for f in review]
    for s in rep["smoke"]:
        if s["fails"] or s["problem"]:
            out.append(f"== смоук {s['folder']}: {s['problem'] or 'FAIL ' + str(s['FAIL'])}")
            out += [f"  {x}" for x in s["fails"]]
    failed = [r["check"] for r in rep["checks"] if r["status"] == "FAIL"]
    out.append("ИТОГ: " + ("чисто" if rep["clean"] else "есть находки — " + ", ".join(failed)))
    return "\n".join(out)


# ─────────────────────────────── самопроверка ───────────────────────────────

def selftest() -> int:
    """Временный репозиторий git во временной папке: чистая правка проходит, каждый посеянный случай ловит своя
    проверка — путь вне масок, битые YAML и JSON, схема вне метасхемы, битая ссылка в новой строке md (в старой —
    счётом), синтаксическая ошибка py, след в новой строке py."""
    ok = fail = 0

    def ok_if(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    def quiet(argv, root):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = main(argv, root)
        return rc, out.getvalue(), err.getvalue()

    cfg = load_data()
    review, soft = cfg["trace_review"], cfg["trace_review_forward_only"]
    fwd = refcheck.trace_rows("forward-only")
    ok_if("данные: пример каждого образца «на разбор» находится своим шаблоном",
          bool(review) and all(re.compile(r["pattern"]).search(r["example"]) for r in review))
    ok_if("данные: имена образцов forward-only «на разбор» есть в общих данных, образцы-находки остались",
          set(soft) <= {r["label"] for r in fwd} and any(r["label"] not in soft for r in fwd))
    ok_if("маска: glob берёт вложенное, папка и файл — целиком, соседняя папка — нет",
          under("a/b/c.py", ["a/*"]) and under("a/b/c.py", ["a/"]) and under("a/b/c.py", ["a"])
          and under("a/b.py", ["a/?.py"]) and under("a/b.py", ["a/b.py"]) and not under("ab/c.py", ["a"])
          and not under("a/b.py", ["a/*.md"]) and not under("a/b.py", []))
    sm = parse_smoke("x", 1, "PASS      0.1s  a.py  help\nFAIL      0.2s  b.py  run: --selftest  код 1\n\n"
                              "итого: PASS 1, FAIL 1, XFAIL 2, XPASS 0; python /x\n", "")
    ok_if("смоук: счёт статусов и строки FAIL из вывода",
          (sm["PASS"], sm["FAIL"], sm["XFAIL"], sm["XPASS"]) == (1, 1, 2, 0) and len(sm["fails"]) == 1
          and not sm["problem"])
    empty = parse_smoke("x", 0, "\nитого: PASS 0, FAIL 0, XFAIL 0, XPASS 0; python /x\n", "")
    ok_if("смоук: папка без строк и несостоявшийся прогон — причина", "ни одной строки" in empty["problem"]
          and parse_smoke("x", 2, "", "smoke: ошибки списков (1)\n")["problem"].startswith("smoke: ошибки списков"))

    sample = next(r["example"] for r in fwd if r["label"] not in soft)   # след-находка — из общих данных
    mild = [r["example"] for r in fwd if r["label"] in soft][:1] + [review[0]["example"]]   # образцы «на разбор»
    doc = "# Док\nСтарая строка: [нет](gone-old.md).\n"
    tool = f"VALUE = 1\nOLD = '{sample}'\n"
    schema = '{"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object"}\n'
    git_env = dict(GIT_ENV)
    GIT_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", GIT_AUTHOR_NAME="selftest",
                   GIT_AUTHOR_EMAIL="selftest@example.invalid", GIT_COMMITTER_NAME="selftest",
                   GIT_COMMITTER_EMAIL="selftest@example.invalid")
    try:
        with tempfile.TemporaryDirectory(prefix="accept-") as td:
            repo = Path(td).resolve() / "repo"
            repo.mkdir()
            GIT_ENV["GIT_CEILING_DIRECTORIES"] = str(repo.parent.parent)   # выше временной папки git не ищет

            def put(rel, text):
                p = repo / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text, encoding="utf-8")

            @contextlib.contextmanager
            def seeded(rel, text):
                """Посев на время проверки: на выходе файл получает содержимое до посева (или файла снова нет)."""
                p = repo / rel
                before = p.read_text(encoding="utf-8") if p.exists() else None
                put(rel, text)
                try:
                    yield
                finally:
                    if before is None:
                        p.unlink()
                    else:
                        p.write_text(before, encoding="utf-8")

            def failed(rep):
                return [r["check"] for r in rep["checks"] if r["status"] == "FAIL"]

            def check_of(rep, name):
                return next(r for r in rep["checks"] if r["check"] == name)

            odd = "zone/имя с пробелом [1].md"                           # путь, который git печатал бы в кавычках
            for rel, text in (("zone/doc.md", doc + "Хвост.\n"), ("zone/other.md", "# Другой\n"),
                              ("zone/tool.py", tool), ("zone/data.yaml", "a: 1\n"), ("zone/drop.txt", "лишний\n"),
                              (odd, doc), ("side/note.txt", "заметка\n")):
                put(rel, text)
            git(repo, "init", "-q")
            git(repo, "add", "-A")
            git(repo, "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + os.devnull, "commit", "-q", "-m", "base")
            rep = accept(repo, masks=["zone/*"])
            ok_if("без правок: изменённых файлов нет, чисто", rep["changed"] == 0 and rep["clean"])

            # чистая правка зоны: новая строка md с живой ссылкой, правка py и yaml, новые json и схемы, удаление
            put("zone/doc.md", doc + "Новая строка: [есть](other.md).\nХвост.\n")
            put("zone/tool.py", tool.replace("VALUE = 1", "VALUE = 2"))
            put("zone/data.yaml", "a: 2\nb: [1, 2]\n---\nc: 3\n")
            put("zone/new.json", '{"k": 1}\n')
            put("zone/t.schema.json", schema)
            put("zone/t.schema.yaml", "type: object\nproperties:\n  a: {type: string}\n")
            (repo / "zone/drop.txt").unlink()
            masks = ["zone/*"]
            rep = accept(repo, masks=masks)
            ok_if("чистая правка: под масками 7 файлов, вне масок 0, код 0",
                  rep["clean"] and exit_code(rep) == 0 and len(rep["own"]) == 7 and not rep["foreign"]
                  and not rep["findings"])
            ok_if("строки диффа: изменённая — её номер, новый файл — все строки",
                  changed_lines(repo, "HEAD", "zone/doc.md", "M") == {3}
                  and changed_lines(repo, "HEAD", "zone/new.json", "?") is None)
            ok_if("md: находка в нетронутой строке — счётом, без отказа",
                  check_of(rep, "ссылки")["findings"] == 0 and check_of(rep, "ссылки")["untouched"] == 1)
            ok_if("py: след в нетронутой строке — счётом, без отказа",
                  check_of(rep, "следы")["findings"] == 0 and check_of(rep, "следы")["untouched"] == 1)
            ok_if("схемы JSON и YAML проходят метасхему; удалённый файл — под масками, без проверок содержимого",
                  check_of(rep, "разбор")["schemas"] == 2 and {"path": "zone/drop.txt", "status": "D"} in rep["own"])
            ok_if("без масок: пути не сверяются, проверяются все файлы",
                  accept(repo)["clean"] and check_of(accept(repo), "маски")["status"] == SKIP)

            with seeded("side/note.txt", "заметка, правка\n"), seeded("side/new.txt", "новый\n"):
                rep = accept(repo, masks=masks)
                ok_if("путь вне масок (правленый и новый) — списком, код 1",
                      [x["path"] for x in rep["foreign"]] == ["side/new.txt", "side/note.txt"]
                      and failed(rep) == ["маски"] and exit_code(rep) == 1)
                ok_if("тот же путь под второй маской — чисто", accept(repo, masks=masks + ["side"])["clean"])
            with seeded("zone/bad.yaml", "a: [1, 2\nb: {\n"):
                rep = accept(repo, masks=masks)
                ok_if("битый YAML — разбор, код 1", failed(rep) == ["разбор"] and exit_code(rep) == 1
                      and [(f["path"], f["kind"]) for f in rep["findings"]] == [("zone/bad.yaml", "разбор")])
            with seeded("zone/new.json", '{"k": 1,}\n'):
                rep = accept(repo, masks=masks)
                ok_if("битый JSON — разбор со строкой", failed(rep) == ["разбор"]
                      and [(f["path"], f["line"]) for f in rep["findings"]] == [("zone/new.json", 1)])
            with seeded("zone/t.schema.json", '{"type": 5}\n'), seeded("zone/t.schema.yaml", "required: да\n"):
                rep = accept(repo, masks=masks)
                ok_if("схемы JSON и YAML вне метасхемы — находки", failed(rep) == ["разбор"]
                      and sorted((f["path"], f["kind"]) for f in rep["findings"])
                      == [("zone/t.schema.json", "метасхема"), ("zone/t.schema.yaml", "метасхема")])
            with seeded("zone/doc.md", doc + "Новая строка: [нет](gone-new.md).\nХвост.\n"):
                rep = accept(repo, masks=masks)
                hits = [f for f in rep["findings"] if f["check"] == "ссылки"]
                ok_if("md: битая ссылка в новой строке — находка, в старой — счётом",
                      failed(rep) == ["ссылки"] and len(hits) == 1 and hits[0]["line"] == 3
                      and "gone-new.md" in hits[0]["message"] and check_of(rep, "ссылки")["untouched"] == 1)
            with seeded(odd, doc + "Новая строка: [нет](gone-new.md).\n"):
                rep = accept(repo, masks=masks)
                hits = [(f["path"], f["line"]) for f in rep["findings"]]
                ok_if("md: путь с пробелом, кириллицей и знаками glob — строки диффа те же",
                      hits == [(odd, 3)] and check_of(rep, "ссылки")["untouched"] == 2)
            with seeded("zone/fresh.md", f"# Новый\n\n[нет](gone.md) и {sample}\n"):
                rep = accept(repo, masks=masks)
                kinds = sorted(f["kind"] for f in rep["findings"] if f["path"] == "zone/fresh.md")
                ok_if("md: в новом файле считаются все строки — битая ссылка и след",
                      failed(rep) == ["ссылки"] and kinds == ["битая ссылка", "след"])
            skip_md = re.sub(r"[*?]", "demo", cfg["links_skip"][0]).strip("/") + "/note.md"   # путь под маской данных
            with seeded(skip_md, f"# Фикстура\n\n[нет](gone.md) и {sample}\n"):
                rep = accept(repo, masks=masks + [skip_md])
                ok_if("md под маской исключения из данных не сверяется",
                      under(skip_md, cfg["links_skip"]) and rep["clean"] and check_of(rep, "ссылки")["skipped"] == 1)
            with seeded("zone/data.yaml", "# схема: ./t.schema.json; рядом: zone-docs/gone.schema.json\na: 2\n"
                        "b: [1, 2]  # форма — sub/<имя>/form.yaml и https://example.org/x/form.yaml\n"):
                rep = accept(repo, masks=masks)
                hits = [(f["path"], f["line"], f["kind"]) for f in rep["findings"]]
                ok_if("yaml: путь в комментарии новой строки, по которому файла нет, — находка; живой путь, образец с "
                      "<…> и адрес в сети — нет",
                      failed(rep) == ["ссылки"] and hits == [("zone/data.yaml", 1, "битая ссылка")]
                      and "zone-docs/gone.schema.json" in rep["findings"][0]["message"])
            with seeded("zone/broken.py", "def f(:\n    pass\n"):
                rep = accept(repo, masks=masks)
                ok_if("py с синтаксической ошибкой — код, строка ошибки", failed(rep) == ["код"]
                      and [(f["path"], f["line"]) for f in rep["findings"]] == [("zone/broken.py", 1)])
            with seeded("zone/tool.py", tool.replace("VALUE = 1", "VALUE = 2") + f"NEW = '{sample}'\n"):
                rep = accept(repo, masks=masks)
                ok_if("py: след в новой строке — находка, код 1", failed(rep) == ["следы"]
                      and [(f["line"], f["severity"]) for f in rep["findings"]] == [(3, "error")])
                rep = accept(repo, masks=masks, trace=False)
                ok_if("--no-trace: следы не ищутся", rep["clean"] and check_of(rep, "следы")["status"] == SKIP)
            with seeded("zone/tool.py", tool.replace("VALUE = 1", "VALUE = 2")
                        + "".join(f"NOTE_{i} = '{x}'\n" for i, x in enumerate(mild))):
                rep = accept(repo, masks=masks)
                ok_if("py: образцы «на разбор» в новых строках (свой и общий) — в списке, без отказа",
                      rep["clean"] and check_of(rep, "следы")["review"] == len(mild)
                      and [f["severity"] for f in rep["findings"]] == ["warning"] * len(mild)
                      and "на разбор" in render(rep))

            mfile = Path(td) / "masks.txt"
            mfile.write_text("# зона\n\n./zone/*\nzone/*\n", encoding="utf-8")
            ok_if("файл масок: маска на строку, комментарии и повторы сняты",
                  read_masks(["side/"], [str(mfile)]) == ["side/", "zone/*"])
            rc, out, _ = quiet(["--masks-file", str(mfile), "--json"], repo)
            ok_if("вызов: чистая правка — код 0, --json — один документ JSON",
                  rc == 0 and json.loads(out)["clean"] is True and json.loads(out)["masks"] == ["zone/*"])
            with seeded("side/note.txt", "заметка, правка\n"):
                rc, out, _ = quiet(["--mask", "zone/*"], repo)
                ok_if("вызов: путь вне масок — код 1, таблица со списком и итогом", rc == 1
                      and "== вне масок (1)" in out and "side/note.txt" in out and "ИТОГ: есть находки — маски" in out)
            codes = [quiet(argv, repo)[0] for argv in (["--base", "нет-такого-коммита"],
                                                       ["--masks-file", str(mfile) + ".нет"], ["--mask", "/zone/*"])]
            ok_if("вызов: нет коммита, нет файла масок, маска от «/» — код 2", codes == [2, 2, 2])
            rc, _, err = quiet(["--mask", "zone/*"], repo.parent)
            ok_if("вызов: папка вне репозитория git — код 2", rc == 2 and "репозитория git" in err)
    finally:
        GIT_ENV.clear()
        GIT_ENV.update(git_env)
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


# ─────────────────────────────── запуск ───────────────────────────────

def main(argv=None, root: Path = ROOT) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], epilog=__doc__.split("\n", 2)[2],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", default="HEAD", metavar="REF", help="базовый коммит: правка — рабочее дерево против него "
                                                                   "плюс неотслеживаемые файлы (по умолчанию HEAD)")
    ap.add_argument("--mask", action="append", default=[], metavar="GLOB",
                    help="маска файлов зоны от корня репозитория (ключ — повтором)")
    ap.add_argument("--masks-file", action="append", default=[], metavar="ФАЙЛ",
                    help="файл масок: маска на строку (ключ — повтором)")
    ap.add_argument("--smoke", action="append", default=[], metavar="ПАПКА[,ПАПКА…]",
                    help="смоук по подстроке пути: scripts/tests/smoke.py --only ПАПКА по каждой папке")
    ap.add_argument("--no-trace", action="store_true", help="не искать следы в строках .py")
    ap.add_argument("--json", action="store_true", help="отчёт одним документом JSON вместо таблицы")
    ap.add_argument("--selftest", action="store_true", help="самопроверка во временном репозитории git, без сети")
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest()
        masks = read_masks(a.mask, a.masks_file)
        smoke = [x.strip() for part in a.smoke for x in part.split(",") if x.strip()]
        rep = accept(root, a.base, masks, smoke, trace=not a.no_trace)
    except CallError as e:
        print(f"accept: {e}", file=sys.stderr)
        return 2
    print(json.dumps(rep, ensure_ascii=False, indent=1) if a.json else render(rep))
    return exit_code(rep)


if __name__ == "__main__":
    _reexec_venv()
    sys.exit(main())
