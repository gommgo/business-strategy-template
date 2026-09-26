#!/usr/bin/env python3
"""Смоук утилит скилла: каждая взятая утилита импортируется и отвечает на --help (или самопроверку). Без сети и браузера.

Список — `smoke-list.tsv` рядом (path от корня скилла, kind, smoke, xfail). Виды проверки в колонке smoke (через «;»):
  help [rc=N]        python FILE --help → код N (по умолчанию 0)
  run: ARGS [rc=N]   python FILE ARGS → код N — самопроверка утилиты ({skill} в ARGS — корень скилла)
  import-only        импорт модуля без запуска main (для утилит без --help)
  compile            только синтаксис: .py — compile(), .sh — bash -n, .mjs/.js — node --check (нет node — пропуск)
  data               файл есть и читается (.json, .yaml — разбор)
Колонка xfail — известная причина, по которой проверка без окружения падает (снимок каталога, бинарник, входы опытов):
«run: причина» относится к проверкам run, «help: …» — к help, без префикса — ко всем проверкам строки. Упавшая такая
проверка — XFAIL, прошедшая — XPASS (окружение уже есть). Код выхода 1 — если есть FAIL.

  python3 scripts/tests/smoke.py                 # все строки, таблица в stdout
  python3 scripts/tests/smoke.py --only ai-media # строки, путь которых содержит подстроку
  python3 scripts/tests/smoke.py --tsv out.tsv --timeout 120

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

LIST = HERE / "smoke-list.tsv"
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
    ap = argparse.ArgumentParser(description="Смоук утилит скилла design-deep-dive")
    ap.add_argument("--list", default=str(LIST))
    ap.add_argument("--only", default="", help="подстрока пути")
    ap.add_argument("--timeout", type=float, default=90.0)
    ap.add_argument("--tsv", default="", help="записать результаты в TSV")
    a = ap.parse_args()

    py = kbpaths.python()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
    rows = list(csv.DictReader(open(a.list, encoding="utf-8"), delimiter="\t"))
    results, counts = [], {"PASS": 0, "FAIL": 0, "XFAIL": 0, "XPASS": 0}
    for row in rows:
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
                            "rc": "" if got is None else got, "seconds": f"{dt:.1f}", "note": note})
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
