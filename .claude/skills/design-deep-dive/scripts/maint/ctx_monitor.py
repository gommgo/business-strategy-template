#!/usr/bin/env python3
"""ctx_monitor — монитор контекста фоновых агентов сессии.

Для того, кто ведёт несколько фоновых агентов и должен принять у агента файл передачи раньше, чем кончится окно
модели. Утилита читает из журналов агентов только счётчики токенов последнего ответа модели (ввод, чтение кэша и
запись кэша — вместе это контекст агента) и печатает строку-событие, когда контекст переходит порог. Содержимое
журналов не печатается и никуда не пишется.

    python3 .claude/skills/design-deep-dive/scripts/maint/ctx_monitor.py --logs ПАПКА [--window 1000000]
                                [--warn 0.9] [--stop 0.95] [--poll 20] [--active-min 15] [--state ФАЙЛ] [--json]
    python3 .claude/skills/design-deep-dive/scripts/maint/ctx_monitor.py --logs ПАПКА [--window ТОКЕНЫ] --once [--json]
    python3 .claude/skills/design-deep-dive/scripts/maint/ctx_monitor.py --selftest

`--logs` — папка журналов субагентов сессии: файлы `agent-<id>.jsonl`, строка — запись JSON, у ответа модели —
`message.usage`. `--window` — окно модели в токенах, по умолчанию 1 000 000; пороги — доли окна: `--warn` (агенту
пора готовить файл передачи; по умолчанию 0,9 — 900 000 токенов) и `--stop` (агенту пора записать результат и
завершиться; по умолчанию 0,95 — 950 000 токенов).

Наблюдение (по умолчанию): папка перечитывается каждые `--poll` секунд до прерывания; событие — строка
`CTX <уровень> <агент> <токены> <доля окна>`, с `--json` — объект JSON на строку. На агента и уровень — одно событие;
контекст, который между проходами перешёл оба порога, даёт одно событие `stop`. Контекст, упавший ниже 0,8 порога
`warn` (сжатие или продолжатель), взводит оба порога заново. Агент, журнал которого не менялся дольше `--active-min`
минут, событий не даёт. Выданные события хранит файл состояния — `--state`, по умолчанию
`$DDD_HOME/out/maint/ctx_monitor/<ключ папки журналов>.json`: перезапуск монитора событий не повторяет.

`--once` — один проход без файла состояния: строка на агента — `<агент> <токены> <доля окна> <простой, мин> <уровень>`
(уровень `ok`, `warn` или `stop`; «-» — ответа модели в журнале нет), с `--json` — объект JSON на строку.

Формат журнала принадлежит среде агента, а не скиллу. Незнакомый формат — в папке есть файлы, но нет ни одного
`agent-*.jsonl`; в журнале нет ни одной записи JSON; у ответа модели нет ни одного из трёх счётчиков — ошибка
окружения: сообщение в stderr и код 2, а не молчание.

Код выхода: 0 — до порога `stop` не дошёл ни один активный агент; 1 — дошёл; 2 — ошибка вызова или окружения (нет
папки журналов, незнакомый формат журнала, файл состояния не читается или не пишется). Только стандартная
библиотека, сети нет.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
import kbpaths  # noqa: E402

PREFIX, SUFFIX = "agent-", ".jsonl"
COUNTERS = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")
WINDOW = 1_000_000              # окно модели по умолчанию, токенов
WARN, STOP = 0.9, 0.95          # пороги по умолчанию, доли окна: 900 000 и 950 000 токенов окна по умолчанию
TAIL = 4 * 1024 * 1024          # последний ответ модели помещается в хвост журнала: большой журнал целиком не читается
REARM = 0.8                     # контекст ниже этой доли порога warn — новый виток агента: пороги взводятся заново
LEVELS = ("stop", "warn")       # порядок сверки: старший уровень первым


class FormatError(Exception):
    """Журнал или папка не того формата, который утилита читает."""


def last_ctx(path: Path, tail: int = TAIL) -> int | None:
    """Контекст последнего ответа модели в журнале: сумма трёх счётчиков `message.usage`; None — ответа нет.
    Читается хвост файла; оборванная первая строка хвоста и недописанная последняя не разбираются."""
    size = path.stat().st_size
    with open(path, "rb") as fh:
        cut = size > tail
        if cut:
            fh.seek(size - tail)
        lines = fh.read().split(b"\n")
    lines.pop()                                         # после последнего «\n» — пусто или недописанная строка
    if cut and lines:
        lines.pop(0)
    ctx, parsed = None, False
    for raw in lines:
        if b'"usage"' not in raw:
            continue
        try:
            rec = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(rec, dict):
            continue
        parsed = True
        msg = rec.get("message")
        usage = msg.get("usage") if isinstance(msg, dict) else None
        if not isinstance(usage, dict):
            continue
        if not any(isinstance(usage.get(k), int) for k in COUNTERS):
            raise FormatError(f"{path.name}: у ответа модели нет счётчиков {', '.join(COUNTERS)}")
        total = sum(usage.get(k) or 0 for k in COUNTERS)
        if total:                                       # запись без токенов — сообщение среды, а не ответ модели
            ctx = total
    if ctx is None and not parsed and any(raw.strip() for raw in lines) and not any(_is_record(raw) for raw in lines):
        raise FormatError(f"{path.name}: в журнале нет ни одной записи JSON")
    return ctx


def _is_record(raw: bytes) -> bool:
    try:
        return isinstance(json.loads(raw), dict)
    except ValueError:
        return False


def journals(logs: Path) -> dict[str, Path]:
    """Журналы агентов папки: {id агента: файл}. В папке есть файлы, но журналов среди них нет — незнакомый формат."""
    files = sorted(p for p in logs.iterdir() if p.is_file() and not p.name.startswith("."))
    found = {p.name[len(PREFIX):-len(SUFFIX)]: p for p in files
             if p.name.startswith(PREFIX) and p.name.endswith(SUFFIX)}
    if files and not found:
        raise FormatError(f"{logs}: в папке нет журналов {PREFIX}*{SUFFIX}")
    return found


def readings(logs: Path, now: float) -> list[tuple[str, int | None, float]]:
    """Показания прохода: [(агент, контекст или None, простой журнала в минутах)]."""
    rows = []
    for agent, path in journals(logs).items():
        try:
            idle = (now - path.stat().st_mtime) / 60
            rows.append((agent, last_ctx(path), idle))
        except FileNotFoundError:                       # журнал убран между перечислением папки и чтением
            continue
    return rows


def level_of(ctx: int, warn_at: float, stop_at: float) -> str:
    return "stop" if ctx >= stop_at else "warn" if ctx >= warn_at else "ok"


def step(rows, state: dict, warn_at: float, stop_at: float, active_min: float) -> list[tuple[str, str, int]]:
    """Один проход наблюдения. state — выданные события {агент: {уровень: токены}}, правится на месте.
    → новые события [(уровень, агент, токены)]: на агента и уровень — одно, `stop` заменяет `warn`."""
    events = []
    for agent, ctx, idle in rows:
        if ctx is None or idle > active_min:
            continue
        seen = state.setdefault(agent, {})
        if ctx < warn_at * REARM:
            seen.clear()
        for level, at in zip(LEVELS, (stop_at, warn_at)):
            if ctx >= at and level not in seen:
                seen[level] = ctx
                if level == "stop":
                    seen.setdefault("warn", ctx)
                events.append((level, agent, ctx))
                break
    return events


def state_file(logs: Path) -> Path:
    """Файл состояния по умолчанию: свой у каждой папки журналов, в выходах утилиты."""
    key = hashlib.sha256(str(logs).encode("utf-8")).hexdigest()[:16]
    return kbpaths.out("maint", "ctx_monitor") / f"{key}.json"


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(isinstance(v, dict) for v in data.values()):
        raise ValueError("ожидается объект {агент: {уровень: токены}}")
    return data


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps({k: v for k, v in state.items() if v}, ensure_ascii=False, sort_keys=True),
                   encoding="utf-8")
    os.replace(tmp, path)


def event_line(level: str, agent: str, ctx: int, window: int, as_json: bool) -> str:
    if as_json:
        return json.dumps({"level": level, "agent": agent, "tokens": ctx, "share": round(ctx / window, 3),
                           "window": window}, ensure_ascii=False)
    return f"CTX {level} {agent} {ctx} {ctx / window:.2f}"


def once(logs: Path, window: int, warn: float, stop: float, active_min: float, as_json: bool) -> int:
    """Один проход: строка на агента. → 1, если активный агент дошёл до порога `stop`, иначе 0."""
    hit = False
    for agent, ctx, idle in readings(logs, time.time()):
        level = level_of(ctx, window * warn, window * stop) if ctx is not None else None
        hit = hit or (level == "stop" and idle <= active_min)
        if as_json:
            share = round(ctx / window, 3) if ctx is not None else None
            print(json.dumps({"agent": agent, "tokens": ctx, "share": share, "idle_min": round(idle, 1),
                              "level": level}, ensure_ascii=False), flush=True)
        else:
            share = f"{ctx / window:.2f}" if ctx is not None else "-"
            print(f"{agent} {ctx if ctx is not None else '-'} {share} {idle:.0f} {level or '-'}", flush=True)
    return 1 if hit else 0


def watch(logs: Path, window: int, warn: float, stop: float, active_min: float, poll: float, path: Path,
          as_json: bool, passes: int | None = None, sleep=time.sleep) -> int:
    """Наблюдение до прерывания (passes — число проходов, None — без предела). → 1, если было событие `stop`."""
    state = load_state(path)
    hit, done = False, 0
    try:
        while passes is None or done < passes:
            before = json.dumps(state, sort_keys=True)
            for level, agent, ctx in step(readings(logs, time.time()), state, window * warn, window * stop, active_min):
                hit = hit or level == "stop"
                print(event_line(level, agent, ctx, window, as_json), flush=True)
            if json.dumps(state, sort_keys=True) != before:
                save_state(path, state)
            done += 1
            if passes is None or done < passes:
                sleep(poll)
    except KeyboardInterrupt:
        pass
    return 1 if hit else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--logs", metavar="ПАПКА", help="папка журналов субагентов сессии (файлы agent-<id>.jsonl)")
    ap.add_argument("--window", type=int, default=WINDOW, metavar="ТОКЕНЫ",
                    help=f"окно модели в токенах (по умолчанию {WINDOW})")
    ap.add_argument("--warn", type=float, default=WARN, metavar="ДОЛЯ",
                    help=f"порог «готовь файл передачи», доля окна (по умолчанию {WARN})")
    ap.add_argument("--stop", type=float, default=STOP, metavar="ДОЛЯ",
                    help=f"порог «запиши результат и завершись», доля окна (по умолчанию {STOP})")
    ap.add_argument("--poll", type=float, default=20, metavar="СЕК", help="пауза между проходами наблюдения")
    ap.add_argument("--active-min", type=float, default=15, metavar="МИН",
                    help="журнал без изменений дольше — агент не активен, событий нет")
    ap.add_argument("--state", metavar="ФАЙЛ", help="файл состояния наблюдения (по умолчанию — в выходах утилиты)")
    ap.add_argument("--once", action="store_true", help="один проход: строка на агента, без файла состояния")
    ap.add_argument("--json", action="store_true", help="строки вывода — объекты JSON")
    ap.add_argument("--selftest", action="store_true", help="самопроверка на образце журнала в коде, без сети")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.logs:
        ap.error("назовите --logs (или --selftest)")
    if args.window <= 0 or not 0 < args.warn < args.stop <= 1 or args.poll <= 0 or args.active_min <= 0:
        ap.error("ожидается: --window > 0, 0 < --warn < --stop ≤ 1, --poll > 0, --active-min > 0")
    logs = Path(args.logs).expanduser().resolve()
    if not logs.is_dir():
        print(f"ctx_monitor: нет папки журналов {logs}", file=sys.stderr)
        return 2
    try:
        if args.once:
            return once(logs, args.window, args.warn, args.stop, args.active_min, args.json)
        path = Path(args.state).expanduser() if args.state else state_file(logs)
        return watch(logs, args.window, args.warn, args.stop, args.active_min, args.poll, path, args.json)
    except FormatError as e:
        print(f"ctx_monitor: незнакомый формат журнала — {e}; формат задаёт среда агента, утилита читает "
              f"{PREFIX}<id>{SUFFIX} со счётчиками message.usage", file=sys.stderr)
        return 2
    except (OSError, ValueError) as e:
        print(f"ctx_monitor: {e}", file=sys.stderr)
        return 2


# ─────────────────────────────── самопроверка ───────────────────────────────

SAMPLE_TASK = {"type": "user", "message": {"role": "user", "content": "Собери таблицу по трём разделам."}}


def _answer(fresh: int, cache_read: int = 0, cache_new: int = 0) -> dict:
    """Запись ответа модели образца журнала: счётчики — как их пишет среда агента."""
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": "Готово."}],
                                             "usage": {"input_tokens": fresh, "cache_read_input_tokens": cache_read,
                                                       "cache_creation_input_tokens": cache_new, "output_tokens": 40}}}


def _journal(folder: Path, agent: str, records: list, tail: str = "") -> Path:
    path = folder / f"{PREFIX}{agent}{SUFFIX}"
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records) + tail, encoding="utf-8")
    return path


def selftest() -> int:
    """Образец журнала во временной папке: чтение контекста, пороги и события, взвод заново, простой, состояние между
    запусками, один проход, умолчания окна и порогов, незнакомый формат."""
    import contextlib
    import io
    import tempfile
    ok = fail = 0

    def check(name, cond):
        nonlocal ok, fail
        print(("OK   " if cond else "FAIL ") + name)
        ok, fail = ok + bool(cond), fail + (not cond)

    def run(argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = main(argv)
            except SystemExit as e:
                rc = e.code
        return rc, out.getvalue(), err.getvalue()

    def raises(fn, *a):
        try:
            fn(*a)
        except FormatError:
            return True
        return False

    old_home = os.environ.get(kbpaths.ENV_HOME)
    with tempfile.TemporaryDirectory(prefix="ctx-monitor-") as td:
        os.environ[kbpaths.ENV_HOME] = str(Path(td) / "home")
        try:
            logs = Path(td) / "subagents"
            logs.mkdir()
            a = _journal(logs, "a01", [SAMPLE_TASK, _answer(10, 400, 90), _answer(20, 500, 130)])
            check("контекст — сумма трёх счётчиков последнего ответа", last_ctx(a) == 650)
            check("журнал без ответа модели — None", last_ctx(_journal(logs, "n00", [SAMPLE_TASK])) is None)
            torn = '{"type": "assistant", "message": {"usage"'
            check("недописанная последняя строка не разбирается",
                  last_ctx(_journal(logs, "p00", [_answer(5, 300, 0)], torn)) == 305)
            check("хвост: оборванная первая строка пропущена, последний ответ прочитан", last_ctx(a, tail=260) == 650)
            zero = _answer(0)
            check("запись без токенов — сообщение среды, контекст берётся из ответа перед ней",
                  last_ctx(_journal(logs, "z00", [_answer(7, 200, 0), zero])) == 207)
            for name in ("n00", "p00", "z00"):
                (logs / f"{PREFIX}{name}{SUFFIX}").unlink()
            _journal(logs, "b02", [SAMPLE_TASK, _answer(100, 700, 100)])
            _journal(logs, "c03", [SAMPLE_TASK, _answer(100)])
            window, state = 1000, {}
            now = time.time()
            ev = step(readings(logs, now), state, window * 0.6, window * 0.8, 15)
            check("пороги: 0,65 окна — warn, 0,9 окна — одно событие stop, 0,1 окна — ничего",
                  sorted(ev) == [("stop", "b02", 900), ("warn", "a01", 650)])
            check("повторный проход событий не повторяет", step(readings(logs, now), state, 600, 800, 15) == [])
            _journal(logs, "a01", [SAMPLE_TASK, _answer(50, 700, 100)])
            check("рост до порога stop — событие stop", step(readings(logs, now), state, 600, 800, 15) == [
                ("stop", "a01", 850)])
            _journal(logs, "a01", [SAMPLE_TASK, _answer(50, 500, 0)])
            check("спад выше 0,8 порога warn пороги не взводит", step(readings(logs, now), state, 600, 800, 15) == []
                  and "stop" in state["a01"])
            _journal(logs, "a01", [SAMPLE_TASK, _answer(100)])
            step(readings(logs, now), state, 600, 800, 15)
            _journal(logs, "a01", [SAMPLE_TASK, _answer(100, 600, 0)])
            check("спад ниже 0,8 порога warn взводит пороги заново", step(readings(logs, now), state, 600, 800, 15) == [
                ("warn", "a01", 700)])
            check("простой дольше --active-min — событий нет",
                  step(readings(logs, now + 16 * 60), {}, 600, 800, 15) == [])

            common = ["--logs", str(logs), "--window", "1000"]
            sfile = Path(td) / "state.json"
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                hit = watch(logs, 1000, 0.6, 0.8, 15, 20, sfile, False, passes=2, sleep=lambda s: None)
            check("наблюдение: два прохода — события по разу, состояние записано, код 1 при событии stop",
                  hit == 1 and out.getvalue().splitlines() == ["CTX warn a01 700 0.70", "CTX stop b02 900 0.90"]
                  and load_state(sfile) == {"a01": {"warn": 700}, "b02": {"stop": 900, "warn": 900}})
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                again = watch(logs, 1000, 0.6, 0.8, 15, 20, sfile, True, passes=1, sleep=lambda s: None)
            check("перезапуск с файлом состояния событий не повторяет", again == 0 and out.getvalue() == "")
            check("файл состояния по умолчанию — в выходах утилиты, свой у папки журналов",
                  state_file(logs).parent == kbpaths.out("maint", "ctx_monitor", create=False)
                  and state_file(logs) != state_file(Path(td)))
            check("строка события и её JSON",
                  event_line("warn", "a01", 700, 1000, False) == "CTX warn a01 700 0.70"
                  and json.loads(event_line("stop", "b02", 900, 1000, True)) == {
                      "level": "stop", "agent": "b02", "tokens": 900, "share": 0.9, "window": 1000})

            rc, text, _ = run(common + ["--once", "--warn", "0.6", "--stop", "0.8"])
            check("--once: строка на агента и код 1 при агенте на пороге stop",
                  rc == 1 and text.splitlines() == ["a01 700 0.70 0 warn", "b02 900 0.90 0 stop", "c03 100 0.10 0 ok"])
            rc, text, _ = run(common + ["--once", "--json", "--warn", "0.6", "--stop", "0.95"])
            rows = [json.loads(x) for x in text.splitlines()]
            check("--once --json: объект на строку, порог из ключа, код 0",
                  rc == 0 and [(r["agent"], r["level"]) for r in rows] == [("a01", "warn"), ("b02", "warn"),
                                                                           ("c03", "ok")])
            big = Path(td) / "big"
            big.mkdir()
            for name, tokens in (("d04", 899_999), ("e05", 900_000), ("f06", 949_999), ("g07", 950_000)):
                _journal(big, name, [SAMPLE_TASK, _answer(tokens - 400_000, 400_000)])
            rc, text, _ = run(["--logs", str(big), "--once"])
            check("умолчания без ключей: окно 1 000 000, warn — с 900 000 токенов, stop — с 950 000, код 1",
                  rc == 1 and [x.split()[0] + " " + x.split()[-1] for x in text.splitlines()] == [
                      "d04 ok", "e05 warn", "f06 warn", "g07 stop"]
                  and (WINDOW, WINDOW * WARN, WINDOW * STOP) == (1_000_000, 900_000, 950_000))

            check("вызов: нет папки, нет --logs, пороги не по порядку — код 2",
                  run(["--logs", str(logs / "nope"), "--window", "1000", "--once"])[0] == 2
                  and run(["--once"])[0] == 2
                  and run(common + ["--once", "--warn", "0.9", "--stop", "0.8"])[0] == 2)
            bad = Path(td) / "bad"
            bad.mkdir()
            (bad / "session.log").write_text("запись среды\n", encoding="utf-8")
            rc, _, err = run(["--logs", str(bad), "--window", "1000", "--once"])
            check("незнакомый формат: в папке нет журналов агентов — код 2 и сообщение", rc == 2 and "формат" in err)
            (bad / "session.log").unlink()
            plain = bad / f"{PREFIX}x09{SUFFIX}"
            plain.write_text("ответ модели: 650 токенов\nещё строка\n", encoding="utf-8")
            rc, _, err = run(["--logs", str(bad), "--window", "1000", "--once"])
            check("незнакомый формат: в журнале нет записей JSON — код 2 и сообщение",
                  rc == 2 and "x09" in err and raises(last_ctx, plain))
            renamed = _answer(0)
            renamed["message"]["usage"] = {"prompt_tokens": 650, "completion_tokens": 40}
            _journal(bad, "x09", [SAMPLE_TASK, renamed])
            rc, _, err = run(["--logs", str(bad), "--window", "1000", "--once"])
            check("незнакомый формат: у ответа нет известных счётчиков — код 2 и сообщение",
                  rc == 2 and "счётчиков" in err)
            empty = Path(td) / "empty"
            empty.mkdir()
            check("пустая папка журналов — не ошибка: строк нет, код 0",
                  run(["--logs", str(empty), "--window", "1000", "--once"])[:2] == (0, ""))
        finally:
            if old_home is None:
                os.environ.pop(kbpaths.ENV_HOME, None)
            else:
                os.environ[kbpaths.ENV_HOME] = old_home
    print(f"selftest: {ok} OK, {fail} FAIL")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
