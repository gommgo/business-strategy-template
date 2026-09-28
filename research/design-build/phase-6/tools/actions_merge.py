#!/usr/bin/env python3
"""Свод ответов агентов-тем Ф6 по действиям сверки: `ACTIONS-MAP.tsv` + таблицы «Действия сверки» спецификаций
`spec/*.md` → `ACTIONS-SPEC.tsv` (id, фаза, решение каркаса, агент, действие, ответ, место в Ф7, решение спецификации,
файл спецификации).

Таблица действий в спецификации — md-таблица с заголовком `| id | решение | ответ | место в Ф7 |` (раздел
«Действия сверки»; подразделы с другим заголовком не читаются). Строка с id, которого нет в `ACTIONS-MAP.tsv`, —
предупреждение; действие без ответа — ошибка.

Запуск (Python ≥ 3.11, только стандартная библиотека), из любой папки:
    python3 research/design-build/phase-6/tools/actions_merge.py [--check]
`--check` — только отчёт, без записи. Код выхода: 0 — у каждого действия есть ответ; 1 — есть действия без ответа.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

PHASE = Path(__file__).resolve().parent.parent
MAP = PHASE / "ACTIONS-MAP.tsv"
SPEC = PHASE / "spec"
OUT = PHASE / "ACTIONS-SPEC.tsv"
HEADER = re.compile(r"^\|\s*id\s*\|\s*решение\s*\|\s*ответ\s*\|\s*место в Ф7\s*\|\s*$")
ROW = re.compile(r"^\|\s*([A-Z]{2}-\d{2,3})\s*\|(.*)\|\s*$")


def split_cells(line: str) -> list[str]:
    """Ячейки md-строки; `|` внутри обратных кавычек ячейку не делит."""
    cells, buf, tick = [], [], False
    for ch in line.strip().strip("|"):
        if ch == "`":
            tick = not tick
        if ch == "|" and not tick:
            cells.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)
    cells.append("".join(buf).strip())
    return cells


def spec_rows(path: Path) -> dict[str, tuple[str, str, str]]:
    rows: dict[str, tuple[str, str, str]] = {}
    inside = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if HEADER.match(line):
            inside = True
            continue
        if inside:
            if line.startswith("|---") or line.startswith("| ---"):
                continue
            if not line.startswith("|"):
                inside = False
                continue
            cells = split_cells(line)
            if len(cells) >= 4 and re.fullmatch(r"[A-Z]{2}-\d{2,3}", cells[0]):
                rows[cells[0]] = (cells[1], cells[2], cells[3])
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="только отчёт, без записи")
    args = ap.parse_args()

    with MAP.open(encoding="utf-8") as f:
        actions = list(csv.DictReader(f, delimiter="\t"))
    answers: dict[str, tuple[str, str, str, str]] = {}
    for path in sorted(SPEC.glob("*.md")):
        for id_, (decision, answer, place) in spec_rows(path).items():
            if id_ in answers:
                print(f"предупреждение: {id_} — ответ и в {answers[id_][3]}, и в {path.name}; берётся первый")
                continue
            answers[id_] = (decision, answer, place, path.name)

    known = {a["id"] for a in actions}
    for id_ in sorted(set(answers) - known):
        print(f"предупреждение: {id_} из {answers[id_][3]} нет в ACTIONS-MAP.tsv")
    missing = [a["id"] for a in actions if a["id"] not in answers]
    by_agent: dict[str, list[int]] = {}
    for a in actions:
        got = a["id"] in answers
        by_agent.setdefault(a["agent"], [0, 0])[0 if got else 1] += 1
    for agent, (ok, no) in sorted(by_agent.items()):
        print(f"{agent}: с ответом {ok}, без ответа {no}")
    if missing:
        print("без ответа: " + ", ".join(missing))

    if not args.check:
        with OUT.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, delimiter="\t", lineterminator="\n")
            w.writerow(["id", "phase", "decision", "agent", "action", "answer", "place", "spec_decision", "spec"])
            for a in actions:
                d, ans, place, src = answers.get(a["id"], ("", "", "", ""))
                w.writerow([a["id"], a["phase"], a["decision"], a["agent"], a["action"], ans, place, d, src])
        print(f"{OUT.name}: строк {len(actions)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
