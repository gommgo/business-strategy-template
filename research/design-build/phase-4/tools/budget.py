#!/usr/bin/env python3
"""Объём чтения узлов Ф4 в токенах: разделы файлов по заголовкам → оценка по калибровке Opus 5.5
(`scripts/maint/calibration.json`: tokens = a·кириллица + b·прочие символы; коэффициенты по виду файла —
prose для md, data для yaml/json/tsv/csv, code для py/js; множитель чтения инструментом Read).

Список чтения — `inputs/reading.tsv` (node, path, sections, note). `path` — от `kb/` или от корня репозитория
(`research/…`, `.claude/…`, `docs/…`); `sections` — `*` (весь файл) или регулярные выражения заголовков через ` || `;
раздел — от заголовка до следующего заголовка того же или более высокого уровня.

Запуск (Python 3.13, только стандартная библиотека):
    python tools/budget.py                       # таблица по узлам (markdown) и итоги
    python tools/budget.py --node TR             # один узел
    python tools/budget.py --headings <path>     # заголовки файла с объёмом разделов — чтобы выбрать разделы
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
REPO = PHASE.parent.parent.parent
KB = REPO / ".claude/skills/design-deep-dive/kb"
CAL = REPO / ".claude/skills/design-deep-dive/scripts/maint/calibration.json"
READING = PHASE / "inputs/reading.tsv"
ROWS = PHASE / "inputs/rows.tsv"
NODES = ["GL", "TR", "GT", "CM", "ST", "NU", "TX", "VI", "JU", "CN"]
HEADING = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
CYR = re.compile("[\\u0400-\\u04FF]")
KIND = {".md": "prose", ".txt": "prose", ".yaml": "data", ".yml": "data", ".json": "data", ".tsv": "data",
        ".csv": "data", ".py": "code", ".js": "code", ".css": "code", ".html": "code"}
# Постоянная часть контекста агента узла: системный промт и инструменты, PLAN.md и CHAIN.md фазы 4, выход узла
# (md и tsv), служебные вызовы. Оценка оркестратора по прошлым узлам фаз 2–3; уточняется по факту.
FIXED = {"система и инструменты": 25_000, "выход узла (md + tsv) и правки": 40_000}
WORK_FACTOR = 1.25   # повторные чтения, grep, выводы скриптов сверх прочитанного
# Выходы предыдущих узлов, которые узел читает сверх списка (nodes/*.tsv и *.md): CN сводит все девять, JU опирается на все.
EXTRA = {"CN": ("выходы узлов GL…JU (nodes/*.tsv, *.md; оценка)", 200_000),
         "JU": ("строки и записи CHAIN предыдущих узлов (оценка)", 50_000)}


def resolve(p: str) -> Path:
    if p.startswith(("research/", ".claude/", "docs/")):
        return REPO / p
    return KB / p


def calibration() -> dict:
    return json.loads(CAL.read_text(encoding="utf-8"))


def tokens(text: str, kind: str, cal: dict) -> int:
    coef = cal["kinds"].get(kind) or cal["global"]
    cyr = len(CYR.findall(text))
    return round((coef["a"] * cyr + coef["b"] * (len(text) - cyr)) * cal.get("read_tool_factor", 1.0))


def headings(lines: list[str]):
    code = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            code = not code
            continue
        if not code:
            m = HEADING.match(line)
            if m:
                yield i, len(m.group(1)), m.group(2)


def section_text(lines: list[str], pattern: str) -> tuple[str, str]:
    rx = re.compile(pattern)
    hs = list(headings(lines))
    for n, (i, lvl, text) in enumerate(hs):
        if rx.search(text):
            end = len(lines)
            for j, lvl2, _ in hs[n + 1:]:
                if lvl2 <= lvl:
                    end = j
                    break
            return text, "\n".join(lines[i:end])
    raise LookupError(f"заголовок не найден: {pattern!r}")


def item_tokens(path: Path, sections: str, cal: dict) -> tuple[int, list[str]]:
    kind = KIND.get(path.suffix.lower(), "prose")
    text = path.read_text(encoding="utf-8", errors="replace")
    if sections.strip() in ("", "*"):
        return tokens(text, kind, cal), ["весь файл"]
    lines = text.splitlines()
    total, found = 0, []
    for pat in [s.strip() for s in sections.split("||") if s.strip()]:
        head, body = section_text(lines, pat)
        total += tokens(body, kind, cal)
        found.append(head)
    return total, found


def load_reading() -> "OrderedDict[str, list[tuple[str, str, str]]]":
    out: "OrderedDict[str, list]" = OrderedDict((n, []) for n in NODES)
    for line in READING.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#") or line.startswith("node\t"):
            continue
        node, path, sections, note = (line.split("\t") + ["", "", "", ""])[:4]
        for n in (NODES if node == "*" else [x.strip() for x in node.split(",")]):
            out.setdefault(n, []).append((path, sections, note))
    return out


def rows_tokens(node: str, cal: dict) -> tuple[int, int]:
    lines = ROWS.read_text(encoding="utf-8").splitlines()
    mine = [x for x in lines[1:] if x.split("\t")[9] == node]
    return len(mine), tokens("\n".join([lines[0]] + mine), "data", cal)


def fmt(n: int) -> str:
    return f"{n / 1000:.1f} тыс." if n < 100_000 else f"{round(n / 1000)} тыс."


def report(nodes: list[str], cal: dict) -> int:
    reading = load_reading()
    errors = 0
    summary = []
    for node in nodes:
        items = reading.get(node, [])
        n_rows, t_rows = rows_tokens(node, cal)
        print(f"\n### {node}\n")
        print("| файл | разделы | токены | зачем |")
        print("|---|---|---:|---|")
        total = t_rows
        print(f"| `research/design-build/phase-4/inputs/rows.tsv` | строки узла: {n_rows} | {fmt(t_rows)} | вход узла |")
        for path, sections, note in items:
            p = resolve(path)
            try:
                t, found = item_tokens(p, sections, cal)
            except (LookupError, FileNotFoundError) as exc:
                print(f"| `{path}` | ОШИБКА: {exc} | — | {note} |")
                errors += 1
                continue
            total += t
            heads = "; ".join(h if len(h) <= 48 else h[:47] + "…" for h in found)
            print(f"| `{path}` | {heads} | {fmt(t)} | {note} |")
        if node in EXTRA:
            what, t = EXTRA[node]
            total += t
            print(f"| — | {what} | {fmt(t)} | сверх списка |")
        work = round(total * WORK_FACTOR) + sum(FIXED.values())
        print(f"\nЧтение: ≈ {fmt(total)}; с повторными чтениями (×{WORK_FACTOR}) и постоянной частью "
              f"({', '.join(f'{k} {fmt(v)}' for k, v in FIXED.items())}) — ≈ {fmt(work)} токенов контекста.")
        summary.append((node, n_rows, total, work))
    print("\n| узел | строк | чтение | контекст |")
    print("|---|---:|---:|---:|")
    for node, n, t, w in summary:
        print(f"| {node} | {n} | {fmt(t)} | {fmt(w)} |")
    return 1 if errors else 0


def list_headings(path: Path, cal: dict):
    kind = KIND.get(path.suffix.lower(), "prose")
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    print(f"{path.relative_to(REPO)} — весь файл {fmt(tokens(text, kind, cal))}")
    hs = list(headings(lines))
    for n, (i, lvl, head) in enumerate(hs):
        end = len(lines)
        for j, lvl2, _ in hs[n + 1:]:
            if lvl2 <= lvl:
                end = j
                break
        t = tokens("\n".join(lines[i:end]), kind, cal)
        print(f"{'  ' * (lvl - 1)}{i + 1:5d}  {fmt(t):>10}  {head[:100]}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--node", help="код узла")
    ap.add_argument("--headings", help="путь файла (от kb/ или корня): заголовки с объёмом разделов")
    args = ap.parse_args()
    cal = calibration()
    if args.headings:
        list_headings(resolve(args.headings), cal)
        return 0
    return report([args.node] if args.node else NODES, cal)


if __name__ == "__main__":
    sys.exit(main())
