#!/usr/bin/env python3
"""Разрез списков зон данных `Д-<база>.tsv` на зоны агентов волны 4 (Ф10).

    python3 split_data_zones.py --zones ПАПКА_code-zones --out ПАПКА [--write]

Без `--write` — только счёт. С `--write` пишет `Д-<зона>.tsv` (те же колонки) и `Д-<зона>.masks` в `--out`.
Файлы витрины blender, которые снимаются с журналом испытания (`15-showcase/vote/`, `_shared/digests/`, `PLAN.md`),
и производные (их собирает генератор) в зоны не идут — печатаются отдельным списком.
"""
import argparse
import csv
from pathlib import Path

SKILL_KB = ".claude/skills/design-deep-dive/kb/"

# зона → (база, предикат по пути файла от kb/)
def folder(rel):
    return rel.split("/")[1]

SPLIT = {
    "Д-site-1": ("site", lambda r: folder(r) in ("02-site-types", "09-ai-generation-evaluation")),
    "Д-site-2": ("site", lambda r: folder(r) not in ("02-site-types", "09-ai-generation-evaluation")),
    "Д-creative-1": ("creative", lambda r: folder(r) in ("06-effects-catalog", "07-stack-implementation",
                                                          "08-uniqueness-anti-slop")),
    "Д-creative-2": ("creative", lambda r: folder(r) not in ("06-effects-catalog", "07-stack-implementation",
                                                              "08-uniqueness-anti-slop")),
    "Д-text-1": ("text", lambda r: folder(r) in ("07-seo-geo-copy", "08-russian-legal-typography",
                                                  "09-ai-generation-evaluation", "10-templates-recipes")),
    "Д-text-2": ("text", lambda r: folder(r) not in ("07-seo-geo-copy", "08-russian-legal-typography",
                                                      "09-ai-generation-evaluation", "10-templates-recipes")),
    "Д-blender-1": ("blender", lambda r: folder(r) != "15-showcase"),
    "Д-blender-2": ("blender", lambda r: folder(r) == "15-showcase"),
    "Д-ai-media-1": ("ai-media", lambda r: folder(r) != "14-recipes"),
    "Д-ai-media-2": ("ai-media", lambda r: folder(r) == "14-recipes"),
}

REMOVED = ("blender/15-showcase/vote/", "blender/15-showcase/_shared/digests/", "blender/15-showcase/PLAN.md")
DERIVED = (
    "ux/12-evaluation-checklists/master-checklist.yaml",
    "site/09-ai-generation-evaluation/site-checklist.yaml",
    "site/09-ai-generation-evaluation/ux-marketing-profile.tsv",
    "site/09-ai-generation-evaluation/ac-profile.tsv",
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zones", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    zones, out = Path(a.zones), Path(a.out)
    cache = {}
    skipped = []
    for zone, (base, pred) in SPLIT.items():
        if base not in cache:
            with open(zones / f"Д-{base}.tsv", encoding="utf-8") as fh:
                rd = csv.DictReader(fh, delimiter="\t")
                cache[base] = (rd.fieldnames, list(rd))
        cols, rows = cache[base]
        mine = []
        for r in rows:
            f = r["file"]
            if not pred(f):
                continue
            if f.startswith(REMOVED):
                skipped.append((zone, f, "снимается с журналом испытания"))
                continue
            if f in DERIVED:
                skipped.append((zone, f, "производный: правится источник"))
                continue
            mine.append(r)
        mk, tk = sum(int(r["sum"]) for r in mine), sum(int(r["tokens"]) for r in mine)
        print(f"{zone:14s} файлов {len(mine):3d}  маркеров {mk:4d}  токенов {tk // 1000:4d}k")
        if a.write:
            out.mkdir(parents=True, exist_ok=True)
            with open(out / f"{zone}.tsv", "w", encoding="utf-8", newline="") as fh:
                wr = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", lineterminator="\n")
                wr.writeheader()
                wr.writerows(mine)
            head = (f"# {zone} — машинные файлы базы {base}: следы процесса исследования (волна 4); маски — пути от "
                    f"корня репозитория, для scripts/maint/accept.py --masks-file\n")
            (out / f"{zone}.masks").write_text(head + "".join(SKILL_KB + r["file"] + "\n" for r in mine),
                                               encoding="utf-8")
    for base, (cols, rows) in cache.items():
        taken = sum(1 for z, (b, p) in SPLIT.items() if b == base for r in rows if p(r["file"]))
        assert taken == len(rows), (base, taken, len(rows))
    print("не идут в зоны:")
    for zone, f, why in skipped:
        print(f"  {zone}: {f} — {why}")


if __name__ == "__main__":
    main()
