#!/usr/bin/env python3
"""Смоук утилит скилла: каждая взятая утилита импортируется и отвечает на --help (или самопроверку). Без сети и браузера.

Списки — все `*.tsv` папки `smoke/` рядом, по имени: у каждой папки `scripts/<папка>/` свой список `<папка>.tsv`, у
утилит `scripts/project/` — по зоне (`project-screens`, `project-ds`, `project-demo`, `project-canvas`,
`project-package`), у файлов корня `scripts/` — `scripts.tsv`, у эталонного кода `kb/` — `kb.tsv`. Колонки: path (от
корня скилла), kind, smoke, xfail. Пара «путь + вид проверки» встречается во всех списках один раз: дубль — ошибка
списков (код выхода 2). Виды проверки в колонке smoke (через «;»):
  help [rc=N]        python FILE --help → код N (по умолчанию 0)
  run: ARGS [rc=N]   python FILE ARGS → код N — самопроверка утилиты ({skill} в ARGS — корень скилла)
  import-only        импорт модуля без запуска main (для утилит без --help)
  compile            только синтаксис: .py — compile(), .sh — bash -n, .mjs/.js — node --check (нет node — пропуск)
  data               файл есть и читается (.json, .yaml — разбор)
Колонка xfail — известная причина, по которой проверка без окружения падает (снимок каталога, бинарник, входы опытов):
«run: причина» относится к проверкам run, «help: …» — к help, без префикса — ко всем проверкам строки. Упавшая такая
проверка — XFAIL, прошедшая — XPASS (окружение уже есть). Код выхода 1 — если есть FAIL.

  python3 scripts/tests/smoke.py                   # все списки, таблица в stdout
  python3 scripts/tests/smoke.py --only ai-media   # строки, путь которых содержит подстроку
  python3 scripts/tests/smoke.py --list scripts/tests/smoke/site.tsv   # только эти списки (файл или папка; ключ — повтором)
  python3 scripts/tests/smoke.py --tsv out.tsv --timeout 120
  python3 scripts/tests/smoke.py --validate        # списки: колонки, виды проверок, дубли, пути; без запуска
  python3 scripts/tests/smoke.py --uncovered       # утилиты scripts/ (.py, .sh, .mjs, .js) без строки смоука

Утилиты запускаются Python окружения скилла (kbpaths.python(): $DDD_HOME/venv), рабочая папка — временная.
"""
import argparse
import csv
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
import kbpaths  # noqa: E402

LISTS = HERE / "smoke"
COLUMNS = ("path", "kind", "smoke", "xfail")
CODE = (".py", ".sh", ".mjs", ".js", ".cjs")             # что считается утилитой для --uncovered
IMPORT_ONLY = ("import importlib.util, sys; f = sys.argv[1]; sys.argv = [f]; sys.path.insert(0, __import__('os').path.dirname(f)); "
               "s = importlib.util.spec_from_file_location('smoke_module', f); m = importlib.util.module_from_spec(s); "
               "s.loader.exec_module(m)")
COMPILE_PY = "import sys; f = sys.argv[1]; compile(open(f, encoding='utf-8').read(), f, 'exec')"


def parse_checks(spec):
    out = []
    for part in [p.strip() for p in (spec or "").split(";") if p.strip() and p.strip() != "-"]:
        rc = 0
        m = re.search(r"\s+rc=(\d+)\s*$", part)
        if m:
            rc, part = int(m.group(1)), part[:m.start()].rstrip()
        if part.startswith("run:"):
            out.append(("run", [a.replace("{skill}", str(kbpaths.skill())) for a in shlex.split(part[4:])], rc))
        elif part in ("help", "import-only", "compile", "data"):
            out.append((part, [], rc))
        else:
            raise ValueError(f"неизвестная проверка: {part!r}")
    return out


