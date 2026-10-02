#!/usr/bin/env python3
"""kbctx — контексты маркеров для текстовой зоны Ф10: агент читает окна вокруг маркеров, а не файлы целиком.

Для каждого md-файла списка зоны пишет файл контекстов: счёт маркеров по классам, указатель заголовков с номерами
строк, шапку (первые строки) и окна вокруг строк с маркерами — строки исходника дословно, с номерами. По номерам строк
агент дочитывает нужный раздел исходника сам (действие сверки, снятие раздела).

    python3 research/design-build/phase-10/tools/kbctx.py --zone ЗОНА.tsv --out ПАПКА [--extra ФАЙЛ] [--around 3]
    python3 research/design-build/phase-10/tools/kbctx.py --zone ЗОНА.tsv --count          # только счёт токенов окон
    python3 research/design-build/phase-10/tools/kbctx.py --selftest

Классы маркеров — `tools/kbscan.py` (целевые; `k3` — вне базы ui) плюс классы файла `--extra` (TSV «класс<TAB>regex»).
Строка окна: `NNNN│текст` — обычная, `NNNN►[классы]│текст` — с маркером. Текст после `│` — дословно, без обрезки.
"""
import argparse
import csv
import importlib.util
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
JOURNAL = HERE.parents[1]
spec = importlib.util.spec_from_file_location("kbscan", JOURNAL / "tools" / "kbscan.py")
kbscan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kbscan)

KB = kbscan.KB_DEFAULT
CYR = re.compile(r"[Ѐ-ӿ]")
HEAD_LINES = 14
HEADING = re.compile(r"^#{1,4} ")


def tokens(text):
    cyr = len(CYR.findall(text))
    return int(round(0.3616 * cyr + 0.6162 * (len(text) - cyr)))


def load_classes(extra):
    classes = kbscan.compile_classes(extra=None)
    out = {}
    for name, (target, rx) in classes.items():
        if target or name == "k3":
            out[name] = rx
    if extra:
        for line in Path(extra).read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#") or "\t" not in line:
                continue
            name, pat = line.split("\t", 1)
            out[name.strip()] = re.compile(pat.strip())
    return out


def marks(lines, classes, base):
    """→ {номер строки (с 1): [классы]}; `k3` в базе ui — id проверки, не маркер."""
    found = {}
    for i, line in enumerate(lines, 1):
        hit = [n for n, rx in classes.items() if not (n == "k3" and base == "ui") and rx.search(line)]
        if hit:
            found[i] = hit
    return found


def windows(found, total, around):
    """Окна строк вокруг маркеров; окна с зазором ≤ 2 строки сливаются."""
    out = []
    for n in sorted(found):
        a, b = max(1, n - around), min(total, n + around)
        if out and a <= out[-1][1] + 3:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def render(rel, lines, found, around):
    wins = windows(found, len(lines), around)
    counts = {}
    for cl in found.values():
        for c in cl:
            counts[c] = counts.get(c, 0) + 1
    full = tokens("\n".join(lines))
    buf = [f"# {rel} — строк {len(lines)}, ≈ {full} токенов; строк с маркерами {len(found)}"
           + (" (" + "; ".join(f"{k} {v}" for k, v in sorted(counts.items())) + ")" if counts else "")]
    buf.append("\n## Заголовки (номер строки · заголовок)")
    for i, line in enumerate(lines, 1):
        if HEADING.match(line):
            buf.append(f"{i:5d}  {line}")
    head_end = min(HEAD_LINES, len(lines))
    buf.append(f"\n## Шапка (строки 1–{head_end})")
    for i in range(1, head_end + 1):
        buf.append(row(i, lines[i - 1], found.get(i)))
    buf.append("\n## Окна маркеров")
    for a, b in wins:
        if b <= head_end:
            continue
        a = max(a, head_end + 1) if a <= head_end else a
        buf.append(f"— строки {a}–{b} —")
        for i in range(a, b + 1):
            buf.append(row(i, lines[i - 1], found.get(i)))
    return "\n".join(buf) + "\n"


def row(i, text, classes):
    if classes:
        return f"{i:04d}►[{','.join(classes)}]│{text}"
    return f"{i:04d}│{text}"


def zone_files(zone):
    rows = list(csv.DictReader(open(zone, encoding="utf-8"), delimiter="\t"))
    return [r for r in rows if r.get("kind", "prose") == "prose"]


def process(zone, out, extra, around, count_only):
    classes = load_classes(extra)
    total_ctx = total_full = total_marks = 0
    report = []
    for r in zone_files(zone):
        rel = r["file"]
        p = KB / rel
        if not p.is_file():
            report.append((rel, "нет файла", 0, 0, 0))
            continue
        lines = p.read_text(encoding="utf-8").split("\n")
        if lines and lines[-1] == "":
            lines.pop()
        base = rel.split("/", 1)[0]
        found = marks(lines, classes, base)
        text = render(rel, lines, found, around)
        ctx, full = tokens(text), tokens("\n".join(lines))
        total_ctx += ctx
        total_full += full
        total_marks += len(found)
        report.append((rel, "", len(found), ctx, full))
        if not count_only:
            dst = Path(out) / (rel.replace("/", "__") + ".ctx.md")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text, encoding="utf-8")
    return report, total_marks, total_ctx, total_full


def selftest():
    classes = load_classes(None)
    lines = ["# Заголовок", "", "Волна 1 · агент B · 2026-09-24", "текст"] + ["строка"] * 20 + ["см. `99-raw/x`", "конец"]
    found = marks(lines, classes, "site")
    assert 3 in found and "process" in found[3], found
    assert 25 in found and "raw" in found[25], found
    wins = windows(found, len(lines), 3)
    assert wins == [[1, 6], [22, 26]], wins
    text = render("site/x.md", lines, found, 3)
    assert "0003►[process]│Волна 1 · агент B · 2026-09-24" in text, text
    assert "0025►[raw]│см. `99-raw/x`" in text
    assert "— строки 22–26 —" in text
    assert marks(["id проверки K3"], classes, "ui") == {}
    assert marks(["модель K3"], classes, "site") != {}
    print("selftest: OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zone")
    ap.add_argument("--out")
    ap.add_argument("--extra")
    ap.add_argument("--around", type=int, default=3)
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.zone or not (a.out or a.count):
        ap.error("нужны --zone и --out (или --count)")
    report, m, ctx, full = process(a.zone, a.out, a.extra, a.around, a.count)
    for rel, note, marks_n, c, f in report:
        print(f"{marks_n:5d}  {c:7d}  {f:7d}  {rel}  {note}")
    print(f"ИТОГО: файлов {len(report)}, строк с маркерами {m}, токенов окон {ctx}, токенов файлов {full}")


if __name__ == "__main__":
    sys.exit(main())
