#!/usr/bin/env python3
"""sync_check — проверка синхронности скилла одним вызовом: производные против генераторов, копии против канона,
описания скиллов в пределах.

Что сверяется (список — `scripts/maint/data/sync.yaml`; новый генератор или копия — строка данных, а не код):
  • generators — генераторы производных файлов с `--check` (словарь и матрица состояний, мастер-чек-лист ux, профиль
    и чек-лист site, таблица соответствия словарей, словарь ux для линтера текстов, why пар «до и после», уровни
    эффектов подачи, карты x-canvas-map) и сборки на фикстурах (`scripts/tests/fixtures/`, собираются во временную
    папку): производные ДС, генерируемые разделы `map.md`, манифест готовности, вход холста всех этапов, фикстуры
    с собранными файлами (`fixture_gen.py build --all --check`). Проверка ничего не пишет в скилл: генераторы идут с
    `--check`, сборки — во временных папках;
  • copies — управляемые копии текста: блок кода копии совпадает с блоком канона байт в байт (грамматика нотации
    дерева `screen-deep-dive/references/tree-notation.md` против `_template/screens/README.md § Нотация дерева`); при
    расхождении прав канон — правится копия;
  • descriptions — описание (`description` передней части) каждого `.claude/skills/*/SKILL.md` не длиннее 600 знаков,
    сумма — не больше 18 000, скилл не скрыт от модели (`disable-model-invocation`).

    python3 .claude/skills/design-deep-dive/scripts/maint/sync_check.py [all | generators | copies | descriptions]
                                                                         [--only ID[,ID…]] [--list] [--json]
    python3 .claude/skills/design-deep-dive/scripts/maint/sync_check.py --selftest

Без команды — all. Строка генератора: OK · FAIL (последние строки вывода утилиты и производный файл) · XFAIL (известная
причина из данных) · XPASS (причины уже нет — снять `xfail`). Утилиты запускаются Python окружения
(`kbpaths.python()`); нужен PyYAML. Код выхода: 0 — FAIL нет; 1 — есть FAIL, расхождение копии или описание вне
пределов; 2 — ошибка вызова или данных (нет утилиты, фикстуры, файла копии).
"""
from __future__ import annotations

import argparse
import contextlib
import difflib
import io
import json
import re
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

kbpaths.use("tests")
import fixture_project  # noqa: E402

DATA = kbpaths.data("maint", "sync.yaml")
ROOT = kbpaths.repo()
TIMEOUT = 600
TAIL_LINES = 6


class DataError(ValueError):
    """Ошибка данных или вызова (код выхода 2)."""


# ─────────────────────────────── данные ───────────────────────────────

def load_data(path: Path = DATA) -> dict:
    d = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(d, dict):
        raise DataError(f"{path}: словарь с generators, copies, descriptions")
    ids = set()
    for g in d.get("generators") or []:
        if not isinstance(g, dict) or not g.get("id") or bool(g.get("run")) == bool(g.get("steps")):
            raise DataError(f"{path}: у генератора id и одно из run, steps: {g}")
        if g["id"] in ids:
            raise DataError(f"{path}: id {g['id']} дважды")
        ids.add(g["id"])
    for c in d.get("copies") or []:
        for k in ("id", "canon", "canon_section", "copy", "copy_section"):
            if not (isinstance(c, dict) and c.get(k)):
                raise DataError(f"{path}: у копии нет {k}: {c}")
    return d


def steps_of(g: dict) -> list[str]:
    return list(g["steps"]) if g.get("steps") else [g["run"]]


# ─────────────────────────────── генераторы ───────────────────────────────

def expand(step: str, subst: dict) -> list[str]:
    args = shlex.split(step)
    out = []
    for a in args:
        for k, v in subst.items():
            a = a.replace("{" + k + "}", str(v))
        if re.search(r"\{(root|slug|out|today)\}", a):
            raise DataError(f"подстановка без значения в «{step}» (у строки нет fixture?)")
        out.append(a)
    tool = Path(out[0])
    out[0] = str(tool if tool.is_absolute() else kbpaths.skill(out[0]))
    if not Path(out[0]).is_file():
        raise DataError(f"нет утилиты {out[0]}")
    return out


