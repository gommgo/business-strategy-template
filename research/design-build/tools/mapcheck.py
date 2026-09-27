#!/usr/bin/env python3
"""Проверка карты знаний по `kb/common/canon.tsv`: адрес карты не должен вести в копию нормы вместо её канона.

Для каждого адреса с разделом или ключом (короткий «ux 06/01 §2», путь в обратных кавычках с `§…` или `#ключ`):
  • ПРОВЕРИТЬ — адрес совпадает с местом из колонки `copies` какой-то нормы и не совпадает ни с одним `place`:
    печатается канон этой нормы и её id. Один раздел бывает каноном одной нормы и копией другой, поэтому это вопрос,
    а не ошибка: если строка карты говорит именно об этой норме — адрес меняют на канон;
  • НЕ НОРМА — адрес (любой, и без раздела) ведёт в `99-raw/`, в `PLAN.md` базы или в журнал сборки — ошибка.
Адрес файла целиком — вход, а не место нормы: он не сверяется с копиями.
Совпадение: тот же файл и тот же раздел; раздел «§4» совпадает с «§4.2» копии только точно.

Запуск: python3 research/design-build/tools/mapcheck.py <файл карты> [...]
Код выхода: 0 — ссылок «не на норму» нет (строки ПРОВЕРИТЬ допустимы); 1 — есть.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import refcheck  # noqa: E402

KB = refcheck.KB
CANON = KB / "common" / "canon.tsv"


def norm_path(p: str) -> str:
    p = p.strip().rstrip(".,;")
    if p.startswith("kb/"):
        p = p[3:]
    return p


def split_place(s: str) -> tuple[str, str]:
    s = s.strip()
    m = re.match(r"^(.*?)(?:\s*§\s*(.+)|#(.+))?$", s)
    path = norm_path(m.group(1))
    sec = (m.group(2) or m.group(3) or "").strip()
    sec = sec.split(",")[0].split("–")[0].strip().rstrip(".")
    return path, sec


def load_canon():
    places, copies = set(), {}
    with CANON.open(encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE):
            places.add(split_place(r["place"]))
            for c in (r.get("copies") or "").split(";"):
                c = c.strip()
                if not c or c == "—":
                    continue
                copies.setdefault(split_place(c), []).append((r["id"], r["place"], r["norm"]))
    return places, copies


def addresses(line: str):
    for m in refcheck.SHORT.finditer(line):
        base, nn, mm, sec = m.group(1), m.group(2), m.group(3), m.group(4) or ""
        p = refcheck.resolve_short(base, nn, mm)
        if p is not None:
            yield m.group(0).strip(), str(p.relative_to(KB)), sec.strip().rstrip(".")
    for m in refcheck.TICK.finditer(line):
        tok = m.group(1).strip()
        path, sec = split_place(tok)
        if not refcheck.looks_like_path(path.split()[0] if path else ""):
            continue
        yield tok, path.split()[0], sec


def main() -> int:
    places, copies = load_canon()
    bad = 0
    for f in sys.argv[1:]:
        p = Path(f).resolve()
        fence = False
        hits = []
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                fence = not fence
                continue
            if fence:
                continue
            for shown, path, sec in addresses(line):
                if "99-raw/" in path or re.match(r"^[a-z-]+/PLAN\.md$", path) or path.startswith("research/"):
                    hits.append(f"{i}: НЕ НОРМА `{shown}`")
                    continue
                if not sec:
                    continue
                key = (path, sec)
                if key in copies and key not in places:
                    ids = "; ".join(f"{i_} «{nm[:50]}» → {pl}" for i_, pl, nm in copies[key][:3])
                    hits.append(f"{i}: ПРОВЕРИТЬ `{shown}` — копия нормы: {ids}")
        errs = sum(1 for h in hits if "НЕ НОРМА" in h)
        bad += errs
        print(f"{p.name}: не на норму {errs}, проверить {len(hits) - errs}")
        for h in hits:
            print("  " + h)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