def xfail_for(spec, kind):
    """Причина ожидаемого падения для вида проверки: «run: …», «help: …» или без префикса — для всех."""
    spec = (spec or "").strip()
    if not spec:
        return ""
    m = re.match(r"^(help|run|import-only|compile|data):\s*(.*)$", spec)
    if m:
        return m.group(2) if m.group(1) == kind else ""
    return spec


def list_files(paths):
    """Списки смоука: файлы .tsv по порядку; папка — все её *.tsv по имени."""
    out = []
    for p in map(Path, paths):
        out += sorted(p.glob("*.tsv")) if p.is_dir() else [p]
    return out


def load_rows(files):
    """Строки всех списков → [(имя списка, номер строки, строка)] и ошибки формы списков (колонки)."""
    rows, errors = [], []
    for f in files:
        if not f.is_file():
            errors.append(f"{f}: нет списка")
            continue
        with open(f, encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh, delimiter="\t")
            if tuple(reader.fieldnames or ()) != COLUMNS:
                errors.append(f"{f.name}: колонки {reader.fieldnames} — ждали {', '.join(COLUMNS)}")
                continue
            for n, row in enumerate(reader, 2):
                rows.append((f.stem, n, row))
    return rows, errors


def list_problems(rows, paths=True):
    """Ошибки строк: пустой путь, неизвестный вид проверки, дубль «путь + вид проверки» во всех списках;
    paths — ещё и файл строки на месте."""
    errs, seen = [], {}
    for name, n, row in rows:
        where = f"{name}.tsv:{n}"
        p = (row.get("path") or "").strip()
        if not p:
            errs.append(f"{where}: пустой path")
            continue
        try:
            kinds = {k for k, _, _ in parse_checks(row.get("smoke"))}
        except ValueError as e:
            errs.append(f"{where}: {e}")
            continue
        for k in sorted(kinds):
            if (p, k) in seen:
                errs.append(f"{where}: дубль {p} [{k}] — уже в {seen[(p, k)]}")
            else:
                seen[(p, k)] = where
        if paths and not kbpaths.skill(p).exists():
            errs.append(f"{where}: нет файла {p}")
    return errs


def uncovered(rows):
    """Файлы кода в scripts/ (CODE) без строки смоука — пути от корня скилла."""
    have = {(row.get("path") or "").strip() for _, _, row in rows}
    root = kbpaths.skill()
    out = []
    for f in sorted(kbpaths.scripts().rglob("*")):
        if not f.is_file() or f.suffix not in CODE:
            continue
        parts = f.relative_to(kbpaths.scripts()).parts
        if "__pycache__" in parts or "node_modules" in parts or parts[:2] == ("tests", "fixtures"):
            continue
        rel = f.relative_to(root).as_posix()
        if rel not in have:
            out.append(rel)
    return out


def run_check(path, kind, args, rc_expect, py, timeout, env):
    """→ (ok, rc, секунды, заметка)."""
    t0 = time.monotonic()
    suffix = path.suffix.lower()
    if kind == "data":
        if not path.is_file() or path.stat().st_size == 0:
            return False, None, 0.0, "нет файла или пустой"
        try:
            if suffix == ".json":
                json.loads(path.read_text(encoding="utf-8"))
            elif suffix in (".yaml", ".yml"):
                import yaml
                yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            return False, None, time.monotonic() - t0, f"не разбирается: {e}"[:200]
        return True, None, time.monotonic() - t0, ""
    if kind == "compile":
        if suffix == ".py":
            cmd = [py, "-c", COMPILE_PY, str(path)]
        elif suffix == ".sh":
            cmd = ["bash", "-n", str(path)]
        elif suffix in (".mjs", ".js", ".cjs"):
            node = kbpaths.node()
            if os.sep not in node and not shutil.which(node):
                return True, None, 0.0, "пропуск: нет node"
            cmd = [node, "--check", str(path)]
        else:
            return path.is_file(), None, 0.0, ""
    elif kind == "import-only":
        cmd = [py, "-c", IMPORT_ONLY, str(path)]
    elif kind == "help":
        cmd = [py, str(path), "--help"]
    else:
        cmd = [(py if suffix == ".py" else "bash"), str(path), *args]
    with tempfile.TemporaryDirectory(prefix="ddd-smoke-") as cwd:
        try:
            r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, None, time.monotonic() - t0, f"таймаут {timeout} с"
    dt = time.monotonic() - t0
    ok = r.returncode == rc_expect
    if kind == "help":
        ok = ok and bool((r.stdout + r.stderr).strip())
    note = ""
    if not ok:
        tail = [ln for ln in (r.stderr or r.stdout).strip().splitlines() if ln.strip()]
        note = (tail[-1] if tail else f"код {r.returncode}")[:240]
    return ok, r.returncode, dt, note