def run_generator(g: dict, today: str) -> dict:
    """Один генератор → {id, status, seconds, note, output}."""
    ok_codes = [int(x) for x in (g.get("ok") or [0])]
    t0 = time.monotonic()
    note, output, passed = "", "", True
    with tempfile.TemporaryDirectory(prefix=f"sync_check-{g['id']}-") as td:
        subst = {"today": today, "out": Path(td) / "out"}
        if g.get("fixture"):
            b = fixture_project.build(g["fixture"], Path(td) / "root")
            subst.update(root=b.root, slug=b.slug)
        for step in steps_of(g):
            cmd = expand(step, subst)
            try:
                r = subprocess.run([kbpaths.python(), *cmd], cwd=td, capture_output=True, text=True, timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                passed, note = False, f"таймаут {TIMEOUT} с: {step}"
                break
            output = (r.stdout + r.stderr).strip()
            if r.returncode not in ok_codes:
                passed = False
                note = f"код {r.returncode} (ждали {', '.join(map(str, ok_codes))}): {step}"
                break
    xfail = g.get("xfail")
    status = ("XPASS" if xfail else "OK") if passed else ("XFAIL" if xfail else "FAIL")
    return {"id": g["id"], "status": status, "seconds": round(time.monotonic() - t0, 1), "note": note,
            "output": output, "what": g.get("what", ""), "derived": g.get("derived", ""), "xfail": xfail or ""}


def check_generators(data: dict, only: set[str] | None = None, today: str | None = None) -> tuple[list[dict], int]:
    """Строки генераторов; `{today}` — опорная дата фикстур `fixture_project.today()` (`today` — своя дата
    самопроверки)."""
    gens = [g for g in data.get("generators") or [] if not only or g["id"] in only]
    unknown = sorted((only or set()) - {g["id"] for g in data.get("generators") or []})
    if unknown:
        raise DataError(f"нет генератора {', '.join(unknown)}")
    rows, bad = [], 0
    today = today or (fixture_project.today() if gens else "")
    for g in gens:
        res = run_generator(g, today)
        rows.append(res)
        bad += res["status"] == "FAIL"
        head = f"{res['status']:<6}{res['id']:<24}{res['seconds']:>6.1f} с  {res['what']}"
        print(head)
        if res["status"] in ("FAIL", "XFAIL"):
            if res["derived"]:
                print(f"        производный файл: {res['derived']}")
            if res["note"]:
                print(f"        {res['note']}")
            if res["status"] == "XFAIL":
                print(f"        причина: {res['xfail']}")
            else:
                for ln in res["output"].splitlines()[-TAIL_LINES:]:
                    print(f"        | {ln[:160]}")
        elif res["status"] == "XPASS":
            print(f"        причины уже нет — снять xfail у строки {res['id']} в data/sync.yaml")
    return rows, bad


# ─────────────────────────────── копии ───────────────────────────────

def code_block(path: Path, section: str, n: int) -> str | None:
    """Текст n-го блока кода (```…```) раздела с заголовком, содержащим имя; раздел — до заголовка того же уровня."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    start = level = None
    for i, ln in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.*)", ln)
        if m and start is None and section.lower() in m.group(2).lower():
            start, level = i + 1, len(m.group(1))
            continue
        if m and start is not None and len(m.group(1)) <= level:
            lines = lines[start:i]
            break
    else:
        if start is None:
            return None
        lines = lines[start:]
    blocks, cur = [], None
    for ln in lines:
        if ln.lstrip().startswith("```"):
            if cur is None:
                cur = []
            else:
                blocks.append("".join(cur))
                cur = None
            continue
        if cur is not None:
            cur.append(ln)
    return blocks[n - 1] if 0 < n <= len(blocks) else None


def check_copies(data: dict, root: Path = ROOT) -> tuple[list[dict], int]:
    rows, bad = [], 0
    for c in data.get("copies") or []:
        canon, copy = root / c["canon"], root / c["copy"]
        for p in (canon, copy):
            if not p.is_file():
                raise DataError(f"копия {c['id']}: нет файла {p}")
        n = int(c.get("block", 1))
        a = code_block(canon, c["canon_section"], n)
        b = code_block(copy, c["copy_section"], n)
        if a is None or b is None:
            miss = [f"{c['canon']} § {c['canon_section']}" if a is None else "",
                    f"{c['copy']} § {c['copy_section']}" if b is None else ""]
            msg = f"нет блока кода {n}: {'; '.join(x for x in miss if x)}"
            status = "FAIL"
        elif a == b:
            msg, status = f"копия совпадает с каноном ({len(a.splitlines())} строк)", "OK"
        else:
            status = "FAIL"
            diff = difflib.unified_diff(a.splitlines(), b.splitlines(), f"канон {c['canon']}", f"копия {c['copy']}",
                                        lineterm="", n=0)
            msg = "копия расходится с каноном — прав канон, правится копия:\n" + "\n".join(
                f"        {ln}" for ln in list(diff)[:40])
        bad += status == "FAIL"
        rows.append({"id": c["id"], "status": status, "message": msg, "copy": c["copy"], "canon": c["canon"]})
        print(f"{status:<6}{c['id']:<24}{c['copy']} против {c['canon']} § {c['canon_section']}: {msg}")
    return rows, bad


# ─────────────────────────────── описания ───────────────────────────────

def description_of(path: Path) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8")
    fm = text.split("---", 2)[1] if text.startswith("---") else ""
    d = yaml.safe_load(fm) or {}
    return str(d.get("description", "")), bool(d.get("disable-model-invocation"))


def check_descriptions(data: dict, root: Path = ROOT) -> tuple[dict, int]:
    spec = data.get("descriptions") or {}
    pattern, limit, total_max = spec.get("skills", ".claude/skills/*/SKILL.md"), int(spec.get("max", 600)), \
        int(spec.get("total_max", 18000))
    rows, over, hidden = [], [], []
    for p in sorted(root.glob(pattern)):
        desc, hide = description_of(p)
        name = p.parent.name
        rows.append((name, len(desc)))
        if len(desc) > limit:
            over.append((p.relative_to(root).as_posix(), len(desc)))
        if hide:
            hidden.append(p.relative_to(root).as_posix())
    total = sum(n for _, n in rows)
    bad = len(over) + len(hidden) + (total > total_max)
    status = "FAIL" if bad else "OK"
    longest = max(rows, key=lambda x: x[1]) if rows else ("—", 0)
    print(f"{status:<6}{'descriptions':<24}скиллов {len(rows)}, сумма {total} знаков (≤ {total_max}); длиннее {limit} — "
          f"{len(over)}; скрытых от модели — {len(hidden)}; самое длинное — {longest[0]} ({longest[1]})")
    for f, n in over:
        print(f"        {f}: {n} знаков (> {limit})")
    for f in hidden:
        print(f"        {f}: скрыт от модели (disable-model-invocation)")
    if total > total_max:
        print(f"        сумма {total} > {total_max}")
    return {"skills": len(rows), "total": total, "over": over, "hidden": hidden, "status": status}, bad


# ─────────────────────────────── самопроверка ───────────────────────────────

def selftest() -> int:
    """Данные скилла и три проверки на временных файлах: коды генератора, xfail, подстановки фикстуры; копия блока;
    предел описаний."""
    ok = fail = 0

    def ok_if(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    def quiet(fn, *a):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            res = fn(*a)
        return res, buf.getvalue()

    data = load_data()
    missing = []
    for g in data.get("generators") or []:
        for step in steps_of(g):
            tool = kbpaths.skill(shlex.split(step)[0])
            if not tool.is_file():
                missing.append(str(tool))
        if g.get("fixture") and g["fixture"] not in fixture_project.names():
            missing.append(f"фикстура {g['fixture']}")
    ok_if("данные: утилиты и фикстуры строк есть", not missing)
    with tempfile.TemporaryDirectory(prefix="sync_check-selftest-") as td:
        d = Path(td)
        probe = d / "probe.py"
        probe.write_text("import sys, pathlib\n"
                         "a = sys.argv[1:]\n"
                         "if a[0] == 'code': sys.exit(int(a[1]))\n"
                         "if a[0] == 'day': sys.exit(0 if a[1] == a[2] else 1)\n"
                         "root = pathlib.Path(a[1])\n"
                         "ok = (root / 'docs' / 'projects' / a[2]).is_dir() and a[3] == '2026-01-02'\n"
                         "print('корень', root, 'проект', a[2]); sys.exit(0 if ok else 1)\n", encoding="utf-8")
        gens = {"generators": [
            {"id": "ok", "run": f"{probe} code 0"},
            {"id": "fail", "run": f"{probe} code 1", "derived": "kb/x.yaml"},
            {"id": "ok-codes", "run": f"{probe} code 1", "ok": [0, 1]},
            {"id": "xfail", "run": f"{probe} code 1", "xfail": "известно"},
            {"id": "xpass", "run": f"{probe} code 0", "xfail": "известно"},
            {"id": "fixture", "fixture": "minimal", "steps": [f"{probe} code 0", f"{probe} root {{root}} {{slug}} {{today}}"]},
        ]}
        (rows, bad), out = quiet(check_generators, gens, None, "2026-01-02")
        st = {r["id"]: r["status"] for r in rows}
        ok_if("генератор: коды и xfail — OK, FAIL, OK по ok, XFAIL, XPASS",
              st == {"ok": "OK", "fail": "FAIL", "ok-codes": "OK", "xfail": "XFAIL", "xpass": "XPASS", "fixture": "OK"}
              and bad == 1)
        ok_if("FAIL называет производный файл", "производный файл: kb/x.yaml" in out)
        ok_if("фикстура: подстановки {root}, {slug}, {today} и шаги по порядку", st["fixture"] == "OK")
        (rows, _), _ = quiet(check_generators, {"generators": [
            {"id": "day", "run": f"{probe} day {{today}} {fixture_project.today()}"}]})
        ok_if("{today} без своей даты — опорная дата фикстур fixture_project.today()", rows[0]["status"] == "OK")
        try:
            quiet(check_generators, {"generators": [{"id": "x", "run": "scripts/нет/такой.py"}]})
            ok_if("нет утилиты — ошибка данных", False)
        except DataError:
            ok_if("нет утилиты — ошибка данных", True)
        grammar = "```\nузел := лист | ветвь\nлист := голова\n```\n"
        (d / "canon.md").write_text("# К\n\n## Нотация дерева\n\nтекст\n\n" + grammar + "\n## Дальше\n\n```\nx\n```\n",
                                    encoding="utf-8")
        (d / "copy.md").write_text("# Копия\n\n## Грамматика\n\n" + grammar, encoding="utf-8")
        cp = {"copies": [{"id": "g", "canon": "canon.md", "canon_section": "Нотация дерева", "copy": "copy.md",
                          "copy_section": "Грамматика", "block": 1}]}
        (rows, bad), _ = quiet(check_copies, cp, d)
        ok_if("копия совпадает с каноном — OK", rows[0]["status"] == "OK" and bad == 0)
        (d / "copy.md").write_text("# Копия\n\n## Грамматика\n\n```\nузел := лист\nлист := голова\n```\n",
                                   encoding="utf-8")
        (rows, bad), out = quiet(check_copies, cp, d)
        ok_if("копия расходится — FAIL с диффом и именами файлов", bad == 1 and "-узел := лист | ветвь" in out
              and "+узел := лист" in out and "copy.md" in out)
        cp["copies"][0]["copy_section"] = "Нет раздела"
        (rows, bad), out = quiet(check_copies, cp, d)
        ok_if("нет раздела копии — FAIL", bad == 1 and "нет блока кода" in out)
        sk = d / ".claude" / "skills"
        for name, desc, extra in (("a", "x" * 600, ""), ("b", "y" * 601, ""), ("c", "z", "disable-model-invocation: true\n")):
            (sk / name).mkdir(parents=True)
            (sk / name / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n{extra}---\n\n# {name}\n",
                                                encoding="utf-8")
        (res, bad), out = quiet(check_descriptions, {"descriptions": {"skills": ".claude/skills/*/SKILL.md", "max": 600,
                                                                        "total_max": 1000}}, d)
        ok_if("описания: 601 знак, скрытый скилл и сумма сверх предела — FAIL с именами",
              bad == 3 and ".claude/skills/b/SKILL.md: 601" in out and ".claude/skills/c/SKILL.md: скрыт" in out
              and "сумма 1202 > 1000" in out)
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


# ─────────────────────────────── запуск ───────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 epilog=__doc__.split("\n", 2)[2], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", nargs="?", default="all", choices=("all", "generators", "copies", "descriptions"))
    ap.add_argument("--only", default="", help="id генераторов через запятую")
    ap.add_argument("--list", action="store_true", help="строки данных без запуска")
    ap.add_argument("--json", action="store_true", help="итог JSON в stdout после таблицы")
    ap.add_argument("--selftest", action="store_true", help="самопроверка на временных файлах, без сети")
    a = ap.parse_args(argv)
    try:
        if a.selftest:
            return selftest()
        data = load_data()
        if a.list:
            for g in data.get("generators") or []:
                fx = f" [фикстура {g['fixture']}]" if g.get("fixture") else ""
                xf = " [xfail]" if g.get("xfail") else ""
                print(f"generators  {g['id']:<24}{g.get('what', '')}{fx}{xf}")
            for c in data.get("copies") or []:
                print(f"copies      {c['id']:<24}{c['copy']} § {c['copy_section']} ← {c['canon']} § {c['canon_section']}")
            print(f"descriptions {data.get('descriptions', {}).get('skills', '')}")
            return 0
        only = {x.strip() for x in a.only.split(",") if x.strip()} or None
        unknown = sorted((only or set()) - {g["id"] for g in data.get("generators") or []})
        if unknown:
            raise DataError(f"нет генератора {', '.join(unknown)}")
        report, bad = {}, 0
        if a.what in ("all", "generators"):
            print("== генераторы и сборки на фикстурах")
            report["generators"], n = check_generators(data, only)
            bad += n
        if a.what in ("all", "copies"):
            print("== управляемые копии")
            report["copies"], n = check_copies(data)
            bad += n
        if a.what in ("all", "descriptions"):
            print("== описания скиллов")
            report["descriptions"], n = check_descriptions(data)
            bad += n
        gens = report.get("generators") or []
        counts = {s: sum(r["status"] == s for r in gens) for s in ("OK", "FAIL", "XFAIL", "XPASS")}
        print(f"ИТОГО: генераторы — OK {counts['OK']}, FAIL {counts['FAIL']}, XFAIL {counts['XFAIL']}, "
              f"XPASS {counts['XPASS']}; копий расходится — {sum(r['status'] == 'FAIL' for r in report.get('copies', []))}; "
              f"описания — {report.get('descriptions', {}).get('status', '—')}; находок {bad}")
        if a.json:
            for r in gens:
                r.pop("output", None)
            print(json.dumps(report, ensure_ascii=False, indent=1))
        return 1 if bad else 0
    except (DataError, fixture_project.FixtureError, OSError, yaml.YAMLError) as e:
        print(f"sync_check: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
