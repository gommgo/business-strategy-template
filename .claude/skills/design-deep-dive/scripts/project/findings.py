#!/usr/bin/env python3
"""findings — формат находок утилит `scripts/project/`: одна копия для всех утилит раздела и их читателей.

Находка — строка JSON (JSON Lines) из восьми полей в этом порядке:

    {"rule": "R-STRUCT-021", "severity": "error", "surface": "office", "kind": "block",
     "ref": "requests-list#/tree/block-header/0",
     "path": "docs/projects/otves-office/screens/office/blocks/requests-list/index.md",
     "message": "ui:Navbar — имя из aka словаря компонентов; тип словаря — TopBar",
     "fix": "заменить на ui:TopBar — /screen-deep-dive otves-office office block:requests-list"}

  rule      id правила аудита слоя (`R-…` реестра `references/rules.md` скилла аудита) — по нему находку читает аудит
  severity  error · warning · hint
  surface   slug поверхности; null — находка уровня проекта
  kind      вид записи: у слоя экранов — screen · block · shell · flow · map · texts, у поверхности целиком —
            surface; утилиты других слоёв пишут вид своей записи тем же словом-slug (например, system, ready)
  ref       slug записи и место в ней: `<slug>` или `<slug>#<место>`; место в дереве — JSON Pointer в разобранном
            YAML тела (`#/states/not-found`, `#/tree/block-body/0`), в своде — `map#<раздел>/<ключ строки>`, в реестре
            текстов — `texts#<ключ>`, у поверхности — её slug
  path      файл от корня данных (`docpaths.rel`) — `docs/projects/<slug>/…`
  message   что не так, словами канона
  fix       что сделать и каким скиллом; пусто — если правка очевидна из сообщения

Коды выхода утилит раздела: 0 — ошибок нет (предупреждения и подсказки не мешают), 1 — есть находки `error`
(у нормализатора — есть что править), 2 — ошибка вызова или окружения (нет проекта, поверхности, файла словаря).

Вывод: `check --json` печатает находки строками JSON и больше ничего; без `--json` — таблица и строка итога.

Подключение в утилите и у читателя (аудит, манифест готовности):

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import findings as F
    rep = F.Report()
    rep.add("R-STRUCT-021", "error", surface="office", kind="block", ref="x#/tree", path="docs/…", message="…")
    F.print_findings(rep.items, as_json=call.json)
    return rep.exit_code()

    items = F.parse_lines(stdout)       # читатель: строки JSON → [Finding], чужая строка — ValueError

Самопроверка: `python3 findings.py --selftest`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass

FIELDS = ("rule", "severity", "surface", "kind", "ref", "path", "message", "fix")
SEVERITIES = ("error", "warning", "hint")
KINDS = ("screen", "block", "shell", "flow", "map", "texts", "surface")   # виды записей слоя экранов
KIND_FORM = re.compile(r"^[a-z][a-z0-9-]*$")
EXIT_OK, EXIT_FINDINGS, EXIT_USAGE = 0, 1, 2
_ORDER = {s: i for i, s in enumerate(SEVERITIES)}


class ToolError(RuntimeError):
    """Ошибка окружения утилиты (нет файла словаря, битые данные базы) — код выхода 2."""


@dataclass(frozen=True)
class Finding:
    rule: str
    severity: str
    surface: str | None
    kind: str
    ref: str
    path: str
    message: str
    fix: str = ""

    def __post_init__(self):
        if self.severity not in SEVERITIES:
            raise ValueError(f"severity: {' · '.join(SEVERITIES)}, не {self.severity!r}")
        if not KIND_FORM.match(str(self.kind or "")):
            raise ValueError(f"kind — вид записи словом-slug ({' · '.join(KINDS)} …), не {self.kind!r}")
        if not str(self.rule).startswith("R-"):
            raise ValueError(f"rule — id правила аудита (R-…), не {self.rule!r}")

    def as_dict(self):
        return {k: getattr(self, k) for k in FIELDS}

    def line(self):
        """Строка JSON находки."""
        return json.dumps(self.as_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, d):
        if not isinstance(d, dict) or set(d) != set(FIELDS):
            got = sorted(d) if isinstance(d, dict) else type(d).__name__
            raise ValueError(f"находка — объект с полями {', '.join(FIELDS)}; пришло: {got}")
        return cls(**{k: d[k] for k in FIELDS})


def severity_for(status, draft="warning", stable="error"):
    """Тяжесть по статусу записи: у `stable` — stable, у остальных — draft (правила «warning, error@stable»)."""
    return stable if status == "stable" else draft


class Report:
    """Сборщик находок: одна находка на (rule, ref, message); порядок — тяжесть, путь, ref."""

    def __init__(self):
        self._seen = set()
        self._items = []

    def add(self, rule, severity, *, surface, kind, ref, path, message, fix=""):
        f = Finding(rule, severity, surface, kind, ref, str(path), message, fix)
        key = (f.rule, f.ref, f.message)
        if key not in self._seen:
            self._seen.add(key)
            self._items.append(f)
        return f

    def extend(self, items):
        for f in items:
            self.add(f.rule, f.severity, surface=f.surface, kind=f.kind, ref=f.ref, path=f.path, message=f.message,
                     fix=f.fix)

    @property
    def items(self):
        return sorted(self._items, key=lambda f: (_ORDER[f.severity], f.path, f.ref, f.rule, f.message))

    def counts(self):
        return count(self._items)

    def exit_code(self):
        return exit_code(self._items)


def count(items):
    out = {s: 0 for s in SEVERITIES}
    for f in items:
        out[f.severity] += 1
    return out


def exit_code(items):
    return EXIT_FINDINGS if any(f.severity == "error" for f in items) else EXIT_OK


def parse_lines(text):
    """Строки JSON находок → [Finding]; пустые строки пропускаются, чужая строка — ValueError."""
    out = []
    for no, line in enumerate(str(text).splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(Finding.from_dict(json.loads(line)))
        except (ValueError, TypeError) as e:
            raise ValueError(f"строка {no}: не находка — {e}") from e
    return out


def summary(items):
    c = count(items)
    return f"итог: {c['error']} error · {c['warning']} warning · {c['hint']} hint"


def print_findings(items, as_json=False, file=None, title=None):
    """Находки: `as_json` — строки JSON; иначе — таблица по тяжести и строка итога."""
    out = file or sys.stdout
    items = sorted(items, key=lambda f: (_ORDER[f.severity], f.path, f.ref, f.rule, f.message))
    if as_json:
        for f in items:
            print(f.line(), file=out)
        return
    if title:
        print(title, file=out)
    for f in items:
        print(f"{f.severity:<8} {f.rule:<13} {f.kind} {f.ref}", file=out)
        print(f"{'':<23}{f.message}", file=out)
        print(f"{'':<23}{f.path}", file=out)
        if f.fix:
            print(f"{'':<23}→ {f.fix}", file=out)
    print(summary(items), file=out)


def _selftest():
    ok = True

    def check(msg, cond):
        nonlocal ok
        ok = ok and bool(cond)
        print(("OK   " if cond else "FAIL ") + msg)

    rep = Report()
    for _ in range(2):
        rep.add("R-TX-001", "error", surface="web", kind="screen", ref="a#/states", path="docs/projects/x/a.md",
                message="m")
    rep.add("R-RT-003", "warning", surface="web", kind="screen", ref="a", path="docs/projects/x/a.md", message="w")
    rep.add("R-TX-006", "hint", surface="web", kind="texts", ref="texts#k", path="docs/projects/x/t.md", message="h")
    check("повтор находки отбрасывается", len(rep.items) == 3)
    check("порядок — error, warning, hint", [f.severity for f in rep.items] == ["error", "warning", "hint"])
    check("код выхода 1 при error", rep.exit_code() == EXIT_FINDINGS)
    check("код выхода 0 без error", exit_code([f for f in rep.items if f.severity != "error"]) == EXIT_OK)
    lines = "\n".join(f.line() for f in rep.items)
    back = parse_lines(lines + "\n\n")
    check("строки JSON читаются обратно", back == rep.items)
    check("поля — восемь, по контракту", list(json.loads(lines.splitlines()[0])) == list(FIELDS))
    for bad in ('{"rule": "R-X"}', '[1]', 'не json'):
        try:
            parse_lines(bad)
            check(f"чужая строка отвергнута: {bad}", False)
        except ValueError:
            check(f"чужая строка отвергнута: {bad}", True)
    for kw in ({"severity": "fatal"}, {"kind": "Page view"}, {"rule": "RT-1"}):
        args = dict(rule="R-TX-001", severity="error", surface=None, kind="screen", ref="a", path="p", message="m")
        args.update(kw)
        try:
            Finding(**args)
            check(f"неверное поле отвергнуто: {kw}", False)
        except ValueError:
            check(f"неверное поле отвергнуто: {kw}", True)
    check("тяжесть по статусу: stable → error, draft → warning",
          severity_for("stable") == "error" and severity_for("draft") == "warning" and severity_for(None) == "warning")
    import io
    buf = io.StringIO()
    print_findings(rep.items, file=buf)
    check("таблица кончается строкой итога", buf.getvalue().rstrip().endswith("1 error · 1 warning · 1 hint"))
    print("findings selftest:", "OK" if ok else "FAIL")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="самопроверка формата, без сети и файлов проекта")
    ap.add_argument("--validate", metavar="FILE", help="проверить файл строк JSON находок ('-' — stdin)")
    a = ap.parse_args(argv)
    if a.selftest:
        return _selftest()
    if a.validate:
        text = sys.stdin.read() if a.validate == "-" else open(a.validate, encoding="utf-8").read()
        try:
            items = parse_lines(text)
        except ValueError as e:
            print(f"findings: {e}", file=sys.stderr)
            return EXIT_USAGE
        print(f"находок: {len(items)}; {summary(items)}")
        return EXIT_OK
    ap.print_help()
    return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
