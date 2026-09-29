#!/usr/bin/env python3
"""Шаг 10 Ф8, VI-02: переименование id проверок макета `K3-<хвост>` → `LOOK-<хвост>`, `F-<хвост>` → `HON-<хвост>`.

  python3 research/design-build/phase-8/tools/rename_tells.py            # сухой прогон: счёт по файлам, дифф в --diff
  python3 research/design-build/phase-8/tools/rename_tells.py --apply    # записать

Список id — ключи раздела `checks` в `kb/common/tells.yaml` с префиксами `K3-` и `F-` (канон VI-02); `M-*`, `V-*`, `E-*`
и ключи `--allow` (`k3_allow`, `allow:`) не меняются. Замена — по id целиком: слева нет буквы, цифры или дефиса
(`COPY-F-QUOTE` не трогается), справа — тоже. Область — `.claude/skills/` и `docs/`; вне области — журнал сборки,
`assets/calibration/` (утверждён заказчиком) и `99-raw/` баз (уборка). Токены вида `K3-…`/`F-…`, которых нет в `checks`,
печатаются отдельно — решает оркестратор.
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TELLS = ROOT / ".claude/skills/design-deep-dive/kb/common/tells.yaml"
AREAS = [ROOT / ".claude/skills", ROOT / "docs"]
SKIP_PARTS = {"99-raw", "calibration", "__pycache__", "node_modules", ".git"}
EXT = {".py", ".md", ".yaml", ".yml", ".json", ".tsv", ".js", ".mjs", ".html", ".txt", ".sh", ".css", ".csv"}
TOKEN = re.compile(r"(?<![A-Za-z0-9-])(K3|F)-([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)(?![A-Za-z0-9-])")


def ids():
    out = []
    in_checks = False
    for line in TELLS.read_text(encoding="utf-8").splitlines():
        if line.startswith("checks:"):
            in_checks = True
            continue
        if in_checks:
            if line and not line.startswith(" "):
                break
            m = re.match(r"\s+((?:K3|F)-[A-Z0-9-]+):", line)
            if m:
                out.append(m.group(1))
    return out


def new_id(old):
    return ("LOOK-" + old[3:]) if old.startswith("K3-") else ("HON-" + old[2:])


def files():
    for area in AREAS:
        for p in sorted(area.rglob("*")):
            if p.is_file() and p.suffix in EXT and not (SKIP_PARTS & set(p.relative_to(ROOT).parts)):
                yield p


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--diff", default="", help="куда записать дифф сухого прогона")
    a = ap.parse_args()
    known = set(ids())
    if not known:
        sys.exit("в tells.yaml#checks нет id K3-*/F-*")
    rx = re.compile(r"(?<![A-Za-z0-9-])(" + "|".join(sorted(map(re.escape, known), key=len, reverse=True)) +
                    r")(?![A-Za-z0-9-])")
    total, per_file, unknown, diff = 0, [], {}, []
    for p in files():
        text = p.read_text(encoding="utf-8", errors="surrogateescape")
        for m in TOKEN.finditer(text):
            tok = m.group(0)
            if tok not in known:
                unknown.setdefault(tok, set()).add(str(p.relative_to(ROOT)))
        new, n = rx.subn(lambda m: new_id(m.group(1)), text)
        if n:
            total += n
            rel = str(p.relative_to(ROOT))
            per_file.append((n, rel))
            if a.diff:
                diff.extend(difflib.unified_diff(text.splitlines(True), new.splitlines(True), rel, rel))
            if a.apply:
                p.write_text(new, encoding="utf-8", errors="surrogateescape")
    print(f"id в checks: {len(known)}; замен: {total} в {len(per_file)} файлах ({'записано' if a.apply else 'сухой прогон'})")
    for n, rel in sorted(per_file, key=lambda x: (-x[0], x[1])):
        print(f"  {n:4d}  {rel}")
    if unknown:
        print("токены K3-*/F-* вне checks (не меняются):")
        for tok, where in sorted(unknown.items()):
            print(f"  {tok}: {', '.join(sorted(where))[:300]}")
    if a.diff:
        Path(a.diff).write_text("".join(diff), encoding="utf-8")
        print(f"дифф: {a.diff}")


if __name__ == "__main__":
    main()
