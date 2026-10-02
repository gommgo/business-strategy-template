#!/usr/bin/env python3
"""rawlabel — механика Ф10: метка доказательности остаётся, путь в непереносимое доказательство уходит.

Правит только скобочные метки `[проверено…: …]` (и синонимы `[замер: …]`, `[измерение: …]`, `[расчёт: …]`), у которых
после двоеточия стоят одни пути в `99-raw` и id опытов («D2/01», «H/14-camera-path», «text I/03»): метка остаётся без
хвоста — `[проверено: 99-raw/experiments/H/14-camera-path]` → `[проверено]`. Метки со словами, условиями, версиями и
числами после двоеточия («Chromium 153», «валидатор B/07», «05, 17») не трогает — их разбирает агент зоны: скрипт не
знает, что из этого условие проверки, а что адрес опыта. Остальной текст строки не меняется.

По умолчанию — сухой прогон: счёт по файлам и образцы. Запись — только с `--apply`.
    python3 research/design-build/phase-10/tools/rawlabel.py                  # сухой прогон по md зон
    python3 research/design-build/phase-10/tools/rawlabel.py --machine        # плюс машинные файлы (YAML, JSON, TSV, код)
    python3 research/design-build/phase-10/tools/rawlabel.py --mask 'site/**' --apply
    python3 research/design-build/phase-10/tools/rawlabel.py --selftest
Не входят: `99-raw`, `PLAN.md` баз, витрина `blender/15-showcase` (у них своя судьба), `kb/common/` (легенда меток и её примеры).
"""
import argparse
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOURNAL = HERE.parents[1]
spec = importlib.util.spec_from_file_location("kbscan", JOURNAL / "tools" / "kbscan.py")
kbscan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kbscan)

LBL = re.compile(r"\[((?:проверено|замер|измерение|расчёт)[^\]:\[]{0,40}?)\s*:\s*([^\]\[]*)\]")
BASE = r"(?:ui|ux|site|text|creative|ai-media|blender|cd|kimi|claude-design)(?:-research)?"
RAW = re.compile(r"^`?(?:\.\./)*(?:" + BASE + r"/)?99-raw/[^\s,;`]+`?$")
EXP = re.compile(r"^`?(?:" + BASE + r"\s+)?[A-Z][0-9A-Z]?/\d{2}[A-Za-z0-9._-]*`?$")
SKIP = re.compile(r"(^|/)99-raw/|^[a-z-]+/PLAN\.md$|^blender/15-showcase/|^common/")


def fix_line(line):
    """→ (новая строка, число снятых хвостов меток)."""
    n = 0

    def repl(m):
        nonlocal n
        items = [x.strip() for x in re.split(r"[;,]|\s+и\s+", m.group(2)) if x.strip()]
        if items and all(RAW.match(it) or EXP.match(it) for it in items):
            n += 1
            return "[" + m.group(1).rstrip() + "]"
        return m.group(0)

    return LBL.sub(repl, line), n


def selftest():
    cases = [
        ("Норма [проверено: 99-raw/experiments/H/14-camera-path].", "Норма [проверено].", 1),
        ("→ §1.6 `[проверено: E/01]`", "→ §1.6 `[проверено]`", 1),
        ("x [проверено: text I/03; D2/01] y", "x [проверено] y", 1),
        ("x [проверено: J/01, Chromium 153 CfT; Pixel 7 — то же]", "x [проверено: J/01, Chromium 153 CfT; Pixel 7 — то же]", 0),
        ("x [проверено: 05, 17]", "x [проверено: 05, 17]", 0),
        ("x [проверено] и [исследование: NN/g 2020]", "x [проверено] и [исследование: NN/g 2020]", 0),
        ("[проверено расчётом: ../99-raw/experiments/A/02-x/calc.py]", "[проверено расчётом]", 1),
    ]
    bad = 0
    for src, want, cnt in cases:
        got, n = fix_line(src)
        if (got, n) != (want, cnt):
            print("FAIL: %r → %r (%d), ожидалось %r (%d)" % (src, got, n, want, cnt)); bad += 1
    print("selftest: %s" % ("OK" if not bad else "ошибок %d" % bad))
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--kb", default=str(kbscan.KB_DEFAULT))
    ap.add_argument("--mask", action="append", default=[])
    ap.add_argument("--machine", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    kb = Path(a.kb).resolve()
    total = files = 0
    shown = 0
    for rel in kbscan.list_files(kb):
        if SKIP.search(rel):
            continue
        if a.mask and not any(kbscan.glob_match(rel, m) for m in a.mask):
            continue
        kind = kbscan.kind_of(kb / rel)
        if kind == "bin" or (kind != "prose" and not a.machine):
            continue
        try:
            text = (kb / rel).read_bytes().decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        out, n_file = [], 0
        for line in text.split("\n"):
            new, n = fix_line(line)
            if n and shown < a.samples:
                print("  %s\n    − %s\n    + %s" % (rel, line.strip()[:200], new.strip()[:200])); shown += 1
            n_file += n
            out.append(new)
        if n_file:
            print("%s\t%d" % (rel, n_file))
            total += n_file; files += 1
            if a.apply:
                (kb / rel).write_bytes("\n".join(out).encode("utf-8"))
    print("ИТОГО\t%d меток в %d файлах%s" % (total, files, "" if a.apply else " (сухой прогон)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