def main():
    ap = argparse.ArgumentParser(description="Смоук утилит скилла design-deep-dive: все списки папки smoke/")
    ap.add_argument("--list", action="append", default=[], metavar="PATH",
                    help="список .tsv или папка списков (ключ — повтором); по умолчанию — все списки папки smoke/")
    ap.add_argument("--only", default="", help="подстрока пути")
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--tsv", default="", help="записать результаты в TSV")
    ap.add_argument("--validate", action="store_true",
                    help="проверить списки (колонки, виды проверок, дубли, файлы строк) без запуска; код 1 — есть ошибки")
    ap.add_argument("--uncovered", action="store_true",
                    help="перечислить утилиты scripts/ без строки смоука (справка; код выхода 0)")
    a = ap.parse_args()

    files = list_files(a.list or [LISTS])
    rows, errors = load_rows(files)
    if a.validate:
        errors += list_problems(rows)
        for e in errors:
            print(e)
        print(f"списков {len(files)}, строк {len(rows)}; ошибок {len(errors)}")
        return 1 if errors else 0
    if a.uncovered:
        rest = uncovered(load_rows(list_files([LISTS]))[0])
        for p in rest:
            print(p)
        print(f"без строки смоука: {len(rest)}")
        return 0
    errors += list_problems(rows, paths=False)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        print(f"smoke: ошибки списков ({len(errors)}) — поправьте строки выше; смоук не запускался", file=sys.stderr)
        return 2

    py = kbpaths.python()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    results, counts = [], {"PASS": 0, "FAIL": 0, "XFAIL": 0, "XPASS": 0}
    for list_name, _, row in rows:
        if a.only and a.only not in row["path"]:
            continue
        path = kbpaths.skill(row["path"])
        for kind, args, rc in parse_checks(row["smoke"]):
            ok, got, dt, note = run_check(path, kind, args, rc, py, a.timeout, env)
            xf = xfail_for(row.get("xfail", ""), kind)
            if xf:
                status = "XPASS" if ok else "XFAIL"
                note = note if ok else f"{note} · ожидаемо: {xf}"
            else:
                status = "PASS" if ok else "FAIL"
            counts[status] += 1
            shown = [a.replace(str(kbpaths.skill()), "{skill}") for a in args]
            label = kind + ((" " + " ".join(shown)) if shown else "") + (f" rc={rc}" if rc else "")
            results.append({"path": row["path"], "kind": row["kind"], "check": label, "status": status,
                            "rc": "" if got is None else got, "seconds": f"{dt:.1f}", "note": note, "list": list_name})
            print(f"{status:<6} {dt:6.1f}s  {row['path']:<58} {label:<22} {note}", flush=True)
    print(f"\nитого: PASS {counts['PASS']}, FAIL {counts['FAIL']}, XFAIL {counts['XFAIL']}, XPASS {counts['XPASS']}; "
          f"python {py}")
    if a.tsv:
        with open(a.tsv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(results[0]) if results else ["path"], delimiter="\t", lineterminator="\n")
            w.writeheader()
            for r in results:
                w.writerow({k: str(v).replace("\t", " ").replace("\n", " ") for k, v in r.items()})
    return 1 if counts["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
