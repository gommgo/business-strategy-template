#!/usr/bin/env python3
"""Приёмка плана разгрузки ДФ9 (оркестратор): механические пункты одним прогоном.
  df9_check.py coverage   — все находки отчётов OE (строки `| OE<n>-<m> |` раздела 2) есть в DF9-ZONES.tsv ровно по
                            разу; классы из списка брифа; у `правка` и `удаление` — зона, у прочих — причина в `note`;
                            строки не из OE (пункты свода §2) — перечнем
  df9_check.py masks      — маски файлов зон из DF9-PLAN.md (строки «Маски файлов» разделов `### D<N>`), порядок пар
                            (§3, строки вида «D1 ∥ D2»): пересечения масок внутри пары по файлам репозитория
                            (git ls-files) и по самим маскам
Журнальный инструмент: стандартная библиотека (системный python3).
"""
import csv, fnmatch, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
J = ROOT / "research/design-build/phase-9"
CLASSES = {"правка", "удаление", "замер", "Ф10", "оставить"}


def oe_ids():
    ids = []
    for n in range(1, 6):
        for line in (J / f"prep/OE-{n}.md").read_text(encoding="utf-8").splitlines():
            m = re.match(r"\|\s*(OE\d-\d\d)\s*\|", line)
            if m:
                ids.append(m.group(1))
    return ids


def zones_rows():
    with open(J / "DF9-ZONES.tsv", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def coverage():
    want = oe_ids()
    rows = zones_rows()
    rc = 0
    print(f"находок в отчётах OE: {len(want)} (уникальных {len(set(want))}); строк плана: {len(rows)}")
    seen = {}
    for r in rows:
        seen.setdefault(r["id"].strip(), []).append(r)
    miss = [i for i in dict.fromkeys(want) if i not in seen]
    dup = [i for i, v in seen.items() if len(v) > 1]
    extra = [i for i in seen if i not in set(want)]
    if miss:
        rc = 1; print("НЕТ В ПЛАНЕ:", " ".join(miss))
    if dup:
        rc = 1; print("ДУБЛИ:", " ".join(dup))
    print("строки не из OE:", " ".join(extra) or "—")
    count = {}
    for r in rows:
        c = (r.get("class") or "").strip(); z = (r.get("zone") or "").strip(); note = (r.get("note") or "").strip()
        count[c] = count.get(c, 0) + 1
        if c not in CLASSES:
            rc = 1; print(f"КЛАСС вне списка: {r['id']} — {c!r}")
        if c in ("правка", "удаление") and not re.fullmatch(r"D\d+[a-z]?", z):
            rc = 1; print(f"БЕЗ ЗОНЫ: {r['id']} ({c}) — {z!r}")
        if c not in ("правка", "удаление") and not note:
            rc = 1; print(f"БЕЗ ПРИЧИНЫ: {r['id']} ({c})")
        if c == "удаление" and not re.search(r"grep|поиск|зов|вызов|импорт|ссыл", note, re.I):
            print(f"  удаление без явного доказательства в note: {r['id']}")
    print("классы:", ", ".join(f"{k} {v}" for k, v in sorted(count.items(), key=lambda kv: -kv[1])))
    byzone = {}
    for r in rows:
        z = (r.get("zone") or "").strip()
        if (r.get("class") or "").strip() in ("правка", "удаление"):
            byzone.setdefault(z, 0); byzone[z] += 1
    print("по зонам:", ", ".join(f"{k} {v}" for k, v in sorted(byzone.items(), key=lambda kv: (len(kv[0]), kv[0]))))
    return rc


def plan_masks():
    text = (J / "DF9-PLAN.md").read_text(encoding="utf-8")
    zones = {}
    cur = None
    buf = None
    for line in text.splitlines():
        h = re.match(r"#{2,4}\s+(D\d+[a-z]?)\b", line)
        if h:
            cur = h.group(1); buf = None; continue
        if line.startswith("## "):
            cur = None; buf = None; continue
        if cur and "Маски файлов" in line:
            buf = zones.setdefault(cur, [])
            buf += re.findall(r"`([^`]+)`", line.split("Маски файлов", 1)[1]); continue
        if buf is not None:
            if line.strip() == "" or re.match(r"\s*[-*]\s+\*\*|\s*[-*]\s+[А-ЯA-Z][^`]*:", line):
                buf = None; continue
            buf += re.findall(r"`([^`]+)`", line)
    return zones, text


def masks():
    zones, text = plan_masks()
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split()
    rc = 0
    for z, gl in sorted(zones.items(), key=lambda kv: (len(kv[0]), kv[0])):
        hit = sum(1 for f in files if any(fnmatch.fnmatch(f, g) for g in gl))
        print(f"{z}: масок {len(gl)}, файлов репозитория под масками {hit}")
    pairs = re.findall(r"(D\d+[a-z]?)\s*∥\s*(D\d+[a-z]?)", text)
    for a, b in dict.fromkeys(pairs):
        ga, gb = zones.get(a, []), zones.get(b, [])
        both = [f for f in files if any(fnmatch.fnmatch(f, g) for g in ga) and any(fnmatch.fnmatch(f, g) for g in gb)]
        same = sorted(set(ga) & set(gb))
        cross = [(x, y) for x in ga for y in gb if x != y and (fnmatch.fnmatch(x, y) or fnmatch.fnmatch(y, x))]
        flag = "ПЕРЕСЕЧЕНИЕ" if (both or same or cross) else "чисто"
        rc |= bool(both or same or cross)
        print(f"пара {a} ∥ {b}: {flag}" + "".join(f"\n  файл {f}" for f in both[:20]) +
              "".join(f"\n  маска {m}" for m in same) + "".join(f"\n  маски {x} ~ {y}" for x, y in cross[:10]))
    missing = [z for z in {x for p in pairs for x in p} if z not in zones]
    if missing:
        rc = 1; print("нет масок у зон:", " ".join(sorted(missing)))
    return rc


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "coverage"
    sys.exit({"coverage": coverage, "masks": masks}[cmd]())
