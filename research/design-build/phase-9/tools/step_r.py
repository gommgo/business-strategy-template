#!/usr/bin/env python3
"""Шаг Р ДФ9 (оркестратор, DF9-PLAN.md §4 «Реестр норм»): строки узлов Ф4, которые называют снятые утилиты текста.
  step_r.py [--apply]   — без --apply печатает замены; с --apply правит phase-4/nodes/02-TR.tsv и 10-CN.tsv по месту
TR-04 copies — без copy_extract.py; TR-54 copies — make_skeleton.py → copydeck.py (skeleton строит каркас из плана и
анатомии блока); TR-54 sides — без make_skeleton.py (сторона описана в positions); CN-95 copies — без copy_extract.py.
Дальше: registry.py check → merge → canon, maint/canon_check.py, maint/mapcheck.py kb/INDEX.md.
"""
import sys
from pathlib import Path

J = Path(__file__).resolve().parents[2] / "phase-4" / "nodes"
SK = ".claude/skills/design-deep-dive/scripts/text/"
EDITS = [  # (файл, id, колонка, было, стало)
    ("02-TR.tsv", "TR-04", "copies", f"; {SK}copy_extract.py", ""),
    ("02-TR.tsv", "TR-54", "copies", f"{SK}make_skeleton.py", f"{SK}copydeck.py"),
    ("02-TR.tsv", "TR-54", "sides", f"text:{SK}make_skeleton.py; ", ""),
    ("10-CN.tsv", "CN-95", "copies", f"; {SK}copy_extract.py", ""),
]


def main():
    apply = "--apply" in sys.argv
    rc = 0
    for name in sorted({e[0] for e in EDITS}):
        p = J / name
        lines = p.read_text(encoding="utf-8").split("\n")
        cols = lines[0].split("\t")
        for fname, rid, col, old, new in EDITS:
            if fname != name:
                continue
            i = next((k for k, l in enumerate(lines) if l.split("\t", 1)[0] == rid), None)
            cells = lines[i].split("\t") if i is not None else []
            c = cols.index(col)
            if i is None or old not in cells[c]:
                print(f"НЕТ: {rid} {col} — «{old}»"); rc = 1; continue
            cells[c] = cells[c].replace(old, new, 1)
            lines[i] = "\t".join(cells)
            print(f"{rid} {col}: «{old}» → «{new}»")
        if apply and not rc:
            p.write_text("\n".join(lines), encoding="utf-8")
    return rc


if __name__ == "__main__":
    sys.exit(main())
