#!/usr/bin/env python3
"""Раскладка действий Ф7 по зонам: `phase-6/ACTIONS-SPEC.tsv` (71 действие сверки Ф6) + таблица
`phase-6/spec/T3-saas-layer.md § 2.1` (41 действие Ф4 с фазой Ф7) → `phase-7/ZONES.tsv` (источник, id, решение,
зоны, место в Ф7).

Зона определяется по файлам, которые называет колонка «место в Ф7»; у действия может быть несколько зон. Части места,
отнесённые к Ф8 и Ф10, зон не дают. Строка T3 § 2.1 «см. раздел 2» берёт место из `ACTIONS-SPEC.tsv`; место «то же» или
«те же файлы» — место строки выше; место «открыто: …» — зона `открыто` (в Ф7 реализовать нечего). Зоны — по
`phase-7/PLAN.md` § 2: 1 — каноны новых слоёв, 2 — каноны слоя проекта, 3 — стыки FSD, mobile, бота, 4 — `CLAUDE.md`
и карты, 5a — `phases.md` и чек-листы, 5b — протокол холста и остальные `references/`, 5c — `SKILL.md`, 6 —
`design-audit` и агенты, 7a — project и interface, 7b — screens, FSD, mobile, бот, 8 — оркестраторы и `/cross-audit`,
10 — база.

Запуск (Python ≥ 3.11, только стандартная библиотека), из любой папки:
    python3 research/design-build/phase-7/tools/zones.py [--check]
`--check` — только отчёт, без записи. Код выхода: 0 — у каждого действия есть зона; 1 — есть действия без зоны.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

BUILD = Path(__file__).resolve().parent.parent.parent
SPEC_TSV = BUILD / "phase-6" / "ACTIONS-SPEC.tsv"
T3 = BUILD / "phase-6" / "spec" / "T3-saas-layer.md"
OUT = BUILD / "phase-7" / "ZONES.tsv"
ORDER = ["1", "2", "3", "4", "5a", "5b", "5c", "6", "7a", "7b", "8", "10"]

RULES: list[tuple[str, re.Pattern[str]]] = [
    ("1", re.compile(r"_template/site/|_template/design/|форм[аеуы] `(?:ready|system|app-brief|brand)\.yaml`|"
                     r"форм[аеуы] `(?:ARTIFACTS|REVIEW)\.md`|`ready\.yaml`")),
    ("2", re.compile(r"_template/(?:project|interface|screens|services)/")),
    ("3", re.compile(r"_template/(?:fsd|mobile|telegram-bot-flow)/")),
    ("4", re.compile(r"`CLAUDE\.md`|CLAUDE\.md` §|`docs/README\.md|`docs/projects/README\.md|getting-started|"
                     r"forward-only\.md|settings\.json")),
    ("5a", re.compile(r"(?<!project-deep-dive/references/)(?<!\{)phases\.md|field-checklists\.md(?!`? `project)|"
                      r"таблица «шаг text → этап»|этап[аеы]? «")),
    ("5b", re.compile(r"claude-design\.md|workflow-patterns\.md|draft-stable\.md|knowledge-base\.md")),
    ("5c", re.compile(r"design-deep-dive/SKILL\.md")),
    ("6", re.compile(r"design-audit|агент-судья|\.claude/agents/")),
    ("7a", re.compile(r"project-deep-dive|project-audit|interface-deep-dive|interface-audit")),
    ("7b", re.compile(r"screen-deep-dive|screen-audit|tree-notation\.md|fsd-deep-dive|fsd-audit|mobile-deep-dive|"
                      r"mobile-audit|telegram-bot-flow-deep-dive|telegram-bot-flow-audit")),
    ("8", re.compile(r"entrypoint|cross-audit|service-audit")),
    ("10", re.compile(r"kb/common/|common/CONTRADICTIONS|canon\.tsv|common/judge\.md|пакет закрытий|kb/INDEX\.md")),
]
# Места, где файл назван словами, а не путём: README mobile у ST-07 («mobile — тип в каноне слоя (README)»).
EXTRA: dict[tuple[str, str], list[str]] = {("Ф4", "ST-07"): ["3"]}
LATER = re.compile(r"(?:^|[;.]\s*)(?:Ф8|Ф10)\b[^;]*")
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


def zones_of(place: str) -> list[str]:
    """Зоны по месту в Ф7; части «Ф8 — …», «Ф10 — …» не считаются."""
    text = LATER.sub(" ", place)
    found = [zone for zone, rule in RULES if rule.search(text)]
    return sorted(set(found), key=ORDER.index)


def read_t3_ph4() -> list[tuple[str, str, str]]:
    """Таблица § 2.1 спецификации T3: (id, место, решение)."""
    rows, inside = [], False
    for line in T3.read_text(encoding="utf-8").splitlines():
        if line.startswith("### 2.1."):
            inside = True
            continue
        if inside and line.startswith("## "):
            break
        if inside and ROW.match(line):
            cells = split_cells(line)
            rows.append((cells[0], cells[1], cells[2]))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="только отчёт, без записи")
    args = parser.parse_args()

    spec = list(csv.DictReader(SPEC_TSV.open(encoding="utf-8"), delimiter="\t"))
    by_id = {r["id"]: r for r in spec}
    out: list[dict[str, str]] = []
    for r in spec:
        out.append({"source": "Ф6", "id": r["id"], "decision": r["decision"], "place": r["place"]})
    for rid, place, decision in read_t3_ph4():
        if place.startswith("см. раздел 2") and rid in by_id:
            place = by_id[rid]["place"]
        out.append({"source": "Ф4", "id": rid, "decision": decision, "place": place})

    missing = []
    for i, row in enumerate(out):
        place = row["place"]
        if place.startswith(("то же", "те же")) and i > 0:
            place = out[i - 1]["place"] + "; " + place
        if place.startswith("открыто"):
            row["zones"] = "открыто"
            continue
        found = set(zones_of(place)) | set(EXTRA.get((row["source"], row["id"]), []))
        row["zones"] = ", ".join(sorted(found, key=ORDER.index))
        if not row["zones"]:
            missing.append(f"{row['source']} {row['id']}")

    counts = {zone: 0 for zone in ORDER + ["открыто"]}
    for row in out:
        for zone in filter(None, row["zones"].split(", ")):
            counts[zone] += 1
    print(f"действий: {len(out)} (Ф6 — {len(spec)}, Ф4 — {len(out) - len(spec)})")
    print("по зонам: " + ", ".join(f"{z} — {n}" for z, n in counts.items()))
    if missing:
        print("без зоны: " + ", ".join(missing))

    if not args.check:
        with OUT.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh, delimiter="\t", lineterminator="\n")
            writer.writerow(["source", "id", "decision", "zones", "place"])
            for row in out:
                writer.writerow([row["source"], row["id"], row["decision"], row["zones"], row["place"]])
        print(f"записано: {OUT.relative_to(BUILD.parent.parent)}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
